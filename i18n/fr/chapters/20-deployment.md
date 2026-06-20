# Déploiement, surveillance et mise à l'échelle

Faire répondre Asterisk à un appel dans un laboratoire est une chose ; le faire fonctionner comme un service qui survive aux plantages, redémarrages, mises à jour et attaques — et que vous puissiez observer, sauvegarder et faire évoluer — en est une autre. Ce chapitre porte sur tout ce qui se passe *après* que le dialplan fonctionne. Nous commençons par le superviseur qui maintient Asterisk en vie (systemd), passons à son empaquetage dans un conteneur (en utilisant le laboratoire Docker du livre comme exemple concret), puis abordons la gestion de configuration et les sauvegardes, la surveillance et l’observabilité, et enfin les schémas que vous utilisez lorsque un serveur ne suffit pas : haute disponibilité et mise à l’échelle, ainsi que les réalités de l’hébergement dans le cloud.

Tout ce qui est présenté a été vérifié sur le laboratoire Asterisk 22 du livre dans `lab/` — le même conteneur que vous avez construit tout au long du livre.

## Objectifs

- Exécuter Asterisk 22 de manière fiable sous systemd, en tant qu'utilisateur non root, avec redémarrage automatique
- Conteneuriser Asterisk avec Docker et comprendre les compromis réseau
- Conserver `/etc/asterisk` dans le contrôle de version et sauvegarder l'état correct
- Surveiller un système en cours d'exécution via la CLI, CDR/CEL, AMI/ARI et les métriques
- Appliquer des modèles de haute disponibilité actif/veille et d'évolutivité horizontale
- Héberger Asterisk dans le cloud en toute sécurité derrière le NAT et un pare-feu

## Exécution d'Asterisk sous systemd

Sur chaque distribution Linux actuelle — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — le gestionnaire de services est **systemd**. Le chapitre d'installation a montré que l'étape `make config` (exécutée pendant `make install`) installe un script d'initialisation de distribution (`/etc/init.d/asterisk` sur Debian, un script `rc.d` sur RedHat), que systemd encapsule automatiquement en tant que service ; Asterisk fournit également une unité native systemd sous `contrib/systemd/asterisk.service` que vous pouvez installer à la place pour un contrôle plus fin.  
Quoi qu'il en soit, systemd est la méthode prise en charge et de production pour exécuter Asterisk. Référez‑vous à *Installing Asterisk 22* pour la compilation elle‑même ; ici nous nous concentrons sur ce que le service vous apporte et sur la façon de le gérer.

### L’unité de service et son cycle de vie

Une fois que `make config` a installé le service, le cycle de vie est celui de systemd ordinaire :

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Quelques notes opérationnelles :

- **`restart` vs. un rechargement gracieux.** `systemctl restart` arrête le processus et coupe tous les appels. Pour des changements de configuration, vous ne voulez presque jamais cela — utilisez plutôt l’interface CLI d’Asterisk : `asterisk -rx 'core reload'` (ou un rechargement spécifique à un module tel que `pjsip reload`). Réservez `systemctl restart` pour les mises à jour ou un processus bloqué.
- **Se connecter au démon en cours d’exécution.** Avec Asterisk fonctionnant comme service, ouvrez sa console avec `asterisk -r` (ou `asterisk -rvvv` pour une sortie verbeuse). Cela se connecte au démon déjà lancé via son socket de contrôle ; cela ne démarre pas une seconde copie.

### `Restart=` remplace safe_asterisk

Historiquement, Asterisk était lancé via le wrapper **safe_asterisk**, un script shell qui relançait Asterisk en cas de plantage. Sous systemd, cette tâche appartient à la directive `Restart=` de l’unité — systemd remarque la sortie du processus et le relance, avec un délai de reprise contrôlé par `RestartSec=` et une protection contre les boucles de plantage assurée par `StartLimitIntervalSec=`/`StartLimitBurst=`. Ainsi, sur un hôte systemd, **safe_asterisk est remplacé** et généralement inutile. Si votre unité fournie ne le définit pas déjà, un remplacement « drop‑in » est la façon propre d’ajouter un redémarrage en cas d’échec sans modifier le fichier empaqueté :

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Appliquez‑le avec `systemctl daemon-reload && systemctl restart asterisk`. Utiliser un « drop‑in » (plutôt que de modifier l’unité installée) signifie qu’une future `make config` ne remplacera pas votre modification.

