# The Asterisk REST Interface (ARI)

El capítulo anterior cubrió AMI y AGI, las dos formas clásicas de acoplar lógica externa a Asterisk. Ambas preceden a la web moderna: AMI le brinda un flujo de eventos crudo, orientado a líneas, a través de un socket TCP, y AGI entrega un canal único a un script durante la duración de una llamada. Ninguna de ellas fue diseñada para el tipo de aplicaciones con estado, asíncronas y multicanal que la gente construye hoy — IVR que se comunican con servicios web, paneles de click‑to‑call, controladores de conferencias o voicebots que transmiten audio a un motor de reconocimiento de voz.

ARI — la Asterisk REST Interface — se introdujo en Asterisk 12 para cubrir esa brecha, y en Asterisk 22 es la interfaz recomendada para crear nuevas aplicaciones de telefonía. La idea detrás de ARI es una separación clara de responsabilidades: **Asterisk se convierte en un motor de medios** (contesta canales, mezcla puentes, reproduce y graba audio, envía DTMF), y **su aplicación proporciona toda la lógica de control de llamadas** mediante una combinación de una API REST (HTTP) y un flujo de eventos WebSocket.

## Objetivos

Al final de este capítulo, el lector deberá ser capaz de:

- Explicar qué es ARI y cómo difiere de AMI y AGI
- Decidir cuándo ARI es la interfaz adecuada para un proyecto
- Configurar `ari.conf` y `http.conf` para habilitar ARI y crear un usuario
- Conectarse al flujo de eventos WebSocket de ARI
- Describir la aplicación de dialplan Stasis y los eventos `StasisStart`/`StasisEnd`
- Describir el modelo de recursos de ARI: canales, puentes, reproducciones, grabaciones, endpoints y estados de dispositivos
- Escribir una aplicación Stasis mínima en Python que conteste un canal, reproduzca un sonido y cuelgue
- Explicar qué es el canal `externalMedia` y por qué es importante para integraciones de IA y bots de voz

## Qué es ARI y cuándo usarlo

ARI se construye sobre dos transportes que trabajan juntos:

- **Una API REST (HTTP)** que tu aplicación llama para *hacer* cosas — originar un canal, contestarlo, reproducir un sonido, crear un puente, iniciar una grabación, colgar. Estas son solicitudes HTTP ordinarias (`GET`, `POST`, `DELETE`) contra `http://asterisk-host:8088/ari/...`.  
- **Un flujo de eventos WebSocket** sobre el cual Asterisk *informa* a tu aplicación lo que está sucediendo — se creó un canal, llegó un dígito DTMF, terminó una reproducción, un canal salió de tu aplicación. Los eventos se entregan como objetos JSON.

El patrón es asíncrono: haces una solicitud, y el *resultado* de esa solicitud normalmente vuelve más tarde como un evento. Por ejemplo, tú `POST` una solicitud para reproducir un sonido; Asterisk responde inmediatamente con un objeto `Playback`, y algunos segundos después recibes un evento `PlaybackFinished` cuando el audio ha terminado.

Elige ARI sobre AMI y AGI cuando:

- Necesites **control fino de canales y puentes** — crear conferencias, aparcamiento, colas, o flujos de llamada personalizados a partir de primitivas en lugar de depender de aplicaciones del dialplan.  
- Tu aplicación sea **stateful y de larga duración**, manteniendo varios canales a la vez y reaccionando a eventos en todos ellos.  
- Quieras integrarte con **servicios web, buses de mensajes o motores de IA/voz** y prefieras JSON sobre HTTP a un protocolo de línea o a un script stdin/stdout.  
- Estés iniciando un **proyecto nuevo** y quieras la interfaz que el proyecto Asterisk recomienda activamente.

AMI sigue siendo la herramienta adecuada cuando solo necesitas *observar* el sistema o disparar comandos ocasionales (marcadores, paneles de información, monitoreo). AGI sigue siendo conveniente para un script IVR rápido y autocontenido. Pero para cualquier cosa que orqueste llamadas, ARI es la respuesta moderna.

> ARI no reemplaza el dialplan — lo complementa. Un canal se ejecuta en el dialplan como de costumbre hasta que alcanza la aplicación `Stasis()`, momento en el cual el control se entrega a tu aplicación ARI. Cuando tu aplicación termina, el canal puede enviarse de vuelta al dialplan o colgarse.

## Habilitando ARI: http.conf y ari.conf

