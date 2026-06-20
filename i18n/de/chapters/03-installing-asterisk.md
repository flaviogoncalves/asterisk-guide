# Installing Asterisk 22

Im ersten Kapitel haben wir ein wenig darüber gelernt, wie Asterisk in der Telefonieumgebung nützlich ist. In diesem Kapitel behandeln wir, wie man Asterisk herunterlädt und installiert. Vor dem Start ist es wichtig zu wissen, wie man es kompiliert und installiert. Der Kompilierungsprozess mag für traditionelle Microsoft™ Windows™‑Benutzer seltsam erscheinen, ist aber in der Linux™‑Umgebung ziemlich üblich. Beim Kompilieren von Asterisk kann man einen für die eigene Hardware optimierten Code erhalten, was wir hier tun werden. Asterisk läuft auf mehreren Betriebssystemen, aber wir halten es einfach und verwenden nur eines: Linux. Wir benutzen **Ubuntu 24.04 LTS**, weil seine Abhängigkeiten leicht zu installieren sind und es eine stabile, gut unterstützte Server‑Distribution mit geringem Ressourcenverbrauch ist. Wenn Sie eine andere Distribution bevorzugen, passen Sie die Paketnamen entsprechend an.

Diese Ausgabe richtet sich an **Asterisk 22 LTS** (veröffentlicht am 2024-10-16; voller Support bis 2028-10-16, Sicherheitsupdates bis 2029-10-16). Asterisk 22 ist die aktuelle Long‑Term‑Support‑Version. Beachten Sie, dass Digium 2018 von **Sangoma** übernommen wurde und Asterisk nun von Sangoma gesponsert wird – Verweise auf „Digium“ in diesem Kapitel beziehen sich auf die frühere Marke für historische Hardware.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die Hardware-Anforderungen für Asterisk zu bestimmen;
- Linux mit den erforderlichen Abhängigkeiten zu installieren;
- Eine stabile Version über HTTPS herunterzuladen;
- Asterisk zu kompilieren; und
- Zu lernen, wie man Asterisk beim Systemstart startet.

## Minimum Hardware Required

Asterisk benötigt nicht viel Hardware zum Betrieb, jedoch gibt es einige Hinweise, um die beste Hardware für Ihre Anforderungen auszuwählen. Sie sollten die folgenden Hauptfaktoren bei der Auswahl Ihrer Hardware berücksichtigen:

- Gesamtzahl der registrierten Benutzer. Definieren Sie, wie viele Registrierungen pro Sekunde Sie unterstützen müssen
- Gesamtzahl gleichzeitiger Anrufe. Definieren Sie, wie viele Netzwerkgespräche Sie im Netzwerkadapter und in der Bridge auf dem Asterisk‑Server verarbeiten müssen
- Welche Codecs Sie unterstützen müssen. Codecs mit hoher Komplexität erfordern viel CPU/FPU‑Leistung in Ihrem Server; iLBC wurde beispielsweise von seinem Erfinder (Global IP Sound) mit etwa 18 MIPS pro Kanal für 30 ms‑Frames (und etwa 15 MIPS für 20 ms‑Frames) auf einem TI C54x DSP gemessen
- Echo‑Unterdrückung. Echo‑Unterdrückung kann viel CPU/FPU beanspruchen, in manchen Fällen sollten Sie hardwarebasierte Echo‑Unterdrückung mit DSPs in der Telefonie‑Schnittstellenkarte wählen
- Verfügbarkeit. Verwenden Sie RAID1 oder 5, um die Verfügbarkeit zu erhöhen. Denken Sie daran, dass Asterisk eine 24x7‑Anwendung ist.

Die Hauptkomponente für einen Asterisk‑Server ist der Netzwerkadapter. Ein guter Server‑Netzwerkadapter wird empfohlen. Die CPU ist wichtig, wenn Sie Codecs mit hoher Komplexität wie g.729 und iLBC sowie Echo‑Unterdrückung unterstützen müssen. Sie können dies auf dedizierte DSPs auslagern: Sangoma (früher Digium) bietet eine DSP‑Karte namens TC400B, die 120 gleichzeitige G.729‑Anrufe unterstützen kann.

