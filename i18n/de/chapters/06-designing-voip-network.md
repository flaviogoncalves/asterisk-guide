# Entwurf eines VoIP-Netzwerks

Voice over IP wächst schnell auf dem Telefonmarkt. Das Paradigma der Konvergenz verändert die Art und Weise, wie wir kommunizieren, senkt Kosten und verbessert den Informationsaustausch. Sprache ist nur der Anfang einer Ära der vollständigen Multimedia-Kommunikation, die Sprache, Video und Präsenz umfasst. In der Zukunft werden wir nicht mehr Menschen zur Arbeit transportieren, sondern die Arbeit zu den Menschen bringen, da dies sauberer, schneller und kostengünstiger ist. VoIP ist nur ein Teil dieser Revolution. Unsere Herausforderung in diesem Kapitel besteht darin, ein VoIP-Netzwerk zu entwerfen. Dazu müssen wir Konzepte wie Sitzungsprotokolle und Codecs verstehen sowie wissen, wie die Anzahl der Leitungen und die Bandbreite zu dimensionieren sind.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Die Vorteile von VoIP zu verstehen
- Zu beschreiben, wie Asterisk VoIP handhabt
- Die Konzepte der SIP- und IAX-Kanäle zu beschreiben
- Das am besten geeignete Protokoll für einen spezifischen Datenkanal auszuwählen
- Den am besten geeigneten Codec für einen spezifischen Datenkanal auszuwählen
- Die erforderliche Anzahl an Kanälen zu dimensionieren
- Die erforderliche Bandbreite zu berechnen

## VoIP-Vorteile

Warum sollten Sie sich für VoIP interessieren? VoIP bietet Vorteile sowohl für Unternehmen als auch für Privatpersonen. Kostensenkung ist sicherlich einer davon, aber in einigen Umgebungen vereinfacht VoIP die Integration von Computersystemen. Einige der Vorteile sind hier detailliert aufgeführt:

### Konvergenz

Der Hauptvorteil von VoIP ist die Kombination von Daten- und Sprachnetzwerken zur Kostensenkung (Konvergenz). Die Analyse der reinen Sprachminutenkosten reicht jedoch möglicherweise nicht aus, um die Einführung von VoIP zu rechtfertigen. Der Preis für Minuten, die von Telefongesellschaften verkauft werden, sinkt schnell und ist etwas, das vor der Einführung von VoIP berücksichtigt werden sollte.

### Infrastrukturkosten

Die Nutzung einer einzigen Netzwerkinfrastruktur reduziert die Kosten, die mit Erweiterungen, Entfernungen und Änderungen verbunden sind. Da IP allgegenwärtig geworden ist, hat es VoIP-bezogene Technologie auf viele neue Geräte gebracht, wie Mobiltelefone, PDAs, eingebettete Systeme und Laptops.

### Offene Standards

Schließlich bieten die offenen Standards, auf denen VoIP aufbaut, die Freiheit, zwischen verschiedenen Anbietern zu wählen. Dieser einzelne Vorteil macht den Kunden zum König, anstatt ihn von TELCOS und PBX-Herstellern abhängig zu machen.

### Computer Telephony Integration

Telefonie ist weitaus älter als die Informatik. Telefon-PBXs basieren auf Leitungsvermittlung, und man hat normalerweise nicht mehr als einen Computer zur Überwachung. Mit VoIP wird Telefonie von Grund auf auf Basis von Computerstandards erstellt. Dies macht die Nutzung von Computer-Telefonie-Anwendungen billiger und einfacher als im alten Modell. Sie können schnell eine lange Liste von Telefonieanwendungen auf Basis von Asterisk erstellen. Sie können IVRs, ACDs, CTI, Dialer, Screen-Popups und andere Anwendungen in einem Bruchteil der Zeit entwickeln, die für herkömmliche PBXs erforderlich wäre.

## Asterisk VoIP-Architektur

Die Architektur von Asterisk ist unten dargestellt. Asterisk behandelt alle VoIP-Protokolle als Kanäle. Sie können jeden Codec oder jedes Protokoll verwenden. Das hier zu lernende Konzept ist, dass Asterisk jede Art von Kanal mit jedem anderen verbindet. Somit können Sie Signalisierungsprotokolle wie SIP und IAX ineinander übersetzen, sogar mit unterschiedlichen Codecs. Zum Beispiel können Sie einen Anruf von einem SIP-Telefon im lokalen Netzwerk mit dem G.711-Codec zu einem SIP-trunk zu Ihrem VoIP-Anbieter mit dem G.729-Codec übersetzen. In den nächsten Kapiteln werden wir die Details der SIP- und IAX-Architektur erläutern. H.323-Unterstützung (über das Add-on chan_ooh323) ist verfügbar, aber zunehmend selten; SIP/PJSIP ist der Standard für moderne Implementierungen.

