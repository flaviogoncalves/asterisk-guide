# Utilisation des fonctionnalités du PBX

Dans les systèmes SIP, la plupart des fonctions téléphoniques sont implémentées dans l'endpoint. Une grande variété de téléphones SIP et de fabricants existent, et l'interopérabilité n'est pas garantie. L'équipe de développement d'Asterisk a réalisé un travail remarquable en implémentant la plupart des fonctions dans le PBX lui‑même, rendant Asterisk presque indépendant de l'endpoint. Cependant, il arrive parfois que la même fonction soit fournie à la fois par le téléphone et par Asterisk. L'intégration du téléphone et du PBX représente la prochaine frontière en matière d'utilisabilité, où les systèmes propriétaires concentrent leurs efforts aujourd'hui. Dans ce chapitre, vous apprendrez à exploiter la plupart de ces fonctions.

## Objectifs

- Stationnement d'appel
- Ramassage d'appel
- Transfert d'appel
- Conférence d'appel (ConfBridge)
- Enregistrement d'appel
- Musique d'attente

## Où les fonctionnalités sont implémentées

Tout d'abord, il est important de comprendre quand les fonctionnalités du PBX sont exécutées versus quand le téléphone effectue tout le travail. Par exemple, vous pouvez transférer un appel en utilisant le bouton TRANSFER sur le téléphone ou en composant # (transfert inconditionnel exécuté par le PBX lui‑même).

## Fonctionnalités implémentées par Asterisk

Ces fonctionnalités sont implémentées dans le standard téléphonique par le code Asterisk :

- Musique d'attente
- Parking d'appel
- Capture d'appel
- Enregistrement d'appel
- Salle de conférence ConfBridge
- Transfert d'appel (aveugle et consultatif)

## Features usually implemented by the dial plan

These features need to be programmed in the Asterisk dial plan (extensions.conf):

- Renvoi d'appel en cas d'occupation
- Renvoi d'appel immédiat
- Renvoi d'appel lorsqu'aucune réponse
- Filtrage d'appels (liste noire)
- Ne pas déranger
- Rappel

## Fonctionnalités généralement implémentées par le téléphone

![Où les fonctionnalités du standard téléphonique sont généralement implémentées : dans Asterisk même, dans le dial plan, ou dans le téléphone](../images/13-pbx-features-fig01.png)

- Mise en attente d’appel
- Transfert aveugle
- Transfert consultatif
- Conférence à trois
- Indicateur de message en attente

## Le fichier de configuration des fonctionnalités

Certaines des fonctionnalités présentées dans ce chapitre sont configurées dans le fichier de configuration features.conf. Il est possible de modifier le comportement de certaines fonctionnalités en modifiant ce fichier. Nous avons inclus l'extrait pertinent ci‑dessous. Dans les sections suivantes de ce chapitre, nous décrirons chaque fonctionnalité. Extrait du fichier d’exemple (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Depuis Asterisk 12, le stationnement d’appels a été déplacé hors de `features.conf` vers son propre module, `res_parking`, avec une configuration dans `res_parking.conf`. Le bloc parking‑lot ci‑dessous (`parkext`, `parkpos`, `context`, `parkingtime`, etc.) se trouve dans `res_parking.conf`. La section `[featuremap]` (les codes de fonctionnalités DTMF, y compris `parkcall`) reste dans `features.conf`.

Les options du parking‑lot se trouvent dans `res_parking.conf`. Un parking‑lot nommé `default` existe toujours, même s’il n’est pas présent dans le fichier de configuration. L’extrait ci‑dessous est tiré du Asterisk 22 `res_parking.conf.sample` :

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

Les codes de fonctionnalités DTMF (y compris le `parkcall` en une étape) restent dans la section `[featuremap]` de `features.conf` :

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## Transfert d'appel

Le transfert d'appel peut être implémenté par le téléphone, par l'ATA ou par Asterisk lui‑même. Consultez le manuel de votre téléphone pour comprendre comment les appels sont transférés. Si votre téléphone ne prend pas en charge le transfert d'appel, vous pouvez utiliser Asterisk pour accomplir cette tâche. Le transfert d'appel est implémenté de deux manières différentes.

