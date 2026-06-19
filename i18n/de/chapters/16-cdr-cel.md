# Asterisk Call Detail Records

Asterisk ermöglicht, wie andere Telefonie-Plattformen auch, die Abrechnung von Telefongesprächen. Es gibt verschiedene Programme auf dem Markt, die die von PBXs erzeugten Datensätze importieren können. Diese Datensätze werden unter anderem dazu verwendet, die Korrektheit von Rechnungsbeträgen zu überprüfen und Statistiken zu erstellen.

## Ziele

Am Ende dieses Kapitels sollte der Leser in der Lage sein:

- Zu beschreiben, wo und in welchem Format die Datensätze generiert werden
- Datensätze unter Verwendung von ODBC (Open Database Connectivity) zu erzeugen
- Ein Authentifizierungsschema zu implementieren, das in die Abrechnung integriert ist

## Asterisk CDR Format

Asterisk generiert für jeden Anruf einen Call Detail Record (CDR). Diese Datensätze werden standardmäßig in einer Textdatei im CSV-Format (Comma Separated Value) unter /var/log/asterisk/cdr-csv gespeichert. Die Datei ist in folgende Felder unterteilt: CDR Description Type Size Accountcode Account Number to use String Src Caller ID Number String Dst Destination Extension String Dcontext Destination Context String Caller ID with Text String Channel Channel Used String Dstchannel Destination channel String Lastapp Last application String Lastdata Last application data String Start Start of call Date/Time Answer Answer of call Date/Time End End of Call Date/Time Duration Time, from dial to hang up Integer (seconds) Billsec Time, from answer to hang up Integer (seconds) Disposition What Happened to the call String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field User defined field String Beispiel einer in eine Tabelle importierten CSV-Datei. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## Account Codes und Automated Message Accounting

Sie können für jeden Kanal Account Codes und amaflags festlegen. Normalerweise geschieht dies in der Konfigurationsdatei des Kanals (z. B. chan_dahdi.conf, pjsip.conf). Der Parameter amaflags definiert, was mit dem CDR-Datensatz geschehen soll. Die möglichen amaflag-Werte sind:

- Default
- Omit
- Billing
- Documentation

Ähnlich wie ein Datensatz für die Abrechnung oder Dokumentation markiert werden kann, kann für jeden Datensatz ein Account Code festgelegt werden. Der Account Code ist eine frei definierbare Zeichenfolge (die `accountcode` endpoint-Option akzeptiert jeden String, und der CDR-Datensatz speichert ihn in einem 80 Zeichen langen Feld), die normalerweise verwendet wird, um einen Datensatz einer Abteilung oder Geschäftseinheit zuzuordnen. Beispiel: pjsip.conf endpoint-Sektion

```
[8576]
type=endpoint
accountcode=Support
```

Das AMA-Flag ist in Asterisk 22 keine `pjsip.conf` endpoint-Option; setzen Sie es pro Anruf über den dialplan mit der `CHANNEL` Funktion (zum Beispiel `Set(CHANNEL(amaflags)=billing)`) oder mit `Set(CDR(amaflags)=billing)`.

## Ändern des CSV- und/oder CDR-Formats

Sie können das CSV-Format ändern, indem Sie die Datei cdr_custom.conf anpassen.

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

Die CDR-Speicherung kann auf verschiedene Arten erfolgen. Die wichtigste Methode sind CSV-Textdateien, die leicht in Tabellenkalkulationen importiert werden können. Für kleine Unternehmen ist dies meist ausreichend. Einige Abrechnungssoftware akzeptiert standardmäßig CSV-Dateien. Das Speichern von CDRs in einer Datenbank ist jedoch wesentlich besser und sicherer. Asterisk unterstützt verschiedene Datenbanktypen. Es gibt einige grafische Oberflächen für die Abrechnung auf dem Markt. Bei so vielen Treibern, welchen sollte man wählen?

### Verfügbare Speichertreiber

