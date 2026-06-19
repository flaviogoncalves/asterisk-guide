# Asterisk Real-Time

Come saprai, la configurazione di Asterisk si ottiene attraverso l'uso di diversi file di testo nella directory /etc/asterisk. Nonostante la facilità di utilizzo dei file di testo, ci sono alcuni svantaggi noti:

- La necessità di ricaricare Asterisk ogni volta che i file vengono modificati
- Maggiore utilizzo di memoria per un grande volume di utenti
- Difficoltà nel programmare un'interfaccia di provisioning utilizzando file di testo
- Nessuna possibilità di integrazione con database esistenti

ARA, o Asterisk Realtime, come è noto, è stato creato da Anthony Minessale II, Mark Spencer e Constantine Filin ed è stato progettato per consentire un'integrazione trasparente con database SQL. È disponibile anche un'interfaccia LDAP. Questo sistema è noto anche come Asterisk External Configuration ed è configurato in /etc/asterisk/extconfig.conf. È possibile mappare i file di configurazione su tabelle in un database (configurazione statica) e utilizzare voci in tempo reale per la creazione dinamica di oggetti senza la necessità di ricaricare Asterisk.

## Obiettivi

Al termine di questo capitolo, il lettore dovrebbe essere in grado di:

- Comprendere i vantaggi e i limiti di Asterisk Real Time.
- Utilizzare ODBC per l'uso con ARA
- Compilare e installare ARA utilizzando ODBC
- Testare il sistema in un ambiente di laboratorio

## Come funziona Asterisk Real Time?

Nella nuova architettura Real Time, tutto il codice specifico del database è stato spostato nei driver di canale. Il canale chiama solo una routine generica che interroga il database. Il risultato è un processo molto più semplice e pulito dal punto di vista del codice sorgente. Il database viene acceduto tramite tre funzioni:

- STATIC: Utilizzata per impostare una configurazione statica quando viene caricato un modulo.
- REALTIME: Utilizzata per cercare oggetti durante una chiamata o un altro evento.


- UPDATE: Utilizzata per aggiornare gli oggetti.

