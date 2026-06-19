# Asterisk Call Detail Records

Asterisk ermöglicht, wie andere Telefonie-Plattformen auch, die Abrechnung von Telefongesprächen. Es gibt verschiedene Programme auf dem Markt, die die von Telefonanlagen (PBXs) erzeugten Datensätze importieren können. Diese Datensätze werden unter anderem dazu verwendet, die Korrektheit von Rechnungsbeträgen zu überprüfen und Statistiken zu erstellen.

## Ziele

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Zu beschreiben, wo und in welchem Format die Datensätze generiert werden
- Datensätze unter Verwendung von ODBC (Open Database Connectivity) zu erzeugen
- Ein in die Abrechnung integriertes Authentifizierungsschema zu implementieren

## Asterisk CDR Format

Asterisk generiert für jedes Gespräch einen Call Detail Record (CDR). Diese Datensätze werden standardmäßig in einer Textdatei im CSV-Format (Comma Separated Value) unter /var/log/asterisk/cdr-csv gespeichert. Die Datei ist in folgende Felder unterteilt: CDR Beschreibung Typ Größe Accountcode Kontonummer zur Verwendung String Src Caller ID Nummer String Dst Ziel-Extension String Dcontext Ziel-Context String Caller ID mit Text String Channel Verwendeter Kanal String Dstchannel Zielkanal String Lastapp Letzte Anwendung String Lastdata Letzte Anwendungsdaten String Start Gesprächsbeginn Datum/Uhrzeit Answer Gesprächsannahme Datum/Uhrzeit End Gesprächsende Datum/Uhrzeit Duration Zeit von der Wahl bis zum Auflegen Ganzzahl (Sekunden) Billsec Zeit von der Annahme bis zum Auflegen Ganzzahl (Sekunden) Disposition Was mit dem Anruf geschah String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field Benutzerdefiniertes Feld String Beispiel einer in eine Tabelle importierten CSV-Datei. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## Account Codes und Automated Message Accounting

Sie können für jeden Kanal Account Codes und AMA-Flags festlegen. Normalerweise geschieht dies in der Konfigurationsdatei des Kanals (z. B. chan_dahdi.conf, pjsip.conf). Der Parameter amaflags definiert, was mit dem CDR-Datensatz geschehen soll. Die möglichen amaflag-Werte sind:

- Default
- Omit
- Billing
- Documentation

Ähnlich wie ein Datensatz für die Abrechnung oder Dokumentation markiert werden kann, lässt sich für jeden Datensatz ein Account Code festlegen. Der Account Code ist eine frei wählbare Zeichenkette (die `accountcode` Endpoint-Option akzeptiert jeden String, und der CDR-Datensatz speichert ihn in einem 80 Zeichen langen Feld), die üblicherweise verwendet wird, um einen Datensatz einer Abteilung oder Geschäftseinheit zuzuordnen. Beispiel: pjsip.conf Endpoint-Sektion

```
[8576]
type=endpoint
accountcode=Support
```

Das AMA-Flag ist in Asterisk 22 keine `pjsip.conf` Endpoint-Option; setzen Sie es pro Anruf über den dialplan mit der `CHANNEL` Funktion (zum Beispiel `Set(CHANNEL(amaflags)=billing)`) oder mit `Set(CDR(amaflags)=billing)`.

## Ändern des CSV- und/oder CDR-Formats

Sie können das CSV-Format ändern, indem Sie die Datei cdr_custom.conf bearbeiten.

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

Sie können das CDR-Format in der Datei cdr_custom.conf ändern.

## CDR-Speicherung

Die CDR-Speicherung kann auf verschiedene Weise erfolgen. Der wichtigste Weg sind CSV-Textdateien, die leicht in Tabellenkalkulationen importiert werden können. Für kleine Unternehmen ist dies meist ausreichend. Einige Abrechnungssoftware akzeptiert standardmäßig CSV-Dateien. Das Speichern von CDRs in einer Datenbank ist jedoch wesentlich besser und sicherer. Asterisk unterstützt verschiedene Datenbankvarianten. Es gibt einige grafische Oberflächen für die Abrechnung auf dem Markt. Bei so vielen Treibern, welchen sollte man wählen?

