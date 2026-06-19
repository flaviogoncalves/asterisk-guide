# Migration von chan_sip zu PJSIP: ein Kochbuch

Wenn Sie dies mit einem Asterisk 13, 16 oder 18 System lesen, das noch im Produktivbetrieb ist, haben Sie eine Frist. `chan_sip` — der ursprüngliche SIP-Kanaltreiber, der über `sip.conf` konfiguriert wurde — wurde **in Asterisk 17 als veraltet markiert, in Asterisk 19 aus dem Standard-Build entfernt und in Asterisk 21 vollständig gelöscht**. Er existiert in Asterisk 22 LTS nicht mehr. Es gibt kein Flag, um ihn wieder zu aktivieren, kein `noload`, um dies zu umgehen, und kein Paket zur Installation. Der einzige SIP-Kanaltreiber in Asterisk 22 ist **PJSIP** (`res_pjsip` plus `chan_pjsip`), konfiguriert über `pjsip.conf`.

Ein Upgrade auf Asterisk 22 ist daher für die meisten Standorte ebenso ein *SIP-Migrationsprojekt* wie ein Versionssprung. Die gute Nachricht ist, dass sich das Protokoll auf der Leitung nicht ändert — ein Telefon, das sich gestern registriert und angerufen hat, wird dies auch morgen tun — und Asterisk liefert ein Konvertierungstool mit, das die ersten 80 % der Übersetzung für Sie erledigt. Dieses Kapitel ist ein praktisches Kochbuch: die Konzeptzuordnung, das Konvertierungsskript, direkte `sip.conf` → `pjsip.conf` Übersetzungen für die Fälle, die Sie tatsächlich haben, die Änderungen am dialplan und der CLI, die mit dem Umzug einhergehen, die Migration von realtime (Datenbank) sowie eine Checkliste und die Fallstricke, die Anwender oft treffen.

Alles hier wurde anhand des Asterisk 22.10.0-Labors des Buches verifiziert. Das tiefgreifende Legacy-Material zu `chan_sip` selbst — und eine vollständige End-to-End-Konvertierung eines Multi-Device `sip.conf` — finden Sie im Kapitel *Legacy channels*; dieses Kapitel ist die fokussierte, rezeptartige Ergänzung dazu.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Zu erklären, warum `chan_sip` in Asterisk 22 verschwunden ist und was es ersetzt
- Das `sip.conf` Peer/User/Friend-Modell auf das PJSIP-Objektmodell abzubilden
  (endpoint + aor + auth + identify + transport + registration)
- Das `sip_to_pjsip.py` Konvertierungsskript auszuführen und dessen Ausgabe kritisch zu prüfen
- Die gängigen Gerätetypen (registrierendes Telefon, eingehender trunk, ausgehende Registrierung) von `sip.conf` zu `pjsip.conf` manuell zu übersetzen
- NAT-, Medien-, DTMF-, codec- und Authentifizierungseinstellungen Option für Option zu migrieren
- Den dialplan (`SIP/` → `PJSIP/`) und die CLI (`sip show` → `pjsip show`) zu aktualisieren
- Eine realtime/ARA-Bereitstellung von `sippeers`/`sipregs` auf die Sorcery `ps_*` Tabellen zu migrieren
- Eine Migrationscheckliste abzuarbeiten und die klassischen Fallstricke zu vermeiden

## Warum überhaupt migrieren

`chan_sip` hat Asterisk fast zwei Jahrzehnte lang gedient, trug aber architektonische Altlasten mit sich: ein monolithisches Modul, einen einzigen Konfigurationsblock pro Gerät, schwache Unterstützung für mehrere Transportschichten und einen SIP-Stack, der hinter den RFCs zurückgeblieben war. **PJSIP** — basierend auf dem ausgereiften pjproject-Stack von Teluu und eingeführt in Asterisk 12 — war der komplette Neuanfang als Ersatz. Mit Asterisk 21 hat das Asterisk-Projekt die Arbeit abgeschlossen und `chan_sip` aus dem Quellcode entfernt.

