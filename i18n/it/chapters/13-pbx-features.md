# Utilizzo delle funzionalità PBX

In sistemi SIP, la maggior parte delle funzionalità telefoniche è implementata nell'endpoint. Esistono numerosi telefoni SIP e produttori, e l'interoperabilità non è garantita. Il team di sviluppo di Asterisk ha svolto un lavoro straordinario implementando la maggior parte delle funzionalità direttamente nel PBX, rendendo Asterisk quasi indipendente dall'endpoint. Tuttavia, a volte si riscontra la stessa funzione realizzata sia dal telefono sia da Asterisk stesso. L'integrazione tra telefono e PBX è la prossima frontiera dell'usabilità e il punto su cui i sistemi proprietari si stanno concentrando attualmente. In questo capitolo imparerai a utilizzare la maggior parte di queste funzionalità.

## Obiettivi

By the end of this chapter, you will be able to understand and use:

- Parcheggio delle chiamate
- Prelievo della chiamata
- Trasferimento della chiamata
- Conferenza chiamata (ConfBridge)
- Registrazione della chiamata
- Musica in attesa

## Dove le funzionalità sono implementate

Prima di tutto, è importante capire quando le funzionalità del PBX vengono eseguite rispetto a quando è il telefono a fare tutto il lavoro. Ad esempio, è possibile trasferire una chiamata usando il pulsante TRANSFER sul telefono o componendo # (trasferimento incondizionato eseguito dal PBX stesso).

## Funzionalità implementate da Asterisk

- Musica in attesa
- Parcheggio chiamata
- Prelievo chiamata
- Registrazione chiamata
- Sala conferenza ConfBridge
- Trasferimento chiamata (cieco e consultivo)

## Funzionalità solitamente implementate dal dial plan

Queste funzionalità devono essere programmate nel Asterisk dial plan (extensions.conf):

- Inoltro chiamata quando occupato
- Inoltro chiamata immediato
- Inoltro chiamata se non risposta
- Filtraggio chiamate (lista nera)
- Non disturbare
- Richiama

## Funzionalità solitamente implementate dal telefono

These features are implemented by the phone’s firmware:

![Dove le funzionalità del PBX sono solitamente implementate: in Asterisk stesso, nel dialplan o nel telefono](../images/13-pbx-features-fig01.png)

- Chiamata in attesa
- Trasferimento cieco
- Trasferimento consultivo
- Conferenza a tre vie
- Indicatore di messaggi in attesa

## Il file di configurazione delle funzionalità

Alcune delle funzionalità presentate in questo capitolo sono configurate nel file di configurazione features.conf. È possibile modificare il comportamento di alcune funzionalità modificando questo file. Abbiamo incluso di seguito l'estratto rilevante. Nelle sezioni successive di questo capitolo descriveremo ogni funzionalità. Estratto dal file di esempio (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

Dalla versione 12 di Asterisk, il parcheggio delle chiamate è stato spostato fuori da `features.conf` in un proprio modulo, `res_parking`, con configurazione in `res_parking.conf`. Il blocco parking-lot qui sotto (`parkext`, `parkpos`, `context`, `parkingtime`, e così via) risiede in `res_parking.conf`. La sezione `[featuremap]` (i codici delle funzionalità DTMF, inclusi `parkcall`) rimane in `features.conf`.

Le opzioni del parking-lot risiedono in `res_parking.conf`. Un parcheggio chiamato `default` esiste sempre, anche se non è presente nel file di configurazione. L'estratto qui sotto è tratto dal file Asterisk 22 `res_parking.conf.sample`:

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

I codici delle funzionalità DTMF (incluso il `parkcall` a un passo) rimangono nella sezione `[featuremap]` di `features.conf`:

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

Il trasferimento di chiamata può essere implementato dal telefono, dall'ATA o da Asterisk stesso. Consulta il manuale del tuo telefono per capire come vengono trasferite le chiamate. Se il tuo telefono non supporta il trasferimento di chiamata, puoi usare Asterisk per svolgere questa operazione. Il trasferimento di chiamata è implementato in due modi diversi.

