# Verwendung von PBX-Funktionen

In SIP-Systemen werden die meisten Telefonfunktionen im Endpoint implementiert. Es gibt eine Vielzahl von SIP-Telefonen und Herstellern, und die Interoperabilität ist nicht garantiert. Das Asterisk-Entwicklungsteam hat hervorragende Arbeit geleistet, indem es die meisten Funktionen direkt in der PBX implementiert hat, wodurch Asterisk fast unabhängig vom Endpoint ist. Manchmal werden jedoch dieselben Funktionen sowohl vom Telefon als auch von Asterisk selbst ausgeführt. Die Integration von Telefon und PBX ist die nächste Grenze der Benutzerfreundlichkeit und der Bereich, auf den sich proprietäre Systeme derzeit konzentrieren. In diesem Kapitel lernen Sie, wie Sie die meisten dieser Funktionen nutzen können.

## Ziele

Am Ende dieses Kapitels werden Sie in der Lage sein, Folgendes zu verstehen und zu verwenden:

- Call Parking (Anrufparken)
- Call Pickup (Anruf heranholen)
- Call Transfer (Anrufweiterleitung)
- Call Conference (ConfBridge)
- Call Recording (Anrufaufzeichnung)
- Music on hold (Wartemusik)

## Wo Funktionen implementiert sind

Es ist vor allem wichtig zu verstehen, wann PBX-Funktionen ausgeführt werden und wann das Telefon die gesamte Arbeit erledigt. Sie können beispielsweise einen Anruf über die TRANSFER-Taste am Telefon weiterleiten oder durch Wählen von # (eine unbedingte Weiterleitung, die von der PBX selbst ausgeführt wird).

## Von Asterisk implementierte Funktionen

Diese Funktionen werden in der PBX durch den Asterisk-Code implementiert:

- Music on hold
- Call parking
- Call pickup
- Call recording
- ConfBridge-Konferenzraum
- Call transfer (blind und beratend)

## Funktionen, die üblicherweise durch den Dialplan implementiert werden

Diese Funktionen müssen im Asterisk-Dialplan (extensions.conf) programmiert werden:

- Anrufweiterleitung bei Besetzt
- Sofortige Anrufweiterleitung
- Anrufweiterleitung bei Nichtannahme
- Anruffilterung (Blacklist)
- Nicht stören (Do not disturb)
- Wahlwiederholung

## Funktionen, die üblicherweise vom Telefon implementiert werden

Diese Funktionen werden durch die Firmware des Telefons implementiert:

![Wo die PBX-Funktionen üblicherweise implementiert sind: in Asterisk selbst, im Dialplan oder im Telefon](../images/13-pbx-features-fig01.png)

- Anruf halten
- Blind transfer
- Consultative transfer
- Drei-Wege-Konferenz
- Message waiting indicator (Nachrichtenanzeige)

## Die Konfigurationsdatei für Funktionen

Einige der in diesem Kapitel vorgestellten Funktionen werden in der Konfigurationsdatei features.conf konfiguriert. Es ist möglich, das Verhalten einiger Funktionen durch Ändern dieser Datei anzupassen. Wir haben den relevanten Auszug unten eingefügt. In den nächsten Abschnitten dieses Kapitels werden wir jede Funktion beschreiben. Auszug aus der Beispieldatei (Asterisk 22)

![Der `[featuremap]` Abschnitt von features.conf mit den standardmäßigen DTMF-Funktionscodes](../images/13-pbx-features-fig02.png)

Seit Asterisk 12 wurde das Call Parking aus `features.conf` in ein eigenes Modul, `res_parking`, verschoben, mit Konfiguration in `res_parking.conf`. Der Parking-Lot-Block unten (`parkext`, `parkpos`, `context`, `parkingtime` usw.) befindet sich in `res_parking.conf`. Der Abschnitt `[featuremap]` (die DTMF-Funktionscodes, einschließlich `parkcall`) verbleibt in `features.conf`.

Die Optionen für den Parkplatz befinden sich in `res_parking.conf`. Ein Parkplatz namens `default` existiert immer, auch wenn er nicht in der Konfigurationsdatei vorhanden ist. Der folgende Auszug stammt aus der Asterisk 22 `res_parking.conf.sample`:

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