- cdr_csv – Comma Separated Value Textdateien
- cdr_adaptive_odbc – Adaptive ODBC-Backend (bevorzugt für die Datenbank-Speicherung)
- cdr_odbc – unixODBC-unterstützte Datenbanken (veraltet; cdr_adaptive_odbc wird bevorzugt)
- cdr_pgsql – Postgres-Datenbanken
- cdr_mysql – MySQL-Datenbanken (**veraltet**; verwenden Sie stattdessen cdr_adaptive_odbc + MySQL ODBC-Treiber)
- cdr_freetds – Sybase- und MSSQL-Datenbanken
- cdr_manager – CDR an Manager Interface
- cdr_radius – CDR Radius-Schnittstelle
- cdr_sqlite3_custom – SQLite3 benutzerdefiniertes CDR-Modul

Die CDR-Aufzeichnung erfolgt für alle aktiven Module, die in der Datei /etc/asterisk/modules.conf geladen sind. Wenn der Parameter autoload=yes gesetzt ist, werden alle Module geladen. Um zu überprüfen, welche cdr_drivers derzeit im System geladen sind, verwenden Sie den folgenden Befehl:

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

Wenn Sie den obigen Screenshot sehen, laufen mindestens cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc und cdr_sqlite3_custom. In den letzten Jahren, nach einigen Astricons, wurde mir klar, dass das Asterisk-Team ODBC bevorzugt. Es ist der einzige Treiber, der Connection Pooling unterstützt. Connection Pooling ist ein großer Vorteil in Bezug auf die Leistung, da Sie nicht für jeden Vorgang eine neue Verbindung öffnen müssen. Dieses Kapitel wurde zuvor unter Verwendung von cdr_mysql geschrieben. Ich bin für diese Ausgabe auf cdr_adaptive_odbc umgestiegen, auch wenn ich weiß, dass die Einrichtung etwas komplexer ist. Die Wahl für cdr_adaptive_odbc ermöglicht uns auch, die CDR anzupassen. Sie können einfach eine neue CDR-Variable im dialplan setzen und die Spalte zur Datenbank hinzufügen. Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### CSV-Speicherung

Wie bereits erwähnt, sendet Asterisk standardmäßig alle CDRs unter Verwendung des Moduls cdr_csv.so an eine CSV-Textdatei. Wenn Sie die Dateien nicht in /var/log/asterisk/cdr-csv sehen können, überprüfen Sie mit dem CLI-Befehl module show, ob das Modul geladen ist. Wenn es nicht geladen ist, überprüfen Sie die modules.conf. In diesem Kapitel werden wir CDRs als Backup an cdr_csv senden.

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

> **[Hinweis zur 2. Auflage]** Die ursprünglichen Schritte zielten auf Ubuntu 18.04 und MySQL Connector/ODBC 8.0.14 ab. Die folgenden Schritte wurden für Ubuntu 22.04 LTS aktualisiert; passen Sie die Paketversionen und Download-URLs an das aktuelle MySQL Connector/ODBC-Release von dev.mysql.com an.

Ich bedauere es immer, detaillierte Anleitungen im Buch zu veröffentlichen. Sie ändern sich manchmal schneller, als das Buch veröffentlicht wird. Versionen ändern sich, Module ändern sich, versuchen Sie also, die Befehle hier an Ihre eigene Situation anzupassen. Meistens reichen geringfügige Änderungen aus, um die Installation zu reproduzieren. Achten Sie auf die Schritte, selbst erfahrene Linux-Benutzer werden die Installation der ODBC-Treiber als schwierig empfinden.

Schritt 1 - Installieren Sie die erforderlichen Pakete:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Schritt 2 - Erstellen Sie eine Datenbank und einen Benutzer:

```
mysql -u root -p
```

(Verwenden Sie das Passwort, das Sie beim Erstellen des MySQL-Servers definiert haben) Geben Sie diese Befehle in der MySQL-Befehlszeile ein

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

Schritt 4: Laden Sie den MySQL ODBC-Connector von Oracle herunter. Überprüfen Sie Ihr Betriebssystem mit: `lsb_release -a`. Für Ubuntu 22.04 (x86_64) besuchen Sie https://dev.mysql.com/downloads/connector/odbc/ und wählen Sie das aktuelle 8.x oder 9.x Release für Ubuntu 22.04.

