# WebRTC con Asterisk

WebRTC (Web Real-Time Communication) permette a un browser web di effettuare e ricevere chiamate senza plugin e senza softphone esterni: bastano JavaScript, un microfono e una connessione sicura ad Asterisk. Asterisk è in grado di agire come server WebRTC da Asterisk 11 e, dall'introduzione dello stack PJSIP (`res_pjsip`) in Asterisk 12, questa è diventata la modalità consigliata; in Asterisk 22 la configurazione si è stabilizzata su un numero limitato di opzioni ben definite. Questo capitolo mostra come trasformare un endpoint PJSIP in un telefono basato su browser, come funziona il percorso multimediale sicuro e quando è opportuno utilizzare il supporto WebRTC integrato di Asterisk rispetto a un gateway dedicato.

Tutto ciò che è contenuto in questo capitolo è stato verificato nel laboratorio Asterisk 22 del libro; la configurazione mostrata è la stessa presente in `lab/asterisk/etc`.

## Obiettivi

Al termine di questo capitolo, sarai in grado di:

- Spiegare cosa aggiunge WebRTC ad Asterisk e quando utilizzarlo
- Descrivere in che modo la sicurezza multimediale WebRTC (DTLS-SRTP) e ICE differiscono dal SIP standard
- Abilitare il server HTTP di Asterisk e l'endpoint WebSocket sicuro (`wss`)
- Configurare un trasporto PJSIP `wss` e un endpoint WebRTC con `webrtc=yes`
- Collegare un softphone basato su browser (SIP.js) ed effettuare una chiamata
- Scegliere tra il WebRTC nativo di Asterisk e un gateway multimediale come Janus

## Perché WebRTC con Asterisk

Un endpoint WebRTC è, dal punto di vista di Asterisk, solo un altro endpoint PJSIP. Ciò che cambia è *come* il browser lo raggiunge e come viene protetto il traffico multimediale. Gli utilizzi tipici includono:

- **Click-to-call** su un sito web: un visitatore chiama una coda o un'extension da una pagina web.
- **Agenti basati su web**: un operatore di contact-center lavora interamente nel browser, senza softphone desktop da installare o aggiornare.
- **Chiamate integrate** nella propria applicazione web: ad esempio, il softphone web SipPulse che comunica con Asterisk.
- **Telefoni interni senza installazione**: il personale utilizza una scheda del browser invece di un telefono hardware o di un client installato.

Il grande vantaggio è la portata: ogni browser moderno parla già WebRTC. Il costo è che WebRTC è rigoroso: *richiede* traffico multimediale criptato e un trasporto sicuro, quindi c'è più da configurare rispetto a un telefono SIP UDP standard.

## In che modo WebRTC differisce dal SIP standard

Un telefono SIP regolare comunica tramite UDP/TCP e solitamente trasporta l'audio come RTP in chiaro. Un client browser WebRTC è diverso per tre aspetti importanti, e Asterisk deve gestire ciascuno di essi:

- **La segnalazione viaggia su WebSocket.** Invece del SIP su porta UDP 5060, il browser apre un WebSocket sicuro (`wss://`) verso il server HTTP integrato di Asterisk. I messaggi SIP viaggiano all'interno di quel WebSocket.
- **Il traffico multimediale è sempre criptato con DTLS-SRTP.** I browser rifiutano l'RTP in chiaro. Le due parti eseguono un handshake DTLS (autenticato tramite impronte digitali del certificato scambiate nell'SDP) e ne derivano le chiavi SRTP.
- **La connettività è negoziata con ICE.** Invece di presupporre un IP e una porta raggiungibili, entrambe le parti raccolgono indirizzi candidati (host, STUN-reflexive, TURN-relayed) e li testano finché uno non funziona. RTP e RTCP sono solitamente multiplexati su una singola porta (`rtcp_mux`).

La buona notizia: in Asterisk 22 una singola opzione dell'endpoint, `webrtc=yes`, attiva tutto questo con impostazioni predefinite sensate. Vedremo esattamente cosa imposta.

## Passaggio 1: il server HTTP e il WebSocket

