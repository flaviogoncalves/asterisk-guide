# Erweiterte Funktionen des Dialplans

Kapitel 3 behandelte die Grundlagen eines Dialplans. Aus didaktischen Gründen haben wir nicht alle Funktionen erklärt, sondern nur einige der wichtigsten. Dieses Kapitel wird tiefer in den Dialplan eintauchen, fortgeschrittene Techniken, neue Anwendungen und Konzepte beschreiben.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Ihre Nebenstellen‑Einträge zu vereinfachen
- Sicherheit im Dialplan und das Filtern von Nebenstellen anzugehen
- Anrufe über ein IVR‑Menü entgegenzunehmen
- Subroutinen zu verwenden, um unnötige Neuschreibungen zu vermeiden
- Einige Dialplan‑Sicherheitsmaßnahmen mit „Include“ umzusetzen
- Follow‑Me mit AsteriskDB zu implementieren
- Nach‑Arbeits‑Verhalten in Ihrer PBX zu implementieren
- Den switch‑Befehl zu nutzen, um zu einer anderen PBX zu transferieren
- Den Privacy Manager zu implementieren
- Voicemail zu implementieren
- Ein Firmenverzeichnis zu implementieren

## Simplifying your Dial Plan

You can simplify your dial plan using the keyword “same” to define an extension. It should reduce the number of typos in the dial plan. Check the example below:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan Security

Ein Fehler wurde im Asterisk-Dialplan entdeckt, der es einem Benutzer ermöglicht, einen neuen Kanal und eine Durchwahlnummer in Ihren Dialplan einzuschleusen. Angenommen, Sie haben die folgende Zeile in Ihrem Server `exten=>_X.,1,Dial(PJSIP/${EXTEN})` und ein bösartiger Benutzer wählt die Nummer `3000&DAHDI/1/011551123456789` im Softphone. Das SIP‑Protokoll akzeptiert standardmäßig beliebige alphanumerische Zeichen, sodass die gewählte Durchwahl tatsächlich zwei Anrufe auslöst: einen für den Kanal PJSIP/3000 und einen für den Kanal DAHDI/011551123456789, eine internationale Nummer. Somit kann jeder Benutzer mit Zugriff auf eine Durchwahl tatsächlich überall auf der Welt anrufen. Der einfachste Weg, dieses Verhalten zu vermeiden, besteht darin, die Nummern vor dem Aufruf der Dial‑Anwendung zu filtern. Die Funktion FILTER() ist hierfür sehr praktisch. Beispiel:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

Die Anwendung filter ermöglicht es Ihnen, alle Zeichen aus der gewählten Nummer zu entfernen, außer den Ziffern 0 bis 9. Weitere Informationen finden Sie in der Datei README‑SERIOUSLY.bestpractices.txt, die von Asterisk bereitgestellt wird.

## Entgegennahme von Anrufen über ein IVR-Menü.

Im letzten Abschnitt haben Sie alle Anrufe über DID oder Weiterleitung zum Operator entgegengenommen. Jetzt lernen Sie, wie man ein IVR‑Menü implementiert und einen Auto‑Attendant‑Dienst erstellt. Bevor wir zu den Details kommen, betrachten wir einige neue Anwendungen. Wir haben die Ausgabe des Befehls `core show application` unten eingefügt, um es den Lesern zu erleichtern. Sie können diese Beschreibungen selbst mit `core show application <application_name>` erhalten.

### Die Background()-Anwendung

Dieses Anwendungsprogramm spielt die angegebene Liste von Dateien ab, während es darauf wartet, dass vom anrufenden Kanal eine Durchwahl gewählt wird. Um nach dem Abspielen der Dateien weiterhin auf Ziffern zu warten, sollte die Anwendung **WaitExten** verwendet werden. Die Option **langoverride** gibt ausdrücklich an, welche Sprache für die angeforderten Audiodateien versucht werden soll. Jeder angegebene Kontext ist der Dialplan‑Kontext, den diese Anwendung beim Verlassen zu einer gewählten Durchwahl verwendet. Wenn eine der angeforderten Audiodateien nicht existiert, wird die Anrufverarbeitung beendet. Optionen:

- s - Veranlasst, dass die Wiedergabe der Nachricht übersprungen wird, wenn der Kanal nicht im 'up'‑Zustand ist (d. h., er wurde noch nicht beantwortet). Wenn das passiert, gibt die Anwendung sofort zurück.  
- n - Den Kanal nicht beantworten, bevor die Dateien abgespielt werden.  
- m - Nur abbrechen, wenn ein gedrücktes Zeichen einer einstelligen Nebenstelle im Ziel‑Kontext entspricht.

### Die Record()-Anwendung

