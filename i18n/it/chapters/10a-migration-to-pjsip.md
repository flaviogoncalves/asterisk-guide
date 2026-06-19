# Migrazione da chan_sip a PJSIP: un ricettario

Se stai leggendo questo testo con un sistema Asterisk 13, 16 o 18 ancora in produzione, hai una scadenza. `chan_sip` — il driver di canale SIP originale configurato tramite `sip.conf` — è stato **deprecato in Asterisk 17, rimosso dalla build predefinita in Asterisk 19 ed eliminato completamente in Asterisk 21**. Non esiste in Asterisk 22 LTS. Non c'è alcun flag per riattivarlo, nessun `noload` per evitarlo, nessun pacchetto da installare. L'unico driver di canale SIP in Asterisk 22 è **PJSIP** (`res_pjsip` più `chan_pjsip`), configurato tramite `pjsip.conf`.

Quindi, un aggiornamento ad Asterisk 22 è, per la maggior parte dei siti, un *progetto di migrazione SIP* tanto quanto un aggiornamento di versione. La buona notizia è che il protocollo sul cavo non cambia — un telefono che si registrava e chiamava ieri si registrerà e chiamerà domani — e Asterisk fornisce uno strumento di conversione per svolgere l'80% del lavoro di traduzione al posto tuo. Questo capitolo è un ricettario pratico: la mappatura dei concetti, lo script di conversione, le traduzioni affiancate `sip.conf` → `pjsip.conf` per i casi che hai realmente, le modifiche al dialplan e alla CLI che accompagnano il passaggio, la migrazione del realtime (database), una checklist e le insidie in cui molti cadono.

Tutto ciò che è qui riportato è verificato rispetto al laboratorio Asterisk 22.10.0 del libro. Il materiale legacy approfondito su `chan_sip` stesso — e una conversione completa end-to-end di un `sip.conf` multi-dispositivo — si trova nel capitolo *Legacy channels*; questo capitolo ne è il compagno focalizzato, in stile ricettario.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Spiegare perché `chan_sip` non c'è più in Asterisk 22 e cosa lo sostituisce
- Mappare il modello peer/user/friend di `sip.conf` sul modello a oggetti PJSIP (endpoint + aor + auth + identify + transport + registration)
- Eseguire lo script di conversione `sip_to_pjsip.py` e rivederne criticamente l'output
- Tradurre manualmente i tipi di dispositivo comuni (telefono che si registra, trunk in entrata, registrazione in uscita) da `sip.conf` a `pjsip.conf`
- Migrare le impostazioni di NAT, media, DTMF, codec e autenticazione opzione per opzione
- Aggiornare il dialplan (`SIP/` → `PJSIP/`) e la CLI (`sip show` → `pjsip show`)
- Migrare una distribuzione realtime/ARA da `sippeers`/`sipregs` alle tabelle Sorcery `ps_*`
- Seguire una checklist di migrazione ed evitare le insidie classiche

## Perché migrare

`chan_sip` ha servito Asterisk per quasi due decenni, ma portava con sé un debito architettonico: un modulo monolitico, un singolo blocco di configurazione per dispositivo, un supporto multi-trasporto debole e uno stack SIP rimasto indietro rispetto alle RFC. **PJSIP** — costruito sullo stack maturo pjproject di Teluu e introdotto in Asterisk 12 — è stato il sostituto creato da zero. Con Asterisk 21, il progetto Asterisk ha completato il lavoro e rimosso `chan_sip` dall'albero.

