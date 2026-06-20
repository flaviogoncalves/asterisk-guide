# Designing a VoIP network

Voice over IP is quickly growing in the telephony market. The convergence paradigm is changing the way in which we communicate, reducing costs and enhancing the way in which we trade information. Voice is just the beginning of a full multimedia communication era, including voice, video, and presence. In the future, we are not going to transport people to work, but work to people because it is cleaner, faster, and cheaper. VoIP is just part of this revolution. Our challenge in this chapter is to design a VoIP network. To do this, we will have to understand concepts such as session protocols and codecs as well as how to dimension the number of circuits and bandwidth.

## Obiettivi

By the end of this chapter, you should be able to:

- Comprendere i vantaggi del VoIP
- Descrivere come Asterisk gestisce il VoIP
- Descrivere i concetti dei canali SIP e IAX
- Scegliere il protocollo più adeguato per un canale dati specifico
- Scegliere il codec più adeguato per un canale dati specifico
- Dimensionare il numero richiesto di canali
- Calcolare la larghezza di banda richiesta

## VoIP benefits

Why would you care about VoIP? VoIP provides benefits to both companies and individuals. Cost reduction is certainly one of them, but in some environments VoIP simplifies the integration of computer systems. Several of the benefits are detailed here:

### Convergence

The primary benefit of VoIP is the combination of data and voice networks to reduce costs (convergence). However, analyzing just voice minute costs may not be enough to justify the adoption of VoIP. The price of the minutes sold by phone companies is quickly becoming cheaper and is something to be considered before adopting VoIP.

### Infrastructure costs

The use of a single network infrastructure reduces the costs associated with additions, removals, and changes. As IP has become pervasive, it has brought VoIP-related technology to several new devices, such as cell phones, PDAs, embedded systems, and laptops.

### Open Standards

Finally, the open standards upon which VoIP is built provide the freedom to choose from different vendors. This single benefit makes the customer king instead of a subordinate to TELCOS and PBX manufacturers.

### Computer Telephony Integration

Telephony is far older than computing. Telephony PBXs are circuit-switch based, and you usually do not have more than a computer for supervision. With VoIP, telephony is from the ground up created based in computer standards. This makes the use of Computer Telephony applications cheaper and easier than in the old model. You can quickly create a long list of telephony applications based on Asterisk. You can develop IVRs, ACDs, CTI, dialers, screen popups, and other applications in a fraction of the time required for traditional PBXs.

## Architettura VoIP di Asterisk

L'architettura di Asterisk è mostrata di seguito. Asterisk tratta tutti i protocolli VoIP come canali. Puoi usare qualsiasi codec o qualsiasi protocollo. Il concetto da apprendere qui è che Asterisk collega qualsiasi tipo di canale a qualsiasi altro. Pertanto, è possibile tradurre protocolli di segnalazione come SIP e IAX l'uno nell'altro e anche con codec diversi. Per esempio, puoi tradurre una chiamata da un telefono SIP nella rete locale usando il codec G.711 a un trunk SIP verso il tuo provider VoIP usando il codec G.729. Nei capitoli successivi spiegheremo i dettagli dell'architettura SIP e IAX. Il supporto H.323 (tramite il componente aggiuntivo chan_ooh323) è disponibile ma sempre più raro; SIP/PJSIP è lo standard per le implementazioni moderne.