La segnalazione WebRTC è gestita dal server HTTP integrato di Asterisk (`res_http_websocket` espone il percorso `/ws` su di esso). I browser richiedono un WebSocket *sicuro*, quindi abilitiamo TLS. Modifica `http.conf`:

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

Ricarica (`module reload res_http_websocket` o riavvia) e conferma:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

Il browser si connetterà a `wss://your-asterisk:8089/ws`.

### Informazioni sul certificato

Il certificato TLS qui protegge il *WebSocket* (il canale di segnalazione). In un laboratorio, un certificato autofirmato va bene: lo accetti una volta nel browser. In produzione, utilizza un certificato reale (ad esempio Let's Encrypt) il cui nome corrisponda all'host a cui si connette il browser, altrimenti il browser rifiuterà il WebSocket.

Per il laboratorio, `lab/make-certs.sh` genera un certificato autofirmato con `CN=localhost` (più i SAN `localhost`/`127.0.0.1`) e lo scrive in `asterisk/etc/keys/`. Per una distribuzione pubblica, ottieni invece un certificato reale, ad esempio con Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Quindi punta `http.conf` ai file emessi e ricarica `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Assicurati che il nome del certificato corrisponda all'host a cui si connette il browser e rinnovalo (il timer di certbot lo fa automaticamente) prima che scada, altrimenti il WebSocket fallirà.

Questo certificato **non** è lo stesso certificato DTLS utilizzato per criptare il traffico multimediale: Asterisk genera quello automaticamente, come vedremo.

## Passaggio 2: il trasporto WSS

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

Non lasciarti ingannare dal `0.0.0.0:5060` mostrato per il trasporto `wss`: il WebSocket **non** è servito sulla porta 5060. La segnalazione WebRTC è servita dal server HTTP che hai configurato nel Passaggio 1 (porta 8089 per `wss`). Il trasporto PJSIP `wss` è un sottile strato sopra `res_http_websocket`, quindi l'indirizzo `bind` stampato per esso è puramente estetico e può essere ignorato; la porta che conta è `tlsbindaddr` in `http.conf`.

## Passaggio 3: l'endpoint WebRTC

Ora l'endpoint stesso. La chiave è `webrtc=yes`:

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
auth_type=userpass
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` è un interruttore di comodità. È equivalente a impostare manualmente tutte le opzioni richieste da WebRTC. Puoi confermare esattamente cosa ha attivato:

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

Leggendo quell'output:

- `media_encryption: dtls` e `dtls_auto_generate_cert: Yes`: il traffico multimediale è DTLS-SRTP e Asterisk genera automaticamente il certificato DTLS, quindi **non** devi crearne uno tu stesso. L'impronta digitale è pubblicizzata nell'SDP (`SHA-256`).
- `ice_support: true`: Asterisk raccoglie e negozia i candidati ICE.
- `rtcp_mux: true`: RTP e RTCP condividono una porta, come previsto dai browser.
- `use_avpf: true`: il profilo RTP AVPF (feedback), richiesto da WebRTC.

`allow=opus` è consigliato: Opus è il codec preferito dai browser. Asterisk 22 include Opus *passthrough* nel core (il modulo `res_format_attr_opus`), che è sufficiente per inoltrare Opus tra due tratte capaci di gestire Opus senza ricodifica. La *transcodifica* di Opus verso un altro codec richiede il modulo separato `codec_opus`, che la guida ufficiale WebRTC elenca come opzionale ma altamente raccomandato e che installi sopra la build di base; vedi la discussione sui codec in *Designing a VoIP network*. Mantieni `ulaw` come fallback per il bridging verso tratte non WebRTC che non supportano Opus.

## Passaggio 4: ICE, STUN e TURN

Su una LAN piatta, ICE con candidati host è sufficiente e non serve altro. Su Internet, solitamente si aggiunge un server STUN affinché Asterisk e il browser possano scoprire i loro indirizzi pubblici, e un server TURN per i casi in cui il traffico multimediale diretto è impossibile (NAT simmetrico, firewall restrittivi). Punta Asterisk verso di essi in `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Il browser viene configurato con i propri server ICE in JavaScript (la lista `RTCPeerConnection` `iceServers`). Per una distribuzione puramente interna puoi saltare STUN/TURN completamente.

`turnaddr` accetta una porta opzionale (predefinita `3478`); `turnusername` e `turnpassword` si autenticano al relay. STUN aiuta solo un peer a *scoprire* il proprio indirizzo pubblico: quando entrambe le estremità si trovano dietro NAT simmetrico o un firewall restrittivo, il traffico multimediale diretto è impossibile e un relay TURN è l'unica cosa che permette all'audio di fluire.

**Raccomandazione per la produzione:** un server STUN pubblico (come quello di Google) va bene per la scoperta dell'indirizzo, ma **non** fare affidamento su un TURN pubblico per il traffico reale: i relay TURN gestiscono tutto il tuo traffico multimediale, quindi vuoi che siano sotto il tuo controllo. Esegui il tuo server [coturn](https://github.com/coturn/coturn). Un `/etc/turnserver.conf` minimale con credenziali a lungo termine appare così:

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

Fornisci al browser lo stesso server TURN nella sua lista `iceServers` in modo che entrambe le tratte possano utilizzare il relay. Per la produzione con utenti su reti mobili o dietro firewall aziendali, un coturn auto-ospitato è praticamente obbligatorio.

## Passaggio 5: il client browser

Qualsiasi libreria SIP WebRTC funziona; due molto utilizzate sono **SIP.js** e **JsSIP**. Il laboratorio include un softphone SIP.js minimale in `lab/webrtc/index.html`. La parte essenziale è l'URL di trasporto e le credenziali:

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

Due realtà del browser da ricordare:

- **Contesto sicuro.** `getUserMedia` (accesso al microfono) funziona solo su pagine `https://` o `http://localhost`. Servi la pagina tramite HTTPS in produzione.
- **Accetta il certificato una volta.** Con un certificato di laboratorio autofirmato, visita prima `https://your-asterisk:8089/ws` nello stesso browser e accetta l'avviso, altrimenti il WebSocket fallirà silenziosamente.

Il softphone web SipPulse è un client di riferimento di livello professionale costruito su queste stesse primitive.

## Verifica di una chiamata WebRTC

Con il browser registrato, `pjsip show contacts` mostra il contatto dinamico e una chiamata accende il canale:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Se l'audio è unidirezionale o assente, quasi sempre si tratta di ICE o del certificato: vedi la risoluzione dei problemi di seguito.

## Asterisk WebRTC vs gateway multimediale

Asterisk può terminare WebRTC direttamente, ma non è sempre lo strumento giusto:

- **Usa il WebRTC nativo di Asterisk** quando il browser è un *telefono* sul tuo PBX: un operatore, un'extension interna, un click-to-call che finisce nel tuo dialplan. Il browser è solo un altro endpoint e tutto (code, voicemail, IVR) funziona.
- **Usa un gateway dedicato (es. Janus)** quando devi scalare molte sessioni browser indipendentemente dal controllo di chiamata, eseguire l'inoltro selettivo per grandi conferenze/streaming o mantenere il piano multimediale separato dal PBX. Un gateway fa da ponte tra WebRTC e SIP standard, e Asterisk vede quindi una normale tratta SIP.

Molti sistemi reali combinano entrambi: Asterisk per il controllo di chiamata, un gateway per la scalabilità multimediale lato browser. (Questa è l'architettura dietro lo stack di SipPulse.)

## Risoluzione dei problemi

- **Il WebSocket non si connette:** il browser ha rifiutato il certificato TLS. Apri `https://host:8089/ws` direttamente e accettalo, oppure installa un certificato attendibile.
- **Si registra ma non c'è audio:** ICE fallito: aggiungi STUN e TURN se attraversi NAT. Controlla `pjsip set logger on` e osserva i candidati SDP.
- **Audio unidirezionale:** solitamente NAT/ICE su un lato, o un codec senza corrispondenza comune: assicurati `allow=opus,ulaw`.
- **La chiamata cade alla risposta:** handshake DTLS fallito; conferma che `dtls_auto_generate_cert` sia `Yes` e che l'orologio di sistema sia corretto (i certificati sono sensibili al tempo).

## Laboratorio

1. Esegui `./lab.sh up`, poi `bash lab/make-certs.sh` e riavvia Asterisk.
2. Servi `lab/webrtc/index.html` (`python3 -m http.server` da `lab/webrtc`) e aprilo; accetta il certificato su `https://localhost:8089/ws`.
3. Registrati come `webrtc-1000` e chiama `600` (test eco): dovresti sentire te stesso.
4. Dal softphone SipPulse registrato come `6001`, componi `1000` per far squillare il browser.
5. Ispeziona la negoziazione: `pjsip set logger on`, effettua una chiamata e trova l'impronta digitale DTLS e i candidati ICE nell'SDP.

## Riepilogo

WebRTC trasforma un browser in un endpoint Asterisk di prima classe. La ricetta è breve ma rigorosa: abilita il server HTTP con TLS affinché il browser possa aprire un WebSocket sicuro, aggiungi un trasporto PJSIP `wss` e imposta `webrtc=yes` sull'endpoint, il che attiva DTLS-SRTP (con un certificato generato automaticamente), ICE, multiplexing RTP/RTCP e il profilo AVPF. Aggiungi STUN/TURN quando attraversi NAT, servi la tua pagina tramite HTTPS e punta un client SIP.js (o JsSIP) verso `wss://asterisk:8089/ws`. Per telefoni basati su browser sul tuo PBX, il WebRTC nativo di Asterisk è il percorso più semplice; per contenuti multimediali su larga scala, abbinalo a un gateway.

## Quiz

1. Quale trasporto utilizza un client browser WebRTC per trasportare la segnalazione SIP ad Asterisk?
   - A. UDP standard su porta 5060
   - B. Un WebSocket sicuro (`wss://`) verso il server HTTP di Asterisk
   - C. TLS su porta 5061
   - D. Un socket TCP raw su porta 8088

2. Il traffico multimediale WebRTC tra il browser e Asterisk viene criptato utilizzando quale meccanismo?
   - A. SDES-SRTP (chiavi scambiate nell'SDP)
   - B. DTLS-SRTP (chiavi derivate da un handshake DTLS)
   - C. IPsec
   - D. RTP in chiaro: WebRTC non cripta il traffico multimediale

3. Vero o falso: quando imposti `webrtc=yes`, devi generare e installare manualmente il certificato DTLS utilizzato per criptare il traffico multimediale.

4. Su quale porta il server HTTP Asterisk del laboratorio espone il WebSocket **sicuro** per WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Quali delle seguenti opzioni attiva `webrtc=yes` per impostazione predefinita? (Scegli tutte le opzioni corrette.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Riempi lo spazio vuoto: WebRTC negozia la connettività facendo in modo che entrambi i lati raccolgano e testino indirizzi candidati (host, STUN-reflexive, TURN-relayed) utilizzando il framework ________.

7. In `rtp.conf`, quali due impostazioni puntano Asterisk verso un server esterno affinché possa scoprire il suo indirizzo pubblico e inoltrare il traffico multimediale quando i percorsi diretti falliscono? (Scegli tutte le opzioni corrette.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Il percorso URL che il server `res_http_websocket` di Asterisk espone per la segnalazione WebRTC è ________.

9. Secondo il capitolo, quando dovresti ricorrere a un gateway multimediale dedicato (come Janus) invece del WebRTC nativo di Asterisk?
   - A. Ogni volta che un browser deve effettuare una chiamata
   - B. Quando devi scalare molte sessioni multimediali del browser indipendentemente dal controllo di chiamata, eseguire l'inoltro selettivo per grandi conferenze o mantenere il piano multimediale separato dal PBX
   - C. Solo quando il browser non supporta DTLS
   - D. Quando vuoi che la voicemail e l'IVR funzionino per l'endpoint del browser

10. Vero o falso: `getUserMedia` (accesso al microfono) funziona su qualsiasi pagina `http://`, quindi servire il softphone del browser tramite HTTPS è opzionale.

**Risposte:** 1 — B · 2 — B · 3 — Falso (Asterisk genera automaticamente il certificato DTLS; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — Falso (richiesto contesto sicuro: `getUserMedia` funziona solo su `https://` o `http://localhost`)
