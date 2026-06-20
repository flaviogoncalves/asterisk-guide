# Building your first PBX with PJSIP

In diesem Kapitel lernen Sie, wie Sie eine grundlegende Asterisk‑PBX‑Konfiguration durchführen. Das Hauptziel ist, die PBX zum ersten Mal laufen zu sehen, zwischen Extensions wählen zu können, eine abgespielte Nachricht zu wählen und zu einem einzelnen analogen oder SIP‑Trunk zu wählen. Die Idee dieses Kapitels ist, sicherzustellen, dass Ihr Asterisk so schnell wie möglich einsatzbereit ist. Nach Abschluss der Arbeiten in diesem Kapitel verfügen Sie über das nötige Grundlagenwissen, um sich auf die folgenden Kapitel vorzubereiten, in denen wir tiefer in die Konfigurationsdetails eintauchen.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Konfigurationsdateien zu verstehen und zu bearbeiten;
- Softphones auf Basis von SIP zu installieren;
- Einen SIP‑Trunk zu installieren und zu konfigurieren;
- Eine analoge Verbindung zu installieren und zu konfigurieren;
- Zwischen Nebenstellen zu wählen;
- Zwischen Telefonen und externen Zielen zu wählen; und
- Einen automatischen Ansprechpartner zu konfigurieren.

## Understanding the configuration files

Asterisk wird durch Text‑Konfigurationsdateien gesteuert, die sich in /etc/asterisk befinden. Das Dateiformat ähnelt den Windows‑“.ini”‑Dateien. Ein Semikolon wird als Kommentarzeichen verwendet, die Zeichen “=” und “=>” sind gleichwertig, und Leerzeichen werden ignoriert.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpretiert “=” und “=>” auf dieselbe Weise. Unterschiede in der Syntax werden genutzt, um zwischen Objekten und Variablen zu unterscheiden. Verwenden Sie “=”, wenn Sie eine Variable deklarieren möchten, und “=>”, um ein Objekt zu bezeichnen. Die Syntax ist in allen Dateien gleich, jedoch werden drei Arten von Grammatik verwendet, wie im Folgenden erläutert.

## Grammars

| Grammar | How the object is created | Conf. file | Example |
|---------|---------------------------|------------|---------|
| Simple Group | All in the same line | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Options are defined first, the object inherits the options | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Each entity receives a context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

The simple group format used in `extensions.conf` and `voicemail.conf` is the most basic grammar. Each object is declared with options in the same line. Example:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

In this example, object 1 is created with options op1, op2, and op3 while object 2 is created with options op1, op2, and op3.

### Object options inheritance grammar

This format is used by the files chan_dahdi.conf and agents.conf, where numerous options are available, and most interfaces and objects share the same options. Typically, one or more sections have objects and channels declarations. Options to the object are declared above the object and can be changed to another object. Although this concept is hard to understand, it is very easy to use. Example:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

The first two lines configure the value of the options op1 and op2 to “bas” and “adv”, respectively. When object 1 is instanced, it is created using option 1 as “bas” and option 2 as “adv”. After defining object 1, we change option 1 to “int”. Next, we create object 2 with option 1 as “int” and option 2 as “adv”.

### Complex entity object

This format is used by pjsip.conf, iax.conf, and other configuration files in which numerous entities with many options exist. Typically, this format does not share a large volume of common configurations. Each entity receives a context. Sometimes reserved contexts exist, like [general] for global configurations. Options are declared in the context declarations. Example:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

The entity [entity1] has values “value1” and “value2” for options op1 and op2, respectively. The entity [entity2] has values “value3” and “value4” for options op1 and op2.

## Optionen zum Aufbau eines LABs für Asterisk

Um eine PBX zu konfigurieren, benötigen Sie einige grundlegende Hardware. Sie ist weder schwer noch teuer, aber es gibt einige Optionen, die berücksichtigt werden sollten. Alles, was Sie benötigen, sind zwei Telefone und eine Anbindung an das öffentliche Netzwerk. Beim Erstellen Ihres Labs sind verschiedene Optionen und Kombinationen möglich, die wir im Folgenden besprechen.

### Option 1: Komplettes LAB

Mit dem kompletten LAB ist es möglich, alle verfügbaren Szenarien zu testen und Lösungen wie ATA, IP‑Telefone und Softphones zu vergleichen. Sie können zudem etwas über analoge und SIP‑Trunks lernen. Sie benötigen:

- Einen SIP‑analog‑Telefon‑Adapter (ATA)
- Ein IP‑Telefon
- Einen dedizierten Server für Asterisk
- Einen Arbeitsplatz mit einem Softphone
- Eine analoge Schnittstellenkarte mit mindestens zwei Schnittstellen (1 FXO und 1 FXS)
- Ein Konto bei einem VoIP‑Provider

### Option 2: Economy LAB

Beim Economy LAB vereinfachen wir es ein wenig. Wir verwenden das ATA, das in der Regel günstiger ist als das IP‑Telefon, und eine einzelne FXO‑Karte, die wirklich preiswert ist. Wir können keine analogen Telefone direkt am Server anschließen, aber das kommt in der Praxis selten vor. Sie benötigen:

- Einen SIP‑analog‑Telefon‑Adapter (ATA)
- Einen dedizierten Server für Asterisk
- Einen Arbeitsplatz für das Softphone
- Eine analoge Schnittstellenkarte mit 1 FXO
- Ein Konto bei einem VoIP‑Provider

### Option 3: Super‑Economy‑Lab

Das dritte LAB nutzt einen virtualisierten Server im eigenen Notebook des Studenten. Das Problem bei diesem Modell sind die Konflikte, die durch den UDP‑Port entstehen. Manchmal versuchen sowohl der Asterisk‑Server als auch das Softphone, denselben Port zu nutzen, wodurch Asterisk daran gehindert wird, den Adress‑Port zu binden. Ein weiteres Problem ist die Gesprächsqualität; virtuelle Umgebungen sind für Echtzeitanwendungen wie Asterisk nicht geeignet. Verwenden Sie ein kostenloses Softphone für Server und Arbeitsplatz und eine Trunk‑Verbindung zu einem SIP‑Provider. Sie benötigen:

- Einen Laptop, auf dem ein Softphone läuft
- Eine virtuelle Maschine (VirtualBox, VMware oder Ähnliches), um Asterisk zu installieren
- Ein Konto bei einem VoIP‑Provider

