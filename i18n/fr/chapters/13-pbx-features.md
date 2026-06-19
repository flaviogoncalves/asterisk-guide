# Utilisation des fonctionnalités PBX

Dans les systèmes SIP, la plupart des fonctionnalités téléphoniques sont implémentées au niveau de l'endpoint. Il existe une grande variété de téléphones SIP et de fabricants, et l'interopérabilité n'est pas garantie. L'équipe de développement d'Asterisk a accompli un travail remarquable en implémentant la plupart des fonctionnalités directement dans le PBX, rendant Asterisk presque indépendant de l'endpoint. Cependant, vous constaterez parfois que la même fonction est assurée à la fois par le téléphone et par Asterisk lui-même. L'intégration du téléphone et du PBX est la prochaine frontière en matière de convivialité, et c'est là que les systèmes propriétaires concentrent leurs efforts actuellement. Dans ce chapitre, vous apprendrez à utiliser la plupart de ces fonctionnalités.

## Objectifs

À la fin de ce chapitre, vous serez capable de comprendre et d'utiliser :

- Le parcage d'appel (Call Parking)
- La prise d'appel (Call Pickup)
- Le transfert d'appel (Call Transfer)
- La conférence téléphonique (ConfBridge)
- L'enregistrement d'appel (Call Recording)
- La musique d'attente (Music on hold)

## Où les fonctionnalités sont-elles implémentées ?

Avant tout, il est important de comprendre quand les fonctionnalités du PBX sont exécutées et quand le téléphone effectue tout le travail. Par exemple, vous pouvez transférer un appel en utilisant le bouton TRANSFER du téléphone ou en composant # (transfert inconditionnel exécuté par le PBX lui-même).

## Fonctionnalités implémentées par Asterisk

Ces fonctionnalités sont implémentées dans le PBX par le code Asterisk :

- Musique d'attente
- Parcage d'appel
- Prise d'appel
- Enregistrement d'appel
- Salle de conférence ConfBridge
- Transfert d'appel (aveugle et assisté)

## Fonctionnalités généralement implémentées par le dialplan

Ces fonctionnalités doivent être programmées dans le dialplan d'Asterisk (extensions.conf) :

- Renvoi d'appel sur occupation
- Renvoi d'appel immédiat
- Renvoi d'appel sur non-réponse
- Filtrage d'appel (liste noire)
- Ne pas déranger (Do not disturb)
- Rappel automatique

## Fonctionnalités généralement implémentées par le téléphone

Ces fonctionnalités sont implémentées par le firmware du téléphone :

![Où les fonctionnalités PBX sont généralement implémentées : dans Asterisk lui-même, dans le dialplan, ou dans le téléphone](../images/13-pbx-features-fig01.png)

- Mise en attente d'appel
- Transfert aveugle
- Transfert assisté
- Conférence à trois
- Indicateur de message en attente

## Le fichier de configuration des fonctionnalités

Certaines des fonctionnalités présentées dans ce chapitre sont configurées dans le fichier de configuration features.conf. Il est possible de modifier le comportement de certaines fonctionnalités en modifiant ce fichier. Nous avons inclus l'extrait pertinent ci-dessous. Dans les sections suivantes de ce chapitre, nous décrirons chaque fonctionnalité. Extrait du fichier exemple (Asterisk 22)

![La section `[featuremap]` de features.conf, avec les codes de fonctionnalités DTMF par défaut](../images/13-pbx-features-fig02.png)

Depuis Asterisk 12, le parcage d'appel a été déplacé hors de `features.conf` vers son propre module, `res_parking`, avec une configuration dans `res_parking.conf`. Le bloc parking-lot ci-dessous (`parkext`, `parkpos`, `context`, `parkingtime`, etc.) se trouve dans `res_parking.conf`. La section `[featuremap]` (les codes de fonctionnalités DTMF, incluant `parkcall`) reste dans `features.conf`.

Les options de parking-lot se trouvent dans `res_parking.conf`. Un parking-lot nommé `default` existe toujours, même s'il n'est pas présent dans le fichier de configuration. L'extrait ci-dessous est tiré du fichier `res_parking.conf.sample` d'Asterisk 22 :

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

Les codes de fonctionnalités DTMF (incluant le `parkcall` en une étape) restent dans la section `[featuremap]` de `features.conf` :

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transfert d'appel

