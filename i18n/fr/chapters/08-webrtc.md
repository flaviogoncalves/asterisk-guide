# WebRTC avec Asterisk

WebRTC (Web Real-Time Communication) permet à un navigateur web de passer et de recevoir des appels sans plugin et sans softphone externe — uniquement avec JavaScript, un microphone et une connexion sécurisée à Asterisk. Asterisk peut agir comme serveur WebRTC depuis la version 11, et depuis l’arrivée de la pile PJSIP (`res_pjsip`) dans Asterisk 12, c’est la méthode recommandée ; dans Asterisk 22, la configuration s’est stabilisée autour de quelques options bien comprises. Ce chapitre montre comment transformer un endpoint PJSIP en téléphone de navigateur, comment fonctionne le chemin média sécurisé, et quand il faut privilégier le support WebRTC intégré d’Asterisk plutôt qu’une passerelle dédiée.

Tout le contenu de ce chapitre a été vérifié avec le laboratoire Asterisk 22 du livre ; la configuration présentée est identique à celle de `lab/asterisk/etc`.

## Objectives

By the end of this chapter, you should be able to:

- Explain what WebRTC adds to Asterisk and when to use it
- Describe how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- Enable the Asterisk HTTP server and the secure WebSocket (`wss`) endpoint
- Configure a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- Connect a browser softphone (SIP.js) and place a call
- Decide between Asterisk-native WebRTC and a media gateway such as Janus

## Pourquoi le WebRTC avec Asterisk

A WebRTC endpoint is, from Asterisk's point of view, just another PJSIP endpoint. What changes is *how* the browser reaches it and how media is secured. Typical uses include:

- **Click-to-call** sur un site web — un visiteur appelle une file d'attente ou une extension depuis une page web.
- **Web-based agents** — un agent de centre de contact travaille entièrement dans le navigateur, sans desktop softphone to install or update.
- **Embedded calling** dans votre propre application web — par exemple, le SipPulse web softphone talking to Asterisk.
- **Zero-install internal phones** — le personnel utilise un onglet de navigateur au lieu d'un hardware phone or installed client.

The big advantage is reach: every modern browser already speaks WebRTC. The cost is that WebRTC is strict — it *requires* encrypted media and a secure transport, so there is more to configure than a plain UDP SIP phone.

## How WebRTC differs from plain SIP

Un téléphone SIP classique signale via UDP/TCP et transporte généralement l’audio sous forme de RTP simple. Un client navigateur WebRTC diffère de trois manières importantes, et Asterisk doit s’adapter à chacune d’elles :

- **Signaling rides a WebSocket.** Au lieu de SIP sur le port UDP 5060, le navigateur ouvre un WebSocket sécurisé (`wss://`) vers le serveur HTTP intégré d’Asterisk. Les messages SIP circulent à l’intérieur de ce WebSocket.
- **Media is always encrypted with DTLS-SRTP.** Les navigateurs refusent le RTP simple. Les deux parties effectuent une poignée de main DTLS (authentifiée par les empreintes de certificats échangées dans le SDP) et en dérivent les clés SRTP.
- **Connectivity is negotiated with ICE.** Au lieu de supposer une adresse IP et un port accessibles, les deux parties collectent des adresses candidates (host, STUN‑reflexive, TURN‑relayed) et les testent jusqu’à ce que l’une fonctionne. Le RTP et le RTCP sont généralement multiplexés sur un seul port (`rtcp_mux`).

La bonne nouvelle : dans Asterisk 22, une seule option d’endpoint, `webrtc=yes`, active tout cela avec des valeurs par défaut sensées. Nous verrons exactement ce qu’elle configure.

## Étape 1 — le serveur HTTP et le WebSocket

Le signalement WebRTC est servi par le serveur HTTP intégré d'Asterisk (`res_http_websocket` expose le chemin `/ws` dessus). Les navigateurs exigent un WebSocket *sécurisé*, nous activons donc TLS. Modifiez `http.conf` :

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

Rechargez (`module reload res_http_websocket` ou redémarrez) et confirmez :

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

