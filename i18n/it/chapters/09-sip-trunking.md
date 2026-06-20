# SIP trunking, DID & the PSTN

Un PBX che può chiamare solo se stesso non è molto utile. Prima o poi ogni sistema
deve raggiungere il resto del mondo — la rete telefonica pubblica commutata
(PSTN), un provider SIP o un altro PBX. Il collegamento che trasporta queste chiamate è un
**trunk**. Nell'era TDM un trunk era un circuito fisico: un PRI T1/E1 o un raggruppamento
di linee analogiche FXO. Oggi è quasi sempre un **SIP trunk** — una connessione
logica a un Internet Telephony Service Provider (ITSP) trasportata sulla stessa
rete IP di tutto il resto.

Questo capitolo mostra come collegare Asterisk 22 a un ITSP con PJSIP, come scegliere
tra un trunk basato su registrazione e uno basato su IP, come instradare i numeri DID
in entrata verso la destinazione corretta, come inviare chiamate in uscita con
caller-ID corretto e formattazione E.164, e come costruire failover e routing a
costo minimo su più trunk. Concludiamo con la gestione del NAT per i trunk e un
laboratorio che avvia un secondo Asterisk (e SIPp) come ITSP simulato così da
poter effettuare chiamate reali attraverso un trunk.

Tutto qui è verificato rispetto al laboratorio del libro per Asterisk 22.10.0; il modello
dell'oggetto trunk è lo stesso introdotto in *Building your first PBX with PJSIP*
e *SIP & PJSIP in depth*.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Collegare Asterisk 22 a un ITSP con PJSIP
- Scegliere tra trunk basati su registrazione e trunk basati su IP (statici)
- Instradare i DID in ingresso verso l'estensione corretta, IVR o coda
- Instradare le chiamate in uscita con il corretto caller-ID e formattazione E.164
- Costruire failover dei trunk e routing a minor costo con `${DIALSTATUS}`
- Gestire il NAT per i trunk sul trasporto e sull'endpoint

## What is a SIP trunk

Un SIP trunk è un percorso vocale logico tra il tuo PBX e un altro sistema SIP. In pratica quel "altro sistema" è una delle due cose:

- **Un ITSP (Internet Telephony Service Provider).** Un operatore commerciale che ti vende l'origine e la terminazione delle chiamate e, di solito, un blocco di numeri telefonici (DID). Puntate Asterisk sull'host di segnalazione del provider, e il provider collega le vostre chiamate alla più ampia PSTN. Questo è il modo in cui la maggior parte dei sistemi moderni raggiunge la rete telefonica — non è necessario hardware telefonico.
- **Un gateway PSTN.** Un dispositivo (o un altro Asterisk) che dispone di interfacce PSTN fisiche — una scheda PRI, porte analogiche FXO, o un gateway GSM/4G — e le presenta al vostro PBX come SIP. Il gateway esegue la conversione TDM‑to‑SIP; dal punto di vista di Asterisk è semplicemente un altro SIP trunk.

In entrambi i casi, in PJSIP un trunk è **solo un endpoint**. La stessa famiglia di oggetti che usavi per un telefono — `endpoint`, `auth`, `aor`, opzionalmente `identify` e `registration` — costruisce un trunk. Le differenze sono nei dettagli: un trunk autentica *in uscita* (tu sei il client, quindi le credenziali vanno in `outbound_auth`, non in `auth`), di solito non registra un user agent a te (tu ti registri a *lui*, o lui ti invia traffico da un IP noto), e fa atterrare le chiamate in ingresso in un contesto dedicato come `from-pstn` invece di `from-internal`.

> **Confrontato con il vecchio trunk TDM.** Un PRI ti forniva un numero fisso di B‑channel (23 su un T1, 30 su un E1) e segnalava l'instaurazione della chiamata su un D‑channel dedicato (vedi il capitolo *Legacy channels*). Un SIP trunk non ha un numero fisso di canali — la capacità è quella consentita dalla tua larghezza di banda, dalla politica del provider e da eventuali limiti `max_contacts`/concurrent‑call. Caller‑ID, DID e lo stato di avanzamento della chiamata, che un tempo viaggiavano negli elementi informativi ISDN, ora viaggiano negli header SIP e SDP.

