# Costruire il tuo primo PBX con PJSIP

In questo capitolo imparerai a eseguire una configurazione di base di un PBX Asterisk. L'obiettivo principale è vedere il PBX in funzione per la prima volta, riuscire a chiamare tra le estensioni, riprodurre un messaggio e chiamare un singolo trunk analogico o SIP. L'idea alla base di questo capitolo è garantire che il tuo Asterisk sia avviato e funzionante il più rapidamente possibile. Dopo aver completato le attività di questo capitolo, avrai le conoscenze sufficienti per prepararti ai capitoli successivi, in cui approfondiremo maggiormente i dettagli di configurazione.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Comprendere e modificare i file di configurazione;
- Installare softphone basati su SIP;
- Installare e configurare un trunk SIP;
- Installare e configurare una connessione analogica;
- Effettuare chiamate tra estensioni;
- Effettuare chiamate tra telefoni e destinazioni esterne; e
- Configurare un operatore automatico.

## Understanding the configuration files

Asterisk è controllato da file di configurazione testuali situati in /etc/asterisk. Il formato del file è simile ai file “.ini” di Windows. Un punto e virgola è usato come carattere di commento, i segni “=” e “=>” sono equivalenti, e gli spazi sono ignorati.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpreta “=” e “=>” allo stesso modo. Le differenze di sintassi sono usate per distinguere tra oggetti e variabili. Usa “=” quando vuoi dichiarare una variabile e “=>” per designare un oggetto. La sintassi è la stessa in tutti i file, ma vengono usati tre tipi di grammatica, come discusso di seguito.

## Grammars

| Grammar | How the object is created | Conf. file | Example |
|---------|---------------------------|------------|---------|
| Simple Group | All in the same line | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Options are defined first, the object inherits the options | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Each entity receives a context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

Il formato di gruppo semplice usato in `extensions.conf` e `voicemail.conf` è la grammatica più elementare. Ogni oggetto è dichiarato con le opzioni nella stessa riga. Esempio:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

In questo esempio, l'oggetto 1 è creato con le opzioni op1, op2 e op3 mentre l'oggetto 2 è creato con le opzioni op1, op2 e op3.

### Object options inheritance grammar

Questo formato è usato nei file chan_dahdi.conf e agents.conf, dove sono disponibili numerose opzioni, e la maggior parte delle interfacce e degli oggetti condivide le stesse opzioni. Tipicamente, una o più sezioni contengono dichiarazioni di oggetti e canali. Le opzioni per l'oggetto sono dichiarate sopra l'oggetto e possono essere cambiate per un altro oggetto. Sebbene questo concetto sia difficile da comprendere, è molto facile da usare. Esempio:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Le prime due righe configurano il valore delle opzioni op1 e op2 a “bas” e “adv”, rispettivamente. Quando l'oggetto 1 è istanziato, viene creato usando l'opzione 1 come “bas” e l'opzione 2 come “adv”. Dopo aver definito l'oggetto 1, cambiamo l'opzione 1 in “int”. Successivamente, creiamo l'oggetto 2 con l'opzione 1 impostata a “int” e l'opzione 2 a “adv”.

### Complex entity object

Questo formato è usato in pjsip.conf, iax.conf e altri file di configurazione in cui esistono numerose entità con molte opzioni. Tipicamente, questo formato non condivide un grande volume di configurazioni comuni. Ogni entità riceve un contesto. A volte esistono contesti riservati, come [general] per le configurazioni globali. Le opzioni sono dichiarate nelle dichiarazioni di contesto. Esempio:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

L'entità [entity1] ha i valori “value1” e “value2” per le opzioni op1 e op2, rispettivamente. L'entità [entity2] ha i valori “value3” e “value4” per le opzioni op1 e op2.

## Opzioni per costruire un LAB per Asterisk

Per configurare un PBX, avrai bisogno di qualche hardware di base. Non è difficile né costoso, ma ci sono alcune opzioni da considerare. Tutto ciò che ti serve sono due telefoni e una connessione alla rete pubblica. Alcune opzioni e combinazioni sono possibili quando crei il tuo laboratorio, di cui parleremo di seguito.

### Opzione 1: LAB completo

Con il LAB completo è possibile testare tutti gli scenari disponibili e confrontare soluzioni come ATA, telefoni IP e softphone. Puoi anche approfondire i trunk analogici e SIP. Avrai bisogno di:

- Un SIP analog telephone adapter (ATA)
- Un telefono IP
- Un server dedicato per Asterisk
- Una workstation con un softphone
- Una scheda di interfaccia analogica con almeno due interfacce (1 FXO e 1 FXS)
- Un account con un provider VoIP

### Opzione 2: LAB economico

Con il LAB economico lo semplifichiamo un po'. Utilizziamo l'ATA, che di solito è meno costoso del telefono IP, e una singola scheda FXO, davvero economica. Non potremo usare telefoni analogici collegati direttamente al server, ma ciò non accade comunemente nella pratica. Avrai bisogno di:

- Un SIP analog telephone adapter (ATA)
- Un server dedicato per Asterisk
- Una workstation per il softphone
- Una scheda di interfaccia analogica con 1 FXO
- Un account con un provider VoIP

### Opzione 3: LAB super economico

Il terzo LAB utilizza un server virtualizzato nel notebook dello studente. Il problema di questo modello sono i conflitti generati dalla porta UDP. A volte sia il server Asterisk sia il softphone cercano di accedere alla stessa porta, impedendo ad Asterisk di associare la porta dell'indirizzo. Un altro problema è la qualità delle chiamate; gli ambienti virtuali non sono indicati per applicazioni in tempo reale come Asterisk. Usa un softphone gratuito per il server e la workstation e una connessione trunk a un provider SIP. Avrai bisogno di:

- Un laptop che esegue un softphone
- Una macchina virtuale (VirtualBox, VMware o simile) per installare Asterisk
- Un account con un provider VoIP

## Sequenza di Installazione

Per aiutarti a comprendere la sequenza di installazione, abbiamo delineato i passaggi necessari per installare e configurare Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. Configurazione delle estensioni
   - a. Estensioni SIP (ATA, Softphone, IP Phone)
   - b. Estensioni IAX
   - c. Estensioni FXS
2. Configurazione del trunk
   - a. Configurazione di un trunk SIP
   - b. Configurazione di un trunk FXO
3. Creazione di un dialplan di base
   - a. Composizione tra estensioni
   - b. Composizione verso destinazioni esterne
   - c. Ricezione di una chiamata nell'estensione operatore
   - d. Ricezione di una chiamata in un auto-attendant

## Configurazione delle estensioni

Le estensioni sono telefoni SIP, IAX o analogici collegati a una porta FXS. Per configurare un’estensione, è necessario modificare il file di configurazione relativo al canale (pjsip.conf, iax.conf, chan_dahdi.conf)

### Estensioni SIP

Su Asterisk 22, PJSIP (lo stack `res_pjsip`, configurato in `/etc/asterisk/pjsip.conf`) è il driver del canale SIP. Supporta più trasporti per endpoint, è attivamente mantenuto ed è l’unico driver SIP fornito con la piattaforma. (Il driver originale `chan_sip` è stato rimosso in Asterisk 21 — vedere il capitolo *Legacy channels* se è necessario migrare una vecchia configurazione.)

L’idea qui è configurare una PBX semplice. (I capitoli successivi forniscono una sessione SIP/PJSIP completa con tutti i dettagli.) PJSIP è configurato in `/etc/asterisk/pjsip.conf` e contiene tutti i parametri relativi ai telefoni SIP e ai provider VoIP. I client SIP devono essere configurati prima di poter effettuare e ricevere chiamate.

#### Il trasporto

In PJSIP, la configurazione del listener (indirizzo di bind, porta, protocollo) vive in un oggetto `transport`. Asterisk ha una protezione integrata contro il guessing dei nomi utente — restituisce sempre una sfida di autenticazione identica per utenti sconosciuti e noti, e le richieste non identificate ripetute da un IP sono limitate in frequenza tramite le opzioni `[global]` `unidentified_request_count`/`unidentified_request_period`. Le principali opzioni di un trasporto sono:

- protocol: Il protocollo di trasporto — `udp`, `tcp`, `tls`, `ws` o `wss`.  
- bind: Indirizzo e porta a cui il listener si lega. Se si imposta l’indirizzo a `0.0.0.0`, si lega a tutte le interfacce; la porta SIP predefinita è 5060 per UDP/TCP.

Un trasporto UDP minimale:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP consente alle sezioni `endpoint`, `auth` e `aor` di condividere lo stesso nome di sezione (ad esempio i due blocchi `[6001]` sopra, distinti dal loro `type=`); molti amministratori invece aggiungono un suffisso (`[6001]`, `[6001-auth]`, `[6001]` aor) per migliorare la leggibilità. Per un dispositivo che si registra, il contatto viene appreso dinamicamente quando il telefono si registra, quindi l'AOR non necessita di un `contact` statico.

## IAX Extensions

`chan_iax2` still ships in Asterisk 22 but is now legacy; SIP/PJSIP is the preferred protocol for new deployments.

You may also create IAX extensions. This protocol is native to the Asterisk, and we will have an entire section devoted to it later in this book. For now, let’s create a few extensions using the protocol. As the first section to be configured, the section [general] has certain parameters to be configured. The main options are:

- allow/disallow: Defines which codecs are going to be used.
- bindaddr: Address the IAX2 listener binds to. If you set it up as 0.0.0.0 (default), it will bind to all interfaces.
- context: Sets the default context for all clients unless changed in the client section. We used dummy for security reasons. Unauthenticated users get into this context when the option allowguest is set to yes.
- bindport: IAX2 UDP port to listen on (default 4569).
- delayreject: When set to yes, delays the sending of an authentication reject for a REGREQ or AUTHREQ, which improves the security against brute-force password attacks.
- bandwidth: When set to high, it allows the selection of high bandwidth codecs, such as the g711 in their variants ulaw and alaw.

The following is a sample of the [general] section of the file iax.conf.

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX Clients

After finishing the general sections, it is time to set up the IAX clients.

- `[name]`: The section name is the IAX peer/user name; an incoming IAX connection is matched to it by name.
- `type`: The connection class — `peer`, `user`, or `friend`:
  - `peer`: Asterisk sends calls to a peer.
  - `user`: Asterisk receives calls from a user.
  - `friend`: both directions at once.
- `host`: IP address or host name. The most common value is `dynamic`, used when the device registers to Asterisk.
- `secret`: Password to authenticate peers and users.

Warning: Use strong passwords with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for IAX md5 hashes are available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers. Example:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configurare i dispositivi SIP

