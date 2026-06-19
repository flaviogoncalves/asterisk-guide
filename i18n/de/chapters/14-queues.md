# Call Queues

Call Queues, auch bekannt als ACD (Automatic Call Distribution), werden immer wichtiger, um Kundenanrufe effizient zu beantworten. Ein automatischer Anrufverteiler kann dazu beitragen, Kosten zu senken, den Service zu verbessern und den Umsatz zu steigern, da Anrufverteiler die Arbeitsweise Ihres Unternehmens beeinflussen – nicht nur für ein paar Tage, sondern für viele Jahre. In einer Call-Center-Umgebung ist der wichtigste Faktor der Mensch; er ist die teuerste Ressource. Es kostet Zeit, Geld und Geduld, Agenten einzustellen, zu schulen und zu motivieren. Mit einer ACD können Sie die Produktivität der Agenten maximieren, indem Sie die erforderliche Anzahl an Agenten präzise dimensionieren, gute und schlechte Mitarbeiter steuern und den Anruffluss analysieren.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Zu verstehen, warum und wie Call Queues eingesetzt werden
- Die grundlegende Theorie von Call Queues zu verstehen
- Das Queue-System zu installieren und zu konfigurieren

## Wie funktionieren Queues?

Call Queues sind keine wirkliche Neuheit. Wenn Sie ein hohes Anrufaufkommen haben, ist es schwierig, Anrufe angemessen zu verteilen. Die Verwendung einer Gruppenstrategie, bei der das Telefon bei allen Agenten gleichzeitig klingelt, scheint nicht zu funktionieren, es sei denn, Sie haben nur wenige Agenten. Eine Call Queue hingegen leitet Anrufe jeweils nur an einen einzelnen verfügbaren Agenten weiter und versetzt den Kunden in die Warteschleife mit Musik, wenn keine Agenten verfügbar sind. Die Queue funktioniert, indem sie den Anruf hält, während sie einen unbesetzten Agenten sucht, der den Anruf entgegennimmt. Einer der größten Vorteile der Queue besteht darin, Anrufverluste zu vermeiden und gleichzeitig die Möglichkeit zu bieten, Statistiken zu erstellen.

![Eine Call Queue: Eingehende 1-800-Anrufe gelangen in die Queue und eine ACD-Strategie (ringall, rrmemory, leastrecent, priority und andere) verteilt sie an die verfügbaren Agenten](../images/14-queues-fig01.png)

Normalerweise funktioniert eine Call Queue wie folgt:

- Agenten melden sich in der Queue an.
- Eingehende Anrufe werden in die Warteschlange eingereiht.
- Eine Warteschlangenstrategie zur Verteilung der Anrufe wird verwendet, um Anrufe an Agenten zu senden.
- Während der Anrufer wartet, wird Warteschleifenmusik (Music on Hold) abgespielt.
- Anrufern können Ansagen gemacht werden, die sie über die Wartezeit informieren.
- Der Anruf wird vom Agenten entgegengenommen und Statistiken werden erstellt.

Die Hauptanwendung für Queues ist der Kundenservice. Durch die Verwendung von Queues vermeiden Sie Anrufverluste, wenn Ihre Agenten beschäftigt sind. Sie können der Queue neue Agenten hinzufügen, wenn Sie feststellen, dass die Anzahl der Anrufer in der Queue wächst. Ein weiterer Vorteil von Queues ist, dass Sie nun Statistiken wie die Abbruchrate, die durchschnittliche Anrufdauer und das Anrufannahmeziel erhalten können. Diese Statistiken helfen Ihnen zu bestimmen, wie viele Agenten Sie einsetzen müssen, um Ihren Kunden einen besseren Service zu bieten.

### ACD-Architektur

Die ACD-Architektur besteht aus Queues und Agenten. Ein Agent kann gleichzeitig in zwei Queues sein. Eine Queue kann Agenten, Kanäle und Agentengruppen haben.

