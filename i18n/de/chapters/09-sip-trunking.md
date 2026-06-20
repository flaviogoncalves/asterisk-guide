# SIP trunking, DID & the PSTN

Eine PBX, die nur sich selbst anrufen kann, ist nicht sehr nützlich. Früher oder später muss jedes System den Rest der Welt erreichen — das öffentliche Telefonnetz (PSTN), einen SIP‑Provider oder eine andere PBX. Die Verbindung, die diese Anrufe transportiert, ist ein **trunk**. In der TDM‑Ära war ein trunk ein physischer Stromkreis: ein T1/E1‑PRI oder ein Bündel analoger FXO‑Leitungen. Heute ist es fast immer ein **SIP trunk** — eine logische Verbindung zu einem Internet Telephony Service Provider (ITSP), die über dasselbe IP‑Netzwerk wie alles andere transportiert wird.

Dieses Kapitel zeigt, wie man Asterisk 22 mit PJSIP an einen ITSP anschließt, wie man zwischen einem registrierungsbasierten und einem IP‑basierten trunk wählt, wie man eingehende DID‑Nummern zum richtigen Ziel routet, wie man ausgehende Anrufe mit korrekter caller‑ID und E.164‑Formatierung sendet und wie man Failover‑ und Least‑Cost‑Routing über mehrere trunks aufbaut. Wir schließen mit NAT‑Handling für trunks und einem Labor ab, das eine zweite Asterisk (und SIPp) als Mock‑ITSP bereitstellt, sodass Sie reale Anrufe über einen trunk tätigen können.

Alles hier ist gegen das Labor der Buchversion Asterisk 22.10.0 verifiziert; das trunk‑Objekt‑Muster ist dasselbe, das in *Building your first PBX with PJSIP* und *SIP & PJSIP in depth* eingeführt wurde.

## Objectives

Am Ende dieses Kapitels sollten Sie in der Lage sein:

- Asterisk 22 mit einem ITSP über PJSIP zu verbinden
- zwischen registrierungsbasierten und IP‑basierten (statischen) Trunks zu wählen
- eingehende DIDs zur richtigen Extension, IVR oder Warteschlange zu routen
- ausgehende Anrufe mit korrekter Caller‑ID und E.164‑Formatierung zu routen
- Trunk‑Failover und Least‑Cost‑Routing mit `${DIALSTATUS}` aufzubauen
- NAT für Trunks auf dem Transport und dem Endpoint zu handhaben

## What is a SIP trunk

Ein SIP‑Trunk ist ein logischer Sprachpfad zwischen Ihrer PBX und einem anderen SIP‑System. In der Praxis ist dieses „andere System“ eines von beiden:

- **Ein ITSP (Internet Telephony Service Provider).** Ein kommerzieller Carrier, der Ihnen Anruf‑Origination und -Termination sowie in der Regel einen Block von Telefonnummern (DIDs) verkauft. Sie zeigen Asterisk auf den Signalisierungs‑Host des Anbieters, und der Anbieter verbindet Ihre Anrufe mit dem breiteren PSTN. So erreichen die meisten modernen Systeme das Telefonnetz – ohne Telefonie‑Hardware.
- **Ein PSTN‑Gateway.** Ein Gerät (oder ein weiteres Asterisk), das physische PSTN‑Schnittstellen besitzt – eine PRI‑Karte, analoge FXO‑Ports oder ein GSM/4G‑Gateway – und diese Ihrem PBX als SIP bereitstellt. Das Gateway übernimmt die TDM‑zu‑SIP‑Konvertierung; aus Asterisk‑Sicht ist es einfach ein weiterer SIP‑Trunk.

In beiden Fällen ist ein Trunk in PJSIP **nur ein Endpoint**. Die gleiche Objektfamilie, die Sie für ein Telefon verwendet haben – `endpoint`, `auth`, `aor`, optional `identify` und `registration` – baut einen Trunk. Die Unterschiede liegen im Detail: Ein Trunk authentifiziert *ausgehend* (Sie sind der Client, daher gehen die Anmeldedaten in `outbound_auth`, nicht in `auth`), er registriert in der Regel keinen User‑Agent bei Ihnen (Sie registrieren sich *bei ihm*, oder er sendet Ihnen Verkehr von einer bekannten IP), und er legt eingehende Anrufe in einem dedizierten Kontext wie `from-pstn` statt `from-internal` ab.

