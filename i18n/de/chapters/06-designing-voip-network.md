# Designing a VoIP network

Voice over IP gewinnt auf dem Telefonie-Markt schnell an Bedeutung. Das Paradigma der Konvergenz verändert die Art und Weise, wie wir kommunizieren, senkt die Kosten und verbessert den Informationsaustausch. Sprache ist nur der Anfang einer Ära der vollständigen Multimedia-Kommunikation, die Sprache, Video und Präsenz umfasst. In der Zukunft werden wir nicht mehr Menschen zur Arbeit transportieren, sondern die Arbeit zu den Menschen bringen, da dies sauberer, schneller und kostengünstiger ist. VoIP ist nur ein Teil dieser Revolution. Unsere Aufgabe in diesem Kapitel ist es, ein VoIP-Netzwerk zu entwerfen. Dazu müssen wir Konzepte wie Sitzungsprotokolle und Codecs verstehen sowie wissen, wie man die Anzahl der Leitungen und die Bandbreite dimensioniert.

## Objectives

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die Vorteile von VoIP zu verstehen
- Zu beschreiben, wie Asterisk mit VoIP umgeht
- Die Konzepte der SIP- und IAX-Kanäle zu beschreiben
- Das am besten geeignete Protokoll für einen bestimmten Datenkanal auszuwählen
- Den am besten geeigneten Codec für einen bestimmten Datenkanal auszuwählen
- Die erforderliche Anzahl von Kanälen zu dimensionieren
- Die erforderliche Bandbreite zu berechnen

## VoIP benefits

Warum sollten Sie sich für VoIP interessieren? VoIP bietet sowohl Unternehmen als auch Privatpersonen Vorteile. Kostensenkung ist sicherlich einer davon, aber in einigen Umgebungen vereinfacht VoIP die Integration von Computersystemen. Einige der Vorteile sind hier im Detail aufgeführt:

### Convergence

Der Hauptvorteil von VoIP ist die Kombination von Daten- und Sprachnetzwerken zur Kostensenkung (Konvergenz). Die Analyse der reinen Sprachminutenkosten reicht jedoch möglicherweise nicht aus, um die Einführung von VoIP zu rechtfertigen. Die Preise für Gesprächsminuten der Telefongesellschaften sinken schnell, was vor der Einführung von VoIP berücksichtigt werden sollte.

### Infrastructure costs

Die Nutzung einer einzigen Netzwerkinfrastruktur reduziert die Kosten für Erweiterungen, Entfernungen und Änderungen. Da IP allgegenwärtig geworden ist, hat es VoIP-bezogene Technologien auf viele neue Geräte gebracht, wie Mobiltelefone, PDAs, eingebettete Systeme und Laptops.

### Open Standards

Schließlich bieten die offenen Standards, auf denen VoIP aufbaut, die Freiheit, zwischen verschiedenen Anbietern zu wählen. Dieser einzige Vorteil macht den Kunden zum König, anstatt ihn von TELCOS und PBX-Herstellern abhängig zu machen.

### Computer Telephony Integration

Telefonie ist weitaus älter als die Informatik. Telefonie-PBXs basieren auf Leitungsvermittlung, und man verfügt normalerweise über nicht mehr als einen Computer zur Überwachung. Bei VoIP ist die Telefonie von Grund auf auf Computerstandards aufgebaut. Dies macht die Nutzung von Computer-Telefonie-Anwendungen billiger und einfacher als im alten Modell. Sie können schnell eine lange Liste von Telefonie-Anwendungen auf Basis von Asterisk erstellen. Sie können IVRs, ACDs, CTI, Dialer, Screen-Popups und andere Anwendungen in einem Bruchteil der Zeit entwickeln, die für herkömmliche PBXs erforderlich wäre.

## Asterisk VoIP architecture

