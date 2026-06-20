# Legacy channels: analog, TDM & IAX2

In einer reinen VoIP-Welt im Jahr 2026 sind die in diesem Kapitel beschriebenen Kanaltypen immer seltener: Die meisten neuen Deployments nutzen SIP‑Trunks und PJSIP‑Endpoints über Ethernet, ohne jegliche Telefonie‑Hardware. Asterisk 22 unterstützt dennoch die meisten von ihnen vollständig. Analoge (FXO/FXS) und digitale TDM (E1/T1/ISDN PRI/BRI) Konnektivität wird über DAHDI bereitgestellt – den Treiber‑Stack, der ursprünglich von Digium entwickelt wurde und 2018 von Sangoma übernommen wurde, nachdem die früheren Zaptel‑Treiber nach einem Markenstreit umbenannt wurden. Server‑zu‑Server‑Konnektivität über IAX2 wird von `chan_iax2` bereitgestellt, das weiterhin ausgeliefert und unterstützt wird, aber nun eindeutig ein Legacy‑Protokoll ist.

Dieses Kapitel sammelt außerdem das **legacy SIP**‑Material: den alten `chan_sip`‑Treiber und seine `sip.conf`‑Konfiguration – entfernt in Asterisk 21 und nicht mehr vorhanden in Asterisk 22 – zusammen mit einer vollständigen Anleitung zur Migration eines bestehenden `sip.conf`‑Systems zu PJSIP. Wenn Sie ein reines SIP‑Setup auf PJSIP ohne Telefoniekarten, ohne IAX2‑Trunks und ohne legacy `sip.conf` zum Konvertieren betreiben, können Sie dieses Kapitel bedenkenlos überspringen.

## Objectives

- Connect Asterisk to analog lines and phones with FXO/FXS interfaces through DAHDI;
- Recognize digital TDM connectivity (E1/T1, ISDN PRI/BRI) and how it is configured;
- Configure IAX2 (`chan_iax2`) for server-to-server trunks and understand why it is now legacy;
- Identify the retired `chan_sip` driver and the `sip.conf` syntax you may still encounter; and
- Migrate an existing `chan_sip`/`sip.conf` system to PJSIP.

## Analog channels (FXO/FXS)

As of Asterisk 22, DAHDI and analog telephony cards remain fully supported, and DAHDI still builds against current kernels. The majority of new deployments are nonetheless pure VoIP (SIP trunks, PJSIP), so analog/TDM hardware is now a niche choice — found mainly in legacy environments, rural PSTN connectivity, or regulated markets. Everything below still applies to those scenarios.

There are several ways to connect the public switched telephone network (PSTN). The best way depends on how the telephone company makes this connection available in your area. The simplest way is to use an analog line, similar to the line you use at home. In this section, we will show you how to configure analog cards from Sangoma™ (formerly Digium™) and Xorcom™.

### Objectives

By the end of this chapter you should be able to:

- Recognize the main telephony terms and acronyms;
- Understand when to use digital and analog circuits;
- Recognize the difference between FXS and FXO; and
- Configure Asterisk for FXS and FXO.

### Telephony basics

Most analog implementations use a pair of cooper lines named tip and ring. When a loop is closed, the phone receives the dial tone from the telecom switch (or the private PBX). The most frequently used signaling is loop-start; other, less common kinds of signaling including ground start, which is used in several countries. The three categories of signaling are:

- Supervision signaling
- Address signaling
- Information signaling

#### Supervision signaling

The main supervision signalings are on-hook, off-hook, and ringing.

- **On-Hook** – When a user puts the phone on the hook, the PBX interrupts and does not allow the electric current to pass. In this state, the circuit is named on-hook. In this position, only the ringer is active.
- **Off-Hook** – Before starting a phone call, the phone needs to pass to the off-hook state. Removing the handset from the hook closes the loop and indicates to the PBX that the user intends to make a call. Upon receiving this indication, the PBX generates a dial tone, indicating to the user that it is ready to accept the destination address (i.e., phone number).
- **Ringing** – When a user calls another phone, it generates a voltage to the ringer that warns the other user about a call being received. Signaling varies by country, with different tones for different countries.

You can personalize Asterisk tones to your country by modifying the indications.conf file. For example:

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

Sie können zwei Arten von Signalisierung zum Wählen verwenden. Die erste und gebräuchlichste ist Dual Tone Multi‑Frequency (dtmf), während die andere Pulswahl (verwendet bei alten Wählscheibentelefonen) ist. Telefone haben ein Tastenfeld zum Wählen, und jede Taste ist mit zwei Frequenzen verbunden: einer hohen und einer niedrigen. Im Fall der dtmf‑Signalisierung gibt die Kombination dieser Töne an, welche Ziffer gedrückt wird. MFC/R2 verwendet einen Mehrfrequenzton, der sich von dtmf unterscheidet.

#### Informationssignalisierung

Informationssignalisierung zeigt den Verlauf des Anrufs und verschiedene Ereignisse.

- Wähltton
- Besetztton
- Rückklingelton
- Überlastton
- Ungültige Nummer
- Bestätigungston

### PSTN‑Schnittstellen

Wie bei alten PBXs ist es oft erforderlich, die Asterisk PBX an das PSTN anzuschließen. Hier zeigen wir Ihnen, wie das geht. Normalerweise haben Sie drei Optionen für Telefonleitungen.

- Analog: Die häufigste Form für Zuhause und kleine Unternehmen, normalerweise geliefert mit einem metallischen Kupferdrahtpaar.  
- Digital: Wird verwendet, wenn viele Leitungen nötig sind. Eine digitale Leitung wird normalerweise von einem CSU/DSU oder einem Fiber‑Multiplexer bereitgestellt. Der Endbenutzer‑Stecker ist in der Regel ein RJ45. In einigen Ländern werden E1‑Leitungen mit zwei Koaxial‑BNC‑Steckern geliefert; in diesem Fall benötigen Sie einen Adapter, um den RJ45‑Stecker mit der Telefonie‑Karte zu verbinden.  
- SIP: Diese Option wurde kürzlich entwickelt. Die Telefonleitung wird über eine Datenverbindung mit SIP‑Signalisierung (VoIP) bereitgestellt. Dies ist eine gute Option für den Einsatz mit Asterisk, da Sie keine Telefoniekarte kaufen müssen. Telefonate werden direkt an den Ethernet‑Port geliefert. Ein weiterer Vorteil ist, dass Sie möglicherweise CPU‑Ressourcen freigeben können, indem Sie das Codec‑Transcoding vermeiden.

### Analoge FXS-, FXO- und E&M-Schnittstellen

Mehrere Arten von analogen Schnittstellen sind verfügbar. Es ist grundlegend, die Unterschiede zwischen diesen Schnittstellen zu verstehen, um zu lernen, wie man sich mit dem Telefonnetz sowie mit anderen PBXs verbindet. Hier zeigen wir Ihnen die E&M‑Schnittstelle. Obwohl sie derzeit nicht für Asterisk verfügbar ist und von mehreren Anbietern eingestellt wurde, können Sie Router und PBXs mit dieser Art von Schnittstelle finden, sodass es besser ist, zu wissen, womit Sie es zu tun haben.

#### Foreign eXchange (FX) Schnittstellen

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![Asterisk zwischen einem analogen Telefon (FXS) und der Telefonnetzleitung (FXO): Die FXS‑Seite liefert Wähltöne und Klingeln für das Telefon, während die FXO‑Seite den Wähltton vom Vermittlungsamt bezieht.](../images/10-legacy-fig01.png)

Das FXO‑Interface wird verwendet, um eine Verbindung zu einer Zentralstelle (CO) oder einer Nebenstelle einer anderen PBX herzustellen. Es kommuniziert direkt mit einer Telefonleitung, die vom PSTN kommt. Eine weitere Möglichkeit besteht darin, das FXO‑Interface an eine vorhandene PBX anzuschließen, wodurch die Kommunikation zwischen Asterisk und der Legacy‑PBX ermöglicht wird. Das Anschließen von Asterisk an einen PBX‑Port und das Bereitstellen einer entfernten Nebenstelle über VoIP wird häufig als off‑promises extension (OPX) bezeichnet. Ein FXO‑Interface empfängt einen Wähltton.  

Foreign eXchange Station (FXS)  

Das FXS‑Interface versorgt ein analoges Telefon, Modem oder Fax. Das FXS liefert den Wähltton und die Stromversorgung für ein Telefon.

#### Trunk-Signalisierung

- Loop-Start
- Ground-Start
- Kewlstart

Die Verwendung von kewlstart Signalisierung in Asterisk ist fast standardmäßig. Kewlstart ist nicht die Signalisierung selbst, sondern fügt dem Stromkreis Intelligenz hinzu, indem es überwacht, was auf der anderen Seite geschieht. Kewlstart basiert auf loop-start. Die meisten Switches unterstützen dieses Feature nicht, das verwendet wird, um die Auflegbenachrichtigung zu erhalten.

- Loopstart: Wird in den meisten analogen Leitungen verwendet, es ermöglicht dem Telefon, „on-hook“ und „off-hook“ anzuzeigen, und dem Switch, „ring“ und „no-ring“ anzuzeigen. Das ist wahrscheinlich das, was die meisten Menschen zu Hause haben. Der Name stammt von der Tatsache, dass die Leitung immer offen ist. Wenn Sie die Schleife schließen, liefert der Switch einen Wähltton. Ein eingehender Anruf wird durch eine 100 V Klingelspannung über das offene Paar signalisiert.

![Asterisk arbeitet als VoIP-Gateway: Ein FXO-Port verbindet sich mit einer Legacy-PBX-Erweiterung, während ein entferntes Asterisk diese Leitung über IP an ein analoges Telefon über einen FXS-Port liefert (eine Off-Premises-Erweiterung, oder OPX).](../images/10-legacy-fig02.png)

- Groundstart: Ähnlich wie Loopstart. Wenn Sie einen Anruf tätigen möchten, wird eine Seite der Leitung kurzgeschlossen. Wenn die Vermittlung diesen Zustand erkennt, kehrt sie die Spannung über das offene Paar um, und dann wird die Schleife geschlossen. Folglich wird die Leitung zuerst belegt, bevor sie dem Anrufer angeboten wird.  
- Kewlstart: Fügt den Schaltkreisen Intelligenz hinzu, wodurch die andere Seite überwacht werden kann. Kewlstart übernimmt viele Vorteile von Loop‑Start.

### Asterisk‑Telefoniekanäle einrichten

Um eine Telephonieschnittstellenkarte zu konfigurieren, sind mehrere Schritte erforderlich. In diesem Kapitel zeigen wir drei der häufigsten Szenarien:

- Analoge Verbindung über FXS
- Analoge Verbindung über FXO
- Anschluss eines Astribank™ mit FXS- und FXO-Schnittstellen

### Konfigurationsverfahren (gültig in beiden Fällen)

Bevor Sie Hardware für Asterisk auswählen, sollten Sie die Anzahl gleichzeitiger Anrufe, Dienste und Codecs berücksichtigen, die installiert und aktiviert werden sollen. Asterisk ist eine CPU‑intensive Anwendung, weshalb wir einen dedizierten Rechner für Asterisk empfehlen. Die Anzahl der im Computer installierten Schnittstellenkarten ist durch die verfügbaren Steckplätze und Interrupts begrenzt. Es ist vorzuziehen, eine einzelne Karte mit acht Sprachschnittstellen zu installieren statt zwei Karten mit je vier. Eine weitere Möglichkeit ist die Verwendung einer USB‑Channel‑Bank, wie der Xorcom Astribank. Kürzlich haben einige Hersteller (z. B. CIANET) begonnen, TDMoE‑Channel‑Banks zu produzieren, was das Anschließen von Dutzenden analoger Schnittstellen noch einfacher macht.

![A Xorcom Astribank: ein 19‑Zoll‑Rack‑Mount‑USB‑Kanalbank, die Dutzende von FXS/FXO‑Ports bereitstellt (hier ein 32‑Port‑Modell), ohne PCI‑Slots im Host zu belegen.](../images/10-legacy-fig03.png)

#### Beispiel 1: Eine FXO-, eine FXS-Installation

In diesem Beispiel verwenden wir eine Sangoma TDM400 Telephoniekarten‑Schnittstelle (früher als Digium TDM400 verkauft) mit einem FXS‑ und einem FXO‑Modul. Die erforderlichen Schritte sind unten aufgeführt:

1. Installieren Sie die analoge Karte FXS, FXO oder beide.  
2. Konfigurieren Sie die Datei `/etc/dahdi/system.conf` (früher `/etc/zaptel.conf`).  
3. Generieren Sie die Konfigurationsdateien mit `dahdi_genconf`.  
4. Laden Sie den Treiber für die DAHDI‑Schnittstelle.  
5. Führen Sie `dahdi_test` aus, um Interrupt‑Verluste zu überprüfen.  
6. Führen Sie `dahdi_cfg` aus, um den Treiber zu konfigurieren.  
7. Konfigurieren Sie den DAHDI‑Kanal in der Datei `chan_dahdi.conf`, dann laden Sie Asterisk.

##### Schritt 1: Installieren Sie die TDM400‑Karte

Die TDM404P-Karte enthält FXS- und FXO-Module. Schließen Sie die FXS (S110M, grün) und FXO (X100M, rot) Module an. Wenn Sie FXS-Module verwenden, schließen Sie die Karte direkt an die Stromversorgung über einen Molex‑Stecker an. Bitte tragen Sie elektrostatische Schutzmaßnahmen, bevor Sie Schnittstellenkarten handhaben, um Beschädigungen der Hardware zu vermeiden. Sangoma (früher Digium) Analoggkarten unterstützen ebenfalls ein Hardware‑Echo‑Unterdrückungsmodul VPMADT032.

##### Schritt 2: Generieren Sie die Konfiguration mit dahdi_genconf

Die gute Nachricht bezüglich der Konfiguration ist das neue Dienstprogramm `dahdi_genconf`, das automatisch die Konfiguration für DAHDI‑Schnittstellen erkennt und erzeugt. Das Dienstprogramm erzeugt zwei Dateien:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (mit der `users` Option)
- Alle diese Dateien verwenden die Option `chan_dahdi full`

Bevor Sie `dahdi_genconf` ausführen können, ist es wichtig, die Datei `genconf_parameters` zu konfigurieren (oft als `gen_parameters.conf` bezeichnet):

![Eine Sangoma/Digium TDM404P Analogkarte: Bis zu vier FXS- oder FXO-Module werden in die nummerierten Ports gesteckt, mit optionaler Hardware‑Echo‑Cancel‑Erweiterungskarte und einem dedizierten 12 V‑Stromanschluss für FXS‑Module.](../images/10-legacy-fig04.png)

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