> **Im Vergleich zum alten TDM‑Trunk.** Ein PRI gab Ihnen eine feste Anzahl von B‑Kanälen (23 auf einem T1, 30 auf einem E1) und signalisierte den Anrufaufbau über einen dedizierten D‑Kanal (siehe das Kapitel *Legacy channels*). Ein SIP‑Trunk hat keine feste Kanalzahl – die Kapazität richtet sich nach Ihrer Bandbreite, den Richtlinien Ihres Anbieters und allen `max_contacts`/gleichzeitigen Anruf‑Beschränkungen. Caller‑ID, DID und Anruf‑Fortschritt, die früher ISDN‑Informationselemente nutzten, reisen jetzt in SIP‑Headern und SDP.

Es gibt zwei Wege, wie ein ITSP dem Austausch von Verkehr mit Ihnen zustimmt, und sie bestimmen, wie Sie den Trunk aufbauen: **registrierungsbasiert** und **IP‑basiert (statisch)**. Wir behandeln beide nacheinander.

## Registration-based trunks

Ein registration-basierter Trunk ist das Modell, das verwendet wird, wenn der Provider erwartet, dass *Sie* sich bei *ihm* anmelden. Ihr Asterisk sendet periodisch ein SIP `REGISTER` an den Provider und authentifiziert sich mit einem Benutzernamen und Passwort, genau wie ein Telefon sich bei Ihrer PBX registriert. Dies ist üblich, wenn Ihre öffentliche IP dynamisch ist, wenn Sie sich hinter NAT befinden oder wenn der Provider Kunden einfach anhand von SIP‑Anmeldedaten statt anhand der IP‑Adresse identifiziert.

In PJSIP befindet sich das ausgehende Login in einem dedizierten `registration`‑Objekt. Es ersetzt die einzelne `register =>`‑Zeile, die der entfernte `chan_sip`‑Treiber in `sip.conf` verwendet hat. Hier ist ein vollständiger Registrierungs‑Trunk zu einem fiktiven Provider, der dem verifizierten Muster aus den vorherigen Kapiteln folgt – beachten Sie `outbound_auth` (nicht `auth`), `server_uri`/`client_uri` (nicht `server`/`client`), `from_user`/`from_domain` am Endpoint und `dtmf_mode=rfc4733`:

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

Einige Dinge, die auffallen:

- **`auth_type=digest`, nicht `userpass`.** Beide erzeugen dieselbe Digest‑Authentifizierung, aber in Asterisk 22 sind `userpass` (und das alte `md5`) **veraltet und werden stillschweigend in `digest` konvertiert**. Verwenden Sie `digest` in neuer Konfiguration; Sie werden `userpass` noch in älteren Dateien und in den vorherigen Kapiteln dieses Buches sehen.
- **`outbound_auth` sowohl am Endpoint als auch an der Registrierung.** Die Registrierung verwendet es, um den `REGISTER` zu authentifizieren; der Endpoint verwendet es, um die `407 Proxy Authentication Required` zu beantworten, die der Provider an ein ausgehendes `INVITE` zurücksendet. Sie können ein gemeinsames `auth`‑Objekt teilen.
- **`from_user` / `from_domain`.** Viele Provider lehnen Anrufe ab, deren `From`‑Header nicht Ihre Kontonummer und deren Domain enthält. Diese beiden Optionen setzen genau das.
- **`contact_user=4830001000`.** Dies wird zum Benutzer‑Teil des `Contact`, das Sie registrieren, sodass der Provider weiß, an welche Nummer eingehende Anrufe zugestellt werden sollen. Es ist das moderne Gegenstück zum `/9999`‑Suffix in der alten `register =>`‑Zeile.
- **`retry_interval=60`.** Bei fehlgeschlagener Registrierung alle 60 Sekunden erneut versuchen.

