# Code Queues

Le code di chiamata, note anche come ACD (Automatic Call Distribution), stanno diventando sempre più importanti per rispondere in modo efficiente alle chiamate dei clienti. Un distributore automatico di chiamate può aiutare a ridurre i costi, migliorare il servizio e incrementare le vendite, poiché i distributori di chiamate influenzano il funzionamento della tua attività, non solo per pochi giorni, ma per molti anni. In un ambiente di call center, il fattore numero uno sono le persone; sono la risorsa più costosa. Richiede tempo, denaro e pazienza assumere, formare e motivare gli agenti. Con un ACD, puoi massimizzare la produttività degli agenti dimensionando con precisione il numero di agenti richiesti, controllando gli operatori validi e quelli meno efficienti e analizzando il flusso delle chiamate.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Comprendere perché e come utilizzare le code di chiamata
- Comprendere la teoria di base delle code di chiamata
- Installare e configurare il sistema di code

## Come funzionano le code?

Le code di chiamata non sono esattamente una novità. Quando hai un flusso elevato di chiamate in entrata, è difficile distribuire le chiamate in modo appropriato. L'utilizzo di una strategia di gruppo in cui il telefono squilla simultaneamente su tutti gli agenti non sembra funzionare, a meno che tu non abbia solo pochi agenti. Tuttavia, una coda di chiamata inoltrerà le chiamate a un singolo agente disponibile alla volta e metterà il cliente in attesa con musica quando non ci sono agenti disponibili. La coda funziona trattenendo la chiamata mentre cerca un agente libero per rispondere. Uno dei maggiori vantaggi della coda è evitare di perdere chiamate fornendo al contempo la possibilità di generare statistiche.

![Una coda di chiamata: le chiamate 1-800 in entrata entrano nella coda e una strategia ACD (ringall, rrmemory, leastrecent, priority e altre) le distribuisce agli agenti disponibili](../images/14-queues-fig01.png)

Di solito, una coda di chiamata funziona così:

- Gli agenti effettuano il login nella coda.
- Le chiamate in entrata vengono accodate.
- Viene utilizzata una strategia di accodamento per distribuire le chiamate agli agenti.
- La musica di attesa (Music on hold) viene riprodotta mentre il chiamante attende.
- È possibile effettuare annunci ai chiamanti, notificando loro il tempo di attesa.
- La chiamata viene risposta dall'agente e vengono generate le statistiche.

L'applicazione principale per le code è il servizio clienti. Quando utilizzi le code, eviti di perdere chiamate quando i tuoi agenti sono occupati. Puoi aggiungere nuovi agenti alla coda se noti che il numero di chiamanti in attesa sta crescendo. Un altro vantaggio delle code è che ora puoi disporre di statistiche come il tasso di abbandono delle chiamate, la durata media della chiamata e l'obiettivo di risposta alle chiamate. Queste statistiche ti aiuteranno a determinare quanti agenti utilizzare per fornire un servizio migliore al tuo cliente.

### Architettura ACD

L'architettura ACD è formata da code e agenti. Un agente può trovarsi in due code contemporaneamente. Una coda può avere agenti, canali e gruppi di agenti.

![Architettura ACD: ogni coda (Servizio Clienti, Vendite Interne) è alimentata da un numero di telefono e inoltra le chiamate agli agenti, che a loro volta sono legati a canali fisici](../images/14-queues-fig02.png)

## Code

Le code sono definite nel file di configurazione queues.conf. Gli agenti sono operatori che effettuano il login e sono membri delle code. Gli agenti sono definiti nel file agents.conf. Il sistema di code è cresciuto significativamente nel corso di molte versioni, rendendo il file di configurazione esteso. Spiegheremo alcuni dei parametri principali. Parametri generali

```
autofill=yes
```

Il vecchio comportamento per la coda era di tipo seriale. La coda attendeva che una chiamata venisse smistata prima di inviare la chiamata successiva all'agente seguente. Se un agente impiegava 15 secondi per rispondere a una chiamata, le altre chiamate nella coda dovevano attendere fino a quando quella chiamata non veniva risposta. Per le code ad alto volume, questo comportamento era inefficiente. Il nuovo comportamento autofill=yes non attende che una chiamata venga risposta, ma lavora in parallelo. Puoi registrare le chiamate nella coda utilizzando l'opzione mixmonitor. In questa modalità, le chiamate vengono registrate e mixate contemporaneamente.