### Verfügbare Speichertreiber

- cdr_csv – Kommagetrennte Textdateien
- cdr_custom – Anpassbare kommagetrennte Textdateien
- cdr_adaptive_odbc – Adaptives ODBC-Backend (bevorzugt für die Datenbankspeicherung)
- cdr_odbc – unixODBC-unterstützte Datenbanken (veraltet; cdr_adaptive_odbc wird bevorzugt)
- cdr_pgsql – Postgres-Datenbanken
- cdr_tds (cdr_freetds) – Sybase- und MSSQL-Datenbanken via FreeTDS
- cdr_manager – CDR zur Manager-Schnittstelle
- cdr_radius – CDR-RADIUS-Schnittstelle
- cdr_sqlite3_custom – Benutzerdefiniertes SQLite3-CDR-Modul

Das `cdr_addon_mysql` (cdr_mysql) Modul, das in älteren Anleitungen empfohlen wurde, wurde in Asterisk 19 entfernt, daher gibt es in Asterisk 22 keinen nativen MySQL-CDR-Treiber mehr. Um CDRs in MySQL/MariaDB zu schreiben, verwenden Sie `cdr_adaptive_odbc` zusammen mit einem MySQL-ODBC-Treiber – der in diesem Kapitel verwendete Ansatz.

Die CDR-Aufzeichnung erfolgt für alle aktiven Module, die in der Datei /etc/asterisk/modules.conf geladen sind. Wenn der Parameter autoload=yes gesetzt ist, werden alle Module geladen. Um zu überprüfen, welche cdr_drivers aktuell im System geladen sind, verwenden Sie den folgenden Befehl:

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

Wenn Sie den obigen Screenshot sehen, laufen mindestens cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc und cdr_sqlite3_custom. In den letzten Jahren, nach einigen Astricons, wurde mir klar, dass das Asterisk-Team ODBC bevorzugt. Es ist der einzige Treiber, der Verbindungspooling unterstützt. Verbindungspooling ist ein großer Vorteil in Bezug auf die Leistung, da Sie nicht für jede Operation eine neue Verbindung öffnen müssen. Dieses Kapitel wurde zuvor mit cdr_mysql geschrieben. Ich bin für diese Ausgabe auf cdr_adaptive_odbc umgestiegen, auch wenn ich weiß, dass die Einrichtung etwas komplexer ist. Die Wahl für cdr_adaptive_odbc erlaubt uns zudem, das CDR anzupassen. Sie können einfach eine neue CDR-Variable im dialplan setzen und die Spalte zur Datenbank hinzufügen. Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### CSV-Speicherung

Wie bereits erwähnt, sendet Asterisk standardmäßig alle CDRs unter Verwendung des Moduls cdr_csv.so in eine CSV-Textdatei. Wenn Sie die Dateien nicht unter /var/log/asterisk/cdr-csv sehen können, überprüfen Sie mit dem CLI-Befehl module show, ob das Modul geladen ist. Wenn es nicht geladen ist, überprüfen Sie die modules.conf. In diesem Kapitel werden wir CDRs als Backup an cdr_csv senden.

### Konfiguration der Datei modules.conf

Um nur die entsprechenden Module zu laden, verwenden Sie die folgenden Zeilen in der Datei modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Jetzt sind nur noch cdr_csv und cdr_adaptive_odbc geladen.

## Installation und Konfiguration von ODBC unter Ubuntu 22.04

Ich bereue es immer, detaillierte Anweisungen in das Buch aufzunehmen. Sie ändern sich manchmal schneller, als das Buch veröffentlicht werden kann. Versionen ändern sich, Module ändern sich, versuchen Sie also, die Befehle hier an Ihre eigene Situation anzupassen. Meistens reichen geringfügige Änderungen aus, um die Installation zu reproduzieren. Achten Sie auf die Schritte, selbst erfahrene Linux-Benutzer finden die Installation der ODBC-Treiber oft schwierig.