Nach einem Reload bestätigen Sie die Registrierung mit `pjsip show registrations`. Im Labor – wo `itsp.example.com` tatsächlich nicht antwortet – sieht die Tabelle so aus:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

Der `(exp. Ns)`‑Suffix zählt die Sekunden bis zum nächsten Versuch herunter; sobald er Null erreicht, wird kurzzeitig `(exp. Ns ago)` angezeigt, bevor der erneute Versuch ausgelöst wird. Bei einem Live‑Provider zeigt die Spalte `Status` `Registered` mit den verbleibenden Sekunden bis zur nächsten Aktualisierung. `Rejected` (oder `Unregistered`) bedeutet, dass der Provider die Anmeldung nicht akzeptiert hat – aktivieren Sie `pjsip set logger on` und lesen Sie die `401`/`403`‑Antwort, fast immer ein falscher Benutzername, Passwort oder `client_uri`‑Domain.

## IP-basierte (statische) Trunks

Das zweite Modell benötigt überhaupt keine Registrierung. Der Provider kennt Ihre öffentliche IP‑Adresse und sendet Anrufe direkt dorthin; Sie senden im Gegenzug Anrufe an die dem Provider bekannte Signalisierungs‑IP. Die Authentifizierung erfolgt über die **Quell‑IP‑Adresse**, nicht über SIP‑Anmeldedaten. Dies ist typisch für Trunks zwischen zwei Servern, die Sie kontrollieren, oder für einen Unternehmens‑Trunk, bei dem beide Seiten statische Adressen haben.

Das Schlüsselelement ist `identify`. Es sagt Asterisk: „Jede SIP‑Anfrage, die von *dieser* IP kommt, gehört zu *jenem* Endpunkt.“ Ohne dieses Element versucht PJSIP, eine eingehende Anfrage anhand des `From`‑Benutzers einem Endpunkt zuzuordnen, was bei einem Carrier‑Verkehr nicht erfüllt wird – sodass der Anruf abgelehnt oder an den `anonymous`‑Endpunkt weitergeleitet würde.

Ein statischer Trunk lässt das `registration`‑Objekt weg und fügt `identify` hinzu:

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

`match` akzeptiert eine IP‑Adresse, einen CIDR‑Bereich oder einen Hostnamen. **Hostnamen werden einmalig beim Laden der Konfiguration aufgelöst**, sodass Sie bei einer IP‑Änderung des Providers neu laden müssen. Für einen Carrier, der mehrere Media‑Gateways veröffentlicht, listen Sie jede Signalisierungs‑IP auf – Sie können `match` wiederholen oder einen CIDR angeben:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Überprüfen Sie, was Asterisk akzeptiert, mit `pjsip show identifies`. Aufgezeichnet aus dem Labor (die `sipp-identify`‑Zeile ist das bereits vorhandene SIPp‑Endpunkt des Labors):

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

### Die sicherheitstechnische Auswirkung

Ein IP‑basierter Trunk ohne Authentifizierung ist eine Tür, und `identify`/`match` ist das einzige Schloss daran. Wenn Sie `match` einen zu breiten Bereich – oder wenn ein Angreifer eine Quell‑IP fälschen kann – landen Anrufe in Ihrem `from-pstn`‑Kontext unauthentifiziert. Zwei Abwehrmaßnahmen, zusammen verwendet:

- **So eng wie möglich abgleichen.** Bevorzugen Sie spezifische Host‑IPs gegenüber breiten CIDRs. Nur die echten Signalisierungs‑IPs des Providers gehören in `match`.
- **Kombinieren Sie es mit einer ACL.** PJSIP kann Verkehr bereits auf der SIP‑Ebene abweisen, bevor er überhaupt einen Endpunkt erreicht, indem ein `type=acl`‑Objekt (oder `acl.conf`) verwendet wird:

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Ein `type=acl`‑Abschnitt benötigt keinen Verweis: `res_pjsip_acl` wendet jedes solche Objekt auf *allen* eingehenden SIP‑Verkehr an, bevor er einen Endpunkt erreicht. (Die Optionen `acl` und `contact_acl` am Objekt ziehen benannte Regel‑Listen aus `acl.conf`, anstatt `permit`/`deny` inline wie oben aufzulisten.) Das Prinzip ist dasselbe wie im SIP‑Kapitel: Alles verweigern, dann nur das zulassen, dem Sie vertrauen. Und was auch immer Ihr Trunk‑Kontext tut, **lassen Sie ihn niemals einen Kontext erreichen, der zurück ins PSTN wählt**, ohne eine bewusste, authentifizierte Regel – das ist das klassische Toll‑Fraud‑Loch.