### Exécution en tant qu’utilisateur non‑root

Asterisk ne doit pas être exécuté en tant que root en production — un bug de code à distance dans un processus fonctionnant en tant que root compromet tout l’hôte, alors que le même bug dans un processus non privilégié reste confiné. Deux endroits complémentaires appliquent cette règle :

- **L’unité / asterisk.conf.** L’unité empaquetée exécute normalement Asterisk en tant qu’utilisateur et groupe `asterisk`. Vous pouvez également (ou à la place) définir `runuser` et `rungroup` dans la section `[options]` de `asterisk.conf`, que le démon respecte lorsqu’il abandonne les privilèges après la liaison :

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propriété des fichiers.** Les répertoires d’exécution doivent être accessibles en écriture par cet utilisateur. Après avoir créé le compte, assurez‑vous de la propriété :

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Comme SIP (5060) et RTP (10000+) utilisent tous des ports élevés, Asterisk **n’a pas besoin** de root pour les lier — seuls les ports privilégiés de type 25 nécessiteraient root, ce qu’Asterisk n’utilise pas. L’exécution non privilégiée est donc sans contrainte. (Le chapitre Sécurité développe pourquoi cela importe ; voir *Asterisk Security*.)

## Containerizing Asterisk

Un conteneur regroupe Asterisk et ses dépendances exactes dans une image immuable, de sorte que
ce que vous testez est exactement le même bit‑pour‑bit que ce que vous livrez. Le compromis porte sur le média en temps réel : un serveur SIP est sensible à la latence et nécessite une large plage prévisible de ports UDP accessibles depuis l’extérieur, et le réseau des conteneurs peut interférer. Le reste de
cette section parcourt le laboratoire du livre — `lab/Dockerfile` et
`lab/docker-compose.yml` — comme exemple concret et fonctionnel, puis explique le seul
piège que tout le monde rencontre : RTP et le réseau en pont.

### The image: building Asterisk from source

Le `Dockerfile` du laboratoire compile Asterisk 22 à partir des sources sur Debian 12. Sa forme vaut la peine d’être lue même si vous n’en écrivez jamais un vous‑même :

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Trois points à souligner :

- **La version est figée** (`ARG ASTERISK_VERSION=22.10.0`). La reproductibilité est le
  but même de la containerisation — augmentez‑la délibérément, reconstruisez, retestez.
- **`--with-pjproject-bundled` et `--with-jansson-bundled`** construisent la pile SIP
  avec une version correspondant à Asterisk, de sorte que vous dépendez de moins de paquets apt et n’avez jamais à combattre un
  PJSIP de la distribution qui serait désynchronisé.
- **`CMD ["asterisk", "-f", "-vvv"]`** exécute Asterisk au *premier plan* (`-f`, « ne pas
  fork »). C’est la différence clé avec un hôte systemd : le processus principal d’un conteneur
  ne doit pas se daemoniser, sinon le conteneur se terminerait immédiatement. Ainsi, dans un conteneur vous
  **ne** utilisez pas du tout l’unité systemd — le runtime du conteneur (Docker, plus la politique `restart:`)
  devient le superviseur que l’unité `Restart=` était sur une VM.

### Montage‑bind `/etc/asterisk`

