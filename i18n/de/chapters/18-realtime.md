# Asterisk Real-Time

Wie Sie wissen, erfolgt die Konfiguration von Asterisk über verschiedene Textdateien im Verzeichnis /etc/asterisk. Trotz der Einfachheit der Verwendung von Textdateien gibt es einige bekannte Nachteile:

- Die Notwendigkeit, Asterisk bei jeder Änderung der Dateien neu zu laden
- Erhöhter Speicherverbrauch bei einer großen Anzahl von Benutzern
- Es ist schwierig, eine Provisionierungsschnittstelle unter Verwendung von Textdateien zu programmieren
- Keine Möglichkeit der Integration in bestehende Datenbanken

ARA oder Asterisk Realtime, wie es genannt wird, wurde von Anthony Minessale II, Mark Spencer und Constantine Filin entwickelt und konzipiert, um eine transparente Integration mit SQL-Datenbanken zu ermöglichen. Eine LDAP-Schnittstelle ist ebenfalls verfügbar. Dieses System ist auch als Asterisk External Configuration bekannt und wird in /etc/asterisk/extconfig.conf konfiguriert. Sie können Konfigurationsdateien auf Tabellen in einer Datenbank abbilden (statische Konfiguration) sowie Echtzeit-Einträge für die dynamische Erstellung von Objekten verwenden, ohne Asterisk neu laden zu müssen.

## Ziele

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Die Vorteile und Einschränkungen von Asterisk Real Time zu verstehen.
- ODBC für die Verwendung mit ARA zu nutzen.
- ARA unter Verwendung von ODBC zu kompilieren und zu installieren.
- Das System in einer Laborumgebung zu testen.

## Wie funktioniert Asterisk Real Time?

In der neuen Real-Time-Architektur wurde der gesamte datenbankspezifische Code in Channel-Treiber verschoben. Der Channel ruft lediglich eine generische Routine auf, die die Datenbank durchsucht. Das Ergebnis ist ein wesentlich einfacherer und saubererer Prozess aus Sicht des Quellcodes. Auf die Datenbank wird über drei Funktionen zugegriffen:

- STATIC: Wird verwendet, um eine statische Konfiguration einzurichten, wenn ein Modul geladen wird.
- REALTIME: Wird verwendet, um Objekte während eines Anrufs oder eines anderen Ereignisses zu suchen.


- UPDATE: Wird verwendet, um Objekte zu aktualisieren.

Unter Asterisk 22 werden SIP-Endpoints vom **PJSIP**-Stack (`res_pjsip`) verarbeitet, der auf dem **Sorcery**-Objektmodell aufbaut. Mit dem `realtime`-Wizard lädt Sorcery jedes PJSIP-Objekt bei Bedarf aus der Datenbank, und diese Objekte existieren dann als gewöhnliche, konfigurierte PJSIP-Objekte — nicht als die kurzlebigen Realtime-Peers, die der alte SIP-Treiber nach jedem Anruf verwarf. Da es sich um echte Objekte handelt, funktionieren NAT-Traversal, Qualify und Message Waiting Indication (MWI) für Realtime-Endpoints ganz normal. (Sorcery kann zusätzlich angewiesen werden, Objekte über einen `memory_cache`-Wizard im Speicher zwischenzuspeichern, aber das ist optional und vom Realtime-Ladevorgang getrennt.) Wenn Sie ein Objekt in der Datenbank ändern, wird die Änderung beim nächsten Suchvorgang übernommen; Sie müssen nicht nach jeder Bearbeitung neu laden. (Das ausgemusterte `chan_sip`-Realtime-Modell mit seinen `sippeers`/`sipusers`-Familien wird nur im Kapitel *Legacy Channels* behandelt.)

## Konfigurieren von Asterisk Real Time

