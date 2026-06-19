# Installazione di Asterisk 22

Nel primo capitolo abbiamo imparato qualcosa su come Asterisk sia utile nell'ambiente della telefonia. In questo capitolo, vedremo come scaricare e installare Asterisk. Prima di iniziare, è essenziale imparare come compilarlo e installarlo. Il processo di compilazione può sembrare strano per i tradizionali utenti Microsoft™ Windows™, ma è piuttosto comune nell'ambiente Linux™. Quando si compila Asterisk, è possibile ottenere un codice ottimizzato per il proprio hardware, che è ciò che faremo qui. Asterisk funziona su diversi sistemi operativi, ma abbiamo scelto di semplificare le cose e iniziare con uno solo di essi: Linux. Abbiamo scelto Debian come distribuzione Linux™ perché le dipendenze sono facili da installare e la distribuzione è stabile, con un ingombro ridotto. Se si desidera utilizzare un'altra distribuzione, si prega di modificare il nome delle dipendenze di conseguenza.

Questa edizione è rivolta ad **Asterisk 22 LTS** (rilasciata il 16-10-2024; supporto completo fino al 16-10-2028, correzioni di sicurezza fino al 16-10-2029). Asterisk 22 è l'attuale release a lungo termine. Si noti che Digium è stata acquisita da **Sangoma** nel 2018 e Asterisk è ora sponsorizzato da Sangoma — i riferimenti a "Digium" in tutto questo capitolo si riferiscono al marchio storico per l'hardware legacy.

## Obiettivi

Alla fine di questo capitolo dovresti essere in grado di:

- Determinare i requisiti hardware per Asterisk;
- Installare Linux con le dipendenze richieste;
- Scaricare una versione stabile tramite HTTPS;
- Compilare Asterisk; e
- Imparare come avviare Asterisk all'avvio del sistema.

## Hardware minimo richiesto

Asterisk non necessita di molto hardware per funzionare, tuttavia ci sono alcuni suggerimenti per scegliere l'hardware migliore per le proprie esigenze. Dovresti prendere in considerazione i seguenti fattori principali quando scegli il tuo hardware:

- Numero totale di utenti registrati. Definisci quante registrazioni al secondo devi supportare
- Numero totale di chiamate simultanee. Definisci quante conversazioni di rete devi elaborare nella scheda di rete e nel bridge sul server Asterisk
- Quali codec devi supportare. I codec ad alta complessità richiederanno molta potenza CPU/FPU nel tuo server; iLBC, ad esempio, è stato misurato dal suo creatore (Global IP Sound) a circa 18 MIPS per canale per frame da 30 ms (e circa 15 MIPS per frame da 20 ms) su un DSP TI C54x
- Cancellazione dell'eco. La cancellazione dell'eco può richiedere molta CPU/FPU, in alcuni casi dovresti scegliere la cancellazione dell'eco hardware utilizzando DSP nella scheda di interfaccia telefonica
- Disponibilità. Utilizza RAID1 o 5 per aumentare la disponibilità. Ricorda, Asterisk è un'applicazione 24x7.

Il componente principale per un server Asterisk è la scheda di rete. Si raccomanda una buona scheda di rete per server. La CPU è importante quando è necessario supportare codec ad alta complessità come g.729 e iLBC e la cancellazione dell'eco. Potresti scegliere di utilizzare DSP dedicati, Sangoma (precedentemente Digium) fornisce una scheda DSP chiamata TC400B in grado di supportare 120 chiamate simultanee g729. La best practice è scegliere un computer nuovo, di classe server, da un produttore noto. Per sapere esattamente quante chiamate simultanee o quanti utenti registrati può supportare una specifica macchina, dovresti testare questo hardware con uno strumento di stress test come SIPP (http://sipp.sourceforge.net). Alcuni produttori di hardware come Xorcom (http://www.xorcom.com) pubblicano i propri risultati sul sito web. Nota: alcune applicazioni Asterisk, come ConfBridge e la musica d'attesa, necessitano di una sorgente di temporizzazione interna. Sui moderni sistemi Linux, questa viene fornita automaticamente dal modulo integrato `res_timing_timerfd` — non è richiesto alcun hardware telefonico. (Il vecchio timer software `dahdi_dummy` non esiste più; la sua funzionalità è stata integrata nel modulo kernel principale `dahdi` in DAHDI Linux 2.3.0.) Puoi confermare il timer attivo con il comando CLI `timing test`.

### Configurazione hardware

L'hardware di Asterisk non deve essere sofisticato. Non hai bisogno di una scheda video costosa o di numerose periferiche. Alcuni suggerimenti sulla configurazione hardware:

- Disabilita le porte USB, seriali e parallele inutilizzate per evitare il consumo di interrupt non necessari.
- Una robusta scheda di interfaccia di rete è essenziale.
- Presta particolare attenzione se stai utilizzando schede di interfaccia telefonica. Alcune schede utilizzano un bus PCI a 3,3 volt e non è facile trovare schede madri per esse. Al giorno d'oggi, il PCI express è più facilmente reperibile.
- Presta molta attenzione al disco rigido, i PBX lavorano in regime 24x7 mentre i desktop lavorano 8x5. Non utilizzare hardware desktop per un PBX, solitamente il disco rigido si guasta prima del primo anno. La mia raccomandazione è di utilizzare una macchina server o un'appliance progettata per eseguire applicazioni 24x7.

### Condivisione IRQ

Le schede di interfaccia telefonica (es. X100P) generano grandi quantità di interruzioni. Servire queste interruzioni richiede tempo di processore. I driver non possono eseguire questa elaborazione se hai un altro dispositivo che utilizza la stessa interruzione. In un sistema a CPU singola, dovresti evitare la condivisione IRQ tra i dispositivi. Raccomandiamo l'uso di hardware dedicato per eseguire Asterisk. Non dimenticare di disabilitare qualsiasi hardware estraneo o non necessario. Alcuni hardware possono essere disabilitati nel setup del BIOS della scheda madre. Una volta avviato il computer, visualizza le interruzioni assegnate in /proc/interrupts.

```
#cat /proc/interrupts
CPU0
0: 41353058 XT-PIC timer
1: 1988 XT-PIC keyboard
2: 0 XT-PIC cascade
3: 413437739 XT-PIC wctdm <-- TDM400
4: 5721494 XT-PIC eth0
7: 413453581 XT-PIC wcfxo <-- X100P
8: 1 XT-PIC rtc
9: 413445182 XT-PIC wcfxo <-- X100P
12: 0 XT-PIC PS/2 Mouse
14: 179578 XT-PIC ide0
15: 3 XT-PIC ide1
NMI: 0
ERR: 0
```

Qui puoi vedere tre schede Digium, ognuna nel proprio IRQ. Se questo è il caso nel tuo sistema, procedi e installa i driver hardware. Se non è così, torna indietro e prova qualcos'altro per evitare la condivisione IRQ.

## Scelta di una distribuzione Linux

Asterisk è stato inizialmente sviluppato per funzionare su Linux. Tuttavia, può anche funzionare su BSD Unix o macOS. Se sei nuovo ad Asterisk, prova prima a usare Linux poiché è molto più semplice. Asterisk punta ufficialmente alla famiglia RHEL (CentOS/RHEL/Fedora), Ubuntu e Debian. Buone scelte pratiche oggi sono **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS** e **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux è a fine vita, quindi preferisci Rocky o AlmaLinux sui sistemi della famiglia RHEL. Per questo libro userò Ubuntu 24.04 LTS. Scarica l'ultima immagine server point-release 24.04 dalla directory delle release ufficiali qui sotto (il nome file esatto include la point-release corrente, es. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparazione di Linux per Asterisk

Immediatamente dopo aver installato Asterisk, installeremo i pacchetti richiesti per la successiva compilazione di Asterisk e dei driver DAHDI. Per prima cosa, indicheremo a Debian da dove verranno scaricati i pacchetti. Questo viene fatto utilizzando l'utility apt-setup. Passaggio 1: Installa Ubuntu 24.04 LTS Server in una macchina virtuale (usa l'immagine a 64 bit; le distribuzioni utilizzate in questo libro sono a 64 bit, sebbene Asterisk stesso supporti ancora x86 a 32 bit). Abbiamo utilizzato VirtualBox per questa formazione. Puoi scaricare l'immagine da https://releases.ubuntu.com/24.04 L'installazione di Linux esula dallo scopo di questa formazione. La conoscenza di base di Linux è un prerequisito per questa formazione.

## Installazione di Linux per Asterisk

Installa il tuo Linux come al solito, senza un'interfaccia utente grafica. Installa e configura anche il server di posta. Avremo bisogno del server di posta (exim4) per inviare notifiche di segreteria telefonica più avanti in questo libro. Attenzione: questa installazione formatterà il tuo PC. Tutti i dati del disco verranno cancellati. Assicurati di eseguire il backup di tutti i dati prima di iniziare. Passaggio 1: Inserisci il CD nell'unità CD-ROM e avvia il tuo PC. La maggior parte delle domande sono molto semplici a cui rispondere.