Sie können die Situation auf jedem Asterisk 22 System bestätigen:

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` gibt *0 modules loaded* zurück — es ist schlicht nicht vorhanden. Es gibt nichts, *zu* dem man migrieren könnte, außer PJSIP, daher ist die einzige wirkliche Frage das *Wie*, nicht das *Ob*.

## Die konzeptionelle Zuordnung: Es gibt keinen einzelnen "peer"

Der mentale Wandel, der jeden stolpern lässt, der von `sip.conf` kommt, ist dieser: **PJSIP hat kein `[peer]`.** In `sip.conf` beschrieb ein eingeklammerter Block — ein `peer`, ein `user` oder ein `friend` — *alles* über ein Gerät: seine Zugangsdaten, wo es zu erreichen ist, seine codecs, sein NAT-Verhalten, seinen dialplan context. PJSIP bricht diesen einzelnen Block bewusst in mehrere kleinere, zweckgebundene Objekte auf, die jeweils mit einem `type=` markiert sind und *sich gegenseitig beim Namen referenzieren*:

| PJSIP-Objekt (`type=`) | Verantwortung |
| --- | --- |
| `endpoint` | Die Identität des Geräts für die Anrufbehandlung: codecs, context, DTMF, Medien, NAT und Verweise auf seine `auth`/`aors`/`transport` |
| `aor` (Address of Record) | *Wo* das Gerät zu erreichen ist — registrierte oder statische Kontakte, `max_contacts`, qualify |
| `auth` | Zugangsdaten (Benutzername/Passwort) für eingehende und/oder ausgehende Authentifizierung |
| `identify` | Abgleich einer eingehenden Anfrage mit einem endpoint anhand der **Quell-IP** anstelle des `From` Benutzers |
| `transport` | Der/die Listening-Socket(s): Protokoll, Bind-Adresse/Port, NAT/externe Adressen |
| `registration` | Eine **ausgehende** REGISTER-Anfrage von Asterisk an einen Provider |

Die Unterscheidung zwischen `friend`/`peer`/`user` verschwindet vollständig — in PJSIP ist alles ein `endpoint`. Ein einzelner `sip.conf` friend wird daher typischerweise zu drei Objekten (`endpoint` + `auth` + `aor`), die einen Namen teilen und aufeinander verweisen:

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

Der endpoint ist das Bindeglied. Er benennt ein `transport` (oder erbt den Standard), ein `auth` Objekt und einen oder mehrere `aors`. Das Objektmodell wird in *SIP & PJSIP in depth* ausführlich behandelt; hier benötigen wir es nur als Ziel jeder Übersetzung.

## Das `sip_to_pjsip.py` Konvertierungstool

Asterisk liefert ein Python-Skript mit, das eine bestehende `sip.conf` liest und eine `pjsip.conf` schreibt. Es wird nicht als CLI-Befehl ausgeführt — es befindet sich im **Asterisk-Quellcode**, nicht in den installierten Binärdateien:

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Auf dem Asterisk 22.10.0 des Labors ist der vollständige Pfad zum Beispiel `/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`. Dasselbe Verzeichnis enthält `sip_to_pjsql.py` (die realtime/SQL-Variante, die später behandelt wird) und die Hilfsmodule `astconfigparser.py`, `astdicts.py` und `sqlconfigparser.py`.

### Ausführung

Das Skript akzeptiert optionale Positionsargumente — `[input-file [output-file]]` — die standardmäßig auf `sip.conf` und `pjsip.conf` im aktuellen Verzeichnis eingestellt sind:

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Seine einzigen wirklichen Optionen sind:

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

Es liest die Eingabe, gibt `Converting to PJSIP...` aus und schreibt die Ausgabedatei. Intern durchläuft es jeden `sip.conf` Abschnitt und erstellt pro Gerät die passenden `endpoint`, `auth`, `aor`, `registration` und (wo es sie ableiten kann) `transport` Objekte, wobei die Optionszuordnungen aus dem nächsten Abschnitt automatisch angewendet werden.

### Was es tut — und seine Grenzen

Betrachten Sie die Ausgabe als **ersten Entwurf, nicht als fertige Datei.** Das Skript ist ehrlich bezüglich seiner eigenen Lücken: Alles, was es nicht sauber zuordnen kann, wird in einen deutlich gekennzeichneten Block am Anfang der Ausgabedatei geschrieben:

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[zoiper]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

Beachten Sie in diesem realen Fragment, dass `qualify = yes` von einem `sip.conf` Peer im Block *non-mapped* gelandet ist — da PJSIP die Qualifizierung auf dem **aor** mit `qualify_frequency` (Sekunden) durchführt, nicht als boolescher Wert auf dem Gerät, überlässt das Skript es Ihnen, dies bewusst einzustellen. Die praktischen Einschränkungen, die Sie einplanen sollten:

- **Transportschichten werden geraten, nicht entworfen.** Das Skript erstellt einen einfachen `transport-udp` aus `bindport`/`bindaddr`, aber es kann Ihre TLS-Zertifikate, Ihre TCP-Anforderungen oder Ihr Multi-Bind-Layout nicht kennen. Überprüfen und schreiben Sie den Transport neu.
- **NAT und externe Adressen erfordern einen Menschen.** `externaddr`/`localnet` werden möglicherweise nicht sauber übernommen; bestätigen Sie `external_media_address`, `external_signaling_address` und `local_net` auf dem Transport manuell.
- **`qualify`, benutzerdefinierte Timer und eine Handvoll Optionen landen in "non-mapped".** Lesen Sie diesen Block von oben nach unten und entscheiden Sie für jeden Punkt.
- **Codec-Listen, Kontexte und Sicherheit müssen überprüft werden.** Verifizieren Sie `disallow`/`allow`, den dialplan `context` und stellen Sie sicher, dass kein Gerät unbeabsichtigt offen gelassen wurde.

Der Arbeitsablauf ist daher: Führen Sie das Skript in eine *Scratch*-Datei aus, vergleichen und überprüfen Sie diese, fügen Sie die guten Teile in Ihre echte `pjsip.conf` ein und testen Sie dann ausgiebig vor dem Produktivbetrieb.

## Direkte Übersetzungen

Dies sind die Rezepte. `sip.conf` auf der linken Seite, das verifizierte `pjsip.conf` Äquivalent auf der rechten Seite (hier für die Seitenbreite gestapelt). Jeder Optionsname und Wert auf der rechten Seite wurde mit dem Asterisk 22 Labor anhand von `config show help res_pjsip ...` überprüft.

### Ein registrierendes Telefon (`host=dynamic`)

Das häufigste Gerät: ein Tischtelefon oder softphone, das sich mit einem Geheimnis anmeldet und seinen eigenen Standort registriert.

**Legacy `sip.conf`:**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf`:**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