Schritt 1 - Installieren Sie die erforderlichen Pakete:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Schritt 2 - Erstellen Sie eine Datenbank und einen Benutzer:

```
mysql -u root -p
```

(Verwenden Sie das Passwort, das Sie bei der Erstellung des MySQL-Servers definiert haben) Geben Sie diese Befehle in der MySQL-Befehlszeile ein

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Schritt 3 - Erstellen Sie die Datenbank

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Schritt 4: Laden Sie den MySQL-ODBC-Connector von Oracle herunter. Überprüfen Sie Ihr Betriebssystem mit: `lsb_release -a`. Für Ubuntu 22.04 (x86_64) besuchen Sie https://dev.mysql.com/downloads/connector/odbc/ und wählen Sie die aktuelle 8.x- oder 9.x-Version für Ubuntu 22.04. Der genaue Dateiname und die Versionsnummer ändern sich im Laufe der Zeit, setzen Sie also `VER` (unten) auf den Namen des aktuellen Linux-glibc-Builds.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Schritt 5: Installieren Sie den ODBC-Treiber

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Schritt 6 - Konfigurieren Sie den ODBC-Connector, bearbeiten Sie die Datei /etc/odbc.ini, um den DSN (Data Source Name) zu erstellen

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Schritt 7: Testen Sie den Treiberzugriff mit iSQL. iSQL ist ein Befehlszeilen-Dienstprogramm, um über unixodbc eine Verbindung zur Datenbank herzustellen.

```
isql -v astconn astdb supersecret
>show tables
```

Bitte fahren Sie nicht mit der Asterisk-Konfiguration fort, wenn Sie das Ergebnis des isql-Befehls nicht sehen können.

### Konfiguration von ODBC in Asterisk

Bevor Sie cdr_adaptive_odbc konfigurieren können, sollten Sie zuerst die ODBC-Ressourcendatei konfigurieren.

Schritt 1 - Verbinden Sie Asterisk mit ODBC. Bearbeiten Sie die Datei res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Schritt 2 – Starten Sie Asterisk neu und testen Sie mit

```
CLI>odbc show
```

Die Ausgabe wird unten angezeigt.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Schritt 3 – Konfigurieren Sie den adaptiven ODBC-Treiber in /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Hier verweist `connection` auf die `[cdr]` Verbindungssektion, die in `res_odbc.conf` definiert ist, und `table` ist die Datenbanktabelle, in die CDRs geschrieben werden.

Schritt 4 – Laden Sie das Modul cdr_adaptive_odbc.so neu:

```
asterisk*CLI>reload cdr_adaptive_odbc
```

Schritt 5 – Führen Sie einige Anrufe durch und überprüfen Sie die Datenbank auf neue Datensätze. Um die Datenbank zu überprüfen:

```
mysql –u root –p
>use astdb
>select * from cdr
```

## Anwendungen und Funktionen

Mehrere Anwendungen stehen im Zusammenhang mit der Abrechnung.

### CDR(accountcode)

Setzt einen Account Code, bevor eine andere Anwendung dial() aufgerufen wird; zum Beispiel: Format:

```
Set(CDR(accountcode)=account)
```

Der Account Code kann mit der Kanalvariablen ${CDR(accountcode)} überprüft werden

### CDR(amaflags)

Setzt ein Flag für Abrechnungszwecke. Optionen sind default, omit, documentation und billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Deaktiviert die CDR-Aufzeichnung für den aktuellen Kanal, sodass kein CDR in die Datei oder Datenbank geschrieben wird. Das Zurücksetzen auf `0` aktiviert die Aufzeichnung wieder.

```
Set(CDR_PROP(disable)=1)
```

Die `NoCDR()` Anwendung, die in früheren Ausgaben dafür verwendet wurde, wurde in Asterisk 21 entfernt; unter Asterisk 22 deaktivieren Sie das CDR eines Kanals stattdessen mit `Set(CDR_PROP(disable)=1)`.

