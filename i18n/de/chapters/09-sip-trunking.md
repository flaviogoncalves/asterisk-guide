# SIP-Trunking, DID & das PSTN

Eine PBX, die nur sich selbst anrufen kann, ist nicht sehr nützlich. Früher oder später muss jedes System den Rest der Welt erreichen — das öffentliche Telefonnetz (PSTN), einen SIP-Provider oder eine andere PBX. Die Verbindung, die diese Anrufe überträgt, ist ein **Trunk**. In der TDM-Ära war ein Trunk ein physischer Schaltkreis: ein T1/E1 PRI oder ein Bündel analoger FXO-Leitungen. Heute ist es fast immer ein **SIP-Trunk** — eine logische Verbindung zu einem Internet Telephony Service Provider (ITSP), die über dasselbe IP-Netzwerk wie alles andere läuft.

Dieses Kapitel zeigt, wie man Asterisk 22 mit PJSIP mit einem ITSP verbindet, wie man zwischen einem registrierungsbasierten und einem IP-basierten Trunk wählt, wie man eingehende DID-Nummern an das richtige Ziel weiterleitet, wie man ausgehende Anrufe mit korrekter Caller-ID und E.164-Formatierung sendet und wie man Failover und Least-Cost-Routing über mehrere Trunks hinweg aufbaut. Wir schließen mit der NAT-Handhabung für Trunks und einem Labor ab, in dem ein zweiter Asterisk (und SIPp) als simulierter ITSP aufgesetzt wird, damit Sie echte Anrufe über einen Trunk tätigen können.

Alles hier ist anhand des Asterisk 22.10.0-Labors des Buches verifiziert; das Trunk-Objektmuster ist dasselbe, das in *Building your first PBX with PJSIP* und *SIP & PJSIP in depth* eingeführt wurde.

## Ziele

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Asterisk 22 mit PJSIP mit einem ITSP zu verbinden
- Zwischen registrierungsbasierten und IP-basierten (statischen) Trunks zu wählen
- Eingehende DIDs an die richtige Extension, IVR oder Queue weiterzuleiten
- Ausgehende Anrufe mit korrekter Caller-ID und E.164-Formatierung zu routen
- Trunk-Failover und Least-Cost-Routing mit `${DIALSTATUS}` aufzubauen
- NAT für Trunks auf Transport- und Endpoint-Ebene zu handhaben

## Was ist ein SIP-Trunk

Ein SIP-Trunk ist ein logischer Sprachpfad zwischen Ihrer PBX und einem anderen SIP-System. In der Praxis ist dieses „andere System“ eines von zwei Dingen:

- **Ein ITSP (Internet Telephony Service Provider).** Ein kommerzieller Anbieter, der Ihnen Anruforigination und -terminierung sowie in der Regel einen Block von Telefonnummern (DIDs) verkauft. Sie verweisen Asterisk auf den Signalisierungs-Host des Providers, und der Provider verbindet Ihre Anrufe mit dem weiteren PSTN. So erreichen die meisten modernen Systeme das Telefonnetz — ohne dass Telefonie-Hardware erforderlich ist.
- **Ein PSTN-Gateway.** Ein Gerät (oder ein anderer Asterisk), das über physische PSTN-Schnittstellen verfügt — eine PRI-Karte, analoge FXO-Ports oder ein GSM/4G-Gateway — und diese Ihrer PBX als SIP präsentiert. Das Gateway führt die TDM-zu-SIP-Konvertierung durch; aus Sicht von Asterisk ist es nur ein weiterer SIP-Trunk.

So oder so ist ein Trunk in PJSIP **nur ein Endpoint**. Dieselbe Objektfamilie, die Sie für ein Telefon verwendet haben — `endpoint`, `auth`, `aor`, optional `identify` und `registration` — baut einen Trunk auf. Die Unterschiede liegen im Detail: Ein Trunk authentifiziert *ausgehend* (Sie sind der Client, also kommen die Anmeldedaten in `outbound_auth`, nicht `auth`), er registriert normalerweise keinen User Agent bei Ihnen (Sie registrieren sich bei *ihm*, oder er sendet Ihnen Datenverkehr von einer bekannten IP), und er lässt eingehende Anrufe in einem dedizierten Context wie `from-pstn` statt `from-internal` landen.

