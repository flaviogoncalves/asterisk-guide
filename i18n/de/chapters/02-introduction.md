# Einführung in Asterisk PBX

Die Beliebtheit von sofort einsatzbereiten Distributionen wie FreePBX und Issabel ist in letzter Zeit stark gewachsen. In diesem Buch behandeln wir das klassische Asterisk, das die Grundlage für das Verständnis dieser Distributionen bildet. Asterisk PBX ist Open‑Source‑Software, die einen gewöhnlichen PC in eine leistungsfähige Multi‑Protokoll‑PBX verwandeln kann. In diesem Kapitel lernen wir die Möglichkeiten dieser neuen Technologie und ihre Grundarchitektur kennen.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- zu erklären, was Asterisk ist und was es tut;
- die Rolle von Digium™ und seinem Nachfolger Sangoma zu beschreiben;
- die Grundarchitektur von Asterisk und seine Komponenten zu erkennen;
- mehrere Anwendungsszenarien zu benennen; und
- Quellen für Informationen und Hilfe zu identifizieren.

## What is Asterisk

Asterisk ist Open‑Source‑PBX‑Software, die einen gewöhnlichen Computer in eine voll ausgestattete PBX für Heimanwender, Unternehmen, VoIP‑Dienstanbieter und Telefonunternehmen verwandelt. Asterisk ist zugleich eine Open‑Source‑Community und ein Projekt, das von Sangoma Technologies gesponsert wird (die 2018 Digium übernommen haben). Sie können Asterisk frei nutzen und an Ihre Bedürfnisse anpassen. Asterisk ermöglicht die Echtzeit‑Verbindung zwischen PSTN‑ und VoIP‑Netzwerken. Da Asterisk weit mehr als eine PBX ist, erhalten Sie nicht nur ein herausragendes Upgrade Ihrer bestehenden PBX, sondern können auch neue Dinge in der Telefonie tun, wie zum Beispiel:

- Mitarbeiter, die von zu Hause aus arbeiten, über das Breitband‑Internet mit einer Office‑PBX verbinden;
- Mehrere Büros an verschiedenen Standorten über ein IP‑Netzwerk, ein privates Netzwerk oder sogar über das Internet selbst verbinden;
- Ihren Mitarbeitern eine Voicemail bereitstellen, die in Web und E‑Mail integriert ist;
- Anwendungen wie IVRs erstellen, die Verbindungen zu Ihrem Bestellsystem oder anderen Anwendungen ermöglichen;
- Reisenden Benutzern Zugriff auf die Unternehmens‑PBX von überall mit einer einfachen Breitband‑ oder VPN‑Verbindung gewähren; und
- vieles mehr....

Asterisk enthält mehrere fortgeschrittene Funktionen, die zuvor nur in High‑End‑Systemen zu finden waren, wie:

- Musik für Kunden, die in Warteschlangen halten, mit Unterstützung für Media‑Streaming und MP3‑Dateien;
- Anrufwarteschlangen, bei denen ein Team von Agenten Anrufe entgegennehmen und Warteschlangen überwachen kann;
- Integration von Text‑zu‑Sprache und Spracherkennung;
- Detaillierte Aufzeichnungen, die sowohl in Textdateien als auch in SQL‑Datenbanken übertragen werden; und
- PSTN‑Konnektivität über digitale und analoge Leitungen.

## Was ist AsteriskNOW (historisch) und FreePBX

Asterisk in seiner reinsten Form, auch bekannt als „classic asterisk“ (Debian‑Paketbezeichnung), wird eher als Entwicklungswerkzeug denn als fertiges Produkt angesehen. AsteriskNOW war eine Initiative, Asterisk zu einer Soft‑Appliance zu machen. Die Distribution enthielt CentOS als Betriebssystem und FreePBX als grafische Oberfläche. AsteriskNOW wurde inzwischen eingestellt.

Heute ist die standardmäßige schlüsselfertige Asterisk‑Distribution **FreePBX** (gepflegt von Sangoma), die Asterisk mit einer webbasierten Administrations‑GUI und einem Modul‑Ökosystem bündelt. FreePBX ist gemäß GPL lizenziert und kann kostenlos von www.freepbx.org heruntergeladen werden. Für kommerzielle Einsätze bietet Sangoma zudem **FreePBX Distro** (ein komplettes Linux‑Image) und das kommerzielle Produkt **PBXact** an.