Die `genconf_parameters`‑Datei ermöglicht es Ihnen, Ihre Konfiguration anzupassen. Die wichtigsten Parameter für analoge Leitungen sind:

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

Warning: Es ist erforderlich, dass Sie mindestens den Echo‑Unterdrückungs‑Algorithmus für die Kanäle konfigurieren. Der base_exten‑Parameter definiert den grundlegenden Dialplan für FXS‑Erweiterungen. In diesem Fall erhält der erste FXS‑Kanal die Durchwahlnummer 4000, der zweite 4001 und so weiter. Der Kontext, in dem die Leitungen (context_phones) und Trunks (context_lines) erstellt werden, ist sehr wichtig. Nach dem Erzeugen der Dateien sollten Sie die Datei `/etc/asterisk/dahdi-channels.conf` in die Datei `/etc/asterisk/chan_dahdi.conf` einbinden:

```
#include dahdi-channels.conf
```

Note: Analogsignalisierung ist etwas verwirrend; sie ist immer das Gegenteil der Karte. FXS‑Karten werden mit FXO signalisiert, während FXO‑Karten mit FXS signalisiert werden. Asterisk spricht mit diesen Geräten, als befände es sich auf der gegenüberliegenden Seite.

##### Schritt 3: Kernel‑Treiber laden

Jetzt müssen Sie das chan_dahdi‑Modul und den zugehörigen Karten‑Kernel‑Treiber laden. Verwenden Sie dahdi_hardware, um Ihre Karte und den Treibernamen zu ermitteln. Zum Beispiel:

| Karte | Treiber | Beschreibung |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 – 3,3 V PCI |
| TE405P | wct4xxp | 4xE1/T1 – 5 V PCI |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Befehle zum Laden der Treiber:

```
modprobe dahdi
modprobe wctdm
```

##### Schritt 4: Verwenden Sie das dahdi_test-Dienstprogramm

Ein wichtiges Dienstprogramm ist dahdi_test, das verwendet wird, um Interrupt‑Verluste in der DAHDI‑Karte zu überprüfen. Audioqualitätsprobleme hängen oft mit Interrupt‑Konflikten zusammen. Um zu überprüfen, dass Ihre DAHDI‑Karte keinen Interrupt mit anderen Karten teilt, verwenden Sie den folgenden Befehl:

```
#cat /proc/interrupts
```

Sie können die Anzahl der Interrupt‑Verluste mit dem mit den DAHDI‑Karten kompilierten **dahdi_test**‑Dienstprogramm überprüfen. Ein Wert unter 99,987 % weist auf mögliche Probleme hin.

##### Schritt 5: Das **dahdi_cfg**‑Dienstprogramm zum Konfigurieren des Treibers verwenden

DAHDI verfügt über ein ungewöhnliches System zum Laden der Treiber. Zuerst konfigurieren Sie die **/etc/dahdi/system.conf** und wenden dann diese Konfigurationen mit **dahdi_cfg** auf den DAHDI‑Treiber an. In diesem Fall wird **dahdi_cfg** verwendet, um die Signalisierung für die FX‑Schnittstellen zu konfigurieren. Um die Ergebnisse zu sehen, können Sie dem Befehl „-vvvvv“ hinzufügen, um eine ausführliche Ausgabe zu erhalten.

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

Wenn die Kanäle erfolgreich geladen wurden, sehen Sie eine Ausgabe, die der oben gezeigten ähnelt. Benutzer konfigurieren chan_dahdi.conf häufig falsch, indem sie das Signaling zwischen den Kanälen vertauschen. Wenn das passiert, sehen Sie eine Meldung wie die unten gezeigte:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

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

Mehrere Optionen sind in der Datei chan_dahdi.conf verfügbar. Eine Beschreibung aller Optionen wäre langweilig und kontraproduktiv; stattdessen konzentrieren wir uns auf die wichtigsten Optionsgruppen für ein leichtes Verständnis.

#### Allgemeine Optionen (kanalunabhängig)

Diese Optionen gelten für jeden Kanal: context: Definiert den eingehenden Kontext.

```
context=default
```

channel: Definiert einen Kanal oder einen Kanalbereich. Jede Kanaldefinition erbt Optionen, die vor der Deklaration definiert wurden. Kanäle können einzeln oder in derselben Zeile durch Kommatrennung identifiziert werden. Bereiche können mit „-“ definiert werden.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Erlaubt es, Kanäle als Gruppe zu behandeln. Wenn Sie eine Gruppennummer anstelle einer Kanalnummer wählen, wird der zuerst verfügbare Kanal verwendet. Wenn die Kanäle Telefone sind, klingeln bei einem Anruf an eine Gruppe alle Telefone gleichzeitig. Mit Kommas können Sie mehr als eine Gruppe für denselben Kanal angeben.

```
group=1
group=3,5
```

language: Schaltet die Internationalisierung ein und konfiguriert eine Sprache. Diese Funktion konfiguriert Systemmeldungen für eine bestimmte Sprache. Englisch ist die einzige Sprache, für die vollständige Eingabeaufforderungen über die Standardinstallation verfügbar. musiconhold: Wählt die Musik‑warteschleife‑Klasse.

#### Caller ID options

Es gibt viele Caller‑ID‑Optionen. Einige können deaktiviert werden, obwohl die meisten standardmäßig aktiviert sind. usecallerid: Aktiviert oder deaktiviert die Übertragung der Caller‑ID für die nachfolgenden Kanäle (Yes/No). Hinweis: Wenn Ihr System zwei Klingeltöne vor dem Annehmen erhält, versuchen Sie, diese Funktion zu deaktivieren. Es sollte sofort beantworten. hidecallerid: Legt fest, ob die ausgehende Caller‑ID verborgen werden soll (Yes/No). callerid: Konfiguriert einen Caller‑ID‑String für einen bestimmten Kanal. Der Anrufer kann mit asreceived konfiguriert werden. Dies wird hauptsächlich in Trunk‑Schnittstellen verwendet, um die eingehende Caller‑ID anzuzeigen.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Unterstützt CallerID während Call Waiting. useincomingcalleridondahditransfer: Verwendet die eingehende CallerID bei einer Weiterleitung.

#### Call Waiting

Asterisk unterstützt Call Waiting in FXS‑Kanälen. Der Benutzer erhält einen Warnton, wenn jemand die Nebenstelle wählt. Um Call Waiting zu aktivieren:

```
callwaiting=yes
```

Um Anrufer-ID in Anklopfen zu unterstützen:

```
callwaitingcallerid=yes
```

#### Audio quality options

Die Einstellung der Echounterdrückung ist halb technisch, halb Kunst. Diese Optionen passen bestimmte Asterisk‑Parameter an, die die Audioqualität in den DAHDI‑Kanälen beeinflussen. Sie können helfen, die Audioqualität bei analogen Schnittstellen zu verbessern.

#### The fxotune utility

Das fxotune ist ein Dienstprogramm, das verwendet wird, um bestimmte Parameter für FXO‑Module fein abzustimmen. Diese Feinabstimmung ist erforderlich, um Impedanzfehlanpassungen, die durch den Hybrid verursacht werden, zu korrigieren. Das Dienstprogramm verfügt über drei Betriebsmodi:

- Detection (-i): erkennt und repariert die bestehenden FXO‑Kanäle und speichert die Konfiguration zu

```
fxotune.conf
```

- Dump mode (-d): erzeugt die Waveform‑Dateien nach fxotune_dump.vals
- Startup mode (-s): liest die Datei fxotune.conf und wendet sie auf die FXO‑Module an

Es ist wichtig zu verstehen, dass Sie die Anweisung fxotune –s in den System‑Load einfügen müssen, bevor Sie Asterisk starten:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Echo cancellation

Die meisten Echo‑Unterdrückungs‑Algorithmen arbeiten, indem sie mehrere Kopien des empfangenen Signals erzeugen, von denen jede um einen bestimmten Zeitraum verzögert ist. Die Anzahl der Taps des Filters bestimmt die Größe der Echoverzögerung, die aufgehoben werden muss. Diese verzögerten Kopien werden dann angepasst und vom empfangenen Signal subtrahiert. Der Trick besteht darin, nur das verzögerte Signal anzupassen, um das Echo zu entfernen, ohne zu viele CPU‑Zyklen zu verbrauchen. Aus Sicht der Benutzer ist es wichtig, einen geeigneten Echo‑Unterdrückungs‑Algorithmus zu wählen. Der Standard ist MG2; es stehen jedoch zwei weitere Optionen zur Verfügung: die High Performance Echo Cancellation (HPEC) von Sangoma (früher Digium) und die Open‑Source‑Echo‑Unterdrückung (OSLEC), entwickelt von David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) wurde in den Linux‑Kernel integriert – sie befindet sich im `drivers/staging/echo`‑Bereich des Kernels – und DAHDI wird dagegen gebaut, anstatt einen separaten Download bereitzustellen. Um den Echo‑Unterdrückungs‑Algorithmus zu ändern, setzen Sie den `echo_can`‑Parameter in `/etc/dahdi/system.conf`. Zum Beispiel:

```
echo_can=oslec
```

Die Echounterdrückung in Asterisk wird durch drei Parameter in der Datei /etc/asterisk/chan- gesteuert.

```
dahdi.conf.
```

- **echocancel**: Deaktiviert oder aktiviert die Echo‑Unterdrückung. Sie sollten diese Funktion aktiviert lassen. Sie akzeptiert „yes“ oder die Anzahl der Taps. (Explanation: How does echo canceling work? Most echo canceling algorithms operate by generating multiple copies of a received signal, with each being delayed by a small interval. This little flow is called a "tap". The number of taps determines the echo delay that can be cancelled. These copies are delayed, adjusted, and subtracted from the original signal. The trick is to adjust the delayed signal exactly to what is necessary to remove the echo.)
- **echocancelwhenbridged**: Aktiviert oder deaktiviert den Echo‑Canceller während eines reinen TDM‑Anrufs. Dies ist normalerweise nicht nötig.
- **rxgain**: Passt die Audio‑Empfangsverstärkung an, um die Empfangslautstärke zu erhöhen oder zu verringern (-100 % bis 100 %).
- **txgain**: Passt die Audio‑Sendeverstärkung an, um die Sendelautstärke zu erhöhen oder zu verringern (-100 % bis 100 %).

For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Abrechnungsoptionen

Diese Optionen ändern, wie Anrufinformationen in der Call Detail Records (CDR)-Datenbank aufgezeichnet werden. amaflags: Konfiguriert die AMA‑Flags, die die CDR‑Kategorisierung beeinflussen. Sie akzeptiert die folgenden Werte:

- billing
- documentation
- omit
- default

accountcode: Konfiguriert einen Account‑Code für einen bestimmten Kanal. Er kann jeden alphanumerischen Wert enthalten – meist die Abteilung oder den Benutzernamen.

```
accountcode=finance
amaflags=billing
```

### Optionen zum Anruffortschritt

Diese Elemente werden verwendet, um Informationen über den Fortschritt des Anrufs zu erhalten. In öffentlichen Schnittstellen kann es nützlich sein, den Anruffortschritt zu erkennen und zu bestimmen, ob er beantwortet oder besetzt war. Die Besetzt‑Erkennung ist stark experimentell und wird durch spezifische Parameter geregelt.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

These parameters (above) specify whether the interface will try to detect the busy tone, how many tones will be used for successful detection, and what is the busy pattern. The busy detection is largely experimental, and some additional parameters can be changed in the Makefile. To detect the answer of a call, which is essential for precise billing, it is possible to use the polarity reversal to signal the exact answer time. This is important if you plan to charge for the call or just wish to have precise billing for comparison. Usually you have to contact the phone company to request this service.

```
answeronpolarityswitch=yes
```

In einigen Ländern ist es möglich, das Auflegen des Anrufs mittels Polaritätsumkehr zu erkennen.

```
hanguponpolarityswitch=yes
```

#### Optionen für Telefone

Diese Optionen werden für Telefone verwendet, die an die FXS‑Schnittstellen angeschlossen sind. Alle Funktionen, die analogen Telefonen, die direkt an die DAHDI‑Schnittstellen angeschlossen sind, bereitgestellt werden, werden von Asterisk gesteuert.

- **adsi** (Analog Display Services Interface): Dies ist ein Satz von Telekom‑Standards, die von einigen Telekommunikationsanbietern verwendet werden, um Dienste wie Ticketkauf anzubieten.
- **cancallforward**: Aktiviert oder deaktiviert Anrufweiterleitung (*72 zum Aktivieren und *73 zum Deaktivieren).
- **calleridcallwaiting**: Aktiviert die Anzeige der Caller‑ID während einer Anklopfung (Ja/Nein).
- **immediate**: Im Sofort‑Modus springt der Kanal anstatt einen Wähltton zu geben sofort zur „s“-Erweiterung im definierten Kontext. Dies wird verwendet, um Hotlines zu erstellen.
- **threewaycalling**: Aktiviert oder deaktiviert Dreierkonferenzen.
- **mailbox**: Warnt den Benutzer über verfügbare Voicemail‑Nachrichten. Es kann ein akustisches Signal oder ein visueller Hinweis sein (wenn das Telefon diese Funktion unterstützt). Das Argument ist die Mailbox‑Nummer.
- **callgroup**: Gruppiert Telefone zum Wählen oder Aufnehmen.
- **pickupgroup**: Gruppe von Telefonen für das Aufheben von Anrufen.

### Nützliche DAHDI‑CLI‑Befehle

Sobald Asterisk läuft und die DAHDI‑Kanäle geladen sind, können Sie den Kanalstatus über die Asterisk‑CLI inspizieren. Diese Befehle gelten weiterhin in Asterisk 22.

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI-Kanalformat

DAHDI‑Kanäle verwenden im Dialplan das folgende Format:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Zum Beispiel:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Digitale Kanäle (E1/T1/PRI / TDM)

Ab Asterisk 22 werden DAHDI und libpri weiterhin vollständig unterstützt, aber TDM‑digitale Trunks (E1/T1/ISDN PRI) werden in neuen Installationen zunehmend durch SIP‑Trunks ersetzt. Dieser Abschnitt bleibt voll anwendbar, wo TDM‑Konnektivität erforderlich ist; in Greenfield‑Umgebungen liefert SIP‑Trunking (Chapter 3) in der Regel dieselbe Kanaldichte ohne Telefonie‑Hardware.

Digitale Kanäle sind äußerst verbreitet, daher müssen Sie lernen, wie man diese Kanäle implementiert, wenn Sie sich auf große Kunden konzentrieren wollen. Wenn die Anzahl der Kanäle hoch ist — in der Regel mehr als 8 — ist es ziemlich üblich, digitale Schnittstellen wie T1/E1/J1 zu verwenden. T1 ist in den USA sehr verbreitet, während E1 in Europa und J1 in Japan üblich ist. Diese Arten von Kanälen ermöglichen eine gute Dichte von Leitungen — 24 pro T1‑Kanal und 30 für E1‑Kanäle.