### ResetCDR()

Setzt das Call Data Record zurück: Die `start` Zeit (und, falls angenommen, die `answer` Zeit) wird auf die aktuelle Zeit gesetzt und alle CDR-Variablen werden gelöscht. Wenn die `v` Option gesetzt ist, bleiben die CDR-Variablen während des Zurücksetzens erhalten.

### Set(CDR(userfield)=Value)

Dieser Befehl setzt ein Benutzerfeld im CDR. Bei Verwendung von `cdr_adaptive_odbc` wird das Benutzerfeld automatisch gespeichert, wenn eine `userfield` Spalte in der CDR-Tabelle existiert — eine Neukompilierung des Quellcodes ist nicht erforderlich. Für CSV-Textdateien müssen Sie den Quellcode (cdr_csv.c) bearbeiten und Asterisk neu kompilieren, wenn Sie Benutzerfelder verwenden möchten.

Frühere Ausgaben speicherten CDRs in MySQL mit dem `cdr_addon_mysql` Modul (`cdr_mysql.conf`). Dieses Modul wurde in Asterisk 19 entfernt und ist daher in Asterisk 22 nicht verfügbar. Der unterstützte Weg ist jetzt `cdr_adaptive_odbc` mit einem MySQL-ODBC-Treiber, der das Benutzerfeld — und jede andere benutzerdefinierte Spalte — nativ durch seine adaptive Spaltenzuordnung speichert.

### AppendCDRUserField(Value)

Hängt Daten an das Benutzerfeld im CDR an.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Benutzerauthentifizierung

Einige Unternehmen stellen die Anrufe ihren Mitarbeitern in Rechnung. In Asterisk können Sie ein Authentifizierungsschema einrichten, das es Ihnen ermöglicht, den authentifizierten Benutzer im CDR abzurechnen. Diese Authentifizierung kann mit einem Passwort erfolgen, das als Parameter an die Authenticate-Anwendung übergeben wird — eine Passwortdatei, gekennzeichnet durch einen / (Schrägstrich) vor dem Parameter, oder ein Asterisk-Datenbankschlüssel (unter Verwendung der `d` Option). Format:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Optionen:

- a – Setzt den Account Code des Kanals auf das eingegebene Passwort.
- d – Interpretiert den angegebenen Pfad als Asterisk-DB-Schlüssel anstelle einer literalen Datei.
- m – Interpretiert den Pfad als eine Datei mit `accountcode:passwordhash` Zeilen.
- r – Entfernt den Datenbankschlüssel nach erfolgreicher Authentifizierung (gültig nur mit `d`).

Wenn der Anrufer alle drei Versuche nicht besteht, wird der Kanal aufgelegt; die Ausführung des dialplan wird nicht fortgesetzt, behandeln Sie daher den Fehlerpfad in der Zeile nach `Authenticate()`. Beispiel (Internationale Anrufe):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

Die alte `j` Option (Sprung zur Priorität n+101 bei Fehler) und die `+101` Prioritätskonvention wurden vor langer Zeit aus Asterisk entfernt; ein fehlgeschlagenes `Authenticate()` legt einfach auf.

Um das Passwort von der Konsole aus in einen DB-Schlüssel einzufügen:

```
CLI> database put senha 123456 1
```

## Verwendung von Passwörtern aus der Voicemail

Diese Anwendung bewirkt dasselbe wie authenticate, verwendet jedoch die Voicemail-Konfigurationsdatei für das Passwort.

```
VMAuthenticate([mailbox][@context][,options])
```

