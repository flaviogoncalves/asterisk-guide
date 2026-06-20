# SIP trunking, DID & the PSTN

Un PBX qui ne peut appeler que lui‑même n’est pas très utile. Tôt ou tard, chaque système doit atteindre le reste du monde — le réseau téléphonique commuté public (PSTN), un fournisseur SIP, ou un autre PBX. Le lien qui transporte ces appels est un **trunk**. À l’époque du TDM, un trunk était un circuit physique : un PRI T1/E1 ou un groupe de lignes analogiques FXO. Aujourd’hui, c’est presque toujours un **SIP trunk** — une connexion logique à un Internet Telephony Service Provider (ITSP) transportée sur le même réseau IP que tout le reste.

Ce chapitre montre comment connecter Asterisk 22 à un ITSP avec PJSIP, comment choisir entre un trunk basé sur l’enregistrement et un trunk basé sur l’IP, comment router les numéros DID entrants vers la bonne destination, comment émettre des appels sortants avec le bon identifiant d’appelant et le formatage E.164, et comment mettre en place un basculement et un routage au moindre coût sur plusieurs trunks. Nous terminons avec la gestion du NAT pour les trunks et un laboratoire qui déploie un second Asterisk (et SIPp) comme ITSP factice afin que vous puissiez passer de vrais appels à travers un trunk.

Tout ce qui est présenté ici a été vérifié avec le laboratoire Asterisk 22.10.0 du livre ; le modèle d’objet trunk est le même que celui introduit dans *Building your first PBX with PJSIP* et *SIP & PJSIP in depth*.

## Objectifs

By the end of this chapter, you should be able to:

- Connecter Asterisk 22 à un ITSP avec PJSIP
- Choisir entre des trunks basés sur l’enregistrement et des trunks basés sur l’IP (statiques)
- Diriger les DIDs entrants vers la bonne extension, IVR ou file d’attente
- Diriger les appels sortants avec le bon caller-ID et le formatage E.164
- Construire la bascule de trunk et le routage au moindre coût avec `${DIALSTATUS}`
- Gérer le NAT pour les trunks sur le transport et le endpoint

## What is a SIP trunk

A SIP trunk is a logical voice path between your PBX and another SIP system. In
practice that "other system" is one of two things:

- **An ITSP (Internet Telephony Service Provider).** A commercial carrier that
  sells you call origination and termination and, usually, a block of phone
  numbers (DIDs). You point Asterisk at the provider's signalling host, and the
  provider connects your calls to the wider PSTN. This is how most modern systems
  reach the phone network — no telephony hardware required.
- **A PSTN gateway.** A device (or another Asterisk) that has physical PSTN
  interfaces — a PRI card, analog FXO ports, or a GSM/4G gateway — and presents
  them to your PBX as SIP. The gateway does the TDM-to-SIP conversion; from
  Asterisk's point of view it is just another SIP trunk.

Either way, in PJSIP a trunk is **just an endpoint**. The same object family you
used for a phone — `endpoint`, `auth`, `aor`, optionally `identify` and
`registration` — builds a trunk. The differences are in the details: a trunk
authenticates *outbound* (you are the client, so credentials go in
`outbound_auth`, not `auth`), it usually does not register a user agent to you
(you register to *it*, or it sends you traffic from a known IP), and it lands
inbound calls in a dedicated context such as `from-pstn` instead of
`from-internal`.

> **Compared with the old TDM trunk.** A PRI gave you a fixed number of B-channels
> (23 on a T1, 30 on an E1) and signalled call setup over a dedicated D-channel
> (see the *Legacy channels* chapter). A SIP trunk has no fixed channel count —
> capacity is whatever your bandwidth, your provider's policy, and any
> `max_contacts`/concurrent-call limits allow. Caller-ID, DID, and call progress
> that used to ride ISDN information elements now ride SIP headers and SDP.

There are two ways an ITSP will agree to exchange traffic with you, and they
determine how you build the trunk: **registration-based** and **IP-based
(static)**. We cover each in turn.

## Trunks basés sur l’enregistrement