> **Vergleich mit dem alten TDM-Trunk.** Ein PRI gab Ihnen eine feste Anzahl von B-Kanälen (23 bei einem T1, 30 bei einem E1) und signalisierte den Verbindungsaufbau über einen dedizierten D-Kanal (siehe das Kapitel *Legacy channels*). Ein SIP-Trunk hat keine feste Kanalanzahl — die Kapazität ist das, was Ihre Bandbreite, die Richtlinie Ihres Providers und etwaige `max_contacts`/Concurrent-Call-Limits zulassen. Caller-ID, DID und Anruffortschritt, die früher über ISDN-Informationselemente übertragen wurden, nutzen jetzt SIP-Header und SDP.

Es gibt zwei Möglichkeiten, wie ein ITSP zustimmt, Datenverkehr mit Ihnen auszutauschen, und diese bestimmen, wie Sie den Trunk aufbauen: **registrierungsbasiert** und **IP-basiert (statisch)**. Wir behandeln beide nacheinander.

## Registrierungsbasierte Trunks

Ein registrierungsbasierter Trunk ist das Modell, das verwendet wird, wenn der Provider erwartet, dass *Sie* sich bei *ihm* anmelden. Ihr Asterisk sendet regelmäßig ein SIP `REGISTER` an den Provider und authentifiziert sich mit Benutzername und Passwort, genau so, wie sich ein Telefon bei Ihrer PBX registriert. Dies ist üblich, wenn Ihre öffentliche IP dynamisch ist, wenn Sie sich hinter NAT befinden oder wenn der Provider Kunden einfach anhand von SIP-Anmeldedaten statt anhand der IP-Adresse identifiziert.

In PJSIP befindet sich die ausgehende Anmeldung in einem dedizierten `registration`-Objekt. Es ersetzt die einzelne `register =>`-Zeile, die der entfernte `chan_sip`-Treiber in `sip.conf` verwendete. Hier ist ein vollständiger registrierender Trunk zu einem fiktiven Provider, der dem verifizierten Muster aus den früheren Kapiteln folgt — beachten Sie `outbound_auth` (nicht `auth`), `server_uri`/`client_uri` (nicht `server`/`client`), `from_user`/`from_domain` am Endpoint und `dtmf_mode=rfc4733`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

Ein paar Dinge, die zu beachten sind:

- **`auth_type=digest`, nicht `userpass`.** Beide erzeugen dieselbe Digest-Authentifizierung, aber in Asterisk 22 sind `userpass` (und das alte `md5`) **veraltet und werden stillschweigend in `digest` konvertiert**. Bevorzugen Sie `digest` in neuen Konfigurationen; Sie werden `userpass` immer noch in älteren Dateien und in den früheren Kapiteln dieses Buches sehen.
- **`outbound_auth` sowohl am Endpoint als auch bei der Registration.** Die Registration verwendet es, um die `REGISTER` zu authentifizieren; der Endpoint verwendet es, um auf das `407 Proxy Authentication Required` zu antworten, das der Provider auf ein ausgehendes `INVITE` zurücksendet. Sie können sich ein `auth`-Objekt teilen.
- **`from_user` / `from_domain`.** Viele Provider lehnen Anrufe ab, deren `From`-Header nicht Ihre Kontonummer und deren Domain enthält. Diese beiden Optionen setzen genau das.
- **`contact_user=4830001000`.** Dies wird zum User-Teil des `Contact`, den Sie registrieren, damit der Provider weiß, an welche Nummer er eingehende Anrufe zustellen soll. Es ist das moderne Äquivalent zum `/9999`-Suffix in der alten `register =>`-Zeile.
- **`retry_interval=60`.** Wenn die Registrierung fehlschlägt, versuchen Sie es alle 60 Sekunden erneut.

Bestätigen Sie nach einem Reload die Registrierung mit `pjsip show registrations`. Im Labor — wo `itsp.example.com` nicht tatsächlich antwortet — sieht die Tabelle so aus:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

