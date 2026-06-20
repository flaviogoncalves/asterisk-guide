# Call Queues

Le code di chiamata, note anche come ACD (Automatic Call Distribution), stanno diventando sempre più importanti per rispondere alle chiamate dei clienti in modo efficiente. Un distributore automatico di chiamate può aiutare a ridurre i costi, aumentare il servizio e migliorare le vendite, poiché i distributori di chiamate influenzano il modo in cui la tua azienda opera—non per pochi giorni, ma per molti anni. In un ambiente di call center, il fattore numero uno sono le persone; sono la risorsa più costosa. Ci vogliono tempo, denaro e pazienza per assumere, formare e motivare gli agenti. Con un ACD, puoi massimizzare la produttività degli agenti dimensionando con precisione il numero di agenti necessario, controllando gli operatori buoni e cattivi, e analizzando il flusso delle chiamate.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Comprendere perché e come utilizzare le code di chiamata
- Comprendere la teoria di base delle code di chiamata
- Installare e configurare il sistema di code

## Come funzionano le code?

Le code di chiamata non sono esattamente una novità. Quando hai un elevato flusso di chiamate in ingresso, è difficile distribuire le chiamate in modo appropriato. Utilizzare una strategia di gruppo in cui il telefono squilla simultaneamente su tutti gli agenti non sembra funzionare, a meno che tu non abbia solo pochi agenti. Tuttavia, una coda di chiamata consegnerà le chiamate a un singolo agente disponibile ogni volta e metterà il cliente in attesa con musica quando non ci sono agenti disponibili. La coda funziona trattenendo la chiamata mentre si trova un agente non occupato per rispondere. Uno dei maggiori vantaggi della coda è evitare la perdita di chiamate fornendo al contempo la possibilità di generare statistiche.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

Di solito, una coda di chiamata funziona così:

- Gli agenti effettuano il login alla coda.
- Le chiamate in ingresso vengono messe in coda.
- Viene utilizzata una strategia di accodamento per distribuire le chiamate agli agenti.
- Viene riprodotta la musica di attesa mentre il chiamante aspetta.
- È possibile fare annunci ai chiamanti, informandoli del tempo di attesa
- La chiamata viene risposta dall'agente e vengono generate le statistiche.

L'applicazione principale delle code è il servizio clienti. Quando usi le code, eviti di perdere chiamate quando i tuoi agenti sono occupati. Puoi aggiungere nuovi agenti alla coda se noti che il numero di chiamanti in coda sta crescendo. Un altro vantaggio delle code è che ora puoi avere statistiche come tasso di abbandono delle chiamate, durata media della chiamata e obiettivo di risposta delle chiamate. Queste statistiche ti aiuteranno a determinare quanti agenti utilizzare per fornire un servizio migliore al tuo cliente.

### Architettura ACD

L'architettura ACD è formata da code e agenti. Un agente può essere in due code contemporaneamente. Una coda può avere agenti, canali e gruppi di agenti.

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Le code sono definite nel file di configurazione queues.conf. Gli agenti sono operatori che effettuano il login e sono membri delle code. Gli agenti sono definiti nel file agents.conf. Il sistema di code è cresciuto notevolmente nel corso di molte versioni, rendendo il file di configurazione esteso. Spiegheremo alcuni dei parametri principali. Un parametro generale degno di nota è `autofill`:

```
autofill=yes
```

Il comportamento precedente per la coda era di tipo seriale. La coda attendeva che una chiamata fosse smistata prima di inviare la chiamata successiva al prossimo agente. Se un agente impiega 15 secondi per rispondere a una chiamata, le altre chiamate in coda dovevano attendere fino a quando quella chiamata fosse stata risposta. Per code ad alto volume, questo comportamento era inefficiente. Il nuovo comportamento autofill=yes non attende che una chiamata sia risposta, ma funziona in parallelo. È possibile registrare le chiamate nella coda usando l'opzione mixmonitor. In questa modalità, le chiamate sono registrate e mescolate contemporaneamente.

### Queue configuration file

Le code sono configurate nel file queues.conf. Nella figura, troverete un esempio funzionante di una coda.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

