# Canaux hérités : analogique, TDM & IAX2

Dans un monde purement VoIP en 2026, les types de canaux présentés dans ce chapitre sont de plus en plus rares : la plupart des nouveaux déploiements utilisent des trunks SIP et des endpoints PJSIP sur Ethernet, sans aucun matériel de téléphonie. Asterisk 22 prend néanmoins toujours en charge la plupart d'entre eux. La connectivité analogique (FXO/FXS) et numérique TDM (E1/T1/ISDN PRI/BRI) est fournie via DAHDI — la pile de pilotes développée à l'origine par Digium, acquise par Sangoma en 2018, après que les anciens pilotes Zaptel aient été renommés suite à un litige sur la marque. La connectivité serveur à serveur via IAX2 est fournie par `chan_iax2`, qui est toujours livré et pris en charge, mais qui est désormais fermement considéré comme un protocole hérité. Ce chapitre rassemble également le matériel sur le **SIP hérité** : l'ancien pilote `chan_sip` et sa configuration `sip.conf` — supprimés dans Asterisk 21 et absents dans Asterisk 22 — ainsi qu'un guide complet pour migrer un système `sip.conf` existant vers PJSIP. Si vous gérez une infrastructure purement SIP sur PJSIP sans cartes de téléphonie, sans trunks IAX2 et sans `sip.conf` hérité à convertir, vous pouvez ignorer ce chapitre en toute sécurité.

## Canaux analogiques (FXO/FXS)

Depuis Asterisk 22, DAHDI et les cartes de téléphonie analogique restent entièrement pris en charge, et DAHDI se compile toujours avec les noyaux actuels. La majorité des nouveaux déploiements sont néanmoins purement VoIP (trunks SIP, PJSIP), le matériel analogique/TDM est donc désormais un choix de niche — principalement présent dans les environnements hérités, la connectivité PSTN rurale ou les marchés réglementés. Tout ce qui suit s'applique toujours à ces scénarios.

Il existe plusieurs façons de se connecter au réseau téléphonique public commuté (PSTN). La meilleure méthode dépend de la manière dont la compagnie de téléphone rend cette connexion disponible dans votre région. Le moyen le plus simple est d'utiliser une ligne analogique, similaire à celle que vous utilisez à la maison. Dans cette section, nous vous montrerons comment configurer les cartes analogiques de Sangoma™ (anciennement Digium™) et Xorcom™.

### Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Reconnaître les principaux termes et acronymes de la téléphonie ;
- Comprendre quand utiliser des circuits numériques et analogiques ;
- Reconnaître la différence entre FXS et FXO ; et
- Configurer Asterisk pour FXS et FXO.

### Bases de la téléphonie

La plupart des implémentations analogiques utilisent une paire de lignes en cuivre appelées tip et ring. Lorsqu'une boucle est fermée, le téléphone reçoit la tonalité de l'autocommutateur (ou du PBX privé). La signalisation la plus fréquemment utilisée est le loop-start ; d'autres types de signalisation moins courants incluent le ground start, utilisé dans plusieurs pays. Les trois catégories de signalisation sont :

- Signalisation de supervision
- Signalisation d'adresse
- Signalisation d'information

#### Signalisation de supervision

Les principales signalisations de supervision sont le décroché (on-hook), le raccroché (off-hook) et la sonnerie. On-Hook – Lorsqu'un utilisateur pose le combiné, le PBX interrompt et ne permet pas au courant électrique de passer. Dans cet état, le circuit est dit on-hook. Dans cette position, seule la sonnerie est active. Off-Hook – Avant de commencer un appel téléphonique, le téléphone doit passer à l'état off-hook. Retirer le combiné du crochet ferme la boucle et indique au PBX que l'utilisateur a l'intention de passer un appel. Dès réception de cette indication, le PBX génère une tonalité, indiquant à l'utilisateur qu'il est prêt à accepter l'adresse de destination (c'est-à-dire le numéro de téléphone). Sonnerie – Lorsqu'un utilisateur appelle un autre téléphone, il génère une tension vers la sonnerie qui avertit l'autre utilisateur qu'un appel est reçu. La signalisation varie selon les pays, avec des tonalités différentes. Vous pouvez personnaliser les tonalités d'Asterisk pour votre pays en modifiant le fichier indications.conf. Par exemple :

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Signalisation d'adresse

Vous pouvez utiliser deux types de signalisation pour la numérotation. La première et la plus courante est la double tonalité multifréquence (dtmf), tandis que l'autre est la numérotation par impulsions (utilisée dans les anciens téléphones à cadran). Les téléphones ont un clavier pour la numérotation, et chaque bouton est associé à deux fréquences : une haute et une basse. Dans le cas de la signalisation dtmf, la combinaison de ces tonalités indique quel chiffre est pressé. MFC/R2 utilise une tonalité multifréquence différente du dtmf.

#### Signalisation d'information

La signalisation d'information montre la progression de l'appel et différents événements.

- Tonalité
- Tonalité d'occupation
- Retour de sonnerie
- Congestion
- Numéro invalide
- Tonalité de confirmation

### Interfaces PSTN

Comme dans le cas des anciens PBX, il est souvent nécessaire de connecter le PBX Asterisk au PSTN. Ici, nous vous montrerons comment le faire. Habituellement, vous avez trois options pour les lignes téléphoniques.

- Analogique : La forme la plus courante pour les particuliers et les petites entreprises, généralement fournie avec une paire métallique de lignes en cuivre.
- Numérique : Utilisée lorsque de nombreuses lignes sont nécessaires. Une ligne numérique est généralement fournie par un CSU/DSU ou un multiplexeur fibre. Le connecteur de l'utilisateur final est généralement un RJ45. Dans certains pays, les lignes E1 sont fournies en utilisant deux connecteurs coaxiaux BNC ; dans ce cas, vous aurez besoin d'un balun pour connecter la prise RJ45 à la carte de téléphonie.
- SIP : Cette option a été développée récemment. La ligne téléphonique est fournie via une connexion de données avec signalisation SIP (VoIP). C'est une bonne option à utiliser avec Asterisk car vous n'aurez pas besoin d'acheter une carte de téléphonie. Les appels téléphoniques seront livrés directement au port Ethernet. Un autre avantage est que vous pourriez être en mesure de libérer des ressources de votre CPU en évitant le transcodage de codec.

### Interfaces analogiques FXS, FXO et E&M

Plusieurs types d'interfaces analogiques sont disponibles. Il est fondamental de comprendre les différences entre ces interfaces pour apprendre à se connecter au réseau téléphonique ainsi qu'à d'autres PBX. Ici, nous vous montrerons l'interface E&M. Bien qu'elle ne soit pas actuellement disponible pour Asterisk et qu'elle ait été abandonnée par plusieurs fournisseurs, vous pouvez trouver des routeurs et des PBX avec ce type d'interface, il est donc préférable de savoir à quoi vous avez affaire.

#### Interfaces Foreign eXchange (FX)

Les interfaces FX sont analogiques. Le terme « Foreign eXchange » est appliqué aux trunks d'accès vers un central téléphonique (CO) PSTN. Foreign eXchange Office (FXO)

![Asterisk entre un téléphone analogique (FXS) et la ligne télécom (FXO) : le côté FXS fournit la tonalité et la sonnerie au téléphone, tandis que le côté FXO tire la tonalité du central.](../images/10-legacy-fig01.png)

L'interface FXO est utilisée pour se connecter à un central (CO) ou à l'extension d'un autre PBX. Elle communique directement avec une ligne téléphonique provenant du PSTN. Une autre option consiste à connecter l'interface FXO à un PBX existant, permettant la communication entre Asterisk et le PBX hérité. Connecter Asterisk à un port PBX et fournir une extension distante via VoIP est souvent appelé extension déportée (OPX). Une interface FXO reçoit une tonalité. Foreign eXchange Station (FXS) L'interface FXS alimente un téléphone analogique, un modem ou un fax. Le FXS fournit la tonalité et l'alimentation pour un téléphone.

#### Signalisation de trunk

- Loop-Start
- Ground-Start
- Kewlstart

L'utilisation de la signalisation kewlstart dans Asterisk est presque par défaut. Kewlstart n'est pas une signalisation en soi, mais ajoute de l'intelligence au circuit en surveillant ce qui se passe de l'autre côté. Kewlstart est basé sur le loop-start. La plupart des commutateurs ne prennent pas en charge cette fonctionnalité, qui est utilisée pour obtenir la notification de raccrochage.

- Loopstart : Utilisé dans la plupart des lignes analogiques, il permet au téléphone d'indiquer « on-hook » et « off-hook » et au commutateur d'indiquer « sonnerie » et « pas de sonnerie ». C'est probablement ce que la plupart des gens ont à la maison. Le nom vient du fait que la ligne est toujours ouverte. Lorsque vous fermez la boucle, le commutateur vous fournit une tonalité. Un appel entrant est signalé par une tension de sonnerie de 100V sur la paire ouverte.

