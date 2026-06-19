# Déploiement, surveillance et mise à l'échelle

Faire en sorte qu'Asterisk réponde à un appel dans un laboratoire est une chose ; l'exécuter en tant que service capable de survivre aux plantages, redémarrages, mises à jour et attaques — et que vous pouvez observer, sauvegarder et faire évoluer — en est une autre. Ce chapitre traite de tout ce qui se passe *après* que le dialplan fonctionne. Nous commençons par le superviseur qui maintient Asterisk en vie (systemd), passons à sa mise en conteneur (en utilisant le laboratoire Docker du livre comme exemple pratique), puis nous abordons la gestion de la configuration et les sauvegardes, la surveillance et l'observabilité, et enfin les modèles à adopter lorsqu'un seul serveur ne suffit plus : la haute disponibilité, la mise à l'échelle et les réalités de l'hébergement dans le cloud.

Tout ce qui est présenté est vérifié par rapport au laboratoire Asterisk 22 du livre dans `lab/` — le même conteneur que vous avez construit tout au long du livre.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Exécuter Asterisk 22 de manière fiable sous systemd, en tant qu'utilisateur non privilégié, avec redémarrage automatique
- Conteneuriser Asterisk avec Docker et comprendre les compromis liés au réseau
- Conserver `/etc/asterisk` dans un système de contrôle de version et sauvegarder l'état approprié
- Surveiller un système en cours d'exécution via la CLI, les CDR/CEL, l'AMI/ARI et les métriques
- Appliquer des modèles de haute disponibilité actif/passif et de mise à l'échelle horizontale
- Héberger Asterisk dans le cloud en toute sécurité derrière un NAT et un pare-feu

## Exécuter Asterisk sous systemd

Sur toutes les distributions Linux actuelles — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — le gestionnaire de services est **systemd**. Le chapitre sur l'installation a montré que l'étape `make config` (exécutée pendant `make install`) installe un script d'initialisation de distribution (`/etc/init.d/asterisk` sur Debian, un script `rc.d` sur RedHat), que systemd encapsule ensuite automatiquement en tant que service ; Asterisk fournit également une unité systemd native sous `contrib/systemd/asterisk.service` que vous pouvez installer à la place pour un contrôle plus précis.
Quoi qu'il en soit, systemd est la méthode prise en charge et recommandée en production pour exécuter Asterisk. Référez-vous à *Installing Asterisk 22* pour la compilation elle-même ; ici, nous nous concentrons sur ce que le service vous apporte et comment l'exploiter.

### L'unité de service et son cycle de vie

Une fois que `make config` a installé le service, le cycle de vie est celui d'un service systemd classique :

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Quelques notes opérationnelles :

- **`restart` vs. un rechargement gracieux.** `systemctl restart` arrête le processus et interrompt tous les appels. Pour des modifications de configuration, vous ne voulez presque jamais cela — utilisez plutôt la CLI Asterisk : `asterisk -rx 'core reload'` (ou un rechargement spécifique à un module tel que `pjsip reload`). Réservez `systemctl restart` aux mises à niveau ou à un processus bloqué.
- **S'attacher au démon en cours d'exécution.** Avec Asterisk fonctionnant comme un service, ouvrez sa console avec `asterisk -r` (ou `asterisk -rvvv` pour une sortie détaillée). Cela se connecte au démon déjà en cours d'exécution via son socket de contrôle ; cela ne démarre pas une seconde instance.

### `Restart=` remplace safe_asterisk

