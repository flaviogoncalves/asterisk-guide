# Deployment, monitoring & scaling

Far sì che Asterisk risponda a una chiamata in un laboratorio è una cosa; eseguirlo come un servizio che sopravvive a crash, riavvii, aggiornamenti e attacchi — e che si può osservare, sottoporre a backup e far crescere — è un'altra. Questo capitolo tratta tutto ciò che accade *dopo* che il dialplan funziona. Iniziamo dal supervisore che mantiene Asterisk attivo (systemd), passiamo al suo impacchettamento in un container (usando il laboratorio Docker del libro come esempio pratico), quindi trattiamo la gestione della configurazione e i backup, il monitoraggio e l'osservabilità, e infine i pattern a cui ricorrere quando un singolo server non è sufficiente: alta affidabilità, scalabilità e le realtà dell'hosting nel cloud.

Tutto ciò che viene mostrato è verificato rispetto al laboratorio Asterisk 22 del libro in `lab/` — lo stesso container su cui hai lavorato per tutto il libro.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Eseguire Asterisk 22 in modo affidabile sotto systemd, come utente non root, con riavvio automatico
- Containerizzare Asterisk con Docker e comprendere i compromessi di rete
- Mantenere `/etc/asterisk` sotto controllo di versione ed eseguire il backup dello stato corretto
- Monitorare un sistema in esecuzione tramite CLI, CDR/CEL, AMI/ARI e metriche
- Applicare pattern di alta affidabilità attivo/standby e di scalabilità orizzontale
- Ospitare Asterisk nel cloud in sicurezza dietro NAT e firewall

## Eseguire Asterisk sotto systemd

Su ogni distribuzione Linux attuale — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — il gestore dei servizi è **systemd**. Il capitolo sull'installazione ha mostrato che il passaggio `make config` (eseguito durante `make install`) installa uno script init di distribuzione (`/etc/init.d/asterisk` su Debian, uno script `rc.d` su RedHat), che systemd avvolge poi automaticamente come servizio; Asterisk fornisce anche un'unità systemd nativa in `contrib/systemd/asterisk.service` che puoi installare al suo posto per un controllo più preciso.
In ogni caso, systemd è il modo supportato e adatto alla produzione per eseguire Asterisk. Fai riferimento a *Installing Asterisk 22* per la compilazione; qui ci concentriamo su ciò che il servizio ti offre e su come gestirlo.

### L'unità di servizio e il suo ciclo di vita

Una volta che `make config` ha installato il servizio, il ciclo di vita è quello ordinario di systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

Alcune note operative:

- **`restart` vs. un ricaricamento (reload) pulito.** `systemctl restart` interrompe il processo e termina ogni chiamata. Per le modifiche alla configurazione non vuoi quasi mai che ciò accada — usa invece la CLI di Asterisk: `asterisk -rx 'core reload'` (o un ricaricamento specifico per modulo come `pjsip reload`). Riserva `systemctl restart` per gli aggiornamenti o per un processo bloccato.
- **Collegarsi al demone in esecuzione.** Con Asterisk in esecuzione come servizio, apri la sua console con `asterisk -r` (o `asterisk -rvvv` per un output dettagliato). Questo si connette al demone già in esecuzione tramite il suo socket di controllo; non avvia una seconda copia.

### `Restart=` sostituisce safe_asterisk

