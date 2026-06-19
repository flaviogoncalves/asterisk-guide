# Einführung in die Asterisk PBX

Die Popularität von sofort einsatzbereiten Distributionen wie FreePBX und Issabel ist in letzter Zeit gewachsen. In diesem Buch behandeln wir das klassische Asterisk, welches die Grundlage für das Verständnis dieser Distributionen bildet. Asterisk PBX ist eine Open-Source-Software, die einen gewöhnlichen PC in eine leistungsstarke Multiprotokoll-PBX verwandeln kann. In diesem Kapitel lernen wir die Möglichkeiten dieser neuen Technologie und ihre grundlegende Architektur kennen.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Zu erklären, was Asterisk ist und was es tut;
- Die Rolle von Digium™ und dessen Nachfolger Sangoma zu beschreiben;
- Die grundlegende Architektur von Asterisk und seine Komponenten zu erkennen;
- Mehrere Einsatzszenarien aufzuzeigen; und
- Informations- und Hilfsquellen zu identifizieren.

## Was ist Asterisk

Asterisk ist eine Open-Source-PBX-Software, die – einmal auf der Hardware eines PCs zusammen mit den korrekten Schnittstellen installiert – als voll funktionsfähige PBX für Privatanwender, Unternehmen, VoIP-Dienstanbieter und Telefongesellschaften genutzt werden kann. Asterisk ist sowohl eine Open-Source-Community als auch ein Projekt, das von Sangoma Technologies (welche Digium im Jahr 2018 übernommen haben) gesponsert wird. Es steht Ihnen frei, Asterisk zu nutzen und an Ihre Bedürfnisse anzupassen. Asterisk ermöglicht eine Echtzeit-Konnektivität zwischen PSTN- und VoIP-Netzwerken. Da Asterisk weit mehr als eine PBX ist, erhalten Sie nicht nur ein außergewöhnliches Upgrade für Ihre bestehende PBX, sondern können auch neue Dinge in der Telefonie umsetzen, wie zum Beispiel:

- Mitarbeiter im Homeoffice über Breitband-Internet mit einer Büro-PBX verbinden;
- Mehrere Büros an verschiedenen Standorten über ein IP-Netzwerk, ein privates Netzwerk oder sogar über das Internet selbst verbinden;
- Ihren Mitarbeitern eine Voicemail bieten, die mit dem Web und E-Mail integriert ist;
- Anwendungen wie IVRs erstellen, die Verbindungen zu Ihrem Bestellsystem oder anderen Anwendungen ermöglichen;
- Reisenden Benutzern von überall aus mit einer einfachen Breitband- oder VPN-Verbindung Zugriff auf die Firmen-PBX geben; und
- vieles mehr....

Asterisk enthält mehrere fortschrittliche Ressourcen, die zuvor nur in High-End-Systemen zu finden waren, wie zum Beispiel:

- Warteschleifenmusik für Kunden, die in Anrufwarteschlangen warten, mit Unterstützung für Medien-Streaming und MP3-Dateien;
- Anrufwarteschlangen, bei denen ein Team von Agenten Anrufe entgegennehmen und Warteschlangen überwachen kann;
- Integration mit Text-to-Speech und Spracherkennung;
- Detaillierte Aufzeichnungen, die sowohl in Textdateien als auch in SQL-Datenbanken übertragen werden; und
- PSTN-Konnektivität über sowohl digitale als auch analoge Leitungen.

## Was ist AsteriskNOW (historisch) und FreePBX

Asterisk in seiner reinsten Form, auch bekannt als „classic asterisk“ (Bezeichnung im Debian-Paket), wird eher als Entwicklungswerkzeug denn als fertiges Produkt an sich betrachtet. AsteriskNOW war eine Initiative, um Asterisk in eine Soft-Appliance zu verwandeln. Die Distribution enthielt CentOS als Betriebssystem und FreePBX als grafische Oberfläche. AsteriskNOW wurde inzwischen eingestellt.

Heute ist die standardmäßige schlüsselfertige Asterisk-Distribution **FreePBX** (gewartet von Sangoma), die Asterisk mit einer webbasierten Administrations-GUI und einem Modul-Ökosystem bündelt. FreePBX ist unter der GPL lizenziert und kann frei von www.freepbx.org heruntergeladen werden. Für kommerzielle Einsätze bietet Sangoma außerdem die **FreePBX Distro** (ein vollständiges Linux-Image) und sein kommerzielles Produkt **PBXact** an.

## Rolle von Digium™ und Sangoma

Digium, ein Unternehmen mit Sitz in Huntsville, Alabama, war seit seiner Gründung im Jahr 1999 der Schöpfer und Hauptentwickler von Asterisk. Neben der Rolle als Hauptsponsor der Asterisk-Entwicklung produzierte Digium Telefonie-Schnittstellenkarten und andere Hardware für Asterisk-PBXs und schuf kommerzielle Produkte wie Switchvox (ausgerichtet auf den KMU-Markt). Im Jahr 2018 wurde Digium von **Sangoma Technologies** übernommen, einem kanadischen Unternehmen für Unified Communications. Seit der Übernahme fördert Sangoma weiterhin die Asterisk-Entwicklung und fungiert als deren primärer Verwalter, der das Open-Source-Projekt unter www.asterisk.org pflegt.