Un trunk basé sur l’enregistrement est le modèle utilisé lorsque le fournisseur s’attend à ce que *vous* vous connectiez à *lui*. Votre Asterisk envoie périodiquement un SIP `REGISTER` au fournisseur, s’authentifiant avec un nom d’utilisateur et un mot de passe, exactement comme un téléphone s’enregistre auprès de votre PBX. C’est courant lorsque votre adresse IP publique est dynamique, lorsque vous êtes derrière un NAT, ou lorsque le fournisseur identifie simplement les clients par leurs identifiants SIP plutôt que par l’adresse IP.

Dans PJSIP, la connexion sortante vit dans un objet dédié `registration`. Il remplace la ligne unique `register =>` que le pilote `chan_sip` supprimé utilisait dans `sip.conf`. Voici un trunk d’enregistrement complet vers un fournisseur fictif, suivant le modèle vérifié des chapitres précédents — notez `outbound_auth` (pas `auth`), `server_uri`/`client_uri` (pas `server`/`client`), `from_user`/`from_domain` sur le point de terminaison, et `dtmf_mode=rfc4733` :

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

Quelques points à remarquer :

- **`auth_type=digest`, pas `userpass`.** Les deux produisent la même authentification par digest, mais dans Asterisk 22 `userpass` (et l’ancien `md5`) sont **dépréciés et convertis silencieusement en `digest`**. Privilégiez `digest` dans les nouvelles configurations ; vous verrez encore `userpass` dans les fichiers plus anciens et dans les chapitres précédents de ce livre.
- **`outbound_auth` sur le point de terminaison et sur l’enregistrement.** L’enregistrement l’utilise pour authentifier le `REGISTER` ; le point de terminaison l’utilise pour répondre au `407 Proxy Authentication Required` que le fournisseur renvoie à un `INVITE` sortant. Ils peuvent partager un même objet `auth`.
- **`from_user` / `from_domain`.** De nombreux fournisseurs rejettent les appels dont l’en‑tête `From` ne porte pas votre numéro de compte et leur domaine. Ces deux options définissent exactement cela.
- **`contact_user=4830001000`.** Cela devient la partie utilisateur du `Contact` que vous enregistrez, de sorte que le fournisseur sache à quel numéro acheminer les appels entrants. C’est l’équivalent moderne du suffixe `/9999` sur l’ancienne ligne `register =>`.
- **`retry_interval=60`.** Si l’enregistrement échoue, réessayez toutes les 60 secondes.

Après un rechargement, confirmez l’enregistrement avec `pjsip show registrations`. Dans le laboratoire — où `itsp.example.com` ne répond pas réellement — le tableau apparaît ainsi :

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

Le suffixe `(exp. Ns)` compte à rebours les secondes jusqu’à la prochaine tentative ; une fois qu’il atteint zéro, il affiche brièvement `(exp. Ns ago)` avant que la nouvelle tentative ne se déclenche. Face à un fournisseur réel, la colonne `Status` indique `Registered` avec les secondes restantes jusqu’au prochain rafraîchissement. `Rejected` (ou `Unregistered`) signifie que le fournisseur n’a pas accepté la connexion — activez `pjsip set logger on` et lisez la réponse `401`/`403`, presque toujours un nom d’utilisateur, un mot de passe ou un domaine `client_uri` incorrect.

## Trunks IP (statiques)

Le deuxième modèle ne nécessite aucune inscription. Le fournisseur connaît votre adresse IP publique et envoie les appels directement à celle‑ci ; vous, à votre tour, envoyez les appels à l’adresse IP de signalisation connue du fournisseur. L’authentification se fait par **adresse IP source**, et non par des identifiants SIP. C’est le cas typique des trunks entre deux serveurs que vous contrôlez, ou d’un trunk d’entreprise où les deux côtés disposent d’adresses statiques.

L’objet clé est `identify`. Il indique à Asterisk : « toute requête SIP provenant de *cette* IP appartient à *cet* endpoint. » Sans cela, PJSIP tente d’associer une requête entrante à un endpoint via l’utilisateur `From`, ce qui ne correspondra pas au trafic d’un opérateur — ainsi l’appel serait rejeté ou redirigé vers l’endpoint `anonymous`.

