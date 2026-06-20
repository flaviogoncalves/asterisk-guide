# Designing a VoIP network

Voice over IP ist ein schnell wachsender Bereich im Telekommunikationsmarkt. Das Konvergenzparadigma verändert die Art und Weise, wie wir kommunizieren, senkt Kosten und verbessert die Art, wie wir Informationen austauschen. Sprache ist nur der Anfang einer vollständigen Multimedia‑Kommunikationsära, die Sprache, Video und Präsenz umfasst. In Zukunft werden wir Menschen nicht mehr zur Arbeit transportieren, sondern die Arbeit zu den Menschen bringen, weil das sauberer, schneller und günstiger ist. VoIP ist nur ein Teil dieser Revolution. Unsere Aufgabe in diesem Kapitel ist es, ein VoIP‑Netzwerk zu entwerfen. Dafür müssen wir Konzepte wie Sitzungsprotokolle und Codecs verstehen sowie wissen, wie man die Anzahl der Leitungen und die Bandbreite dimensioniert.

## Ziele

By the end of this chapter, you should be able to:

- Die Vorteile von VoIP verstehen
- Beschreiben, wie Asterisk VoIP verarbeitet
- Die Konzepte der SIP- und IAX-Kanäle beschreiben
- Das am besten geeignete Protokoll für einen bestimmten Datenkanal auswählen
- Den am besten geeigneten Codec für einen bestimmten Datenkanal auswählen
- Die erforderliche Anzahl an Kanälen dimensionieren
- Die erforderliche Bandbreite berechnen

## VoIP benefits

Why would you care about VoIP? VoIP provides benefits to both companies and individuals. Cost reduction is certainly one of them, but in some environments VoIP simplifies the integration of computer systems. Several of the benefits are detailed here:

### Convergence

The primary benefit of VoIP is the combination of data and voice networks to reduce costs (convergence). However, analyzing just voice minute costs may not be enough to justify the adoption of VoIP. The price of the minutes sold by phone companies is quickly becoming cheaper and is something to be considered before adopting VoIP.

### Infrastructure costs

The use of a single network infrastructure reduces the costs associated with additions, removals, and changes. As IP has become pervasive, it has brought VoIP-related technology to several new devices, such as cell phones, PDAs, embedded systems, and laptops.

### Open Standards

Finally, the open standards upon which VoIP is built provide the freedom to choose from different vendors. This single benefit makes the customer king instead of a subordinate to TELCOS and PBX manufacturers.

### Computer Telephony Integration

Telephony is far older than computing. Telephony PBXs are circuit-switch based, and you usually do not have more than a computer for supervision. With VoIP, telephony is from the ground up created based in computer standards. This makes the use of Computer Telephony applications cheaper and easier than in the old model. You can quickly create a long list of telephony applications based on Asterisk. You can develop IVRs, ACDs, CTI, dialers, screen popups, and other applications in a fraction of the time required for traditional PBXs.

## Asterisk VoIP-Architektur

Die Architektur von Asterisk ist unten dargestellt. Asterisk behandelt alle VoIP‑Protokolle als Channels. Sie können jeden Codec oder jedes Protokoll verwenden. Das zu lernende Konzept ist, dass Asterisk beliebige Channel‑Typen miteinander verbindet. So können Sie Signalisierungsprotokolle wie SIP und IAX zueinander übersetzen, sogar mit unterschiedlichen Codecs. Zum Beispiel können Sie einen Anruf von einem SIP‑Telefon im lokalen Netzwerk, das den Codec G.711 nutzt, zu einem SIP‑Trunk zu Ihrem VoIP‑Provider, der den Codec G.729 verwendet, übersetzen. In den nächsten Kapiteln erklären wir die Details der SIP‑ und IAX‑Architektur. Unterstützung für H.323 (über das chan_ooh323‑Add‑on) ist verfügbar, aber zunehmend selten; SIP/PJSIP ist der Standard für moderne Deployments.

