# Verwendung von PBX‑Funktionen

In SIP‑Systemen werden die meisten Telefonfunktionen im Endpoint implementiert. Es gibt eine Vielzahl von SIP‑Telefonen und Herstellern, und die Interoperabilität ist nicht garantiert. Das Asterisk‑Entwicklungsteam hat hervorragende Arbeit geleistet, indem es die meisten Funktionen in der PBX selbst implementiert hat, wodurch Asterisk nahezu endpoint‑unabhängig wird. Trotzdem kommt es gelegentlich vor, dass dieselbe Funktion sowohl vom Telefon als auch von Asterisk ausgeführt wird. Die Integration von Telefon und PBX ist die nächste Grenze der Benutzerfreundlichkeit und derzeit ein Schwerpunkt proprietärer Systeme. In diesem Kapitel lernen Sie, wie Sie die meisten dieser Funktionen nutzen können.

## Ziele

By the end of this chapter, you will be able to understand and use:

- Anrufparken
- Anrufannahme
- Anrufweiterleitung
- Anrufkonferenz (ConfBridge)
- Anrufaufzeichnung
- Wartemusik

## Where features are implemented

First and foremost, it is important to understand when the PBX features are being executed versus when the phone is doing all the work. For example, you may transfer a call using the TRANSFER button on the phone or by dialing # (unconditional transfer executed by the PBX itself).

## Von Asterisk implementierte Funktionen

- Musik in Warteschleife
- Anrufparken
- Anrufannahme
- Anrufaufzeichnung
- ConfBridge-Konferenzraum
- Anrufweiterleitung (blind und konsultativ)

## Funktionen, die üblicherweise im Dialplan implementiert werden

- Rufumleitung bei Besetzt
- Sofortige Rufumleitung
- Rufumleitung bei Nichtantwort
- Anruffilterung (Blacklist)
- Bitte nicht stören
- Rückwahl

## Funktionen, die normalerweise vom Telefon implementiert werden

![Wo die PBX‑Funktionen normalerweise implementiert werden: in Asterisk selbst, im Dialplan oder im Telefon](../images/13-pbx-features-fig01.png)

- Anruf halten
- Blinde Weiterleitung
- Beratende Weiterleitung
- Dreierkonferenz
- Nachrichten‑Warteanzeige

## The features configuration file

