# Deployment, monitoring & scaling

Far rispondere Asterisk a una chiamata in laboratorio è una cosa; farlo funzionare come un servizio
che sopravvive a crash, riavvii, aggiornamenti e attacchi — e che puoi osservare,
fare backup e far crescere — è un'altra. Questo capitolo tratta tutto ciò che accade *dopo*
che il dialplan funziona. Iniziamo con il supervisore che mantiene Asterisk attivo
(systemd), passiamo al suo confezionamento in un container (usando il laboratorio Docker del libro come
esempio pratico), poi copriamo la gestione della configurazione e i backup, il monitoraggio e
l'osservabilità, e infine i pattern a cui ricorrere quando un solo server non è sufficiente:
alta disponibilità e scaling, e le realtà dell'hosting nel cloud.

Tutto quanto mostrato è verificato contro il laboratorio Asterisk 22 del libro in `lab/` — lo stesso
container che hai costruito durante tutto il libro.

## Obiettivi

- Eseguire Asterisk 22 in modo affidabile sotto systemd, come utente non root, con riavvio automatico
- Containerizzare Asterisk con Docker e comprendere i compromessi di rete
- Tenere `/etc/asterisk` sotto controllo di versione e eseguire il backup dello stato corretto
- Monitorare un sistema in esecuzione tramite la CLI, CDR/CEL, AMI/ARI e metriche
- Applicare schemi di alta disponibilità attiva/standby e scaling orizzontale
- Ospitare Asterisk nel cloud in modo sicuro dietro NAT e un firewall

## Esecuzione di Asterisk sotto systemd

Su ogni distribuzione Linux attuale — Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9 — il gestore dei servizi è **systemd**. Il capitolo di installazione ha mostrato che il passaggio `make config` (eseguito durante `make install`) installa uno script di init della distribuzione (`/etc/init.d/asterisk` su Debian, uno script `rc.d` su RedHat), che systemd avvolge automaticamente come servizio; Asterisk fornisce anche un'unità systemd nativa sotto `contrib/systemd/asterisk.service` che è possibile installare al suo posto per un controllo più fine.  
In ogni caso, systemd è il metodo supportato e di produzione per eseguire Asterisk. Vedi il capitolo *Installing Asterisk 22* per la compilazione stessa; qui ci concentriamo su ciò che il servizio offre e su come gestirlo.

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

- **`restart` vs. un reload graduale.** `systemctl restart` termina il processo e interrompe tutte le chiamate. Per le modifiche di configurazione quasi mai si desidera questo — usare invece la CLI di Asterisk: `asterisk -rx 'core reload'` (o un reload specifico del modulo come `pjsip reload`). Riserva `systemctl restart` per aggiornamenti o per un processo bloccato.
- **Collegarsi al demone in esecuzione.** Con Asterisk in esecuzione come servizio, apri la sua console con `asterisk -r` (o `asterisk -rvvv` per output dettagliato). Questo si connette al demone già avviato tramite il suo socket di controllo; non avvia una seconda copia.

### `Restart=` sostituisce safe_asterisk

Storicamente Asterisk veniva avviato tramite il wrapper **safe_asterisk**, uno script shell che rilanciava Asterisk in caso di crash. Con systemd quel compito appartiene alla direttiva `Restart=` dell'unità — systemd rileva l'uscita del processo e lo riavvia, con back‑off controllato da `RestartSec=` e protezione contro loop di crash tramite `StartLimitIntervalSec=`/`StartLimitBurst=`. Quindi su un host systemd **safe_asterisk è** **soppiantato** e generalmente non necessario. Se la tua unità fornita non lo imposta già, un override drop‑in è il modo corretto per aggiungere il riavvio in caso di errore senza modificare il file confezionato:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

Applica l'override con `systemctl daemon-reload && systemctl restart asterisk`. Usare un drop‑in (piuttosto che modificare l'unità installata) significa che un futuro `make config` non sovrascriverà la tua modifica.

### Esecuzione come utente non root

Asterisk non dovrebbe essere eseguito come root in produzione — un bug di codice remoto in un processo che gira come root compromette l'intero host, mentre lo stesso bug in un processo non privilegiato è contenuto. Ci sono due punti complementari in cui questo è imposto:

- **L'unità / asterisk.conf.** L'unità confezionata normalmente avvia Asterisk come utente e gruppo `asterisk`. È inoltre possibile (o in alternativa) impostare `runuser` e `rungroup` nella sezione `[options]` di `asterisk.conf`, che il demone rispetta quando rilascia i privilegi dopo il binding:

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

Poiché SIP (5060) e RTP (10000+) sono tutte porte alte, Asterisk **non** ha bisogno di root per bindarle — solo le porte privilegiate in stile porta‑25 lo richiederebbero, e Asterisk non le utilizza. L'esecuzione non privilegiata è quindi gratuita. (Il capitolo Sicurezza approfondisce perché questo è importante; vedi *Asterisk Security*.)

## Containerizing Asterisk

Un container impacchetta Asterisk e le sue dipendenze esatte in un’unica immagine immutabile, così
ciò che testi è byte‑for‑byte ciò che spedisci. Il compromesso riguarda i media in tempo reale:
un server SIP è sensibile alla latenza e necessita di un ampio e prevedibile intervallo di porte UDP
raggiungibili dall’esterno, e la rete dei container può intralciare. Il resto di
questa sezione percorre il laboratorio del libro — `lab/Dockerfile` e
`lab/docker-compose.yml` — come esempio concreto e funzionante, per poi spiegare la
trappola che tutti incontrano: RTP e rete bridged.

### The image: building Asterisk from source

Il `Dockerfile` del laboratorio compila Asterisk 22 dal sorgente su Debian 12. La sua struttura vale la pena leggere anche se non scrivi mai un laboratorio tu stesso:

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

Tre cose da evidenziare:

- **La versione è fissata** (`ARG ASTERISK_VERSION=22.10.0`). La riproducibilità è lo
  scopo principale della containerizzazione — aumentala deliberatamente, ricostruisci, ritesta.
- **`--with-pjproject-bundled` e `--with-jansson-bundled`** costruiscono lo stack SIP
  con la versione corrispondente ad Asterisk, così dipendi da meno pacchetti apt e non ti trovi mai a combattere con un
  PJSIP della distribuzione fuori passo.
- **`CMD ["asterisk", "-f", "-vvv"]`** esegue Asterisk in *primo piano* (`-f`, "non forkare"). Questa è la differenza fondamentale rispetto a un host systemd: il processo principale di un container
  non deve diventare demone, altrimenti il container terminerebbe immediatamente. Quindi in un container **non** usi affatto l'unità systemd — il runtime del container (Docker, più la politica `restart:`)
  diventa il supervisore che l'unità `Restart=` era su una VM.

### Bind-mounting `/etc/asterisk`

L'immagine contiene deliberatamente **nessuna** configurazione. Invece `docker-compose.yml`
bind-mounta la directory di configurazione dell'host in:

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

`./asterisk/etc:/etc/asterisk:ro` mappa la directory `lab/asterisk/etc` controllata da versionamento sul `/etc/asterisk` del container, in sola lettura (`:ro`). Il vantaggio è grande: l'immagine rimane immutabile e riutilizzabile, mentre la configurazione vive sull'host dove può essere modificata e, soprattutto, tenuta in git (sezione successiva). Per applicare una modifica alla configurazione si modifica il file e si ricarica — `docker compose exec asterisk asterisk -rx 'core reload'` — senza ricostruire. `restart: unless-stopped` è l'equivalente a livello di compose di systemd's `Restart=`: Docker riavvia il container se Asterisk termina, ma non se lo si ferma deliberatamente.

### Host vs. rete bridged — il problema RTP

Questo è il fallimento più comune di Asterisk containerizzato, quindi vale la pena comprenderlo con precisione. Per impostazione predefinita Docker colloca un container su una rete **bridged** e si pubblicano le porte individuali con `ports:`. Il segnalamento è a posto — 5060 è una porta. Il problema è il media: RTP utilizza un *intervallo* di porte UDP (il laboratorio `rtp.conf` imposta `rtpstart=10000` / `rtpend=10100`), e **ogni** porta che potrebbe trasportare audio deve essere pubblicata.

Il laboratorio fa esattamente questo:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

Nota che l'intervallo di pubblicazione RTP (`10000-10100`) corrisponde esattamente a `rtp.conf`. Se lo imposti in modo errato — pubblica troppi pochi porti, o un intervallo diverso da `rtp.conf` — le chiamate si connettono ma hanno **audio a senso unico o nessun audio**, perché i pacchetti RTP arrivano su una porta che Docker non sta inoltrando. Altre due precauzioni con la modalità bridge:

- **Pubblicare migliaia di porte è lento e pesante.** Un intervallo RTP di produzione è tipicamente 10000–20000. Docker crea ~10000 proxy userland è costoso all'avvio e aggiunge un salto nel percorso dei media. Il laboratorio mantiene un intervallo deliberatamente piccolo di 100 porte perché esegue solo una o due chiamate di prova.
- **NAT nel SDP.** Dietro il bridge, Asterisk vede il suo IP privato del contenitore e può pubblicarlo nel SDP. Su un host pubblico devi indicare a PJSIP il suo indirizzo esterno con `external_media_address` / `external_signaling_address` sul trasporto (e impostare `local_net`), esattamente come faresti dietro qualsiasi NAT — vedi *Cloud hosting* sotto.

L'alternativa è **host networking** (`network_mode: host`), che rimuove completamente il bridge: il contenitore condivide lo stack di rete dell'host, quindi 5060 e l'intero intervallo RTP sono raggiungibili senza pubblicazione di porte e senza salto extra nei media. Questa è la modalità consigliata per un vero contenitore Asterisk — elimina completamente il problema dell'intervallo RTP. Il suo costo è l'isolamento: il contenitore può legare qualsiasi porta dell'host e perdi la rete per servizio di compose. (Host networking è una funzionalità Linux; su Docker Desktop per macOS/Windows si comporta diversamente, il che è in parte il motivo per cui questo laboratorio didattico utilizza porte pubblicate esplicitamente.)

### Volumi persistenti per spool e voicemail

Lo strato scrivibile di un contenitore è **effimero** — distruggi il contenitore e tutto ciò che ha scritto sparisce. Per Asterisk ciò significa che voicemail, registrazioni, lo spool delle chiamate in uscita e il database locale svanirebbero ad ogni `docker compose up --build`. La configurazione sopravvive perché è bind-mounted dall'host; lo *stato* necessita dello stesso trattamento. All'interno del contenitore gli alberi rilevanti sono:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

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

Il laboratorio didattico omette questi di proposito — è senza stato e riproducibile per progettazione, quindi ogni `up` è una tabula rasa — ma un contenitore di produzione **deve** averli, altrimenti perderai la segreteria telefonica al primo ridistribuzione.

## Configuration management and backups

Il bind-mount sopra suggerisce il modello corretto: trattare `/etc/asterisk` come **code** e
il resto come **data**.

### Keep `/etc/asterisk` in version control

La directory di configurazione è un insieme piatto di file di testo senza segreti che non possono essere
templati — è ideale per git. Inizializza un repository in `/etc/asterisk` (o, come fa il laboratorio,
mantieni la configurazione accanto al progetto e bind-mountala). Benefici:

- Ogni modifica è revisionabile e reversibile (`git diff`, `git revert`).
- Hai una traccia di audit su chi ha cambiato cosa e quando.
- In combinazione con un'immagine container, un commit di configurazione noto‑buono più un tag immagine fissato
  descrivono completamente un deployment.

Un paio di avvertenze specifiche alla configurazione di Asterisk:

- **Secrets.** `pjsip.conf` (e `manager.conf`, `ari.conf`) contengono password. Non
  commettere segreti reali in un repository condiviso in chiaro — templali (un file per
  ambiente, o un gestore di segreti / sostituzione d'ambiente al momento del deploy) e mantieni
  solo segnaposto in git. Le password di stile `Lab-6001-secret` del laboratorio sono accettabili
  *solo* perché vivono su una subnet Docker privata.
- **Per-environment templating.** I valori realtime che differiscono tra dev, staging
  e produzione (indirizzi bind, IP esterni, credenziali trunk, URL database) sono
  esattamente le righe che devi templare, mantenendo la maggior parte della configurazione identica tra
  gli ambienti.

### What to back up

La configurazione in git copre il dialplan e gli endpoint, ma un PBX live accumula
*state* che non è presente in alcun file di configurazione. Un backup completo è:

| What | Where | Why |
|------|-------|-----|
| Configuration | `/etc/asterisk/` | dialplan, endpoints (also in git) |
| Voicemail & recordings | `/var/spool/asterisk/` | user data — irreplaceable |
| Internal database | `/var/lib/asterisk/astdb.sqlite3` | `DB()` keys, device state |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` or SQL store | billing & history |
| External databases | your MySQL/PostgreSQL | realtime, CDR, voicemail |

L'**astdb** merita una nota: è il piccolo archivio chiave/valore integrato di Asterisk (un
file SQLite in `/var/lib/asterisk/astdb.sqlite3`) usato dalle funzioni dialplan di `DB()`,
stati dei dispositivi, impostazioni follow‑me e simili. Puoi esportarlo per ispezione o backup
dal CLI:

```
asterisk -rx 'database show'
```

Se il tuo CDR/CEL o la segreteria telefonica o la configurazione PJSIP risiedono in un database esterno (vedi
*Asterisk Real-Time* e *Asterisk Call Detail Records*), quel database è ora la
fonte di verità per quei dati e deve far parte della tua normale rotazione di backup dei database —
eseguire il backup di `/etc/asterisk` da solo non è sufficiente.

## Monitoring and observability

Non puoi gestire ciò che non vedi. Asterisk espone il suo stato a quattro livelli, da
uno sguardo rapido umano a una pipeline di metriche: il **CLI**, i record **CDR/CEL**,
gli eventi **AMI/ARI**, e gli **exporter di metriche**.

### CLI health checks

Il controllo più veloce "è sano?" è il CLI. I comandi seguenti sono eseguiti in tempo reale contro
il laboratorio. Prima i canali:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` su un sistema inattivo è normale; su uno occupato questa è la tua concorrenza in tempo reale. `core show uptime` conferma che il processo non si sta riavviando sotto di te:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

Per lo stato di salute SIP, `pjsip show endpoints` mostra ogni endpoint e se i suoi contatti registrati sono raggiungibili. Dal laboratorio:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` qui significa semplicemente che nessun telefono è attualmente registrato a quegli endpoint (il laboratorio non ha client attivi) — una volta che un softphone si registra e `qualify` lo conferma, lo stato mostra il contatto come raggiungibile. Comandi di supporto: `pjsip show contacts` (registrazioni correnti e tempo di andata/ritorno), `pjsip show transports` e `pjsip show aor <name>` per un AOR. Questi sono gli strumenti quotidiani del tipo “perché l’estensione X non può essere raggiunta?”.

### CDR e CEL

Ogni chiamata genera un **Call Detail Record** (CDR); **Channel Event Logging** (CEL) aggiunge eventi più dettagliati per canale. Verifica che il CDR sia attivo e quale backend lo memorizza:

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

Il laboratorio mostra `(none)` sotto i backend registrati perché la configurazione minima del laboratorio non carica alcun modulo di archiviazione CDR — quindi i record vengono calcolati ma non scritti da nessuna parte. In produzione si carica un backend (CSV, o `cdr_odbc`/`cdr_adaptive_odbc` su MySQL/PostgreSQL) e questo diventa la tua fonte di fatturazione e storico. CEL è **disabilitato per impostazione predefinita** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` solo quando hai bisogno di dettagli a livello di evento. Entrambi sono trattati in profondità in *Asterisk Call Detail Records*; per il monitoraggio, il punto è che CDR/CEL sono il tuo record *storico*, mentre la CLI è la tua vista *in tempo reale*.

### AMI and ARI events

Per il monitoraggio programmatico e in tempo reale vuoi un flusso push di eventi anziché
interrogare la CLI:

- **AMI (Asterisk Manager Interface)** è il protocollo TCP di eventi/comandi di lunga data
  (`manager.conf`). Iscriviti e ricevi `Newchannel`, `Hangup`, `DialBegin`,
  `BridgeEnter`, `PeerStatus` e eventi simili man mano che le chiamate avvengono — la spina dorsale dei wallboard
  e degli strumenti di contabilità delle chiamate. Nel laboratorio AMI è disabilitato per impostazione predefinita (`manager show settings`
  segnala `Manager (AMI): No`); lo abiliti e lo blocchi in `manager.conf`.
- **ARI (Asterisk REST Interface)** è l’interfaccia moderna HTTP + WebSocket
  (`ari.conf`, servita dal server HTTP integrato). Fornisce un flusso di eventi JSON e
  un controllo delle chiamate a livello granulare — la scelta giusta per nuove integrazioni.

Entrambi sono dettagliati in *Extending Asterisk with AMI and AGI* e *The Asterisk REST
Interface (ARI)*. Avviso rilevante per il deployment: **AMI e ARI sono potenti e non devono mai essere esposte a Internet.** Lega il
server HTTP a localhost o a una rete di gestione, usa segreti forti e unici, e
configura il firewall sulle porte — vedi *Asterisk Security*.

### Metrics: Prometheus and Grafana

Per cruscotti e avvisi, Asterisk 22 fornisce un esportatore Prometheus,
**`res_prometheus.so`** (un modulo con livello di supporto *esteso*), che espone metriche
su un endpoint HTTP che un server Prometheus raccoglie. Accanto alle metriche di processo core, fornisce provider plug‑in che coprono canali, chiamate, endpoint, bridge e registrazioni outbound PJSIP:

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

Puoi confermare che il modulo è presente nella build di laboratorio:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it (`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active calls dropped to zero" or "registration failures spiking"). For teams already running Prometheus/Grafana this is the natural way to fold Asterisk into existing observability, rather than parsing CLI output.

### Codici di risposta SIP da tenere d'occhio

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on: sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*); `503 Service Unavailable` points at an overloaded or congested server or trunk; and a spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints have gone unreachable (NAT timeout, qualify failures).

## High availability and scaling

Un server Asterisk è un punto unico di guasto e ha un limite finito di chiamate. I due
problemi — *rimanere attivi* e *crescere* — hanno risposte diverse.

### Active/standby with a floating IP

Il classico, ben collaudato modello HA per Asterisk è **active/standby** (non
active/active — lo stato delle chiamate in Asterisk è difficile da condividere in tempo reale). Due server identici,
uno attivo, uno in standby, condividono un **floating (virtual) IP** gestito da un gestore di cluster
come **keepalived** (VRRP) o **Pacemaker/Corosync**. Telefoni e trunk si registrano al
floating IP, non a ciascun host reale. Se il nodo attivo fallisce il suo health check, il
floating IP passa allo standby, che prende il controllo.

La sincera avvertenza: un failover IP **fa cadere le chiamate in corso** — Asterisk non
replica lo stato dei canali in tempo reale tra i nodi, quindi chi è a metà chiamata deve
richiamare. Le registrazioni si ristabiliscono entro un ciclo di qualify/registration. Ciò che il failover ti offre è che il
*servizio* si ripristina in pochi secondi senza intervento manuale, che per la maggior parte dei PBX è esattamente
l'obiettivo. Per far sì che lo standby sia realmente in grado di subentrare, entrambi i nodi devono avere la stessa
configurazione (il tuo git'd `/etc/asterisk`, distribuita identicamente) e lo stesso *state* —
che è il punto successivo.

### Externalize state with PJSIP Realtime

Active/standby funziona solo se lo standby conosce gli stessi endpoint e
registrazioni del nodo attivo. Il modo per ottenerlo è **smettere di tenere lo stato in
file flat su una singola macchina** e spostarlo in un database condiviso che entrambi i nodi leggono. **PJSIP
Realtime** (Sorcery supportato da un database) fa esattamente questo: endpoint, AOR, auth —
e, cosa importante, **registrations** (la tabella `ps_contacts`) — vivono in MySQL/PostgreSQL
invece di `pjsip.conf` e della memoria locale. Entrambi i nodi Asterisk puntano allo stesso database,
così un telefono registrato tramite un nodo è visibile all'altro. Questo è trattato in
*Asterisk Real-Time* (la sezione PJSIP Realtime / Sorcery); qui il punto di deployment è
che **externalizzare lo stato è il prerequisito sia per HA sia per lo scaling orizzontale** —
senza di esso, ogni nodo è un'isola.

Applica la stessa logica al resto del tuo stato: CDR/CEL in un archivio SQL condiviso, voicemail
su storage condiviso/replicato (o `ODBC_STORAGE`), e le chiavi astdb di cui dipendi in un
database. Una volta che lo stato è esterno, i nodi Asterisk diventano più simili a front-end intercambiabili.

### SIP proxies in front (OpenSIPS)

Per scalare *oltre* la capacità di un singolo server si mette un **SIP proxy/load balancer** davanti a
un pool di server media Asterisk. **OpenSIPS** è un proxy SIP costruito appositamente, molto
high-throughput (gestisce centinaia di migliaia di registrazioni e instrada
segnalazione senza toccare i media). Il proxy presenta un unico indirizzo SIP al mondo,
mantiene il servizio di registrazione/locazione, e distribuisce le chiamate tra i back-end Asterisk.
Questa separazione — un livello proxy leggero che gestisce registrazione e routing, un
livello Asterisk scalabile orizzontalmente che esegue l'effettivo processamento delle chiamate (IVR, code,
conferenze, transcoding) — è il modo in cui grandi implementazioni superano un singolo box. (La piattaforma SipPulse
usa OpenSIPS davanti ai suoi server media/applicazione proprio per questo motivo.)

### Media scaling

Il proxy distribuisce *segnalazione* a basso costo; **i media sono la risorsa costosa**. Il relay RTP,
e soprattutto il transcoding tra codec (es. Opus ↔ G.711)

## Cloud hosting

Eseguire Asterisk su una VM cloud (AWS, GCP, Azure, un VPS) è comune e funziona bene, ma la
rete cloud è **NAT‑ed e protetta da firewall per impostazione predefinita**, il che crea conflitti con SIP. Di seguito sono riportate le problematiche specifiche del deployment.

### NAT e l'SDP

Una VM cloud ha quasi sempre un IP **privato** sulla sua NIC e un IP **pubblico** separato che
il provider NATta verso di esso. Se Asterisk pubblica l'IP privato nell'SDP, i telefoni remoti inviano
RTP in un buco nero — il classico sintomo di audio unidirezionale/assenza di audio. Indica a PJSIP la sua identità pubblica sul trasporto:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` fa riscrivere a Asterisk l'indirizzo che pubblica verso i peer pubblici, mentre
`local_net` indica quali peer sono locali (e non devono essere riscritti). Questo è lo stesso
gestione NAT discussa per il networking Docker bridged sopra — una VM cloud è, in
pratica, dietro NAT.

### Firewall e l'intervallo RTP

Di solito su una VM cloud si applicano due firewall: il **gruppo di sicurezza** del provider / ACL di rete,
e il **firewall** dell'host (iptables). Entrambi devono aprire le stesse porte, e la politica è
quella del capitolo Sicurezza. Il set di regole della prima edizione recuperato
(`docs/legacy-labs/configs/Lab7/rules.v4`) cattura la forma — accetta SIP e l'intervallo RTP,
accetta connessioni stabilite/relative, scarta il resto:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

Due correzioni apportate nel capitolo Sicurezza che contano qui: apri **5061 su TCP** (non
UDP) se utilizzi SIP/TLS, e ricorda che l'intervallo UDP RTP nel tuo firewall deve corrispondere a
`rtpstart`/`rtpend` in `rtp.conf` esattamente — lo stesso intervallo che pubblichi su un container.
Non duplicare qui la costruzione iptables/Fail2Ban; **segui le sezioni firewall, Fail2Ban e
TLS/SRTP di *Asterisk Security*** (Fail2Ban monitora il canale di log `security` che il laboratorio già abilita in `logger.conf`) e applica quella politica sia nel firewall
dell'host sia nel gruppo di sicurezza cloud.

### Latenza, regione e l'SBC

- **Scegli una regione vicina ai tuoi utenti.** La voce è sensibile alla latenza — una latenza
  unidirezionale bocca‑orecchio superiore a ~150 ms è percepibile. Posiziona la VM nella regione più vicina alla maggior parte dei tuoi
  telefoni e trunk; i media intercontinentali risultano udibilmente peggiori.
- **Metti un SBC davanti a qualsiasi deployment esposto a Internet.** Un **Session Border
  Controller** termina SIP/RTP al bordo, nasconde la tua topologia, normalizza il NAT e
  assorbe traffico DoS e di scansione prima che raggiunga Asterisk. La raccomandazione principale del capitolo Sicurezza — *non esporre Asterisk grezzo a Internet* — è ancora più valida nel
  cloud, dove l'IP pubblico della tua VM viene scansionato entro minuti dall'avvio. Un SBC (o
  almeno un proxy SIP rinforzato come OpenSIPS più Fail2Ban) è lo standard
  al bordo.

## Summary

Deployment is where a working dialplan becomes a dependable service. On a VM, run  
Asterisk under **systemd** as a **non-root** user, letting the unit's `Restart=` keep it  
alive (safe_asterisk is superseded) and using `core reload` rather than `systemctl  
restart` for config changes. **Containerizing** with Docker — as the book's lab does —  
gives you an immutable, pinned image with config **bind-mounted** from a git'd  
`/etc/asterisk`; the catch is media, so either use **host networking** or publish an RTP  
port range that **exactly matches `rtp.conf`**, and mount **persistent volumes** for  
spool/voicemail/astdb so state survives a redeploy. Treat config as code and **back up the  
state** config does not capture: voicemail, recordings, `astdb.sqlite3`, and CDR/CEL.  
**Observe** the system at four levels — the CLI (`core show channels`, `pjsip show  
endpoints`) for the live view, **CDR/CEL** for history, **AMI/ARI** for programmatic  
events, and the **`res_prometheus`** exporter into Grafana for dashboards and alerts —  
while keeping AMI/ARI off the public internet. To **stay up**, run active/standby with a  
**floating IP** (accepting that failover drops live calls); to **grow**, externalize state  
with **PJSIP Realtime**, front a pool of media servers with **OpenSIPS**, and  
minimize transcoding because **media — not registrations — is what caps a server**.  
Finally, in the **cloud**, treat the VM as behind NAT (`external_media_address`,  
`local_net`), open the firewall per the Security chapter in both the host and the provider  
security group, pick a low-latency region, and never expose raw Asterisk — put an **SBC**  
at the edge.

## Quiz

1. Su un host systemd, cosa sostituisce il vecchio wrapper `safe_asterisk` per il riavvio di un Asterisk
   crashato?
   - A. Un lavoro cron
   - B. La direttiva `Restart=` del file unit
   - C. `systemctl enable`
   - D. L'astdb
2. Per applicare una modifica di configurazione a un Asterisk in esecuzione **senza interrompere le chiamate**, dovresti:
   - A. `systemctl restart asterisk`
   - B. Riavviare il server
   - C. `asterisk -rx 'core reload'`
   - D. Ricostruire l'immagine del container
3. Un Asterisk containerizzato (rete bridge) collega le chiamate ma **non ha audio**. La causa più probabile è:
   - A. Il dialplan è errato
   - B. L'intervallo di porte UDP RTP pubblicato non corrisponde a `rtpstart`/`rtpend` in `rtp.conf`
   - C. Il CDR è disabilitato
   - D. La CLI è irraggiungibile
4. Quali directory devono essere montate come **volumi persistenti** affinché un ridispiegamento del container non perda lo stato? (seleziona tutte le opzioni valide)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (già bind-mounted dall'host)
   - D. `/usr/sbin`
5. Quale comando CLI fornisce il conteggio in tempo reale delle chiamate attive?
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. In Asterisk 22, il modo supportato per esporre metriche di chiamata/canale a uno stack Prometheus/Grafana è:
   - A. Analizzare il file di log `full`
   - B. Il modulo `res_prometheus.so`
   - C. Script AGI
   - D. Nessuno
7. Qual è il prerequisito sia per il failover HA sia per il dimensionamento orizzontale su più nodi Asterisk?
   - A. Esecuzione come root
   - B. Esternalizzare lo stato (ad es. registrazioni PJSIP Realtime in un database condiviso)
   - C. Disabilitare il CDR
   - D. Usare rete bridge
8. Quale risorsa limita più direttamente il numero di chiamate simultanee che un server Asterisk può gestire?
   - A. Il numero di utenti registrati
   - B. Elaborazione media, specialmente il transcoding
   - C. La dimensione di `/etc/asterisk`
   - D. Il backend del CDR
9. Su una VM cloud, quali impostazioni di trasporto `pjsip.conf` fanno sì che Asterisk annunci il suo indirizzo pubblico affinché l'audio remoto funzioni? (seleziona tutte le opzioni valide)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. Per un deployment cloud esposto a Internet, la regola fondamentale del capitolo Sicurezza è:
    - A. Utilizzare sempre due NIC
    - B. Non esporre mai Asterisk grezzo a Internet; posizionare un SBC (o proxy rinforzato + Fail2Ban) al perimetro
    - C. Usare solo UDP
    - D. Disabilitare TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