Le navigateur se connectera à `wss://your-asterisk:8089/ws`.

### À propos du certificat

Le certificat TLS ici sécurise le *WebSocket* (le canal de signalement). Dans un laboratoire, un certificat auto‑signé suffit — vous l’acceptez une fois dans le navigateur. En production, utilisez un vrai certificat (par exemple Let's Encrypt) dont le nom correspond à l’hôte auquel le navigateur se connecte, sinon le navigateur refusera le WebSocket.

Pour le laboratoire, `lab/make-certs.sh` génère un certificat auto‑signé avec `CN=localhost` (plus les SAN `localhost`/`127.0.0.1`) et l’écrit dans `asterisk/etc/keys/`. Pour un déploiement public, obtenez plutôt un vrai certificat — par exemple avec Let's Encrypt :

```
certbot certonly --standalone -d voip.example.com
```

Puis pointez `http.conf` vers les fichiers émis et rechargez `res_http_websocket` :

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Assurez‑vous que le nom du certificat correspond à l’hôte auquel le navigateur se connecte, et renouvelez‑le (le minuteur de certbot le fait automatiquement) avant son expiration, sinon le WebSocket échouera.

Ce certificat n’est **pas** le même que le certificat DTLS utilisé pour chiffrer les médias — Asterisk génère celui‑ci automatiquement, comme nous le verrons.

## Étape 2 — le transport WSS

PJSIP a besoin d'un transport de type `wss`. Ajoutez‑le à `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Vérifiez qu'il a été chargé:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Ne vous laissez pas tromper par le `0.0.0.0:5060` affiché pour le transport `wss` — le WebSocket n'est **pas** servi sur le port 5060. La signalisation WebRTC est fournie par le serveur HTTP que vous avez configuré à l'étape 1 (port 8089 pour `wss`). Le transport PJSIP `wss` est une fine couche d'adaptation au-dessus de `res_http_websocket`, de sorte que l'adresse `bind` affichée est cosmétique et peut être ignorée ; le port qui compte est `tlsbindaddr` dans `http.conf`.

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

- `media_encryption: dtls` and `dtls_auto_generate_cert: Yes` — media is DTLS‑SRTP,
  and Asterisk auto‑generates the DTLS certificate, so you do **not** create one
  yourself. The fingerprint is advertised in the SDP (`SHA-256`).
- `ice_support: true` — Asterisk gathers and negotiates ICE candidates.
- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect.
- `use_avpf: true` — the AVPF RTP profile (feedback), required by WebRTC.

`allow=opus` is recommended — Opus is the codec browsers prefer. Asterisk 22 ships
Opus *passthrough* in core (the `res_format_attr_opus` module), which is enough to
relay Opus between two Opus‑capable legs without re‑encoding. *Transcoding* Opus to
another codec requires the separate `codec_opus` module, which the official WebRTC
guide lists as optional but highly recommended and which you install on top of the
base build; see the codecs discussion in *Designing a VoIP network*. Keep `ulaw` as a
fallback for bridging to non‑WebRTC legs that cannot speak Opus.

## Step 4 — ICE, STUN and TURN

Sur un LAN plat, ICE avec des candidats hôtes suffit et rien d’autre n’est nécessaire. Sur Internet, on ajoute généralement un serveur STUN afin qu’Asterisk et le navigateur puissent découvrir leurs adresses publiques, et un serveur TURN pour les cas où le média direct est impossible (NAT symétrique, pare‑feux restrictifs). Pointez Asterisk vers eux dans
`rtp.conf` :

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Le navigateur est configuré avec ses propres serveurs ICE en JavaScript (la liste `RTCPeerConnection` `iceServers`). Pour un déploiement purement interne, vous pouvez ignorer complètement STUN/TURN.

`turnaddr` accepte un port optionnel (par défaut `3478`) ; `turnusername` et `turnpassword` s’authentifient auprès du relais. STUN ne fait qu’aider un pair à *découvrir* son adresse publique — lorsque les deux extrémités sont derrière un NAT symétrique ou un pare‑feu restrictif, le média direct est impossible et un relais TURN est la seule chose qui permet le flux audio.

**Recommandation en production :** un serveur STUN public (tel que celui de Google) suffit pour la découverte d’adresses, mais **ne comptez pas** sur un TURN public pour le trafic réel — les relais TURN transportent tout votre média, il faut donc qu’ils soient sous votre contrôle. Exécutez votre propre serveur [coturn](https://github.com/coturn/coturn). Un fichier `/etc/turnserver.conf` minimal avec des identifiants à long terme ressemble à :

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Puis pointez Asterisk vers celui‑ci dans `rtp.conf` :

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Donnez au navigateur le même serveur TURN dans sa liste `iceServers` afin que les deux jambes puissent relayer. Pour la production avec des utilisateurs sur des réseaux mobiles ou derrière des pare‑feux d’entreprise, un coturn auto‑hébergé est effectivement obligatoire.

## Étape 5 — le client navigateur

Toute bibliothèque WebRTC SIP fonctionne ; deux très utilisées sont **SIP.js** et **JsSIP**. Le laboratoire inclut un softphone SIP.js minimal à `lab/webrtc/index.html`. L'élément essentiel est l'URL de transport et les identifiants :

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

- **Contexte sécurisé.** `getUserMedia` (accès au microphone) ne fonctionne que sur les pages `https://` ou `http://localhost`. Servez la page via HTTPS en production.
- **Accepter le certificat une fois.** Avec un certificat de laboratoire auto‑signé, visitez `https://your-asterisk:8089/ws` dans le même navigateur d'abord et acceptez l'avertissement, sinon le WebSocket échouera silencieusement.

Le softphone web SipPulse est un client de référence de qualité production construit sur ces mêmes primitives.

## Vérification d'un appel WebRTC

Avec le navigateur enregistré, `pjsip show contacts` affiche le contact dynamique, et un appel allume le canal:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Si l’audio est à sens unique ou absent, c’est presque toujours l’ICE ou le certificat — voir le dépannage ci‑dessous.

## Asterisk WebRTC vs une passerelle média

Asterisk peut terminer le WebRTC directement, mais ce n’est pas toujours l’outil approprié :

- **Use Asterisk-native WebRTC** lorsque le navigateur est un *téléphone* sur votre PBX — un agent, une extension interne, un clic‑to‑call qui aboutit dans votre dialplan. Le navigateur n’est qu’un autre endpoint et tout (queues, voicemail, IVR) fonctionne.
- **Use a dedicated gateway (e.g. Janus)** lorsque vous devez mettre à l’échelle de nombreuses sessions de navigateur indépendamment du contrôle d’appel, effectuer un renvoi sélectif pour de grandes conférences/streaming, ou garder le plan média séparé du PBX. Une passerelle fait le pont entre WebRTC et SIP simple, et Asterisk voit alors une jambe SIP ordinaire.

De nombreux systèmes réels combinent les deux : Asterisk pour le contrôle d’appel, une passerelle pour la mise à l’échelle du média côté navigateur. (C’est l’architecture derrière la pile propre de SipPulse.)

## Dépannage

- **WebSocket won't connect:** le navigateur a rejeté le certificat TLS. Ouvrez `https://host:8089/ws` directement et acceptez‑le, ou installez un certificat de confiance.  
- **Registers but no audio:** ICE a échoué — ajoutez STUN, et TURN si vous êtes derrière un NAT. Vérifiez `pjsip set logger on` et examinez les candidats SDP.  
- **One-way audio:** généralement NAT/ICE d’un côté, ou un codec sans correspondance commune — assurez‑vous que `allow=opus,ulaw`.  
- **Call drops at answer:** la poignée de main DTLS a échoué ; confirmez que `dtls_auto_generate_cert` est `Yes` et que l’horloge du système est correcte (les certificats sont sensibles au temps).

## Laboratoire

1. Exécutez `./lab.sh up`, puis `bash lab/make-certs.sh` et redémarrez Asterisk.
2. Servez `lab/webrtc/index.html` (`python3 -m http.server` depuis `lab/webrtc`) et ouvrez‑le ; acceptez le certificat à `https://localhost:8089/ws`.
3. Enregistrez‑vous en tant que `webrtc-1000` et appelez `600` (test d’écho) — vous devriez vous entendre.
4. Depuis le SipPulse Softphone enregistré sous `6001`, composez `1000` pour faire sonner le navigateur.
5. Inspectez la négociation : `pjsip set logger on`, lancez un appel et trouvez l’empreinte DTLS ainsi que les candidats ICE dans le SDP.

## Résumé

WebRTC transforme un navigateur en un endpoint Asterisk de première classe. La recette est petite mais
stricte : activez le serveur HTTP avec TLS afin que le navigateur puisse ouvrir un WebSocket sécurisé,
ajoutez un `wss` transport PJSIP, et définissez `webrtc=yes` sur l'endpoint — ce qui active
DTLS‑SRTP (avec un certificat auto‑généré), ICE, le multiplexage RTP/RTCP et le
profil AVPF. Ajoutez STUN/TURN lors du franchissement du NAT, servez votre page via HTTPS, et pointez
un client SIP.js (ou JsSIP) vers `wss://asterisk:8089/ws`. Pour les téléphones navigateur sur votre
PBX, le WebRTC natif d'Asterisk est le chemin le plus simple ; pour les médias à grande échelle, associez‑le à une passerelle.

## Quiz

1. Quel transport un client navigateur WebRTC utilise‑t‑il pour transporter le signalement SIP vers
   Asterisk ?
   - A. UDP simple sur le port 5060
   - B. Un WebSocket sécurisé (`wss://`) vers le serveur HTTP d’Asterisk
   - C. TLS sur le port 5061
   - D. Une socket TCP brute sur le port 8088

2. Les médias WebRTC entre le navigateur et Asterisk sont chiffrés à l’aide de quel mécanisme ?
   - A. SDES‑SRTP (clés échangées dans le SDP)
   - B. DTLS‑SRTP (clés dérivées d’une poignée de main DTLS)
   - C. IPsec
   - D. RTP simple — WebRTC ne chiffre pas les médias

3. Vrai ou faux : lorsque vous définissez `webrtc=yes`, vous devez générer et installer manuellement le certificat DTLS utilisé pour chiffrer les médias.

4. Sur quel port le serveur HTTP d’Asterisk du laboratoire expose‑t‑il le WebSocket **sécurisé** pour WebRTC ?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Lequel des éléments suivants `webrtc=yes` active‑t‑il par défaut ? (Choisissez toutes les réponses applicables.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Complétez la phrase : WebRTC négocie la connectivité en faisant rassembler et sonder les adresses candidates (host, STUN‑reflexive, TURN‑relayed) à l’aide du cadre ________.

7. Dans `rtp.conf`, quels deux paramètres indiquent à Asterisk un serveur externe afin qu’il puisse découvrir son adresse publique et relayer les médias lorsque les chemins directs échouent ? (Choisissez toutes les réponses applicables.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Le chemin d’URL que `res_http_websocket` d’Asterisk expose pour le signalement WebRTC est ________.

9. Selon le chapitre, quand devez‑vous recourir à une passerelle média dédiée (comme Janus) au lieu du WebRTC natif d’Asterisk ?
   - A. Chaque fois qu’un navigateur doit passer un appel
   - B. Lorsque vous devez mettre à l’échelle de nombreuses sessions média de navigateur indépendamment du contrôle d’appel, faire du sélective forwarding pour de grandes conférences, ou séparer le plan média du PBX
   - C. Seulement lorsque le navigateur ne supporte pas DTLS
   - D. Lorsque vous voulez que la messagerie vocale et l’IVR fonctionnent pour le point d’accès navigateur

10. Vrai ou faux : `getUserMedia` (accès au microphone) fonctionne sur n’importe quelle page `http://`, donc
    servir le softphone navigateur via HTTPS est optionnel.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