## Installazione delle dipendenze

Per installare Asterisk e DAHDI devi installare molte dipendenze software. Il modo consigliato per farlo in Asterisk 22 è utilizzare lo script fornito con l'albero dei sorgenti, che conosce i nomi corretti dei pacchetti per ogni distribuzione supportata. Dopo aver scaricato ed estratto i sorgenti di Asterisk (vedi "Compilazione di Asterisk" di seguito), esegui:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

Passaggio 1: Accedi come root (o usa `sudo`). Passaggio 2: Se preferisci installare le dipendenze manualmente su un sistema Debian/Ubuntu, l'elenco dei pacchetti equivalente è:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

Si noti che i sorgenti di Asterisk sono ora ospitati su Git, quindi `subversion` non è più necessario e le moderne Debian/Ubuntu forniscono `libncurses-dev` piuttosto che la versione `libncurses5-dev`. Preferisci `./contrib/scripts/install_prereq install` rispetto a un elenco gestito manualmente, poiché lo script tiene sempre traccia dei nomi corretti dei pacchetti per la tua distribuzione.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) è l'architettura dei driver per schede analogiche e digitali. Prima di installare Asterisk è importante installare DAHDI se hai intenzione di utilizzare interfacce analogiche o digitali. DAHDI esiste ancora per le schede telefoniche analogiche/digitali ma è sempre più di nicchia — la maggior parte delle implementazioni moderne sono puramente VoIP e possono saltare completamente questa sezione. Installa DAHDI solo se disponi di hardware di interfaccia telefonica fisico. Ottieni i file sorgente usando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Decomprimi i file usando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compilazione dei driver DAHDI

Dovrai compilare i moduli DAHDI. I comandi ./configure e make menuselect sono stati introdotti diversi anni fa. Quest'ultimo ti consente di selezionare quali utility e moduli compilare. I seguenti comandi faranno questo:

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config DAHDI è stato configurato. Se disponi di hardware DAHDI, ora si consiglia di modificare /etc/dahdi/modules per caricare il supporto solo per l'hardware DAHDI installato in questo sistema. Per impostazione predefinita, il supporto per tutto l'hardware DAHDI viene caricato all'avvio di DAHDI. Penso che l'hardware DAHDI che hai sul tuo sistema sia: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware Questa schermata (sopra) ti chiede di modificare il file /etc/dahdi/modules per caricare solo i driver richiesti per la tua configurazione specifica e mostrare l'hardware rilevato. Modifica il file /etc/dahdi/modules e carica solo l'hardware richiesto. Nel mio caso, stavo usando una macchina di test con un Xorcom Astribank 6FXS e 2FXO. Il file è mostrato di seguito.

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

Reinizializza il tuo computer e verifica il corretto caricamento dei driver.

## Quale versione scegliere

Come regola generale, dovresti usare la versione con le funzionalità richieste. Asterisk segue un modello di rilascio che alterna versioni LTS (supporto a lungo termine) e versioni standard. Al momento di questa edizione, **Asterisk 22 è l'attuale release LTS** (rilasciata nell'ottobre 2024; l'ultima point-release è la 22.10.0), il che la rende la migliore da scegliere ora. Asterisk 20 è la precedente LTS e la versione 16 (utilizzata nella prima edizione) è a fine vita. Per i sistemi di produzione, scegli sempre una release LTS.

## Compilazione di Asterisk

Se hai già compilato software in precedenza, compilare Asterisk sarà un compito facile. Esegui i seguenti comandi per compilare e installare Asterisk. Ricorda, puoi scegliere quali applicazioni e moduli compilare usando make menuselect. Passaggio 1: Scarica il codice sorgente

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Passaggio 2: Installa i prerequisiti di compilazione (vedi "Installazione delle dipendenze" sopra)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Passaggio 3: Configura la compilazione

```
./configure
```

Passaggio 4: Seleziona i moduli da compilare

```
make menuselect
```

Usa make menuselect per installare solo i moduli necessari. In Asterisk 22 il canale SIP è **chan_pjsip** (compilato per impostazione predefinita); il vecchio **chan_sip** è stato rimosso in Asterisk 21 e non esiste più. Il *pass-through* Opus funziona immediatamente (il modulo integrato `res_format_attr_opus` gestisce la negoziazione SDP), ma il modulo di transcodifica **codec_opus** è ancora un binario esterno a codice chiuso di Sangoma/Digium — selezionandolo in menuselect lo si scarica dai server di Digium. Il binario è gratuito. Vedi "Selezione dei moduli con menuselect" di seguito per i dettagli.