La première consiste à utiliser la fonction de transfert aveugle : composer # suivi du numéro à transférer. Parfois vous utiliserez la fonction de transfert de votre téléphone IP ou de votre softphone IP. Vous pouvez modifier le caractère de transfert en éditant le paramètre blindxfer dans le fichier features.conf.

Vous pouvez activer le transfert assisté dans Asterisk en supprimant le ; devant le paramètre atxfer dans le fichier features.conf. Pendant une conversation, vous appuyez sur *2. Asterisk dira « transfer » et vous donnera une tonalité de numérotation. L'appelant est envoyé en musique d'attente. Après avoir parlé à la personne de destination et raccroché le téléphone, le système relie l'appelant à la destination.

![Transfert d'appel : les étapes d'un transfert aveugle (appuyez sur # pendant l'appel) et d'un transfert assisté (appuyez sur *2)](../images/13-pbx-features-fig03.png)

### Liste des tâches de configuration

1. Pour un endpoint PJSIP, assurez‑vous que l'option `direct_media` est définie sur `no` (afin que le média transite par Asterisk et que les codes de fonction soient détectés), ou utilisez une option `t`/`T` dans l'application `Dial()`.

## Call parking

Cette fonctionnalité est utilisée pour mettre un appel en attente. Cela aide, par exemple, lorsque vous répondez à un appel téléphonique en dehors de votre pièce et que vous souhaitez transférer l’appel à votre bureau. Vous pouvez le faire en plaçant l’appel dans une extension. Une fois arrivé à votre bureau, composez simplement le numéro de l’extension de parking pour récupérer l’appel.

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

Par défaut, l’extension 700 est utilisée pour mettre un appel en attente. Au milieu d’une conversation, appuyez sur # pour transférer l’appel vers l’extension 700. Asterisk annoncera alors votre extension de parking, comme 701 ou 702. Raccrochez le téléphone, et l’appelant sera mis en attente. Allez à votre téléphone de bureau et composez l’extension de parking annoncée pour récupérer l’appel. Si l’appelant reste en attente longtemps, la fonction de temporisation se déclenchera et l’extension d’origine sonnera de nouveau.

### Configuration task list

Suivez les étapes ci‑dessous pour activer le parking d’appels. Étape 1 : Rendre le parking accessible depuis votre dialplan (obligatoire). Le parking par défaut a `context` `parkedcalls` (défini dans `res_parking.conf`). Incluez ce contexte dans le contexte depuis lequel vos téléphones composent, dans `extensions.conf` :

```
include => parkedcalls
```

Étape 2 : Testez la fonction de parking d’appels en composant #700. Remarques :

- L’extension de parking ne sera pas affichée dans la commande CLI `dialplan show`.
- Il est nécessaire de recharger le module de parking après avoir modifié le fichier de configuration du parking : `module reload res_parking.so`. Pour les changements de `features.conf`, `module reload features.so`.
- Pour mettre un appel en attente, vous devez le transférer vers #700. Vérifiez les options `t` et `T` dans l’application `Dial()`.

## Call pickup

Le call pickup vous permet de capturer un appel d’un collègue appartenant au même groupe d’appels. Cela évite, par exemple, de devoir se lever pour répondre à un appel qui sonne pour une autre personne dans votre pièce, mais qui n’est pas présente. En composant *8, vous pouvez capturer un appel au sein de votre groupe d’appels. Ce numéro peut être modifié dans le fichier `features.conf`.

![Call pickup: members can only capture calls within their own group; the operator (pickupgroup=1,2,3) can pick up calls from every group](../images/13-pbx-features-fig05.png)

### Configuration task list

Suivez les étapes ci‑dessous pour configurer la fonction de call pickup. Étape 1 : configurez un groupe d’appels pour vos extensions. Cela se fait dans le fichier de configuration du canal (pjsip.conf, iax.conf, chan_dahdi.conf). Pour les endpoints PJSIP, définissez `call_group` et `pickup_group` dans la section endpoint de `pjsip.conf` (pjsip.conf utilise des noms d’options snake_case). Cette tâche est obligatoire.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```

Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (call conference)

Il existe différentes manières de mettre en place une conférence sur Asterisk. La première option consiste simplement à utiliser la capacité de conférence à trois voies du téléphone. En utilisant cette fonction sur le téléphone, vous n’avez pas besoin de support côté serveur. Cependant, lorsque vous souhaitez une conférence avec plus de 3 personnes, vous devez créer une salle de conférence. L’application de conférence moderne d’Asterisk est ConfBridge (`app_confbridge`).

ConfBridge prend en charge les conférences vocales HD et la vidéoconférence. Certaines limites s’appliquent à la vidéoconférence, comme l’absence de transcodage — tous les participants doivent utiliser le même codec et le même profil. La vidéoconférence utilise un mode « follow‑the‑talker », affichant l’image de la dernière personne à parler. Vous pouvez facilement configurer de nouveaux menus DTMF dans ConfBridge.

ConfBridge remplace l’ancienne application MeetMe, qui a été dépréciée dans Asterisk 19. MeetMe est toujours présent dans l’arbre source d’Asterisk 22, mais il dépend de DAHDI et n’est pas compilé par défaut, donc sur une installation typique de PJSIP il est simplement indisponible — ConfBridge est l’application de conférence prise en charge. Contrairement à MeetMe, ConfBridge **ne** nécessite **pas** DAHDI ni de source de timing matérielle : il s’appuie sur l’interface de timing intégrée d’Asterisk (`res_timing_timerfd` sur Linux, ou `res_timing_pthread`), ainsi aucun module `dahdi_dummy` n’est requis. Si vous migrez depuis un système plus ancien qui utilisait `MeetMe()` et `meetme.conf`, remplacez‑les par `ConfBridge()` et `confbridge.conf` comme décrit ci‑dessous.

### ConfBridge

Pour démarrer une salle de conférence, la syntaxe est indiquée ci‑dessous.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Pour obtenir une description complète de la commande, vous pouvez utiliser **core show application confbridge**.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

Comme vous pouvez le voir ci‑dessus, il existe trois arguments importants, chacun correspondant à un type de section dans `confbridge.conf`. **bridge_profile** (une section `type=bridge`) : ici vous choisissez le nombre maximal de participants (`max_members`), l’enregistrement (`record_conference`), `video_mode`, et de nombreux autres paramètres globaux du pont.

Il n’est pas judicieux de reproduire l’ensemble du fichier d’exemple ici, alors laissez‑moi vous donner un exemple simple sur la façon de configurer un **bridge_profile** dans le fichier **confbridge.conf**.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (une section `type=user`) : ici vous définissez des options spécifiques à chaque utilisateur, comme si l'utilisateur est un administrateur (`admin=yes`), s'il démarre en muet (`startmuted=yes`), la musique d’attente, et de nombreuses autres options par utilisateur. Exemple:

```
[admin_user]
type=user
admin=yes
```

**menu** (une section `type=menu`) : ici vous définissez le mappage du clavier (DTMF) pour la conférence — par exemple quelle touche active/désactive le mute, ajuste le volume, ou quitte la conférence. Consultez le fichier `confbridge.conf.sample` pour voir toutes les actions disponibles. Exemple:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### Fonctions Confbridge

Les options du pont de conférence peuvent être transmises dynamiquement dans le dialplan en utilisant la fonction CONFBRIDGE(). Voir les exemples ci‑dessous :

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Commandes d'administration ConfBridge et migration depuis MeetMe

Si vous venez de MeetMe, les fonctions d'administration que vous utilisiez via `MeetMeAdmin()` et l'option `a` (admin) sont maintenant exprimées à travers le **profil d'utilisateur admin** (`admin=yes`) plus les actions du **menu**. Un administrateur qui se connecte avec un profil admin et un menu contenant des actions d'administration peut verrouiller la salle, expulser des utilisateurs et mettre en sourdine les participants en direct depuis le clavier. Les actions de menu pertinentes dans `confbridge.conf` sont :

- `admin_kick_last` -- expulser le dernier utilisateur qui a rejoint
- `admin_toggle_mute_participants` -- mettre en sourdine / réactiver le son de tous les participants non‑admin
- `toggle_mute` -- mettre en sourdine / réactiver votre propre son
- `participant_count` -- annoncer le nombre de participants
- `leave_conference` -- quitter le pont et continuer dans le dialplan

Ces actions remplacent les indicateurs d'option MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) et les commandes `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). Sur une installation moderne de PJSIP, vous ne chargerez plus `app_meetme` du tout ; toute la configuration de conférence vit dans `confbridge.conf`, et les modifications sont appliquées avec `module reload app_confbridge.so` (la logique de ConfBridge réside dans `app_confbridge` ; il n'existe aucun module `res_confbridge`).

### Exemple ConfBridge

Pour créer une salle de conférence accessible à l'extension 500, dans `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Le premier appelant qui compose le 500 crée la conférence `101` ; les appelants suivants le rejoignent. Les profils et menus référencés ici (`default_bridge`, `default_user`, `sample_user_menu`) sont définis dans `confbridge.conf`. Pour exiger un PIN, définissez `pin=` dans le profil utilisateur ; pour faire d'un participant un administrateur de conférence, attribuez‑lui un profil utilisateur avec `admin=yes`.

## Enregistrement d'appel

Il existe plusieurs façons d’enregistrer un appel dans Asterisk. Vous pouvez utiliser l’application `MixMonitor()` pour enregistrer facilement les appels. (L’application plus ancienne `Monitor`, qui enregistrait deux fichiers séparés, a été supprimée ; utilisez `MixMonitor` à la place.)

### Utilisation de l’application MixMonitor

L’application `MixMonitor` enregistre l’audio du canal actuel dans le fichier spécifié. Si le nom de fichier est un chemin absolu, il utilise ce chemin. Sinon, il crée le fichier dans le répertoire de surveillance configuré dans asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

Enregistre un appel et mélange l’audio pendant l’enregistrement. Syntaxe : `MixMonitor(filename.extension[,options[,command]])`. Enregistre l’audio du canal actuel dans le fichier spécifié. Options valides :

- a - Ajoute au fichier au lieu de l’écraser.
- b - N’enregistre l’audio dans le fichier que tant que le canal est en pont.
- Note : n’inclut pas les conférences.
- v(<x>) - Ajuste le volume audible d’un facteur de <x> (de -4 à 4)
- V(<x>) - Ajuste le volume parlé d’un facteur de <x> (de -4 à 4)
- W(<x>) - Ajuste à la fois les volumes audible et parlé d’un facteur de <x> (de -4 à 4)
- <command> sera exécutée lorsque l’enregistrement sera terminé. Toute chaîne correspondant à ^{X} sera déséchappée en ${X} et toutes les variables seront évaluées à ce moment‑là. La variable MIXMONITOR_FILENAME contiendra le nom du fichier utilisé pour l’enregistrement.

Une ressource intéressante est la fonction d’enregistrement en un clic `automixmon`, qui permet à une partie de composer un code DTMF (l’exemple `features.conf` suggère `*3` ; il n’existe pas de valeur par défaut intégrée, vous devez donc la définir) pendant un appel pour démarrer immédiatement (et désactiver) l’enregistrement. Elle repose sur MixMonitor, donc elle écrit un seul fichier mixé. Exemple:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Les options `X` et `x` activent la fonction MixMonitor en une touche pour l'appelant et le destinataire respectivement. Comme MixMonitor enregistre un seul fichier mixé, il n'est pas nécessaire de combiner des fichiers IN/OUT séparés par la suite (l'ancienne approche `automon`/`Monitor`, qui produisait deux fichiers pour `soxmix`, a été supprimée avec l'application `Monitor`).

Si vous ne souhaitez pas utiliser Set() avant l'application Dial(), vous pouvez définir cela dans la section globals :

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Musique d’attente

La musique d’attente (MOH) a changé plusieurs fois entre les versions 1.0, 1.2 et 1.4. Dans la version la plus récente, MOH utilise par défaut le mode « FILE-BASED ». En d’autres termes, Asterisk fournira les fichiers MOH dans des formats tels que g729, alaw, ulaw et gsm. Ainsi, il n’est pas nécessaire de transcoder la musique avant de l’envoyer au canal. Cela économise du temps processeur, ce qui est une modification bienvenue pour ceux qui travaillent avec des systèmes de production.

Dans les versions plus anciennes, MOH était généralement fourni en MP3 (il peut encore être configuré ainsi). Fournir MOH en MP3 oblige Asterisk à transcoder, consommant ainsi une précieuse puissance CPU dans le processus.

Le nouveau fichier de configuration est présenté ci‑dessous. Notez que la classe par défaut utilise maintenant le mode de fichier natif = files. Tous les autres modes sont commentés. Chaque section représente une classe. La seule classe non commentée à ce stade est default. Si vous souhaitez avoir différentes classes pour différents fichiers, vous devrez créer de nouvelles sections (classes).

![Exemple de configuration musiconhold.conf, répertoriant les modes MOH valides (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### Tâches de configuration du MOH

Now, to use music on hold, set the MOH class in the channel configuration files (chan_dahdi.conf, pjsip.conf, iax.conf, and so on). For PJSIP endpoints, set `moh_suggest` in the endpoint section of `pjsip.conf` (the legacy `musicclass` option name applies to chan_dahdi and other channel drivers, not to PJSIP). The freeplay tunes installed are now in wav format. At the time of installation, you can select (using make menuselect) the MOH file formats available. If you want to add new MOH files, you will have to supply them in the required formats. For example:

In `/etc/asterisk/chan_dahdi.conf`, add the `musiconhold` line:

```
[channels]
musiconhold=default
```

Ensuite, modifiez `/etc/asterisk/musiconhold.conf` pour définir cette classe :

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Dans le dial plan, vous pouvez démarrer la musique d’attente sur un canal avec `StartMusicOnHold` (et l’arrêter avec `StopMusicOnHold`) :

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Pour jouer de la musique d’attente pendant un temps fixe à titre de test rapide, utilisez l’application `MusicOnHold` avec une durée (en secondes) :

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Cartes d'application

Les cartes d'application vous permettent d'ajouter de nouvelles fonctionnalités en utilisant la section `[applicationmap]` du fichier features.conf. Supposons que vous deviez identifier le type de client auquel vous répondez dans un centre d'appels. Vous pourriez créer une carte d'application pour chaque type de client, ce qui pourrait compter le nombre de clients répondus par type.

## Summary

Dans ce chapitre, vous avez découvert où résident les fonctions PBX d’Asterisk — certaines dans le cœur, d’autres dans le dialplan, et d’autres encore sur le téléphone — et comment les codes de fonction DTMF sont mappés dans la section `[featuremap]` de `features.conf`. Vous avez configuré le **transfert d’appel** (aveugle et assisté) et le **parking d’appel** (`res_parking.conf`, avec les options de numérotation `k`/`K` et le lot `parkedcalls`), le **ramassage d’appel** par groupe, et la **conférence** avec **ConfBridge** (profils de pont/utilisateur/menu `confbridge.conf`), qui remplace l’ancien MeetMe. Vous avez mis en place l’**enregistrement en un clic** avec MixMonitor (`automixmon`, les options de numérotation `X`/`x` et `DYNAMIC_FEATURES`), configuré la **musique d’attente**, et vu comment les **mappages d’application** vous permettent de lier votre propre logique de dialplan à une séquence DTMF. Avec ces blocs de construction, vous pouvez fournir les fonctionnalités quotidiennes attendues par les utilisateurs d’un PBX d’entreprise.

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
