# Legacy channels: analog, TDM & IAX2

Dans un monde purement VoIP en 2026, les types de canaux présentés dans ce chapitre sont de plus en plus rares : la plupart des nouvelles implémentations utilisent des trunks SIP et des endpoints PJSIP sur Ethernet, sans aucun matériel téléphonique. Asterisk 22 prend néanmoins toujours en charge la plupart d’entre eux de façon complète. La connectivité analogique (FXO/FXS) et numérique TDM (E1/T1/ISDN PRI/BRI) est fournie via DAHDI — la pile de pilotes initialement développée par Digium, rachetée par Sangoma en 2018, après que les pilotes Zaptel aient été renommés suite à un litige de marque. La connectivité serveur‑à‑serveur via IAX2 est assurée par `chan_iax2`, qui est toujours fourni et supporté mais constitue désormais un protocole hérité.

Ce chapitre rassemble également le matériel **legacy SIP** : l’ancien pilote `chan_sip` et sa configuration `sip.conf` — supprimés dans Asterisk 21 et disparus dans Asterisk 22 — ainsi qu’un guide complet pour migrer un système `sip.conf` existant vers PJSIP. Si vous exploitez un environnement pure‑SIP sur PJSIP sans cartes téléphoniques, sans trunks IAX2 et sans legacy `sip.conf` à convertir, vous pouvez ignorer ce chapitre en toute sécurité.

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk to analog lines and phones with FXO/FXS interfaces through DAHDI;
- Recognize digital TDM connectivity (E1/T1, ISDN PRI/BRI) and how it is configured;
- Configure IAX2 (`chan_iax2`) for server-to-server trunks and understand why it is now legacy;
- Identify the retired `chan_sip` driver and the `sip.conf` syntax you may still encounter; and
- Migrate an existing `chan_sip`/`sip.conf` system to PJSIP.

## Analog channels (FXO/FXS)

As of Asterisk 22, DAHDI and analog telephony cards remain fully supported, and DAHDI still builds against current kernels. The majority of new deployments are nonetheless pure VoIP (SIP trunks, PJSIP), so analog/TDM hardware is now a niche choice — found mainly in legacy environments, rural PSTN connectivity, or regulated markets. Everything below still applies to those scenarios.

There are several ways to connect the public switched telephone network (PSTN). The best way depends on how the telephone company makes this connection available in your area. The simplest way is to use an analog line, similar to the line you use at home. In this section, we will show you how to configure analog cards from Sangoma™ (formerly Digium™) and Xorcom™.

### Objectives

By the end of this chapter you should be able to:

- Recognize the main telephony terms and acronyms;
- Understand when to use digital and analog circuits;
- Recognize the difference between FXS and FXO; and
- Configure Asterisk for FXS and FXO.

### Telephony basics

Most analog implementations use a pair of cooper lines named tip and ring. When a loop is closed, the phone receives the dial tone from the telecom switch (or the private PBX). The most frequently used signaling is loop-start; other, less common kinds of signaling including ground start, which is used in several countries. The three categories of signaling are:

- Supervision signaling
- Address signaling
- Information signaling

#### Supervision signaling

The main supervision signalings are on-hook, off-hook, and ringing.

- **On-Hook** – When a user puts the phone on the hook, the PBX interrupts and does not allow the electric current to pass. In this state, the circuit is named on-hook. In this position, only the ringer is active.
- **Off-Hook** – Before starting a phone call, the phone needs to pass to the off-hook state. Removing the handset from the hook closes the loop and indicates to the PBX that the user intends to make a call. Upon receiving this indication, the PBX generates a dial tone, indicating to the user that it is ready to accept the destination address (i.e., phone number).
- **Ringing** – When a user calls another phone, it generates a voltage to the ringer that warns the other user about a call being received. Signaling varies by country, with different tones for different countries.

You can personalize Asterisk tones to your country by modifying the indications.conf file. For example:

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

Vous pouvez utiliser deux types de signalisation pour composer. Le premier et le plus courant est la double tonalité multi‑fréquence (dtmf) tandis que l’autre est la numérotation à impulsions (utilisée sur les anciens téléphones à cadran rotatif). Les téléphones disposent d’un clavier de numérotation, et chaque touche est associée à deux fréquences : une haute et une basse. Dans le cas de la signalisation dtmf, la combinaison de ces tons indique le chiffre pressé. MFC/R2 utilise un ton multi‑fréquence différent du dtmf.

#### Signalisation d'information

Le signalement d'information indique la progression de l’appel et les différents événements.

- Ton de numérotation
- Ton occupé
- Sonnerie d'appel
- Congestion
- Numéro invalide
- Ton de confirmation

### Interfaces PSTN

Comme dans le cas des anciens PBX, il est souvent nécessaire de connecter le Asterisk PBX au PSTN. Ici nous vous montrerons comment le faire. En général, vous avez trois options pour les lignes téléphoniques.

- Analog : La forme la plus courante pour les foyers et les petites entreprises, généralement fournie avec une paire métallique de lignes en cuivre.  
- Digital : Utilisée lorsque de nombreuses lignes sont nécessaires. Une ligne numérique est généralement fournie par un CSU/DSU ou un multiplexeur fibre. Le connecteur de l'utilisateur final est généralement un RJ45. Dans certains pays, les lignes E1 sont livrées à l'aide de deux connecteurs coaxiaux BNC ; dans ce cas, vous aurez besoin d'un adaptateur pour connecter la prise RJ45 à la carte téléphonique.  
- SIP : Cette option a été développée récemment. La ligne téléphonique est fournie via une connexion de données avec signalisation SIP (VoIP). C’est une bonne option à utiliser avec Asterisk puisque vous n’aurez pas besoin d’acheter une carte téléphonique. Les appels téléphoniques seront livrés directement au port Ethernet. Un autre avantage est que vous pourriez libérer des ressources de votre CPU en évitant la transcodification des codecs.

### Interfaces analogiques FXS, FXO et E&M interfaces

Plusieurs types d'interfaces analogiques sont disponibles. Il est fondamental de comprendre les différences entre ces interfaces pour apprendre comment se connecter au réseau téléphonique ainsi qu'à d'autres PBX. Ici, nous vous présenterons l'interface E&M. Bien qu'elle ne soit pas actuellement disponible pour Asterisk et qu'elle ait été abandonnée par plusieurs fournisseurs, vous pouvez rencontrer des routeurs et des PBX dotés de ce type d'interface, il est donc préférable de savoir à quoi vous avez affaire.

#### Interfaces d'échange étranger (FX)

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![Asterisk entre un téléphone analogique (FXS) et la ligne télécom (FXO) : le côté FXS fournit le ton de numérotation et la sonnerie au téléphone, tandis que le côté FXO prélève le ton de numérotation du central.](../images/10-legacy-fig01.png)

L'interface FXO est utilisée pour se connecter à un central téléphonique (CO) ou à l'extension d'un autre PBX. Elle communique directement avec une ligne téléphonique provenant du PSTN. Une autre option consiste à connecter l'interface FXO à un PBX existant, permettant la communication entre Asterisk et le PBX hérité. Connecter Asterisk à un port PBX et fournir une extension distante via VoIP est souvent appelé une extension hors promesse (OPX). Une interface FXO reçoit un signal de tonalité. 

Station d'échange étrangère (FXS)  
L'interface FXS alimente un téléphone analogique, un modem ou un fax. Le FXS fournit la tonalité de numérotation et l'alimentation pour un téléphone.

#### Signalisation du trunk

- Loop-Start
- Ground-Start
- Kewlstart

L'utilisation du signalement kewlstart dans Asterisk est presque par défaut. Kewlstart n'est pas un signalement en soi, mais ajoute de l'intelligence au circuit en surveillant ce qui se passe de l'autre côté. Kewlstart est basé sur le loop-start. La plupart des commutateurs ne prennent pas en charge cette fonctionnalité, qui est utilisée pour obtenir la notification de raccrochage.

- Loopstart : Utilisé sur la plupart des lignes analogiques, il permet au téléphone d'indiquer « on-hook » et « off-hook » et au commutateur d'indiquer « ring » et « no-ring ». C’est probablement ce que la plupart des gens ont à la maison. Le nom vient du fait que la ligne est toujours ouverte. Lorsque vous fermez la boucle, le commutateur vous fournit un ton de numérotation. Un appel entrant est signalé par une tension de sonnerie de 100 V sur la paire ouverte.

![Asterisk fonctionnant comme une passerelle VoIP : un port FXO se connecte à une extension PBX héritée tandis qu’un Asterisk distant délivre cette ligne à un téléphone analogique via IP à travers un port FXS (une extension hors site, ou OPX).](../images/10-legacy-fig02.png)

- Groundstart : similaire à Loopstart. Lorsque vous souhaitez passer un appel, une extrémité de la ligne est court‑circuitée. Lorsque le commutateur identifie cet état, il inverse la tension à travers la paire ouverte, puis la boucle se ferme. En conséquence, la ligne devient d'abord occupée avant d'être proposée à l'appelant.  
- Kewlstart : ajoute de l'intelligence aux circuits, permettant la surveillance de l'autre côté. Kewlstart intègre de nombreux avantages du loop‑start.

### Configuration des canaux téléphoniques Asterisk

Pour configurer une carte d'interface téléphonique, plusieurs étapes sont nécessaires. Dans ce chapitre, nous présenterons trois des scénarios les plus courants :

- Connexion analogique utilisant FXS
- Connexion analogique utilisant FXO
- Connexion d'un Astribank™ avec des interfaces FXS et FXO

### Procédure de configuration (valide dans les deux cas)

Avant de choisir le matériel pour Asterisk, vous devez prendre en compte le nombre d’appels simultanés, les services et les codecs qui seront installés et activés. Asterisk est une application gourmande en CPU, c’est pourquoi nous recommandons une machine dédiée à Asterisk. Le nombre de cartes d’interface installées dans l’ordinateur est limité par le nombre de slots et d’interruptions disponibles. Il est préférable d’installer une seule carte avec huit interfaces vocales plutôt que deux cartes avec quatre. Une autre option consiste à utiliser une banque de canaux USB, telle que le Xorcom Astribank. Récemment, certains fabricants (par exemple, CIANET) ont commencé à produire des banques de canaux TDMoE, ce qui facilite encore davantage la connexion de dizaines d’interfaces analogiques.

![A Xorcom Astribank : une banque de canaux USB 19 pouces en montage rack qui expose des dizaines de ports FXS/FXO (ici une unité de 32 ports) sans occuper de slots PCI dans l'hôte.](../images/10-legacy-fig03.png)

#### Exemple 1 : Installation d'un FXO et d'un FXS

Dans cet exemple, nous utiliserons une carte d'interface téléphonique Sangoma TDM400 (vendue auparavant sous le nom Digium TDM400) avec un module FXS et un module FXO. Les étapes requises sont listées ci‑dessous:

1. Installez la carte analogique FXS, FXO, ou les deux.  
2. Configurez le fichier `/etc/dahdi/system.conf` (anciennement `/etc/zaptel.conf`).  
3. Générez les fichiers de configuration en utilisant `dahdi_genconf`.  
4. Chargez le pilote pour l'interface DAHDI.  
5. Exécutez `dahdi_test` pour vérifier les pertes d'interruption.  
6. Exécutez `dahdi_cfg` pour configurer le pilote.  
7. Configurez le canal DAHDI dans le fichier `chan_dahdi.conf`, puis chargez Asterisk.

##### Étape 1 : Installer la carte TDM400

La carte TDM404P contient des modules FXS et FXO. Connectez les modules FXS (S110M, vert) et FXO (X100M, rouge). Si vous utilisez des modules FXS, branchez la carte directement à la source d’alimentation à l’aide d’un connecteur molex. Veuillez porter une protection antistatique avant de manipuler les cartes d’interface afin d’éviter d’endommager le matériel. Les cartes analogiques Sangoma (anciennement Digium) prennent également en charge un module matériel d’annulation d’écho VPMADT032.

##### Étape 2 : Générer la configuration avec dahdi_genconf

La bonne nouvelle concernant la configuration est le nouvel utilitaire `dahdi_genconf`, qui détecte automatiquement et génère la configuration pour les interfaces DAHDI. L'utilitaire génère deux fichiers:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (avec l'option `users`)
- Tous ces fichiers utilisent l'option `chan_dahdi full`

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![Une carte analogique Sangoma/Digium TDM404P : jusqu'à quatre modules FXS ou FXO se branchent sur les ports numérotés, avec une carte fille optionnelle d'annulation d'écho matérielle et un connecteur d'alimentation dédié de 12 V pour les modules FXS.](../images/10-legacy-fig04.png)

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

Le fichier `genconf_parameters` vous permet de personnaliser votre configuration. Les paramètres les plus importants pour les lignes analogiques sont :

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