Dopo aver definito i telefoni nel file di configurazione di Asterisk, è il momento di configurare il telefono stesso. In questo esempio, mostreremo come configurare un softphone gratuito — il SipPulse Softphone (scaricalo da https://www.sippulse.com/produtos/softphone). Consulta il manuale del tuo dispositivo per comprendere i parametri del telefono. Passo 1: Configura il telefono per utilizzare l’estensione 6000. Esegui il programma di installazione. Dopo l’esecuzione, apri le impostazioni account/SIP e aggiungi un nuovo account SIP. Compila le informazioni richieste.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Conferma che il tuo telefono sia registrato usando il comando console `pjsip show endpoints` (o `pjsip show endpoint 6000` per i dettagli; `pjsip show contacts` mostra i contatti AOR registrati). Ripeti la configurazione per il telefono 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configurazione dei dispositivi IAX

IAX2 è un protocollo legacy (vedi il capitolo *Legacy channels*), e il Softphone SipPulse è solo SIP, quindi non può registrare un account IAX. Se hai bisogno di testare IAX2, usa un softphone che lo supporti ancora. Crea un nuovo account IAX,

3. Seleziona nuovo account IAX.  
4. Inserisci le opzioni correlate per il telefono 6003 e opzionalmente per il 6004.  
5. Salva la configurazione e verifica se il telefono è registrato usando `iax2 show peers`.

Importante: usa un account per SIP e un altro per IAX. Se vuoi configurare il sistema affinché squilli sia IAX sia SIP contemporaneamente, ti mostreremo come farlo nella sezione del dialplan.

### Configurazione di un'interfaccia PSTN

Per collegarti al PSTN, avrai bisogno di un’interfaccia foreign exchange office (FXO) e di una linea telefonica. Puoi anche usare un’estensione PBX esistente. Puoi ottenere una scheda di interfaccia telefonica con interfaccia FXO da diversi produttori. In questo esempio, ti mostreremo come installare una scheda di interfaccia DAHDI.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### Linee analogiche con DAHDI

Puoi acquistare una scheda analogica compatibile con DAHDI da diversi produttori. X100P è stata una delle prime schede Digium ed è già stata interrotta. Alcuni produttori producono ancora cloni simili. Oltre al prezzo della X100P, abbiamo riscontrato diversi problemi tra queste schede e le nuove schede madri, quindi usala con cautela. X100P, a mio avviso, non è una buona scelta per un ambiente di produzione. Qualsiasi scheda compatibile con DAHDI dovrebbe funzionare. Grazie al team di sviluppatori DAHDI, ora disponiamo di uno strumento per rilevare e configurare le schede di interfaccia quasi automaticamente. Se hai appena installato i driver DAHDI, non dimenticare di eseguire `make config` e riavviare la macchina per caricarli automaticamente. Puoi usare i comandi seguenti per rilevare e configurare la tua scheda. Step 1: Per rilevare l’hardware, usa:

```
dahdi_hardware
```

Passo 2: Per configurare usa:

```
dahdi_genconf
```

Il comando sopra genererà due file /etc/dahdi/system.conf e /etc/asterisk/dahdi-channels.conf. I parametri predefiniti per dahdi_genconf sono di solito adeguati, ma è possibile modificarli nel file /etc/dahdi/genconf_parameters. Per impostazione predefinita, inserirà le linee (FXO) nel contesto from-pstn e i telefoni (FXS) nel contesto from-internal. Passo 3: Dopo aver eseguito dahdi_genconf, nell'ultima riga del file /etc/asterisk/chan_dahdi.conf inserire la seguente riga:

```
#include dahdi-channels.conf
```

Passo 4: Modifica il file /etc/dahdi/modules e commenta tutti i driver non utilizzati. Riavvia prima di procedere e verifica se i canali vengono riconosciuti usando:

```
*CLI> dahdi show channels
```

### Connessione al PSTN tramite un provider VoIP

Se il tuo budget è davvero limitato, puoi configurare un trunk SIP per collegarti al PSTN. È certamente il modo più economico per connettersi al PSTN. Migliaia di provider VoIP esistono in tutto il mondo. Per collegarti a uno di essi, avrai bisogno di alcuni parametri. Parametri forniti dal provider SIP.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

Due parametri devono essere determinati da te.

- Extension to receive calls—in this case: 9999
- context: from-sip

In PJSIP, un trunk SIP di registrazione è costruito dalla stessa famiglia di oggetti usata per un endpoint, più gli espliciti oggetti `registration` e `identify`. L'oggetto `registration` indica ad Asterisk di registrarsi al provider, l'oggetto `identify` corrisponde al traffico in ingresso dall'IP del provider all'endpoint (PJSIP autentica gli INVITE in ingresso per IP di origine), e `outbound_auth` fornisce le credenziali per le chiamate in uscita e la registrazione.

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

Per accedere a questo trunk, utilizzeremo il nome canale `PJSIP/siptrunk`. L’impostazione `dtmf_mode=rfc4733` trasporta DTMF fuori banda (RFC 4733 rende obsoleto il precedente RFC 2833; il payload è identico). L’opzione `identify`/`match` accetta indirizzi IP, CIDR o nomi host, ma i nomi host vengono risolti una sola volta al caricamento della configurazione, quindi per un provider con IP variabili elencare esplicitamente gli IP di segnalazione. Confermare la registrazione con `pjsip show registrations`.

## Introduzione al dial plan

Il dial plan è come il cuore di Asterisk. Definisce come Asterisk gestisce ogni singola chiamata verso il PBX. È costituito da estensioni che creano un elenco di istruzioni da seguire per Asterisk. Le istruzioni vengono attivate dai numeri ricevuti dal canale o dall’applicazione. Per configurare Asterisk con successo, è fondamentale comprendere il dial plan. La maggior parte del dial plan è contenuta nel file extensions.conf nella directory /etc/asterisk. Questo file utilizza la semplice grammatica di gruppo e presenta quattro concetti principali:

- Extensions
- Priorities
- Applications
- Contexts

Creiamo un dial plan di base. Nelle sezioni successive di questo libro, dedicherò un capitolo esclusivamente al dial plan. Se hai installato i file di esempio (make samples), extensions.conf esiste già. Salvalo con un altro nome e inizia con un file vuoto.

## The structure of the file extensions.conf

Il file extensions.conf è suddiviso in sezioni. La prima è la sezione [general] seguita dalla sezione [globals]. L’inizio di ogni sezione comincia con la definizione del suo nome (ad es., [default]) e termina quando viene creata un’altra sezione.

### The section [general]

La sezione general si trova in cima al file. Prima di iniziare a configurare il dialplan, è utile conoscere le opzioni generali che controllano alcuni comportamenti del dialplan. Queste opzioni sono:

- static and write protect: Se `static=yes` e `writeprotect=no`, è possibile salvare il dialplan in esecuzione su disco con il comando CLI:

```
*CLI> dialplan save
```

Warning: Se si esegue un comando `dialplan save` dalla CLI, si perderanno tutte le osservazioni e i commenti nel file.

- autofallthrough: Se autofallthrough è impostato, allora se un’estensione esaurisce le azioni da eseguire, terminerà la chiamata con BUSY, CONGESTION o HANGUP a seconda della migliore ipotesi di Asterisk. Questo è il valore predefinito. Se autofallthrough non è impostato, allora se un’estensione esaurisce le azioni da eseguire, Asterisk attenderà che venga composta una nuova estensione.
- clearglobalvars: Se clearglobalvars è impostato, le variabili globali verranno cancellate e rianalizzate durante un reload del dialplan o un reload di Asterisk. Se clearglobalvars non è impostato, le variabili globali persisteranno attraverso i reload e—anche se eliminate da extensions.conf o da uno dei suoi file inclusi—rimarranno impostate al valore precedente.
- extenpatternmatchnew: Usa un algoritmo di pattern‑matching più veloce, che aiuta notevolmente quando si hanno molte estensioni. Il valore predefinito è no.
- userscontext: Questo è il contesto in cui vengono registrate le voci di users.conf.

### The section [globals]

Nella sezione [globals] si definiscono le variabili globali e i loro valori iniziali. È possibile accedere alla variabile nel dialplan usando ${GLOBAL(variable)}. Si possono anche accedere alle variabili definite nell’ambiente linux/unix usando ${ENV(variable)}. Le variabili globali non distinguono tra maiuscole e minuscole. Alcuni esempi potrebbero essere:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

Nel seguente esempio, è possibile impostare e testare una variabile globale nel dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contesti

Il contesto è la partizione nominata del dialplan. Dopo le sezioni [general] e [globals], il dialplan è un insieme di contesti in cui ogni contesto contiene diverse estensioni, ogni estensione ha diverse priorità, e ogni priorità chiama un’applicazione con diversi argomenti.

![Flusso di chiamata Asterisk: ogni chiamata arriva su un canale (IAX, SIP e altri) come gamba di chiamata in ingresso; il contesto del canale — impostato globalmente o per canale nel file di configurazione del canale — decide quale contesto in extensions.conf elabora la chiamata prima che essa lasci la gamba in uscita.](../images/04-first-pbx-fig03.png)

![Elaborazione della chiamata: il `context=` definito per un canale (in chan_dahdi.conf o pjsip.conf) indica il contesto corrispondente in extensions.conf dove il dialplan gestisce la chiamata.](../images/04-first-pbx-fig04.png)

Puoi costruire un dialplan semplice per raggiungere altri telefoni e la PSTN. Tuttavia, Asterisk è molto più potente di così. Il nostro obiettivo è insegnarti più dettagli su ciò che è possibile nel dialplan.

## Extensions

Unlike the traditional PBX, where extensions are associated with phones, interfaces, menus, and so on, in Asterisk an extension is a list of commands to be processed when a specific extension number or name is triggered. The commands are processed in priority order.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

An extension can be literal, standard, or special. A standard extension includes only numbers or names and the characters * and #; 12#89* is a valid literal extension. Names can be used for extension matching as well. Extensions are case sensitive. However, you cannot create two extensions with the same name but different cases. When an extension is dialed, the command with the first priority is executed followed by the command with priority 2 and so on. This happens until the call is disconnected or some command returns the number one, indicating failure. What Asterisk does when the last priority is executed is regulated by the parameter autofallthrough. See the [general] section in this chapter. Example:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Above you find the list of instructions to be processed when the extension 123 is dialed. The first priority is to answer the channel (necessary when the channel is in the ringing state: i.e., FXO channels). The second priority is to play back an audio file called tt-weasels. The third priority hangs up the channel. Another option is to handle the call according to the caller ID. You can use the / character to specify the caller ID to be processed. Examples:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

This example will trigger extension 123 and execute the following options only if the caller ID is 100. This can also be done by using the pattern described below:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: maps an extension to a channel. It is used to monitor the channel state. It is used in conjunction with presence. The phone has to support it.

#### Patterns

You can use patterns and literals in the dial plan. Patterns are very useful for reducing the dial plan size. All patterns start with the “_” character. The following characters may be used to define a pattern. The figure identifies the patterns available for use with Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk uses some extension names as standard extensions.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Description:

- **s**: Start. It is used to handle a call when there is no dialed number. It is useful for FXO trunks and in-menu processing.
- **t**: Timeout. It is used when calls remain inactive after a prompt has been played. It is also used to hang up an inactive line.
- **T**: AbsoluteTimeout. If you establish a call limit using the `TIMEOUT(absolute)` dialplan function, once the call exceeds the limit defined, it will be sent to the T extension.
- **h**: Hangup. It is called after the user disconnects the call.
- **i**: Invalid. It is triggered when you call an non-existent extension in the context. Using these extensions can affect the content of CDR records—specifically, the dst that does not contain the number dialed.
- **o**: Operator. It is used to go to operator when the user presses "0" during the voicemail.

The use of these extensions can change the content of the billing records (CDR)—in particular, the field dst will not have the number dialed. To work around this problem, you should use the option g in the dial() application and consider the functions resetcdr(w) and/or nocdr()

## Variables

Nel PBX Asterisk, le variabili possono essere globali, specifiche del canale e specifiche dell'ambiente. È possibile utilizzare l'applicazione NoOP() per vedere il contenuto di una variabile nella console. Può usare una variabile globale o una variabile specifica del canale come argomenti dell'applicazione. Una variabile può essere referenziata come nell'esempio seguente, dove varname è il nome della variabile.

```
${varname}
```

Il nome di una variabile può essere una stringa alfanumerica che inizia con una lettera. I nomi delle variabili globali non sono sensibili al maiuscolo/minuscolo. Tuttavia, le variabili di sistema (definite da Asterisk o definite dal canale) sono sensibili al maiuscolo/minuscolo. Pertanto, la variabile ${EXTEN} è diversa da ${exten}.

### Global variables

Le variabili globali possono essere configurate nella sezione [global] del file extensions.conf o utilizzando l'applicazione:

```
set(Global(variable)=content)
```

### Channel-specific variables

Le variabili specifiche del canale sono configurate usando l'applicazione set(). Ogni canale riceve il proprio spazio di variabili. Non c'è rischio di collisioni tra variabili provenienti da canali diversi. Una variabile specifica del canale viene distrutta quando il canale termina la chiamata. Alcune delle variabili più comunemente usate sono:

- ${EXTEN} Extension dialed
- ${CONTEXT} Current context
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} Current caller ID
- ${PRIORITY} Current priority