## Rolle von Digium™ und Sangoma

Digium, ein Unternehmen mit Sitz in Huntsville, Alabama, war seit seiner Gründung im Jahr 1999 der Erfinder und Hauptentwickler von Asterisk. Neben der Hauptsponsorship für die Asterisk‑Entwicklung stellte Digium Telefonie‑Interface‑Karten und weitere Hardware für Asterisk‑PBXs her und entwickelte kommerzielle Produkte wie Switchvox (gerichtet an den SMB‑Markt). 2018 wurde Digium von **Sangoma Technologies**, einem kanadischen Unternehmen für Unified Communications, übernommen. Seit der Übernahme unterstützt Sangoma die Asterisk‑Entwicklung weiterhin und fungiert als primärer Verwalter, wobei das Open‑Source‑Projekt unter www.asterisk.org gepflegt wird.

Historisch bot Digium Asterisk unter drei Arten von Lizenzvereinbarungen an:

- General Public License (GPL) Asterisk. Dies ist die am häufigsten genutzte Version. Sie enthält alle Funktionen und darf gemäß den Bedingungen der GPL‑Lizenz frei verwendet und modifiziert werden.
- Asterisk Business Edition war eine kommerzielle Version von Asterisk. Einige Unternehmen nutzten die Business Edition, weil sie die GPL‑Lizenz nicht verwenden wollten oder konnten – meist weil sie ihren Quellcode nicht zusammen mit Asterisk veröffentlichen wollten. **Hinweis:** Asterisk Business Edition wurde eingestellt; heute wird Asterisk ausschließlich unter der GPL vertrieben.
- Asterisk OEM‑Lizenzierung. Nachdem Digium den Einzelhandelsverkauf der Asterisk Business Edition eingestellt hatte, lizenzierte es diese kommerzielle Edition weiterhin an OEM‑Kunden – Gerätehersteller, die proprietäre Produkte auf Basis von Asterisk bauen wollten, ohne ihren eigenen Quellcode unter der GPL zu veröffentlichen.

### Das Zapata‑Projekt und seine Beziehung zu Asterisk

Das Zapata‑Projekt wurde von Jim Dixon entwickelt, der ebenfalls für das revolutionäre Hardware‑Design verantwortlich war, das mit Asterisk verwendet wird. Die Hardware ist ebenfalls Open‑Source; sie kann daher von jedem Unternehmen genutzt werden, und heute produzieren mehrere Hersteller Karten, die mit dieser Architektur kompatibel sind.

Das Zapata‑Projekt erzeugte eine Architektur namens Zaptel, später umbenannt in DAHDI (Digium/Asterisk Hardware Device Interface). Einer der Hauptvorteile dieser Architektur ist die Möglichkeit, die PC‑CPU zur Verarbeitung von Medien‑Streaming, Echo‑Unterdrückung und Transkodierung zu nutzen. Im Gegensatz dazu verwenden die meisten bestehenden Karten digitale Signalprozessoren (DSP), um diese Aufgaben zu erledigen. Der Einsatz der PC‑CPU anstelle dedizierter DSPs senkt den Preis der Karte dramatisch. Daher sind diese Karten deutlich günstiger als zuvor verfügbare Schnittstellen anderer Hersteller. Auf der anderen Seite benötigen diese Karten viel CPU; ein Missbrauch der PC‑CPU kann die Sprachqualität erheblich beeinträchtigen. Kürzlich hat Digium eine Coprozessor‑Karte eingeführt, die DSPs zum Kodieren und Dekodieren von G.729 und G.723 verwendet und so eine bessere Skalierbarkeit für eine große Anzahl von Kanälen ermöglicht.

## Why Asterisk?

I remember my first contact with Asterisk. Usually, the first reaction to something new—especially something that competes with what you already know—is to reject it! This is exactly what happened in 2003. Asterisk was competing with a solution that I was selling to a customer (4 E1 VoIP Gateway), and it was ten times less expensive than what I was charging for the solution I already knew. This disproportionate price led me to start studying Asterisk in order to identify potential pitfalls and drawbacks. For example, I found that the PC CPU at that time would not support 120 g.729 simultaneous sections, at the end of the day, I won the proposal with my Gateway solution.

