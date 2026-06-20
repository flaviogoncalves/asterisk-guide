# Asterisk Echtzeit

Wie Sie wissen, wird die Asterisk‑Konfiguration durch die Verwendung mehrerer Textdateien im Verzeichnis /etc/asterisk erreicht. Trotz der Einfachheit von Textdateien gibt es einige bekannte Nachteile:

- Die Notwendigkeit, Asterisk jedes Mal neu zu laden, wenn die Dateien geändert werden
- Erhöhter Speicherverbrauch bei einer großen Benutzerzahl
- Es ist schwierig, eine Bereitstellungsschnittstelle mit Textdateien zu programmieren
- Keine Möglichkeit zur Integration in bestehende Datenbanken

ARA oder Asterisk Realtime, wie es genannt wird, wurde von Anthony Minessale II, Mark Spencer und Constantine Filin erstellt und wurde entwickelt, um eine transparente Integration mit SQL‑Datenbanken zu ermöglichen. Eine LDAP‑Schnittstelle ist ebenfalls verfügbar. Dieses System ist auch als Asterisk External Configuration bekannt und wird in /etc/asterisk/extconfig.conf konfiguriert. Sie können Konfigurationsdateien Tabellen in einer Datenbank zuordnen (statische Konfiguration) und Echtzeit‑Einträge für die dynamische Erstellung von Objekten, ohne Asterisk neu laden zu müssen.

## Ziele

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Die Vorteile und Einschränkungen von Asterisk Real Time verstehen.
- ODBC für die Verwendung mit ARA nutzen
- ARA mit ODBC kompilieren und installieren
- Das System in einer Laborumgebung testen

## Wie funktioniert Asterisk Real Time?

In der neuen Real‑Time‑Architektur wurde der datenbankspezifische Code zu den Kanal‑Treibern verschoben. Der Kanal ruft nur eine generische Routine auf, die die Datenbank durchsucht. Das Ergebnis ist aus Sicht des Quellcodes ein wesentlich einfacher‑ und sauberer‑er Prozess. Auf die Datenbank wird über drei Funktionen zugegriffen:

- STATIC: Wird verwendet, um eine statische Konfiguration beim Laden eines Moduls einzurichten.
- REALTIME: Wird verwendet, um Objekte während eines Anrufs oder eines anderen Ereignisses zu suchen.


- UPDATE: Wird verwendet, um Objekte zu aktualisieren.

Auf Asterisk 22 werden SIP‑Endpunkte vom **PJSIP**‑Stack (`res_pjsip`) verarbeitet, der auf dem **Sorcery**‑Objektmodell aufbaut. Mit dem `realtime`‑Assistenten lädt Sorcery jedes PJSIP‑Objekt bei Bedarf aus der Datenbank, und diese Objekte existieren dann als gewöhnliche konfigurierte PJSIP‑Objekte – nicht als die flüchtigen Real‑Time‑Peers, die der alte SIP‑Treiber nach jedem Anruf verworfen hat.

Da es sich um echte Objekte handelt, funktionieren NAT‑Traversal, Qualify und Message‑Waiting‑Indication (MWI) für Real‑Time‑Endpunkte normal. (Sorcery kann zusätzlich angewiesen werden, Objekte über einen `memory_cache`‑Assistenten im Speicher zu cachen, aber das ist optional und getrennt vom Real‑Time‑Laden.) Wenn Sie ein Objekt in der Datenbank ändern, wird die Änderung beim nächsten Lookup übernommen; ein erneutes Laden nach jeder Bearbeitung ist nicht nötig. (Das eingestellte `chan_sip`‑Real‑Time‑Modell mit seinen `sippeers`/`sipusers`‑Familien wird nur im Kapitel *Legacy Channels* behandelt.)

## Configuring Asterisk Real Time

