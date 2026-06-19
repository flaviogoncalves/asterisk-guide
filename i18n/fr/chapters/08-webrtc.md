# WebRTC avec Asterisk

WebRTC (Web Real-Time Communication) permet à un navigateur web d'émettre et de recevoir des appels sans plugin ni softphone externe — juste avec JavaScript, un microphone et une connexion sécurisée vers Asterisk. Asterisk est capable d'agir comme un serveur WebRTC depuis Asterisk 11, et depuis l'arrivée de la pile PJSIP (`res_pjsip`) dans Asterisk 12, c'est la méthode recommandée pour le faire ; dans Asterisk 22, la configuration s'est stabilisée autour d'une poignée d'options bien comprises. Ce chapitre montre comment transformer un endpoint PJSIP en téléphone par navigateur, comment fonctionne le chemin média sécurisé, et quand vous devriez opter pour le support WebRTC natif d'Asterisk plutôt que pour une passerelle dédiée.

Tout ce qui est présenté dans ce chapitre est vérifié par rapport au labo Asterisk 22 du livre ; la configuration montrée est la même que dans `lab/asterisk/etc`.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Expliquer ce que WebRTC apporte à Asterisk et quand l'utiliser
- Décrire en quoi la sécurité média WebRTC (DTLS-SRTP) et ICE diffèrent du SIP standard
- Activer le serveur HTTP d'Asterisk et l'endpoint WebSocket sécurisé (`wss`)
- Configurer un transport PJSIP `wss` et un endpoint WebRTC avec `webrtc=yes`
- Connecter un softphone par navigateur (SIP.js) et passer un appel
- Choisir entre le WebRTC natif d'Asterisk et une passerelle média telle que Janus

## Pourquoi WebRTC avec Asterisk

Un endpoint WebRTC est, du point de vue d'Asterisk, juste un autre endpoint PJSIP. Ce qui change, c'est la *manière* dont le navigateur l'atteint et dont le média est sécurisé. Les usages typiques incluent :

- **Click-to-call** sur un site web — un visiteur appelle une file d'attente ou une extension depuis une page web.
- **Agents basés sur le web** — un agent de centre de contact travaille entièrement dans le navigateur, sans softphone de bureau à installer ou mettre à jour.
- **Appels intégrés** dans votre propre application web — par exemple, le softphone web SipPulse communiquant avec Asterisk.
- **Téléphones internes sans installation** — le personnel utilise un onglet de navigateur au lieu d'un téléphone matériel ou d'un client installé.

Le grand avantage est la portée : chaque navigateur moderne parle déjà WebRTC. Le coût est que WebRTC est strict — il *exige* des médias chiffrés et un transport sécurisé, il y a donc plus à configurer qu'un téléphone SIP UDP classique.

## Comment WebRTC diffère du SIP standard

Un téléphone SIP classique communique via UDP/TCP et transporte généralement l'audio sous forme de RTP brut. Un client navigateur WebRTC est différent de trois manières importantes, et Asterisk doit correspondre à chacune d'elles :

- **La signalisation passe par un WebSocket.** Au lieu du SIP sur le port UDP 5060, le navigateur ouvre un WebSocket sécurisé (`wss://`) vers le serveur HTTP intégré d'Asterisk. Les messages SIP voyagent à l'intérieur de ce WebSocket.
- **Le média est toujours chiffré avec DTLS-SRTP.** Les navigateurs refusent le RTP brut. Les deux parties effectuent une poignée de main DTLS (authentifiée par des empreintes de certificat échangées dans le SDP) et en dérivent des clés SRTP.
- **La connectivité est négociée avec ICE.** Plutôt que de supposer une IP et un port accessibles, les deux côtés collectent des adresses candidates (hôte, STUN-réflexif, TURN-relais) et les sondent jusqu'à ce qu'une fonctionne. Le RTP et le RTCP sont généralement multiplexés sur un seul port (`rtcp_mux`).

La bonne nouvelle : dans Asterisk 22, une seule option d'endpoint, `webrtc=yes`, active tout cela avec des paramètres par défaut judicieux. Nous verrons exactement ce qu'elle active.

## Étape 1 — le serveur HTTP et le WebSocket

