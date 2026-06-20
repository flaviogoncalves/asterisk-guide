# WebRTC con Asterisk

WebRTC (Web Real-Time Communication) consente a un browser web di effettuare e ricevere chiamate senza plugin e senza softphone esterno — solo JavaScript, un microfono e una connessione sicura ad Asterisk. Asterisk può fungere da server WebRTC sin da Asterisk 11, e da quando lo stack PJSIP (`res_pjsip`) è arrivato in Asterisk 12 è stato il metodo consigliato; in Asterisk 22 la configurazione si è consolidata in un piccolo insieme di opzioni ben comprese. Questo capitolo mostra come trasformare un endpoint PJSIP in un telefono browser, come funziona il percorso multimediale sicuro e quando è opportuno utilizzare il supporto WebRTC integrato di Asterisk rispetto a un gateway dedicato.

Tutto in questo capitolo è stato verificato con il laboratorio Asterisk 22 del libro; la configurazione mostrata è la stessa di `lab/asterisk/etc`.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Spiegare cosa aggiunge WebRTC ad Asterisk e quando usarlo
- Descrivere come la sicurezza multimediale di WebRTC (DTLS-SRTP) e ICE differiscono dal SIP semplice
- Abilitare il server HTTP di Asterisk e l'endpoint WebSocket sicuro (`wss`)
- Configurare un trasporto PJSIP `wss` e un endpoint WebRTC con `webrtc=yes`
- Collegare un softphone browser (SIP.js) e effettuare una chiamata
- Decidere tra WebRTC nativo di Asterisk e un gateway multimediale come Janus

## Perché WebRTC con Asterisk

Un endpoint WebRTC è, dal punto di vista di Asterisk, semplicemente un altro endpoint PJSIP.  
Ciò che cambia è *come* il browser lo raggiunge e come i media sono protetti. Gli usi tipici includono:

- **Click-to-call** su un sito web — un visitatore chiama una coda o un’estensione da una pagina web.  
- **Agenti basati sul web** — un operatore di contact‑center lavora interamente nel browser, senza dover installare o aggiornare un softphone desktop.  
- **Chiamate incorporate** nella tua applicazione web — ad esempio, il softphone web SipPulse che comunica con Asterisk.  
- **Telefonia interna senza installazione** — il personale utilizza una scheda del browser invece di un telefono hardware o di un client installato.  

Il grande vantaggio è la portata: ogni browser moderno supporta già WebRTC. Il costo è che WebRTC è rigido — richiede media crittografati e un trasporto sicuro, quindi c’è più da configurare rispetto a un semplice telefono SIP UDP.

## Come WebRTC differisce dal SIP tradizionale

Un telefono SIP normale segnala su UDP/TCP e di solito trasporta l’audio come RTP semplice. Un client browser WebRTC è diverso in tre modi importanti, e Asterisk deve adeguarsi a ciascuno di essi:

- **Il segnalamento avviene su un WebSocket.** Invece di SIP su UDP porta 5060, il browser apre un WebSocket sicuro (`wss://`) al server HTTP integrato di Asterisk. I messaggi SIP viaggiano all’interno di quel WebSocket.
- **I media sono sempre crittografati con DTLS‑SRTP.** I browser rifiutano RTP semplice. Le due parti eseguono un handshake DTLS (autenticato dalle impronte digitali dei certificati scambiate nell’SDP) e ne derivano le chiavi SRTP.
- **La connettività è negoziata con ICE.** Piuttosto che presumere un IP e una porta raggiungibili, entrambe le parti raccolgono indirizzi candidato (host, STUN‑riflessivo, TURN‑relay) e li sondano finché uno funziona. RTP e RTCP sono di solito multiplexati su una singola porta (`rtcp_mux`).

La buona notizia: in Asterisk 22 un’unica opzione endpoint, `webrtc=yes`, attiva tutto questo con impostazioni predefinite sensate. Vedremo esattamente cosa configura.

## Step 1 — the HTTP server and the WebSocket

WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket`
exposes the `/ws` path on it). Browsers require a *secure* WebSocket, so we enable
TLS. Edit `http.conf`:

```
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC. Browsers require a secure WebSocket (wss://).
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

Reload (`module reload res_http_websocket` or restart) and confirm:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

The browser will connect to `wss://your-asterisk:8089/ws`.

### About the certificate

The TLS certificate here secures the *WebSocket* (the signaling channel). In a lab
a self-signed certificate is fine — you accept it once in the browser. In
production use a real certificate (for example Let's Encrypt) whose name matches
the host the browser connects to, otherwise the browser will refuse the WebSocket.

For the lab, `lab/make-certs.sh` generates a self-signed certificate with
`CN=localhost` (plus `localhost`/`127.0.0.1` SANs) and writes it to
`asterisk/etc/keys/`. For a public deployment, obtain a real certificate instead — for
example with Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Then point `http.conf` at the issued files and reload `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Make sure the certificate name matches the host the browser connects to, and renew it
(certbot's timer does this automatically) before it expires, or the WebSocket will fail.

This certificate is **not** the same as the DTLS certificate used to encrypt the
media — Asterisk generates that one automatically, as we will see.

## Step 2 — il trasporto WSS

PJSIP necessita di un trasporto di tipo `wss`. Aggiungilo a `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verifica che sia stato caricato:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Non lasciarti ingannare dal `0.0.0.0:5060` mostrato per il trasporto `wss` — il WebSocket **non** è servito sulla porta 5060. Il segnalamento WebRTC è servito dal server HTTP che hai configurato nel Passo 1 (porta 8089 per `wss`). Il trasporto PJSIP `wss` è un sottile shim su `res_http_websocket`, quindi l'indirizzo `bind` stampato per esso è puramente estetico e può essere ignorato; la porta che conta è `tlsbindaddr` in `http.conf`.

## Step 3 — the WebRTC endpoint

Now the endpoint itself. The key is `webrtc=yes`:

```
[webrtc-1000]
type=endpoint
context=internal
disallow=all
allow=opus,ulaw
webrtc=yes
transport=transport-wss
aors=webrtc-1000
auth=webrtc-1000

[webrtc-1000]
type=auth
auth_type=digest
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` is a convenience switch. It is equivalent to setting all of the
WebRTC-required options by hand. You can confirm exactly what it turned on:

```
*CLI> pjsip show endpoint webrtc-1000
 dtls_auto_generate_cert            : Yes
 dtls_fingerprint                   : SHA-256
 dtls_setup                         : actpass
 ice_support                        : true
 media_encryption                   : dtls
 rtcp_mux                           : true
 use_avpf                           : true
 webrtc                             : yes
```

Reading that output:

- `media_encryption: dtls` and `dtls_auto_generate_cert: Yes` — media is DTLS-SRTP,
  and Asterisk auto-generates the DTLS certificate, so you do **not** create one
  yourself. The fingerprint is advertised in the SDP (`SHA-256`).
- `ice_support: true` — Asterisk gathers and negotiates ICE candidates.
- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect.
- `use_avpf: true` — the AVPF RTP profile (feedback), required by WebRTC.

`allow=opus` is recommended — Opus is the codec browsers prefer. Asterisk 22 ships
Opus *passthrough* in core (the `res_format_attr_opus` module), which is enough to
relay Opus between two Opus-capable legs without re-encoding. *Transcoding* Opus to
another codec requires the separate `codec_opus` module, which the official WebRTC
guide lists as optional but highly recommended and which you install on top of the
base build; see the codecs discussion in *Designing a VoIP network*. Keep `ulaw` as a
fallback for bridging to non-WebRTC legs that cannot speak Opus.

## Step 4 — ICE, STUN and TURN

Su una LAN piatta, ICE con host candidates è sufficiente e non serve nient'altro. Attraverso
Internet si aggiunge solitamente un server STUN affinché Asterisk e il browser possano scoprire
i loro indirizzi pubblici, e un server TURN per i casi in cui il media diretto è
impossibile (NAT simmetrico, firewall restrittivi). Puntare Asterisk verso di essi in
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Il browser è configurato con i propri server ICE in JavaScript (l'elenco
`RTCPeerConnection` `iceServers`). Per un'installazione puramente interna è possibile omettere
STUN/TURN del tutto.

`turnaddr` accetta una porta opzionale (default `3478`); `turnusername` e `turnpassword`
autenticano al relay. STUN aiuta solo un peer a *scoprire* il proprio indirizzo pubblico — quando
entrambi i lati sono dietro NAT simmetrico o un firewall restrittivo, il media diretto è
impossibile e un relay TURN è l'unica cosa che permette il flusso audio.

**Raccomandazione per la produzione:** un server STUN pubblico (come quello di Google) è adeguato per
scoprire gli indirizzi, ma **non** fare affidamento su TURN pubblico per il traffico reale — i relay TURN
instradano tutto il tuo media, quindi è preferibile averlo sotto il tuo controllo. Esegui il tuo
[coturn](https://github.com/coturn/coturn) server. Un minimo `/etc/turnserver.conf`
con credenziali a lungo termine appare così:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Quindi punta Asterisk verso di esso in `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Fornisci al browser lo stesso server TURN nella sua lista `iceServers` così entrambe le estremità possono fare relay.
Per la produzione con utenti su reti mobili o dietro firewall aziendali, un
coturn auto‑ospitato è praticamente obbligatorio.

## Step 5 — the browser client

Any WebRTC SIP library works; two widely used ones are **SIP.js** and **JsSIP**. The
lab includes a minimal SIP.js softphone at `lab/webrtc/index.html`. The essential
part is the transport URL and the credentials:

```javascript
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
// place a call to the echo test
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();
```

Two browser realities to remember:

- **Secure context.** `getUserMedia` (microphone access) only works on `https://`
  pages or `http://localhost`. Serve the page over HTTPS in production.
- **Accept the cert once.** With a self-signed lab certificate, visit
  `https://your-asterisk:8089/ws` in the same browser first and accept the warning,
  or the WebSocket will fail silently.

The SipPulse web softphone is a production-grade reference client built on these same
primitives.

## Verifica di una chiamata WebRTC

Con il browser registrato, `pjsip show contacts` mostra il contatto dinamico, e una chiamata accende il canale:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Se l'audio è unidirezionale o assente, è quasi sempre dovuto a ICE o al certificato — vedere la risoluzione dei problemi di seguito.

## Asterisk WebRTC vs un gateway multimediale

Asterisk può terminare WebRTC direttamente, ma non è sempre lo strumento giusto:

- **Use Asterisk-native WebRTC** quando il browser è un *telefono* sul tuo PBX — un agente, un interno, un click‑to‑call che arriva nel tuo dialplan. Il browser è solo un altro endpoint e tutto (queues, voicemail, IVR) funziona.
- **Use a dedicated gateway (e.g. Janus)** quando hai bisogno di scalare molte sessioni browser indipendentemente dal controllo delle chiamate, fare forwarding selettivo per grandi conferenze/streaming, o tenere il piano media separato dal PBX. Un gateway collega WebRTC a plain SIP, e Asterisk then sees an ordinary SIP leg.

Many real systems combine both: Asterisk for call control, a gateway for browser-side media scaling. (This is the architecture behind SipPulse's own stack.)

## Risoluzione dei problemi

- **WebSocket non si connette:** il browser ha rifiutato il certificato TLS. Apri `https://host:8089/ws` direttamente e accettalo, oppure installa un certificato attendibile.  
- **Registrazioni ma nessun audio:** ICE fallito — aggiungi STUN e TURN se sei dietro NAT. Controlla `pjsip set logger on` e osserva i candidati SDP.  
- **Audio unidirezionale:** di solito NAT/ICE su un lato, o un codec senza corrispondenza comune — assicurati che `allow=opus,ulaw`.  
- **Chiamata interrotta al rispondere:** handshake DTLS fallito; conferma che `dtls_auto_generate_cert` sia `Yes` e che l’orologio di sistema sia corretto (i certificati sono sensibili al tempo).

## Laboratorio

1. Esegui `./lab.sh up`, poi `bash lab/make-certs.sh` e riavvia Asterisk.
2. Fornisci `lab/webrtc/index.html` (`python3 -m http.server` da `lab/webrtc`) e aprilo; accetta il certificato su `https://localhost:8089/ws`.
3. Registrati come `webrtc-1000` e chiama `600` (test di eco) — dovresti sentirti.
4. Dal Softphone SipPulse registrato come `6001`, componi `1000` per far squillare il browser.
5. Ispeziona la negoziazione: `pjsip set logger on`, effettua una chiamata e trova l'impronta DTLS e i candidati ICE nel SDP.

## Riepilogo

WebRTC trasforma un browser in un endpoint Asterisk di prima classe. La procedura è breve ma rigorosa: abilita il server HTTP con TLS affinché il browser possa aprire un WebSocket sicuro, aggiungi un `wss` trasporto PJSIP e imposta `webrtc=yes` sull'endpoint — che attiva DTLS‑SRTP (con un certificato generato automaticamente), ICE, il multiplexing RTP/RTCP e il profilo AVPF. Aggiungi STUN/TURN quando attraversi un NAT, servi la tua pagina via HTTPS e punta un client SIP.js (o JsSIP) a `wss://asterisk:8089/ws`. Per i telefoni browser sul tuo PBX, il WebRTC nativo di Asterisk è il percorso più semplice; per media su larga scala, accoppialo a un gateway.

## Quiz

1. Quale trasporto usa un client browser WebRTC per trasportare il segnalamento SIP verso
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. I media WebRTC tra il browser e Asterisk sono criptati usando quale meccanismo?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. Vero o falso: quando imposti `webrtc=yes`, devi generare e installare manualmente
   il certificato DTLS usato per criptare i media.

4. Su quale porta il server HTTP di Asterisk del laboratorio espone il **secure** WebSocket
   per WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Quale dei seguenti `webrtc=yes` attiva per impostazione predefinita? (Scegli tutti quelli
   che si applicano.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Completa la frase: WebRTC negozia la connettività facendo raccogliere e
   sondare a entrambe le parti gli indirizzi candidate (host, STUN-reflexive, TURN-relayed) usando il
   ________ framework.

7. In `rtp.conf`, quali due impostazioni indicano ad Asterisk un server esterno così può
   scoprire il suo indirizzo pubblico e inoltrare i media quando i percorsi diretti falliscono? (Scegli tutti
   quelli che si applicano.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Il percorso URL che `res_http_websocket` di Asterisk espone per il segnalamento WebRTC è
   ________.

9. Secondo il capitolo, quando dovresti ricorrere a un gateway media dedicato
   (come Janus) invece del WebRTC nativo di Asterisk?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. Vero o falso: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