![Modulare Architektur von Asterisk: Anwendungen und Kanäle verbinden sich über APIs mit dem PBX-Switch-Kern, wobei Codec-Übersetzungs- und Dateiformatmodule dynamisch geladen werden.](../images/06-voip-network-fig01.png)

## VoIP-Protokolle und der Netzwerk-Stack

VoIP verwendet eine Reihe verschiedener Protokolle, die zusammenarbeiten. Es ist verlockend, sie dem siebenstufigen OSI-Referenzmodell gegenüberzustellen, und viele ältere Diagramme tun genau das — sie platzieren SIP und H.323 auf der „Sitzungsschicht“ und die Codecs auf der „Darstellungsschicht“. Diese Zuordnung war schon immer umstritten. Die IETF, die SIP standardisiert, verwendet nicht das OSI-Modell; sie folgt dem älteren vierstufigen TCP/IP-Modell (DoD), und RFC 3261 definiert **SIP als Protokoll der Anwendungsschicht**. Die Medien folgen demselben Muster: RTP und die Codecs leben in der Nutzlast der Anwendung, übertragen über UDP auf der Transportschicht. Die folgende Tabelle ordnet die wichtigsten VoIP-Protokolle dem TCP/IP-Modell zu, das die IETF tatsächlich verwendet, wobei das grobe OSI-Äquivalent nur als Referenz dient.

| TCP/IP (IETF) Schicht | Protokolle | Grobes OSI-Äquivalent |
|---|---|---|
| Anwendung | SIP, H.323, MGCP, IAX2-Signalisierung; RTP/RTCP; Codecs (G.711, G.729, Opus…) | Anwendung / Darstellung / Sitzung |
| Transport | UDP, TCP | Transport |
| Internet | IP (mit QoS wie DiffServ) | Netzwerk |
| Verbindung | Ethernet, PPP, Frame Relay… | Sicherung / Physikalisch |

QoS-Mechanismen wie DiffServ arbeiten auf der IP-Schicht, um Sprachpakete zu priorisieren und die Anrufqualität zu verbessern. Einige Protokollspezifika:

- **SIP** verwendet UDP oder TCP auf Port 5060 (TLS auf 5061) zur Signalisierung. Das Audio wird separat per RTP über einen konfigurierbaren UDP-Portbereich übertragen (das mitgelieferte `rtp.conf` Beispiel von Asterisk verwendet 10000 bis 20000), kodiert mit einem Codec wie G.711.
- **H.323** überträgt die Anrufsignalisierung über TCP (H.225-Anrufsignalisierung auf Port 1720), während der H.225-RAS-Kanal UDP auf Port 1719 verwendet; RTP transportiert das Audio.
- **IAX2** ist ungewöhnlich: Es bündelt sowohl Signalisierung als auch Medien über einen einzigen UDP-Port (4569), was die NAT- und Firewall-Durchquerung vereinfacht.

> **[author]** Optional: Geben Sie eine neu gezeichnete Abbildung des TCP/IP-Stacks oben in Auftrag, falls eine visuelle Darstellung gewünscht ist; die Tabelle ist ansonsten in sich geschlossen.

## Wie man ein Protokoll auswählt

Wie können Sie angesichts der vielen Protokolle das beste für Ihr Netzwerk auswählen? In diesem Abschnitt werden wir die Vor- und Nachteile jedes Protokolls hervorheben.

### SIP - Session Initiated Protocol

SIP ist ein offener Standard der Internet Engineering Task Force (IETF), weitgehend definiert in RFC 3261. Die meisten modernen VoIP-Anbieter verwenden SIP; tatsächlich wird es zum populärsten VoIP-Standard. Die Stärke von SIP liegt darin, dass es ein IETF-basierter Standard ist. SIP ist leicht im Vergleich zum älteren H.323. Die Hauptschwäche von SIP ist die NAT-Durchquerung — eine Herausforderung für die meisten SIP-VoIP-Anbieter. Die IETF hat SIP nicht mit Blick auf die Abrechnung entwickelt, sondern für offene Kommunikation zwischen Peers. Abrechnung ist normalerweise ein Anliegen von VoIP-Anbietern.

### IAX – Inter Asterisk eXchange

