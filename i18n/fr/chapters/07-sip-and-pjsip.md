# SIP & PJSIP in depth

SIP est le protocole ; PJSIP est la manière dont Asterisk 22 l'utilise. **PJSIP** (`chan_pjsip`, configuré via `pjsip.conf`) est le seul pilote de canal SIP dans Asterisk 22 LTS. Ce chapitre couvre les fondamentaux du protocole SIP (qui sont au niveau du protocole et restent valides à 100 %) ainsi que le modèle d'objet et la configuration PJSIP que vous utilisez au quotidien. Le pilote hérité retiré et un guide de migration sont traités dans le chapitre *Legacy channels*.

## Fondamentaux du protocole SIP

Le Session Initiation Protocol (SIP) est un protocole textuel similaire à HTTP et SMTP, conçu pour initialiser, maintenir et terminer des sessions de communication interactive entre des utilisateurs. Ces sessions peuvent inclure la voix, la vidéo, le chat, des jeux interactifs, et plus encore. SIP a été défini par l'IETF et est devenu le standard de facto pour les communications vocales. Il est très important de comprendre comment fonctionne SIP. Sur Asterisk 22, la configuration SIP réside dans `pjsip.conf`, qui est l'un des fichiers les plus fréquemment modifiés sur un système basé sur SIP (juste après `extensions.conf`).

### Théorie de fonctionnement

SIP est un protocole de signalisation composé des éléments suivants : User Agent Client, User Agent Servers, SIP Proxies et SIP Gateways. La figure suivante illustre les relations entre ces composants.

- UAC (user agent client) – Le client ou terminal qui initialise la signalisation SIP.
- UAS (user agent server) – Le serveur qui répond à une signalisation SIP provenant d'un UAC.
- UA (user agent) – Le terminal SIP (téléphones ou passerelles contenant à la fois un UAC et un UAS).
- Proxy Server – Reçoit les requêtes d'un UA et les transfère à d'autres SIP Proxies si la station concernée n'est pas sous leur administration.
- Redirect Server – Reçoit les requêtes et les renvoie à l'UA, incluant les données de destination, au lieu de les transférer directement à la destination.
- Location Server – Reçoit les requêtes d'un UA et met à jour la base de données de localisation avec ces informations.

Habituellement, les serveurs proxy, de redirection et de localisation sont hébergés sur le même matériel et utilisent le même logiciel, que nous appelons le SIP proxy. Le SIP proxy est responsable de la maintenance de la base de données de localisation, de l'établissement de la connexion et de la terminaison de session.

![Les principaux composants SIP : user agents (UAC/UAS/UA), le serveur registrar/proxy/redirect, et une passerelle vers le PSTN, avec le flux média RTP circulant directement entre les endpoints](../images/07-sip-and-pjsip-fig01.png)

#### Processus d'enregistrement SIP

Avant qu'un téléphone puisse recevoir des appels, il doit être enregistré dans une base de données de localisation. Dans cette base de données, l'adresse IP sera liée au nom. Dans l'exemple suivant, l'extension 8500 sera liée à l'adresse IP 200.180.1.1. Vous n'avez pas nécessairement besoin d'utiliser des numéros de téléphone. Dans l'architecture SIP, l'extension enregistrée pourrait tout aussi bien être flavio@voip.school.

