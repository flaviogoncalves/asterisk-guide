# Progettare una rete VoIP

Il Voice over IP sta crescendo rapidamente nel mercato della telefonia. Il paradigma della convergenza sta cambiando il modo in cui comunichiamo, riducendo i costi e migliorando il modo in cui scambiamo informazioni. La voce è solo l'inizio di un'era di comunicazione multimediale completa, che include voce, video e presenza. In futuro, non saremo noi a spostarci per andare al lavoro, ma sarà il lavoro a venire da noi, perché è più pulito, più veloce e più economico. Il VoIP è solo una parte di questa rivoluzione. La nostra sfida in questo capitolo è progettare una rete VoIP. Per farlo, dovremo comprendere concetti come i protocolli di sessione e i codec, oltre a come dimensionare il numero di circuiti e la larghezza di banda.

## Obiettivi

Al termine di questo capitolo, dovresti essere in grado di:

- Comprendere i vantaggi del VoIP
- Descrivere come Asterisk gestisce il VoIP
- Descrivere i concetti dei canali SIP e IAX
- Scegliere il protocollo più adeguato per uno specifico canale dati
- Scegliere il codec più adeguato per uno specifico canale dati
- Dimensionare il numero di canali richiesti
- Calcolare la larghezza di banda necessaria

## Vantaggi del VoIP

Perché dovresti interessarti al VoIP? Il VoIP offre vantaggi sia alle aziende che ai privati. La riduzione dei costi è certamente uno di questi, ma in alcuni ambienti il VoIP semplifica l'integrazione dei sistemi informatici. Alcuni dei vantaggi sono descritti qui di seguito:

### Convergenza

Il vantaggio principale del VoIP è la combinazione delle reti dati e voce per ridurre i costi (convergenza). Tuttavia, analizzare solo i costi al minuto della voce potrebbe non essere sufficiente per giustificare l'adozione del VoIP. Il prezzo dei minuti venduto dalle compagnie telefoniche sta diventando rapidamente più economico ed è un aspetto da considerare prima di adottare il VoIP.

### Costi di infrastruttura

L'uso di un'unica infrastruttura di rete riduce i costi associati ad aggiunte, rimozioni e modifiche. Poiché l'IP è diventato pervasivo, ha portato la tecnologia legata al VoIP su diversi nuovi dispositivi, come telefoni cellulari, PDA, sistemi embedded e laptop.

### Standard aperti

Infine, gli standard aperti su cui è costruito il VoIP offrono la libertà di scegliere tra diversi fornitori. Questo singolo vantaggio rende il cliente il re, invece di un subordinato delle TELCO e dei produttori di PBX.

### Computer Telephony Integration

La telefonia è molto più antica dell'informatica. I PBX telefonici si basano sulla commutazione di circuito e solitamente non si dispone di più di un computer per la supervisione. Con il VoIP, la telefonia è creata fin dalle fondamenta basandosi sugli standard informatici. Questo rende l'uso delle applicazioni di Computer Telephony più economico e facile rispetto al vecchio modello. Puoi creare rapidamente una lunga lista di applicazioni di telefonia basate su Asterisk. Puoi sviluppare IVR, ACD, CTI, dialer, popup su schermo e altre applicazioni in una frazione del tempo richiesto per i PBX tradizionali.

## Architettura VoIP di Asterisk

