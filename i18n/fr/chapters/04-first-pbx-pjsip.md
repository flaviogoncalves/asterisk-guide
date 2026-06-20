# Construire votre première PBX avec PJSIP

Dans ce chapitre, vous apprendrez comment réaliser une configuration de base d’une PBX Asterisk. L’objectif principal est de voir la PBX fonctionner pour la première fois, pouvoir composer entre extensions, lancer la lecture d’un message, et appeler un trunk analogique ou SIP unique. L’idée de ce chapitre est de garantir que votre Asterisk soit opérationnel le plus rapidement possible. Après avoir terminé les travaux de ce chapitre, vous disposerez des connaissances suffisantes pour vous préparer aux chapitres suivants, où nous approfondirons les détails de configuration.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Comprendre et modifier les fichiers de configuration ;
- Installer des softphones basés sur SIP ;
- Installer et configurer un trunk SIP ;
- Installer et configurer une connexion analogique ;
- Composer entre extensions ;
- Composer entre téléphones et destinations externes ; et
- Configurer un standard automatique.

## Understanding the configuration files

Asterisk is controlled by text configuration files located in /etc/asterisk. The file format is similar to the Windows “.ini” files. A semicolon is used as a remark character, the signs “=” and “=>” are equivalent, and spaces are ignored.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interprets “=” and “=>” in the same way. Differences in syntax are used to distinguish between objects and variables. Use “=” when you want to declare a variable and “=>” to designate an object. The syntax is the same between all files, but three types of grammar are used, as discussed below.

## Grammaires

| Grammaire | Comment l'objet est créé | Fichier de conf. | Exemple |
|-----------|--------------------------|------------------|---------|
| Simple Group | Tout sur la même ligne | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Les options sont définies d'abord, l'objet hérite des options | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Chaque entité reçoit un contexte | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

Le format de groupe simple utilisé dans `extensions.conf` et `voicemail.conf` est la grammaire la plus basique. Chaque objet est déclaré avec des options sur la même ligne. Exemple :

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

Dans cet exemple, l'objet 1 est créé avec les options op1, op2 et op3 tandis que l'objet 2 est créé avec les options op1, op2 et op3.

### Grammaire d'héritage des options d'objet

Ce format est utilisé par les fichiers chan_dahdi.conf et agents.conf, où de nombreuses options sont disponibles, et la plupart des interfaces et objets partagent les mêmes options. Typiquement, une ou plusieurs sections contiennent des déclarations d'objets et de canaux. Les options de l'objet sont déclarées au-dessus de l'objet et peuvent être modifiées pour un autre objet. Bien que ce concept soit difficile à comprendre, il est très simple à utiliser. Exemple :

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Les deux premières lignes configurent la valeur des options op1 et op2 à « bas » et « adv », respectivement. Lorsque l'objet 1 est instancié, il est créé en utilisant l'option 1 comme « bas » et l'option 2 comme « adv ». Après avoir défini l'objet 1, nous changeons l'option 1 en « int ». Ensuite, nous créons l'objet 2 avec l'option 1 comme « int » et l'option 2 comme « adv ».

### Objet d'entité complexe

Ce format est utilisé par pjsip.conf, iax.conf et d'autres fichiers de configuration dans lesquels de nombreuses entités avec de multiples options existent. Typiquement, ce format ne partage pas un grand volume de configurations communes. Chaque entité reçoit un contexte. Parfois, des contextes réservés existent, comme [general] pour les configurations globales. Les options sont déclarées dans les déclarations de contexte. Exemple :

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

L'entité [entity1] possède les valeurs « value1 » et « value2 » pour les options op1 et op2, respectivement. L'entité [entity2] possède les valeurs « value3 » et « value4 » pour les options op1 et op2.

## Options to build a LAB for Asterisk

To configure a PBX, you will need some basic hardware. It is not hard or expensive, but there are some options to be considered. All you will need are two phones and a connection to the public network. Some options and combinations are possible when creating your lab, which we will discuss below.

### Option 1: Complete LAB

With the complete LAB, it is possible to test all the scenarios available and compare solutions such as ATA, IP-phones, and softphones. You can also learn about analog and SIP trunks. You will need:

- Un adaptateur téléphonique analogique SIP (ATA)
- Un téléphone IP
- Un serveur dédié pour Asterisk
- Une station de travail avec un softphone
- Une carte d’interface analogique avec au moins deux interfaces (1 FXO et 1 FXS)
- Un compte chez un fournisseur VoIP

### Option 2: Economy LAB

With the economy LAB, we simplify it a bit. We use the ATA, which is usually less expensive than the IP-phone, and a single FXO card, which is really inexpensive. We won’t be able to use analog phones connected directly to the server, but this does not commonly occur in practice. You will need:

- Un adaptateur téléphonique analogique SIP (ATA)
- Un serveur dédié pour Asterisk
- Une station de travail pour le softphone
- Une carte d’interface analogique avec 1 FXO
- Un compte chez un fournisseur VoIP

### Option 3: Super economy lab

The third LAB uses a virtualized server in the student’s own notebook. The problem with this model is the conflicts generated by the UDP port. Sometimes both the Asterisk server and the softphone try to access the same port, preventing Asterisk from binding the address port. Another issue is the quality of the calls; virtual environments are not indicated for real-time applications such as Asterisk. Use a free softphone for the server and workstation and a trunk connection to a SIP provider. You will need:

- Un ordinateur portable exécutant un softphone
- Une machine virtuelle (VirtualBox, VMware, ou similaire) pour installer Asterisk
- Un compte chez un fournisseur VoIP

## Séquence d'installation

Pour vous aider à comprendre la séquence d'installation, nous avons décrit les étapes nécessaires pour installer et configurer Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. Configuration des extensions
   - a. Extensions SIP (ATA, Softphone, IP Phone)
   - b. Extensions IAX
   - c. Extensions FXS
2. Configuration des trunks
   - a. Configuration d'un trunk SIP
   - b. Configuration d'un trunk FXO