> **Welches Modell sollte ich verwenden?** Wenn der Provider Ihnen einen Benutzernamen und ein Passwort gibt, verwenden Sie einen **Registrierungs‑**Trunk. Wenn er nach Ihrer IP‑Adresse fragt und Ihnen seine gibt, verwenden Sie einen **Identify**‑Trunk. Einige Provider unterstützen beides; viele reale Trunks kombinieren eine Registrierung (damit der Provider Sie finden kann) mit einem Identify (damit eingehende INVITEs von den Media‑Gateways des Providers selbst dann zugeordnet werden, wenn sie von einer anderen IP als dem Registrar kommen).

## Inbound routing and DID handling

Sobald eingehende Anrufe ankommen, landen sie im Endpoint‑`context` — hier
`from-pstn`. Eine **DID** (Direct Inward Dialing number) ist einfach die gewählte Nummer,
die der Provider Ihnen in der Request‑URI übergibt. Ihre Aufgabe im Dialplan ist es,
jede DID einer Zieladresse zuzuordnen: einer einzelnen Extension, einem IVR, einer
Queue oder einer Ring‑Gruppe.

Die Nummer, die der Provider sendet, wird als `${EXTEN}` in `from-pstn` gematcht. Wie viel davon
Sie sehen, hängt vom Provider ab – manche senden die vollständige E.164‑Nummer
(`+4830001000`), manche die nationale Nummer, wieder andere nur die letzten paar Ziffern.
Untersuchen Sie einen echten eingehenden Anruf mit `pjsip set logger on` und schauen Sie sich die
Request‑URI an, bevor Sie Muster schreiben.

### One DID to one extension

Der einfachste Fall – eine einzelne DID, die direkt zu einem Telefon geleitet wird:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

Eine Hauptnummer, die mit einem Menü antworten soll, anstatt ein Telefon zu klingeln:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` ist der Auto‑Attendant‑Context, den Sie in den Dialplan‑Kapitel
(`Background()` + `WaitExten()`) gebaut haben. Das Routing der DID ist einfach ein `Goto`.

### One DID to a queue

Eine Support‑Leitung, die in einer Call‑Queue landen soll:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

Wenn Sie einen Block von Nummern kaufen, hält ein Muster den Dialplan klein. Angenommen,
Ihr DID‑Bereich ist `4830003000`–`4830003099` und der Provider sendet die vollständige Nummer; ordnen Sie
die letzten beiden Ziffern jeder DID der Extension `60xx` zu:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` nimmt die letzten beiden Ziffern (ein negativer Offset zählt von rechts),
so dass `4830003007` `PJSIP/6007` klingelt. Eine `did => extension`‑Lookup‑Tabelle, gebaut mit
`GoSub` oder einer Asterisk‑Datenbank (`AstDB`/`func_odbc`), skaliert noch weiter, aber für
eine Handvoll Nummern sind explizite Muster am klarsten.

> **Catch the unmatched DID.** Add an `i` (invalid) extension to `from-pstn` so a
> mis-routed inbound number plays an announcement or rings the operator instead of
> dropping silently:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Outbound routing, caller-ID and E.164

Outbound calls flow the other way: an internal phone dials a number, your dialplan
matches it, strips any access prefix, sets the caller-ID the provider expects, and
hands the call to the trunk endpoint with `Dial(PJSIP/<number>@itsp)`.

### Sending the call to the trunk

