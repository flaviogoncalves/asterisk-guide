# The Asterisk REST Interface (ARI)

Das vorherige Kapitel behandelte AMI und AGI, die beiden klassischen Methoden, um Asterisk um externe Logik zu erweitern. Beide stammen aus einer Zeit vor dem modernen Web: AMI bietet einen rohen, zeilenorientierten Event-Stream über einen TCP-Socket, und AGI übergibt für die Dauer eines Anrufs einen einzelnen Kanal an ein Skript. Keine der beiden Methoden wurde für die Art von zustandsbehafteten, asynchronen Multi-Channel-Anwendungen entwickelt, die heute üblich sind — IVRs, die mit Webdiensten kommunizieren, Click-to-Call-Dashboards, Konferenzsteuerungen oder Voicebots, die Audio an eine Spracherkennungs-Engine streamen.

ARI — das Asterisk REST Interface — wurde in Asterisk 12 eingeführt, um diese Lücke zu schließen, und ist in Asterisk 22 die empfohlene Schnittstelle für die Entwicklung neuer Telefonieanwendungen. Die Idee hinter ARI ist eine saubere Trennung der Zuständigkeiten: **Asterisk fungiert als Media-Engine** (es nimmt Kanäle an, mischt Bridges, spielt Audio ab und nimmt es auf, sendet DTMF), und **Ihre Anwendung stellt die gesamte Anrufsteuerungslogik** über eine Kombination aus einer REST (HTTP) API und einem WebSocket-Event-Stream bereit.

## Ziele

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Zu erklären, was ARI ist und wie es sich von AMI und AGI unterscheidet
- Zu entscheiden, wann ARI die richtige Schnittstelle für ein Projekt ist
- `ari.conf` und `http.conf` zu konfigurieren, um ARI zu aktivieren und einen Benutzer zu erstellen
- Eine Verbindung zum ARI WebSocket-Event-Stream herzustellen
- Die Stasis Dialplan-Anwendung und die Events `StasisStart`/`StasisEnd` zu beschreiben
- Das ARI-Ressourcenmodell zu beschreiben: Kanäle, Bridges, Playbacks, Aufzeichnungen, Endpoints und Device States
- Eine minimale Stasis-Anwendung in Python zu schreiben, die einen Kanal annimmt, einen Ton abspielt und auflegt
- Zu erklären, was der `externalMedia` Kanal ist und warum er für KI- und Voicebot-Integrationen wichtig ist

## Was ARI ist und wann man es verwendet

ARI basiert auf zwei zusammenarbeitenden Transportwegen:

- **Eine REST (HTTP) API**, die Ihre Anwendung aufruft, um Dinge zu *tun* — einen Kanal zu initiieren, ihn anzunehmen, einen Ton abzuspielen, eine Bridge zu erstellen, eine Aufzeichnung zu starten, aufzulegen. Dies sind gewöhnliche HTTP-Anfragen (`GET`, `POST`, `DELETE`) an `http://asterisk-host:8088/ari/...`.
- **Ein WebSocket-Event-Stream**, über den Asterisk Ihrer Anwendung *mitteilt*, was passiert — ein Kanal wurde erstellt, eine DTMF-Ziffer kam an, eine Wiedergabe wurde beendet, ein Kanal hat Ihre Anwendung verlassen. Events werden als JSON-Objekte geliefert.

Das Muster ist asynchron: Sie stellen eine Anfrage, und das *Ergebnis* dieser Anfrage kommt normalerweise später als Event zurück. Zum Beispiel senden Sie `POST` eine Anfrage, um einen Ton abzuspielen; Asterisk antwortet sofort mit einem `Playback` Objekt, und einige Sekunden später erhalten Sie ein `PlaybackFinished` Event, wenn das Audio beendet ist.

Wählen Sie ARI anstelle von AMI und AGI, wenn:

- Sie eine **feingranulare Kontrolle über Kanäle und Bridges** benötigen — um Konferenzen, Parken, Warteschlangen oder benutzerdefinierte Anrufverläufe aus Grundelementen aufzubauen, anstatt sich auf Dialplan-Anwendungen zu verlassen.
- Ihre Anwendung **zustandsbehaftet und langlebig** ist, mehrere Kanäle gleichzeitig hält und auf Events über alle hinweg reagiert.
- Sie eine Integration mit **Webdiensten, Message-Bussen oder KI/Sprach-Engines** wünschen und JSON über HTTP einem zeilenbasierten Protokoll oder einem stdin/stdout-Skript vorziehen.
- Sie ein **neues Projekt** starten und die Schnittstelle verwenden möchten, die das Asterisk-Projekt aktiv empfiehlt.

AMI ist immer noch das richtige Werkzeug, wenn Sie das System nur *beobachten* oder gelegentlich Befehle absetzen müssen (Dialer, Wallboards, Monitoring). AGI ist weiterhin praktisch für ein schnelles, in sich geschlossenes IVR-Skript. Aber für alles, was Anrufe orchestriert, ist ARI die moderne Antwort.

> ARI ersetzt den Dialplan nicht — es ergänzt ihn. Ein Kanal läuft wie gewohnt im Dialplan, bis er die `Stasis()` Anwendung erreicht, woraufhin die Kontrolle an Ihre ARI-Anwendung übergeben wird. Wenn Ihre Anwendung fertig ist, kann der Kanal zurück in den Dialplan gesendet oder aufgelegt werden.

## ARI aktivieren: http.conf und ari.conf

ARI läuft auf dem eingebauten HTTP-Server von Asterisk, daher sind zwei Konfigurationsdateien beteiligt: `http.conf` aktiviert den Webserver, und `ari.conf` aktiviert ARI und definiert dessen Benutzer.

### http.conf

Der HTTP-Server muss aktiviert und an eine Adresse und einen Port gebunden sein. Der konventionelle ARI-Port ist **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

Für die Produktion sollten Sie ARI hinter TLS betreiben. Asterisk kann HTTPS direkt bereitstellen (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), oder Sie können TLS in einem Reverse-Proxy vor Port 8088 terminieren. Über TLS werden die URLs zu `https://` und `wss://` anstelle von `http://` und `ws://`.

