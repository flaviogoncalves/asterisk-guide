# Costruire il tuo primo PBX con PJSIP

In questo capitolo imparerai come eseguire una configurazione base di un PBX Asterisk. L'obiettivo principale qui è vedere il PBX in funzione per la prima volta, essere in grado di chiamare tra extension, comporre un messaggio in riproduzione e chiamare verso un singolo trunk analogico o SIP. L'idea alla base di questo capitolo è assicurarsi che il tuo Asterisk sia operativo il prima possibile. Dopo aver completato il lavoro in questo capitolo, avrai una base sufficiente per prepararti ai capitoli successivi, dove approfondiremo i dettagli della configurazione.

## Obiettivi

Alla fine di questo capitolo, dovresti essere in grado di:

- Comprendere e modificare i file di configurazione;
- Installare softphone basati su SIP;
- Installare e configurare un trunk SIP;
- Installare e configurare una connessione analogica;
- Chiamare tra extension;
- Chiamare tra telefoni e destinazioni esterne; e
- Configurare un risponditore automatico.

## Comprendere i file di configurazione

Asterisk è controllato da file di configurazione di testo situati in /etc/asterisk. Il formato del file è simile ai file “.ini” di Windows. Il punto e virgola è usato come carattere di commento, i segni “=” e “=>” sono equivalenti e gli spazi vengono ignorati.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk interpreta “=” e “=>” nello stesso modo. Le differenze nella sintassi sono usate per distinguere tra oggetti e variabili. Usa “=” quando vuoi dichiarare una variabile e “=>” per designare un oggetto. La sintassi è la stessa tra tutti i file, ma vengono utilizzati tre tipi di grammatica, come discusso di seguito.

## Grammatiche

| Grammatica | Come viene creato l'oggetto | File di conf. | Esempio |
|---------|---------------------------|------------|---------|
| Simple Group | Tutto nella stessa riga | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Le opzioni sono definite prima, l'oggetto eredita le opzioni | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Ogni entità riceve un context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

Il formato simple group utilizzato in `extensions.conf` e `voicemail.conf` è la grammatica più basilare. Ogni oggetto viene dichiarato con le opzioni sulla stessa riga. Esempio:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

In questo esempio, l'oggetto 1 viene creato con le opzioni op1, op2 e op3, mentre l'oggetto 2 viene creato con le opzioni op1, op2 e op3.

### Grammatica di ereditarietà delle opzioni dell'oggetto

Questo formato è utilizzato dai file chan_dahdi.conf e agents.conf, dove sono disponibili numerose opzioni e la maggior parte delle interfacce e degli oggetti condivide le stesse opzioni. Tipicamente, una o più sezioni contengono dichiarazioni di oggetti e canali. Le opzioni per l'oggetto sono dichiarate sopra l'oggetto e possono essere modificate per un altro oggetto. Sebbene questo concetto sia difficile da comprendere, è molto facile da usare. Esempio:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

Le prime due righe configurano il valore delle opzioni op1 e op2 rispettivamente su “bas” e “adv”. Quando l'oggetto 1 viene istanziato, viene creato usando l'opzione 1 come “bas” e l'opzione 2 come “adv”. Dopo aver definito l'oggetto 1, cambiamo l'opzione 1 in “int”. Successivamente, creiamo l'oggetto 2 con l'opzione 1 come “int” e l'opzione 2 come “adv”.

### Oggetto Complex entity

Questo formato è utilizzato da pjsip.conf, iax.conf e altri file di configurazione in cui esistono numerose entità con molte opzioni. Tipicamente, questo formato non condivide un grande volume di configurazioni comuni. Ogni entità riceve un context. A volte esistono context riservati, come [general] per le configurazioni globali. Le opzioni sono dichiarate nelle dichiarazioni del context. Esempio:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

L'entità [entity1] ha i valori “value1” e “value2” rispettivamente per le opzioni op1 e op2. L'entità [entity2] ha i valori “value3” e “value4” rispettivamente per le opzioni op1 e op2.

## Opzioni per costruire un LAB per Asterisk

Per configurare un PBX, avrai bisogno di un po' di hardware di base. Non è difficile o costoso, ma ci sono alcune opzioni da considerare. Tutto ciò di cui avrai bisogno sono due telefoni e una connessione alla rete pubblica. Alcune opzioni e combinazioni sono possibili durante la creazione del tuo laboratorio, che discuteremo di seguito.

### Opzione 1: LAB completo

Con il LAB completo, è possibile testare tutti gli scenari disponibili e confrontare soluzioni come ATA, telefoni IP e softphone. Puoi anche imparare a conoscere i trunk analogici e SIP. Avrai bisogno di:

- Un adattatore telefonico analogico SIP (ATA)
- Un telefono IP
- Un server dedicato per Asterisk
- Una workstation con un softphone
- Una scheda di interfaccia analogica con almeno due interfacce (1 FXO e 1 FXS)
- Un account presso un provider VoIP

### Opzione 2: LAB economico

Con il LAB economico, semplifichiamo un po' le cose. Usiamo l'ATA, che di solito è meno costoso del telefono IP, e una singola scheda FXO, che è davvero economica. Non saremo in grado di utilizzare telefoni analogici collegati direttamente al server, ma questo non accade comunemente nella pratica. Avrai bisogno di:

- Un adattatore telefonico analogico SIP (ATA)
- Un server dedicato per Asterisk
- Una workstation per il softphone
- Una scheda di interfaccia analogica con 1 FXO
- Un account presso un provider VoIP

### Opzione 3: LAB super economico

Il terzo LAB utilizza un server virtualizzato sul notebook dello studente. Il problema con questo modello sono i conflitti generati dalla porta UDP. A volte sia il server Asterisk che il softphone tentano di accedere alla stessa porta, impedendo ad Asterisk di collegarsi alla porta dell'indirizzo. Un altro problema è la qualità delle chiamate; gli ambienti virtuali non sono indicati per applicazioni in tempo reale come Asterisk. Usa un softphone gratuito per il server e la workstation e una connessione trunk a un provider SIP. Avrai bisogno di:

- Un laptop che esegue un softphone
- Una macchina virtuale (VirtualBox, VMware o simili) per installare Asterisk
- Un account presso un provider VoIP

## Sequenza di installazione

Per aiutarti a comprendere la sequenza di installazione, abbiamo delineato la sequenza di passaggi necessari per installare e configurare Asterisk.

![Layout del laboratorio di riferimento: softphone SIP/IAX, un telefono IP e adattatori analogici come extension (1), il server Asterisk con interfacce ETH0/FXO/FXS (3) e i trunk verso la PSTN tramite un provider VoIP o un collegamento a banda larga (2).](../images/04-first-pbx-fig01.png)

