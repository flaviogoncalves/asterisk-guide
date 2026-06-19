# Call Queues

Call Queues, auch bekannt als ACD (Automatic Call Distribution), werden immer wichtiger, um Kundenanrufe effizient zu beantworten. Ein automatischer Anrufverteiler kann dazu beitragen, Kosten zu senken, den Service zu verbessern und den Umsatz zu steigern, da Anrufverteiler die Arbeitsweise Ihres Unternehmens beeinflussen – nicht nur für ein paar Tage, sondern für viele Jahre. In einer Call-Center-Umgebung ist der wichtigste Faktor der Mensch; er ist die teuerste Ressource. Es kostet Zeit, Geld und Geduld, Agenten einzustellen, zu schulen und zu motivieren. Mit einer ACD können Sie die Produktivität der Agenten maximieren, indem Sie die erforderliche Anzahl an Agenten präzise dimensionieren, gute und schlechte Mitarbeiter kontrollieren und den Anruffluss analysieren.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Zu verstehen, warum und wie man Call Queues verwendet
- Die grundlegende Theorie von Call Queues zu verstehen
- Das Queue-System zu installieren und zu konfigurieren

## Wie funktionieren Queues?

Call Queues sind keine absolute Neuheit. Wenn Sie ein hohes Volumen an eingehenden Anrufen haben, ist es schwierig, diese angemessen zu verteilen. Die Verwendung einer Gruppenstrategie, bei der das Telefon bei allen Agenten gleichzeitig klingelt, scheint nicht zu funktionieren, es sei denn, Sie haben nur wenige Agenten. Eine Call Queue hingegen stellt Anrufe jeweils nur an einen einzigen verfügbaren Agenten zu und hält den Kunden mit Warteschleifenmusik in der Leitung, wenn keine Agenten verfügbar sind. Die Queue funktioniert, indem sie den Anruf hält, während sie nach einem freien Agenten sucht, der den Anruf entgegennehmen kann. Einer der größten Vorteile der Queue besteht darin, Anrufverluste zu vermeiden und gleichzeitig die Möglichkeit zu bieten, Statistiken zu erstellen.

![Eine Call Queue: Eingehende 1-800-Anrufe gelangen in die Queue und eine ACD-Strategie (ringall, rrmemory, leastrecent, priority und andere) verteilt sie an die verfügbaren Agenten](../images/14-queues-fig01.png)

Normalerweise funktioniert eine Call Queue wie folgt:

- Agenten melden sich an der Queue an.
- Eingehende Anrufe werden in die Warteschlange eingereiht.
- Eine Warteschlangenstrategie zur Verteilung der Anrufe wird verwendet, um Anrufe an Agenten zu senden.
- Während der Anrufer wartet, wird Warteschleifenmusik abgespielt.
- Anrufern können Ansagen gemacht werden, die sie über die Wartezeit informieren.
- Der Anruf wird vom Agenten entgegengenommen und Statistiken werden erstellt.

Die Hauptanwendung für Queues ist der Kundenservice. Durch die Verwendung von Queues vermeiden Sie Anrufverluste, wenn Ihre Agenten beschäftigt sind. Sie können der Queue neue Agenten hinzufügen, wenn Sie feststellen, dass die Anzahl der Anrufer in der Warteschlange wächst. Ein weiterer Vorteil von Queues ist, dass Sie nun Statistiken wie die Abbruchrate, die durchschnittliche Anrufdauer und das Anrufannahmeziel erhalten können. Diese Statistiken helfen Ihnen zu bestimmen, wie viele Agenten Sie einsetzen müssen, um Ihren Kunden einen besseren Service zu bieten.

### ACD-Architektur

Die ACD-Architektur besteht aus Queues und Agenten. Ein Agent kann gleichzeitig in zwei Queues sein. Eine Queue kann Agenten, Channels und Agentengruppen haben.