![Architettura modulare di Asterisk: le applicazioni e i canali si collegano al nucleo dello switch PBX tramite API, con traduzione dei codec e moduli di formato file caricati dinamicamente.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP utilizza un insieme di protocolli diversi che lavorano insieme. È allettante allinearli al modello di riferimento OSI a sette strati, e molti diagrammi più vecchi lo fanno esattamente — posizionando SIP e H.323 allo strato "sessione" e i codec allo strato "presentazione". Tale mappatura è sempre stata controversa. L'IETF, che standardizza SIP, non usa il modello OSI; segue il più vecchio modello a quattro strati TCP/IP (DoD), e l'RFC 3261 definisce **SIP come un protocollo di livello applicazione**. I media seguono lo stesso schema: RTP e i codec vivono nel payload applicativo, trasportati su UDP allo strato di trasporto. La tabella sotto mappa i principali protocolli VoIP sul modello TCP/IP che l'IETF utilizza realmente, con l'equivalente OSI approssimativo mostrato solo per riferimento.

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

I meccanismi QoS come DiffServ operano allo strato IP per dare priorità ai pacchetti vocali e migliorare la qualità delle chiamate. Alcune specifiche dei protocolli:

- **SIP** usa UDP o TCP sulla porta 5060 (TLS su 5061) per trasportare il signaling. L'audio è trasportato separatamente da RTP su un intervallo di porte UDP configurabile (il campione `rtp.conf` fornito con Asterisk utilizza da 10000 a 20000), codificato con un codec come G.711.
- **H.323** trasporta il signaling della chiamata su TCP (signaling H.225 sulla porta 1720), mentre il canale H.225 RAS usa UDP sulla porta 1719; RTP trasporta l'audio.
- **IAX2** è insolito: multiplexa sia il signaling sia i media su un'unica porta UDP (4569), il che semplifica il traversal di NAT e firewall.


## Come scegliere un protocollo

Data la moltitudine di protocolli, come si può scegliere quello più adatto alla propria rete? In questa sezione evidenzieremo i vantaggi e gli svantaggi di ciascun protocollo.

### SIP - Session Initiated Protocol

SIP è uno standard aperto dell'Internet Engineering Task Force (IETF), ampiamente definito nella RFC 3261. La maggior parte dei fornitori di VoIP moderni utilizza SIP; infatti, sta diventando lo standard VoIP più popolare. Il punto di forza di SIP è che è uno standard basato su IETF. SIP è leggero rispetto al più vecchio H.323. La principale debolezza di SIP è il superamento del NAT—una sfida per la maggior parte dei fornitori di VoIP SIP. L'IETF non ha creato SIP pensando alla fatturazione, ma per comunicazioni aperte tra peer. La fatturazione è solitamente una preoccupazione per i fornitori di VoIP.

### IAX – Inter Asterisk eXchange

IAX è un protocollo aperto originariamente sviluppato da Digium (ora Sangoma). IAX è un protocollo tutto-in-uno poiché trasporta segnalazione e media attraverso la stessa porta UDP (4569). Mark Spencer ha sviluppato IAX come protocollo binario per ridurre la larghezza di banda. Il principale punto di forza di IAX è il suo consumo ridotto di larghezza di banda (non utilizza RTP); è anche molto semplice per il superamento di NAT e firewall poiché usa una sola porta UDP (4569).

Se un produttore tradizionale di PBX avesse creato IAX, probabilmente avrebbe commercializzato il protocollo come la “cosa migliore dal gelato”; in alcune situazioni, IAX in modalità trunk può ridurre l'uso della larghezza di banda vocale di un terzo. IAX2 (versione 2) è ancora incluso in Asterisk 22 tramite il modulo `chan_iax2` e rimane utile per trunk Asterisk‑to‑Asterisk, sebbene sia considerato legacy; SIP/PJSIP è preferito per nuove implementazioni. IAX2 è specificato in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP è un protocollo usato in combinazione con H.323, SIP e IAX. Il suo più grande vantaggio è la scalabilità. È configurato nell'agente di chiamata anziché nei gateway. Ciò semplifica il processo di configurazione e consente una gestione centralizzata. Tuttavia, l'implementazione in Asterisk non è completa, e sembra che non molte persone lo utilizzino.

### H.323

H.323 è ancora ampiamente usato in VoIP. È uno dei primi protocolli VoIP ed è essenziale per collegare infrastrutture VoIP più vecchie basate su gateway. H.323 è ancora lo standard nel mercato dei gateway, sebbene il mercato stia lentamente migrando verso SIP. I punti di forza di H.323 includono la grande adozione di mercato e la maturità. Le debolezze di H.323 sono legate alla complessità di implementazione e ai costi associati agli organismi di standardizzazione.

### Tabella comparativa dei protocolli

La tabella seguente riassume le differenze tra i protocolli di sessione.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## Un endpoint per dispositivo

In Asterisk 22 lo stack PJSIP modella ogni telefono, trunk o gateway come un unico oggetto **endpoint** in `pjsip.conf`. Un endpoint sia piazza sia riceve chiamate; le sue credenziali vivono in un oggetto `auth`, il suo indirizzo registrato in un `aor`, e il suo percorso di rete in un `transport`. Si configura un endpoint per dispositivo e si collegano i componenti necessari — non esiste un ruolo separato di "user" rispetto a "peer" da considerare. (Il modello completo degli oggetti è trattato in *SIP & PJSIP in depth*.)

## Codecs and codec translation

Userai un codec per convertire la voce da un'onda analogica a un segnale digitale. I codec differiscono tra loro per aspetti come la qualità del suono, il tasso di compressione, la larghezza di banda e i requisiti di calcolo. Servizi, telefoni e gateway solitamente supportano diversi di questi aspetti. Il codec G.729 è molto popolare. Non fa parte della build standard di Asterisk 22; invece è fornito come modulo aggiuntivo esterno (`codec_g729`) che scarichi da Digium (ora Sangoma). Il sorgente `menuselect` di Asterisk lo elenca con `support_level=external` e nota chiaramente: "Download the g729a codec from Digium. A license must be purchased for this codec." In altre parole, l'uso legale di G.729 richiede una licenza per canale acquistata. (Esiste anche un'alternativa open‑source, `bcg729`.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 supporta i seguenti codec (tra gli altri):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — qualità PSTN standard; ulaw comune in Nord America, alaw comune in Europa e America Latina
- ITU G.722: 64 Kbps — wideband (HD voice), buona qualità con la stessa larghezza di banda di G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — modulo binario esterno `codec_g729` scaricato da Digium/Sangoma (`support_level=external`; è necessaria una licenza per usarlo)
- Speex: 2.15 to 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variabile — codec moderno wideband/fullband; eccellente qualità e resilienza alla perdita di pacchetti; fornito come modulo binario esterno `codec_opus` scaricato da Digium/Sangoma (`support_level=external`; non è indicato l'acquisto di licenza, a differenza di G.729); consigliato per WebRTC e endpoint SIP moderni. (Esistono alternative di build open‑source su GitHub.)

Inoltre, Asterisk consente la traduzione tra codec. In alcuni casi, ciò non è possibile, come nel caso di g723, supportato solo in modalità pass‑thru. Tradurre da un codec a un altro consuma molte risorse CPU. Pertanto, evita questa operazione quando possibile.

## How to choose a Codec

La scelta del codec dipende da diverse opzioni, come:

- Qualità del suono
- Costi di licenza
- Consumo di CPU
- Requisiti di larghezza di banda
- Nascondimento della perdita di pacchetti
- Disponibilità per Asterisk e dispositivi telefonici

La tabella seguente confronta i codec più popolari. La qualità di questi codec è considerata “toll”—in altre parole, simile alla PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

I moduli Asterisk 22 sono: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core) e GSM `codec_gsm` (core). Opus è “Narrow–full” perché scala dal narrowband al fullband; la sua larghezza di banda (6–510 Kbps) è variabile, e la sua resistenza all’erasure dei frame proviene dal FEC/PLC integrato.

Il riferimento PSTN è **G.711** — è il riferimento per la qualità “toll” e transcodifica gratuitamente all’interno di Asterisk. **G.722** offre voce wideband (HD) alla stessa velocità di 64 Kbps ed è una buona scelta LAN/interna. **Opus** è il moderno default per endpoint WebRTC e SIP capaci: adatta il bitrate, ha correzione d’errore in avanti integrata e resiste bene alla perdita di pacchetti; è fornito come binario esterno `codec_opus` (gratuito da scaricare). **G.729** rimane utile su trunk WAN a bassa larghezza di banda, ma l’uso legale richiede il binario con licenza di Sangoma `codec_g729` (gratuito da scaricare, licenza per canale per l’uso) o l’implementazione open‑source **bcg729** come alternativa.

¹ Il binario `codec_g729` di Sangoma è gratuito da scaricare ma richiede una licenza per canale acquistata per l’uso legale. L’alternativa open‑source `bcg729` è priva di licenza.

² La resistenza all’erasure dei frame indica quanto bene la qualità percepita (MOS) si mantiene sotto perdita di pacchetti. Il punto di crossover esatto varia con la packetizzazione e le condizioni di rete; usa questa colonna per un confronto relativo, non come valore preciso.

**Raccomandazioni sui codec per Asterisk 22:**

- **G.711 (ulaw/alaw):** Da usare per trunk PSTN e massima interoperabilità; costo di transcoding zero all’interno di Asterisk.
- **G.729:** Utile per trunk WAN a bassa larghezza di banda; il modulo `codec_g729` di Sangoma è gratuito da scaricare ma richiede una licenza per canale acquistata per l’uso.
- **G.722:** Buona scelta per voce wideband (HD) su estensioni LAN/interni; stessa larghezza di banda di G.711 con qualità migliore.
- **Opus:** Consigliato per endpoint moderni, client WebRTC e qualsiasi distribuzione in cui l’endpoint lo supporta. Bitrate adattivo, eccellente resilienza alla perdita di pacchetti, disponibile gratuitamente tramite il modulo binario `codec_opus` di Sangoma.

## Overhead causato dalle intestazioni di protocollo

Nonostante i codec utilizzino poco larghezza di banda, dobbiamo considerare l'overhead causato dalle intestazioni di protocollo come Ethernet, IP, UDP e RTP. Pertanto, la larghezza di banda effettivamente consumata dipende dalle intestazioni utilizzate. Su una rete Ethernet il requisito è più alto rispetto a una rete PPP, perché l'intestazione PPP è più corta di quella Ethernet. Un singolo pacchetto vocale G.729, ad esempio, trasporta solo 20 byte di payload ma è avvolto in circa 58 byte di intestazioni Ethernet, IP, UDP e RTP — quindi sono le intestazioni, non il codec, a dominare la larghezza di banda (vedi la figura sotto).

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Puoi calcolare facilmente altri requisiti di larghezza di banda usando un calcolatore online di larghezza di banda VoIP come <https://www.voip.school/bandcalc/bandcalc.php>.


## Traffic Engineering

Un problema principale nella progettazione delle reti VoIP è dimensionare il numero di linee e la larghezza di banda necessaria verso una destinazione specifica, come un ufficio remoto o un provider di servizi. È anche importante dimensionare il numero di chiamate simultanee di Asterisk (parametro principale per il dimensionamento di Asterisk).

### Simplifications

La semplificazione primaria e più ampiamente usata è stimare il numero di chiamate per tipo di utente. Per esempio:

- Business PBX (una chiamata simultanea per ogni cinque estensioni)
- Utenti residenziali (una chiamata simultanea per ogni sedici utenti)

Example #1 La sede centrale dell'azienda ha 120 estensioni e due filiali—la prima con 30 estensioni e la seconda con 15 estensioni. Il nostro obiettivo è dimensionare il numero di trunk E1 nella sede centrale e la larghezza di banda richiesta per la rete Frame‑Relay.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Number of T1 lines

- Numero totale di estensioni che usano linee T1: 120+30+15=165 linee
- Utilizzando un trunk per ogni cinque estensioni per uso business
- Numero totale di linee = 33 o circa 2xT1 linee

1b Bandwidth requirements Scegliamo il codec g.729 per le esigenze di larghezza di banda, qualità del suono e consumo medio di CPU.

Con un trunk per ogni cinque estensioni:

- Larghezza di banda richiesta per la filiale #1 (Frame‑relay): 26.8*6=160.8 Kbps
- Larghezza di banda richiesta per la filiale #2 (Frame‑relay): 26.8*3= 80.4 Kbps

### Erlang B method

Quando si dispone di dati storici, è possibile dimensionare il trunk in modo più scientifico invece di semplificare. Useremo il lavoro di Agner Karup Erlang (Copenhagen Telephone Company, 1909), che sviluppò una formula per calcolare il numero di linee in un gruppo di trunk tra due città.

Un **Erlang** è un'unità di misura del traffico comune nelle telecomunicazioni; descrive il volume di traffico durante un'ora. Per esempio, supponiamo che in un'ora avvengano 20 chiamate, con una media di 5 minuti di conversazione ciascuna:

- Minuti di traffico nell'ora: 20 × 5 = 100 minuti
- Ore di traffico in un'ora: 100 / 60 = **1.66 Erlangs**

È possibile leggere queste misure da un call logger e usarle per progettare la rete e calcolare il numero di linee richieste. Una volta noto il numero di linee, si possono calcolare i requisiti di larghezza di banda.

**Erlang B** è il metodo più comunemente usato per calcolare il numero di linee in un gruppo di trunk. Assume che le chiamate arrivino in modo casuale (distribuzione di Poisson) e che le chiamate bloccate vengano immediatamente liberate. Richiede di conoscere il **Busy Hour Traffic (BHT)**, che si può ottenere da un call logger o stimare come semplificazione: BHT = 17 % dei minuti di chiamata di un giorno.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

Un'altra variabile importante è il Grade of Service (GoS), che definisce la probabilità di bloccare chiamate per mancanza di linee. Si può arbitrariamente impostare questo parametro, solitamente 0.05 (5 % chiamate perse) o 0.01 (1 % chiamate perse). Example #1: Usando lo stesso esempio di sede centrale e due filiali introdotto in precedenza in questa sezione, vi forniremo alcuni dati sui pattern di traffico. Dal call logger, abbiamo scoperto questi dati: Dati dal call logger (Minuti di chiamata

## Ridurre la larghezza di banda richiesta per la VoIP

Tre metodi possono essere usati per ridurre la larghezza di banda richiesta per le chiamate VoIP:

- Compressione dell'intestazione RTP
- Trunk IAX
- Payload VoIP

### Compressione dell'intestazione RTP

Nelle reti Frame-Relay e PPP, è possibile utilizzare la compressione dell'intestazione RTP. La compressione dell'intestazione RTP è stata definita nella RFC 2508. È uno standard IETF disponibile in diversi router. Tuttavia, fate attenzione, poiché alcuni router richiedono un diverso set di funzionalità affinché questa risorsa sia disponibile. L'impatto dell'uso della compressione dell'intestazione RTP è notevole, poiché riduce la larghezza di banda richiesta nel nostro esempio da 26,8 Kbps per conversazione vocale a 11,2 Kbps — una riduzione del 58,2 %!

### Modalità trunk IAX2

Se state collegando due server Asterisk, potete usare il protocollo IAX2 in modalità trunk. Questa tecnologia rivoluzionaria non richiede router speciali e può essere applicata a qualsiasi tipo di collegamento dati.

![IAX2 trunk mode on Ethernet: a single g.729 call needs its full header stack (31.2 Kbps), but a second call shares those headers and adds only a small IAX2 miniframe, averaging about 9.6 Kbps of extra bandwidth per additional call.](../images/06-voip-network-fig08.png)

La modalità trunk IAX2 riutilizza le stesse intestazioni dalla seconda chiamata in poi. Usando g.729 in un collegamento PPP, la prima chiamata consumerà 30 Kbps di larghezza di banda, mentre la seconda chiamata utilizzerà la stessa intestazione della prima e ridurrà la larghezza di banda necessaria per la chiamata aggiuntiva a 9,6 Kbps. Possiamo calcolare la larghezza di banda richiesta in modalità trunk come segue: Branch #1 (11 calls) Bandwidth = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Branch #2 (8 calls) Bandwidth = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps La prima chiamata usa 31,2 Kbps, la successiva 9,6 Kbps, e così via.

### Aumento del payload vocale

Questo metodo è molto comune quando si usano gateway VoIP su Internet. Quando si utilizza un payload più grande, si sacrifica la latenza a favore di una larghezza di banda ridotta. È possibile modificare la packetizzazione RTP aggiungendo la dimensione del frame al codec nell'istruzione allow.

![Increasing the voice payload: packing 60 bytes of g.729 payload into one packet (instead of 20) amortizes the 58 bytes of headers across more voice, dropping bandwidth to about 16.05 Kbps per call at the cost of added latency.](../images/06-voip-network-fig09.png)

Esempio:

```
allow=ulaw:30
```

Il numero dopo i due punti è l'intervallo di packetizzazione in millisecondi — quanta voce è trasportata in ogni pacchetto RTP. Un valore più grande ammortizza l'overhead fisso dell'intestazione su più audio (meno larghezza di banda) a costo di latenza aggiuntiva. Ogni codec ha la propria dimensione minima, massima e predefinita del frame; G.711 (`ulaw`/`alaw`), per esempio, ha come valore predefinito 20 ms.

## Sommario

In questo capitolo hai appreso che Asterisk gestisce la VoIP tramite canali. Supporta SIP (via `chan_pjsip` in Asterisk 22) e IAX2; H.323 è disponibile solo tramite il componente aggiuntivo della community `ooh323`, e i canali più vecchi MGCP e SCCP (Skinny) non fanno più parte di una build standard di Asterisk 22. Hai confrontato e imparato come scegliere un protocollo di segnalazione e un codec per i canali VoIP. IAX2 è più efficiente in termini di larghezza di banda e può attraversare NAT facilmente. SIP/PJSIP è il protocollo più supportato dai fornitori di telefoni e gateway di terze parti ed è l’unico driver di canale SIP in Asterisk 22. Il protocollo H.323 è il più antico e dovrebbe essere usato per connettersi a infrastrutture VoIP legacy. Nella sezione Ingegneria del Traffico, abbiamo imparato come progettare e dimensionare una rete VoIP.

## Quiz

1. Quali dei seguenti sono i vantaggi del VoIP descritti in questo capitolo (seleziona tutti quelli applicabili)?
   - A. Convergenza di reti dati e voce per ridurre i costi
   - B. Minori costi di infrastruttura per aggiunte, rimozioni e modifiche
   - C. Standard aperti che ti liberano da un unico fornitore
   - D. Integrazione Computer Telephony più semplice ed economica
   - E. Tariffe per minuto garantite più basse rispetto a qualsiasi compagnia telefonica
2. La convergenza è l'integrazione di voce, dati e video in una singola rete; il suo beneficio principale è la riduzione dei costi nell'implementazione e nella manutenzione di reti separate.
   - A. Falso
   - B. Vero
3. Asterisk tratta ogni protocollo VoIP come un canale e può collegare qualsiasi tipo di canale a qualsiasi altro, effettuando il transcoding tra codec quando necessario.
   - A. Falso
   - B. Vero
4. In Asterisk 22, SIP è gestito da quale driver di canale?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. Nel modello TCP/IP (IETF) contro il quale SIP è effettivamente definito nel RFC 3261, i protocolli di segnalazione SIP, H.323 e IAX2 operano al livello ___.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP è il protocollo più adottato per i telefoni IP ed è uno standard aperto ampiamente definito dall'IETF nel RFC 3261.
   - A. Falso
   - B. Vero
7. IAX2 trasporta sia la segnalazione sia i media su una singola porta UDP, il che lo rende efficiente e facile da attraversare NAT. Quale porta UDP utilizza IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX è stato originariamente sviluppato da Digium (ora Sangoma). Nonostante l'adozione limitata da parte dei fornitori di telefoni, IAX è eccellente quando hai bisogno (seleziona tutti quelli applicabili):
   - A. Ridurre l'uso di larghezza di banda (non utilizza RTP)
   - B. Un formato video per i media
   - C. Traversata NAT e firewall semplice
   - D. Modalità trunk per combinare molte chiamate Asterisk‑to‑Asterisk e ammortizzare l'overhead dell'header
9. In Asterisk 22, un dispositivo è configurato come un unico oggetto PJSIP `endpoint` che sia effettua sia riceve chiamate — non esiste un ruolo separato di "user" o "peer".
   - A. Falso
   - B. Vero
10. Per quanto riguarda i codec in Asterisk 22, seleziona tutte le affermazioni vere:
    - A. G.711 è equivalente a PCM e utilizza 64 Kbps di larghezza di banda.
    - B. Il modulo codec_g729 di Sangoma è gratuito da scaricare, ma l'uso legale richiede una licenza per canale acquistata.
    - C. GSM è popolare perché utilizza circa 13 Kbps e non richiede licenza.
    - D. G.711 u‑law è comune in Nord America, mentre a‑law è comune in Europa e America Latina.
    - E. G.729 è leggero e utilizza pochissime risorse CPU per codificare e decodificare rispetto a G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