Wenn eine Mailbox angegeben ist, wird nur das Passwort dieser Mailbox als gültig betrachtet. Wenn die Mailbox nicht angegeben ist, wird die Kanalvariable `${AUTH_MAILBOX}` mit der authentifizierten Mailbox gesetzt. Wenn die `s` Option gesetzt ist, werden die anfänglichen Ansagen übersprungen. Beispiel (Internationale Anrufe):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDR-Datensätze liefern eine Zusammenfassungszeile pro Anruf. Für eine detailliertere Ereignisverfolgung — wie individuelle Kanalzustandsübergänge, Bridge-Eintritts-/Austrittsereignisse und vermittelte Transferabschnitte — enthält Asterisk 22 das **Channel Event Logging (CEL)**, das über `/etc/asterisk/cel.conf` konfiguriert und über Backends wie `cel_odbc` oder `cel_custom` gespeichert wird.

CEL ergänzt CDR, anstatt es zu ersetzen: CDR bleibt der Standard für Abrechnungszusammenfassungen, während CEL granulare Daten pro Ereignis liefert, die für Betrugserkennung, Qualitätsüberwachung und fortgeschrittene Berichterstattung nützlich sind.

Das `cel.conf` Konfigurationsmuster spiegelt `cdr.conf` wider: Sie aktivieren die gewünschten Ereignistypen in der `[general]` Sektion von `cel.conf` und konfigurieren dann jedes Speicher-Backend in seiner eigenen Datei — `cel_custom.conf` für CSV, `cel_odbc.conf` für eine ODBC-Datenbank (dieselbe `res_odbc.conf` Verbindung, die für CDRs verwendet wird). Sie können mit `cel show status` auf der CLI bestätigen, ob CEL aktiv ist.

## Zusammenfassung

In diesem Kapitel haben wir gelernt, wie man die CDR-Aufzeichnung in Textdateien und in einer MySQL-Datenbank implementiert. Wir haben auch gelernt, wie man amaflags und Account Codes setzt. Am Ende des Kapitels haben wir gelernt, wie man ein in CDR und Abrechnung integriertes Authentifizierungsschema verwendet.

## Quiz

1. Standardmäßig zeichnet Asterisk das CDR im Verzeichnis /var/log/asterisk/cdr-csv auf.
   - A. Falsch
   - B. Wahr
2. Asterisk kann CDRs schreiben nach (wählen Sie alle zutreffenden aus):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV-Textdateien
   - E. unixODBC-unterstützte Datenbanken
3. Asterisk generiert ein CDR jeweils nur für eine Speicherart.
   - A. Falsch
   - B. Wahr
4. Welche Asterisk amaflags sind verfügbar?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Um eine Abteilung mit einem CDR zu verknüpfen, verwenden Sie den ___ Befehl, und der Account Code kann mit der ___ Kanalvariablen gelesen werden.
6. Der Unterschied zwischen `Set(CDR_PROP(disable)=1)` und `ResetCDR()` besteht darin, dass das Deaktivieren des CDR verhindert, dass ein Datensatz geschrieben wird, während `ResetCDR()` den aktuellen Datensatz zurücksetzt (auf Null setzt). (Die `NoCDR()` Anwendung, die zuvor CDRs deaktivierte, wurde in Asterisk 21 entfernt.)
   - A. Falsch
   - B. Wahr
7. Um ein benutzerdefiniertes Feld mit dem `cdr_csv.so` Modul zu verwenden, müssen Sie den Quellcode bearbeiten und Asterisk neu kompilieren.
   - A. Falsch
   - B. Wahr
8. Die drei Authentifizierungsmethoden, die der Authenticate()-Anwendung zur Verfügung stehen, sind:
   - A. Passwort
   - B. Passwortdatei
   - C. Asterisk DB (dbput und dbget)
   - D. Voicemail
9. Voicemail-Passwörter werden in einer separaten Sektion von `voicemail.conf` angegeben und sind nicht dieselben wie die der Voicemail-Benutzer.
   - A. Falsch
   - B. Wahr
10. Channel Event Logging (CEL) ersetzt CDR in Asterisk 22 — sobald CEL aktiviert ist, werden keine CDR-Abrechnungszusammenfassungen mehr erstellt.
    - A. Falsch
    - B. Wahr

**Antworten:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