Das `(exp. Ns)`-Suffix zählt die Sekunden bis zum nächsten Versuch herunter; sobald es Null erreicht, liest es kurz `(exp. Ns ago)`, bevor der erneute Versuch ausgelöst wird. Bei einem Live-Provider liest die `Status`-Spalte `Registered` mit den verbleibenden Sekunden bis zur nächsten Aktualisierung. `Rejected` (oder `Unregistered`) bedeutet, dass der Provider die Anmeldung nicht akzeptiert hat — schalten Sie `pjsip set logger on` ein und lesen Sie die `401`/`403`-Antwort, fast immer ein falscher Benutzername, ein falsches Passwort oder eine falsche `client_uri`-Domain.

## IP-basierte (statische) Trunks

Das zweite Modell benötigt überhaupt keine Registrierung. Der Provider kennt Ihre öffentliche IP-Adresse und sendet Anrufe direkt an diese; Sie wiederum senden Anrufe an die bekannte Signalisierungs-IP des Providers. Die Authentifizierung erfolgt über die **Quell-IP-Adresse**, nicht über SIP-Anmeldedaten. Dies ist typisch für Trunks zwischen zwei Servern, die Sie kontrollieren, oder für einen Enterprise-Trunk, bei dem beide Seiten statische Adressen haben.

Das Schlüsselobjekt ist `identify`. Es sagt Asterisk: „Jede SIP-Anfrage, die von *dieser* IP ankommt, gehört zu *diesem* Endpoint.“ Ohne dies versucht PJSIP, eine eingehende Anfrage anhand des `From`-Users einem Endpoint zuzuordnen, was der Datenverkehr eines Carriers nicht erfüllen wird — daher würde der Anruf abgelehnt oder an den `anonymous`-Endpoint fallen.

Ein statischer Trunk lässt das `registration`-Objekt weg und fügt `identify` hinzu:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` akzeptiert eine IP-Adresse, einen CIDR-Bereich oder einen Hostnamen. **Hostnamen werden nur einmal beim Laden der Konfiguration aufgelöst**, wenn sich also die IP Ihres Providers ändert, müssen Sie neu laden. Für einen Carrier, der mehrere Media-Gateways veröffentlicht, listen Sie jede Signalisierungs-IP auf — Sie können `match` wiederholen oder ein CIDR angeben:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Überprüfen Sie mit `pjsip show identifies`, was Asterisk akzeptieren wird. Erfasst aus dem Labor (die `sipp-identify`-Zeile ist der bereits existierende SIPp-Endpoint des Labors):

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### Die Sicherheitsimplikation

Ein IP-basierter Trunk ohne Authentifizierung ist eine Tür, und `identify`/`match` ist das einzige Schloss daran. Wenn Sie `match` einen zu breiten Bereich wählen — oder wenn ein Angreifer eine Quell-IP fälschen kann — landen Anrufe unauthentifiziert in Ihrem `from-pstn`-Context. Zwei Verteidigungsmaßnahmen, die zusammen verwendet werden:

- **So eng wie möglich abgleichen.** Bevorzugen Sie spezifische Host-IPs gegenüber weiten CIDRs. Nur die echten Signalisierungs-IPs des Providers gehören in `match`.
- **Koppeln Sie es mit einer ACL.** PJSIP kann Datenverkehr auf der SIP-Ebene verwerfen, bevor er jemals einen Endpoint erreicht, indem ein `type=acl`-Objekt (oder `acl.conf`) verwendet wird:

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Referenzieren Sie es aus dem globalen Abschnitt (`acl=itsp-acl` in `[global]`/`type=global`) oder wenden Sie es pro Transport an. Das Prinzip ist dasselbe wie im SIP-Kapitel: Alles verweigern, dann nur das erlauben, dem Sie vertrauen. Und was auch immer Ihr Trunk-Context tut, **lassen Sie ihn niemals einen Context erreichen, der ohne eine bewusste, authentifizierte Regel zurück zum PSTN wählen kann** — das ist das klassische Loch für Gebührenbetrug.

> **Welches Modell sollte ich verwenden?** Wenn der Provider Ihnen einen Benutzernamen und ein Passwort gibt, verwenden Sie einen **Registrierungs-Trunk**. Wenn er nach Ihrer IP-Adresse fragt und Ihnen seine gibt, verwenden Sie einen **Identify-Trunk**. Einige Provider unterstützen beides; viele echte Trunks kombinieren eine Registrierung (damit der Provider Sie finden kann) mit einem Identify (damit eingehende INVITEs von den Media-Gateways des Providers auch dann zugeordnet werden, wenn sie von einer anderen IP als der des Registrars ankommen).

## Eingehendes Routing und DID-Handhabung

Sobald eingehende Anrufe ankommen, landen sie im `context` des Endpoints — hier `from-pstn`. Eine **DID** (Direct Inward Dialing-Nummer) ist einfach die gewählte Nummer, die der Provider Ihnen im Request-URI übergibt. Ihre Aufgabe im Dialplan ist es, jede DID einem Ziel zuzuordnen: einer einzelnen Extension, einer IVR, einer Queue oder einer Ring-Gruppe.

Die Nummer, die der Provider sendet, wird als `${EXTEN}` in `from-pstn` abgeglichen. Wie viel davon Sie sehen, hängt vom Provider ab — einige senden die vollständige E.164-Nummer (`+4830001000`), einige senden die nationale Nummer, einige senden nur die letzten paar Ziffern. Untersuchen Sie einen echten eingehenden Anruf mit `pjsip set logger on` und schauen Sie sich den Request-URI an, bevor Sie Muster schreiben.

### Eine DID zu einer Extension

Der einfachste Fall — eine einzelne DID, die direkt an ein Telefon weitergeleitet wird:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### Eine DID zu einer IVR (Auto-Attendant)

Eine Hauptnummer, die mit einem Menü antworten soll, anstatt ein Telefon klingeln zu lassen:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` ist der Auto-Attendant-Context, den Sie in den Dialplan-Kapiteln erstellt haben (`Background()` + `WaitExten()`). Das Routing der DID ist nur ein `Goto`.

