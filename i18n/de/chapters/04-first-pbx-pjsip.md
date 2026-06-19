# Aufbau Ihrer ersten PBX mit PJSIP

In diesem Kapitel lernen Sie, wie Sie eine grundlegende Asterisk PBX-Konfiguration durchführen. Das Hauptziel besteht darin, die PBX zum ersten Mal in Betrieb zu nehmen, Anrufe zwischen Nebenstellen zu tätigen, eine abgespielte Nachricht anzurufen und eine Verbindung zu einem einzelnen analogen oder SIP-Trunk herzustellen. Die Idee hinter diesem Kapitel ist es, sicherzustellen, dass Ihr Asterisk so schnell wie möglich einsatzbereit ist. Nach Abschluss der Arbeiten in diesem Kapitel verfügen Sie über ausreichend Hintergrundwissen, um sich auf die nachfolgenden Kapitel vorzubereiten, in denen wir tiefer in die Konfigurationsdetails eintauchen werden.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Konfigurationsdateien zu verstehen und zu bearbeiten;
- SIP-basierte Softphones zu installieren;
- Einen SIP-Trunk zu installieren und zu konfigurieren;
- Eine analoge Verbindung zu installieren und zu konfigurieren;
- Anrufe zwischen Nebenstellen zu tätigen;
- Anrufe zwischen Telefonen und externen Zielen zu tätigen; und
- Eine automatische Telefonzentrale (Auto Attendant) zu konfigurieren.

## Verständnis der Konfigurationsdateien

Asterisk wird über Text-Konfigurationsdateien gesteuert, die sich in /etc/asterisk befinden. Das Dateiformat ähnelt den Windows-„.ini“-Dateien. Ein Semikolon wird als Kommentarzeichen verwendet, die Zeichen „=” und „=>“ sind gleichwertig, und Leerzeichen werden ignoriert.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpretiert „=” und „=>“ auf die gleiche Weise. Syntaxunterschiede werden verwendet, um zwischen Objekten und Variablen zu unterscheiden. Verwenden Sie „=“, wenn Sie eine Variable deklarieren möchten, und „=>“, um ein Objekt zu bezeichnen. Die Syntax ist in allen Dateien gleich, aber es werden drei Arten von Grammatik verwendet, wie unten erläutert.

## Grammatiken

| Grammatik | Wie das Objekt erstellt wird | Konf.-Datei | Beispiel |
|---------|---------------------------|------------|---------|
| Einfache Gruppe | Alles in derselben Zeile | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Optionsvererbung | Optionen werden zuerst definiert, das Objekt erbt die Optionen | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Komplexe Entität | Jede Entität erhält einen Kontext | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Einfache Gruppe

Das Format der einfachen Gruppe, das in extensions.conf, meetme.conf und voicemail.conf verwendet wird, ist die grundlegendste Grammatik. Jedes Objekt wird mit Optionen in derselben Zeile deklariert. Beispiel:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

In diesem Beispiel wird Objekt 1 mit den Optionen op1, op2 und op3 erstellt, während Objekt 2 mit den Optionen op1, op2 und op3 erstellt wird.

### Grammatik der Objekt-Optionsvererbung

Dieses Format wird von den Dateien chan_dahdi.conf und agents.conf verwendet, in denen zahlreiche Optionen verfügbar sind und die meisten Schnittstellen und Objekte dieselben Optionen teilen. Typischerweise enthalten ein oder mehrere Abschnitte Objekt- und Kanaldeklarationen. Optionen für das Objekt werden über dem Objekt deklariert und können für ein anderes Objekt geändert werden. Obwohl dieses Konzept schwer zu verstehen ist, ist es sehr einfach anzuwenden. Beispiel:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Die ersten beiden Zeilen konfigurieren den Wert der Optionen op1 und op2 auf „bas“ bzw. „adv“. Wenn Objekt 1 instanziiert wird, wird es mit Option 1 als „bas“ und Option 2 als „adv“ erstellt. Nach der Definition von Objekt 1 ändern wir Option 1 auf „int“. Als Nächstes erstellen wir Objekt 2 mit Option 1 als „int“ und Option 2 als „adv“.

### Komplexe Entität

Dieses Format wird von pjsip.conf, iax.conf und anderen Konfigurationsdateien verwendet, in denen zahlreiche Entitäten mit vielen Optionen existieren. Typischerweise teilt dieses Format kein großes Volumen an gemeinsamen Konfigurationen. Jede Entität erhält einen Kontext. Manchmal existieren reservierte Kontexte, wie [general] für globale Konfigurationen. Optionen werden in den Kontextdeklarationen deklariert. Beispiel:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

Die Entität [entity1] hat die Werte „value1“ und „value2“ für die Optionen op1 bzw. op2. Die Entität [entity2] hat die Werte „value3“ und „value4“ für die Optionen op1 und op2.

## Optionen zum Aufbau eines LAB für Asterisk

Um eine PBX zu konfigurieren, benötigen Sie einige grundlegende Hardware. Es ist weder schwierig noch teuer, aber es gibt einige Optionen, die berücksichtigt werden sollten. Alles, was Sie benötigen, sind zwei Telefone und eine Verbindung zum öffentlichen Netz. Es gibt einige Optionen und Kombinationen beim Erstellen Ihres Labs, die wir unten besprechen werden.

### Option 1: Vollständiges LAB

Mit dem vollständigen LAB ist es möglich, alle verfügbaren Szenarien zu testen und Lösungen wie ATA, IP-Telefone und Softphones zu vergleichen. Sie können auch etwas über analoge und SIP-Trunks lernen. Sie benötigen:

- Einen SIP-Analog-Telefonadapter (ATA)
- Ein IP-Telefon
- Einen dedizierten Server für Asterisk
- Eine Workstation mit einem Softphone
- Eine analoge Schnittstellenkarte mit mindestens zwei Schnittstellen (1 FXO und 1 FXS)
- Ein Konto bei einem VoIP-Anbieter

### Option 2: Economy LAB

Mit dem Economy LAB vereinfachen wir es ein wenig. Wir verwenden den ATA, der normalerweise günstiger ist als das IP-Telefon, und eine einzelne FXO-Karte, die wirklich preiswert ist. Wir werden keine analogen Telefone direkt an den Server anschließen können, aber das kommt in der Praxis selten vor. Sie benötigen:

- Einen SIP-Analog-Telefonadapter (ATA)
- Einen dedizierten Server für Asterisk
- Eine Workstation für das Softphone
- Eine analoge Schnittstellenkarte mit 1 FXO
- Ein Konto bei einem VoIP-Anbieter

### Option 3: Super Economy LAB

Das dritte LAB verwendet einen virtualisierten Server auf dem eigenen Notebook des Schülers. Das Problem bei diesem Modell sind die Konflikte, die durch den UDP-Port entstehen. Manchmal versuchen sowohl der Asterisk-Server als auch das Softphone, auf denselben Port zuzugreifen, was Asterisk daran hindert, den Adress-Port zu binden. Ein weiteres Problem ist die Qualität der Anrufe; virtuelle Umgebungen sind nicht für Echtzeitanwendungen wie Asterisk geeignet. Verwenden Sie ein kostenloses Softphone für den Server und die Workstation sowie eine Trunk-Verbindung zu einem SIP-Anbieter. Sie benötigen:

- Einen Laptop, auf dem ein Softphone läuft
- Eine virtuelle Maschine (VirtualBox, VMware oder ähnlich), um Asterisk zu installieren
- Ein Konto bei einem VoIP-Anbieter

## Installationssequenz

Um Ihnen das Verständnis der Installationssequenz zu erleichtern, haben wir die notwendigen Schritte zur Installation und Konfiguration von Asterisk skizziert.

![Referenz-Lab-Layout: SIP/IAX-Softphones, ein IP-Telefon und analoge Adapter als Nebenstellen (1), der Asterisk-Server mit ETH0/FXO/FXS-Schnittstellen (3) und die Trunks zum PSTN über einen VoIP-Anbieter oder eine Breitbandverbindung (2).](../images/04-first-pbx-fig01.png)

1. Konfiguration der Nebenstellen a. SIP-Nebenstellen (ATA, Softphone, IP-Telefon) b. IAX-Nebenstellen c. FXS-Nebenstellen 2. Trunk-Konfiguration a. Konfiguration eines SIP-Trunks b. Konfiguration eines FXO-Trunks 3. Aufbau eines grundlegenden Dialplan a. Wählen zwischen Nebenstellen b. Wählen externer Ziele c. Empfangen eines Anrufs von der Operator-Nebenstelle d. Empfangen eines Anrufs in einer automatischen Telefonzentrale