Für dieses Labor setzen wir voraus, dass Sie ODBC bereits aus dem CDR-Kapitel installiert haben. ARA wird in der Textdatei extconfig.conf konfiguriert, in der zwei Abschnitte leicht zu erkennen sind. Der erste ist der Abschnitt für statische Konfigurationsdateien, in dem Sie die Textkonfigurationsdateien durch Datenbanktabellen ersetzen können. Der zweite Abschnitt ist die Realtime-Konfigurations-Engine, in der Sie Datenbanktabellen für dynamische Objekte (Peers/Benutzer) konfigurieren. Es ist nicht ungewöhnlich, Textdateien für die statische Konfiguration und die Datenbank für dynamische Einträge zu verwenden. In diesem Fall bleibt der erste Abschnitt unangetastet.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time-Architektur: Konfigurationsdateien und statische Datenbanktabellen werden beim Start von Asterisk geladen, während Realtime-Datenbanktabellen eine dynamische Konfiguration bereitstellen, die während eines Anrufs bei Bedarf gelesen wird.](../images/18-realtime-fig01.png)

```
;
[settings]
;
; Static configuration files:
;
; file.conf => driver,database[,table]
;
; maps a particular configuration file to the given
; database driver, database and table (or uses the
; name of the file as the table if not specified)
;
;uncomment to load queues.conf via the odbc engine.
;
;queues.conf => odbc,asterisk,ast_config
;
; The following files CANNOT be loaded from Realtime storage:
;       asterisk.conf
;       extconfig.conf (this file)
;       logger.conf
;
; Additionally, the following files cannot be loaded from
; Realtime storage unless the storage driver is loaded
; early using 'preload' statements in modules.conf:
;       manager.conf
;       cdr.conf
;       rtp.conf
;
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
;example => odbc,asterisk,alttable
;ps_endpoints => odbc,asterisk
;ps_aors => odbc,asterisk
;ps_auths => odbc,asterisk
;ps_contacts => odbc,asterisk
;voicemail => odbc,asterisk
;extensions => odbc,asterisk
;queues => odbc,asterisk
;queue_members => odbc,asterisk
```


### Abschnitt für statische Konfiguration

Der Abschnitt für die statische Konfiguration ist der Ort, an dem Sie das Äquivalent zu Konfigurationsdateien in der Datenbank speichern. Diese Konfigurationen werden während des Asterisk-Ladevorgangs gelesen. Einige Module lesen die Datenbank erneut, wenn Sie einen Reload durchführen. Beispiele für die statische Konfiguration sind:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

Das Mapping statischer Dateien ist am nützlichsten für Konfigurationsdateien, die kein objektbezogenes Realtime-Äquivalent haben. Bevorzugen Sie für PJSIP die objektbezogenen Realtime-Familien (`ps_endpoints`, `ps_aors` usw.), die später in diesem Kapitel beschrieben werden, anstatt die gesamte `pjsip.conf` als statische Datei abzubilden.

Oben sind drei Beispiele beschrieben. Im ersten binden Sie queues.conf an eine Tabelle queues in der Datenbank asteriskdb. Im zweiten Beispiel binden Sie pjsip.conf an die Tabelle pjsip_conf in der Datenbank asteriskdb, die in der ODBC-Konfiguration definiert ist. Im letzten Beispiel binden Sie iax.conf an ein LDAP-Verzeichnis. MyBaseDN ist der Basis-DN, der durchsucht werden soll. Im vorherigen Beispiel wird die Anwendung app_queue.so geladen, während der MySQL-Treiber die Datenbank abfragt und die erforderlichen Informationen abruft.

### Abschnitt für Real-Time-Konfiguration

Die Real-Time-Konfiguration (zweiter Teil der Datei extconfig.conf) ist der Ort, an dem das zu ladende Konfigurationsstück in Echtzeit konfiguriert, aktualisiert und entladen wird. Mit Real Time ist es nicht erforderlich, die Konfigurationen neu zu laden. Die Real-Time-Syntax lautet wie folgt:

```
<family name> => <driver>,<database name>[,table_name]
```

Beispiel:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Hier haben wir fünf Konfigurationszeilen. In der ersten Zeile binden Sie die PJSIP/Sorcery-Familie `ps_endpoints` an eine Tabelle `ps_endpoints` in der Datenbank asteriskdb. In der letzten binden Sie die Voicemail-Familie an die Tabelle test in der Datenbank asteriskdb. Jeder PJSIP-Objekttyp (endpoint, aor, auth, contact) erhält seine eigene Familie und Tabelle; der vollständige Satz wird im Abschnitt "PJSIP Realtime (Sorcery)" unten gezeigt. Die Familien `voicemail`, `extensions`, `queues` und `queue_members` sind in Asterisk 22 weiterhin gültig.