È possibile configurare i propri agenti nel file agents.conf. Gli agenti possono effettuare il login da qualsiasi interno per ricevere chiamate. È possibile chiamare un agente usando:

```
Dial(agent/<name>)
```

#### Agent login

Il flusso di login per l'Agent 300 funziona così:

- L'utente compone un interno che esegue l'applicazione `AgentLogin()`.
- `AgentLogin()` viene eseguito e l'agente viene associato al canale corrente.
- È possibile verificare lo stato degli agenti usando il comando `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

È possibile definire gli agenti nel file agents.conf

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

### Members

I membri sono canali attivi che rispondono alla coda. I membri possono essere canali diretti (PJSIP, DAHDI) o agenti che effettuano il login prima di ricevere chiamate.

### Strategies

Le chiamate sono distribuite tra i membri secondo una di queste strategie:

- ringall: Suona tutti i canali disponibili finché qualcuno non risponde.
- leastrecent: Distribuisce al membro meno recente.
- fewestcalls: Distribuisce al membro con il minor numero di chiamate.
- random: Suona un'interfaccia casuale.
- wrandom: Suona un'interfaccia casuale, ma usa la penalità del membro come peso nel calcolo della metrica.
- rrmemory: Usa round robin con memoria; ricorda dove aveva interrotto con la chiamata nell'ultimo ciclo.
- rrordered: Come rrmemory, ma l'ordine dei membri della coda nel file di configurazione è preservato.
- linear: Suona i membri nell'ordine in cui sono elencati in queues.conf; per i membri dinamici, nell'ordine in cui sono stati aggiunti.

La più vecchia strategia `roundrobin` è stata deprecata già in Asterisk 1.4. Non è più una strategia documentata e non dovrebbe essere usata: in Asterisk 22 il parser accetta ancora la parola `roundrobin`, ma solo come alias di retrocompatibilità che mappa a `rrmemory`. Usare `rrmemory` (o `rrordered`) esplicitamente al suo posto. L'elenco sopra è l'insieme delle strategie documentate per l'opzione `strategy` nell'Asterisk 22 `queues.conf`.

## Agents

Gli agenti sono implementati come canali proxy. Possono essere usati all'interno delle code. Un altro utilizzo dei canali agente è la mobilità delle estensioni. L'utente può effettuare il login usando qualsiasi telefono e ricevere le sue chiamate. Questo consente a un utente di andare in qualsiasi stanza per trasformarla in un ufficio. È possibile chiamare un agente nel dialplan usando dial(agent/<name>). Si definiscono gli agenti nel file agents.conf.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

Può essere opportuno utilizzare i gruppi di agenti. Questa funzione non prende in considerazione le strategie ACD. Probabilmente preferirai elencare tutti gli agenti singolarmente. Se vuoi trasferire a un gruppo di agenti, puoi usare `queues.conf`:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Gli agenti sono definiti nel file agents.conf. Di seguito è riportato un esempio funzionante del file.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## Applicazioni correlate all'ACD

Il sistema di code di Asterisk mette a disposizione diverse applicazioni per implementare le code nel dialplan. Di seguito ne mostriamo alcune.

### L'applicazione queue()

Questa applicazione accoda le chiamate in ingresso in una specifica coda definita in queues.conf. La stringa delle opzioni può contenere zero o più opzioni a singola lettera (mostrate nella figura sotto). Oltre a trasferire la chiamata, una chiamata può essere parcheggiata e poi ripresa da un altro utente. L'URL opzionale sarà inviato alla parte chiamata se il canale lo supporta. Il parametro AGI opzionale imposterà uno script AGI da eseguire sul canale della parte chiamante una volta connessa a un membro della coda. Il timeout farà fallire la coda dopo un numero specificato di secondi, controllato tra ogni ciclo di timeout e retry. Questa applicazione imposta la variabile di stato QUEUE al completamento:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### L'applicazione agentlogin()

Questa applicazione richiede all'agente di accedere al sistema. Restituisce sempre -1. Mentre è connesso, l'agente che riceve le chiamate sentirà un segnale acustico quando arriva una nuova chiamata. L'agente può terminare la chiamata premendo il tasto *.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### L'applicazione addQueueMember()

Questa applicazione aggiunge dinamicamente un dispositivo (ad es., PJSIP/3000) a una coda. Se il dispositivo esiste già, restituirà un errore.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### L'applicazione removeQueueMember()

Questa applicazione rimuove dinamicamente un dispositivo dalla coda. Se il dispositivo non appartiene alla coda, restituirà un errore.

```
RemoveQueueMember(queuename[|interface])
```

### Applicazioni di supporto e comandi CLI

Alcune applicazioni e comandi della console possono aiutare nella gestione delle code. Di seguito è riportato ciò che fa ciascuna applicazione:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

The figure below summarizes the major tasks to create a working queue system.

![Le attività di configurazione dell'ACD: (1) creare la coda di chiamata (obbligatorio), (2) definire i parametri dell'agente (opzionale), (3) creare gli agenti (opzionale), (4) inserire la coda nel dialplan (obbligatorio), (5) configurare la registrazione dell'agente (opzionale) e (6) verificare con agent show all e queue show (opzionale)](../images/14-queues-fig10.png)

Step 1: Create the call queue In the file queues.conf:

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

Step 2: Define agent parameters In the file agents.conf:

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

Step 3: Create the agents In the file agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Step 4: Insert the queue in the dial plan, in the file `extensions.conf`:

```
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configure queue recording