Warning: Il est obligatoire de configurer au moins l'algorithme d'annulation d'écho pour les canaux. Le paramètre base_exten définit le plan de numérotation de base pour les extensions FXS. Dans ce cas, le premier canal FXS recevra le numéro d'extension 4000, le deuxième 4001, etc. Le contexte dans lequel les lignes (context_phones) et les trunks (context_lines) sont créés est très important. Après avoir généré les fichiers, vous devez inclure le fichier `/etc/asterisk/dahdi-channels.conf` dans le fichier `/etc/asterisk/chan_dahdi.conf`.

```
#include dahdi-channels.conf
```

Note : Le signalement analogique est un peu déroutant ; il est toujours l’inverse de la carte. Les cartes FXS sont signalées avec FXO tandis que les cartes FXO sont signalées avec FXS. Asterisk communique avec ces appareils comme s’il était du côté opposé.

##### Étape 3 : Charger les pilotes du noyau

Vous devez maintenant charger le module chan_dahdi et le pilote de carte du noyau correspondant. Utilisez dahdi_hardware pour détecter votre carte et le nom du pilote. Par exemple :

| Card | Driver | Description |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - PCI 3,3 V |
| TE405P | wct4xxp | 4xE1/T1 - PCI 5 V |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### Étape 4 : Utiliser l’utilitaire dahdi_test

Un utilitaire important est dahdi_test, qui sert à vérifier les pertes d’interruptions sur la carte DAHDI. Les problèmes de qualité audio sont souvent liés à des conflits d’interruptions. Pour vérifier que votre carte DAHDI ne partage pas d’interruption avec d’autres cartes, utilisez la commande suivante :

```
#cat /proc/interrupts
```

Vous pouvez vérifier le nombre de pertes d’interruption à l’aide de l’utilitaire dahdi_test compilé avec les cartes DAHDI. Un pourcentage inférieur à 99,987 % indique des problèmes possibles.

##### Étape 5 : Utiliser l’utilitaire dahdi_cfg pour configurer le pilote

DAHDI possède un système inhabituel pour charger les pilotes. Commencez par configurer le fichier /etc/dahdi/system.conf, puis appliquez ces configurations au pilote DAHDI à l’aide de dahdi_cfg. Dans ce cas, dahdi_cfg est utilisé pour configurer la signalisation des interfaces FX. Pour voir les résultats, vous pouvez ajouter « -vvvvv » à la commande pour un mode verbeux.

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

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Étape 6 : Configurer le fichier /etc/asterisk/chan_dahdi.conf

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

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

Plusieurs options sont disponibles dans le fichier chan_dahdi.conf. Une description de toutes les options serait ennuyeuse et contre‑productive ; à la place, nous nous concentrerons sur les principaux groupes d’options disponibles pour une compréhension facile.

#### Options générales (indépendantes du canal)

Ces options fonctionnent pour n’importe quel canal : context : Définit le contexte entrant.

```
context=default
```

channel: Définit un canal ou une plage de canaux. Chaque définition de canal héritera des options définies avant la déclaration. Les canaux peuvent être identifiés individuellement ou sur la même ligne par séparation par des virgules. Les plages peuvent être définies en utilisant « - ».

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permet de gérer les canaux comme un groupe. Si vous composez un numéro de groupe au lieu d’un numéro de canal, le premier canal disponible est utilisé. Si les canaux sont des téléphones, appeler un groupe fait sonner tous les téléphones simultanément. Avec des virgules, vous pouvez spécifier plus d’un groupe pour le même canal.

```
group=1
group=3,5
```

language : Active l’internationalisation et configure une langue. Cette fonctionnalité configurera les messages système pour une langue spécifique. L’anglais est la seule langue dont les invites sont complètes via l’installation standard. musiconhold : Sélectionne la classe de musique d’attente.

#### Options d’identification de l’appelant

Il existe de nombreuses options d’identification de l’appelant. Certaines peuvent être désactivées, bien que la plupart soient activées par défaut. usecallerid : Active ou désactive la transmission de l’identification de l’appelant pour les canaux suivants (Oui/Non). Note : Si votre système sonne deux fois avant de répondre, essayez de désactiver cette fonction. Le système devrait répondre immédiatement. hidecallerid : Définit s’il faut masquer ou non l’identifiant de l’appelant sortant (Oui/Non). callerid : Configure une chaîne d’identification de l’appelant pour un canal spécifique. L’appelant peut être configuré avec asreceived. Cela est principalement utilisé dans les interfaces de trunk pour indiquer l’identifiant de l’appelant entrant.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Prend en charge l’identifiant d’appel pendant la mise en attente.  
useincomingcalleridondahditransfer: Utilise l’identifiant d’appel entrant lors d’un transfert.

#### Mise en attente

Asterisk prend en charge la mise en attente des appels sur les canaux FXS. L'utilisateur recevra un ton d'attente si quelqu'un sonne l'extension. Pour activer la mise en attente:

```
callwaiting=yes
```

Pour prendre en charge l’identifiant de l’appelant en attente d’appel :

```
callwaitingcallerid=yes
```

#### Options de qualité audio

Ajuster l'annulation d'écho est à la fois technique et artistique. Ces options modifient certains paramètres d'Asterisk qui influent sur la qualité audio dans les canaux DAHDI. Elles peuvent aider à améliorer la qualité audio sur les interfaces analogiques.

#### L'utilitaire fxotune

Le fxotune est un utilitaire utilisé pour affiner certains paramètres des modules FXO. Cet ajustement fin est nécessaire pour corriger le désalignement d’impédance causé par le hybride. L'utilitaire propose trois modes de fonctionnement :

- Detection (-i) : détecte et corrige les canaux FXO existants et enregistre la configuration vers

```
fxotune.conf
```

- Mode vidage (-d) : génère les fichiers d’onde vers fxotune_dump.vals
- Mode démarrage (-s) : lit le fichier fxotune.conf et l’applique aux modules FXO

Il est important de comprendre que vous devrez insérer l’instruction fxotune –s dans le chargement du système avant de démarrer Asterisk.

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Echo cancellation

La plupart des algorithmes d'annulation d'écho fonctionnent en générant plusieurs copies du signal reçu, chacune étant retardée d'une durée spécifique. Le nombre de taps du filtre détermine la taille du retard d'écho qui doit être annulé. Ces copies retardées sont ensuite ajustées et soustraites du signal reçu. L'astuce consiste à ajuster uniquement le signal retardé pour supprimer l'écho sans consommer trop de cycles CPU. Du point de vue de l'utilisateur, il est important de choisir un algorithme d'annulation d'écho approprié. Le défaut est MG2 ; cependant, deux autres options sont disponibles : le High Performance Echo Cancellation (HPEC) de Sangoma (anciennement Digium) et l'annulation d'écho open‑source (OSLEC) développée par David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) a été intégré au noyau Linux — il se trouve dans la zone `drivers/staging/echo` du noyau — et DAHDI est compilé contre celui‑ci plutôt que de fournir un téléchargement séparé. Pour changer l'algorithme d'annulation d'écho, définissez le paramètre `echo_can` dans `/etc/dahdi/system.conf`. Par exemple:

```
echo_can=oslec
```

La suppression d'écho dans Asterisk est contrôlée par trois paramètres dans le fichier /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel** : Désactive ou active l’annulation d’écho. Vous devez garder cette fonction activée. Elle accepte « yes » ou le nombre de taps. (Explication : comment fonctionne l’annulation d’écho ? La plupart des algorithmes d’annulation d’écho fonctionnent en générant plusieurs copies d’un signal reçu, chacune étant retardée d’un petit intervalle. Ce petit flux s’appelle un « tap ». Le nombre de taps détermine le délai d’écho qui peut être annulé. Ces copies sont retardées, ajustées et soustraites du signal original. L’astuce consiste à ajuster le signal retardé exactement comme il faut pour supprimer l’écho.)
- **echocancelwhenbridged** : Active ou désactive l’annulateur d’écho pendant un appel TDM pur. Cela n’est généralement pas nécessaire.
- **rxgain** : Ajuste le gain de réception audio pour augmenter ou diminuer le volume de réception (‑100 % à 100 %).
- **txgain** : Ajuste le gain de transmission audio pour augmenter ou diminuer le volume de transmission (‑100 % à 100 %).  

Par exemple :

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Options de facturation

These options change how call information is recorded in the call detail records (CDR) database. amaflags: Configures the AMA flags affecting the CDR categorization. It accepts the following values:

- billing
- documentation
- omit
- default

accountcode: Configures an account code for a specific channel. It can contain any alphanumeric value—usually the department or user name.

```
accountcode=finance
amaflags=billing
```

### Options de progression d'appel

Ces éléments sont utilisés pour obtenir des informations sur la progression de l'appel. Dans les interfaces publiques, il peut être utile de détecter la progression de l'appel et de déterminer s'il a été répondu ou occupé. La détection d'occupation est très expérimentale et régulée par des paramètres spécifiques.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Ces paramètres (ci‑dessus) indiquent si l’interface doit tenter de détecter le ton occupé, combien de tons seront utilisés pour une détection réussie, et quel est le motif d’occupation. La détection d’occupation est largement expérimentale, et certains paramètres supplémentaires peuvent être modifiés dans le Makefile. Pour détecter la réponse d’un appel, ce qui est essentiel pour une facturation précise, il est possible d’utiliser l’inversion de polarité afin de signaler le moment exact de la réponse. Cela est important si vous prévoyez de facturer l’appel ou simplement de disposer d’une facturation précise à des fins de comparaison. En général, vous devez contacter l’opérateur téléphonique pour demander ce service.

```
answeronpolarityswitch=yes
```

Dans certains pays, il est possible de détecter la fin de l'appel en utilisant l'inversion de polarité également.

```
hanguponpolarityswitch=yes
```

#### Options for phones

These options are used for phones connected to the FXS interfaces. All the functionalities delivered to analog phones connected directly to the DAHDI interfaces are controlled by Asterisk.

- **adsi** (Analog Display Services Interface) : Il s’agit d’un ensemble de normes télécom utilisées par certains opérateurs pour offrir des services tels que l’achat de billets.
- **cancallforward** : Active ou désactive le renvoi d’appel (*72 pour activer et *73 pour désactiver).
- **calleridcallwaiting** : Active l’affichage du callerid pendant une indication d’appel en attente (Oui/Non).
- **immediate** : En mode immédiat, au lieu de fournir un ton de numérotation, le canal saute immédiatement vers l’extension « s » dans le contexte défini. Ceci est utilisé pour créer des lignes directes.
- **threewaycalling** : Active ou désactive la conférence à trois.
- **mailbox** : Avertit l’utilisateur de la présence de messages de voicemail disponibles. Cela peut être un signal sonore ou un indicateur visuel (si le téléphone supporte cette fonction). L’argument est le numéro de la boîte vocale.
- **callgroup** : Regroupe les téléphones pour composer ou récupérer un appel.
- **pickupgroup** : Groupe de téléphones pour le pickup d’appel.

### Useful DAHDI CLI commands

Once Asterisk is running with DAHDI channels loaded, you can inspect channel status from the Asterisk CLI. These commands remain current in Asterisk 22:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### Format de canal DAHDI

Les canaux DAHDI utilisent le format suivant dans le dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Par exemple :

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Canaux numériques (E1/T1/PRI / TDM)

À partir d'Asterisk 22, DAHDI et libpri restent entièrement pris en charge, mais les trunks numériques TDM (E1/T1/ISDN PRI) sont de plus en plus remplacés par des trunks SIP dans les nouvelles implémentations. Cette section reste entièrement applicable lorsque la connectivité TDM est requise ; dans les environnements greenfield, le trunking SIP (Chapter 3) fournit généralement la même densité de canaux sans matériel téléphonique.

Les canaux numériques sont extrêmement courants, vous devrez donc apprendre à les mettre en œuvre si vous souhaitez vous concentrer sur les gros clients. Lorsque le nombre de canaux est élevé — généralement plus de 8 — il est assez fréquent d'utiliser des interfaces numériques telles que T1/E1/J1. Le T1 est très répandu aux États‑Unis, tandis que l'E1 l'est en Europe et le J1 au Japon. Ces types de canaux permettent une bonne densité de circuits — 24 par canal T1 et 30 pour les canaux E1.

En Amérique latine, en Chine et en Afrique, il est courant d'utiliser un type de signalisation associée aux canaux (CAS) appelé MFC/R2. Ce chapitre examinera comment implémenter MFC/R2 en utilisant la bibliothèque OpenR2. Aux États‑Unis et en Europe, le Réseau Numérique à Services Intégrés (ISDN) PRI est la signalisation la plus courante. Le chapitre abordera également l'Interface de Taux Bas ISDN (BRI), très répandue en Europe dans les applications de gamme moyenne.

Tous les exemples du livre se concentrent sur les canaux DAHDI. Certaines cartes sont implémentées à l'aide de canaux propriétaires, veuillez donc vérifier auprès de votre fabricant pour plus de détails sur la façon de configurer votre carte spécifique.