## Installationsablauf

Um Ihnen das Verständnis des Installationsablaufs zu erleichtern, haben wir die notwendigen Schritte zum Installieren und Konfigurieren von Asterisk zusammengestellt.

![Referenz‑Laboraufbau: SIP/IAX‑Softphones, ein IP‑Telefon und analoge Adapter als Nebenstellen (1), der Asterisk‑Server mit ETH0/FXO/FXS‑Schnittstellen (3) und die Trunks zur PSTN über einen VoIP‑Provider oder eine Breitbandverbindung (2).](../images/04-first-pbx-fig01.png)

1. Konfiguration von Nebenstellen
   - a. SIP‑Nebenstellen (ATA, Softphone, IP‑Telefon)
   - b. IAX‑Nebenstellen
   - c. FXS‑Nebenstellen
2. Konfiguration von Trunks
   - a. Konfiguration eines SIP‑Trunks
   - b. Konfiguration eines FXO‑Trunks
3. Aufbau eines einfachen Dialplans
   - a. Wählen zwischen Nebenstellen
   - b. Wählen externer Ziele
   - c. Anrufannahme in der Operator‑Nebenstelle
   - d. Anrufannahme in einer automatischen Telefonzentrale

## Configuration of the extensions

The extensions are SIP, IAX, or analog phones connected to an FXS port. To configure an extension, you should edit the configuration file related to the channel (pjsip.conf, iax.conf, chan_dahdi.conf)

### SIP extensions

On Asterisk 22, PJSIP (the `res_pjsip` stack, configured in `/etc/asterisk/pjsip.conf`) is the SIP channel driver. It supports multiple transports per endpoint, is actively maintained, and is the only SIP driver shipped with the platform. (The original `chan_sip` driver was removed in Asterisk 21 — see the *Legacy channels* chapter if you need to migrate an old configuration.)

The idea here is to configure a simple PBX. (Subsequent chapters provide an entire SIP/PJSIP session with all the details.) PJSIP is configured in `/etc/asterisk/pjsip.conf` and holds all the parameters related to SIP phones and VoIP providers. SIP clients have to be configured before you can make and receive calls.

#### The transport

In PJSIP, the listener configuration (bind address, port, protocol) lives in a `transport` object. Asterisk has built-in protection against username guessing — it always returns an identical authentication challenge for unknown and known users, and repeated unidentified requests from one IP are rate-limited via the `[global]` options `unidentified_request_count`/`unidentified_request_period`. The main options of a transport are:

- protocol: The transport protocol — `udp`, `tcp`, `tls`, `ws`, or `wss`.
- bind: Address and port the listener binds to. If you set the address to `0.0.0.0`, it binds to all interfaces; the SIP port defaults to 5060 for UDP/TCP.

A minimal UDP transport:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

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
auth_type=digest
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
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP allows the `endpoint`, `auth`, and `aor` sections to share the same section name (e.g. the two `[6001]` blocks above, distinguished by their `type=`); many admins instead suffix them (`[6001]`, `[6001-auth]`, `[6001]` aor) for readability. For a device that registers, the contact is learned dynamically when the phone registers, so the AOR needs no static `contact`.

## IAX Extensions

`chan_iax2` still ships in Asterisk 22 but is now legacy; SIP/PJSIP is the preferred protocol for new deployments.

You may also create IAX extensions. This protocol is native to the Asterisk, and we will have an entire section devoted to it later in this book. For now, let’s create a few extensions using the protocol. As the first section to be configured, the section [general] has certain parameters to be configured. The main options are:

- allow/disallow: Defines which codecs are going to be used.
- bindaddr: Address the IAX2 listener binds to. If you set it up as 0.0.0.0 (default), it will bind to all interfaces.
- context: Sets the default context for all clients unless changed in the client section. We used dummy for security reasons. Unauthenticated users get into this context when the option allowguest is set to yes.
- bindport: IAX2 UDP port to listen on (default 4569).
- delayreject: When set to yes, delays the sending of an authentication reject for a REGREQ or AUTHREQ, which improves the security against brute-force password attacks.
- bandwidth: When set to high, it allows the selection of high bandwidth codecs, such as the g711 in their variants ulaw and alaw.

The following is a sample of the [general] section of the file iax.conf.

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

### IAX Clients

After finishing the general sections, it is time to set up the IAX clients.

- `[name]`: The section name is the IAX peer/user name; an incoming IAX connection is matched to it by name.
- `type`: The connection class — `peer`, `user`, or `friend`:
  - `peer`: Asterisk sends calls to a peer.
  - `user`: Asterisk receives calls from a user.
  - `friend`: both directions at once.
- `host`: IP address or host name. The most common value is `dynamic`, used when the device registers to Asterisk.
- `secret`: Password to authenticate peers and users.

Warning: Use strong passwords with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for IAX md5 hashes are available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers. Example:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Konfiguration der SIP-Geräte