Le transfert d'appel peut être implémenté par le téléphone, par un ATA ou par Asterisk lui-même. Reportez-vous au manuel de votre téléphone pour comprendre comment les appels sont transférés. Si votre téléphone ne prend pas en charge le transfert d'appel, vous pouvez utiliser Asterisk pour accomplir cette tâche. Le transfert d'appel est implémenté de deux manières différentes. La première consiste à utiliser la fonctionnalité de transfert aveugle : composez # suivi du numéro vers lequel transférer l'appel. Parfois, vous utiliserez la fonctionnalité de transfert de votre téléphone IP ou de votre softphone IP. Vous pouvez modifier le caractère de transfert en éditant le paramètre blindxfer dans le fichier features.conf. Vous pouvez activer le transfert assisté dans Asterisk en supprimant le ; devant le paramètre atxfer dans le fichier features.conf. Pendant une conversation, vous appuierez sur *2. Asterisk dira « transfer » et vous donnera une tonalité. L'appelant est envoyé vers la musique d'attente. Après avoir parlé à la personne destinataire et raccroché le téléphone, le système relie l'appelant au destinataire.

![Transfert d'appel : les étapes pour un transfert aveugle (appuyez sur # pendant l'appel) et un transfert assisté (appuyez sur *2)](../images/13-pbx-features-fig03.png)

### Liste des tâches de configuration

1. Pour un endpoint PJSIP, assurez-vous que l'option `direct_media` est réglée sur `no` (afin que les médias transitent par Asterisk et que les codes de fonctionnalités soient détectés), ou utilisez une option `t`/`T` dans l'application `Dial()`

## Parcage d'appel

Cette fonctionnalité est utilisée pour parquer un appel. Cela aide, par exemple, lorsque vous répondez à un appel téléphonique en dehors de votre bureau et que vous souhaitez transférer l'appel vers votre poste. Vous pouvez y parvenir en parquant l'appel dans une extension. Une fois arrivé à votre bureau, composez simplement le numéro de l'extension de parcage pour récupérer l'appel.

![Parcage d'appel : composez 700 pour parquer un appel dans le premier emplacement libre (701–720) ; Asterisk annonce l'emplacement, que vous composez depuis n'importe quel téléphone pour récupérer l'appel](../images/13-pbx-features-fig04.png)

Par défaut, l'extension 700 est utilisée pour parquer un appel. Au milieu d'une conversation, appuyez sur # pour transférer l'appel vers l'extension 700. Asterisk annoncera alors votre extension de parcage, telle que 701 ou 702. Raccrochez le téléphone, et l'appelant sera mis en attente. Allez à votre téléphone de bureau et composez l'extension de parcage annoncée pour récupérer l'appel. Si l'appelant reste parqué trop longtemps, la fonctionnalité de timeout se déclenchera et l'extension initialement appelée sonnera à nouveau.

### Liste des tâches de configuration

Suivez les étapes ci-dessous pour activer le parcage d'appel. Étape 1 : Rendez le parking-lot accessible depuis votre dialplan (requis). Le `context` du parking-lot par défaut est `parkedcalls` (défini dans `res_parking.conf`). Incluez ce context dans le context depuis lequel vos téléphones composent, dans `extensions.conf` :

```
include => parkedcalls
```

Étape 2 : Testez la fonctionnalité de parcage d'appel en composant #700. Notes :

- L'extension de parcage ne sera pas affichée dans la commande CLI dialplan show.
- Il est nécessaire de recharger le module de parcage après avoir modifié le fichier de configuration du parcage : `module reload res_parking.so`. Pour les modifications de features.conf, `module reload features.so`.
- Pour parquer un appel, vous devez transférer vers #700. Vérifiez les options `t` et `T` dans l'application `Dial()`.

## Prise d'appel

La prise d'appel vous permet de capturer un appel provenant d'un collègue dans le même groupe d'appel. Cela permettrait d'éviter, par exemple, d'avoir à se lever pour prendre un appel qui sonne pour une autre personne dans votre pièce, mais qui n'est pas présente. En composant *8, vous pouvez capturer un appel au sein de votre groupe d'appel. Ce numéro peut être modifié dans le

```
features.conf file.
```

![Prise d'appel : les membres ne peuvent capturer que les appels au sein de leur propre groupe ; l'opérateur (pickupgroup=1,2,3) peut prendre les appels de chaque groupe](../images/13-pbx-features-fig05.png)

### Liste des tâches de configuration

