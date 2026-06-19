# Migrer de chan_sip vers PJSIP : un guide pratique

Si vous lisez ceci avec un serveur Asterisk 13, 16 ou 18 toujours en production,
vous avez une échéance. `chan_sip` — le pilote de canal SIP original configuré
via `sip.conf` — a été **déprécié dans Asterisk 17, retiré de la compilation par
défaut dans Asterisk 19, et entièrement supprimé dans Asterisk 21**. Il n'existe pas dans
Asterisk 22 LTS. Il n'existe aucun drapeau pour le réactiver, aucun `noload` pour l'éviter, aucun
paquet à installer. Le seul pilote de canal SIP dans Asterisk 22 est **PJSIP**
(`res_pjsip` plus `chan_pjsip`), configuré via `pjsip.conf`.

Ainsi, une mise à niveau vers Asterisk 22 est, pour la plupart des sites, un *projet de migration SIP* autant
qu'une montée de version. La bonne nouvelle est que le protocole sur le réseau ne change pas
— un téléphone qui s'enregistrait et appelait hier s'enregistrera et appellera demain —
et Asterisk fournit un outil de conversion pour effectuer les 80 % initiaux de la traduction pour
vous. Ce chapitre est un guide pratique : la correspondance des concepts, le script de conversion, les traductions
côte à côte `sip.conf` → `pjsip.conf` pour les cas que vous avez réellement, les changements dans le dialplan et la CLI qui accompagnent ce passage, la migration realtime (base de données), ainsi qu'une liste de contrôle et les pièges à éviter.

Tout ce qui est présenté ici est vérifié par rapport au laboratoire Asterisk 22.10.0 du livre. Le matériel historique approfondi sur `chan_sip` lui-même — ainsi qu'une conversion complète de bout en bout d'un `sip.conf` multi-périphérique — se trouve dans le chapitre *Legacy channels* ; ce chapitre est le compagnon ciblé, sous forme de recettes, de ce dernier.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Expliquer pourquoi `chan_sip` a disparu dans Asterisk 22 et ce qui le remplace
- Mapper le modèle pair/user/friend de `sip.conf` sur le modèle d'objet PJSIP
  (endpoint + aor + auth + identify + transport + registration)
- Exécuter le script de conversion `sip_to_pjsip.py` et examiner son résultat de manière critique
- Traduire manuellement les types de périphériques courants (téléphone avec enregistrement, trunk entrant,
  enregistrement sortant) de `sip.conf` vers `pjsip.conf`
- Migrer les paramètres NAT, média, DTMF, codec et authentification option par option
- Mettre à jour le dialplan (`SIP/` → `PJSIP/`) et la CLI (`sip show` → `pjsip show`)
- Migrer un déploiement realtime/ARA de `sippeers`/`sipregs` vers les tables Sorcery
  `ps_*`
- Suivre une liste de contrôle de migration et éviter les pièges classiques

## Pourquoi migrer

`chan_sip` a servi Asterisk pendant près de deux décennies, mais il portait une
dette architecturale : un module monolithique, un seul bloc de configuration par périphérique, un support multi-transport limité, et une pile SIP qui avait pris du retard sur les RFC.
**PJSIP** — construit sur la pile mature pjproject de Teluu et introduit dans Asterisk 12
— a été le remplacement complet. Avec Asterisk 21, le projet Asterisk a terminé le
travail et a supprimé `chan_sip` de l'arborescence.