Storicamente Asterisk veniva lanciato tramite il wrapper **safe_asterisk**, uno script shell che riavviava Asterisk in caso di crash. Sotto systemd quel compito spetta alla direttiva `Restart=` dell'unità — systemd nota l'uscita del processo e lo riavvia, con un back-off controllato da `RestartSec=` e una protezione contro i crash-loop tramite `StartLimitIntervalSec=`/`StartLimitBurst=`. Quindi su un host systemd **safe_asterisk è superato** e generalmente non necessario. Se l'unità fornita non lo imposta già, un override drop-in è il modo pulito per aggiungere il riavvio in caso di errore senza modificare il file pacchettizzato:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Applica la modifica con `systemctl daemon-reload && systemctl restart asterisk`. L'uso di un file drop-in (piuttosto che la modifica dell'unità installata) significa che un futuro `make config` non sovrascriverà la tua modifica.

### Eseguire come utente non root

Asterisk non dovrebbe essere eseguito come root in produzione — un bug di esecuzione remota di codice in un processo eseguito come root è una compromissione totale dell'host, mentre lo stesso bug in un processo senza privilegi è contenuto. Ci sono due punti complementari in cui questo viene applicato:

- **L'unità / asterisk.conf.** L'unità pacchettizzata normalmente esegue Asterisk come utente e gruppo `asterisk`. Puoi anche (o in alternativa) impostare `runuser` e `rungroup` nella sezione `[options]` di `asterisk.conf`, che il demone onora quando rilascia i privilegi dopo il binding:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **Proprietà dei file.** Le directory di runtime devono essere scrivibili da quell'utente. Dopo aver creato l'account, assicurati della proprietà:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

Poiché SIP (5060) e RTP (10000+) sono tutte porte alte, Asterisk **non** ha bisogno di root per il binding — solo le porte privilegiate in stile porta 25 ne avrebbero bisogno, ma Asterisk non le usa. L'esecuzione senza privilegi è quindi gratuita. (Il capitolo sulla sicurezza approfondisce il motivo per cui questo è importante; vedi *Asterisk Security*.)

## Containerizzare Asterisk

Un container impacchetta Asterisk e le sue dipendenze esatte in un'immagine immutabile, in modo che ciò che testi sia byte per byte ciò che distribuisci. Il compromesso riguarda i media in tempo reale: un server SIP è sensibile alla latenza e necessita di un intervallo ampio e prevedibile di porte UDP raggiungibili dall'esterno, e la rete dei container può essere d'intralcio. Il resto di questa sezione percorre il laboratorio del libro — `lab/Dockerfile` e `lab/docker-compose.yml` — come esempio concreto e funzionante, e poi spiega l'unica trappola in cui tutti cadono: RTP e networking a ponte (bridged).

### L'immagine: compilare Asterisk dai sorgenti

Il file `Dockerfile` del laboratorio compila Asterisk 22 dai sorgenti su Debian 12. Vale la pena leggere la sua struttura anche se non ne scriverai mai uno tu stesso:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Tre cose da sottolineare:

- **La versione è bloccata** (`ARG ASTERISK_VERSION=22.10.0`). La riproducibilità è l'intero scopo della containerizzazione — aggiornala deliberatamente, ricompila, ritesta.
- **`--with-pjproject-bundled` e `--with-jansson-bundled`** compilano lo stack SIP in versione corrispondente ad Asterisk, così dipendi da meno pacchetti apt e non dovrai mai combattere con un PJSIP di distribuzione non allineato.
- **`CMD ["asterisk", "-f", "-vvv"]`** esegue Asterisk in *primo piano* (`-f`, "do not fork"). Questa è la differenza chiave rispetto a un host systemd: il processo principale di un container non deve diventare un demone, altrimenti il container uscirebbe immediatamente. Quindi in un container **non** usi affatto l'unità systemd — il runtime del container (Docker, più la policy `restart:`) diventa il supervisore che la `Restart=` dell'unità era su una VM.

### Bind-mount di `/etc/asterisk`

L'immagine non contiene deliberatamente **alcuna** configurazione. Invece `docker-compose.yml` esegue il bind-mount della directory di configurazione dell'host:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` mappa la directory `lab/asterisk/etc` sotto controllo di versione su `/etc/asterisk` del container, in sola lettura (`:ro`). Il vantaggio è grande: l'immagine rimane immutabile e riutilizzabile, mentre la configurazione risiede sull'host dove può essere modificata e, cosa fondamentale, mantenuta in git (sezione successiva). Per applicare una modifica alla configurazione modifichi il file e ricarichi — `docker compose exec asterisk asterisk -rx 'core reload'` — senza ricostruire. `restart: unless-stopped` è l'equivalente a livello di compose della `Restart=` di systemd: Docker riavvia il container se Asterisk esce, ma non se lo hai fermato deliberatamente.

### Networking host vs. bridged — il problema RTP

Questo è il fallimento più comune di Asterisk containerizzato, quindi vale la pena capirlo con precisione. Per impostazione predefinita Docker inserisce un container su una rete **bridged** e pubblichi le singole porte con `ports:`. La segnalazione va bene — 5060 è una porta. Il problema sono i media: RTP usa un *intervallo* di porte UDP (il `rtp.conf` del laboratorio imposta `rtpstart=10000` / `rtpend=10100`), e **ogni** porta che potrebbe trasportare audio deve essere pubblicata.

Il laboratorio fa esattamente questo:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Nota che l'intervallo di pubblicazione RTP (`10000-10100`) corrisponde esattamente a `rtp.conf`. Se sbagli questo — pubblichi troppe poche porte, o un intervallo diverso da `rtp.conf` — le chiamate si connettono ma hanno **audio unidirezionale o assente**, perché i pacchetti RTP finiscono su una porta che Docker non sta inoltrando. Due ulteriori avvertenze con la modalità bridged:

- **Pubblicare migliaia di porte è lento e pesante.** Un intervallo RTP di produzione è tipicamente 10000–20000. Docker che crea ~10000 inoltri proxy userland è costoso all'avvio e aggiunge un salto nel percorso dei media. Il laboratorio mantiene un intervallo deliberatamente piccolo di 100 porte perché esegue solo una o due chiamate di test.
- **NAT nell'SDP.** Dietro il bridge, Asterisk vede il suo IP privato del container e potrebbe annunciarlo nell'SDP. Su un host pubblico devi comunicare a PJSIP il suo indirizzo esterno con `external_media_address` / `external_signaling_address` sul transport (e impostare `local_net`), esattamente come faresti dietro qualsiasi NAT — vedi *Cloud hosting* di seguito.

L'alternativa è il **networking host** (`network_mode: host`), che rimuove completamente il bridge: il container condivide lo stack di rete dell'host, quindi la 5060 e l'intero intervallo RTP sono raggiungibili senza pubblicazione di porte e senza salti extra per i media. Questa è la modalità consigliata per un vero container Asterisk — aggira completamente il problema dell'intervallo RTP. Il suo costo è l'isolamento: il container può collegarsi a qualsiasi porta dell'host e perdi la rete per-servizio di compose. (Il networking host è una funzionalità Linux; su Docker Desktop per macOS/Windows si comporta diversamente, motivo per cui questo laboratorio didattico usa porte pubblicate esplicite.)

### Volumi persistenti per spool e voicemail

Il livello scrivibile di un container è **effimero** — distruggi il container e tutto ciò che ha scritto scompare. Per Asterisk ciò significa che voicemail, registrazioni, lo spool delle chiamate in uscita e il database locale svanirebbero a ogni `docker compose up --build`. La configurazione sopravvive perché è bind-mountata dall'host; lo *stato* necessita dello stesso trattamento. All'interno del container gli alberi rilevanti sono:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(Il container in esecuzione del laboratorio mostra esattamente questi — `/var/spool/asterisk` contiene `voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` contiene `astdb.sqlite3`.) Per preservarli, monta volumi nominati per le directory che contengono lo stato che ti interessa:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

Il laboratorio didattico li omette apposta — è stateless e riproducibile per design, quindi ogni `up` è un nuovo inizio — ma un container di produzione **deve** averli, altrimenti perderai la voicemail al primo redeploy.

## Gestione della configurazione e backup

Il bind-mount sopra suggerisce il modello corretto: tratta `/etc/asterisk` come **codice** e il resto come **dati**.

### Mantieni `/etc/asterisk` sotto controllo di versione

La directory di configurazione è un insieme piatto di file di testo senza segreti che non possano essere templatizzati — è ideale per git. Inizializza un repo in `/etc/asterisk` (o, come fa il laboratorio, mantieni la configurazione insieme al progetto ed eseguine il bind-mount). Vantaggi:

- Ogni modifica è revisionabile e reversibile (`git diff`, `git revert`).
- Hai una traccia di controllo di chi ha cambiato cosa e quando.
- Combinato con un'immagine container, un commit di configurazione noto come buono più un tag di immagine bloccato descrive completamente una distribuzione.

Un paio di avvertenze specifiche per la configurazione di Asterisk:

- **Segreti.** `pjsip.conf` (e `manager.conf`, `ari.conf`) contengono password. Non committare segreti reali in un repo condiviso in testo chiaro — usa dei template (un file per ambiente, o un gestore di segreti / sostituzione di variabili d'ambiente al momento del deploy) e mantieni solo segreti segnaposto in git. Le password banali in stile `Lab-6001-secret` del laboratorio vanno bene *solo* perché vivono su una sottorete Docker privata.
- **Templating per ambiente.** I valori realtime che differiscono tra dev, staging e produzione (indirizzi di bind, IP esterni, credenziali di trunk, URL di database) sono esattamente le righe che devi templatizzare, mantenendo la maggior parte della configurazione identica tra gli ambienti.

### Cosa sottoporre a backup

La configurazione in git copre il dialplan e gli endpoint, ma un PBX attivo accumula *stato* che non si trova in nessun file di configurazione. Un backup completo è:

| Cosa | Dove | Perché |
|------|-------|-----|
| Configurazione | `/etc/asterisk/` | dialplan, endpoint (anche in git) |
| Voicemail & registrazioni | `/var/spool/asterisk/` | dati utente — insostituibili |
| Database interno | `/var/lib/asterisk/astdb.sqlite3` | chiavi `DB()`, stato dispositivo |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` o store SQL | fatturazione & cronologia |
| Database esterni | il tuo MySQL/PostgreSQL | realtime, CDR, voicemail |

L'**astdb** merita una nota: è il piccolo store chiave/valore integrato di Asterisk (un file SQLite in `/var/lib/asterisk/astdb.sqlite3`) usato dalle funzioni di dialplan `DB()`, stati dei dispositivi, impostazioni di follow-me e simili. Puoi scaricarlo per ispezione o backup dalla CLI:

```
asterisk -rx 'database show'
```

Se il tuo CDR/CEL o la configurazione di voicemail o PJSIP risiedono in un database esterno (vedi *Asterisk Real-Time* e *Asterisk Call Detail Records*), quel database è ora la fonte di verità per quei dati e deve essere nella tua normale rotazione di backup del database — eseguire il backup di `/etc/asterisk` da solo non è sufficiente.

## Monitoraggio e osservabilità

Non puoi gestire ciò che non puoi vedere. Asterisk espone il suo stato a quattro livelli, da una rapida occhiata umana a una pipeline di metriche: la **CLI**, i record **CDR/CEL**, gli eventi **AMI/ARI** e gli **esportatori di metriche**.

### Controlli di salute della CLI

Il controllo "è sano?" più veloce è la CLI. I comandi seguenti vengono eseguiti dal vivo contro il laboratorio. Prima i canali:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` su un sistema silenzioso è normale; su uno occupato questa è la tua concorrenza in tempo reale. `core show uptime` conferma che il processo non si è riavviato sotto di te:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Per la salute SIP, `pjsip show endpoints` mostra ogni endpoint e se i suoi contatti registrati sono raggiungibili. Dal laboratorio:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` qui significa semplicemente che nessun telefono è attualmente registrato su quegli endpoint (il laboratorio non ha client attivi) — una volta che un softphone si registra e `qualify` lo conferma, lo stato mostra il contatto come raggiungibile. Comandi di accompagnamento: `pjsip show contacts` (registrazioni correnti e round-trip time), `pjsip show transports` e `pjsip show aor <name>` per un AOR. Questi sono gli strumenti quotidiani per rispondere a "perché l'interno X non è raggiungibile?".

### CDR e CEL

Ogni chiamata lascia un **Call Detail Record** (CDR); il **Channel Event Logging** (CEL) aggiunge eventi più dettagliati per canale. Conferma che il CDR sia attivo e quale backend lo memorizza:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

Il laboratorio mostra `(none)` tra i backend registrati perché la configurazione minima del laboratorio non carica alcun modulo di archiviazione CDR — quindi i record vengono calcolati ma non scritti da nessuna parte. In produzione carichi un backend (CSV, o `cdr_odbc`/`cdr_adaptive_odbc` in MySQL/PostgreSQL) e quello diventa la tua fonte per fatturazione e cronologia. Il CEL è **disabilitato per impostazione predefinita** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` solo quando hai bisogno di dettagli a livello di evento. Entrambi sono trattati in profondità in *Asterisk Call Detail Records*; per il monitoraggio, il punto è che CDR/CEL sono il tuo record *storico*, mentre la CLI è la tua vista *dal vivo*.

### Eventi AMI e ARI

Per un monitoraggio programmatico in tempo reale vuoi un feed push di eventi piuttosto che interrogare la CLI:

- **AMI (Asterisk Manager Interface)** è il protocollo TCP di eventi/comandi di lunga data (`manager.conf`). Ti iscrivi e ricevi eventi `Newchannel`, `Hangup`, `DialBegin`, `BridgeEnter`, `PeerStatus` e simili man mano che le chiamate avvengono — la spina dorsale di wallboard e strumenti di contabilità delle chiamate. Nel laboratorio AMI è disabilitato per impostazione predefinita (`manager show settings` riporta `Manager (AMI): No`); lo abiliti e lo blocchi in `manager.conf`.
- **ARI (Asterisk REST Interface)** è la moderna interfaccia HTTP + WebSocket (`ari.conf`, servita dal server HTTP integrato). Fornisce uno stream di eventi JSON e un controllo granulare delle chiamate — la scelta giusta per nuove integrazioni.

Entrambi sono dettagliati in *Extending Asterisk with AMI and AGI* e *The Asterisk REST Interface (ARI)*. L'avvertimento rilevante per la distribuzione: **AMI e ARI sono potenti e non devono mai essere esposti a Internet.** Lega il server HTTP a localhost o a una rete di gestione, usa segreti unici forti e proteggi le porte con un firewall — vedi *Asterisk Security*.

### Metriche: Prometheus e Grafana

Per dashboard e avvisi, Asterisk 22 fornisce un esportatore Prometheus, **`res_prometheus.so`** (un modulo con livello di supporto *esteso*), che espone le metriche su un endpoint HTTP che un server Prometheus interroga. Oltre alle metriche di processo principali, fornisce provider collegabili che coprono canali, chiamate, endpoint, bridge e registrazioni in uscita PJSIP:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

Puoi confermare che il modulo sia presente nella build del laboratorio:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

Mostra `Not Running` perché il laboratorio non lo configura né lo carica; abilitandolo (`prometheus.conf` più il server HTTP) trasformi Asterisk in un target Prometheus. Punta Prometheus all'endpoint di scraping e Grafana a Prometheus, e otterrai dashboard di serie temporali (chiamate simultanee, registrazioni, trend ASR/ACD) e avvisi (es. "chiamate attive scese a zero" o "picchi di fallimenti di registrazione"). Per i team che eseguono già Prometheus/Grafana questo è il modo naturale per integrare Asterisk nell'osservabilità esistente, piuttosto che analizzare l'output della CLI.

### Codici di risposta SIP da tenere d'occhio

Qualunque sia la pipeline, alcuni risultati SIP segnalano problemi e vale la pena monitorarli: fallimenti persistenti di sfida `401`/`407` o `403 Forbidden` suggeriscono un attacco brute-force o una tempesta di credenziali mal configurate (fai riferimento a Fail2Ban in *Asterisk Security*); `503 Service Unavailable` punta a un server o trunk sovraccarico o congestionato; e un picco in `408 Request Timeout`/`480 Temporarily Unavailable` di solito significa che gli endpoint sono diventati irraggiungibili (timeout NAT, fallimenti di qualify).

## Alta affidabilità e scalabilità

Un server Asterisk è un singolo punto di fallimento e ha un limite massimo di chiamate. I due problemi — *rimanere attivi* e *diventare più grandi* — hanno risposte diverse.

### Attivo/standby con un IP flottante

Il classico pattern HA ben collaudato per Asterisk è **attivo/standby** (non attivo/attivo — lo stato delle chiamate in Asterisk è difficile da condividere dal vivo). Due server identici, uno attivo, uno standby, condividono un **IP flottante (virtuale)** gestito da un gestore di cluster come **keepalived** (VRRP) o **Pacemaker/Corosync**. Telefoni e trunk si registrano all'IP flottante, non a nessuno dei due host reali. Se il nodo attivo fallisce il suo controllo di salute, l'IP flottante si sposta sullo standby, che prende il sopravvento.

L'avvertenza onesta: un failover IP **interrompe le chiamate in corso** — Asterisk non replica lo stato del canale dal vivo tra i nodi, quindi chiunque sia a metà chiamata deve ricomporre. Le registrazioni si ristabiliscono entro un ciclo di qualify/registrazione. Ciò che il failover ti garantisce è che il *servizio* si riprenda in pochi secondi senza intervento manuale, che per la maggior parte dei PBX è esattamente l'obiettivo. Per rendere lo standby effettivamente in grado di subentrare, entrambi i nodi necessitano della stessa configurazione (il tuo `/etc/asterisk` in git, distribuito in modo identico) e dello stesso *stato* — che è il punto successivo.

### Esternalizzare lo stato con PJSIP Realtime

L'attivo/standby funziona solo se lo standby conosce gli stessi endpoint e registrazioni del nodo attivo. Il modo per ottenerlo è **smettere di mantenere lo stato in file piatti su una sola macchina** e spostarlo in un database condiviso che entrambi i nodi leggono. **PJSIP Realtime** (Sorcery supportato da un database) fa esattamente questo: endpoint, AOR, autenticazioni — e, cosa importante, **registrazioni** (la tabella `ps_contacts`) — vivono in MySQL/PostgreSQL invece che in `pjsip.conf` e nella memoria locale. Entrambi i nodi Asterisk puntano allo stesso database, quindi un telefono registrato tramite un nodo è visibile all'altro. Questo è trattato in *Asterisk Real-Time* (la sezione PJSIP Realtime / Sorcery); qui il punto della distribuzione è che **esternalizzare lo stato è il prerequisito sia per l'HA che per la scalabilità orizzontale** — senza di esso, ogni nodo è un'isola.

Applica la stessa logica al resto del tuo stato: CDR/CEL in uno store SQL condiviso, voicemail su storage condiviso/replicato (o `ODBC_STORAGE`), e le chiavi astdb da cui dipendi in un database. Una volta che lo stato è esterno, i nodi Asterisk diventano più simili a front-end intercambiabili.

### Proxy SIP davanti (OpenSIPS)

Per scalare *oltre* la capacità di un singolo server metti un **proxy SIP/bilanciatore di carico** davanti a un pool di server media Asterisk. **OpenSIPS** è un proxy SIP appositamente costruito ad altissimo throughput (gestiscono centinaia di migliaia di registrazioni e instrada la segnalazione senza toccare i media). Il proxy presenta un singolo indirizzo SIP al mondo, mantiene il servizio di registrazione/posizione e distribuisce le chiamate tra i back-end Asterisk. Questa separazione — un livello proxy leggero che gestisce registrazione e routing, un livello Asterisk scalabile orizzontalmente che gestisce l'elaborazione effettiva delle chiamate (IVR, code, conferenze, transcodifica) — è il modo in cui le grandi distribuzioni crescono oltre una singola macchina. (La piattaforma SipPulse stessa usa OpenSIPS davanti ai suoi server media/applicazione esattamente per questo motivo.)

### Scalabilità dei media

Il proxy distribuisce la *segnalazione* a basso costo; **i media sono la risorsa costosa**. Il relay RTP, e specialmente la transcodifica tra codec (es. Opus ↔ G.711) o l'esecuzione di grandi conferenze, è limitato dalla CPU ed è ciò che effettivamente limita un server. Strategie:

- **Evita la transcodifica** ove possibile — negozia un codec comune end-to-end in modo che Asterisk faccia il bridge nativamente (pass-through) invece di transcodificare. Questa è la singola vittoria più grande per la capacità media.
- **Scala i media orizzontalmente** aggiungendo nodi Asterisk dietro il proxy; ognuno trasporta una quota delle chiamate simultanee.
- **Scarica i media del browser** su un gateway WebRTC dedicato (es. Janus) in modo che il PBX non stia anche terminando e inoltrando ogni stream DTLS-SRTP del browser — vedi *WebRTC with Asterisk*, che discute esattamente questa divisione Asterisk-più-gateway.

Dimensiona la capacità in base a **chiamate simultanee e carico di transcodifica**, non in base agli utenti registrati — 10.000 telefoni registrati che sono per lo più inattivi sono molto più economici di 200 conferenze transcodificate simultanee.

## Cloud hosting

Eseguire Asterisk su una VM cloud (AWS, GCP, Azure, un VPS) è comune e funziona bene, ma la rete cloud è **NAT'd e protetta da firewall per impostazione predefinita**, il che contrasta con il SIP. Le seguenti sono le preoccupazioni specifiche per la distribuzione.

### NAT e SDP

Una VM cloud ha quasi sempre un IP **privato** sulla sua NIC e un IP **pubblico** separato che il provider NATta su di esso. Se Asterisk annuncia l'IP privato nell'SDP, i telefoni remoti inviano RTP in un buco nero — il classico sintomo audio unidirezionale/assente. Comunica a PJSIP la sua identità pubblica sul transport:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` fa sì che Asterisk riscriva l'indirizzo che annuncia ai peer pubblici, mentre `local_net` gli dice quali peer sono locali (e *non* dovrebbero essere riscritti). Questa è la stessa gestione NAT discussa sopra per il networking Docker bridged — una VM cloud è, in effetti, dietro NAT.

### Firewall e intervallo RTP

Due firewall si applicano solitamente su una VM cloud: il gruppo di sicurezza / ACL di rete del **provider**, e gli iptables dell'**host**. Entrambi devono aprire le stesse porte, e la policy è quella del capitolo sulla sicurezza. Il set di regole salvato della 1a edizione (`docs/legacy-labs/configs/Lab7/rules.v4`) ne cattura la forma — accetta SIP e l'intervallo RTP, accetta established/related, scarta il resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Due correzioni che il capitolo sulla sicurezza apporta e che contano qui: apri **5061 su TCP** (non UDP) se esegui SIP/TLS, e ricorda che l'intervallo UDP RTP nel tuo firewall deve corrispondere esattamente a `rtpstart`/`rtpend` in `rtp.conf` — lo stesso intervallo che pubblichi su un container. Non duplicare qui la build di iptables/Fail2Ban; **segui le sezioni firewall, Fail2Ban e TLS/SRTP di *Asterisk Security*** (Fail2Ban osserva il canale logger `security` che il laboratorio abilita già in `logger.conf`) e applica quella policy *sia* nel firewall dell'host che nel gruppo di sicurezza cloud.

### Latenza, regione e SBC

- **Scegli una regione vicina ai tuoi utenti.** La voce è sensibile alla latenza — una latenza bocca-orecchio unidirezionale superiore a ~150 ms è percepibile. Ospita la VM nella regione più vicina alla maggior parte dei tuoi telefoni e trunk; i media transcontinentali sono udibilmente peggiori.
- **Metti un SBC davanti per qualsiasi distribuzione esposta a Internet.** Un **Session Border Controller** termina SIP/RTP al bordo, nasconde la tua topologia, normalizza il NAT e assorbe il traffico DoS e di scansione prima che raggiunga Asterisk. La raccomandazione principale del capitolo sulla sicurezza — *non esporre Asterisk grezzo a Internet* — si applica doppiamente nel cloud, dove l'IP pubblico della tua VM viene scansionato pochi minuti dopo l'avvio. Un SBC (o almeno un proxy SIP indurito come OpenSIPS più Fail2Ban) è il bordo standard.

## Riepilogo

La distribuzione è dove un dialplan funzionante diventa un servizio affidabile. Su una VM, esegui Asterisk sotto **systemd** come utente **non-root**, lasciando che la `Restart=` dell'unità lo mantenga attivo (safe_asterisk è superato) e usando `core reload` invece di `systemctl restart` per le modifiche alla configurazione. La **containerizzazione** con Docker — come fa il laboratorio del libro — ti offre un'immagine immutabile e bloccata con configurazione **bind-mountata** da un `/etc/asterisk` in git; l'insidia sono i media, quindi usa il **networking host** o pubblica un intervallo di porte RTP che **corrisponda esattamente a `rtp.conf`**, e monta **volumi persistenti** per spool/voicemail/astdb in modo che lo stato sopravviva a un redeploy. Tratta la configurazione come codice ed **esegui il backup dello stato** che la configurazione non cattura: voicemail, registrazioni, `astdb.sqlite3` e CDR/CEL. **Osserva** il sistema a quattro livelli — la CLI (`core show channels`, `pjsip show endpoints`) per la vista dal vivo, **CDR/CEL** per la cronologia, **AMI/ARI** per eventi programmatici, e l'esportatore **`res_prometheus`** in Grafana per dashboard e avvisi — mantenendo AMI/ARI fuori da Internet pubblico. Per **rimanere attivo**, esegui attivo/standby con un **IP flottante** (accettando che il failover interrompa le chiamate dal vivo); per **crescere**, esternalizza lo stato con **PJSIP Realtime**, metti davanti un pool di server media con **OpenSIPS** e minimizza la transcodifica perché **i media — non le registrazioni — sono ciò che limita un server**. Infine, nel **cloud**, tratta la VM come se fosse dietro NAT (`external_media_address`, `local_net`), apri il firewall secondo il capitolo sulla sicurezza sia nell'host che nel gruppo di sicurezza del provider, scegli una regione a bassa latenza e non esporre mai Asterisk grezzo — metti un **SBC** al bordo.

## Quiz

1. Su un host systemd, cosa sostituisce il vecchio compito del wrapper `safe_asterisk` di riavviare un Asterisk crashato?
   - A. Un cron job
   - B. La direttiva `Restart=` del file di unità
   - C. `systemctl enable`
   - D. L'astdb
2. Per applicare una modifica alla configurazione a un Asterisk in esecuzione **senza interrompere le chiamate**, dovresti:
   - A. `systemctl restart asterisk`
   - B. Riavviare il server
   - C. `asterisk -rx 'core reload'`
   - D. Ricostruire l'immagine del container
3. Un Asterisk containerizzato (rete bridged) connette le chiamate ma **non ha audio**. La causa più probabile è:
   - A. Il dialplan è sbagliato
   - B. L'intervallo di porte UDP RTP pubblicato non corrisponde a `rtpstart`/`rtpend` in `rtp.conf`
   - C. Il CDR è disabilitato
   - D. La CLI è irraggiungibile
4. Quali directory devono essere montate come **volumi persistenti** affinché un redeploy del container non perda lo stato? (seleziona tutte le opzioni corrette)
   - A. `/var/spool/asterisk` (voicemail, registrazioni)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (già bind-mountata dall'host)
   - D. `/usr/sbin`
5. Quale comando CLI fornisce il conteggio dal vivo delle chiamate attive?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22, il modo supportato per esporre le metriche di chiamata/canale a uno stack Prometheus/Grafana è:
   - A. Analizzare il file di log `full`
   - B. Il modulo `res_prometheus.so`
   - C. Script AGI
   - D. Non esiste
7. Qual è il prerequisito sia per il failover HA che per la scalabilità orizzontale su più nodi Asterisk?
   - A. Eseguire come root
   - B. Esternalizzare lo stato (es. registrazioni PJSIP Realtime in un database condiviso)
   - C. Disabilitare il CDR
   - D. Usare il networking bridged
8. Quale risorsa limita più direttamente quante chiamate simultanee può gestire un server Asterisk?
   - A. Il numero di utenti registrati
   - B. L'elaborazione dei media, specialmente la transcodifica
   - C. La dimensione di `/etc/asterisk`
   - D. Il backend CDR
9. Su una VM cloud, quali impostazioni di trasporto `pjsip.conf` fanno sì che Asterisk annunci il suo indirizzo pubblico in modo che l'audio remoto funzioni? (seleziona tutte le opzioni corrette)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Per una distribuzione cloud esposta a Internet, la regola fondamentale del capitolo sulla sicurezza è:
    - A. Eseguire sempre due NIC
    - B. Non esporre mai Asterisk grezzo a Internet; metti un SBC (o proxy indurito + Fail2Ban) al bordo
    - C. Usare solo UDP
    - D. Disabilitare TLS

**Risposte:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
