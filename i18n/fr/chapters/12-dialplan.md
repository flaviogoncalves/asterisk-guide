# Plan de numérotation fonctionnalités avancées

Le chapitre 3 a abordé les bases d’un plan de numérotation. Pour des raisons didactiques, nous n’avons pas expliqué toutes les fonctionnalités, mais seulement certaines des plus importantes. Ce chapitre approfondira le plan de numérotation, en décrivant des techniques avancées, de nouvelles applications et des concepts.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Simplifier vos entrées d'extension
- Traiter la sécurité du dialplan et filtrer les extensions
- Recevoir des appels en utilisant un menu IVR
- Utiliser des sous‑routines pour éviter des réécritures inutiles
- Mettre en œuvre une partie de la sécurité du dialplan avec « Include »
- Mettre en œuvre le suivi d’appel avec AsteriskDB
- Mettre en œuvre un comportement hors‑heures dans votre PBX
- Utiliser la commande switch pour transférer vers un autre PBX
- Mettre en œuvre le gestionnaire de confidentialité
- Mettre en œuvre la messagerie vocale
- Mettre en œuvre un annuaire d’entreprise

## Simplifier votre plan de numérotation

Vous pouvez simplifier votre plan de numérotation en utilisant le mot‑clé « same » pour définir une extension. Cela devrait réduire le nombre de fautes de frappe dans le plan de numérotation. Consultez l’exemple ci‑dessous :

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Sécurité du Dialplan

Une faille a été découverte dans le dialplan d’Asterisk qui permet à un utilisateur d’injecter un nouveau canal et un numéro composé dans votre dialplan. Supposons que vous ayez la ligne suivante dans votre serveur `exten=>_X.,1,Dial(PJSIP/${EXTEN})` et qu’un utilisateur malveillant compose le numéro `3000&DAHDI/1/011551123456789` dans le softphone. Le protocole SIP, par défaut, accepte tous les caractères alphanumériques, de sorte que l’extension composée déclenchera en réalité deux appels : un pour le canal PJSIP/3000 et l’autre pour le canal DAHDI/011551123456789, qui est un numéro international. Ainsi, tout utilisateur ayant accès à une extension peut réellement appeler n’importe où dans le monde. La façon la plus simple d’éviter ce comportement est de filtrer les numéros avant d’appeler l’application dial. La fonction FILTER() est très pratique pour cela. Exemple :

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

L’application filter vous permettra de filtrer tous les caractères du numéro composé sauf les chiffres de 0 à 9. Vous trouverez plus d’informations dans le fichier README‑SERIOUSLY.bestpractices.txt disponible depuis Asterisk.

## Réception des appels à l'aide d'un menu IVR.

Dans la section précédente, vous avez reçu tous les appels en utilisant le DID ou le renvoi vers l'opérateur. Maintenant vous allez apprendre comment implémenter un menu IVR ainsi que créer un service d’accueil automatique. Avant d’entrer dans les détails, examinons quelques nouvelles applications. Nous avons placé la sortie de la commande `core show application` ci‑dessous simplement pour faciliter la lecture. Vous pouvez obtenir ces descriptions vous‑même en utilisant `core show application <application_name>`.

### L'application Background() application

Cette application jouera la liste de fichiers fournie tout en attendant qu’une extension soit composée par le canal appelant. Pour continuer à attendre des chiffres après que cette application a fini de jouer les fichiers, l’application **WaitExten** doit être utilisée. L’option **langoverride** indique explicitement la langue à tenter d’utiliser pour les fichiers sonores demandés. Tout contexte spécifié sera le contexte du dialplan que cette application utilise lors du retour vers une extension composée. Si l’un des fichiers sonores demandés n’existe pas, le traitement de l’appel sera interrompu. Options:

- s - Provoque le saut de la lecture du message si le canal n'est pas dans l'état « up » (c’est‑à‑dire qu’il n’a pas encore été répondu). Si cela se produit, l’application retournera immédiatement.  
- n - Ne répond pas au canal avant de lire les fichiers.  
- m - Interrompt uniquement si le chiffre saisi correspond à une extension à un chiffre dans le contexte de destination.

### L'application Record()

Cette application enregistre depuis le canal dans un nom de fichier donné. Si le fichier existe, il sera écrasé.

![figure 1 des fonctionnalités avancées du dialplan](../images/10-dialplan-advanced-features-img01.png)