L'architettura di Asterisk è mostrata di seguito. Asterisk tratta tutti i protocolli VoIP come canali. Puoi utilizzare qualsiasi codec o qualsiasi protocollo. Il concetto da imparare qui è che Asterisk mette in comunicazione qualsiasi tipo di canale con qualsiasi altro. Pertanto, è possibile tradurre protocolli di segnalazione come SIP e IAX l'uno nell'altro e persino con codec diversi. Ad esempio, puoi tradurre una chiamata da un telefono SIP nella rete locale utilizzando il codec G.711 verso un trunk SIP verso il tuo provider VoIP utilizzando il codec G.729. Nei prossimi capitoli, spiegheremo i dettagli dell'architettura SIP e IAX. Il supporto H.323 (tramite l'add-on chan_ooh323) è disponibile ma sempre più raro; SIP/PJSIP è lo standard per le implementazioni moderne.

![Architettura modulare di Asterisk: le applicazioni e i canali si collegano al core dello switch PBX tramite API, con moduli di traduzione codec e formati di file caricati dinamicamente.](../images/06-voip-network-fig01.png)

## Protocolli VoIP e stack di rete

Il VoIP utilizza un insieme di protocolli diversi che lavorano insieme. È allettante allinearli al modello di riferimento OSI a sette livelli, e molti diagrammi più vecchi fanno esattamente questo: posizionano SIP e H.323 al livello "sessione" e i codec al livello "presentazione". Tale mappatura è sempre stata controversa. L'IETF, che standardizza SIP, non utilizza il modello OSI; segue il più vecchio modello TCP/IP (DoD) a quattro livelli, e RFC 3261 definisce **SIP come un protocollo a livello applicazione**. I media seguono lo stesso schema: RTP e i codec risiedono nel payload dell'applicazione, trasportati su UDP al livello di trasporto. La tabella sottostante mappa i principali protocolli VoIP sul modello TCP/IP che l'IETF utilizza effettivamente, con l'equivalente OSI approssimativo mostrato solo per riferimento.

| Livello TCP/IP (IETF) | Protocolli | Equivalente OSI approssimativo |
|---|---|---|
| Applicazione | SIP, H.323, MGCP, segnalazione IAX2; RTP/RTCP; codec (G.711, G.729, Opus…) | Applicazione / Presentazione / Sessione |
| Trasporto | UDP, TCP | Trasporto |
| Internet | IP (con QoS come DiffServ) | Rete |
| Collegamento | Ethernet, PPP, Frame Relay… | Data link / Fisico |

I meccanismi di QoS come DiffServ operano a livello IP per dare priorità ai pacchetti vocali e migliorare la qualità delle chiamate. Alcune specifiche dei protocolli:

- **SIP** utilizza UDP o TCP sulla porta 5060 (TLS sulla 5061) per trasportare la segnalazione. L'audio è trasportato separatamente da RTP su un intervallo di porte UDP configurabile (il campione `rtp.conf` fornito con Asterisk utilizza da 10000 a 20000), codificato con un codec come G.711.
- **H.323** trasporta la segnalazione di chiamata su TCP (segnalazione di chiamata H.225 sulla porta 1720), mentre il canale RAS H.225 utilizza UDP sulla porta 1719; RTP trasporta l'audio.
- **IAX2** è insolito: multiplexa sia la segnalazione che i media su un'unica porta UDP (4569), il che semplifica l'attraversamento di NAT e firewall.

> **[Nota della 2ª ed.]** La figura della 1ª edizione qui mappava SIP/H.323 sul livello *sessione* OSI e i codec sul livello *presentazione*. Tale mappatura è stata a lungo fonte di controversie — l'IETF utilizza il modello TCP/IP, in cui SIP è un protocollo a livello applicazione — quindi la figura è stata sostituita dalla tabella sopra. Commissionare una figura ridisegnata basata sullo stack TCP/IP se si desidera una rappresentazione visiva.

## Come scegliere un protocollo

Dati i numerosi protocolli, come puoi scegliere quello migliore per la tua rete? In questa sezione, evidenzieremo i vantaggi e gli svantaggi di ciascun protocollo.

### SIP - Session Initiated Protocol

SIP è uno standard aperto dell'Internet Engineering Task Force (IETF), ampiamente definito nella RFC 3261. La maggior parte dei moderni provider VoIP utilizza SIP; infatti, sta diventando lo standard VoIP più popolare. Il punto di forza di SIP è che si tratta di uno standard basato su IETF. SIP è leggero se confrontato con il più vecchio H.323. Il punto debole principale di SIP è l'attraversamento NAT, una sfida per la maggior parte dei provider VoIP SIP. L'IETF non ha creato SIP pensando alla fatturazione, ma per comunicazioni aperte tra peer. La fatturazione è solitamente una preoccupazione per i provider VoIP.

### IAX – Inter Asterisk eXchange

IAX è un protocollo aperto originariamente sviluppato da Digium (ora Sangoma). IAX è un protocollo tutto-in-uno poiché trasporta segnalazione e media attraverso la stessa porta UDP (4569). Mark Spencer ha sviluppato IAX come protocollo binario per una larghezza di banda ridotta. Il principale punto di forza di IAX è il suo ridotto utilizzo di larghezza di banda (non utilizza RTP); è anche molto facile per l'attraversamento di NAT e firewall poiché utilizza solo una porta UDP (4569). Se un produttore di PBX tradizionale avesse creato IAX, probabilmente avrebbe commercializzato il protocollo come "la cosa migliore dopo il gelato"; in alcune situazioni, IAX in modalità trunk può ridurre l'utilizzo della larghezza di banda vocale di un terzo. IAX2 (versione 2) è ancora presente in Asterisk 22 tramite il modulo `chan_iax2` e rimane utile per i trunk Asterisk-to-Asterisk, sebbene sia considerato legacy; SIP/PJSIP è preferito per le nuove implementazioni. IAX2 è specificato nella [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informativa).

### MGCP – Media Gateway Control Protocol

MGCP è un protocollo utilizzato insieme a H.323, SIP e IAX. Il suo più grande vantaggio è la scalabilità. È configurato nell'agente di chiamata invece che nei gateway. Questo semplifica il processo di configurazione e consente una gestione centralizzata. Tuttavia, l'implementazione in Asterisk non è completa e sembra che non molte persone lo utilizzino.

### H.323

H.323 è ampiamente utilizzato nel VoIP. È uno dei primi protocolli VoIP ed è essenziale per collegare infrastrutture VoIP più vecchie basate su gateway. H.323 è ancora lo standard nel mercato dei gateway, sebbene il mercato stia lentamente migrando verso SIP. I punti di forza di H.323 includono l'ampia adozione sul mercato e la maturità. I punti deboli di H.323 sono legati alla complessità dell'implementazione e ai costi associati agli organismi di standardizzazione.

### Tabella di confronto dei protocolli

La seguente tabella riassume le differenze tra i protocolli di sessione.

| Protocollo | Organismo di standardizzazione | Utilizzato per |
|----------|---------------|----------|
| SIP | Standard IETF | Telefoni SIP; connessione a provider di servizi SIP |
| IAX2 | RFC 5456 (Informativa) | Trunk Asterisk-to-Asterisk; telefoni IAX2; provider di servizi IAX |
| H.323 | Standard ITU | Telefoni e gateway H.323 (può utilizzare un gatekeeper esterno, non può esserlo) |
| MGCP | IETF/ITU | Telefoni MGCP (nessun supporto provider/gateway) |
| SCCP | Proprietario Cisco | Telefoni Cisco |

> **[Nota della 2ª ed.]** Considerare l'aggiornamento di questa tabella per riflettere i nomi dei moduli attuali di Asterisk 22 e lo stato del supporto.

## Un endpoint per dispositivo

In Asterisk 22, lo stack PJSIP modella ogni telefono, trunk o gateway come un singolo oggetto **endpoint** in `pjsip.conf`. Un endpoint effettua e riceve chiamate; le sue credenziali risiedono in un oggetto `auth`, il suo indirizzo registrato in un `aor` e il suo percorso di rete in un `transport`. Si configura un endpoint per dispositivo e si collegano i pezzi necessari: non c'è un ruolo separato "user" contro "peer" su cui ragionare. (Il modello a oggetti completo è trattato in *SIP e PJSIP*.)

## Codec e traduzione dei codec

Utilizzerai un codec per convertire la voce da un'onda analogica a un segnale digitale. I codec differiscono l'uno dall'altro per aspetti come la qualità del suono, il tasso di compressione, la larghezza di banda e i requisiti di calcolo. Servizi, telefoni e gateway solitamente supportano diversi di questi aspetti. Il codec G.729 è molto popolare. Non fa parte della build standard di Asterisk 22; viene invece fornito come modulo add-on esterno (`codec_g729`) che scarichi da Digium (ora Sangoma). Il sorgente `menuselect` di Asterisk lo elenca con `support_level=external` e nota chiaramente: "Scarica il codec g729a da Digium. Deve essere acquistata una licenza per questo codec." In altre parole, l'uso legale di G.729 richiede una licenza acquistata per canale. (Esiste anche un'alternativa open-source, `bcg729`.)

![Pulse Code Modulation (PCM): un segnale analogico a 4000 Hz viene campionato 8000 volte al secondo (teorema di Nyquist) e codificato in un flusso di bit digitale a 64 Kbps.](../images/06-voip-network-fig04.png)

Asterisk 22 supporta i seguenti codec (tra gli altri):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — qualità PSTN standard; ulaw comune in Nord America, alaw comune in Europa e America Latina
- ITU G.722: 64 Kbps — banda larga (voce HD), buona qualità alla stessa larghezza di banda del G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — modulo binario esterno `codec_g729` scaricato da Digium/Sangoma (`support_level=external`; deve essere acquistata una licenza per utilizzarlo)
- Speex: da 2.15 a 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variabile — moderno codec a banda larga/banda intera; eccellente qualità e resilienza alla perdita di pacchetti; fornito come modulo binario esterno `codec_opus` scaricato da Digium/Sangoma (`support_level=external`; nessun acquisto di licenza indicato, a differenza di G.729); raccomandato per WebRTC e endpoint SIP moderni. (Esistono alternative di build open-source su GitHub.)

Inoltre, Asterisk consente la traduzione tra codec. In alcuni casi, ciò non è possibile, come nel caso di g723, che è supportato solo in modalità pass-thru. La traduzione da un codec all'altro consuma molte risorse della CPU. Pertanto, evita tutto ciò quando possibile.

## Come scegliere un Codec

La selezione del codec dipende da diverse opzioni, come:

- Qualità del suono
- Costi di licenza
- Consumo di elaborazione CPU
- Requisiti di larghezza di banda
- Occultamento della perdita di pacchetti
- Disponibilità per Asterisk e dispositivi telefonici

La seguente tabella confronta i codec più popolari. La qualità di questi codec è considerata "toll"—in altre parole, simile alla PSTN.

| Codec | G.711 | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|
| Intervallo di campionamento | 20 ms | 30 ms | 30 ms | RTE/LTP |
| Larghezza di banda (Kbps) | 64 | 8 | 13.33 | 13 |
| Costo (per canale) | Gratuito | ~USD 10.00 | Gratuito | Gratuito |
| Resistenza alla cancellazione di frame¹ | Nessuna | 3% | 5% | 3% |
| Complessità (MIPS)² | ~0.35 | ~13 | ~18 | ~5 |

¹ La resistenza alla perdita di pacchetti si riferisce al tasso a cui il MOS scende a circa 0.5 al di sotto della qualità di picco per lo specifico codec.

² La complessità si riferisce alla quantità, in milioni di istruzioni al secondo, spesa per codificare e decodificare il codec utilizzando un design di riferimento su un DSP Texas Instruments (TMS320C54x). Esiste una relazione diretta tra la frequenza del processore e i MIPS, ma non è possibile tracciare una relazione precisa tra piattaforme hardware così diverse. Usa questa tabella solo per confronto.

> **[Nota della 2ª ed.]** Ricostruire questa tabella di confronto per la 2ª edizione: aggiungere Opus (gratuito `codec_opus`) e G.722 (banda larga, 64 Kbps); mantenere G.711 ulaw/alaw come baseline PSTN. Per G.729, notare la realtà delle licenze: il modulo `codec_g729` di Sangoma è scaricabile gratuitamente ma richiede una licenza per canale; l'open-source `bcg729` è un'alternativa.

**Raccomandazioni sui codec per Asterisk 22:**

- **G.711 (ulaw/alaw):** Utilizzare per trunk PSTN e massima interoperabilità; costo di transcodifica zero all'interno di Asterisk.
- **G.729:** Utile per trunk WAN a bassa larghezza di banda; il modulo `codec_g729` di Sangoma è scaricabile gratuitamente ma richiede una licenza acquistata per canale per l'uso.
- **G.722:** Buona scelta per banda larga (voce HD) su LAN/estensioni interne; stessa larghezza di banda del G.711 con qualità migliore.
- **Opus:** Raccomandato per endpoint moderni, client WebRTC e qualsiasi implementazione in cui l'endpoint lo supporti. Bitrate adattivo, eccellente resilienza alla perdita di pacchetti, liberamente disponibile tramite il modulo binario `codec_opus` di Sangoma.

## Overhead causato dagli header di protocollo

Nonostante il fatto che i codec facciano scarso uso di larghezza di banda, dobbiamo considerare l'overhead causato dagli header di protocollo come Ethernet, IP, UDP e RTP. Come tale, potremmo dire che la larghezza di banda dipende dagli header utilizzati. Se siamo in una rete Ethernet, il requisito di larghezza di banda è superiore rispetto a una rete PPP perché l'header PPP è più corto di quello Ethernet. Diamo un'occhiata ad alcuni esempi: Destinazione Ethernet G.729 codificato (20) Header UDP (8) Tipo Ethernet (2) Sorgente Ethernet Header IP (20) Header RTP (12) Payload Voce Checksum (4) Indirizzo (6) Indirizzo (6) Ethernet Codec g.711 (64 Kbps)

![Un singolo pacchetto vocale g.729 su Ethernet: 20 byte di payload avvolti in 58 byte di header Ethernet, IP, UDP e RTP — una conversazione g.729 consuma 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

Puoi facilmente calcolare altri requisiti di larghezza di banda utilizzando un calcolatore di larghezza di banda VoIP online come <https://www.voip.school/bandcalc/bandcalc.php>.


## Ingegneria del traffico

Un problema principale nella progettazione delle reti VoIP è il dimensionamento del numero di linee e della larghezza di banda richiesta verso una destinazione specifica, come una sede remota o un provider di servizi. È anche importante dimensionare il numero di chiamate simultanee di Asterisk (parametro principale per il dimensionamento di Asterisk).

### Semplificazioni

La semplificazione primaria e più utilizzata è stimare il numero di chiamate per tipo di utente. Ad esempio:

- PBX aziendali (una chiamata simultanea ogni cinque estensioni)
- Utenti residenziali (una chiamata simultanea ogni sedici utenti)

Esempio n. 1 La sede centrale dell'azienda ha 120 estensioni e due filiali: la prima con 30 estensioni e la seconda con 15 estensioni. Il nostro obiettivo è dimensionare il numero di trunk E1 nella sede centrale e la larghezza di banda richiesta per la rete Frame-Relay.

![Topologia di rete di esempio (stessa città): la sede centrale con 120 estensioni si collega alla PSTN su linee T1, e alla filiale n. 1 (30 estensioni) e alla filiale n. 2 (15 estensioni) su un cloud Frame-Relay.](../images/06-voip-network-fig06.png)

1a Numero di linee T1

- Numero totale di estensioni che utilizzano linee T1: 120+30+15=165 linee
- Utilizzando un trunk ogni cinque estensioni per uso aziendale
- Numero totale di linee = 33 o circa 2xT1 linee

1b Requisiti di larghezza di banda Scegliamo il codec g.729 a causa dei requisiti di larghezza di banda, della qualità del suono e del consumo medio della CPU.

Con un trunk ogni cinque estensioni:

- Larghezza di banda richiesta per la filiale n. 1 (Frame-relay): 26.8*6=160.8 Kbps
- Larghezza di banda richiesta per la filiale n. 2 (Frame-relay): 26.8*3= 80.4 Kbps

### Metodo Erlang B

1.a Numero di chiamate VoIP simultanee A volte, la semplificazione non è l'approccio migliore. Quando si dispone di dati precedenti, è possibile adottare un approccio più scientifico. Utilizzeremo il lavoro di Agner Karup Erlang (Copenhagen Telephone Company, 1909), che ha sviluppato una formula per calcolare le linee in un gruppo di trunk tra due città. Erlang è un'unità di misura del traffico solitamente presente nelle telecomunicazioni. Viene utilizzata per descrivere il volume di traffico per un'ora. Ad esempio: 20 chiamate si verificano in un'ora, con una media di 5 minuti di conversazione ciascuna. Puoi calcolare il numero di Erlang come mostrato di seguito: Minuti di traffico nell'ora: 20 x 5 = 100 minuti Ora di traffico all'interno di un'ora: 100/60 = 1.66 Erlang. Puoi determinare queste misure da un registro chiamate e utilizzarlo per progettare la tua rete per calcolare il numero di linee richieste. Una volta noto il numero di linee, è possibile calcolare i requisiti di larghezza di banda. Erlang B è il metodo più comunemente utilizzato per calcolare il numero di linee in un gruppo di trunk. Presuppone che le chiamate arrivino casualmente (distribuzione di Poisson) mentre le chiamate bloccate vengono immediatamente eliminate. Questo metodo richiede di conoscere il traffico nell'ora di punta (BHT), che puoi ottenere da un registro chiamate o tramite la seguente semplificazione: BHT=17% dei minuti di chiamata di un giorno.

![Risultati del calcolatore Erlang B: 5 Erlang con blocco all'1% richiedono 11 linee (sede centrale verso filiale n. 1), e 2.83 Erlang con blocco all'1% richiedono 8 linee (sede centrale verso filiale n. 2).](../images/06-voip-network-fig07.png)

Un'altra variabile importante è il Grade of Service (GoS), che definisce la probabilità di bloccare le chiamate per carenza di linee. Puoi arbitrare questo parametro, che solitamente è 0.05 (5% chiamate perse) o 0.01 (1% chiamate perse). Esempio n. 1: Utilizzando lo stesso esempio del 5.10.1, ti forniremo alcuni dati sui modelli di traffico. Dal registro chiamate, abbiamo scoperto questi dati: Dati dal registro chiamate (Minuti di chiamata e BHT):

- Sede centrale verso Filiale n. 1 = 2.000 minuti, BHT = 300 minuti
- Sede centrale verso Filiale n. 2 = 1.000 minuti, BHT = 170 minuti
- Filiale n. 1 verso Filiale n. 2 = 0, BHT=0

Arbitriamo GoS=0.01

- Sede centrale verso Filiale n. 1 - BHT=300 minuti/60 = 5 Erlang
- Sede centrale verso Filiale n. 2 – BHT=170 minuti/60 = 2.83 Erlang

Utilizzando un calcolatore Erlang come <https://www.erlang.com>

- Per la Sede centrale verso la Filiale n. 1, sono richieste 11 linee.
- Per la Sede centrale verso la Filiale n. 2, sono richieste 8 linee.

1.b Larghezza di banda richiesta Stiamo utilizzando una WAN dove la perdita di pacchetti è rara. Sceglieremo il codec g729 a causa della sua buona qualità del suono e della compressione dati (8 Kbps).

Codec selezionato: g729 Livello Datalink: Frame-Relay

- Larghezza di banda vocale stimata per la Filiale n. 1: 26.8x11 = 294.8 Kbps
- Larghezza di banda vocale stimata per la Filiale n. 2: 26.8x8 = 214.40 Kbps

## Riduzione della larghezza di banda richiesta per il VoIP

Tre metodi possono essere utilizzati per ridurre la larghezza di banda richiesta per le chiamate VoIP:

- Compressione dell'header RTP
- IAX Trunked
- Payload VoIP

### Compressione dell'header RTP

Nelle reti Frame-Relay e PPP, è possibile utilizzare la compressione dell'header RTP. La compressione dell'header RTP è stata definita nella RFC 2508. È uno standard IETF disponibile in diversi router. Tuttavia, fai attenzione, poiché alcuni router richiedono un set di funzionalità diverso affinché questa risorsa sia disponibile. L'impatto dell'utilizzo della compressione dell'header RTP è favoloso poiché riduce la larghezza di banda richiesta nel nostro esempio da 26.8 Kbps per conversazione vocale a 11.2 Kbps: una riduzione del 58.2%!

### Modalità trunk IAX2

Se stai collegando due server Asterisk, puoi utilizzare il protocollo IAX2 in modalità trunk. Questa tecnologia rivoluzionaria non necessita di router speciali e può essere applicata a qualsiasi tipo di collegamento dati.

![Modalità trunk IAX2 su Ethernet: una singola chiamata g.729 necessita del suo intero stack di header (31.2 Kbps), ma una seconda chiamata condivide quegli header e aggiunge solo un piccolo miniframe IAX2, con una media di circa 9.6 Kbps di larghezza di banda extra per chiamata aggiuntiva.](../images/06-voip-network-fig08.png)

La modalità trunk IAX2 riutilizza gli stessi header dalla seconda chiamata in poi. Utilizzando g729 in un collegamento PPP, la prima chiamata consumerà 30 Kbps di larghezza di banda, mentre la seconda chiamata utilizzerà lo stesso header della prima e ridurrà la larghezza di banda necessaria per la chiamata aggiuntiva a 9.6 Kbps. Possiamo calcolare la larghezza di banda richiesta in modalità trunk come segue: Filiale n. 1 (11 chiamate) Larghezza di banda = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps Filiale n. 2 (8 chiamate) Larghezza di banda = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps La prima chiamata utilizza 31.2 Kbps, la successiva 9.6, e così via.

### Aumento del payload vocale

Questo metodo è molto comune quando si utilizzano gateway VoIP su Internet. Quando si utilizza un payload più grande, si sacrificherà la latenza a favore di una larghezza di banda ridotta. Puoi modificare la pacchettizzazione RTP aggiungendo la dimensione del frame al codec nell'istruzione allow.

![Aumento del payload vocale: impacchettare 60 byte di payload g.729 in un pacchetto (invece di 20) ammortizza i 58 byte di header su più voce, riducendo la larghezza di banda a circa 16.05 Kbps per chiamata al costo di una maggiore latenza.](../images/06-voip-network-fig09.png)

Esempio:

```
allow=ulaw:30
```

I valori permessi sono: Nome Min Max Default Incremento g723 gsm ulaw alaw g726 ADPCM SLIN lpc10 g729 speex ilbc

## Riepilogo

In questo capitolo, hai imparato che Asterisk tratta il VoIP utilizzando i canali. Supporta SIP (tramite `chan_pjsip` in Asterisk 22) e IAX2; H.323 è disponibile solo tramite l'add-on della community `ooh323`, e i più vecchi canali MGCP e SCCP (Skinny) non fanno più parte di una build standard di Asterisk 22. Hai confrontato e imparato come scegliere un protocollo di segnalazione e un codec per i canali VoIP. IAX2 è più efficiente in termini di larghezza di banda e può attraversare facilmente il NAT. SIP/PJSIP è il protocollo più supportato dai fornitori di telefoni e gateway di terze parti ed è l'unico driver di canale SIP in Asterisk 22. Il protocollo H.323 è il più vecchio e dovrebbe essere utilizzato per connettersi a infrastrutture VoIP legacy. Nella sezione 5.11, abbiamo imparato come progettare e dimensionare una rete VoIP.

## Quiz

1. Quali dei seguenti sono vantaggi del VoIP descritti in questo capitolo (seleziona tutto ciò che si applica)?
   - A. Convergenza delle reti dati e voce per ridurre i costi
   - B. Minori costi di infrastruttura per aggiunte, rimozioni e modifiche
   - C. Standard aperti che ti liberano da un singolo fornitore
   - D. Integrazione Computer Telephony più facile ed economica
   - E. Tariffe di chiamata al minuto garantite più basse di qualsiasi compagnia telefonica
2. La convergenza è l'integrazione di voce, dati e video in un'unica rete; il suo vantaggio principale è la riduzione dei costi nell'implementazione e nella manutenzione di reti separate.
   - A. Falso
   - B. Vero
3. Asterisk tratta ogni protocollo VoIP come un canale e può mettere in comunicazione qualsiasi tipo di canale con qualsiasi altro, transcodificando tra codec quando necessario.
   - A. Falso
   - B. Vero
4. In Asterisk 22, SIP è gestito da quale driver di canale?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. Nel modello TCP/IP (IETF) rispetto al quale SIP è effettivamente definito nella RFC 3261, i protocolli di segnalazione SIP, H.323 e IAX2 operano al livello ___.
   - A. Presentazione
   - B. Applicazione
   - C. Fisico
   - D. Sessione
   - E. Data link
6. SIP è il protocollo più adottato per i telefoni IP ed è uno standard aperto ampiamente definito dall'IETF nella RFC 3261.
   - A. Falso
   - B. Vero
7. IAX2 trasporta sia la segnalazione che i media su un'unica porta UDP, il che lo rende efficiente e facile per attraversare il NAT. Quale porta UDP utilizza IAX2?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX è stato originariamente sviluppato da Digium (ora Sangoma). Nonostante la limitata adozione da parte dei fornitori di telefonia, IAX è eccellente quando hai bisogno di (seleziona tutto ciò che si applica):
   - A. Ridurre l'utilizzo della larghezza di banda (non utilizza RTP)
   - B. Un formato media video
   - C. Facile attraversamento di NAT e firewall
   - D. Modalità trunk per combinare molte chiamate Asterisk-to-Asterisk e ammortizzare l'overhead degli header
9. In Asterisk 22, un dispositivo è configurato come un singolo oggetto PJSIP `endpoint` che effettua e riceve chiamate: non esiste un ruolo separato "user" o "peer".
   - A. Falso
   - B. Vero
10. Per quanto riguarda i codec in Asterisk 22, seleziona tutte le affermazioni vere:
    - A. G.711 è equivalente a PCM e utilizza 64 Kbps di larghezza di banda.
    - B. Il modulo codec_g729 di Sangoma è scaricabile gratuitamente, ma l'uso legale richiede una licenza acquistata per canale.
    - C. GSM è popolare perché utilizza circa 13 Kbps e non necessita di licenza.
    - D. G.711 u-law è comune in Nord America, mentre a-law è comune in Europa e America Latina.
    - E. G.729 è leggero e utilizza pochissime risorse CPU per codificare e decodificare rispetto a G.711.

**Risposte:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Applicazione — SIP è un protocollo a livello applicazione nel modello TCP/IP utilizzato dall'IETF) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
