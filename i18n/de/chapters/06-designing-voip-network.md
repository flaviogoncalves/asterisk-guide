# Designing a VoIP network

Voice over IP wächst schnell auf dem Telefonie-Markt. Das Konvergenz-Paradigma verändert die Art und Weise, wie wir kommunizieren, senkt Kosten und verbessert den Informationsaustausch. Sprache ist nur der Anfang einer Ära der vollständigen Multimedia-Kommunikation, die Sprache, Video und Präsenz umfasst. In der Zukunft werden wir nicht mehr Menschen zur Arbeit transportieren, sondern die Arbeit zu den Menschen bringen, da dies sauberer, schneller und kostengünstiger ist. VoIP ist nur ein Teil dieser Revolution. Unsere Herausforderung in diesem Kapitel ist der Entwurf eines VoIP-Netzwerks. Dazu müssen wir Konzepte wie Sitzungsprotokolle und Codecs verstehen sowie wissen, wie man die Anzahl der Leitungen und die Bandbreite dimensioniert.

## Objectives

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die Vorteile von VoIP zu verstehen
- Zu beschreiben, wie Asterisk VoIP handhabt
- Die Konzepte der SIP- und IAX-Kanäle zu beschreiben
- Das am besten geeignete Protokoll für einen spezifischen Datenkanal auszuwählen
- Den am besten geeigneten Codec für einen spezifischen Datenkanal auszuwählen
- Die erforderliche Anzahl an Kanälen zu dimensionieren
- Die erforderliche Bandbreite zu berechnen

## VoIP benefits

Warum sollten Sie sich für VoIP interessieren? VoIP bietet sowohl Unternehmen als auch Privatpersonen Vorteile. Kostensenkung ist sicherlich einer davon, aber in einigen Umgebungen vereinfacht VoIP die Integration von Computersystemen. Einige der Vorteile sind hier detailliert aufgeführt:

### Convergence

Der Hauptvorteil von VoIP ist die Kombination von Daten- und Sprachnetzwerken zur Kostensenkung (Konvergenz). Die Analyse der reinen Gesprächsminutenkosten reicht jedoch möglicherweise nicht aus, um die Einführung von VoIP zu rechtfertigen. Der Preis für Minuten, die von Telefongesellschaften verkauft werden, sinkt schnell und ist etwas, das vor der Einführung von VoIP berücksichtigt werden sollte.

### Infrastructure costs

Die Nutzung einer einzigen Netzwerkinfrastruktur reduziert die Kosten, die mit Erweiterungen, Entfernungen und Änderungen verbunden sind. Da IP allgegenwärtig geworden ist, hat es VoIP-bezogene Technologie auf viele neue Geräte gebracht, wie Mobiltelefone, PDAs, eingebettete Systeme und Laptops.

### Open Standards

Schließlich bieten die offenen Standards, auf denen VoIP aufbaut, die Freiheit, zwischen verschiedenen Anbietern zu wählen. Dieser einzelne Vorteil macht den Kunden zum König, anstatt ihn von TELCOS und PBX-Herstellern abhängig zu machen.

### Computer Telephony Integration

Telefonie ist weitaus älter als die Informatik. Telefonie-PBXs basieren auf Leitungsvermittlung, und man hat normalerweise nicht mehr als einen Computer zur Überwachung. Mit VoIP wird Telefonie von Grund auf auf Basis von Computerstandards erstellt. Dies macht die Nutzung von Computer-Telefonie-Anwendungen billiger und einfacher als im alten Modell. Sie können schnell eine lange Liste von Telefonie-Anwendungen auf Basis von Asterisk erstellen. Sie können IVRs, ACDs, CTI, Dialer, Screen-Popups und andere Anwendungen in einem Bruchteil der Zeit entwickeln, die für herkömmliche PBXs erforderlich wäre.

## Asterisk VoIP architecture