Le altre variabili specifiche del canale sono tutte in maiuscolo. È possibile vedere il contenuto di diverse variabili usando l'applicazione dumpchan(). Di seguito è riportato un semplice estratto delle variabili dump-channel.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Dumpchan output:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

Il layout dei campi sopra è l'output Asterisk 22 `DumpChan` (un vero nome di canale `PJSIP/...`, i campi `CallerIDNum`/`ConnectedLineID`, e le righe `Raw*`/`Transcode`/`BridgeID` che i canali PJSIP popolano). A differenza del vecchio driver, un canale PJSIP non imposta automaticamente le variabili di canale `SIPCALLID`/`SIPUSERAGENT`; i dettagli SIP equivalenti sono letti su richiesta con le funzioni dialplan `PJSIP_HEADER()` e `CHANNEL()` — per esempio `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` e `${CHANNEL(rtp,dest)}` per l'indirizzo RTP remoto.

### Environment-specific variables

Le variabili specifiche dell'ambiente possono essere usate per accedere a variabili definite nel sistema operativo. È possibile impostare variabili specifiche dell'ambiente usando la funzione ENV(). Per esempio:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

Alcune applicazioni usano variabili per l'input e l'output dei dati. È possibile impostare le variabili prima di chiamare l'applicazione o recuperare la variabile dopo l'esecuzione dell'applicazione. Per esempio: l'applicazione Dial restituisce le seguenti variabili:

- ${DIALEDTIME} ->Questo è il tempo dal momento in cui si compone un canale fino a quando viene disconnesso.
- ${ANSWEREDTIME} -> Questo è il tempo effettivo della chiamata.
- ${DIALSTATUS} Questo è lo stato della chiamata: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Messaggio di errore per la chiamata.

## Expressions

Le espressioni possono essere molto utili nel dial plan. Sono usate per manipolare stringhe ed eseguire operazioni matematiche e logiche.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

La sintassi delle espressioni è definita come segue:

```
$[expression1 operator expression2]
```

Supponiamo di avere una variabile chiamata “I” e di voler aggiungere 100 alla variabile:

```
$[${I}+100]
```

Quando Asterisk trova un'espressione nel dial plan, sostituisce l'intera espressione con il valore risultante.

### Operators

I seguenti operatori possono essere usati per costruire espressioni. È importante osservare la precedenza degli operatori.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

Una regular expression è una stringa di testo speciale usata per descrivere un modello di ricerca. Puoi pensare alle regular expression come a dei caratteri jolly. Le regular expression sono usate per confrontare una stringa con un modello per verificarne la corrispondenza. Se il confronto ha successo e la regular expression contiene almeno una corrispondenza, viene restituita la prima corrispondenza; altrimenti, il risultato è il numero di caratteri corrispondenti.

#### Comparison operators

Il risultato di un confronto è 1 se la relazione è vera o 0 se è falsa.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Inserisci queste espressioni nel tuo dial plan e usa l'applicazione NoOP() per valutarle. Componi 9002 ed esamina i risultati nella console di Asterisk. Usa verbose 15 per mostrare i risultati.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Functions

Alcune applicazioni sono state sostituite da funzioni, che consentono l'elaborazione delle variabili in modo più avanzato rispetto alle sole espressioni. È possibile visualizzare l'elenco completo delle funzioni eseguendo il seguente comando console:

```
*CLI> core show functions
```

Lunghezza della stringa: ${LEN(string)} restituisce la lunghezza della stringa

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Nella prima operazione, il sistema mostra 5 come risultato (il numero di lettere nella parola “fruit”). La seconda restituisce il numero 4 (il numero di lettere nella parola “pear”). Sottostringhe: restituisce la sottostringa, a partire dalla posizione definita dal parametro “offset”, con la lunghezza della stringa definita nel parametro “length”. Se l'offset è negativo, inizia da destra verso sinistra, a partire dalla fine della stringa. Se la lunghezza è omessa o negativa, prende l'intera stringa a partire dall'offset.

```
${string:offset:length }
```

Esempio #1: Diverse sottostringhe

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Esempio #2: Estrarre il prefisso telefonico dalle prime tre cifre.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Esempio #3: Prende tutte le cifre dalla variabile ${EXTEN}, eccetto il prefisso telefonico.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenazione di stringhe

Per concatenare due stringhe, basta scriverle una accanto all'altra.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Applicazioni

