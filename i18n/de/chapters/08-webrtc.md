# WebRTC mit Asterisk

WebRTC (Web Real-Time Communication) ermöglicht es einem Webbrowser, Anrufe zu tätigen und zu empfangen, ohne Plugin und ohne externes Softphone – nur JavaScript, ein Mikrofon und eine sichere Verbindung zu Asterisk. Asterisk kann seit Version 11 als WebRTC‑Server fungieren, und seit das PJSIP‑Stack (`res_pjsip`) in Asterisk 12 eingeführt wurde, ist dies der empfohlene Weg; in Asterisk 22 hat sich die Konfiguration auf eine Handvoll gut verstandener Optionen festgelegt. Dieses Kapitel zeigt, wie man einen PJSIP‑Endpoint in ein Browser‑Telefon verwandelt, wie der sichere Medienpfad funktioniert und wann man die integrierte WebRTC‑Unterstützung von Asterisk gegenüber einem dedizierten Gateway einsetzen sollte.

Alles in diesem Kapitel wurde anhand des Asterisk 22‑Labors aus dem Buch verifiziert; die gezeigte Konfiguration entspricht der in `lab/asterisk/etc`.

## Objectives

By the end of this chapter, you should be able to:

- Explain what WebRTC adds to Asterisk and when to use it
- Describe how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- Enable the Asterisk HTTP server and the secure WebSocket (`wss`) endpoint
- Configure a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- Connect a browser softphone (SIP.js) and place a call
- Decide between Asterisk-native WebRTC and a media gateway such as Janus

## Warum WebRTC mit Asterisk

Ein WebRTC‑Endpunkt ist aus Sicht von Asterisk einfach ein weiterer PJSIP‑Endpunkt. Was sich ändert, ist *wie* der Browser ihn erreicht und wie Medien gesichert werden. Typische Anwendungsfälle sind:

- **Click-to-call** auf einer Website — ein Besucher ruft aus einer Webseite eine Queue oder eine Extension an.
- **Web‑basierte Agenten** — ein Contact‑Center‑Agent arbeitet vollständig im Browser, es muss kein Desktop‑Softphone installiert oder aktualisiert werden.
- **Eingebettete Anrufe** in Ihrer eigenen Webanwendung — zum Beispiel das SipPulse‑Web‑Softphone, das mit Asterisk kommuniziert.
- **Zero‑Install‑interne Telefone** — Mitarbeiter nutzen einen Browser‑Tab anstelle eines Hardware‑Phones oder eines installierten Clients.

Der große Vorteil ist die Erreichbarkeit: Jeder moderne Browser unterstützt bereits WebRTC. Der Nachteil ist, dass WebRTC streng ist — es *erfordert* verschlüsselte Medien und einen sicheren Transport, sodass mehr konfiguriert werden muss als bei einem einfachen UDP‑SIP‑Telefon.

## How WebRTC differs from plain SIP

Ein reguläres SIP‑Telefon signalisiert über UDP/TCP und überträgt Audio in der Regel als plain RTP. Ein WebRTC‑Browser‑Client unterscheidet sich in drei wichtigen Punkten, und Asterisk muss jeden davon berücksichtigen:

- **Signaling rides a WebSocket.** Statt SIP über UDP‑Port 5060 öffnet der Browser einen sicheren WebSocket (`wss://`) zum integrierten HTTP‑Server von Asterisk. SIP‑Nachrichten werden innerhalb dieses WebSockets transportiert.
- **Media is always encrypted with DTLS‑SRTP.** Browser lehnen plain RTP ab. Die beiden Seiten führen einen DTLS‑Handshake durch (authentifiziert durch Zertifikats‑Fingerabdrücke, die im SDP ausgetauscht werden) und leiten daraus SRTP‑Schlüssel ab.
- **Connectivity is negotiated with ICE.** Anstatt eine erreichbare IP und einen Port anzunehmen, sammeln beide Seiten Kandidatenadressen (host, STUN‑reflexive, TURN‑relayed) und prüfen sie, bis eine funktioniert. RTP und RTCP werden in der Regel auf einem einzigen Port (`rtcp_mux`) multiplexiert.

