# SIP & PJSIP en profondeur

SIP est le protocole ; PJSIP est la façon dont Asterisk 22 le parle. **PJSIP** (`chan_pjsip`, configuré via `pjsip.conf`) est le seul pilote de canal SIP dans Asterisk 22 LTS. Ce chapitre couvre les fondamentaux du protocole SIP (qui sont au niveau du protocole et restent 100 % valides) ainsi que le modèle d’objets PJSIP et la configuration que vous utilisez quotidiennement. Le pilote hérité retiré et un guide de migration sont traités dans le chapitre *Legacy channels*.

## Objectives

By the end of this chapter, you should be able to:

- Explain the role of the SIP user agents, proxies, registrar, and gateways;
- Follow a basic SIP call flow (REGISTER, INVITE, provisional and final responses, ACK, BYE) and read a SIP message;
- Describe how SDP negotiates the media session and how NAT affects SIP signaling and RTP;
- Map the PJSIP object model — `endpoint`, `auth`, `aor`, `transport`, `identify`, and `registration` — and how the objects reference one another;
- Configure SIP phones and trunks in `pjsip.conf`, including the NAT-traversal options; and
- Verify and troubleshoot endpoints with the `pjsip show …` CLI commands.

## Principes fondamentaux du protocole SIP

Le protocole Session Initiation Protocol (SIP) est un protocole texte similaire à HTTP et SMTP qui a été conçu pour initialiser, maintenir et terminer des sessions de communication interactive entre utilisateurs. Ces sessions peuvent inclure la voix, la vidéo, le chat, des jeux interactifs et d’autres services. Le SIP a été défini par l’IETF et est devenu le standard de facto pour les communications vocales. Il est très important de comprendre le fonctionnement du SIP. Sur Asterisk 22, la configuration SIP se trouve dans `pjsip.conf`, qui est l’un des fichiers les plus fréquemment modifiés sur un système basé sur SIP (juste après `extensions.conf`).

### Théorie de fonctionnement

SIP est un protocole de signalisation avec les composants suivants : User Agent Client, User Agent Servers, SIP Proxies, et SIP Gateways. La figure suivante représente les relations entre ces composants.

- UAC (user agent client) – Le client ou terminal qui initialise la signalisation SIP.  
- UAS (user agent server) – Le serveur qui répond à une signalisation SIP provenant d’un UAC.  
- UA (user agent) – Le terminal SIP (téléphones ou passerelles qui contiennent à la fois UAC et UAS).  
- Proxy Server – Reçoit les requêtes d’un UA et les transfère à d’autres Proxy SIP si la station particulière n’est pas sous leur administration.  
- Redirect Server – Reçoit les requêtes et les renvoie à l’UA, incluant les données de destination, au lieu de les transmettre directement à la destination.  
- Location Server – Reçoit les requêtes d’un UA et met à jour la base de données de localisation avec ces informations.

Habituellement, les serveurs proxy, redirect et location sont hébergés sur le même matériel et utilisent le même logiciel, que nous appelons le proxy SIP. Le proxy SIP est responsable de la maintenance de la base de données de localisation, de l’établissement de la connexion et de la terminaison de la session.

![Les principaux composants SIP : agents utilisateurs (UAC/UAS/UA), le serveur d’enregistrement/proxy/redirection, et une passerelle vers le PSTN, avec le média RTP circulant directement entre les points d’extrémité](../images/07-sip-and-pjsip-fig01.png)

#### Processus d'enregistrement SIP

Avant qu’un téléphone puisse recevoir des appels, il doit être enregistré dans une base de données de localisation. Dans la base de données de localisation, l’adresse IP sera liée au nom. Dans l’exemple suivant, l’extension 8500 sera liée à l’adresse IP 200.180.1.1. Vous n’avez pas nécessairement besoin d’utiliser des numéros de téléphone. Dans l’architecture SIP, l’extension enregistrée pourrait également être flavio@voip.school.

