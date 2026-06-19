# Utilizzo delle funzionalità del PBX

Nei sistemi SIP, la maggior parte delle funzionalità telefoniche è implementata nell'endpoint. Esiste una grande varietà di telefoni SIP e produttori, e l'interoperabilità non è garantita. Il team di sviluppo di Asterisk ha svolto un lavoro straordinario implementando la maggior parte delle funzionalità direttamente nel PBX, rendendo Asterisk quasi indipendente dall'endpoint. Tuttavia, a volte troverai la stessa funzione eseguita sia dal telefono che da Asterisk stesso. L'integrazione tra telefono e PBX è la prossima frontiera dell'usabilità, su cui i sistemi proprietari si stanno concentrando proprio ora. In questo capitolo, imparerai come utilizzare la maggior parte di queste funzionalità.

## Obiettivi

Al termine di questo capitolo, sarai in grado di comprendere e utilizzare:

- Parcheggio di chiamata (Call Parking)
- Risposta a chiamata (Call Pickup)
- Trasferimento di chiamata (Call Transfer)
- Conferenza (ConfBridge)
- Registrazione di chiamata (Call Recording)
- Musica d'attesa (Music on hold)

## Dove sono implementate le funzionalità

Innanzitutto, è importante capire quando le funzionalità del PBX vengono eseguite e quando invece è il telefono a svolgere tutto il lavoro. Ad esempio, potresti trasferire una chiamata utilizzando il tasto TRANSFER sul telefono o componendo # (trasferimento incondizionato eseguito dal PBX stesso).

## Funzionalità implementate da Asterisk

Queste funzionalità sono implementate nel PBX dal codice di Asterisk:

- Musica d'attesa
- Parcheggio di chiamata
- Risposta a chiamata
- Registrazione di chiamata
- Sala conferenze ConfBridge
- Trasferimento di chiamata (cieco e consultivo)

## Funzionalità solitamente implementate dal dialplan

Queste funzionalità devono essere programmate nel dialplan di Asterisk (extensions.conf):

- Trasferimento di chiamata su occupato
- Trasferimento di chiamata immediato
- Trasferimento di chiamata su mancata risposta
- Filtraggio chiamate (blacklist)
- Non disturbare (Do not disturb)
- Ricomposizione (Redial)

## Funzionalità solitamente implementate dal telefono

Queste funzionalità sono implementate dal firmware del telefono:

![Dove sono solitamente implementate le funzionalità del PBX: in Asterisk stesso, nel dialplan o nel telefono](../images/13-pbx-features-fig01.png)

- Messa in attesa di chiamata
- Trasferimento cieco
- Trasferimento consultivo
- Conferenza a tre
- Indicatore di messaggio in attesa

## Il file di configurazione delle funzionalità

Alcune delle funzionalità presentate in questo capitolo sono configurate nel file di configurazione features.conf. È possibile modificare il comportamento di alcune funzionalità modificando questo file. Abbiamo incluso il relativo estratto qui sotto. Nelle prossime sezioni di questo capitolo, descriveremo ogni funzionalità. Estratto dal file di esempio (Asterisk 22)

![La sezione `[featuremap]` di features.conf, con i codici DTMF predefiniti per le funzionalità](../images/13-pbx-features-fig02.png)

Da Asterisk 12, il parcheggio di chiamata è stato spostato fuori da `features.conf` nel suo modulo dedicato, `res_parking`, con la configurazione in `res_parking.conf`. Il blocco parking-lot qui sotto (`parkext`, `parkpos`, `context`, `parkingtime` e così via) risiede in `res_parking.conf`. La sezione `[featuremap]` (i codici DTMF delle funzionalità, incluso `parkcall`) rimane in `features.conf`.

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

I codici DTMF delle funzionalità (incluso `parkcall` in un solo passaggio) rimangono nella sezione `[featuremap]` di `features.conf`:

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

## Trasferimento di chiamata