## PJSIP Realtime (Sorcery)

Unter Asterisk 22 werden SIP-Endpoints ausschließlich vom **PJSIP**-Stack (`res_pjsip`) verarbeitet, der auf der **Sorcery**-Objekt-Abstraktionsschicht aufbaut. Anstatt eines einzelnen SIP-"Peers" unterteilt PJSIP ein SIP-Konto in mehrere Objekttypen, die jeweils in ihrer eigenen Realtime-Tabelle gespeichert werden:

| Sorcery-Objekttyp | Realtime-Tabelle | Inhalt |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | Kontoeinstellungen (context, codecs, DTMF, etc.) |
| aor (address of record) | ps_aors | Registrierungslimits und `qualify`-Einstellungen |
| auth | ps_auths | `username` / `password`-Anmeldedaten |
| contact | ps_contacts | der dynamisch registrierte Standort |
| domain alias | ps_domain_aliases | alternative SIP-Domains für einen Endpoint |
| endpoint identifier by IP | ps_endpoint_id_ips | Abgleich eines Endpoints anhand der Quell-IP |

Realtime für PJSIP wird an zwei Stellen aktiviert. Zuerst bilden Sie die Sorcery-Objekttypen in `extconfig.conf` auf Realtime ab:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Zweitens weisen Sie Sorcery an, den `realtime`-Wizard für diese Objekttypen in `sorcery.conf` zu verwenden. Der Mapping-Name (hier `res_pjsip`) ist das Modul, dessen Objekte Sie verschieben, und der Wert auf der rechten Seite verweist auf die Familie, die Sie in `extconfig.conf` definiert haben:

```
[res_pjsip]
endpoint=realtime,ps_endpoints
aor=realtime,ps_aors
auth=realtime,ps_auths
domain_alias=realtime,ps_domain_aliases
contact=realtime,ps_contacts

[res_pjsip_endpoint_identifier_ip]
identify=realtime,ps_endpoint_id_ips
```

Sie können statische und Realtime-Objekte mischen. Wenn Sie einen Typ in `sorcery.conf` weglassen, liest dieser Objekttyp weiterhin aus `pjsip.conf`. Ein gängiges Muster ist es, statische Transports und globale Einstellungen in `pjsip.conf` zu belassen, während Endpoints, AORs, Auths und Contacts in der Datenbank gespeichert werden.

### Erstellen des PJSIP-Realtime-Schemas mit Alembic

Asterisk liefert Datenbankmigrationen für alle seine Realtime-Schemas unter `contrib/ast-db-manage` aus. Dies ist der unterstützte Weg, um PJSIP-Tabellen zu erstellen (und Versions-Upgrades durchzuführen) — Sie schreiben die `ps_*`-Tabellendefinitionen nicht mehr von Hand. Der Migrationssatz `config` enthält die PJSIP/Sorcery-Tabellen.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Dies erstellt `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` und die anderen PJSIP-Tabellen mit den korrekten Spalten für die laufende Asterisk-Version. (Alembic erfordert das Python-Paket `alembic` sowie einen SQLAlchemy-Treiber wie `pymysql` für MySQL/MariaDB oder `psycopg2` für PostgreSQL.)

Ein minimaler Realtime-Endpoint besteht dann aus einer Zeile in jeder der drei Tabellen — zum Beispiel Endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Nach dem Einfügen der Zeilen muss nichts neu geladen werden — das nächste REGISTER/INVITE zieht die Objekte aus der Datenbank. Sie können mit folgendem Befehl überprüfen, was Realtime zurückgegeben hat:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Datenbankkonfiguration

Nachdem wir nun die Datei extconfig.conf konfiguriert haben, erstellen wir die Tabellen. Im Allgemeinen entspricht jede Datenbankspalte einem Optionsnamen aus der entsprechenden Konfigurationsdatei. Die PJSIP-Tabellen `ps_*` folgen dieser Regel: Jede `ps_endpoints`-Spalte ist nach einer `pjsip.conf`-Endpoint-Option benannt, jede `ps_auths`-Spalte nach einer Auth-Option und so weiter. Zum Beispiel der `pjsip.conf`-Endpoint unten,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