## Konfiguration der Nebenstellen

Die Nebenstellen sind SIP-, IAX- oder analoge Telefone, die an einen FXS-Port angeschlossen sind. Um eine Nebenstelle zu konfigurieren, sollten Sie die Konfigurationsdatei bearbeiten, die sich auf den Kanal bezieht (pjsip.conf, iax.conf, chan_dahdi.conf).

### SIP-Nebenstellen

In Asterisk 22 ist PJSIP (der `res_pjsip` Stack, konfiguriert in `/etc/asterisk/pjsip.conf`) der SIP-Kanaltreiber. Er unterstützt mehrere Transporte pro Endpoint, wird aktiv gewartet und ist der einzige SIP-Treiber, der mit der Plattform ausgeliefert wird. (Der ursprüngliche `chan_sip` Treiber wurde in Asterisk 21 entfernt – siehe das Kapitel *Legacy channels*, falls Sie eine alte Konfiguration migrieren müssen.)

Die Idee hier ist, eine einfache PBX zu konfigurieren. (Nachfolgende Kapitel bieten eine vollständige SIP/PJSIP-Sitzung mit allen Details.) PJSIP wird in `/etc/asterisk/pjsip.conf` konfiguriert und enthält alle Parameter, die sich auf SIP-Telefone und VoIP-Anbieter beziehen. SIP-Clients müssen konfiguriert werden, bevor Sie Anrufe tätigen und empfangen können.

#### Der Transport

In PJSIP befindet sich die Listener-Konfiguration (Bind-Adresse, Port, Protokoll) in einem `transport` Objekt. Asterisk verfügt über einen eingebauten Schutz gegen das Erraten von Benutzernamen – es gibt immer eine identische Authentifizierungsaufforderung für unbekannte und bekannte Benutzer zurück, und wiederholte nicht identifizierte Anfragen von einer IP werden über die `[global]` Optionen `unidentified_request_count`/`unidentified_request_period` ratenbegrenzt. Die Hauptoptionen eines Transports sind:

- protocol: Das Transportprotokoll — `udp`, `tcp`, `tls`, `ws` oder `wss`.
- bind: Adresse und Port, an die der Listener bindet. Wenn Sie die Adresse auf `0.0.0.0` setzen, bindet er an alle Schnittstellen; der SIP-Port ist standardmäßig 5060 für UDP/TCP.

Ein minimaler UDP-Transport:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Die Codec-Auswahl (`disallow`/`allow`) und der Standard `context` werden auf jedem `endpoint` (siehe unten) konfiguriert, nicht auf dem Transport. Anonyme/Gast-Anrufe werden von einem `endpoint` namens `anonymous` behandelt. Registrierungs-Timer werden pro AOR über `maximum_expiration`/`default_expiration` gesteuert.

#### SIP-Clients

Nach Abschluss des Transport-Abschnitts ist es an der Zeit, die SIP-Clients einzurichten. Ich möchte den Leser noch einmal daran erinnern, dass wir später im Buch ein ganzes SIP/PJSIP-Kapitel haben werden. Konzentrieren wir uns vorerst auf die Grundlagen und überlassen die Details für später.

In PJSIP wird ein SIP-Client aus einer Reihe zusammengehöriger Objekte aufgebaut, die durch Namensreferenz miteinander verbunden sind:

- `endpoint`: Das Anrufverhalten — Codecs (`allow`/`disallow`), der Dialplan `context` und welche `auth` und `aors` er verwendet.
- `auth`: Die Anmeldedaten. `username` ist der SIP-Authentifizierungsbenutzer und `password` ist das Geheimnis (Secret), das zur Authentifizierung des Geräts verwendet wird.
- `aor`: Die "Address of Record" (AOR) — wo der Endpoint erreicht werden kann. Entweder eine statische `contact=` (für ein Gerät mit fester IP) oder `max_contacts=`, um dem Gerät die dynamische Registrierung zu ermöglichen.

Warnung: Verwenden Sie starke Passwörter mit mindestens 8 Zeichen, alphanumerischen und numerischen Zeichen sowie mindestens einem Symbol. Berichte über gehackte Server sind in den Mailinglisten aufgetaucht, und Brute-Force-Passwort-Cracker für SIP sind für Script-Kiddies leicht verfügbar. Telefonbetrug kostet Verbraucher und Anbieter Tausende von Dollar.