Diese Anwendung zeichnet vom Kanal in einen angegebenen Dateinamen auf. Wenn die Datei bereits existiert, wird sie überschrieben.

![10-dialplan-advanced-features Abbildung 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' ist das Format des Dateityps, der aufgenommen werden soll (wav, gsm, etc).
- 'silence' ist die Anzahl der Sekunden Stille, die erlaubt sind, bevor zurückgekehrt wird.
- 'maxduration' ist die maximale Aufnahmedauer in Sekunden; fehlt sie oder ist null, gibt es kein Maximum.
- 'options' kann eines der folgenden Zeichen enthalten:
    - `a` — fügt einer bestehenden Aufnahme hinzu, anstatt sie zu ersetzen
    - `n` — nicht beantworten, aber trotzdem aufnehmen, wenn die Leitung noch nicht beantwortet ist
    - `q` — leise (kein Signalton wird abgespielt)
    - `s` — überspringt die Aufnahme, wenn die Leitung noch nicht beantwortet ist
    - `t` — verwendet die alternative `*` Beendetaste (DTMF) anstelle der Standard‑`#`
    - `x` — ignoriert alle Beendetasten (DTMF) und nimmt bis zum Auflegen weiter auf

If filename contains %d, these characters will be replaced with a number incremented by one each time the file is recorded. Use `core show file formats` to see the available formats on your system. The user can press # to terminate the recording and continue to the next priority. If the user hangs up during a recording, all data will be lost and the application will terminate.

### Die Playback()-Anwendung

Diese Anwendung gibt angegebene Dateinamen wieder (ohne Erweiterung). Optionen können ebenfalls nach einem Pipe‑Symbol angegeben werden. Die Option 'skip' bewirkt, dass die Wiedergabe der Nachricht übersprungen wird, wenn der Kanal nicht im 'up'-Zustand ist (d. h. noch nicht beantwortet wurde).

![10-dialplan-advanced-features Abbildung 2](../images/10-dialplan-advanced-features-img02.png)

![10-dialplan-advanced-features Abbildung 3](../images/10-dialplan-advanced-features-img03.png)

Wenn 'skip' angegeben ist, beendet die Anwendung sofort, falls der Kanal nicht abgehoben ist. Andernfalls, sofern nicht 'noanswer' angegeben ist, wird der Kanal beantwortet, bevor der Sound abgespielt wird. Nicht alle Kanäle unterstützen das Abspielen von Nachrichten, während sie noch am Hörer liegen. Wenn 'j' angegeben ist, springt die Anwendung zu Priorität n+101, wenn die Datei nicht existiert, falls vorhanden. Diese Anwendung setzt nach Abschluss die folgende Kanalvariable:

- PLAYBACKSTATUS — der Status des Wiedergabeversuchs als Textzeichenkette, einer von:
    - `SUCCESS`
    - `FAILED`

### Die Read()-Anwendung

Diese Anwendung liest eine vorbestimmte Anzahl von Zeichenziffern, eine bestimmte Anzahl von Malen, vom Benutzer in die angegebene Variable ein.

- filename -- Datei, die abgespielt wird, bevor Ziffern oder Ton mit Option i gelesen werden
- maxdigits -- maximal zulässige Anzahl von Ziffern. Stoppt das Einlesen, nachdem maxdigits eingegeben wurden (ohne dass der Benutzer die #‑Taste drücken muss). Standardwert ist 0 - kein Limit - um auf das Drücken der #‑Taste zu warten. Jeder Wert unter 0 bedeutet dasselbe. Der maximal zulässige Wert ist 255.

![10-dialplan-advanced-features Abbildung 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features Abbildung 5](../images/10-dialplan-advanced-features-img05.png)

- option -- options are `s`, `i`, `n`:
    - `s` — sofort zurückkehren, wenn die Leitung nicht belegt ist
    - `i` — Datei als Hinweiston von Ihrem `indications.conf` abspielen
    - `n` — Ziffern einlesen, selbst wenn die Leitung nicht belegt ist
- attempts -- wenn größer als 1, die Anzahl der Versuche, die unternommen werden, falls keine Daten eingegeben werden
- timeout -- Eine ganze Zahl von Sekunden, die auf eine Ziffernantwort gewartet wird. Wenn größer als 0, überschreibt dieser Wert den Standard‑Timeout.

Die read()-Anwendung sollte die Verbindung trennen, wenn die Funktion fehlschlägt oder einen Fehler erzeugt.

### Die Gotoif()-Anwendung

This application will cause the calling channel to jump to the specified location in the dial plan based on the evaluation of the given condition. The channel will continue at labeliftrue if the condition is true, or 'labeliffalse' if the condition is false. The labels are specified with the same syntax as that used within the Goto application. If the label chosen by the condition is omitted, no jump is performed; rather, the execution continues with the next priority in the dial plan.

### Lab: Aufbau eines IVR-Menüs Schritt für Schritt

Lassen Sie uns ein IVR‑Menü mit der folgenden Funktionalität erstellen. Beim Anrufen spielt das IVR eine Audiodatei mit der Meldung „Willkommen bei der XYZ Corporation; drücken Sie 1 für Vertrieb, 2 für technischen Support, 3 für Schulungen, oder warten Sie, um mit einem Vertreter zu sprechen.“ ab. Die Ziffern leiten den Anrufer wie folgt weiter:

- `1` — Weiterleitung an den Vertrieb (PJSIP/4001)
- `2` — Weiterleitung an den technischen Support (PJSIP/4002)
- `3` — Weiterleitung an die Schulung (PJSIP/4003)
- No digit pressed — Weiterleitung an den Operator (PJSIP/4000)

**Schritt 1 – Eingabeaufforderungen aufzeichnen**

Lassen Sie uns eine Nebenstelle erstellen, um die Ansagen aufzunehmen. Um eine Ansage aufzunehmen, wählen Sie von einem Softphone zu `9003<filename>` (zum Beispiel `9003welcome`). Wenn Sie den Piepton hören, beginnen Sie mit der Aufnahme; drücken Sie `#`, um zu stoppen. Sie hören einen Piepton, und das System spielt die aufgezeichnete Ansage ab.

**Schritt 2 – Erstelle die Menülogik**

Beim Wählen der Durchwahl 9004 springt die Verarbeitung zum Menü in der `s` Durchwahl, Priorität 1.

### Matching as you dial

Dies ist ein Unternehmens‑Setup‑Menü zum Empfangen von Anrufen. Die `Background()` Anwendung spielt die Willkommensansage ab und wartet dann auf Ziffern, wobei das, was der Anrufer wählt, mit den im aktuellen Kontext definierten Nebenstellen abgeglichen wird.

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

Wenn Sie dieses Unternehmen anrufen, wird zuerst die Begrüßungsnachricht abgespielt. Danach wartet Asterisk darauf, dass eine Ziffer gewählt wird:

| Gewählte Nummer | Asterisk‑Aktion |
|-----------------|-----------------|
| 1 | Ruft sofort `Dial(DAHDI/1)` an |
| 2 | Wartet auf das Timeout, dann ruft `Dial(DAHDI/2)` an |
| 21 | Ruft sofort `Dial(DAHDI/3)` an |
| 22 | Ruft sofort `Dial(DAHDI/4)` an |
| 3 | Wartet auf das Timeout, dann trennt die Verbindung |
| 31 | Ruft sofort `Dial(DAHDI/5)` an |
| 32 | Ruft sofort `Dial(DAHDI/6)` an |

Es ist wichtig, Mehrdeutigkeiten in den Menüs zu vermeiden. Jeder möchte schnell beantwortet werden. Aus diesem Grund sollten Sie die Zahlen 2, 21 oder 22 nicht verwenden.

### Labor: Verwendung der Read()-Anwendung

Bitte probieren Sie das Labor mit der read()-Anwendung aus. Read akzeptiert Ziffern vom Benutzer und fügt sie in die angegebene Variable ein; Sie können anschließend die gotoif‑Anwendung verwenden, um den Anruf umzuleiten.

## Kontext-Einbindung

Ein Kontext kann den Inhalt eines anderen Kontextes einbinden. Im obigen Beispiel kann jeder Kanal jede Nebenstelle im internen Kontext wählen, aber nur der Kanal 4003 kann internationale Nebenstellen wählen. Sie können die Kontext‑Einbindung nutzen, um die Erstellung des Dialplans zu vereinfachen. Durch die Kontext‑Einbindung können Sie steuern, wer Zugriff auf welche Nebenstellen hat.

### Fehlersuche bei der Meldung „number not found“

Es kommt sehr häufig vor, dass die Meldung „number not found“ angezeigt wird. Viele Menschen verwechseln das Konzept der eingebundenen Kontexte, weil es nicht intuitiv ist. Als Faustregel gehen Sie zuerst zur Konfigurationsdatei des eingehenden Kanals, z. B. `pjsip.conf`, `chan_dahdi.conf` und `iax.conf`, und bestimmen den aktuellen Kontext. Dann gehen Sie zum Dialplan in der Datei extensions.conf und prüfen, ob die gewählte Nummer in diesem Kontext gefunden werden kann. Wenn nicht, ist etwas mit Ihrem Dialplan falsch. Die goldenen Regeln für Kontexte lauten: 1. Ein Kanal kann nur Nummern innerhalb desselben Kontextes wie der Kanal wählen. 2. Der Kontext, in dem der Anruf verarbeitet wird, ist in der Konfigurationsdatei des eingehenden Kanals definiert (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`).

## Verwendung der switch-Anweisung

Sie können die Dialplan‑Verarbeitung an einen anderen Server senden, indem Sie den switch‑Befehl verwenden. Sie benötigen den Namen und den Schlüssel des anderen Servers. Der Kontext ist der Zielkontext.

![10-dialplan-advanced-features Abbildung 6](../images/10-dialplan-advanced-features-img06.png)

## Dialplan-Verarbeitungsreihenfolge

Wenn Asterisk einen eingehenden Anruf erhält, schaut es im durch den Kanal definierten Kontext nach. In manchen Fällen, wenn mehr als ein Muster zur gewählten Nummer passt, kann Asterisk den Anruf nicht exakt so verarbeiten, wie Sie es erwarten. Sie können die Reihenfolge der Übereinstimmungen mit dem CLI‑Befehl `dialplan show` anzeigen. Beispiel: Angenommen, Sie möchten die Nummer 912 zu einem analogen Trunk (DAHDI/1) leiten und alle anderen Nummern, die mit 9 beginnen, zu einem anderen analogen Trunk (DAHDI/2). Dann würden Sie etwa Folgendes schreiben:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

Wenn zwei Muster zu einer Extension passen, können Sie mit den eingebundenen Kontexten steuern, welche Extension zuerst verarbeitet wird. Ein eingebundener Kontext wird später verarbeitet als ein Muster im selben Kontext.

## Die #INCLUDE-Anweisung

Sollten wir eine große Datei oder mehrere Dateien verwenden? Sie können die #include <filename>-Anweisung verwenden, um andere Dateien in Ihre extensions.conf einzubinden. Zum Beispiel könnten wir eine users.conf für lokale Benutzer und eine services.conf für spezielle Dienste erstellen. Achten Sie darauf, #include <filename> nicht zu verwechseln mit dem

```
include=>context statement.
```

## Subroutinen mit GOSUB

In älteren Versionen von Asterisk gab es den Befehl Macro. Dieser Befehl wurde vor langer Zeit zugunsten von GOSUB veraltet. Wir zeigen hier, wie man Subroutinen für die Voicemail‑Verarbeitung auf einfache und geordnete Weise erstellt. Befehlsformat:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

Der Befehl GOSUB ist seit Asterisk 1.6 verfügbar und unterstützt das Übergeben von Argumenten (innerhalb der Subroutine verfügbar als `${ARG1}`, `${ARG2}` usw.). Mit Argumenten ist es nun möglich, die alten Macro‑Befehle vollständig zu ersetzen. Macros (`app_macro`) wurden in Asterisk 21 entfernt; Sie müssen GOSUB für Subroutinen verwenden.

### Erstellen der Subroutine

Die Definition ist sehr ähnlich. Betrachten Sie die unten definierte Subroutine für Voicemail mit dem Namen stdexten (wählen Sie einen Namen, der Ihnen gefällt). Nachdem der Befehl Dial mit dem ersten Argument (Name des Kanals) aufgerufen wurde, prüfen wir den ${DIALSTATUS}, um die Anruflogik zum nächsten Schritt zu leiten.

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

## Using Asterisk DB

Um Anrufweiterleitung und Sperrlisten zu implementieren, benötigen wir eine Möglichkeit, Daten zu speichern und wiederherzustellen. Glücklicherweise stellt Asterisk einen Mechanismus zum Speichern und Abrufen von Daten aus einer eingebauten Datenbank namens AstDB bereit. In modernem Asterisk (einschließlich Asterisk 22) wird AstDB von **SQLite3** unterstützt (die Datei `/var/lib/asterisk/astdb.sqlite3`); Asterisk 1.8 und frühere Versionen nutzten Berkeley DB v1. Dies ist ähnlich der Windows‑Registrierungsdatenbank, die das hierarchische Konzept von Familien und Schlüsseln verwendet. Die Daten bleiben zwischen Asterisk‑Neustarts erhalten. Die Family/Key‑API ist von dem älteren Backend unverändert; nur das Dateispeicherformat hat sich geändert.

### Functions, applications, and CLI commands

Es gibt einige Funktionen, Anwendungen und CLI‑Befehle, die mit AstDB arbeiten:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Beispiele:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

Einige Anwendungen können verwendet werden, um AstDB zu manipulieren:

- DB_DELETE(<family/key>) — Funktion, die einen einzelnen Schlüssel zurückgibt und löscht
- DBdeltree(<family>) — Anwendung, die eine ganze Familie/Unterbaum löscht

Die alte `DBdel()`‑Anwendung existiert in Asterisk 22 nicht mehr. Löschen Sie einen einzelnen Schlüssel mit der `DB_DELETE()`‑Dialplan‑Funktion — z. B. `Set(x=${DB_DELETE(family/key)})` oder, als Schreiboperation, `Set(DB_DELETE(family/key)=)`. `DBdeltree()` (löscht eine ganze Familie/Unterbaum) ist weiterhin eine Anwendung.

Es ist ebenfalls möglich, CLI‑Befehle zum Setzen und Löschen von Schlüsseln zu verwenden:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementing Call Forward, DND, and Blacklists

In diesem Beispiel lernen Sie, wie man sofortige Anrufweiterleitung und Anrufweiterleitung bei Besetzt implementiert. Wir verwenden *21* zum Programmieren der sofortigen Anrufweiterleitung und *61* zum Programmieren der Anrufweiterleitung bei Besetzt‑Status. Zum Abbrechen der Programmierung verwenden Sie #21# bzw. #61#. Nutzen Sie das obige Beispiel, um die Datenbank zu füllen. Verwendete Familien:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

Versuchen Sie, die Datenbank zu füllen, indem Sie wählen:

- *21* (Ziel‑Durchwahl für sofortige Anrufweiterleitung)
- *61* (Ziel‑Durchwahl für Anrufweiterleitung bei Besetzt)
- *41* (Durchwahl, die auf Nicht‑Stören gesetzt wird)

Verwenden Sie den CLI‑Befehl `database show`, um die hinzugefügten Familien, Schlüssel und Werte zu sehen.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward, Blacklist, DND

Die Unterroutine prüft, ob die Datenbank die Schlüssel‑Wert‑Paare enthält, die CFIM, CFBS oder DND entsprechen, und verarbeitet sie dann entsprechend. Die folgende Unterroutine ruft die Wählroutine auf:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Using a blacklist

Die alte `LookupBlacklist()`‑Anwendung wurde **entfernt** aus Asterisk (sie verschwand zusammen mit dem veralteten „priority+101 jump“-Mechanismus). In Asterisk 22 bauen Sie eine Blacklist direkt mit der `DB_EXISTS()`‑Funktion (die sowohl nach einem Schlüssel sucht als auch, wenn gefunden, dessen Wert in `${DB_RESULT}` bereitstellt) plus `GotoIf`. Speichern Sie jede gesperrte Nummer als Schlüssel in einer `blacklist`‑Familie und prüfen Sie die Caller‑ID am Anfang Ihres eingehenden Kontextes:

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

`DB_EXISTS(blacklist/${CALLERID(num)})` liefert `1`, wenn die Nummer des Anrufers in der Datenbank vorhanden ist (der Anruf wird in den `blocked`‑Kontext geleitet) und `0` andernfalls, sodass der Anruf zum normalen `Dial()` fortfährt.

Um eine Nummer zur Blacklist hinzuzufügen, können wir dieselbe Ressource wie zuvor verwenden, indem wir *31* gefolgt von den zu sperrenden Durchwahlen wählen. Um eine Nummer aus der Blacklist zu entfernen, sollten Sie #31# gefolgt von der zu entfernenden Nummer wählen.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

Sie können die Nummern auch über die Konsolen‑CLI in die Blacklist eintragen:

```
*CLI>database put blacklist <name/number> 1
```

Hinweis: Mit dem Schlüssel kann jeder Wert verknüpft werden. Der `DB_EXISTS()`‑Test sucht nach dem Schlüssel, nicht nach dem Wert. Um die Nummer aus der Blacklist zu löschen, können Sie verwenden:

```
*CLI>database del blacklist <name/number>
```

## Time-based contexts

In der folgenden Abbildung haben wir einen Dialplan mit drei Kontexten. Der [incoming] Kontext ist dort, wo die Anrufe üblicherweise empfangen werden. Wir haben vier Zeilen eingefügt, die das Verhalten abhängig von der Systemzeit ändern, wie unten beispielhaft dargestellt:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modernes Asterisk (einschließlich 22) trennt die time-include Felder mit **Kommas**, nicht mit Pipes. Die veraltete Pipe‑Form (`include => context|times|weekdays|mdays|months`) wird als einfacher Literal‑Kontextname geparst und führt stillschweigend dazu, dass keine Zeitbedingung angewendet wird.

Während der regulären Arbeitszeiten wird die Verarbeitung zum mainmenu umgeleitet, wo wahrscheinlich ein IVR aufgerufen wird, um den eingehenden Anruf zu bearbeiten. Findet der Anruf außerhalb der Geschäftszeiten statt, wird die im ${SECURITY}‑Variable definierte Sicherheits‑Durchwahl gewählt. Antwortet die Sicherheits‑Durchwahl nicht, wird der Anruf an die Mailbox des Operators weitergeleitet.

![10-dialplan-advanced-features Abbildung 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features Abbildung 12](../images/10-dialplan-advanced-features-img12.png)

## Time-based messages using gotoiftime()

The GotoIfTime() syntax is shown below.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

In Asterisk 22 the field separator is a **comma**, not a pipe (the pipe form was deprecated in Asterisk 1.6). An optional `timezone` field is supported, and each branch label uses the usual `[[context,]extension,]priority` form.

This application can replace the time-based context and seems easier to understand and read. You can specify the time as follows:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Names for days and months are not case sensitive.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

The previous statement transfers the processing to the extension s in the normalhours context if the call is between 08:00AM and 06:00PM from Monday to Friday.

## Using DISA to get a new dial tone

DISA, oder „direct inward system access“, ist ein System, das Benutzern einen zweiten Wähltton ermöglicht. Es erlaubt den Benutzern, erneut zu einem anderen Ziel zu wählen. Es wird häufig von Technikern verwendet, wenn sie am Wochenende Ferngespräche für den technischen Support tätigen; anstatt von zu Hause aus direkt zum Ziel zu wählen, rufen sie die DISA‑Nummer des Büros an, erhalten einen Wähltton und wählen dann das Ziel. Die Ferngesprächskosten entstehen beim Unternehmen statt beim Heimtelefon.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Beispiel:

```
exten => s,1,DISA(no-password,default)
```

Mit der vorherigen Anweisung wählt der Benutzer die PBX und – ohne ein Passwort zu benötigen – erhält einen Wähltton. Jeder Anruf, der DISA verwendet, wird im Kontext `default` verarbeitet. Die Argumente für diese Anwendung umfassen ein globales Passwort oder ein individuelles Passwort in einer Datei. Wenn kein Kontext angegeben ist, wird der Kontext `disa` angenommen. Wenn Sie eine Passwortdatei verwenden, muss der vollständige Pfad angegeben werden. Für das externe Wählen über DISA kann ebenfalls eine Caller‑ID angegeben werden. Beispiel:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 verwendet Kommas als Argumenttrenner (die Pipe‑Form wurde in 1.6 veraltet). Das erste Argument ist entweder ein einzelner Passcode oder der Pfad zu einer Passcode‑Datei, und der Standard‑Kontext, wenn keiner angegeben wird, ist `disa`.

## Limit simultaneous calls

Die GROUP()-Funktion ermöglicht es Ihnen, zu zählen, wie viele aktive Kanäle Sie gleichzeitig in einer Gruppe haben. Beispiel: Sie haben eine Niederlassung in Rio de Janeiro, wo Telefone dem Muster “_214X” folgen. Dieser Standort wird über eine Leitungsverbindung bedient, mit 64K reserviert für Sprachbandbreite. In diesem Fall ist die maximale Anzahl zulässiger Anrufe 2 (G.729, etwa 31,2K pro Anruf). Um Anrufe nach Rio auf zwei zu begrenzen:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail ist ein computerisiertes Anrufbeantwortersystem, das eingehende Sprachnachrichten aufzeichnet, sie auf der Festplatte speichert oder per E‑Mail versendet. Manchmal gibt es ein Verzeichnis, in dem man Voicemail‑Boxen nach Namen durchsuchen kann. Früher waren Voicemail‑Systeme sehr teuer. Heute wird Voicemail mit IP‑Telefonie zu einer Standardfunktion.

Um Voicemail zu konfigurieren, sollten Sie die folgenden Schritte durchgehen.

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

The application voicemailmain() is used to configure the voicemail mailbox. Users can dial the application, record their greeting, and listen to their voicemail. To call the application in the dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Below you will find a list of the options available for the application.

### Voicemail application syntax

This application allows the calling party to leave a message for a specified list of mailboxes. When multiple mailboxes are specified, the greeting will be taken from the first specified mailbox. The dial plan execution will stop if the specified mailbox does not exist. The syntax is shown below:

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

In all cases, the beep.gsm file will be played before the recording begins. Voicemail messages will be stored in the inbox directory.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

If a caller presses 0 (zero) during the announcement, it will be moved to the ‘o’ (out) extension in the voicemail current context. This can be used to exit to the operator. If during the recording the caller presses # or the silence limit times out, recording is stopped and the call goes to the next priority. Make sure that you handle the call after the voicemail is played, as shown below.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

You may tag some messages as “urgent.” Two methods are available for this:

- Pass the option ‘U’ in the application voicemail()
- Specify review=yes in the file voicemail.conf. If using this option, the user will be able to tag the message as urgent after recording the voice instructions.

## Sending voicemail to e-mail

In einigen Fällen (wie bei mir) verwenden wir die Anwendung voicemailmain() nicht, um E‑Mails zu lesen. Es ist einfacher und praktischer, alle Nachrichten per E‑Mail zu versenden und die Audiodatei anzuhängen. Mit den Parametern ‘attach’ und ‘delete’ können Sie alle Nachrichten per E‑Mail senden und sie aus dem Postfach löschen.

```
attach=yes
delete=yes
```

Um Voicemail per E‑Mail zu senden, nutzt die Voicemail‑Anwendung den Message Transfer Agent (MTA), ein Bestandteil Ihres Betriebssystems. Debian verwendet Exim als MTA. Die Anwendung, die die E‑Mail verschickt, wird im Parameter ‘mailcmd’ definiert.

```
mailcmd =/usr/sbin/sendmail -t
```

In der Debian‑Distribution von Linux ist der MTA Exim. Um Exim in Debian zu konfigurieren, verwenden Sie:

```
dpkg-reconfigure exim4-config
```

Sie können wählen, ob Ihr MTA die E‑Mail direkt über SMTP oder über einen Smarthost (in der Regel der Mail‑Server Ihres Unternehmens) senden soll. Klären Sie mit Ihrem E‑Mail‑Administrator die beste Methode, um E‑Mails vom Asterisk‑Server an Ihren E‑Mail‑Server zu senden.

## Anpassen der E-Mail-Nachricht

Sie können steuern, wie Nachrichten gesendet werden, indem Sie die folgenden Variablen festlegen: Variablen für den E-Mail‑Betreff und den E-Mail‑Text:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

Der E-Mail‑Text und der Betreff werden aus einer Vorlage erzeugt, die Sie im `[general]`‑Abschnitt von `voicemail.conf` festlegen. Sie können sowohl den Text als auch den Betreff ändern, aber die Größenbeschränkung der Nachricht beträgt 512 Byte. In der Vorlage fügt `\n` einen Zeilenumbruch ein und `\t` einen Tabulator.

Das `emailsubject`‑Beispiel unten ist einfach gehalten. Das `emailbody`‑Beispiel liegt dem Standard sehr nahe; der Standard zeigt nur den CIDNAME, wenn er nicht null ist, sonst die CIDNUM, oder „ein unbekannter Anrufer“, wenn beide null sind.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Web interface

Es gibt ein Perl‑Skript in der Quelldistribution namens `vmail.cgi`, das sich im Verzeichnis `contrib/scripts/vmail.cgi` im Asterisk‑Quellbaum befindet (es wird noch mit Asterisk 22 ausgeliefert). Der Befehl `make install` installiert diese Schnittstelle nicht; Sie müssen `make webvmail` aus dem Quellverzeichnis ausführen. Dieses Skript benötigt den Perl‑Befehl‑Interpreter und einen Web‑Server (wie Apache), die auf dem Server installiert sein müssen.

```
make webvmail
```

Das Ziel `make webvmail` installiert das Skript (setuid root) in das CGI‑Verzeichnis Ihres Web‑Servers (`HTTP_CGIDIR`) und kopiert die unterstützenden Bilder von `images/*.gif` nach `HTTP_DOCSDIR/_asterisk` (standardmäßig `/var/www/html/_asterisk`). Stimmen diese Pfade nicht mit dem Layout Ihres Web‑Servers überein, bearbeiten Sie die Variablen `HTTP_CGIDIR` und `HTTP_DOCSDIR` in der obersten Ebene `Makefile`, bevor Sie das Ziel ausführen.

## Voicemail notification

Sie können die Voicemail so konfigurieren, dass eine Benachrichtigung an Ihr Telefon gesendet wird, wenn Sie neue Voicemails haben. In Asterisk 22 funktioniert Message Waiting Indication (MWI) sowohl mit PJSIP‑ als auch mit SIP‑Telefonen sowie mit DAHDI‑Telefonen. Um eine ungelesene Voicemail anzuzeigen, kann ein Anzeigelicht blinken oder das Telefon spielt einen Hinweiston ab. Sie müssen das Postfach in der entsprechenden Kanal‑Konfigurationsdatei einrichten. Beispiel: `pjsip.conf` (im endpoint‑Abschnitt):

```
mailboxes=8590
```

In PJSIP wird der Mailbox‑Hinweis mit der `mailboxes`‑Option im endpoint‑Abschnitt von `pjsip.conf` gesetzt, anstatt des alten `mailbox=` von `sip.conf`. MWI‑Abonnements werden vom `res_pjsip_mwi`‑Modul verarbeitet.

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab: Message Notification in the Phone

Dieses Labor wurde mit einem SIP‑Softphone getestet.

1. Editieren Sie `pjsip.conf` und fügen Sie `mailboxes=4401` im endpoint‑Abschnitt für das Gerät mit dem Namen 4401 hinzu.
2. Editieren Sie die `extensions.conf` und erstellen Sie eine Extension, um eine Voicemail für die 4401‑Extensions aufzunehmen.

```
exten=9008,1,voicemail(4401,b)
```

3. Gehen Sie zur Konsole und laden Sie neu.
4. Öffnen Sie in der SipPulse Softphone die SIP‑Kontoeinstellungen und aktivieren Sie die Prüfung von Voicemail (message‑waiting) für das Konto.
5. Wählen Sie 9008 und hinterlassen Sie eine Nachricht.
6. Beobachten Sie das Nachrichtensymbol auf dem Telefon.

## Verwendung der directory-Anwendung

Diese Anwendung ermöglicht es Ihnen, schnell einen Benutzer zum Wählen zu finden. Die Liste der Namen und zugehörigen Nebenstellen wird aus der Voicemail‑Konfigurationsdatei voicemail.conf abgerufen. Die Syntax für die Anwendung kann mit core show application directory angezeigt werden:

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

1. Bearbeiten Sie die Datei voicemail.conf, um zwei Nebenstellen im Dialplan hinzuzufügen

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. Erstellen Sie diese Nebenstellen in Ihrem Dialplan

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. Gehen Sie zur Konsole und laden Sie neu  
4. Wählen Sie 9006 und nehmen Sie einen Namen für jede Nebenstelle auf (4400, 4401)  
5. Wählen Sie 9007 und wählen Sie die drei Buchstaben des Nachnamens für eine Nebenstelle aus (Eas=327). Wenn dies die richtige Option ist, drücken Sie „1“, um zum Namen zu transferieren.

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

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, wie man Anrufe über ein IVR oder einen automatischen Telefonist entgegennimmt. Sie haben das Konzept der Kontext‑Einbindung studiert und einige Beispiele implementiert. Subroutinen wurden verwendet, um wiederholtes Tippen zu vermeiden, und die Asterisk‑Datenbank (AstDB, unterstützt durch SQLite3 in Asterisk 22) wurde für Funktionen genutzt, die Datenspeicherung erfordern (z. B. Anrufweiterleitung, Nicht‑stören, Sperrlisten). Abschließend haben Sie gelernt, wie man das Verhalten außerhalb der Geschäftszeiten implementiert und einen vollständigen Dialplan mit diesen Konzepten erstellt.

## Quiz

1. Ein zeitabhängiger Kontext‑Include verwendet die Form `include => context,<times>,<weekdays>,<mdays>,<months>`. Was bewirkt `include => normalhours,08:00-18:00,mon-fri,*,*`?
   - A. Führt die Extensions von Montag bis Freitag, 08:00 bis 18:00 aus
   - B. Führt die Optionen jeden Tag in allen Monaten aus
   - C. Nichts; das Format ist ungültig
2. In modernem Asterisk (einschließlich Asterisk 22) werden die Felder eines zeitbasierten `include =>` und von `GotoIfTime()` durch welches Zeichen getrennt?
   - A. Das Pipe‑Zeichen `|`
   - B. Das Komma `,`
   - C. Das Semikolon `;`
   - D. Der Schrägstrich `/`
3. Um mehrere Kanäle gleichzeitig zu wählen (sie gleichzeitig klingeln zu lassen), trennt man sie innerhalb von `Dial()` mit dem ___ Zeichen.
4. Ein Sprachmenü, das einen Prompt abspielt, während auf die Eingabe einer Durchwahl gewartet wird, wird üblicherweise mit der ___ Anwendung erstellt.
5. Sie können den Inhalt einer anderen Datei innerhalb von `extensions.conf` mit der ___ Anweisung einbinden (Hinweis: dies unterscheidet sich von der `include =>` Kontext‑Anweisung).
6. In Asterisk 22 wird die eingebaute AstDB‑Datenbank unterstützt von:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. Wenn Sie `Dial(type1/identifier1&type2/identifier2)` verwenden, wählt Asterisk jeden Kanal nacheinander, wobei zwischen den Versuchen 20 Sekunden gewartet werden.
   - A. Falsch
   - B. Richtig
8. Bei der Anwendung Background() muss man warten, bis die Nachricht zu Ende abgespielt ist, bevor man eine DTMF‑Taste drücken kann, um eine Option zu wählen.
   - A. Falsch
   - B. Richtig
9. Angesichts der Syntax `Goto([[context,]extension,]priority)`, welche der folgenden Aufrufe der Goto()-Anwendung sind gültig? (markieren Sie alle zutreffenden)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. Um einen einzelnen Schlüssel aus AstDB im Asterisk 22‑Dialplan zu löschen, verwenden Sie:
    - A. Die `DBdel()` Anwendung
    - B. Die `DB_DELETE()` Funktion
    - C. Die `DBdeltree()` Anwendung
    - D. Die `LookupBlacklist()` Anwendung

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
