# Dial Plan fortgeschrittene Funktionen

Kapitel 3 behandelte die Grundlagen eines dialplan. Aus didaktischen Gründen haben wir nicht alle Funktionen erklärt, sondern nur einige der wichtigsten. Dieses Kapitel befasst sich eingehender mit dem dialplan und beschreibt fortgeschrittene Techniken, neue Anwendungen und Konzepte.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Ihre extension-Einträge zu vereinfachen
- dialplan-Sicherheit und das Filtern von extensions zu adressieren
- Anrufe mithilfe eines IVR-Menüs entgegenzunehmen
- Subroutinen zu verwenden, um unnötige Wiederholungen zu vermeiden
- dialplan-Sicherheit mithilfe von „Include“ zu implementieren
- Follow-me mithilfe der AsteriskDB zu implementieren
- Verhalten außerhalb der Geschäftszeiten in Ihrer PBX zu implementieren
- Den switch-Befehl zu verwenden, um an eine andere PBX weiterzuleiten
- Den Privacy Manager zu implementieren
- Voicemail zu implementieren
- Ein Unternehmensverzeichnis zu implementieren

## Vereinfachung Ihres Dial Plan

Sie können Ihren dialplan mithilfe des Schlüsselworts „same“ vereinfachen, um eine extension zu definieren. Dies sollte die Anzahl der Tippfehler im dialplan reduzieren. Prüfen Sie das folgende Beispiel:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan Sicherheit

Es wurde eine Schwachstelle im Asterisk dialplan entdeckt, die es einem Benutzer ermöglicht, einen neuen Kanal einzuschleusen und eine Nummer in Ihren dialplan zu wählen. Nehmen wir an, Sie haben die folgende Zeile in Ihrem Server `exten=>_X.,1,Dial(PJSIP/${EXTEN})` und ein böswilliger Benutzer hat die Nummer `3000&DAHDI/1/011551123456789` im softphone gewählt. Das SIP-Protokoll akzeptiert standardmäßig alle alphanumerischen Zeichen, daher wird die gewählte extension tatsächlich zwei Anrufe auslösen: einen für den Kanal PJSIP/3000 und den anderen für den Kanal DAHDI/011551123456789, bei dem es sich um eine internationale Nummer handelt. Somit kann jeder Benutzer mit Zugriff auf eine extension tatsächlich überall auf der Welt anrufen. Der einfachste Weg, dieses Verhalten zu vermeiden, besteht darin, die Nummern zu filtern, bevor die dial-Anwendung aufgerufen wird. Die Funktion FILTER() ist hierfür sehr praktisch. Beispiel:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

Die Anwendung filter ermöglicht es Ihnen, alle Zeichen aus der gewählten Nummer zu filtern, mit Ausnahme der Zahlen 0 bis 9. Weitere Informationen finden Sie in der Datei README-SERIOUSLY.bestpractices.txt, die von Asterisk bereitgestellt wird.

## Anrufe mithilfe eines IVR-Menüs entgegennehmen.

Im letzten Abschnitt haben Sie alle Anrufe mithilfe von DID oder durch Weiterleitung an die Vermittlung entgegengenommen. Jetzt lernen Sie, wie Sie ein IVR-Menü implementieren und einen Auto-Attendant-Dienst erstellen. Bevor wir auf die Einzelheiten eingehen, lassen Sie uns einige neue Anwendungen untersuchen. Wir haben die Ausgabe des Befehls show application unten eingefügt, um es den Lesern zu erleichtern. Sie können diese Beschreibungen mithilfe von show application application_name erhalten. 1 http://downloads.asterisk.org/pub/security/AST-2010-002.pdf

### Die Background() Anwendung

Diese Anwendung spielt die angegebene Liste von Dateien ab, während sie darauf wartet, dass eine extension vom anrufenden Kanal gewählt wird. Um nach dem Abspielen der Dateien weiterhin auf Ziffern zu warten, sollte die Anwendung WaitExten verwendet werden. Die Option langoverride gibt explizit an, welche Sprache für die angeforderten Sounddateien versucht werden soll. Jeder angegebene context ist der dialplan-context, den diese Anwendung beim Beenden zu einer gewählten extension verwendet. Wenn eine der angeforderten Sounddateien nicht existiert, wird die Anrufverarbeitung beendet. Optionen:

- s - Bewirkt, dass die Wiedergabe der Nachricht übersprungen wird, wenn sich der Kanal nicht im 'up'-Zustand befindet (d. h. er wurde noch nicht beantwortet). Wenn dies geschieht, kehrt die Anwendung sofort zurück.
- n - Den Kanal nicht beantworten, bevor die Dateien abgespielt werden.
- m - Nur unterbrechen, wenn eine gewählte Ziffer mit einer einstelligen extension im Ziel-context übereinstimmt.

### Die Record() Anwendung

Diese Anwendung nimmt vom Kanal in einen angegebenen Dateinamen auf. Wenn die Datei existiert, wird sie überschrieben.