In Lateinamerika, China und Afrika ist es üblich, eine Art kanalgebundene Signalisierung (CAS) namens MFC/R2 zu verwenden. Dieses Kapitel untersucht, wie MFC/R2 mit der Bibliothek OpenR2 implementiert wird. In den USA und Europa ist Integrated Services Digital Networks (ISDN) PRI die gebräuchlichste Signalisierung. Das Kapitel behandelt außerdem ISDN Basic Rate Interface (BRI), das in Europa bei mittelgroßen Anwendungen sehr verbreitet ist.

Alle Beispiele im Buch konzentrieren sich auf DAHDI‑Kanäle. Einige Karten werden mit proprietären Kanälen implementiert, daher prüfen Sie bitte beim Hersteller weitere Details zur Konfiguration Ihrer spezifischen Karte.

### Ziele

Am Ende dieses Kapitels werden Sie in der Lage sein:

- Erkennen Sie die in der digitalen Telefonie verwendeten Hauptbegriffe
- Unterscheiden Sie CAS- und CCS-Signalisierung
- Unterscheiden Sie R2- und ISDN-Signalisierung
- Konfigurieren Sie Schnittstellen mit ISDN-Signalisierung
- Konfigurieren Sie Schnittstellen mit R2-Signalisierung

### E1/T1-Digitalleitungen

Digitale Leitungen E1/T1 sind eine Option, wenn Sie eine große Anzahl von Kanälen bereitstellen müssen. Ein einzelner E1‑Kreis kann 30 gleichzeitige Anrufe bewältigen, und Sie können Funktionen wie Direct Inward Dial (DID), Caller ID (Anruferidentifikation) und erweitertes Signalling nutzen. Die E1/T1‑Leitung kann je nach Land Ihres Unternehmens auf verschiedene Weise über Twisted‑Pair, Glasfaser und Mikrowellen bereitgestellt werden. Digitale Leitungen werden Ihrem Unternehmen über UTP, Glasfaser oder Mikrowellen zugeführt. Modems und Multiplexoren (MUX) werden verwendet, um die physische Leitung zu übertragen. Der Anschluss an eine T1‑Leitung erfolgt stets über einen RJ45‑Stecker. E1‑Leitungen können jedoch ebenfalls über BNC bereitgestellt werden. Es ist sehr wichtig, den Steckertyp, den Sie im Voraus erhalten werden, zu kennen, insbesondere bei E1‑Leitungen. In der Regel wird die gesamte Ausrüstung bis zum RJ45‑Stecker vom TELCO bereitgestellt.

![Wie E1/T1‑Leitungen bereitgestellt werden: Der Betreiber kann den Trunk über UTP‑Kupfer (HDSL‑Modem für E1 oder eine direkte Kartenverbindung für T1), über Glasfaser durch einen optischen Multiplexer oder über eine Mikrowellenfunkverbindung bereitstellen.](../images/10-legacy-fig05.png)

![UTP oder BNC? Die meisten digitalen Karten verwenden RJ45 (UTP)-Stecker, aber einige E1-Leitungen werden über duale BNC‑Koaxialkabel bereitgestellt; in diesem Fall wird ein Balun benötigt, um das Koaxialpaar an die RJ45‑Buchse der Karte anzupassen.](../images/10-legacy-fig06.png)

#### Wie wird die Stimme in Bits umgewandelt?

Das analoge Signal wird 8.000 Mal pro Sekunde abgetastet, um eine digitale Version der analogen Stimme zu erzeugen. Diese Kodierung ist als Puls‑Code‑Modulation (PCM) bekannt. In den USA und Japan wird das Signal mit law kodiert (in Asterisk als ulaw bezeichnet). Im Rest der Welt wird die Kodierung alaw verwendet.

![Pulse code modulation (PCM): das 4 kHz‑analoge Sprachsignal wird 8.000‑mal pro Sekunde (Nyquist) abgetastet und in einen 64 Kbps‑digitalen Bitstrom codiert.](../images/10-legacy-fig07.png)

#### Zeitmultiplexverfahren

Analog lines make sense when you need just a few channels. When using time division multiplexing (TDM), it is possible to stuff multiple channels into a single data connection. When you want a large number of circuits, the phone company will usually provide you with a digital trunk, which is a data circuit in which the voice is transported in a digital format using PCM. Each timeslot uses 64 Kbps of bandwidth to transport a single voice channel.

