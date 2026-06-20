# The Asterisk REST Interface (ARI)

Il capitolo precedente ha trattato AMI e AGI, i due metodi classici per agganciare logica esterna ad Asterisk. Entrambi precedono il web moderno: AMI fornisce un flusso di eventi grezzo, orientato a linee, su un socket TCP, e AGI consegna un singolo canale a uno script per tutta la durata di una chiamata. Nessuno dei due è stato progettato per il tipo di applicazioni stateful, asincrone e multi‑canale che le persone costruiscono oggi — IVR che interagiscono con servizi web, dashboard click‑to‑call, controller di conferenze o voicebot che trasmettono audio a un motore di riconoscimento vocale.

ARI — l’Asterisk REST Interface — è stato introdotto in Asterisk 12 per colmare questa lacuna, e in Asterisk 22 è l’interfaccia consigliata per lo sviluppo di nuove applicazioni telefoniche. L’idea alla base di ARI è una chiara separazione delle responsabilità: **Asterisk diventa un motore multimediale** (risponde ai canali, mescola i bridge, riproduce e registra audio, invia DTMF), e **la tua applicazione fornisce tutta la logica di controllo delle chiamate** tramite una combinazione di API REST (HTTP) e un flusso di eventi WebSocket.

## Objectives

By the end of this chapter, the reader should be able to:

- Explain what ARI is and how it differs from AMI and AGI
- Decide when ARI is the right interface for a project
- Configure `ari.conf` and `http.conf` to enable ARI and create a user
- Connect to the ARI WebSocket event stream
- Describe the Stasis dialplan application and the `StasisStart`/`StasisEnd` events
- Describe the ARI resource model: channels, bridges, playbacks, recordings, endpoints, and device states
- Write a minimal Stasis application in Python that answers a channel, plays a sound, and hangs up
- Explain what the `externalMedia` channel is and why it matters for AI and voicebot integrations

## What ARI is, and when to use it

ARI è costruito su due trasporti che lavorano insieme:

- **Una API REST (HTTP)** che la tua applicazione chiama per *fare* cose — originare un canale, rispondere, riprodurre un suono, creare un bridge, avviare una registrazione, chiudere. Queste sono normali richieste HTTP (`GET`, `POST`, `DELETE`) contro `http://asterisk-host:8088/ari/...`.
- **Un flusso di eventi WebSocket** sul quale Asterisk *informa* la tua applicazione di ciò che sta accadendo — è stato creato un canale, è arrivata una cifra DTMF, una riproduzione è terminata, un canale ha lasciato la tua applicazione. Gli eventi sono consegnati come oggetti JSON.

Il modello è asincrono: fai una richiesta, e il *risultato* di quella richiesta di solito ritorna più tardi come evento. Per esempio, **`POST`** una richiesta per riprodurre un suono; Asterisk risponde immediatamente con un oggetto `Playback`, e qualche secondo dopo ricevi un evento `PlaybackFinished` quando l’audio è terminato.

Scegli ARI al posto di AMI e AGI quando:

- Hai bisogno di **controllo fine dei canali e dei bridge** — costruire conferenze, parcheggi, code, o flussi di chiamata personalizzati a partire da primitive invece di fare affidamento sulle applicazioni del dialplan.
- La tua applicazione è **stateful e a lunga durata**, gestendo più canali contemporaneamente e reagendo agli eventi su tutti loro.
- Vuoi integrare **servizi web, bus di messaggi, o motori AI/voice** e preferisci JSON su HTTP a un protocollo a riga di comando o a uno script stdin/stdout.
- Stai avviando un **nuovo progetto** e desideri l’interfaccia che il progetto Asterisk raccomanda attivamente.

AMI è ancora lo strumento giusto quando hai solo bisogno di *osservare* il sistema o inviare comandi occasionali (dialer, wallboard, monitoraggio). AGI è ancora comodo per uno script IVR rapido e autonomo. Ma per qualsiasi cosa che orchestri chiamate, ARI è la risposta moderna.