Wichtige Schritte: `host=dynamic` wird zu einem `aor` mit `max_contacts` (das Gerät führt ein REGISTER aus, um seinen Kontakt einzutragen); `secret=` wird zu `password=` innerhalb eines `type=auth`; `qualify=yes` wird zu `qualify_frequency=60` (Sekunden) auf dem **aor**, nicht auf dem endpoint. Setzen Sie `max_contacts` nur dann auf einen Wert größer als 1, wenn Sie wirklich dasselbe Konto auf mehreren Geräten gleichzeitig nutzen möchten.

### Ein eingehender trunk (`host=<ip>` / `type=peer`)

Ein Provider, der Ihnen Anrufe von einer bekannten IP-Adresse sendet. Hier findet keine Registrierung statt — Sie authentifizieren den *Datenverkehr des Anbieters anhand seiner Quell-IP* unter Verwendung von `identify`.

**Legacy `sip.conf`:**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

Die entscheidende Übersetzung ist **`insecure=invite` → `identify`**. In `chan_sip` wies `insecure=invite` Asterisk an: "Fordere bei eingehenden INVITEs von diesem Peer keine Authentifizierung an." PJSIP erreicht denselben Effekt, indem es die *Quell-IP mit dem endpoint abgleicht* mittels `type=identify`/`match=`, was sowohl expliziter als auch sicherer ist. Der statische `host=` wird zu einem permanenten `contact=` auf dem `aor`, sodass Sie auch *nach außen* zum Provider wählen können. `match=` akzeptiert eine IP, einen CIDR-Bereich oder einen Hostnamen (der zum Zeitpunkt des Konfigurationsladens aufgelöst wird — laden Sie neu, wenn sich die IP des Providers ändert).

