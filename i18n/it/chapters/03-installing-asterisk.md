# Installing Asterisk 22

Nel capitolo precedente abbiamo appreso un po' di come Asterisk sia utile nell'ambiente telefonico. In questo capitolo tratteremo come scaricare e installare Asterisk. Prima di iniziare, è fondamentale imparare come compilarlo e installarlo. Il processo di compilazione può sembrare strano per gli utenti tradizionali di Microsoft™ Windows™, ma è piuttosto comune nell'ambiente Linux™. Si può ottenere un codice ottimizzato per il proprio hardware compilando Asterisk, ed è proprio quello che faremo qui. Asterisk gira su diversi sistemi operativi, ma per semplicità ne utilizzeremo solo uno: Linux. Usiamo **Ubuntu 24.04 LTS** perché le sue dipendenze sono facili da installare ed è una distribuzione server stabile, ben supportata e a basso impatto. Se preferisci un'altra distribuzione, adatta i nomi dei pacchetti di conseguenza.

Questa edizione è rivolta a **Asterisk 22 LTS** (rilasciato il 2024-10-16; supporto completo fino al 2028-10-16, correzioni di sicurezza fino al 2029-10-16). Asterisk 22 è l'attuale versione a lungo termine. Nota che Digium è stata acquisita da **Sangoma** nel 2018, e Asterisk è ora sponsorizzato da Sangoma — i riferimenti a "Digium" in questo capitolo indicano il marchio storico per hardware legacy.

## Obiettivi

Entro la fine di questo capitolo dovresti essere in grado di:

- Determinare i requisiti hardware per Asterisk;
- Installare Linux con le dipendenze necessarie;
- Scaricare una versione stabile via HTTPS;
- Compilare Asterisk; e
- Imparare come avviare Asterisk all’avvio del sistema.

## Minimum Hardware Required

Asterisk non richiede molto hardware per funzionare, tuttavia ci sono alcuni consigli per scegliere l'hardware migliore per le tue esigenze. Dovresti tenere in considerazione i seguenti fattori principali quando scegli l'hardware:

- Numero totale di utenti registrati. Definisci quante registrazioni al secondo devi supportare
- Numero totale di chiamate simultanee. Definisci quante conversazioni di rete devi elaborare nell'adattatore di rete e nel bridge sul server Asterisk
- Quali codec devi supportare. I codec ad alta complessità richiederanno molta potenza CPU/FPU nel tuo server; iLBC, per esempio, è stato misurato dal suo creatore (Global IP Sound) a circa 18 MIPS per canale per frame da 30 ms (e circa 15 MIPS per frame da 20 ms) su un DSP TI C54x
- Cancellazione dell'eco. La cancellazione dell'eco può richiedere molta CPU/FPU; in alcuni casi dovresti scegliere la cancellazione dell'eco hardware usando DSP nella scheda di interfaccia telefonica
- Disponibilità. Usa RAID1 o 5 per aumentare la disponibilità. Ricorda, Asterisk è un'applicazione 24x7.

Il componente principale per un Server Asterisk è l'adattatore di rete. Si raccomanda un buon adattatore di rete per server. La CPU è importante quando devi supportare codec ad alta complessità come g.729 e iLBC e la cancellazione dell'eco. Puoi scegliere di delegare questo a DSP dedicati: Sangoma (ex Digium) fornisce una scheda DSP chiamata TC400B capace di supportare 120 chiamate simultanee G.729.

