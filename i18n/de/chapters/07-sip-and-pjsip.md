# SIP & PJSIP im Detail

SIP ist das Protokoll; PJSIP ist die Art und Weise, wie Asterisk 22 es verwendet. **PJSIP** (`chan_pjsip`, konfiguriert über `pjsip.conf`) ist der einzige SIP‑Kanaltreiber in Asterisk 22 LTS. Dieses Kapitel behandelt die Grundlagen des SIP‑Protokolls (die auf Protokollebene liegen und zu 100 % gültig bleiben) sowie das PJSIP‑Objektmodell und die Konfiguration, die Sie täglich nutzen. Der veraltete Legacy‑Treiber und ein Migrationshandbuch werden im Kapitel *Legacy channels* behandelt.

## Objectives

By the end of this chapter, you should be able to:

- Explain the role of the SIP user agents, proxies, registrar, and gateways;
- Follow a basic SIP call flow (REGISTER, INVITE, provisional and final responses, ACK, BYE) and read a SIP message;
- Describe how SDP negotiates the media session and how NAT affects SIP signaling and RTP;
- Map the PJSIP object model — `endpoint`, `auth`, `aor`, `transport`, `identify`, and `registration` — and how the objects reference one another;
- Configure SIP phones and trunks in `pjsip.conf`, including the NAT-traversal options; and
- Verify and troubleshoot endpoints with the `pjsip show …` CLI commands.

## Grundlagen des SIP-Protokolls

Session Initiation Protocol (SIP) ist ein textbasiertes Protokoll, das HTTP und SMTP ähnelt und dazu entwickelt wurde, interaktive Kommunikationssitzungen zwischen Benutzern zu initialisieren, aufrechtzuerhalten und zu beenden. Diese Sitzungen können Sprache, Video, Chat, interaktive Spiele und weitere Inhalte umfassen. SIP wurde vom IETF definiert und ist zum de‑facto‑Standard für Sprachkommunikation geworden. Es ist sehr wichtig, zu verstehen, wie SIP funktioniert. Auf Asterisk 22 befindet sich die SIP‑Konfiguration in `pjsip.conf`, einer der am häufigsten bearbeiteten Dateien in einem SIP‑basierten System (direkt nach `extensions.conf`).

### Funktionsweise

SIP ist ein Signalisierungsprotokoll mit den folgenden Komponenten: User Agent Client, User Agent Servers, SIP Proxies und SIP Gateways. Die folgende Abbildung zeigt die Beziehungen zwischen diesen Komponenten.

- UAC (user agent client) – Der Client oder das Terminal, das das SIP‑Signalisieren initiiert.
- UAS (user agent server) – Der Server, der auf ein SIP‑Signalisieren von einem UAC antwortet.
- UA (user agent) – Das SIP‑Terminal (Telefone oder Gateways, die sowohl UAC als auch UAS enthalten).
- Proxy Server – Empfängt Anfragen von einer UA und leitet sie an andere SIP‑Proxies weiter, wenn die jeweilige Station nicht unter deren Verwaltung steht.
- Redirect Server – Empfängt Anfragen und sendet sie zurück an die UA, einschließlich Zielinformationen, anstatt sie direkt an das Ziel weiterzuleiten.
- Location Server – Empfängt Anfragen von einer UA und aktualisiert die Standortdatenbank mit diesen Informationen.

Usually, the proxy, redirect, and location servers are hosted within the same hardware and use the same piece of software, which we call the SIP proxy. The SIP proxy is responsible for location database maintenance, connection establishment, and session termination.

![Die Haupt‑SIP‑Komponenten: User‑Agents (UAC/UAS/UA), der Registrar/Proxy/Redirect‑Server und ein Gateway zur PSTN, wobei die RTP‑Medien direkt zwischen Endpunkten fließen](../images/07-sip-and-pjsip-fig01.png)

#### SIP-Registrierungsprozess

Bevor ein Telefon Anrufe empfangen kann, muss es in einer Standortdatenbank registriert werden. In der Standortdatenbank wird die IP‑Adresse an den Namen gebunden. Im folgenden Beispiel wird die Nebenstelle 8500 an die IP‑Adresse 200.180.1.1 gebunden. Es ist nicht zwingend erforderlich, Telefonnummern zu verwenden. In der SIP‑Architektur könnte die registrierte Nebenstelle auch flavio@voip.school sein.