### Eine ausgehende Registrierung (`register =>`)

Wenn der Provider möchte, dass *Sie* sich bei *ihm* anmelden, verwendete `chan_sip` eine einzelne `register =>` Zeile in `[general]`. PJSIP ersetzt dies durch ein dediziertes `type=registration` Objekt plus ein `outbound_auth`.

**Legacy `sip.conf`:**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

Ordnen Sie die `register =>` Felder eins zu eins zu: Die `1020:supersecret` Zugangsdaten werden zum `auth` Objekt (referenziert als `outbound_auth`); `@sip.example.com:5600` wird zum `server_uri`; das `/9999` Suffix — der Benutzerteil, an den der Provider eingehende Anrufe sendet — wird zu `contact_user=9999`. `defaultuser`/`fromuser` und `fromdomain` werden zu `from_user` und `from_domain` auf dem endpoint. Beachten Sie, dass `outbound_auth` *zweimal* erscheint: Die Registrierung verwendet es für das REGISTER, der endpoint verwendet es, um die `407` Herausforderung bei ausgehenden INVITEs zu beantworten.

## Migrationsreferenz Option für Option

Wenn Sie manuell übersetzen (oder die Ausgabe des Skripts prüfen), ist diese Tabelle Ihr Nachschlagewerk. Jeder PJSIP-Optionsname und die Platzierung (endpoint / aor / auth / transport) wurde anhand des Asterisk 22 Labors verifiziert.

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | Ort |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (Gerät führt REGISTER aus) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (auth method) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (gleiche Syntax) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | auth weglassen; `type=identify` + `match=` nutzen | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### Ein Hinweis zu `secret` → `auth` und `auth_type`

`chan_sip`s `secret=` wird zum `password=` Feld eines `type=auth` Objekts. Die **Authentifizierungsmethode** wird mit `auth_type` festgelegt. Verwenden Sie `auth_type=digest`. Die älteren Werte `userpass` und `md5` funktionieren zwar noch, sind aber **veraltet und werden stillschweigend in `digest` konvertiert** — direkt aus dem Labor verifiziert:

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

Sie werden `auth_type=userpass` in älteren Konfigurationen und in der Ausgabe des Konvertierungsskripts (sowie in früheren Kapiteln dieses Buches) sehen. Es ist harmlos, aber schreiben Sie `digest` in alles Neue.

### NAT, Medien und DTMF im Detail

Diese drei Punkte sind der Grund für die meisten Tickets nach der Migration vom Typ "es registriert sich, hat aber keinen Ton". Die `chan_sip` Kurzform `nat=force_rport,comedia` packte drei Verhaltensweisen in eine Option; PJSIP trennt sie, damit Sie über jede einzeln nachdenken können:

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

