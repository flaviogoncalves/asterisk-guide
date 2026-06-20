# Introduzione ad Asterisk PBX

La popolarità delle distribuzioni pronte all'uso come FreePBX e Issabel è cresciuta recentemente. In questo libro, tratteremo il classico Asterisk, che è la base per comprendere queste distribuzioni. Asterisk PBX è un software open-source capace di trasformare un PC ordinario in un potente PBX multiprotocollo. In questo capitolo, impareremo le possibilità di questa nuova tecnologia e la sua architettura di base.

## Obiettivi

Al termine di questo capitolo dovresti essere in grado di:

- Spiegare cos'è Asterisk e cosa fa;
- Descrivere il ruolo di Digium™ e del suo successore Sangoma;
- Riconoscere l'architettura di base di Asterisk e i suoi componenti;
- Evidenziare diversi scenari d'uso; e
- Identificare le fonti di informazione e di supporto.

## What is Asterisk

Asterisk è un software PBX open-source che trasforma un normale computer in un PBX completo per utenti domestici, imprese, fornitori di servizi VoIP e compagnie telefoniche. Asterisk è anche sia una community open-source sia un progetto sponsorizzato da Sangoma Technologies (che ha acquisito Digium nel 2018). Sei libero di usare e modificare Asterisk per soddisfare le tue esigenze. Asterisk consente la connettività in tempo reale tra reti PSTN e VoIP. Poiché Asterisk è molto più di un PBX, non solo ottieni un aggiornamento eccezionale al tuo PBX esistente, ma puoi anche fare cose nuove nella telefonia, come:

- Collegare i dipendenti che lavorano da casa a un PBX d'ufficio tramite Internet a banda larga;
- Collegare più uffici in luoghi diversi tramite una rete IP, rete privata o anche attraverso Internet stesso;
- Fornire ai dipendenti una segreteria telefonica integrata con il web e l'e‑mail;
- Creare applicazioni come IVR che consentono connessioni al tuo sistema di ordinazione o ad altre applicazioni;
- Dare agli utenti in viaggio l'accesso al PBX aziendale da qualsiasi luogo con una semplice connessione a banda larga o VPN; e
- molto altro....

Asterisk include diverse risorse avanzate precedentemente disponibili solo in sistemi di fascia alta, come:

- Musica per i clienti in attesa in coda, con supporto per streaming multimediale e file MP3;
- Code di chiamata, in cui un team di operatori può rispondere alle chiamate e monitorare le code;
- Integrazione con sintesi vocale e riconoscimento vocale;
- Registri dettagliati trasferiti sia in file di testo sia in database SQL; e
- Connettività PSTN tramite linee digitali e analogiche.

## Che cos'è AsteriskNOW (Storico) e FreePBX

Asterisk nella sua forma più pura, noto anche come “classic asterisk” (denominazione del pacchetto Debian), è considerato più uno strumento di sviluppo che un prodotto finito di per sé. AsteriskNOW è stata un'iniziativa per trasformare Asterisk in un soft‑appliance. La distribuzione includeva CentOS come sistema operativo e FreePBX come interfaccia grafica. AsteriskNOW è stato interrotto.