Il trasferimento di chiamata può essere implementato dal telefono, da un ATA o da Asterisk stesso. Consulta il manuale del tuo telefono per capire come vengono trasferite le chiamate. Se il tuo telefono non supporta il trasferimento di chiamata, puoi utilizzare Asterisk per completare questa operazione. Il trasferimento di chiamata è implementato in due modi diversi. Il primo modo consiste nell'utilizzare la funzionalità di trasferimento cieco: componi # seguito dal numero verso cui trasferire. A volte utilizzerai la funzionalità di trasferimento del tuo telefono IP o softphone IP. Puoi modificare il carattere di trasferimento modificando il parametro blindxfer nel file features.conf. Puoi abilitare il trasferimento assistito in Asterisk rimuovendo il ; prima del parametro atxfer nel file features.conf. Durante una conversazione, dovrai premere *2. Asterisk dirà “transfer” e ti darà un segnale di linea. Il chiamante viene messo in musica d'attesa. Dopo aver parlato con la persona di destinazione e aver riagganciato il telefono, il sistema mette in comunicazione il chiamante con la destinazione.

![Trasferimento di chiamata: i passaggi per un trasferimento cieco (premi # durante la chiamata) e un trasferimento assistito (premi *2)](../images/13-pbx-features-fig03.png)

### Elenco delle attività di configurazione

1. Per un endpoint PJSIP, assicurati che l'opzione `direct_media` sia impostata su `no` (in modo che il media fluisca attraverso Asterisk e i codici delle funzionalità vengano rilevati), oppure utilizza un'opzione `t`/`T` nell'applicazione `Dial()`

## Parcheggio di chiamata

Questa funzionalità viene utilizzata per parcheggiare una chiamata. Questo è utile, ad esempio, quando rispondi a una telefonata lontano dalla tua postazione e vuoi trasferire la chiamata sulla tua scrivania. Puoi farlo parcheggiando la chiamata in un'extension. Una volta raggiunta la scrivania, componi semplicemente il numero dell'extension di parcheggio per recuperare la chiamata.

![Parcheggio di chiamata: componi 700 per parcheggiare una chiamata nel primo slot libero (701–720); Asterisk annuncia lo slot, che componi da qualsiasi telefono per recuperare la chiamata](../images/13-pbx-features-fig04.png)

Per impostazione predefinita, l'extension 700 viene utilizzata per parcheggiare una chiamata. Nel mezzo di una conversazione, premi # per trasferire la chiamata all'extension 700. Ora Asterisk annuncerà la tua extension di parcheggio, come 701 o 702. Riaggancia il telefono e il chiamante verrà messo in attesa. Vai al telefono della tua scrivania e componi l'extension di parcheggio annunciata per recuperare la chiamata. Se il chiamante rimane parcheggiato per molto tempo, la funzionalità di timeout si attiverà e l'extension originariamente chiamata squillerà di nuovo.

### Elenco delle attività di configurazione

Segui i passaggi seguenti per abilitare il parcheggio di chiamata. Passaggio 1: Rendi il parcheggio raggiungibile dal tuo dialplan (obbligatorio). Il `context` del parcheggio predefinito è `parkedcalls` (impostato in `res_parking.conf`). Includi quel context nel context da cui i tuoi telefoni effettuano le chiamate, in `extensions.conf`:

```
include => parkedcalls
```

Passaggio 2: Testa la funzionalità di parcheggio di chiamata componendo #700. Note:

- L'extension di parcheggio non verrà mostrata nel comando CLI dialplan show.
- È necessario ricaricare il modulo di parcheggio dopo aver modificato il file di configurazione del parcheggio: `module reload res_parking.so`. Per le modifiche a features.conf, `module reload features.so`.
- Per parcheggiare una chiamata, devi trasferire a #700. Verifica le opzioni `t` e `T` nell'applicazione `Dial()`.

## Risposta a chiamata

La risposta a chiamata ti consente di catturare una chiamata da un collega nello stesso gruppo di chiamata. Questo aiuta, ad esempio, a evitare di doversi alzare per rispondere a una chiamata che sta squillando per un'altra persona nella tua stanza, ma che non è presente. Componendo *8, puoi catturare una chiamata all'interno del tuo gruppo di chiamata. Questo numero può essere modificato nel

```
features.conf file.
```

![Risposta a chiamata: i membri possono catturare solo le chiamate all'interno del proprio gruppo; l'operatore (pickupgroup=1,2,3) può rispondere alle chiamate di ogni gruppo](../images/13-pbx-features-fig05.png)

### Elenco delle attività di configurazione

Segui i passaggi seguenti per configurare la funzionalità di risposta a chiamata. Passaggio 1: Configura un gruppo di chiamata per le tue extension. Questo viene fatto nel file di configurazione del canale (pjsip.conf, iax.conf, chan_dahdi.conf). Per gli endpoint PJSIP, imposta `call_group` e `pickup_group` nella sezione endpoint di `pjsip.conf` (pjsip.conf utilizza nomi di opzioni in snake_case). Questa attività è obbligatoria.

Per PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


Passaggio 2: Modifica il numero della funzionalità di risposta a chiamata (opzionale). Questo è impostato nella sezione `[general]` di `features.conf`, non in `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## Conferenza (call conference)

Esistono diversi modi per implementare una conferenza su Asterisk. La prima opzione è semplicemente utilizzare la funzionalità di conferenza a tre del telefono. Utilizzando questa funzionalità nel telefono non è richiesto alcun supporto nel server stesso. Tuttavia, quando desideri una conferenza con più di 3 persone, dovresti gestire una sala conferenze. L'applicazione di conferenza moderna di Asterisk è ConfBridge (`app_confbridge`).

ConfBridge supporta conferenze vocali HD e videoconferenze. Ci sono alcune limitazioni per le videoconferenze, come l'assenza di transcodifica: tutti i partecipanti devono utilizzare lo stesso codec e profilo. La videoconferenza utilizza una modalità "follow-the-talker", visualizzando l'immagine dell'ultima persona che ha parlato. Puoi configurare facilmente nuovi menu DTMF in ConfBridge.

ConfBridge sostituisce la vecchia applicazione MeetMe, che è stata deprecata in Asterisk 19 e rimossa in Asterisk 21. A differenza di MeetMe, ConfBridge **non** richiede DAHDI o una sorgente di timing hardware: si basa sull'interfaccia di timing integrata di Asterisk (`res_timing_timerfd` su Linux, o `res_timing_pthread`), quindi non è necessario alcun modulo `dahdi_dummy`. Se stai migrando da un sistema più vecchio che utilizzava `MeetMe()` e `meetme.conf`, sostituiscili con `ConfBridge()` e `confbridge.conf` come descritto di seguito.

### ConfBridge

Per avviare una sala conferenze, la sintassi è elencata di seguito.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Per ottenere una descrizione completa del comando puoi usare core show application confbridge.

![Output di `core show application confbridge`, che mostra la sinossi, la sintassi e gli argomenti bridge_profile, user_profile e menu](../images/13-pbx-features-fig06.png)

![Diversi endpoint PJSIP si uniscono a una conferenza ConfBridge denominata (101); un partecipante è l'amministratore. Il mixing e il timing sono gestiti da `res_confbridge` e dal timer integrato `res_timing_*` — non è richiesto DAHDI.](../images/13-pbx-features-fig09.png)

Come puoi vedere sopra, ci sono tre argomenti importanti, ognuno dei quali mappa a un tipo di sezione in `confbridge.conf`. **bridge_profile** (una sezione `type=bridge`): qui selezioni il numero massimo di partecipanti (`max_members`), la registrazione (`record_conference`), `video_mode` e molti altri parametri a livello di bridge.

Non ha senso riprodurre l'intero file di esempio qui, quindi ti fornirò un semplice esempio su come configurare un bridge_profile nel file confbridge.conf.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (una sezione `type=user`): qui definisci le opzioni specifiche per utente, come se l'utente sia un amministratore (`admin=yes`), se inizia in muto (`startmuted=yes`), musica d'attesa e molte altre opzioni per utente. Esempio:

```
[admin_user]
type=user
admin=yes
```

**menu** (una sezione `type=menu`): qui definisci la mappatura del tastierino (DTMF) per la conferenza, ad esempio quale tasto attiva/disattiva il muto, regola il volume o abbandona la conferenza. Controlla il file `confbridge.conf.sample` per vedere tutte le azioni disponibili. Esempio:

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

#### Funzioni di ConfBridge

Le opzioni del bridge di conferenza possono essere passate dinamicamente nel dialplan utilizzando la funzione CONFBRIDGE(). Vedi gli esempi qui sotto:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandi di amministrazione di ConfBridge e migrazione da MeetMe

Se provieni da MeetMe, le funzioni di amministrazione che utilizzavi tramite `MeetMeAdmin()` e l'opzione `a` (admin) sono ora espresse tramite il **profilo utente amministratore** (`admin=yes`) più le azioni del **menu**. Un amministratore che si unisce con un profilo admin e un menu contenente azioni di amministrazione può bloccare la sala, espellere utenti e silenziare i partecipanti dal vivo tramite il tastierino. Le azioni di menu pertinenti in `confbridge.conf` sono:

- `admin_kick_last` -- espelle l'ultimo utente che si è unito
- `admin_toggle_mute_participants` -- silenzia/riattiva tutti i partecipanti non amministratori
- `toggle_mute` -- silenzia/riattiva te stesso
- `participant_count` -- annuncia il numero di partecipanti
- `leave_conference` -- abbandona il bridge e continua nel dialplan

Queste sostituiscono i flag delle opzioni di MeetMe `MeetMe()` (`a`, `A`, `m`, `M`, `l`, `x`, …) e i comandi `MeetMeAdmin()` (`k`, `K`, `L`, `M`, `N`, …). Non esiste `meetme.conf` in Asterisk 22; tutta la configurazione della conferenza risiede in `confbridge.conf` e le modifiche vengono applicate con `module reload res_confbridge.so`.

### Esempio di ConfBridge

Per creare una sala conferenze raggiungibile all'extension 500, in `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Il primo chiamante a comporre il 500 crea la conferenza `101`; i chiamanti successivi si uniscono ad essa. I profili e i menu qui referenziati (`default_bridge`, `default_user`, `sample_user_menu`) sono definiti in `confbridge.conf`. Per richiedere un PIN, imposta `pin=` nel profilo utente; per rendere un partecipante un amministratore della conferenza, assegna loro un profilo utente con `admin=yes`.

## Registrazione di chiamata

Esistono diversi modi per registrare una chiamata in Asterisk. Puoi utilizzare l'applicazione `MixMonitor()` per registrare facilmente le chiamate. (La vecchia applicazione `Monitor`, che registrava due file separati, è stata rimossa; usa invece `MixMonitor`.)

### Utilizzo dell'applicazione MixMonitor

L'applicazione `MixMonitor` registra l'audio nel canale corrente nel file specificato. Se il nome del file è un percorso assoluto, utilizza quel percorso. Altrimenti, crea il file nella directory di monitoraggio configurata in asterisk.conf.

![L'applicazione MixMonitor(): registra e mixa l'audio di un canale in un file, con opzioni per append, bridged-only e regolazione del volume](../images/13-pbx-features-fig09.png)

### MixMonitor()

Registra una chiamata e mixa l'audio durante la registrazione. Sintassi: `MixMonitor(filename.extension[,options[,command]])`. Registra l'audio sul canale corrente nel file specificato. Opzioni valide:

- a - Aggiunge al file invece di sovrascriverlo.
- b - Salva l'audio nel file solo mentre il canale è in bridge.
- Nota: non include le conferenze.
- v(<x>) - Regola il volume udibile di un fattore <x> (da -4 a 4)
- V(<x>) - Regola il volume parlato di un fattore <x> (da -4 a 4)
- W(<x>) - Regola entrambi i volumi, udibile e parlato, di un fattore <x> (da -4 a 4)
- <command> verrà eseguito al termine della registrazione. Qualsiasi stringa corrispondente a ^{X} verrà de-escapata in ${X} e tutte le variabili verranno valutate in quel momento. La variabile MIXMONITOR_FILENAME conterrà il nome del file utilizzato per la registrazione.

Una risorsa interessante è la funzionalità di registrazione one-touch `automixmon`, che consente a una parte di comporre un codice DTMF (predefinito `*3`) durante una chiamata per avviare immediatamente (e disattivare) la registrazione. È basata su MixMonitor, quindi scrive un singolo file mixato. Esempio:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Le opzioni `X` e `x` abilitano la funzionalità di MixMonitor one-touch rispettivamente per il chiamante e il chiamato. Poiché MixMonitor registra un singolo file mixato, non c'è bisogno di combinare file IN/OUT separati in seguito (il vecchio approccio `automon`/`Monitor`, che produceva due file per `soxmix`, è stato rimosso insieme all'applicazione `Monitor`).

Se non vuoi usare Set() prima dell'applicazione Dial(), puoi impostarlo nella sezione globals:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Musica d'attesa

La musica d'attesa (MOH) è cambiata diverse volte tra le versioni 1.0, 1.2 e 1.4. Nell'ultima versione, la MOH è impostata per impostazione predefinita su “FILE-BASED”. In altre parole, Asterisk fornirà i file MOH in formati come g729, alaw, ulaw e gsm. Pertanto, non è necessario transcodificare la musica prima di inviarla al canale. Questo risparmia tempo di processore, il che è una modifica gradita per chi lavora con sistemi in produzione. Nelle versioni precedenti, la MOH era solitamente fornita in MP3 (può ancora essere configurata in quel modo). Fornire MOH utilizzando MP3 obbliga Asterisk a transcodificare, spendendo preziosa potenza della CPU nel processo. Il nuovo file di configurazione è mostrato di seguito. Nota che la classe predefinita ora utilizza la modalità nativa del formato file mode=files. Tutte le altre modalità sono commentate. Ogni sezione è una classe. L'unica classe non commentata a questo punto è default. Se vuoi avere classi diverse per file diversi, dovrai creare nuove sezioni (classi).

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

Ora, per utilizzare la musica d'attesa, imposta la classe MOH nei file di configurazione del canale (chan_dahdi.conf, pjsip.conf, iax.conf e così via). Per gli endpoint PJSIP, imposta `moh_suggest` nella sezione endpoint di `pjsip.conf` (il nome dell'opzione legacy `musicclass` si applica a chan_dahdi e ad altri driver di canale, non a PJSIP). I brani freeplay installati sono ora in formato wav. Al momento dell'installazione, puoi selezionare (usando make menuselect) i formati di file MOH disponibili. Se vuoi aggiungere nuovi file MOH, dovrai fornirli nei formati richiesti. Ad esempio:

```
In /etc/asterisk/chan_dahdi.conf, add the line:
[channels]
musiconhold=default
Edit the file /etc/asterisk/musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Nel dialplan, puoi avviare la musica d'attesa su un canale con `StartMusicOnHold` (e interromperla con `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Per riprodurre musica d'attesa per un tempo fisso come test rapido, usa l'applicazione `MusicOnHold` con una durata (in secondi):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mappe delle applicazioni

Le mappe delle applicazioni ti consentono di aggiungere nuove funzionalità utilizzando la sezione `[applicationmap]` del file features.conf. Supponiamo che tu debba identificare il tipo di cliente a cui stai rispondendo in un call center. Potresti creare una mappa delle applicazioni per ogni tipo di cliente, che potrebbe contare il numero di clienti che hanno risposto per tipo.

## Quiz

1. Quali affermazioni sono vere riguardo al parcheggio di chiamata?
   - A. Per impostazione predefinita, l'extension 800 viene utilizzata per il parcheggio di chiamata.
   - B. Quando sei lontano dalla tua scrivania e ricevi una chiamata, puoi parcheggiarla; il sistema annuncia lo slot di parcheggio e tu componi quello slot da qualsiasi telefono per recuperare la chiamata.
   - C. Per impostazione predefinita, l'extension 700 parcheggia una chiamata e le chiamate vengono parcheggiate negli slot 701–720.
   - D. Componi 700 per recuperare una chiamata parcheggiata.