Calls may be recorded using Asterisk's MixMonitor application. (The standalone Monitor application was removed in Asterisk 22, and the queues.conf `monitor-type` option now accepts only MixMonitor.) Recording can be enabled from within the queue application, beginning when the call is actually picked up. Only successful calls are recorded, and no recordings are performed while people are listening to MOH. To enable monitoring, simply specify monitor-format. This feature is otherwise disabled. You can set the filename for the recording using `Set(MONITOR_FILENAME=<filename>)`; otherwise it will use `MONITOR_FILENAME=${UNIQUEID}`.

In the file queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Operazione della coda

Gli esempi seguenti spiegano come utilizzare la coda.

1. Accesso agente. Esempio: Un agente nella coda telemarketing risponde al telefono e compone #9000. L'agente sente un messaggio di login non valido e gli viene chiesto il nome e la password. La coda di audit segue la stessa procedura.
2. Coda. Una volta nella coda, l'agente sentirà la MOH, se definita. Quando arriva una chiamata nella coda telemarketing, l'agente sentirà un segnale acustico e verrà collegato a quella chiamata.
3. Fine chiamata. Quando l'agente termina la chiamata, può:
   - Premere ‘*’ per disconnettersi e rimanere nella coda.
   - Scollegare il telefono, uscendo così dalla coda.
   - Premere #8000 per trasferire la chiamata per l'audit.

## Risorse avanzate

Il sistema di code di Asterisk offre alcune funzionalità avanzate per dare priorità a determinati clienti e agenti, oltre a consentire un menu utente.

### Menu utente

È possibile definire un menu per un utente in attesa nella coda usando estensioni a una cifra. Per abilitare questa opzione, definire un contesto nella configurazione della coda `queues.conf`.

### Penalty

Gli agenti possono essere configurati con una penalità. Una coda invierà le chiamate prima agli utenti con valori di penalità più bassi. Ad esempio, poiché sappiamo che i nostri clienti adorano Susan e la sua voce dolce, potremmo assegnarle priorità 0. In alternativa, l'agente chiamato Uber, che ha meno esperienza, è meno preferito per il servizio clienti; pertanto, assegniamo a questo agente priorità 10. Nel file `queues.conf`:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority

Le code operano in modalità FIFO (first in first out). Se si desidera dare priorità a clienti speciali (platinum, gold) è possibile impostare priorità differenziate. Per clienti platinum o gold:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Clienti blue:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

The application `agentcallbacklogin()` was deprecated by Digium in Asterisk 1.4 (July 2006) and is no longer available in Asterisk 22. The recommended approach is to use `AddQueueMember()` with a PJSIP interface to dynamically add callback-style members to a queue. The document `queues-with-callback-members.txt` was included in older Asterisk `/doc` directories for migration guidance.

