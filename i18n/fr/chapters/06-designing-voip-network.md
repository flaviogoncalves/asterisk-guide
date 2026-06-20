# Designing a VoIP network

Voice over IP is quickly growing in the telephony market. The convergence paradigm is changing the way in which we communicate, reducing costs and enhancing the way in which we trade information. Voice is just the beginning of a full multimedia communication era, including voice, video, and presence. In the future, we are not going to transport people to work, but work to people because it is cleaner, faster, and cheaper. VoIP is just part of this revolution. Our challenge in this chapter is to design a VoIP network. To do this, we will have to understand concepts such as session protocols and codecs as well as how to dimension the number of circuits and bandwidth.

## Objectives

À la fin de ce chapitre, vous devriez être capable de :

- Comprendre les avantages de la VoIP
- Décrire comment Asterisk gère la VoIP
- Décrire les concepts des canaux SIP et IAX
- Choisir le protocole le plus adéquat pour un canal de données spécifique
- Choisir le codec le plus adéquat pour un canal de données spécifique
- Dimensionner le nombre de canaux requis
- Calculer la bande passante nécessaire

## Avantages de la VoIP

Pourquoi s’intéresser à la VoIP ? La VoIP offre des avantages tant aux entreprises qu’aux particuliers. La réduction des coûts en est évidemment un, mais dans certains environnements la VoIP simplifie l’intégration des systèmes informatiques. Plusieurs de ces avantages sont détaillés ci‑dessous :

### Convergence

Le principal avantage de la VoIP est la combinaison des réseaux de données et de voix pour réduire les coûts (convergence). Cependant, analyser uniquement le coût des minutes vocales peut ne pas suffire à justifier l’adoption de la VoIP. Le prix des minutes vendues par les opérateurs téléphoniques devient rapidement moins cher et constitue un élément à prendre en compte avant de passer à la VoIP.

### Coûts d’infrastructure

L’utilisation d’une infrastructure réseau unique réduit les coûts liés aux ajouts, suppressions et modifications. À mesure que l’IP s’est généralisée, elle a apporté la technologie liée à la VoIP à de nombreux nouveaux appareils, tels que les téléphones cellulaires, les PDA, les systèmes embarqués et les ordinateurs portables.

### Standards ouverts

Enfin, les standards ouverts sur lesquels repose la VoIP offrent la liberté de choisir parmi différents fournisseurs. Cet unique avantage place le client au centre, plutôt que comme simple subordonné aux TELCOS et aux fabricants de PBX.

### Intégration téléphonie‑informatique

La téléphonie est bien plus ancienne que l’informatique. Les PBX téléphoniques sont basées sur le commutateur à circuits, et vous ne disposez généralement pas de plus d’un ordinateur pour la supervision. Avec la VoIP, la téléphonie est créée dès le départ selon des standards informatiques. Cela rend l’utilisation d’applications de téléphonie‑informatique moins chère et plus simple qu’avec l’ancien modèle. Vous pouvez rapidement créer une longue liste d’applications téléphoniques basées sur Asterisk. Vous pouvez développer des IVR, ACD, CTI, composeurs automatiques, fenêtres contextuelles, et d’autres applications en une fraction du temps requis pour les PBX traditionnels.

## Architecture VoIP d'Asterisk

L'architecture d'Asterisk est illustrée ci‑dessous. Asterisk traite tous les protocoles VoIP comme des canaux. Vous pouvez utiliser n'importe quel codec ou n'importe quel protocole. Le concept à retenir ici est qu'Asterisk relie tout type de canal à tout autre. Ainsi, vous pouvez traduire les protocoles de signalisation tels que SIP et IAX les uns vers les autres, même avec des codecs différents. Par exemple, vous pouvez traduire un appel d'un téléphone SIP sur le réseau local utilisant le codec G.711 vers un trunk SIP de votre fournisseur VoIP utilisant le codec G.729. Dans les chapitres suivants, nous expliquerons les détails de l'architecture SIP et IAX. Le support H.323 (via le module chan_ooh323) est disponible mais de plus en plus rare ; SIP/PJSIP est la norme pour les déploiements modernes.