### Objectifs

À la fin de ce chapitre, vous serez capable de :

- Reconnaître les principaux termes utilisés en téléphonie numérique
- Différencier la signalisation CAS et CCS
- Différencier la signalisation R2 et ISDN
- Configurer les interfaces avec la signalisation ISDN
- Configurer les interfaces avec la signalisation R2

### Lignes numériques E1/T1

Les lignes numériques E1/T1 sont une option chaque fois que vous devez mettre en œuvre un grand nombre de canaux. Un seul circuit E1 peut gérer 30 appels simultanés, et vous pouvez disposer de fonctionnalités telles que le numérotation directe entrante (DID), l’identification de l’appelant (Caller ID) et la signalisation avancée. La ligne E1/T1 peut arriver dans votre entreprise de plusieurs manières en utilisant du câble à paires torsadées, de la fibre ou des micro-ondes, selon votre pays. Les lignes numériques sont livrées à votre entreprise via UTP, fibre ou micro-ondes. Des modems et des multiplexeurs (MUX) sont utilisés pour fournir la ligne physique. La connexion à une ligne T1 se fait toujours avec un connecteur RJ45. Cependant, les lignes E1 peuvent également être provisionnées en utilisant un BNC. Il est très important de connaître à l’avance le type de connecteur que vous allez recevoir, notamment pour les lignes E1. En général, tout l’équipement jusqu’au RJ45 est fourni par le TELCO.

![Comment les circuits E1/T1 sont provisionnés : le telco peut fournir le trunk via cuivre UTP (modem HDSL pour E1, ou connexion directe par carte pour T1), via fibre optique à travers un multiplexeur optique, ou via un lien radio micro-ondes.](../images/10-legacy-fig05.png)

![UTP ou BNC ? La plupart des cartes numériques utilisent des connecteurs RJ45 (UTP), mais certaines lignes E1 sont fournies sur double coaxial BNC, auquel cas un balun est nécessaire pour adapter la paire coaxiale à la prise RJ45 de la carte.](../images/10-legacy-fig06.png)

#### Comment la voix est‑elle convertie en bits?

Le signal analogique est échantillonné 8 000 fois par seconde pour créer une version numérique de la voix analogique. Cette encodage est connue sous le nom de modulation par impulsions codées (PCM). Aux États‑Unis et au Japon, le signal est encodé en utilisant la loi (dans Asterisk, appelée ulaw). Dans le reste du monde, l’encodage est alaw.

![Modulation par impulsions codées (PCM) : le signal vocal analogique de 4 kHz est échantillonné 8 000 fois par seconde (Nyquist) et codé en un flux numérique de bits de 64 kbps.](../images/10-legacy-fig07.png)

#### Multiplexage par répartition dans le temps

Les lignes analogiques sont utiles lorsque vous avez besoin de seulement quelques canaux. Lors de l’utilisation du multiplexage à division de temps (TDM), il est possible d’empaqueter plusieurs canaux dans une seule connexion de données. Lorsque vous avez besoin d’un grand nombre de circuits, l’opérateur téléphonique vous fournira généralement un trunk numérique, qui est un circuit de données dans lequel la voix est transportée au format numérique à l’aide du PCM. Chaque créneau temporel utilise 64 Kbps de bande passante pour transporter un seul canal vocal.

![Multiplexage en temps partagé dans E1 et T1 : une trame E1 transporte 32 créneaux à 2048 kbps (DS0 #0 pour la synchronisation de trame, DS0 #16 pour la signalisation), tandis qu’une trame T1 transporte 24 créneaux à 1544 kbps en utilisant un bit pour la synchronisation et un schéma de bit volé pour la signalisation.](../images/10-legacy-fig08.png)

En États‑Unis, le trunk numérique le plus répandu est le T1, qui possède 24 lignes disponibles ; en Europe et en Amérique latine, les trunks E1 offrent 30 lignes. Certaines entreprises proposent un T1/E1 fractionné avec moins de canaux. **Robbed bit signaling**  
Parfois, un trunk T1 utilise un schéma de « robbed bit » où un bit est emprunté pour la signalisation. Sur les trunks T1, le canal données/voix est transmis à 56 Kbps sur chaque créneau temporel. Comme vous pouvez le constater, lorsque vous utilisez le robbed bit, le circuit T1 ne perd pas deux créneaux pour la synchronisation et la signalisation.

#### T1/E1 Code de ligne

Les T1 et E1 sont en fait des circuits de données et possèdent un codage de données qui détermine la façon dont les bits sont interprétés. Pour les E1, le code de ligne le plus courant est HDB3 pour la couche 1 et CCS pour la couche 2. La façon la plus simple de savoir comment votre trunk numérique est configuré est de demander cette information au TELCO. Vous aurez besoin de ces informations pour configurer le fichier /etc/dahdi/system.conf.

#### T1/E1 Signalisation

Il est important de comprendre que les lignes T1/E1 peuvent être livrées en utilisant différents types de signalisation, tels que :

- T1 avec signalisation robbed bit
- T1 avec signalisation ISDN
- E1 avec MFC/R2 (CAS - Signalisation associée au canal)
- E1 avec signalisation ISDN

L'ISDN est souvent utilisé en Europe et aux États-Unis. C’est un réseau vocal numérique, normalisé par l'Union internationale des télécommunications (UIT) en 1984. L'ISDN fournit deux types de canaux :

- Canaux porteurs
  - Voix
  - Données
- Canaux de données
  - Signalisation hors bande
  - Signalisation LAPD
  - Q.931

Habituellement, une ligne ISDN est fournie à l'aide de deux moyens physiques:

- Interface à débit de base (BRI)
  - Connu sous le nom de 2B+D
  - Deux canaux porteuse (64K) et un canal de données (16K)
  - Utilise une paire de fils de cuivre avec 148Kbps.
- Interface à débit principal (PRI)
  - Fourni via un T1/E1 trunk
  - 23B+D pour T1s
  - 30B+D pour E1s

Parfois, les circuits E1 utilisent un schéma de signalisation CAS appelé MFC/R2, qui a été défini par l'ITU comme une norme connue sous le nom de Q.421/Q441. On le trouve fréquemment en Amérique latine et en Asie. Plusieurs entreprises de téléphonie dans ces pays utilisent des variantes personnalisées de MFC/R2. Ainsi, vous devrez connaître la variante nationale correcte afin de le faire fonctionner.

### ISDN BRI

Les canaux utilisant la signalisation ISDN BRI sont très populaires en Europe. La plupart des cartes ISDN BRI pour Asterisk prennent en charge une interface S/T avec des capacités NT et TE. La connexion TE (terminal) est celle utilisée pour se connecter au TELCO ou à d’autres PBX configurés comme termination de réseau (NT). Le NT est utilisé pour connecter les téléphones et les PBX configurés comme TE. ISDN BRI fournit deux canaux de données/voix et un canal de signalisation. Les cartes ISDN BRI sont disponibles auprès de plusieurs fournisseurs de cartes d’interface pour Asterisk.

### Choisir une carte téléphonique pour votre serveur Asterisk

Il existe plusieurs fabricants de cartes numériques compatibles avec Asterisk. Le choix d’une carte dépend de certains des facteurs suivants :

#### Bus de données

Il existe plusieurs types de bus sur votre PC. Il est très important que vous disposiez de la bonne carte pour votre serveur. L'aperçu suivant décrit les cartes les plus fréquemment utilisées :

- 32 Bits PCI 5 V trouvés dans la plupart des ordinateurs, y compris les ordinateurs de bureau
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, et TC400
  - Sangoma A101, A102, et A104
- 32/64 bits PCI 3.3 V, essentiellement trouvés dans les serveurs
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, et TC400
- PCI Express trouvé sur les ordinateurs de bureau et les serveurs
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, et AEX800
  - Sangoma A101, A102, et A104

Ces familles de cartes proviennent de Digium, qui a été acquis par Sangoma en 2018 ; elles sont désormais vendues et prises en charge sous la marque Sangoma. Beaucoup des SKU plus anciens répertoriés ici ont été abandonnés, il faut donc vérifier la disponibilité actuelle des modèles sur www.sangoma.com avant d’acheter.

- MiniPCI trouvé sur les systèmes embarqués
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI) et B400M(ISDN BRI)
- USB 2.0 présent sur la plupart des PC modernes. Les solutions basées sur l’USB permettent une grande densité de canaux analogiques et numériques. Ce bus supporte 480 Mbps, et chaque canal vocal occupe 64 Kbps. En utilisant des hubs USB, il est possible d’atteindre des densités allant jusqu’à mille ports analogiques sur un seul port.
  - Xorcom Astribank (FXS, FXO, E1‑ISDN, E1‑R2)
- Ethernet. Le principal avantage de l’Ethernet est de permettre à la carte d’être connectée à plusieurs serveurs. Les solutions de haute disponibilité sont généralement l’application principale pour ces appareils. La force de cette solution réside dans l’utilisation de serveurs sans emplacements PCI libres ou de serveurs en lame.  
  - Redfone FoneBridge (jusqu’à quatre circuits E1)

### Utilisation de l'annulation d'écho matérielle

L'annulation d'écho matérielle réduit la charge du CPU hôte. Pour les cartes disposant de plus d'une interface E1, l'annulation d'écho matérielle peut aider à alléger votre processeur. Les nouveaux annulateurs d'écho logiciels améliorés tels que l'OSLEC réduisent le besoin d'un annulateur d'écho matériel. Pour choisir entre les annulateurs d'écho matériels et logiciels, vous devez prendre en compte la puissance de traitement disponible sur votre serveur et le nombre de circuits E1. Un processus d'annulation d'écho peut consommer jusqu'à neuf MIPS (millions d'instructions par seconde) par canal vocal avec 128 taps d'amplitude en utilisant l'OSLEC (Référence : Xorcom Ltd.). Si vous considérez 1 cycle CPU par instruction (ce qui n'est pas toujours exact selon le processeur et l'implémentation logicielle), nous parlons de 1,080 GHz pour quatre E1.

#### Type de signalisation

Sélectionner le type de signalisation (par exemple, T1 CAS, T1 PRI, E1 CAS R2 ou E1 CAS ISDN) n’est pas une tâche facile. Cela dépend vraiment de ce qui est disponible dans votre région et à quel prix. Le Common Channel Signaling (CCS) est souvent préférable à la signalisation associée au canal (CAS). Cependant, il n’est souvent pas disponible. Aux États‑Unis, vous pouvez généralement choisir, car la plupart des TELCOS proposent le T1 CAS pour les utilisateurs ordinaires et le T1 PRI pour les utilisateurs avancés (par exemple, les centres d’appels). En Amérique latine, le E1 CAS R2 est répandu, mais le ISDN PRI est disponible dans certaines villes.

