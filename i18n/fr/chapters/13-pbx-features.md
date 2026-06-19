# Utilisation des fonctionnalités PBX

Dans les systèmes SIP, la plupart des fonctionnalités téléphoniques sont implémentées au niveau de l'endpoint. Il existe une grande variété de téléphones SIP et de fabricants, et l'interopérabilité n'est pas garantie. L'équipe de développement d'Asterisk a accompli un travail remarquable en implémentant la plupart des fonctionnalités directement dans le PBX, rendant Asterisk presque indépendant de l'endpoint. Cependant, vous constaterez parfois que la même fonction est effectuée à la fois par le téléphone et par Asterisk lui-même. L'intégration du téléphone et du PBX est la prochaine frontière en matière de convivialité, et c'est là que les systèmes propriétaires concentrent leurs efforts actuellement. Dans ce chapitre, vous apprendrez à utiliser la plupart de ces fonctionnalités.

## Objectifs

À la fin de ce chapitre, vous serez capable de comprendre et d'utiliser :

- Le parcage d'appel (Call Parking)
- La capture d'appel (Call Pickup)
- Le transfert d'appel (Call Transfer)
- La conférence téléphonique (ConfBridge)
- L'enregistrement d'appel (Call Recording)
- La musique d'attente (Music on hold)

## Où les fonctionnalités sont-elles implémentées

Avant tout, il est important de comprendre quand les fonctionnalités du PBX sont exécutées et quand le téléphone effectue tout le travail. Par exemple, vous pouvez transférer un appel en utilisant le bouton TRANSFER du téléphone ou en composant # (transfert inconditionnel exécuté par le PBX lui-même).

## Fonctionnalités implémentées par Asterisk

Ces fonctionnalités sont implémentées dans le PBX par le code Asterisk :

- Musique d'attente
- Parcage d'appel
- Capture d'appel
- Enregistrement d'appel
- Salle de conférence ConfBridge
- Transfert d'appel (aveugle et assisté)

## Fonctionnalités généralement implémentées par le dialplan

Ces fonctionnalités doivent être programmées dans le dialplan d'Asterisk (extensions.conf) :

- Renvoi d'appel sur occupation
- Renvoi d'appel immédiat
- Renvoi d'appel sur non-réponse
- Filtrage d'appel (liste noire)
- Ne pas déranger
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

> **[Note de la 2e éd.]** À partir d'Asterisk 12+, le parcage d'appel a été déplacé de `features.conf`/`app_features` vers son propre module `res_parking` avec une configuration dans `res_parking.conf`. Le bloc parking-lot ci-dessous (parkext, parkpos, context, parkingtime, etc.) réside dans `res_parking.conf` et est présenté en utilisant la syntaxe de l'Asterisk 22 `res_parking.conf.sample`. La section `[featuremap]` (les codes de fonctionnalités DTMF, incluant `parkcall`) reste dans `features.conf`.

Les options de parking-lot résident dans `res_parking.conf`. Un parking-lot nommé `default` existe toujours, même s'il n'est pas présent dans le fichier de configuration. L'extrait ci-dessous est tiré de l'Asterisk 22 `res_parking.conf.sample` :

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
;automon => *1                  ; One Touch Record a.k.a. Touch Monitor -- Make sure to set the W
and/or w option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Transfert d'appel

Le transfert d'appel peut être implémenté par le téléphone, par un ATA, ou par Asterisk lui-même. Reportez-vous au manuel de votre téléphone pour comprendre comment les appels sont transférés. Si votre téléphone ne prend pas en charge le transfert d'appel, vous pouvez utiliser Asterisk pour accomplir cette tâche. Le transfert d'appel est implémenté de deux manières différentes. La première consiste à utiliser la fonctionnalité de transfert aveugle : composez # suivi du numéro vers lequel transférer. Parfois, vous utiliserez la fonctionnalité de transfert de votre téléphone IP ou de votre softphone IP. Vous pouvez modifier le caractère de transfert en éditant le paramètre blindxfer dans le fichier features.conf. Vous pouvez activer le transfert assisté dans Asterisk en supprimant le ; avant le paramètre atxfer dans le fichier features.conf. Pendant une conversation, vous appuieriez sur *2. Asterisk dira « transfer » et vous donnera une tonalité. L'appelant est envoyé vers la musique d'attente. Après avoir parlé à la personne destinataire et raccroché le téléphone, le système relie l'appelant au destinataire.