Die gute Nachricht: In Asterisk 22 aktiviert eine einzige Endpoint‑Option, `webrtc=yes`, all dies mit sinnvollen Vorgabewerten. Wir werden genau sehen, was dabei gesetzt wird.

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

## Schritt 2 — der WSS-Transport

PJSIP benötigt einen Transport vom Typ `wss`. Fügen Sie ihn zu `pjsip.conf` hinzu:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Überprüfen Sie, ob er geladen wurde:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Lassen Sie sich nicht von dem `0.0.0.0:5060`, das für den `wss`‑Transport angezeigt wird, täuschen – der WebSocket wird **nicht** auf Port 5060 bereitgestellt. Das WebRTC‑Signaling wird vom HTTP‑Server bereitgestellt, den Sie in Schritt 1 konfiguriert haben (Port 8089 für `wss`). Der PJSIP `wss`‑Transport ist ein dünner Wrapper über `res_http_websocket`, sodass die für ihn ausgegebene `bind`‑Adresse rein kosmetisch ist und ignoriert werden kann; der relevante Port ist `tlsbindaddr` in `http.conf`.

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

In einem flachen LAN reicht ICE mit Host‑Kandidaten aus und es wird nichts Weiteres benötigt. Über das Internet fügt man üblicherweise einen STUN‑Server hinzu, damit Asterisk und der Browser ihre öffentlichen Adressen ermitteln können, und einen TURN‑Server für Fälle, in denen direkter Medienverkehr unmöglich ist (symmetrisches NAT, restriktive Firewalls). Zeigen Sie Asterisk darauf in
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Der Browser wird in JavaScript mit eigenen ICE‑Servern konfiguriert (die
`RTCPeerConnection` `iceServers`‑Liste). Für eine rein interne Bereitstellung kann STUN/TURN komplett weggelassen werden.

`turnaddr` nimmt einen optionalen Port (Standard `3478`); `turnusername` und `turnpassword`
authentifizieren sich beim Relay. STUN hilft nur einem Peer, seine öffentliche Adresse *zu entdecken* – wenn beide Enden hinter einem symmetrischen NAT oder einer restriktiven Firewall sitzen, ist direkter Medienverkehr unmöglich und ein TURN‑Relay ist das einzige, was Audio fließen lässt.