Il primo modo è utilizzare la funzione di trasferimento cieco: comporre # seguito dal numero da trasferire. Talvolta utilizzerai la funzione di trasferimento del tuo telefono IP o del tuo softphone IP. Puoi modificare il carattere di trasferimento modificando il parametro blindxfer nel file features.conf.

Puoi abilitare il trasferimento assistito in Asterisk rimuovendo il ; prima del parametro atxfer nel file features.conf. Durante una conversazione, premi *2. Asterisk dirà "transfer" e ti darà un tono di composizione. Il chiamante viene inviato alla musica di attesa. Dopo aver parlato con la persona di destinazione e aver riagganciato il telefono, il sistema collega il chiamante alla destinazione.

![Call transfer: i passaggi per un trasferimento cieco (premi # durante la chiamata) e un trasferimento assistito (premi *2)](../images/13-pbx-features-fig03.png)

### Configuration task list

1. For a PJSIP endpoint, make sure the option `direct_media` is set to `no` (so the media flows through Asterisk and the feature codes are detected), or use a `t`/`T` option in the `Dial()` application

## Call parking

Questa funzionalità è usata per parcheggiare una chiamata. Questo è utile, ad esempio, quando si risponde a una telefonata fuori dalla propria stanza e si desidera trasferire la chiamata di nuovo alla propria scrivania. È possibile farlo parcheggiando la chiamata in un’estensione. Una volta arrivati alla scrivania, basta digitare il numero dell’estensione di parcheggio per recuperare la chiamata.

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

Per impostazione predefinita, l’estensione 700 è usata per parcheggiare una chiamata. Nel mezzo di una conversazione, premere # per trasferire la chiamata all’estensione 700. Ora Asterisk annuncerà la tua estensione di parcheggio, ad esempio 701 o 702. Riagganciare il telefono e il chiamante verrà messo in attesa. Andare al telefono della scrivania e digitare l’estensione di parcheggio annunciata per recuperare la chiamata. Se il chiamante rimane parcheggiato a lungo, la funzione di timeout si attiverà e l’estensione originale chiamata squillerà nuovamente.

### Configuration task list

Segui i passaggi seguenti per abilitare il parcheggio delle chiamate. Passo 1: Rendi il parcheggio raggiungibile dal tuo dialplan (obbligatorio). Il parcheggio predefinito `context` è `parkedcalls` (impostato in `res_parking.conf`). Includi quel contesto nel contesto da cui i tuoi telefoni compongono, in `extensions.conf`:

```
include => parkedcalls
```

Passo 2: Testa la funzionalità di parcheggio chiamando #700. Note:

- L’estensione di parcheggio non verrà mostrata nel comando CLI `dialplan show`.
- È necessario ricaricare il modulo di parcheggio dopo aver modificato il file di configurazione del parcheggio: `module reload res_parking.so`. Per le modifiche a `features.conf`, `module reload features.so`.
- Per parcheggiare una chiamata, è necessario trasferire a #700. Verifica le opzioni `t` e `T` nell’applicazione `Dial()`.

## Call pickup

Call pickup allows you to capture a call from a colleague in the same call group. This would help avoid, for example, having to wake up to take a call that is ringing to another person in your room, but who is not present. By dialing *8, you can capture a call within your call group. This number can be modified in the `features.conf` file.

![Call pickup: i membri possono catturare solo le chiamate all'interno del proprio gruppo; l'operatore (pickupgroup=1,2,3) può rispondere alle chiamate di tutti i gruppi](../images/13-pbx-features-fig05.png)

### Configuration task list

Follow the steps below to configure the call pickup feature. Step 1: Configure a call group for your extensions. This is done in the channel configuration file (pjsip.conf, iax.conf, chan_dahdi.conf). For PJSIP endpoints, set `call_group` and `pickup_group` in the endpoint section of `pjsip.conf` (pjsip.conf uses snake_case option names). This task is required.

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

Ci sono diversi modi per implementare una conferenza su Asterisk. La prima opzione è semplicemente utilizzare la capacità di conferenza a tre vie del telefono. Usando questa funzione sul telefono non è necessario alcun supporto sul server stesso. Tuttavia, quando si desidera una conferenza con più di 3 persone, è necessario avviare una stanza conferenza. L'applicazione moderna per conferenze di Asterisk è ConfBridge (`app_confbridge`).

ConfBridge supporta conferenze vocali HD e videoconferenze. Ci sono alcune limitazioni per le videoconferenze, come l'assenza di transcodifica — tutti i partecipanti devono utilizzare lo stesso codec e profilo. La videoconferenza utilizza una modalità follow-the-talker, mostrando l'immagine dell'ultima persona che ha parlato. È possibile configurare facilmente nuovi menu DTMF in ConfBridge.

ConfBridge sostituisce la vecchia applicazione MeetMe, che è stata deprecata in Asterisk 19. MeetMe è ancora presente nell'albero sorgente di Asterisk 22, ma dipende da DAHDI e non viene compilata per impostazione predefinita, quindi in una tipica installazione PJSIP è semplicemente non disponibile — ConfBridge è l'applicazione conferenza supportata. A differenza di MeetMe, ConfBridge **non** richiede DAHDI o una sorgente di temporizzazione hardware: si basa sull'interfaccia di temporizzazione integrata di Asterisk (`res_timing_timerfd` on Linux, or `res_timing_pthread`), quindi non è necessario alcun modulo `dahdi_dummy`. Se si sta migrando da un sistema più vecchio che utilizzava `MeetMe()` e `meetme.conf`, sostituire questi con `ConfBridge()` e `confbridge.conf` come descritto di seguito.

### ConfBridge

Per avviare una stanza conferenza, la sintassi è elencata di seguito.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

Per ottenere una descrizione completa del comando è possibile utilizzare `core show application confbridge`.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

Come si può vedere sopra, ci sono tre argomenti importanti, ognuno dei quali corrisponde a un tipo di sezione in `confbridge.conf`. **bridge_profile** (una sezione `type=bridge`): qui si seleziona il numero massimo di partecipanti (`max_members`), la registrazione (`record_conference`), `video_mode` e molti altri parametri a livello di bridge.

Non ha senso riprodurre l'intero file di esempio qui, quindi vi fornirò un semplice esempio su come configurare un `bridge_profile` nel file `confbridge.conf`.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (una sezione `type=user`): qui definisci le opzioni specifiche per utente, come se l'utente è un amministratore (`admin=yes`), se parte in modalità silenziosa (`startmuted=yes`), musica in attesa, e molte altre opzioni per utente. Esempio:

```
[admin_user]
type=user
admin=yes
```

**menu** (a `type=menu` section): qui definisci la mappatura della tastiera (DTMF) per la conferenza — ad esempio quale tasto attiva/disattiva il mute, regola il volume o lascia la conferenza. Controlla il file `confbridge.conf.sample` per vedere tutte le azioni disponibili. Esempio:

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

Le opzioni del ponte conferenza possono essere passate dinamicamente nel dialplan usando la funzione CONFBRIDGE(). Vedi gli esempi sotto:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### Comandi di amministrazione di ConfBridge e migrazione da MeetMe

If you are coming from MeetMe, the admin functions you used through `MeetMeAdmin()` and the `a` (admin) option are now expressed through the **admin user profile** (`admin=yes`) plus the **menu** actions. An administrator who joins with an admin profile and a menu containing admin actions can lock the room, kick users, and mute participants live from the keypad. The relevant menu actions in `confbridge.conf` are:

- `admin_kick_last` -- espelli l'ultimo utente che si è unito
- `admin_toggle_mute_participants` -- silenzia/riattiva l'audio di tutti i partecipanti non amministratori
- `toggle_mute` -- silenzia/riattiva l'audio per te stesso
- `participant_count` -- annuncia il numero di partecipanti
- `leave_conference` -- esci dal bridge e continua nel dialplan

These replace the MeetMe `MeetMe()` option flags (`a`, `A`, `m`, `M`, `l`, `x`, …) and the `MeetMeAdmin()` commands (`k`, `K`, `L`, `M`, `N`, …). On a modern PJSIP install you won't be loading `app_meetme` at all; all conference configuration lives in `confbridge.conf`, and changes are applied with `module reload app_confbridge.so` (the ConfBridge logic lives in `app_confbridge`; there is no `res_confbridge` module).

### Esempio di ConfBridge

To create a conference room reachable at extension 500, in `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

Il primo chiamante che compone 500 crea la conferenza `101`; i chiamanti successivi vi si uniscono. I profili e i menu a cui si fa riferimento qui (`default_bridge`, `default_user`, `sample_user_menu`) sono definiti in `confbridge.conf`. Per richiedere un PIN, impostare `pin=` nel profilo utente; per rendere un partecipante amministratore della conferenza, assegnargli un profilo utente con `admin=yes`.

## Call Recording

Ci sono diversi modi per registrare una chiamata in Asterisk. È possibile utilizzare l'applicazione `MixMonitor()` per registrare le chiamate in modo semplice. (L'applicazione più vecchia `Monitor`, che registrava due file separati, è stata rimossa; utilizzare `MixMonitor` invece.)

### Using the MixMonitor application

L'applicazione `MixMonitor` registra l'audio nel canale corrente nel file specificato. Se il nome file è un percorso assoluto, utilizza quel percorso. Altrimenti, crea il file nella directory di monitoraggio configurata in asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

Registra una chiamata e mescola l'audio durante la registrazione. Sintassi: `MixMonitor(filename.extension[,options[,command]])`. Registra l'audio sul canale corrente nel file specificato. Opzioni valide:

- a - Aggiunge al file invece di sovrascriverlo.
- b - Salva l'audio nel file solo mentre il canale è collegato.
- Nota: non include le conferenze.
- v(<x>) - Regola il volume udibile di un fattore <x> (da -4 a 4)
- V(<x>) - Regola il volume parlato di un fattore <x> (da -4 a 4)
- W(<x>) - Regola sia i volumi udibili che parlati di un fattore <x> (da -4 a 4)
- <command> verrà eseguito quando la registrazione sarà terminata. Qualsiasi stringa che corrisponde a ^{X} sarà de‑escaped in ${X} e tutte le variabili saranno valutate in quel momento. La variabile MIXMONITOR_FILENAME conterrà il nome del file usato per la registrazione.

Una risorsa interessante è la funzione di registrazione a un tocco `automixmon`, che consente a una parte di digitare un codice DTMF (il campione `features.conf` suggerisce `*3`; non esiste un valore predefinito integrato, quindi è necessario impostarlo) durante una chiamata per avviare immediatamente (e disattivare) la registrazione. È basata su MixMonitor, quindi scrive un unico file misto. Esempio:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

Le opzioni `X` e `x` abilitano la funzione MixMonitor a tocco singolo per il chiamante e il chiamato rispettivamente. Poiché MixMonitor registra un unico file misto, non è necessario combinare successivamente i file IN/OUT separati (l'approccio vecchio `automon`/`Monitor`, che produceva due file per `soxmix`, è stato rimosso insieme all'applicazione `Monitor`).

Se non vuoi usare Set() prima dell'applicazione Dial(), puoi impostarlo nella sezione globals:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) has changed several times among versions 1.0, 1.2, and 1.4. In the latest version, MOH defaults to "FILE-BASED". In other words, Asterisk will supply the MOH files in formats such as g729, alaw, ulaw, and gsm. Thus, it is not necessary to transcode the music before sending it to the channel. This saves processor time, which is a welcomed modification for those working with production systems.

In older versions, MOH was usually provided by MP3 (it still can be configured that way). Providing MOH using MP3 obligates Asterisk to transcode, spending valuable CPU power in the process.

The new configuration file is shown below. Note that the default class now uses the native file format mode=files. All other modes are commented. Each section is a class. The only uncommented class at this point is default. If you want to have different classes for different files, you will need to create new sections (classes).

![Esempio di configurazione di musiconhold.conf, elencando le modalità MOH valide (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

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

Ora, per utilizzare la musica di attesa, impostare la classe MOH nei file di configurazione dei canali (chan_dahdi.conf, pjsip.conf, iax.conf, ecc.). Per gli endpoint PJSIP, impostare `moh_suggest` nella sezione endpoint di `pjsip.conf` (il nome dell'opzione legacy `musicclass` si applica a chan_dahdi e ad altri driver di canale, non a PJSIP). Le melodie freeplay installate sono ora in formato wav. Al momento dell'installazione, è possibile selezionare (usando make menuselect) i formati di file MOH disponibili. Se si desidera aggiungere nuovi file MOH, sarà necessario fornire i file nei formati richiesti. Per esempio:

In `/etc/asterisk/chan_dahdi.conf`, aggiungere la riga `musiconhold`.

```
[channels]
musiconhold=default
```

Quindi modifica `/etc/asterisk/musiconhold.conf` per definire quella classe:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

Nel dial plan, è possibile avviare la musica in attesa su un canale con `StartMusicOnHold` (e fermarla con `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

Per riprodurre musica in attesa per un tempo fisso come test rapido, usa l'applicazione `MusicOnHold` con una durata (in secondi):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## Mappature delle Applicazioni

Le mappature delle applicazioni consentono di aggiungere nuove funzionalità utilizzando la sezione `[applicationmap]` del file features.conf. Supponiamo che tu debba identificare il tipo di cliente a cui rispondi in un call center. Potresti creare una mappatura delle applicazioni per ogni tipo di cliente, che potrebbe contare il numero di clienti risposti per tipo.

## Summary

In this chapter you learned where Asterisk's PBX features live — some in the core, some in the dial plan, and some on the phone — and how the DTMF feature codes are mapped in the `[featuremap]` section of `features.conf`. You configured **call transfer** (blind and attended) and **call parking** (`res_parking.conf`, with the `k`/`K` Dial options and the `parkedcalls` lot), **call pickup** by group, and **conferencing** with **ConfBridge** (`confbridge.conf` bridge/user/menu profiles), which replaces the old MeetMe. You set up **one-touch recording** with MixMonitor (`automixmon`, the `X`/`x` Dial options, and `DYNAMIC_FEATURES`), configured **music on hold**, and saw how **application maps** let you bind your own dialplan logic to a DTMF sequence. With these building blocks you can deliver the everyday features users expect from a business PBX.

## Quiz

1. Quali affermazioni sono vere sul parcheggio delle chiamate?
   - A. Per impostazione predefinita, l'interno 800 è usato per il parcheggio delle chiamate.
   - B. Quando sei lontano dalla tua scrivania e ricevi una chiamata, puoi parcheggiarla; il sistema annuncia lo slot di parcheggio e lo componi da qualsiasi telefono per recuperare la chiamata.
   - C. Per impostazione predefinita, l'interno 700 parcheggia una chiamata, e le chiamate sono parcheggiate negli slot 701–720.
   - D. Componi 700 per recuperare una chiamata parcheggiata.
2. Per usare la funzione di call‑pickup, tutte le estensioni devono essere nello stesso ___. Per i canali DAHDI questo è configurato nel file ___.
3. Quando trasferisci una chiamata puoi scegliere tra un trasferimento ___, dove la destinazione non è consultata prima, e un trasferimento ___, dove parli con la destinazione prima di completarlo.
4. Per effettuare un trasferimento assistito (consultativo) usi la sequenza ___; per un trasferimento cieco usi ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. Per ospitare conferenze in Asterisk 22, usi l'applicazione ___.
6. In ConfBridge, un partecipante ottiene i privilegi di amministratore (espellere, silenziare altri, bloccare la stanza) impostando ___ nel suo profilo utente (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. Il formato migliore per la musica in attesa è MP3, perché utilizza pochissima potenza di elaborazione sul server Asterisk.
   - A. True
   - B. False
8. Per rispondere a una chiamata da un gruppo di call‑pickup specifico, devi appartenere al gruppo ___ corrispondente.
9. Puoi registrare una chiamata con l'applicazione MixMonitor() o con la funzione di registrazione a un tocco (`automixmon`). Nell'esempio `features.conf`, `automixmon` è mappato alla sequenza DTMF ___.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, quale opzione del profilo utente `confbridge.conf` fa entrare un partecipante in modalità silenziosa (può ascoltare la conferenza ma non è udibile finché non viene smutato)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