Puoi confermare la situazione su qualsiasi sistema Asterisk 22:

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` restituisce *0 modules loaded* — semplicemente non è presente. Non c'è nulla *verso cui* migrare se non PJSIP, quindi l'unica vera domanda è *come*, non *se*.

## La mappatura concettuale: non esiste un unico "peer"

Il cambiamento mentale che mette in difficoltà chiunque provenga da `sip.conf` è questo: **PJSIP non ha un `[peer]`.** In `sip.conf` un blocco tra parentesi — un `peer`, un `user` o un `friend` — descriveva *tutto* di un dispositivo: le sue credenziali, dove raggiungerlo, i suoi codec, il suo comportamento NAT, il suo contesto nel dialplan. PJSIP divide deliberatamente quel singolo blocco in diversi oggetti più piccoli e a scopo singolo, ognuno etichettato con un `type=`, che *si riferiscono l'un l'altro per nome*:

| Oggetto PJSIP (`type=`) | Responsabilità |
| --- | --- |
| `endpoint` | L'identità di gestione delle chiamate del dispositivo: codec, contesto, DTMF, media, NAT e riferimenti ai suoi `auth`/`aors`/`transport` |
| `aor` (Address of Record) | *Dove* raggiungere il dispositivo — contatti registrati o statici, `max_contacts`, qualify |
| `auth` | Credenziali (nome utente/password) per l'autenticazione in entrata e/o in uscita |
| `identify` | Corrispondenza di una richiesta in entrata a un endpoint tramite **IP sorgente** invece che tramite l'utente `From` |
| `transport` | Socket in ascolto: protocollo, indirizzo/porta di bind, indirizzi NAT/esterni |
| `registration` | Una REGISTER **in uscita** da Asterisk verso un provider |

La distinzione `friend`/`peer`/`user` scompare del tutto — in PJSIP tutto è un `endpoint`. Un singolo friend `sip.conf` diventa quindi, tipicamente, tre oggetti (`endpoint` + `auth` + `aor`) che condividono un nome e puntano l'uno all'altro:

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

L'endpoint è il collante. Esso nomina un `transport` (o eredita quello predefinito), un oggetto `auth` e uno o più `aors`. Il modello a oggetti è trattato in profondità in *SIP & PJSIP in depth*; qui ci serve solo come destinazione di ogni traduzione.

## Lo strumento di conversione `sip_to_pjsip.py`

Asterisk fornisce uno script Python che legge un `sip.conf` esistente e scrive un `pjsip.conf`. Non viene eseguito come comando CLI — risiede nell'**albero dei sorgenti di Asterisk**, non nei binari installati:

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

Sull'Asterisk 22.10.0 del laboratorio, il percorso completo è, ad esempio, `/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py`. La stessa directory contiene `sip_to_pjsql.py` (la variante realtime/SQL, trattata più avanti) e i moduli helper `astconfigparser.py`, `astdicts.py` e `sqlconfigparser.py`.

### Esecuzione

Lo script accetta argomenti posizionali opzionali — `[input-file [output-file]]` — che hanno come valore predefinito `sip.conf` e `pjsip.conf` nella directory corrente:

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Le sue uniche vere opzioni sono:

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

Legge l'input, stampa `Converting to PJSIP...` e scrive il file di output. Internamente attraversa ogni sezione `sip.conf` e, per ogni dispositivo, emette gli oggetti corrispondenti `endpoint`, `auth`, `aor`, `registration` e (dove può dedurli) `transport`, applicando automaticamente le mappature delle opzioni descritte nella sezione successiva.

### Cosa fa — e i suoi limiti

Tratta l'output come una **prima bozza, non come un file finito.** Lo script è onesto riguardo alle proprie lacune: tutto ciò che non riesce a mappare chiaramente viene scritto in un blocco chiaramente delimitato all'inizio del file di output:

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[softphone]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

Nota in quel frammento reale che `qualify = yes` da un peer `sip.conf` è finito nel blocco *non-mapped* — poiché PJSIP esegue il qualify sull'**aor** con `qualify_frequency` (secondi), non come booleano sul dispositivo, lo script lo lascia a te affinché tu possa impostarlo deliberatamente. Le limitazioni pratiche da pianificare sono:

- **I trasporti sono ipotizzati, non progettati.** Lo script emette un `transport-udp` di base da `bindport`/`bindaddr`, ma non può conoscere i tuoi certificati TLS, le tue esigenze TCP o il tuo layout multi-bind. Rivedi e riscrivi il trasporto.
- **NAT e indirizzi esterni richiedono un intervento umano.** `externaddr`/`localnet` potrebbero non essere convertiti correttamente; conferma manualmente `external_media_address`, `external_signaling_address` e `local_net` sul trasporto.
- **`qualify`, timer personalizzati e una manciata di opzioni finiscono in "non-mapped".** Leggi quel blocco dall'inizio alla fine e decidi per ognuna.
- **Elenchi di codec, contesti e sicurezza necessitano di revisione.** Verifica `disallow`/`allow`, il dialplan `context` e che nessun dispositivo sia lasciato involontariamente aperto.

Il flusso di lavoro è quindi: esegui lo script in un file *di prova*, confrontalo e rivedilo, integra le parti corrette nel tuo `pjsip.conf` reale, quindi testa esaustivamente prima della messa in produzione.

## Traduzioni affiancate

Queste sono le ricette. `sip.conf` a sinistra, l'equivalente verificato `pjsip.conf` a destra (impilato qui per larghezza di pagina). Ogni nome di opzione e valore a destra è stato verificato rispetto al laboratorio Asterisk 22 con `config show help res_pjsip ...`.

### Un telefono che si registra (`host=dynamic`)

Il dispositivo più comune: un telefono da scrivania o un softphone che effettua il login con una password e registra la propria posizione.

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

Passaggi chiave: `host=dynamic` diventa un `aor` con `max_contacts` (il dispositivo invia una REGISTER per riempire il suo contatto); `secret=` diventa `password=` all'interno di un `type=auth`; `qualify=yes` diventa `qualify_frequency=60` (secondi) sull'**aor**, non sull'endpoint. Imposta `max_contacts` sopra 1 solo se desideri genuinamente lo stesso account su più dispositivi contemporaneamente.

### Un trunk in entrata (`host=<ip>` / `type=peer`)

Un provider che ti invia chiamate da un indirizzo IP noto. Qui non c'è registrazione — autentichi il *traffico del carrier tramite il suo IP sorgente* usando `identify`.

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

La traduzione cruciale è **`insecure=invite` → `identify`**. In `chan_sip`, `insecure=invite` diceva ad Asterisk "non sfidare le INVITE in entrata da questo peer per l'autenticazione". PJSIP ottiene lo stesso effetto facendo corrispondere l'IP sorgente all'endpoint con `type=identify`/`match=`, che è sia più esplicito che più sicuro. Il `host=` statico diventa un `contact=` permanente sull'endpoint `aor` in modo da poter anche chiamare *in uscita* verso il carrier. `match=` accetta un IP, un intervallo CIDR o un hostname (risolto al momento del caricamento della configurazione — ricarica se l'IP del provider cambia).

### Una registrazione in uscita (`register =>`)

Quando il provider vuole che *tu* effettui il login verso *loro*, `chan_sip` usava una singola riga `register =>` in `[general]`. PJSIP la sostituisce con un oggetto dedicato `type=registration` più un `outbound_auth`.

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

Mappa i campi `register =>` uno a uno: le credenziali `1020:supersecret` diventano l'oggetto `auth` (riferito come `outbound_auth`); `@sip.example.com:5600` diventa il `server_uri`; il suffisso `/9999` — la parte utente a cui il provider invia le chiamate in entrata — diventa `contact_user=9999`. `defaultuser`/`fromuser` e `fromdomain` diventano `from_user` e `from_domain` sull'endpoint. Nota che `outbound_auth` appare *due volte*: la registrazione lo usa per la REGISTER, l'endpoint lo usa per rispondere alla sfida `407` sulle INVITE in uscita.

## Riferimento alla migrazione opzione per opzione

Quando traduci manualmente (o controlli l'output dello script), questa tabella è il riferimento. Ogni nome di opzione PJSIP e la sua posizione (endpoint / aor / auth / transport) è verificata rispetto al laboratorio Asterisk 22.

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | Dove |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (il dispositivo invia REGISTER) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (metodo auth) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (stessa sintassi) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | ometti auth; usa `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### Una nota su `secret` → `auth` e `auth_type`