> ARI non sostituisce il dialplan — lo completa. Un canale gira nel dialplan come di consueto fino a quando non raggiunge l’applicazione `Stasis()`, a quel punto il controllo è passato alla tua applicazione ARI. Quando la tua applicazione ha terminato, il canale può essere rimandato al dialplan o chiuso.

## Abilitare ARI: http.conf e ari.conf

ARI si basa sul server HTTP integrato di Asterisk, quindi sono coinvolti due file di configurazione: `http.conf` abilita il server web, e `ari.conf` abilita ARI e definisce i suoi utenti.

### http.conf

Il server HTTP deve essere abilitato e associato a un indirizzo e una porta. La porta ARI convenzionale è **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

Per la produzione dovresti mettere ARI dietro TLS. Asterisk può servire HTTPS direttamente (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), oppure puoi terminare TLS in un reverse proxy davanti alla porta 8088. Su TLS gli URL diventano `https://` e `wss://` invece di `http://` e `ws://`.

Puoi confermare che il server HTTP è attivo dal CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` ha una sezione `[general]` e una sezione per ogni utente.

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

Alcune note su queste opzioni:

- `enabled` attiva o disattiva ARI a livello globale.
- `pretty` formatta le risposte JSON per renderle leggibili dall’uomo; disattivalo in produzione.
- Ogni utente è una sezione nominata con `type=user`.
- `read_only=yes` limita quell’utente a richieste in sola lettura (GET).
- `password_format` può essere `plain` (la password è in chiaro) o `crypt` (una password hashata, generata con `mkpasswd -m sha-512`).
- `permit`, `deny` e `acl` consentono restrizioni IP per utente, seguendo le stesse regole di `acl.conf`.

Dopo aver modificato i file, ricarica i moduli pertinenti (`module reload res_ari.so` e `module reload http.so`) o riavvia Asterisk. Puoi verificare che ARI sia in esecuzione con:

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

`ari show apps` elenca le applicazioni Stasis attualmente registrate dai client connessi. È vuoto finché un client non si connette, che è esattamente ciò che facciamo nel passo successivo.

### L'URL degli eventi WebSocket

Un client si iscrive al flusso di eventi aprendo un WebSocket verso il endpoint `/ari/events`, indicando l’applicazione Stasis che implementa e passando le proprie credenziali:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

I parametri di query sono:

- `app` — il nome della tua applicazione Stasis. È lo stesso nome che utilizzerai nella chiamata `Stasis()` del dialplan. Puoi passare più nomi separati da virgola.
- `api_key` — le credenziali, nella forma `username:password`, corrispondenti a un utente in `ari.conf`.
- `subscribeAll` — booleano opzionale (default `false`); quando `true`, l’applicazione riceve tutti gli eventi, non solo quelli per le risorse di sua proprietà.

Le stesse credenziali `user:pass` sono usate come autenticazione HTTP Basic nelle chiamate REST (o aggiunte come parametro di query `api_key` anche lì).

## Stasis: handing a channel to your application

Il ponte tra il dialplan e ARI è l’applicazione dialplan **`Stasis()`** (il framework sottostante è chiamato anche Stasis). Quando un canale raggiunge `Stasis(appname[,args])`, Asterisk passa quel canale all’applicazione ARI registrata sotto `appname` e interrompe l’esecuzione del dialplan per esso. Il controllo ora appartiene al tuo codice.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Quando il canale entra nell’applicazione, ogni client connesso iscritto a `hello` riceve un evento **`StasisStart`** tramite il WebSocket, contenente l’intero oggetto canale (ID, nome, caller ID, stato e qualsiasi argomento passato a `Stasis()`). Questo è il segnale per iniziare a controllare il canale.

Quando il canale lascia l’applicazione — perché il tuo codice lo ha riportato al dialplan con `continueInDialplan`, o perché è stato chiuso — ricevi un evento **`StasisEnd`**. Dopo che `Stasis()` ritorna al dialplan imposta la variabile di canale `STASISSTATUS` (`SUCCESS` o `FAILED`), così il dialplan può ramificare in base al risultato.

## The ARI resource model

ARI espone gli interni di Asterisk come un piccolo insieme di risorse REST. Ogni risorsa vive sotto `/ari/<resource>` e viene manipolata con i metodi HTTP standard. Le più importanti sono:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point that joins channels | create, add/remove channels, play to the bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

Alcune chiamate REST concrete (percorsi mostrati con il prefisso `/ari` che appare sul wire):

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

Il parametro `media` su una richiesta `play` accetta un URI multimediale. La forma più comune è un URI `sound:` che indica un suono integrato, ad es. `sound:hello-world` o `sound:tt-monkeys`. Quando l’audio termina, Asterisk emette un evento `PlaybackFinished` per quell’ID di riproduzione, ed è così che la tua applicazione sa che può proseguire.

I canali e i bridge sono i due blocchi costitutivi che combini per creare i flussi di chiamata. Per collegare due chiamanti, per esempio, origini o accetti due canali, crei un bridge `mixing` con `POST /ari/bridges`, e aggiungi entrambi i canali con `POST /ari/bridges/{bridgeId}/addChannel`. Per costruire una conferenza, continui semplicemente ad aggiungere canali allo stesso bridge.

## Un esempio pratico: un'applicazione Stasis minimale

Costruiamo la più piccola applicazione ARI utile. Quando viene chiamata qualsiasi estensione, la chiamata entra nella nostra app Stasis, che la risponde, riproduce il classico prompt `hello-world` e termina la chiamata.

### Il dialplan

In `extensions.conf`, invia il canale a Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

Il nome dell'applicazione `hello` corrisponde al `app=hello` che usiamo quando ci connettiamo.

### Il client Python

Questo client utilizza due librerie ben note: `requests` per le chiamate REST e `websocket-client` per lo stream di eventi. Installale con `pip install requests websocket-client`.

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

Esegui lo script, poi componi qualsiasi numero da un endpoint registrato. Dovresti sentire "Hello, world", dopodiché la chiamata viene rilasciata. Sulla console di Asterisk, `ari show apps` elencherà ora `hello` mentre il client è connesso.

Il flusso vale la pena di essere tracciato una volta:

1. Il dialplan esegue `Stasis(hello)`; Asterisk passa il canale alla nostra app e invia un evento `StasisStart`.
2. Rispondiamo al canale, poi chiediamo ad Asterisk di riprodurre `sound:hello-world`. Asterisk restituisce un oggetto `Playback` il cui `id` ricordiamo.
3. Quando l'audio termina, Asterisk invia `PlaybackFinished` con quella riproduzione `id`; cerchiamo il canale e lo terminiamo.
4. Il termine della chiamata fa sì che il canale lasci Stasis, generando un evento `StasisEnd`.

> **Una nota sulle librerie client.** Esiste un wrapper di livello superiore chiamato `ari-py` (il pacchetto `ari`), ma non è più mantenuto ed è stato scritto per un'epoca più vecchia di Python e degli strumenti Swagger. Per nuovi lavori su Asterisk 22, preferisci l'approccio esplicito `requests` + WebSocket mostrato sopra, o una libreria asyncio come `asyncari` se hai bisogno di concorrenza. L'approccio grezzo ti mantiene vicino alle reali chiamate REST e agli eventi, che è esattamente ciò che desideri mentre impari ARI.

## externalMedia: the door to AI and voicebots

Le risorse sopra ti permettono di riprodurre e registrare *file*. Ma le moderne applicazioni vocali — trascrizione speech‑to‑text, voicebot AI, analisi in tempo reale — hanno bisogno del *flusso audio live* di una chiamata consegnato a un processo esterno, e devono poter iniettare audio indietro.

ARI fornisce questo tramite il **`externalMedia` channel**. Una richiesta `POST /ari/channels/externalMedia` crea un canale speciale che, invece di parlare con un telefono, trasmette i media RTP della chiamata a (e da) un host esterno. Colleghi questo canale al canale del chiamante, e ora il tuo programma esterno è nel percorso audio: riceve l’audio del chiamante come RTP e può inviare audio sintetizzato indietro.

La richiesta richiede solo:

- `app` — l’applicazione Stasis che possiede il nuovo canale.
- `format` — il formato audio, ad es. `ulaw` o `slin16`.

`external_host` (il `host:port` della tua applicazione media) è opzionale nello schema — può essere vuoto per una connessione in stile server WebSocket — ma per un voicebot RTP classico lo fornirai. Il parametro `encapsulation` predefinito è `rtp` e `transport` è `udp`, che è esattamente ciò che vuoi per un endpoint media in streaming.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

Questa singola funzionalità è ciò che trasforma Asterisk in un front‑end per l’AI: la rete telefonica termina su Asterisk, ARI orchestra la chiamata, e `externalMedia` invia l’audio a un motore speech/AI e lo riporta indietro. Questo è il meccanismo su cui si basano i servizi AI e i voicebot.

## Sommario

ARI è l'interfaccia moderna e consigliata per costruire applicazioni telefoniche su Asterisk 22. Divide il lavoro in modo netto: Asterisk è il motore multimediale, e la tua applicazione — che parla JSON su HTTP e su un WebSocket — fornisce la logica di controllo delle chiamate. La abiliti tramite `http.conf` (il server web integrato sulla porta 8088) e `ari.conf` (che attiva ARI e definisce gli utenti).

L'applicazione dialplan `Stasis()` passa un canale alla tua app, generando `StasisStart` quando entra e `StasisEnd` quando esce. Da lì manipoli un piccolo insieme di risorse REST — canali, bridge, riproduzioni, registrazioni, endpoint e stati dei dispositivi — per rispondere, riprodurre, registrare, collegare e terminare la chiamata.

Abbiamo creato una minima app Python Stasis che risponde a una chiamata, riproduce un prompt e termina la chiamata, e abbiamo visto come il canale `externalMedia` trasmette RTP in tempo reale a un programma esterno — la base per integrazioni AI e voicebot.

## Quiz

1. ARI è stato introdotto in quale versione di Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. Nel modello ARI, Asterisk agisce come motore multimediale mentre la tua applicazione esterna fornisce la logica di controllo delle chiamate.
   - A. Vero
   - B. Falso
3. ARI utilizza due trasporti insieme. Quale coppia è corretta?
   - A. Un'API REST/HTTP per inviare comandi e un flusso WebSocket per ricevere eventi
   - B. Un protocollo a linea TCP e uno script stdin/stdout
   - C. SNMP e SMTP
   - D. Due socket UDP separati
4. Quali due file di configurazione devono essere impostati per abilitare ARI?
   - A. `manager.conf` e `agi.conf`
   - B. `http.conf` e `ari.conf`
   - C. `sip.conf` e `rtp.conf`
   - D. `modules.conf` e `cdr.conf`
5. La porta TCP convenzionale per il server HTTP di Asterisk (e quindi per ARI) è ____.
6. Quale applicazione del dialplan passa un canale a un'applicazione ARI?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. Quando un canale entra in un'applicazione Stasis, quale evento viene inviato al client connesso?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Quale richiesta ARI crea un punto di mixing che può unire due o più canali insieme?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. Per riprodurre un prompt integrato su un canale, quale evento informa la tua applicazione che l'audio è terminato così può proseguire?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. Il canale `externalMedia` è principalmente usato per:
    - A. Registrare una chiamata in un file WAV locale
    - B. Trasmettere l'audio live della chiamata (RTP) verso e da un'applicazione esterna, ad es. un motore AI/di sintesi vocale
    - C. Registrare un endpoint PJSIP
    - D. Ricaricare il dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