1. Configurazione delle extension a. Extension SIP (ATA, Softphone, Telefono IP) b. Extension IAX c. Extension FXS 2. Configurazione del trunk a. Configurazione di un trunk SIP b. Configurazione di un trunk FXO 3. Costruzione di un dialplan di base a. Chiamate tra extension b. Chiamate verso destinazioni esterne c. Ricezione di una chiamata dall'extension operatore d. Ricezione di una chiamata in un risponditore automatico

## Configurazione delle extension

Le extension sono telefoni SIP, IAX o analogici collegati a una porta FXS. Per configurare un'extension, dovresti modificare il file di configurazione relativo al canale (pjsip.conf, iax.conf, chan_dahdi.conf)

### Extension SIP

Su Asterisk 22, PJSIP (lo stack `res_pjsip`, configurato in `/etc/asterisk/pjsip.conf`) è il driver del canale SIP. Supporta trasporti multipli per endpoint, è attivamente mantenuto ed è l'unico driver SIP fornito con la piattaforma. (Il driver originale `chan_sip` è stato rimosso in Asterisk 21 — vedi il capitolo *Legacy channels* se hai bisogno di migrare una vecchia configurazione.)

L'idea qui è configurare un PBX semplice. (I capitoli successivi forniscono un'intera sessione SIP/PJSIP con tutti i dettagli.) PJSIP è configurato in `/etc/asterisk/pjsip.conf` e contiene tutti i parametri relativi ai telefoni SIP e ai provider VoIP. I client SIP devono essere configurati prima di poter effettuare e ricevere chiamate.

#### Il trasporto

In PJSIP, la configurazione del listener (indirizzo di bind, porta, protocollo) risiede in un oggetto `transport`. Asterisk ha una protezione integrata contro l'indovinare il nome utente — restituisce sempre una sfida di autenticazione identica per utenti sconosciuti e noti, e le richieste non identificate ripetute da un IP sono limitate tramite le opzioni `[global]` `unidentified_request_count`/`unidentified_request_period`. Le opzioni principali di un trasporto sono:

- protocol: Il protocollo di trasporto — `udp`, `tcp`, `tls`, `ws` o `wss`.
- bind: Indirizzo e porta a cui il listener si lega. Se imposti l'indirizzo su `0.0.0.0`, si lega a tutte le interfacce; la porta SIP è predefinita su 5060 per UDP/TCP.

Un trasporto UDP minimale:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

La selezione del codec (`disallow`/`allow`) e il `context` predefinito sono configurati su ogni `endpoint` (mostrato di seguito), non sul trasporto. Le chiamate anonime/guest sono gestite da un `endpoint` chiamato `anonymous`. I timer di registrazione sono controllati per AOR tramite `maximum_expiration`/`default_expiration`.

#### Client SIP

Dopo aver completato la sezione di trasporto, è il momento di configurare i client SIP. Vorrei ricordare ancora una volta al lettore che avremo un intero capitolo su SIP/PJSIP più avanti nel libro. Per ora, concentriamoci sulle basi e lasciamo i dettagli per dopo.

In PJSIP un client SIP è costruito da un insieme di oggetti correlati, legati insieme dal riferimento al nome:

- `endpoint`: Il comportamento della chiamata — codec (`allow`/`disallow`), il dialplan `context` e quali `auth` e `aors` utilizza.
- `auth`: Le credenziali. `username` è l'utente di autenticazione SIP e `password` è il segreto usato per autenticare il dispositivo.
- `aor`: L'"address of record" — dove l'endpoint può essere raggiunto. O un `contact=` statico (per un dispositivo a un IP fisso) o `max_contacts=` per consentire al dispositivo di registrarsi dinamicamente.

Attenzione: Usa password forti, con almeno 8 caratteri, caratteri alfanumerici e numerici e almeno un simbolo. Rapporti di server hackerati sono apparsi nelle mailing list, e i cracker di password a forza bruta per SIP sono facilmente disponibili per gli script kiddies. Le frodi telefoniche costano migliaia di dollari a consumatori e provider.

L'endpoint 6000 è un dispositivo a un IP fisso, quindi il suo AOR trasporta un `contact` statico invece di consentire la registrazione. L'endpoint 6001 è un dispositivo che si registra, quindi il suo AOR gli consente di registrarsi (`max_contacts=1`):

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
auth_type=userpass
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
auth_type=userpass
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP consente alle sezioni `endpoint`, `auth` e `aor` di condividere lo stesso nome di sezione (es. i due blocchi `[6001]` sopra, distinti dal loro `type=`); molti amministratori invece aggiungono un suffisso (`[6001]`, `[6001-auth]`, `[6001]` aor) per leggibilità. Per un dispositivo che si registra, il contatto viene appreso dinamicamente quando il telefono si registra, quindi l'AOR non necessita di alcun `contact` statico.

## Extension IAX

`chan_iax2` è ancora presente in Asterisk 22 ma è ora legacy; SIP/PJSIP è il protocollo preferito per le nuove implementazioni.

Puoi anche creare extension IAX. Questo protocollo è nativo di Asterisk e avremo un'intera sezione dedicata ad esso più avanti in questo libro. Per ora, creiamo alcune extension usando il protocollo. Come prima sezione da configurare, la sezione [general] ha alcuni parametri da configurare. Le opzioni principali sono:

- allow/disallow: Definisce quali codec verranno utilizzati.
- bindaddr: Indirizzo a cui legarsi per il listener SIP di Asterisk. Se lo imposti come 0.0.0.0 (predefinito), si legherà a tutte le interfacce.
- context: Imposta il context predefinito per tutti i client a meno che non venga modificato nella sezione client. Abbiamo usato dummy per motivi di sicurezza. Gli utenti non autenticati entrano in questo context quando l'opzione allowguest è impostata su yes.
- bindport: Porta UDP SIP in ascolto.
- delayreject: Quando impostato su yes, ritarda l'invio di un rifiuto di autenticazione per una REGREQ o AUTHREQ, il che migliora la sicurezza contro gli attacchi di forza bruta alle password.
- bandwidth: Quando impostato su high, consente la selezione di codec a banda larga, come il g711 nelle loro varianti ulaw e alaw.

Il seguente è un esempio della sezione [general] del file iax.conf.

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

### Client IAX

Dopo aver terminato le sezioni generali, è il momento di configurare i client IAX.

- [name]: Quando un dispositivo SIP si connette ad Asterisk, usa la parte del nome utente dell'URI SIP per trovare il peer/user.
- type: Configura la classe di connessione. Le opzioni sono peer, user e friend. o peer: Asterisk invia chiamate a un peer. o user: Asterisk riceve chiamate da un utente. o friend: Entrambe le cose accadono contemporaneamente.
- host: Indirizzo IP o nome host. L'opzione più comune è dynamic, che viene usata quando l'host si registra ad Asterisk.
- secret: Password per autenticare peer e utenti.