The channel syntax for a trunk is `PJSIP/<number>@<endpoint>`: the part before the
`@` becomes the user portion of the outbound request URI, and the part after the
`@` names the endpoint whose `aor` `contact` supplies the destination host. A
classic "dial 9 for an outside line" rule:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` strips the leading `9` access code before the number is sent. The
pattern `_9NXXXXXXXXX` matches `9` plus a 10-digit number whose first digit is
2–9; adjust it to your dial plan.

### Caller-ID on outbound calls

Most ITSPs ignore — or actively reject — a caller-ID that is not a number you own.
Set the outbound caller-ID number to one of your DIDs with the `CALLERID(num)`
function before `Dial()`, as shown above. You can also set the name:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

If the provider still strips or overrides your caller-ID name, that is their
policy — many carriers source the displayed name from their own CNAM database
keyed on the number, not from your `From` header.

Two endpoint options interact with this:

- **`from_user`** sets the user part of the `From` header at the SIP level, which
  some providers use to identify your account regardless of `CALLERID(num)`.
- **`trust_id_outbound`** (default `no`) controls whether Asterisk will send
  privacy-sensitive identity headers (`P-Asserted-Identity`/`P-Preferred-Identity`)
  outbound. Leave it off unless your provider documents that they want PAI, in
  which case set `trust_id_outbound=yes` and `send_pai=yes`.

### Normalizing to E.164

E.164 is the international number format: a leading `+`, country code, then the
national number, with no spaces or punctuation (for example `+5548999990000` or
`+14155550100`). Carriers increasingly expect — or require — E.164 on the trunk.
Rather than scatter formatting across the dialplan, normalize once in the outbound
context.

A North-American example that accepts a 10-digit local number, an 11-digit
`1`-prefixed number, or an already-E.164 number, and always presents `+1…` to the
trunk:

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

Some providers want the `+`; others want the bare digits. If yours rejects the
`+`, strip it on the way out with `${EXTEN:1}` in the `Dial`. The point is that
all the format knowledge lives in one place, so switching providers — or adding a
second one — is a one-line change.

## Failover und Least-Cost-Routing

Mit einem Trunk bedeutet ein Provider-Ausfall, dass keine ausgehenden Anrufe möglich sind. Mit zwei oder mehr können Sie automatisch failover durchführen und sogar die günstigste Route pro Ziel auswählen — *least-cost routing* (LCR).

### Failover mit `${DIALSTATUS}`

`Dial()` setzt die Kanalvariable `${DIALSTATUS}`, wenn es zurückkehrt. Die Werte, die Sie für das Failover beachten müssen, sind `CHANUNAVAIL` (der Trunk konnte überhaupt nicht erreicht werden) und `CONGESTION` (der Anruf wurde abgelehnt, z. B. weil alle Leitungen belegt sind). Versuchen Sie den primären Trunk; wenn er den Anruf nicht transportieren konnte, springen Sie zum Backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Beachten Sie die bewusste Entscheidung, **nicht** bei `BUSY` oder `NOANSWER` failover zu betreiben — diese bedeuten, dass die *angerufene Partei* erreicht und abgelehnt wurde, sodass ein erneuter Versuch über einen anderen Trunk ein Telefon erneut klingeln lassen würde, das bereits „Nein“ gesagt hat (und Sie einen zweiten Anruf kosten könnte). Leiten Sie nur um, wenn der *Trunk selbst* ausgefallen ist.

### Eine wiederverwendbare Routing-Unterroutine

Dieses Logik‑Muster für jedes Wählmuster zu wiederholen, ist fehleranfällig. Faktorisieren Sie es in eine `GoSub`‑Routine, die die Zielnummer entgegennimmt und jeden Trunk der Reihe nach ausprobiert:

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

Jetzt ist jedes ausgehende Muster ein `GoSub`‑Aufruf, und die Trunk‑Reihenfolge ist an genau einer Stelle definiert.

### Least-Cost-Routing nach Ziel

Echtes LCR wählt den Trunk danach aus, wohin der Anruf geht. Eine gängige Vorgehensweise ist, das Ziel‑Präfix zu matchen und jede Anrufklasse an den Anbieter zu senden, der dafür am günstigsten ist — zum Beispiel internationale Anrufe zu einem Wholesale‑Carrier und lokale/nationale Anrufe zu Ihrem primären Anbieter:

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

Für mehr als ein paar Präfixe speichern Sie die Routentabelle in einer Datenbank (`func_odbc`/`AstDB`) und holen den Trunk anhand des Präfixes statt durch hartkodierte Muster. Der Dialplan bleibt klein und die Tarife leben in einer Tabelle, die Sie bearbeiten können, ohne die Logik neu zu laden.

## NAT und Trunks

NAT ist die mit Abstand häufigste Ursache für Trunk‑Probleme – typischerweise ein‑seitiger Audio oder ein Trunk, der sich registriert, aber nie eingehende Anrufe empfängt. Die Ursache ist dieselbe wie bei Telefonen (siehe *SIP & PJSIP in depth* und *Designing a VoIP network*): Asterisk gibt seine eigene Vorstellung seiner Adresse in SIP und SDP bekannt, und hinter NAT ist das eine private RFC‑1918‑Adresse, die der Provider nicht zurückrouten kann.

Für Trunks besteht die Lösung aus zwei Teilen – Einstellungen am **Transport** (Ihre öffentliche Adresse) und Einstellungen am **Endpoint** (wie die Medien des Providers behandelt werden).

### Am Transport – Ihre öffentliche Adresse

Wenn der Asterisk‑Server selbst hinter NAT steht (eine Cloud‑ oder On‑Prem‑Box mit einer privaten IP und einer 1:1‑öffentlichen IP), teilen Sie dem Transport seine öffentliche Adresse und welche Netze lokal sind mit. Diese Optionen werden einmalig auf dem `transport` gesetzt und gelten für den gesamten Verkehr darüber:

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

- **`external_signaling_address`** – die öffentliche IP, die Asterisk in SIP‑Headern (`Via`, `Contact`) für Ziele außerhalb von `local_net` einträgt.
- **`external_media_address`** – die öffentliche IP, die Asterisk in die SDP `c=`‑Zeile schreibt, sodass RTP an die richtige Stelle zurückkommt. In der Regel identisch mit der Signalisierungsadresse.
- **`local_net`** – Netze, die Asterisk als intern behandelt, sodass es *nicht* Adressen für LAN‑Peers umschreibt. Listen Sie jedes interne Subnetz auf.

### Am Endpoint – die Medien des Providers

Die andere Hälfte behandelt einen Provider, der selbst hinter NAT sitzt oder einfach Medien von einer anderen Adresse als der in seinem SDP angegebenen sendet. Setzen Sie diese pro Trunk‑Endpoint:

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

- **`direct_media=no`** – Medien über Asterisk fließen lassen, anstatt die beiden Beine direkt miteinander kommunizieren zu lassen. Essenziell bei NAT und ohnehin nötig, wenn Sie den Anruf aufzeichnen, transkodieren oder überwachen wollen.
- **`rtp_symmetric=yes`** – das klassische *comedia*‑Verhalten: RTP zurück an die Adresse senden, von der die Medien tatsächlich kamen, nicht an die Adresse, die das SDP angibt.
- **`force_rport=yes`** – auf SIP mit der Quell‑IP/Port der Anfrage (RFC 3581) antworten, anstatt dem `Via`‑Header zu vertrauen.
- **`rewrite_contact=yes`** – bei eingehenden SIP‑Nachrichten von diesem Endpoint den `Contact`‑Header (oder einen passenden `Record-Route`‑Header) auf die Quell‑IP‑Adresse und den Port umschreiben, von dem das Paket wirklich kam. Laut der eigenen Dokumentation dieser Option „hilft sie Servern, mit Endpoints zu kommunizieren, die hinter NATs stehen“ und „ermöglicht die Wiederverwendung zuverlässiger Transportverbindungen wie TCP und TLS.“

> **Empfehlung – Telefone vs. Trunks.** `rewrite_contact` ist fast immer die richtige Wahl für Telefone, weil ihr angekündigter Contact typischerweise eine private RFC‑1918‑Adresse ist, die nicht zu ihnen zurückgeroutet werden kann. Bei einem statischen IP‑basierten Trunk ist der Contact des Providers meist bereits eine korrekte öffentliche Adresse, sodass das Umschreiben oft unnötig ist; einige Betreiber lassen es dort weg und aktivieren es nur für Registrierungs‑Trunks und NAT‑Telefone. Die dokumentierte Wirkung der Option ist ausschließlich das oben beschriebene eingehende `Contact`/`Record-Route`‑Umschreiben – daher ist die sichere Vorgehensweise, die Einstellung zuerst mit Ihrem konkreten Carrier zu testen, bevor Sie sie bei einem statischen Trunk aktivieren.

Sie können die wirksamen Einstellungen an jedem Endpoint mit
`pjsip show endpoint <name>` – `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, und den übrigen im Parameter‑Dump ausgegebenen Werten überprüfen.