Für **Medien** wird `directmedia` zu `direct_media` (der Unterstrich ist die gesamte Änderung); behalten Sie `direct_media=no` bei, wann immer der Anruf auf Asterisk verankert werden muss — über NAT hinweg oder zum Aufzeichnen/Transkodieren/Weiterleiten. Für **DTMF** wurde die RFC neu nummeriert: `chan_sip`s `dtmfmode=rfc2833` ist PJSIPs `dtmf_mode=rfc4733` (derselbe Out-of-Band telephone-event Mechanismus, aktuelle RFC-Nummer). Das Labor bestätigt, dass die gültigen `dtmf_mode` Werte `rfc4733`, `inband`, `info`, `auto` und `auto_info` sind, mit dem Standardwert `rfc4733`.

Für **codecs** ändert sich nichts: `disallow=all` gefolgt von `allow=ulaw` (usw.) verwendet die identische Syntax auf dem PJSIP endpoint.

## Änderungen an dialplan und CLI

Die Migration endet nicht bei `pjsip.conf`. Zwei Dinge im täglichen Gebrauch ändern sich.

### Kanal-Strings: `SIP/` → `PJSIP/`

Jeder `Dial()` und Kanalverweis in `extensions.conf`, der die alte Technologie benannte, muss aktualisiert werden:

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Trunk-Wählstrings folgen demselben Muster — `Dial(SIP/${EXTEN}@itsp)` wird zu `Dial(PJSIP/${EXTEN}@itsp)`. PJSIP fügt auch die `PJSIP_DIAL_CONTACTS()` Funktion hinzu, um jeden Kontakt, der an eine AOR gebunden ist, gleichzeitig anzurufen, sowie die `PJSIP_HEADER()` / `PJSIP_MEDIA_OFFER()` dialplan-Funktionen; durchsuchen Sie Ihren dialplan nach `SIP/`, `SIPPEER`, `SIPCHANINFO` und `CHANNEL(...)` SIP-Verweisen und übersetzen Sie jeden.

### CLI: `sip show ...` → `pjsip show ...`

Der gesamte `sip ...` Befehlsbaum ist mit dem Treiber verschwunden. Die Ersatzbefehle:

| `chan_sip` Befehl | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (oder `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (oder `core reload`) |

Die alten Befehle verhalten sich nicht nur anders — sie existieren nicht mehr. Im Labor gibt `sip show peers` *No such command* zurück, während `pjsip show endpoints`, `pjsip show aors`, `pjsip show auths`, `pjsip show contacts`, `pjsip show registrations` und `pjsip show identifies` alle vorhanden sind. Der nützlichste Befehl zur Fehlerbehebung — der SIP-Paket-Logger, der jede Nachricht mit `sip set debug` ausgab — ist jetzt **`pjsip set logger on`** (mit `pjsip set logger host <ip>`, um sich auf einen Peer zu konzentrieren).

## Realtime (ARA) Migration

Wenn Sie `chan_sip` aus einer Datenbank (Asterisk Realtime Architecture) betrieben haben, befanden sich Ihre Geräte in der `sippeers` Tabelle und Registrierungen in `sipregs`. PJSIP verwendet eine völlig andere Speicherschicht — **Sorcery** — mit einer Tabelle *pro Objekttyp*. Die Zuordnung:

| `chan_sip` Realtime-Tabelle | PJSIP / Sorcery Tabelle(n) |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (jeweils eine Zeile, aufgeteilt) |
| `sipregs` | `ps_contacts` (dynamische Registrierungen) |
| — (ausgehend `register=>`) | `ps_registrations` |
| — (IP-Abgleich) | `ps_endpoint_id_ips` (die `identify` Objekte) |
| — (Domain-Aliase) | `ps_domain_aliases` |

Die konzeptionelle Aufteilung ist dieselbe wie beim Flat-File-Fall: Eine `sippeers` Zeile wird zu *drei* Zeilen in drei Tabellen (`ps_endpoints` + `ps_aors` + `ps_auths`), die sich gegenseitig über den endpoint-Namen referenzieren.

Zwei Dinge machen dies handhabbar:

- **Das Schema wird für Sie generiert.** Asterisk liefert Alembic-Migrationen unter `contrib/ast-db-manage/` mit, die jede `ps_*` Tabelle erstellen. Führen Sie `alembic upgrade head` gegen die `config` Datenbank aus, um das aktuelle PJSIP-Schema zu erstellen, anstatt DDL manuell zu schreiben.
- **Es gibt ein SQL-Konvertierungsskript.** Neben `sip_to_pjsip.py` befindet sich **`sip_to_pjsql.py`** im selben `contrib/scripts/sip_to_pjsip/` Verzeichnis; es verwendet dieselbe `convert()` Logik, gibt aber eine `pjsip.sql` Datei mit `INSERT` Anweisungen für die `ps_*` Tabellen aus, anstatt eine Flat-File-Konfiguration. Wie beim Flat-File-Tool gilt: Überprüfen Sie die Ausgabe, bevor Sie sie laden.

Zeigen Sie schließlich mit `sorcery.conf` auf Ihre Datenbank, damit PJSIP endpoints, aors, auths und Kontakte aus den `ps_*` Tabellen liest (via `res_config_odbc` / `res_pjsip_realtime`), genau wie `extconfig.conf` einst `sippeers` für `chan_sip` auf die Datenbank verwies. Die Realtime-Mechanik wird im Kapitel *Realtime* behandelt; der migrationsspezifische Punkt ist einfach, *welche Tabellen auf welche abgebildet werden*.

## Migrationscheckliste

Eine pragmatische Reihenfolge der Operationen für eine produktive Umstellung:

1. **Inventur.** Listen Sie jedes Gerät, jeden trunk und jedes `register =>` in `sip.conf` (oder jede `sippeers`/`sipregs` Zeile) auf. Notieren Sie benutzerdefinierte NAT-, codec- und DTMF-Einstellungen.
2. **Führen Sie den Konverter in eine Scratch-Datei aus.** `sip_to_pjsip.py sip.conf pjsip_generated.conf`. Zeigen Sie **nicht** auf Ihre aktive `pjsip.conf`.
3. **Lesen Sie den Block "Non mapped elements"** am Anfang der Ausgabe und lösen Sie jede Zeile auf — insbesondere `qualify`, Timer und alles, was mit NAT zu tun hat.
4. **Entwerfen Sie die Transportschicht(en) manuell.** Ein Transport pro IP/Port; fügen Sie TLS/TCP nach Bedarf hinzu; setzen Sie `external_*_address` und `local_net` für Cloud/NAT-Boxen.
5. **Überprüfen Sie die Authentifizierung.** Bestätigen Sie `auth_type=digest`, Benutzernamen und Passwörter auf jedem `auth` Objekt.
6. **Überprüfen Sie NAT/Medien/DTMF.** `force_rport`/`rewrite_contact`/`rtp_symmetric`, `direct_media`, `dtmf_mode=rfc4733` pro endpoint nach Bedarf.
7. **Aktualisieren Sie den dialplan.** `SIP/` → `PJSIP/` überall; überprüfen Sie `SIP*` Funktionen und Kanalvariablen.
8. **Aktualisieren Sie Skripte und Überwachung.** Jedes Tool oder jeder AMI-Consumer, der die Ausgabe von `sip show ...` geparst hat, muss auf `pjsip show ...` / PJSIP AMI-Aktionen umgestellt werden.
9. **Neu laden und verifizieren.** `module reload res_pjsip.so`, dann `pjsip show endpoints`, `pjsip show registrations`, `pjsip show identifies`.
10. **Testen Sie mit dem Paket-Logger.** `pjsip set logger on`; führen Sie eine Registrierung, einen eingehenden Anruf und einen ausgehenden Anruf durch und lesen Sie den SIP-Austausch von Anfang bis Ende.

## Häufige Fallstricke

- **`alwaysauthreject` ist jetzt eingebaut — suchen Sie nicht danach.** `chan_sip` benötigte `alwaysauthreject=yes`, damit nicht durch unterschiedliche Antworten auf falsche Benutzernamen durchsickerte, welche extensions existierten. PJSIP tut das Sicherere von Design her: Es verrät niemals, ob ein endpoint existiert. Es gibt keine `alwaysauthreject` Option zum Einstellen. Der zugehörige Schutz — das Drosseln nicht identifizierter Absender — ist die globale `unidentified_request_count` / `unidentified_request_period`, die standardmäßig aktiviert ist.

- **`insecure=invite` ist keine PJSIP-Option — verwenden Sie `identify`.** Es gibt kein `insecure=` in `pjsip.conf`. Der Weg, unauthentifizierte INVITEs von einem bekannten Provider zu akzeptieren, besteht darin, den *endpoint anhand der Quell-IP zu identifizieren* mit `type=identify` / `match=`. Gleichen Sie so eng wie möglich ab (spezifische Host-IPs, keine weiten CIDRs) und sichern Sie dies mit einem `type=acl` ab — ein IP-abgeglichener trunk ohne Authentifizierung ist ein Ziel für Gebührenbetrug.

- **Ein Transport pro IP/Port.** Sie können nicht zwei Transportschichten an dieselbe IP:Port binden, und Sie können nicht mehrere TCP- oder TLS-Transportschichten derselben IP-Version binden. Das Konvertierungsskript erstellt möglicherweise einen Transport, der mit einem bereits vorhandenen kollidiert — konsolidieren Sie dies zu einer einzigen, bewusst entworfenen Transportschicht.

- **`qualify=yes` lässt sich nicht in einen booleschen Wert übersetzen.** Er gehört auf den **aor** als `qualify_frequency=<seconds>`. Der Konverter verschiebt `qualify=yes` in den "non-mapped" Block, genau weil es keinen äquivalenten booleschen Wert auf dem endpoint gibt.

- **`secret=` ist keine endpoint-Option.** Zugangsdaten leben nur in einem `type=auth` Objekt, auf das der endpoint *verweist* (`auth=` für eingehend, `outbound_auth=` für ausgehend). Ein Passwort auf den endpoint zu setzen, bewirkt nichts.

- **Die CLI und alle Scraping-Skripte brechen stillschweigend.** `sip show ...` gibt "No such command" zurück, nicht unbedingt einen Fehler, den Ihre Überwachung abfängt. Prüfen Sie jeden Cronjob, Nagios-Check und AMI-Client auf `sip ` Befehle vor der Umstellung.

## Zusammenfassung

Die Migration auf Asterisk 22 bedeutet, von `chan_sip` wegzumigrieren, da der Treiber in Asterisk 21 entfernt wurde und PJSIP der einzige verbleibende SIP-Kanal ist. Der Kern der Arbeit besteht darin, jeden `sip.conf` `peer`/`user`/`friend` — der alles in einen Block packte — als eine Reihe zusammenarbeitender PJSIP-Objekte auszudrücken: ein `endpoint` plus ein `auth`, ein `aor` und, je nach Gerät, ein `identify` (eingehender trunk), ein `registration` (ausgehende Anmeldung) und ein gemeinsamer `transport`. Das `sip_to_pjsip.py` Skript in `contrib/scripts/sip_to_pjsip/` erledigt die Hauptübersetzung und markiert ehrlich, was es nicht zuordnen kann, in einem "Non mapped elements" Block, aber seine Ausgabe ist ein erster Entwurf: Entwerfen Sie Transport, NAT und Sicherheit manuell und testen Sie vor dem Produktivbetrieb. Aktualisieren Sie rund um die Konfiguration den dialplan (`SIP/` → `PJSIP/`) sowie Ihre Finger und Skripte (`sip show` → `pjsip show`, `sip set debug` → `pjsip set logger`). Realtime-Bereitstellungen ziehen von `sippeers`/`sipregs` auf die Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/`ps_contacts` Tabellen um, wobei `sip_to_pjsql.py` und das `contrib/ast-db-manage` Schema helfen. Achten Sie auf die Fallstricke — `alwaysauthreject` ist eingebaut, `insecure=invite` wird zu `identify`, `qualify=yes` wird zu `qualify_frequency` und ein Transport pro IP/Port — und die Umstellung ist eher mechanisch als mysteriös.

## Quiz

1. Warum muss eine Asterisk 22 Bereitstellung PJSIP für SIP verwenden?
   - A. `chan_sip` ist langsamer, aber noch verfügbar
   - B. `chan_sip` wurde in Asterisk 21 entfernt und existiert in Asterisk 22 nicht
   - C. PJSIP ist der Standard, aber `chan_sip` kann mit `modules.conf` geladen werden
   - D. `chan_sip` funktioniert in Asterisk 22 nur mit TLS

2. Ein einzelner `sip.conf` `type=friend` Block wird meistens zu welcher Gruppe von PJSIP-Objekten?
   - A. Ein einzelner `type=peer`
   - B. Nur `type=endpoint`
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. In `sip.conf` wird `host=dynamic` (das Gerät registriert seinen eigenen Standort) abgebildet auf:
   - A. `type=identify` mit `match=dynamic`
   - B. ein `type=aor` mit `max_contacts` (das Gerät führt ein REGISTER aus)
   - C. `direct_media=yes` auf dem endpoint
   - D. `type=registration`

4. Das `sip_to_pjsip.py` Konvertierungsskript ist:
   - A. Ein CLI-Befehl: `asterisk -rx 'sip_to_pjsip'`
   - B. Ein Python-Skript im Asterisk-Quellcode unter `contrib/scripts/sip_to_pjsip/`
   - C. Ein kompiliertes Modul, das beim Booten geladen wird
   - D. Teil von `res_pjsip.so`

5. Wahr oder Falsch: Die Ausgabe von `sip_to_pjsip.py` ist produktionsbereit und sollte ohne Überprüfung geladen werden.

6. Die `chan_sip` Kurzform `nat=force_rport,comedia` übersetzt sich auf einem PJSIP endpoint in welche drei Optionen?
   - A. `nat=yes`, `qualify=yes`, `directmedia=no`
   - B. `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes`
   - C. `external_media_address`, `external_signaling_address`, `local_net`
   - D. `insecure=invite`, `identify`, `match`

7. `sip.conf`s `dtmfmode=rfc2833` wird zu welcher PJSIP-Einstellung?
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. Auf Asterisk 22 sollte ein `auth` Objekt welches `auth_type` verwenden, und was ist der Status von `userpass`?
   - A. `auth_type=userpass`; es ist der einzige gültige Wert
   - B. `auth_type=digest`; `userpass` ist veraltet und wird in `digest` konvertiert
   - C. `auth_type=md5`; `digest` ist veraltet
   - D. `auth_type=plaintext`; `digest` wurde entfernt

9. Ein `chan_sip` Provider-Peer mit `insecure=invite` (akzeptiere unauthentifizierte INVITEs von einer bekannten IP) wird auf PJSIP migriert mittels:
   - A. `insecure=invite` auf dem endpoint
   - B. `allowguest=yes` in `[global]`
   - C. ein `type=identify` Objekt mit `match=<provider IP>`
   - D. `auth_type=anonymous`

10. Bei einer Realtime-Migration wird die `chan_sip` `sippeers` Tabelle ersetzt durch welche PJSIP/Sorcery-Tabellen?
    - A. Eine einzelne `pjsip_peers` Tabelle
    - B. `ps_endpoints`, `ps_aors` und `ps_auths`
    - C. `sipregs` und `voicemail`
    - D. Nur `ps_contacts`

**Antworten:** 1 — B · 2 — C · 3 — B · 4 — B · 5 — Falsch · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