![L'architecture logicielle DAHDI : Asterisk communique avec le pilote de canal `chan_dahdi`, qui charge à son tour les bibliothèques de protocole libpri (ISDN), libopenr2 (MFC/R2) et libss7 (SS7) ; celles‑ci reposent sur l'interface `/dev/dahdi`, le pilote noyau DAHDI et le pilote noyau d'interface spécifique à la carte.](../images/10-legacy-fig09.png)

Implémenter R2 est nécessaire pour installer une bibliothèque appelée OpenR2 (www.libopenr2.org), développée par Moises Silva, et pour patcher Asterisk avant l'installation — une procédure simple présentée plus loin dans ce chapitre. La bibliothèque a passé plusieurs tests et est en production chez plusieurs de nos clients. L’ISDN est, à mon avis, toujours le meilleur choix, si disponible. Certains fournisseurs peuvent avoir accès au système de signalisation 7 (SS7), qui est une signalisation CCS disponible entre les opérateurs téléphoniques. Des solutions propriétaires et open source sont disponibles pour le SS7. La bibliothèque libss7 est utilisée pour prendre en charge le SS7 sur Asterisk.

### Configuration des canaux téléphoniques Asterisk

Configurer une carte d'interface téléphonique implique plusieurs étapes nécessaires. Dans ce chapitre, nous présenterons trois des scénarios les plus courants :

- Connexion numérique utilisant ISDN PRI
- Connexion numérique utilisant ISDN BRI
- Connexion numérique utilisant MFC/R2

Il existe deux manières de configurer les canaux DAHDI. La première consiste à les configurer manuellement avec un contrôle complet de tous les paramètres. La seconde consiste à utiliser l’utilitaire dahdi_genconf pour détecter et configurer les cartes.

#### Détection automatique et configuration

Thanks to the DAHDI development team, we now have automatic detection and configuration of the cards. Step 1: To generate the configuration automatically, use the utility dahdi_genconf, which will detect the card and generate the files /etc/dahdi/system.conf and dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: In the last line of the file chan_dahdi.conf, include the file dahdi-channels.conf

```
#include dahdi_channels.conf
```

Étape 3 : Commentez tous les modules inutilisés dans le fichier modules ou utilisez simplement :

```
dahdi_genconf modules
```

#### Configuration manuelle

Une autre option consiste à configurer les interfaces manuellement. Vous trouverez ci‑dessous quelques exemples de configuration pour les canaux DAHDI.

##### Exemple #1 – Deux canaux T1/ E1 utilisant ISDN

Étapes requises :

1. Installation TE205P ou TE210P
2. `/etc/dahdi/system.conf` configuration du fichier
3. Chargement du pilote DAHDI
4. Utilitaire `dahdi_test`
5. Utilitaire `dahdi_cfg`
6. `chan_dahdi.conf` configuration du fichier
7. Chargement et test d’Asterisk

Étape 1 : Installation TE205P. Avant d’installer le TE205P, il est important de comprendre les différences entre les cartes TE205P et TE210P. La carte TE210P utilise un bus 64 bits alimenté en 3,3 volts que l’on trouve presque uniquement sur les cartes mères de serveurs. Soyez prudent si vous spécifiez cette carte d’interface ; assurez‑vous que votre matériel prend en charge un bus 64 bits, 3,3 V. La carte TE205P utilise un PCI 5 V, que l’on trouve souvent dans les ordinateurs de bureau. Nous avons choisi la carte d’interface TE205P à deux spans pour cet exemple parce qu’il est plus simple de la réduire à une carte à un span ou de l’étendre à une carte à quatre spans. Ces cartes sont maintenant commercialisées sous la marque Sangoma (anciennement Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

La configuration des cartes numériques TDM est légèrement différente de celle de leurs homologues analogiques. Tout d'abord, nous devrons configurer les spans de la carte puis les canaux. Les spans sont numérotés séquentiellement en fonction de l'ordre de reconnaissance des cartes. En d'autres termes, si vous avez plusieurs cartes d'interface, il est difficile de savoir à quel span appartient chaque carte. Utilisez dahdi_hardware pour vérifier quel matériel est installé sur chaque span. Exemple #1 (2xT1 PRI)

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

# Exemple #2 (2xE1 PRI)

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

Étape 3 : Chargement des pilotes du noyau Vérifiez quel pilote vous devez installer en utilisant dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Pour charger, utilisez :

```
modprobe dahdi
modprobe wct2xxp
```

Step 4: Using dahdi_test, check the missing interrupts  
You may verify the number of interrupt misses using the dahdi_test utility compiled with the DAHDI cards. A number below 99.987% indicates possible problems. You will find dahdi_test in

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

Étape 5 : Utilisation de l’utilitaire dahdi_cfg  
Voici la sortie correcte de dahdi_cfg pour un E1 fractionnel (15 ports) et deux ports FXO.

```
#./dahdi_cfg -vvvv
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

Étape 6 : Configuration de DAHDI dans le fichier /etc/asterisk/chan_dahdi.conf Exemple #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
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
callerid="Flavio Eduardo" <4830258580>
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

Utilisez signaling=bri_cpe_ptmp pour le BRI point à multipoint. Actuellement, le BRI point à multipoint n’est pas pris en charge en mode NT.

#### Chargement des pilotes du noyau

Après avoir configuré les pilotes, vous pouvez simplement redémarrer le serveur. Si vous avez installé DAHDI avec make config, vous n’aurez rien d’autre à faire. Le pilote du noyau sera chargé et configuré automatiquement. Cependant, il est parfois utile de charger et décharger les pilotes manuellement. Exemple :

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### Dépannage

Sometimes things don’t work the first time. Let’s check some resources for troubleshooting DAHDI. Step 1: Check if the card is being recognized by the operation system. Sangoma/Digium cards are usually recognized as the ISDN modem.

```
lspci -v
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

Étape 2 : Vérifiez que le pilote du noyau se charge correctement en utilisant :

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

Étape 3 : Vérifier l’état des alarmes liées à la couche physique de la connexion.  
Pour vérifier la couche physique de la connexion E1, vous pouvez utiliser la commande CLI Asterisk suivante.

```
dahdi show status
```

Les alarmes indiquent des problèmes avec le port : Alarme rouge : Impossible de maintenir la synchronisation avec le commutateur distant. Il s’agit généralement d’un problème physique, tel qu’un code de ligne ou un désalignement de trame. Alarme jaune : Signale que le commutateur distant est en alarme rouge. Cela indique que le commutateur distant ne reçoit pas vos transmissions. Alarme bleue : Reçoit uniquement des 1 non encadrés sur tous les créneaux ; dahdi_tool ne détecte actuellement pas d’alarme bleue. Boucle de retour : Le port est en boucle locale ou distante.

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Étape 4 : Pour détecter les problèmes avec DAHDI sur le serveur Asterisk, vérifiez d'abord si les canaux sont reconnus en utilisant :

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

Step 5: Vérifiez l’état de la couche 3 ISDN, également appelée q.931. Vous pouvez vérifier si la couche 3 ISDN est active en utilisant : `pri show spans` (pour lister toutes les liaisons) ou `pri show span <n>` pour une liaison spécifique :

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

Utilisez `pri show spans` (pluriel) pour lister le statut de toutes les liaisons PRI configurées en une fois.

Vérifiez un canal spécifique. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
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

debug pri span x : Si après tout vous avez encore des problèmes, commencez le débogage du pri span. Cette commande active un débogage détaillé des appels ISDN. C’est une commande importante lorsque vous pensez que quelque chose n’est pas correct. Vous pouvez détecter les chiffres composés incorrectement et d’autres problèmes. Ci‑dessous nous présentons un exemple de sortie de débogage pour un appel réussi. Référez‑vous à cet exemple si vous devez comparer un appel infructueux à un appel sans problème. Une astuce consiste à utiliser core set verbose=0 pour ne recevoir que les messages ISDN q.931.

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
> [a1]
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

Several options are available in the file chan_dahdi.conf. A description of all options would be boring and counterproductive. Here, we will detail the main option groups available to provide a better understanding.

#### Options générales (channel independent)

context: Defines the incoming context.

```
context=default
```

channel: Définit un canal ou une plage de canaux. Chaque définition de canal héritera des options définies avant la déclaration. Les canaux peuvent être identifiés individuellement ou sur la même ligne séparés par des virgules. Les plages peuvent être définies en utilisant “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Permet de traiter les canaux comme un groupe. Si vous composez un numéro de groupe au lieu d’un numéro de canal, le premier canal disponible est utilisé. Si les canaux sont des téléphones, lorsque vous appelez un groupe, tous les téléphones sonneront simultanément. En utilisant des virgules, vous pouvez spécifier plusieurs groupes pour le même canal.

```
group=1
group=3,5
```

language: Active l’internationalisation et configure une langue. Cette fonctionnalité configurera les messages système pour une langue spécifique. L’anglais est la seule langue dont les invites sont complètes dans l’installation standard. musiconhold: Sélectionner la classe de musique d’attente.

#### options ISDN

switchtype: Dépend du PBX ou du commutateur utilisé. En Europe et en Amérique latine, EuroISDN est courant.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Obligatoire pour certains commutateurs qui nécessitent une spécification du plan de numérotation. Cette option est ignorée par de nombreux commutateurs. Les options valides sont private, national, international et unknown.

```
pridialplan = unknown
```

prilocaldialplan : Nécessaire pour certains commutateurs, généralement inconnu.

```
prilocaldialplan = unknown
```

overlapdial : Le « overlap dialing » est utilisé lorsque vous transmettez des chiffres après l’établissement de la connexion. Vous pouvez utiliser le mode de numérotation bloc (overlapdial=no) ou le mode chiffre (overlapdial=yes). Le mode bloc est souvent utilisé par les opérateurs.  
signaling : Configure le type de signalisation pour les canaux suivants. Ces paramètres doivent correspondre à ceux du fichier chan_dahdi.conf. Les choix corrects dépendent du canal disponible. Pour l’ISDN vous pouvez choisir parmi cinq options :

- pri_cpe : Utilisé lorsque l’appareil est un CPE, parfois appelé client, utilisateur ou esclave. C’est la forme de signalisation la plus simple et la plus utilisée. Parfois, lorsque vous essayez de vous connecter à un PBX privé, le PBX a également été configuré comme CPE. Dans ce cas, utilisez la signalisation pri_net dans Asterisk.  
- pri_net : Utilisé lorsque Asterisk est connecté à un PBX privé configuré comme CPE. La signalisation est souvent désignée comme hôte, maître ou réseau.  
- bri_cpe : Utilisé lorsque Asterisk est connecté comme CPE à un trunk ISDN BRI  
- bri_net : Utilisé lorsque Asterisk est connecté à un téléphone ISDN ou à un PBX configuré comme terminal (TE).  
- bri_cpe_ptmp : Identique à bri_cpe, mais dans une architecture point‑à‑multipoint.  

#### Options CallerID

De nombreuses options d’identification d’appelant sont disponibles. Certaines peuvent être désactivées, bien que la plupart soient activées par défaut.  
usecallerid : Active ou désactive la transmission du Caller ID pour les canaux suivants (Yes/No). Note : Si votre système nécessite deux sonneries avant de répondre, essayez de désactiver cette fonction afin qu’il réponde immédiatement.  
hidecallerid : Masque le Caller ID (Yes/No).  
calleridcallwaiting : Active la réception du Caller ID pendant une indication d’appel en attente (Yes/No).  
callerid : Configure une chaîne Caller ID pour un canal spécifique. L’appelant peut être configuré avec “asreceived” dans les interfaces trunk pour transmettre le Caller ID en avant.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Note : La plupart des TELCO exigent que vous configuriez votre identifiant d’appel correct. Si vous ne transmettez pas le bon identifiant d’appel, vous ne devriez pas pouvoir composer vers l’extérieur via le TELCO. En revanche, vous pourrez recevoir des appels même sans configurer l’identifiant d’appel.

#### Options de qualité audio

Ces options ajustent certains paramètres d’Asterisk qui affectent la qualité audio dans les canaux DAHDI.

- **echocancel** : Désactiver ou activer l’annulation d’écho. Vous devez garder cette fonction activée. Elle accepte « yes » ou le nombre de taps. (Explication : Comment fonctionne l’annulation d’écho ? La plupart des algorithmes d’annulation d’écho fonctionnent en générant plusieurs copies d’un signal reçu, chacune étant retardée d’un petit intervalle. Ce petit flux est appelé « tap ». Le nombre de taps détermine le retard d’écho qui peut être annulé. Ces copies sont retardées, ajustées et soustraites du signal original. L’astuce consiste à ajuster le signal retardé exactement comme il faut pour supprimer l’écho.)
- **echocancelwhenbridged** : Active ou désactive l’annulateur d’écho pendant un appel TDM pur. Cela n’est généralement pas requis.
- **rxgain** : Ajuste le gain de réception audio pour augmenter ou diminuer le volume de réception (-100 % à 100 %).
- **txgain** : Ajuste le gain de transmission audio pour augmenter ou diminuer le volume de transmission (-100 % à 100 %).

Example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Options de facturation

Ces options modifient la façon dont les informations d'appel sont enregistrées dans la base de données des enregistrements détaillés des appels (CDR). amaflags : Influence la catégorisation du CDR. Il accepte les valeurs suivantes :

- billing
- documentation
- omit
- default

accountcode : Il configure un code de compte pour un canal spécifique. Il peut contenir n'importe quelle valeur alphanumérique, généralement le département ou le nom d'utilisateur.

```
accountcode=finance
amaflags=billing
```

### Configuration MFC/R2

MFC/R2 est utilisé dans plusieurs pays d'Amérique latine, en Chine et en Afrique ainsi que dans certains pays européens. L'ISDN est supérieur et préféré s'il est disponible dans votre région.

#### Comprendre le problème

La carte utilisée pour signaler MFC/R2 est la même que celle utilisée pour signaler l’ISDN. Il est possible d’utiliser MFC/R2 sur les canaux DAHDI en utilisant la bibliothèque appelée libopenR2 (www.libopenr2.com). Cette bibliothèque ne faisait pas partie des versions d’Asterisk antérieures à la 1.6.2.

##### Comprendre le protocole MFC/R2

Le protocole MFC/R2 combine la signalisation en bande et hors bande. La signalisation d'adresse est transmise en bande à l'aide d'un ensemble de tonalités tandis que les informations de canal sont transmises sur le créneau temporel 16 en tant que signalisation hors bande.

**Signalisation de ligne (ITU-T Q.421).** Dans le créneau 16, chaque canal vocal utilise quatre bits ABCD pour signaler ses états et le contrôle d’appel. Les bits C et D sont rarement utilisés. Dans certains pays, ils peuvent servir à la comptabilisation (comptage d’impulsions pour la facturation). Dans une conversation normale, les deux parties sont actives : l’appelant et le côté appelé. La signalisation depuis le côté appelant est appelée signalisation avant (forward signaling) tandis que le côté appelé utilise la signalisation arrière (backward signaling). Nous désignerons Af et Bf pour la signalisation avant et Ab et Bb pour la signalisation arrière.

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 a été défini par l'UIT. Malheureusement, plusieurs pays ont personnalisé la norme selon leurs propres besoins. En conséquence, des variations sont apparues dans les normes entre les pays.

**Signaux inter‑registres (ITU-T Q.441).** Le signalement MFC/R2 utilise une combinaison de deux tonalités. Les tableaux ci‑dessous montrent la norme ITU.

Groupe de signaux I (avant) :

| Description | Forward signal |
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
| Indicateur de code pays, suppressor de demi‑écho sortant requis | I-11 |
| Indicateur de code pays, aucun suppressor d'écho requis | I-12 |
| Indicateur d'appel de test | I-13 |
| Indicateur de code pays, suppressor de demi‑écho sortant inséré | I-14 |
| Non utilisé | I-15 |

Groupe de signaux II (avant) :

| Description | Forward signal |
| --- | --- |
| Abonné sans priorité | II-1 |
| Abonné avec priorité | II-2 |
| Équipement de maintenance | II-3 |
| Réserve | II-4 |
| Opérateur | II-5 |
| Transmission de données | II-6 |
| Abonné ou opérateur sans installation de transfert avant | II-7 |
| Transmission de données | II-8 |
| Abonné avec priorité | II-9 |
| Opérateur avec installation de transfert avant | II-10 |
| Réserve | II-11 |
| Réserve | II-12 |
| Réserve | II-13 |
| Réserve | II-14 |
| Réserve | II-15 |

Groupe de signaux A (en arrière):

| Description | Backward signal |
| --- | --- |
| Envoyer le chiffre suivant (n+1) | A-1 |
| Envoyer l'avant‑dernier chiffre (n-1) | A-2 |
| Adresse complète, basculement à la réception des signaux du groupe B | A-3 |
| Congestion du réseau national | A-4 |
| Envoyer la catégorie du correspondant appelant | A-5 |
| Adresse complète, facturation, mise en place des conditions de parole | A-6 |
| Envoyer le chiffre avant‑avant‑dernier (n-2) | A-7 |
| Envoyer le chiffre avant‑avant‑avant‑dernier (n-3) | A-8 |
| Réserve | A-9 |
| Réserve | A-10 |
| Envoyer l’indicateur du code pays | A-11 |
| Envoyer le chiffre de langue ou de discrimination | A-12 |
| Envoyer la nature du circuit | A-13 |
| Demander des informations sur l’utilisation du suppresseur d’écho | A-14 |
| Congestion dans un échange international ou à sa sortie | A-15 |

Signal group B (backward):

| Description | Backward signal |
| --- | --- |
| Réservé | B-1 |
| Envoyer le ton d'information spécial | B-2 |
| Ligne de l'abonné occupée | B-3 |
| Congestion (après le basculement du groupe A vers B) | B-4 |
| Numéro non attribué | B-5 |
| Ligne de l'abonné libre, facturée | B-6 |
| Ligne de l'abonné libre, non facturée | B-7 |
| Ligne de l'abonné hors service | B-8 |
| Réservé | B-9 |
| Réservé | B-10 |
| Réservé | B-11 |
| Réservé | B-12 |
| Réservé | B-13 |
| Réservé | B-14 |
| Réservé | B-15 |

#### Séquence MFC/R2

La séquence suivante illustre un appel provenant de l'extension d'Asterisk vers un terminal du PSTN. Le PSTN interrompt l'appel et met fin à la communication.

![Un flux d'appel complet MFC/R2 entre Asterisk et le télécom : la signalisation de ligne (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) est échangée dans le créneau 16, les chiffres composés et les signaux de « send next digit » en retour (groupes I/A/B) voyagent en bande, et les tonalités audibles atteignent l'abonné.](../images/10-legacy-fig11.png)

### Comment utiliser le pilote libopenr2

Le projet initié par Moises Silva s'est inspiré du pilote de canal Unicall écrit par Steve Underwood. La bibliothèque OpenR2 est actuellement la solution logicielle la plus stable pour Asterisk. Avec cette solution, nous pouvons utiliser n'importe quelle carte numérique compatible avec DAHDI. Auparavant, seules des solutions propriétaires étaient disponibles pour MFC/R2, l'une des meilleures que j'ai utilisées est celle mise à disposition par Khomp, www.khomp.com.br. Dans Asterisk 22, la prise en charge de MFC/R2 via libopenR2 est intégrée lorsque la bibliothèque est présente au moment de la compilation — aucun correctif externe n'est requis. Les étapes ci‑dessous montrent l'installation manuelle historique à titre de référence ; sur les systèmes modernes, installez `libopenr2-dev` depuis le gestionnaire de paquets de votre distribution avant d'exécuter `./configure`, puis activez `chan_dahdi` dans `make menuselect`.

Les étapes ci‑dessous construisent openr2 et Asterisk à partir de leurs dépôts Git actuels. Elles sont conservées comme référence pour les sites qui compilent à partir du source ; sur une distribution moderne, vous pouvez généralement les ignorer complètement en installant le paquet `libopenr2-dev` et une version empaquetée d’Asterisk 22, puisque `chan_dahdi` compile le support R2 directement contre libopenr2 sans correctif externe.

Step 1: Install the build tooling you need.

```
apt-get install git
```

Étape 2 : Clonez la bibliothèque openr2 et le code source d’Asterisk. Aucun arbre patché spécial n’est nécessaire sur Asterisk 22 — un checkout standard compile la prise en charge R2 tant que libopenr2 est présent.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Étape 3 : Compiler et installer Veuillez, SAUVEGARDEZ votre serveur avant de continuer.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: Ne pas exécuter « make samples » afin d'éviter d'écraser vos fichiers de configuration.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Supposons que vous disposiez d’une carte avec une interface E1.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: Run the command dahdi_cfg to apply the changes to the driver:

```
dahdi_cfg -vvvvvvvv
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

Step 5 : Modifier le fichier chan_dahdi.conf

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

Étape 6 : Modifier le plan de numérotation dans le fichier extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Note : Certains TELCOS n’acceptent pas les appels sans l’identifiant de l’appelant. Veuillez définir l’identifiant de l’appelant sur l’un des numéros DID attribués par l’opérateur. Dans certains pays, cette étape n’est pas requise. Étape 7 : Tester la solution : Maintenant, avec une extension dans le contexte from-internal, appelez n’importe quel numéro et observez la console. Vérifiez s’il y a des erreurs. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

Pour détecter les erreurs dans les appels, vous pouvez activer le débogage. Pour ce faire, suivez les étapes ci‑dessous.

1. Modifiez le fichier `chan_dahdi.conf` et ajoutez les trois lignes suivantes à la configuration :

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Redémarrez le serveur Asterisk
3. Testez l’appel et vérifiez les fichiers d’appel à `/var/log/asterisk/mfcr2/span1`

Below is a trace for a normal call. Compare it to what you receive in your call.

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

Les options sont documentées dans le fichier chan_dahdi.conf. Certaines des options les plus importantes sont détaillées ici. Paramètres obligatoires : mfcr2_variant, mfcr2_max_ani et mfcr2_max_dnis. mfcr2_variant : variante du pays.

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

mfcr2_max_ani : Nombre maximal de chiffres ANI à demander  
mfcr2_max_dnis : Nombre maximal de chiffres DNIS à demander  
mfcr2_get_ani_first : Indique s’il faut récupérer l’ANI avant le DNIS (requis par certains TELCOS)  
mfcr2_category : Catégorie de l’appelant. Vous pouvez définir la variable MFCR2_CATEGORY avant de lancer l’appel  
mfcr2_logdir : Répertoire où consigner les fichiers d’appel. (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files : Indique s’il faut consigner les appels  

- mfcr2_logging : valeurs de journalisation  
- cas – bits ABCD pour tx et rx  
- mf – tonalités multifréquences  
- stack – sortie détaillée de la pile du canal et du contexte  
- all – toutes les activités  
- nothing – ne rien journaliser  

mfcr2_mfback_timeout : Cette valeur mérite d’être mentionnée. Parfois, si vous appelez un téléphone portable ou tout appel qui met du temps à se terminer, ce paramètre peut expirer, il est donc souvent modifié pour un réglage fin. Si certains de vos appels ne sont pas complétés, c’est le paramètre à changer en premier.  
mfcr2_metering_pulse_timeout : Les impulsions sont utilisées par certaines variantes R2 pour indiquer les coûts  
mfcr2_allow_collect_calls : Au Brésil, le ton II‑8 indique un appel à frais virés ; ce paramètre vous permet de bloquer les appels à frais virés.  
mfcr2_double_answer : Utilisé également pour éviter les appels à frais virés lorsqu’une double réponse est requise. Avec double_answer=yes vous bloquez effectivement les appels à frais virés.  
mfcr2_immediate_accept : Vous permet de sauter l’utilisation des signaux groupe B/II et de passer directement à l’état accepté.  
mfcr2_forced_release : Vous permet d’accélérer la libération de l’appel ; fonctionne pour la variante brésilienne.  

#### ANI et DNIS

Automatic Number Identification (ANI) est le numéro de l’appelant. Dialed Number Identification Service (DNIS) est le numéro appelé ou, en d’autres termes, le numéro composé. Lorsqu’un appel est reçu, les quatre derniers chiffres sont généralement transmis au PBX dans un processus appelé direct inward dial (DID). Le numéro ANI est en fait le Caller ID. L’ANI contiendra l’extension de l’appelant lors de la composition tandis que le DNIS contiendra la destination de l’appel. Il est important que ces paramètres soient configurés correctement. Certains commutateurs n’envoient que les quatre derniers chiffres tandis que d’autres envoient le numéro complet.  

### Format du canal DAHDI

Les canaux DAHDI utilisent le format suivant dans le dialplan :

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Exemples:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Le protocole IAX2

Dans ce chapitre, nous apprendrons le protocole Inter-Asterisk eXchange (IAX), y compris ses forces et ses faiblesses. Les détails tels que le mode trunk et l’interconnexion de deux serveurs Asterisk seront également abordés. Toutes les références dans ce document correspondent à la version 2 d’IAX.

Le protocole IAX assure le transport média et la signalisation pour la voix et la vidéo. IAX est très innovant ; il économise de la bande passante en mode trunk et est beaucoup plus simple que SIP lorsque vous devez traverser le NAT. L’utilisation principale d’IAX de nos jours est d’interconnecter les serveurs Asterisk. IAX a été créé principalement pour la voix, mais il peut également prendre en charge la vidéo et d’autres flux multimédias.

IAX a été inspiré par d'autres protocoles VoIP, tels que SIP et MGCP. Au lieu d'utiliser deux protocoles séparés pour la signalisation et les médias, IAX les a unifiés pour créer un protocole unique. IAX n'utilise pas RTP pour le transport des médias ; à la place, il intègre les médias dans la même connexion UDP.

**Statut dans Asterisk 22.** `chan_iax2` est toujours inclus et pleinement pris en charge dans Asterisk 22 LTS, de sorte que tout ce qui se trouve dans cette section reste valable. IAX2 est, cependant, un protocole hérité qui voit relativement peu de nouveaux déploiements : l'industrie s'est largement convergée vers SIP (via `chan_pjsip` dans Asterisk 22) pour le trunking des fournisseurs et l'interconnexion des serveurs. Le principal avantage restant d'IAX2 est sa conception à port unique — tous les signaux et médias circulent sur un seul port UDP (4569 par défaut), ce qui simplifie la configuration du pare‑feu et du NAT comparé à SIP avec ses flux RTP séparés. Pour un nouveau trunk Asterisk‑to‑Asterisk où le NAT n'est pas un problème, un trunk PJSIP est l'approche moderne recommandée ; IAX2 est traité ici parce qu'il reste un choix valable, notamment lorsque seul un port UDP peut être ouvert à travers un pare‑feu.

### Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Identifier les forces et les faiblesses du protocole IAX
- Décrire les scénarios d’utilisation du protocole IAX
- Décrire les avantages du mode trunk IAX
- Configurer iax.conf pour les téléphones
- Configurer iax.conf pour la connexion à un fournisseur VoIP
- Configurer iax.conf pour l’interconnexion d’Asterisk
- Comprendre l’authentification IAX

### Conception IAX

Les objectifs principaux de la conception d'IAX sont :

- Réduire la bande passante requise pour le transport des médias et la signalisation
- Fournir une transparence NAT
- Pouvoir transmettre les informations du dial plan
- Prendre en charge l'utilisation efficace du paging et de l'intercom

IAX est un protocole de signalisation et de média peer‑to‑peer similaire à SIP mais n’utilisant pas RTP. L’approche de base consiste à multiplexe les flux multimédias sur une seule connexion UDP entre deux hôtes. Le principal avantage de cette méthode est sa simplicité lors du franchissement de connexions NAT, couramment rencontrées dans les modems xDSL. IAX utilise un seul port, UDP 4569 par défaut, puis un numéro d’appel de 15 bits pour multiplexe tous les flux. Le protocole IAX utilise des processus d’enregistrement et d’authentification similaires à ceux du protocole SIP. Une description du protocole est disponible à l’adresse http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![Le protocole IAX multiplexe de nombreux appels entre deux points d'extrémité sur un seul port UDP (4569 par défaut), en utilisant un numéro d'appel de 15 bits pour séparer les flux — ce qui rend la traversée NAT simple.](../images/10-legacy-fig12.png)

### Utilisation de la bande passante

La bande passante utilisée dans les réseaux VoIP est affectée par plusieurs facteurs ; les codecs et les en‑têtes de protocole sont les plus importants. Le protocole IAX possède une fonctionnalité surprenante appelée mode trunk, qui multiplexe plusieurs appels en utilisant un seul en‑tête. En jouant avec le calculateur de bande passante d’Asterisk, vous verrez comment les trunks IAX peuvent vous faire économiser jusqu’à 80 % du trafic avec plusieurs appels.

![Comparaison de la surcharge IAX et SIP : deux appels SIP/RTP nécessitent deux paquets (40 octets de charge utile transportés sous 156 octets de surcharge), tandis que le mode trunk IAX2 transporte les deux appels dans un seul paquet (40 octets de charge utile sous seulement 66 octets de surcharge) en partageant un en‑tête IP/UDP entre de nombreuses mini‑trames.](../images/10-legacy-fig13.png)

### Nommage des canaux

Il est important de comprendre les conventions de nommage des canaux, car vous utiliserez ces noms lors de la spécification d’un canal dans le dialplan. Le format d’un nom de canal IAX utilisé pour les canaux sortants est :

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — Identifiant d'utilisateur sur le pair distant, ou nom du client configuré dans iax.conf
- `<secret>` — Le mot de passe. Alternativement, cela peut être le nom de fichier d'une clé RSA sans l'extension finale (.key ou .pub) et entouré de crochets
- `<peer>` — Nom du serveur auquel se connecter
- `<portno>` — Numéro de port pour la connexion
- `<exten>` — Extension sur le serveur Asterisk distant
- `<context>` — Contexte sur le serveur Asterisk distant
- `<options>` — La seule option disponible est 'a', signifiant 'demander auto-réponse'

#### Exemple de canaux sortants :

Les canaux sortants sont visibles dans la console Asterisk.

- `IAX2/8590:secret@myserver/8590@default` — Appeler l'extension 8590 sur myserver. Elle utilise 8590:secret comme paire nom/mot de passe
- `IAX2/iaxphone` — Appeler "iaxphone"
- `IAX2/judy:[judyrsa]@somewhere.com` — Appeler somewhere.com en utilisant judy comme nom d'utilisateur et une clé RSA pour l'authentification

#### Le format d'un canal IAX entrant est :

Les canaux entrants sont visibles dans la console Asterisk.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — Nom d'utilisateur si connu
- `<host>` — Hôte de connexion
- `<callno>` — Numéro d'appel local

Incoming channel example:

- `IAX2[flavio@8.8.30.34]/10` — Numéro d'appel 10 depuis l'adresse IP 8.8.30.34 en utilisant flavio comme utilisateur.
- `IAX2[8.8.30.50]/11` — Numéro d'appel 11 depuis l'adresse IP 8.8.30.50.

### Utilisation d'IAX

Vous pouvez utiliser IAX de plusieurs manières. Dans cette section, nous vous montrerons comment configurer IAX pour plusieurs scénarios, y compris :

- Connexion d'un softphone avec IAX
- Connexion d'IAX à un fournisseur VoIP avec IAX
- Connexion de deux serveurs avec IAX
- Connexion de deux serveurs avec IAX en mode trunk
- Débogage d'une connexion IAX
- Utilisation de paires de clés RSA pour l'authentification

#### Connexion d'un softphone avec IAX

Asterisk prend en charge les téléphones IP basés sur IAX tels que l'ATCOM et l'ancien ATA de Digium (appelé IAXy) ainsi que les softphones qui implémentent encore le protocole IAX2. Le processus pour les softphones, les ATA et les téléphones fixes est similaire. Pour configurer un dispositif IAX, vous devez éditer le fichier iax.conf dans /etc/asterisk

```
directory.
```

Nous utiliserons un softphone compatible IAX2 comme exemple.

1. Faites une sauvegarde du fichier `iax.conf` original en utilisant:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. Commencez à éditer un nouveau fichier `iax.conf` :

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

J’ai essayé de préserver les lignes par défaut (non commentées) du fichier d’exemple. Les paramètres suivants ont été modifiés :

```
bandwidth=high
```

Cette ligne affecte la sélection du codec. Utiliser le paramètre high permet de choisir un codec à large bande passante et haute qualité tel que g.711 défini par le mot‑clé ulaw. Si vous conservez le paramètre par défaut, vous ne pourrez pas choisir ulaw. Dans ce cas, Asterisk vous affichera le message « no codec available » pour la configuration ci‑dessous.

```
disallow=all
allow=ulaw
```

Dans les commandes décrites ci‑dessus, nous avons désactivé tous les codecs et n’activé que ulaw. Dans les LAN, la plupart des gens préfèrent utiliser ulaw car il n’est pas gourmand en processeur et économise des cycles CPU. Même en consommant davantage de bande passante, ce codec est préférable parce que dans les LAN on dispose généralement d’un Ethernet 100 Mbits ou même d’un Gigabit. Un appel vocal utilisant ulaw consomme près de 100 kilobits par seconde de bande passante sur votre réseau, ce qui représente une utilisation très légère pour les LAN à haut débit d’aujourd’hui. Dans les réseaux WAN ou Internet, on désactive généralement ulaw, échangeant quelques cycles CPU disponibles contre une compression vocale afin d’optimiser l’utilisation de la bande passante. Les codecs gsm, g729 et ilbc offrent également un bon facteur de compression.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Dans les commandes ci‑dessus, nous avons défini un ami nommé [2003]. Le contexte est le défaut (dans les premiers labs nous utilisons toujours le contexte par défaut pour éviter la confusion ; ce contexte sera entièrement expliqué lorsque nous aborderons le dial plan). La ligne « host=dynamic » fournit un enregistrement dynamique de l’adresse IP du téléphone.

3. Téléchargez et installez un softphone compatible IAX2. Vous pouvez choisir n’importe quel softphone qui prend encore en charge le protocole IAX2 pour le laboratoire.  
4. Configurez un compte IAX dans le client (généralement *Add account* → IAX). Notez que le SipPulse Softphone est uniquement SIP et ne peut pas s’enregistrer via IAX2, donc pour les tests IAX vous avez besoin d’un client qui supporte encore le protocole.

5. Configurez le fichier `extensions.conf` pour tester votre dispositif IAX.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![Un Asterisk d’un client connecté à un fournisseur VoIP via un trunk IAX à travers Internet : un seul trunk transporte tous les appels vers et depuis le fournisseur.](../images/10-legacy-fig14.png)

The number of IAX-capable commercial VoIP providers has declined sharply over the past several Asterisk releases; most providers now offer SIP/PJSIP trunks exclusively. Before committing to an IAX provider, confirm they actively maintain their IAX infrastructure. For a new provider integration, a PJSIP trunk (Chapter 3) is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

Dans les instructions décrites ci‑dessus, vous vous êtes enregistré auprès de votre fournisseur en utilisant votre compte et votre mot de passe. Dès que vous recevez un appel, il sera transféré vers l'extension 2003.

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

Dans les instructions décrites ci‑dessus, nous avons créé un pair correspondant au fournisseur à des fins de numérotation.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Ceci est requis pour l'authentification RSA. Utiliser la clé publique de votre fournisseur vous permet de vous assurer que l'appel reçu provient réellement du vrai fournisseur. Si quelqu'un d'autre tente d'utiliser le même chemin, il ne pourra pas l'authentifier car il ne possède pas la clé privée correspondante. Étape 4 : Essayez la connexion. Pour tester la connexion, appelez n'importe quel numéro. Certains fournisseurs offrent un test d'écho. Pour ce faire, veuillez modifier le fichier extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Allez à l'interface de ligne de commande d'Asterisk et effectuez un rechargement. Pour vérifier si Asterisk est enregistré auprès du fournisseur, utilisez la commande suivante.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Connexion de deux serveurs Asterisk via un trunk IAX

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![Connexion de deux serveurs Asterisk avec un trunk IAX : le serveur HQ (192.168.1.1, extensions 20xx) et le serveur Branch (192.168.1.2, extensions 22xx) se rejoignent via un seul trunk IAX — aucune inscription n’est nécessaire car les deux adresses IP sont fixes et connues.](../images/10-legacy-fig15.png)

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

Étape 2 : Configurez le fichier extensions.conf sur le serveur Branch

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

# Étape 3 : Configurer le fichier iax.conf sur le serveur HQ

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

Step 4 : Configurez le fichier extensions.conf sur le serveur HQ.

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

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

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

If un appel possède un nom d'utilisateur spécifié, tel que :

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk essaiera d'authentifier l'appel en utilisant uniquement l'entrée correspondante dans le fichier iax.conf. Si d'autres noms sont spécifiés, l'appel sera rejeté. Si aucun utilisateur n'est indiqué, Asterisk tentera d'authentifier la connexion en tant que guest. Cependant, si guest n'existe pas, il essaiera toute autre connexion avec un secret correspondant. En d'autres termes, si vous n'avez pas de section guest dans votre fichier iax.conf, un utilisateur malveillant pourrait tenter de deviner un secret correspondant en ne spécifiant pas le nom d'utilisateur. Les restrictions de refus/autorisation d'adresses IP s'appliquent également. Une bonne façon d'éviter le devinage de secret est d'utiliser l'authentification RSA. Une autre méthode consiste à restreindre les adresses IP autorisées à appeler.

#### Restrictions d'adresses IP

L'accès est contrôlé avec `permit` et `deny` lignes :

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

Les règles sont interprétées séquentiellement, et toutes sont évaluées (ce concept diffère des ACL généralement présentes dans les routeurs et les pare-feu). La dernière instruction correspondante remplace les précédentes.

Exemple #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

Cela refusera tout paquet provenant du réseau 192.168.0.0/24.

Exemple #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

Cela permettra n’importe quel paquet, car la dernière instruction l’emporte sur la première.

#### Connexions sortantes

Les connexions sortantes récupèrent les informations d’authentification en utilisant les méthodes suivantes :

- La description du canal IAX2 transmise par l’application `dial()`.
- Une entrée avec `type=peer` ou `type=friend` dans le fichier `iax.conf`.
- Une combinaison des deux méthodes.

#### Connexion de deux serveurs Asterisk à l’aide de clés RSA

Il est possible d’utiliser IAX avec une authentification forte en recourant à des clés RSA asymétriques. D’après le code source (`res_krypto.c`), Asterisk utilise des clés RSA avec un algorithme SHA‑1 pour les résumés de messages, au lieu du MD5 plus faible. Voici un guide étape par étape pour configurer deux serveurs avec des clés RSA.

##### Configuration du serveur pour la branche

Étape 1 : Générer les clés RSA sur le serveur de branche

```
astgenkey -n
```

Lorsque demandé, utilisez le nom de clé branch. Nous avons utilisé le paramètre –n pour éviter de fournir une phrase de passe chaque fois qu'Asterisk se réinitialise. Si vous souhaitez améliorer la sécurité, n'utilisez pas le –n et lancez Asterisk avec asterisk -i Étape 2 : Copiez les clés dans le répertoire /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Step 3: Copier la clé publique sur le serveur HQ

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4 : Modifiez le fichier iax.conf sur le serveur Branch.

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

# Étape 8 : Configurer le fichier extensions.conf sur le serveur Branch

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configuration du serveur pour le siège

Étape 1 : Générer les clés RSA sur le serveur du siège

```
astgenkey -n
```

Lorsque demandé, utilisez le nom de clé hq.  
Étape 2 : Copiez les clés dans le répertoire /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

Step 3 : Copiez la clé publique sur le serveur BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Step 4 : Configurer le fichier iax.conf sur le serveur HQ

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

Step 10: Configurer le fichier extensions.conf sur le serveur HQ.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### Chiffrement IAX2

IAX prend en charge le chiffrement des appels à l'aide d'une clé symétrique, d'un chiffrement par bloc de 128 bits appelé AES (Advanced Encryption Standard). Il est très simple d'activer le chiffrement entre les trunks IAX. Dans le fichier iax.conf, utilisez:

```
encryption=yes
```

Pour forcer le chiffrement :

```
forceencryption=yes
```

Pour garantir la compatibilité avec les versions antérieures, vous devrez peut-être désactiver la rotation des clés en utilisant :

```
keyrotate=no
```

### Commandes de débogage IAX2

Voici quelques-unes des commandes console de dépannage les plus importantes pour Asterisk.

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

En examinant cette sortie, identifiez le début et la fin de l’appel. Observez les informations de délai et de gigue obtenues à l’aide des paquets poke et pong. Ces paquets aident à créer la sortie de la commande “iax2 show netstats”.

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

Pour désactiver le débogage, utilisez :

```
vtsvoffice*CLI>iax2 no debug
```

### Résumé

Ce chapitre a passé en revue les forces et les faiblesses du protocole IAX. Il a démontré le fonctionnement d’IAX dans plusieurs scénarios, tels que les softphones et un trunk entre deux serveurs Asterisk. Le mode trunk vous permet d’économiser de la bande passante en transportant plusieurs appels dans un seul paquet. Enfin, vous avez appris les commandes console que vous pouvez utiliser pour vérifier l’état et déboguer le protocole.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Step 2: Configure the [peer] on sip.conf Créez une entrée de type peer pour le fournisseur souhaité afin de simplifier la numérotation d’Asterisk.

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

Step 3: Create a route to the provider in the dial plan  
We will choose the digits 010 as the destination route to the provider.  
To dial #610000 inside the provider, simply dial 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### Options SIP spécifiques au scénario du fournisseur

La discussion suivante examine les détails des options définies dans le fichier sip.conf pour la connexion à un fournisseur VoIP.

```
register=>username:password@hostname/4100
```

L'instruction **registered** dans le fichier **sip.conf** est utilisée pour s'enregistrer auprès d'un fournisseur. La transaction **register** est authentifiée avec le **name** et le **secret**. Vous pouvez utiliser une barre oblique (“/”) pour fournir une extension pour les appels entrants. Techniquement, l'extension sera placée dans le champ d’en‑tête “Contact” de la requête **SIP**. Le comportement d’enregistrement peut être contrôlé par certains paramètres :

```
registertimeout=20
registerattempts=10
```

Pour vérifier si l’enregistrement a réussi, la commande console héritée était `sip show registry`. Sur Asterisk 22, la commande équivalente est `pjsip show registrations` (enregistrements sortants) et `pjsip show endpoints` pour l’état de l’endpoint.

Le paramètre “username” est utilisé dans le digest d’authentification. Le digest est calculé à partir de username, secret et realm:

```
username=username
```

Host définit l'adresse ou le nom du fournisseur VoIP :

```
host=hostname
```

Les paramètres Fromuser et Fromdomain sont parfois requis pour l'authentification. Ces paramètres sont utilisés dans le champ d'en-tête SIP From :

```
fromuser=username
fromdomain=hostname
```

Lorsque vous vous connectez à un fournisseur VoIP, des identifiants sont requis. Après l’invite initiale, le fournisseur vous envoie un message appelé « 407 Proxy Authentication Required » ; vous fournissez les identifiants dans le message INVITE suivant. Pour les appels entrants, votre serveur Asterisk demandera des identifiants au fournisseur. Évidemment, le fournisseur ne possède pas d’identifiant valide pour votre serveur Asterisk. Lorsque vous utilisez insecure=invite, vous indiquez à Asterisk de ne pas envoyer le « 407 Proxy Authentication Required » au fournisseur et d’accepter les appels entrants. Vous pouvez également utiliser insecure=port, invite pour faire correspondre le pair en fonction de l’adresse IP sans tenir compte du numéro de port.

```
insecure=invite, port
```

### Connexion de deux serveurs Asterisk entre eux en utilisant SIP (sip.conf)

Vous pouvez utiliser SIP pour interconnecter deux serveurs Asterisk. Il est important de prêter attention au dialplan avant de poursuivre cette configuration. Les utilisateurs souhaitent généralement connecter d’autres PBX avec un effort minimal. L’idée ici est d’utiliser uniquement un numéro d’extension pour se connecter à l’autre PBX. Étape 1 : Modifiez le fichier sip.conf sur le serveur A:

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

Step 2: Edit the sip.conf file in server B:

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

![Connexion de deux serveurs Asterisk via SIP : le serveur A (extensions 4400/4401) et le serveur B (extensions 4500/4501) échangent les signaux SIP afin que les utilisateurs de chaque PBX puissent appeler l'autre](../images/07-sip-and-pjsip-fig08.png)

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

Étape 3 : Modifiez le fichier extensions.conf sur le serveur A :

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Étape 4 : Modifier le fichier extensions.conf sur le serveur B :

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk domain support (sip.conf)

Le protocole SIP suit l'architecture Internet. La première chose à faire avant de configurer SIP est de définir correctement les serveurs DNS. Dans un environnement SIP, vous pouvez appeler un utilisateur situé dans n'importe quel proxy SIP, et d'autres utilisateurs peuvent également vous appeler en utilisant votre SIP Uniform Resource Identifier (URI). Pour définir un serveur DNS pour SIP, vous devez ajouter des enregistrements SRV à votre serveur DNS.

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

Après avoir configuré le DNS, vous pouvez utiliser l’URI, qui pointe vers un utilisateur SIP, un téléphone SIP ou une extension téléphonique. Une URI SIP ressemble à une adresse e‑mail (par exemple, sip:chuck@yourpartnerdomain.com). En utilisant les URI SIP, aucun numéro de téléphone n’est nécessaire pour passer un appel d’un téléphone SIP à un autre. Pour appeler un utilisateur externe, il suffit d’utiliser une instruction comme celle montrée ci‑dessous.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certains paramètres peuvent contrôler le comportement du domaine.

```
srvlookup=yes
```

Ce paramètre active les recherches DNS SRV pour les appels sortants. En utilisant ce paramètre, il est possible de composer des appels en utilisant des noms SIP basés sur le domaine.

```
allowguest=yes
```

Ce paramètre permet à une invitation externe d'être traitée sans authentification. Il traite l'appel dans le contexte défini dans la section générale ou dans l'instruction domain. Attention : si vous définissez un contexte dans la section générale avec accès au PSTN, un utilisateur externe peut composer le PSTN via votre PBX. Dans ce cas, vous supporterez tous les frais. Autorisez uniquement vos propres extensions dans le contexte défini dans la section générale.

![Connexion à d'autres serveurs SIP par domaine : youdomain.com et yourpartnerdomain.com échangent des signaux SIP, de sorte que des utilisateurs comme lee et bruce peuvent appeler chuck et norris en utilisant des URI SIP](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

La commande domain vous permet de gérer plusieurs domaines au sein d'Asterisk. Si un appel provient d'un domaine spécifique, il est dirigé vers un contexte spécifique.

```
;autodomain=yes
```

Ce paramètre inclut l'adresse IP locale et le nom d'hôte dans les domaines autorisés.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

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

Step 2 : Maintenant configurez le softphone pour utiliser la présence. Nous vous montrons comment configurer le SipPulse Softphone.

- Séquence : clic droit → Paramètres du compte SIP → Propriétés → Présence
- Changez le modèle de présence de peer-to-peer à presence agent, ce qui fera que le softphone s’abonne à Asterisk pour les événements SIP.

Step 3 : Ajoutez le contact aux autres softphones. Dans cet exemple, le SipPulse Softphone est le compte 2000, nous allons donc ajouter un contact pour le compte 2001. Séquence : ouvrez le panneau droit (panneau de présence dans le softphone) → Cliquez sur Contacts → Ajouter un contact. Remplissez le nom 2001. Affichage comme 2001 et n’oubliez pas de cocher la case Afficher la disponibilité de ce contact.

Step 4 : Appelez maintenant l’extension 2001 et vérifiez le statut du téléphone dans le panneau droit du softphone. Utilisez la commande console `core show hints` pour voir le statut de présence changer sur le serveur (dans le chan_sip hérité, `sip show inuse` montrait le nombre d’appels sur chaque ligne). Sur Asterisk 22, utilisez `pjsip show endpoints` pour inspecter l’état de l’endpoint et du canal. Le statut de présence/BLF apparaît dans les contacts du softphone ou le panneau BLF — la façon dont il est affiché dépend du client.

#### Configuration du codec

La configuration du codec est simple et directe. Vous pouvez définir les mots allow et disallow dans la section [general] ou dans la section peer/user. La meilleure pratique consiste à standardiser le codec afin d’éviter le transcoding, qui est gourmand en processeur. Veuillez utiliser le même codec pour les messages et les invites.

```
[general]
disallow=all
allow=g729
```

#### Options DTMF

Dans certaines situations, vous devez transmettre des chiffres à une application telle que la messagerie vocale ou la réponse vocale interactive (IVR). Il est important de transmettre le DTMF correctement. La méthode la plus simple pour transmettre le DTMF s’appelle « inband ». Elle se configure dans la section [general] ou dans la section peer/user du fichier sip.conf. Lorsque vous définissez `dtmfmode=inband`, les tons DTMF sont générés comme des sons dans le canal audio. Le principal problème de cette méthode est que, lorsque vous compressez le canal audio à l’aide d’un codec tel que `g729`, les sons sont déformés et les tons DTMF ne sont pas correctement reconnus. Si vous prévoyez d’utiliser `dtmfmode=inband`, utilisez le codec `g.711` (`ulaw` et `alaw`).

```
dtmfmode=inband
```

Une autre approche consiste à utiliser RFC2833, qui vous permet de transmettre les tonalités DTMF sous forme d'événements nommés dans les paquets RTP.

```
dtmfmode=rfc2833
```

Enfin, vous pouvez transmettre les chiffres DTMF à l'intérieur des paquets SIP, au lieu des paquets RTP. Cette méthode est définie dans les RFC3265 (événements de signalisation) et RFC2976.

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

This tries to use the RFC2833; if it is not possible, use band tones.

#### Configuration du marquage Quality of service (QoS)

Le QoS est un ensemble de techniques responsables de la qualité de la voix. Le QoS est mis en œuvre de manière à réduire la bande passante, la latence et le jitter. Les principales fonctions du QoS sont la planification des paquets, la fragmentation et la compression d’en-têtes. Le QoS est implémenté dans les commutateurs et les routeurs, pas par Asterisk lui‑même. Cependant, Asterisk peut aider les routeurs et les commutateurs en marquant les paquets pour une livraison prioritaire. Le marquage est effectué à l'aide des points de code de services différenciés (DSCP) définis dans les RFC 2474 et RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

À partir de la version 1.4, vous pouvez spécifier des codes différents pour la signalisation (SIP), l’audio (RTP) et la vidéo (RTP).

### Authentification SIP (sip.conf)

Lorsque le legacy `chan_sip` reçoit un appel SIP, il suit les règles décrites dans le diagramme suivant. Trois paramètres jouent un rôle important dans l’authentification SIP. Sur Asterisk 22, l’authentification est configurée à la place avec des objets PJSIP `auth` (`type=auth`, `auth_type=userpass`, `username=`, `password=`) référencés par un endpoint, et le contrôle d’accès IP est effectué avec `permit=`/`deny=` sur le endpoint ou via un `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Ce paramètre contrôle si un utilisateur sans pair correspondant peut s’authentifier sans nom et secret. Nous avons abordé ce paramètre dans la section de prise en charge des domaines.

```
insecure=invite,port
```

Lorsque nous utilisons insecure=invite, Asterisk ne génère pas le message “407 Proxy Authentication Required”. Sans ce message, l'utilisateur peut passer un appel sans authentification. Cela est souvent utilisé pour se connecter aux fournisseurs de services VoIP. Les appels provenant du fournisseur de services VoIP ne sont généralement pas authentifiés.

```
autocreatepeer=yes/no
```

Cette commande est utilisée lorsque Asterisk est connecté à un proxy SIP. Elle crée dynamiquement un pair pour chaque appel. Lorsque cette option est activée, tout UAC peut se connecter au serveur Asterisk. Il est important de limiter la connexion IP au proxy SIP. Le proxy SIP, à son tour, prend en charge le contrôle d'accès. La configuration du pair est basée sur les options générales ainsi que sur le champ d’en‑tête “Contact” du paquet SIP. Avertissement : utilisez ceci avec une extrême prudence car cela ouvre complètement Asterisk.

```
secret=secret, remotesecret=secret
```

Ce paramètre configure le secret pour l'authentification : utilisez secret pour les requêtes entrantes et remotesecret pour les requêtes sortantes. Si vous ne souhaitez pas exposer les secrets dans les fichiers texte, vous pouvez utiliser md5secret pour inclure un hachage à la place du secret. Pour générer le secret MD5, vous pouvez utiliser :

```
echo -n "username:realm:secret" |md5sum
```

Ensuite, utilisez l'instruction suivante :

```
md5secret=0b0e5d467890....
```

Warning: N'oubliez pas d'utiliser le paramètre –n ; le retour chariot sera utilisé dans le calcul md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

Les déclarations ci‑above refuseront toutes les adresses IP et autoriseront le UAC uniquement depuis le réseau local (192.168.1.0/24).

#### options RTP

Il est possible de contrôler certains paramètres RTP.

```
rtptimeout=60
```

Cela met fin aux appels sans activité RTP pendant plus de 60 secondes lorsqu’ils ne sont pas en attente.

```
rtpholdtimeout=120
```

Cela termine les appels sans activité RTP même en attente (doit être supérieur à rtptimeout).

### SIP NAT traversal (sip.conf)

La *théorie* NAT (les quatre types de NAT, le problème de l’en‑tête Contact, les keep‑alives et le forçage du média à travers le serveur) est au niveau du protocole et est couverte dans le chapitre *SIP & PJSIP in depth*. Les paramètres `sip.conf` présentés ici (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) sont **legacy chan_sip** et ont été supprimés dans Asterisk 21+. Sur PJSIP, ils correspondent à des réglages transport/endpoint tels que `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address` et `local_net=` sur le transport, plus `qualify_frequency=` sur l’AOR.

Dans le chan_sip legacy, le paramètre `nat` avait cinq options :

- nat = no — Ne pas effectuer de traitement NAT spécial autre que RFC3581
- nat = force_rport — Faire comme s’il y avait un paramètre rport même s’il n’en existe pas
- nat = comedia — Envoyer le média au port d’où Asterisk l’a reçu, quel que soit le port indiqué dans le SDP.
- nat = auto_force_rport — Activer l’option force_rport si Asterisk détecte du NAT (par défaut)
- nat = auto_comedia — Activer l’option comedia si Asterisk détecte du NAT

Lorsque vous placez l’instruction « nat=force_rport » dans le fichier sip.conf, vous indiquez à Asterisk d’ignorer l’adresse contenue dans le champ d’en‑tête « Contact » du SIP et d’utiliser l’adresse IP source et le port dans l’en‑tête IP du paquet, ainsi que d’envoyer le média à l’adresse d’où il a été reçu en ignorant le contenu de l’en‑tête SDP.

```
nat=force_rport,comedia
```

Il est nécessaire de garder le mappage NAT ouvert. Si le NAT expire, Asterisk ne peut pas envoyer d’invite au UAC. Le UAC peut envoyer des appels, mais n’en recevoir aucun. L’instruction suivante peut être utilisée pour garder le NAT ouvert.

```
qualify=yes
```

Qualify enverra régulièrement un paquet SIP utilisant la méthode OPTIONS, ce qui aidera à maintenir le NAT ouvert. Qualify envoie un OPTIONS toutes les 60 secondes et chaque 10ᵉ seconde lorsque l’hôte n’est pas joignable. Vous pouvez utiliser « sip show peers » pour voir la latence des pairs. Si le NAT de l’utilisateur est du type symétrique, il n’est pas possible d’envoyer des paquets d’un UAC à un autre directement ; dans ce cas, vous devez forcer le RTP à traverser Asterisk en utilisant :

```
directmedia=no
```

#### Asterisk derrière NAT (sip.conf)

Tous les scénarios précédents supposent que le serveur Asterisk possède une adresse Internet externe (valide). Parfois le serveur Asterisk est déployé derrière un pare‑feu avec NAT. Dans ce cas, il faut effectuer quelques configurations supplémentaires.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. Configurez le pare‑feu pour rediriger statiquement le port UDP 5060 vers le serveur Asterisk.  
2. Configurez le pare‑feu pour rediriger statiquement les ports UDP de 10000 à 20000.

Si vous souhaitez limiter le nombre de ports ouverts, vous pouvez modifier le fichier `rtp.conf` pour changer la plage de ports RTP. Une autre solution consiste à utiliser un pare‑feu intelligent qui prend en charge le protocole SIP afin d’ouvrir les ports RTP dynamiquement.

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

Étape 3 : Configurez Asterisk pour inclure l'adresse externe dans les champs d'en-tête des paquets SIP, y compris le Session Description Protocol (SDP). Vous pouvez le faire en ajoutant les deux déclarations suivantes au fichier sip.conf :

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

Le premier paramètre **externaddr** indique à Asterisk d’inclure l’adresse IP externe dans les en‑têtes SIP pour les destinations externes. Le deuxième paramètre **localnet** permet à Asterisk de différencier les adresses externes et internes. Optionnellement, vous pouvez utiliser **externhost** si vous utilisez un DNS dynamique avec une adresse DHCP sur le serveur.

### Chaînes de numérotation SIP (chan_sip)

La technologie de chaîne de numérotation `SIP/...` présentée ci‑dessous correspond au pilote **chan_sip** supprimé. Sur Asterisk 22, utilisez la technologie `PJSIP/...` à la place — par exemple `Dial(PJSIP/2000)` ou `Dial(PJSIP/${EXTEN}@provider)`. Les formes et la signification restent par ailleurs analogues.

Vous pouvez appeler une destination SIP héritée en utilisant différentes chaînes de numérotation :

```
SIP/peer
```

- ; Il faut avoir un pair défini dans sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Exemples :

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migration d’un système legacy chan_sip vers PJSIP

Parce que `chan_sip` a été supprimé dans Asterisk 21 et n’existe plus dans Asterisk 22, toute
déploiement `sip.conf` existant doit être migré vers PJSIP. Le plus grand changement conceptuel
est qu’un seul `sip.conf` `[peer]` ou `[friend]` est découpé en plusieurs
objets PJSIP, chacun avec un `type=` : un **endpoint** (paramètres d’appel/codec/média),
un ou plusieurs objets **aor** (où le dispositif peut être joint / enregistrement),
un objet **auth** (identifiants), et un **transport** partagé (la socket d’écoute,
adresses NAT). Le tableau suivant fait correspondre les concepts les plus courants.

| Concept legacy sip.conf | Équivalent PJSIP (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (référencé via `auth=` et `aors=`) |
| `type=friend` / `type=peer` / `type=user` | un seul `type=endpoint` (PJSIP n’a pas de distinction friend/peer/user) |
| `host=dynamic` (l’appareil s’enregistre) | `type=aor` avec `max_contacts=1` ; l’appareil REGISTER pour mettre à jour son contact |
| `host=<ip/hostname>` (statique) | `type=aor` avec un `contact=sip:host:port` statique |
| `register=>user:secret@host/ext` (sortant) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` sur l’endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` sur l’endpoint (même syntaxe) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — aussi `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` sur l’endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (secondes) sur le **aor** |
| `externaddr=` | `external_media_address=` et `external_signaling_address=` sur le **transport** |
| `localnet=` | `local_net=` sur le **transport** |
| `insecure=invite` (fournisseur, pas d’auth) | omettre `auth=`/`outbound_auth=` et utiliser `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (utiliser avec précaution) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (et `cos_audio` / `cos_video`) sur l’endpoint |

Une extension d’enregistrement qui ressemblait à cela dans le legacy `sip.conf`:

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

devient le suivant dans `pjsip.conf` sur Asterisk 22:

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

Asterisk fournit un script d’assistance, **`sip_to_pjsip.py`**, qui lit un fichier existant
`sip.conf` et génère un `pjsip.conf`. Vous pouvez l’exécuter directement dans le
répertoire /etc/asterisk. L’utilitaire se trouve dans l’arborescence des sources d’Asterisk sous
`contrib/scripts/sip_to_pjsip/`, où `${PATH_TO_ASTERISK_SOURCE}` est le chemin
où les fichiers sources d’Asterisk sont situés (généralement /usr/src/asterisk-22.x.y/).

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

If you run it with the `--help` option you will see its options:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

Il accepte également des arguments positionnels optionnels — `[input-file [output-file]]`,
avec pour valeurs par défaut `sip.conf` et `pjsip.conf` dans le répertoire actuel.

Considérez sa sortie comme un **point de départ** : examinez chaque objet généré,
en particulier les transports, les paramètres NAT et les listes de codecs, et testez soigneusement avant de passer en production.

Migrons le sip.conf dans nos laboratoires compagnons de VoIP School Blackbelt (voip.school)

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
register=>1020:supersecret@sip.flagonc.com:5600/9999
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
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
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
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
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
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
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
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

Bien que la conversion semble correcte, nous pouvons voir que certains éléments tels que qualify=yes ne peuvent pas être mappés directement. Pour corriger, vous devez ajouter à la section aor la commande qualify_frequency=time en secondes. Exemple ci‑dessous.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

La configuration complète de PJSIP est couverte dans le chapitre *SIP & PJSIP in depth*, et la documentation officielle sur docs.asterisk.org couvre entièrement le canal. Dans nos laboratoires complémentaires sur voip.school, le laboratoire 5 vous permet de mettre en pratique ce que vous venez d'apprendre.

## Summary

Ce chapitre regroupe les technologies de canaux qui précèdent les déploiements VoIP purs d’aujourd’hui mais que Asterisk 22 prend encore en charge. Vous avez vu comment les lignes **analog** et les téléphones se connectent via les interfaces **FXO/FXS** sur DAHDI, comment les liaisons **digital TDM** (E1/T1 et ISDN PRI/BRI) sont provisionnées, et comment **IAX2** (`chan_iax2`) sert toujours de trunk serveur‑à‑serveur efficace et compatible NAT même s’il est désormais clairement hérité. Vous avez également revisité le pilote **`chan_sip`** retiré et sa syntaxe `sip.conf` — que vous rencontrerez dans d’anciens systèmes mais qui n’existe plus dans Asterisk 22 — et travaillé à la migration d’un tel système vers PJSIP à l’aide du tableau de correspondance des concepts et du script `sip_to_pjsip.py`. La règle d’or : ne vous tournez vers quoi que ce soit présenté dans ce chapitre que lorsque du matériel réel ou un système hérité existant vous y contraint ; tout ce qui est nouveau doit être PJSIP sur IP.

## Quiz

1. Concernant les deux interfaces analogiques Foreign eXchange, indiquez les affirmations correctes (choisissez toutes celles qui s'appliquent) :
   - A. Une interface FXO se connecte au central téléphonique public (PSTN) et en tire le ton de numérotation.
   - B. Une interface FXS fournit le ton de numérotation et l’alimentation de sonnerie à un téléphone analogique, fax ou modem standard.
   - C. Une interface FXS est la façon correcte de connecter Asterisk à une ligne télécom.
   - D. Une interface FXO peut également être connectée à un port d’extension d’un PBX hérité.
2. Le signalement de supervision sur une ligne analogique comprend quels éléments (choisissez toutes les réponses applicables) ?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Les échos, crépitements et bruits sur une carte analogique DAHDI sont le plus souvent causés par :
   - A. La façon dont Asterisk a été compilé
   - B. Des conflits d’interruption PCI
   - C. Un codec SIP incorrect
   - D. Un plan de numérotation manquant
4. Pour une facturation précise sur les canaux analogiques, vous devez détecter exactement le moment où l’autre bout répond. Quelle fonctionnalité activez‑vous sur Asterisk (et demandez‑vous au telco) pour cela ?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial‑tone generation
5. Le matériel DAHDI est indépendant d’Asterisk : la carte physique est configurée dans `/etc/dahdi/system.conf`, tandis que `chan_dahdi.conf` définit les canaux Asterisk, pas le matériel lui‑même.
   - A. True
   - B. False
6. Concernant la capacité des trunks numériques et la signalisation, indiquez les affirmations correctes (choisissez toutes celles qui s’appliquent) :
   - A. Un trunk E1 transporte 30 canaux voix et un trunk T1 en transporte 24.
   - B. Un ISDN PRI utilise 30B+D sur un E1 et 23B+D sur un T1.
   - C. ISDN est un exemple de signalisation CCS, tandis que MFC/R2 est un exemple de signalisation CAS.
   - D. Le T1 est le trunk numérique le plus couramment utilisé en Europe et en Amérique latine.
7. Quel utilitaire détecte automatiquement les cartes DAHDI et génère `/etc/dahdi/system.conf` et `dahdi-channels.conf` ?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. Lors de la migration d’un `sip.conf` `[friend]` hérité vers PJSIP, un seul bloc doit être découpé en plusieurs objets. Quel ensemble d’objets PJSIP `type=` remplace normalement un `[friend]` d’enregistrement ?
   - A. `type=endpoint`, `type=aor` et `type=auth`
   - B. `type=peer` et `type=user`
   - C. `type=sip` uniquement
   - D. `type=channel` et `type=device`
9. Quel est l’avantage pratique principal d’utiliser le mode trunk IAX2 entre deux serveurs Asterisk ?
   - A. Il chiffre chaque appel avec TLS par défaut
   - B. Il transporte plusieurs appels sous un même en‑tête, économisant de la bande passante
   - C. Il supprime le besoin de tout codec
   - D. Il alloue un port UDP séparé par appel pour une meilleure qualité
10. Les clés RSA peuvent être utilisées pour l’authentification IAX2. Quelle clé devez‑vous garder secrète, et laquelle donnez‑vous à l’autre serveur ?
    - A. Garder la clé publique secrète ; partager la clé privée
    - B. Garder la clé privée secrète ; partager la clé publique
    - C. Garder la clé partagée secrète ; partager la clé privée
    - D. Les deux clés doivent être partagées

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
