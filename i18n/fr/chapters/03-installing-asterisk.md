# Installing Asterisk 22

Dans le premier chapitre, nous avons appris un peu comment Asterisk est utile dans l’environnement téléphonique. Dans ce chapitre, nous couvrirons comment télécharger et installer Asterisk. Avant de commencer, il est essentiel d’apprendre comment le compiler et l’installer. Le processus de compilation peut sembler étrange pour les utilisateurs traditionnels de Microsoft™ Windows™ , mais il est assez courant dans l’environnement Linux™. On peut obtenir un code optimisé pour votre matériel lors de la compilation d’Asterisk, ce que nous ferons ici. Asterisk fonctionne sur plusieurs systèmes d’exploitation, mais nous garderons les choses simples et n’utiliserons qu’un seul : Linux. Nous utilisons **Ubuntu 24.04 LTS** parce que ses dépendances sont faciles à installer et c’est une distribution serveur stable, bien supportée et à faible empreinte. Si vous préférez une autre distribution, ajustez les noms de paquets en conséquence.

Cette édition cible **Asterisk 22 LTS** (publié le 2024-10-16 ; support complet jusqu’au 2028-10-16, correctifs de sécurité jusqu’au 2029-10-16). Asterisk 22 est la version actuelle à support à long terme. Notez que Digium a été acquis par **Sangoma** en 2018, et Asterisk est maintenant sponsorisé par Sangoma — les références à « Digium » tout au long de ce chapitre renvoient à la marque historique pour le matériel.

## Objectives

By the end of this chapter you should be able to:

- Determine the hardware requirements for Asterisk;
- Install Linux with the required dependencies;
- Download a stable version over HTTPS;
- Compile Asterisk; and
- Learn how to start Asterisk at boot time.

## Minimum Hardware Required

Asterisk ne nécessite pas beaucoup de matériel pour fonctionner, cependant il existe quelques conseils pour choisir le meilleur matériel selon vos besoins. Vous devez prendre en compte les facteurs principaux suivants lors du choix de votre matériel :

- Nombre total d'utilisateurs enregistrés. Définissez combien d'enregistrements par seconde vous devez supporter
- Nombre total d'appels simultanés. Définissez combien de conversations réseau vous devez traiter dans l'adaptateur réseau et le pont sur le serveur Asterisk
- Quels codecs vous devez supporter. Les codecs à haute complexité nécessiteront beaucoup de puissance CPU/FPU sur votre serveur ; iLBC, par exemple, a été mesuré par son créateur (Global IP Sound) à environ 18 MIPS par canal pour des trames de 30 ms (et environ 15 MIPS pour des trames de 20 ms) sur un DSP TI C54x
- Annulation d'écho. L'annulation d'écho peut consommer beaucoup de CPU/FPU, dans certains cas vous devriez choisir une annulation d'écho matérielle utilisant des DSP dans la carte d'interface téléphonique
- Disponibilité. Utilisez RAID1 ou 5 pour augmenter la disponibilité. Rappelez‑vous, Asterisk est une application 24x7.

Le composant principal d’un serveur Asterisk est l’adaptateur réseau. Un bon adaptateur réseau serveur est recommandé. Le CPU est important lorsque vous devez supporter des codecs à haute complexité tels que g.729 et iLBC ainsi que l'annulation d'écho. Vous pouvez choisir de déléguer cela à des DSP dédiés : Sangoma (anciennement Digium) fournit une carte DSP nommée TC400B capable de supporter 120 appels simultanés G.729.

