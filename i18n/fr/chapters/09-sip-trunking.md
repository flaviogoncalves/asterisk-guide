# SIP trunking, DID & the PSTN

Un PBX qui ne peut appeler que lui-même n'est pas très utile. Tôt ou tard, chaque système doit atteindre le reste du monde — le réseau téléphonique public commuté (PSTN), un fournisseur SIP ou un autre PBX. Le lien qui transporte ces appels est un **trunk**. À l'ère du TDM, un trunk était un circuit physique : un accès primaire T1/E1 ou un faisceau de lignes analogiques FXO. Aujourd'hui, il s'agit presque toujours d'un **SIP trunk** — une connexion logique vers un fournisseur de services de téléphonie sur Internet (ITSP) transportée sur le même réseau IP que tout le reste.

Ce chapitre montre comment connecter Asterisk 22 à un ITSP avec PJSIP, comment choisir entre un trunk basé sur l'enregistrement et un trunk basé sur IP, comment router les numéros DID entrants vers la bonne destination, comment envoyer des appels sortants avec le bon identifiant d'appelant et le formatage E.164, et comment construire un basculement et un routage au moindre coût sur plusieurs trunks. Nous terminons par la gestion du NAT pour les trunks et un laboratoire qui met en place un second Asterisk (et SIPp) en tant qu'ITSP fictif afin que vous puissiez passer de vrais appels via un trunk.

Tout ce qui est présenté ici est vérifié par rapport au laboratoire Asterisk 22.10.0 du livre ; le modèle d'objet trunk est le même que celui introduit dans *Building your first PBX with PJSIP* et *SIP & PJSIP in depth*.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Connecter Asterisk 22 à un ITSP avec PJSIP
- Choisir entre des trunks basés sur l'enregistrement et des trunks basés sur IP (statiques)
- Router les DID entrants vers la bonne extension, le bon IVR ou la bonne file d'attente
- Router les appels sortants avec le bon identifiant d'appelant et le formatage E.164
- Construire un basculement de trunk et un routage au moindre coût avec `${DIALSTATUS}`
- Gérer le NAT pour les trunks sur le transport et l'endpoint

## Qu'est-ce qu'un SIP trunk

Un SIP trunk est un chemin vocal logique entre votre PBX et un autre système SIP. En pratique, cet « autre système » est l'une des deux choses suivantes :

- **Un ITSP (Internet Telephony Service Provider).** Un opérateur commercial qui vous vend l'origination et la terminaison d'appels et, généralement, un bloc de numéros de téléphone (DID). Vous pointez Asterisk vers l'hôte de signalisation du fournisseur, et le fournisseur connecte vos appels au PSTN plus large. C'est ainsi que la plupart des systèmes modernes atteignent le réseau téléphonique — aucun matériel de téléphonie requis.
- **Une passerelle PSTN.** Un appareil (ou un autre Asterisk) qui possède des interfaces PSTN physiques — une carte PRI, des ports FXO analogiques ou une passerelle GSM/4G — et les présente à votre PBX en tant que SIP. La passerelle effectue la conversion TDM-vers-SIP ; du point de vue d'Asterisk, il s'agit simplement d'un autre SIP trunk.

Quoi qu'il en soit, dans PJSIP, un trunk est **juste un endpoint**. La même famille d'objets que vous avez utilisée pour un téléphone — `endpoint`, `auth`, `aor`, éventuellement `identify` et `registration` — construit un trunk. Les différences résident dans les détails : un trunk s'authentifie en *sortant* (vous êtes le client, donc les identifiants vont dans `outbound_auth`, pas `auth`), il n'enregistre généralement pas d'agent utilisateur auprès de vous (vous vous enregistrez auprès de *lui*, ou il vous envoie du trafic depuis une IP connue), et il fait atterrir les appels entrants dans un context dédié tel que `from-pstn` au lieu de `from-internal`.

> **Comparé à l'ancien trunk TDM.** Un PRI vous donnait un nombre fixe de canaux B (23 sur un T1, 30 sur un E1) et signalait l'établissement de l'appel sur un canal D dédié (voir le chapitre *Legacy channels*). Un SIP trunk n'a pas de nombre de canaux fixe — la capacité est ce que votre bande passante, la politique de votre fournisseur et toute limite `max_contacts`/appels simultanés permettent. L'identifiant d'appelant, le DID et la progression d'appel qui passaient autrefois par les éléments d'information ISDN passent désormais par les en-têtes SIP et le SDP.