L’image contient délibérément **aucune** configuration. À la place, `docker-compose.yml`
monte en bind le répertoire de configuration de l’hôte dans :

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` mappe le répertoire versionné `lab/asterisk/etc` sur le `/etc/asterisk` du conteneur, en lecture seule (`:ro`). Le gain est important : l’image reste immuable et réutilisable, tandis que la configuration vit sur l’hôte où elle peut être modifiée et, surtout, conservée dans git (section suivante). Pour appliquer un changement de configuration, vous modifiez le fichier et rechargez — `docker compose exec asterisk asterisk -rx 'core reload'` — sans reconstruction. `restart: unless-stopped` est l’équivalent au niveau compose de systemd's `Restart=` : Docker redémarre le conteneur si Asterisk se termine, mais pas si vous l’arrêtez délibérément.

### Hôte vs. réseau ponté — le problème RTP

Ceci est le problème le plus courant avec Asterisk conteneurisé, il vaut donc la peine de le comprendre précisément. Par défaut Docker place un conteneur sur un réseau **bridged** et vous publiez des ports individuels avec `ports:`. La signalisation fonctionne — 5060 est un port. Le problème est le média : RTP utilise une *plage* de ports UDP (le `rtp.conf` du laboratoire définit `rtpstart=10000` / `rtpend=10100`), et **chaque** port pouvant transporter de l’audio doit être publié.

Le laboratoire fait exactement cela :

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Notez que la plage de publication RTP (`10000-10100`) correspond exactement à `rtp.conf`. Faites une erreur —
publiez trop peu de ports, ou une plage différente de `rtp.conf` — et les appels se connectent mais
ont **un son à sens unique ou aucun son**, parce que les paquets RTP atterrissent sur un port que Docker ne
transmet pas. Deux autres précautions avec le mode pont :

- **Publier des milliers de ports est lent et lourd.** Une plage RTP de production est
  généralement de 10000 à 20000. Docker crée ~10000 proxys userland est coûteux au
  démarrage et ajoute un saut dans le chemin média. Le laboratoire garde une plage
  délibérément petite de 100 ports parce qu’il ne lance jamais plus d’un ou deux appels de test.
- **NAT dans le SDP.** Derrière le pont, Asterisk voit l’adresse IP privée du conteneur et peut
  la publier dans le SDP. Sur un hôte public, vous devez indiquer à PJSIP son adresse externe avec
  `external_media_address` / `external_signaling_address` sur le transport (et définir
  `local_net`), exactement comme vous le feriez derrière n’importe quel NAT — voir *Cloud hosting* ci‑dessous.

L’alternative est **host networking** (`network_mode: host`), qui supprime complètement le pont : le conteneur partage la pile réseau de l’hôte, ainsi le 5060 et toute la plage RTP sont accessibles sans publication de ports et sans saut média supplémentaire. C’est le
mode recommandé pour un vrai conteneur Asterisk — il contourne complètement le problème de plage RTP. Son coût est l’isolation : le conteneur peut lier n’importe quel port de l’hôte et vous perdez le réseau par service de compose. (Le host networking est une fonctionnalité Linux ; sous Docker Desktop
pour macOS/Windows il se comporte différemment, ce qui explique en partie pourquoi ce laboratoire pédagogique utilise
des ports publiés explicitement à la place.)

### Volumes persistants pour spool et voicemail

La couche writable d’un conteneur est **éphémère** — détruisez le conteneur et tout ce qu’il
a écrit disparaît. Pour Asterisk, cela signifie que la messagerie vocale, les enregistrements, le spool des appels sortants
et la base de données locale disparaîtraient à chaque `docker compose up --build`. La configuration
survit parce qu’elle est bind‑montée depuis l’hôte ; *l’état* nécessite le même traitement.
À l’intérieur du conteneur, les arbres pertinents sont :

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

Le laboratoire d'enseignement omet ceux‑ci exprès — il est sans état et reproductible par conception, donc chaque `up` est une ardoise vierge — mais un conteneur de production **doit** les avoir, sinon vous perdrez la messagerie vocale lors du premier redéploiement.

## Gestion de la configuration et sauvegardes

Le bind‑mount ci‑dessus indique le bon modèle : traiter `/etc/asterisk` comme **code** et le reste comme **données**.

### Conserver `/etc/asterisk` sous contrôle de version

Le répertoire de configuration est un ensemble plat de fichiers texte sans secrets qui ne peuvent pas être templatisés — il est idéal pour git. Initialise un dépôt dans `/etc/asterisk` (ou, comme le laboratoire le fait, garde la configuration à côté du projet et bind‑mount‑le). Avantages :

- Chaque modification est révisable et réversible (`git diff`, `git revert`).
- Vous disposez d’une trace d’audit indiquant qui a changé quoi et quand.
- Combiné avec une image de conteneur, un commit de configuration connu‑bon plus une balise d’image figée décrit entièrement un déploiement.

Quelques mises en garde spécifiques à la configuration d’Asterisk :

- **Secrets.** `pjsip.conf` (et `manager.conf`, `ari.conf`) contiennent des mots de passe. Ne
  commettez pas de vrais secrets dans un dépôt partagé en texte clair — templatez‑les (un fichier par
  environnement, ou un gestionnaire de secrets / substitution d’environnement au moment du déploiement) et ne conservez
  que des espaces réservés dans git. Les mots de passe de style `Lab-6001-secret` du laboratoire sont acceptables
  *uniquement* parce qu’ils résident sur un sous‑réseau Docker privé.
- **Templatisation par environnement.** Les valeurs en temps réel qui diffèrent entre dev, staging
  et production (adresses de bind, IP externes, identifiants de trunk, URL de bases de données) sont
  exactement les lignes que vous templatez, en gardant le gros du fichier de configuration identique entre
  les environnements.

### Ce qu’il faut sauvegarder

La configuration dans git couvre le dialplan et les endpoints, mais un PBX en fonctionnement accumule
*un état* qui n’est présent dans aucun fichier de configuration. Une sauvegarde complète comprend :

| Quoi | Où | Pourquoi |
|------|----|----------|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (également dans git) |
| Messagerie vocale & enregistrements | `/var/spool/asterisk/` | données utilisateur — irremplaçables |
| Base de données interne | `/var/lib/asterisk/astdb.sqlite3` | clés `DB()`, état des appareils |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` ou stockage SQL | facturation & historique |
| Bases de données externes | votre MySQL/PostgreSQL | realtime, CDR, messagerie vocale |

