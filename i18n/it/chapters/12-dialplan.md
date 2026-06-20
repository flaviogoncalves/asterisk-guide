# Funzionalità avanzate del Dial Plan

Il Capitolo 3 ha trattato le basi di un dial plan. Per ragioni didattiche, non abbiamo spiegato tutte le funzionalità, ma solo alcune delle più importanti. Questo capitolo approfondirà il dial plan, descrivendo tecniche avanzate, nuove applicazioni e concetti.

## Objectives

Al termine di questo capitolo, dovresti essere in grado di:

- Semplificare le voci delle tue estensioni
- Affrontare la sicurezza del dialplan e filtrare le estensioni
- Ricevere chiamate utilizzando un menu IVR
- Usare le subroutine per evitare riscritture non necessarie
- Implementare alcune misure di sicurezza del dialplan usando “Include”
- Implementare il follow-me con AsteriskDB
- Implementare il comportamento fuori orario nel tuo PBX
- Usare il comando switch per trasferire a un altro PBX
- Implementare il privacy manager
- Implementare la segreteria telefonica
- Implementare una rubrica aziendale

## Semplificare il tuo Dial Plan

Puoi semplificare il tuo dial plan usando la parola chiave “same” per definire un'estensione. Dovrebbe ridurre il numero di errori di battitura nel dial plan. Guarda l'esempio sotto:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan Security

È stata scoperta una vulnerabilità nel dial plan di Asterisk che consente a un utente di iniettare un nuovo canale e un numero da comporre nel tuo dial plan. Supponiamo che tu abbia la seguente riga nel tuo server `exten=>_X.,1,Dial(PJSIP/${EXTEN})` e che un utente malintenzionato abbia composto il numero `3000&DAHDI/1/011551123456789` nel softphone. Il protocollo SIP, per impostazione predefinita, accetta qualsiasi carattere alfanumerico, quindi l’estensione composta attiverà in realtà due chiamate: una per il canale PJSIP/3000 e l’altra per il canale DAHDI/011551123456789, che è un numero internazionale. In questo modo, qualsiasi utente con accesso a un’estensione può effettivamente chiamare ovunque nel mondo. Il modo più semplice per evitare questo comportamento è filtrare i numeri prima di chiamare l’applicazione dial. La funzione FILTER() è molto utile a questo scopo. Esempio:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

L’applicazione filter ti consentirà di filtrare tutti i caratteri dal numero composto eccetto i numeri da 0 a 9. Ulteriori informazioni sono disponibili nel file README‑SERIOUSLY.bestpractices.txt fornito da Asterisk.

## Ricevere chiamate usando un menu IVR.

In the last section, you received all calls using DID or forwarding to the operator. Now you will learn how to implement an IVR menu as well as create an auto‑attendant service. Before getting into the specifics, let’s examine some new applications. We put the output of the command `core show application` below simply to make it easier for readers. You can obtain these descriptions yourself using `core show application <application_name>`.

### L'applicazione Background()

Questa applicazione riprodurrà l'elenco di file fornito attendendo che un'estensione venga composta dal canale chiamante. Per continuare ad attendere cifre dopo che questa applicazione ha terminato la riproduzione dei file, deve essere utilizzata l'applicazione WaitExten. L'opzione **langoverride** specifica esplicitamente quale lingua tentare di usare per i file audio richiesti. Qualsiasi contesto specificato sarà il contesto del dialplan che questa applicazione utilizza uscendo verso un'estensione composta. Se uno dei file audio richiesti non esiste, l'elaborazione della chiamata verrà terminata. Opzioni:

- s - Fa sì che la riproduzione del messaggio venga saltata se il canale non è nello stato 'up' (cioè non è ancora stato risposto). Se ciò accade, l'applicazione ritornerà immediatamente.  
- n - Non rispondere al canale prima di riprodurre i file.  
- m - Interrompe solo se un tasto premuto corrisponde a un'estensione a una cifra nel contesto di destinazione.

### L'applicazione Record()

Questa applicazione registra dal canale in un nome file specificato. Se il file esiste, verrà sovrascritto.