![Asterisk fonctionnant comme une passerelle VoIP : un port FXO se connecte à une extension de PBX hérité tandis qu'un Asterisk distant livre cette ligne à un téléphone analogique sur IP via un port FXS (une extension déportée, ou OPX).](../images/10-legacy-fig02.png)

- Groundstart : Similaire au Loopstart. Lorsque vous voulez passer un appel, un côté de la ligne est court-circuité. Lorsque le commutateur identifie cet état, il inverse la tension à travers la paire ouverte, puis la boucle est fermée. Par conséquent, la ligne devient d'abord occupée avant d'être offerte à l'appelant.
- Kewlstart : Ajoute de l'intelligence aux circuits, permettant la surveillance de l'autre côté. Kewlstart intègre de nombreux avantages du loop-start.

### Configuration des canaux de téléphonie Asterisk

Pour configurer une carte d'interface de téléphonie, plusieurs étapes sont nécessaires. Dans ce chapitre, nous montrerons trois des scénarios les plus courants :

- Connexion analogique utilisant FXS
- Connexion analogique utilisant FXO
- Connexion d'un Astribank™ avec des interfaces FXS et FXO

### Procédure de configuration (valable dans les deux cas)

Avant de choisir le matériel pour Asterisk, vous devez tenir compte du nombre d'appels simultanés, des services et des codecs qui seront installés et activés. Asterisk est une application gourmande en CPU, c'est pourquoi nous recommandons une machine dédiée pour Asterisk. Le nombre de cartes d'interface installées dans l'ordinateur est limité par le nombre d'emplacements et d'interruptions disponibles. Il est préférable d'installer une seule carte avec huit interfaces vocales que deux cartes avec quatre. Une autre option consiste à utiliser une banque de canaux USB, telle que le Xorcom Astribank. Récemment, certains fabricants (par exemple, CIANET) ont commencé à produire des banques de canaux TDMoE, facilitant encore plus la connexion de dizaines d'interfaces analogiques.

![Un Xorcom Astribank : une banque de canaux USB rackable 19 pouces qui expose des dizaines de ports FXS/FXO (ici une unité de 32 ports) sans consommer d'emplacements PCI dans l'hôte.](../images/10-legacy-fig03.png)

#### Exemple 1 : Installation d'un FXO, un FXS

Dans cet exemple, nous utiliserons une carte d'interface de téléphonie Sangoma TDM400 (anciennement vendue sous le nom Digium TDM400) avec un module FXS et un module FXO. Les étapes requises sont listées ci-dessous :

1. Installez la carte analogique FXS, FXO, ou les deux.
2. Configurez le fichier `/etc/dahdi/system.conf` (anciennement `/etc/zaptel.conf`).
3. Générez les fichiers de configuration en utilisant `dahdi_genconf`.
4. Chargez le pilote pour l'interface DAHDI.
5. Exécutez `dahdi_test` pour vérifier les pertes d'interruptions.
6. Exécutez `dahdi_cfg` pour configurer le pilote.
7. Configurez le canal DAHDI dans le fichier `chan_dahdi.conf`, puis chargez Asterisk.

##### Étape 1 : Installer la carte TDM400

La carte TDM404P contient des modules FXS et FXO. Connectez les modules FXS (S110M, vert) et FXO (X100M, rouge). Si vous utilisez des modules FXS, connectez la carte directement à la source d'alimentation à l'aide d'un connecteur molex. Veuillez porter une protection électrostatique avant de manipuler les cartes d'interface pour éviter d'endommager le matériel. Les cartes analogiques Sangoma (anciennement Digium) prennent également en charge un module d'annulation d'écho matériel VPMADT032.

##### Étape 2 : Générer la configuration avec dahdi_genconf

La bonne nouvelle concernant la configuration est le nouvel utilitaire `dahdi_genconf`, qui détecte et génère automatiquement la configuration pour les interfaces DAHDI. L'utilitaire génère deux fichiers :

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (avec l'option `users`)
- Tous ces fichiers utilisent l'option `chan_dahdi full`

Avant de pouvoir exécuter `dahdi_genconf`, il est important de configurer le fichier `genconf_parameters` (souvent appelé `gen_parameters.conf`) :

![Une carte analogique Sangoma/Digium TDM404P : jusqu'à quatre modules FXS ou FXO se branchent dans les ports numérotés, avec une carte fille d'annulation d'écho matérielle optionnelle et un connecteur d'alimentation 12 V dédié pour les modules FXS.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

Le fichier `genconf_parameters` vous permet de personnaliser votre configuration. Les paramètres les plus importants pour les lignes analogiques sont :

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Avertissement : Il est nécessaire que vous configuriez au moins l'algorithme d'annulation d'écho pour les canaux. Le paramètre base_exten définit le dialplan de base pour les extensions FXS. Dans ce cas, le premier canal FXS recevra le numéro d'extension 4000, le second 4001, et ainsi de suite. Le contexte dans lequel les lignes (context_phones) et les trunks (context_lines) sont créés est très important. Après avoir généré les fichiers, vous devez inclure le fichier `/etc/asterisk/dahdi-channels.conf` dans le fichier `/etc/asterisk/chan_dahdi.conf` :

```
#include dahdi-channels.conf
```

Note : La signalisation analogique est un peu déroutante ; c'est toujours l'inverse de la carte. Les cartes FXS sont signalées avec FXO tandis que les cartes FXO sont signalées avec FXS. Asterisk communique avec ces appareils comme s'il était du côté opposé.

##### Étape 3 : Charger les pilotes du noyau

Maintenant, vous devez charger le module chan_dahdi et le pilote du noyau de la carte associée. Utilisez dahdi_hardware pour détecter votre carte et le nom du pilote. Par exemple :

- Pilote de carte Description
- TE410P wct4xxp 4xE1/T1-3.3V PCI
- TE405P wct4xxp 4xE1/T1-5V PCI
- TDM400P wctdm 4 FXS/FXO
- T100P wct1xxp 1 T1 E100P wctlxxp 1 E1 X100P wcfxo 1 FXO

Commandes pour charger les pilotes :

```
modprobe dahdi
modprobe wctdm
```

##### Étape 4 : Utiliser l'utilitaire dahdi_test

Un utilitaire important est dahdi_test, qui est utilisé pour vérifier les pertes d'interruptions dans la carte DAHDI. Les problèmes de qualité audio sont souvent liés à des conflits d'interruptions. Pour vérifier que votre carte DAHDI ne partage pas une interruption avec d'autres cartes, utilisez la commande suivante :

```
#cat /proc/interrupts
```

Vous pouvez vérifier le nombre de pertes d'interruptions en utilisant l'utilitaire dahdi_test compilé avec les cartes DAHDI. Un nombre inférieur à 99,987 % indique des problèmes possibles.

##### Étape 5 : Utiliser l'utilitaire dahdi_cfg pour configurer le pilote

DAHDI a un système inhabituel pour charger les pilotes. Configurez d'abord /etc/dahdi/system.conf, puis appliquez ces configurations au pilote DAHDI en utilisant dahdi_cfg. Dans ce cas, dahdi_cfg est utilisé pour configurer la signalisation pour les interfaces FX. Pour voir les résultats, vous pouvez ajouter « -vvvvv » à la commande pour le mode verbeux.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

Si les canaux ont été chargés avec succès, vous verrez une sortie similaire à celle montrée ci-dessus. Les utilisateurs configurent souvent incorrectement chan_dahdi.conf avec une signalisation inversée entre les canaux. Si cela se produit, vous verrez un message comme celui montré ci-dessous :

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

Après avoir configuré avec succès le matériel, vous pouvez procéder à la configuration d'Asterisk.

##### Étape 6 : Configurer le fichier /etc/asterisk/chan_dahdi.conf

Cela semble étrange, mais après avoir configuré /etc/dahdi/system.conf, vous avez configuré la carte elle-même. DAHDI peut être utilisé à d'autres fins, comme le routage et le SS7. Pour l'utiliser avec Asterisk, vous devez configurer les canaux DAHDI d'Asterisk. Chaque canal dans Asterisk doit être défini ; les canaux SIP/PJSIP sont définis dans pjsip.conf (note : chan_sip et sip.conf ont été supprimés dans Asterisk 21) tandis que les canaux TDM sont définis dans chan_dahdi.conf. Cela crée les canaux TDM logiques à utiliser dans votre dialplan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Options de configuration

Plusieurs options sont disponibles dans le fichier chan_dahdi.conf. Une description de toutes les options serait ennuyeuse et contre-productive ; au lieu de cela, nous nous concentrerons sur les principaux groupes d'options disponibles pour une compréhension facile.

#### Options générales (indépendantes du canal)

Ces options fonctionnent pour n'importe quel canal : context : Définit le contexte entrant.

```
context=default
```

channel : Définit le canal ou la plage de canaux. Chaque définition de canal héritera des options définies avant la déclaration. Les canaux peuvent être identifiés individuellement ou sur la même ligne par séparation par virgule. Les plages peuvent être définies en utilisant « - ».

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group : Permet aux canaux d'être gérés comme un groupe. Si vous composez un numéro de groupe au lieu d'un numéro de canal, le premier canal disponible est utilisé. Si les canaux sont des téléphones, lorsque vous appelez un groupe, tous les téléphones sonneront simultanément. Avec des virgules, vous pouvez spécifier plus d'un groupe pour le même canal.

```
group=1
group=3,5
```

language : Active l'internationalisation et configure une langue. Cette fonctionnalité configurera les messages système pour une langue spécifique. L'anglais est la seule langue avec des invites complètes disponibles via l'installation standard. musiconhold : Sélectionne la classe de musique d'attente.

#### Options d'identification de l'appelant (Caller ID)

Il existe de nombreuses options callerid. Certaines peuvent être désactivées, bien que la plupart soient activées par défaut. usecallerid : Active ou désactive la transmission du callerid pour les canaux suivants (Yes/No). Note : Si votre système reçoit deux sonneries avant de répondre, essayez de désactiver cette fonctionnalité. Il devrait répondre immédiatement. hidecallerid : Définit s'il faut masquer ou non le callerid sortant (Yes/No). callerid : Configure une chaîne callerid pour un canal spécifique. L'appelant peut être configuré avec asreceived. Ceci est principalement utilisé dans les interfaces de trunk pour indiquer le callerid entrant.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid : Prend en charge le callerid pendant l'appel en attente. useincomingcalleridondahditransfer : Utilise le callerid entrant dans un transfert.

#### Appel en attente

Asterisk prend en charge l'appel en attente dans les canaux FXS. L'utilisateur recevra une tonalité d'attente si quelqu'un essaie l'extension. Pour activer l'appel en attente :

```
callwaiting=yes
```

Pour prendre en charge le callerid dans l'appel en attente :

```
callwaitingcallerid=yes
```

#### Options de qualité audio

L'ajustement de l'annulation d'écho est à moitié technique, à moitié artistique. Ces options ajustent certains paramètres d'Asterisk qui affectent la qualité audio dans les canaux DAHDI. Elles peuvent aider à améliorer la qualité audio dans les interfaces analogiques.

#### L'utilitaire fxotune

Le fxotune est un utilitaire utilisé pour affiner certains paramètres pour les modules FXO. Cet affinage est nécessaire pour ajuster le déséquilibre d'impédance causé par l'hybride. L'utilitaire a trois modes de fonctionnement :

- Détection (-i) : détecte et corrige les canaux FXO existants et enregistre la configuration dans

```
fxotune.conf
```

- Mode Dump (-d) : génère les fichiers de forme d'onde vers fxotune_dump.vals
- Mode Startup (-s) : lit le fichier fxotune.conf et l'applique aux modules FXO

Il est important de comprendre que vous devrez insérer l'instruction fxotune –s dans le chargement du système avant de démarrer Asterisk :

```
#modprobe dahdi
#modprobe wctdm
#fxotune-s
```

### Annulation d'écho

La plupart des algorithmes d'annulation d'écho fonctionnent en générant plusieurs copies du signal reçu, dans lesquelles chacune est retardée d'une quantité de temps spécifique. Le nombre de taps du filtre détermine la taille du retard d'écho qui doit être annulé. Ces copies retardées sont ensuite ajustées et soustraites du signal reçu. L'astuce consiste à ajuster uniquement le signal retardé pour supprimer l'écho sans utiliser trop de cycles CPU. Du point de vue des utilisateurs, il est important de choisir un algorithme d'annulation d'écho approprié. La valeur par défaut est MG2 ; cependant, deux autres options sont disponibles : le High Performance Echo Cancellation (HPEC) de Sangoma (anciennement Digium) et l'annulation d'écho open-source (OSLEC) développée par David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) a été fusionné dans le noyau Linux — il réside dans la zone `drivers/staging/echo` du noyau — et DAHDI est construit avec lui plutôt que de fournir un téléchargement séparé. Pour changer l'algorithme d'annulation d'écho, définissez le paramètre `echo_can` dans `/etc/dahdi/system.conf`. Par exemple :

```
echo_can=oslec
```

L'annulation d'écho dans Asterisk est contrôlée par trois paramètres dans le fichier /etc/asterisk/chan-

```
dahdi.conf.
```

echocancel : Désactive ou active l'annulation d'écho. Vous devriez garder cette fonctionnalité activée. Elle accepte « yes » ou le nombre de taps. Explication : Comment fonctionne l'annulation d'écho ? La plupart des algorithmes d'annulation d'écho fonctionnent en générant plusieurs copies d'un signal reçu, chacune étant retardée d'un petit intervalle. Ce petit flux est appelé « tap ». Le nombre de taps détermine le retard d'écho qui peut être annulé. Ces copies sont retardées, ajustées et soustraites du signal original. L'astuce consiste à ajuster le signal retardé exactement à ce qui est nécessaire pour supprimer l'écho. echocancelwhenbridged : Active ou désactive l'annulateur d'écho pendant un appel TDM pur. Ce n'est généralement pas nécessaire. rxgain : Ajuste le gain de réception audio pour augmenter ou diminuer le volume de réception (-100 % à 100 %). txgain : Ajuste le gain de transmission audio pour augmenter ou diminuer le volume de transmission (- 100 % à 100 %). Par exemple :

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Options de facturation

Ces options modifient la façon dont les informations d'appel sont enregistrées dans la base de données des enregistrements de détails d'appel (CDR). amaflags : Configure les drapeaux AMA affectant la catégorisation CDR. Il accepte les valeurs suivantes :

- billing
- documentation
- omit
- default

accountcode : Configure un code de compte pour un canal spécifique. Il peut contenir n'importe quelle valeur alphanumérique — généralement le département ou le nom d'utilisateur.

```
accountcode=finance
amaflags=billing
```

### Options de progression d'appel

Ces éléments sont utilisés pour acquérir des informations sur la progression de l'appel. Dans les interfaces publiques, il peut être utile de détecter la progression de l'appel et de déterminer s'il a été répondu ou s'il est occupé. La détection d'occupation est hautement expérimentale et réglementée par des paramètres spécifiques.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Ces paramètres (ci-dessus) spécifient si l'interface tentera de détecter la tonalité d'occupation, combien de tonalités seront utilisées pour une détection réussie, et quel est le motif d'occupation. La détection d'occupation est largement expérimentale, et certains paramètres supplémentaires peuvent être modifiés dans le Makefile. Pour détecter la réponse d'un appel, ce qui est essentiel pour une facturation précise, il est possible d'utiliser l'inversion de polarité pour signaler l'heure exacte de la réponse. Ceci est important si vous prévoyez de facturer l'appel ou si vous souhaitez simplement avoir une facturation précise pour comparaison. Habituellement, vous devez contacter la compagnie de téléphone pour demander ce service.

```
answeronpolarityswitch=yes
```

Dans certains pays, il est possible de détecter le raccrochage de l'appel en utilisant également l'inversion de polarité.

```
hanguponpolarityswitch=yes
```

#### Options pour les téléphones

Ces options sont utilisées pour les téléphones connectés aux interfaces FXS. Toutes les fonctionnalités fournies aux téléphones analogiques connectés directement aux interfaces DAHDI sont contrôlées par Asterisk. Adsi (Analog Display Services Interface) : Il s'agit d'un ensemble de normes télécoms utilisées par certaines sociétés de télécoms pour offrir des services tels que l'achat de billets. cancallforward : Active ou désactive le transfert d'appel (*72 pour activer et *73 pour désactiver). calleridcallwaiting : Active le callerid reçu pendant une indication d'appel en attente (Yes/No). immediate : En mode immédiat, au lieu de fournir une tonalité, le canal saute immédiatement à l'extension « s » dans le contexte défini. Ceci est utilisé pour créer des lignes directes. threewaycalling : Active ou désactive la conférence à trois. mailbox : Avertit l'utilisateur des messages vocaux disponibles. Il peut s'agir d'un signe sonore ou d'un indicateur visuel (si le téléphone prend en charge cette fonctionnalité). L'argument est le numéro de la boîte vocale. callgroup : Groupe les téléphones pour composer ou pour décrocher. pickupgroup : Groupe de téléphones pour la prise d'appel.

### Commandes CLI DAHDI utiles

Une fois qu'Asterisk est en cours d'exécution avec les canaux DAHDI chargés, vous pouvez inspecter l'état du canal depuis l'interface CLI d'Asterisk. Ces commandes restent actuelles dans Asterisk 22 :

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### Format de canal DAHDI

Les canaux DAHDI utilisent le format suivant dans le dialplan :

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

Par exemple :

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
```

## Canaux numériques (E1/T1/PRI / TDM)

Depuis Asterisk 22, DAHDI et libpri restent entièrement pris en charge, mais les trunks numériques TDM (E1/T1/ISDN PRI) sont de plus en plus remplacés par des trunks SIP dans les nouveaux déploiements. Cette section reste entièrement applicable là où la connectivité TDM est requise ; dans les environnements vierges, le trunking SIP (Chapitre 3) offre généralement la même densité de canaux sans matériel de téléphonie.

Les canaux numériques sont extrêmement courants, vous devrez donc apprendre à implémenter ces canaux si vous souhaitez vous concentrer sur les grands clients. Lorsque le nombre de canaux est élevé — généralement plus de 8 — il est assez courant d'utiliser des interfaces numériques telles que T1/E1/J1. T1 est très courant aux États-Unis, tandis que E1 est courant en Europe et J1 au Japon. Ces types de canaux permettent une bonne densité de circuits — 24 par canal T1 et 30 pour les canaux E1. En Amérique latine, en Chine et en Afrique, il est courant d'utiliser un type de signalisation associée au canal (CAS) connu sous le nom de MFC/R2. Ce chapitre examinera comment implémenter MFC/R2 en utilisant la bibliothèque OpenR2. Aux États-Unis et en Europe, l'Integrated Services Digital Networks (ISDN) PRI est la signalisation la plus courante. Le chapitre discutera également de l'ISDN Basic Rate Interface (BRI), qui est très courant en Europe dans les applications de milieu de gamme. Tous les exemples du livre se concentrent sur les canaux DAHDI. Certaines cartes sont implémentées en utilisant des canaux propriétaires, veuillez donc vérifier auprès de votre fabricant pour plus de détails sur la façon de configurer votre carte spécifique.

### Objectifs

À la fin de ce chapitre, vous serez capable de :

- Reconnaître les principaux termes utilisés dans la téléphonie numérique
- Différencier la signalisation CAS et CCS
- Différencier la signalisation R2 et ISDN
- Configurer des interfaces avec la signalisation ISDN
- Configurer des interfaces avec la signalisation R2

### Lignes numériques E1/T1

Les lignes numériques E1/T1 sont une option chaque fois que vous devez implémenter un grand nombre de canaux. Un seul circuit E1 est capable de 30 appels simultanés, et vous pouvez avoir des fonctionnalités telles que la sélection directe à l'arrivée (DID), l'identification de l'appelant (Caller ID) et une signalisation avancée. La ligne E1/T1 peut arriver dans votre entreprise de plusieurs manières en utilisant des paires torsadées, de la fibre et des micro-ondes, selon votre pays. Les lignes numériques sont livrées à votre entreprise en utilisant UTP, fibre ou micro-ondes. Des modems et des multiplexeurs (MUX) sont utilisés pour livrer la ligne physique. La connexion à une ligne T1 est toujours basée sur un connecteur RJ45. Cependant, les lignes E1 peuvent également être provisionnées en utilisant BNC. Il est très important de connaître à l'avance le type de connecteur que vous allez recevoir, principalement dans les lignes E1. Habituellement, tout l'équipement jusqu'au RJ45 est fourni par le TELCO.

![Comment les circuits E1/T1 sont provisionnés : le telco peut livrer le trunk sur cuivre UTP (modem HDSL pour E1, ou une connexion directe par carte pour T1), sur fibre optique via un multiplexeur optique, ou sur une liaison radio micro-ondes.](../images/10-legacy-fig05.png)

![UTP ou BNC ? La plupart des cartes numériques utilisent des connecteurs RJ45 (UTP), mais certaines lignes E1 sont livrées sur coax BNC double, auquel cas un balun est nécessaire pour adapter la paire coaxiale à la prise RJ45 de la carte.](../images/10-legacy-fig06.png)

#### Comment la voix est-elle convertie en bits ?

Le signal analogique est échantillonné 8 000 fois par seconde pour créer une version numérique de la voix analogique. Ce codage est connu sous le nom de modulation par impulsions codées (PCM). Aux États-Unis et au Japon, le signal est codé en utilisant la loi mu (dans Asterisk, appelée ulaw). Dans le reste du monde, le codage est alaw.

![Modulation par impulsions codées (PCM) : le signal vocal analogique de 4 kHz est échantillonné 8 000 fois par seconde (Nyquist) et codé en un flux numérique de 64 Kbps.](../images/10-legacy-fig07.png)

#### Multiplexage par répartition dans le temps

Les lignes analogiques ont du sens lorsque vous n'avez besoin que de quelques canaux. Lors de l'utilisation du multiplexage par répartition dans le temps (TDM), il est possible de regrouper plusieurs canaux dans une seule connexion de données. Lorsque vous voulez un grand nombre de circuits, la compagnie de téléphone vous fournira généralement un trunk numérique, qui est un circuit de données dans lequel la voix est transportée dans un format numérique utilisant PCM. Chaque intervalle de temps utilise 64 Kbps de bande passante pour transporter un seul canal vocal.

![Multiplexage par répartition dans le temps en E1 et T1 : une trame E1 transporte 32 intervalles de temps à 2048 Kbps (DS0 #0 pour la synchronisation de trame, DS0 #16 pour la signalisation), tandis qu'une trame T1 transporte 24 intervalles de temps à 1544 Kbps en utilisant un bit pour la synchronisation et un schéma de bits volés pour la signalisation.](../images/10-legacy-fig08.png)

Aux États-Unis, le trunk numérique le plus courant est T1, qui dispose de 24 lignes disponibles ; en Europe et en Amérique latine, les trunks E1 ont 30 lignes. Certaines entreprises fournissent un T1/E1 fractionnaire avec moins de canaux. Signalisation par bits volés Parfois, un trunk T1 utilise un schéma de bits volés où un bit est emprunté pour la signalisation. Sur les trunks T1, le canal de données/voix est transmis avec 56 Kbps sur chaque intervalle de temps. Comme vous pouvez l'observer, lorsque vous utilisez le bit volé, le circuit T1 ne perd pas deux intervalles pour la synchronisation et la signalisation.

#### Code de ligne T1/E1

Les T1 et E1 sont en fait des circuits de données et ont un codage de données qui détermine la manière dont les bits sont interprétés. Pour les E1, le code de ligne le plus courant est HDB3 pour la couche 1 et CCS pour la couche 2. Le moyen le plus simple de savoir comment votre trunk numérique est configuré est de demander au TELCO ces informations. Vous aurez besoin de ces informations pour configurer le fichier /etc/dahdi/system.conf.

#### Signalisation T1/E1

Il est important de comprendre que les lignes T1/E1 peuvent être livrées en utilisant différents types de signalisation, tels que :

- T1 avec signalisation par bits volés
- T1 avec signalisation ISDN
- E1 avec MFC/R2 (CAS - Channel Associated Signaling)
- E1 avec signalisation ISDN

ISDN est souvent utilisé en Europe et aux États-Unis. C'est un réseau vocal numérique, standardisé par l'Union internationale des télécommunications (UIT) en 1984. ISDN fournit deux types de canaux :

- Canaux porteurs (Bearer channels) o Voix o Données
- Canaux de données o Signalisation hors bande o Signalisation LAPD o Q.931

Habituellement, une ligne ISDN est fournie en utilisant deux moyens physiques :

- Basic rate interface (BRI) o Connu sous le nom de 2B+D o Deux canaux porteurs (64K) et un canal de données (16K) o Utilise une paire de fils de cuivre avec 148Kbps.
- Primary rate interface (PRI) o Livré en utilisant un trunk T1/E1 o 23B+D pour les T1 o 30B+D pour les E1

Parfois, les circuits E1 utilisent un schéma de signalisation CAS appelé MFC/R2, qui a été défini par l'UIT comme une norme connue sous le nom de Q.421/Q441. On le trouve fréquemment en Amérique latine et en Asie. Plusieurs compagnies de téléphonie dans ces pays utilisent des variantes personnalisées de MFC/R2. Par conséquent, vous devrez connaître la variante de pays correcte pour que cela fonctionne.

### ISDN BRI

Les canaux utilisant la signalisation ISDN BRI sont très populaires en Europe. La plupart des cartes ISDN BRI pour Asterisk prennent en charge une interface S/T avec des capacités NT et TE. La connexion TE (terminal) est celle utilisée pour se connecter au TELCO ou à d'autres PBX configurés comme terminaison de réseau (NT). Le NT est utilisé pour connecter des téléphones et des PBX configurés comme TE. ISDN BRI fournit deux canaux de données/voix et un canal de signalisation. Les cartes ISDN BRI sont disponibles auprès de plusieurs fournisseurs de cartes d'interface pour Asterisk.

### Choisir une carte de téléphonie pour votre serveur Asterisk

Il existe plusieurs fabricants de cartes numériques compatibles avec Asterisk. Le choix d'une carte dépend de certains des facteurs suivants :

#### Bus de données

Il existe plusieurs types de bus sur votre PC. Il est très important que vous ayez la bonne carte pour votre serveur. L'aperçu suivant présente les cartes les plus fréquemment utilisées :

- 32 Bits PCI 5V présent dans la plupart des ordinateurs, y compris les ordinateurs de bureau o Sangoma (anciennement Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, et TC400 o Sangoma A101, A102, et A104
- 32/64 bits PCI 3.3V, essentiellement présent dans les serveurs o Sangoma (anciennement Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, et TC400
- PCI Express présent sur les ordinateurs de bureau et les serveurs o Sangoma (anciennement Digium) TE420, TE220, TE121, AEX2400, et AEX800 o Sangoma A101, A102, et A104

Ces familles de cartes proviennent de Digium, que Sangoma a acquis en 2018 ; elles sont désormais vendues et prises en charge sous la marque Sangoma. Beaucoup des anciennes références listées ici ont été abandonnées, veuillez donc confirmer la disponibilité du modèle actuel sur www.sangoma.com avant d'acheter.

- MiniPCI présent sur les systèmes embarqués o OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), et B400M(ISDN BRI)
- USB 2.0 présent dans la plupart des PC modernes. Les solutions basées sur USB permettent une grande densité de canaux analogiques et numériques. Ce bus prend en charge 480 Mbps, et chaque canal vocal occupe 64 Kbps. Lors de l'utilisation de hubs USB, il est possible d'obtenir des densités allant jusqu'à un millier de ports analogiques sur un seul port. o Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. Le plus grand avantage de l'Ethernet est de permettre à la carte d'être connectée par plus d'un serveur. Les solutions à haute disponibilité sont généralement l'application principale pour ces appareils. La force de cette solution est l'utilisation de serveurs sans emplacements PCI libres ou de serveurs lames. o Redfone FoneBridge (jusqu'à quatre circuits E1)

### Utilisation de l'annulation d'écho matérielle

L'annulation d'écho matérielle réduit la charge sur le CPU hôte. Pour les cartes avec plus d'une seule interface E1, l'annulation d'écho matérielle peut aider à soulager votre processeur. De nouveaux annulateurs d'écho logiciels améliorés tels que l'OSLEC réduisent le besoin d'un annulateur d'écho matériel. Pour choisir entre les annulateurs d'écho matériels et logiciels, vous devez tenir compte de la puissance de traitement disponible sur votre serveur et du nombre de circuits E1. Un processus d'annulation d'écho peut utiliser jusqu'à neuf MIPS (millions d'instructions par seconde) par canal vocal avec 128 taps d'amplitude en utilisant OSLEC (Référence : Xorcom Ltd.). Si vous considérez 1 cycle CPU par instruction (ce qui n'est pas toujours correct en fonction du processeur et de l'implémentation logicielle elle-même), nous parlons de 1,080 GHz pour quatre E1.

#### Type de signalisation

Sélectionner le type de signalisation (par exemple, T1 CAS, T1 PRI, E1 CAS R2, ou E1 CAS ISDN) n'est pas une tâche facile. Cela dépend vraiment de ce que vous avez de disponible dans votre région et à quel prix. La signalisation par canal commun (CCS) est souvent meilleure que la signalisation associée au canal (CAS). Cependant, elle n'est souvent pas disponible. Aux États-Unis, vous pouvez généralement choisir, car la plupart des TELCO proposent T1 CAS pour les utilisateurs réguliers et T1 PRI pour les utilisateurs avancés (par exemple, les centres d'appels). En Amérique latine, E1 CAS R2 est prédominant, mais ISDN PRI est disponible dans certaines villes.

![L'architecture logicielle DAHDI : Asterisk communique avec le pilote de canal `chan_dahdi`, qui à son tour charge les bibliothèques de protocole libpri (ISDN), libopenr2 (MFC/R2), et libss7 (SS7) ; celles-ci reposent sur l'interface `/dev/dahdi`, le pilote de noyau DAHDI, et le pilote de noyau d'interface spécifique à la carte.](../images/10-legacy-fig09.png)

L'implémentation de R2 est nécessaire pour installer une bibliothèque connue sous le nom d'OpenR2 (www.libopenr2.org), développée par Moises Silva, et pour patcher Asterisk avant l'installation — une procédure simple montrée plus loin dans ce chapitre. La bibliothèque a passé plusieurs tests et est en production chez plusieurs de nos clients. ISDN est, à mon avis, toujours le meilleur choix, s'il est disponible. Certains fournisseurs peuvent avoir accès à la signalisation système 7 (SS7), qui est une signalisation CCS disponible entre les compagnies de téléphone. Des solutions propriétaires et open source sont disponibles pour SS7. La bibliothèque libss7 est utilisée pour prendre en charge SS7 sur Asterisk.

### Configuration des canaux de téléphonie Asterisk

La configuration d'une carte d'interface de téléphonie implique plusieurs étapes nécessaires. Dans ce chapitre, nous montrerons trois des scénarios les plus courants :

- Connexion numérique utilisant ISDN PRI
- Connexion numérique utilisant ISDN BRI
- Connexion numérique utilisant MFC/R2

Il existe deux façons de configurer les canaux DAHDI. La première consiste à le configurer manuellement avec un contrôle total de tous les paramètres. La seconde consiste à utiliser l'utilitaire dahdi_genconf pour détecter et configurer les cartes.

#### Détection et configuration automatiques

Grâce à l'équipe de développement DAHDI, nous avons maintenant une détection et une configuration automatiques des cartes. Étape 1 : Pour générer la configuration automatiquement, utilisez l'utilitaire dahdi_genconf, qui détectera la carte et générera les fichiers /etc/dahdi/system.conf et dahdi-channels.conf.

```
dahdi_genconf
```

Étape 2 : Dans la dernière ligne du fichier chan_dahdi.conf, incluez le fichier dahdi-channels.conf

```
#include dahdi_channels.conf
```

Étape 3 : Commentez tous les modules inutilisés dans le fichier modules ou utilisez simplement :

```
dahdi_genconf modules
```

#### Configuration manuelle

Une autre option consiste à configurer les interfaces manuellement. Voici quelques exemples de configuration pour les canaux DAHDI.

##### Exemple #1 – Deux canaux T1/ E1 utilisant ISDN

Étapes requises :

1. Installation de TE205P ou TE210P
2. Configuration du fichier `/etc/dahdi/system.conf`
3. Chargement du pilote DAHDI
4. Utilitaire `dahdi_test`
5. Utilitaire `dahdi_cfg`
6. Configuration du fichier `chan_dahdi.conf`
7. Chargement et test d'Asterisk

Étape 1 : Installation de TE205P. Avant d'installer TE205P, il est important de comprendre les différences entre les cartes TE205P et TE210P. La carte TE210P utilise un bus 64 bits alimenté par 3,3 volts que l'on trouve presque uniquement sur les cartes mères de serveurs. Soyez prudent si vous spécifiez cette carte d'interface ; assurez-vous que votre matériel prend en charge un bus 64 bits, 3,3V. La carte TE205P utilise un PCI 5V, que l'on trouve souvent dans les ordinateurs de bureau. Nous avons choisi la carte d'interface TE205P avec deux spans pour cet exemple car il est plus facile de la réduire à une carte à un span ou de l'étendre à la carte à quatre spans. Ces cartes sont maintenant vendues sous la marque Sangoma (anciennement Digium).

![Une carte E1/T1 double span Sangoma/Digium TE205P : les deux ports RJ45 acceptent les trunks numériques, et un cavalier intégré (le sélecteur E1/T1/J1) définit la norme de ligne.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

La configuration des cartes numériques TDM est un peu différente de la configuration de leurs homologues analogiques. Tout d'abord, nous devrons configurer les spans de la carte, puis les canaux. Les spans sont numérotés séquentiellement en fonction de l'ordre de reconnaissance des cartes. En d'autres termes, si vous avez plus d'une carte d'interface, il est difficile de savoir quel span appartient à laquelle. Utilisez dahdi_hardware pour vérifier quel matériel est installé sur chaque span. Exemple #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

Exemple #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Exemple #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Étape 3 : Chargement des pilotes du noyau Vérifiez quel pilote vous devez installer en utilisant dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Pour charger, utilisez :

```
modprobe dahdi
modprobe wct2xxp
```

Étape 4 : En utilisant dahdi_test, vérifiez les interruptions manquantes Vous pouvez vérifier le nombre de pertes d'interruptions en utilisant l'utilitaire dahdi_test compilé avec les cartes DAHDI. Un nombre inférieur à 99,987 % indique des problèmes possibles. Vous trouverez dahdi_test dans

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Étape 5 : Utilisation de l'utilitaire dahdi_cfg C'est la sortie correcte de dahdi_cfg pour un span E1 fractionnaire (15 ports) et deux ports FXO.

```
#./dahdi_cfg –vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Étape 6 : Configuration de DAHDI dans le fichier /etc/asterisk/chan_dahdi.conf Exemple #1 (2xT1)

```
callerid=”John Doe”<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Exemple #2 (2xE1)

```
callerid=”Flavio Eduardo” <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Exemple #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Utilisez signaling=bri_cpe_ptmp pour BRI point à multipoint. Actuellement, BRI point à multipoint n'est pas pris en charge en mode NT.

#### Chargement des pilotes du noyau

Après avoir configuré les pilotes, vous pouvez simplement redémarrer le serveur. Si vous avez installé DAHDI avec make config, vous n'aurez rien d'autre à faire. Le pilote du noyau sera automatiquement chargé et configuré. Cependant, il est parfois utile de charger et décharger les pilotes manuellement. Exemple :

```
modprobe wct11xp
dahdi_cfg –vvvvv
```

La première commande charge le pilote et la seconde, dahdi_cfg, applique la configuration au pilote du noyau.

### Dépannage

Parfois, les choses ne fonctionnent pas du premier coup. Vérifions quelques ressources pour le dépannage de DAHDI. Étape 1 : Vérifiez si la carte est reconnue par le système d'exploitation. Les cartes Sangoma/Digium sont généralement reconnues comme le modem ISDN.

```
lspci –v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Étape 2 : Vérifiez si le pilote du noyau se charge correctement en utilisant :

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Étape 3 : Vérifiez l'état des alarmes liées à la couche physique de la connexion. Pour vérifier la couche physique de la connexion E1, vous pouvez utiliser la commande CLI Asterisk suivante.

```
dahdi show status
```

Les alarmes indiquent des problèmes avec le port : Alarme rouge : Impossible de maintenir la synchronisation avec le commutateur distant. Il s'agit généralement d'un problème physique, tel qu'un code de ligne ou une inadéquation de trame. Alarme jaune : Signale que le commutateur distant est en alarme rouge. Cela indique que le commutateur distant ne reçoit pas vos transmissions. Alarme bleue : Reçoit tous les 1 non tramés sur tous les intervalles de temps ; dahdi_tool ne détecte actuellement pas d'alarme bleue. Loopback : Le port est soit en loopback local, soit en loopback distant

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Étape 4 : Pour détecter les problèmes avec DAHDI sur le serveur Asterisk, vérifiez d'abord si les canaux sont reconnus en utilisant :

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Étape 5 : Vérifiez l'état de la couche ISDN 3, également connue sous le nom de q.931. Vous pouvez vérifier si la couche ISDN 3 est active en utilisant : `pri show spans` (pour lister tous les spans) ou `pri show span <n>` pour un span spécifique :

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Utilisez `pri show spans` (pluriel) pour lister l'état de tous les spans PRI configurés à la fois.

Vérifiez un canal spécifique. dahdi show channel x :

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1*CLI>
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x : Si après tout, vous avez toujours des problèmes, commencez à déboguer le span pri. Cette commande active un débogage détaillé des appels ISDN. C'est une commande importante lorsque vous pensez que quelque chose n'est pas correct. Vous pouvez détecter les chiffres mal composés et d'autres problèmes. Ci-dessous, nous présentons l'exemple d'une sortie de débogage pour un appel réussi. Référez-vous à cet exemple si vous devez comparer un appel infructueux à un appel sans problème. Une astuce consiste à utiliser core set verbose=0 pour ne recevoir que les messages ISDN q.931.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]fice*CLI>
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Options de configuration dans chan_dahdi.conf

Plusieurs options sont disponibles dans le fichier chan_dahdi.conf. Une description de toutes les options serait ennuyeuse et contre-productive. Ici, nous détaillerons les principaux groupes d'options disponibles pour fournir une meilleure compréhension.

#### Options générales (indépendantes du canal)

context : Définit le contexte entrant.

```
context=default
```

channel : Définit le canal ou la plage de canaux. Chaque définition de canal héritera des options définies avant la déclaration. Les canaux peuvent être identifiés individuellement ou sur la même ligne avec une séparation par virgule. Les plages peuvent être définies en utilisant « - ».

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group : Permet aux canaux d'être traités comme un groupe. Si vous composez un numéro de groupe au lieu d'un numéro de canal, le premier canal disponible est utilisé. Si les canaux sont des téléphones, lorsque vous appelez un groupe, tous les téléphones sonneront simultanément. En utilisant des virgules, vous pouvez spécifier plus d'un groupe pour le même canal.

```
group=1
group=3,5
```

language : Active l'internationalisation et configure une langue. Cette fonctionnalité configurera les messages système pour une langue spécifique. L'anglais est la seule langue avec des invites complètes disponibles à partir de l'installation standard. musiconhold : Sélectionne la classe de musique d'attente.

#### Options ISDN

switchtype : Dépend du PBX ou du commutateur utilisé. En Europe et en Amérique latine, EuroISDN est courant.

- 5ess : Lucent 5ESS
- euroisdn : EuroISDN
- national : National ISDN
- dms100 : Nortel DMS100
- 4ess : AT&T 4ESS
- Qsig : Q.SIG

```
switchtype = EuroISDN
```

pridialplan : Requis pour certains commutateurs qui ont besoin d'une spécification de plan de numérotation. Cette option est ignorée par de nombreux commutateurs. Les options valides sont private, national, international, et unknown.

```
pridialplan = unknown
```

prilocaldialplan : Nécessaire pour certains commutateurs, généralement unknown.

```
prilocaldialplan = unknown
```

overlapdial : La numérotation par chevauchement est utilisée lorsque vous passez des chiffres après que la connexion est établie. Vous pouvez utiliser le mode de numérotation par bloc (overlapdial=no) ou le mode chiffre (overlapdial=yes). Le mode bloc est souvent utilisé par les opérateurs. signaling : Configure le type de signalisation pour les canaux suivants. Ces paramètres doivent correspondre à ceux du fichier chan_dahdi.conf. Les choix corrects sont basés sur le canal disponible. Pour ISDN, vous pourriez choisir cinq options :

- pri_cpe : Utilisé lorsque l'appareil est un CPE, parfois appelé client, utilisateur ou esclave. C'est la forme de signalisation la plus simple et la plus utilisée. Parfois, lorsque vous essayez de vous connecter à un PBX privé, le PBX a généralement été configuré comme un CPE également. Dans ce cas, utilisez la signalisation pri_net dans Asterisk.
- pri_net : Utilisé lorsque Asterisk est connecté à un PBX privé configuré comme un CPE. La signalisation est souvent appelée hôte, maître ou réseau.
- bri_cpe : Utilisé lorsque Asterisk est connecté en tant que CPE à un trunk ISDN BRI
- bri_net : Utilisé lorsque Asterisk est connecté à un téléphone ISDN ou un PBX configuré comme un terminal (TE).
- bri_cpe_ptmp : Identique à bri_cpe, mais dans une architecture point à multipoint.

#### Options CallerID

De nombreuses options Caller ID sont disponibles. Certaines peuvent être désactivées, bien que la plupart soient activées par défaut. usecallerid : Active ou désactive la transmission du Caller ID pour les canaux suivants (Yes/No). Note : Si votre système nécessite deux sonneries avant de répondre, essayez de désactiver cette fonctionnalité afin qu'il réponde immédiatement. hidecallerid : Masque le Caller ID (Yes/No). calleridcallwaiting : Active la réception du Caller ID pendant une indication d'appel en attente (Yes/No). callerid : Configure une chaîne Caller ID pour un canal spécifique. L'appelant peut être configuré avec « asreceived » dans les interfaces de trunk pour transmettre le Caller ID.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note : La plupart des TELCO exigent que vous configuriez votre caller ID correct. Si vous ne transmettez pas le bon caller ID, vous ne devriez pas pouvoir composer en sortie via le TELCO. D'un autre côté, vous pourrez recevoir des appels même sans configurer le caller ID.

#### Options de qualité audio

Ces options ajustent certains paramètres d'Asterisk qui affectent la qualité audio dans les canaux DAHDI. echocancel : Désactive ou active l'annulation d'écho. Vous devriez garder cette fonctionnalité activée. Elle accepte « yes » ou le nombre de taps. Explication : Comment fonctionne l'annulation d'écho ? La plupart des algorithmes d'annulation d'écho fonctionnent en générant plusieurs copies d'un signal reçu, chacune étant retardée d'un petit intervalle. Ce petit flux est appelé « tap ». Le nombre de taps détermine le retard d'écho qui peut être annulé. Ces copies sont retardées, ajustées et soustraites du signal original. L'astuce consiste à ajuster le signal retardé exactement à ce qui est nécessaire pour supprimer l'écho. echocancelwhenbridged : Active ou désactive l'annulateur d'écho pendant un appel TDM pur. Ce n'est généralement pas requis. rxgain : Ajuste le gain de réception audio pour augmenter ou diminuer le volume de réception (-100 % à 100 %). txgain : Ajuste le gain de transmission audio pour augmenter ou diminuer le volume de transmission (- 100 % à 100 %). Exemple :

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Options de facturation

Ces options modifient la façon dont les informations d'appel sont enregistrées dans la base de données des enregistrements de détails d'appel (CDR). amaflags : Affecte la catégorisation CDR. Il accepte ces valeurs :

- billing
- documentation
- omit
- default

accountcode : Il configure un code de compte pour un canal spécifique. Il peut contenir n'importe quelle valeur alphanumérique, généralement le département ou le nom d'utilisateur.

```
accountcode=finance
amaflags=billing
```

### Configuration MFC/R2

MFC/R2 est utilisé dans plusieurs pays d'Amérique latine, en Chine et en Afrique ainsi que dans certains pays européens. ISDN est supérieur et préféré s'il est disponible dans votre région.

#### Comprendre le problème

La carte utilisée pour signaler MFC/R2 est la même que celle utilisée pour signaler ISDN. Il est possible d'utiliser MFC/R2 sur les canaux DAHDI en utilisant la bibliothèque appelée libopenR2 (www.libopenr2.com). Cette bibliothèque ne faisait pas partie des versions d'Asterisk antérieures à 1.6.2.

##### Comprendre le protocole MFC/R2

Le protocole MFC/R2 combine la signalisation intrabande et hors bande. La signalisation d'adresse est transmise intrabande en utilisant un ensemble de tonalités tandis que les informations de canal sont transmises sur l'intervalle de temps 16 en tant que signalisation hors bande.

**Signalisation de ligne (UIT-T Q.421).** Dans l'intervalle de temps 16, chaque canal vocal utilise quatre bits ABCD pour signaler ses états et le contrôle d'appel. Les bits C et D sont rarement utilisés. Dans certains pays, ils peuvent être utilisés pour la taxation (taxation par impulsions pour la facturation). Dans une conversation normale, nous avons les deux côtés qui travaillent : l'appelant et l'appelé. La signalisation du côté appelant est appelée signalisation avant tandis que le côté appelé utilise la signalisation arrière. Nous désignerons Af et Bf pour la signalisation avant et Ab et Bb pour la signalisation arrière.

| État | ABCD avant | ABCD arrière |
| --- | --- | --- |
| Inactif/Libéré | 1001 | 1001 |
| Saisi | 0001 | 1001 |
| Accusé de saisie | 0001 | 1101 |
| Répondu | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (avant clear-back) | 1001 | 0101 |
| ClearFwd (confirmation de déconnexion) | 1001 | 1001 |
| Bloqué | 1001 | 1101 |

MFC/R2 a été défini par l'UIT. Malheureusement, plusieurs pays ont personnalisé la norme selon leurs propres besoins. En conséquence, des variations sont apparues dans les normes entre les pays.

**Signaux inter-registres (UIT-T Q.441).** La signalisation MFC/R2 utilise une combinaison de deux tonalités. Les tableaux ci-dessous montrent la norme UIT.

Groupe de signaux I (avant) :

| Description | Signal avant |
| --- | --- |
| Chiffre 1 | I-1 |
| Chiffre 2 | I-2 |
| Chiffre 3 | I-3 |
| Chiffre 4 | I-4 |
| Chiffre 5 | I-5 |
| Chiffre 6 | I-6 |
| Chiffre 7 | I-7 |
| Chiffre 8 | I-8 |
| Chiffre 9 | I-9 |
| Chiffre 0 | I-10 |
| Indicateur de code pays, suppresseur d'écho moitié sortant requis | I-11 |
| Indicateur de code pays, aucun suppresseur d'écho requis | I-12 |
| Indicateur d'appel de test | I-13 |
| Indicateur de code pays, suppresseur d'écho moitié sortant inséré | I-14 |
| Non utilisé | I-15 |

Groupe de signaux II (avant) :

| Description | Signal avant |
| --- | --- |
| Abonné sans priorité | II-1 |
| Abonné avec priorité | II-2 |
| Équipement de maintenance | II-3 |
| Spare | II-4 |
| Opérateur | II-5 |
| Transmission de données | II-6 |
| Abonné ou opérateur sans installation de transfert avant | II-7 |
| Transmission de données | II-8 |
| Abonné avec priorité | II-9 |
| Opérateur avec installation de transfert avant | II-10 |
| Spare | II-11 |
| Spare | II-12 |
| Spare | II-13 |
| Spare | II-14 |
| Spare | II-15 |

Groupe de signaux A (arrière) :

| Description | Signal arrière |
| --- | --- |
| Envoyer le chiffre suivant (n+1) | A-1 |
| Envoyer l'avant-dernier chiffre (n-1) | A-2 |
| Adresse complète, passage à la réception des signaux du groupe B | A-3 |
| Congestion dans le réseau national | A-4 |
| Envoyer la catégorie de l'appelant | A-5 |
| Adresse complète, taxation, conditions de parole établies | A-6 |
| Envoyer l'antépénultième chiffre (n-2) | A-7 |
| Envoyer le chiffre (n-3) | A-8 |
| Spare | A-9 |
| Spare | A-10 |
| Envoyer l'indicateur de code pays | A-11 |
| Envoyer le chiffre de langue ou de discrimination | A-12 |
| Envoyer la nature du circuit | A-13 |
| Demander des informations sur l'utilisation du suppresseur d'écho | A-14 |
| Congestion dans un central international ou à sa sortie | A-15 |

Groupe de signaux B (arrière) :

| Description | Signal arrière |
| --- | --- |
| Spare | B-1 |
| Envoyer une tonalité d'information spéciale | B-2 |
| Ligne d'abonné occupée | B-3 |
| Congestion (après passage du groupe A au B) | B-4 |
| Numéro non alloué | B-5 |
| Ligne d'abonné libre, taxation | B-6 |
| Ligne d'abonné libre, pas de taxation | B-7 |
| Ligne d'abonné en dérangement | B-8 |
| Spare | B-9 |
| Spare | B-10 |
| Spare | B-11 |
| Spare | B-12 |
| Spare | B-13 |
| Spare | B-14 |
| Spare | B-15 |

#### Séquence MFC/R2

La séquence suivante illustre un appel provenant d'une extension Asterisk vers un terminal dans le PSTN. Le PSTN abandonne l'appel et met fin à la communication.

![Un flux d'appel MFC/R2 complet entre Asterisk et le telco : la signalisation de ligne (Inactif, Saisi, Accusé de saisie, Réponse, Clearback, Clear Forward) est échangée dans l'intervalle de temps 16, les chiffres composés et les signaux arrière "envoyer le chiffre suivant" (groupes I/A/B) voyagent intrabande, et les tonalités audibles atteignent l'abonné.](../images/10-legacy-fig11.png)

### Comment utiliser le pilote libopenr2

Le projet initié par Moises Silva a été inspiré par le pilote de canal Unicall écrit par Steve Underwood. La bibliothèque OpenR2 est actuellement la solution logicielle la plus stable pour Asterisk. Avec cette solution, nous pouvons utiliser n'importe quelle carte numérique compatible avec DAHDI. Auparavant, seules des solutions propriétaires étaient disponibles pour MFC/R2, l'une des meilleures que j'ai utilisées est celle mise à disposition par Khomp, www.khomp.com.br. Dans Asterisk 22, la prise en charge de MFC/R2 via libopenR2 est intégrée lorsque la bibliothèque est présente au moment de la compilation — aucun patch externe n'est requis. Les étapes ci-dessous montrent l'installation manuelle historique pour référence ; sur les systèmes modernes, installez `libopenr2-dev` depuis le gestionnaire de paquets de votre distribution avant d'exécuter `./configure`, puis activez `chan_dahdi` dans `make menuselect`.

Les étapes ci-dessous compilent openr2 et Asterisk à partir de leurs dépôts Git actuels. Elles sont conservées comme référence pour les sites qui compilent à partir de la source ; sur une distribution moderne, vous pouvez généralement les ignorer entièrement en installant le paquet `libopenr2-dev` et une version Asterisk 22 packagée, puisque `chan_dahdi` compile la prise en charge R2 directement avec libopenr2 sans patch externe.

Étape 1 : Installez les outils de construction dont vous avez besoin.

```
apt-get install git
```

Étape 2 : Clonez la bibliothèque openr2 et la source Asterisk. Aucun arbre patché spécial n'est nécessaire sur Asterisk 22 — un checkout standard compile la prise en charge R2 tant que libopenr2 est présent.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Étape 3 : Compilez et installez S'il vous plaît, SAUVEGARDEZ votre serveur avant de continuer.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note : N'exécutez pas « make samples » pour éviter d'écraser vos fichiers de configuration.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Supposons que vous ayez une carte avec une interface E1.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Étape 5 : Exécutez la commande dahdi_cfg pour appliquer les modifications au pilote :

```
dahdi_cfg –vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Étape 5 : Modifiez le fichier chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Étape 6 : Modifiez le dialplan dans le fichier extensions .conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Note : Certains TELCO n'acceptent pas les appels sans le caller ID. Veuillez définir le caller ID sur l'un des numéros DID attribués par l'opérateur. Dans certains pays, cette étape n'est pas requise. Étape 7 : Testez la solution : Maintenant, avec une extension dans le contexte from-internal, appelez n'importe quel numéro et observez la console. Vérifiez si des erreurs se produisent. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Débogage OpenR2

Pour détecter les erreurs dans les appels, vous pouvez activer le débogage. Pour ce faire, suivez les étapes ci-dessous. Étape 1 : Modifiez le fichier chan_dahdi.conf et ajoutez les trois lignes suivantes à la configuration :

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

Étape 2 : Redémarrez le serveur Asterisk Étape 3 : Testez l'appel et vérifiez les fichiers d'appel dans /var/log/asterisk/mfcr2/span1 Ci-dessous est une trace pour un appel normal. Comparez-la à ce que vous recevez dans votre appel.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### Configuration MFC/R2

Les options sont documentées dans le fichier chan_dahdi.conf. Certaines des options les plus importantes sont détaillées ici. Paramètres obligatoires : mfcr2_variant, mfcr2_max_ani et mfcr2_max_dnis. mfcr2_variant : Variante de pays.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani : Quantité maximale de chiffres ANI à demander mfcr2_max_dnis : Quantité maximale de chiffres DNIS à demander mfcr2_get_ani_first : Obtenir ou non l'ANI avant le DNIS (requis par certains TELCO) mfcr2_category : Catégorie de l'appelant. Vous pouvez définir la variable MFCR2_CATEGORY avant de démarrer l'appel mfcr2_logdir : Répertoire pour enregistrer les fichiers d'appel. (/var/log/asterisk/mfcr2/directory) mfcr2_call_files : Enregistrer ou non les appels

- mfcr2_logging : valeurs de journalisation
- cas – bits ABCD pour tx et rx
- mf – Tonalités multifréquences
- stack – sortie verbeuse de la pile de canal et de contexte
- all – toutes les activités
- nothing – ne rien enregistrer

mfcr2_mfback_timeout : Cette valeur mérite d'être mentionnée. Parfois, si vous appelez un téléphone portable ou tout appel qui prend beaucoup de temps à se terminer, ce paramètre peut expirer, il est donc souvent modifié pour un affinage. Si certains de vos appels ne sont pas terminés, c'est le paramètre que vous devez modifier en premier. mfcr2_metering_pulse_timeout : Les impulsions sont utilisées par certaines variantes R2 pour indiquer les coûts mfcr2_allow_collect_calls : Au Brésil, la tonalité II-8 est utilisée pour indiquer un appel en PCV ; ce paramètre vous permet de bloquer les appels en PCV. mfcr2_double_answer : Également utilisé pour éviter les appels en PCV lorsqu'une double réponse est requise. Avec double_answer=yes, vous bloquez réellement les appels en PCV. mfcr2_immediate_accept : Vous permet de sauter l'utilisation des signaux de groupe B/II et d'aller directement à l'état accepté. mfcr2_forced_release : Vous permet d'accélérer la libération de l'appel ; fonctionne pour la variante brésilienne.

#### ANI et DNIS

L'identification automatique du numéro (ANI) est le numéro de l'appelant. Le service d'identification du numéro composé (DNIS) est le numéro appelé ou, en d'autres termes, le numéro composé. Lorsqu'un appel est reçu, généralement les quatre derniers numéros sont transmis au PBX dans un processus appelé sélection directe à l'arrivée (DID). Le numéro ANI est en fait le Caller ID. L'ANI aura l'extension de l'appelant lors de la composition tandis que le DNIS contiendra la destination de l'appel. Il est important que ces paramètres soient configurés correctement. Certains commutateurs envoient juste les quatre derniers chiffres tandis que d'autres envoient le numéro complet.

### Format de canal DAHDI

Les canaux DAHDI utilisent le format suivant dans le dialplan :

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

Exemples :

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
[g] – Group identifier
[c] – Answer confirmation; A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

## Le protocole IAX2

Dans ce chapitre, nous apprendrons le protocole Inter-Asterisk eXchange (IAX), y compris ses forces et ses faiblesses. Des détails tels que le mode trunk et l'interconnexion de deux serveurs Asterisk seront également couverts. Toutes les références dans ce document correspondent à IAX version 2. Le protocole IAX fournit le transport multimédia et la signalisation pour la voix et la vidéo. IAX est très innovant ; il économise de la bande passante en mode trunk et est beaucoup plus simple que SIP lorsque vous devez traverser NAT. L'utilisation principale pour IAX de nos jours est d'interconnecter les serveurs Asterisk. IAX a été créé principalement pour la voix, mais il peut également accueillir la vidéo et d'autres flux multimédias. IAX a été inspiré par d'autres protocoles VoIP, tels que SIP et MGCP. Au lieu d'utiliser deux protocoles séparés pour la signalisation et le média, IAX les a unifiés pour créer un protocole unique. IAX n'utilise pas RTP pour le transport multimédia ; au lieu de cela, il intègre le média dans la même connexion UDP.

**État dans Asterisk 22.** `chan_iax2` est toujours inclus et entièrement pris en charge dans Asterisk 22 LTS, donc tout dans cette section reste valide. IAX2 est cependant un protocole hérité qui voit relativement peu de nouveaux déploiements : l'industrie a largement convergé vers SIP (via `chan_pjsip` dans Asterisk 22) pour à la fois le trunking fournisseur et l'interconnexion de serveurs. Le principal avantage restant d'IAX2 est sa conception à port unique — toute la signalisation et le média circulent sur un seul port UDP (4569 par défaut), ce qui simplifie la configuration du pare-feu et du NAT par rapport à SIP et ses flux RTP séparés. Pour un nouveau trunk Asterisk-à-Asterisk où le NAT n'est pas une préoccupation, un trunk PJSIP est l'approche moderne recommandée ; IAX2 est couvert ici car il reste un choix valide, surtout là où un seul port UDP peut être ouvert à travers un pare-feu.

### Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Identifier les forces et les faiblesses du protocole IAX
- Décrire les scénarios d'utilisation pour le protocole IAX
- Décrire les avantages du mode trunk IAX
- Configurer iax.conf pour les téléphones
- Configurer iax.conf pour la connexion à un fournisseur VoIP
- Configurer iax.conf pour l'interconnexion Asterisk
- Comprendre l'authentification IAX

### Conception IAX

Les principaux objectifs de la conception IAX sont :

- De réduire la bande passante requise pour le transport multimédia et la signalisation
- De fournir une transparence NAT
- D'être capable de transmettre les informations du dialplan
- De prendre en charge l'utilisation efficace de la pagination et de l'interphone

IAX est un protocole de signalisation et de média pair-à-pair similaire à SIP sans utiliser RTP. L'approche de base consiste à multiplexer les flux multimédias sur une seule connexion UDP entre deux hôtes. Le plus grand avantage de cette approche est sa simplicité lors de la traversée de connexions sur NAT, régulièrement trouvées dans les modems xDSL. IAX utilise un seul port, UDP 4569 par défaut, puis utilise un numéro d'appel avec 15 bits pour multiplexer tous les flux. Le protocole IAX utilise des processus d'enregistrement et d'authentification similaires au protocole SIP. Une description du protocole peut être trouvée sur http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![Le protocole IAX multiplexe de nombreux appels entre deux endpoints sur un seul port UDP (4569 par défaut), en utilisant un numéro d'appel de 15 bits pour séparer les flux — ce qui rend la traversée NAT simple.](../images/10-legacy-fig12.png)

### Utilisation de la bande passante

La bande passante utilisée dans les réseaux VoIP est affectée par plusieurs facteurs ; les codecs et les en-têtes de protocole sont les plus importants. Le protocole IAX a une fonctionnalité surprenante appelée mode trunk, par laquelle il multiplexe plusieurs appels en utilisant un seul en-tête. En jouant avec le calculateur de bande passante Asterisk, vous verrez comment les trunks IAX peuvent vous faire économiser jusqu'à 80 % du trafic avec plusieurs appels.

![Comparaison du surcoût IAX et SIP : deux appels SIP/RTP nécessitent deux paquets (40 octets de charge utile transportés sous 156 octets de surcoût), tandis que le mode trunk IAX2 transporte les deux appels dans un seul paquet (40 octets de charge utile sous seulement 66 octets de surcoût) en partageant un en-tête IP/UDP sur de nombreuses mini-trames.](../images/10-legacy-fig13.png)

### Nommage des canaux

Il est important de comprendre les conventions de nommage des canaux car vous utiliserez ces noms lors de la spécification d'un canal dans le dialplan. Le format d'un nom de canal IAX utilisé pour les canaux sortants est :

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

<user> UserID sur le pair distant, ou nom du client configuré dans iax.conf <secret> Le mot de passe. Alternativement, il peut s'agir du nom de fichier pour une clé RSA sans l'extension finale (.key ou .pub) et enfermé entre crochets <peer> Nom du serveur auquel se connecter <portno> Numéro de port pour la connexion <exten> Extension dans le serveur Asterisk distant <context> Contexte dans le serveur Asterisk distant <options> La seule option disponible est ‘a’ signifiant ‘request autoanswer’

#### Exemple de canaux sortants :

Les canaux sortants sont vus dans la console Asterisk. IAX2/8590:secret@myserver/8590@default Appelez l'extension 8590 dans myserver. Il utilise 8590:secret comme paire nom/mot de passe

IAX2/iaxphone Appelez "iaxphone" IAX2/judy:[judyrsa]@somewhere.com Appelez somewhere.com en utilisant judy comme nom d'utilisateur et une clé RSA pour l'authentification

#### Le format d'un canal IAX entrant est :

Les canaux entrants sont vus dans la console Asterisk.

```
IAX2/[<username>@]<host>]-<callno>
```

<username> Nom d'utilisateur si connu <host> Hôte se connectant <callno> Numéro d'appel local Exemple de canal entrant : IAX2[flavio@8.8.30.34]/10 Numéro d'appel 10 depuis l'adresse IP 8.8.30.34 en utilisant flavio comme utilisateur. IAX2[8.8.30.50]/11 Numéro d'appel 11 depuis l'adresse IP 8.8.30.50.

### Utilisation d'IAX

Vous pouvez utiliser IAX de plusieurs manières. Dans cette section, nous vous montrerons comment configurer IAX pour plusieurs scénarios, notamment :

- Connexion d'un soft-phone utilisant IAX
- Connexion d'IAX à un fournisseur VoIP utilisant IAX
- Connexion de deux serveurs utilisant IAX
- Connexion de deux serveurs utilisant IAX en mode trunk
- Débogage d'une connexion IAX
- Utilisation de paires de clés RSA pour l'authentification

#### Connexion d'un soft-phone utilisant IAX

Asterisk prend en charge les téléphones IP basés sur IAX tels que l'ATCOM et l'ancien ATA de Digium (appelé IAXy) ainsi que les soft-phones qui implémentent toujours le protocole IAX2. Le processus pour les soft-phones, les ATA et les téléphones matériels est similaire. Pour configurer un appareil IAX, vous devez modifier le fichier iax.conf dans /etc/asterisk

```
directory.
```

Nous utiliserons un soft-phone compatible IAX2 comme exemple. Étape 1 : Faites une sauvegarde du fichier iax.conf original en utilisant :

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

Étape 2 : Commencez à modifier un nouveau fichier iax.conf :

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Paramètre très important, il modifie les codecs disponibles

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

J'ai essayé de préserver les lignes par défaut (non commentées) du fichier exemple. Les paramètres suivants ont été modifiés :

```
bandwidth=high
```

Cette ligne affecte la sélection du codec. L'utilisation du réglage high permet la sélection d'une bande passante élevée et d'un codec de haute qualité tel que g.711 défini par le mot-clé ulaw. Si vous gardez le paramètre par défaut, vous ne pourrez pas choisir ulaw. Dans ce cas, Asterisk vous donnera le message « no codec available » pour la configuration ci-dessous.

```
disallow=all
allow=ulaw
```

Dans les commandes décrites ci-dessus, nous avons désactivé tous les codecs et activé uniquement ulaw. Dans les LAN, la plupart des gens préfèrent utiliser ulaw car il n'est pas gourmand en processeur et économise des cycles CPU. Même en utilisant plus de bande passante, ce codec est préférable car dans les LAN, vous avez généralement un Ethernet 100 mégabits ou même un Gigabit. Un appel vocal utilisant ulaw utilise près de 100 kilobits par seconde de bande passante de votre réseau, ce qui est une utilisation très légère pour les LAN haut débit d'aujourd'hui. Dans les réseaux WAN ou Internet, vous désactiverez généralement ulaw, échangeant quelques cycles CPU disponibles par la compression vocale pour une meilleure utilisation de la bande passante. Les codecs gsm , g729, et ilbc offrent également un bon facteur de compression.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Dans les commandes ci-dessus, nous avons défini un ami nommé [2003]. Le contexte est le default (dans les premiers laboratoires, nous utilisons toujours le contexte default pour éviter toute confusion ; ce contexte sera entièrement expliqué au chapitre 9). La ligne « host=dynamic » fournit un enregistrement dynamique de l'adresse IP du téléphone. Étape 3 : Téléchargez et installez un soft-phone compatible IAX2. Vous pouvez choisir n'importe quel soft-phone qui prend toujours en charge le protocole IAX2 pour le laboratoire. Étape 4 : Configurez un compte IAX dans le client (généralement *Add account* → IAX). Notez que le SipPulse Softphone est uniquement SIP et ne peut pas s'enregistrer via IAX2, donc pour le test IAX, vous avez besoin d'un client qui prend toujours en charge le protocole.

Étape 5 : Configurez le fichier extensions.conf pour tester votre appareil IAX.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Maintenant, vous pouvez composer entre les téléphones SIP créés au chapitre 3 et le téléphone IAX créé dans le laboratoire.

#### Connexion à un fournisseur VoIP utilisant IAX

Quelques fournisseurs VoIP prennent en charge IAX. Vous pouvez facilement trouver un fournisseur IAX en recherchant « IAX providers ». L'utilisation d'un fournisseur IAX a beaucoup de sens car IAX peut économiser beaucoup de bande passante, traverse facilement le NAT et peut s'authentifier en utilisant des paires de clés RSA.

![L'Asterisk d'un client connecté à un fournisseur VoIP via un trunk IAX sur Internet : un seul trunk transporte tous les appels vers et depuis le fournisseur.](../images/10-legacy-fig14.png)

Le nombre de fournisseurs VoIP commerciaux compatibles IAX a fortement diminué au cours des dernières versions d'Asterisk ; la plupart des fournisseurs proposent désormais exclusivement des trunks SIP/PJSIP. Avant de vous engager auprès d'un fournisseur IAX, confirmez qu'ils maintiennent activement leur infrastructure IAX. Pour une nouvelle intégration de fournisseur, un trunk PJSIP (Chapitre 3) est l'alternative recommandée.

#### Connexion à un fournisseur utilisant IAX

Étape 1 : Ouvrez un compte chez votre fournisseur préféré. Votre fournisseur vous fournira trois choses.

- Nom
- Secret
- Adresse IP ou nom d'hôte
- Clé publique RSA

Étape 2 : Configurez le fichier iax.conf pour enregistrer votre Asterisk auprès de votre fournisseur. Ajoutez les lignes suivantes à la section [general] du fichier.

```
[general]
register=>name:secret@hostname/2003
```

Dans les instructions décrites ci-dessus, vous vous êtes enregistré auprès de votre fournisseur en utilisant votre compte et votre mot de passe. Au moment où vous recevez un appel, il sera transféré vers l'extension 2003.

```
[name]
```

- ; Votre nom de compte ou numéro

```
type=peer
secret=secret
; Your password
host=hostname
```

Dans les instructions décrites ci-dessus, nous avons créé un pair correspondant au fournisseur à des fins de composition.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Ceci est requis pour l'authentification RSA. L'utilisation de la clé publique de votre fournisseur vous permet d'être sûr que l'appel reçu provient réellement du vrai fournisseur. Si quelqu'un d'autre essaie d'utiliser le même chemin, il ne pourra pas l'authentifier car il ne possède pas la clé privée correspondante. Étape 4 : Essayez la connexion. Pour tester la connexion, composez n'importe quel numéro. Certains fournisseurs proposent un test d'écho. Pour ce faire, veuillez modifier le fichier extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Allez dans la CLI Asterisk et lancez un reload. Pour vérifier si Asterisk est enregistré auprès du fournisseur, utilisez la commande suivante.

```
CLI>reload
CLI>iax2 show register
```

Maintenant, composez simplement *98 sur le soft-phone connecté au serveur Asterisk.

#### Connexion de deux serveurs Asterisk via un trunk IAX

Il est très facile de connecter un serveur à un autre. Vous n'aurez pas besoin de les enregistrer car les adresses IP sont déjà connues. Vous devrez créer les pairs et les utilisateurs dans le fichier iax.conf. Toutes les extensions sur le site HQ commencent par 20 suivies de deux chiffres (par exemple, 2000). Dans la succursale, toutes les extensions commencent par 22 suivies de deux chiffres (par exemple, 2200). Nous utiliserons le trunk. Vous aurez besoin d'une source de synchronisation DAHDI pour activer cette fonctionnalité. Étape 1 : Modifiez le fichier iax.conf dans le serveur de la succursale.

![Connexion de deux serveurs Asterisk avec un trunk IAX : le serveur HQ (192.168.1.1, extensions 20xx) et le serveur de la succursale (192.168.1.2, extensions 22xx) se rejoignent via un seul trunk IAX — aucun enregistrement n'est nécessaire car les deux adresses IP sont fixes et connues.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

Étape 2 : Configurez le fichier extensions.conf dans le serveur de la succursale

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

Étape 3 : Configurez le fichier iax.conf dans le serveur HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Étape 4 : Configurez le fichier extensions.conf dans le serveur HQ.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Étape 5 : Testez un appel depuis le téléphone 2000 dans le serveur HQ vers le téléphone 2200 dans le serveur de la succursale.

### Authentification IAX

Analysons maintenant le processus d'authentification IAX d'un point de vue pratique pour vous aider à choisir la meilleure méthode pour chaque exigence spécifique.

#### Connexions entrantes

![Le flux de décision d'authentification IAX pour un appel entrant : Asterisk se branche sur le fait qu'un nom d'utilisateur est fourni, s'il correspond à une section, si l'adresse IP source est autorisée, et si le secret (texte clair, MD5, ou RSA) correspond — acceptant l'appel avec le contexte et les options de pair de cette section, ou le refusant.](../images/10-legacy-fig16.png)

Lorsqu'Asterisk reçoit une connexion entrante, les informations initiales peuvent inclure un nom d'utilisateur (à partir du champ « username= ») ou non. La connexion entrante a également une adresse IP, qu'Asterisk utilise également pour l'authentification. Si un utilisateur est fourni, Asterisk : 1. Recherche dans iax.conf une entrée avec type=user (ou type=friend avec un nom de section correspondant au nom d'utilisateur). S'il ne le trouve pas, Asterisk refuse la connexion. 2. Si l'entrée trouvée a des configurations deny/allow, il compare l'adresse IP de l'appelant pour déterminer s'il faut accepter l'appel ou non en fonction des clauses deny/allow. 3. Il vérifie le mot de passe (secret) en utilisant du texte clair, md5, ou RSA. 4. Il accepte la connexion et envoie l'appel au contexte spécifié dans la ligne « context= » du fichier iax.conf. Si un nom d'utilisateur n'est pas fourni, Asterisk : 1. Recherche une entrée contenant type=user (ou type=friend) dans le fichier iax.conf sans secret spécifié. Il vérifie également les clauses deny/allow. Si une entrée est trouvée, la connexion est acceptée et le nom de la section est utilisé comme nom d'utilisateur. 2. Recherche une entrée contenant type=user (ou type=friend) dans le fichier iax.conf avec un secret ou une clé RSA spécifiée. Il vérifie les clauses deny/allow. Si une entrée est trouvée, il tente d'authentifier l'appelant en utilisant le secret spécifié ; s'il correspond, il accepte la connexion. Le nom de la section est le nom de l'utilisateur. Supposons que votre fichier iax.conf ait les entrées suivantes :

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

Si un appel a un nom d'utilisateur spécifié, tel que :

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk tentera d'authentifier l'appel en utilisant uniquement l'entrée correspondante dans le fichier iax.conf. Si d'autres noms sont spécifiés, l'appel serait rejeté. Si aucun utilisateur n'est spécifié, Asterisk tentera d'authentifier la connexion en tant que guest. Cependant, si guest n'existe pas, il tentera toute autre connexion avec un secret correspondant. En d'autres termes, si vous n'avez pas de section guest dans votre fichier iax.conf, un utilisateur malveillant pourrait essayer de deviner n'importe quel secret correspondant en ne spécifiant pas le nom d'utilisateur. Les restrictions deny/allow des adresses IP s'appliquent également. Un bon moyen d'éviter la devinette de secret est d'utiliser l'authentification RSA. Une autre méthode consiste à restreindre les adresses IP autorisées à appeler.

#### Restrictions d'adresse IP

permit = <ipaddr>/<netmask> Les règles sont interprétées en séquence, et toutes sont évaluées (ce concept est différent des ACL deny = <ipaddr>/<netmask> généralement trouvées dans les routeurs et les pare-feux). Exemple #1 permit=0.0.0.0/0.0.0.0 deny=192.168.0.0/255.255.255.0 Refusera tout paquet du réseau 192.168.0.0/24 Exemple #2 deny=192.168.0.0/255.255.255.0 permit=0.0.0.0/0.0.0.0 Il autorisera tout paquet. La dernière instruction supplante la première.

#### Connexions sortantes

Les connexions sortantes acquièrent des informations d'authentification en utilisant les méthodes suivantes :

- La description du canal IAX2 passée par l'application dial().
- Une entrée avec type=peer ou type=friend dans le fichier iax.conf.
- Une combinaison des deux méthodes.

#### Connexion de deux serveurs Asterisk utilisant des clés RSA

Il est possible d'utiliser IAX avec une authentification forte en utilisant des clés RSA asymétriques. Selon le code source (res_krypto.c), Asterisk utilise des clés RSA avec un algorithme SHA-1 pour les digests de message au lieu du MD5 plus faible. Voici un guide étape par étape pour configurer deux serveurs en utilisant des clés RSA.

##### Configuration du serveur pour la succursale

Étape 1 : Générez les clés RSA dans le serveur de la succursale

```
astgenkey -n
```

Lorsqu'on vous le demande, utilisez le nom de clé branch. Nous avons utilisé le paramètre –n pour éviter de passer une phrase de passe chaque fois qu'Asterisk se réinitialise. Si vous voulez améliorer la sécurité, n'utilisez pas le –n et démarrez Asterisk avec asterisk -i Étape 2 : Copiez les clés dans le répertoire /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Étape 3 : Copiez la clé publique vers le serveur HQ

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Étape 4 : Modifiez le fichier iax.conf dans le serveur de la succursale.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

Étape 8 : Configurez le fichier extensions.conf dans le serveur de la succursale

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configuration du serveur pour le siège social

Étape 1 : Générez les clés RSA dans le serveur HQ

```
astgenkey -n
```

Lorsqu'on vous le demande, utilisez le nom de clé hq. Étape 2 : Copiez les clés dans le répertoire /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

Étape 3 : Copiez la clé publique vers le serveur BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Étape 4 : Configurez le fichier iax.conf dans le serveur HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Étape 10 : Configurez le fichier extensions.conf dans le serveur HQ.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Étape 11 : Testez un appel depuis le téléphone 2000 dans le serveur HQ vers le téléphone 2200 dans le serveur de la succursale.

### Configuration du fichier iax.conf

Le fichier iax.conf a plusieurs paramètres ; discuter de chaque paramètre un par un serait ennuyeux et contre-productif. Tous les paramètres, ainsi qu'une description, peuvent être trouvés dans le fichier exemple. Sur le wiki www.voip-info.org, vous trouverez des informations détaillées sur chacun d'eux. Ici, nous montrerons certains des paramètres les plus importants pour la configuration de la section générale, des pairs et des utilisateurs.

#### Section [General]

Adresses du serveur bindport = <portnum> Configure le port UDP IAX. La valeur par défaut est 4569. bindaddr = <ipaddr> Utilisez 0.0.0.0 pour lier Asterisk à toutes les interfaces ou spécifiez l'adresse IP d'une interface spécifique. Sélection du codec bandwidth = [low|medium|high] High = tous les codecs Medium = tous les codecs sauf ulaw et alaw Low = codecs à faible bande passante allow/disallow = Affinage de la sélection du codec [alaw|ulaw|gsm|g.729| etc.]

### Jitter buffer

Le jitter est la variation de délai entre les paquets. C'est le facteur le plus important affectant la qualité vocale. Un Jitter buffer est utilisé pour compenser la variation de délai. Il sacrifie la latence en faveur d'un jitter plus faible. Vous pouvez faire une analogie entre le jitter buffer et un réservoir d'eau. Les deux peuvent recevoir des paquets ou de l'eau à des intervalles irréguliers, mais délivreront finalement un flux régulier.

![Le jitter buffer comme réservoir d'eau : les paquets arrivent irrégulièrement du réseau et remplissent le buffer, qui les libère ensuite à un débit constant pour produire un flux vocal fluide. La taille du buffer (en ms) échange un peu de latence contre un jitter plus faible ; la bande de buffer excédentaire permet à Asterisk d'agrandir ou de réduire le buffer à mesure que les conditions du réseau changent.](../images/10-legacy-fig17.png)

Un jitter faible (c'est-à-dire inférieur à 20 ms) est généralement imperceptible. Cependant, un jitter au-dessus de ce niveau est ennuyeux. La latence ou le délai doit être maintenu en dessous de 150 ms. Créer un jitter buffer sacrifiera un certain délai pour un jitter plus faible — un concept connu sous le nom de « budget de délai ». Vous pouvez affecter le jitter buffer en utilisant ces paramètres :

- Jitterbuffer=<yes/no> – Active ou désactive
- Dropcount=<number> - Quantité maximale de trames qui devraient être retardées au cours des deux dernières secondes. Le réglage recommandé est 3 (1,5 % de trames perdues)
- Maxjitterbuffer=<ms> - Généralement en dessous de 100 ms
- Maxexcessbuffer=<ms> - Si le délai du réseau s'améliore, le jitter buffer pourrait être surdimensionné. Par conséquent, Asterisk essaiera de le réduire.
- Minexcessbuffer=<ms> - Une fois que le buffer excédentaire tombe à cette valeur, Asterisk commence à augmenter la taille du buffer.

### Marquage de trame

Le paramètre ci-dessous marque le paquet IP dans le champ type de service. Les routeurs peuvent lire cette étiquette, donnant ainsi la priorité au trafic. Asterisk utilise des codes DSCP pour ce champ (RFC 2474). Les valeurs autorisées sont CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, et ef (c'est-à-dire, transfert accéléré).

```
tos=ef
```

### Chiffrement IAX2

IAX prend en charge le chiffrement des appels en utilisant une clé symétrique, un chiffrement par bloc de 128 bits appelé AES (Advanced Encryption Standard). Il est très simple d'activer le chiffrement entre les trunks IAX. Dans le fichier iax.conf, utilisez :

```
encryption=yes
```

Pour forcer le chiffrement :

```
forceencryption=yes
```

Pour garantir la compatibilité avec les anciennes versions, vous devrez peut-être désactiver la rotation de clé en utilisant :

```
keyrotate=no
```

### Commandes de débogage IAX2

Voici quelques-unes des commandes de console de dépannage les plus importantes pour Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

En regardant cette sortie, identifiez le début et la fin de l'appel. Observez les informations de délai et de jitter obtenues en utilisant les paquets poke et pong. Ces paquets aident à créer la sortie de la commande « iax2 show netstats ».

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

Pour désactiver le débogage, utilisez :

```
vtsvoffice*CLI>iax2 no debug
```

### Résumé

Ce chapitre a passé en revue les forces et les faiblesses du protocole IAX. Il a démontré comment IAX fonctionne dans plusieurs scénarios, tels que les soft-phones et un trunk entre deux serveurs Asterisk. Le mode trunk vous permet d'économiser de la bande passante en transportant plus d'un appel dans un seul paquet. Enfin, vous avez appris des commandes de console que vous pouvez utiliser pour vérifier l'état et déboguer le protocole.

## SIP hérité : chan_sip et sip.conf (supprimé dans Asterisk 21+)

> **Hérité / historique :** Tout dans cette section utilise l'ancien pilote `chan_sip` et son fichier de configuration `sip.conf`. `chan_sip` a été obsolète pendant plusieurs versions et **supprimé dans Asterisk 21**, donc il **n'existe pas dans Asterisk 22**. Aucun des exemples `sip.conf` ci-dessous ne fonctionnera sur un système actuel — ils sont conservés ici uniquement pour documenter comment les déploiements hérités fonctionnaient et pour vous aider à les migrer. Pour la méthode moderne et prise en charge de faire tout cela, voir la section *PJSIP : le canal SIP* du chapitre *SIP & PJSIP en profondeur*. La théorie du *protocole* SIP (méthodes, enregistrement, proxy/redirect, SDP, types NAT) est au niveau du protocole et vit dans ce chapitre ; ce qui suit est purement la **configuration** `chan_sip` supprimée.

Sur les systèmes hérités jusqu'à Asterisk 20, SIP était configuré dans `/etc/asterisk/sip.conf`, qui était le deuxième fichier le plus modifié (juste après `extensions.conf`). Les sections ci-dessous montrent comment `chan_sip` connectait Asterisk à un fournisseur SIP, comment connecter deux Asterisks ensemble en utilisant SIP, la prise en charge de domaine, la présence, les options de codec/DTMF/QoS, l'authentification et le NAT — suivies d'un guide pour migrer tout cela vers PJSIP.

### Connexion d'Asterisk à un fournisseur SIP (sip.conf)

Asterisk est souvent utilisé pour se connecter à un fournisseur VoIP SIP. Les fournisseurs VoIP ont généralement de meilleurs tarifs pour les appels téléphoniques que les fournisseurs traditionnels. Un autre point intéressant et attrayant des fournisseurs VoIP est la possibilité d'acheter des numéros DID dans d'autres villes — même dans des pays étrangers. Ce sont de bonnes raisons d'utiliser la VoIP pour les télécommunications. Dans cette section, vous apprendrez comment le `chan_sip` hérité connectait Asterisk à un fournisseur VoIP. Trois étapes sont nécessaires pour connecter Asterisk à un fournisseur SIP. Les tests peuvent être effectués en établissant un compte avec votre fournisseur préféré. Étape 1 : Enregistrement auprès d'un fournisseur SIP dans sip.conf Pour vous connecter à un fournisseur SIP, vous aurez besoin des informations suivantes du fournisseur :

![Asterisk connecté à un fournisseur de services VoIP via Internet ou un WAN privé, avec des téléphones SIP locaux enregistrés sur le serveur Asterisk](../images/07-sip-and-pjsip-fig07.png)

- nom d'utilisateur
- secret et remotesecret (Utilisez secret pour authentifier les demandes entrantes et remotesecret pour les demandes sortantes)
- nom d'hôte
- domaine
- codecs autorisés

Cette configuration permettra à votre fournisseur de localiser l'adresse IP d'Asterisk. Dans l'instruction suivante, nous disons à Asterisk de s'enregistrer auprès d'un fournisseur SIP défini par le nom d'hôte et d'informer le fournisseur de l'adresse IP d'Asterisk. L'instruction dit que vous voulez recevoir des appels à l'extension 4100. Dans la section [general] du fichier sip.conf, entrez la ligne suivante :

```
register=>name:secret@hostname/4100
```

Étape 2 : Configurez le [peer] sur sip.conf Créez une entrée de type peer pour le fournisseur souhaité afin de simplifier la composition d'Asterisk.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Étape 3 : Créez une route vers le fournisseur dans le dialplan Nous choisirons les chiffres 010 comme route de destination vers le fournisseur. Pour composer #610000 à l'intérieur du fournisseur, composez simplement 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)=”Flavio Gonçalves”)
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### Options SIP spécifiques au scénario du fournisseur

La discussion suivante examine les détails des options définies dans le fichier sip.conf pour la connexion à un fournisseur VoIP.

```
register=>username:password@hostname/4100
```

L'instruction registered dans le fichier sip.conf est utilisée pour s'enregistrer auprès d'un fournisseur. La transaction d'enregistrement est authentifiée avec le nom et le secret. Vous pouvez utiliser une barre oblique (« / ») pour fournir une extension pour les appels entrants. Techniquement parlant, l'extension sera placée dans le champ d'en-tête « Contact » de la requête SIP. Le comportement d'enregistrement peut être contrôlé par certains paramètres :

```
registertimeout=20
registerattempts=10
```

Pour vérifier si l'enregistrement a réussi, la commande de console héritée était `sip show registry`. Sur Asterisk 22, la commande équivalente est `pjsip show registrations` (enregistrements sortants) et `pjsip show endpoints` pour l'état de l'endpoint.

Le paramètre « username » est utilisé dans le digest d'authentification. Le digest est calculé en utilisant le nom d'utilisateur, le secret et le domaine :

```
username=username
```

Host définit l'adresse ou le nom du fournisseur VoIP :

```
host=hostname
```

Les paramètres Fromuser et Fromdomain sont parfois requis pour l'authentification. Ces paramètres sont utilisés dans le champ d'en-tête SIP From :

```
fromuser=username
fromdomain=hostname
```

Lorsque vous vous connectez à un fournisseur VoIP, des informations d'identification sont requises. Après l'invitation initiale, le fournisseur vous envoie un message appelé « 407 Proxy Authentication Required » ; vous fournissez les informations d'identification dans le message INVITE suivant. Pour les appels entrants, votre serveur Asterisk demandera des informations d'identification pour le fournisseur. Évidemment, le fournisseur n'a pas d'informations d'identification valides pour votre serveur Asterisk. Lorsque vous utilisez insecure=invite, vous dites à Asterisk de ne pas envoyer le « 407 Proxy Authentication Required » au fournisseur et d'accepter les appels entrants. Vous pouvez également utiliser insecure=port, invite pour faire correspondre le pair en fonction de l'adresse IP sans faire correspondre le numéro de port.

```
insecure=invite, port
```

### Connexion de deux serveurs Asterisk ensemble en utilisant SIP (sip.conf)

Vous pouvez utiliser SIP pour interconnecter deux boîtes Asterisk. Il est important de faire attention au dialplan avant de poursuivre avec cette configuration. Les utilisateurs veulent généralement connecter d'autres PBX avec un effort minimal. L'idée ici est d'utiliser un numéro d'extension uniquement pour se connecter à l'autre PBX. Étape 1 : Modifiez le fichier sip.conf dans le serveur A :

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Étape 2 : Modifiez le fichier sip.conf dans le serveur B :

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Connexion de deux serveurs Asterisk utilisant SIP : le serveur A (extensions 4400/4401) et le serveur B (extensions 4500/4501) échangent de la signalisation SIP afin que les utilisateurs sur chaque PBX puissent composer l'autre](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Étape 3 : Modifiez le fichier extensions.conf dans le serveur A :

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Étape 4 : Modifiez le fichier extensions.conf dans le serveur B :

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Prise en charge de domaine Asterisk (sip.conf)

Le protocole SIP suit l'architecture Internet. La première chose à faire avant de configurer SIP est de définir correctement les serveurs DNS. Dans un environnement SIP, vous pouvez appeler un utilisateur situé dans n'importe quel proxy SIP, et d'autres utilisateurs peuvent vous appeler également en utilisant votre identifiant de ressource uniforme (URI) SIP. Pour définir un serveur DNS pour SIP, vous devez ajouter des enregistrements SRV à votre serveur DNS.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

Après avoir configuré le DNS, vous pouvez utiliser l'URI, qui pointe vers un utilisateur SIP, un téléphone SIP ou une extension téléphonique. Un URI SIP ressemble à une adresse e-mail (par exemple, sip:chuck@yourpartnerdomain.com). En utilisant des URI SIP, aucun numéro de téléphone n'est nécessaire pour passer un appel d'un téléphone SIP à un autre. Pour appeler un utilisateur externe, utilisez simplement une instruction comme celle montrée ci-dessous.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certains paramètres peuvent contrôler le comportement du domaine.

```
srvlookup=yes
```

Ce paramètre active les recherches DNS SRV sur les appels sortants. En utilisant ce paramètre, il est possible de composer des appels en utilisant des noms SIP basés sur le domaine.

```
allowguest=yes
```

Ce paramètre permet à une invitation externe d'être traitée sans authentification. Il traite l'appel dans le contexte défini dans la section générale ou dans l'instruction de domaine. Avertissement : Si vous définissez un contexte dans la section générale avec accès au PSTN, un utilisateur externe peut composer le PSTN via votre PBX. Dans ce cas, vous encourrez des frais. N'autorisez que vos propres extensions dans le contexte défini dans la section générale.

![Connexion à d'autres serveurs SIP par domaine : youdomain.com et yourpartnerdomain.com échangent de la signalisation SIP, afin que les utilisateurs tels que lee et bruce puissent appeler chuck et norris en utilisant des URI SIP](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

La commande domain vous permet de gérer plus d'un domaine au sein d'Asterisk. Si un appel provient d'un domaine spécifique, il est dirigé vers un contexte spécifique.

```
;autodomain=yes
```

Ce paramètre inclut l'IP locale et le nom d'hôte dans les domaines autorisés.

```
;allowexternaldomains=no
```

La valeur par défaut est yes. Décommentez la ligne pour interdire les appels vers des domaines extérieurs.

### Configurations SIP avancées (sip.conf)

Cette section explique certains paramètres avancés du canal SIP hérité, tels que la présence, la sélection de codec, les options DTMF et le marquage de paquets QoS. Les **concepts** (BLF/présence, négociation de codec, modes DTMF, marquage DSCP) sont reportés sur PJSIP, mais les noms de paramètres `sip.conf` montrés ici n'existent **pas** dans Asterisk 22. Sur PJSIP, le mode DTMF est `dtmf_mode=` sur un endpoint, et les codecs sont définis avec `allow=`/`disallow=`.

#### Présence SIP

La présence SIP est partiellement implémentée dans Asterisk. Asterisk prend en charge les demandes telles que SUBSCRIBE et NOTIFY pour les utilisateurs en fonction de l'état d'un canal. Asterisk ne prend pas en charge la méthode SIP PUBLISH. En d'autres termes, vous pouvez vous abonner aux états (occupé, inactif et sonnerie) d'un canal, mais ne pouvez pas publier d'informations telles que « absent » ou « ne pas déranger ». Le scénario le plus courant pour la présence est le champ de lampe occupée (BLF), dans lequel vous simulez le comportement d'un système KS avec des lampes pour chaque extension et trunk. Paramètres SIP pour la présence :

- allowsubscribe=yes : Autoriser les méthodes d'abonnement SIP
- subscribecontext=sip_subscribers : Contexte où chercher des indices
- notifyring=yes : Envoyer SIP NOTIFY sur sonnerie
- notifyhold=yes : Envoyer SIP NOTIFY sur attente
- counteronpeer (renommé de limitonpeer pour Asterisk 1.4.x) : Appliquer le compteur uniquement du côté pair
- callcounter=yes : Activer les compteurs d'appels dans l'appareil.
- busylevel=1 : Seuil pour le nombre d'appels pour considérer l'appareil comme occupé.

Par exemple : Étape 1 : Tester la présence SIP avec Asterisk n'est pas si difficile. Tout d'abord, configurons les fichiers sip.conf et extensions.conf.

Dans le fichier sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Étape 2 : Configurez maintenant le soft-phone pour utiliser la présence. Nous vous montrerons comment configurer le SipPulse Softphone.

- Séquence : clic droit->SIP Account Settings->Properties->Presence
- Changez le modèle de présence de pair-à-pair à agent de présence, ce qui fera que le soft-phone s'abonnera à Asterisk pour les événements SIP.

Étape 3 : Ajoutez le contact à d'autres soft-phones. Dans cet exemple, le SipPulse Softphone est le compte 2000, nous ajouterons donc un contact pour le compte 2001. Séquence : Ouvrez le panneau droit (panneau de présence dans le softphone)->Cliquez sur Contacts->Ajouter un contact. Remplissez le nom 2001. Affichez comme 2001 et n'oubliez pas de cocher la case Show this contact’s availability.

Étape 4 : Maintenant, appelez l'extension 2001 et vérifiez l'état du téléphone dans le panneau droit du soft-phone. Utilisez la commande de console `core show hints` pour voir l'état de présence changer dans le serveur (dans chan_sip hérité, `sip show inuse` montrait combien d'appels vous aviez sur chaque ligne). Sur Asterisk 22, utilisez `pjsip show endpoints` pour inspecter l'état de l'endpoint et du canal. L'état de présence/BLF apparaît dans les contacts ou le panneau BLF du softphone — exactement comment il est affiché dépend du client.

#### Configuration du codec

La configuration du codec est simple et directe. Vous pouvez définir les mots allow et disallow dans la section [general] ou la section pair/utilisateur. La meilleure pratique est de standardiser le codec pour éviter le transcodage, qui est gourmand en processeur. Veuillez utiliser le même codec pour les messages et les invites.

```
[general]
disallow=all
allow=g729
```

#### Options DTMF

À certaines occasions, vous passerez des chiffres à une application telle que la messagerie vocale ou le serveur vocal interactif (IVR). Il est important de passer le DTMF correctement. La méthode la plus simple pour passer le DTMF est appelée inband. Elle est définie dans la section [general] ou pair/utilisateur du fichier sip.conf. Lorsque vous définissez dtmfmode=inband, les tonalités DTMF sont générées sous forme de sons dans le canal audio. Le problème principal avec cette méthode est que, lorsque vous compressez le canal audio en utilisant un codec tel que g729, les sons sont déformés et les tonalités DTMF ne sont pas correctement reconnues. Si vous prévoyez d'utiliser dtmfmode=inband, utilisez le codec g.711 (ulaw et alaw).

```
dtmfmode=inband
```

Une autre approche consiste à utiliser RFC2833, qui vous permet de passer des tonalités DTMF sous forme d'événements nommés dans les paquets RTP.

```
dtmfmode=rfc2833
```

Enfin, vous pouvez passer des chiffres DTMF à l'intérieur des paquets SIP, au lieu des paquets RTP. Cette méthode est définie dans la RFC3265 (événements de signalisation) et la RFC2976.

```
dtmfmode=info
```

Suite à la sortie de la version 1.2, il est maintenant possible d'utiliser :

```
dtmfmode=auto
```

Ceci tente d'utiliser le RFC2833 ; si ce n'est pas possible, utilisez des tonalités de bande.

#### Configuration du marquage de la qualité de service (QoS)

La QoS est un ensemble de techniques responsables de la qualité vocale. La QoS est implémentée de manière à réduire la bande passante, la latence et le jitter. Les principales fonctions QoS sont la planification de paquets, la fragmentation et la compression d'en-tête. La QoS est implémentée dans les commutateurs et les routeurs, pas par Asterisk lui-même. Cependant, Asterisk peut aider les routeurs et les commutateurs en marquant les paquets pour une livraison express. Le marquage est effectué en utilisant des points de code de services différenciés (DSCP) définis dans les RFC 2474 et RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

À partir de la version 1.4, vous pouvez spécifier des codes différents pour la signalisation (SIP), l'audio (RTP) et la vidéo (RTP).

### Authentification SIP (sip.conf)

Lorsque le `chan_sip` hérité recevait un appel SIP, il suivait les règles décrites dans le diagramme suivant. Trois paramètres jouaient un rôle important dans l'authentification SIP. Sur Asterisk 22, l'authentification est configurée à la place avec des objets PJSIP `auth` (`type=auth`, `auth_type=userpass`, `username=`, `password=`) référencés par un endpoint, et le contrôle d'accès IP est effectué avec `permit=`/`deny=` sur l'endpoint ou via un `acl`.

![Flux de décision d'authentification chan_sip hérité : Asterisk vérifie l'en-tête From par rapport à sip.conf, essaie la section type=user/peer correspondante et les informations d'identification MD5, et revient à insecure=invite ou allowguest avant d'autoriser ou de refuser l'appel](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Ce paramètre contrôle si un utilisateur sans pair correspondant peut s'authentifier sans nom et secret. Nous avons discuté de ce paramètre dans la section sur la prise en charge de domaine.

```
insecure=invite,port
```

Lorsque nous utilisons insecure=invite, Asterisk ne génère pas le message « 407 Proxy Authentication Required ». Sans ce message, l'utilisateur peut passer un appel sans authentification. Ceci est souvent utilisé pour se connecter aux fournisseurs de services VoIP. Les appels provenant du fournisseur de services VoIP ne sont généralement pas authentifiés.

```
autocreatepeer=yes/no
```

Cette commande est utilisée lorsqu'Asterisk est connecté à un proxy SIP. Elle crée dynamiquement un pair pour chaque appel. Lorsque cette option est activée, n'importe quel UAC peut se connecter au serveur Asterisk. Il est important de limiter la connexion IP au proxy SIP. Le proxy SIP, à son tour, s'occupe du contrôle d'accès. La configuration du pair est basée sur les options générales ainsi que sur le champ d'en-tête « Contact » du paquet SIP. Avertissement : Utilisez ceci avec une extrême prudence car cela ouvre complètement Asterisk.

```
secret=secret, remotesecret=secret
```

Ce paramètre configure le secret pour l'authentification, utilisez secret pour les demandes entrantes et remotesecret pour les demandes sortantes. Si vous ne voulez pas présenter les secrets dans des fichiers texte, vous pouvez utiliser md5secret pour inclure un hash au lieu du secret. Pour générer le secret MD5, vous pouvez utiliser :

```
echo –n “username:realm:secret” |md5sum
```

Ensuite, utilisez l'instruction suivante :

```
md5secret=0b0e5d467890....
```

Avertissement : N'oubliez pas d'utiliser le paramètre –n ; le retour chariot sera utilisé dans le calcul md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

Les instructions ci-dessus refuseront toutes les adresses IP et autoriseront l'UAC uniquement depuis le réseau local (192.168.1.0/24).

#### Options RTP

Il est possible de contrôler certains paramètres RTP.

```
rtptimeout=60
```

Ceci termine les appels sans activité RTP pendant plus de 60 secondes lorsqu'ils ne sont pas en attente.

```
rtpholdtimeout=120
```

Ceci termine les appels sans activité RTP même en attente (devrait être plus grand que rtptimeout).

### Traversée NAT SIP (sip.conf)

La *théorie* du NAT (les quatre types de NAT, le problème de l'en-tête Contact, les keep-alives, et le forçage du média via le serveur) est au niveau du protocole et est couverte dans le chapitre *SIP & PJSIP en profondeur*. Les paramètres `sip.conf` montrés ici (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) sont du **chan_sip hérité** et ont été supprimés dans Asterisk 21+. Sur PJSIP, ceux-ci correspondent à des paramètres de transport/endpoint tels que `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, et `local_net=` sur le transport, plus `qualify_frequency=` sur l'AOR.

Dans chan_sip hérité, le paramètre `nat` avait cinq options :

- nat = no — Pas de gestion NAT spéciale autre que RFC3581
- nat = force_rport — Prétendre qu'il y avait un paramètre rport même s'il n'y en avait pas
- nat = comedia — Envoyer le média vers le port d'où Asterisk l'a reçu, indépendamment de l'endroit où le SDP dit de l'envoyer.
- nat = auto_force_rport — Définir l'option force_rport si Asterisk détecte NAT (par défaut)
- nat = auto_comedia — Définir l'option comedia si Asterisk détecte NAT

Lorsque vous mettez l'instruction « nat=force_rport » dans le fichier sip.conf, vous dites à Asterisk d'ignorer l'adresse contenue dans le champ d'en-tête « Contact » de l'en-tête SIP et d'utiliser l'adresse IP source et le port dans l'en-tête IP du paquet et aussi d'envoyer le média vers l'adresse d'où il a été reçu en ignorant le contenu de l'en-tête SDP.

```
nat=force_rport,comedia
```

Il est nécessaire de garder la correspondance NAT ouverte. Si le NAT expire, Asterisk ne peut pas envoyer d'invitation à l'UAC. L'UAC est capable d'envoyer des appels, mais pas d'en recevoir. L'instruction suivante peut être utilisée pour garder le NAT ouvert.

```
qualify=yes
```

Qualify enverra régulièrement un paquet SIP en utilisant la méthode OPTIONS, ce qui aidera à garder le NAT ouvert. Qualify envoie un OPTIONS toutes les 60 secondes et toutes les 10 secondes lorsque l'hôte n'est pas joignable. Vous pouvez utiliser « sip show peers » pour voir la latence des pairs. Si le NAT de l'utilisateur est de type symétrique, il n'est pas possible d'envoyer des paquets d'un UAC à un autre directement ; dans ce cas, vous devez forcer le RTP via Asterisk en utilisant :

```
directmedia=no
```

#### Asterisk derrière NAT (sip.conf)

Tous les scénarios précédents supposent que le serveur Asterisk a une adresse Internet externe (valide). Parfois, le serveur Asterisk est implémenté derrière un pare-feu avec NAT. Dans ce cas, il est nécessaire de faire quelques configurations supplémentaires.

![Asterisk derrière NAT : un pare-feu mappe l'adresse publique 200.180.4.168 vers le serveur Asterisk interne (192.168.1.100), transférant SIP sur UDP 5060 et la plage RTP UDP 10000–20000 définie dans rtp.conf](../images/07-sip-and-pjsip-fig13.png)

Étape 1 : Configurez le pare-feu pour rediriger statiquement le port UDP 5060 vers le serveur Asterisk. Étape 2 : Configurez le pare-feu pour rediriger statiquement les ports UDP de 10000 à 20000. Si vous voulez restreindre le nombre de ports ouverts, vous pouvez modifier le fichier rtp.conf pour changer la plage de ports RTP. Une autre façon est d'utiliser un pare-feu intelligent qui prend en charge le protocole SIP pour ouvrir dynamiquement les ports RTP.

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

Étape 3 : Configurez Asterisk pour inclure l'adresse externe dans les champs d'en-tête des paquets SIP, y compris le protocole de description de session (SDP). Vous pouvez accomplir cela en ajoutant les deux instructions suivantes au fichier sip.conf :

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

Le premier paramètre externaddr dit à Asterisk d'inclure l'adresse IP externe à l'intérieur des en-têtes SIP pour les destinations externes. Le second paramètre localnet permet à Asterisk de différencier les adresses externes et internes. Optionnellement, vous pouvez utiliser externhost si vous utilisez un DNS dynamique avec une adresse DHCP sur le serveur.

### Chaînes de numérotation SIP (chan_sip)

La technologie de chaîne de numérotation `SIP/...` montrée ci-dessous est le pilote chan_sip supprimé. Sur Asterisk 22, utilisez plutôt la technologie `PJSIP/...` — par exemple `Dial(PJSIP/2000)` ou `Dial(PJSIP/${EXTEN}@provider)`. Les formes et la signification sont par ailleurs analogues.

Vous pouvez appeler une destination SIP héritée en utilisant différentes chaînes de numérotation :

```
SIP/peer
```

- ; Besoin d'avoir un pair défini dans sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Les exemples incluent :

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrer un système chan_sip hérité vers PJSIP

Parce que `chan_sip` a été supprimé dans Asterisk 21 et est absent dans Asterisk 22, tout déploiement `sip.conf` existant doit être migré vers PJSIP. Le plus grand changement conceptuel est qu'un seul bloc `sip.conf` `[peer]` ou `[friend]` est divisé en plusieurs objets PJSIP, chacun avec un `type=` : un **endpoint** (paramètres d'appel/codec/média), un ou plusieurs objets **aor** (où l'appareil peut être atteint / enregistrement), un objet **auth** (informations d'identification), et un **transport** partagé (le socket d'écoute, adresses NAT). Le tableau suivant mappe les concepts les plus courants.

| Concept sip.conf hérité | Équivalent PJSIP (pjsip.conf) |
| --- | --- |
| Bloc `[peer]` / `[friend]` | `type=endpoint` + `type=aor` + `type=auth` (référencé via `auth=` et `aors=`) |
| `type=friend` / `type=peer` / `type=user` | un seul `type=endpoint` (PJSIP n'a pas de distinction ami/pair/utilisateur) |
| `host=dynamic` (l'appareil s'enregistre) | `type=aor` avec `max_contacts=1` ; l'appareil REGISTER pour mettre à jour son contact |
| `host=<ip/hostname>` (statique) | `type=aor` avec un `contact=sip:host:port` statique |
| `register=>user:secret@host/ext` (sortant) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` sur l'endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` sur l'endpoint (même syntaxe) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — aussi `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` sur l'endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (secondes) sur l'**aor** |
| `externaddr=` | `external_media_address=` et `external_signaling_address=` sur le **transport** |
| `localnet=` | `local_net=` sur le **transport** |
| `insecure=invite` (fournisseur, pas d'auth) | omettez `auth=`/`outbound_auth=` et utilisez `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (à utiliser avec précaution) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (et `cos_audio` / `cos_video`) sur l'endpoint |

Une extension d'enregistrement qui ressemblait à ceci dans le `sip.conf` hérité :

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

devient ce qui suit dans `pjsip.conf` sur Asterisk 22 :

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### Le script de conversion sip_to_pjsip.py

Asterisk livre un script d'assistance, **`sip_to_pjsip.py`**, qui lit un `sip.conf` existant et produit un `pjsip.conf`. Vous pouvez l'exécuter directement dans le répertoire /etc/asterisk. L'utilitaire se trouve dans l'arborescence source d'Asterisk sous `contrib/scripts/sip_to_pjsip/`, où `${PATH_TO_ASTERISK_SOURCE}` est le chemin où les fichiers source d'Asterisk sont trouvés (généralement /usr/src/asterisk-22.x.y/) :

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Si vous l'exécutez avec l'option `--help`, vous verrez ses options :

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

Il accepte également des arguments positionnels optionnels — `[input-file [output-file]]`, par défaut `sip.conf` et `pjsip.conf` dans le répertoire actuel.

Traitez sa sortie comme un **point de départ** : examinez chaque objet généré, en particulier les transports, les paramètres NAT et les listes de codecs, et testez minutieusement avant de passer en production.

Migrons le sip.conf dans nos laboratoires compagnons au VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.api4com.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.api4com.com
fromuser=1020
fromdomain=sip.api4com.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.api4com.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.api4com.com
client_uri = sip:1020@sip.api4com.com:5600
server_uri = sip:sip.api4com.com:5600
[auth_reg_sip.api4com.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.api4com.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.api4com.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.api4com.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

Bien que la conversion semble correcte, nous pouvons voir que certains éléments tels que qualify=yes ne peuvent pas être mappés directement. Pour corriger, vous devez ajouter à la section aor la commande qualify_frequency=time en secondes. Exemple ci-dessous.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

La configuration PJSIP complète est couverte dans le chapitre *SIP & PJSIP en profondeur*, et la documentation officielle sur docs.asterisk.org a une couverture complète du canal. Dans nos laboratoires compagnons sur voip.school, le laboratoire 5 vous permet de pratiquer ce que vous venez d'apprendre.

## Quiz

1. Concernant les deux interfaces analogiques Foreign eXchange, marquez les déclarations correctes (choisissez tout ce qui s'applique) :
   - A. Une interface FXO se connecte au central du réseau téléphonique public commuté (PSTN) et en tire la tonalité.
   - B. Une interface FXS fournit la tonalité et l'alimentation de sonnerie à un téléphone, fax ou modem analogique standard.
   - C. Une interface FXS est le bon moyen de connecter Asterisk à une ligne télécom.
   - D. Une interface FXO peut également être connectée à un port d'extension d'un PBX hérité.
2. La signalisation de supervision sur une ligne analogique inclut laquelle des suivantes (choisissez tout ce qui s'applique) ?
   - A. On-hook
   - B. Off-hook
   - C. Sonnerie
   - D. DTMF
3. L'écho, les pops et le bruit sur une carte analogique DAHDI sont le plus souvent causés par :
   - A. La façon dont Asterisk a été compilé
   - B. Des conflits d'interruptions PCI
   - C. Un codec SIP incorrect
   - D. Un dialplan manquant
4. Pour une facturation précise sur les canaux analogiques, vous devez détecter exactement quand l'extrémité distante répond. Quelle fonctionnalité activez-vous sur Asterisk (et demandez-vous au telco) pour faire cela ?
   - A. Inversion de réponse
   - B. Inversion de facturation
   - C. Inversion de polarité
   - D. Génération de tonalité
5. Le matériel DAHDI est indépendant d'Asterisk : la carte physique est configurée dans `/etc/dahdi/system.conf`, tandis que `chan_dahdi.conf` définit les canaux Asterisk, pas le matériel lui-même.
   - A. Vrai
   - B. Faux
6. Concernant la capacité et la signalisation des trunks numériques, marquez les déclarations correctes (choisissez tout ce qui s'applique) :
   - A. Un trunk E1 transporte 30 canaux vocaux et un trunk T1 en transporte 24.
   - B. Un ISDN PRI utilise 30B+D sur un E1 et 23B+D sur un T1.
   - C. ISDN est un exemple de signalisation CCS, tandis que MFC/R2 est un exemple de signalisation CAS.
   - D. T1 est le trunk numérique le plus couramment utilisé en Europe et en Amérique latine.
7. Quel utilitaire détecte automatiquement les cartes DAHDI et génère `/etc/dahdi/system.conf` et `dahdi-channels.conf` ?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. Lors de la migration d'un `sip.conf` `[friend]` hérité vers PJSIP, un seul bloc doit être divisé en plusieurs objets. Quel ensemble d'objets PJSIP `type=` remplace normalement un `[friend]` d'enregistrement ?
   - A. `type=endpoint`, `type=aor`, et `type=auth`
   - B. `type=peer` et `type=user`
   - C. `type=sip` seulement
   - D. `type=channel` et `type=device`
9. Quel est l'avantage pratique principal de l'utilisation du mode trunk IAX2 entre deux serveurs Asterisk ?
   - A. Il chiffre chaque appel avec TLS par défaut
   - B. Il transporte plusieurs appels sous un seul en-tête, économisant de la bande passante
   - C. Il supprime le besoin de tout codec
   - D. Il alloue un port UDP séparé par appel pour une meilleure qualité
10. Les clés RSA peuvent être utilisées pour l'authentification IAX2. Quelle clé devez-vous garder secrète, et laquelle donnez-vous à l'autre serveur ?
    - A. Gardez la clé publique secrète ; partagez la clé privée
    - B. Gardez la clé privée secrète ; partagez la clé publique
    - C. Gardez la clé partagée secrète ; partagez la clé privée
    - D. Les deux clés doivent être partagées

**Réponses :** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
