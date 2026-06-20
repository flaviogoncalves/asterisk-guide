# Anrufwarteschlangen

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Verstehen, warum und wie Anrufwarteschlangen verwendet werden
- Die Grundtheorie von Anrufwarteschlangen verstehen
- Das Warteschlangensystem installieren und konfigurieren

## Wie funktionieren Warteschlangen?

Call queues sind nicht gerade eine Neuheit. Wenn Sie einen hohen eingehenden Anrufverkehr haben, ist es schwierig, Anrufe angemessen zu verteilen. Eine Gruppenstrategie, bei der das Telefon gleichzeitig bei allen Agenten klingelt, scheint nicht zu funktionieren, es sei denn, Sie haben nur wenige Agenten. Eine Call Queue liefert jedoch jedes Mal nur einen einzelnen verfügbaren Agenten den Anruf und legt den Kunden bei fehlenden Agenten in die Warteschleife mit Musik. Die Warteschlange funktioniert, indem sie den Anruf behält, während ein freier Agent gesucht wird, der den Anruf annimmt. Einer der größten Vorteile der Queue ist, dass Anrufe nicht verloren gehen und gleichzeitig die Möglichkeit besteht, Statistiken zu erzeugen.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

In der Regel funktioniert eine Call Queue so:

- Agenten melden sich bei der Queue an.
- Eingehende Anrufe werden in die Warteschlange gestellt.
- Eine Warteschlangen‑Strategie zur Verteilung der Anrufe wird verwendet, um Anrufe zu den Agenten zu senden.
- Musik in der Warteschleife wird abgespielt, während der Anrufer wartet.
- Durchsagen können an die Anrufer gesendet werden, um sie über die Wartezeit zu informieren
- Der Anruf wird vom Agenten beantwortet und Statistiken werden erstellt.

Die Hauptanwendung für Queues ist der Kundenservice. Durch den Einsatz von Queues vermeiden Sie den Verlust von Anrufen, wenn Ihre Agenten beschäftigt sind. Sie können neue Agenten zur Queue hinzufügen, wenn Sie feststellen, dass die Zahl der Anrufer in der Warteschlange steigt. Ein weiterer Vorteil von Queues ist, dass Sie nun Statistiken wie Abbruchrate, durchschnittliche Gesprächsdauer und Ziel für die Anrufbeantwortung erhalten. Diese Statistiken helfen Ihnen zu bestimmen, wie viele Agenten Sie einsetzen müssen, um Ihren Kunden einen besseren Service zu bieten.

### ACD‑Architektur

Die ACD‑Architektur besteht aus Queues und Agenten. Ein Agent kann gleichzeitig in zwei Queues sein. Eine Queue kann Agenten, Channels und Agentengruppen enthalten.

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Queues are defined in the queues.conf configuration file. Agents are attendants who log in and are members of queues. Agents are defined in the agents.conf file. The queue system has grown significantly over many releases, making the configuration file extensive. We will explain some of the major parameters. One general parameter worth highlighting is `autofill`:

```
autofill=yes
```

The old behavior for the queue was serial type. The queue waited for a call to be dispatched before sending the succeeding call to the next agent. If an agent takes 15 seconds to answer a call, the other calls in the queue had to wait until that call was answered. For high-volume queues, this behavior was inefficient. The new behavior autofill=yes does not wait until a call is answered, but rather works in parallel. You can record the calls in the queue using the option mixmonitor. In this mode, calls are recorded and mixed at the same time.

### Queue configuration file

Queues are configured in the queues.conf file. In the figure, you will find a working example of a queue.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

You can configure your agents in the file agents.conf. Agents can log in from any extension to receive calls. You can dial an agent using:

```
Dial(agent/<name>)
```

#### Agent login

The login flow for Agent 300 works like this:

- The user dials an extension that runs the `AgentLogin()` application.
- `AgentLogin()` is executed and the agent is associated with the current channel.
- You can check the status of the agents using the command `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

You can define the agents in the file agents.conf

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

Members are active channels responding to the queue. Members can be direct channels (PJSIP, DAHDI) or agents who log in before receiving calls.

### Strategies

Calls are distributed among members according to one of these strategies:

- ringall: Plays all channels available until someone answers.
- leastrecent: Distributes to the least recent member.
- fewestcalls: Distributes to the member with fewest calls.
- random: Ring random interface.
- wrandom: Ring random interface, but use the member’s penalty as a weight when calculating their metric.
- rrmemory: Uses round robin with memory; it remembers where it left off with the call in the last pass.
- rrordered: Same as rrmemory, except the queue member order from the config file is preserved.
- linear: Rings members in the order they are listed in queues.conf; for dynamic members, in the order they were added.

The older `roundrobin` strategy was deprecated back in Asterisk 1.4. It is no longer a documented strategy and should not be used: in Asterisk 22 the parser still accepts the word `roundrobin`, but only as a backward-compatibility alias that maps to `rrmemory`. Use `rrmemory` (or `rrordered`) explicitly instead. The list above is the set of documented strategies for the `strategy` option in the Asterisk 22 `queues.conf`.

## Agents

Agents werden als Proxy‑Kanäle implementiert. Sie können innerhalb von Queues verwendet werden. Ein weiterer Verwendungszweck für die Agent‑Kanäle ist Extension Mobility. Der Benutzer kann sich an jedem Telefon anmelden und dessen Anrufe entgegennehmen. Das ermöglicht es einem Benutzer, in jeden Raum zu gehen und ihn zu einem Büro zu machen. Man kann einen Agenten im Dialplan mit dial(agent/<name>) anrufen. Agenten werden in der Datei agents.conf definiert.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

Sie können Agent‑Gruppen verwenden. Diese Funktion berücksichtigt keine ACD‑Strategien. Wahrscheinlich listen Sie lieber alle Agenten einzeln auf. Wenn Sie zu einer Agent‑Gruppe weiterleiten möchten, können Sie `queues.conf` verwenden:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Agents werden in der Datei agents.conf definiert. Nachfolgend ein funktionierendes Beispiel der Datei.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## ACD-bezogene Anwendungen

Das Asterisk-Warteschlangensystem stellt mehrere Anwendungen zur Verfügung, um die Warteschlangen im Dialplan zu implementieren. Im Folgenden zeigen wir einige davon.

### Die Anwendung queue()

Diese Anwendung legt eingehende Anrufe in eine bestimmte Anrufwarteschlange, wie in queues.conf definiert, ein. Die Optionszeichenkette kann null oder mehr einbuchstabige Optionen enthalten (siehe Abbildung unten). Zusätzlich zum Weiterleiten des Anrufs kann ein Anruf geparkt und anschließend von einem anderen Benutzer abgeholt werden. Die optionale URL wird an die angerufene Partei gesendet, wenn der Kanal dies unterstützt. Der optionale AGI‑Parameter richtet ein AGI‑Skript ein, das auf dem Kanal der anrufenden Partei ausgeführt wird, sobald sie mit einem Warteschlangenmitglied verbunden ist. Der Timeout führt dazu, dass die Warteschlange nach einer angegebenen Anzahl von Sekunden fehlschlägt, geprüft zwischen jedem Timeout‑ und Wiederholungszyklus. Diese Anwendung setzt die STATUS‑Variable QUEUE bei Abschluss:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### Die Anwendung agentlogin()

Diese Anwendung fordert den Agenten auf, sich im System anzumelden. Sie gibt immer -1 zurück. Während der Anmeldung hört der Agent, der Anrufe entgegennimmt, einen Signalton, wenn ein neuer Anruf eingeht. Der Agent kann den Anruf durch Drücken der *‑Taste auflegen.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### Die Anwendung addQueueMember()

Diese Anwendung fügt einem Queue dynamisch ein Gerät hinzu (z. B. PJSIP/3000). Existiert das Gerät bereits, wird ein Fehler zurückgegeben.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### Die Anwendung removeQueueMember()

Diese Anwendung entfernt ein Gerät dynamisch aus der Warteschlange. Gehört das Gerät nicht zur Warteschlange, wird ein Fehler zurückgegeben.

```
RemoveQueueMember(queuename[|interface])
```

### Unterstützende Anwendungen und CLI‑Befehle

Einige Anwendungen und Konsolenbefehle können bei der Arbeit mit Warteschlangen helfen. Das Folgende gibt einen Überblick darüber, was jede Anwendung tut:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

The figure below summarizes the major tasks to create a working queue system.

![Die ACD-Konfigurationsaufgaben: (1) Anlegen der Anrufwarteschlange (erforderlich), (2) Definieren von Agentenparametern (optional), (3) Anlegen von Agenten (optional), (4) Einbinden der Warteschlange in den Dialplan (erforderlich), (5) Konfigurieren der Agentenaufnahme (optional) und (6) Verifizieren mit „agent show all“ und „queue show“ (optional)](../images/14-queues-fig10.png)

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

## Warteschlangenbetrieb

Die folgenden Beispiele erklären, wie man die Warteschlange verwendet.

1. Agent-Anmeldung. Beispiel: Ein Agent in der Telemarketing-Warteschlange nimmt den Hörer ab und wählt #9000. Der Agent hört eine ungültige Anmeldemeldung und wird nach seinem/ihrem Namen und Passwort gefragt. Die Prüfungswarteschlange folgt dem gleichen Verfahren.
2. Warteschlange. Sobald er in der Warteschlange ist, hört der Agent MOH, falls definiert. Wenn ein Anruf in die Telemarketing-Warteschlange kommt, hört der Agent einen Piepton und wird mit diesem Anruf verbunden.
3. Anruf beenden. Wenn der Agent den Anruf beendet, kann er/sie:
   - ‘*’ drücken, um die Verbindung zu trennen und in der Warteschlange zu bleiben.
   - Das Telefon auflegen, wodurch die Verbindung zur Warteschlange getrennt wird.
   - #8000 drücken, um den Anruf zur Prüfung zu übertragen.

## Advanced resources

Das Asterisk-Warteschlangensystem verfügt über einige erweiterte Funktionen, um bestimmte Kunden und Agenten zu priorisieren sowie ein Benutzermenü zu aktivieren.

### User menu

Sie können ein Menü für einen Benutzer definieren, während er in der Warteschlange wartet, indem Sie einstellige Nebenstellen verwenden. Um diese Option zu aktivieren, definieren Sie einen Kontext in der Warteschlangen‑Konfiguration `queues.conf`.

### Penalty

Agenten können mit einer Penalty konfiguriert werden. Eine Warteschlange sendet die Anrufe zuerst an Benutzer mit niedrigeren Penalty‑Werten. Da wir zum Beispiel wissen, dass unsere Kunden Susan und ihre sanfte Stimme lieben, können wir ihr die Priorität 0 zuweisen. Alternativ wird dem Agenten namens Uber, der weniger Erfahrung hat, eine geringere Präferenz für den Kundendienst eingeräumt; daher weisen wir diesem Agenten die Priorität 10 zu. In der Datei `queues.conf`:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority

Warteschlangen arbeiten im FIFO‑Modus (first in first out). Wenn Sie bestimmten Kunden (Platin, Gold) Vorrang geben möchten, können Sie differenzierte Prioritäten einrichten. Für Platin‑ oder Gold‑Kunden:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Blaue Kunden:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## Die Anwendung agentcallbacklogin() wurde entfernt

Die Anwendung `agentcallbacklogin()` wurde von Digium in Asterisk 1.4 (Juli 2006) veraltet erklärt und ist in Asterisk 22 nicht mehr verfügbar. Der empfohlene Ansatz ist die Verwendung von `AddQueueMember()` mit einer PJSIP‑Schnittstelle, um callback‑artige Mitglieder dynamisch zu einer Warteschlange hinzuzufügen. Das Dokument `queues-with-callback-members.txt` war in älteren Asterisk `/doc`‑Verzeichnissen für Migrationshinweise enthalten.

Der alte `chan_agent`‑Kanaltreiber wurde ebenfalls entfernt; seine Funktionalität wurde als das `app_agent_pool`‑Modul neu implementiert, das `AgentLogin()`, `AgentRequest()` und die `AGENT()`‑Dialplan‑Funktion in Asterisk 22 bereitstellt (diese sind weiterhin vorhanden — `app_agent_pool.so` wird mit einem Standard‑22‑Build ausgeliefert). Für moderne Call‑Center ist jedoch das gängige Muster, Agent‑Kanäle vollständig zu überspringen und das PJSIP‑Gerät des Agenten direkt mit `AddQueueMember()`/`RemoveQueueMember()` zur Warteschlange hinzuzufügen (statisch in `queues.conf` oder dynamisch aus dem Dialplan oder AMI). Das ist einfacher, integriert sich sauber in den PJSIP‑Gerätestatus und ist das im gesamten Kapitel verwendete Vorgehen.

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

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, wie man ein ACD verwendet, seine Architektur und wie man es konfiguriert. Einige erweiterte Funktionen wie Prioritäten und Strafpunkte wurden ebenfalls vorgestellt.

## Quiz

1. Welche der folgenden sind gültige Queue‑Verteilungsstrategien in `queues.conf` (alle zutreffenden auswählen)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. Sie können ein Gespräch zwischen einem Agenten und einem Kunden innerhalb der Queue aufzeichnen, indem Sie die ___‑Option in der `queues.conf`‑Datei setzen.
3. Welche `strategy` ruft Mitglieder in exakt der Reihenfolge an, in der sie in `queues.conf` aufgeführt sind?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. Wenn der Agent im Telemarketing‑Beispiel einen Anruf beendet, welche Aktionen kann er ausführen (alle zutreffenden auswählen)?
   - A. Drücken Sie `*`, um die Verbindung zu trennen und in der Queue zu bleiben
   - B. Legen Sie auf und trennen Sie die Verbindung zur Queue
   - C. Drücken Sie `#8000`, um den Anruf zur Prüfung zu übertragen
   - D. Drücken Sie `#`, um sich sofort von allen Queues abzumelden