The old `chan_agent` channel driver was likewise removed; its functionality was rewritten as the `app_agent_pool` module, which is what provides `AgentLogin()`, `AgentRequest()` and the `AGENT()` dialplan function in Asterisk 22 (these are still present — `app_agent_pool.so` ships with a stock 22 build). For modern call centers, however, the standard pattern is to skip agent channels entirely and add the agent's PJSIP device directly to the queue with `AddQueueMember()`/`RemoveQueueMember()` (statically in `queues.conf`, or dynamically from the dialplan or AMI). This is simpler, integrates cleanly with PJSIP device state, and is the approach used throughout this chapter.

## Queue statistics

All events from queues are logged to /var/log/asterisk/queue_log. The format of the queue log is published in the document queuelog.txt in the /doc directory of the Asterisk documentation. Below are some of the most important events logged.

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

You can build your own utility to process these events or use a ready-to-run statistics package:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – a commercial, actively maintained package that parses `queue_log` and remains one of the most complete reporting tools for Asterisk call centers.
- **Roll your own** – because the `queue_log` format above is stable and well documented, it is straightforward to parse it with a small script (Python, etc.) and feed the events into a database or dashboard.

For a more event-driven approach than tailing `queue_log`, the **Asterisk REST Interface (ARI)** and the **AMI** `QueueSummary`/`QueueStatus` actions let you build live queue dashboards and custom integrations against real-time queue state rather than after-the-fact log parsing. ARI is the modern, supported integration surface for this kind of work in Asterisk 22.

## Riepilogo

In questo capitolo hai imparato come utilizzare un ACD, la sua architettura e come configurarlo. Sono state presentate anche alcune funzionalità avanzate come le priorità e le penalità.

## Quiz

1. Quali delle seguenti sono strategie di distribuzione della coda valide in `queues.conf` (scegli tutte le risposte corrette)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. È possibile registrare una conversazione tra un agente e un cliente dalla coda impostando l'opzione ___ nel file `queues.conf`.
3. Quale `strategy` chiama i membri nell'ordine esatto in cui sono elencati in `queues.conf`?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. Quando l'agente termina una chiamata nell'esempio di telemarketing, quali azioni può compiere (scegli tutte le risposte corrette)?
   - A. Premere `*` per disconnettersi e rimanere nella coda
   - B. Riagganciare il telefono e disconnettersi dalla coda
   - C. Premere `#8000` per trasferire la chiamata per l'audit
   - D. Premere `#` per disconnettersi da tutte le code immediatamente
5. Quali due compiti sono *necessari* per ottenere una coda funzionante (scegli tutte le risposte corrette)?
   - A. Creare la coda
   - B. Creare gli agenti
   - C. Configurare i parametri dell'agente
   - D. Configurare la registrazione
   - E. Inserire la coda nel dialplan
6. In una coda di chiamata è possibile offrire un menu a un solo tasto che il chiamante può digitare mentre attende. Questo è abilitato definendo un ___ nella sezione `queues.conf` della coda:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. Le applicazioni di supporto `AddQueueMember()` e `RemoveQueueMember()` sono usate nel ___ per aggiungere o rimuovere membri a runtime:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Poiché chan_sip è stato rimosso in Asterisk 21, un membro statico della coda deve fare riferimento a un canale come ___ piuttosto che a `SIP/1001`.
9. Il parametro `wrapuptime` è il tempo minimo dopo che un agente ha disconnesso una chiamata prima che la coda gli invii una nuova chiamata.
   - A. True
   - B. False
10. Un chiamante può ottenere una posizione più alta nella stessa coda impostando la variabile di canale `QUEUE_PRIO` prima di chiamare `Queue()`.
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin non è una strategia documentata; in Asterisk 22 è presente solo come alias deprecato per rrmemory) · 2 — `monitor-format` (la registrazione dalla coda è abilitata specificando `monitor-format`; in Asterisk 22 `monitor-type` supporta solo MixMonitor) · 3 — C (linear) · 4 — A, B, C (`*` disconnette e rimane; `#` non è un tasto di log‑off‑all) · 5 — A, E · 6 — C (l'opzione `context`) · 7 — A (il dial plan) · 8 — `PJSIP/1001` (qualsiasi interfaccia `PJSIP/`) · 9 — True · 10 — True
