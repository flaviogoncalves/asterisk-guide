# Asterisk Real-Time

Come sapete, la configurazione di Asterisk avviene tramite l'uso di diversi file di testo nella directory /etc/asterisk. Nonostante la semplicità di utilizzo dei file di testo, esistono alcuni svantaggi noti:

- La necessità di ricaricare Asterisk ogni volta che i file vengono modificati
- Maggiore utilizzo di memoria per un grande volume di utenti
- È difficile scrivere un'interfaccia di provisioning usando file di testo
- Nessuna possibilità di integrazione con database esistenti

ARA o Asterisk Realtime, come è conosciuto, è stato creato da Anthony Minessale II, Mark Spencer e Constantine Filin ed è stato progettato per consentire un'integrazione trasparente con database SQL. È disponibile anche un'interfaccia LDAP. Questo sistema è noto anche come Asterisk External Configuration ed è configurato in /etc/asterisk/extconfig.conf. È possibile mappare i file di configurazione a tabelle in un database (configurazione statica) e le voci in tempo reale per la creazione dinamica di oggetti senza la necessità di ricaricare Asterisk.

## Objectives

By the end of this chapter, the reader should be able to:

- Understand advantages and limitations of Asterisk Real Time.
- Use ODBC for use with ARA
- Compile and install ARA using ODBC
- Test the system in a lab environment

## Come funziona Asterisk Real Time?

Nella nuova architettura Real Time, tutto il codice specifico del database è stato spostato nei driver dei canali. Il canale chiama solo una routine generica che ricerca nel database. Il risultato è un processo molto più semplice e pulito dal punto di vista del codice sorgente. Il database è accessibile tramite tre funzioni:

- STATIC: Utilizzata per impostare una configurazione statica quando un modulo viene caricato.
- REALTIME: Utilizzata per cercare oggetti durante una chiamata o un altro evento.


- UPDATE: Utilizzata per aggiornare gli oggetti.

Su Asterisk 22, gli endpoint SIP sono gestiti dallo stack **PJSIP** (`res_pjsip`), che è basato sul modello di oggetti **Sorcery**. Con la procedura guidata `realtime`, Sorcery carica ogni oggetto PJSIP dal database su richiesta, e quegli oggetti esistono quindi come normali oggetti PJSIP configurati — non come i peer realtime temporanei che il vecchio driver SIP scartava dopo ogni chiamata.

Poiché sono oggetti reali, il traversal NAT, la qualificazione e l'indicazione di messaggi in attesa (MWI) funzionano normalmente per gli endpoint realtime. (Sorcery può inoltre essere configurato per memorizzare gli oggetti nella cache in memoria tramite una procedura guidata `memory_cache`, ma ciò è opzionale e separato dal caricamento realtime.) Quando si modifica un oggetto nel database, la modifica viene rilevata al successivo lookup; non è necessario ricaricare dopo ogni modifica. (Il modello realtime ritirato `chan_sip`, con le sue famiglie `sippeers`/`sipusers`, è trattato solo nel capitolo *Legacy Channels*.)

## Configurare Asterisk Real Time

Per questo laboratorio, supporremo che tu abbia già installato ODBC dal capitolo CDR. ARA è configurato nel file di testo extconfig.conf, dove sono facilmente visibili due sezioni. La prima è la sezione dei file di configurazione statici, dove puoi sostituire i file di configurazione testuali con tabelle di database. La seconda sezione è il motore di configurazione realtime, dove configuri le tabelle di database per oggetti dinamici (peer/utente). Non è insolito usare file di testo per la configurazione statica e il database per le voci dinamiche. In questo caso, la prima sezione rimane intatta.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Architettura Asterisk Real Time: i file di configurazione e le tabelle statiche del database vengono caricati all'avvio di Asterisk, mentre le tabelle realtime del database forniscono configurazioni dinamiche lette su richiesta durante una chiamata.](../images/18-realtime-fig01.png)

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


### Sezione di configurazione statica

La sezione di configurazione statica è dove memorizzi l'equivalente dei file di configurazione nel database. Queste configurazioni vengono lette durante il caricamento di Asterisk. Alcuni moduli rilegono il database quando esegui un reload. Esempi di configurazione statica sono:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

