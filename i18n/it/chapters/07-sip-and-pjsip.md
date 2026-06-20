# SIP & PJSIP in profondità

SIP è il protocollo; PJSIP è il modo in cui Asterisk 22 lo utilizza. **PJSIP** (`chan_pjsip`, configurato tramite `pjsip.conf`) è l'unico driver del canale SIP in Asterisk 22 LTS. Questo capitolo copre i fondamenti del protocollo SIP (che sono a livello di protocollo e rimangono validi al 100%) e il modello oggetto e la configurazione di PJSIP che usi quotidianamente. Il driver legacy ritirato e una guida alla migrazione sono trattati nel capitolo *Legacy channels*.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Spiegare il ruolo degli agenti utente SIP, proxy, registrar e gateway;
- Seguire un flusso di chiamata SIP di base (REGISTER, INVITE, risposte provvisorie e finali, ACK, BYE) e leggere un messaggio SIP;
- Descrivere come SDP negozia la sessione multimediale e come il NAT influisce sulla segnalazione SIP e su RTP;
- Mappare il modello oggetto PJSIP — `endpoint`, `auth`, `aor`, `transport`, `identify`, e `registration` — e come gli oggetti si riferiscono tra loro;
- Configurare telefoni SIP e trunk in `pjsip.conf`, incluse le opzioni di attraversamento NAT; e
- Verificare e risolvere i problemi degli endpoint con i comandi CLI `pjsip show …`.

## Fondamenti del protocollo SIP

Session Initiation Protocol (SIP) è un protocollo basato su testo simile a HTTP e SMTP che è stato progettato per inizializzare, mantenere e terminare sessioni di comunicazione interattive tra utenti. Queste sessioni possono includere voce, video, chat, giochi interattivi e altro. SIP è stato definito dall'IETF ed è diventato lo standard de facto per le comunicazioni vocali. È molto importante comprendere come funziona SIP. Su Asterisk 22 la configurazione SIP si trova in `pjsip.conf`, che è uno dei file più frequentemente modificati su un sistema basato su SIP (subito dopo `extensions.conf`).

### Teoria del funzionamento

SIP è un protocollo di segnalazione con i seguenti componenti: User Agent Client, User Agent Servers, SIP Proxies e SIP Gateways. La figura seguente mostra le relazioni tra questi componenti.

- UAC (user agent client) – Il client o terminale che avvia la segnalazione SIP.  
- UAS (user agent server) – Il server che risponde a una segnalazione SIP proveniente da un UAC.  
- UA (user agent) – Il terminale SIP (telefoni o gateway che contengono sia UAC sia UAS).  
- Proxy Server – Riceve richieste da un UA e le trasferisce ad altri SIP Proxy se la stazione particolare non è sotto la loro amministrazione.  
- Redirect Server – Riceve richieste e le rimanda all'UA, includendo i dati di destinazione, invece di inoltrarle direttamente alla destinazione.  
- Location Server – Riceve richieste da un UA e aggiorna il database di localizzazione con queste informazioni.

Di solito, i server proxy, redirect e location sono ospitati nello stesso hardware e utilizzano lo stesso software, che chiamiamo il SIP proxy. Il SIP proxy è responsabile della manutenzione del database di location, dell'instaurazione della connessione e della terminazione della sessione.

![I principali componenti SIP: agenti utente (UAC/UAS/UA), il server registrar/proxy/redirect e un gateway verso la PSTN, con i media RTP che fluiscono direttamente tra gli endpoint](../images/07-sip-and-pjsip-fig01.png)

#### Processo di registrazione SIP

Before a phone can receive calls, it needs to be registered to a location database. In the location database, the IP address will be bonded to the name. In the following example, extension 8500 will be bound to IP address 200.180.1.1. You do not necessarily need to use phone numbers. In the SIP architecture, the registered extension could be flavio@voip.school as well.