Suivez les étapes ci-dessous pour configurer la fonctionnalité de prise d'appel. Étape 1 : Configurez un groupe d'appel pour vos extensions. Cela se fait dans le fichier de configuration du canal (pjsip.conf, iax.conf, chan_dahdi.conf). Pour les endpoints PJSIP, définissez `call_group` et `pickup_group` dans la section endpoint de `pjsip.conf` (pjsip.conf utilise des noms d'options en snake_case). Cette tâche est requise.

Pour PJSIP (pjsip.conf) :
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```

Étape 2 : Modifiez le numéro de la fonctionnalité de prise d'appel (optionnel). Ceci est défini dans la section `[general]` de `features.conf`, et non dans `pjsip.conf` :

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conférence (conférence téléphonique)

Il existe différentes manières d'implémenter une conférence sur Asterisk. La première option consiste simplement à utiliser la capacité de conférence à trois du téléphone. En utilisant cette fonctionnalité dans le téléphone, vous n'avez besoin d'aucun support sur le serveur lui-même. Cependant, lorsque vous souhaitez une conférence avec plus de 3 personnes, vous devez exécuter une salle de conférence. L'application de conférence moderne d'Asterisk est ConfBridge (`app_confbridge`).

ConfBridge prend en charge les conférences voix HD et la visioconférence. Il existe certaines limitations pour la visioconférence, comme l'absence de transcodage — tous les participants doivent utiliser le même codec et le même profil. La visioconférence utilise un mode « follow-the-talker », affichant l'image de la dernière personne à avoir parlé. Vous pouvez facilement configurer de nouveaux menus DTMF dans ConfBridge.

ConfBridge remplace l'ancienne application MeetMe, qui a été dépréciée dans Asterisk 19 et supprimée dans Asterisk 21. Contrairement à MeetMe, ConfBridge ne nécessite **pas** DAHDI ou une source de synchronisation matérielle : il s'appuie sur l'interface de synchronisation intégrée d'Asterisk (`res_timing_timerfd` sur Linux, ou `res_timing_pthread`), donc aucun module `dahdi_dummy` n'est nécessaire. Si vous migrez depuis un ancien système qui utilisait `MeetMe()` et `meetme.conf`, remplacez-les par `ConfBridge()` et `confbridge.conf` comme décrit ci-dessous.

### ConfBridge

Pour démarrer une salle de conférence, la syntaxe est listée ci-dessous.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Pour obtenir une description complète de la commande, vous pouvez utiliser core show application confbridge.

![Sortie de `core show application confbridge`, montrant le synopsis, la syntaxe, et les arguments bridge_profile, user_profile et menu](../images/13-pbx-features-fig06.png)

> **[Note de la 2e éd.]** Un diagramme ConfBridge serait utile ici : montrer plusieurs endpoints SIP rejoignant une conférence nommée unique (par ex. `101`) via `ConfBridge()`, avec un participant marqué comme admin, et une note indiquant que le mixage/synchronisation est géré par `res_confbridge` + le minuteur intégré `res_timing_*` (pas de DAHDI).

Comme vous pouvez le voir ci-dessus, il y a trois arguments importants, chacun correspondant à un type de section dans `confbridge.conf`. **bridge_profile** (une section `type=bridge`) : ici vous sélectionnez le nombre maximum de participants (`max_members`), l'enregistrement (`record_conference`), `video_mode`, et de nombreux autres paramètres à l'échelle du pont.

Il n'est pas logique de reproduire l'intégralité du fichier exemple ici, alors laissez-moi vous donner un exemple simple sur la façon de configurer un bridge_profile dans le fichier confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (une section `type=user`) : ici vous définissez des options spécifiques par utilisateur, telles que si l'utilisateur est un administrateur (`admin=yes`), s'il commence en mode muet (`startmuted=yes`), la musique d'attente, et de nombreuses autres options par utilisateur. Exemple :

```
[admin_user]
type=user
admin=yes
```

**menu** (une section `type=menu`) : ici vous définissez le mappage du clavier (DTMF) pour la conférence — par exemple, quelle touche active/désactive le muet, ajuste le volume ou quitte la conférence. Consultez le fichier `confbridge.conf.sample` pour voir toutes les actions disponibles. Exemple :

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

Les options du pont de conférence peuvent être transmises dynamiquement dans le dialplan en utilisant la fonction CONFBRIDGE(). Voir les exemples ci-dessous :

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Commandes d'administration ConfBridge et migration depuis MeetMe

Si vous venez de MeetMe, les fonctions d'administration que vous utilisiez via `MeetMeAdmin()` et l'option `a` (admin) sont maintenant exprimées via le **profil utilisateur admin** (`admin=yes`) plus les actions du **menu**. Un administrateur qui rejoint avec un profil admin et un menu contenant des actions admin peut verrouiller la salle, expulser des utilisateurs et mettre les participants en sourdine en direct depuis le clavier. Les actions de menu pertinentes dans `confbridge.conf` sont :

- `admin_kick_last` -- expulser le dernier utilisateur ayant rejoint
- `admin_toggle_mute_participants` -- mettre en sourdine/réactiver tous les participants non-admin
- `toggle_mute` -- mettre en sourdine/réactiver vous-même
- `participant_count` -- annoncer le nombre de participants
- `leave_conference` -- quitter le pont et continuer dans le dialplan

Celles-ci remplacent les indicateurs d'option MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) et les commandes `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). Il n'y a pas de `meetme.conf` dans Asterisk 22 ; toute la configuration de conférence se trouve dans `confbridge.conf`, et les modifications sont appliquées avec `module reload res_confbridge.so`.

