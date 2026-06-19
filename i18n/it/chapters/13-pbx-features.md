# Utilizzo delle funzionalità del PBX

Nei sistemi SIP, la maggior parte delle funzionalità telefoniche è implementata nell'endpoint. Esiste una grande varietà di telefoni SIP e produttori, e l'interoperabilità non è garantita. Il team di sviluppo di Asterisk ha svolto un lavoro straordinario implementando la maggior parte delle funzionalità direttamente nel PBX, rendendo Asterisk quasi indipendente dall'endpoint. Tuttavia, a volte troverai la stessa funzione eseguita sia dal telefono che da Asterisk stesso. L'integrazione tra telefono e PBX è la prossima frontiera dell'usabilità, su cui si stanno concentrando attualmente i sistemi proprietari. In questo capitolo, imparerai come utilizzare la maggior parte di queste funzionalità.

## Obiettivi

Al termine di questo capitolo, sarai in grado di comprendere e utilizzare:

- Parcheggio di chiamata (Call Parking)
- Risposta di chiamata (Call Pickup)
- Trasferimento di chiamata (Call Transfer)
- Conferenza (ConfBridge)
- Registrazione di chiamata (Call Recording)
- Musica d'attesa (Music on hold)

## Dove sono implementate le funzionalità

Innanzitutto, è importante capire quando le funzionalità del PBX vengono eseguite dal PBX stesso e quando invece è il telefono a svolgere tutto il lavoro. Ad esempio, puoi trasferire una chiamata utilizzando il tasto TRANSFER sul telefono oppure componendo # (trasferimento incondizionato eseguito dal PBX stesso).

## Funzionalità implementate da Asterisk

Queste funzionalità sono implementate nel PBX dal codice di Asterisk:

- Musica d'attesa
- Parcheggio di chiamata
- Risposta di chiamata
- Registrazione di chiamata
- Sala conferenze ConfBridge
- Trasferimento di chiamata (cieco e assistito)

## Funzionalità solitamente implementate dal dial plan

Queste funzionalità devono essere programmate nel dial plan di Asterisk (extensions.conf):

- Trasferimento su occupato
- Trasferimento immediato
- Trasferimento su mancata risposta
- Filtraggio chiamate (blacklist)
- Non disturbare (Do not disturb)
- Ripetizione chiamata (Redial)

## Funzionalità solitamente implementate dal telefono

Queste funzionalità sono implementate dal firmware del telefono:

![Dove sono solitamente implementate le funzionalità del PBX: in Asterisk stesso, nel dial plan o nel telefono](../images/13-pbx-features-fig01.png)

- Messa in attesa (Call on hold)
- Trasferimento cieco (Blind transfer)
- Trasferimento assistito (Consultative transfer)
- Conferenza a tre
- Indicatore di messaggio in attesa (Message waiting indicator)

## Il file di configurazione delle funzionalità

Alcune delle funzionalità presentate in questo capitolo sono configurate nel file di configurazione features.conf. È possibile modificare il comportamento di alcune funzionalità modificando questo file. Abbiamo incluso il relativo estratto qui sotto. Nelle prossime sezioni di questo capitolo, descriveremo ciascuna funzionalità. Estratto dal file di esempio (Asterisk 22)

![La sezione `[featuremap]` di features.conf, con i codici DTMF predefiniti per le funzionalità](../images/13-pbx-features-fig02.png)

> **[Nota 2ª ed.]** A partire da Asterisk 12+, il parcheggio di chiamata è stato spostato da `features.conf`/`app_features` nel suo modulo dedicato `res_parking` con configurazione in `res_parking.conf`. Il blocco parking-lot qui sotto (parkext, parkpos, context, parkingtime, ecc.) risiede in `res_parking.conf` ed è mostrato utilizzando la sintassi di Asterisk 22 `res_parking.conf.sample`. La sezione `[featuremap]` (i codici funzionalità DTMF, incluso `parkcall`) rimane in `features.conf`.

Le opzioni del parcheggio risiedono in `res_parking.conf`. Un parcheggio chiamato `default` esiste sempre, anche se non è presente nel file di configurazione. L'estratto qui sotto è tratto da Asterisk 22 `res_parking.conf.sample`:

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

