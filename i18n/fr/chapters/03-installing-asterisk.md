# Installation d'Asterisk 22

Dans le premier chapitre, nous avons appris comment Asterisk est utile dans l'environnement de la téléphonie. Dans ce chapitre, nous verrons comment télécharger et installer Asterisk. Avant de commencer, il est essentiel d'apprendre à le compiler et à l'installer. Le processus de compilation peut sembler étrange pour les utilisateurs habituels de Microsoft™ Windows™, mais il est assez courant dans l'environnement Linux™. On peut obtenir un code optimisé pour son matériel lors de la compilation d'Asterisk, ce que nous ferons ici. Asterisk fonctionne sur plusieurs systèmes d'exploitation, mais nous avons choisi de simplifier les choses en commençant par un seul d'entre eux : Linux. Nous avons choisi Debian comme distribution Linux™ car les dépendances sont faciles à installer et la distribution est stable, avec une faible empreinte mémoire. Si vous souhaitez utiliser une autre distribution, veuillez modifier le nom des dépendances en conséquence.

> **[Note 2e éd.]** Cette édition cible **Asterisk 22 LTS** (publiée en 2024, support complet jusqu'au 16/10/2028). Asterisk 22 est la version actuelle avec support à long terme. Notez que Digium a été acquis par **Sangoma** (2018), et Asterisk est désormais sponsorisé par Sangoma — les références à "Digium" tout au long de ce chapitre font référence à la marque historique pour le matériel ancien.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Déterminer les exigences matérielles pour Asterisk ;
- Installer Linux avec les dépendances requises ;
- Télécharger une version stable via HTTPS ;
- Compiler Asterisk ; et
- Apprendre à démarrer Asterisk au démarrage du système.

## Matériel minimum requis

Asterisk n'a pas besoin de beaucoup de matériel pour fonctionner, cependant il existe quelques conseils pour choisir le meilleur matériel selon vos besoins. Vous devez prendre en considération les facteurs principaux suivants lors du choix de votre matériel :

- Nombre total d'utilisateurs enregistrés. Définissez combien d'enregistrements par seconde vous devez prendre en charge.
- Nombre total d'appels simultanés. Définissez combien de conversations réseau vous devez traiter dans l'adaptateur réseau et le pont sur le serveur Asterisk.
- Quels codecs vous devez prendre en charge. Les codecs à haute complexité nécessiteront beaucoup de puissance CPU/FPU sur votre serveur ; l'iLBC, par exemple, a été mesuré par son créateur (Global IP Sound) à environ 18 MIPS par canal pour des trames de 30 ms (et environ 15 MIPS pour des trames de 20 ms) sur un DSP TI C54x.
- Annulation d'écho. L'annulation d'écho peut consommer beaucoup de CPU/FPU ; dans certains cas, vous devriez choisir une annulation d'écho matérielle utilisant des DSP sur la carte d'interface téléphonique.
- Disponibilité. Utilisez RAID1 ou 5 pour augmenter la disponibilité. N'oubliez pas qu'Asterisk est une application 24h/24 et 7j/7.

Le composant principal d'un serveur Asterisk est l'adaptateur réseau. Un bon adaptateur réseau serveur est recommandé. Le CPU est important lorsque vous devez prendre en charge des codecs à haute complexité tels que g.729 et iLBC, ainsi que l'annulation d'écho. Vous pouvez choisir d'utiliser des DSP dédiés ; Sangoma (anciennement Digium) fournit une carte DSP nommée TC400B capable de prendre en charge 120 appels g.729 simultanés. La meilleure pratique consiste à choisir un ordinateur neuf, de classe serveur, provenant d'un fabricant connu. Pour savoir exactement combien d'appels simultanés ou combien d'utilisateurs enregistrés une machine spécifique peut prendre en charge, vous devriez tester ce matériel avec un outil de test de charge tel que SIPP (http://sipp.sourceforge.net). Certains fabricants de matériel tels que Xorcom (http://www.xorcom.com) publient leurs résultats sur leur site web. Note : Certaines applications Asterisk, telles que ConfBridge et la musique d'attente, ont besoin d'une source de synchronisation interne. Sur les systèmes Linux modernes, cela est fourni automatiquement par le module intégré `res_timing_timerfd` — aucun matériel téléphonique n'est requis. (L'ancien minuteur logiciel `dahdi_dummy` n'existe plus ; sa fonctionnalité a été intégrée au module noyau principal `dahdi` dans DAHDI Linux 2.3.0.) Vous pouvez confirmer le minuteur actif avec la commande CLI `timing test`.

### Configuration matérielle

Le matériel pour Asterisk n'a pas besoin d'être sophistiqué. Vous n'avez pas besoin d'une carte vidéo coûteuse ou de nombreux périphériques. Quelques conseils sur la configuration matérielle :

- Désactivez les ports USB, série et parallèle inutilisés pour éviter la consommation d'interruptions inutiles.
- Une carte d'interface réseau robuste est essentielle.
- Soyez particulièrement vigilant si vous utilisez des cartes d'interface téléphonique. Certaines cartes utilisent un bus PCI 3,3 volts, et il n'est pas facile de trouver des cartes mères pour celles-ci. De nos jours, le PCI Express est plus facile à trouver.
- Accordez une attention particulière au disque dur ; un PBX travaille généralement en régime 24h/24 et 7j/7, tandis que les ordinateurs de bureau travaillent en 8h/5. N'utilisez pas de matériel de bureau pour un PBX, le disque dur tombe généralement en panne avant la première année. Ma recommandation est d'utiliser une machine serveur ou un appareil conçu pour exécuter des applications 24h/24 et 7j/7.

### Partage d'IRQ

Les cartes d'interface téléphonique (par ex. X100P) génèrent de grandes quantités d'interruptions. Le traitement de ces interruptions nécessite du temps processeur. Les pilotes ne peuvent pas effectuer ce traitement si un autre périphérique utilise la même interruption. Dans un système à CPU unique, vous devez éviter le partage d'IRQ entre les périphériques. Nous recommandons l'utilisation de matériel dédié pour exécuter Asterisk. N'oubliez pas de désactiver tout matériel étranger ou inutile. Certains matériels peuvent être désactivés dans la configuration du BIOS de la carte mère. Une fois que vous avez démarré votre ordinateur, consultez vos interruptions assignées dans /proc/interrupts.

```
#cat /proc/interrupts
CPU0
0: 41353058 XT-PIC timer
1: 1988 XT-PIC keyboard
2: 0 XT-PIC cascade
3: 413437739 XT-PIC wctdm <-- TDM400
4: 5721494 XT-PIC eth0
7: 413453581 XT-PIC wcfxo <-- X100P
8: 1 XT-PIC rtc
9: 413445182 XT-PIC wcfxo <-- X100P
12: 0 XT-PIC PS/2 Mouse
14: 179578 XT-PIC ide0
15: 3 XT-PIC ide1
NMI: 0
ERR: 0
```

Ici, vous pouvez voir trois cartes Digium, chacune sur sa propre IRQ. Si c'est le cas sur votre système, allez-y et installez les pilotes matériels. Si ce n'est pas le cas, revenez en arrière et essayez autre chose pour éviter le partage d'IRQ.

## Choisir une distribution Linux

Asterisk a été initialement développé pour fonctionner sous Linux. Cependant, il peut également fonctionner sous BSD Unix ou macOS. Si vous débutez avec Asterisk, essayez d'abord Linux car c'est beaucoup plus facile. Asterisk cible officiellement la famille RHEL (CentOS/RHEL/Fedora), Ubuntu et Debian. De bons choix pratiques aujourd'hui sont **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** et **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux est en fin de vie, préférez donc Rocky ou AlmaLinux sur les systèmes de la famille RHEL. Pour ce livre, j'utiliserai Ubuntu 24.04 LTS. Téléchargez la dernière image serveur 24.04 depuis le répertoire officiel des versions ci-dessous (le nom de fichier exact inclut la version mineure actuelle, par ex. `ubuntu-24.04.4-live-server-amd64.iso`) :

```
https://releases.ubuntu.com/24.04/
```

### Préparer Linux pour Asterisk

Immédiatement après l'installation d'Asterisk, nous installerons les paquets requis pour la compilation ultérieure d'Asterisk et des pilotes DAHDI. Tout d'abord, nous indiquerons à Debian d'où les paquets seront téléchargés. Cela se fait en utilisant l'utilitaire apt-setup. Étape 1 : Installez Ubuntu 24.04 LTS Server dans une machine virtuelle (utilisez l'image 64 bits ; les distributions utilisées dans ce livre sont en 64 bits, bien qu'Asterisk lui-même prenne toujours en charge le x86 32 bits). Nous avons utilisé VirtualBox pour cette formation. Vous pouvez télécharger l'image depuis https://releases.ubuntu.com/24.04. L'installation de Linux est hors du cadre de cette formation. Une connaissance de base de Linux est un prérequis pour cette formation.

## Installer Linux pour Asterisk

Installez votre Linux comme d'habitude, sans interface utilisateur graphique. Installez et configurez également le serveur de messagerie. Nous aurons besoin du serveur de messagerie (exim4) pour envoyer des notifications de messagerie vocale plus tard dans ce livre. Attention : Cette installation formatera votre PC. Toutes vos données sur le disque seront effacées. Veuillez vous assurer de sauvegarder toutes les données avant de commencer. Étape 1 : Insérez le CD dans le lecteur CD-ROM et démarrez votre PC. La plupart des questions sont très simples à répondre.

## Installer les dépendances

Pour installer Asterisk et DAHDI, vous devez installer de nombreuses dépendances logicielles. La méthode recommandée pour le faire dans Asterisk 22 est d'utiliser le script fourni avec l'arborescence source, qui connaît les noms de paquets corrects pour chaque distribution prise en charge. Après avoir téléchargé et extrait la source d'Asterisk (voir "Compiler Asterisk" ci-dessous), exécutez :

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

Étape 1 : Connectez-vous en tant que root (ou utilisez `sudo`). Étape 2 : Si vous préférez installer les dépendances manuellement sur un système Debian/Ubuntu, la liste de paquets équivalente est :

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

> **[Note 2e éd.]** La liste originale faisait référence à `subversion`, `libnewt-dev` et `libncurses5-dev`. La source d'Asterisk est désormais hébergée sur Git (subversion n'est plus nécessaire), et les systèmes Debian/Ubuntu modernes fournissent `libncurses-dev` plutôt que la version `libncurses5-dev`. Préférez `./contrib/scripts/install_prereq install` à une liste maintenue manuellement.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) est l'architecture de pilotes pour les cartes analogiques et numériques. Avant d'installer Asterisk, il est important d'installer DAHDI si vous prévoyez d'utiliser des interfaces analogiques ou numériques. DAHDI existe toujours pour les cartes de téléphonie analogique/numérique mais est de plus en plus spécialisé — la plupart des déploiements modernes sont purement VoIP et peuvent ignorer cette section entièrement. Installez DAHDI uniquement si vous disposez de matériel d'interface téléphonique physique. Obtenez les fichiers source en utilisant :

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Décompressez les fichiers en utilisant :

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiler les pilotes DAHDI

