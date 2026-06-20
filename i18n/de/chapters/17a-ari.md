# The Asterisk REST Interface (ARI)

Das vorherige Kapitel behandelte AMI und AGI, die beiden klassischen Methoden, externe Logik an Asterisk anzukoppeln. Beide sind älter als das moderne Web: AMI liefert einen rohen, zeilenorientierten Ereignis‑Stream über einen TCP‑Socket, und AGI übergibt einem Skript einen einzelnen Kanal für die Dauer eines Anrufs. Keines von beidem wurde für die Art von zustandsbehafteten, asynchronen, Multi‑Channel‑Anwendungen konzipiert, die heute gebaut werden — IVRs, die mit Web‑Services kommunizieren, Click‑to‑Call‑Dashboards, Konferenz‑Controller oder Voice‑Bots, die Audio an eine Spracherkennungs‑Engine streamen.

ARI — das Asterisk REST Interface — wurde in Asterisk 12 eingeführt, um diese Lücke zu schließen, und in Asterisk 22 ist es die empfohlene Schnittstelle zum Erstellen neuer Telefonie‑Anwendungen. Die Idee hinter ARI ist eine klare Trennung der Verantwortlichkeiten: **Asterisk wird zu einer Media‑Engine** (es beantwortet Kanäle, mischt Bridges, spielt Audio ab und nimmt es auf, sendet DTMF) und **Ihre Anwendung liefert die gesamte Call‑Control‑Logik** über eine Kombination aus einer REST (HTTP)‑API und einem WebSocket‑Ereignis‑Stream.

## Ziele

- Erklären, was ARI ist und wie es sich von AMI und AGI unterscheidet
- Entscheiden, wann ARI die richtige Schnittstelle für ein Projekt ist
- `ari.conf` und `http.conf` konfigurieren, um ARI zu aktivieren und einen Benutzer anzulegen
- Eine Verbindung zum ARI WebSocket-Ereignisstrom herstellen
- Die Stasis-Dialplan-Anwendung und die `StasisStart`/`StasisEnd`-Ereignisse beschreiben
- Das ARI-Ressourcenmodell beschreiben: channels, bridges, playbacks, recordings, endpoints und device states
- Eine minimale Stasis-Anwendung in Python schreiben, die einen channel annimmt, einen Sound abspielt und auflegt
- Erklären, was der `externalMedia`-Kanal ist und warum er für AI- und Voicebot-Integrationen wichtig ist

## What ARI is, and when to use it

ARI is built on two transports working together:

- **A REST (HTTP) API** that your application calls to *do* things — originate a channel, answer it, play a sound, create a bridge, start a recording, hang up. These are ordinary HTTP requests (`GET`, `POST`, `DELETE`) against `http://asterisk-host:8088/ari/...`.
- **A WebSocket event stream** over which Asterisk *tells* your application what is happening — a channel was created, a DTMF digit arrived, a playback finished, a channel left your application. Events are delivered as JSON objects.

The pattern is asynchronous: you make a request, and the *result* of that request usually comes back later as an event. For example, you `POST` a request to play a sound; Asterisk answers immediately with a `Playback` object, and some seconds later you receive a `PlaybackFinished` event when the audio is done.

Choose ARI over AMI and AGI when:

- You need **fine-grained control of channels and bridges** — building conferences, parking, queues, or custom call flows from primitives instead of relying on dialplan applications.
- Your application is **stateful and long-lived**, holding several channels at once and reacting to events across all of them.
- You want to integrate with **web services, message buses, or AI/speech engines** and prefer JSON over HTTP to a line protocol or a stdin/stdout script.
- You are starting a **new project** and want the interface the Asterisk project actively recommends.

AMI is still the right tool when you only need to *observe* the system or fire occasional commands (dialers, wallboards, monitoring). AGI is still convenient for a quick, self-contained IVR script. But for anything that orchestrates calls, ARI is the modern answer.

> ARI does not replace the dialplan — it complements it. A channel runs in the dialplan as usual until it reaches the `Stasis()` application, at which point control is handed to your ARI application. When your application is done, the channel can be sent back into the dialplan or hung up.

## Enabling ARI: http.conf and ari.conf

ARI rides on top of Asterisk's built-in HTTP server, so two configuration files are involved: `http.conf` enables the web server, and `ari.conf` enables ARI and defines its users.

### http.conf

The HTTP server must be enabled and bound to an address and port. The conventional ARI port is **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