Die bewährte Vorgehensweise ist, einen neuen, serverklassigen Computer von einem bekannten Hersteller zu wählen. Um genau zu wissen, wie viele gleichzeitige Anrufe oder wie viele registrierte Benutzer eine bestimmte Maschine unterstützen kann, sollten Sie diese Hardware mit einem Stresstest‑Tool wie SIPP (http://sipp.sourceforge.net) testen. Einige Hardware‑Hersteller wie Xorcom (http://www.xorcom.com) veröffentlichen ihre Ergebnisse auf der Website.

Hinweis: Einige Asterisk‑Anwendungen, wie ConfBridge und Music on Hold, benötigen eine interne Zeitquelle. Auf modernen Linux‑Systemen wird diese automatisch vom eingebauten `res_timing_timerfd`‑Modul bereitgestellt – es wird keine Telefonie‑Hardware benötigt. (Der alte `dahdi_dummy`‑Software‑Timer existiert nicht mehr; seine Funktionalität wurde in das Haupt‑`dahdi`‑Kernelmodul in DAHDI Linux 2.3.0 integriert.) Sie können den aktiven Timer mit dem CLI‑Befehl `timing test` bestätigen.

### Hardware configuration

Die Asterisk‑Hardware muss nicht besonders anspruchsvoll sein. Sie benötigen keine teure Grafikkarte oder zahlreiche Peripheriegeräte. Einige Hinweise zur Hardware‑Konfiguration:

- Deaktivieren Sie ungenutzte USB-, seriellen und Parallelanschlüsse, um unnötige Interrupts zu vermeiden.
- Eine robuste Netzwerkschnittstellenkarte ist essenziell.
- Achten Sie besonders, wenn Sie Telefonie‑Schnittstellenkarten verwenden. Einige Karten nutzen einen 3,3‑Volt‑PCI‑Bus, und es ist nicht einfach, dafür Motherboards zu finden. Heutzutage ist PCI‑Express leichter zu bekommen.
- Achten Sie genau auf die Festplatte, PBX‑Systeme arbeiten im 24x7‑Betrieb, während Desktop‑Computer 8x5 laufen. Verwenden Sie keine Desktop‑Hardware für eine PBX, da die Festplatte meist bereits nach dem ersten Jahr ausfällt. Meine Empfehlung ist, eine Server‑Maschine oder ein Appliance‑Gerät zu verwenden, das für den 24x7‑Betrieb ausgelegt ist.

### IRQ sharing (legacy PCI cards only)

Dieses Thema gilt **nur**, wenn Sie physische PCI/PCI‑Express‑Telefoniekarten (DAHDI‑Hardware) installieren. Solche Karten erzeugen viele Interrupts, und auf älteren Single‑CPU‑Systemen kann das Teilen einer IRQ‑Leitung mit einem anderen Gerät den Treiber „aushungern“ und die Sprachqualität verschlechtern. Wenn Sie Telefoniekarten verwenden, widmen Sie die Maschine Asterisk, deaktivieren Sie alle ungenutzten On‑Board‑Geräte im BIOS und prüfen Sie die zugewiesenen Interrupts mit `cat /proc/interrupts`. Moderne Multi‑

## Choosing a Linux distribution

Asterisk wurde ursprünglich für Linux entwickelt. Es kann jedoch auch auf BSD Unix oder macOS laufen. Wenn Sie neu bei Asterisk sind, probieren Sie zuerst Linux, da es viel einfacher ist. Asterisk richtet sich offiziell an die RHEL‑Familie (CentOS/RHEL/Fedora), Ubuntu und Debian. Gute praktische Optionen heute sind **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** und **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux ist am Lebensende, daher bevorzugen Sie Rocky oder AlmaLinux auf RHEL‑Familien‑Systemen. Für dieses Buch verwende ich Ubuntu 24.04 LTS. Laden Sie das neueste 24.04‑Punkt‑Release‑Server‑Image aus dem offiziellen Release‑Verzeichnis unten herunter (der genaue Dateiname enthält das aktuelle Punkt‑Release, z. B. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Bevor Sie Asterisk kompilieren, benötigen Sie ein funktionierendes Linux‑System mit den installierten Build‑Paketen. Installieren Sie **Ubuntu 24.04 LTS Server** in einer virtuellen Maschine oder auf einem dedizierten Rechner (verwenden Sie das 64‑Bit‑Image; alles in diesem Buch ist 64‑Bit, obwohl Asterisk selbst noch 32‑Bit‑x86 unterstützt). Wir haben VirtualBox für dieses Training verwendet; Sie können das Image von <https://releases.ubuntu.com/24.04> herunterladen. Die Installation von Linux selbst liegt außerhalb des Umfangs dieses Buches — grundlegende Linux‑Kenntnisse sind eine Voraussetzung. Nach der Installation von Linux fügen Sie die Asterisk‑Build‑Abhängigkeiten hinzu (siehe *Installing dependencies* weiter unten) und kompilieren dann Asterisk.

## Installing Linux for Asterisk

Installieren Sie Linux wie üblich, ohne grafische Desktop-Umgebung. Aktivieren Sie während der Installation auch einen Mail-Transfer-Agent (wir verwenden **exim4**) — Asterisk wird ihn später in diesem Buch benötigen, um Voicemail‑zu‑E‑Mail‑Benachrichtigungen zu senden. **Caution:** Das Installieren eines Betriebssystems löscht die Ziel‑Festplatte. Wenn Sie auf physischer Hardware installieren, sichern Sie zuerst Ihre Daten; die Installation in einer virtuellen Maschine lässt Ihren Host unberührt. Starten Sie den Installer vom Ubuntu Server ISO (oder vom virtuellen optischen Laufwerk der VM) und beantworten Sie die Eingabeaufforderungen — die meisten sind eindeutig.

## Installing dependencies

Um Asterisk und DAHDI zu installieren, müssen Sie viele Software‑Abhängigkeiten installieren. Der empfohlene Weg, dies in Asterisk 22 zu tun, ist das Skript zu verwenden, das im Quellbaum mitgeliefert wird und die korrekten Paketnamen für jede unterstützte Distribution kennt. Nachdem Sie den Asterisk‑Quellcode heruntergeladen und entpackt haben (siehe „Compiling Asterisk“ weiter unten), führen Sie aus:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Melden Sie sich als root an (oder verwenden Sie `sudo`).
2. Wenn Sie die Abhängigkeiten manuell auf einem Debian/Ubuntu‑System installieren möchten, lautet die entsprechende Paketliste:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Beachten Sie, dass der Asterisk‑Quellcode jetzt auf Git gehostet wird, sodass `subversion` nicht mehr benötigt wird, und moderne Debian/Ubuntu liefern `libncurses-dev` anstelle des versionierten `libncurses5-dev`. Bevorzugen Sie `./contrib/scripts/install_prereq install` gegenüber einer selbst gepflegten Liste, da das Skript stets die korrekten Paketnamen für Ihre Distribution verfolgt.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) ist die Treiberarchitektur für analoge und digitale Karten. Vor der Installation von Asterisk ist es wichtig, DAHDI zu installieren, wenn Sie analoge oder digitale Schnittstellen nutzen wollen. DAHDI gibt es nach wie vor für analoge/digitale Telefoniekarten, ist aber zunehmend eine Nischenlösung — die meisten modernen Einsätze sind reine VoIP und können diesen Abschnitt komplett überspringen. Installieren Sie DAHDI nur, wenn Sie physische Telefonie‑Schnittstellen‑Hardware besitzen. Holen Sie sich die Quelldateien mit:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Entpacken Sie die Dateien mit:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

Sie müssen die DAHDI‑Module kompilieren. Die Befehle `./configure` und `make menuselect` wurden vor mehreren Jahren eingeführt. Letzterer ermöglicht Ihnen, auszuwählen, welche Dienstprogramme und Module gebaut werden sollen. Die folgenden Befehle erledigen das:

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

`make install-config` DAHDI wurde konfiguriert. Wenn Sie DAHDI‑Hardware besitzen, wird jetzt empfohlen, die Datei `/etc/dahdi/modules` zu bearbeiten, um nur die Unterstützung für die im System installierte DAHDI‑Hardware zu laden. Standardmäßig wird die Unterstützung für alle DAHDI‑Hardware beim Start von DAHDI geladen. Ich vermute, dass die DAHDI‑Hardware in Ihrem System ist: `usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware`. Dieser Bildschirm (oben) fordert Sie auf, die Datei `/etc/dahdi/modules` zu ändern, damit nur die für Ihre spezifische Konfiguration erforderlichen Treiber geladen werden und die erkannte Hardware angezeigt wird. Bearbeiten Sie die Datei `/etc/dahdi/modules` und laden Sie nur die benötigte Hardware. In meinem Fall nutzte ich eine Testmaschine mit einem Xorcom Astribank 6FXS und 2FXO. Die Datei wird unten gezeigt.

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

Starten Sie Ihren Computer neu und prüfen Sie, ob die Treiber korrekt geladen wurden.

## Welche Version wählen

Als Faustregel sollten Sie die Version mit den benötigten Funktionen verwenden. Asterisk folgt einem Release‑Modell mit abwechselnden LTS‑ (Long‑Term‑Support) und Standard‑Releases. Zum Zeitpunkt dieser Ausgabe ist **Asterisk 22 das aktuelle LTS‑Release** (veröffentlicht im Oktober 2024; das neueste Point‑Release ist 22.10.0), was es zur besten Wahl macht. Asterisk 20 ist das vorherige LTS, und Version 16 (verwendet in der ersten Ausgabe) ist am Ende ihres Lebenszyklus. Für Produktionssysteme wählen Sie immer ein LTS‑Release.

## Compiling Asterisk

Wenn Sie bereits Software kompiliert haben, wird das Kompilieren von Asterisk eine einfache Aufgabe sein. Führen Sie die folgenden Befehle aus, um Asterisk zu kompilieren und zu installieren. Denken Sie daran, dass Sie mit **make menuselect** auswählen können, welche Anwendungen und Module gebaut werden sollen. Schritt 1: Quellcode herunterladen

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Schritt 2: Build‑Voraussetzungen installieren (siehe „Installing dependencies“ weiter oben)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Schritt 3: Build konfigurieren

```
./configure
```

Schritt 4: Module zum Bau auswählen

```
make menuselect
```

Verwenden Sie **make menuselect**, um nur die notwendigen Module zu installieren. In Asterisk 22 ist der SIP‑Kanal **chan_pjsip** (standardmäßig gebaut); der alte **chan_sip** wurde in Asterisk 21 entfernt und existiert nicht mehr. Opus *Pass‑Through* funktioniert out of the box (das im Quellbaum befindliche `res_format_attr_opus`‑Modul übernimmt die SDP‑Verhandlung), aber das **codec_opus**‑Transcoding‑Modul ist weiterhin ein externes, proprietäres Binary von Sangoma/Digium — die Auswahl im menuselect lädt es von Digiums Servern herunter. Das Binary ist kostenlos. Siehe unten „Selecting modules with menuselect“ für Details.

Schritt 5: Asterisk bauen und installieren, dann die Standard‑Konfiguration und Beispiel‑Dateien erzeugen

```
make
make install
make samples
make config
ldconfig
```

`make install` installiert die Binaries und Module, `make samples` schreibt die Beispiel‑Konfigurationsdateien nach `/etc/asterisk`, `make config` installiert das SysV‑Init‑Startskript für Ihre erkannte Distribution (z. B. `/etc/init.d/asterisk` unter Debian/Ubuntu) und `ldconfig` aktualisiert den Shared‑Library‑Cache. Eine systemd‑Unit wird ebenfalls im Quellbaum unter `contrib/systemd/asterisk.service` mitgeliefert, aber `make config` installiert sie nicht automatisch — kopieren Sie sie selbst an den richtigen Ort, wenn Sie Asterisk unter systemd betreiben möchten (siehe unten).

### Selecting modules with menuselect

`make menuselect` öffnet ein textbasiertes Menü, in dem Sie exakt auswählen können, welche Anwendungen, Codecs, Kanäle und Ressourcen gebaut werden sollen. Einige Hinweise speziell für Asterisk 22:

- **chan_pjsip** (unter *Channel Drivers*) ist der moderne SIP‑Kanal und ist standardmäßig aktiviert; er ist der einzige SIP‑Kanal in Asterisk 22.
- **codec_opus** (unter *Codec Translators*) ist ein **externes** Modul (sein menuselect‑Eintrag lautet „Download the Opus codec from Digium“); die Aktivierung lässt `make` das kostenlose, proprietäre Binary von Sangoma/Digium herunterladen. Opus Pass‑Through selbst benötigt kein zusätzliches Modul. Sangomas **codec_g729**‑Modul ist ebenfalls verfügbar — das Binary ist kostenlos, aber das legale G.729‑Transcoding erfordert eine pro‑Kanal‑Lizenz, die erworben werden muss.
- Wählen Sie die Sound‑Formate und Sprachen, die Sie in den Menüs *Core Sound Packages*, *Music On Hold File Packages* und *Extras Sound Packages* benötigen; alles, was Sie dort aktivieren, wird automatisch während `make install` heruntergeladen und installiert.

Nachdem Sie Ihre Auswahl getroffen haben, wählen Sie **Save & Exit** und fahren mit `make` fort.

## Starting and stopping Asterisk

Mit dieser Minimal-Konfiguration ist es möglich, Asterisk erfolgreich zu starten. Zum Lernen und Debuggen können Sie Asterisk im Vordergrund an die Konsole anhängen:

```
/usr/sbin/asterisk -vvvgc
```

Verwenden Sie den CLI‑Befehl `core stop now`, um Asterisk herunterzufahren:

```
*CLI> core stop now
```

### Starting Asterisk with systemd

Auf modernen Linux‑Distributionen (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9) ist der System‑Service‑Manager **systemd**. Asterisk liefert eine systemd‑Unit unter `contrib/systemd/asterisk.service` im Quellbaum; kopieren Sie sie nach `/etc/systemd/system/asterisk.service` und führen Sie `systemctl daemon-reload` aus. Sobald sie installiert ist, ist der empfohlene Weg, Asterisk in der Produktion zu betreiben, über `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Wenn Asterisk als Service läuft, können Sie sich mit `asterisk -r` (connect) oder `asterisk -rvvv` (connect with verbose output) an dessen CLI anhängen.

Auf älteren Systemen wurde Asterisk über das klassische SysV‑Init‑Script (`/etc/init.d/asterisk`) und den **safe_asterisk**‑Wrapper gestartet, der Asterisk automatisch neu startete, falls es abstürzte. Bei systemd wird der automatische Neustart durch die `Restart=`‑Direktive der Unit‑Datei gehandhabt, sodass `safe_asterisk` im Allgemeinen nicht mehr nötig ist. Der alte Init/`safe_asterisk`‑Ansatz funktioniert weiterhin, ist aber auf systemd‑basierten Distributionen veraltet.

### Asterisk runtime options

Der Startvorgang von Asterisk ist sehr einfach. Wird Asterisk ohne Parameter gestartet, wird es als Daemon ausgeführt.

```
/sbin/asterisk
```

Sie können auf die Asterisk‑Konsole zugreifen, indem Sie den folgenden Befehl ausführen. Bitte beachten Sie, dass gleichzeitig mehr als ein Konsolen‑Prozess laufen kann.

```
/sbin/asterisk -r
```

### Available runtime options for Asterisk

Sie können die verfügbaren Laufzeitoptionen mit `asterisk -h` anzeigen:

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

## Installationsverzeichnisse

Asterisk wird in mehreren Verzeichnissen installiert, die in der asterisk.conf Datei geändert werden können. Zu Trainingszwecken würde ich das verbose von 3 auf 15 setzen, für den Produktionseinsatz bei 3 belassen. Die Optionen `maxcalls` und `maxload` sind gute Optionen, um Ihr System vor Überlastung zu schützen.

### asterisk.conf (Auszug)

Der `[directories]` Abschnitt definiert, wo Asterisk seine Konfiguration, Module, Daten, spool und Logs ablegt:

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

Der `[options]` Abschnitt enthält Runtime‑Tuning. Die nützlichsten Optionen sind unten gezeigt (auskommentieren, um zu aktivieren); die Datei liefert viele weitere, jeweils durch einen Inline‑Kommentar dokumentiert:

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

## Logdateien und Logrotation

Asterisk PBX protokolliert seine Meldungen in `/var/log/asterisk`. Das Logging wird durch `logger.conf` gesteuert. Der zentrale Teil ist der Abschnitt `[logfiles]`, in dem jede Zeile einen Log‑Kanal und die erfassten Meldungsstufen definiert (Auszug):

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

Nach dem Bearbeiten die Änderung mit `logger reload` anwenden und die Kanäle mit `logger show channels` bestätigen:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

Die Logdateien können schnell wachsen, daher sollten sie mit dem System‑Daemon `logrotate` rotiert werden — eine Datei unter `/etc/logrotate.d/` hinzufügen:

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

Weitere Informationen zu logrotate erhalten Sie mit:

```
#man logrotate
```

## Deinstallieren von Asterisk

Um Asterisk zu deinstallieren, verwenden Sie:

```
make uninstall
```

Um Asterisk und alle Konfigurationsdateien zu deinstallieren, verwenden Sie:

```
make uninstall-all
```

## Asterisk installation notes

This section will provide some advice about issues to address before installing Asterisk.

### Production Systems

If Asterisk is installed in a production environment, you should pay attention to the system design. A server has to be optimized in such a way that telephony systems have priority over other system processes. Asterisk should not run together with processor-intensive software such as X-Windows. If you need to run CPU-intensive processes (e.g., a huge database), use a separate server. Generally speaking, Asterisk is susceptible to hardware performance variations. Thus, try using Asterisk in a hardware environment that does not require more than 40% of CPU utilization.

### Network Tips

If you plan to use IP phones, it is important that you pay attention to your network. Voice protocols are very good and resistant to latency and even jitters; however, if you use a poorly configured local area network, voice quality will suffer. It is only possible to guarantee good voice quality using quality of service (QoS) in switches and routers. Voice in a local area network tends to be good, but even in a LAN environment, if you have 10 Mbps hubs with too many collisions, you will end up having a distorted or crappy voice. Follow these recommendations to ensure the best possible voice quality:

- Use end-to-end QoS if possible or economically feasible. With end-to-end QoS, the voice quality is perfect. No excuses!
- Avoid using 10/100 Mbps hubs for voice in a production environment. Collisions can impose jitters on the network. Full duplex 10/100 Mbps are preferred because no collisions occur.
- Use VLANs to separate unnecessary broadcasts of the voice network. You don’t want a virus destroying your voice network with ARP broadcasts.
- Educate users about expectations in a voice network. Without QoS, don’t state that the voice will be perfect as in most cases it won’t be. A quality of voice similar to a mobile phone will most often be achieved. Use quality phones as problems with firmware and hardware design are common.

## Zusammenfassung

In diesem Kapitel haben Sie die minimalen Hardwareanforderungen sowie das Herunterladen, Installieren und Kompilieren von Asterisk kennengelernt. Asterisk sollte aus Sicherheitsgründen mit einem Nicht‑Root‑Benutzer ausgeführt werden. Sie sollten Ihre Netzwerkumgebung prüfen, bevor Sie die Produktionsumgebung starten.

## Quiz

1. In Asterisk 22, welcher Channel‑Treiber bietet SIP‑Unterstützung, und was ist mit dem älteren `chan_sip` passiert?
   - A. `chan_sip` ist weiterhin der Standard; `chan_pjsip` ist optional.
   - B. `chan_pjsip` ist der Standard‑SIP‑Channel; `chan_sip` wurde in Asterisk 21 entfernt und existiert nicht mehr.
   - C. Beide werden standardmäßig gebaut und Sie wählen zur Laufzeit zwischen ihnen.
   - D. SIP‑Unterstützung wurde vollständig zugunsten von IAX2 entfernt.
2. Telephoniekarten für Asterisk besitzen in der Regel integrierte Digital Signal Processor (DSP) und benötigen daher kaum CPU‑Leistung vom PC.
   - A. Wahr
   - B. Falsch
3. Wenn Sie perfekte Sprachqualität wollen, müssen Sie End‑to‑End‑Quality of Service (QoS) implementieren.
   - A. Wahr
   - B. Falsch
4. Sie sollten immer die neueste Asterisk‑Version wählen, da sie die stabilste ist.
   - A. Wahr
   - B. Falsch
5. Was ist der empfohlene Weg, die Build‑Abhängigkeiten für Asterisk 22 zu installieren?
6. Wenn Sie keine TDM‑Karte besitzen, haben Sie trotzdem eine interne Zeitquelle zur Synchronisation, bereitgestellt vom `res_timing_timerfd`‑Modul unter Linux. Diese Zeitquelle wird von Anwendungen wie ________ und ________ verwendet.
7. Beim Installieren von Asterisk ist es besser, Desktop‑Umgebungen wie GNOME oder KDE wegzulassen, weil grafische Oberflächen CPU‑Zyklen verbrauchen.
   - A. Wahr
   - B. Falsch
8. Asterisk‑Konfigurationsdateien befinden sich im Verzeichnis ________.
9. Um die Asterisk‑Beispielkonfigurationsdateien zu installieren, geben Sie den Befehl ein: ________
10. Warum ist es wichtig, Asterisk als Nicht‑Root‑Benutzer auszuführen?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