## Lab — a mock ITSP with a second Asterisk and SIPp

Sie benötigen keinen kostenpflichtigen Trunk zum Üben. Das Laborbuch startet bereits einen Asterisk
22.10.0‑Container und einen SIPp‑Container in einem privaten `172.30.0.0/24`‑Netzwerk; wir
betrachten den SIPp‑Container als den „Carrier“, der eingehende Anrufe platziert, und fügen einen
Trunk‑Endpoint hinzu, der diese Anrufe in einen `from-pstn`‑Kontext leitet.

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

Fügen Sie einen IP‑basierten Trunk zu `lab/asterisk/etc/pjsip.conf` hinzu, der zum SIPp‑Host des Labors passt
und eingehende Anrufe in `from-pstn` leitet:

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

### 2. Route the inbound DID

Fügen Sie in `lab/asterisk/etc/extensions.conf` einen `from-pstn`‑Kontext hinzu, der die
DID beantwortet, die der Mock‑Carrier wählt, und sie wieder abspielt, und fügen Sie dann eine ausgehende Regel hinzu:

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

Laden Sie beide Dateien neu (`core reload`) und prüfen Sie, ob der Trunk geladen wurde:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

Richten Sie ein SIPp‑Szenario auf die PBX aus, wobei die DID als Ziel‑Benutzer verwendet wird. Das Labor liefert bereits
`lab/sipp/uac_9000.xml`, das die Extension `9000` anruft; kopieren Sie es nach
`uac_did.xml` und ändern Sie die Request‑URI/`To`‑Benutzer von `9000` zu `4830001000`,
und führen Sie es dann aus dem SIPp‑Container aus:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Beobachten Sie, wie der Anruf `from-pstn` auf der Asterisk‑Konsole trifft (`pjsip set logger on`
zeigt das eingehende INVITE; `core show channels` zeigt den `PJSIP/itsp-…`‑Kanal,
der `demo-congrats` abspielt). Da die SIPp‑Quell‑IP mit dem `identify` übereinstimmt, wird der
Anruf ohne Authentifizierung akzeptiert – genau so, wie ein statischer Carrier‑Trunk
sich verhält.

