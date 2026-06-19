# WebRTC mit Asterisk

WebRTC (Web Real-Time Communication) ermöglicht es einem Webbrowser, Anrufe ohne Plugins und ohne externes Softphone zu tätigen und zu empfangen — alles, was benötigt wird, ist JavaScript, ein Mikrofon und eine sichere Verbindung zu Asterisk. Asterisk kann seit Asterisk 11 als WebRTC-Server fungieren, und seit der PJSIP-Stack (`res_pjsip`) in Asterisk 12 eingeführt wurde, ist dies der empfohlene Weg; in Asterisk 22 hat sich die Konfiguration auf eine Handvoll gut verständlicher Optionen eingependelt. Dieses Kapitel zeigt, wie man einen PJSIP-endpoint in ein Browser-Telefon verwandelt, wie der sichere Medienpfad funktioniert und wann Sie die integrierte WebRTC-Unterstützung von Asterisk gegenüber einem dedizierten Gateway bevorzugen sollten.

Alles in diesem Kapitel wurde mit dem Asterisk 22-Labor des Buches verifiziert; die gezeigte Konfiguration ist identisch mit der in `lab/asterisk/etc`.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Zu erklären, was WebRTC zu Asterisk hinzufügt und wann es eingesetzt werden sollte
- Zu beschreiben, wie sich WebRTC-Mediensicherheit (DTLS-SRTP) und ICE von einfachem SIP unterscheiden
- Den Asterisk HTTP-Server und den sicheren WebSocket (`wss`) endpoint zu aktivieren
- Einen `wss` PJSIP-transport und einen WebRTC-endpoint mit `webrtc=yes` zu konfigurieren
- Ein Browser-Softphone (SIP.js) zu verbinden und einen Anruf zu tätigen
- Zwischen Asterisk-nativem WebRTC und einem Media-Gateway wie Janus zu entscheiden

## Warum WebRTC mit Asterisk

Ein WebRTC-endpoint ist aus Sicht von Asterisk nur ein weiterer PJSIP-endpoint. Was sich ändert, ist *wie* der Browser ihn erreicht und wie die Medien gesichert werden. Typische Anwendungsfälle sind:

- **Click-to-call** auf einer Website — ein Besucher ruft eine Warteschlange oder eine extension von einer Webseite aus an.
- **Webbasierte Agenten** — ein Contact-Center-Agent arbeitet vollständig im Browser, ohne dass ein Desktop-Softphone installiert oder aktualisiert werden muss.
- **Eingebettete Telefonie** in Ihrer eigenen Webanwendung — zum Beispiel das SipPulse Web-Softphone, das mit Asterisk kommuniziert.
- **Interne Telefone ohne Installation** — Mitarbeiter nutzen einen Browser-Tab anstelle eines Hardware-Telefons oder eines installierten Clients.

Der große Vorteil ist die Reichweite: Jeder moderne Browser spricht bereits WebRTC. Der Preis dafür ist, dass WebRTC streng ist — es *erfordert* verschlüsselte Medien und einen sicheren Transport, daher gibt es mehr zu konfigurieren als bei einem einfachen UDP-SIP-Telefon.

## Wie sich WebRTC von einfachem SIP unterscheidet

Ein reguläres SIP-Telefon signalisiert über UDP/TCP und überträgt Audio normalerweise als einfaches RTP. Ein WebRTC-Browser-Client unterscheidet sich in drei wichtigen Punkten, und Asterisk muss jeden davon erfüllen:

- **Signalisierung erfolgt über WebSocket.** Anstatt SIP über den UDP-Port 5060 zu verwenden, öffnet der Browser einen sicheren WebSocket (`wss://`) zum integrierten HTTP-Server von Asterisk. SIP-Nachrichten werden innerhalb dieses WebSockets übertragen.
- **Medien werden immer mit DTLS-SRTP verschlüsselt.** Browser lehnen einfaches RTP ab. Die beiden Seiten führen einen DTLS-Handshake durch (authentifiziert durch Zertifikats-Fingerabdrücke, die im SDP ausgetauscht werden) und leiten daraus SRTP-Schlüssel ab.
- **Konnektivität wird mit ICE ausgehandelt.** Anstatt eine erreichbare IP und einen Port vorauszusetzen, sammeln beide Seiten Kandidaten-Adressen (host, STUN-reflexive, TURN-relayed) und testen diese, bis eine funktioniert. RTP und RTCP werden normalerweise auf einem einzigen Port gemultiplext (`rtcp_mux`).