Für dieses Labor gehen wir davon aus, dass Sie ODBC bereits aus dem CDR‑Kapitel installiert haben. ARA wird in der Textdatei extconfig.conf konfiguriert, wo zwei Abschnitte leicht zu erkennen sind. Der erste ist der Abschnitt für statische Konfigurationsdateien, in dem Sie die Text‑Konfigurationsdateien durch Datenbanktabellen ersetzen können. Der zweite Abschnitt ist die Realtime‑Konfigurations‑Engine, in der Sie Datenbanktabellen für dynamische Objekte (Peers/Benutzer) konfigurieren. Es ist nicht ungewöhnlich, Textdateien für die statische Konfiguration und die Datenbank für dynamische Einträge zu verwenden. In diesem Fall bleibt der erste Abschnitt unverändert.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time‑Architektur: Konfigurationsdateien und statische Datenbanktabellen werden beim Start von Asterisk geladen, während Realtime‑Datenbanktabellen die dynamische Konfiguration bereitstellen, die bei Bedarf während eines Anrufs gelesen wird.](../images/18-realtime-fig01.png)

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

### Static configuration section

Der Abschnitt für statische Konfiguration ist dort, wo Sie das Äquivalent zu Konfigurationsdateien in der Datenbank speichern. Diese Konfigurationen werden beim Laden von Asterisk gelesen. Einige Module lesen die Datenbank erneut, wenn Sie sie neu laden. Beispiele für die statische Konfiguration sind:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

Die Zuordnung von statischen Dateien ist am nützlichsten für Konfigurationsdateien, die kein per‑Objekt Realtime‑Äquivalent besitzen. Für PJSIP sollten Sie die per‑Objekt Realtime‑Familien (`ps_endpoints`, `ps_aors` usw.) verwenden, die später in diesem Kapitel beschrieben werden, anstatt die gesamte `pjsip.conf` als statische Datei zuzuordnen.

Drei Beispiele wurden oben beschrieben. Im ersten binden Sie queues.conf an die Tabelle queues in der Datenbank asteriskdb. Im zweiten Beispiel binden Sie pjsip.conf an die Tabelle pjsip_conf in der Datenbank asteriskdb, die in der ODBC‑Konfiguration definiert ist. Im letzten Beispiel binden Sie iax.conf an ein LDAP‑Verzeichnis. MyBaseDN ist der zu durchsuchende Basis‑DN. Im vorherigen Beispiel wird das Modul app_queue.so geladen, während der MySQL‑Treiber die Datenbank abfragt und die benötigten Informationen erhält.

### Real Time configuration section

Der Realtime‑Konfigurationsabschnitt (zweiter Teil der extconfig.conf‑Datei) ist dort, wo das zu ladende Konfigurationselement in Echtzeit konfiguriert, aktualisiert und entladen wird. Mit Realtime ist es nicht nötig, die Konfigurationen neu zu laden. Die Realtime‑Syntax lautet:

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

Hier haben wir fünf Konfigurationszeilen. In der ersten Zeile binden Sie die PJSIP/Sorcery‑Familie `ps_endpoints` an die Tabelle `ps_endpoints` in der Datenbank asteriskdb. In der letzten Zeile binden Sie die voicemail‑Familie an die Test‑Tabelle in der Datenbank asteriskdb. Jeder PJSIP‑Objekttyp (endpoint, aor, auth, contact) erhält seine eigene Familie und Tabelle; das vollständige Set ist im Abschnitt „PJSIP Realtime (Sorcery)“ unten dargestellt. Die Familien `voicemail`, `extensions`, `queues` und `queue_members` sind weiterhin in Asterisk 22 gültig.

## PJSIP Realtime (Sorcery)

Auf Asterisk 22 werden SIP‑Endpunkte ausschließlich vom **PJSIP**‑Stack (`res_pjsip`) verarbeitet, der auf der **Sorcery**‑Objektabstraktionsschicht aufbaut. Anstatt eines einzelnen SIP‑„Peers“ teilt PJSIP ein SIP‑Konto in mehrere Objekttypen auf, die jeweils in einer eigenen Realtime‑Tabelle gespeichert werden:

| Sorcery‑Objekttyp | Realtime‑Tabelle | Was sie enthält |
|-------------------|-------------------|-----------------|
| endpoint | ps_endpoints | Kontoeinstellungen (context, codecs, DTMF usw.) |
| aor (address of record) | ps_aors | Registrierungsgrenzen und `qualify`‑Einstellungen |
| auth | ps_auths | `username` / `password`‑Anmeldedaten |
| contact | ps_contacts | Der dynamisch registrierte Standort |
| domain alias | ps_domain_aliases | Alternative SIP‑Domänen für einen Endpunkt |
| endpoint identifier by IP | ps_endpoint_id_ips | Zuordnung eines Endpunkts anhand der Quell‑IP |