L’**astdb** mérite une note : c’est le petit magasin clé/valeur intégré d’Asterisk (un fichier SQLite à `/var/lib/asterisk/astdb.sqlite3`) utilisé par les fonctions de dialplan `DB()`,
les états des appareils, les paramètres follow‑me et similaires. Vous pouvez le dumper pour inspection ou sauvegarde
depuis la CLI :

```
asterisk -rx 'database show'
```

Si votre CDR/CEL ou votre messagerie vocale ou la configuration PJSIP résident dans une base de données externe (voir
*Asterisk Real-Time* et *Asterisk Call Detail Records*), cette base de données devient la source de vérité pour ces données et doit figurer dans votre rotation habituelle de sauvegardes de bases de données —
sauvegarder uniquement `/etc/asterisk` n’est pas suffisant.

## Monitoring and observability

Vous ne pouvez pas gérer ce que vous ne voyez pas. Asterisk expose son état à quatre niveaux, d’un coup d’œil humain rapide à un pipeline de métriques : le **CLI**, les enregistrements **CDR/CEL**, les événements **AMI/ARI**, et les **metrics exporters**.

### CLI health checks

Le test le plus rapide « est‑il en bonne santé ? » est le CLI. Les commandes ci‑dessous sont exécutées en direct contre le laboratoire. Channels first:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` sur un système calme est normal ; sur un système chargé, c’est votre concurrence en temps réel. `core show uptime` confirme que le processus ne redémarre pas sous vous :

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Pour la santé SIP, `pjsip show endpoints` montre chaque endpoint et si ses contacts enregistrés sont accessibles. D'après le laboratoire:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` signifie simplement qu’aucun téléphone n’est actuellement enregistré sur ces endpoints (le laboratoire n’a aucun client en ligne) — une fois qu’un softphone s’enregistre et que `qualify` le confirme, l’état indique que le contact est joignable. Commandes associées : `pjsip show contacts` (enregistrements actuels et temps de trajet aller‑retour), `pjsip show transports`, et `pjsip show aor <name>` pour un AOR. Ce sont les outils du quotidien pour « pourquoi l’extension X n’est‑elle pas joignable ? ».

### CDR et CEL

Chaque appel génère un **Call Detail Record** (CDR) ; **Channel Event Logging** (CEL) ajoute des événements plus fins par canal. Vérifiez que le CDR est actif et quel backend le stocke :

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