### Eine DID zu einer Queue

Eine Support-Leitung, die in einer Anruf-Queue landen soll:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Viele DIDs auf einmal

Wenn Sie einen Nummernblock kaufen, hält ein Muster den Dialplan klein. Angenommen, Ihr DID-Bereich ist `4830003000`–`4830003099` und der Provider sendet die vollständige Nummer; ordnen Sie die letzten zwei Ziffern jeder DID der Extension `60xx` zu:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` nimmt die letzten zwei Ziffern (negativer Offset zählt von rechts), also klingelt `4830003007` bei `PJSIP/6007`. Eine `did => extension`-Nachschlagetabelle, die mit `GoSub` oder einer Asterisk-Datenbank (`AstDB`/`func_odbc`) erstellt wurde, skaliert noch weiter, aber für eine Handvoll Nummern sind explizite Muster am übersichtlichsten.

> **Die nicht zugeordnete DID abfangen.** Fügen Sie eine `i` (invalid)-Extension zu `from-pstn` hinzu, damit eine falsch geroutete eingehende Nummer eine Ansage abspielt oder den Operator klingeln lässt, anstatt stillschweigend abzubrechen:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Ausgehendes Routing, Caller-ID und E.164

Ausgehende Anrufe fließen in die andere Richtung: Ein internes Telefon wählt eine Nummer, Ihr Dialplan gleicht sie ab, entfernt ein etwaiges Zugangspräfix, setzt die Caller-ID, die der Provider erwartet, und übergibt den Anruf mit `Dial(PJSIP/<number>@itsp)` an den Trunk-Endpoint.

### Den Anruf an den Trunk senden

Die Kanal-Syntax für einen Trunk ist `PJSIP/<number>@<endpoint>`: Der Teil vor dem `@` wird zum User-Teil des ausgehenden Request-URI, und der Teil nach dem `@` benennt den Endpoint, dessen `aor` `contact` den Ziel-Host liefert. Eine klassische „Wähle 9 für eine Außenleitung“-Regel:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` entfernt den führenden `9`-Zugangscode, bevor die Nummer gesendet wird. Das Muster `_9NXXXXXXXXX` gleicht `9` plus eine 10-stellige Nummer ab, deren erste Ziffer 2–9 ist; passen Sie es an Ihren Dialplan an.

### Caller-ID bei ausgehenden Anrufen