Historiquement, Asterisk était lancé via le wrapper **safe_asterisk**, un script shell qui relançait Asterisk s'il plantait. Sous systemd, cette tâche appartient à la directive `Restart=` de l'unité — systemd détecte la sortie du processus et le relance, avec un délai contrôlé par `RestartSec=` et une protection contre les boucles de plantage par `StartLimitIntervalSec=`/`StartLimitBurst=`. Ainsi, sur un hôte systemd, **safe_asterisk est obsolète** et généralement inutile. Si votre unité fournie ne le définit pas déjà, une surcharge (drop-in) est le moyen propre d'ajouter un redémarrage en cas d'échec sans modifier le fichier packagé :

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Appliquez-le avec `systemctl daemon-reload && systemctl restart asterisk`. L'utilisation d'un fichier de surcharge (plutôt que la modification de l'unité installée) signifie qu'une future mise à jour `make config` n'écrasera pas votre modification.

### Exécuter en tant qu'utilisateur non privilégié

Asterisk ne devrait pas s'exécuter en tant que root en production — un bug de code distant dans un processus s'exécutant en tant que root constitue une compromission totale de l'hôte, alors que le même bug dans un processus non privilégié est contenu. Il existe deux endroits complémentaires où cela est appliqué :

- **L'unité / asterisk.conf.** L'unité packagée exécute normalement Asterisk en tant qu'utilisateur et groupe `asterisk`. Vous pouvez également (ou à la place) définir `runuser` et `rungroup` dans la section `[options]` de `asterisk.conf`, que le démon respecte lorsqu'il abandonne ses privilèges après la liaison :

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Propriété des fichiers.** Les répertoires d'exécution doivent être accessibles en écriture par cet utilisateur. Après avoir créé le compte, assurez-vous de la propriété :

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Comme SIP (5060) et RTP (10000+) sont tous des ports élevés, Asterisk n'a **pas** besoin de root pour les lier — seuls les ports privilégiés de type port 25 le nécessiteraient, ce qu'Asterisk n'utilise pas. L'exécution sans privilèges est donc gratuite. (Le chapitre sur la sécurité explique pourquoi cela est important ; voir *Asterisk Security*.)

## Conteneuriser Asterisk

Un conteneur regroupe Asterisk et ses dépendances exactes dans une image immuable, de sorte que ce que vous testez est identique octet pour octet à ce que vous déployez. Le compromis concerne les médias en temps réel : un serveur SIP est sensible à la latence et nécessite une plage large et prévisible de ports UDP accessibles depuis l'extérieur, et la mise en réseau des conteneurs peut poser problème. Le reste de cette section parcourt le laboratoire du livre — `lab/Dockerfile` et `lab/docker-compose.yml` — comme un exemple concret et fonctionnel, puis explique le piège dans lequel tout le monde tombe : le RTP et le réseau ponté (bridged).

### L'image : compiler Asterisk à partir des sources

Le fichier `Dockerfile` du laboratoire compile Asterisk 22 à partir des sources sur Debian 12. Sa structure mérite d'être lue même si vous n'en écrivez jamais vous-même :

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

- **La version est figée** (`ARG ASTERISK_VERSION=22.10.0`). La reproductibilité est tout l'intérêt de la conteneurisation — augmentez-la délibérément, reconstruisez, retestez.
- **`--with-pjproject-bundled` et `--with-jansson-bundled`** compilent la pile SIP en faisant correspondre la version à celle d'Asterisk, vous dépendez donc de moins de paquets apt et ne vous battez jamais contre un PJSIP de distribution qui n'est pas à jour.
- **`CMD ["asterisk", "-f", "-vvv"]`** exécute Asterisk au *premier plan* (`-f`, "ne pas forker"). C'est la différence clé avec un hôte systemd : le processus principal d'un conteneur ne doit pas se transformer en démon, sinon le conteneur s'arrêterait immédiatement. Donc, dans un conteneur, vous n'utilisez **pas** l'unité systemd du tout — le runtime du conteneur (Docker, plus la politique `restart:`) devient le superviseur que l'unité `Restart=` était sur une VM.

### Montage par liaison (Bind-mounting) de `/etc/asterisk`

L'image ne contient délibérément **aucune** configuration. Au lieu de cela, `docker-compose.yml` monte par liaison le répertoire de configuration de l'hôte :

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

`./asterisk/etc:/etc/asterisk:ro` mappe le répertoire `lab/asterisk/etc` sous contrôle de version sur le répertoire `/etc/asterisk` du conteneur, en lecture seule (`:ro`). Le gain est important : l'image reste immuable et réutilisable, tandis que la configuration réside sur l'hôte où elle peut être modifiée et, surtout, conservée dans git (section suivante). Pour appliquer une modification de configuration, vous modifiez le fichier et rechargez — `docker compose exec asterisk asterisk -rx 'core reload'` — sans reconstruction. `restart: unless-stopped` est l'équivalent au niveau compose de `Restart=` de systemd : Docker redémarre le conteneur si Asterisk s'arrête, mais pas si vous l'avez arrêté délibérément.

### Réseau hôte vs. ponté — le problème RTP

C'est l'échec le plus courant avec Asterisk conteneurisé, il vaut donc la peine d'être compris précisément. Par défaut, Docker place un conteneur sur un réseau **ponté** et vous publiez des ports individuels avec `ports:`. La signalisation fonctionne bien — 5060 est un port unique. Le problème concerne les médias : le RTP utilise une *plage* de ports UDP (le `rtp.conf` du laboratoire définit `rtpstart=10000` / `rtpend=10100`), et **chaque** port susceptible de transporter de l'audio doit être publié.

Le laboratoire fait exactement cela :

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Notez que la plage de publication RTP (`10000-10100`) correspond exactement à `rtp.conf`. Si vous vous trompez — en publiant trop peu de ports, ou une plage différente de `rtp.conf` — les appels se connectent mais présentent un **audio unidirectionnel ou inexistant**, car les paquets RTP arrivent sur un port que Docker ne transfère pas. Deux mises en garde supplémentaires avec le mode ponté :

- **Publier des milliers de ports est lent et lourd.** Une plage RTP de production est généralement de 10000 à 20000. Le fait que Docker crée environ 10000 proxys en espace utilisateur est coûteux au démarrage et ajoute un saut dans le chemin des médias. Le laboratoire conserve une petite plage de 100 ports car il n'exécute jamais qu'un ou deux appels de test.
- **NAT dans le SDP.** Derrière le pont, Asterisk voit son IP de conteneur privée et peut l'annoncer dans le SDP. Sur un hôte public, vous devez indiquer à PJSIP son adresse externe avec `external_media_address` / `external_signaling_address` sur le transport (et définir `local_net`), exactement comme vous le feriez derrière n'importe quel NAT — voir *Hébergement cloud* ci-dessous.

L'alternative est le **réseau hôte** (`network_mode: host`), qui supprime complètement le pont : le conteneur partage la pile réseau de l'hôte, donc 5060 et toute la plage RTP sont accessibles sans publication de port et sans saut média supplémentaire. C'est le mode recommandé pour un conteneur Asterisk réel — il évite complètement le problème de la plage RTP. Son coût est l'isolation : le conteneur peut lier n'importe quel port de l'hôte et vous perdez le réseau par service de compose. (Le réseau hôte est une fonctionnalité Linux ; sur Docker Desktop pour macOS/Windows, il se comporte différemment, ce qui explique en partie pourquoi ce laboratoire pédagogique utilise des ports publiés explicites.)

### Volumes persistants pour le spool et la messagerie vocale

La couche inscriptible d'un conteneur est **éphémère** — détruisez le conteneur et tout ce qu'il a écrit disparaît. Pour Asterisk, cela signifie que la messagerie vocale, les enregistrements, le spool d'appels sortants et la base de données locale disparaîtraient à chaque `docker compose up --build`. La configuration survit car elle est montée par liaison depuis l'hôte ; l' *état* a besoin du même traitement. À l'intérieur du conteneur, les arborescences pertinentes sont :

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(Le conteneur en cours d'exécution du laboratoire montre exactement celles-ci — `/var/spool/asterisk` contient `voicemail`, `monitor`, `outgoing`, `recording` ; `/var/lib/asterisk` contient `astdb.sqlite3`.) Pour les préserver, montez des volumes nommés pour les répertoires qui contiennent l'état qui vous importe :

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

Le laboratoire pédagogique les omet volontairement — il est sans état et reproductible par conception, donc chaque `up` est une page blanche — mais un conteneur de production **doit** les avoir, sinon vous perdrez la messagerie vocale lors du premier redéploiement.

## Gestion de la configuration et sauvegardes

Le montage par liaison ci-dessus suggère le bon modèle : traitez `/etc/asterisk` comme du **code** et le reste comme des **données**.

### Conserver `/etc/asterisk` sous contrôle de version

Le répertoire de configuration est un ensemble plat de fichiers texte sans secrets qui ne peuvent pas être modélisés — il est idéal pour git. Initialisez un dépôt dans `/etc/asterisk` (ou, comme le fait le laboratoire, conservez la configuration à côté du projet et montez-la par liaison). Avantages :

- Chaque modification est révisable et réversible (`git diff`, `git revert`).
- Vous avez une piste d'audit de qui a changé quoi et quand.
- Combiné avec une image de conteneur, un commit de configuration connu comme bon plus une balise d'image figée décrit entièrement un déploiement.

Quelques mises en garde spécifiques à la configuration d'Asterisk :

- **Secrets.** `pjsip.conf` (et `manager.conf`, `ari.conf`) contiennent des mots de passe. Ne committez pas de vrais secrets dans un dépôt partagé en texte clair — modélisez-les (un fichier par environnement, ou un gestionnaire de secrets / substitution d'environnement au moment du déploiement) et ne gardez que des espaces réservés dans git. Les mots de passe triviaux de style `Lab-6001-secret` du laboratoire ne sont acceptables *que* parce qu'ils vivent sur un sous-réseau Docker privé.
- **Modélisation par environnement.** Les valeurs temps réel qui diffèrent entre le développement, la pré-production et la production (adresses de liaison, IP externes, identifiants de trunk, URL de base de données) sont exactement les lignes que vous modélisez, gardant la majeure partie de la configuration identique entre les environnements.

### Que sauvegarder

La configuration dans git couvre le dialplan et les endpoints, mais un PBX en direct accumule un *état* qui n'est dans aucun fichier de configuration. Une sauvegarde complète est :

| Quoi | Où | Pourquoi |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (également dans git) |
| Messagerie vocale & enregistrements | `/var/spool/asterisk/` | données utilisateur — irremplaçables |
| Base de données interne | `/var/lib/asterisk/astdb.sqlite3` | clés `DB()`, état des périphériques |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` ou stockage SQL | facturation & historique |
| Bases de données externes | votre MySQL/PostgreSQL | temps réel, CDR, messagerie vocale |

L' **astdb** mérite une note : c'est le petit magasin clé/valeur intégré d'Asterisk (un fichier SQLite à `/var/lib/asterisk/astdb.sqlite3`) utilisé par les fonctions de dialplan `DB()`, les états des périphériques, les paramètres de suivi d'appel et similaires. Vous pouvez le vider pour inspection ou sauvegarde depuis la CLI :

```
asterisk -rx 'database show'
```

Si votre configuration CDR/CEL ou messagerie vocale ou PJSIP réside dans une base de données externe (voir *Asterisk Real-Time* et *Asterisk Call Detail Records*), cette base de données est désormais la source de vérité pour ces données et doit être dans votre rotation de sauvegarde de base de données normale — sauvegarder `/etc/asterisk` seul ne suffit pas.

## Surveillance et observabilité

Vous ne pouvez pas exploiter ce que vous ne pouvez pas voir. Asterisk expose son état à quatre niveaux, d'un coup d'œil humain rapide à un pipeline de métriques : la **CLI**, les enregistrements **CDR/CEL**, les événements **AMI/ARI**, et les **exportateurs de métriques**.

### Vérifications de santé via la CLI

La vérification "est-ce sain ?" la plus rapide est la CLI. Les commandes ci-dessous sont exécutées en direct sur le laboratoire. Les canaux d'abord :

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` sur un système calme est normal ; sur un système occupé, c'est votre concurrence en temps réel. `core show uptime` confirme que le processus n'a pas redémarré sous vous :

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Pour la santé SIP, `pjsip show endpoints` montre chaque endpoint et si ses contacts enregistrés sont joignables. Depuis le laboratoire :

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` ici signifie simplement qu'aucun téléphone n'est actuellement enregistré sur ces endpoints (le laboratoire n'a pas de clients actifs) — une fois qu'un softphone s'enregistre et que `qualify` le confirme, l'état montre le contact comme joignable. Commandes compagnons : `pjsip show contacts` (enregistrements actuels et temps d'aller-retour), `pjsip show transports`, et `pjsip show aor <name>` pour un AOR. Ce sont les outils quotidiens "pourquoi l'extension X ne peut-elle pas être atteinte ?".

### CDR et CEL

Chaque appel laisse un **Call Detail Record** (CDR) ; le **Channel Event Logging** (CEL) ajoute des événements plus précis par canal. Confirmez que le CDR est actif et quel backend le stocke :

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

Le laboratoire montre `(none)` sous les backends enregistrés car la configuration minimale du laboratoire ne charge aucun module de stockage CDR — les enregistrements sont donc calculés mais écrits nulle part. En production, vous chargez un backend (CSV, ou `cdr_odbc`/`cdr_adaptive_odbc` dans MySQL/PostgreSQL) et cela devient votre source de facturation et d'historique. Le CEL est **désactivé par défaut** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` uniquement lorsque vous avez besoin de détails au niveau de l'événement. Les deux sont couverts en profondeur dans *Asterisk Call Detail Records* ; pour la surveillance, le point est que les CDR/CEL sont votre enregistrement *historique*, là où la CLI est votre vue *en direct*.

### Événements AMI et ARI

Pour une surveillance programmatique en temps réel, vous voulez un flux d'événements plutôt que d'interroger la CLI :

- **AMI (Asterisk Manager Interface)** est le protocole d'événements/commandes TCP de longue date (`manager.conf`). Abonnez-vous et vous recevrez des événements `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` et similaires au fur et à mesure que les appels se produisent — l'épine dorsale des tableaux de bord et des outils de comptabilité d'appels. Dans le laboratoire, l'AMI est désactivé par défaut (`manager show settings` rapporte `Manager (AMI): No`) ; vous l'activez et le verrouillez dans `manager.conf`.
- **ARI (Asterisk REST Interface)** est l'interface HTTP + WebSocket moderne (`ari.conf`, servie par le serveur HTTP intégré). Elle donne un flux d'événements JSON et un contrôle d'appel granulaire — le bon choix pour les nouvelles intégrations.

Les deux sont détaillés dans *Extending Asterisk with AMI and AGI* et *The Asterisk REST Interface (ARI)*. L'avertissement pertinent pour le déploiement : **AMI et ARI sont puissants et ne doivent jamais être exposés à Internet.** Liez le serveur HTTP à localhost ou à un réseau de gestion, utilisez des secrets uniques forts, et pare-feu les ports — voir *Asterisk Security*.

### Métriques : Prometheus et Grafana

Pour les tableaux de bord et les alertes, Asterisk 22 fournit un exportateur Prometheus, **`res_prometheus.so`** (un module avec un niveau de support *étendu*), qui expose des métriques sur un point de terminaison HTTP que le serveur Prometheus interroge. En plus des métriques de processus de base, il fournit des fournisseurs enfichables couvrant les canaux, les appels, les endpoints, les ponts et les enregistrements sortants PJSIP :

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

Vous pouvez confirmer que le module est présent dans la compilation du laboratoire :

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Il montre `Not Running` car le laboratoire ne le configure pas et ne le charge pas ; l'activer (`prometheus.conf` plus le serveur HTTP) transforme Asterisk en une cible Prometheus. Pointez Prometheus sur le point de terminaison et Grafana sur Prometheus, et vous obtenez des tableaux de bord de séries temporelles (appels simultanés, enregistrements, tendances ASR/ACD) et des alertes (par exemple, "appels actifs tombés à zéro" ou "pics d'échecs d'enregistrement"). Pour les équipes exécutant déjà Prometheus/Grafana, c'est le moyen naturel d'intégrer Asterisk dans l'observabilité existante, plutôt que d'analyser la sortie de la CLI.

### Codes de réponse SIP à surveiller

Quel que soit le pipeline, quelques résultats SIP signalent des problèmes et méritent une alerte : les échecs de défi `401`/`407` soutenus ou `403 Forbidden` suggèrent une attaque par force brute ou une tempête d'identifiants mal configurés (référez-vous à Fail2Ban dans *Asterisk Security*) ; `503 Service Unavailable` pointe vers un serveur ou un trunk surchargé ou congestionné ; et un pic de `408 Request Timeout`/`480 Temporarily Unavailable` signifie généralement que les endpoints sont devenus injoignables (délai d'expiration NAT, échecs de qualification).

## Haute disponibilité et mise à l'échelle

Un serveur Asterisk est un point de défaillance unique et a un plafond d'appels fini. Les deux problèmes — *rester opérationnel* et *grandir* — ont des réponses différentes.

### Actif/passif avec une IP flottante

Le modèle HA classique et bien rodé pour Asterisk est **actif/passif** (pas actif/actif — l'état de l'appel dans Asterisk est difficile à partager en direct). Deux serveurs identiques, un actif, un passif, partagent une **IP flottante (virtuelle)** gérée par un gestionnaire de cluster tel que **keepalived** (VRRP) ou **Pacemaker/Corosync**. Les téléphones et les trunks s'enregistrent sur l'IP flottante, pas sur l'un ou l'autre hôte réel. Si le nœud actif échoue à son test de santé, l'IP flottante passe au passif, qui prend le relais.

La mise en garde honnête : un basculement d'IP **interrompt les appels en cours** — Asterisk ne réplique pas l'état du canal en direct entre les nœuds, donc toute personne en milieu d'appel doit recomposer. Les enregistrements se rétablissent dans un cycle de qualification/enregistrement. Ce que le basculement vous apporte, c'est que le *service* récupère en quelques secondes sans intervention manuelle, ce qui, pour la plupart des PBX, est exactement l'objectif. Pour que le passif soit réellement capable de prendre le relais, les deux nœuds ont besoin de la même configuration (votre `/etc/asterisk` git, déployé de manière identique) et du même *état* — ce qui est le point suivant.

### Externaliser l'état avec PJSIP Realtime

L'actif/passif ne fonctionne que si le passif connaît les mêmes endpoints et enregistrements que le nœud actif. Le moyen d'y parvenir est d' **arrêter de conserver l'état dans des fichiers plats sur une seule machine** et de le déplacer vers une base de données partagée que les deux nœuds lisent. **PJSIP Realtime** (Sorcery soutenu par une base de données) fait exactement cela : les endpoints, AORs, auths — et, surtout, les **enregistrements** (la table `ps_contacts`) — vivent dans MySQL/PostgreSQL au lieu de `pjsip.conf` et de la mémoire locale. Les deux nœuds Asterisk pointent vers la même base de données, donc un téléphone enregistré via un nœud est visible par l'autre. Ceci est couvert dans *Asterisk Real-Time* (la section PJSIP Realtime / Sorcery) ; ici, le point de déploiement est que **l'externalisation de l'état est le prérequis à la fois pour la HA et la mise à l'échelle horizontale** — sans cela, chaque nœud est une île.

Appliquez la même logique au reste de votre état : CDR/CEL dans un magasin SQL partagé, messagerie vocale sur un stockage partagé/répliqué (ou `ODBC_STORAGE`), et les clés astdb dont vous dépendez dans une base de données. Une fois l'état externalisé, les nœuds Asterisk deviennent plus proches de front-ends interchangeables.

### Proxys SIP en façade (OpenSIPS)

Pour évoluer *au-delà* de la capacité d'un seul serveur, vous placez un **proxy SIP/équilibreur de charge** devant un pool de serveurs média Asterisk. **OpenSIPS** est un proxy SIP conçu à cet effet, à très haut débit (ils gèrent des centaines de milliers d'enregistrements et acheminent la signalisation sans toucher aux médias). Le proxy présente une adresse SIP unique au monde, maintient le service d'enregistrement/localisation, et distribue les appels sur les back-ends Asterisk. Cette séparation — un niveau de proxy léger effectuant l'enregistrement et le routage, un niveau Asterisk évolutif horizontalement effectuant le traitement réel des appels (IVR, files d'attente, conférences, transcodage) — est la façon dont les grands déploiements dépassent une seule machine. (La plateforme SipPulse elle-même utilise OpenSIPS devant ses serveurs média/application pour exactement cette raison.)

### Mise à l'échelle des médias

Le proxy distribue la *signalisation* à moindre coût ; **les médias sont la ressource coûteuse**. Le relais RTP, et surtout le transcodage entre codecs (par exemple Opus ↔ G.711) ou l'exécution de grandes conférences, est lié au CPU et est ce qui plafonne réellement un serveur. Stratégies :

- **Évitez le transcodage** autant que possible — négociez un codec commun de bout en bout afin qu'Asterisk ponte nativement (pass-through) au lieu de transcoder. C'est le plus grand gain de capacité média.
- **Mettez à l'échelle les médias horizontalement** en ajoutant des nœuds Asterisk derrière le proxy ; chacun porte une part des appels simultanés.
- **Déchargez les médias du navigateur** vers une passerelle WebRTC dédiée (par exemple Janus) afin que le PBX ne termine et ne relaie pas non plus chaque flux DTLS-SRTP du navigateur — voir *WebRTC with Asterisk*, qui discute exactement de cette séparation Asterisk-plus-passerelle.

Dimensionnez la capacité par **appels simultanés et charge de transcodage**, pas par utilisateurs enregistrés — 10 000 téléphones enregistrés qui sont pour la plupart inactifs sont bien moins chers que 200 conférences transcodées simultanées.

## Hébergement cloud

Exécuter Asterisk sur une VM cloud (AWS, GCP, Azure, un VPS) est courant et fonctionne bien, mais le réseau cloud est **NATé et pare-feu par défaut**, ce qui entre en conflit avec le SIP. Voici les préoccupations spécifiques au déploiement.

### NAT et SDP

Une VM cloud a presque toujours une IP **privée** sur sa carte réseau et une IP **publique** distincte que le fournisseur NATe vers elle. Si Asterisk annonce l'IP privée dans le SDP, les téléphones distants envoient le RTP dans un trou noir — le symptôme classique unidirectionnel/sans audio. Indiquez à PJSIP son identité publique sur le transport :

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` fait en sorte qu'Asterisk réécrive l'adresse qu'il annonce aux pairs publics, tandis que `local_net` lui indique quels pairs sont locaux (et ne doivent *pas* être réécrits). C'est la même gestion NAT discutée pour le réseau Docker ponté ci-dessus — une VM cloud est, en effet, derrière un NAT.

### Pare-feu et plage RTP

Deux pare-feu s'appliquent généralement sur une VM cloud : le groupe de sécurité / ACL réseau du **fournisseur**, et les iptables de l' **hôte**. Les deux doivent ouvrir les mêmes ports, et la politique est celle du chapitre sur la sécurité. L'ensemble de règles de la 1ère édition récupéré (`docs/legacy-labs/configs/Lab7/rules.v4`) capture la forme — accepter le SIP et la plage RTP, accepter les connexions établies/associées, abandonner le reste :

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Deux corrections que le chapitre sur la sécurité apporte et qui comptent ici : ouvrez **5061 sur TCP** (pas UDP) si vous exécutez SIP/TLS, et rappelez-vous que la plage UDP RTP dans votre pare-feu doit correspondre exactement à `rtpstart`/`rtpend` dans `rtp.conf` — la même plage que vous publiez sur un conteneur. Ne dupliquez pas la construction iptables/Fail2Ban ici ; **suivez les sections pare-feu, Fail2Ban et TLS/SRTP de *Asterisk Security*** (Fail2Ban surveille le canal de journalisation `security` qu'Asterisk active déjà dans `logger.conf`) et appliquez cette politique à la fois dans le pare-feu de l'hôte et dans le groupe de sécurité cloud.

### Latence, région et SBC

- **Choisissez une région proche de vos utilisateurs.** La voix est sensible à la latence — une latence bouche-à-oreille unidirectionnelle supérieure à ~150 ms est perceptible. Hébergez la VM dans la région la plus proche de la majorité de vos téléphones et trunks ; les médias transcontinentaux sont audiblement pires.
- **Placez un SBC en façade pour tout déploiement exposé à Internet.** Un **Session Border Controller** termine le SIP/RTP à la périphérie, masque votre topologie, normalise le NAT, et absorbe le trafic DoS et de scan avant qu'il n'atteigne Asterisk. La recommandation principale du chapitre sur la sécurité — *ne pas exposer Asterisk brut à Internet* — s'applique doublement dans le cloud, où l'IP publique de votre VM est scannée quelques minutes après sa mise en service. Un SBC (ou au minimum un proxy SIP durci comme OpenSIPS plus Fail2Ban) est la norme à la périphérie.

## Résumé

Le déploiement est l'endroit où un dialplan fonctionnel devient un service fiable. Sur une VM, exécutez Asterisk sous **systemd** en tant qu'utilisateur **non privilégié**, en laissant la directive `Restart=` de l'unité le maintenir en vie (safe_asterisk est obsolète) et en utilisant `core reload` plutôt que `systemctl restart` pour les changements de configuration. La **conteneurisation** avec Docker — comme le fait le laboratoire du livre — vous donne une image immuable et figée avec une configuration **montée par liaison** depuis un `/etc/asterisk` git ; le piège est le média, donc utilisez soit le **réseau hôte**, soit publiez une plage de ports RTP qui **correspond exactement à `rtp.conf`**, et montez des **volumes persistants** pour le spool/messagerie vocale/astdb afin que l'état survive à un redéploiement. Traitez la configuration comme du code et **sauvegardez l'état** que la configuration ne capture pas : messagerie vocale, enregistrements, `astdb.sqlite3`, et CDR/CEL. **Observez** le système à quatre niveaux — la CLI (`core show channels`, `pjsip show endpoints`) pour la vue en direct, les **CDR/CEL** pour l'historique, l' **AMI/ARI** pour les événements programmatiques, et l'exportateur **`res_prometheus`** vers Grafana pour les tableaux de bord et les alertes — tout en gardant l'AMI/ARI hors de l'Internet public. Pour **rester opérationnel**, exécutez en actif/passif avec une **IP flottante** (en acceptant que le basculement interrompe les appels en direct) ; pour **grandir**, externalisez l'état avec **PJSIP Realtime**, placez un pool de serveurs média derrière **OpenSIPS**, et minimisez le transcodage car **les médias — pas les enregistrements — sont ce qui plafonne un serveur**. Enfin, dans le **cloud**, traitez la VM comme étant derrière un NAT (`external_media_address`, `local_net`), ouvrez le pare-feu selon le chapitre sur la sécurité à la fois dans l'hôte et dans le groupe de sécurité du fournisseur, choisissez une région à faible latence, et n'exposez jamais Asterisk brut — placez un **SBC** à la périphérie.

## Quiz

1. Sur un hôte systemd, qu'est-ce qui remplace le travail de l'ancien wrapper `safe_asterisk` consistant à redémarrer un Asterisk planté ?
   - A. Une tâche cron
   - B. La directive `Restart=` du fichier d'unité
   - C. `systemctl enable`
   - D. L'astdb
2. Pour appliquer un changement de configuration à un Asterisk en cours d'exécution **sans interrompre les appels**, vous devez :
   - A. `systemctl restart asterisk`
   - B. Redémarrer le serveur
   - C. `asterisk -rx 'core reload'`
   - D. Reconstruire l'image du conteneur
3. Un Asterisk conteneurisé (réseau ponté) connecte les appels mais n'a **pas d'audio**. La cause la plus probable est :
   - A. Le dialplan est faux
   - B. La plage de ports UDP RTP publiée ne correspond pas à `rtpstart`/`rtpend` dans `rtp.conf`
   - C. Le CDR est désactivé
   - D. La CLI est injoignable
4. Quels répertoires doivent être montés en tant que **volumes persistants** pour qu'un redéploiement de conteneur ne perde pas l'état ? (cochez tout ce qui s'applique)
   - A. `/var/spool/asterisk` (messagerie vocale, enregistrements)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (déjà monté par liaison depuis l'hôte)
   - D. `/usr/sbin`
5. Quelle commande CLI donne le nombre en direct d'appels actifs ?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. Dans Asterisk 22, la méthode prise en charge pour exposer les métriques d'appel/canal à une pile Prometheus/Grafana est :
   - A. Analyser le fichier journal `full`
   - B. Le module `res_prometheus.so`
   - C. Les scripts AGI
   - D. Il n'y en a pas
7. Quel est le prérequis à la fois pour le basculement HA et la mise à l'échelle horizontale sur plusieurs nœuds Asterisk ?
   - A. Exécuter en tant que root
   - B. Externaliser l'état (par exemple, les enregistrements PJSIP Realtime dans une base de données partagée)
   - C. Désactiver le CDR
   - D. Utiliser le réseau ponté
8. Quelle ressource plafonne le plus directement le nombre d'appels simultanés qu'un serveur Asterisk peut gérer ?
   - A. Le nombre d'utilisateurs enregistrés
   - B. Le traitement des médias, en particulier le transcodage
   - C. La taille de `/etc/asterisk`
   - D. Le backend CDR
9. Sur une VM cloud, quels paramètres de transport `pjsip.conf` font qu'Asterisk annonce son adresse publique pour que l'audio distant fonctionne ? (cochez tout ce qui s'applique)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Pour un déploiement cloud exposé à Internet, la règle principale du chapitre sur la sécurité est :
    - A. Toujours exécuter deux cartes réseau
    - B. Ne jamais exposer Asterisk brut à Internet ; placez un SBC (ou un proxy durci + Fail2Ban) à la périphérie
    - C. Utiliser uniquement UDP
    - D. Désactiver TLS

**Réponses :** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