Le laboratoire montre `(none)` sous les back‑ends enregistrés parce que la configuration minimale du laboratoire ne charge aucun module de stockage CDR — les enregistrements sont donc calculés mais n’écrits nulle part. En production, vous chargez un back‑end (CSV, ou `cdr_odbc`/`cdr_adaptive_odbc` dans MySQL/PostgreSQL) et cela devient votre source de facturation et d’historique. CEL est **désactivé par défaut** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` uniquement lorsque vous avez besoin de détails au niveau des événements. Les deux sont couverts en profondeur dans *Asterisk Call Detail Records* ; pour la surveillance, l’essentiel est que CDR/CEL sont votre enregistrement *historique*, tandis que le CLI est votre vue *en temps réel*.

### AMI et événements ARI

Pour une surveillance programmatique et en temps réel, vous voulez un flux poussé d’événements plutôt que d’interroger le CLI :

- **AMI (Asterisk Manager Interface)** est le protocole d’événements/commandes TCP de longue date (`manager.conf`). Abonnez‑vous et vous recevez `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` et d’autres événements au fur et à mesure que les appels se produisent — l’épine dorsale des panneaux d’affichage et des outils de comptabilité des appels. Dans le laboratoire, AMI est désactivé par défaut (`manager show settings` signale `Manager (AMI): No`) ; vous l’activez et le sécurisez dans `manager.conf`.
- **ARI (Asterisk REST Interface)** est l’interface moderne HTTP + WebSocket (`ari.conf`, servie par le serveur HTTP intégré). Elle fournit un flux d’événements JSON et un contrôle d’appel granulaire — le choix approprié pour les nouvelles intégrations.

Les deux sont détaillés dans *Extending Asterisk with AMI and AGI* et *The Asterisk REST Interface (ARI)*. Avertissement lié au déploiement : **AMI et ARI sont puissants et ne doivent jamais être exposés à Internet.** Liez le serveur HTTP à localhost ou à un réseau de gestion, utilisez des secrets forts et uniques, et filtrez les ports avec un pare‑feu — voir *Asterisk Security*.

### Métriques : Prometheus et Grafana

Pour les tableaux de bord et les alertes, Asterisk 22 fournit un exportateur Prometheus, **`res_prometheus.so`** (un module avec un niveau de support *étendu*), qui expose des métriques sur un point de terminaison HTTP qu’un serveur Prometheus interroge. En plus des métriques de processus de base, il propose des fournisseurs modulables couvrant les canaux, les appels, les endpoints, les ponts et les enregistrements sortants PJSIP :

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

Vous pouvez confirmer que le module est présent dans la version du laboratoire :

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Il affiche `Not Running` parce que le laboratoire ne le configure ni ne le charge ; l’activer (`prometheus.conf` plus le serveur HTTP) transforme Asterisk en cible Prometheus. Dirigez Prometheus vers le point de collecte et Grafana vers Prometheus, et vous obtenez des tableaux de bord de séries temporelles (appels concurrents, enregistrements, tendances ASR/ACD) ainsi que des alertes (par ex. « les appels actifs sont tombés à zéro » ou « les échecs d’enregistrement augmentent fortement »). Pour les équipes qui utilisent déjà Prometheus/Grafana, c’est la façon naturelle d’intégrer Asterisk à l’observabilité existante, plutôt que d’analyser la sortie CLI.

### Codes de réponse SIP à surveiller

Quel que soit le pipeline, quelques résultats SIP signalent des problèmes et méritent d’être surveillés : des échecs persistants de challenge `401`/`407` ou `403 Forbidden` suggèrent une attaque par force brute ou une tempête d’identifiants mal configurés (voir la correspondance avec Fail2Ban dans *Asterisk Security*) ; `503 Service Unavailable` indique un serveur ou un trunk surchargé ou congestionné ; et un pic de `408 Request Timeout`/`480 Temporarily Unavailable` signifie généralement que les points de terminaison sont devenus inaccessibles (expiration NAT, échecs de qualification).

## Haute disponibilité et mise à l'échelle

Un serveur Asterisk constitue un point de défaillance unique et possède un plafond d'appels fini. Les deux problèmes — *rester en ligne* et *grandir* — ont des réponses différentes.

### Actif/veille avec une IP flottante

Le modèle HA classique et bien éprouvé pour Asterisk est **actif/veille** (pas actif/actif — l'état des appels dans Asterisk est difficile à partager en temps réel). Deux serveurs identiques, un actif, un veille, partagent une **IP flottante (virtuelle)** gérée par un gestionnaire de cluster tel que **keepalived** (VRRP) ou **Pacemaker/Corosync**. Les téléphones et trunks s'enregistrent sur l'IP flottante, pas sur l'un ou l'autre hôte réel. Si le nœud actif échoue à son contrôle de santé, l'IP flottante passe au nœud veille, qui prend le relais.

L’avertissement honnête : un basculement d’IP **interrompt les appels en cours** — Asterisk ne réplique pas l’état des canaux en direct entre les nœuds, donc toute personne en pleine conversation doit rappeler. Les enregistrements se rétablissent au cours d’un cycle de qualification/enregistrement. Ce que le basculement vous apporte, c’est que le *service* se rétablit en quelques secondes sans intervention manuelle, ce qui, pour la plupart des PBX, est exactement l’objectif. Pour que le nœud veille puisse réellement prendre le relais, les deux nœuds doivent disposer de la même configuration (votre `/etc/asterisk` versionnée dans git, déployée identiquement) et du même *état* — ce qui constitue le point suivant.

### Externaliser l’état avec PJSIP Realtime

Actif/veille ne fonctionne que si le nœud veille connaît les mêmes endpoints et enregistrements que le nœud actif. La façon d’y parvenir est de **cesser de conserver l’état dans des fichiers plats sur une seule machine** et de le déplacer vers une base de données partagée que les deux nœuds lisent. **PJSIP Realtime** (Sorcery soutenu par une base de données) fait exactement cela : endpoints, AORs, auths — et, surtout, **registrations** (la table `ps_contacts`) — résident dans MySQL/PostgreSQL au lieu de `pjsip.conf` et de la mémoire locale. Les deux nœuds Asterisk pointent vers la même base de données, de sorte qu’un téléphone enregistré via un nœud soit visible par l’autre. Cela est couvert dans *Asterisk Real-Time* (la section PJSIP Realtime / Sorcery) ; ici le point de déploiement est que **externaliser l’état est le prérequis tant pour la HA que pour la mise à l’échelle horizontale** — sans cela, chaque nœud est une île.

Appliquez la même logique au reste de votre état : CDR/CEL dans un magasin SQL partagé, voicemail sur un stockage partagé/réplication (ou `ODBC_STORAGE`), et les clés astdb dont vous dépendez dans une base de données. Une fois l’état externalisé, les nœuds Asterisk deviennent presque interchangeables en tant que front‑ends.

### Proxies SIP en façade (OpenSIPS)

Pour dépasser la capacité d’un seul serveur, on place un **proxy SIP/équilibreur de charge** devant un pool de serveurs médias Asterisk. **OpenSIPS** est un proxy SIP spécialement conçu, très **haute performance** (il gère des centaines de milliers d’enregistrements et route le signalement sans toucher aux médias). Le proxy présente une adresse SIP unique au monde, maintient le service d’enregistrement/localisation, et distribue les appels parmi les back‑ends Asterisk. Cette séparation — une couche proxy légère assurant l’enregistrement et le routage, une couche Asterisk horizontalement scalable effectuant le traitement réel des appels (IVR, files d’attente, conférences, transcodage) — est la façon dont les déploiements importants dépassent une seule boîte. (La plateforme SipPulse elle‑même utilise OpenSIPS devant ses serveurs médias/application pour exactement cette raison.)

### Mise à l’échelle des médias

Le proxy distribue le *signalement* à moindre coût ; **les médias sont la ressource coûteuse**. Le relais RTP, et surtout le transcodage entre codecs (p. ex. Opus ↔ G.711) ou la gestion

## Hébergement cloud

Exécuter Asterisk sur une VM cloud (AWS, GCP, Azure, un VPS) est courant et fonctionne bien, mais le réseau cloud est **NATé et protégé par défaut**, ce qui entre en conflit avec SIP. Les préoccupations spécifiques au déploiement sont les suivantes.

### NAT et le SDP

Une VM cloud possède presque toujours une adresse **privée** sur son NIC et une adresse **publique** distincte que le fournisseur NATe vers elle. Si Asterisk annonce l’adresse privée dans le SDP, les téléphones distants envoient le RTP dans un trou noir — le symptôme classique d’audio à sens unique ou absent. Indiquez à PJSIP son identité publique sur le transport :

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` fait réécrire à Asterisk l’adresse qu’il annonce aux pairs publics, tandis que
`local_net` indique quels pairs sont locaux (et ne doivent *pas* être réécrits). C’est la même gestion du NAT décrite pour le réseau Docker en pont ci‑dessus — une VM cloud est, en fait, derrière un NAT.