Die DTMF-Funktionscodes (einschließlich des einstufigen `parkcall`) verbleiben im Abschnitt `[featuremap]` von `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t
option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option
in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Call Transfer

Die Anrufweiterleitung kann vom Telefon, von einem ATA oder von Asterisk selbst implementiert werden. Lesen Sie im Handbuch Ihres Telefons nach, wie Anrufe weitergeleitet werden. Wenn Ihr Telefon keine Anrufweiterleitung unterstützt, können Sie Asterisk verwenden, um diese Aufgabe zu erledigen. Die Anrufweiterleitung wird auf zwei verschiedene Arten implementiert. Die erste Methode ist die Verwendung der Blind-Transfer-Funktion: Wählen Sie # gefolgt von der Nummer, an die weitergeleitet werden soll. Manchmal verwenden Sie die Transfer-Funktion Ihres IP-Telefons oder IP-Softphones. Sie können das Transfer-Zeichen ändern, indem Sie den Parameter blindxfer in der Datei features.conf bearbeiten. Sie können die assistierte Weiterleitung in Asterisk aktivieren, indem Sie das ; vor dem Parameter atxfer in der Datei features.conf entfernen. Während eines Gesprächs drücken Sie *2. Asterisk sagt „transfer“ und gibt Ihnen ein Freizeichen. Der Anrufer wird in die Warteschleife (Music on hold) gelegt. Nachdem Sie mit der Zielperson gesprochen und aufgelegt haben, verbindet das System den Anrufer mit dem Ziel.

![Anrufweiterleitung: die Schritte für eine Blind-Weiterleitung (drücken Sie # während des Anrufs) und eine assistierte Weiterleitung (drücken Sie *2)](../images/13-pbx-features-fig03.png)

### Konfigurations-Checkliste

1. Stellen Sie bei einem PJSIP-Endpoint sicher, dass die Option `direct_media` auf `no` gesetzt ist (damit die Medien durch Asterisk fließen und die Funktionscodes erkannt werden), oder verwenden Sie eine `t`/`T` Option in der Anwendung `Dial()`

## Call parking

Diese Funktion wird verwendet, um einen Anruf zu parken. Dies hilft zum Beispiel, wenn Sie einen Anruf außerhalb Ihres Büros entgegennehmen und den Anruf zurück an Ihren Schreibtisch weiterleiten möchten. Sie können dies erreichen, indem Sie den Anruf auf einer Extension parken. Sobald Sie Ihren Schreibtisch erreichen, wählen Sie einfach die Nummer der Park-Extension, um den Anruf zurückzuholen.

![Call parking: Wählen Sie 700, um einen Anruf auf dem ersten freien Platz (701–720) zu parken; Asterisk kündigt den Platz an, den Sie von jedem Telefon aus wählen können, um den Anruf zurückzuholen](../images/13-pbx-features-fig04.png)

Standardmäßig wird die Extension 700 verwendet, um einen Anruf zu parken. Drücken Sie während eines Gesprächs #, um den Anruf an die Extension 700 weiterzuleiten. Nun kündigt Asterisk Ihre Park-Extension an, z. B. 701 oder 702. Legen Sie auf, und der Anrufer wird in die Warteschleife gelegt. Gehen Sie zu Ihrem Schreibtischtelefon und wählen Sie die angekündigte Park-Extension, um den Anruf zurückzuholen. Wenn der Anrufer für längere Zeit geparkt bleibt, wird die Timeout-Funktion ausgelöst und die ursprünglich gewählte Extension klingelt erneut.

### Konfigurations-Checkliste

Befolgen Sie die unten stehenden Schritte, um Call Parking zu aktivieren. Schritt 1: Machen Sie den Parkplatz über Ihren Dialplan erreichbar (erforderlich). Das `context` des Standard-Parkplatzes ist `parkedcalls` (eingestellt in `res_parking.conf`). Fügen Sie diesen Context in den Context ein, von dem aus Ihre Telefone wählen, in `extensions.conf`:

```
include => parkedcalls
```

Schritt 2: Testen Sie die Call-Parking-Funktion durch Wählen von #700. Hinweise:

- Die Park-Extension wird im CLI-Befehl dialplan show nicht angezeigt.
- Es ist notwendig, das Parking-Modul nach dem Ändern der Parking-Konfigurationsdatei neu zu laden: `module reload res_parking.so`. Für Änderungen an features.conf: `module reload features.so`.
- Um einen Anruf zu parken, müssen Sie an #700 weiterleiten. Überprüfen Sie die Optionen `t` und `T` in der Anwendung `Dial()`.

## Call pickup

Call pickup ermöglicht es Ihnen, einen Anruf von einem Kollegen in derselben Anrufgruppe heranzuholen. Dies hilft beispielsweise zu vermeiden, dass Sie aufstehen müssen, um einen Anruf entgegenzunehmen, der bei einer anderen Person in Ihrem Raum klingelt, die jedoch nicht anwesend ist. Durch Wählen von *8 können Sie einen Anruf innerhalb Ihrer Anrufgruppe heranzuholen. Diese Nummer kann geändert werden in der

```
features.conf file.
```

![Call pickup: Mitglieder können nur Anrufe innerhalb ihrer eigenen Gruppe heranzuholen; der Operator (pickupgroup=1,2,3) kann Anrufe aus jeder Gruppe heranzuholen](../images/13-pbx-features-fig05.png)

### Konfigurations-Checkliste

Befolgen Sie die unten stehenden Schritte, um die Call-Pickup-Funktion zu konfigurieren. Schritt 1: Konfigurieren Sie eine Anrufgruppe für Ihre Extensions. Dies geschieht in der Kanal-Konfigurationsdatei (pjsip.conf, iax.conf, chan_dahdi.conf). Setzen Sie für PJSIP-Endpoints `call_group` und `pickup_group` im Endpoint-Abschnitt von `pjsip.conf` (pjsip.conf verwendet snake_case-Optionsnamen). Diese Aufgabe ist erforderlich.

Für PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Schritt 2: Ändern Sie die Call-Pickup-Funktionsnummer (optional). Dies wird im Abschnitt `[general]` von `features.conf` eingestellt, nicht in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (Konferenzschaltung)

Es gibt verschiedene Möglichkeiten, eine Konferenz auf Asterisk zu implementieren. Die erste Option ist die Verwendung der Drei-Wege-Konferenzfunktion des Telefons. Durch die Verwendung dieser Funktion im Telefon benötigen Sie keine Unterstützung auf dem Server selbst. Wenn Sie jedoch eine Konferenz mit mehr als 3 Personen wünschen, sollten Sie einen Konferenzraum betreiben. Asterisks moderne Konferenzanwendung ist ConfBridge (`app_confbridge`).

ConfBridge unterstützt HD-Sprachkonferenzen und Videokonferenzen. Es gibt einige Einschränkungen für Videokonferenzen, wie z. B. kein Transcoding — alle Teilnehmer müssen denselben Codec und dasselbe Profil verwenden. Die Videokonferenz verwendet einen „Follow-the-Talker“-Modus, der das Bild der Person anzeigt, die zuletzt gesprochen hat. Sie können in ConfBridge einfach neue DTMF-Menüs konfigurieren.

ConfBridge ersetzt die alte MeetMe-Anwendung, die in Asterisk 19 als veraltet markiert und in Asterisk 21 entfernt wurde. Im Gegensatz zu MeetMe erfordert ConfBridge **kein** DAHDI oder eine Hardware-Zeitquelle: Es basiert auf der eingebauten Zeitsteuerungsschnittstelle von Asterisk (`res_timing_timerfd` unter Linux oder `res_timing_pthread`), daher wird kein `dahdi_dummy` Modul benötigt. Wenn Sie von einem älteren System migrieren, das `MeetMe()` und `meetme.conf` verwendete, ersetzen Sie diese durch `ConfBridge()` und `confbridge.conf` wie unten beschrieben.

### ConfBridge

Um einen Konferenzraum zu starten, ist die Syntax unten aufgeführt.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Um eine vollständige Beschreibung des Befehls zu erhalten, können Sie core show application confbridge verwenden.

![Ausgabe von `core show application confbridge`, die die Synopsis, Syntax und die Argumente bridge_profile, user_profile und menu zeigt](../images/13-pbx-features-fig06.png)

> **[2nd-ed note]** Ein ConfBridge-Diagramm wäre hier hilfreich: Zeigen Sie mehrere SIP-Endpoints, die einer einzigen benannten Konferenz (z. B. `101`) über `ConfBridge()` beitreten, wobei ein Teilnehmer als Admin markiert ist, und ein Hinweis darauf, dass das Mischen/Timing von `res_confbridge` + dem eingebauten `res_timing_*` Timer (kein DAHDI) gehandhabt wird.

Wie Sie oben sehen können, gibt es drei wichtige Argumente, die jeweils einem Abschnittstyp in `confbridge.conf` zugeordnet sind. **bridge_profile** (ein `type=bridge` Abschnitt): Hier wählen Sie die maximale Anzahl an Teilnehmern (`max_members`), Aufzeichnung (`record_conference`), `video_mode` und viele andere Bridge-weite Parameter.

Es ist nicht sinnvoll, die gesamte Beispieldatei hier zu reproduzieren, daher gebe ich Ihnen ein einfaches Beispiel, wie man ein bridge_profile in der Datei confbridge.conf konfiguriert.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (ein `type=user` Abschnitt): Hier definieren Sie Optionen, die benutzerspezifisch sind, wie z. B. ob der Benutzer ein Administrator ist (`admin=yes`), ob er stummgeschaltet startet (`startmuted=yes`), Wartemusik und viele andere benutzerspezifische Optionen. Beispiel:

```
[admin_user]
type=user
admin=yes
```

**menu** (ein `type=menu` Abschnitt): Hier definieren Sie die Tastenfeld-Belegung (DTMF) für die Konferenz — zum Beispiel, welche Taste die Stummschaltung umschaltet, die Lautstärke anpasst oder die Konferenz verlässt. Überprüfen Sie die Datei `confbridge.conf.sample`, um alle verfügbaren Aktionen zu sehen. Beispiel:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### ConfBridge-Funktionen

Die Konferenz-Bridge-Optionen können dynamisch im Dialplan mit der Funktion CONFBRIDGE() übergeben werden. Siehe die Beispiele unten:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge Admin-Befehle und Migration von MeetMe

Wenn Sie von MeetMe kommen, werden die Admin-Funktionen, die Sie über `MeetMeAdmin()` und die Option `a` (admin) verwendet haben, jetzt über das **Admin-Benutzerprofil** (`admin=yes`) plus die **Menü**-Aktionen ausgedrückt. Ein Administrator, der mit einem Admin-Profil und einem Menü mit Admin-Aktionen beitritt, kann den Raum sperren, Benutzer kicken und Teilnehmer live über das Tastenfeld stummschalten. Die relevanten Menü-Aktionen in `confbridge.conf` sind:

- `admin_kick_last` -- den zuletzt beigetretenen Benutzer kicken
- `admin_toggle_mute_participants` -- alle Nicht-Admin-Teilnehmer stummschalten/die Stummschaltung aufheben
- `toggle_mute` -- sich selbst stummschalten/die Stummschaltung aufheben
- `participant_count` -- die Anzahl der Teilnehmer ansagen
- `leave_conference` -- die Bridge verlassen und im Dialplan fortfahren

Diese ersetzen die MeetMe-Options-Flags `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x` …) und die Befehle `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N` …). Es gibt kein `meetme.conf` in Asterisk 22; die gesamte Konferenzkonfiguration befindet sich in `confbridge.conf`, und Änderungen werden mit `module reload res_confbridge.so` angewendet.

### ConfBridge-Beispiel

Um einen Konferenzraum zu erstellen, der unter der Extension 500 erreichbar ist, in `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Der erste Anrufer, der 500 wählt, erstellt die Konferenz `101`; nachfolgende Anrufer treten ihr bei. Die hier referenzierten Profile und Menüs (`default_bridge`, `default_user`, `sample_user_menu`) sind in `confbridge.conf` definiert. Um eine PIN zu verlangen, setzen Sie `pin=` im Benutzerprofil; um einen Teilnehmer zum Konferenzadministrator zu machen, geben Sie ihm ein Benutzerprofil mit `admin=yes`.