### Exemple ConfBridge

Pour créer une salle de conférence accessible à l'extension 500, dans `extensions.conf` :

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Le premier appelant à composer le 500 crée la conférence `101` ; les appelants suivants la rejoignent. Les profils et menus référencés ici (`default_bridge`, `default_user`, `sample_user_menu`) sont définis dans `confbridge.conf`. Pour exiger un code PIN, définissez `pin=` dans le profil utilisateur ; pour faire d'un participant un administrateur de conférence, donnez-lui un profil utilisateur avec `admin=yes`.

## Enregistrement d'appel

Il existe plusieurs façons d'enregistrer un appel dans Asterisk. Vous pouvez utiliser l'application `MixMonitor()` pour enregistrer facilement les appels. (L'ancienne application `Monitor`, qui enregistrait deux fichiers séparés, a été supprimée ; utilisez `MixMonitor` à la place.)

### Utilisation de l'application MixMonitor

L'application `MixMonitor` enregistre l'audio du canal actuel dans le fichier spécifié. Si le nom de fichier est un chemin absolu, il utilise ce chemin. Sinon, il crée le fichier dans le répertoire de surveillance configuré dans asterisk.conf.

![L'application MixMonitor() : enregistre et mixe l'audio d'un canal dans un fichier, avec des options pour ajouter, pont uniquement, et ajustement du volume](../images/13-pbx-features-fig09.png)

### MixMonitor()

Enregistrez un appel et mixez l'audio pendant l'enregistrement. Syntaxe : `MixMonitor(filename.extension[,options[,command]])`. Enregistre l'audio sur le canal actuel dans le fichier spécifié. Options valides :

- a - Ajoute au fichier au lieu de l'écraser.
- b - Sauvegarde l'audio dans le fichier uniquement lorsque le canal est ponté.
- Note : n'inclut pas les conférences.
- v(<x>) - Ajuste le volume audible par un facteur de <x> (allant de -4 à 4)
- V(<x>) - Ajuste le volume parlé par un facteur de <x> (allant de -4 à 4)
- W(<x>) - Ajuste les volumes audible et parlé par un facteur de <x> (allant de -4 à 4)
- <command> sera exécuté lorsque l'enregistrement sera terminé. Toutes les chaînes correspondant à ^{X} seront déséchappées en ${X} et toutes les variables seront évaluées à ce moment-là. La variable MIXMONITOR_FILENAME contiendra le nom de fichier utilisé pour l'enregistrement.

Une ressource intéressante est la fonctionnalité d'enregistrement « one-touch » `automixmon`, qui permet à une partie de composer un code DTMF (par défaut `*3`) pendant un appel pour démarrer immédiatement (et arrêter) l'enregistrement. Elle est basée sur MixMonitor, elle écrit donc un seul fichier mixé. Exemple :

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Les options `X` et `x` activent la fonctionnalité MixMonitor « one-touch » pour l'appelant et l'appelé respectivement. Parce que MixMonitor enregistre un seul fichier mixé, il n'est pas nécessaire de combiner des fichiers IN/OUT séparés par la suite (l'ancienne approche `automon`/`Monitor`, qui produisait deux fichiers pour `soxmix`, a été supprimée avec l'application `Monitor`).

Si vous ne voulez pas utiliser Set() avant l'application Dial(), vous pouvez définir cela dans la section globals :

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Musique d'attente

La musique d'attente (MOH) a changé plusieurs fois entre les versions 1.0, 1.2 et 1.4. Dans la dernière version, la MOH est par défaut « FILE-BASED ». En d'autres termes, Asterisk fournira les fichiers MOH dans des formats tels que g729, alaw, ulaw et gsm. Ainsi, il n'est pas nécessaire de transcoder la musique avant de l'envoyer vers le canal. Cela économise du temps processeur, ce qui est une modification bienvenue pour ceux qui travaillent avec des systèmes de production. Dans les anciennes versions, la MOH était généralement fournie par MP3 (elle peut toujours être configurée de cette façon). Fournir la MOH en utilisant MP3 oblige Asterisk à transcoder, dépensant une précieuse puissance CPU dans le processus. Le nouveau fichier de configuration est montré ci-dessous. Notez que la classe par défaut utilise maintenant le format de fichier natif mode=files. Tous les autres modes sont commentés. Chaque section est une classe. La seule classe non commentée à ce stade est default. Si vous souhaitez avoir des classes différentes pour des fichiers différents, vous devrez créer de nouvelles sections (classes).

![La configuration exemple musiconhold.conf, listant les modes MOH valides (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

### Tâches de configuration MOH

Maintenant, pour utiliser la musique d'attente, définissez la classe MOH dans les fichiers de configuration des canaux (chan_dahdi.conf, pjsip.conf, iax.conf, etc.). Pour les endpoints PJSIP, définissez `moh_suggest` dans la section endpoint de `pjsip.conf` (le nom d'option hérité `musicclass` s'applique à chan_dahdi et aux autres pilotes de canaux, pas à PJSIP). Les morceaux « freeplay » installés sont maintenant au format wav. Au moment de l'installation, vous pouvez sélectionner (en utilisant make menuselect) les formats de fichiers MOH disponibles. Si vous souhaitez ajouter de nouveaux fichiers MOH, vous devrez les fournir dans les formats requis. Par exemple :

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Dans le dialplan, vous pouvez démarrer la musique d'attente sur un canal avec `StartMusicOnHold` (et l'arrêter avec `StopMusicOnHold`) :

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Pour jouer de la musique d'attente pendant une durée fixe comme test rapide, utilisez l'application `MusicOnHold` avec une durée (en secondes) :

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mappages d'applications (Application Maps)

Les mappages d'applications vous permettent d'ajouter de nouvelles fonctionnalités en utilisant la section `[applicationmap]` du fichier features.conf. Supposons que vous ayez besoin d'identifier le type de client auquel vous répondez dans un centre d'appels. Vous pourriez créer un mappage d'application pour chaque type de client, qui pourrait compter le nombre de clients répondus par type.

## Quiz

1. Quelles affirmations sont vraies concernant le parcage d'appel ?
   - A. Par défaut, l'extension 800 est utilisée pour le parcage d'appel.
   - B. Lorsque vous êtes loin de votre bureau et que vous recevez un appel, vous pouvez le parquer ; le système annonce l'emplacement de parcage, et vous composez cet emplacement depuis n'importe quel téléphone pour récupérer l'appel.
   - C. Par défaut, l'extension 700 parque un appel, et les appels sont parqués dans les emplacements 701–720.
   - D. Vous composez 700 pour récupérer un appel parqué.
2. Pour utiliser la fonctionnalité de prise d'appel, toutes les extensions doivent être dans le même ___. Pour les canaux DAHDI, cela est configuré dans le fichier ___.
3. Lors du transfert d'un appel, vous pouvez choisir entre un transfert ___, où le destinataire n'est pas consulté au préalable, et un transfert ___, où vous parlez au destinataire avant de terminer le transfert.
4. Pour effectuer un transfert assisté (consultatif), vous utilisez la séquence ___; pour un transfert aveugle, vous utilisez ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Pour héberger des conférences téléphoniques dans Asterisk 22, vous utilisez l'application ___.
6. Dans ConfBridge, un participant se voit accorder des privilèges d'administrateur (expulser, mettre les autres en sourdine, verrouiller la salle) en définissant ___ dans son profil utilisateur (`confbridge.conf`) :
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Le meilleur format pour la musique d'attente est le MP3, car il utilise très peu de puissance de traitement sur le serveur Asterisk.
   - A. Vrai
   - B. Faux
8. Pour prendre un appel d'un groupe d'appel spécifique, vous devez être dans le groupe ___ correspondant.
9. Vous pouvez enregistrer un appel avec l'application MixMonitor() ou la fonctionnalité d'enregistrement « one-touch » (`automixmon`). Par défaut, `automixmon` utilise la séquence DTMF ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. Dans ConfBridge, quelle option de profil utilisateur `confbridge.conf` fait rejoindre un participant en mode muet (ils peuvent entendre la conférence mais ne peuvent pas être entendus tant qu'ils ne sont pas réactivés) ?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Réponses :** 1 — B, C · 2 — groupe de prise d'appel (pickup group) ; `chan_dahdi.conf` · 3 — aveugle ; assisté · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — prise d'appel (pickup) · 9 — C · 10 — A