ARI se ejecuta sobre el servidor HTTP incorporado de Asterisk, por lo que intervienen dos archivos de configuración: `http.conf` habilita el servidor web, y `ari.conf` habilita ARI y define sus usuarios.

### http.conf

El servidor HTTP debe estar habilitado y vinculado a una dirección y puerto. El puerto convencional de ARI es **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

Para producción debe colocar ARI detrás de TLS. Asterisk puede servir HTTPS directamente (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), o puede terminar TLS en un proxy inverso delante del puerto 8088. Sobre TLS las URLs se convierten en `https://` y `wss://` en lugar de `http://` y `ws://`.

Puede confirmar que el servidor HTTP está activo desde la CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` tiene una sección `[general]` y una sección por cada usuario.

```ini
[general]
enabled=yes
pretty=yes              ; pretty-print JSON responses (handy while learning)

[asterisk]
type=user
read_only=no            ; set to yes for a user that may only issue GET requests
password=secret
password_format=plain   ; "plain" (default) or "crypt"
```

Algunas notas sobre estas opciones:

- `enabled` activa o desactiva ARI globalmente.
- `pretty` formatea las respuestas JSON para que sean legibles por humanos; desactívelo en producción.
- Cada usuario es una sección nombrada con `type=user`.
- `read_only=yes` restringe a ese usuario a solicitudes de solo lectura (GET).
- `password_format` puede ser `plain` (la contraseña está en texto plano) o `crypt` (una contraseña hash, generada con `mkpasswd -m sha-512`).
- `permit`, `deny` y `acl` permiten restricciones de IP por usuario, siguiendo las mismas reglas que `acl.conf`.

Después de editar los archivos, recargue los módulos relevantes (`module reload res_ari.so` y `module reload http.so`) o reinicie Asterisk. Puede verificar que ARI está en ejecución con:

```
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

`ari show apps` enumera las aplicaciones Stasis actualmente registradas por los clientes conectados. Está vacío hasta que un cliente se conecte, que es exactamente lo que hacemos a continuación.

### La URL de eventos WebSocket

Un cliente se suscribe al flujo de eventos abriendo un WebSocket al endpoint `/ari/events`, nombrando la aplicación Stasis que implementa y pasando sus credenciales:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

Los parámetros de consulta son:

- `app` — el nombre de su aplicación Stasis. Este es el mismo nombre que usará en la llamada `Stasis()` del dialplan. Puede pasar varios nombres separados por comas.
- `api_key` — las credenciales, en la forma `username:password`, que coinciden con un usuario en `ari.conf`.
- `subscribeAll` — booleano opcional (por defecto `false`); cuando `true`, la aplicación recibe todos los eventos, no solo los de los recursos que posee.

Las mismas credenciales `user:pass` se usan como autenticación HTTP Basic en las llamadas REST (o se añaden como un parámetro de consulta `api_key` allí también).

## Stasis: entregando un canal a su aplicación

El puente entre el dialplan y ARI es la aplicación de dialplan **`Stasis()`** (el marco subyacente también se llama Stasis). Cuando un canal llega a `Stasis(appname[,args])`, Asterisk entrega ese canal a la aplicación ARI registrada bajo `appname` y deja de ejecutar el dialplan para él. El control ahora pertenece a su código.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Cuando el canal entra en la aplicación, cada cliente conectado suscrito a `hello` recibe un evento **`StasisStart`** a través del WebSocket, que lleva el objeto completo del canal (su ID, nombre, caller ID, estado y cualquier argumento pasado a `Stasis()`). Esta es su señal para comenzar a controlar el canal.

Cuando el canal sale de la aplicación — porque su código lo devolvió al dialplan con `continueInDialplan`, o porque se colgó — usted recibe un evento **`StasisEnd`**. Después de que `Stasis()` regresa al dialplan, establece la variable de canal `STASISSTATUS` (`SUCCESS` o `FAILED`), de modo que el dialplan pueda ramificarse según el resultado.

## El modelo de recursos ARI

ARI expone los internos de Asterisk como un pequeño conjunto de recursos REST. Cada recurso vive bajo `/ari/<resource>` y se manipula con los métodos HTTP estándar. Los más importantes son:

| Recurso | Lo que representa | Operaciones de ejemplo |
|----------|--------------------|--------------------|
| **channels** | Una sola pierna de llamada | originate, answer, play, record, hangup |
| **bridges** | Un punto de mezcla que une canales | create, add/remove channels, play to the bridge |
| **playbacks** | Una reproducción de medios en curso | get status, stop, pause/unpause |
| **recordings** | Grabaciones en vivo y almacenadas | start, stop, list stored, delete |
| **endpoints** | Pares configurados (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Estados de dispositivo personalizados | list, get, set, delete |

Algunas llamadas REST concretas (rutas mostradas con el prefijo `/ari` que aparece en la transmisión):

```
# Channels
POST   /ari/channels                          # originate a new channel
POST   /ari/channels/{channelId}/answer       # answer an incoming channel
POST   /ari/channels/{channelId}/play         # play media (body: media=sound:hello-world)
POST   /ari/channels/{channelId}/record       # record the channel
DELETE /ari/channels/{channelId}              # hang up the channel

# Bridges
POST   /ari/bridges                           # create a bridge (e.g. type=mixing)
POST   /ari/bridges/{bridgeId}/addChannel     # add a channel (param: channel=<id>)
POST   /ari/bridges/{bridgeId}/play           # play media to everyone in the bridge
DELETE /ari/bridges/{bridgeId}                # destroy the bridge

# Read-only resources
GET    /ari/endpoints
GET    /ari/deviceStates
GET    /ari/recordings/stored
GET    /ari/playbacks/{playbackId}
```

El parámetro `media` en una solicitud `play` toma un URI de medios. La forma más común es un URI `sound:` que nombra un sonido incorporado, por ejemplo `sound:hello-world` o `sound:tt-monkeys`. Cuando el audio termina, Asterisk emite un evento `PlaybackFinished` para ese ID de reproducción, que es como su aplicación sabe que puede continuar.

Los canales y puentes son los dos bloques de construcción que combina para crear flujos de llamadas. Para conectar a dos llamantes, por ejemplo, origina o acepta dos canales, crea un puente `mixing` con `POST /ari/bridges`, y agrega ambos canales a él con `POST /ari/bridges/{bridgeId}/addChannel`. Para construir una conferencia, simplemente sigue agregando canales al mismo puente.

## Un ejemplo práctico: una aplicación Stasis mínima

Construyamos la aplicación ARI más pequeña y útil. Cuando se marca cualquier extensión, la llamada entra en nuestra aplicación Stasis, la contesta, reproduce el clásico mensaje `hello-world` y cuelga.

### El dialplan

En `extensions.conf`, envía el canal a Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

El nombre de la aplicación `hello` coincide con el `app=hello` que usamos al conectar.

### El cliente Python

Este cliente usa dos bibliotecas bien conocidas: `requests` para las llamadas REST y `websocket-client` para el flujo de eventos. Instálalas con `pip install requests websocket-client`.

```python
#!/usr/bin/env python3
"""Minimal ARI Stasis app: answer, play hello-world, hang up."""
import json
import requests
from websocket import create_connection

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
ARI_USER = "asterisk"
ARI_PASS = "secret"
APP = "hello"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(channel_id):
    requests.post(f"{BASE}/channels/{channel_id}/answer", auth=AUTH)

def play(channel_id, media):
    # Returns the Playback object; we could track its id to await PlaybackFinished.
    r = requests.post(
        f"{BASE}/channels/{channel_id}/play",
        params={"media": media},
        auth=AUTH,
    )
    return r.json()

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=AUTH)

def main():
    ws_url = (
        f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
        f"?app={APP}&api_key={ARI_USER}:{ARI_PASS}"
    )
    ws = create_connection(ws_url)
    print(f"Connected to ARI, waiting for calls into Stasis app '{APP}'...")

    # Track which channel each playback belongs to, so we hang up when it ends.
    playback_owner = {}

    while True:
        event = json.loads(ws.recv())
        kind = event["type"]

        if kind == "StasisStart":
            channel_id = event["channel"]["id"]
            print(f"StasisStart on channel {channel_id}")
            answer(channel_id)
            pb = play(channel_id, "sound:hello-world")
            playback_owner[pb["id"]] = channel_id

        elif kind == "PlaybackFinished":
            pb_id = event["playback"]["id"]
            channel_id = playback_owner.pop(pb_id, None)
            if channel_id:
                print(f"Playback done, hanging up {channel_id}")
                hangup(channel_id)

        elif kind == "StasisEnd":
            print(f"StasisEnd on channel {event['channel']['id']}")

if __name__ == "__main__":
    main()
```

Ejecuta el script y luego marca cualquier número desde un endpoint registrado. Deberías escuchar “Hello, world”, tras lo cual la llamada se libera. En la consola de Asterisk, `ari show apps` ahora listará `hello` mientras el cliente está conectado.

El flujo vale la pena seguirlo una vez:

1. El dialplan ejecuta `Stasis(hello)`; Asterisk entrega el canal a nuestra aplicación y envía un evento `StasisStart`.
2. Contestamos el canal y luego pedimos a Asterisk reproducir `sound:hello-world`. Asterisk devuelve un objeto `Playback` cuyo `id` recordamos.
3. Cuando el audio termina, Asterisk envía `PlaybackFinished` con esa reproducción `id`; buscamos el canal y lo colgamos.
4. Colgar hace que el canal salga de Stasis, generando un evento `StasisEnd`.

> **Una nota sobre las bibliotecas cliente.** Existe un contenedor de nivel superior llamado `ari-py` (el paquete `ari`), pero está sin mantenimiento y fue escrito para una era anterior de Python y herramientas Swagger. Para trabajos nuevos en Asterisk 22, prefiere el enfoque explícito `requests` + WebSocket mostrado arriba, o una biblioteca asyncio como `asyncari` si necesitas concurrencia. El enfoque crudo te mantiene cerca de las llamadas REST y eventos reales, que es exactamente lo que deseas mientras aprendes ARI.

## externalMedia: the door to AI and voicebots

The resources above let you play and record *files*. But modern voice applications — speech-to-text transcription, AI voicebots, real-time analytics — need the *live audio stream* of a call delivered to an external process, and they need to inject audio back.

ARI provides this through the **`externalMedia` channel**. A `POST /ari/channels/externalMedia` request creates a special channel that, instead of talking to a phone, streams the call's RTP media to (and from) an external host. You bridge this channel with the caller's channel, and now your external program is in the audio path: it receives the caller's audio as RTP and can send synthesized audio back.

The request requires only:

- `app` — the Stasis application that owns the new channel.
- `format` — the audio format, e.g. `ulaw` or `slin16`.

`external_host` (the `host:port` of your media application) is optional in the schema — it may be empty for a WebSocket-server-style connection — but for a classic RTP voicebot you will supply it. The `encapsulation` parameter defaults to `rtp` and `transport` to `udp`, which is exactly what you want for a streaming media endpoint.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

This single feature is what turns Asterisk into a front-end for AI: the telephone network terminates on Asterisk, ARI orchestrates the call, and `externalMedia` pipes the audio to a speech/AI engine and back. This is the mechanism on which AI services and voicebots are built.

## Resumen

ARI es la interfaz moderna y recomendada para crear aplicaciones de telefonía en Asterisk 22. Divide el trabajo de forma clara: Asterisk es el motor de medios, y su aplicación — que habla JSON a través de HTTP y un WebSocket — proporciona la lógica de control de llamadas. La habilita mediante `http.conf` (el servidor web integrado en el puerto 8088) y `ari.conf` (que activa ARI y define usuarios).

La aplicación de dialplan `Stasis()` entrega un canal a su aplicación, generando `StasisStart` cuando entra y `StasisEnd` cuando sale. A partir de ahí manipula un pequeño conjunto de recursos REST — canales, puentes, reproducciones, grabaciones, endpoints y estados de dispositivos — para contestar, reproducir, grabar, puentear y colgar.

Construimos una aplicación mínima de Python Stasis que contesta una llamada, reproduce un mensaje y cuelga, y vimos cómo el canal `externalMedia` transmite RTP en vivo a un programa externo — la base para integraciones de IA y bots de voz.

## Quiz

1. ARI was introduced in which version of Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. In the ARI model, Asterisk acts as a media engine while your external application provides the call-control logic.
   - A. True
   - B. False
3. ARI uses two transports together. Which pair is correct?
   - A. A REST/HTTP API for issuing commands and a WebSocket stream for receiving events
   - B. A TCP line protocol and a stdin/stdout script
   - C. SNMP and SMTP
   - D. Two separate UDP sockets
4. Which two configuration files must be set up to enable ARI?
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. The conventional TCP port for the Asterisk HTTP server (and therefore ARI) is ____.
6. Which dialplan application hands a channel over to an ARI application?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. When a channel enters a Stasis application, which event is sent to the connected client?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Which ARI request creates a mixing point that can join two or more channels together?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. To play a built-in prompt on a channel, which event tells your application that the audio has finished so it can move on?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. The `externalMedia` channel is primarily used to:
    - A. Record a call to a local WAV file
    - B. Stream the call's live audio (RTP) to and from an external application, e.g. an AI/speech engine
    - C. Register a PJSIP endpoint
    - D. Reload the dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