IAX ist ein offenes Protokoll, das ursprünglich von Digium (jetzt Sangoma) entwickelt wurde. IAX ist ein All-in-One-Protokoll, da es Signalisierung und Medien über denselben UDP-Port (4569) transportiert. Mark Spencer entwickelte IAX als binäres Protokoll für reduzierte Bandbreite. Die Hauptstärke von IAX ist seine reduzierte Bandbreitennutzung (es verwendet kein RTP); es ist auch sehr einfach für NAT- und Firewall-Durchquerung, da es nur einen UDP-Port (4569) verwendet. Wenn ein traditioneller PBX-Hersteller IAX entwickelt hätte, hätte er das Protokoll wahrscheinlich als „das Beste seit Speiseeis“ vermarktet; in manchen Situationen kann IAX im Trunk-Modus die Sprachbandbreitennutzung um ein Drittel reduzieren. IAX2 (Version 2) ist in Asterisk 22 weiterhin über das `chan_iax2` Modul enthalten und bleibt nützlich für Asterisk-zu-Asterisk-Trunks, obwohl es als veraltet gilt; SIP/PJSIP wird für neue Implementierungen bevorzugt. IAX2 ist in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational) spezifiziert.

### MGCP – Media Gateway Control Protocol

MGCP ist ein Protokoll, das in Verbindung mit H.323, SIP und IAX verwendet wird. Sein größter Vorteil ist die Skalierbarkeit. Es wird im Call-Agent anstatt in den Gateways konfiguriert. Dies vereinfacht den Konfigurationsprozess und ermöglicht eine zentralisierte Verwaltung. Die Asterisk-Implementierung ist jedoch nicht vollständig, und es scheint, dass nicht viele Leute es verwenden.

### H.323

H.323 wird weitgehend in VoIP verwendet. Es ist eines der ersten VoIP-Protokolle und ist essenziell für die Verbindung älterer VoIP-Infrastrukturen, die auf Gateways basieren. H.323 ist immer noch der Standard auf dem Gateway-Markt, obwohl der Markt langsam zu SIP migriert. Zu den Stärken von H.323 gehören die große Marktakzeptanz und Reife. Die Schwächen von H.323 hängen mit der Komplexität der Implementierung und den mit den Standardisierungsgremien verbundenen Kosten zusammen.

### Protokollvergleichstabelle

Die folgende Tabelle fasst die Unterschiede zwischen den Sitzungsprotokollen zusammen.

| Protokoll | Standardisierungsgremium | Asterisk 22 Modul / Status | Verwendet für |
|----------|---------------|-----------------------------|----------|
| SIP | IETF-Standard | `chan_pjsip` (Kern; der einzige SIP-Treiber — `chan_sip` wurde in Asterisk 21 entfernt) | SIP-Telefone; Verbindung zu SIP-Dienstanbietern |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (Kern; weiterhin enthalten, gilt als veraltet) | Asterisk-zu-Asterisk-Trunks; IAX2-Telefone; IAX-Dienstanbieter |
| H.323 | ITU-Standard | `chan_ooh323` (externes Community-Add-on, nicht im Basis-Build) | H.323-Telefone und Gateways (kann einen externen Gatekeeper verwenden, kann keiner sein) |
| MGCP | IETF/ITU | `chan_mgcp` in Asterisk 21 entfernt — nicht mehr verfügbar | (veraltete MGCP-Telefone) |
| SCCP (Skinny) | Cisco proprietär | `chan_skinny` in Asterisk 21 entfernt — nicht mehr verfügbar | (veraltete Cisco-Telefone) |

## Ein Endpoint pro Gerät

In Asterisk 22 modelliert der PJSIP-Stack jedes Telefon, jeden Trunk oder jedes Gateway als ein einzelnes **Endpoint**-Objekt in `pjsip.conf`. Ein Endpoint tätigt und empfängt Anrufe; seine Anmeldedaten leben in einem `auth`-Objekt, seine registrierte Adresse in einem `aor` und sein Netzwerkpfad in einem `transport`. Sie konfigurieren einen Endpoint pro Gerät und fügen die benötigten Teile hinzu — es gibt keine separate „User“- versus „Peer“-Rolle, über die man nachdenken müsste. (Das vollständige Objektmodell wird in *SIP und PJSIP* behandelt.)

## Codecs und Codec-Übersetzung