Nachdem die Telefone in der Asterisk-Konfigurationsdatei definiert wurden, ist es Zeit, das Telefon selbst zu konfigurieren. In diesem Beispiel zeigen wir, wie man ein kostenloses Softphone – das SipPulse Softphone (Download von https://www.sippulse.com/produtos/softphone) – einrichtet. Lesen Sie das Handbuch Ihres Geräts, um die Parameter Ihres Telefons zu verstehen. Schritt 1: Konfigurieren Sie das Telefon, um die Nebenstelle 6000 zu verwenden. Führen Sie das Installationsprogramm aus. Nach der Ausführung öffnen Sie die Konto‑/SIP‑Einstellungen und fügen ein neues SIP‑Konto hinzu. Geben Sie die erforderlichen Informationen ein.

![Der SipPulse Softphone Kontobildschirm – geben Sie den Server (Ihre Asterisk‑IP oder Domain), Benutzernamen, Passwort und Anzeigenamen ein und wählen Sie dann den Transport (UDP, TCP oder TLS).](../images/softphone/sipphone-account.png){width=35%}

Anzeigename: 6000  Benutzername: 6000  Passwort: #MySecret1#7  Autorisierungs‑Benutzername: 6000  Domain: ip_of_your_server. Bestätigen Sie, dass Ihr Telefon registriert ist, indem Sie den Konsolenbefehl `pjsip show endpoints` (oder `pjsip show endpoint 6000` für Details; `pjsip show contacts` zeigt die registrierten AOR‑Kontakte) ausführen. Wiederholen Sie die Konfiguration für das Telefon 6001.

![Ein registriertes SipPulse Softphone – der grüne Punkt und die Kontoleiste (`1001@softphone.sippulse.com.br`) bestätigen die Registrierung; tätigen Sie einen Anruf über das Tastenfeld oder die Anruf‑/Video‑Buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configuring the IAX devices

IAX2 ist ein Legacy‑Protokoll (siehe das Kapitel *Legacy channels*), und das SipPulse Softphone unterstützt nur SIP, sodass es kein IAX‑Konto registrieren kann. Wenn Sie IAX2 testen müssen, verwenden Sie ein Softphone, das es noch unterstützt. Erstellen Sie ein neues IAX‑Konto,

3. Wählen Sie neues IAX‑Konto.
4. Fügen Sie die zugehörigen Optionen für das Telefon 6003 und optional für das Telefon 6004 ein.
5. Speichern Sie die Konfiguration und prüfen Sie, ob das Telefon mit `iax2 show peers` registriert ist.

Wichtig: Verwenden Sie ein Konto für SIP und ein weiteres für IAX. Wenn Sie das System so konfigurieren möchten, dass sowohl IAX als auch SIP gleichzeitig klingeln, zeigen wir Ihnen, wie das im Dial‑Plan‑Abschnitt funktioniert.

### Configuring a PSTN interface

Um eine Verbindung zur PSTN herzustellen, benötigen Sie ein Foreign‑Exchange‑Office‑Interface (FXO) und eine Telefonleitung. Sie können auch eine bestehende PBX‑Durchwahl verwenden. Sie können eine Telefonie‑Interface‑Karte mit einem FXO‑Interface von verschiedenen Herstellern beziehen. In diesem Beispiel zeigen wir Ihnen, wie Sie eine DAHDI‑Interface‑Karte installieren.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### Analog lines using DAHDI

Sie können eine analoge Karte, die mit DAHDI kompatibel ist, von mehreren Herstellern erwerben. Die X100P war eine der ersten Digium‑Karten und wurde bereits eingestellt. Einige Hersteller produzieren noch ähnliche Klone. Zusätzlich zum Preis der X100P haben wir mehrere Probleme zwischen diesen Karten und neuen Motherboards festgestellt, daher sollten Sie sie mit Vorsicht einsetzen. Die X100P ist meiner Meinung nach keine gute Wahl für eine Produktionsumgebung. Jede mit DAHDI kompatible Karte sollte funktionieren. Dank des Teams der DAHDI‑Entwickler haben wir jetzt ein Werkzeug, das Interface‑Karten fast automatisch erkennt und konfiguriert. Wenn Sie gerade die DAHDI‑Treiber installiert haben, vergessen Sie nicht, `make config` auszuführen und die Maschine neu zu starten, damit sie automatisch geladen wird. Sie können die folgenden Befehle verwenden, um Ihre Karte zu erkennen und zu konfigurieren. Schritt 1: Um Ihre Hardware zu erkennen, verwenden Sie:

```
dahdi_hardware
```

Step 2: Zur Konfiguration verwenden Sie:

```
dahdi_genconf
```

Der obige Befehl erzeugt zwei Dateien /etc/dahdi/system.conf und /etc/asterisk/dahdi-channels.conf. Die Standardparameter für dahdi_genconf sind normalerweise in Ordnung, können aber in der Datei /etc/dahdi/genconf_parameters geändert werden. Standardmäßig fügt er die Zeilen (FXO) im Kontext from-pstn und die Telefone (FXS) im Kontext from-internal ein. Schritt 3: Nach dem Ausführen von dahdi_genconf fügen Sie in der letzten Zeile der Datei /etc/asterisk/chan_dahdi.conf die folgende Zeile ein:

```
#include dahdi-channels.conf
```

Schritt 4: Bearbeiten Sie die Datei /etc/dahdi/modules und kommentieren Sie alle nicht verwendeten Treiber aus. Starten Sie neu, bevor Sie fortfahren, und prüfen Sie, ob die Kanäle erkannt werden, indem Sie verwenden:

```
*CLI> dahdi show channels
```

### Verbindung zum PSTN über einen VoIP‑Provider

Wenn Ihr Budget wirklich begrenzt ist, können Sie einen SIP‑Trunk konfigurieren, um eine Verbindung zum PSTN herzustellen. Das ist mit Abstand die günstigste Methode, um zum PSTN zu verbinden. Tausende von VoIP‑Providern gibt es weltweit. Um sich mit einem von ihnen zu verbinden, benötigen Sie einige Parameter. Parameter, die vom SIP‑Provider bereitgestellt werden.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

Zwei Parameter müssen Sie selbst bestimmen.

- Extension to receive calls—in this case: 9999
- context: from-sip

In PJSIP wird ein registrierender SIP‑Trunk aus derselben Objektfamilie wie ein endpoint gebaut, plus expliziten `registration`‑ und `identify`‑Objekten. Das `registration`‑Objekt weist Asterisk an, sich beim Provider zu registrieren, das `identify`‑Objekt ordnet eingehenden Verkehr von der IP des Providers dem endpoint zu (PJSIP authentifiziert eingehende INVITEs anhand der Quell‑IP), und `outbound_auth` liefert die Zugangsdaten für ausgehende Anrufe und die Registrierung.

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
auth_type=digest
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

Um auf diesen Trunk zuzugreifen, verwenden wir den Kanalnamen `PJSIP/siptrunk`. Die Einstellung `dtmf_mode=rfc4733` überträgt DTMF out‑of‑band (RFC 4733 ersetzt das ältere RFC 2833; die Nutzlast ist identisch). Die Option `identify`/`match` akzeptiert IP‑Adressen, CIDRs oder Hostnamen, aber Hostnamen werden einmalig beim Laden der Konfiguration aufgelöst, daher sollten Sie bei einem Anbieter mit wechselnden IPs die Signalisierungs‑IP(s) explizit angeben. Bestätigen Sie die Registrierung mit `pjsip show registrations`.

## Dialplan-Einführung

Der Dialplan ist wie das Herz von Asterisk. Er definiert, wie Asterisk jeden einzelnen Anruf zur PBX verarbeitet. Er besteht aus Extensions, die eine Anweisungsliste für Asterisk bilden. Anweisungen werden durch Ziffern ausgelöst, die vom Channel oder von einer Anwendung empfangen werden. Um Asterisk erfolgreich zu konfigurieren, ist es entscheidend, den Dialplan zu verstehen. Der größte Teil des Dialplans befindet sich in der Datei extensions.conf im Verzeichnis /etc/asterisk. Diese Datei verwendet die einfache Gruppen‑Grammatik und hat vier Hauptkonzepte:

- Extensions
- Priorities
- Applications
- Contexts

Lassen Sie uns einen einfachen Dialplan erstellen. In den folgenden Abschnitten dieses Buches widme ich ein ganzes Kapitel ausschließlich dem Dialplan. Wenn Sie die Beispieldateien installiert haben (make samples), existiert die extensions.conf bereits. Speichern Sie sie unter einem anderen Namen und beginnen Sie mit einer leeren Datei.

## The structure of the file extensions.conf

The extensions.conf file is separated into sections. The first is the [general] section followed by the [globals] section. The beginning of each section starts with its name definition (i.e., [default]) and finishes when another section is created.

### The section [general]

The general section sits at the top of the file. Before starting to configure the dial plan, it is helpful to know the general options that control certain dial plan behaviors. These options are:

- static and write protect: If `static=yes` and `writeprotect=no`, you can save the running dial plan back to disk with the CLI command:

```
*CLI> dialplan save
```

Warning: If you issue a `dialplan save` command from the CLI, you will lose any remarks and comments in the file.

- autofallthrough: If autofallthrough is set, then if an extension runs out of things to do, it will terminate the call with BUSY, CONGESTION, or HANGUP depending on Asterisk's best guess. This is the default. If autofallthrough is not set, then if an extension runs out of things to do, Asterisk will wait for a new extension to be dialed.
- clearglobalvars: If clearglobalvars is set, global variables will be cleared and reparsed into an dialplan reload or Asterisk reload. If clearglobalvars is not set, then global variables will persist through reloads and—even if deleted from the extensions.conf or one of its included files—they will remain set to the previous value.
- extenpatternmatchnew: Uses a faster pattern-matching algorithm, which helps noticeably when you have a large number of extensions. Defaults to no.
- userscontext: This is the context where the entries from the users.conf are registered.

### The section [globals]

In the [globals] section you will define global variables and their initial values. You can access the variable in the dial plan using ${GLOBAL(variable)}. You can even access variables defined in the linux/unix environment using ${ENV(variable)}. Global variables are not case sensitive. A few examples could be:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

In the following example, you can set and test a global variable in the dial plan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Kontexte

Context ist die benannte Partition des Dialplans. Nach den Abschnitten [general] und [globals] ist der Dialplan ein Satz von Kontexten, in denen jeder Kontext mehrere Extensions enthält, jede Extension mehrere Prioritäten hat und jede Priorität eine Anwendung mit mehreren Argumenten aufruft.

![Asterisk-Anrufablauf: Jeder Anruf kommt auf einem Kanal (IAX, SIP und andere) als eingehender Anrufzweig an; der Kontext des Kanals — global oder pro Kanal in der Kanal-Konfigurationsdatei festgelegt — entscheidet, welcher Kontext in extensions.conf den Anruf verarbeitet, bevor er auf dem ausgehenden Zweig weitergeleitet wird.](../images/04-first-pbx-fig03.png)

![Anrufverarbeitung: Das `context=`, das für einen Kanal definiert ist (in chan_dahdi.conf oder pjsip.conf), benennt den passenden Kontext in extensions.conf, in dem der Dialplan den Anruf behandelt.](../images/04-first-pbx-fig04.png)

Sie können einen einfachen Dialplan erstellen, um andere Telefone und das PSTN zu erreichen. Asterisk ist jedoch weitaus leistungsfähiger. Unser Ziel ist es, Ihnen weitere Details dessen zu vermitteln, was im Dialplan möglich ist.

## Extensions

Im Gegensatz zur traditionellen PBX, bei der Durchwahlen Telefonen, Schnittstellen, Menüs usw. zugeordnet sind, ist eine Durchwahl in Asterisk eine Liste von Befehlen, die verarbeitet werden, wenn eine bestimmte Durchwahlnummer oder ein Name ausgelöst wird. Die Befehle werden in Prioritätsreihenfolge verarbeitet.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

Eine Durchwahl kann wörtlich, standard oder speziell sein. Eine Standard‑Durchwahl enthält nur Zahlen oder Namen sowie die Zeichen * und #; 12#89* ist eine gültige wörtliche Durchwahl. Namen können ebenfalls zum Durchwahl‑Matching verwendet werden. Durchwahlen sind case‑sensitive. Sie können jedoch nicht zwei Durchwahlen mit demselben Namen, aber unterschiedlicher Groß‑/Kleinschreibung erstellen. Wenn eine Durchwahl gewählt wird, wird der Befehl mit der ersten Priorität ausgeführt, gefolgt vom Befehl mit Priorität 2 usw. Dies geschieht, bis der Anruf beendet wird oder ein Befehl die Nummer eins zurückgibt, was einen Fehler anzeigt. Was Asterisk tut, wenn die letzte Priorität ausgeführt wurde, wird durch den Parameter autofallthrough geregelt. Siehe den Abschnitt [general] in diesem Kapitel. Beispiel:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Oben finden Sie die Liste der Anweisungen, die verarbeitet werden, wenn die Durchwahl 123 gewählt wird. Die erste Priorität ist, den Kanal zu beantworten (notwendig, wenn sich der Kanal im Klingelzustand befindet, d. h. FXO‑Kanäle). Die zweite Priorität spielt die Audiodatei tt‑weasels ab. Die dritte Priorität legt den Kanal auf. Eine weitere Möglichkeit besteht darin, den Anruf anhand der Caller‑ID zu behandeln. Sie können das Zeichen / verwenden, um die zu verarbeitende Caller‑ID anzugeben. Beispiele:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Dieses Beispiel löst die Durchwahl 123 aus und führt die folgenden Optionen nur aus, wenn die Caller‑ID 100 ist. Das kann auch mit dem unten beschriebenen Muster erfolgen:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: ordnet einer Durchwahl einen Kanal zu. Sie wird verwendet, um den Kanalzustand zu überwachen. Sie wird zusammen mit presence eingesetzt. Das Telefon muss dies unterstützen.

#### Patterns

Sie können Muster und wörtliche Werte im Dialplan verwenden. Muster sind sehr nützlich, um die Größe des Dialplans zu reduzieren. Alle Muster beginnen mit dem Zeichen “_”. Die folgenden Zeichen können zur Definition eines Musters verwendet werden. Die Abbildung zeigt die für Asterisk verfügbaren Muster.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk verwendet einige Durchwahlnamen als Standard‑Durchwahlen.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Beschreibung:

- **s**: Start. Wird verwendet, um einen Anruf zu bearbeiten, wenn keine Durchwahl gewählt wurde. Nützlich für FXO‑Trunks und die Verarbeitung in Menüs.
- **t**: Timeout. Wird verwendet, wenn Anrufe nach einer abgespielten Aufforderung inaktiv bleiben. Außerdem wird damit eine inaktive Leitung aufgelegt.
- **T**: AbsoluteTimeout. Wenn Sie ein Anruflimit mit der `TIMEOUT(absolute)`‑Dialplan‑Funktion festlegen, wird der Anruf nach Überschreiten des Limits an die T‑Durchwahl gesendet.
- **h**: Hangup. Wird aufgerufen, nachdem der Benutzer den Anruf beendet hat.
- **i**: Invalid. Wird ausgelöst, wenn Sie

## Variables

In the Asterisk PBX, variables can be global, channel-specific, and environment-specific. You can use the NoOP() application to see the content of a variable in the console. It can use a global variable or a channel-specific variable as applications arguments. A variable can be referenced as in the following example, where varname is the name of the variable.

```
${varname}
```

A variable name can be an alphanumeric string starting with a letter. Global variable names are not case sensitive. However, system variables (Asterisk-defined are channel-defined) are case sensitive. Thus, the variable ${EXTEN} is different from ${exten}.

### Global variables

Global variables can be configured in the [global] section in the extensions.conf file or using the application:

```
set(Global(variable)=content)
```

### Channel-specific variables

Channel-specific variables are configured using the application set(). Each channel receives its own variable space. There is no chance of collisions between variables from different channels. A channel- specific variable is destroyed when the channel hangs up. Some of the most commonly used variables are:

- ${EXTEN} Extension dialed
- ${CONTEXT} Current context
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Current caller ID
- ${PRIORITY} Current priority

Other channel-specific variables are all uppercase. You can see the content of several variables using the dumpchan() application. Below is a simple excerpt of dump-channel variables.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Dumpchan output:

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

The field layout above is the Asterisk 22 `DumpChan` output (a real `PJSIP/...` channel name, the `CallerIDNum`/`ConnectedLineID` fields, and the `Raw*`/`Transcode`/`BridgeID` rows that PJSIP channels populate). Unlike the old driver, a PJSIP channel does not auto-set `SIPCALLID`/`SIPUSERAGENT` channel variables; the equivalent SIP details are read on demand with the `PJSIP_HEADER()` and `CHANNEL()` dialplan functions — for example `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}`, and `${CHANNEL(rtp,dest)}` for the remote RTP address.

### Environment-specific variables

Environment-specific variables can be used to access variables defined in the operating system. You can set environment-specific variables using the function ENV(). For example:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

Some applications use variables for data input and output. You can set variables before calling the application or retrieve the variable after the application execution. For example: The Dial application returns the following variables:

- ${DIALEDTIME} ->This is the time from dialing a channel until it is disconnected.
- ${ANSWEREDTIME} -> This is the amount of time for the actual call.
- ${DIALSTATUS} This is the status of the call: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Error message for the call.

## Expressions

Expressions can be very useful in the dial plan. They are used to manipulate strings and perform math and logical operations.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

The expression syntax is defined as follows:

```
$[expression1 operator expression2]
```

Let’s suppose that we have a variable called “I” and we want to add 100 to the variable:

```
$[${I}+100]
```

When Asterisk finds an expression in the dial plan, it changes the entire expression by the resulting value.

### Operators

The following operators can be used to build expressions. It is important to observe operator precedence.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

A regular expression is a special text string used to describe a search pattern. You can think of regular expressions as wildcards. Regular expressions are used to match a string to a pattern to check the matching. If the match succeeds and the regular expression contains at least one match, the first match is returned; otherwise, the result is the number of characters matched.

#### Comparison operators

The result of a comparison is 1 if the relation is true or 0 if it is false.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Put these expressions in your dial plan and use the NoOP() application to evaluate the expressions. Dial 9002 and examine the results in the Asterisk console. Use verbose 15 to show the results.

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

## Functions

Einige Anwendungen wurden durch Funktionen ersetzt, die die Verarbeitung von Variablen auf fortgeschrittenere Weise als reine Ausdrücke ermöglichen. Die vollständige Funktionsliste erhalten Sie, indem Sie den folgenden Konsolenbefehl ausführen:

```
*CLI> core show functions
```

String‑Länge: ${LEN(string)} gibt die Länge des Strings zurück

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Im ersten Vorgang zeigt das System 5 als Ergebnis (die Anzahl der Buchstaben im Wort „fruit“). Der zweite gibt die Zahl 4 zurück (die Anzahl der Buchstaben im Wort „pear“). Teilstrings: Gibt den Teilstring zurück, beginnend an der Position, die durch den Parameter „offset“ definiert ist, mit der String‑Länge, die im Parameter „length“ angegeben ist. Ist der Offset negativ, wird von rechts nach links begonnen, ausgehend vom Ende des Strings. Wird die Länge weggelassen oder ist sie negativ, wird der gesamte String ab dem Offset genommen.

```
${string:offset:length }
```

Beispiel #1: Mehrere Teilstrings

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Beispiel #2: Die Vorwahl aus den ersten drei Ziffern extrahieren.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Beispiel #3: Nimmt alle Ziffern aus der Variable ${EXTEN}, außer der Vorwahl.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### String‑Verkettung

Um zwei Strings zu verketten, schreiben Sie sie einfach hintereinander.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Anwendungen

Um einen Dialplan zu erstellen, müssen wir das Konzept der Anwendungen verstehen. Sie werden Anwendungen verwenden, um den Kanal im Dialplan zu steuern. Anwendungen werden in mehreren Modulen implementiert. Verfügbare Anwendungen hängen von den Modulen ab. Sie können alle Asterisk‑Anwendungen mit dem Konsolenbefehl anzeigen:

```
*CLI> core show applications
```

Alternativ können Sie Details einer bestimmten Anwendung mit dem folgenden Beispiel anzeigen:

```
*CLI> core show application Dial
```

Um einen einfachen Dialplan zu erstellen, müssen Sie einige Anwendungen kennen. Wir werden später im Buch fortgeschrittenere Beispiele besprechen.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

Wir werden diese Anwendungen (oben) verwenden, um einen einfachen Dialplan für zwei grundlegende PBXs zu erstellen.

### Answer()

[Synopsis] Answers a channel if ringing [Description] Answer([delay]): If the call has not been answered, the application will answer it. Otherwise, it has no effect on the call. If a delay is specified, Asterisk will wait the number of milliseconds specified in ‘delay’ before answering the call.

### Dial()

The following description can be obtained by issuing the show application dial in the dial plan. For easy searching, it is reproduced below. The syntax for the Dial application is also shown below:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

Dieses Anwendungsprogramm wird Anrufe zu einem oder mehreren angegebenen Kanälen tätigen. Sobald einer der angeforderten Kanäle annimmt, wird der ausgehende Kanal beantwortet – falls er noch nicht beantwortet wurde. Diese beiden Kanäle sind dann in einem gebrückten Anruf aktiv. Alle anderen angeforderten Kanäle werden anschließend aufgelegt. Sofern kein Timeout angegeben ist, wartet die Dial‑Anwendung unbegrenzt, bis einer der angerufenen Kanäle annimmt, der Benutzer auflegt oder alle angerufenen Kanäle besetzt oder nicht erreichbar sind. Die Ausführung des Dialplans wird fortgesetzt, wenn keine angeforderten Kanäle angerufen werden können oder wenn das Timeout abläuft. Diese Anwendung setzt nach Abschluss die folgenden Kanalvariablen:

- DIALEDTIME – Dies ist die Zeit vom Wählen eines Kanals bis zu dem Zeitpunkt, an dem er getrennt wird.  
- ANSWEREDTIME – Dies ist die Dauer eines tatsächlichen Gesprächs.  
- DIALSTATUS – Dies ist der Status des Anrufs: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE  

Für die Privacy‑ und Screening‑Modi wird die Variable DIALSTATUS auf DONTCALL gesetzt, wenn die angerufene Partei die anrufende Partei zum „Go Away“-Skript weiterleitet. Die Variable DIALSTATUS wird auf TORTURE gesetzt, wenn die angerufene Partei den Anrufer zum „torture“-Skript weiterleiten möchte. Diese Anwendung meldet eine normale Beendigung, wenn der ausgehende Kanal auflegt oder wenn der Anruf gebrückt ist und einer der beiden Parteien im Bridge den Anruf beendet. Die optionale URL wird an die angerufene Partei gesendet, wenn der Kanal dies unterstützt. Wenn die Variable OUTBOUND_GROUP gesetzt ist, werden alle von dieser Anwendung erstellten Peer‑Kanäle in diese Gruppe aufgenommen (wie in

```
Set(GROUP()=...).
```

The following table summarizes some of the most frequently used options for the application Dial. For the complete list, use the console command `core show application Dial`. In Asterisk 22 these options are separated from the channel and timeout by commas — for example `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Plays an announcement to the called party, using `x` as the file. |
| `C` | Resets the CDR for this call. |
| `d` | Allows the calling user to dial a 1-digit extension while waiting for the call to be answered. Exits to that extension if it exists in the current context, or to the context defined in the `EXITCONTEXT` variable, if it exists. |
| `D([called][:calling])` | Sends the specified DTMF strings after the called party answers, but before the call is bridged. The `called` string is sent to the called party and the `calling` string to the calling party. Either parameter can be used alone. |
| `f` | Forces the caller ID of the calling channel to be set to the extension associated with the channel via a dial plan `hint`. Useful where the PSTN does not allow an arbitrary caller ID. |
| `g` | Proceeds with dial plan execution at the current extension if the destination channel hangs up. |
| `G(context^exten^pri)` | If the call is answered, transfers the calling party to the specified priority and the called party to priority+1. Optionally an extension (or extension and context) can be specified; otherwise the current extension is used. |
| `h` | Allows the called party to hang up by sending the `*` DTMF digit. |
| `H` | Allows the calling party to hang up by sending the `*` DTMF digit. |
| `L(x[:y][:z])` | Limits the call to `x` ms, plays a warning when `y` ms are left, and repeats the warning every `z` ms. See the `LIMIT_*` variables below. |
| `m([class])` | Provides music on hold to the calling party until the requested channel answers. A specific MusicOnHold class can be specified. |
| `r` | Indicates ringing to the calling party and passes no audio until the called channel answers. |
| `S(x)` | Hangs up the call `x` seconds after the called party answers. |
| `t` | Allows the called party to transfer the calling party by sending the DTMF sequence defined in `features.conf`. |
| `T` | Allows the calling party to transfer the called party by sending the DTMF sequence defined in `features.conf`. |
| `w` | Allows the called party to enable one-touch recording by sending the DTMF sequence defined in `features.conf`. |
| `W` | Allows the calling party to enable one-touch recording by sending the DTMF sequence defined in `features.conf`. |
| `k` | Allows the called party to park the call by sending the DTMF sequence defined for call parking in `features.conf`. |
| `K` | Allows the calling party to park the call by sending the DTMF sequence defined for call parking in `features.conf`. |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): plays sounds for the caller.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: plays sounds for the called party.
- `LIMIT_TIMEOUT_FILE` — file to be played when time is up.
- `LIMIT_CONNECT_FILE` — file to be played when the call begins.
- `LIMIT_WARNING_FILE` — file to be played as a warning when `y` is defined. The default is to say the time remaining.

Example:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

Im obigen Beispiel wählt die Anwendung den entsprechenden PJSIP‑Kanal. Sowohl Anrufer als auch Angerufener können den Anruf übertragen (Tt). Statt eines Rückklingelns wird Musik on Hold gehört. Wenn innerhalb von 20 Sekunden niemand antwortet, springt die Nebenstelle zur nächsten Priorität.

### Hangup()

Hängt den anrufenden Kanal auf [Description] Hangup([causecode]): Diese Anwendung legt den anrufenden Kanal auf. Wird ein Cause‑Code angegeben, wird der Aufleggrund des Kanals auf den angegebenen Wert gesetzt.

### Goto()

Springt zu einer bestimmten Priorität, Nebenstelle oder Kontext [Description] Goto([[context|]extension|]priority): Diese Anwendung veranlasst den anrufenden Kanal, die Dial‑Plan‑Ausführung an der angegebenen Priorität fortzusetzen. Wird keine spezifische Nebenstelle (oder Nebenstelle und Kontext) angegeben, springt diese Anwendung zur angegebenen Priorität der aktuellen Nebenstelle. Wenn der Versuch, zu einem anderen Ort im Dial‑Plan zu springen, nicht erfolgreich ist, setzt der Kanal die Ausführung an der nächsten Priorität der aktuellen Nebenstelle fort.

## Erstellen eines Dialplans

Um einen einfachen Dialplan zu erstellen, müssen Sie alle eingehenden und ausgehenden Anrufe behandeln, indem Sie Kontexte und Nebenstellen anlegen. In diesem Abschnitt zeigen wir Ihnen, wie Sie die gebräuchlichsten Nebenstellen erstellen.

### Wählen zwischen Nebenstellen

Um das Wählen zwischen Nebenstellen zu ermöglichen, können wir die Kanalvariable ${EXTEN} verwenden, die sich auf die gewählte Nebenstelle bezieht. Beispielsweise, wenn der Nebenstellenbereich zwischen 4000 und 4999 liegt und alle Nebenstellen SIP verwenden, könnten wir den folgenden Befehl übernehmen:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Wählen einer externen Zielnummer

Um eine externe Zielnummer zu wählen, können Sie die gewählte Nummer mit einer Vorwahl versehen. In Nordamerika ist es üblich, eine 9 gefolgt von der extern zu wählenden Nummer zu verwenden. Wenn Sie einen analogen oder digitalen Kanal zum PSTN nutzen, sollte der Befehl wie folgt aussehen: Wenn Sie stattdessen den SIP‑Trunk anstelle des DAHDI verwenden möchten, benutzen Sie den `PJSIP/...@siptrunk`‑Kanal.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

Die obige Zeile erlaubt es Ihnen, die 9 und die gewünschte Nummer zu wählen. Im gegebenen Beispiel verwenden Sie den ersten DAHDI‑Kanal (DAHDI/1). Wenn Sie mehrere Leitungen haben und diese belegt ist, wird der Anruf nicht abgeschlossen. Sie könnten jedoch die folgende Zeile verwenden, um automatisch den ersten verfügbaren DAHDI‑Kanal auszuwählen. Optional können Sie den SIP‑Trunk anstelle von DAHDI verwenden. Im PJSIP‑Formular `Dial(PJSIP/number@siptrunk,...)` ist die gewählte Nummer der Benutzerteil und `siptrunk` ist der oben konfigurierte Endpoint.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

Der Parameter „g1“ sucht den ersten verfügbaren Kanal in der Gruppe und ermöglicht die Nutzung aller Kanäle. Mit der unten stehenden Zeile könnten Sie eine Ferngesprächsnummer wählen.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Wählen von 9, um eine PSTN-Leitung zu erhalten

Wenn Sie keine Einschränkungen für das externe Wählen haben, können Sie es vereinfachen und das Folgende verwenden:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Entgegennahme eines Anrufs in der Operator-Erweiterung

Im folgenden Beispiel ist die Operator-Erweiterung 4000. Die PSTN-Leitung ist an ein FXO-Interface angeschlossen. In der Datei chan_dahdi.conf ist der angegebene Kontext from-pstn. Jeder Anruf, der von der PSTN kommt, wird zum Kontext from-pstn im Dialplan geroutet. Diese Leitung hat kein Direct Inward Dialing (DID); daher müssen wir den Anruf über die „s“-Erweiterung entgegennehmen. Beim Empfang vom SIP-Trunk verwenden Sie den Kontext [from-sip].

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

### Empfang eines Anrufs mittels Direct Inward Dialing (DID)

Wenn Sie eine digitale Leitung haben, erhalten Sie die gewählte Nebenstelle. In diesem Fall müssen Sie den Anruf nicht an den Operator weiterleiten; stattdessen können Sie den Anruf direkt an das Ziel weiterleiten. Angenommen, Ihr DID‑Bereich reicht von 3028550 bis 3028599 und die letzten vier Ziffern werden im DID übergeben. Die Konfiguration würde wie im folgenden Beispiel aussehen:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Mehrere Nebenstellen gleichzeitig anrufen

Sie können Asterisk so konfigurieren, dass es eine Nebenstelle wählt und, falls diese nicht beantwortet wird, mehrere andere Nebenstellen gleichzeitig anruft, wie im folgenden Beispiel gezeigt:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

In diesem Beispiel, wenn jemand die Operator‑Taste wählt, wird zunächst der Kanal DAHDI/1 versucht. Wenn nach 15 Sekunden niemand antwortet (Timeout), klingeln die Kanäle DAHDI/1, DAHDI/2 und DAHDI/3 gleichzeitig für weitere 15 Sekunden.

### Routing by Caller ID

In diesem Beispiel könnten Sie je nach Anrufer‑ID unterschiedliche Behandlungen vornehmen, was bei Call‑Spammern nützlich sein könnte. Zum Beispiel:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In diesem Beispiel haben wir eine spezielle Regel hinzugefügt, die bei der Anrufer-ID 4832518888 eine Nachricht aus der zuvor aufgenommenen Datei „I-have-moved-to-china“ abspielt. Andere Anrufe werden wie üblich angenommen.

### Verwendung von Variablen im Dialplan

Asterisk kann globale und Kanal‑Variablen im Dialplan als Argumente für bestimmte Anwendungen verwenden. Betrachten Sie die folgenden Beispiele:

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

Using variables makes future changes easier. If you change the variable, all references are changed immediately.

### Aufzeichnen einer Durchsage

In einigen der später in diesem Abschnitt besprochenen Optionen werden wir aufgezeichnete Ansagen verwenden. Hier zeigen wir Ihnen eine einfache Methode, sie aufzunehmen. Wir werden die Anwendung Record() benutzen, um die Durchsage mit dem eigenen Telefon zu speichern.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Diese Anweisungen ermöglichen es Ihnen, jede Nachricht von einem Softphone aufzunehmen. Beispiel: Wählen Sie recordmenu vom Softphone Die Anweisungen rufen die Aufnahme mit der Variable ${EXTEN:6} ohne die ersten sechs Buchstaben auf. Mit anderen Worten, die Anweisung ist äquivalent zu record(menu:gsm). Alles, was Sie tun müssen, ist `record` + `name_of_the_file_to_be_recorded` zu wählen, # zu drücken, um die Aufnahme zu beenden, und zu warten, bis die Aufnahme zu hören ist.

### Empfang der Anrufe in einer digitalen Rezeption

Jetzt, wo wir einige einfache Beispiele haben, erweitern wir unser Wissen über die Anwendungen **background()** und **goto()**. Der Schlüssel für interaktive Systeme in Asterisk ist die Anwendung **background()**, die es Ihnen ermöglicht, eine Audiodatei abzuspielen, die bei Tastendruck des Anrufers unterbrochen wird, um den Anruf an die gewählte Nebenstelle zu senden. Syntax der Anwendung **background()**:

```
exten=>extension, priority, background(filename)
```

Eine weitere sehr nützliche Anwendung ist goto(). Wie der Name impliziert, springt sie zum angegebenen Kontext, zur Erweiterung und zur Priorität. Syntax der Anwendung goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Gültige Formate für den goto()-Befehl:

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

Im folgenden Beispiel erstellen wir eine digitale Telefonistin. Es ist sehr einfach, die Datei extensions.conf zu bearbeiten und die folgenden Nebenstellen zu konfigurieren:

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

Die SIP‑Erweiterungen verwenden `PJSIP/` und die IAX‑Erweiterungen verwenden `IAX2/` — beide Treiber werden in Asterisk 22 ausgeliefert, obwohl `chan_iax2` inzwischen als veraltet gilt und SIP/PJSIP bevorzugt wird.

In der Datei **menu1.gsm** nehmen Sie die Meldung „press the extension or wait for the operator“ auf. Wenn der Benutzer die Nummer 6000 wählt, wird er zur Erweiterung 6000 weitergeleitet. An diesem Punkt sollten Sie ein klares Verständnis für die Verwendung mehrerer Anwendungen haben, darunter `answer()`, `background()`, `goto()`, `hangup()` und `playback()`. Wenn Ihnen das noch nicht klar ist, lesen Sie dieses Kapitel erneut, bis Sie sich mit dem Inhalt wohlfühlen. Die Anwendung `background` werden Sie sehr häufig einsetzen. Sobald Sie die Grundlagen von Erweiterungen, Prioritäten und Anwendungen verstanden haben, wird es einfach sein, einen einfachen Dialplan zu erstellen. Diese Konzepte werden später im Buch ausführlicher behandelt, und Sie werden sehen, dass der Dialplan immer leistungsfähiger wird.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Konfigurationsdateien im Verzeichnis /etc/asterisk gespeichert werden. Um Asterisk zu verwenden, ist es zunächst notwendig, die Kanäle (z. B. pjsip, dahdi, iax) zu konfigurieren. Für Konfigurationsdateien existieren drei verschiedene Grammatikformen: einfache Gruppe, Objektvererbung und komplexe Entität. Der Dialplan wird in der Datei extensions.conf erstellt und besteht aus einer Menge von Kontexten und Extensions. Im Dialplan löst jede Extension eine Anwendung aus. Sie haben gelernt, die Anwendungen playback, background, dial, goto, hangup und answer zu verwenden.

## Quiz

1. Die Kanalkonfigurationsdateien sind (wählen Sie alle zutreffenden aus):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Auf Asterisk 22 wird der einzelne `chan_sip`‑Peer `[6001]` (`type=friend`/`host=dynamic`) in `pjsip.conf` durch welchen Satz verwandter Objekte ersetzt?
   - A. Ein `type=peer` und ein `type=user`
   - B. Ein `type=endpoint`, ein `type=auth` und ein `type=aor`
   - C. Ein einzelnes `type=friend`
   - D. Ein `type=transport` und ein `type=global`
3. Das Definieren eines Kontextes in der Kanalkonfigurationsdatei ist wichtig, weil er den eingehenden Kontext für Anrufe von diesem Kanal festlegt – ein Anruf von dem Kanal wird im passenden Kontext in `extensions.conf` verarbeitet.
   - A. True
   - B. False
4. Die Hauptunterschiede zwischen den Anwendungen `Playback()` und `Background()` sind (wählen Sie zwei):
   - A. Playback spielt eine Ansage, wartet aber nicht auf Ziffern.
   - B. Background spielt eine Ansage, wartet aber nicht auf Ziffern.
   - C. Background spielt eine Nachricht und wartet darauf, dass Ziffern gedrückt werden.
   - D. Playback spielt eine Nachricht und wartet darauf, dass Ziffern gedrückt werden.
5. Wenn ein Anruf über eine Telephoniekarten‑Schnittstelle (FXO) ohne DID in Asterisk gelangt, wird er in der speziellen Nebenstelle verarbeitet:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. Gültige Formate für die Anwendung `Goto()` sind (wählen Sie drei):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. Das Muster `_7[1-5]XX` trifft zu (wählen Sie alle zutreffenden aus):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. In `Dial(PJSIP/${EXTEN},20,tTm)`, was bewirkt die Option `m`?
   - A. Begrenzt die Anrufdauer auf ein Maximum.
   - B. Liefert Musik on Hold an den Anrufer anstelle von Klingelton, bis der Kanal annimmt.
   - C. Sendet DTMF‑Ziffern, nachdem die angerufene Partei geantwortet hat.
   - D. Erzwingt die Caller‑ID mittels eines Dial‑Plan‑Hints.
9. In der Options‑Vererbungs‑Grammatik, die von `chan_dahdi.conf` verwendet wird, Sie:
   - A. Definieren das Objekt in einer einzigen Zeile.
   - B. Definieren zuerst Optionen und deklarieren die Objekte unter den definierten Optionen.
   - C. Definieren einen separaten Kontext für jedes Objekt.
10. Prioritäten in einer Nebenstelle müssen fortlaufend nummeriert sein (1, 2, 3, …) und dürfen `n` nicht verwenden.
    - A. True
    - B. False

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