La meilleure pratique consiste à choisir un ordinateur de classe serveur, neuf, d’un fabricant connu. Pour savoir exactement combien d’appels simultanés ou combien d’utilisateurs enregistrés une machine spécifique peut supporter, vous devez tester ce matériel avec un outil de test de charge tel que SIPP (http://sipp.sourceforge.net). Certains fabricants de matériel comme Xorcom (http://www.xorcom.com) publient leurs résultats sur le site web.

Note : Certaines applications Asterisk, telles que ConfBridge et la musique d’attente, nécessitent une source de timing interne. Sous Linux moderne, cela est fourni automatiquement par le module intégré `res_timing_timerfd` — aucun matériel téléphonique n’est requis. (L’ancien minuteur logiciel `dahdi_dummy` n’existe plus ; ses fonctionnalités ont été intégrées dans le module noyau principal `dahdi` sous DAHDI Linux 2.3.0.) Vous pouvez confirmer le minuteur actif avec la commande CLI `timing test`.

### Hardware configuration

Le matériel Asterisk n’a pas besoin d’être sophistiqué. Vous n’avez pas besoin d’une carte vidéo coûteuse ou de nombreux périphériques. Quelques conseils concernant la configuration matérielle :

- Désactivez les ports USB, série et parallèle inutilisés afin d’éviter la consommation d’interruptions inutiles.
- Une carte d’interface réseau robuste est essentielle.
- Soyez particulièrement vigilant si vous utilisez des cartes d’interface téléphonique. Certaines cartes utilisent un bus PCI de 3,3 volts, et il n’est pas facile de trouver des cartes mères compatibles. De nos jours, le PCI‑Express est plus facilement disponible.
- Portez une attention particulière au disque dur, le PBX fonctionnant en régime 24x7 alors que les postes de travail fonctionnent 8x5. N’utilisez pas de matériel de bureau pour un PBX, généralement le disque dur tombe en panne avant la première année. Ma recommandation est d’utiliser une machine serveur ou un appliance conçu pour exécuter des applications 24x7.

### IRQ sharing (legacy PCI cards only)

Cette préoccupation s’applique **uniquement** si vous installez des cartes téléphoniques PCI/PCI‑Express physiques (matériel DAHDI). Ces cartes génèrent un grand nombre d’interruptions, et sur les anciens systèmes à processeur unique, partager une ligne IRQ avec un autre dispositif pourrait priver le pilote de ressources et dégrader la qualité vocale. Si vous utilisez des cartes téléphoniques, dédiez la machine à Asterisk, désactivez tout dispositif intégré inutilisé dans le BIOS, et vérifiez les interruptions assignées avec `cat /proc/interrupts`. Les serveurs modernes multi‑cœurs utilisant des interruptions MSI/MSI‑X rendent le partage d’IRQ un problème inexistant en pratique, et un déploiement pure‑VoIP (sans cartes) n’a pas besoin de s’en préoccuper.

## Choosing a Linux distribution

Asterisk a été initialement développé pour fonctionner sous Linux. Cependant, il peut également fonctionner sous BSD Unix ou macOS. Si vous êtes nouveau avec Asterisk, essayez d’utiliser Linux d’abord car c’est beaucoup plus simple. Asterisk cible officiellement les familles RHEL (CentOS/RHEL/Fedora), Ubuntu et Debian. Les bons choix pratiques aujourd’hui sont **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, et **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux est en fin de vie, donc privilégiez Rocky ou AlmaLinux sur les systèmes de la famille RHEL. Pour ce livre, j’utiliserai Ubuntu 24.04 LTS. Téléchargez l’image serveur du dernier point‑release 24.04 depuis le répertoire officiel des releases ci‑dessous (le nom exact du fichier comprend le point‑release actuel, par ex. `ubuntu-24.04.4-live-server-amd64.iso`) :

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Avant de compiler Asterisk, vous avez besoin d’un système Linux fonctionnel avec les paquets de construction installés. Installez **Ubuntu 24.04 LTS Server** dans une machine virtuelle ou sur une boîte dédiée (utilisez l’image 64 bits ; tout dans ce livre est 64 bits, bien qu’Asterisk supporte encore le 32 bits x86). Nous avons utilisé VirtualBox pour cette formation ; vous pouvez télécharger l’image depuis <https://releases.ubuntu.com/24.04>. L’installation de Linux elle‑même dépasse le cadre de ce livre — des connaissances de base en Linux sont une condition préalable. Une fois Linux installé, vous ajouterez les dépendances de construction d’Asterisk (voir *Installing dependencies* ci‑dessous) puis compilerez Asterisk.

## Installation de Linux pour Asterisk

Installez Linux comme d'habitude, sans environnement de bureau graphique. Pendant l'installation, activez également un agent de transfert de courrier (nous utilisons **exim4**) — Asterisk en aura besoin pour envoyer les notifications de messagerie vocale par e‑mail plus tard dans ce livre. **Attention:** l'installation d'un système d'exploitation efface le disque cible. Si vous installez sur du matériel physique, sauvegardez d'abord vos données ; installer dans une machine virtuelle laisse votre hôte intact. Démarrez l'installateur depuis l'ISO Ubuntu Server (ou le lecteur optique virtuel de la VM) et répondez aux invites — la plupart sont simples.

## Installing dependencies

Pour installer Asterisk et DAHDI, vous devez installer de nombreuses dépendances logicielles. La méthode recommandée pour cela dans Asterisk 22 est d’utiliser le script fourni avec l’arbre source, qui connaît les noms de paquets corrects pour chaque distribution prise en charge. Après avoir téléchargé et extrait les sources d’Asterisk (voir « Compiling Asterisk » ci‑dessous), exécutez :

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Connectez‑vous en tant que root (ou utilisez `sudo`).
2. Si vous préférez installer les dépendances manuellement sur un système Debian/Ubuntu, la liste de paquets équivalente est :

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Notez que les sources d’Asterisk sont maintenant hébergées sur Git, donc `subversion` n’est plus nécessaire, et les versions récentes de Debian/Ubuntu livrent `libncurses-dev` plutôt que le `libncurses5-dev` versionné. Privilégiez `./contrib/scripts/install_prereq install` plutôt qu’une liste maintenue manuellement, car le script suit toujours les noms de paquets corrects pour votre distribution.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) est l’architecture des pilotes pour les cartes analogiques et numériques. Avant d’installer Asterisk, il est important d’installer DAHDI si vous prévoyez d’utiliser des interfaces analogiques ou numériques. DAHDI existe encore pour les cartes téléphoniques analogiques/numériques mais devient de plus en plus marginal — la plupart des déploiements modernes sont purement VoIP et peuvent ignorer complètement cette section. Installez DAHDI uniquement si vous disposez de matériel d’interface téléphonique physique. Récupérez les fichiers sources avec :

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Décompressez les fichiers avec :

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