However, this exercise led me to the discovery that Asterisk could solve a variety of very expensive problems for my customer base. We were in trouble with expensive quotes for IVR, unified messaging, call recording, and dialers; with appropriate dimensioning, the CPU problems could be worked around. Indeed, in just three years Asterisk became the flagship product of my company (I actually decided to open another company just for the Asterisk business). In my opinion, Asterisk is a revolution in telecommunication that represents to IP telephony what Apache represents to web services.

### Extreme cost reduction

If you compare a traditional PBX with Asterisk in regard to digital interfaces and phones, Asterisk is slightly cheaper than those PBXs. However, Asterisk really pays off when you add advanced features such as voicemail, ACD, IVR and CTI. With these advanced features, Asterisk becomes significantly less expensive than traditional PBXs. In fact, comparing Asterisk PBXs with low-end analog PBXs is unfair because Asterisk offers so many features not available in low-end analog systems.

### Telephony system control and independence

One of customers’ most often-quoted benefits of asterisk is the independence that it provides. Some of today’s manufacturers do not even give the customer the system’s password or the configuration documentation. With Asterisk's “do-it-yourself” approach, the user achieves total freedom; as a bonus, the user has access to a standard interface.

### Easy and rapid development environment

Asterisk can be extended using script languages like PHP and Perl with AMI and AGI interfaces. Asterisk is open-source, and its source code can be modified by the user. The source code is written mostly in ANSI C programming language.

### Feature rich

Asterisk has several features that are either not found or optional in traditional PBXs (e.g., voicemail, CTI, ACD, IVR, built-in music on hold, and recording). The costs of these features in some platforms exceed the price of the platform itself.

### Dynamic content on the phone

Asterisk is programmed using C language and other languages common in today's development environment. The possibility to provide dynamic content is practically limitless.

### Flexible and powerful dial plan

Another Asterisk breakthrough is its powerful dial plan. In traditional PBXs, even simple features like least cost routing (LCR) are either not feasible or optional. With Asterisk, choosing the best route is easy and clean.

### Open-source running on top of Linux