Il existe deux façons pour un ITSP d'accepter d'échanger du trafic avec vous, et elles déterminent comment vous construisez le trunk : **basé sur l'enregistrement** et **basé sur IP (statique)**. Nous couvrons chacun à tour de rôle.

## Trunks basés sur l'enregistrement

Un trunk basé sur l'enregistrement est le modèle utilisé lorsque le fournisseur s'attend à ce que *vous* vous connectiez à *lui*. Votre Asterisk envoie périodiquement un SIP `REGISTER` au fournisseur, en s'authentifiant avec un nom d'utilisateur et un mot de passe, exactement de la même manière qu'un téléphone s'enregistre auprès de votre PBX. C'est courant lorsque votre IP publique est dynamique, lorsque vous êtes derrière un NAT, ou lorsque le fournisseur identifie simplement les clients par des identifiants SIP plutôt que par adresse IP.

Dans PJSIP, la connexion sortante réside dans un objet `registration` dédié. Il remplace la ligne unique `register =>` que le pilote supprimé `chan_sip` utilisait dans `sip.conf`. Voici un trunk d'enregistrement complet vers un fournisseur fictif, suivant le modèle vérifié des chapitres précédents — notez `outbound_auth` (pas `auth`), `server_uri`/`client_uri` (pas `server`/`client`), `from_user`/`from_domain` sur l'endpoint, et `dtmf_mode=rfc4733` :

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

Quelques points à noter :