Vous devrez compiler les modules DAHDI. Les commandes ./configure et make menuselect ont été introduites il y a plusieurs années. Cette dernière vous permet de choisir les utilitaires et modules à construire. Les commandes suivantes accompliront cela :

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config DAHDI a été configuré. Si vous avez du matériel DAHDI, il est maintenant recommandé de modifier /etc/dahdi/modules afin de ne charger que le matériel DAHDI installé sur ce système. Par défaut, le support de tout le matériel DAHDI est chargé au démarrage de DAHDI. Je pense que le matériel DAHDI présent sur votre système est : usb:004/002 xpp_usb‑ e4e4:1150 Astribank‑multi no‑firmware Cet écran (ci‑dessus) vous demande de modifier le fichier /etc/dahdi/modules pour ne charger que les pilotes requis pour votre configuration spécifique et afficher le matériel détecté. Modifiez le fichier /etc/dahdi/modules et ne chargez que le matériel requis. Dans mon cas, j’utilisais une machine de test avec un Xorcom Astribank 6FXS et 2FXO. Le fichier est présenté ci‑dessous.

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

Ré‑initialisez votre ordinateur et vérifiez le chargement correct des pilotes.

## Which version to choose

En règle générale, vous devez utiliser la version qui possède les fonctionnalités requises. Asterisk suit un modèle de publication alternant les versions LTS (support à long terme) et les versions standard. Au moment de cette édition, **Asterisk 22 est la version LTS actuelle** (publiée en octobre 2024 ; la dernière version point est 22.10.0), ce qui en fait la meilleure à choisir maintenant. Asterisk 20 est la LTS précédente, et la version 16 (utilisée dans la première édition) est en fin de vie. Pour les systèmes de production, choisissez toujours une version LTS.

## Compilation d'Asterisk

Si vous avez déjà compilé des logiciels, compiler Asterisk sera une tâche facile. Exécutez les commandes suivantes pour compiler et installer Asterisk. N'oubliez pas que vous pouvez choisir les applications et modules à construire avec **make menuselect**. Étape 1 : Télécharger le code source

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Étape 2 : Installer les prérequis de compilation (voir « Installation des dépendances » plus haut)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Étape 3 : Configurer la compilation

```
./configure
```

Étape 4 : Sélectionner les modules à construire

```
make menuselect
```

Utilisez **make menuselect** pour n'installer que les modules nécessaires. Dans Asterisk 22, le canal SIP est **chan_pjsip** (activé par défaut) ; l’ancien **chan_sip** a été supprimé dans Asterisk 21 et n’existe plus. Le *pass‑through* Opus fonctionne immédiatement (le module intégré `res_format_attr_opus` gère la négociation SDP), mais le module de transcodage **codec_opus** reste un binaire externe, propriétaire, fourni par Sangoma/Digium — le sélectionner dans menuselect le télécharge depuis les serveurs de Digium. Le binaire est gratuit. Voir la section « Sélection des modules avec menuselect » ci‑dessous pour plus de détails.

Étape 5 : Construire et installer Asterisk, puis créer la configuration par défaut et les fichiers d’exemple

```
make
make install
make samples
make config
ldconfig
```