Sie können über das CLI bestätigen, dass der HTTP-Server läuft:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` hat einen `[general]` Abschnitt und einen Abschnitt pro Benutzer.

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

Einige Anmerkungen zu diesen Optionen:

- `enabled` schaltet ARI global ein oder aus.
- `pretty` formatiert JSON-Antworten so, dass sie für Menschen lesbar sind; schalten Sie dies in der Produktion aus.
- Jeder Benutzer ist ein benannter Abschnitt mit `type=user`.
- `read_only=yes` beschränkt diesen Benutzer auf schreibgeschützte (GET) Anfragen.
- `password_format` kann `plain` (das Passwort steht im Klartext) oder `crypt` (ein gehashtes Passwort, generiert mit `mkpasswd -m sha-512`) sein.
- `permit`, `deny` und `acl` erlauben IP-Beschränkungen pro Benutzer, wobei dieselben Regeln wie bei `acl.conf` gelten.

Nach dem Bearbeiten der Dateien laden Sie die entsprechenden Module neu (`module reload res_ari.so` und `module reload http.so`) oder starten Asterisk neu. Sie können überprüfen, ob ARI läuft mit:

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

`ari show apps` listet die Stasis-Anwendungen auf, die derzeit von verbundenen Clients registriert sind. Dies ist leer, bis ein Client eine Verbindung herstellt, was wir als Nächstes tun.

### Die WebSocket-Events-URL

Ein Client abonniert den Event-Stream, indem er einen WebSocket zum `/ari/events` Endpunkt öffnet, die Stasis-Anwendung benennt, die er implementiert, und seine Anmeldedaten übergibt:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

Die Abfrageparameter sind:

- `app` — der Name Ihrer Stasis-Anwendung. Dies ist derselbe Name, den Sie im `Stasis()` Aufruf des Dialplans verwenden werden. Sie können mehrere durch Kommas getrennte Namen übergeben.
- `api_key` — die Anmeldedaten in der Form `username:password`, passend zu einem Benutzer in `ari.conf`.
- `subscribeAll` — optionaler boolescher Wert (Standard `false`); wenn `true`, empfängt die Anwendung alle Events, nicht nur die für Ressourcen, die sie besitzt.

Dieselben `user:pass` Anmeldedaten werden als HTTP Basic Auth bei den REST-Aufrufen verwendet (oder dort ebenfalls als `api_key` Abfrageparameter angehängt).

## Stasis: Übergabe eines Kanals an Ihre Anwendung

Die Brücke zwischen dem Dialplan und ARI ist die **`Stasis()`** Dialplan-Anwendung (das zugrunde liegende Framework wird ebenfalls Stasis genannt). Wenn ein Kanal `Stasis(appname[,args])` erreicht, übergibt Asterisk diesen Kanal an die ARI-Anwendung, die unter `appname` registriert ist, und stoppt die Ausführung des Dialplans für diesen Kanal. Die Kontrolle liegt nun bei Ihrem Code.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Wenn der Kanal in die Anwendung eintritt, erhält jeder verbundene Client, der `hello` abonniert hat, ein **`StasisStart`** Event über den WebSocket, das das vollständige Kanalobjekt enthält (seine ID, Name, Caller ID, Status und alle an `Stasis()` übergebenen Argumente). Dies ist Ihr Signal, mit der Steuerung des Kanals zu beginnen.

Wenn der Kanal die Anwendung verlässt — weil Ihr Code ihn mit `continueInDialplan` zurück in den Dialplan verschoben hat oder weil aufgelegt wurde — erhalten Sie ein **`StasisEnd`** Event. Nachdem `Stasis()` zum Dialplan zurückgekehrt ist, setzt es die `STASISSTATUS` Kanalvariable (`SUCCESS` oder `FAILED`), sodass der Dialplan je nach Ergebnis verzweigen kann.

## Das ARI-Ressourcenmodell

ARI macht die Interna von Asterisk als eine kleine Menge von REST-Ressourcen verfügbar. Jede Ressource befindet sich unter `/ari/<resource>` und wird mit Standard-HTTP-Methoden manipuliert. Die wichtigsten sind:

| Ressource | Was sie repräsentiert | Beispieloperationen |
|----------|--------------------|--------------------|
| **channels** | Ein einzelner Anrufzweig | originate, answer, play, record, hangup |
| **bridges** | Ein Mischpunkt, der Kanäle verbindet | create, add/remove channels, play to the bridge |
| **playbacks** | Eine laufende Medienwiedergabe | get status, stop, pause/unpause |
| **recordings** | Laufende und gespeicherte Aufnahmen | start, stop, list stored, delete |
| **endpoints** | Konfigurierte Peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Benutzerdefinierte Gerätestatus | list, get, set, delete |

Einige konkrete REST-Aufrufe (Pfade werden mit dem `/ari` Präfix angezeigt, das auf der Leitung erscheint):

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

Der `media` Parameter bei einer `play` Anfrage nimmt einen Medien-URI entgegen. Die gebräuchlichste Form ist ein `sound:` URI, der einen eingebauten Ton benennt, z. B. `sound:hello-world` oder `sound:tt-monkeys`. Wenn das Audio endet, sendet Asterisk ein `PlaybackFinished` Event für diese Playback-ID, woran Ihre Anwendung erkennt, dass sie fortfahren kann.

Kanäle und Bridges sind die beiden Bausteine, die Sie kombinieren, um Anrufverläufe zu erstellen. Um beispielsweise zwei Anrufer zu verbinden, initiieren oder akzeptieren Sie zwei Kanäle, erstellen eine `mixing` Bridge mit `POST /ari/bridges` und fügen beide Kanäle mit `POST /ari/bridges/{bridgeId}/addChannel` hinzu. Um eine Konferenz aufzubauen, fügen Sie einfach weiterhin Kanäle derselben Bridge hinzu.

## Ein praktisches Beispiel: eine minimale Stasis-Anwendung

Lassen Sie uns die kleinste nützliche ARI-Anwendung bauen. Wenn eine Extension gewählt wird, tritt der Anruf in unsere Stasis-App ein, die ihn annimmt, den klassischen `hello-world` Prompt abspielt und auflegt.

### Der Dialplan

Senden Sie den Kanal in `extensions.conf` an Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Der Anwendungsname `hello` entspricht dem `app=hello`, den wir beim Verbinden verwenden.

### Der Python-Client

Dieser Client verwendet zwei bekannte Bibliotheken: `requests` für die REST-Aufrufe und `websocket-client` für den Event-Stream. Installieren Sie diese mit `pip install requests websocket-client`.

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

Führen Sie das Skript aus und wählen Sie dann eine beliebige Nummer von einem registrierten Endpoint. Sie sollten "Hello, world" hören, wonach der Anruf beendet wird. Auf der Asterisk-Konsole listet `ari show apps` nun `hello` auf, während der Client verbunden ist.

Der Ablauf ist es wert, einmal nachverfolgt zu werden:

1. Der Dialplan führt `Stasis(hello)` aus; Asterisk übergibt den Kanal an unsere App und sendet ein `StasisStart` Event.
2. Wir nehmen den Kanal an und bitten Asterisk, `sound:hello-world` abzuspielen. Asterisk gibt ein `Playback` Objekt zurück, dessen `id` wir uns merken.
3. Wenn das Audio endet, sendet Asterisk `PlaybackFinished` mit dieser Playback-ID `id`; wir suchen den Kanal und legen auf.
4. Das Auflegen führt dazu, dass der Kanal Stasis verlässt, was ein `StasisEnd` Event erzeugt.

> **Ein Hinweis zu Client-Bibliotheken.** Ein höherwertiger Wrapper namens `ari-py` (das `ari` Paket) existiert, ist aber ungepflegt und wurde für eine ältere Ära von Python- und Swagger-Tools geschrieben. Bevorzugen Sie für neue Arbeiten mit Asterisk 22 den expliziten `requests` + WebSocket-Ansatz, der oben gezeigt wurde, oder eine asyncio-Bibliothek wie `asyncari`, falls Sie Nebenläufigkeit benötigen. Der rohe Ansatz hält Sie nah an den tatsächlichen REST-Aufrufen und Events, was genau das ist, was Sie beim Erlernen von ARI benötigen.

## externalMedia: das Tor zu KI und Voicebots

Die oben genannten Ressourcen ermöglichen es Ihnen, *Dateien* abzuspielen und aufzunehmen. Aber moderne Sprachanwendungen — Speech-to-Text-Transkription, KI-Voicebots, Echtzeitanalysen — benötigen den *Live-Audiostream* eines Anrufs, der an einen externen Prozess geliefert wird, und sie müssen Audio zurück injizieren.

ARI bietet dies durch den **`externalMedia` Kanal**. Eine `POST /ari/channels/externalMedia` Anfrage erstellt einen speziellen Kanal, der, anstatt mit einem Telefon zu sprechen, die RTP-Medien des Anrufs an einen externen Host streamt (und von dort empfängt). Sie verbinden diesen Kanal mit dem Kanal des Anrufers, und nun befindet sich Ihr externes Programm im Audiopfad: Es empfängt das Audio des Anrufers als RTP und kann synthetisiertes Audio zurücksenden.

Die Anfrage erfordert nur:

- `app` — die Stasis-Anwendung, die den neuen Kanal besitzt.
- `format` — das Audioformat, z. B. `ulaw` oder `slin16`.

`external_host` (die `host:port` Ihrer Medienanwendung) ist im Schema optional — sie kann für eine WebSocket-Server-Verbindung leer sein —, aber für einen klassischen RTP-Voicebot werden Sie sie angeben. Der `encapsulation` Parameter ist standardmäßig `rtp` und `transport` auf `udp`, was genau das ist, was Sie für einen Streaming-Media-Endpoint benötigen.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

Diese einzelne Funktion macht Asterisk zu einem Frontend für KI: Das Telefonnetz endet bei Asterisk, ARI orchestriert den Anruf, und `externalMedia` leitet das Audio an eine Sprach-/KI-Engine und zurück. Dies ist der Mechanismus, auf dem KI-Dienste und Voicebots aufbauen.

## Zusammenfassung

ARI ist die moderne, empfohlene Schnittstelle für die Entwicklung von Telefonieanwendungen auf Asterisk 22. Sie teilt die Arbeit sauber auf: Asterisk ist die Media-Engine, und Ihre Anwendung — die JSON über HTTP und einen WebSocket spricht — stellt die Anrufsteuerungslogik bereit. Sie aktivieren sie über `http.conf` (den eingebauten Webserver auf Port 8088) und `ari.conf` (der ARI einschaltet und Benutzer definiert). Die `Stasis()` Dialplan-Anwendung übergibt einen Kanal an Ihre App und löst `StasisStart` aus, wenn er eintritt, und `StasisEnd`, wenn er sie verlässt. Von dort aus manipulieren Sie eine kleine Menge von REST-Ressourcen — Kanäle, Bridges, Playbacks, Aufzeichnungen, Endpoints und Device States —, um Anrufe anzunehmen, abzuspielen, aufzunehmen, zu verbinden und aufzulegen. Wir haben eine minimale Python-Stasis-App erstellt, die einen Anruf annimmt, einen Prompt abspielt und auflegt, und wir haben gesehen, wie der `externalMedia` Kanal Live-RTP an ein externes Programm streamt — die Grundlage für KI- und Voicebot-Integrationen.

## Quiz

1. ARI wurde in welcher Version von Asterisk eingeführt?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. Im ARI-Modell fungiert Asterisk als Media-Engine, während Ihre externe Anwendung die Anrufsteuerungslogik bereitstellt.
   - A. Wahr
   - B. Falsch
3. ARI verwendet zwei Transportwege zusammen. Welches Paar ist korrekt?
   - A. Eine REST/HTTP API zum Absetzen von Befehlen und ein WebSocket-Stream zum Empfangen von Events
   - B. Ein TCP-Zeilenprotokoll und ein stdin/stdout-Skript
   - C. SNMP und SMTP
   - D. Zwei separate UDP-Sockets
4. Welche zwei Konfigurationsdateien müssen eingerichtet werden, um ARI zu aktivieren?
   - A. `manager.conf` und `agi.conf`
   - B. `http.conf` und `ari.conf`
   - C. `sip.conf` und `rtp.conf`
   - D. `modules.conf` und `cdr.conf`
5. Der konventionelle TCP-Port für den Asterisk HTTP-Server (und damit ARI) ist ____.
6. Welche Dialplan-Anwendung übergibt einen Kanal an eine ARI-Anwendung?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Wenn ein Kanal in eine Stasis-Anwendung eintritt, welches Event wird an den verbundenen Client gesendet?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Welche ARI-Anfrage erstellt einen Mischpunkt, der zwei oder mehr Kanäle miteinander verbinden kann?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Um einen eingebauten Prompt auf einem Kanal abzuspielen, welches Event teilt Ihrer Anwendung mit, dass das Audio beendet ist, damit sie fortfahren kann?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. Der `externalMedia` Kanal wird hauptsächlich verwendet, um:
    - A. Einen Anruf in eine lokale WAV-Datei aufzunehmen
    - B. Das Live-Audio (RTP) des Anrufs an eine externe Anwendung zu streamen und von ihr zu empfangen, z. B. eine KI/Sprach-Engine
    - C. Einen PJSIP-Endpoint zu registrieren
    - D. Den Dialplan neu zu laden

**Antworten:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
