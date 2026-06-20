# The Asterisk REST Interface (ARI)

O capítulo anterior abordou AMI e AGI, as duas formas clássicas de acoplar lógica externa ao Asterisk. Ambas são anteriores à web moderna: AMI fornece um fluxo bruto de eventos orientado a linhas sobre um socket TCP, e AGI entrega um único canal a um script durante a duração de uma chamada. Nenhuma delas foi projetada para o tipo de aplicações stateful, assíncronas e multi‑canal que as pessoas constroem hoje — IVRs que conversam com serviços web, painéis click‑to‑call, controladores de conferência ou voicebots que transmitem áudio para um motor de reconhecimento de fala.

ARI — a Asterisk REST Interface — foi introduzida no Asterisk 12 para preencher essa lacuna, e no Asterisk 22 é a interface recomendada para construir novas aplicações de telefonia. A ideia por trás do ARI é uma separação limpa de responsabilidades: **Asterisk torna‑se um motor de mídia** (ele atende canais, mistura bridges, reproduz e grava áudio, envia DTMF), e **sua aplicação fornece toda a lógica de controle de chamadas** através de uma combinação de uma API REST (HTTP) e um fluxo de eventos WebSocket.

## Objectives

Ao final deste capítulo, o leitor deverá ser capaz de:

- Explicar o que é ARI e como ele difere de AMI e AGI
- Decidir quando ARI é a interface adequada para um projeto
- Configurar `ari.conf` e `http.conf` para habilitar ARI e criar um usuário
- Conectar ao fluxo de eventos WebSocket do ARI
- Descrever o aplicativo de dialplan Stasis e os eventos `StasisStart`/`StasisEnd`
- Descrever o modelo de recursos do ARI: channels, bridges, playbacks, recordings, endpoints e device states
- Escrever uma aplicação Stasis mínima em Python que atenda um channel, reproduza um som e encerre a chamada
- Explicar o que é o channel `externalMedia` e por que ele é importante para integrações de IA e voicebot

## O que é ARI e quando usá‑lo

ARI é construído sobre dois transportes que trabalham juntos:

- **Uma API REST (HTTP)** que sua aplicação chama para *fazer* coisas — originar um canal, atendê‑lo, reproduzir um som, criar uma ponte, iniciar uma gravação, desligar. Estas são requisições HTTP comuns (`GET`, `POST`, `DELETE`) contra `http://asterisk-host:8088/ari/...`.  
- **Um fluxo de eventos WebSocket** pelo qual o Asterisk *informa* sua aplicação o que está acontecendo — um canal foi criado, um dígito DTMF chegou, uma reprodução terminou, um canal saiu da sua aplicação. Os eventos são entregues como objetos JSON.

O padrão é assíncrono: você faz uma requisição, e o *resultado* dessa requisição geralmente volta depois como um evento. Por exemplo, você `POST` uma requisição para reproduzir um som; o Asterisk responde imediatamente com um objeto `Playback`, e alguns segundos depois você recebe um evento `PlaybackFinished` quando o áudio termina.

Escolha ARI em vez de AMI e AGI quando:

- Você precisa de **controle granular de canais e pontes** — construir conferências, estacionamento, filas ou fluxos de chamada personalizados a partir de primitivas em vez de depender de aplicações do dialplan.  
- Sua aplicação é **stateful e de longa duração**, mantendo vários canais simultaneamente e reagindo a eventos de todos eles.  
- Você quer integrar com **serviços web, barramentos de mensagens ou motores de IA/fala** e prefere JSON sobre HTTP a um protocolo de linha ou a um script stdin/stdout.  
- Você está iniciando um **novo projeto** e deseja a interface que o projeto Asterisk recomenda ativamente.

AMI ainda é a ferramenta correta quando você só precisa *observar* o sistema ou disparar comandos ocasionais (discadores, painéis, monitoramento). AGI ainda é conveniente para um script IVR rápido e autocontido. Mas para qualquer coisa que orquestre chamadas, ARI é a resposta moderna.

> ARI não substitui o dialplan — ele o complementa. Um canal roda no dialplan como de costume até alcançar a aplicação `Stasis()`, ponto em que o controle é passado para sua aplicação ARI. Quando sua aplicação termina, o canal pode ser enviado de volta ao dialplan ou desligado.

## Habilitando ARI: http.conf e ari.conf

ARI funciona sobre o servidor HTTP interno do Asterisk, portanto dois arquivos de configuração são envolvidos: `http.conf` habilita o servidor web, e `ari.conf` habilita o ARI e define seus usuários.