- « format » est le format du type de fichier à enregistrer (wav, gsm, etc).
- « silence » est le nombre de secondes de silence autorisées avant de retourner.
- « maxduration » est la durée maximale d’enregistrement en secondes ; s’il est absent ou égal à zéro, il n’y a pas de maximum.
- « options » peut contenir l’une des lettres suivantes :
    - `a` — ajoute à un enregistrement existant plutôt que de le remplacer
    - `n` — ne répond pas, mais enregistre quand même si la ligne n’est pas encore répondue
    - `q` — silencieux (ne pas jouer de tonalité de bip)
    - `s` — saute l’enregistrement si la ligne n’est pas encore répondue
    - `t` — utilise la touche de terminaison alternative `*` (DTMF) au lieu de la valeur par défaut `#`
    - `x` — ignore toutes les touches de terminaison (DTMF) et continue l’enregistrement jusqu’à la rupture du canal

Si le nom de fichier contient %d, ces caractères seront remplacés par un numéro incrémenté de un à chaque fois que le fichier est enregistré. Utilisez core show file formats pour voir les formats disponibles sur votre système. L'utilisateur peut appuyer sur # pour terminer l'enregistrement et passer à la priorité suivante. Si l'utilisateur raccroche pendant un enregistrement, toutes les données seront perdues et l'application se terminera.

### L'application Playback() application

Cette application lit les noms de fichiers fournis (n’incluez pas l’extension). Des options peuvent également être ajoutées après le symbole pipe. L’option 'skip' fait que la lecture du message est ignorée si le canal n’est pas dans l’état 'up' (c’est‑à‑dire, n’a pas encore été répondu).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Si `skip` est spécifié, l'application retournera immédiatement si le canal n'est pas décroché. Sinon, à moins que `noanswer` ne soit spécifié, le canal sera décroché avant que le son ne soit joué. Tous les canaux ne supportent pas la lecture de messages tant qu'ils sont encore sur le combiné. Si `j` est spécifié, l'application sautera à la priorité n+101 lorsque le fichier n'existe pas, si présent. Cette application définit la variable de canal suivante à la fin :

- PLAYBACKSTATUS — le statut de la tentative de lecture sous forme de chaîne de texte, l’un des :
    - `SUCCESS`
    - `FAILED`

### L'application Read()

Cette application lit un nombre prédéfini de chiffres sous forme de chaîne, un certain nombre de fois, depuis l'utilisateur dans la variable donnée.