Passaggio 5: Compila e installa Asterisk, quindi crea la configurazione predefinita e i file di esempio

```
make
make install
make samples
make config
ldconfig
```

`make install` installa i binari e i moduli, `make samples` scrive i file di configurazione di esempio in `/etc/asterisk`, `make config` installa lo script di avvio SysV init per la tua distribuzione rilevata (es. `/etc/init.d/asterisk` su Debian/Ubuntu) e `ldconfig` aggiorna la cache delle librerie condivise. Un'unità systemd è presente anche nell'albero dei sorgenti in `contrib/systemd/asterisk.service`, ma `make config` non la installa automaticamente — copiala al suo posto se preferisci eseguire Asterisk sotto systemd (vedi sotto).

### Selezione dei moduli con menuselect

`make menuselect` apre un menu basato su testo dove scegli esattamente quali applicazioni, codec, canali e risorse compilare. Alcune note specifiche per Asterisk 22:

- **chan_pjsip** (sotto *Channel Drivers*) è il moderno canale SIP ed è abilitato per impostazione predefinita; è l'unico canale SIP in Asterisk 22.
- **codec_opus** (sotto *Codec Translators*) è un modulo **esterno** (la sua voce in menuselect recita "Download the Opus codec from Digium"); abilitandolo, `make` recupera il binario gratuito a codice chiuso da Sangoma/Digium. Il pass-through Opus di per sé non necessita di alcun modulo aggiuntivo. È disponibile anche il modulo **codec_g729** di Sangoma — il binario è scaricabile gratuitamente, ma la transcodifica G.729 legale richiede una licenza per canale acquistata.
- Seleziona i formati audio e le lingue che desideri nei menu *Core Sound Packages*, *Music On Hold File Packages* e *Extras Sound Packages*; tutto ciò che spunti lì viene scaricato e installato automaticamente durante `make install`.

Dopo aver effettuato le selezioni, scegli **Save & Exit** e continua con `make`.

## Avvio e arresto di Asterisk

Con questa configurazione minima, è possibile avviare Asterisk con successo. Per l'apprendimento e il debug, puoi avviare Asterisk in primo piano collegato alla console:

```
/usr/sbin/asterisk –vvvgc
```

Usa il comando CLI stop now per arrestare Asterisk.

```
CLI>core stop now
```

### Avvio di Asterisk con systemd