### Pare‑feu et la plage RTP

Deux pare‑feux s’appliquent généralement sur une VM cloud : le groupe de sécurité / ACL réseau du **fournisseur**, et le **pare‑feu** iptables de l’**hôte**. Les deux doivent ouvrir les mêmes ports, et la politique est celle du chapitre Sécurité. Le jeu de règles de la première édition récupéré
(`docs/legacy-labs/configs/Lab7/rules.v4`) capture la forme — accepter SIP et la plage RTP, accepter les connexions établies/connexes, bloquer le reste :

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Deux corrections apportées par le chapitre Sécurité qui comptent ici : ouvrir **5061 en TCP** (pas UDP) si vous utilisez SIP/TLS, et veiller à ce que la plage UDP RTP de votre pare‑feu corresponde exactement à `rtpstart`/`rtpend` dans `rtp.conf` — la même plage que vous publiez sur un conteneur. Ne dupliquez pas la construction iptables/Fail2Ban ici ; **suivez les sections pare‑feu, Fail2Ban et TLS/SRTP du *Asterisk Security*** (Fail2Ban surveille le canal de journal `security` que le laboratoire active déjà dans `logger.conf`) et appliquez cette politique à la fois sur le pare‑feu de l’hôte et sur le groupe de sécurité cloud.