![SIP-Registrierung: Das Telefon sendet ein REGISTER‑Binding für die Nebenstelle 8500 an seine IP‑Adresse, der Registrar speichert den Kontakt in der Standortdatenbank und antwortet mit 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Proxy-Betrieb

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![Proxy‑Operation: Der SIP‑Proxy bleibt im Signalisierungspfad (INVITE/200 OK) und sucht den Angerufenen im Standort‑Server, während der RTP‑Medienstrom direkt zwischen den beiden Endpunkten fließt](../images/07-sip-and-pjsip-fig03.png)

#### Umleitungsoperation

Beim Weiterleiten sendet der SIP‑Server einfach eine Nachricht (z. B. 302 moved temporarily) an den User Agent und bleibt aus dem Pfad neuer Nachrichten heraus. Es ist sehr ressourcenschonend, aber Sie haben keinerlei Kontrolle. Weiterleitungen werden manchmal in Load‑Balance‑Designs verwendet.

![Umleitungsoperation: Der Weiterleitungsserver beantwortet das INVITE mit einem 302 Moved Temporarily, das den Contact enthält, und tritt dann zurück, während der Anrufer das INVITE/ACK direkt an den neuen Ort erneut sendet】(../images/07-sip-and-pjsip-fig04.png)

#### Wie Asterisk SIP verarbeitet

Es ist wichtig zu verstehen, dass Asterisk weder ein SIP‑Proxy noch ein SIP‑Redirector ist. Asterisk kann die Rolle des Registrars und des Standortservers übernehmen; jedoch verbindet es nur zwei UACs mit sich selbst. Daher wird Asterisk als Back‑to‑Back User Agent (B2BUA) betrachtet. Mit anderen Worten verbindet es zwei SIP‑Kanäle und bridgt sie miteinander. Asterisk verfügt über einen Re‑Invite‑Mechanismus, der die SIP‑Kanäle direkt miteinander kommunizieren lassen kann, anstatt über Asterisk zu laufen. Auf einem PJSIP‑Endpoint wird dies durch den Parameter `direct_media` gesteuert. Wenn `direct_media=yes` verwendet wird, fließt der RTP‑Fluss direkt von einem Endpoint zum anderen, wodurch Serverressourcen frei werden.

#### SIP-Betrieb mit direct_media=yes

![SIP‑Betrieb mit directmedia=yes: SIP‑Signalisierung läuft über Asterisk, während das RTP‑Audio direkt zwischen den beiden Telefonen fließt und Serverressourcen freigibt】(../images/07-sip-and-pjsip-fig05.png)

Allerdings, wenn Sie den Anruf mit Asterisk weiterleiten oder aufnehmen müssen, können Sie den Parameter `direct_media=no` verwenden, um den RTP‑Fluss über den Asterisk‑Server zu erzwingen.

#### SIP-Betrieb mit direct_media=no

![SIP operation with directmedia=no: both the SIP signaling and the RTP audio are anchored through Asterisk, allowing it to record, transcode, or transfer the call](../images/07-sip-and-pjsip-fig06.png)

#### SIP-Nachrichten

Die grundlegenden SIP-Nachrichten sind:

- INVITE – Verbindungsaufbau
- ACK – Bestätigung
- BYE – Verbindungsabbau
- CANCEL – Verbindungsabbau für einen nicht etablierten Anruf
- REGISTER – einen UAC bei einem SIP-Proxy registrieren
- OPTIONS – kann verwendet werden, um Verfügbarkeit zu prüfen
- REFER – einen SIP-Anruf an jemand anderen übertragen
- SUBSCRIBE – sich für Benachrichtigungsereignisse anmelden
- NOTIFY – Kanalinformationen senden
- INFO – verschiedene Nachrichten senden (z. B. DTMF )
- MESSAGE – Sofortnachrichten senden

Die SIP‑Antworten liegen im Textformat vor und sind leicht lesbar (ähnlich wie HTTP‑Nachrichten). Die wichtigsten Antworten sind:

- 1XX – Informationsnachrichten (100–trying, 180–ringing, 183–progress)
- 2XX – Erfolgreiche Anfrage abgeschlossen (200 – OK)
- 3XX – Anrufumleitung, Anfrage muss an einen anderen Ort geleitet werden (302 – moved temporarily, 305 – use proxy)
- 4XX – Fehler (403 – Forbidden)
- 5XX – Serverfehler (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Globaler Fehler (606 – Not acceptable)

Zum Beispiel:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Session Description Protocol (SDP)

SDP wurde ursprünglich in IETF RFC 2327 definiert und ist inzwischen durch RFC 4566 ersetzt worden. Es dient dazu, Multimedia‑Sitzungen für die Ankündigung, Einladung und andere Formen des Starts von Multimedia‑Sitzungen zu beschreiben. SDP umfasst:

- Transportprotokoll (RTP/UDP/IP)
- Medientyp (Text, Audio, Video)
- Medienformat oder Codec (H.261‑Video, g.711‑Audio usw.)
- Informationen, die zum Empfang dieser Medien benötigt werden (Adressen, Ports usw.)

Das folgende Beispiel ist eine Transkription eines SDP, das einen Anruf zwischen zwei Telefonen beschreibt.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### SIP NAT-Überquerung

Network Address Translation (NAT) ist ein Feature, das von den meisten Netzwerken verwendet wird, um Internet‑IP‑Adressen zu sparen. Normalerweise erhält ein Unternehmen einen kleinen Block von IP‑Adressen, und Endbenutzer erhalten dynamisch eine IP‑Adresse, wenn sie mit dem Internet verbunden sind. NAT löst das Adressierungsproblem, indem es interne Adressen internen zu externen Adressen zuordnet. Es speichert eine Zuordnung von internen zu externen Adressen im Speicher. Diese Zuordnung ist für eine bestimmte Zeitdauer gültig, danach wird sie verworfen. Die Zuordnung verwendet IP:Port‑Paare für die internen und externen Adressen. Vier Arten von NAT existieren:

- Full Cone
- Restricted Cone
- Port Restricted Cone
- Symmetric

Die nachstehende NAT-Theorie — die vier NAT-Typen, das Contact-Header-Problem, Keep-Alives und das Erzwingen von Medien über den Server — ist protokollbasiert und gilt für jede SIP-Implementierung. Wie Sie jedes Verhalten in Asterisk 22 (PJSIP) konfigurieren, wird später in diesem Kapitel unter *Nat traversal on res_pjsip* behandelt.

#### Full Cone

Das erste NAT, Full Cone, stellt eine statische Zuordnung von einem externen IP:port-Paar zu einem internen IP:port-Paar dar. Jeder externe Computer kann sich über das externe IP:port-Paar mit ihm verbinden. Dies ist der Fall bei nicht‑zustandsbehafteten Firewalls, die mittels Filter implementiert werden.

![Full Cone NAT: der interne Host (10.0.0.1:8000) ist statisch auf das externe Paar 200.180.4.168:1234 gemappt, sodass jeder externe Computer Pakete an dieses Paar senden und den internen Host erreichen kann](../images/07-sip-and-pjsip-fig11.png)

#### Eingeschränkter Kegel

Im Szenario des eingeschränkten Kegels wird das externe IP:Port‑Paar nur geöffnet, wenn der interne Computer Daten an eine externe Adresse sendet. Allerdings blockiert das eingeschränkte Kegel‑NAT eingehende Pakete von einer anderen Adresse. Mit anderen Worten, der interne Computer muss Daten an einen externen Computer senden, bevor er Daten zurücksenden kann.

#### Portbeschränkter Kegel

Der portbeschränkte Kegel‑Firewall ist fast identisch mit dem eingeschränkten Kegel. Der einzige Unterschied besteht darin, dass das eingehende Paket nun genau von derselben IP und demselben Port wie das gesendete Paket stammen muss.

#### Symmetrisch

Der letzte NAT‑Typ wird symmetrisch genannt. Er unterscheidet sich von den ersten drei dadurch, dass für jede externe Adresse eine spezifische Zuordnung vorgenommen wird. Nur bestimmte externe Adressen dürfen über die NAT‑Zuordnung zurückkehren. Es ist nicht möglich, das externe IP:Port‑Paar vorherzusagen, das vom NAT‑Gerät verwendet wird. Die anderen drei NAT‑Typen erlauben die Nutzung eines externen Servers, um die externe IP‑Adresse für die Kommunikation zu ermitteln. Bei symmetrischem NAT kann die ermittelte Adresse, selbst wenn man sich mit einem externen Server verbinden kann, für kein anderes Gerät außer diesem Server verwendet werden.

![Symmetrisches NAT: für jedes Ziel wird ein anderer externer Quellport zugewiesen, sodass die entdeckte Zuordnung zu einem Server nicht von einem anderen Host wiederverwendet werden kann, was die STUN-basierte Durchdringung verhindert](../images/07-sip-and-pjsip-fig12.png)

#### NAT-Firewall-Tabelle

Die folgende Tabelle fasst die vier Arten von NAT zusammen.

| NAT-Typ | Muss zuerst Daten senden | Kann die externe IP:Port für Rückpakete bestimmen | Beschränkt eingehende Pakete auf die Ziel-IP:Port |
| --- | --- | --- | --- |
| Full Cone | No | Yes | No |
| Restricted Cone | Yes | Yes | Only IP |
| Port Restricted Cone | Yes | Yes | Yes |
| Symmetric | Yes | No | Yes |

#### SIP signaling and RTP over NAT

Einige der größten Probleme bei der NAT‑Durchquerung sind, dass Sie zwei Probleme lösen müssen: SIP‑Signalisierung und Audio (RTP). Die meisten Probleme mit einseitigem Audio sind NAT‑bedingt. Eine interessante Sache bei SIP ist, dass, wenn ein UAC ein Paket sendet, es die IP‑Adresse im SIP‑„Contact“-Header‑Feld einbettet. Normalerweise ist dies eine interne (RFC1918) Adresse; Antworten auf dieses Paket können nicht über das Internet zurück zum UAC geroutet werden. Die konzeptionellen Lösungen sind immer dieselben:

- **Ignoriere die Contact/Via‑Adresse und antworte dort, wo das Paket tatsächlich herkam.** Dies ist das in RFC 3581 definierte Verhalten (`rport`). Auf PJSIP ist es `force_rport=yes`, und `rewrite_contact=yes` überschreibt den gespeicherten Contact mit der Quelladresse.  
- **Sende Medien zurück an die Adresse, von der das RTP tatsächlich eingetroffen ist** (symmetrisches RTP, historisch *comedia* genannt). Auf PJSIP ist das `rtp_symmetric=yes`.  
- **Halte das NAT‑Mapping offen.** Wenn das Mapping abläuft, kann Asterisk keine INVITE mehr an den UAC senden — das Telefon kann Anrufe tätigen, aber nicht empfangen. Das periodische Senden von OPTIONS (ein *qualify*) hält das Loch offen. Auf PJSIP ist das `qualify_frequency=` auf dem AOR.

If the user’s NAT is of the symmetric type, it is not possible to send packets from one UAC to another directly; in that case you have to force the RTP through Asterisk with `direct_media=no`. These configurations are appropriate for most cases. It is possible to optimize the traffic using advanced techniques like Simple Traversal of UDP over NAT (STUN), which is useful with full cone, restricted cone, and port restricted cone, and Application Layer Gateway (ALG). Unfortunately, most firewalls today — even home DSL/cable routers — are symmetric, making STUN unusable. ALG could solve the problem, but it is not supported, not implemented, or buggy in most cases.

#### Asterisk hinter NAT

Manchmal befindet sich der Asterisk-Server selbst hinter einer Firewall mit NAT – eine sehr häufige Situation, wenn Sie in der Cloud bereitstellen. In diesem Fall ist es notwendig, zusätzliche Konfiguration vorzunehmen, damit Asterisk seine **public** Adresse in den SIP- und SDP-Headern anstelle seiner privaten Adresse bewirbt.

Konzeptionell gibt es drei Schritte:

- Leiten Sie den SIP‑Signalisierungsport (UDP 5060 standardmäßig) von der Firewall zum Asterisk‑Server weiter.
- Leiten Sie den RTP‑Medienportbereich (UDP 10000–20000 standardmäßig, festgelegt in `rtp.conf`) von der Firewall zum Asterisk‑Server weiter.
- Teilen Sie Asterisk seine externe Adresse und welches Netzwerk lokal ist mit, damit es weiß, wann die öffentliche Adresse in die Header eingesetzt werden muss.

Bei PJSIP entsprechen diese letzten beiden Elemente `external_media_address` / `external_signaling_address` und `local_net=` im **transport**, und der RTP‑Portbereich wird weiterhin in `rtp.conf` konfiguriert:

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

Die vollständige, ausgearbeitete PJSIP‑Konfiguration für einen Asterisk‑Server hinter NAT wird später in diesem Kapitel unter *Asterisk Server behind NAT* angegeben.

### SIP‑Einschränkungen

Asterisk verwendet den eingehenden RTP‑Strom, um den ausgehenden Strom zu synchronisieren. Wird der eingehende Strom unterbrochen (Silenzienunterdrückung), wird die Musik‑on‑Hold abgeschnitten. Mit anderen Worten, Sie sollten bei Telefonen oder Anbietern, die Asterisk verwenden, keine Silenzienunterdrückung einsetzen.

## PJSIP: der SIP‑Kanal

PJSIP ist der SIP‑Kanal in Asterisk. Er wurde erstmals in Asterisk 12 eingeführt und nach jahrelanger Entwicklung zum Standard‑ und empfohlenen SIP‑Kanal. In Asterisk 22 (dem aktuellen LTS) ist er der einzige SIP‑Kanal‑Treiber. PJSIP basiert auf Teluu’s Projekt namens pjproject. Der pjproject‑Stack wird von vielen Softphones und kommerziellen SIP‑Implementierungen verwendet. Er ist ein vielseitiger und ausgereifter SIP‑Stack.

### Warum PJSIP verwenden

PJSIP war ein kompletter Neuentwurf, wie Asterisk SIP spricht, und es lohnt sich, die Funktionen zu verstehen, die es zum Standard gemacht haben.

#### Funktionen

Der Kanal unterstützt viele Funktionen, einige verdienen hier Erwähnung

- Mehrfache Registrierungen: Sie können mehr als ein Telefon verwenden, das mit demselben Address of Record verbunden ist. Mit anderen Worten, Sie können zwei Telefone mit demselben endpoint verbinden.
- Freundliche Application Program Interface (API). Die API ist modular und leicht erweiterbar, aufgebaut aus vielen kleinen kooperierenden Modulen statt einem großen Code‑Block.
- Mehrfache Transporte: Sie können beim Einsatz von PJSIP an mehrere Adressen, Ports und Transporte lauschen. Sie sind nicht auf eine einzige Bind‑Adresse für alle Ihre Geräte beschränkt. PJSIP ist sehr flexibel.

#### Hinweis zur Konfiguration

Die PJSIP‑Konfiguration ist ausführlicher: Sie erfordert etwas mehr Aufwand und mehr Zeilen Konfiguration, da jedes Gerät durch mehrere verwandte Objekte statt eines einzigen peer‑Blocks beschrieben wird. Diese zusätzliche Struktur verleiht PJSIP seine Flexibilität, und der Konfigurations‑Wizard (später behandelt) hält die tägliche Bereitstellung kurz.

### PJSIP‑Module

Der PJSIP‑Kanal wird durch viele unten beschriebene Module implementiert:

#### res_pjsip

Dies ist die Basisschicht von PJSIP und das Hauptmodul. Es ist für einige der wichtigsten Dienste verantwortlich.

#### res_pjsip_session

Dieses Modul ist für Mediensitzungen, die Verarbeitung des Session Description Protocol und einige Add‑ons verantwortlich.

#### res_pjsip_messaging

Verarbeitet SIP‑Nachrichten und analysiert SIP‑Header.

#### res_pjsip_registrar

Verantwortlich für die Handhabung von SIP‑Registrierungen.

#### res_pjsip_pubsub

Verantwortlich für die Verarbeitung von subscribe, notify und publish. Diese Nachrichten sind für die Handhabung von SIP‑Presence und BLF (Busy Lamp Field) zuständig.

### PJSIP‑Konfiguration

PJSIP hat viele verschiedene Abschnitte. Das Format der Abschnitte ist:

```
[Section Name]
Option = Value
Option = Value
```

#### End point section

Das wichtigste Konfigurationsobjekt ist der endpoint. Die endpoint-Konfiguration hat Kernfunktionalität und muss mit einem AOR und einem Transport-Abschnitt verknüpft werden. Beispiel:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

Wenn Sie sich das obige Beispiel ansehen, ist der Endpoint eine Art Klebstoff, der alle Abschnitte miteinander verbindet. Er gibt einen Transport, die Address of Record und die Authentifizierung für ein Telefon an. Außerdem definiert er den wichtigsten Teil, den Einstiegspunkt des Kontextes im Dialplan.

#### Address of Record (AOR)

Dieses Objekt teilt Asterisk mit, wo der Endpoint zu erreichen ist. Es speichert die Kontaktadressen. Es ermöglicht außerdem die Konfiguration von Mailboxen. Beispiel:

```
[softphone]
type=aor
max_contacts=2
```

#### Authentifizierung

Dieser Abschnitt ist für eingehende und ausgehende Authentifizierung verantwortlich. Die Dokumentation findet sich in der Beispieldatei pjsip.conf. Beispiel:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### Transport

Der Transport‑Abschnitt ermöglicht es Ihnen, IPv4‑ und IPv6‑Adressen sowie das Transportprotokoll TCP, UDP, TLS, Websockets usw. zu definieren. Sie können in diesem Abschnitt auch NAT‑adressen konfigurieren. Sie können mehrere Transporte anlegen, aber sie dürfen nicht dieselbe IP und denselben Port teilen, und Sie können nicht mehrere TCP‑ oder TLS‑Transporte derselben IP‑Version binden. Beispiel:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Registrierung

Dieses Objekt wird verwendet, um eine ausgehende Registrierung zu konfigurieren. Beispiel:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identifizieren

Dieses Objekt steuert, welche SIP‑Anfrage zu welchem Endpoint gehört. Wenn Sie keinen Identify‑Abschnitt haben, gleicht das System den Inhalt des „From“-Headers mit dem Namen des Endpoints ab. Mit diesem Abschnitt können Sie bestimmten Endpoints, die durch Benutzernamen oder IP identifiziert werden, spezifische IP‑Adressen zuweisen. Beispiel:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

Das ACL-Objekt ermöglicht es Ihnen, bestimmte Netzwerke mit Zugriff auf den Endpunkt zu konfigurieren. ACLs werden jetzt in einem speziellen Abschnitt oder in der acl.conf definiert. Beispiel:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relationship between entities

The relationship between the configuration objects provides a great flexibility for configuration. However, it seems a bit complex for anyone starting.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

The graphic above means:

#### Relationships:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | many to many |
| ENDPOINT / AUTH | zero to many, to zero to one |
| ENDPOINT / IDENTIFY | zero to one |
| ENDPOINT / TRANSPORT | zero to many, to at least one |
| REGISTRATION / AUTH | zero to many, to zero to one |
| REGISTRATION / TRANSPORT | zero to many, to at least one |
| AOR / CONTACT | many to many |

ACL and DOMAIN_ALIAS don’t have a direct configuration relationship to the other objects.

### Configuring a Softphone

To configure a softphone you have to define many different sections. Below an example on how to configure a softphone. For the client side you can use the SipPulse Softphone (https://www.sippulse.com/produtos/softphone), which you can download and register against the endpoint below.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

Die obige Konfiguration legt einen Transport für UDP im Port 5060 fest, definiert anschließend einen Endpoint, dessen Authentifizierung per Benutzername und Passwort sowie den Address of Record mit maximal zwei Kontakten.

### Konfiguration eines SIP‑Trunks

Um einen SIP‑Trunk zu konfigurieren, benötigen Sie die IP‑Adresse oder den Host des SIP‑Trunks, den Namen und das Passwort. Sie müssen dafür einen neuen Registrierungs‑Abschnitt anlegen.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Nat traversal on res_pjsip

Network Address Translation wurde vor langer Zeit als Mittel zur Bewältigung des Mangels an IPv4‑Adressen geschaffen. Viele Menschen nutzen NAT auch als Sicherheitsfunktion, um die internen Adressen eines Netzwerks vor dem öffentlichen Internet zu verbergen. Manchmal muss man NAT‑Traversal handhaben. In einigen Fällen kann der Server hinter NAT stehen, etwa wenn Sie den Server in der Cloud bereitstellen. Häufig befinden sich bei einer Cloud‑Bereitstellung auch die Nutzer hinter einem NAT‑Router. Zur besseren Übersicht teilen wir das Thema in zwei Teile. Der erste Teil behandelt den Asterisk‑Server hinter NAT, wie bei einer Cloud‑Bereitstellung. Im zweiten Abschnitt zeigen wir, wie Clients hinter NAT mit res_pjsip unterstützt werden können.

#### Asterisk Server behind NAT

Wenn der Asterisk‑Server hinter NAT steht, sollten Sie die externe und interne lokale Adresse im Transport‑Abschnitt angeben. Wir benötigen die folgenden Direktiven.

##### direct_media

Fließt das Medium direkt von Peer zu Peer oder über den Server? Für NAT sollte es über den Server fließen. Für NAT wählen Sie **no**. Beispiel:

```
direct_media=no
```

##### external_media_address

Medienadresse zur Handhabung von externem RTP. In der Regel dieselbe wie die external_signaling_address. Verwenden Sie die öffentliche IP-Adresse Ihres Servers für Medien und Signalisierung. Beispiel:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Externe SIP-Adresse, über die Nachrichten empfangen werden. Beispiel:

```
external_signaling_address=54.232.1.20
```

##### local_net

Das Netzwerk, das Sie als Ihr lokales Netzwerk betrachten. Beispiel:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Komplettes Beispiel für Transport für einen Asterisk-Server hinter NAT

Um einen Asterisk-Server hinter NAT zu verwenden, müssen Sie zwei Schritte ausführen. Erstens einen Transport hinter NAT definieren. Zweitens diesen Transport dem Endpoint zuordnen.

##### Erstellen des Transports hinter NAT

Um den Transport hinter NAT in der Datei pjsip.conf zu erstellen, erzeugen Sie einen Abschnitt wie unten.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

# Transport einem Endpunkt zuordnen

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Für SIP‑Trunks sollten Sie den Transport ebenfalls dem Registrierungsabschnitt wie unten zuordnen.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Verwendung von Asterisk mit Clients hinter NAT

Um Telefone hinter NAT zu verwenden, müssen Sie einige zusätzliche Parameter pro Endpoint konfigurieren.

##### direct_media

Fließt das Medium direkt von Peer zu Peer oder über den Server? Für NAT sollte es über den Server fließen. Beispiel:

```
direct_media=no
```

##### rtp_symmetric

Das ist, was wir comedia nennen. Anstatt sich wie üblich in SIP auf die im SDP-Header definierte Adresse zu verlassen, verwendet man die Adresse, von der man das erste rtp packet empfängt, und sendet zurück von derselben Adresse. Beispiel:

```
rtp_symmetric=yes
```

##### force_rport

Dies ist das in RFC3581 definierte Verhalten. Anstatt die Adresse im VIA-Header zu verwenden, werden die Antworten von dem Ort zurückgesendet, von dem die Anfragen kommen. Beispiel:

```
force_rport=yes
```

##### qualify_frequency

Diese Einstellung muss auf das AOR (nicht den endpoint) angewendet werden. Es gibt außerdem den letzten Schritt, die Option qualify zu konfigurieren. Sie sollten immer einige Pakete haben, die das Ziel anpingen, um die NAT‑Zuordnung offen zu halten. Dies wird im AOR‑Abschnitt gesetzt. Beispiel:

- qualify_frequency=15

Vollständiges Beispiel eines endpoint, bei dem Server und Client hinter NAT stehen

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Kanalbenennung

Wie üblich ist einer der wichtigen Aspekte eines Kanals seine Benennung, und PJSIP hat einige interessante Details. Sie wählen einen PJSIP‑Endpoint mit der `PJSIP/`‑Technologie:

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Eine nützliche Funktion ist die Möglichkeit, alle an einem AOR registrierten Kontakte auf einmal zu wählen. Die Funktion PJSIP_DIAL_CONTACTS wird in die Liste der zu wählenden Kontakte übersetzt.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

Ein Trunk zu wählen ist etwas anders. Angenommen, der Trunk wird nicht bei Ihrer Plattform registriert oder hat keine IP‑Adresse, die mit Ihrer AOR (Address of Record) verknüpft ist. Sie können die Adresse des Trunks direkt in der Zeile angeben. Als Beispiel wird eine internationale Rufnummer verwendet.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Wenn Sie es vorziehen, die Adresse des Trunks im AOR‑Abschnitt anzugeben, können Sie auch verwenden.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### PJSIP-Konfigurationsassistent

PJSIP ist leistungsstark, aber bei der Konfiguration sehr umfangreich: viele verschiedene Abschnitte und Vorlagen, die zunächst verwirrend sein können. Die gute Nachricht ist der PJSIP-Konfigurationsassistent. Indem jeder Kanal in wenigen Zeilen definiert wird, ermöglicht er das Erstellen von Vorlagen und vereinfacht die Konfiguration neuer Geräte. Verwenden Sie die Datei pjsip_wizard.conf zur Konfiguration. Sie müssen weiterhin Transport‑ und globale Abschnitte in der Datei pjsip.conf definieren. Persönlich nutze ich den Assistenten nur für Telefone; für SIP‑Trunks ist die Anzahl meist nicht groß und man kann sie direkt in pjsip konfigurieren. Der größte Vorteil des Assistenten ist die Möglichkeit, Vorlagen zu verwenden und Telefone schnell anzulegen.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Laden und Entladen von PJSIP

PJSIP ist der einzige SIP‑Kanal in Asterisk 22, und seine Module werden standardmäßig geladen. In seltenen Fällen möchten Sie möglicherweise die Modul‑Ladung über die Datei modules.conf steuern — zum Beispiel, um PJSIP auf einem Server zu deaktivieren, der nur IAX2 oder DAHDI verwendet.

#### Zum Deaktivieren von PJSIP

Bearbeiten Sie die Datei modules.conf und fügen Sie die folgenden Zeilen hinzu.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### Console commands

Now that you configured your PJSIP endpoints, it is time to see how to check your configuration. There are many console commands to help you with this task. After editing pjsip.conf, reload the configuration with:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

#### pjsip set history on

Eine großartige Ergänzung zu PJSIP ist das Konzept der History. Sie können SIP‑Anfragen und -Antworten in Echtzeit auf einfache Weise erfassen und analysieren. Um die History zu starten, verwenden Sie den untenstehenden Befehl.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Jetzt können Sie die History anzeigen:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Um dann eine bestimmte Anfrage oder Antwort zu sehen, zeigen Sie das History‑Element an:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Sehr einfach, nicht wahr? Sie können die History jederzeit mit `pjsip set history clear` löschen.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Zusammenfassung

SIP ist das IETF‑Signalisierungsprotokoll, das Medien‑Sessions aufbaut, ändert und beendet. Seine User‑Agents, Proxies, Registrar und Gateways tauschen textbasierte Nachrichten aus — REGISTER, INVITE, die vorläufigen und endgültigen Antworten, ACK und BYE — während SDP die Codecs verhandelt und RTP die Medien transportiert. Diese Protokoll‑Theorie ist zeitlos und gilt für jede SIP‑Implementierung.

In Asterisk 22 spricht man SIP über **PJSIP** (`chan_pjsip`), konfiguriert in `pjsip.conf`. Anstatt eines monolithischen Peers wird ein Gerät als Satz kleiner, miteinander referenzierter Objekte modelliert: `endpoint` (Anrufverhalten und Codecs), `auth` (Anmeldedaten), `aor` (wo es erreichbar ist) und `transport` (der Listener), plus `identify` (einen Trunk per IP zuzuordnen) und `registration` (ausgehende Registrierung) für Dienstanbieter. Sie haben gesehen, wie diese Objekte zusammenpassen, wie sowohl Telefone als auch Trunks konfiguriert werden, wie die NAT‑Traversierungs‑Optionen (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media` und die Transport‑`external_*`/`local_net`) reale Einsätze lösen, und wie man das alles mit `pjsip show endpoints`, `aors`, `contacts` und `registrations` inspiziert.

## Quiz

1. In der SIP‑Architektur, welche Komponente empfängt eine Anfrage und beantwortet sie mit einer Redirect‑Antwort (wie `302 Moved Temporarily`) mit dem neuen Standort, und bleibt dann aus dem Pfad der nachfolgenden Nachrichten heraus?
   - A. Proxy‑Server
   - B. Redirect‑Server
   - C. Location‑Server
   - D. Registrar

2. Welche Rolle spielt Asterisk, wenn es einen SIP‑Anruf zwischen zwei Telefonen verarbeitet?
   - A. Ein SIP‑Proxy, der nur im Signalisierungspfad bleibt
   - B. Ein SIP‑Redirect‑Server
   - C. Ein Back‑to‑Back‑User‑Agent (B2BUA), der zwei SIP‑Kanäle verbindet
   - D. Ein zustandsloser SIP‑Load‑Balancer

3. Welche SIP‑Methode wird von einem Telefon verwendet, um dem Registrar seine aktuelle IP‑Adresse mitzuteilen, damit es später Anrufe erhalten kann?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Wahr oder Falsch: In Asterisk 22 sind `chan_sip` und `sip.conf` noch als Legacy‑Fallback neben PJSIP verfügbar.

5. Welche Konfigurationsobjekte muss einem Endpoint zugeordnet sein, damit Asterisk den zu benutzenden Listening‑Socket kennt und weiß, wohin Anrufe für dieses Gerät gesendet werden sollen? (Wählen Sie alle zutreffenden aus.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. In einem PJSIP `aor`‑Objekt, welche Einstellung hält die NAT‑Zuordnung offen, indem sie periodisch den Contact qualifiziert, und welche Einheit hat sie?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. Lückentext: Damit Asterisk eine eingehende SIP‑Anfrage anhand der Quell‑IP‑Adresse (statt anhand des `From`‑Headers) einem bestimmten Endpoint zuordnet, erstellen Sie einen Abschnitt mit `type=________`.

8. Welches PJSIP‑Objekt wird verwendet, um eine **ausgehende** Registrierung von Asterisk zu einem SIP‑Trunk‑Provider zu konfigurieren?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Auf der Asterisk 22‑CLI, welcher Befehl aktiviert den SIP‑Paket‑Logger, der jede SIP‑Anfrage und -Antwort in der Konsole ausgibt?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Auf einem PJSIP‑Endpoint, das ein Telefon hinter einem symmetrischen NAT bedient, welches Paar von Einstellungen lässt Asterisk auf die Quelladresse der Anfrage (RFC 3581) antworten und Medien dorthin senden, wo das RTP tatsächlich ankommt?
    - A. `direct_media=yes` und `srvlookup=yes`
    - B. `force_rport=yes` und `rtp_symmetric=yes`
    - C. `allowguest=yes` und `insecure=invite`
    - D. `qualify=yes` und `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