> **[Hinweis zur 2. Auflage]** Überprüfen Sie die genaue Download-URL und den Dateinamen auf dev.mysql.com; die Versionsnummer und das Ubuntu-Suffix werden von der 1. Auflage abweichen. Das folgende Beispiel verwendet eine Platzhalterversion.

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

Schritt 7: Testen Sie den Treiberzugriff mit iSQL. iSQL ist ein Befehlszeilen-Dienstprogramm, um sich über unixodbc mit der Datenbank zu verbinden.

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

> **[Hinweis zur 2. Auflage]** Der ursprüngliche Text verwendete die Anwendung `NoCDR()`. `NoCDR` wurde als veraltet markiert und dann in Asterisk 21 entfernt; verwenden Sie stattdessen `Set(CDR_PROP(disable)=1)`.

### ResetCDR()

Setzt den Call Data Record zurück: Die `start` Zeit (und, falls beantwortet, die `answer` Zeit) wird auf die aktuelle Zeit gesetzt und alle CDR-Variablen werden gelöscht. Wenn die `v` Option gesetzt ist, bleiben die CDR-Variablen während des Zurücksetzens erhalten.

### Set(CDR(userfield)=Value)

Dieser Befehl setzt ein Benutzerfeld im CDR. Bei Verwendung von `cdr_adaptive_odbc` wird das Benutzerfeld automatisch gespeichert, wenn eine `userfield` Spalte in der CDR-Tabelle existiert — eine Neukompilierung der Quelle ist nicht erforderlich. Für CSV-Textdateien müssen Sie den Quellcode (cdr_csv.c) bearbeiten und Asterisk neu kompilieren, wenn Sie Benutzerfelder verwenden möchten.

> **[Hinweis zur 2. Auflage]** Der ursprüngliche Text verwies auf `cdr_addon_mysql` und `cdr_mysql.conf`. Das Modul `cdr_mysql` ist in Asterisk 22 veraltet; der empfohlene Weg ist `cdr_adaptive_odbc` mit einem MySQL ODBC-Treiber, der Benutzerfelder nativ über das adaptive Spalten-Mapping unterstützt.

### AppendCDRUserField(Value)

Hängt Daten an das Benutzerfeld im CDR an.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Benutzerauthentifizierung

Einige Unternehmen stellen ihren Mitarbeitern die Anrufe in Rechnung. In Asterisk können Sie ein Authentifizierungsschema einrichten, das es Ihnen ermöglicht, den authentifizierten Benutzer im CDR abzurechnen. Diese Authentifizierung kann mit einem Passwort erfolgen, das als Parameter an die Authenticate-Anwendung übergeben wird — eine Passwortdatei, die durch einen / (Schrägstrich) vor dem Parameter gekennzeichnet ist, oder eine Asterisk-Datenbank (dbput/dbget). Format:

```
Authenticate(password[|options])
Authenticate(/passwdfile|[|options])
Authenticate(</db-keyfamily|d>options)
```

Optionen:

- a – Setzt den Account Code als Passwort.
- d – Interpretiert den Parameter als Asterisk DB-Schlüssel
- r – Entfernt den Schlüssel nach erfolgreicher Authentifizierung (nur mit der Option ´d´)
- j – Springt bei ungültiger Authentifizierung zur Priorität n+101

Beispiel: (Internationale Anrufe)