Vous pouvez confirmer la situation sur n'importe quel système Asterisk 22 :

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` renvoie *0 modules loaded* — il n'est tout simplement plus là. Il n'y a rien
vers quoi migrer *à part* PJSIP, donc la seule vraie question est *comment*, et non *si*.

## La correspondance conceptuelle : il n'y a pas de "peer" unique

Le changement de mentalité qui piège tous ceux venant de `sip.conf` est le suivant : **PJSIP
n'a pas de `[peer]`.** Dans `sip.conf`, un bloc entre crochets — un `peer`, un `user` ou un
`friend` — décrivait *tout* à propos d'un périphérique : ses identifiants, où le joindre, ses codecs, son comportement NAT, son contexte de dialplan. PJSIP divise délibérément ce bloc unique en plusieurs objets plus petits et spécialisés, chacun étiqueté avec un `type=`, qui *se référencent mutuellement par leur nom* :

| Objet PJSIP (`type=`) | Responsabilité |
| --- | --- |
| `endpoint` | L'identité de gestion d'appel du périphérique : codecs, contexte, DTMF, média, NAT, et références à ses `auth`/`aors`/`transport` |
| `aor` (Address of Record) | *Où* joindre le périphérique — contacts enregistrés ou statiques, `max_contacts`, qualify |
| `auth` | Identifiants (nom d'utilisateur/mot de passe) pour l'authentification entrante et/ou sortante |
| `identify` | Faire correspondre une requête entrante à un endpoint par **IP source** au lieu de l'utilisateur `From` |
| `transport` | Le(s) socket(s) d'écoute : protocole, adresse/port de liaison, adresses NAT/externes |
| `registration` | Un REGISTER **sortant** d'Asterisk vers un fournisseur |

La distinction `friend`/`peer`/`user` disparaît entièrement — dans PJSIP, tout
est un `endpoint`. Un seul friend `sip.conf` devient donc, typiquement, trois
objets (`endpoint` + `auth` + `aor`) qui partagent un nom et pointent les uns vers les autres :

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

L'endpoint est le ciment. Il nomme un `transport` (ou hérite du défaut), un
objet `auth`, et un ou plusieurs `aors`. Le modèle d'objet est couvert en profondeur dans
*SIP & PJSIP in depth* ; ici, nous en avons juste besoin comme cible de chaque traduction.

## L'outil de conversion `sip_to_pjsip.py`

Asterisk fournit un script Python qui lit un `sip.conf` existant et écrit un
`pjsip.conf`. Il ne s'exécute pas comme une commande CLI — il réside dans l'**arborescence source
d'Asterisk**, pas dans les binaires installés :

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Sur l'Asterisk 22.10.0 du laboratoire, le chemin complet est, par exemple,
`/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`. Le même
répertoire contient `sip_to_pjsql.py` (la variante realtime/SQL, couverte plus tard) et
les modules d'assistance `astconfigparser.py`, `astdicts.py` et `sqlconfigparser.py`.

### Exécution

Le script prend des arguments positionnels optionnels — `[input-file [output-file]]` —
par défaut `sip.conf` et `pjsip.conf` dans le répertoire courant :

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Ses seules options réelles sont :

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

Il lit l'entrée, affiche `Converting to PJSIP...` et écrit le fichier de sortie.
En interne, il parcourt chaque section `sip.conf` et, par périphérique, émet les objets
`endpoint`, `auth`, `aor`, `registration` et (là où il peut les déduire)
`transport` correspondants, en appliquant automatiquement les mappages d'options de la section suivante.

### Ce qu'il fait — et ses limites

Considérez le résultat comme un **premier brouillon, pas un fichier final.** Le script est honnête
sur ses propres lacunes : tout ce qu'il ne peut pas mapper proprement est écrit dans un bloc clairement délimité en haut du fichier de sortie :

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[softphone]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

Remarquez dans ce fragment réel que `qualify = yes` provenant d'un pair `sip.conf` a atterri dans
le bloc *non-mapped* — parce que PJSIP qualifie sur l'**aor** avec
`qualify_frequency` (secondes), et non un booléen sur le périphérique, le script vous laisse le soin de le définir délibérément. Les limitations pratiques à prévoir :

- **Les transports sont devinés, pas conçus.** Le script émet un `transport-udp` de base
  à partir de `bindport`/`bindaddr`, mais il ne peut pas connaître vos certificats TLS,
  vos besoins TCP ou votre configuration multi-liaison. Examinez et réécrivez le transport.
- **Le NAT et les adresses externes nécessitent une intervention humaine.** `externaddr`/`localnet` peuvent ne pas
  survivre proprement ; confirmez `external_media_address`, `external_signaling_address`
  et `local_net` sur le transport manuellement.
- **`qualify`, les minuteurs personnalisés et une poignée d'options atterrissent dans "non-mapped".**
  Lisez ce bloc de haut en bas et décidez pour chacun.
- **Les listes de codecs, les contextes et la sécurité nécessitent une révision.** Vérifiez `disallow`/`allow`,
  le dialplan `context`, et assurez-vous qu'aucun périphérique n'est laissé ouvert par inadvertance.

Le flux de travail est donc : exécutez le script dans un fichier *temporaire*, comparez et examinez
le résultat, intégrez les bonnes parties dans votre vrai `pjsip.conf`, puis testez exhaustivement avant la mise en production.

## Traductions côte à côte

Voici les recettes. `sip.conf` à gauche, l'équivalent vérifié `pjsip.conf`
à droite (empilé ici pour la largeur de page). Chaque nom d'option et valeur
à droite a été vérifié par rapport au laboratoire Asterisk 22 avec
`config show help res_pjsip ...`.

### Un téléphone avec enregistrement (`host=dynamic`)

Le périphérique le plus courant : un téléphone de bureau ou un softphone qui se connecte avec un secret et enregistre sa propre position.

**Legacy `sip.conf` :**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf` :**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