### Latence, région et le SBC

- **Choisissez une région proche de vos utilisateurs.** La voix est sensible à la latence — une latence unidirectionnelle bouche‑à‑oreille supérieure à ~150 ms se remarque. Hébergez la VM dans la région la plus proche de la majorité de vos téléphones et trunks ; les médias intercontinentaux sont audiblement pires.
- **Placez un SBC en façade pour tout déploiement exposé à Internet.** Un **Session Border Controller** termine SIP/RTP à la périphérie, masque votre topologie, normalise le NAT et absorbe le trafic DoS et de scan avant qu’il n’atteigne Asterisk. La recommandation principale du chapitre Sécurité — *ne pas exposer Asterisk brut à Internet* — s’applique doublement dans le cloud, où l’adresse IP publique de votre VM est scannée quelques minutes après son démarrage. Un SBC (ou au minimum un proxy SIP renforcé comme OpenSIPS avec Fail2Ban) est la solution de bord standard.

## Summary

Le déploiement est l’endroit où un dialplan fonctionnel devient un service fiable. Sur une VM, exécutez Asterisk sous **systemd** en tant qu’utilisateur **non-root**, laissant le `Restart=` de l’unité le garder en vie (safe_asterisk est remplacé) et en utilisant `core reload` plutôt que `systemctl restart` pour les changements de configuration. **Containeriser** avec Docker — comme le laboratoire du livre le fait — vous fournit une image immuable, épinglée, avec la configuration **bind‑mounted** depuis un `/etc/asterisk` git; le problème réside dans les médias, donc utilisez soit **host networking** soit publiez une plage de ports RTP qui **correspond exactement à `rtp.conf`**, et montez des **volumes persistants** pour spool/voicemail/astdb afin que l’état survive à un redéploiement. Traitez la configuration comme du code et **sauvegardez l’état** que la configuration ne capture pas : voicemail, enregistrements, `astdb.sqlite3`, et CDR/CEL. **Observez** le système à quatre niveaux — le CLI (`core show channels`, `pjsip show endpoints`) pour la vue en temps réel, **CDR/CEL** pour l’historique, **AMI/ARI** pour les événements programmatiques, et l’exportateur **`res_prometheus`** vers Grafana pour les tableaux de bord et les alertes — tout en gardant AMI/ARI hors d’Internet public. Pour **rester en ligne**, exécutez une configuration active/standby avec une **IP flottante** (en acceptant que le basculement coupe les appels en cours) ; pour **grandir**, externalisez l’état avec **PJSIP Realtime**, placez un pool de serveurs médias devant **OpenSIPS**, et minimisez le transcodage car **les médias — et non les enregistrements — sont ce qui limite un serveur**. Enfin, dans le **cloud**, considérez la VM comme derrière NAT (`external_media_address`, `local_net`), ouvrez le pare‑feu selon le chapitre Sécurité à la fois sur l’hôte et dans le groupe de sécurité du fournisseur, choisissez une région à faible latence, et n’exposez jamais Asterisk brut — placez un **SBC** à la périphérie.