![10-dialplan-advanced-features figure 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' ist das Format des Dateityps, der aufgenommen werden soll (wav, gsm, etc.).
- 'silence' ist die Anzahl der Sekunden der Stille, die erlaubt sind, bevor zurückgekehrt wird.
- 'maxduration' ist die maximale Aufnahmedauer in Sekunden; wenn sie fehlt oder null ist, gibt es kein Maximum.
- 'options' kann einen der folgenden Buchstaben enthalten:
    - `a` — hängt an eine bestehende Aufnahme an, anstatt sie zu ersetzen
    - `n` — nicht beantworten, aber trotzdem aufnehmen, wenn die Leitung noch nicht beantwortet wurde
    - `q` — leise (keinen Piepton abspielen)
    - `s` — überspringt die Aufnahme, wenn die Leitung noch nicht beantwortet wurde
    - `t` — verwendet die alternative `*` Abbruchtaste (DTMF) anstelle der Standardtaste `#`
    - `x` — ignoriert alle Abbruchtasten (DTMF) und nimmt bis zum Auflegen auf

Wenn der Dateiname %d enthält, werden diese Zeichen jedes Mal, wenn die Datei aufgenommen wird, durch eine um eins erhöhte Zahl ersetzt. Verwenden Sie core show file formats, um die verfügbaren Formate auf Ihrem System zu sehen. Der Benutzer kann # drücken, um die Aufnahme zu beenden und mit der nächsten Priorität fortzufahren. Wenn der Benutzer während einer Aufnahme auflegt, gehen alle Daten verloren und die Anwendung wird beendet.

### Die Playback() Anwendung

Diese Anwendung spielt angegebene Dateinamen ab (ohne Erweiterung). Optionen können auch nach einem Pipe-Symbol eingefügt werden. Die Option 'skip' bewirkt, dass die Wiedergabe der Nachricht übersprungen wird, wenn sich der Kanal nicht im 'up'-Zustand befindet (d. h. noch nicht beantwortet wurde).

![10-dialplan-advanced-features figure 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features figure 3](../images/10-dialplan-advanced-features-img03.png)

Wenn 'skip' angegeben ist, kehrt die Anwendung sofort zurück, falls der Kanal nicht abgenommen wurde. Andernfalls wird der Kanal beantwortet, bevor der Ton abgespielt wird, es sei denn, 'noanswer' ist angegeben. Nicht alle Kanäle unterstützen das Abspielen von Nachrichten, während der Hörer noch aufgelegt ist. Wenn 'j' angegeben ist, springt die Anwendung zu Priorität n+101, wenn die Datei nicht existiert. Diese Anwendung setzt nach Abschluss die folgende Kanalvariable:

- PLAYBACKSTATUS — der Status des Wiedergabeversuchs als Textzeichenfolge, einer der folgenden:
    - `SUCCESS`
    - `FAILED`

### Die Read() Anwendung

Diese Anwendung liest eine vorbestimmte Anzahl von Ziffernzeichenfolgen, eine bestimmte Anzahl von Malen, vom Benutzer in die angegebene Variable.

- filename -- Datei, die vor dem Lesen von Ziffern oder Tönen mit Option i abgespielt werden soll
- maxdigits -- maximale akzeptable Anzahl von Ziffern. Stoppt das Lesen, nachdem maxdigits eingegeben wurden (ohne dass der Benutzer die # Taste drücken muss). Standard ist 0 - kein Limit - um darauf zu warten, dass der Benutzer die # Taste drückt. Jeder Wert unter 0 bedeutet dasselbe. Der maximal akzeptierte Wert ist 255.

![10-dialplan-advanced-features figure 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features figure 5](../images/10-dialplan-advanced-features-img05.png)

- option -- Optionen sind `s`, `i`, `n`:
    - `s` — sofort zurückkehren, wenn die Leitung nicht up ist
    - `i` — filename als Hinweiston von Ihrem `indications.conf` abspielen
    - `n` — Ziffern lesen, auch wenn die Leitung nicht up ist
- attempts -- wenn größer als 1, die Anzahl der Versuche, die unternommen werden, falls keine Daten eingegeben werden
- timeout -- Eine Ganzzahl in Sekunden, um auf eine Ziffernantwort zu warten. Wenn größer als 0, überschreibt dieser Wert das Standard-Timeout.

Die read() Anwendung sollte die Verbindung trennen, wenn die Funktion fehlschlägt oder einen Fehler ausgibt.

### Die Gotoif() Anwendung

Diese Anwendung bewirkt, dass der anrufende Kanal basierend auf der Auswertung der angegebenen Bedingung an die angegebene Stelle im dialplan springt. Der Kanal fährt bei labeliftrue fort, wenn die Bedingung wahr ist, oder bei 'labeliffalse', wenn die Bedingung falsch ist. Die Labels werden mit derselben Syntax angegeben wie innerhalb der Goto-Anwendung. Wenn das durch die Bedingung gewählte Label weggelassen wird, wird kein Sprung durchgeführt; stattdessen wird die Ausführung mit der nächsten Priorität im dialplan fortgesetzt.

### Labor: Schritt-für-Schritt-Aufbau eines IVR-Menüs

Lassen Sie uns ein IVR-Menü mit der folgenden Funktionalität erstellen. Wenn es gewählt wird, spielt das IVR eine Audiodatei mit der Nachricht „Willkommen bei der XYZ Corporation; drücken Sie 1 für Vertrieb, 2 für technischen Support, 3 für Schulungen oder warten Sie, um mit einem Mitarbeiter zu sprechen.“ Die Ziffern leiten den Anrufer wie folgt weiter:

- `1` — Weiterleitung an Vertrieb (PJSIP/4001)
- `2` — Weiterleitung an technischen Support (PJSIP/4002)
- `3` — Weiterleitung an Schulung (PJSIP/4003)
- Keine Ziffer gedrückt — Weiterleitung an die Vermittlung (PJSIP/4000)

**Schritt 1 – Die Ansagen aufnehmen**

Lassen Sie uns eine extension erstellen, um die Ansagen aufzunehmen. Um eine Ansage aufzunehmen, wählen Sie von einem softphone aus `9003<filename>` (zum Beispiel `9003welcome`). Wenn Sie den Piepton hören, beginnen Sie mit der Aufnahme; drücken Sie `#` zum Stoppen. Sie hören einen Piepton und das System spielt die aufgenommene Ansage ab.

**Schritt 2 – Die Menülogik erstellen**

Beim Wählen der extension 9004 springt die Verarbeitung zum Menü in der extension `s`, Priorität 1.

### Abgleich während des Wählens

Dies ist ein Firmen-Einrichtungsmenü für den Empfang von Anrufen. Die background-Anwendung liest den aktuellen context und definiert die maximale Länge für jede Nummer für jede mögliche Kombination.

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

Wenn Sie diese Firma anrufen, wird zuerst die Willkommensnachricht abgespielt. Danach wartet Asterisk darauf, dass eine Ziffer gewählt wird. Gewählte Nummer Asterisk Aktion Ruft sofort Dial(DAHDI/1) auf Wartet auf das Timeout, geht dann zu Dial(DAHDI/2) Ruft sofort (DAHDI/3) auf Ruft sofort (DAHDI/4) auf Wartet auf das Timeout, dann trennt die Verbindung Ruft sofort Dial(DAHDI/5) auf Ruft sofort Dial(DAHDI/6) auf Trennt sofort die Verbindung Es ist wichtig, Mehrdeutigkeiten in den Menüs zu vermeiden. Jeder möchte schnell bedient werden. Aus diesem Grund sollten Sie die Nummern 2, 21 oder 22 nicht verwenden.

### Labor: Verwendung der Read() Anwendung

Bitte versuchen Sie das Labor mit der read() Anwendung. Read akzeptiert Ziffern vom Benutzer und fügt sie in die angegebene Variable ein; Sie können dann die gotoif-Anwendung verwenden, um den Anruf umzuleiten.

## Context Inclusion

Ein context kann den Inhalt eines anderen context enthalten. Im obigen Beispiel kann jeder Kanal jede extension im internal-context wählen, aber nur der Kanal 4003 kann internationale extensions wählen. Sie können context inclusion verwenden, um die Erstellung des dialplan zu erleichtern. Mithilfe von context inclusion können Sie steuern, wer Zugriff auf welche extensions hat.

### Fehlerbehebung bei der Meldung „number not found“

Es ist sehr üblich, die Meldung „number not found“ zu erhalten. Die meisten Leute verwechseln das Konzept der inkludierten contexts, weil es nicht wirklich intuitiv ist. Als Faustregel gilt: Gehen Sie zuerst zur Konfigurationsdatei des eingehenden Kanals, wie `pjsip.conf`, `chan_dahdi.conf` und `iax.conf`, und bestimmen Sie den aktuellen context. Gehen Sie dann zum dialplan in der Datei extensions.conf und prüfen Sie, ob die gewählte Nummer in diesem context gefunden werden kann. Wenn nicht, stimmt etwas mit Ihrem dialplan nicht. Die goldenen Regeln für contexts sind: 1. Ein Kanal kann nur Nummern innerhalb desselben context wie der Kanal wählen. 2. Der context, in dem der Anruf verarbeitet wird, ist in der Konfigurationsdatei des eingehenden Kanals definiert (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Verwendung der switch-Anweisung

Sie können die dialplan-Verarbeitung mithilfe des switch-Befehls an einen anderen Server senden. Sie benötigen den Namen und den Schlüssel des anderen Servers. Der context ist der Ziel-context.

![10-dialplan-advanced-features figure 6](../images/10-dialplan-advanced-features-img06.png)

## Reihenfolge der Dial Plan Verarbeitung

Wenn Asterisk einen eingehenden Anruf empfängt, sucht es in dem durch den Kanal definierten context. In einigen Fällen, wenn mehr als ein Muster mit der gewählten Nummer übereinstimmt, kann Asterisk den Anruf nicht genau so verarbeiten, wie Sie es erwarten. Sie können die Übereinstimmungsreihenfolge mithilfe des CLI-Befehls dialplan show sehen. Beispiel: Nehmen wir an, Sie möchten 912 wählen, um zu einem analogen trunk (DAHDI/1) weiterzuleiten, und alle anderen Nummern, die mit 9 beginnen, zu einem anderen analogen trunk (DAHDI/2). Sie würden etwa Folgendes schreiben:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Wenn zwei Muster mit einer extension übereinstimmen, können Sie steuern, welche extension zuerst verarbeitet wird, indem Sie inkludierte contexts verwenden. Ein inkludierter context wird später verarbeitet als ein Muster im selben context.

## Die #INCLUDE Anweisung

Sollten wir eine große Datei oder mehrere Dateien verwenden? Sie können die Anweisung #include <filename> verwenden, um andere Dateien in Ihre extensions.conf einzubinden. Zum Beispiel könnten wir eine users.conf für lokale Benutzer und services.conf für spezielle Dienste erstellen. Achten Sie darauf, #include <filename> nicht mit der

```
include=>context statement.
```

## Subroutinen mit GOSUB

In älteren Versionen von Asterisk gab es den Befehl Macro. Dieser Befehl wurde vor langer Zeit zugunsten von GOSUB als veraltet markiert. Wir zeigen hier, wie man Subroutinen für die Voicemail-Verarbeitung auf einfache und geordnete Weise erstellt. Befehlsformat:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

Der Befehl GOSUB ist seit Asterisk 1.6 verfügbar und unterstützt die Übergabe von Argumenten (verfügbar innerhalb der Subroutine als `${ARG1}`, `${ARG2}` usw.). Mit Argumenten ist es nun möglich, die alten Macro-Befehle vollständig zu ersetzen. Macros (`app_macro`) wurden in Asterisk 21 entfernt; Sie müssen GOSUB für Subroutinen verwenden.

### Erstellen der Subroutine

Die Definition ist sehr ähnlich. Schauen Sie sich die untenstehende Subroutine für Voicemail mit dem Namen stdexten an (wählen Sie den Namen, den Sie mögen). Nach dem Aufruf des Befehls Dial mit dem ersten Argument (Name des Kanals) prüfen wir die ${DIALSTATUS}, um die Anruflogik an den nächsten Schritt zu senden.

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

### Aufrufen einer Subroutine

Achten Sie beim Aufrufen der Subroutine darauf, Klammern vor den Parametern zu verwenden.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Verwendung der Asterisk DB

Um Anrufweiterleitung und Blacklists zu implementieren, benötigen wir eine Möglichkeit, Daten zu speichern und wiederherzustellen. Glücklicherweise bietet Asterisk einen Mechanismus zum Speichern und Abrufen von Daten aus einer eingebauten Datenbank namens AstDB. Im modernen Asterisk (einschließlich Asterisk 22) wird AstDB durch **SQLite3** unterstützt (die Datei `/var/lib/asterisk/astdb.sqlite3`); ältere Versionen verwendeten Berkeley DB v1. Dies ähnelt der Windows-Registrierungsdatenbank, die das hierarchische Konzept von Familie und Schlüsseln verwendet. Die Daten bleiben zwischen Asterisk-Neustarts erhalten.

> **[2nd-ed note]** Seit Asterisk 10 wird die AstDB in SQLite3 (`astdb.sqlite3`) gespeichert, nicht mehr in der alten Berkeley DB v1-Datei, die von Asterisk 1.8 und früher verwendet wurde. Die Familie/Schlüssel-API ist unverändert.

### Funktionen, Anwendungen und CLI-Befehle

Es gibt einige Funktionen, Anwendungen und CLI-Befehle, die mit AstDB arbeiten:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Beispiele:

```
exten=_*21*XXXX,1,set(DB(CFBS/${CALLERID(num)}=${EXTEN:4}))
exten=s,1,set(temp=${DB(CFBS/${EXTEN})})
```

Einige Anwendungen können verwendet werden, um AstDB zu manipulieren:

- DB_DELETE(<family/key>) — Funktion, die einen Schlüssel zurückgibt und löscht (die alte `DBdel()` Anwendung wurde entfernt)
- DBdeltree(<family>)

> **[2nd-ed note]** Die `DBdel()` Anwendung existiert in Asterisk 22 nicht mehr. Löschen Sie einen einzelnen Schlüssel mit der `DB_DELETE()` dialplan-Funktion — z. B. `Set(x=${DB_DELETE(family/key)})` oder, als Schreiboperation, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (Löschen einer ganzen Familie/eines Teilbaums) ist immer noch eine Anwendung.

Es ist möglich, CLI-Befehle zu verwenden, um Schlüssel ebenfalls zu setzen und zu löschen:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementierung von Anrufweiterleitung, DND und Blacklists

In diesem Beispiel lernen Sie, wie Sie Anrufweiterleitung sofort und Anrufweiterleitung bei Besetzt implementieren. Wir verwenden *21* zum Programmieren der Anrufweiterleitung sofort und *61* zum Programmieren der Anrufweiterleitung bei Besetzt. Um die Programmierung abzubrechen, verwenden Sie #21# bzw. #61#. Verwenden Sie das obige Beispiel, um die Datenbank zu füllen. Verwendete Familien:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Versuchen Sie, die Datenbank durch Wählen von Folgendem zu füllen:

- *21* (Ziel-extension für Anrufweiterleitung sofort)
- *61* (Ziel-extension für Anrufweiterleitung bei Besetzt)
- *41* (extension für Nicht-Stören)

Verwenden Sie den CLI-Befehl database show, um die hinzugefügten Familien, Schlüssel und Werte zu sehen.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Anrufweiterleitung, Blacklist, DND

Die obige Subroutine prüft, ob die Datenbank die Schlüssel:Wert-Paare enthält, die CFIM, CFBS oder DND entsprechen, und behandelt sie dann entsprechend. Die follow-Subroutine ruft die Wählroutine auf:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Verwendung einer Blacklist

> **[2nd-ed note]** Die `LookupBlacklist()` Anwendung wurde **entfernt** (sie verschwand mit dem alten "priority+101 jump"-Mechanismus lange vor Asterisk 22 — bestätigt, nicht im 22.10.0 Labor registriert). Implementieren Sie stattdessen eine Blacklist mit den `DB()`/`DB_EXISTS()` Funktionen plus `GotoIf`, zum Beispiel:
>
> ```
> exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
> exten => s,n,Dial(PJSIP/4000,20,tT)
> exten => s,n,Hangup()
> ```
>
> Das Beispiel unten wird aus historischen Gründen beibehalten; die `j` Option und der `n+101` Prioritätssprung existieren nicht mehr.

Um eine Blacklist zu erstellen, verwenden wir die Anwendung LookupBlacklist(). Die Anwendung prüft den Namen/die Nummer in der Anrufer-ID. Wenn die Nummer nicht gefunden wird, setzt die Anwendung die Variable $LOOKUPBLSTATUS auf NOTFOUND. Wenn die Nummer gefunden wird, setzt die Anwendung die Variable auf FOUND. Sie können die „j“-Option in der Anwendung verwenden, um das alte (1.0) Verhalten zu nutzen, bei dem 101 Positionen gesprungen wird, wenn die Nummer/der Name gefunden wird. Beispiel:

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

Um eine Nummer in die Blacklist einzufügen, können wir dieselbe Ressource wie zuvor verwenden, indem wir *31* gefolgt von den zu sperrenden extensions verwenden. Um eine Nummer aus der Blacklist zu entfernen, sollten Sie #31# gefolgt von der zu entfernenden Nummer verwenden.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN}=1})
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Sie können die Nummern auch mithilfe der Konsolen-CLI in die Blacklist einfügen:

```
CLI>database put blacklist <name/number> 1
```

Hinweis: Jeder Wert kann mit dem Schlüssel verknüpft werden. Die Blacklist-Anwendung sucht nach dem Schlüssel, nicht nach dem Wert. Um die Nummer aus der Blacklist zu löschen, können Sie Folgendes verwenden:

```
CLI>database del blacklist <name/number>
```

## Zeitbasierte Contexts

In der folgenden Abbildung haben wir einen dialplan mit drei contexts. Der [incoming] context ist der Ort, an dem die Anrufe normalerweise empfangen werden. Wir haben vier Zeilen eingefügt, die das Verhalten je nach Systemzeit ändern, wie unten beispielhaft dargestellt:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

> **[2nd-ed note]** Modernes Asterisk (inkl. 22) trennt die time-include-Felder mit **Kommas**, nicht mit Pipes. Die alte Pipe-Form (`include => context|times|weekdays|mdays|months`) wird als einfacher literaler context-Name geparst und wendet stillschweigend keine Zeitbedingung an. Verifiziert im Asterisk 22.10.0 Labor.

Während der regulären Arbeitszeiten wird die Verarbeitung an das mainmenu umgeleitet, wo wahrscheinlich ein IVR aufgerufen wird, um den eingehenden Anruf zu bearbeiten. Wenn der Anruf außerhalb der Geschäftszeiten erfolgt, wird die security-extension aufgerufen, die in der Variable ${SECURITY} definiert ist. Wenn die security-extension den Anruf nicht beantwortet, wird er an die Voicemail der Vermittlung gesendet.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Zeitbasierte Nachrichten mithilfe von gotoiftime()

Die Syntax von gotoiftime() ist unten dargestellt.

```
GotoIfTime(<timerange>,<daysofweek>,<daysofmonth>,<months>[,<timezone>]?[[context,]extension,]pri)
```

> **[2nd-ed note]** In Asterisk 22 ist das Feldtrennzeichen ein **Komma**, keine Pipe (die Pipe-Form wurde in Asterisk 1.6 als veraltet markiert). Die aktuell dokumentierte Syntax ist `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`. Ein optionales `timezone` Feld wird unterstützt.

Diese Anwendung kann den zeitbasierten context ersetzen und scheint einfacher zu verstehen und zu lesen zu sein. Sie können die Zeit wie folgt angeben:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=Zahl von 1 bis 31
- <hour>=Zahl von 0 bis 23
- <minute>=Zahl von 0 bis 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Namen für Tage und Monate sind nicht groß-/kleinschreibungssensitiv.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

Die vorherige Anweisung überträgt die Verarbeitung an die extension s im normalhours-context, wenn der Anruf zwischen 08:00 Uhr und 18:00 Uhr von Montag bis Freitag erfolgt.

## Verwendung von DISA, um ein neues Wähltonsignal zu erhalten

DISA, oder „direct inward system access“, ist ein System, das es Benutzern ermöglicht, ein zweites Wähltonsignal zu erhalten. Es erlaubt Benutzern, erneut zu einem anderen Ziel zu wählen. Es wird oft von Technikern verwendet, wenn sie am Wochenende Ferngespräche für technischen Support führen; anstatt direkt von zu Hause aus das Ziel zu wählen, rufen sie die DISA-Nummer des Büros an, erhalten ein Wähltonsignal und rufen dann das Ziel an. Die Ferngesprächsgebühren fallen bei der Firma an, anstatt beim Telefon zu Hause.

```
DISA(passcode[,context])
DISA(password-file[,context])
```

Beispiel:

```
exten => s,1,DISA(no-password,default)
```

Bei Verwendung der vorherigen Anweisung wählt der Benutzer die PBX und erhält – ohne dass ein Passwort erforderlich ist – ein Wähltonsignal. Jeder Anruf, der DISA verwendet, wird mithilfe des `default` context verarbeitet. Die Argumente für diese Anwendung beinhalten ein globales Passwort oder ein individuelles Passwort innerhalb einer Datei. Wenn kein context angegeben ist, wird der `disa` context angenommen. Wenn Sie eine Passwortdatei verwenden, muss der vollständige Pfad angegeben werden. Eine Anrufer-ID kann auch für das externe Wählen über DISA angegeben werden. Beispiel:

```
numeric-passcode,context,"Flavio" <4830258590>
```

> **[2nd-ed note]** Asterisk 22 verwendet Kommas als Argumenttrennzeichen (die Pipe-Form wurde in 1.6 als veraltet markiert). Die vollständige Syntax ist `DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])`, und der Standard-context, wenn keiner angegeben ist, ist `disa` (nicht "DISA"). Verifiziert mit `core show application DISA` im Asterisk 22.10.0 Labor.

## Begrenzung gleichzeitiger Anrufe

Die GROUP()-Funktion ermöglicht es Ihnen zu zählen, wie viele aktive Kanäle Sie gleichzeitig in einer Gruppe haben. Beispiel: Sie haben eine Niederlassung in Rio de Janeiro, wo Telefone dem Muster „_214X“ folgen. Dieser Standort wird über eine Standleitung bedient, wobei 64K für die Sprachbandbreite reserviert sind. In diesem Fall beträgt die maximal zulässige Anzahl von Anrufen 2 (G.729, 30r.2K pro Anruf). Um Anrufe nach Rio auf zwei zu begrenzen:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail ist ein computergestütztes Telefonbeantwortungssystem, das eingehende Sprachnachrichten aufzeichnet, sie auf der Festplatte speichert oder per E-Mail versendet. Manchmal gibt es ein Verzeichnis, in dem Sie Voicemail-Boxen nach Namen suchen können. In der Vergangenheit waren Voicemail-Systeme sehr teuer. Heute, mit IP-Telefonie, wird Voicemail zu einer Standardfunktion.

Um Voicemail zu konfigurieren, sollten Sie die folgenden Schritte durchlaufen.

**Schritt 1: Bearbeiten Sie `voicemail.conf` und legen Sie die allgemeinen Parameter fest.**

- `format` — Codec, der zum Aufzeichnen der Nachricht verwendet wird (z. B. wav49, wav, gsm)
- `serveremail` — Von wem die E-Mail-Benachrichtigung zu kommen scheint
- `maxmsg` — Maximale Anzahl von Nachrichten in der Mailbox; nach diesem Schwellenwert werden Nachrichten verworfen
- `maxsecs` — Maximale Länge einer Voicemail-Nachricht in Sekunden
- `minsecs` — Minimale Länge einer Nachricht in Sekunden; unter diesem Schwellenwert wird keine Nachricht aufgezeichnet
- `maxsilence` — Wie viele Sekunden Stille als Ende der Nachricht behandelt werden sollen

**Schritt 2: Bearbeiten Sie `voicemail.conf` und erstellen Sie die Mailboxen der Benutzer.**

### Voicemail.conf

Eine Mailbox wird mit einer Zeile pro Mailbox definiert, in der Form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

Die Felder sind:

- **MailboxID** — normalerweise die extension-Nummer
- **Pincode** — Passwort für den Zugriff auf das Voicemail-System
- **Full name** — wird von der Verzeichnisanwendung verwendet
- **E-mail** — Adresse für Voicemail-Benachrichtigung
- **Pager e-mail** — Adresse für Benachrichtigung über ein SMS-Gateway oder einen Pager
- **Options** — Mailbox-spezifische Optionen (dieselben Optionen wie in `[general]`, aber auf diese Mailbox angewendet)

Voicemail hat mehrere Optionen, die ihr Verhalten steuern. Vorerst bleiben wir bei den Standardoptionen und konzentrieren uns auf die Mailbox-Definition. Nach dem `[general]` Abschnitt in der Datei beginnen Sie mit der Konfiguration der Mailbox-IDs, jede in ihrem eigenen context. Beispiel:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Bitte prüfen Sie die erweiterten Optionen in der Datei `voicemail.conf`.

**Schritt 3: Konfigurieren Sie die Datei `extensions.conf`.**

Unten finden Sie die Anweisungen zum Erstellen der Subroutine und den Aufruf, der Voicemail in `extensions.conf` implementiert. Wir verwenden den Wert der Kanalvariable `${DIALSTATUS}`, um den Anruffluss zum richtigen Voicemail-Menü umzuleiten.

### Voicemail Subroutine

## Verwendung der Voicemailmain() Anwendung

Die Anwendung voicemailmain() wird verwendet, um die Voicemail-Mailbox zu konfigurieren. Benutzer können die Anwendung wählen, ihre Begrüßung aufnehmen und ihre Voicemail abhören. Um die Anwendung im dialplan aufzurufen, verwenden Sie:

```
exten=>9000,1,VoiceMailMain()
```

Unten finden Sie eine Liste der für die Anwendung verfügbaren Optionen.

### Voicemail Anwendungssyntax

Diese Anwendung ermöglicht es dem Anrufer, eine Nachricht für eine angegebene Liste von Mailboxen zu hinterlassen. Wenn mehrere Mailboxen angegeben sind, wird die Begrüßung aus der ersten angegebenen Mailbox genommen. Die dialplan-Ausführung stoppt, wenn die angegebene Mailbox nicht existiert. Die Syntax ist unten dargestellt:

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

In allen Fällen wird die Datei beep.gsm abgespielt, bevor die Aufnahme beginnt. Voicemail-Nachrichten werden im inbox-Verzeichnis gespeichert.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

Wenn ein Anrufer während der Ansage 0 (null) drückt, wird er zur ‚o‘ (out) extension im aktuellen Voicemail-context weitergeleitet. Dies kann verwendet werden, um zur Vermittlung zu gelangen. Wenn der Anrufer während der Aufnahme # drückt oder das Stille-Limit abläuft, wird die Aufnahme gestoppt und der Anruf geht zur nächsten Priorität über. Stellen Sie sicher, dass Sie den Anruf behandeln, nachdem die Voicemail abgespielt wurde, wie unten gezeigt.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Voicemail-Nachrichten als dringend markieren

Sie können einige Nachrichten als „dringend“ markieren. Dafür stehen zwei Methoden zur Verfügung:

- Übergeben Sie die Option ‚U‘ in der Anwendung voicemail()
- Geben Sie review=yes in der Datei voicemail.conf an. Wenn Sie diese Option verwenden, kann der Benutzer die Nachricht nach dem Aufzeichnen der Sprachanweisungen als dringend markieren.

## Voicemail per E-Mail versenden

In einigen Fällen (wie bei mir) verwenden wir die Anwendung voicemailmain() einfach nicht, um E-Mails zu lesen. Es ist einfacher und praktischer, alle Nachrichten mit angehängtem Audio per E-Mail zu versenden. Mithilfe der Parameter ‚attach‘ und ‚delete‘ können Sie alle E-Mails per E-Mail versenden und sie aus der Mailbox löschen.

```
attach=yes
delete=yes
```

Um Voicemail per E-Mail zu versenden, verwendet die Voicemail-Anwendung den Message Transfer Agent (MTA), eine Komponente Ihres Betriebssystems. Debian verwendet Exim als MTA. Die Anwendung, die die E-Mail versendet, ist im Parameter ‚mailcmd‘ definiert.

```
mailcmd =/usr/sbin/sendmail -t
```

In der Debian-Distribution von Linux ist der MTA Exim. Um Exim in Debian zu konfigurieren, verwenden Sie:

```
dpkg-reconfigure exim4-config
```

Sie können wählen, ob Ihr MTA eine E-Mail direkt über SMTP oder einen Smarthost (normalerweise der Mailserver Ihres Unternehmens) versenden soll. Prüfen Sie mit Ihrem E-Mail-Administrator den besten Weg, um E-Mails vom Asterisk-Server an Ihren E-Mail-Server zu senden.

## Anpassen der E-Mail-Nachricht

Sie können steuern, wie Nachrichten versendet werden, indem Sie die folgenden Variablen einrichten. Variablen für E-Mail-Betreff und E-Mail-Text:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Der E-Mail-Text und der Betreff werden aus einer Vorlage erstellt, die Sie im `[general]` Abschnitt von `voicemail.conf` festlegen. Sie können sowohl den Text als auch den Betreff ändern, aber die Größenbeschränkung der Nachricht beträgt 512 Bytes. In der Vorlage fügt `\n` einen Zeilenumbruch ein und `\t` fügt einen Tabulator ein.

Das `emailsubject` Beispiel unten ist unkompliziert. Das `emailbody` Beispiel liegt sehr nahe am Standard; der Standard zeigt nur den CIDNAME, wenn er nicht null ist, andernfalls die CIDNUM oder "an unknown caller", wenn beide null sind.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Web-Schnittstelle

Es gibt ein Perl-Skript in der Quell-Distribution namens `vmail.cgi`, das sich unter `contrib/scripts/vmail.cgi` im Asterisk-Quellbaum befindet (es wird immer noch mit Asterisk 22 ausgeliefert). Der Befehl `make install` installiert diese Schnittstelle nicht; Sie müssen `make webvmail` aus dem Quellverzeichnis ausführen. Dieses Skript erfordert den Perl-Befehlsinterpreter und einen Webserver (wie Apache), der auf dem Server installiert ist.

```
make webvmail
```

Das `make webvmail` Ziel installiert das Skript (setuid root) in das CGI-Verzeichnis Ihres Webservers (`HTTP_CGIDIR`) und kopiert die unterstützenden Bilder von `images/*.gif` nach `HTTP_DOCSDIR/_asterisk` (standardmäßig `/var/www/html/_asterisk`). Wenn diese Pfade nicht mit Ihrem Webserver-Layout übereinstimmen, bearbeiten Sie die Variablen `HTTP_CGIDIR` und `HTTP_DOCSDIR` im obersten `Makefile`, bevor Sie das Ziel ausführen.

## Voicemail-Benachrichtigung

Sie können Voicemail so konfigurieren, dass eine Benachrichtigung an Ihr Telefon gesendet wird, wenn Sie eine neue Voicemail haben. In Asterisk 22 funktioniert die Message Waiting Indication (MWI) mit PJSIP- und SIP-Telefonen sowie DAHDI-Telefonen. Um eine ungehörte Voicemail anzuzeigen, kann eine Anzeigeleuchte blinken oder das Telefon kann einen Signalton abspielen. Sie müssen die Mailbox in der entsprechenden Kanal-Konfigurationsdatei konfigurieren. Beispiel: `pjsip.conf` (im endpoint-Abschnitt):

```
mailboxes=8590
```

> **[2nd-ed note]** In PJSIP wird der Mailbox-Hinweis mit der `mailboxes` Option innerhalb des `[endpoint]` Abschnitts von `pjsip.conf` gesetzt, anstatt `mailbox=` in `sip.conf`. MWI-Abonnements werden von `res_pjsip_mwi` gehandhabt. Prüfen Sie die genaue Konfigurationssyntax für Asterisk 22.

![Die Comedian Mail Web-Schnittstelle (`vmail.cgi`): der Asterisk Web-Voicemail-Login — geben Sie Ihre Mailbox und Ihr Passwort ein, um Voicemail über einen Browser abzuspielen, zu speichern, weiterzuleiten oder zu löschen. Es wird immer noch mit Asterisk 22 ausgeliefert und mit `make webvmail` installiert.](../images/10-dialplan-advanced-features-img14.png)

### Labor: Nachrichtenbenachrichtigung im Telefon

Dieses Labor wurde mit einem SIP-softphone getestet. 1. Bearbeiten Sie `pjsip.conf` und fügen Sie `mailboxes=4401` im endpoint-Abschnitt für das Gerät mit dem Namen 4401 hinzu. 2. Bearbeiten Sie die extensions.conf und erstellen Sie eine extension, um eine Voicemail an 4401 extensions aufzunehmen.

```
exten=9008,n,voicemail(b4401)
```

3. Gehen Sie zur CLI > Konsole und laden Sie neu. 4. Öffnen Sie im SipPulse Softphone die SIP-Kontoeinstellungen und aktivieren Sie die Voicemail-Prüfung (message-waiting) für das Konto. 5. Wählen Sie 9008 und hinterlassen Sie eine Nachricht. 6. Beobachten Sie das Nachrichtensymbol auf dem Telefon.

## Verwendung der directory-Anwendung

Diese Anwendung ermöglicht es Ihnen, schnell einen Benutzer zum Wählen zu finden. Die Liste der Namen und entsprechenden extensions wird aus der Voicemail-Konfigurationsdatei voicemail.conf abgerufen. Die Syntax für die Anwendung kann mithilfe von core show application directory angezeigt werden:

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

### Labor: Verwendung der directory-Anwendung

1. Bearbeiten Sie die voicemail.conf-Datei, um zwei extensions im dialplan hinzuzufügen

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Erstellen Sie diese extensions in Ihrem dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Gehen Sie zur Konsole und laden Sie neu 4. Wählen Sie 9006 und nehmen Sie einen Namen für jede extension (4400, 4401) auf 5. Wählen Sie 9007 und wählen Sie die drei Buchstaben des Nachnamens für eine extension (Eas=327). Wenn dies die richtige Option ist, drücken Sie ‚1‘, um zum Namen weiterzuleiten.

## Labor: Alles zusammenfügen

Bisher haben Sie mehrere dialplan-Konzepte kennengelernt. Lassen Sie uns alle Anwendungen, Funktionen und Konzepte in einem dialplan-Beispiel zusammenfügen, damit Sie verstehen, wie sie zusammen verwendet werden. Lassen Sie uns Sie durch die gesamte PBX-Konfiguration für das untenstehende Szenario führen.

- 4 analoge trunks
- 16 SIP-basierte extensions
- 3 Dienstklassen:
    - restrict (intern, lokal und 1-800)
    - ld (Ferngespräch)
    - ldi (international)
- Nachricht außerhalb der Geschäftszeiten
- Auto Attendant

### Schritt 1 – Konfigurieren der Kanäle

Analoge trunks (chan_dahdi.conf) Zuerst konfigurieren wir die analogen trunks in der DAHDI-Kanal-Konfigurationsdatei chan_dahdi.conf. In diesem Fall verwenden wir eine T400P Digium-Karte mit 4 FXO-Schnittstellen. Nehmen wir an, dass der Treiber bereits geladen ist und die Treiber-Konfigurationsdatei (/etc/dahdi/system.conf) korrekt konfiguriert ist.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

SIP-Kanäle (pjsip.conf) Wir haben die dialplan-Nummerierung von 2000 bis 2099 gewählt. Zwei Codecs werden verwendet: G.729 und G.711 ulaw. Der erste wird für Telefone verwendet, die Asterisk über das Internet oder WAN nutzen, während der zweite für Telefone verwendet wird, die das lokale Netzwerk nutzen. In `pjsip.conf` werden wir entscheiden, welche Geräte zu welcher Dienstklasse (restrict, ld, ldi) gehören. Um die Anfälligkeit für Brute-Force-Angriffe zu verringern, verwenden wir die MAC-Adressen der Telefone als Gerätenamen. Ich rate dringend dazu, starke Passwörter zu verwenden, um Brute-Force-Angriffe zu vermeiden!

Wir definieren einen Transport und drei wiederverwendbare Vorlagen — eine endpoint-Basis mit den geteilten Codecs, eine userpass-Authentifizierung und einen einzelnen Kontakt-AOR — und hängen dann jedes Gerät an die Vorlagen an und überschreiben nur das, was sich unterscheidet (seinen Dienstklassen-context und die Anmeldeinformationen). `host=dynamic` wird zu einem AOR, bei dem sich das Telefon registriert, und `directmedia` wird zu `direct_media`:

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

### Schritt 2 – Konfigurieren des dialplan

Lassen Sie uns nun mit der Konfiguration der extensions.conf beginnen. Definieren Sie interne extensions und lokales Wählen

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Definieren Sie LD (Ferngespräch)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Definieren Sie internationale Anrufe

```
[ldi)
include=> ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Schritt 3 - Anrufe mithilfe eines Auto-Attendant entgegennehmen

Um Anrufe entgegenzunehmen, verwenden Sie zwei contexts. Der erste ist für den Betrieb während der normalen Geschäftszeiten, wo der Anruf von einem Auto-Attendant entgegengenommen wird. Der zweite ist für außerhalb der Geschäftszeiten, wo der Anrufer eine Nachricht erhält wie „Sie haben die Firma XYZ angerufen, unsere normalen Geschäftszeiten sind von 08:00 Uhr bis 18:00 Uhr; wenn Sie die Ziel-extension-Nummer kennen, können Sie versuchen, sie jetzt zu wählen oder aufzulegen.“ Menüs: Normale Geschäftszeiten, Außerhalb der Geschäftszeiten In den Menüs unten spielt das System eine Nachricht ab, die den Anrufer warnt, dass die Firma außerhalb der regulären Arbeitszeiten erreicht wurde, und ermöglicht es dem Anrufer, die Ziel-extension-Nummer zu wählen (jemand könnte nach den regulären Arbeitszeiten arbeiten).

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

Menüs: Hauptmenü und Vertrieb Während der normalen Geschäftszeiten wird der Anruf von einem Auto-Attendant-Menü beantwortet, das eine Nachricht erhält wie „Willkommen bei der Firma XYZ; wählen Sie 1 für Vertrieb, 2 für technischen Support, 3 für Schulungen oder die gewünschte extension-Nummer“.

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

Mit all diesen Anweisungen ist die Funktionalität Ihres Wählplans nun bereit. Im nächsten Abschnitt zeigen wir Ihnen, wie Sie die PBX bedienen.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, wie Sie Anrufe mithilfe eines IVR oder eines Auto-Attendant entgegennehmen. Sie haben das Konzept der context-Inklusion studiert und einige Beispiele implementiert. Subroutinen wurden verwendet, um wiederholtes Tippen zu vermeiden, und die Asterisk-Datenbank basierend auf der Berkley DB-Engine wurde für Funktionen verwendet, die Datenspeicherung erfordern (z. B. Anrufweiterleitung, Nicht-Stören, Blacklists). Schließlich haben Sie gelernt, wie man Verhalten außerhalb der Geschäftszeiten implementiert und einen vollständigen dialplan mithilfe dieser Konzepte implementiert.

## Quiz

1. Ein zeitabhängiger context-include verwendet die Form `include => context,<times>,<weekdays>,<mdays>,<months>`. Was macht `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Führt die extensions Montag bis Freitag, 08:00 bis 18:00 Uhr aus
   - B. Führt die Optionen jeden Tag in allen Monaten aus
   - C. Nichts; das Format ist ungültig
2. Im modernen Asterisk (einschließlich Asterisk 22) werden die Felder eines zeitbasierten `include =>` und von `GotoIfTime()` durch welches Zeichen getrennt?
   - A. Die Pipe `|`
   - B. Das Komma `,`
   - C. Das Semikolon `;`
   - D. Der Schrägstrich `/`
3. Um mehrere Kanäle gleichzeitig zu wählen (sie gleichzeitig klingeln zu lassen), trennen Sie sie innerhalb von `Dial()` mit dem ___ Zeichen.
4. Ein Sprachmenü, das eine Ansage abspielt, während darauf gewartet wird, dass der Anrufer eine extension wählt, wird normalerweise mit der ___ Anwendung erstellt.
5. Sie können den Inhalt einer anderen Datei innerhalb von `extensions.conf` mithilfe der ___ Anweisung einbinden (Hinweis: dies ist anders als die `include =>` context-Anweisung).
6. In Asterisk 22 wird die eingebaute AstDB-Datenbank unterstützt durch:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Wenn Sie `Dial(type1/identifier1&type2/identifier2)` verwenden, wählt Asterisk jeden Kanal nacheinander und wartet 20 Sekunden zwischen ihnen.
   - A. Falsch
   - B. Wahr
8. Bei der Background()-Anwendung müssen Sie warten, bis die Nachricht zu Ende gespielt wurde, bevor Sie eine DTMF-Ziffer drücken können, um eine Option zu wählen.
   - A. Falsch
   - B. Wahr
9. Gegeben die Syntax `Goto([[context,]extension,]priority)`, welche der folgenden sind gültige Aufrufe der Goto()-Anwendung? (markieren Sie alle zutreffenden)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Um einen einzelnen Schlüssel aus der AstDB im Asterisk 22 dialplan zu löschen, verwenden Sie:
    - A. Die `DBdel()` Anwendung
    - B. Die `DB_DELETE()` Funktion
    - C. Die `DBdeltree()` Anwendung
    - D. Die `LookupBlacklist()` Anwendung

**Antworten:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