3. Construction d'un plan de numérotation de base
   - a. Numérotation entre extensions
   - b. Numérotation vers des destinations externes
   - c. Réception d'un appel depuis l'extension opérateur
   - d. Réception d'un appel dans un standard automatique

## Configuration des extensions

Les extensions sont des téléphones SIP, IAX ou analogiques connectés à un port FXS. Pour configurer une extension, vous devez éditer le fichier de configuration lié au canal (pjsip.conf, iax.conf, chan_dahdi.conf)

### Extensions SIP

Sur Asterisk 22, PJSIP (la pile `res_pjsip`, configurée dans `/etc/asterisk/pjsip.conf`) est le pilote de canal SIP. Il prend en charge plusieurs transports par endpoint, est activement maintenu, et est le seul pilote SIP fourni avec la plateforme. (Le pilote original `chan_sip` a été supprimé dans Asterisk 21 — voir le chapitre *Legacy channels* si vous devez migrer une ancienne configuration.)

L’idée ici est de configurer une PBX simple. (Les chapitres suivants fournissent une session SIP/PJSIP complète avec tous les détails.) PJSIP est configuré dans `/etc/asterisk/pjsip.conf` et contient tous les paramètres liés aux téléphones SIP et aux fournisseurs VoIP. Les clients SIP doivent être configurés avant de pouvoir passer et recevoir des appels.

#### Le transport

Dans PJSIP, la configuration de l’écouteur (adresse de liaison, port, protocole) se trouve dans un objet `transport`. Asterisk possède une protection intégrée contre la devinette de nom d’utilisateur — il renvoie toujours un défi d’authentification identique pour les utilisateurs inconnus et connus, et les requêtes non identifiées répétées provenant d’une même IP sont limitées en débit via les options `[global]` `unidentified_request_count`/`unidentified_request_period`. Les principales options d’un transport sont :

- protocol : Le protocole de transport — `udp`, `tcp`, `tls`, `ws` ou `wss`.  
- bind : Adresse et port auxquels l’écouteur se lie. Si vous définissez l’adresse sur `0.0.0.0`, il se lie à toutes les interfaces ; le port SIP est par défaut 5060 pour UDP/TCP.

Un transport UDP minimal :

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP permet aux sections `endpoint`, `auth` et `aor` de partager le même nom de section (par ex. les deux blocs `[6001]` ci‑dessus, distingués par leurs `type=`) ; de nombreux administrateurs ajoutent plutôt un suffixe (`[6001]`, `[6001-auth]`, `[6001]` aor) pour plus de lisibilité. Pour un appareil qui s’enregistre, le contact est appris dynamiquement lorsque le téléphone s’enregistre, de sorte que l’AOR n’a pas besoin de `contact` statique.

## IAX Extensions

`chan_iax2` still ships in Asterisk 22 but is now legacy; SIP/PJSIP is the preferred protocol for new deployments.

You may also create IAX extensions. This protocol is native to the Asterisk, and we will have an entire section devoted to it later in this book. For now, let’s create a few extensions using the protocol. As the first section to be configured, the section [general] has certain parameters to be configured. The main options are:

- allow/disallow : Définit quels codecs seront utilisés.
- bindaddr : Adresse à laquelle l’écouteur IAX2 se lie. Si vous le définissez à 0.0.0.0 (par défaut), il se liera à toutes les interfaces.
- context : Définit le contexte par défaut pour tous les clients sauf modification dans la section client. Nous avons utilisé dummy pour des raisons de sécurité. Les utilisateurs non authentifiés accèdent à ce contexte lorsque l’option allowguest est réglée sur yes.
- bindport : Port UDP IAX2 sur lequel écouter (par défaut 4569).
- delayreject : Lorsqu’il est réglé sur yes, retarde l’envoi d’un rejet d’authentification pour un REGREQ ou AUTHREQ, ce qui améliore la sécurité contre les attaques par force brute sur les mots de passe.
- bandwidth : Lorsqu’il est réglé sur high, il autorise la sélection de codecs à large bande, tels que le g711 dans leurs variantes ulaw et alaw.

The following is a sample of the [general] section of the file iax.conf.

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX Clients

After finishing the general sections, it is time to set up the IAX clients.

- `[name]` : Le nom de la section est le nom du pair/utilisateur IAX ; une connexion IAX entrante est associée à celui‑ci par son nom.
- `type` : La classe de connexion — `peer`, `user`, ou `friend` :
  - `peer` : Asterisk envoie des appels à un pair.
  - `user` : Asterisk reçoit des appels d’un utilisateur.
  - `friend` : les deux directions simultanément.
- `host` : Adresse IP ou nom d’hôte. La valeur la plus courante est `dynamic`, utilisée lorsque le dispositif s’enregistre auprès d’Asterisk.
- `secret` : Mot de passe pour authentifier les pairs et les utilisateurs.

Warning: Use strong passwords with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for IAX md5 hashes are available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers. Example:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configurer les appareils SIP