Actions clés : `host=dynamic` devient un `aor` avec `max_contacts` (le périphérique
s'enregistre pour remplir son contact) ; `secret=` devient `password=` à l'intérieur d'un
`type=auth` ; `qualify=yes` devient `qualify_frequency=60` (secondes) sur l'**aor**, pas l'endpoint. Ne définissez `max_contacts` au-dessus de 1 que si vous voulez vraiment le même compte sur plusieurs périphériques à la fois.

### Un trunk entrant (`host=<ip>` / `type=peer`)

Un fournisseur qui vous envoie des appels depuis une adresse IP connue. Il n'y a pas d'enregistrement
ici — vous authentifiez le *trafic de l'opérateur par son IP source* en utilisant `identify`.

**Legacy `sip.conf` :**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf` :**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

La traduction cruciale est **`insecure=invite` → `identify`**. Dans `chan_sip`,
`insecure=invite` disait à Asterisk "ne conteste pas les INVITE entrants de ce pair
pour l'authentification." PJSIP obtient le même effet en *faisant correspondre l'IP source à
l'endpoint* avec `type=identify`/`match=`, ce qui est à la fois plus explicite et plus
sécurisé. Le `host=` statique devient un `contact=` permanent sur l'`aor` afin que vous puissiez également appeler *vers* l'opérateur. `match=` accepte une IP, une plage CIDR ou un nom d'hôte (résolu au moment du chargement de la configuration — rechargez si l'IP du fournisseur change).

### Un enregistrement sortant (`register =>`)

Lorsque le fournisseur veut que *vous* vous connectiez à *eux*, `chan_sip` utilisait une seule
ligne `register =>` dans `[general]`. PJSIP la remplace par un objet dédié
`type=registration` plus un `outbound_auth`.

**Legacy `sip.conf` :**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf` :**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

Mappez les champs `register =>` un par un : les identifiants `1020:supersecret` deviennent
l'objet `auth` (référencé comme `outbound_auth`) ; `@sip.example.com:5600` devient
le `server_uri` ; le suffixe `/9999` — la partie utilisateur vers laquelle le fournisseur livre les appels entrants — devient `contact_user=9999`. `defaultuser`/`fromuser` et `fromdomain`
deviennent `from_user` et `from_domain` sur l'endpoint. Notez que `outbound_auth` apparaît
*deux fois* : l'enregistrement l'utilise pour le REGISTER, l'endpoint l'utilise pour répondre au
défi `407` sur les INVITE sortants.

## Référence de migration option par option

Lorsque vous traduisez manuellement (ou auditez le résultat du script), ce tableau est
la référence. Chaque nom d'option PJSIP et son emplacement (endpoint / aor / auth /
transport) est vérifié par rapport au laboratoire Asterisk 22.

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | Emplacement |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (le périphérique s'enregistre) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (méthode d'auth) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (même syntaxe) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | omettre auth ; utiliser `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### Une note sur `secret` → `auth` et `auth_type`

Le `secret=` de `chan_sip` devient le champ `password=` d'un objet `type=auth`. La
**méthode d'authentification** est définie avec `auth_type`. Utilisez `auth_type=digest`. Les
valeurs plus anciennes `userpass` et `md5` fonctionnent toujours mais sont **dépréciées et silencieusement converties en `digest`** — vérifié directement depuis le laboratoire :

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

Vous verrez `auth_type=userpass` dans les anciennes configurations et dans le résultat du script de conversion (et dans les chapitres précédents de ce livre). C'est inoffensif, mais écrivez `digest` dans tout ce qui est nouveau.

### NAT, média et DTMF en détail

Ces trois éléments sont la source de la plupart des tickets post-migration du type "ça s'enregistre mais il n'y a pas d'audio". Le raccourci `chan_sip` `nat=force_rport,comedia` regroupait trois comportements en une seule option ; PJSIP les sépare pour que vous puissiez raisonner sur chacun :

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

Pour le **média**, `directmedia` devient `direct_media` (le soulignement est tout le changement) ; gardez `direct_media=no` chaque fois que l'appel doit être ancré sur Asterisk — à travers un NAT, ou pour enregistrer/transcoder/transférer. Pour le **DTMF**, la RFC a été renumérotée : le `dtmfmode=rfc2833` de `chan_sip` est le `dtmf_mode=rfc4733` de PJSIP (même mécanisme d'événement téléphonique hors bande, numéro de RFC actuel). Le laboratoire confirme que les valeurs valides `dtmf_mode` sont `rfc4733`, `inband`, `info`, `auto` et `auto_info`, avec `rfc4733` par défaut.

Pour les **codecs**, rien ne change : `disallow=all` suivi de `allow=ulaw` (etc.)
utilise la syntaxe identique sur l'endpoint PJSIP.

## Changements dans le dialplan et la CLI

La migration ne s'arrête pas à `pjsip.conf`. Deux choses changent dans l'utilisation quotidienne.

### Chaînes de canal : `SIP/` → `PJSIP/`

Chaque `Dial()` et référence de canal dans `extensions.conf` qui nommait l'ancienne
technologie doit être mis à jour :

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Les chaînes de numérotation des trunks suivent le même modèle — `Dial(SIP/${EXTEN}@itsp)` devient
`Dial(PJSIP/${EXTEN}@itsp)`. PJSIP ajoute également la fonction `PJSIP_DIAL_CONTACTS()`
pour appeler tous les contacts liés à un AOR à la fois, ainsi que les fonctions de dialplan `PJSIP_HEADER()` /
`PJSIP_MEDIA_OFFER()` ; grep votre dialplan pour les références SIP `SIP/`,
`SIPPEER`, `SIPCHANINFO` et `CHANNEL(...)` et traduisez chacune.

### CLI : `sip show ...` → `pjsip show ...`

L'arborescence complète des commandes `sip ...` disparaît avec le pilote. Les remplacements :

| Commande `chan_sip` | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (ou `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (ou `core reload`) |