Per costruire un dialplan, dobbiamo comprendere il concetto di applicazioni. Userai le applicazioni per gestire il canale nel dialplan. Le applicazioni sono implementate in diversi moduli. Le applicazioni disponibili dipendono dai moduli. Puoi visualizzare tutte le applicazioni Asterisk usando il comando console:

```
*CLI> core show applications
```

In alternativa, puoi mostrare i dettagli di una specifica applicazione usando il seguente esempio:

```
*CLI> core show application Dial
```

Per costruire un semplice dialplan, è necessario conoscere alcune applicazioni. Discuteremo esempi più avanzati più avanti nel libro.

![Il piccolo insieme di applicazioni necessarie per costruire un semplice dialplan: Answer (risponde a un canale), Dial (chiama un altro canale), Hangup (riaggancia un canale), Playback (riproduce un file audio) e Goto (salta a una priorità, estensione o contesto).](../images/04-first-pbx-fig09.png)

Useremo queste applicazioni (sopra) per creare un semplice dialplan per due PBX di base.

### Answer()

[Synopsis] Risponde a un canale se sta squillando [Description] Answer([delay]): Se la chiamata non è stata risposta, l'applicazione la risponderà. Altrimenti, non ha alcun effetto sulla chiamata. Se viene specificato un ritardo, Asterisk attenderà il numero di millisecondi indicato in ‘delay’ prima di rispondere alla chiamata.

### Dial()

La descrizione seguente può essere ottenuta eseguendo il comando `show application dial` nel dialplan. Per una ricerca più semplice, è riprodotta qui sotto. Anche la sintassi per l'applicazione Dial è mostrata di seguito:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

Questa applicazione effettuerà chiamate verso uno o più canali specificati. Non appena uno dei canali richiesti risponde, il canale di origine verrà risposto—se non è già stato risposto. Questi due canali saranno quindi attivi in una chiamata collegata. Tutti gli altri canali richiesti verranno poi chiusi. Se non viene specificato un timeout, l'applicazione Dial attenderà indefinitamente finché uno dei canali chiamati risponde, l'utente riaggancia, o tutti i canali chiamati sono occupati o non disponibili. L'esecuzione del dial plan continuerà se nessun canale richiesto può essere chiamato o se il timeout scade. Questa applicazione imposta le seguenti variabili di canale al completamento:

- DIALEDTIME - Questo è il tempo dal composizione di un canale fino al momento in cui viene disconnesso.
- ANSWEREDTIME - Questo è la durata di una chiamata reale.
- DIALSTATUS - Questo è lo stato della chiamata: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Per le modalità Privacy e Screening, la variabile DIALSTATUS sarà impostata su DONTCALL se la parte chiamata sceglie di inviare la parte chiamante allo script “Go Away”. La variabile DIALSTATUS sarà impostata su TORTURE se la parte chiamata vuole inviare il chiamante allo script “torture”. Questa applicazione segnalerà la terminazione normale se il canale di origine riaggancia o se la chiamata è collegata e una delle parti nel ponte termina la chiamata. L’URL opzionale sarà inviato alla parte chiamata se il canale lo supporta. Se la variabile OUTBOUND_GROUP è impostata, tutti i canali peer creati da questa applicazione saranno inclusi in quel gruppo (come in

```
Set(GROUP()=...).
```

La tabella seguente riassume alcune delle opzioni più frequentemente usate per l'applicazione Dial. Per l'elenco completo, usa il comando console `core show application Dial`. In Asterisk 22 queste opzioni sono separate dal canale e dal timeout da virgole — per esempio `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Riproduce un annuncio alla parte chiamata, usando `x` come file. |
| `C` | Reimposta il CDR per questa chiamata. |
| `d` | Consente all'utente chiamante di digitare un'estensione a 1 cifra mentre attende che la chiamata venga risposta. Esce verso quell'estensione se esiste nel contesto corrente, o verso il contesto definito nella variabile `EXITCONTEXT`, se esiste. |
| `D([called][:calling])` | Invia le stringhe DTMF specificate dopo che la parte chiamata risponde, ma prima che la chiamata sia collegata. La stringa `called` è inviata alla parte chiamata e la stringa `calling` alla parte chiamante. Uno dei due parametri può essere usato da solo. |
| `f` | Forza l'ID chiamante del canale chiamante a essere impostato sull'estensione associata al canale tramite un dial plan `hint`. Utile quando il PSTN non consente un ID chiamante arbitrario. |
| `g` | Prosegue l'esecuzione del dial plan all'estensione corrente se il canale di destinazione riaggancia. |
| `G(context^exten^pri)` | Se la chiamata è risposta, trasferisce la parte chiamante alla priorità specificata e la parte chiamata alla priorità+1. Facoltativamente può essere specificata un'estensione (o estensione e contesto); altrimenti viene usata l'estensione corrente. |
| `h` | Consente alla parte chiamata di riagganciare inviando il digit DTMF `*`. |
| `H` | Consente alla parte chiamante di riagganciare inviando il digit DTMF `*`. |
| `L(x[:y][:z])` | Limita la chiamata a `x` ms, riproduce un avviso quando rimangono `y` ms e ripete l'avviso ogni `z` ms. Vedi le variabili `LIMIT_*` sotto. |
| `m([class])` | Fornisce musica di attesa alla parte chiamante fino a quando il canale richiesto risponde. Può essere specificata una classe MusicOnHold specifica. |
| `r` | Indica la suoneria alla parte chiamante e non passa audio finché il canale chiamato non risponde. |
| `S(x)` | Riaggancia la chiamata `x` secondi dopo che la parte chiamata risponde. |
| `t` | Consente alla parte chiamata di trasferire la parte chiamante inviando la sequenza DTMF definita in `features.conf`. |
| `T` | Consente alla parte chiamante di trasferire la parte chiamata inviando la sequenza DTMF definita in `features.conf`. |
| `w` | Consente alla parte chiamata di abilitare la registrazione con un solo tocco inviando la sequenza DTMF definita in `features.conf`. |
| `W` | Consente alla parte chiamante di abilitare la registrazione con un solo tocco inviando la sequenza DTMF definita in `features.conf`. |
| `k` | Consente alla parte chiamata di parcheggiare la chiamata inviando la sequenza DTMF definita per il parcheggio chiamate in `features.conf`. |
| `K` | Consente alla parte chiamante di parcheggiare la chiamata inviando la sequenza DTMF definita per il parcheggio chiamate in `features.conf`. |

L'opzione `L(x[:y][:z])` può essere configurata con le seguenti variabili speciali:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): riproduce suoni per il chiamante.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: riproduce suoni per la parte chiamata.
- `LIMIT_TIMEOUT_FILE` — file da riprodurre quando il tempo è scaduto.
- `LIMIT_CONNECT_FILE` — file da riprodurre quando la chiamata inizia.
- `LIMIT_WARNING_FILE` — file da riprodurre come avviso quando è definito `y`. Il

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

In the esempio sopra, l'applicazione effettuerà la chiamata sul canale PJSIP corrispondente. Sia il chiamante sia il chiamato potranno trasferire la chiamata (Tt). Verrà riprodotta la musica di attesa al posto del segnale di ritorno. Se nessuno risponde entro 20 secondi, l'estensione passerà alla priorità successiva.

### Hangup()

Riaggancia il canale chiamante [Description] Hangup([causecode]): Questa applicazione riaggancerà il canale chiamante. Se viene fornito un codice di causa, la causa di riaggancio del canale sarà impostata al valore specificato.

### Goto()

Salta a una priorità, estensione o contesto specifici [Description] Goto([[context|]extension|]priority): Questa applicazione farà continuare l'esecuzione del dialplan del canale chiamante alla priorità specificata. Se non viene specificata un'estensione (o estensione e contesto) specifica, questa applicazione salterà alla priorità indicata dell'estensione corrente. Se il tentativo di salto a un'altra posizione nel dialplan non ha successo, il canale continuerà alla priorità successiva dell'estensione corrente.

## Costruire un piano di composizione

Per costruire un semplice piano di composizione, è necessario gestire tutte le chiamate in ingresso e in uscita creando contesti ed estensioni. In questa sezione, mostreremo come creare le estensioni più comuni.

### Composizione tra estensioni

Per abilitare la composizione tra estensioni, possiamo utilizzare la variabile di canale ${EXTEN}, che si riferisce all’estensione composta. Ad esempio, se l’intervallo di estensioni è compreso tra 4000 e 4999 e tutte le estensioni usano SIP, possiamo adottare il seguente comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Dialing to an external destination

Per comporre una destinazione esterna è possibile precedere il numero chiamato con una rotta. In Nord America è comune usare 9 seguito dal numero da comporre esternamente. Se si utilizza un canale analogico o digitale verso il PSTN, il comando dovrebbe apparire come segue: Se si desidera usare il SIP trunk invece del DAHDI, usare il `PJSIP/...@siptrunk` channel.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

La riga sopra consentirà di comporre 9 e il numero desiderato. Nell'esempio fornito, utilizzerai il primo canale DAHDI (DAHDI/1). Se hai diverse linee e questa è occupata, la chiamata non verrà completata. Tuttavia, potresti usare la riga seguente per scegliere automaticamente il primo canale DAHDI disponibile. Facoltativamente, puoi usare il trunk SIP invece di DAHDI. Nel modulo PJSIP `Dial(PJSIP/number@siptrunk,...)`, il numero composto è la parte utente e `siptrunk` è l'endpoint configurato sopra.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

Il parametro “g1” cercherà il primo canale disponibile nel gruppo, consentendo l'uso di tutti i canali. Utilizzando la riga qui sotto, potresti comporre un numero a lunga distanza.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Comporre 9 per ottenere una linea PSTN

Se non hai alcuna restrizione alle chiamate esterne, potresti semplificare e usare il seguente:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Ricevere una chiamata nell'estensione operatore

Nell'esempio seguente, l'estensione operatore è 4000. La linea PSTN è collegata a un'interfaccia FXO. Nel file chan_dahdi.conf, il contesto specificato è from-pstn. Qualsiasi chiamata proveniente dalla PSTN verrà instradata al contesto from-pstn nel dialplan. Questa linea non ha direct inward dialing (DID); pertanto, dovremo ricevere la chiamata tramite l'estensione “s”. Se si riceve dal trunk SIP, utilizzare il contesto [from-sip].

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### Ricevere una chiamata usando il direct inward dialing (DID)

Se disponi di una linea digitale, riceverai l’estensione composta. In questo caso non è necessario inoltrare la chiamata all’operatore; puoi invece inoltrare la chiamata direttamente alla destinazione. Supponi che il tuo intervallo DID vada da 3028550 a 3028599 e che gli ultimi quattro numeri vengano passati nel DID. La configurazione apparirebbe come nell’esempio seguente:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Riproduzione di più estensioni simultaneamente

È possibile configurare Asterisk per chiamare un'estensione e, se non viene risposta, per chiamare simultaneamente diverse altre estensioni, come indicato nel seguente esempio:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

In questo esempio, quando qualcuno chiama l'operatore, il canale DAHDI/1 viene provato inizialmente. Se nessuno risponde dopo 15 secondi (timeout), i canali DAHDI/1, DAHDI/2 e DAHDI/3 squilleranno simultaneamente per altri 15 secondi.

### Routing per Caller ID

In questo esempio, è possibile applicare trattamenti diversi in base al caller ID, il che potrebbe essere utile per gli spammer di chiamate. Per esempio:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In questo esempio, abbiamo aggiunto una regola speciale che, se il caller ID è 4832518888, riproduce un messaggio dal file precedentemente registrato “I-have-moved-to-china”. Le altre chiamate sono accettate come al solito.

### Utilizzare le variabili nel dialplan

Asterisk può utilizzare variabili globali e di canale nel dialplan come argomenti per alcune applicazioni. Guarda i seguenti esempi:

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

Usare le variabili rende più facili le modifiche future. Se cambi la variabile, tutti i riferimenti vengono modificati immediatamente.

### Registrare un annuncio

In alcune delle opzioni discusse più avanti in questa sezione, utilizzeremo prompt registrati. Qui ti mostriamo un modo semplice per registrarli. Useremo l'applicazione Record() per salvare l'annuncio usando il proprio telefono.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Queste istruzioni consentono di registrare qualsiasi messaggio da un softphone. Esempio: comporre recordmenu dal softphone Le istruzioni chiameranno la registrazione con la variabile ${EXTEN:6} senza le prime sei lettere. In altre parole, l'istruzione è equivalente a record(menu:gsm). Tutto quello che devi fare è comporre record + nome_del_file_da_registrare, premere # per terminare la registrazione e attendere di sentire la registrazione.

### Ricevere le chiamate in una receptionist digitale

Ora che abbiamo alcuni esempi semplici, espandiamo la nostra conoscenza delle applicazioni background() e goto(). La chiave per i sistemi interattivi in Asterisk è l'applicazione background(), che consente di eseguire un file audio che, quando il chiamante preme un tasto, viene interrotto per inviare la chiamata all'estensione composta. Sintassi dell'applicazione background():

```
exten=>extension, priority, background(filename)
```

Un'altra applicazione molto utile è goto(). Come suggerisce il nome, salta al contesto, all'estensione e alla priorità indicati. Sintassi dell'applicazione goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formati validi per il comando goto():"

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

Nel seguente esempio, creeremo una reception digitale. È molto semplice modificare il file extensions.conf e configurare le seguenti estensioni:

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

Le estensioni SIP usano `PJSIP/` e le estensioni IAX usano `IAX2/` — entrambi i driver sono inclusi in Asterisk 22, sebbene `chan_iax2` sia ora considerato legacy e si preferisca SIP/PJSIP.

Nel file menu1.gsm, registra il messaggio “premi l’estensione o attendi l’operatore”. Quando l’utente compone il numero 6000, verrà inviato all’estensione 6000. A questo punto, dovresti avere una chiara comprensione dell’uso di diverse applicazioni, tra cui answer(), background(), goto(), hangup() e playback(). Se non hai una chiara comprensione, rileggi questo capitolo finché non ti senti a tuo agio con il contenuto. Userai molto spesso l’applicazione background. Una volta compresi i concetti di base di estensioni, priorità e applicazioni, sarà facile creare un semplice dial plan. Questi concetti saranno approfonditi più avanti nel libro, e vedrai che il dial plan diventerà più potente.

## Sommario

In questo capitolo, hai imparato che i file di configurazione sono memorizzati nella directory /etc/asterisk. Per usare Asterisk, è prima necessario configurare i canali (ad es., pjsip, dahdi, iax). Esistono tre grammatiche diverse per i file di configurazione: gruppo semplice, ereditarietà di oggetti e entità complessa. Il dial plan è creato nel file extensions.conf ed è un insieme di contesti ed estensioni. Nel dial plan, ogni estensione attiva un'applicazione. Hai imparato a usare le applicazioni playback, background, dial, goto, hangup e answer.

## Quiz

1. I file di configurazione del canale sono (scegli tutti quelli che si applicano):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Su Asterisk 22, il singolo peer `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) è sostituito in `pjsip.conf` da quale insieme di oggetti correlati?
   - A. Un `type=peer` e un `type=user`
   - B. Un `type=endpoint`, un `type=auth` e un `type=aor`
   - C. Un singolo `type=friend`
   - D. Un `type=transport` e un `type=global`