Die meisten ITSPs ignorieren — oder lehnen aktiv — eine Caller-ID ab, die keine Nummer ist, die Sie besitzen. Setzen Sie die ausgehende Caller-ID-Nummer vor `Dial()` mit der `CALLERID(num)`-Funktion auf eine Ihrer DIDs, wie oben gezeigt. Sie können auch den Namen setzen:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Wenn der Provider Ihren Caller-ID-Namen trotzdem entfernt oder überschreibt, ist das seine Richtlinie — viele Carrier beziehen den angezeigten Namen aus ihrer eigenen CNAM-Datenbank, basierend auf der Nummer, nicht aus Ihrem `From`-Header.

Zwei Endpoint-Optionen interagieren damit:

- **`from_user`** setzt den User-Teil des `From`-Headers auf SIP-Ebene, was einige Provider verwenden, um Ihr Konto unabhängig von `CALLERID(num)` zu identifizieren.
- **`trust_id_outbound`** (Standard `no`) steuert, ob Asterisk datenschutzrelevante Identitäts-Header (`P-Asserted-Identity`/`P-Preferred-Identity`) ausgehend sendet. Lassen Sie es aus, es sei denn, Ihr Provider dokumentiert, dass er PAI wünscht; in diesem Fall setzen Sie `trust_id_outbound=yes` und `send_pai=yes`.

### Normalisierung auf E.164

E.164 ist das internationale Nummernformat: ein führendes `+`, Ländercode, dann die nationale Nummer, ohne Leerzeichen oder Satzzeichen (zum Beispiel `+5548999990000` oder `+14155550100`). Carrier erwarten — oder verlangen — zunehmend E.164 auf dem Trunk. Anstatt die Formatierung über den Dialplan zu verteilen, normalisieren Sie einmal im ausgehenden Context.

Ein nordamerikanisches Beispiel, das eine 10-stellige lokale Nummer, eine 11-stellige `1`-vorangestellte Nummer oder eine bereits E.164-konforme Nummer akzeptiert und dem Trunk immer `+1…` präsentiert:

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

Einige Provider wollen das `+`; andere wollen die nackten Ziffern. Wenn Ihrer das `+` ablehnt, entfernen Sie es auf dem Weg nach draußen mit `${EXTEN:1}` im `Dial`. Der Punkt ist, dass das gesamte Formatwissen an einem Ort lebt, sodass der Wechsel des Providers — oder das Hinzufügen eines zweiten — eine Ein-Zeilen-Änderung ist.

## Failover und Least-Cost-Routing

Mit einem Trunk bedeutet ein Provider-Ausfall keine ausgehenden Anrufe. Mit zwei oder mehr können Sie automatisch ein Failover durchführen und sogar die günstigste Route pro Ziel wählen — *Least-Cost-Routing* (LCR).

### Failover mit `${DIALSTATUS}`

`Dial()` setzt die `${DIALSTATUS}`-Kanalvariable, wenn es zurückkehrt. Die Werte, die für Failover wichtig sind, sind `CHANUNAVAIL` (der Trunk konnte überhaupt nicht erreicht werden) und `CONGESTION` (der Anruf wurde abgelehnt, z. B. alle Leitungen belegt). Versuchen Sie den primären Trunk; wenn er den Anruf nicht tragen konnte, fallen Sie auf den Backup zurück:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Beachten Sie die bewusste Entscheidung, **nicht** bei `BUSY` oder `NOANSWER` ein Failover durchzuführen — diese bedeuten, dass die *angerufene Partei* erreicht wurde und abgelehnt hat, also würde ein erneuter Versuch auf einem anderen Trunk ein Telefon erneut klingeln lassen, das bereits Nein gesagt hat (und könnte Sie einen zweiten Anruf kosten). Routen Sie nur um, wenn der *Trunk selbst* fehlgeschlagen ist.

### Eine wiederverwendbare Routing-Subroutine

Diese Logik für jedes Wählmuster zu wiederholen, ist fehleranfällig. Fassen Sie sie in einer `GoSub`-Routine zusammen, die die Zielnummer nimmt und jeden Trunk der Reihe nach versucht:

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

Jetzt ist jedes ausgehende Muster ein `GoSub`-Aufruf, und die Trunk-Reihenfolge ist an genau einer Stelle definiert.

### Least-Cost-Routing nach Ziel