![Transfert d'appel : les étapes pour un transfert aveugle (appuyez sur # pendant l'appel) et un transfert assisté (appuyez sur *2)](../images/13-pbx-features-fig03.png)

### Liste des tâches de configuration

1. Si le téléphone est basé sur SIP, assurez-vous que l'option directmedia est égale à no ou utilisez une option t ou T dans l'application dial()

## Parcage d'appel

Cette fonctionnalité est utilisée pour parquer un appel. Cela aide, par exemple, lorsque vous répondez à un appel téléphonique en dehors de votre bureau et que vous souhaitez transférer l'appel vers votre poste. Vous pouvez y parvenir en parquant l'appel dans une extension. Une fois arrivé à votre bureau, composez simplement le numéro de l'extension de parcage pour récupérer l'appel.

![Parcage d'appel : composez 700 pour parquer un appel dans le premier emplacement libre (701–720) ; Asterisk annonce l'emplacement, que vous composez depuis n'importe quel téléphone pour récupérer l'appel](../images/13-pbx-features-fig04.png)

Par défaut, l'extension 700 est utilisée pour parquer un appel. Au milieu d'une conversation, appuyez sur # pour transférer l'appel vers l'extension 700. Asterisk annoncera alors votre extension de parcage, telle que 701 ou 702. Raccrochez le téléphone, et l'appelant sera mis en attente. Allez à votre téléphone de bureau et composez l'extension de parcage annoncée pour récupérer l'appel. Si l'appelant est parqué pendant une longue période, la fonctionnalité de timeout se déclenchera et l'extension initialement appelée sonnera à nouveau.

### Liste des tâches de configuration

Suivez les étapes ci-dessous pour activer le parcage d'appel. Étape 1 : Rendez le parking-lot accessible depuis votre dialplan (requis). Le `context` du parking-lot par défaut est `parkedcalls` (défini dans `res_parking.conf`). Incluez ce context dans le context depuis lequel vos téléphones composent, dans `extensions.conf` :

```
include => parkedcalls
```

Étape 2 : Testez la fonctionnalité de parcage d'appel en composant #700. Notes :

- L'extension de parcage ne sera pas affichée dans la commande CLI dialplan show.
- Il est nécessaire de recharger le module de parcage après avoir modifié le fichier de configuration du parcage : `module reload res_parking.so`. Pour les modifications de features.conf, `module reload features.so`.
- Pour parquer un appel, vous devez transférer vers #700. Vérifiez les options t et T dans l'application dial().

## Capture d'appel

La capture d'appel vous permet de récupérer un appel provenant d'un collègue dans le même groupe d'appel. Cela aiderait, par exemple, à éviter d'avoir à se lever pour prendre un appel qui sonne pour une autre personne dans votre pièce, mais qui n'est pas présente. En composant *8, vous pouvez capturer un appel au sein de votre groupe d'appel. Ce numéro peut être modifié dans le

```
features.conf file.
```

![Capture d'appel : les membres ne peuvent capturer que les appels au sein de leur propre groupe ; l'opérateur (pickupgroup=1,2,3) peut capturer les appels de chaque groupe](../images/13-pbx-features-fig05.png)

### Liste des tâches de configuration