La signalisation WebRTC est servie par le serveur HTTP intégré d'Asterisk (`res_http_websocket` expose le chemin `/ws` sur celui-ci). Les navigateurs exigent un WebSocket *sécurisé*, nous activons donc le TLS. Modifiez `http.conf` :

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

Le certificat TLS ici sécurise le *WebSocket* (le canal de signalisation). Dans un labo, un certificat auto-signé suffit — vous l'acceptez une fois dans le navigateur. En production, utilisez un vrai certificat (par exemple Let's Encrypt) dont le nom correspond à l'hôte auquel le navigateur se connecte, sinon le navigateur refusera le WebSocket.

Pour le labo, `lab/make-certs.sh` génère un certificat auto-signé avec `CN=localhost` (plus les SAN `localhost`/`127.0.0.1`) et l'écrit dans `asterisk/etc/keys/`. Pour un déploiement public, obtenez plutôt un vrai certificat — par exemple avec Let's Encrypt :

```
certbot certonly --standalone -d voip.example.com
```

Puis pointez `http.conf` vers les fichiers émis et rechargez `res_http_websocket` :

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Assurez-vous que le nom du certificat correspond à l'hôte auquel le navigateur se connecte, et renouvelez-le (le timer de certbot le fait automatiquement) avant qu'il n'expire, sinon le WebSocket échouera.

Ce certificat n'est **pas** le même que le certificat DTLS utilisé pour chiffrer le média — Asterisk génère celui-là automatiquement, comme nous le verrons.

## Étape 2 — le transport WSS

PJSIP a besoin d'un transport de type `wss`. Ajoutez-le à `pjsip.conf` :

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Vérifiez qu'il est chargé :

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Ne soyez pas induit en erreur par le `0.0.0.0:5060` affiché pour le transport `wss` — le WebSocket n'est **pas** servi sur le port 5060. La signalisation WebRTC est servie par le serveur HTTP que vous avez configuré à l'étape 1 (port 8089 pour `wss`). Le transport PJSIP `wss` est une fine couche au-dessus de `res_http_websocket`, donc l'adresse `bind` affichée pour lui est cosmétique et peut être ignorée ; le port qui compte est `tlsbindaddr` dans `http.conf`.

## Étape 3 — l'endpoint WebRTC

Maintenant, l'endpoint lui-même. La clé est `webrtc=yes` :

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

`webrtc=yes` est un commutateur de commodité. Il équivaut à définir manuellement toutes les options requises par WebRTC. Vous pouvez confirmer exactement ce qu'il a activé :

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

En lisant cette sortie :

- `media_encryption: dtls` et `dtls_auto_generate_cert: Yes` — le média est en DTLS-SRTP, et Asterisk auto-génère le certificat DTLS, vous n'en créez donc **pas** vous-même. L'empreinte est annoncée dans le SDP (`SHA-256`).
- `ice_support: true` — Asterisk collecte et négocie les candidats ICE.
- `rtcp_mux: true` — RTP et RTCP partagent un seul port, comme les navigateurs l'attendent.
- `use_avpf: true` — le profil RTP AVPF (feedback), requis par WebRTC.

`allow=opus` est recommandé — Opus est le codec que les navigateurs préfèrent. Asterisk 22 intègre le *passthrough* Opus dans le cœur (le module `res_format_attr_opus`), ce qui suffit pour relayer Opus entre deux jambes capables d'Opus sans ré-encodage. Le *transcodage* d'Opus vers un autre codec nécessite le module séparé `codec_opus`, que le guide WebRTC officiel liste comme optionnel mais fortement recommandé et que vous installez en plus de la version de base ; voir la discussion sur les codecs dans *Designing a VoIP network*. Gardez `ulaw` comme solution de repli pour le pontage vers des jambes non-WebRTC qui ne peuvent pas parler Opus.

## Étape 4 — ICE, STUN et TURN

Sur un réseau local plat, ICE avec des candidats hôtes suffit et rien d'autre n'est nécessaire. Sur Internet, vous ajoutez généralement un serveur STUN pour qu'Asterisk et le navigateur puissent découvrir leurs adresses publiques, et un serveur TURN pour les cas où le média direct est impossible (NAT symétrique, pare-feu restrictifs). Pointez Asterisk vers eux dans `rtp.conf` :

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

Le navigateur est configuré avec ses propres serveurs ICE en JavaScript (la liste `RTCPeerConnection` `iceServers`). Pour un déploiement purement interne, vous pouvez ignorer STUN/TURN entièrement.