Die gute Nachricht: In Asterisk 22 schaltet eine einzige endpoint-Option, `webrtc=yes`, all dies mit sinnvollen Standardwerten ein. Wir werden genau sehen, was diese einstellt.

## Schritt 1 — der HTTP-Server und der WebSocket

Die WebRTC-Signalisierung wird vom integrierten HTTP-Server von Asterisk bereitgestellt (`res_http_websocket` stellt den `/ws` Pfad darauf bereit). Browser erfordern einen *sicheren* WebSocket, daher aktivieren wir TLS. Bearbeiten Sie `http.conf`:

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

Führen Sie einen Reload (`module reload res_http_websocket` oder Neustart) durch und bestätigen Sie:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

Der Browser wird sich mit `wss://your-asterisk:8089/ws` verbinden.

### Über das Zertifikat

Das TLS-Zertifikat sichert hier den *WebSocket* (den Signalisierungskanal). In einer Laborumgebung ist ein selbstsigniertes Zertifikat in Ordnung — Sie akzeptieren es einmal im Browser. Verwenden Sie in der Produktion ein echtes Zertifikat (zum Beispiel Let's Encrypt), dessen Name mit dem Host übereinstimmt, mit dem sich der Browser verbindet, andernfalls wird der Browser den WebSocket ablehnen.

> **[2nd-ed note]** Das Labor liefert `lab/make-certs.sh`, das ein selbstsigniertes Zertifikat mit `CN=localhost` generiert. Dokumentieren Sie für einen öffentlichen Einsatz den Let's Encrypt-Ablauf und verweisen Sie `tlscertfile`/`tlsprivatekey` auf die ausgestellten Dateien.

Dieses Zertifikat ist **nicht** dasselbe wie das DTLS-Zertifikat, das zur Verschlüsselung der Medien verwendet wird — Asterisk generiert dieses automatisch, wie wir sehen werden.

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

> **[2nd-ed note]** Der `wss` Transport gibt eine `0.0.0.0:5060` Bind-Adresse aus, obwohl der eigentliche WebSocket vom HTTP-Server auf Port 8089 bereitgestellt wird. Dies ist zu erwarten: Der `wss` Transport ist ein dünner Aufsatz über `res_http_websocket`; die `bind` Zeile darin ist effektiv kosmetisch. Es ist einen Satz im finalen Text wert, damit Leser nicht durch den Port verwirrt werden.

## Schritt 3 — der WebRTC-endpoint

Nun zum endpoint selbst. Der Schlüssel ist `webrtc=yes`:

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

`webrtc=yes` ist ein Komfort-Schalter. Er entspricht dem manuellen Setzen aller für WebRTC erforderlichen Optionen. Sie können genau bestätigen, was er aktiviert hat:

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

Beim Lesen dieser Ausgabe:

- `media_encryption: dtls` und `dtls_auto_generate_cert: Yes` — Medien sind DTLS-SRTP, und Asterisk generiert das DTLS-Zertifikat automatisch, Sie erstellen also **keines** selbst. Der Fingerabdruck wird im SDP (`SHA-256`) beworben.
- `ice_support: true` — Asterisk sammelt und handelt ICE-Kandidaten aus.
- `rtcp_mux: true` — RTP und RTCP teilen sich einen Port, wie es Browser erwarten.
- `use_avpf: true` — das AVPF RTP-Profil (Feedback), das von WebRTC benötigt wird.

`allow=opus` wird empfohlen — Opus ist der Codec, den Browser bevorzugen. Asterisk 22 liefert Opus *passthrough* im Core (das `res_format_attr_opus` Modul), was ausreicht, um Opus zwischen zwei Opus-fähigen Beinen ohne Neukodierung weiterzuleiten. Das *Transkodieren* von Opus in einen anderen Codec erfordert das separate `codec_opus` Modul, das der offizielle WebRTC-Leitfaden als optional, aber sehr empfehlenswert auflistet und das Sie zusätzlich zur Basisinstallation installieren; siehe die Codec-Diskussion in *Designing a VoIP network*. Behalten Sie `ulaw` als Fallback für die Überbrückung zu Nicht-WebRTC-Beinen bei, die kein Opus sprechen können.

## Schritt 4 — ICE, STUN und TURN

In einem flachen LAN reicht ICE mit Host-Kandidaten aus und es wird nichts weiter benötigt. Über das Internet fügen Sie normalerweise einen STUN-Server hinzu, damit Asterisk und der Browser ihre öffentlichen Adressen entdecken können, sowie einen TURN-Server für Fälle, in denen direkte Medien unmöglich sind (symmetrisches NAT, restriktive Firewalls). Verweisen Sie Asterisk in `rtp.conf` darauf:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Der Browser wird mit seinen eigenen ICE-Servern in JavaScript konfiguriert (die `RTCPeerConnection` `iceServers` Liste). Für einen rein internen Einsatz können Sie STUN/TURN komplett überspringen.

> **[2nd-ed note]** Überprüfen Sie, ob ein selbst gehostetes coturn für die Produktion empfohlen werden sollte (die meisten echten Implementierungen benötigen TURN). Fügen Sie ggf. ein kurzes coturn-Konfigurationsbeispiel hinzu.

## Schritt 5 — der Browser-Client

Jede WebRTC-SIP-Bibliothek funktioniert; zwei weit verbreitete sind **SIP.js** und **JsSIP**. Das Labor enthält ein minimales SIP.js-Softphone unter `lab/webrtc/index.html`. Der wesentliche Teil ist die Transport-URL und die Anmeldedaten:

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

Zwei Browser-Realitäten, an die man sich erinnern sollte:

- **Sicherer Kontext.** `getUserMedia` (Mikrofonzugriff) funktioniert nur auf `https://` Seiten oder `http://localhost`. Stellen Sie die Seite in der Produktion über HTTPS bereit.
- **Zertifikat einmal akzeptieren.** Besuchen Sie bei einem selbstsignierten Laborzertifikat zuerst `https://your-asterisk:8089/ws` im selben Browser und akzeptieren Sie die Warnung, sonst wird der WebSocket stillschweigend fehlschlagen.

Das SipPulse Web-Softphone ist ein produktionsreifer Referenz-Client, der auf denselben Grundelementen aufbaut.

## Überprüfung eines WebRTC-Anrufs

Wenn der Browser registriert ist, zeigt `pjsip show contacts` den dynamischen Kontakt an, und ein Anruf lässt den Kanal aufleuchten:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Wenn Audio einseitig oder abwesend ist, liegt es fast immer an ICE oder dem Zertifikat — siehe Fehlerbehebung unten.

## Asterisk WebRTC vs. ein Media-Gateway

Asterisk kann WebRTC direkt terminieren, aber es ist nicht immer das richtige Werkzeug:

- **Verwenden Sie Asterisk-natives WebRTC**, wenn der Browser ein *Telefon* an Ihrer PBX ist — ein Agent, eine interne extension, ein Click-to-call, das in Ihrem dialplan landet. Der Browser ist nur ein weiterer endpoint und alles (Warteschlangen, voicemail, IVR) funktioniert.
- **Verwenden Sie ein dediziertes Gateway (z. B. Janus)**, wenn Sie viele Browser-Sitzungen unabhängig von der Anrufsteuerung skalieren, selektives Forwarding für große Konferenzen/Streaming durchführen oder die Medienebene von der PBX getrennt halten müssen. Ein Gateway überbrückt WebRTC zu einfachem SIP, und Asterisk sieht dann ein gewöhnliches SIP-Bein.

Viele echte Systeme kombinieren beides: Asterisk für die Anrufsteuerung, ein Gateway für die browserseitige Medienskalierung. (Dies ist die Architektur hinter der eigenen Stack von SipPulse.)

## Fehlerbehebung

- **WebSocket verbindet nicht:** Der Browser hat das TLS-Zertifikat abgelehnt. Öffnen Sie `https://host:8089/ws` direkt und akzeptieren Sie es, oder installieren Sie ein vertrauenswürdiges Zertifikat.
- **Registriert, aber kein Audio:** ICE fehlgeschlagen — fügen Sie STUN hinzu, und TURN bei NAT-Durchquerung. Prüfen Sie `pjsip set logger on` und schauen Sie sich die SDP-Kandidaten an.
- **Einseitiges Audio:** Normalerweise NAT/ICE auf einer Seite oder ein Codec ohne gemeinsame Übereinstimmung — stellen Sie `allow=opus,ulaw` sicher.
- **Anruf bricht bei Annahme ab:** DTLS-Handshake fehlgeschlagen; bestätigen Sie, dass `dtls_auto_generate_cert` auf `Yes` steht und die Systemzeit korrekt ist (Zertifikate sind zeitkritisch).

## Labor

1. Führen Sie `./lab.sh up` aus, dann `bash lab/make-certs.sh` und starten Sie Asterisk neu.
2. Stellen Sie `lab/webrtc/index.html` bereit (`python3 -m http.server` von `lab/webrtc`) und öffnen Sie es; akzeptieren Sie das Zertifikat unter `https://localhost:8089/ws`.
3. Registrieren Sie sich als `webrtc-1000` und rufen Sie `600` (Echo-Test) an — Sie sollten sich selbst hören.
4. Wählen Sie vom SipPulse Softphone, das als `6001` registriert ist, `1000`, um den Browser anzurufen.
5. Untersuchen Sie die Aushandlung: `pjsip set logger on`, tätigen Sie einen Anruf und finden Sie den DTLS-Fingerabdruck und die ICE-Kandidaten im SDP.

## Zusammenfassung

WebRTC macht aus einem Browser einen vollwertigen Asterisk-endpoint. Das Rezept ist klein, aber streng: Aktivieren Sie den HTTP-Server mit TLS, damit der Browser einen sicheren WebSocket öffnen kann, fügen Sie einen `wss` PJSIP-transport hinzu und setzen Sie `webrtc=yes` auf dem endpoint — was DTLS-SRTP (mit einem automatisch generierten Zertifikat), ICE, RTP/RTCP-Multiplexing und das AVPF-Profil einschaltet. Fügen Sie STUN/TURN hinzu, wenn Sie NAT durchqueren, stellen Sie Ihre Seite über HTTPS bereit und verweisen Sie einen SIP.js (oder JsSIP) Client auf `wss://asterisk:8089/ws`. Für Browser-Telefone an Ihrer PBX ist Asterisk-natives WebRTC der einfachste Weg; für großskalige Medien koppeln Sie es mit einem Gateway.

## Quiz

1. Welchen Transport verwendet ein WebRTC-Browser-Client, um SIP-Signalisierung zu Asterisk zu übertragen?
   - A. Einfaches UDP auf Port 5060
   - B. Ein sicherer WebSocket (`wss://`) zum HTTP-Server von Asterisk
   - C. TLS auf Port 5061
   - D. Ein roher TCP-Socket auf Port 8088

2. WebRTC-Medien zwischen dem Browser und Asterisk werden mit welchem Mechanismus verschlüsselt?
   - A. SDES-SRTP (Schlüssel im SDP ausgetauscht)
   - B. DTLS-SRTP (Schlüssel aus einem DTLS-Handshake abgeleitet)
   - C. IPsec
   - D. Einfaches RTP — WebRTC verschlüsselt Medien nicht

3. Wahr oder falsch: Wenn Sie `webrtc=yes` setzen, müssen Sie das DTLS-Zertifikat, das zur Verschlüsselung der Medien verwendet wird, manuell generieren und installieren.

4. Auf welchem Port stellt der HTTP-Server von Asterisk im Labor den **sicheren** WebSocket für WebRTC bereit?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Welches der folgenden aktiviert `webrtc=yes` standardmäßig? (Wählen Sie alle zutreffenden aus.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Füllen Sie die Lücke aus: WebRTC handelt Konnektivität aus, indem beide Seiten Kandidaten-Adressen (host, STUN-reflexive, TURN-relayed) sammeln und testen, unter Verwendung des ________ Frameworks.

7. Welche zwei Einstellungen in `rtp.conf` verweisen Asterisk auf einen externen Server, damit es seine öffentliche Adresse entdecken und Medien weiterleiten kann, wenn direkte Pfade fehlschlagen? (Wählen Sie alle zutreffenden aus.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Der URL-Pfad, den der `res_http_websocket` von Asterisk für WebRTC-Signalisierung bereitstellt, ist ________.

9. Wann sollten Sie laut Kapitel zu einem dedizierten Media-Gateway (wie Janus) greifen, anstatt zu Asterisk-nativem WebRTC?
   - A. Immer wenn ein Browser einen Anruf tätigen muss
   - B. Wenn Sie viele Browser-Mediensitzungen unabhängig von der Anrufsteuerung skalieren, selektives Forwarding für große Konferenzen durchführen oder die Medienebene von der PBX getrennt halten müssen
   - C. Nur wenn der Browser DTLS nicht unterstützt
   - D. Wenn Sie möchten, dass voicemail und IVR für den Browser-endpoint funktionieren

10. Wahr oder falsch: `getUserMedia` (Mikrofonzugriff) funktioniert auf jeder `http://` Seite, daher ist die Bereitstellung des Browser-Softphones über HTTPS optional.

**Antworten:** 1 — B · 2 — B · 3 — Falsch (Asterisk generiert das DTLS-Zertifikat automatisch; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — Falsch (sicherer Kontext erforderlich: `getUserMedia` funktioniert nur auf `https://` oder `http://localhost`)
