# Verwendung von PBX-Funktionen

In SIP-Systemen sind die meisten Telefonfunktionen im Endpoint implementiert. Es gibt eine Vielzahl von SIP-Telefonen und Herstellern, und die Interoperabilität ist nicht garantiert. Das Asterisk-Entwicklungsteam hat hervorragende Arbeit geleistet, indem es die meisten Funktionen direkt in der PBX implementiert hat, wodurch Asterisk nahezu unabhängig vom Endpoint ist. Manchmal werden Sie jedoch feststellen, dass dieselbe Funktion sowohl vom Telefon als auch von Asterisk selbst ausgeführt wird. Die Integration von Telefon und PBX ist die nächste Grenze der Benutzerfreundlichkeit und der Bereich, auf den sich proprietäre Systeme derzeit konzentrieren. In diesem Kapitel lernen Sie, wie Sie die meisten dieser Funktionen nutzen können.

## Ziele

Am Ende dieses Kapitels werden Sie in der Lage sein, Folgendes zu verstehen und zu nutzen:

- Anrufparken (Call Parking)
- Anrufübernahme (Call Pickup)
- Anrufweiterleitung (Call Transfer)
- Telefonkonferenzen (ConfBridge)
- Anrufaufzeichnung (Call Recording)
- Wartemusik (Music on hold)

## Wo Funktionen implementiert sind

Es ist vor allem wichtig zu verstehen, wann PBX-Funktionen ausgeführt werden und wann das Telefon die gesamte Arbeit erledigt. Sie können beispielsweise einen Anruf über die TRANSFER-Taste am Telefon weiterleiten oder durch Wählen von # (eine unbedingte Weiterleitung, die von der PBX selbst ausgeführt wird).

## Von Asterisk implementierte Funktionen

Diese Funktionen werden in der PBX durch den Asterisk-Code implementiert:

- Wartemusik
- Anrufparken
- Anrufübernahme
- Anrufaufzeichnung
- ConfBridge-Konferenzraum
- Anrufweiterleitung (blind und mit Rücksprache)

## Funktionen, die normalerweise durch den Dialplan implementiert werden

Diese Funktionen müssen im Asterisk-Dialplan (extensions.conf) programmiert werden:

- Anrufweiterleitung bei Besetzt
- Anrufweiterleitung sofort
- Anrufweiterleitung bei Nichtannahme
- Anruffilterung (Blacklist)
- Nicht stören (Do not disturb)
- Wahlwiederholung

## Funktionen, die normalerweise vom Telefon implementiert werden

Diese Funktionen werden durch die Firmware des Telefons implementiert:

![Wo die PBX-Funktionen normalerweise implementiert sind: in Asterisk selbst, im Dialplan oder im Telefon](../images/13-pbx-features-fig01.png)

- Anruf halten
- Blindweiterleitung
- Weiterleitung mit Rücksprache
- Drei-Wege-Konferenz
- Nachrichtenanzeige (Message waiting indicator)

## Die Konfigurationsdatei für Funktionen

Einige der in diesem Kapitel vorgestellten Funktionen werden in der Konfigurationsdatei features.conf konfiguriert. Es ist möglich, das Verhalten einiger Funktionen durch Ändern dieser Datei zu ändern. Wir haben den relevanten Auszug unten eingefügt. In den nächsten Abschnitten dieses Kapitels werden wir jede Funktion beschreiben. Auszug aus der Beispieldatei (Asterisk 22)

![Der Abschnitt `[featuremap]` der features.conf mit den standardmäßigen DTMF-Funktionscodes](../images/13-pbx-features-fig02.png)