## Call Recording (Anrufaufzeichnung)

Es gibt verschiedene Möglichkeiten, einen Anruf in Asterisk aufzuzeichnen. Sie können die Anwendung `MixMonitor()` verwenden, um Anrufe einfach aufzuzeichnen. (Die ältere Anwendung `Monitor`, die zwei separate Dateien aufzeichnete, wurde entfernt; verwenden Sie stattdessen `MixMonitor`.)

### Verwendung der MixMonitor-Anwendung

Die Anwendung `MixMonitor` zeichnet das Audio im aktuellen Kanal in der angegebenen Datei auf. Wenn der Dateiname ein absoluter Pfad ist, verwendet sie diesen Pfad. Andernfalls erstellt sie die Datei im konfigurierten Überwachungsverzeichnis aus asterisk.conf.

![Die MixMonitor()-Anwendung: zeichnet das Audio eines Kanals auf und mischt es in eine Datei, mit Optionen für Anhängen, nur gebrückt und Lautstärkeanpassung](../images/13-pbx-features-fig09.png)

### MixMonitor()

Zeichnen Sie einen Anruf auf und mischen Sie das Audio während der Aufnahme. Syntax: `MixMonitor(filename.extension[,options[,command]])`. Zeichnet das Audio auf dem aktuellen Kanal in der angegebenen Datei auf. Gültige Optionen:

- a - Hängt an die Datei an, anstatt sie zu überschreiben.
- b - Speichert Audio nur dann in der Datei, während der Kanal gebrückt ist.
- Hinweis: beinhaltet keine Konferenzen.
- v(<x>) - Passt die hörbare Lautstärke um einen Faktor von <x> an (Bereich von -4 bis 4)
- V(<x>) - Passt die gesprochene Lautstärke um einen Faktor von <x> an (Bereich von -4 bis 4)
- W(<x>) - Passt sowohl die hörbare als auch die gesprochene Lautstärke um einen Faktor von <x> an (Bereich von -4 bis 4)
- <command> wird ausgeführt, wenn die Aufnahme beendet ist. Alle Zeichenfolgen, die ^{X} entsprechen, werden zu ${X} unescaped und alle Variablen werden zu diesem Zeitpunkt ausgewertet. Die Variable MIXMONITOR_FILENAME enthält den Dateinamen, der für die Aufnahme verwendet wurde.

Eine interessante Ressource ist die One-Touch-Aufzeichnungsfunktion `automixmon`, mit der eine Partei während eines Anrufs einen DTMF-Code (Standard `*3`) wählen kann, um die Aufnahme sofort zu starten (und auszuschalten). Sie basiert auf MixMonitor, schreibt also eine einzige gemischte Datei. Beispiel:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Die Optionen `X` und `x` aktivieren die One-Touch-MixMonitor-Funktion für den Anrufer bzw. den Angerufenen. Da MixMonitor eine einzelne gemischte Datei aufzeichnet, müssen danach keine separaten IN/OUT-Dateien kombiniert werden (der alte Ansatz `automon`/`Monitor`, der zwei Dateien für `soxmix` erzeugte, wurde zusammen mit der Anwendung `Monitor` entfernt).

