```{=latex}
\frontmatter
```

## Copyright {.unnumbered}

*Asterisk Guide* — Zweite Ausgabe (Asterisk 22 LTS)

Copyright © 2006–2026 Flavio E. Gonçalves. Alle Rechte vorbehalten.

Kein Teil dieses Buches darf ohne die vorherige schriftliche Zustimmung des Autors in irgendeiner Form oder mit irgendwelchen Mitteln reproduziert, in einem Datenabrufsystem gespeichert oder übertragen werden, mit Ausnahme kurzer Auszüge für veröffentlichte Rezensionen.

**Ausgabe:** Zweite Ausgabe.
**ISBN:** *wird noch zugewiesen.*

> **[author TODO]** Weisen Sie eine neue ISBN für die 2. Ausgabe zu (verwenden Sie nicht die 9781796396973 der 1. Ausgabe) und legen Sie das Veröffentlichungsdatum vor dem Druck fest.

Viele der von Herstellern und Verkäufern verwendeten Bezeichnungen zur Unterscheidung ihrer Produkte werden als Marken beansprucht. Wo diese Bezeichnungen in diesem Buch erscheinen und der Autor Kenntnis von einem Markenanspruch hatte, wurden sie in Großbuchstaben oder mit Anfangsbuchstaben in Großschreibung gedruckt. Asterisk, Digium, IAX und DUNDi sind Marken von Sangoma Technologies (Digium wurde 2018 von Sangoma übernommen; Asterisk wird heute von Sangoma gesponsert).

Obwohl bei der Erstellung dieses Buches mit größter Sorgfalt vorgegangen wurde, übernimmt der Autor keine Verantwortung für Fehler oder Auslassungen oder für Schäden, die aus der Verwendung der hierin enthaltenen Informationen resultieren.

## Vorwort {.unnumbered}

Dieses Buch richtet sich an alle, die lernen möchten, wie man eine PBX (Private Branch Exchange) auf Basis von Asterisk 22 LTS installiert und konfiguriert. Asterisk ist eine Open-Source-Telefonieplattform, die VoIP und traditionelle TDM-Kanäle miteinander verbindet.

Dies ist die fünfte Generation eines Buches, das ursprünglich als *Asterisk Configuration Guide* begann. Das Material entstand aus der Arbeit, die ich zur Vorbereitung auf die Digium dCAP-Zertifizierung im Jahr 2006 geleistet habe – die ich im ersten Anlauf bestanden habe – und wurde seitdem an mehr als tausend Studenten vermittelt.

Das Konzept der Open-Source-PBX ist revolutionär. Über Jahrzehnte wurde die Telefonie von einer Handvoll Unternehmen dominiert, die teure proprietäre Systeme verkauften. Asterisk gab diese Macht zurück in die Hände der Anwender: Funktionen, die einst wirtschaftlich unerreichbar waren – CTI (Computer-Telephony Integration), IVR (Interactive Voice Response), ACD (Automatic Call Distribution), Voicemail und vieles mehr – sind heute für jeden mit einem Linux-Rechner und der Bereitschaft zu lernen verfügbar.