Oggi, la distribuzione chiavi‑in‑mano standard di Asterisk è **FreePBX** (mantenuta da Sangoma), che raggruppa Asterisk con una GUI di amministrazione web‑based e un ecosistema di moduli. FreePBX è rilasciato sotto licenza GPL e può essere scaricato gratuitamente da www.freepbx.org. Per le implementazioni commerciali, Sangoma offre anche **FreePBX Distro** (un'immagine Linux completa) e il suo prodotto commerciale **PBXact**.

## Ruolo di Digium™ e Sangoma

Digium, un'azienda situata a Huntsville, Alabama, è stata il creatore e lo sviluppatore principale di Asterisk sin dalla sua fondazione nel 1999. Oltre a essere lo sponsor principale dello sviluppo di Asterisk, Digium produceva schede di interfaccia telefonica e altro hardware per i PBX Asterisk, e creava prodotti commerciali come Switchvox (destinato al mercato SMB). Nel 2018, Digium è stata acquisita da **Sangoma Technologies**, una società canadese di comunicazioni unificate. Dall'acquisizione, Sangoma ha continuato a sponsorizzare lo sviluppo di Asterisk e ne è il principale custode, mantenendo il progetto open‑source su www.asterisk.org.

Storicamente, Digium offriva Asterisk sotto tre tipi di accordi di licenza:

- General Public License (GPL) Asterisk. Questa è la versione più utilizzata. Include tutte le funzionalità ed è libera da usare e modificare secondo i termini della licenza GPL.
- Asterisk Business Edition era una versione commerciale di Asterisk. Alcune aziende usavano l'edition business perché non volevano o non potevano utilizzare la licenza GPL—di solito perché non desideravano rilasciare il proprio codice sorgente insieme ad Asterisk. **Nota:** Asterisk Business Edition è stata interrotta; oggi Asterisk è distribuito esclusivamente sotto GPL.
- Licenza Asterisk OEM. Dopo che Digium ha smesso di vendere Asterisk Business Edition al dettaglio, ha continuato a concedere in licenza quella versione commerciale ai clienti OEM — fornitori di apparecchiature che volevano costruire prodotti proprietari sopra Asterisk senza rilasciare il proprio codice sorgente sotto GPL.

### Il progetto Zapata e il suo rapporto con Asterisk

Il progetto Zapata è stato sviluppato da Jim Dixon, che è stato anche responsabile del rivoluzionario design hardware utilizzato con Asterisk. L'hardware è anch'esso open‑source; in quanto tale, può essere usato da qualsiasi azienda, e oggi diversi produttori realizzano schede compatibili con questa architettura.

Il progetto Zapata ha prodotto un'architettura chiamata Zaptel, successivamente rinominata DAHDI (Digium/Asterisk Hardware Device Interface). Uno dei principali vantaggi di questa architettura è la possibilità di utilizzare la CPU del PC per elaborare lo streaming multimediale, la cancellazione dell'eco e la transcodifica. Al contrario, la maggior parte delle schede esistenti utilizza processori di segnale digitale (DSP) per svolgere queste attività. L'uso della CPU del PC invece dei DSP dedicati riduce drasticamente il prezzo della scheda. Pertanto, queste schede sono significativamente più economiche rispetto alle interfacce precedentemente disponibili di altri produttori. D'altro canto, queste schede richiedono molta CPU; un uso improprio della CPU del PC può influire notevolmente sulla qualità della voce. Recentemente, Digium ha lanciato una scheda coprocessore che utilizza DSP per codificare e decodificare G.729 e G.723, consentendo una migliore scalabilità per un gran numero di canali.

## Why Asterisk?

Ricordo il mio primo contatto con Asterisk. Di solito, la prima reazione a qualcosa di nuovo—soprattutto a qualcosa che compete con ciò che già conosci—è rifiutarlo! È esattamente quello che è successo nel 2003. Asterisk era in competizione con una soluzione che stavo vendendo a un cliente (4 E1 VoIP Gateway), ed era dieci volte meno costosa di quella che stavo addebitando per la soluzione che già conoscevo. Questo prezzo sproporzionato mi ha spinto a studiare Asterisk per identificare potenziali insidie e svantaggi. Per esempio, ho scoperto che la CPU del PC a quel tempo non avrebbe supportato 120 sezioni simultanee g.729; alla fine, ho vinto la proposta con la mia soluzione Gateway.

Tuttavia, questo esercizio mi ha portato alla scoperta che Asterisk poteva risolvere una varietà di problemi molto costosi per la mia base di clienti. Avevamo difficoltà con preventivi costosi per IVR, messaggistica unificata, registrazione delle chiamate e dialer; con un dimensionamento appropriato, i problemi di CPU potevano essere aggirati. Infatti, in soli tre anni Asterisk è diventato il prodotto di punta della mia azienda (ho persino deciso di aprire un'altra società solo per il business Asterisk). A mio avviso, Asterisk è una rivoluzione nelle telecomunicazioni che rappresenta per la telefonia IP ciò che Apache rappresenta per i servizi web.

### Extreme cost reduction

Se confronti una PBX tradizionale con Asterisk per quanto riguarda le interfacce digitali e i telefoni, Asterisk è leggermente più economico di quelle PBX. Tuttavia, Asterisk rende davvero conveniente l’aggiunta di funzionalità avanzate come voicemail, ACD, IVR e CTI. Con queste funzionalità avanzate, Asterisk diventa significativamente meno costoso delle PBX tradizionali. Infatti, confrontare le PBX Asterisk con PBX analogiche di fascia bassa è ingiusto perché Asterisk offre molte più funzionalità non disponibili nei sistemi analogici di fascia bassa.

### Telephony system control and independence

Uno dei benefici più citati dai clienti di Asterisk è l’indipendenza che fornisce. Alcuni dei produttori odierni non forniscono nemmeno al cliente la password del sistema o la documentazione di configurazione. Con l’approccio “fai-da-te” di Asterisk, l’utente ottiene totale libertà; in più, l’utente ha accesso a un’interfaccia standard.

### Easy and rapid development environment

Asterisk può essere esteso usando linguaggi di scripting come PHP e Perl con le interfacce AMI e AGI. Asterisk è open-source, e il suo codice sorgente può essere modificato dall’utente. Il codice sorgente è scritto principalmente in linguaggio di programmazione ANSI C.

### Feature rich

Asterisk ha diverse funzionalità che sono assenti o opzionali nelle PBX tradizionali (ad es., voicemail, CTI, ACD, IVR, musica di attesa integrata e registrazione). I costi di queste funzionalità in alcune piattaforme superano il prezzo della piattaforma stessa.

### Dynamic content on the phone

Asterisk è programmato usando il linguaggio C e altri linguaggi comuni nell’attuale ambiente di sviluppo. La possibilità di fornire contenuti dinamici è praticamente illimitata.

### Flexible and powerful dial plan

Un altro punto di forza di Asterisk è il suo potente dial plan. Nelle PBX tradizionali, anche funzionalità semplici come il least cost routing (LCR) sono o non fattibili o opzionali. Con Asterisk, scegliere il percorso migliore è facile e pulito.

### Open-source running on top of Linux

Una delle più grandi caratteristiche di Asterisk è la sua community. Sono disponibili diverse risorse, inclusa la documentazione ufficiale di Asterisk (docs.asterisk.org), il wiki VoIP-Info mantenuto dalla community (www.voip-info.org <http://www.voip-info.org>), le mailing list e i forum. Man mano che Asterisk viene adottato sempre di più, i bug vengono trovati e corretti rapidamente. Con una vasta base di utenti e un team di sviluppo attivo, Asterisk è tra le piattaforme PBX più ampiamente testate al mondo, il che aiuta a mantenere il codice stabile e maturo.

### Asterisk architecture limitations

Alcune limitazioni di Asterisk derivano dall

## Obiezioni principali a Asterisk PBX

È comune sentire obiezioni all'adozione di Asterisk, che affronteremo qui.

### La quota di mercato di Asterisk è troppo piccola

La quota di mercato è solitamente misurata dal numero di PBX vendute. Queste statistiche sono generalmente acquisite dai più grandi distributori. Asterisk è software libero che può essere scaricato e distribuito senza che venga registrata alcuna vendita, quindi è sistematicamente sottostimato in quei dati. Anche così, Asterisk alimenta una base installata molto ampia a livello mondiale — da PBX per uffici a server singolo a grandi implementazioni di carrier e contact‑center — e rimane il motore dominante dietro l'ecosistema PBX open‑source (incluse distribuzioni chiavi in mano come FreePBX).

### Se è gratuito, come sopravvive il produttore?

In realtà, non esiste un “produttore” di software open‑source nel senso tradizionale. Digium ha sviluppato Asterisk dal 1999, sostenendosi attraverso la vendita di schede di interfaccia telefonica, prodotti PBX commerciali come Switchvox e software correlato. Nel 2018, Sangoma Technologies ha acquisito Digium. Sangoma continua a finanziare lo sviluppo di Asterisk e genera ricavi tramite prodotti commerciali (moduli commerciali di FreePBX, PBXact, Switchvox), vendite hardware e servizi professionali.

### È difficile trovare supporto tecnico!

Sangoma fornisce supporto tecnico commerciale per Asterisk attraverso il suo ecosistema di partner e direttamente tramite le proprie offerte di prodotto. Una rete globale di professionisti certificati fornisce supporto di primo livello e servizi professionali. Il supporto della community rimane attivo tramite i forum di Asterisk e le mailing list su www.asterisk.org.

### Asterisk supporta più di 200 estensioni?

Sì, assolutamente. Un singolo server Asterisk ben dimensionato può gestire un gran numero di estensioni, e Asterisk scala ulteriormente distribuendo gli utenti su più server con bilanciamento del carico e failover, consentendo grandi implementazioni multi‑sito.

### Solo i “geek” riescono a installare Asterisk

Con FreePBX (disponibile come distro autonoma da Sangoma), anche professionisti con conoscenze limitate di Linux sono in grado di installare e configurare una PBX di media complessità. Con l’aiuto di una GUI, è possibile configurare un’intera PBX in poche ore.

### Cosa succede se il server fallisce?

Uno dei principali vantaggi di Asterisk è la sua capacità di operare in sistemi tolleranti ai guasti. È relativamente semplice ed economico avere due server in esecuzione in parallelo. Ti sfido a provare questo con una PBX convenzionale!

### La nostra azienda non usa software open‑source

Probabilmente la tua azienda utilizza software open‑source senza nemmeno rendersene conto. Molti appliance usano Linux come sistema operativo. Inoltre, supporto commerciale e implementazioni gestite sono disponibili da Sangoma e dalla sua rete di partner certificati.

### Usare la CPU del PC per elaborare segnalazione e media non è consigliato

Asterisk utilizza la CPU del server per elaborare segnalazione e media per i canali vocali invece di avere DSP dedicati. Sebbene ciò consenta una riduzione dei costi fino a cinque volte, rende il sistema dipendente dalle prestazioni della CPU principale. Con il corretto dimensionamento, Asterisk è in grado di gestire grandi volumi. Se desideri comunque liberare la CPU principale da questi compiti, puoi anche usare cancellazione dell’eco hardware e persino schede transcoder, come la Sangoma (ex Digium) TC400B basata su DSP.

## Asterisk Architecture

Questa sezione spiegherà come funziona l'architettura di Asterisk. La figura qui sotto mostra l'architettura di base di Asterisk. Successivamente, spiegheremo i concetti legati all'architettura, inclusi canali, codec e applicazioni.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

Un canale è l'equivalente di una linea telefonica, ma in formato digitale. Di solito consiste in un sistema di segnalazione analogico o digitale (TDM) o in una combinazione di codec e protocollo di segnalazione (ad es., SIP‑GSM, IAX‑uLaw). Inizialmente, tutte le connessioni telefoniche erano analogiche e soggette a eco e rumore. Successivamente, la maggior parte dei sistemi è stata convertita in sistemi digitali, con il suono analogico convertito in formato digitale usando la modulazione a codice di impulsi (PCM) nella maggior parte dei casi. Questo formato consente la trasmissione della voce a 64 kilobit al secondo senza compressione.

Canali che interfacciamo con la Public Switched Telephone Network (PSTN):

- `chan_dahdi`: schede TDM analogiche (FXO/FXS) e digitali (E1/T1/PRI) di Sangoma (ex Digium), Xorcom e altri. Costruite separatamente contro DAHDI — vedere il capitolo *Legacy channels*.

Canali che interfacciamo con Voice over IP:

- `chan_pjsip`: SIP — il driver di canale SIP principale e unico in Asterisk 22 LTS. Stringa di composizione: `PJSIP/endpoint_name`. (**Nota:** il vecchio `chan_sip` è stato rimosso in Asterisk 21 e non esiste in Asterisk 22. Vedere *Building your first PBX with PJSIP* per la configurazione.)
- `chan_iax2`: il protocollo IAX2 — ancora incluso in Asterisk 22 ma legacy; SIP/PJSIP è preferito per nuove implementazioni. Stringa di composizione: `IAX2/peer`.
- `chan_unistim`: telefoni Nortel/Avaya UNISTIM. Ancora disponibili (supporto esteso) ma raramente usati.

I canali VoIP più vecchi non fanno più parte di una build standard di Asterisk 22: `chan_h323` (H.323) sopravvive solo come add‑on della community `ooh323`, e `chan_mgcp` (MGCP) e `chan_skinny` (Cisco SCCP) sono stati deprecati e rimossi dal set di canali moderno. Se è necessario interagire con quei protocolli, un gateway davanti ad Asterisk è l'approccio usuale.

Canali vari:

- **Local**: un pseudo‑canale (integrato nel core) che ritorna al dialplan in un contesto diverso — utile per il routing ricorsivo e per distribuire una chiamata verso più destinazioni. Stringa di composizione: `Local/extension@context`.

### Codec and codec translation

Di solito cerchiamo di mettere quante più connessioni vocali possibile in una rete dati. I codec abilitano nuove funzionalità nella voce digitale, inclusa la compressione, che è una delle caratteristiche più importanti poiché consente rapporti di compressione superiori a 8 a 1. Molti codec definiscono anche funzionalità come il rilevamento dell'attività vocale (soppressione del silenzio), la compensazione della perdita di pacchetti e la generazione di rumore di comfort, sebbene Asterisk stesso non generi rumore di comfort né esegua la soppressione del silenzio. Diversi codec sono disponibili per Asterisk e possono essere tradotti in modo trasparente da uno all'altro. Internamente, Asterisk usa slinear come formato di flusso quando deve convertire da un codec all'altro. Alcuni codec in Asterisk sono supportati solo in modalità pass‑through; questi codec non possono essere tradotti. Per verificare quali codec sono installati nel tuo sistema, puoi usare il comando console:

```
CLI>core show translation
```

The seguenti codec sono supportati:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Solo modalità pass-through
- G.726 - (16/24/32/40kbps)
- G.729 - Modulo codec binario distribuito da Sangoma; il download è gratuito, ma l'uso legale richiede l'acquisto di una licenza per canale (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

Inviare dati da un telefono all'altro dovrebbe essere semplice, a condizione che i dati trovino da soli un percorso verso l'altro telefono. Sfortunatamente, non avviene così, ed è necessario un protocollo di segnalazione per stabilire connessioni tra telefoni, scoprire i dispositivi finali e implementare la segnalazione telefonica. SIP è il protocollo di segnalazione dominante nelle implementazioni moderne ed è l'unico canale SIP disponibile in Asterisk 22 LTS (via chan_pjsip). IAX2 è ancora disponibile ma considerato legacy. Asterisk supporta i seguenti protocolli.

- SIP — via `chan_pjsip`
- IAX2 — legacy, ancora incluso in Asterisk 22
- UNISTIM — telefoni Nortel/Avaya (supporto esteso)
- H.323, MGCP e SCCP (Cisco Skinny) — protocolli legacy non più presenti in una build standard di Asterisk 22 (H.323 solo tramite il componente aggiuntivo della community `ooh323`)

### Applications

Per collegare le chiamate da un telefono all'altro, si utilizza l'applicazione dial(). La maggior parte delle funzionalità di Asterisk (ad esempio voicemail e conferenze) è implementata come applicazioni. È possibile vedere le applicazioni disponibili di Asterisk usando il comando console core show applications.

```
CLI>core show applications
```

Puoi aggiungere applicazioni dagli add‑on di Asterisk, da fornitori terzi, o anche da quelle che sviluppi tu stesso.

## Panoramica di un sistema Asterisk

Asterisk è un PBX open-source che funziona come un PBX ibrido, integrando tecnologie come la telefonia TDM e IP. Asterisk è pronto a implementare funzionalità come l’interactive voice response (IVR) e l’automatic call distribution (ACD); inoltre, come accennato in precedenza, è aperto allo sviluppo di nuove applicazioni. Questa figura mostra come Asterisk si collega al PSTN e ai PBX esistenti utilizzando interfacce analogiche e digitali, oltre a supportare telefoni analogici e IP. Può fungere da soft‑switch, media gateway, voicemail e conferenza audio e dispone anche di musica di attesa integrata.

![Panoramica di un sistema Asterisk](../images/01-introduction-fig02.png)

## Confrontare il vecchio e il nuovo mondo

Nel modello di soft‑switch tradizionale, tutti i componenti venivano venduti separatamente, il che significava che dovevi acquistare ogni componente singolarmente e poi integrarli nell’ambiente PBX o soft‑switch. I costi e i rischi erano elevati e la maggior parte dell’attrezzatura era proprietaria.

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### Telefonia con Asterisk

Tutte le funzioni sono integrate nella piattaforma Asterisk nello stesso o in diversi box a seconda del dimensionamento, e tutte sono licenziate sotto GPL. A volte è più semplice installare Asterisk che licenziare alcuni dei principali IP‑PBX

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## Building a test system

When implementing an Asterisk solution, our first step is generally to build a test system. The goal is a minimal **1×1 PBX** — one phone that can call another — so you can try out endpoints, dialplan, and features before touching production. Today this is entirely software: you do not need any telephony hardware.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### The modern way: a software lab (recommended)

The fastest test system is Asterisk 22 running in a container or virtual machine, with **softphones** for the endpoints and, optionally, a **SIP trunk** to reach the public network:

- **Asterisk 22** on a small Linux box, VM, or Docker container. This book ships a ready-made Docker lab (see the lab guide) that boots a fully configured Asterisk 22 with a single command — no compilation, no hardware.
- **Two softphones** registered as PJSIP endpoints, so you can place a real call between them. Throughout this book we use the **SipPulse Softphone** (free download: <https://www.sippulse.com/produtos/softphone>), available for desktop and mobile.
- **A SIP trunk** (optional) from a VoIP provider, for when you want to reach the PSTN. No card and no analog line — just credentials.

This is how every example in this book is built and verified, and you can reproduce it on any laptop.

### The legacy way: analog/digital cards

Before VoIP, a test PBX needed physical interfaces: an **FXO** port to connect to an existing telephone line and an **FXS** port to connect an analog phone, which together gave you a 1×1 PBX. A single card carrying one FXO and one FXS interface was the classic starter kit. These DAHDI-based cards (from Sangoma, formerly Digium) still exist for sites that must terminate analog or T1/E1 lines, but they are niche today — most deployments are pure VoIP. If you only need to connect analog phones or lines, see the *Legacy Channels* chapter; otherwise you can skip telephony hardware entirely.

## Asterisk scenari

Asterisk può essere utilizzato in diversi scenari. Elencheremo alcuni di essi e spiegheremo i vantaggi e le possibili limitazioni di ciascuno.

### IP PBX

Lo scenario più comune è l'installazione di una nuova o la sostituzione di una PBX esistente. Se confronti Asterisk con alcune altre alternative, scoprirai che è più economico e più ricco di funzionalità rispetto alla maggior parte delle PBX attualmente disponibili sul mercato. Diverse aziende stanno ora cambiando le loro specifiche a favore di Asterisk invece di altre PBX di marca.

![Asterisk come IP PBX](../images/01-introduction-fig06.png)

### Abilitare IP i PBX legacy

L'immagine seguente illustra una delle configurazioni più comunemente usate. Le grandi aziende generalmente non vogliono correre rischi significativi quando investono in nuove tecnologie e desiderano al contempo preservare i loro investimenti in apparecchiature legacy. Abilitare IP un PBX legacy può essere molto costoso; quindi, collegare un Asterisk PBX usando linee T1/E1 può essere una buona alternativa per i clienti attenti ai costi. Un altro vantaggio è la possibilità di connettersi a un provider di servizi VoIP con tariffe telefoniche migliori.

![Abilitare IP a un PBX legacy](../images/01-introduction-fig07.png)

### Evasione del pedaggio

Un'applicazione molto utile per la VoIP è collegare le filiali tramite Internet o una WAN. Utilizzare una connessione dati esistente consente di bypassare le tariffe di chiamata sostenute nelle connessioni di telecomunicazione tra la sede centrale e le filiali.

![Bypass del pedaggio tra uffici su una WAN](../images/01-introduction-fig08.png)

### Server Applicativo (IVR, Conferenza, Segreteria Telefonica)

Asterisk può essere usato come server applicativo per l'esistente PBX o collegato direttamente al PSTN. Asterisk offre servizi come segreteria telefonica, ricezione fax, registrazione delle chiamate, IVR collegato a un database e un server di conferenza audio. Se integri la segreteria telefonica e il fax in un server di posta elettronica esistente, otterrai un sistema di messaggistica unificata, che di solito è una soluzione costosa. Utilizzare Asterisk come server applicativo fornisce una riduzione dei costi estrema rispetto ad altre soluzioni.

![Asterisk come server di applicazioni](../images/01-introduction-fig09.png)

### Gateway Multimediale

La maggior parte dei provider di servizi voice-over IP utilizza un proxy SIP per gestire tutte le registrazioni, la localizzazione e l'autenticazione degli utenti SIP. Devono comunque inviare le chiamate al PSTN direttamente o instradarle attraverso un fornitore di terminazione di chiamate all'ingrosso usando una connessione voice-over IP SIP o H.323. Asterisk può agire come back-to-back user agent (B2BUA) o media gateway, sostituendo soft switch o media gateway molto costosi. Confronta il prezzo di un gateway quattro E1/T1 dei principali produttori di mercato con Asterisk. La soluzione Asterisk può costare diverse volte meno di altre soluzioni ed è in grado di tradurre i protocolli di segnalazione (H.323, SIP, IAX…) e i codec (G.711, G.729…).

![Asterisk come gateway multimediale](../images/01-introduction-fig10.png)

### Piattaforma Contact Center

Un contact center è una soluzione molto complessa che combina diverse tecnologie, come la distribuzione automatica delle chiamate (ACD), la risposta vocale interattiva (IVR) e la supervisione delle chiamate. Fondamentalmente, sono disponibili tre tipi di contact center: inbound, outbound e blended.

I centri di contatto in ingresso sono molto sofisticati e solitamente richiedono ACD, IVR, CTI, registrazione, supervisione e report. Asterisk dispone di un ACD integrato per accodare le chiamate. L'IVR può essere realizzato utilizzando l'Asterisk Gateway Interface (AGI) o meccanismi interni come l'applicazione `background()`. L'integrazione telefonica computer (CTI) è ottenuta tramite l'Asterisk Manager Interface (AMI); la registrazione e la generazione di report sono integrate in Asterisk.

Per un contact center outbound, un predictive o power dialer è uno dei componenti principali. Sebbene siano disponibili diversi dialer per l'Asterisk open‑source, non è difficile creare il proprio per la piattaforma se lo si desidera. Un contact center blended consente operazioni simultanee inbound e outbound, risparmiando denaro garantendo un migliore utilizzo del tempo dell'agente. È possibile utilizzare Asterisk e il suo meccanismo ACD per implementare una soluzione blended.

![Una piattaforma di contact-center Asterisk](../images/01-introduction-fig11.png)

## Trovare informazioni e aiuto

Questa sezione fornirà alcune delle principali fonti di informazione relative ad Asterisk.

- Sito ufficiale di Asterisk: <https://www.asterisk.org> Qui è possibile trovare informazioni su:
- Documentazione & Wiki -> <https://docs.asterisk.org>
- Forum della community -> <https://community.asterisk.org>
- Tracciamento dei bug -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legacy, in gran parte sostituito da docs.asterisk.org) -> <https://wiki.asterisk.org>

### Forum della community

Il forum della community di Asterisk ha in gran parte sostituito le vecchie mailing list ed è il luogo dove porre domande. Cerca di raccogliere quante più informazioni possibili prima di pubblicare. Nessuno ti aiuterà se non hai fatto i compiti — prova almeno una volta a risolvere il problema da solo.

- <https://community.asterisk.org>

## Summary

Asterisk è un software con licenza GPL che consente a un normale PC di fungere da potente piattaforma IP PBX. Mark Spencer di Digium ha creato Asterisk alla fine degli anni ’90, e Digium si è sostenuta vendendo hardware e prodotti commerciali correlati ad Asterisk. Digium è stata acquisita da Sangoma Technologies nel 2018; Sangoma ora sponsorizza lo sviluppo di Asterisk. Il design dell’interfaccia hardware ha avuto origine nel progetto Zapata sviluppato da Jim Dixon, che ha dato vita a DAHDI.

L’architettura di Asterisk comprende i seguenti componenti principali:

- CHANNELS: Analogico, digitale o voice‑over IP. In Asterisk 22 LTS, SIP è gestito esclusivamente da `chan_pjsip`.  
- PROTOCOLS: Protocolli di comunicazione, responsabili della segnalazione delle chiamate, inclusi SIP (via PJSIP), H.323, MGCP e IAX2.  
- CODECS: Traduzione dei formati digitali della voce, consentendo compressione e nascondimento della perdita di pacchetti. Si noti che Asterisk stesso non esegue la soppressione del silenzio (voice activity detection) né la generazione di rumore di comfort; quando gli endpoint usano VAD, il rumore di comfort dovrebbe essere disabilitato sul lato client.  
- APPLICATIONS: Responsabili della funzionalità PBX di Asterisk. Conferenza, segreteria telefonica e fax sono esempi di applicazioni Asterisk.

Asterisk può essere utilizzato in vari scenari, da una piccola IP PBX a un sofisticato contact center. È facile trovare aiuto su www.asterisk.org e docs.asterisk.org.

## Quiz

1. Quale azienda ha acquisito Digium nel 2018 e ora è il principale responsabile del progetto open‑source Asterisk?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. In Asterisk 22 LTS, quale driver di canale fornisce la connettività SIP?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Vero o falso: il driver di canale `chan_sip` è stato rimosso in Asterisk 21 e non è presente in una build standard di Asterisk 22.

4. Quali dei seguenti canali/protocolli **non fanno più** parte di una build standard di Asterisk 22? (Seleziona tutti quelli applicabili.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, sopravvissuto solo come componente aggiuntivo della community `ooh323`)

5. L'architettura hardware del progetto Zapata, originariamente chiamata Zaptel, è stata successivamente rinominata in ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Quando Asterisk deve convertire l’audio da un codec all’altro, attraverso quale formato di flusso interno effettua la traduzione?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Secondo il capitolo, qual è la situazione di licenza del modulo codec G.729 distribuito da Sangoma?
   - A. È GPL e completamente gratuito per qualsiasi utilizzo.
   - B. Il download è gratuito, ma l’uso legale richiede l’acquisto di una licenza per canale.
   - C. Non può essere ottenuto affatto senza acquistare Asterisk Business Edition.
   - D. Funziona solo in modalità pass‑through e non può essere installato.

8. Quale applicazione di Asterisk è usata per collegare una chiamata da un telefono a un altro?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Che cos’è il canale `Local` in Asterisk?
   - A. Un’interfaccia hardware FXS per telefoni analogici.
   - B. Un trunk SIP verso un provider locale.
   - C. Un pseudo‑canale che reinvia una chiamata nel dialplan in un contesto diverso.
   - D. Un codec usato per chiamate on‑net.

10. In quale scenario di utilizzo Asterisk agisce come back‑to‑back user agent (B2BUA), traducendo tra protocolli di segnalazione e codec per sostituire costosi soft switch?
    - A. Abilitazione IP di un PBX legacy
    - B. Bypass delle tariffe
    - C. Media Gateway
    - D. Piattaforma per Contact Center

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
