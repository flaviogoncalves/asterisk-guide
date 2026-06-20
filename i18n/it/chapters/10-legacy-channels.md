# Legacy channels: analog, TDM & IAX2

In un mondo pure‑VoIP del 2026, i tipi di canale descritti in questo capitolo sono sempre più rari: la maggior parte delle nuove implementazioni utilizza trunk SIP e endpoint PJSIP su Ethernet, senza alcun hardware telefonico. Asterisk 22 supporta comunque la maggior parte di essi in modo completo. La connettività analogica (FXO/FXS) e digitale TDM (E1/T1/ISDN PRI/BRI) è fornita tramite DAHDI — lo stack di driver originariamente sviluppato da Digium, acquisito da Sangoma nel 2018, dopo che i precedenti driver Zaptel furono rinominati a seguito di una disputa sul marchio. La connettività server‑to‑server su IAX2 è fornita da `chan_iax2`, che è ancora distribuita e supportata ma ora è fermamente un protocollo legacy.

Questo capitolo raccoglie anche il materiale **legacy SIP**: il vecchio driver `chan_sip` e la sua configurazione `sip.conf` — rimossi in Asterisk 21 e assenti in Asterisk 22 — insieme a una guida completa per migrare un sistema `sip.conf` esistente a PJSIP. Se gestisci un negozio pure‑SIP su PJSIP senza schede telefoniche, senza trunk IAX2 e senza legacy `sip.conf` da convertire, puoi tranquillamente saltare questo capitolo.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Collegare Asterisk a linee analogiche e telefoni con interfacce FXO/FXS tramite DAHDI;
- Riconoscere la connettività digitale TDM (E1/T1, ISDN PRI/BRI) e come è configurata;
- Configurare IAX2 (`chan_iax2`) per trunk server‑to‑server e comprendere perché è ora legacy;
- Identificare il driver `chan_sip` ritirato e la sintassi `sip.conf` che potresti ancora incontrare; e
- Migrare un sistema `chan_sip`/`sip.conf` esistente a PJSIP.

## Analog channels (FXO/FXS)

As of Asterisk 22, DAHDI and analog telephony cards remain fully supported, and DAHDI still builds against current kernels. The majority of new deployments are nonetheless pure VoIP (SIP trunks, PJSIP), so analog/TDM hardware is now a niche choice — found mainly in legacy environments, rural PSTN connectivity, or regulated markets. Everything below still applies to those scenarios.

There are several ways to connect the public switched telephone network (PSTN). The best way depends on how the telephone company makes this connection available in your area. The simplest way is to use an analog line, similar to the line you use at home. In this section, we will show you how to configure analog cards from Sangoma™ (formerly Digium™) and Xorcom™.

### Objectives

By the end of this chapter you should be able to:

- Recognize the main telephony terms and acronyms;
- Understand when to use digital and analog circuits;
- Recognize the difference between FXS and FXO; and
- Configure Asterisk for FXS and FXO.

### Telephony basics

Most analog implementations use a pair of cooper lines named tip and ring. When a loop is closed, the phone receives the dial tone from the telecom switch (or the private PBX). The most frequently used signaling is loop-start; other, less common kinds of signaling including ground start, which is used in several countries. The three categories of signaling are:

- Supervision signaling
- Address signaling
- Information signaling

#### Supervision signaling

The main supervision signalings are on-hook, off-hook, and ringing.

- **On-Hook** – When a user puts the phone on the hook, the PBX interrupts and does not allow the electric current to pass. In this state, the circuit is named on-hook. In this position, only the ringer is active.
- **Off-Hook** – Before starting a phone call, the phone needs to pass to the off-hook state. Removing the handset from the hook closes the loop and indicates to the PBX that the user intends to make a call. Upon receiving this indication, the PBX generates a dial tone, indicating to the user that it is ready to accept the destination address (i.e., phone number).
- **Ringing** – When a user calls another phone, it generates a voltage to the ringer that warns the other user about a call being received. Signaling varies by country, with different tones for different countries.

You can personalize Asterisk tones to your country by modifying the indications.conf file. For example:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### Segnalazione Indirizzo

Puoi usare due tipi di segnalazione per comporre. Il primo e più comune è dual tone multi-frequency (dtmf) mentre l'altro è la composizione a impulsi (usata nei vecchi telefoni a disco). I telefoni hanno una tastiera per la composizione, e ogni tasto è associato a due frequenze: una alta e una bassa. Nel caso della segnalazione dtmf, la combinazione di questi toni indica quale cifra è stata premuta. MFC/R2 usa un tono multifrequenza diverso dal dtmf.

#### Segnalazione delle informazioni

Il segnalamento delle informazioni mostra l'avanzamento della chiamata e i diversi eventi.

- Segnale di composizione
- Tono occupato
- Tono di ritorno
- Congestione
- Numero non valido
- Tono di conferma

### Interfacce PSTN

Come nel caso dei vecchi PBX, è spesso necessario collegare l'Asterisk PBX al PSTN. Qui ti mostreremo come farlo. Di solito hai tre opzioni per le linee telefoniche.

- Analog: La forma più comune per abitazioni e piccole imprese, solitamente fornita con una coppia metallica di linee in rame.  
- Digital: Utilizzata quando sono necessarie molte linee. Una linea digitale è solitamente fornita da un CSU/DSU o da un multiplexer in fibra. Il connettore dell'utente finale è solitamente un RJ45. In alcuni paesi, le linee E1 sono fornite usando due connettori coassiali BNC; in questo caso sarà necessario un adattatore a “balloon” per collegare la presa RJ45 alla scheda telefonica.  
- SIP: Questa opzione è stata sviluppata di recente. La linea telefonica è fornita tramite una connessione dati con segnalazione SIP (VoIP). È una buona opzione da usare con Asterisk poiché non sarà necessario acquistare una scheda telefonica. Le chiamate telefoniche saranno consegnate direttamente alla porta Ethernet. Un altro vantaggio è che potresti riuscire a liberare risorse dalla CPU evitando la transcodifica dei codec.

### Interfacce analogiche FXS, FXO e E&M interfaces

Sono disponibili diversi tipi di interfacce analogiche. È fondamentale comprendere le differenze tra queste interfacce per imparare come collegarsi alla rete telefonica così come ad altri PBX. Qui vi mostreremo l'interfaccia E&M. Sebbene non sia attualmente disponibile per Asterisk e sia stata interrotta da diversi fornitori, potreste trovare router e PBX con questo tipo di interfaccia, quindi è meglio sapere con cosa si ha a che fare.

#### Interfacce Foreign eXchange (FX) Interfaces

Le interfacce FX sono analogiche. Il termine “Foreign eXchange” viene applicato ai trunk di accesso verso un centralino PSTN (CO). Foreign eXchange Office (FXO)