- **`auth_type=digest`, pas `userpass`.** Les deux produisent la même authentification digest, mais dans Asterisk 22, `userpass` (et l'ancien `md5`) sont **dépréciés et convertis silencieusement en `digest`**. Préférez `digest` dans la nouvelle configuration ; vous verrez toujours `userpass` dans les anciens fichiers et dans les chapitres précédents de ce livre.
- **`outbound_auth` sur l'endpoint et l'enregistrement.** L'enregistrement l'utilise pour authentifier le `REGISTER` ; l'endpoint l'utilise pour répondre au `407 Proxy Authentication Required` que le fournisseur renvoie vers un `INVITE` sortant. Ils peuvent partager un objet `auth`.
- **`from_user` / `from_domain`.** De nombreux fournisseurs rejettent les appels dont l'en-tête `From` ne contient pas votre numéro de compte et leur domaine. Ces deux options définissent exactement cela.
- **`contact_user=4830001000`.** Cela devient la partie utilisateur du `Contact` que vous enregistrez, afin que le fournisseur sache quel numéro utiliser pour livrer les appels entrants. C'est l'équivalent moderne du suffixe `/9999` sur l'ancienne ligne `register =>`.
- **`retry_interval=60`.** Si l'enregistrement échoue, réessayez toutes les 60 secondes.

Après un rechargement, confirmez l'enregistrement avec `pjsip show registrations`. Dans le laboratoire — où `itsp.example.com` ne répond pas réellement — le tableau ressemble à ceci :

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

Le suffixe `(exp. Ns)` décompte les secondes jusqu'à la prochaine tentative ; une fois qu'il passe à zéro, il affiche brièvement `(exp. Ns ago)` avant que la nouvelle tentative ne se déclenche. Face à un fournisseur réel, la colonne `Status` affiche `Registered` avec les secondes restantes jusqu'au prochain rafraîchissement. `Rejected` (ou `Unregistered`) signifie que le fournisseur n'a pas accepté la connexion — activez `pjsip set logger on` et lisez la réponse `401`/`403`, presque toujours un mauvais nom d'utilisateur, mot de passe ou domaine `client_uri`.

## Trunks basés sur IP (statiques)

Le second modèle ne nécessite aucune inscription. Le fournisseur connaît votre adresse IP publique et envoie les appels directement vers celle-ci ; vous, à votre tour, envoyez les appels vers l'IP de signalisation connue du fournisseur. L'authentification se fait par **adresse IP source**, et non par identifiants SIP. C'est typique pour les trunks entre deux serveurs que vous contrôlez, ou pour un trunk d'entreprise où les deux côtés ont des adresses statiques.

L'objet clé est `identify`. Il dit à Asterisk : « toute requête SIP arrivant de *cette* IP appartient à *cet* endpoint ». Sans cela, PJSIP essaie de faire correspondre une requête entrante à un endpoint par l'utilisateur `From`, ce que le trafic d'un opérateur ne satisfera pas — l'appel serait donc rejeté ou tomberait sur l'endpoint `anonymous`.

Un trunk statique supprime l'objet `registration` et ajoute `identify` :

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` accepte une adresse IP, une plage CIDR ou un nom d'hôte. **Les noms d'hôtes sont résolus une seule fois, au moment du chargement de la configuration**, donc si l'IP de votre fournisseur change, vous devez recharger. Pour un opérateur qui publie plusieurs passerelles média, listez chaque IP de signalisation — vous pouvez répéter `match` ou donner un CIDR :

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Vérifiez ce qu'Asterisk acceptera avec `pjsip show identifies`. Capturé depuis le laboratoire (la ligne `sipp-identify` est l'endpoint SIPp préexistant du laboratoire) :

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### L'implication en matière de sécurité

Un trunk basé sur IP sans authentification est une porte, et `identify`/`match` est le seul verrou dessus. Si vous `match` une plage trop large — ou si un attaquant peut usurper une IP source — les appels atterrissent dans votre contexte `from-pstn` sans authentification. Deux défenses, utilisées ensemble :

- **Faites correspondre aussi étroitement que possible.** Préférez les IP d'hôtes spécifiques aux larges CIDR. Seules les véritables IP de signalisation du fournisseur doivent figurer dans `match`.
- **Associez-le à une ACL.** PJSIP peut abandonner le trafic au niveau de la couche SIP avant même qu'il n'atteigne un endpoint, en utilisant un objet `type=acl` (ou `acl.conf`) :

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Référencez-le depuis la section globale (`acl=itsp-acl` dans `[global]`/`type=global`) ou appliquez-le par transport. Le principe est le même que dans le chapitre SIP : refusez tout, puis autorisez uniquement ce en quoi vous avez confiance. Et quel que soit le contexte de votre trunk, **ne le laissez jamais atteindre un contexte capable de rappeler vers le PSTN** sans une règle délibérée et authentifiée — c'est le trou classique de la fraude téléphonique.

> **Quel modèle dois-je utiliser ?** Si le fournisseur vous donne un nom d'utilisateur et un mot de passe, utilisez un trunk **d'enregistrement**. S'ils demandent votre adresse IP et vous donnent la leur, utilisez un trunk **d'identification**. Certains fournisseurs prennent en charge les deux ; de nombreux trunks réels combinent un enregistrement (pour que le fournisseur puisse vous trouver) avec une identification (pour que les INVITE entrants des passerelles média du fournisseur soient reconnus même lorsqu'ils arrivent d'une IP autre que celle du registraire).

## Routage entrant et gestion des DID

Une fois que les appels entrants arrivent, ils atterrissent dans le `context` de l'endpoint — ici `from-pstn`. Un **DID** (numéro d'appel direct) est simplement le numéro composé que le fournisseur vous transmet dans l'URI de la requête. Votre travail dans le dialplan est de mapper chaque DID à une destination : une extension unique, un IVR, une file d'attente ou un groupe d'appel.

Le numéro envoyé par le fournisseur est comparé en tant que `${EXTEN}` dans `from-pstn`. La partie que vous voyez dépend du fournisseur — certains envoient le numéro E.164 complet (`+4830001000`), certains envoient le numéro national, certains n'envoient que les derniers chiffres. Inspectez un appel entrant réel avec `pjsip set logger on` et regardez l'URI de la requête avant d'écrire des modèles.

### Un DID vers une extension

Le cas le plus simple — un seul DID routé directement vers un téléphone :

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### Un DID vers un IVR (standard automatique)

Un numéro principal qui doit répondre avec un menu au lieu de faire sonner un téléphone :

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` est le contexte du standard automatique que vous avez construit dans les chapitres sur le dialplan (`Background()` + `WaitExten()`). Router le DID est juste un `Goto`.

### Un DID vers une file d'attente

Une ligne de support qui doit atterrir dans une file d'attente d'appels :

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Plusieurs DID à la fois

Lorsque vous achetez un bloc de numéros, un modèle permet de garder le dialplan petit. Supposons que votre plage de DID soit `4830003000`–`4830003099` et que le fournisseur envoie le numéro complet ; mappez les deux derniers chiffres de chaque DID vers l'extension `60xx` :

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` prend les deux derniers chiffres (le décalage négatif compte à partir de la droite), donc `4830003007` fait sonner `PJSIP/6007`. Une table de recherche `did => extension` construite avec `GoSub` ou une base de données Asterisk (`AstDB`/`func_odbc`) évolue encore plus, mais pour une poignée de numéros, les modèles explicites sont les plus clairs.

> **Attrapez le DID non reconnu.** Ajoutez une extension `i` (invalide) à `from-pstn` afin qu'un numéro entrant mal routé joue une annonce ou fasse sonner l'opérateur au lieu de tomber silencieusement :
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Routage sortant, identifiant d'appelant et E.164

Les appels sortants circulent dans l'autre sens : un téléphone interne compose un numéro, votre dialplan le fait correspondre, supprime tout préfixe d'accès, définit l'identifiant d'appelant attendu par le fournisseur et transmet l'appel à l'endpoint du trunk avec `Dial(PJSIP/<number>@itsp)`.

### Envoi de l'appel vers le trunk

La syntaxe de canal pour un trunk est `PJSIP/<number>@<endpoint>` : la partie avant le `@` devient la partie utilisateur de l'URI de la requête sortante, et la partie après le `@` nomme l'endpoint dont le `aor` `contact` fournit l'hôte de destination. Une règle classique « composez le 9 pour une ligne extérieure » :

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` supprime le code d'accès `9` initial avant que le numéro ne soit envoyé. Le modèle `_9NXXXXXXXXX` correspond à `9` plus un numéro à 10 chiffres dont le premier chiffre est 2–9 ; ajustez-le à votre plan de numérotation.

### Identifiant d'appelant sur les appels sortants

La plupart des ITSP ignorent — ou rejettent activement — un identifiant d'appelant qui n'est pas un numéro que vous possédez. Définissez le numéro d'identifiant d'appelant sortant sur l'un de vos DID avec la fonction `CALLERID(num)` avant `Dial()`, comme indiqué ci-dessus. Vous pouvez également définir le nom :

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Si le fournisseur supprime ou remplace toujours votre nom d'identifiant d'appelant, c'est leur politique — de nombreux opérateurs tirent le nom affiché de leur propre base de données CNAM indexée sur le numéro, et non de votre en-tête `From`.

Deux options d'endpoint interagissent avec cela :

- **`from_user`** définit la partie utilisateur de l'en-tête `From` au niveau SIP, que certains fournisseurs utilisent pour identifier votre compte indépendamment de `CALLERID(num)`.
- **`trust_id_outbound`** (par défaut `no`) contrôle si Asterisk enverra des en-têtes d'identité sensibles à la confidentialité (`P-Asserted-Identity`/`P-Preferred-Identity`) en sortie. Laissez-le désactivé à moins que votre fournisseur ne documente qu'il souhaite PAI, auquel cas définissez `trust_id_outbound=yes` et `send_pai=yes`.

### Normalisation vers E.164

E.164 est le format de numéro international : un `+` initial, le code pays, puis le numéro national, sans espaces ni ponctuation (par exemple `+5548999990000` ou `+14155550100`). Les opérateurs attendent de plus en plus — ou exigent — E.164 sur le trunk. Plutôt que de disperser le formatage dans le dialplan, normalisez une fois dans le contexte sortant.

Un exemple nord-américain qui accepte un numéro local à 10 chiffres, un numéro préfixé par `1` à 11 chiffres, ou un numéro déjà au format E.164, et présente toujours `+1…` au trunk :

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

Certains fournisseurs veulent le `+` ; d'autres veulent les chiffres nus. Si le vôtre rejette le `+`, supprimez-le à la sortie avec `${EXTEN:1}` dans le `Dial`. Le point est que toute la connaissance du format réside au même endroit, donc changer de fournisseur — ou en ajouter un second — est un changement d'une seule ligne.

## Basculement et routage au moindre coût

Avec un seul trunk, une panne de fournisseur signifie aucun appel sortant. Avec deux ou plus, vous pouvez basculer automatiquement et même choisir l'itinéraire le moins cher par destination — *routage au moindre coût* (LCR).

### Basculement avec `${DIALSTATUS}`

`Dial()` définit la variable de canal `${DIALSTATUS}` lorsqu'il revient. Les valeurs qui vous intéressent pour le basculement sont `CHANUNAVAIL` (le trunk n'a pas pu être atteint du tout) et `CONGESTION` (l'appel a été rejeté, par exemple tous les circuits sont occupés). Essayez le trunk principal ; s'il n'a pas pu acheminer l'appel, passez au secours :

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Notez le choix délibéré de **ne pas** basculer sur `BUSY` ou `NOANSWER` — cela signifie que la *partie appelée* a été atteinte et a refusé, donc réessayer sur un autre trunk ferait sonner à nouveau un téléphone qui a déjà dit non (et pourrait vous coûter un deuxième appel). Ne reroutez que lorsque le *trunk lui-même* a échoué.

### Une sous-routine de routage réutilisable

Répéter cette logique pour chaque modèle de numérotation est sujet aux erreurs. Factorisez-la dans une routine `GoSub` qui prend le numéro de destination et essaie chaque trunk dans l'ordre :

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

Désormais, chaque modèle sortant est un appel `GoSub`, et l'ordre des trunks est défini à un seul endroit.

### Routage au moindre coût par destination

Le vrai LCR choisit le trunk en fonction de la destination de l'appel. Une forme courante consiste à faire correspondre le préfixe de destination et à envoyer chaque classe d'appel au fournisseur le moins cher pour celle-ci — par exemple, les appels internationaux vers un opérateur de gros et les appels locaux/nationaux vers votre principal :

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

Pour plus de quelques préfixes, stockez la table de routage dans une base de données (`func_odbc`/`AstDB`) et recherchez le trunk par préfixe au lieu de coder en dur les modèles. Le dialplan reste petit et les tarifs résident dans une table que vous pouvez modifier sans recharger la logique.

## NAT et trunks

Le NAT est la cause la plus fréquente de problèmes de trunk — généralement de l'audio unidirectionnel, ou un trunk qui s'enregistre mais ne reçoit jamais d'appels entrants. La cause est la même que pour les téléphones (couverte dans *SIP & PJSIP in depth* et *Designing a VoIP network*) : Asterisk annonce sa propre idée de son adresse dans SIP et SDP, et derrière un NAT, il s'agit d'une adresse privée RFC 1918 vers laquelle le fournisseur ne peut pas router.

Pour les trunks, la correction comporte deux parties — les paramètres sur le **transport** (votre adresse publique) et les paramètres sur l'**endpoint** (comment traiter les médias du fournisseur).

### Sur le transport — votre adresse publique

Lorsque le serveur Asterisk lui-même est derrière un NAT (un cloud ou une boîte sur site avec une IP privée et une IP publique 1:1), indiquez au transport son adresse publique et quels réseaux sont locaux. Ces options sont définies une fois, sur le `transport`, et s'appliquent à tout le trafic sur celui-ci :

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — l'IP publique qu'Asterisk écrit dans les en-têtes SIP (`Via`, `Contact`) pour les destinations en dehors de `local_net`.
- **`external_media_address`** — l'IP publique qu'Asterisk écrit dans la ligne SDP `c=` afin que le RTP revienne au bon endroit. Généralement identique à l'adresse de signalisation.
- **`local_net`** — les réseaux qu'Asterisk traite comme internes, afin qu'il ne réécrive *pas* les adresses pour les pairs LAN. Listez chaque sous-réseau interne.

### Sur l'endpoint — les médias du fournisseur

L'autre moitié gère un fournisseur qui se trouve lui-même derrière un NAT, ou qui envoie simplement des médias depuis une adresse autre que celle indiquée dans son SDP. Définissez ces paramètres par endpoint de trunk :

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — gardez les médias circulant à travers Asterisk plutôt que de laisser les deux jambes se parler directement. Essentiel à travers un NAT, et requis de toute façon si vous souhaitez enregistrer, transcoder ou surveiller l'appel.
- **`rtp_symmetric=yes`** — le comportement classique *comedia* : renvoyez le RTP vers l'adresse d'où le média est réellement venu, et non vers l'adresse que le SDP prétend.
- **`force_rport=yes`** — répondez au SIP depuis l'IP/port source de la requête (RFC 3581), au lieu de faire confiance à l'en-tête `Via`.
- **`rewrite_contact=yes`** — sur les messages SIP entrants de cet endpoint, réécrivez l'en-tête `Contact` (ou un en-tête `Record-Route` approprié) vers l'IP source et le port d'où le paquet est réellement venu. Selon la documentation de l'option, cela « aide les serveurs à communiquer avec des endpoints qui sont derrière des NAT » et « aide à réutiliser des connexions de transport fiables telles que TCP et TLS ».

> **Recommandation — téléphones vs trunks.** `rewrite_contact` est presque toujours le bon choix pour les téléphones, car leur contact annoncé est généralement une adresse privée RFC 1918 qui n'est pas routable vers eux. Sur un trunk statique basé sur IP, le contact du fournisseur est généralement déjà une adresse publique correcte, donc le réécrire est souvent inutile ; certains opérateurs préfèrent le laisser désactivé là-bas et ne l'activer que pour les trunks d'enregistrement et les téléphones derrière NAT. L'effet documenté de l'option est purement la réécriture entrante `Contact`/`Record-Route` ci-dessus — la pratique sûre est donc de tester avec votre opérateur spécifique avant de l'activer sur un trunk statique.

Vous pouvez confirmer les paramètres effectifs sur n'importe quel endpoint avec `pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`, `rewrite_contact`, et le reste sont tous imprimés dans le vidage des paramètres.

## Lab — un ITSP fictif avec un second Asterisk et SIPp

Vous n'avez pas besoin d'un trunk payant pour pratiquer. Le laboratoire du livre exécute déjà un conteneur Asterisk 22.10.0 et un conteneur SIPp sur un réseau privé `172.30.0.0/24` ; nous traiterons le conteneur SIPp comme l'« opérateur » passant des appels entrants, et ajouterons un endpoint de trunk qui fait atterrir ces appels dans un contexte `from-pstn`.

![Un SIP trunk entre le PBX Asterisk et l'ITSP : le PBX s'enregistre comme un compte, les appels sortants composent `PJSIP/<num>@trunk`, et les appels entrants atterrissent dans le contexte `from-pstn`.](../images/09-sip-trunking-fig01.png)

### 1. Ajouter l'endpoint du trunk

Ajoutez un trunk basé sur IP à `lab/asterisk/etc/pjsip.conf` qui correspond à l'hôte SIPp du laboratoire et fait atterrir les appels entrants dans `from-pstn` :

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. Router le DID entrant

Dans `lab/asterisk/etc/extensions.conf`, ajoutez un contexte `from-pstn` qui répond au DID que l'opérateur fictif composera et le rejoue, puis ajoutez une règle sortante :

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

Rechargez les deux fichiers (`core reload`) et vérifiez que le trunk est chargé :

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Passer un appel entrant via le trunk

Pointez un scénario SIPp vers le PBX avec le DID comme utilisateur cible. Le laboratoire fournit déjà `lab/sipp/uac_9000.xml`, qui INVITE l'extension `9000` ; copiez-le vers `uac_did.xml` et changez l'utilisateur request-URI/`To` de `9000` à `4830001000`, puis exécutez-le depuis le conteneur SIPp :

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Regardez l'appel atteindre `from-pstn` sur la console Asterisk (`pjsip set logger on` montre l'INVITE entrant ; `core show channels` montre le canal `PJSIP/itsp-…` jouant `demo-congrats`). Parce que l'IP source SIPp correspond au `identify`, l'appel est accepté sans authentification — exactement comme se comporte un trunk d'opérateur statique.