2. Per utilizzare la funzionalità di risposta a chiamata, tutte le extension devono trovarsi nello stesso ___. Per i canali DAHDI questo è configurato nel file ___.
3. Quando trasferisci una chiamata puoi scegliere tra un trasferimento ___, dove la destinazione non viene consultata prima, e un trasferimento ___, dove parli con la destinazione prima di completarlo.
4. Per effettuare un trasferimento assistito (consultativo) utilizzi la sequenza ___; per un trasferimento cieco utilizzi ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Per ospitare chiamate in conferenza in Asterisk 22, utilizzi l'applicazione ___.
6. In ConfBridge, a un partecipante vengono concessi privilegi di amministratore (espellere, silenziare altri, bloccare la sala) impostando ___ nel suo profilo utente (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Il formato migliore per la musica d'attesa è MP3, perché utilizza pochissima potenza di elaborazione sul server Asterisk.
   - A. Vero
   - B. Falso
8. Per rispondere a una chiamata da uno specifico gruppo di chiamata, devi essere nel gruppo ___ corrispondente.
9. Puoi registrare una chiamata con l'applicazione MixMonitor() o la funzionalità di registrazione one-touch (`automixmon`). Per impostazione predefinita, `automixmon` utilizza la sequenza DTMF ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, quale opzione del profilo utente `confbridge.conf` fa sì che un partecipante si unisca in muto (possono sentire la conferenza ma non possono essere sentiti finché non vengono riattivati)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Risposte:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
