# Funzionalità avanzate del dialplan

Il Capitolo 3 ha trattato le basi di un dialplan. Per ragioni didattiche, non abbiamo spiegato tutte le funzionalità, ma solo alcune delle più importanti. Questo capitolo approfondirà il dialplan, descrivendo tecniche avanzate, nuove applicazioni e concetti.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Semplificare le voci delle tue extension
- Gestire la sicurezza del dialplan e filtrare le extension
- Ricevere chiamate utilizzando un menu IVR
- Utilizzare le subroutine per evitare riscritture non necessarie
- Implementare la sicurezza del dialplan utilizzando "Include"
- Implementare il follow-me utilizzando AsteriskDB
- Implementare il comportamento fuori orario nel tuo PBX
- Utilizzare il comando switch per trasferire a un altro PBX
- Implementare il privacy manager
- Implementare la voicemail
- Implementare una rubrica aziendale

## Semplificare il tuo dialplan

Puoi semplificare il tuo dialplan utilizzando la parola chiave "same" per definire un'extension. Ciò dovrebbe ridurre il numero di errori di battitura nel dialplan. Controlla l'esempio qui sotto:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Sicurezza del dialplan

È stata scoperta una falla nel dialplan di Asterisk che consente a un utente di iniettare un nuovo canale e un numero di chiamata nel tuo dialplan. Supponiamo che tu abbia la seguente riga nel tuo server `exten=>_X.,1,Dial(PJSIP/${EXTEN})` e che un utente malintenzionato componga il numero `3000&DAHDI/1/011551123456789` nel softphone. Il protocollo SIP, per impostazione predefinita, accetta qualsiasi carattere alfanumerico, quindi l'extension composta attiverà effettivamente due chiamate: una per il canale PJSIP/3000 e l'altra per il canale DAHDI/011551123456789, che è un numero internazionale. Pertanto, qualsiasi utente con accesso a un'extension può effettivamente chiamare ovunque nel mondo. Il modo più semplice per evitare questo comportamento è filtrare i numeri prima di chiamare l'applicazione dial. La funzione FILTER() è molto utile per questo. Esempio:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

L'applicazione filter ti consentirà di filtrare tutti i caratteri dal numero composto ad eccezione dei numeri da 0 a 9. Maggiori informazioni possono essere trovate nel file README-SERIOUSLY.bestpractices.txt disponibile da Asterisk.

## Ricevere chiamate utilizzando un menu IVR.

Nell'ultima sezione, hai ricevuto tutte le chiamate utilizzando DID o inoltrandole all'operatore. Ora imparerai come implementare un menu IVR e come creare un servizio di auto-attendant. Prima di entrare nello specifico, esaminiamo alcune nuove applicazioni. Abbiamo inserito l'output del comando show application qui sotto semplicemente per renderlo più facile da leggere per gli utenti. Puoi ottenere queste descrizioni utilizzando show application application_name. 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### L'applicazione Background()

Questa applicazione riprodurrà l'elenco di file fornito in attesa che un'extension venga composta dal canale chiamante. Per continuare ad attendere le cifre dopo che questa applicazione ha terminato la riproduzione dei file, dovrebbe essere utilizzata l'applicazione WaitExten. L'opzione langoverride specifica esplicitamente quale lingua tentare di utilizzare per i file audio richiesti. Qualsiasi context specificato sarà il context del dialplan che questa applicazione utilizza quando esce verso un'extension composta. Se uno dei file audio richiesti non esiste, l'elaborazione della chiamata verrà terminata. Opzioni:

- s - Causa il salto della riproduzione del messaggio se il canale non è nello stato 'up' (ovvero, non ha ancora risposto). Se ciò accade, l'applicazione tornerà immediatamente.
- n - Non rispondere al canale prima di riprodurre i file.
- m - Interrompi solo se una cifra digitata corrisponde a un'extension a una cifra nel context di destinazione.

### L'applicazione Record()

Questa applicazione registra dal canale in un dato nome file. Se il file esiste, verrà sovrascritto.

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' è il formato del tipo di file da registrare (wav, gsm, ecc.).
- 'silence' è il numero di secondi di silenzio consentiti prima di tornare.
- 'maxduration' è la durata massima della registrazione in secondi; se manca o è zero, non c'è massimo.
- 'options' può contenere una delle seguenti lettere:
    - `a` — aggiunge a una registrazione esistente invece di sostituirla
    - `n` — non rispondere, ma registra comunque se la linea non ha ancora risposto
    - `q` — silenzioso (non riprodurre un segnale acustico)
    - `s` — salta la registrazione se la linea non ha ancora risposto
    - `t` — utilizza il tasto terminatore alternativo `*` (DTMF) invece del predefinito `#`
    - `x` — ignora tutti i tasti terminatori (DTMF) e continua a registrare fino alla chiusura della chiamata