Suivez les étapes ci-dessous pour configurer la fonctionnalité de capture d'appel. Étape 1 : Configurez un groupe d'appel pour vos extensions. Cela se fait dans le fichier de configuration du canal (pjsip.conf, iax.conf, chan_dahdi.conf). Pour les endpoints PJSIP, définissez `call_group` et `pickup_group` dans la section endpoint de `pjsip.conf` (pjsip.conf utilise des noms d'options en snake_case). Cette tâche est requise.

Pour PJSIP (pjsip.conf) :
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Étape 2 : Modifiez le numéro de la fonctionnalité de capture d'appel (optionnel).

```
pickupexten=*8; Configures the call pickup extension
```

## Conférence (conférence téléphonique)

Il existe différentes manières d'implémenter une conférence sur Asterisk. La première option consiste simplement à utiliser la capacité de conférence à trois du téléphone. En utilisant cette fonctionnalité dans le téléphone, vous n'avez besoin d'aucun support sur le serveur lui-même. Cependant, lorsque vous souhaitez une conférence avec plus de 3 personnes, vous devez exécuter une salle de conférence. L'application de conférence moderne d'Asterisk est ConfBridge (`app_confbridge`).

ConfBridge prend en charge les conférences vocales HD et la visioconférence. Il existe certaines limitations pour la visioconférence, comme l'absence de transcodage — tous les participants doivent utiliser le même codec et le même profil. La visioconférence utilise un mode « follow-the-talker », affichant l'image de la dernière personne à parler. Vous pouvez facilement configurer de nouveaux menus DTMF dans ConfBridge.

> **[Note de la 2e éd.]** MeetMe (`app_meetme`) a été **déprécié dans Asterisk 19** et était prévu pour être supprimé dans Asterisk 21, mais cette suppression a été suspendue (à la demande du projet ViciDial). La source du module est toujours fournie avec Asterisk 22, mais elle nécessite DAHDI et n'est **pas construite par la compilation par défaut d'Asterisk 22** — une installation standard n'a pas de `app_meetme.so` et l'application `MeetMe()` est indisponible. Tous les nouveaux déploiements de salles de conférence doivent utiliser ConfBridge. La section MeetMe ci-dessous est conservée à des fins de référence historique uniquement.

### Confbridge

Pour démarrer une salle de conférence, la syntaxe est listée ci-dessous.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Pour obtenir une description complète de la commande, vous pouvez utiliser core show application confbridge.

![Sortie de `core show application confbridge`, montrant le synopsis, la syntaxe, et les arguments bridge_profile, user_profile et menu](../images/13-pbx-features-fig06.png)

Comme vous pouvez le voir ci-dessus, il y a trois sections importantes : Bridge_profile : Vous définissez le profil dans le fichier confbridge.conf. Là, vous pouvez sélectionner le nombre maximum de participants, l'enregistrement, video_mode et de nombreux autres paramètres de pont.

Il n'est pas logique de reproduire l'intégralité du fichier exemple ici, alors permettez-moi de vous donner un exemple simple sur la façon de configurer un bridge_profile dans le fichier confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile : Ici, vous définissez des options spécifiques par utilisateur, comme si l'utilisateur est un administrateur ou non. La musique d'attente et de nombreuses autres options peuvent être définies par utilisateur. Exemple :

```
[admin_user]
type=user
admin=yes
```

Menu : Dans la section menu, vous pouvez définir votre mappage clavier pour l'application, où activer/désactiver le mode muet. Consultez le fichier confbridge.conf pour voir les options. Exemple :

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

## Meetme (Héritage — déprécié, non construit par défaut dans Asterisk 22)

> **[Note de la 2e éd.]** `app_meetme` a été déprécié dans Asterisk 19. Sa suppression prévue dans Asterisk 21 a été suspendue, donc la source est toujours fournie dans Asterisk 22, mais le module n'est pas construit par la compilation par défaut d'Asterisk 22 (il dépend de DAHDI). Une installation standard d'Asterisk 22 n'a donc pas d'application `MeetMe()`. Le contenu ci-dessous est conservé pour référence historique et pour les lecteurs mettant à niveau des systèmes plus anciens. **Pour les nouvelles installations, utilisez ConfBridge (voir ci-dessus).** La dépendance DAHDI et le module `dahdi_dummy` ne sont pas requis pour ConfBridge.

Alternativement, dans les anciennes versions d'Asterisk, vous pouviez utiliser l'application meetme(). Meetme est un pont de conférence très simple à utiliser. Rappelez-vous, meetme a été déprécié dans Asterisk 19 et dépend du module DAHDI pour la synchronisation.

![Types de conférence MeetMe — haut-parleur unique, protégé par mot de passe, et conférences dynamiques — nécessitant tous une source de synchronisation Zaptel/DAHDI](../images/13-pbx-features-fig07.png)

### L'application meetme()

En utilisant la commande CLI meetme show, vous pouvez obtenir la description ci-dessus. Pour utiliser meetme, vous devez compiler les pilotes DAHDI et avoir au moins un module noyau DAHDI chargé. Si vous n'avez pas au moins une carte DAHDI installée, chargez le module noyau dahdi_dummy pour fournir une source de synchronisation. Description :

![L'application MeetMe() : syntaxe `MeetMe([confno][,[options][,pin]])` et ses principaux indicateurs d'option](../images/13-pbx-features-fig08.png)

L'application meetme() fait entrer l'utilisateur dans une conférence meetme spécifiée. Si le numéro de conférence est omis, l'utilisateur sera invité à en saisir un. L'utilisateur peut quitter la conférence en raccrochant ou — si l'option p est spécifiée — en appuyant sur #. Veuillez noter : Les modules noyau DAHDI et au moins un pilote matériel (ou dahdi_dummy) doivent être présents pour que la conférence fonctionne correctement. De plus, le pilote de canal chan_dahdi doit être chargé pour que les options i et r fonctionnent.

> **[Note de la 2e éd.]** Les listes d'indicateurs d'option et de commandes d'administration qui suivent décrivent l'interface héritée `app_meetme` et reflètent la documentation historique `MeetMe()`/`MeetMeAdmin()`. Parce que `app_meetme` n'est pas construit par l'installation par défaut d'Asterisk 22, ces indicateurs ne peuvent pas être confirmés par rapport à un système Asterisk 22 en cours d'exécution ; ils sont reproduits pour les lecteurs maintenant des déploiements plus anciens. Sur Asterisk 22, utilisez ConfBridge et la fonction de dialplan `CONFBRIDGE()` à la place.

La chaîne d'options peut contenir zéro, un ou plusieurs des caractères suivants :

- 'a' -- définit le mode administrateur
- 'A' -- définit le mode marqué
- 'b' – exécute le script AGI spécifié dans ${MEETME_AGI_BACKGROUND}Par défaut : conf-background.agi (Note : Cela ne fonctionne pas avec des canaux non-DAHDI dans la même conférence)
- 'c' -- annonce le nombre d'utilisateur(s) lors de la jonction à une conférence
- 'd' -- ajoute dynamiquement une conférence
- 'D' -- ajoute dynamiquement une conférence, en demandant un code PIN
- 'e' -- sélectionne une conférence vide
- 'E' -- sélectionne une conférence vide sans code PIN
- 'i' -- annonce un utilisateur rejoignant/quittant avec révision
- 'I' -- annonce un utilisateur rejoignant/quittant sans révision
- 'l' -- définit le mode écoute seule (Écoute seule, pas de parole)
- 'm' -- définit initialement en mode muet
- 'M' -- active la musique d'attente lorsque la conférence n'a qu'un seul appelant
- 'o' -- définit l'optimisation du locuteur, qui traite les locuteurs qui ne parlent pas comme étant en mode muet, ce qui signifie (a) aucun encodage n'est effectué lors de la transmission et (b) l'audio reçu qui n'est pas enregistré comme parlant est omis, ne causant aucune accumulation de bruit de fond
- 'p' -- permet aux utilisateurs de quitter la conférence en appuyant sur '#'
- 'P' -- demande toujours le code PIN même s'il est spécifié
- 'q' -- mode silencieux (ne joue pas les sons d'entrée/sortie)
- 'r' -- Enregistre la conférence (enregistre sous ${MEETME_RECORDINGFILE} en utilisant le format ${MEETME_RECORDINGFORMAT}). Le nom de fichier par défaut est meetme-conf-rec-${CONFNO}-${UNIQUEID} et le format par défaut est wav.
- 's' -- Présente le menu (utilisateur ou administrateur) lorsque '*' est reçu ('send' au menu)
- 't' -- définit le mode parole seule. (Parole seule, pas d'écoute)
- 'T' -- définit la détection de locuteur (envoyé à l'interface de gestion et à la liste meetme)
- 'w[(<secs>)]' -- attend jusqu'à ce que l'utilisateur marqué entre dans la conférence
- 'x' -- ferme la conférence lorsque le dernier utilisateur marqué sort
- 'X' -- permet à l'utilisateur de quitter la conférence en entrant une extension valide à un chiffre ${MEETME_EXIT_CONTEXT} ou le context actuel si cette variable n'est pas définie.
- '1' -- ne joue pas de message lorsque la première personne entre

### Fichier de configuration Meetme

Ce fichier est utilisé pour configurer l'application meetme. Par exemple :

```
;
; Configuration file for MeetMe simple conference rooms for Asterisk of course.
;
; This configuration file is read every time you call app meetme()
[general]
;audiobuffers=32        ; The number of 20ms audio buffers to be used
                        ; when feeding audio frames from non-DAHDI channels
                        ; into the conference; larger numbers will allow
                        ; for the conference to 'de-jitter' audio that arrives
                        ; at different timing than the conference's timing
                        ; source, but can also allow for latency in hearing
                        ; the audio from the speaker. Minimum value is 2,
                        ; maximum value is 32.
;
[rooms]
;
; Usage is conf => confno[,pin][,adminpin]
;
conf=>9000
conf=>9001,123456
```

Il n'est pas nécessaire d'utiliser reload ou restart pour qu'Asterisk prenne en compte les modifications dans le fichier meetme.conf.

### Applications liées à Meetme

L'application meetme() possède deux autres applications de support.

```
MeetMeCount(confno[|var])
```

Ceci joue le nombre d'utilisateurs dans la conférence. Si une variable est spécifiée, il ne joue pas le message mais définit le nombre d'utilisateurs à celle-ci.

```
MeetMeAdmin(confno,command,[user]):
```

Exécute la commande d'administration pour une conférence :

- 'e' -- Éjecte le dernier utilisateur qui a rejoint
- 'k' -- Expulse un utilisateur de la conférence
- 'K' -- Expulse tous les utilisateurs de la conférence
- 'l' -- Déverrouille la conférence
- 'L' -- Verrouille la conférence
- 'm' -- Active le micro d'un utilisateur
- 'M' -- Coupe le micro d'un utilisateur
- 'n' -- Active le micro de tous les utilisateurs dans la conférence
- 'N' -- Coupe le micro de tous les utilisateurs non-administrateurs dans la conférence
- 'r' -- Réinitialise les paramètres de volume d'un utilisateur
- 'R' -- Réinitialise les paramètres de volume de tous les utilisateurs
- 's' -- Baisse le volume de parole de toute la conférence
- 'S' -- Augmente le volume de parole de toute la conférence
- 't' -- Baisse le volume de parole d'un utilisateur
- 'T' -- Baisse le volume de parole de tous les utilisateurs
- 'u' -- Baisse le volume d'écoute d'un utilisateur
- 'U' -- Baisse le volume d'écoute de tous les utilisateurs
- 'v' -- Baisse le volume d'écoute de toute la conférence
- 'V' -- Augmente le volume d'écoute de toute la conférence

### Liste des tâches de configuration Meetme

Suivez les étapes ci-dessous pour configurer l'application de conférence meetme. Étape 1 : Choisissez l'extension pour la salle Meetme (requis) Étape 2 : Éditez le fichier meetme.conf pour configurer les mots de passe (optionnel)

### Exemples

Exemple n°1 : Salle meetme simple 1. Dans le fichier extensions.conf, créez la salle de conférence 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. Dans le fichier meetme.conf, établissez le mot de passe pour la salle 101. Note importante : L'application meetme() a besoin d'un minuteur pour fonctionner. Si vous n'avez pas de matériel Digium installé et configuré, utilisez dahdi_dummy comme source de synchronisation.

## Enregistrement d'appel

Il existe plusieurs façons d'enregistrer un appel dans Asterisk. Vous pouvez utiliser l'application mixmonitor() pour enregistrer facilement les appels.

### Utilisation de l'application mixmonitor

L'application mixmonitor enregistre l'audio du canal actuel dans le fichier spécifié. Si le nom de fichier est un chemin absolu, il utilise ce chemin. Sinon, il crée le fichier dans le répertoire de surveillance configuré dans asterisk.conf.

![L'application MixMonitor() : enregistre et mixe l'audio d'un canal dans un fichier, avec des options pour l'ajout, le pontage uniquement, et l'ajustement du volume](../images/13-pbx-features-fig09.png)

### Mixmonitor()

Enregistrez un appel et mixez l'audio pendant l'enregistrement [Description] MixMonitor(<file>.<ext>[|<options>[|<command>]]) Enregistre l'audio sur le canal actuel dans le fichier spécifié. options : a- Ajoute au fichier au lieu de l'écraser. b-Sauvegarde uniquement l'audio dans le fichier pendant que le canal est ponté. Note : n'inclut pas les conférences. v(<x>) - Ajuste le volume entendu par un facteur de <x> V(<x>) - Ajuste le volume parlé par un facteur de <x> W(<x>) - Ajuste les volumes entendu et parlé Valid options :

- a - Ajoute au fichier au lieu de l'écraser.
- b - Sauvegarde uniquement l'audio dans le fichier pendant que le canal est ponté.
- Note : n'inclut pas les conférences.
- v(<x>) - Ajuste le volume audible par un facteur de <x> (allant de -4 à 4)
- V(<x>) - Ajuste le volume parlé par un facteur de <x> (allant de -4 à 4)
- W(<x>) - Ajuste les volumes audible et parlé par un facteur de <x> (allant de -4 à 4)
- <command> sera exécutée lorsque l'enregistrement sera terminé. Toutes les chaînes correspondant à ^{X} seront déséchappées en ${X} et toutes les variables seront évaluées à ce moment-là. La variable MIXMONITOR_FILENAME contiendra le nom de fichier utilisé pour enregistrer.

Une ressource intéressante est automon, qui vous permet de simplement composer *1 pour démarrer immédiatement l'enregistrement. Exemple :

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

Les canaux audio sont entrants (IN) et sortants (OUT) et sont séparés en deux fichiers distincts dans le répertoire /var/spool/asterisk/monitor. Les deux fichiers peuvent être mixés en utilisant l'application sox.

```
debian#soxmix *in.wav *out.wav output.wav
```

Si vous ne voulez pas utiliser Set() avant l'application Dial(), vous pouvez définir ceci dans la section globals :

```
[globals]
DYNAMIC_FEATURES=>automon
```

### Musique d'attente

La musique d'attente (MOH) a changé plusieurs fois entre les versions 1.0, 1.2 et 1.4. Dans la dernière version, la MOH est par défaut « FILE-BASED ». En d'autres termes, Asterisk fournira les fichiers MOH dans des formats tels que g729, alaw, ulaw et gsm. Ainsi, il n'est pas nécessaire de transcoder la musique avant de l'envoyer au canal. Cela économise du temps processeur, ce qui est une modification bienvenue pour ceux qui travaillent avec des systèmes de production. Dans les anciennes versions, la MOH était généralement fournie par MP3 (elle peut toujours être configurée de cette façon). Fournir la MOH en utilisant MP3 oblige Asterisk à transcoder, dépensant une précieuse puissance CPU dans le processus. Le nouveau fichier de configuration est montré ci-dessous. Notez que la classe par défaut utilise maintenant le mode de format de fichier natif mode=files. Tous les autres modes sont commentés. Chaque section est une classe. La seule classe non commentée à ce stade est default. Si vous voulez avoir différentes classes pour différents fichiers, vous devrez créer de nouvelles sections (classes).

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

Maintenant, pour utiliser la musique d'attente, définissez la classe MOH dans les fichiers de configuration des canaux (chan_dahdi.conf, pjsip.conf, iax.conf, et ainsi de suite). Pour les endpoints PJSIP, définissez `moh_suggest` dans la section endpoint de `pjsip.conf` (le nom d'option hérité `musicclass` s'applique à chan_dahdi et aux autres pilotes de canal, pas à PJSIP). Les morceaux freeplay installés sont maintenant au format wav. Au moment de l'installation, vous pouvez sélectionner (en utilisant make menuselect) les formats de fichier MOH disponibles. Si vous voulez ajouter de nouveaux fichiers MOH, vous devrez les fournir dans les formats requis. Par exemple :

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Dans le dialplan, vous pouvez entendre la MOH en utilisant l'exemple suivant :

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

Pour configurer le fichier extensions.conf pour tester la MOH :

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## Application Maps

Les Application maps vous permettent d'ajouter de nouvelles fonctionnalités en utilisant la section `[applicationmap]` du fichier features.conf. Supposons que vous ayez besoin d'identifier le type de client auquel vous répondez dans un centre d'appels. Vous pourriez créer une application map pour chaque type de client, qui pourrait compter le nombre de clients ayant répondu par type.

## Quiz

1. Quelles affirmations sont vraies concernant le parcage d'appel ?
   - A. Par défaut, l'extension 800 est utilisée pour le parcage d'appel.
   - B. Lorsque vous êtes loin de votre bureau et que vous recevez un appel, vous pouvez le parquer ; le système annonce l'emplacement de parcage, et vous composez cet emplacement depuis n'importe quel téléphone pour récupérer l'appel.
   - C. Par défaut, l'extension 700 parque un appel, et les appels sont parqués dans les emplacements 701–720.
   - D. Vous composez 700 pour récupérer un appel parqué.
2. Pour utiliser la fonctionnalité de capture d'appel, toutes les extensions doivent être dans le même ___. Pour les canaux DAHDI, cela est configuré dans le fichier ___.
3. Lors du transfert d'un appel, vous pouvez choisir entre un transfert ___, où le destinataire n'est pas consulté au préalable, et un transfert ___, où vous parlez au destinataire avant de le terminer.
4. Pour effectuer un transfert assisté (consultatif), vous utilisez la séquence ___; pour un transfert aveugle, vous utilisez ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Pour héberger des conférences téléphoniques dans Asterisk 22, vous utilisez l'application ___.
6. Dans ConfBridge, un participant se voit accorder des privilèges d'administrateur (expulser, couper le micro des autres, verrouiller la salle) en définissant ___ dans son profil utilisateur (`confbridge.conf`) :
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Le meilleur format pour la musique d'attente est le MP3, car il utilise très peu de puissance de traitement sur le serveur Asterisk.
   - A. Vrai
   - B. Faux
8. Pour capturer un appel d'un groupe d'appel spécifique, vous devez être dans le groupe ___ correspondant.
9. Vous pouvez enregistrer un appel avec l'application MixMonitor() ou la fonctionnalité one-touch (automon). Par défaut, automon utilise la séquence DTMF ___.
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. Dans ConfBridge, quelle option de profil utilisateur `confbridge.conf` fait en sorte qu'un participant rejoigne en mode muet (il peut entendre la conférence mais ne peut pas être entendu tant qu'il n'est pas réactivé) ?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Réponses :** 1 — B, C · 2 — groupe de capture ; `chan_dahdi.conf` · 3 — aveugle ; assisté · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — capture · 9 — A · 10 — A