Sulle moderne distribuzioni Linux (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), il gestore dei servizi di sistema è **systemd**. Asterisk fornisce un'unità systemd in `contrib/systemd/asterisk.service` nell'albero dei sorgenti; copiala in `/etc/systemd/system/asterisk.service` ed esegui `systemctl daemon-reload`. Una volta installato, il modo consigliato per eseguire Asterisk in produzione è tramite `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Una volta che Asterisk è in esecuzione come servizio, collegati alla sua CLI con `asterisk -r` (connessione) o `asterisk -rvvv` (connessione con output dettagliato).

Sui sistemi più vecchi Asterisk veniva avviato tramite lo script init SysV legacy (`/etc/init.d/asterisk`) e il wrapper **safe_asterisk**, che riavviava Asterisk automaticamente in caso di crash. Con systemd, il riavvio automatico è gestito dalla direttiva `Restart=` del file unit, quindi `safe_asterisk` non è generalmente più necessario. L'approccio legacy init/`safe_asterisk` funziona ancora ma è deprecato sulle distribuzioni basate su systemd.

### Opzioni di runtime di Asterisk

Il processo di avvio di Asterisk è molto semplice. Se Asterisk viene eseguito senza parametri, viene lanciato come demone.

```
/sbin/asterisk
```

Puoi accedere alla console di Asterisk eseguendo il seguente comando. Si prega di notare che più di un processo di console può essere eseguito contemporaneamente.

```
/sbin/asterisk -r
```

### Opzioni di runtime disponibili per Asterisk

Puoi mostrare le opzioni di runtime disponibili usando asterisk –h

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation e altri. Utilizzo: asterisk [OPTIONS] Opzioni valide: -V Visualizza il numero di versione ed esci -C <configfile> Usa un file di configurazione alternativo -G <group> Esegui come gruppo diverso dal chiamante -U <user> Esegui come utente diverso dal chiamante -c Fornisci CLI console -d Aumenta il debug (più d = più debug) -f Non effettuare il fork -F Effettua sempre il fork -g Scarica il core in caso di crash -h Questa schermata di aiuto -i Inizializza le chiavi crittografiche all'avvio -L <load> Limita il carico massimo medio prima di rifiutare nuove chiamate -M <value> Limita il numero massimo di chiamate al valore specificato -m Disattiva il debug e l'output della console sulla console -n Disabilita la colorazione della console. Può essere usato solo all'avvio. -p Esegui come thread pseudo-realtime -q Modalità silenziosa (sopprimi l'output) -r Connettiti ad Asterisk su questa macchina -R Come -r, eccetto tenta di riconnettersi se disconnesso -s <socket> Connettiti ad Asterisk tramite socket <socket> (valido solo con -r) -t Registra i file audio in /var/tmp e spostali dove appartengono dopo che hanno finito -T Visualizza l'ora nel formato [Mmm dd hh:mm:ss] per ogni riga di output sulla CLI. Non può essere usato con la modalità console remota. -v Aumenta la verbosità (più v = più dettagliato) -x <cmd> Esegui il comando <cmd> (implica -r) -X Abilita l'uso di #exec in asterisk.conf -W Regola i colori del terminale per compensare uno sfondo chiaro

## Directory di installazione

Asterisk è installato in diverse directory, che possono essere modificate nel file asterisk.conf. Per scopi di formazione cambierei la verbosità da 3 a 15, per la produzione mantienila a 3. Le opzioni max_calls e max_load sono buone opzioni per proteggere il tuo sistema dal sovraccarico.

### asterisk.conf

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
[options]
;verbose = 3
;debug = 3
;refdebug = yes                 ; Enable reference count debug logging.
;alwaysfork = yes               ; Same as -F at startup.
;nofork = yes                   ; Same as -f at startup.
;quiet = yes                    ; Same as -q at startup.
;timestamp = yes                ; Same as -T at startup.
;execincludes = yes             ; Support #exec in config files.
;console = yes                  ; Run as console (same as -c at startup).
;highpriority = yes             ; Run realtime priority (same as -p at
                                ; startup).
;initcrypto = yes               ; Initialize crypto keys (same as -i at
                                ; startup).
;nocolor = yes                  ; Disable console colors.
;dontwarn = yes                 ; Disable some warnings.
;dumpcore = yes                 ; Dump core on crash (same as -g at startup).
;languageprefix = yes           ; Use the new sound prefix path syntax.
;systemname = my_system_name    ; Prefix uniqueid with a system name for
                                ; Global uniqueness issues.
;autosystemname = yes           ; Automatically set systemname to hostname,
                                ; uses 'localhost' on failure, or systemname if
                                ; set.
;mindtmfduration = 80           ; Set minimum DTMF duration in ms (default 80
ms)
                                ; If we get shorter DTMF messages, these will
be
                                ; changed to the minimum duration
;maxcalls = 10                  ; Maximum amount of calls allowed.
;maxload = 0.9                  ; Asterisk stops accepting new calls if the
                                ; load average exceed this limit.
;maxfiles = 1000                ; Maximum amount of openfiles.
;minmemfree = 1                 ; In MBs, Asterisk stops accepting new calls if
                                ; the amount of free memory falls below this
                                ; watermark.
;cache_media_frames = yes       ; Cache media frames for performance
                                ; Disable this option to help track down media
frame
                                ; mismanagement when using valgrind or
MALLOC_DEBUG.
                                ; The cache gets in the way of determining if
the
                                ; frame is used after being freed and who freed
it.
                                ; NOTE: This option has no effect when Asterisk
is
                                ; compiled with the LOW_MEMORY compile time
option
                                ; enabled because the cache code does not
exist.
                                ; Default yes
;cache_record_files = yes       ; Cache recorded sound files to another
                                ; directory during recording.
;record_cache_dir = /tmp        ; Specify cache directory (used in conjunction
                                ; with cache_record_files).
;transmit_silence = yes         ; Transmit silence while a channel is in a
                                ; waiting state, a recording only state, or
                                ; when DTMF is being generated.  Note that the
                                ; silence internally is generated in raw signed
                                ; linear format. This means that it must be
                                ; transcoded into the native format of the
                                ; channel before it can be sent to the device.
                                ; It is for this reason that this is optional,
                                ; as it may result in requiring a temporary
                                ; codec translation path for a channel that may
                                ; not otherwise require one.
;transcode_via_sln = yes        ; Build transcode paths via SLINEAR, instead of
                                ; directly.
;runuser = asterisk             ; The user to run as.
;rungroup = asterisk            ; The group to run as.
;lightbackground = yes          ; If your terminal is set for a light-colored
                                ; background.
;forceblackbackground = yes     ; Force the background of the terminal to be
                                ; black, in order for terminal colors to show
                                ; up properly.
;defaultlanguage = en           ; Default language
documentation_language = en_US  ; Set the language you want documentation
                                ; displayed in. Value is in the same format as
                                ; locale names.
;hideconnect = yes              ; Hide messages displayed when a remote console
                                ; connects and disconnects.
;lockconfdir = no               ; Protect the directory containing the
                                ; configuration files (/etc/asterisk) with a
                                ; lock.
;live_dangerously = no          ; Enable the execution of 'dangerous' dialplan
                                ; functions from external sources (AMI,
                                ; etc.) These functions (such as SHELL) are
                                ; considered dangerous because they can allow
                                ; privilege escalation.
                                ; Default no
;entityid=00:11:22:33:44:55     ; Entity ID.
                                ; This is in the form of a MAC address.
                                ; It should be universally unique.
                                ; It must be unique between servers
communicating
                                ; with a protocol that uses this value.
                                ; This is currently is used by DUNDi and
                                ; Exchanging Device and Mailbox State
                                ; using protocols: XMPP, Corosync and PJSIP.
;rtp_use_dynamic = yes          ; When set to "yes" RTP dynamic payload types
                                ; are assigned dynamically per RTP instance vs.
                                ; allowing Asterisk to globally initialize them
                                ; to pre-designated numbers (defaults to
"yes").
;rtp_pt_dynamic = 35            ; Normally the Dynamic RTP Payload Type numbers
                                ; are 96-127, which allow just 32 formats. The
                                ; starting point 35 enables the range 35-63 and
                                ; allows 29 additional formats. When you use
                                ; more than 32 formats in the dynamic range and
                                ; calls are not accepted by a remote
                                ; implementation, please report this and go
                                ; back to value 96.
; Changing the following lines may compromise your security.
;[files]
;astctlpermissions = 0660
;astctlowner = root
;astctlgroup = apache
;astctl = asterisk.ctl
```