- filename -- fichier à lire avant de lire les chiffres ou le ton avec l'option i
- maxdigits -- nombre maximal de chiffres acceptables. Arrête la lecture après que maxdigits aient été saisis (sans obliger l'utilisateur à appuyer sur la touche #). La valeur par défaut est 0 - aucune limite - pour attendre que l'utilisateur appuie sur la touche #. Toute valeur inférieure à 0 signifie la même chose. La valeur maximale acceptée est 255.

![figure 4 des fonctionnalités avancées du dialplan](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- les options sont `s`, `i`, `n`:
    - `s` — retourner immédiatement si la ligne n'est pas active
    - `i` — lire le fichier comme un ton d'indication depuis votre `indications.conf`
    - `n` — lire les chiffres même si la ligne n'est pas active
- attempts -- si supérieur à 1, le nombre de tentatives qui seront effectuées en cas d'absence de saisie
- timeout -- Un nombre entier de secondes à attendre pour une réponse de chiffre. Si supérieur à 0, cette valeur remplacera le délai d'attente par défaut.

L'application `read()` doit se déconnecter si la fonction échoue ou génère une erreur.

### L'application Gotoif()

Cette application fera sauter le canal appelant vers l'emplacement spécifié dans le dial plan en fonction de l'évaluation de la condition donnée. Le canal continuera à labeliftrue si la condition est vraie, ou 'labeliffalse' si la condition est fausse. Les labels sont spécifiés avec la même syntaxe que celle utilisée dans l'application Goto. Si le label choisi par la condition est omis, aucun saut n'est effectué ; l'exécution continue plutôt avec la priorité suivante dans le dial plan.

### Lab: Construction d’un menu IVR étape par étape

Créons un menu IVR avec la fonctionnalité suivante. Lorsqu’il est composé, l’IVR lit un fichier audio contenant le message « Bienvenue chez XYZ Corporation ; appuyez sur 1 pour les ventes, 2 pour le support technique, 3 pour la formation, ou attendez pour parler à un représentant. » Les chiffres dirigent l’appelant comme suit:

- `1` — transfert vers les ventes (PJSIP/4001)
- `2` — transfert vers le support technique (PJSIP/4002)
- `3` — transfert vers la formation (PJSIP/4003)
- Aucun chiffre appuyé — transfert vers l'opérateur (PJSIP/4000)

**Étape 1 – Enregistrer les invites**

Créons une extension pour enregistrer les invites. Pour enregistrer une invite, composez depuis un soft phone vers `9003<filename>` (par exemple, `9003welcome`). Lorsque vous entendez le bip, commencez l’enregistrement ; appuyez sur `#` pour arrêter. Vous entendrez un bip, et le système jouera l’invite enregistrée.

**Étape 2 – Créer la logique du menu**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### Correspondance lors de la numérotation

Ceci est un menu de configuration d'entreprise pour recevoir les appels. L'application `Background()` joue le message d'accueil puis attend les chiffres, en faisant correspondre ce que l'appelant compose aux extensions définies dans le contexte actuel.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

Lorsque vous composez cette entreprise, le message d’accueil est joué en premier. Ensuite, Asterisk attend qu’un chiffre soit composé :

| Numéro composé | Action d’Asterisk |
|---------------|-----------------|
| 1 | Appelle immédiatement `Dial(DAHDI/1)` |
| 2 | Attend le délai d’attente, puis appelle `Dial(DAHDI/2)` |
| 21 | Appelle immédiatement `Dial(DAHDI/3)` |
| 22 | Appelle immédiatement `Dial(DAHDI/4)` |
| 3 | Attend le délai d’attente, puis déconnecte |
| 31 | Appelle immédiatement `Dial(DAHDI/5)` |
| 32 | Appelle immédiatement `Dial(DAHDI/6)` |

Il est important d’éviter toute ambiguïté dans les menus. Tout le monde veut être répondu rapidement. Pour cette raison, vous ne devez pas utiliser les numéros 2, 21 ou 22.

### Laboratoire : utilisation de l’application Read()

Veuillez essayer le laboratoire avec l’application read(). Read accepte les chiffres de l’utilisateur et les insère dans la variable spécifiée ; vous pouvez ensuite utiliser l’application gotoif pour rediriger l’appel.

## Inclusion de contexte

Un contexte peut inclure le contenu d’un autre contexte. Dans l’exemple ci‑dessus, n’importe quel canal peut composer n’importe quelle extension du contexte interne, mais seul le canal 4003 peut composer des extensions internationales. Vous pouvez utiliser l’inclusion de contexte pour faciliter la création du dialplan. En utilisant l’inclusion de contexte, vous pouvez contrôler qui a accès à quelles extensions.

### Dépannage du message « number not found »

Il est très fréquent de recevoir le message « number not found ». La plupart des gens confondent le concept de contextes inclus car il n’est vraiment pas intuitif. En règle générale, commencez par le fichier de configuration du canal entrant, tel que `pjsip.conf`, `chan_dahdi.conf` et `iax.conf`, et déterminez le contexte actuel. Puis, allez au dialplan dans le fichier extensions.conf et vérifiez si le numéro composé se trouve dans ce contexte. Sinon, quelque chose ne va pas dans votre dialplan. Les règles d’or des contextes sont : 1. Un canal ne peut composer que des numéros dans le même contexte que le canal. 2. Le contexte où l’appel est traité est défini dans le fichier de configuration du canal entrant (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Utilisation de l'instruction switch

Vous pouvez envoyer le traitement du dialplan vers un autre serveur en utilisant la commande switch. Vous aurez besoin du nom et de la clé de l'autre serveur. Le contexte est le contexte de destination.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Ordre de traitement du dialplan

Lorsque Asterisk reçoit un appel entrant, il consulte le contexte défini par le canal. Dans certains cas, si plusieurs motifs correspondent au numéro composé, Asterisk ne peut pas traiter l’appel exactement comme vous l’attendez. Vous pouvez voir l’ordre de correspondance en utilisant la commande CLI `dialplan show`. Exemple : supposons que vous vouliez composer le 912 pour le router vers un trunk analogique (DAHDI/1) et tous les autres numéros commençant par 9 vers un autre trunk analogique (DAHDI/2). Vous écririez quelque chose comme :

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Si deux motifs correspondent à une extension, vous pouvez contrôler quelle extension est traitée en premier en utilisant les contextes inclus. Un contexte inclus est traité après un motif dans le même contexte.

## L'instruction #INCLUDE

Doit‑on utiliser un gros fichier ou plusieurs fichiers ? Vous pouvez utiliser l’instruction #include <filename> pour inclure d’autres fichiers dans votre extensions.conf. Par exemple, nous pourrions créer un users.conf pour les utilisateurs locaux et un services.conf pour les services spéciaux. Faites attention à ne pas confondre #include <filename> avec le

```
include=>context statement.
```

## Sous‑routines avec GOSUB

Dans les versions antérieures d’Asterisk, vous aviez la commande Macro. Cette commande a été dépréciée il y a longtemps au profit de GOSUB. Nous allons démontrer ici comment créer des sous‑routines pour le traitement de la messagerie vocale de façon simple et ordonnée. Format de la commande :

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

La commande GOSUB est disponible depuis Asterisk 1.6 et prend en charge le passage d’arguments (disponibles dans la sous‑routine sous la forme `${ARG1}`, `${ARG2}`, etc.). Avec les arguments, il est désormais possible de remplacer complètement les anciennes commandes Macro. Les macros (`app_macro`) ont été supprimées dans Asterisk 21 ; vous devez utiliser GOSUB pour les sous‑routines.

### Création de la sous‑routine

La définition est très similaire. Regardez la sous‑routine ci‑dessous définie pour la messagerie vocale avec le nom stdexten (choisissez le nom qui vous convient). Après avoir appelé la commande Dial avec le premier argument (nom du canal), nous vérifions le ${DIALSTATUS} pour diriger la logique d’appel vers l’étape suivante.

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### Appel d’une sous‑routine

Faites attention, lors de l’appel de la sous‑routine, à utiliser des parenthèses avant les paramètres.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Utilisation de la base de données Asterisk

Pour mettre en œuvre le renvoi d’appel et les listes noires, nous avons besoin d’un moyen de stocker et de restaurer les données. Heureusement, Asterisk fournit un mécanisme de stockage et de récupération des données à partir d’une base de données intégrée appelée AstDB. Dans les versions modernes d’Asterisk (y compris Asterisk 22), AstDB repose sur **SQLite3** (le fichier `/var/lib/asterisk/astdb.sqlite3`) ; Asterisk 1.8 et les versions antérieures utilisaient Berkeley DB v1. Cela ressemble à la base de registre Windows utilisant le concept hiérarchique de familles et de clés. Les données persistent entre les redémarrages d’Asterisk. L’API famille/clé n’a pas changé par rapport à l’ancien moteur ; seul le format de stockage sur disque a été modifié.

### Fonctions, applications et commandes CLI

Il existe certaines fonctions, applications et commandes CLI qui travaillent avec AstDB :

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Exemples :

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

Certaines applications peuvent être utilisées pour manipuler AstDB :

- DB_DELETE(<family/key>) — fonction qui renvoie et supprime une clé unique
- DBdeltree(<family>) — application qui supprime une famille/arborescence entière

L’ancienne application `DBdel()` n’existe plus dans Asterisk 22. Supprimez une clé unique avec la fonction de dialplan `DB_DELETE()` — par ex. `Set(x=${DB_DELETE(family/key)})` ou, comme opération d’écriture, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (suppression d’une famille/arborescence entière) reste une application.

Il est également possible d’utiliser des commandes CLI pour définir et supprimer des clés :

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Mise en œuvre du renvoi d’appel, DND et des listes noires

Dans cet exemple, vous apprendrez à mettre en œuvre le renvoi d’appel immédiat et le renvoi d’appel en cas d’occupation. Nous utiliserons *21* pour programmer le renvoi d’appel immédiat et *61* pour programmer le renvoi d’appel en cas d’occupation. Pour annuler la programmation, utilisez respectivement #21# et #61#. Utilisez l’exemple ci‑dessus pour remplir la base de données. Familles utilisées :

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Essayez de remplir la base de données en composant :

- *21* (extension de destination pour le renvoi d’appel immédiat)
- *61* (extension de destination pour le renvoi d’appel en cas d’occupation)
- *41* (extension à mettre en mode ne pas déranger)

Utilisez la commande CLI `database show` pour voir les familles, clés et valeurs ajoutées.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Renvoi d’appel, liste noire, DND

La sous‑routine vérifie si la base de données contient les paires clé :valeur correspondant à CFIM, CFBS ou DND, puis les gère de manière appropriée. La sous‑routine suivante appelle la routine de numérotation :

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Utilisation d’une liste noire

L’ancienne application `LookupBlacklist()` a **été supprimée** d’Asterisk (elle a disparu avec le mécanisme hérité « priority+101 jump »). Dans Asterisk 22, vous créez une liste noire directement avec la fonction `DB_EXISTS()` (qui teste à la fois la présence d’une clé et, lorsqu’elle est trouvée, expose sa valeur dans `${DB_RESULT}`) plus `GotoIf`. Stockez chaque numéro bloqué comme clé dans une famille `blacklist`, puis vérifiez l’identifiant de l’appelant en haut de votre contexte entrant :

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})` renvoie `1` lorsque le numéro de l’appelant est présent dans la base de données (en envoyant l’appel vers le contexte `blocked`) et `0` sinon, de sorte que l’appel continue vers le `Dial()` normal.

Pour insérer un numéro dans la liste noire, vous pouvez utiliser la même ressource qu’auparavant, en composant *31* suivi des extensions à mettre sur liste noire. Pour retirer un numéro de la liste noire, vous devez composer #31# suivi du numéro à supprimer.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Vous pouvez également insérer les numéros dans la liste noire en utilisant la CLI de la console :

```
*CLI>database put blacklist <name/number> 1
```

Remarque : toute valeur peut être associée à la clé. Le test `DB_EXISTS()` recherche la clé, pas la valeur. Pour effacer le numéro de la liste noire, vous pouvez utiliser :

```
*CLI>database del blacklist <name/number>
```

## Contextes basés sur le temps

Dans la figure suivante, nous avons un dialplan avec trois contextes. Le contexte [incoming] est celui où les appels sont généralement reçus. Nous avons inclus quatre lignes qui modifient le comportement en fonction de l'heure du système, comme illustré ci‑dessous :

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modern Asterisk (including 22) separates the time-include fields with **commas**, not pipes. The legacy pipe form (`include => context|times|weekdays|mdays|months`) is parsed as a plain literal context name and silently fails to apply any time condition.

During regular working hours, processing will be redirected to the mainmenu, where it will probably call an IVR to handle the incoming call. If the call takes place after hours, it will call the security extension defined in the ${SECURITY} variable. If the security extension does not answer the call, it will be sent to the operator’s voicemail.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Messages basés sur le temps avec gotoiftime()

La syntaxe de GotoIfTime() est montrée ci‑dessous.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

Dans Asterisk 22 le séparateur de champs est une **virgule**, pas un pipe (la forme avec pipe était dépréciée dans Asterisk 1.6). Un champ `timezone` optionnel est pris en charge, et chaque libellé de branche utilise la forme habituelle `[[context,]extension,]priority`.

Cette application peut remplacer le contexte basé sur le temps et semble plus facile à comprendre et à lire. Vous pouvez spécifier le temps comme suit :

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Les noms des jours et des mois ne sont pas sensibles à la casse.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

L’instruction précédente transfère le traitement vers l’extension s dans le contexte normalhours si l’appel a lieu entre 08:00 AM et 06:00 PM du lundi au vendredi.

## Utiliser DISA pour obtenir une nouvelle tonalité de numérotation

DISA, ou « direct inward system access », est un système qui permet aux utilisateurs de recevoir une seconde tonalité de numérotation. Il leur permet de composer à nouveau vers une autre destination. Il est souvent utilisé par les techniciens lorsqu’ils composent des appels longue distance pour le support technique le week‑end ; au lieu de composer depuis leur domicile directement vers la destination, ils appellent le numéro DISA du bureau, reçoivent une tonalité de numérotation, puis appellent la destination. Les frais de longue distance sont facturés à l’entreprise plutôt qu’au téléphone domestique.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Exemple :

```
exten => s,1,DISA(no-password,default)
```

En utilisant l’instruction précédente, l’utilisateur compose le PBX et—sans nécessiter de mot de passe—reçoit une tonalité de numérotation. Tout appel utilisant DISA sera traité avec le contexte `default`. Les arguments pour cette application incluent un mot de passe global ou un mot de passe individuel dans un fichier. Si aucun contexte n’est spécifié, le contexte `disa` est supposé. Si vous utilisez un fichier de mots de passe, le chemin complet doit être indiqué. Un identifiant d’appelant peut également être spécifié pour la numérotation externe DISA. Exemple :

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 utilise des virgules comme séparateurs d’arguments (la forme avec le pipe a été dépréciée dans la version 1.6). Le premier argument est soit un code d’accès unique, soit le chemin vers un fichier de codes d’accès, et le contexte par défaut lorsqu’aucun n’est fourni est `disa`.

## Limit simultaneous calls

The GROUP() function allows you to count how many active channels you have in one group at the same time. Example: You have a branch in Rio de Janeiro, where phones follow the pattern “_214X”. This location is served by a leased line, with 64K reserved for voice bandwidth. In this case, the maximum number of allowed calls is 2 (G.729, about 31.2K per call). To limit calls to Rio by two:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

La messagerie vocale est un système de réponse téléphonique informatisé qui enregistre les messages vocaux entrants, les sauvegarde sur disque ou les envoie par e‑mail. Parfois, elle possède un annuaire permettant de rechercher les boîtes vocales par nom. Par le passé, les systèmes de messagerie vocale étaient très coûteux. Aujourd’hui, avec la téléphonie IP, la messagerie vocale devient une fonction standard.

Pour configurer la messagerie vocale, vous devez suivre les étapes suivantes.

**Étape 1 : Modifiez `voicemail.conf` et définissez les paramètres généraux.**

- `format` — codec utilisé pour enregistrer le message (par ex., wav49, wav, gsm)
- `serveremail` — qui doit apparaître comme expéditeur de la notification e‑mail
- `maxmsg` — nombre maximal de messages dans la boîte aux lettres ; au‑delà de ce seuil, les messages sont supprimés
- `maxsecs` — durée maximale d’un message vocal, en secondes
- `minsecs` — durée minimale d’un message, en secondes ; en dessous de ce seuil, aucun message n’est enregistré
- `maxsilence` — nombre de secondes de silence à considérer comme la fin du message

**Étape 2 : Modifiez `voicemail.conf` et créez les boîtes aux lettres des utilisateurs.**

### Voicemail.conf

Une boîte aux lettres est définie par une ligne par boîte, sous la forme :

```
mailboxID => pincode,fullname,email,pager-email,options
```

Les champs sont :

- **MailboxID** — généralement le numéro d’extension
- **Pincode** — mot de passe pour accéder au système de messagerie vocale
- **Full name** — utilisé par l’application d’annuaire
- **E-mail** — adresse pour la notification de messagerie vocale
- **Pager e-mail** — adresse pour la notification via une passerelle SMS ou un pager
- **Options** — options spécifiques à la boîte aux lettres (les mêmes options que dans `[general]`, mais appliquées à cette boîte)

La messagerie vocale possède plusieurs options qui contrôlent son comportement. Pour l’instant, nous nous en tiendrons aux options par défaut et nous concentrerons sur la définition de la boîte aux lettres. Après la section `[general]` du fichier, vous commencez à configurer les identifiants de boîtes aux lettres, chacun dans son propre contexte. Exemple :

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Veuillez consulter les options avancées dans le fichier `voicemail.conf`.

**Étape 3 : Configurez le fichier `extensions.conf`.**

La sous‑routine `stdexten` présentée précédemment (dans *Subroutines with GOSUB*) est exactement le gestionnaire appel/messagerie vocale dont vous avez besoin ici : elle compose l’extension et utilise la valeur de la variable de canal `${DIALSTATUS}` pour rediriger le flux d’appel vers la salutation vocale appropriée (`b` pour occupé, `u` pour indisponible). Appelez‑la avec `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` depuis chaque extension dans `extensions.conf`.

## Utilisation de l'application VoiceMailMain()

L'application voicemailmain() est utilisée pour configurer la boîte vocale. Les utilisateurs peuvent appeler l'application, enregistrer leur message d'accueil et écouter leur messagerie vocale. Pour appeler l'application dans le dialplan, utilisez :

```
exten=>9000,1,VoiceMailMain()
```

Vous trouverez ci‑dessous une liste des options disponibles pour l'application.

### Syntaxe de l'application Voicemail

Cette application permet à l'appelant de laisser un message pour une liste spécifiée de boîtes aux lettres. Lorsque plusieurs boîtes aux lettres sont indiquées, le message d'accueil sera pris dans la première boîte spécifiée. L'exécution du dialplan s'arrêtera si la boîte aux lettres spécifiée n'existe pas. La syntaxe est présentée ci‑dessous :

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

Dans tous les cas, le fichier beep.gsm sera joué avant le début de l'enregistrement. Les messages vocaux seront stockés dans le répertoire inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Si un appelant appuie sur 0 (zéro) pendant l'annonce, il sera redirigé vers l'extension « o » (out) dans le contexte actuel de la messagerie vocale. Cela peut être utilisé pour sortir vers l'opérateur. Si, pendant l'enregistrement, l'appelant appuie sur # ou que le délai de silence expire, l'enregistrement s'arrête et l'appel passe à la priorité suivante. Assurez‑vous de gérer l'appel après la lecture du message vocal, comme indiqué ci‑dessous.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Marquer les messages vocaux comme urgents

Vous pouvez marquer certains messages comme « urgent ». Deux méthodes sont disponibles :

- Passer l'option ‘U’ dans l'application voicemail()
- Spécifier review=yes dans le fichier voicemail.conf. En utilisant cette option, l'utilisateur pourra marquer le message comme urgent après avoir enregistré les instructions vocales.

## Sending voicemail to e-mail

Dans certains cas (comme le mien), nous n’utilisons tout simplement pas l’application voicemailmain() pour lire les e‑mails. Il est plus simple et plus pratique d’envoyer tous les messages par e‑mail avec l’audio en pièce jointe. En utilisant les paramètres « attach » et « delete », vous pouvez envoyer tous les courriels et les supprimer de la boîte vocale.

```
attach=yes
delete=yes
```

Pour envoyer la messagerie vocale par e‑mail, l’application voicemail utilise le agent de transfert de messages (MTA), un composant de votre système d’exploitation. Debian utilise Exim comme MTA. L’application qui envoie le courriel est définie dans le paramètre « mailcmd ».

```
mailcmd =/usr/sbin/sendmail -t
```

Dans la distribution Debian de Linux, le MTA est Exim. Pour configurer Exim sous Debian, utilisez :

```
dpkg-reconfigure exim4-config
```

Vous pouvez choisir de faire envoyer votre MTA un e‑mail directement via SMTP ou via un smarthost (généralement le serveur de messagerie de votre entreprise). Vérifiez avec votre administrateur de messagerie la meilleure façon d’envoyer des e‑mails depuis le serveur Asterisk vers votre serveur de messagerie.

## Personnalisation du message e‑mail

Vous pouvez contrôler la façon dont les messages sont envoyés en configurant les variables suivantes : Variables pour le sujet du e‑mail et le corps du e‑mail :

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Le corps et le sujet du e‑mail sont construits à partir d’un modèle que vous définissez dans la section `[general]` de `voicemail.conf`. Vous pouvez modifier à la fois le corps et le sujet, mais la taille maximale du message est de 512 octets. Dans le modèle, `\n` insère un saut de ligne et `\t` insère une tabulation.

L’exemple `emailsubject` ci‑dessous est simple. L’exemple `emailbody` est très proche du défaut ; le défaut affiche uniquement le CIDNAME lorsqu’il n’est pas nul, sinon le CIDNUM, ou « un appelant inconnu » lorsque les deux sont nuls.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interface Web de la messagerie vocale

Il existe un script Perl dans la distribution source appelé `vmail.cgi`, situé à `contrib/scripts/vmail.cgi` dans l'arborescence source d'Asterisk (il est toujours fourni avec Asterisk 22). La commande `make install` n'installe pas cette interface ; vous devez exécuter `make webvmail` depuis le répertoire source. Ce script nécessite l'interpréteur de commandes Perl et un serveur web (tel qu'Apache) installés sur le serveur.

```
make webvmail
```

La cible `make webvmail` installe le script (setuid root) dans le répertoire CGI de votre serveur web (`HTTP_CGIDIR`) et copie les images de support de `images/*.gif` vers `HTTP_DOCSDIR/_asterisk` (par défaut `/var/www/html/_asterisk`). Si ces chemins ne correspondent pas à la disposition de votre serveur web, modifiez les variables `HTTP_CGIDIR` et `HTTP_DOCSDIR` dans le fichier `Makefile` de niveau supérieur avant d'exécuter la cible.

## Notification de messagerie vocale

Vous pouvez configurer la messagerie vocale pour envoyer un message de notification à votre téléphone lorsque vous avez un nouveau message vocal. Dans Asterisk 22, l’indication de message en attente (MWI) fonctionne avec les téléphones PJSIP et SIP ainsi qu’avec les téléphones DAHDI. Pour indiquer un message vocal non écouté, un voyant peut clignoter ou le téléphone peut émettre un ton de rappel. Vous devez configurer la boîte aux lettres dans le fichier de configuration du canal correspondant. Exemple : `pjsip.conf` (dans la section endpoint) :

```
mailboxes=8590
```

Dans PJSIP, l’indice de boîte aux lettres est défini avec l’option `mailboxes` à l’intérieur de la section endpoint de `pjsip.conf`, plutôt que l’ancien `mailbox=` de `sip.conf`. Les abonnements MWI sont gérés par le module `res_pjsip_mwi`.

![L’interface web The Comedian Mail (`vmail.cgi`) : la connexion Web‑Voicemail d’Asterisk — saisissez votre boîte aux lettres et votre mot de passe pour lire, enregistrer, transférer ou supprimer les messages vocaux depuis un navigateur. Elle est toujours fournie avec Asterisk 22 et s’installe avec `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratoire : Notification de message sur le téléphone

Ce laboratoire a été testé avec un softphone SIP.

1. Modifiez `pjsip.conf` et ajoutez `mailboxes=4401` dans la section endpoint pour le dispositif nommé 4401.
2. Modifiez le `extensions.conf` et créez une extension pour enregistrer une messagerie vocale vers les extensions 4401.

```
exten=9008,1,voicemail(4401,b)
```

3. Accédez à la console et rechargez.
4. Dans le SipPulse Softphone, ouvrez les paramètres du compte SIP et activez la vérification de la messagerie vocale (message‑waiting) pour le compte.
5. Composez le 9008 et laissez un message.
6. Observez l’icône de message sur le téléphone.

## Utilisation de l'application directory

Cette application vous permet de trouver rapidement un utilisateur à appeler. La liste des noms et des extensions correspondantes est récupérée à partir du fichier de configuration de la messagerie vocale voicemail.conf. La syntaxe de l'application peut être affichée avec :

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### Laboratoire : Utilisation de l'application directory

1. Modifiez le fichier voicemail.conf pour ajouter deux extensions dans le plan de numérotation

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Créez ces extensions dans votre plan de numérotation

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Accédez à la console et rechargez  
4. Composez 9006 et enregistrez un nom pour chaque extension (4400, 4401)  
5. Composez 9007 et sélectionnez les trois lettres du nom de famille pour une extension (Eas=327). Si c’est l’option correcte, appuyez sur « 1 » pour transférer vers le nom.

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## Résumé

Dans ce chapitre, vous avez appris comment recevoir des appels en utilisant un IVR ou un standard automatique. Vous avez étudié le concept d’inclusion de contexte et implémenté quelques exemples. Des sous‑routines ont été utilisées pour éviter la saisie répétitive, et la base de données Asterisk (AstDB, soutenue par SQLite3 dans Asterisk 22) a été utilisée pour les fonctions nécessitant un stockage de données (par exemple, renvoi d’appel, ne pas déranger, listes noires). Enfin, vous avez appris comment implémenter un comportement hors‑heures et mis en place un plan de numérotation complet en utilisant ces concepts.

## Quiz

1. Un contexte dépendant du temps utilise la forme `include => context,<times>,<weekdays>,<mdays>,<months>`. Que fait `include => normalhours,08:00-18:00,mon-fri,*,*` ?
   - A. Exécuter les extensions du lundi au vendredi, de 08 h00 à 18 h00
   - B. Exécuter les options chaque jour de tous les mois
   - C. Rien ; le format est invalide
2. Dans les versions modernes d’Asterisk (y compris Asterisk 22), les champs d’un `include =>` basé sur le temps et de `GotoIfTime()` sont séparés par quel caractère ?
   - A. Le pipe `|`
   - B. La virgule `,`
   - C. Le point‑virgule `;`
   - D. Le slash `/`
3. Pour appeler plusieurs canaux à la fois (les faire sonner simultanément), vous les séparez dans `Dial()` avec le caractère ___.
4. Un menu vocal qui lit une invite en attendant que l’appelant compose une extension est généralement créé avec l’application ___.
5. Vous pouvez inclure le contenu d’un autre fichier dans `extensions.conf` en utilisant l’instruction ___ (note : c’est différent de l’instruction de contexte `include =>`).
6. Dans Asterisk 22, la base de données intégrée AstDB repose sur :
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Lorsque vous utilisez `Dial(type1/identifier1&type2/identifier2)`, Asterisk compose chaque canal séquentiellement, en attendant 20 secondes entre eux.
   - A. Faux
   - B. Vrai
8. Avec l’application Background(), vous devez attendre que le message se termine avant de pouvoir appuyer sur une touche DTMF pour choisir une option.
   - A. Faux
   - B. Vrai
9. Étant donné la syntaxe `Goto([[context,]extension,]priority)`, lesquelles des invocations suivantes de l’application Goto() sont valides ? (cochez toutes les réponses applicables)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Pour supprimer une clé unique d’AstDB dans le plan de numérotation Asterisk 22, vous utilisez :
    - A. L’application `DBdel()`
    - B. La fonction `DB_DELETE()`
    - C. L’application `DBdeltree()`
    - D. L’application `LookupBlacklist()`

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