I codici funzionalità DTMF (incluso quello a un passo `parkcall`) rimangono nella sezione `[featuremap]` di `features.conf`:

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

## Trasferimento di chiamata

Il trasferimento di chiamata può essere implementato dal telefono, da un ATA o da Asterisk stesso. Consulta il manuale del tuo telefono per capire come vengono trasferite le chiamate. Se il tuo telefono non supporta il trasferimento di chiamata, puoi utilizzare Asterisk per completare questa operazione. Il trasferimento di chiamata è implementato in due modi diversi. Il primo modo è utilizzare la funzionalità di trasferimento cieco: componi # seguito dal numero verso cui trasferire. A volte utilizzerai la funzionalità di trasferimento del tuo telefono IP o softphone IP. Puoi modificare il carattere di trasferimento modificando il parametro blindxfer nel file features.conf. Puoi abilitare il trasferimento assistito in Asterisk rimuovendo il ; prima del parametro atxfer nel file features.conf. Durante una conversazione, dovrai premere *2. Asterisk dirà “transfer” e ti darà il tono di linea. Il chiamante viene messo in attesa con musica. Dopo aver parlato con la persona di destinazione e aver riagganciato il telefono, il sistema mette in comunicazione il chiamante con la destinazione.

![Trasferimento di chiamata: i passaggi per un trasferimento cieco (premi # durante la chiamata) e un trasferimento assistito (premi *2)](../images/13-pbx-features-fig03.png)

### Elenco attività di configurazione

1. Se il telefono è basato su SIP, assicurati che l'opzione directmedia sia uguale a no oppure utilizza un'opzione t o T nell'applicazione dial()

## Parcheggio di chiamata

Questa funzionalità viene utilizzata per parcheggiare una chiamata. È utile, ad esempio, quando rispondi a una chiamata lontano dalla tua postazione e vuoi trasferire la chiamata sulla tua scrivania. Puoi farlo parcheggiando la chiamata in un'extension. Una volta raggiunta la scrivania, componi semplicemente il numero dell'extension di parcheggio per recuperare la chiamata.

![Parcheggio di chiamata: componi 700 per parcheggiare una chiamata nel primo slot libero (701–720); Asterisk annuncia lo slot, che comporrai da qualsiasi telefono per recuperare la chiamata](../images/13-pbx-features-fig04.png)

Per impostazione predefinita, l'extension 700 viene utilizzata per parcheggiare una chiamata. Durante una conversazione, premi # per trasferire la chiamata all'extension 700. Asterisk annuncerà l'extension di parcheggio, ad esempio 701 o 702. Riaggancia il telefono e il chiamante verrà messo in attesa. Vai al telefono sulla tua scrivania e componi l'extension di parcheggio annunciata per recuperare la chiamata. Se il chiamante rimane parcheggiato per troppo tempo, si attiverà la funzionalità di timeout e l'extension originariamente chiamata squillerà di nuovo.

### Elenco attività di configurazione

Segui i passaggi seguenti per abilitare il parcheggio di chiamata. Passaggio 1: Rendi il parcheggio raggiungibile dal tuo dialplan (obbligatorio). Il `context` del parcheggio predefinito è `parkedcalls` (impostato in `res_parking.conf`). Includi quel context nel context da cui i tuoi telefoni effettuano le chiamate, in `extensions.conf`:

```
include => parkedcalls
```

Passaggio 2: Testa la funzionalità di parcheggio di chiamata componendo #700. Note:

- L'extension di parcheggio non verrà mostrata nel comando CLI dialplan show.
- È necessario ricaricare il modulo di parcheggio dopo aver modificato il file di configurazione del parcheggio: `module reload res_parking.so`. Per le modifiche a features.conf, `module reload features.so`.
- Per parcheggiare una chiamata, devi trasferire a #700. Verifica le opzioni t e T nell'applicazione dial().

## Risposta di chiamata

La risposta di chiamata (call pickup) ti consente di catturare una chiamata di un collega nello stesso gruppo di chiamata. Questo aiuta, ad esempio, a evitare di doversi alzare per rispondere a una chiamata che sta squillando per un'altra persona nella tua stanza, ma che non è presente. Componendo *8, puoi catturare una chiamata all'interno del tuo gruppo di chiamata. Questo numero può essere modificato nel

```
features.conf file.
```

![Risposta di chiamata: i membri possono catturare solo le chiamate all'interno del proprio gruppo; l'operatore (pickupgroup=1,2,3) può rispondere alle chiamate di ogni gruppo](../images/13-pbx-features-fig05.png)

### Elenco attività di configurazione

Segui i passaggi seguenti per configurare la funzionalità di risposta di chiamata. Passaggio 1: Configura un gruppo di chiamata per le tue extension. Questo viene fatto nel file di configurazione del canale (pjsip.conf, iax.conf, chan_dahdi.conf). Per gli endpoint PJSIP, imposta `call_group` e `pickup_group` nella sezione endpoint di `pjsip.conf` (pjsip.conf utilizza nomi di opzioni in snake_case). Questa attività è obbligatoria.

Per PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Passaggio 2: Modifica il numero della funzionalità di risposta di chiamata (opzionale).

```
pickupexten=*8; Configures the call pickup extension
```

## Conferenza

Esistono diversi modi per implementare una conferenza su Asterisk. La prima opzione è semplicemente utilizzare la funzionalità di conferenza a tre del telefono. Utilizzando questa funzionalità nel telefono, non è richiesto alcun supporto nel server stesso. Tuttavia, quando desideri una conferenza con più di 3 persone, dovresti utilizzare una sala conferenze. L'applicazione di conferenza moderna di Asterisk è ConfBridge (`app_confbridge`).

ConfBridge supporta conferenze vocali HD e videoconferenze. Ci sono alcune limitazioni per la videoconferenza, come l'assenza di transcodifica: tutti i partecipanti devono utilizzare lo stesso codec e profilo. La videoconferenza utilizza una modalità "follow-the-talker", visualizzando l'immagine dell'ultima persona che ha parlato. Puoi configurare facilmente nuovi menu DTMF in ConfBridge.

> **[Nota 2ª ed.]** MeetMe (`app_meetme`) è stato **deprecato in Asterisk 19** ed era prevista la sua rimozione in Asterisk 21, ma tale rimozione è stata sospesa (su richiesta del progetto ViciDial). Il codice sorgente del modulo viene ancora distribuito con Asterisk 22, ma richiede DAHDI e **non viene compilato nella build predefinita di Asterisk 22**: un'installazione standard non ha `app_meetme.so` e l'applicazione `MeetMe()` non è disponibile. Tutte le nuove implementazioni di sale conferenze devono utilizzare ConfBridge. La sezione MeetMe di seguito è conservata solo per riferimento storico.

### Confbridge

Per avviare una sala conferenze, la sintassi è elencata di seguito.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Per ottenere una descrizione completa del comando, puoi utilizzare core show application confbridge.

![Output di `core show application confbridge`, che mostra la sinossi, la sintassi e gli argomenti bridge_profile, user_profile e menu](../images/13-pbx-features-fig06.png)

Come puoi vedere sopra, ci sono tre sezioni importanti: Bridge_profile: Definisci il profilo nel file confbridge.conf. Lì puoi selezionare il numero massimo di partecipanti, la registrazione, video_mode e molti altri parametri del bridge.

Non ha senso riprodurre l'intero file di esempio qui, quindi ti fornirò un semplice esempio su come configurare un bridge_profile nel file confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

User_profile: Qui definisci le opzioni specifiche per utente, come se l'utente sia un amministratore o meno. La musica d'attesa e molte altre opzioni possono essere impostate per utente. Esempio:

```
[admin_user]
type=user
admin=yes
```

Menu: Nella sezione menu puoi definire la mappatura della tastiera per l'applicazione, ad esempio dove attivare/disattivare il silenziamento (mute). Controlla il file confbridge.conf per vedere le opzioni. Esempio:

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

#### Funzioni Confbridge

Le opzioni del bridge di conferenza possono essere passate dinamicamente nel dial plan utilizzando la funzione CONFBRIDGE(). Vedi gli esempi di seguito:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

## Meetme (Legacy — deprecato, non compilato per impostazione predefinita in Asterisk 22)

> **[Nota 2ª ed.]** `app_meetme` è stato deprecato in Asterisk 19. La sua rimozione pianificata in Asterisk 21 è stata sospesa, quindi il codice sorgente viene ancora distribuito in Asterisk 22, ma il modulo non viene compilato nella build predefinita di Asterisk 22 (dipende da DAHDI). Un'installazione standard di Asterisk 22 non ha quindi l'applicazione `MeetMe()`. Il contenuto seguente è conservato per riferimento storico e per i lettori che effettuano l'aggiornamento da sistemi più vecchi. **Per le nuove installazioni, utilizza ConfBridge (vedi sopra).** La dipendenza DAHDI e il modulo `dahdi_dummy` non sono richiesti per ConfBridge.

In alternativa, nelle versioni precedenti di Asterisk potevi utilizzare l'applicazione meetme(). Meetme è un bridge di conferenza molto semplice da usare. Ricorda, meetme è stato deprecato in Asterisk 19 e dipende dal modulo DAHDI per la sincronizzazione.

![Tipi di conferenza MeetMe — conferenze a singolo oratore, protette da password e dinamiche — tutte richiedono una sorgente di temporizzazione Zaptel/DAHDI](../images/13-pbx-features-fig07.png)

### L'applicazione meetme()

Utilizzando il comando CLI meetme show, puoi ottenere la descrizione sopra. Per utilizzare meetme, devi compilare i driver DAHDI e avere almeno un modulo kernel DAHDI caricato. Se non hai almeno una scheda DAHDI installata, carica il modulo kernel dahdi_dummy per fornire una sorgente di temporizzazione. Descrizione:

![L'applicazione MeetMe(): sintassi `MeetMe([confno][,[options][,pin]])` e i suoi principali flag di opzione](../images/13-pbx-features-fig08.png)

L'applicazione meetme() inserisce l'utente in una conferenza meetme specificata. Se il numero della conferenza viene omesso, all'utente verrà richiesto di inserirne uno. L'utente può lasciare la conferenza riagganciando o, se viene specificata l'opzione p, premendo #. Nota: i moduli kernel DAHDI e almeno un driver hardware (o dahdi_dummy) devono essere presenti affinché la conferenza funzioni correttamente. Inoltre, il driver di canale chan_dahdi deve essere caricato affinché le opzioni i e r funzionino.

> **[Nota 2ª ed.]** Gli elenchi dei flag di opzione e dei comandi di amministrazione che seguono descrivono l'interfaccia legacy `app_meetme` e riflettono la documentazione storica `MeetMe()`/`MeetMeAdmin()`. Poiché `app_meetme` non viene compilato nell'installazione predefinita di Asterisk 22, questi flag non possono essere confermati su un sistema Asterisk 22 in esecuzione; sono riprodotti per i lettori che mantengono distribuzioni più vecchie. Su Asterisk 22, utilizza ConfBridge e la funzione di dialplan `CONFBRIDGE()` invece.

La stringa delle opzioni può contenere zero, una o più delle seguenti lettere:

- 'a' -- imposta la modalità amministratore
- 'A' -- imposta la modalità contrassegnata (marked)
- 'b' – esegue lo script AGI specificato in ${MEETME_AGI_BACKGROUND}. Predefinito: conf-background.agi (Nota: non funziona con canali non DAHDI nella stessa conferenza)
- 'c' -- annuncia il conteggio degli utenti quando si uniscono a una conferenza
- 'd' -- aggiunge dinamicamente la conferenza
- 'D' -- aggiunge dinamicamente la conferenza, richiedendo un PIN
- 'e' -- seleziona una conferenza vuota
- 'E' -- seleziona una conferenza vuota senza PIN
- 'i' -- annuncia un utente che entra/esce con revisione
- 'I' -- annuncia un utente che entra/esce senza revisione
- 'l' -- imposta la modalità solo ascolto (Listen only, niente conversazione)
- 'm' -- imposta inizialmente silenziato (muted)
- 'M' -- abilita la musica d'attesa quando la conferenza ha un singolo chiamante
- 'o' -- imposta l'ottimizzazione dell'oratore, che tratta gli oratori che non stanno parlando come silenziati, il che significa (a) nessuna codifica viene eseguita in trasmissione e (b) l'audio ricevuto che non è registrato come parlante viene omesso, evitando l'accumulo di rumore di fondo
- 'p' -- consente agli utenti di uscire dalla conferenza premendo '#'
- 'P' -- richiede sempre il PIN anche se è specificato
- 'q' -- modalità silenziosa (non riproduce i suoni di entrata/uscita)
- 'r' -- Registra la conferenza (registra come ${MEETME_RECORDINGFILE} utilizzando il formato ${MEETME_RECORDINGFORMAT}). Il nome file predefinito è meetme-conf-rec-${CONFNO}-${UNIQUEID} e il formato predefinito è wav.
- 's' -- Presenta il menu (utente o amministratore) quando viene ricevuto '*' ('send' al menu)
- 't' -- imposta la modalità solo conversazione (Talk only, niente ascolto)
- 'T' -- imposta il rilevamento dell'oratore (inviato all'interfaccia manager e all'elenco meetme)
- 'w[(<secs>)]' -- attende finché l'utente contrassegnato non entra nella conferenza
- 'x' -- chiude la conferenza quando l'ultimo utente contrassegnato esce
- 'X' -- consente all'utente di uscire dalla conferenza inserendo un'extension a una cifra valida ${MEETME_EXIT_CONTEXT} o il contesto corrente se tale variabile non è definita.
- '1' -- non riproduce il messaggio quando entra la prima persona

### File di configurazione Meetme

Questo file viene utilizzato per configurare l'applicazione meetme. Ad esempio:

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

Non è necessario utilizzare reload o restart per far sì che Asterisk veda le modifiche nel file meetme.conf.

### Applicazioni correlate a Meetme

L'applicazione meetme() ha altre due applicazioni di supporto.

```
MeetMeCount(confno[|var])
```

Riproduce il numero di utenti nella conferenza. Se viene specificata una variabile, non riproduce il messaggio ma imposta il numero di utenti su di essa.

```
MeetMeAdmin(confno,command,[user]):
```

Esegue il comando di amministrazione per una conferenza:

- 'e' -- Espelle l'ultimo utente che si è unito
- 'k' -- Espelle un utente dalla conferenza
- 'K' -- Espelle tutti gli utenti dalla conferenza
- 'l' -- Sblocca la conferenza
- 'L' -- Blocca la conferenza
- 'm' -- Riattiva l'audio di un utente
- 'M' -- Silenzia un utente
- 'n' -- Riattiva l'audio di tutti gli utenti nella conferenza
- 'N' -- Silenzia tutti gli utenti non amministratori nella conferenza
- 'r' -- Ripristina le impostazioni del volume di un utente
- 'R' -- Ripristina le impostazioni del volume di tutti gli utenti
- 's' -- Abbassa il volume di conversazione dell'intera conferenza
- 'S' -- Alza il volume di conversazione dell'intera conferenza
- 't' -- Abbassa il volume di conversazione di un utente
- 'T' -- Abbassa il volume di conversazione di tutti gli utenti
- 'u' -- Abbassa il volume di ascolto di un utente
- 'U' -- Abbassa il volume di ascolto di tutti gli utenti
- 'v' -- Abbassa il volume di ascolto dell'intera conferenza
- 'V' -- Alza il volume di ascolto dell'intera conferenza

### Elenco attività di configurazione Meetme

Segui i passaggi seguenti per configurare l'applicazione di conferenza meetme. Passaggio 1: Scegli l'extension per la sala Meetme (obbligatorio). Passaggio 2: Modifica il file meetme.conf per configurare le password (opzionale).

### Esempi

Esempio n. 1: Semplice sala meetme 1. Nel file extensions.conf, crea la sala conferenze 101

```
exten=>500,1,MeetMe(101,,123456)
```

2. Nel file meetme.conf, stabilisci la password per la sala 101. Nota importante: l'applicazione meetme() necessita di un timer per funzionare. Se non hai hardware Digium installato e configurato, usa dahdi_dummy come sorgente di temporizzazione.

## Registrazione di chiamata

Esistono diversi modi per registrare una chiamata in Asterisk. Puoi utilizzare l'applicazione mixmonitor() per registrare facilmente le chiamate.

### Utilizzo dell'applicazione mixmonitor

L'applicazione mixmonitor registra l'audio nel canale corrente nel file specificato. Se il nome file è un percorso assoluto, utilizza quel percorso. Altrimenti, crea il file nella directory di monitoraggio configurata da asterisk.conf.

![L'applicazione MixMonitor(): registra e mixa l'audio di un canale in un file, con opzioni per append, bridged-only e regolazione del volume](../images/13-pbx-features-fig09.png)

### Mixmonitor()

Registra una chiamata e mixa l'audio durante la registrazione [Descrizione] MixMonitor(<file>.<ext>[|<opzioni>[|<comando>]]) Registra l'audio sul canale corrente nel file specificato. opzioni: a- Accoda al file invece di sovrascriverlo. b-Salva l'audio nel file solo mentre il canale è in bridge. Nota: non include le conferenze. v(<x>) - Regola il volume di ascolto di un fattore <x> V(<x>) - Regola il volume di conversazione di un fattore <x> W(<x>) - Regola entrambi i volumi, di ascolto e di conversazione Opzioni valide:

- a - Accoda al file invece di sovrascriverlo.
- b - Salva l'audio nel file solo mentre il canale è in bridge.
- Nota: non include le conferenze.
- v(<x>) - Regola il volume udibile di un fattore <x> (da -4 a 4)
- V(<x>) - Regola il volume di conversazione di un fattore <x> (da -4 a 4)
- W(<x>) - Regola entrambi i volumi, udibile e di conversazione, di un fattore <x> (da -4 a 4)
- <comando> verrà eseguito al termine della registrazione. Qualsiasi stringa corrispondente a ^{X} verrà de-escapata in ${X} e tutte le variabili verranno valutate in quel momento. La variabile MIXMONITOR_FILENAME conterrà il nome del file utilizzato per la registrazione.

Una risorsa interessante è automon, che ti consente di comporre semplicemente *1 per iniziare immediatamente la registrazione. Esempio:

```
exten=>_4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten=>_4XXX,2,Dial(PJSIP/${EXTEN},20,jtTwW);wW enables the recording.
```

I canali audio sono in entrata (IN) e in uscita (OUT) e sono separati in due file distinti nella directory /var/spool/asterisk/monitor. Entrambi i file possono essere mixati utilizzando l'applicazione sox.

```
debian#soxmix *in.wav *out.wav output.wav
```

Se non vuoi utilizzare Set() prima dell'applicazione Dial(), puoi impostarlo nella sezione globals:

```
[globals]
DYNAMIC_FEATURES=>automon
```

### Musica d'attesa

La musica d'attesa (MOH) è cambiata diverse volte tra le versioni 1.0, 1.2 e 1.4. Nell'ultima versione, la MOH è impostata per impostazione predefinita su “FILE-BASED”. In altre parole, Asterisk fornirà i file MOH in formati come g729, alaw, ulaw e gsm. Pertanto, non è necessario transcodificare la musica prima di inviarla al canale. Ciò consente di risparmiare tempo di processore, il che è una modifica gradita per chi lavora con sistemi di produzione. Nelle versioni precedenti, la MOH era solitamente fornita tramite MP3 (può ancora essere configurata in quel modo). Fornire MOH tramite MP3 obbliga Asterisk a transcodificare, consumando preziosa potenza della CPU nel processo. Il nuovo file di configurazione è mostrato di seguito. Nota che la classe predefinita ora utilizza il formato file nativo mode=files. Tutte le altre modalità sono commentate. Ogni sezione è una classe. L'unica classe non commentata a questo punto è default. Se vuoi avere classi diverse per file diversi, dovrai creare nuove sezioni (classi).

![La configurazione di esempio di musiconhold.conf, che elenca le modalità MOH valide (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

### Attività di configurazione MOH

Ora, per utilizzare la musica d'attesa, imposta la classe MOH nei file di configurazione del canale (chan_dahdi.conf, pjsip.conf, iax.conf, ecc.). Per gli endpoint PJSIP, imposta `moh_suggest` nella sezione endpoint di `pjsip.conf` (il nome dell'opzione legacy `musicclass` si applica a chan_dahdi e ad altri driver di canale, non a PJSIP). I brani freeplay installati sono ora in formato wav. Al momento dell'installazione, puoi selezionare (utilizzando make menuselect) i formati di file MOH disponibili. Se vuoi aggiungere nuovi file MOH, dovrai fornirli nei formati richiesti. Ad esempio:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Nel dial plan, puoi ascoltare la MOH utilizzando il seguente esempio:

```
Exten=>100,1,SetMusicOnHold(default)
Exten=>100,2,Dial(DAHDI/2)
```

Per configurare il file extensions.conf per testare la MOH:

```
[local]
exten => 6601,1,WaitMusicOnHold(30)
```

## Mappe delle applicazioni

Le mappe delle applicazioni ti consentono di aggiungere nuove funzionalità utilizzando la sezione `[applicationmap]` del file features.conf. Supponiamo che tu debba identificare il tipo di cliente a cui stai rispondendo in un call center. Potresti creare una mappa delle applicazioni per ogni tipo di cliente, che potrebbe contare il numero di clienti che hanno risposto per tipo.

## Quiz

1. Quali affermazioni sono vere riguardo al parcheggio di chiamata?
   - A. Per impostazione predefinita, l'extension 800 viene utilizzata per il parcheggio di chiamata.
   - B. Quando sei lontano dalla tua scrivania e ricevi una chiamata, puoi parcheggiarla; il sistema annuncia lo slot di parcheggio e tu componi quello slot da qualsiasi telefono per recuperare la chiamata.
   - C. Per impostazione predefinita, l'extension 700 parcheggia una chiamata e le chiamate vengono parcheggiate negli slot 701–720.
   - D. Componi 700 per recuperare una chiamata parcheggiata.
2. Per utilizzare la funzionalità di risposta di chiamata, tutte le extension devono essere nello stesso ___. Per i canali DAHDI, questo viene configurato nel file ___.
3. Quando trasferisci una chiamata puoi scegliere tra un trasferimento ___, dove la destinazione non viene consultata prima, e un trasferimento ___, dove parli con la destinazione prima di completarlo.
4. Per effettuare un trasferimento assistito (consultativo) utilizzi la sequenza ___; per un trasferimento cieco utilizzi ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Per ospitare chiamate in conferenza in Asterisk 22, utilizzi l'applicazione ___.
6. In ConfBridge, a un partecipante vengono concessi privilegi di amministratore (espellere, silenziare gli altri, bloccare la sala) impostando ___ nel suo profilo utente (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Il formato migliore per la musica d'attesa è MP3, perché utilizza pochissima potenza di elaborazione sul server Asterisk.
   - A. Vero
   - B. Falso
8. Per rispondere a una chiamata da uno specifico gruppo di chiamata, devi essere nel gruppo ___ corrispondente.
9. Puoi registrare una chiamata con l'applicazione MixMonitor() o la funzionalità one-touch (automon). Per impostazione predefinita, automon utilizza la sequenza DTMF ___.
   - A. *1
   - B. *2
   - C. #3
   - D. #1
10. In ConfBridge, quale opzione del profilo utente `confbridge.conf` fa sì che un partecipante si unisca silenziato (possono sentire la conferenza ma non possono essere sentiti finché non viene riattivato l'audio)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Risposte:** 1 — B, C · 2 — gruppo di risposta (pickup group); `chan_dahdi.conf` · 3 — cieco; assistito · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — risposta · 9 — A · 10 — A