![Asterisk tra un telefono analogico (FXS) e la linea telefonica (FXO): il lato FXS fornisce tono di chiamata e segnale di squillo al telefono, mentre il lato FXO preleva il tono di chiamata dall'ufficio centrale.](../images/10-legacy-fig01.png)

L'interfaccia FXO è usata per collegarsi a un centralino (CO) o all'estensione di un altro PBX. Comunica direttamente con una linea telefonica proveniente dalla PSTN. Un'altra opzione è collegare l'interfaccia FXO a un PBX esistente, consentendo la comunicazione tra Asterisk e il PBX legacy. Collegare Asterisk a una porta PBX e fornire un'estensione remota tramite VoIP è spesso definito come un'estensione off‑promises (OPX). Un'interfaccia FXO riceve un segnale di tono di chiamata. Foreign eXchange Station (FXS) L'interfaccia FXS alimenta un telefono analogico, un modem o un fax. L'FXS fornisce il tono di chiamata e l'alimentazione per il telefono.

#### Segnalazione del trunk

- Loop-Start
- Ground-Start
- Kewlstart

L'uso del segnalamento kewlstart in Asterisk è quasi predefinito. Kewlstart non è un segnalamento di per sé, ma aggiunge intelligenza al circuito monitorando ciò che accade dall'altra parte. Kewlstart si basa su loop-start. La maggior parte degli switch non supporta questa funzionalità, che è usata per ottenere la notifica di hang‑up.

- Loopstart: Usato nella maggior parte delle linee analogiche, consente al telefono di indicare “on-hook” e “off-hook” e allo switch di indicare “ring” e “no-ring”. Probabilmente è quello che la maggior parte delle persone ha a casa. Il nome deriva dal fatto che la linea è sempre aperta. Quando chiudi il loop, lo switch ti fornisce un segnale di tono di chiamata. Una chiamata in arrivo è segnalata da una tensione di squillo di 100V sul paio aperto.

![Asterisk che opera come gateway VoIP: una porta FXO si collega a un’estensione PBX legacy mentre un Asterisk remoto consegna quella linea a un telefono analogico via IP attraverso una porta FXS (un’estensione fuori sede, o OPX).](../images/10-legacy-fig02.png)

- Groundstart: Simile a Loopstart. Quando si desidera effettuare una chiamata, un lato della linea è cortocircuitato. Quando lo switch identifica questo stato, inverte la tensione attraverso la coppia aperta e quindi il loop si chiude. Di conseguenza, la linea diventa occupata prima di essere offerta al chiamante.
- Kewlstart: Aggiunge intelligenza ai circuiti, consentendo il monitoraggio dell'altra estremità. Kewlstart incorpora molti vantaggi del loop-start.

### Configurazione dei canali telefonici Asterisk

Per configurare una scheda di interfaccia telefonica, sono necessari diversi passaggi. In questo capitolo, mostreremo tre dei scenari più comuni:

- Connessione analogica tramite FXS
- Connessione analogica tramite FXO
- Connessione di un Astribank™ con interfacce FXS e FXO

### Procedura di configurazione (valida in entrambi i casi)

Prima di scegliere l'hardware per Asterisk, dovresti considerare il numero di chiamate simultanee, i servizi e i codec che verranno installati e abilitati. Asterisk è un'applicazione ad alta intensità di CPU, motivo per cui consigliamo una macchina dedicata per Asterisk. Il numero di schede di interfaccia installate nel computer è limitato dal numero di slot e interruzioni disponibili. È preferibile installare una singola scheda con otto interfacce vocali piuttosto che due schede con quattro. Un'altra opzione è utilizzare una bank di canali USB, come la Xorcom Astribank. Recentemente, alcuni produttori (ad es., CIANET) hanno iniziato a produrre bank di canali TDMoE, rendendo ancora più semplice collegare decine di interfacce analogiche.

![Un Xorcom Astribank: un banco canali USB da 19 pollici rack-mount che espone decine di porte FXS/FXO (qui un'unità da 32 porte) senza consumare slot PCI nell'host.](../images/10-legacy-fig03.png)

#### Esempio 1: Installazione di un FXO, un FXS

In questo esempio, utilizzeremo una scheda di interfaccia telefonica Sangoma TDM400 (precedentemente venduta come Digium TDM400) con un modulo FXS e un modulo FXO. I passaggi richiesti sono elencati di seguito:

1. Installa la scheda analogica FXS, FXO o entrambe.  
2. Configura il file `/etc/dahdi/system.conf` (precedentemente `/etc/zaptel.conf`).  
3. Genera i file di configurazione usando `dahdi_genconf`.  
4. Carica il driver per l'interfaccia DAHDI.  
5. Esegui `dahdi_test` per verificare le perdite di interrupt.  
6. Esegui `dahdi_cfg` per configurare il driver.  
7. Configura il canale DAHDI nel file `chan_dahdi.conf`, quindi carica Asterisk.

##### Passo 1: Installa la scheda TDM400

La scheda TDM404P contiene moduli FXS e FXO. Collegare i moduli FXS (S110M, verde) e FXO (X100M, rosso). Se si utilizzano moduli FXS, collegare la scheda direttamente all'alimentazione usando un connettore molex. Si prega di indossare protezione elettrostatica prima di maneggiare le schede di interfaccia per evitare danni all'hardware. Le schede analogiche Sangoma (ex Digium) supportano anche un modulo hardware di cancellazione eco VPMADT032.

##### Passo 2: Genera la configurazione con dahdi_genconf

La buona notizia sulla configurazione è la nuova utility `dahdi_genconf`, che rileva automaticamente e genera la configurazione per le interfacce DAHDI. L'utility genera due file:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (with the `users` option)
- All these files use the option `chan_dahdi full`

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![Una scheda analogica Sangoma/Digium TDM404P: fino a quattro moduli FXS o FXO si collegano alle porte numerate, con una scheda figlia opzionale per la cancellazione dell'eco hardware e un connettore di alimentazione dedicato da 12 V per i moduli FXS.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

Il file `genconf_parameters` ti permette di personalizzare la tua configurazione. I parametri più importanti per le linee analogiche sono:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

Warning: è necessario configurare almeno l'algoritmo di cancellazione dell'eco per i canali. Il parametro base_exten definisce il piano di composizione di base per le estensioni FXS. In questo caso, il primo canale FXS riceverà il numero di estensione 4000, il secondo 4001, e così via. Il contesto in cui le linee (context_phones) e i trunk (context_lines) sono creati è molto importante. Dopo aver generato i file, dovresti includere il file `/etc/asterisk/dahdi-channels.conf` nel file `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: La segnalazione analogica è un po' confusa; è sempre l'inverso della scheda. Le schede FXS sono segnalate con FXO mentre le schede FXO sono segnalate con FXS. Asterisk comunica con questi dispositivi come se fosse dall'altro lato.

##### Step 3: Load kernel drivers

Ora devi caricare il modulo chan_dahdi e il driver kernel della scheda correlato. Usa dahdi_hardware per rilevare la tua scheda e il nome del driver. Per esempio:

| Card | Driver | Description |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - PCI 3.3V |
| TE405P | wct4xxp | 4xE1/T1 - PCI 5V |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### Passo 4: Usa l'utilità dahdi_test

Un'utilità importante è dahdi_test, che viene usata per verificare le perdite di interrupt nella scheda DAHDI. I problemi di qualità audio sono spesso legati a conflitti di interrupt. Per verificare che la tua scheda DAHDI non condivida un interrupt con altre schede, usa il comando seguente:

```
#cat /proc/interrupts
```

Puoi verificare il numero di interruzioni perse usando l'utilità **dahdi_test** compilata con le schede DAHDI. Un valore inferiore al 99,987 % indica possibili problemi.

##### Step 5: Usa l'utilità **dahdi_cfg** per configurare il driver

DAHDI ha un sistema insolito per il caricamento dei driver. Prima configura il file **/etc/dahdi/system.conf**, quindi applica tali configurazioni al driver DAHDI usando **dahdi_cfg**. In questo caso, **dahdi_cfg** viene usato per configurare il signaling per le interfacce FX. Per vedere i risultati, puoi aggiungere “-vvvvv” al comando per ottenere output dettagliato.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

If the channels were loaded successfully, you will see an output similar to the one shown above. Users often incorrectly configure chan_dahdi.conf with inverted signaling between channels. If this happens, you will see a message like the one shown below:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After aver configurato con successo l'hardware, puoi procedere alla configurazione di Asterisk.

##### Step 6: Configura il file /etc/asterisk/chan_dahdi.conf

Può sembrare strano, ma dopo aver configurato il file /etc/dahdi/system.conf, hai configurato la scheda stessa. DAHDI può essere usato per altri scopi, come routing e SS7. Per usarlo con Asterisk, devi configurare i canali DAHDI di Asterisk. Ogni canale in Asterisk deve essere definito; i canali SIP/PJSIP sono definiti in pjsip.conf (nota: chan_sip e sip.conf sono stati rimossi in Asterisk 21) mentre i canali TDM sono definiti in chan_dahdi.conf. Questo crea i canali logici TDM da utilizzare nel tuo dial plan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Configuration options

Several options are available in the chan_dahdi.conf file. A description of all options would be boring and counterproductive; instead, we will focus on the main option groups available for easy understanding.

#### General options (channel independent)

These options work for any channel: context: Defines the incoming context.

```
context=default
```

channel: Definisce canale o intervallo di canali. Ogni definizione di canale erediterà le opzioni definite prima della dichiarazione. I canali possono essere identificati individualmente o nella stessa riga mediante separazione con virgola. Gli intervalli possono essere definiti usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Consente di gestire i canali come un gruppo. Se componi un numero di gruppo invece di un numero di canale, viene utilizzato il primo canale disponibile. Se i canali sono telefoni, quando chiami un gruppo, tutti i telefoni squilleranno simultaneamente. Con le virgole, puoi specificare più di un gruppo per lo stesso canale.

```
group=1
group=3,5
```

language: Attiva l'internazionalizzazione e configura una lingua. Questa funzionalità configurerà i messaggi di sistema per una lingua specifica. L'inglese è l'unica lingua con prompt completi disponibili tramite installazione standard. musiconhold: Seleziona la classe di musica di attesa.

#### Opzioni Caller ID

Esistono molte opzioni per il callerid. Alcune possono essere disabilitate, sebbene la maggior parte sia abilitata per impostazione predefinita. usecallerid: Abilita o disabilita la trasmissione del callerid per i canali successivi (Yes/No). Nota: Se il tuo sistema riceve due squilli prima di rispondere, prova a disabilitare questa funzionalità. Dovrebbe rispondere immediatamente. hidecallerid: Definisce se nascondere o meno il callerid in uscita (Yes/No). callerid: Configura una stringa callerid per un canale specifico. Il caller può essere configurato con asreceived. Questo è usato principalmente nelle interfacce trunk per indicare il callerid in ingresso.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: Supporta il callerid durante la chiamata in attesa. useincomingcalleridondahditransfer: Usa il callerid in ingresso in un trasferimento.

#### Call Waiting

Asterisk supporta la chiamata in attesa nei canali FXS. L'utente riceverà un tono di attesa se qualcuno prova a chiamare l'interno. Per abilitare la chiamata in attesa:

```
callwaiting=yes
```

Per supportare il callerid in chiamata in attesa:

```
callwaitingcallerid=yes
```

#### Opzioni di qualità audio

Regolare la cancellazione dell'eco è metà tecnica, metà arte. Queste opzioni regolano alcuni parametri di Asterisk che influenzano la qualità audio nei canali DAHDI. Possono aiutare a migliorare la qualità audio nelle interfacce analogiche.

#### L'utilità fxotune

fxotune è un'utilità usata per affinare alcuni parametri per i moduli FXO. Questa messa a punto è necessaria per correggere il disallineamento di impedenza causato dall'ibrido. L'utilità ha tre modalità operative:

- Detection (-i): rileva e corregge i canali FXO esistenti e salva la configurazione in

```
fxotune.conf
```

- Dump mode (-d): genera i file di forma d'onda in fxotune_dump.vals
- Startup mode (-s): legge il file fxotune.conf e lo applica ai moduli FXO

È importante capire che dovrai inserire l'istruzione fxotune –s nel caricamento del sistema prima di avviare Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Echo cancellation

La maggior parte degli algoritmi di cancellazione dell'eco funziona generando più copie del segnale ricevuto, ognuna delle quali è ritardata di una quantità specifica di tempo. Il numero di tap del filtro determina la dimensione del ritardo dell'eco che deve essere cancellato. Queste copie ritardate vengono quindi regolate e sottratte dal segnale ricevuto. Il trucco consiste nel regolare solo il segnale ritardato per rimuovere l'eco senza utilizzare troppi cicli CPU. Dal punto di vista dell'utente, è importante scegliere un algoritmo di cancellazione dell'eco appropriato. Il valore predefinito è MG2; tuttavia, sono disponibili altre due opzioni: l'High Performance Echo Cancellation (HPEC) di Sangoma (ex Digium) e la cancellazione dell'eco open‑source (OSLEC) sviluppata da David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) è stato integrato nel kernel Linux — risiede nell'area `drivers/staging/echo` del kernel — e DAHDI è compilato contro di esso anziché fornire un download separato. Per cambiare l'algoritmo di cancellazione dell'eco, impostare il parametro `echo_can` in `/etc/dahdi/system.conf`. Per esempio:

```
echo_can=oslec
```

La cancellazione dell'eco in Asterisk è controllata da tre parametri nel file /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: Disabilita o abilita la cancellazione dell'eco. Si consiglia di mantenere questa funzione attiva. Accetta "yes" o il numero di tap. (Explanation: How does echo canceling work? Most echo canceling algorithms operate by generating multiple copies of a received signal, with each being delayed by a small interval. This little flow is called a "tap". The number of taps determines the echo delay that can be cancelled. These copies are delayed, adjusted, and subtracted from the original signal. The trick is to adjust the delayed signal exactly to what is necessary to remove the echo.)
- **echocancelwhenbridged**: Abilita o disabilita il cancellatore di eco durante una chiamata TDM pura. Di solito non è necessario.
- **rxgain**: Regola il guadagno di ricezione audio per aumentare o diminuire il volume di ricezione (-100% to 100%).
- **txgain**: Regola il guadagno di trasmissione audio per aumentare o diminuire il volume di trasmissione (-100% to 100%).

For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opzioni di fatturazione

Queste opzioni modificano il modo in cui le informazioni delle chiamate vengono registrate nel database dei record dettagliati delle chiamate (CDR). amaflags: Configura i flag AMA che influenzano la categorizzazione del CDR. Accetta i seguenti valori:

- billing
- documentation
- omit
- default

accountcode: Configura un codice di conto per un canale specifico. Può contenere qualsiasi valore alfanumerico—di solito il dipartimento o il nome utente.

```
accountcode=finance
amaflags=billing
```

### Call progress options

Questi elementi sono usati per acquisire informazioni sullo stato della chiamata. Nelle interfacce pubbliche, può essere utile rilevare il progresso della chiamata e determinare se è stata risposta o occupata. Il rilevamento di occupato è altamente sperimentale e regolato da parametri specifici.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

Questi parametri (sopra) specificano se l'interfaccia cercherà di rilevare il tono di occupato, quanti toni saranno usati per il rilevamento riuscito e qual è il modello di occupato. Il rilevamento di occupato è in gran parte sperimentale, e alcuni parametri aggiuntivi possono essere modificati nel Makefile. Per rilevare la risposta di una chiamata, che è essenziale per una fatturazione precisa, è possibile utilizzare l'inversione di polarità per segnalare l'esatto momento di risposta. Questo è importante se si prevede di addebitare la chiamata o semplicemente si desidera avere una fatturazione precisa per confronto. Di solito è necessario contattare l'operatore telefonico per richiedere questo servizio.

```
answeronpolarityswitch=yes
```

In alcuni paesi, è possibile rilevare l'uscita dalla chiamata usando l'inversione di polarità.

```
hanguponpolarityswitch=yes
```

#### Opzioni per i telefoni

Queste opzioni sono utilizzate per i telefoni collegati alle interfacce FXS. Tutte le funzionalità fornite ai telefoni analogici collegati direttamente alle interfacce DAHDI sono controllate da Asterisk.

- **adsi** (Analog Display Services Interface): È un insieme di standard telecom utilizzati da alcuni operatori per offrire servizi come l'acquisto di biglietti.
- **cancallforward**: Abilita o disabilita il trasferimento di chiamata (*72 per abilitare e *73 per disabilitare).
- **calleridcallwaiting**: Abilita il callerid ricevuto durante l'indicazione di chiamata in attesa (Sì/No).
- **immediate**: In modalità immediata, invece di fornire un segnale di composizione, il canale salta immediatamente all'estensione "s" nel contesto definito. Questo è usato per creare linee dirette.
- **threewaycalling**: Abilita o disabilita la conferenza a tre vie.
- **mailbox**: Avvisa l'utente della presenza di mess

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### Formato del canale DAHDI

I canali DAHDI usano il seguente formato nel dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Ad esempio:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## Canali digitali (E1/T1/PRI / TDM)

As of Asterisk 22, DAHDI and libpri remain fully supported, but TDM digital trunks (E1/T1/ISDN PRI) are increasingly replaced by SIP trunks in new deployments. This section remains fully applicable where TDM connectivity is required; in greenfield environments, SIP trunking (Chapter 3) usually delivers the same channel density without telephony hardware.

I canali digitali sono estremamente comuni, quindi dovrai imparare come implementare questi canali se vuoi concentrarti su grandi clienti. Quando il numero di canali è elevato—di solito più di 8—è piuttosto comune usare interfacce digitali come T1/E1/J1. T1 è molto comune negli Stati Uniti, mentre E1 è comune in Europa e J1 in Giappone. Questo tipo di canali consente una buona densità di circuiti—24 per canale T1 e 30 per canali E1.

In Latin America, China, and Africa, it is common to use a type of channel associated signaling (CAS) known as MFC/R2. This chapter will examine how to implement MFC/R2 using the library OpenR2. In the US and Europe, Integrated Services Digital Networks (ISDN) PRI is the most common signaling. The chapter will also discuss ISDN Basic Rate Interface (BRI), which is very common in Europe in mid-range applications.

Tutti gli esempi nel libro si concentrano sui canali DAHDI. Alcune schede sono implementate usando canali proprietari, quindi si prega di consultare il produttore per ulteriori dettagli su come configurare la scheda specifica.

### Obiettivi

Entro la fine di questo capitolo sarai in grado di:

- Riconoscere i termini principali usati nella telefonia digitale
- Differenziare la segnalazione CAS e CCS
- Differenziare la segnalazione R2 e ISDN
- Configurare le interfacce con segnalazione ISDN
- Configurare le interfacce con segnalazione R2

### Linee digitali E1/T1

Le linee digitali E1/T1 sono un'opzione ogni volta che è necessario implementare un gran numero di canali. Un singolo circuito E1 è in grado di gestire 30 chiamate simultanee e può includere funzionalità come direct inward dial (DID), Caller ID (identificazione del chiamante) e segnalazione avanzata. La linea E1/T1 può arrivare alla tua azienda in diversi modi, utilizzando coppia intrecciata, fibra e microonde, a seconda del tuo paese. Le linee digitali vengono consegnate alla tua azienda tramite UTP, fibra o microonde. Modem e multiplexor (MUX) sono usati per fornire la linea fisica. La connessione a una linea T1 è sempre basata su un connettore RJ45. Tuttavia, le linee E1 possono essere fornite anche utilizzando BNC. È molto importante conoscere in anticipo il tipo di connettore che riceverai, soprattutto per le linee E1. Di solito tutto l'equipaggiamento fino al RJ45 è fornito dal TELCO.

![Come vengono provisionati i circuiti E1/T1: il provider può fornire il trunk su rame UTP (modem HDSL per E1, o connessione diretta su scheda per T1), su fibra ottica tramite un multiplexer ottico, o su un collegamento radio a microonde.](../images/10-legacy-fig05.png)

![UTP o BNC? La maggior parte delle schede digitali utilizza connettori RJ45 (UTP), ma alcune linee E1 sono fornite su cavo coassiale BNC doppio; in tal caso è necessario un balun per adattare la coppia coassiale al jack RJ45 della scheda.](../images/10-legacy-fig06.png)

#### Come viene convertita la voce in bit?

Il segnale analogico viene campionato 8.000 volte al secondo per creare una versione digitale della voce analogica. Questa codifica è nota come modulazione a codice di impulso (PCM). Negli Stati Uniti e in Giappone, il segnale è codificato usando la legge (in Asterisk, indicata come ulaw). Nel resto del mondo, la codifica è alaw.

![Modulazione a codice di impulsi (PCM): il segnale vocale analogico a 4 kHz viene campionato 8 000 volte al secondo (Nyquist) e codificato in un flusso digitale di bit a 64 Kbps.](../images/10-legacy-fig07.png)

#### Multiplexing a Divisione di Tempo

Le linee analogiche hanno senso quando hai bisogno di solo pochi canali. Quando si utilizza il multiplexing a divisione di tempo (TDM), è possibile inserire più canali in un'unica connessione dati. Quando desideri un gran numero di circuiti, la compagnia telefonica di solito ti fornirà un digital trunk, che è un circuito dati in cui la voce viene trasportata in formato digitale usando PCM. Ogni timeslot utilizza 64 Kbps di larghezza di banda per trasportare un singolo canale vocale.

![Multiplexing a divisione di tempo in E1 e T1: un frame E1 trasporta 32 timeslot a 2048 Kbps (DS0 #0 per la sincronizzazione del frame, DS0 #16 per il segnalamento), mentre un frame T1 trasporta 24 timeslot a 1544 Kbps usando un bit per la sincronizzazione e uno schema di bit rubati per il segnalamento.](../images/10-legacy-fig08.png)

In gli Stati Uniti, il trunk digitale più comune è il T1, che dispone di 24 linee disponibili; in Europa e America Latina, i trunk E1 hanno 30 linee. Alcune aziende offrono un T1/E1 frazionario con meno canali. **Robbed bit signaling** A volte un trunk T1 utilizza uno schema di robbed bit in cui un bit viene preso in prestito per il segnalamento. Nei trunk T1, il canale dati/voce viene trasmesso a 56 Kbps su ogni timeslot. Come si può osservare, quando si utilizza il robbed bit, il circuito T1 non perde due slot per sincronizzazione e segnalamento.

#### Codice di linea T1/E1

T1 e E1 sono in realtà circuiti dati e hanno una codifica dei dati che determina il modo in cui i bit vengono interpretati. Per gli E1, il codice di linea più comune è HDB3 per il livello 1 e CCS per il livello 2. Il modo più semplice per sapere come è configurato il tuo trunk digitale è chiedere al TELCO queste informazioni. Avrai bisogno di queste informazioni per configurare il file /etc/dahdi/system.conf.

#### Segnalazione T1/E1

È importante capire che le linee T1/E1 possono essere fornite usando diversi tipi di segnalazione, come:

- T1 con segnalazione robbed bit
- T1 con segnalazione ISDN
- E1 con MFC/R2 (CAS - Channel Associated Signaling)
- E1 con segnalazione ISDN

L'ISDN è spesso usato in Europa e negli Stati Uniti. È una rete vocale digitale, standardizzata dall'International Telecommunications Union (ITU) nel 1984. L'ISDN fornisce due tipi di canali:

- Canali di trasporto
  - Voce
  - Dati
- Canali dati
  - Segnalazione fuori banda
  - Segnalazione LAPD
  - Q.931

Di solito, una linea ISDN è fornita utilizzando due mezzi fisici:

- Interfaccia a tasso base (BRI)
  - Conosciuta come 2B+D
  - Due canali di trasporto (64K) e un canale dati (16K)
  - Utilizza una coppia di cavi di rame con 148Kbps.
- Interfaccia a tasso primario (PRI)
  - Fornita tramite un trunk T1/E1
  - 23B+D per i T1
  - 30B+D per gli E1

Sometimes, E1 circuits use a CAS signaling scheme called MFC/R2, which was defined by the ITU as a standard known as Q.421/Q441. This is frequently found in Latin America and Asia. Several telephony companies in these countries use customized variants of MFC/R2. Hence, you will need to know the correct country variation in order to make it work.

### ISDN BRI

I canali che utilizzano la segnalazione ISDN BRI sono molto popolari in Europa. La maggior parte delle schede ISDN BRI per Asterisk supporta un'interfaccia S/T con capacità NT e TE. La connessione TE (terminal) è quella usata per collegarsi al TELCO o ad altri PBX configurati come network termination (NT). L'NT è utilizzato per collegare telefoni e PBX configurati come TE. ISDN BRI fornisce due canali dati/voce e un canale di segnalazione. Le schede ISDN BRI sono disponibili da diversi fornitori di schede di interfaccia per Asterisk.

### Scegliere una scheda telefonica per il tuo server Asterisk

Esistono diversi produttori di schede digitali compatibili con Asterisk. La scelta di una scheda dipende da alcuni dei seguenti fattori:

#### Bus dati

Ci sono diversi tipi di bus nel tuo PC. È molto importante avere la scheda giusta per il tuo server. La seguente panoramica descrive le schede più comunemente usate:

- 32 Bits PCI 5V found in most computers, including desktops
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 32/64 bits PCI 3.3V, basically found in servers
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express found on desktops and servers
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

Queste famiglie di schede hanno avuto origine da Digium, che Sangoma ha acquisito nel 2018; ora sono vendute e supportate sotto il marchio Sangoma. Molti dei vecchi SKU elencati qui sono stati interrotti, quindi verifica la disponibilità dei modelli attuali su www.sangoma.com prima dell'acquisto.

- MiniPCI trovata su sistemi embedded
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), and B400M(ISDN BRI)
- USB 2.0 trovata nella maggior parte dei PC moderni. Le soluzioni basate su USB consentono un'elevata densità di canali analogici e digitali. Questo bus supporta 480 Mbps e ogni canale vocale occupa 64 Kbps. Quando si utilizzano hub USB, è possibile raggiungere densità fino a mille porte analogiche in una singola porta.
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet. Il più grande vantaggio di Ethernet è permettere alla scheda di essere collegata a più di un server. Le soluzioni ad alta disponibilità sono solitamente l'applicazione principale per questi dispositivi. Il punto di forza di questa soluzione è l'uso di server senza slot PCI liberi o server blade.
  - Redfone FoneBridge (up to four E1 circuits)

### Utilizzo della cancellazione dell'eco hardware

L'eliminazione dell'eco hardware riduce il carico sulla CPU host. Per le schede con più di una singola interfaccia E1, l'eliminazione dell'eco hardware può aiutare ad alleviare il tuo processore. I nuovi cancellatori dell'eco software migliorati, come l'OSLEC, stanno riducendo la necessità di un cancellatore dell'eco hardware. Per scegliere tra cancellatori dell'eco hardware e software, dovresti considerare la quantità di potenza di elaborazione disponibile nel tuo server e il numero di circuiti E1. Un processo di cancellazione dell'eco può utilizzare fino a nove MIPS (milioni di istruzioni al secondo) per canale vocale con 128 tap di ampiezza usando OSLEC (Reference: Xorcom Ltd.). Se consideri 1 CPU cycle per each instruction (which is not always correct based on the processor and software implementation itself), we are speaking of 1.080 Ghz for four E1s.

#### Tipo di segnalazione

Selezionare il tipo di segnalazione (ad es., T1 CAS, T1 PRI, E1 CAS R2 o E1 CAS ISDN) non è un compito semplice. Dipende davvero da ciò che è disponibile nella tua zona e a quale prezzo. Il Common Channel Signaling (CCS) è spesso migliore del channel associated signaling (CAS). Tuttavia, spesso non è disponibile. Negli Stati Uniti, di solito puoi scegliere, poiché la maggior parte dei TELCOS offre T1 CAS per gli utenti normali e T1 PRI per gli utenti avanzati (ad es., call center). In America Latina, l’E1 CAS R2 è diffuso, ma l’ISDN PRI è disponibile in alcune città.

![L'architettura software DAHDI: Asterisk comunica con il driver di canale `chan_dahdi`, che a sua volta carica le librerie di protocollo libpri (ISDN), libopenr2 (MFC/R2) e libss7 (SS7); queste si trovano sopra l'interfaccia `/dev/dahdi`, il driver kernel DAHDI e il driver kernel dell'interfaccia specifica per la scheda.](../images/10-legacy-fig09.png)

Implementare R2 è necessario per installare una libreria nota come OpenR2 (www.libopenr2.org), sviluppata da Moises Silva, e per patchare Asterisk prima dell'installazione—una procedura semplice mostrata più avanti in questo capitolo. La libreria ha superato numerosi test ed è in produzione in diversi dei nostri clienti. ISDN è, a mio avviso, sempre la scelta migliore, se disponibile. Alcuni provider possono avere accesso al signaling system 7 (SS7), che è un segnale CCS disponibile tra le compagnie telefoniche. Sono disponibili soluzioni proprietarie e open source per SS7. La libreria libss7 è usata per supportare SS7 su Asterisk.

### Configurazione dei canali telefonici Asterisk

Configurare una scheda di interfaccia telefonica richiede diversi passaggi necessari. In questo capitolo, mostreremo tre dei scenari più comuni:

- Connessione digitale usando ISDN PRI
- Connessione digitale usando ISDN BRI
- Connessione digitale usando MFC/R2

Ci sono due modi per configurare i canali DAHDI. Il primo è configurarlo manualmente con il pieno controllo di tutti i parametri. Il secondo modo è utilizzare l'utilità dahdi_genconf per rilevare e configurare le schede.

#### Rilevamento e configurazione automatici

Grazie al team di sviluppo DAHDI, ora abbiamo il rilevamento e la configurazione automatici delle schede. Passo 1: Per generare la configurazione automaticamente, usa l'utilità dahdi_genconf, che rileverà la scheda e genererà i file /etc/dahdi/system.conf e dahdi-channels.conf.

```
dahdi_genconf
```

Passo 2: Nell'ultima riga del file chan_dahdi.conf, includi il file dahdi-channels.conf

```
#include dahdi_channels.conf
```

Passo 3: Commenta tutti i moduli inutilizzati nel file modules o usa semplicemente:

```
dahdi_genconf modules
```

#### Configurazione manuale

Un'altra opzione è configurare le interfacce manualmente. Di seguito sono riportati alcuni esempi di configurazione per i canali DAHDI.

##### Esempio #1 – Due canali T1/ E1 che utilizzano ISDN

Passaggi richiesti:

1. Installazione TE205P o TE210P
2. `/etc/dahdi/system.conf` file configuration
3. Caricamento driver DAHDI
4. `dahdi_test` utility
5. `dahdi_cfg` utility
6. `chan_dahdi.conf` file configuration
7. Caricamento e test di Asterisk

Passo 1: Installazione TE205P. Prima di installare il TE205P, è importante comprendere le differenze tra le schede TE205P e TE210P. La scheda TE210P utilizza un bus a 64‑bit alimentato a 3,3 V presente quasi esclusivamente nelle schede madri dei server. Fate attenzione se specificate questa scheda di interfaccia; assicuratevi che l’hardware supporti un bus a 64‑bit, 3,3 V. La scheda TE205P utilizza un PCI a 5 V, che si trova spesso nei computer desktop. Abbiamo scelto la scheda di interfaccia TE205P con due span per questo esempio perché è più semplice ridurla a una scheda a singolo span o espanderla a una scheda a quattro span. Queste schede sono ora vendute sotto il marchio Sangoma (ex Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

La configurazione delle schede digitali TDM è un po' diversa da quella delle loro controparti analogiche.  
Prima, dovremo configurare gli span della scheda e poi i canali.  
Gli span sono numerati sequenzialmente in base all'ordine di riconoscimento delle schede.  
In altre parole, se hai più di una scheda di interfaccia, è difficile sapere a quale span appartiene ciascuna.  
Usa dahdi_hardware per verificare quale hardware è installato su ogni span.  
Esempio #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

# Esempio #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

Esempio #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

Passo 3: Caricamento dei driver del kernel  
Verifica quale driver è necessario installare usando dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

Per caricare usa:

```
modprobe dahdi
modprobe wct2xxp
```

Passo 4: usando dahdi_test, controlla gli interrupt mancanti

Puoi verificare il numero di interruzioni perse usando l'utilità dahdi_test compilata con le schede DAHDI. Un valore inferiore al 99,987% indica possibili problemi. Troverai dahdi_test in

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

Step 5: Utilizzo dell'utilità dahdi_cfg

Questo è l'output corretto per dahdi_cfg per uno span E1 frazionario (15 porte) e due porte FXO.

```
#./dahdi_cfg -vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

Passo 6: Configurazione di DAHDI nel file /etc/asterisk/chan_dahdi.conf Esempio #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

Esempio #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

Esempio #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Usa `signaling=bri_cpe_ptmp` per BRI point‑to‑multipoint. Attualmente, il BRI point‑to‑multipoint non è supportato in modalità NT.

#### Caricamento dei driver del kernel

Dopo aver configurato i driver, è sufficiente riavviare il server. Se hai installato DAHDI con `make config`, non dovrai fare nulla di extra. Il driver del kernel verrà caricato e configurato automaticamente. Tuttavia, a volte è utile caricare e scaricare i driver manualmente. Esempio:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

Il primo comando carica il driver e il secondo, dahdi_cfg, applica la configurazione al driver del kernel.

### Risoluzione dei problemi

A volte le cose non funzionano al primo tentativo. Controlliamo alcune risorse per la risoluzione dei problemi di DAHDI. Passo 1: Verificare se la scheda è riconosciuta dal sistema operativo. Le schede Sangoma/Digium sono solitamente riconosciute come modem ISDN.

```
lspci -v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

Step 2: Verifica se il driver del kernel si sta caricando correttamente usando:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Passo 3: Verifica lo stato degli allarmi relativi al livello fisico della connessione. Per verificare il livello fisico della connessione E1, puoi utilizzare il seguente comando CLI di Asterisk.

```
dahdi show status
```

Le segnalazioni di allarme indicano problemi con la porta: Allarme rosso: Impossibile mantenere la sincronizzazione con lo switch remoto. Questo è solitamente un problema fisico, come un codice di linea o un mismatch di framing. Allarme giallo: Segnala che lo switch remoto è in allarme rosso. Ciò indica che lo switch remoto non sta ricevendo le tue trasmissioni. Allarme blu: Riceve tutti gli 1 non incorniciati su tutti gli slot temporali; dahdi_tool attualmente non rileva un allarme blu. Loopback: La porta è in loopback locale o remoto

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Passo 4: Per rilevare problemi con DAHDI sul server Asterisk, controlla prima se i canali vengono riconosciuti usando:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Step 5: Check the status of the ISDN layer 3, also known as q.931. You can check if the ISDN layer 3 is up using: `pri show spans` (to list all spans) or `pri show span <n>` for a specific span:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Usa `pri show spans` (plurale) per elencare lo stato di tutti i PRI span configurati in una volta.

Verifica un canale specifico. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: Se dopo tutto hai ancora problemi, inizia a fare il debug del pri span. Questo comando abilita un debug dettagliato delle chiamate ISDN. È un comando importante quando pensi che qualcosa non sia corretto. Puoi rilevare cifre composte in modo errato e altri problemi. Di seguito presentiamo l'esempio di un output di debug per una chiamata riuscita. Fai riferimento a questo esempio se devi confrontare una chiamata non riuscita con una senza problemi. Un suggerimento è usare core set verbose=0 per ricevere solo i messaggi ISDN q.931.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Opzioni di configurazione in chan_dahdi.conf

Diverse opzioni sono disponibili nel file chan_dahdi.conf. Una descrizione di tutte le opzioni sarebbe noiosa e controproducente. Qui, dettaglieremo i principali gruppi di opzioni disponibili per fornire una migliore comprensione.

#### Opzioni generali (indipendenti dal canale)

context: Definisce il contesto in ingresso.

```
context=default
```

channel: Definisce un canale o un intervallo di canali. Ogni definizione di canale erediterà le opzioni definite prima della dichiarazione. I canali possono essere identificati singolarmente o nella stessa riga con separazione tramite virgola. Gli intervalli possono essere definiti usando “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: Consente di trattare i canali come un gruppo. Se componi un numero di gruppo invece di un numero di canale, viene usato il primo canale disponibile. Se i canali sono telefoni, quando chiami un gruppo, tutti i telefoni squilleranno simultaneamente. Usando le virgole, puoi specificare più di un gruppo per lo stesso canale.

```
group=1
group=3,5
```

language: Attiva l'internazionalizzazione e configura una lingua. Questa funzionalità configurerà i messaggi di sistema per una lingua specifica. L'inglese è l'unica lingua con prompt completi disponibili dall'installazione standard. musiconhold: Seleziona la classe di musica in attesa.

#### Opzioni ISDN

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: Obbligatorio per alcuni switch che richiedono una specifica del piano di composizione. Questa opzione è ignorata da molti switch. Le opzioni valide sono private, national, international e unknown.

```
pridialplan = unknown
```

prilocaldialplan: Necessario per alcuni switch, solitamente sconosciuto.

```
prilocaldialplan = unknown
```

overlapdial: La composizione sovrapposta viene utilizzata quando si inviano cifre dopo che la connessione è stata stabilita. È possibile usare la numerazione in modalità blocco (overlapdial=no) o la modalità cifra (overlapdial=yes). La modalità blocco è spesso usata dagli operatori.  
signaling: Configura il tipo di segnalazione per i canali successivi. Questi parametri dovrebbero corrispondere a quelli presenti nel file chan_dahdi.conf. Le scelte corrette dipendono dal canale disponibile. Per ISDN si possono scegliere cinque opzioni:

- pri_cpe: Usato quando il dispositivo è un CPE, talvolta indicato come client, user o slave. È la forma di segnalazione più semplice e più utilizzata. A volte, quando si tenta di connettersi a un PBX privato, anche il PBX è stato configurato come CPE. In questo caso, usare la segnalazione pri_net in Asterisk.  
- pri_net: Usato quando Asterisk è collegato a un PBX privato configurato come CPE. La segnalazione è spesso indicata come host, master o network.  
- bri_cpe: Usato quando Asterisk è collegato come CPE a un trunk ISDN BRI  
- bri_net: Usato quando Asterisk è collegato a un telefono ISDN o a un PBX configurato come terminale (TE).  
- bri_cpe_ptmp: Stessa cosa di bri_cpe, ma in un'architettura point‑to‑multipoint.  

#### CallerID options

Molte opzioni di Caller ID sono disponibili. Alcune possono essere disabilitate, sebbene la maggior parte sia abilitata per impostazione predefinita.  
usecallerid: Abilita o disabilita la trasmissione del Caller ID per i canali successivi (Yes/No). Nota: se il sistema richiede due squilli prima di rispondere, provare a disabilitare questa funzione affinché risponda immediatamente.  
hidecallerid: Nasconde il Caller ID (Yes/No).  
calleridcallwaiting: Abilita la ricezione del Caller ID durante un'indicazione di chiamata in attesa (Yes/No).  
callerid: Configura una stringa di Caller ID per un canale specifico. Il chiamante può essere configurato con “asreceived” nelle interfacce trunk per inoltrare il Caller ID.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

Nota: La maggior parte dei TELCO richiede di configurare il proprio ID chiamante corretto. Se non fornisci l'ID chiamante corretto, non dovresti poter effettuare chiamate verso il TELCO. D'altra parte, potrai ricevere chiamate anche senza configurare l'ID chiamante.

#### Opzioni di qualità audio

Queste opzioni regolano alcuni parametri di Asterisk che influenzano la qualità audio nei canali DAHDI.

- **echocancel**: Disabilita o abilita la cancellazione dell'eco. Dovresti mantenere questa funzionalità abilitata. Accetta "yes" o il numero di tap. (Spiegazione: Come funziona la cancellazione dell'eco? La maggior parte degli algoritmi di cancellazione dell'eco opera generando più copie di un segnale ricevuto, ognuna delle quali è ritardata di un piccolo intervallo. Questo piccolo ritardo è chiamato "tap". Il numero di tap determina il ritardo dell'eco che può essere cancellato. Queste copie sono ritardate, regolate e sottratte dal segnale originale. L'astuzia consiste nel regolare il segnale ritardato esattamente al punto necessario per rimuovere l'eco.)
- **echocancelwhenbridged**: Abilita o disabilita il cancellatore di eco durante una chiamata TDM pura. Di solito non è necessario.
- **rxgain**: Regola il guadagno di ricezione audio per aumentare o diminuire il volume di ricezione (-100% a 100%).
- **txgain**: Regola il guadagno di trasmissione audio per aumentare o diminuire il volume di trasmissione (-100% a 100%).

Esempio:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### Opzioni di fatturazione

Queste opzioni modificano il modo in cui le informazioni delle chiamate vengono registrate nel database dei record dettagliati delle chiamate (CDR). amaflags: Influisce sulla categorizzazione del CDR. Accetta i seguenti valori:

- billing
- documentation
- omit
- default

accountcode: Configura un codice account per un canale specifico. Può contenere qualsiasi valore alfanumerico, solitamente il nome del dipartimento o dell'utente.

```
accountcode=finance
amaflags=billing
```

### Configurazione MFC/R2

MFC/R2 è utilizzato in diversi paesi dell'America Latina, in Cina e in Africa, nonché in alcuni paesi europei. ISDN è superiore e preferito se disponibile nella tua zona.

#### Comprendere il problema

La scheda usata per segnalare MFC/R2 è la stessa usata per segnalare ISDN. È possibile usare MFC/R2 sui canali DAHDI usando la libreria chiamata libopenR2 (www.libopenr2.com). Questa libreria non faceva parte delle versioni di Asterisk precedenti alla 1.6.2.

##### Comprendere il protocollo MFC/R2

Il protocollo MFC/R2 combina la segnalazione in-band e out-of-band. La segnalazione degli indirizzi viene inoltrata in-band usando un insieme di toni mentre le informazioni del canale vengono trasmesse sul timeslot 16 come segnalazione out-of-band.

**Line Signaling (ITU-T Q.421).** Nel timeslot 16, ogni canale vocale utilizza quattro bit ABCD per segnalare i propri stati e il controllo della chiamata. I bit C e D sono raramente usati. In alcuni paesi possono essere impiegati per la misurazione (misurazione a impulsi per la fatturazione). In una conversazione normale, entrambe le parti sono operative: il chiamante e il chiamato. La segnalazione dal lato del chiamante è definita segnalazione in avanti, mentre il lato del chiamato utilizza la segnalazione all’indietro. Indicheremo Af e Bf per la segnalazione in avanti e Ab e Bb per la segnalazione all’indietro.

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0101 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 è stato definito dall'ITU. Sfortunatamente, diversi paesi hanno personalizzato lo standard secondo le proprie esigenze. Di conseguenza, sono emerse variazioni negli standard tra i paesi.

**Segnali inter-registri (ITU-T Q.441).** Il segnalamento MFC/R2 utilizza una combinazione di due toni. Le tabelle seguenti mostrano lo standard ITU.

Gruppo di segnale I (avanti):

| Description | Forward signal |
| --- | --- |
| Cifra 1 | I-1 |
| Cifra 2 | I-2 |
| Cifra 3 | I-3 |
| Cifra 4 | I-4 |
| Cifra 5 | I-5 |
| Cifra 6 | I-6 |
| Cifra 7 | I-7 |
| Cifra 8 | I-8 |
| Cifra 9 | I-9 |
| Cifra 0 | I-10 |
| Indicatore di prefisso internazionale, necessario soppressore di eco a metà in uscita | I-11 |
| Indicatore di prefisso internazionale, non è necessario alcun soppressore di eco | I-12 |
| Indicatore di chiamata di prova | I-13 |
| Indicatore di prefisso internazionale, soppressore di eco a metà in uscita inserito | I-14 |
| Non usato | I-15 |

Gruppo di segnalazione II (avanti):

| Description | Forward signal |
| --- | --- |
| Abbonato senza priorità | II-1 |
| Abbonato con priorità | II-2 |
| Apparecchiatura di manutenzione | II-3 |
| Ricambio | II-4 |
| Operatore | II-5 |
| Trasmissione dati | II-6 |
| Abbonato o operatore senza struttura di trasferimento in avanti | II-7 |
| Trasmissione dati | II-8 |
| Abbonato con priorità | II-9 |
| Operatore con struttura di trasferimento in avanti | II-10 |
| Ricambio | II-11 |
| Ricambio | II-12 |
| Ricambio | II-13 |
| Ricambio | II-14 |
| Ricambio | II-15 |

Gruppo di segnale A (indietro):

| Descrizione | Segnale inverso |
| --- | --- |
| Invia la cifra successiva (n+1) | A-1 |
| Invia la penultima cifra (n-1) | A-2 |
| Indirizzo completo, passaggio alla ricezione dei segnali del Gruppo B | A-3 |
| Congestione nella rete nazionale | A-4 |
| Invia la categoria del chiamante | A-5 |
| Indirizzo completo, addebito, impostazione delle condizioni di parlato | A-6 |
| Invia la terzultima cifra (n-2) | A-7 |
| Invia la quartultima cifra (n-3) | A-8 |
| Riserva | A-9 |
| Riserva | A-10 |
| Invia l'indicatore del prefisso internazionale | A-11 |
| Invia la cifra di lingua o discriminazione | A-12 |
| Invia la natura del circuito | A-13 |
| Richiedi informazioni sull'uso del soppressore di eco | A-14 |
| Congestione in uno scambio internazionale o al suo output | A-15 |

Gruppo di segnale B (all'indietro):

| Description | Backward signal |
| --- | --- |
| Riserva | B-1 |
| Invia tono di informazione speciale | B-2 |
| Linea dell'abbonato occupata | B-3 |
| Congestione (dopo commutazione dal gruppo A al B) | B-4 |
| Numero non assegnato | B-5 |
| Linea dell'abbonato libera, a pagamento | B-6 |
| Linea dell'abbonato libera, senza addebito | B-7 |
| Linea dell'abbonato fuori servizio | B-8 |
| Riserva | B-9 |
| Riserva | B-10 |
| Riserva | B-11 |
| Riserva | B-12 |
| Riserva | B-13 |
| Riserva | B-14 |
| Riserva | B-15 |

#### MFC/R2 sequenza

La sequenza seguente illustra una chiamata originata dall'estensione di Asterisk verso un terminale nella PSTN. La PSTN interrompe la chiamata e termina la comunicazione.

![Un flusso di chiamata MFC/R2 completo tra Asterisk e il telco: la segnalazione di linea (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) viene scambiata nello slot temporale 16, le cifre composte e i segnali di ritorno "send next digit" (gruppi I/A/B) viaggiano in‑band, e i toni udibili raggiungono l'abbonato.](../images/10-legacy-fig11.png)

### Come utilizzare il driver libopenr2

Il progetto avviato da Moises Silva è stato ispirato dal driver del canale Unicall scritto da Steve Underwood. La libreria OpenR2 è attualmente la soluzione software più stabile per Asterisk. Con questa soluzione, possiamo usare qualsiasi scheda digitale compatibile con DAHDI. In precedenza, erano disponibili solo soluzioni proprietarie per MFC/R2, una delle migliori che ho usato è quella messa a disposizione da Khomp, www.khomp.com.br. In Asterisk 22, il supporto MFC/R2 tramite libopenR2 è integrato quando la libreria è presente al momento della compilazione — non è necessario alcun patch esterno. I passaggi seguenti mostrano l'installazione manuale storica per riferimento; sui sistemi moderni, installa `libopenr2-dev` dal gestore di pacchetti della tua distribuzione prima di eseguire `./configure`, quindi abilita `chan_dahdi` in `make menuselect`.

I passaggi seguenti compilano openr2 e Asterisk dai loro attuali repository Git. Sono mantenuti come riferimento per i siti che compilano dal sorgente; su una distribuzione moderna è solitamente possibile saltarli del tutto installando il pacchetto `libopenr2-dev` e una build di Asterisk 22 confezionata, poiché `chan_dahdi` compila il supporto R2 direttamente contro libopenr2 senza patch esterne.

Passo 1: Installa gli strumenti di compilazione di cui hai bisogno.

```
apt-get install git
```

Passo 2: Clona la libreria openr2 e il sorgente di Asterisk. Nessun albero patchato speciale è necessario su Asterisk 22 — un checkout standard costruisce il supporto R2 finché libopenr2 è presente.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Step 3: Compila e installa Per favore, BACK UP il tuo server prima di procedere.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Nota: non eseguire “make samples” per evitare di sovrascrivere i file di configurazione.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

Supponiamo che tu abbia una scheda con un’interfaccia E1.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: Esegui il comando dahdi_cfg per applicare le modifiche al driver:

```
dahdi_cfg -vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Step 5: Change the file chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Step 6: Cambia il dial plan nel file extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Nota: Alcuni TELCOS non accettano chiamate senza ID chiamante. Imposta l'ID chiamante su uno dei numeri DID assegnati dall'operatore. In alcuni paesi, questo passaggio non è necessario. Passo 7: Testare la soluzione: ora, con un'estensione nel contesto from-internal, chiama qualsiasi numero e osserva la console. Verifica se si verificano errori. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

Per rilevare errori nelle chiamate, puoi attivare il debug. Per farlo, segui i passaggi seguenti.

1. Modifica il file `chan_dahdi.conf` e aggiungi le seguenti tre righe alla configurazione:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Riavvia il server Asterisk
3. Testa la chiamata e controlla i file di chiamata su `/var/log/asterisk/mfcr2/span1`

Di seguito è presente un trace di una chiamata normale. Confrontalo con quello che ricevi nella tua chiamata.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### Configurazione MFC/R2

Le opzioni sono documentate nel file chan_dahdi.conf. Alcune delle opzioni più importanti sono descritte qui. Parametri obbligatori: mfcr2_variant, mfcr2_max_ani e mfcr2_max_dnis. mfcr2_variant: variante del paese.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Numero massimo di cifre ANI da richiedere  
mfcr2_max_dnis: Numero massimo di cifre DNIS da richiedere  
mfcr2_get_ani_first: Indica se ottenere l'ANI prima del DNIS (richiesto da alcuni TELCOS)  
mfcr2_category: Categoria del chiamante. È possibile impostare la variabile MFCR2_CATEGORY prima di avviare la chiamata  
mfcr2_logdir: Directory in cui registrare i file delle chiamate. (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files: Indica se registrare o meno le chiamate  

- mfcr2_logging: valori di logging  
- cas – bit ABCD per tx e rx  
- mf – toni multifrequenza  
- stack – output dettagliato dello stack del canale e del contesto  
- all – tutte le attività  
- nothing – non registrare nulla  

mfcr2_mfback_timeout: Questo valore merita di essere menzionato. A volte, se si chiama un cellulare o una chiamata che richiede molto tempo per completarsi, questo parametro può scadere, quindi viene spesso modificato per una messa a punto fine. Se alcune delle tue chiamate non vengono completate, è questo il parametro da cambiare per primo.  
mfcr2_metering_pulse_timeout: I pulsanti sono usati da alcune varianti R2 per indicare i costi  
mfcr2_allow_collect_calls: In Brasile, il tono II-8 è usato per indicare una chiamata a carico del destinatario; questo parametro consente di bloccare le chiamate a carico.  
mfcr2_double_answer: Usato anche per evitare le chiamate a carico quando è richiesto un doppio risposta. Con double_answer=yes si bloccano effettivamente le chiamate a carico.  
mfcr2_immediate_accept: Consente di saltare l'uso dei segnali gruppo B/II e passare direttamente allo stato accettato.  
mfcr2_forced_release: Consente di accelerare il rilascio della chiamata; funziona per la variante brasiliana.  

#### ANI e DNIS

Automatic Number Identification (ANI) è il numero del chiamante. Dialed Number Identification Service (DNIS) è il numero chiamato o, in altre parole, il numero composto. Quando una chiamata viene ricevuta, di solito le ultime quattro cifre vengono trasmesse al PBX in un processo denominato direct inward dial (DID). Il numero ANI è in realtà il Caller ID. L'ANI conterrà l'estensione del chiamante quando si effettua la chiamata, mentre il DNIS conterrà la destinazione della chiamata. È importante che questi parametri siano configurati correttamente. Alcuni switch inviano solo le ultime quattro cifre, mentre altri inviano il numero completo.  

### Formato del canale DAHDI

I canali DAHDI usano il seguente formato nel dialplan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

Esempi:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## The IAX2 protocol

In this chapter, we will learn about the Inter-Asterisk eXchange (IAX) protocol, including its strengths and weaknesses. Details such as trunk mode and the interconnection of two Asterisk servers will also be covered. All references in this document correspond to IAX version 2.

The IAX protocol provides media transport and signaling for voice and video. IAX is very innovative; it saves bandwidth in trunk mode and is much simpler than SIP when you need to traverse NAT. The primary use for IAX nowadays is to interconnect Asterisk servers. IAX was created primarily for voice, but it can also accommodate video and other multimedia streams.

IAX was inspired from other VoIP protocols, such as SIP and MGCP. Instead of using two separate protocols for signaling and media, IAX unified them to make a unique protocol. IAX does not use RTP for media transport; instead, it embeds the media in the same UDP connection.

**Status in Asterisk 22.** `chan_iax2` is still included and fully supported in Asterisk 22 LTS, so everything in this section remains valid. IAX2 is, however, a legacy protocol that sees relatively little new deployment: the industry has largely converged on SIP (via `chan_pjsip` in Asterisk 22) for both provider trunking and server interconnection. IAX2's main remaining advantage is its single-port design — all signaling and media flow over a single UDP port (4569 by default), which simplifies firewall and NAT configuration compared to SIP plus its separate RTP streams. For a new Asterisk-to-Asterisk trunk where NAT is not a concern, a PJSIP trunk is the recommended modern approach; IAX2 is covered here because it remains a valid choice, especially where only one UDP port can be opened through a firewall.

### Objectives

By the end of this chapter, you should be able to:

- Identify strengths and weakness of IAX protocol
- Describe usage scenarios for the IAX protocol
- Describe the advantages of IAX trunk mode
- Configure iax.conf for phones
- Configure iax.conf for connection to a VoIP provider
- Configure iax.conf for Asterisk interconnection
- Understand IAX authentication

### IAX design

The main objectives for IAX design are:

- To reduce the bandwidth required for media transport and signaling
- To provide NAT transparency
- To be able to transmit the dial plan information
- To support the efficient use of paging and intercom

IAX is a peer-to-peer signaling and media protocol that is similar to SIP without using RTP. The basic approach is to multiplex the multimedia streams over a single UDP connection between two hosts. The greatest benefit of this approach is its simplicity when traversing connections over NAT, regularly found in xDSL modems. IAX uses a single port, UDP 4569 by default, and then uses a call number with 15 bits to multiplex all streams. The IAX protocol uses registration and authentication processes similar to the SIP protocol. A description of the protocol can be found at http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![Il protocollo IAX multiplexa molte chiamate tra due endpoint su una singola porta UDP (4569 per impostazione predefinita), usando un numero di chiamata a 15 bit per tenere separati i flussi — il che rende il traversal NAT semplice.](../images/10-legacy-fig12.png)

### Bandwidth usage

The bandwidth used in VoIP networks is affected by several factors; codecs and protocol headers are the most important. The IAX protocol has a surprising feature called trunk mode, whereby it multiplexes several calls using a single header. By playing with the Asterisk bandwidth calculator, you will see how IAX trunks can save you up to 80% of the traffic with multiple calls.

![Confronto overhead IAX e SIP: due chiamate SIP/RTP richiedono due pacchetti (40 byte di payload trasportati sotto 156 byte di overhead), mentre la modalità trunk IAX2 trasporta entrambe le chiamate in un unico pacchetto (40 byte di payload sotto appena 66 byte di overhead) condividendo un header IP/UDP tra molti mini‑frame.](../images/10-legacy-fig13.png)

### Channel naming

It is important to understand channel-naming conventions as you will use these names when specifying a channel in the dial plan. The format of an IAX channel name used for outbound channels is:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — UserID sul peer remoto, o nome del client configurato in iax.conf
- `<secret>` — La password. In alternativa può essere il nome file di una chiave RSA senza l’estensione finale (.key o .pub) e racchiuso tra parentesi quadre
- `<peer>` — Nome del server a cui connettersi
- `<portno>` — Numero di porta per la connessione
- `<exten>` — Interno nel server Asterisk remoto
- `<context>` — Contesto nel server Asterisk remoto
- `<options>` — L’unica opzione disponibile è 'a', che significa 'richiedi autoanswer'

#### Outbound channels example:

Outbound channels are seen in the Asterisk console.

- `IAX2/8590:secret@myserver/8590@default` — Chiama l’interno 8590 in myserver. Usa 8590:secret come coppia nome/password
- `IAX2/iaxphone` — Chiama "iaxphone"
- `IAX2/judy:[judyrsa]@somewhere.com` — Chiama somewhere.com usando judy come nome utente e una chiave RSA per l’autenticazione

#### The format of an incoming IAX channel is:

Inbound channels are seen in the Asterisk console.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — Username if known
- `<host>` — Host connecting
- `<callno>` — Local call number

Esempio di canale in ingresso:

- `IAX2[flavio@8.8.30.34]/10` — Call number 10 from IP address 8.8.30.34 using flavio as the user.
- `IAX2[8.8.30.50]/11` — Call number 11 from IP address 8.8.30.50.

### Using IAX

Puoi utilizzare IAX in diversi modi. In questa sezione, ti mostreremo come configurare IAX per diversi scenari, includendo:

- Connessione di un softphone tramite IAX
- Connessione di IAX a un provider VoIP tramite IAX
- Connessione di due server tramite IAX
- Connessione di due server tramite IAX in modalità trunk
- Debug di una connessione IAX
- Utilizzo di chiavi RSA per l'autenticazione

#### Connecting a softphone using IAX

Asterisk supporta telefoni IP basati su IAX come l'ATCOM e il vecchio ATA di Digium (chiamato IAXy) così come softphone che implementano ancora il protocollo IAX2. Il processo per softphone, ATA e telefoni fissi è simile. Per configurare un dispositivo IAX, è necessario modificare il file iax.conf in /etc/asterisk

```
directory.
```

We will use an IAX2-capable softphone as an example.

1. Make a backup of the original `iax.conf` file using:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. Inizia a modificare un nuovo file `iax.conf`:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; Parametro molto importante, cambia i codec disponibili

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Ho cercato di preservare le righe predefinite (non commentate) del file di esempio. I seguenti parametri sono stati modificati:

```
bandwidth=high
```

Questa riga influisce sulla selezione del codec. Usare l'impostazione alta consente la selezione di un codec a larghezza di banda elevata e alta qualità come g.711 definito dalla parola chiave ulaw. Se mantieni il parametro predefinito, non potrai scegliere ulaw. In questo caso, Asterisk ti mostrerà il messaggio “no codec available” per la configurazione sotto.

```
disallow=all
allow=ulaw
```

Nel comando descritto sopra, abbiamo disabilitato tutti i codec e abilitato solo ulaw. Nelle LAN, la maggior parte delle persone preferisce usare ulaw perché non richiede molte risorse di elaborazione e risparmia cicli CPU. Anche se utilizza più larghezza di banda, questo codec è preferibile perché nelle LAN si dispone solitamente di una rete Ethernet a 100 megabit o anche a Gigabit. Una chiamata vocale che utilizza ulaw consuma quasi 100 kilobit al secondo di larghezza di banda dalla tua rete, il che rappresenta un utilizzo molto leggero per le LAN ad alta velocità odierne. Nelle reti WAN o Internet, di solito si disabilita ulaw, scambiando alcuni cicli CPU disponibili mediante compressione vocale per un migliore utilizzo della larghezza di banda. I codec gsm, g729 e ilbc offrono anch'essi un buon fattore di compressione.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

Nel comando sopra, abbiamo definito un amico chiamato [2003]. Il contesto è quello predefinito (nei primi laboratori usiamo sempre il contesto predefinito per evitare confusione; questo contesto sarà spiegato completamente quando tratteremo il dialplan). La riga “host=dynamic” fornisce una registrazione dinamica dell’indirizzo IP del telefono.

3. Scarica e installa un softphone compatibile con IAX2. Puoi scegliere qualsiasi softphone che supporti ancora il protocollo IAX2 per il laboratorio.  
4. Configura un account IAX nel client (tipicamente *Add account* → IAX). Nota che il SipPulse Softphone è solo SIP e non può registrarsi via IAX2, quindi per i test IAX hai bisogno di un client che supporti ancora il protocollo.

5. Configura il file `extensions.conf` per testare il tuo dispositivo IAX.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

A few VoIP providers support IAX. You can easily find an IAX provider by searching for “IAX providers”. Using an IAX provider makes a lot of sense as IAX can save a lot of bandwidth, easily traverses NAT, and can authenticate using RSA key pairs.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

The number of IAX‑capable commercial VoIP providers has declined sharply over the past several Asterisk releases; most providers now offer SIP/PJSIP trunks exclusively. Before committing to an IAX provider, confirm they actively maintain their IAX infrastructure. For a new provider integration, a PJSIP trunk (Chapter 3) is the recommended alternative.

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

Nelle istruzioni descritte sopra, ti sei registrato con il tuo provider usando il tuo account e la password. Non appena ricevi una chiamata, verrà inoltrata all'estensione 2003.

```
[name]
```

- ; Il tuo nome account o numero

```
type=peer
secret=secret
; Your password
host=hostname
```

Nelle istruzioni descritte sopra, abbiamo creato un peer corrispondente al provider per scopi di composizione.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

Questo è necessario per l'autenticazione RSA. L'uso della chiave pubblica del tuo provider ti consente di essere sicuro che la chiamata ricevuta provenga davvero dal vero provider. Se qualcun altro tenta di utilizzare lo stesso percorso, non potrà autenticarsi perché non possiede la chiave privata corrispondente. Passo 4: Prova la connessione. Per testare la connessione, chiama qualsiasi numero. Alcuni fornitori offrono un test di eco. Per farlo, modifica il file extensions.conf.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Vai alla CLI di Asterisk ed esegui un reload. Per verificare se Asterisk è registrato con il provider, usa il comando successivo.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### Connecting two Asterisk servers through an IAX trunk

It is very easy to connect one server to another. You won’t need to register them because the IP addresses are already known. You will have to create the peers and users in the iax.conf file. All extensions in the HQ site start with 20 followed by two digits (e.g., 2000). In the Branch, all extensions start with 22 followed by two digits (e.g., 2200). We will use the trunk. You will need a DAHDI timing source to enable this feature. Step 1: Edit the iax.conf file in the Branch server.

![Collegamento di due server Asterisk con un trunk IAX: il server HQ (192.168.1.1, estensioni 20xx) e il server Branch (192.168.1.2, estensioni 22xx) si raggiungono tramite un unico trunk IAX — non è necessaria la registrazione perché entrambi gli indirizzi IP sono fissi e noti.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

# Passo 2: Configura il file extensions.conf nel server Branch

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

# Passo 3: Configura il file iax.conf nel server HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Passo 4: Configura il file extensions.conf nel server HQ.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

Se una chiamata ha un nome utente specificato, ad esempio:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk cercherà di autenticare la chiamata utilizzando solo la voce corrispondente nel file iax.conf. Se vengono specificati altri nomi, la chiamata verrà rifiutata. Se non viene specificato alcun utente, Asterisk proverà ad autenticare la connessione come guest. Tuttavia, se guest non esiste, proverà qualsiasi altra connessione con un secret corrispondente. In altre parole, se non hai una sezione guest nel tuo file iax.conf, un utente malintenzionato potrebbe provare a indovinare un secret corrispondente non specificando il nome utente. Anche le restrizioni deny/allow per gli indirizzi IP si applicano. Un buon modo per evitare l’indovinamento dei secret è utilizzare l’autenticazione RSA. Un altro metodo è limitare gli indirizzi IP autorizzati a chiamare.

#### Restrizioni sugli indirizzi IP

L’accesso è controllato con le righe `permit` e `deny`:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

Le regole vengono interpretate in sequenza e tutte vengono valutate (questo concetto è diverso dalle ACL solitamente presenti in router e firewall). L'ultima istruzione corrispondente sostituisce le precedenti.

Esempio #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

This will deny any packet from the 192.168.0.0/24 network.

Example #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

Questo permetterà qualsiasi pacchetto, perché l'ultima istruzione sovrascrive la prima.

#### Connessioni in uscita

Le connessioni in uscita acquisiscono le informazioni di autenticazione usando i seguenti metodi:

- La descrizione del canale IAX2 passata dall'applicazione `dial()`.
- Una voce con `type=peer` o `type=friend` nel file `iax.conf`.
- Una combinazione di entrambi i metodi.

#### Collegare due server Asterisk usando chiavi RSA

È possibile utilizzare IAX con autenticazione forte usando chiavi RSA asimmetriche. Secondo il codice sorgente (`res_krypto.c`), Asterisk usa chiavi RSA con algoritmo SHA‑1 per i digest dei messaggi invece del più debole MD5. Di seguito una guida passo‑passo per configurare due server usando chiavi RSA.

##### Configurazione del server per il ramo

Passo 1: Generare le chiavi RSA nel server del ramo

```
astgenkey -n
```

When asked, use the key name branch.  
We have used the parameter –n to avoid passing a passphrase whenever Asterisk reinitializes.  
If you want to improve the security, don’t use the –n and start Asterisk with asterisk -i  

Passo 2: Copy the keys to the directory /var/lib/asterisk/keys

```
cp branch.* /var/lib/asterisk/keys
```

Passo 3: Copia la chiave pubblica sul server HQ

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4: Modifica il file iax.conf nel server Branch.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

# Passo 8: Configura il file extensions.conf nel server Branch

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### Configurazione del server per la sede centrale

Passo 1: Genera le chiavi RSA nel server della sede centrale

```
astgenkey -n
```

Quando richiesto, usa il nome chiave hq.  
Passo 2: Copia le chiavi nella directory /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

# Passo 3: Copia la chiave pubblica sul server BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

Step 4: Configura il file iax.conf nel server HQ

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Step 10: Configura il file extensions.conf nel server HQ.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### Crittografia IAX2

IAX supporta la crittografia delle chiamate usando una chiave simmetrica, cifrario a blocchi a 128‑bit chiamato AES (Advanced Encryption Standard). È molto semplice attivare la crittografia tra i trunk IAX. Nel file iax.conf usare:

```
encryption=yes
```

Per forzare la crittografia:

```
forceencryption=yes
```

Per garantire la compatibilità con le versioni precedenti, potresti dover disabilitare la rotazione delle chiavi usando:

```
keyrotate=no
```

### Comandi di debug IAX2

Di seguito sono riportati alcuni dei comandi console di troubleshooting più importanti per Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Guardando questo output, identifica l'inizio e la fine della chiamata. Osserva le informazioni su ritardo e jitter ottenute usando i pacchetti poke e pong. Questi pacchetti aiutano a creare l'output del comando “iax2 show netstats”.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

Per disattivare il debug, usa:

```
vtsvoffice*CLI>iax2 no debug
```

### Riepilogo

Questo capitolo ha esaminato i punti di forza e le debolezze del protocollo IAX. Ha dimostrato come IAX funzioni in diversi scenari, come i softphone e un trunk tra due server Asterisk. La modalità trunk consente di risparmiare larghezza di banda trasportando più di una chiamata in un unico pacchetto. Infine, hai imparato i comandi della console che puoi usare per verificare lo stato e fare il debug del protocollo.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

Step 2: Configura il [peer] su sip.conf Crea una voce di tipo peer al provider desiderato per semplificare il dialing di Asterisk.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Step 3: Create a route to the provider in the dial plan  
We will choose the digits 010 as the destination route to the provider.  
To dial #610000 inside the provider, simply dial 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### Opzioni SIP specifiche per lo scenario del provider

La discussione seguente esamina i dettagli delle opzioni impostate nel file sip.conf per la connessione a un provider VoIP.

```
register=>username:password@hostname/4100
```

L'istruzione register nel file sip.conf è usata per registrarsi con un provider. La transazione register è autenticata con il nome e il secret. È possibile usare una barra (“/”) per fornire un’estensione per le chiamate in ingresso. Tecnicamente, l’estensione verrà inserita nel campo header “Contact” della richiesta SIP. Il comportamento di registrazione può essere controllato da alcuni parametri:

```
registertimeout=20
registerattempts=10
```

Per verificare se la registrazione è avvenuta con successo, il comando console legacy era `sip show registry`. Su Asterisk 22 il comando equivalente è `pjsip show registrations` (registrazioni in uscita) e `pjsip show endpoints` per lo stato dell'endpoint.

Il parametro “username” è usato nel digest di autenticazione. Il digest è calcolato usando username, secret e realm:

```
username=username
```

Host definisce l'indirizzo o il nome del provider VoIP:

```
host=hostname
```

I parametri Fromuser e Fromdomain sono talvolta richiesti per l'autenticazione. Questi parametri sono usati nel campo header SIP From:

```
fromuser=username
fromdomain=hostname
```

Quando ti connetti a un provider VoIP, sono necessarie credenziali. Dopo l'invite iniziale, il provider ti invia un messaggio chiamato “407 Proxy Authentication Required”; fornisci le credenziali nel successivo messaggio INVITE. Per le chiamate in ingresso, il tuo server Asterisk richiederà le credenziali al provider. Ovviamente, il provider non possiede credenziali valide per il tuo server Asterisk. Quando usi insecure=invite, stai dicendo ad Asterisk di non inviare il “407 Proxy Authentication Required” al provider e di accettare le chiamate in ingresso. Puoi anche usare insecure=port, invite per far corrispondere il peer basandoti sull'indirizzo IP senza confrontare il numero di porta.

```
insecure=invite, port
```

### Connecting two Asterisk servers together using SIP (sip.conf)

Puoi usare SIP per interconnettere due server Asterisk. È importante prestare attenzione al dialplan prima di procedere con questa configurazione. Gli utenti generalmente vogliono collegare altri PBX con il minimo sforzo. L'idea qui è utilizzare solo un numero di estensione per connettersi all'altro PBX. Passo 1: Modifica il file sip.conf nel server A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Step 2: Modifica il file sip.conf nel server B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![Connessione di due server Asterisk usando SIP: il server A (estensioni 4400/4401) e il server B (estensioni 4500/4501) scambiano segnalazione SIP così gli utenti su ciascun PBX possono chiamare l'altro](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Step 3: Modifica il file extensions.conf nel server A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Step 4: Modifica il file extensions.conf nel server B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Supporto del dominio Asterisk (sip.conf)

Il protocollo SIP segue l'architettura Internet. La prima cosa da fare prima di configurare SIP è impostare correttamente i server DNS. In un ambiente SIP, puoi chiamare un utente situato in qualsiasi proxy SIP, e altri utenti possono chiamare te utilizzando il tuo SIP Uniform Resource Identifier (URI). Per impostare un server DNS per SIP, devi aggiungere record SRV al tuo server DNS.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

Dopo aver configurato il DNS, è possibile utilizzare l'URI, che punta a un utente SIP, a un telefono SIP o a un interno telefonico. Un URI SIP ha un aspetto simile a un indirizzo email (ad es., sip:chuck@yourpartnerdomain.com). Utilizzando gli URI SIP, non è necessario alcun numero di telefono per effettuare una chiamata da un telefono SIP a un altro. Per chiamare un utente esterno, basta usare un'istruzione come quella mostrata di seguito.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Alcuni parametri possono controllare il comportamento del dominio.

```
srvlookup=yes
```

Questo parametro abilita le ricerche DNS SRV per le chiamate in uscita. Utilizzando questo parametro, è possibile effettuare chiamate usando nomi SIP basati sul dominio.

```
allowguest=yes
```

Questo parametro consente a un invito esterno di essere elaborato senza autenticazione. Elabora la chiamata nel contesto definito nella sezione generale o nella dichiarazione del dominio. **Attenzione**: se definisci un contesto nella sezione generale con accesso al PSTN, un utente esterno può comporre il PSTN tramite il tuo PBX. In tal caso, potresti sostenere costi. Consenti solo le tue estensioni nel contesto definito nella sezione generale.

![Connessione ad altri server SIP per dominio: youdomain.com e yourpartnerdomain.com scambiano segnalazione SIP, così utenti come lee e bruce possono chiamare chuck e norris usando URI SIP](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

Il comando **domain** consente di gestire più di un dominio all'interno di Asterisk. Se una chiamata proviene da un dominio specifico, viene indirizzata a un contesto specifico.

```
;autodomain=yes
```

Questo parametro include l'IP locale e il nome host nei domini consentiti.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: Ora configura il softphone per usare la presenza. Ti mostreremo come configurare il SipPulse Softphone.

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Cambia il modello di presenza da peer-to-peer a presence agent, il che farà sì che il softphone si iscriva ad Asterisk per gli eventi SIP.

Step 3: Aggiungi il contatto ad altri softphone. In questo esempio, il SipPulse Softphone è l'account 2000, quindi aggiungeremo un contatto per l'account 2001. Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Compila il nome 2001. Display as 2001 e non dimenticare di spuntare la casella Show this contact’s availability.

Step 4: Ora chiama l'estensione 2001 e controlla lo stato del telefono nel pannello destro del softphone. Usa il comando console `core show hints` per vedere lo stato della presenza cambiare sul server (in legacy chan_sip, `sip show inuse` mostrava quante chiamate avevi su ogni linea). Su Asterisk 22, usa `pjsip show endpoints` per ispezionare lo stato di endpoint e canale. Lo stato di presenza/BLF appare nei contatti del softphone o nel pannello BLF — esattamente come viene mostrato dipende dal client.

#### Codec configuration

La configurazione del codec è semplice e diretta. Puoi impostare le parole allow e disallow nella sezione [general] o nella sezione peer/user. La best practice è standardizzare il codec per evitare il transcoding, che è intensivo per il processore. Per favore usa lo stesso codec per messaggi e prompt.

```
[general]
disallow=all
allow=g729
```

#### Opzioni DTMF

In alcune occasioni, dovrai inviare cifre a un'applicazione come la segreteria telefonica o il voice response interattivo (IVR). È importante trasmettere correttamente il DTMF. Il metodo più semplice per inviare DTMF si chiama inband. Viene impostato nella sezione `[general]` o nella sezione peer/user del file `sip.conf`. Quando imposti `dtmfmode=inband`, i toni DTMF vengono generati come suoni nel canale audio. Il problema principale di questo metodo è che, comprimendo il canale audio con un codec come `g729`, i suoni vengono distorti e i toni DTMF non vengono riconosciuti correttamente. Se prevedi di usare `dtmfmode=inband`, utilizza il codec `g.711` (`ulaw` e `alaw`).

```
dtmfmode=inband
```

Un altro approccio è utilizzare RFC2833, che consente di trasmettere i toni DTMF come eventi nominati nei pacchetti RTP.

```
dtmfmode=rfc2833
```

Infine, è possibile inviare i digit DTMF all'interno dei pacchetti SIP, invece che nei pacchetti RTP. Questo metodo è definito negli RFC3265 (eventi di segnalazione) e RFC2976.

```
dtmfmode=info
```

A seguito del rilascio della versione 1.2, è ora possibile utilizzare:

```
dtmfmode=auto
```

This tries to use the RFC2833; if it is not possible, use band tones.

#### Quality of service (QoS) marking configuration

QoS è un insieme di tecniche responsabili della qualità della voce. QoS è implementato in modo da ridurre larghezza di banda, latenza e jitter. Le principali funzioni di QoS sono la programmazione dei pacchetti, la frammentazione e la compressione dell'intestazione. QoS è implementato in switch e router, non da Asterisk stesso. Tuttavia, Asterisk può aiutare router e switch marcando i pacchetti per una consegna rapida. Il marcatore utilizza i punti di codice dei servizi differenziati (DSCP) definiti negli RFC 2474 e RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

A partire dalla versione 1.4, è possibile specificare codici diversi per il segnalamento (SIP), l’audio (RTP) e il video (RTP).

### SIP authentication (sip.conf)

Quando il legacy `chan_sip` riceveva una chiamata SIP, seguiva le regole descritte nel diagramma seguente. Tre parametri svolgevano un ruolo importante nell’autenticazione SIP. Su Asterisk 22, l’autenticazione è configurata invece con oggetti PJSIP `auth` (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenziati da un endpoint, e il controllo di accesso IP è gestito con `permit=`/`deny=` sull’endpoint o tramite un `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

Questo parametro controlla se un utente senza un peer corrispondente può autenticarsi senza nome e segreto. Abbiamo discusso di questo parametro nella sezione di supporto del dominio.

```
insecure=invite,port
```

Quando usiamo insecure=invite, Asterisk non genera il messaggio “407 Proxy Authentication Required”. Senza questo messaggio, l'utente può effettuare una chiamata senza autenticazione. Questo è spesso usato per connettersi ai fornitori di servizi VoIP. Le chiamate provenienti dal fornitore di servizi VoIP di solito non sono autenticate.

```
autocreatepeer=yes/no
```

Questo comando è usato quando Asterisk è connesso a un proxy SIP. Crea dinamicamente un peer per ogni chiamata. Quando questa opzione è abilitata, qualsiasi UAC può connettersi al server Asterisk. È importante limitare la connessione IP al proxy SIP. Il proxy SIP, a sua volta, si occupa del controllo degli accessi. La configurazione del peer si basa sulle opzioni generali così come sul campo header “Contact” del pacchetto SIP. Avvertimento: Usare questo con estrema cautela poiché apre completamente Asterisk.

```
secret=secret, remotesecret=secret
```

Questo parametro configura il segreto per l'autenticazione; usa secret per le richieste in ingresso e remotesecret per le richieste in uscita. Se non vuoi esporre i segreti nei file di testo, puoi usare md5secret per includere un hash al posto del segreto. Per generare il segreto MD5, puoi usare:

```
echo -n "username:realm:secret" |md5sum
```

Quindi usa la seguente istruzione:

```
md5secret=0b0e5d467890....
```

Attenzione: non dimenticare di usare il parametro –n; il ritorno a capo verrà utilizzato nel calcolo md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

The statements above will deny all IP addresses and allow UAC only from the local network (192.168.1.0/24).

#### opzioni RTP

It is possible to control some RTP parameters.

```
rtptimeout=60
```

This terminates calls without RTP activity for more the 60 seconds when not in hold.

```
rtpholdtimeout=120
```

Questo termina le chiamate senza attività RTP anche quando in attesa (deve essere più grande di rtptimeout).

### SIP NAT traversal (sip.conf)

La *teoria* NAT (i quattro tipi di NAT, il problema dell'header Contact, i keep-alive e il forzare i media attraverso il server) è a livello di protocollo ed è trattata nel capitolo *SIP & PJSIP in depth*. I parametri `sip.conf` mostrati qui (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) sono **legacy chan_sip** e sono stati rimossi in Asterisk 21+. Su PJSIP questi corrispondono a impostazioni di transport/endpoint come `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address` e `local_net=` sul transport, più `qualify_frequency=` sull'AOR.

Nel chan_sip legacy, il parametro `nat` aveva cinque opzioni:

- nat = no — Non eseguire alcuna gestione speciale del NAT oltre a RFC3581
- nat = force_rport — Fingere che esista un parametro rport anche se non è presente
- nat = comedia — Inviare i media alla porta da cui Asterisk li ha ricevuti, indipendentemente da dove l'SDP indica di inviarli.
- nat = auto_force_rport — Impostare l'opzione force_rport se Asterisk rileva NAT (predefinito)
- nat = auto_comedia — Impostare l'opzione comedia se Asterisk rileva NAT

Quando inserisci l'istruzione “nat=force_rport” nel file sip.conf, stai dicendo ad Asterisk di ignorare l'indirizzo contenuto nel campo header “Contact” dell'header SIP e di utilizzare l'indirizzo IP di origine e la porta nell'header IP del pacchetto, oltre a inviare i media indietro all'indirizzo da cui sono stati ricevuti ignorando il contenuto dell'header SDP.

```
nat=force_rport,comedia
```

È necessario mantenere aperta la mappatura NAT. Se il NAT scade, Asterisk non può inviare un invito al UAC. Il UAC è in grado di inviare chiamate, ma non di riceverne alcuna. La seguente istruzione può essere usata per mantenere aperto il NAT.

```
qualify=yes
```

Qualify invierà regolarmente un pacchetto SIP usando il metodo OPTIONS, il che aiuterà a mantenere aperta la NAT. Qualify invia un OPTIONS ogni 60 secondi e ogni 10° secondo quando l'host non è raggiungibile. È possibile utilizzare “sip show peers” per vedere la latenza dei peer. Se la NAT dell'utente è del tipo simmetrico, non è possibile inviare pacchetti da un UAC all'altro direttamente; in tal caso è necessario forzare l'RTP attraverso Asterisk usando:

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

Tutti gli scenari precedenti presumono che il server Asterisk abbia un indirizzo Internet esterno (valido). Talvolta il server Asterisk è implementato dietro un firewall con NAT. In questo caso è necessario effettuare alcune configurazioni aggiuntive.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. Configurare il firewall per reindirizzare staticamente la porta UDP 5060 al server Asterisk.  
2. Configurare il firewall per reindirizzare staticamente le porte UDP da 10000 a 20000.

Se si desidera limitare il numero di porte aperte, è possibile modificare il file `rtp.conf` per cambiare l’intervallo di porte RTP. Un’alternativa è utilizzare un firewall intelligente che supporti il protocollo SIP per aprire dinamicamente le porte RTP.

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

Passo 3: Configurare Asterisk per includere l'indirizzo esterno nei campi header dei pacchetti SIP, inclusi Session Description Protocol (SDP). È possibile farlo aggiungendo le seguenti due istruzioni al file sip.conf:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

Il primo parametro externaddr indica ad Asterisk di includere l'indirizzo IP esterno all'interno delle intestazioni SIP per le destinazioni esterne. Il secondo parametro localnet consente ad Asterisk di differenziare tra indirizzi esterni e interni. Facoltativamente, è possibile utilizzare externhost se si utilizza un Dynamic DNS con un indirizzo DHCP sul server.

### Stringhe di composizione SIP (chan_sip)

La tecnologia di dial-string `SIP/...` mostrata di seguito è il driver chan_sip rimosso. Su Asterisk 22 utilizzare la tecnologia `PJSIP/...` al suo posto — ad esempio `Dial(PJSIP/2000)` o `Dial(PJSIP/${EXTEN}@provider)`. Le forme e il significato sono altrimenti analoghi.

È possibile chiamare una destinazione SIP legacy utilizzando diverse stringhe di composizione:

```
SIP/peer
```

- ; È necessario avere un peer definito in sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

Esempi includono:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Migrating a legacy chan_sip system to PJSIP

Because `chan_sip` was removed in Asterisk 21 and is gone in Asterisk 22, any
existing `sip.conf` deployment must be migrated to PJSIP. The biggest conceptual
shift is that a single `sip.conf` `[peer]` or `[friend]` is split into several
PJSIP objects, each with a `type=`: an **endpoint** (call/codec/media settings),
one or more **aor** objects (where the device can be reached / registration),
an **auth** object (credentials), and a shared **transport** (the listening
socket, NAT addresses). The following table maps the most common concepts.

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (referenced via `auth=` and `aors=`) |
| `type=friend` / `type=peer` / `type=user` | a single `type=endpoint` (PJSIP has no friend/peer/user distinction) |
| `host=dynamic` (device registers) | `type=aor` with `max_contacts=1`; the device REGISTERs to update its contact |
| `host=<ip/hostname>` (static) | `type=aor` with a static `contact=sip:host:port` |
| `register=>user:secret@host/ext` (outbound) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` on the endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` on the endpoint (same syntax) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — also `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` on the endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (seconds) on the **aor** |
| `externaddr=` | `external_media_address=` and `external_signaling_address=` on the **transport** |
| `localnet=` | `local_net=` on the **transport** |
| `insecure=invite` (provider, no auth) | omit `auth=`/`outbound_auth=` and use `identify` (`type=identify`, `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (use with care) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (and `cos_audio` / `cos_video`) on the endpoint |

A registering extension that looked like this in legacy `sip.conf`:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

becomes the following in `pjsip.conf` on Asterisk 22:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### The sip_to_pjsip.py conversion script

Asterisk ships a helper script, **`sip_to_pjsip.py`**, that reads an existing
`sip.conf` and produces a `pjsip.conf`. You can run it directly in the
/etc/asterisk directory. The utility is in the Asterisk source tree under
`contrib/scripts/sip_to_pjsip/`, where `${PATH_TO_ASTERISK_SOURCE}` is the path
where the Asterisk source files are found (usually /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

If you run it with the `--help` option you will see its options:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

It also accepts optional positional arguments — `[input-file [output-file]]`,
defaulting to `sip.conf` and `pjsip.conf` in the current directory.

Treat its output as a **starting point**: review every generated object,
especially transports, NAT settings, and codec lists, and test thoroughly before
going to production.

Let’s migrate the sip.conf in our companion labs at VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

While the conversion seems ok, we can see that some elements such as qualify=yes cannot be mapped directly. To fix you have to add to the aor section the command qualify_frequency=time in seconds. Example below.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

Full PJSIP configuration is covered in the *SIP & PJSIP in depth* chapter, and the official documentation at docs.asterisk

## Summary

Questo capitolo raccoglie le tecnologie dei canali che precedono le moderne implementazioni pure‑VoIP ma che Asterisk 22 supporta ancora. Hai visto come le linee **analog** e i telefoni si collegano tramite interfacce **FXO/FXS** su DAHDI, come i collegamenti **digital TDM** (E1/T1 e ISDN PRI/BRI) vengono provisionati, e come **IAX2** (`chan_iax2`) continui a servire come un trunk server‑to‑server efficiente e amichevole con NAT anche se ora è fermamente legacy. Hai anche rivisitato il driver **`chan_sip`** ritirato e la sua sintassi `sip.conf` — che incontrerai in sistemi più vecchi ma che non esiste più in Asterisk 22 — e hai lavorato alla migrazione di tale sistema verso PJSIP con la tabella di mappatura dei concetti e lo script `sip_to_pjsip.py`. La regola pratica: ricorri a quanto descritto in questo capitolo solo quando hardware reale o un sistema legacy esistente ti costringono; tutto ciò che è green‑field è PJSIP su IP.

## Quiz

1. Riguardo alle due interfacce analogiche Foreign eXchange, indica le affermazioni corrette (scegli tutte le opzioni valide):
   - A. Un'interfaccia FXO si collega all'ufficio centrale della rete telefonica pubblica (PSTN) e preleva il segnale di tono di chiamata da essa.
   - B. Un'interfaccia FXS fornisce il tono di chiamata e l'alimentazione di squillo a un telefono analogico standard, fax o modem.
   - C. Un'interfaccia FXS è il modo corretto per collegare Asterisk a una linea telefonica del gestore.
   - D. Un'interfaccia FXO può anche essere collegata a una porta di estensione di un PBX legacy.
2. Il segnale di supervisione su una linea analogica include quale delle seguenti opzioni (scegli tutte le opzioni valide)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pop e rumore su una scheda analogica DAHDI sono più spesso causati da:
   - A. Il modo in cui Asterisk è stato compilato
   - B. Conflitti di interrupt PCI
   - C. Un codec SIP errato
   - D. Un dial plan mancante
4. Per una fatturazione precisa sui canali analogici è necessario rilevare esattamente quando l'estremità remota risponde. Quale funzionalità attivi su Asterisk (e richiedi al gestore) per farlo?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Generazione del tono di chiamata
5. L'hardware DAHDI è indipendente da Asterisk: la scheda fisica è configurata in `/etc/dahdi/system.conf`, mentre `chan_dahdi.conf` definisce i canali Asterisk, non l'hardware stesso.
   - A. True
   - B. False
6. Riguardo alla capacità dei trunk digitali e al segnale, indica le affermazioni corrette (scegli tutte le opzioni valide):
   - A. Un trunk E1 trasporta 30 canali vocali e un trunk T1 ne trasporta 24.
   - B. Un ISDN PRI utilizza 30B+D su un E1 e 23B+D su un T1.
   - C. ISDN è un esempio di segnalazione CCS, mentre MFC/R2 è un esempio di segnalazione CAS.
   - D. Il T1 è il trunk digitale più comunemente usato in Europa e America Latina.
7. Quale utility rileva automaticamente le schede DAHDI e genera `/etc/dahdi/system.conf` e `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. Quando si migra un legacy `sip.conf` `[friend]` a PJSIP, un singolo blocco deve essere suddiviso in più oggetti. Quale insieme di oggetti PJSIP `type=` normalmente sostituisce un unico `[friend]` di registrazione?
   - A. `type=endpoint`, `type=aor` e `type=auth`
   - B. `type=peer` e `type=user`
   - C. `type=sip` only
   - D. `type=channel` e `type=device`
9. Qual è il principale vantaggio pratico dell'utilizzare la modalità trunk IAX2 tra due server Asterisk?
   - A. Cripta ogni chiamata con TLS per impostazione predefinita
   - B. Trasporta più chiamate sotto un unico header, risparmiando larghezza di banda
   - C. Elimina la necessità di qualsiasi codec
   - D. Assegna una porta UDP separata per chiamata per una migliore qualità
10. Le chiavi RSA possono essere usate per l'autenticazione IAX2. Quale chiave devi mantenere segreta e quale devi fornire all'altro server?
    - A. Mantieni segreta la chiave pubblica; condividi la chiave privata
    - B. Mantieni segreta la chiave privata; condividi la chiave pubblica
    - C. Mantieni segreta la chiave condivisa; condividi la chiave privata
    - D. Entrambe le chiavi devono essere condivise

**Answers:** 1 — A, B, D · 2