Un trunk statique supprime l’objet `registration` et ajoute `identify` :

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

`match` accepte une adresse IP, une plage CIDR ou un nom d’hôte. **Les noms d’hôte sont résolus une fois, au moment du chargement de la configuration**, donc si l’IP de votre fournisseur change, vous devez recharger. Pour un opérateur qui publie plusieurs passerelles média, listez chaque IP de signalisation — vous pouvez répéter `match` ou fournir un CIDR :

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Vérifiez ce qu’Asterisk acceptera avec `pjsip show identifies`. Capturé depuis le laboratoire (la ligne `sipp-identify` est l’endpoint SIPp pré‑existant du laboratoire) :

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

### Implication de sécurité

Un trunk basé sur IP sans authentification est une porte, et `identify`/`match` en est le seul verrou. Si vous `match` une plage trop large — ou si un attaquant peut usurper une IP source — les appels atterrissent dans votre contexte `from-pstn` non authentifié. Deux défenses, utilisées conjointement :

- **Faire correspondre le plus précisément possible.** Privilégiez les IP d’hôte spécifiques aux CIDR larges. Seules les véritables IP de signalisation du fournisseur appartiennent à `match`.
- **L’associer à une ACL.** PJSIP peut bloquer le trafic au niveau SIP avant même qu’il n’atteigne un endpoint, en utilisant un objet `type=acl` (ou `acl.conf`) :

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Une section `type=acl` n’a pas besoin de référence : `res_pjsip_acl` applique chaque tel objet à *tout* le trafic SIP entrant avant qu’il n’atteigne un endpoint. (Les options `acl` et `contact_acl` sur l’objet tirent des listes de règles nommées depuis `acl.conf` au lieu d’énumérer `permit`/`deny` en ligne comme ci‑dessus.) Le principe est le même que dans le chapitre SIP : refuser tout, puis autoriser uniquement ce en quoi vous avez confiance. Et quoi que fasse votre contexte de trunk,
**ne le laissez jamais atteindre un contexte qui peut rappeler la PSTN** sans une règle délibérée et authentifiée — c’est le trou classique de fraude de péage.

> **Quel modèle dois‑je utiliser ?** Si le fournisseur vous fournit un nom d’utilisateur et un mot de passe,
> utilisez un trunk **d’enregistrement**. S’il vous demande votre adresse IP et vous donne la sienne, utilisez un trunk **identify**. Certains fournisseurs supportent les deux ; de nombreux trunks réels combinent un enregistrement (pour que le fournisseur puisse vous localiser) avec un identify (pour que les INVITE entrants des passerelles média du fournisseur soient associés même lorsqu’ils proviennent d’une IP autre que celle du registre).

## Routage entrant et gestion des DID

Une fois les appels entrants arrivés, ils atterrissent dans le `context` de l'endpoint — ici
`from-pstn`. Un **DID** (numéro de numérotation directe entrante) est simplement le numéro composé
que le fournisseur vous transmet dans l'URI de requête. Votre tâche dans le dialplan est de mapper chaque
DID à une destination : une extension unique, un IVR, une file d’attente ou un groupe de sonnerie.

Le numéro que le fournisseur envoie est comparé comme `${EXTEN}` dans `from-pstn`. La quantité que
vous voyez dépend du fournisseur — certains envoient le numéro complet au format E.164
(`+4830001000`), d’autres envoient le numéro national, d’autres n’envoient que les derniers chiffres.
Inspectez un appel entrant réel avec `pjsip set logger on` et examinez l'URI de requête avant d'écrire les modèles.

### Un DID vers une extension

Le cas le plus simple — un seul DID routé directement vers un téléphone :

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### Un DID vers un IVR (standard automatique)

