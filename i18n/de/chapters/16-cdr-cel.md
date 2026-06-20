# Asterisk-Anrufdetailaufzeichnungen

Asterisk, wie andere Telefonieplattformen, ermöglicht die Abrechnung von Telefonaten. Mehrere Programme auf dem Markt können die von PBXs erzeugten Aufzeichnungen importieren. Diese Aufzeichnungen werden unter anderem verwendet, um die korrekte Rechnungsmenge und Statistiken zu überprüfen.

## Objectives

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Beschreiben, wo und in welchem Format die Datensätze erzeugt werden
- Datensätze mithilfe von ODBC (Open Database Connectivity) erzeugen
- Ein Authentifizierungsschema implementieren, das in die Abrechnung integriert ist

## Asterisk CDR Format

Asterisk erzeugt für jeden Anruf einen Call Detail Record (CDR). Diese Datensätze werden standardmäßig in einer Textdatei im CSV‑Format im Verzeichnis /var/log/asterisk/cdr-csv gespeichert. Die Datei ist in den folgenden Feldern organisiert:

| Field | Description | Type |
|-------|-------------|------|
| Accountcode | Account‑Nummer, die verwendet werden soll | String |
| Src | Anrufer‑ID‑Nummer | String |
| Dst | Ziel‑Durchwahl | String |
| Dcontext | Ziel‑Kontext | String |
| Clid | Anrufer‑ID mit Text | String |
| Channel | Verwendeter Kanal | String |
| Dstchannel | Ziel‑Kanal | String |
| Lastapp | Letzte Anwendung | String |
| Lastdata | Daten der letzten Anwendung | String |
| Start | Beginn des Anrufs | Date/Time |
| Answer | Annahme des Anrufs | Date/Time |
| End | Ende des Anrufs | Date/Time |
| Duration | Zeit von Wahl bis Auflegen | Integer (seconds) |
| Billsec | Zeit von Annahme bis Auflegen | Integer (seconds) |
| Disposition | Was mit dem Anruf geschah (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | Benutzerdefiniertes Feld | String |

Beispiel einer CSV‑Datei. Jede Zeile ist ein Datensatz; die Felder erscheinen in derselben Reihenfolge wie die obige Tabelle (`accountcode` zuerst, `amaflags` zuletzt):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Account codes and automated message accounting

Sie können Account‑Codes und AMA‑Flags für jeden Kanal festlegen. Üblicherweise geschieht dies in der Kanal‑Konfigurationsdatei (z. B. chan_dahdi.conf, pjsip.conf). Der Parameter amaflags definiert, was mit dem CDR‑Datensatz geschehen soll. Die möglichen amaflag‑Werte sind:

- Default
- Omit
- Billing
- Documentation

Ähnlich wie ein Datensatz für Billing oder Documentation markiert werden kann, kann für jeden Datensatz ein Account‑Code gesetzt werden. Der Account‑Code ist ein freier Text (die `accountcode` endpoint‑Option akzeptiert jede Zeichenkette, und der CDR‑Datensatz speichert ihn in einem 80‑Zeichen‑Feld), der üblicherweise verwendet wird, um einen Datensatz einer Abteilung oder Geschäftseinheit zuzuordnen. Beispiel: pjsip.conf endpoint‑Abschnitt

```
[8576]
type=endpoint
accountcode=Support
```

Das AMA‑Flag ist keine `pjsip.conf` endpoint‑Option in Asterisk 22; setzen Sie es pro Anruf aus dem Dialplan mit der `CHANNEL`‑Funktion (zum Beispiel `Set(CHANNEL(amaflags)=billing)`) oder mit `Set(CDR(amaflags)=billing)`.

## Changing the CSV and/or CDR format

You can change the CSV format by changing the cdr_custom.conf file.

```
;
; Mappings for custom config file
;
[mappings]
Master.csv =>
"${CDR(clid)}","${CDR(src)}","${CDR(dst)}","${CDR(dcontext)}","${CDR(channel)}"
,"${CDR(dstchannel)}","${CDR(lastapp)}","${CDR(lastdata)}","${CDR(start)}","${C
DR(answer)}","${CDR(end)}","${CDR(duration)}","${CDR(billsec)}","${CDR(disposit
ion)}","${CDR(amaflags)}","${CDR(accountcode)}","${CDR(uniqueid)}","${CDR(userf
ield)}"
```

You can change the CDR format in the cdr_custom.conf file.

## CDR Storage

CDR‑Speicherung kann auf verschiedene Arten erfolgen. Der wichtigste Weg sind CSV‑Textdateien, die leicht in Tabellenkalkulationen importiert werden können. Für kleine Unternehmen ist das in der Regel ausreichend. Einige Abrechnungsprogramme akzeptieren standardmäßig CSV‑Dateien. Das Speichern von CDRs in einer Datenbank ist jedoch deutlich besser und sicherer. Asterisk unterstützt mehrere Datenbank‑Varianten. Es gibt einige grafische Oberflächen für die Abrechnung auf dem Markt. Bei so vielen Treibern – welcher ist der richtige?

### Storage drivers available

- cdr_csv – Comma Separated Value text files
- cdr_custom – Customizable comma-separated-value text files
- cdr_adaptive_odbc – Adaptive ODBC backend (preferred for database storage)
- cdr_odbc – unixODBC supported databases (legacy; cdr_adaptive_odbc preferred)
- cdr_pgsql – Postgres databases
- cdr_tds (cdr_freetds) – Sybase and MSSQL databases via FreeTDS
- cdr_manager – CDR to Manager Interface
- cdr_radius – CDR radius interface
- cdr_sqlite3_custom – SQLite3 custom CDR module

Das `cdr_addon_mysql` (cdr_mysql)‑Modul, das ältere Anleitungen empfohlen haben, wurde in Asterisk 19 entfernt, sodass es keinen nativen MySQL‑CDR‑Treiber in Asterisk 22 gibt. Um CDRs nach MySQL/MariaDB zu schreiben, verwenden Sie `cdr_adaptive_odbc` zusammen mit einem MySQL‑ODBC‑Treiber — der Ansatz, der in diesem Kapitel verwendet wird.

Die CDR‑Aufzeichnung erfolgt für alle aktiven Module, die in der Datei /etc/asterisk/modules.conf geladen sind. Wenn der Parameter autoload=yes gesetzt ist, werden alle Module geladen. Um zu prüfen, welche cdr_drivers derzeit im System geladen sind, verwenden Sie den folgenden Befehl:

```
asterisk*CLI> module show like cdr_
Module                 Description                              Use Count  Status
Support Level
cdr_adaptive_odbc.so   Adaptive ODBC CDR backend                0          Running
core
cdr_csv.so             Comma Separated Values CDR Backend       0          Running
extended
cdr_custom.so          Customizable Comma Separated Values CDR  0          Running
core
cdr_manager.so         Asterisk Manager Interface CDR Backend   0          Running
core
cdr_odbc.so            ODBC CDR Backend                         0          Running
extended
cdr_sqlite3_custom.so  SQLite3 Custom CDR Module                0          Not Running
extended
6 modules loaded
```

Wenn Sie den Screenshot oben sehen, laufen mindestens cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc und cdr_sqlite3_custom. In den letzten Jahren, nach einigen Astricons, wurde mir klar, dass das Asterisk‑Team ODBC bevorzugt. Es ist der einzige Treiber, der Connection Pooling unterstützt. Connection Pooling ist ein großer Vorteil in Bezug auf die Leistung, weil Sie nicht für jede Operation eine neue Verbindung öffnen müssen. Dieses Kapitel wurde ursprünglich mit cdr_mysql geschrieben. Für diese Ausgabe bin ich zu cdr_adaptive_odbc gewechselt, obwohl die Einrichtung etwas komplexer ist. Die Wahl von cdr_adaptive_odbc ermöglicht es uns zudem, das CDR anzupassen. Sie können einfach eine neue CDR‑Variable im Dialplan setzen und die entsprechende Spalte in der Datenbank hinzufügen. Zum Beispiel, um den Audio‑Jitter aufzuzeichnen:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV Storage

Wie bereits erwähnt, sendet Asterisk standardmäßig alle CDRs in eine CSV‑Textdatei über das Modul cdr_csv.so. Wenn Sie die Dateien im Verzeichnis /var/log/asterisk/cdr-csv nicht sehen, prüfen Sie, ob das Modul mit dem CLI‑Befehl `module show` geladen ist. Wenn es nicht geladen ist, prüfen Sie modules.conf. In diesem Kapitel senden wir CDRs zu cdr_csv als Backup.

### Configuring the file modules.conf

Um nur die passenden Module zu laden, verwenden Sie die folgenden Zeilen in der Datei modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Jetzt haben wir nur cdr_csv und cdr_adaptive_odbc geladen.

## Installing and configuring ODBC on Ubuntu 22.04

I always regret to publish detailed instructions in the book. They will change sometimes sooner than the book is published. Versions change, modules change, so try to adapt the command here to your own situation. Most of the time minor changes are enough to reproduce the installation. Pay attention on the steps even experienced Linux users will find hard to install the ODBC drivers.

Step 1 - Install the required packages:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Step 2 - Create a database and a user:

```
mysql -u root -p
```

(Use the password defined when you created the mysql server) Type this commands in mysql command line

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Step 3 - Create the database

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Step 4: Download the MySQL ODBC connector from Oracle. Check your operating system using: `lsb_release -a`. For Ubuntu 22.04 (x86_64), visit https://dev.mysql.com/downloads/connector/odbc/ and choose the current 8.x or 9.x release for Ubuntu 22.04. The exact filename and version number change over time, so set `VER` (below) to whatever the current Linux glibc build is called.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Step 5: Install the ODBC driver

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Step 6 - Configure the ODBC connector edit the file /etc/odbc.ini to create the DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Step 7: Test the driver access using iSQL. iSQL is a command line utility to connect to the database over unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Please, do not procede with Asterisk configuration if you can’t see the result of the isql command.

### Configuring ODBC in the Asterisk

Before you can configure the cdr_adaptive_odbc, you should first configure the ODBC resource file.

Step 1 - Connect Asterisk to ODBC. Edit the file res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Step 2 – Restart Asterisk and test using

```
asterisk*CLI> odbc show
```

The output is shown below.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Step 3 – Configure the adaptive ODBC driver in /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Here `connection` points to the `[cdr]` connection section defined in `res_odbc.conf`, and `table` is the database table where CDRs are written.

Step 4 – Reload the module cdr_adaptive_odbc.so:

```
asterisk*CLI> reload cdr_adaptive_odbc
```

Step 5 – Make same calls and check the database fro new records. To check the database:

```
mysql -u root -p
>use astdb
>select * from cdr;
```

## Applications and functions

Several applications are related to billing.

### CDR(accountcode)

Sets an account code before calling another application dial(); for example: Format:

```
Set(CDR(accountcode)=account)
```

The account code can be verified using the channel variable ${CDR(accountcode)}

### CDR(amaflags)

Set a flag for billing purposes. Options are default, omit, documentation, and billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Disables CDR recording for the current channel, so no CDR is written to the file or database. Setting it back to `0` re-enables recording.

```
Set(CDR_PROP(disable)=1)
```

The `NoCDR()` application that previous editions used for this was removed in Asterisk 21; on Asterisk 22 you disable a channel's CDR with `Set(CDR_PROP(disable)=1)` instead.

### ResetCDR()

Resets the Call Data Record: the `start` time (and, if answered, the `answer` time) is set to the current time and all CDR variables are wiped. If the `v` option is set, the CDR variables are preserved during the reset.

### Set(CDR(userfield)=Value)

This command sets a user field in the CDR. When using `cdr_adaptive_odbc`, the user field is automatically stored if a `userfield` column exists in the CDR table — no source recompilation needed. For CSV text files, you have to edit the source code (cdr_csv.c) and recompile Asterisk if you want to use user fields.

Earlier editions stored CDRs in MySQL with the `cdr_addon_mysql` module (`cdr_mysql.conf`). That module was removed in Asterisk 19, so it is not available on Asterisk 22. The supported path is now `cdr_adaptive_odbc` with a MySQL ODBC driver, which stores the user field — and any other custom column — natively through its adaptive column mapping.

### Appending to the user field

Earlier editions used the `AppendCDRUserField()` application to append data to the
CDR user field. That application was removed from Asterisk; on Asterisk 22 you append
to the user field by reading and re-setting it with the `CDR` function, for example
`Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## User authentication

Einige Unternehmen berechnen die Anrufe ihren Mitarbeitern. In Asterisk können Sie ein Authentifizierungsschema festlegen, das es ermöglicht, den authentifizierten Benutzer im CDR abzurechnen. Diese Authentifizierung kann mithilfe eines Passworts erfolgen, das als Parameter an die Anwendung Authenticate übergeben wird – eine Passwortdatei, angegeben durch ein / (Slash) vor dem Parameter, oder ein Asterisk‑Datenbank‑Schlüssel (unter Verwendung der `d`‑Option). Format:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Optionen:

- a – Setzt den Account‑Code des Kanals auf das eingegebene Passwort.
- d – Interpretiert den angegebenen Pfad als Asterisk‑DB‑Schlüssel statt als literal Datei.
- m – Interpretiert den Pfad als Datei mit `accountcode:passwordhash`‑Zeilen.
- r – Entfernt den Datenbankschlüssel nach erfolgreicher Authentifizierung (nur gültig mit `d`).

Wenn der Anrufer alle drei Versuche scheitert, wird der Kanal aufgelegt; die Dialplan‑Ausführung wird nicht fortgesetzt, daher muss der Fehlerschritt in der Zeile nach `Authenticate()` behandelt werden. Beispiel (Internationale Anrufe):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

Die alte `j`‑Option (Sprung zu Priorität n+101 bei Fehler) und die `+101`‑Prioritätskonvention wurden bereits vor langer Zeit aus Asterisk entfernt; ein fehlgeschlagener `Authenticate()` legt einfach auf.

Um das Passwort in einem DB‑Schlüssel von der Konsole einzufügen:

```
asterisk*CLI> database put senha 123456 1
```

## Using passwords from voicemail

This application does the same as authenticate, but uses the voicemail configuration file for the password.

```
VMAuthenticate([mailbox][@context][,options])
```

If a mailbox is specified, only that mailbox's password will be considered valid. If the mailbox is not specified, the channel variable `${AUTH_MAILBOX}` will be set with the authenticated mailbox. If the `s` option is set, the initial prompts are skipped. Example (International Calls):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDR records provide one summary row per call. For more detailed event tracking — such as individual channel state transitions, bridge enter/leave events, and attended transfer legs — Asterisk 22 includes **Channel Event Logging (CEL)**, configured via `/etc/asterisk/cel.conf` and stored through backends such as `cel_odbc` or `cel_custom`.

CEL complements CDR rather than replacing it: CDR remains the standard for billing summaries, while CEL gives granular per-event data useful for fraud detection, quality monitoring, and advanced reporting.

The `cel.conf` configuration pattern mirrors `cdr.conf`: you enable the event types you want in the `[general]` section of `cel.conf`, then configure each storage back-end in its own file — `cel_custom.conf` for CSV, `cel_odbc.conf` for an ODBC database (the same `res_odbc.conf` connection used for CDRs). You can confirm whether CEL is active with `cel show status` on the CLI.

## Zusammenfassung

In diesem Kapitel haben wir gelernt, wie man CDR‑Aufzeichnungen in Textdateien und in einer MySQL‑Datenbank implementiert. Wir haben außerdem gelernt, wie man amaflags und Kontocodes setzt. Am Ende des Kapitels haben wir gelernt, wie man ein Authentifizierungsschema verwendet, das in CDR und Abrechnung integriert ist.

## Quiz

1. Standardmäßig speichert Asterisk die CDR im Verzeichnis /var/log/asterisk/cdr-csv.
   - A. Falsch
   - B. Wahr
2. Asterisk kann CDRs schreiben nach (alle zutreffenden auswählen):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV‑Textdateien
   - E. unixODBC‑unterstützten Datenbanken
3. Asterisk erzeugt jeweils nur eine Art von Speicherung für eine CDR.
   - A. Falsch
   - B. Wahr
4. Welche Asterisk amaflags sind verfügbar?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Um einer Abteilung eine CDR zuzuordnen, verwenden Sie den ___‑Befehl, und der Account‑Code kann mit der ___‑Kanalvariablen ausgelesen werden.
6. Der Unterschied zwischen `Set(CDR_PROP(disable)=1)` und `ResetCDR()` besteht darin, dass das Deaktivieren der CDR verhindert, dass ein Eintrag geschrieben wird, während `ResetCDR()` den aktuellen Eintrag zurücksetzt (auf Null). (Die `NoCDR()`‑Anwendung, die zuvor CDRs deaktivierte, wurde in Asterisk 21 entfernt.)
   - A. Falsch
   - B. Wahr
7. Um ein benutzerdefiniertes Feld mit dem `cdr_csv.so`‑Modul zu verwenden, müssen Sie den Quellcode bearbeiten und Asterisk neu kompilieren.
   - A. Falsch
   - B. Wahr
8. Die drei Authentifizierungsmethoden, die der Anwendung Authenticate() zur Verfügung stehen, sind:
   - A. Passwort
   - B. Passwortdatei
   - C. Asterisk DB (dbput und dbget)
   - D. Voicemail
9. Voicemail‑Passwörter werden in einem separaten Abschnitt von `voicemail.conf` angegeben und sind nicht dieselben wie die Voicemail‑Benutzer.
   - A. Falsch
   - B. Wahr
10. Channel Event Logging (CEL) ersetzt CDR in Asterisk 22 — sobald CEL aktiviert ist, werden keine CDR‑Abrechnungszusammenfassungen mehr erstellt.
    - A. Falsch
    - B. Wahr

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