Wahres LCR wählt den Trunk danach aus, wohin der Anruf geht. Eine übliche Form ist es, das Zielpräfix abzugleichen und jede Anrufklasse an den Provider zu senden, der dafür am günstigsten ist — zum Beispiel internationale Anrufe an einen Wholesale-Carrier und lokale/nationale Anrufe an Ihren primären:

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

Für mehr als ein paar Präfixe speichern Sie die Routentabelle in einer Datenbank (`func_odbc`/`AstDB`) und schlagen Sie den Trunk nach Präfix nach, anstatt Muster fest zu kodieren. Der Dialplan bleibt klein und die Tarife leben in einer Tabelle, die Sie bearbeiten können, ohne die Logik neu zu laden.

## NAT und Trunks

NAT ist die häufigste Ursache für Trunk-Probleme — typischerweise einseitiges Audio oder ein Trunk, der sich registriert, aber niemals eingehende Anrufe empfängt. Die Ursache ist dieselbe wie bei Telefonen (behandelt in *SIP & PJSIP in depth* und *Designing a VoIP network*): Asterisk bewirbt seine eigene Vorstellung seiner Adresse in SIP und SDP, und hinter NAT ist das eine private RFC 1918-Adresse, zu der der Provider nicht zurückrouten kann.

Für Trunks hat die Lösung zwei Teile — Einstellungen am **Transport** (Ihre öffentliche Adresse) und Einstellungen am **Endpoint** (wie die Medien des Providers behandelt werden).

### Am Transport — Ihre öffentliche Adresse

Wenn der Asterisk-Server selbst hinter NAT steht (eine Cloud- oder On-Prem-Box mit einer privaten IP und einer 1:1 öffentlichen IP), teilen Sie dem Transport seine öffentliche Adresse mit und welche Netzwerke lokal sind. Diese Optionen werden einmal am `transport` gesetzt und gelten für den gesamten Datenverkehr darüber:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — die öffentliche IP, die Asterisk in SIP-Header (`Via`, `Contact`) für Ziele außerhalb von `local_net` schreibt.
- **`external_media_address`** — die öffentliche IP, die Asterisk in die SDP `c=`-Zeile schreibt, damit RTP an den richtigen Ort zurückkommt. Normalerweise identisch mit der Signalisierungsadresse.
- **`local_net`** — Netzwerke, die Asterisk als intern behandelt, sodass es Adressen für LAN-Peers *nicht* umschreibt. Listen Sie jedes interne Subnetz auf.

### Am Endpoint — die Medien des Providers

Die andere Hälfte handhabt einen Provider, der selbst hinter NAT sitzt oder Medien einfach von einer anderen Adresse sendet als der, die im SDP steht. Setzen Sie diese pro Trunk-Endpoint:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — halten Sie Medien durch Asterisk fließend, anstatt die beiden Beine direkt miteinander sprechen zu lassen. Unerlässlich über NAT und ohnehin erforderlich, wenn Sie den Anruf aufzeichnen, transkodieren oder überwachen möchten.
- **`rtp_symmetric=yes`** — das klassische *comedia*-Verhalten: Senden Sie RTP an die Adresse zurück, von der die Medien tatsächlich kamen, nicht an die Adresse, die das SDP behauptet.
- **`force_rport=yes`** — antworten Sie auf SIP von der Quell-IP/Port der Anfrage (RFC 3581), anstatt dem `Via`-Header zu vertrauen.
- **`rewrite_contact=yes`** — schreiben Sie bei eingehenden SIP-Nachrichten von diesem Endpoint den `Contact`-Header (oder einen geeigneten `Record-Route`-Header) auf die Quell-IP-Adresse und den Port um, von denen das Paket tatsächlich kam. Laut der eigenen Dokumentation der Option hilft dies „Servern, mit Endpoints zu kommunizieren, die sich hinter NATs befinden“ und „hilft bei der Wiederverwendung zuverlässiger Transportverbindungen wie TCP und TLS.“