Il mapping di file statici è più utile per i file di configurazione che non hanno un equivalente realtime per oggetto. Per PJSIP, preferisci le famiglie realtime per oggetto (`ps_endpoints`, `ps_aors`, ecc.) descritte più avanti in questo capitolo piuttosto che mappare l'intero `pjsip.conf` come file statico.

Tre esempi sono descritti sopra. Nel primo, associ queues.conf a una tabella queues nel database asteriskdb. Nel secondo esempio, associ pjsip.conf alla tabella pjsip_conf nel database asteriskdb definito nella configurazione odbc. Nell'ultimo esempio, associ iax.conf a una directory LDAP. MyBaseDN è il DN di base da cercare. Nell'esempio precedente, il modulo app_queue.so viene caricato mentre il driver MySQL interroga il database e ottiene le informazioni richieste.

### Sezione di configurazione Real Time

La configurazione realtime (seconda parte del file extconfig.conf) è dove il pezzo di configurazione da caricare viene configurato, aggiornato e scaricato in tempo reale. Con il realtime non è necessario ricaricare le configurazioni. La sintassi realtime è la seguente:

```
<family name> => <driver>,<database name>[,table_name]
```

Esempio:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Qui abbiamo cinque righe di configurazione. Nella prima riga, associ la famiglia PJSIP/Sorcery `ps_endpoints` a una tabella `ps_endpoints` nel database asteriskdb. Nell'ultima, associ la famiglia voicemail alla tabella test nel database asteriskdb. Ogni tipo di oggetto PJSIP (endpoint, aor, auth, contact) ottiene la propria famiglia e tabella; l'insieme completo è mostrato nella sezione "PJSIP Realtime (Sorcery)" qui sotto. Le famiglie `voicemail`, `extensions`, `queues` e `queue_members` sono ancora valide in Asterisk 22.

## PJSIP Realtime (Sorcery)

Su Asterisk 22, gli endpoint SIP sono gestiti esclusivamente dallo stack **PJSIP** (`res_pjsip`), che è costruito sul livello di astrazione degli oggetti **Sorcery**. Invece di un unico “peer” SIP, PJSIP suddivide un account SIP in diversi tipi di oggetti, ciascuno memorizzato nella propria tabella realtime:

| Tipo di oggetto Sorcery | Tabella realtime | Cosa contiene |
|--------------------------|------------------|----------------|
| endpoint | ps_endpoints | impostazioni per account (context, codec, DTMF, ecc.) |
| aor (address of record) | ps_aors | limiti di registrazione e impostazioni `qualify` |
| auth | ps_auths | credenziali `username` / `password` |
| contact | ps_contacts | la posizione registrata dinamicamente |
| domain alias | ps_domain_aliases | domini SIP alternativi per un endpoint |
| endpoint identifier by IP | ps_endpoint_id_ips | associazione di un endpoint all'IP di origine |

Il realtime per PJSIP è abilitato in due punti. Prima, mappa i tipi di oggetto Sorcery al realtime in `extconfig.conf`:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Secondo, indica a Sorcery di usare la procedura guidata `realtime` per quei tipi di oggetto in `sorcery.conf`. Il nome della mappatura (qui `res_pjsip`) è il modulo i cui oggetti stai spostando, e il valore a destra punta alla famiglia che hai definito in `extconfig.conf`:

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

Puoi mescolare oggetti statici e realtime. Se ometti un tipo da `sorcery.conf`, quel tipo di oggetto continua a leggere da `pjsip.conf`. Un modello comune è mantenere i trasporti statici e le impostazioni globali in `pjsip.conf` mentre si memorizzano endpoint, aors, auths e contacts nel database.

### Creazione dello schema realtime PJSIP con Alembic

Asterisk fornisce migrazioni di database per tutti i suoi schemi realtime sotto `contrib/ast-db-manage`. Questo è il modo supportato per creare (e aggiornare di versione) le tabelle PJSIP — non è più necessario scrivere manualmente le definizioni delle tabelle `ps_*`. Il set di migrazioni `config` contiene le tabelle PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Questo crea `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` e le altre tabelle PJSIP con le colonne corrette per la versione di Asterisk in esecuzione. (Alembic richiede il pacchetto Python `alembic` più un driver SQLAlchemy come `pymysql` per MySQL/MariaDB o `psycopg2` per PostgreSQL.)