`make install` installe les exécutables et modules, `make samples` écrit les fichiers de configuration d’exemple dans `/etc/asterisk`, `make config` installe le script de démarrage SysV init pour votre distribution détectée (par ex. `/etc/init.d/asterisk` sur Debian/Ubuntu), et `ldconfig` rafraîchit le cache des bibliothèques partagées. Une unité systemd est également fournie dans l’arbre source à `contrib/systemd/asterisk.service`, mais `make config` ne l’installe pas automatiquement — copiez‑la vous‑même si vous préférez exécuter Asterisk sous systemd (voir ci‑après).

### Sélection des modules avec menuselect

`make menuselect` ouvre un menu texte où vous choisissez exactement quelles applications, codecs, canaux et ressources compiler. Quelques notes spécifiques à Asterisk 22 :

- **chan_pjsip** (dans *Channel Drivers*) est le canal SIP moderne et est activé par défaut ; c’est le seul canal SIP dans Asterisk 22.
- **codec_opus** (dans *Codec Translators*) est un module **externe** (son entrée menuselect indique « Download the Opus codec from Digium ») ; l’activer fait que `make` récupère le binaire gratuit et propriétaire de Sangoma/Digium. Le *pass‑through* Opus ne nécessite aucun module supplémentaire. Le module **codec_g729** de Sangoma est également disponible — le binaire est téléchargeable gratuitement, mais le transcodage légal du G.729 requiert une licence par canal achetée.
- Sélectionnez les formats sonores et les langues souhaités dans les menus *Core Sound Packages*, *Music On Hold File Packages* et *Extras Sound Packages* ; tout ce que vous cochez sera téléchargé et installé automatiquement pendant `make install`.

Après avoir fait vos sélections, choisissez **Save & Exit** et continuez avec `make`.

## Démarrage et arrêt d'Asterisk

Avec cette configuration minimale, il est possible de démarrer Asterisk avec succès. Pour l'apprentissage et le débogage, vous pouvez lancer Asterisk au premier plan, attaché à la console :

```
/usr/sbin/asterisk -vvvgc
```

Utilisez la commande CLI `core stop now` pour arrêter Asterisk :

```
*CLI> core stop now
```

### Démarrage d'Asterisk avec systemd

Sur les distributions Linux modernes (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), le gestionnaire de services système est **systemd**. Asterisk fournit une unité systemd à `contrib/systemd/asterisk.service` dans l'arborescence des sources ; copiez‑la vers `/etc/systemd/system/asterisk.service` et exécutez `systemctl daemon-reload`. Une fois installée, la méthode recommandée pour exécuter Asterisk en production est via `systemctl` :

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Une fois qu'Asterisk fonctionne en tant que service, attachez‑vous à son CLI avec `asterisk -r` (connect) ou `asterisk -rvvv` (connect with verbose output).

Sur les systèmes plus anciens, Asterisk était démarré via le script d'initialisation SysV hérité (`/etc/init.d/asterisk`) et le wrapper **safe_asterisk**, qui redémarrait automatiquement Asterisk en cas de plantage. Avec systemd, le redémarrage automatique est géré par la directive `Restart=` du fichier d'unité, de sorte que `safe_asterisk` n'est généralement plus nécessaire. L'approche legacy init/`safe_asterisk` fonctionne toujours mais est dépréciée sur les distributions basées sur systemd.

### Options d'exécution d'Asterisk

Le processus de démarrage d'Asterisk est très simple. Si Asterisk est lancé sans aucun paramètre, il démarre en tant que démon.

```
/sbin/asterisk
```

Vous pouvez accéder à la console d'Asterisk en exécutant la commande suivante. Veuillez noter que plusieurs processus de console peuvent être exécutés simultanément.

```
/sbin/asterisk -r
```

### Options d'exécution disponibles pour Asterisk

Vous pouvez afficher les options d'exécution disponibles en utilisant `asterisk -h`

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## Répertoires d'installation

Asterisk est installé dans plusieurs répertoires, qui peuvent être modifiés dans le fichier asterisk.conf. À des fins de formation, je modifierais le niveau de verbosité de 3 à 15, tandis qu'en production il faut le laisser à 3. Les options `maxcalls` et `maxload` sont de bonnes options pour protéger votre système contre la surcharge.

### asterisk.conf (extrait)

La section `[directories]` définit où Asterisk conserve sa configuration, ses modules, ses données, son spool et ses journaux :

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
```

La section `[options]` contient les réglages d'exécution. Les options les plus utiles à connaître sont présentées ci‑dessous (décommentez pour activer) ; le fichier est fourni avec de nombreuses autres, chacune documentée par un commentaire en ligne :

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## Log files and log rotation

Asterisk PBX logs its messages in `/var/log/asterisk`. Logging is controlled by `logger.conf`. The key part is the `[logfiles]` section, where each line defines a log channel and the message levels it captures (excerpt):

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

After editing, apply the change with `logger reload` and confirm the channels with `logger show channels`:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

The log files can grow quickly, so rotate them with the system `logrotate` daemon — add a file under `/etc/logrotate.d/`:

```text
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