Les anciennes commandes ne se comportent pas seulement différemment — elles n'existent plus. Sur le
laboratoire, `sip show peers` renvoie *No such command*, tandis que `pjsip show endpoints`,
`pjsip show aors`, `pjsip show auths`, `pjsip show contacts`,
`pjsip show registrations` et `pjsip show identifies` sont toutes présentes. La commande de dépannage la plus
utile — l'enregistreur de paquets SIP qui imprimait chaque message avec `sip set debug` — est maintenant **`pjsip set logger on`** (avec `pjsip set logger host <ip>` pour se concentrer sur un pair).

## Migration Realtime (ARA)

Si vous exécutiez `chan_sip` depuis une base de données (Asterisk Realtime Architecture), vos
périphériques résidaient dans la table `sippeers` et les enregistrements dans `sipregs`. PJSIP utilise une
couche de stockage complètement différente — **Sorcery** — avec une table *par type d'objet*. Le mappage :

| Table realtime `chan_sip` | Table(s) PJSIP / Sorcery |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (une ligne chacune, séparées) |
| `sipregs` | `ps_contacts` (enregistrements dynamiques) |
| — (`register=>` sortant) | `ps_registrations` |
| — (correspondance IP) | `ps_endpoint_id_ips` (les objets `identify`) |
| — (alias de domaine) | `ps_domain_aliases` |

