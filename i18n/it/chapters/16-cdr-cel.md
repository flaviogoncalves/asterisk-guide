# Registri Dettaglio Chiamate Asterisk

Asterisk, come altre piattaforme telefoniche, consente la fatturazione delle chiamate. Numerosi programmi sul mercato possono importare i record generati dai PBX. Questi record sono usati per verificare l'importo corretto della bolletta e le statistiche, tra le altre cose.

## Obiettivi

Entro la fine di questo capitolo, il lettore dovrebbe essere in grado di:

- Descrivere dove e in quale formato vengono generati i record
- Generare record usando ODBC (Open Database Connectivity)
- Implementare uno schema di autenticazione integrato con la fatturazione

## Formato CDR di Asterisk

Asterisk genera un record di dettaglio chiamata (CDR) per ogni chiamata. Questi record sono memorizzati, per impostazione predefinita, in un file di testo in formato valore separato da virgole (CSV) in **/var/log/asterisk/cdr-csv**. Il file è organizzato nei seguenti campi:

| Campo | Descrizione | Tipo |
|-------|-------------|------|
| Accountcode | Numero di conto da utilizzare | String |
| Src | Numero ID chiamante | String |
| Dst | Interno di destinazione | String |
| Dcontext | Contesto di destinazione | String |
| Clid | ID chiamante con testo | String |
| Channel | Canale utilizzato | String |
| Dstchannel | Canale di destinazione | String |
| Lastapp | Ultima applicazione | String |
| Lastdata | Dati dell'ultima applicazione | String |
| Start | Inizio della chiamata | Date/Time |
| Answer | Risposta della chiamata | Date/Time |
| End | Fine della chiamata | Date/Time |
| Duration | Tempo, dal dial al riaggancio | Integer (seconds) |
| Billsec | Tempo, dalla risposta al riaggancio | Integer (seconds) |
| Disposition | Cosa è accaduto alla chiamata (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | Flag (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | Campo definito dall'utente | String |

Esempio di file CSV. Ogni riga è un record; i campi compaiono nello stesso ordine della tabella sopra (`accountcode` per primo, `amaflags` per ultimo):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Codici conto e contabilizzazione dei messaggi automatici

È possibile specificare codici conto e flag ama su ogni canale. Di solito ciò avviene nel file di configurazione del canale (ad es., chan_dahdi.conf, pjsip.conf). Il parametro amaflags definisce cosa fare con il record CDR. I possibili valori di amaflag sono:

- Default
- Omit
- Billing
- Documentation

Simile al modo in cui un record può essere contrassegnato per fatturazione o documentazione, un codice conto può essere impostato su ogni record. Il codice conto è una stringa libera (l’opzione endpoint `accountcode` accetta qualsiasi String, e il record CDR lo memorizza in un campo di 80 caratteri) solitamente usata per assegnare un record a un dipartimento o a un'unità aziendale. Esempio: sezione endpoint di pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

Il flag AMA non è un’opzione endpoint `pjsip.conf` in Asterisk 22; impostalo per chiamata dal dialplan con la funzione `CHANNEL` (ad esempio `Set(CHANNEL(amaflags)=billing)`), o con `Set(CDR(amaflags)=billing)`.

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

CDR storage can be achieved in several ways. The most important way is CSV text files that can be easily imported into spreadsheets. For small businesses, this is usually okay. Some billing software accepts, by default, CSV files. However, storing CDRs in a database is a lot better and safer. Asterisk supports several database flavors. There are some graphical interfaces for billing in the market. With so many drivers, which one to choose?

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

The `cdr_addon_mysql` (cdr_mysql) module that older guides recommended was removed in Asterisk 19, so there is no native MySQL CDR driver on Asterisk 22. To write CDRs to MySQL/MariaDB, use `cdr_adaptive_odbc` together with a MySQL ODBC driver — the approach used in this chapter.

CDR recording is done to all active modules loaded in the file /etc/asterisk/modules.conf. If the parameter autoload=yes is set, all modules are loaded. To check which cdr_drivers are currently loaded in the system use the command below:

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

If you see the screenshot above, at least cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc and cdr_sqlite3_custom are running. In the latest years after some astricons it become clear for me the Asterisk team was favoring ODBC. It is the only driver supporting connection pooling. Connection pooling is a great advantage in terms of performance because you don’t have to open a new connection for every operation. This chapter was previously written using cdr_mysql. I have moved to cdr_adaptive_odbc for this edition even knowing that it is a little more complex to setup. The choice for cdr_adaptive_odbc also allows us to customize the CDR. You may simply set a new CDR variable in the dialplan and add the matching column to the database. For example, to record the audio jitter:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV Storage

As we said before, by default, Asterisk sends all CDR to a CSV text file using the cdr_csv.so module. If you can’t see the files in the /var/log/asterisk/cdr-csv, check to see if the module is being loaded using the CLI command module show. If it’s not loaded, check modules.conf. In this chapter we will send cdrs to cdr_csv as a backup.

### Configuring the file modules.conf

To load only the appropriate modules, use the lines below in the modules.conf file

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Now we have only cdr_csv and cdr_adaptive_odbc loaded.

## Installazione e configurazione di ODBC su Ubuntu 22.04

Mi rammarico sempre di pubblicare istruzioni dettagliate nel libro. A volte cambiano prima che il libro venga pubblicato. Le versioni cambiano, i moduli cambiano, quindi cerca di adattare il comando qui alla tua situazione. Nella maggior parte dei casi sono sufficienti modifiche minori per riprodurre l'installazione. Presta attenzione ai passaggi che anche gli utenti Linux esperti troveranno difficili per installare i driver ODBC.

Passo 1 - Installa i pacchetti richiesti:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Passo 2 - Crea un database e un utente:

```
mysql -u root -p
```

(Usa la password definita quando hai creato il server mysql) Digita questi comandi nella riga di comando di mysql

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Passo 3 - Crea il database

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Passo 4: Scarica il connettore MySQL ODBC da Oracle. Controlla il tuo sistema operativo usando: `lsb_release -a`. Per Ubuntu 22.04 (x86_64), visita https://dev.mysql.com/downloads/connector/odbc/ e scegli la versione corrente 8.x o 9.x per Ubuntu 22.04. Il nome esatto del file e il numero di versione cambiano nel tempo, quindi imposta `VER` (sotto) a qualunque sia il nome della build Linux glibc attuale.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Passo 5: Installa il driver ODBC

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Passo 6 - Configura il connettore ODBC modificando il file /etc/odbc.ini per creare il DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Passo 7: Verifica l'accesso al driver usando iSQL. iSQL è un'utilità a riga di comando per connettersi al database tramite unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Per favore, non procedere con la configurazione di Asterisk se non riesci a vedere il risultato del comando isql.

### Configurazione di ODBC in Asterisk

Prima di poter configurare cdr_adaptive_odbc, devi prima configurare il file di risorsa ODBC.

Passo 1 - Collega Asterisk a ODBC. Modifica il file res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Passo 2 – Riavvia Asterisk e testa usando

```
asterisk*CLI> odbc show
```

L'output è mostrato di seguito.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Passo 3 – Configura il driver ODBC adattivo in /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Qui `connection` punta alla sezione di connessione `[cdr]` definita in `res_odbc.conf`, e `table` è la tabella del database dove vengono scritti i CDR.

Passo 4 – Ricarica il modulo cdr_adaptive_odbc.so:

```
asterisk*CLI> reload cdr_adaptive_odbc
```

Passo 5 – Effettua le stesse chiamate e controlla il database per nuovi record. Per controllare il database:

```
mysql -u root -p
>use astdb
>select * from cdr;
```

## Applicazioni e funzioni

Diversi applicazioni sono correlate alla fatturazione.

### CDR(accountcode)

Imposta un codice account prima di chiamare un'altra applicazione dial(); per esempio: Formato:

```
Set(CDR(accountcode)=account)
```

Il codice account può essere verificato usando la variabile di canale ${CDR(accountcode)}

### CDR(amaflags)

Imposta un flag a scopo di fatturazione. Le opzioni sono default, omit, documentation e billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Disabilita la registrazione CDR per il canale corrente, quindi nessun CDR viene scritto su file o database. Ripristinandolo a `0` riattiva la registrazione.

```
Set(CDR_PROP(disable)=1)
```

L’applicazione `NoCDR()` che le edizioni precedenti usavano per questo è stata rimossa in Asterisk 21; in Asterisk 22 si disabilita il CDR di un canale con `Set(CDR_PROP(disable)=1)` invece.

### ResetCDR()

Reimposta il Call Data Record: il tempo `start` (e, se risposto, il tempo `answer`) viene impostato all’ora corrente e tutte le variabili CDR vengono cancellate. Se l’opzione `v` è impostata, le variabili CDR vengono conservate durante il reset.

### Set(CDR(userfield)=Value)

Questo comando imposta un campo utente nel CDR. Quando si usa `cdr_adaptive_odbc`, il campo utente viene memorizzato automaticamente se esiste una colonna `userfield` nella tabella CDR — non è necessaria la ricompilazione della sorgente. Per i file di testo CSV, è necessario modificare il codice sorgente (cdr_csv.c) e ricompilare Asterisk se si vogliono usare i campi utente.

Le edizioni precedenti memorizzavano i CDR in MySQL con il modulo `cdr_addon_mysql` (`cdr_mysql.conf`). Quel modulo è stato rimosso in Asterisk 19, quindi non è disponibile in Asterisk 22. Il percorso supportato ora è `cdr_adaptive_odbc` con un driver MySQL ODBC, che memorizza il campo utente — e qualsiasi altra colonna personalizzata — nativamente tramite la sua mappatura adattiva delle colonne.

### Aggiunta al campo utente

Le edizioni precedenti usavano l’applicazione `AppendCDRUserField()` per aggiungere dati al campo utente CDR. Quell’applicazione è stata rimossa da Asterisk; in Asterisk 22 si aggiunge al campo utente leggendo e reimpostandolo con la funzione `CDR`, per esempio

`Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## User authentication

Alcune aziende fatturano le chiamate ai propri dipendenti. In Asterisk è possibile impostare uno schema di autenticazione che consente di addebitare l'utente autenticato sul CDR. Questa autenticazione può essere eseguita usando una password passata come parametro all'applicazione Authenticate—un file di password, indicato da una / (barra) prima del parametro, o una chiave del database di Asterisk (usando l'opzione `d`). Formato:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Opzioni:

- a – Imposta il codice account del canale sulla password inserita.  
- d – Interpreta il percorso fornito come chiave del DB di Asterisk anziché come file letterale.  
- m – Interpreta il percorso come un file di righe `accountcode:passwordhash`.  
- r – Rimuove la chiave del database dopo un'autenticazione riuscita (valido solo con `d`).

Se il chiamante esaurisce tutti e tre i tentativi, il canale viene chiuso; l'esecuzione del dialplan non continua, quindi gestire il percorso di errore sulla riga successiva a `Authenticate()`. Esempio (Chiamate internazionali):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

L'opzione `j` (salta alla priorità n+101 in caso di errore) e la convenzione di priorità `+101` sono state rimosse da Asterisk molto tempo fa; un `Authenticate()` fallito semplicemente chiude la chiamata.

Per inserire la password in una chiave DB dalla console:

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

I record CDR forniscono una riga di riepilogo per chiamata. Per un tracciamento più dettagliato degli eventi — come le transizioni di stato dei singoli canale, gli eventi di ingresso/uscita dal bridge e le gambe di trasferimento assistito — Asterisk 22 include **Channel Event Logging (CEL)**, configurato tramite `/etc/asterisk/cel.conf` e memorizzato attraverso backend come `cel_odbc` o `cel_custom`.

CEL completa i CDR invece di sostituirli: i CDR rimangono lo standard per i riepiloghi di fatturazione, mentre CEL fornisce dati granulari per evento utili per la rilevazione delle frodi, il monitoraggio della qualità e la generazione di report avanzati.

Il modello di configurazione `cel.conf` rispecchia `cdr.conf`: si abilitano i tipi di evento desiderati nella sezione `[general]` di `cel.conf`, quindi si configura ogni backend di memorizzazione nel proprio file — `cel_custom.conf` per CSV, `cel_odbc.conf` per un database ODBC (la stessa connessione `res_odbc.conf` usata per i CDR). È possibile verificare se CEL è attivo con `cel show status` sulla CLI.

## Sommario

In questo capitolo abbiamo imparato come implementare la registrazione dei CDR in file di testo e in un database MySQL. Abbiamo anche imparato come impostare amaflags e codici di conto. Alla fine del capitolo, abbiamo imparato come utilizzare uno schema di autenticazione integrato con CDR e fatturazione.

## Quiz

1. Per impostazione predefinita, Asterisk registra il CDR nella directory /var/log/asterisk/cdr-csv.
   - A. False
   - B. True
2. Asterisk può scrivere i CDR su (seleziona tutte le opzioni valide):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. File di testo CSV
   - E. database supportati da unixODBC
3. Asterisk genera un CDR per un solo tipo di archiviazione alla volta.
   - A. False
   - B. True
4. Quali amaflags di Asterisk sono disponibili?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Per associare un dipartimento a un CDR si usa il comando ___, e il codice account può essere letto con la variabile di canale ___.
6. La differenza tra `Set(CDR_PROP(disable)=1)` e `ResetCDR()` è che disabilitare il CDR impedisce che venga scritto qualsiasi record, mentre `ResetCDR()` azzera (resetta) il record corrente. (L’applicazione `NoCDR()` che in precedenza disabilitava i CDR è stata rimossa in Asterisk 21.)
   - A. False
   - B. True
7. Per usare un campo definito dall’utente con il modulo `cdr_csv.so`, è necessario modificare il codice sorgente e ricompilare Asterisk.
   - A. False
   - B. True
8. I tre metodi di autenticazione disponibili per l’applicazione Authenticate() sono:
   - A. Password
   - B. File di password
   - C. Asterisk DB (dbput e dbget)
   - D. Voicemail
9. Le password della segreteria telefonica sono specificate in una sezione separata di `voicemail.conf` e non sono le stesse degli utenti della segreteria telefonica.
   - A. False
   - B. True
10. Channel Event Logging (CEL) sostituisce il CDR in Asterisk 22 — una volta abilitato il CEL, i riepiloghi di fatturazione del CDR non vengono più prodotti.
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