Einige der in diesem Kapitel vorgestellten Features werden in der Konfigurationsdatei **features.conf** konfiguriert. Es ist möglich, das Verhalten einiger Features zu ändern, indem man diese Datei anpasst. Wir haben den relevanten Ausschnitt unten eingefügt. In den nächsten Abschnitten dieses Kapitels werden wir jedes Feature beschreiben. Auszug aus der Beispieldatei (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Seit Asterisk 12 wurde das Call‑Parking aus `features.conf` in ein eigenes Modul, `res_parking`, ausgelagert, mit Konfiguration in `res_parking.conf`. Der **parking-lot**‑Block unten (`parkext`, `parkpos`, `context`, `parkingtime` usw.) befindet sich in `res_parking.conf`. Der **`[featuremap]`**‑Abschnitt (die DTMF‑Feature‑Codes, einschließlich `parkcall`) bleibt in `features.conf`.

Die **parking-lot**‑Optionen befinden sich in `res_parking.conf`. Ein Parking‑Lot mit dem Namen `default` existiert immer, selbst wenn es nicht in der Konfigurationsdatei angegeben ist. Der untenstehende Auszug stammt aus dem Asterisk 22 `res_parking.conf.sample`:

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

Die DTMF‑Feature‑Codes (einschließlich des One‑Step `parkcall`) bleiben im **`[featuremap]`**‑Abschnitt von `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## Call Transfer

Call transfer can be implemented by the phone, by ATA, or by Asterisk itself. Refer to your phone manual to understand how calls are transferred. If your phone does not support call transfer, you can use Asterisk to accomplish this task. Call transfer is implemented in two different ways.

The first way is to use the blind transfer feature: dial # followed by the number to be transferred. Sometimes you will use the transfer feature of your IP phone or IP soft phone. You can change the transfer character by editing the blindxfer parameter in the features.conf file.

You can enable assisted transfer in Asterisk by removing the ; before the atxfer parameter in the features.conf file. During a conversation, you would press *2. Asterisk will say "transfer" and will give you a dial tone. The caller is sent to music on hold. After you speak to the destination person and hang up the phone, the system bridges the caller to the destination.

![Anrufweiterleitung: die Schritte für eine blinde Weiterleitung (drücken Sie # während des Anrufs) und eine betreute Weiterleitung (drücken Sie *2)](../images/13-pbx-features-fig03.png)

### Configuration task list

1. For a PJSIP endpoint, make sure the option `direct_media` is set to `no` (so the media flows through Asterisk and the feature codes are detected), or use a `t`/`T` option in the `Dial()` application

## Call parking

Dieses Feature wird verwendet, um einen Anruf zu parken. Das ist zum Beispiel hilfreich, wenn Sie einen Anruf außerhalb Ihres Raumes entgegennehmen und den Anruf zurück an Ihren Schreibtisch übertragen möchten. Sie können dies erreichen, indem Sie den Anruf in einer Nebenstelle parken. Sobald Sie an Ihrem Schreibtisch sind, wählen Sie einfach die Nummer der Park‑Nebenstelle, um den Anruf wiederherzustellen.

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

Standardmäßig wird die Nebenstelle 700 zum Parken eines Anrufs verwendet. Während eines Gesprächs drücken Sie #, um den Anruf an die Nebenstelle 700 zu übertragen. Jetzt wird Asterisk Ihre Park‑Nebenstelle ansagen, z. B. 701 oder 702. Legen Sie auf, und der Anrufer wird in die Warteschleife gelegt. Gehen Sie zu Ihrem Schreibtischtelefon und wählen Sie die angesagte Park‑Nebenstelle, um den Anruf wiederherzustellen. Wenn der Anrufer lange geparkt wird, löst die Timeout‑Funktion aus und die ursprünglich gewählte Nebenstelle klingelt erneut.

### Configuration task list

Folgen Sie den untenstehenden Schritten, um Call Parking zu aktivieren. Schritt 1: Machen Sie den Parkplatz aus Ihrem Dialplan erreichbar (erforderlich). Der Standard‑Parkplatz‑`context` ist `parkedcalls` (gesetzt in `res_parking.conf`). Binden Sie diesen Kontext in den Kontext ein, aus dem Ihre Telefone wählen, in `extensions.conf`:

```
include => parkedcalls
```

Schritt 2: Testen Sie das Call‑Parking‑Feature, indem Sie #700 wählen. Hinweise:

- Die Park‑Nebenstelle wird im CLI‑Befehl `dialplan show` nicht angezeigt.
- Nach Änderungen an der Park‑Konfigurationsdatei muss das Parking‑Modul neu geladen werden: `module reload res_parking.so`. Für Änderungen in `features.conf` gilt: `module reload features.so`.
- Um einen Anruf zu parken, müssen Sie zu #700 transferieren. Überprüfen Sie die Optionen `t` und `T` in der Anwendung `Dial()`.

## Call pickup

Call pickup ermöglicht es Ihnen, einen Anruf von einem Kollegen in derselben Anrufgruppe zu übernehmen. Das hilft zum Beispiel, zu vermeiden, dass Sie aufstehen müssen, um einen Anruf entgegenzunehmen, der bei einer anderen Person in Ihrem Raum klingelt, die jedoch nicht anwesend ist. Durch Wählen von *8 können Sie einen Anruf innerhalb Ihrer Anrufgruppe übernehmen. Diese Nummer kann in der `features.conf`‑Datei geändert werden.

![Call pickup: members can only capture calls within their own group; the operator (pickupgroup=1,2,3) can pick up calls from every group](../images/13-pbx-features-fig05.png)

### Configuration task list

Folgen Sie den nachstehenden Schritten, um die Call‑Pickup‑Funktion zu konfigurieren. Schritt 1: Konfigurieren Sie eine Anrufgruppe für Ihre Nebenstellen. Dies erfolgt in der Kanal‑Konfigurationsdatei (pjsip.conf, iax.conf, chan_dahdi.conf). Für PJSIP‑Endpoints setzen Sie `call_group` und `pickup_group` im Endpoint‑Abschnitt von `pjsip.conf` (pjsip.conf verwendet snake_case‑Optionen). Diese Aufgabe ist erforderlich.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Step 2: Change the call-pickup feature number (optional). This is set in the `[general]` section of `features.conf`, not in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conference (call conference)

Es gibt verschiedene Möglichkeiten, eine Konferenz in Asterisk zu implementieren. Die erste Option besteht einfach darin, die Dreierkonferenz‑Funktion des Telefons zu nutzen. Durch die Verwendung dieser Funktion im Telefon ist keine Unterstützung auf dem Server selbst erforderlich. Wenn Sie jedoch eine Konferenz mit mehr als 3 Personen wünschen, sollten Sie einen Konferenzraum betreiben. Asterisk's moderne Konferenzanwendung ist ConfBridge (`app_confbridge`).

ConfBridge unterstützt HD‑Sprachkonferenzen und Videokonferenzen. Es gibt einige Einschränkungen für Videokonferenzen, wie z. B. kein Transcoding — alle Teilnehmer müssen denselben Codec und dasselbe Profil verwenden. Die Videokonferenz verwendet einen „follow‑the‑talker“-Modus, bei dem das Bild der zuletzt sprechenden Person angezeigt wird. Sie können in ConfBridge leicht neue DTMF‑Menüs konfigurieren.

ConfBridge ersetzt die alte MeetMe‑Anwendung, die in Asterisk 19 veraltet ist. MeetMe ist noch im Quellcode‑Baum von Asterisk 22 enthalten, hängt jedoch von DAHDI ab und wird standardmäßig nicht gebaut, sodass es bei einer typischen PJSIP‑Installation einfach nicht verfügbar ist — ConfBridge ist die unterstützte Konferenzanwendung. Im Gegensatz zu MeetMe erfordert ConfBridge **keine** DAHDI oder eine Hardware‑Timing‑Quelle: Es nutzt die eingebaute Timing‑Schnittstelle von Asterisk (`res_timing_timerfd` unter Linux, oder `res_timing_pthread`), sodass kein `dahdi_dummy`‑Modul nötig ist. Wenn Sie von einem älteren System migrieren, das `MeetMe()` und `meetme.conf` verwendet hat, ersetzen Sie diese durch `ConfBridge()` und `confbridge.conf` wie unten beschrieben.

### ConfBridge

Um einen Konferenzraum zu starten, ist die Syntax unten aufgeführt.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Um eine vollständige Beschreibung des Befehls zu erhalten, können Sie `core show application confbridge` verwenden.

![Ausgabe von `core show application confbridge`, die die Zusammenfassung, Syntax und die Argumente bridge_profile, user_profile und menu zeigt](../images/13-pbx-features-fig06.png)

![Mehrere PJSIP‑Endpoints treten einer benannten ConfBridge‑Konferenz (101) bei; ein Teilnehmer ist der Administrator. Das Mischen und die Zeitsteuerung werden von `app_confbridge` zusammen mit `bridge_softmix` und dem integrierten `res_timing_*`‑Timer übernommen – kein DAHDI erforderlich.](../images/13-pbx-features-fig09.png)

Wie oben zu sehen ist, gibt es drei wichtige Argumente, die jeweils einem Abschnittstyp in `confbridge.conf` zugeordnet sind. **bridge_profile** (ein `type=bridge`‑Abschnitt): Hier wählen Sie die maximale Teilnehmerzahl (`max_members`), Aufzeichnung (`record_conference`), `video_mode` und viele weitere bridge‑weite Parameter.

Es macht keinen Sinn, die gesamte Beispieldatei hier zu reproduzieren, daher gebe ich Ihnen ein einfaches Beispiel, wie man ein `bridge_profile` in der Datei `confbridge.conf` konfiguriert.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (ein `type=user` Abschnitt): hier definieren Sie Optionen, die spezifisch pro Benutzer sind, wie z.B. ob der Benutzer ein Administrator ist (`admin=yes`), ob er stumm startet (`startmuted=yes`), Musik on Hold und viele andere benutzerspezifische Optionen. Beispiel:

```
[admin_user]
type=user
admin=yes
```

**menu** (ein `type=menu` Abschnitt): hier definieren Sie die Tastatur (DTMF) Zuordnung für die Konferenz — zum Beispiel welche Taste Stummschaltung umschaltet, die Lautstärke anpasst oder die Konferenz verlässt. Prüfen Sie die `confbridge.conf.sample` Datei, um alle verfügbaren Aktionen zu sehen. Beispiel:

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

Die Optionen der Konferenzbrücke können dynamisch im Dialplan mittels der CONFBRIDGE()-Funktion übergeben werden. Siehe die Beispiele unten:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### ConfBridge-Admin-Befehle und Migration von MeetMe

Wenn Sie von MeetMe kommen, werden die Admin‑Funktionen, die Sie über `MeetMeAdmin()` und die `a`‑Option (admin) verwendet haben, jetzt über das **Admin‑Benutzerprofil** (`admin=yes`) plus die **Menü**‑Aktionen ausgedrückt. Ein Administrator, der sich mit einem Admin‑Profil und einem Menü mit Admin‑Aktionen einloggt, kann den Raum sperren, Benutzer entfernen und Teilnehmer live vom Tastaturfeld stumm schalten. Die relevanten Menü‑Aktionen in `confbridge.conf` sind:

- `admin_kick_last` – den zuletzt beigetretenen Benutzer entfernen
- `admin_toggle_mute_participants` – alle Nicht‑Admin‑Teilnehmer stumm schalten/entschalten
- `toggle_mute` – sich selbst stumm schalten/entschalten
- `participant_count` – die Anzahl der Teilnehmer ankündigen
- `leave_conference` – die Bridge verlassen und im Dialplan fortfahren

Diese ersetzen die MeetMe `MeetMe()`‑Optionsflags (`a`, `A`, `m`, `M`, `l`, `x`, …) und die `MeetMeAdmin()`‑Befehle (`k`, `K`, `L`, `M`, `N`, …). Auf einer modernen PJSIP‑Installation werden Sie `app_meetme` überhaupt nicht laden; die gesamte Konferenzkonfiguration befindet sich in `confbridge.conf`, und Änderungen werden mit `module reload app_confbridge.so` angewendet (die ConfBridge‑Logik befindet sich in `app_confbridge`; es gibt kein `res_confbridge`‑Modul).

### ConfBridge‑Beispiel

Um einen Konferenzraum zu erstellen, der über die Nebenstelle 500 erreichbar ist, in `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Der erste Anrufer, der 500 wählt, erstellt die Konferenz `101`; nachfolgende Anrufer treten ihr bei. Die hier referenzierten Profile und Menüs (`default_bridge`, `default_user`, `sample_user_menu`) sind in `confbridge.conf` definiert. Um eine PIN zu verlangen, setzen Sie `pin=` im Benutzerprofil; um einen Teilnehmer zum Konferenzadministrator zu machen, geben Sie ihm ein Benutzerprofil mit `admin=yes`.

## Call Recording

There are several ways to record a call in Asterisk. You can use the `MixMonitor()` application to easily record calls. (The older `Monitor` application, which recorded two separate files, was removed; use `MixMonitor` instead.)

### Using the MixMonitor application

The `MixMonitor` application records the audio in the current channel to the specified file. If the filename is an absolute path, it uses that path. Otherwise, it creates the file in the configured monitoring directory from asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

Record a call and mix the audio during the recording. Syntax: `MixMonitor(filename.extension[,options[,command]])`. Records the audio on the current channel to the specified file. Valid options:

- a - Appends to the file instead of overwriting it.
- b - Only saves audio to the file while the channel is bridged.
- Note: does not include conferences.
- v(<x>) - Adjusts the audible volume by a factor of <x> (ranging from -4 to 4)
- V(<x>) - Adjusts the spoken volume by a factor of <x> (ranging from -4 to 4)
- W(<x>) - Adjusts both audible and spoken volumes by a factor of <x> (ranging from -4 to 4)
- <command> will be executed when the recording is over. Any strings matching ^{X} will be unescaped to ${X} and all variables will be evaluated at that time. The variable MIXMONITOR_FILENAME will contain the filename used to record.

An interesting resource is the one-touch recording feature `automixmon`, which lets a party dial a DTMF code (the `features.conf` sample suggests `*3`; there is no built-in default, so you must set it) during a call to immediately start (and toggle off) recording. It is built on MixMonitor, so it writes a single mixed file. Example:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Die `X`- und `x`-Optionen aktivieren die One‑Touch‑MixMonitor‑Funktion für den Anrufer bzw. den Angerufenen. Da MixMonitor eine einzige gemischte Datei aufzeichnet, muss man danach keine separaten IN/OUT‑Dateien mehr zusammenführen (der alte `automon`/`Monitor`‑Ansatz, der zwei Dateien für `soxmix` erzeugte, wurde zusammen mit der `Monitor`‑Anwendung entfernt).

Wenn Sie Set() nicht vor der Dial()-Anwendung verwenden möchten, können Sie dies im globals‑Abschnitt festlegen:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) hat sich über die Versionen 1.0, 1.2 und 1.4 mehrfach geändert. In der neuesten Version ist MOH standardmäßig auf „FILE-BASED“ eingestellt. Das bedeutet, Asterisk liefert die MOH‑Dateien in Formaten wie g729, alaw, ulaw und gsm. Es ist also nicht nötig, die Musik vor dem Senden an den Kanal zu transkodieren. Das spart Prozessorzeit, was eine willkommene Änderung für den Einsatz in Produktionssystemen darstellt.