Realtime für PJSIP wird an zwei Stellen aktiviert. Zuerst ordnen Sie die Sorcery‑Objekttypen Realtime in `extconfig.conf` zu:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Zweitens teilen Sie Sorcery mit, den `realtime`‑Assistenten für diese Objekttypen in `sorcery.conf` zu verwenden. Der Mapping‑Name (hier `res_pjsip`) ist das Modul, dessen Objekte Sie verlagern, und der rechts stehende Wert verweist auf die Familie, die Sie in `extconfig.conf` definiert haben:

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

Sie können statische und Realtime‑Objekte mischen. Wenn Sie einen Typ aus `sorcery.conf` weglassen, liest dieser Objekttyp weiterhin aus `pjsip.conf`. Ein übliches Muster ist, statische Transports und globale Einstellungen in `pjsip.conf` zu belassen, während Endpunkte, AORs, Auths und Contacts in der Datenbank gespeichert werden.

### Erstellen des PJSIP‑Realtime‑Schemas mit Alembic

Asterisk liefert Datenbank‑Migrationen für alle seine Realtime‑Schemas unter `contrib/ast-db-manage`. Dies ist der unterstützte Weg, die PJSIP‑Tabellen zu erstellen (und Versions‑Upgrades durchzuführen) – Sie schreiben die `ps_*`‑Tabellendefinitionen nicht mehr von Hand. Das `config`‑Migrationsset enthält die PJSIP/Sorcery‑Tabellen.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Damit werden `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` und die anderen PJSIP‑Tabellen mit den korrekten Spalten für die laufende Asterisk‑Version erzeugt. (Alembic benötigt das Python‑Paket `alembic` sowie einen SQLAlchemy‑Treiber wie `pymysql` für MySQL/MariaDB oder `psycopg2` für PostgreSQL.)

Ein minimales Realtime‑Endpoint besteht dann aus einer Zeile in jeder der drei Tabellen – zum Beispiel Endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Nach dem Einfügen der Zeilen muss nichts neu geladen werden – das nächste REGISTER/INVITE holt die Objekte aus der Datenbank. Sie können prüfen, was Realtime zurückgegeben hat, mit:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Database configuration

Now that we have configured the extconfig.conf file, let’s create the tables. Generally speaking, each database column matches an option name from the corresponding configuration file. The PJSIP `ps_*` tables follow this rule: every `ps_endpoints` column is named after a `pjsip.conf` endpoint option, every `ps_auths` column after an auth option, and so on. For example, the `pjsip.conf` endpoint below,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