Die Architektur von Asterisk ist unten dargestellt. Asterisk behandelt alle VoIP-Protokolle als Kanäle. Sie können jeden Codec oder jedes Protokoll verwenden. Das hier zu lernende Konzept ist, dass Asterisk jede Art von Kanal mit jeder anderen verbindet. Somit können Sie Signalisierungsprotokolle wie SIP und IAX ineinander übersetzen, sogar mit unterschiedlichen Codecs. Zum Beispiel können Sie einen Anruf von einem SIP-Telefon im lokalen Netzwerk mit dem G.711-Codec zu einem SIP-Trunk zu Ihrem VoIP-Anbieter mit dem G.729-Codec übersetzen. In den nächsten Kapiteln werden wir die Details der SIP- und IAX-Architektur erläutern. H.323-Unterstützung (über das Add-on chan_ooh323) ist verfügbar, aber zunehmend selten; SIP/PJSIP ist der Standard für moderne Implementierungen.

![Asterisk's modular architecture: applications and channels connect to the PBX switch core through APIs, with codec translation and file-format modules loaded dynamically.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP verwendet eine Reihe verschiedener Protokolle, die zusammenarbeiten. Es ist verlockend, sie dem Sieben-Schichten-OSI-Referenzmodell gegenüberzustellen, und viele ältere Diagramme tun genau das — sie platzieren SIP und H.323 in der "Sitzungs"-Schicht und die Codecs in der "Präsentations"-Schicht. Diese Zuordnung war schon immer umstritten. Die IETF, die SIP standardisiert, verwendet nicht das OSI-Modell; sie folgt dem älteren vier-schichtigen TCP/IP (DoD)-Modell, und RFC 3261 definiert **SIP als ein Protokoll der Anwendungsschicht**. Die Medien folgen dem gleichen Muster: RTP und die Codecs leben in der Anwendungsnutzlast, übertragen über UDP in der Transportschicht. Die folgende Tabelle ordnet die wichtigsten VoIP-Protokolle dem TCP/IP-Modell zu, das die IETF tatsächlich verwendet, wobei das grobe OSI-Äquivalent nur als Referenz dient.

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

QoS-Mechanismen wie DiffServ arbeiten auf der IP-Schicht, um Sprachpakete zu priorisieren und die Anrufqualität zu verbessern. Einige Protokollspezifika:

- **SIP** verwendet UDP oder TCP auf Port 5060 (TLS auf 5061), um die Signalisierung zu übertragen. Das Audio wird separat durch RTP über einen konfigurierbaren UDP-Portbereich übertragen (Asterisk's shipped `rtp.conf` sample uses 10000 to 20000), kodiert mit einem Codec wie G.711.
- **H.323** überträgt die Anrufsignalisierung über TCP (H.225-Anrufsignalisierung auf Port 1720), während der H.225 RAS-Kanal UDP auf Port 1719 verwendet; RTP transportiert das Audio.
- **IAX2** ist ungewöhnlich: Es bündelt sowohl Signalisierung als auch Medien über einen einzigen UDP-Port (4569), was die NAT- und Firewall-Durchquerung vereinfacht.

> **[2nd-ed note]** The 1st-edition figure here mapped SIP/H.323 onto the OSI *session*
> layer and the codecs onto the *presentation* layer. That mapping was a long-standing
> source of controversy — the IETF uses the TCP/IP model, in which SIP is an
> application-layer protocol — so the figure has been replaced by the table above.
> Commission a redrawn figure based on the TCP/IP stack if a visual is desired.

## How to choose a protocol

Angesichts der vielen Protokolle, wie wählen Sie das beste für Ihr Netzwerk aus? In diesem Abschnitt werden wir die Vor- und Nachteile jedes Protokolls hervorheben.

### SIP - Session Initiated Protocol

SIP ist ein offener Standard der Internet Engineering Task Force (IETF), der weitgehend in RFC 3261 definiert ist. Die meisten modernen VoIP-Anbieter verwenden SIP; tatsächlich wird es zum populärsten VoIP-Standard. Die Stärke von SIP ist, dass es ein IETF-basierter Standard ist. SIP ist leicht im Vergleich zum älteren H.323. Die Hauptschwäche von SIP ist die NAT-Durchquerung — eine Herausforderung für die meisten SIP-VoIP-Anbieter. Die IETF hat SIP nicht mit Blick auf die Abrechnung entwickelt, sondern für offene Kommunikation zwischen Peers. Abrechnung ist normalerweise ein Anliegen für VoIP-Anbieter.

### IAX – Inter Asterisk eXchange

IAX ist ein offenes Protokoll, das ursprünglich von Digium (jetzt Sangoma) entwickelt wurde. IAX ist ein All-in-One-Protokoll, da es Signalisierung und Medien über denselben UDP-Port (4569) transportiert. Mark Spencer entwickelte IAX als binäres Protokoll für reduzierte Bandbreite. Die Hauptstärke von IAX ist seine reduzierte Bandbreitennutzung (es verwendet kein RTP); es ist auch sehr einfach für NAT- und Firewall-Durchquerung, da es nur einen UDP-Port (4569) verwendet. Wenn ein traditioneller PBX-Hersteller IAX entwickelt hätte, hätte er das Protokoll wahrscheinlich als „das Beste seit Speiseeis“ vermarktet; in manchen Situationen kann IAX im Trunk-Modus die Sprachbandbreitennutzung um ein Drittel reduzieren. IAX2 (Version 2) wird in Asterisk 22 weiterhin über das `chan_iax2` Modul ausgeliefert und bleibt nützlich für Asterisk-zu-Asterisk-Trunks, obwohl es als veraltet gilt; SIP/PJSIP wird für neue Implementierungen bevorzugt. IAX2 ist in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational) spezifiziert.

### MGCP – Media Gateway Control Protocol

MGCP ist ein Protokoll, das in Verbindung mit H.323, SIP und IAX verwendet wird. Sein größter Vorteil ist die Skalierbarkeit. Es wird im Call-Agent anstatt in den Gateways konfiguriert. Dies vereinfacht den Konfigurationsprozess und ermöglicht eine zentralisierte Verwaltung. Die Asterisk-Implementierung ist jedoch nicht vollständig, und es scheint, dass nicht viele Leute es verwenden.

### H.323

H.323 wird weitgehend in VoIP verwendet. Es ist eines der ersten VoIP-Protokolle und ist wesentlich für die Verbindung älterer VoIP-Infrastrukturen, die auf Gateways basieren. H.323 ist immer noch der Standard auf dem Gateway-Markt, obwohl der Markt langsam zu SIP migriert. Zu den Stärken von H.323 gehören die große Marktakzeptanz und Reife. Die Schwächen von H.323 hängen mit der Komplexität der Implementierung und den mit den Standardisierungsgremien verbundenen Kosten zusammen.

### Protocol comparison table

Die folgende Tabelle fasst die Unterschiede zwischen den Sitzungsprotokollen zusammen.

| Protocol | Standard body | Used for |
|----------|---------------|----------|
| SIP | IETF standard | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | MGCP phones (no provider/gateway support) |
| SCCP | Cisco proprietary | Cisco phones |

> **[2nd-ed note]** Consider refreshing this table to reflect current Asterisk 22 module names and support status.

## One endpoint per device

In Asterisk 22 modelliert der PJSIP-Stack jedes Telefon, jeden Trunk oder jedes Gateway als ein einziges **endpoint**-Objekt in `pjsip.conf`. Ein Endpoint tätigt und empfängt Anrufe; seine Anmeldedaten leben in einem `auth`-Objekt, seine registrierte Adresse in einem `aor` und sein Netzwerkpfad in einem `transport`. Sie konfigurieren einen Endpoint pro Gerät und fügen die benötigten Teile hinzu — es gibt keine separate "User"- versus "Peer"-Rolle, über die man nachdenken muss. (Das vollständige Objektmodell wird in *SIP and PJSIP* behandelt.)

## Codecs and codec translation

Sie verwenden einen Codec, um die Sprache von einer analogen Welle in ein digitales Signal umzuwandeln. Codecs unterscheiden sich voneinander in Aspekten wie Klangqualität, Kompressionsrate, Bandbreite und Rechenanforderungen. Dienste, Telefone und Gateways unterstützen normalerweise mehrere dieser Aspekte. Der Codec G.729 ist sehr beliebt. Er ist nicht Teil des Standard-Asterisk 22-Builds; stattdessen wird er als externes Add-on-Modul (`codec_g729`) ausgeliefert, das Sie von Digium (jetzt Sangoma) herunterladen. Asterisk's `menuselect`-Quelle listet es mit `support_level=external` und merkt deutlich an: "Download the g729a codec from Digium. A license must be purchased for this codec." Mit anderen Worten, eine rechtmäßige G.729-Nutzung erfordert eine gekaufte Lizenz pro Kanal. (Eine Open-Source-Alternative, `bcg729`, existiert ebenfalls.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 unterstützt die folgenden Codecs (unter anderem):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — standard PSTN quality; ulaw common in North America, alaw common in Europe and Latin America
- ITU G.722: 64 Kbps — wideband (HD voice), good quality at the same bandwidth as G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — external `codec_g729` binary module downloaded from Digium/Sangoma (`support_level=external`; a license must be purchased to use it)
- Speex: 2.15 to 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variable — modern wideband/fullband codec; excellent quality and packet-loss resilience; provided as an external `codec_opus` binary module downloaded from Digium/Sangoma (`support_level=external`; no license purchase noted, unlike G.729); recommended for WebRTC and modern SIP endpoints. (Open-source build alternatives exist on GitHub.)

Darüber hinaus erlaubt Asterisk die Übersetzung zwischen Codecs. In einigen Fällen ist dies nicht möglich, wie im Fall von g723, das nur im Pass-Thru-Modus unterstützt wird. Die Übersetzung von einem Codec in einen anderen verbraucht viele CPU-Ressourcen. Vermeiden Sie dies daher nach Möglichkeit vollständig.

## How to choose a Codec

Die Codec-Auswahl hängt von mehreren Optionen ab, wie:

- Klangqualität
- Lizenzkosten
- CPU-Verarbeitungsauslastung
- Bandbreitenanforderungen
- Paketverlustverschleierung
- Verfügbarkeit für Asterisk und Telefongeräte

Die folgende Tabelle vergleicht die populärsten Codecs. Die Qualität dieser Codecs wird als „toll“ betrachtet—mit anderen Worten, ähnlich wie PSTN.

| Codec | G.711 | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|
| Sample interval | 20 ms | 30 ms | 30 ms | RTE/LTP |
| Bandwidth (Kbps) | 64 | 8 | 13.33 | 13 |
| Cost (per channel) | Free | ~USD 10.00 | Free | Free |
| Resistance to frame erasure¹ | None | 3% | 5% | 3% |
| Complexity (MIPS)² | ~0.35 | ~13 | ~18 | ~5 |

¹ Resistance to packet loss refers to the rate at which the MOS drops to about 0.5 below the peak quality for the specific codec.

² Complexity refers to the quantity, in millions of instructions per second, spent to code and decode the codec using a reference design on a Texas Instruments DSP (TMS320C54x). A direct relationship exists between processor frequency and MIPS, but it is not possible to draw a precise relationship among such diverse hardware platforms. Use this table just for comparison.

> **[2nd-ed note]** Rebuild this comparison table for the 2nd edition: add Opus (free `codec_opus`) and G.722 (wideband, 64 Kbps); keep G.711 ulaw/alaw as the PSTN baseline. For G.729, note the licensing reality — Sangoma's `codec_g729` is free to download but requires a per-channel license; the open-source `bcg729` is an alternative.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

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

- Business-PBXs (ein gleichzeitiger Anruf für jeweils fünf Nebenstellen)
- Privatnutzer (ein gleichzeitiger Anruf für jeweils sechzehn Benutzer)

Example #1 Der Hauptsitz des Unternehmens hat 120 Nebenstellen und zwei Zweigstellen — die erste mit 30 Nebenstellen und die zweite mit 15 Nebenstellen. Unser Ziel ist es, die Anzahl der E1-Trunks im Hauptsitz und die für das Frame-Relay-Netzwerk erforderliche Bandbreite zu dimensionieren.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Number of T1 lines

- Gesamtzahl der Nebenstellen, die T1-Leitungen nutzen: 120+30+15=165 Leitungen
- Verwendung eines Trunks für jeweils fünf Nebenstellen für den geschäftlichen Gebrauch
- Gesamtzahl der Leitungen = 33 oder ungefähr 2xT1-Leitungen

1b Bandwidth requirements Wir wählen den g.729-Codec aufgrund der Bandbreitenanforderungen, der Klangqualität und des mittleren CPU-Verbrauchs.

Mit einem Trunk für jeweils fünf Nebenstellen:

- Erforderliche Bandbreite für Zweigstelle #1 (Frame-Relay): 26.8*6=160.8 Kbps
- Erforderliche Bandbreite für Zweigstelle #2 (Frame-Relay): 26.8*3= 80.4 Kbps

### Erlang B method

1.a Number of VoIP simultaneous calls Manchmal ist Vereinfachung nicht der beste Ansatz. Wenn Sie über frühere Daten verfügen, können Sie einen wissenschaftlicheren Ansatz wählen. Wir verwenden die Arbeit von Agner Karup Erlang (Copenhagen Telephone Company, 1909), der eine Formel zur Berechnung von Leitungen in einer Trunk-Gruppe zwischen zwei Städten entwickelte. Erlang ist eine Verkehrsmessungseinheit, die normalerweise in der Telekommunikation vorkommt. Sie wird verwendet, um das Verkehrsaufkommen für eine Stunde zu beschreiben. Zum Beispiel: 20 Anrufe finden in einer Stunde statt, mit durchschnittlich 5 Minuten Gesprächsdauer. Sie können die Anzahl der Erlangs wie folgt berechnen: Verkehrsminuten in der Stunde: 20 x 5 = 100 Minuten Stunde des Verkehrs innerhalb einer Stunde: 100/60 = 1.66 Erlangs Sie können diese Maße aus einem Anrufprotokoll bestimmen und sie verwenden, um Ihr Netzwerk zu entwerfen, um die Anzahl der erforderlichen Leitungen zu berechnen. Sobald die Anzahl der Leitungen bekannt ist, ist es möglich, die Bandbreitenanforderungen zu berechnen. Erlang B ist die am häufigsten verwendete Methode zur Berechnung der Anzahl der Leitungen in einer Trunk-Gruppe. Es wird davon ausgegangen, dass Anrufe zufällig eintreffen (Poisson-Verteilung), während blockierte Anrufe sofort gelöscht werden. Diese Methode erfordert, dass Sie den Busy Hour Traffic (BHT) kennen, den Sie aus einem Anrufprotokoll oder durch die folgende Vereinfachung erhalten können: BHT=17% der Anrufminuten eines Tages.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Eine weitere wichtige Variable ist der Grade of Service (GoS), der die Wahrscheinlichkeit definiert, Anrufe durch Leitungsmangel zu blockieren. Sie können diesen Parameter festlegen, der normalerweise 0.05 (5% verlorene Anrufe) oder 0.01 (1% verlorene Anrufe) beträgt. Example #1: Unter Verwendung desselben Beispiels aus 5.10.1 geben wir Ihnen einige Daten zu Verkehrsmustern. Aus dem Anrufprotokoll haben wir diese Daten entdeckt: Daten aus dem Anrufprotokoll (Anrufminuten und BHT):

- Hauptsitz zu Zweigstelle #1 = 2,000 Minuten, BHT = 300 Minuten
- Hauptsitz zu Zweigstelle #2 = 1,000 Minuten, BHT = 170 Minuten
- Zweigstelle #1 zu Zweigstelle #2 = 0, BHT=0

Lassen Sie uns GoS=0.01 festlegen

- Hauptsitz zu Zweigstelle #1 - BHT=300 Minuten/60 = 5 Erlangs
- Hauptsitz zu Zweigstelle #2 – BHT=170 Minuten/60 = 2.83 Erlangs

Unter Verwendung eines Erlang-Rechners wie <https://www.erlang.com>

- Für den Hauptsitz zu Zweigstelle #1 sind 11 Leitungen erforderlich.
- Für den Hauptsitz zu Zweigstelle #2 sind 8 Leitungen erforderlich

1.b Bandwidth Required Wir verwenden ein WAN, in dem Paketverlust selten ist. Wir wählen den g729-Codec wegen seiner guten Klangqualität und Datenkompression (8 Kbps).

Ausgewählter Codec: g729 Datalink layer: Frame-Relay

- Geschätzte Sprachbandbreite für Zweigstelle #1: 26.8x11 = 294.8 Kbps
- Geschätzte Sprachbandbreite für Zweigstelle #2: 26.8x8 = 214.40 Kbps

## Reducing the bandwidth required for VoIP

Drei Methoden können verwendet werden, um die für VoIP-Anrufe erforderliche Bandbreite zu reduzieren:

- RTP-Header-Kompression
- IAX Trunked
- VoIP-Nutzlast

### RTP Header Compression

In Frame-Relay- und PPP-Netzwerken können Sie RTP-Header-Kompression verwenden. RTP-Header-Kompression wurde in RFC 2508 definiert. Es ist ein IETF-Standard, der in mehreren Routern verfügbar ist. Seien Sie jedoch vorsichtig, da einige Router ein anderes Funktionsset erfordern, damit diese Ressource verfügbar ist. Die Auswirkung der Verwendung von RTP-Header-Kompression ist fabelhaft, da sie die in unserem Beispiel erforderliche Bandbreite von 26.8 Kbps pro Sprachkonversation auf 11.2 Kbps reduziert — eine Reduzierung um 58.2%!

### IAX2 trunk mode

Wenn Sie zwei Asterisk-Server verbinden, können Sie das IAX2-Protokoll im Trunk-Modus verwenden. Diese revolutionäre Technologie benötigt keine speziellen Router und kann auf jede Art von Datenverbindung angewendet werden.

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

Der IAX2-Trunk-Modus verwendet dieselben Header ab dem zweiten Anruf wieder. Bei Verwendung von g729 in einer PPP-Verbindung verbraucht der erste Anruf 30 Kbps Bandbreite, während der zweite Anruf denselben Header wie der erste verwendet und die notwendige Bandbreite für den zusätzlichen Anruf auf 9.6 Kbps reduziert. Wir können die erforderliche Bandbreite im Trunk-Modus wie folgt berechnen: Zweigstelle #1 (11 Anrufe) Bandbreite = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Zweigstelle #2 (8 Anrufe) Bandbreite = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps Der erste Anruf verbraucht 31.2 Kbps, der nächste 9.6, und so weiter.

### Increasing the Voice Payload

Diese Methode ist sehr verbreitet, wenn VoIP-Gateways über das Internet verwendet werden. Bei Verwendung einer größeren Nutzlast opfern Sie Latenz zugunsten einer reduzierten Bandbreite. Sie können die RTP-Paketierung ändern, indem Sie die Frame-Größe an den Codec in der allow-Anweisung anhängen.

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

Beispiel:

```
allow=ulaw:30
```

Die zulässigen Werte sind: Name Min Max Default Increment g723 gsm ulaw alaw g726 ADPCM SLIN lpc10 g729 speex ilbc

## Summary

In diesem Kapitel haben Sie gelernt, dass Asterisk VoIP unter Verwendung von Kanälen behandelt. Es unterstützt SIP (via `chan_pjsip` in Asterisk 22) und IAX2; H.323 ist nur über das Community-Add-on `ooh323` verfügbar, und die älteren MGCP- und SCCP (Skinny)-Kanäle sind nicht mehr Teil eines Standard-Asterisk 22-Builds. Sie haben verglichen und gelernt, wie man ein Signalisierungsprotokoll und einen Codec für VoIP-Kanäle auswählt. IAX2 ist bandbreiteneffizienter und kann NAT leicht durchqueren. SIP/PJSIP ist das von Drittanbieter-Telefon- und Gateway-Herstellern am meisten unterstützte Protokoll und der einzige SIP-Kanaltreiber in Asterisk 22. Das H.323-Protokoll ist das älteste und sollte verwendet werden, um eine Verbindung zu älteren VoIP-Infrastrukturen herzustellen. In Abschnitt 5.11 haben wir gelernt, wie man ein VoIP-Netzwerk entwirft und dimensioniert.

## Quiz

1. Welche der folgenden sind Vorteile von VoIP, die in diesem Kapitel beschrieben werden (alle zutreffenden ankreuzen)?
   - A. Konvergenz von Daten- und Sprachnetzwerken zur Kostensenkung
   - B. Niedrigere Infrastrukturkosten für Erweiterungen, Entfernungen und Änderungen
   - C. Offene Standards, die Sie von einem einzigen Anbieter befreien
   - D. Einfachere und billigere Computer-Telefonie-Integration
   - E. Garantierte niedrigere Minutenpreise als bei jeder Telefongesellschaft
2. Konvergenz ist die Integration von Sprache, Daten und Video in einem einzigen Netzwerk; ihr Hauptvorteil ist die Kostensenkung bei der Implementierung und Wartung separater Netzwerke.
   - A. False
   - B. True
3. Asterisk behandelt jedes VoIP-Protokoll als Kanal und kann jeden Kanaltyp mit jedem anderen verbinden, wobei bei Bedarf zwischen Codecs transkodiert wird.
   - A. False
   - B. True
4. In Asterisk 22, welcher Kanaltreiber handhabt SIP?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. Im TCP/IP (IETF)-Modell, gegen das SIP in RFC 3261 tatsächlich definiert ist, arbeiten die Signalisierungsprotokolle SIP, H.323 und IAX2 auf der ___ Schicht.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP ist das am meisten angenommene Protokoll für IP-Telefone und ein offener Standard, der weitgehend von der IETF in RFC 3261 definiert ist.
   - A. False
   - B. True
7. IAX2 transportiert sowohl Signalisierung als auch Medien über einen einzigen UDP-Port, was es effizient und einfach macht, NAT zu durchqueren. Welchen UDP-Port verwendet IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX wurde ursprünglich von Digium (jetzt Sangoma) entwickelt. Trotz begrenzter Akzeptanz durch Telefonhersteller ist IAX exzellent, wenn Sie benötigen (alle zutreffenden ankreuzen):
   - A. Die Bandbreitennutzung zu reduzieren (es verwendet kein RTP)
   - B. Ein Video-Medienformat
   - C. Einfache NAT- und Firewall-Durchquerung
   - D. Trunk-Modus, um viele Asterisk-zu-Asterisk-Anrufe zu kombinieren und den Header-Overhead zu amortisieren
9. In Asterisk 22 wird ein Gerät als ein einziges PJSIP `endpoint`-Objekt konfiguriert, das sowohl Anrufe tätigt als auch empfängt — es gibt keine separate "User"- oder "Peer"-Rolle.
   - A. False
   - B. True
10. Bezüglich Codecs in Asterisk 22, kreuzen Sie alle wahren Aussagen an:
    - A. G.711 ist äquivalent zu PCM und verwendet 64 Kbps Bandbreite.
    - B. Sangomas codec_g729-Modul ist kostenlos herunterladbar, aber die rechtmäßige Nutzung erfordert eine gekaufte Lizenz pro Kanal.
    - C. GSM ist beliebt, weil es etwa 13 Kbps verwendet und keine Lizenz benötigt.
    - D. G.711 u-law ist in Nordamerika üblich, während a-law in Europa und Lateinamerika üblich ist.
    - E. G.729 ist leicht und verbraucht im Vergleich zu G.711 sehr wenige CPU-Ressourcen zum Kodieren und Dekodieren.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
