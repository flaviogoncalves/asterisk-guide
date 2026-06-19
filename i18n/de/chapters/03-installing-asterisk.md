# Installation von Asterisk 22

Im ersten Kapitel haben wir einiges darüber gelernt, wie Asterisk in der Telefonieumgebung nützlich ist. In diesem Kapitel werden wir behandeln, wie man Asterisk herunterlädt und installiert. Bevor wir beginnen, ist es wichtig zu lernen, wie man es kompiliert und installiert. Der Kompilierungsprozess mag für traditionelle Microsoft™ Windows™-Benutzer seltsam erscheinen, ist aber in der Linux™-Umgebung recht üblich. Beim Kompilieren von Asterisk kann man einen für die eigene Hardware optimierten Code erhalten, was wir hier tun werden. Asterisk läuft auf verschiedenen Betriebssystemen, aber wir haben uns entschieden, die Dinge einfach zu halten und mit nur einem davon zu beginnen: Linux. Wir haben Debian als Linux™-Distribution gewählt, da die Abhängigkeiten einfach zu installieren sind und die Distribution stabil ist und nur wenig Ressourcen benötigt. Wenn Sie eine andere Distribution verwenden möchten, ändern Sie bitte die Namen der Abhängigkeiten entsprechend.

Diese Ausgabe zielt auf **Asterisk 22 LTS** ab (veröffentlicht am 16.10.2024; voller Support bis zum 16.10.2028, Sicherheitsupdates bis zum 16.10.2029). Asterisk 22 ist die aktuelle Long-Term-Support-Version. Beachten Sie, dass Digium 2018 von **Sangoma** übernommen wurde und Asterisk nun von Sangoma gesponsert wird – Verweise auf "Digium" in diesem Kapitel beziehen sich auf die Legacy-Marke für historische Hardware.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die Hardwareanforderungen für Asterisk zu bestimmen;
- Linux mit den erforderlichen Abhängigkeiten zu installieren;
- Eine stabile Version über HTTPS herunterzuladen;
- Asterisk zu kompilieren; und
- Zu lernen, wie man Asterisk beim Systemstart automatisch startet.

## Minimale Hardwareanforderungen

Asterisk benötigt nicht viel Hardware, um zu laufen, jedoch gibt es einige Tipps, um die beste Hardware für Ihre Anforderungen auszuwählen. Sie sollten bei der Auswahl Ihrer Hardware die folgenden Hauptfaktoren berücksichtigen:

- Gesamtzahl der registrierten Benutzer. Definieren Sie, wie viele Registrierungen pro Sekunde Sie unterstützen müssen.
- Gesamtzahl der gleichzeitigen Anrufe. Definieren Sie, wie viele Netzwerkgespräche Sie im Netzwerkadapter und in der Bridge auf dem Asterisk-Server verarbeiten müssen.
- Welche codecs Sie unterstützen müssen. Hochkomplexe codecs erfordern viel CPU/FPU-Leistung auf Ihrem Server; iLBC wurde beispielsweise von seinem Entwickler (Global IP Sound) auf etwa 18 MIPS pro Kanal für 30 ms Frames (und etwa 15 MIPS für 20 ms Frames) auf einem TI C54x DSP gemessen.
- Echounterdrückung. Die Echounterdrückung kann viel CPU/FPU beanspruchen; in einigen Fällen sollten Sie eine hardwarebasierte Echounterdrückung mittels DSPs auf der Telefonieschnittstellenkarte wählen.
- Verfügbarkeit. Verwenden Sie RAID1 oder 5, um die Verfügbarkeit zu erhöhen. Denken Sie daran, Asterisk ist eine 24x7-Anwendung.