Sie verwenden einen Codec, um die Sprache von einer analogen Welle in ein digitales Signal umzuwandeln. Codecs unterscheiden sich voneinander in Aspekten wie Klangqualität, Kompressionsrate, Bandbreite und Rechenanforderungen. Dienste, Telefone und Gateways unterstützen normalerweise mehrere dieser Aspekte. Der Codec G.729 ist sehr beliebt. Er ist nicht Teil des Standard-Asterisk 22-Builds; stattdessen wird er als externes Add-on-Modul (`codec_g729`) ausgeliefert, das Sie von Digium (jetzt Sangoma) herunterladen. Die `menuselect`-Quelle von Asterisk listet es mit `support_level=external` auf und merkt deutlich an: „Laden Sie den g729a-Codec von Digium herunter. Für diesen Codec muss eine Lizenz erworben werden.“ Mit anderen Worten, die rechtmäßige Nutzung von G.729 erfordert eine gekaufte Lizenz pro Kanal. (Eine Open-Source-Alternative, `bcg729`, existiert ebenfalls.)

![Pulscodemodulation (PCM): Ein 4000-Hz-Analogsignal wird 8000 Mal pro Sekunde abgetastet (Nyquist-Theorem) und in einen digitalen 64-Kbps-Bitstrom kodiert.](../images/06-voip-network-fig04.png)

Asterisk 22 unterstützt (unter anderem) die folgenden Codecs:

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — Standard-PSTN-Qualität; ulaw üblich in Nordamerika, alaw üblich in Europa und Lateinamerika
- ITU G.722: 64 Kbps — Breitband (HD-Sprache), gute Qualität bei gleicher Bandbreite wie G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — externes `codec_g729` Binärmodul, heruntergeladen von Digium/Sangoma (`support_level=external`; eine Lizenz muss erworben werden, um es zu nutzen)
- Speex: 2.15 bis 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variabel — moderner Breitband-/Fullband-Codec; exzellente Qualität und Widerstandsfähigkeit gegen Paketverlust; bereitgestellt als externes `codec_opus` Binärmodul, heruntergeladen von Digium/Sangoma (`support_level=external`; kein Lizenzkauf vermerkt, im Gegensatz zu G.729); empfohlen für WebRTC und moderne SIP-Endpoints. (Open-Source-Build-Alternativen existieren auf GitHub.)

Zusätzlich erlaubt Asterisk die Übersetzung zwischen Codecs. In einigen Fällen ist dies nicht möglich, wie im Fall von g723, das nur im Pass-thru-Modus unterstützt wird. Die Übersetzung von einem Codec in einen anderen verbraucht viele CPU-Ressourcen. Vermeiden Sie dies daher nach Möglichkeit vollständig.

## Wie man einen Codec auswählt

Die Codec-Auswahl hängt von mehreren Optionen ab, wie:

- Klangqualität
- Lizenzkosten
- CPU-Verarbeitungslast
- Bandbreitenanforderungen
- Verschleierung von Paketverlusten
- Verfügbarkeit für Asterisk und Telefongeräte

Die folgende Tabelle vergleicht die populärsten Codecs. Die Qualität dieser Codecs gilt als „toll“-Qualität — mit anderen Worten, ähnlich wie PSTN.

| Codec | G.711 (ulaw/alaw) | G.722 | Opus | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|---|---|
| Audioband | Schmalband | Breitband (HD) | Schmal→Fullband | Schmalband | Schmalband | Schmalband |
| Bandbreite (Kbps) | 64 | 64 | 6–510 (variabel) | 8 | 13.33 | 13 |
| Asterisk 22 Modul | `codec_ulaw`/`codec_alaw` (Kern) | `codec_g722` (Kern) | `codec_opus` (extern) | `codec_g729` (extern) | `codec_ilbc` (Kern) | `codec_gsm` (Kern) |
| Kosten (pro Kanal) | Kostenlos | Kostenlos | Kostenlos (Binär-Download) | Lizenzkauf erforderlich¹ | Kostenlos | Kostenlos |
| Widerstand gegen Frame-Verlust² | Keiner | Niedrig | Exzellent (eingebautes FEC/PLC) | ~3% | ~5% | ~3% |
| Relative CPU-Kosten | Sehr niedrig | Niedrig | Moderat–hoch | Hoch | Hoch | Niedrig |

Die PSTN-Basislinie ist **G.711** — sie ist die Referenz für „toll“-Qualität und transkodiert kostenlos innerhalb von Asterisk. **G.722** liefert Breitband-Sprache (HD) bei denselben 64 Kbps und ist eine gute Wahl für LAN/intern. **Opus** ist der moderne Standard für WebRTC und fähige SIP-Endpoints: Er passt seine Bitrate an, verfügt über eine eingebaute Vorwärtsfehlerkorrektur und widersteht Paketverlusten gut; er wird als externes `codec_opus` Binärpaket ausgeliefert (kostenloser Download). **G.729** bleibt nützlich auf WAN-Trunks mit geringer Bandbreite, aber die rechtmäßige Nutzung erfordert entweder Sangomas lizenziertes `codec_g729` (kostenloser Download, Lizenz pro Kanal zum Nutzen erforderlich) oder die Open-Source-Implementierung **bcg729** als Alternative.