One of the greatest features of Asterisk is its community. Several resources are available, including the official Asterisk documentation (docs.asterisk.org), the community-maintained VoIP-Info wiki (www.voip-info.org <http://www.voip-info.org>), e-mail distribution lists, and forums. As Asterisk becomes increasingly adopted, bugs are found and fixed quickly. With a large user base and an active development team, Asterisk is among the most widely tested PBX platforms in the world, which helps keep the code base stable and mature.

### Asterisk architecture limitations

Some limitations in Asterisk stem from the use of the Zapata telephony design. In this design, Asterisk uses the PC CPU to process voice channels instead of dedicated digital signal processors (DSPs), which are common in other platforms. Although this allows for a huge cost reduction in hardware interface, the system becomes dependent on the PC CPU. My recommendation is to run Asterisk in a dedicated machine and be conservative about hardware dimensioning. You can also use Asterisk in a separate VLAN to avoid excessive broadcasts that consume the CPU (broadcast storms caused by loops or viruses). Some newer interface cards from several vendors are now including DSPs to process echo cancellation, codecs, and other features, which will make Asterisk even better.

## Main objections to Asterisk PBX

Es ist üblich, Einwände gegen die Einführung von Asterisk zu hören, die wir hier behandeln werden.

### Asterisk’s market share is too small

Der Marktanteil wird üblicherweise anhand der verkauften PBXs gemessen. Diese Statistiken werden im Allgemeinen von den größten Vertriebspartnern bezogen. Asterisk ist freie Software, die heruntergeladen und eingesetzt werden kann, ohne dass ein Verkauf erfasst wird, sodass es in diesen Zahlen systematisch unterrepräsentiert ist. Trotzdem treibt Asterisk eine sehr große installierte Basis weltweit an – von Ein-Server‑Büro‑PBXs bis hin zu großen Carrier‑ und Contact‑Center‑Installationen – und bleibt die dominante Engine hinter dem Open‑Source‑PBX‑Ökosystem (einschließlich schlüsselfertiger Distributionen wie FreePBX).

### If it is free, how does the manufacturer survive?

Tatsächlich gibt es im traditionellen Sinne keinen Open‑Source‑Software‑Hersteller. Digium entwickelte Asterisk seit 1999 und finanzierte sich durch den Verkauf von Telefonie‑Interface‑Karten, kommerziellen PBX‑Produkten wie Switchvox und zugehöriger Software. 2018 wurde Digium von Sangoma Technologies übernommen. Sangoma finanziert weiterhin die Asterisk‑Entwicklung und erzielt Einnahmen durch kommerzielle Produkte (FreePBX‑Kommerzmodule, PBXact, Switchvox), Hardware‑Verkäufe und professionelle Dienstleistungen.

### It is hard to find technical support!

Sangoma bietet kommerziellen technischen Support für Asterisk über sein Partner‑Ökosystem und direkt über seine Produktangebote. Ein globales Netzwerk zertifizierter Fachleute leistet First‑Line‑Support und professionelle Services. Der Community‑Support bleibt aktiv über die Asterisk‑Foren und Mailing‑Listen unter www.asterisk.org.

### Does Asterisk support more than 200 extensions?

Ja, absolut. Ein einzelner gut dimensionierter Asterisk‑Server kann eine große Anzahl von Extensions verarbeiten, und Asterisk skaliert weiter, indem Benutzer über mehrere Server mit Load‑Balancing und Failover verteilt werden, was große Multi‑Site‑Deployments ermöglicht.

### Only “geeks” are able to install Asterisk

Mit FreePBX (verfügbar als eigenständige Distribution von Sangoma) können selbst Fachleute mit begrenztem Linux‑Wissen eine PBX mittlerer Komplexität installieren und konfigurieren. Mit Hilfe einer GUI ist es möglich, eine komplette PBX in nur wenigen Stunden zu konfigurieren.

### What if the server fails?

Einer der Hauptvorteile von Asterisk ist seine Fähigkeit, in fehlertoleranten Systemen zu laufen. Es ist relativ einfach und kostengünstig, zwei Server parallel zu betreiben. Ich fordere Sie heraus, dies mit einer konventionellen PBX zu versuchen!

### Our company does not use open-source software

Ihr Unternehmen nutzt wahrscheinlich Open‑Source‑Software, ohne es zu merken. Mehrere Appliances verwenden Linux als Betriebssystem. Darüber hinaus stehen kommerzieller Support und verwaltete Deployments von Sangoma und seinem zertifizierten Partnernetzwerk zur Verfügung.

### Using the PC's CPU to process signaling and media is not recommended

Asterisk nutzt die CPU des Servers, um Signalisierung und Medien für Sprachkanäle zu verarbeiten, anstatt dedizierte DSPs zu verwenden. Obwohl dies eine Kostenreduktion von bis zu dem Fünffachen ermöglicht, macht es das System abhängig von der Leistung der Haupt‑CPU. Mit der richtigen Dimensionierung ist Asterisk in der Lage, große Volumina zu bewältigen. Wenn Sie die Haupt‑CPU dennoch von diesen Aufgaben entlasten möchten, können Sie auch Hardware‑Echo‑Cancellation und sogar Transcoder‑Karten einsetzen, wie die Sangoma (früher Digium) TC400B, die auf DSPs basiert.

## Asterisk Architecture

This section will explain how Asterisk’s architecture works. The figure below shows the basic Asterisk architecture. Next, we will explain architecture-related concepts, including channels, codecs, and applications.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

A channel is the equivalent of a telephone line, but in a digital format. It usually consists of an analog or digital (TDM) signaling system or a combination of codec and signaling protocol (e.g., SIP-GSM, IAX-uLaw). Initially, all telephony connections were analog and susceptible to echo and noise. Later, most systems were converted to digital systems, with the analogical sound converted into a digital format using pulse code modulation (PCM) in most cases. This format allows voice transmission in 64 kilobits/second without compression.

Channels interfacing with the Public Switched Telephone Network (PSTN):

- `chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards from Sangoma (formerly Digium), Xorcom, and others. Built separately against DAHDI — see the *Legacy channels* chapter.

Channels interfacing with Voice over IP:

- `chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS. Dial string: `PJSIP/endpoint_name`. (**Note:** the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22. See *Building your first PBX with PJSIP* for configuration.)
- `chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy; SIP/PJSIP is preferred for new deployments. Dial string: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support) but rarely used.

The older VoIP channels are no longer part of a standard Asterisk 22 build: `chan_h323` (H.323) survives only as the community `ooh323` add-on, and `chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set. If you must interwork with those protocols, a gateway in front of Asterisk is the usual approach.

Miscellaneous channels:

- **Local**: a pseudo-channel (built into the core) that loops back into the dial plan in a different context — useful for recursive routing and for fanning a call out to multiple destinations. Dial string: `Local/extension@context`.

### Codec and codec translation

We usually try to put as many voice connections as possible in a data network. Codecs enable new features in digital voice, including compression, which is one of the most important features as it allows compression rates larger than 8 to 1. Many codecs also define features such as voice activity detection (silence suppression), packet loss concealment, and comfort noise generation, though Asterisk itself does not generate comfort noise or perform silence suppression. Several codecs are available for Asterisk and can be transparently translated from one to another. Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another. Some codecs in Asterisk are supported only in pass-through mode; these codecs cannot be translated. To verify which codecs are installed in your system, you can use the console command:

```
CLI>core show translation
```

The following codecs are supported:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Only pass-through mode
- G.726 - (16/24/32/40kbps)
- G.729 - Binary codec module distributed by Sangoma; the download is free of charge, but lawful use requires purchasing a per-channel license (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

Sending data from one phone to another should be easy provided that the data find a path to the other phone on their own. Unfortunately, it doesn't happen this way, and a signaling protocol is necessary in order to establish connections between phones, discover end devices, and implement telephony signaling. SIP is the dominant signaling protocol in modern deployments and is the only SIP channel available in Asterisk 22 LTS (via chan_pjsip). IAX2 is still available but considered legacy. Asterisk supports the following protocols.

- SIP — via `chan_pjsip`
- IAX2 — legacy, still ships in Asterisk 22
- UNISTIM — Nortel/Avaya phones (extended support)
- H.323, MGCP, and SCCP (Cisco Skinny) — legacy protocols no longer in a standard Asterisk 22 build (H.323 only via the community `ooh323` add-on)

### Applications

To bridge calls from one phone to another, the application dial() is used. Most Asterisk features (e.g., voicemail and conferencing) are implemented as applications. You can see available Asterisk applications by using the core show applications console command.

```
CLI>core show applications
```

Sie können Anwendungen aus Asterisk‑Add‑Ons, von Drittanbietern oder sogar solche, die Sie selbst entwickeln, hinzufügen.

## Überblick über ein Asterisk‑System

Asterisk ist eine Open‑Source‑PBX, die wie eine hybride PBX funktioniert und Technologien wie TDM‑ und IP‑Telefonie integriert. Asterisk ist bereit, Funktionen wie Interactive Voice Response (IVR) und Automatic Call Distribution (ACD) zu implementieren; zudem, wie bereits erwähnt, ist es offen für die Entwicklung neuer Anwendungen. Diese Abbildung zeigt, wie Asterisk über analoge und digitale Schnittstellen mit dem PSTN und bestehenden PBXs verbunden ist und gleichzeitig analoge sowie IP‑Telefone unterstützt. Es kann als Soft‑Switch, Media‑Gateway, Voicemail und Audio‑Konferenz fungieren und verfügt zudem über integrierte Music‑on‑Hold.

![Überblick über ein Asterisk‑System](../images/01-introduction-fig02.png)

## Vergleich der alten und der neuen Welt

Im alten Soft‑Switch‑Modell wurden alle Komponenten einzeln verkauft, das bedeutet, dass Sie jede Komponente separat erwerben und dann in die PBX‑ oder Soft‑Switch‑Umgebung integrieren mussten. Die Kosten und Risiken waren hoch und die meisten Geräte waren proprietär.

![Die alte Welt: Komponenten separat gekauft und integriert](../images/01-introduction-fig03.png)

### Telefonie mit Asterisk

Alle Funktionen sind in der Asterisk‑Plattform integriert, entweder in derselben oder in verschiedenen Boxen je nach Dimensionierung, und alle sind GPL‑lizenziert. Manchmal ist es einfacher, Asterisk zu installieren, als einige der gängigen IP‑PBXs zu lizenzieren.

![Telefonie mit Asterisk: Die Funktionen sind integriert](../images/01-introduction-fig04.png)

## Building a test system

When implementing an Asterisk solution, our first step is generally to build a test system. The goal is a minimal **1×1 PBX** — one phone that can call another — so you can try out endpoints, dialplan, and features before touching production. Today this is entirely software: you do not need any telephony hardware.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### The modern way: a software lab (recommended)

The fastest test system is Asterisk 22 running in a container or virtual machine, with **softphones** for the endpoints and, optionally, a **SIP trunk** to reach the public network:

- **Asterisk 22** on a small Linux box, VM, or Docker container. This book ships a ready-made Docker lab (see the lab guide) that boots a fully configured Asterisk 22 with a single command — no compilation, no hardware.
- **Two softphones** registered as PJSIP endpoints, so you can place a real call between them. Throughout this book we use the **SipPulse Softphone** (free download: <https://www.sippulse.com/produtos/softphone>), available for desktop and mobile.
- **A SIP trunk** (optional) from a VoIP provider, for when you want to reach the PSTN. No card and no analog line — just credentials.

This is how every example in this book is built and verified, and you can reproduce it on any laptop.

### The legacy way: analog/digital cards

Before VoIP, a test PBX needed physical interfaces: an **FXO** port to connect to an existing telephone line and an **FXS** port to connect an analog phone, which together gave you a 1×1 PBX. A single card carrying one FXO and one FXS interface was the classic starter kit. These DAHDI-based cards (from Sangoma, formerly Digium) still exist for sites that must terminate analog or T1/E1 lines, but they are niche today — most deployments are pure VoIP. If you only need to connect analog phones or lines, see the *Legacy Channels* chapter; otherwise you can skip telephony hardware entirely.

## Asterisk-Szenarien

Asterisk kann in mehreren verschiedenen Szenarien eingesetzt werden. Wir werden einige davon auflisten und die Vorteile sowie mögliche Einschränkungen jedes einzelnen erläutern.

### IP PBX

Das häufigste Szenario ist die Installation einer neuen oder der Austausch einer bestehenden PBX. Wenn Sie Asterisk mit einigen anderen Alternativen vergleichen, werden Sie feststellen, dass es günstiger und funktionsreicher ist als die meisten derzeit auf dem Markt erhältlichen PBXs. Mehrere Unternehmen stellen ihre Spezifikationen jetzt auf Asterisk um, anstatt andere Marken‑PBXs zu verwenden.

![Asterisk als IP-PBX](../images/01-introduction-fig06.png)

### IP-fähige Legacy-PBXs

Das folgende Bild veranschaulicht eine der am häufigsten verwendeten Aufbauten. Große Unternehmen wollen im Allgemeinen kein erhebliches Risiko eingehen, wenn sie in neue Technologien investieren, und gleichzeitig ihre Investitionen in Altgeräte erhalten. Die IP‑Aktivierung von Legacy‑PBX kann sehr teuer sein; daher kann die Anbindung einer Asterisk‑PBX über T1/E1‑Leitungen eine gute Alternative für kostenbewusste Kunden sein. Ein weiterer Vorteil ist die Möglichkeit, sich mit einem VoIP‑Dienstanbieter zu verbinden, der bessere Telefoniekonditionen bietet.

![IP-Aktivierung einer Legacy-PBX](../images/01-introduction-fig07.png)

### Gebührenumgehung

Eine sehr nützliche Anwendung für VoIP ist das Verbinden von Niederlassungen über das Internet oder ein WAN. Die Nutzung einer bestehenden Datenverbindung ermöglicht es, die bei Telekommunikationsverbindungen zwischen Hauptsitz und Niederlassungen anfallenden Gebühren zu umgehen.

![Gebührenumgehung zwischen Büros über ein WAN](../images/01-introduction-fig08.png)

### Anwendungsserver (IVR, Konferenz, Voicemail)

Asterisk kann als Anwendungs‑Server für die bestehende PBX verwendet werden oder direkt an die PSTN angeschlossen werden. Asterisk bietet Dienste wie Voicemail, Faxempfang, Anrufaufzeichnung, IVR, das an eine Datenbank angebunden ist, und einen Audio‑Konferenz‑Server. Wenn Sie Voicemail und Fax in einen bestehenden E‑Mail‑Server integrieren, erhalten Sie ein einheitliches Messaging‑System, das in der Regel eine teure Lösung darstellt. Die Nutzung von Asterisk als Anwendungs‑Server ermöglicht eine extreme Kostenreduktion im Vergleich zu anderen Lösungen.

![Asterisk als Anwendungsserver](../images/01-introduction-fig09.png)

### Media-Gateway

Most voice-over IP service providers use an SIP proxy to host all registration, location, and authentication of SIP users. They still have to send calls to the PSTN directly or route it through a wholesale call termination provider using an SIP or H.323 voice-over IP connection. Asterisk can act as a back-to-back user agent (B2BUA) or media gateway, replacing very expensive soft switches or media gateways. Compare the price of a four E1/T1 gateway from the main market manufacturers with Asterisk. The Asterisk solution can cost several times less than other solutions and is capable of translating signaling protocols (H.323, SIP, IAX…) and codecs (G.711, G.729…).

![Asterisk als Mediengateway](../images/01-introduction-fig10.png)

### Contact Center Plattform

Ein Contact Center ist eine sehr komplexe Lösung, die mehrere Technologien kombiniert, wie automatische Anrufverteilung (ACD), Interactive Voice Response (IVR) und Anrufüberwachung. Grundsätzlich stehen drei Arten von Contact Centern zur Verfügung: inbound, outbound und blended.

Inbound contact centers sind sehr anspruchsvoll und benötigen in der Regel ACD, IVR, CTI, Aufzeichnung, Überwachung und Berichte. Asterisk hat ein integriertes ACD, um die Anrufe zu queueen. IVR kann mit dem Asterisk Gateway Interface (AGI) oder internen Mechanismen wie der Anwendung background() umgesetzt werden. Computer‑Telephony‑Integration (CTI) wird über das Asterisk Manager Interface (AMI) realisiert; Aufzeichnung und Reporting sind in Asterisk eingebaut.

Für ein ausgehendes Contact Center ist ein Predictive‑ oder Power‑Dialer einer der Hauptkomponenten. Obwohl mehrere Dialer für das Open‑Source‑Asterisk verfügbar sind, ist es nicht schwer, einen eigenen für die Plattform zu erstellen, wenn Sie das wünschen. Ein gemischtes Contact Center ermöglicht gleichzeitigen eingehenden und ausgehenden Betrieb und spart Geld, indem die Zeit der Agenten besser genutzt wird. Es ist möglich, Asterisk und seinen ACD‑Mechanismus zu verwenden, um eine gemischte Lösung zu implementieren.

![Eine Asterisk Contact-Center-Plattform](../images/01-introduction-fig11.png)

## Informationen finden und Hilfe

Dieser Abschnitt bietet einige der wichtigsten Informationsquellen zu Asterisk.

- Asterisk’s offizielle Website: <https://www.asterisk.org> Hier finden Sie Informationen zu:
- Documentation & Wiki -> <https://docs.asterisk.org>
- Community-Forum -> <https://community.asterisk.org>
- Bug tracking -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legacy, largely superseded by docs.asterisk.org) -> <https://wiki.asterisk.org>

### Community-Forum

Das Asterisk Community-Forum hat die alten Mailinglisten weitgehend ersetzt und ist der Ort, um Fragen zu stellen. Versuchen Sie, so viele Informationen wie möglich zu sammeln, bevor Sie posten. Niemand wird Ihnen helfen, wenn Sie Ihre Hausaufgaben nicht gemacht haben – versuchen Sie mindestens einmal, das Problem selbst zu lösen.

- <https://community.asterisk.org>

## Summary

Asterisk ist eine nach GPL lizenzierte Software, die einen gewöhnlichen PC zu einer leistungsfähigen IP‑PBX‑Plattform macht. Digiums Mark Spencer entwickelte Asterisk Ende der 1990er Jahre, und Digium finanzierte sich durch den Verkauf von Asterisk‑bezogener Hardware und kommerziellen Produkten. Digium wurde 2018 von Sangoma Technologies übernommen; Sangoma unterstützt nun die Entwicklung von Asterisk. Das Design der Hardware‑Schnittstelle stammt aus dem Zapata‑Projekt von Jim Dixon, aus dem DAHDI hervorging.

Die Asterisk‑Architektur besteht aus den folgenden Hauptkomponenten:

- CHANNELS: Analog, digital oder Voice‑over‑IP. In Asterisk 22 LTS wird SIP ausschließlich von `chan_pjsip` verarbeitet.
- PROTOCOLS: Kommunikationsprotokolle, die für die Signalisierung der Anrufe verantwortlich sind, einschließlich SIP (via PJSIP), H.323, MGCP und IAX2.
- CODECS: Übersetzen digitale Sprachformate und ermöglichen Kompression sowie Concealment von Paketverlusten. Beachten Sie, dass Asterisk selbst keine Stummsuppression (Voice Activity Detection) oder Comfort‑Noise‑Erzeugung durchführt; wenn Endpunkte VAD verwenden, sollte Comfort‑Noise auf der Client‑Seite deaktiviert werden.
- APPLICATIONS: Verantwortlich für die PBX‑Funktionalität von Asterisk. Konferenz, Voicemail und Fax sind Beispiele für Asterisk‑Anwendungen.

Asterisk kann in verschiedenen Szenarien eingesetzt werden, von einer kleinen IP‑PBX bis hin zu einem anspruchsvollen Contact‑Center. Hilfe finden Sie leicht unter www.asterisk.org und docs.asterisk.org.

## Quiz

1. Welches Unternehmen hat Digium im Jahr 2018 übernommen und ist jetzt der Hauptverwalter des Open‑Source‑Projekts Asterisk?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. In Asterisk 22 LTS, welcher Kanal‑Treiber stellt SIP‑Konnektivität bereit?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Wahr oder Falsch: Der `chan_sip`‑Kanal‑Treiber wurde in Asterisk 21 entfernt und ist in einem Standard‑Asterisk 22‑Build nicht mehr enthalten.

4. Welche der folgenden Kanäle/Protokolle sind **nicht mehr** Teil eines Standard‑Asterisk 22‑Builds? (Wählen Sie alle zutreffenden aus.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, nur noch als Community‑`ooh323`‑Add‑on erhalten)

5. Die Hardware‑Architektur des Zapata‑Projekts, ursprünglich Zaptel genannt, wurde später in ____ umbenannt.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Wenn Asterisk Audio von einem Codec in einen anderen konvertieren muss, welches interne Stream‑Format wird dafür verwendet?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Laut Kapitel, wie ist die Lizenzsituation des von Sangoma vertriebenen G.729‑Codec‑Moduls?
   - A. Es ist GPL und völlig kostenlos für jede Nutzung.
   - B. Der Download ist kostenlos, aber die legale Nutzung erfordert den Kauf einer pro‑Kanal‑Lizenz.
   - C. Es kann überhaupt nicht bezogen werden, ohne die Asterisk Business Edition zu kaufen.
   - D. Es funktioniert nur im Pass‑Through‑Modus und kann nicht installiert werden.

8. Welche Asterisk‑Anwendung wird verwendet, um einen Anruf von einem Telefon zu einem anderen zu verbinden?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Was ist der `Local`‑Kanal in Asterisk?
   - A. Eine Hardware‑FXS‑Schnittstelle für analoge Telefone.
   - B. Ein SIP‑Trunk zu einem lokalen Dienstanbieter.
   - C. Ein Pseudo‑Kanal, der einen Anruf zurück in den Dialplan in einem anderen Kontext schleift.
   - D. Ein Codec für On‑Net‑Anrufe.

10. In welchem Anwendungsszenario fungiert Asterisk als Back‑to‑Back‑User‑Agent (B2BUA) und übersetzt zwischen Signalisierungs‑Protokollen und Codecs, um teure SoftSwitches zu ersetzen?
    - A. IP‑Aktivierung einer Legacy‑PBX
    - B. Toll‑Bypass
    - C. Media‑Gateway
    - D. Contact‑Center‑Plattform

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