Die Architektur von Asterisk ist unten dargestellt. Asterisk behandelt alle VoIP-Protokolle als Kanäle. Sie können jeden Codec oder jedes Protokoll verwenden. Das hier zu erlernende Konzept ist, dass Asterisk jede Art von Kanal mit jedem anderen verbindet. Somit können Sie Signalisierungsprotokolle wie SIP und IAX ineinander übersetzen, sogar mit unterschiedlichen Codecs. Zum Beispiel können Sie einen Anruf von einem SIP-Telefon im lokalen Netzwerk mit dem G.711-Codec zu einem SIP-trunk zu Ihrem VoIP-Anbieter mit dem G.729-Codec übersetzen. In den nächsten Kapiteln werden wir die Details der SIP- und IAX-Architektur erläutern. H.323-Unterstützung (über das Add-on chan_ooh323) ist verfügbar, aber zunehmend selten; SIP/PJSIP ist der Standard für moderne Implementierungen.

![Asterisk's modular architecture: applications and channels connect to the PBX switch core through APIs, with codec translation and file-format modules loaded dynamically.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP verwendet eine Reihe verschiedener Protokolle, die zusammenarbeiten. Es ist verlockend, sie dem sieben-schichtigen OSI-Referenzmodell gegenüberzustellen, und viele ältere Diagramme tun genau das — sie platzieren SIP und H.323 in der "Sitzungsschicht" und die Codecs in der "Präsentationsschicht". Diese Zuordnung war schon immer umstritten. Die IETF, die SIP standardisiert, verwendet nicht das OSI-Modell; sie folgt dem älteren vier-schichtigen TCP/IP (DoD)-Modell, und RFC 3261 definiert **SIP als ein Protokoll der Anwendungsschicht**. Die Medien folgen dem gleichen Muster: RTP und die Codecs befinden sich in der Nutzlast der Anwendung und werden über UDP in der Transportschicht übertragen. Die folgende Tabelle ordnet die wichtigsten VoIP-Protokolle dem TCP/IP-Modell zu, das die IETF tatsächlich verwendet, wobei das grobe OSI-Äquivalent nur als Referenz dient.

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

QoS-Mechanismen wie DiffServ arbeiten auf der IP-Schicht, um Sprachpakete zu priorisieren und die Anrufqualität zu verbessern. Einige Protokollspezifika:

- **SIP** verwendet UDP oder TCP auf Port 5060 (TLS auf 5061) zur Übertragung der Signalisierung. Das Audio wird separat per RTP über einen konfigurierbaren UDP-Portbereich übertragen (Asterisk's ausgeliefertes `rtp.conf` Beispiel verwendet 10000 bis 20000), kodiert mit einem Codec wie G.711.
- **H.323** überträgt die Anrufsignalisierung über TCP (H.225-Anrufsignalisierung auf Port 1720), während der H.225-RAS-Kanal UDP auf Port 1719 verwendet; RTP transportiert das Audio.
- **IAX2** ist ungewöhnlich: Es bündelt sowohl Signalisierung als auch Medien über einen einzigen UDP-Port (4569), was die NAT- und Firewall-Durchquerung vereinfacht.

> **[2nd-ed note]** Die Abbildung der 1. Auflage ordnete SIP/H.323 der OSI-*Sitzungsschicht* und die Codecs der *Präsentationsschicht* zu. Diese Zuordnung war eine langjährige Quelle der Kontroverse — die IETF verwendet das TCP/IP-Modell, in dem SIP ein Protokoll der Anwendungsschicht ist — daher wurde die Abbildung durch die obige Tabelle ersetzt. Beauftragen Sie eine neu gezeichnete Abbildung auf Basis des TCP/IP-Stacks, falls eine visuelle Darstellung gewünscht ist.

## How to choose a protocol

Wie können Sie angesichts der vielen Protokolle das beste für Ihr Netzwerk auswählen? In diesem Abschnitt werden wir die Vor- und Nachteile jedes Protokolls hervorheben.

### SIP - Session Initiated Protocol

SIP ist ein offener Standard der Internet Engineering Task Force (IETF), der weitgehend in RFC 3261 definiert ist. Die meisten modernen VoIP-Anbieter verwenden SIP; tatsächlich wird es zum populärsten VoIP-Standard. Die Stärke von SIP liegt darin, dass es ein IETF-basierter Standard ist. SIP ist im Vergleich zum älteren H.323 leichtgewichtig. Die Hauptschwäche von SIP ist die NAT-Durchquerung — eine Herausforderung für die meisten SIP-VoIP-Anbieter. Die IETF hat SIP nicht mit Blick auf die Abrechnung entwickelt, sondern für die offene Kommunikation zwischen Peers. Die Abrechnung ist normalerweise ein Anliegen von VoIP-Anbietern.

### IAX – Inter Asterisk eXchange

IAX ist ein offenes Protokoll, das ursprünglich von Digium (jetzt Sangoma) entwickelt wurde. IAX ist ein All-in-One-Protokoll, da es Signalisierung und Medien über denselben UDP-Port (4569) transportiert. Mark Spencer entwickelte IAX als binäres Protokoll für reduzierte Bandbreite. Die Hauptstärke von IAX ist die reduzierte Bandbreitennutzung (es verwendet kein RTP); es ist auch sehr einfach für die NAT- und Firewall-Durchquerung, da es nur einen UDP-Port (4569) verwendet. Wenn ein traditioneller PBX-Hersteller IAX entwickelt hätte, hätte er das Protokoll wahrscheinlich als „das Beste seit Speiseeis“ vermarktet; in manchen Situationen kann IAX im Trunk-Modus die Sprachbandbreitennutzung um ein Drittel reduzieren. IAX2 (Version 2) wird in Asterisk 22 weiterhin über das `chan_iax2` Modul ausgeliefert und bleibt nützlich für Asterisk-zu-Asterisk-Trunks, obwohl es als Legacy gilt; SIP/PJSIP wird für neue Implementierungen bevorzugt. IAX2 ist in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational) spezifiziert.

### MGCP – Media Gateway Control Protocol

MGCP ist ein Protokoll, das in Verbindung mit H.323, SIP und IAX verwendet wird. Sein größter Vorteil ist die Skalierbarkeit. Es wird im Call-Agent anstatt in den Gateways konfiguriert. Dies vereinfacht den Konfigurationsprozess und ermöglicht eine zentralisierte Verwaltung. Die Asterisk-Implementierung ist jedoch nicht vollständig, und es scheint, dass nicht viele Leute es verwenden.

### H.323

H.323 wird weitgehend in VoIP verwendet. Es ist eines der ersten VoIP-Protokolle und ist für die Verbindung älterer VoIP-Infrastrukturen auf Gateway-Basis unerlässlich. H.323 ist immer noch der Standard auf dem Gateway-Markt, obwohl der Markt langsam zu SIP migriert. Zu den Stärken von H.323 gehören die große Marktakzeptanz und Reife. Die Schwächen von H.323 hängen mit der Komplexität der Implementierung und den mit den Standardisierungsgremien verbundenen Kosten zusammen.

### Protocol comparison table

Die folgende Tabelle fasst die Unterschiede zwischen den Sitzungsprotokollen zusammen.

| Protocol | Standard body | Used for |
|----------|---------------|----------|
| SIP | IETF standard | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | MGCP phones (no provider/gateway support) |
| SCCP | Cisco proprietary | Cisco phones |

> **[2nd-ed note]** Erwägen Sie, diese Tabelle zu aktualisieren, um die aktuellen Asterisk 22-Modulnamen und den Unterstützungsstatus widerzuspiegeln.

## Peers, Users, and Friends

Es gibt drei Arten von SIP- und IAX-Clients. Der erste ist „User“. User können Anrufe an einen Asterisk-Server tätigen, aber sie können keine Verbindung herstellen, um Anrufe von diesem Server zu empfangen. Der zweite ist ein „Peer“. Sie können Anrufe an einen Peer tätigen, aber Sie werden keine Anrufe von ihm empfangen. Normalerweise benötigt ein Server oder ein Gerät beide Konzepte gleichzeitig. Ein „Friend“ ist eine Abkürzung für „User“ + „Peer“. Ein Telefon würde wahrscheinlich in diese Kategorie fallen, da es benötigt wird, um Anrufe zu tätigen und zu empfangen.

![Peer, user, and friend from Asterisk's point of view: a "user" places calls to Asterisk, a "peer" receives calls from Asterisk, and a "friend" does both.](../images/06-voip-network-fig03.png)

> **[2nd-ed note]** Die Unterscheidung zwischen Peer/User/Friend ist ein `chan_sip` (`sip.conf`) Konzept. In PJSIP (`pjsip.conf`) wird dies durch das **endpoint**-Objekt ersetzt, das sowohl eingehende als auch ausgehende Anrufe verarbeitet. Die Trennung zwischen Peer und User gilt in Asterisk 22 nicht mehr.

## Codecs and codec translation

Sie verwenden einen Codec, um die Sprache von einer analogen Welle in ein digitales Signal umzuwandeln. Codecs unterscheiden sich voneinander in Aspekten wie Klangqualität, Kompressionsrate, Bandbreite und Rechenanforderungen. Dienste, Telefone und Gateways unterstützen normalerweise mehrere dieser Aspekte. Der Codec G.729 ist sehr beliebt. Er ist nicht Teil des Standard-Asterisk 22-Builds; stattdessen wird er als externes Add-on-Modul (`codec_g729`) ausgeliefert, das Sie von Digium (jetzt Sangoma) herunterladen. Asterisk's `menuselect` Quelle listet es mit `support_level=external` auf und merkt deutlich an: "Download the g729a codec from Digium. A license must be purchased for this codec." Mit anderen Worten, die rechtmäßige Nutzung von G.729 erfordert eine gekaufte Lizenz pro Kanal. (Eine Open-Source-Alternative, `bcg729`, existiert ebenfalls.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 unterstützt (unter anderem) die folgenden Codecs:

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — Standard PSTN-Qualität; ulaw üblich in Nordamerika, alaw üblich in Europa und Lateinamerika
- ITU G.722: 64 Kbps — Breitband (HD-Sprache), gute Qualität bei gleicher Bandbreite wie G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — externes `codec_g729` Binärmodul, heruntergeladen von Digium/Sangoma (`support_level=external`; eine Lizenz muss erworben werden, um es zu nutzen)
- Speex: 2.15 bis 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variabel — moderner Breitband-/Fullband-Codec; exzellente Qualität und Widerstandsfähigkeit gegen Paketverlust; bereitgestellt als externes `codec_opus` Binärmodul, heruntergeladen von Digium/Sangoma (`support_level=external`; kein Lizenzkauf vermerkt, im Gegensatz zu G.729); empfohlen für WebRTC und moderne SIP-Endpoints. (Open-Source-Build-Alternativen existieren auf GitHub.)

Darüber hinaus erlaubt Asterisk die Übersetzung zwischen Codecs. In einigen Fällen ist dies nicht möglich, wie im Fall von g723, das nur im Pass-thru-Modus unterstützt wird. Die Übersetzung von einem Codec in einen anderen verbraucht viele CPU-Ressourcen. Vermeiden Sie dies daher nach Möglichkeit vollständig.

## How to choose a Codec

Die Codec-Auswahl hängt von mehreren Optionen ab, wie zum Beispiel:

- Klangqualität
- Lizenzkosten
- CPU-Verarbeitungsauslastung
- Bandbreitenanforderungen
- Verschleierung von Paketverlusten
- Verfügbarkeit für Asterisk und Telefongeräte

Die folgende Tabelle vergleicht die populärsten Codecs. Die Qualität dieser Codecs gilt als „toll“ — mit anderen Worten, ähnlich wie PSTN.

| Codec | G.711 | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|
| Sample interval | 20 ms | 30 ms | 30 ms | RTE/LTP |
| Bandwidth (Kbps) | 64 | 8 | 13.33 | 13 |
| Cost (per channel) | Free | ~USD 10.00 | Free | Free |
| Resistance to frame erasure¹ | None | 3% | 5% | 3% |
| Complexity (MIPS)² | ~0.35 | ~13 | ~18 | ~5 |

¹ Die Widerstandsfähigkeit gegen Paketverlust bezieht sich auf die Rate, bei der der MOS um etwa 0,5 unter die Spitzenqualität für den spezifischen Codec fällt.

² Komplexität bezieht sich auf die Menge in Millionen von Befehlen pro Sekunde, die für die Kodierung und Dekodierung des Codecs unter Verwendung eines Referenzdesigns auf einem Texas Instruments DSP (TMS320C54x) aufgewendet wird. Es besteht eine direkte Beziehung zwischen Prozessorfrequenz und MIPS, aber es ist nicht möglich, eine präzise Beziehung zwischen solch unterschiedlichen Hardwareplattformen herzustellen. Verwenden Sie diese Tabelle nur zum Vergleich.

> **[2nd-ed note]** Erstellen Sie diese Vergleichstabelle für die 2. Auflage neu: Fügen Sie Opus (kostenlos `codec_opus`) und G.722 (Breitband, 64 Kbps) hinzu; behalten Sie G.711 ulaw/alaw als PSTN-Basislinie bei. Beachten Sie bei G.729 die Lizenzrealität — Sangomas `codec_g729` ist kostenlos herunterladbar, erfordert aber eine Lizenz pro Kanal; das Open-Source-`bcg729` ist eine Alternative.

**Codec-Empfehlungen für Asterisk 22:**

- **G.711 (ulaw/alaw):** Verwendung für PSTN-Trunks und maximale Interoperabilität; null Transcoding-Kosten innerhalb von Asterisk.
- **G.729:** Nützlich für WAN-Trunks mit geringer Bandbreite; Sangomas `codec_g729` Modul ist kostenlos herunterladbar, erfordert aber eine gekaufte Lizenz pro Kanal zur Nutzung.
- **G.722:** Gute Wahl für Breitband (HD-Sprache) in LAN/internen Nebenstellen; gleiche Bandbreite wie G.711 bei besserer Qualität.
- **Opus:** Empfohlen für moderne Endpunkte, WebRTC-Clients und jede Implementierung, bei der der Endpunkt dies unterstützt. Adaptive Bitrate, exzellente Widerstandsfähigkeit gegen Paketverlust, frei verfügbar über Sangomas `codec_opus` Binärmodul.

## Overhead caused by protocol headers

Obwohl Codecs wenig Bandbreite verbrauchen, müssen wir den Overhead durch Protokoll-Header wie Ethernet, IP, UDP und RTP berücksichtigen. Daher könnten wir sagen, dass die Bandbreite von den verwendeten Headern abhängt. Wenn wir uns in einem Ethernet-Netzwerk befinden, ist der Bandbreitenbedarf höher als in einem PPP-Netzwerk, da der PPP-Header kürzer ist als der Ethernet-Header. Schauen wir uns einige Beispiele an: Ethernet Destination G.729 coded (20) UDP Header (8) Ethernet Type (2) Ethernet Source IP Header (20) RTP Header (12) Voice Payload Checksum (4) Address (6) Address (6) Ethernet Codec g.711 (64 Kbps)

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Sie können andere Bandbreitenanforderungen einfach mit einem Online-VoIP-Bandbreitenrechner wie <https://www.voip.school/bandcalc/bandcalc.php> berechnen.


## Traffic Engineering

Ein Hauptproblem beim Entwurf von VoIP-Netzwerken ist die Dimensionierung der Anzahl der Leitungen und der erforderlichen Bandbreite zu einem bestimmten Ziel, wie einer Außenstelle oder einem Dienstanbieter. Es ist auch wichtig, die Anzahl der gleichzeitigen Anrufe von Asterisk zu dimensionieren (Hauptparameter für die Dimensionierung von Asterisk).

### Simplifications

Die primäre und am weitesten verbreitete Vereinfachung besteht darin, die Anzahl der Anrufe nach Benutzertyp zu schätzen. Zum Beispiel:

- Business-PBXs (ein gleichzeitiger Anruf für alle fünf Nebenstellen)
- Privatnutzer (ein gleichzeitiger Anruf für alle sechzehn Benutzer)

Beispiel #1 Der Hauptsitz des Unternehmens hat 120 Nebenstellen und zwei Zweigstellen — die erste mit 30 Nebenstellen und die zweite mit 15 Nebenstellen. Unser Ziel ist es, die Anzahl der E1-Trunks im Hauptsitz und die für das Frame-Relay-Netzwerk erforderliche Bandbreite zu dimensionieren.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Anzahl der T1-Leitungen

- Gesamtzahl der Nebenstellen, die T1-Leitungen nutzen: 120+30+15=165 Leitungen
- Verwendung eines Trunks für alle fünf Nebenstellen für den geschäftlichen Gebrauch
- Gesamtzahl der Leitungen = 33 oder ungefähr 2xT1-Leitungen

1b Bandbreitenanforderungen Wir wählen den g.729-Codec aufgrund der Bandbreitenanforderungen, der Klangqualität und des mittleren CPU-Verbrauchs.

Mit einem Trunk für alle fünf Nebenstellen:

- Erforderliche Bandbreite für Zweigstelle #1 (Frame-relay): 26.8*6=160.8 Kbps
- Erforderliche Bandbreite für Zweigstelle #2 (Frame-relay): 26.8*3= 80.4 Kbps

### Erlang B method

1.a Anzahl der gleichzeitigen VoIP-Anrufe Manchmal ist Vereinfachung nicht der beste Ansatz. Wenn Sie über Daten aus der Vergangenheit verfügen, können Sie einen wissenschaftlicheren Ansatz wählen. Wir verwenden die Arbeit von Agner Karup Erlang (Copenhagen Telephone Company, 1909), der eine Formel zur Berechnung von Leitungen in einer Trunk-Gruppe zwischen zwei Städten entwickelte. Erlang ist eine Verkehrsmessungseinheit, die normalerweise in der Telekommunikation vorkommt. Sie wird verwendet, um das Verkehrsaufkommen für eine Stunde zu beschreiben. Zum Beispiel: 20 Anrufe finden in einer Stunde statt, mit durchschnittlich 5 Minuten Gesprächsdauer. Sie können die Anzahl der Erlangs wie folgt berechnen: Verkehrsminuten in der Stunde: 20 x 5 = 100 Minuten Verkehrsaufkommen innerhalb einer Stunde: 100/60 = 1.66 Erlangs. Sie können diese Messungen aus einem Anrufprotokoll bestimmen und damit Ihr Netzwerk entwerfen, um die Anzahl der erforderlichen Leitungen zu berechnen. Sobald die Anzahl der Leitungen bekannt ist, ist es möglich, die Bandbreitenanforderungen zu berechnen. Erlang B ist die am häufigsten verwendete Methode zur Berechnung der Anzahl der Leitungen in einer Trunk-Gruppe. Sie geht davon aus, dass Anrufe zufällig eintreffen (Poisson-Verteilung), während blockierte Anrufe sofort gelöscht werden. Diese Methode erfordert, dass Sie den Busy Hour Traffic (BHT) kennen, den Sie aus einem Anrufprotokoll oder durch die folgende Vereinfachung erhalten können: BHT=17% der Anrufminuten eines Tages.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Eine weitere wichtige Variable ist die Grade of Service (GoS), die die Wahrscheinlichkeit definiert, Anrufe aufgrund von Leitungsmangel zu blockieren. Sie können diesen Parameter festlegen, der normalerweise 0.05 (5% Anrufe verloren) oder 0.01 (1% Anrufe verloren) beträgt. Beispiel #1: Unter Verwendung desselben Beispiels aus 5.10.1 geben wir Ihnen einige Daten zu Verkehrsmustern. Aus dem Anrufprotokoll haben wir diese Daten entdeckt: Daten aus dem Anrufprotokoll (Anrufminuten und BHT):

- Hauptsitz zu Zweigstelle #1 = 2.000 Minuten, BHT = 300 Minuten
- Hauptsitz zu Zweigstelle #2 = 1.000 Minuten, BHT = 170 Minuten
- Zweigstelle #1 zu Zweigstelle #2 = 0, BHT=0

Lassen Sie uns GoS=0.01 festlegen

- Hauptsitz zu Zweigstelle #1 - BHT=300 Minuten/60 = 5 Erlangs
- Hauptsitz zu Zweigstelle #2 – BHT=170 Minuten/60 = 2.83 Erlangs

Unter Verwendung eines Erlang-Rechners wie <https://www.erlang.com>

- Für den Hauptsitz zu Zweigstelle #1 sind 11 Leitungen erforderlich.
- Für den Hauptsitz zu Zweigstelle #2 sind 8 Leitungen erforderlich

1.b Erforderliche Bandbreite Wir verwenden ein WAN, in dem Paketverlust selten ist. Wir wählen den g729-Codec aufgrund seiner guten Klangqualität und Datenkompression (8 Kbps).

Ausgewählter Codec: g729 Datalink-Schicht: Frame-Relay

- Geschätzte Sprachbandbreite für Zweigstelle #1: 26.8x11 = 294.8 Kbps
- Geschätzte Sprachbandbreite für Zweigstelle #2: 26.8x8 = 214.40 Kbps

## Reducing the bandwidth required for VoIP

Drei Methoden können verwendet werden, um die für VoIP-Anrufe erforderliche Bandbreite zu reduzieren:

- RTP-Header-Kompression
- IAX Trunked
- VoIP-Nutzlast

### RTP Header Compression

In Frame-Relay- und PPP-Netzwerken können Sie RTP-Header-Kompression verwenden. RTP-Header-Kompression wurde in RFC 2508 definiert. Es ist ein IETF-Standard, der in mehreren Routern verfügbar ist. Seien Sie jedoch vorsichtig, da einige Router ein anderes Funktionsset erfordern, damit diese Ressource verfügbar ist. Die Auswirkungen der Verwendung von RTP-Header-Kompression sind fabelhaft, da sie die in unserem Beispiel erforderliche Bandbreite von 26.8 Kbps pro Sprachkonversation auf 11.2 Kbps reduziert — eine Reduzierung um 58.2%!

### IAX2 trunk mode

Wenn Sie zwei Asterisk-Server verbinden, können Sie das IAX2-Protokoll im Trunk-Modus verwenden. Diese revolutionäre Technologie benötigt keine speziellen Router und kann auf jede Art von Datenverbindung angewendet werden.

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

Der IAX2-Trunk-Modus verwendet dieselben Header ab dem zweiten Anruf wieder. Bei Verwendung von g729 in einer PPP-Verbindung verbraucht der erste Anruf 30 Kbps Bandbreite, während der zweite Anruf denselben Header wie der erste verwendet und die notwendige Bandbreite für den zusätzlichen Anruf auf 9.6 Kbps reduziert. Wir können die erforderliche Bandbreite im Trunk-Modus wie folgt berechnen: Zweigstelle #1 (11 Anrufe) Bandbreite = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Zweigstelle #2 (8 Anrufe) Bandbreite = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps Der erste Anruf verbraucht 31.2 Kbps, der nächste 9.6, und so weiter.

### Increasing the Voice Payload

Diese Methode ist sehr verbreitet, wenn VoIP-Gateways über das Internet verwendet werden. Bei Verwendung einer größeren Nutzlast opfern Sie Latenz zugunsten einer reduzierten Bandbreite. Sie können die RTP-Paketierung ändern, indem Sie die Rahmengröße an den Codec in der allow-Anweisung anhängen.

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

Beispiel:

```
allow=ulaw:30
```

Die zulässigen Werte sind: Name Min Max Default Increment g723 gsm ulaw alaw g726 ADPCM SLIN lpc10 g729 speex ilbc

## Summary

In diesem Kapitel haben Sie gelernt, dass Asterisk VoIP unter Verwendung von Kanälen behandelt. Es unterstützt SIP (via `chan_pjsip` in Asterisk 22) und IAX2; H.323 ist nur über das Community-`ooh323` Add-on verfügbar, und die älteren MGCP- und SCCP (Skinny)-Kanäle sind nicht mehr Teil eines Standard-Asterisk 22-Builds. Sie haben verglichen und gelernt, wie man ein Signalisierungsprotokoll und einen Codec für VoIP-Kanäle auswählt. IAX2 ist bandbreiteneffizienter und kann NAT leicht durchqueren. SIP/PJSIP ist das von Drittanbietern für Telefone und Gateways am meisten unterstützte Protokoll und der einzige SIP-Kanaltreiber in Asterisk 22. Das H.323-Protokoll ist das älteste und sollte verwendet werden, um eine Verbindung zu Legacy-VoIP-Infrastrukturen herzustellen. In Abschnitt 5.11 haben wir gelernt, wie man ein VoIP-Netzwerk entwirft und dimensioniert.

## Quiz

1. Welche der folgenden Punkte sind Vorteile von VoIP, die in diesem Kapitel beschrieben wurden (kreuzen Sie alle zutreffenden an)?
   - A. Konvergenz von Daten- und Sprachnetzwerken zur Kostensenkung
   - B. Niedrigere Infrastrukturkosten für Erweiterungen, Entfernungen und Änderungen
   - C. Offene Standards, die Sie von einem einzigen Anbieter befreien
   - D. Einfachere und billigere Computer-Telefonie-Integration
   - E. Garantierte niedrigere Minutenpreise als bei jeder Telefongesellschaft
2. Konvergenz ist die Integration von Sprache, Daten und Video in einem einzigen Netzwerk; ihr Hauptvorteil ist die Kostensenkung bei der Implementierung und Wartung getrennter Netzwerke.
   - A. False
   - B. True
3. Asterisk behandelt jedes VoIP-Protokoll als Kanal und kann jeden Kanaltyp mit jedem anderen verbinden, wobei bei Bedarf zwischen Codecs transkodiert wird.
   - A. False
   - B. True
4. In Asterisk 22 wird SIP von welchem Kanaltreiber verarbeitet?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In dem TCP/IP (IETF)-Modell, auf dem SIP in RFC 3261 tatsächlich definiert ist, arbeiten die Signalisierungsprotokolle SIP, H.323 und IAX2 auf der ___ Schicht.
   - A. Präsentation
   - B. Anwendung
   - C. Physisch
   - D. Sitzung
   - E. Datenverbindung
6. SIP ist das am häufigsten übernommene Protokoll für IP-Telefone und ein offener Standard, der weitgehend von der IETF in RFC 3261 definiert wurde.
   - A. False
   - B. True
7. IAX2 transportiert sowohl Signalisierung als auch Medien über einen einzigen UDP-Port, was es effizient und einfach für die NAT-Durchquerung macht. Welchen UDP-Port verwendet IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX wurde ursprünglich von Digium (jetzt Sangoma) entwickelt. Trotz begrenzter Akzeptanz durch Telefonhersteller ist IAX exzellent, wenn Sie (kreuzen Sie alle zutreffenden an):
   - A. Die Bandbreitennutzung reduzieren müssen (es verwendet kein RTP)
   - B. Ein Video-Medienformat benötigen
   - C. Einfache NAT- und Firewall-Durchquerung benötigen
   - D. Den Trunk-Modus benötigen, um viele Asterisk-zu-Asterisk-Anrufe zu kombinieren und den Header-Overhead zu amortisieren
9. Im Legacy-Modell chan_sip kann ein "User" Anrufe von Asterisk empfangen.
   - A. False
   - B. True
10. Bezüglich Codecs in Asterisk 22, kreuzen Sie alle wahren Aussagen an:
    - A. G.711 entspricht PCM und verbraucht 64 Kbps Bandbreite.
    - B. Sangomas codec_g729-Modul ist kostenlos herunterladbar, aber die rechtmäßige Nutzung erfordert eine gekaufte Lizenz pro Kanal.
    - C. GSM ist beliebt, weil es etwa 13 Kbps verbraucht und keine Lizenz benötigt.
    - D. G.711 u-law ist in Nordamerika üblich, während a-law in Europa und Lateinamerika üblich ist.
    - E. G.729 ist leichtgewichtig und verbraucht im Vergleich zu G.711 sehr wenige CPU-Ressourcen zum Kodieren und Dekodieren.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Anwendung — SIP ist ein Protokoll der Anwendungsschicht im TCP/IP-Modell, das die IETF verwendet) · 6 — B · 7 — C · 8 — A, C, D · 9 — A · 10 — A, B, C, D