![Architecture modulaire d'Asterisk : les applications et les canaux se connectent au cœur du commutateur PBX via des API, avec traduction de codecs et modules de formats de fichiers chargés dynamiquement.](../images/06-voip-network-fig01.png)

## Protocoles VoIP et la pile réseau

Le VoIP utilise un ensemble de protocoles différents qui fonctionnent ensemble. Il est tentant de les aligner avec le modèle de référence OSI à sept couches, et de nombreux diagrammes anciens le font exactement — plaçant SIP et H.323 au niveau « session » et les codecs au niveau « présentation ». Cette correspondance a toujours été controversée. L'IETF, qui normalise SIP, n'utilise pas le modèle OSI ; il suit le modèle TCP/IP à quatre couches (DoD) plus ancien, et le RFC 3261 définit **SIP comme un protocole de couche application**. Les médias suivent le même schéma : RTP et les codecs résident dans la charge utile d'application, transportés sur UDP au niveau transport. Le tableau ci‑dessous associe les principaux protocoles VoIP au modèle TCP/IP réellement utilisé par l'IETF, avec l’équivalent OSI approximatif indiqué uniquement à titre de référence.

| Couche TCP/IP (IETF) | Protocoles | Équivalent OSI approximatif |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

Les mécanismes QoS tels que DiffServ fonctionnent au niveau IP pour prioriser les paquets voix et améliorer la qualité des appels. Quelques spécificités de protocole :

- **SIP** utilise UDP ou TCP sur le port 5060 (TLS sur 5061) pour transporter la signalisation. L’audio est transporté séparément par RTP sur une plage de ports UDP configurable (l’exemple `rtp.conf` fourni avec Asterisk utilise 10000 à 20000), encodé avec un codec tel que G.711.
- **H.323** transporte la signalisation d’appel sur TCP (signalisation d’appel H.225 sur le port 1720), tandis que le canal H.225 RAS utilise UDP sur le port 1719 ; RTP transporte l’audio.
- **IAX2** est inhabituel : il multiplexe à la fois la signalisation et les médias sur un seul port UDP (4569), ce qui simplifie le franchissement NAT et pare‑feu.


## Comment choisir un protocole

Étant donné le grand nombre de protocoles, comment choisir le meilleur pour votre réseau ? Dans cette section, nous mettrons en avant les avantages et les inconvénients de chaque protocole.

### SIP - Session Initiated Protocol

SIP est une norme ouverte de l’Internet Engineering Task Force (IETF), largement définie dans le RFC 3261. La plupart des fournisseurs VoIP modernes utilisent SIP ; en effet, il devient la norme VoIP la plus populaire. La force de SIP réside dans le fait qu’il s’agit d’une norme basée sur l’IETF. SIP est léger comparé au plus ancien H.323. La principale faiblesse de SIP est le contournement du NAT — un défi pour la plupart des fournisseurs VoIP SIP. L’IETF n’a pas créé SIP avec la facturation à l’esprit, mais pour des communications ouvertes entre pairs. La facturation est généralement une préoccupation pour les fournisseurs VoIP.

### IAX – Inter Asterisk eXchange

IAX est un protocole ouvert développé à l’origine par Digium (maintenant Sangoma). IAX est un protocole tout‑en‑un car il transporte la signalisation et les médias via le même port UDP (4569). Mark Spencer a développé IAX comme un protocole binaire pour réduire la bande passante. La principale force d’IAX est sa consommation réduite de bande passante (il n’utilise pas RTP) ; il est également très facile à faire traverser les NAT et les pare‑feux puisqu’il n’utilise qu’un seul port UDP (4569).

Si un fabricant de PBX traditionnel avait créé IAX, il l’aurait probablement commercialisé comme « la meilleure chose depuis la crème glacée » ; dans certaines situations, IAX en mode trunk peut réduire l’utilisation de la bande passante vocale d’un tiers. IAX2 (version 2) est toujours fourni avec Asterisk 22 via le module `chan_iax2` et reste utile pour les trunks Asterisk‑to‑Asterisk, bien qu’il soit considéré comme hérité ; SIP/PJSIP est préféré pour les nouvelles installations. IAX2 est spécifié dans [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP est un protocole utilisé en conjonction avec H.323, SIP et IAX. Son plus grand avantage est l’évolutivité. Il est configuré dans l’agent d’appel plutôt que dans les passerelles. Cela simplifie le processus de configuration et permet une gestion centralisée. Cependant, l’implémentation dans Asterisk n’est pas complète, et il semble que peu de personnes l’utilisent.

### H.323

H.323 est encore largement utilisé dans la VoIP. C’est l’un des premiers protocoles VoIP et il est essentiel pour connecter les anciennes infrastructures VoIP basées sur des passerelles. H.323 reste la norme sur le marché des passerelles, bien que le marché migre lentement vers SIP. Les forces de H.323 incluent la large adoption du marché et la maturité. Les faiblesses de H.323 sont liées à la complexité de mise en œuvre et aux coûts associés aux organismes de normalisation.

### Tableau de comparaison des protocoles

Le tableau suivant résume les différences entre les protocoles de session.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core ; le seul pilote SIP — `chan_sip` a été supprimé dans Asterisk 21) | SIP phones ; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core ; still shipped, considered legacy) | Asterisk-to-Asterisk trunks ; IAX2 phones ; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## Un point de terminaison par appareil