More information about logrotate can be obtained using:

```
#man logrotate
```

## Désinstallation d'Asterisk

Pour désinstaller Asterisk, utilisez :

```
make uninstall
```

Pour désinstaller Asterisk ainsi que tous les fichiers de configuration, utilisez :

```
make uninstall-all
```

## Asterisk installation notes

Cette section fournira quelques conseils sur les problèmes à résoudre avant d’installer Asterisk.

### Production Systems

Si Asterisk est installé dans un environnement de production, vous devez prêter attention à la conception du système. Un serveur doit être optimisé de manière à ce que les systèmes de téléphonie aient la priorité sur les autres processus du système. Asterisk ne doit pas fonctionner conjointement avec des logiciels gourmands en processeur tels que X-Windows. Si vous devez exécuter des processus intensifs en CPU (par exemple, une base de données volumineuse), utilisez un serveur séparé. De façon générale, Asterisk est sensible aux variations de performance du matériel. Ainsi, essayez d’utiliser Asterisk dans un environnement matériel qui ne nécessite pas plus de 40 % d’utilisation du CPU.

### Network Tips

Si vous prévoyez d’utiliser des téléphones IP, il est important de prêter attention à votre réseau. Les protocoles voix sont très bons et résistants à la latence et même aux jitter ; cependant, si vous utilisez un réseau local mal configuré, la qualité de la voix en pâtira. Il n’est possible de garantir une bonne qualité de voix qu’en utilisant la qualité de service (QoS) dans les commutateurs et routeurs. La voix sur un réseau local a tendance à être bonne, mais même dans un environnement LAN, si vous avez des hubs 10 Mbps avec trop de collisions, vous finirez par obtenir une voix déformée ou médiocre. Suivez ces recommandations pour assurer la meilleure qualité de voix possible :

- Utilisez la QoS de bout en bout si possible ou économiquement viable. Avec la QoS de bout en bout, la qualité de la voix est parfaite. Aucun excuse !
- Évitez d’utiliser des hubs 10/100 Mbps pour la voix dans un environnement de production. Les collisions peuvent imposer des jitter sur le réseau. Les 10/100 Mbps full duplex sont préférés car aucune collision ne se produit.
- Utilisez des VLANs pour séparer les diffusions inutiles du réseau voix. Vous ne voulez pas qu’un virus détruise votre réseau voix avec des diffusions ARP.
- Sensibilisez les utilisateurs aux attentes dans un réseau voix. Sans QoS, ne prétendez pas que la voix sera parfaite car dans la plupart des cas elle ne le sera pas. Une qualité de voix similaire à celle d’un téléphone mobile sera le plus souvent atteinte. Utilisez des téléphones de qualité car les problèmes de firmware et de conception matérielle sont courants.

## Résumé

Dans ce chapitre, vous avez appris les exigences matérielles minimales ainsi que la façon de télécharger, installer et compiler Asterisk. Asterisk doit être exécuté avec un utilisateur non root pour des raisons de sécurité. Vous devez vérifier votre environnement réseau avant de lancer l’environnement de production.

## Quiz

1. In Asterisk 22, which channel driver provides SIP support, and what happened to the older `chan_sip`?
   - A. `chan_sip` is still the default; `chan_pjsip` is optional.
   - B. `chan_pjsip` is the default SIP channel; `chan_sip` was removed in Asterisk 21 and no longer exists.
   - C. Both are built by default and you choose between them at runtime.
   - D. SIP support was removed entirely in favor of IAX2.
2. Telephony interface cards for Asterisk usually have Digital Signal Processors (DSPs) built in and so do not need much CPU from the PC.
   - A. True
   - B. False
3. If you want perfect voice quality, you need to implement end-to-end quality of service (QoS).
   - A. True
   - B. False
4. You should always choose the latest Asterisk version, as it is the most stable.
   - A. True
   - B. False
5. What is the recommended way to install the build dependencies for Asterisk 22?
6. If you don't have a TDM interface card you will still have an internal timing source for synchronization, provided by the `res_timing_timerfd` module on Linux. This timing is used by applications such as ________ and ________.
7. When installing Asterisk it is better to leave desktop environments such as GNOME or KDE out, because graphical interfaces consume CPU cycles.
   - A. True
   - B. False
8. Asterisk configuration files are located in the ________ directory.
9. To install the Asterisk sample configuration files, type the command: ________
10. Why is it important to run Asterisk as a non-root user?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