Après avoir défini les téléphones dans le fichier de configuration d’Asterisk, il est temps de configurer le téléphone lui‑même. Dans cet exemple, nous allons montrer comment configurer un softphone gratuit — le SipPulse Softphone (téléchargez‑le depuis https://www.sippulse.com/produtos/softphone). Consultez le manuel de votre appareil pour comprendre les paramètres de votre téléphone. Étape 1 : configurez le téléphone pour utiliser l’extension 6000. Exécutez le programme d’installation. Après l’exécution, ouvrez les paramètres de compte/SIP et ajoutez un nouveau compte SIP. Remplissez les informations requises.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirmez que votre téléphone est enregistré en utilisant la commande console `pjsip show endpoints` (ou `pjsip show endpoint 6000` pour plus de détails ; `pjsip show contacts` montre les contacts AOR enregistrés). Répétez la configuration pour le téléphone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configurer les appareils IAX

IAX2 est un protocole hérité (voir le chapitre *Legacy channels*), et le Softphone SipPulse est uniquement SIP, il ne peut donc pas enregistrer un compte IAX. Si vous devez tester IAX2, utilisez un softphone qui le supporte encore. Créez un nouveau compte IAX,

3. Sélectionnez nouveau compte IAX.  
4. Insérez les options liées pour le téléphone 6003 et éventuellement pour le 6004.  
5. Enregistrez la configuration et vérifiez si le téléphone est enregistré en utilisant `iax2 show peers`.

Important : utilisez un compte pour SIP et un autre pour IAX. Si vous voulez configurer le système pour sonner à la fois IAX et SIP simultanément, nous vous montrerons comment le faire dans la section du dialplan.

### Configurer une interface PSTN

Pour vous connecter au PSTN, vous aurez besoin d’une interface foreign exchange office (FXO) et d’une ligne téléphonique. Vous pouvez également utiliser une extension PBX existante. Vous pouvez obtenir une carte d’interface téléphonique avec une interface FXO auprès de plusieurs fabricants. Dans cet exemple, nous vous montrons comment installer une carte d’interface DAHDI.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### Lignes analogiques utilisant DAHDI

Vous pouvez acheter une carte analogique compatible avec DAHDI auprès de plusieurs fabricants. X100P était l’une des premières cartes Digium et a déjà été abandonnée. Certains fabricants produisent encore des clones similaires. En plus du prix du X100P, nous avons constaté plusieurs problèmes entre ces cartes et les nouvelles cartes mères, donc utilisez‑la avec précaution. X100P, à mon avis, n’est pas un bon choix pour un environnement de production. Toute carte compatible avec DAHDI devrait fonctionner. Grâce à l’équipe de développeurs DAHDI, nous disposons maintenant d’un outil de détection et de configuration des cartes d’interface presque automatiquement. Si vous venez d’installer les pilotes DAHDI, n’oubliez pas d’exécuter `make config` et de redémarrer la machine pour le charger automatiquement. Vous pouvez utiliser les commandes ci‑dessous pour détecter et configurer votre carte. Étape 1 : Pour détecter votre matériel, utilisez :

```
dahdi_hardware
```

Step 2: To configure use:

```
dahdi_genconf
```

La commande ci‑dessus générera deux fichiers /etc/dahdi/system.conf et /etc/asterisk/dahdi-channels.conf. Les paramètres par défaut de dahdi_genconf sont généralement corrects, mais vous pouvez les modifier dans le fichier /etc/dahdi/genconf_parameters. Par défaut, elle insérera les lignes (FXO) dans le contexte from-pstn et les téléphones (FXS) dans le contexte from-internal. Étape 3 : après l’exécution de dahdi_genconf, ajoutez la ligne suivante à la dernière ligne du fichier /etc/asterisk/chan_dahdi.conf :

```
#include dahdi-channels.conf
```

Étape 4 : Modifiez le fichier /etc/dahdi/modules et commentez tous les pilotes inutilisés. Redémarrez avant de continuer et vérifiez si les canaux sont reconnus en utilisant :

```
*CLI> dahdi show channels
```

### Connexion au PSTN via un fournisseur VoIP

Si votre budget est vraiment limité, vous pouvez configurer un trunk SIP pour vous connecter au PSTN. C’est certainement la façon la plus économique de se connecter au PSTN. Des milliers de fournisseurs VoIP existent dans le monde. Pour vous connecter à l’un d’eux, vous aurez besoin de certains paramètres. Paramètres fournis par le fournisseur SIP.

- username : login
- password : secret
- Provider’s domain : domain
- UDP port : 5060
- Allowed codecs : g729, ilbc, alaw

Deux paramètres doivent être déterminés par vous.

- Extension to receive calls—in this case : 9999
- context : from-sip

In PJSIP, a registering SIP trunk is built from the same object family used for an endpoint, plus explicit `registration` and `identify` objects. The `registration` object tells Asterisk to register to the provider, the `identify` object matches inbound traffic from the provider's IP to the endpoint (PJSIP authenticates inbound INVITEs by source IP), and `outbound_auth` supplies the credentials for outbound calls and registration:

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

Pour accéder à ce trunk, nous utiliserons le nom de canal `PJSIP/siptrunk`. Le paramètre `dtmf_mode=rfc4733` transporte le DTMF hors bande (RFC 4733 remplace le plus ancien RFC 2833 ; la charge utile est identique). L'option `identify`/`match` accepte les adresses IP, les CIDR ou les noms d'hôte, mais les noms d'hôte sont résolus une fois au chargement de la configuration, donc pour un fournisseur dont les IP changent, indiquez explicitement les IP(s) de signalisation. Confirmez l'enregistrement avec `pjsip show registrations`.

## Introduction du plan de numérotation

Le plan de numérotation est comme le cœur d’Asterisk. Il définit comment Asterisk gère chaque appel vers le PBX. Il se compose d’extensions qui constituent une liste d’instructions que Asterisk doit suivre. Les instructions sont déclenchées par les chiffres reçus du canal ou de l’application. Pour configurer Asterisk avec succès, il est essentiel de comprendre le plan de numérotation. La majeure partie du plan de numérotation se trouve dans le fichier extensions.conf du répertoire /etc/asterisk. Ce fichier utilise la grammaire simple de groupe et comporte quatre concepts majeurs :

- Extensions
- Priorities
- Applications
- Contexts

Créons un plan de numérotation de base. Dans les sections suivantes de ce livre, je consacrerai un chapitre exclusivement au plan de numérotation. Si vous avez installé les fichiers d’exemple (make samples), le fichier extensions.conf existe déjà. Enregistrez‑le sous un autre nom et commencez avec un fichier vierge.

## The structure of the file extensions.conf

Le fichier extensions.conf est divisé en sections. La première est la section [general] suivie de la section [globals]. Le début de chaque section commence par la définition de son nom (par ex., [default]) et se termine lorsqu’une autre section est créée.

### The section [general]

La section générale se trouve en haut du fichier. Avant de commencer à configurer le dialplan, il est utile de connaître les options générales qui contrôlent certains comportements du dialplan. Ces options sont :

- static and write protect : Si `static=yes` et `writeprotect=no`, vous pouvez enregistrer le dialplan en cours sur le disque avec la commande CLI :

```
*CLI> dialplan save
```

Warning : Si vous exécutez une commande `dialplan save` depuis la CLI, vous perdrez toutes les remarques et commentaires dans le fichier.

- autofallthrough : Si autofallthrough est activé, alors lorsqu’une extension n’a plus rien à faire, l’appel sera terminé avec BUSY, CONGESTION ou HANGUP selon la meilleure estimation d’Asterisk. C’est le comportement par défaut. Si autofallthrough n’est pas activé, alors lorsqu’une extension n’a plus rien à faire, Asterisk attendra qu’une nouvelle extension soit composée.
- clearglobalvars : Si clearglobalvars est activé, les variables globales seront effacées et re‑analysées lors d’un reload du dialplan ou d’un reload d’Asterisk. Si clearglobalvars n’est pas activé, les variables globales persisteront à travers les reloads et—même si elles sont supprimées du fichier extensions.conf ou d’un de ses fichiers inclus—elles resteront définies à la valeur précédente.
- extenpatternmatchnew : Utilise un algorithme de correspondance de motifs plus rapide, ce qui aide nettement lorsque vous avez un grand nombre d’extensions. La valeur par défaut est non.
- userscontext : C’est le contexte où les entrées du fichier users.conf sont enregistrées.

### The section [globals]

Dans la section [globals] vous définirez des variables globales et leurs valeurs initiales. Vous pouvez accéder à la variable dans le dialplan en utilisant ${GLOBAL(variable)}. Vous pouvez même accéder aux variables définies dans l’environnement linux/unix en utilisant ${ENV(variable)}. Les variables globales ne sont pas sensibles à la casse. Quelques exemples pourraient être :

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

Dans l’exemple suivant, vous pouvez définir et tester une variable globale dans le dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context is the named partition of the dial plan. After the [general] and [globals] sections, the dial plan is a set of contexts in which each context has several extensions, each extension has several priorities, and each priority calls an application with several arguments.

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

You can build a simple dial plan to reach other phones and the PSTN. However, Asterisk is much more powerful than that. Our objective is to teach you more details of what is possible in the dial plan.

## Extensions

Contrairement au PBX traditionnel, où les extensions sont associées à des téléphones, des interfaces, des menus, etc., dans Asterisk une extension est une liste de commandes à exécuter lorsqu’un numéro ou un nom d’extension spécifique est déclenché. Les commandes sont traitées par ordre de priorité.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

Une extension peut être littérale, standard ou spéciale. Une extension standard ne comprend que des chiffres ou des noms ainsi que les caractères * et # ; 12#89* est une extension littérale valide. Les noms peuvent également être utilisés pour la correspondance d’extension. Les extensions sont sensibles à la casse. Cependant, vous ne pouvez pas créer deux extensions portant le même nom mais avec des casses différentes. Lorsqu’une extension est composée, la commande avec la première priorité est exécutée, suivie de la commande avec la priorité 2, etc. Cela se poursuit jusqu’à ce que l’appel soit déconnecté ou qu’une commande renvoie le nombre un, indiquant un échec. Ce que fait Asterisk lorsque la dernière priorité est exécutée est régulé par le paramètre autofallthrough. Voir la section [general] de ce chapitre. Exemple :

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Ci‑dessus vous trouvez la liste des instructions à traiter lorsque l’extension 123 est composée. La première priorité consiste à répondre au canal (nécessaire lorsque le canal est en état de sonnerie : c’est‑à‑dire les canaux FXO). La deuxième priorité lit un fichier audio nommé tt‑weasels. La troisième priorité raccroche le canal. Une autre option consiste à gérer l’appel en fonction de l’identifiant de l’appelant. Vous pouvez utiliser le caractère / pour spécifier l’identifiant de l’appelant à traiter. Exemples :

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Cet exemple déclenchera l’extension 123 et exécutera les options suivantes uniquement si l’identifiant de l’appelant est 100. Cela peut également être fait en utilisant le modèle décrit ci‑dessous :

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint : associe une extension à un canal. Il est utilisé pour surveiller l’état du canal. Il est utilisé en conjonction avec la présence. Le téléphone doit le prendre en charge.

#### Patterns

Vous pouvez utiliser des modèles et des littéraux dans le dialplan. Les modèles sont très utiles pour réduire la taille du dialplan. Tous les modèles commencent par le caractère « _ ». Les caractères suivants peuvent être utilisés pour définir un modèle. La figure identifie les modèles disponibles pour une utilisation avec Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk utilise certains noms d’extension comme extensions standard.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Description :

- **s** : Start. Il est utilisé pour gérer un appel lorsqu’aucun numéro n’est composé. Il est utile pour les trunks FXO et le traitement dans les menus.
- **t** : Timeout. Il est utilisé lorsque les appels restent inactifs après la lecture d’une invite. Il sert également à raccrocher une ligne inactive.
- **T** : AbsoluteTimeout. Si vous définissez une limite d’appel avec la fonction de dialplan `TIMEOUT(absolute)`, une fois que l’appel dépasse la limite définie, il sera dirigé vers l’extension T.
- **h** : Hangup. Il est appelé après que l’utilisateur a déconnecté l’appel.
- **i** : Invalid

## Variables

Dans l'Asterisk PBX, les variables peuvent être globales, spécifiques à un canal et spécifiques à l'environnement. Vous pouvez utiliser l'application NoOP() pour voir le contenu d'une variable dans la console. Elle peut utiliser une variable globale ou une variable spécifique à un canal comme arguments d'application. Une variable peut être référencée comme dans l'exemple suivant, où varname est le nom de la variable.

```
${varname}
```

Un nom de variable peut être une chaîne alphanumérique commençant par une lettre. Les noms de variables globales ne sont pas sensibles à la casse. Cependant, les variables système (définies par Asterisk ou par le canal) sont sensibles à la casse. Ainsi, la variable ${EXTEN} est différente de ${exten}.

### Global variables

Les variables globales peuvent être configurées dans la section [global] du fichier extensions.conf ou en utilisant l'application :

```
set(Global(variable)=content)
```

### Channel-specific variables

Les variables spécifiques à un canal sont configurées à l'aide de l'application set(). Chaque canal reçoit son propre espace de variables. Il n'y a aucune possibilité de collisions entre les variables de différents canaux. Une variable spécifique à un canal est détruite lorsque le canal raccroche. Certaines des variables les plus couramment utilisées sont :

- ${EXTEN} Extension composée
- ${CONTEXT} Contexte actuel
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Identifiant de l'appelant actuel
- ${PRIORITY} Priorité actuelle

Les autres variables spécifiques à un canal sont toutes en majuscules. Vous pouvez voir le contenu de plusieurs variables en utilisant l'application dumpchan(). Ci-dessous un extrait simple des variables dump-channel.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Sortie de Dumpchan :

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

La disposition des champs ci‑above est la sortie Asterisk 22 `DumpChan` (un vrai nom de canal `PJSIP/...`, les champs `CallerIDNum`/`ConnectedLineID`, et les lignes `Raw*`/`Transcode`/`BridgeID` que les canaux PJSIP remplissent). Contrairement à l'ancien pilote, un canal PJSIP ne définit pas automatiquement les variables de canal `SIPCALLID`/`SIPUSERAGENT` ; les détails SIP équivalents sont lus à la demande avec les fonctions de dialplan `PJSIP_HEADER()` et `CHANNEL()` — par exemple `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` et `${CHANNEL(rtp,dest)}` pour l'adresse RTP distante.

### Environment-specific variables

Les variables spécifiques à l'environnement peuvent être utilisées pour accéder aux variables définies dans le système d'exploitation. Vous pouvez définir des variables spécifiques à l'environnement en utilisant la fonction ENV(). Par exemple :

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

Certaines applications utilisent des variables pour l'entrée et la sortie de données. Vous pouvez définir des variables avant d'appeler l'application ou récupérer la variable après l'exécution de l'application. Par exemple : L'application Dial renvoie les variables suivantes :

- ${DIALEDTIME} -> Il s'agit du temps écoulé depuis la composition d'un canal jusqu'à sa déconnexion.
- ${ANSWEREDTIME} -> Il s'agit de la durée réelle de l'appel.
- ${DIALSTATUS} Il s'agit du statut de l'appel : o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Message d'erreur pour l'appel.

## Expressions

Les expressions peuvent être très utiles dans le dialplan. Elles sont utilisées pour manipuler des chaînes et effectuer des opérations mathématiques et logiques.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

La syntaxe des expressions est définie comme suit :

```
$[expression1 operator expression2]
```

Supposons que nous ayons une variable appelée « I » et que nous voulions ajouter 100 à cette variable :

```
$[${I}+100]
```

Lorsque Asterisk trouve une expression dans le dialplan, il remplace l’expression entière par la valeur résultante.

### Opérateurs

Les opérateurs suivants peuvent être utilisés pour construire des expressions. Il est important de respecter la priorité des opérateurs.

1. Parenthèses « () »
2. Opérateurs unaires « ! - »
3. Expression régulière « : =~ »
4. Opérateurs multiplicatifs « * / % »
5. Opérateurs additifs « + - »
6. Opérateurs de comparaison
7. Opérateurs logiques
8. Opérateurs conditionnels

#### Opérateurs mathématiques

- Addition (+)
- Soustraction (-)
- Multiplication (*)
- Division (/)
- Modulo (%)

#### Opérateurs logiques

- « AND » logique (&)
- « OR » logique (|)
- Complément unaire logique (!)

#### Opérateurs d’expression régulière

- Correspondance d’expression régulière (:)
- Correspondance exacte d’expression régulière (=~)

Une expression régulière est une chaîne de texte spéciale utilisée pour décrire un motif de recherche. Vous pouvez considérer les expressions régulières comme des jokers. Elles servent à faire correspondre une chaîne à un motif afin de vérifier la correspondance. Si la correspondance réussit et que l’expression régulière contient au moins une correspondance, la première correspondance est renvoyée ; sinon, le résultat est le nombre de caractères correspondants.

#### Opérateurs de comparaison

Le résultat d’une comparaison est 1 si la relation est vraie ou 0 si elle est fausse.

- = égal
- != différent
- < inférieur à
- > supérieur à
- <= inférieur ou égal à
- >= supérieur ou égal à

### LAB. Évaluez les expressions suivantes :

Placez ces expressions dans votre dialplan et utilisez l’application NoOP() pour les évaluer. Composez le 9002 et examinez les résultats dans la console Asterisk. Utilisez verbose 15 pour afficher les résultats.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Fonctions

Certaines applications ont été remplacées par des fonctions, qui permettent le traitement des variables d’une manière plus avancée que les seules expressions. Vous pouvez voir la liste complète des fonctions en exécutant la commande console suivante :

```
*CLI> core show functions
```

Longueur de chaîne : ${LEN(string)} renvoie la longueur de la chaîne

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Dans la première opération, le système affiche 5 comme résultat (le nombre de lettres du mot « fruit »). La seconde renvoie le nombre 4 (le nombre de lettres du mot « pear »). Sous‑chaînes : renvoie la sous‑chaîne, en commençant à la position définie par le paramètre « offset », avec la longueur de chaîne définie dans le paramètre « length ». Si l’offset est négatif, il commence de droite à gauche, à partir de la fin de la chaîne. Si la longueur est omise ou négative, elle prend toute la chaîne à partir de l’offset.

```
${string:offset:length }
```

Exemple #1 : Plusieurs sous‑chaînes

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Exemple #2 : Extraire l’indicatif régional des trois premiers chiffres.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Exemple #3 : Prend tous les chiffres de la variable ${EXTEN}, sauf l’indicatif régional.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenation de chaînes

Pour concaténer deux chaînes, écrivez‑les simplement l’une à la suite de l’autre.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Applications

Pour créer un dialplan, nous devons comprendre le concept d’applications. Vous utiliserez des applications pour gérer le canal dans le dialplan. Les applications sont implémentées dans plusieurs modules. Les applications disponibles dépendent des modules. Vous pouvez afficher toutes les applications Asterisk en utilisant la commande console :

```
*CLI> core show applications
```

Alternativement, vous pouvez afficher les détails d'une application spécifique en utilisant l'exemple suivant :

```
*CLI> core show application Dial
```

Pour créer un plan de numérotation simple, vous devez connaître quelques applications. Nous aborderons des exemples plus avancés plus tard dans le livre.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

Nous utiliserons ces applications (ci‑dessus) pour créer un plan de numérotation simple pour deux PBX de base.

### Answer()

[Synopsis] Répond à un canal s’il sonne [Description] Answer([delay]) : Si l’appel n’a pas été répondu, l’application y répondra. Sinon, elle n’a aucun effet sur l’appel. Si un délai est spécifié, Asterisk attendra le nombre de millisecondes indiqué dans ‘delay’ avant de répondre à l’appel.

### Dial()

La description suivante peut être obtenue en exécutant la commande **show application dial** dans le plan de numérotation. Pour faciliter la recherche, elle est reproduite ci‑dessous. La syntaxe de l’application Dial est également affichée ci‑dessous :

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

Cette application placera des appels vers un ou plusieurs canaux spécifiés. Dès qu’un des canaux demandés répond, le canal d’origine sera répondu—s’il n’a pas déjà été répondu. Ces deux canaux seront alors actifs dans un appel en pont. Tous les autres canaux demandés seront alors raccrochés. À moins qu’un délai d’attente ne soit spécifié, l’application Dial attendra indéfiniment jusqu’à ce qu’un des canaux appelés réponde, que l’utilisateur raccroche, ou que tous les canaux appelés soient occupés ou indisponibles. L’exécution du dial plan se poursuivra si aucun canal demandé ne peut être appelé ou si le délai d’attente expire. Cette application définit les variables de canal suivantes à la fin :

- DIALEDTIME - C’est le temps écoulé depuis le numérotation d’un canal jusqu’au moment où il est déconnecté.  
- ANSWEREDTIME - C’est la durée réelle de l’appel.  
- DIALSTATUS - C’est le statut de l’appel : o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE  

Pour les modes de confidentialité et de filtrage, la variable DIALSTATUS sera définie à DONTCALL si la partie appelée choisit d’envoyer l’appelant au script « Go Away ». La variable DIALSTATUS sera définie à TORTURE si la partie appelée veut envoyer l’appelant au script « torture ». Cette application signalera une terminaison normale si le canal d’origine raccroche ou si l’appel est mis en pont et que l’une des parties du pont met fin à l’appel. L’URL optionnelle sera envoyée à la partie appelée si le canal le prend en charge. Si la variable OUTBOUND_GROUP est définie, tous les canaux pairs créés par cette application seront inclus dans ce groupe (comme dans

```
Set(GROUP()=...).
```

The following table summarizes some of the most frequently used options for the application Dial. For the complete list, use the console command `core show application Dial`. In Asterisk 22 these options are separated from the channel and timeout by commas — for example `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Joue une annonce à la partie appelée, en utilisant `x` comme fichier. |
| `C` | Réinitialise le CDR pour cet appel. |
| `d` | Permet à l'utilisateur appelant de composer une extension à 1 chiffre pendant l'attente que l'appel soit répondu. Quitte vers cette extension si elle existe dans le contexte actuel, ou vers le contexte défini dans la variable `EXITCONTEXT`, si elle existe. |
| `D([called][:calling])` | Envoie les chaînes DTMF spécifiées après que la partie appelée a répondu, mais avant que l'appel ne soit mis en pont. La chaîne `called` est envoyée à la partie appelée et la chaîne `calling` à la partie appelante. Chaque paramètre peut être utilisé seul. |
| `f` | Force l'ID d'appelant du canal appelant à être défini sur l'extension associée au canal via un dial plan `hint`. Utile lorsque le PSTN n'autorise pas un ID d'appelant arbitraire. |
| `g` | Poursuit l'exécution du dial plan à l'extension actuelle si le canal de destination raccroche. |
| `G(context^exten^pri)` | Si l'appel est répondu, transfère la partie appelante à la priorité spécifiée et la partie appelée à priorité+1. Une extension (ou extension et contexte) peut être spécifiée ; sinon l'extension actuelle est utilisée. |
| `h` | Permet à la partie appelée de raccrocher en envoyant le chiffre DTMF `*`. |
| `H` | Permet à la partie appelante de raccrocher en envoyant le chiffre DTMF `*`. |
| `L(x[:y][:z])` | Limite l'appel à `x` ms, joue un avertissement lorsqu’il reste `y` ms, et répète l’avertissement toutes les `z` ms. Voir les variables `LIMIT_*` ci‑dessous. |
| `m([class])` | Fournit de la musique d’attente à la partie appelante jusqu’à ce que le canal demandé réponde. Une classe MusicOnHold spécifique peut être indiquée. |
| `r` | Indique la sonnerie à la partie appelante et ne transmet aucun son jusqu’à ce que le canal appelé réponde. |
| `S(x)` | Raccroche l’appel `x` secondes après que la partie appelée a répondu. |
| `t` | Permet à la partie appelée de transférer la partie appelante en envoyant la séquence DTMF définie dans `features.conf`. |
| `T` | Permet à la partie appelante de transférer la partie appelée en envoyant la séquence DTMF définie dans `features.conf`. |
| `w` | Permet à la partie appelée d’activer l’enregistrement en un clic en envoyant la séquence DTMF définie dans `features.conf`. |
| `W` | Permet à la partie appelante d’activer l’enregistrement en un clic en envoyant la séquence DTMF définie dans `features.conf`. |
| `k` | Permet à la partie appelée de mettre l’appel en parc en envoyant la séquence DTMF définie pour le parking d’appel dans `features.conf`. |
| `K` | Permet à la partie appelante de mettre l’appel en parc en envoyant la séquence DTMF définie pour le parking d’appel dans `features.conf`. |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`) : joue des sons pour l’appelant.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no` : joue des sons pour la partie appelée.
- `LIMIT_TIMEOUT_FILE` — fichier à jouer lorsque le temps est écoulé.
- `LIMIT_CONNECT_FILE` — fichier à jouer lorsque l’appel commence.
- `LIMIT_WARNING_FILE` — fichier à jouer comme avertissement lorsque `y` est défini. Le comportement par défaut est d’annoncer le temps restant.

Example:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

Dans l'exemple ci‑dessus, l'application composera le canal PJSIP correspondant. L’appelant et l’appelé peuvent tous deux transférer l’appel (Tt). De la musique d’attente sera entendue à la place du son de rappel. Si personne ne répond dans les 20 secondes, l’extension passera à la priorité suivante.

### Hangup()

Met fin au canal appelant [Description] Hangup([causecode]) : Cette application raccroche le canal appelant. Si un code de cause est fourni, la cause du raccrochage du canal sera définie sur la valeur indiquée.

### Goto()

Saute à une priorité, une extension ou un contexte particulier [Description] Goto([[context|]extension|]priority) : Cette application fait en sorte que le canal appelant continue l’exécution du dialplan à la priorité spécifiée. Si aucune extension spécifique (ou extension et contexte) n’est indiquée, cette application sautera à la priorité spécifiée de l’extension courante. Si la tentative de saut vers un autre emplacement du dialplan échoue, le canal continuera à la priorité suivante de l’extension courante.

## Construction d'un plan de numérotation

Pour créer un plan de numérotation simple, vous devez gérer tous les appels entrants et sortants en créant des contextes et des extensions. Dans cette section, nous vous montrerons comment construire les extensions les plus courantes.

### Numérotation entre extensions

Pour activer la numérotation entre extensions, nous pouvons utiliser la variable de canal ${EXTEN}, qui fait référence à l'extension composées. Par exemple, si la plage d'extensions se situe entre 4000 et 4999 et que toutes les extensions utilisent SIP, nous pourrions adopter la commande suivante :

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Dialing to an external destination

Pour composer une destination externe, vous pouvez préfixer le numéro composé avec une route. En Amérique du Nord, il est courant d’utiliser le 9 suivi du numéro à composer à l’extérieur. Si vous utilisez un canal analogique ou numérique vers le PSTN, la commande doit ressembler à ce qui suit : Si vous souhaitez utiliser le trunk SIP au lieu du DAHDI, utilisez le canal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

La ligne ci‑dessus vous permettra de composer le 9 puis le numéro souhaité. Dans l’exemple donné, vous utiliserez le premier canal DAHDI (DAHDI/1). Si vous avez plusieurs lignes et que celle‑ci est occupée, l’appel ne sera pas complété. Cependant, vous pouvez utiliser la ligne suivante pour choisir automatiquement le premier canal DAHDI disponible. Optionnellement, vous pouvez utiliser le trunk SIP à la place de DAHDI. Dans le formulaire PJSIP `Dial(PJSIP/number@siptrunk,...)`, le numéro composé est la partie utilisateur et `siptrunk` est l’endpoint configuré ci‑dessus.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

Le paramètre « g1 » recherchera le premier canal disponible dans le groupe, permettant l’utilisation de tous les canaux. En utilisant la ligne ci‑dessous, vous pourriez composer un numéro longue distance.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Composer le 9 pour obtenir une ligne PSTN

Si vous n’avez aucune restriction concernant les appels externes, vous pouvez simplifier et utiliser ce qui suit :

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Réception d'un appel dans l'extension opérateur

Dans l'exemple suivant, l'extension opérateur est 4000. La ligne PSTN est connectée à une interface FXO. Dans le fichier chan_dahdi.conf, le contexte spécifié est from-pstn. Tout appel provenant du PSTN sera acheminé vers le contexte from-pstn dans le dialplan. Cette ligne ne possède pas de numérotation directe entrante (DID) ; en conséquence, nous devrons recevoir l'appel via l'extension « s ». Si vous recevez depuis le trunk SIP, utilisez le contexte [from-sip].

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### Réception d'un appel en utilisant le numérotation directe entrante (DID)

Si vous avez une ligne numérique, vous recevrez l'extension composée. Dans ce cas, vous n'avez pas besoin de transférer l'appel à l'opérateur ; vous pouvez plutôt transférer l'appel directement vers la destination. Supposons que votre plage DID s'étende de 3028550 à 3028599 et que les quatre derniers chiffres soient transmis dans le DID. La configuration ressemblerait à l'exemple suivant :

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Appeler plusieurs extensions simultanément

Vous pouvez configurer Asterisk pour appeler une extension et, si elle n’est pas répondue, appeler plusieurs autres extensions simultanément, comme indiqué dans l’exemple suivant :

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

Dans cet exemple, lorsqu’une personne compose l’opérateur, le canal DAHDI/1 est d’abord essayé. Si personne ne répond après 15 secondes (timeout), les canaux DAHDI/1, DAHDI/2 et DAHDI/3 sonneront simultanément pendant encore 15 secondes.

### Routage par Caller ID

Dans cet exemple, vous pourriez appliquer des traitements différents en fonction du Caller ID, ce qui pourrait être utile pour les spammeurs d’appels. Par exemple:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

Dans cet exemple, nous avons ajouté une règle spéciale qui, si l’identifiant de l’appelant est 4832518888, lit un message depuis le fichier préalablement enregistré « I-have-moved-to-china ». Les autres appels sont acceptés comme d’habitude.

### Utilisation des variables dans le dialplan

Asterisk peut utiliser des variables globales et de canal dans le dialplan comme arguments pour certaines applications. Regardez les exemples suivants :

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

Utiliser des variables facilite les modifications futures. Si vous modifiez la variable, toutes les références sont immédiatement mises à jour.

### Enregistrement d’une annonce

Dans certaines des options abordées plus loin dans cette section, nous utiliserons des invites enregistrées. Voici une façon simple de les enregistrer. Nous utiliserons l’application `Record()` pour sauvegarder l’annonce à l’aide de son propre téléphone.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Ces instructions vous permettent d’enregistrer n’importe quel message depuis un softphone. Exemple : composer recordmenu depuis le softphone Les instructions appelleront l’enregistrement avec la variable ${EXTEN:6} sans les six premières lettres. En d’autres termes, l’instruction est équivalente à record(menu:gsm). Tout ce que vous avez à faire est de composer record + nom_du_fichier_à_enregistrer, appuyer sur # pour terminer l’enregistrement, et attendre d’entendre l’enregistrement.

### Réception des appels dans une réceptionniste numérique

Maintenant que nous disposons de quelques exemples simples, élargissons notre apprentissage des applications background() et goto(). La clé des systèmes interactifs dans Asterisk est l’application background(), qui vous permet d’exécuter un fichier audio qui, lorsque l’appelant appuie sur une touche, est interrompu afin d’envoyer l’appel vers l’extension composées. Syntaxe de l’application background() :

```
exten=>extension, priority, background(filename)
```

Une autre application très utile est `goto()`. Comme son nom l'indique, elle saute vers le contexte, l'extension et la priorité indiqués. Syntaxe de l'application `goto()` :

```
exten=>extension, priority,goto(context, extension, priority)
```

Formats valides pour la commande goto() :

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

Dans l'exemple suivant, nous allons créer un réceptionniste numérique. Il est très simple de modifier le fichier extensions.conf et de configurer les extensions suivantes :

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

Les extensions SIP utilisent `PJSIP/` et les extensions IAX utilisent `IAX2/` — les deux pilotes sont fournis avec Asterisk 22, bien que `chan_iax2` soit désormais considéré comme hérité et que SIP/PJSIP soit préféré.

Dans le fichier menu1.gsm, enregistrez le message « press the extension or wait for the operator ». Lorsque l'utilisateur compose le numéro 6000, il sera dirigé vers l'extension 6000. À ce stade, vous devez avoir une compréhension claire de l’utilisation de plusieurs applications, notamment answer(), background(), goto(), hangup() et playback(). Si vous n’avez pas une compréhension claire, veuillez relire ce chapitre jusqu’à ce que vous vous sentiez à l’aise avec le contenu. Vous utiliserez très souvent l’application background. Une fois que vous comprendrez les bases des extensions, des priorités et des applications, il sera facile de créer un plan de numérotation simple. Ces concepts seront approfondis plus tard dans le livre, et vous verrez que le plan de numérotation deviendra plus puissant.

## Résumé

Dans ce chapitre, vous avez appris que les fichiers de configuration sont stockés dans le répertoire /etc/asterisk. Pour utiliser Asterisk, il faut d'abord configurer les canaux (par ex., pjsip, dahdi, iax). Trois grammaires différentes existent pour les fichiers de configuration : groupe simple, héritage d'objet et entité complexe. Le plan de numérotation est créé dans le fichier extensions.conf et constitue un ensemble de contextes et d'extensions. Dans le plan de numérotation, chaque extension déclenche une application. Vous avez appris à utiliser les applications playback, background, dial, goto, hangup et answer.

## Quiz

1. Les fichiers de configuration des canaux sont (choisissez toutes les réponses qui s'appliquent) :
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Sur Asterisk 22, le pair `chan_sip` unique `[6001]` (`type=friend`/`host=dynamic`) est remplacé dans `pjsip.conf` par quel ensemble d’objets associés ?
   - A. Un `type=peer` et un `type=user`
   - B. Un `type=endpoint`, un `type=auth` et un `type=aor`
   - C. Un seul `type=friend`
   - D. Un `type=transport` et un `type=global`
3. Définir un contexte dans le fichier de configuration du canal est important car il définit le contexte entrant pour les appels provenant de ce canal — un appel du canal est traité dans le contexte correspondant dans `extensions.conf`.
   - A. Vrai
   - B. Faux
4. Les principales différences entre les applications `Playback()` et `Background()` sont (choisissez deux) :
   - A. Playback lit une invite mais n’attend pas de chiffres.
   - B. Background lit une invite mais n’attend pas de chiffres.
   - C. Background lit un message et attend que des chiffres soient composés.
   - D. Playback lit un message et attend que des chiffres soient composés.
5. Lorsqu’un appel entre dans Asterisk via une carte d’interface téléphonique (FXO) sans DID, il est traité dans l’extension spéciale :
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Les formats valides pour l’application `Goto()` sont (choisissez trois) :
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. Le motif `_7[1-5]XX` correspond (choisissez toutes les réponses qui s’appliquent) :
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. Dans `Dial(PJSIP/${EXTEN},20,tTm)`, que fait l’option `m` ?
   - A. Limite l’appel à une durée maximale.
   - B. Fournit de la musique d’attente à l’appelant au lieu du son de sonnerie jusqu’à ce que le canal réponde.
   - C. Envoie les chiffres DTMF après que le destinataire a répondu.
   - D. Force l’identifiant de l’appelant en utilisant un indice du plan de numérotation.
9. Dans la grammaire d’héritage des options utilisée par `chan_dahdi.conf`, vous :
   - A. Définissez l’objet sur une seule ligne.
   - B. Définissez d’abord les options et déclarez les objets sous les options définies.
   - C. Définissez un contexte séparé pour chaque objet.
10. Les priorités dans une extension doivent être numérotées consécutivement (1, 2, 3, …) et ne peuvent pas utiliser `n`.
    - A. Vrai
    - B. Faux

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