## File di log e rotazione dei log

Il PBX Asterisk registra i suoi messaggi nella directory /var/log/asterisk. Il file che controlla i log

```
is the logger.conf.
;
; Logging Configuration
;
; In this file, you configure logging to files or to
; the syslog system.
;
; "logger reload" at the CLI will reload configuration
; of the logging system.
[general]
;
; Customize the display of debug message time stamps
; this example is the ISO 8601 date format (yyyy-mm-dd HH:MM:SS)
;
; see strftime(3) Linux manual for format specifiers.  Note that there is also
; a fractional second parameter which may be used in this field.  Use %1q
; for tenths, %2q for hundredths, etc.
;
;dateformat=%F %T       ; ISO 8601 date format
;dateformat=%F %T.%3q   ; with milliseconds
;
;
; This makes Asterisk write callids to log messages
; (defaults to yes)
;use_callids = no
;
; This appends the hostname to the name of the log files.
;appendhostname = yes
;
; This determines whether or not we log queue events to a file
; (defaults to yes).
;queue_log = no
;
; Determines whether the queue_log always goes to a file, even
; when a realtime backend is present (defaults to no).
;queue_log_to_file = yes
;
; Set the queue_log filename
; (defaults to queue_log)
;queue_log_name = queue_log
;
; When using realtime for the queue log, use GMT for the timestamp
; instead of localtime.  The default of this option is 'no'.
;queue_log_realtime_use_gmt = yes
;
; Log rotation strategy:
; none:  Do not perform any logrotation at all.  You should make
;        very sure to set up some external logrotate mechanism
;        as the asterisk logs can get very large, very quickly.
; sequential:  Rename archived logs in order, such that the newest
;              has the highest sequence number [default].  When
;              exec_after_rotate is set, ${filename} will specify
;              the new archived logfile.
; rotate:  Rotate all the old files, such that the oldest has the
;          highest sequence number [this is the expected behavior
;          for Unix administrators].  When exec_after_rotate is
;          set, ${filename} will specify the original root filename.
; timestamp:  Rename the logfiles using a timestamp instead of a
;             sequence number when "logger rotate" is executed.
;             When exec_after_rotate is set, ${filename} will
;             specify the new archived logfile.
;rotatestrategy = rotate
;
; Run a system command after rotating the files.  This is mainly
; useful for rotatestrategy=rotate. The example allows the last
; two archive files to remain uncompressed, but after that point,
; they are compressed on disk.
;
; exec_after_rotate=gzip -9 ${filename}.2
;
;
; For each file, specify what to log.
;
; For console logging, you set options at start of
; Asterisk with -v for verbose and -d for debug
; See 'asterisk -h' for more information.
;
; Directory for log files is configures in asterisk.conf
; option astlogdir
;
; All log messages go to a queue serviced by a single thread
; which does all the IO.  This setting controls how big that
; queue can get (and therefore how much memory is allocated)
; before new messages are discarded.
; The default is 1000
;logger_queue_limit = 250
;
;
[logfiles]
;
; Format is:
;
; logger_name => [formatter]levels
;
; The name of the logger dictates not only the name of the logging
; channel, but also its type. Valid types are:
;   - 'console'  - The root console of Asterisk
;   - 'syslog'   - Linux syslog, with facilities specified afterwards with
;                  a period delimiter, e.g., 'syslog.local0'
;   - 'filename' - The name of the log file to create. This is the default
;                  for log channels.
;
; Filenames can either be relative to the standard Asterisk log directory
; (see 'astlogdir' in asterisk.conf), or absolute paths that begin with
; '/'.
;
; An optional formatter can be specified prior to the log levels sent
; to the log channel. The formatter is defined immediately preceeding the
; levels, and is enclosed in square brackets. Valid formatters are:
;   - [default] - The default formatter, this outputs log messages using a
;                 human readable format.
;   - [json]    - Log the output in JSON. Note that JSON formatted log entries,
;                 if specified for a logger type of 'console', will be formatted
;                 per the 'default' formatter for log messages of type VERBOSE.
;                 This is due to the remote consoles intepreting verbosity
;                 outside of the logging subsystem.
;
; Log levels include the following, and are specified in a comma delineated
; list:
;    debug
;    notice
;    warning
;    error
;    verbose(<level>)
;    dtmf
;    fax
;    security
;
; Verbose takes an optional argument, in the form of an integer level.
; Verbose messages with higher levels will not be logged to the file.  If
; the verbose level is not specified, it will log verbose messages following
; the current level of the root console.
;
; Special level name "*" means all levels, even dynamic levels registered
; by modules after the logger has been initialized (this means that loading
; and unloading modules that create/remove dynamic logger levels will result
; in these levels being included on filenames that have a level name of "*",
; without any need to perform a 'logger reload' or similar operation).
; Note that there is no value in specifying both "*" and specific level names
; for a filename; the "*" level means all levels.  The only exception is if
; you need to specify a specific verbose level. e.g, "verbose(3),*".
;
; We highly recommend that you DO NOT turn on debug mode if you are simply
; running a production system.  Debug mode turns on a LOT of extra messages,
; most of which you are unlikely to understand without an understanding of
; the underlying code.  Do NOT report debug messages as code issues, unless
; you have a specific issue that you are attempting to debug.  They are
; messages for just that -- debugging -- and do not rise to the level of
; something that merit your attention as an Asterisk administrator.  Debug
; messages are also very verbose and can and do fill up logfiles quickly;
; this is another reason not to have debug mode on a production system unless
; you are in the process of debugging a specific issue.
;
;debug => debug
;security => security
console => notice,warning,error
;console => notice,warning,error,debug
messages => notice,warning,error
;full => notice,warning,error,debug,verbose,dtmf,fax
;
;full-json => [json]debug,verbose,notice,warning,error,dtmf,fax
;
;syslog keyword : This special keyword logs to syslog facility
;
;syslog.local0 => notice,warning,error
```