¹ Sangomas `codec_g729` Binärpaket ist kostenlos herunterladbar, erfordert aber eine gekaufte Lizenz pro Kanal für die rechtmäßige Nutzung. Das Open-Source-Modul `bcg729` ist eine lizenzfreie Alternative.

² Widerstand gegen Frame-Verlust bezieht sich darauf, wie gut die wahrgenommene Qualität (MOS) bei Paketverlusten erhalten bleibt. Der exakte Übergangspunkt variiert mit der Paketierung und den Netzwerkbedingungen; verwenden Sie diese Spalte für einen relativen Vergleich, nicht als präzisen Wert.

**Codec-Empfehlungen für Asterisk 22:**

- **G.711 (ulaw/alaw):** Verwenden Sie dies für PSTN-Trunks und maximale Interoperabilität; keine Transkodierungskosten innerhalb von Asterisk.
- **G.729:** Nützlich für WAN-Trunks mit geringer Bandbreite; Sangomas `codec_g729` Modul ist kostenlos herunterladbar, erfordert aber eine gekaufte Lizenz pro Kanal für die Nutzung.
- **G.722:** Gute Wahl für Breitband (HD-Sprache) bei LAN/internen Extensions; gleiche Bandbreite wie G.711 bei besserer Qualität.
- **Opus:** Empfohlen für moderne Endpunkte, WebRTC-Clients und jede Implementierung, bei der der Endpunkt dies unterstützt. Adaptive Bitrate, exzellente Widerstandsfähigkeit gegen Paketverlust, frei verfügbar über Sangomas `codec_opus` Binärmodul.

## Overhead durch Protokoll-Header

Obwohl Codecs wenig Bandbreite verbrauchen, müssen wir den Overhead durch Protokoll-Header wie Ethernet, IP, UDP und RTP berücksichtigen. Daher könnten wir sagen, dass die Bandbreite von den verwendeten Headern abhängt. Wenn wir uns in einem Ethernet-Netzwerk befinden, ist der Bandbreitenbedarf höher als in einem PPP-Netzwerk, da der PPP-Header kürzer ist als der Ethernet-Header. Schauen wir uns einige Beispiele an: Ethernet-Ziel G.729 kodiert (20) UDP-Header (8) Ethernet-Typ (2) Ethernet-Quelle IP-Header (20) RTP-Header (12) Sprach-Nutzlast Prüfsumme (4) Adresse (6) Adresse (6) Ethernet Codec g.711 (64 Kbps)