For production you should put ARI behind TLS. Asterisk can serve HTTPS directly (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), or you can terminate TLS in a reverse proxy in front of port 8088. Over TLS the URLs become `https://` and `wss://` instead of `http://` and `ws://`.

You can confirm the HTTP server is up from the CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` has a `[general]` section and one section per user.

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

A few notes on these options:

- `enabled` turns ARI on or off globally.
- `pretty` formats JSON responses to be human-readable; turn it off in production.
- Each user is a named section with `type=user`.
- `read_only=yes` restricts that user to read-only (GET) requests.
- `password_format` may be `plain` (the password is in plaintext) or `crypt` (a hashed password, generated with `mkpasswd -m sha-512`).
- `permit`, `deny`, and `acl` allow per-user IP restrictions, following the same rules as `acl.conf`.

After editing the files, reload the relevant modules (`module reload res_ari.so` and `module reload http.so`) or restart Asterisk. You can verify ARI is running with:

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

`ari show apps` lists the Stasis applications currently registered by connected clients. It is empty until a client connects, which is exactly what we do next.

### The WebSocket events URL

A client subscribes to the event stream by opening a WebSocket to the `/ari/events` endpoint, naming the Stasis application it implements and passing its credentials:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

The query parameters are:

- `app` — the name of your Stasis application. This is the same name you will use in the dialplan's `Stasis()` call. You may pass several comma-separated names.
- `api_key` — the credentials, in the form `username:password`, matching a user in `ari.conf`.
- `subscribeAll` — optional boolean (default `false`); when `true`, the application receives all events, not just those for resources it owns.

The same `user:pass` credentials are used as HTTP Basic auth on the REST calls (or appended as an `api_key` query parameter there too).

## Stasis: Übergabe eines Kanals an Ihre Anwendung

Die Brücke zwischen dem Dialplan und ARI ist die **`Stasis()`** Dialplan‑Anwendung (das zugrunde liegende Framework heißt ebenfalls Stasis). Wenn ein Kanal `Stasis(appname[,args])` erreicht, übergibt Asterisk diesen Kanal an die ARI‑Anwendung, die unter `appname` registriert ist, und stoppt die Ausführung des Dialplans für ihn. Die Kontrolle liegt nun bei Ihrem Code.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Wenn der Kanal die Anwendung betritt, erhält jeder verbundene Client, der bei `hello` abonniert ist, ein **`StasisStart`**‑Ereignis über den WebSocket, das das vollständige Kanalobjekt enthält (seine ID, Name, Caller‑ID, Zustand und alle an `Stasis()` übergebenen Argumente). Das ist Ihr Signal, mit der Steuerung des Kanals zu beginnen.

Wenn der Kanal die Anwendung verlässt – weil Ihr Code ihn mit `continueInDialplan` zurück zum Dialplan verschoben hat oder weil er aufgelegt wurde – erhalten Sie ein **`StasisEnd`**‑Ereignis. Nachdem `Stasis()` zum Dialplan zurückkehrt, setzt es die Kanalvariable `STASISSTATUS` (`SUCCESS` oder `FAILED`), sodass der Dialplan je nach Ergebnis verzweigen kann.

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

## Ein praktisches Beispiel: eine minimale Stasis‑Anwendung

Lassen Sie uns die kleinste nützliche ARI‑Anwendung bauen. Wenn irgendeine Nebenstelle gewählt wird, gelangt der Anruf in unsere Stasis‑App, die ihn annimmt, den klassischen `hello-world`‑Prompt abspielt und auflegt.

### Der Dialplan

In `extensions.conf` wird der Kanal an Stasis gesendet:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Der Anwendungsname `hello` entspricht dem `app=hello`, das wir beim Verbinden verwenden.

### Der Python‑Client

Dieser Client nutzt zwei bekannte Bibliotheken: `requests` für die REST‑Aufrufe und `websocket-client` für den Ereignis‑Stream. Installieren Sie sie mit `pip install requests websocket-client`.

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

Führen Sie das Skript aus und wählen Sie dann irgendeine Nummer von einem registrierten Endpunkt. Sie sollten „Hello, world“ hören, wonach der Anruf beendet wird. Auf der Asterisk‑Konsole wird `ari show apps` nun `hello` auflisten, während der Client verbunden ist.

Der Ablauf lohnt sich einmal nachzuvollziehen:

1. Der Dialplan führt `Stasis(hello)` aus; Asterisk übergibt den Kanal an unsere App und sendet ein `StasisStart`‑Ereignis.
2. Wir nehmen den Kanal an und lassen Asterisk `sound:hello-world` abspielen. Asterisk liefert ein `Playback`‑Objekt, dessen `id` wir merken.
3. Wenn die Audiodatei endet, sendet Asterisk `PlaybackFinished` mit dieser Wiedergabe‑`id`; wir suchen den Kanal und legen auf.
4. Das Auflegen lässt den Kanal Stasis verlassen und erzeugt ein `StasisEnd`‑Ereignis.

> **Ein Hinweis zu Client‑Bibliotheken.** Ein höherwertiger Wrapper namens `ari-py` (das `ari`‑Paket) existiert, ist jedoch nicht mehr gepflegt und wurde für eine ältere Ära von Python und Swagger‑Werkzeugen geschrieben. Für neue Arbeiten an Asterisk 22 bevorzugen Sie den expliziten `requests` + WebSocket‑Ansatz, der oben gezeigt wird, oder eine asyncio‑Bibliothek wie `asyncari`, wenn Sie Parallelität benötigen. Der rohe Ansatz hält Sie nah an den tatsächlichen REST‑Aufrufen und Ereignissen, was genau das ist, was Sie beim Lernen von ARI wollen.

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

## Zusammenfassung

ARI ist die moderne, empfohlene Schnittstelle zum Erstellen von Telefonie‑Anwendungen auf Asterisk 22. Sie trennt die Aufgaben sauber: Asterisk ist die Medien‑Engine und Ihre Anwendung — die JSON über HTTP und einen WebSocket spricht — liefert die Anruf‑Steuerungslogik. Sie aktivieren sie über `http.conf` (den integrierten Web‑Server auf Port 8088) und `ari.conf` (die ARI einschaltet und Benutzer definiert).

Die `Stasis()`‑Dialplan‑Anwendung übergibt einen Kanal an Ihre App und löst `StasisStart` aus, wenn sie betreten wird, sowie `StasisEnd`, wenn sie verlassen wird. Von dort aus manipulieren Sie eine kleine Menge von REST‑Ressourcen — channels, bridges, playbacks, recordings, endpoints und device states — um anzunehmen, abzuspielen, aufzunehmen, zu verbinden und aufzulegen.

Wir haben eine minimale Python‑Stasis‑App gebaut, die einen Anruf annimmt, einen Prompt abspielt und auflegt, und wir haben gesehen, wie der `externalMedia`‑Kanal Live‑RTP an ein externes Programm streamt — die Grundlage für KI‑ und Voice‑Bot‑Integrationen.

## Quiz

1. ARI wurde in welcher Version von Asterisk eingeführt?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. Im ARI‑Modell fungiert Asterisk als Media‑Engine, während Ihre externe Anwendung die Call‑Control‑Logik bereitstellt.
   - A. Wahr
   - B. Falsch
3. ARI verwendet zwei Transportmechanismen zusammen. Welches Paar ist korrekt?
   - A. Eine REST/HTTP‑API zum Senden von Befehlen und ein WebSocket‑Stream zum Empfangen von Events
   - B. Ein TCP‑Zeilenprotokoll und ein stdin/stdout‑Skript
   - C. SNMP und SMTP
   - D. Zwei separate UDP‑Sockets
4. Welche beiden Konfigurationsdateien müssen eingerichtet werden, um ARI zu aktivieren?
   - A. `manager.conf` und `agi.conf`
   - B. `http.conf` und `ari.conf`
   - C. `sip.conf` und `rtp.conf`
   - D. `modules.conf` und `cdr.conf`
5. Der konventionelle TCP‑Port für den Asterisk‑HTTP‑Server (und damit für ARI) ist ____.
6. Welche Dialplan‑Anwendung übergibt einen Kanal an eine ARI‑Anwendung?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Wenn ein Kanal in eine Stasis‑Anwendung eintritt, welches Event wird an den verbundenen Client gesendet?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Welche ARI‑Anfrage erstellt einen Mixing‑Point, der zwei oder mehr Kanäle zusammenführen kann?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Um einen eingebauten Prompt auf einem Kanal abzuspielen, welches Event teilt Ihrer Anwendung mit, dass das Audio beendet ist, sodass sie fortfahren kann?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. Der `externalMedia`‑Kanal wird hauptsächlich verwendet, um:
    - A. Einen Anruf in einer lokalen WAV‑Datei aufzuzeichnen
    - B. Das Live‑Audio (RTP) des Anrufs zu und von einer externen Anwendung zu streamen, z. B. einer KI/Sprach‑Engine
    - C. Einen PJSIP‑Endpoint zu registrieren
    - D. Den Dialplan neu zu laden

**Antworten:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