### 4. Inspecter le trunk

Capturez la configuration complète du trunk pour vos notes :

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Extension) en faire un trunk d'enregistrement

Mettez en place le *second* conteneur Asterisk comme un vrai registraire : donnez-lui un `endpoint`+`auth`+`aor` pour le compte `4830001000`, puis sur le PBX, échangez le bloc `identify` pour le bloc `registration` du début de ce chapitre (pointant `server_uri` vers l'IP du second conteneur). Confirmez avec `pjsip show registrations` que le statut indique `Registered`, puis passez un appel dans chaque direction.

## Résumé

Un SIP trunk connecte votre PBX au monde extérieur, et dans PJSIP, c'est juste un endpoint construit à partir de la même famille `endpoint` + `auth` + `aor` que vous connaissez déjà, plus un `identify` ou un `registration`. Utilisez un **trunk d'enregistrement** (`type=registration` avec `outbound_auth`) lorsque le fournisseur vous donne un nom d'utilisateur et un mot de passe ; utilisez un **trunk basé sur IP** (`type=identify` avec `match`) lorsque l'authentification se fait par IP source — et verrouillez ce dernier avec un `match` étroit et une `acl`, car un trunk non authentifié est une cible de fraude téléphonique. En entrant, le DID du fournisseur arrive en tant que `${EXTEN}` dans votre contexte `from-pstn`, où vous le routez vers une extension, un IVR ou une file d'attente — les modèles et `${EXTEN:-N}` gardent les blocs DID compacts. En sortant, définissez `CALLERID(num)` sur un numéro que vous possédez, normalisez vers E.164 à un seul endroit et transmettez l'appel à `PJSIP/<number>@trunk`. Construisez la résilience en essayant plusieurs trunks et en bifurquant sur `${DIALSTATUS}` (`CHANUNAVAIL`/`CONGESTION` signifient rerouter ; `BUSY`/`NOANSWER` ne le font pas), et mettez le routage au moindre coût dans une table `GoSub`. Enfin, le NAT pour les trunks est bilatéral : `external_media_address`/`external_signaling_address`/`local_net` sur le **transport** pour votre adresse publique, et `direct_media=no`, `rtp_symmetric`, `force_rport` et `rewrite_contact` sur l'**endpoint** pour les médias du fournisseur.

## Quiz

1. Dans PJSIP, les identifiants utilisés pour authentifier un appel *sortant* ou un enregistrement auprès d'un fournisseur sont référencés avec :
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Vous devriez utiliser un trunk `type=registration` lorsque :
   - A. Le fournisseur vous identifie par votre adresse IP source.
   - B. Le fournisseur vous donne un nom d'utilisateur et un mot de passe et s'attend à ce que vous vous connectiez.
   - C. Vous ne voulez jamais qu'Asterisk envoie un `REGISTER`.
   - D. Le trunk est entre deux serveurs à IP statique que vous contrôlez.
3. L'option `match` de l'objet `identify` accepte (choisissez tout ce qui s'applique) :
   - A. Une adresse IP
   - B. Une plage CIDR
   - C. Un nom d'hôte (résolu au moment du chargement de la config)
   - D. Un nom d'utilisateur SIP uniquement
4. Sur Asterisk 22, `auth_type=userpass` est :
   - A. La seule valeur valide
   - B. Déprécié et converti en `digest`
   - C. Supprimé et provoque une erreur de chargement
   - D. Requis pour l'enregistrement sortant
5. Un numéro DID entrant arrive dans le dialplan en tant que :
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` dans le `context` de l'endpoint du trunk
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Pour envoyer les deux derniers chiffres du DID composé `4830003007` vers une extension, vous utiliseriez :
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Après `Dial()` vers un trunk, vous devriez basculer vers un trunk de secours sur quelles valeurs `${DIALSTATUS}` (choisissez deux) ?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Pour définir le numéro d'identifiant d'appelant présenté au fournisseur avant de composer, utilisez :
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Les options qui indiquent à Asterisk son adresse *publique* lorsque le serveur est derrière un NAT sont définies sur le :
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` sur un endpoint de trunk amène Asterisk à :
    - A. Chiffrer le RTP avec SRTP
    - B. Renvoyer le RTP vers l'adresse d'où le média est réellement arrivé, en ignorant le SDP
    - C. Désactiver complètement le RTP
    - D. Forcer le média direct entre les endpoints

**Réponses :** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