La séparation conceptuelle est la même que pour le cas des fichiers plats : une ligne `sippeers` devient
*trois* lignes dans trois tables (`ps_endpoints` + `ps_aors` + `ps_auths`) qui
se référencent mutuellement par le nom de l'endpoint.

Deux choses rendent cela réalisable :

- **Le schéma est généré pour vous.** Asterisk fournit des migrations Alembic sous
  `contrib/ast-db-manage/` qui créent chaque table `ps_*`. Exécutez
  `alembic upgrade head` sur la base de données `config` pour construire le schéma PJSIP actuel
  plutôt que d'écrire le DDL à la main.
- **Il existe un script de conversion SQL.** À côté de `sip_to_pjsip.py` se trouve
  **`sip_to_pjsql.py`** dans le même répertoire `contrib/scripts/sip_to_pjsip/` ; il
  réutilise la même logique `convert()` mais émet un fichier `pjsip.sql` d'instructions `INSERT`
  pour les tables `ps_*` au lieu d'un fichier de configuration plat. Comme pour l'outil de fichier plat, examinez le résultat avant de le charger.

Enfin, pointez `sorcery.conf` vers votre base de données afin que PJSIP lise les endpoints, aors,
auths et contacts depuis les tables `ps_*` (via `res_config_odbc` /
`res_pjsip_realtime`), exactement comme `extconfig.conf` pointait autrefois `sippeers` vers la
base de données pour `chan_sip`. Les mécanismes realtime sont couverts dans le chapitre *Realtime* ; le point spécifique à la migration est simplement *quelles tables correspondent à quelles tables*.

## Liste de contrôle de migration

Un ordre d'opérations pragmatique pour une bascule en production :

1. **Inventaire.** Listez chaque périphérique, trunk et `register =>` dans `sip.conf` (ou
   chaque ligne `sippeers`/`sipregs`). Notez les paramètres personnalisés de NAT, codec et DTMF.
2. **Exécutez le convertisseur dans un fichier temporaire.**
   `sip_to_pjsip.py sip.conf pjsip_generated.conf`. Ne le pointez **pas** vers votre
   `pjsip.conf` en production.
3. **Lisez le bloc "Non mapped elements"** en haut du résultat et résolvez
   chaque ligne — surtout `qualify`, les minuteurs et tout ce qui concerne le NAT.
4. **Concevez le(s) transport(s) à la main.** Un transport par IP/port ; ajoutez TLS/TCP si
   nécessaire ; définissez `external_*_address` et `local_net` pour les serveurs cloud/NAT.
5. **Vérifiez l'authentification.** Confirmez `auth_type=digest`, les noms d'utilisateur et les mots de passe sur chaque
   objet `auth`.
6. **Vérifiez NAT/média/DTMF.** `force_rport`/`rewrite_contact`/`rtp_symmetric`,
   `direct_media`, `dtmf_mode=rfc4733` par endpoint selon les besoins.