### File di configurazione delle code

Le code sono configurate nel file queues.conf. Nella figura, troverai un esempio funzionante di una coda.

![Un esempio funzionante del file queues.conf, che mostra la sezione generale e una coda customerservice con strategia, livello di servizio, annunci, registrazione e membri](../images/14-queues-fig03.png)

### Agenti

Puoi configurare i tuoi agenti nel file agents.conf. Gli agenti possono effettuare il login da qualsiasi extension per ricevere chiamate. Puoi chiamare un agente utilizzando:

```
Dial(agent/<name>)
```

#### Agenti

Agente 300

- Puoi controllare lo stato degli agenti utilizzando il comando `agent show all`
- viene eseguito il comando agentlogin e l'agente viene associato al canale corrente.
- L'utente compone un'extension con l'applicazione agentlogin.

![Agenti: un utente effettua il login componendo un'extension che esegue l'applicazione agentlogin, che lega l'Agente 300 al canale corrente; puoi controllare lo stato dell'agente con `agent show all`](../images/14-queues-fig04.png)

Puoi definire gli agenti nel file agents.conf

```
; Agent configuration
[general]
persistentagents=yes
[agents]
autologoff=15
autologoffunavail=yes
ackcall=no
endcall=yes
wrapuptime=5000
musiconhold => default
;
;This section contains the agent definitions, in the form:
;
; agent => agentid,agentpassword,name
;
agent => 300,300
agent => 301,301
```

### Membri

I membri sono canali attivi che rispondono alla coda. I membri possono essere canali diretti (PJSIP, DAHDI) o agenti che effettuano il login prima di ricevere chiamate.

### Strategie

Le chiamate vengono distribuite tra i membri secondo una di queste strategie:

- ringall: Fa squillare tutti i canali disponibili finché qualcuno non risponde.
- leastrecent: Distribuisce al membro meno recente.
- fewestcalls: Distribuisce al membro con meno chiamate.
- random: Fa squillare un'interfaccia casuale.
- wrandom: Fa squillare un'interfaccia casuale, ma utilizza la penalità del membro come peso nel calcolo della metrica.
- rrmemory: Utilizza il round robin con memoria; ricorda dove si era interrotto con la chiamata nel passaggio precedente.
- rrordered: Uguale a rrmemory, eccetto che l'ordine dei membri della coda dal file di configurazione viene preservato.
- linear: Fa squillare i membri nell'ordine in cui sono elencati in queues.conf; per i membri dinamici, nell'ordine in cui sono stati aggiunti.

> **[Nota 2a ed.]** La strategia `roundrobin` è stata sostituita da `rrmemory` nelle prime versioni di Asterisk e non è più disponibile. Rimuovila dall'elenco delle strategie se appariva nel testo dell'edizione precedente. Tutte le strategie sopra elencate sono confermate presenti in Asterisk 22.

## Agenti

Gli agenti sono implementati come canali proxy. Possono essere utilizzati all'interno delle code. Un altro utilizzo dei canali agente è l'extension mobility. L'utente può effettuare il login utilizzando qualsiasi telefono e ricevere le proprie chiamate. Ciò consente a un utente di andare in qualsiasi stanza per renderla un ufficio. Puoi chiamare un agente nel dialplan utilizzando dial(agent/<name>). Definisci gli agenti nel file agents.conf.