Se il nome file contiene %d, questi caratteri verranno sostituiti con un numero incrementato di uno ogni volta che il file viene registrato. Usa core show file formats per vedere i formati disponibili sul tuo sistema. L'utente può premere # per terminare la registrazione e passare alla priorità successiva. Se l'utente chiude la chiamata durante una registrazione, tutti i dati andranno persi e l'applicazione terminerà.

### L'applicazione Playback()

Questa applicazione riproduce i nomi file forniti (non includere l'estensione). Le opzioni possono anche essere incluse dopo un simbolo pipe. L'opzione 'skip' causa il salto della riproduzione del messaggio se il canale non è nello stato 'up' (ovvero, non ha ancora risposto).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Se viene specificato 'skip', l'applicazione tornerà immediatamente se il canale non è sganciato. Altrimenti, a meno che non venga specificato 'noanswer', il canale riceverà risposta prima che il suono venga riprodotto. Non tutti i canali supportano la riproduzione di messaggi mentre sono ancora agganciati. Se viene specificato 'j', l'applicazione salterà alla priorità n+101 quando il file non esiste, se presente. Questa applicazione imposta la seguente variabile di canale al completamento:

- PLAYBACKSTATUS — lo stato del tentativo di riproduzione come stringa di testo, uno tra:
    - `SUCCESS`
    - `FAILED`

### L'applicazione Read()

Questa applicazione legge un numero predeterminato di cifre, un certo numero di volte, dall'utente nella variabile data.

- filename -- file da riprodurre prima di leggere le cifre o il tono con l'opzione i
- maxdigits -- numero massimo accettabile di cifre. Interrompe la lettura dopo che sono state inserite maxdigits (senza richiedere all'utente di premere il tasto #). Il valore predefinito è 0 - nessun limite - per attendere che l'utente prema il tasto #. Qualsiasi valore inferiore a 0 significa lo stesso. Il valore massimo accettato è 255.

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- le opzioni sono `s`, `i`, `n`:
    - `s` — torna immediatamente se la linea non è attiva
    - `i` — riproduci filename come tono di indicazione dal tuo `indications.conf`
    - `n` — leggi le cifre anche se la linea non è attiva
- attempts -- se maggiore di 1, il numero di tentativi che verranno effettuati nel caso in cui non vengano inseriti dati
- timeout -- Un numero intero di secondi da attendere per una risposta in cifre. Se maggiore di 0, tale valore sovrascriverà il timeout predefinito.

L'applicazione read() dovrebbe disconnettersi se la funzione fallisce o genera un errore.

### L'applicazione Gotoif()

Questa applicazione farà saltare il canale chiamante alla posizione specificata nel dialplan in base alla valutazione della condizione data. Il canale continuerà a labeliftrue se la condizione è vera, o 'labeliffalse' se la condizione è falsa. Le etichette sono specificate con la stessa sintassi utilizzata all'interno dell'applicazione Goto. Se l'etichetta scelta dalla condizione viene omessa, non viene eseguito alcun salto; piuttosto, l'esecuzione continua con la priorità successiva nel dialplan.

### Lab: Costruire un menu IVR passo dopo passo

Creiamo un menu IVR con la seguente funzionalità. Quando composto, l'IVR riproduce un file audio con il messaggio "Benvenuti alla XYZ Corporation; premi 1 per le vendite, 2 per il supporto tecnico, 3 per la formazione, o attendi per parlare con un rappresentante." Le cifre instradano il chiamante come segue:

- `1` — trasferisci alle vendite (PJSIP/4001)
- `2` — trasferisci al supporto tecnico (PJSIP/4002)
- `3` — trasferisci alla formazione (PJSIP/4003)
- Nessuna cifra premuta — trasferisci all'operatore (PJSIP/4000)

**Passaggio 1 – Registra i prompt**

Creiamo un'extension per registrare i prompt. Per registrare un prompt, componi da un softphone il numero `9003<filename>` (ad esempio, `9003welcome`). Quando senti il segnale acustico, inizia a registrare; premi `#` per interrompere. Sentirai un segnale acustico e il sistema riprodurrà il prompt registrato.

**Passaggio 2 – Crea la logica del menu**

Quando si compone l'extension 9004, l'elaborazione salta al menu nell'extension `s`, priorità 1.

### Corrispondenza durante la composizione

Questo è un menu di configurazione aziendale per la ricezione di chiamate. L'applicazione background legge il context corrente e definisce la lunghezza massima per ogni numero per qualsiasi combinazione possibile.

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

Quando chiami questa azienda, viene riprodotto prima il messaggio di benvenuto. Dopodiché, Asterisk attende che venga composta una cifra. Numero composto Asterisk Azione Chiama immediatamente Dial(DAHDI/1) Attende il timeout, quindi va a Dial(DAHDI/2) Chiama immediatamente (DAHDI/3) Chiama immediatamente (DAHDI/4) Attende il timeout, quindi si disconnette Chiama immediatamente Dial(DAHDI/5) Chiama immediatamente Dial(DAHDI/6) Si disconnette immediatamente È importante evitare ambiguità nei menu. Tutti vogliono ricevere risposta rapidamente. Per questo motivo, non dovresti usare i numeri 2, 21 o 22.

### Lab: Utilizzo dell'applicazione Read()

Prova il lab con l'applicazione read(). Read accetta cifre dall'utente e le inserisce nella variabile specificata; puoi quindi utilizzare l'applicazione gotoif per reindirizzare la chiamata.

## Inclusione di context

Un context può includere i contenuti di un altro context. Nell'esempio sopra, qualsiasi canale può comporre qualsiasi extension nel context internal, ma solo il canale 4003 può comporre extension internazionali. Puoi utilizzare l'inclusione di context per semplificare la creazione del dialplan. Utilizzando l'inclusione di context, puoi controllare chi ha accesso a quali extension.

### Risoluzione dei problemi del messaggio "number not found"

È molto comune ricevere il messaggio "number not found". La maggior parte delle persone confonde il concetto di context inclusi perché non è affatto intuitivo. Come regola generale, vai prima al file di configurazione del canale in entrata, come `pjsip.conf`, `chan_dahdi.conf` e `iax.conf`, e determina il context corrente. Quindi, vai al dialplan nel file extensions.conf e controlla se il numero composto può essere trovato in quel context. In caso contrario, c'è qualcosa che non va nel tuo dialplan. Le regole d'oro dei context sono: 1. Un canale può comporre solo numeri all'interno dello stesso context del canale. 2. Il context in cui viene elaborata la chiamata è definito nel file di configurazione del canale in entrata (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Utilizzo dell'istruzione switch

Puoi inviare l'elaborazione del dialplan a un altro server utilizzando il comando switch. Avrai bisogno del nome e della chiave dell'altro server. Il context è il context di destinazione.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Ordine di elaborazione del dialplan

Quando Asterisk riceve una chiamata in entrata, cerca nel context definito dal canale. In alcuni casi, se più di un pattern corrisponde al numero composto, Asterisk non può elaborare la chiamata nel modo esatto in cui pensi che dovrebbe. Puoi vedere l'ordine di corrispondenza utilizzando il comando CLI dialplan show. Esempio: Diciamo che vuoi comporre 912 per instradare verso un trunk analogico (DAHDI/1) e tutti gli altri numeri che iniziano con 9 verso un altro trunk analogico (DAHDI/2). Scriveresti qualcosa come:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Se due pattern corrispondono a un'extension, puoi controllare quale extension viene elaborata per prima utilizzando i context inclusi. Un context incluso viene elaborato dopo un pattern nello stesso context.

## L'istruzione #INCLUDE

Dovremmo usare un file grande o diversi file? Puoi usare l'istruzione #include <filename> per includere altri file nel tuo extensions.conf. Ad esempio, potremmo creare un users.conf per gli utenti locali e services.conf per i servizi speciali. Fai attenzione a non confondere #include <filename> con il

```
include=>context statement.
```

## Subroutine con GOSUB

Nelle versioni precedenti di Asterisk avevi il comando Macro. Questo comando è stato deprecato molto tempo fa a favore di GOSUB. Dimostreremo qui come creare subroutine per l'elaborazione della voicemail in modo semplice e ordinato. Formato del comando:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

Il comando GOSUB è disponibile da Asterisk 1.6 e supporta il passaggio di argomenti (disponibili all'interno della subroutine come `${ARG1}`, `${ARG2}` e così via). Con gli argomenti, è ora possibile sostituire completamente i vecchi comandi Macro. Le Macro (`app_macro`) sono state rimosse in Asterisk 21; devi usare GOSUB per le subroutine.

### Creazione della subroutine

La definizione è molto simile. Guarda la subroutine qui sotto definita per la voicemail con il nome stdexten (scegli il nome che preferisci). Dopo aver chiamato il comando Dial con il primo argomento (nome del canale) controlliamo ${DIALSTATUS} per inviare la logica della chiamata al passaggio successivo.

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

### Chiamata di una subroutine

Presta attenzione quando chiami la subroutine a utilizzare le parentesi prima dei parametri.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Utilizzo di Asterisk DB

Per implementare l'inoltro di chiamata e le liste nere, abbiamo bisogno di un modo per archiviare e ripristinare i dati. Fortunatamente, Asterisk fornisce un meccanismo per archiviare e recuperare dati da un database integrato chiamato AstDB. Nell'Asterisk moderno (incluso Asterisk 22) AstDB è supportato da **SQLite3** (il file `/var/lib/asterisk/astdb.sqlite3`); le versioni precedenti utilizzavano Berkeley DB v1. Questo è simile al database del registro di Windows che utilizza il concetto gerarchico di famiglia e chiavi. I dati persistono tra i riavvii di Asterisk.

> **[Nota 2a ed.]** Dall'Asterisk 10, AstDB è memorizzato in SQLite3 (`astdb.sqlite3`), non nel file legacy Berkeley DB v1 utilizzato da Asterisk 1.8 e versioni precedenti. L'API famiglia/chiave è invariata.

### Funzioni, applicazioni e comandi CLI

Ci sono alcune funzioni, applicazioni e comandi CLI che funzionano con AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Esempi:

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

Alcune applicazioni possono essere utilizzate per manipolare AstDB:

- DB_DELETE(<family/key>) — funzione che restituisce ed elimina una chiave (la vecchia applicazione `DBdel()` è stata rimossa)
- DBdeltree(<family>)

> **[Nota 2a ed.]** L'applicazione `DBdel()` non esiste più in Asterisk 22. Elimina una singola chiave con la funzione di dialplan `DB_DELETE()` — ad es. `Set(x=${DB_DELETE(family/key)})` o, come operazione di scrittura, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (elimina un'intera famiglia/sottoalbero) è ancora un'applicazione.

È possibile utilizzare i comandi CLI per impostare ed eliminare anche le chiavi:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementazione di Call Forward, DND e Blacklist

In questo esempio, imparerai come implementare l'inoltro di chiamata immediato e l'inoltro di chiamata su occupato. Useremo *21* per programmare l'inoltro di chiamata immediato e *61* per programmare l'inoltro di chiamata su occupato. Per annullare la programmazione, usa #21# e #61#, rispettivamente. Usa l'esempio sopra per popolare il database. Famiglie utilizzate:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Prova a popolare il database componendo:

- *21* (Extension di destinazione per l'inoltro di chiamata immediato)
- *61* (Extension di destinazione per l'inoltro di chiamata su occupato)
- *41* (Extension da mettere in non disturbare)

Usa il comando CLI database show per vedere le famiglie, le chiavi e i valori aggiunti.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward. BlackList, DND

La subroutine sopra verifica se il database contiene le coppie chiave:valore corrispondenti a CFIM, CFBS o DND, e quindi le gestisce in modo appropriato. La subroutine follow chiama la routine di composizione:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Utilizzo di una blacklist

> **[Nota 2a ed.]** L'applicazione `LookupBlacklist()` è stata **rimossa** (è scomparsa con il vecchio meccanismo di "salto priority+101" molto prima di Asterisk 22 — confermato non registrato nel lab 22.10.0). Implementa invece una blacklist con le funzioni `DB()`/`DB_EXISTS()` più `GotoIf`, ad esempio:
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> L'esempio seguente è conservato per riferimento storico; l'opzione `j` e il salto di priorità `n+101` non esistono più.

Per creare una blacklist, utilizziamo l'applicazione LookupBlacklist(). L'applicazione controlla il nome/numero nel caller ID. Se il numero non viene trovato, l'applicazione imposta la variabile $LOOKUPBLSTATUS su NOTFOUND. Se il numero viene trovato, l'applicazione imposta la variabile su FOUND. Puoi utilizzare l'opzione "j" nell'applicazione per utilizzare il vecchio comportamento (1.0), saltando 101 posizioni se il numero/nome viene trovato. Esempio:

```
[incoming]
exten => s,1,LookupBlacklist(j)
exten => s,2,Dial(PJSIP/4000,20,tTj)
exten => s,3,Hangup()
exten => s,102,Goto(blocked,s,1)
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

Per inserire un numero nella blacklist, possiamo utilizzare la stessa risorsa di prima, utilizzando *31* seguito dalle extension da inserire nella blacklist. Per rimuovere un numero dalla blacklist, dovresti usare #31# seguito dal numero da rimuovere.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Puoi anche inserire i numeri nella blacklist utilizzando la console CLI:

```
CLI>database put blacklist <name/number> 1
```

Nota: Qualsiasi valore può essere associato alla chiave. L'applicazione blacklist cercherà la chiave, non il valore. Per cancellare il numero dalla blacklist, puoi usare:

```
CLI>database del blacklist <name/number>
```

## Context basati sul tempo

Nella figura seguente, abbiamo un dialplan con tre context. Il context [incoming] è dove le chiamate vengono solitamente ricevute. Abbiamo incluso quattro righe che cambiano comportamento a seconda dell'ora del sistema, come esemplificato di seguito:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[Nota 2a ed.]** L'Asterisk moderno (incl. 22) separa i campi time-include con **virgole**, non pipe. La forma legacy pipe (`include => context|times|weekdays|mdays|months`) viene analizzata come un nome di context letterale semplice e non riesce silenziosamente ad applicare alcuna condizione temporale. Verificato nel lab Asterisk 22.10.0.

Durante il normale orario di lavoro, l'elaborazione verrà reindirizzata al mainmenu, dove probabilmente chiamerà un IVR per gestire la chiamata in entrata. Se la chiamata avviene fuori orario, chiamerà l'extension di sicurezza definita nella variabile ${SECURITY}. Se l'extension di sicurezza non risponde alla chiamata, questa verrà inviata alla voicemail dell'operatore.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Messaggi basati sul tempo utilizzando gotoiftime()

La sintassi di gotoiftime() è mostrata di seguito.

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[Nota 2a ed.]** In Asterisk 22 il separatore di campo è una **virgola**, non un pipe (la forma pipe è stata deprecata in Asterisk 1.6). La sintassi documentata corrente è `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`. È supportato un campo opzionale `timezone`.

Questa applicazione può sostituire il context basato sul tempo e sembra più facile da capire e leggere. Puoi specificare l'ora come segue:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=numero da 1 a 31
- <hour>=numero da 0 a 23
- <minute>=numero da 0 a 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

I nomi per giorni e mesi non sono sensibili alle maiuscole.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

La dichiarazione precedente trasferisce l'elaborazione all'extension s nel context normalhours se la chiamata avviene tra le 08:00 e le 18:00 dal lunedì al venerdì.

## Utilizzo di DISA per ottenere un nuovo tono di composizione

DISA, o "direct inward system access", è un sistema che consente agli utenti di ricevere un secondo tono di composizione. Permette agli utenti di comporre di nuovo verso un'altra destinazione. Viene spesso utilizzato dai tecnici quando effettuano chiamate a lunga distanza per il supporto tecnico durante i fine settimana; invece di chiamare dalle loro case direttamente alla destinazione, chiamano il numero DISA dell'ufficio, ricevono un tono di composizione e poi chiamano la destinazione. Le spese a lunga distanza vengono addebitate all'azienda invece che al telefono di casa.

```
DISA(passcode[,context])
DISA(password-file[,context])
```

Esempio:

```
exten => s,1,DISA(no-password,default)
```

Utilizzando la dichiarazione precedente, l'utente chiama il PBX e—senza richiedere alcuna password—riceve un tono di composizione. Qualsiasi chiamata che utilizza DISA verrà elaborata utilizzando il context `default`. Gli argomenti per questa applicazione includono una password globale o una password individuale all'interno di un file. Se non viene specificato alcun context, viene assunto il context `disa`. Se utilizzi un file di password, deve essere specificato il percorso completo. Un caller ID può essere specificato anche per la composizione esterna DISA. Esempio:

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[Nota 2a ed.]** Asterisk 22 utilizza le virgole come separatori di argomenti (la forma pipe è stata deprecata nella 1.6). La sintassi completa è `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])` e il context predefinito quando non ne viene fornito nessuno è `disa` (non "DISA"). Verificato con `core show application DISA` nel lab Asterisk 22.10.0.

## Limitare le chiamate simultanee

La funzione GROUP() ti consente di contare quanti canali attivi hai in un gruppo allo stesso tempo. Esempio: Hai una filiale a Rio de Janeiro, dove i telefoni seguono il pattern "_214X". Questa posizione è servita da una linea dedicata, con 64K riservati per la larghezza di banda vocale. In questo caso, il numero massimo di chiamate consentite è 2 (G.729, 30r.2K per chiamata). Per limitare le chiamate a Rio a due:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

La voicemail è un sistema di risposta telefonica computerizzato che registra i messaggi vocali in entrata, salvandoli su disco o inviandoli via e-mail. A volte ha una rubrica dove puoi cercare le caselle vocali per nome. In passato, i sistemi di voicemail erano molto costosi. Ora, con la telefonia IP, la voicemail sta diventando una funzionalità standard.

Per configurare la voicemail, dovresti seguire i seguenti passaggi.

**Passaggio 1: Modifica `voicemail.conf` e imposta i parametri generali.**

- `format` — codec utilizzato per registrare il messaggio (ad es. wav49, wav, gsm)
- `serveremail` — da chi dovrebbe apparire provenire la notifica e-mail
- `maxmsg` — numero massimo di messaggi nella casella vocale; dopo questa soglia, i messaggi vengono eliminati
- `maxsecs` — durata massima di un messaggio vocale, in secondi
- `minsecs` — durata minima di un messaggio, in secondi; al di sotto di questa soglia, nessun messaggio viene registrato
- `maxsilence` — quanti secondi di silenzio trattare come fine del messaggio

**Passaggio 2: Modifica `voicemail.conf` e crea le caselle vocali degli utenti.**

### Voicemail.conf

Una casella vocale viene definita con una riga per casella, nella forma:

```
mailboxID => pincode,fullname,email,pager-email,options
```

I campi sono:

- **MailboxID** — solitamente il numero dell'extension
- **Pincode** — password per accedere al sistema di voicemail
- **Full name** — utilizzato dall'applicazione directory
- **E-mail** — indirizzo per la notifica della voicemail
- **Pager e-mail** — indirizzo per la notifica tramite un gateway SMS o cercapersone
- **Options** — opzioni per casella (le stesse opzioni di `[general]`, ma applicate a questa casella)

La voicemail ha diverse opzioni che ne controllano il comportamento. Per ora, ci atterremo alle opzioni predefinite e ci concentreremo sulla definizione della casella vocale. Dopo la sezione `[general]` nel file, inizi a configurare gli ID delle caselle vocali, ognuno nel proprio context. Esempio:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Si prega di verificare le opzioni avanzate nel file `voicemail.conf`.

**Passaggio 3: Configura il file `extensions.conf`.**

Di seguito, hai le istruzioni per creare la subroutine e la chiamata che implementano la voicemail in `extensions.conf`. Utilizziamo il valore della variabile di canale `${DIALSTATUS}` per reindirizzare il flusso della chiamata al menu della voicemail corretto.

### Subroutine Voicemail

## Utilizzo dell'applicazione Voicemailmain()

L'applicazione voicemailmain() viene utilizzata per configurare la casella vocale. Gli utenti possono chiamare l'applicazione, registrare il loro saluto e ascoltare la loro voicemail. Per chiamare l'applicazione nel dialplan, usa:

```
exten=>9000,1,VoiceMailMain()
```

Di seguito troverai un elenco delle opzioni disponibili per l'applicazione.

### Sintassi dell'applicazione Voicemail

Questa applicazione consente al chiamante di lasciare un messaggio per un elenco specificato di caselle vocali. Quando vengono specificate più caselle vocali, il saluto verrà preso dalla prima casella vocale specificata. L'esecuzione del dialplan si interromperà se la casella vocale specificata non esiste. La sintassi è mostrata di seguito:

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

In tutti i casi, il file beep.gsm verrà riprodotto prima che inizi la registrazione. I messaggi vocali verranno archiviati nella directory inbox.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Se un chiamante preme 0 (zero) durante l'annuncio, verrà spostato all'extension 'o' (out) nel context corrente della voicemail. Questo può essere utilizzato per uscire verso l'operatore. Se durante la registrazione il chiamante preme # o il limite di silenzio scade, la registrazione viene interrotta e la chiamata passa alla priorità successiva. Assicurati di gestire la chiamata dopo che la voicemail è stata riprodotta, come mostrato di seguito.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Contrassegnare i messaggi vocali come urgenti

Puoi contrassegnare alcuni messaggi come "urgenti". Sono disponibili due metodi per questo:

- Passa l'opzione 'U' nell'applicazione voicemail()
- Specifica review=yes nel file voicemail.conf. Se utilizzi questa opzione, l'utente sarà in grado di contrassegnare il messaggio come urgente dopo aver registrato le istruzioni vocali.

## Invio della voicemail all'e-mail

In alcuni casi (come il mio), semplicemente non utilizziamo l'applicazione voicemailmain() per leggere l'e-mail. È più semplice e pratico inviare tutti i messaggi all'e-mail con l'audio allegato. Utilizzando i parametri 'attach' e 'delete', puoi inviare tutte le e-mail all'e-mail ed eliminarle dalla casella vocale.

```
attach=yes
delete=yes
```

Per inviare la voicemail all'e-mail, l'applicazione voicemail utilizza il message transfer agent (MTA), un componente del tuo sistema operativo. Debian utilizza Exim come MTA. L'applicazione che invia l'e-mail è definita nel parametro 'mailcmd'.

```
mailcmd =/usr/sbin/sendmail -t
```

Nella distribuzione Debian di Linux, l'MTA è Exim. Per configurare Exim in Debian, usa:

```
dpkg-reconfigure exim4-config
```

Puoi scegliere di far inviare al tuo MTA un'e-mail direttamente tramite SMTP o uno smarthost (solitamente il server di posta della tua azienda). Verifica con il tuo amministratore di posta elettronica il modo migliore per inviare e-mail dal server Asterisk al tuo server di posta elettronica.

## Personalizzazione del messaggio e-mail

Puoi controllare come vengono inviati i messaggi impostando le seguenti variabili: Variabili per l'oggetto e il corpo dell'e-mail:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Il corpo e l'oggetto dell'e-mail sono costruiti da un modello che imposti nella sezione `[general]` di `voicemail.conf`. Puoi modificare sia il corpo che l'oggetto, ma il limite di dimensione del messaggio è 512 byte. Nel modello, `\n` inserisce una nuova riga e `\t` inserisce una tabulazione.

L'esempio `emailsubject` qui sotto è semplice. L'esempio `emailbody` è molto vicino a quello predefinito; quello predefinito mostra solo il CIDNAME quando non è nullo, altrimenti il CIDNUM, o "un chiamante sconosciuto" quando entrambi sono nulli.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Interfaccia Web Voicemail

C'è uno script Perl nella distribuzione sorgente chiamato `vmail.cgi`, situato in `contrib/scripts/vmail.cgi` nell'albero dei sorgenti di Asterisk (viene ancora fornito con Asterisk 22). Il comando `make install` non installa questa interfaccia; devi eseguire `make webvmail` dalla directory dei sorgenti. Questo script richiede l'interprete di comandi Perl e un server web (come Apache) installati sul server.

```
make webvmail
```

La destinazione `make webvmail` installa lo script (setuid root) nella directory CGI del tuo server web (`HTTP_CGIDIR`) e copia le immagini di supporto da `images/*.gif` in `HTTP_DOCSDIR/_asterisk` (per impostazione predefinita `/var/www/html/_asterisk`). Se quei percorsi non corrispondono al layout del tuo server web, modifica le variabili `HTTP_CGIDIR` e `HTTP_DOCSDIR` nel file `Makefile` di primo livello prima di eseguire la destinazione.

## Notifica Voicemail

Puoi configurare la voicemail per inviare un messaggio di notifica al tuo telefono quando hai una nuova voicemail. In Asterisk 22, la Message Waiting Indication (MWI) funziona con telefoni PJSIP e SIP così come con i telefoni DAHDI. Per indicare una voicemail non ascoltata, una spia luminosa potrebbe lampeggiare o il telefono potrebbe riprodurre un tono di avviso. Devi configurare la casella vocale nel file di configurazione del canale corrispondente. Esempio: `pjsip.conf` (nella sezione endpoint):

```
mailboxes=8590
```

> **[Nota 2a ed.]** In PJSIP l'hint della casella vocale viene impostato con l'opzione `mailboxes` all'interno della sezione `[endpoint]` di `pjsip.conf`, piuttosto che `mailbox=` in `sip.conf`. Le sottoscrizioni MWI sono gestite da `res_pjsip_mwi`. Verifica l'esatta sintassi di configurazione per Asterisk 22.

![L'interfaccia web Comedian Mail (`vmail.cgi`): il login Asterisk Web-Voicemail — inserisci la tua casella vocale e la password per riprodurre, salvare, inoltrare o eliminare la voicemail da un browser. Viene ancora fornito con Asterisk 22 e viene installato con `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab: Notifica messaggio nel telefono

Questo lab è stato testato utilizzando un softphone SIP. 1. Modifica `pjsip.conf` e aggiungi `mailboxes=4401` nella sezione endpoint per il dispositivo denominato 4401. 2. Modifica extensions.conf e crea un'extension per registrare una voicemail sulle extension 4401.

```
exten=9008,n,voicemail(b4401)
```

3. Vai alla CLI > console e ricarica. 4. Vai su X-Lite > Tasto destro del mouse > Impostazioni account SIP > Proprietà > Voicemail e seleziona la casella 'check voicemail'. 5. Componi 9008 e lascia un messaggio. 6. Osserva l'icona del messaggio sul telefono.

## Utilizzo dell'applicazione directory

Questa applicazione ti consente di trovare rapidamente un utente da chiamare. L'elenco dei nomi e delle extension corrispondenti viene recuperato dal file di configurazione della voicemail voicemail.conf. La sintassi per l'applicazione può essere mostrata utilizzando core show application directory:

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

### Lab: Utilizzo dell'applicazione directory

1. Modifica il file voicemail.conf per aggiungere due extension nel dialplan

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Crea queste extension nel tuo dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Vai alla console e ricarica 4. Componi 9006 e registra un nome per ogni extension (4400, 4401) 5. Componi 9007 e seleziona le tre lettere del cognome per un'extension (Eas=327). Se questa è l'opzione corretta, premi '1' per trasferire al nome.

## Lab: Mettere tutto insieme

Finora, hai imparato diversi concetti di dialplan. Mettiamo tutte le applicazioni, le funzioni e i concetti in un esempio di dialplan in modo che tu possa capire come vengono utilizzati insieme. Ti guideremo attraverso l'intera configurazione del PBX per lo scenario seguente.

- 4 trunk analogici
- 16 extension basate su SIP
- 3 classi di servizio:
    - restrict (interno, locale e 1-800)
    - ld (lunga distanza)
    - ldi (internazionale)
- Messaggio fuori orario
- Auto attendant

### Passaggio 1 – Configurazione dei canali

Trunk analogici (chan_dahdi.conf) Per prima cosa, configureremo i trunk analogici nel file di configurazione del canale DAHDI chan_dahdi.conf. In questo caso, utilizzeremo una scheda T400P Digium con 4 interfacce FXO. Supponiamo che il driver sia già caricato e che il file di configurazione del driver (/etc/dahdi/system.conf) sia configurato correttamente.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

Canali SIP (pjsip.conf) Abbiamo scelto la numerazione del dialplan da 2000 a 2099. Verranno utilizzati due codec: G.729 e G.711 ulaw. Il primo verrà utilizzato per i telefoni che utilizzano Asterisk su Internet o WAN, mentre il secondo verrà utilizzato per i telefoni che utilizzano la rete locale. In `pjsip.conf`, arbitreremo quali dispositivi apparterranno a ciascuna classe di servizio (restrict, ld, ldi). Per ridurre la vulnerabilità agli attacchi brute force, utilizzeremo gli indirizzi MAC dei telefoni come nomi dei dispositivi. Consiglio vivamente di utilizzare password forti per evitare attacchi brute force!

Definiamo un trasporto e tre modelli riutilizzabili — una base endpoint con i
codec condivisi, un'autenticazione userpass e un singolo contatto AOR — quindi colleghiamo ogni dispositivo
ai modelli e sovrascriviamo solo ciò che differisce (il suo context di classe di servizio e
credenziali). `host=dynamic` diventa un AOR a cui il telefono si registra, e
`directmedia` diventa `direct_media`:

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

[auth-userpass](!)
type=auth
auth_type=userpass

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-userpass)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-userpass)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-userpass)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Passaggio 2 – Configura il dialplan

Ora iniziamo a configurare extensions.conf. Definisci le extension interne e la composizione locale

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Definisci LD (lunga distanza)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Definisci le chiamate internazionali

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Passaggio 3 - Ricevere chiamate utilizzando un auto-attendant

Per ricevere chiamate, utilizza due context. Il primo è per il funzionamento durante il normale orario, dove la chiamata verrà ricevuta da un auto-attendant. Il secondo è per fuori orario, dove il chiamante riceverà un messaggio come "hai chiamato l'azienda XYZ, il nostro normale orario è dalle 08:00 alle 18:00; se conosci il numero dell'extension di destinazione puoi provare a comporlo ora o chiudere la chiamata." Menu: Normale orario, Fuori orario Nei menu qui sotto, il sistema riprodurrà un messaggio avvisando il chiamante che l'azienda è stata raggiunta fuori dal normale orario di lavoro, consentendo al chiamante di comporre il numero dell'extension di destinazione (qualcuno potrebbe lavorare fuori dal normale orario di lavoro).

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

Menu: Principale e Vendite Durante il normale orario di lavoro, la chiamata riceve risposta da un menu auto-attendant, ricevendo un messaggio come "benvenuti alla XYZ Company; componi 1 per le vendite, 2 per il supporto tecnico, 3 per la formazione, o il numero dell'extension desiderato".

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

Con tutte queste dichiarazioni, la funzionalità del tuo piano di composizione è ora pronta. Nella prossima sezione, dimostreremo come operare il PBX.

## Riepilogo

In questo capitolo, hai imparato come ricevere chiamate utilizzando un IVR o un auto-attendant. Hai studiato il concetto di inclusione di context e implementato alcuni esempi. Le subroutine sono state utilizzate per evitare la digitazione ripetitiva e il database Asterisk basato sul motore Berkley DB è stato utilizzato per le funzioni che richiedono l'archiviazione dei dati (ad es. inoltro di chiamata, non disturbare, blacklist). Infine, hai imparato come implementare il comportamento fuori orario e implementato un dialplan completo utilizzando questi concetti.

## Quiz

1. Un include di context dipendente dal tempo utilizza la forma `include => context,<times>,<weekdays>,<mdays>,<months>`. Cosa fa `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Esegue le extension dal lunedì al venerdì, dalle 08:00 alle 18:00
   - B. Esegue le opzioni ogni giorno in tutti i mesi
   - C. Nulla; il formato non è valido
2. Nell'Asterisk moderno (incluso Asterisk 22), i campi di un `include =>` basato sul tempo e di `GotoIfTime()` sono separati da quale carattere?
   - A. Il pipe `|`
   - B. La virgola `,`
   - C. Il punto e virgola `;`
   - D. Lo slash `/`
3. Per comporre diversi canali contemporaneamente (facendoli squillare simultaneamente), li separi all'interno di `Dial()` con il carattere ___.
4. Un menu vocale che riproduce un prompt in attesa che il chiamante componga un'extension viene solitamente creato con l'applicazione ___.
5. Puoi includere i contenuti di un altro file all'interno di `extensions.conf` utilizzando l'istruzione ___ (nota: questo è diverso dall'istruzione di context `include =>`).
6. In Asterisk 22, il database integrato AstDB è supportato da:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Quando utilizzi `Dial(type1/identifier1&type2/identifier2)`, Asterisk compone ogni canale in sequenza, attendendo 20 secondi tra loro.
   - A. Falso
   - B. Vero
8. Con l'applicazione Background(), devi attendere che il messaggio finisca di essere riprodotto prima di poter premere una cifra DTMF per scegliere un'opzione.
   - A. Falso
   - B. Vero
9. Data la sintassi `Goto([[context,]extension,]priority)`, quali delle seguenti sono invocazioni valide dell'applicazione Goto()? (segna tutte quelle applicabili)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Per eliminare una singola chiave da AstDB nel dialplan di Asterisk 22, utilizzi:
    - A. L'applicazione `DBdel()`
    - B. La funzione `DB_DELETE()`
    - C. L'applicazione `DBdeltree()`
    - D. L'applicazione `LookupBlacklist()`

**Risposte:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