### 4. Inspect the trunk

Erfassen Sie die vollständige Konfiguration des Trunks für Ihre Notizen:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

Stellen Sie den *zweiten* Asterisk‑Container als echten Registrar bereit: geben Sie ihm ein
`endpoint`+`auth`+`aor` für das Konto `4830001000`, und tauschen Sie dann auf der PBX den
`identify`‑Block gegen den `registration`‑Block aus dem Anfang dieses Kapitels aus
(der `server_uri` auf die IP des zweiten Containers zeigt). Bestätigen Sie mit
`pjsip show registrations`, dass der Status `Registered` anzeigt, und führen Sie dann in beide Richtungen einen Anruf durch.

## Summary

Ein SIP‑Trunk verbindet Ihre PBX mit der Außenwelt, und in PJSIP ist er einfach ein
Endpoint, der aus derselben `endpoint` + `auth` + `aor`‑Familie besteht, die Sie bereits kennen,
plus einem `identify` oder einem `registration`. Verwenden Sie einen **registration trunk**
(`type=registration` mit `outbound_auth`), wenn der Provider Ihnen einen Benutzernamen
und ein Passwort gibt; verwenden Sie einen **IP‑basierten trunk** (`type=identify` mit `match`), wenn
die Authentifizierung über die Quell‑IP erfolgt – und sperren Sie Letzteren mit einem engen `match`
und einem `acl`, weil ein nicht authentifizierter Trunk ein Ziel für Toll‑Fraud ist. Eingehend,
kommt die DID des Providers als `${EXTEN}` in Ihrem `from-pstn`‑Kontext an, wo Sie
sie zu einer Extension, einem IVR oder einer Queue weiterleiten – Muster und `${EXTEN:-N}` halten
DID‑Blöcke kompakt. Ausgehend setzen Sie `CALLERID(num)` auf eine Nummer, die Sie besitzen, normalisieren
zu E.164 an einer Stelle und übergeben den Anruf an `PJSIP/<number>@trunk`. Erhöhen Sie die
Resilienz, indem Sie mehrere Trunks ausprobieren und basierend auf `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` bedeuten Umleitung; `BUSY`/`NOANSWER` nicht) verzweigen, und legen Sie
Least‑Cost‑Routing in einer `GoSub`‑Tabelle fest. Schließlich ist NAT für Trunks zweiseitig:
`external_media_address`/`external_signaling_address`/`local_net` auf dem
**transport** für Ihre öffentliche Adresse und `direct_media=no`, `rtp_symmetric`,
`force_rport` und `rewrite_contact` auf dem **endpoint** für das Medien des Providers.

