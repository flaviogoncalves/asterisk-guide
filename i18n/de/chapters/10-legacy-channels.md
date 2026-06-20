# Legacy-Kanäle: Analog, TDM & IAX2

In einer reinen VoIP-Welt des Jahres 2026 sind die in diesem Kapitel behandelten Kanaltypen zunehmend selten: Die meisten neuen Installationen basieren auf SIP-Trunks und PJSIP-endpoints über Ethernet, ganz ohne Telefonie-Hardware. Asterisk 22 unterstützt die meisten davon jedoch weiterhin vollständig. Analoge (FXO/FXS) und digitale TDM-Konnektivität (E1/T1/ISDN PRI/BRI) wird über DAHDI bereitgestellt — den Treibersatz, der ursprünglich von Digium entwickelt wurde. Digium wurde 2018 von Sangoma übernommen, nachdem die früheren Zaptel-Treiber infolge eines Markenrechtsstreits umbenannt worden waren. Die Server-zu-Server-Konnektivität über IAX2 wird durch `chan_iax2` bereitgestellt, das weiterhin ausgeliefert und unterstützt wird, aber mittlerweile fest als Legacy-Protokoll gilt. Dieses Kapitel enthält auch das Material zu **Legacy-SIP**: den alten `chan_sip`-Treiber und seine `sip.conf`-Konfiguration — in Asterisk 21 entfernt und in Asterisk 22 nicht mehr vorhanden — zusammen mit einem vollständigen Leitfaden zur Migration eines bestehenden `sip.conf`-Systems auf PJSIP. Wenn Sie eine reine SIP-Umgebung auf PJSIP ohne Telefoniekarten, ohne IAX2-Trunks und ohne zu konvertierende Legacy-`sip.conf` betreiben, können Sie dieses Kapitel getrost überspringen.

## Analoge Kanäle (FXO/FXS)

Seit Asterisk 22 werden DAHDI und analoge Telefoniekarten weiterhin vollständig unterstützt, und DAHDI lässt sich nach wie vor mit aktuellen Kernels kompilieren. Da die Mehrheit der neuen Installationen jedoch reines VoIP (SIP-Trunks, PJSIP) verwendet, ist analoge/TDM-Hardware heute eine Nischenwahl — sie findet sich hauptsächlich in Legacy-Umgebungen, bei der Anbindung ländlicher PSTN-Anschlüsse oder in regulierten Märkten. Alles Folgende gilt weiterhin für diese Szenarien.

Es gibt verschiedene Möglichkeiten, das öffentliche Telefonnetz (PSTN) anzubinden. Der beste Weg hängt davon ab, wie die Telefongesellschaft diesen Anschluss in Ihrer Region bereitstellt. Der einfachste Weg ist die Nutzung einer analogen Leitung, ähnlich dem Anschluss, den Sie von zu Hause kennen. In diesem Abschnitt zeigen wir Ihnen, wie Sie analoge Karten von Sangoma™ (ehemals Digium™) und Xorcom™ konfigurieren.

### Lernziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die wichtigsten Begriffe und Akronyme der Telefonie zu erkennen;
- Zu verstehen, wann digitale und analoge Schaltkreise zu verwenden sind;
- Den Unterschied zwischen FXS und FXO zu erkennen; und
- Asterisk für FXS und FXO zu konfigurieren.

### Grundlagen der Telefonie

Die meisten analogen Implementierungen verwenden ein Adernpaar, das als Tip und Ring bezeichnet wird. Wenn eine Schleife geschlossen wird, erhält das Telefon ein Freizeichen von der Vermittlungsstelle (oder der privaten PBX). Die am häufigsten verwendete Signalisierung ist Loop-Start; andere, weniger verbreitete Signalisierungsarten umfassen Ground-Start, das in einigen Ländern verwendet wird. Die drei Kategorien der Signalisierung sind:

- Überwachungssignalisierung (Supervision)
- Adresssignalisierung
- Informationssignalisierung

#### Überwachungssignalisierung

Die wichtigsten Überwachungssignale sind On-Hook, Off-Hook und Ringing. On-Hook – Wenn ein Benutzer den Hörer auflegt, unterbricht die PBX die Verbindung und lässt keinen elektrischen Strom fließen. In diesem Zustand befindet sich der Schaltkreis im On-Hook-Zustand. In dieser Position ist nur der Klingelkreis aktiv. Off-Hook – Vor dem Starten eines Telefonats muss das Telefon in den Off-Hook-Zustand übergehen. Das Abnehmen des Hörers schließt die Schleife und signalisiert der PBX, dass der Benutzer einen Anruf tätigen möchte. Nach Erhalt dieser Anzeige erzeugt die PBX ein Freizeichen, das dem Benutzer signalisiert, dass sie bereit ist, die Zieladresse (d. h. die Telefonnummer) entgegenzunehmen. Ringing – Wenn ein Benutzer ein anderes Telefon anruft, erzeugt es eine Spannung für die Klingel, die den anderen Benutzer über einen eingehenden Anruf warnt. Die Signalisierung variiert je nach Land, mit unterschiedlichen Tönen für verschiedene Länder. Sie können die Töne in Asterisk an Ihr Land anpassen, indem Sie die Datei indications.conf bearbeiten. Zum Beispiel:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Adresssignalisierung

Sie können zwei Arten der Signalisierung für das Wählen verwenden. Die erste und gebräuchlichste ist das Mehrfrequenzwahlverfahren (dtmf), während die andere die Impulswahl ist (verwendet bei alten Wählscheibentelefonen). Telefone haben ein Tastenfeld zum Wählen, und jede Taste ist mit zwei Frequenzen verknüpft: einer hohen und einer niedrigen. Bei der dtmf-Signalisierung zeigt die Kombination dieser Töne an, welche Ziffer gedrückt wird. MFC/R2 verwendet einen Mehrfrequenzton, der sich von dtmf unterscheidet.

#### Informationssignalisierung

Die Informationssignalisierung zeigt den Fortschritt des Anrufs und verschiedene Ereignisse an.

- Freizeichen
- Besetztzeichen
- Rückrufton
- Überlastung (Congestion)
- Ungültige Nummer
- Bestätigungston

### PSTN-Schnittstellen

Wie bei alten PBXs ist es oft erforderlich, die Asterisk-PBX mit dem PSTN zu verbinden. Hier zeigen wir Ihnen, wie das geht. Normalerweise haben Sie drei Optionen für Telefonleitungen.

- Analog: Die gebräuchlichste Form für Privathaushalte und kleine Unternehmen, normalerweise über ein metallisches Adernpaar geliefert.
- Digital: Wird verwendet, wenn viele Leitungen erforderlich sind. Eine digitale Leitung wird normalerweise von einem CSU/DSU oder einem Glasfaser-Multiplexer bereitgestellt. Der Anschluss für den Endbenutzer ist normalerweise ein RJ45. In einigen Ländern werden E1-Leitungen über zwei koaxiale BNC-Anschlüsse bereitgestellt; in diesem Fall benötigen Sie einen Balun, um den Anschluss an die RJ45-Buchse der Telefoniekarte herzustellen.
- SIP: Diese Option wurde in jüngerer Zeit entwickelt. Die Telefonleitung wird über eine Datenverbindung mit SIP-Signalisierung (VoIP) bereitgestellt. Dies ist eine gute Option für Asterisk, da Sie keine Telefoniekarte kaufen müssen. Telefonanrufe werden direkt an den Ethernet-Port geliefert. Ein weiterer Vorteil ist, dass Sie CPU-Ressourcen sparen können, indem Sie das Transcoding von Codecs vermeiden.

### Analoge FXS-, FXO- und E&M-Schnittstellen

Es sind verschiedene Arten von analogen Schnittstellen verfügbar. Es ist grundlegend, die Unterschiede zwischen diesen Schnittstellen zu verstehen, um zu lernen, wie man eine Verbindung zum Telefonnetz sowie zu anderen PBXs herstellt. Hier zeigen wir Ihnen die E&M-Schnittstelle. Obwohl sie derzeit für Asterisk nicht verfügbar ist und von mehreren Herstellern eingestellt wurde, finden Sie möglicherweise Router und PBXs mit dieser Art von Schnittstelle, daher ist es besser zu wissen, womit Sie es zu tun haben.

#### Foreign eXchange (FX)-Schnittstellen

FX-Schnittstellen sind analog. Der Begriff „Foreign eXchange“ wird auf Zugangsleitungen zu einer PSTN-Vermittlungsstelle (CO) angewendet. Foreign eXchange Office (FXO)

![Asterisk zwischen einem analogen Telefon (FXS) und der Telco-Leitung (FXO): Die FXS-Seite liefert Freizeichen und Klingelspannung an das Telefon, während die FXO-Seite das Freizeichen von der Vermittlungsstelle bezieht.](../images/10-legacy-fig01.png)

Die FXO-Schnittstelle wird verwendet, um eine Verbindung zu einer Vermittlungsstelle (CO) oder der Nebenstelle einer anderen PBX herzustellen. Sie kommuniziert direkt mit einer Telefonleitung, die vom PSTN kommt. Eine weitere Option ist der Anschluss der FXO-Schnittstelle an eine bestehende PBX, was die Kommunikation zwischen Asterisk und der Legacy-PBX ermöglicht. Die Verbindung von Asterisk mit einem PBX-Port und die Bereitstellung einer entfernten Nebenstelle mittels VoIP wird oft als Off-Premises Extension (OPX) bezeichnet. Eine FXO-Schnittstelle empfängt ein Freizeichen. Foreign eXchange Station (FXS) Die FXS-Schnittstelle speist ein analoges Telefon, Modem oder Fax. Die FXS liefert das Freizeichen und die Stromversorgung für ein Telefon.

#### Trunk-Signalisierung

- Loop-Start
- Ground-Start
- Kewlstart

Die Verwendung der Kewlstart-Signalisierung in Asterisk ist fast Standard. Kewlstart ist keine Signalisierung an sich, sondern fügt dem Schaltkreis Intelligenz hinzu, indem es überwacht, was auf der anderen Seite passiert. Kewlstart basiert auf Loop-Start. Die meisten Vermittlungsstellen unterstützen diese Funktion nicht, die verwendet wird, um die Auflegen-Benachrichtigung zu erhalten.

- Loopstart: Wird bei den meisten analogen Leitungen verwendet und ermöglicht es dem Telefon, „On-Hook“ und „Off-Hook“ zu signalisieren, und der Vermittlungsstelle, „Ring“ und „No-Ring“ zu signalisieren. Das ist wahrscheinlich das, was die meisten Leute zu Hause haben. Der Name kommt daher, dass die Leitung immer offen ist. Wenn Sie die Schleife schließen, stellt Ihnen die Vermittlungsstelle ein Freizeichen zur Verfügung. Ein eingehender Anruf wird durch eine 100V-Klingelspannung über das offene Adernpaar signalisiert.

![Asterisk als VoIP-Gateway: Ein FXO-Port verbindet sich mit einer Legacy-PBX-Nebenstelle, während ein entfernter Asterisk diese Leitung über IP durch einen FXS-Port an ein analoges Telefon liefert (eine Off-Premises Extension, oder OPX).](../images/10-legacy-fig02.png)

- Groundstart: Ähnlich wie Loopstart. Wenn Sie einen Anruf tätigen möchten, wird eine Seite der Leitung kurzgeschlossen. Wenn die Vermittlungsstelle diesen Zustand identifiziert, kehrt sie die Spannung über das offene Adernpaar um, und dann wird die Schleife geschlossen. Folglich wird die Leitung zuerst belegt, bevor sie dem Anrufer angeboten wird.
- Kewlstart: Fügt den Schaltkreisen Intelligenz hinzu und ermöglicht die Überwachung der anderen Seite. Kewlstart enthält viele Vorteile von Loop-Start.

### Einrichtung der Asterisk-Telefoniekanäle

Um eine Telefonie-Schnittstellenkarte zu konfigurieren, sind mehrere Schritte erforderlich. In diesem Kapitel zeigen wir drei der häufigsten Szenarien:

- Analoge Verbindung mit FXS
- Analoge Verbindung mit FXO
- Verbindung eines Astribank™ mit FXS- und FXO-Schnittstellen

### Konfigurationsverfahren (in beiden Fällen gültig)

Bevor Sie Hardware für Asterisk auswählen, sollten Sie die Anzahl der gleichzeitigen Anrufe, Dienste und Codecs berücksichtigen, die installiert und aktiviert werden sollen. Asterisk ist eine CPU-intensive Anwendung, weshalb wir eine dedizierte Maschine für Asterisk empfehlen. Die Anzahl der im Computer installierten Schnittstellenkarten ist durch die Anzahl der verfügbaren Steckplätze und Interrupts begrenzt. Es ist vorzuziehen, eine einzelne Karte mit acht Sprachschnittstellen zu installieren als zwei Karten mit vier. Eine weitere Option ist die Verwendung einer USB-Channel-Bank, wie die Xorcom Astribank. Kürzlich haben einige Hersteller (z. B. CIANET) begonnen, TDMoE-Channel-Banks zu produzieren, was es noch einfacher macht, Dutzende von analogen Schnittstellen anzuschließen.

![Eine Xorcom Astribank: eine 19-Zoll-Rack-montierbare USB-Channel-Bank, die Dutzende von FXS/FXO-Ports (hier eine 32-Port-Einheit) bereitstellt, ohne PCI-Steckplätze im Host zu belegen.](../images/10-legacy-fig03.png)

#### Beispiel 1: Eine FXO-, eine FXS-Installation

In diesem Beispiel verwenden wir eine Sangoma TDM400 Telefonie-Schnittstellenkarte (früher als Digium TDM400 verkauft) mit einem FXS- und einem FXO-Modul. Die erforderlichen Schritte sind unten aufgeführt:

1. Installieren Sie die analoge Karte FXS, FXO oder beides.
2. Konfigurieren Sie die Datei `/etc/dahdi/system.conf` (früher `/etc/zaptel.conf`).
3. Generieren Sie die Konfigurationsdateien mit `dahdi_genconf`.
4. Laden Sie den Treiber für die DAHDI-Schnittstelle.
5. Führen Sie `dahdi_test` aus, um Interrupt-Verluste zu überprüfen.
6. Führen Sie `dahdi_cfg` aus, um den Treiber zu konfigurieren.
7. Konfigurieren Sie den DAHDI-Kanal in der Datei `chan_dahdi.conf`, dann laden Sie Asterisk.

##### Schritt 1: Installieren Sie die TDM400-Karte

Die TDM404P-Karte enthält FXS- und FXO-Module. Schließen Sie die FXS (S110M, grün) und FXO (X100M, rot) Module an. Wenn Sie FXS-Module verwenden, schließen Sie die Karte direkt über einen Molex-Anschluss an die Stromquelle an. Bitte tragen Sie einen elektrostatischen Schutz, bevor Sie Schnittstellenkarten handhaben, um Schäden an der Hardware zu vermeiden. Sangoma (ehemals Digium) Analogkarten unterstützen auch ein Hardware-Echokompensationsmodul VPMADT032.

##### Schritt 2: Generieren Sie die Konfiguration mit dahdi_genconf

Die gute Nachricht bei der Konfiguration ist das neue Dienstprogramm `dahdi_genconf`, das automatisch die DAHDI-Schnittstellen erkennt und die Konfiguration generiert. Das Dienstprogramm generiert zwei Dateien:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (mit der Option `users`)
- Alle diese Dateien verwenden die Option `chan_dahdi full`

Bevor Sie `dahdi_genconf` ausführen können, ist es wichtig, die Datei `genconf_parameters` (oft als `gen_parameters.conf` bezeichnet) zu konfigurieren:

![Eine Sangoma/Digium TDM404P Analogkarte: Bis zu vier FXS- oder FXO-Module werden in die nummerierten Ports gesteckt, mit einer optionalen Hardware-Echokompensations-Tochterkarte und einem dedizierten 12V-Stromanschluss für FXS-Module.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

Die Datei `genconf_parameters` lässt Sie Ihre Konfiguration anpassen. Die wichtigsten Parameter für analoge Leitungen sind:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Warnung: Es ist erforderlich, dass Sie zumindest den Echokompensationsalgorithmus für die Kanäle konfigurieren. Der Parameter base_exten definiert den grundlegenden Dialplan für FXS-Nebenstellen. In diesem Fall erhält der erste FXS-Kanal die Nebenstellennummer 4000, der zweite 4001, und so weiter. Der Kontext, in dem die Leitungen (context_phones) und Trunks (context_lines) erstellt werden, ist sehr wichtig. Nach dem Generieren der Dateien sollten Sie die Datei `/etc/asterisk/dahdi-channels.conf` in die Datei `/etc/asterisk/chan_dahdi.conf` einbinden:

```
#include dahdi-channels.conf
```

Hinweis: Analoge Signalisierung ist etwas verwirrend; sie ist immer das Inverse der Karte. FXS-Karten werden mit FXO signalisiert, während FXO-Karten mit FXS signalisiert werden. Asterisk spricht mit diesen Geräten, als ob es sich auf der gegenüberliegenden Seite befände.

##### Schritt 3: Laden Sie die Kernel-Treiber

Jetzt müssen Sie das Modul chan_dahdi und den zugehörigen Karten-Kernel-Treiber laden. Verwenden Sie dahdi_hardware, um Ihre Karte und den Treibernamen zu erkennen. Zum Beispiel:

- Karten-Treiber-Beschreibung
- TE410P wct4xxp 4xE1/T1-3.3V PCI
- TE405P wct4xxp 4xE1/T1-5V PCI
- TDM400P wctdm 4 FXS/FXO
- T100P wct1xxp 1 T1 E100P wctlxxp 1 E1 X100P wcfxo 1 FXO

Befehle zum Laden der Treiber:

```
modprobe dahdi
modprobe wctdm
```

##### Schritt 4: Verwenden Sie das Dienstprogramm dahdi_test

Ein wichtiges Dienstprogramm ist dahdi_test, das verwendet wird, um Interrupt-Verluste in der DAHDI-Karte zu überprüfen. Probleme mit der Audioqualität hängen oft mit Interrupt-Konflikten zusammen. Um zu überprüfen, ob Ihre DAHDI-Karte keinen Interrupt mit anderen Karten teilt, verwenden Sie den folgenden Befehl:

```
#cat /proc/interrupts
```

Sie können die Anzahl der Interrupt-Verluste mit dem Dienstprogramm dahdi_test überprüfen, das mit den DAHDI-Karten kompiliert wurde. Eine Zahl unter 99,987% deutet auf mögliche Probleme hin.

##### Schritt 5: Verwenden Sie das Dienstprogramm dahdi_cfg, um den Treiber zu konfigurieren

DAHDI hat ein ungewöhnliches System zum Laden der Treiber. Konfigurieren Sie zuerst /etc/dahdi/system.conf und wenden Sie diese Konfigurationen dann mit dahdi_cfg auf den DAHDI-Treiber an. In diesem Fall wird dahdi_cfg verwendet, um die Signalisierung für die FX-Schnittstellen zu konfigurieren. Um die Ergebnisse zu sehen, können Sie „-vvvvv“ an den Befehl für Verbose anhängen.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

Wenn die Kanäle erfolgreich geladen wurden, sehen Sie eine Ausgabe ähnlich der oben gezeigten. Benutzer konfigurieren chan_dahdi.conf oft falsch mit invertierter Signalisierung zwischen den Kanälen. Wenn dies passiert, sehen Sie eine Meldung wie die unten gezeigte:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

Nach erfolgreicher Konfiguration der Hardware können Sie mit der Asterisk-Konfiguration fortfahren.

##### Schritt 6: Konfigurieren Sie die Datei /etc/asterisk/chan_dahdi.conf

Es klingt seltsam, aber nach der Konfiguration von /etc/dahdi/system.conf haben Sie die Karte selbst konfiguriert. DAHDI kann für andere Zwecke verwendet werden, wie Routing und SS7. Um es mit Asterisk zu verwenden, müssen Sie die Asterisk DAHDI-Kanäle konfigurieren. Jeder Kanal in Asterisk muss definiert werden; SIP/PJSIP-Kanäle werden in pjsip.conf definiert (Hinweis: chan_sip und sip.conf wurden in Asterisk 21 entfernt), während TDM-Kanäle in chan_dahdi.conf definiert werden. Dies erstellt die logischen TDM-Kanäle, die in Ihrem Dialplan verwendet werden sollen.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Konfigurationsoptionen

In der Datei chan_dahdi.conf sind mehrere Optionen verfügbar. Eine Beschreibung aller Optionen wäre langweilig und kontraproduktiv; stattdessen konzentrieren wir uns auf die wichtigsten Optionsgruppen, um ein einfaches Verständnis zu ermöglichen.

#### Allgemeine Optionen (kanalunabhängig)

Diese Optionen funktionieren für jeden Kanal: context: Definiert den eingehenden Kontext.

```
context=default
```

channel: Definiert den Kanal oder Kanalbereich. Jede Kanaldefinition erbt Optionen, die vor der Deklaration definiert wurden. Kanäle können einzeln oder in derselben Zeile durch Kommas getrennt identifiziert werden. Bereiche können mit „-“ definiert werden.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Ermöglicht es, Kanäle als Gruppe zu behandeln. Wenn Sie eine Gruppennummer anstelle einer Kanalnummer wählen, wird der erste verfügbare Kanal verwendet. Wenn es sich bei den Kanälen um Telefone handelt, klingeln bei einem Anruf einer Gruppe alle Telefone gleichzeitig. Mit Kommas können Sie mehr als eine Gruppe für denselben Kanal angeben.

```
group=1
group=3,5
```

language: Schaltet die Internationalisierung ein und konfiguriert eine Sprache. Diese Funktion konfiguriert Systemmeldungen für eine bestimmte Sprache. Englisch ist die einzige Sprache mit vollständigen Prompts, die über die Standardinstallation verfügbar sind. musiconhold: Wählt die Music-on-Hold-Klasse aus.

#### Caller-ID-Optionen

Es gibt viele Caller-ID-Optionen. Einige können deaktiviert werden, obwohl die meisten standardmäßig aktiviert sind. usecallerid: Aktiviert oder deaktiviert die Caller-ID-Übertragung für die nachfolgenden Kanäle (Yes/No). Hinweis: Wenn Ihr System zwei Klingelzeichen erhält, bevor es antwortet, versuchen Sie, diese Funktion zu deaktivieren. Es sollte sofort antworten. hidecallerid: Definiert, ob die ausgehende Caller-ID ausgeblendet werden soll oder nicht (Yes/No). callerid: Konfiguriert eine Caller-ID-Zeichenfolge für einen bestimmten Kanal. Der Anrufer kann mit asreceived konfiguriert werden. Dies wird meistens in Trunk-Schnittstellen verwendet, um die eingehende Caller-ID anzuzeigen.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Unterstützt Caller-ID während des Anklopfens. useincomingcalleridondahditransfer: Verwendet die eingehende Caller-ID bei einer Weiterleitung.

#### Anklopfen (Call Waiting)

Asterisk unterstützt Anklopfen bei FXS-Kanälen. Der Benutzer erhält einen Anklopfton, wenn jemand versucht, die Nebenstelle zu erreichen. Um Anklopfen zu aktivieren:

```
callwaiting=yes
```

Um die Caller-ID beim Anklopfen zu unterstützen:

```
callwaitingcallerid=yes
```

#### Audioqualitätsoptionen

Die Anpassung der Echokompensation ist halb Technik, halb Kunst. Diese Optionen passen bestimmte Asterisk-Parameter an, die die Audioqualität in den DAHDI-Kanälen beeinflussen. Sie können helfen, die Audioqualität bei analogen Schnittstellen zu verbessern.

#### Das Dienstprogramm fxotune

fxotune ist ein Dienstprogramm, das zur Feinabstimmung bestimmter Parameter für FXO-Module verwendet wird. Diese Feinabstimmung ist erforderlich, um Impedanzfehlanpassungen auszugleichen, die durch die Hybridschaltung verursacht werden. Das Dienstprogramm hat drei Betriebsmodi:

- Erkennung (-i): erkennt und korrigiert die vorhandenen FXO-Kanäle und speichert die Konfiguration in

```
fxotune.conf
```

- Dump-Modus (-d): generiert die Wellenformdateien für fxotune_dump.vals
- Start-Modus (-s): liest die Datei fxotune.conf und wendet sie auf die FXO-Module an

Es ist wichtig zu verstehen, dass Sie die Anweisung fxotune –s beim Systemstart einfügen müssen, bevor Sie Asterisk starten:

```
#modprobe dahdi
#modprobe wctdm
#fxotune-s
```

### Echokompensation

Die meisten Echokompensationsalgorithmen arbeiten, indem sie mehrere Kopien des empfangenen Signals erzeugen, wobei jede um eine bestimmte Zeitspanne verzögert wird. Die Anzahl der Taps des Filters bestimmt die Größe der Echoverzögerung, die kompensiert werden muss. Diese verzögerten Kopien werden dann angepasst und vom empfangenen Signal subtrahiert. Der Trick besteht darin, nur das verzögerte Signal anzupassen, um das Echo zu entfernen, ohne zu viele CPU-Zyklen zu verbrauchen. Aus Sicht der Benutzer ist es wichtig, einen geeigneten Echokompensationsalgorithmus zu wählen. Der Standard ist MG2; es sind jedoch zwei weitere Optionen verfügbar: die High Performance Echo Cancellation (HPEC) von Sangoma (ehemals Digium) und die Open-Source-Echokompensation (OSLEC), die von David Rowe entwickelt wurde.

OSLEC (https://www.rowetel.com/?page_id=454) wurde in den Linux-Kernel integriert — es befindet sich im `drivers/staging/echo`-Bereich des Kernels — und DAHDI wird dagegen kompiliert, anstatt einen separaten Download bereitzustellen. Um den Echokompensationsalgorithmus zu ändern, setzen Sie den Parameter `echo_can` in `/etc/dahdi/system.conf`. Zum Beispiel:

```
echo_can=oslec
```

Die Echokompensation in Asterisk wird durch drei Parameter in der Datei /etc/asterisk/chan-

```
dahdi.conf.
```

echocancel: Deaktiviert oder aktiviert die Echokompensation. Sie sollten diese Funktion aktiviert lassen. Sie akzeptiert „yes“ oder die Anzahl der Taps. Erklärung: Wie funktioniert Echokompensation? Die meisten Echokompensationsalgorithmen arbeiten, indem sie mehrere Kopien eines empfangenen Signals erzeugen, wobei jede um ein kleines Intervall verzögert wird. Dieser kleine Fluss wird als „Tap“ bezeichnet. Die Anzahl der Taps bestimmt die Echoverzögerung, die kompensiert werden kann. Diese Kopien werden verzögert, angepasst und vom ursprünglichen Signal subtrahiert. Der Trick besteht darin, das verzögerte Signal genau auf das Maß anzupassen, das erforderlich ist, um das Echo zu entfernen. echocancelwhenbridged: Aktiviert oder deaktiviert den Echokompensator während eines reinen TDM-Anrufs. Dies ist normalerweise nicht erforderlich. rxgain: Passt die Audio-Empfangsverstärkung an, um die Empfangslautstärke zu erhöhen oder zu verringern (-100% bis 100%). txgain: Passt die Audio-Übertragungsverstärkung an, um die Übertragungslautstärke zu erhöhen oder zu verringern (-100% bis 100%). Zum Beispiel:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Abrechnungsoptionen

Diese Optionen ändern die Art und Weise, wie Anrufinformationen in der Datenbank für Anrufdetails (CDR) aufgezeichnet werden. amaflags: Konfiguriert die AMA-Flags, die die CDR-Kategorisierung beeinflussen. Sie akzeptiert die folgenden Werte:

- billing
- documentation
- omit
- default

accountcode: Konfiguriert einen Kontocode für einen bestimmten Kanal. Er kann jeden alphanumerischen Wert enthalten — normalerweise die Abteilung oder den Benutzernamen.

```
accountcode=finance
amaflags=billing
```

### Optionen für den Anruffortschritt

Diese Elemente werden verwendet, um Informationen über den Fortschritt des Anrufs zu erhalten. Bei öffentlichen Schnittstellen kann es nützlich sein, den Anruffortschritt zu erkennen und festzustellen, ob der Anruf beantwortet wurde oder besetzt war. Die Besetzterkennung ist hochgradig experimentell und durch spezifische Parameter reguliert.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Diese Parameter (oben) geben an, ob die Schnittstelle versuchen soll, das Besetztzeichen zu erkennen, wie viele Töne für eine erfolgreiche Erkennung verwendet werden und wie das Besetztmuster aussieht. Die Besetzterkennung ist weitgehend experimentell, und einige zusätzliche Parameter können im Makefile geändert werden. Um die Antwort eines Anrufs zu erkennen, was für eine präzise Abrechnung unerlässlich ist, ist es möglich, die Polaritätsumkehr zu verwenden, um die genaue Antwortzeit zu signalisieren. Dies ist wichtig, wenn Sie planen, den Anruf in Rechnung zu stellen oder einfach eine präzise Abrechnung zum Vergleich wünschen. Normalerweise müssen Sie die Telefongesellschaft kontaktieren, um diesen Dienst anzufordern.

```
answeronpolarityswitch=yes
```

In einigen Ländern ist es möglich, das Auflegen des Anrufs ebenfalls durch Polaritätsumkehr zu erkennen.

```
hanguponpolarityswitch=yes
```

#### Optionen für Telefone

Diese Optionen werden für Telefone verwendet, die an die FXS-Schnittstellen angeschlossen sind. Alle Funktionen, die an analoge Telefone geliefert werden, die direkt an die DAHDI-Schnittstellen angeschlossen sind, werden von Asterisk gesteuert. Adsi (Analog Display Services Interface): Dies ist eine Reihe von Telekommunikationsstandards, die von einigen Telefongesellschaften verwendet werden, um Dienste wie Ticketkauf anzubieten. cancallforward: Aktiviert oder deaktiviert die Anrufweiterleitung (*72 zum Aktivieren und *73 zum Deaktivieren). calleridcallwaiting: Aktiviert die Caller-ID, die während einer Anklopfanzeige empfangen wird (Yes/No). immediate: Im Immediate-Modus springt der Kanal sofort zur „s“-Nebenstelle im definierten Kontext, anstatt ein Freizeichen bereitzustellen. Dies wird verwendet, um Hotlines zu erstellen. threewaycalling: Aktiviert oder deaktiviert die Drei-Wege-Konferenz. mailbox: Warnt den Benutzer über verfügbare Voicemail-Nachrichten. Es kann ein akustisches Signal oder eine visuelle Anzeige sein (wenn das Telefon diese Funktion unterstützt). Das Argument ist die Mailbox-Nummer. callgroup: Gruppieren Sie Telefone zum Wählen oder Abheben. pickupgroup: Gruppe von Telefonen für die Anrufannahme.

### Nützliche DAHDI CLI-Befehle

Sobald Asterisk mit geladenen DAHDI-Kanälen läuft, können Sie den Kanalstatus über die Asterisk CLI überprüfen. Diese Befehle bleiben in Asterisk 22 aktuell:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI-Kanalformat

DAHDI-Kanäle verwenden das folgende Format im Dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

Zum Beispiel:

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
```

## Digitale Kanäle (E1/T1/PRI / TDM)

Seit Asterisk 22 werden DAHDI und libpri weiterhin vollständig unterstützt, aber digitale TDM-Trunks (E1/T1/ISDN PRI) werden bei neuen Installationen zunehmend durch SIP-Trunks ersetzt. Dieser Abschnitt bleibt voll anwendbar, wo TDM-Konnektivität erforderlich ist; in Greenfield-Umgebungen liefert SIP-Trunking (Kapitel 3) normalerweise die gleiche Kanaldichte ohne Telefonie-Hardware.

Digitale Kanäle sind extrem verbreitet, daher müssen Sie lernen, wie man diese Kanäle implementiert, wenn Sie sich auf große Kunden konzentrieren möchten. Wenn die Anzahl der Kanäle hoch ist — normalerweise mehr als 8 — ist es ziemlich üblich, digitale Schnittstellen wie T1/E1/J1 zu verwenden. T1 ist in den USA sehr verbreitet, während E1 in Europa und J1 in Japan üblich ist. Diese Arten von Kanälen ermöglichen eine gute Dichte an Schaltkreisen — 24 pro T1-Kanal und 30 für E1-Kanäle. In Lateinamerika, China und Afrika ist es üblich, eine Art von kanalassoziierter Signalisierung (CAS) zu verwenden, die als MFC/R2 bekannt ist. Dieses Kapitel untersucht, wie MFC/R2 unter Verwendung der Bibliothek OpenR2 implementiert wird. In den USA und Europa ist das Integrated Services Digital Network (ISDN) PRI die gebräuchlichste Signalisierung. Das Kapitel wird auch das ISDN Basic Rate Interface (BRI) diskutieren, das in Europa bei Anwendungen im mittleren Bereich sehr verbreitet ist. Alle Beispiele im Buch konzentrieren sich auf DAHDI-Kanäle. Einige Karten werden unter Verwendung proprietärer Kanäle implementiert, daher erkundigen Sie sich bitte bei Ihrem Hersteller nach weiteren Details zur Konfiguration Ihrer spezifischen Karte.

### Lernziele

Am Ende dieses Kapitels werden Sie in der Lage sein:

- Die wichtigsten Begriffe der digitalen Telefonie zu erkennen
- CAS- und CCS-Signalisierung zu unterscheiden
- R2- und ISDN-Signalisierung zu unterscheiden
- Schnittstellen mit ISDN-Signalisierung zu konfigurieren
- Schnittstellen mit R2-Signalisierung zu konfigurieren

### E1/T1-Digitallinien

Digitale E1/T1-Leitungen sind eine Option, wann immer Sie eine große Anzahl von Kanälen implementieren müssen. Ein einzelner E1-Schaltkreis ist zu 30 gleichzeitigen Anrufen fähig, und Sie können Funktionen wie Direct Inward Dial (DID), Caller ID (Anruferidentifikation) und erweiterte Signalisierung haben. Die E1/T1-Leitung kann auf verschiedene Weise in Ihrem Unternehmen ankommen, unter Verwendung von verdrillten Paaren, Glasfaser und Mikrowellen, abhängig von Ihrem Land. Digitale Leitungen werden Ihrem Unternehmen über UTP, Glasfaser oder Mikrowellen geliefert. Modems und Multiplexer (MUX) werden verwendet, um die physische Leitung bereitzustellen. Die Verbindung zu einer T1-Leitung basiert immer auf einem RJ45-Anschluss. E1-Leitungen können jedoch auch über BNC bereitgestellt werden. Es ist sehr wichtig, im Voraus zu wissen, welche Art von Anschluss Sie erhalten werden, hauptsächlich bei E1-Leitungen. Normalerweise wird die gesamte Ausrüstung bis zum RJ45 von der Telefongesellschaft bereitgestellt.

![Wie E1/T1-Schaltkreise bereitgestellt werden: Die Telefongesellschaft kann den Trunk über UTP-Kupfer (HDSL-Modem für E1 oder eine direkte Kartenverbindung für T1), über Glasfaser durch einen optischen Multiplexer oder über eine Mikrowellen-Funkverbindung liefern.](../images/10-legacy-fig05.png)

![UTP oder BNC? Die meisten digitalen Karten verwenden RJ45 (UTP)-Anschlüsse, aber einige E1-Leitungen werden über duale BNC-Koaxialkabel geliefert, in diesem Fall wird ein Balun benötigt, um das Koaxialpaar an die RJ45-Buchse der Karte anzupassen.](../images/10-legacy-fig06.png)

#### Wie wird die Stimme in Bits umgewandelt?

Das analoge Signal wird 8.000 Mal pro Sekunde abgetastet, um eine digitale Version der analogen Stimme zu erstellen. Diese Kodierung wird als Pulscodemodulation (PCM) bezeichnet. In den USA und Japan wird das Signal unter Verwendung von law kodiert (in Asterisk als ulaw bezeichnet). Im Rest der Welt ist die Kodierung alaw.

![Pulscodemodulation (PCM): Das 4 kHz analoge Sprachsignal wird 8.000 Mal pro Sekunde abgetastet (Nyquist) und in einen digitalen 64 Kbps-Bitstrom kodiert.](../images/10-legacy-fig07.png)

#### Zeitmultiplexverfahren (Time Division Multiplexing)

Analoge Leitungen sind sinnvoll, wenn Sie nur wenige Kanäle benötigen. Bei Verwendung von Zeitmultiplex (TDM) ist es möglich, mehrere Kanäle in eine einzige Datenverbindung zu packen. Wenn Sie eine große Anzahl von Schaltkreisen wünschen, stellt Ihnen die Telefongesellschaft normalerweise einen digitalen Trunk zur Verfügung, bei dem es sich um einen Datenstrom handelt, in dem die Stimme in einem digitalen Format unter Verwendung von PCM transportiert wird. Jeder Zeitschlitz verwendet 64 Kbps Bandbreite, um einen einzelnen Sprachkanal zu transportieren.

![Zeitmultiplex in E1 und T1: Ein E1-Frame trägt 32 Zeitschlitze bei 2048 Kbps (DS0 #0 für Frame-Synchronisation, DS0 #16 für Signalisierung), während ein T1-Frame 24 Zeitschlitze bei 1544 Kbps trägt, wobei ein Bit für Synchronisation und ein Robbed-Bit-Schema für Signalisierung verwendet wird.](../images/10-legacy-fig08.png)

In den USA ist der gebräuchlichste digitale Trunk T1, der über 24 verfügbare Leitungen verfügt; in Europa und Lateinamerika haben E1-Trunks 30 Leitungen. Einige Unternehmen bieten einen fraktionierten T1/E1 mit weniger Kanälen an. Robbed-Bit-Signalisierung Manchmal verwendet ein T1-Trunk ein Robbed-Bit-Schema, bei dem ein Bit für die Signalisierung ausgeliehen wird. Bei T1-Trunks wird der Daten-/Sprachkanal mit 56 Kbps auf jedem Zeitschlitz übertragen. Wie Sie sehen können, verliert der T1-Schaltkreis bei Verwendung des Robbed-Bits keine zwei Schlitze für Synchronisation und Signalisierung.

#### T1/E1-Leitungscode

T1s und E1s sind eigentlich Datenstrom-Schaltkreise und haben eine Datenkodierung, die bestimmt, wie die Bits interpretiert werden. Für E1s ist der gebräuchlichste Leitungscode HDB3 für Layer 1 und CCS für Layer 2. Der einfachste Weg, um zu wissen, wie Ihr digitaler Trunk konfiguriert ist, besteht darin, die Telefongesellschaft nach diesen Informationen zu fragen. Sie benötigen diese Informationen, um die Datei /etc/dahdi/system.conf zu konfigurieren.

#### T1/E1-Signalisierung

Es ist wichtig zu verstehen, dass T1/E1-Leitungen unter Verwendung verschiedener Arten von Signalisierung geliefert werden können, wie z. B.:

- T1 mit Robbed-Bit-Signalisierung
- T1 mit ISDN-Signalisierung
- E1 mit MFC/R2 (CAS - Channel Associated Signaling)
- E1 mit ISDN-Signalisierung

ISDN wird oft in Europa und den USA verwendet. Es ist ein digitales Sprachnetzwerk, das 1984 von der International Telecommunications Union (ITU) standardisiert wurde. ISDN bietet zwei Arten von Kanälen:

- Bearer-Kanäle o Stimme o Daten
- Datenkanäle o Out-of-Band-Signalisierung o LAPD-Signalisierung o Q.931

Normalerweise wird eine ISDN-Leitung über zwei physische Mittel bereitgestellt:

- Basic Rate Interface (BRI) o Bekannt als 2B+D o Zwei Bearer-Kanäle (64K) und ein Datenkanal (16K) o Verwendet ein Kupferadernpaar mit 148Kbps.
- Primary Rate Interface (PRI) o Bereitgestellt über einen T1/E1-Trunk o 23B+D für T1s o 30B+D für E1s

Manchmal verwenden E1-Schaltkreise ein CAS-Signalisierungsschema namens MFC/R2, das von der ITU als Standard bekannt als Q.421/Q441 definiert wurde. Dies findet sich häufig in Lateinamerika und Asien. Mehrere Telefongesellschaften in diesen Ländern verwenden angepasste Varianten von MFC/R2. Daher müssen Sie die korrekte Ländervariante kennen, damit es funktioniert.

### ISDN BRI

Kanäle mit ISDN BRI-Signalisierung sind in Europa sehr beliebt. Die meisten ISDN BRI-Karten für Asterisk unterstützen eine S/T-Schnittstelle mit NT- und TE-Funktionen. Die TE-Verbindung (Terminal) wird verwendet, um eine Verbindung zur Telefongesellschaft oder zu anderen PBXs herzustellen, die als Netzabschluss (NT) konfiguriert sind. Der NT wird verwendet, um Telefone und PBXs anzuschließen, die als TE konfiguriert sind. ISDN BRI bietet zwei Daten-/Sprachkanäle und einen Signalisierungskanal. ISDN BRI-Karten sind von mehreren Anbietern von Schnittstellenkarten für Asterisk erhältlich.

### Auswahl einer Telefoniekarte für Ihren Asterisk-Server

Es gibt mehrere Hersteller für digitale Karten, die mit Asterisk kompatibel sind. Die Wahl einer Karte hängt von einigen der folgenden Faktoren ab:

#### Datenbus

Es gibt verschiedene Arten von Bussen auf Ihrem PC. Es ist sehr wichtig, dass Sie die richtige Karte für Ihren Server haben. Der folgende Überblick skizziert die am häufigsten verwendeten Karten:

- 32-Bit PCI 5V, in den meisten Computern zu finden, einschließlich Desktops o Sangoma (ehemals Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410 und TC400 o Sangoma A101, A102 und A104
- 32/64-Bit PCI 3.3V, hauptsächlich in Servern zu finden o Sangoma (ehemals Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410 und TC400
- PCI Express, auf Desktops und Servern zu finden o Sangoma (ehemals Digium) TE420, TE220, TE121, AEX2400 und AEX800 o Sangoma A101, A102 und A104

Diese Kartenfamilien stammen von Digium, das Sangoma 2018 übernommen hat; sie werden jetzt unter der Marke Sangoma verkauft und unterstützt. Viele der hier aufgeführten älteren SKUs wurden eingestellt, bestätigen Sie daher vor dem Kauf die aktuelle Modellverfügbarkeit unter www.sangoma.com.

- MiniPCI, auf eingebetteten Systemen zu finden o OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI) und B400M(ISDN BRI)
- USB 2.0, in den meisten modernen PCs zu finden. Lösungen auf USB-Basis ermöglichen eine große Dichte an analogen und digitalen Kanälen. Dieser Bus unterstützt 480 Mbps, und jeder Sprachkanal belegt 64 Kbps. Bei Verwendung von USB-Hubs ist es möglich, Dichten von bis zu tausend analogen Ports an einem einzigen Port zu erreichen. o Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. Der größte Vorteil von Ethernet besteht darin, dass die Karte von mehr als einem Server verbunden werden kann. Hochverfügbarkeitslösungen sind normalerweise die Kernanwendung für diese Geräte. Die Stärke dieser Lösung ist die Verwendung von Servern ohne freie PCI-Steckplätze oder Blade-Servern. o Redfone FoneBridge (bis zu vier E1-Schaltkreise)

### Verwendung von Hardware-Echokompensation

Hardware-Echokompensation reduziert die Last auf der Host-CPU. Bei Karten mit mehr als einer E1-Schnittstelle kann Hardware-Echokompensation helfen, Ihren Prozessor zu entlasten. Neue verbesserte Software-Echokompensatoren wie OSLEC reduzieren den Bedarf an einem Hardware-Echokompensator. Um zwischen Hardware- und Software-Echokompensatoren zu wählen, sollten Sie die verfügbare Rechenleistung Ihres Servers und die Anzahl der E1-Schaltkreise berücksichtigen. Ein Echokompensationsprozess kann bis zu neun MIPS (Millionen Instruktionen pro Sekunde) pro Sprachkanal mit 128 Taps Amplitude unter Verwendung von OSLEC verbrauchen (Referenz: Xorcom Ltd.). Wenn Sie 1 CPU-Zyklus pro Instruktion berücksichtigen (was basierend auf dem Prozessor und der Softwareimplementierung selbst nicht immer korrekt ist), sprechen wir von 1,080 GHz für vier E1s.

#### Art der Signalisierung

Die Auswahl der Signalisierungsart (z. B. T1 CAS, T1 PRI, E1 CAS R2 oder E1 CAS ISDN) ist keine leichte Aufgabe. Es hängt wirklich davon ab, was in Ihrer Region verfügbar ist und zu welchem Preis. Common Channel Signaling (CCS) ist oft besser als Channel Associated Signaling (CAS). Es ist jedoch oft nicht verfügbar. In den USA können Sie normalerweise wählen, da die meisten Telefongesellschaften T1 CAS für normale Benutzer und T1 PRI für fortgeschrittene Benutzer (z. B. Callcenter) anbieten. In Lateinamerika ist E1 CAS R2 vorherrschend, aber ISDN PRI ist in einigen Städten verfügbar.

![Die DAHDI-Softwarearchitektur: Asterisk spricht mit dem `chan_dahdi`-Kanaltreiber, der wiederum die Protokollbibliotheken libpri (ISDN), libopenr2 (MFC/R2) und libss7 (SS7) lädt; diese sitzen auf der `/dev/dahdi`-Schnittstelle, dem DAHDI-Kernel-Treiber und dem kartenspezifischen Schnittstellen-Kernel-Treiber.](../images/10-legacy-fig09.png)

Die Implementierung von R2 ist erforderlich für die Installation einer Bibliothek namens OpenR2 (www.libopenr2.org), die von Moises Silva entwickelt wurde, und zum Patchen von Asterisk vor der Installation — ein einfaches Verfahren, das später in diesem Kapitel gezeigt wird. Die Bibliothek hat mehrere Tests bestanden und ist bei mehreren unserer Kunden im produktiven Einsatz. ISDN ist meiner Meinung nach immer die beste Wahl, falls verfügbar. Einige Anbieter haben möglicherweise Zugriff auf das Signaling System 7 (SS7), eine CCS-Signalisierung, die zwischen Telefongesellschaften verfügbar ist. Proprietäre und Open-Source-Lösungen sind für SS7 verfügbar. Die Bibliothek libss7 wird verwendet, um SS7 auf Asterisk zu unterstützen.

### Einrichtung der Asterisk-Telefoniekanäle

Die Konfiguration einer Telefonie-Schnittstellenkarte umfasst mehrere notwendige Schritte. In diesem Kapitel zeigen wir drei der häufigsten Szenarien:

- Digitale Verbindung mit ISDN PRI
- Digitale Verbindung mit ISDN BRI
- Digitale Verbindung mit MFC/R2

Es gibt zwei Möglichkeiten, DAHDI-Kanäle zu konfigurieren. Die erste besteht darin, sie manuell mit voller Kontrolle über alle Parameter zu konfigurieren. Die zweite Möglichkeit besteht darin, das Dienstprogramm dahdi_genconf zu verwenden, um die Karten zu erkennen und zu konfigurieren.

#### Automatische Erkennung und Konfiguration

Dank des DAHDI-Entwicklungsteams haben wir jetzt eine automatische Erkennung und Konfiguration der Karten. Schritt 1: Um die Konfiguration automatisch zu generieren, verwenden Sie das Dienstprogramm dahdi_genconf, das die Karte erkennt und die Dateien /etc/dahdi/system.conf und dahdi-channels.conf generiert.

```
dahdi_genconf
```

Schritt 2: Fügen Sie in der letzten Zeile der Datei chan_dahdi.conf die Datei dahdi-channels.conf ein

```
#include dahdi_channels.conf
```

Schritt 3: Kommentieren Sie alle ungenutzten Module in der Datei modules aus oder verwenden Sie einfach:

```
dahdi_genconf modules
```

#### Manuelle Konfiguration

Eine weitere Option ist die manuelle Konfiguration der Schnittstellen. Nachfolgend finden Sie einige Beispiele für die Konfiguration von DAHDI-Kanälen.

##### Beispiel #1 – Zwei T1/E1-Kanäle mit ISDN

Erforderliche Schritte:

1. Installation von TE205P oder TE210P
2. Konfiguration der Datei `/etc/dahdi/system.conf`
3. Laden des DAHDI-Treibers
4. Dienstprogramm `dahdi_test`
5. Dienstprogramm `dahdi_cfg`
6. Konfiguration der Datei `chan_dahdi.conf`
7. Asterisk-Laden und Testen

Schritt 1: Installation von TE205P. Vor der Installation von TE205P ist es wichtig, die Unterschiede zwischen den Karten TE205P und TE210P zu verstehen. Die Karte TE210P verwendet einen 64-Bit-Bus mit 3,3 Volt, der fast nur auf Server-Motherboards zu finden ist. Seien Sie vorsichtig, wenn Sie diese Schnittstellenkarte spezifizieren; stellen Sie sicher, dass Ihre Hardware einen 64-Bit, 3,3V-Bus unterstützt. Die Karte TE205P verwendet einen 5V-PCI-Bus, der oft in Desktop-Computern zu finden ist. Wir haben für dieses Beispiel die Schnittstellenkarte TE205P mit zwei Spans gewählt, da es einfacher ist, sie auf eine Ein-Span-Karte zu reduzieren oder auf eine Vier-Span-Karte zu erweitern. Diese Karten werden jetzt unter der Marke Sangoma (ehemals Digium) verkauft.

![Eine Sangoma/Digium TE205P Dual-Span E1/T1-Karte: Die beiden RJ45-Ports akzeptieren die digitalen Trunks, und ein On-Board-Jumper (der E1/T1/J1-Wahlschalter) stellt den Leitungsstandard ein.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

Die Konfiguration von digitalen TDM-Karten unterscheidet sich ein wenig von der Konfiguration ihrer analogen Gegenstücke. Zuerst müssen wir die Board-Spans und dann die Kanäle konfigurieren. Spans werden sequenziell nummeriert, abhängig von der Erkennungsreihenfolge der Karten. Mit anderen Worten, wenn Sie mehr als eine Schnittstellenkarte haben, ist es schwer zu wissen, welcher Span zu welcher gehört. Verwenden Sie dahdi_hardware, um zu überprüfen, welche Hardware auf jedem Span installiert ist. Beispiel #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

Beispiel #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Beispiel #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Schritt 3: Laden der Kernel-Treiber Überprüfen Sie mit dahdi_hardware, welchen Treiber Sie installieren müssen.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Zum Laden verwenden Sie:

```
modprobe dahdi
modprobe wct2xxp
```

Schritt 4: Überprüfen Sie mit dahdi_test auf fehlende Interrupts Sie können die Anzahl der Interrupt-Verluste mit dem Dienstprogramm dahdi_test überprüfen, das mit den DAHDI-Karten kompiliert wurde. Eine Zahl unter 99,987% deutet auf mögliche Probleme hin. Sie finden dahdi_test in

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Schritt 5: Verwendung des Dienstprogramms dahdi_cfg Dies ist die korrekte Ausgabe für dahdi_cfg für einen fraktionierten E1-Span (15 Ports) und zwei FXO-Ports.

```
#./dahdi_cfg –vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Schritt 6: Konfiguration von DAHDI in der Datei /etc/asterisk/chan_dahdi.conf Beispiel #1 (2xT1)

```
callerid=”John Doe”<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Beispiel #2 (2xE1)

```
callerid=”Flavio Eduardo” <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Beispiel #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Verwenden Sie signaling=bri_cpe_ptmp für Punkt-zu-Mehrpunkt-BRI. Derzeit wird BRI Punkt-zu-Mehrpunkt im NT-Modus nicht unterstützt.

#### Laden der Kernel-Treiber

Nach der Konfiguration der Treiber können Sie den Server einfach neu starten. Wenn Sie DAHDI mit make config installiert haben, müssen Sie nichts weiter tun. Der Kernel-Treiber wird automatisch geladen und konfiguriert. Manchmal ist es jedoch nützlich, die Treiber manuell zu laden und zu entladen. Beispiel:

```
modprobe wct11xp
dahdi_cfg –vvvvv
```

Der erste Befehl lädt den Treiber und der zweite, dahdi_cfg, wendet die Konfiguration auf den Kernel-Treiber an.

### Fehlerbehebung

Manchmal funktionieren Dinge nicht beim ersten Mal. Lassen Sie uns einige Ressourcen zur Fehlerbehebung bei DAHDI überprüfen. Schritt 1: Überprüfen Sie, ob die Karte vom Betriebssystem erkannt wird. Sangoma/Digium-Karten werden normalerweise als ISDN-Modem erkannt.

```
lspci –v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Schritt 2: Überprüfen Sie mit folgendem Befehl, ob der Kernel-Treiber korrekt geladen wird:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Schritt 3: Überprüfen Sie den Status der Alarme, die sich auf die physische Schicht der Verbindung beziehen. Um die physische Schicht der E1-Verbindung zu überprüfen, können Sie den folgenden Asterisk CLI-Befehl verwenden.

```
dahdi show status
```

Die Alarme zeigen Probleme mit dem Port an: Roter Alarm: Kann die Synchronisation mit der entfernten Vermittlungsstelle nicht aufrechterhalten. Dies ist normalerweise ein physisches Problem, wie z. B. eine Fehlanpassung des Leitungscodes oder des Framings. Gelber Alarm: Signalisiert, dass sich die entfernte Vermittlungsstelle im roten Alarm befindet. Dies zeigt an, dass die entfernte Vermittlungsstelle Ihre Übertragungen nicht empfängt. Blauer Alarm: Empfängt alle unframed 1s auf allen Zeitschlitzen; dahdi_tool erkennt derzeit keinen blauen Alarm. Loopback: Der Port befindet sich entweder im lokalen oder entfernten Loopback

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Schritt 4: Um Probleme mit DAHDI auf dem Asterisk-Server zu erkennen, überprüfen Sie zuerst, ob die Kanäle erkannt werden, indem Sie verwenden:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Schritt 5: Überprüfen Sie den Status der ISDN-Schicht 3, auch bekannt als q.931. Sie können überprüfen, ob die ISDN-Schicht 3 aktiv ist, indem Sie `pri show spans` (um alle Spans aufzulisten) oder `pri show span <n>` für einen bestimmten Span verwenden:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Verwenden Sie `pri show spans` (Plural), um den Status aller konfigurierten PRI-Spans auf einmal aufzulisten.

Überprüfen Sie einen bestimmten Kanal. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1*CLI>
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: Wenn Sie nach allem immer noch Probleme haben, starten Sie das Debugging des PRI-Spans. Dieser Befehl ermöglicht ein detailliertes Debugging von ISDN-Anrufen. Es ist ein wichtiger Befehl, wenn Sie glauben, dass etwas nicht korrekt ist. Sie können falsch gewählte Ziffern und andere Probleme erkennen. Nachfolgend präsentieren wir das Beispiel einer Debugging-Ausgabe für einen erfolgreichen Anruf. Beziehen Sie sich auf dieses Beispiel, wenn Sie einen erfolglosen Anruf mit einem fehlerfreien vergleichen müssen. Ein Tipp ist die Verwendung von core set verbose=0, um nur die ISDN q.931-Meldungen zu erhalten.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]fice*CLI>
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Konfigurationsoptionen in chan_dahdi.conf

In der Datei chan_dahdi.conf sind mehrere Optionen verfügbar. Eine Beschreibung aller Optionen wäre langweilig und kontraproduktiv. Hier werden wir die wichtigsten Optionsgruppen detailliert beschreiben, um ein besseres Verständnis zu ermöglichen.

#### Allgemeine Optionen (kanalunabhängig)

context: Definiert den eingehenden Kontext.

```
context=default
```

channel: Definiert den Kanal oder Kanalbereich. Jede Kanaldefinition erbt Optionen, die vor der Deklaration definiert wurden. Kanäle können einzeln oder in derselben Zeile mit Kommatrennung identifiziert werden. Bereiche können mit „-“ definiert werden.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Ermöglicht es, Kanäle als Gruppe zu behandeln. Wenn Sie eine Gruppennummer anstelle einer Kanalnummer wählen, wird der erste verfügbare Kanal verwendet. Wenn es sich bei den Kanälen um Telefone handelt, klingeln bei einem Anruf einer Gruppe alle Telefone gleichzeitig. Mit Kommas können Sie mehr als eine Gruppe für denselben Kanal angeben.

```
group=1
group=3,5
```

language: Schaltet die Internationalisierung ein und konfiguriert eine Sprache. Diese Funktion konfiguriert Systemmeldungen für eine bestimmte Sprache. Englisch ist die einzige Sprache mit vollständigen Prompts, die aus der Standardinstallation verfügbar sind. musiconhold: Wählen Sie die Music-on-Hold-Klasse aus.

#### ISDN-Optionen

switchtype: Ist abhängig von der verwendeten PBX oder Vermittlungsstelle. In Europa und Lateinamerika ist EuroISDN üblich.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Erforderlich für einige Vermittlungsstellen, die eine Dialplan-Spezifikation benötigen. Diese Option wird von vielen Vermittlungsstellen ignoriert. Die gültigen Optionen sind private, national, international und unknown.

```
pridialplan = unknown
```

prilocaldialplan: Notwendig für einige Vermittlungsstellen, normalerweise unknown.

```
prilocaldialplan = unknown
```

overlapdial: Overlap-Dialing wird verwendet, wenn Sie Ziffern übergeben, nachdem die Verbindung hergestellt wurde. Sie können den Block-Modus (overlapdial=no) oder den Ziffern-Modus (overlapdial=yes) verwenden. Der Block-Modus wird oft von Betreibern verwendet. signaling: Konfiguriert den Signalisierungstyp für die nachfolgenden Kanäle. Diese Parameter sollten denen in der Datei chan_dahdi.conf entsprechen. Korrekte Entscheidungen basieren auf dem verfügbaren Kanal. Für ISDN könnten Sie fünf Optionen wählen:

- pri_cpe: Wird verwendet, wenn das Gerät ein CPE ist, manchmal als Client, Benutzer oder Slave bezeichnet. Dies ist die einfachste und am häufigsten verwendete Form der Signalisierung. Manchmal, wenn Sie versuchen, eine Verbindung zu einer privaten PBX herzustellen, wurde die PBX ebenfalls als CPE konfiguriert. Verwenden Sie in diesem Fall pri_net-Signalisierung in Asterisk.
- pri_net: Wird verwendet, wenn Asterisk mit einer privaten PBX verbunden ist, die als CPE konfiguriert ist. Die Signalisierung wird oft als Host, Master oder Netzwerk bezeichnet.
- bri_cpe: Wird verwendet, wenn Asterisk als CPE mit einem ISDN BRI-Trunk verbunden ist
- bri_net: Wird verwendet, wenn Asterisk mit einem ISDN-Telefon oder einer PBX verbunden ist, die als Terminal (TE) konfiguriert ist.
- bri_cpe_ptmp: Dasselbe wie bri_cpe, aber in einer Punkt-zu-Mehrpunkt-Architektur.

#### CallerID-Optionen

Viele Caller-ID-Optionen sind verfügbar. Einige können deaktiviert werden, obwohl die meisten standardmäßig aktiviert sind. usecallerid: Aktiviert oder deaktiviert die Caller-ID-Übertragung für die nachfolgenden Kanäle (Yes/No). Hinweis: Wenn Ihr System zwei Klingelzeichen erfordert, bevor es antwortet, versuchen Sie, diese Funktion zu deaktivieren, damit es sofort antwortet. hidecallerid: Blendet die Caller-ID aus (Yes/No). calleridcallwaiting: Aktiviert den Empfang der Caller-ID während einer Anklopfanzeige (Yes/No). callerid: Konfiguriert eine Caller-ID-Zeichenfolge für einen bestimmten Kanal. Der Anrufer kann in Trunk-Schnittstellen mit „asreceived“ konfiguriert werden, um die Caller-ID weiterzuleiten.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Hinweis: Die meisten Telefongesellschaften schreiben vor, dass Sie Ihre korrekte Caller-ID konfigurieren. Wenn Sie nicht die richtige Caller-ID übermitteln, sollten Sie nicht in der Lage sein, über die Telefongesellschaft nach außen zu wählen. Andererseits können Sie Anrufe auch ohne Konfiguration der Caller-ID empfangen.

#### Audioqualitätsoptionen

Diese Optionen passen bestimmte Asterisk-Parameter an, die die Audioqualität in DAHDI-Kanälen beeinflussen. echocancel: Deaktiviert oder aktiviert die Echokompensation. Sie sollten diese Funktion aktiviert lassen. Sie akzeptiert „yes“ oder die Anzahl der Taps. Erklärung: Wie funktioniert Echokompensation? Die meisten Echokompensationsalgorithmen arbeiten, indem sie mehrere Kopien eines empfangenen Signals erzeugen, wobei jede um ein kleines Intervall verzögert wird. Dieser kleine Fluss wird als „Tap“ bezeichnet. Die Anzahl der Taps bestimmt die Echoverzögerung, die kompensiert werden kann. Diese Kopien werden verzögert, angepasst und vom ursprünglichen Signal subtrahiert. Der Trick besteht darin, das verzögerte Signal genau auf das Maß anzupassen, das erforderlich ist, um das Echo zu entfernen. echocancelwhenbridged: Aktiviert oder deaktiviert den Echokompensator während eines reinen TDM-Anrufs. Dies ist normalerweise nicht erforderlich. rxgain: Passt die Audio-Empfangsverstärkung an, um die Empfangslautstärke zu erhöhen oder zu verringern (-100% bis 100%). txgain: Passt die Audio-Übertragungsverstärkung an, um die Übertragungslautstärke zu erhöhen oder zu verringern (-100% bis 100%). Beispiel:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Abrechnungsoptionen

Diese Optionen ändern die Art und Weise, wie Anrufinformationen in der Datenbank für Anrufdetails (CDR) aufgezeichnet werden. amaflags: Beeinflusst die Kategorisierung von CDR. Sie akzeptiert diese Werte:

- billing
- documentation
- omit
- default

accountcode: Es konfiguriert einen Kontocode für einen bestimmten Kanal. Er kann jeden alphanumerischen Wert enthalten, normalerweise die Abteilung oder den Benutzernamen.

```
accountcode=finance
amaflags=billing
```

### MFC/R2-Konfiguration

MFC/R2 wird in mehreren Ländern in Lateinamerika, China und Afrika sowie in einigen europäischen Ländern verwendet. ISDN ist überlegen und wird bevorzugt, falls in Ihrer Region verfügbar.

#### Das Problem verstehen

Die Karte, die für die MFC/R2-Signalisierung verwendet wird, ist dieselbe, die für die ISDN-Signalisierung verwendet wird. Es ist möglich, MFC/R2 auf DAHDI-Kanälen unter Verwendung der Bibliothek namens libopenR2 (www.libopenr2.com) zu verwenden. Diese Bibliothek war vor Version 1.6.2 nicht Teil von Asterisk.

##### Das MFC/R2-Protokoll verstehen

Das MFC/R2-Protokoll kombiniert In-Band- und Out-of-Band-Signalisierung. Die Adresssignalisierung wird In-Band unter Verwendung einer Reihe von Tönen weitergeleitet, während Kanalinformationen über Zeitschlitz 16 als Out-of-Band-Signalisierung übertragen werden.

**Leitungssignalisierung (ITU-T Q.421).** In Zeitschlitz 16 verwendet jeder Sprachkanal vier ABCD-Bits, um seine Zustände und die Anrufsteuerung zu signalisieren. Die Bits C und D werden selten verwendet. In einigen Ländern können sie für die Gebührenerfassung (Impulszählung für die Abrechnung) verwendet werden. In einem normalen Gespräch arbeiten beide Seiten: die Anrufer- und die Angerufene Seite. Die Signalisierung von der Anruferseite wird als Vorwärtssignalisierung bezeichnet, während die Angerufene Seite Rückwärtssignalisierung verwendet. Wir bezeichnen Af und Bf für die Vorwärtssignalisierung und Ab und Bb für die Rückwärtssignalisierung.

| Zustand | ABCD vorwärts | ABCD rückwärts |
| --- | --- | --- |
| Leer/Freigegeben | 1001 | 1001 |
| Belegt | 0001 | 1001 |
| Belegungsbestätigung | 0001 | 1101 |
| Beantwortet | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (vor Clear-Back) | 1001 | 0101 |
| ClearFwd (Verbindungsbestätigung) | 1001 | 1001 |
| Blockiert | 1001 | 1101 |

MFC/R2 wurde von der ITU definiert. Leider haben mehrere Länder den Standard an ihre eigenen Bedürfnisse angepasst. Infolgedessen entstanden Abweichungen in den Standards zwischen den Ländern.

**Inter-Register-Signale (ITU-T Q.441).** Die MFC/R2-Signalisierung verwendet eine Kombination aus zwei Tönen. Die Tabellen unten zeigen den ITU-Standard.

Signalgruppe I (vorwärts):

| Beschreibung | Vorwärtssignal |
| --- | --- |
| Ziffer 1 | I-1 |
| Ziffer 2 | I-2 |
| Ziffer 3 | I-3 |
| Ziffer 4 | I-4 |
| Ziffer 5 | I-5 |
| Ziffer 6 | I-6 |
| Ziffer 7 | I-7 |
| Ziffer 8 | I-8 |
| Ziffer 9 | I-9 |
| Ziffer 0 | I-10 |
| Ländercode-Indikator, ausgehender Halb-Echosperrer erforderlich | I-11 |
| Ländercode-Indikator, kein Echosperrer erforderlich | I-12 |
| Testanruf-Indikator | I-13 |
| Ländercode-Indikator, ausgehender Halb-Echosperrer eingefügt | I-14 |
| Nicht verwendet | I-15 |

Signalgruppe II (vorwärts):

| Beschreibung | Vorwärtssignal |
| --- | --- |
| Teilnehmer ohne Priorität | II-1 |
| Teilnehmer mit Priorität | II-2 |
| Wartungsausrüstung | II-3 |
| Reserve | II-4 |
| Operator | II-5 |
| Datenübertragung | II-6 |
| Teilnehmer oder Operator ohne Vorwärtsübertragungseinrichtung | II-7 |
| Datenübertragung | II-8 |
| Teilnehmer mit Priorität | II-9 |
| Operator mit Vorwärtsübertragungseinrichtung | II-10 |
| Reserve | II-11 |
| Reserve | II-12 |
| Reserve | II-13 |
| Reserve | II-14 |
| Reserve | II-15 |

Signalgruppe A (rückwärts):

| Beschreibung | Rückwärtssignal |
| --- | --- |
| Sende nächste Ziffer (n+1) | A-1 |
| Sende vorletzte Ziffer (n-1) | A-2 |
| Adresse vollständig, Umschaltung auf Empfang von Gruppe B-Signalen | A-3 |
| Überlastung im nationalen Netzwerk | A-4 |
| Sende Kategorie des anrufenden Teilnehmers | A-5 |
| Adresse vollständig, Gebühr, Sprachbedingungen einrichten | A-6 |
| Sende vorvorletzte Ziffer (n-2) | A-7 |
| Sende vorvorvorletzte Ziffer (n-3) | A-8 |
| Reserve | A-9 |
| Reserve | A-10 |
| Sende Ländercode-Indikator | A-11 |
| Sende Sprach- oder Diskriminierungsziffer | A-12 |
| Sende Art des Schaltkreises | A-13 |
| Anforderung von Informationen zur Verwendung des Echosperrers | A-14 |
| Überlastung in einer internationalen Vermittlungsstelle oder an deren Ausgang | A-15 |

Signalgruppe B (rückwärts):

| Beschreibung | Rückwärtssignal |
| --- | --- |
| Reserve | B-1 |
| Sende speziellen Informationston | B-2 |
| Teilnehmerleitung besetzt | B-3 |
| Überlastung (nach Umschaltung Gruppe A auf B) | B-4 |
| Nicht zugewiesene Nummer | B-5 |
| Teilnehmerleitung frei, Gebühr | B-6 |
| Teilnehmerleitung frei, keine Gebühr | B-7 |
| Teilnehmerleitung außer Betrieb | B-8 |
| Reserve | B-9 |
| Reserve | B-10 |
| Reserve | B-11 |
| Reserve | B-12 |
| Reserve | B-13 |
| Reserve | B-14 |
| Reserve | B-15 |

#### MFC/R2-Sequenz

Die folgende Sequenz veranschaulicht einen Anruf, der von einer Asterisk-Nebenstelle zu einem Endgerät im PSTN ausgeht. Das PSTN bricht den Anruf ab und beendet die Kommunikation.

![Ein vollständiger MFC/R2-Anruffluss zwischen Asterisk und der Telefongesellschaft: Leitungssignalisierung (Leer, Belegt, Belegungsbestätigung, Antwort, Clearback, Clear Forward) wird in Zeitschlitz 16 ausgetauscht, die gewählten Ziffern und Rückwärts-„Sende nächste Ziffer“-Signale (Gruppen I/A/B) reisen In-Band, und die hörbaren Töne erreichen den Teilnehmer.](../images/10-legacy-fig11.png)

### Verwendung des Treibers libopenr2

Das von Moises Silva initiierte Projekt wurde vom Unicall-Kanaltreiber inspiriert, der von Steve Underwood geschrieben wurde. Die OpenR2-Bibliothek ist derzeit die stabilste Softwarelösung für Asterisk. Mit dieser Lösung können wir jede digitale Karte verwenden, die mit DAHDI kompatibel ist. Zuvor waren nur proprietäre Lösungen für MFC/R2 verfügbar; eine der besten, die ich verwendet habe, ist die von Khomp, www.khomp.com.br. In Asterisk 22 ist die MFC/R2-Unterstützung über libopenR2 integriert, wenn die Bibliothek zum Zeitpunkt der Kompilierung vorhanden ist — es ist kein externer Patch erforderlich. Die folgenden Schritte zeigen die historische manuelle Installation als Referenz; auf modernen Systemen installieren Sie `libopenr2-dev` über den Paketmanager Ihrer Distribution, bevor Sie `./configure` ausführen, und aktivieren dann `chan_dahdi` in `make menuselect`.

Die folgenden Schritte bauen openr2 und Asterisk aus ihren aktuellen Git-Repositories. Sie werden als Referenz für Standorte beibehalten, die aus dem Quellcode bauen; auf einer modernen Distribution können Sie sie normalerweise vollständig überspringen, indem Sie das Paket `libopenr2-dev` und einen paketierten Asterisk 22-Build installieren, da `chan_dahdi` die R2-Unterstützung direkt gegen libopenr2 ohne externen Patch kompiliert.

Schritt 1: Installieren Sie die benötigten Build-Tools.

```
apt-get install git
```

Schritt 2: Klonen Sie die openr2-Bibliothek und den Asterisk-Quellcode. Auf Asterisk 22 ist kein spezieller gepatchter Baum erforderlich — ein Standard-Checkout baut die R2-Unterstützung, solange libopenr2 vorhanden ist.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Schritt 3: Kompilieren und installieren Bitte sichern Sie Ihren Server, bevor Sie fortfahren.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Hinweis: Führen Sie nicht „make samples“ aus, um ein Überschreiben Ihrer Konfigurationsdateien zu vermeiden.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Nehmen wir an, Sie haben eine Karte mit einer E1-Schnittstelle.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Schritt 5: Führen Sie den Befehl dahdi_cfg aus, um die Änderungen auf den Treiber anzuwenden:

```
dahdi_cfg –vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Schritt 5: Ändern Sie die Datei chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Schritt 6: Ändern Sie den Dialplan in der Datei extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Hinweis: Einige Telefongesellschaften akzeptieren keine Anrufe ohne Caller-ID. Bitte setzen Sie die Caller-ID auf eine der DID-Nummern, die vom Betreiber zugewiesen wurden. In einigen Ländern ist dieser Schritt nicht erforderlich. Schritt 7: Testen Sie die Lösung: Rufen Sie nun mit einer Nebenstelle im Kontext from-internal eine beliebige Nummer an und beobachten Sie die Konsole. Überprüfen Sie, ob Fehler auftreten. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging von OpenR2

Um Fehler bei den Anrufen zu erkennen, können Sie das Debugging aktivieren. Befolgen Sie dazu die folgenden Schritte. Schritt 1: Bearbeiten Sie die Datei chan_dahdi.conf und fügen Sie die folgenden drei Zeilen zur Konfiguration hinzu:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

Schritt 2: Starten Sie den Asterisk-Server neu Schritt 3: Testen Sie den Anruf und überprüfen Sie die Anrufdateien unter /var/log/asterisk/mfcr2/span1 Unten ist ein Trace für einen normalen Anruf. Vergleichen Sie ihn mit dem, was Sie bei Ihrem Anruf erhalten.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2-Konfiguration

Die Optionen sind in der Datei chan_dahdi.conf dokumentiert. Einige der wichtigsten Optionen werden hier detailliert beschrieben. Obligatorische Parameter: mfcr2_variant, mfcr2_max_ani und mfcr2_max_dnis. mfcr2_variant: Ländervariante.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Maximale Anzahl von ANI-Ziffern, die angefordert werden sollen mfcr2_max_dnis: Maximale Anzahl von DNIS-Ziffern, die angefordert werden sollen mfcr2_get_ani_first: Ob ANI vor DNIS abgerufen werden soll oder nicht (von einigen Telefongesellschaften erforderlich) mfcr2_category: Anruferkategorie. Sie können die Variable MFCR2_CATEGORY vor dem Starten des Anrufs setzen mfcr2_logdir: Verzeichnis zum Protokollieren der Anrufdateien. (/var/log/asterisk/mfcr2/directory) mfcr2_call_files: Ob die Anrufe protokolliert werden sollen oder nicht

- mfcr2_logging: Protokollierungswerte
- cas – ABCD-Bits für tx und rx
- mf – Mehrfrequenztöne
- stack – ausführliche Ausgabe des Kanal- und Kontext-Stacks
- all – alle Aktivitäten
- nothing – nichts protokollieren

mfcr2_mfback_timeout: Dieser Wert verdient Erwähnung. Wenn Sie ein Mobiltelefon anrufen oder einen Anruf tätigen, dessen Abschluss lange dauert, kann dieser Parameter ein Timeout verursachen, daher wird er oft zur Feinabstimmung geändert. Wenn einige Ihrer Anrufe nicht abgeschlossen werden, ist dies der Parameter, den Sie zuerst ändern sollten. mfcr2_metering_pulse_timeout: Impulse werden von einigen R2-Varianten verwendet, um Kosten anzuzeigen mfcr2_allow_collect_calls: In Brasilien wird der Ton II-8 verwendet, um ein R-Gespräch anzuzeigen; dieser Parameter ermöglicht es Ihnen, R-Gespräche zu blockieren. mfcr2_double_answer: Wird ebenfalls verwendet, um R-Gespräche zu vermeiden, wenn eine doppelte Antwort erforderlich ist. Mit double_answer=yes blockieren Sie tatsächlich die R-Gespräche. mfcr2_immediate_accept: Ermöglicht es Ihnen, die Verwendung von Gruppe B/II-Signalen zu überspringen und direkt zum akzeptierten Zustand überzugehen. mfcr2_forced_release: Ermöglicht es Ihnen, die Freigabe des Anrufs zu beschleunigen; funktioniert für die brasilianische Variante.

#### ANI und DNIS

Automatic Number Identification (ANI) ist die Nummer des Anrufers. Dialed Number Identification Service (DNIS) ist die angerufene Nummer oder, mit anderen Worten, die gewählte Nummer. Wenn ein Anruf eingeht, werden normalerweise die letzten vier Nummern an die PBX in einem Prozess weitergegeben, der als Direct Inward Dial (DID) bezeichnet wird. Die ANI-Nummer ist eigentlich die Caller-ID. ANI enthält die Nebenstelle des Anrufers beim Wählen, während DNIS das Anrufziel enthält. Es ist wichtig, dass diese Parameter korrekt konfiguriert sind. Einige Vermittlungsstellen senden nur die letzten vier Ziffern, während andere die vollständige Nummer senden.

### DAHDI-Kanalformat

DAHDI-Kanäle verwenden das folgende Format im Dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier>- Physical channel numeric identifier
[g] – Group identifier
[c] – Answer confirmation. A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

Beispiele:

```
DAHDI/2
- channel 2
DAHDI/g1  - First available channel in group 1
[g] – Group identifier
[c] – Answer confirmation; A number is not considered until the callee press
“#”
[r] – customized ringing
[cadence] Integer from 1 to 4
```

## Das IAX2-Protokoll

In diesem Kapitel lernen wir das Inter-Asterisk eXchange (IAX)-Protokoll kennen, einschließlich seiner Stärken und Schwächen. Details wie der Trunk-Modus und die Verbindung zweier Asterisk-Server werden ebenfalls behandelt. Alle Referenzen in diesem Dokument entsprechen IAX Version 2. Das IAX-Protokoll bietet Medientransport und Signalisierung für Sprache und Video. IAX ist sehr innovativ; es spart Bandbreite im Trunk-Modus und ist viel einfacher als SIP, wenn Sie NAT durchqueren müssen. Die primäre Verwendung für IAX heutzutage ist die Verbindung von Asterisk-Servern. IAX wurde primär für Sprache entwickelt, kann aber auch Video und andere Multimedia-Streams aufnehmen. IAX wurde von anderen VoIP-Protokollen wie SIP und MGCP inspiriert. Anstatt zwei separate Protokolle für Signalisierung und Medien zu verwenden, hat IAX sie zu einem einzigartigen Protokoll vereint. IAX verwendet kein RTP für den Medientransport; stattdessen bettet es die Medien in dieselbe UDP-Verbindung ein.

**Status in Asterisk 22.** `chan_iax2` ist in Asterisk 22 LTS weiterhin enthalten und vollständig unterstützt, daher bleibt alles in diesem Abschnitt gültig. IAX2 ist jedoch ein Legacy-Protokoll, das relativ wenig neue Implementierungen sieht: Die Industrie hat sich weitgehend auf SIP (via `chan_pjsip` in Asterisk 22) sowohl für Provider-Trunking als auch für Server-Interkonnektion geeinigt. Der Hauptvorteil von IAX2, der verbleibt, ist sein Single-Port-Design — alle Signalisierung und Medien fließen über einen einzigen UDP-Port (standardmäßig 4569), was die Firewall- und NAT-Konfiguration im Vergleich zu SIP plus seinen separaten RTP-Streams vereinfacht. Für einen neuen Asterisk-zu-Asterisk-Trunk, bei dem NAT kein Problem darstellt, ist ein PJSIP-Trunk der empfohlene moderne Ansatz; IAX2 wird hier behandelt, weil es eine gültige Wahl bleibt, insbesondere wenn nur ein UDP-Port durch eine Firewall geöffnet werden kann.

### Lernziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Stärken und Schwächen des IAX-Protokolls zu identifizieren
- Nutzungsszenarien für das IAX-Protokoll zu beschreiben
- Die Vorteile des IAX-Trunk-Modus zu beschreiben
- iax.conf für Telefone zu konfigurieren
- iax.conf für die Verbindung zu einem VoIP-Anbieter zu konfigurieren
- iax.conf für die Asterisk-Interkonnektion zu konfigurieren
- IAX-Authentifizierung zu verstehen

### IAX-Design

Die Hauptziele für das IAX-Design sind:

- Die für Medientransport und Signalisierung erforderliche Bandbreite zu reduzieren
- NAT-Transparenz bereitzustellen
- Dialplan-Informationen übertragen zu können
- Die effiziente Nutzung von Paging und Intercom zu unterstützen

IAX ist ein Peer-to-Peer-Signalisierungs- und Medienprotokoll, das SIP ähnelt, ohne RTP zu verwenden. Der grundlegende Ansatz besteht darin, die Multimedia-Streams über eine einzige UDP-Verbindung zwischen zwei Hosts zu multiplexen. Der größte Vorteil dieses Ansatzes ist seine Einfachheit bei der Durchquerung von Verbindungen über NAT, die regelmäßig in xDSL-Modems zu finden sind. IAX verwendet einen einzigen Port, standardmäßig UDP 4569, und verwendet dann eine Anrufnummer mit 15 Bits, um alle Streams zu multiplexen. Das IAX-Protokoll verwendet Registrierungs- und Authentifizierungsprozesse, die dem SIP-Protokoll ähneln. Eine Beschreibung des Protokolls finden Sie unter http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![Das IAX-Protokoll multiplext viele Anrufe zwischen zwei Endpunkten über einen einzigen UDP-Port (standardmäßig 4569), wobei eine 15-Bit-Anrufnummer verwendet wird, um die Streams getrennt zu halten — was die NAT-Durchquerung einfach macht.](../images/10-legacy-fig12.png)

### Bandbreitennutzung

Die in VoIP-Netzwerken verwendete Bandbreite wird von mehreren Faktoren beeinflusst; Codecs und Protokoll-Header sind die wichtigsten. Das IAX-Protokoll hat eine überraschende Funktion namens Trunk-Modus, bei der es mehrere Anrufe unter Verwendung eines einzigen Headers multiplext. Wenn Sie mit dem Asterisk-Bandbreitenrechner spielen, werden Sie sehen, wie IAX-Trunks Ihnen bei mehreren Anrufen bis zu 80% des Verkehrs sparen können.

![Vergleich von IAX- und SIP-Overhead: Zwei SIP/RTP-Anrufe benötigen zwei Pakete (40 Bytes Payload, getragen unter 156 Bytes Overhead), während der IAX2-Trunk-Modus beide Anrufe in einem einzigen Paket trägt (40 Bytes Payload unter nur 66 Bytes Overhead), indem ein IP/UDP-Header über viele Mini-Frames geteilt wird.](../images/10-legacy-fig13.png)

### Kanalbenennung

Es ist wichtig, die Konventionen zur Kanalbenennung zu verstehen, da Sie diese Namen verwenden werden, wenn Sie einen Kanal im Dialplan angeben. Das Format eines IAX-Kanalnamens, der für ausgehende Kanäle verwendet wird, ist:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

<user> UserID auf dem entfernten Peer oder Name des in iax.conf konfigurierten Clients <secret> Das Passwort. Alternativ kann es der Dateiname für einen RSA-Schlüssel ohne die nachgestellte Erweiterung (.key oder .pub) sein und in eckigen Klammern eingeschlossen <peer> Name des Servers, zu dem eine Verbindung hergestellt werden soll <portno> Portnummer für die Verbindung <exten> Nebenstelle im entfernten Asterisk-Server <context> Kontext im entfernten Asterisk-Server <options> Die einzige verfügbare Option ist ‚a‘, was ‚request autoanswer‘ bedeutet

#### Beispiel für ausgehende Kanäle:

Ausgehende Kanäle werden in der Asterisk-Konsole angezeigt. IAX2/8590:secret@myserver/8590@default Ruft die 8590-Nebenstelle in myserver an. Es verwendet 8590:secret als Name/Passwort-Paar

IAX2/iaxphone Ruft "iaxphone" an IAX2/judy:[judyrsa]@somewhere.com Ruft somewhere.com unter Verwendung von judy als Benutzername und einem RSA-Schlüssel für die Authentifizierung an

#### Das Format eines eingehenden IAX-Kanals ist:

Eingehende Kanäle werden in der Asterisk-Konsole angezeigt.

```
IAX2/[<username>@]<host>]-<callno>
```

<username> Benutzername, falls bekannt <host> Host, der sich verbindet <callno> Lokale Anrufnummer Beispiel für eingehenden Kanal: IAX2[flavio@8.8.30.34]/10 Anrufnummer 10 von IP-Adresse 8.8.30.34 unter Verwendung von flavio als Benutzer. IAX2[8.8.30.50]/11 Anrufnummer 11 von IP-Adresse 8.8.30.50.

### Verwendung von IAX

Sie können IAX auf verschiedene Weise verwenden. In diesem Abschnitt zeigen wir Ihnen, wie Sie IAX für verschiedene Szenarien konfigurieren, einschließlich:

- Anschließen eines Softphones über IAX
- Anschließen von IAX an einen VoIP-Anbieter über IAX
- Anschließen zweier Server über IAX
- Anschließen zweier Server über IAX im Trunk-Modus
- Debugging einer IAX-Verbindung
- Verwendung von RSA-Schlüsselpaaren für die Authentifizierung

#### Anschließen eines Softphones über IAX

Asterisk unterstützt IP-Telefone auf IAX-Basis wie das ATCOM und das alte ATA von Digium (genannt IAXy) sowie Softphones, die das IAX2-Protokoll weiterhin implementieren. Der Prozess für Softphones, ATAs und Hardphones ist ähnlich. Um ein IAX-Gerät zu konfigurieren, müssen Sie die Datei iax.conf in /etc/asterisk bearbeiten

```
directory.
```

Wir verwenden ein IAX2-fähiges Softphone als Beispiel. Schritt 1: Erstellen Sie ein Backup der ursprünglichen iax.conf-Datei mit:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

Schritt 2: Beginnen Sie mit der Bearbeitung einer neuen iax.conf-Datei:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Sehr wichtiger Parameter, er ändert die verfügbaren Codecs

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Ich habe versucht, die Standardzeilen (nicht kommentiert) der Beispieldatei beizubehalten. Die folgenden Parameter wurden geändert:

```
bandwidth=high
```

Diese Zeile beeinflusst die Codec-Auswahl. Die Verwendung der Einstellung high ermöglicht die Auswahl eines Codecs mit hoher Bandbreite und hoher Qualität wie g.711, definiert durch das Schlüsselwort ulaw. Wenn Sie den Standardparameter beibehalten, können Sie ulaw nicht auswählen. In diesem Fall gibt Ihnen Asterisk für die unten stehende Konfiguration die Meldung „no codec available“.

```
disallow=all
allow=ulaw
```

In den oben beschriebenen Befehlen haben wir alle Codecs deaktiviert und nur ulaw aktiviert. In LANs bevorzugen die meisten Leute die Verwendung von ulaw, da es nicht prozessorintensiv ist und CPU-Zyklen spart. Selbst bei Verwendung von mehr Bandbreite ist dieser Codec vorzuziehen, da Sie in LANs normalerweise ein 100-Megabit-Ethernet oder sogar ein Gigabit haben. Ein Sprachanruf mit ulaw verbraucht fast 100 Kilobit pro Sekunde Bandbreite aus Ihrem Netzwerk, was eine sehr geringe Nutzung für die heutigen Hochgeschwindigkeits-LANs darstellt. In WAN- oder Internet-Netzwerken deaktivieren Sie normalerweise ulaw und tauschen einige verfügbare CPU-Zyklen gegen Sprachkompression für eine bessere Bandbreitennutzung. Die Codecs gsm, g729 und ilbc bieten ebenfalls einen guten Kompressionsfaktor.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

In den obigen Befehlen haben wir einen Freund namens [2003] definiert. Der Kontext ist default (in den ersten Labs verwenden wir immer den default-Kontext, um Verwirrung zu vermeiden; dieser Kontext wird in Kapitel 9 vollständig erklärt). Die Zeile „host=dynamic“ ermöglicht eine dynamische Registrierung der IP-Adresse des Telefons. Schritt 3: Laden Sie ein IAX2-fähiges Softphone herunter und installieren Sie es. Sie können für das Lab jedes Softphone wählen, das das IAX2-Protokoll weiterhin unterstützt. Schritt 4: Konfigurieren Sie ein IAX-Konto im Client (typischerweise *Add account* → IAX). Beachten Sie, dass das SipPulse Softphone nur SIP unterstützt und sich nicht über IAX2 registrieren kann, daher benötigen Sie für IAX-Tests einen Client, der das Protokoll weiterhin unterstützt.

Schritt 5: Konfigurieren Sie die Datei extensions.conf, um Ihr IAX-Gerät zu testen.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Jetzt können Sie zwischen den in Kapitel 3 erstellten SIP-Telefonen und dem im Lab erstellten IAX-Telefon wählen.

#### Anschließen an einen VoIP-Anbieter über IAX

Einige VoIP-Anbieter unterstützen IAX. Sie können leicht einen IAX-Anbieter finden, indem Sie nach „IAX providers“ suchen. Die Verwendung eines IAX-Anbieters ist sehr sinnvoll, da IAX viel Bandbreite sparen kann, NAT leicht durchquert und sich unter Verwendung von RSA-Schlüsselpaaren authentifizieren kann.

![Ein Asterisk eines Kunden, der über einen IAX-Trunk über das Internet mit einem VoIP-Anbieter verbunden ist: Ein einziger Trunk trägt alle Anrufe zum und vom Anbieter.](../images/10-legacy-fig14.png)

Die Anzahl der IAX-fähigen kommerziellen VoIP-Anbieter ist in den letzten Asterisk-Releases stark zurückgegangen; die meisten Anbieter bieten jetzt ausschließlich SIP/PJSIP-Trunks an. Bevor Sie sich für einen IAX-Anbieter entscheiden, bestätigen Sie, dass dieser seine IAX-Infrastruktur aktiv pflegt. Für eine neue Anbieterintegration ist ein PJSIP-Trunk (Kapitel 3) die empfohlene Alternative.

#### Anschließen an einen Anbieter über IAX

Schritt 1: Eröffnen Sie ein Konto bei Ihrem bevorzugten Anbieter. Ihr Anbieter wird Ihnen drei Dinge zur Verfügung stellen.

- Name
- Secret
- IP-Adresse oder Hostname
- Öffentlicher RSA-Schlüssel

Schritt 2: Konfigurieren Sie die Datei iax.conf, um Ihren Asterisk bei Ihrem Anbieter zu registrieren. Fügen Sie die folgenden Zeilen zum Abschnitt [general] der Datei hinzu.

```
[general]
register=>name:secret@hostname/2003
```

In den oben beschriebenen Anweisungen haben Sie sich bei Ihrem Anbieter unter Verwendung Ihres Kontos und Passworts registriert. In dem Moment, in dem Sie einen Anruf erhalten, wird dieser an die Nebenstelle 2003 weitergeleitet.

```
[name]
```

- ; Ihr Kontoname oder Ihre Nummer

```
type=peer
secret=secret
; Your password
host=hostname
```

In den oben beschriebenen Anweisungen haben wir einen Peer erstellt, der dem Anbieter für Wählzwecke entspricht.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Dies ist für die RSA-Authentifizierung erforderlich. Die Verwendung des öffentlichen Schlüssels Ihres Anbieters ermöglicht es Ihnen, sicher zu sein, dass der empfangene Anruf wirklich vom echten Anbieter stammt. Wenn jemand anderes versucht, denselben Pfad zu verwenden, kann er ihn nicht authentifizieren, da er nicht über den entsprechenden privaten Schlüssel verfügt. Schritt 4: Testen Sie die Verbindung. Um die Verbindung zu testen, wählen Sie eine beliebige Nummer. Einige Anbieter bieten einen Echotest an. Um dies zu erreichen, bearbeiten Sie bitte die Datei extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Gehen Sie zur Asterisk CLI und führen Sie ein Reload durch. Um zu überprüfen, ob Asterisk beim Anbieter registriert ist, verwenden Sie den nächsten Befehl.

```
CLI>reload
CLI>iax2 show register
```

Wählen Sie nun einfach *98 auf dem Softphone, das mit dem Asterisk-Server verbunden ist.

#### Anschließen zweier Asterisk-Server über einen IAX-Trunk

Es ist sehr einfach, einen Server mit einem anderen zu verbinden. Sie müssen sie nicht registrieren, da die IP-Adressen bereits bekannt sind. Sie müssen die Peers und Benutzer in der Datei iax.conf erstellen. Alle Nebenstellen am HQ-Standort beginnen mit 20 gefolgt von zwei Ziffern (z. B. 2000). In der Niederlassung beginnen alle Nebenstellen mit 22 gefolgt von zwei Ziffern (z. B. 2200). Wir werden den Trunk verwenden. Sie benötigen eine DAHDI-Zeitquelle, um diese Funktion zu aktivieren. Schritt 1: Bearbeiten Sie die Datei iax.conf auf dem Niederlassungs-Server.

![Verbindung zweier Asterisk-Server mit einem IAX-Trunk: Der HQ-Server (192.168.1.1, Nebenstellen 20xx) und der Niederlassungs-Server (192.168.1.2, Nebenstellen 22xx) erreichen sich über einen einzigen IAX-Trunk — keine Registrierung ist erforderlich, da beide IP-Adressen fest und bekannt sind.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

Schritt 2: Konfigurieren Sie die Datei extensions.conf auf dem Niederlassungs-Server

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

Schritt 3: Konfigurieren Sie die Datei iax.conf auf dem HQ-Server

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Schritt 4: Konfigurieren Sie die Datei extensions.conf auf dem HQ-Server.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Schritt 5: Testen Sie einen Anruf vom Telefon 2000 auf dem HQ-Server zum Telefon 2200 auf dem Niederlassungs-Server.

### IAX-Authentifizierung

Lassen Sie uns nun den IAX-Authentifizierungsprozess aus praktischer Sicht analysieren, um Ihnen bei der Auswahl der besten Methode für jede spezifische Anforderung zu helfen.

#### Eingehende Verbindungen

![Der IAX-Authentifizierungsentscheidungsfluss für einen eingehenden Anruf: Asterisk verzweigt danach, ob ein Benutzername angegeben ist, ob er mit einem Abschnitt übereinstimmt, ob die Quell-IP erlaubt ist und ob das Secret (Klartext, MD5 oder RSA) übereinstimmt — akzeptiert den Anruf mit dem Kontext und den Peer-Optionen dieses Abschnitts oder lehnt ihn ab.](../images/10-legacy-fig16.png)

Wenn Asterisk eine eingehende Verbindung empfängt, können die anfänglichen Informationen einen Benutzernamen (aus dem Feld „username=“) enthalten oder nicht. Die eingehende Verbindung hat auch eine IP-Adresse, die Asterisk ebenfalls zur Authentifizierung verwendet. Wenn ein Benutzer angegeben wird, Asterisk: 1. Durchsucht iax.conf nach einem Eintrag mit type=user (oder type=friend mit einem Abschnittsnamen, der mit dem Benutzernamen übereinstimmt). Wenn es ihn nicht findet, verweigert Asterisk die Verbindung. 2. Wenn der gefundene Eintrag deny/allow-Konfigurationen hat, vergleicht es die IP-Adresse des Anrufers, um zu bestimmen, ob der Anruf akzeptiert werden soll oder nicht, abhängig von den deny/allow-Klauseln. 3. Es überprüft das Passwort (secret) unter Verwendung von Klartext, md5 oder RSA. 4. Es akzeptiert die Verbindung und sendet den Anruf an den Kontext, der in der Zeile „context=“ in der Datei iax.conf angegeben ist. Wenn kein Benutzername angegeben wird, Asterisk: 1. Durchsucht die Datei iax.conf nach einem Eintrag mit type=user (oder type=friend) ohne angegebenes Secret. Es überprüft auch deny/allow-Klauseln. Wenn ein Eintrag gefunden wird, wird die Verbindung akzeptiert und der Abschnittsname als Benutzername verwendet. 2. Durchsucht die Datei iax.conf nach einem Eintrag mit type=user (oder type=friend) mit einem angegebenen Secret oder RSA-Schlüssel. Es überprüft deny/allow-Klauseln. Wenn ein Eintrag gefunden wird, versucht es, den Anrufer unter Verwendung des angegebenen Secrets zu authentifizieren; wenn es übereinstimmt, akzeptiert es die Verbindung. Der Abschnittsname ist der Benutzername. Nehmen wir an, Ihre Datei iax.conf hat die folgenden Einträge:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

Wenn ein Anruf einen angegebenen Benutzernamen hat, wie z. B.:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk wird versuchen, den Anruf nur unter Verwendung des entsprechenden Eintrags in der Datei iax.conf zu authentifizieren. Wenn andere Namen angegeben werden, würde der Anruf abgelehnt. Wenn kein Benutzer angegeben ist, versucht Asterisk, die Verbindung als guest zu authentifizieren. Wenn guest jedoch nicht existiert, versucht es andere Verbindungen mit einem übereinstimmenden Secret. Mit anderen Worten, wenn Sie keinen guest-Abschnitt in Ihrer Datei iax.conf haben, könnte ein böswilliger Benutzer versuchen, ein übereinstimmendes Secret zu erraten, indem er den Benutzernamen nicht angibt. IP-Adress-Beschränkungen (deny/allow) gelten ebenfalls. Ein guter Weg, um Secret-Raten zu vermeiden, ist die Verwendung der RSA-Authentifizierung. Eine weitere Methode besteht darin, die IP-Adressen einzuschränken, die anrufen dürfen.

#### IP-Adressbeschränkungen

permit = <ipaddr>/<netmask> Regeln werden nacheinander interpretiert, und alle werden ausgewertet (dieses Konzept unterscheidet sich von ACLs, die normalerweise in Routern und Firewalls zu finden sind). deny = <ipaddr>/<netmask> Beispiel #1 permit=0.0.0.0/0.0.0.0 deny=192.168.0.0/255.255.255.0 Verweigert jedes Paket aus dem Netzwerk 192.168.0.0/24 Beispiel #2 deny=192.168.0.0/255.255.255.0 permit=0.0.0.0/0.0.0.0 Es erlaubt jedes Paket. Die letzte Anweisung ersetzt die erste.

#### Ausgehende Verbindungen

Ausgehende Verbindungen erhalten Authentifizierungsinformationen unter Verwendung der folgenden Methoden:

- Die IAX2-Kanalbeschreibung, die von der Dial()-Anwendung übergeben wird.
- Ein Eintrag mit type=peer oder type=friend in der Datei iax.conf.
- Eine Kombination aus beiden Methoden.

#### Verbindung zweier Asterisk-Server über RSA-Schlüssel

Es ist möglich, IAX mit starker Authentifizierung unter Verwendung asymmetrischer RSA-Schlüssel zu verwenden. Laut Quellcode (res_krypto.c) verwendet Asterisk RSA-Schlüssel mit einem SHA-1-Algorithmus für Message Digests anstelle des schwächeren MD5. Nachfolgend finden Sie eine Schritt-für-Schritt-Anleitung zum Einrichten zweier Server unter Verwendung von RSA-Schlüsseln.

##### Konfiguration des Servers für die Niederlassung

Schritt 1: Generieren Sie die RSA-Schlüssel auf dem Niederlassungs-Server

```
astgenkey -n
```

Verwenden Sie bei Aufforderung den Schlüsselnamen branch. Wir haben den Parameter –n verwendet, um zu vermeiden, dass jedes Mal ein Passwort eingegeben werden muss, wenn Asterisk neu initialisiert wird. Wenn Sie die Sicherheit verbessern möchten, verwenden Sie nicht –n und starten Sie Asterisk mit asterisk -i Schritt 2: Kopieren Sie die Schlüssel in das Verzeichnis /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Schritt 3: Kopieren Sie den öffentlichen Schlüssel auf den HQ-Server

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Schritt 4: Bearbeiten Sie die Datei iax.conf auf dem Niederlassungs-Server.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

Schritt 8: Konfigurieren Sie die Datei extensions.conf auf dem Niederlassungs-Server

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Konfiguration des Servers für die Zentrale

Schritt 1: Generieren Sie die RSA-Schlüssel auf dem HQ-Server

```
astgenkey -n
```

Verwenden Sie bei Aufforderung den Schlüsselnamen hq. Schritt 2: Kopieren Sie die Schlüssel in das Verzeichnis /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

Schritt 3: Kopieren Sie den öffentlichen Schlüssel auf den BRANCH-Server

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Schritt 4: Konfigurieren Sie die Datei iax.conf auf dem HQ-Server

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Schritt 10: Konfigurieren Sie die Datei extensions.conf auf dem HQ-Server.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Schritt 11: Testen Sie einen Anruf vom Telefon 2000 auf dem HQ-Server zum Telefon 2200 auf dem Niederlassungs-Server.

### Die Konfiguration der Datei iax.conf

Die Datei iax.conf hat mehrere Parameter; jeden Parameter einzeln zu diskutieren wäre langweilig und kontraproduktiv. Alle Parameter finden Sie zusammen mit einer Beschreibung in der Beispieldatei. Im Wiki www.voip-info.org finden Sie detaillierte Informationen zu jedem einzelnen. Hier zeigen wir einige der wichtigsten Parameter für die Konfiguration des allgemeinen Abschnitts, der Peers und der Benutzer.

#### [General]-Abschnitt

Serveradressen bindport = <portnum> Konfiguriert den IAX-UDP-Port. Standard ist 4569. bindaddr = <ipaddr> Verwenden Sie 0.0.0.0, um Asterisk an alle Schnittstellen zu binden, oder geben Sie die IP-Adresse einer bestimmten Schnittstelle an. Codec-Auswahl bandwidth = [low|medium|high] High = alle Codecs Medium = alle Codecs außer ulaw und alaw Low = Codecs mit niedriger Bandbreite allow/disallow = Feinabstimmung der Codec-Auswahl [alaw|ulaw|gsm|g.729| etc.]

### Jitter-Buffer

Jitter ist die Verzögerungsvariation zwischen Paketen. Er ist der wichtigste Faktor, der die Sprachqualität beeinflusst. Ein Jitter-Buffer wird verwendet, um die Verzögerungsvariation zu kompensieren. Er opfert Latenz zugunsten eines geringeren Jitters. Sie können eine Analogie zwischen dem Jitter-Buffer und einem Wassertank ziehen. Beide können Pakete oder Wasser in unregelmäßigen Abständen empfangen, liefern aber letztendlich einen regelmäßigen Fluss.

![Der Jitter-Buffer als Wassertank: Pakete kommen unregelmäßig aus dem Netzwerk an und füllen den Puffer, der sie dann mit einer konstanten Rate freigibt, um einen gleichmäßigen Sprachfluss zu erzeugen. Die Puffergröße (in ms) tauscht ein wenig Latenz gegen geringeren Jitter; das Excess-Buffer-Band lässt Asterisk den Puffer vergrößern oder verkleinern, wenn sich die Netzwerkbedingungen ändern.](../images/10-legacy-fig17.png)

Ein kleiner Jitter (d. h. unter 20 ms) ist normalerweise nicht wahrnehmbar. Ein Jitter über diesem Wert ist jedoch störend. Die Latenz oder Verzögerung sollte unter 150 ms gehalten werden. Das Erstellen eines Jitter-Buffers opfert etwas Verzögerung für einen geringeren Jitter — ein Konzept, das als „Delay-Budget“ bekannt ist. Sie können den Jitter-Buffer mit diesen Parametern beeinflussen:

- Jitterbuffer=<yes/no> – Aktiviert oder deaktiviert
- Dropcount=<number> - Maximale Anzahl von Frames, die in den letzten zwei Sekunden verzögert werden sollten. Die empfohlene Einstellung ist 3 (1,5% der verworfenen Frames)
- Maxjitterbuffer=<ms> - Normalerweise unter 100 ms
- Maxexcessbuffer=<ms> - Wenn sich die Netzwerkverzögerung verbessert, könnte der Jitter-Buffer überdimensioniert sein. Folglich wird Asterisk versuchen, ihn zu reduzieren.
- Minexcessbuffer=<ms> - Sobald der Excess-Buffer auf diesen Wert fällt, beginnt Asterisk, die Puffergröße zu erhöhen.

### Frame-Tagging

Der unten stehende Parameter markiert das IP-Paket im Type-of-Service-Feld. Router können dieses Tag lesen und dadurch den Verkehr priorisieren. Asterisk verwendet DSCP-Codes für dieses Feld (RFC 2474). Zulässige Werte sind CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43 und ef (d. h. expedited forwarding).

```
tos=ef
```

### IAX2-Verschlüsselung

IAX unterstützt Anrufverschlüsselung unter Verwendung eines symmetrischen Schlüssels, einer 128-Bit-Blockchiffre namens AES (Advanced Encryption Standard). Es ist sehr einfach, die Verschlüsselung zwischen IAX-Trunks zu aktivieren. Verwenden Sie in der Datei iax.conf:

```
encryption=yes
```

Um die Verschlüsselung zu erzwingen:

```
forceencryption=yes
```

Um die Kompatibilität mit älteren Versionen zu gewährleisten, müssen Sie möglicherweise die Schlüsselrotation deaktivieren mit:

```
keyrotate=no
```

### IAX2-Debug-Befehle

Nachfolgend finden Sie einige der wichtigsten Konsolenbefehle zur Fehlerbehebung für Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Identifizieren Sie anhand dieser Ausgabe den Anfang und das Ende des Anrufs. Beobachten Sie die Verzögerungs- und Jitter-Informationen, die mit Poke- und Pong-Paketen erhalten wurden. Diese Pakete helfen bei der Erstellung der Ausgabe des Befehls „iax2 show netstats“.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

Um das Debugging auszuschalten, verwenden Sie:

```
vtsvoffice*CLI>iax2 no debug
```

### Zusammenfassung

Dieses Kapitel hat die Stärken und Schwächen des IAX-Protokolls überprüft. Es hat gezeigt, wie IAX in verschiedenen Szenarien funktioniert, wie z. B. bei Softphones und einem Trunk zwischen zwei Asterisk-Servern. Der Trunk-Modus ermöglicht es Ihnen, Bandbreite zu sparen, indem mehr als ein Anruf in einem einzigen Paket transportiert wird. Schließlich haben Sie Konsolenbefehle kennengelernt, die Sie verwenden können, um den Status zu überprüfen und das Protokoll zu debuggen.

## Legacy-SIP: chan_sip und sip.conf (entfernt in Asterisk 21+)

> **Legacy / historisch:** Alles in diesem Abschnitt verwendet den alten `chan_sip`-Treiber und seine `sip.conf`-Konfigurationsdatei. `chan_sip` war für mehrere Releases veraltet und wurde **in Asterisk 21 entfernt**, daher **existiert es in Asterisk 22 nicht**. Keines der unten aufgeführten `sip.conf`-Beispiele wird auf einem aktuellen System ausgeführt — sie werden hier nur aufbewahrt, um zu dokumentieren, wie Legacy-Installationen funktionierten und um Ihnen bei der Migration zu helfen. Für den modernen, unterstützten Weg, dies zu tun, siehe den Abschnitt *PJSIP: the SIP channel* im Kapitel *SIP & PJSIP in depth*. Die SIP-*Protokoll*-Theorie (Methoden, Registrierung, Proxy/Redirect, SDP, NAT-Typen) ist protokollebene und befindet sich in diesem Kapitel; was folgt, ist rein die entfernte `chan_sip`-**Konfiguration**.

Auf Legacy-Systemen bis Asterisk 20 wurde SIP in `/etc/asterisk/sip.conf` konfiguriert, das die zweithäufigste geänderte Datei war (direkt nach `extensions.conf`). Die Abschnitte unten zeigen, wie `chan_sip` Asterisk mit einem SIP-Anbieter verband, wie man zwei Asterisks über SIP verbindet, Domain-Unterstützung, Präsenz, Codec/DTMF/QoS-Optionen, Authentifizierung und NAT — gefolgt von einem Leitfaden zur Migration all dessen auf PJSIP.

### Verbinden von Asterisk mit einem SIP-Anbieter (sip.conf)

Asterisk wird oft verwendet, um eine Verbindung zu einem SIP-VoIP-Anbieter herzustellen. VoIP-Anbieter haben normalerweise bessere Tarife für Telefonanrufe als traditionelle Anbieter. Ein weiterer interessanter und attraktiver Punkt von VoIP-Anbietern ist die Möglichkeit, DID-Nummern in anderen Städten zu kaufen — sogar in fremden Ländern. Dies sind gute Gründe, VoIP für die Telekommunikation zu verwenden. In diesem Abschnitt lernen Sie, wie das Legacy-`chan_sip` Asterisk mit einem VoIP-Anbieter verband. Drei Schritte sind erforderlich, um Asterisk mit einem SIP-Anbieter zu verbinden. Tests können durchgeführt werden, indem Sie ein Konto bei Ihrem bevorzugten Anbieter einrichten. Schritt 1: Registrierung bei einem SIP-Anbieter in sip.conf Um eine Verbindung zu einem SIP-Anbieter herzustellen, benötigen Sie die folgenden Informationen vom Anbieter:

![Asterisk, verbunden mit einem VoIP-Dienstanbieter über das Internet oder ein privates WAN, mit lokalen SIP-Telefonen, die am Asterisk-Server registriert sind](../images/07-sip-and-pjsip-fig07.png)

- Benutzername
- Secret und Remotesecret (Verwenden Sie Secret, um eingehende Anfragen zu authentifizieren, und Remotesecret für ausgehende Anfragen)
- Hostname
- Domain
- Zulässige Codecs

Diese Konfiguration ermöglicht es Ihrem Anbieter, die IP-Adresse von Asterisk zu lokalisieren. In der folgenden Anweisung weisen wir Asterisk an, sich bei einem SIP-Anbieter zu registrieren, der durch den Hostnamen definiert ist, und dem Anbieter die IP-Adresse von Asterisk mitzuteilen. Die Anweisung besagt, dass Sie Anrufe an der Nebenstelle 4100 empfangen möchten. Geben Sie im Abschnitt [general] der Datei sip.conf die folgende Zeile ein:

```
register=>name:secret@hostname/4100
```

Schritt 2: Konfigurieren Sie den [peer] in sip.conf Erstellen Sie einen Eintrag vom Typ Peer für den gewünschten Anbieter, um das Wählen von Asterisk zu vereinfachen.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Schritt 3: Erstellen Sie eine Route zum Anbieter im Dialplan Wir wählen die Ziffern 010 als Zielroute zum Anbieter. Um #610000 innerhalb des Anbieters zu wählen, wählen Sie einfach 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)=”Flavio Gonçalves”)
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### SIP-Optionen spezifisch für das Anbieterszenario

Die folgende Diskussion untersucht die Details der Optionen, die in der Datei sip.conf für die Verbindung zu einem VoIP-Anbieter festgelegt wurden.

```
register=>username:password@hostname/4100
```

Die Anweisung registered in der Datei sip.conf wird verwendet, um sich bei einem Anbieter zu registrieren. Die Registrierungstransaktion wird mit dem Namen und dem Secret authentifiziert. Sie können einen Schrägstrich („/“) verwenden, um eine Nebenstelle für eingehende Anrufe anzugeben. Technisch gesehen wird die Nebenstelle im Feld „Contact“ der SIP-Anfrage platziert. Das Registrierungsverhalten kann durch bestimmte Parameter gesteuert werden:

```
registertimeout=20
registerattempts=10
```

Um zu überprüfen, ob die Registrierung erfolgreich war, war der Legacy-Konsolenbefehl `sip show registry`. In Asterisk 22 ist der äquivalente Befehl `pjsip show registrations` (ausgehende Registrierungen) und `pjsip show endpoints` für den Endpunktstatus.

Der Parameter „username“ wird im Authentifizierungs-Digest verwendet. Der Digest wird unter Verwendung von Benutzername, Secret und Realm berechnet:

```
username=username
```

Host definiert die Adresse oder den Namen des VoIP-Anbieters:

```
host=hostname
```

Die Parameter Fromuser und Fromdomain sind manchmal für die Authentifizierung erforderlich. Diese Parameter werden im SIP-Header-Feld From verwendet:

```
fromuser=username
fromdomain=hostname
```

Wenn Sie eine Verbindung zu einem VoIP-Anbieter herstellen, sind Anmeldeinformationen erforderlich. Nach der ersten Einladung sendet Ihnen der Anbieter eine Nachricht namens „407 Proxy Authentication Required“; Sie geben die Anmeldeinformationen in der nachfolgenden INVITE-Nachricht an. Für eingehende Anrufe fragt Ihr Asterisk-Server nach Anmeldeinformationen für den Anbieter. Offensichtlich hat der Anbieter keine gültigen Anmeldeinformationen für Ihren Asterisk-Server. Wenn Sie insecure=invite verwenden, weisen Sie Asterisk an, die „407 Proxy Authentication Required“ nicht an den Anbieter zu senden und eingehende Anrufe zu akzeptieren. Sie können auch insecure=port, invite verwenden, um den Peer basierend auf der IP-Adresse abzugleichen, ohne die Portnummer abzugleichen.

```
insecure=invite, port
```

### Verbinden zweier Asterisk-Server über SIP (sip.conf)

Sie können SIP verwenden, um zwei Asterisk-Boxen miteinander zu verbinden. Es ist wichtig, auf den Dialplan zu achten, bevor Sie mit dieser Konfiguration fortfahren. Benutzer möchten andere PBXs normalerweise mit minimalem Aufwand verbinden. Die Idee hier ist, eine Nebenstellennummer nur zu verwenden, um eine Verbindung zur anderen PBX herzustellen. Schritt 1: Bearbeiten Sie die Datei sip.conf auf Server A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Schritt 2: Bearbeiten Sie die Datei sip.conf auf Server B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Verbindung zweier Asterisk-Server über SIP: Server A (Nebenstellen 4400/4401) und Server B (Nebenstellen 4500/4501) tauschen SIP-Signalisierung aus, sodass Benutzer auf jeder PBX die andere wählen können](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Schritt 3: Bearbeiten Sie die Datei extensions.conf auf Server A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Schritt 4: Bearbeiten Sie die Datei extensions.conf auf Server B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk-Domain-Unterstützung (sip.conf)

Das SIP-Protokoll folgt der Internet-Architektur. Das erste, was vor der Konfiguration von SIP zu tun ist, ist die korrekte Einstellung der DNS-Server. In einer SIP-Umgebung können Sie einen Benutzer anrufen, der sich in einem beliebigen SIP-Proxy befindet, und andere Benutzer können Sie ebenfalls unter Verwendung Ihres SIP Uniform Resource Identifier (URI) anrufen. Um einen DNS-Server für SIP einzustellen, müssen Sie SRV-Einträge zu Ihrem DNS-Server hinzufügen.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

Nach der Konfiguration des DNS können Sie den URI verwenden, der auf einen SIP-Benutzer, ein SIP-Telefon oder eine Telefonnebenstelle zeigt. Ein SIP-URI sieht ähnlich aus wie eine E-Mail-Adresse (z. B. sip:chuck@yourpartnerdomain.com). Unter Verwendung von SIP-URIs ist keine Telefonnummer erforderlich, um einen Anruf von einem SIP-Telefon zu einem anderen zu tätigen. Um einen externen Benutzer anzurufen, verwenden Sie einfach eine Anweisung wie die unten gezeigte.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Bestimmte Parameter können das Domain-Verhalten steuern.

```
srvlookup=yes
```

Dieser Parameter aktiviert DNS SRV-Lookups bei ausgehenden Anrufen. Unter Verwendung dieses Parameters ist es möglich, Anrufe unter Verwendung von SIP-Namen basierend auf der Domain zu tätigen.

```
allowguest=yes
```

Dieser Parameter ermöglicht es, eine externe Einladung ohne Authentifizierung zu verarbeiten. Er verarbeitet den Anruf innerhalb des Kontexts, der im allgemeinen Abschnitt oder in der Domain-Anweisung definiert ist. Warnung: Wenn Sie einen Kontext im allgemeinen Abschnitt mit Zugriff auf das PSTN definieren, kann ein externer Benutzer das PSTN über Ihre PBX wählen. In diesem Fall fallen Gebühren an. Erlauben Sie nur Ihre eigenen Nebenstellen in dem Kontext, der im allgemeinen Abschnitt definiert ist.

![Verbindung zu anderen SIP-Servern nach Domain: youdomain.com und yourpartnerdomain.com tauschen SIP-Signalisierung aus, sodass Benutzer wie lee und bruce chuck und norris unter Verwendung von SIP-URIs anrufen können](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

Der Domain-Befehl ermöglicht es Ihnen, mehr als eine Domain innerhalb von Asterisk zu handhaben. Wenn ein Anruf von einer bestimmten Domain kommt, wird er an einen bestimmten Kontext weitergeleitet.

```
;autodomain=yes
```

Dieser Parameter schließt die lokale IP und den Hostnamen in die zulässigen Domains ein.

```
;allowexternaldomains=no
```

Der Standardwert ist yes. Kommentieren Sie die Zeile aus, um Anrufe an externe Domains zu verbieten.

### SIP-erweiterte Konfigurationen (sip.conf)

Dieser Abschnitt erklärt einige erweiterte Parameter des Legacy-SIP-Kanals, wie Präsenz, Codec-Auswahl, DTMF-Optionen und QoS-Paketmarkierung. Die **Konzepte** (BLF/Präsenz, Codec-Aushandlung, DTMF-Modi, DSCP-Markierung) werden auf PJSIP übertragen, aber die hier gezeigten `sip.conf`-Parameternamen existieren in Asterisk 22 **nicht**. Bei PJSIP ist der DTMF-Modus `dtmf_mode=` an einem Endpunkt, und Codecs werden mit `allow=`/`disallow=` eingestellt.

#### SIP-Präsenz

SIP-Präsenz ist in Asterisk teilweise implementiert. Asterisk unterstützt Anfragen wie SUBSCRIBE und NOTIFY-Benutzer abhängig vom Status eines Kanals. Asterisk unterstützt die SIP-Methode PUBLISH nicht. Mit anderen Worten, Sie können die Zustände (besetzt, leer und klingelnd) eines Kanals abonnieren, aber keine Informationen wie „abwesend“ oder „nicht stören“ veröffentlichen. Das gebräuchlichste Szenario für Präsenz ist das Busy Lamp Field (BLF), bei dem Sie das Verhalten eines KS-Systems mit Lampen für jede Nebenstelle und jeden Trunk simulieren. SIP-Parameter für Präsenz:

- allowsubscribe=yes: SIP-Abonnementmethoden erlauben
- subscribecontext=sip_subscribers: Kontext, in dem nach Hinweisen gesucht werden soll
- notifyring=yes: SIP NOTIFY bei Klingeln senden
- notifyhold=yes: SIP NOTIFY bei Halten senden
- counteronpeer (umbenannt von limitonpeer für Asterisk 1.4.x): Den Zähler nur auf der Peer-Seite anwenden
- callcounter=yes: Anrufzähler im Gerät aktivieren.
- busylevel=1: Schwellenwert für die Anzahl der Anrufe, um das Gerät als besetzt zu betrachten.

Zum Beispiel: Schritt 1: Das Testen der SIP-Präsenz mit Asterisk ist nicht so schwer. Konfigurieren wir zuerst die Dateien sip.conf und extensions.conf.

In der Datei sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: Konfigurieren Sie nun das Softphone für die Verwendung von Präsenz. Wir zeigen Ihnen, wie Sie das SipPulse Softphone konfigurieren.

- Sequenz: Rechtsklick->SIP Account Settings->Properties->Presence
- Ändern Sie das Präsenzmodell von Peer-to-Peer auf Presence Agent, wodurch das Softphone Asterisk für SIP-Ereignisse abonniert.

Step 3: Fügen Sie den Kontakt zu anderen Softphones hinzu. In diesem Beispiel ist das SipPulse Softphone Konto 2000, also fügen wir einen Kontakt für Konto 2001 hinzu. Sequenz: Öffnen Sie das rechte Panel (Präsenz-Panel im Softphone)->Klicken Sie auf Contacts->Add a contact. Geben Sie den Namen 2001 ein. Anzeigen als 2001 und vergessen Sie nicht, das Kästchen Show this contact’s availability zu aktivieren.

Step 4: Rufen Sie nun die Nebenstelle 2001 an und überprüfen Sie den Status des Telefons im rechten Panel des Softphones. Verwenden Sie den Konsolenbefehl `core show hints`, um zu sehen, wie sich der Präsenzstatus auf dem Server ändert (im Legacy chan_sip zeigte `sip show inuse`, wie viele Anrufe Sie auf jeder Leitung hatten). Verwenden Sie in Asterisk 22 `pjsip show endpoints`, um den Endpunkt- und Kanalstatus zu überprüfen. Der Präsenz-/BLF-Status erscheint in den Kontakten oder im BLF-Panel des Softphones — genau wie er angezeigt wird, hängt vom Client ab.

#### Codec-Konfiguration

Die Codec-Konfiguration ist einfach und unkompliziert. Sie können die Wörter allow und disallow im Abschnitt [general] oder im Peer-/Benutzerabschnitt festlegen. Die bewährte Methode ist die Standardisierung des Codecs, um Transcoding zu vermeiden, das prozessorintensiv ist. Bitte verwenden Sie denselben Codec für Nachrichten und Prompts.

```
[general]
disallow=all
allow=g729
```

#### DTMF-Optionen

Bei bestimmten Gelegenheiten übergeben Sie Ziffern an eine Anwendung wie Voicemail oder Interactive Voice Response (IVR). Es ist wichtig, DTMF korrekt zu übergeben. Die einfachste Methode zur Übergabe von DTMF heißt inband. Sie wird im Abschnitt [general] oder im Peer-/Benutzerabschnitt der Datei sip.conf festgelegt. Wenn Sie dtmfmode=inband einstellen, werden DTMF-Töne als Töne im Audiokanal erzeugt. Das Hauptproblem bei dieser Methode ist, dass bei der Komprimierung des Audiokanals unter Verwendung eines Codecs wie g729 die Töne verzerrt werden und DTMF-Töne nicht ordnungsgemäß erkannt werden. Wenn Sie planen, dtmfmode=inband zu verwenden, verwenden Sie den g.711-Codec (ulaw und alaw).

```
dtmfmode=inband
```

Ein weiterer Ansatz ist die Verwendung von RFC2833, die es Ihnen ermöglicht, DTMF-Töne als benannte Ereignisse in den RTP-Paketen zu übergeben.

```
dtmfmode=rfc2833
```

Schließlich können Sie DTMF-Ziffern innerhalb von SIP-Paketen anstelle von RTP-Paketen übergeben. Diese Methode ist in RFC3265 (Signalisierungsereignisse) und RFC2976 definiert.

```
dtmfmode=info
```

Nach der Veröffentlichung von Version 1.2 ist es nun möglich, Folgendes zu verwenden:

```
dtmfmode=auto
```

Dies versucht, RFC2833 zu verwenden; wenn dies nicht möglich ist, werden In-Band-Töne verwendet.

#### Konfiguration der Quality-of-Service (QoS)-Markierung

QoS ist eine Reihe von Techniken, die für die Sprachqualität verantwortlich sind. QoS ist so implementiert, dass Bandbreite, Latenz und Jitter reduziert werden. Die Haupt-QoS-Funktionen sind Paketplanung, Fragmentierung und Header-Komprimierung. QoS wird in Switches und Routern implementiert, nicht von Asterisk selbst. Asterisk kann jedoch Routern und Switches helfen, indem es Pakete für die Express-Zustellung markiert. Die Markierung erfolgt unter Verwendung von Differentiated Services Code Points (DSCP), die in RFC 2474 und RFC 2475 definiert sind.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Ab Version 1.4 können Sie unterschiedliche Codes für Signalisierung (SIP), Audio (RTP) und Video (RTP) angeben.

### SIP-Authentifizierung (sip.conf)

Wenn das Legacy-`chan_sip` einen SIP-Anruf empfing, folgte es den Regeln, die im folgenden Diagramm beschrieben sind. Drei Parameter spielten eine wichtige Rolle bei der SIP-Authentifizierung. In Asterisk 22 wird die Authentifizierung stattdessen mit PJSIP-`auth`-Objekten (`type=auth`, `auth_type=userpass`, `username=`, `password=`) konfiguriert, auf die von einem Endpunkt verwiesen wird, und die IP-Zugriffskontrolle erfolgt mit `permit=`/`deny=` am Endpunkt oder über eine `acl`.

![Legacy chan_sip-Authentifizierungsentscheidungsfluss: Asterisk überprüft den From-Header gegen sip.conf, versucht den passenden type=user/peer-Abschnitt und MD5-Anmeldeinformationen und fällt auf insecure=invite oder allowguest zurück, bevor der Anruf zugelassen oder abgelehnt wird](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Dieser Parameter steuert, ob ein Benutzer ohne entsprechenden Peer ohne Namen und Secret authentifizieren kann. Wir haben diesen Parameter im Abschnitt Domain-Unterstützung diskutiert.

```
insecure=invite,port
```

Wenn wir insecure=invite verwenden, generiert Asterisk nicht die Nachricht „407 Proxy Authentication Required“. Ohne diese Nachricht kann der Benutzer einen Anruf ohne Authentifizierung tätigen. Dies wird oft verwendet, um eine Verbindung zu VoIP-Dienstanbietern herzustellen. Die Anrufe, die vom VoIP-Dienstanbieter kommen, werden normalerweise nicht authentifiziert.

```
autocreatepeer=yes/no
```

Dieser Befehl wird verwendet, wenn Asterisk mit einem SIP-Proxy verbunden ist. Er erstellt dynamisch einen Peer für jeden Anruf. Wenn diese Option aktiviert ist, kann sich jeder UAC mit dem Asterisk-Server verbinden. Es ist wichtig, die IP-Verbindung auf den SIP-Proxy zu beschränken. Der SIP-Proxy wiederum kümmert sich um die Zugriffskontrolle. Die Peer-Konfiguration basiert auf den allgemeinen Optionen sowie dem „Contact“-Header-Feld des SIP-Pakets. Warnung: Verwenden Sie dies mit äußerster Vorsicht, da es Asterisk vollständig öffnet.

```
secret=secret, remotesecret=secret
```

Dieser Parameter konfiguriert das Secret für die Authentifizierung; verwenden Sie secret für eingehende Anfragen und remotesecret für ausgehende Anfragen. Wenn Sie die Secrets nicht in Textdateien präsentieren möchten, können Sie md5secret verwenden, um einen Hash anstelle des Secrets einzufügen. Um das MD5-Secret zu generieren, können Sie verwenden:

```
echo –n “username:realm:secret” |md5sum
```

Verwenden Sie dann die folgende Anweisung:

```
md5secret=0b0e5d467890....
```

Warnung: Vergessen Sie nicht, den –n-Parameter zu verwenden; der Wagenrücklauf wird bei der MD5-Berechnung verwendet.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

Die oben genannten Anweisungen verweigern alle IP-Adressen und erlauben UAC nur aus dem lokalen Netzwerk (192.168.1.0/24).

#### RTP-Optionen

Es ist möglich, einige RTP-Parameter zu steuern.

```
rtptimeout=60
```

Dies beendet Anrufe ohne RTP-Aktivität für mehr als 60 Sekunden, wenn sie nicht gehalten werden.

```
rtpholdtimeout=120
```

Dies beendet Anrufe ohne RTP-Aktivität, selbst wenn sie gehalten werden (sollte größer als rtptimeout sein).

### SIP-NAT-Durchquerung (sip.conf)

Die NAT-*Theorie* (die vier NAT-Typen, das Contact-Header-Problem, Keep-Alives und das Erzwingen von Medien durch den Server) ist protokollebene und wird im Kapitel *SIP & PJSIP in depth* behandelt. Die hier gezeigten `sip.conf`-Parameter (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) sind **Legacy chan_sip** und wurden in Asterisk 21+ entfernt. Bei PJSIP werden diese auf Transport-/Endpunkteinstellungen wie `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address` und `local_net=` am Transport sowie `qualify_frequency=` am AOR abgebildet.

Im Legacy chan_sip hatte der Parameter `nat` fünf Optionen:

- nat = no — Keine spezielle NAT-Behandlung außer RFC3581
- nat = force_rport — So tun, als gäbe es einen rport-Parameter, auch wenn keiner vorhanden war
- nat = comedia — Senden Sie Medien an den Port, von dem Asterisk sie empfangen hat, unabhängig davon, wo das SDP sagt, dass sie gesendet werden sollen.
- nat = auto_force_rport — Setzen Sie die Option force_rport, wenn Asterisk NAT erkennt (Standard)
- nat = auto_comedia — Setzen Sie die Option comedia, wenn Asterisk NAT erkennt

Wenn Sie die Anweisung „nat=force_rport“ in die Datei sip.conf einfügen, weisen Sie Asterisk an, die Adresse im „Contact“-Header-Feld des SIP-Headers zu ignorieren und die Quell-IP-Adresse und den Port im IP-Header des Pakets zu verwenden und die Medien auch an die Adresse zurückzusenden, von der sie empfangen wurden, wobei der Inhalt des SDP-Headers ignoriert wird.

```
nat=force_rport,comedia
```

Es ist notwendig, die NAT-Zuordnung offen zu halten. Wenn NAT ein Timeout hat, kann Asterisk keine Einladung an den UAC senden. Der UAC kann Anrufe senden, aber keine empfangen. Die folgende Anweisung kann verwendet werden, um NAT offen zu halten.

```
qualify=yes
```

Qualify sendet regelmäßig ein SIP-Paket unter Verwendung der OPTIONS-Methode, was hilft, NAT offen zu halten. Qualify sendet alle 60 Sekunden ein OPTIONS und alle 10 Sekunden, wenn der Host nicht erreichbar ist. Sie können „sip show peers“ verwenden, um die Latenz für die Peers zu sehen. Wenn das NAT des Benutzers vom symmetrischen Typ ist, ist es nicht möglich, Pakete direkt von einem UAC zum anderen zu senden; in diesem Fall müssen Sie das RTP über Asterisk erzwingen unter Verwendung von:

```
directmedia=no
```

#### Asterisk hinter NAT (sip.conf)

Alle vorherigen Szenarien gehen davon aus, dass der Asterisk-Server eine externe (gültige) Internetadresse hat. Manchmal wird der Asterisk-Server hinter einer Firewall mit NAT implementiert. In diesem Fall sind einige zusätzliche Konfigurationen erforderlich.

![Asterisk hinter NAT: Eine Firewall bildet die öffentliche Adresse 200.180.4.168 auf den internen Asterisk-Server (192.168.1.100) ab und leitet SIP auf UDP 5060 und den RTP-Bereich UDP 10000–20000, der in rtp.conf definiert ist, weiter](../images/07-sip-and-pjsip-fig13.png)

Schritt 1: Konfigurieren Sie die Firewall, um den UDP-Port 5060 statisch an den Asterisk-Server weiterzuleiten. Schritt 2: Konfigurieren Sie die Firewall, um die UDP-Ports von 10000 bis 20000 statisch weiterzuleiten. Wenn Sie die Anzahl der geöffneten Ports einschränken möchten, können Sie die Datei rtp.conf bearbeiten, um den RTP-Portbereich zu ändern. Eine andere Möglichkeit ist die Verwendung einer intelligenten Firewall, die das SIP-Protokoll unterstützt, um die RTP-Ports dynamisch zu öffnen.

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

Schritt 3: Konfigurieren Sie Asterisk so, dass die externe Adresse in die Header-Felder der SIP-Pakete einschließlich Session Description Protocol (SDP) aufgenommen wird. Sie können dies erreichen, indem Sie die folgenden zwei Anweisungen zur Datei sip.conf hinzufügen:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

Der erste Parameter externaddr weist Asterisk an, die externe IP-Adresse in die SIP-Header für externe Ziele aufzunehmen. Der zweite Parameter localnet ermöglicht es Asterisk, zwischen externen und internen Adressen zu unterscheiden. Optional können Sie externhost verwenden, wenn Sie ein dynamisches DNS mit einer DHCP-Adresse auf dem Server verwenden.

### SIP-Wählstrings (chan_sip)

Die `SIP/...`-Wählstring-Technologie, die unten gezeigt wird, ist der entfernte chan_sip-Treiber. Verwenden Sie in Asterisk 22 stattdessen die `PJSIP/...`-Technologie — zum Beispiel `Dial(PJSIP/2000)` oder `Dial(PJSIP/${EXTEN}@provider)`. Die Formen und Bedeutungen sind ansonsten analog.

Sie können ein Legacy-SIP-Ziel unter Verwendung verschiedener Wählstrings anrufen:

```
SIP/peer
```

- ; Muss einen definierten Peer in sip.conf haben

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Beispiele sind:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migration eines Legacy-chan_sip-Systems auf PJSIP

Da `chan_sip` in Asterisk 21 entfernt wurde und in Asterisk 22 nicht mehr vorhanden ist, muss jede bestehende `sip.conf`-Installation auf PJSIP migriert werden. Der größte konzeptionelle Wandel besteht darin, dass ein einzelner `sip.conf` `[peer]` oder `[friend]` in mehrere PJSIP-Objekte aufgeteilt wird, jedes mit einem `type=`: ein **Endpunkt** (Anruf-/Codec-/Medieneinstellungen), ein oder mehrere **aor**-Objekte (wo das Gerät erreicht werden kann / Registrierung), ein **auth**-Objekt (Anmeldeinformationen) und ein gemeinsamer **Transport** (der hörende Socket, NAT-Adressen). Die folgende Tabelle ordnet die gebräuchlichsten Konzepte zu.

| Legacy sip.conf-Konzept | PJSIP-Äquivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]`-Block | `type=endpoint` + `type=aor` + `type=auth` (referenziert über `auth=` und `aors=`) |
| `type=friend` / `type=peer` / `type=user` | ein einzelner `type=endpoint` (PJSIP hat keine Unterscheidung zwischen Friend/Peer/User) |
| `host=dynamic` (Gerät registriert) | `type=aor` mit `max_contacts=1`; das Gerät REGISTERt, um seinen Kontakt zu aktualisieren |
| `host=<ip/hostname>` (statisch) | `type=aor` mit einem statischen `contact=sip:host:port` |
| `register=>user:secret@host/ext` (ausgehend) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` am Endpunkt |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` am Endpunkt (gleiche Syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — auch `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` am Endpunkt |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (Endpunkt) |
| `qualify=yes` | `qualify_frequency=` (Sekunden) am **aor** |
| `externaddr=` | `external_media_address=` und `external_signaling_address=` am **Transport** |
| `localnet=` | `local_net=` am **Transport** |
| `insecure=invite` (Anbieter, keine Auth) | `auth=`/`outbound_auth=` weglassen und `identify` (`type=identify`, `match=`) verwenden |
| `allowguest=yes` | `anonymous` Endpunkt + `allow_unauthenticated_options` (mit Vorsicht verwenden) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (und `cos_audio` / `cos_video`) am Endpunkt |

Eine registrierende Nebenstelle, die in Legacy-`sip.conf` so aussah:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

wird in `pjsip.conf` auf Asterisk 22 zu:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### Das sip_to_pjsip.py-Konvertierungsskript

Asterisk liefert ein Hilfsskript, **`sip_to_pjsip.py`**, das eine bestehende `sip.conf` liest und eine `pjsip.conf` produziert. Sie können es direkt im Verzeichnis /etc/asterisk ausführen. Das Dienstprogramm befindet sich im Asterisk-Quellbaum unter `contrib/scripts/sip_to_pjsip/`, wobei `${PATH_TO_ASTERISK_SOURCE}` der Pfad ist, in dem die Asterisk-Quelldateien gefunden werden (normalerweise /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Wenn Sie es mit der Option `--help` ausführen, sehen Sie seine Optionen:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

Es akzeptiert auch optionale positionale Argumente — `[input-file [output-file]]`, standardmäßig `sip.conf` und `pjsip.conf` im aktuellen Verzeichnis.

Betrachten Sie die Ausgabe als **Ausgangspunkt**: Überprüfen Sie jedes generierte Objekt, insbesondere Transporte, NAT-Einstellungen und Codec-Listen, und testen Sie gründlich, bevor Sie in die Produktion gehen.

Migrieren wir die sip.conf in unseren Begleit-Labs an der VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

Während die Konvertierung in Ordnung zu sein scheint, können wir sehen, dass einige Elemente wie qualify=yes nicht direkt abgebildet werden können. Um dies zu beheben, müssen Sie dem aor-Abschnitt den Befehl qualify_frequency=time in Sekunden hinzufügen. Beispiel unten.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

Die vollständige PJSIP-Konfiguration wird im Kapitel *SIP & PJSIP in depth* behandelt, und die offizielle Dokumentation unter docs.asterisk.org bietet eine vollständige Abdeckung des Kanals. In unseren Begleit-Labs unter voip.school können Sie in Lab 5 üben, was Sie gerade gelernt haben.

## Quiz

1. Markieren Sie bezüglich der beiden analogen Foreign eXchange-Schnittstellen die korrekten Aussagen (wählen Sie alle zutreffenden aus):
   - A. Eine FXO-Schnittstelle verbindet sich mit der Vermittlungsstelle des öffentlichen Telefonnetzes (PSTN) und bezieht von dort das Freizeichen.
   - B. Eine FXS-Schnittstelle liefert Freizeichen und Klingelspannung an ein Standard-Analogtelefon, Fax oder Modem.
   - C. Eine FXS-Schnittstelle ist der richtige Weg, um Asterisk mit einer Telco-Leitung zu verbinden.
   - D. Eine FXO-Schnittstelle kann auch mit einem Nebenstellenport einer Legacy-PBX verbunden werden.
2. Welche der folgenden Punkte gehören zur Überwachungssignalisierung auf einer analogen Leitung (wählen Sie alle zutreffenden aus)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, Knacken und Rauschen auf einer analogen DAHDI-Karte werden am häufigsten verursacht durch:
   - A. Die Art und Weise, wie Asterisk kompiliert wurde
   - B. PCI-Interrupt-Konflikte
   - C. Einen falschen SIP-Codec
   - D. Einen fehlenden Dialplan
4. Für eine präzise Abrechnung auf analogen Kanälen müssen Sie genau erkennen, wann die Gegenseite antwortet. Welche Funktion aktivieren Sie auf Asterisk (und fordern sie bei der Telefongesellschaft an), um dies zu tun?
   - A. Antwortumkehr (Answer reversal)
   - B. Abrechnungsumkehr (Billing reversal)
   - C. Polaritätsumkehr (Polarity reversal)
   - D. Freizeichenerzeugung
5. Die DAHDI-Hardware ist unabhängig von Asterisk: Die physische Karte wird in `/etc/dahdi/system.conf` konfiguriert, während `chan_dahdi.conf` die Asterisk-Kanäle definiert, nicht die Hardware selbst.
   - A. Wahr
   - B. Falsch
6. Markieren Sie bezüglich der Kapazität und Signalisierung digitaler Trunks die korrekten Aussagen (wählen Sie alle zutreffenden aus):
   - A. Ein E1-Trunk trägt 30 Sprachkanäle und ein T1-Trunk trägt 24.
   - B. Ein ISDN PRI verwendet 30B+D auf einem E1 und 23B+D auf einem T1.
   - C. ISDN ist ein Beispiel für CCS-Signalisierung, während MFC/R2 ein Beispiel für CAS-Signalisierung ist.
   - D. T1 ist der digitale Trunk, der am häufigsten in Europa und Lateinamerika verwendet wird.
7. Welches Dienstprogramm erkennt automatisch DAHDI-Karten und generiert `/etc/dahdi/system.conf` und `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. Bei der Migration eines Legacy-`sip.conf` `[friend]` auf PJSIP muss ein einzelner Block in mehrere Objekte aufgeteilt werden. Welcher Satz von PJSIP-`type=`-Objekten ersetzt normalerweise eine registrierende `[friend]`?
   - A. `type=endpoint`, `type=aor` und `type=auth`
   - B. `type=peer` und `type=user`
   - C. `type=sip` nur
   - D. `type=channel` und `type=device`
9. Was ist der praktische Hauptvorteil der Verwendung des IAX2-Trunk-Modus zwischen zwei Asterisk-Servern?
   - A. Es verschlüsselt jeden Anruf standardmäßig mit TLS
   - B. Es trägt mehrere Anrufe unter einem einzigen Header, was Bandbreite spart
   - C. Es macht jeden Codec überflüssig
   - D. Es weist einen separaten UDP-Port pro Anruf für bessere Qualität zu
10. RSA-Schlüssel können für die IAX2-Authentifizierung verwendet werden. Welchen Schlüssel müssen Sie geheim halten und welchen geben Sie dem anderen Server?
    - A. Öffentlichen Schlüssel geheim halten; privaten Schlüssel teilen
    - B. Privaten Schlüssel geheim halten; öffentlichen Schlüssel teilen
    - C. Gemeinsamen Schlüssel geheim halten; privaten Schlüssel teilen
    - D. Beide Schlüssel müssen geteilt werden

**Antworten:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