Historisch gesehen bot Digium Asterisk unter drei Arten von Lizenzvereinbarungen an:

- General Public License (GPL) Asterisk. Dies ist die am häufigsten verwendete Version. Sie enthält alle Funktionen und kann gemäß den Bedingungen der GPL-Lizenz frei verwendet und modifiziert werden.
- Asterisk Business Edition war eine kommerzielle Version von Asterisk. Einige Unternehmen nutzten die Business Edition, weil sie die GPL-Lizenz nicht wollten oder nicht nutzen konnten – meist, weil sie ihren Quellcode nicht zusammen mit Asterisk veröffentlichen wollten. **Hinweis:** Die Asterisk Business Edition wurde eingestellt; heute wird Asterisk ausschließlich unter der GPL vertrieben.
- Asterisk OEM-Lizenzierung. Nachdem Digium den Verkauf der Asterisk Business Edition im Einzelhandel eingestellt hatte, lizenzierte es diese kommerzielle Edition weiterhin an OEM-Kunden – Gerätehersteller, die proprietäre Produkte auf Basis von Asterisk entwickeln wollten, ohne ihren eigenen Quellcode unter der GPL veröffentlichen zu müssen.

### Das Zapata-Projekt und seine Beziehung zu Asterisk

Das Zapata-Projekt wurde von Jim Dixon entwickelt, der auch für das revolutionäre Hardware-Design verantwortlich war, das mit Asterisk verwendet wurde. Die Hardware ist ebenfalls Open-Source; daher kann sie von jedem Unternehmen genutzt werden, und heute produzieren mehrere Hersteller Karten, die mit dieser Architektur kompatibel sind.

Das Zapata-Projekt brachte eine Architektur namens Zaptel hervor, die später in DAHDI (Digium/Asterisk Hardware Device Interface) umbenannt wurde. Einer der Hauptvorteile dieser Architektur ist die Fähigkeit, die PC-CPU zur Verarbeitung von Medien-Streaming, Echokompensation und Transkodierung zu nutzen. Im Gegensatz dazu verwenden die meisten bestehenden Karten digitale Signalprozessoren (DSP), um diese Aufgaben auszuführen. Die Nutzung der PC-CPU anstelle dedizierter DSPs senkt den Preis der Karte dramatisch. Somit sind diese Karten deutlich günstiger als zuvor verfügbare Schnittstellen anderer Hersteller. Andererseits benötigen diese Karten viel CPU-Leistung; ein Missbrauch der PC-CPU kann die Sprachqualität erheblich beeinträchtigen. Kürzlich hat Digium eine Koprozessorkarte auf den Markt gebracht, die DSPs zum Kodieren und Dekodieren von G.729 und G.723 verwendet, was eine bessere Skalierbarkeit für eine große Anzahl von Kanälen ermöglicht.

## Warum Asterisk?

Ich erinnere mich an meinen ersten Kontakt mit Asterisk. Normalerweise ist die erste Reaktion auf etwas Neues – besonders auf etwas, das mit dem konkurriert, was man bereits kennt – Ablehnung! Genau das passierte im Jahr 2003. Asterisk konkurrierte mit einer Lösung, die ich gerade an einen Kunden verkaufte (4 E1 VoIP Gateway), und es war zehnmal günstiger als das, was ich für die Lösung berechnete, die ich bereits kannte. Dieser unverhältnismäßige Preis veranlasste mich dazu, Asterisk zu studieren, um potenzielle Fallstricke und Nachteile zu identifizieren. Zum Beispiel fand ich heraus, dass die PC-CPU zu dieser Zeit keine 120 gleichzeitigen G.729-Verbindungen unterstützen würde; am Ende des Tages gewann ich den Auftrag mit meiner Gateway-Lösung. Diese Übung führte mich jedoch zu der Entdeckung, dass Asterisk eine Vielzahl sehr teurer Probleme für meinen Kundenstamm lösen konnte. Wir hatten Probleme mit teuren Angeboten für IVR, Unified Messaging, Anrufaufzeichnung und Dialer; bei entsprechender Dimensionierung konnten die CPU-Probleme umgangen werden. Tatsächlich wurde Asterisk in nur drei Jahren zum Flaggschiff-Produkt meines Unternehmens (ich entschied mich sogar, ein weiteres Unternehmen nur für das Asterisk-Geschäft zu eröffnen). Meiner Meinung nach ist Asterisk eine Revolution in der Telekommunikation, die für die IP-Telefonie das darstellt, was Apache für Webdienste bedeutet.

### Extreme Kostenreduzierung