7. **Mettez à jour le dialplan.** `SIP/` → `PJSIP/` partout ; vérifiez
   les fonctions `SIP*` et les variables de canal.
8. **Mettez à jour les scripts et la surveillance.** Tout outil ou consommateur AMI qui analysait
   le résultat de `sip show ...` doit passer aux actions `pjsip show ...` / PJSIP AMI.
9. **Rechargez et vérifiez.** `module reload res_pjsip.so`, puis
   `pjsip show endpoints`, `pjsip show registrations`, `pjsip show identifies`.
10. **Testez avec l'enregistreur de paquets.** `pjsip set logger on` ; effectuez un enregistrement,
    un appel entrant et un appel sortant et lisez l'échange SIP de bout en bout.

## Pièges courants

- **`alwaysauthreject` est intégré maintenant — ne le cherchez pas.** `chan_sip` avait besoin de
  `alwaysauthreject=yes` pour ne pas révéler quels numéros existaient en répondant
  différemment aux mauvais noms d'utilisateur. PJSIP fait ce qui est sécurisé par conception : il ne révèle jamais si un endpoint existe. Il n'y a pas d'option `alwaysauthreject` à
  définir. La protection associée — limiter les expéditeurs non identifiés — est le paramètre global
  `unidentified_request_count` / `unidentified_request_period`, activé par défaut.

- **`insecure=invite` n'est pas une option PJSIP — utilisez `identify`.** Il n'y a pas de
  `insecure=` dans `pjsip.conf`. La façon d'accepter des INVITE non authentifiés d'un
  opérateur connu est d'*identifier l'endpoint par IP source* avec `type=identify` /
  `match=`. Faites correspondre aussi étroitement que possible (IP d'hôtes spécifiques, pas de larges CIDR), et
  soutenez cela avec un `type=acl` — un trunk identifié par IP sans authentification est une cible pour la fraude téléphonique.

- **Un transport par IP/port.** Vous ne pouvez pas lier deux transports à la même
  IP:port, et vous ne pouvez pas lier plusieurs transports TCP ou TLS de la même version IP. Le script de conversion peut émettre un transport qui entre en collision avec un que
  vous avez déjà — consolidez vers une seule couche de transport délibérément conçue.

- **`qualify=yes` ne se traduit pas en booléen.** Il appartient à l'**aor** en tant que
  `qualify_frequency=<seconds>`. Le convertisseur dépose `qualify=yes` dans le
  bloc non-mapped précisément parce qu'il n'y a pas de booléen équivalent sur
  l'endpoint.

- **`secret=` n'est pas une option d'endpoint.** Les identifiants résident uniquement dans un objet `type=auth`
  que l'endpoint *référence* (`auth=` pour l'entrant, `outbound_auth=` pour
  le sortant). Mettre un mot de passe sur l'endpoint ne fait rien.

- **La CLI et tous les scripts de scraping échouent silencieusement.** `sip show ...` renvoie "No
  such command", pas une erreur que votre surveillance détectera nécessairement. Auditez chaque
  tâche cron, vérification Nagios et client AMI pour les commandes `sip ` avant la bascule.

## Résumé

Migrer vers Asterisk 22 signifie abandonner `chan_sip`, car le pilote a été
supprimé dans Asterisk 21 et PJSIP est le seul canal SIP qui reste. Le cœur du
travail consiste à ré-exprimer chaque `sip.conf` `peer`/`user`/`friend` — qui regroupait
tout dans un seul bloc — comme un ensemble d'objets PJSIP coopérants : un `endpoint`
plus un `auth`, un `aor` et, selon le périphérique, un `identify` (trunk
entrant), un `registration` (connexion sortante) et un `transport` partagé. Le
script `sip_to_pjsip.py` dans `contrib/scripts/sip_to_pjsip/` effectue la traduction en masse
et signale honnêtement ce qu'il ne peut pas mapper dans un bloc "Non mapped elements", mais son résultat est un premier brouillon : concevez le transport, le NAT et la sécurité à
la main et testez avant la production. Autour de la configuration, mettez à jour le dialplan
(`SIP/` → `PJSIP/`) et vos doigts et scripts (`sip show` → `pjsip show`,
`sip set debug` → `pjsip set logger`). Les déploiements realtime passent de
`sippeers`/`sipregs` aux tables Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/
`ps_contacts`, avec `sip_to_pjsql.py` et le schéma `contrib/ast-db-manage`
pour vous aider. Surveillez les pièges — `alwaysauthreject` est intégré,
`insecure=invite` devient `identify`, `qualify=yes` devient
`qualify_frequency`, et un transport par IP/port — et la bascule est
mécanique plutôt que mystérieuse.