Vous devrez compiler les modules DAHDI. Les commandes ./configure et make menuselect ont été introduites il y a plusieurs années. Ce dernier vous permet de sélectionner les utilitaires et les modules à construire. Les commandes suivantes feront cela :

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

make install-config DAHDI a été configuré. Si vous avez du matériel DAHDI, il est maintenant recommandé de modifier /etc/dahdi/modules afin de charger le support uniquement pour le matériel DAHDI installé dans ce système. Par défaut, le support pour tout le matériel DAHDI est chargé au démarrage de DAHDI. Je pense que le matériel DAHDI que vous avez sur votre système est : usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware Cet écran (ci-dessus) vous demande de modifier le fichier /etc/dahdi/modules pour charger uniquement les pilotes requis pour votre configuration spécifique et afficher le matériel détecté. Modifiez le fichier /etc/dahdi/modules et chargez uniquement le matériel requis. Dans mon cas, j'utilisais une machine de test avec une Xorcom Astribank 6FXS et 2FXO. Le fichier est montré ci-dessous.

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

Réinitialisez votre ordinateur et vérifiez le chargement correct des pilotes.

## Quelle version choisir

En règle générale, vous devriez utiliser la version avec les fonctionnalités requises. Asterisk suit un modèle de publication alternant entre les versions LTS (support à long terme) et les versions standard. Au moment de cette édition, **Asterisk 22 est la version LTS actuelle** (publiée en 2024, supportée jusqu'en 2028), ce qui en fait la meilleure à choisir maintenant. Asterisk 20 est la précédente LTS, et la version 16 (utilisée dans la première édition) est en fin de vie. Pour les systèmes de production, choisissez toujours une version LTS.

> **[Note 2e éd.]** Vérifiez la version mineure actuelle exacte sur downloads.asterisk.org avant l'impression. Au moment de la rédaction, la branche 22 est la LTS active.

## Compiler Asterisk

Si vous avez déjà compilé des logiciels, compiler Asterisk sera une tâche facile. Exécutez les commandes suivantes pour compiler et installer Asterisk. N'oubliez pas que vous pouvez choisir les applications et les modules à construire en utilisant make menuselect. Étape 1 : Téléchargez le code source

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Étape 2 : Installez les prérequis de compilation (voir "Installer les dépendances" ci-dessus)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Étape 3 : Configurez la compilation

```
./configure
```

Étape 4 : Sélectionnez les modules à construire

```
make menuselect
```

Utilisez make menuselect pour installer uniquement les modules nécessaires. Dans Asterisk 22, le canal SIP est **chan_pjsip** (construit par défaut) ; l'ancien **chan_sip** a été supprimé dans Asterisk 21 et n'existe plus. Le *pass-through* Opus fonctionne immédiatement (le module `res_format_attr_opus` intégré gère la négociation SDP), mais le module de transcodage **codec_opus** est toujours un binaire externe propriétaire de Sangoma/Digium — le sélectionner dans menuselect le télécharge depuis les serveurs de Digium. Le binaire est gratuit. Voir "Sélectionner des modules avec menuselect" ci-dessous pour plus de détails.

Étape 5 : Construisez et installez Asterisk, puis créez la configuration par défaut et les fichiers d'exemple

```
make
make install
make samples
make config
ldconfig
```

`make install` installe les binaires et les modules, `make samples` écrit les fichiers de configuration d'exemple dans `/etc/asterisk`, `make config` installe le script de démarrage SysV init pour votre distribution détectée (par ex. `/etc/init.d/asterisk` sur Debian/Ubuntu), et `ldconfig` rafraîchit le cache des bibliothèques partagées. Une unité systemd est également fournie dans l'arborescence source à `contrib/systemd/asterisk.service`, mais `make config` ne l'installe pas automatiquement — copiez-la vous-même si vous préférez exécuter Asterisk sous systemd (voir ci-dessous).

### Sélectionner des modules avec menuselect

`make menuselect` ouvre un menu textuel où vous choisissez exactement quelles applications, codecs, canaux et ressources construire. Quelques notes spécifiques à Asterisk 22 :

- **chan_pjsip** (sous *Channel Drivers*) est le canal SIP moderne et est activé par défaut ; c'est le seul canal SIP dans Asterisk 22.
- **codec_opus** (sous *Codec Translators*) est un module **externe** (son entrée dans menuselect indique "Download the Opus codec from Digium") ; l'activer fait que `make` récupère le binaire gratuit et propriétaire de Sangoma/Digium. Le pass-through Opus lui-même ne nécessite aucun module supplémentaire. Le module **codec_g729** de Sangoma est également disponible — le binaire est gratuit à télécharger, mais le transcodage G.729 légal nécessite l'achat d'une licence par canal.
- Sélectionnez les formats sonores et les langues que vous souhaitez dans les menus *Core Sound Packages*, *Music On Hold File Packages* et *Extras Sound Packages* ; tout ce que vous cochez là est téléchargé et installé automatiquement pendant `make install`.

Après avoir fait vos sélections, choisissez **Save & Exit** et continuez avec `make`.

> **[Note 2e éd.]** Insérez une capture d'écran fraîche de `make menuselect` prise depuis Asterisk 22 (la capture d'écran de la 1ère édition montrait chan_sip/chan_skinny/chan_mgcp, qui n'existent plus). L'écran Channel Drivers devrait montrer chan_pjsip et aucun chan_sip.

## Démarrer et arrêter Asterisk

Avec cette configuration minimale, il est possible de démarrer Asterisk avec succès. Pour l'apprentissage et le débogage, vous pouvez démarrer Asterisk au premier plan attaché à la console :

```
/usr/sbin/asterisk –vvvgc
```

Utilisez la commande CLI stop now pour arrêter Asterisk.

```
CLI>core stop now
```

### Démarrer Asterisk avec systemd

Sur les distributions Linux modernes (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), le gestionnaire de services système est **systemd**. Asterisk fournit une unité systemd à `contrib/systemd/asterisk.service` dans l'arborescence source ; copiez-la vers `/etc/systemd/system/asterisk.service` et exécutez `systemctl daemon-reload`. Une fois installé, la méthode recommandée pour exécuter Asterisk en production est via `systemctl` :

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Une fois qu'Asterisk fonctionne en tant que service, attachez-vous à sa CLI avec `asterisk -r` (connexion) ou `asterisk -rvvv` (connexion avec sortie verbeuse).

> **[Note 2e éd.]** Sur les anciens systèmes, Asterisk était démarré via le script init SysV hérité (`/etc/init.d/asterisk`) et le wrapper **safe_asterisk**, qui redémarrait Asterisk automatiquement s'il plantait. Avec systemd, le redémarrage automatique est géré par la directive `Restart=` du fichier d'unité, donc `safe_asterisk` n'est généralement plus nécessaire. L'approche héritée init/`safe_asterisk` fonctionne toujours mais est obsolète sur les distributions basées sur systemd.

### Options d'exécution d'Asterisk

Le processus de démarrage d'Asterisk est très simple. Si Asterisk est exécuté sans aucun paramètre, il est lancé en tant que démon.

```
/sbin/asterisk
```

Vous pouvez accéder à la console Asterisk en exécutant la commande suivante. Veuillez noter que plus d'un processus de console peut être exécuté en même temps.

```
/sbin/asterisk -r
```

### Options d'exécution disponibles pour Asterisk

Vous pouvez afficher les options d'exécution disponibles en utilisant asterisk –h

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation et autres. Utilisation : asterisk [OPTIONS] Options valides : -V Affiche le numéro de version et quitte -C <configfile> Utilise un fichier de configuration alternatif -G <group> Exécute en tant que groupe autre que l'appelant -U <user> Exécute en tant qu'utilisateur autre que l'appelant -c Fournit la CLI de console -d Augmente le débogage (plusieurs d = plus de débogage) -f Ne pas forker -F Toujours forker -g Vide le core en cas de crash -h Cet écran d'aide -i Initialise les clés cryptographiques au démarrage -L <load> Limite la charge moyenne maximale avant de rejeter de nouveaux appels -M <value> Limite le nombre maximal d'appels à la valeur spécifiée -m Coupe le débogage et la sortie de console sur la console -n Désactive la colorisation de la console. Peut être utilisé uniquement au démarrage. -p Exécute en tant que thread pseudo-temps réel -q Mode silencieux (supprime la sortie) -r Se connecte à Asterisk sur cette machine -R Identique à -r, sauf qu'il tente de se reconnecter si déconnecté -s <socket> Se connecte à Asterisk via socket <socket> (valide uniquement avec -r) -t Enregistre les fichiers son dans /var/tmp et les déplace là où ils doivent être une fois terminés -T Affiche l'heure au format [Mmm dd hh:mm:ss] pour chaque ligne de sortie vers la CLI. Ne peut pas être utilisé avec le mode console distante. -v Augmente la verbosité (plusieurs v = plus verbeux) -x <cmd> Exécute la commande <cmd> (implique -r) -X Active l'utilisation de #exec dans asterisk.conf -W Ajuste les couleurs du terminal pour compenser un arrière-plan clair

## Répertoires d'installation

Asterisk est installé dans plusieurs répertoires, qui peuvent être modifiés dans le fichier asterisk.conf. À des fins de formation, je changerais la verbosité de 3 à 15, pour la production, gardez-la à 3. Les options max_calls et max_load sont de bonnes options pour protéger votre système contre la surcharge.

### asterisk.conf

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
[options]
;verbose = 3
;debug = 3
;refdebug = yes                 ; Enable reference count debug logging.
;alwaysfork = yes               ; Same as -F at startup.
;nofork = yes                   ; Same as -f at startup.
;quiet = yes                    ; Same as -q at startup.
;timestamp = yes                ; Same as -T at startup.
;execincludes = yes             ; Support #exec in config files.
;console = yes                  ; Run as console (same as -c at startup).
;highpriority = yes             ; Run realtime priority (same as -p at
                                ; startup).
;initcrypto = yes               ; Initialize crypto keys (same as -i at
                                ; startup).
;nocolor = yes                  ; Disable console colors.
;dontwarn = yes                 ; Disable some warnings.
;dumpcore = yes                 ; Dump core on crash (same as -g at startup).
;languageprefix = yes           ; Use the new sound prefix path syntax.
;systemname = my_system_name    ; Prefix uniqueid with a system name for
                                ; Global uniqueness issues.
;autosystemname = yes           ; Automatically set systemname to hostname,
                                ; uses 'localhost' on failure, or systemname if
                                ; set.
;mindtmfduration = 80           ; Set minimum DTMF duration in ms (default 80
ms)
                                ; If we get shorter DTMF messages, these will
be
                                ; changed to the minimum duration
;maxcalls = 10                  ; Maximum amount of calls allowed.
;maxload = 0.9                  ; Asterisk stops accepting new calls if the
                                ; load average exceed this limit.
;maxfiles = 1000                ; Maximum amount of openfiles.
;minmemfree = 1                 ; In MBs, Asterisk stops accepting new calls if
                                ; the amount of free memory falls below this
                                ; watermark.
;cache_media_frames = yes       ; Cache media frames for performance
                                ; Disable this option to help track down media
frame
                                ; mismanagement when using valgrind or
MALLOC_DEBUG.
                                ; The cache gets in the way of determining if
the
                                ; frame is used after being freed and who freed
it.
                                ; NOTE: This option has no effect when Asterisk
is
                                ; compiled with the LOW_MEMORY compile time
option
                                ; enabled because the cache code does not
exist.
                                ; Default yes
;cache_record_files = yes       ; Cache recorded sound files to another
                                ; directory during recording.
;record_cache_dir = /tmp        ; Specify cache directory (used in conjunction
                                ; with cache_record_files).
;transmit_silence = yes         ; Transmit silence while a channel is in a
                                ; waiting state, a recording only state, or
                                ; when DTMF is being generated.  Note that the
                                ; silence internally is generated in raw signed
                                ; linear format. This means that it must be
                                ; transcoded into the native format of the
                                ; channel before it can be sent to the device.
                                ; It is for this reason that this is optional,
                                ; as it may result in requiring a temporary
                                ; codec translation path for a channel that may
                                ; not otherwise require one.
;transcode_via_sln = yes        ; Build transcode paths via SLINEAR, instead of
                                ; directly.
;runuser = asterisk             ; The user to run as.
;rungroup = asterisk            ; The group to run as.
;lightbackground = yes          ; If your terminal is set for a light-colored
                                ; background.
;forceblackbackground = yes     ; Force the background of the terminal to be
                                ; black, in order for terminal colors to show
                                ; up properly.
;defaultlanguage = en           ; Default language
documentation_language = en_US  ; Set the language you want documentation
                                ; displayed in. Value is in the same format as
                                ; locale names.
;hideconnect = yes              ; Hide messages displayed when a remote console
                                ; connects and disconnects.
;lockconfdir = no               ; Protect the directory containing the
                                ; configuration files (/etc/asterisk) with a
                                ; lock.
;live_dangerously = no          ; Enable the execution of 'dangerous' dialplan
                                ; functions from external sources (AMI,
                                ; etc.) These functions (such as SHELL) are
                                ; considered dangerous because they can allow
                                ; privilege escalation.
                                ; Default no
;entityid=00:11:22:33:44:55     ; Entity ID.
                                ; This is in the form of a MAC address.
                                ; It should be universally unique.
                                ; It must be unique between servers
communicating
                                ; with a protocol that uses this value.
                                ; This is currently is used by DUNDi and
                                ; Exchanging Device and Mailbox State
                                ; using protocols: XMPP, Corosync and PJSIP.
;rtp_use_dynamic = yes          ; When set to "yes" RTP dynamic payload types
                                ; are assigned dynamically per RTP instance vs.
                                ; allowing Asterisk to globally initialize them
                                ; to pre-designated numbers (defaults to
"yes").
;rtp_pt_dynamic = 35            ; Normally the Dynamic RTP Payload Type numbers
                                ; are 96-127, which allow just 32 formats. The
                                ; starting point 35 enables the range 35-63 and
                                ; allows 29 additional formats. When you use
                                ; more than 32 formats in the dynamic range and
                                ; calls are not accepted by a remote
                                ; implementation, please report this and go
                                ; back to value 96.
; Changing the following lines may compromise your security.
;[files]
;astctlpermissions = 0660
;astctlowner = root
;astctlgroup = apache
;astctl = asterisk.ctl
```

## Fichiers journaux et rotation des journaux

Le PBX Asterisk enregistre ses messages dans le répertoire /var/log/asterisk. Le fichier qui contrôle les journaux

```
is the logger.conf.
;
; Logging Configuration
;
; In this file, you configure logging to files or to
; the syslog system.
;
; "logger reload" at the CLI will reload configuration
; of the logging system.
[general]
;
; Customize the display of debug message time stamps
; this example is the ISO 8601 date format (yyyy-mm-dd HH:MM:SS)
;
; see strftime(3) Linux manual for format specifiers.  Note that there is also
; a fractional second parameter which may be used in this field.  Use %1q
; for tenths, %2q for hundredths, etc.
;
;dateformat=%F %T       ; ISO 8601 date format
;dateformat=%F %T.%3q   ; with milliseconds
;
;
; This makes Asterisk write callids to log messages
; (defaults to yes)
;use_callids = no
;
; This appends the hostname to the name of the log files.
;appendhostname = yes
;
; This determines whether or not we log queue events to a file
; (defaults to yes).
;queue_log = no
;
; Determines whether the queue_log always goes to a file, even
; when a realtime backend is present (defaults to no).
;queue_log_to_file = yes
;
; Set the queue_log filename
; (defaults to queue_log)
;queue_log_name = queue_log
;
; When using realtime for the queue log, use GMT for the timestamp
; instead of localtime.  The default of this option is 'no'.
;queue_log_realtime_use_gmt = yes
;
; Log rotation strategy:
; none:  Do not perform any logrotation at all.  You should make
;        very sure to set up some external logrotate mechanism
;        as the asterisk logs can get very large, very quickly.
; sequential:  Rename archived logs in order, such that the newest
;              has the highest sequence number [default].  When
;              exec_after_rotate is set, ${filename} will specify
;              the new archived logfile.
; rotate:  Rotate all the old files, such that the oldest has the
;          highest sequence number [this is the expected behavior
;          for Unix administrators].  When exec_after_rotate is
;          set, ${filename} will specify the original root filename.
; timestamp:  Rename the logfiles using a timestamp instead of a
;             sequence number when "logger rotate" is executed.
;             When exec_after_rotate is set, ${filename} will
;             specify the new archived logfile.
;rotatestrategy = rotate
;
; Run a system command after rotating the files.  This is mainly
; useful for rotatestrategy=rotate. The example allows the last
; two archive files to remain uncompressed, but after that point,
; they are compressed on disk.
;
; exec_after_rotate=gzip -9 ${filename}.2
;
;
; For each file, specify what to log.
;
; For console logging, you set options at start of
; Asterisk with -v for verbose and -d for debug
; See 'asterisk -h' for more information.
;
; Directory for log files is configures in asterisk.conf
; option astlogdir
;
; All log messages go to a queue serviced by a single thread
; which does all the IO.  This setting controls how big that
; queue can get (and therefore how much memory is allocated)
; before new messages are discarded.
; The default is 1000
;logger_queue_limit = 250
;
;
[logfiles]
;
; Format is:
;
; logger_name => [formatter]levels
;
; The name of the logger dictates not only the name of the logging
; channel, but also its type. Valid types are:
;   - 'console'  - The root console of Asterisk
;   - 'syslog'   - Linux syslog, with facilities specified afterwards with
;                  a period delimiter, e.g., 'syslog.local0'
;   - 'filename' - The name of the log file to create. This is the default
;                  for log channels.
;
; Filenames can either be relative to the standard Asterisk log directory
; (see 'astlogdir' in asterisk.conf), or absolute paths that begin with
; '/'.
;
; An optional formatter can be specified prior to the log levels sent
; to the log channel. The formatter is defined immediately preceeding the
; levels, and is enclosed in square brackets. Valid formatters are:
;   - [default] - The default formatter, this outputs log messages using a
;                 human readable format.
;   - [json]    - Log the output in JSON. Note that JSON formatted log entries,
;                 if specified for a logger type of 'console', will be formatted
;                 per the 'default' formatter for log messages of type VERBOSE.
;                 This is due to the remote consoles intepreting verbosity
;                 outside of the logging subsystem.
;
; Log levels include the following, and are specified in a comma delineated
; list:
;    debug
;    notice
;    warning
;    error
;    verbose(<level>)
;    dtmf
;    fax
;    security
;
; Verbose takes an optional argument, in the form of an integer level.
; Verbose messages with higher levels will not be logged to the file.  If
; the verbose level is not specified, it will log verbose messages following
; the current level of the root console.
;
; Special level name "*" means all levels, even dynamic levels registered
; by modules after the logger has been initialized (this means that loading
; and unloading modules that create/remove dynamic logger levels will result
; in these levels being included on filenames that have a level name of "*",
; without any need to perform a 'logger reload' or similar operation).
; Note that there is no value in specifying both "*" and specific level names
; for a filename; the "*" level means all levels.  The only exception is if
; you need to specify a specific verbose level. e.g, "verbose(3),*".
;
; We highly recommend that you DO NOT turn on debug mode if you are simply
; running a production system.  Debug mode turns on a LOT of extra messages,
; most of which you are unlikely to understand without an understanding of
; the underlying code.  Do NOT report debug messages as code issues, unless
; you have a specific issue that you are attempting to debug.  They are
; messages for just that -- debugging -- and do not rise to the level of
; something that merit your attention as an Asterisk administrator.  Debug
; messages are also very verbose and can and do fill up logfiles quickly;
; this is another reason not to have debug mode on a production system unless
; you are in the process of debugging a specific issue.
;
;debug => debug
;security => security
console => notice,warning,error
;console => notice,warning,error,debug
messages => notice,warning,error
;full => notice,warning,error,debug,verbose,dtmf,fax
;
;full-json => [json]debug,verbose,notice,warning,error,dtmf,fax
;
;syslog keyword : This special keyword logs to syslog facility
;
;syslog.local0 => notice,warning,error
```

; Certaines commandes de console sont associées au processus logger.

```
CLI> logger show channels
Logger queue limit: 1000

Channel                             Type     Formatter  Status    Configuration
-------                             ----     ---------  ------    -------------
/var/log/asterisk/security          File     default    Enabled    - SECURITY
/var/log/asterisk/full              File     default    Enabled    - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages          File     default    Enabled    - NOTICE WARNING ERROR
CLI> logger rotate
  == Parsing '/etc/asterisk/logger.conf': Found
Asterisk Event Logger restarted
Asterisk Queue Logger restarted
You can control the log rotation using the logrotate daemon. Edit the file
/etc/logrotate.d and include the content below to start rotating the log files.
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

Plus d'informations sur logrotate peuvent être obtenues en utilisant :

```
#man logrotate
```

## Désinstaller Asterisk

Pour désinstaller Asterisk, utilisez :

```
make uninstall
```

Pour désinstaller Asterisk et tous les fichiers de configuration, utilisez :

```
make uninstall-all
```

## Notes d'installation d'Asterisk

Cette section fournira quelques conseils sur les problèmes à résoudre avant d'installer Asterisk.

### Systèmes de production

Si Asterisk est installé dans un environnement de production, vous devez faire attention à la conception du système. Un serveur doit être optimisé de telle manière que les systèmes de téléphonie aient la priorité sur les autres processus système. Asterisk ne devrait pas fonctionner avec des logiciels intensifs en processeur tels que X-Windows. Si vous devez exécuter des processus intensifs en CPU (par ex. une énorme base de données), utilisez un serveur séparé. De manière générale, Asterisk est sensible aux variations de performance matérielle. Ainsi, essayez d'utiliser Asterisk dans un environnement matériel qui ne nécessite pas plus de 40 % d'utilisation du CPU.

### Conseils réseau

Si vous prévoyez d'utiliser des téléphones IP, il est important que vous prêtiez attention à votre réseau. Les protocoles vocaux sont très bons et résistants à la latence et même à la gigue ; cependant, si vous utilisez un réseau local mal configuré, la qualité vocale en souffrira. Il n'est possible de garantir une bonne qualité vocale qu'en utilisant la qualité de service (QoS) dans les commutateurs et les routeurs. La voix dans un réseau local a tendance à être bonne, mais même dans un environnement LAN, si vous avez des hubs 10 Mbps avec trop de collisions, vous finirez par avoir une voix déformée ou médiocre. Suivez ces recommandations pour garantir la meilleure qualité vocale possible :

- Utilisez la QoS de bout en bout si possible ou économiquement réalisable. Avec la QoS de bout en bout, la qualité vocale est parfaite. Pas d'excuses !
- Évitez d'utiliser des hubs 10/100 Mbps pour la voix dans un environnement de production. Les collisions peuvent imposer de la gigue sur le réseau. Le 10/100 Mbps full duplex est préférable car aucune collision ne se produit.
- Utilisez des VLAN pour séparer les diffusions inutiles du réseau vocal. Vous ne voulez pas qu'un virus détruise votre réseau vocal avec des diffusions ARP.
- Éduquez les utilisateurs sur les attentes dans un réseau vocal. Sans QoS, ne dites pas que la voix sera parfaite car dans la plupart des cas, elle ne le sera pas. Une qualité de voix similaire à celle d'un téléphone mobile sera le plus souvent atteinte. Utilisez des téléphones de qualité car les problèmes de firmware et de conception matérielle sont courants.

## Résumé

Dans ce chapitre, vous avez appris les exigences matérielles minimales ainsi que comment télécharger, installer et compiler Asterisk. Asterisk devrait être exécuté avec un utilisateur non-root pour des raisons de sécurité. Vous devriez vérifier votre environnement réseau avant de démarrer l'environnement de production.

## Quiz

1. Dans Asterisk 22, quel pilote de canal fournit le support SIP, et qu'est-il arrivé à l'ancien `chan_sip` ?
   - A. `chan_sip` est toujours le défaut ; `chan_pjsip` est optionnel.
   - B. `chan_pjsip` est le canal SIP par défaut ; `chan_sip` a été supprimé dans Asterisk 21 et n'existe plus.
   - C. Les deux sont construits par défaut et vous choisissez entre eux au moment de l'exécution.
   - D. Le support SIP a été entièrement supprimé au profit d'IAX2.
2. Les cartes d'interface téléphonique pour Asterisk ont généralement des processeurs de signal numérique (DSP) intégrés et n'ont donc pas besoin de beaucoup de CPU de la part du PC.
   - A. Vrai
   - B. Faux
3. Si vous voulez une qualité vocale parfaite, vous devez implémenter une qualité de service (QoS) de bout en bout.
   - A. Vrai
   - B. Faux
4. Vous devriez toujours choisir la dernière version d'Asterisk, car c'est la plus stable.
   - A. Vrai
   - B. Faux
5. Quelle est la méthode recommandée pour installer les dépendances de compilation pour Asterisk 22 ?
6. Si vous n'avez pas de carte d'interface TDM, vous aurez toujours une source de synchronisation interne, fournie par le module `res_timing_timerfd` sur Linux. Cette synchronisation est utilisée par des applications telles que ________ et ________.
7. Lors de l'installation d'Asterisk, il est préférable de laisser de côté les environnements de bureau tels que GNOME ou KDE, car les interfaces graphiques consomment des cycles CPU.
   - A. Vrai
   - B. Faux
8. Les fichiers de configuration d'Asterisk sont situés dans le répertoire ________.
9. Pour installer les fichiers de configuration d'exemple d'Asterisk, tapez la commande : ________
10. Pourquoi est-il important d'exécuter Asterisk en tant qu'utilisateur non-root ?

**Réponses :** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Exécutez `./contrib/scripts/install_prereq install` depuis l'arborescence source d'Asterisk extraite · 6 — ConfBridge et Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Sécurité (limite les dégâts si Asterisk est compromis)