Die Hauptkomponente für einen Asterisk-Server ist der Netzwerkadapter. Ein guter Server-Netzwerkadapter wird empfohlen. Die CPU ist wichtig, wenn Sie hochkomplexe codecs wie g.729 und iLBC sowie Echounterdrückung unterstützen müssen. Sie können sich für dedizierte DSPs entscheiden; Sangoma (ehemals Digium) bietet eine DSP-Karte namens TC400B an, die 120 gleichzeitige g729-Anrufe unterstützen kann. Die bewährte Methode ist die Wahl eines neuen Computers der Serverklasse von einem bekannten Hersteller. Um genau zu wissen, wie viele gleichzeitige Anrufe oder wie viele registrierte Benutzer eine bestimmte Maschine unterstützen kann, sollten Sie diese Hardware mit einem Stresstest-Tool wie SIPP (http://sipp.sourceforge.net) testen. Einige Hardwarehersteller wie Xorcom (http://www.xorcom.com) veröffentlichen ihre Ergebnisse auf ihrer Website. Hinweis: Einige Asterisk-Anwendungen, wie ConfBridge und Music on Hold, benötigen eine interne Zeitquelle. Auf modernem Linux wird dies automatisch durch das integrierte `res_timing_timerfd`-Modul bereitgestellt – es ist keine Telefonie-Hardware erforderlich. (Der alte `dahdi_dummy`-Software-Timer existiert nicht mehr; seine Funktionalität wurde in das Haupt-Kernel-Modul `dahdi` in DAHDI Linux 2.3.0 integriert.) Sie können den aktiven Timer mit dem CLI-Befehl `timing test` bestätigen.

### Hardwarekonfiguration

Die Asterisk-Hardware muss nicht hochkomplex sein. Sie benötigen keine teure Grafikkarte oder zahlreiche Peripheriegeräte. Einige Tipps zur Hardwarekonfiguration:

- Deaktivieren Sie ungenutzte USB-, serielle und parallele Anschlüsse, um den Verbrauch unnötiger Interrupts zu vermeiden.
- Eine robuste Netzwerkschnittstellenkarte ist unerlässlich.
- Seien Sie besonders vorsichtig, wenn Sie Telefonieschnittstellenkarten verwenden. Einige Karten verwenden einen 3,3-Volt-PCI-Bus, und es ist nicht einfach, dafür Mainboards zu finden. Heutzutage ist PCI Express leichter zu finden.
- Achten Sie besonders auf die Festplatte; PBX-Systeme arbeiten meist im 24x7-Betrieb, während Desktops 8x5 arbeiten. Verwenden Sie keine Desktop-Hardware für eine PBX, da die Festplatte normalerweise vor dem ersten Jahr ausfällt. Meine Empfehlung ist die Verwendung einer Servermaschine oder eines Appliances, das für den 24x7-Betrieb ausgelegt ist.

### IRQ-Sharing

Telefonieschnittstellenkarten (z. B. X100P) erzeugen eine große Anzahl von Unterbrechungen (Interrupts). Die Bedienung dieser Unterbrechungen erfordert Prozessorzeit. Die Treiber können diese Verarbeitung nicht durchführen, wenn ein anderes Gerät dieselbe Unterbrechung verwendet. In einem System mit einer einzigen CPU sollten Sie IRQ-Sharing zwischen Geräten vermeiden. Wir empfehlen die Verwendung dedizierter Hardware für den Betrieb von Asterisk. Vergessen Sie nicht, fremde oder unnötige Hardware zu deaktivieren. Einige Hardware kann im BIOS-Setup des Mainboards deaktiviert werden. Sobald Sie Ihren Computer gestartet haben, sehen Sie Ihre zugewiesenen Interrupts in /proc/interrupts.

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

Hier sehen Sie drei Digium-Karten, jede auf ihrem eigenen IRQ. Wenn dies in Ihrem System der Fall ist, fahren Sie fort und installieren Sie die Hardwaretreiber. Wenn dies nicht der Fall ist, gehen Sie zurück und versuchen Sie etwas anderes, um IRQ-Sharing zu vermeiden.

## Auswahl einer Linux-Distribution

Asterisk wurde ursprünglich für Linux entwickelt. Es kann jedoch auch auf BSD Unix oder macOS laufen. Wenn Sie neu bei Asterisk sind, versuchen Sie es zuerst mit Linux, da es viel einfacher ist. Asterisk zielt offiziell auf die RHEL-Familie (CentOS/RHEL/Fedora), Ubuntu und Debian ab. Gute praktische Entscheidungen sind heute **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** und **Rocky Linux 9 / AlmaLinux 9** – CentOS Linux ist am Ende seines Lebenszyklus, bevorzugen Sie also Rocky oder AlmaLinux bei Systemen der RHEL-Familie. Für dieses Buch verwende ich Ubuntu 24.04 LTS. Laden Sie das neueste 24.04 Point-Release-Server-Image aus dem offiziellen Release-Verzeichnis unten herunter (der genaue Dateiname enthält das aktuelle Point-Release, z. B. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Vorbereitung von Linux für Asterisk

Unmittelbar nach der Installation von Asterisk installieren wir die Pakete, die für die anschließende Kompilierung von Asterisk und DAHDI-Treibern erforderlich sind. Zuerst geben wir Debian an, von wo die Pakete heruntergeladen werden sollen. Dies geschieht mit dem Dienstprogramm apt-setup. Schritt 1: Installieren Sie Ubuntu 24.04 LTS Server in einer virtuellen Maschine (verwenden Sie das 64-Bit-Image; die in diesem Buch verwendeten Distributionen sind 64-Bit, obwohl Asterisk selbst immer noch 32-Bit x86 unterstützt). Wir haben VirtualBox für dieses Training verwendet. Sie können das Image von https://releases.ubuntu.com/24.04 herunterladen. Die Linux-Installation ist nicht Gegenstand dieses Trainings. Grundlegende Linux-Kenntnisse sind Voraussetzung für dieses Training.

## Installation von Linux für Asterisk

Installieren Sie Ihr Linux wie gewohnt, ohne grafische Benutzeroberfläche. Installieren und konfigurieren Sie auch den E-Mail-Server. Wir werden den E-Mail-Server (exim4) benötigen, um später in diesem Buch Voicemail-Benachrichtigungen zu versenden. Achtung: Diese Installation formatiert Ihren PC. Alle Ihre Festplattendaten werden gelöscht. Bitte stellen Sie sicher, dass Sie alle Daten sichern, bevor Sie beginnen. Schritt 1: Legen Sie die CD in das CD-ROM-Laufwerk und starten Sie Ihren PC. Die meisten Fragen sind sehr einfach zu beantworten.

## Installation von Abhängigkeiten

Um Asterisk und DAHDI zu installieren, müssen Sie viele Softwareabhängigkeiten installieren. Der empfohlene Weg, dies in Asterisk 22 zu tun, ist die Verwendung des Skripts, das mit dem Quellcode geliefert wird und die korrekten Paketnamen für jede unterstützte Distribution kennt. Nachdem Sie den Asterisk-Quellcode heruntergeladen und entpackt haben (siehe "Kompilieren von Asterisk" unten), führen Sie aus:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

Schritt 1: Melden Sie sich als root an (oder verwenden Sie `sudo`). Schritt 2: Wenn Sie die Abhängigkeiten lieber manuell auf einem Debian/Ubuntu-System installieren möchten, lautet die entsprechende Paketliste:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

Beachten Sie, dass der Asterisk-Quellcode jetzt auf Git gehostet wird, daher ist `subversion` nicht mehr erforderlich, und moderne Debian/Ubuntu-Systeme liefern `libncurses-dev` anstelle der versionierten `libncurses5-dev`. Bevorzugen Sie `./contrib/scripts/install_prereq install` gegenüber einer manuell gepflegten Liste, da das Skript immer die korrekten Paketnamen für Ihre Distribution nachverfolgt.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) ist die Treiberarchitektur für analoge und digitale Karten. Vor der Installation von Asterisk ist es wichtig, DAHDI zu installieren, wenn Sie analoge oder digitale Schnittstellen verwenden möchten. DAHDI existiert weiterhin für analoge/digitale Telefoniekarten, ist aber zunehmend eine Nische – die meisten modernen Implementierungen sind reines VoIP und können diesen Abschnitt komplett überspringen. Installieren Sie DAHDI nur, wenn Sie physische Telefonieschnittstellen-Hardware haben. Laden Sie die Quelldateien mit folgendem Befehl herunter:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Entpacken Sie die Dateien mit:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Kompilieren von DAHDI-Treibern

Sie müssen die DAHDI-Module kompilieren. Die Befehle ./configure und make menuselect wurden vor einigen Jahren eingeführt. Letzterer ermöglicht es Ihnen, auszuwählen, welche Dienstprogramme und Module erstellt werden sollen. Die folgenden Befehle führen dies aus:

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

make install-config DAHDI wurde konfiguriert. Wenn Sie DAHDI-Hardware haben, wird nun empfohlen, /etc/dahdi/modules zu bearbeiten, um nur die Unterstützung für die in diesem System installierte DAHDI-Hardware zu laden. Standardmäßig wird die Unterstützung für alle DAHDI-Hardware beim DAHDI-Start geladen. Ich denke, die DAHDI-Hardware, die Sie auf Ihrem System haben, ist: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware Dieser Bildschirm (oben) fordert Sie auf, die Datei /etc/dahdi/modules zu ändern, um nur die erforderlichen Treiber für Ihre spezifische Konfiguration zu laden und die erkannte Hardware anzuzeigen. Bearbeiten Sie die Datei /etc/dahdi/modules und laden Sie nur die erforderliche Hardware. In meinem Fall verwendete ich eine Testmaschine mit einer Xorcom Astribank 6FXS und 2FXO. Die Datei ist unten dargestellt.

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

Starten Sie Ihren Computer neu und überprüfen Sie das korrekte Laden der Treiber.

## Welche Version soll man wählen

Als Faustregel sollten Sie die Version mit den erforderlichen Funktionen verwenden. Asterisk folgt einem Release-Modell aus abwechselnden LTS- (Long-Term Support) und Standard-Releases. Zum Zeitpunkt dieser Ausgabe ist **Asterisk 22 die aktuelle LTS-Version** (veröffentlicht im Oktober 2024; das neueste Point-Release ist 22.10.0), was sie zur besten Wahl für den Moment macht. Asterisk 20 ist die vorherige LTS-Version, und Version 16 (verwendet in der ersten Ausgabe) ist am Ende ihres Lebenszyklus. Wählen Sie für Produktionssysteme immer eine LTS-Version.

> **[Hinweis zur 2. Ausgabe]** Nur Prüfung zum Zeitpunkt der Drucklegung: Bestätigen Sie das neueste 22.x Point-Release unter downloads.asterisk.org und aktualisieren Sie die Versionszeichenfolge oben, falls eine neuere Version erschienen ist.

## Kompilieren von Asterisk

Wenn Sie bereits Software kompiliert haben, wird das Kompilieren von Asterisk eine einfache Aufgabe sein. Führen Sie die folgenden Befehle aus, um Asterisk zu kompilieren und zu installieren. Denken Sie daran, dass Sie mit make menuselect auswählen können, welche Anwendungen und Module erstellt werden sollen. Schritt 1: Laden Sie den Quellcode herunter

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Schritt 2: Installieren Sie die Build-Voraussetzungen (siehe "Installation von Abhängigkeiten" oben)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Schritt 3: Konfigurieren Sie den Build

```
./configure
```

Schritt 4: Wählen Sie die zu erstellenden Module aus

```
make menuselect
```

Verwenden Sie make menuselect, um nur die notwendigen Module zu installieren. In Asterisk 22 ist der SIP-Kanal **chan_pjsip** (standardmäßig erstellt); das alte **chan_sip** wurde in Asterisk 21 entfernt und existiert nicht mehr. Opus *Pass-Through* funktioniert sofort (das integrierte `res_format_attr_opus`-Modul übernimmt die SDP-Aushandlung), aber das **codec_opus**-Transcoding-Modul ist immer noch ein externes, proprietäres Binärpaket von Sangoma/Digium – die Auswahl in menuselect lädt es von den Digium-Servern herunter. Das Binärpaket ist kostenlos. Siehe "Auswählen von Modulen mit menuselect" unten für Details.

Schritt 5: Erstellen und installieren Sie Asterisk, erstellen Sie dann die Standardkonfigurations- und Beispieldateien

```
make
make install
make samples
make config
ldconfig
```

`make install` installiert die Binärdateien und Module, `make samples` schreibt die Beispielkonfigurationsdateien nach `/etc/asterisk`, `make config` installiert das SysV-Init-Startskript für Ihre erkannte Distribution (z. B. `/etc/init.d/asterisk` auf Debian/Ubuntu), und `ldconfig` aktualisiert den Cache der gemeinsam genutzten Bibliotheken. Eine systemd-Unit wird ebenfalls im Quellcodebaum unter `contrib/systemd/asterisk.service` mitgeliefert, aber `make config` installiert sie nicht automatisch – kopieren Sie sie selbst an den richtigen Ort, wenn Sie Asterisk unter systemd ausführen möchten (siehe unten).

### Auswählen von Modulen mit menuselect

`make menuselect` öffnet ein textbasiertes Menü, in dem Sie genau auswählen können, welche Anwendungen, codecs, Kanäle und Ressourcen erstellt werden sollen. Ein paar spezifische Hinweise zu Asterisk 22:

- **chan_pjsip** (unter *Channel Drivers*) ist der moderne SIP-Kanal und standardmäßig aktiviert; es ist der einzige SIP-Kanal in Asterisk 22.
- **codec_opus** (unter *Codec Translators*) ist ein **externes** Modul (der menuselect-Eintrag lautet "Download the Opus codec from Digium"); die Aktivierung bewirkt, dass `make` das kostenlose, proprietäre Binärpaket von Sangoma/Digium abruft. Opus Pass-Through selbst benötigt kein zusätzliches Modul. Sangomas **codec_g729**-Modul ist ebenfalls verfügbar – das Binärpaket ist kostenlos herunterladbar, aber für legales G.729-Transcoding ist eine gekaufte Lizenz pro Kanal erforderlich.
- Wählen Sie die Soundformate und Sprachen, die Sie möchten, in den Menüs *Core Sound Packages*, *Music On Hold File Packages* und *Extras Sound Packages*; alles, was Sie dort auswählen, wird während `make install` automatisch heruntergeladen und installiert.

Nachdem Sie Ihre Auswahl getroffen haben, wählen Sie **Save & Exit** und fahren Sie mit `make` fort.

> **[Hinweis zur 2. Ausgabe]** Autorenaktion: Ersetzen Sie den `make menuselect`-Screenshot der 1. Ausgabe durch eine aktuelle Asterisk 22-Aufnahme, deren Channel Drivers-Bildschirm chan_pjsip zeigt und kein chan_sip/chan_skinny/chan_mgcp.

## Starten und Stoppen von Asterisk

Mit dieser minimalen Konfiguration ist es möglich, Asterisk erfolgreich zu starten. Zum Lernen und Debuggen können Sie Asterisk im Vordergrund starten, verbunden mit der Konsole:

```
/usr/sbin/asterisk –vvvgc
```

Verwenden Sie den CLI-Befehl stop now, um Asterisk herunterzufahren.

```
CLI>core stop now
```

### Starten von Asterisk mit systemd

Auf modernen Linux-Distributionen (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9) ist der Systemdienstmanager **systemd**. Asterisk liefert eine systemd-Unit unter `contrib/systemd/asterisk.service` im Quellcodebaum; kopieren Sie sie nach `/etc/systemd/system/asterisk.service` und führen Sie `systemctl daemon-reload` aus. Sobald installiert, ist der empfohlene Weg, Asterisk in der Produktion auszuführen, über `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Sobald Asterisk als Dienst läuft, verbinden Sie sich mit seiner CLI über `asterisk -r` (Verbinden) oder `asterisk -rvvv` (Verbinden mit ausführlicher Ausgabe).

Auf älteren Systemen wurde Asterisk über das Legacy-SysV-Init-Skript (`/etc/init.d/asterisk`) und den **safe_asterisk**-Wrapper gestartet, der Asterisk bei einem Absturz automatisch neu startete. Mit systemd wird der automatische Neustart durch die `Restart=`-Direktive der Unit-Datei gehandhabt, daher ist `safe_asterisk` im Allgemeinen nicht mehr erforderlich. Der Legacy-Init/`safe_asterisk`-Ansatz funktioniert weiterhin, ist aber auf systemd-basierten Distributionen veraltet.

### Asterisk-Laufzeitoptionen

Der Asterisk-Startprozess ist sehr einfach. Wenn Asterisk ohne Parameter ausgeführt wird, wird es als Daemon gestartet.

```
/sbin/asterisk
```

Sie können auf die Asterisk-Konsole zugreifen, indem Sie den folgenden Befehl ausführen. Bitte beachten Sie, dass mehr als ein Konsolenprozess gleichzeitig ausgeführt werden kann.

```
/sbin/asterisk -r
```

### Verfügbare Laufzeitoptionen für Asterisk

Sie können die verfügbaren Laufzeitoptionen mit asterisk –h anzeigen.

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation und andere. Verwendung: asterisk [OPTIONEN] Gültige Optionen: -V Versionsnummer anzeigen und beenden -C <configfile> Alternative Konfigurationsdatei verwenden -G <group> Als andere Gruppe als der Aufrufer ausführen -U <user> Als anderer Benutzer als der Aufrufer ausführen -c Konsolen-CLI bereitstellen -d Debugging erhöhen (mehrere d's = mehr Debugging) -f Nicht forken -F Immer forken -g Core-Dump bei Absturz -h Dieser Hilfebildschirm -i Kryptoschlüssel beim Start initialisieren -L <load> Maximale Lastdurchschnitt begrenzen, bevor neue Anrufe abgelehnt werden -M <value> Maximale Anzahl von Anrufen auf den angegebenen Wert begrenzen -m Debugging- und Konsolenausgabe auf der Konsole stummschalten -n Konsolenfarben deaktivieren. Kann nur beim Start verwendet werden. -p Als Pseudo-Echtzeit-Thread ausführen -q Quiet-Modus (Ausgabe unterdrücken) -r Mit Asterisk auf dieser Maschine verbinden -R Wie -r, außer dass versucht wird, die Verbindung wiederherzustellen, falls sie unterbrochen wurde -s <socket> Über Socket <socket> mit Asterisk verbinden (nur gültig mit -r) -t Sounddateien in /var/tmp aufzeichnen und dorthin verschieben, wo sie hingehören, nachdem sie fertig sind -T Zeit im Format [Mmm dd hh:mm:ss] für jede Zeile der Ausgabe an die CLI anzeigen. Kann nicht mit dem Remote-Konsolenmodus verwendet werden. -v Ausführlichkeit erhöhen (mehrere v's = ausführlicher) -x <cmd> Befehl <cmd> ausführen (impliziert -r) -X Verwendung von #exec in asterisk.conf aktivieren -W Terminalfarben anpassen, um einen hellen Hintergrund auszugleichen

## Installationsverzeichnisse

Asterisk wird in mehreren Verzeichnissen installiert, die in der Datei asterisk.conf geändert werden können. Zu Schulungszwecken würde ich die Ausführlichkeit (verbose) von 3 auf 15 ändern, für die Produktion lassen Sie sie auf 3. Die Optionen max_calls und max_load sind gute Optionen, um Ihr System vor Überlastung zu schützen.

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

## Protokolldateien und Log-Rotation

Asterisk PBX protokolliert seine Meldungen im Verzeichnis /var/log/asterisk. Die Datei, die die Protokolle steuert:

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

; Einige Konsolenbefehle sind mit dem Logger-Prozess verknüpft.

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

Weitere Informationen über logrotate erhalten Sie mit:

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

## Hinweise zur Asterisk-Installation

Dieser Abschnitt enthält einige Ratschläge zu Themen, die vor der Installation von Asterisk angegangen werden sollten.

### Produktionssysteme

Wenn Asterisk in einer Produktionsumgebung installiert wird, sollten Sie auf das Systemdesign achten. Ein Server muss so optimiert sein, dass Telefoniesysteme Vorrang vor anderen Systemprozessen haben. Asterisk sollte nicht zusammen mit prozessorintensiver Software wie X-Windows ausgeführt werden. Wenn Sie CPU-intensive Prozesse ausführen müssen (z. B. eine riesige Datenbank), verwenden Sie einen separaten Server. Im Allgemeinen ist Asterisk anfällig für Hardware-Leistungsschwankungen. Versuchen Sie daher, Asterisk in einer Hardwareumgebung zu verwenden, die nicht mehr als 40 % der CPU-Auslastung erfordert.

### Netzwerktipps

Wenn Sie IP-Telefone verwenden möchten, ist es wichtig, dass Sie auf Ihr Netzwerk achten. Sprachprotokolle sind sehr gut und resistent gegen Latenz und sogar Jitter; wenn Sie jedoch ein schlecht konfiguriertes lokales Netzwerk verwenden, wird die Sprachqualität leiden. Es ist nur möglich, eine gute Sprachqualität durch Quality of Service (QoS) in Switches und Routern zu garantieren. Sprache in einem lokalen Netzwerk ist tendenziell gut, aber selbst in einer LAN-Umgebung werden Sie bei 10-Mbit/s-Hubs mit zu vielen Kollisionen am Ende eine verzerrte oder schlechte Sprachqualität haben. Befolgen Sie diese Empfehlungen, um die bestmögliche Sprachqualität zu gewährleisten:

- Verwenden Sie End-to-End-QoS, wenn möglich oder wirtschaftlich vertretbar. Mit End-to-End-QoS ist die Sprachqualität perfekt. Keine Ausreden!
- Vermeiden Sie die Verwendung von 10/100-Mbit/s-Hubs für Sprache in einer Produktionsumgebung. Kollisionen können Jitter im Netzwerk verursachen. Vollduplex 10/100 Mbit/s werden bevorzugt, da keine Kollisionen auftreten.
- Verwenden Sie VLANs, um unnötige Broadcasts des Sprachnetzwerks zu trennen. Sie möchten nicht, dass ein Virus Ihr Sprachnetzwerk mit ARP-Broadcasts zerstört.
- Klären Sie Benutzer über Erwartungen in einem Sprachnetzwerk auf. Ohne QoS sollten Sie nicht behaupten, dass die Sprache perfekt sein wird, da dies in den meisten Fällen nicht der Fall sein wird. Eine Sprachqualität ähnlich der eines Mobiltelefons wird meistens erreicht. Verwenden Sie hochwertige Telefone, da Probleme mit Firmware und Hardwaredesign häufig sind.

## Zusammenfassung

In diesem Kapitel haben Sie die minimalen Hardwareanforderungen kennengelernt sowie wie man Asterisk herunterlädt, installiert und kompiliert. Asterisk sollte aus Sicherheitsgründen mit einem Nicht-Root-Benutzer ausgeführt werden. Sie sollten Ihre Netzwerkumgebung überprüfen, bevor Sie die Produktionsumgebung starten.

## Quiz

1. Welcher Kanaltreiber bietet in Asterisk 22 SIP-Unterstützung und was ist mit dem älteren `chan_sip` passiert?
   - A. `chan_sip` ist immer noch der Standard; `chan_pjsip` ist optional.
   - B. `chan_pjsip` ist der Standard-SIP-Kanal; `chan_sip` wurde in Asterisk 21 entfernt und existiert nicht mehr.
   - C. Beide werden standardmäßig erstellt und Sie wählen zur Laufzeit zwischen ihnen.
   - D. Die SIP-Unterstützung wurde zugunsten von IAX2 komplett entfernt.
2. Telefonieschnittstellenkarten für Asterisk haben normalerweise eingebaute digitale Signalprozessoren (DSPs) und benötigen daher nicht viel CPU vom PC.
   - A. Wahr
   - B. Falsch
3. Wenn Sie eine perfekte Sprachqualität wünschen, müssen Sie End-to-End Quality of Service (QoS) implementieren.
   - A. Wahr
   - B. Falsch
4. Sie sollten immer die neueste Asterisk-Version wählen, da sie die stabilste ist.
   - A. Wahr
   - B. Falsch
5. Was ist der empfohlene Weg, um die Build-Abhängigkeiten für Asterisk 22 zu installieren?
6. Wenn Sie keine TDM-Schnittstellenkarte haben, haben Sie trotzdem eine interne Zeitquelle für die Synchronisation, die vom `res_timing_timerfd`-Modul unter Linux bereitgestellt wird. Dieses Timing wird von Anwendungen wie ________ und ________ verwendet.
7. Bei der Installation von Asterisk ist es besser, Desktop-Umgebungen wie GNOME oder KDE wegzulassen, da grafische Oberflächen CPU-Zyklen verbrauchen.
   - A. Wahr
   - B. Falsch
8. Asterisk-Konfigurationsdateien befinden sich im Verzeichnis ________.
9. Um die Asterisk-Beispielkonfigurationsdateien zu installieren, geben Sie den Befehl ein: ________
10. Warum ist es wichtig, Asterisk als Nicht-Root-Benutzer auszuführen?

**Antworten:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Führen Sie `./contrib/scripts/install_prereq install` aus dem entpackten Asterisk-Quellcodebaum aus · 6 — ConfBridge und Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Sicherheit (begrenzt den Schaden, falls Asterisk kompromittiert wird)