**Produktions‑Empfehlung:** Ein öffentlicher STUN‑Server (wie der von Google) ist für die Adressermittlung ausreichend, aber verlassen Sie sich **nicht** auf öffentliche TURN‑Server für echten Datenverkehr – TURN leitet Ihren gesamten Medienverkehr um, daher sollte er unter Ihrer Kontrolle stehen. Betreiben Sie Ihren eigenen
[coturn](https://github.com/coturn/coturn)‑Server. Ein minimaler `/etc/turnserver.conf`
mit langfristigen Anmeldeinformationen sieht so aus:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Dann verweisen Sie Asterisk darauf in `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Geben Sie dem Browser denselben TURN‑Server in seiner `iceServers`‑Liste, damit beide Seiten relayed arbeiten können. Für den Produktionseinsatz mit Nutzern in Mobilnetzen oder hinter Unternehmens‑Firewalls ist ein selbstgehosteter coturn praktisch zwingend erforderlich.

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

## Verifying a WebRTC call

With the browser registered, `pjsip show contacts` shows the dynamic contact, and a
call lights up the channel:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

If audio is one-way or absent, it is almost always ICE or the certificate — see
troubleshooting below.

## Asterisk WebRTC vs ein Media-Gateway

- **Use Asterisk-native WebRTC** wenn der Browser ein *Telefon* an Ihrer PBX ist — ein Agent, eine interne Nebenstelle, ein Click-to-Call, das in Ihrem Dialplan landet. Der Browser ist nur ein weiteres Endpoint und alles (queues, voicemail, IVR) funktioniert.
- **Use a dedicated gateway (e.g. Janus)** wenn Sie viele Browser‑Sitzungen unabhängig von der Anrufsteuerung skalieren müssen, selektives Forwarding für große Konferenzen/Streaming durchführen oder die Media‑Ebene von der PBX getrennt halten wollen. Ein Gateway verbindet WebRTC mit einfachem SIP, und Asterisk sieht dann ein gewöhnliches SIP‑Leg.

Viele reale Systeme kombinieren beides: Asterisk für die Anrufsteuerung, ein Gateway für die medienseitige Skalierung im Browser. (Dies ist die Architektur hinter dem eigenen Stack von SipPulse.)

## Fehlersuche

- **WebSocket verbindet sich nicht:** Der Browser hat das TLS‑Zertifikat abgelehnt. Öffnen Sie `https://host:8089/ws` direkt und akzeptieren Sie es, oder installieren Sie ein vertrauenswürdiges Zertifikat.
- **Registriert, aber kein Audio:** ICE ist fehlgeschlagen — fügen Sie STUN hinzu und TURN, wenn Sie über ein NAT gehen. Prüfen Sie `pjsip set logger on` und sehen Sie sich die SDP‑Kandidaten an.
- **Einweg‑Audio:** In der Regel NAT/ICE auf einer Seite oder ein Codec ohne gemeinsame Übereinstimmung — stellen Sie sicher, dass `allow=opus,ulaw`.
- **Anruf bricht beim Annehmen ab:** DTLS‑Handshake fehlgeschlagen; bestätigen Sie, dass `dtls_auto_generate_cert` **ist** `Yes` und die Systemuhr korrekt ist (Zertifikate sind zeitabhängig).

## Labor

1. Führen Sie `./lab.sh up` aus, dann `bash lab/make-certs.sh` und starten Sie Asterisk neu.  
2. Stellen Sie `lab/webrtc/index.html` bereit (`python3 -m http.server` von `lab/webrtc`) und öffnen Sie es; akzeptieren Sie das Zertifikat bei `https://localhost:8089/ws`.  
3. Registrieren Sie sich als `webrtc-1000` und rufen Sie `600` an (Echo‑Test) — Sie sollten sich selbst hören.  
4. Vom SipPulse Softphone, registriert als `6001`, wählen Sie `1000`, um den Browser zum Klingeln zu bringen.  
5. Untersuchen Sie die Aushandlung: `pjsip set logger on`, tätigen Sie einen Anruf und finden Sie den DTLS‑Fingerabdruck sowie die ICE‑Kandidaten im SDP.

## Zusammenfassung

WebRTC verwandelt einen Browser in einen erstklassigen Asterisk‑Endpoint. Das Vorgehen ist klein, aber streng: Aktivieren Sie den HTTP‑Server mit TLS, damit der Browser einen sicheren WebSocket öffnen kann, fügen Sie einen `wss` PJSIP‑Transport hinzu und setzen Sie `webrtc=yes` am Endpoint — wodurch DTLS‑SRTP (mit einem automatisch erzeugten Zertifikat), ICE, RTP/RTCP‑Multiplexing und das AVPF‑Profil aktiviert werden. Fügen Sie STUN/TURN hinzu, wenn Sie NAT durchqueren, stellen Sie Ihre Seite über HTTPS bereit und richten Sie einen SIP.js‑(oder JsSIP‑)Client auf `wss://asterisk:8089/ws` aus. Für Browser‑Telefone an Ihrer PBX ist Asterisk‑native WebRTC der einfachste Weg; für großskalige Medien koppeln Sie es mit einem Gateway.

## Quiz

1. Which transport does a WebRTC browser client use to carry SIP signaling to
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. WebRTC media between the browser and Asterisk is encrypted using which mechanism?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. True or false: when you set `webrtc=yes`, you must manually generate and install
   the DTLS certificate used to encrypt the media.

4. On which port does the lab's Asterisk HTTP server expose the **secure** WebSocket
   for WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Which of the following does `webrtc=yes` turn on by default? (Choose all that
   apply.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Fill in the blank: WebRTC negotiates connectivity by having both sides gather and
   probe candidate addresses (host, STUN-reflexive, TURN-relayed) using the
   ________ framework.

7. In `rtp.conf`, which two settings point Asterisk at an external server so it can
   discover its public address and relay media when direct paths fail? (Choose all
   that apply.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. The URL path that Asterisk's `res_http_websocket` exposes for WebRTC signaling is
   ________.

9. According to the chapter, when should you reach for a dedicated media gateway
   (such as Janus) instead of Asterisk-native WebRTC?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. True or false: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