> **[Anmerkung zur 2. Auflage]** Ab Asterisk 12+ wurde das Anrufparken aus `features.conf`/`app_features` in ein eigenes Modul `res_parking` mit Konfiguration in `res_parking.conf` verschoben. Der Parking-Lot-Block unten (parkext, parkpos, context, parkingtime, etc.) befindet sich in `res_parking.conf` und wird unter Verwendung der Syntax aus Asterisk 22 `res_parking.conf.sample` gezeigt. Der Abschnitt `[featuremap]` (die DTMF-Funktionscodes, einschließlich `parkcall`) verbleibt in `features.conf`.

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
;automon => *1                  ; One Touch Record a.k.a. Touch Monitor -- Make sure to set the W
and/or w option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the
Dial() or Queue()  app call!
;parkcall => #72        ; Park call (one step parking)  -- Make sure to set the K and/or k option in
the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X
and/or x option in the Dial() or Queue() app call!
```

## Anrufweiterleitung

Die Anrufweiterleitung kann vom Telefon, von einem ATA oder von Asterisk selbst implementiert werden. Lesen Sie im Handbuch Ihres Telefons nach, wie Anrufe weitergeleitet werden. Wenn Ihr Telefon keine Anrufweiterleitung unterstützt, können Sie Asterisk verwenden, um diese Aufgabe zu erledigen. Die Anrufweiterleitung wird auf zwei verschiedene Arten implementiert. Die erste Methode ist die Verwendung der Blindweiterleitungsfunktion: Wählen Sie # gefolgt von der Nummer, an die weitergeleitet werden soll. Manchmal verwenden Sie die Weiterleitungsfunktion Ihres IP-Telefons oder IP-Softphones. Sie können das Weiterleitungszeichen ändern, indem Sie den Parameter blindxfer in der Datei features.conf bearbeiten. Sie können die assistierte Weiterleitung in Asterisk aktivieren, indem Sie das ; vor dem Parameter atxfer in der Datei features.conf entfernen. Während eines Gesprächs drücken Sie *2. Asterisk sagt „transfer“ und gibt Ihnen ein Freizeichen. Der Anrufer wird in die Warteschleife (Music on hold) gelegt. Nachdem Sie mit der Zielperson gesprochen und aufgelegt haben, verbindet das System den Anrufer mit dem Ziel.

![Anrufweiterleitung: die Schritte für eine Blindweiterleitung (drücken Sie # während des Anrufs) und eine vermittelte Weiterleitung (drücken Sie *2)](../images/13-pbx-features-fig03.png)

### Konfigurationsaufgabenliste

1. Wenn das Telefon SIP-basiert ist, stellen Sie sicher, dass die Option directmedia auf no gesetzt ist, oder verwenden Sie eine t- oder T-Option in der dial()-Anwendung.

## Anrufparken

Diese Funktion wird verwendet, um einen Anruf zu parken. Dies hilft zum Beispiel, wenn Sie einen Anruf außerhalb Ihres Büros entgegennehmen und den Anruf zurück an Ihren Schreibtisch weiterleiten möchten. Sie können dies erreichen, indem Sie den Anruf auf einer Extension parken. Sobald Sie Ihren Schreibtisch erreichen, wählen Sie einfach die Nummer der Park-Extension, um den Anruf wieder aufzunehmen.

![Anrufparken: Wählen Sie 700, um einen Anruf auf dem ersten freien Platz (701–720) zu parken; Asterisk kündigt den Platz an, den Sie von jedem Telefon aus wählen können, um den Anruf abzurufen](../images/13-pbx-features-fig04.png)

Standardmäßig wird die Extension 700 verwendet, um einen Anruf zu parken. Drücken Sie während eines Gesprächs #, um den Anruf an die Extension 700 weiterzuleiten. Nun kündigt Asterisk Ihre Park-Extension an, wie z. B. 701 oder 702. Legen Sie auf, und der Anrufer wird in die Warteschleife gelegt. Gehen Sie zu Ihrem Schreibtischtelefon und wählen Sie die angekündigte Park-Extension, um den Anruf abzurufen. Wenn der Anrufer für längere Zeit geparkt bleibt, wird die Timeout-Funktion ausgelöst und die ursprünglich gewählte Extension klingelt erneut.

### Konfigurationsaufgabenliste

Befolgen Sie die unten stehenden Schritte, um das Anrufparken zu aktivieren. Schritt 1: Machen Sie den Parkplatz von Ihrem Dialplan aus erreichbar (erforderlich). Der `context` des Standard-Parkplatzes ist `parkedcalls` (eingestellt in `res_parking.conf`). Fügen Sie diesen Kontext in den Kontext ein, von dem aus Ihre Telefone wählen, in `extensions.conf`:

```
include => parkedcalls
```

Schritt 2: Testen Sie die Anrufparkfunktion durch Wählen von #700. Hinweise:

- Die Park-Extension wird im CLI-Befehl dialplan show nicht angezeigt.
- Es ist notwendig, das Parkmodul nach dem Ändern der Park-Konfigurationsdatei neu zu laden: `module reload res_parking.so`. Für Änderungen an der features.conf: `module reload features.so`.
- Um einen Anruf zu parken, müssen Sie an #700 weiterleiten. Überprüfen Sie die Optionen t und T in der dial()-Anwendung.

## Anrufübernahme

Die Anrufübernahme ermöglicht es Ihnen, einen Anruf von einem Kollegen in derselben Anrufgruppe entgegenzunehmen. Dies hilft beispielsweise zu vermeiden, dass Sie aufstehen müssen, um einen Anruf entgegenzunehmen, der bei einer anderen Person in Ihrem Raum klingelt, die jedoch nicht anwesend ist. Durch Wählen von *8 können Sie einen Anruf innerhalb Ihrer Anrufgruppe übernehmen. Diese Nummer kann geändert werden in der

```
features.conf file.
```

![Anrufübernahme: Mitglieder können nur Anrufe innerhalb ihrer eigenen Gruppe übernehmen; der Operator (pickupgroup=1,2,3) kann Anrufe aus jeder Gruppe übernehmen](../images/13-pbx-features-fig05.png)

### Konfigurationsaufgabenliste

Befolgen Sie die unten stehenden Schritte, um die Anrufübernahmefunktion zu konfigurieren. Schritt 1: Konfigurieren Sie eine Anrufgruppe für Ihre Extensions. Dies geschieht in der Kanal-Konfigurationsdatei (pjsip.conf, iax.conf, chan_dahdi.conf). Für PJSIP-Endpoints setzen Sie `call_group` und `pickup_group` im Endpoint-Abschnitt von `pjsip.conf` (pjsip.conf verwendet snake_case-Optionsnamen). Diese Aufgabe ist erforderlich.

Für PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Schritt 2: Ändern Sie die Nummer für die Anrufübernahmefunktion (optional).

```
pickupexten=*8; Configures the call pickup extension
```

## Konferenz (Telefonkonferenz)

Es gibt verschiedene Möglichkeiten, eine Konferenz auf Asterisk zu implementieren. Die erste Option ist einfach die Nutzung der Drei-Wege-Konferenzfunktion des Telefons. Durch die Verwendung dieser Funktion im Telefon benötigen Sie keine Unterstützung auf dem Server selbst. Wenn Sie jedoch eine Konferenz mit mehr als 3 Personen wünschen, sollten Sie einen Konferenzraum betreiben. Die moderne Konferenzanwendung von Asterisk ist ConfBridge (`app_confbridge`).

ConfBridge unterstützt HD-Sprachkonferenzen und Videokonferenzen. Es gibt einige Einschränkungen für Videokonferenzen, wie z. B. kein Transcoding — alle Teilnehmer müssen denselben Codec und dasselbe Profil verwenden. Die Videokonferenz verwendet einen „Follow-the-Talker“-Modus, bei dem das Bild der Person angezeigt wird, die zuletzt gesprochen hat. Sie können ganz einfach neue DTMF-Menüs in ConfBridge konfigurieren.

> **[Anmerkung zur 2. Auflage]** MeetMe (`app_meetme`) wurde **in Asterisk 19 als veraltet markiert** und sollte in Asterisk 21 entfernt werden, aber diese Entfernung wurde (auf Anfrage des ViciDial-Projekts) pausiert. Der Modulquellcode wird weiterhin mit Asterisk 22 ausgeliefert, erfordert jedoch DAHDI und wird **nicht durch den Standard-Build von Asterisk 22 erstellt** — eine Standardinstallation hat kein `app_meetme.so` und die Anwendung `MeetMe()` ist nicht verfügbar. Alle neuen Konferenzraum-Implementierungen müssen ConfBridge verwenden. Der MeetMe-Abschnitt unten bleibt nur aus historischen Gründen erhalten.

### Confbridge

Um einen Konferenzraum zu starten, ist die Syntax unten aufgeführt.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Um eine vollständige Beschreibung des Befehls zu erhalten, können Sie core show application confbridge verwenden.

![Ausgabe von `core show application confbridge`, die die Synopsis, Syntax und die Argumente bridge_profile, user_profile und menu zeigt](../images/13-pbx-features-fig06.png)

Wie Sie oben sehen können, gibt es drei wichtige Abschnitte: Bridge_profile: Sie definieren das Profil in der Datei confbridge.conf. Dort können Sie die maximale Anzahl an Teilnehmern, Aufzeichnung, video_mode und viele andere Bridge-Parameter auswählen.

Es ist nicht sinnvoll, die gesamte Beispieldatei hier wiederzugeben, daher gebe ich Ihnen ein einfaches Beispiel, wie man ein bridge_profile in der Datei confbridge.conf konfiguriert.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile: Hier definieren Sie Optionen, die benutzerspezifisch sind, wie z. B. ob der Benutzer ein Administrator ist oder nicht. Wartemusik und viele andere Optionen können pro Benutzer eingestellt werden. Beispiel:

```
[admin_user]
type=user
admin=yes
```

Menu: Im Menü-Abschnitt können Sie Ihre Tastaturbelegung für die Anwendung definieren, wo Stummschaltung und Aufhebung der Stummschaltung umgeschaltet werden können. Überprüfen Sie die Datei confbridge.conf, um die Optionen zu sehen. Beispiel:

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

#### Confbridge-Funktionen

Die Optionen der Konferenzbrücke können dynamisch im Dialplan unter Verwendung der Funktion CONFBRIDGE() übergeben werden. Siehe die Beispiele unten:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme (Legacy — veraltet, standardmäßig nicht in Asterisk 22 erstellt)

> **[Anmerkung zur 2. Auflage]** `app_meetme` wurde in Asterisk 19 als veraltet markiert. Die geplante Entfernung in Asterisk 21 wurde pausiert, daher wird der Quellcode weiterhin in Asterisk 22 ausgeliefert, aber das Modul wird nicht durch den Standard-Build von Asterisk 22 erstellt (es hängt von DAHDI ab). Eine Standardinstallation von Asterisk 22 hat daher keine Anwendung `MeetMe()`. Der Inhalt unten wird aus historischen Gründen und für Leser beibehalten, die von älteren Systemen aktualisieren. **Verwenden Sie für neue Installationen ConfBridge (siehe oben).** Die DAHDI-Abhängigkeit und das Modul `dahdi_dummy` sind für ConfBridge nicht erforderlich.

Alternativ konnten Sie in älteren Asterisk-Versionen die Anwendung meetme() verwenden. Meetme ist eine Konferenzbrücke, die sehr einfach zu bedienen ist. Denken Sie daran, dass meetme in Asterisk 19 als veraltet markiert wurde und für die Synchronisierung vom DAHDI-Modul abhängt.

![MeetMe-Konferenztypen — Einzelsprecher-, passwortgeschützte und dynamische Konferenzen — erfordern alle eine Zaptel/DAHDI-Zeitquelle](../images/13-pbx-features-fig07.png)

### Die Anwendung meetme()

Mit dem CLI-Befehl meetme show können Sie die obige Beschreibung erhalten. Um meetme zu verwenden, müssen Sie die DAHDI-Treiber kompilieren und mindestens ein DAHDI-Kernelmodul geladen haben. Wenn Sie keine DAHDI-Karte installiert haben, laden Sie das Kernelmodul dahdi_dummy, um eine Zeitquelle bereitzustellen. Beschreibung:

![Die Anwendung MeetMe(): Syntax `MeetMe([confno][,[options][,pin]])` und ihre wichtigsten Options-Flags](../images/13-pbx-features-fig08.png)

Die Anwendung meetme() bringt den Benutzer in eine angegebene Meetme-Konferenz. Wenn die Konferenznummer weggelassen wird, wird der Benutzer aufgefordert, eine einzugeben. Der Benutzer kann die Konferenz durch Auflegen verlassen oder — wenn die Option p angegeben ist — durch Drücken von #. Bitte beachten Sie: Die DAHDI-Kernelmodule und mindestens ein Hardwaretreiber (oder dahdi_dummy) müssen vorhanden sein, damit Konferenzen ordnungsgemäß funktionieren. Außerdem muss der Kanaltreiber chan_dahdi geladen sein, damit die Optionen i und r überhaupt funktionieren.

> **[Anmerkung zur 2. Auflage]** Die folgenden Listen der Options-Flags und Admin-Befehle beschreiben die Legacy-Schnittstelle `app_meetme` und spiegeln die historische Dokumentation von `MeetMe()`/`MeetMeAdmin()` wider. Da `app_meetme` nicht durch die Standardinstallation von Asterisk 22 erstellt wird, können diese Flags nicht an einem laufenden Asterisk 22-System bestätigt werden; sie werden für Leser reproduziert, die ältere Implementierungen warten. Verwenden Sie unter Asterisk 22 ConfBridge und stattdessen die Dialplan-Funktion `CONFBRIDGE()`.

Die Optionszeichenfolge kann null oder eine oder mehrere der folgenden Zeichen enthalten:

- 'a' -- setzt den Admin-Modus
- 'A' -- setzt den markierten Modus
- 'b' – führt das AGI-Skript aus, das in ${MEETME_AGI_BACKGROUND} angegeben ist. Standard: conf-background.agi (Hinweis: Dies funktioniert nicht mit Nicht-DAHDI-Kanälen in derselben Konferenz)
- 'c' -- kündigt die Anzahl der Benutzer beim Beitritt zu einer Konferenz an
- 'd' -- fügt Konferenz dynamisch hinzu
- 'D' -- fügt Konferenz dynamisch hinzu und fordert zur Eingabe einer PIN auf
- 'e' -- wählt eine leere Konferenz aus
- 'E' -- wählt eine leere Konferenz ohne PIN aus
- 'i' -- kündigt einen Benutzer an, der beitritt/verlässt, mit Überprüfung
- 'I' -- kündigt einen Benutzer an, der beitritt/verlässt, ohne Überprüfung
- 'l' -- setzt den Modus „Nur hören“ (Nur zuhören, kein Sprechen)
- 'm' -- setzt anfänglich stumm
- 'M' -- aktiviert Wartemusik, wenn die Konferenz einen einzelnen Anrufer hat
- 'o' -- setzt Sprecheroptimierung, die Sprecher, die nicht sprechen, als stumm behandelt, was bedeutet (a) keine Kodierung bei der Übertragung erfolgt und (b) empfangenes Audio, das nicht als Sprechen registriert ist, weggelassen wird, wodurch kein Aufbau von Hintergrundrauschen verursacht wird
- 'p' -- ermöglicht es Benutzern, die Konferenz durch Drücken von '#' zu verlassen
- 'P' -- fordert immer zur Eingabe der PIN auf, auch wenn sie angegeben ist
- 'q' -- Ruhemodus (keine Beitritts-/Verlassensgeräusche abspielen)
- 'r' -- Zeichnet Konferenz auf (zeichnet als ${MEETME_RECORDINGFILE} unter Verwendung des Formats ${MEETME_RECORDINGFORMAT} auf). Der Standarddateiname ist meetme-conf-rec-${CONFNO}-${UNIQUEID} und das Standardformat ist wav.
- 's' -- Präsentiert Menü (Benutzer oder Admin), wenn '*' empfangen wird ('send' to menu)
- 't' -- setzt den Modus „Nur sprechen“. (Nur sprechen, kein Zuhören)
- 'T' -- setzt Sprechererkennung (wird an die Managerschnittstelle und die Meetme-Liste gesendet)
- 'w[(<secs>)]' -- wartet, bis der markierte Benutzer die Konferenz betritt
- 'x' -- schließt die Konferenz, wenn der letzte markierte Benutzer sie verlässt
- 'X' -- ermöglicht es dem Benutzer, die Konferenz durch Eingabe einer gültigen einstelligen Extension ${MEETME_EXIT_CONTEXT} oder des aktuellen Kontexts zu verlassen, wenn diese Variable nicht definiert ist.
- '1' -- spielt keine Nachricht ab, wenn die erste Person eintritt

### Meetme-Konfigurationsdatei

Diese Datei wird verwendet, um die Anwendung meetme zu konfigurieren. Zum Beispiel:

```
;
; Configuration file for MeetMe simple conference rooms for Asterisk of course.
;
; This configuration file is read every time you call app meetme()
[general]
;audiobuffers=32        ; The number of 20ms audio buffers to be used
                        ; when feeding audio frames from non-DAHDI channels
                        ; into the conference; larger numbers will allow
                        ; for the conference to 'de-jitter' audio that arrives
                        ; at different timing than the conference's timing
                        ; source, but can also allow for latency in hearing
                        ; the audio from the speaker. Minimum value is 2,
                        ; maximum value is 32.