![Mobilità dell'agente: l'utente solleva un telefono qualsiasi, compone un'extension di login e inserisce il numero dell'agente e la password; dopo che agentlogin() ha avuto successo, l'agente (Agente 300) è pronto a ricevere chiamate e puoi controllare lo stato con il comando CLI `agent show all`](../images/14-queues-fig05.png)

### Gruppi di agenti

Puoi scegliere di utilizzare i gruppi di agenti. Questa funzione non prende in considerazione le strategie ACD. Probabilmente preferirai elencare tutti gli agenti individualmente. Se vuoi trasferire a un gruppo di agenti, tu

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### Il file di configurazione per gli agenti

Gli agenti sono definiti nel file agents.conf. Di seguito è riportato un esempio funzionante del file.

![Un esempio funzionante del file agents.conf: una sezione generale con persistentagents, una sezione agents con i parametri predefiniti (autologoff, ackcall, endcall, wrapuptime, musiconhold) e due definizioni di agente (300 e 301)](../images/14-queues-fig06.png)

## Applicazioni correlate all'ACD

Il sistema di code di Asterisk rende disponibili diverse applicazioni per implementare le code nel dialplan. Di seguito, ne mostriamo alcune.

### L'applicazione queue()

Questa applicazione accoda le chiamate in entrata in una particolare coda di chiamata come definita in queues.conf. La stringa delle opzioni può contenere zero o più dei seguenti caratteri: Oltre a trasferire la chiamata, una chiamata può essere parcheggiata e poi ripresa da un altro utente. L'URL opzionale verrà inviato alla parte chiamata se il canale lo supporta. Il parametro AGI opzionale configurerà uno script AGI da eseguire sul canale della parte chiamante una volta che sono connessi a un membro della coda. Il timeout farà fallire la coda dopo un numero specificato di secondi, controllato tra ogni ciclo di timeout e riprova. Questa applicazione imposta la variabile di stato QUEUE al completamento:

![L'applicazione queue(): la sua sintassi `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` e le opzioni a lettera singola disponibili (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### L'applicazione agentlogin()

Questa applicazione chiede all'agente di effettuare il login nel sistema. Restituisce sempre -1. Mentre è connesso, l'agente che riceve le chiamate sentirà un segnale acustico quando arriva una nuova chiamata. L'agente può terminare la chiamata premendo il tasto *.

![L'applicazione agentlogin(): la sua sintassi `AgentLogin([AgentNo][|options])` e l'opzione `s` per un login silenzioso che non annuncia la conferma del login](../images/14-queues-fig08.png)

### L'applicazione addQueueMember()

Questa applicazione aggiunge dinamicamente un dispositivo (es. PJSIP/3000) a una coda. Se il dispositivo esiste già, restituirà un errore.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### L'applicazione removeQueueMember()

Questa applicazione rimuove dinamicamente un dispositivo dalla coda. Se il dispositivo non appartiene alla coda, restituirà un errore.

```
RemoveQueueMember(queuename[|interface])
```

### Applicazioni di supporto e comandi CLI

Alcune applicazioni e comandi della console sono in grado di aiutare il lavoro con le code. Quanto segue delinea cosa fa ogni applicazione:

![Applicazioni di supporto (AddQueueMember, RemoveQueueMember) e comandi CLI (agent show all, queue show, queue show <name>) utilizzati per gestire le code in fase di esecuzione](../images/14-queues-fig09.png)

## Attività di configurazione

La figura seguente riassume le attività principali per creare un sistema di code funzionante.

![Le attività di configurazione ACD: (1) creare la coda di chiamata (richiesto), (2) definire i parametri dell'agente (opzionale), (3) creare gli agenti (opzionale), (4) inserire la coda nel dialplan (richiesto), (5) configurare la registrazione dell'agente (opzionale) e (6) verificare con agent show all e queue show (opzionale)](../images/14-queues-fig10.png)

Passaggio 1: Creare la coda di chiamata Nel file queues.conf:

```
[telemarketing]
music = default
;announce = queue-telemarketing
;context = qoutcon
timeout = 2
retry = 2
maxlen = 0
member => Agent/300
member => Agent/301
[auditing]
music = default
;announce = queue-auditing
;context = qoutcon
timeout = 15
retry = 5
maxlen = 0
member => Agent/600
member => Agent/601
```

Passaggio 2: Definire i parametri dell'agente Nel file agents.conf:

```
debian:/etc/asterisk# cat agents.conf
;
; Agent configuration
;
[agents]
; Define maxlogintries to allow agent to try max logins before
; failed.
; default to 3
maxlogintries=5
; Define autologoff times if appropriate.  This is how long
; the phone has to ring with no answer before the agent is
; automatically logged off (in seconds)
autologoff=15
; Define autologoffunavail to have agents automatically logged
; out when the extension that they are at returns a CHANUNAVAIL
; status when a call is attempted to be sent there.
; Default is "no".
;autologoffunavail=yes
; Define ackcall to require an acknowledgement by '#' when
; an agent logs in using agentcallbacklogin.  Default is "no".
;ackcall=no
; Define endcall to allow an agent to hangup a call by '*'.
; Default is "yes". Set this to "no" to ignore '*'.
;endcall=yes
; Define wrapuptime.  This is the minimum amount of time when
; after disconnecting before the caller can receive a new call
; note this is in milliseconds.
;wrapuptime=5000
; Define the default musiconhold for agents
; musiconhold => music_class
;musiconhold => default
;
; Define the default good bye sound file for agents
; default to vm-goodbye
;agentgoodbye => goodbye_file
; Define updatecdr. This is whether or not to change the source
; channel in the CDR record for this call to agent/agent_id so
; that we know which agent generates the call
;updatecdr=no
;
; Group memberships for agents (may change in mid-file)
;
;group=3
;group=1,2
;group=
```

Passaggio 3: Creare gli agenti Nel file agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Passaggio 4: Inserire la coda nel dialplan

```
In the file extensions.conf:
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue,(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configurare la registrazione della coda

Le chiamate possono essere registrate utilizzando l'applicazione MixMonitor di Asterisk. (L'applicazione autonoma Monitor è stata rimossa in Asterisk 22 e l'opzione `monitor-type` di queues.conf ora accetta solo MixMonitor.) La registrazione può essere abilitata dall'interno dell'applicazione di coda, iniziando quando la chiamata viene effettivamente risposta. Vengono registrate solo le chiamate riuscite e non vengono eseguite registrazioni mentre le persone ascoltano la MOH. Per abilitare il monitoraggio, specifica semplicemente monitor-format. Questa funzione è altrimenti disabilitata. Puoi impostare il nome del file per la registrazione utilizzando Set (MONITOR_FILENAME=<filename>); altrimenti

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

Nel file queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Operazione della coda

I seguenti esempi spiegano come utilizzare la coda. Passaggio 1: Login dell'agente Esempio: Un agente nella coda di telemarketing solleva il telefono e compone #9000. L'agente sente un messaggio di login non valido e gli viene chiesto il nome e la password. La coda di auditing segue la stessa procedura. Passaggio 2: Coda Una volta nella coda, l'agente sentirà la MOH, se definita. Quando arriva una chiamata alla coda di telemarketing, l'agente sentirà un segnale acustico e verrà connesso a quella chiamata. Passaggio 3: Fine della chiamata Quando l'agente termina la chiamata, può:

- Premere '*' per disconnettersi e rimanere nella coda.
- Disconnettere il telefono, disconnettendosi così dalla coda.
- Premere #8000 per trasferire la chiamata per l'auditing.

## Risorse avanzate

Il sistema di code di Asterisk ha alcune funzionalità avanzate per dare priorità a determinati clienti e agenti, nonché per abilitare un menu utente.

### Menu utente

Puoi definire un menu per un utente in attesa nella coda utilizzando extension a una cifra. Per abilitare questa opzione, definisci un context nella configurazione della coda queues.conf.

### Penalità

Gli agenti possono essere configurati con una penalità. Una coda invierà le chiamate prima agli utenti con valori di penalità inferiori. Ad esempio, poiché sappiamo che i nostri clienti adorano Susan e la sua voce dolce, potremmo scegliere di assegnarle la priorità 0. In alternativa, l'agente di nome Uber, che ha meno esperienza, è meno preferito per il servizio clienti; pertanto, assegniamo a questo agente la priorità 10. Nel file queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priorità

Le code operano in modalità FIFO (first in first out). Se vuoi dare priorità a clienti speciali (platino, oro) puoi impostare priorità differenziate. Per i clienti platino o oro:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clienti blu:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## L'applicazione agentcallbacklogin() è stata rimossa

L'applicazione `agentcallbacklogin()` è stata deprecata da Digium in Asterisk 1.4 (luglio 2006) e non è più disponibile in Asterisk 22. L'approccio consigliato è utilizzare `AddQueueMember()` con un'interfaccia PJSIP per aggiungere dinamicamente membri in stile callback a una coda. Il documento `queues-with-callback-members.txt` era incluso nelle vecchie directory `/doc` di Asterisk per la guida alla migrazione.

> **[Nota 2a ed.]** Verifica se il driver di canale `chan_agent` (app_agent_pool) è ancora il meccanismo preferito per il comportamento di callback dell'agente in Asterisk 22, o se i membri PJSIP diretti con `AddQueueMember()`/`RemoveQueueMember()` sono ora lo standard.

## Statistiche della coda

Tutti gli eventi dalle code vengono registrati in /var/log/asterisk/queue_log. Il formato del registro della coda è pubblicato nel documento queuelog.txt nella directory /doc della documentazione di Asterisk. Di seguito sono riportati alcuni degli eventi registrati più importanti.

- ABANDON(position|origposition|waittime)
- AGENTDUMP
- AGENTLOGIN(channel)
- AGENTLOGOFF(channel|logintime)
- ATTENDEDTRANSFER(destexten|destcontext|holdtime|calltime|origposition)
- BLINDTRANSFER(extension|context|holdtime|calltime|origposition)
- COMPLETEAGENT(holdtime|calltime|origposition)
- COMPLETECALLER(holdtime|calltime|origposition)
- CONFIGRELOAD
- CONNECT(holdtime|bridgedchanneluniqueid)
- ENTERQUEUE(url|callerid)
- EXITEMPTY(position|origposition|waittime)
- EXITWITHKEY(key|position)
- EXITWITHTIMEOUT(position|origposition|waittime)
- QUEUESTART
- RINGNOANSWER(ringtime)
- SYSCOMPAT

Puoi costruire la tua utility per elaborare questi eventi o utilizzare un pacchetto di statistiche pronto all'uso. Abbiamo testato due utility su voip.school:

- Qlog analyzer (http://www.micpc.com/qloganalyzer/) – Eccellente pacchetto open source
- Queue metrics (http://queuemetrics.com/) – Uno dei pacchetti più completi per le statistiche delle code

> **[Nota 2a ed.]** Verifica che entrambi gli strumenti di statistica di terze parti sopra indicati siano ancora mantenuti e compatibili con il formato queue_log di Asterisk 22. Considera l'aggiunta di un riferimento all'Asterisk REST Interface (ARI) come alternativa moderna per la creazione di integrazioni di reportistica delle code personalizzate.

## Riepilogo

In questo capitolo hai imparato come utilizzare un ACD, la sua architettura e come configurarlo. Sono state presentate anche alcune funzionalità avanzate come priorità e penalità.

## Quiz

1. Quali delle seguenti sono strategie di distribuzione delle code valide in `queues.conf` (scegli tutte le opzioni applicabili)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. Puoi registrare una conversazione tra un agente e un cliente dall'interno della coda impostando l'opzione ___ nel file `queues.conf`.
3. Quale `strategy` fa squillare i membri nell'ordine esatto in cui sono elencati in `queues.conf`?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. Quando l'agente termina una chiamata nell'esempio di telemarketing, quali azioni può intraprendere (scegli tutte le opzioni applicabili)?
   - A. Premere `*` per disconnettersi e rimanere nella coda
   - B. Riagganciare il telefono e disconnettersi dalla coda
   - C. Premere `#8000` per trasferire la chiamata per l'auditing
   - D. Premere `#` per disconnettersi immediatamente da tutte le code
5. Quali due attività sono *richieste* per ottenere una coda funzionante (scegli tutte le opzioni applicabili)?
   - A. Creare la coda
   - B. Creare gli agenti
   - C. Configurare i parametri dell'agente
   - D. Configurare la registrazione
   - E. Inserire la coda nel dialplan
6. In una coda di chiamata puoi offrire un menu a una cifra che il chiamante può comporre mentre è in attesa. Questo si abilita definendo un/a ___ nella sezione `queues.conf` della coda:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. Le applicazioni di supporto `AddQueueMember()` e `RemoveQueueMember()` vengono utilizzate nel ___ per aggiungere o rimuovere membri in fase di esecuzione:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Poiché chan_sip è stato rimosso in Asterisk 21, un membro statico della coda deve fare riferimento a un canale come ___ piuttosto che `SIP/1001`.
9. Il parametro `wrapuptime` è il tempo minimo dopo che un agente disconnette una chiamata prima che la coda invii a quell'agente una nuova chiamata.
   - A. True
   - B. False
10. A un chiamante può essere assegnata una posizione più alta nella stessa coda impostando la variabile di canale `QUEUE_PRIO` prima di chiamare `Queue()`.
    - A. True
    - B. False

**Risposte:** 1 — A, C, D, E, F (roundrobin è stato sostituito da rrmemory e non esiste più) · 2 — `monitor-format` (la registrazione dalla coda è abilitata specificando `monitor-format`; `monitor-type` seleziona MixMonitor vs Monitor) · 3 — C (linear) · 4 — A, B, C (`*` disconnette e rimane; `#` non è un tasto di disconnessione totale) · 5 — A, E · 6 — C (l'opzione `context`) · 7 — A (il dial plan) · 8 — `PJSIP/1001` (qualsiasi interfaccia `PJSIP/`) · 9 — True · 10 — True