is stored as one row across three tables. The `ps_endpoints` row holds `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; the `ps_auths` row holds `id=4000, auth_type=userpass, username=4000, password=supersecret`; and the `ps_aors` row holds `id=4000, max_contacts=1`. You only need to populate the columns you actually use — any column you leave NULL falls back to the option's default. If you want, for example, the `callerid` parameter on an endpoint, fill in the `callerid` column of `ps_endpoints` (the column name is the same as the `pjsip.conf` option name).

A voicemail table follows the same idea. Its columns map to the `voicemail.conf` fields:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

The `uniqueid` should be unique to each voicemail user and can be autoincrement. It need not have any relationship to the mailbox or context.

### Building a dial plan using Asterisk Real Time

You can also use the real-time system to create the dial plan. ARA uses the `switch` statement to include the real-time extensions into the normal dial plan contained in the extensions.conf file. The extension table should look like the one below:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

The `extensions` realtime family is unchanged in Asterisk 22; just make sure the `appdata` column dials PJSIP channels, for example `PJSIP/4000`. In the dial plan, you have to use the `switch` command to use the real time.

![Building a dial plan with Asterisk Real Time: extensions.conf uses a `switch => realtime` statement to pull extension rows (context, exten, priority, app, data) from a database table instead of from the text file.](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

or

```
[local]
switch => realtime/from-internal@extensions
```

## Lab: Installing and creating the database tables

In diesem Labor bereiten wir die Datenbank darauf vor, Asterisk‑Parameter zu empfangen. Wir erstellen nur die REALTIME‑Tabellen. Die statische Konfiguration bleibt in den Konfigurations‑Textdateien (cool, nicht wahr?). Die Tabellenerstellung in MySQL folgt.

Step 1: Get into the MySQL database as root.

```
mysql -u root -p
```

Step 2: Log in to the MySQL server created in the CDR labs.

```
mysql -u astdb -p
```

When asked for the password, type supersecret.

Step 3: Create the necessary tables. The legacy static schema files still ship under `contrib/realtime/` (for example `/usr/src/asterisk-22.x/contrib/realtime/mysql`), but on Asterisk 22 the recommended and version-correct way to build the realtime tables — especially the PJSIP `ps_*` tables — is the **Alembic** migrations under `contrib/ast-db-manage` (see the "Creating the PJSIP realtime schema with Alembic" section above).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

The Alembic `config` migration set builds the PJSIP `ps_*` tables (along with `voicemail`, `extensions`, and the other realtime schemas) with exactly the columns the running Asterisk version expects, so the schema always matches the build.

Use supersecret as the password.

Step 4: Verify the creation of the tables.

```
mysql -u astdb -p astdb
mysql>use astdb;
mysql>show tables;
```

You should see the PJSIP `ps_*` tables (created by the Alembic `config` migration), along with the `voicemail`, `extensions`, and other realtime tables:

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

(Alembic creates more tables than these — the list above shows the ones relevant to this lab.)

Step 5: The database is already configured for ODBC (since the CDR lab), so no further ODBC setup is needed here.

Step 6: Inspect and populate the tables from the MySQL client. You do not need a graphical tool such as phpMyAdmin — every step in this chapter is plain, copy-pasteable SQL run from the `mysql` command line. Connect to the `astdb` database (use `supersecret` when prompted):

```
mysql -u astdb -p astdb
```

You can confirm the columns of a table at any time with `DESCRIBE`, for example:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

These tables were created by the Alembic `config` migration, so their columns already match the `pjsip.conf` option names for the running Asterisk version — you only fill in the columns you need.

## Lab: Configuring and testing ARA

In diesem Labor ändern wir die extconfig.conf‑Konfiguration, um unsere Datenbankkonfiguration und -tabellen widerzuspiegeln.

Step 1: Configure extconfig.conf and reload Asterisk.

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

Beachten Sie die Familien `ps_endpoints`, `ps_aors`, `ps_auths` und `ps_contacts` oben; zusammen mit den passenden `sorcery.conf`‑Zuordnungen (siehe den Abschnitt „PJSIP Realtime (Sorcery)“) lassen sie PJSIP seine Accounts aus der Datenbank lesen. Die Familien `voicemail` und `extensions` runden das Beispiel ab.

Step 2: Real Time extension test. Create a new `6010` endpoint by inserting one row into each of `ps_auths`, `ps_aors`, and `ps_endpoints`, then try to register this endpoint with a softphone. Run the following SQL in the `mysql` client (`mysql -u astdb -p astdb`):

```sql
INSERT INTO ps_auths (id, auth_type, username, password)
VALUES ('6010-auth', 'userpass', '6010', 'supersecret');

INSERT INTO ps_aors (id, max_contacts)
VALUES ('6010', 1);

INSERT INTO ps_endpoints
  (id, transport, aors, auth, context, disallow, allow, dtmf_mode, direct_media)
VALUES
  ('6010', 'transport-udp', '6010', '6010-auth', 'from-internal',
   'all', 'ulaw', 'rfc4733', 'no');