## Quiz

1. Pourquoi un déploiement Asterisk 22 doit-il utiliser PJSIP pour le SIP ?
   - A. `chan_sip` est plus lent mais toujours disponible
   - B. `chan_sip` a été supprimé dans Asterisk 21 et n'existe pas dans Asterisk 22
   - C. PJSIP est le défaut mais `chan_sip` peut être chargé avec `modules.conf`
   - D. `chan_sip` ne fonctionne qu'avec TLS dans Asterisk 22

2. Un bloc `sip.conf` `type=friend` unique devient le plus souvent quel ensemble
   d'objets PJSIP ?
   - A. Un seul `type=peer`
   - B. `type=endpoint` seulement
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. Dans `sip.conf`, `host=dynamic` (le périphérique enregistre sa propre position) correspond à :
   - A. `type=identify` avec `match=dynamic`
   - B. un `type=aor` avec `max_contacts` (le périphérique s'enregistre)
   - C. `direct_media=yes` sur l'endpoint
   - D. `type=registration`

4. Le script de conversion `sip_to_pjsip.py` est :
   - A. Une commande CLI : `asterisk -rx 'sip_to_pjsip'`
   - B. Un script Python dans l'arborescence source d'Asterisk sous
     `contrib/scripts/sip_to_pjsip/`
   - C. Un module compilé chargé au démarrage
   - D. Une partie de `res_pjsip.so`

5. Vrai ou Faux : Le résultat de `sip_to_pjsip.py` est prêt pour la production et doit être
   chargé sans examen.

6. Le raccourci `chan_sip` `nat=force_rport,comedia` se traduit sur un endpoint PJSIP
   par quelles trois options ?
   - A. `nat=yes`, `qualify=yes`, `directmedia=no`
   - B. `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes`
   - C. `external_media_address`, `external_signaling_address`, `local_net`
   - D. `insecure=invite`, `identify`, `match`

7. Le `dtmfmode=rfc2833` de `sip.conf` devient quel paramètre PJSIP ?
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. Sur Asterisk 22, un objet `auth` doit utiliser quel `auth_type`, et quel est le
   statut de `userpass` ?
   - A. `auth_type=userpass` ; c'est la seule valeur valide
   - B. `auth_type=digest` ; `userpass` est déprécié et converti en `digest`
   - C. `auth_type=md5` ; `digest` est déprécié
   - D. `auth_type=plaintext` ; `digest` a été supprimé

9. Un pair fournisseur `chan_sip` avec `insecure=invite` (accepter les INVITE
   non authentifiés depuis une IP connue) est migré vers PJSIP en utilisant :
   - A. `insecure=invite` sur l'endpoint
   - B. `allowguest=yes` dans `[global]`
   - C. un objet `type=identify` avec `match=<provider IP>`
   - D. `auth_type=anonymous`

10. Dans une migration realtime, la table `chan_sip` `sippeers` est remplacée par quelles
    tables PJSIP/Sorcery ?
    - A. Une seule table `pjsip_peers`
    - B. `ps_endpoints`, `ps_aors` et `ps_auths`
    - C. `sipregs` et `voicemail`
    - D. `ps_contacts` seulement

**Réponses :** 1 — B · 2 — C · 3 — B · 4 — B · 5 — Faux · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