## Trunk basati sulla registrazione

Un trunk basato sulla registrazione è il modello usato quando il provider si aspetta che *tu* ti
connetta a *loro*. Il tuo Asterisk invia periodicamente un SIP `REGISTER` al
provider, autenticandosi con nome utente e password, esattamente come un telefono
si registra al tuo PBX. Questo è comune quando il tuo IP pubblico è dinamico, quando sei
dietro NAT, o quando il provider identifica semplicemente i clienti tramite credenziali SIP
piuttosto che tramite indirizzo IP.

In PJSIP il login in uscita vive in un oggetto `registration` dedicato. Sostituisce la singola riga `register =>` che il driver `chan_sip` rimosso usava in
`sip.conf`. Ecco un trunk di registrazione completo verso un provider fittizio,
seguendo lo schema verificato nei capitoli precedenti — nota `outbound_auth`
(non `auth`), `server_uri`/`client_uri` (non `server`/`client`),
`from_user`/`from_domain` sull'endpoint e `dtmf_mode=rfc4733`:

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

Alcune cose da notare:

- **`auth_type=digest`, non `userpass`.** Entrambi producono la stessa autenticazione digest,
  ma in Asterisk 22 `userpass` (e il vecchio `md5`) sono
  **deprecati e convertiti silenziosamente in `digest`**. Preferisci `digest` nella nuova
  configurazione; vedrai ancora `userpass` nei file più vecchi e nei capitoli
  precedenti di questo libro.
- **`outbound_auth` sia sull'endpoint che sulla registrazione.** La registrazione
  lo usa per autenticare il `REGISTER`; l'endpoint lo usa per rispondere al
  `407 Proxy Authentication Required` che il provider invia indietro a un outbound
  `INVITE`. Possono condividere lo stesso oggetto `auth`.
- **`from_user` / `from_domain`.** Molti provider rifiutano chiamate il cui header `From`
  non contiene il tuo numero di conto e il loro dominio. Queste due opzioni
  impostano esattamente questo.
- **`contact_user=4830001000`.** Questo diventa la parte utente del `Contact` che
  registri, così il provider sa a quale numero consegnare le chiamate in ingresso. È
  l'equivalente moderno del suffisso `/9999` sulla vecchia riga `register =>`.
- **`retry_interval=60`.** Se la registrazione fallisce, riprova ogni 60 secondi.

Dopo un reload, conferma la registrazione con `pjsip show registrations`. Nel
laboratorio — dove `itsp.example.com` non risponde realmente — la tabella appare così:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

Il suffisso `(exp. Ns)` conta alla rovescia i secondi fino al prossimo tentativo; una volta che
raggiunge zero legge brevemente `(exp. Ns ago)` prima che il retry venga attivato. Contro un
provider live la colonna `Status` legge `Registered` con i secondi rimanenti
fino al prossimo refresh. `Rejected` (o `Unregistered`) indica che il provider non
ha accettato il login — attiva `pjsip set logger on` e leggi la risposta `401`/`403`,
quasi sempre un nome utente, password o dominio `client_uri` errati.

## IP-based (static) trunks

Il secondo modello non richiede alcuna registrazione. Il provider conosce il tuo indirizzo IP pubblico e invia le chiamate direttamente a esso; tu, a tua volta, invii le chiamate all'indirizzo IP di segnalazione noto del provider. L'autenticazione avviene tramite **indirizzo IP di origine**, non tramite credenziali SIP. Questo è tipico per trunk tra due server che controlli, o per un trunk aziendale dove entrambe le parti hanno indirizzi statici.