### http.conf

O servidor HTTP deve estar habilitado e vinculado a um endereço e porta. A porta convencional do ARI é **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

Para produção você deve colocar o ARI atrás de TLS. O Asterisk pode servir HTTPS diretamente (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), ou você pode terminar o TLS em um proxy reverso na frente da porta 8088. Sobre TLS as URLs tornam‑se `https://` e `wss://` ao invés de `http://` e `ws://`.

Você pode confirmar que o servidor HTTP está ativo a partir da CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` tem uma seção `[general]` e uma seção por usuário.

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

Algumas observações sobre essas opções:

- `enabled` liga ou desliga o ARI globalmente.
- `pretty` formata as respostas JSON para serem legíveis por humanos; desative em produção.
- Cada usuário é uma seção nomeada com `type=user`.
- `read_only=yes` restringe esse usuário a requisições somente leitura (GET).
- `password_format` pode ser `plain` (a senha está em texto puro) ou `crypt` (uma senha hash, gerada com `mkpasswd -m sha-512`).
- `permit`, `deny` e `acl` permitem restrições de IP por usuário, seguindo as mesmas regras de `acl.conf`.

Depois de editar os arquivos, recarregue os módulos relevantes (`module reload res_ari.so` e `module reload http.so`) ou reinicie o Asterisk. Você pode verificar se o ARI está em execução com:

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

`ari show apps` lista as aplicações Stasis atualmente registradas pelos clientes conectados. Ela está vazia até que um cliente se conecte, que é exatamente o que faremos a seguir.

### URL de eventos WebSocket

Um cliente se inscreve no fluxo de eventos abrindo um WebSocket para o endpoint `/ari/events`, nomeando a aplicação Stasis que implementa e passando suas credenciais:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

Os parâmetros de consulta são:

- `app` — o nome da sua aplicação Stasis. Este é o mesmo nome que você usará na chamada `Stasis()` do dialplan. Você pode passar vários nomes separados por vírgula.
- `api_key` — as credenciais, no formato `username:password`, correspondendo a um usuário em `ari.conf`.
- `subscribeAll` — booleano opcional (padrão `false`); quando `true`, a aplicação recebe todos os eventos, não apenas aqueles dos recursos que possui.

As mesmas credenciais `user:pass` são usadas como autenticação HTTP Basic nas chamadas REST (ou adicionadas como parâmetro de consulta `api_key` lá também).

## Stasis: entregando um canal à sua aplicação

A ponte entre o dialplan e o ARI é a aplicação de dialplan **`Stasis()`** (a estrutura subjacente também se chama Stasis). Quando um canal chega a `Stasis(appname[,args])`, o Asterisk entrega esse canal à aplicação ARI registrada em `appname` e interrompe a execução do dialplan para ele. O controle passa agora para o seu código.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Quando o canal entra na aplicação, todo cliente conectado inscrito em `hello` recebe um evento **`StasisStart`** via WebSocket, contendo o objeto completo do canal (seu ID, nome, caller ID, estado e quaisquer argumentos passados para `Stasis()`). Este é o seu sinal para começar a controlar o canal.

Quando o canal sai da aplicação — porque seu código o devolveu ao dialplan com `continueInDialplan`, ou porque foi encerrado — você recebe um evento **`StasisEnd`**. Após `Stasis()` retornar ao dialplan ele define a variável de canal `STASISSTATUS` (`SUCCESS` ou `FAILED`), permitindo que o dialplan faça ramificações com base no resultado.

## The ARI resource model

ARI exposes Asterisk's internals as a small set of REST resources. Each resource lives under `/ari/<resource>` and is manipulated with standard HTTP methods. The most important ones:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point that joins channels | create, add/remove channels, play to the bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

Some concrete REST calls (paths shown with the `/ari` prefix that appears on the wire):

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

The `media` parameter on a `play` request takes a media URI. The most common form is a `sound:` URI naming a built-in sound, e.g. `sound:hello-world` or `sound:tt-monkeys`. When the audio finishes, Asterisk emits a `PlaybackFinished` event for that playback ID, which is how your application knows it can move on.

Channels and bridges are the two building blocks you combine to make call flows. To connect two callers, for instance, you originate or accept two channels, create a `mixing` bridge with `POST /ari/bridges`, and add both channels to it with `POST /ari/bridges/{bridgeId}/addChannel`. To build a conference, you simply keep adding channels to the same bridge.

## Um exemplo prático: uma aplicação Stasis mínima

Vamos construir a menor aplicação ARI útil. Quando qualquer ramal for discado, a chamada entra em nossa aplicação Stasis, que a atende, reproduz o prompt clássico `hello-world` e encerra a chamada.

### O dialplan

Em `extensions.conf`, envie o canal para Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

O nome da aplicação `hello` corresponde ao `app=hello` que usamos ao conectar.

### O cliente Python

Este cliente usa duas bibliotecas bem conhecidas: `requests` para as chamadas REST e `websocket-client` para o fluxo de eventos. Instale‑as com `pip install requests websocket-client`.

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

Execute o script e, em seguida, disque qualquer número a partir de um endpoint registrado. Você deverá ouvir "Hello, world", após o que a chamada será liberada. No console do Asterisk, `ari show apps` agora listará `hello` enquanto o cliente estiver conectado.

O fluxo vale a pena ser rastreado uma vez:

1. O dialplan executa `Stasis(hello)`; o Asterisk entrega o canal à nossa aplicação e envia um evento `StasisStart`.
2. Atendemos o canal e então pedimos ao Asterisk para reproduzir `sound:hello-world`. O Asterisk devolve um objeto `Playback` cujo `id` lembramos.
3. Quando o áudio termina, o Asterisk envia `PlaybackFinished` com aquela reprodução `id`; localizamos o canal e o encerramos.
4. Encerrar a chamada faz com que o canal saia do Stasis, gerando um evento `StasisEnd`.

> **Uma observação sobre bibliotecas cliente.** Existe um wrapper de nível mais alto chamado `ari-py` (o pacote `ari`), mas ele está sem manutenção e foi escrito para uma era mais antiga do Python e das ferramentas Swagger. Para novos trabalhos no Asterisk 22, prefira a abordagem explícita `requests` + WebSocket mostrada acima, ou uma biblioteca asyncio como `asyncari` se precisar de concorrência. A abordagem direta mantém você próximo das chamadas REST e dos eventos reais, que é exatamente o que se deseja ao aprender ARI.

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

## Resumo

ARI é a interface moderna e recomendada para construir aplicações de telefonia no Asterisk 22. Ela divide o trabalho de forma clara: o Asterisk é o motor de mídia, e sua aplicação — falando JSON via HTTP e um WebSocket — fornece a lógica de controle de chamadas. Você a habilita através de `http.conf` (o servidor web interno na porta 8088) e `ari.conf` (que ativa o ARI e define usuários).

A aplicação de dialplan `Stasis()` entrega um canal para sua app, disparando `StasisStart` quando ele entra e `StasisEnd` quando ele sai. A partir daí você manipula um pequeno conjunto de recursos REST — channels, bridges, playbacks, recordings, endpoints e device states — para atender, reproduzir, gravar, conectar e encerrar chamadas.

Construímos uma aplicação mínima em Python Stasis que atende uma chamada, reproduz um prompt e encerra a chamada, e vimos como o canal `externalMedia` transmite RTP ao vivo para um programa externo — a base para integrações de IA e voicebot.

## Quiz

1. ARI foi introduzido em qual versão do Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. No modelo ARI, o Asterisk atua como motor de mídia enquanto sua aplicação externa fornece a lógica de controle de chamadas.
   - A. Verdadeiro
   - B. Falso
3. ARI usa dois transportes juntos. Qual par está correto?
   - A. Uma API REST/HTTP para emitir comandos e um fluxo WebSocket para receber eventos
   - B. Um protocolo de linha TCP e um script stdin/stdout
   - C. SNMP e SMTP
   - D. Dois sockets UDP separados
4. Quais dois arquivos de configuração devem ser configurados para habilitar o ARI?
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. A porta TCP convencional para o servidor HTTP do Asterisk (e, portanto, para o ARI) é ____.
6. Qual aplicação de dialplan entrega um canal a uma aplicação ARI?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Quando um canal entra em uma aplicação Stasis, qual evento é enviado ao cliente conectado?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Qual requisição ARI cria um ponto de mistura que pode juntar dois ou mais canais?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Para reproduzir um prompt interno em um canal, qual evento informa à sua aplicação que o áudio terminou para que ela possa prosseguir?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. O canal `externalMedia` é usado principalmente para:
    - A. Gravar uma chamada em um arquivo WAV local
    - B. Transmitir o áudio ao vivo da chamada (RTP) para e de uma aplicação externa, por exemplo, um motor de IA/fala
    - C. Registrar um endpoint PJSIP
    - D. Recarregar o dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