![ACD-Architektur: Jede Queue (Kundenservice, Inside Sales) wird von einer Telefonnummer gespeist und liefert Anrufe an Agenten, die wiederum an physische Channels gebunden sind](../images/14-queues-fig02.png)

## Queues

Queues werden in der Konfigurationsdatei queues.conf definiert. Agenten sind Mitarbeiter, die sich anmelden und Mitglieder von Queues sind. Agenten werden in der Datei agents.conf definiert. Das Queue-System ist über viele Releases hinweg erheblich gewachsen, was die Konfigurationsdatei umfangreich macht. Wir werden einige der wichtigsten Parameter erläutern. Allgemeine Parameter

```
autofill=yes
```

Das alte Verhalten der Queue war vom Typ serial. Die Queue wartete darauf, dass ein Anruf zugestellt wurde, bevor der nachfolgende Anruf an den nächsten Agenten gesendet wurde. Wenn ein Agent 15 Sekunden brauchte, um einen Anruf anzunehmen, mussten die anderen Anrufe in der Queue warten, bis dieser Anruf beantwortet wurde. Bei Queues mit hohem Volumen war dieses Verhalten ineffizient. Das neue Verhalten autofill=yes wartet nicht, bis ein Anruf beantwortet wurde, sondern arbeitet parallel. Sie können die Anrufe in der Queue mit der Option mixmonitor aufzeichnen. In diesem Modus werden Anrufe gleichzeitig aufgezeichnet und gemischt.

### Queue-Konfigurationsdatei

Queues werden in der Datei queues.conf konfiguriert. In der Abbildung finden Sie ein funktionierendes Beispiel einer Queue.

![Ein funktionierendes Beispiel der Datei queues.conf, das den allgemeinen Abschnitt und eine customerservice-Queue mit Strategie, Service-Level, Ansagen, Aufzeichnung und Mitgliedern zeigt](../images/14-queues-fig03.png)

### Agenten

Sie können Ihre Agenten in der Datei agents.conf konfigurieren. Agenten können sich von jedem Extension aus anmelden, um Anrufe entgegenzunehmen. Sie können einen Agenten anrufen mit:

```
Dial(agent/<name>)
```

#### Agenten

Agent 300

- Sie können den Status der Agenten mit dem Befehl `agent show all` überprüfen.
- Der Befehl agentlogin wird ausgeführt und der Agent wird dem aktuellen Channel zugeordnet.
- Der Benutzer wählt eine Extension mit der Applikation agentlogin.

![Agenten: Ein Benutzer meldet sich an, indem er eine Extension wählt, die die Applikation agentlogin ausführt, welche Agent 300 an den aktuellen Channel bindet; Sie können den Agentenstatus mit `agent show all` überprüfen](../images/14-queues-fig04.png)

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

Mitglieder sind aktive Channels, die auf die Queue reagieren. Mitglieder können direkte Channels (PJSIP, DAHDI) oder Agenten sein, die sich anmelden, bevor sie Anrufe erhalten.


### Strategien

Anrufe werden gemäß einer dieser Strategien unter den Mitgliedern verteilt:

- ringall: Lässt alle verfügbaren Channels klingeln, bis jemand abhebt.
- leastrecent: Verteilt an das Mitglied, das am längsten keinen Anruf erhalten hat.
- fewestcalls: Verteilt an das Mitglied mit den wenigsten Anrufen.
- random: Klingelt bei einer zufälligen Schnittstelle.
- wrandom: Klingelt bei einer zufälligen Schnittstelle, verwendet aber die Penalty des Mitglieds als Gewichtung bei der Berechnung der Metrik.
- rrmemory: Verwendet Round Robin mit Speicher; es merkt sich, wo es beim letzten Durchgang mit dem Anruf aufgehört hat.
- rrordered: Wie rrmemory, außer dass die Reihenfolge der Queue-Mitglieder aus der Konfigurationsdatei beibehalten wird.
- linear: Klingelt bei den Mitgliedern in der Reihenfolge, in der sie in queues.conf aufgelistet sind; bei dynamischen Mitgliedern in der Reihenfolge, in der sie hinzugefügt wurden.