![Zeitmultiplexverfahren in E1 und T1: Ein E1‑Frame enthält 32 Timeslots mit 2048 Kbps (DS0 #0 für Frame‑Synchronisation, DS0 #16 für Signalisierung), während ein T1‑Frame 24 Timeslots mit 1544 Kbps verwendet, wobei ein Bit für die Synchronisation und ein robbed‑bit‑Verfahren für die Signalisierung genutzt wird.](../images/10-legacy-fig08.png)

In den USA ist der am häufigsten verwendete digitale Trunk T1, der 24 verfügbare Leitungen hat; in Europa und Lateinamerika haben E1‑Trunks 30 Leitungen. Einige Unternehmen bieten ein fraktioniertes T1/E1 mit weniger Kanälen an.  
Robbed‑Bit‑Signalisierung  
Manchmal verwendet ein T1‑Trunk ein Robbed‑Bit‑Schema, bei dem ein Bit für die Signalisierung entliehen wird. Bei T1‑Trunks wird der Daten‑/Sprachkanal mit 56 Kbps auf jedem Timeslot übertragen. Wie Sie beobachten können, verliert der T1‑Kreis bei Verwendung des Robbed‑Bits nicht zwei Slots für Synchronisation und Signalisierung.

#### T1/E1 Leitungscode

T1s und E1s sind eigentlich Datenleitungen und haben eine Datenkodierung, die bestimmt, wie die Bits interpretiert werden. Für E1s ist der am häufigsten verwendete Leitungscode HDB3 für Schicht 1 und CCS für Schicht 2. Der einfachste Weg, um herauszufinden, wie Ihr digitaler Trunk konfiguriert ist, besteht darin, den TELCO danach zu fragen. Sie benötigen diese Information, um die Datei /etc/dahdi/system.conf zu konfigurieren.

#### T1/E1 Signalgebung

Es ist wichtig zu verstehen, dass T1/E1-Leitungen mit unterschiedlichen Signalisierungsarten bereitgestellt werden können, wie zum Beispiel:

- T1 mit robbed bit signaling
- T1 mit ISDN signaling
- E1 mit MFC/R2 (CAS - Channel Associated Signaling)
- E1 mit ISDN signaling

ISDN wird häufig in Europa und den USA verwendet. Es ist ein digitales Sprachnetz, das 1984 von der International Telecommunications Union (ITU) standardisiert wurde. ISDN bietet zwei Arten von Kanälen:

- Trägerkanäle
  - Sprache
  - Daten
- Datenkanäle
  - Out-of-Band-Signalisierung
  - LAPD-Signalisierung
  - Q.931

In der Regel wird eine ISDN-Leitung über zwei physische Mittel bereitgestellt:

- Basic rate interface (BRI)
  - Known as 2B+D → Bekanntermaßen 2B+D
  - Two bearer (64K) channels and a data (16K) channel → Zwei Bearer (64K) Kanäle und ein Daten (16K) Kanal
  - Uses a pair of copper wires with 148Kbps. → Verwendet ein Paar Kupferdrähte mit 148Kbps.
- Primary rate interface (PRI)
  - Delivered using a T1/E1 trunk → Bereitgestellt über einen T1/E1 Trunk
  - 23B+D for T1s → 23B+D für T1s
  - 30B+D for E1s → 30B+D für E1s

Manchmal verwenden E1‑Leitungen ein CAS‑Signalisierungsschema namens MFC/R2, das von der ITU als Standard Q.421/Q441 definiert wurde. Dies ist häufig in Lateinamerika und Asien zu finden. Mehrere Telefonie‑Unternehmen in diesen Ländern nutzen angepasste Varianten von MFC/R2. Daher müssen Sie die korrekte länderspezifische Variante kennen, um es zum Laufen zu bringen.

### ISDN BRI

Channels using ISDN BRI signalling are very popular in Europe. Most ISDN BRI cards for Asterisk supports an S/T interface with NT and TE capabilities. The TE (terminal) connection is the one used to connect to the TELCO or to other PBXs configured as network termination (NT). The NT is used to connect phones and PBXs configured as TE. ISDN BRI provides two data/voice channels and one signalling channel. ISDN BRI cards are available from several vendors of interface cards for Asterisk.

### Auswahl einer Telefoniekarte für Ihren Asterisk-Server

Es gibt mehrere Hersteller für digitale Karten, die mit Asterisk kompatibel sind. Die Auswahl einer Karte hängt von einigen der folgenden Faktoren ab:

#### Datenbus

Es gibt mehrere Arten von Bussen in Ihrem PC. Es ist sehr wichtig, dass Sie die richtige Karte für Ihren Server haben. Die folgende Übersicht gibt einen Überblick über die am häufigsten verwendeten Karten:

- 32 Bits PCI 5 V, gefunden in den meisten Computern, einschließlich Desktop‑Computern
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, und TC400
  - Sangoma A101, A102, und A104
- 32/64 Bits PCI 3.3 V, im Wesentlichen in Servern gefunden
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, und TC400
- PCI Express, auf Desktop‑Computern und Servern gefunden
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, und AEX800
  - Sangoma A101, A102, und A104

Diese Kartenfamilien stammen von Digium, das 2018 von Sangoma übernommen wurde; sie werden jetzt unter der Marke Sangoma verkauft und unterstützt. Viele der hier aufgeführten älteren SKUs wurden eingestellt, daher prüfen Sie die aktuelle Modellverfügbarkeit auf www.sangoma.com, bevor Sie kaufen.

- MiniPCI auf eingebetteten Systemen gefunden
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI) und B400M(ISDN BRI)
- USB 2.0 auf den meisten modernen PCs gefunden. Lösungen auf Basis von USB ermöglichen eine hohe Dichte an analogen und digitalen Kanälen. Dieser Bus unterstützt 480 Mbps, und jeder Sprachkanal belegt 64 Kbps. Beim Einsatz von USB‑Hubs ist es möglich, Dichten von bis zu tausend analogen Ports an einem einzigen Port zu erreichen.
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. Der größte Vorteil von Ethernet besteht darin, dass die Karte von mehr als einem Server aus angeschlossen werden kann. Hochverfügbarkeits‑Lösungen sind für diese Geräte meist die Kernanwendung. Die Stärke dieser Lösung liegt in der Nutzung von Servern ohne freie PCI‑Slots oder Blade‑Servern.
  - Redfone FoneBridge (up to four E1 circuits)

### Verwendung von Hardware‑Echounterdrückung

Hardware-Echounterdrückung reduziert die Belastung der Host‑CPU. Für Karten mit mehr als einer einzelnen E1‑Schnittstelle kann Hardware-Echounterdrückung helfen, Ihren Prozessor zu entlasten. Neue verbesserte Software‑Echounterdrücker wie der OSLEC reduzieren den Bedarf an einem Hardware‑Echounterdrücker. Um zwischen Hardware‑ und Software‑Echounterdrückern zu wählen, sollten Sie die verfügbare Rechenleistung Ihres Servers und die Anzahl der E1‑Strecken berücksichtigen. Ein Echounterdrückungsprozess kann bis zu neun MIPS (millions of instructions per second) pro Sprachkanal mit 128 Taps der Amplitude unter Verwendung von OSLEC (Reference: Xorcom Ltd.) verbrauchen. Wenn Sie 1 CPU‑Zyklus pro jeder Instruktion annehmen (was nicht immer korrekt ist, basierend auf dem Prozessor und der Software‑Implementierung selbst), sprechen wir von 1.080 Ghz für vier E1s.

#### Art der Signalisierung

Die Auswahl des Signalisierungstyps (z. B. T1 CAS, T1 PRI, E1 CAS R2 oder E1 CAS ISDN) ist keine leichte Aufgabe. Sie hängt wirklich davon ab, was in Ihrer Region verfügbar ist und zu welchem Preis. Common Channel Signaling (CCS) ist oft besser als channel associated signaling (CAS). Allerdings ist es häufig nicht verfügbar. In den USA können Sie in der Regel wählen, da die meisten TELCOS T1 CAS für reguläre Nutzer und T1 PRI für fortgeschrittene Nutzer (z. B. Call‑Center) anbieten. In Lateinamerika ist E1 CAS R2 verbreitet, aber ISDN PRI ist in einigen Städten verfügbar.

![Die DAHDI-Softwarearchitektur: Asterisk kommuniziert mit dem `chan_dahdi` Channel‑Treiber, der wiederum die Protokollbibliotheken libpri (ISDN), libopenr2 (MFC/R2) und libss7 (SS7) lädt; diese liegen über der `/dev/dahdi`‑Schnittstelle, dem DAHDI‑Kernel‑Treiber und dem karten­spezifischen Kernel‑Treiber.](../images/10-legacy-fig09.png)

Die Implementierung von R2 ist notwendig, um eine Bibliothek namens OpenR2 (www.libopenr2.org) zu installieren, die von Moises Silva entwickelt wurde, und um Asterisk vor der Installation zu patchen – ein einfacher Vorgang, der später in diesem Kapitel gezeigt wird. Die Bibliothek hat mehrere Tests bestanden und ist in der Produktion bei mehreren unserer Kunden im Einsatz. ISDN ist meiner Meinung nach immer die beste Wahl, wenn es verfügbar ist. Einige Anbieter können Zugriff auf das Signalisierungssystem 7 (SS7) haben, das ein CCS‑Signalisierungssystem zwischen Telefonunternehmen ist. Proprietäre und Open‑Source‑Lösungen für SS7 sind verfügbar. Die Bibliothek libss7 wird verwendet, um SS7 in Asterisk zu unterstützen.

### Asterisk‑Telephoniekanäle einrichten

Die Konfiguration einer Telefonie‑Schnittstellenkarte erfordert mehrere notwendige Schritte. In diesem Kapitel zeigen wir drei der häufigsten Szenarien:

- Digitale Verbindung über ISDN PRI
- Digitale Verbindung über ISDN BRI
- Digitale Verbindung über MFC/R2

Es gibt zwei Möglichkeiten, DAHDI‑Kanäle zu konfigurieren. Die erste besteht darin, sie manuell mit voller Kontrolle aller Parameter zu konfigurieren. Die zweite Möglichkeit ist die Verwendung des Dienstprogramms dahdi_genconf, um die Karten zu erkennen und zu konfigurieren.

#### Automatische Erkennung und Konfiguration

Dank dem DAHDI-Entwicklungsteam haben wir jetzt die automatische Erkennung und Konfiguration der Karten. Schritt 1: Um die Konfiguration automatisch zu erzeugen, verwenden Sie das Dienstprogramm dahdi_genconf, das die Karte erkennt und die Dateien /etc/dahdi/system.conf und dahdi-channels.conf erzeugt.

```
dahdi_genconf
```

Step 2: In der letzten Zeile der Datei chan_dahdi.conf, include die Datei dahdi-channels.conf

```
#include dahdi_channels.conf
```

Schritt 3: Kommentieren Sie alle nicht verwendeten Module in der Datei modules oder verwenden Sie einfach:

```
dahdi_genconf modules
```

#### Manuelle Konfiguration

Eine weitere Möglichkeit besteht darin, die Schnittstellen manuell zu konfigurieren. Nachfolgend einige Beispiele für die Konfiguration von DAHDI‑Kanälen.

##### Beispiel #1 – Zwei T1/ E1‑Kanäle mit ISDN

Erforderliche Schritte:

1. TE205P‑ oder TE210P‑Installation
2. `/etc/dahdi/system.conf`‑Dateikonfiguration
3. DAHDI‑Treiber‑Laden
4. `dahdi_test`‑Dienstprogramm
5. `dahdi_cfg`‑Dienstprogramm
6. `chan_dahdi.conf`‑Dateikonfiguration
7. Asterisk‑Laden und Testen

Schritt 1: TE205P‑Installation. Vor der Installation von TE205P ist es wichtig, die Unterschiede zwischen den Karten TE205P und TE210P zu verstehen. Die TE210P‑Karte verwendet einen 64‑Bit‑Bus, der mit 3,3 V betrieben wird und fast ausschließlich in Server‑Motherboards zu finden ist. Seien Sie vorsichtig, wenn Sie diese Schnittstellenkarte angeben; stellen Sie sicher, dass Ihre Hardware einen 64‑Bit‑, 3,3 V‑Bus unterstützt. Die TE205P‑Karte verwendet ein 5 V‑PCI, das häufig in Desktop‑Computern zu finden ist. Für dieses Beispiel haben wir die TE205P‑Schnittstellenkarte mit zwei Spans gewählt, weil sie sich leichter zu einer Ein‑Span‑Karte reduzieren oder zu einer Vier‑Span‑Karte erweitern lässt. Diese Karten werden jetzt unter der Marke Sangoma (früher Digium) verkauft.

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

Die Konfiguration von TDM‑Digital‑Karten unterscheidet sich etwas von der Konfiguration ihrer analogen Gegenstücke. Zuerst müssen wir die Board‑Spans konfigurieren und dann die Kanäle. Spans werden sequenziell nummeriert, abhängig von der Erkennungsreihenfolge der Karten. Mit anderen Worten, wenn Sie mehr als eine Schnittstellenkarte haben, ist es schwer zu wissen, zu welchem Span jede gehört. Verwenden Sie dahdi_hardware, um zu prüfen, welche Hardware auf jedem Span installiert ist. Beispiel #1 (2xT1 PRI)

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

Step 3: Laden von Kernel‑Treibern Prüfen Sie, welchen Treiber Sie mit dahdi_hardware installieren müssen.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Zum Laden verwenden:

```
modprobe dahdi
modprobe wct2xxp
```

Schritt 4: Mit dahdi_test die fehlenden Interrupts prüfen  
Sie können die Anzahl der fehlgeschlagenen Interrupts mit dem dahdi_test‑Dienstprogramm überprüfen, das für die DAHDI‑Karten kompiliert wurde. Eine Zahl unter 99,987 % weist auf mögliche Probleme hin. Sie finden dahdi_test in

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

Step 5: Using the dahdi_cfg utility  
This is the correct output for dahdi_cfg for one fractional E1 (15 ports) span and two FXO ports.

```
#./dahdi_cfg -vvvv
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

Schritt 6: Konfiguration von DAHDI in die Datei /etc/asterisk/chan_dahdi.conf Beispiel #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
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
callerid="Flavio Eduardo" <4830258580>
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

Use signaling=bri_cpe_ptmp for point to multipoint BRI. Currently, BRI point to multipoint is not supported in NT mode.

#### Laden der Kernel‑Treiber

After configuring the drivers, you may simply restart the server. If you have installed DAHDI with make config, you won’t need to do anything extra. The kernel driver will be automatically loaded and configured. However, sometimes it is useful to load and unload the drivers manually. Example:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

Der erste Befehl lädt den Treiber und der zweite, dahdi_cfg, wendet die Konfiguration auf den Kernel‑Treiber an.

### Fehlerbehebung

Manchmal funktioniert etwas beim ersten Mal nicht. Lassen Sie uns einige Ressourcen zur Fehlerbehebung von DAHDI prüfen. Schritt 1: Überprüfen Sie, ob die Karte vom Betriebssystem erkannt wird. Sangoma/Digium‑Karten werden normalerweise als ISDN‑Modem erkannt.

```
lspci -v
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

Schritt 2: Überprüfen Sie, ob der Kernel‑Treiber korrekt geladen wird, mit:

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

Step 3: Überprüfen Sie den Status von Alarmen, die die physische Schicht der Verbindung betreffen. Um die physische Schicht der E1‑Verbindung zu überprüfen, können Sie den folgenden Asterisk CLI‑Befehl verwenden.

```
dahdi show status
```

Die Alarme zeigen Probleme mit dem Port an: Roter Alarm: Kann die Synchronisation mit dem entfernten Switch nicht aufrechterhalten. Dies ist normalerweise ein physikalisches Problem, wie Leitungsfehler oder Rahmenfehlanpassung. Gelber Alarm: Signalisiert, dass der entfernte Switch im roten Alarm ist. Das bedeutet, dass der entfernte Switch Ihre Übertragungen nicht empfängt. Blauer Alarm: Empfängt alle ungerahmten 1en auf allen Timeslots; dahdi_tool erkennt derzeit keinen blauen Alarm. Loopback: Der Port befindet sich entweder im lokalen oder entfernten Loopback

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Schritt 4: Um Probleme mit DAHDI auf dem Asterisk‑Server zu erkennen, prüfen Sie zunächst, ob die Kanäle erkannt werden, indem Sie verwenden:

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

Step 5: Überprüfen Sie den Status der ISDN‑Schicht 3, auch bekannt als q.931. Sie können prüfen, ob die ISDN‑Schicht 3 aktiv ist, indem Sie verwenden: `pri show spans` (um alle Spans aufzulisten) oder `pri show span <n>` für einen bestimmten Span:

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

Verwenden Sie `pri show spans` (Plural), um den Status aller konfigurierten PRI‑Spannen auf einmal aufzulisten.

Überprüfen Sie einen bestimmten Kanal. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
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

debug pri span x: Wenn Sie nach allem noch Probleme haben, starten Sie das Debugging des pri span. Dieser Befehl ermöglicht ein detailliertes Debugging von ISDN-Anrufen. Er ist ein wichtiger Befehl, wenn Sie denken, dass etwas nicht korrekt ist. Sie können falsch gewählte Ziffern und andere Probleme erkennen. Im Folgenden präsentieren wir ein Beispiel einer Debugging‑Ausgabe für einen erfolgreichen Anruf. Beziehen Sie sich auf dieses Beispiel, wenn Sie einen fehlgeschlagenen Anruf mit einem problemlosen vergleichen müssen. Ein Hinweis ist, core set verbose=0 zu verwenden, um nur die ISDN q.931‑Nachrichten zu erhalten.

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
> [a1]
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

Mehrere Optionen sind in der Datei chan_dahdi.conf verfügbar. Eine Beschreibung aller Optionen wäre langweilig und kontraproduktiv. Hier werden die wichtigsten Optionsgruppen detailliert dargestellt, um ein besseres Verständnis zu ermöglichen.

#### Allgemeine Optionen (kanalunabhängig)

context: Definiert den eingehenden Kontext.

```
context=default
```

channel: Definiert Kanal oder Kanalbereich. Jede Kanaldefinition erbt Optionen, die vor der Deklaration definiert wurden. Kanäle können einzeln oder in derselben Zeile durch Komma getrennt identifiziert werden. Bereiche können mit “-” definiert werden.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Erlaubt es, Kanäle als Gruppe zu behandeln. Wenn Sie anstelle einer Kanalnummer eine Gruppennummer wählen, wird der zuerst verfügbare Kanal verwendet. Sind die Kanäle Telefone, klingeln bei einem Anruf an die Gruppe alle Telefone gleichzeitig. Mit Kommas können Sie mehr als eine Gruppe für denselben Kanal angeben.

```
group=1
group=3,5
```

language: Schaltet die Internationalisierung ein und konfiguriert eine Sprache. Diese Funktion richtet Systemmeldungen für eine bestimmte Sprache ein. Englisch ist die einzige Sprache, für die vollständige Eingabeaufforderungen in der Standardinstallation verfügbar. musiconhold: Wählt die Music‑on‑Hold‑Klasse.

#### ISDN‑Optionen

switchtype: Hängt vom verwendeten PBX oder Switch ab. In Europa und Lateinamerika ist EuroISDN üblich.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Erforderlich für einige Switches, die eine Dialplan‑Spezifikation benötigen. Diese Option wird von vielen Switches ignoriert. Die gültigen Optionen sind private, national, international und unknown.

```
pridialplan = unknown
```

prilocaldialplan: Notwendig für einige Switches, normalerweise unbekannt.

```
prilocaldialplan = unknown
```

overlapdial: Overlap‑Wählen wird verwendet, wenn Sie nach dem Herstellen der Verbindung Ziffern übermitteln. Sie können Block‑Modus‑Nummerierung (overlapdial=no) oder Ziffern‑Modus (overlapdial=yes) verwenden. Der Block‑Modus wird häufig von Operatoren eingesetzt.  
signaling: Konfiguriert den Signalisierungstyp für die nachfolgenden Kanäle. Diese Parameter sollten denjenigen in der Datei chan_dahdi.conf entsprechen. Die richtige Auswahl hängt vom verfügbaren Kanal ab. Für ISDN könnten Sie fünf Optionen wählen:

- pri_cpe: Wird verwendet, wenn das Gerät ein CPE ist, manchmal auch Client, User oder Slave genannt. Dies ist die einfachste und am häufigsten genutzte Form der Signalisierung. Manchmal, wenn Sie sich mit einer privaten PBX verbinden, ist die PBX ebenfalls häufig als CPE konfiguriert. In diesem Fall verwenden Sie pri_net‑Signalisierung in Asterisk.  
- pri_net: Wird verwendet, wenn Asterisk mit einer privaten PBX verbunden ist, die als CPE konfiguriert ist. Die Signalisierung wird oft als Host, Master oder Network bezeichnet.  
- bri_cpe: Wird verwendet, wenn Asterisk als CPE an einen ISDN‑BRI‑Trunk angeschlossen ist  
- bri_net: Wird verwendet, wenn Asterisk an ein ISDN‑Telefon oder eine PBX angeschlossen ist, die als Terminal (TE) konfiguriert ist.  
- bri_cpe_ptmp: Gleich wie bri_cpe, jedoch in einer Point‑to‑Multipoint‑Architektur.  

#### CallerID‑Optionen

Es stehen viele Caller‑ID‑Optionen zur Verfügung. Einige können deaktiviert werden, obwohl die meisten standardmäßig aktiviert sind.  
usecallerid: Aktiviert oder deaktiviert die Übertragung der Caller‑ID für die nachfolgenden Kanäle (Yes/No). Hinweis: Wenn Ihr System zwei Klingeltöne vor dem Annehmen verlangt, versuchen Sie, diese Funktion zu deaktivieren, damit sofort angenommen wird.  
hidecallerid: Verbirgt die Caller‑ID (Yes/No).  
calleridcallwaiting: Aktiviert das Empfangen der Caller‑ID während einer Anklopfung (Yes/No).  
callerid: Konfiguriert einen Caller‑ID‑String für einen bestimmten Kanal. Der Anrufer kann mit „asreceived“ in Trunk‑Schnittstellen konfiguriert werden, um die Caller‑ID weiterzuleiten.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Hinweis: Die meisten TELCOs verlangen, dass Sie Ihre korrekte Caller‑ID konfigurieren. Wenn Sie die richtige Caller‑ID nicht übergeben, sollten Sie nicht über das TELCO herausrufen können. Andererseits können Sie Anrufe empfangen, selbst wenn die Caller‑ID nicht konfiguriert ist.

#### Audio‑Qualitätsoptionen

Diese Optionen passen bestimmte Asterisk‑Parameter an, die die Audio‑Qualität in DAHDI‑Kanälen beeinflussen.

- **echocancel**: Deaktivieren oder aktivieren Sie die Echounterdrückung. Sie sollten diese Funktion aktiviert lassen. Sie akzeptiert „yes“ oder die Anzahl der Taps. (Erklärung: Wie funktioniert die Echounterdrückung? Die meisten Echounterdrückungs‑Algorithmen arbeiten, indem sie mehrere Kopien eines empfangenen Signals erzeugen, wobei jede um ein kleines Intervall verzögert wird. Dieser kleine Fluss wird „Tap“ genannt. Die Anzahl der Taps bestimmt die Echoverzögerung, die aufgehoben werden kann. Diese Kopien werden verzögert, angepasst und vom Originalsignal subtrahiert. Der Trick besteht darin, das verzögerte Signal exakt so anzupassen, dass das Echo entfernt wird.)
- **echocancelwhenbridged**: Aktiviert oder deaktiviert den Echo‑Canceller während eines reinen TDM‑Anrufs. Dies ist normalerweise nicht erforderlich.
- **rxgain**: Passt die Empfangs‑Gain des Audios an, um die Empfangslautstärke zu erhöhen oder zu verringern (‑100 % bis 100 %).
- **txgain**: Passt die Sendungs‑Gain des Audios an, um die Sendelautstärke zu erhöhen oder zu verringern (‑100 % bis 100 %).

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Abrechnungsoptionen

Diese Optionen ändern die Art und Weise, wie Anrufinformationen in der Call‑Detail‑Records (CDR)‑Datenbank gespeichert werden. amaflags: Beeinflusst die Kategorisierung von CDR. Es akzeptiert diese Werte:

- billing
- documentation
- omit
- default

accountcode: Es konfiguriert einen Account‑Code für einen bestimmten Kanal. Er kann jeden alphanumerischen Wert enthalten, üblicherweise die Abteilung oder den Benutzernamen.

```
accountcode=finance
amaflags=billing
```

### MFC/R2-Konfiguration

MFC/R2 wird in mehreren Ländern Lateinamerikas, Chinas und Afrikas sowie in einigen europäischen Ländern eingesetzt. ISDN ist überlegen und wird bevorzugt, wenn es in Ihrer Region verfügbar ist.

#### Verstehen des Problems

Die Karte, die zur Signalisierung von MFC/R2 verwendet wird, ist dieselbe, die zur Signalisierung von ISDN verwendet wird. Es ist möglich, MFC/R2 auf DAHDI‑Kanälen mit der Bibliothek namens libopenR2 (www.libopenr2.com) zu verwenden. Diese Bibliothek war in Versionen von Asterisk vor 1.6.2 nicht enthalten.

##### Verstehen des MFC/R2-Protokolls

Das MFC/R2‑Protokoll kombiniert In‑Band‑ und Out‑Of‑Band‑Signalisierung. Die Adresssignalisierung wird In‑Band mittels einer Reihe von Tönen weitergeleitet, während Kanalinformationen über Timeslot 16 als Out‑Of‑Band‑Signalisierung übertragen werden.

**Line Signaling (ITU-T Q.421).** In Zeitschlitz 16 verwendet jeder Sprachkanal vier ABCD‑Bits, um seine Zustände und die Anrufsteuerung zu signalisieren. Die Bits C und D werden selten genutzt. In einigen Ländern können sie für die Messung (Impulszählung zur Abrechnung) verwendet werden. In einem normalen Gespräch arbeiten beide Seiten: der Anrufer und die angerufene Seite. Die Signalisierung von der Anruferseite wird als Vorwärts‑Signalisierung bezeichnet, während die angerufene Seite Rückwärts‑Signalisierung verwendet. Wir bezeichnen Vorwärts‑Signalisierung mit Af und Bf und Rückwärts‑Signalisierung mit Ab und Bb.

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 wurde von der ITU definiert. Leider haben mehrere Länder den Standard an ihre eigenen Bedürfnisse angepasst. Infolgedessen entstanden zwischen den Ländern unterschiedliche Varianten des Standards.

**Inter-Register-Signale (ITU-T Q.441).** MFC/R2-Signalisierung verwendet eine Kombination aus zwei Tönen. Die nachstehenden Tabellen zeigen den ITU-Standard.

Signalgruppe I (vorwärts):

| Description | Forward signal |
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
| Länderkennzeichen, ausgehender Halb-Echo-Unterdrücker erforderlich | I-11 |
| Länderkennzeichen, kein Echo-Unterdrücker erforderlich | I-12 |
| Testanruf-Indikator | I-13 |
| Länderkennzeichen, ausgehender Halb-Echo-Unterdrücker eingesetzt | I-14 |
| Nicht verwendet | I-15 |

Signalgruppe II (vorwärts):

| Description | Forward signal |
| --- | --- |
| Teilnehmer ohne Priorität | II-1 |
| Teilnehmer mit Priorität | II-2 |
| Wartungsgerät | II-3 |
| Reserve | II-4 |
| Operator | II-5 |
| Datenübertragung | II-6 |
| Teilnehmer oder Operator ohne Weiterleitungsfunktion | II-7 |
| Datenübertragung | II-8 |
| Teilnehmer mit Priorität | II-9 |
| Operator mit Weiterleitungsfunktion | II-10 |
| Reserve | II-11 |
| Reserve | II-12 |
| Reserve | II-13 |
| Reserve | II-14 |
| Reserve | II-15 |

Signalgruppe A (rückwärts):

| Description | Backward signal |
| --- | --- |
| Sende nächste Ziffer (n+1) | A-1 |
| Sende vorletzte Ziffer (n-1) | A-2 |
| Adresse vollständig, Umschaltung zum Empfang von Group B Signalen | A-3 |
| Stau im nationalen Netzwerk | A-4 |
| Sende Kategorie des Anrufers | A-5 |
| Adresse vollständig, abrechnen, Sprachbedingungen einrichten | A-6 |
| Sende drittletzte Ziffer (n-2) | A-7 |
| Sende viertletzte Ziffer (n-3) | A-8 |
| Reserve | A-9 |
| Reserve | A-10 |
| Sende Länderkennzeichen-Indikator | A-11 |
| Sende Sprach‑ oder Diskriminierungsziffer | A-12 |
| Sende Art des Leitungs | A-13 |
| Fordere Information zur Nutzung des Echo‑Suppressors an | A-14 |
| Stau in einer internationalen Vermittlungsstelle oder an deren Ausgang | A-15 |

Signalgruppe B (rückwärts):

| Description | Backward signal |
| --- | --- |
| Reserve | B-1 |
| Send special information tone | B-2 |
| Leitung des Teilnehmers besetzt | B-3 |
| Stau (nach Umschaltung Gruppe A zu B) | B-4 |
| Nicht zugewiesene Nummer | B-5 |
| Leitung des Teilnehmers frei, kostenpflichtig | B-6 |
| Leitung des Teilnehmers frei, kostenfrei | B-7 |
| Leitung des Teilnehmers außer Betrieb | B-8 |
| Reserve | B-9 |
| Reserve | B-10 |
| Reserve | B-11 |
| Reserve | B-12 |
| Reserve | B-13 |
| Reserve | B-14 |
| Reserve | B-15 |

#### MFC/R2 Sequenz

Die folgende Sequenz veranschaulicht einen Anruf, der von einer Erweiterung eines Asterisk zu einem Endgerät im PSTN ausgeht. Das PSTN legt den Anruf auf und beendet die Kommunikation.

![Ein vollständiger MFC/R2 Anrufablauf zwischen Asterisk und dem Telekommunikationsanbieter: Leitungs­signalisierung (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) wird im Timeslot 16 ausgetauscht, die gewählten Ziffern und rückwärts gerichtete „send next digit“-Signale (Gruppen I/A/B) reisen in‑Band, und die hörbaren Töne erreichen den Teilnehmer.](../images/10-legacy-fig11.png)

### Wie man den Treiber libopenr2 verwendet

Das von Moises Silva initiierte Projekt wurde von dem von Steve Underwood geschriebenen Unicall‑Channel‑Treiber inspiriert. Die OpenR2‑Bibliothek ist derzeit die stabilste Software‑Lösung für Asterisk. Mit dieser Lösung können wir jede digitale Karte verwenden, die mit DAHDI kompatibel ist. Zuvor standen nur proprietäre Lösungen für MFC/R2 zur Verfügung; eine der besten, die ich verwendet habe, ist die von Khomp bereitgestellte, www.khomp.com.br. In Asterisk 22 ist die MFC/R2‑Unterstützung über libopenR2 integriert, wenn die Bibliothek zur Compile‑Zeit vorhanden ist – es ist kein externes Patch erforderlich. Die nachstehenden Schritte zeigen die historische manuelle Installation zur Referenz; auf modernen Systemen installieren Sie `libopenr2-dev` über den Paketmanager Ihrer Distribution, bevor Sie `./configure` ausführen, und aktivieren dann `chan_dahdi` in `make menuselect`.

Die nachstehenden Schritte bauen openr2 und Asterisk aus ihren aktuellen Git‑Repositories. Sie werden als Referenz für Seiten bereitgehalten, die aus dem Quellcode bauen; auf einer modernen Distribution können Sie sie in der Regel vollständig überspringen, indem Sie das `libopenr2-dev`‑Paket und ein paketiertes Asterisk 22‑Build installieren, da `chan_dahdi` die R2‑Unterstützung direkt gegen libopenr2 kompiliert, ohne externen Patch.

Schritt 1: Installieren Sie die benötigten Build‑Tools.

```
apt-get install git
```

Schritt 2: Klonen Sie die openr2‑Bibliothek und den Asterisk‑Quellcode. Kein spezieller gepatchter Baum ist für Asterisk 22 erforderlich — ein Standard‑Checkout baut die R2‑Unterstützung, solange libopenr2 vorhanden ist.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Step 3: Kompilieren und installieren Bitte, BACK UP Ihren Server, bevor Sie fortfahren.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Hinweis: Führen Sie nicht “make samples” aus, um das Überschreiben Ihrer Konfigurationsdateien zu vermeiden.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Angenommen, Sie haben eine Karte mit einer E1‑Schnittstelle.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: Führen Sie den Befehl dahdi_cfg aus, um die Änderungen am Treiber anzuwenden:

```
dahdi_cfg -vvvvvvvv
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

Step 5: Ändern Sie die Datei chan_dahdi.conf

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

Schritt 6: Ändern Sie den dial plan in der Datei extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Hinweis: Einige TELCOS akzeptieren keine Anrufe ohne Anrufer-ID. Bitte setzen Sie die Anrufer-ID auf eine der vom Betreiber zugewiesenen DID‑Nummern. In manchen Ländern ist dieser Schritt nicht erforderlich. Schritt 7: Lösung testen: Jetzt, mit einer Nebenstelle im Kontext **from-internal**, rufen Sie irgendeine Nummer an und beobachten Sie die Konsole. Prüfen Sie, ob Fehler auftreten. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

Um Fehler in den Anrufen zu erkennen, können Sie das Debugging aktivieren. Gehen Sie dazu wie folgt vor.

1. Editieren Sie die Datei `chan_dahdi.conf` und fügen Sie die folgenden drei Zeilen zur Konfiguration hinzu:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Starten Sie den Asterisk-Server neu
3. Testen Sie den Anruf und prüfen Sie die Anrufdateien unter `/var/log/asterisk/mfcr2/span1`

Unten ist ein Trace für einen normalen Anruf. Vergleichen Sie ihn mit dem, was Sie in Ihrem Anruf erhalten.

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

Die Optionen sind in der Datei chan_dahdi.conf dokumentiert. Einige der wichtigsten Optionen werden hier im Detail beschrieben. Pflichtparameter: mfcr2_variant, mfcr2_max_ani und mfcr2_max_dnis. mfcr2_variant: Ländervariante.

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

mfcr2_max_ani: Maximale Anzahl von ANI‑Ziffern, nach denen gefragt werden soll  
mfcr2_max_dnis: Maximale Anzahl von DNIS‑Ziffern, nach denen gefragt werden soll  
mfcr2_get_ani_first: Gibt an, ob ANI vor DNIS abgefragt werden soll (von einigen TELCOS verlangt)  
mfcr2_category: Anruferkategorie. Sie können die Variable MFCR2_CATEGORY setzen, bevor der Anruf gestartet wird  
mfcr2_logdir: Verzeichnis, in dem die Anrufdateien protokolliert werden. (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files: Gibt an, ob Anrufe protokolliert werden sollen  

- mfcr2_logging: Protokollierungswerte  
- cas – ABCD‑Bits für Tx und Rx  
- mf – Multifrequenz‑Töne  
- stack – ausführliche Ausgabe des Kanal‑ und Kontext‑Stacks  
- all – alle Aktivitäten  
- nothing – nichts protokollieren  

mfcr2_mfback_timeout: Dieser Wert verdient besondere Erwähnung. Wenn Sie ein Mobiltelefon anrufen oder ein Anruf lange dauert, kann dieser Parameter ein Timeout verursachen, daher wird er häufig für Feinabstimmungen angepasst. Wenn einige Ihrer Anrufe nicht abgeschlossen werden, ist dies der Parameter, den Sie zuerst ändern sollten.  
mfcr2_metering_pulse_timeout: Pulse werden von einigen R2‑Varianten verwendet, um Kosten anzuzeigen  
mfcr2_allow_collect_calls: In Brasilien wird der Ton II‑8 verwendet, um einen Sammelruf anzuzeigen; dieser Parameter ermöglicht es, Sammelrufe zu blockieren.  
mfcr2_double_answer: Wird ebenfalls verwendet, um Sammelrufe zu vermeiden, wenn eine doppelte Annahme erforderlich ist. Mit double_answer=yes blockieren Sie tatsächlich die Sammelrufe.  
mfcr2_immediate_accept: Ermöglicht das Überspringen der Verwendung von Gruppe‑B/II‑Signalen und springt direkt in den akzeptierten Zustand.  
mfcr2_forced_release: Ermöglicht das schnellere Freigeben des Anrufs; funktioniert für die brasilianische Variante.  

#### ANI and DNIS

Automatic Number Identification (ANI) ist die Rufnummer des Anrufers. Dialed Number Identification Service (DNIS) ist die angerufene Nummer bzw. die gewählte Nummer. Wenn ein Anruf empfangen wird, werden normalerweise die letzten vier Ziffern an die PBX übermittelt, ein Vorgang, der als direct inward dial (DID) bezeichnet wird. Die ANI‑Nummer ist tatsächlich die Caller ID. ANI enthält die Durchwahl des Anrufers, während DNIS das Ziel des Anrufs enthält. Es ist wichtig, dass diese Parameter korrekt konfiguriert sind. Einige Switches senden nur die letzten vier Ziffern, andere senden die vollständige Nummer.  

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Beispiele:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Das IAX2-Protokoll

In diesem Kapitel lernen wir das Inter-Asterisk eXchange (IAX)-Protokoll kennen, einschließlich seiner Stärken und Schwächen. Details wie Trunk‑Modus und die Verbindung zweier Asterisk‑Server werden ebenfalls behandelt. Alle Verweise in diesem Dokument entsprechen IAX Version 2.

Das IAX‑Protokoll bietet Medientransport und Signalisierung für Sprache und Video. IAX ist sehr innovativ; es spart Bandbreite im Trunk‑Modus und ist viel einfacher als SIP, wenn man NAT durchqueren muss. Der hauptsächliche Einsatz von IAX heutzutage ist die Vernetzung von Asterisk‑Servern. IAX wurde ursprünglich hauptsächlich für Sprache entwickelt, kann aber auch Video und andere Multimedia‑Streams unterstützen.

IAX wurde von anderen VoIP-Protokollen inspiriert, wie SIP und MGCP. Anstatt zwei separate Protokolle für Signalisierung und Medien zu verwenden, hat IAX sie zu einem einzigen Protokoll zusammengefasst. IAX verwendet kein RTP für den Medientransport; stattdessen bettet es die Medien in dieselbe UDP-Verbindung ein.

**Status in Asterisk 22.** `chan_iax2` ist weiterhin enthalten und wird in Asterisk 22 LTS vollständig unterstützt, sodass alles in diesem Abschnitt gültig bleibt. IAX2 ist jedoch ein Legacy‑Protokoll, das nur noch relativ wenig neu eingesetzt wird: Die Branche hat sich weitgehend auf SIP (über `chan_pjsip` in Asterisk 22) für sowohl Provider‑Trunking als auch Server‑Interconnection geeinigt. Der Hauptvorteil von IAX2 bleibt sein Single‑Port‑Design – alle Signalisierung und Medien fließen über einen einzigen UDP‑Port (standardmäßig 4569), was die Firewall‑ und NAT‑Konfiguration im Vergleich zu SIP mit separaten RTP‑Streams vereinfacht. Für einen neuen Asterisk‑zu‑Asterisk‑Trunk, bei dem NAT kein Thema ist, wird ein PJSIP‑Trunk als moderner Ansatz empfohlen; IAX2 wird hier behandelt, weil es nach wie vor eine gültige Wahl ist, insbesondere wenn nur ein UDP‑Port durch eine Firewall geöffnet werden kann.

### Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Stärken und Schwächen des IAX-Protokolls identifizieren
- Nutzungsszenarien für das IAX-Protokoll beschreiben
- Die Vorteile des IAX-Trunk-Modus beschreiben
- iax.conf für Telefone konfigurieren
- iax.conf für die Anbindung an einen VoIP‑Provider konfigurieren
- iax.conf für die Asterisk‑Verbindung konfigurieren
- IAX‑Authentifizierung verstehen

### IAX-Design

Die Hauptziele für das IAX-Design sind:

- Um die für Medientransport und Signalisierung erforderliche Bandbreite zu reduzieren
- Um NAT‑Transparenz zu bieten
- Um die Dialplan‑Informationen übertragen zu können
- Um die effiziente Nutzung von Paging und Intercom zu unterstützen

IAX ist ein Peer-to-Peer‑Signalisierungs‑ und Medienprotokoll, das dem SIP ähnlich ist, jedoch kein RTP verwendet. Der grundlegende Ansatz besteht darin, die Multimedia‑Streams über eine einzige UDP‑Verbindung zwischen zwei Hosts zu multiplexen. Der größte Vorteil dieses Ansatzes ist seine Einfachheit beim Durchqueren von Verbindungen über NAT, die häufig in xDSL‑Modems vorkommen. IAX verwendet standardmäßig einen einzigen Port, UDP 4569, und nutzt dann eine Rufnummer mit 15 Bits, um alle Streams zu multiplexen. Das IAX‑Protokoll verwendet Registrierungs‑ und Authentifizierungsprozesse, die dem SIP‑Protokoll ähneln. Eine Beschreibung des Protokolls findet sich unter http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![Das IAX‑Protokoll multiplexiert viele Anrufe zwischen zwei Endpunkten über einen einzigen UDP‑Port (standardmäßig 4569) und verwendet eine 15‑Bit‑Rufnummer, um die Streams zu trennen – was die NAT‑Durchdringung einfach macht.](../images/10-legacy-fig12.png)

### Bandbreitennutzung

Der in VoIP‑Netzwerken verwendete Bandbreite wird von mehreren Faktoren beeinflusst; Codecs und Protokoll‑Header sind die wichtigsten. Das IAX‑Protokoll hat ein überraschendes Merkmal namens trunk mode, wodurch es mehrere Anrufe mit einem einzigen Header multiplext. Durch das Spielen mit dem Asterisk‑Bandbreitenrechner sehen Sie, wie IAX‑Trunks Sie bis zu 80 % des Datenverkehrs bei mehreren Anrufen einsparen können.

![Vergleich von IAX- und SIP-Overhead: Zwei SIP/RTP-Anrufe benötigen zwei Pakete (40 Byte Nutzdaten unter 156 Byte Overhead), während der IAX2-Trunk‑Modus beide Anrufe in einem einzigen Paket (40 Byte Nutzdaten unter nur 66 Byte Overhead) transportiert, indem ein IP/UDP‑Header über viele Mini‑Frames geteilt wird.](../images/10-legacy-fig13.png)

### Kanalbenennung

Es ist wichtig, die Kanalbenennungs‑Konventionen zu verstehen, da Sie diese Namen verwenden werden, wenn Sie einen Kanal im Dialplan angeben. Das Format eines IAX‑Kanalnamens, der für ausgehende Kanäle verwendet wird, lautet:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — UserID auf dem entfernten Peer oder Name des in iax.conf konfigurierten Clients
- `<secret>` — Das Passwort. Alternativ kann es der Dateiname für einen RSA‑Schlüssel ohne die Endung (.key oder .pub) sein, eingeschlossen in eckige Klammern
- `<peer>` — Name des Servers, zu dem verbunden werden soll
- `<portno>` — Port‑Nummer für die Verbindung
- `<exten>` — Durchwahl im entfernten Asterisk‑Server
- `<context>` — Kontext im entfernten Asterisk‑Server
- `<options>` — Die einzige verfügbare Option ist 'a', was 'request autoanswer' bedeutet

#### Outbound channels example:

Outbound channels werden in der Asterisk‑Konsole angezeigt.

- `IAX2/8590:secret@myserver/8590@default` — Ruf die Durchwahl 8590 in myserver an. Sie verwendet 8590:secret als Namens‑/Passwort‑Paar
- `IAX2/iaxphone` — Ruf „iaxphone“ an
- `IAX2/judy:[judyrsa]@somewhere.com` — Ruf somewhere.com mit judy als Benutzernamen und einem RSA‑Schlüssel zur Authentifizierung an

#### The format of an incoming IAX channel is:

Inbound channels werden in der Asterisk‑Konsole angezeigt.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — Benutzername, falls bekannt
- `<host>` — Host, der sich verbindet
- `<callno>` — Lokale Rufnummer

Beispiel für eingehenden Kanal:

- `IAX2[flavio@8.8.30.34]/10` — Rufnummer 10 von IP‑Adresse 8.8.30.34 mit flavio als Benutzer.
- `IAX2[8.8.30.50]/11` — Rufnummer 11 von IP‑Adresse 8.8.30.50.

### Verwendung von IAX

Sie können IAX auf verschiedene Arten nutzen. In diesem Abschnitt zeigen wir Ihnen, wie Sie IAX für mehrere Szenarien konfigurieren, darunter:

- Anschluss eines Softphones über IAX
- Anschluss von IAX an einen VoIP‑Provider über IAX
- Anschluss zweier Server über IAX
- Anschluss zweier Server über IAX im Trunk‑Modus
- Fehlersuche bei einer IAX‑Verbindung
- Verwendung von RSA‑Schlüsselpaaren zur Authentifizierung

#### Anschluss eines Softphones über IAX

Asterisk unterstützt IP‑Telefone, die auf IAX basieren, wie das ATCOM und das alte ATA von Digium (genannt IAXy) sowie Softphones, die noch das IAX2‑Protokoll implementieren. Der Vorgang für Softphones, ATAs und Hard‑Phones ist ähnlich. Um ein IAX‑Gerät zu konfigurieren, müssen Sie die Datei iax.conf in /etc/asterisk bearbeiten

```
directory.
```

Wir werden ein IAX2‑fähiges Softphone als Beispiel verwenden.

1. Erstellen Sie ein Backup der originalen `iax.conf`‑Datei mit:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. Beginnen Sie mit dem Bearbeiten einer neuen `iax.conf` Datei:

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

Ich habe versucht, die Standard‑(nicht kommentierten) Zeilen der Beispieldatei beizubehalten. Die folgenden Parameter wurden geändert:

```
bandwidth=high
```

Diese Zeile beeinflusst die Codec‑Auswahl. Die Verwendung der hohen Einstellung ermöglicht die Auswahl eines breitbandigen und hochwertigen Codecs wie g.711, definiert durch das Schlüsselwort ulaw. Wenn Sie den Standardparameter beibehalten, können Sie ulaw nicht auswählen. In diesem Fall gibt Asterisk die Meldung “no codec available” für die untenstehende Konfiguration aus.

```
disallow=all
allow=ulaw
```

In den oben beschriebenen Befehlen haben wir alle Codecs deaktiviert und nur ulaw aktiviert. In LANs bevorzugen die meisten Menschen ulaw, weil es nicht prozessorintensiv ist und CPU‑Zyklen spart. Auch wenn dabei mehr Bandbreite verbraucht wird, ist dieser Codec vorzuziehen, weil man in LANs üblicherweise ein 100‑Megabit‑Ethernet oder sogar ein Gigabit hat. Ein Sprachgespräch mit ulaw verbraucht fast 100 Kilobit pro Sekunde Bandbreite Ihres Netzwerks, was für heutige Hochgeschwindigkeits‑LANs ein sehr geringer Verbrauch ist. In WAN‑ oder Internet‑Netzwerken deaktiviert man normalerweise ulaw und tauscht einige verfügbare CPU‑Zyklen gegen Sprachkompression ein, um die Bandbreitennutzung zu verbessern. Die Codecs gsm, g729 und ilbc bieten ebenfalls einen guten Kompressionsfaktor.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

In den obigen Befehlen haben wir einen Freund namens [2003] definiert. Der Kontext ist der Standard (in den ersten Labs verwenden wir immer den Standard‑Kontext, um Verwirrung zu vermeiden; dieser Kontext wird vollständig erklärt, wenn wir den Dialplan behandeln). Die Zeile „host=dynamic“ ermöglicht eine dynamische Registrierung der IP‑Adresse des Telefons.

3. Laden Sie ein IAX2‑fähiges Softphone herunter und installieren Sie es. Sie können jedes Softphone wählen, das das IAX2‑Protokoll noch unterstützt, für das Labor.
4. Konfigurieren Sie ein IAX‑Konto im Client (typischerweise *Add account* → IAX). Beachten Sie, dass das SipPulse Softphone nur SIP unterstützt und sich nicht über IAX2 registrieren kann, sodass Sie für IAX‑Tests einen Client benötigen, der das Protokoll noch unterstützt.

5. Konfigurieren Sie die `extensions.conf`‑Datei, um Ihr IAX‑Gerät zu testen.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

The number of IAX-capable commercial VoIP providers has declined sharply over the past several Asterisk releases; most providers now offer SIP/PJSIP trunks exclusively. Before committing to an IAX provider, confirm they actively maintain their IAX infrastructure. For a new provider integration, a PJSIP trunk (Chapter 3) is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

In den oben beschriebenen Anweisungen haben Sie sich bei Ihrem Provider mit Ihrem Konto und Passwort registriert. Sobald Sie einen Anruf erhalten, wird er an die Durchwahl 2003 weitergeleitet.

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

In den oben beschriebenen Anweisungen haben wir einen Peer erstellt, der dem Provider für Wählzwecke entspricht.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Dies ist für die RSA-Authentifizierung erforderlich. Die Verwendung des öffentlichen Schlüssels Ihres Anbieters ermöglicht es Ihnen, sicherzustellen, dass der empfangene Anruf wirklich vom echten Anbieter stammt. Wenn jemand anderes versucht, denselben Pfad zu verwenden, kann er ihn nicht authentifizieren, weil ihm der entsprechende private Schlüssel fehlt. Schritt 4: Versuchen Sie die Verbindung. Um die Verbindung zu testen, wählen Sie irgendeine Nummer. Einige Anbieter stellen einen Echo‑Test bereit. Um dies zu erreichen, bearbeiten Sie bitte die Datei extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Gehen Sie zur Asterisk CLI und führen Sie einen Reload aus. Um zu überprüfen, ob Asterisk beim Provider registriert ist, verwenden Sie den nächsten Befehl.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Connecting two Asterisk servers through an IAX trunk

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![Connecting two Asterisk servers with an IAX trunk: the HQ server (192.168.1.1, extensions 20xx) and the Branch server (192.168.1.2, extensions 22xx) reach each other over a single IAX trunk — no registration is needed because both IP addresses are fixed and known.](../images/10-legacy-fig15.png)

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

Step 2: Konfigurieren Sie die Datei extensions.conf im Branch-Server

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

Step 3: Konfigurieren Sie die iax.conf-Datei im HQ-Server

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

Step 4: Konfigurieren Sie die extensions.conf-Datei im HQ-Server.

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

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

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

If ein Anruf einen angegebenen Benutzernamen hat, wie zum Beispiel:

- guest
- iaxtel
- iax-gateway
- iax-friend

wird Asterisk versuchen, den Anruf nur mit dem entsprechenden Eintrag in der iax.conf‑Datei zu authentifizieren. Werden andere Namen angegeben, wird der Anruf abgewiesen. Wird kein Benutzer angegeben, versucht Asterisk, die Verbindung als guest zu authentifizieren. Existiert jedoch kein guest, wird versucht, jede andere Verbindung mit einem passenden Secret zu verwenden. Mit anderen Worten: Wenn Sie keinen guest‑Abschnitt in Ihrer iax.conf‑Datei haben, könnte ein böswilliger Benutzer versuchen, ein passendes Secret zu erraten, indem er keinen Benutzernamen angibt. Die Deny/Allow‑Beschränkungen für IP‑Adressen gelten ebenfalls. Eine gute Möglichkeit, das Erraten von Secrets zu verhindern, ist die Verwendung von RSA‑Authentifizierung. Eine weitere Methode besteht darin, die IP‑Adressen, die Anrufe tätigen dürfen, zu beschränken.

#### IP‑Adressbeschränkungen

Der Zugriff wird mit den Zeilen `permit` und `deny` gesteuert:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

Regeln werden nacheinander interpretiert, und alle werden ausgewertet (dieses Konzept unterscheidet sich von den ACLs, die üblicherweise in Routern und Firewalls zu finden sind). Die zuletzt passende Anweisung überschreibt die vorherigen.

Beispiel #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

This will deny any packet from the 192.168.0.0/24 network.

Example #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

Dies wird jedes Paket zulassen, weil die letzte Anweisung die erste überschreibt.

#### Outbound connections

Outbound connections acquire authentication information using the following methods:

- The IAX2 channel description passed by the dial() application.
- An entry with type=peer or type=friend in the iax.conf file.
- A combination of both methods.

#### Connecting two Asterisk servers using RSA keys

It is possible to use IAX with strong authentication using asymmetric RSA keys. According to the source code (res_krypto.c), Asterisk uses RSA keys with an SHA-1 algorithm for message digests instead of the weaker MD5. Below is a step-by-step guide for setting up two servers using RSA keys.

##### Configuring the server for the branch

Step 1: Generate the RSA keys in the branch server

```
astgenkey -n
```

Wenn Sie gefragt werden, verwenden Sie den Schlüsselnamen **branch**. Wir haben den Parameter **–n** verwendet, um das Übergeben einer Passphrase bei jeder Neuinitialisierung von **Asterisk** zu vermeiden. Wenn Sie die Sicherheit erhöhen möchten, verwenden Sie nicht den **–n** und starten Sie **Asterisk** mit **asterisk -i**. **Schritt 2:** Kopieren Sie die Schlüssel in das Verzeichnis **/var/lib/asterisk/keys**.

```
cp branch.* /var/lib/asterisk/keys
```

Step 3: Kopieren Sie den öffentlichen Schlüssel zum HQ-Server

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4: Bearbeiten Sie die iax.conf-Datei im Branch-Server.

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

# Schritt 8: Konfigurieren Sie die extensions.conf-Datei im Branch-Server

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Konfiguration des Servers für die Zentrale

Schritt 1: Generieren Sie die RSA‑Schlüssel im HQ‑Server

```
astgenkey -n
```

Wenn Sie gefragt werden, verwenden Sie den Schlüsselnamen hq.  
Schritt 2: Kopieren Sie die Schlüssel in das Verzeichnis /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

# Schritt 3: Kopieren Sie den öffentlichen Schlüssel zum BRANCH-Server

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Step 4: Konfigurieren Sie die iax.conf-Datei im HQ-Server

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

Schritt 10: Konfigurieren Sie die extensions.conf-Datei im HQ-Server.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### IAX2-Verschlüsselung

IAX unterstützt die Anrufverschlüsselung mit einem symmetrischen Schlüssel, einem 128‑Bit‑Blockcipher namens AES (Advanced Encryption Standard). Es ist sehr einfach, die Verschlüsselung zwischen IAX‑Trunks zu aktivieren. In der Datei iax.conf verwenden Sie:

```
encryption=yes
```

Um die Verschlüsselung zu erzwingen:

```
forceencryption=yes
```

Um die Kompatibilität mit älteren Versionen zu gewährleisten, müssen Sie möglicherweise die Schlüsselrotation deaktivieren, indem Sie verwenden:

```
keyrotate=no
```

### IAX2-Debug-Befehle

Im Folgenden finden Sie einige der wichtigsten Fehlersuch‑Konsolenbefehle für Asterisk.

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

Betrachten Sie diese Ausgabe, identifizieren Sie den Beginn und das Ende des Anrufs. Beobachten Sie die Verzögerungs‑ und Jitter‑Informationen, die mit poke‑ und pong‑Paketen erhalten werden. Diese Pakete helfen, die Ausgabe des Befehls „iax2 show netstats“ zu erzeugen.

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

Um das Debugging zu deaktivieren, verwenden Sie:

```
vtsvoffice*CLI>iax2 no debug
```

### Zusammenfassung

Dieses Kapitel hat die Stärken und Schwächen des IAX‑Protokolls überprüft. Es hat gezeigt, wie IAX in mehreren Szenarien funktioniert, wie zum Beispiel bei Softphones und einem Trunk zwischen zwei Asterisk‑Servern. Der Trunk‑Modus ermöglicht es, Bandbreite zu sparen, indem mehr als ein Anruf in einem einzigen Paket transportiert wird. Abschließend haben Sie Konsolenbefehle kennengelernt, die Sie verwenden können, um den Status zu prüfen und das Protokoll zu debuggen.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Schritt 2: Konfigurieren Sie den [peer] in sip.conf Erstellen Sie einen Eintrag vom Typ peer beim gewünschten Provider, um das Wählen mit Asterisk zu vereinfachen.

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

Step 3: Erstellen Sie eine Route zum Provider im Dialplan Wir wählen die Ziffern 010 als Zielroute zum Provider. Um #610000 beim Provider zu wählen, wählen Sie einfach 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### SIP-Optionen, die speziell für das Provider‑Szenario gelten

Die folgende Diskussion untersucht die Details der in der sip.conf-Datei gesetzten Optionen für die Verbindung zu einem VoIP‑Provider.

```
register=>username:password@hostname/4100
```

Die in der sip.conf-Datei registrierte Anweisung wird verwendet, um sich bei einem Provider zu registrieren. Die Register‑Transaktion wird mit dem Namen und dem Secret authentifiziert. Sie können einen Schrägstrich („/“) verwenden, um eine Nebenstelle für eingehende Anrufe anzugeben. Technisch gesehen wird die Nebenstelle im „Contact“-Header‑Feld der SIP‑Anfrage platziert. Das Registrierungsverhalten kann durch bestimmte Parameter gesteuert werden:

```
registertimeout=20
registerattempts=10
```

Um zu prüfen, ob die Registrierung erfolgreich war, war der veraltete Konsolenbefehl `sip show registry`. Unter Asterisk 22 ist der entsprechende Befehl `pjsip show registrations` (ausgehende Registrierungen) und `pjsip show endpoints` für den Endpunktstatus.

Der Parameter “username” wird im Authentifizierungs‑Digest verwendet. Der Digest wird aus username, secret und realm berechnet:

```
username=username
```

Host definiert die Adresse oder den Namen des VoIP‑Anbieters:

```
host=hostname
```

Die Parameter Fromuser und Fromdomain werden manchmal für die Authentifizierung benötigt. Diese Parameter werden im SIP-From-Header-Feld verwendet:

```
fromuser=username
fromdomain=hostname
```

Wenn Sie sich mit einem VoIP‑Provider verbinden, werden Anmeldeinformationen benötigt. Nach dem ersten Invite sendet der Provider eine Nachricht namens “407 Proxy Authentication Required”; Sie geben die Anmeldeinformationen in der nachfolgenden INVITE‑Nachricht an. Für eingehende Anrufe wird Ihr Asterisk‑Server den Provider nach Anmeldeinformationen fragen. Offensichtlich hat der Provider keine gültige Anmeldeinformation für Ihren Asterisk‑Server. Wenn Sie insecure=invite verwenden, teilen Sie Asterisk mit, die “407 Proxy Authentication Required” nicht an den Provider zu senden und eingehende Anrufe zu akzeptieren. Sie können auch insecure=port, invite verwenden, um den Peer anhand der IP‑Adresse zuzuordnen, ohne die Portnummer zu prüfen.

```
insecure=invite, port
```

### Connecting two Asterisk servers together using SIP (sip.conf)

Sie können SIP verwenden, um zwei Asterisk‑Boxen zu verbinden. Es ist wichtig, auf den Dialplan zu achten, bevor Sie mit dieser Konfiguration fortfahren. Benutzer möchten im Allgemeinen andere PBXs mit minimalem Aufwand verbinden. Die Idee hier ist, nur eine Durchwahlnummer zu verwenden, um sich mit der anderen PBX zu verbinden. Schritt 1: Bearbeiten Sie die sip.conf‑Datei auf Server A:

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

Step 2: Edit the sip.conf file in server B:

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

![Zwei Asterisk-Server über SIP verbinden: Server A (Durchwahlen 4400/4401) und Server B (Durchwahlen 4500/4501) tauschen SIP-Signalisierung aus, sodass Benutzer jeder PBX die andere anrufen können](../images/07-sip-and-pjsip-fig08.png)

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

Step 3: Bearbeiten Sie die extensions.conf‑Datei auf Server A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Step 4: Edit the extensions.conf file in server B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk domain support (sip.conf)

Das SIP‑Protokoll folgt der Internet‑Architektur. Das Erste, was vor der Konfiguration von SIP zu tun ist, besteht darin, die DNS‑Server korrekt einzurichten. In einer SIP‑Umgebung können Sie einen Benutzer anrufen, der sich in einem beliebigen SIP‑Proxy befindet, und andere Benutzer können Sie ebenfalls über Ihre SIP Uniform Resource Identifier (URI) anrufen. Um einen DNS‑Server für SIP festzulegen, müssen Sie SRV‑Einträge zu Ihrem DNS‑Server hinzufügen.

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

Nachdem Sie den DNS konfiguriert haben, können Sie die URI verwenden, die auf einen SIP‑Benutzer, ein SIP‑Telefon oder eine Telefon­erweiterung verweist. Eine SIP‑URI sieht ähnlich wie eine E‑Mail‑Adresse aus (z. B. sip:chuck@yourpartnerdomain.com). Mit SIP‑URIs ist keine Telefonnummer erforderlich, um einen Anruf von einem SIP‑Telefon zu einem anderen zu tätigen. Um einen externen Benutzer zu wählen, verwenden Sie einfach eine Anweisung wie die unten gezeigte.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Bestimmte Parameter können das Domain-Verhalten steuern.

```
srvlookup=yes
```

Dieser Parameter aktiviert DNS SRV‑Abfragen bei ausgehenden Anrufen. Mit diesem Parameter ist es möglich, Anrufe mit SIP‑Namen basierend auf der Domain zu wählen.

```
allowguest=yes
```

This parameter allows an external invite to be processed without authentication. It processes the call within the context defined in the general section or in the domain statement. Warning: If you define a context in the general section with access to PSTN, an external user can dial the PSTN over your PBX. In this case, you will incur any charges. Allow only your own extensions in the context defined in the general section.

![Verbindung zu anderen SIP-Servern per Domain: youdomain.com und yourpartnerdomain.com tauschen SIP‑Signalisierung aus, sodass Benutzer wie lee und bruce chuck und norris über SIP‑URIs anrufen können](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

Der domain command ermöglicht es Ihnen, mehr als eine Domain innerhalb von Asterisk zu verwalten. Wenn ein Anruf von einer bestimmten Domain kommt, wird er zu einem bestimmten Kontext geleitet.

```
;autodomain=yes
```

Dieser Parameter schließt die lokale IP und den Hostnamen in die erlaubten Domains ein.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

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

Step 2: Jetzt das Softphone für Presence konfigurieren. Wir zeigen Ihnen, wie Sie das SipPulse Softphone einrichten.

- Ablauf: Rechtsklick → SIP Account Settings → Properties → Presence
- Ändern Sie das Presence‑Modell von peer-to-peer zu presence agent, wodurch das Softphone Asterisk für SIP‑Events abonniert.

Step 3: Den Kontakt zu anderen Softphones hinzufügen. In diesem Beispiel ist das SipPulse Softphone Konto 2000, daher fügen wir einen Kontakt für Konto 2001 hinzu. Ablauf: Das rechte Panel öffnen (Presence‑Panel im Softphone) → Auf Kontakte klicken → Kontakt hinzufügen. Namen 2001 eingeben. Anzeige 2001 und nicht vergessen, das Kästchen „Show this contact’s availability“ zu aktivieren.

Step 4: Jetzt die Nebenstelle 2001 anrufen und den Status des Telefons im rechten Panel des Softphones prüfen. Verwenden Sie den Konsolenbefehl `core show hints`, um den Presence‑Status auf dem Server zu beobachten (im alten chan_sip zeigte `sip show inuse`, wie viele Anrufe Sie auf jeder Leitung hatten). Auf Asterisk 22 benutzen Sie `pjsip show endpoints`, um Endpoint‑ und Kanal‑Zustand zu inspizieren. Der Presence/BLF‑Status erscheint in den Kontakten oder im BLF‑Panel des Softphones — wie genau er dargestellt wird, hängt vom Client ab.

#### Codec configuration

Codec configuration ist einfach und unkompliziert. Sie können die Schlüsselwörter allow und disallow im Abschnitt [general] oder im Peer/User‑Abschnitt setzen. Die bewährte Vorgehensweise ist, den Codec zu standardisieren, um Transcoding zu vermeiden, das prozessorintensiv ist. Bitte verwenden Sie denselben Codec für Nachrichten und Ansagen.

```
[general]
disallow=all
allow=g729
```

#### DTMF-Optionen

Bei bestimmten Gelegenheiten übergeben Sie Ziffern an eine Anwendung wie Voicemail oder Interactive Voice Response (IVR). Es ist wichtig, DTMF korrekt zu übermitteln. Die einfachste Methode zur Übermittlung von DTMF heißt inband. Sie wird im [general]- oder Peer/User‑Abschnitt der sip.conf‑Datei festgelegt. Wenn Sie `dtmfmode=inband` setzen, werden DTMF‑Töne als Geräusche im Audiokanal erzeugt. Das Hauptproblem bei dieser Methode ist, dass bei Kompression des Audiokanals mit einem Codec wie `g729` die Geräusche verzerrt werden und die DTMF‑Töne nicht richtig erkannt werden. Wenn Sie planen, `dtmfmode=inband` zu verwenden, nutzen Sie den Codec `g.711` (ulaw und alaw).

```
dtmfmode=inband
```

Ein weiterer Ansatz ist die Verwendung von RFC2833, das es ermöglicht, DTMF‑Töne als benannte Ereignisse in den RTP‑Paketen zu übermitteln.

```
dtmfmode=rfc2833
```

Schließlich können Sie DTMF‑Ziffern in SIP‑Paketen statt in RTP‑Paketen übermitteln. Diese Methode ist in RFC3265 (Signaling Events) und RFC2976 definiert.

```
dtmfmode=info
```

Following the release of version 1.2, it is now possible to use:

```
dtmfmode=auto
```

This tries to use the RFC2833; if it is not possible, use band tones.

#### Qualitätsdienst (QoS) Markierungs-Konfiguration

QoS ist ein Satz von Techniken, die für die Sprachqualität verantwortlich sind. QoS wird so implementiert, dass Bandbreite, Latenz und Jitter reduziert werden. Die Hauptfunktionen von QoS sind Paketscheduling, Fragmentierung und Header‑Kompression. QoS wird in Switches und Routern implementiert, nicht von Asterisk selbst. Allerdings kann Asterisk Router und Switches unterstützen, indem es Pakete für die bevorzugte Zustellung markiert. Die Markierung erfolgt mittels Differentiated Services Code Points (DSCP), die in den RFCs 2474 und RFC2475 definiert sind.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Ab Version 1.4 können Sie unterschiedliche Codes für Signalisierung (SIP), Audio (RTP) und Video (RTP) angeben.

### SIP-Authentifizierung (sip.conf)

Wenn das veraltete `chan_sip` einen SIP-Anruf erhielt, folgte es den im folgenden Diagramm beschriebenen Regeln. Drei Parameter spielten eine wichtige Rolle bei der SIP-Authentifizierung. Auf Asterisk 22 wird die Authentifizierung stattdessen mit PJSIP `auth`‑Objekten (`type=auth`, `auth_type=userpass`, `username=`, `password=`) konfiguriert, die von einem Endpoint referenziert werden, und die IP‑Zugriffskontrolle erfolgt mit `permit=`/`deny=` am Endpoint oder über ein `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Dieser Parameter steuert, ob ein Benutzer ohne entsprechenden Peer sich ohne Namen und Geheimnis authentifizieren kann. Wir haben diesen Parameter im Abschnitt zur Domain‑Unterstützung besprochen.

```
insecure=invite,port
```

When we use insecure=invite, Asterisk does not generate the message “407 Proxy Authentication Required”. Without this message, the user can make a call without authentication. This is often used to connect to VoIP service providers. The calls coming from the VoIP service provider are usually not authenticated.

```
autocreatepeer=yes/no
```

This command is used when Asterisk is connected to a SIP proxy. It dynamically creates a peer to each call. When this option is enabled, any UAC can connect to the Asterisk server. It is important to limit the IP connection to the SIP proxy. The SIP proxy, in turn, takes care of access control. Peer configuration is based on the general options as well as the “Contact” header field of the SIP packet. Warning: Use this with extreme caution as it completely opens Asterisk.

```
secret=secret, remotesecret=secret
```

Dieser Parameter konfiguriert das Secret für die Authentifizierung, verwendet **secret** für eingehende Anfragen und **remotesecret** für ausgehende Anfragen. Wenn Sie die Secrets nicht in Textdateien offenlegen möchten, können Sie **md5secret** verwenden, um stattdessen einen Hash einzufügen. Um das MD5‑Secret zu erzeugen, können Sie verwenden:

```
echo -n "username:realm:secret" |md5sum
```

Dann verwenden Sie die folgende Anweisung:

```
md5secret=0b0e5d467890....
```

Warning: Vergessen Sie nicht, den –n Parameter zu verwenden; der Wagenrücklauf wird bei der md5‑Berechnung verwendet.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

The statements above will deny all IP addresses and allow UAC only from the local network (192.168.1.0/24).

#### RTP-Optionen

It is possible to control some RTP parameters.

```
rtptimeout=60
```

Dies beendet Anrufe ohne RTP‑Aktivität nach mehr als 60 Sekunden, wenn sie nicht gehalten werden.

```
rtpholdtimeout=120
```

This terminates calls without RTP activity even on hold (should be bigger than rtptimeout).

### SIP NAT traversal (sip.conf)

The NAT *theory* (the four NAT types, the Contact-header problem, keep-alives, and forcing media through the server) is protocol-level and is covered in the *SIP & PJSIP in depth* chapter. The `sip.conf` parameters shown here (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) are **legacy chan_sip** and were removed in Asterisk 21+. On PJSIP these map to transport/endpoint settings such as `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, and `local_net=` on the transport, plus `qualify_frequency=` on the AOR.

In legacy chan_sip, the parameter `nat` had five options:

- nat = no — Do no special NAT handling other than RFC3581
- nat = force_rport — Pretend there was an rport parameter even if there wasn't
- nat = comedia — Send media to the port Asterisk received it from regardless of where the SDP says to send it.
- nat = auto_force_rport — Set the force_rport option if Asterisk detects NAT (default)
- nat = auto_comedia — Set the comedia option if Asterisk detects NAT

When you put the statement “nat=force_rport” in the sip.conf file, you are telling Asterisk to ignore the address contained in the “Contact” header field of the SIP header and use the source IP address and port in the packet’s IP header and also to send the media back to the address from where it was received ignoring the content of the SDP header.

```
nat=force_rport,comedia
```

Es ist notwendig, das NAT‑Mapping offen zu halten. Wenn das NAT abläuft, kann Asterisk keine Einladung an den UAC senden. Der UAC kann Anrufe senden, aber keine empfangen. Die folgende Anweisung kann verwendet werden, um das NAT offen zu halten.

```
qualify=yes
```

Qualify sendet regelmäßig ein SIP‑Paket mit der OPTIONS‑Methode, wodurch NAT‑Verbindungen offen gehalten werden. Qualify sendet alle 60 Sekunden ein OPTIONS‑Paket und zusätzlich jede 10. Sekunde, wenn der Host nicht erreichbar ist. Sie können `sip show peers` verwenden, um die Latenz der Peers anzuzeigen. Wenn das NAT des Benutzers vom symmetrischen Typ ist, ist es nicht möglich, Pakete direkt von einem UAC zu einem anderen zu senden; in diesem Fall müssen Sie das RTP über Asterisk erzwingen, indem Sie:

```
directmedia=no
```

#### Asterisk hinter NAT (sip.conf)

Alle vorherigen Szenarien gehen davon aus, dass der Asterisk‑Server eine externe (gültige) Internetadresse hat. Manchmal wird der Asterisk‑Server jedoch hinter einer Firewall mit NAT betrieben. In diesem Fall sind zusätzliche Konfigurationen erforderlich.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. Konfigurieren Sie die Firewall, um den UDP‑Port 5060 statisch an den Asterisk‑Server weiterzuleiten.  
2. Konfigurieren Sie die Firewall, um die UDP‑Ports von 10000 bis 20000 statisch weiterzuleiten.

Wenn Sie die Anzahl der geöffneten Ports einschränken möchten, können Sie die `rtp.conf`‑Datei bearbeiten, um den RTP‑Port‑Bereich zu ändern. Eine andere Möglichkeit besteht darin, eine intelligente Firewall zu verwenden, die das SIP‑Protokoll unterstützt, um die RTP‑Ports dynamisch zu öffnen.

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

Schritt 3: Konfigurieren Sie Asterisk so, dass die externe Adresse in den Header‑Feldern der SIP‑Pakete einschließlich Session Description Protocol (SDP) enthalten ist. Sie können dies erreichen, indem Sie die folgenden beiden Anweisungen zur sip.conf‑Datei hinzufügen:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

Der erste Parameter externaddr weist Asterisk an, die externe IP-Adresse in die SIP-Header für externe Ziele einzufügen. Der zweite Parameter localnet ermöglicht es Asterisk, zwischen externen und internen Adressen zu unterscheiden. Optional können Sie externhost verwenden, wenn Sie einen Dynamic DNS mit einer DHCP‑Adresse auf dem Server nutzen.

### SIP-Wählstrings (chan_sip)

Die `SIP/...`‑Dial‑String‑Technologie, die unten gezeigt wird, ist der entfernte chan_sip‑Treiber. Unter Asterisk 22 verwenden Sie stattdessen die `PJSIP/...`‑Technologie – zum Beispiel `Dial(PJSIP/2000)` oder `Dial(PJSIP/${EXTEN}@provider)`. Die Formen und Bedeutungen sind ansonsten analog.

Sie können ein Legacy‑SIP‑Ziel mit verschiedenen Dial‑Strings anrufen:

```
SIP/peer
```

- ; Muss einen definierten Peer in sip.conf haben

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Beispiele umfassen:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migration eines Legacy‑chan_sip‑Systems zu PJSIP

Da `chan_sip` in Asterisk 21 entfernt wurde und in Asterisk 22 nicht mehr existiert, muss jede
bestehende `sip.conf`‑Installation zu PJSIP migriert werden. Der größte konzeptionelle
Wechsel besteht darin, dass ein einzelner `sip.conf` `[peer]` oder `[friend]` in mehrere
PJSIP‑Objekte aufgeteilt wird, von denen jedes ein `type=` besitzt: ein **endpoint** (Call/Codec/Media‑Einstellungen),
ein oder mehrere **aor**‑Objekte (wo das Gerät erreichbar ist / Registrierung),
ein **auth**‑Objekt (Zugangsdaten) und ein gemeinsamer **transport** (der Listening‑Socket, NAT‑Adressen). Die folgende Tabelle ordnet die gebräuchlichsten Konzepte zu.

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenced via `auth=` and `aors=`) |
| `type=friend` / `type=peer` / `type=user` | a single `type=endpoint` (PJSIP has no friend/peer/user distinction) |
| `host=dynamic` (device registers) | `type=aor` with `max_contacts=1`; the device REGISTERs to update its contact |
| `host=<ip/hostname>` (static) | `type=aor` with a static `contact=sip:host:port` |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` on the endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` on the endpoint (same syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — also `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` on the endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (seconds) on the **aor** |
| `externaddr=` | `external_media_address=` and `external_signaling_address=` on the **transport** |
| `localnet=` | `local_net=` on the **transport** |
| `insecure=invite` (provider, no auth) | omit `auth=`/`outbound_auth=` and use `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (use with care) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (and `cos_audio` / `cos_video`) on the endpoint |

Eine registrierende Nebenstelle, die in legacy `sip.conf` so aussah:

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

wird in `pjsip.conf` unter Asterisk 22 wie folgt:

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

### Das sip_to_pjsip.py Konvertierungsskript

Asterisk liefert ein Hilfsskript, **`sip_to_pjsip.py`**, das eine bestehende `sip.conf` liest und eine `pjsip.conf` erzeugt. Sie können es direkt im Verzeichnis /etc/asterisk ausführen. Das Dienstprogramm befindet sich im Asterisk-Quellbaum unter `contrib/scripts/sip_to_pjsip/`, wobei `${PATH_TO_ASTERISK_SOURCE}` der Pfad ist, in dem die Asterisk-Quelldateien zu finden sind (normalerweise /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Wenn Sie es mit der `--help`‑Option ausführen, sehen Sie dessen Optionen:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

Es akzeptiert außerdem optionale Positionsargumente — `[input-file [output-file]]`,
standardmäßig `sip.conf` und `pjsip.conf` im aktuellen Verzeichnis.

Betrachten Sie die Ausgabe als **Ausgangspunkt**: Überprüfen Sie jedes erzeugte Objekt,
insbesondere Transporte, NAT‑Einstellungen und Codec‑Listen, und testen Sie gründlich, bevor
Sie in die Produktion gehen.

Lassen Sie uns die sip.conf in unseren Begleit‑Labs bei VoIP School Blackbelt (voip.school) migrieren

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

Während die Konvertierung in Ordnung zu sein scheint, können wir sehen, dass einige Elemente wie qualify=yes nicht direkt abgebildet werden können. Um das zu beheben, müssen Sie dem aor-Abschnitt den Befehl qualify_frequency=time in Sekunden hinzufügen. Beispiel unten.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

Die vollständige PJSIP‑Konfiguration wird im Kapitel *SIP & PJSIP in depth* behandelt, und die offizielle Dokumentation unter docs.asterisk.org bietet eine vollständige Abdeckung des Kanals. In unseren begleitenden Labs bei voip.school ermöglicht Labor 5 Ihnen, das gerade Gelernte zu üben.

## Summary

Dieses Kapitel sammelt die Kanaltechnologien, die den heutigen reinen VoIP‑Einsätzen vorausgingen, aber von Asterisk 22 weiterhin unterstützt werden. Sie haben gesehen, wie **analoge** Leitungen und Telefone über **FXO/FXS**‑Schnittstellen auf DAHDI angeschlossen werden, wie **digitale TDM**‑Verbindungen (E1/T1 und ISDN PRI/BRI) bereitgestellt werden und wie **IAX2** (`chan_iax2`) nach wie vor als effizienter, NAT‑freundlicher Server‑zu‑Server‑Trunk dient, obwohl es inzwischen eindeutig als Legacy gilt. Außerdem haben Sie den eingestellten **`chan_sip`**‑Treiber und seine `sip.conf`‑Syntax erneut betrachtet – Sie begegnen ihr in älteren Systemen, sie existiert jedoch nicht mehr in Asterisk 22 – und haben die Migration eines solchen Systems zu PJSIP mithilfe der Konzept‑Mapping‑Tabelle und des `sip_to_pjsip.py`‑Skripts durchgearbeitet. Die Faustregel: Greifen Sie auf alles in diesem Kapitel nur zurück, wenn reale Hardware oder ein bestehendes Legacy‑System Ihnen keine andere Wahl lässt; alles Neugründende ist PJSIP über IP.

## Quiz

1. Bezüglich der beiden analogen Foreign eXchange‑Schnittstellen markieren Sie die korrekten Aussagen (alle zutreffenden auswählen):
   - A. Eine FXO‑Schnittstelle verbindet sich mit dem öffentlichen Telefonnetz (PSTN)‑Zentralamt und bezieht dort den Wähltton.
   - B. Eine FXS‑Schnittstelle liefert Wähltton und Klingelspannung an ein Standard‑Analogtelefon, Faxgerät oder Modem.
   - C. Eine FXS‑Schnittstelle ist die richtige Art, Asterisk an eine Telefonielinie anzuschließen.
   - D. Eine FXO‑Schnittstelle kann auch an einen Nebenstellenanschluss einer alten PBX angeschlossen werden.
2. Welche Signale gehören zur Überwachung einer analogen Leitung (alle zutreffenden auswählen)?
   - A. Auflegen
   - B. Abheben
   - C. Klingeln
   - D. DTMF
3. Echo, Knackgeräusche und Störgeräusche auf einer DAHDI‑Analogkarte werden am häufigsten verursacht durch:
   - A. Die Art, wie Asterisk kompiliert wurde
   - B. PCI‑Interrupt‑Konflikte
   - C. Einen falschen SIP‑Codec
   - D. Einen fehlenden Dial‑Plan
4. Für eine präzise Abrechnung von analogen Kanälen müssen Sie exakt erkennen, wann die Gegenstelle abnimmt. Welches Feature aktivieren Sie in Asterisk (und fordern beim Telefonanbieter an), um dies zu erreichen?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial‑tone generation
5. Die DAHDI‑Hardware ist unabhängig von Asterisk: Die physische Karte wird in `/etc/dahdi/system.conf` konfiguriert, während `chan_dahdi.conf` die Asterisk‑Kanäle definiert, nicht die Hardware selbst.
   - A. Wahr
   - B. Falsch
6. Bezüglich der Kapazität digitaler Trunks und Signalisierung markieren Sie die korrekten Aussagen (alle zutreffenden auswählen):
   - A. Ein E1‑Trunk transportiert 30 Sprachkanäle und ein T1‑Trunk 24.
   - B. Ein ISDN‑PRI verwendet 30B+D auf einem E1 und 23B+D auf einem T1.
   - C. ISDN ist ein Beispiel für CCS‑Signalisierung, während MFC/R2 ein Beispiel für CAS‑Signalisierung ist.
   - D. T1 ist der digitale Trunk, der in Europa und Lateinamerika am häufigsten verwendet wird.
7. Welches Dienstprogramm erkennt DAHDI‑Karten automatisch und erzeugt `/etc/dahdi/system.conf` und `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. Beim Migrieren einer alten `sip.conf` `[friend]` zu PJSIP muss ein einzelner Block in mehrere Objekte aufgeteilt werden. Welche Menge von PJSIP `type=`‑Objekten ersetzt normalerweise ein registrierendes `[friend]`?
   - A. `type=endpoint`, `type=aor` und `type=auth`
   - B. `type=peer` und `type=user`
   - C. `type=sip` nur
   - D. `type=channel` und `type=device`
9. Was ist der wichtigste praktische Vorteil der Verwendung des IAX2‑Trunk‑Modus zwischen zwei Asterisk‑Servern?
   - A. Es verschlüsselt jeden Anruf standardmäßig mit TLS
   - B. Es transportiert mehrere Anrufe unter einem einzigen Header und spart Bandbreite
   - C. Es eliminiert die Notwendigkeit eines Codecs
   - D. Es weist jedem Anruf einen separaten UDP‑Port zu für bessere Qualität
10. RSA‑Schlüssel können für die IAX2‑Authentifizierung verwendet werden. Welchen Schlüssel müssen Sie geheim halten und welchen geben Sie dem anderen Server?
    - A. Den öffentlichen Schlüssel geheim halten; den privaten Schlüssel teilen
    - B. Den privaten Schlüssel geheim halten; den öffentlichen Schlüssel teilen
    - C. Den gemeinsamen Schlüssel geheim halten; den privaten Schlüssel teilen
    - D. Beide Schlüssel müssen geteilt werden

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 —