L'oggetto chiave è `identify`. Dice ad Asterisk: "qualsiasi richiesta SIP proveniente da *questo* IP appartiene a *quel* endpoint." Senza di esso, PJSIP tenta di associare una richiesta in ingresso a un endpoint tramite l'utente `From`, cosa che il traffico di un carrier non soddisferà — quindi la chiamata verrebbe rifiutata o cadrebbe sull'endpoint `anonymous`.

Un trunk statico elimina l'oggetto `registration` e aggiunge `identify`:

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

`match` accetta un indirizzo IP, un intervallo CIDR o un nome host. **I nomi host vengono risolti una sola volta, al momento del caricamento della configurazione**, quindi se l'IP del tuo provider cambia devi ricaricare. Per un carrier che pubblica diversi gateway multimediali, elenca ogni IP di segnalazione — puoi ripetere `match` o fornire un CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Verifica cosa accetterà Asterisk con `pjsip show identifies`. Catturato dal laboratorio (la riga `sipp-identify` è l'endpoint SIPp preesistente del laboratorio):

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

### The security implication

Un trunk basato su IP senza autenticazione è una porta, e `identify`/`match` è l'unica serratura su di essa. Se `match` un intervallo troppo ampio — o se un attaccante può falsificare un IP di origine — le chiamate arrivano nel tuo contesto `from-pstn` non autenticate. Due difese, usate insieme:

- **Corrispondi il più strettamente possibile.** Preferisci IP host specifici rispetto a CIDR ampi. Solo gli IP di segnalazione reali del provider appartengono a `match`.
- **Abbinalo a una ACL.** PJSIP può scartare il traffico a livello SIP prima che raggiunga un endpoint, usando un oggetto `type=acl` (o `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Una sezione `type=acl` non richiede riferimento: `res_pjsip_acl` applica ogni tale oggetto a *tutto* il traffico SIP in ingresso prima che raggiunga qualsiasi endpoint. (Le opzioni `acl` e `contact_acl` sull'oggetto estraggono elenchi di regole nominati da `acl.conf` invece di elencare `permit`/`deny` inline come sopra.) Il principio è lo stesso del capitolo SIP: nega tutto, poi consenti solo ciò di cui ti fidi. E qualunque cosa faccia il tuo contesto trunk,
**non lasciarlo mai raggiungere un contesto che possa chiamare nuovamente verso il PSTN** senza una regola deliberata e autenticata — questo è il classico buco di frode tariffaria.

> **Which model should I use?** If the provider gives you a username and password,
> use a **registration** trunk. If they ask for your IP address and give you
> theirs, use an **identify** trunk. Some providers support both; many real
> trunks combine a registration (so the provider can find you) with an identify
> (so inbound INVITEs from the provider's media gateways are matched even when
> they arrive from an IP other than the registrar).

## Inbound routing and DID handling

Una volta che le chiamate in ingresso arrivano, atterrano nell'endpoint's `context` — qui
`from-pstn`. Un **DID** (Direct Inward Dialing number) è semplicemente il numero composto
che il provider ti passa nella request URI. Il tuo compito nel dialplan è mappare ogni
DID a una destinazione: un'unica estensione, un IVR, una coda, o un ring group.

Il numero che il provider invia viene confrontato come `${EXTEN}` in `from-pstn`. Quanto
ne vedi dipende dal provider — alcuni inviano il numero completo E.164
(`+4830001000`), altri il numero nazionale, altri solo le ultime cifre.
Esamina una chiamata reale in ingresso con `pjsip set logger on` e guarda la
request URI prima di scrivere i pattern.

### One DID to one extension

Il caso più semplice — un singolo DID instradato direttamente a un telefono:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

Un numero principale che dovrebbe rispondere con un menu invece di far squillare un telefono:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` è il contesto auto-attendant che hai costruito nei capitoli del dialplan
(`Background()` + `WaitExten()`). Instradare il DID è solo un `Goto`.

### One DID to a queue

Una linea di supporto che dovrebbe finire in una coda di chiamate:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

Quando acquisti un blocco di numeri, un pattern mantiene il dialplan piccolo. Supponi che
il tuo intervallo di DID sia `4830003000`–`4830003099` e il provider invii il numero completo; mappa
le ultime due cifre di ogni DID all'estensione `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` prende le ultime due cifre (un offset negativo conta da destra),
quindi `4830003007` squilla `PJSIP/6007`. Una tabella di lookup `did => extension` costruita con
`GoSub` o un database Asterisk (`AstDB`/`func_odbc`) scala ancora di più, ma per
una manciata di numeri i pattern espliciti sono i più chiari.

> **Catch the unmatched DID.** Aggiungi un’estensione `i` (invalid) a `from-pstn` così un
> numero in ingresso instradato erroneamente riproduce un annuncio o fa squillare l'operatore invece di
> cadere silenziosamente:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Instradamento in uscita, caller-ID e E.164

Le chiamate in uscita fluiscono nell'altro verso: un interno compone un numero, il tuo dialplan lo corrisponde, rimuove eventuali prefissi di accesso, imposta il caller-ID che il provider si aspetta e passa la chiamata all'endpoint trunk con `Dial(PJSIP/<number>@itsp)`.

### Invio della chiamata al trunk

La sintassi del canale per un trunk è `PJSIP/<number>@<endpoint>`: la parte prima del
`@` diventa la porzione utente dell'URI di richiesta in uscita, e la parte dopo il
`@` indica l'endpoint il cui `aor` `contact` fornisce l'host di destinazione. Una regola classica “comporre 9 per una linea esterna”:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` rimuove il prefisso di accesso `9` iniziale prima che il numero venga inviato. Il
modello `_9NXXXXXXXXX` corrisponde a `9` più un numero a 10 cifre il cui primo digit è
2–9; adattalo al tuo piano di composizione.

### Caller-ID sulle chiamate in uscita

La maggior parte degli ITSP ignora — o rifiuta attivamente — un caller-ID che non sia un numero di tua proprietà.
Imposta il numero del caller-ID in uscita su uno dei tuoi DID con la funzione `CALLERID(num)`
prima di `Dial()`, come mostrato sopra. Puoi anche impostare il nome:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

Se il provider continua a rimuovere o a sovrascrivere il nome del tuo caller-ID, è una loro politica — molti operatori ricavano il nome visualizzato dal proprio database CNAM indicizzato sul numero, non dal tuo header `From`.

Due opzioni dell'endpoint interagiscono con questo:

- **`from_user`** imposta la parte utente dell'header `From` a livello SIP, che
  alcuni provider usano per identificare il tuo account indipendentemente da `CALLERID(num)`.
- **`trust_id_outbound`** (predefinito `no`) controlla se Asterisk invierà
  header di identità sensibili alla privacy (`P-Asserted-Identity`/`P-Preferred-Identity`)
  in uscita. Lascia l'opzione disattivata a meno che il tuo provider non documenti che desidera PAI, nel qual caso imposta `trust_id_outbound=yes` e `send_pai=yes`.

### Normalizzazione a E.164

E.164 è il formato internazionale dei numeri: un prefisso `+` iniziale, il codice paese, poi il
numero nazionale, senza spazi o punteggiatura (ad esempio `+5548999990000` o
`+14155550100`). Gli operatori richiedono sempre più spesso — o obbligano — E.164 sul trunk.
Piuttosto che spargere la formattazione nel dialplan, normalizza una volta sola nel contesto outbound.

Un esempio nordamericano che accetta un numero locale a 10 cifre, un numero prefissato da 11 cifre `1`, o un numero già in formato E.164, e presenta sempre `+1…` al
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

Alcuni provider vogliono il `+`; altri vogliono le sole cifre. Se il tuo rifiuta il
`+`, rimuovilo in uscita con `${EXTEN:1}` nel `Dial`. Il punto è che
tutta la conoscenza del formato vive in un unico posto, così cambiare provider — o aggiungerne un
secondo — è una modifica a una sola riga.

## Failover e routing a costo minimo

Con un solo trunk, un’interruzione del provider significa nessuna chiamata in uscita. Con due o più, è possibile effettuare il failover automaticamente e persino scegliere il percorso più economico per destinazione — *least-cost routing* (LCR).

### Failover con `${DIALSTATUS}`

`Dial()` imposta la variabile di canale `${DIALSTATUS}` al ritorno. I valori di cui ti interessa tenere conto per il failover sono `CHANUNAVAIL` (il trunk non è stato raggiunto affatto) e `CONGESTION` (la chiamata è stata rifiutata, ad es. tutti i circuiti occupati). Prova il trunk primario; se non può trasportare la chiamata, passa a quello di backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Nota la scelta deliberata **di non** effettuare il failover su `BUSY` o `NOANSWER` — questi indicano che la *parte chiamata* è stata raggiunta e ha rifiutato, quindi ritentare su un altro trunk farebbe squillare nuovamente un telefono che ha già detto no (e potrebbe costarti una seconda chiamata). Reroute solo quando il *trunk stesso* è fallito.

### Una subroutine di routing riutilizzabile

Ripetere quella logica per ogni modello di composizione è soggetto a errori. Fattorizzala in una routine `GoSub` che prende il numero di destinazione e prova ogni trunk in ordine:

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

Ora ogni modello di uscita è una chiamata `GoSub`, e l’ordine dei trunk è definito in un unico posto.

### Routing a costo minimo per destinazione

Il vero LCR sceglie il trunk in base alla destinazione della chiamata. Una forma comune è quella di abbinare il prefisso di destinazione e inviare ogni classe di chiamata al provider più economico per quella classe — ad esempio, chiamate internazionali a un carrier all’ingrosso e chiamate locali/nazionali al tuo trunk primario:

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

Per più di pochi prefissi, memorizza la tabella di routing in un database (`func_odbc`/`AstDB`) e cerca il trunk per prefisso invece di codificare i modelli. Il dialplan rimane piccolo e le tariffe vivono in una tabella che puoi modificare senza ricaricare la logica.

## NAT and trunks

NAT è la causa più comune di problemi con i trunk — tipicamente audio a senso unico,
o un trunk che si registra ma non riceve mai chiamate in ingresso. La causa è la stessa
dei telefoni (coperta in *SIP & PJSIP in depth* e *Designing a VoIP network*):
Asterisk pubblica la propria idea del proprio indirizzo in SIP e SDP, e dietro NAT
quello è un indirizzo privato RFC 1918 che il provider non può instradare indietro.

Per i trunk la correzione ha due parti — impostazioni sul **transport** (il tuo
indirizzo pubblico) e impostazioni sul **endpoint** (come trattare i media del provider).

### On the transport — your public address

Quando il server Asterisk stesso è dietro NAT (un box cloud o on‑prem con un
IP privato e un IP pubblico 1:1), indica al transport il suo indirizzo pubblico e quali
reti sono locali. Queste opzioni vengono impostate una volta, sul `transport`, e si applicano a
tutto il traffico su di esso:

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

- **`external_signaling_address`** — l'IP pubblico che Asterisk scrive negli header SIP
  (`Via`, `Contact`) per destinazioni al di fuori `local_net`.
- **`external_media_address`** — l'IP pubblico che Asterisk scrive nella riga SDP `c=`
  così che l'RTP torni al posto giusto. Di solito identico all'indirizzo di segnalazione.
- **`local_net`** — reti che Asterisk tratta come interne, quindi *non* riscrive
  gli indirizzi per i peer LAN. Elenca ogni subnet interna.

### On the endpoint — the provider's media

L'altra metà gestisce un provider che è anch'esso dietro NAT, o che semplicemente invia
media da un indirizzo diverso da quello presente nel suo SDP. Imposta questi per ogni endpoint del trunk:

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

- **`direct_media=no`** — mantieni i media che passano attraverso Asterisk invece di lasciare
  che le due gambe comunichino direttamente. Essenziale attraverso NAT, e comunque necessario se
  vuoi registrare, transcodificare o monitorare la chiamata.
- **`rtp_symmetric=yes`** — il classico comportamento *comedia*: invia l'RTP all'indirizzo da cui i media sono effettivamente arrivati, non all'indirizzo che l'SDP dichiara.
- **`force_rport=yes`** — rispondi al SIP dall'IP/porta di origine della richiesta
  (RFC 3581), invece di fidarti dell'header `Via`.
- **`rewrite_contact=yes`** — sui messaggi SIP in ingresso da questo endpoint, riscrivi
  l'header `Contact` (o un appropriato header `Record-Route`) con l'IP di origine
  e la porta da cui il pacchetto è realmente arrivato. Secondo la documentazione dell'opzione, questo "aiuta i server a comunicare con endpoint che sono dietro
  NAT" e "aiuta a riutilizzare connessioni di trasporto affidabili come TCP e TLS."

> **Recommendation — phones vs trunks.** `rewrite_contact` è quasi sempre la
> scelta giusta per i telefoni, perché il loro contatto pubblicizzato è tipicamente un indirizzo privato
> RFC 1918 che non è instradabile verso di loro. Su un trunk basato su IP statico
> il contatto del provider è solitamente già un corretto indirizzo pubblico, quindi riscriverlo è spesso inutile; alcuni operatori preferiscono lasciarlo disattivato lì e abilitarlo
> solo per i trunk di registrazione e i telefoni dietro NAT. L'effetto documentato dell'opzione è puramente la riscrittura inbound `Contact`/`Record-Route` sopra — quindi la
> pratica sicura è testare con il tuo carrier specifico prima di attivarla su un
> trunk statico.

Puoi confermare le impostazioni effettive su qualsiasi endpoint con
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, e il resto viene stampato nel dump dei parametri.

## Laboratorio — un ITSP simulato con un secondo Asterisk e SIPp

Non è necessario un trunk a pagamento per esercitarsi. Il laboratorio del libro esegue già un contenitore Asterisk
22.10.0 e un contenitore SIPp su una rete privata `172.30.0.0/24`; tratteremo il contenitore SIPp come il “carrier” che effettua chiamate in ingresso, e aggiungeremo un
endpoint trunk che indirizza quelle chiamate in un contesto `from-pstn`.

![Un trunk SIP tra il PBX Asterisk e l'ITSP: il PBX si registra come un account, le chiamate in uscita compongono `PJSIP/<num>@trunk`, e le chiamate in ingresso atterrano nel contesto `from-pstn`](../images/09-sip-trunking-fig01.png)

### 1. Aggiungere l'endpoint trunk

Aggiungere un trunk basato su IP a `lab/asterisk/etc/pjsip.conf` che corrisponda all'host SIPp del laboratorio
e indirizzi le chiamate in ingresso in `from-pstn`:

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

### 2. Instradare il DID in ingresso

In `lab/asterisk/etc/extensions.conf`, aggiungere un contesto `from-pstn` che risponde al
DID che il carrier simulato comporrà e lo riproduce, quindi aggiungere una regola in uscita:

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

Ricaricare entrambi i file (`core reload`) e verificare che il trunk sia stato caricato:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Effettuare una chiamata in ingresso attraverso il trunk

Puntare uno scenario SIPp verso il PBX con il DID come utente di destinazione. Il laboratorio fornisce già
`lab/sipp/uac_9000.xml`, che INVITA l'estensione `9000`; copiarlo in
`uac_did.xml` e modificare il request-URI/utente `To` da `9000` a `4830001000`,
quindi eseguirlo dal contenitore SIPp:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Osservare la chiamata arrivare a `from-pstn` sulla console di Asterisk (`pjsip set logger on`
mostra l'INVITE in ingresso; `core show channels` mostra il canale `PJSIP/itsp-…`
che riproduce `demo-congrats`). Poiché l'IP di origine SIPp corrisponde al `identify`, la
chiamata è accettata senza autenticazione — esattamente come si comporta un trunk carrier statico.

### 4. Ispezionare il trunk

Catturare la configurazione completa del trunk per le proprie note:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Estensione) renderlo un trunk di registrazione

Attivare il *secondo* contenitore Asterisk come registrar reale: assegnargli un
`endpoint`+`auth`+`aor` per l'account `4830001000`, quindi sul PBX sostituire il
blocco `identify` con il blocco `registration` dall'inizio di questo capitolo
(puntando `server_uri` all'IP del secondo contenitore). Confermare con
`pjsip show registrations` che lo stato mostri `Registered`, quindi effettuare una chiamata
in entrambe le direzioni.

## Summary

Un trunk SIP collega il tuo PBX al mondo esterno, e in PJSIP è semplicemente un
endpoint costruito dalla stessa famiglia `endpoint` + `auth` + `aor` che già conosci,
più un `identify` o un `registration`. Usa un **registration trunk**
(`type=registration` con `outbound_auth`) quando il provider ti fornisce un nome utente
e una password; usa un **IP-based trunk** (`type=identify` con `match`) quando
l'autenticazione avviene per IP di origine — e blocca quest'ultimo con un ristretto `match`
e un `acl`, perché un trunk non autenticato è un bersaglio di frode telefonica. In ingresso,
il DID del provider arriva come `${EXTEN}` nel tuo contesto `from-pstn`, dove lo
instradi verso un'estensione, un IVR o una coda — i pattern e `${EXTEN:-N}` mantengono
i blocchi DID compatti. In uscita, imposta `CALLERID(num)` su un numero di tua proprietà, normalizza
a E.164 in un unico punto, e passa la chiamata a `PJSIP/<number>@trunk`. Costruisci
resilienza provando più trunk e ramificando su `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` significano ri‑instradamento; `BUSY`/`NOANSWER` no), e inserisci
il routing a costo minimo in una tabella `GoSub`. Infine, il NAT per i trunk è a due lati:
`external_media_address`/`external_signaling_address`/`local_net` sul
**transport** per il tuo indirizzo pubblico, e `direct_media=no`, `rtp_symmetric`,
`force_rport` e `rewrite_contact` sull'**endpoint** per i media del provider.

## Quiz

1. In PJSIP, le credenziali usate per autenticare una chiamata *outbound* o
   la registrazione a un provider sono riferite con:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. Dovresti usare un trunk `type=registration` quando:
   - A. Il provider ti identifica per il tuo indirizzo IP di origine.
   - B. Il provider ti fornisce un nome utente e una password e si aspetta che tu effettui il login.
   - C. Non vuoi mai che Asterisk invii un `REGISTER`.
   - D. Il trunk è tra due server con IP statici che controlli.
3. L'opzione `match` dell'oggetto `identify` accetta (scegli tutte le risposte corrette):
   - A. Un indirizzo IP
   - B. Un intervallo CIDR
   - C. Un nome host (risolto al momento del caricamento della configurazione)
   - D. Solo un nome utente SIP
4. Su Asterisk 22, `auth_type=userpass` è:
   - A. L'unico valore valido
   - B. Deprecato e convertito in `digest`
   - C. Rimosso e provoca un errore di caricamento
   - D. Obbligatorio per la registrazione outbound
5. Un numero DID in ingresso arriva nel dialplan come:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` nel `context` del trunk endpoint
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. Per inviare le ultime due cifre del DID composto `4830003007` a un'estensione,
   useresti:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. Dopo `Dial()` a un trunk, dovresti passare a un trunk di backup sul quale
   i valori `${DIALSTATUS}` (scegli due)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. Per impostare il numero caller-ID presentato al provider prima di comporre,
   usa:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. Le opzioni che indicano ad Asterisk il suo indirizzo *pubblico* quando il server è dietro
   NAT sono impostate su:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` su un trunk endpoint fa sì che Asterisk:
    - A. Cripti RTP con SRTP
    - B. Invi RTP all'indirizzo da cui i media sono effettivamente arrivati, ignorando l'SDP
    - C. Disabiliti completamente RTP
    - D. Forzi media diretto tra gli endpoint

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