![ACD-Architektur: Jede Queue (Kundenservice, Inside Sales) wird von einer Telefonnummer gespeist und leitet Anrufe an Agenten weiter, die wiederum an physische Kanäle gebunden sind](../images/14-queues-fig02.png)

## Queues

Queues werden in der Konfigurationsdatei queues.conf definiert. Agenten sind Mitarbeiter, die sich anmelden und Mitglieder von Queues sind. Agenten werden in der Datei agents.conf definiert. Das Queue-System ist über viele Releases hinweg erheblich gewachsen, was die Konfigurationsdatei umfangreich macht. Wir werden einige der wichtigsten Parameter erläutern. Allgemeine Parameter

```
autofill=yes
```

Das alte Verhalten der Queue war vom Typ seriell. Die Queue wartete darauf, dass ein Anruf zugestellt wurde, bevor der nachfolgende Anruf an den nächsten Agenten gesendet wurde. Wenn ein Agent 15 Sekunden brauchte, um einen Anruf anzunehmen, mussten die anderen Anrufe in der Queue warten, bis dieser Anruf beantwortet war. Bei Queues mit hohem Volumen war dieses Verhalten ineffizient. Das neue Verhalten autofill=yes wartet nicht, bis ein Anruf beantwortet wurde, sondern arbeitet parallel. Sie können die Anrufe in der Queue mit der Option mixmonitor aufzeichnen. In diesem Modus werden Anrufe gleichzeitig aufgezeichnet und gemischt.

### Queue-Konfigurationsdatei

Queues werden in der Datei queues.conf konfiguriert. In der Abbildung finden Sie ein funktionierendes Beispiel einer Queue.

![Ein funktionierendes Beispiel der Datei queues.conf, das den allgemeinen Abschnitt und eine customerservice-Queue mit Strategie, Service-Level, Ansagen, Aufzeichnung und Mitgliedern zeigt](../images/14-queues-fig03.png)

### Agenten

Sie können Ihre Agenten in der Datei agents.conf konfigurieren. Agenten können sich von jeder Extension aus anmelden, um Anrufe entgegenzunehmen. Sie können einen Agenten anrufen mit:

```
Dial(agent/<name>)
```

#### Agenten

Agent 300

- Sie können den Status der Agenten mit dem Befehl `agent show all` überprüfen.
- Der Befehl agentlogin wird ausgeführt und der Agent wird mit dem aktuellen Kanal verknüpft.
- Der Benutzer wählt eine Extension mit der Anwendung agentlogin.

![Agenten: Ein Benutzer meldet sich an, indem er eine Extension wählt, die die Anwendung agentlogin ausführt, welche Agent 300 an den aktuellen Kanal bindet; Sie können den Agentenstatus mit `agent show all` überprüfen](../images/14-queues-fig04.png)

Sie können die Agenten in der Datei agents.conf definieren

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

### Mitglieder

Mitglieder sind aktive Kanäle, die auf die Queue reagieren. Mitglieder können direkte Kanäle (PJSIP, DAHDI) oder Agenten sein, die sich anmelden, bevor sie Anrufe erhalten.


### Strategien

Anrufe werden gemäß einer dieser Strategien unter den Mitgliedern verteilt:

- ringall: Lässt alle verfügbaren Kanäle klingeln, bis jemand abhebt.
- leastrecent: Verteilt an das Mitglied, das am längsten keinen Anruf erhalten hat.
- fewestcalls: Verteilt an das Mitglied mit den wenigsten Anrufen.
- random: Lässt eine zufällige Schnittstelle klingeln.
- wrandom: Lässt eine zufällige Schnittstelle klingeln, verwendet aber die Penalty des Mitglieds als Gewichtung bei der Berechnung der Metrik.
- rrmemory: Verwendet Round Robin mit Speicher; es merkt sich, wo es beim letzten Durchgang mit dem Anruf aufgehört hat.
- rrordered: Wie rrmemory, außer dass die Reihenfolge der Queue-Mitglieder aus der Konfigurationsdatei beibehalten wird.
- linear: Lässt Mitglieder in der Reihenfolge klingeln, in der sie in queues.conf aufgelistet sind; bei dynamischen Mitgliedern in der Reihenfolge, in der sie hinzugefügt wurden.