![Enregistrement SIP : le téléphone envoie un REGISTER liant l'extension 8500 à son adresse IP, le registre stocke le contact dans la base de données de localisation et répond avec 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Fonctionnement du proxy

Lorsqu'il fonctionne comme un proxy SIP, le serveur SIP reste au milieu de la signalisation et est capable d'un routage avancé et de la facturation. Le flux média, basé sur le protocole en temps réel (RTP), continue d'aller directement entre les points d'extrémité.

![Fonctionnement du proxy : le proxy SIP reste dans le chemin de signalisation (INVITE/200 OK) et recherche le destinataire dans le serveur de localisation, tandis que le média RTP circule directement entre les deux points d’extrémité](../images/07-sip-and-pjsip-fig03.png)

#### Opération de redirection

Lors de la redirection, le serveur SIP envoie simplement un message (par ex., 302 moved temporarily) à l’agent utilisateur et reste hors du chemin des nouveaux messages. C’est très léger en termes d’utilisation des ressources, mais vous n’avez aucun contrôle. La redirection est parfois utilisée dans les conceptions d’équilibrage de charge.

![Opération de redirection : le serveur de redirection répond à l'INVITE avec un 302 Moved Temporarily contenant le contact, puis se retire pendant que l'appelant renvoie l'INVITE/ACK directement vers la nouvelle destination](../images/07-sip-and-pjsip-fig04.png)

#### Comment Asterisk gère SIP

Il est important de comprendre qu'Asterisk n'est ni un proxy SIP ni un redirecteur SIP. Asterisk peut jouer le rôle de serveur d'enregistrement et de serveur de localisation ; cependant, il ne connecte que deux UAC à lui-même. Par conséquent, Asterisk est considéré comme un agent utilisateur bout à bout (B2BUA). En d'autres termes, il connecte deux canaux SIP, les pontant ensemble. Asterisk possède un mécanisme de re‑invite qui peut faire communiquer les canaux SIP directement entre eux au lieu de passer par Asterisk. Sur un endpoint PJSIP, cela est contrôlé par le paramètre `direct_media`. Lors de l'utilisation de `direct_media=yes` le flux RTP va directement d'un endpoint à l'autre, libérant les ressources du serveur.

#### Opération SIP avec direct_media=yes

![Fonctionnement SIP avec directmedia=yes : le signalement SIP transite par Asterisk tandis que l’audio RTP passe directement entre les deux téléphones, libérant les ressources du serveur](../images/07-sip-and-pjsip-fig05.png)

Cependant, si vous devez transférer ou enregistrer l'appel en utilisant Asterisk, vous pouvez utiliser le paramètre `direct_media=no` pour forcer le flux RTP à travers le serveur Asterisk.

#### Fonctionnement SIP avec direct_media=no

![Opération SIP avec directmedia=no : le signalement SIP et l’audio RTP sont ancrés via Asterisk, ce qui lui permet d’enregistrer, de transcoder ou de transférer l’appel](../images/07-sip-and-pjsip-fig06.png)

#### Messages SIP

Les messages SIP de base sont :

- INVITE – établissement de la connexion
- ACK – accusé de réception
- BYE – terminaison de la connexion
- CANCEL – terminaison de la connexion pour un appel non établi
- REGISTER – enregistrer un UAC auprès d’un proxy SIP
- OPTIONS – peut être utilisé pour vérifier la disponibilité
- REFER – transférer un appel SIP à quelqu’un d’autre
- SUBSCRIBE – s’abonner aux événements de notification
- NOTIFY – envoyer des informations de canal
- INFO – envoyer divers messages (par ex., DTMF )
- MESSAGE – envoyer des messages instantanés

Les réponses SIP sont au format texte et sont facilement lisibles (similaires aux messages HTTP). Les réponses les plus importantes sont :

- 1XX – Messages d'information (100–trying, 180–ringing, 183–progress)
- 2XX – Requête réussie terminée (200 – OK)
- 3XX – Redirection d'appel, la requête doit être dirigée vers un autre endroit (302 – moved temporarily, 305 – use proxy)
- 4XX – Erreur (403 – Forbidden)
- 5XX – Erreur du serveur (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Échec global (606 – Not acceptable)

Par exemple:

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

SDP a été initialement défini dans l'IETF RFC 2327, aujourd'hui remplacé par le RFC 4566. Il sert à décrire les sessions multimédia aux fins d'annonce de session, d'invitation à une session, et d'autres formes d'initiation de session multimédia. SDP comprend :

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

Network Address Translation (NAT) est une fonctionnalité utilisée par la plupart des réseaux pour économiser les adresses IP Internet. En général, une entreprise reçoit un petit bloc d'adresses IP, et les utilisateurs finaux reçoivent une adresse IP de façon dynamique lorsqu'ils se connectent à Internet. NAT résout le problème d'adressage en mappant les adresses internes aux adresses externes. Il stocke un tableau de correspondance des adresses internes et externes dans sa mémoire. Cette correspondance est valable pendant une durée déterminée, après quoi elle est supprimée. Le mappage utilise des paires IP:port pour les adresses internes et externes. Quatre types de NAT existent :

- Cône complet
- Cône restreint
- Cône à ports restreints
- Symétrique

La théorie NAT ci‑dessous — les quatre types de NAT, le problème d’en‑tête Contact, les keep‑alives, et le forçage du média via le serveur — est au niveau du protocole et s’applique à toute implémentation SIP. La façon dont vous configurez chaque comportement sur Asterisk 22 (PJSIP) est abordée plus loin dans ce chapitre sous *Nat traversal on res_pjsip*.

#### Cône complet

Le premier NAT, le cône complet, représente une correspondance statique d’une paire IP :port externe vers une paire IP :port interne. Tout ordinateur externe peut s’y connecter en utilisant la paire IP :port externe. C’est le cas dans les pare‑feu non étatistes implémentés avec l’utilisation de filtres.

![Full Cone NAT : l’hôte interne (10.0.0.1:8000) est mappé statiquement à la paire externe 200.180.4.168:1234, de sorte que tout ordinateur externe peut envoyer des paquets à cette paire et atteindre l’hôte interne](../images/07-sip-and-pjsip-fig11.png)

#### Cône Restreint

Dans le scénario de cône restreint, la paire IP :port externe n’est ouverte que lorsque l’ordinateur interne envoie des données vers une adresse extérieure. Cependant, le NAT à cône restreint bloque tout paquet entrant provenant d’une adresse différente. En d’autres termes, l’ordinateur interne doit envoyer des données à un ordinateur externe avant de pouvoir recevoir des données en retour.

#### Cône à ports restreints

Le pare-feu à cône restreint de port est presque identique au cône restreint. La seule différence est que, maintenant, le paquet entrant doit provenir exactement de la même adresse IP et du même port que le paquet envoyé.

#### Symétrique

Le dernier type de NAT s'appelle symétrique. Il diffère des trois premiers en ce qu'une correspondance spécifique est faite pour chaque adresse externe. Seules des adresses externes spécifiques sont autorisées à revenir via la correspondance NAT. Il n'est pas possible de prédire la paire IP:port externe qui sera utilisée par le dispositif NAT. Les trois autres types de NAT permettent l'utilisation d'un serveur externe pour découvrir l'adresse IP externe pour la communication. Avec le NAT symétrique, même si vous pouvez vous connecter à un serveur externe, l'adresse découverte ne peut être utilisée pour aucun autre dispositif que ce serveur.

![NAT symétrique : un port source externe différent est attribué pour chaque destination, de sorte que le mappage découvert vers un serveur ne peut pas être réutilisé par un autre hôte, ce qui empêche le contournement basé sur STUN】(../images/07-sip-and-pjsip-fig12.png)

#### Tableau du pare-feu NAT

Le tableau suivant résume les quatre types de NAT.

| Type NAT | Doit envoyer des données d'abord | Peut déterminer l'IP:port externe pour les paquets de retour | Restreint les paquets entrants à l'IP:port de destination |
| --- | --- | --- | --- |
| Full Cone | No | Yes | No |
| Restricted Cone | Yes | Yes | Only IP |
| Port Restricted Cone | Yes | Yes | Yes |
| Symmetric | Yes | No | Yes |

#### Signalisation SIP et RTP sur NAT

Certaines des plus grandes problématiques de la traversée NAT sont que vous devez résoudre deux problèmes : le signalement SIP et l’audio (RTP). La plupart des problèmes d’audio à sens unique sont liés au NAT. Une chose intéressante concernant SIP est que, lorsqu’un UAC envoie un paquet, il intègre l’adresse IP dans le champ d’en‑tête SIP « Contact ». Habituellement il s’agit d’une adresse interne (RFC1918) ; les réponses à ce paquet ne peuvent pas être routées sur Internet vers l’UAC. Les solutions conceptuelles sont toujours les mêmes :

- **Ignore the Contact/Via address and reply to where the packet actually came from.** This is the behaviour defined in RFC 3581 (`rport`). On PJSIP it is `force_rport=yes`, and `rewrite_contact=yes` rewrites the stored contact to the source address.  
- **Send media back to the address the RTP actually arrived from** (symmetric RTP, historically called *comedia*). On PJSIP this is `rtp_symmetric=yes`.  
- **Keep the NAT mapping open.** If the mapping times out, Asterisk can no longer send an INVITE to the UAC — the phone can place calls but not receive them. Sending a periodic OPTIONS (a *qualify*) keeps the pinhole open. On PJSIP this is `qualify_frequency=` on the AOR.

Si le NAT de l'utilisateur est du type symétrique, il n'est pas possible d'envoyer des paquets d'un UAC à un autre directement ; dans ce cas, vous devez forcer le RTP à travers Asterisk avec `direct_media=no`. Ces configurations conviennent à la plupart des cas. Il est possible d'optimiser le trafic en utilisant des techniques avancées comme le Simple Traversal of UDP over NAT (STUN), qui est utile avec les cônes complets, les cônes restreints et les cônes à ports restreints, ainsi que l'Application Layer Gateway (ALG). Malheureusement, la plupart des pare‑feux aujourd'hui — même les routeurs DSL/câble domestiques — sont symétriques, rendant STUN inutilisable. ALG pourrait résoudre le problème, mais il n'est pas supporté, pas implémenté, ou bogué dans la plupart des cas.

#### Asterisk derrière NAT

Parfois, le serveur Asterisk lui‑même est déployé derrière un pare‑feu avec NAT — une situation très courante lorsque vous déployez dans le cloud. Dans ce cas, il est nécessaire d’effectuer une configuration supplémentaire afin qu’Asterisk annonce son adresse **public** dans les en‑têtes SIP et SDP au lieu de son adresse privée.

Conceptuellement il y a trois étapes:

- Rediriger le port de signalisation SIP (UDP 5060 par défaut) du pare‑feu vers le serveur Asterisk.
- Rediriger la plage de ports médias RTP (UDP 10000–20000 par défaut, définie dans `rtp.conf`) du pare‑feu vers le serveur Asterisk.
- Indiquer à Asterisk son adresse externe et quel réseau est local, afin qu’il sache quand substituer l’adresse publique dans les en‑têtes.

Sur PJSIP, ces deux derniers éléments correspondent à `external_media_address` / `external_signaling_address` et `local_net=` sur le **transport**, et la plage de ports RTP est toujours configurée dans `rtp.conf`:

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

The complete, worked PJSIP configuration for an Asterisk server behind NAT is given later in this chapter under *Asterisk Server behind NAT*.

### Limitations SIP

Asterisk utilise le flux RTP entrant pour synchroniser le flux sortant. Si le flux entrant est interrompu (suppression du silence), la musique d’attente sera coupée. En d’autres termes, vous ne devez pas utiliser la suppression du silence sur les téléphones ou auprès des fournisseurs avec Asterisk.

## PJSIP : le canal SIP

PJSIP est le canal SIP dans Asterisk. Il a été introduit pour la première fois dans Asterisk 12 et, après des années de développement, est devenu le canal SIP par défaut et recommandé, et dans Asterisk 22 (le LTS actuel) il est le seul pilote de canal SIP. PJSIP repose sur le projet de Teluu appelé pjproject. La pile pjproject est utilisée par de nombreux softphones et implémentations SIP commerciales. C’est une pile SIP polyvalente et mature.

### Pourquoi utiliser PJSIP

PJSIP a été une refonte complète de la façon dont Asterisk parle SIP, et il est utile de comprendre les fonctionnalités qui en ont fait la norme.

#### Fonctionnalités

Le canal prend en charge de nombreuses fonctionnalités, certaines méritent d’être mentionnées ici

- Enregistrements multiples : Vous pouvez utiliser plus d’un téléphone connecté au même Address of Record. En d’autres termes, vous pouvez connecter deux téléphones au même endpoint.
- Interface de programmation d’application (API) conviviale. L’API est modulaire et facile à étendre, construite à partir de nombreux petits modules coopérants plutôt que d’un seul gros bloc de code.
- Transports multiples : Vous pouvez écouter plusieurs adresses, ports et transports lors de l’utilisation de PJSIP. Vous n’êtes pas limité à une adresse de liaison unique pour tous vos appareils. PJSIP est très flexible.

#### Une note sur la configuration

La configuration de PJSIP est plus verbeuse : elle nécessite un peu plus d’effort et davantage de lignes de configuration, chaque appareil étant décrit par plusieurs objets liés au lieu d’un seul bloc peer. Cette structure supplémentaire est ce qui confère à PJSIP sa flexibilité, et l’assistant de configuration (décrit plus loin) maintient la mise en service quotidienne courte.

### Modules PJSIP

Le canal PJSIP est implémenté par de nombreux modules décrits ci‑dessous :

#### res_pjsip

Il s’agit de la couche de base de PJSIP et du module principal. Il est responsable de certains des services principaux.

#### res_pjsip_session

Ce module est responsable des sessions média, du traitement du protocole de description de session et de quelques extensions.

#### res_pjsip_messaging

Traite les messages SIP et analyse les en‑têtes SIP.

#### res_pjsip_registrar

Responsable de la gestion des enregistrements SIP.

#### res_pjsip_pubsub

Responsable du traitement des subscribe, notify et publish. Ces messages sont responsables de la gestion de la présence SIP et du BLF (Busy Lamp Field).

### Configuration PJSIP

PJSIP possède de nombreuses sections différentes. Le format de la section est :

```
[Section Name]
Option = Value
Option = Value
```

#### Section endpoint

L'objet de configuration le plus important est l'endpoint. La configuration de l'endpoint possède les fonctionnalités de base et doit être associée à une section AOR et Transport. Example:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

Si vous examinez l’exemple ci‑dessus, le endpoint est une sorte de colle qui relie toutes les sections entre elles. Il spécifie un transport, l’adresse d’enregistrement et l’authentification pour un téléphone. Il définit également la partie la plus importante, le point d’entrée du context dans le dialplan.

#### Address of Record (AOR)

Cet objet indique à Asterisk où contacter le endpoint. Il stocke les adresses de contact. Il permet aussi la configuration des boîtes vocales. Exemple:

```
[softphone]
type=aor
max_contacts=2
```

#### Authentification

Cette section est responsable de l'authentification entrante et sortante. La documentation se trouve dans le fichier d'exemple pjsip.conf. Exemple:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### Transport

La section transport vous permet de définir des adresses IPV4 et IPV6 ainsi que le protocole de transport, TCP, UDP, TLS, Websockets, etc. Vous pouvez également configurer des adresses NATées dans cette section. Vous pouvez créer plusieurs transports, mais ils ne peuvent pas partager la même IP et le même port et vous ne pouvez pas lier plusieurs transports TCP ou TLS de la même version IP. Exemple:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Enregistrement

Cet objet est utilisé pour configurer un enregistrement sortant. Exemple:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identifier

Cet objet contrôle à quelle requête SIP appartient chaque endpoint. Si vous n’avez pas de section identify, le système fera correspondre le contenu de l’en‑tête « From » avec le nom de l’endpoint. En utilisant cette section, vous pouvez attribuer des adresses IP spécifiques à des endpoints spécifiques, identifiés par nom d’utilisateur ou IP. Exemple:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

L'objet ACL vous permet de configurer des réseaux spécifiques avec accès à l'endpoint. Désormais, les ACL sont définies dans une section spécifique ou dans le fichier acl.conf. Exemple:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relation entre les entités

La relation entre les objets de configuration offre une grande flexibilité. Cependant, elle peut sembler un peu complexe pour les débutants.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

Le graphique ci‑dessus signifie :

#### Relations :

| Objets | Cardinalité |
| --- | --- |
| ENDPOINT / AOR | plusieurs à plusieurs |
| ENDPOINT / AUTH | zéro à plusieurs, à zéro à un |
| ENDPOINT / IDENTIFY | zéro à un |
| ENDPOINT / TRANSPORT | zéro à plusieurs, à au moins un |
| REGISTRATION / AUTH | zéro à plusieurs, à zéro à un |
| REGISTRATION / TRANSPORT | zéro à plusieurs, à au moins un |
| AOR / CONTACT | plusieurs à plusieurs |

ACL et DOMAIN_ALIAS n’ont pas de relation de configuration directe avec les autres objets.

### Configuration d’un softphone

Pour configurer un softphone, vous devez définir de nombreuses sections différentes. Voici un exemple de configuration d’un softphone. Du côté client, vous pouvez utiliser le SipPulse Softphone (https://www.sippulse.com/produtos/softphone), que vous pouvez télécharger et enregistrer contre l’endpoint ci‑dessus.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

La configuration ci‑dessus définit un transport UDP sur le port 5060, puis définit un endpoint, son authentification par nom d'utilisateur et mot de passe, puis l'Address of Record avec un maximum de deux contacts.

### Configuration d'un trunk SIP

Pour configurer un trunk SIP, vous devez disposer de l'adresse IP ou du Host du trunk SIP, du nom et du mot de passe. Vous devez créer une nouvelle section d'enregistrement à cette fin.

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
auth_type=digest
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

Le Network Address Translation a été créé il y a longtemps comme moyen de pallier la pénurie d'adresses IPv4. De nombreuses personnes utilisent également le NAT comme fonction de sécurité en masquant les adresses internes d’un réseau depuis Internet public. Parfois, vous devrez gérer la traversée NAT. Dans certains cas, le serveur peut se trouver derrière un NAT, par exemple lorsque vous déployez le serveur dans le cloud. Bien souvent, si vous déployez dans le cloud, vos utilisateurs seront également derrière un routeur NAT. Pour organiser les choses, nous allons diviser cela en deux parties. La première concerne le serveur Asterisk derrière NAT, comme dans un déploiement cloud. Dans la deuxième section, nous verrons comment prendre en charge les clients derrière NAT en utilisant res_pjsip.

#### Serveur Asterisk derrière NAT

Lorsque le serveur Asterisk se trouve derrière NAT, vous devez indiquer les adresses locales externes et internes dans la section transport. Nous aurons les directives suivantes.

##### direct_media

Le média circule-t-il directement de pair à pair ou via le serveur ? Pour le NAT, il doit passer par le serveur. Pour le NAT, choisissez **no**. Exemple :

```
direct_media=no
```

##### external_media_address

Adresse média pour gérer le RTP externe. Habituellement la même que external_signaling_address. Utilisez l'adresse IP publique de votre serveur pour le média et la signalisation. Exemple :

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Adresse SIP externe où recevoir les messages. Exemple :

```
external_signaling_address=54.232.1.20
```

##### local_net

Le réseau que vous considérez comme votre réseau local. Exemple:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Exemple complet de transport pour un serveur Asterisk derrière un NAT

To use an Asterisk server behind NAT you have to do two steps. First, define a transport behind NAT. Two, associate this transport to the endpoint.

##### Création du transport derrière le NAT

To create the transport behind NAT in the file pjsip.conf create a section like below.

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

Associer le transport à un point de terminaison

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Pour les trunks SIP vous devez également associer le transport à la section d’enregistrement comme ci‑dessous.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Utilisation d'Asterisk avec des clients derrière le NAT

Pour utiliser des téléphones derrière le NAT, vous devez configurer des paramètres supplémentaires par endpoint.

##### direct_media

Le flux média passe-t-il directement de pair à pair ou via le serveur ? Pour le NAT, il doit passer via le serveur. Exemple:

```
direct_media=no
```

##### rtp_symmetric

C’est ce que l’on appelle la comédie. Au lieu de se fier à l’adresse définie dans cet en‑tête SDP comme d’habitude dans SIP, utilisez l’adresse d’où vous recevez le premier paquet RTP et renvoyez depuis la même adresse. Exemple:

```
rtp_symmetric=yes
```

##### force_rport

Il s'agit du comportement défini dans la RFC3581. Au lieu d'utiliser l'adresse dans l'en-tête VIA, renvoyez les réponses depuis l'endroit d'où proviennent les requêtes. Exemple :

```
force_rport=yes
```

##### qualify_frequency

Ce paramètre doit être appliqué à l'AOR (et non à l'endpoint). Il y a également la dernière étape, qui consiste à configurer l'option **qualify**. Vous devez toujours faire en sorte que des paquets pinguent la destination afin de maintenir la correspondance NAT ouverte. Cela se définit dans la section AOR. Exemple :

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

Comme d'habitude, l'un des aspects importants d'un canal est son nommage et PJSIP présente quelques détails intéressants. Vous composez un endpoint PJSIP avec la `PJSIP/` technologie.

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Une fonctionnalité utile est la possibilité de composer tous les contacts enregistrés à un AOR en une seule fois. La fonction PJSIP_DIAL_CONTACTS sera traduite en la liste des contacts à composer.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

To dial a trunk is slightly different. Assume the trunk won’t be registered to your platform or don’t have and IP address associated with your AOR address of record. You can specify the address of the trunk directly in the line. Using an international dial as the example.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Si vous préférez spécifier l'adresse du trunk dans la section AOR, vous pouvez également l'utiliser.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### Assistant de configuration PJSIP

PJSIP est puissant mais verbeux à configurer : de nombreuses sections différentes, et des modèles qui peuvent prêter à confusion au départ. La bonne nouvelle, c’est l’assistant de configuration PJSIP. En définissant chaque canal en quelques lignes, il vous permet de créer des modèles et de simplifier la configuration de nouveaux appareils. Utilisez le fichier **pjsip_wizard.conf** pour configurer. Vous devez toujours définir les sections transport et global dans le fichier **pjsip.conf**. Personnellement, je préfère n’utiliser l’assistant que pour les téléphones ; pour les trunks SIP, le nombre est généralement faible et vous pouvez les configurer directement dans pjsip. Le principal avantage de l’assistant est la possibilité d’utiliser des modèles et de créer rapidement des téléphones.

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
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Chargement et déchargement de PJSIP

PJSIP est le seul canal SIP dans Asterisk 22, et ses modules sont chargés par défaut. Dans de rares cas, vous pouvez encore vouloir contrôler le chargement des modules depuis le fichier modules.conf — par exemple, pour désactiver PJSIP sur un serveur qui n'utilise que IAX2 ou DAHDI.

#### Pour désactiver PJSIP

Modifiez le fichier modules.conf et ajoutez les lignes suivantes.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### Commandes console

Maintenant que vous avez configuré vos endpoints PJSIP, il est temps de voir comment vérifier votre configuration. Il existe de nombreuses commandes console pour vous aider dans cette tâche. Après avoir modifié pjsip.conf, rechargez la configuration avec:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

Vous pouvez également restreindre la journalisation à un seul hôte avec `pjsip set logger host <ip>`.

#### pjsip set history on

Une excellente addition à PJSIP est le concept d’historique. Vous pouvez capturer et analyser les requêtes et réponses SIP en temps réel de manière simple. Pour démarrer l’historique, utilisez la commande ci‑dessous.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Vous pouvez maintenant afficher l’historique :

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Puis, pour voir une requête ou une réponse spécifique, affichez l’élément d’historique :

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Très simple, n’est‑ce pas ? Vous pouvez également effacer l’historique quand vous le souhaitez en utilisant `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Summary

SIP est le protocole de signalisation IETF qui établit, modifie et termine les sessions média. Ses agents utilisateurs, proxys, registreurs et passerelles échangent des messages textuels — REGISTER, INVITE, les réponses provisoires et finales, ACK et BYE — tandis que SDP négocie les codecs et RTP transporte le média. Cette théorie du protocole est intemporelle et s’applique à toute implémentation SIP.

Dans Asterisk 22 vous utilisez SIP via **PJSIP** (`chan_pjsip`), configuré dans `pjsip.conf`. Au lieu d’un seul pair monolithique, un appareil est modélisé comme un ensemble de petits objets inter‑référencés : `endpoint` (comportement d’appel et codecs), `auth` (identifiants), `aor` (où il est joignable), et `transport` (l’écouteur), plus `identify` (correspondance d’un trunk par IP) et `registration` (enregistrement sortant) pour les fournisseurs de services. Vous avez vu comment ces objets s’assemblent, comment configurer à la fois les téléphones et les trunks, comment les options de traversée NAT (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media`, et les `external_*`/`local_net` du transport) résolvent les déploiements réels, et comment inspecter le tout avec `pjsip show endpoints`, `aors`, `contacts` et `registrations`.

## Quiz

1. Dans l'architecture SIP, quel composant reçoit une requête et y répond avec une réponse de redirection (telle que `302 Moved Temporarily`) contenant la nouvelle localisation, puis reste hors du chemin des messages suivants ?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. Quel rôle Asterisk joue‑t‑il lorsqu’il gère un appel SIP entre deux téléphones ?
   - A. A SIP proxy that stays only in the signaling path
   - B. A SIP redirect server
   - C. A back-to-back user agent (B2BUA) that bridges two SIP channels
   - D. A stateless SIP load balancer

3. Quelle méthode SIP est utilisée par un téléphone pour informer le registrar de son adresse IP actuelle afin de pouvoir recevoir des appels ultérieurement ?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Vrai ou Faux : Dans Asterisk 22, `chan_sip` et `sip.conf` sont toujours disponibles comme solution de secours legacy aux côtés de PJSIP.

5. Quels objets de configuration un endpoint doit‑il être associé afin qu’Asterisk connaisse la socket d’écoute à utiliser et où envoyer les appels pour cet appareil ? (Choisissez toutes les réponses applicables.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. Dans un objet PJSIP `aor`, quel paramètre maintient la correspondance NAT ouverte en qualifiant périodiquement le contact, et quelle est son unité ?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. Complétez la phrase : Pour que Asterisk associe une requête SIP entrante à un endpoint spécifique par adresse IP source (au lieu de l’en‑tête `From`), vous créez une section avec `type=________`.

8. Quel objet PJSIP est utilisé pour configurer un **enregistrement sortant** d’Asterisk vers un fournisseur de trunk SIP ?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Sur la CLI d’Asterisk 22, quelle commande active le journalisateur de paquets SIP qui affiche chaque requête et réponse SIP dans la console ?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Sur un endpoint PJSIP qui sert un téléphone derrière un NAT symétrique, quelle paire de paramètres fait qu’Asterisk répond à l’adresse source de la requête (RFC 3581) et renvoie les médias là où le RTP arrive réellement ?
    - A. `direct_media=yes` and `srvlookup=yes`
    - B. `force_rport=yes` and `rtp_symmetric=yes`
    - C. `allowguest=yes` and `insecure=invite`
    - D. `qualify=yes` and `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