Il `secret=` di `chan_sip` diventa il campo `password=` di un oggetto `type=auth`. Il **metodo di autenticazione** si imposta con `auth_type`. Usa `auth_type=digest`. I valori più vecchi `userpass` e `md5` funzionano ancora ma sono **deprecati e convertiti silenziosamente in `digest`** — verificato direttamente dal laboratorio:

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

Vedrai `auth_type=userpass` nelle configurazioni più vecchie e nell'output dello script di conversione (e nei capitoli precedenti di questo libro). È innocuo, ma scrivi `digest` in qualsiasi cosa nuova.

### NAT, media e DTMF in dettaglio

Questi tre sono l'origine della maggior parte dei ticket post-migrazione del tipo "si registra ma non ha audio". La scorciatoia `chan_sip` `nat=force_rport,comedia` racchiudeva tre comportamenti in un'unica opzione; PJSIP li divide in modo che tu possa ragionare su ciascuno:

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

Per i **media**, `directmedia` diventa `direct_media` (il trattino basso è l'unico cambiamento); mantieni `direct_media=no` ogni volta che la chiamata deve essere ancorata su Asterisk — attraverso NAT, o per registrare/transcodificare/trasferire. Per il **DTMF**, la RFC è stata rinumerata: il `dtmfmode=rfc2833` di `chan_sip` è il `dtmf_mode=rfc4733` di PJSIP (stesso meccanismo out-of-band telephone-event, numero RFC corrente). Il laboratorio conferma che i valori validi per `dtmf_mode` sono `rfc4733`, `inband`, `info`, `auto` e `auto_info`, con valore predefinito `rfc4733`.

Per i **codec**, non cambia nulla: `disallow=all` seguito da `allow=ulaw` (ecc.) usa la sintassi identica sull'endpoint PJSIP.

## Modifiche al dialplan e alla CLI

La migrazione non si ferma a `pjsip.conf`. Due cose di uso quotidiano cambiano.

### Stringhe di canale: `SIP/` → `PJSIP/`

Ogni `Dial()` e riferimento al canale nel `extensions.conf` che nominava la vecchia tecnologia deve essere aggiornato:

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Le stringhe di dial dei trunk seguono lo stesso schema — `Dial(SIP/${EXTEN}@itsp)` diventa `Dial(PJSIP/${EXTEN}@itsp)`. PJSIP aggiunge anche la funzione `PJSIP_DIAL_CONTACTS()` per far squillare contemporaneamente ogni contatto legato a un AOR, e le funzioni di dialplan `PJSIP_HEADER()` / `PJSIP_MEDIA_OFFER()`; grep il tuo dialplan per i riferimenti SIP `SIP/`, `SIPPEER`, `SIPCHANINFO` e `CHANNEL(...)` e traduci ognuno.

### CLI: `sip show ...` → `pjsip show ...`

L'intero albero di comandi `sip ...` scompare con il driver. Le sostituzioni:

| Comando `chan_sip` | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (o `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (o `core reload`) |

I vecchi comandi non si comportano solo in modo diverso — non esistono più. Nel laboratorio, `sip show peers` restituisce *No such command*, mentre `pjsip show endpoints`, `pjsip show aors`, `pjsip show auths`, `pjsip show contacts`, `pjsip show registrations` e `pjsip show identifies` sono tutti presenti. Il comando di risoluzione dei problemi più utile — il logger dei pacchetti SIP che stampava ogni messaggio con `sip set debug` — è ora **`pjsip set logger on`** (con `pjsip set logger host <ip>` per concentrarsi su un singolo peer).

## Migrazione Realtime (ARA)

Se eseguivi `chan_sip` da un database (Asterisk Realtime Architecture), i tuoi dispositivi risiedevano nella tabella `sippeers` e le registrazioni in `sipregs`. PJSIP usa uno strato di archiviazione completamente diverso — **Sorcery** — con una tabella *per tipo di oggetto*. La mappatura:

| Tabella realtime `chan_sip` | Tabella/e PJSIP / Sorcery |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (una riga ciascuna, suddivise) |
| `sipregs` | `ps_contacts` (registrazioni dinamiche) |
| — (`register=>` in uscita) | `ps_registrations` |
| — (corrispondenza IP) | `ps_endpoint_id_ips` (gli oggetti `identify`) |
| — (alias di dominio) | `ps_domain_aliases` |

La suddivisione concettuale è la stessa del caso dei file flat: una riga `sippeers` diventa *tre* righe in tre tabelle (`ps_endpoints` + `ps_aors` + `ps_auths`) che si riferiscono l'un l'altra tramite il nome dell'endpoint.

Due cose rendono questo processo gestibile:

- **Lo schema viene generato per te.** Asterisk fornisce migrazioni Alembic sotto `contrib/ast-db-manage/` che creano ogni tabella `ps_*`. Esegui `alembic upgrade head` contro il database `config` per costruire lo schema PJSIP corrente invece di scrivere DDL a mano.
- **Esiste uno script di conversione SQL.** Accanto a `sip_to_pjsip.py` si trova **`sip_to_pjsql.py`** nella stessa directory `contrib/scripts/sip_to_pjsip/`; riutilizza la stessa logica di `convert()` ma emette un file `pjsip.sql` di istruzioni `INSERT` per le tabelle `ps_*` invece di un file di configurazione flat. Come con lo strumento per file flat, rivedi l'output prima di caricarlo.

Infine, punta `sorcery.conf` al tuo database in modo che PJSIP legga endpoint, aor, auth e contatti dalle tabelle `ps_*` (tramite `res_config_odbc` / `res_pjsip_realtime`), esattamente come `extconfig.conf` puntava un tempo `sippeers` al database per `chan_sip`. Le meccaniche realtime sono trattate nel capitolo *Realtime*; il punto specifico della migrazione è semplicemente *quali tabelle mappano a quali*.

## Checklist di migrazione

Un ordine operativo pragmatico per un passaggio in produzione:

1. **Inventario.** Elenca ogni dispositivo, trunk e `register =>` in `sip.conf` (o ogni riga `sippeers`/`sipregs`). Prendi nota delle impostazioni personalizzate di NAT, codec e DTMF.
2. **Esegui il convertitore in un file di prova.** `sip_to_pjsip.py sip.conf pjsip_generated.conf`. **Non** puntarlo al tuo `pjsip.conf` attivo.
3. **Leggi il blocco "Non mapped elements"** all'inizio dell'output e risolvi ogni riga — specialmente `qualify`, timer e qualsiasi cosa relativa al NAT.
4. **Progetta il/i trasporto/i a mano.** Un trasporto per IP/porta; aggiungi TLS/TCP se necessario; imposta `external_*_address` e `local_net` per box cloud/NAT.
5. **Verifica l'autenticazione.** Conferma `auth_type=digest`, nomi utente e password su ogni oggetto `auth`.
6. **Verifica NAT/media/DTMF.** `force_rport`/`rewrite_contact`/`rtp_symmetric`, `direct_media`, `dtmf_mode=rfc4733` per endpoint come richiesto.
7. **Aggiorna il dialplan.** `SIP/` → `PJSIP/` ovunque; controlla le funzioni `SIP*` e le variabili di canale.
8. **Aggiorna script e monitoraggio.** Qualsiasi strumento o consumer AMI che analizzava l'output di `sip show ...` deve passare a `pjsip show ...` / azioni AMI PJSIP.
9. **Ricarica e verifica.** `module reload res_pjsip.so`, quindi `pjsip show endpoints`, `pjsip show registrations`, `pjsip show identifies`.
10. **Testa con il packet logger.** `pjsip set logger on`; effettua una registrazione, una chiamata in entrata e una in uscita e leggi lo scambio SIP dall'inizio alla fine.

## Insidie comuni

- **`alwaysauthreject` è integrato ora — non cercarlo.** `chan_sip` necessitava di `alwaysauthreject=yes` in modo da non rivelare quali estensioni esistessero rispondendo diversamente a nomi utente errati. PJSIP fa la cosa sicura per progettazione: non rivela mai se un endpoint esiste. Non c'è alcuna opzione `alwaysauthreject` da impostare. La protezione correlata — limitare i mittenti non identificati — è il parametro globale `unidentified_request_count` / `unidentified_request_period`, attivo per impostazione predefinita.

- **`insecure=invite` non è un'opzione PJSIP — usa `identify`.** Non esiste `insecure=` in `pjsip.conf`. Il modo per accettare INVITE non autenticate da un carrier noto è *identificare l'endpoint tramite IP sorgente* con `type=identify` / `match=`. Abbina il più strettamente possibile (IP host specifici, non ampi CIDR) e proteggilo con un `type=acl` — un trunk con corrispondenza IP senza autenticazione è un bersaglio per frodi telefoniche.

- **Un trasporto per IP/porta.** Non puoi associare due trasporti allo stesso IP:porta, e non puoi associare più trasporti TCP o TLS della stessa versione IP. Lo script di conversione potrebbe emettere un trasporto che collide con uno che hai già — consolida in un unico strato di trasporto progettato deliberatamente.

- **`qualify=yes` non si traduce in un booleano.** Appartiene all'**aor** come `qualify_frequency=<seconds>`. Il convertitore rilascia `qualify=yes` nel blocco non-mapped proprio perché non esiste un booleano equivalente sull'endpoint.

- **`secret=` non è un'opzione dell'endpoint.** Le credenziali risiedono solo in un oggetto `type=auth` che l'endpoint *referenzia* (`auth=` per l'entrata, `outbound_auth=` per l'uscita). Mettere una password sull'endpoint non fa nulla.

- **La CLI e qualsiasi script di scraping si rompono silenziosamente.** `sip show ...` restituisce "No such command", non un errore che il tuo monitoraggio necessariamente rileverà. Controlla ogni cron job, controllo Nagios e client AMI per i comandi `sip ` prima del passaggio.

## Sommario

Migrare ad Asterisk 22 significa abbandonare `chan_sip`, perché il driver è stato rimosso in Asterisk 21 e PJSIP è l'unico canale SIP che rimane. Il fulcro del lavoro è riesprimere ogni `sip.conf` `peer`/`user`/`friend` — che racchiudeva tutto in un unico blocco — come un insieme di oggetti PJSIP cooperanti: un `endpoint` più un `auth`, un `aor` e, a seconda del dispositivo, un `identify` (trunk in entrata), un `registration` (login in uscita) e un `transport` condiviso. Lo script `sip_to_pjsip.py` in `contrib/scripts/sip_to_pjsip/` esegue la traduzione di massa e segnala onestamente ciò che non può mappare in un blocco "Non mapped elements", ma il suo output è una prima bozza: progetta il trasporto, il NAT e la sicurezza a mano e testa prima della produzione. Attorno alla configurazione, aggiorna il dialplan (`SIP/` → `PJSIP/`) e i tuoi script (`sip show` → `pjsip show`, `sip set debug` → `pjsip set logger`). Le distribuzioni realtime passano da `sippeers`/`sipregs` alle tabelle Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/`ps_contacts`, con `sip_to_pjsql.py` e lo schema `contrib/ast-db-manage` come aiuto. Osserva le insidie — `alwaysauthreject` è integrato, `insecure=invite` diventa `identify`, `qualify=yes` diventa `qualify_frequency` e un trasporto per IP/porta — e il passaggio sarà meccanico piuttosto che misterioso.

## Quiz

1. Perché una distribuzione Asterisk 22 deve usare PJSIP per SIP?
   - A. `chan_sip` è più lento ma ancora disponibile
   - B. `chan_sip` è stato rimosso in Asterisk 21 e non esiste in Asterisk 22
   - C. PJSIP è il predefinito ma `chan_sip` può essere caricato con `modules.conf`
   - D. `chan_sip` funziona solo con TLS in Asterisk 22

2. Un singolo blocco `sip.conf` `type=friend` diventa più comunemente quale set di oggetti PJSIP?
   - A. Un singolo `type=peer`
   - B. Solo `type=endpoint`
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. In `sip.conf`, `host=dynamic` (il dispositivo registra la propria posizione) mappa a:
   - A. `type=identify` con `match=dynamic`
   - B. un `type=aor` con `max_contacts` (il dispositivo invia REGISTER)
   - C. `direct_media=yes` sull'endpoint
   - D. `type=registration`

4. Lo script di conversione `sip_to_pjsip.py` è:
   - A. Un comando CLI: `asterisk -rx 'sip_to_pjsip'`
   - B. Uno script Python nell'albero dei sorgenti di Asterisk sotto `contrib/scripts/sip_to_pjsip/`
   - C. Un modulo compilato caricato all'avvio
   - D. Parte di `res_pjsip.so`

5. Vero o Falso: L'output di `sip_to_pjsip.py` è pronto per la produzione e dovrebbe essere caricato senza revisione.

6. La scorciatoia `chan_sip` `nat=force_rport,comedia` si traduce su un endpoint PJSIP in quali tre opzioni?
   - A. `nat=yes`, `qualify=yes`, `directmedia=no`
   - B. `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes`
   - C. `external_media_address`, `external_signaling_address`, `local_net`
   - D. `insecure=invite`, `identify`, `match`

7. Il `dtmfmode=rfc2833` di `sip.conf` diventa quale impostazione PJSIP?
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. Su Asterisk 22, un oggetto `auth` dovrebbe usare quale `auth_type`, e qual è lo stato di `userpass`?
   - A. `auth_type=userpass`; è l'unico valore valido
   - B. `auth_type=digest`; `userpass` è deprecato e convertito in `digest`
   - C. `auth_type=md5`; `digest` è deprecato
   - D. `auth_type=plaintext`; `digest` è stato rimosso

9. Un peer provider `chan_sip` con `insecure=invite` (accetta INVITE non autenticate da un IP noto) viene migrato a PJSIP usando:
   - A. `insecure=invite` sull'endpoint
   - B. `allowguest=yes` in `[global]`
   - C. un oggetto `type=identify` con `match=<provider IP>`
   - D. `auth_type=anonymous`

10. In una migrazione realtime, la tabella `chan_sip` `sippeers` è sostituita da quali tabelle PJSIP/Sorcery?
    - A. Una singola tabella `pjsip_peers`
    - B. `ps_endpoints`, `ps_aors` e `ps_auths`
    - C. `sipregs` e `voicemail`
    - D. Solo `ps_contacts`

**Risposte:** 1 — B · 2 — C · 3 — B · 4 — B · 5 — Falso · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