;
[rooms]
;
; Usage is conf => confno[,pin][,adminpin]
;
conf=>9000
conf=>9001,123456
```

Es ist nicht notwendig, entweder reload oder restart zu verwenden, damit Asterisk die Änderungen in der Datei meetme.conf erkennt.

### Meetme-bezogene Anwendungen

Die Anwendung meetme() hat zwei weitere unterstützende Anwendungen.

```
MeetMeCount(confno[|var])
```

Dies spielt die Anzahl der Benutzer in der Konferenz ab. Wenn eine Variable angegeben ist, wird die Nachricht nicht abgespielt, sondern die Anzahl der Benutzer darauf gesetzt.

```
MeetMeAdmin(confno,command,[user]):
```

Führen Sie den Admin-Befehl für eine Konferenz aus:

- 'e' -- Wirft den letzten Benutzer raus, der beigetreten ist
- 'k' -- Kickt einen Benutzer aus der Konferenz
- 'K' -- Kickt alle Benutzer aus der Konferenz
- 'l' -- Entsperrt die Konferenz
- 'L' -- Sperrt die Konferenz
- 'm' -- Hebt die Stummschaltung eines Benutzers auf
- 'M' -- Schaltet einen Benutzer stumm
- 'n' -- Hebt die Stummschaltung aller Benutzer in der Konferenz auf
- 'N' -- Schaltet alle Nicht-Admin-Benutzer in der Konferenz stumm
- 'r' -- Setzt die Lautstärkeeinstellungen eines Benutzers zurück
- 'R' -- Setzt die Lautstärkeeinstellungen aller Benutzer zurück
- 's' -- Senkt die Sprechlautstärke der gesamten Konferenz
- 'S' -- Erhöht die Sprechlautstärke der gesamten Konferenz
- 't' -- Senkt die Sprechlautstärke eines Benutzers
- 'T' -- Senkt die Sprechlautstärke aller Benutzer
- 'u' -- Senkt die Hörlautstärke eines Benutzers
- 'U' -- Senkt die Hörlautstärke aller Benutzer
- 'v' -- Senkt die Hörlautstärke der gesamten Konferenz
- 'V' -- Erhöht die Hörlautstärke der gesamten Konferenz

### Meetme-Konfigurationsaufgabenliste

Befolgen Sie die unten stehenden Schritte, um die Meetme-Konferenzanwendung zu konfigurieren. Schritt 1: Wählen Sie die Extension für den Meetme-Raum (erforderlich). Schritt 2: Bearbeiten Sie die Datei meetme.conf, um die Passwörter zu konfigurieren (optional).

### Beispiele

Beispiel #1: Einfacher Meetme-Raum 1. Erstellen Sie in der Datei extensions.conf den Konferenzraum 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. Legen Sie in der Datei meetme.conf das Passwort für Raum 101 fest. Wichtiger Hinweis: Die Anwendung meetme() benötigt einen Timer, um zu funktionieren. Wenn Sie keine Digium-Hardware installiert und konfiguriert haben, verwenden Sie dahdi_dummy als Zeitquelle.

## Anrufaufzeichnung

Es gibt verschiedene Möglichkeiten, einen Anruf in Asterisk aufzuzeichnen. Sie können die Anwendung mixmonitor() verwenden, um Anrufe einfach aufzuzeichnen.

### Verwendung der Anwendung mixmonitor

Die Anwendung mixmonitor zeichnet das Audio im aktuellen Kanal in der angegebenen Datei auf. Wenn der Dateiname ein absoluter Pfad ist, verwendet sie diesen Pfad. Andernfalls erstellt sie die Datei im konfigurierten Überwachungsverzeichnis aus asterisk.conf.

![Die Anwendung MixMonitor(): zeichnet das Audio eines Kanals auf und mischt es in eine Datei, mit Optionen für Anhängen, nur gebrückt und Lautstärkeanpassung](../images/13-pbx-features-fig09.png)

### Mixmonitor()

Zeichnen Sie einen Anruf auf und mischen Sie das Audio während der Aufzeichnung [Beschreibung] MixMonitor(<file>.<ext>[|<options>[|<command>]]) Zeichnet das Audio auf dem aktuellen Kanal in der angegebenen Datei auf. Optionen: a- An die Datei anhängen, anstatt sie zu überschreiben. b- Audio nur in der Datei speichern, während der Kanal gebrückt ist. Hinweis: beinhaltet keine Konferenzen. v(<x>) - Passen Sie die gehörte Lautstärke um einen Faktor von <x> an. V(<x>) - Passen Sie die gesprochene Lautstärke um einen Faktor von <x> an. W(<x>) - Passen Sie sowohl die gehörte als auch die gesprochene Lautstärke an. Gültige Optionen:

- a - Hängt an die Datei an, anstatt sie zu überschreiben.
- b - Speichert Audio nur in der Datei, während der Kanal gebrückt ist.
- Hinweis: beinhaltet keine Konferenzen.
- v(<x>) - Passt die hörbare Lautstärke um einen Faktor von <x> an (im Bereich von -4 bis 4)
- V(<x>) - Passt die gesprochene Lautstärke um einen Faktor von <x> an (im Bereich von -4 bis 4)
- W(<x>) - Passt sowohl die hörbare als auch die gesprochene Lautstärke um einen Faktor von <x> an (im Bereich von -4 bis 4)
- <command> wird ausgeführt, wenn die Aufzeichnung beendet ist. Alle Zeichenfolgen, die ^{X} entsprechen, werden zu ${X} unescaped und alle Variablen werden zu diesem Zeitpunkt ausgewertet. Die Variable MIXMONITOR_FILENAME enthält den Dateinamen, der für die Aufzeichnung verwendet wurde.

Eine interessante Ressource ist automon, mit der Sie einfach *1 wählen können, um sofort mit der Aufzeichnung zu beginnen. Beispiel:

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

Die Audiokanäle sind eingehend (IN) und ausgehend (OUT) und werden in zwei getrennte Dateien im Verzeichnis /var/spool/asterisk/monitor aufgeteilt. Beide Dateien können mit der Anwendung sox gemischt werden.

```
debian#soxmix *in.wav *out.wav output.wav
```

Wenn Sie Set() nicht vor der Anwendung Dial() verwenden möchten, können Sie dies im Abschnitt globals festlegen:

```
[globals]
DYNAMIC_FEATURES=>automon
```

### Wartemusik

Wartemusik (MOH) hat sich zwischen den Versionen 1.0, 1.2 und 1.4 mehrmals geändert. In der neuesten Version ist MOH standardmäßig „FILE-BASED“. Mit anderen Worten, Asterisk liefert die MOH-Dateien in Formaten wie g729, alaw, ulaw und gsm. Daher ist es nicht notwendig, die Musik zu transkodieren, bevor sie an den Kanal gesendet wird. Dies spart Prozessorzeit, was eine willkommene Änderung für diejenigen ist, die mit Produktionssystemen arbeiten. In älteren Versionen wurde MOH normalerweise durch MP3 bereitgestellt (es kann immer noch so konfiguriert werden). Die Bereitstellung von MOH mittels MP3 zwingt Asterisk zum Transkodieren, was wertvolle CPU-Leistung verbraucht. Die neue Konfigurationsdatei ist unten dargestellt. Beachten Sie, dass die Standardklasse jetzt das native Dateiformat mode=files verwendet. Alle anderen Modi sind auskommentiert. Jeder Abschnitt ist eine Klasse. Die einzige nicht auskommentierte Klasse an dieser Stelle ist default. Wenn Sie verschiedene Klassen für verschiedene Dateien haben möchten, müssen Sie neue Abschnitte (Klassen) erstellen.

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

Um nun Wartemusik zu verwenden, stellen Sie die MOH-Klasse in den Kanal-Konfigurationsdateien (chan_dahdi.conf, pjsip.conf, iax.conf usw.) ein. Für PJSIP-Endpoints setzen Sie `moh_suggest` im Endpoint-Abschnitt von `pjsip.conf` (der Legacy-Optionsname `musicclass` gilt für chan_dahdi und andere Kanaltreiber, nicht für PJSIP). Die installierten Freeplay-Melodien sind jetzt im wav-Format. Zum Zeitpunkt der Installation können Sie (mit make menuselect) die verfügbaren MOH-Dateiformate auswählen. Wenn Sie neue MOH-Dateien hinzufügen möchten, müssen Sie diese in den erforderlichen Formaten bereitstellen. Zum Beispiel:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Im Dialplan können Sie die MOH mit dem folgenden Beispiel hören:

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

So konfigurieren Sie die Datei extensions.conf, um die MOH zu testen:

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## Application Maps

Application Maps ermöglichen es Ihnen, neue Funktionen hinzuzufügen, indem Sie den Abschnitt `[applicationmap]` der Datei features.conf verwenden. Angenommen, Sie müssen die Art des Kunden identifizieren, den Sie in einem Callcenter annehmen. Sie könnten eine Application Map für jeden Kundentyp erstellen, die die Anzahl der angenommenen Kunden pro Typ zählen könnte.

## Quiz

1. Welche Aussagen über das Anrufparken sind wahr?
   - A. Standardmäßig wird die Extension 800 für das Anrufparken verwendet.
   - B. Wenn Sie nicht an Ihrem Schreibtisch sind und einen Anruf erhalten, können Sie ihn parken; das System kündigt den Parkplatz an, und Sie wählen diesen Platz von jedem Telefon aus, um den Anruf abzurufen.
   - C. Standardmäßig parkt die Extension 700 einen Anruf, und Anrufe werden auf den Plätzen 701–720 geparkt.
   - D. Sie wählen 700, um einen geparkten Anruf abzurufen.
2. Um die Anrufübernahmefunktion zu nutzen, müssen sich alle Extensions in derselben ___ befinden. Für DAHDI-Kanäle wird dies in der Datei ___ konfiguriert.
3. Beim Weiterleiten eines Anrufs können Sie zwischen einer ___ Weiterleitung, bei der das Ziel nicht zuerst konsultiert wird, und einer ___ Weiterleitung wählen, bei der Sie mit dem Ziel sprechen, bevor Sie sie abschließen.
4. Um eine vermittelte (mit Rücksprache) Weiterleitung durchzuführen, verwenden Sie die Sequenz ___; für eine Blindweiterleitung verwenden Sie ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Um Telefonkonferenzen in Asterisk 22 zu hosten, verwenden Sie die Anwendung ___.
6. In ConfBridge erhält ein Teilnehmer Administratorrechte (kicken, andere stumm schalten, Raum sperren), indem er ___ in seinem Benutzerprofil (`confbridge.conf`) einstellt:
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Das beste Format für Wartemusik ist MP3, da es sehr wenig Rechenleistung auf dem Asterisk-Server verbraucht.
   - A. Richtig
   - B. Falsch
8. Um einen Anruf aus einer bestimmten Anrufgruppe zu übernehmen, müssen Sie sich in der passenden ___ Gruppe befinden.
9. Sie können einen Anruf mit der Anwendung MixMonitor() oder der One-Touch-Funktion (automon) aufzeichnen. Standardmäßig verwendet automon die DTMF-Sequenz ___.
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. Welche Benutzerprofil-Option `confbridge.conf` in ConfBridge lässt einen Teilnehmer stumm beitreten (er kann die Konferenz hören, aber nicht gehört werden, bis die Stummschaltung aufgehoben wird)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Antworten:** 1 — B, C · 2 — Pickup-Gruppe; `chan_dahdi.conf` · 3 — blind; vermittelt · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — Pickup · 9 — A · 10 — A