Attenzione: Usa password forti con almeno 8 caratteri, caratteri alfanumerici e numerici e almeno un simbolo. Rapporti di server hackerati sono apparsi nelle mailing list, e i cracker di password a forza bruta per gli hash md5 SIP sono disponibili per gli script kiddies. Le frodi telefoniche costano migliaia di dollari a consumatori e provider. Esempio:

```
[guest]
type=user
context=dummy
callerid=”Guest IAX User”
[6003]
context=from-internal
type=friend
secret=#sup3rs3cr3t#
host=dynamic
context=from-internal
[6004]
context=from-internal
type=friend
secret=#s3cr3ts3cr3t#
host=dynamic
context=from-internal
```

## Configurazione dei dispositivi SIP

Dopo aver definito i telefoni nel file di configurazione di Asterisk, è il momento di configurare il telefono stesso. In questo esempio, mostreremo come configurare un softphone gratuito — il SipPulse Softphone (scaricalo da https://www.sippulse.com/produtos/softphone). Controlla il manuale del tuo dispositivo per comprendere i parametri del tuo telefono. Passaggio 1: Configura il telefono per usare l'extension 6000. Esegui il programma di installazione. Dopo l'esecuzione, apri le impostazioni account/SIP e aggiungi un nuovo account SIP. Inserisci le informazioni richieste.

![La schermata dell'account SipPulse Softphone — inserisci il Server (il tuo IP o dominio Asterisk), Nome utente, Password e Nome visualizzato, quindi scegli il Trasporto (UDP, TCP o TLS).](../images/softphone/sipphone-account.png){width=35%}

Nome visualizzato: 6000  Nome utente: 6000  Password: #MySecret1#7  Nome utente autorizzazione: 6000  Dominio: ip_of_your_server. Conferma che il tuo telefono sia registrato usando il comando della console `pjsip show endpoints` (o `pjsip show endpoint 6000` per i dettagli; `pjsip show contacts` mostra i contatti AOR registrati). Ripeti la configurazione per il telefono 6001.

![Un SipPulse Softphone registrato — il punto verde e la riga dell'account (`1001@softphone.sippulse.com.br`) confermano la registrazione; effettua una chiamata dal tastierino o dai pulsanti chiamata/video.](../images/softphone/sipphone-registered.png){width=35%}

## Configurazione dei dispositivi IAX

IAX2 è un protocollo legacy (vedi il capitolo *Legacy channels*) e il SipPulse Softphone è solo SIP, quindi non può registrare un account IAX. Se hai bisogno di testare IAX2, usa un softphone che lo supporti ancora. Crea un nuovo account IAX,

3. Seleziona nuovo account IAX. 4. Inserisci le opzioni relative per il telefono 6003 e facoltativamente per il 6004. 5. Salva la configurazione e controlla se il telefono è registrato usando iax2 show peers. Importante: Usa un account per SIP e un altro per IAX. Se vuoi configurare il sistema per far squillare sia IAX che SIP contemporaneamente, ti mostreremo come farlo nella sezione del dialplan.

### Configurazione di un'interfaccia PSTN

Per connetterti alla PSTN, avrai bisogno di un'interfaccia foreign exchange office (FXO) e di una linea telefonica. Puoi usare anche un'extension PBX esistente. Puoi ottenere una scheda di interfaccia telefonica con un'interfaccia FXO da diversi produttori. In questo esempio, ti mostreremo come installare una scheda di interfaccia DAHDI.

![Porte FXS e FXO: la porta FXS pilota un telefono analogico (fornisce tono di linea e squillo), mentre la porta FXO collega Asterisk alla linea Telco.](../images/04-first-pbx-fig02.png)

### Linee analogiche usando DAHDI

Puoi acquistare una scheda analogica compatibile con DAHDI da diversi produttori. X100P è stata una delle prime schede Digium ed è già stata fuori produzione. Alcuni produttori producono ancora cloni simili. Oltre al prezzo della X100P, abbiamo riscontrato diversi problemi tra queste schede e le nuove schede madri, quindi usala con cautela. X100P, a mio parere, non è una buona scelta per un ambiente di produzione. Qualsiasi scheda compatibile con DAHDI dovrebbe funzionare. Grazie al team di sviluppatori DAHDI, ora abbiamo uno strumento per rilevare e configurare le schede di interfaccia quasi automaticamente. Se hai appena installato i driver DAHDI, non dimenticare di eseguire make config e riavviare la macchina per caricarlo automaticamente. Puoi usare i comandi seguenti per rilevare e configurare la tua scheda. Passaggio 1: Per rilevare il tuo hardware, usa:

```
dahdi_hardware.
```

Passaggio 2: Per configurare usa:

```
dahdi_genconf.
```

Il comando sopra genererà due file /etc/dahdi/system.conf e /etc/asterisk/dahdi-channels.conf. I parametri predefiniti per dahdi_genconf di solito vanno bene, ma puoi modificarli nel file /etc/dahdi/genconf_parameters. Per impostazione predefinita, inserirà le linee (FXO) nel context from-pstn e i telefoni (FXS) nel context from-internal. Passaggio 3: Dopo aver eseguito dahdi_genconf, nell'ultima riga del file /etc/asterisk/chan_dahdi.conf inserisci la seguente riga:

```
#include dahdi-channels.conf
```

Passaggio 4: Modifica il file /etc/dahdi/modules e commenta tutti i driver non utilizzati. Riavvia prima di procedere e controlla se i canali vengono riconosciuti usando:

```
CLI>dahdi show channels
```

### Connessione alla PSTN usando un provider VoIP

Se il tuo budget è davvero limitato, puoi configurare un trunk SIP per connetterti alla PSTN. È certamente il modo più conveniente per connettersi alla PSTN. Esistono migliaia di provider VoIP in tutto il mondo. Per connetterti a uno di essi, avrai bisogno di alcuni parametri. Parametri forniti dal provider SIP.

- username: login
- password: secret
- Dominio del provider: domain
- Porta UDP: 5060
- Codec consentiti: g729, ilbc, alaw

Due parametri dovrebbero essere determinati da te.

- Extension per ricevere chiamate — in questo caso: 9999
- context: from-sip

In PJSIP, un trunk SIP che si registra è costruito dalla stessa famiglia di oggetti usata per un endpoint, più oggetti espliciti `registration` e `identify`. L'oggetto `registration` dice ad Asterisk di registrarsi presso il provider, l'oggetto `identify` abbina il traffico in entrata dall'IP del provider all'endpoint (PJSIP autentica gli INVITE in entrata tramite IP sorgente) e `outbound_auth` fornisce le credenziali per le chiamate in uscita e la registrazione:

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
auth_type=userpass
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

Per accedere a questo trunk, useremo il nome del canale `PJSIP/siptrunk`. L'impostazione `dtmf_mode=rfc4733` trasporta DTMF fuori banda (RFC 4733 sostituisce la vecchia RFC 2833; il payload è identico). L'opzione `identify`/`match` accetta indirizzi IP, CIDR o nomi host, ma i nomi host vengono risolti una volta al momento del caricamento della configurazione, quindi per un provider con IP che cambiano, elenca esplicitamente l'IP/gli IP di segnalazione. Conferma la registrazione con `pjsip show registrations`.

## Introduzione al dialplan

Il dialplan è come il cuore di Asterisk. Definisce come Asterisk gestisce ogni singola chiamata al PBX. Consiste in extension che creano un elenco di istruzioni che Asterisk deve seguire. Le istruzioni vengono attivate da cifre ricevute dal canale o dall'applicazione. Per configurare Asterisk con successo, è fondamentale comprendere il dialplan. La maggior parte del dialplan è contenuta nel file extensions.conf nella directory /etc/asterisk. Questo file usa la grammatica simple group e ha quattro concetti principali:

- Extension
- Priorità
- Applicazioni
- Context

Creiamo un dialplan di base. Nelle sezioni successive di questo libro, dedicherò un capitolo esclusivamente al dialplan. Se hai installato i file di esempio (make samples), il file extensions.conf esiste già. Salvalo con un altro nome e inizia con un file vuoto.

## La struttura del file extensions.conf

Il file extensions.conf è separato in sezioni. La prima è la sezione [general] seguita dalla sezione [globals]. L'inizio di ogni sezione inizia con la definizione del suo nome (es. [default]) e termina quando viene creata un'altra sezione.

### La sezione [general]

La sezione general si trova nella parte superiore del file. Prima di iniziare a configurare il dialplan, è utile conoscere le opzioni generali che controllano determinati comportamenti del dialplan. Queste opzioni sono:

- static e write protect: Se static=yes e writeprotect=no, puoi usare la CLI

```
command save dialplan.
```

Attenzione: Se emetti un comando save dialplan dalla CLI, finirai per perdere eventuali note e commenti nel file.

- autofallthrough: Se autofallthrough è impostato, allora se un'extension esaurisce le cose da fare, terminerà la chiamata con BUSY, CONGESTION o HANGUP a seconda della migliore stima di Asterisk. Questa è l'impostazione predefinita. Se autofallthrough non è impostato, allora se un'extension esaurisce le cose da fare, Asterisk attenderà che venga composta una nuova extension.
- clearglobalvars: Se clearglobalvars è impostato, le variabili globali verranno cancellate e rianalizzate in un dialplan reload o Asterisk reload. Se clearglobalvars non è impostato, le variabili globali persisteranno attraverso i ricaricamenti e — anche se eliminate da extensions.conf o da uno dei suoi file inclusi — rimarranno impostate sul valore precedente.
- extenpatternmatchnew: Usa un algoritmo di pattern-matching più veloce, che aiuta notevolmente quando hai un gran numero di extension. Predefinito su no.
- userscontext: Questo è il context dove vengono registrate le voci da users.conf.

### La sezione [globals]

Nella sezione [globals] definirai le variabili globali e i loro valori iniziali. Puoi accedere alla variabile nel dialplan usando ${GLOBAL(variable)}. Puoi persino accedere alle variabili definite nell'ambiente linux/unix usando ${ENV(variable)}. Le variabili globali non sono sensibili alle maiuscole/minuscole. Alcuni esempi potrebbero essere:

```
INCOMING>DAHDI/8&DAHDI/9
RINGTIME=>3
```

Nell'esempio seguente, puoi impostare e testare una variabile globale nel dialplan.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Context

Il context è la partizione denominata del dialplan. Dopo le sezioni [general] e [globals], il dialplan è un insieme di context in cui ogni context ha diverse extension, ogni extension ha diverse priorità e ogni priorità chiama un'applicazione con diversi argomenti.

![Flusso di chiamata Asterisk: ogni chiamata arriva su un canale (IAX, SIP e altri) come una tratta di chiamata in entrata; il context del canale — impostato globalmente o per canale nel file di configurazione del canale — decide quale context in extensions.conf elabora la chiamata prima che lasci la tratta in uscita.](../images/04-first-pbx-fig03.png)

![Elaborazione della chiamata: il `context=` definito per un canale (in chan_dahdi.conf o pjsip.conf) nomina il context corrispondente in extensions.conf dove il dialplan gestisce la chiamata.](../images/04-first-pbx-fig04.png)

Puoi costruire un semplice dialplan per raggiungere altri telefoni e la PSTN. Tuttavia, Asterisk è molto più potente di così. Il nostro obiettivo è insegnarti maggiori dettagli su ciò che è possibile fare nel dialplan.

## Extension

A differenza del PBX tradizionale, dove le extension sono associate a telefoni, interfacce, menu e così via, in Asterisk un'extension è un elenco di comandi da elaborare quando viene attivato un numero o un nome di extension specifico. I comandi vengono elaborati in ordine di priorità.

![Sintassi dell'extension: `exten => number(name),{priority|label}[(alias)],application`. Le extension possono essere numeriche, alfanumeriche, numeriche con ID chiamante, un pattern o un'extension standard come `s`; le priorità possono essere un numero, `n` (successivo), `s` (stesso), un offset o un `hint`.](../images/04-first-pbx-fig05.png)

Un'extension può essere letterale, standard o speciale. Un'extension standard include solo numeri o nomi e i caratteri * e #; 12#89* è un'extension letterale valida. I nomi possono essere usati anche per la corrispondenza delle extension. Le extension sono sensibili alle maiuscole/minuscole. Tuttavia, non puoi creare due extension con lo stesso nome ma maiuscole/minuscole diverse. Quando viene composta un'extension, viene eseguito il comando con la prima priorità, seguito dal comando con priorità 2 e così via. Questo accade finché la chiamata non viene disconnessa o qualche comando restituisce il numero uno, indicando un errore. Cosa fa Asterisk quando viene eseguita l'ultima priorità è regolato dal parametro autofallthrough. Vedi la sezione [general] in questo capitolo. Esempio:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

Sopra trovi l'elenco delle istruzioni da elaborare quando viene composta l'extension 123. La prima priorità è rispondere al canale (necessario quando il canale è nello stato di squillo: es. canali FXO). La seconda priorità è riprodurre un file audio chiamato tt-weasels. La terza priorità riaggancia il canale. Un'altra opzione è gestire la chiamata in base all'ID chiamante. Puoi usare il carattere / per specificare l'ID chiamante da elaborare. Esempi:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

Questo esempio attiverà l'extension 123 ed eseguirà le seguenti opzioni solo se l'ID chiamante è 100. Questo può essere fatto anche usando il pattern descritto di seguito:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: mappa un'extension a un canale. Viene usato per monitorare lo stato del canale. Viene usato insieme alla presenza. Il telefono deve supportarlo.

#### Pattern

Puoi usare pattern e letterali nel dialplan. I pattern sono molto utili per ridurre le dimensioni del dialplan. Tutti i pattern iniziano con il carattere “_”. I seguenti caratteri possono essere usati per definire un pattern. La figura identifica i pattern disponibili per l'uso con Asterisk.

![Caratteri di corrispondenza dei pattern: `_` avvia un pattern, `.` corrisponde a uno o più caratteri, `!` corrisponde a zero o più, `[123-7]` corrisponde a qualsiasi cifra o intervallo elencato, `X` è 0-9, `Z` è 1-9 e `N` è 2-9 — con esempi che mappano intervalli di extension d'ufficio.](../images/04-first-pbx-fig06.png)

### Extension speciali

Asterisk usa alcuni nomi di extension come extension standard.

![Extension speciali di Asterisk: `i` (non valido), `s` (avvio), `h` (riaggancio), `t` (timeout), `T` (timeout assoluto), `o` (operatore), `a` (premuto `*` nella segreteria telefonica), `fax` (rilevamento fax) e `Talk` (usato con BackgroundDetect).](../images/04-first-pbx-fig07.png)

Descrizione: s: Avvio. Viene usato per gestire una chiamata quando non c'è un numero composto. È utile per i trunk FXO e l'elaborazione dei menu. t: Timeout. Viene usato quando le chiamate rimangono inattive dopo che è stato riprodotto un prompt. Viene anche usato per riagganciare una linea inattiva. T: AbsoluteTimeout. Se stabilisci un limite di chiamata usando la funzione dialplan `TIMEOUT(absolute)`, una volta che la chiamata supera il limite definito, verrà inviata all'extension T. h: Riaggancio. Viene chiamato dopo che l'utente disconnette la chiamata. i: Non valido. Viene attivato quando chiami un'extension inesistente nel context. L'uso di queste extension può influenzare il contenuto dei record CDR — specificamente, il dst che non contiene il numero composto. o: Operatore. Viene usato per andare all'operatore quando l'utente preme “0” durante la segreteria telefonica. L'uso di queste extension può modificare il contenuto dei record di fatturazione (CDR) — in particolare, il campo dst non avrà il numero composto. Per aggirare questo problema, dovresti usare l'opzione g nell'applicazione dial() e considerare le funzioni resetcdr(w) e/o nocdr()

## Variabili

Nel PBX Asterisk, le variabili possono essere globali, specifiche del canale e specifiche dell'ambiente. Puoi usare l'applicazione NoOP() per vedere il contenuto di una variabile nella console. Può usare una variabile globale o una variabile specifica del canale come argomenti dell'applicazione. Una variabile può essere referenziata come nell'esempio seguente, dove varname è il nome della variabile.

```
${varname}
```

Un nome di variabile può essere una stringa alfanumerica che inizia con una lettera. I nomi delle variabili globali non sono sensibili alle maiuscole/minuscole. Tuttavia, le variabili di sistema (definite da Asterisk sono definite dal canale) sono sensibili alle maiuscole/minuscole. Pertanto, la variabile ${EXTEN} è diversa da ${exten}.

### Variabili globali

Le variabili globali possono essere configurate nella sezione [global] nel file extensions.conf o usando l'applicazione:

```
set(Global(variable)=content)
```

### Variabili specifiche del canale

Le variabili specifiche del canale sono configurate usando l'applicazione set(). Ogni canale riceve il proprio spazio di variabili. Non c'è possibilità di collisioni tra variabili di canali diversi. Una variabile specifica del canale viene distrutta quando il canale riaggancia. Alcune delle variabili più comunemente usate sono:

- ${EXTEN} Extension composta
- ${CONTEXT} Context corrente
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} ID chiamante corrente
- ${PRIORITY} Priorità corrente

Altre variabili specifiche del canale sono tutte in maiuscolo. Puoi vedere il contenuto di diverse variabili usando l'applicazione dumpchan(). Di seguito è riportato un semplice estratto delle variabili dump-channel.

```
exten=9001,1,dumnpchan()
exten=9001,n,echo()
exten=9001,n,hangup()
```

Output di Dumpchan:

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

Il layout del campo sopra è l'output `DumpChan` di Asterisk 22 (un vero nome di canale `PJSIP/...`, i campi `CallerIDNum`/`ConnectedLineID` e le righe `Raw*`/`Transcode`/`BridgeID` che i canali PJSIP popolano). A differenza del vecchio driver, un canale PJSIP non imposta automaticamente le variabili di canale `SIPCALLID`/`SIPUSERAGENT`; i dettagli SIP equivalenti vengono letti su richiesta con le funzioni dialplan `PJSIP_HEADER()` e `CHANNEL()` — ad esempio `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}` e `${CHANNEL(rtp,dest)}` per l'indirizzo RTP remoto.

### Variabili specifiche dell'ambiente

Le variabili specifiche dell'ambiente possono essere usate per accedere alle variabili definite nel sistema operativo. Puoi impostare variabili specifiche dell'ambiente usando la funzione ENV(). Ad esempio:

```
${ENV(LANG)}
Set(ENV(LANG))=en_US
```

### Variabili specifiche dell'applicazione

Alcune applicazioni usano variabili per l'input e l'output dei dati. Puoi impostare variabili prima di chiamare l'applicazione o recuperare la variabile dopo l'esecuzione dell'applicazione. Ad esempio: L'applicazione Dial restituisce le seguenti variabili:

- ${DIALEDTIME} -> Questo è il tempo dalla composizione di un canale fino alla sua disconnessione.
- ${ANSWEREDTIME} -> Questa è la quantità di tempo per la chiamata effettiva.
- ${DIALSTATUS} Questo è lo stato della chiamata: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> Messaggio di errore per la chiamata.

## Espressioni

Le espressioni possono essere molto utili nel dialplan. Vengono usate per manipolare stringhe ed eseguire operazioni matematiche e logiche.

![Panoramica delle espressioni Asterisk — `$[expression1 operator expression2]` — raggruppamento degli operatori matematici, logici, di confronto, di espressione regolare e condizionali disponibili nel dialplan.](../images/04-first-pbx-fig08.png)

La sintassi dell'espressione è definita come segue:

```
$[expression1 operator expression2]
```

Supponiamo di avere una variabile chiamata “I” e vogliamo aggiungere 100 alla variabile:

```
$[${I}+100]
```

Quando Asterisk trova un'espressione nel dialplan, cambia l'intera espressione con il valore risultante.

### Operatori

I seguenti operatori possono essere usati per costruire espressioni. È importante osservare la precedenza degli operatori. 1. Parentesi “()” 2. Operatori unari “! -“ 3. Espressione regolare “: =~ 4. Operatori moltiplicativi “* / %” 5. Operatori additivi “+ -“ 6. Operatori di confronto 7. Operatori logici 8. Operatori condizionali

#### Operatori matematici

- Addizione (+)
- Sottrazione (-)
- Moltiplicazione (*)
- Divisione (/)
- Modulo (%)

#### Operatori logici

- Logico “AND” (&)
- Logico “OR” (|)
- Complemento unario logico (!)

#### Operatori di espressione regolare

- Corrispondenza di espressione regolare (:)
- Corrispondenza esatta di espressione regolare (=~)

Un'espressione regolare è una stringa di testo speciale usata per descrivere un pattern di ricerca. Puoi pensare alle espressioni regolari come caratteri jolly. Le espressioni regolari vengono usate per abbinare una stringa a un pattern per verificare la corrispondenza. Se la corrispondenza ha successo e l'espressione regolare contiene almeno una corrispondenza, viene restituita la prima corrispondenza; altrimenti, il risultato è il numero di caratteri abbinati.

#### Operatori di confronto

Il risultato di un confronto è 1 se la relazione è vera o 0 se è falsa.

- = uguale
- != non uguale
- < minore di
- > maggiore di
- <= minore o uguale a
- >= maggiore o uguale a

### LAB. Valuta le seguenti espressioni:

Inserisci queste espressioni nel tuo dialplan e usa l'applicazione NoOP() per valutare le espressioni. Componi 9002 ed esamina i risultati nella console Asterisk. Usa verbose 15 per mostrare i risultati.

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

## Funzioni

Alcune applicazioni sono state sostituite da funzioni, che consentono l'elaborazione delle variabili in un modo più avanzato rispetto alle sole espressioni. Puoi vedere l'elenco completo delle funzioni emettendo il seguente comando di console:

```
CLI>core show functions
```

Lunghezza stringa: ${LEN(string)} restituisce la lunghezza della stringa

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

Nella prima operazione, il sistema mostra 5 come risultato (il numero di lettere nella parola “fruit”). La seconda restituisce il numero 4 (il numero di lettere nella parola “pear”). Sottostringhe: Restituisce la sottostringa, a partire dalla posizione definita dal parametro “offset”, con la lunghezza della stringa definita nel parametro “length”. Se l'offset è negativo, inizia da destra a sinistra, iniziando alla fine della stringa. Se la lunghezza è omessa o negativa, prende l'intera stringa a partire dall'offset.

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

Esempio #2: Prendi il prefisso dalle prime tre cifre.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Esempio #3: Prende tutte le cifre dalla variabile ${EXTEN}, eccetto il prefisso.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### Concatenazione di stringhe

Per concatenare due stringhe, scrivile semplicemente insieme.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Applicazioni

Per costruire un dialplan, dobbiamo comprendere il concetto di applicazioni. Userai le applicazioni per gestire il canale nel dialplan. Le applicazioni sono implementate in diversi moduli. Le applicazioni disponibili dipendono dai moduli. Puoi mostrare tutte le applicazioni Asterisk usando il comando di console:

```
CLI>core show applications
```

In alternativa, puoi mostrare i dettagli di un'applicazione specifica usando l'esempio seguente:

```
CLI>core show application dial
```

Per costruire un semplice dialplan, devi conoscere alcune applicazioni. Discuteremo esempi più avanzati più avanti nel libro.

![La manciata di applicazioni necessarie per costruire un semplice dialplan: Answer (rispondi a un canale), Dial (chiama un altro canale), Hangup (riaggancia un canale), Playback (riproduci un file audio) e Goto (salta a una priorità, extension o context).](../images/04-first-pbx-fig09.png)

Useremo queste applicazioni (sopra) per creare un semplice dialplan per due PBX di base.

### Answer()

[Sinossi] Risponde a un canale se sta squillando [Descrizione] Answer([delay]): Se la chiamata non ha ricevuto risposta, l'applicazione risponderà. Altrimenti, non ha alcun effetto sulla chiamata. Se viene specificato un ritardo, Asterisk attenderà il numero di millisecondi specificato in ‘delay’ prima di rispondere alla chiamata.

### Dial()

La seguente descrizione può essere ottenuta emettendo show application dial nel dialplan. Per una facile ricerca, è riprodotta di seguito. La sintassi per l'applicazione Dial è mostrata anche di seguito:

```
;dial to a single channel
Dial(type/identifier,timeout,options, URL)
;Dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...][|timeout][|options][|URL]):
```

Questa applicazione effettuerà chiamate verso uno o più canali specificati. Non appena uno dei canali richiesti risponde, il canale di origine riceverà risposta — se non ha già ricevuto risposta. Questi due canali saranno quindi attivi in una chiamata in bridge. Tutti gli altri canali richiesti verranno quindi riagganciati. A meno che non venga specificato un timeout, l'applicazione Dial attenderà indefinitamente finché uno dei canali chiamati non risponde, l'utente riaggancia o tutti i canali chiamati sono occupati o non disponibili. L'esecuzione del dialplan continuerà se nessun canale richiesto può essere chiamato o se il timeout scade. Questa applicazione imposta le seguenti variabili di canale al completamento:

- DIALEDTIME - Questo è il tempo dalla composizione di un canale fino al momento in cui viene disconnesso.
- ANSWEREDTIME - Questa è la quantità di tempo per una chiamata effettiva.
- DIALSTATUS - Questo è lo stato della chiamata: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

Per le modalità Privacy e Screening, la variabile DIALSTATUS verrà impostata su DONTCALL se la parte chiamata sceglie di inviare la parte chiamante allo script 'Go Away'. La variabile DIALSTATUS verrà impostata su TORTURE se la parte chiamata vuole inviare il chiamante allo script 'torture'. Questa applicazione segnalerà la terminazione normale se il canale di origine riaggancia o se la chiamata è in bridge e una delle parti nel bridge termina la chiamata. L'URL facoltativo verrà inviato alla parte chiamata se il canale lo supporta. Se la variabile OUTBOUND_GROUP è impostata, tutti i canali peer creati da questa applicazione saranno inclusi in quel gruppo (come in

```
Set(GROUP()=...).
```

La seguente tabella riassume alcune delle opzioni più frequentemente utilizzate per l'applicazione Dial. Per l'elenco completo, usa il comando di console `core show application Dial`. In Asterisk 22 queste opzioni sono separate dal canale e dal timeout da virgole — ad esempio `Dial(PJSIP/2000,20,tTm)`.

| Opzione | Descrizione |
|--------|-------------|
| `A(x)` | Riproduce un annuncio alla parte chiamata, usando `x` come file. |
| `C` | Reimposta il CDR per questa chiamata. |
| `d` | Consente all'utente chiamante di comporre un'extension a 1 cifra mentre attende che la chiamata riceva risposta. Esce su quell'extension se esiste nel context corrente, o sul context definito nella variabile `EXITCONTEXT`, se esiste. |
| `D([called][:calling])` | Invia le stringhe DTMF specificate dopo che la parte chiamata risponde, ma prima che la chiamata venga messa in bridge. La stringa `called` viene inviata alla parte chiamata e la stringa `calling` alla parte chiamante. Entrambi i parametri possono essere usati da soli. |
| `f` | Forza l'ID chiamante del canale chiamante a essere impostato sull'extension associata al canale tramite un `hint` del dialplan. Utile dove la PSTN non consente un ID chiamante arbitrario. |
| `g` | Procede con l'esecuzione del dialplan all'extension corrente se il canale di destinazione riaggancia. |
| `G(context^exten^pri)` | Se la chiamata riceve risposta, trasferisce la parte chiamante alla priorità specificata e la parte chiamata alla priorità+1. Facoltativamente può essere specificata un'extension (o extension e context); altrimenti viene usata l'extension corrente. |
| `h` | Consente alla parte chiamata di riagganciare inviando la cifra DTMF `*`. |
| `H` | Consente alla parte chiamante di riagganciare inviando la cifra DTMF `*`. |
| `L(x[:y][:z])` | Limita la chiamata a `x` ms, riproduce un avviso quando rimangono `y` ms e ripete l'avviso ogni `z` ms. Vedi le variabili `LIMIT_*` di seguito. |
| `m([class])` | Fornisce musica in attesa alla parte chiamante finché il canale richiesto non risponde. Può essere specificata una classe MusicOnHold specifica. |
| `r` | Indica lo squillo alla parte chiamante e non passa alcun audio finché il canale chiamato non risponde. |
| `S(x)` | Riaggancia la chiamata `x` secondi dopo che la parte chiamata risponde. |
| `t` | Consente alla parte chiamata di trasferire la parte chiamante inviando la sequenza DTMF definita in `features.conf`. |
| `T` | Consente alla parte chiamante di trasferire la parte chiamata inviando la sequenza DTMF definita in `features.conf`. |
| `w` | Consente alla parte chiamata di abilitare la registrazione one-touch inviando la sequenza DTMF definita in `features.conf`. |
| `W` | Consente alla parte chiamante di abilitare la registrazione one-touch inviando la sequenza DTMF definita in `features.conf`. |
| `k` | Consente alla parte chiamata di parcheggiare la chiamata inviando la sequenza DTMF definita per il parcheggio di chiamata in `features.conf`. |
| `K` | Consente alla parte chiamante di parcheggiare la chiamata inviando la sequenza DTMF definita per il parcheggio di chiamata in `features.conf`. |

L'opzione `L(x[:y][:z])` può essere regolata con le seguenti variabili speciali:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (predefinito `yes`): riproduce suoni per il chiamante.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: riproduce suoni per la parte chiamata.
- `LIMIT_TIMEOUT_FILE` — file da riprodurre quando il tempo è scaduto.
- `LIMIT_CONNECT_FILE` — file da riprodurre quando inizia la chiamata.
- `LIMIT_WARNING_FILE` — file da riprodurre come avviso quando `y` è definito. Il valore predefinito è dire il tempo rimanente.

Esempio:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

Nell'esempio sopra, l'applicazione chiamerà il canale PJSIP corrispondente. Sia il chiamante che il chiamato potrebbero trasferire la chiamata (Tt). Si sentirà musica in attesa invece dello squillo. Se nessuno risponde entro 20 secondi, l'extension passerà alla priorità successiva.

### Hangup()

Riaggancia il canale chiamante [Descrizione] Hangup([causecode]): Questa applicazione riaggancerà il canale chiamante. Se viene fornito un codice di causa, la causa di riaggancio del canale verrà impostata sul valore fornito.

### Goto()

Salta a una particolare priorità, extension o context [Descrizione] Goto([[context|]extension|]priority): Questa applicazione farà sì che il canale chiamante continui l'esecuzione del dialplan alla priorità specificata. Se non vengono specificate un'extension specifica (o extension e context), questa applicazione salterà alla priorità specificata dell'extension corrente. Se il tentativo di saltare in un'altra posizione nel dialplan non ha successo, il canale continuerà alla priorità successiva dell'extension corrente.

## Costruire un dialplan

Per costruire un semplice dialplan, devi trattare tutte le chiamate in entrata e in uscita creando context ed extension. In questa sezione, ti mostreremo come costruire le extension più comuni.

### Chiamate tra extension

Per abilitare le chiamate tra extension, potremmo usare la variabile di canale ${EXTEN}, che si riferisce all'extension composta. Ad esempio, se l'intervallo di extension è compreso tra 4000 e 4999 e tutte le extension usano SIP, potremmo adottare il seguente comando:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Chiamate verso una destinazione esterna

Per comporre una destinazione esterna potresti far precedere il numero composto da una rotta. In Nord America, è comune usare 9 seguito dal numero da comporre esternamente. Se stai usando un canale analogico o digitale verso la PSTN, il comando dovrebbe apparire come segue: Se vuoi usare il trunk SIP invece del DAHDI, usa il canale `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

La riga sopra ti permetterà di comporre 9 e il numero desiderato. Nell'esempio fornito, userai il primo canale DAHDI (DAHDI/1). Se hai diverse linee e questa è occupata, la chiamata non verrà completata. Tuttavia, potresti usare la seguente riga per scegliere automaticamente il primo canale DAHDI disponibile. Facoltativamente, puoi usare il trunk SIP invece di DAHDI. Nel formato PJSIP `Dial(PJSIP/number@siptrunk,...)`, il numero composto è la parte utente e `siptrunk` è l'endpoint configurato sopra.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

Il parametro “g1” cercherà il primo canale disponibile nel gruppo, consentendo l'uso di tutti i canali. Usando la riga sotto, potresti comporre un numero interurbano.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Comporre 9 per ottenere una linea PSTN

Se non hai restrizioni alla composizione esterna, potresti semplificare e usare quanto segue:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### Ricezione di una chiamata nell'extension operatore

Nell'esempio seguente, l'extension operatore è 4000. La linea PSTN è collegata a un'interfaccia FXO. Nel file chan_dahdi.conf, il context specificato è from-pstn. Qualsiasi chiamata proveniente dalla PSTN verrà instradata al context from-pstn nel dialplan. Questa linea non ha la selezione passante (DID); come tale, dovremo ricevere la chiamata tramite l'extension “s”. Se ricevi dal trunk SIP, usa il context [from-sip].

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

### Ricezione di una chiamata usando la selezione passante (DID)

Se hai una linea digitale, riceverai l'extension composta. Quando questo è il caso, non hai bisogno di inoltrare la chiamata all'operatore; piuttosto, puoi inoltrare la chiamata direttamente alla destinazione. Supponiamo che il tuo intervallo DID vada da 3028550 a 3028599 e che le ultime quattro cifre vengano passate nel DID. La configurazione apparirebbe come nell'esempio seguente:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### Riproduzione di diverse extension simultaneamente

Puoi impostare Asterisk per chiamare un'extension e, se non riceve risposta, per chiamare diverse altre extension simultaneamente, come indicato nell'esempio seguente:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

In questo esempio, quando qualcuno chiama l'operatore, viene inizialmente tentato il canale DAHDI/1. Se nessuno risponde dopo 15 secondi (timeout), i canali DAHDI/1, DAHDI/2 e DAHDI/3 squilleranno simultaneamente per altri 15 secondi.

### Instradamento per ID chiamante

In questo esempio, potresti dare trattamenti diversi in base all'ID chiamante, il che potrebbe essere utile per gli spammer di chiamate. Ad esempio:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In questo esempio, abbiamo aggiunto una regola speciale che, se l'ID chiamante è 4832518888, riproduci un messaggio dal file precedentemente registrato “I-have-moved-to-china”. Altre chiamate vengono accettate come al solito.

### Uso di variabili nel dialplan

Asterisk può usare variabili globali e di canale nel dialplan come argomenti per determinate applicazioni. Guarda i seguenti esempi:

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

L'uso di variabili rende più facili i cambiamenti futuri. Se cambi la variabile, tutti i riferimenti vengono cambiati immediatamente.

### Registrazione di un annuncio

In alcune delle opzioni discusse più avanti in questa sezione, useremo prompt registrati. Qui ti mostriamo un modo semplice per registrarli. Useremo l'applicazione Record() per salvare l'annuncio usando il proprio telefono.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

Queste istruzioni ti consentono di registrare qualsiasi messaggio da un softphone. Esempio: comporre recordmenu dal softphone Le istruzioni chiameranno la registrazione con la variabile ${EXTEN:6} senza le prime sei lettere. In altre parole, l'istruzione è equivalente a record(menu:gsm). Tutto quello che devi fare è comporre record + nome_del_file_da_registrare, premere # per terminare la registrazione e attendere di ascoltare la registrazione.

### Ricezione delle chiamate in un centralino digitale

Ora che abbiamo alcuni semplici esempi, espandiamo il nostro apprendimento sulle applicazioni background() e goto(). La chiave per i sistemi interattivi in Asterisk è l'applicazione background(), che ti consente di eseguire un file audio che, quando il chiamante preme un tasto, viene interrotto per inviare la chiamata all'extension composta. Sintassi dell'applicazione background():

```
exten=>extension, priority, background(filename)
```

Un'altra applicazione molto utile è goto(). Come suggerisce il nome, salta al context, all'extension e alla priorità indicati. Sintassi dell'applicazione goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

Formati validi per il comando goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

Nell'esempio seguente, creeremo un centralino digitale. È molto semplice modificare il file extensions.conf e configurare le seguenti extension:

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

Le extension SIP usano `PJSIP/` e le extension IAX usano `IAX2/` — entrambi i driver sono forniti in Asterisk 22, sebbene `chan_iax2` sia ora considerato legacy e SIP/PJSIP sia preferito.

Nel file menu1.gsm, registra il messaggio “premi l'extension o attendi l'operatore”. Quando l'utente compone il numero 6000, verrà inviato all'extension 6000. A questo punto, dovresti avere una chiara comprensione dell'uso di diverse applicazioni, tra cui answer(), background(), goto(), hangup() e playback(). Se non hai una chiara comprensione, leggi di nuovo questo capitolo finché non ti senti a tuo agio con il contenuto. Userai l'applicazione background molto spesso. Una volta comprese le basi di extension, priorità e applicazioni, sarà facile creare un semplice dialplan. Questi concetti saranno esplorati più approfonditamente più avanti nel libro e vedrai che il dialplan diventerà più potente.

## Riepilogo

In questo capitolo, hai imparato che i file di configurazione sono memorizzati nella directory /etc/asterisk. Per usare Asterisk, è prima necessario configurare i canali (es. pjsip, dahdi, iax). Esistono tre diverse grammatiche per i file di configurazione: simple group, object inheritance e complex entity. Il dialplan viene creato nel file extensions.conf ed è un insieme di context ed extension. Nel dialplan, ogni extension attiva un'applicazione. Hai imparato a usare le applicazioni playback, background, dial, goto, hangup e answer.

## Quiz

1. I file di configurazione del canale sono (scegli tutto ciò che si applica):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Su Asterisk 22, il singolo peer `chan_sip` `[6001]` (`type=friend`/`host=dynamic`) viene sostituito in `pjsip.conf` da quale insieme di oggetti correlati?
   - A. Un `type=peer` e un `type=user`
   - B. Un `type=endpoint`, un `type=auth` e un `type=aor`
   - C. Un singolo `type=friend`
   - D. Un `type=transport` e un `type=global`
3. Definire un context nel file di configurazione del canale è importante perché imposta il context in entrata per le chiamate da quel canale — una chiamata dal canale viene elaborata nel context corrispondente in `extensions.conf`.
   - A. Vero
   - B. Falso
4. Le differenze principali tra le applicazioni `Playback()` e `Background()` sono (scegli due):
   - A. Playback riproduce un prompt ma non attende cifre.
   - B. Background riproduce un prompt ma non attende cifre.
   - C. Background riproduce un messaggio e attende che vengano premute cifre.
   - D. Playback riproduce un messaggio e attende che vengano premute cifre.
5. Quando una chiamata entra in Asterisk tramite una scheda di interfaccia telefonica (FXO) senza DID, viene gestita nell'extension speciale:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. I formati validi per l'applicazione `Goto()` sono (scegli tre):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. Il pattern `_7[1-5]XX` corrisponde a (scegli tutto ciò che si applica):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. In `Dial(PJSIP/${EXTEN},20,tTm)`, cosa fa l'opzione `m`?
   - A. Limita la chiamata a una durata massima.
   - B. Fornisce musica in attesa al chiamante invece dello squillo finché il canale non risponde.
   - C. Invia cifre DTMF dopo che la parte chiamata risponde.
   - D. Forza l'ID chiamante usando un hint del dialplan.
9. Nella grammatica di ereditarietà delle opzioni usata da `chan_dahdi.conf`, tu:
   - A. Definisci l'oggetto in una singola riga.
   - B. Definisci le opzioni prima e dichiari gli oggetti sotto le opzioni definite.
   - C. Definisci un context separato per ogni oggetto.
10. Le priorità in un'extension devono essere numerate consecutivamente (1, 2, 3, …) e non possono usare `n`.
    - A. Vero
    - B. Falso

**Risposte:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