Wenn Sie Set() nicht vor der Dial()-Anwendung verwenden möchten, können Sie dies im Globals-Abschnitt festlegen:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold (Wartemusik)

Music on hold (MOH) hat sich zwischen den Versionen 1.0, 1.2 und 1.4 mehrmals geändert. In der neuesten Version ist MOH standardmäßig auf „FILE-BASED“ eingestellt. Mit anderen Worten, Asterisk liefert die MOH-Dateien in Formaten wie g729, alaw, ulaw und gsm. Daher ist es nicht notwendig, die Musik zu transkodieren, bevor sie an den Kanal gesendet wird. Dies spart Prozessorzeit, was eine willkommene Änderung für diejenigen ist, die mit Produktionssystemen arbeiten. In älteren Versionen wurde MOH normalerweise durch MP3 bereitgestellt (es kann immer noch so konfiguriert werden). Die Bereitstellung von MOH über MP3 zwingt Asterisk zum Transkodieren, was wertvolle CPU-Leistung verbraucht. Die neue Konfigurationsdatei ist unten dargestellt. Beachten Sie, dass die Standardklasse jetzt den nativen Dateiformatmodus mode=files verwendet. Alle anderen Modi sind auskommentiert. Jeder Abschnitt ist eine Klasse. Die einzige nicht auskommentierte Klasse ist an dieser Stelle default. Wenn Sie verschiedene Klassen für verschiedene Dateien haben möchten, müssen Sie neue Abschnitte (Klassen) erstellen.