![Enregistrement SIP : le téléphone envoie un REGISTER liant l'extension 8500 à son adresse IP, le registrar stocke le contact dans la base de données de localisation et répond avec un 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Fonctionnement du proxy

Lorsqu'il fonctionne comme un SIP proxy, le serveur SIP reste au milieu de la signalisation et est capable de routage avancé et de facturation. Le flux média, basé sur le real time protocol (RTP), circule toujours directement entre les endpoints.

![Fonctionnement du proxy : le SIP proxy reste dans le chemin de signalisation (INVITE/200 OK) et recherche l'appelé dans le serveur de localisation, tandis que le flux média RTP circule directement entre les deux endpoints](../images/07-sip-and-pjsip-fig03.png)

#### Fonctionnement de la redirection

Lors d'une redirection, le serveur SIP envoie simplement un message (par exemple, 302 moved temporarily) à l'user agent et reste en dehors du chemin des nouveaux messages. C'est très léger en termes d'utilisation des ressources, mais vous n'avez aucun contrôle. La redirection est parfois utilisée dans les conceptions d'équilibrage de charge.

![Fonctionnement de la redirection : le serveur de redirection répond à l'INVITE avec un 302 Moved Temporarily contenant le contact, puis s'écarte pendant que l'appelant renvoie l'INVITE/ACK directement vers la nouvelle destination](../images/07-sip-and-pjsip-fig04.png)

#### Comment Asterisk gère SIP

Il est important de comprendre qu'Asterisk n'est ni un SIP proxy ni un SIP redirector. Asterisk peut jouer le rôle de registrar et de serveur de localisation ; cependant, il ne connecte que deux UAC à lui-même. Par conséquent, Asterisk est considéré comme un back-to-back user agent (B2BUA). En d'autres termes, il connecte deux canaux SIP, en les pontant ensemble. Asterisk possède un mécanisme de re-invite qui peut permettre aux canaux SIP de communiquer directement entre eux au lieu de passer par Asterisk. Sur un endpoint PJSIP, cela est contrôlé par le paramètre `direct_media`. Lors de l'utilisation de `direct_media=yes`, le flux RTP circule directement d'un endpoint à un autre, libérant ainsi des ressources serveur.

#### Fonctionnement SIP avec direct_media=yes

![Fonctionnement SIP avec directmedia=yes : la signalisation SIP transite par Asterisk tandis que l'audio RTP circule directement entre les deux téléphones, libérant des ressources serveur](../images/07-sip-and-pjsip-fig05.png)

Cependant, si vous devez transférer ou enregistrer l'appel en utilisant Asterisk, vous pouvez utiliser le paramètre `direct_media=no` pour forcer le flux RTP à passer par le serveur Asterisk.

#### Fonctionnement SIP avec direct_media=no

![Fonctionnement SIP avec directmedia=no : la signalisation SIP et l'audio RTP sont ancrés via Asterisk, lui permettant d'enregistrer, de transcoder ou de transférer l'appel](../images/07-sip-and-pjsip-fig06.png)

#### Messages SIP

Les messages SIP de base sont :

- INVITE – établissement de connexion
- ACK – accusé de réception
- BYE – terminaison de connexion
- CANCEL – terminaison de connexion pour un appel non établi
- REGISTER – enregistrer un UAC auprès d'un SIP proxy
- OPTIONS – peut être utilisé pour vérifier la disponibilité
- REFER – transférer un appel SIP à quelqu'un d'autre
- SUBSCRIBE – s'abonner à des événements de notification
- NOTIFY – envoyer des informations sur le canal
- INFO – envoyer divers messages (par exemple, DTMF)
- MESSAGE – envoyer des messages instantanés

Les réponses SIP sont au format texte et sont facilement lisibles (similaires aux messages HTTP). Les réponses les plus importantes sont :

- 1XX – Messages d'information (100–trying, 180–ringing, 183–progress)
- 2XX – Succès de la requête (200 – OK)
- 3XX – Redirection d'appel, la requête doit être dirigée vers un autre endroit (302 – moved temporarily, 305 – use proxy)
- 4XX – Erreur (403 – Forbidden)
- 5XX – Erreur serveur (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Échec global (606 – Not acceptable)

Par exemple :

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Session description protocol (SDP)

Le SDP a été défini à l'origine dans la RFC 2327 de l'IETF, désormais obsolète et remplacée par la RFC 4566. Il est destiné à décrire des sessions multimédias à des fins d'annonce de session, d'invitation de session et d'autres formes d'initialisation de session multimédia. Le SDP inclut :

- Protocole de transport (RTP/UDP/IP)
- Type de média (texte, audio, vidéo)
- Format média ou codec (vidéo H.261, audio g.711, etc.)
- Informations nécessaires pour recevoir ces médias (adresses, ports, etc.)

L'exemple suivant est une transcription d'un SDP décrivant un appel entre deux téléphones.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### Traversée NAT SIP

Le Network Address Translation (NAT) est une fonctionnalité utilisée par la plupart des réseaux pour économiser les adresses IP Internet. Habituellement, une entreprise reçoit un petit bloc d'adresses IP, et les utilisateurs finaux reçoivent une adresse IP dynamiquement lorsqu'ils sont connectés à Internet. Le NAT résout le problème d'adressage en mappant les adresses internes vers des adresses externes. Il stocke un mappage des adresses internes vers externes dans sa mémoire. Ce mappage est valide pour une durée spécifique, après quoi il est supprimé. Le mappage utilise des paires IP:port pour les adresses internes et externes. Il existe quatre types de NAT :

- Full Cone
- Restricted Cone
- Port Restricted Cone
- Symmetric

La théorie NAT ci-dessous — les quatre types de NAT, le problème de l'en-tête Contact, les keep-alives et le forçage du média via le serveur — est au niveau du protocole et s'applique à toute implémentation SIP. La manière dont vous configurez chaque comportement sur Asterisk 22 (PJSIP) est traitée plus loin dans ce chapitre sous *Nat traversal on res_pjsip*.

#### Full Cone

Le premier NAT, le full cone, représente un mappage statique d'une paire IP:port externe vers une paire IP:port interne. N'importe quel ordinateur externe peut s'y connecter en utilisant la paire IP:port externe. C'est le cas des pare-feu non persistants implémentés avec l'utilisation de filtres.

![Full Cone NAT : l'hôte interne (10.0.0.1:8000) est mappé statiquement vers la paire externe 200.180.4.168:1234, donc n'importe quel ordinateur externe peut envoyer des paquets à cette paire et atteindre l'hôte interne](../images/07-sip-and-pjsip-fig11.png)

#### Restricted Cone

Dans le scénario du restricted cone, la paire IP:port externe n'est ouverte que lorsque l'ordinateur interne envoie des données vers une adresse extérieure. Cependant, le NAT restricted cone bloque tous les paquets entrants provenant d'une adresse différente. En d'autres termes, l'ordinateur interne doit envoyer des données à un ordinateur externe avant de pouvoir recevoir des données en retour.

#### Port Restricted Cone

Le pare-feu port restricted cone est presque identique au restricted cone. La seule différence est que, maintenant, le paquet entrant doit provenir exactement de la même IP et du même port que le paquet envoyé.

#### Symmetric

Le dernier type de NAT est appelé symétrique. Il diffère des trois premiers en ce qu'un mappage spécifique est effectué pour chaque adresse externe. Seules des adresses externes spécifiques sont autorisées à revenir par le mappage NAT. Il n'est pas possible de prédire la paire IP:port externe qui sera utilisée par le périphérique NAT. Les trois autres types de NAT permettent l'utilisation d'un serveur externe pour découvrir l'adresse IP externe pour la communication. Avec le NAT symétrique, même si vous pouvez vous connecter à un serveur externe, l'adresse découverte ne peut être utilisée pour aucun autre périphérique que ce serveur.

![Symmetric NAT : un port source externe différent est alloué pour chaque destination, donc le mappage découvert vers un serveur ne peut pas être réutilisé par un autre hôte, ce qui rompt la traversée basée sur STUN](../images/07-sip-and-pjsip-fig12.png)

#### Tableau des pare-feu NAT

Le tableau suivant résume les quatre types de NAT.

| Type de NAT | Doit envoyer des données en premier | Peut déterminer l'IP:port externe pour les paquets de retour | Restreint les paquets entrants à l'IP:port de destination |
| --- | --- | --- | --- |
| Full Cone | Non | Oui | Non |
| Restricted Cone | Oui | Oui | IP seulement |
| Port Restricted Cone | Oui | Oui | Oui |
| Symmetric | Oui | Non | Oui |

#### Signalisation SIP et RTP sur NAT

Certains des plus gros problèmes de traversée NAT sont que vous devez résoudre deux problèmes : la signalisation SIP et l'audio (RTP). La plupart des problèmes d'audio unidirectionnel sont liés au NAT. Une chose intéressante à propos de SIP est que, lorsqu'un UAC envoie un paquet, il intègre l'adresse IP dans le champ d'en-tête SIP « Contact ». Habituellement, il s'agit d'une adresse interne (RFC1918) ; les réponses à ce paquet ne peuvent pas être routées sur Internet vers l'UAC. Les correctifs conceptuels sont toujours les mêmes :

- **Ignorer l'adresse Contact/Via et répondre là d'où le paquet provient réellement.** C'est le comportement défini dans la RFC 3581 (`rport`). Sur PJSIP, c'est `force_rport=yes`, et `rewrite_contact=yes` réécrit le contact stocké vers l'adresse source.
- **Renvoyer le média vers l'adresse d'où le RTP est réellement arrivé** (RTP symétrique, historiquement appelé *comedia*). Sur PJSIP, c'est `rtp_symmetric=yes`.
- **Maintenir le mappage NAT ouvert.** Si le mappage expire, Asterisk ne peut plus envoyer d'INVITE à l'UAC — le téléphone peut passer des appels mais pas en recevoir. L'envoi périodique d'OPTIONS (un *qualify*) maintient le trou ouvert. Sur PJSIP, c'est `qualify_frequency=` sur l'AOR.

Si le NAT de l'utilisateur est de type symétrique, il n'est pas possible d'envoyer des paquets d'un UAC à un autre directement ; dans ce cas, vous devez forcer le RTP via Asterisk avec `direct_media=no`. Ces configurations sont appropriées pour la plupart des cas. Il est possible d'optimiser le trafic en utilisant des techniques avancées comme le Simple Traversal of UDP over NAT (STUN), qui est utile avec le full cone, le restricted cone et le port restricted cone, ainsi que l'Application Layer Gateway (ALG). Malheureusement, la plupart des pare-feu aujourd'hui — même les routeurs DSL/câble domestiques — sont symétriques, rendant STUN inutilisable. L'ALG pourrait résoudre le problème, mais il n'est pas pris en charge, pas implémenté ou bogué dans la plupart des cas.

#### Asterisk derrière NAT

Parfois, le serveur Asterisk lui-même est implémenté derrière un pare-feu avec NAT — une situation très courante lors d'un déploiement dans le cloud. Dans ce cas, il est nécessaire d'effectuer une configuration supplémentaire afin qu'Asterisk annonce son adresse **publique** dans les en-têtes SIP et SDP au lieu de son adresse privée.

Conceptuellement, il y a trois étapes :

- Transférer le port de signalisation SIP (UDP 5060 par défaut) du pare-feu vers le serveur Asterisk.
- Transférer la plage de ports média RTP (UDP 10000–20000 par défaut, définie dans `rtp.conf`) du pare-feu vers le serveur Asterisk.
- Indiquer à Asterisk son adresse externe et quel réseau est local, afin qu'il sache quand substituer l'adresse publique dans les en-têtes.

Sur PJSIP, ces deux derniers éléments correspondent à `external_media_address` / `external_signaling_address` et `local_net=` sur le **transport**, et la plage de ports RTP est toujours configurée dans `rtp.conf` :

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

La configuration PJSIP complète et fonctionnelle pour un serveur Asterisk derrière NAT est donnée plus loin dans ce chapitre sous *Asterisk Server behind NAT*.

### Limitations SIP

Asterisk utilise le flux RTP entrant pour synchroniser le flux sortant. Si le flux entrant est interrompu (suppression de silence), la musique d'attente sera coupée. En d'autres termes, vous ne devriez pas utiliser la suppression de silence dans les téléphones ou chez les fournisseurs avec Asterisk.

## PJSIP : le canal SIP

PJSIP est le canal SIP dans Asterisk. Il a été introduit pour la première fois dans Asterisk 12 et, après des années de développement, est devenu le canal SIP par défaut et recommandé. Dans Asterisk 22 (la version LTS actuelle), c'est le seul pilote de canal SIP. PJSIP est basé sur le projet de Teluu appelé pjproject. La pile pjproject est utilisée par de nombreux softphones et implémentations SIP commerciales. C'est une pile SIP polyvalente et mature.

### Pourquoi utiliser PJSIP

PJSIP a été une refonte complète de la manière dont Asterisk utilise SIP, et il vaut la peine de comprendre les fonctionnalités qui en ont fait le standard.

#### Fonctionnalités

Le canal prend en charge de nombreuses fonctionnalités, dont certaines méritent d'être mentionnées ici :

- Enregistrements multiples : Vous pouvez utiliser plus d'un téléphone connecté à la même Address of Record. En d'autres termes, vous pouvez connecter deux téléphones au même endpoint.
- Interface de programmation d'application (API) conviviale : L'API est modulaire et facile à étendre, construite à partir de nombreux petits modules coopérants plutôt qu'un seul gros bloc de code.
- Transports multiples : Vous pouvez écouter sur plusieurs adresses, ports et transports lors de l'utilisation de PJSIP. Vous n'êtes pas limité à une seule adresse de liaison pour tous vos appareils. PJSIP est très flexible.

#### Une note sur la configuration

La configuration PJSIP est plus verbeuse : elle nécessite un peu plus d'efforts et plus de lignes de configuration, car chaque appareil est décrit par plusieurs objets liés au lieu d'un seul bloc peer. Cette structure supplémentaire est ce qui donne à PJSIP sa flexibilité, et l'assistant de configuration (traité plus loin) permet de garder le provisionnement quotidien court.

### Modules PJSIP

Le canal PJSIP est implémenté par de nombreux modules décrits ci-dessous :

#### res_pjsip

C'est la couche de base de PJSIP et le module principal. Il est responsable de certains des services principaux.

#### res_pjsip_session

Ce module est responsable des sessions média, du traitement du protocole de description de session et de certains addons.

#### res_pjsip_messaging

Traite les messages SIP et analyse les en-têtes SIP.

#### res_pjsip_registrar

Responsable de la gestion des enregistrements SIP.

#### res_pjsip_pubsub

Responsable du traitement des subscribe, notify et publish. Ces messages sont responsables de la gestion de la présence SIP et du BLF (Busy Lamp Field).

### Configuration PJSIP

PJSIP possède de nombreuses sections différentes. Le format de la section est :

```
[Section Name]
Option = Value
Option = Value
```

#### Section End point

L'objet de configuration le plus important est l'endpoint. La configuration de l'endpoint possède des fonctionnalités de base et doit être associée à une section AOR et Transport. Exemple :

```
[xlite]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=xlite
auth=xlite
```

Si vous regardez l'exemple ci-dessus, l'endpoint est une sorte de colle reliant toutes les sections ensemble. Il spécifie un transport, l'address of record et l'authentification pour un téléphone. Il définit également la partie la plus importante, le point d'entrée du contexte dans le dialplan.

#### Address of Record (AOR)

Cet objet indique à Asterisk où contacter l'endpoint. Il stocke les adresses de contact. Il permet également la configuration des boîtes vocales. Exemple :

```
[xlite]
type=aor
max_contacts=2
```

#### Authentication

Cette section est responsable de l'authentification entrante et sortante. La documentation se trouve dans le fichier d'exemple pjsip.conf. Exemple :

```
[xlite]
type=auth
auth_type=userpass
username=xlite
password=#supersecret#
```

#### Transport

La section transport vous permet de définir des adresses IPV4 et IPV6 et le protocole de transport, TCP, UDP, TLS, Websockets, etc. Vous pouvez également configurer des adresses NAT dans cette section. Vous pouvez créer plusieurs transports, mais ils ne peuvent pas partager la même IP et le même port, et vous ne pouvez pas lier plusieurs transports TCP ou TLS de la même version IP. Exemple :

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Registration

Cet objet est utilisé pour configurer un enregistrement sortant. Exemple :

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identify

Cet objet contrôle quelle requête SIP appartient à quel endpoint. Si vous n'avez pas de section identify, le système fera correspondre le contenu de l'en-tête « From » avec le nom de l'endpoint. En utilisant cette section, vous pouvez assigner des adresses IP spécifiques à des endpoints spécifiques, identifiés par nom d'utilisateur ou IP. Exemple :

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

L'objet ACL vous permet de configurer des réseaux spécifiques avec un accès à l'endpoint. Désormais, les ACL sont définies dans une section spécifique ou dans acl.conf. Exemple :

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relation entre les entités

La relation entre les objets de configuration offre une grande flexibilité pour la configuration. Cependant, cela semble un peu complexe pour quiconque débute.

![Relations entre les objets de configuration PJSIP : l'endpoint se lie au transport, à l'auth et à l'AOR (qui contient les contacts) ; l'enregistrement se lie au transport et à l'auth ; l'identify pointe vers l'endpoint, tandis que l'ACL et le domain alias sont autonomes](../images/07-sip-and-pjsip-fig14.png)

Le graphique ci-dessus signifie :

#### Relations :

- ENDPOINT/AOR plusieurs à plusieurs
- ENDPOINT/AUTH zéro à plusieurs vers zéro à un
- ENDPOINT/IDENTIFY zéro à plusieurs vers un
- ENDPOINT/AUTH zéro à plusieurs vers un
- ENDPOINT/TRANSPORT zéro à plusieurs vers au moins un
- REGISTRATION/AUTH zéro à plusieurs vers zéro à un
- REGISTRATION/TRANSPORT zéro à plusieurs vers au moins un
- AOR/CONTACT plusieurs à plusieurs, ACL, DOMAIN_ALIAS n'ont pas de configurations de relation

### Configuration d'un Softphone

Pour configurer un softphone, vous devez définir de nombreuses sections différentes. Voici un exemple sur la façon de configurer un softphone.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[xlite]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=xlite
auth=xlite
[xlite]
type=auth
auth_type=userpass
username=xlite
password=#supersecret#
[xlite]
type=aor
max_contacts=2
```

La configuration ci-dessus définit un transport pour UDP sur le port 5060, puis définit un endpoint, son authentification par nom d'utilisateur et mot de passe, puis l'Address of Record avec un maximum de deux contacts.

### Configuration d'un trunk SIP

Pour configurer un trunk SIP, vous devez avoir l'adresse IP ou l'hôte du trunk SIP, le nom et le mot de passe. Vous devez créer une nouvelle section d'enregistrement à cet effet.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=userpass
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Traversée NAT sur res_pjsip

Le Network Address Translation a été créé il y a longtemps pour faire face à la pénurie d'adresses IP version 4. Beaucoup de gens utilisent également le NAT comme fonctionnalité de sécurité masquant les adresses internes d'un réseau par rapport à l'Internet public. Parfois, vous devrez gérer la traversée NAT. Dans certains cas, le serveur peut être derrière un NAT, comme lorsque vous déployez le serveur dans le cloud. Souvent, si vous déployez dans le cloud, vos utilisateurs seront également derrière un routeur NAT. Pour organiser les choses, nous allons diviser cela en deux parties. La première est le serveur Asterisk derrière NAT, comme dans un déploiement cloud. Dans la deuxième section, nous couvrirons comment prendre en charge les clients derrière NAT en utilisant res_pjsip.

#### Serveur Asterisk derrière NAT

Lorsque le serveur Asterisk est derrière un NAT, vous devez informer les adresses locales externes et internes dans la section transport. Nous aurons les directives suivantes.

##### direct_media

Le média circule-t-il directement de pair à pair ou via le serveur ? Pour le NAT, il devrait circuler via le serveur. Pour le NAT, sélectionnez no. Exemple :

```
direct_media=no
```

##### external_media_address

Adresse média pour gérer le RTP externe. Habituellement la même que l'external_signaling_address. Utilisez l'adresse IP publique de votre serveur pour le média et la signalisation. Exemple :

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Adresse SIP externe où recevoir les messages. Exemple :

```
external_signaling_address=54.232.1.20
```

##### local_net

Le réseau que vous considérez comme votre réseau local. Exemple :

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Exemple complet de transport pour un serveur Asterisk derrière NAT

Pour utiliser un serveur Asterisk derrière NAT, vous devez effectuer deux étapes. Premièrement, définir un transport derrière NAT. Deuxièmement, associer ce transport à l'endpoint.

##### Création du transport derrière NAT

Pour créer le transport derrière NAT dans le fichier pjsip.conf, créez une section comme ci-dessous.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

Associez le transport à un endpoint

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Pour les trunks SIP, vous devez également associer le transport à la section d'enregistrement comme ci-dessous.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Utilisation d'Asterisk avec des clients derrière NAT

Pour utiliser des téléphones derrière NAT, vous devez configurer des paramètres supplémentaires par endpoint.

##### direct_media

Le média circule-t-il directement de pair à pair ou via le serveur ? Pour le NAT, il devrait circuler via le serveur. Exemple :

```
direct_media=no
```

##### rtp_symmetric

C'est ce que nous appelons comedia. Au lieu de se fier à l'adresse définie dans cet en-tête SDP comme d'habitude dans SIP, utilisez l'adresse d'où vous recevez le premier paquet RTP et renvoyez depuis la même adresse. Exemple :

```
rtp_symmetric=yes
```

##### force_rport

C'est le comportement défini dans la RFC 3581. Plutôt que d'utiliser l'adresse dans l'en-tête VIA, renvoyez les réponses d'où proviennent les requêtes. Exemple :

```
force_rport=yes
```

##### qualify_frequency

Ce paramètre doit être appliqué à l'AOR (pas à l'endpoint). Il y a aussi la dernière étape, configurer l'option qualify. Vous devriez toujours avoir des paquets pingant la destination pour maintenir le mappage NAT ouvert. Ceci est défini dans la section AOR. Exemple :

- qualify_frequency=15

Exemple complet d'un endpoint où le serveur et le client sont derrière NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Nommage des canaux

Comme d'habitude, l'un des aspects importants d'un canal est son nommage et PJSIP a quelques détails intéressants. Vous composez un endpoint PJSIP avec la technologie `PJSIP/` :

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Une fonctionnalité utile est la possibilité de composer tous les contacts enregistrés sur un AOR à la fois. La fonction PJSIP_DIAL_CONTACTS sera traduite en la liste des contacts à composer.

```
exten=>6000,dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

Composer un trunk est légèrement différent. Supposons que le trunk ne sera pas enregistré sur votre plateforme ou n'a pas d'adresse IP associée à votre adresse AOR. Vous pouvez spécifier l'adresse du trunk directement dans la ligne. En utilisant un appel international comme exemple.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Si vous préférez spécifier l'adresse du trunk dans la section AOR, vous pouvez également utiliser.

```
exten=>9011.,Dial(PJSIP/${EXTEN:1}@siptrunk
```

### Assistant de configuration PJSIP

PJSIP est puissant mais verbeux à configurer : beaucoup de sections différentes et de modèles qui peuvent être déroutants au début. La bonne nouvelle est l'assistant de configuration PJSIP. En définissant chaque canal en quelques lignes, il vous permet de créer des modèles et de simplifier la configuration de nouveaux appareils. Utilisez le fichier pjsip_wizard.conf pour configurer. Vous devez toujours définir les sections transport et global dans le fichier pjsip.conf. Personnellement, je préfère utiliser l'assistant juste pour les téléphones, pour les trunks SIP, le nombre n'est généralement pas grand et vous pouvez configurer directement dans pjsip. Le plus grand avantage de l'assistant est la possibilité d'utiliser des modèles et de créer des téléphones rapidement.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[xlite](phone_default)
inbound_auth/username = xlite
inbound_auth/password = supersecret
[zoiper](phone_default)
inbound_auth/username = zoiper
inbound_auth/password = supersecret
```

### Chargement et déchargement de PJSIP

PJSIP est le seul canal SIP dans Asterisk 22, et ses modules sont chargés par défaut. Dans de rares cas, vous voudrez peut-être toujours contrôler le chargement des modules depuis le fichier modules.conf — par exemple, pour désactiver PJSIP sur un serveur qui n'utilise que IAX2 ou DAHDI.

#### Pour désactiver PJSIP

Modifiez le fichier modules.conf et ajoutez les lignes suivantes.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
noload => res_pjsip_log_forwarder.so
```

### Commandes de console

Maintenant que vous avez configuré vos endpoints PJSIP, il est temps de voir comment vérifier votre configuration. Il existe de nombreuses commandes de console pour vous aider dans cette tâche. Après avoir modifié pjsip.conf, rechargez la configuration avec :

```
module reload res_pjsip.so
```

Un simple `reload` (ou `core reload`) recharge tous les modules, y compris PJSIP. (Notez qu'il n'y a pas de commande `pjsip reload` nue — `pjsip reload` n'existe que sous la forme `pjsip reload qualify aor|endpoint`.) Vous pouvez lister toutes les commandes de console PJSIP disponibles avec `help pjsip`.

#### pjsip show endpoints

Cette commande affiche les endpoints disponibles. Dans l'image ci-dessous, nous avons une capture d'écran. Vous pouvez voir l'adresse du softphone xlite et voir qu'il est disponible.

![Sortie de `pjsip show endpoints` listant les endpoints blink, siptrunk, xlite et zoiper avec leur AOR, auth, transport et disponibilité — le contact xlite est enregistré (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

Avec la commande ci-dessus, vous pouvez voir chaque paramètre de l'endpoint. La liste ci-dessous a été coupée à moins de la moitié des paramètres actuels.

![Sortie de `pjsip show endpoint xlite` montrant la liste complète des paramètres pour un seul endpoint, de 100rel et allow=(ulaw) jusqu'à callerid et connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

Cette commande liste les objets Address of Record configurés et leurs contacts, afin que vous puissiez confirmer où Asterisk enverra les appels pour chaque endpoint.

#### pjsip show registrations

La commande ci-dessous montre les enregistrements effectués par notre propre serveur.

![Sortie de `pjsip show registrations` : l'enregistrement sortant siptrunk/sip:1020@sip.api4com.com:5600 est affiché avec le statut Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

La commande list est un peu plus conviviale et affiche moins de données, mais mieux structurées. Liste des endpoints :

![Sortie de `pjsip list endpoints` : une liste compacte d'une ligne par endpoint (blink, siptrunk, xlite, zoiper) avec leur état et le nombre de canaux](../images/07-sip-and-pjsip-fig18.png)

Liste des contacts :

![Sortie de `pjsip list contacts` montrant les URI de contact siptrunk et xlite avec leur hash et leur statut de qualification](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

La commande de dépannage la plus utile est le logger de paquets SIP. Il imprime chaque requête et réponse SIP sur la console au fur et à mesure qu'elles sont envoyées ou reçues, ce qui est inestimable lors du diagnostic des problèmes d'enregistrement et d'établissement d'appel.

```
pjsip set logger on
pjsip set logger off
```

Vous pouvez également restreindre la journalisation à un seul hôte avec `pjsip set logger host <ip>`.

#### pjsip set history on

Un excellent ajout à PJSIP est le concept d'historique. Vous pouvez capturer et analyser les requêtes et réponses SIP en temps réel de manière simple. Pour démarrer l'historique, utilisez la commande ci-dessous.

![L'exécution de `pjsip set history on` renvoie "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Maintenant, vous pouvez afficher l'historique :

![Sortie de `pjsip show history` : un tableau numéroté de messages SIP capturés — REGISTER, 401 Unauthorized, REGISTER, 200 OK — avec horodatages, direction et adresse](../images/07-sip-and-pjsip-fig21.png)

Ensuite, pour voir une requête ou une réponse spécifique, affichez l'élément de l'historique :

![Sortie de `pjsip show history entry` : le texte complet d'un seul message SIP capturé — ici la réponse `404 Not Found` d'Asterisk 22 à une sonde OPTIONS — montrant les en-têtes Via (avec `rport`/`received`), Call-ID, From, To et CSeq, les capacités `Allow`/`Supported` et l'en-tête `Server: Asterisk PBX 22.10.0`](../images/07-sip-and-pjsip-fig22.png)

Très facile, n'est-ce pas ? Vous pouvez également effacer l'historique quand vous le souhaitez en utilisant `pjsip set history clear`.

> **Migration d'un système chan_sip/sip.conf existant ?** Le pilote hérité `chan_sip`
> et un **guide de migration complet sip.conf → pjsip.conf** (incluant le
> tableau de correspondance des concepts et le script de conversion `sip_to_pjsip.py`) sont couverts
> dans le chapitre *Legacy channels*.

## Quiz

1. Dans l'architecture SIP, quel composant reçoit une requête et y répond avec une réponse de redirection (telle que `302 Moved Temporarily`) contenant la nouvelle localisation, puis reste en dehors du chemin des messages de suivi ?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. Quel rôle joue Asterisk lorsqu'il gère un appel SIP entre deux téléphones ?
   - A. Un SIP proxy qui reste uniquement dans le chemin de signalisation
   - B. Un SIP redirect server
   - C. Un back-to-back user agent (B2BUA) qui ponte deux canaux SIP
   - D. Un équilibreur de charge SIP sans état

3. Quelle méthode SIP est utilisée par un téléphone pour indiquer au registrar son adresse IP actuelle afin qu'il puisse recevoir des appels ultérieurement ?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Vrai ou Faux : Dans Asterisk 22, `chan_sip` et `sip.conf` sont toujours disponibles en tant que secours hérité aux côtés de PJSIP.

5. Avec quels objets de configuration un endpoint doit-il être associé pour qu'Asterisk connaisse le socket d'écoute à utiliser et où envoyer les appels pour cet appareil ? (Choisissez toutes les réponses qui s'appliquent.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. Dans un objet PJSIP `aor`, quel paramètre maintient le mappage NAT ouvert en qualifiant périodiquement le contact, et quelle est son unité ?
   - A. `qualify=yes` (booléen)
   - B. `qualify_frequency` (secondes)
   - C. `rtp_timeout` (millisecondes)
   - D. `nat=force_rport`

7. Remplissez le blanc : Pour qu'Asterisk fasse correspondre une requête SIP entrante à un endpoint spécifique par adresse IP source (au lieu de l'en-tête `From`), vous créez une section avec `type=________`.

8. Quel objet PJSIP est utilisé pour configurer un enregistrement **sortant** d'Asterisk vers un fournisseur de trunk SIP ?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Sur la CLI d'Asterisk 22, quelle commande active le logger de paquets SIP qui imprime chaque requête et réponse SIP sur la console ?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Sur un endpoint PJSIP qui dessert un téléphone derrière un NAT symétrique, quelle paire de paramètres permet à Asterisk de répondre à l'adresse source de la requête (RFC 3581) et de renvoyer le média là d'où le RTP arrive réellement ?
    - A. `direct_media=yes` et `srvlookup=yes`
    - B. `force_rport=yes` et `rtp_symmetric=yes`
    - C. `allowguest=yes` et `insecure=invite`
    - D. `qualify=yes` et `nat=no`

**Réponses :** 1 — B · 2 — C · 3 — D · 4 — Faux · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