In älteren Versionen wurde MOH meist über MP3 bereitgestellt (dies kann nach wie vor so konfiguriert werden). Die Bereitstellung von MOH über MP3 zwingt Asterisk zum Transkodieren, wodurch wertige CPU‑Leistung verbraucht wird.

Die neue Konfigurationsdatei ist unten abgebildet. Beachten Sie, dass die Standardklasse nun den nativen Dateiformat‑Modus = files verwendet. Alle anderen Modi sind auskommentiert. Jeder Abschnitt ist eine Klasse. Die einzige nicht auskommentierte Klasse an dieser Stelle ist default. Wenn Sie verschiedene Klassen für unterschiedliche Dateien benötigen, müssen Sie neue Abschnitte (Klassen) anlegen.

![Die Beispielkonfiguration von musiconhold.conf, die die gültigen MOH‑Modi (quietmp3, mp3, custom, files, …) auflistet](../images/13-pbx-features-fig10.png)

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

Now, to use music on hold, set the MOH class in the channel configuration files (chan_dahdi.conf, pjsip.conf, iax.conf, and so on). For PJSIP endpoints, set `moh_suggest` in the endpoint section of `pjsip.conf` (the legacy `musicclass` option name applies to chan_dahdi and other channel drivers, not to PJSIP). The freeplay tunes installed are now in wav format. At the time of installation, you can select (using make menuselect) the MOH file formats available. If you want to add new MOH files, you will have to supply them in the required formats. For example:

In `/etc/asterisk/chan_dahdi.conf`, add the `musiconhold` line:

```
[channels]
musiconhold=default
```

Then edit `/etc/asterisk/musiconhold.conf` to define that class:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Im dial plan, you can start music on hold on a channel with `StartMusicOnHold` (and stop it with `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Um Musik in Warteschleife für eine feste Zeit als schnellen Test abzuspielen, verwenden Sie die `MusicOnHold`‑Anwendung mit einer Dauer (in Sekunden):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Anwendungszuordnungen

Anwendungskarten ermöglichen es Ihnen, neue Funktionen hinzuzufügen, indem Sie den `[applicationmap]`‑Abschnitt der Datei features.conf verwenden. Angenommen, Sie müssen den Kundentyp identifizieren, den Sie in einem Callcenter beantworten. Sie könnten für jeden Kundentyp eine Anwendungskarte erstellen, die die Anzahl der beantworteten Kunden pro Typ zählen könnte.

## Zusammenfassung

In diesem Kapitel haben Sie gelernt, wo die PBX‑Funktionen von Asterisk leben — einige im Kern, einige im Dialplan und einige am Telefon — und wie die DTMF‑Feature‑Codes im `[featuremap]`‑Abschnitt von `features.conf` zugeordnet sind. Sie haben **Anrufweiterleitung** (blind und attended) und **Anrufparken** (`res_parking.conf`, mit den Dial‑Optionen `k`/`K` und dem `parkedcalls`‑Set) konfiguriert, **Anrufannahme** per Gruppe und **Konferenzen** mit **ConfBridge** (`confbridge.conf`‑Bridge/User/Menu‑Profile), das das alte MeetMe ersetzt. Sie haben **Ein‑Klick‑Aufnahme** mit MixMonitor (`automixmon`, die Dial‑Optionen `X`/`x` und `DYNAMIC_FEATURES`) eingerichtet, **Musik on Hold** konfiguriert und gesehen, wie **Application Maps** es Ihnen ermöglichen, Ihre eigene Dialplan‑Logik an eine DTMF‑Sequenz zu binden. Mit diesen Bausteinen können Sie die alltäglichen Funktionen bereitstellen, die Benutzer von einer Business‑PBX erwarten.

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