```
exten=_9011.,1,Authenticate(/password|daj)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

Um das Passwort von der Konsole aus in einen DB-Schlüssel einzufügen:

```
CLI> database put senha 123456 1
```

## Verwendung von Passwörtern aus der Voicemail

Diese Anwendung bewirkt dasselbe wie authenticate, verwendet jedoch die Voicemail-Konfigurationsdatei für das Passwort.

```
VMAuthenticate([mailbox][@context][|options])
```

Wenn ein Postfach angegeben ist, wird nur das Postfach-Passwort als gültig betrachtet. Wenn das Postfach nicht angegeben ist, wird eine Kanalvariable AUTH_MAILBOX mit dem authentifizierten Postfach gesetzt. Wenn die Option ´s´ (silent) gesetzt ist, wird keine Aufforderung ausgeführt. Beispiel: (Internationale Anrufe)

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local|ajs)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

## Channel Event Logging (CEL)

CDR-Datensätze liefern eine Zusammenfassungszeile pro Anruf. Für eine detailliertere Ereignisverfolgung — wie individuelle Kanalzustandsübergänge, Bridge-Eintritts-/Austrittsereignisse und vermittelte Transfer-Abschnitte — enthält Asterisk 22 **Channel Event Logging (CEL)**, das über `/etc/asterisk/cel.conf` konfiguriert und über Backends wie `cel_odbc` oder `cel_custom` gespeichert wird.

CEL ergänzt CDR, anstatt es zu ersetzen: CDR bleibt der Standard für Abrechnungszusammenfassungen, während CEL granulare Daten pro Ereignis liefert, die für Betrugserkennung, Qualitätsüberwachung und fortgeschrittene Berichterstattung nützlich sind.

> **[Hinweis zur 2. Auflage]** Erwägen Sie das Hinzufügen eines kurzen CEL-Unterabschnitts oder eines Vorwärtsverweises auf ein fortgeschrittenes Abrechnungskapitel, falls der Lehrplan dies abdeckt. Das `cel.conf` Konfigurationsmuster spiegelt `cdr.conf` wider.

## Zusammenfassung

In diesem Kapitel haben wir gelernt, wie man die CDR-Aufzeichnung in Textdateien und in einer MySQL-Datenbank implementiert. Wir haben auch gelernt, wie man amaflags und Account Codes setzt. Am Ende des Kapitels haben wir gelernt, wie man ein Authentifizierungsschema verwendet, das in CDR und Abrechnung integriert ist.

## Quiz

1. Standardmäßig zeichnet Asterisk das CDR im Verzeichnis /var/log/asterisk/cdr-csv auf.
   - A. Falsch
   - B. Wahr
2. Asterisk kann CDRs schreiben an (wählen Sie alle zutreffenden aus):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV-Textdateien
   - E. unixODBC-unterstützte Datenbanken
3. Asterisk generiert ein CDR jeweils nur für eine Art der Speicherung.
   - A. Falsch
   - B. Wahr
4. Welche Asterisk amaflags sind verfügbar?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Um eine Abteilung mit einem CDR zu verknüpfen, verwenden Sie den Befehl ___, und der Account Code kann mit der Kanalvariablen ___ gelesen werden.
6. Der Unterschied zwischen `Set(CDR_PROP(disable)=1)` und `ResetCDR()` besteht darin, dass das Deaktivieren des CDR verhindert, dass ein Datensatz geschrieben wird, während `ResetCDR()` den aktuellen Datensatz zurücksetzt (auf Null setzt). (Die Anwendung `NoCDR()`, die zuvor CDRs deaktivierte, wurde in Asterisk 21 entfernt.)
   - A. Falsch
   - B. Wahr
7. Um ein benutzerdefiniertes Feld mit dem Modul `cdr_csv.so` zu verwenden, müssen Sie den Quellcode bearbeiten und Asterisk neu kompilieren.
   - A. Falsch
   - B. Wahr
8. Die drei Authentifizierungsmethoden, die für die Anwendung Authenticate() verfügbar sind, sind:
   - A. Passwort
   - B. Passwortdatei
   - C. Asterisk DB (dbput und dbget)
   - D. Voicemail
9. Voicemail-Passwörter werden in einem separaten Abschnitt von `voicemail.conf` angegeben und sind nicht dieselben wie die der Voicemail-Benutzer.
   - A. Falsch
   - B. Wahr
10. Channel Event Logging (CEL) ersetzt CDR in Asterisk 22 — sobald CEL aktiviert ist, werden keine CDR-Abrechnungszusammenfassungen mehr erstellt.
    - A. Falsch
    - B. Wahr

**Antworten:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