Die ältere Strategie `roundrobin` wurde bereits in Asterisk 1.4 als veraltet markiert und entfernt; sie existiert in Asterisk 22 nicht mehr. Verwenden Sie stattdessen `rrmemory` (oder `rrordered`). Die oben genannten Strategien sind der vollständige Satz, der von der Option `strategy` in der Asterisk 22 `queues.conf` akzeptiert wird.

## Agenten

Agenten werden als Proxy-Kanäle implementiert. Sie können innerhalb der Queues verwendet werden. Eine weitere Verwendung der Agentenkanäle ist die Extension-Mobilität. Der Benutzer kann sich mit jedem Telefon anmelden und seine Anrufe empfangen. Dies ermöglicht es einem Benutzer, in jeden Raum zu gehen und ihn zu seinem Büro zu machen. Sie können einen Agenten im Dialplan mit dial(agent/<name>) anrufen. Sie definieren Agenten in der Datei agents.conf.

![Agenten-Mobilität: Der Benutzer nimmt ein beliebiges Telefon ab, wählt eine Anmelde-Extension und gibt Agentennummer und Passwort ein; nachdem agentlogin() erfolgreich war, ist der Agent (Agent 300) bereit, Anrufe entgegenzunehmen, und Sie können den Status mit dem CLI-Befehl `agent show all` überprüfen](../images/14-queues-fig05.png)

### Agentengruppen

Sie können sich für die Verwendung von Agentengruppen entscheiden. Diese Funktion berücksichtigt keine ACD-Strategien. Sie werden es wahrscheinlich vorziehen, alle Agenten einzeln aufzulisten. Wenn Sie an eine Agentengruppe weiterleiten möchten,

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### Die Konfigurationsdatei für Agenten

Agenten werden in der Datei agents.conf definiert. Unten ist ein funktionierendes Beispiel der Datei.

![Ein funktionierendes Beispiel der Datei agents.conf: ein allgemeiner Abschnitt mit persistentagents, ein Agenten-Abschnitt mit den Standardparametern (autologoff, ackcall, endcall, wrapuptime, musiconhold) und zwei Agentendefinitionen (300 und 301)](../images/14-queues-fig06.png)

## ACD-bezogene Anwendungen

Das Asterisk-Queue-System stellt mehrere Anwendungen zur Verfügung, um die Queues im Dialplan zu implementieren. Nachfolgend zeigen wir einige davon.

### Die Anwendung queue()

Diese Anwendung reiht eingehende Anrufe in eine bestimmte Call Queue ein, wie in queues.conf definiert. Die Optionszeichenfolge kann null oder mehr der folgenden Zeichen enthalten: Zusätzlich zur Weiterleitung des Anrufs kann ein Anruf geparkt und dann von einem anderen Benutzer abgeholt werden. Die optionale URL wird an den angerufenen Teilnehmer gesendet, wenn der Kanal dies unterstützt. Der optionale AGI-Parameter richtet ein AGI-Skript ein, das auf dem Kanal des anrufenden Teilnehmers ausgeführt wird, sobald dieser mit einem Queue-Mitglied verbunden ist. Das Timeout führt dazu, dass die Queue nach einer festgelegten Anzahl von Sekunden abbricht, geprüft zwischen jedem Timeout- und Wiederholungszyklus. Diese Anwendung setzt nach Abschluss die Statusvariable QUEUE:

![Die Anwendung queue(): ihre Syntax `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` und die verfügbaren einbuchstabigen Optionen (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### Die Anwendung agentlogin()

Diese Anwendung fordert den Agenten auf, sich am System anzumelden. Sie gibt immer -1 zurück. Während der Anmeldung hört der Agent, der Anrufe empfängt, einen Piepton, wenn ein neuer Anruf eingeht. Der Agent kann den Anruf abwerfen, indem er die Taste * drückt.

![Die Anwendung agentlogin(): ihre Syntax `AgentLogin([AgentNo][|options])` und die Option `s` für eine stille Anmeldung, die die Anmeldebestätigung nicht ankündigt](../images/14-queues-fig08.png)

### Die Anwendung addQueueMember()

Diese Anwendung fügt einer Queue dynamisch ein Gerät (z. B. PJSIP/3000) hinzu. Wenn das Gerät bereits existiert, gibt sie einen Fehler zurück.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### Die Anwendung removeQueueMember()

Diese Anwendung entfernt ein Gerät dynamisch aus der Queue. Wenn das Gerät nicht zur Queue gehört, gibt sie einen Fehler zurück.

```
RemoveQueueMember(queuename[|interface])
```

### Unterstützende Anwendungen und CLI-Befehle

Einige Anwendungen und Konsolenbefehle können bei der Arbeit mit Queues helfen. Das Folgende skizziert, was jede Anwendung tut:

![Unterstützende Anwendungen (AddQueueMember, RemoveQueueMember) und CLI-Befehle (agent show all, queue show, queue show <name>), die zur Verwaltung von Queues zur Laufzeit verwendet werden](../images/14-queues-fig09.png)

## Konfigurationsaufgaben

Die folgende Abbildung fasst die wichtigsten Aufgaben zur Erstellung eines funktionierenden Queue-Systems zusammen.

![Die ACD-Konfigurationsaufgaben: (1) Call Queue erstellen (erforderlich), (2) Agentenparameter definieren (optional), (3) Agenten erstellen (optional), (4) Queue in den Dialplan einfügen (erforderlich) und (5) mit agent show all und queue show überprüfen (optional)](../images/14-queues-fig10.png)

Schritt 1: Call Queue erstellen In der Datei queues.conf:

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

Schritt 2: Agentenparameter definieren In der Datei agents.conf:

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

Schritt 3: Agenten erstellen In der Datei agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Schritt 4: Queue in den Dialplan einfügen

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

### Queue-Aufzeichnung konfigurieren

Anrufe können mit der Asterisk-Anwendung MixMonitor aufgezeichnet werden. (Die eigenständige Anwendung Monitor wurde in Asterisk 22 entfernt, und die Option `monitor-type` in queues.conf akzeptiert jetzt nur noch MixMonitor.) Die Aufzeichnung kann innerhalb der Queue-Anwendung aktiviert werden und beginnt, sobald der Anruf tatsächlich entgegengenommen wird. Nur erfolgreiche Anrufe werden aufgezeichnet, und während der Warteschleifenmusik finden keine Aufzeichnungen statt. Um die Überwachung zu aktivieren, geben Sie einfach monitor-format an. Diese Funktion ist ansonsten deaktiviert. Sie können den Dateinamen für die Aufzeichnung mit Set(MONITOR_FILENAME=<filename>) festlegen; andernfalls

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

In der Datei queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Queue-Betrieb

Die folgenden Beispiele erklären, wie die Queue verwendet wird. Schritt 1: Agenten-Anmeldung Beispiel: Ein Agent in der Telemarketing-Queue nimmt das Telefon ab und wählt #9000. Der Agent hört eine Nachricht über eine ungültige Anmeldung und wird nach seinem Namen und Passwort gefragt. Die Audit-Queue folgt dem gleichen Verfahren. Schritt 2: Queue Sobald der Agent in der Queue ist, hört er MOH, falls definiert. Wenn ein Anruf in der Telemarketing-Queue eingeht, hört der Agent einen Piepton und wird mit diesem Anruf verbunden. Schritt 3: Anrufende Wenn der Agent den Anruf beendet, kann er/sie:

- ‘*’ drücken, um die Verbindung zu trennen und in der Queue zu bleiben.
- Das Telefon auflegen und sich dadurch von der Queue trennen.
- #8000 drücken, um den Anruf zur Prüfung weiterzuleiten.

## Erweiterte Ressourcen

Das Asterisk-Queue-System verfügt über einige erweiterte Funktionen, um bestimmte Kunden und Agenten zu priorisieren sowie ein Benutzermenü zu ermöglichen.

### Benutzermenü

Sie können ein Menü für einen Benutzer definieren, während er in der Queue wartet, indem Sie einstellige Extensions verwenden. Um diese Option zu aktivieren, definieren Sie einen context in der Queue-Konfiguration queues.conf.

### Penalty

Agenten können mit einer Penalty konfiguriert werden. Eine Queue sendet die Anrufe zuerst an Benutzer mit niedrigeren Penalty-Werten. Da wir zum Beispiel wissen, dass unsere Kunden Susan und ihre sanfte Stimme lieben, könnten wir ihr die Priorität 0 zuweisen. Alternativ ist der Agent namens Uber, der weniger Erfahrung hat, für den Kundenservice weniger bevorzugt; daher weisen wir diesem Agenten die Priorität 10 zu. In der Datei queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priorität

Queues arbeiten im FIFO-Modus (First In, First Out). Wenn Sie speziellen Kunden (Platin, Gold) Priorität einräumen möchten, können Sie differenzierte Prioritäten einrichten. Für Platin- oder Gold-Kunden:

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

Die Anwendung `agentcallbacklogin()` wurde von Digium in Asterisk 1.4 (Juli 2006) als veraltet markiert und ist in Asterisk 22 nicht mehr verfügbar. Der empfohlene Ansatz ist die Verwendung von `AddQueueMember()` mit einer PJSIP-Schnittstelle, um dynamisch Mitglieder im Callback-Stil zu einer Queue hinzuzufügen. Das Dokument `queues-with-callback-members.txt` war in älteren Asterisk-Verzeichnissen `/doc` für Migrationsanleitungen enthalten.

Der alte Kanal-Treiber `chan_agent` wurde ebenfalls entfernt; seine Funktionalität wurde als Modul `app_agent_pool` neu geschrieben, welches in Asterisk 22 `AgentLogin()`, `AgentRequest()` und die Dialplan-Funktion `AGENT()` bereitstellt (diese sind weiterhin vorhanden – `app_agent_pool.so` wird mit einem Standard-Build 22 ausgeliefert). Für moderne Call-Center ist es jedoch das Standardmuster, Agentenkanäle komplett zu überspringen und das PJSIP-Gerät des Agenten direkt mit `AddQueueMember()`/`RemoveQueueMember()` zur Queue hinzuzufügen (statisch in `queues.conf` oder dynamisch über den Dialplan oder AMI). Dies ist einfacher, lässt sich sauber in den PJSIP-Gerätestatus integrieren und ist der Ansatz, der in diesem Kapitel durchgehend verwendet wird.

## Queue-Statistiken

Alle Ereignisse aus Queues werden in /var/log/asterisk/queue_log protokolliert. Das Format des Queue-Logs ist im Dokument queuelog.txt im Verzeichnis /doc der Asterisk-Dokumentation veröffentlicht. Nachfolgend sind einige der wichtigsten protokollierten Ereignisse aufgeführt.

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

Sie können Ihr eigenes Dienstprogramm zur Verarbeitung dieser Ereignisse erstellen oder ein fertiges Statistikpaket verwenden:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – ein kommerzielles, aktiv gepflegtes Paket, das `queue_log` analysiert und eines der vollständigsten Reporting-Tools für Asterisk-Call-Center bleibt.
- **Eigenbau** – da das Format `queue_log` oben stabil und gut dokumentiert ist, ist es einfach, es mit einem kleinen Skript (Python etc.) zu parsen und die Ereignisse in eine Datenbank oder ein Dashboard einzuspeisen.

Für einen ereignisgesteuerten Ansatz, der über das Auslesen von `queue_log` hinausgeht, ermöglichen die **Asterisk REST Interface (ARI)** und die **AMI**-Aktionen `QueueSummary`/`QueueStatus` den Aufbau von Live-Queue-Dashboards und benutzerdefinierten Integrationen basierend auf dem Echtzeit-Queue-Status anstatt einer nachträglichen Log-Analyse. ARI ist die moderne, unterstützte Integrationsschnittstelle für diese Art von Arbeit in Asterisk 22.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, wie man eine ACD verwendet, wie ihre Architektur aussieht und wie man sie konfiguriert. Einige erweiterte Funktionen wie Prioritäten und Penalties wurden ebenfalls vorgestellt.

## Quiz

1. Welche der folgenden sind gültige Queue-Verteilungsstrategien in `queues.conf` (wählen Sie alle zutreffenden aus)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. Sie können ein Gespräch zwischen einem Agenten und einem Kunden innerhalb der Queue aufzeichnen, indem Sie die Option ___ in der Datei `queues.conf` setzen.
3. Welche `strategy` lässt Mitglieder in der genauen Reihenfolge klingeln, in der sie in `queues.conf` aufgelistet sind?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. Wenn der Agent im Telemarketing-Beispiel ein Gespräch beendet, welche Aktionen kann er durchführen (wählen Sie alle zutreffenden aus)?
   - A. Drücken von `*`, um die Verbindung zu trennen und in der Queue zu bleiben
   - B. Auflegen des Telefons und Trennen von der Queue
   - C. Drücken von `#8000`, um den Anruf zur Prüfung weiterzuleiten
   - D. Drücken von `#`, um sich sofort von allen Queues abzumelden
5. Welche zwei Aufgaben sind *erforderlich*, um eine funktionierende Queue zu erhalten (wählen Sie alle zutreffenden aus)?
   - A. Queue erstellen
   - B. Agenten erstellen
   - C. Agentenparameter konfigurieren
   - D. Aufzeichnung konfigurieren
   - E. Queue in den Dialplan einfügen
6. In einer Call Queue können Sie ein einstelliges Menü anbieten, das der Anrufer während des Wartens wählen kann. Dies wird durch die Definition eines/einer ___ im Abschnitt `queues.conf` der Queue aktiviert:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. Die unterstützenden Anwendungen `AddQueueMember()` und `RemoveQueueMember()` werden im ___ verwendet, um Mitglieder zur Laufzeit hinzuzufügen oder zu entfernen:
   - A. Dialplan
   - B. Command-Line Interface
   - C. queues.conf
   - D. agents.conf
8. Da chan_sip in Asterisk 21 entfernt wurde, muss ein statisches Queue-Mitglied auf einen Kanal wie ___ verweisen, anstatt auf `SIP/1001`.
9. Der Parameter `wrapuptime` ist die Mindestzeit, nachdem ein Agent ein Gespräch beendet hat, bevor die Queue diesem Agenten einen neuen Anruf sendet.
   - A. True
   - B. False
10. Einem Anrufer kann eine höhere Position in derselben Queue zugewiesen werden, indem die Kanalvariable `QUEUE_PRIO` vor dem Aufruf von `Queue()` gesetzt wird.
    - A. True
    - B. False

**Antworten:** 1 — A, C, D, E, F (roundrobin wurde durch rrmemory ersetzt und existiert nicht mehr) · 2 — `monitor-format` (die Aufzeichnung aus der Queue wird durch Angabe von `monitor-format` aktiviert; `monitor-type` wählt zwischen MixMonitor und Monitor) · 3 — C (linear) · 4 — A, B, C (`*` trennt die Verbindung und bleibt in der Queue; `#` ist keine Taste zum Abmelden von allen) · 5 — A, E · 6 — C (die Option `context`) · 7 — A (der Dialplan) · 8 — `PJSIP/1001` (jede `PJSIP/` Schnittstelle) · 9 — True · 10 — True