Un endpoint realtime minimale consiste quindi in una riga in ciascuna delle tre tabelle — ad esempio l'endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Dopo aver inserito le righe non è necessario ricaricare nulla — il successivo REGISTER/INVITE preleverà gli oggetti dal database. Puoi confermare ciò che il realtime ha restituito con:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Configurazione del database

Ora che abbiamo configurato il file extconfig.conf, creiamo le tabelle. In generale, ogni colonna del database corrisponde a un nome di opzione del relativo file di configurazione. Le tabelle PJSIP `ps_*` seguono questa regola: ogni colonna `ps_endpoints` è denominata come un'opzione endpoint `pjsip.conf`, ogni colonna `ps_auths` come un'opzione auth, e così via. Per esempio, l'endpoint `pjsip.conf` qui sotto,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

viene memorizzato come una riga distribuita su tre tabelle. La riga `ps_endpoints` contiene `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; la riga `ps_auths` contiene `id=4000, auth_type=userpass, username=4000, password=supersecret`; e la riga `ps_aors` contiene `id=4000, max_contacts=1`. È necessario popolare solo le colonne che si usano realmente — qualsiasi colonna lasciata NULL riprenderà il valore predefinito dell'opzione. Se si desidera, ad esempio, il parametro `callerid` su un endpoint, compilare la colonna `callerid` di `ps_endpoints` (il nome della colonna è lo stesso del nome dell'opzione `pjsip.conf`).

Una tabella voicemail segue lo stesso concetto. Le sue colonne corrispondono ai campi `voicemail.conf`:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

Il `uniqueid` deve essere unico per ogni utente voicemail e può essere autoincrementante. Non è necessario che abbia alcuna relazione con la mailbox o il context.

### Creazione di un dialplan usando Asterisk Real Time

È possibile utilizzare anche il sistema real‑time per creare il dialplan. ARA usa l'istruzione `switch` per includere le estensioni real‑time nel dialplan normale contenuto nel file extensions.conf. La tabella delle estensioni dovrebbe apparire come quella sotto:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

La famiglia realtime `extensions` è invariata in Asterisk 22; basta assicurarsi che la colonna `appdata` effettui chiamate ai canali PJSIP, ad esempio `PJSIP/4000`. Nel dialplan, è necessario usare il comando `switch` per utilizzare il real time.

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

In questo laboratorio, prepareremo il database per ricevere i parametri di Asterisk. Prepariamo solo le tabelle REALTIME. La configurazione statica verrà lasciata ai file di testo di configurazione (fantastico, vero?). La creazione delle tabelle in MySQL segue.

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

## Lab: Configurare e testare ARA

In questo laboratorio cambieremo la configurazione di **extconfig.conf** per riflettere la nostra configurazione del database e le tabelle.

Passo 1: Configurare **extconfig.conf** e ricaricare Asterisk.

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

Nota le famiglie `ps_endpoints`, `ps_aors`, `ps_auths` e `ps_contacts` sopra; insieme alle corrispondenti mappature `sorcery.conf` (vedi la sezione “PJSIP Realtime (Sorcery)”) fanno sì che PJSIP legga i propri account dal database. Le famiglie `voicemail` e `extensions` completano l’esempio.

Passo 2: Test dell’estensione Real Time. Crea un nuovo endpoint `6010` inserendo una riga in ciascuna delle tabelle `ps_auths`, `ps_aors` e `ps_endpoints`, quindi prova a registrare questo endpoint con un softphone. Esegui il seguente SQL nel client `mysql` (`mysql -u astdb -p astdb`):

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

Le tre righe insieme descrivono un account SIP. Le impostazioni rimanenti dell’account sono distribuite negli oggetti PJSIP: context, codec, modalità DTMF e gestione dei media presenti direttamente sull’endpoint (le ultime sei colonne sopra); la registrazione dinamica vive sull’AOR. Non esiste un flag “dynamic” separato — un AOR accetta REGISTER dinamici finché `max_contacts` è maggiore di zero, e ogni posizione registrata viene scritta in `ps_contacts`.

In PJSIP la modalità DTMF out‑of‑band RFC 2833 / RFC 4733 è chiamata `rfc4733`, e `dtmf_mode=rfc4733` è il valore predefinito — quindi la colonna `dtmf_mode` sopra è opzionale e mostrata solo per chiarezza.

Passo 3: Prova a registrare il nuovo telefono con un softphone usando lo username `6010` e la password `supersecret`. Conferma la registrazione sulla CLI di Asterisk:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Passo 4: Includere le estensioni nel database.

```
mysql -u astdb -p
```

Inserisci la password:

Usa **supersecret** quando richiesto, quindi inserisci la riga dell’estensione dal client MySQL:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Passo 5: Includere Asterisk Real Time nel dialplan. Nel context `default`:

```
switch => realtime/test@extensions
```

Ricarica le estensioni per attivare la modifica.

```
asterisk-server*CLI> extensions reload
```

Passo 6: Riconfigura uno dei telefoni con lo username `bria`, se non lo hai già fatto.

Passo 7: Componi 6007 da un telefono esistente; il telefono `bria` dovrebbe squillare.

## Sommario

In questo capitolo hai appreso che Asterisk Real Time ti consente di inserire le tue configurazioni in un database. Asterisk fornisce driver realtime nativi per ODBC (che raggiunge qualsiasi database supportato da UnixODBC, inclusi MySQL/MariaDB e SQLite) e PostgreSQL, oltre a un driver realtime LDAP per backend di directory. MySQL/MariaDB è raggiunto tramite ODBC, come abbiamo fatto in questo capitolo (esiste anche un add‑on dedicato `res_config_mysql`, ma vive al di fuori del core, quindi ODBC è il percorso comune). La configurazione è divisa in statica e realtime. La configurazione statica sostituisce i file di configurazione, mentre quella realtime crea oggetti dinamici che vengono caricati solo quando avviene una chiamata o un altro evento correlato. Abbiamo concluso con un laboratorio pratico su come installare e configurare ARA.

## Quiz

1. Asterisk Realtime è parte della distribuzione standard di Asterisk.
   - A. Vero
   - B. Falso
2. I parametri di connessione di un server di database sono configurati nel file:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. Il file `extconfig.conf` configura le tabelle usate da Realtime. Ha due sezioni distinte (seleziona due):
   - A. Configurazione statica
   - B. Configurazione Realtime
   - C. Rotte in uscita
   - D. Indirizzi IP e porte del database
4. Nella configurazione statica, una volta che gli oggetti sono caricati dal database rimangono nella memoria di Asterisk e vengono aggiornati solo all’avvio o al reload.
   - A. Vero
   - B. Falso
5. PJSIP realtime (Sorcery) supporta pienamente `qualify` e MWI per gli endpoint realtime, perché Sorcery li carica come normali oggetti PJSIP configurati anziché scartarli dopo ogni chiamata come avveniva per i vecchi peer SIP realtime.
   - A. Vero
   - B. Falso
6. In PJSIP realtime, quali tabelle contengono gli endpoint e i loro contatti registrati?
   - A. `ps_endpoints` e `ps_contacts`
   - B. `ps_peers` e `ps_registry`
   - C. `ps_config` e `ps_data`
   - D. `extconfig` e `res_odbc`
7. È ancora possibile utilizzare file di configurazione testuali anche dopo aver abilitato ARA.
   - A. Vero
   - B. Falso
8. phpMyAdmin è obbligatorio quando si usa Realtime.
   - A. Vero
   - B. Falso
9. Il database deve essere creato con tutti i campi che esistono nel file di configurazione.
   - A. Vero
   - B. Falso
10. Su Asterisk 22, qual è il modo consigliato e corretto per versione di creare le tabelle realtime PJSIP (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`)?
    - A. Scrivere manualmente le istruzioni `CREATE TABLE` per ogni tabella `ps_*`
    - B. Importare il legacy `mysql_config.sql` da `contrib/realtime/`
    - C. Eseguire le migrazioni Alembic `config` sotto `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)
    - D. Le tabelle vengono create automaticamente al primo avvio di Asterisk

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