5. Welche beiden Aufgaben sind *erforderlich*, um eine funktionierende Queue zu erhalten (alle zutreffenden auswählen)?
   - A. Die Queue erstellen
   - B. Die Agenten erstellen
   - C. Agenten‑Parameter konfigurieren
   - D. Aufnahme konfigurieren
   - E. Die Queue in den Dialplan einbinden
6. In einer Call‑Queue können Sie ein einstellungs‑menü mit einer einzigen Ziffer anbieten, das der Anrufer während des Wartens wählen kann. Dies wird aktiviert, indem ein(e) ___ im `queues.conf`‑Abschnitt der Queue definiert wird:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. Die Support‑Anwendungen `AddQueueMember()` und `RemoveQueueMember()` werden im ___ verwendet, um Mitglieder zur Laufzeit hinzuzufügen oder zu entfernen:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Da chan_sip in Asterisk 21 entfernt wurde, muss ein statisches Queue‑Mitglied einen Kanal wie ___ referenzieren statt `SIP/1001`.
9. Der Parameter `wrapuptime` ist die minimale Zeit, die nach dem Trennen eines Anrufs durch einen Agenten vergehen muss, bevor die Queue diesem Agenten einen neuen Anruf sendet.
   - A. True
   - B. False
10. Ein Anrufer kann in derselben Queue eine höhere Position erhalten, indem die Kanal‑Variable `QUEUE_PRIO` vor dem Aufruf von `Queue()` gesetzt wird.
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin ist keine dokumentierte Strategie; in Asterisk 22 existiert sie nur noch als veralteter Alias für rrmemory) · 2 — `monitor-format` (Aufzeichnung aus der Queue wird aktiviert, indem `monitor-format` angegeben wird; in Asterisk 22 unterstützt `monitor-type` nur MixMonitor) · 3 — C (linear) · 4 — A, B, C (`*` trennt und bleibt; `#` ist keine Log‑off‑All‑Taste) · 5 — A, E · 6 — C (die `context`‑Option) · 7 — A (der dial plan) · 8 — `PJSIP/1001` (beliebige `PJSIP/`‑Schnittstelle) · 9 — True · 10 — True