Wenn man eine traditionelle PBX mit Asterisk in Bezug auf digitale Schnittstellen und Telefone vergleicht, ist Asterisk etwas günstiger als diese PBXs. Asterisk zahlt sich jedoch erst richtig aus, wenn man fortschrittliche Funktionen wie Voicemail, ACD, IVR und CTI hinzufügt. Mit diesen fortschrittlichen Funktionen wird Asterisk deutlich günstiger als traditionelle PBXs. Tatsächlich ist der Vergleich von Asterisk-PBXs mit analogen Low-End-PBXs unfair, da Asterisk so viele Funktionen bietet, die in analogen Low-End-Systemen nicht verfügbar sind.

### Kontrolle und Unabhängigkeit des Telefonsystems

Einer der am häufigsten genannten Vorteile von Asterisk durch Kunden ist die Unabhängigkeit, die es bietet. Einige der heutigen Hersteller geben dem Kunden nicht einmal das Systempasswort oder die Konfigurationsdokumentation. Mit dem „Do-it-yourself“-Ansatz von Asterisk erreicht der Benutzer völlige Freiheit; als Bonus hat der Benutzer Zugriff auf eine Standardschnittstelle.

### Einfache und schnelle Entwicklungsumgebung

Asterisk kann unter Verwendung von Skriptsprachen wie PHP und Perl mit AMI- und AGI-Schnittstellen erweitert werden. Asterisk ist Open-Source, und sein Quellcode kann vom Benutzer modifiziert werden. Der Quellcode ist größtenteils in der Programmiersprache ANSI C geschrieben.

### Funktionsreich

Asterisk verfügt über mehrere Funktionen, die in traditionellen PBXs entweder nicht vorhanden oder optional sind (z. B. Voicemail, CTI, ACD, IVR, integrierte Warteschleifenmusik und Aufzeichnung). Die Kosten für diese Funktionen übersteigen bei einigen Plattformen den Preis der Plattform selbst.

### Dynamischer Inhalt am Telefon

Asterisk wird unter Verwendung der Sprache C und anderer Sprachen programmiert, die in der heutigen Entwicklungsumgebung üblich sind. Die Möglichkeit, dynamische Inhalte bereitzustellen, ist praktisch unbegrenzt.

### Flexibler und leistungsstarker Dialplan

Ein weiterer Durchbruch von Asterisk ist sein leistungsstarker Dialplan. In traditionellen PBXs sind selbst einfache Funktionen wie Least Cost Routing (LCR) entweder nicht machbar oder optional. Mit Asterisk ist die Wahl der besten Route einfach und sauber.

### Open-Source auf Linux-Basis