La best practice è scegliere un nuovo computer di classe server, da un produttore noto. Per sapere esattamente quante chiamate simultanee o quanti utenti registrati una macchina specifica può supportare, dovresti testare questo hardware con uno strumento di stress test come SIPP (http://sipp.sourceforge.net). Alcuni produttori di hardware come Xorcom (http://www.xorcom.com) pubblicano i risultati sul proprio sito web.

Nota: Alcune applicazioni Asterisk, come ConfBridge e musica in attesa, necessitano di una sorgente di temporizzazione interna. Su Linux moderno questo è fornito automaticamente dal modulo integrato `res_timing_timerfd` — non è richiesto hardware telefonico. (Il vecchio timer software `dahdi_dummy` non esiste più; la sua funzionalità è stata incorporata nel modulo kernel principale `dahdi` in DAHDI Linux 2.3.0.) Puoi confermare il timer attivo con il comando CLI `timing test`.

### Hardware configuration

L'hardware di Asterisk non deve essere sofisticato. Non ti serve una scheda video costosa né numerosi periferici. Alcuni consigli sulla configurazione hardware:

- Disabilita le porte USB, seriali e parallele inutilizzate per evitare il consumo di interruzioni non necessarie.
- Una scheda di rete robusta è essenziale.
- Presta particolare attenzione se usi schede di interfaccia telefonica. Alcune schede usano un bus PCI a 3,3 volt, e non è facile trovare schede madri compatibili. Oggi, il PCI Express è più facilmente reperibile.
- Presta molta attenzione al disco rigido; una PBX lavora in regime 24x7 mentre i desktop operano 8x5. Non usare hardware da desktop per una PBX, di solito il disco rigido fallisce prima del primo anno. La mia raccomandazione è usare una macchina server o un appliance progettato per eseguire applicazioni 24x7.

### IRQ sharing (legacy PCI cards only)

Questo avviso si applica **solo** se installi schede telefoniche fisiche PCI/PCI-Express (hardware DAHDI). Tali schede generano un gran numero di interruzioni e, su sistemi più vecchi a singola CPU, condividere una linea IRQ con un altro dispositivo potrebbe privare il driver delle risorse necessarie e degradare la qualità della voce. Se usi schede telefoniche, dedica la macchina ad Asterisk, disabilita eventuali dispositivi integrati inutilizzati nel BIOS e controlla le interruzioni assegnate con `cat /proc/interrupts`. I server moderni multicore che usano interruzioni MSI

## Scegliere una distribuzione Linux

Asterisk è stato inizialmente sviluppato per funzionare su Linux. Tuttavia, può anche girare su BSD Unix o macOS. Se sei nuovo a Asterisk, prova prima a usare Linux poiché è molto più semplice. Asterisk punta ufficialmente alle famiglie RHEL (CentOS/RHEL/Fedora), Ubuntu e Debian. Buone scelte pratiche oggi sono **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, e **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux è fuori vita, quindi preferisci Rocky o AlmaLinux sui sistemi della famiglia RHEL. Per questo libro utilizzerò Ubuntu 24.04 LTS. Scarica l’immagine server più recente della release 24.04 dal directory ufficiale dei rilasci qui sotto (il nome file esatto include il punto di rilascio corrente, ad es. `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparare Linux per Asterisk

Prima di compilare Asterisk è necessario un sistema Linux funzionante con i pacchetti di build installati. Installa **Ubuntu 24.04 LTS Server** in una macchina virtuale o su un box dedicato (usa l’immagine a 64‑bit; tutto in questo libro è a 64‑bit, anche se Asterisk stesso supporta ancora x86 a 32‑bit). Abbiamo usato VirtualBox per questo training; puoi scaricare l’immagine da <https://releases.ubuntu.com/24.04>. L’installazione di Linux stessa è fuori dall’ambito di questo libro — la conoscenza di base di Linux è un prerequisito. Con Linux installato, aggiungerai le dipendenze di build di Asterisk (vedi *Installing dependencies* più sotto) e poi compilerai Asterisk.

## Installing Linux for Asterisk

Installa Linux come di consueto, senza un desktop grafico. Durante l'installazione, abilita anche un agente di trasferimento mail (usiamo **exim4**) — Asterisk ne avrà bisogno per inviare le notifiche di voicemail‑to‑email più avanti in questo libro. **Attenzione:** l'installazione di un sistema operativo cancella il disco di destinazione. Se installi su hardware fisico, esegui prima il backup dei dati; installare in una macchina virtuale lascia intatto l'host. Avvia il programma di installazione dall'ISO di Ubuntu Server (o dall'unità ottica virtuale della VM) e rispondi alle richieste — la maggior parte è semplice.

## Installing dependencies

Per installare Asterisk e DAHDI è necessario installare molte dipendenze software. Il modo consigliato per farlo in Asterisk 22 è utilizzare lo script fornito con l’albero dei sorgenti, che conosce i nomi corretti dei pacchetti per ogni distribuzione supportata. Dopo aver scaricato e estratto i sorgenti di Asterisk (vedi “Compiling Asterisk” più sotto), esegui:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. Accedi come root (o usa `sudo`).
2. Se preferisci installare manualmente le dipendenze su un sistema Debian/Ubuntu, l’elenco di pacchetti equivalente è:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

Nota che il sorgente di Asterisk è ora ospitato su Git, quindi `subversion` non è più necessario, e le versioni moderne di Debian/Ubuntu forniscono `libncurses-dev` anziché il `libncurses5-dev` versionato. Preferisci `./contrib/scripts/install_prereq install` rispetto a un elenco mantenuto manualmente, poiché lo script traccia sempre i nomi corretti dei pacchetti per la tua distribuzione.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) è l’architettura dei driver per schede analogiche e digitali. Prima di installare Asterisk è importante installare DAHDI se prevedi di usare interfacce analogiche o digitali. DAHDI esiste ancora per le schede telefoniche analogiche/digitali, ma è sempre più di nicchia — la maggior parte delle implementazioni moderne è puramente VoIP e può saltare completamente questa sezione. Installa DAHDI solo se possiedi hardware di interfaccia telefonica fisico. Ottieni i file sorgente usando:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

Decomprimi i file usando:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

Dovrai compilare i moduli DAHDI. I comandi ./configure e make menuselect sono stati introdotti diversi anni fa. Quest’ultimo ti permette di selezionare quali utility e moduli costruire. I seguenti comandi eseguiranno questa operazione:

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

make install-config DAHDI è stato configurato. Se possiedi hardware DAHDI, ora è consigliato modificare /etc/dahdi/modules per caricare il supporto solo per l’hardware DAHDI presente in questo sistema. Per impostazione predefinita il supporto per tutto l’hardware DAHDI viene caricato all’avvio di DAHDI. Credo che l’hardware DAHDI presente sul tuo sistema sia: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware. Questa schermata (sopra) ti chiede di modificare il file /etc/dahdi/modules per caricare solo i driver necessari per la tua configurazione specifica e mostra l’hardware rilevato. Modifica il file /etc/dahdi/modules e carica solo l’hardware richiesto. Nel mio caso, stavo usando una macchina di test con un Xorcom Astribank 6FXS e 2FXO. Il file è mostrato di seguito.

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

Riavvia il computer e verifica il corretto caricamento dei driver.

## Quale versione scegliere

Come regola generale, dovresti usare la versione con le funzionalità richieste. Asterisk segue un modello di rilascio alternato tra LTS (long-term support) e versioni standard. Al momento di questa edizione, **Asterisk 22 è l'attuale rilascio LTS** (rilasciato ottobre 2024; l'ultima release point è 22.10.0), il che lo rende la migliore da scegliere ora. Asterisk 20 è il LTS precedente, e la versione 16 (usata nella prima edizione) è fuori vita. Per i sistemi di produzione, scegli sempre un rilascio LTS.

## Compilare Asterisk

Se hai già compilato software in precedenza, compilare Asterisk sarà un compito semplice. Esegui i seguenti comandi per compilare e installare Asterisk. Ricorda, puoi scegliere quali applicazioni e moduli costruire usando `make menuselect`.  
Passo 1: Scarica il codice sorgente

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Passo 2: Installa le dipendenze di compilazione (vedi "Installing dependencies" sopra)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Passo 3: Configura la compilazione

```
./configure
```

Passo 4: Seleziona i moduli da compilare

```
make menuselect
```

Usa `make menuselect` per installare solo i moduli necessari. In Asterisk 22 il canale SIP è **chan_pjsip** (compilato di default); il vecchio **chan_sip** è stato rimosso in Asterisk 21 e non esiste più. Il *pass-through* Opus funziona subito (il modulo interno `res_format_attr_opus` gestisce la negoziazione SDP), ma il modulo di transcodifica **codec_opus** è ancora un binario esterno, closed‑source, di Sangoma/Digium — selezionandolo in menuselect lo scarica dai server di Digium. Il binario è gratuito. Vedi "Selecting modules with menuselect" più sotto per i dettagli.

Passo 5: Compila e installa Asterisk, poi crea la configurazione predefinita e i file di esempio

```
make
make install
make samples
make config
ldconfig
```

`make install` installa i binari e i moduli, `make samples` scrive i file di configurazione di esempio in `/etc/asterisk`, `make config` installa lo script di avvio SysV init per la distribuzione rilevata (ad es. `/etc/init.d/asterisk` su Debian/Ubuntu), e `ldconfig` aggiorna la cache delle librerie condivise. Un'unità systemd è presente nell'albero dei sorgenti in `contrib/systemd/asterisk.service`, ma `make config` non la installa automaticamente — copiala manualmente se preferisci eseguire Asterisk sotto systemd (vedi sotto).

### Selezione dei moduli con menuselect

`make menuselect` apre un menu testuale dove scegli esattamente quali applicazioni, codec, canali e risorse compilare. Alcune note specifiche per Asterisk 22:

- **chan_pjsip** (sotto *Channel Drivers*) è il canale SIP moderno ed è abilitato di default; è l'unico canale SIP in Asterisk 22.
- **codec_opus** (sotto *Codec Translators*) è un modulo **esterno** (la sua voce in menuselect recita "Download the Opus codec from Digium"); abilitarlo fa sì che `make` scarichi il binario gratuito, closed‑source, da Sangoma/Digium. Il pass‑through Opus di per sé non richiede moduli aggiuntivi. È disponibile anche il modulo **codec_g729** di Sangoma — il binario è gratuito, ma la transcodifica legale G.729 richiede una licenza per canale acquistata.
- Seleziona i formati audio e le lingue desiderate nei menu *Core Sound Packages*, *Music On Hold File Packages* e *Extras Sound Packages*; tutto ciò che spunti verrà scaricato e installato automaticamente durante `make install`.

Dopo aver effettuato le scelte, scegli **Save & Exit** e continua con `make`.

## Avvio e arresto di Asterisk

Con questa configurazione minima, è possibile avviare Asterisk con successo. Per apprendere e fare debug, è possibile avviare Asterisk in primo piano collegato alla console:

```
/usr/sbin/asterisk -vvvgc
```

Usa il comando CLI `core stop now` per arrestare Asterisk:

```
*CLI> core stop now
```

### Avvio di Asterisk con systemd

Sui moderni sistemi Linux (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), il gestore dei servizi di sistema è **systemd**. Asterisk fornisce un'unità systemd in `contrib/systemd/asterisk.service` nell'albero dei sorgenti; copiala in `/etc/systemd/system/asterisk.service` ed esegui `systemctl daemon-reload`. Una volta installata, il modo consigliato per eseguire Asterisk in produzione è tramite `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Una volta che Asterisk è in esecuzione come servizio, collegati alla sua CLI con `asterisk -r` (connect) o `asterisk -rvvv` (connect with verbose output).

Nei sistemi più vecchi Asterisk veniva avviato tramite lo script di init legacy SysV (`/etc/init.d/asterisk`) e il wrapper **safe_asterisk**, che riavviava automaticamente Asterisk in caso di crash. Con systemd, il riavvio automatico è gestito dalla direttiva `Restart=` del file unit, quindi `safe_asterisk` non è più generalmente necessario. L'approccio legacy init/`safe_asterisk` funziona ancora ma è deprecato nelle distribuzioni basate su systemd.

### Opzioni di runtime di Asterisk

Il processo di avvio di Asterisk è molto semplice. Se Asterisk viene eseguito senza parametri, viene avviato come demone.

```
/sbin/asterisk
```

Puoi accedere alla console di Asterisk eseguendo il comando seguente. Nota che è possibile eseguire più di un processo console contemporaneamente.

```
/sbin/asterisk -r
```

### Opzioni di runtime disponibili per Asterisk

Puoi visualizzare le opzioni di runtime disponibili usando `asterisk -h`

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## Directory di installazione

Asterisk è installato in diverse directory, che possono essere modificate nel file asterisk.conf. Per scopi di formazione cambierei il livello verbose da 3 a 15, per la produzione lo lascio a 3. Le opzioni `maxcalls` e `maxload` sono buone opzioni per proteggere il sistema dal sovraccarico.

### asterisk.conf (estratto)

La sezione `[directories]` definisce dove Asterisk conserva la sua configurazione, i moduli, i dati, lo spool e i log:

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
```

La sezione `[options]` contiene la messa a punto a runtime. Le opzioni più utili da conoscere sono mostrate di seguito (decommentare per abilitare); il file è fornito con molte altre, ognuna documentata da un commento in linea:

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## Log files and log rotation

Asterisk PBX registra i suoi messaggi in `/var/log/asterisk`. La registrazione è controllata da `logger.conf`. La parte chiave è la sezione `[logfiles]`, dove ogni riga definisce un canale di log e i livelli di messaggio che cattura (estratto):

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

Dopo la modifica, applica il cambiamento con `logger reload` e conferma i canali con `logger show channels`:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

I file di log possono crescere rapidamente, quindi ruotali con il demone di sistema `logrotate` — aggiungi un file sotto `/etc/logrotate.d/`:

```text
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

Per disinstallare Asterisk, utilizzare:

```
make uninstall
```

Per disinstallare Asterisk e tutti i file di configurazione, utilizzare:

```
make uninstall-all
```

## Note sull'installazione di Asterisk

Questa sezione fornirà alcuni consigli su questioni da affrontare prima di installare Asterisk.

### Sistemi di produzione

Se Asterisk è installato in un ambiente di produzione, è necessario prestare attenzione al design del sistema. Un server deve essere ottimizzato in modo che i sistemi telefonici abbiano priorità rispetto agli altri processi di sistema. Asterisk non dovrebbe essere eseguito insieme a software ad alta intensità di CPU come X-Windows. Se è necessario eseguire processi intensivi di CPU (ad esempio, un enorme database), utilizzare un server separato. In generale, Asterisk è sensibile alle variazioni di prestazioni hardware. Pertanto, cercate di utilizzare Asterisk in un ambiente hardware che non richieda più del 40 % di utilizzo della CPU.

### Consigli di rete

Se prevedete di utilizzare telefoni IP, è importante prestare attenzione alla vostra rete. I protocolli vocali sono molto buoni e resistenti alla latenza e anche ai jitter; tuttavia, se si utilizza una rete locale configurata in modo errato, la qualità della voce ne risentirà. È possibile garantire una buona qualità vocale solo utilizzando la qualità del servizio (QoS) in switch e router. La voce in una rete locale tende a essere buona, ma anche in un ambiente LAN, se si hanno hub da 10 Mbps con troppe collisioni, si otterrà una voce distorta o scadente. Seguite queste raccomandazioni per assicurare la migliore qualità vocale possibile:

- Utilizzate QoS end‑to‑end se possibile o economicamente fattibile. Con QoS end‑to‑end, la qualità della voce è perfetta. Nessuna scusa!
- Evitate di usare hub da 10/100 Mbps per la voce in un ambiente di produzione. Le collisioni possono introdurre jitter nella rete. Sono preferiti i 10/100 Mbps full‑duplex perché non si verificano collisioni.
- Usate VLAN per separare le trasmissioni broadcast non necessarie della rete vocale. Non volete che un virus distrugga la vostra rete vocale con broadcast ARP.
- Educate gli utenti sulle aspettative in una rete vocale. Senza QoS, non affermate che la voce sarà perfetta, poiché nella maggior parte dei casi non lo sarà. Si otterrà più spesso una qualità vocale simile a quella di un telefono cellulare. Utilizzate telefoni di buona qualità, poiché i problemi di firmware e design hardware sono comuni.

## Sommario

In questo capitolo hai appreso i requisiti hardware minimi, nonché come scaricare, installare e compilare Asterisk. Asterisk dovrebbe essere eseguito con un utente non root per motivi di sicurezza. Dovresti verificare il tuo ambiente di rete prima di avviare l'ambiente di produzione.

## Quiz

1. In Asterisk 22, quale driver di canale fornisce il supporto SIP, e cosa è accaduto al vecchio `chan_sip`?
   - A. `chan_sip` è ancora il predefinito; `chan_pjsip` è opzionale.
   - B. `chan_pjsip` è il canale SIP predefinito; `chan_sip` è stato rimosso in Asterisk 21 e non esiste più.
   - C. Entrambi sono compilati per impostazione predefinita e si sceglie tra loro a runtime.
   - D. Il supporto SIP è stato rimosso completamente a favore di IAX2.
2. Le schede di interfaccia telefonica per Asterisk hanno solitamente Digital Signal Processors (DSP) integrati e quindi non richiedono molta CPU dal PC.
   - A. Vero
   - B. Falso
3. Se vuoi una qualità vocale perfetta, devi implementare la qualità del servizio end‑to‑end (QoS).
   - A. Vero
   - B. Falso
4. Dovresti sempre scegliere l'ultima versione di Asterisk, poiché è la più stabile.
   - A. Vero
   - B. Falso
5. Qual è il modo consigliato per installare le dipendenze di compilazione per Asterisk 22?
6. Se non hai una scheda di interfaccia TDM avrai comunque una sorgente di timing interna per la sincronizzazione, fornita dal modulo `res_timing_timerfd` su Linux. Questo timing è usato da applicazioni come ________ e ________.
7. Quando installi Asterisk è meglio escludere ambienti desktop come GNOME o KDE, perché le interfacce grafiche consumano cicli CPU.
   - A. Vero
   - B. Falso
8. I file di configurazione di Asterisk si trovano nella directory ________.
9. Per installare i file di configurazione di esempio di Asterisk, digita il comando: ________
10. Perché è importante eseguire Asterisk come utente non root?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