`turnaddr` prend un port optionnel (par défaut `3478`) ; `turnusername` et `turnpassword` s'authentifient auprès du relais. STUN aide seulement un pair à *découvrir* son adresse publique — lorsque les deux extrémités sont derrière un NAT symétrique ou un pare-feu restrictif, le média direct est impossible et un relais TURN est la seule chose qui permet à l'audio de passer.

**Recommandation de production :** un serveur STUN public (tel que celui de Google) est très bien pour la découverte d'adresse, mais ne comptez **pas** sur un TURN public pour le trafic réel — TURN relaie tout votre média, vous voulez donc qu'il soit sous votre contrôle. Exécutez votre propre serveur [coturn](https://github.com/coturn/coturn). Un `/etc/turnserver.conf` minimal avec des identifiants à long terme ressemble à :

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Puis pointez Asterisk vers celui-ci dans `rtp.conf` :

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Donnez au navigateur le même serveur TURN dans sa liste `iceServers` pour que les deux jambes puissent relayer. Pour la production avec des utilisateurs sur des réseaux mobiles ou derrière des pare-feu d'entreprise, un coturn auto-hébergé est pratiquement obligatoire.

## Étape 5 — le client navigateur

N'importe quelle bibliothèque SIP WebRTC fonctionne ; deux très utilisées sont **SIP.js** et **JsSIP**. Le labo inclut un softphone SIP.js minimal à `lab/webrtc/index.html`. La partie essentielle est l'URL de transport et les identifiants :

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

Deux réalités du navigateur à retenir :

- **Contexte sécurisé.** `getUserMedia` (accès au microphone) ne fonctionne que sur les pages `https://` ou `http://localhost`. Servez la page via HTTPS en production.
- **Acceptez le certificat une fois.** Avec un certificat de labo auto-signé, visitez `https://your-asterisk:8089/ws` dans le même navigateur d'abord et acceptez l'avertissement, sinon le WebSocket échouera silencieusement.

Le softphone web SipPulse est un client de référence de qualité production construit sur ces mêmes primitives.

## Vérification d'un appel WebRTC

Avec le navigateur enregistré, `pjsip show contacts` montre le contact dynamique, et un appel allume le canal :

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

Si l'audio est unidirectionnel ou absent, c'est presque toujours ICE ou le certificat — voir le dépannage ci-dessous.

## Asterisk WebRTC vs une passerelle média

Asterisk peut terminer le WebRTC directement, mais ce n'est pas toujours le bon outil :

- **Utilisez le WebRTC natif d'Asterisk** lorsque le navigateur est un *téléphone* sur votre PBX — un agent, une extension interne, un click-to-call qui atterrit dans votre dialplan. Le navigateur est juste un autre endpoint et tout (files d'attente, voicemail, IVR) fonctionne.
- **Utilisez une passerelle dédiée (ex: Janus)** lorsque vous devez mettre à l'échelle de nombreuses sessions de navigateur indépendamment du contrôle d'appel, effectuer un transfert sélectif pour de grandes conférences/streaming, ou garder le plan média séparé du PBX. Une passerelle fait le pont entre WebRTC et SIP classique, et Asterisk voit alors une jambe SIP ordinaire.

De nombreux systèmes réels combinent les deux : Asterisk pour le contrôle d'appel, une passerelle pour la mise à l'échelle média côté navigateur. (C'est l'architecture derrière la pile de SipPulse.)

## Dépannage

- **Le WebSocket ne se connecte pas :** le navigateur a rejeté le certificat TLS. Ouvrez `https://host:8089/ws` directement et acceptez-le, ou installez un certificat de confiance.
- **Enregistré mais pas d'audio :** ICE a échoué — ajoutez STUN, et TURN si vous traversez un NAT. Vérifiez `pjsip set logger on` et regardez les candidats SDP.
- **Audio unidirectionnel :** généralement NAT/ICE d'un côté, ou un codec sans correspondance commune — assurez-vous de `allow=opus,ulaw`.
- **L'appel coupe au décrochage :** la poignée de main DTLS a échoué ; confirmez que `dtls_auto_generate_cert` est `Yes` et que l'horloge système est correcte (les certificats sont sensibles au temps).

## Labo