Dans Asterisk 22, la pile PJSIP modélise chaque téléphone, trunk ou passerelle comme un seul objet **endpoint** dans `pjsip.conf`. Un endpoint place et reçoit les appels ; ses informations d’identification résident dans un objet `auth`, son adresse enregistrée dans un `aor`, et son chemin réseau dans un `transport`. Vous configurez un endpoint par appareil et vous y attachez les éléments nécessaires — il n’existe aucun rôle distinct « user » ou « peer » à gérer. (Le modèle complet des objets est présenté dans *SIP & PJSIP in depth*.)

## Codecs and codec translation

Vous utiliserez un codec pour convertir la voix d’une onde analogique en un signal numérique. Les codecs diffèrent les uns des autres sur des aspects tels que la qualité sonore, le taux de compression, la bande passante et les exigences de calcul. Les services, téléphones et passerelles prennent généralement en charge plusieurs de ces aspects. Le codec G.729 est très populaire. Il ne fait pas partie de la version standard d’Asterisk 22 ; il est fourni comme module externe (`codec_g729`) que vous téléchargez auprès de Digium (aujourd’hui Sangoma). Le source `menuselect` d’Asterisk le répertorie avec `support_level=external` et indique clairement : « Download the g729a codec from Digium. A license must be purchased for this codec. ». En d’autres termes, l’utilisation légale du G.729 nécessite l’achat d’une licence par canal. (Une alternative open‑source, `bcg729`, existe également.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 prend en charge les codecs suivants (entre autres) :

- GSM : 13 Kbps
- iLBC : 13,3 Kbps
- ITU G.711 (ulaw/alaw) : 64 Kbps — qualité PSTN standard ; ulaw couramment utilisé en Amérique du Nord, alaw en Europe et en Amérique latine
- ITU G.722 : 64 Kbps — large bande (voix HD), bonne qualité avec la même bande passante que le G.711
- ITU G.723.1 : 5,3/6,3 Kbps
- ITU G.726 : 16/24/32/40 Kbps
- ITU G.729 : 8 Kbps — module binaire externe `codec_g729` téléchargé depuis Digium/Sangoma (`support_level=external` ; une licence doit être achetée pour l’utiliser)
- Speex : 2,15 à 44,2 Kbps
- LPC10 : 2,4 Kbps
- **Opus** : 6–510 Kbps, variable — codec moderne large‑band/full‑band ; excellente qualité et résilience aux pertes de paquets ; fourni comme module binaire externe `codec_opus` téléchargé depuis Digium/Sangoma (`support_level=external` ; aucune licence d’achat n’est mentionnée, contrairement au G.729) ; recommandé pour WebRTC et les points d’extrémité SIP modernes. (Des alternatives de construction open‑source existent sur GitHub.)

De plus, Asterisk autorise la traduction entre codecs. Dans certains cas, cela n’est pas possible, comme pour le g723, qui n’est supporté qu’en mode pass‑thru. Traduire d’un codec à un autre consomme de nombreuses ressources CPU. Il faut donc éviter cela autant que possible.

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## Overhead caused by protocol headers

Despite the fact that codecs make little use of bandwidth, we have to consider the overhead caused by protocol headers such as Ethernet, IP, UDP, and RTP. As such, the bandwidth actually consumed depends on the headers used. On an Ethernet network the requirement is higher than on a PPP network, because the PPP header is shorter than the Ethernet one. A single G.729 voice packet, for example, carries only 20 bytes of payload but is wrapped in roughly 58 bytes of Ethernet, IP, UDP, and RTP headers — so the headers, not the codec, dominate the bandwidth (see the figure below).

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

You can easily calculate other bandwidth requirements using an online VoIP bandwidth calculator such as <https://www.voip.school/bandcalc/bandcalc.php>.


## Traffic Engineering

Un problème majeur dans la conception des réseaux VoIP est le dimensionnement du nombre de lignes et de la bande passante requise vers une destination spécifique, comme un bureau distant ou un fournisseur de services. Il est également important de dimensionner le nombre d’appels simultanés d’Asterisk (paramètre principal pour le dimensionnement d’Asterisk).

### Simplifications

La simplification principale et la plus largement utilisée consiste à estimer le nombre d’appels par type d’utilisateur. Par exemple :

- PBX d’entreprise (un appel simultané pour cinq postes)
- Utilisateurs résidentiels (un appel simultané pour seize utilisateurs)

Exemple #1 Le siège de l’entreprise possède 120 postes et deux succursales — la première avec 30 postes et la seconde avec 15 postes. Notre objectif est de dimensionner le nombre de trunks E1 au siège et la bande passante requise pour le réseau Frame‑Relay.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Nombre de lignes T1

- Nombre total de postes utilisant des lignes T1 : 120+30+15=165 lignes
- Utilisation d’un trunk pour chaque cinq postes pour un usage professionnel
- Nombre total de lignes = 33 ou approximativement 2×T1 lignes

1b Exigences de bande passante Nous choisissons le codec g.729 en raison des exigences de bande passante, de la qualité sonore et de la consommation moyenne du CPU.

Avec un trunk pour chaque cinq postes :

- Bande passante requise pour la succursale #1 (Frame‑relay) : 26.8×6=160.8 Kbps
- Bande passante requise pour la succursale #2 (Frame‑relay) : 26.8×3= 80.4 Kbps

### Méthode Erlang B

Lorsque vous disposez de données historiques, vous pouvez dimensionner le trunk de façon plus scientifique au lieu de simplifier. Nous utiliserons le travail d’Agner Karup Erlang (Copenhagen Telephone Company, 1909), qui a développé une formule pour calculer le nombre de lignes dans un groupe de trunks entre deux villes.

Un **Erlang** est une unité de mesure du trafic courante dans les télécoms ; elle décrit le volume de trafic pendant une heure. Par exemple, supposons que 20 appels se produisent en une heure, avec une moyenne de 5 minutes de conversation chacun :

- Minutes de trafic dans l’heure : 20 × 5 = 100 minutes
- Heures de trafic sur une heure : 100 / 60 = **1,66 Erlangs**

Vous pouvez lire ces mesures à partir d’un journal d’appels et les utiliser pour concevoir votre réseau et calculer le nombre de lignes nécessaires. Une fois le nombre de lignes connu, vous pouvez calculer les exigences de bande passante.

**Erlang B** est la méthode la plus couramment utilisée pour calculer le nombre de lignes dans un groupe de trunks. Elle suppose que les appels arrivent aléatoirement (distribution de Poisson) et que les appels bloqués sont immédiatement libérés. Elle nécessite que vous connaissiez le **Busy Hour Traffic (BHT)**, que vous pouvez obtenir à partir d’un journal d’appels ou estimer comme simplification : BHT = 17 % des minutes d’appels d’une journée.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Une autre variable importante est le Grade of Service (GoS), qui définit la probabilité de blocage des appels par manque de lignes. Vous pouvez arbitrer ce paramètre, généralement 0,05 (5 % d’appels perdus) ou 0,01 (1 % d’appels perdus). Exemple #1 : En utilisant le même exemple de siège et deux succursales présenté plus haut, nous vous fournirons quelques données sur les modèles de trafic. À partir du journal d’appels, nous avons découvert ces données : Données du journal d’appels (minutes d’appels et BHT) :

- Siège vers Succursale #1 = 2 000 minutes, BHT = 300 minutes
-

## Réduire la bande passante requise pour la VoIP

Trois méthodes peuvent être utilisées pour réduire la bande passante requise pour les appels VoIP :

- Compression d’en-tête RTP
- Trunk IAX
- Charge utile VoIP

### Compression d’en-tête RTP

Dans les réseaux Frame‑Relay et PPP, vous pouvez utiliser la compression d’en‑tête RTP. La compression d’en‑tête RTP a été définie dans la RFC 2508. C’est une norme IETF disponible sur plusieurs routeurs. Cependant, soyez prudent, car certains routeurs nécessitent un ensemble de fonctionnalités différent pour que cette ressource soit disponible. L’impact de l’utilisation de la compression d’en‑tête RTP est remarquable puisqu’elle réduit la bande passante requise dans notre exemple de 26,8 Kbps par conversation vocale à 11,2 Kbps — une réduction de 58,2 % !

### Mode trunk IAX2

Si vous connectez deux serveurs Asterisk, vous pouvez utiliser le protocole IAX2 en mode trunk. Cette technologie révolutionnaire ne nécessite aucun routeur spécial et peut être appliquée à tout type de liaison de données.

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

Le mode trunk IAX2 réutilise les mêmes en‑têtes à partir du deuxième appel et ainsi de suite. En utilisant g729 sur une liaison PPP, le premier appel consommera 30 Kbps de bande passante, tandis que le deuxième appel utilisera le même en‑tête que le premier et réduira la bande passante nécessaire pour l’appel supplémentaire à 9,6 Kbps. Nous pouvons calculer la bande passante requise en mode trunk comme suit : Branche #1 (11 appels) Bande passante = 31,2 + (11‑1)* 9,6 Kbps = 127,2 Kbps Branche #2 (8 appels) Bande passante = 31,2 + (8‑1)* 9,6 Kbps = 98,4 Kbps Le premier appel utilise 31,2 Kbps, le suivant 9,6 Kbps, etc.

### Augmentation de la charge utile vocale

Cette méthode est très courante lors de l’utilisation de passerelles VoIP sur Internet. En utilisant une charge utile plus importante, vous sacrifiez la latence au profit d’une bande passante réduite. Vous pouvez modifier la packetisation RTP en ajoutant la taille de trame au codec dans l’instruction allow.

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

Exemple :

```
allow=ulaw:30
```

Le nombre après les deux‑points est l’intervalle de packetisation en millisecondes — la quantité de voix transportée dans chaque paquet RTP. Une valeur plus grande amortit le surcoût fixe de l’en‑tête sur plus d’audio (moins de bande passante) au prix d’une latence accrue. Chaque codec possède sa propre taille de trame minimale, maximale et par défaut ; G.711 (`ulaw`/`alaw`), par exemple, utilise par défaut 20 ms.

## Summary

Dans ce chapitre, vous avez appris qu’Asterisk traite la VoIP à l’aide de canaux. Il prend en charge SIP (via `chan_pjsip` dans Asterisk 22) et IAX2 ; H.323 n’est disponible que via le module communautaire `ooh323`, et les anciens canaux MGCP et SCCP (Skinny) ne font plus partie d’une compilation standard d’Asterisk 22. Vous avez comparé et appris comment choisir un protocole de signalisation et un codec pour les canaux VoIP. L’IAX2 est plus efficace en bande passante et peut traverser facilement le NAT. SIP/PJSIP est le protocole le plus supporté par les fournisseurs de téléphones et de passerelles tiers et est le seul pilote de canal SIP dans Asterisk 22. Le protocole H.323 est le plus ancien et doit être utilisé pour se connecter à des infrastructures VoIP héritées. Dans la section Ingénierie du trafic, nous avons appris comment concevoir et dimensionner un réseau VoIP.

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