Un numéro principal qui doit répondre par un menu au lieu de sonner un téléphone :

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` est le contexte du standard automatique que vous avez construit dans les chapitres du dialplan
(`Background()` + `WaitExten()`). Le routage du DID n’est qu’un `Goto`.

### Un DID vers une file d’attente

Une ligne de support qui doit atterrir dans une file d’attente d’appels :

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Plusieurs DID à la fois

Lorsque vous achetez un bloc de numéros, un modèle permet de garder le dialplan petit. Supposons que
votre plage de DID soit `4830003000`–`4830003099` et que le fournisseur envoie le numéro complet ; mappez
les deux derniers chiffres de chaque DID vers l’extension `60xx` :

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` prend les deux derniers chiffres (un décalage négatif compte depuis la droite),
ainsi `4830003007` sonne `PJSIP/6007`. Un tableau de correspondance `did => extension` construit avec
`GoSub` ou une base de données Asterisk (`AstDB`/`func_odbc`) permet de monter en échelle davantage, mais pour
une poignée de numéros, les modèles explicites restent les plus clairs.

> **Capturez le DID non correspondant.** Ajoutez une extension `i` (invalid) à `from-pstn` afin qu’un
> numéro entrant mal routé joue une annonce ou sonne l’opérateur au lieu d’être simplement abandonné :
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Routage sortant, identifiant d’appelant et E.164

Les appels sortants circulent dans l’autre sens : un téléphone interne compose un numéro, votre dialplan le fait correspondre, supprime tout préfixe d’accès, définit l’identifiant d’appelant que le fournisseur attend, et transmet l’appel au point de terminaison du trunk avec `Dial(PJSIP/<number>@itsp)`.

### Envoi de l’appel au trunk