Su Asterisk 22, gli endpoint SIP sono gestiti dallo stack **PJSIP** (`res_pjsip`), costruito sul modello a oggetti **Sorcery**. Con il wizard `realtime`, Sorcery carica ogni oggetto PJSIP dal database su richiesta, e tali oggetti esistono quindi come normali oggetti PJSIP configurati — non come peer realtime usa-e-getta che il vecchio driver SIP scartava dopo ogni chiamata. Poiché sono oggetti reali, il NAT traversal, il qualify e il message waiting indication (MWI) funzionano tutti normalmente per gli endpoint realtime. (A Sorcery può essere inoltre indicato di memorizzare gli oggetti nella cache tramite un wizard `memory_cache`, ma questa è un'opzione facoltativa e separata dal caricamento realtime.) Quando modifichi un oggetto nel database, la modifica viene rilevata alla ricerca successiva; non è necessario ricaricare dopo ogni modifica. (Il modello realtime ritirato `chan_sip`, con le sue famiglie `sippeers`/`sipusers`, è trattato solo nel capitolo *Legacy Channels*.)

## Configurazione di Asterisk Real Time

Per questo laboratorio, assumeremo che tu abbia già installato ODBC dal capitolo CDR. ARA è configurato nel file di testo extconfig.conf, dove si possono facilmente vedere due sezioni. La prima è la sezione dei file di configurazione statica, dove è possibile sostituire i file di configurazione di testo con tabelle di database. La seconda sezione è il motore di configurazione realtime, dove si configurano le tabelle del database per gli oggetti dinamici (peer/utenti). Non è insolito utilizzare file di testo per la configurazione statica e il database per le voci dinamiche. In questo caso, la prima sezione rimane invariata.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Architettura di Asterisk Real Time: i file di configurazione e le tabelle statiche del database vengono caricati all'avvio di Asterisk, mentre le tabelle realtime del database forniscono una configurazione dinamica che viene letta su richiesta durante una chiamata.](../images/18-realtime-fig01.png)

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

La sezione di configurazione statica è dove memorizzi l'equivalente dei file di configurazione nel database. Queste configurazioni vengono lette durante il caricamento di Asterisk. Alcuni moduli rileggono il database quando si esegue il reload. Esempi di configurazione statica sono:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

La mappatura dei file statici è più utile per i file di configurazione che non hanno un equivalente realtime per oggetto. Per PJSIP, preferisci le famiglie realtime per oggetto (`ps_endpoints`, `ps_aors` e così via) descritte più avanti in questo capitolo piuttosto che mappare l'intero `pjsip.conf` come file statico.

Tre esempi sono descritti sopra. Nel primo, leghi queues.conf a una tabella queues nel database asteriskdb. Nel secondo esempio, leghi pjsip.conf alla tabella pjsip_conf nel database asteriskdb definito nella configurazione odbc. Nell'ultimo esempio, leghi iax.conf a una directory LDAP. MyBaseDN è il DN di base da cercare. Nell'esempio precedente, l'applicazione app_queue.so viene caricata mentre il driver MySQL interroga il database e ottiene le informazioni richieste.

### Sezione di configurazione Real Time

La configurazione real-time (seconda parte del file extconfig.conf) è dove il pezzo di configurazione da caricare viene configurato, aggiornato e scaricato in tempo reale. Con il real time, non è necessario ricaricare le configurazioni. La sintassi real-time segue:

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

Qui abbiamo cinque righe di configurazione. Nella prima riga, leghi la famiglia PJSIP/Sorcery `ps_endpoints` a una tabella `ps_endpoints` nel database asteriskdb. Nell'ultima, leghi la famiglia voicemail alla tabella test nel database asteriskdb. Ogni tipo di oggetto PJSIP (endpoint, aor, auth, contact) ottiene la propria famiglia e tabella; l'insieme completo è mostrato nella sezione "PJSIP Realtime (Sorcery)" qui sotto. Le famiglie `voicemail`, `extensions`, `queues` e `queue_members` sono ancora valide in Asterisk 22.

## PJSIP Realtime (Sorcery)

Su Asterisk 22, gli endpoint SIP sono gestiti esclusivamente dallo stack **PJSIP** (`res_pjsip`), costruito sul livello di astrazione degli oggetti **Sorcery**. Piuttosto che un singolo "peer" SIP, PJSIP divide un account SIP in diversi tipi di oggetto, ognuno memorizzato nella propria tabella realtime:

| Tipo di oggetto Sorcery | Tabella Realtime | Cosa contiene |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | impostazioni per account (context, codec, DTMF, ecc.) |
| aor (address of record) | ps_aors | limiti di registrazione e impostazioni `qualify` |
| auth | ps_auths | credenziali `username` / `password` |
| contact | ps_contacts | la posizione registrata dinamicamente |
| domain alias | ps_domain_aliases | domini SIP alternativi per un endpoint |
| endpoint identifier by IP | ps_endpoint_id_ips | corrispondenza di un endpoint tramite IP sorgente |

Il realtime per PJSIP è abilitato in due punti. Primo, mappa i tipi di oggetto Sorcery al realtime in `extconfig.conf`:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Secondo, indica a Sorcery di utilizzare il wizard `realtime` per quei tipi di oggetto in `sorcery.conf`. Il nome della mappatura (qui `res_pjsip`) è il modulo i cui oggetti stai ricollocando, e il valore a destra punta alla famiglia che hai definito in `extconfig.conf`:

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

Puoi mescolare oggetti statici e realtime. Se ometti un tipo da `sorcery.conf`, quel tipo di oggetto continua a leggere da `pjsip.conf`. Un pattern comune è mantenere i transport statici e le impostazioni globali in `pjsip.conf` mentre si memorizzano endpoint, aor, auth e contact nel database.

### Creazione dello schema realtime PJSIP con Alembic

Asterisk fornisce migrazioni del database per tutti i suoi schemi realtime sotto `contrib/ast-db-manage`. Questo è il modo supportato per creare (e aggiornare la versione) delle tabelle PJSIP — non scriverai più a mano le definizioni delle tabelle `ps_*`. Il set di migrazione `config` contiene le tabelle PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Questo crea `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` e le altre tabelle PJSIP con le colonne corrette per la versione di Asterisk in esecuzione. (Alembic richiede il pacchetto `alembic` di Python più un driver SQLAlchemy come `pymysql` per MySQL/MariaDB o `psycopg2` per PostgreSQL.)

Un endpoint realtime minimale consiste quindi in una riga in ciascuna delle tre tabelle — ad esempio l'endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Dopo aver inserito le righe non c'è nulla da ricaricare — il successivo REGISTER/INVITE estrae gli oggetti dal database. Puoi confermare cosa ha restituito il realtime con:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Configurazione del database

Ora che abbiamo configurato il file extconfig.conf, creiamo le tabelle. In generale, ogni colonna del database corrisponde a un nome di opzione dal file di configurazione corrispondente. Le tabelle PJSIP `ps_*` seguono questa regola: ogni colonna `ps_endpoints` prende il nome da un'opzione endpoint `pjsip.conf`, ogni colonna `ps_auths` da un'opzione auth, e così via. Ad esempio, l'endpoint `pjsip.conf` qui sotto,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

è memorizzato come una riga su tre tabelle. La riga `ps_endpoints` contiene `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; la riga `ps_auths` contiene `id=4000, auth_type=userpass, username=4000, password=supersecret`; e la riga `ps_aors` contiene `id=4000, max_contacts=1`. Devi popolare solo le colonne che utilizzi effettivamente — qualsiasi colonna lasciata NULL ricade sul valore predefinito dell'opzione. Se vuoi, ad esempio, il parametro `callerid` su un endpoint, compila la colonna `callerid` di `ps_endpoints` (il nome della colonna è lo stesso del nome dell'opzione `pjsip.conf`).

Una tabella voicemail segue la stessa idea. Le sue colonne mappano ai campi `voicemail.conf`:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

Il `uniqueid` dovrebbe essere univoco per ogni utente voicemail e può essere autoincrementale. Non deve avere alcuna relazione con la mailbox o il context.

### Costruire un dial plan utilizzando Asterisk Real Time

Puoi anche utilizzare il sistema real-time per creare il dial plan. ARA utilizza l'istruzione `switch` per includere le estensioni real-time nel dial plan normale contenuto nel file extensions.conf. La tabella delle estensioni dovrebbe apparire come quella qui sotto:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

La famiglia realtime `extensions` rimane invariata in Asterisk 22; assicurati solo che la colonna `appdata` componga i canali PJSIP, ad esempio `PJSIP/4000`. Nel dial plan, devi usare il comando `switch` per utilizzare il real time.

![Costruire un dial plan con Asterisk Real Time: extensions.conf utilizza un'istruzione `switch => realtime` per estrarre le righe delle estensioni (context, exten, priority, app, data) da una tabella del database invece che dal file di testo.](../images/18-realtime-fig02.png)


```
[local]
switch => realtime
```

o

```
[local]
switch => realtime/from-internal@extensions
```

## Laboratorio: Installazione e creazione delle tabelle del database

In questo laboratorio, prepareremo il database per ricevere i parametri di Asterisk. Prepareremo solo le tabelle REALTIME. La configurazione statica sarà lasciata ai file di configurazione di testo (bello, vero?). La creazione della tabella in MySQL segue.

Passaggio 1: Entra nel database MySQL come root.

```
mysql –u root –p
```

Passaggio 2: Accedi al server MySQL creato nei laboratori CDR.

```
mysql –u astdb –p
```

Quando viene richiesta la password, digita supersecret.

Passaggio 3: Crea le tabelle necessarie. I file di schema statici legacy sono ancora forniti sotto `contrib/realtime/` (ad esempio `/usr/src/asterisk-22.x/contrib/realtime/mysql`), ma su Asterisk 22 il modo consigliato e corretto per la versione per costruire le tabelle realtime — specialmente le tabelle PJSIP `ps_*` — sono le migrazioni **Alembic** sotto `contrib/ast-db-manage` (vedi la sezione "Creazione dello schema realtime PJSIP con Alembic" sopra).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Il set di migrazione Alembic `config` costruisce le tabelle PJSIP `ps_*` (insieme a `voicemail`, `extensions` e agli altri schemi realtime) con esattamente le colonne che la versione di Asterisk in esecuzione si aspetta, quindi lo schema corrisponde sempre alla build.

Usa supersecret come password.

Passaggio 4: Verifica la creazione delle tabelle.

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

Dovresti vedere le tabelle PJSIP `ps_*` (create dalla migrazione Alembic `config`), insieme alle tabelle realtime `voicemail`, `extensions` e altre:

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

(Alembic crea più tabelle di queste — l'elenco sopra mostra quelle rilevanti per questo laboratorio.)

Passaggio 5: Il database è già configurato per ODBC (dal laboratorio CDR), quindi non è necessaria alcuna ulteriore configurazione ODBC qui.

Passaggio 6: Ispeziona e popola le tabelle dal client MySQL. Non hai bisogno di uno strumento grafico come phpMyAdmin — ogni passaggio in questo capitolo è SQL semplice, copiabile e incollabile, eseguito dalla riga di comando `mysql`. Connettiti al database `astdb` (usa `supersecret` quando richiesto):

```
mysql -u astdb -p astdb
```

Puoi confermare le colonne di una tabella in qualsiasi momento con `DESCRIBE`, ad esempio:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

Queste tabelle sono state create dalla migrazione Alembic `config`, quindi le loro colonne corrispondono già ai nomi delle opzioni `pjsip.conf` per la versione di Asterisk in esecuzione — devi compilare solo le colonne di cui hai bisogno.

## Laboratorio: Configurazione e test di ARA

In questo laboratorio modificheremo la configurazione di extconfig.conf per riflettere la nostra configurazione del database e le tabelle.

Passaggio 1: Configura extconfig.conf e ricarica Asterisk.

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

Nota le famiglie `ps_endpoints`, `ps_aors`, `ps_auths` e `ps_contacts` sopra; insieme alle mappature `sorcery.conf` corrispondenti (vedi la sezione "PJSIP Realtime (Sorcery)") fanno sì che PJSIP legga i suoi account dal database. Le famiglie `voicemail` e `extensions` completano l'esempio.

Passaggio 2: Test dell'estensione Real Time. Crea un nuovo endpoint `6010` inserendo una riga in ciascuna delle tabelle `ps_auths`, `ps_aors` e `ps_endpoints`, quindi prova a registrare questo endpoint con un softphone. Esegui il seguente SQL nel client `mysql` (`mysql -u astdb -p astdb`):

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

Le tre righe insieme descrivono un account SIP. Le restanti impostazioni dell'account sono distribuite tra gli oggetti PJSIP: context, codec, modalità DTMF e gestione dei media risiedono sull'endpoint (le ultime sei colonne sopra); la registrazione dinamica risiede sull'AOR. Non esiste un flag "dinamico" separato — un AOR accetta REGISTER dinamici finché `max_contacts` è maggiore di zero, e ogni posizione registrata viene scritta su `ps_contacts`.

In PJSIP la modalità DTMF out-of-band RFC 2833 / RFC 4733 è chiamata `rfc4733`, e `dtmf_mode=rfc4733` è il valore predefinito — quindi la colonna `dtmf_mode` sopra è facoltativa e mostrata solo per chiarezza.

Passaggio 3: Prova a registrare il nuovo telefono con un softphone utilizzando username `6010` e password `supersecret`. Conferma la registrazione sulla CLI di Asterisk:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Passaggio 4: Includi le estensioni nel database.

```
mysql -u astdb -p
```

Inserisci la password:

Usa supersecret quando richiesto, quindi inserisci la riga dell'estensione dal client MySQL:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Passaggio 5: Includi Asterisk Real Time nel dial plan. Nel context `default`:

```
switch => realtime/test@extensions
```

Ricarica le estensioni per attivare la modifica.

```
asterisk-server*CLI>extensions reload
```

Passaggio 6: Riconfigura uno dei telefoni con lo username `bria`, se non l'hai già fatto.

Passaggio 7: Componi 6007 da un telefono esistente; il telefono `bria` dovrebbe squillare.

## Riepilogo

In questo capitolo, hai imparato che Asterisk Real Time ti consente di inserire le tue configurazioni in un database. Asterisk fornisce driver realtime nativi per ODBC (che raggiunge qualsiasi database supportato da UnixODBC, inclusi MySQL/MariaDB e SQLite), MySQL e PostgreSQL, oltre a un driver realtime LDAP per backend di directory. La configurazione è divisa in statica e real time. La configurazione statica sostituisce i file di configurazione, mentre la configurazione real-time crea oggetti dinamici che vengono caricati solo quando si verifica una chiamata o un altro evento correlato. Abbiamo concluso con un laboratorio pratico su come installare e configurare ARA.

## Quiz

1. Asterisk Realtime fa parte della distribuzione standard di Asterisk.
   - A. Vero
   - B. Falso
2. I parametri di connessione di un server database sono configurati nel file:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. Il file `extconfig.conf` configura le tabelle utilizzate da Realtime. Ha due sezioni distinte (selezionane due):
   - A. Configurazione statica
   - B. Configurazione Realtime
   - C. Rotte in uscita
   - D. Indirizzi IP e porte del database
4. Nella configurazione statica, una volta che gli oggetti vengono caricati dal database, vengono mantenuti nella memoria di Asterisk e aggiornati solo all'avvio o al ricaricamento.
   - A. Vero
   - B. Falso
5. PJSIP realtime (Sorcery) supporta pienamente `qualify` e MWI per gli endpoint realtime, perché Sorcery li carica come normali oggetti PJSIP configurati invece di scartarli dopo ogni chiamata come facevano i vecchi peer SIP realtime.
   - A. Vero
   - B. Falso
6. Nel realtime PJSIP, quali tabelle contengono gli endpoint e i loro contatti registrati?
   - A. `ps_endpoints` e `ps_contacts`
   - B. `ps_peers` e `ps_registry`
   - C. `ps_config` e `ps_data`
   - D. `extconfig` e `res_odbc`
7. Puoi ancora utilizzare i file di configurazione di testo anche dopo aver abilitato ARA.
   - A. Vero
   - B. Falso
8. phpMyAdmin è obbligatorio quando si utilizza Realtime.
   - A. Vero
   - B. Falso
9. Il database deve essere creato con ogni campo esistente nel file di configurazione.
   - A. Vero
   - B. Falso
10. Su Asterisk 22, qual è il modo consigliato e corretto per la versione per creare le tabelle realtime PJSIP (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`)?
    - A. Scrivere a mano le istruzioni `CREATE TABLE` per ogni tabella `ps_*`
    - B. Importare il legacy `mysql_config.sql` da `contrib/realtime/`
    - C. Eseguire le migrazioni Alembic `config` sotto `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)
    - D. Le tabelle vengono create automaticamente al primo avvio di Asterisk

**Risposte:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