Endpoint 6000 ist ein Gerät mit fester IP, daher trägt seine AOR eine statische `contact`, anstatt eine Registrierung zu erlauben. Endpoint 6001 ist ein Gerät, das sich registriert, daher erlaubt seine AOR die Registrierung (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=userpass
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=userpass
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP erlaubt es den Abschnitten `endpoint`, `auth` und `aor`, denselben Abschnittsnamen zu teilen (z. B. die beiden `[6001]` Blöcke oben, unterschieden durch ihre `type=`); viele Administratoren hängen stattdessen Suffixe an (`[6001]`, `[6001-auth]`, `[6001]` aor), um die Lesbarkeit zu verbessern. Bei einem Gerät, das sich registriert, wird der Kontakt dynamisch gelernt, wenn sich das Telefon registriert, daher benötigt die AOR keine statische `contact`.

## IAX-Nebenstellen

`chan_iax2` wird in Asterisk 22 immer noch mitgeliefert, ist aber jetzt veraltet (Legacy); SIP/PJSIP ist das bevorzugte Protokoll für neue Bereitstellungen.

Sie können auch IAX-Nebenstellen erstellen. Dieses Protokoll ist nativ für Asterisk, und wir werden später in diesem Buch einen ganzen Abschnitt dazu haben. Erstellen wir vorerst ein paar Nebenstellen unter Verwendung des Protokolls. Als erster zu konfigurierender Abschnitt hat der Abschnitt [general] bestimmte Parameter, die konfiguriert werden müssen. Die Hauptoptionen sind:

- allow/disallow: Definiert, welche Codecs verwendet werden sollen.
- bindaddr: Adresse, an die der Asterisk SIP-Listener gebunden werden soll. Wenn Sie sie auf 0.0.0.0 (Standard) setzen, bindet er an alle Schnittstellen.
- context: Legt den Standardkontext für alle Clients fest, sofern er nicht im Client-Abschnitt geändert wird. Wir haben aus Sicherheitsgründen dummy verwendet. Nicht authentifizierte Benutzer gelangen in diesen Kontext, wenn die Option allowguest auf yes gesetzt ist.
- bindport: SIP-UDP-Port, auf dem gelauscht werden soll.
- delayreject: Wenn auf yes gesetzt, verzögert dies das Senden einer Authentifizierungsablehnung für ein REGREQ oder AUTHREQ, was die Sicherheit gegen Brute-Force-Passwortangriffe verbessert.
- bandwidth: Wenn auf high gesetzt, erlaubt dies die Auswahl von Codecs mit hoher Bandbreite, wie z. B. g711 in ihren Varianten ulaw und alaw.

Das Folgende ist ein Beispiel für den Abschnitt [general] der Datei iax.conf.

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX-Clients

Nachdem die allgemeinen Abschnitte abgeschlossen sind, ist es an der Zeit, die IAX-Clients einzurichten.

- [name]: Wenn sich ein SIP-Gerät mit Asterisk verbindet, verwendet es den Benutzernamen-Teil der SIP-URI, um den Peer/Benutzer zu finden.
- type: Konfiguriert die Verbindungsklasse. Optionen sind peer, user und friend. o peer: Asterisk sendet Anrufe an einen Peer. o user: Asterisk empfängt Anrufe von einem Benutzer. o friend: Beides geschieht gleichzeitig.
- host: IP-Adresse oder Hostname. Die häufigste Option ist dynamic, die verwendet wird, wenn sich der Host bei Asterisk registriert.
- secret: Passwort zur Authentifizierung von Peers und Benutzern.

Warnung: Verwenden Sie starke Passwörter mit mindestens 8 Zeichen, alphanumerischen und numerischen Zeichen sowie mindestens einem Symbol. Berichte über gehackte Server sind in den Mailinglisten aufgetaucht, und Brute-Force-Passwort-Cracker für SIP-MD5-Hashes sind für Script-Kiddies verfügbar. Telefonbetrug kostet Verbraucher und Anbieter Tausende von Dollar. Beispiel:

```
[guest]
type=user
context=dummy
callerid=”Guest IAX User”
[6003]
context=from-internal
type=friend
secret=#sup3rs3cr3t#
host=dynamic
context=from-internal
[6004]
context=from-internal
type=friend
secret=#s3cr3ts3cr3t#
host=dynamic
context=from-internal
```

## Konfiguration der SIP-Geräte

Nachdem die Telefone in der Asterisk-Konfigurationsdatei definiert wurden, ist es an der Zeit, das Telefon selbst zu konfigurieren. In diesem Beispiel zeigen wir, wie man ein kostenloses Softphone konfiguriert. Die 1. Auflage verwendete X-Lite von CounterPath; dieses Produkt wurde eingestellt, verwenden Sie also ein beliebiges modernes kostenloses SIP-Softphone (zum Beispiel Zoiper, Linphone oder MicroSIP). Überprüfen Sie das Handbuch Ihres Geräts, um die Parameter Ihres Telefons zu verstehen. Schritt 1: Konfigurieren Sie das Telefon so, dass es die Nebenstelle 6000 verwendet. Führen Sie das Installationsprogramm aus. Öffnen Sie nach der Ausführung die Konto-/SIP-Einstellungen und fügen Sie ein neues SIP-Konto hinzu. Geben Sie die erforderlichen Informationen ein.

![Der SipPulse Softphone-Kontobildschirm — geben Sie den Server (Ihre Asterisk-IP oder Domain), Benutzername, Passwort und Anzeigename ein, dann wählen Sie den Transport (UDP, TCP oder TLS).](../images/softphone/sipphone-account.png){width=35%}

Anzeigename: 6000  Benutzername: 6000  Passwort: #MySecret1#7  Autorisierungs-Benutzername: 6000  Domain: ip_of_your_server. Bestätigen Sie, dass Ihr Telefon registriert ist, indem Sie den Konsolenbefehl `pjsip show endpoints` (oder `pjsip show endpoint 6000` für Details; `pjsip show contacts` zeigt die registrierten AOR-Kontakte) verwenden. Wiederholen Sie die Konfiguration für das Telefon 6001.

![Ein registriertes SipPulse Softphone — der grüne Punkt und die Kontozeile (`1001@softphone.sippulse.com.br`) bestätigen die Registrierung; tätigen Sie einen Anruf über das Tastenfeld oder die Anruf-/Video-Schaltflächen.](../images/softphone/sipphone-registered.png){width=35%}

## Konfiguration der IAX-Geräte

IAX2 ist ein veraltetes Protokoll (siehe das Kapitel *Legacy channels*), und das SipPulse Softphone ist nur SIP-fähig, daher kann es kein IAX-Konto registrieren. Wenn Sie IAX2 testen müssen, verwenden Sie einen Client, der es noch unterstützt (zum Beispiel Zoiper, das historisch IAX anbot). Erstellen Sie ein neues IAX-Konto,

3. Wählen Sie ein neues IAX-Konto. 4. Geben Sie die zugehörigen Optionen für das Telefon 6003 und optional für das 6004 ein. 5. Speichern Sie die Konfiguration und prüfen Sie, ob das Telefon registriert ist, indem Sie iax2 show peers verwenden. Wichtig: Verwenden Sie ein Konto für SIP und ein anderes für IAX. Wenn Sie das System so konfigurieren möchten, dass sowohl IAX als auch SIP gleichzeitig klingeln, zeigen wir Ihnen im Abschnitt Dialplan, wie das geht.

### Konfiguration einer PSTN-Schnittstelle

Um eine Verbindung zum PSTN herzustellen, benötigen Sie eine Schnittstelle für ein Foreign Exchange Office (FXO) und eine Telefonleitung. Sie können auch eine bestehende PBX-Nebenstelle verwenden. Sie können eine Telefonschnittstellenkarte mit einer FXO-Schnittstelle von verschiedenen Herstellern erhalten. In diesem Beispiel zeigen wir Ihnen, wie Sie eine DAHDI-Schnittstellenkarte installieren.

![FXS- und FXO-Ports: Der FXS-Port steuert ein analoges Telefon (liefert Wählton und Klingeln), während der FXO-Port Asterisk mit der Telco-Leitung verbindet.](../images/04-first-pbx-fig02.png)

### Analoge Leitungen mit DAHDI

Sie können eine analoge Karte, die mit DAHDI kompatibel ist, von verschiedenen Herstellern kaufen. X100P war eine der ersten Digium-Karten und wurde bereits eingestellt. Einige Hersteller produzieren immer noch ähnliche Klone. Zusätzlich zum Preis der X100P haben wir mehrere Probleme zwischen diesen Karten und neuen Motherboards festgestellt, verwenden Sie sie also mit Vorsicht. X100P ist meiner Meinung nach keine gute Wahl für eine Produktionsumgebung. Jede Karte, die mit DAHDI kompatibel ist, sollte funktionieren. Dank des Teams der DAHDI-Entwickler haben wir jetzt ein Tool zum Erkennen und Konfigurieren der Schnittstellenkarten fast automatisch. Wenn Sie gerade die DAHDI-Treiber installiert haben, vergessen Sie bitte nicht, make config auszuführen und die Maschine neu zu starten, um sie automatisch zu laden. Sie können die unten stehenden Befehle verwenden, um Ihre Karte zu erkennen und zu konfigurieren. Schritt 1: Um Ihre Hardware zu erkennen, verwenden Sie:

```
dahdi_hardware.
```

Schritt 2: Zur Konfiguration verwenden Sie:

```
dahdi_genconf.
```

Der obige Befehl generiert zwei Dateien /etc/dahdi/system.conf und /etc/asterisk/dahdi-channels.conf. Die Standardparameter für dahdi_genconf sind normalerweise in Ordnung, aber Sie können sie in der Datei /etc/dahdi/genconf_parameters ändern. Standardmäßig fügt es die Leitungen (FXO) in den Kontext from-pstn und die Telefone (FXS) in den Kontext from-internal ein. Schritt 3: Fügen Sie nach dem Ausführen von dahdi_genconf in der letzten Zeile der Datei /etc/asterisk/chan_dahdi.conf die folgende Zeile ein:

```
#include dahdi-channels.conf
```

Schritt 4: Bearbeiten Sie die Datei /etc/dahdi/modules und kommentieren Sie alle ungenutzten Treiber aus. Starten Sie neu, bevor Sie fortfahren, und prüfen Sie, ob die Kanäle erkannt werden, indem Sie verwenden:

```
CLI>dahdi show channels
```

### Verbindung zum PSTN über einen VoIP-Anbieter

Wenn Ihr Budget wirklich begrenzt ist, können Sie einen SIP-Trunk konfigurieren, um eine Verbindung zum PSTN herzustellen. Es ist sicherlich der erschwinglichste Weg, eine Verbindung zum PSTN herzustellen. Weltweit gibt es Tausende von VoIP-Anbietern. Um eine Verbindung zu einem von ihnen herzustellen, benötigen Sie einige Parameter. Parameter, die vom SIP-Anbieter bereitgestellt werden.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

Zwei Parameter sollten von Ihnen bestimmt werden.

- Nebenstelle zum Empfangen von Anrufen – in diesem Fall: 9999
- context: from-sip

In PJSIP wird ein registrierender SIP-Trunk aus derselben Objektfamilie aufgebaut, die für einen Endpoint verwendet wird, plus expliziten `registration` und `identify` Objekten. Das `registration` Objekt sagt Asterisk, dass es sich beim Anbieter registrieren soll, das `identify` Objekt gleicht eingehenden Datenverkehr von der IP des Anbieters mit dem Endpoint ab (PJSIP authentifiziert eingehende INVITEs anhand der Quell-IP), und `outbound_auth` liefert die Anmeldedaten für ausgehende Anrufe und die Registrierung:

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=userpass
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

Um auf diesen Trunk zuzugreifen, verwenden wir den Kanalnamen `PJSIP/siptrunk`. Die `dtmf_mode=rfc4733` Einstellung überträgt DTMF außerhalb des Bandes (RFC 4733 ersetzt das ältere RFC 2833; die Nutzlast ist identisch). Die `identify`/`match` Option akzeptiert IP-Adressen, CIDRs oder Hostnamen, aber Hostnamen werden nur zum Zeitpunkt des Konfigurationsladens aufgelöst. Listen Sie daher bei einem Anbieter mit wechselnden IPs die Signalisierungs-IP(s) explizit auf. Bestätigen Sie die Registrierung mit `pjsip show registrations`.

## Einführung in den Dialplan

Der Dialplan ist wie das Herz von Asterisk. Er definiert, wie Asterisk jeden einzelnen Anruf an die PBX handhabt. Er besteht aus Nebenstellen, die eine Anweisungsliste für Asterisk erstellen, der es folgen soll. Anweisungen werden durch Ziffern ausgelöst, die vom Kanal oder der Anwendung empfangen werden. Um Asterisk erfolgreich zu konfigurieren, ist es entscheidend, den Dialplan zu verstehen. Der größte Teil des Dialplans ist in der Datei extensions.conf im Verzeichnis /etc/asterisk enthalten. Diese Datei verwendet die Grammatik der einfachen Gruppe und hat vier Hauptkonzepte:

- Nebenstellen (Extensions)
- Prioritäten
- Anwendungen
- Kontexte

Lassen Sie uns einen grundlegenden Dialplan erstellen. In nachfolgenden Abschnitten dieses Buches werde ich dem Dialplan ein eigenes Kapitel widmen. Wenn Sie die Beispieldateien installiert haben (make samples), existiert die extensions.conf bereits. Speichern Sie sie unter einem anderen Namen und beginnen Sie mit einer leeren Datei.

## Die Struktur der Datei extensions.conf

Die Datei extensions.conf ist in Abschnitte unterteilt. Der erste ist der Abschnitt [general], gefolgt vom Abschnitt [globals]. Der Anfang jedes Abschnitts beginnt mit seiner Namensdefinition (z. B. [default]) und endet, wenn ein anderer Abschnitt erstellt wird.

### Der Abschnitt [general]

Der Abschnitt general befindet sich ganz oben in der Datei. Bevor Sie mit der Konfiguration des Dialplans beginnen, ist es hilfreich, die allgemeinen Optionen zu kennen, die bestimmte Dialplan-Verhaltensweisen steuern. Diese Optionen sind:

- static und write protect: Wenn static=yes und writeprotect=no, können Sie die CLI verwenden

```
command save dialplan.
```

Warnung: Wenn Sie einen Befehl save dialplan von der CLI ausgeben, verlieren Sie alle Anmerkungen und Kommentare in der Datei.

- autofallthrough: Wenn autofallthrough gesetzt ist und eine Nebenstelle keine Aufgaben mehr hat, beendet sie den Anruf mit BUSY, CONGESTION oder HANGUP, je nachdem, was Asterisk für am wahrscheinlichsten hält. Dies ist der Standard. Wenn autofallthrough nicht gesetzt ist und eine Nebenstelle keine Aufgaben mehr hat, wartet Asterisk darauf, dass eine neue Nebenstelle gewählt wird.
- clearglobalvars: Wenn clearglobalvars gesetzt ist, werden globale Variablen bei einem dialplan reload oder Asterisk reload gelöscht und neu geparst. Wenn clearglobalvars nicht gesetzt ist, bleiben globale Variablen über Neuladevorgänge hinweg bestehen und – selbst wenn sie aus der extensions.conf oder einer ihrer inkludierten Dateien gelöscht werden – bleiben sie auf dem vorherigen Wert gesetzt.
- extenpatternmatchnew: Verwendet einen schnelleren Algorithmus für den Musterabgleich, was bei einer großen Anzahl von Nebenstellen spürbar hilft. Standardmäßig auf no.
- userscontext: Dies ist der Kontext, in dem die Einträge aus der users.conf registriert werden.

### Der Abschnitt [globals]

Im Abschnitt [globals] definieren Sie globale Variablen und deren Anfangswerte. Sie können im Dialplan über ${GLOBAL(variable)} auf die Variable zugreifen. Sie können sogar auf Variablen zugreifen, die in der Linux/Unix-Umgebung definiert sind, indem Sie ${ENV(variable)} verwenden. Globale Variablen unterscheiden nicht zwischen Groß- und Kleinschreibung. Ein paar Beispiele könnten sein:

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

Im folgenden Beispiel können Sie eine globale Variable im Dialplan setzen und testen.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Kontexte

Ein Kontext ist die benannte Partition des Dialplans. Nach den Abschnitten [general] und [globals] ist der Dialplan eine Menge von Kontexten, in denen jeder Kontext mehrere Nebenstellen hat, jede Nebenstelle mehrere Prioritäten hat und jede Priorität eine Anwendung mit mehreren Argumenten aufruft.

![Asterisk-Anruffluss: Jeder Anruf kommt auf einem Kanal (IAX, SIP und andere) als eingehender Anrufzweig an; der Kontext des Kanals – global oder pro Kanal in der Kanalkonfigurationsdatei festgelegt – entscheidet, welcher Kontext in extensions.conf den Anruf verarbeitet, bevor er den ausgehenden Zweig verlässt.](../images/04-first-pbx-fig03.png)

![Anrufverarbeitung: Der `context=`, der für einen Kanal definiert ist (in chan_dahdi.conf oder pjsip.conf), benennt den passenden Kontext in extensions.conf, in dem der Dialplan den Anruf handhabt.](../images/04-first-pbx-fig04.png)

Sie können einen einfachen Dialplan erstellen, um andere Telefone und das PSTN zu erreichen. Asterisk ist jedoch viel leistungsfähiger als das. Unser Ziel ist es, Ihnen mehr Details darüber beizubringen, was im Dialplan möglich ist.

## Nebenstellen (Extensions)

Im Gegensatz zur traditionellen PBX, bei der Nebenstellen mit Telefonen, Schnittstellen, Menüs usw. verknüpft sind, ist eine Nebenstelle in Asterisk eine Liste von Befehlen, die verarbeitet werden, wenn eine bestimmte Nebenstellennummer oder ein Name ausgelöst wird. Die Befehle werden in der Reihenfolge ihrer Priorität verarbeitet.

![Nebenstellen-Syntax: `exten => number(name),{priority|label}[(alias)],application`. Nebenstellen können numerisch, alphanumerisch, numerisch mit Anrufer-ID, ein Muster oder eine Standard-Nebenstelle wie `s` sein; Prioritäten können eine Zahl, `n` (nächste), `s` (gleiche), ein Offset oder ein `hint` sein.](../images/04-first-pbx-fig05.png)

Eine Nebenstelle kann wörtlich, standardmäßig oder speziell sein. Eine Standard-Nebenstelle enthält nur Zahlen oder Namen und die Zeichen * und #; 12#89* ist eine gültige wörtliche Nebenstelle. Namen können ebenfalls für den Nebenstellenabgleich verwendet werden. Nebenstellen unterscheiden zwischen Groß- und Kleinschreibung. Sie können jedoch nicht zwei Nebenstellen mit demselben Namen, aber unterschiedlicher Groß-/Kleinschreibung erstellen. Wenn eine Nebenstelle gewählt wird, wird der Befehl mit der ersten Priorität ausgeführt, gefolgt vom Befehl mit Priorität 2 und so weiter. Dies geschieht, bis der Anruf getrennt wird oder ein Befehl die Zahl eins zurückgibt, was auf einen Fehler hinweist. Was Asterisk tut, wenn die letzte Priorität ausgeführt wird, wird durch den Parameter autofallthrough geregelt. Siehe den Abschnitt [general] in diesem Kapitel. Beispiel:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Oben finden Sie die Liste der Anweisungen, die verarbeitet werden, wenn die Nebenstelle 123 gewählt wird. Die erste Priorität besteht darin, den Kanal zu beantworten (notwendig, wenn sich der Kanal im Klingelzustand befindet: z. B. FXO-Kanäle). Die zweite Priorität besteht darin, eine Audiodatei namens tt-weasels abzuspielen. Die dritte Priorität legt den Kanal auf. Eine weitere Option besteht darin, den Anruf gemäß der Anrufer-ID zu behandeln. Sie können das Zeichen / verwenden, um die zu verarbeitende Anrufer-ID anzugeben. Beispiele:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Dieses Beispiel löst die Nebenstelle 123 aus und führt die folgenden Optionen nur aus, wenn die Anrufer-ID 100 ist. Dies kann auch durch die Verwendung des unten beschriebenen Musters erfolgen:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: ordnet eine Nebenstelle einem Kanal zu. Es wird verwendet, um den Kanalstatus zu überwachen. Es wird in Verbindung mit Präsenz (Presence) verwendet. Das Telefon muss dies unterstützen.

#### Muster

Sie können Muster und Literale im Dialplan verwenden. Muster sind sehr nützlich, um die Größe des Dialplans zu reduzieren. Alle Muster beginnen mit dem Zeichen „_“. Die folgenden Zeichen können verwendet werden, um ein Muster zu definieren. Die Abbildung identifiziert die Muster, die für die Verwendung mit Asterisk verfügbar sind.

![Musterabgleichszeichen: `_` startet ein Muster, `.` entspricht einem oder mehreren Zeichen, `!` entspricht null oder mehr, `[123-7]` entspricht jeder aufgelisteten Ziffer oder jedem Bereich, `X` ist 0-9, `Z` ist 1-9 und `N` ist 2-9 – mit Beispielen, die Büro-Nebenstellenbereiche abbilden.](../images/04-first-pbx-fig06.png)

### Spezielle Nebenstellen

Asterisk verwendet einige Nebenstellennamen als Standard-Nebenstellen.

![Asterisk-Spezial-Nebenstellen: `i` (ungültig), `s` (Start), `h` (Auflegen), `t` (Timeout), `T` (absolutes Timeout), `o` (Operator), `a` (gedrückt `*` in Voicemail), `fax` (Faxerkennung) und `Talk` (verwendet mit BackgroundDetect).](../images/04-first-pbx-fig07.png)

Beschreibung: s: Start. Wird verwendet, um einen Anruf zu behandeln, wenn keine Nummer gewählt wurde. Es ist nützlich für FXO-Trunks und die Menüverarbeitung. t: Timeout. Wird verwendet, wenn Anrufe inaktiv bleiben, nachdem eine Aufforderung abgespielt wurde. Es wird auch verwendet, um eine inaktive Leitung aufzulegen. T: AbsoluteTimeout. Wenn Sie ein Anruflimit mit der Dialplan-Funktion `TIMEOUT(absolute)` festlegen, wird der Anruf an die T-Nebenstelle gesendet, sobald er das definierte Limit überschreitet. h: Hangup. Wird aufgerufen, nachdem der Benutzer den Anruf getrennt hat. i: Invalid. Wird ausgelöst, wenn Sie eine nicht existierende Nebenstelle im Kontext anrufen. Die Verwendung dieser Nebenstellen kann den Inhalt von CDR-Datensätzen beeinflussen – insbesondere das Feld dst, das nicht die gewählte Nummer enthält. o: Operator. Wird verwendet, um zum Operator zu gelangen, wenn der Benutzer während der Voicemail „0“ drückt. Die Verwendung dieser Nebenstellen kann den Inhalt der Abrechnungsdatensätze (CDR) ändern – insbesondere wird das Feld dst nicht die gewählte Nummer haben. Um dieses Problem zu umgehen, sollten Sie die Option g in der Anwendung dial() verwenden und die Funktionen resetcdr(w) und/oder nocdr() in Betracht ziehen.

## Variablen

In der Asterisk PBX können Variablen global, kanalspezifisch und umgebungsspezifisch sein. Sie können die Anwendung NoOP() verwenden, um den Inhalt einer Variablen in der Konsole zu sehen. Sie kann eine globale Variable oder eine kanalspezifische Variable als Anwendungsargumente verwenden. Eine Variable kann wie im folgenden Beispiel referenziert werden, wobei varname der Name der Variablen ist.

```
${varname}
```

Ein Variablenname kann eine alphanumerische Zeichenfolge sein, die mit einem Buchstaben beginnt. Globale Variablennamen unterscheiden nicht zwischen Groß- und Kleinschreibung. Systemvariablen (Asterisk-definiert sind kanaldefiniert) unterscheiden jedoch zwischen Groß- und Kleinschreibung. Daher ist die Variable ${EXTEN} anders als ${exten}.

### Globale Variablen

Globale Variablen können im Abschnitt [global] in der Datei extensions.conf oder unter Verwendung der Anwendung konfiguriert werden:

```
set(Global(variable)=content)
```

### Kanalspezifische Variablen

Kanalspezifische Variablen werden mit der Anwendung set() konfiguriert. Jeder Kanal erhält seinen eigenen Variablenraum. Es gibt keine Möglichkeit von Kollisionen zwischen Variablen verschiedener Kanäle. Eine kanalspezifische Variable wird zerstört, wenn der Kanal aufgelegt wird. Einige der am häufigsten verwendeten Variablen sind:

- ${EXTEN} Gewählte Nebenstelle
- ${CONTEXT} Aktueller Kontext
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Aktuelle Anrufer-ID
- ${PRIORITY} Aktuelle Priorität

Andere kanalspezifische Variablen sind alle in Großbuchstaben. Sie können den Inhalt mehrerer Variablen mit der Anwendung dumpchan() sehen. Unten ist ein einfacher Auszug von Dump-Channel-Variablen.

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
```

Dumpchan-Ausgabe:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

Das Feldlayout oben ist die Asterisk 22 `DumpChan` Ausgabe (ein echter `PJSIP/...` Kanalname, die `CallerIDNum`/`ConnectedLineID` Felder und die `Raw*`/`Transcode`/`BridgeID` Zeilen, die PJSIP-Kanäle belegen). Im Gegensatz zum alten Treiber setzt ein PJSIP-Kanal nicht automatisch `SIPCALLID`/`SIPUSERAGENT` Kanalvariablen; die entsprechenden SIP-Details werden bei Bedarf mit den Dialplan-Funktionen `PJSIP_HEADER()` und `CHANNEL()` gelesen – zum Beispiel `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` und `${CHANNEL(rtp,dest)}` für die entfernte RTP-Adresse.

### Umgebungsspezifische Variablen

Umgebungsspezifische Variablen können verwendet werden, um auf Variablen zuzugreifen, die im Betriebssystem definiert sind. Sie können umgebungsspezifische Variablen mit der Funktion ENV() setzen. Zum Beispiel:

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### Anwendungsspezifische Variablen

Einige Anwendungen verwenden Variablen für die Dateneingabe und -ausgabe. Sie können Variablen setzen, bevor Sie die Anwendung aufrufen, oder die Variable nach der Ausführung der Anwendung abrufen. Zum Beispiel: Die Dial-Anwendung gibt die folgenden Variablen zurück:

- ${DIALEDTIME} -> Dies ist die Zeit vom Wählen eines Kanals bis zur Trennung.
- ${ANSWEREDTIME} -> Dies ist die Zeitdauer für den eigentlichen Anruf.
- ${DIALSTATUS} Dies ist der Status des Anrufs: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Fehlermeldung für den Anruf.

## Ausdrücke

Ausdrücke können im Dialplan sehr nützlich sein. Sie werden verwendet, um Zeichenfolgen zu manipulieren und mathematische sowie logische Operationen durchzuführen.

![Übersicht der Asterisk-Ausdrücke — `$[expression1 operator expression2]` — Gruppierung der mathematischen, logischen, Vergleichs-, regulären Ausdrucks- und bedingten Operatoren, die im Dialplan verfügbar sind.](../images/04-first-pbx-fig08.png)

Die Ausdruckssyntax ist wie folgt definiert:

```
$[expression1 operator expression2]
```

Nehmen wir an, wir haben eine Variable namens „I“ und wir möchten 100 zur Variablen addieren:

```
$[${I}+100]
```

Wenn Asterisk einen Ausdruck im Dialplan findet, ersetzt es den gesamten Ausdruck durch den resultierenden Wert.

### Operatoren

Die folgenden Operatoren können verwendet werden, um Ausdrücke zu erstellen. Es ist wichtig, die Operatorrangfolge zu beachten. 1. Klammern „()“ 2. Unäre Operatoren „! -“ 3. Regulärer Ausdruck „: =~ 4. Multiplikative Operatoren „* / %“ 5. Additive Operatoren „+ -“ 6. Vergleichsoperatoren 7. Logische Operatoren 8. Bedingte Operatoren

#### Mathematische Operatoren

- Addition (+)
- Subtraktion (-)
- Multiplikation (*)
- Division (/)
- Modulo (%)

#### Logische Operatoren

- Logisches „UND“ (&)
- Logisches „ODER“ (|)
- Logische unäre Komplementierung (!)

#### Operatoren für reguläre Ausdrücke

- Abgleich mit regulärem Ausdruck (:)
- Exakter Abgleich mit regulärem Ausdruck (=~)

Ein regulärer Ausdruck ist eine spezielle Textzeichenfolge, die verwendet wird, um ein Suchmuster zu beschreiben. Sie können sich reguläre Ausdrücke als Platzhalter vorstellen. Reguläre Ausdrücke werden verwendet, um eine Zeichenfolge mit einem Muster abzugleichen, um die Übereinstimmung zu prüfen. Wenn der Abgleich erfolgreich ist und der reguläre Ausdruck mindestens eine Übereinstimmung enthält, wird die erste Übereinstimmung zurückgegeben; andernfalls ist das Ergebnis die Anzahl der übereinstimmenden Zeichen.

#### Vergleichsoperatoren

Das Ergebnis eines Vergleichs ist 1, wenn die Beziehung wahr ist, oder 0, wenn sie falsch ist.

- = gleich
- != ungleich
- < kleiner als
- > größer als
- <= kleiner oder gleich
- >= größer oder gleich

### LAB. Bewerten Sie die folgenden Ausdrücke:

Setzen Sie diese Ausdrücke in Ihren Dialplan und verwenden Sie die Anwendung NoOP(), um die Ausdrücke zu bewerten. Wählen Sie 9002 und untersuchen Sie die Ergebnisse in der Asterisk-Konsole. Verwenden Sie verbose 15, um die Ergebnisse anzuzeigen.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Funktionen

Einige Anwendungen wurden durch Funktionen ersetzt, die die Verarbeitung von Variablen auf eine fortgeschrittenere Weise ermöglichen als Ausdrücke allein. Sie können die vollständige Liste der Funktionen sehen, indem Sie den folgenden Konsolenbefehl ausgeben:

```
CLI>core show functions
```

Zeichenfolgenlänge: ${LEN(string)} gibt die Länge der Zeichenfolge zurück

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Bei der ersten Operation zeigt das System 5 als Ergebnis (die Anzahl der Buchstaben im Wort „fruit“). Die zweite gibt die Zahl 4 zurück (die Anzahl der Buchstaben im Wort „pear“). Teilzeichenfolgen (Substrings): Gibt die Teilzeichenfolge zurück, beginnend an der Position, die durch den Parameter „offset“ definiert ist, mit der Zeichenfolgenlänge, die im Parameter „length“ definiert ist. Wenn der Offset negativ ist, beginnt er von rechts nach links, beginnend am Ende der Zeichenfolge. Wenn die Länge weggelassen oder negativ ist, wird die gesamte Zeichenfolge ab dem Offset genommen.

```
${string:offset:length }
```

Beispiel #1: Mehrere Teilzeichenfolgen

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Beispiel #2: Nehmen Sie die Vorwahl aus den ersten drei Ziffern.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Beispiel #3: Nimmt alle Ziffern aus der Variablen ${EXTEN}, außer der Vorwahl.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Zeichenfolgenverkettung

Um zwei Zeichenfolgen zu verketten, schreiben Sie sie einfach zusammen.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Anwendungen

Um einen Dialplan zu erstellen, müssen wir das Konzept der Anwendungen verstehen. Sie verwenden Anwendungen, um den Kanal im Dialplan zu handhaben. Anwendungen sind in verschiedenen Modulen implementiert. Verfügbare Anwendungen hängen von den Modulen ab. Sie können alle Asterisk-Anwendungen mit dem Konsolenbefehl anzeigen:

```
CLI>core show applications
```

Alternativ können Sie Details einer bestimmten Anwendung mit dem folgenden Beispiel anzeigen:

```
CLI>core show application dial
```

Um einen einfachen Dialplan zu erstellen, müssen Sie einige Anwendungen kennen. Wir werden später im Buch fortgeschrittenere Beispiele besprechen.

![Die Handvoll Anwendungen, die zum Erstellen eines einfachen Dialplans benötigt werden: Answer (einen Kanal beantworten), Dial (einen anderen Kanal anrufen), Hangup (einen Kanal auflegen), Playback (eine Audiodatei abspielen) und Goto (zu einer Priorität, Nebenstelle oder einem Kontext springen).](../images/04-first-pbx-fig09.png)

Wir werden diese Anwendungen (oben) verwenden, um einen einfachen Dialplan für zwei grundlegende PBXs zu erstellen.

### Answer()

[Synopsis] Beantwortet einen Kanal, wenn er klingelt [Beschreibung] Answer([delay]): Wenn der Anruf nicht beantwortet wurde, wird die Anwendung ihn beantworten. Andernfalls hat es keine Auswirkungen auf den Anruf. Wenn eine Verzögerung angegeben ist, wartet Asterisk die in „delay“ angegebene Anzahl von Millisekunden, bevor der Anruf beantwortet wird.

### Dial()

Die folgende Beschreibung kann durch die Eingabe von show application dial im Dialplan erhalten werden. Zur einfachen Suche ist sie unten reproduziert. Die Syntax für die Dial-Anwendung ist ebenfalls unten dargestellt:

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

Diese Anwendung tätigt Anrufe an einen oder mehrere angegebene Kanäle. Sobald einer der angeforderten Kanäle antwortet, wird der ursprüngliche Kanal beantwortet – falls er nicht bereits beantwortet wurde. Diese beiden Kanäle sind dann in einem gebrückten Anruf aktiv. Alle anderen angeforderten Kanäle werden dann aufgelegt. Sofern kein Timeout angegeben ist, wartet die Dial-Anwendung unbegrenzt, bis einer der angerufenen Kanäle antwortet, der Benutzer auflegt oder alle angerufenen Kanäle besetzt oder nicht verfügbar sind. Die Ausführung des Dialplans wird fortgesetzt, wenn keine angeforderten Kanäle angerufen werden können oder wenn das Timeout abläuft. Diese Anwendung setzt nach Abschluss die folgenden Kanalvariablen:

- DIALEDTIME - Dies ist die Zeit vom Wählen eines Kanals bis zur Trennung.
- ANSWEREDTIME - Dies ist die Zeitdauer für einen tatsächlichen Anruf.
- DIALSTATUS - Dies ist der Status des Anrufs: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Für die Datenschutz- und Screening-Modi wird die Variable DIALSTATUS auf DONTCALL gesetzt, wenn die angerufene Partei sich entscheidet, die anrufende Partei an das 'Go Away'-Skript zu senden. Die Variable DIALSTATUS wird auf TORTURE gesetzt, wenn die angerufene Partei den Anrufer an das 'Torture'-Skript senden möchte. Diese Anwendung meldet einen normalen Abschluss, wenn der ursprüngliche Kanal auflegt oder wenn der Anruf gebrückt ist und eine der Parteien in der Brücke den Anruf beendet. Die optionale URL wird an die angerufene Partei gesendet, wenn der Kanal dies unterstützt. Wenn die Variable OUTBOUND_GROUP gesetzt ist, werden alle von dieser Anwendung erstellten Peer-Kanäle in diese Gruppe aufgenommen (wie in

```
Set(GROUP()=...).
```

Die folgende Tabelle fasst einige der am häufigsten verwendeten Optionen für die Anwendung Dial zusammen. Für die vollständige Liste verwenden Sie den Konsolenbefehl `core show application Dial`. In Asterisk 22 sind diese Optionen durch Kommas vom Kanal und Timeout getrennt – zum Beispiel `Dial(PJSIP/2000,20,tTm)`.

| Option | Beschreibung |
|--------|-------------|
| `A(x)` | Spielt eine Ankündigung für die angerufene Partei ab, wobei `x` als Datei verwendet wird. |
| `C` | Setzt den CDR für diesen Anruf zurück. |
| `d` | Erlaubt dem anrufenden Benutzer, eine 1-stellige Nebenstelle zu wählen, während er darauf wartet, dass der Anruf beantwortet wird. Beendet zu dieser Nebenstelle, wenn sie im aktuellen Kontext existiert, oder zu dem Kontext, der in der Variablen `EXITCONTEXT` definiert ist, falls vorhanden. |
| `D([called][:calling])` | Sendet die angegebenen DTMF-Zeichenfolgen, nachdem die angerufene Partei geantwortet hat, aber bevor der Anruf gebrückt wird. Die Zeichenfolge `called` wird an die angerufene Partei gesendet und die Zeichenfolge `calling` an die anrufende Partei. Jeder Parameter kann allein verwendet werden. |
| `f` | Erzwingt, dass die Anrufer-ID des anrufenden Kanals auf die Nebenstelle gesetzt wird, die dem Kanal über einen Dialplan `hint` zugeordnet ist. Nützlich, wenn das PSTN keine beliebige Anrufer-ID erlaubt. |
| `g` | Fährt mit der Dialplan-Ausführung an der aktuellen Nebenstelle fort, wenn der Zielkanal auflegt. |
| `G(context^exten^pri)` | Wenn der Anruf beantwortet wird, überträgt er die anrufende Partei an die angegebene Priorität und die angerufene Partei an Priorität+1. Optional kann eine Nebenstelle (oder Nebenstelle und Kontext) angegeben werden; andernfalls wird die aktuelle Nebenstelle verwendet. |
| `h` | Erlaubt der angerufenen Partei aufzulegen, indem sie die DTMF-Ziffer `*` sendet. |
| `H` | Erlaubt der anrufenden Partei aufzulegen, indem sie die DTMF-Ziffer `*` sendet. |
| `L(x[:y][:z])` | Begrenzt den Anruf auf `x` ms, spielt eine Warnung ab, wenn noch `y` ms übrig sind, und wiederholt die Warnung alle `z` ms. Siehe die Variablen `LIMIT_*` unten. |
| `m([class])` | Bietet der anrufenden Partei Wartemusik (Music on Hold), bis der angeforderte Kanal antwortet. Eine spezifische MusicOnHold-Klasse kann angegeben werden. |
| `r` | Zeigt der anrufenden Partei das Klingeln an und leitet kein Audio weiter, bis der angerufene Kanal antwortet. |
| `S(x)` | Legt den Anruf `x` Sekunden nach der Antwort der angerufenen Partei auf. |
| `t` | Erlaubt der angerufenen Partei, die anrufende Partei zu übertragen, indem sie die in `features.conf` definierte DTMF-Sequenz sendet. |
| `T` | Erlaubt der anrufenden Partei, die angerufene Partei zu übertragen, indem sie die in `features.conf` definierte DTMF-Sequenz sendet. |
| `w` | Erlaubt der angerufenen Partei, die One-Touch-Aufnahme zu aktivieren, indem sie die in `features.conf` definierte DTMF-Sequenz sendet. |
| `W` | Erlaubt der anrufenden Partei, die One-Touch-Aufnahme zu aktivieren, indem sie die in `features.conf` definierte DTMF-Sequenz sendet. |
| `k` | Erlaubt der angerufenen Partei, den Anruf zu parken, indem sie die für das Anrufparken in `features.conf` definierte DTMF-Sequenz sendet. |
| `K` | Erlaubt der anrufenden Partei, den Anruf zu parken, indem sie die für das Anrufparken in `features.conf` definierte DTMF-Sequenz sendet. |

Die Option `L(x[:y][:z])` kann mit den folgenden speziellen Variablen abgestimmt werden:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (Standard `yes`): spielt Töne für den Anrufer ab.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: spielt Töne für die angerufene Partei ab.
- `LIMIT_TIMEOUT_FILE` — Datei, die abgespielt werden soll, wenn die Zeit abgelaufen ist.
- `LIMIT_CONNECT_FILE` — Datei, die abgespielt werden soll, wenn der Anruf beginnt.
- `LIMIT_WARNING_FILE` — Datei, die als Warnung abgespielt werden soll, wenn `y` definiert ist. Standardmäßig wird die verbleibende Zeit angesagt.

Beispiel:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

Im obigen Beispiel wählt die Anwendung den entsprechenden PJSIP-Kanal. Sowohl Anrufer als auch Angerufener könnten den Anruf übertragen (Tt). Wartemusik ist anstelle des Freizeichens zu hören. Wenn innerhalb von 20 Sekunden niemand antwortet, geht die Nebenstelle zur nächsten Priorität über.

### Hangup()

Legt den anrufenden Kanal auf [Beschreibung] Hangup([causecode]): Diese Anwendung legt den anrufenden Kanal auf. Wenn ein Ursachencode angegeben ist, wird die Auflegeursache des Kanals auf den angegebenen Wert gesetzt.

### Goto()

Springt zu einer bestimmten Priorität, Nebenstelle oder einem Kontext [Beschreibung] Goto([[context|]extension|]priority): Diese Anwendung bewirkt, dass der anrufende Kanal die Dialplan-Ausführung an der angegebenen Priorität fortsetzt. Wenn keine spezifische Nebenstelle (oder Nebenstelle und Kontext) angegeben ist, springt diese Anwendung zur angegebenen Priorität der aktuellen Nebenstelle. Wenn der Versuch, an eine andere Stelle im Dialplan zu springen, nicht erfolgreich ist, fährt der Kanal mit der nächsten Priorität der aktuellen Nebenstelle fort.

## Aufbau eines Dialplans

Um einen einfachen Dialplan zu erstellen, müssen Sie alle eingehenden und ausgehenden Anrufe behandeln, indem Sie Kontexte und Nebenstellen erstellen. In diesem Abschnitt zeigen wir Ihnen, wie Sie die gebräuchlichsten Nebenstellen erstellen.

### Wählen zwischen Nebenstellen

Um das Wählen zwischen Nebenstellen zu ermöglichen, könnten wir die Kanalvariable ${EXTEN} verwenden, die sich auf die gewählte Nebenstelle bezieht. Wenn der Nebenstellenbereich beispielsweise zwischen 4000 und 4999 liegt und alle Nebenstellen SIP verwenden, könnten wir den folgenden Befehl annehmen:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Wählen zu einem externen Ziel

Um ein externes Ziel zu wählen, könnten Sie der gewählten Nummer eine Route voranstellen. In Nordamerika ist es üblich, 9 gefolgt von der extern zu wählenden Nummer zu verwenden. Wenn Sie einen analogen oder digitalen Kanal zum PSTN verwenden, sollte der Befehl wie folgt aussehen: Wenn Sie den SIP-Trunk anstelle von DAHDI verwenden möchten, verwenden Sie den Kanal `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

Die obige Zeile erlaubt es Ihnen, 9 und die gewünschte Nummer zu wählen. Im gegebenen Beispiel verwenden Sie den ersten DAHDI-Kanal (DAHDI/1). Wenn Sie mehrere Leitungen haben und diese besetzt ist, wird der Anruf nicht abgeschlossen. Sie könnten jedoch die folgende Zeile verwenden, um automatisch den ersten verfügbaren DAHDI-Kanal auszuwählen. Optional können Sie den SIP-Trunk anstelle von DAHDI verwenden. In der PJSIP-Form `Dial(PJSIP/number@siptrunk,...)` ist die gewählte Nummer der Benutzerteil und `siptrunk` ist der oben konfigurierte Endpoint.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

Der Parameter „g1“ sucht nach dem ersten verfügbaren Kanal in der Gruppe, was die Nutzung aller Kanäle ermöglicht. Mit der folgenden Zeile könnten Sie eine Ferngesprächsnummer wählen.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 9 wählen, um eine PSTN-Leitung zu erhalten

Wenn Sie keine Einschränkungen für externe Anrufe haben, können Sie vereinfachen und Folgendes verwenden:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Empfangen eines Anrufs in der Operator-Nebenstelle

Im folgenden Beispiel ist die Operator-Nebenstelle 4000. Die PSTN-Leitung ist mit einer FXO-Schnittstelle verbunden. In der Datei chan_dahdi.conf ist der angegebene Kontext from-pstn. Jeder Anruf, der vom PSTN kommt, wird an den Kontext from-pstn im Dialplan weitergeleitet. Diese Leitung hat kein Direct Inward Dialing (DID); daher müssen wir den Anruf über die „s“-Nebenstelle empfangen. Wenn Sie vom SIP-Trunk empfangen, verwenden Sie den Kontext [from-sip].

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### Empfangen eines Anrufs mit Direct Inward Dialing (DID)

Wenn Sie eine digitale Leitung haben, empfangen Sie die gewählte Nebenstelle. In diesem Fall müssen Sie den Anruf nicht an den Operator weiterleiten; stattdessen können Sie den Anruf direkt an das Ziel weiterleiten. Angenommen, Ihr DID-Bereich reicht von 3028550 bis 3028599 und die letzten vier Nummern werden in der DID übergeben. Die Konfiguration würde wie im folgenden Beispiel aussehen:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Gleichzeitiges Abspielen mehrerer Nebenstellen

Sie können Asterisk so einstellen, dass eine Nebenstelle gewählt wird und, falls sie nicht beantwortet wird, mehrere andere Nebenstellen gleichzeitig gewählt werden, wie im folgenden Beispiel angegeben:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

In diesem Beispiel wird, wenn jemand den Operator wählt, zuerst der Kanal DAHDI/1 versucht. Wenn nach 15 Sekunden (Timeout) niemand antwortet, klingeln die Kanäle DAHDI/1, DAHDI/2 und DAHDI/3 gleichzeitig für weitere 15 Sekunden.

### Routing nach Anrufer-ID

In diesem Beispiel könnten Sie je nach Anrufer-ID unterschiedliche Behandlungen vornehmen, was für Anruf-Spammer nützlich sein könnte. Zum Beispiel:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In diesem Beispiel haben wir eine spezielle Regel hinzugefügt, dass, wenn die Anrufer-ID 4832518888 ist, Sie eine Nachricht aus der zuvor aufgenommenen Datei „I-have-moved-to-china“ abspielen. Andere Anrufe werden wie gewohnt akzeptiert.

### Verwendung von Variablen im Dialplan

Asterisk kann globale und Kanalvariablen im Dialplan als Argumente für bestimmte Anwendungen verwenden. Betrachten Sie die folgenden Beispiele:

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

Die Verwendung von Variablen erleichtert zukünftige Änderungen. Wenn Sie die Variable ändern, werden alle Referenzen sofort geändert.

### Aufnehmen einer Ankündigung

In einigen der Optionen, die später in diesem Abschnitt besprochen werden, verwenden wir aufgezeichnete Ansagen. Hier zeigen wir Ihnen einen einfachen Weg, sie aufzunehmen. Wir verwenden die Anwendung Record(), um die Ankündigung mit dem eigenen Telefon zu speichern.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Diese Anweisungen ermöglichen es Ihnen, jede Nachricht von einem Softphone aufzunehmen. Beispiel: Wählen von recordmenu vom Softphone. Die Anweisungen rufen die Aufnahme mit der Variablen ${EXTEN:6} ohne die ersten sechs Buchstaben auf. Mit anderen Worten, die Anweisung entspricht record(menu:gsm). Alles, was Sie tun müssen, ist record + name_der_aufzunehmenden_datei zu wählen, # zu drücken, um die Aufnahme zu beenden, und zu warten, bis Sie die Aufnahme hören.

### Empfangen der Anrufe in einer digitalen Rezeption

Nachdem wir nun einige einfache Beispiele haben, erweitern wir unser Wissen über die Anwendungen background() und goto(). Der Schlüssel für interaktive Systeme in Asterisk ist die Anwendung background(), die es Ihnen ermöglicht, eine Audiodatei auszuführen, die, wenn der Anrufer eine Taste drückt, unterbrochen wird, um den Anruf an die gewählte Nebenstelle zu senden. Syntax der Anwendung background():

```
exten=>extension, priority, background(filename)
```

Eine weitere sehr nützliche Anwendung ist goto(). Wie der Name schon sagt, springt sie zum angegebenen Kontext, zur Nebenstelle und zur Priorität. Syntax der Anwendung goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Gültige Formate für den Befehl goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

Im folgenden Beispiel erstellen wir eine digitale Rezeption. Es ist sehr einfach, die Datei extensions.conf zu bearbeiten und die folgenden Nebenstellen zu konfigurieren:

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

Die SIP-Nebenstellen verwenden `PJSIP/` und die IAX-Nebenstellen verwenden `IAX2/` – beide Treiber werden in Asterisk 22 mitgeliefert, obwohl `chan_iax2` jetzt als veraltet gilt und SIP/PJSIP bevorzugt wird.

Nehmen Sie in der Datei menu1.gsm die Nachricht „drücken Sie die Nebenstelle oder warten Sie auf den Operator“ auf. Wenn der Benutzer die Nummer 6000 wählt, wird er an die Nebenstelle 6000 gesendet. An diesem Punkt sollten Sie ein klares Verständnis für die Verwendung mehrerer Anwendungen haben, einschließlich answer(), background(), goto(), hangup() und playback(). Wenn Sie kein klares Verständnis haben, lesen Sie dieses Kapitel bitte erneut, bis Sie sich mit dem Inhalt wohl fühlen. Sie werden die Anwendung background sehr oft verwenden. Sobald Sie die Grundlagen von Nebenstellen, Prioritäten und Anwendungen verstehen, wird es einfach sein, einen einfachen Dialplan zu erstellen. Diese Konzepte werden später im Buch eingehender untersucht, und Sie werden sehen, dass der Dialplan immer leistungsfähiger wird.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Konfigurationsdateien im Verzeichnis /etc/asterisk gespeichert sind. Um Asterisk zu verwenden, ist es zunächst erforderlich, die Kanäle (z. B. pjsip, dahdi, iax) zu konfigurieren. Es gibt drei verschiedene Grammatiken für Konfigurationsdateien: einfache Gruppe, Objektvererbung und komplexe Entität. Der Dialplan wird in der Datei extensions.conf erstellt und ist eine Menge von Kontexten und Nebenstellen. Im Dialplan löst jede Nebenstelle eine Anwendung aus. Sie haben gelernt, die Anwendungen playback, background, dial, goto, hangup und answer zu verwenden.

## Quiz

1. Die Kanalkonfigurationsdateien sind (wählen Sie alle zutreffenden aus):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. In Asterisk 22 wird der einzelne `chan_sip` Peer `[6001]` (`type=friend`/`host=dynamic`) in `pjsip.conf` durch welche Menge zusammengehöriger Objekte ersetzt?
   - A. Ein `type=peer` und ein `type=user`
   - B. Ein `type=endpoint`, ein `type=auth` und ein `type=aor`
   - C. Ein einzelnes `type=friend`
   - D. Ein `type=transport` und ein `type=global`
3. Das Definieren eines Kontextes in der Kanalkonfigurationsdatei ist wichtig, weil es den eingehenden Kontext für Anrufe von diesem Kanal festlegt – ein Anruf vom Kanal wird im passenden Kontext in `extensions.conf` verarbeitet.
   - A. Wahr
   - B. Falsch
4. Die Hauptunterschiede zwischen den Anwendungen `Playback()` und `Background()` sind (wählen Sie zwei):
   - A. Playback spielt eine Aufforderung ab, wartet aber nicht auf Ziffern.
   - B. Background spielt eine Aufforderung ab, wartet aber nicht auf Ziffern.
   - C. Background spielt eine Nachricht ab und wartet darauf, dass Ziffern gedrückt werden.
   - D. Playback spielt eine Nachricht ab und wartet darauf, dass Ziffern gedrückt werden.
5. Wenn ein Anruf über eine Telefonschnittstellenkarte (FXO) ohne DID in Asterisk eingeht, wird er in der speziellen Nebenstelle behandelt:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Gültige Formate für die Anwendung `Goto()` sind (wählen Sie drei):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. Das Muster `_7[1-5]XX` entspricht (wählen Sie alle zutreffenden aus):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. Was bewirkt die Option `m` in `Dial(PJSIP/${EXTEN},20,tTm)`?
   - A. Begrenzt den Anruf auf eine maximale Dauer.
   - B. Bietet dem Anrufer Wartemusik anstelle des Freizeichens, bis der Kanal antwortet.
   - C. Sendet DTMF-Ziffern, nachdem die angerufene Partei geantwortet hat.
   - D. Erzwingt die Anrufer-ID mithilfe eines Dialplan-Hinweises.
9. In der Grammatik der Optionsvererbung, die von `chan_dahdi.conf` verwendet wird, tun Sie:
   - A. Definieren Sie das Objekt in einer einzigen Zeile.
   - B. Definieren Sie zuerst Optionen und deklarieren Sie die Objekte unter den definierten Optionen.
   - C. Definieren Sie einen separaten Kontext für jedes Objekt.
10. Prioritäten in einer Nebenstelle müssen fortlaufend nummeriert sein (1, 2, 3, …) und können nicht `n` verwenden.
    - A. Wahr
    - B. Falsch

**Antworten:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
