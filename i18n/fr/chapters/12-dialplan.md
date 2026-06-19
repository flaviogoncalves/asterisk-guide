# Fonctionnalités avancées du dialplan

Le chapitre 3 a abordé les bases du dialplan. Pour des raisons didactiques, nous n'avons pas expliqué toutes les fonctionnalités, mais seulement certaines des plus importantes. Ce chapitre approfondira le dialplan en décrivant des techniques avancées, de nouvelles applications et des concepts.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Simplifier vos entrées d'extension
- Gérer la sécurité du dialplan et filtrer les extensions
- Recevoir des appels via un menu IVR
- Utiliser des sous-routines pour éviter les réécritures inutiles
- Implémenter une sécurité du dialplan en utilisant « Include »
- Implémenter le suivi d'appel (follow-me) en utilisant AsteriskDB
- Implémenter un comportement après les heures d'ouverture dans votre PBX
- Utiliser la commande switch pour transférer vers un autre PBX
- Implémenter le gestionnaire de confidentialité (privacy manager)
- Implémenter la messagerie vocale (voicemail)
- Implémenter un annuaire d'entreprise

## Simplifier votre dialplan

Vous pouvez simplifier votre dialplan en utilisant le mot-clé « same » pour définir une extension. Cela devrait réduire le nombre de fautes de frappe dans le dialplan. Consultez l'exemple ci-dessous :

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Sécurité du dialplan

Une faille a été découverte dans le dialplan Asterisk qui permet à un utilisateur d'injecter un nouveau canal et de composer un numéro dans votre dialplan. Supposons que vous ayez la ligne suivante dans votre serveur `exten=>_X.,1,Dial(PJSIP/${EXTEN})` et qu'un utilisateur malveillant compose le numéro `3000&DAHDI/1/011551123456789` sur son softphone. Le protocole SIP, par défaut, accepte tous les caractères alphanumériques, donc l'extension composée déclenchera en réalité deux appels : un pour le canal PJSIP/3000 et l'autre pour le canal DAHDI/011551123456789, qui est un numéro international. Ainsi, tout utilisateur ayant accès à une extension peut en réalité appeler n'importe où dans le monde. Le moyen le plus simple d'éviter ce comportement est de filtrer les numéros avant d'appeler l'application de numérotation. La fonction FILTER() est très pratique pour cela. Exemple :

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

L'application filter vous permettra de filtrer tous les caractères du numéro composé à l'exception des chiffres de 0 à 9. Plus d'informations peuvent être trouvées dans le fichier README-SERIOUSLY.bestpractices.txt disponible auprès d'Asterisk.

## Recevoir des appels via un menu IVR

Dans la dernière section, vous avez reçu tous les appels en utilisant le DID ou en transférant vers l'opérateur. Maintenant, vous apprendrez à implémenter un menu IVR ainsi qu'à créer un service d'accueil automatique. Avant d'entrer dans les détails, examinons quelques nouvelles applications. Nous avons mis la sortie de la commande show application ci-dessous simplement pour faciliter la lecture. Vous pouvez obtenir ces descriptions en utilisant show application nom_de_l_application. 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### L'application Background()

Cette application jouera la liste de fichiers donnée tout en attendant qu'une extension soit composée par le canal appelant. Pour continuer à attendre des chiffres après que cette application a fini de jouer les fichiers, l'application WaitExten doit être utilisée. L'option langoverride spécifie explicitement quelle langue tenter d'utiliser pour les fichiers sonores demandés. Tout contexte spécifié sera le contexte du dialplan que cette application utilise lors de la sortie vers une extension composée. Si l'un des fichiers sonores demandés n'existe pas, le traitement de l'appel sera terminé. Options :

- s - Provoque le saut de la lecture du message si le canal n'est pas dans l'état 'up' (c'est-à-dire qu'il n'a pas encore été répondu). Si cela se produit, l'application reviendra immédiatement.
- n - Ne pas répondre au canal avant de jouer les fichiers.
- m - Ne s'interrompre que si un chiffre correspond à une extension à un chiffre dans le contexte de destination.

### L'application Record()

Cette application enregistre depuis le canal dans un nom de fichier donné. Si le fichier existe, il sera écrasé.

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' est le format du type de fichier à enregistrer (wav, gsm, etc).
- 'silence' est le nombre de secondes de silence autorisées avant de revenir.
- 'maxduration' est la durée maximale d'enregistrement en secondes ; si elle est manquante ou égale à zéro, il n'y a pas de maximum.
- 'options' peut contenir l'une des lettres suivantes :
    - `a` — ajoute à un enregistrement existant plutôt que de le remplacer
    - `n` — ne pas répondre, mais enregistrer quand même si la ligne n'a pas encore été répondue
    - `q` — silencieux (ne pas jouer de tonalité de bip)
    - `s` — saute l'enregistrement si la ligne n'a pas encore été répondue
    - `t` — utilise la touche de terminaison alternative `*` (DTMF) au lieu de la valeur par défaut `#`
    - `x` — ignore toutes les touches de terminaison (DTMF) et continue l'enregistrement jusqu'au raccrochage

Si le nom de fichier contient %d, ces caractères seront remplacés par un nombre incrémenté de un à chaque fois que le fichier est enregistré. Utilisez core show file formats pour voir les formats disponibles sur votre système. L'utilisateur peut appuyer sur # pour terminer l'enregistrement et passer à la priorité suivante. Si l'utilisateur raccroche pendant un enregistrement, toutes les données seront perdues et l'application se terminera.

### L'application Playback()

Cette application joue les noms de fichiers donnés (n'incluez pas l'extension). Des options peuvent également être incluses après un symbole pipe. L'option 'skip' provoque le saut de la lecture du message si le canal n'est pas dans l'état 'up' (c'est-à-dire qu'il n'a pas encore été répondu).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Si 'skip' est spécifié, l'application reviendra immédiatement si le canal n'est pas décroché. Sinon, à moins que 'noanswer' ne soit spécifié, le canal recevra une réponse avant que le son ne soit joué. Tous les canaux ne prennent pas en charge la lecture de messages alors qu'ils sont encore décrochés. Si 'j' est spécifié, l'application sautera à la priorité n+101 lorsque le fichier n'existe pas, s'il est présent. Cette application définit la variable de canal suivante une fois terminée :