; Alcuni comandi della console sono associati al processo logger.

```
CLI> logger show channels
Logger queue limit: 1000

Channel                             Type     Formatter  Status    Configuration
-------                             ----     ---------  ------    -------------
/var/log/asterisk/security          File     default    Enabled    - SECURITY
/var/log/asterisk/full              File     default    Enabled    - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages          File     default    Enabled    - NOTICE WARNING ERROR
CLI> logger rotate
  == Parsing '/etc/asterisk/logger.conf': Found
Asterisk Event Logger restarted
Asterisk Queue Logger restarted
You can control the log rotation using the logrotate daemon. Edit the file
/etc/logrotate.d and include the content below to start rotating the log files.
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

Maggiori informazioni su logrotate possono essere ottenute usando:

```
#man logrotate
```

## Disinstallazione di Asterisk

Per disinstallare Asterisk, usa:

```
make uninstall
```

Per disinstallare Asterisk e tutti i file di configurazione, usa:

```
make uninstall-all
```

## Note sull'installazione di Asterisk

Questa sezione fornirà alcuni consigli sui problemi da affrontare prima di installare Asterisk.

### Sistemi di produzione

Se Asterisk è installato in un ambiente di produzione, dovresti prestare attenzione alla progettazione del sistema. Un server deve essere ottimizzato in modo tale che i sistemi di telefonia abbiano la priorità rispetto ad altri processi di sistema. Asterisk non dovrebbe essere eseguito insieme a software ad alta intensità di processore come X-Windows. Se hai bisogno di eseguire processi ad alta intensità di CPU (es. un database enorme), usa un server separato. In generale, Asterisk è suscettibile alle variazioni delle prestazioni hardware. Pertanto, prova a utilizzare Asterisk in un ambiente hardware che non richieda più del 40% di utilizzo della CPU.

### Suggerimenti di rete

Se prevedi di utilizzare telefoni IP, è importante prestare attenzione alla tua rete. I protocolli vocali sono molto buoni e resistenti alla latenza e persino al jitter; tuttavia, se utilizzi una rete locale configurata male, la qualità vocale ne risentirà. È possibile garantire una buona qualità vocale solo utilizzando la qualità del servizio (QoS) in switch e router. La voce in una rete locale tende ad essere buona, ma anche in un ambiente LAN, se hai hub da 10 Mbps con troppe collisioni, finirai per avere una voce distorta o scadente. Segui queste raccomandazioni per garantire la migliore qualità vocale possibile:

- Usa QoS end-to-end se possibile o economicamente fattibile. Con QoS end-to-end, la qualità vocale è perfetta. Nessuna scusa!
- Evita di utilizzare hub da 10/100 Mbps per la voce in un ambiente di produzione. Le collisioni possono imporre jitter sulla rete. Sono preferibili 10/100 Mbps full duplex perché non si verificano collisioni.
- Usa le VLAN per separare i broadcast non necessari della rete vocale. Non vuoi che un virus distrugga la tua rete vocale con broadcast ARP.
- Educa gli utenti sulle aspettative in una rete vocale. Senza QoS, non affermare che la voce sarà perfetta poiché nella maggior parte dei casi non lo sarà. Molto spesso si otterrà una qualità vocale simile a quella di un telefono cellulare. Usa telefoni di qualità poiché i problemi con il firmware e la progettazione hardware sono comuni.

## Riepilogo

In questo capitolo, hai imparato i requisiti hardware minimi e come scaricare, installare e compilare Asterisk. Asterisk dovrebbe essere eseguito con un utente non root per motivi di sicurezza. Dovresti controllare il tuo ambiente di rete prima di avviare l'ambiente di produzione.

## Quiz

1. In Asterisk 22, quale driver di canale fornisce il supporto SIP e cosa è successo al vecchio `chan_sip`?
   - A. `chan_sip` è ancora il predefinito; `chan_pjsip` è opzionale.
   - B. `chan_pjsip` è il canale SIP predefinito; `chan_sip` è stato rimosso in Asterisk 21 e non esiste più.
   - C. Entrambi sono compilati per impostazione predefinita e scegli tra loro in fase di runtime.
   - D. Il supporto SIP è stato rimosso interamente a favore di IAX2.
2. Le schede di interfaccia telefonica per Asterisk solitamente hanno processori di segnale digitale (DSP) integrati e quindi non necessitano di molta CPU dal PC.
   - A. Vero
   - B. Falso
3. Se vuoi una qualità vocale perfetta, devi implementare la qualità del servizio (QoS) end-to-end.
   - A. Vero
   - B. Falso
4. Dovresti sempre scegliere l'ultima versione di Asterisk, poiché è la più stabile.
   - A. Vero
   - B. Falso
5. Qual è il modo consigliato per installare le dipendenze di compilazione per Asterisk 22?
6. Se non hai una scheda di interfaccia TDM avrai comunque una sorgente di temporizzazione interna per la sincronizzazione, fornita dal modulo `res_timing_timerfd` su Linux. Questa temporizzazione è utilizzata da applicazioni come ________ e ________.
7. Quando si installa Asterisk è meglio lasciare fuori gli ambienti desktop come GNOME o KDE, perché le interfacce grafiche consumano cicli di CPU.
   - A. Vero
   - B. Falso
8. I file di configurazione di Asterisk si trovano nella directory ________.
9. Per installare i file di configurazione di esempio di Asterisk, digita il comando: ________
10. Perché è importante eseguire Asterisk come utente non root?

**Risposte:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Esegui `./contrib/scripts/install_prereq install` dall'albero dei sorgenti di Asterisk estratto · 6 — ConfBridge e Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Sicurezza (limita i danni se Asterisk viene compromesso)