## Quiz

1. In PJSIP werden die Anmeldeinformationen, die für einen *ausgehenden* Anruf oder die Registrierung bei einem Provider verwendet werden, referenziert mit:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Sie sollten einen `type=registration`‑Trunk verwenden, wenn:
   - A. Der Provider Sie anhand Ihrer Quell‑IP‑Adresse identifiziert.
   - B. Der Provider Ihnen einen Benutzernamen und ein Passwort gibt und erwartet, dass Sie sich anmelden.
   - C. Sie niemals möchten, dass Asterisk ein `REGISTER` sendet.
   - D. Der Trunk zwischen zwei statischen IP‑Servern liegt, die Sie kontrollieren.
3. Die Option `match` des Objekts `identify` akzeptiert (wählen Sie alle zutreffenden aus):
   - A. Eine IP‑Adresse
   - B. Einen CIDR‑Bereich
   - C. Einen Hostnamen (zur Ladezeit der Konfiguration aufgelöst)
   - D. Nur einen SIP‑Benutzernamen
4. Auf Asterisk 22 ist `auth_type=userpass`:
   - A. Der einzige gültige Wert
   - B. Veraltet und wird zu `digest` konvertiert
   - C. Entfernt und verursacht einen Ladefehler
   - D. Für ausgehende Registrierungen erforderlich
5. Eine eingehende DID‑Nummer erscheint im Dialplan als:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` im `context` des Trunk‑Endpoints
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Um die letzten beiden Ziffern der gewählten DID `4830003007` an eine Nebenstelle zu senden, würden Sie verwenden:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Nach `Dial()` zu einem Trunk sollten Sie auf einen Backup‑Trunk umschalten, bei dem die Werte `${DIALSTATUS}` (wählen Sie zwei) gelten?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Um die dem Provider vor dem Auswählen präsentierte Caller‑ID‑Nummer festzulegen, verwenden Sie:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Die Optionen, die Asterisk seine *öffentliche* Adresse mitteilen, wenn der Server hinter NAT steht, werden gesetzt auf:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` auf einem Trunk‑Endpoint bewirkt, dass Asterisk:
    - A. RTP mit SRTP verschlüsselt
    - B. RTP an die Adresse zurücksendet, von der das Medium tatsächlich eingetroffen ist, und das SDP ignoriert
    - C. RTP vollständig deaktiviert
    - D. Direktmedien zwischen Endpunkten erzwingt

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