- PLAYBACKSTATUS — le statut de la tentative de lecture sous forme de chaîne de texte, l'un des suivants :
    - `SUCCESS`
    - `FAILED`

### L'application Read()

Cette application lit un nombre prédéterminé de chiffres, un certain nombre de fois, depuis l'utilisateur dans la variable donnée.

- filename -- fichier à jouer avant de lire les chiffres ou la tonalité avec l'option i
- maxdigits -- nombre maximal de chiffres acceptables. Arrête la lecture après que maxdigits ont été saisis (sans nécessiter que l'utilisateur appuie sur la touche #). Par défaut à 0 - aucune limite - pour attendre que l'utilisateur appuie sur la touche #. Toute valeur inférieure à 0 signifie la même chose. La valeur maximale acceptée est 255.

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- les options sont `s`, `i`, `n` :
    - `s` — revenir immédiatement si la ligne n'est pas active
    - `i` — jouer filename comme une tonalité d'indication depuis votre `indications.conf`
    - `n` — lire les chiffres même si la ligne n'est pas active
- attempts -- si supérieur à 1, le nombre de tentatives qui seront effectuées au cas où aucune donnée ne serait saisie
- timeout -- Un nombre entier de secondes à attendre pour une réponse par chiffre. Si supérieur à 0, cette valeur remplacera le délai d'attente par défaut.

L'application read() doit se déconnecter si la fonction échoue ou génère une erreur.

### L'application Gotoif()

Cette application provoquera le saut du canal appelant vers l'emplacement spécifié dans le dialplan en fonction de l'évaluation de la condition donnée. Le canal continuera à labeliftrue si la condition est vraie, ou 'labeliffalse' si la condition est fausse. Les étiquettes sont spécifiées avec la même syntaxe que celle utilisée dans l'application Goto. Si l'étiquette choisie par la condition est omise, aucun saut n'est effectué ; l'exécution continue plutôt avec la priorité suivante dans le dialplan.

### Lab : Construire un menu IVR étape par étape

Créons un menu IVR avec la fonctionnalité suivante. Lorsqu'il est composé, l'IVR joue un fichier audio avec le message « Bienvenue à la société XYZ ; appuyez sur 1 pour les ventes, 2 pour le support technique, 3 pour la formation, ou attendez pour parler à un représentant. » Les chiffres dirigent l'appelant comme suit :

- `1` — transfert vers les ventes (PJSIP/4001)
- `2` — transfert vers le support technique (PJSIP/4002)
- `3` — transfert vers la formation (PJSIP/4003)
- Aucun chiffre pressé — transfert vers l'opérateur (PJSIP/4000)

**Étape 1 – Enregistrer les invites**

Créons une extension pour enregistrer les invites. Pour enregistrer une invite, composez depuis un softphone le `9003<filename>` (par exemple, `9003welcome`). Lorsque vous entendez le bip, commencez l'enregistrement ; appuyez sur `#` pour arrêter. Vous entendrez un bip et le système jouera l'invite enregistrée.

**Étape 2 – Créer la logique du menu**

Lors de la composition de l'extension 9004, le traitement saute au menu dans l'extension `s`, priorité 1.

### Correspondance pendant la numérotation

Il s'agit d'un menu de configuration d'entreprise pour recevoir des appels. L'application background lit le contexte actuel et définit la longueur maximale pour chaque numéro pour toute combinaison possible.

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

Lorsque vous appelez cette entreprise, le message de bienvenue est joué en premier. Après cela, Asterisk attend qu'un chiffre soit composé. Numéro composé Action d'Asterisk Appelle immédiatement Dial(DAHDI/1) Attend le délai d'attente, puis passe à Dial(DAHDI/2) Appelle immédiatement (DAHDI/3) Appelle immédiatement (DAHDI/4) Attend le délai d'attente, puis se déconnecte Appelle immédiatement Dial(DAHDI/5) Appelle immédiatement Dial(DAHDI/6) Se déconnecte immédiatement Il est important d'éviter toute ambiguïté dans les menus. Tout le monde veut obtenir une réponse rapidement. Pour cette raison, vous ne devriez pas utiliser les numéros 2, 21 ou 22.

### Lab : Utiliser l'application Read()

Veuillez essayer le lab avec l'application read(). Read accepte les chiffres de l'utilisateur et les insère dans la variable spécifiée ; vous pouvez ensuite utiliser l'application gotoif pour rediriger l'appel.

## Inclusion de contexte

Un contexte peut inclure le contenu d'un autre contexte. Dans l'exemple ci-dessus, n'importe quel canal peut appeler n'importe quelle extension dans le contexte interne, mais seul le canal 4003 peut appeler des extensions internationales. Vous pouvez utiliser l'inclusion de contexte pour faciliter la création du dialplan. En utilisant l'inclusion de contexte, vous pouvez contrôler qui a accès à quelles extensions.

### Dépannage du message « number not found »

Il est très courant de recevoir le message « number not found ». La plupart des gens confondent le concept de contextes inclus car ce n'est vraiment pas intuitif. En règle générale, allez d'abord dans le fichier de configuration du canal entrant, tel que `pjsip.conf`, `chan_dahdi.conf` et `iax.conf`, et déterminez le contexte actuel. Ensuite, allez dans le dialplan dans le fichier extensions.conf et vérifiez si le numéro composé peut être trouvé dans ce contexte. Sinon, quelque chose ne va pas avec votre dialplan. Les règles d'or des contextes sont : 1. Un canal ne peut appeler que des numéros dans le même contexte que le canal. 2. Le contexte où l'appel est traité est défini dans le fichier de configuration du canal entrant (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Utiliser l'instruction switch

Vous pouvez envoyer le traitement du dialplan vers un autre serveur en utilisant la commande switch. Vous aurez besoin du nom et de la clé de l'autre serveur. Le contexte est le contexte de destination.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Ordre de traitement du dialplan

Lorsqu'Asterisk reçoit un appel entrant, il regarde dans le contexte défini par le canal. Dans certains cas, si plusieurs modèles correspondent au numéro composé, Asterisk ne peut pas traiter l'appel exactement de la manière dont vous pensez qu'il devrait le faire. Vous pouvez voir l'ordre de correspondance en utilisant la commande CLI dialplan show. Exemple : Disons que vous voulez composer le 912 pour acheminer vers un trunk analogique (DAHDI/1) et tous les autres numéros commençant par 9 vers un autre trunk analogique (DAHDI/2). Vous écririez quelque chose comme :

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Si deux modèles correspondent à une extension, vous pouvez contrôler quelle extension est traitée en premier en utilisant les contextes inclus. Un contexte inclus est traité plus tard qu'un modèle dans le même contexte.

## L'instruction #INCLUDE

Devrions-nous utiliser un gros fichier ou plusieurs fichiers ? Vous pouvez utiliser l'instruction #include <filename> pour inclure d'autres fichiers dans votre extensions.conf. Par exemple, nous pourrions créer un users.conf pour les utilisateurs locaux et services.conf pour les services spéciaux. Faites attention à ne pas confondre #include <filename> avec l'instruction de contexte

```
include=>context statement.
```

## Sous-routines avec GOSUB

Dans les anciennes versions d'Asterisk, vous aviez la commande Macro. Cette commande a été obsolète depuis longtemps au profit de GOSUB. Nous démontrerons ici comment créer des sous-routines pour le traitement de la messagerie vocale de manière simple et ordonnée. Format de commande :

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

La commande GOSUB est disponible depuis Asterisk 1.6 et prend en charge le passage d'arguments (disponibles à l'intérieur de la sous-routine sous la forme `${ARG1}`, `${ARG2}`, etc.). Avec des arguments, il est maintenant possible de remplacer complètement les anciennes commandes Macro. Les macros (`app_macro`) ont été supprimées dans Asterisk 21 ; vous devez utiliser GOSUB pour les sous-routines.

### Créer la sous-routine

La définition est très similaire. Regardez la sous-routine ci-dessous définie pour la messagerie vocale avec le nom stdexten (choisissez le nom que vous voulez). Après avoir appelé la commande Dial avec le premier argument (nom du canal), nous vérifions le ${DIALSTATUS} pour envoyer la logique d'appel à l'étape suivante.

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

### Appeler une sous-routine

Faites attention lors de l'appel de la sous-routine à utiliser des parenthèses avant les paramètres.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Utiliser Asterisk DB

Pour implémenter le transfert d'appel et les listes noires, nous avons besoin d'un moyen de stocker et de restaurer des données. Heureusement, Asterisk fournit un mécanisme pour stocker et récupérer des données à partir d'une base de données intégrée appelée AstDB. Dans l'Asterisk moderne (y compris Asterisk 22), AstDB est soutenu par **SQLite3** (le fichier `/var/lib/asterisk/astdb.sqlite3`) ; les anciennes versions utilisaient Berkeley DB v1. C'est similaire à la base de données du registre Windows utilisant le concept hiérarchique de famille et de clés. Les données persistent entre les redémarrages d'Asterisk.

> **[Note 2e éd.]** Depuis Asterisk 10, l'AstDB est stockée dans SQLite3 (`astdb.sqlite3`), et non dans le fichier hérité Berkeley DB v1 utilisé par Asterisk 1.8 et versions antérieures. L'API famille/clé est inchangée.

### Fonctions, applications et commandes CLI

Il existe des fonctions, des applications et des commandes CLI qui fonctionnent avec AstDB :

- variable=${DB(<famille/clé>)}
- DB(<famille/clé>)=valeur
- DB_EXISTS(<famille/clé>)

Exemples :

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

Certaines applications peuvent être utilisées pour manipuler AstDB :

- DB_DELETE(<famille/clé>) — fonction qui renvoie et supprime une clé (l'ancienne application `DBdel()` a été supprimée)
- DBdeltree(<famille>)

> **[Note 2e éd.]** L'application `DBdel()` n'existe plus dans Asterisk 22. Supprimez une seule clé avec la fonction de dialplan `DB_DELETE()` — par ex. `Set(x=${DB_DELETE(family/key)})` ou, en tant qu'opération d'écriture, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (supprimer toute une famille/sous-arborescence) est toujours une application.

Il est possible d'utiliser des commandes CLI pour définir et supprimer des clés également :

- database del
- database put
- database show <famille[/clé]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implémenter le transfert d'appel, DND et les listes noires

Dans cet exemple, vous apprendrez à implémenter le transfert d'appel immédiat et le transfert d'appel sur occupation. Nous utiliserons *21* pour programmer le transfert d'appel immédiat et *61* pour programmer le transfert d'appel sur occupation. Pour annuler la programmation, utilisez #21# et #61#, respectivement. Utilisez l'exemple ci-dessus pour remplir la base de données. Familles utilisées :

- CFIM – Transfert d'appel immédiat
- CFBS – Transfert d'appel sur occupation
- DND – Ne pas déranger

Essayez de remplir la base de données en composant :

- *21* (Extension de destination pour le transfert d'appel immédiat)
- *61* (Extension de destination pour le transfert d'appel sur occupation)
- *41* (Extension pour mettre en mode ne pas déranger)

Utilisez la commande CLI database show pour voir les familles, clés et valeurs ajoutées.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Transfert d'appel, liste noire, DND

La sous-routine ci-dessus vérifie si la base de données contient les paires clé:valeur correspondant à CFIM, CFBS ou DND, puis les traite de manière appropriée. La sous-routine follow appelle la routine de numérotation :

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Utiliser une liste noire

> **[Note 2e éd.]** L'application `LookupBlacklist()` a été **supprimée** (elle a disparu avec l'ancien mécanisme de "saut de priorité+101" bien avant Asterisk 22 — confirmé non enregistré dans le labo 22.10.0). Implémentez plutôt une liste noire avec les fonctions `DB()`/`DB_EXISTS()` plus `GotoIf`, par exemple :
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> L'exemple ci-dessous est conservé pour référence historique ; l'option `j` et le saut de priorité `n+101` n'existent plus.

Pour créer une liste noire, nous utilisons l'application LookupBlacklist(). L'application vérifie le nom/numéro dans l'ID de l'appelant. Si le numéro n'est pas trouvé, l'application définit la variable $LOOKUPBLSTATUS sur NOTFOUND. Si le numéro est trouvé, l'application définit la variable sur FOUND. Vous pouvez utiliser l'option « j » dans l'application pour utiliser l'ancien comportement (1.0), sautant 101 positions si le numéro/nom est trouvé. Exemple :

```
[incoming]
exten => s,1,LookupBlacklist(j)
exten => s,2,Dial(PJSIP/4000,20,tTj)
exten => s,3,Hangup()
exten => s,102,Goto(blocked,s,1)
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

Pour insérer un numéro dans la liste noire, nous pouvons utiliser la même ressource qu'auparavant, en utilisant *31* suivi des extensions à mettre sur liste noire. Pour supprimer un numéro de la liste noire, vous devez utiliser #31# suivi du numéro à supprimer.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Vous pouvez également insérer les numéros dans la liste noire en utilisant la CLI de la console :

```
CLI>database put blacklist <name/number> 1
```

Note : Toute valeur peut être associée à la clé. L'application de liste noire recherchera la clé, pas la valeur. Pour effacer le numéro de la liste noire, vous pouvez utiliser :

```
CLI>database del blacklist <name/number>
```

## Contextes basés sur le temps

Dans la figure suivante, nous avons un dialplan avec trois contextes. Le contexte [incoming] est celui où les appels sont généralement reçus. Nous avons inclus quatre lignes qui changent de comportement en fonction de l'heure du système, comme illustré ci-dessous :

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[Note 2e éd.]** L'Asterisk moderne (y compris 22) sépare les champs time-include par des **virgules**, pas par des pipes. L'ancienne forme pipe (`include => context|times|weekdays|mdays|months`) est analysée comme un nom de contexte littéral simple et échoue silencieusement à appliquer toute condition temporelle. Vérifié dans le labo Asterisk 22.10.0.

Pendant les heures de travail habituelles, le traitement sera redirigé vers le mainmenu, où il appellera probablement un IVR pour gérer l'appel entrant. Si l'appel a lieu après les heures d'ouverture, il appellera l'extension de sécurité définie dans la variable ${SECURITY}. Si l'extension de sécurité ne répond pas à l'appel, il sera envoyé à la messagerie vocale de l'opérateur.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Messages basés sur le temps utilisant gotoiftime()

La syntaxe gotoiftime() est montrée ci-dessous.

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[Note 2e éd.]** Dans Asterisk 22, le séparateur de champ est une **virgule**, pas un pipe (la forme pipe était obsolète dans Asterisk 1.6). La syntaxe documentée actuelle est `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`. Un champ optionnel `timezone` est pris en charge.

Cette application peut remplacer le contexte basé sur le temps et semble plus facile à comprendre et à lire. Vous pouvez spécifier l'heure comme suit :

- <timerange>=<heure>':'<minute>'-'<heure>':'<minute> |"*"
- <daysofweek>=<nomdujour>|<nomdujour>'-'<nomdujour>|"*"
- <nomdujour>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<numérodujour>|<numérodujour>'-'<numérodujour> |"*"
- <numérodujour>=nombre de 1 à 31
- <heure>=nombre de 0 à 23
- <minute>=nombre de 0 à 59
- <mois>=<nomdumois>|<nomdumois>'-'<nomdumois>|"*"
- <nomdumois>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Les noms des jours et des mois ne sont pas sensibles à la casse.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

L'instruction précédente transfère le traitement vers l'extension s dans le contexte normalhours si l'appel est entre 08h00 et 18h00 du lundi au vendredi.

## Utiliser DISA pour obtenir une nouvelle tonalité

DISA, ou « direct inward system access », est un système qui permet aux utilisateurs de recevoir une seconde tonalité. Il permet aux utilisateurs de composer à nouveau vers une autre destination. Il est souvent utilisé par les techniciens lorsqu'ils composent des appels longue distance pour le support technique le week-end ; au lieu de composer depuis leur domicile directement vers la destination, ils appellent le numéro DISA du bureau, reçoivent une tonalité, puis appellent la destination. Les frais longue distance sont facturés à l'entreprise au lieu du téléphone domestique.

```
DISA(passcode[,context])
DISA(password-file[,context])
```

Exemple :

```
exten => s,1,DISA(no-password,default)
```

En utilisant l'instruction précédente, l'utilisateur appelle le PBX et — sans nécessiter de mot de passe — reçoit une tonalité. Tout appel utilisant DISA sera traité en utilisant le contexte `default`. Les arguments de cette application incluent un mot de passe global ou un mot de passe individuel dans un fichier. Si aucun contexte n'est spécifié, le contexte `disa` est supposé. Si vous utilisez un fichier de mots de passe, le chemin complet doit être spécifié. Un ID d'appelant peut également être spécifié pour la numérotation externe DISA. Exemple :

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[Note 2e éd.]** Asterisk 22 utilise des virgules comme séparateurs d'arguments (la forme pipe était obsolète en 1.6). La syntaxe complète est `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])`, et le contexte par défaut lorsqu'aucun n'est donné est `disa` (pas "DISA"). Vérifié avec `core show application DISA` dans le labo Asterisk 22.10.0.

## Limiter les appels simultanés

La fonction GROUP() vous permet de compter combien de canaux actifs vous avez dans un groupe en même temps. Exemple : Vous avez une succursale à Rio de Janeiro, où les téléphones suivent le modèle « _214X ». Cet emplacement est desservi par une ligne louée, avec 64K réservés pour la bande passante vocale. Dans ce cas, le nombre maximal d'appels autorisés est de 2 (G.729, 30r.2K par appel). Pour limiter les appels vers Rio à deux :

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Messagerie vocale

La messagerie vocale est un système de réponse téléphonique informatisé qui enregistre les messages vocaux entrants, les enregistrant sur disque ou les envoyant par e-mail. Parfois, il dispose d'un annuaire où vous pouvez rechercher des boîtes vocales par nom. Dans le passé, les systèmes de messagerie vocale étaient très coûteux. Maintenant, avec la téléphonie IP, la messagerie vocale devient une fonctionnalité standard.

Pour configurer la messagerie vocale, vous devez suivre les étapes suivantes.

**Étape 1 : Modifiez `voicemail.conf` et définissez les paramètres généraux.**

- `format` — codec utilisé pour enregistrer le message (par ex., wav49, wav, gsm)
- `serveremail` — de qui la notification par e-mail doit sembler provenir
- `maxmsg` — nombre maximal de messages dans la boîte aux lettres ; après ce seuil, les messages sont supprimés
- `maxsecs` — longueur maximale d'un message vocal, en secondes
- `minsecs` — longueur minimale d'un message, en secondes ; en dessous de ce seuil, aucun message n'est enregistré
- `maxsilence` — combien de secondes de silence traiter comme la fin du message

**Étape 2 : Modifiez `voicemail.conf` et créez les boîtes aux lettres des utilisateurs.**

### Voicemail.conf

Une boîte aux lettres est définie avec une ligne par boîte aux lettres, sous la forme :

```
mailboxID => pincode,fullname,email,pager-email,options
```

Les champs sont :

- **MailboxID** — généralement le numéro d'extension
- **Pincode** — mot de passe pour accéder au système de messagerie vocale
- **Full name** — utilisé par l'application d'annuaire
- **E-mail** — adresse pour la notification de messagerie vocale
- **Pager e-mail** — adresse pour la notification via une passerelle SMS ou un téléavertisseur
- **Options** — options par boîte aux lettres (les mêmes options que dans `[general]`, mais appliquées à cette boîte aux lettres)

La messagerie vocale a plusieurs options qui contrôlent son comportement. Pour l'instant, nous nous en tiendrons aux options par défaut et nous concentrerons sur la définition de la boîte aux lettres. Après la section `[general]` dans le fichier, vous commencez à configurer les IDs de boîte aux lettres, chacun dans son propre contexte. Exemple :

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Veuillez vérifier les options avancées dans le fichier `voicemail.conf`.

**Étape 3 : Configurez le fichier `extensions.conf`.**

Ci-dessous, vous avez les instructions pour créer la sous-routine et l'appel qui implémentent la messagerie vocale dans `extensions.conf`. Nous utilisons la valeur de la variable de canal `${DIALSTATUS}` pour rediriger le flux d'appel vers le menu de messagerie vocale approprié.

### Sous-routine de messagerie vocale

## Utiliser l'application Voicemailmain()

L'application voicemailmain() est utilisée pour configurer la boîte aux lettres vocale. Les utilisateurs peuvent appeler l'application, enregistrer leur message d'accueil et écouter leur messagerie vocale. Pour appeler l'application dans le dialplan, utilisez :

```
exten=>9000,1,VoiceMailMain()
```

Vous trouverez ci-dessous une liste des options disponibles pour l'application.

### Syntaxe de l'application Voicemail

Cette application permet à la partie appelante de laisser un message pour une liste spécifiée de boîtes aux lettres. Lorsque plusieurs boîtes aux lettres sont spécifiées, le message d'accueil sera pris de la première boîte aux lettres spécifiée. L'exécution du dialplan s'arrêtera si la boîte aux lettres spécifiée n'existe pas. La syntaxe est montrée ci-dessous :

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

Dans tous les cas, le fichier beep.gsm sera joué avant que l'enregistrement ne commence. Les messages vocaux seront stockés dans le répertoire inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Si un appelant appuie sur 0 (zéro) pendant l'annonce, il sera transféré vers l'extension 'o' (out) dans le contexte actuel de la messagerie vocale. Cela peut être utilisé pour sortir vers l'opérateur. Si pendant l'enregistrement l'appelant appuie sur # ou si la limite de silence expire, l'enregistrement est arrêté et l'appel passe à la priorité suivante. Assurez-vous de gérer l'appel après que la messagerie vocale a été jouée, comme indiqué ci-dessous.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Marquer les messages vocaux comme urgents

Vous pouvez marquer certains messages comme « urgents ». Deux méthodes sont disponibles pour cela :

- Passer l'option 'U' dans l'application voicemail()
- Spécifier review=yes dans le fichier voicemail.conf. Si vous utilisez cette option, l'utilisateur pourra marquer le message comme urgent après avoir enregistré les instructions vocales.

## Envoyer la messagerie vocale par e-mail

Dans certains cas (comme le mien), nous n'utilisons tout simplement pas l'application voicemailmain() pour lire les e-mails. Il est plus simple et plus pratique d'envoyer tous les messages par e-mail avec l'audio en pièce jointe. En utilisant les paramètres 'attach' et 'delete', vous pouvez envoyer tous les e-mails par e-mail et les supprimer de la boîte aux lettres.

```
attach=yes
delete=yes
```

Pour envoyer la messagerie vocale par e-mail, l'application de messagerie vocale utilise l'agent de transfert de messages (MTA), un composant de votre système d'exploitation. Debian utilise Exim comme MTA. L'application qui envoie l'e-mail est définie dans le paramètre 'mailcmd'.

```
mailcmd =/usr/sbin/sendmail -t
```

Dans la distribution Debian de Linux, le MTA est Exim. Pour configurer Exim dans Debian, utilisez :

```
dpkg-reconfigure exim4-config
```

Vous pouvez choisir de faire envoyer un e-mail par votre MTA directement via SMTP ou un smarthost (généralement le serveur de messagerie de votre entreprise). Vérifiez auprès de votre administrateur de messagerie le meilleur moyen d'envoyer des e-mails depuis le serveur Asterisk vers votre serveur de messagerie.

## Personnaliser le message e-mail

Vous pouvez contrôler la façon dont les messages sont envoyés en configurant les variables suivantes : Variables pour l'objet et le corps de l'e-mail :

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Le corps et l'objet de l'e-mail sont construits à partir d'un modèle que vous définissez dans la section `[general]` de `voicemail.conf`. Vous pouvez modifier à la fois le corps et l'objet, mais la limite de taille du message est de 512 octets. Dans le modèle, `\n` insère un saut de ligne et `\t` insère une tabulation.

L'exemple `emailsubject` ci-dessous est simple. L'exemple `emailbody` est très proche de la valeur par défaut ; la valeur par défaut affiche juste le CIDNAME lorsqu'il n'est pas nul, sinon le CIDNUM, ou "un appelant inconnu" lorsque les deux sont nuls.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interface Web de messagerie vocale

Il existe un script Perl dans la distribution source appelé `vmail.cgi`, situé à `contrib/scripts/vmail.cgi` dans l'arborescence source d'Asterisk (il est toujours fourni avec Asterisk 22). La commande `make install` n'installe pas cette interface ; vous devez exécuter `make webvmail` depuis le répertoire source. Ce script nécessite l'interpréteur de commandes Perl et un serveur web (tel qu'Apache) pour être installé sur le serveur.

```
make webvmail
```

La cible `make webvmail` installe le script (setuid root) dans le répertoire CGI de votre serveur web (`HTTP_CGIDIR`) et copie les images de support de `images/*.gif` dans `HTTP_DOCSDIR/_asterisk` (par défaut `/var/www/html/_asterisk`). Si ces chemins ne correspondent pas à la disposition de votre serveur web, modifiez les variables `HTTP_CGIDIR` et `HTTP_DOCSDIR` dans le `Makefile` de niveau supérieur avant d'exécuter la cible.

## Notification de messagerie vocale

Vous pouvez configurer la messagerie vocale pour envoyer un message de notification à votre téléphone lorsque vous avez une nouvelle messagerie vocale. Dans Asterisk 22, l'indication d'attente de message (MWI) fonctionne avec les téléphones PJSIP et SIP ainsi qu'avec les téléphones DAHDI. Pour indiquer une messagerie vocale non écoutée, un voyant peut clignoter ou le téléphone peut jouer une tonalité d'obturation. Vous devez configurer la boîte aux lettres dans le fichier de configuration du canal correspondant. Exemple : `pjsip.conf` (dans la section endpoint) :

```
mailboxes=8590
```

> **[Note 2e éd.]** Dans PJSIP, l'indicateur de boîte aux lettres est défini avec l'option `mailboxes` à l'intérieur de la section `[endpoint]` de `pjsip.conf`, plutôt que `mailbox=` dans `sip.conf`. Les abonnements MWI sont gérés par `res_pjsip_mwi`. Vérifiez la syntaxe de configuration exacte pour Asterisk 22.

![L'interface web Comedian Mail (`vmail.cgi`) : la connexion à la messagerie vocale web Asterisk — entrez votre boîte aux lettres et votre mot de passe pour lire, enregistrer, transférer ou supprimer la messagerie vocale depuis un navigateur. Elle est toujours fournie avec Asterisk 22 et est installée avec `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab : Notification de message sur le téléphone

Ce labo a été testé en utilisant un softphone SIP. 1. Modifiez `pjsip.conf` et ajoutez `mailboxes=4401` dans la section endpoint pour l'appareil nommé 4401. 2. Modifiez le extensions.conf et créez une extension pour enregistrer une messagerie vocale vers les extensions 4401.

```
exten=9008,n,voicemail(b4401)
```

3. Allez dans la console CLI et rechargez. 4. Dans le softphone SipPulse, ouvrez les paramètres du compte SIP et activez la vérification de la messagerie vocale (message-waiting) pour le compte. 5. Composez le 9008 et laissez un message. 6. Observez l'icône de message sur le téléphone.

## Utiliser l'application directory

Cette application vous permet de trouver rapidement un utilisateur à appeler. La liste des noms et des extensions correspondantes est récupérée à partir du fichier de configuration de la messagerie vocale voicemail.conf. La syntaxe de l'application peut être affichée en utilisant core show application directory :

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

### Lab : Utiliser l'application directory

1. Modifiez le fichier voicemail.conf pour ajouter deux extensions dans le dialplan

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Créez ces extensions dans votre dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Allez dans la console et rechargez 4. Composez le 9006 et enregistrez un nom pour chaque extension (4400, 4401) 5. Composez le 9007 et sélectionnez les trois lettres du nom de famille pour une extension (Eas=327). Si c'est la bonne option, appuyez sur '1' pour transférer vers le nom.

## Lab : Tout mettre ensemble

Jusqu'à présent, vous avez appris plusieurs concepts de dialplan. Mettons toutes les applications, fonctions et concepts dans un exemple de dialplan afin que vous puissiez comprendre comment ils sont utilisés ensemble. Guidons-vous à travers toute la configuration du PBX pour le scénario ci-dessous.

- 4 trunks analogiques
- 16 extensions basées sur SIP
- 3 classes de service :
    - restrict (interne, local et 1-800)
    - ld (longue distance)
    - ldi (international)
- Message après les heures d'ouverture
- Standard automatique

### Étape 1 – Configurer les canaux

Trunks analogiques (chan_dahdi.conf) Tout d'abord, nous configurerons les trunks analogiques dans le fichier de configuration du canal DAHDI chan_dahdi.conf. Dans ce cas, nous utiliserons une carte T400P Digium avec 4 interfaces FXO. Supposons que le pilote soit déjà chargé et que le fichier de configuration du pilote (/etc/dahdi/system.conf) soit correctement configuré.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

Canaux SIP (pjsip.conf) Nous avons choisi la numérotation du dialplan de 2000 à 2099. Deux codecs seront utilisés : G.729 et G.711 ulaw. Le premier sera utilisé pour les téléphones utilisant Asterisk sur Internet ou WAN tandis que le second sera utilisé pour les téléphones utilisant le réseau local. Dans `pjsip.conf`, nous arbitrerons quels appareils appartiendront à chaque classe de service (restrict, ld, ldi). Pour réduire la vulnérabilité aux attaques par force brute, nous utiliserons les adresses MAC des téléphones comme noms d'appareils. Je vous conseille vivement d'utiliser des mots de passe forts pour éviter les attaques par force brute !

Nous définissons un transport et trois modèles réutilisables — une base endpoint avec les codecs partagés, une authentification userpass et un seul contact AOR — puis nous attachons chaque appareil aux modèles et ne remplaçons que ce qui diffère (son contexte de classe de service et ses informations d'identification). `host=dynamic` devient un AOR contre lequel le téléphone s'enregistre, et `directmedia` devient `direct_media` :

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

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Étape 2 – Configurer le dialplan

Maintenant, commençons à configurer le extensions.conf. Définissez les extensions internes et la numérotation locale

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Définissez LD (longue distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Définissez les appels internationaux

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Étape 3 - Recevoir des appels via un standard automatique

Pour recevoir des appels, utilisez deux contextes. Le premier est pour le fonctionnement aux heures normales, où l'appel sera reçu par un standard automatique. Le second est pour après les heures d'ouverture, où l'appelant recevra un message tel que « vous avez appelé la société XYZ, nos heures normales sont de 08h00 à 18h00 ; si vous connaissez le numéro de l'extension de destination, vous pouvez essayer de le composer maintenant ou raccrocher ». Menus : Heures normales, Après les heures d'ouverture Dans les menus ci-dessous, le système jouera un message avertissant l'appelant que l'entreprise a été contactée après les heures de travail régulières, permettant à l'appelant de composer le numéro de l'extension de destination (quelqu'un peut travailler après les heures de travail régulières).

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

Menus : Principal et Ventes Pendant les heures de travail normales, l'appel est répondu par un menu de standard automatique, recevant un message tel que « bienvenue à la société XYZ ; composez 1 pour les ventes, 2 pour le support technique, 3 pour la formation, ou le numéro d'extension souhaité ».

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

Avec toutes ces instructions, la fonctionnalité de votre plan de numérotation est maintenant prête. Dans la section suivante, nous démontrerons comment faire fonctionner le PBX.

## Résumé

Dans ce chapitre, vous avez appris à recevoir des appels en utilisant un IVR ou un standard automatique. Vous avez étudié le concept d'inclusion de contexte et implémenté quelques exemples. Des sous-routines ont été utilisées pour éviter de taper de manière répétitive, et la base de données Asterisk basée sur le moteur Berkley DB a été utilisée pour les fonctions nécessitant un stockage de données (par ex., transfert d'appel, ne pas déranger, listes noires). Enfin, vous avez appris à implémenter un comportement après les heures d'ouverture et implémenté un dialplan complet en utilisant ces concepts.

## Quiz

1. Une inclusion de contexte dépendante du temps utilise la forme `include => context,<times>,<weekdays>,<mdays>,<months>`. Que fait `include => normalhours,08:00-18:00,mon-fri,*,*` ?
   - A. Exécuter les extensions du lundi au vendredi, de 08h00 à 18h00
   - B. Exécuter les options tous les jours de tous les mois
   - C. Rien ; le format est invalide
2. Dans l'Asterisk moderne (y compris Asterisk 22), les champs d'un `include =>` basé sur le temps et de `GotoIfTime()` sont séparés par quel caractère ?
   - A. Le pipe `|`
   - B. La virgule `,`
   - C. Le point-virgule `;`
   - D. La barre oblique `/`
3. Pour appeler plusieurs canaux à la fois (les faire sonner simultanément), vous les séparez à l'intérieur de `Dial()` avec le caractère ___.
4. Un menu vocal qui joue une invite en attendant que l'appelant compose une extension est généralement créé avec l'application ___.
5. Vous pouvez inclure le contenu d'un autre fichier à l'intérieur de `extensions.conf` en utilisant l'instruction ___ (note : ceci est différent de l'instruction de contexte `include =>`).
6. Dans Asterisk 22, la base de données AstDB intégrée est soutenue par :
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Lorsque vous utilisez `Dial(type1/identifier1&type2/identifier2)`, Asterisk appelle chaque canal en séquence, attendant 20 secondes entre eux.
   - A. Faux
   - B. Vrai
8. Avec l'application Background(), vous devez attendre que le message finisse de jouer avant de pouvoir appuyer sur un chiffre DTMF pour choisir une option.
   - A. Faux
   - B. Vrai
9. Étant donné la syntaxe `Goto([[context,]extension,]priority)`, lesquelles des invocations suivantes de l'application Goto() sont valides ? (cochez tout ce qui s'applique)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Pour supprimer une seule clé de l'AstDB dans le dialplan Asterisk 22, vous utilisez :
    - A. L'application `DBdel()`
    - B. La fonction `DB_DELETE()`
    - C. L'application `DBdeltree()`
    - D. L'application `LookupBlacklist()`

**Réponses :** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