> **[2nd-ed note]** Die Strategie `roundrobin` wurde in frühen Asterisk-Releases durch `rrmemory` ersetzt und ist nicht mehr verfügbar. Entfernen Sie sie aus der Strategieliste, falls sie in früheren Ausgaben des Textes erschien. Alle oben aufgeführten Strategien sind in Asterisk 22 bestätigt vorhanden.

## Agenten

Agenten werden als Proxy-Channels implementiert. Sie können innerhalb der Queues verwendet werden. Eine weitere Verwendung der Agenten-Channels ist Extension Mobility. Der Benutzer kann sich mit jedem Telefon anmelden und seine Anrufe empfangen. Dies ermöglicht es einem Benutzer, in jeden Raum zu gehen und ihn zu seinem Büro zu machen. Sie können einen Agenten im Dialplan mit dial(agent/<name>) anrufen. Sie definieren Agenten in der Datei agents.conf.

![Agenten-Mobilität: Der Benutzer nimmt ein beliebiges Telefon ab, wählt eine Login-Extension und gibt die Agentennummer und das Passwort ein; nachdem agentlogin() erfolgreich war, ist der Agent (Agent 300) bereit, Anrufe entgegenzunehmen, und Sie können den Status mit dem CLI-Befehl `agent show all` überprüfen](../images/14-queues-fig05.png)

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

## ACD-bezogene Applikationen

Das Asterisk-Queue-System stellt mehrere Applikationen zur Verfügung, um die Queues im Dialplan zu implementieren. Nachfolgend zeigen wir einige davon.

### Die Applikation queue()

Diese Applikation reiht eingehende Anrufe in eine bestimmte Call Queue ein, wie in queues.conf definiert. Die Optionszeichenfolge kann null oder mehr der folgenden Zeichen enthalten: Zusätzlich zur Weiterleitung des Anrufs kann ein Anruf geparkt und dann von einem anderen Benutzer abgeholt werden. Die optionale URL wird an den angerufenen Teilnehmer gesendet, wenn der Channel dies unterstützt. Der optionale AGI-Parameter richtet ein AGI-Skript ein, das auf dem Channel des anrufenden Teilnehmers ausgeführt wird, sobald dieser mit einem Queue-Mitglied verbunden ist. Das Timeout führt dazu, dass die Queue nach einer bestimmten Anzahl von Sekunden fehlschlägt, geprüft zwischen jedem Timeout- und Wiederholungszyklus. Diese Applikation setzt nach Abschluss die Statusvariable QUEUE:

![Die Applikation queue(): ihre Syntax `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` und die verfügbaren einbuchstabigen Optionen (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### Die Applikation agentlogin()

Diese Applikation fordert den Agenten auf, sich am System anzumelden. Sie gibt immer -1 zurück. Während der Anmeldung hört der Agent bei einem eingehenden Anruf einen Piepton. Der Agent kann den Anruf durch Drücken der Taste * abwerfen.

![Die Applikation agentlogin(): ihre Syntax `AgentLogin([AgentNo][|options])` und die Option `s` für eine stille Anmeldung, die die Anmeldebestätigung nicht ankündigt](../images/14-queues-fig08.png)

### Die Applikation addQueueMember()

Diese Applikation fügt dynamisch ein Gerät (z. B. PJSIP/3000) zu einer Queue hinzu. Wenn das Gerät bereits existiert, gibt sie einen Fehler zurück.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### Die Applikation removeQueueMember()

Diese Applikation entfernt dynamisch ein Gerät aus der Queue. Wenn das Gerät nicht zur Queue gehört, gibt sie einen Fehler zurück.

```
RemoveQueueMember(queuename[|interface])
```

### Support-Applikationen und CLI-Befehle

Einige Applikationen und Konsolenbefehle können bei der Arbeit mit Queues helfen. Das Folgende skizziert, was jede Applikation tut:

![Support-Applikationen (AddQueueMember, RemoveQueueMember) und CLI-Befehle (agent show all, queue show, queue show <name>), die zur Verwaltung von Queues zur Laufzeit verwendet werden](../images/14-queues-fig09.png)

## Konfigurationsaufgaben

Die folgende Abbildung fasst die wichtigsten Aufgaben zur Erstellung eines funktionierenden Queue-Systems zusammen.

![Die ACD-Konfigurationsaufgaben: (1) Call Queue erstellen (erforderlich), (2) Agentenparameter definieren (optional), (3) Agenten erstellen (optional), (4) Queue in den Dialplan einfügen (erforderlich), (5) Agentenaufzeichnung konfigurieren (optional) und (6) mit agent show all und queue show überprüfen (optional)](../images/14-queues-fig10.png)

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

Anrufe können mit der Asterisk-Applikation MixMonitor aufgezeichnet werden. (Die eigenständige Monitor-Applikation wurde in Asterisk 22 entfernt, und die Option `monitor-type` in queues.conf akzeptiert jetzt nur noch MixMonitor.) Die Aufzeichnung kann innerhalb der Queue-Applikation aktiviert werden und beginnt, sobald der Anruf tatsächlich angenommen wird. Nur erfolgreiche Anrufe werden aufgezeichnet, und es werden keine Aufzeichnungen durchgeführt, während Personen MOH hören. Um die Überwachung zu aktivieren, geben Sie einfach monitor-format an. Diese Funktion ist ansonsten deaktiviert. Sie können den Dateinamen für die Aufzeichnung mit Set(MONITOR_FILENAME=<filename>) festlegen; andernfalls

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

Die folgenden Beispiele erklären, wie man die Queue verwendet. Schritt 1: Agenten-Login Beispiel: Ein Agent in der Telemarketing-Queue nimmt das Telefon ab und wählt #9000. Der Agent hört eine Nachricht über eine ungültige Anmeldung und wird nach seinem Namen und Passwort gefragt. Die Audit-Queue folgt demselben Verfahren. Schritt 2: Queue Sobald der Agent in der Queue ist, hört er MOH, falls definiert. Wenn ein Anruf in der Telemarketing-Queue eingeht, hört der Agent einen Piepton und wird mit diesem Anruf verbunden. Schritt 3: Anrufende Wenn der Agent den Anruf beendet, kann er/sie:

- '*' drücken, um die Verbindung zu trennen und in der Queue zu bleiben.
- Das Telefon auflegen und sich dadurch von der Queue trennen.
- #8000 drücken, um den Anruf zur Prüfung weiterzuleiten.

## Erweiterte Ressourcen

Das Asterisk-Queue-System verfügt über einige erweiterte Funktionen, um bestimmte Kunden und Agenten zu priorisieren sowie ein Benutzermenü zu ermöglichen.

### Benutzermenü

Sie können ein Menü für einen Benutzer definieren, während er in der Queue wartet, indem Sie einstellige Extensions verwenden. Um diese Option zu aktivieren, definieren Sie einen Context in der Queue-Konfiguration queues.conf.

### Penalty

Agenten können mit einer Penalty konfiguriert werden. Eine Queue sendet die Anrufe zuerst an Benutzer mit niedrigeren Penalty-Werten. Da wir zum Beispiel wissen, dass unsere Kunden Susan und ihre sanfte Stimme lieben, können wir ihr die Priorität 0 zuweisen. Alternativ ist der Agent namens Uber, der weniger Erfahrung hat, für den Kundenservice weniger bevorzugt; daher weisen wir diesem Agenten die Priorität 10 zu. In der Datei queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priorität

Queues arbeiten im FIFO-Modus (First In, First Out). Wenn Sie besonderen Kunden (Platin, Gold) Priorität einräumen möchten, können Sie differenzierte Prioritäten einrichten. Für Platin- oder Gold-Kunden:

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

## Die Applikation agentcallbacklogin() wurde entfernt

Die Applikation `agentcallbacklogin()` wurde von Digium in Asterisk 1.4 (Juli 2006) als veraltet markiert und ist in Asterisk 22 nicht mehr verfügbar. Der empfohlene Ansatz ist die Verwendung von `AddQueueMember()` mit einer PJSIP-Schnittstelle, um dynamisch Mitglieder im Callback-Stil zu einer Queue hinzuzufügen. Das Dokument `queues-with-callback-members.txt` war in älteren Asterisk-Verzeichnissen `/doc` für Migrationsanleitungen enthalten.

> **[2nd-ed note]** Überprüfen Sie, ob der Channel-Treiber `chan_agent` (app_agent_pool) in Asterisk 22 immer noch der bevorzugte Mechanismus für das Agenten-Callback-Verhalten ist oder ob direkte PJSIP-Mitglieder mit `AddQueueMember()`/`RemoveQueueMember()` jetzt das Standardmuster sind.

## Queue-Statistiken

Alle Ereignisse von Queues werden in /var/log/asterisk/queue_log protokolliert. Das Format des Queue-Logs ist im Dokument queuelog.txt im Verzeichnis /doc der Asterisk-Dokumentation veröffentlicht. Nachfolgend sind einige der wichtigsten protokollierten Ereignisse aufgeführt.

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

Sie können Ihr eigenes Dienstprogramm zur Verarbeitung dieser Ereignisse erstellen oder ein fertiges Statistikpaket verwenden. Wir haben zwei Dienstprogramme bei voip.school getestet:

- Qlog analyzer (http://www.micpc.com/qloganalyzer/) – Exzellentes Open-Source-Paket
- Queue metrics (http://queuemetrics.com/) – Eines der vollständigsten Pakete für Queue-Statistiken

> **[2nd-ed note]** Überprüfen Sie, ob beide Statistik-Tools von Drittanbietern noch gewartet werden und mit dem Format von Asterisk 22 queue_log kompatibel sind. Erwägen Sie, einen Verweis auf die Asterisk REST Interface (ARI) als moderne Alternative für den Aufbau benutzerdefinierter Queue-Reporting-Integrationen hinzuzufügen.

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
7. Die Support-Applikationen `AddQueueMember()` und `RemoveQueueMember()` werden im ___ verwendet, um Mitglieder zur Laufzeit hinzuzufügen oder zu entfernen:
   - A. Dialplan
   - B. Command-Line Interface
   - C. queues.conf
   - D. agents.conf
8. Da chan_sip in Asterisk 21 entfernt wurde, muss ein statisches Queue-Mitglied auf einen Channel wie ___ verweisen, anstatt auf `SIP/1001`.
9. Der Parameter `wrapuptime` ist die Mindestzeit, nachdem ein Agent ein Gespräch beendet hat, bevor die Queue diesem Agenten einen neuen Anruf sendet.
   - A. True
   - B. False
10. Ein Anrufer kann eine höhere Position in derselben Queue erhalten, indem er die Channel-Variable `QUEUE_PRIO` setzt, bevor er `Queue()` aufruft.
    - A. True
    - B. False

**Antworten:** 1 — A, C, D, E, F (roundrobin wurde durch rrmemory ersetzt und existiert nicht mehr) · 2 — `monitor-format` (die Aufzeichnung aus der Queue wird durch Angabe von `monitor-format` aktiviert; `monitor-type` wählt zwischen MixMonitor und Monitor) · 3 — C (linear) · 4 — A, B, C (`*` trennt die Verbindung und bleibt in der Queue; `#` ist keine Taste zum Abmelden von allen Queues) · 5 — A, E · 6 — C (die Option `context`) · 7 — A (der Dialplan) · 8 — `PJSIP/1001` (jede `PJSIP/` Schnittstelle) · 9 — True · 10 — True