![Ein einzelnes g.729-Sprachpaket auf Ethernet: 20 Bytes Nutzlast verpackt in 58 Bytes Ethernet-, IP-, UDP- und RTP-Header — ein g.729-Gespräch verbraucht 31,2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95,2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82,4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82,8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31,2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26,4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26,8 Kbps

Sie können andere Bandbreitenanforderungen einfach mit einem Online-VoIP-Bandbreitenrechner wie <https://www.voip.school/bandcalc/bandcalc.php> berechnen.


## Traffic Engineering

Ein Hauptproblem beim Entwurf von VoIP-Netzwerken ist die Dimensionierung der Anzahl der Leitungen und der erforderlichen Bandbreite zu einem bestimmten Ziel, wie einer entfernten Niederlassung oder einem Dienstanbieter. Es ist auch wichtig, die Anzahl der gleichzeitigen Asterisk-Anrufe zu dimensionieren (Hauptparameter für die Dimensionierung von Asterisk).

### Vereinfachungen

Die primäre und am weitesten verbreitete Vereinfachung besteht darin, die Anzahl der Anrufe nach Benutzertyp zu schätzen. Zum Beispiel:

- Business-PBXs (ein gleichzeitiger Anruf für alle fünf Extensions)
- Privatnutzer (ein gleichzeitiger Anruf für alle sechzehn Benutzer)

Beispiel #1 Der Hauptsitz des Unternehmens hat 120 Extensions und zwei Niederlassungen — die erste mit 30 Extensions und die zweite mit 15 Extensions. Unser Ziel ist es, die Anzahl der E1-Trunks im Hauptsitz und die für das Frame-Relay-Netzwerk erforderliche Bandbreite zu dimensionieren.

![Beispiel-Netzwerktopologie (gleiche Stadt): Hauptsitz mit 120 Extensions verbindet sich über T1-Leitungen mit dem PSTN und über eine Frame-Relay-Cloud mit Niederlassung #1 (30 Extensions) und Niederlassung #2 (15 Extensions).](../images/06-voip-network-fig06.png)

1a Anzahl der T1-Leitungen

- Gesamtzahl der Extensions, die T1-Leitungen nutzen: 120+30+15=165 Leitungen
- Verwendung eines Trunks für alle fünf Extensions für geschäftliche Nutzung
- Gesamtzahl der Leitungen = 33 oder ungefähr 2xT1-Leitungen

1b Bandbreitenanforderungen Wir wählen den g.729-Codec aufgrund der Bandbreitenanforderungen, der Klangqualität und des mittleren CPU-Verbrauchs.

Mit einem Trunk für alle fünf Extensions:

- Erforderliche Bandbreite für Niederlassung #1 (Frame-Relay): 26,8*6=160,8 Kbps
- Erforderliche Bandbreite für Niederlassung #2 (Frame-Relay): 26,8*3= 80,4 Kbps

### Erlang-B-Methode

1.a Anzahl der gleichzeitigen VoIP-Anrufe Manchmal ist Vereinfachung nicht der beste Ansatz. Wenn Sie über frühere Daten verfügen, können Sie einen wissenschaftlicheren Ansatz wählen. Wir verwenden die Arbeit von Agner Karup Erlang (Kopenhagener Telefongesellschaft, 1909), der eine Formel zur Berechnung von Leitungen in einer Trunk-Gruppe zwischen zwei Städten entwickelte. Erlang ist eine Verkehrsmessungseinheit, die normalerweise in der Telekommunikation zu finden ist. Sie wird verwendet, um das Verkehrsaufkommen für eine Stunde zu beschreiben. Zum Beispiel: 20 Anrufe finden in einer Stunde statt, mit durchschnittlich 5 Minuten Gesprächsdauer. Sie können die Anzahl der Erlangs wie unten gezeigt berechnen: Verkehrsminuten in der Stunde: 20 x 5 = 100 Minuten Verkehrsstunde innerhalb einer Stunde: 100/60 = 1,66 Erlangs Sie können diese Maße aus einem Anrufprotokoll bestimmen und sie verwenden, um Ihr Netzwerk zu entwerfen und die Anzahl der erforderlichen Leitungen zu berechnen. Sobald die Anzahl der Leitungen bekannt ist, ist es möglich, die Bandbreitenanforderungen zu berechnen. Erlang B ist die am häufigsten verwendete Methode zur Berechnung der Anzahl der Leitungen in einer Trunk-Gruppe. Es nimmt an, dass Anrufe zufällig eintreffen (Poisson-Verteilung), während blockierte Anrufe sofort gelöscht werden. Diese Methode erfordert, dass Sie den Busy Hour Traffic (BHT) kennen, den Sie aus einem Anrufprotokoll oder durch die folgende Vereinfachung erhalten können: BHT=17% der Anrufminuten eines Tages.

![Erlang-B-Rechnerergebnisse: 5 Erlangs bei 1% Blockierung erfordern 11 Leitungen (Hauptsitz zu Niederlassung #1), und 2,83 Erlangs bei 1% Blockierung erfordern 8 Leitungen (Hauptsitz zu Niederlassung #2).](../images/06-voip-network-fig07.png)

Eine weitere wichtige Variable ist der Grade of Service (GoS), der die Wahrscheinlichkeit definiert, Anrufe aufgrund von Leitungsmangel zu blockieren. Sie können diesen Parameter festlegen, der normalerweise 0,05 (5% Anrufe verloren) oder 0,01 (1% Anrufe verloren) beträgt. Beispiel #1: Unter Verwendung desselben Beispiels aus 5.10.1 geben wir Ihnen einige Daten zu Verkehrsmustern. Aus dem Anrufprotokoll haben wir diese Daten entdeckt: Daten aus dem Anrufprotokoll (Anrufminuten und BHT):

- Hauptsitz zu Niederlassung #1 = 2.000 Minuten, BHT = 300 Minuten
- Hauptsitz zu Niederlassung #2 = 1.000 Minuten, BHT = 170 Minuten
- Niederlassung #1 zu Niederlassung #2 = 0, BHT=0

Legen wir GoS=0,01 fest

- Hauptsitz zu Niederlassung #1 - BHT=300 Minuten/60 = 5 Erlangs
- Hauptsitz zu Niederlassung #2 – BHT=170 Minuten/60 = 2,83 Erlangs

Unter Verwendung eines Erlang-Rechners wie <https://www.erlang.com>

- Für den Hauptsitz zu Niederlassung #1 sind 11 Leitungen erforderlich.
- Für den Hauptsitz zu Niederlassung #2 sind 8 Leitungen erforderlich

1.b Erforderliche Bandbreite Wir verwenden ein WAN, in dem Paketverlust selten ist. Wir wählen den g729-Codec aufgrund seiner guten Klangqualität und Datenkompression (8 Kbps).

Ausgewählter Codec: g729 Datalink-Schicht: Frame-Relay

- Geschätzte Sprachbandbreite für Niederlassung #1: 26,8x11 = 294,8 Kbps
- Geschätzte Sprachbandbreite für Niederlassung #2: 26,8x8 = 214,40 Kbps

## Reduzierung der für VoIP erforderlichen Bandbreite

Drei Methoden können verwendet werden, um die für VoIP-Anrufe erforderliche Bandbreite zu reduzieren:

- RTP-Header-Kompression
- IAX Trunked
- VoIP-Nutzlast

### RTP-Header-Kompression

In Frame-Relay- und PPP-Netzwerken können Sie RTP-Header-Kompression verwenden. RTP-Header-Kompression wurde in RFC 2508 definiert. Es ist ein IETF-Standard, der in mehreren Routern verfügbar ist. Seien Sie jedoch vorsichtig, da einige Router ein anderes Funktionsset erfordern, damit diese Ressource verfügbar ist. Die Auswirkung der Verwendung von RTP-Header-Kompression ist fabelhaft, da sie die in unserem Beispiel erforderliche Bandbreite von 26,8 Kbps pro Sprachgespräch auf 11,2 Kbps reduziert — eine Reduzierung um 58,2%!

### IAX2-Trunk-Modus

Wenn Sie zwei Asterisk-Server verbinden, können Sie das IAX2-Protokoll im Trunk-Modus verwenden. Diese revolutionäre Technologie benötigt keine speziellen Router und kann auf jede Art von Datenverbindung angewendet werden.

![IAX2-Trunk-Modus auf Ethernet: Ein einzelner g.729-Anruf benötigt seinen vollständigen Header-Stack (31,2 Kbps), aber ein zweiter Anruf teilt sich diese Header und fügt nur ein kleines IAX2-Miniframe hinzu, was durchschnittlich etwa 9,6 Kbps zusätzliche Bandbreite pro zusätzlichem Anruf bedeutet.](../images/06-voip-network-fig08.png)

Der IAX2-Trunk-Modus verwendet dieselben Header ab dem zweiten Anruf wieder. Bei Verwendung von g729 in einer PPP-Verbindung verbraucht der erste Anruf 30 Kbps Bandbreite, während der zweite Anruf denselben Header wie der erste verwendet und die notwendige Bandbreite für den zusätzlichen Anruf auf 9,6 Kbps reduziert. Wir können die erforderliche Bandbreite im Trunk-Modus wie folgt berechnen: Niederlassung #1 (11 Anrufe) Bandbreite = 31,2 + (11-1)* 9,6 Kbps = 127,2 Kbps Niederlassung #2 (8 Anrufe) Bandbreite = 31,2 + (8-1)* 9,6 Kbps = 98,4 Kbps Der erste Anruf verbraucht 31,2 Kbps, der nächste 9,6 und so weiter.

### Erhöhung der Sprach-Nutzlast

Diese Methode ist sehr verbreitet, wenn VoIP-Gateways über das Internet verwendet werden. Bei Verwendung einer größeren Nutzlast opfern Sie Latenz zugunsten einer reduzierten Bandbreite. Sie können die RTP-Paketierung ändern, indem Sie die Frame-Größe an den Codec in der allow-Anweisung anhängen.

![Erhöhung der Sprach-Nutzlast: Das Packen von 60 Bytes g.729-Nutzlast in ein Paket (statt 20) amortisiert die 58 Bytes an Headern über mehr Sprache, was die Bandbreite auf etwa 16,05 Kbps pro Anruf senkt, auf Kosten einer erhöhten Latenz.](../images/06-voip-network-fig09.png)

Beispiel:

```
allow=ulaw:30
```

Die zulässigen Werte sind: Name Min Max Default Increment g723 gsm ulaw alaw g726 ADPCM SLIN lpc10 g729 speex ilbc

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Asterisk VoIP unter Verwendung von Kanälen behandelt. Es unterstützt SIP (über `chan_pjsip` in Asterisk 22) und IAX2; H.323 ist nur über das Community-Add-on `ooh323` verfügbar, und die älteren MGCP- und SCCP (Skinny)-Kanäle sind nicht mehr Teil eines Standard-Asterisk 22-Builds. Sie haben verglichen und gelernt, wie man ein Signalisierungsprotokoll und einen Codec für VoIP-Kanäle auswählt. Das IAX2 ist bandbreiteneffizienter und kann NAT leicht durchqueren. SIP/PJSIP ist das von Drittanbietern für Telefone und Gateways am meisten unterstützte Protokoll und der einzige SIP-Kanaltreiber in Asterisk 22. Das H.323-Protokoll ist das älteste und sollte verwendet werden, um eine Verbindung zu veralteten VoIP-Infrastrukturen herzustellen. In Abschnitt 5.11 haben wir gelernt, wie man ein VoIP-Netzwerk entwirft und dimensioniert.

## Quiz

1. Welche der folgenden sind Vorteile von VoIP, die in diesem Kapitel beschrieben werden (kreuzen Sie alle zutreffenden an)?
   - A. Konvergenz von Daten- und Sprachnetzwerken zur Kostensenkung
   - B. Niedrigere Infrastrukturkosten für Erweiterungen, Entfernungen und Änderungen
   - C. Offene Standards, die Sie von einem einzigen Anbieter befreien
   - D. Einfachere und billigere Computer-Telefonie-Integration
   - E. Garantierte niedrigere Minutenpreise als bei jeder Telefongesellschaft
2. Konvergenz ist die Integration von Sprache, Daten und Video in einem einzigen Netzwerk; ihr Hauptvorteil ist die Kostensenkung bei der Implementierung und Wartung separater Netzwerke.
   - A. Falsch
   - B. Richtig
3. Asterisk behandelt jedes VoIP-Protokoll als Kanal und kann jeden Kanaltyp mit jedem anderen verbinden, wobei bei Bedarf zwischen Codecs transkodiert wird.
   - A. Falsch
   - B. Richtig
4. In Asterisk 22 wird SIP von welchem Kanaltreiber gehandhabt?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In dem TCP/IP (IETF)-Modell, gegen das SIP in RFC 3261 tatsächlich definiert ist, arbeiten die Signalisierungsprotokolle SIP, H.323 und IAX2 auf der ___ Schicht.
   - A. Darstellung
   - B. Anwendung
   - C. Physikalisch
   - D. Sitzung
   - E. Sicherung
6. SIP ist das am meisten angenommene Protokoll für IP-Telefone und ein offener Standard, der weitgehend von der IETF in RFC 3261 definiert ist.
   - A. Falsch
   - B. Richtig
7. IAX2 transportiert sowohl Signalisierung als auch Medien über einen einzigen UDP-Port, was es effizient und einfach macht, NAT zu durchqueren. Welchen UDP-Port verwendet IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX wurde ursprünglich von Digium (jetzt Sangoma) entwickelt. Trotz begrenzter Akzeptanz durch Telefonhersteller ist IAX exzellent, wenn Sie (kreuzen Sie alle zutreffenden an):
   - A. Bandbreitennutzung reduzieren müssen (es verwendet kein RTP)
   - B. Ein Video-Medienformat benötigen
   - C. Einfache NAT- und Firewall-Durchquerung benötigen
   - D. Trunk-Modus benötigen, um viele Asterisk-zu-Asterisk-Anrufe zu kombinieren und den Header-Overhead zu amortisieren
9. In Asterisk 22 wird ein Gerät als einzelnes PJSIP `endpoint`-Objekt konfiguriert, das sowohl Anrufe tätigt als auch empfängt — es gibt keine separate „User“- oder „Peer“-Rolle.
   - A. Falsch
   - B. Richtig
10. Bezüglich Codecs in Asterisk 22, kreuzen Sie alle wahren Aussagen an:
    - A. G.711 ist äquivalent zu PCM und verwendet 64 Kbps Bandbreite.
    - B. Sangomas codec_g729-Modul ist kostenlos herunterladbar, aber die rechtmäßige Nutzung erfordert eine gekaufte Lizenz pro Kanal.
    - C. GSM ist beliebt, weil es etwa 13 Kbps verwendet und keine Lizenz benötigt.
    - D. G.711 u-law ist in Nordamerika üblich, während a-law in Europa und Lateinamerika üblich ist.
    - E. G.729 ist leicht und verbraucht im Vergleich zu G.711 sehr wenige CPU-Ressourcen zum Kodieren und Dekodieren.

**Antworten:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Anwendung — SIP ist ein Protokoll der Anwendungsschicht im TCP/IP-Modell, das die IETF verwendet) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