![Registrazione SIP: il telefono invia un REGISTER collegando l'estensione 8500 al suo indirizzo IP, il registrar memorizza il contatto nel database di localizzazione e risponde con 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### Operazione del proxy

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![Operazione del proxy: il proxy SIP rimane nel percorso di segnalazione (INVITE/200 OK) e ricerca il chiamato nel server di localizzazione, mentre i media RTP fluiscono direttamente tra i due endpoint](../images/07-sip-and-pjsip-fig03.png)

#### Operazione di reindirizzamento

Durante il reindirizzamento, il server SIP invia semplicemente un messaggio (ad es., 302 moved temporarily) all'agente utente e rimane fuori dal percorso dei nuovi messaggi. È molto leggero in termini di utilizzo delle risorse, ma non hai alcun controllo. Il reindirizzamento è talvolta utilizzato nei progetti di bilanciamento del carico.

![Operazione di reindirizzamento: il server di reindirizzamento risponde all'INVITE con un 302 Moved Temporarily contenente il contatto, quindi si ritira mentre il chiamante reinvia INVITE/ACK direttamente alla nuova destinazione](../images/07-sip-and-pjsip-fig04.png)

#### Come Asterisk gestisce SIP

È importante capire che Asterisk non è né un proxy SIP né un redirector SIP. Asterisk può svolgere il ruolo di registrar e server di localizzazione; tuttavia, collega solo due UAC a sé stesso. Pertanto, Asterisk è considerato un back-to-back user agent (B2BUA). In altre parole, collega due canali SIP, mettendoli in ponte tra loro. Asterisk dispone di un meccanismo di re‑invite che può far parlare direttamente i canali SIP tra loro invece di passare attraverso Asterisk. Su un endpoint PJSIP questo è controllato dal parametro `direct_media`. Quando si utilizza `direct_media=yes` il flusso RTP va direttamente da un endpoint all’altro, liberando le risorse del server.

#### Operazione SIP con direct_media=yes

![Operazione SIP con directmedia=yes: il segnalamento SIP passa attraverso Asterisk mentre l'audio RTP va direttamente tra i due telefoni, liberando le risorse del server](../images/07-sip-and-pjsip-fig05.png)

Tuttavia, se è necessario trasferire o registrare la chiamata usando Asterisk, è possibile utilizzare il parametro `direct_media=no` per forzare il flusso RTP attraverso il server Asterisk.

#### Operazione SIP con direct_media=no

![Operazione SIP con directmedia=no: sia la segnalazione SIP sia l'audio RTP sono ancorati tramite Asterisk, consentendo di registrare, transcodificare o trasferire la chiamata](../images/07-sip-and-pjsip-fig06.png)

#### Messaggi SIP

I messaggi SIP di base sono:

- INVITE – stabilimento della connessione
- ACK – riconoscimento
- BYE – terminazione della connessione
- CANCEL – terminazione della connessione per una chiamata non stabilita
- REGISTER – registra un UAC a un proxy SIP
- OPTIONS – può essere usato per verificare la disponibilità
- REFER – trasferisce una chiamata SIP a un altro destinatario
- SUBSCRIBE – si iscrive a eventi di notifica
- NOTIFY – invia informazioni sul canale
- INFO – invia vari messaggi (ad es., DTMF )
- MESSAGE – invia messaggi istantanei

Le risposte SIP sono in formato testo e sono facilmente leggibili (simili ai messaggi HTTP). Le risposte più importanti sono:

- 1XX – Messaggi informativi (100–trying, 180–ringing, 183–progress)
- 2XX – Richiesta completata con successo (200 – OK)
- 3XX – Reindirizzamento chiamata, la richiesta deve essere indirizzata altrove (302 – moved temporarily, 305 – use proxy)
- 4XX – Errore (403 – Forbidden)
- 5XX – Errore del server (500 – Internal Server Error; 501 – Not implemented)
- 6XX – Fallimento globale (606 – Not acceptable)

Ad esempio:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### Session description protocol (SDP)

SDP è stato originariamente definito nell'IETF RFC 2327, ora sostituito dal RFC 4566. È destinato a descrivere le sessioni multimediali ai fini dell'annuncio della sessione, dell'invito alla sessione e di altre forme di avvio di sessioni multimediali. SDP include:

- Transport protocol (RTP/UDP/IP)
- Type of media (text, audio, video)
- Media format or codec (H.261 video, g.711 audio, etc.)
- Information needed to receive these media (addresses, ports, etc.)

The following example is a transcription of a SDP describing a call between two phones.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### Traversata NAT SIP

Network Address Translation (NAT) è una funzionalità utilizzata dalla maggior parte delle reti per risparmiare indirizzi IP Internet. Di solito, un'azienda riceve un piccolo blocco di indirizzi IP, e gli utenti finali ottengono un indirizzo IP in modo dinamico quando si connettono a Internet. NAT risolve il problema di indirizzamento mappando gli indirizzi interni a quelli esterni. Memorizza una mappatura degli indirizzi interni a quelli esterni nella sua memoria. Questa mappatura è valida per un periodo di tempo specifico, dopodiché viene scartata. La mappatura utilizza coppie IP:porta per gli indirizzi interni ed esterni. Esistono quattro tipi di NAT:

- Cono completo
- Cono ristretto
- Cono con restrizione di porta
- Simmetrico

La teoria NAT di seguito — i quattro tipi di NAT, il problema dell'header Contact, i keep-alives e il forzare i media attraverso il server — è a livello di protocollo e si applica a qualsiasi implementazione SIP. Il modo in cui si configura ciascun comportamento su Asterisk 22 (PJSIP) è trattato più avanti in questo capitolo sotto *Nat traversal on res_pjsip*.

#### Full Cone

Il primo NAT, full cone, rappresenta una mappatura statica da una coppia IP:porta esterna a una coppia IP:porta interna. Qualsiasi computer esterno può connettersi ad essa usando la coppia IP:porta esterna. Questo è il caso nei firewall non stateful implementati con l'uso di filtri.

![Full Cone NAT: l'host interno (10.0.0.1:8000) è mappato staticamente alla coppia esterna 200.180.4.168:1234, così qualsiasi computer esterno può inviare pacchetti a quella coppia e raggiungere l'host interno](../images/07-sip-and-pjsip-fig11.png)

#### Cono ristretto

Nello scenario di NAT a cono ristretto, la coppia IP:porta esterna viene aperta solo quando il computer interno invia dati a un indirizzo esterno. Tuttavia, il NAT a cono ristretto blocca tutti i pacchetti in ingresso provenienti da un indirizzo diverso. In altre parole, il computer interno deve inviare dati a un computer esterno prima di poter ricevere dati di ritorno.

#### Cono a Porta Ristretta

Il firewall a cono restritto di porta è quasi identico al cono restritto. L'unica differenza è che, ora, il pacchetto in ingresso deve provenire esattamente dallo stesso IP e porta del pacchetto inviato.

#### Simmetrico

L'ultimo tipo di NAT si chiama symmetric. È diverso dai primi tre perché viene creata una mappatura specifica per ogni indirizzo esterno. Solo indirizzi esterni specifici sono consentiti a tornare tramite la mappatura NAT. Non è possibile prevedere la coppia IP:porta esterna che verrà usata dal dispositivo NAT. Gli altri tre tipi di NAT consentono l'uso di un server esterno per scoprire l'indirizzo IP esterno per la comunicazione. Con il NAT symmetric, anche se riesci a connetterti a un server esterno, l'indirizzo scoperto non può essere usato per nessun altro dispositivo se non per questo server.

![NAT simmetrico: per ogni destinazione viene assegnata una porta sorgente esterna diversa, quindi la mappatura scoperta verso un server non può essere riutilizzata da un altro host, il che interrompe il traversal basato su STUN】(../images/07-sip-and-pjsip-fig12.png)

#### Tabella del firewall NAT

La tabella seguente riepiloga i quattro tipi di NAT.

| Tipo NAT | Deve inviare dati per primo | Può determinare l'IP:porta esterno per i pacchetti di ritorno | Limita i pacchetti in ingresso all'IP:porta di destinazione |
| --- | --- | --- | --- |
| Full Cone | No | Yes | No |
| Restricted Cone | Yes | Yes | Only IP |
| Port Restricted Cone | Yes | Yes | Yes |
| Symmetric | Yes | No | Yes |

#### Segnalazione SIP e RTP su NAT

Alcuni dei problemi più grandi nella traversata NAT sono che devi risolvere due problemi: segnalazione SIP e audio (RTP). La maggior parte dei problemi di audio a senso unico è correlata al NAT. Una cosa interessante di SIP è che, quando un UAC invia un pacchetto, incorpora l'indirizzo IP nell'intestazione SIP “Contact”. Di solito questo è un indirizzo interno (RFC1918); le risposte a questo pacchetto non possono essere instradate su Internet verso l'UAC. Le soluzioni concettuali sono sempre le stesse:

- **Ignora l'indirizzo Contact/Via e rispondi a dove il pacchetto è realmente arrivato.** Questo è il comportamento definito in RFC 3581 (`rport`). Su PJSIP è `force_rport=yes`, e `rewrite_contact=yes` riscrive il contatto memorizzato all'indirizzo di origine.  
- **Invia i media all'indirizzo da cui è arrivato realmente l'RTP** (RTP simmetrico, storicamente chiamato *comedia*). Su PJSIP è `rtp_symmetric=yes`.  
- **Mantieni aperta la mappatura NAT.** Se la mappatura scade, Asterisk non può più inviare un INVITE al UAC — il telefono può effettuare chiamate ma non riceverle. L'invio periodico di OPTIONS (un *qualify*) mantiene il foro aperto. Su PJSIP è `qualify_frequency=` sull'AOR.

Se il NAT dell'utente è del tipo simmetrico, non è possibile inviare pacchetti da un UAC all'altro direttamente; in tal caso è necessario forzare l'RTP attraverso Asterisk con `direct_media=no`. Queste configurazioni sono appropriate per la maggior parte dei casi. È possibile ottimizzare il traffico usando tecniche avanzate come Simple Traversal of UDP over NAT (STUN), utile con full cone, restricted cone e port restricted cone, e Application Layer Gateway (ALG). Sfortunatamente, la maggior parte dei firewall odierni — anche i router DSL/cable domestici — sono simmetrici, rendendo STUN inutilizzabile. ALG potrebbe risolvere il problema, ma non è supportato, non è implementato o è difettoso nella maggior parte dei casi.

#### Asterisk dietro NAT

Sometimes the Asterisk server itself is implemented behind a firewall with NAT — a very common situation when you deploy in the cloud. In this case it is necessary to do some extra configuration so that Asterisk advertises its **public** address in the SIP and SDP headers instead of its private one.

Concettualmente ci sono tre passaggi:

- Inoltrare la porta di segnalazione SIP (UDP 5060 per impostazione predefinita) dal firewall al server Asterisk.
- Inoltrare l’intervallo di porte media RTP (UDP 10000–20000 per impostazione predefinita, impostato in `rtp.conf`) dal firewall al server Asterisk.
- Indicare ad Asterisk il suo indirizzo esterno e quale rete è locale, così saprà quando sostituire l’indirizzo pubblico negli header.

Su PJSIP questi ultimi due elementi corrispondono a `external_media_address` / `external_signaling_address` e `local_net=` sul **transport**, e l’intervallo di porte RTP è ancora configurato in `rtp.conf`:

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

La configurazione PJSIP completa e funzionante per un server Asterisk dietro NAT è fornita più avanti in questo capitolo sotto *Asterisk Server behind NAT*.

### Limitazioni SIP

Asterisk utilizza il flusso RTP in ingresso per sincronizzare il flusso in uscita. Se il flusso in ingresso viene interrotto (silence suppression), music-on-hold verrà interrotta. In altre parole, non dovresti usare la silence suppression nei telefoni o nei provider con Asterisk.

## PJSIP: il canale SIP

PJSIP è il canale SIP in Asterisk. È stato introdotto per la prima volta in Asterisk 12 e, dopo anni di sviluppo, è diventato il canale SIP predefinito e consigliato, e in Asterisk 22 (l’attuale LTS) è l’unico driver del canale SIP. PJSIP si basa sul progetto di Teluu chiamato pjproject. Lo stack pjproject è impiegato da molti softphone e implementazioni SIP commerciali. È uno stack SIP versatile e maturo.

### Perché usare PJSIP

PJSIP è stato ridisegnato da zero il modo in cui Asterisk parla SIP, ed è utile comprendere le funzionalità che lo hanno reso lo standard.

#### Funzionalità

Il canale supporta molte funzionalità, alcune meritano una menzione qui

- Registrazioni multiple: È possibile utilizzare più di un telefono collegato allo stesso Address of Record. In altre parole, è possibile collegare due telefoni allo stesso endpoint.
- Friendly Application Program Interface (API). L’API è modulare e facile da estendere, costruita da molti piccoli moduli cooperanti anziché da un unico grande blocco di codice.
- Trasporti multipli: È possibile ascoltare più indirizzi, porte e trasporti quando si usa PJSIP. Non si è limitati a un unico indirizzo di bind per tutti i dispositivi. PJSIP è molto flessibile.

#### Una nota sulla configurazione

La configurazione di PJSIP è più verbosa: richiede un po' più di impegno e più righe di configurazione, poiché ogni dispositivo è descritto da diversi oggetti correlati anziché da un unico blocco peer. Questa struttura aggiuntiva è ciò che conferisce a PJSIP la sua flessibilità, e la procedura guidata di configurazione (trattata più avanti) mantiene breve il provisioning quotidiano.

### Moduli PJSIP

Il canale PJSIP è implementato da molti moduli descritti di seguito:

#### res_pjsip

Questo è lo strato base di PJSIP e il modulo principale. È responsabile di alcuni dei servizi principali.

#### res_pjsip_session

Questo modulo è responsabile delle sessioni multimediali, dell’elaborazione del protocollo di descrizione della sessione e di alcuni addon.

#### res_pjsip_messaging

Elabora i messaggi SIP e analizza le intestazioni SIP.

#### res_pjsip_registrar

Responsabile della gestione delle registrazioni SIP.

#### res_pjsip_pubsub

Responsabile dell’elaborazione di subscribe, notify e publish. Questi messaggi gestiscono la presenza SIP e il BLF (Busy Lamp Field).

### Configurazione PJSIP

PJSIP ha molte sezioni diverse. Il formato della sezione è:

```
[Section Name]
Option = Value
Option = Value
```

#### Sezione endpoint

L'oggetto di configurazione più importante è l'endpoint. La configurazione dell'endpoint ha funzionalità di base e deve essere associata a una sezione AOR e Transport. Esempio:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

Se guardi l'esempio sopra, l'endpoint è una sorta di colla che collega tutte le sezioni insieme. Specifica un trasporto, l'indirizzo di record e l'autenticazione per un telefono. Definisce anche la parte più importante, il punto di ingresso del contesto nel dialplan.

#### Address of Record (AOR)

Questo oggetto indica ad Asterisk dove contattare l'endpoint. Memorizza gli indirizzi di contatto. Consente inoltre la configurazione delle caselle vocali. Esempio:

```
[softphone]
type=aor
max_contacts=2
```

#### Autenticazione

Questa sezione è responsabile dell'autenticazione in ingresso e in uscita. La documentazione si trova nel file di esempio pjsip.conf. Esempio:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### Transport

La sezione transport consente di definire indirizzi IPV4 e IPV6 e il protocollo di trasporto, TCP, UDP, TLS, Websockets e così via. È inoltre possibile configurare indirizzi Natted in questa sezione. È possibile creare più transport, ma non possono condividere lo stesso IP e porta e non è possibile associare più transport TCP o TLS della stessa versione IP. Esempio:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### Registrazione

Questo oggetto è usato per configurare una registrazione in uscita. Esempio:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### Identifica

Questo oggetto controlla a quale richiesta SIP appartiene ciascun endpoint. Se non è presente una sezione identify, il sistema confronterà il contenuto dell’intestazione “From” con il nome dell’endpoint. Utilizzando questa sezione, è possibile assegnare indirizzi IP specifici a endpoint specifici, identificati per nome utente o IP. Esempio:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

L'oggetto ACL consente di configurare reti specifiche con accesso all'endpoint. Ora le ACL sono definite in una sezione specifica o in acl.conf. Esempio:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relazione tra le entità

The relationship between the configuration objects provides a great flexibility for configuration. However, it seems a bit complex for anyone starting.

![Relazioni tra gli oggetti di configurazione PJSIP: l'endpoint è collegato a transport, auth e AOR (che contiene i contatti); la registrazione è legata a transport e auth; identify punta all'endpoint, mentre ACL e domain alias sono autonomi](../images/07-sip-and-pjsip-fig14.png)

The graphic above means:

#### Relazioni:

| Oggetti | Cardinalità |
| --- | --- |
| ENDPOINT / AOR | molti a molti |
| ENDPOINT / AUTH | zero a molti, a zero o uno |
| ENDPOINT / IDENTIFY | zero o uno |
| ENDPOINT / TRANSPORT | zero a molti, almeno uno |
| REGISTRATION / AUTH | zero a molti, a zero o uno |
| REGISTRATION / TRANSPORT | zero a molti, almeno uno |
| AOR / CONTACT | molti a molti |

ACL and DOMAIN_ALIAS don’t have a direct configuration relationship to the other objects.

### Configurazione di un Softphone

To configure a softphone you have to define many different sections. Below an example on how to configure a softphone. For the client side you can use the SipPulse Softphone (https://www.sippulse.com/produtos/softphone), which you can download and register against the endpoint below.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

La configurazione sopra imposta un trasporto per UDP sulla porta 5060, quindi definisce un endpoint, la sua autenticazione tramite nome utente e password e infine l’Address of Record con un massimo di due contatti.

### Configurare un trunk SIP

Per configurare un trunk SIP è necessario conoscere l’indirizzo IP o l’host del trunk SIP, il nome e la password. È necessario creare una nuova sezione di registrazione a questo scopo.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Traversal NAT su res_pjsip

Il Network Address Translation è stato creato molto tempo fa come modo per gestire la carenza di indirizzi IPv4. Molte persone lo usano anche come funzionalità di sicurezza per nascondere gli indirizzi interni di una rete dalla Internet pubblica. Talvolta sarà necessario gestire il traversal NAT. In alcuni casi, il server può trovarsi dietro NAT, ad esempio quando si distribuisce il server nel cloud. Molte volte, se si distribuisce nel cloud, anche gli utenti saranno dietro un router NAT. Per organizzare le cose, divideremo l'argomento in due parti. La prima riguarda il server Asterisk dietro NAT, come in una distribuzione cloud. Nella seconda sezione, vedremo come supportare i client dietro NAT usando res_pjsip.

#### Server Asterisk dietro NAT

Quando il server Asterisk è dietro NAT, è necessario indicare gli indirizzi esterno e interno nella sezione transport. Avremo le seguenti direttive.

##### direct_media

Il flusso multimediale avviene direttamente da peer a peer o attraverso il server? Per il NAT dovrebbe passare attraverso il server. Per il NAT selezionare no. Esempio:

```
direct_media=no
```

##### external_media_address

Indirizzo media per gestire RTP esterno. Di solito è lo stesso di external_signaling_address. Usa l'indirizzo IP pubblico del tuo server per media e segnalazione. Esempio:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

Indirizzo SIP esterno dove ricevere i messaggi. Esempio:

```
external_signaling_address=54.232.1.20
```

##### local_net

La rete che consideri la tua rete locale. Esempio:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### Esempio completo di trasporto per un server Asterisk dietro NAT

Per utilizzare un server Asterisk dietro NAT devi eseguire due passaggi. Prima, definisci un trasporto dietro NAT. Secondo, associa questo trasporto all'endpoint.

##### Creazione del trasporto dietro NAT

Per creare il trasporto dietro NAT nel file pjsip.conf crea una sezione come mostrato di seguito.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

Associate the transport to an endpoint

--- 

Associa il trasporto a un endpoint

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

Per i trunk SIP dovresti anche associare il trasporto alla sezione di registrazione come mostrato di seguito.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Utilizzare Asterisk con client dietro NAT

Per utilizzare i telefoni dietro NAT è necessario configurare alcuni parametri aggiuntivi per endpoint.

##### direct_media

Il flusso multimediale avviene direttamente da peer a peer o attraverso il server? Per NAT dovrebbe passare attraverso il server. Esempio:

```
direct_media=no
```

##### rtp_symmetric

Questo è ciò che chiamiamo comedia. Invece di fare affidamento sull'indirizzo definito in questo header SDP come di consueto in SIP, usa l'indirizzo da cui ricevi il primo pacchetto rtp e rispondi dallo stesso indirizzo. Esempio:

```
rtp_symmetric=yes
```

##### force_rport

Questo è il comportamento definito nella RFC3581. Invece di utilizzare l'indirizzo nell'intestazione VIA, invia le risposte da dove provengono le richieste. Esempio:

```
force_rport=yes
```

##### qualify_frequency

Questa impostazione deve essere applicata all'AOR (non all'endpoint). C'è anche l'ultimo passaggio, configurare l'opzione qualify. Dovresti sempre avere alcuni pacchetti che pingano la destinazione per mantenere aperta la mappatura NAT. Questo è impostato nella sezione AOR. Esempio:

- qualify_frequency=15

Esempio completo di un endpoint in cui il server e il client sono dietro NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Nominazione del Canale

Come al solito, uno degli aspetti importanti di un canale è la sua denominazione e PJSIP presenta alcuni dettagli interessanti. Si chiama un endpoint PJSIP con la tecnologia `PJSIP/`:

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

Una funzione utile è la possibilità di chiamare tutti i contatti registrati a un AOR in una sola volta. La funzione PJSIP_DIAL_CONTACTS verrà tradotta nella lista dei contatti da chiamare.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

Comporre un trunk è leggermente diverso. Supponi che il trunk non sia registrato sulla tua piattaforma o non abbia un indirizzo IP associato al tuo AOR (address of record). Puoi specificare l'indirizzo del trunk direttamente nella linea. Usando un numero internazionale come esempio.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

Se preferisci specificare l'indirizzo del trunk nella sezione AOR, puoi anche usare.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### Wizard di configurazione PJSIP

PJSIP è potente ma verboso da configurare: molte sezioni diverse e template che possono risultare confusi inizialmente. La buona notizia è il wizard di configurazione PJSIP. Definendo ogni canale in poche righe, consente di creare template e semplificare la configurazione di nuovi dispositivi. Usa il file **pjsip_wizard.conf** per configurare. Devi comunque definire le sezioni transport e global nel file **pjsip.conf**. Personalmente, preferisco usare il wizard solo per i telefoni; per i trunk SIP di solito il numero non è elevato e puoi configurare direttamente in pjsip. Il più grande vantaggio del wizard è la possibilità di usare i template e creare telefoni rapidamente.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Caricamento e scaricamento di PJSIP

PJSIP è l'unico canale SIP in Asterisk 22, e i suoi moduli sono caricati per impostazione predefinita. In rari casi potresti comunque voler controllare il caricamento dei moduli dal file modules.conf — ad esempio, per disabilitare PJSIP su un server che utilizza solo IAX2 o DAHDI.

#### Per disabilitare PJSIP

Modifica il file modules.conf e aggiungi le seguenti righe.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### Comandi della console

Ora che hai configurato i tuoi endpoint PJSIP, è il momento di vedere come verificare la tua configurazione. Esistono molti comandi della console per aiutarti in questo compito. Dopo aver modificato pjsip.conf, ricarica la configurazione con:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

You can also restrict the logging to a single host with `pjsip set logger host <ip>`.

#### pjsip set history on

A great addition to PJSIP is the concept of history. You can capture and analyse SIP request and replies in real time in an easy way. To start history use the command below.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

Now you can show the history:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

Then to see a specific request or reply, show the history item:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

Very easy, isn’t it? You may also clear the history whenever you want using `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Sommario

SIP è il protocollo di segnalazione IETF che crea, modifica e termina le sessioni multimediali. I suoi user agent, proxy, registrar e gateway scambiano messaggi basati su testo — REGISTER, INVITE, le risposte provvisorie e finali, ACK e BYE — mentre SDP negozia i codec e RTP trasporta i media. Questa teoria del protocollo è senza tempo e si applica a qualsiasi implementazione SIP.

In Asterisk 22 si utilizza SIP tramite **PJSIP** (`chan_pjsip`), configurato in `pjsip.conf`. Invece di un unico peer monolitico, un dispositivo è modellato come un insieme di piccoli oggetti intercorrelati: `endpoint` (comportamento della chiamata e codec), `auth` (credenziali), `aor` (dove è raggiungibile) e `transport` (l’ascoltatore), più `identify` (corrispondenza di un trunk per IP) e `registration` (registrazione in uscita) per i provider di servizi. Hai visto come questi oggetti si integrano, come configurare sia i telefoni sia i trunk, come le opzioni di attraversamento NAT (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media` e i `external_*`/`local_net` del trasporto) risolvono le implementazioni reali, e come ispezionarli tutti con `pjsip show endpoints`, `aors`, `contacts` e `registrations`.

## Quiz

1. Nell'architettura SIP, quale componente riceve una richiesta e la risponde con una risposta di reindirizzamento (come `302 Moved Temporarily`) contenente la nuova posizione, per poi uscire dal percorso dei messaggi successivi?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. Quale ruolo svolge Asterisk quando gestisce una chiamata SIP tra due telefoni?
   - A. Un proxy SIP che rimane solo nel percorso di segnalazione
   - B. Un server di reindirizzamento SIP
   - C. Un back-to-back user agent (B2BUA) che collega due canali SIP
   - D. Un bilanciatore di carico SIP senza stato

3. Quale metodo SIP utilizza un telefono per informare il registrar del proprio indirizzo IP corrente in modo da poter ricevere chiamate in seguito?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. Vero o Falso: In Asterisk 22, `chan_sip` e `sip.conf` sono ancora disponibili come fallback legacy accanto a PJSIP.

5. Quali oggetti di configurazione devono essere associati a un endpoint affinché Asterisk conosca il socket di ascolto da utilizzare e dove inviare le chiamate per quel dispositivo? (Seleziona tutti quelli applicabili.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. In un oggetto PJSIP `aor`, quale impostazione mantiene aperta la mappatura NAT qualificando periodicamente il contatto, e qual è la sua unità?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. Completa la frase: Per far corrispondere a Asterisk una richiesta SIP in ingresso a un endpoint specifico per indirizzo IP di origine (invece che per l'intestazione `From`), crei una sezione con `type=________`.

8. Quale oggetto PJSIP è usato per configurare una **registrazione outbound** da Asterisk a un provider di trunk SIP?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Nella CLI di Asterisk 22, quale comando abilita il logger dei pacchetti SIP che stampa ogni richiesta e risposta SIP sulla console?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. Su un endpoint PJSIP che serve un telefono dietro un NAT simmetrico, quale coppia di impostazioni fa rispondere Asterisk all'indirizzo di origine della richiesta (RFC 3581) e invia i media dove effettivamente arrivano i pacchetti RTP?
    - A. `direct_media=yes` e `srvlookup=yes`
    - B. `force_rport=yes` e `rtp_symmetric=yes`
    - C. `allowguest=yes` e `insecure=invite`
    - D. `qualify=yes` e `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