1. Exécutez `./lab.sh up`, puis `bash lab/make-certs.sh` et redémarrez Asterisk.
2. Servez `lab/webrtc/index.html` (`python3 -m http.server` depuis `lab/webrtc`) et ouvrez-le ; acceptez le certificat à `https://localhost:8089/ws`.
3. Enregistrez-vous en tant que `webrtc-1000` et appelez `600` (test d'écho) — vous devriez vous entendre.
4. Depuis le softphone SipPulse enregistré en tant que `6001`, composez `1000` pour faire sonner le navigateur.
5. Inspectez la négociation : `pjsip set logger on`, passez un appel, et trouvez l'empreinte DTLS et les candidats ICE dans le SDP.

## Résumé

WebRTC transforme un navigateur en un endpoint Asterisk de première classe. La recette est courte mais stricte : activez le serveur HTTP avec TLS pour que le navigateur puisse ouvrir un WebSocket sécurisé, ajoutez un transport PJSIP `wss`, et réglez `webrtc=yes` sur l'endpoint — ce qui active DTLS-SRTP (avec un certificat auto-généré), ICE, le multiplexage RTP/RTCP et le profil AVPF. Ajoutez STUN/TURN lors de la traversée de NAT, servez votre page via HTTPS, et pointez un client SIP.js (ou JsSIP) vers `wss://asterisk:8089/ws`. Pour des téléphones par navigateur sur votre PBX, le WebRTC natif d'Asterisk est le chemin le plus simple ; pour des médias à grande échelle, couplez-le avec une passerelle.

## Quiz

1. Quel transport un client navigateur WebRTC utilise-t-il pour transporter la signalisation SIP vers Asterisk ?
   - A. UDP brut sur le port 5060
   - B. Un WebSocket sécurisé (`wss://`) vers le serveur HTTP d'Asterisk
   - C. TLS sur le port 5061
   - D. Un socket TCP brut sur le port 8088

2. Le média WebRTC entre le navigateur et Asterisk est chiffré en utilisant quel mécanisme ?
   - A. SDES-SRTP (clés échangées dans le SDP)
   - B. DTLS-SRTP (clés dérivées d'une poignée de main DTLS)
   - C. IPsec
   - D. RTP brut — WebRTC ne chiffre pas le média

3. Vrai ou faux : lorsque vous réglez `webrtc=yes`, vous devez générer et installer manuellement le certificat DTLS utilisé pour chiffrer le média.

4. Sur quel port le serveur HTTP Asterisk du labo expose-t-il le WebSocket **sécurisé** pour WebRTC ?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Laquelle des options suivantes `webrtc=yes` active-t-il par défaut ? (Choisissez toutes les réponses qui s'appliquent.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Complétez le blanc : WebRTC négocie la connectivité en faisant en sorte que les deux côtés collectent et sondent des adresses candidates (hôte, STUN-réflexif, TURN-relais) en utilisant le framework ________.

7. Dans `rtp.conf`, quels deux paramètres pointent Asterisk vers un serveur externe afin qu'il puisse découvrir son adresse publique et relayer le média lorsque les chemins directs échouent ? (Choisissez toutes les réponses qui s'appliquent.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. Le chemin d'URL que le `res_http_websocket` d'Asterisk expose pour la signalisation WebRTC est ________.

9. Selon le chapitre, quand devriez-vous opter pour une passerelle média dédiée (telle que Janus) au lieu du WebRTC natif d'Asterisk ?
   - A. Chaque fois qu'un navigateur doit passer un appel
   - B. Lorsque vous devez mettre à l'échelle de nombreuses sessions média de navigateur indépendamment du contrôle d'appel, effectuer un transfert sélectif pour de grandes conférences, ou garder le plan média séparé du PBX
   - C. Uniquement lorsque le navigateur ne supporte pas DTLS
   - D. Lorsque vous voulez que la voicemail et l'IVR fonctionnent pour l'endpoint navigateur

10. Vrai ou faux : `getUserMedia` (accès au microphone) fonctionne sur n'importe quelle page `http://`, donc servir le softphone navigateur via HTTPS est optionnel.

**Réponses :** 1 — B · 2 — B · 3 — Faux (Asterisk auto-génère le certificat DTLS ; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — Faux (contexte sécurisé requis : `getUserMedia` ne fonctionne que sur `https://` ou `http://localhost`)