![10-dialplan-advanced-features figura 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' è il formato del tipo di file da registrare (wav, gsm, ecc).
- 'silence' è il numero di secondi di silenzio consentiti prima di restituire.
- 'maxduration' è la durata massima della registrazione in secondi; se è mancante o zero, non c’è limite massimo.
- 'options' può contenere una delle seguenti lettere:
    - `a` — aggiunge a una registrazione esistente invece di sostituirla
    - `n` — non rispondere, ma registra comunque se la linea non è ancora stata risposta
    - `q` — silenzioso (non riprodurre un tono di beep)
    - `s` — salta la registrazione se la linea non è ancora stata risposta
    - `t` — usa il tasto terminatore alternativo `*` (DTMF) invece del predefinito `#`
    - `x` — ignora tutti i tasti terminatori (DTMF) e continua a registrare fino all'hang-up

Se il nome file contiene %d, questi caratteri saranno sostituiti con un numero incrementato di uno ogni volta che il file viene registrato. Usa core show file formats per vedere i formati disponibili sul tuo sistema. L'utente può premere # per terminare la registrazione e continuare alla priorità successiva. Se l'utente riaggancia durante una registrazione, tutti i dati verranno persi e l'applicazione terminerà.

### L'applicazione Playback()

Questa applicazione riproduce i nomi file forniti (non includere l'estensione). È possibile includere anche opzioni dopo un simbolo pipe. L'opzione 'skip' fa sì che la riproduzione del messaggio venga saltata se il canale non è nello stato 'up' (cioè non è ancora stato risposto).

![10-dialplan-advanced-features figura 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figura 3](../images/10-dialplan-advanced-features-img03.png)

Se è specificato 'skip', l'applicazione ritornerà immediatamente se il canale non è off the hook. Altrimenti, a meno che non sia specificato 'noanswer', il canale verrà risposto prima che il suono sia riprodotto. Non tutti i canali supportano la riproduzione di messaggi mentre sono ancora on the hook. Se è specificato 'j', l'applicazione passerà alla priorità n+101 quando il file non esiste, se presente. Questa applicazione imposta la seguente variabile di canale al completamento:

- PLAYBACKSTATUS — lo stato del tentativo di riproduzione come stringa di testo, uno dei:
    - `SUCCESS`
    - `FAILED`

### L'applicazione Read()

Questa applicazione legge un numero predeterminato di cifre di stringa, un certo numero di volte, dall'utente nella variabile data.

- filename -- file da riprodurre prima di leggere le cifre o il tono con l'opzione i
- maxdigits -- numero massimo accettabile di cifre. Interrompe la lettura dopo che sono state inserite maxdigits cifre (senza richiedere all'utente di premere il tasto #). Il valore predefinito è 0 - nessun limite - per attendere che l'utente prema il tasto #. Qualsiasi valore inferiore a 0 ha lo stesso effetto. Il valore massimo accettato è 255.

![10-dialplan-advanced-features figura 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figura 5](../images/10-dialplan-advanced-features-img05.png)

- option -- le opzioni sono `s`, `i`, `n`:
    - `s` — ritorna immediatamente se la linea non è attiva
    - `i` — riproduci il nome file come tono di indicazione dal tuo `indications.conf`
    - `n` — leggi le cifre anche se la linea non è attiva
- attempts -- se maggiore di 1, il numero di tentativi che verranno effettuati nel caso in cui non vengano inseriti dati
- timeout -- Un numero intero di secondi da attendere per una risposta di cifra. Se maggiore di 0, quel valore sovrascriverà il timeout predefinito.

L'applicazione read() dovrebbe disconnettersi se la funzione fallisce o genera un errore.

### L'applicazione Gotoif()

Questa applicazione farà sì che il canale chiamante salti alla posizione specificata nel dial plan in base alla valutazione della condizione fornita. Il canale continuerà su labeliftrue se la condizione è vera, o su 'labeliffalse' se la condizione è falsa. Le etichette sono specificate con la stessa sintassi usata nell'applicazione Goto. Se l'etichetta scelta dalla condizione è omessa, non viene eseguito alcun salto; invece, l'esecuzione continua con la priorità successiva nel dial plan.

### Lab: Creazione di un menu IVR passo‑passo

Creiamo un menu IVR con la seguente funzionalità. Quando viene chiamato, l'IVR riproduce un file audio con il messaggio “Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.” I numeri instradano il chiamante come segue:

- `1` — trasferimento alle vendite (PJSIP/4001)
- `2` — trasferimento al supporto tecnico (PJSIP/4002)
- `3` — trasferimento alla formazione (PJSIP/4003)
- Nessun tasto premuto — trasferimento all'operatore (PJSIP/4000)

**Passo 1 – Registra i prompt**

Creiamo un’estensione per registrare i prompt. Per registrare un prompt, componi da un soft phone a `9003<filename>` (ad esempio, `9003welcome`). Quando senti il segnale acustico, inizia la registrazione; premi `#` per fermare. Sentirai un segnale acustico e il sistema riprodurrà il prompt registrato.

**Passo 2 – Crea la logica del menu**

When dialing the 9004 extension, processing jumps to the menu in the `s` extension, priority 1.

### Corrispondenza mentre componi

Questo è un menu di configurazione aziendale per ricevere chiamate. L'applicazione `Background()` riproduce il messaggio di benvenuto e poi attende i tasti, confrontando ciò che chiama l'utente con le estensioni definite nel contesto corrente.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

Quando componi questa azienda, il messaggio di benvenuto viene riprodotto per primo. Dopo di ciò, Asterisk attende che venga digitata una cifra:

| Dialed number | Asterisk action |
|---------------|-----------------|
| 1 | Chiama immediatamente `Dial(DAHDI/1)` |
| 2 | Attende il timeout, poi chiama `Dial(DAHDI/2)` |
| 21 | Chiama immediatamente `Dial(DAHDI/3)` |
| 22 | Chiama immediatamente `Dial(DAHDI/4)` |
| 3 | Attende il timeout, poi disconnette |
| 31 | Chiama immediatamente `Dial(DAHDI/5)` |
| 32 | Chiama immediatamente `Dial(DAHDI/6)` |

È importante evitare ambiguità nei menu. Tutti vogliono ricevere risposta rapidamente. Per questo motivo, non dovresti usare i numeri 2, 21 o 22.

### Laboratorio: Uso dell'applicazione Read()

Prova il laboratorio con l'applicazione read(). Read accetta cifre dall'utente e le inserisce nella variabile specificata; puoi quindi usare l'applicazione gotoif per reindirizzare la chiamata.

## Inclusione del contesto

Un contesto può includere il contenuto di un altro contesto. Nell'esempio sopra, qualsiasi canale può chiamare qualsiasi interno nel contesto interno, ma solo il canale 4003 può chiamare interni internazionali. È possibile utilizzare l'inclusione del contesto per semplificare la creazione del dialplan. Con l'inclusione del contesto, è possibile controllare chi ha accesso a quali interni.

### Risoluzione del messaggio “number not found”

È molto comune ricevere il messaggio “number not found”. La maggior parte delle persone confonde il concetto di contesti inclusi perché non è davvero intuitivo. Come regola generale, prima andare al file di configurazione del canale in ingresso, come `pjsip.conf`, `chan_dahdi.conf` e `iax.conf`, e determinare il contesto corrente. Poi, andare al dialplan nel file extensions.conf e verificare se il numero chiamato è presente in quel contesto. In caso contrario, qualcosa non va nel dialplan. Le regole d'oro dei contesti sono: 1. Un canale può chiamare solo numeri all'interno dello stesso contesto del canale. 2. Il contesto in cui la chiamata viene elaborata è definito nel file di configurazione del canale in ingresso (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Utilizzo dell'istruzione switch

Puoi inviare l'elaborazione del dialplan a un altro server usando il comando switch. Avrai bisogno del nome e della chiave dell'altro server. Il contesto è il contesto di destinazione.

![10-dialplan-advanced-features figura 6](../images/10-dialplan-advanced-features-img06.png)

## Ordine di elaborazione del dialplan

Quando Asterisk riceve una chiamata in ingresso, controlla il contesto definito dal canale. In alcuni casi, se più di un modello corrisponde al numero composto, Asterisk non può elaborare la chiamata esattamente come ti aspetti. Puoi vedere l'ordine di corrispondenza usando il comando CLI `dialplan show`. Esempio: supponiamo che tu voglia comporre 912 per instradarlo verso un trunk analogico (DAHDI/1) e tutti gli altri numeri che iniziano con 9 verso un altro trunk analogico (DAHDI/2). Scriveresti qualcosa del genere:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Se due modelli corrispondono a un'estensione, puoi controllare quale estensione viene elaborata per prima usando i contesti inclusi. Un contesto incluso viene elaborato dopo un modello nello stesso contesto.

## L'istruzione #INCLUDE

Dovremmo usare un file grande o diversi file? Puoi usare l'istruzione #include <filename> per includere altri file nel tuo extensions.conf. Per esempio, potremmo creare un users.conf per gli utenti locali e un services.conf per i servizi speciali. Fai attenzione a non confondere #include <filename> con il

```
include=>context statement.
```

## Subroutine con GOSUB

Nelle versioni più vecchie di Asterisk esisteva il comando Macro. Questo comando è stato deprecato molto tempo fa a favore di GOSUB. Qui dimostreremo come creare subroutine per l'elaborazione della segreteria telefonica in modo semplice e ordinato. Formato del comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

Il comando GOSUB è disponibile sin da Asterisk 1.6 e supporta il passaggio di argomenti (disponibili all'interno della subroutine come `${ARG1}`, `${ARG2}`, e così via). Con gli argomenti è ora possibile sostituire completamente i vecchi comandi Macro. Le macro (`app_macro`) sono state rimosse in Asterisk 21; è necessario usare GOSUB per le subroutine.

### Creazione della subroutine

La definizione è molto simile. Guardate la subroutine qui sotto definita per la segreteria telefonica con il nome stdexten (scegliete il nome che preferite). Dopo aver chiamato il comando Dial con il primo argomento (nome del canale) controlliamo il ${DIALSTATUS} per inviare la logica della chiamata al passo successivo.

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### Chiamare una subroutine

Fate attenzione, quando chiamate la subroutine, a utilizzare le parentesi prima dei parametri.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Using Asterisk DB

Per implementare il trasferimento di chiamata e le liste nere, abbiamo bisogno di un modo per memorizzare e ripristinare i dati. Fortunatamente, Asterisk fornisce un meccanismo per archiviare e recuperare dati da un database integrato chiamato AstDB. Nelle versioni moderne di Asterisk (incluso Asterisk 22) AstDB è basato su **SQLite3** (il file `/var/lib/asterisk/astdb.sqlite3`); Asterisk 1.8 e versioni precedenti usavano Berkeley DB v1. Questo è simile al database del registro di Windows che utilizza il concetto gerarchico di family e keys. I dati persistono tra i riavvii di Asterisk. L'API family/key è invariata rispetto al backend più vecchio; solo il formato di memorizzazione su disco è cambiato.

### Functions, applications, and CLI commands

Esistono alcune funzioni, applicazioni e comandi CLI che lavorano con AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Esempi:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

Alcune applicazioni possono essere usate per manipolare AstDB:

- DB_DELETE(<family/key>) — funzione che restituisce ed elimina una singola chiave
- DBdeltree(<family>) — applicazione che elimina un intero family/subtree

La vecchia applicazione `DBdel()` non esiste più in Asterisk 22. Elimina una singola chiave con la funzione dialplan `DB_DELETE()` — ad es. `Set(x=${DB_DELETE(family/key)})` o, come operazione di scrittura, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (elimina un intero family/subtree) è ancora un'applicazione.

È possibile usare i comandi CLI per impostare ed eliminare chiavi anche:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementing Call Forward, DND, and Blacklists

In questo esempio imparerai come implementare il trasferimento di chiamata immediato e il trasferimento di chiamata in caso di occupato. Useremo *21* per programmare il trasferimento immediato e *61* per programmare il trasferimento in caso di occupato. Per annullare la programmazione, usa rispettivamente #21# e #61#. Usa l'esempio sopra per popolare il database. Family utilizzate:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Prova a popolare il database componendo:

- *21* (Estensione di destinazione per il trasferimento immediato)
- *61* (Estensione di destinazione per il trasferimento in caso di occupato)
- *41* (Estensione da mettere in modalità non disturbare)

Usa il comando CLI `database show` per vedere le family, le chiavi e i valori aggiunti.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward, Blacklist, DND

La subroutine verifica se il database contiene le coppie chiave:valore corrispondenti a CFIM, CFBS o DND, e quindi le gestisce in modo appropriato. La subroutine seguente chiama la routine di composizione:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Using a blacklist

The old `LookupBlacklist()` application was **removed** from Asterisk (it disappeared together with the legacy "priority+101 jump" mechanism). In Asterisk 22 you build a blacklist directly with the `DB_EXISTS()` function (which both tests for a key and, when found, exposes its value in `${DB_RESULT}`) plus `GotoIf`. Store each blocked number as a key in a `blacklist` family, then check the caller ID at the top of your incoming context:

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})` returns `1` when the caller's number is present in the database (sending the call to the `blocked` context) and `0` otherwise, so the call proceeds to the normal `Dial()`.

To insert a number in the blacklist, we can use the same resource as before, using *31* followed by the extensions to be blacklisted. To remove a number from the blacklist, you should use #31# followed by the number to be removed.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

You can also insert the numbers in the blacklist using the console CLI:

```
*CLI>database put blacklist <name/number> 1
```

Note: Any value can be associated with the key. The `DB_EXISTS()` test searches for the key, not the value. To erase the number from the blacklist, you can use:

```
*CLI>database del blacklist <name/number>
```

## Contesti basati sul tempo

Nella figura seguente, abbiamo un dialplan con tre contesti. Il contesto [incoming] è dove le chiamate vengono solitamente ricevute. Abbiamo incluso quattro righe che modificano il comportamento a seconda dell'ora di sistema, come mostrato di seguito:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modern Asterisk (including 22) separates the time-include fields with **commas**, not pipes. The legacy pipe form (`include => context|times|weekdays|mdays|months`) is parsed as a plain literal context name and silently fails to apply any time condition.

During regular working hours, processing will be redirected to the mainmenu, where it will probably call an IVR to handle the incoming call. If the call takes place after hours, it will call the security extension defined in the ${SECURITY} variable. If the security extension does not answer the call, it will be sent to the operator’s voicemail.

![10-dialplan-advanced-features figura 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figura 12](../images/10-dialplan-advanced-features-img12.png)

## Messaggi basati sul tempo usando gotoiftime()

La sintassi di GotoIfTime() è mostrata di seguito.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

In Asterisk 22 il separatore di campo è una **virgola**, non una barra verticale (la forma con barra verticale è stata deprecata in Asterisk 1.6). È supportato un campo opzionale `timezone`, e ogni etichetta di ramo utilizza la consueta forma `[[context,]extension,]priority`.

Questa applicazione può sostituire il contesto basato sul tempo e sembra più facile da capire e leggere. È possibile specificare il tempo come segue:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=numero da 1 a 31
- <hour>=numero da 0 a 23
- <minute>=numero da 0 a 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

I nomi dei giorni e dei mesi non sono sensibili al maiuscolo/minuscolo.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

L'istruzione precedente trasferisce l'elaborazione all'estensione s nel contesto normalhours se la chiamata avviene tra le 08:00 e le 18:00 dal lunedì al venerdì.

## Utilizzare DISA per ottenere un nuovo tono di composizione

DISA, o “direct inward system access”, è un sistema che consente agli utenti di ricevere un secondo tono di composizione. Permette agli utenti di comporre nuovamente verso un’altra destinazione. È spesso usato dai tecnici quando effettuano chiamate a lunga distanza per supporto tecnico nei fine settimana; invece di comporre da casa direttamente verso la destinazione, chiamano il numero DISA dell’ufficio, ricevono un tono di composizione e poi chiamano la destinazione. Le tariffe per le chiamate a lunga distanza vengono addebitate all’azienda anziché al telefono di casa.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Esempio:

```
exten => s,1,DISA(no-password,default)
```

Usando l’istruzione precedente, l’utente compone il PBX e—senza richiedere alcuna password—riceve un tono di composizione. Qualsiasi chiamata che utilizza DISA verrà elaborata usando il contesto `default`. Gli argomenti per questa applicazione includono una password globale o una password individuale all’interno di un file. Se non viene specificato alcun contesto, si assume il contesto `disa`. Se si utilizza un file di password, deve essere specificato il percorso completo. È possibile specificare un caller ID anche per la composizione esterna DISA. Esempio:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 utilizza le virgole come separatori di argomenti (la forma con il pipe è stata deprecata nella 1.6). Il primo argomento è o un singolo codice di accesso o il percorso a un file di codici di accesso, e il contesto predefinito quando non è fornito è `disa`.

## Limit simultaneous calls

The GROUP() function allows you to count how many active channels you have in one group at the same time. Example: You have a branch in Rio de Janeiro, where phones follow the pattern “_214X”. This location is served by a leased line, with 64K reserved for voice bandwidth. In this case, the maximum number of allowed calls is 2 (G.729, about 31.2K per call). To limit calls to Rio by two:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

La segreteria telefonica è un sistema di risposta telefonica computerizzato che registra i messaggi vocali in arrivo, salvandoli su disco o inviandoli via e‑mail. Talvolta dispone di una directory in cui è possibile cercare le cassette vocali per nome. In passato, i sistemi di segreteria erano molto costosi. Ora, con la telefonia IP, la segreteria sta diventando una funzionalità standard.

Per configurare la segreteria, dovresti seguire i seguenti passaggi.

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — codec used to record the message (e.g., wav49, wav, gsm)
- `serveremail` — who the e-mail notification should appear to come from
- `maxmsg` — maximum number of messages in the mailbox; after this threshold, messages are discarded
- `maxsecs` — maximum length of a voicemail message, in seconds
- `minsecs` — minimum length of a message, in seconds; below this threshold, no message is recorded
- `maxsilence` — how many seconds of silence to treat as the end of the message

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

A mailbox is defined with one line per mailbox, in the form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

The fields are:

- **MailboxID** — usually the extension number
- **Pincode** — password to access the voicemail system
- **Full name** — used by the directory application
- **E-mail** — address for voicemail notification
- **Pager e-mail** — address for notification via an SMS gateway or pager
- **Options** — per-mailbox options (the same options as in `[general]`, but applied to this mailbox)

Voicemail has several options that control its behavior. For now, we will stick to the default options and concentrate on the mailbox definition. After the `[general]` section in the file, you start configuring the mailbox IDs, each in its own context. Example:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Please check for advanced options in the file `voicemail.conf`.

**Step 3: Configure the file `extensions.conf`.**

The `stdexten` subroutine shown earlier (under *Subroutines with GOSUB*) is exactly the call/voicemail handler you need here: it dials the extension and uses the value of the channel variable `${DIALSTATUS}` to redirect the call flow to the proper voicemail greeting (`b` for busy, `u` for unavailable). Call it with `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` from each extension in `extensions.conf`.

## Using the VoiceMailMain() application

L'applicazione voicemailmain() è usata per configurare la casella di posta vocale. Gli utenti possono chiamare l'applicazione, registrare il proprio saluto e ascoltare la segreteria telefonica. Per chiamare l'applicazione nel dialplan, usare:

```
exten=>9000,1,VoiceMailMain()
```

Di seguito trovi un elenco delle opzioni disponibili per l'applicazione.

### Voicemail application syntax

Questa applicazione consente alla parte chiamante di lasciare un messaggio per un elenco specificato di caselle di posta. Quando vengono specificate più caselle, il saluto verrà preso dalla prima casella indicata. L'esecuzione del dialplan si interromperà se la casella specificata non esiste. La sintassi è mostrata di seguito:

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

In tutti i casi, il file beep.gsm verrà riprodotto prima dell'inizio della registrazione. I messaggi di segreteria telefonica saranno salvati nella directory inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Se un chiamante preme 0 (zero) durante l'annuncio, verrà spostato all'estensione ‘o’ (out) nel contesto corrente della segreteria telefonica. Questo può essere usato per uscire verso l'operatore. Se durante la registrazione il chiamante preme # o il limite di silenzio scade, la registrazione si interrompe e la chiamata passa alla priorità successiva. Assicurati di gestire la chiamata dopo che la segreteria è stata riprodotta, come mostrato di seguito.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

Puoi etichettare alcuni messaggi come “urgenti”. Sono disponibili due metodi:

- Passare l'opzione ‘U’ nell'applicazione voicemail()
- Specificare review=yes nel file voicemail.conf. Se usi questa opzione, l'utente potrà etichettare il messaggio come urgente dopo aver registrato le istruzioni vocali.

## Invio della segreteria telefonica via e‑mail

In alcuni casi (come il mio), non utilizziamo semplicemente l’applicazione voicemailmain() per leggere le e‑mail. È più semplice e pratico inviare tutti i messaggi via e‑mail con l’audio allegato. Usando i parametri ‘attach’ e ‘delete’, è possibile inviare tutte le e‑mail e cancellarle dalla casella di posta.

```
attach=yes
delete=yes
```

Per inviare la segreteria telefonica via e‑mail, l’applicazione voicemail utilizza il message transfer agent (MTA), un componente del tuo sistema operativo. Debian utilizza Exim come MTA. L’applicazione che invia l’e‑mail è definita nel parametro ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

Nella distribuzione Debian di Linux, il MTA è Exim. Per configurare Exim in Debian, usa:

```
dpkg-reconfigure exim4-config
```

Puoi scegliere di far inviare al tuo MTA un’e‑mail direttamente tramite SMTP o tramite uno smarthost (di solito il server di posta della tua azienda). Verifica con l’amministratore della tua e‑mail il modo migliore per inviare le e‑mail dal server Asterisk al tuo server di posta.

## Personalizzare il messaggio e‑mail

È possibile controllare come vengono inviati i messaggi impostando le seguenti variabili: Variabili per l'oggetto e il corpo dell’e‑mail:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Il corpo e l'oggetto dell’e‑mail sono costruiti a partire da un modello che si imposta nella sezione `[general]` di `voicemail.conf`. È possibile modificare sia il corpo sia l'oggetto, ma il limite di dimensione del messaggio è di 512 byte. Nel modello, `\n` inserisce una nuova riga e `\t` inserisce una tabulazione.

L’esempio `emailsubject` qui sotto è semplice. L’esempio `emailbody` è molto vicino al valore predefinito; il valore predefinito mostra solo il CIDNAME quando non è nullo, altrimenti il CIDNUM, o “un chiamante sconosciuto” quando entrambi sono nulli.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interfaccia Web della segreteria telefonica

Esiste uno script Perl nella distribuzione sorgente chiamato `vmail.cgi`, situato in `contrib/scripts/vmail.cgi` nell'albero dei sorgenti di Asterisk (è ancora incluso in Asterisk 22). Il comando `make install` non installa questa interfaccia; è necessario eseguire `make webvmail` dalla directory dei sorgenti. Questo script richiede l'interprete di comandi Perl e un server web (come Apache) installati sul server.

```
make webvmail
```

Il target `make webvmail` installa lo script (setuid root) nella directory CGI del tuo server web (`HTTP_CGIDIR`) e copia le immagini di supporto da `images/*.gif` in `HTTP_DOCSDIR/_asterisk` (per impostazione predefinita `/var/www/html/_asterisk`). Se questi percorsi non corrispondono alla struttura del tuo server web, modifica le variabili `HTTP_CGIDIR` e `HTTP_DOCSDIR` nel file `Makefile` di livello superiore prima di eseguire il target.

## Notifica della segreteria telefonica

È possibile configurare la segreteria telefonica per inviare un messaggio di notifica al proprio telefono quando si riceve una nuova segreteria. In Asterisk 22, il Message Waiting Indication (MWI) funziona con telefoni PJSIP e SIP così come con telefoni DAHDI. Per indicare una segreteria non ascoltata, una luce indicatrice può lampeggiare o il telefono può riprodurre un tono di avviso. È necessario configurare la casella postale nel file di configurazione del canale corrispondente. Esempio: `pjsip.conf` (nella sezione endpoint):

```
mailboxes=8590
```

In PJSIP l'indicatore della casella postale è impostato con l'opzione `mailboxes` all'interno della sezione endpoint di `pjsip.conf`, anziché con il vecchio `mailbox=` di `sip.conf`. Le sottoscrizioni MWI sono gestite dal modulo `res_pjsip_mwi`.

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Laboratorio: Notifica dei messaggi sul telefono

Questo laboratorio è stato testato usando un softphone SIP.

1. Modifica `pjsip.conf` e aggiungi `mailboxes=4401` nella sezione endpoint per il dispositivo denominato 4401.
2. Modifica il `extensions.conf` e crea un'estensione per registrare una segreteria su 4401 extensions.

```
exten=9008,1,voicemail(4401,b)
```

3. Vai alla console e ricarica.
4. Nel SipPulse Softphone, apri le impostazioni dell'account SIP e abilita il controllo della segreteria (message-waiting) per l'account.
5. Componi 9008 e lascia un messaggio.
6. Osserva l'icona del messaggio sul telefono.

## Utilizzo dell'applicazione directory

Questa applicazione consente di trovare rapidamente un utente da chiamare. L'elenco dei nomi e le relative estensioni vengono recuperati dal file di configurazione della segreteria telefonica `voicemail.conf`. La sintassi per l'applicazione può essere mostrata usando `core show application directory`:

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### Laboratorio: Utilizzo dell'applicazione directory

1. Modifica il file `voicemail.conf` per aggiungere due estensioni nel dialplan

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Crea queste estensioni nel tuo dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vai alla console e ricarica  
4. Digita `9006` e registra un nome per ciascuna estensione (4400, 4401)  
5. Digita `9007` e seleziona le tre lettere del cognome per una delle estensioni (Eas=327). Se questa è l'opzione corretta, premi `1` per trasferire al nome.

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## Sommario

In questo capitolo hai imparato come ricevere chiamate usando un IVR o un operatore automatico. Hai studiato il concetto di inclusione dei contesti e implementato alcuni esempi. Sono state usate subroutine per evitare la digitazione ripetitiva, e il database di Asterisk (AstDB, basato su SQLite3 in Asterisk 22) è stato utilizzato per funzioni che richiedono la memorizzazione dei dati (ad esempio, inoltro chiamata, non disturbare, blacklist). Infine, hai appreso come implementare il comportamento fuori orario e hai realizzato un piano di composizione completo usando questi concetti.

## Quiz

1. Un contesto dipendente dal tempo include l'uso della forma `include => context,<times>,<weekdays>,<mdays>,<months>`. Cosa fa `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Esegue le estensioni dal lunedì al venerdì, dalle 08:00 alle 18:00
   - B. Esegue le opzioni ogni giorno in tutti i mesi
   - C. Nulla; il formato è non valido
2. Nelle versioni moderne di Asterisk (incluso Asterisk 22), i campi di un `include =>` basato sul tempo e di `GotoIfTime()` sono separati da quale carattere?
   - A. Il pipe `|`
   - B. La virgola `,`
   - C. Il punto e virgola `;`
   - D. La barra `/`
3. Per chiamare più canali contemporaneamente (facendoli squillare simultaneamente), li separi all'interno di `Dial()` con il carattere ___.
4. Un menu vocale che riproduce un prompt in attesa che il chiamante digiti un'estensione è solitamente creato con l'applicazione ___.
5. Puoi includere il contenuto di un altro file all'interno di `extensions.conf` usando l'istruzione ___ (nota: è diversa dall'istruzione di contesto `include =>`).
6. In Asterisk 22, il database interno AstDB è basato su:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Quando usi `Dial(type1/identifier1&type2/identifier2)`, Asterisk chiama ogni canale in sequenza, attendendo 20 secondi tra di loro.
   - A. Falso
   - B. Vero
8. Con l'applicazione Background(), devi attendere che il messaggio termini la riproduzione prima di poter premere un tasto DTMF per scegliere un'opzione.
   - A. Falso
   - B. Vero
9. Data la sintassi `Goto([[context,]extension,]priority)`, quali delle seguenti sono invocazioni valide dell'applicazione Goto()? (seleziona tutte le risposte corrette)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Per eliminare una singola chiave da AstDB nel dialplan di Asterisk 22, usi:
    - A. L'applicazione `DBdel()`
    - B. La funzione `DB_DELETE()`
    - C. L'applicazione `DBdeltree()`
    - D. L'applicazione `LookupBlacklist()`

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