Eines der größten Merkmale von Asterisk ist seine Community. Es stehen zahlreiche Ressourcen zur Verfügung, darunter die offizielle Asterisk-Dokumentation (docs.asterisk.org), das von der Community gepflegte VoIP-Info-Wiki (www.voip-info.org <http://www.voip-info.org>), E-Mail-Verteilerlisten und Foren. Da Asterisk zunehmend übernommen wird, werden Fehler schnell gefunden und behoben. Mit einer großen Benutzerbasis und einem aktiven Entwicklungsteam gehört Asterisk zu den am weitesten getesteten PBX-Plattformen der Welt, was dazu beiträgt, die Codebasis stabil und ausgereift zu halten.

### Einschränkungen der Asterisk-Architektur

Einige Einschränkungen bei Asterisk ergeben sich aus der Verwendung des Zapata-Telefondesigns. Bei diesem Design nutzt Asterisk die PC-CPU zur Verarbeitung von Sprachkanälen anstelle von dedizierten digitalen Signalprozessoren (DSPs), die auf anderen Plattformen üblich sind. Obwohl dies eine enorme Kostenreduzierung bei der Hardwareschnittstelle ermöglicht, wird das System von der PC-CPU abhängig. Meine Empfehlung ist, Asterisk auf einer dedizierten Maschine zu betreiben und bei der Hardware-Dimensionierung konservativ zu sein. Sie können Asterisk auch in einem separaten VLAN verwenden, um übermäßige Broadcasts zu vermeiden, die die CPU belasten (Broadcast-Stürme durch Schleifen oder Viren). Einige neuere Schnittstellenkarten verschiedener Anbieter enthalten mittlerweile DSPs zur Verarbeitung von Echokompensation, Codecs und anderen Funktionen, was Asterisk noch besser machen wird.

## Haupteinwände gegen Asterisk PBX

Es ist üblich, Einwände gegen die Einführung von Asterisk zu hören, auf die wir hier eingehen werden.

### Der Marktanteil von Asterisk ist zu klein

Der Marktanteil wird normalerweise an der Anzahl der verkauften PBXs gemessen. Diese Statistiken werden im Allgemeinen von den größten Distributoren bezogen. Asterisk ist freie Software, die heruntergeladen und bereitgestellt werden kann, ohne dass ein Verkauf registriert wird, daher wird sie in diesen Zahlen systematisch unterschätzt. Dennoch betreibt Asterisk eine sehr große installierte Basis weltweit – von Office-PBXs auf einem einzelnen Server bis hin zu großen Carrier- und Contact-Center-Bereitstellungen – und bleibt die dominierende Engine hinter dem Open-Source-PBX-Ökosystem (einschließlich schlüsselfertiger Distributionen wie FreePBX).

### Wenn es kostenlos ist, wie überlebt der Hersteller?

Tatsächlich gibt es keinen Open-Source-Softwarehersteller im traditionellen Sinne. Digium entwickelte Asterisk seit 1999 und finanzierte sich durch den Verkauf von Telefonie-Schnittstellenkarten, kommerziellen PBX-Produkten wie Switchvox und zugehöriger Software. Im Jahr 2018 erwarb Sangoma Technologies Digium. Sangoma finanziert weiterhin die Asterisk-Entwicklung und generiert Einnahmen durch kommerzielle Produkte (kommerzielle FreePBX-Module, PBXact, Switchvox), Hardwareverkäufe und professionelle Dienstleistungen.

### Es ist schwer, technischen Support zu finden!

Sangoma bietet kommerziellen technischen Support für Asterisk über sein Partner-Ökosystem und direkt über seine Produktangebote an. Ein globales Netzwerk zertifizierter Fachleute bietet First-Level-Support und professionelle Dienstleistungen. Community-Support bleibt über die Asterisk-Foren und Mailinglisten unter www.asterisk.org aktiv.

### Unterstützt Asterisk mehr als 200 Nebenstellen?

Ja, absolut. Ein einzelner, gut dimensionierter Asterisk-Server kann eine große Anzahl von Nebenstellen verarbeiten, und Asterisk skaliert weiter, indem Benutzer über mehrere Server mit Lastausgleich und Failover verteilt werden, was große standortübergreifende Bereitstellungen ermöglicht.

### Nur „Geeks“ können Asterisk installieren

Mit FreePBX (erhältlich als eigenständige Distro von Sangoma) sind selbst Fachleute mit begrenzten Linux-Kenntnissen in der Lage, eine PBX mittlerer Komplexität zu installieren und zu konfigurieren. Mit Hilfe einer GUI ist es möglich, eine komplette PBX in nur wenigen Stunden zu konfigurieren.

### Was passiert, wenn der Server ausfällt?

Einer der Hauptvorteile von Asterisk ist seine Fähigkeit, in fehlertoleranten Systemen zu laufen. Es ist relativ einfach und kostengünstig, zwei Server parallel laufen zu lassen. Ich fordere Sie heraus, dies mit einer herkömmlichen PBX zu versuchen!

### Unser Unternehmen verwendet keine Open-Source-Software

Ihr Unternehmen verwendet wahrscheinlich Open-Source-Software, ohne es überhaupt zu merken. Mehrere Appliances nutzen Linux als Betriebssystem. Darüber hinaus sind kommerzieller Support und verwaltete Bereitstellungen von Sangoma und seinem zertifizierten Partnernetzwerk verfügbar.

### Die Nutzung der PC-CPU zur Verarbeitung von Signalisierung und Medien wird nicht empfohlen

Asterisk nutzt die CPU des Servers zur Verarbeitung von Signalisierung und Medien für Sprachkanäle, anstatt dedizierte DSPs zu haben. Obwohl dies eine Kostenreduzierung um das bis zu Fünffache ermöglicht, macht es das System von der Leistung der Haupt-CPU abhängig. Bei korrekter Dimensionierung ist Asterisk in der Lage, große Volumina zu verarbeiten. Wenn Sie die Haupt-CPU dennoch von diesen Aufgaben entlasten möchten, können Sie auch Hardware-Echokompensation und sogar Transcoder-Karten verwenden, wie die Sangoma (ehemals Digium) TC400B auf DSP-Basis.

## Asterisk-Architektur

Dieser Abschnitt erklärt, wie die Architektur von Asterisk funktioniert. Die Abbildung unten zeigt die grundlegende Asterisk-Architektur. Als Nächstes erklären wir architekturbezogene Konzepte, einschließlich Kanälen, Codecs und Anwendungen.

![Die Asterisk-Architektur](../images/01-introduction-fig01.png)

### Kanäle

Ein Kanal ist das Äquivalent einer Telefonleitung, jedoch in einem digitalen Format. Er besteht normalerweise aus einem analogen oder digitalen (TDM) Signalisierungssystem oder einer Kombination aus Codec und Signalisierungsprotokoll (z. B. SIP-GSM, IAX-uLaw). Anfangs waren alle Telefonieverbindungen analog und anfällig für Echo und Rauschen. Später wurden die meisten Systeme auf digitale Systeme umgestellt, wobei der analoge Ton in den meisten Fällen mittels Pulscodemodulation (PCM) in ein digitales Format umgewandelt wurde. Dieses Format ermöglicht die Sprachübertragung mit 64 Kilobit/Sekunde ohne Kompression.

Kanäle zur Anbindung an das öffentliche Telefonnetz (PSTN):

- `chan_dahdi`: analoge (FXO/FXS) und digitale (E1/T1/PRI) TDM-Karten von Sangoma (ehemals Digium), Xorcom und anderen. Separat gegen DAHDI gebaut – siehe das Kapitel *Legacy-Kanäle*.

Kanäle zur Anbindung an Voice over IP:

- `chan_pjsip`: SIP – der primäre und einzige SIP-Kanaltreiber in Asterisk 22 LTS. Wählzeichenfolge: `PJSIP/endpoint_name`. (**Hinweis:** der alte `chan_sip` wurde in Asterisk 21 entfernt und existiert in Asterisk 22 nicht mehr. Siehe *Aufbau Ihrer ersten PBX mit PJSIP* für die Konfiguration.)
- `chan_iax2`: das IAX2-Protokoll – wird in Asterisk 22 noch mitgeliefert, ist aber veraltet; SIP/PJSIP wird für neue Bereitstellungen bevorzugt. Wählzeichenfolge: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM-Telefone. Immer noch verfügbar (erweiterter Support), aber selten verwendet.

Die älteren VoIP-Kanäle sind nicht mehr Teil eines Standard-Asterisk-22-Builds: `chan_h323` (H.323) überlebt nur als Community-Add-on `ooh323`, und `chan_mgcp` (MGCP) sowie `chan_skinny` (Cisco SCCP) wurden als veraltet markiert und aus dem modernen Kanal-Set entfernt. Wenn Sie mit diesen Protokollen zusammenarbeiten müssen, ist ein Gateway vor Asterisk der übliche Ansatz.

Sonstige Kanäle:

- **Local**: ein Pseudo-Kanal (im Kern eingebaut), der in einen anderen Kontext zurück in den Dialplan schleift – nützlich für rekursives Routing und um einen Anruf an mehrere Ziele zu verteilen. Wählzeichenfolge: `Local/extension@context`.

### Codec und Codec-Übersetzung

Wir versuchen normalerweise, so viele Sprachverbindungen wie möglich in einem Datennetzwerk unterzubringen. Codecs ermöglichen neue Funktionen in der digitalen Sprache, einschließlich Kompression, was eines der wichtigsten Merkmale ist, da es Kompressionsraten von mehr als 8 zu 1 ermöglicht. Viele Codecs definieren auch Funktionen wie Spracherkennung (Stilleunterdrückung), Paketverlustverschleierung und Komfortrauschen-Erzeugung, obwohl Asterisk selbst kein Komfortrauschen erzeugt oder eine Stilleunterdrückung durchführt. Mehrere Codecs sind für Asterisk verfügbar und können transparent von einem in einen anderen übersetzt werden. Intern verwendet Asterisk slinear als Stream-Format, wenn es von einem Codec in einen anderen konvertieren muss. Einige Codecs in Asterisk werden nur im Pass-Through-Modus unterstützt; diese Codecs können nicht übersetzt werden. Um zu überprüfen, welche Codecs auf Ihrem System installiert sind, können Sie den Konsolenbefehl verwenden:

```
CLI>core show translation
```

Die folgenden Codecs werden unterstützt:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europa) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Nur Pass-Through-Modus
- G.726 - (16/24/32/40kbps)
- G.729 - Binäres Codec-Modul, vertrieben von Sangoma; der Download ist kostenlos, aber die rechtmäßige Nutzung erfordert den Erwerb einer Lizenz pro Kanal (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protokolle

Das Senden von Daten von einem Telefon zum anderen sollte einfach sein, vorausgesetzt, die Daten finden ihren Weg zum anderen Telefon von selbst. Leider passiert das nicht so, und ein Signalisierungsprotokoll ist notwendig, um Verbindungen zwischen Telefonen herzustellen, Endgeräte zu entdecken und Telefoniesignalisierung zu implementieren. SIP ist das dominierende Signalisierungsprotokoll in modernen Bereitstellungen und der einzige SIP-Kanal, der in Asterisk 22 LTS verfügbar ist (via chan_pjsip). IAX2 ist weiterhin verfügbar, gilt aber als veraltet. Asterisk unterstützt die folgenden Protokolle.

- SIP — via `chan_pjsip`
- IAX2 — veraltet, wird in Asterisk 22 noch mitgeliefert
- UNISTIM — Nortel/Avaya-Telefone (erweiterter Support)
- H.323, MGCP und SCCP (Cisco Skinny) — veraltete Protokolle, nicht mehr in einem Standard-Asterisk-22-Build (H.323 nur via Community-Add-on `ooh323`)

### Anwendungen

Um Anrufe von einem Telefon zum anderen zu überbrücken, wird die Anwendung dial() verwendet. Die meisten Asterisk-Funktionen (z. B. Voicemail und Konferenzen) sind als Anwendungen implementiert. Sie können die verfügbaren Asterisk-Anwendungen mit dem Konsolenbefehl core show applications sehen.

```
CLI>core show applications
```

Sie können Anwendungen aus Asterisk-Add-ons, Drittanbietern oder sogar solchen, die Sie selbst entwickeln, hinzufügen.

## Überblick über ein Asterisk-System

Asterisk ist eine Open-Source-PBX, die wie eine Hybrid-PBX agiert und Technologien wie TDM und IP-Telefonie integriert. Asterisk ist bereit, Funktionen wie interaktive Sprachdialogsysteme (IVR) und automatische Anrufverteilung (ACD) zu implementieren; darüber hinaus ist es, wie bereits erwähnt, offen für die Entwicklung neuer Anwendungen. Diese Abbildung zeigt, wie Asterisk eine Verbindung zum PSTN und bestehenden PBXs über analoge und digitale Schnittstellen herstellt sowie analoge und IP-Telefone unterstützt. Es kann als Soft-Switch, Media-Gateway, Voicemail- und Audiokonferenzsystem fungieren und verfügt zudem über eine integrierte Warteschleifenmusik.

![Überblick über ein Asterisk-System](../images/01-introduction-fig02.png)

## Vergleich der alten und der neuen Welt

Im alten Soft-Switch-Modell wurden alle Komponenten separat verkauft, was bedeutete, dass Sie jede Komponente einzeln erwerben und dann in die PBX- oder Soft-Switch-Umgebung integrieren mussten. Die Kosten und Risiken waren hoch und die meisten Geräte proprietär.

![Die alte Welt: Komponenten separat gekauft und integriert](../images/01-introduction-fig03.png)

### Telefonie mit Asterisk

Alle Funktionen sind in der Asterisk-Plattform in derselben oder in verschiedenen Boxen je nach Dimensionierung integriert und alle sind unter der GPL lizenziert. Manchmal ist es einfacher, Asterisk zu installieren, als einige der gängigen IP-PBXs zu lizenzieren.

![Telefonie mit Asterisk: die Funktionen sind integriert](../images/01-introduction-fig04.png)

## Aufbau eines Testsystems

Bei der Implementierung einer Asterisk-Lösung ist unser erster Schritt im Allgemeinen der Aufbau einer Testmaschine. Die einfachste Testmaschine ist die 1x1 PBX, die mindestens ein Telefon und eine Leitung umfasst. Es gibt verschiedene Möglichkeiten, dies zu tun.

![Ein einfaches Asterisk-Testsystem](../images/01-introduction-fig05.png)

### Ein FXO, ein FXS

Der erste und einfachste Weg, eine Testmaschine zu bauen, ist der Kauf einer Karte mit einer FXO- und einer FXS-Schnittstelle. Verbinden Sie den FXO-Port mit einer bestehenden Leitung und verbinden Sie ein FXS mit einem analogen Telefon. Somit haben Sie eine 1x1 PBX.

### VoIP-Dienstanbieter: ATA

Dies ist die VoIP-Option. In diesem Fall würden Sie sich bei einem Sprachdienstanbieter anmelden, um die SIP-Trunks zu erhalten, und müssten einen analogen SIP-Telefonieadapter kaufen. Sie werden wahrscheinlich weniger als hundert Dollar ausgeben, wenn Sie den PC bereits haben.

### Günstige FXO-Karte oder ATA

Ich habe mit einer günstigen FXO-Karte begonnen. Einige günstige V.90-Faxmodems funktionieren mit Asterisk als FXO-Karte. Einige der ersten Digium-Karten wurden unter Verwendung dieser Karten erstellt (z. B. X100P und X101P), bei denen es sich um alte Modems auf Basis von Motorola- und Intel-Chipsätzen handelt (Motorola 68202-51, Intel 537PU, Intel 537PG und Intel Ambient MD3200 sind bekannt dafür, zu funktionieren). Diese Modems sind oft mit neuen Motherboards inkompatibel. Kürzlich begannen einige Hersteller, diese Karten als X100P-Klone zu verkaufen. Einige der Inkompatibilitäten können mit einem Patch gelöst werden, weitere Informationen finden Sie unter:

- http://www.voip.school/mediawiki/index.php/Asterisk_patch_for_the_X100P_card

## Asterisk-Szenarien

Asterisk kann in verschiedenen Szenarien eingesetzt werden. Wir werden einige davon auflisten und die Vorteile sowie mögliche Einschränkungen der jeweiligen Szenarien erläutern.

### IP PBX

Das häufigste Szenario ist die Installation einer neuen oder der Ersatz einer bestehenden PBX. Wenn Sie Asterisk mit einigen anderen Alternativen vergleichen, werden Sie feststellen, dass es günstiger und funktionsreicher ist als die meisten derzeit auf dem Markt erhältlichen PBXs. Mehrere Unternehmen ändern ihre Spezifikationen jetzt auf Asterisk anstelle anderer Marken-PBXs.

![Asterisk als IP PBX](../images/01-introduction-fig06.png)

### IP-Fähigkeit für Legacy-PBXs

Das folgende Bild veranschaulicht eines der am häufigsten verwendeten Setups. Große Unternehmen wollen im Allgemeinen kein nennenswertes Risiko eingehen, wenn sie in neue Technologien investieren, und gleichzeitig ihre Investitionen in Legacy-Geräte bewahren. Die IP-Fähigkeit für eine Legacy-PBX kann sehr teuer sein; daher kann der Anschluss einer Asterisk-PBX über T1/E1-Leitungen eine gute Alternative für kostenbewusste Kunden sein. Ein weiterer Vorteil ist die Möglichkeit, eine Verbindung zu einem VoIP-Dienstanbieter mit besseren Telefonietarifen herzustellen.

![IP-Fähigkeit für eine Legacy-PBX](../images/01-introduction-fig07.png)

### Toll Bypass

Eine sehr nützliche Anwendung für VoIP ist die Verbindung von Zweigstellen über das Internet oder ein WAN. Die Nutzung einer bestehenden Datenverbindung ermöglicht es Ihnen, Gebühren für Telekommunikationsverbindungen zwischen Hauptsitz und Zweigstellen zu umgehen.

![Toll Bypass zwischen Büros über ein WAN](../images/01-introduction-fig08.png)

### Anwendungsserver (IVR, Konferenz, Voicemail)

Asterisk kann als Anwendungsserver für die bestehende PBX verwendet oder direkt an das PSTN angeschlossen werden. Asterisk bietet Dienste wie Voicemail, Faxempfang, Anrufaufzeichnung, IVR mit Datenbankanbindung und einen Audiokonferenzserver. Wenn Sie Voicemail und Fax in einen bestehenden E-Mail-Server integrieren, erhalten Sie ein Unified-Messaging-System, was normalerweise eine teure Lösung ist. Die Verwendung von Asterisk als Anwendungsserver bietet eine extreme Kostenreduzierung im Vergleich zu anderen Lösungen.

![Asterisk als Anwendungsserver](../images/01-introduction-fig09.png)

### Media Gateway

Die meisten Voice-over-IP-Dienstanbieter verwenden einen SIP-Proxy, um die gesamte Registrierung, Lokalisierung und Authentifizierung von SIP-Benutzern zu hosten. Sie müssen Anrufe immer noch direkt an das PSTN senden oder sie über eine SIP- oder H.323-Voice-over-IP-Verbindung über einen Wholesale-Anbieter für Anrufbeendigung routen. Asterisk kann als Back-to-Back User Agent (B2BUA) oder Media-Gateway fungieren und sehr teure Soft-Switches oder Media-Gateways ersetzen. Vergleichen Sie den Preis eines Vier-E1/T1-Gateways der führenden Markthersteller mit Asterisk. Die Asterisk-Lösung kann um ein Vielfaches günstiger sein als andere Lösungen und ist in der Lage, Signalisierungsprotokolle (H.323, SIP, IAX…) und Codecs (G.711, G.729…) zu übersetzen.

![Asterisk als Media Gateway](../images/01-introduction-fig10.png)

### Contact-Center-Plattform

Ein Contact-Center ist eine sehr komplexe Lösung, die mehrere Technologien kombiniert, wie automatische Anrufverteilung (ACD), interaktive Sprachdialogsysteme (IVR) und Anrufüberwachung. Grundsätzlich gibt es drei Arten von Contact-Centern: Inbound, Outbound und Blended. Inbound-Contact-Center sind sehr anspruchsvoll und erfordern normalerweise ACD, IVR, CTI, Aufzeichnung, Überwachung und Berichte. Asterisk verfügt über eine integrierte ACD, um die Anrufe in die Warteschlange zu stellen. IVR kann unter Verwendung der Asterisk Gateway Interface (AGI) oder interner Mechanismen wie der Anwendung background() durchgeführt werden. Computer-Telefonie-Integration (CTI) wird unter Verwendung der Asterisk Manager Interface (AMI) erreicht; Aufzeichnung und Berichterstattung sind in Asterisk integriert. Für ein Outbound-Contact-Center ist ein prädiktiver oder Power-Dialer eine der Hauptkomponenten. Obwohl mehrere Dialer für das Open-Source-Asterisk verfügbar sind, ist es nicht schwer, bei Bedarf einen eigenen für die Plattform zu bauen. Ein Blended-Contact-Center ermöglicht den gleichzeitigen Inbound- und Outbound-Betrieb und spart Geld durch eine bessere Auslastung der Zeit der Agenten. Es ist möglich, Asterisk und seinen ACD-Mechanismus zu verwenden, um eine Blended-Lösung zu implementieren.

![Eine Asterisk-Contact-Center-Plattform](../images/01-introduction-fig11.png)

## Informationen und Hilfe finden

Dieser Abschnitt bietet einige der wichtigsten Informationsquellen zu Asterisk.

- Offizielle Asterisk-Website: <https://www.asterisk.org> Hier finden Sie Informationen zu:
- Dokumentation & Wiki -> <https://docs.asterisk.org>
- Community-Forum -> <https://community.asterisk.org>
- Fehlerverfolgung -> <https://github.com/asterisk/asterisk/issues>
- Wiki (veraltet, weitgehend durch docs.asterisk.org ersetzt) -> <https://wiki.asterisk.org>

### Community-Forum

Das Asterisk-Community-Forum hat die alten Mailinglisten weitgehend ersetzt und ist der Ort, um Fragen zu stellen. Versuchen Sie, so viele Informationen wie möglich zu sammeln, bevor Sie posten. Niemand wird Ihnen helfen, wenn Sie Ihre Hausaufgaben nicht gemacht haben – versuchen Sie mindestens einmal, das Problem selbst zu lösen.

- <https://community.asterisk.org>

## Zusammenfassung

Asterisk ist eine unter der GPL lizenzierte Software, die es einem gewöhnlichen PC ermöglicht, als leistungsstarke IP-PBX-Plattform zu fungieren. Mark Spencer von Digium schuf Asterisk in den späten 1990er Jahren, und Digium finanzierte sich durch den Verkauf von Asterisk-bezogener Hardware und kommerziellen Produkten. Digium wurde 2018 von Sangoma Technologies übernommen; Sangoma fördert nun die Asterisk-Entwicklung. Das Hardware-Schnittstellendesign stammte aus dem Zapata-Projekt, das von Jim Dixon entwickelt wurde und aus dem DAHDI hervorging.

Die Asterisk-Architektur hat die folgenden Hauptkomponenten:

- KANÄLE: Analog, digital oder Voice-over-IP. In Asterisk 22 LTS wird SIP ausschließlich über chan_pjsip abgewickelt.
- PROTOKOLLE: Kommunikationsprotokolle, die für die Signalisierung der Anrufe verantwortlich sind, einschließlich SIP (via PJSIP), H323, MGCP und IAX2.
- CODECS: Übersetzen digitale Formate der Sprache und ermöglichen Kompression und Paketverlustverschleierung. Beachten Sie, dass Asterisk selbst keine Stilleunterdrückung (Spracherkennung) oder Komfortrauschen-Erzeugung durchführt; wenn Endpunkte VAD verwenden, sollte das Komfortrauschen auf der Client-Seite deaktiviert werden.
- ANWENDUNGEN: Verantwortlich für die Funktionalität der Asterisk-PBX. Konferenz, Voicemail und Fax sind Beispiele für Asterisk-Anwendungen.

Asterisk kann in verschiedenen Szenarien eingesetzt werden, von einer kleinen IP-PBX bis hin zu einem anspruchsvollen Contact-Center. Hilfe finden Sie einfach unter www.asterisk.org und docs.asterisk.org.

## Quiz

1. Welches Unternehmen hat Digium im Jahr 2018 übernommen und fungiert nun als primärer Verwalter des Asterisk-Open-Source-Projekts?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. Welcher Kanaltreiber bietet in Asterisk 22 LTS SIP-Konnektivität?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Wahr oder Falsch: Der Kanaltreiber `chan_sip` wurde in Asterisk 21 entfernt und ist in einem Standard-Asterisk-22-Build nicht vorhanden.

4. Welche der folgenden Kanäle/Protokolle sind **nicht mehr** Teil eines Standard-Asterisk-22-Builds? (Wählen Sie alle zutreffenden aus.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, überlebt nur als Community-Add-on `ooh323`)

5. Die Hardware-Architektur des Zapata-Projekts, ursprünglich Zaptel genannt, wurde später umbenannt in ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Wenn Asterisk Audio von einem Codec in einen anderen konvertieren muss, über welches interne Stream-Format übersetzt es?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Wie ist laut Kapitel die Lizenzsituation des von Sangoma vertriebenen G.729-Codec-Moduls?
   - A. Es ist GPL und für jede Nutzung völlig kostenlos.
   - B. Der Download ist kostenlos, aber die rechtmäßige Nutzung erfordert den Erwerb einer Lizenz pro Kanal.
   - C. Es kann ohne den Kauf der Asterisk Business Edition überhaupt nicht bezogen werden.
   - D. Es funktioniert nur im Pass-Through-Modus und kann nicht installiert werden.

8. Welche Asterisk-Anwendung wird verwendet, um einen Anruf von einem Telefon zum anderen zu überbrücken?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Was ist der `Local` Kanal in Asterisk?
   - A. Eine Hardware-FXS-Schnittstelle für analoge Telefone.
   - B. Ein SIP-Trunk zu einem lokalen Dienstanbieter.
   - C. Ein Pseudo-Kanal, der einen Anruf in einen anderen Kontext zurück in den Dialplan schleift.
   - D. Ein Codec, der für On-Net-Anrufe verwendet wird.

10. In welchem Einsatzszenario agiert Asterisk als Back-to-Back User Agent (B2BUA), der zwischen Signalisierungsprotokollen und Codecs übersetzt, um teure Soft-Switches zu ersetzen?
    - A. IP-Fähigkeit für eine Legacy-PBX
    - B. Toll Bypass
    - C. Media Gateway
    - D. Contact-Center-Plattform

**Antworten:** 1 — B · 2 — C · 3 — Wahr · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