> **Empfehlung — Telefone vs. Trunks.** `rewrite_contact` ist fast immer die richtige Wahl für Telefone, da ihr beworbener Kontakt typischerweise eine private RFC 1918-Adresse ist, die nicht zu ihnen zurückroutbar ist. Bei einem statischen IP-basierten Trunk ist der Kontakt des Providers normalerweise bereits eine korrekte öffentliche Adresse, daher ist ein Umschreiben oft unnötig; einige Betreiber ziehen es vor, es dort wegzulassen und nur für Registrierungs-Trunks und NAT-Telefone zu aktivieren. Der dokumentierte Effekt der Option ist rein das oben genannte eingehende `Contact`/`Record-Route`-Umschreiben — daher ist die sichere Praxis, gegen Ihren spezifischen Carrier zu testen, bevor Sie es auf einem statischen Trunk aktivieren.

Sie können die effektiven Einstellungen an jedem Endpoint mit `pjsip show endpoint <name>` bestätigen — `direct_media`, `rtp_symmetric`, `force_rport`, `rewrite_contact` und der Rest werden alle im Parameter-Dump ausgegeben.

## Labor — ein simulierter ITSP mit einem zweiten Asterisk und SIPp

Sie benötigen keinen bezahlten Trunk zum Üben. Das Labor des Buches betreibt bereits einen Asterisk 22.10.0-Container und einen SIPp-Container in einem privaten `172.30.0.0/24`-Netzwerk; wir werden den SIPp-Container als den „Carrier“ behandeln, der eingehende Anrufe tätigt, und einen Trunk-Endpoint hinzufügen, der diese Anrufe in einem `from-pstn`-Context landen lässt.

![Ein SIP-Trunk zwischen der Asterisk PBX und dem ITSP: Die PBX registriert sich als ein Konto, ausgehende Anrufe wählen `PJSIP/<num>@trunk`, und eingehende Anrufe landen im `from-pstn`-Context.](../images/09-sip-trunking-fig01.png)

### 1. Den Trunk-Endpoint hinzufügen

Fügen Sie einen IP-basierten Trunk zu `lab/asterisk/etc/pjsip.conf` hinzu, der mit dem SIPp-Host des Labors übereinstimmt und eingehende Anrufe in `from-pstn` landen lässt:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. Die eingehende DID routen

Fügen Sie in `lab/asterisk/etc/extensions.conf` einen `from-pstn`-Context hinzu, der die DID beantwortet, die der simulierte Carrier wählen wird, und sie wiedergibt, fügen Sie dann eine ausgehende Regel hinzu:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

Laden Sie beide Dateien neu (`core reload`) und überprüfen Sie, ob der Trunk geladen wurde:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Einen eingehenden Anruf über den Trunk tätigen

Richten Sie ein SIPp-Szenario mit der DID als Ziel-User auf die PBX. Das Labor liefert bereits `lab/sipp/uac_9000.xml`, das die Extension `9000` INVITEt; kopieren Sie es nach `uac_did.xml` und ändern Sie den Request-URI/`To`-User von `9000` auf `4830001000`, führen Sie es dann vom SIPp-Container aus:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Beobachten Sie, wie der Anruf auf der Asterisk-Konsole auf `from-pstn` trifft (`pjsip set logger on` zeigt das eingehende INVITE; `core show channels` zeigt den `PJSIP/itsp-…`-Kanal, der `demo-congrats` abspielt). Da die SIPp-Quell-IP mit dem `identify` übereinstimmt, wird der Anruf ohne Authentifizierung akzeptiert — genau so, wie sich ein statischer Carrier-Trunk verhält.

### 4. Den Trunk untersuchen

Erfassen Sie die vollständige Konfiguration des Trunks für Ihre Notizen:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Zusatz) Machen Sie daraus einen Registrierungs-Trunk

Setzen Sie den *zweiten* Asterisk-Container als echten Registrar auf: Geben Sie ihm ein `endpoint`+`auth`+`aor` für das Konto `4830001000`, tauschen Sie dann auf der PBX den `identify`-Block gegen den `registration`-Block vom Anfang dieses Kapitels aus (und verweisen Sie `server_uri` auf die IP des zweiten Containers). Bestätigen Sie mit `pjsip show registrations`, dass der Status `Registered` lautet, und tätigen Sie dann einen Anruf in jede Richtung.

## Zusammenfassung