Dieses Buch wird Sie nicht von alleine zu einem Guru machen – das kann kein Buch – aber am Ende werden Sie in der Lage sein, eine echte PBX mit erweiterten Funktionen aufzubauen und zu betreiben. Das Buch hat eine Ergänzung – praktische Übungen und einen Online-Kurs – bei **VoIP School Blackbelt** (<https://voip.school>).

## Zielgruppe {.unnumbered}

Dieses Buch ist für Leser gedacht, die neu bei Asterisk sind. Ich setze voraus, dass Sie mit Linux vertraut sind – der Shell, einem Texteditor und der grundlegenden Systemadministration. Sie können die Beispiele auf einem Linux-Desktop nachvollziehen, falls dies beim Lernen einfacher ist, und eine virtuelle Maschine ist für die Übungen in Ordnung (erwarten Sie eine etwas schlechtere Sprachqualität). Für Produktionssysteme empfehle ich nicht, Asterisk in einer Desktop-Umgebung oder innerhalb einer schwach ausgestatteten VM zu betreiben. Etwas Vertrautheit mit IP-Netzwerken, Voice over IP (VoIP) und grundlegenden Telefoniekonzepten ist hilfreich.

## Was ist neu in der zweiten Ausgabe {.unnumbered}

Die zweite Ausgabe ist eine gründliche Modernisierung für **Asterisk 22 LTS** (veröffentlicht 2024, unterstützt bis Oktober 2028). Die wichtigsten Änderungen:

- **PJSIP ist der einzige SIP-Kanal.** `chan_sip` wurde in Asterisk 21 entfernt und existiert in 22 nicht mehr. Jedes SIP-Beispiel verwendet jetzt PJSIP (`pjsip.conf`); das alte Material zu `sip.conf` wird nur noch als Migrationsreferenz beibehalten.
- **Sangoma-Verwaltung.** Digium wurde 2018 von Sangoma übernommen; das Projekt wird nun von Sangoma entwickelt und gesponsert, was sich durchgehend im Text widerspiegelt.
- **Drei neue Kapitel.** *WebRTC with Asterisk* (Browser-Telefone über WSS/DTLS-SRTP), *SIP trunking, DID & the PSTN* und *Deployment, monitoring & scaling*.
- **Ein reproduzierbares Labor.** Jede Konfiguration und jeder Befehl im Buch wurde anhand eines Asterisk 22 Docker-Labors verifiziert, das Sie selbst ausführen können.
- **Modernisierte Funktionen.** ConfBridge ersetzt die alte MeetMe-Konferenzschaltung, ARI wird neben AMI/AGI eingeführt, PJSIP Realtime (Sorcery) wird behandelt, und die Kapitel zu Installation, Sicherheit und CDR wurden auf den neuesten Stand gebracht.
- **Eine neue Struktur.** Das Buch ist nun in vier Teile gegliedert – Grundlagen, Kanäle & Konnektivität, Dialplan & Anruffunktionen sowie Integration & Betrieb.

## Über den Autor {.unnumbered}

Flavio E. Gonçalves wurde 1966 in Brasilien geboren. Er hegt ein starkes Interesse an Computern, seit er 1983 seinen ersten PC bekam, und erwarb 1989 einen Ingenieursabschluss mit Schwerpunkt auf computergestütztem Design und Fertigung. Er ist CEO von SipPulse in Brasilien, einem Unternehmen, das sich auf Softswitches, Session Border Controller und mandantenfähige PBXs spezialisiert hat.

Im Laufe seiner Karriere hat er eine lange Liste von Zertifizierungen erworben – darunter Novell MCNE/MCNI, Microsoft MCSE/MCT, Cisco CCSP/CCNP/CCDP und Asterisk dCAP. Er begann über Open-Source-Software zu schreiben, weil er glaubt, dass die strukturierte Art und Weise, wie Zertifizierungen ihr Material einst vermittelten, ein großartiger Weg zum Lernen ist. Er hat auf mehr als 25 Jahre Unterrichtserfahrung zurückgegriffen, um so zu schreiben, wie Menschen tatsächlich lernen, anstatt dies rein aus technischer Sicht zu tun.

Flavio ist Vater von zwei Kindern und lebt in Florianópolis, Brasilien – einem der schönsten Orte der Welt –, wo er seine Freizeit mit Surfen und Segeln verbringt.

## Feedback, Credits & Training {.unnumbered}

Ich bemühe mich sehr, Fehler zu finden und zu beseitigen, aber einige schlüpfen immer durch. Wenn Sie etwas Falsches finden, lassen Sie es mich bitte wissen, und ich werde darauf reagieren.

Dieses Buch wird auch als Schulungsmaterial verwendet. Wenn Sie es in Ihrem eigenen Schulungszentrum verwenden oder am begleitenden Online-Kurs und den Übungen teilnehmen möchten, besuchen Sie **VoIP School Blackbelt** unter <https://voip.school> oder senden Sie eine E-Mail an <flavio@voip.school>.

**Credits.** Cover-Arbeit: Karla Braga. Korrektoren: Luis F. Gonçalves, Guilherme Goes (dCAP) und professionelle Lektoren. Mein Dank gilt auch den vielen Studenten, deren Feedback über die Jahre dieses Material geformt hat, sowie meiner Familie für ihre Unterstützung.

```{=latex}
\cleardoublepage
```