3. Definire un contesto nel file di configurazione del canale è importante perché imposta il contesto in ingresso per le chiamate da quel canale — una chiamata dal canale viene elaborata nel contesto corrispondente in `extensions.conf`.
   - A. Vero
   - B. Falso
4. Le principali differenze tra le applicazioni `Playback()` e `Background()` sono (scegli due):
   - A. Playback riproduce un prompt ma non attende i tasti.
   - B. Background riproduce un prompt ma non attende i tasti.
   - C. Background riproduce un messaggio e attende che vengano premuti i tasti.
   - D. Playback riproduce un messaggio e attende che vengano premuti i tasti.
5. Quando una chiamata entra in Asterisk tramite una scheda di interfaccia telefonica (FXO) senza DID, viene gestita nell'estensione speciale:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. I formati validi per l'applicazione `Goto()` sono (scegli tre):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. Il modello `_7[1-5]XX` corrisponde (scegli tutti quelli che si applicano):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. In `Dial(PJSIP/${EXTEN},20,tTm)`, cosa fa l'opzione `m`?
   - A. Limita la chiamata a una durata massima.
   - B. Fornisce musica in attesa al chiamante invece del segnale di chiamata finché il canale non risponde.
   - C. Invia i tasti DTMF dopo che la parte chiamata risponde.
   - D. Forza l'ID chiamante usando un hint del dialplan.
9. Nella grammatica di ereditarietà delle opzioni usata da `chan_dahdi.conf`, tu:
   - A. Definisci l'oggetto in una singola riga.
   - B. Definisci prima le opzioni e dichiari gli oggetti sotto le opzioni definite.
   - C. Definisci un contesto separato per ogni oggetto.
10. Le priorità in un'estensione devono essere numerate consecutivamente (1, 2, 3, …) e non possono usare `n`.
    - A. Vero
    - B. Falso

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