La syntaxe du canal pour un trunk est `PJSIP/<number>@<endpoint>` : la partie avant le `@` devient la portion utilisateur de l’URI de requête sortante, et la partie après le `@` indique le point de terminaison dont le `aor` `contact` fournit l’hôte de destination. Une règle classique « composer 9 pour une ligne extérieure » :

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` supprime le code d’accès `9` initial avant que le numéro ne soit envoyé. Le motif `_9NXXXXXXXXX` correspond à `9` plus un numéro à 10 chiffres dont le premier chiffre est 2–9 ; adaptez‑le à votre plan de numérotation.

### Identifiant d’appelant sur les appels sortants

La plupart des ITSP ignorent — ou rejettent activement — un identifiant d’appelant qui n’est pas un numéro que vous possédez. Définissez le numéro d’identifiant d’appelant sortant sur l’un de vos DID avec la fonction `CALLERID(num)` avant `Dial()`, comme indiqué ci‑dessus. Vous pouvez également définir le nom :

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Si le fournisseur supprime toujours ou remplace le nom de votre identifiant d’appelant, c’est sa politique — de nombreux opérateurs tirent le nom affiché de leur propre base de données CNAM indexée sur le numéro, et non de votre en‑tête `From`.

Deux options de point de terminaison interagissent avec cela :

- **`from_user`** définit la partie utilisateur de l’en‑tête `From` au niveau SIP, que certains fournisseurs utilisent pour identifier votre compte quel que soit `CALLERID(num)`.
- **`trust_id_outbound`** (par défaut `no`) contrôle si Asterisk enverra les en‑têtes d’identité sensibles à la vie privée (`P-Asserted-Identity`/`P-Preferred-Identity`) en sortie. Laissez‑les désactivés sauf si votre fournisseur indique qu’il veut le PAI, auquel cas définissez `trust_id_outbound=yes` et `send_pai=yes`.

### Normalisation vers E.164

E.164 est le format de numéro international : un + initial `+`, le code pays, puis le numéro national, sans espaces ni ponctuation (par exemple `+5548999990000` ou `+14155550100`). Les opérateurs attendent de plus en plus — voire exigent — le format E.164 sur le trunk. Plutôt que de disperser le formatage dans le dialplan, normalisez‑le une fois dans le contexte sortant.

Un exemple nord‑américain qui accepte un numéro local à 10 chiffres, un numéro préfixé de 11 chiffres avec `1`, ou un numéro déjà au format E.164, et qui présente toujours `+1…` au trunk :

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

Certains fournisseurs veulent le `+` ; d’autres veulent les chiffres bruts. Si le vôtre rejette le `+`, supprimez‑le à la sortie avec `${EXTEN:1}` dans le `Dial`. L’idée est que toute la connaissance du format réside en un seul endroit, de sorte que changer de fournisseur — ou en ajouter un second — ne nécessite qu’une modification d’une ligne.

## Failover et routage au moindre coût

Avec un seul trunk, une panne du fournisseur signifie aucune appel sortant. Avec deux ou plus, vous pouvez basculer automatiquement et même choisir la route la moins chère par destination — *least-cost routing* (LCR).

### Failover avec `${DIALSTATUS}`

`Dial()` définit la variable de canal `${DIALSTATUS}` lorsqu’il renvoie. Les valeurs qui vous intéressent pour le basculement sont `CHANUNAVAIL` (le trunk n’a pas pu être atteint du tout) et `CONGESTION` (l’appel a été rejeté, par ex. toutes les voies occupées). Essayez le trunk principal ; s’il ne peut pas prendre l’appel, passez au trunk de secours :

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Notez le choix délibéré **de ne pas** basculer sur `BUSY` ou `NOANSWER` — ceux‑ci signifient que le *called party* a été atteint et a décliné, donc réessayer sur un autre trunk ferait sonner à nouveau un téléphone qui a déjà dit non (et pourrait vous coûter un second appel). Ne re‑acheminez que lorsque le *trunk lui‑même* a échoué.

### Une sous‑routine de routage réutilisable

Répéter cette logique pour chaque motif de numérotation est source d’erreurs. Factorisez‑la dans une routine `GoSub` qui prend le numéro de destination et essaie chaque trunk dans l’ordre :

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

Désormais chaque motif sortant n’est qu’un appel `GoSub`, et l’ordre des trunks est défini en un seul endroit.

### Routage au moindre coût par destination

Le vrai LCR choisit le trunk en fonction de la destination de l’appel. Une forme courante consiste à faire correspondre le préfixe de destination et à envoyer chaque classe d’appel au fournisseur le moins cher pour celle‑ci — par exemple, les appels internationaux vers un transporteur de gros et les appels locaux/nationaux vers votre trunk principal :

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

Pour plus que quelques préfixes, stockez la table de routage dans une base de données (`func_odbc`/`AstDB`) et recherchez le trunk par préfixe au lieu de coder en dur les motifs. Le dialplan reste petit et les tarifs vivent dans une table que vous pouvez modifier sans recharger la logique.

## NAT et trunks

NAT est la cause la plus fréquente de problèmes de trunk — typiquement un audio à sens unique,
ou un trunk qui s’enregistre mais ne reçoit jamais d’appels entrants. La cause est la même
que pour les téléphones (voir *SIP & PJSIP in depth* et *Designing a VoIP network*) :
Asterisk annonce sa propre idée de son adresse dans SIP et SDP, et derrière NAT
c’est une adresse privée RFC 1918 que le fournisseur ne peut pas router en retour.

Pour les trunks, la solution comporte deux parties — paramètres sur le **transport** (votre adresse
publique) et paramètres sur le **endpoint** (comment traiter les médias du fournisseur).

### Sur le transport — votre adresse publique

Lorsque le serveur Asterisk lui‑même se trouve derrière NAT (un serveur cloud ou sur site avec une
IP privée et une IP publique 1:1), indiquez au transport son adresse publique et quels
réseaux sont locaux. Ces options sont définies une fois, sur le `transport`, et s’appliquent à
tout le trafic qui le traverse :

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

- **`external_signaling_address`** — l’IP publique qu’Asterisk écrit dans les en‑têtes SIP
  (`Via`, `Contact`) pour les destinations hors `local_net`.
- **`external_media_address`** — l’IP publique qu’Asterisk écrit dans la ligne SDP `c=`
  afin que le RTP revienne au bon endroit. Généralement identique à l’adresse de signalisation.
- **`local_net`** — réseaux qu’Asterisk considère comme internes, de sorte qu’il ne réécrive *pas*
  les adresses pour les pairs LAN. Listez chaque sous‑réseau interne.

### Sur l’endpoint — les médias du fournisseur

L’autre moitié gère un fournisseur qui lui‑même se trouve derrière NAT, ou qui envoie simplement
des médias depuis une adresse différente de celle indiquée dans son SDP. Définissez ces paramètres
par endpoint de trunk :

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

- **`direct_media=no`** — garder les médias qui transitent par Asterisk plutôt que de laisser
  les deux jambes communiquer directement. Essentiel derrière NAT, et nécessaire de toute façon
  si vous voulez enregistrer, transcoder ou surveiller l’appel.
- **`rtp_symmetric=yes`** — le comportement classique *comedia* : renvoyer le RTP à l’adresse
  d’où les médias proviennent réellement, et non à l’adresse réclamée par le SDP.
- **`force_rport=yes`** — répondre au SIP depuis l’IP/port source de la requête
  (RFC 3581), au lieu de faire confiance à l’en‑tête `Via`.
- **`rewrite_contact=yes`** — sur les messages SIP entrants de cet endpoint, réécrire
  l’en‑tête `Contact` (ou un en‑tête `Record-Route` approprié) avec l’adresse IP source
  et le port dont le paquet provient réellement. Selon la documentation de l’option,
  cela « aide les serveurs à communiquer avec des endpoints qui sont derrière
  des NAT » et « aide à réutiliser des connexions de transport fiables telles que TCP et TLS. »

> **Recommandation — téléphones vs trunks.** `rewrite_contact` est presque toujours le
> bon choix pour les téléphones, car leur contact annoncé est généralement une adresse
> privée RFC 1918 qui n’est pas routable vers eux. Sur un trunk basé sur une IP statique,
> le contact du fournisseur est habituellement déjà une adresse publique correcte, donc le réécrire
> est souvent inutile ; certains opérateurs préfèrent le désactiver là et ne l’activer
> que pour les trunks d’enregistrement et les téléphones NATés. L’effet documenté de l’option
> est purement la réécriture inbound `Contact`/`Record-Route` ci‑dessus — ainsi la
> pratique sûre est de tester avec votre opérateur spécifique avant de l’activer sur un
> trunk statique.

Vous pouvez confirmer les paramètres effectifs sur n’importe quel endpoint avec
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, et le reste est affiché dans le dump des paramètres.

## Lab — a mock ITSP with a second Asterisk and SIPp

Vous n’avez pas besoin d’un trunk payant pour vous entraîner. Le laboratoire du livre exécute déjà un conteneur Asterisk
22.10.0 et un conteneur SIPp sur un réseau privé `172.30.0.0/24` ; nous
traiterons le conteneur SIPp comme le « transporteur » qui passe des appels entrants, et ajouterons un
endpoint trunk qui fait atterrir ces appels dans un contexte `from-pstn`.

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

Ajoutez un trunk basé sur IP à `lab/asterisk/etc/pjsip.conf` qui correspond à l’hôte SIPp du laboratoire
et fait atterrir les appels entrants dans `from-pstn` :

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

### 2. Route the inbound DID

Dans `lab/asterisk/etc/extensions.conf`, ajoutez un contexte `from-pstn` qui répond au
DID que le transporteur factice composera et le lit en retour, puis ajoutez une règle sortante :

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

Rechargez les deux fichiers (`core reload`) et vérifiez que le trunk a été chargé :

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

Pointez un scénario SIPp vers le PBX avec le DID comme utilisateur cible. Le laboratoire fournit déjà
`lab/sipp/uac_9000.xml`, qui INVITE l’extension `9000` ; copiez‑le vers
`uac_did.xml` et modifiez le request‑URI/​`To` utilisateur de `9000` à `4830001000`,
puis exécutez‑le depuis le conteneur SIPp :

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Observez l’appel atteindre `from-pstn` sur la console Asterisk (`pjsip set logger on`
affiche l’INVITE entrant ; `core show channels` montre le canal `PJSIP/itsp-…`
lisant `demo-congrats`). Comme l’adresse IP source de SIPp correspond au `identify`, l’appel est accepté sans authentification — exactement comme un trunk de transporteur statique se comporte.

### 4. Inspect the trunk

Capturez la configuration complète du trunk pour vos notes :

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

Déployez le *second* conteneur Asterisk comme un véritable registraire : donnez‑lui un
`endpoint`+`auth`+`aor` pour le compte `4830001000`, puis sur le PBX remplacez le
bloc `identify` par le bloc `registration` du début de ce chapitre
(pointant `server_uri` vers l’adresse IP du second conteneur). Confirmez avec
`pjsip show registrations` que le statut indique `Registered`, puis passez un appel
dans chaque direction.

## Summary

A SIP trunk connects your PBX to the outside world, and in PJSIP it is just an
endpoint built from the same `endpoint` + `auth` + `aor` family you already know,
plus an `identify` or a `registration`. Use a **registration trunk**
(`type=registration` with `outbound_auth`) when the provider gives you a username
and password; use an **IP-based trunk** (`type=identify` with `match`) when
authentication is by source IP — and lock the latter down with a narrow `match`
and an `acl`, because an unauthenticated trunk is a toll-fraud target. Inbound,
the provider's DID arrives as `${EXTEN}` in your `from-pstn` context, where you
route it to an extension, an IVR, or a queue — patterns and `${EXTEN:-N}` keep
DID blocks compact. Outbound, set `CALLERID(num)` to a number you own, normalize
to E.164 in one place, and hand the call to `PJSIP/<number>@trunk`. Build
resilience by trying multiple trunks and branching on `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` mean re-route; `BUSY`/`NOANSWER` do not), and put
least-cost routing in a `GoSub` table. Finally, NAT for trunks is two-sided:
`external_media_address`/`external_signaling_address`/`local_net` on the
**transport** for your public address, and `direct_media=no`, `rtp_symmetric`,
`force_rport`, and `rewrite_contact` on the **endpoint** for the provider's media.

## Quiz

1. Dans PJSIP, les informations d’identification utilisées pour authentifier un appel *sortant* ou
   l’enregistrement auprès d’un fournisseur sont référencées avec :
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Vous devez utiliser un trunk `type=registration` lorsque :
   - A. Le fournisseur vous identifie par votre adresse IP source.
   - B. Le fournisseur vous fournit un nom d’utilisateur et un mot de passe et attend que vous vous connectiez.
   - C. Vous ne voulez jamais qu’Asterisk envoie un `REGISTER`.
   - D. Le trunk se trouve entre deux serveurs à IP statique que vous contrôlez.
3. L’option `match` de l’objet `identify` accepte (choisissez tout ce qui s’applique) :
   - A. Une adresse IP
   - B. Une plage CIDR
   - C. Un nom d’hôte (résolu au moment du chargement de la configuration)
   - D. Un nom d’utilisateur SIP uniquement
4. Sur Asterisk 22, `auth_type=userpass` est :
   - A. La seule valeur valide
   - B. Obsolète et converti en `digest`
   - C. Supprimé et provoque une erreur de chargement
   - D. Obligatoire pour l’enregistrement sortant
5. Un numéro DID entrant arrive dans le dialplan sous la forme :
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` dans le `context` du trunk endpoint
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Pour envoyer les deux derniers chiffres du DID composé `4830003007` à une extension,
   vous devez utiliser :
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Après `Dial()` vers un trunk, vous devez basculer vers un trunk de secours sur lequel
   les valeurs `${DIALSTATUS}` (choisissez deux) ?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Pour définir le numéro d’identification de l’appelant présenté au fournisseur avant de composer, utilisez :
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Les options qui indiquent à Asterisk son adresse *publique* lorsque le serveur est derrière
   NAT sont définies sur le :
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` sur un trunk endpoint fait que Asterisk :
    - A. Chiffre le RTP avec SRTP
    - B. Renvoie le RTP à l’adresse d’où le média est réellement arrivé, en ignorant le SDP
    - C. Désactive complètement le RTP
    - D. Force le média direct entre les points d’extrémité

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