![Asterisk's modular architecture: applications and channels connect to the PBX switch core through APIs, with codec translation and file-format modules loaded dynamically.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP verwendet eine Reihe verschiedener Protokolle, die zusammenarbeiten. Es ist verlockend, sie
gegen das sieben‑schichtige OSI‑Referenzmodell zu stellen, und viele ältere Diagramme tun genau
das – sie platzieren SIP und H.323 in der „Session“-Schicht und die Codecs in der
„Presentation“-Schicht. Diese Zuordnung war stets umstritten. Das IETF, das
SIP standardisiert, verwendet nicht das OSI‑Modell; es folgt dem älteren vier‑schichtigen TCP/IP
(DoD)-Modell, und RFC 3261 definiert **SIP als ein Application‑Layer‑Protokoll**. Das Media‑
Verhalten folgt demselben Muster: RTP und die Codecs befinden sich im Anwendungspayload,
über UDP auf der Transportschicht transportiert. Die nachfolgende Tabelle ordnet die wichtigsten VoIP‑Protokolle dem
TCP/IP‑Modell zu, das das IETF tatsächlich verwendet, wobei das grobe OSI‑Äquivalent nur
zur Referenz angegeben ist.

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

QoS‑Mechanismen wie DiffServ arbeiten auf der IP‑Schicht, um Sprachpakete zu priorisieren und
die Anrufqualität zu verbessern. Einige protokollspezifische Details:

- **SIP** verwendet UDP oder TCP auf Port 5060 (TLS auf 5061), um Signalisierung zu transportieren. Der Audio‑Stream
  wird separat per RTP über einen konfigurierbaren UDP‑Port‑Bereich (Asterisk's shipped
  `rtp.conf` sample uses 10000 to 20000) übertragen, kodiert mit einem Codec wie G.711.
- **H.323** transportiert die Anrufsignalisierung über TCP (H.225 call signaling on port 1720), während
  der H.225 RAS‑Kanal UDP auf Port 1719 nutzt; RTP transportiert das Audio.
- **IAX2** ist ungewöhnlich: Es multiplexiert sowohl Signalisierung als auch Media über einen einzigen UDP‑Port
  (4569), was die NAT‑ und Firewall‑Durchdringung vereinfacht.


## How to choose a protocol

Given the many protocols, how can you choose the best one for your network? In this section, we will highlight the advantages and drawbacks of each protocol.

### SIP - Session Initiated Protocol

SIP is an Internet Engineering Task Force (IETF) open standard, largely defined in RFC 3261. Most modern VoIP providers use SIP; indeed, it is becoming the most popular VoIP standard. The strength of SIP is that it is an IETF-based standard. SIP is light when compared to the older H.323. SIP’s main weakness is the NAT traversal—a challenge to most SIP VoIP providers. IETF did not create SIP with billing in mind, but for open communications between peers. Billing is usually a concern for VoIP providers.

### IAX – Inter Asterisk eXchange

IAX is an open protocol originally developed by Digium (now Sangoma). IAX is an all-in-one protocol as it transports signaling and media through the same UDP port (4569). Mark Spencer developed IAX as a binary protocol for reduced bandwidth. The main strength of IAX is its reduced bandwidth usage (it does not use RTP); it is also very easy for NAT and firewall traversal since it uses only one UDP port (4569).

If a traditional PBX manufacturer were to have created IAX, it would probably have marketed the protocol as the "best thing since ice cream"; in some situations, IAX in trunk mode can reduce voice bandwidth use by one third. IAX2 (version 2) still ships in Asterisk 22 via the `chan_iax2` module and remains useful for Asterisk-to-Asterisk trunks, though it is considered legacy; SIP/PJSIP is preferred for new deployments. IAX2 is specified in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP is a protocol used in conjunction with H.323, SIP, and IAX. Its greatest advantage is scalability. It is configured in the call agent instead of the gateways. This simplifies the configuration process and permits centralized management. However, Asterisk implementation is not complete, and it seems that not many people use it.

### H.323

H.323 is largely being used in VoIP. It is one of the first VoIP protocols and is essential for connecting older VoIP infrastructures based in gateways. H.323 is still the standard in the gateway market, although the market is slowly migrating to SIP. H.323’s strengths include the large market adoption and maturity. H.323’s weaknesses are related to the complexity of implementation and standard bodies’ associated costs.

### Protocol comparison table

The following table summarizes the differences among the session protocols.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## Ein Endpunkt pro Gerät

In Asterisk 22 modelliert der PJSIP‑Stack jedes Telefon, jede Trunk oder jedes Gateway als ein einzelnes **endpoint**‑Objekt in `pjsip.conf`. Ein Endpunkt sowohl platziert als auch empfängt Anrufe; seine Anmeldedaten befinden sich in einem `auth`‑Objekt, seine registrierte Adresse in einem `aor`, und sein Netzwerkpfad in einem `transport`. Sie konfigurieren einen Endpunkt pro Gerät und hängen die benötigten Komponenten an – es gibt keine separate „user“‑ versus „peer“‑Rolle, über die nachgedacht werden muss. (Das vollständige Objektmodell wird in *SIP & PJSIP in depth* behandelt.)

## Codecs und Codec-Übersetzung

Sie verwenden einen Codec, um die Stimme von einer analogen Welle in ein digitales Signal zu konvertieren. Codecs unterscheiden sich in Aspekten wie Klangqualität, Kompressionsrate, Bandbreite und Rechenanforderungen. Dienste, Telefone und Gateways unterstützen in der Regel mehrere dieser Aspekte. Der Codec G.729 ist sehr verbreitet. Er ist nicht Teil des Standard‑Asterisk‑22‑Builds; stattdessen wird er als externes Add‑on‑Modul (`codec_g729`) bereitgestellt, das Sie von Digium (heute Sangoma) herunterladen. Asterisk’s `menuselect`‑Quellcode listet ihn unter `support_level=external` auf und weist eindeutig darauf hin: „Download the g729a codec from Digium. A license must be purchased for this codec.“ Mit anderen Worten, die legale Nutzung von G.729 erfordert den Kauf einer Lizenz pro Kanal. (Eine Open‑Source‑Alternative, `bcg729`, existiert ebenfalls.)

![Pulse Code Modulation (PCM): ein 4000 Hz‑Analogsignal wird 8000 mal pro Sekunde abgetastet (Nyquist‑Theorem) und in einen 64 Kbps‑digitalen Bitstrom codiert.](../images/06-voip-network-fig04.png)

Asterisk 22 unterstützt die folgenden Codecs (unter anderem):

- GSM: 13 Kbps
- iLBC: 13,3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — Standard‑PSTN‑Qualität; ulaw üblich in Nordamerika, alaw üblich in Europa und Lateinamerika
- ITU G.722: 64 Kbps — Wideband (HD‑Voice), gute Qualität bei gleicher Bandbreite wie G.711
- ITU G.723.1: 5,3/6,3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — externes `codec_g729`‑Binärmodul von Digium/Sangoma heruntergeladen (`support_level=external`; eine Lizenz muss zum Einsatz erworben werden)
- Speex: 2,15 bis 44,2 Kbps
- LPC10: 2,4 Kbps
- **Opus**: 6–510 Kbps, variabel — moderner Wideband/Fullband‑Codec; exzellente Qualität und Paketverlust‑Resilienz; wird als externes `codec_opus`‑Binärmodul von Digium/Sangoma bereitgestellt (`support_level=external`; kein Lizenzkauf erforderlich, im Gegensatz zu G.729); empfohlen für WebRTC und moderne SIP‑Endpoints. (Open‑Source‑Build‑Alternativen gibt es auf GitHub.)

Zusätzlich erlaubt Asterisk die Übersetzung zwischen Codecs. In einigen Fällen ist dies nicht möglich, etwa beim g723, das nur im Pass‑Thru‑Modus unterstützt wird. Die Übersetzung von einem Codec zum anderen verbraucht viele CPU‑Ressourcen. Daher sollte man dies nach Möglichkeit ganz vermeiden.

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## Overhead caused by protocol headers

Trotz der Tatsache, dass Codecs nur wenig Bandbreite benötigen, müssen wir den Overhead berücksichtigen, der durch Protokoll‑Header wie Ethernet, IP, UDP und RTP entsteht. Damit hängt die tatsächlich verbrauchte Bandbreite von den verwendeten Headern ab. In einem Ethernet‑Netzwerk ist der Bedarf höher als in einem PPP‑Netzwerk, weil der PPP‑Header kürzer ist als der Ethernet‑Header. Ein einzelnes G.729‑Sprachpaket trägt beispielsweise nur 20 Byte Nutzdaten, wird jedoch in etwa 58 Byte Ethernet‑, IP‑, UDP‑ und RTP‑Header eingewickelt – also dominieren die Header, nicht der Codec, die Bandbreite (siehe Abbildung unten).

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95,2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82,4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82,8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31,2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26,4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26,8 Kbps

Sie können andere Bandbreitenanforderungen leicht mit einem Online‑VoIP‑Bandbreitenrechner wie <https://www.voip.school/bandcalc/bandcalc.php> berechnen.


## Traffic Engineering

Ein Hauptproblem beim Entwurf von VoIP‑Netzwerken ist die Dimensionierung der Leitungsanzahl und der benötigten Bandbreite zu einem bestimmten Ziel, etwa einem entfernten Büro oder einem Dienstanbieter. Es ist ebenfalls wichtig, die Anzahl gleichzeitiger Anrufe von Asterisk zu dimensionieren (Hauptparameter für die Dimensionierung von Asterisk).

### Simplifications

Die primäre und am weitesten verbreitete Vereinfachung besteht darin, die Anzahl der Anrufe nach Benutzertyp zu schätzen. Zum Beispiel:

- Business‑PBXs (ein gleichzeitiger Anruf pro fünf Nebenstellen)
- Residential users (ein gleichzeitiger Anruf pro sechzehn Nutzer)

Example #1 Das Unternehmen hat 120 Nebenstellen am Hauptsitz und zwei Niederlassungen – die erste mit 30 Nebenstellen und die zweite mit 15 Nebenstellen. Unser Ziel ist es, die Anzahl der E1‑Trunks am Hauptsitz und die für das Frame‑Relay‑Netzwerk erforderliche Bandbreite zu dimensionieren.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Number of T1 lines

- Gesamtzahl der Nebenstellen, die T1‑Leitungen nutzen: 120+30+15=165 Leitungen
- Ein Trunk pro fünf Nebenstellen für geschäftliche Nutzung
- Gesamtzahl der Leitungen = 33 oder ungefähr 2 × T1‑Leitungen

1b Bandwidth requirements Wir wählen den g.729‑Codec wegen der Bandbreitenanforderungen, der Klangqualität und des mittleren CPU‑Verbrauchs.

Mit einem Trunk pro fünf Nebenstellen:

- Benötigte Bandbreite für Niederlassung #1 (Frame‑relay): 26.8*6=160.8 Kbps
- Benötigte Bandbreite für Niederlassung #2 (Frame‑relay): 26.8*3= 80.4 Kbps

### Erlang B method

Wenn Sie historische Daten haben, können Sie den Trunk wissenschaftlicher dimensionieren, anstatt zu vereinfachen. Wir verwenden die Arbeit von Agner Karup Erlang (Copenhagen Telephone Company, 1909), der eine Formel zur Berechnung der Leitungsanzahl in einer Trunk‑Gruppe zwischen zwei Städten entwickelte.

Ein **Erlang** ist eine in der Telekommunikation gebräuchliche Verkehrsmessgröße; sie beschreibt das Verkehrsvolumen während einer Stunde. Beispiel: Angenommen, in einer Stunde finden 20 Anrufe statt, durchschnittlich 5 Minuten Gesprächsdauer pro Anruf:

- Verkehrsminuten in der Stunde: 20 × 5 = 100 Minuten
- Stundenverkehr innerhalb einer Stunde: 100 / 60 = **1.66 Erlangs**

Sie können diese Messwerte aus einem Call‑Logger auslesen und zur Planung Ihres Netzwerks sowie zur Berechnung der erforderlichen Leitungsanzahl verwenden. Sobald die Leitungsanzahl bekannt ist, können Sie die Bandbreitenanforderungen berechnen.

**Erlang B** ist die am häufigsten verwendete Methode zur Berechnung der Leitungsanzahl in einer Trunk‑Gruppe. Sie geht davon aus, dass Anrufe zufällig (Poisson‑Verteilung) eintreffen und blockierte Anrufe sofort abgeworfen werden. Sie erfordert, dass Sie den **Busy Hour Traffic (BHT)** kennen, den Sie aus einem Call‑Logger erhalten oder als Vereinfachung schätzen können: BHT = 17 % der Anrufminuten eines Tages.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Eine weitere wichtige Variable ist der Grade of Service (GoS), der die Wahrscheinlichkeit blockierter Anrufe wegen Leitungsengpässen definiert. Sie können diesen Parameter festlegen, üblich sind 0.05 (5 % verlorene Anrufe) oder 0.01 (1 % verlorene Anrufe). Example #1: Unter Verwendung des zuvor in diesem Abschnitt vorgestellten Hauptsitz‑und‑zwei‑Niederlassungen‑Beispiels geben wir Ihnen einige Daten zu den Verkehrsmustern. Aus dem Call‑Logger haben wir diese Daten ermittelt: Daten aus dem Call‑Logger

## Reduzierung der für VoIP erforderlichen Bandbreite

Drei Methoden können verwendet werden, um die für VoIP‑Gespräche erforderliche Bandbreite zu reduzieren:

- RTP‑Header‑Kompression
- IAX Trunked
- VoIP‑Payload

### RTP Header Compression

In Frame‑Relay‑ und PPP‑Netzwerken können Sie RTP‑Header‑Kompression einsetzen. RTP‑Header‑Kompression wurde in RFC 2508 definiert. Es ist ein IETF‑Standard, der in mehreren Routern verfügbar ist. Seien Sie jedoch vorsichtig, da einige Router einen anderen Funktionsumfang benötigen, damit diese Ressource verfügbar ist. Die Auswirkung der Verwendung von RTP‑Header‑Kompression ist beeindruckend, da sie die in unserem Beispiel benötigte Bandbreite von 26,8 Kbps pro Sprachgespräch auf 11,2 Kbps reduziert – eine Verringerung um 58,2 %!

### IAX2 trunk mode

Wenn Sie zwei Asterisk‑Server verbinden, können Sie das IAX2‑Protokoll im Trunk‑Modus verwenden. Diese revolutionäre Technologie benötigt keine speziellen Router und kann auf jede Art von Datenlink angewendet werden.

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

Der IAX2‑Trunk‑Modus verwendet dieselben Header vom zweiten Anruf und darüber hinaus. Bei Verwendung von g729 in einer PPP‑Verbindung verbraucht der erste Anruf 30 Kbps Bandbreite, während der zweite Anruf denselben Header wie der erste nutzt und die für den zusätzlichen Anruf notwendige Bandbreite auf 9,6 Kbps reduziert. Wir können die erforderliche Bandbreite im Trunk‑Modus wie folgt berechnen: Branch #1 (11 calls) Bandwidth = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Branch #2 (8 calls) Bandwidth = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps Der erste Anruf verwendet 31,2 Kbps, der nächste 9,6 Kbps und so weiter.

### Increasing the Voice Payload

Diese Methode ist sehr verbreitet, wenn VoIP‑Gateways über das Internet eingesetzt werden. Bei Verwendung einer größeren Payload opfern Sie Latenz zugunsten einer reduzierten Bandbreite. Sie können die RTP‑Packetisierung ändern, indem Sie die Frame‑Größe an den Codec in der allow‑Anweisung anhängen.

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

Beispiel:

```
allow=ulaw:30
```

Die Zahl nach dem Doppelpunkt ist das Packetisierungsintervall in Millisekunden – wie viel Sprache in jedem RTP‑Paket transportiert wird. Ein größerer Wert amortisiert den festen Header‑Overhead über mehr Audio (weniger Bandbreite) auf Kosten zusätzlicher Latenz. Jeder Codec hat seine eigene minimale, maximale und Standard‑Frame‑Größe; G.711 (`ulaw`/`alaw`) verwendet beispielsweise standardmäßig 20 ms.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Asterisk VoIP über Kanäle verarbeitet. Es unterstützt SIP (via `chan_pjsip` in Asterisk 22) und IAX2; H.323 ist nur über das Community‑Add‑on `ooh323` verfügbar, und die älteren MGCP‑ und SCCP‑(Skinny)‑Kanäle gehören nicht mehr zu einem Standard‑Build von Asterisk 22. Sie haben verglichen und gelernt, wie man ein Signalisierungsprotokoll und einen Codec für VoIP‑Kanäle auswählt. IAX2 ist bandbreiteneffizienter und kann NAT leicht durchqueren. SIP/PJSIP ist das am meisten unterstützte Protokoll bei Drittanbieter‑Telefon‑ und Gateway‑Herstellern und ist der einzige SIP‑Kanaltreiber in Asterisk 22. Das H.323‑Protokoll ist das älteste und sollte verwendet werden, um sich mit Legacy‑VoIP‑Infrastrukturen zu verbinden. Im Abschnitt Traffic Engineering haben wir gelernt, wie man ein VoIP‑Netzwerk plant und dimensioniert.

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