Ein SIP-Trunk verbindet Ihre PBX mit der Außenwelt, und in PJSIP ist er nur ein Endpoint, der aus derselben `endpoint` + `auth` + `aor`-Familie aufgebaut ist, die Sie bereits kennen, plus einem `identify` oder einem `registration`. Verwenden Sie einen **Registrierungs-Trunk** (`type=registration` mit `outbound_auth`), wenn der Provider Ihnen einen Benutzernamen und ein Passwort gibt; verwenden Sie einen **IP-basierten Trunk** (`type=identify` mit `match`), wenn die Authentifizierung über die Quell-IP erfolgt — und sichern Sie letzteren mit einem engen `match` und einer `acl` ab, da ein unauthentifizierter Trunk ein Ziel für Gebührenbetrug ist. Eingehend kommt die DID des Providers als `${EXTEN}` in Ihrem `9`-Context an, wo Sie sie an eine Extension, eine IVR oder eine Queue routen — Muster und `${EXTEN:-N}` halten DID-Blöcke kompakt. Setzen Sie ausgehend `CALLERID(num)` auf eine Nummer, die Sie besitzen, normalisieren Sie an einer Stelle auf E.164 und übergeben Sie den Anruf an `PJSIP/<number>@trunk`. Bauen Sie Resilienz auf, indem Sie mehrere Trunks versuchen und bei `${DIALSTATUS}` verzweigen (`CHANUNAVAIL`/`CONGESTION` bedeuten Umrouten; `BUSY`/`NOANSWER` nicht), und legen Sie Least-Cost-Routing in eine `GoSub`-Tabelle. Schließlich ist NAT für Trunks zweiseitig: `external_media_address`/`external_signaling_address`/`local_net` am **Transport** für Ihre öffentliche Adresse und `direct_media=no`, `rtp_symmetric`, `force_rport` und `rewrite_contact` am **Endpoint** für die Medien des Providers.

## Quiz

1. In PJSIP werden die Anmeldedaten, die zur Authentifizierung eines *ausgehenden* Anrufs oder einer Registrierung bei einem Provider verwendet werden, referenziert mit:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Sie sollten einen `type=registration`-Trunk verwenden, wenn:
   - A. Der Provider Sie anhand Ihrer Quell-IP-Adresse identifiziert.
   - B. Der Provider Ihnen einen Benutzernamen und ein Passwort gibt und erwartet, dass Sie sich anmelden.
   - C. Sie niemals möchten, dass Asterisk ein `REGISTER` sendet.
   - D. Der Trunk zwischen zwei Servern mit statischer IP ist, die Sie kontrollieren.
3. Die `match`-Option des `identify`-Objekts akzeptiert (wählen Sie alle zutreffenden aus):
   - A. Eine IP-Adresse
   - B. Einen CIDR-Bereich
   - C. Einen Hostnamen (aufgelöst beim Laden der Konfiguration)
   - D. Nur einen SIP-Benutzernamen
4. Auf Asterisk 22 ist `auth_type=userpass`:
   - A. Der einzige gültige Wert
   - B. Veraltet und in `digest` konvertiert
   - C. Entfernt und verursacht einen Ladefehler
   - D. Erforderlich für die ausgehende Registrierung
5. Eine eingehende DID-Nummer kommt im Dialplan an als:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` im `context` des Trunk-Endpoints
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Um die letzten zwei Ziffern der gewählten DID `4830003007` an eine Extension zu senden, würden Sie verwenden:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Nach `Dial()` an einen Trunk sollten Sie auf einen Backup-Trunk ausweichen, bei welchen `${DIALSTATUS}`-Werten (wählen Sie zwei)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Um die Caller-ID-Nummer zu setzen, die dem Provider vor dem Rauswählen präsentiert wird, verwenden Sie:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Die Optionen, die Asterisk seine *öffentliche* Adresse mitteilen, wenn der Server hinter NAT steht, werden gesetzt am:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` an einem Trunk-Endpoint bewirkt, dass Asterisk:
    - A. RTP mit SRTP verschlüsselt
    - B. RTP an die Adresse zurücksendet, von der die Medien tatsächlich kamen, unter Ignorierung des SDP
    - C. RTP vollständig deaktiviert
    - D. Direkte Medien zwischen Endpoints erzwingt

**Antworten:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