![Die Beispielkonfiguration musiconhold.conf, die die gültigen MOH-Modi auflistet (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### MOH-Konfigurationsaufgaben

Um nun Wartemusik zu verwenden, setzen Sie die MOH-Klasse in den Kanal-Konfigurationsdateien (chan_dahdi.conf, pjsip.conf, iax.conf usw.). Setzen Sie für PJSIP-Endpoints `moh_suggest` im Endpoint-Abschnitt von `pjsip.conf` (der Legacy-Optionsname `musicclass` gilt für chan_dahdi und andere Kanaltreiber, nicht für PJSIP). Die installierten Freeplay-Melodien sind jetzt im wav-Format. Zum Zeitpunkt der Installation können Sie (mit make menuselect) die verfügbaren MOH-Dateiformate auswählen. Wenn Sie neue MOH-Dateien hinzufügen möchten, müssen Sie diese in den erforderlichen Formaten bereitstellen. Zum Beispiel:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Im Dialplan können Sie Wartemusik auf einem Kanal mit `StartMusicOnHold` starten (und mit `StopMusicOnHold` stoppen):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Um Wartemusik für eine feste Zeit als schnellen Test abzuspielen, verwenden Sie die Anwendung `MusicOnHold` mit einer Dauer (in Sekunden):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Application Maps

Application Maps ermöglichen es Ihnen, neue Funktionen hinzuzufügen, indem Sie den Abschnitt `[applicationmap]` der Datei features.conf verwenden. Angenommen, Sie müssen die Art des Kunden identifizieren, den Sie in einem Callcenter annehmen. Sie könnten eine Application Map für jeden Kundentyp erstellen, die die Anzahl der angenommenen Kunden pro Typ zählen könnte.

## Quiz

1. Welche Aussagen über Call Parking sind wahr?
   - A. Standardmäßig wird die Extension 800 für Call Parking verwendet.
   - B. Wenn Sie nicht an Ihrem Schreibtisch sind und einen Anruf erhalten, können Sie ihn parken; das System kündigt den Parkplatz an, und Sie wählen diesen Platz von jedem Telefon aus, um den Anruf zurückzuholen.
   - C. Standardmäßig parkt die Extension 700 einen Anruf, und Anrufe werden auf den Plätzen 701–720 geparkt.
   - D. Sie wählen 700, um einen geparkten Anruf zurückzuholen.
2. Um die Call-Pickup-Funktion zu nutzen, müssen sich alle Extensions in derselben ___ befinden. Für DAHDI-Kanäle wird dies in der Datei ___ konfiguriert.
3. Beim Weiterleiten eines Anrufs können Sie zwischen einer ___ Weiterleitung, bei der das Ziel nicht zuerst konsultiert wird, und einer ___ Weiterleitung wählen, bei der Sie mit dem Ziel sprechen, bevor Sie sie abschließen.
4. Um eine assistierte (beratende) Weiterleitung durchzuführen, verwenden Sie die Sequenz ___; für eine Blind-Weiterleitung verwenden Sie ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Um Konferenzgespräche in Asterisk 22 zu hosten, verwenden Sie die Anwendung ___.
6. In ConfBridge erhält ein Teilnehmer Administratorrechte (kicken, andere stummschalten, Raum sperren), indem er ___ in seinem Benutzerprofil (`confbridge.conf`) setzt:
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Das beste Format für Wartemusik ist MP3, da es sehr wenig Rechenleistung auf dem Asterisk-Server verbraucht.
   - A. Wahr
   - B. Falsch
8. Um einen Anruf aus einer bestimmten Anrufgruppe heranzuholen, müssen Sie in der passenden ___ Gruppe sein.
9. Sie können einen Anruf mit der Anwendung MixMonitor() oder der One-Touch-Aufzeichnungsfunktion (`automixmon`) aufzeichnen. Standardmäßig verwendet `automixmon` die DTMF-Sequenz ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. Welche Benutzerprofil-Option `confbridge.conf` in ConfBridge lässt einen Teilnehmer stummgeschaltet beitreten (er kann die Konferenz hören, aber nicht gehört werden, bis die Stummschaltung aufgehoben wird)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Antworten:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