## Quiz

1. Sur un hôte systemd, qu’est‑ce qui remplace le rôle de l’ancien wrapper `safe_asterisk` consistant à redémarrer un Asterisk planté ?
   - A. Une tâche cron
   - B. La directive `Restart=` du fichier d’unité
   - C. `systemctl enable`
   - D. L’astdb
2. Pour appliquer une modification de configuration à un Asterisk en cours d’exécution **sans interrompre les appels**, vous devez :
   - A. `systemctl restart asterisk`
   - B. Redémarrer le serveur
   - C. `asterisk -rx 'core reload'`
   - D. Reconstruire l’image du conteneur
3. Un Asterisk conteneurisé (réseau pont) établit les appels mais n’a **pas d’audio**. La cause la plus probable est :
   - A. Le dialplan est incorrect
   - B. La plage de ports UDP RTP publiée ne correspond pas à `rtpstart`/`rtpend` dans `rtp.conf`
   - C. Le CDR est désactivé
   - D. Le CLI est inaccessible
4. Quels répertoires doivent être montés comme **volumes persistants** afin qu’un redéploiement de conteneur ne perde pas l’état ? (cochez tout ce qui s’applique)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (déjà bind‑mounté depuis l’hôte)
   - D. `/usr/sbin`
5. Quelle commande CLI donne le nombre en temps réel d’appels actifs ?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. Dans Asterisk 22, la méthode prise en charge pour exposer les métriques d’appels/canaux à une pile Prometheus/Grafana est :
   - A. Analyser le fichier journal `full`
   - B. Le module `res_prometheus.so`
   - C. Les scripts AGI
   - D. Il n’y en a pas
7. Quelle est la condition préalable à la fois pour le basculement HA et le dimensionnement horizontal sur plusieurs nœuds Asterisk ?
   - A. S’exécuter en tant que root
   - B. Externaliser l’état (par ex. les enregistrements Realtime PJSIP dans une base de données partagée)
   - C. Désactiver le CDR
   - D. Utiliser un réseau ponté
8. Quelle ressource limite le plus directement le nombre d’appels simultanés qu’un serveur Asterisk peut gérer ?
   - A. Le nombre d’utilisateurs enregistrés
   - B. Le traitement média, en particulier le transcodage
   - C. La taille de `/etc/asterisk`
   - D. Le backend du CDR
9. Sur une VM cloud, quels paramètres de transport `pjsip.conf` font qu’Asterisk annonce son adresse publique afin que l’audio distant fonctionne ? (cochez tout ce qui s’applique)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Pour un déploiement cloud exposé à Internet, la règle principale du chapitre Sécurité est :
    - A. Toujours utiliser deux NIC
    - B. Ne jamais exposer Asterisk brut à Internet ; placer un SBC (ou un proxy renforcé + Fail2Ban) en périphérie
    - C. Utiliser uniquement UDP
    - D. Désactiver TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