wird als eine Zeile über drei Tabellen hinweg gespeichert. Die `ps_endpoints`-Zeile enthält `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; die `ps_auths`-Zeile enthält `id=4000, auth_type=userpass, username=4000, password=supersecret`; und die `ps_aors`-Zeile enthält `id=4000, max_contacts=1`. Sie müssen nur die Spalten ausfüllen, die Sie tatsächlich verwenden — jede Spalte, die Sie NULL lassen, greift auf den Standardwert der Option zurück. Wenn Sie zum Beispiel den Parameter `callerid` an einem Endpoint wünschen, füllen Sie die `callerid`-Spalte von `ps_endpoints` aus (der Spaltenname ist derselbe wie der `pjsip.conf`-Optionsname).

Eine Voicemail-Tabelle folgt der gleichen Idee. Ihre Spalten werden auf die `voicemail.conf`-Felder abgebildet:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

Die `uniqueid` sollte für jeden Voicemail-Benutzer eindeutig sein und kann ein Autoincrement sein. Sie muss keine Beziehung zur Mailbox oder zum Context haben.

### Erstellen eines Dialplans unter Verwendung von Asterisk Real Time

Sie können das Real-Time-System auch verwenden, um den Dialplan zu erstellen. ARA verwendet die Anweisung `switch`, um die Realtime-Extensions in den normalen Dialplan einzubinden, der in der Datei extensions.conf enthalten ist. Die Extension-Tabelle sollte wie folgt aussehen:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

Die Realtime-Familie `extensions` ist in Asterisk 22 unverändert; stellen Sie nur sicher, dass die `appdata`-Spalte PJSIP-Channels anwählt, zum Beispiel `PJSIP/4000`. Im Dialplan müssen Sie den Befehl `switch` verwenden, um Real Time zu nutzen.

![Erstellen eines Dialplans mit Asterisk Real Time: extensions.conf verwendet eine `switch => realtime`-Anweisung, um Extension-Zeilen (context, exten, priority, app, data) aus einer Datenbanktabelle zu ziehen, anstatt aus der Textdatei.](../images/18-realtime-fig02.png)


```
[local]
switch => realtime
```

oder

```
[local]
switch => realtime/from-internal@extensions
```

## Labor: Installieren und Erstellen der Datenbanktabellen

In diesem Labor bereiten wir die Datenbank darauf vor, Asterisk-Parameter zu empfangen. Wir bereiten nur die REALTIME-Tabellen vor. Die statische Konfiguration wird den Textkonfigurationsdateien überlassen (cool, oder?). Die Tabellenerstellung in MySQL folgt.

Schritt 1: Melden Sie sich als Root bei der MySQL-Datenbank an.

```
mysql –u root –p
```

Schritt 2: Melden Sie sich bei dem MySQL-Server an, der in den CDR-Laboren erstellt wurde.

```
mysql –u astdb –p
```

Wenn Sie nach dem Passwort gefragt werden, geben Sie supersecret ein.

Schritt 3: Erstellen Sie die notwendigen Tabellen. Die alten statischen Schemadateien werden immer noch unter `contrib/realtime/` ausgeliefert (zum Beispiel `/usr/src/asterisk-22.x/contrib/realtime/mysql`), aber unter Asterisk 22 ist der empfohlene und versionskorrekte Weg, die Realtime-Tabellen zu erstellen — insbesondere die PJSIP-Tabellen `ps_*` — die **Alembic**-Migrationen unter `contrib/ast-db-manage` (siehe Abschnitt "Erstellen des PJSIP-Realtime-Schemas mit Alembic" oben).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Der Alembic-Migrationssatz `config` erstellt die PJSIP-Tabellen `ps_*` (zusammen mit `voicemail`, `extensions` und den anderen Realtime-Schemas) mit genau den Spalten, die die laufende Asterisk-Version erwartet, sodass das Schema immer mit dem Build übereinstimmt.

Verwenden Sie supersecret als Passwort.

Schritt 4: Überprüfen Sie die Erstellung der Tabellen.

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

Sie sollten die PJSIP-Tabellen `ps_*` (erstellt durch die Alembic-Migration `config`) zusammen mit den Realtime-Tabellen `voicemail`, `extensions` und anderen sehen:

```
mysql> show tables;
+----------------------------+
| Tables_in_astdb            |
+----------------------------+
| ps_aors                    |
| ps_auths                   |
| ps_contacts                |
| ps_domain_aliases          |
| ps_endpoint_id_ips         |
| ps_endpoints               |
| ps_registrations           |
| extensions                 |
| voicemail                  |
+----------------------------+
```

(Alembic erstellt mehr Tabellen als diese — die Liste oben zeigt die für dieses Labor relevanten.)

Schritt 5: Die Datenbank ist bereits für ODBC konfiguriert (seit dem CDR-Labor), daher ist hier keine weitere ODBC-Einrichtung erforderlich.

Schritt 6: Installieren Sie phpMyAdmin, um Datenbankaufgaben zu erledigen.

```
apt-get install phpmyadmin
```

Unten sehen Sie zwei Screenshots des Anmeldebildschirms und des Tabellenbildschirms des Dienstprogramms. Verwenden Sie astdb/supersecret als Name und Passwort.

> **[2nd-ed note]** Ersetzen Sie dies durch einen aktuellen Screenshot der Datenbankverwaltung (phpMyAdmin/Adminer) oder wandeln Sie diese Schritte in reines SQL (CREATE TABLE/INSERT) um.

## Labor: Konfigurieren und Testen von ARA

In diesem Labor ändern wir die Konfiguration in extconfig.conf, um unsere Datenbankkonfiguration und Tabellen widerzuspiegeln.

Schritt 1: Konfigurieren Sie extconfig.conf und laden Sie Asterisk neu.

```
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
ps_endpoints => odbc,cdr
ps_aors => odbc,cdr
ps_auths => odbc,cdr
ps_contacts => odbc,cdr
voicemail => odbc,cdr,voicemail
extensions => odbc,cdr,extensions
```

Beachten Sie die Familien `ps_endpoints`, `ps_aors`, `ps_auths` und `ps_contacts` oben; zusammen mit den passenden `sorcery.conf`-Mappings (siehe Abschnitt "PJSIP Realtime (Sorcery)") sorgen sie dafür, dass PJSIP seine Konten aus der Datenbank liest. Die Familien `voicemail` und `extensions` runden das Beispiel ab.

Schritt 2: Real-Time-Extension-Test. Erstellen Sie mit phpMyAdmin einen neuen `6010`-Endpoint, indem Sie jeweils eine Zeile in `ps_auths`, `ps_aors` und `ps_endpoints` einfügen, und versuchen Sie dann, diesen Endpoint mit einem Softphone zu registrieren.

```
-- ps_auths
id=6010-auth, auth_type=userpass, username=6010, password=supersecret
-- ps_aors
id=6010, max_contacts=1
-- ps_endpoints
id=6010, transport=transport-udp, aors=6010, auth=6010-auth
```

> **[2nd-ed note]** Ersetzen Sie dies durch einen aktuellen Screenshot der Datenbankverwaltung (phpMyAdmin/Adminer) oder wandeln Sie diese Schritte in reines SQL (CREATE TABLE/INSERT) um.

Die restlichen Kontoeinstellungen sind auf die PJSIP-Objekte verteilt. Context, Codecs, DTMF-Modus und Medienverarbeitung befinden sich auf dem Endpoint; die dynamische Registrierung befindet sich auf dem AOR:

```
-- ps_endpoints columns for 6010
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
-- ps_aors: dynamic registration is implicit; the AOR accepts
--          registrations and the contact is written to ps_contacts
```

In PJSIP heißt der DTMF-Modus RFC 2833 / RFC 4733 `rfc4733` (`dtmf_mode=rfc4733`, der Standard). Es gibt kein separates "dynamisches" Flag für die Registrierung: Ein AOR akzeptiert dynamische REGISTER, solange er mindestens einen Kontakt zulässt (`max_contacts` größer als null), und jeder registrierte Standort wird in `ps_contacts` geschrieben.

Schritt 3: Versuchen Sie, das neue Telefon mit einem Softphone unter Verwendung des Benutzernamens `6010` und des Passworts `supersecret` zu registrieren. Bestätigen Sie die Registrierung auf der Asterisk-CLI:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Schritt 4: Fügen Sie die Extensions in die Datenbank ein.

```
mysql -u astdb -p
```

Passwort eingeben:

Verwenden Sie supersecret, wenn Sie dazu aufgefordert werden. Verwenden Sie phpMyAdmin, um eine Extension in die Datenbank aufzunehmen. Wenn Sie möchten, verwenden Sie stattdessen die folgenden Befehle im MySQL-Client-Interface.

```
use astdb;
insert into extensions(id, context, exten, priority, app, appdata) VALUES
('1','test', '6007','1','Dial','PJSIP/bria');
```

Schritt 5: Binden Sie Asterisk Real Time in den Dialplan ein. Im Context `default`:

```
switch => realtime/test@extensions
```

Laden Sie die Extensions neu, um die Änderung zu aktivieren.

```
asterisk-server*CLI>extensions reload
```

Schritt 6: Konfigurieren Sie eines der Telefone auf den Benutzernamen `bria` um, falls Sie dies noch nicht getan haben.

Schritt 7: Wählen Sie 6007 von einem bestehenden Telefon aus; das `bria`-Telefon sollte klingeln.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Asterisk Real Time es Ihnen ermöglicht, Ihre Konfigurationen in einer Datenbank abzulegen. Asterisk liefert native Realtime-Treiber für ODBC (das jede von UnixODBC unterstützte Datenbank erreicht, einschließlich MySQL/MariaDB und SQLite), MySQL und PostgreSQL sowie einen LDAP-Realtime-Treiber für Verzeichnis-Backends. Die Konfiguration ist in statisch und Real Time unterteilt. Die statische Konfiguration ersetzt die Konfigurationsdateien, während die Real-Time-Konfiguration dynamische Objekte erstellt, die nur geladen werden, wenn ein Anruf oder ein anderes zugehöriges Ereignis eintritt. Wir schlossen mit einem praktischen Labor zur Installation und Konfiguration von ARA ab.

## Quiz

1. Asterisk Realtime ist Teil der Standard-Asterisk-Distribution.
   - A. Wahr
   - B. Falsch
2. Die Verbindungsparameter eines Datenbankservers werden in der folgenden Datei konfiguriert:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. Die Datei `extconfig.conf` konfiguriert die von Realtime verwendeten Tabellen. Sie hat zwei verschiedene Abschnitte (zwei ankreuzen):
   - A. Statische Konfiguration
   - B. Realtime-Konfiguration
   - C. Ausgehende Routen
   - D. IP-Adressen und Datenbank-Ports
4. In der statischen Konfiguration werden die Objekte nach dem Laden aus der Datenbank im Speicher von Asterisk gehalten und nur beim Start oder Reload aktualisiert.
   - A. Wahr
   - B. Falsch
5. PJSIP Realtime (Sorcery) unterstützt `qualify` und MWI für Realtime-Endpoints vollständig, da Sorcery sie als gewöhnliche, konfigurierte PJSIP-Objekte lädt, anstatt sie nach jedem Anruf zu verwerfen, wie es die alten SIP-Realtime-Peers taten.
   - A. Wahr
   - B. Falsch
6. Welche Tabellen enthalten in PJSIP Realtime die Endpoints und ihre registrierten Kontakte?
   - A. `ps_endpoints` und `ps_contacts`
   - B. `ps_peers` und `ps_registry`
   - C. `ps_config` und `ps_data`
   - D. `extconfig` und `res_odbc`
7. Sie können weiterhin Textkonfigurationsdateien verwenden, auch nachdem Sie ARA aktiviert haben.
   - A. Wahr
   - B. Falsch
8. phpMyAdmin ist zwingend erforderlich, wenn Sie Realtime verwenden.
   - A. Wahr
   - B. Falsch
9. Die Datenbank muss mit jedem Feld erstellt werden, das in der Konfigurationsdatei existiert.
   - A. Wahr
   - B. Falsch
10. Was ist unter Asterisk 22 der empfohlene, versionskorrekte Weg, um die PJSIP-Realtime-Tabellen (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`) zu erstellen?
    - A. Schreiben Sie die `CREATE TABLE`-Anweisungen für jede `ps_*`-Tabelle von Hand
    - B. Importieren Sie die Legacy-`mysql_config.sql` aus `contrib/realtime/`
    - C. Führen Sie die Alembic-Migrationen `config` unter `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`) aus
    - D. Die Tabellen werden automatisch beim ersten Start von Asterisk erstellt

**Antworten:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