```

Die drei Zeilen zusammen beschreiben einen SIP‑Account. Die übrigen Account‑Einstellungen verteilen sich über die PJSIP‑Objekte: context, codecs, DTMF‑Modus und Medien‑Handling, die live am Endpoint liegen (die letzten sechs Spalten oben); die dynamische Registrierung liegt am AOR. Es gibt kein separates „dynamic“‑Flag – ein AOR akzeptiert dynamische REGISTERs, solange `max_contacts` größer als null ist, und jeder registrierte Standort wird in `ps_contacts` geschrieben.

In PJSIP heißt der out‑of‑band DTMF‑Modus nach RFC 2833 / RFC 4733 `rfc4733`, und `dtmf_mode=rfc4733` ist der Standard – daher ist die Spalte `dtmf_mode` oben optional und nur zur Übersicht angezeigt.

Step 3: Try to register the new phone with a softphone using username `6010` and password `supersecret`. Confirm the registration on the Asterisk CLI:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Step 4: Include the extensions in the database.

```
mysql -u astdb -p
```

Enter password:

Use supersecret when asked, then insert the extension row from the MySQL client:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Step 5: Include Asterisk Real Time in the dial plan. In the context `default`:

```
switch => realtime/test@extensions
```

Reload the extensions to activate the change.

```
asterisk-server*CLI> extensions reload
```

Step 6: Reconfigure one of the phones to the username `bria`, if you have not already done so.

Step 7: Dial 6007 from an existing phone; the `bria` phone should ring.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, dass Asterisk Real Time es Ihnen ermöglicht, Ihre Konfigurationen in einer Datenbank zu speichern. Asterisk liefert native Realtime‑Treiber für ODBC (die jede von UnixODBC unterstützte Datenbank erreichen, einschließlich MySQL/MariaDB und SQLite) und PostgreSQL sowie einen LDAP‑Realtime‑Treiber für Verzeichnis‑Backends. MySQL/MariaDB wird über ODBC erreicht, wie wir in diesem Kapitel gezeigt haben (ein dediziertes `res_config_mysql`‑Add‑on existiert ebenfalls, lebt jedoch außerhalb des Kern‑Builds, sodass ODBC der übliche Weg ist). Die Konfiguration ist in statisch und realtime unterteilt. Statische Konfiguration ersetzt die Konfigurationsdateien, während die realtime‑Konfiguration dynamische Objekte erzeugt, die nur geladen werden, wenn ein Anruf oder ein anderes zugehöriges Ereignis eintritt. Wir schlossen mit einem praktischen Labor ab, in dem gezeigt wurde, wie man ARA installiert und konfiguriert.

## Quiz

1. Asterisk Realtime ist Teil der Standard‑Asterisk‑Distribution.  
   - A. Wahr  
   - B. Falsch
2. Die Verbindungsparameter eines Datenbank‑Servers werden in der Datei konfiguriert:  
   - A. extensions.conf  
   - B. pjsip.conf  
   - C. res_odbc.conf  
   - D. extconfig.conf
3. Die `extconfig.conf`‑Datei konfiguriert die von Realtime genutzten Tabellen. Sie hat zwei unterschiedliche Abschnitte (zwei auswählen):  
   - A. Statische Konfiguration  
   - B. Realtime‑Konfiguration  
   - C. Ausgehende Routen  
   - D. IP‑Adressen und Datenbank‑Ports
4. In der statischen Konfiguration werden die Objekte nach dem Laden aus der Datenbank im Speicher von Asterisk gehalten und nur beim Start oder Reload aktualisiert.  
   - A. Wahr  
   - B. Falsch
5. PJSIP realtime (Sorcery) unterstützt vollständig `qualify` und MWI für Realtime‑Endpoints, weil Sorcery sie als gewöhnliche konfigurierte PJSIP‑Objekte lädt, anstatt sie nach jedem Anruf zu verwerfen, wie es bei den alten SIP‑Realtime‑Peers der Fall war.  
   - A. Wahr  
   - B. Falsch
6. Welche Tabellen enthalten in PJSIP realtime die Endpunkte und deren registrierte Kontakte?  
   - A. `ps_endpoints` und `ps_contacts`  
   - B. `ps_peers` und `ps_registry`  
   - C. `ps_config` und `ps_data`  
   - D. `extconfig` und `res_odbc`
7. Sie können weiterhin Text‑Konfigurationsdateien verwenden, selbst nachdem ARA aktiviert wurde.  
   - A. Wahr  
   - B. Falsch
8. phpMyAdmin ist zwingend erforderlich, wenn Sie Realtime verwenden.  
   - A. Wahr  
   - B. Falsch
9. Die Datenbank muss mit jedem Feld erstellt werden, das in der Konfigurationsdatei existiert.  
   - A. Wahr  
   - B. Falsch
10. Auf Asterisk 22, was ist der empfohlene, versionsgerechte Weg, die PJSIP‑Realtime‑Tabellen (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`) zu erstellen?  
    - A. Die `CREATE TABLE`‑Anweisungen für jede `ps_*`‑Tabelle von Hand schreiben  
    - B. Das Legacy‑`mysql_config.sql` aus `contrib/realtime/` importieren  
    - C. Die Alembic `config`‑Migrationen unter `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`) ausführen  
    - D. Die Tabellen werden automatisch beim ersten Start von Asterisk erstellt

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
