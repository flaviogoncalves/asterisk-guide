# Asterisk Security

Fin dall'inizio, la questione della sicurezza per Asterisk è critica. SIP, Session Initiation Protocol, è il protocollo più attaccato su Internet secondo il CERT.BR. Qualsiasi persona che gestisce un honeypot può confermarlo. Il problema del Internet Revenue Share Fraud è molto serio e può portare a perdite superiori a centinaia di migliaia di dollari. Non dovresti mai installare un server Asterisk connesso a Internet senza una sicurezza adeguata. In questo capitolo imparerai a identificare i principali tipi di attacchi che puoi ricevere e come prevenirli usando una corretta politica di sicurezza. Ultimo, ma non meno importante, imparerai come implementare la politica di sicurezza suggerita.

Questo capitolo è rivolto ad **Asterisk 22 LTS**, dove PJSIP (`res_pjsip` / `chan_pjsip`) è l'unico canale SIP. (Il vecchio driver `chan_sip` è stato rimosso in Asterisk 21 — vedi il capitolo *Legacy Channels* se stai migrando un sistema più vecchio.) Una conseguenza rilevante per la sicurezza: le autenticazioni fallite sono ora emesse attraverso il **security event framework** di Asterisk e il canale logger dedicato `security`, il che cambia il modo in cui Fail2Ban è configurato (coperto più avanti in questo capitolo).

## Objectives

By the end of this chapter you should be able to:

- Identify the main types of attacks frequently made to Asterisk servers
- Define an effective security policy
- Implement the security policy
- Install and configure IPTABLES for Asterisk
- Install and configure Fail2Ban for Asterisk
- Install and configure TLS and SRTP for encryption

## Principali attacchi alla telefonia IP

Le principali tipologie di attacchi alla telefonia IP possono essere classificate come DOS/DDOS, Furto di Servizio/Frode di Tariffazione e Intercettazione. Alcuni dei nomi possono creare confusione e fonti diverse a volte usano nomi differenti per lo stesso attacco. Furto di Servizio, Frode di Tariffazione, Frode di Condivisione dei Ricavi Internet, Frode Telefonica sono nomi diversi per gli hacker che usano il tuo PBX per generare traffico verso un Numero a Tariffa Premium e ottenere rimborsi dal provider.

### Attacchi DDoS/DOS

Denial of Service e Distributed Denial of Service sono attacchi popolari a qualsiasi infrastruttura IT. Non è diverso con SIP e gli altri protocolli Voice over IP. Il distributed denial of service è solitamente perpetrato da una botnet mentre il DOS da un singolo computer. Nel febbraio 2011 la botnet Sality ha effettuato una scansione furtiva e coordinata dell'intero spazio di indirizzi IPv4 alla ricerca di server SIP vulnerabili — i ricercatori che osservavano il UCSD Network Telescope l'hanno attribuita a circa tre milioni di IP sorgente distinti che sondavano la porta UDP 5060, molto probabilmente per forzare gli account SIP per frodi di tariffazione.[^sality]

[^sality]: A. Dainotti et al., "Analisi di una scansione stealth “/0” da un botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Una botnet peer-to-peer che dirige migliaia di tentativi di registrazione SIP verso un server](../images/19-security-fig01.png)

Il DOS viene solitamente applicato tramite tecniche come il fuzzing e il flooding. Il flooding può utilizzare SIP, IAX, RTP e altri protocolli. Possono interrompere completamente il servizio o degradare la qualità della voce. Sono molto difficili da mitigare se le porte sono aperte a Internet. Di seguito sono riportati alcuni degli strumenti utilizzati dagli aggressori

**Fuzzing:**

- **PROTOS Test Suite (c07-sip)** — dall'Università di Oulu OUSPG. Invia migliaia di pacchetti malformati per provocare un malfunzionamento come un buffer overflow che arresta il software.  
- **Voiper** — genera più di 200.000 test che coprono tutti gli attributi SIP e verifica se il tuo server può elaborare i messaggi in modo efficace. <http://voiper.sourceforge.net/>

**Inondazione:**

- **INVITE Flooder** — inonda il server con richieste SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — inonda il server con traffico IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — inonda le sessioni media attive con pacchetti RTP per degradare la qualità della voce. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Tecniche di mitigazione per DoS/DDoS

Le mie raccomandazioni sono

1. Non esporre il tuo server Asterisk su Internet, a meno che non sia necessario con adeguata protezione (SBC)  
2. Nella rete interna utilizza una Virtual LAN per la voce, soprattutto se ti trovi in un'Università o College dove il numero di utenti è elevato.  
3. Usa VPN o TLS per l'accesso esterno.

### Frode sul Revenue Share Internet

This fraud is a bit tricky to understand. The key is to understand the concept of an International premium rate number (IPRN).

![I tre passaggi della frode di condivisione dei ricavi su Internet: acquistare un numero a tariffa premium, trovare un dispositivo VoIP vulnerabile e chiamare il numero, quindi raccogliere il pagamento](../images/19-security-fig02.png)

Un IPRN è un numero che puoi allocare gratuitamente in alcune specifiche compagnie telefoniche internet. Search for Internet Premium Rate Number Providers e troverai un sacco di loro. In questo tipo di operatore puoi allocare, come esempio, un numero in una rete satellitare come Iridium, una destinazione che costa decimi di dollari al minuto per il chiamante. Il provider IPRN ti restituirà una percentuale del ricavo (10 al 20% del reddito) per ogni minuto ricevuto.

![Un listino prezzi di un provider IPRN che mostra le tariffe di pagamento per paese e i numeri di test](../images/19-security-fig03.png)

Dopo la fase di allocazione, l'hacker cerca di trovare qualsiasi server Asterisk aperto in grado di chiamare l'IPRN allocato. Il PBX della vittima, controllato dall'hacker, effettuerà centinaia di chiamate al numero IPRN generando un grande ritorno per l'hacker e una enorme bolletta telefonica per la vittima. Molte volte, più di centinaia di migliaia di dollari in un unico weekend.

Principali strumenti usati dagli hacker per attaccare un PBX:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious è un set di strumenti di sicurezza facile da usare. Il suo obiettivo principale è riconoscere PBX vulnerabili e forzare le password SIP usando un attacco a forza bruta. Lo strumento più usato è svcrack. Lo strumento è in grado di testare migliaia di password al secondo.  
2. **Phone vulnerabilities**. Un altro punto frequentemente sfruttato dagli hacker come vettore di attacco è il telefono stesso. Molte persone che installano Asterisk non cambiano la password predefinita nell'interfaccia web del telefono. Una volta che questi telefoni sono esposti su Internet, gli hacker possono provare a usare la password predefinita dell'interfaccia per scaricare la configurazione dove spesso possono trovare la password segreta SIP.

#### TFTPTheft:

Se stai usando il provisioning automatico dei telefoni tramite TFTP, probabilmente sei vulnerabile a questo tipo di attacco. TFTP è una forma semplice e insicura di File Transfer Protocol.

![Un attaccante che scarica file .cfg indovinabili da un server TFTP, raccogliendo credenziali in chiaro dai file di configurazione](../images/19-security-fig04.png)

Il nome dei file di configurazione è facilmente indovinabile usando l'indirizzo MAC seguito da .cfg (ad es. 001A2B3C4D5E.cfg). Un hacker esperto può facilmente creare un'utilità per provare tutti gli indirizzi MAC in sequenza o semplicemente scaricare uno strumento per farlo. Il file di configurazione è solitamente non crittografato e contiene la password segreta SIP al suo interno.

#### Mitigazione per attacchi di forza bruta e furto tftp

Per mitigare questi attacchi è possibile applicare le soluzioni seguenti. Brute force: La soluzione migliore per mitigare gli attacchi di forza bruta è impedire tentativi non autorizzati sequenziali. Quasi tutti gli installer di Asterisk usano l'utilità fail2ban a questo scopo. Quando fail2ban rileva più tentativi con password o nome utente errati, banna l'IP dell'attaccante per un certo periodo di tempo. La seconda misura contro la forza bruta è utilizzare password robuste, più di 12 caratteri, con almeno un carattere speciale. Tftptheft: Per prevenire il TFTPTheft, configurare il provisioning per usare https con nome e password. Il file viene trasmesso criptato e un nome e una password impediscono agli aggressori di tentare di scaricare qualsiasi file.

### Intercettazione

Non vediamo molte di queste tipologie di attacco perché nella maggior parte dei casi non vengono semplicemente rilevate. L’intercettazione è molto difficile da rilevare in un ambiente IP. Utility come UCsniff, disponibili gratuitamente, sono in grado di intercettare una chiamata VoIP nella maggior parte delle reti. La tecnica principale consiste nell’utilizzare l’ARP spoofing per forzare il traffico attraverso il computer che esegue UCsniff e registrare le chiamate.

#### Mitigazione contro l'intercettazione

Puoi prevenire l'intercettazione crittografando il tuo traffico VoIP. L'altro modo è prevenire gli attacchi man‑in‑the‑middle (MITM) sulla tua rete. L'ispezione ARP è molto efficace per prevenire i MITM nelle reti di livello 2. Consulta il supporto tecnico della tua rete per capire come implementarla. Più avanti in questo libro impareremo come installare la crittografia basata su TLS e SRTP. Puoi anche usare ARPWatch per scoprire se qualcuno sta abusando del protocollo ARP per attaccare la tua rete.

## Politica di sicurezza per Asterisk

Il modo migliore per implementare la sicurezza è creare una politica di sicurezza. Per questo corso suggerirò una politica di sicurezza per la maggior parte delle installazioni di Asterisk. Usala come punto di partenza di base e modificala in base alle tue esigenze. La politica di sicurezza suggerita segue di seguito:

1. Nessuna porta UDP/TCP non necessaria aperta
2. Nessun accesso a nessuna interfaccia amministrativa (SSH/HTTPS) aperta su Internet.
3. Per accedere a SSH e/o HTTP/HTTPS dovrebbe esserci un'eccezione esplicita nel firewall IPTABLES
4. Password robuste con 12 caratteri e almeno un carattere speciale
5. Bloccare gli indirizzi IP che falliscono più di 10 volte l'autenticazione usando Fail2ban
6. Conferma della password per le chiamate internazionali
7. Limitare l'accesso alla porta SIP al tuo intervallo di indirizzi IP conosciuto

Se hai bisogno di avere accesso esterno al tuo PBX, ci sono due possibilità. Usa un SBC (Session Border Controller) per proteggere il tuo server contro DOS/DDOS o usa una VPN ogni volta che desideri accesso esterno. Se lasci la porta 5060 aperta su Internet senza un SBC o VPN, sei vulnerabile a un attacco DOS/DDOS. Il rischio è tuo.

### Rinforzo dell'era PJSIP (Asterisk 22)

Beyond the firewall and Fail2Ban, Asterisk 22's PJSIP stack provides several configuration-level controls that should be part of your security policy. These complement (not replace) the network controls above:

- **Autenticazione per endpoint.** Ogni endpoint dovrebbe fare riferimento a una sezione dedicata `type=auth` con un `password` forte e unico (`auth_type=digest`). Non riutilizzare credenziali tra endpoint.  
- **La gestione anonima è integrata.** PJSIP non rivela se un nome utente esiste quando l'autenticazione fallisce. Per accettare chiamate anonime è necessario creare esplicitamente un endpoint chiamato `anonymous` e usare sezioni `type=identify` (corrispondenti all'IP di origine) per mappare peer noti su endpoint. Se non vuoi chiamate anonime, basta non creare un endpoint `anonymous`, e le richieste non corrispondenti verranno sfidate/rifiutate.  
- **ACL.** Limita chi può raggiungere un endpoint con ACL denominate `/etc/asterisk/acl.conf`, richiamate dall'endpoint con `acl=` (ACL di segnalazione/fonte) e `contact_acl=` (limita l'indirizzo di contatto/registrazione). È anche possibile impostare permit/deny direttamente sull'endpoint.  
- **`qualify`.** Imposta `qualify_frequency` (e `qualify_timeout`) sull'AOR affinché Asterisk monitori attivamente la raggiungibilità dei contatti registrati e rimuova quelli inattivi.  
- **Rinforzo del trasporto PJSIP / protezione DoS.** Il `type=transport` non espone un limite client per trasporto, quindi la protezione contro inondazioni di connessioni proviene dal firewall (le regole iptables/Fail2Ban in questo capitolo) anziché da un'opzione PJSIP. Ciò che il trasporto *fornisce* è la regolazione del keep-alive TCP (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) per eliminare connessioni morte o semi‑aperte, e le impostazioni `local_net`/`external_*` per una corretta gestione NAT. Combina questi con le regole del firewall per attenuare gli attacchi di flood di connessioni.  
- **TLS + SRTP per i media.** Cifra la segnalazione con un trasporto TLS e i media con `media_encryption=sdes` (o `dtls` per WebRTC) sull'endpoint — trattato più avanti in questo capitolo.  
- **Controllo accessi AMI/ARI.** Limita l'Interfaccia di Gestione di Asterisk (`manager.conf`) e ARI (`ari.conf` / `http.conf`) a localhost o a una rete di gestione fidata, usa segreti forti e unici, associa il server HTTP a un'interfaccia privata e non esporre mai questi servizi a Internet.

Tutti i nomi delle opzioni sopra sono confermati rispetto ad Asterisk 22.10: la sezione `type=transport` espone `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, e la famiglia `external_*`, ma non ha **nessuna** opzione `max_clients` — la protezione contro il flood di connessioni proviene dal firewall, non dal trasporto. Le opzioni endpoint `acl` e `contact_acl` prendono i nomi delle sezioni da `acl.conf`, e il matching dell'IP di origine per i peer non autenticati è effettuato con le sezioni `type=identify` (`match=`).

### Rimozione delle porte non necessarie

Invece di scoprire tutte le vulnerabilità associate a tutti i protocolli Asterisk, semplifichiamo il problema rimuovendo le porte non necessarie. Per elencare tutte le porte aperte dal server Asterisk usa:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 non è più necessario noload `chan_mgcp` o `chan_skinny` — quei driver sono stati *rimossi* in Asterisk 21 e non fanno parte di una build standard 22.) Con le istruzioni sopra, ho rimosso tutti i canali non necessari mantenendo solo PJSIP. Puoi scegliere i moduli di protocollo che desideri, basta rimuovere quelli inutilizzati. Il risultato è mostrato nello screenshot qui sotto — solo la porta SIP (5060) legata al tuo trasporto PJSIP è ora esposta in ingresso.

![output di netstat dopo aver disabilitato i moduli inutilizzati: solo la porta UDP 5060 rimane legata ad Asterisk](../images/19-security-fig06.png)

### Implementazione della politica di sicurezza con IPTABLES

IPTABLES o netfilter è un firewall standard presente nella maggior parte delle distribuzioni Linux. In questo laboratorio configureremo iptables e fail2ban. L'obiettivo è implementare la politica di sicurezza consigliata per Asterisk e bloccare tutto il traffico non necessario. Segui i passaggi seguenti:

1. Bloccare tutto il traffico esterno
2. Consentire il traffico SSH da una rete interna o da un singolo host
3. Consentire il traffico SIP in UDP e TCP sulle porte 5060
4. Consentire il traffico RTP nell'intervallo di porte media UDP. Non esiste un valore predefinito unico incorporato — il `rtp.conf` di Asterisk ricade sulle porte 5000–31000 quando non è impostato nulla, ma il `rtp.conf.sample` fornito configura `rtpstart=10000` / `rtpend=20000`, quindi usiamo quell'intervallo di esempio qui. Adatta la regola del firewall a qualsiasi `rtpstart`/`rtpend` tu abbia effettivamente impostato in `rtp.conf`.

Assicurati di avere accesso alla console del server, non vuoi bloccare te stesso fuori dal sistema. Fai attenzione.

1. Installa il pacchetto net-persistent.```
   sudo apt-get install iptables-persistent
   ```

2. Consenti tutto il traffico dal loopback```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. Consenti connessioni stabilite```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. Consenti traffico SSH/HTTPS dalla rete 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Inserire le regole di Asterisk```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   Nota che la porta 5061 (SIP over TLS) è **TCP**, non UDP. Le regole sopra aprono la 5060 sia su UDP che su TCP e la 5061 su TCP. Se utilizzi solo TLS, puoi eliminare completamente le regole per la 5060 in chiaro. Apri solo le porte a cui i tuoi trasporti PJSIP si legano effettivamente.

   `-I` significa PREPEND

6. L'ultima regola deve essere un drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` significa APPEND. Nota: fai attenzione quando mantieni nuove regole, devi aggiungere le regole prima del DROP. Usa PREPEND per nuove regole `-I`

7. Salva le regole e riavvia iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Utilizzare Fail2Ban per bloccare più tentativi falliti di autenticazione

Fail2Ban è quasi uno standard per Asterisk. La maggior parte degli utenti lo implementa per migliorare la sicurezza. Questa utility analizza i log di Asterisk alla ricerca di tentativi falliti e banna gli indirizzi IP degli aggressori. Di seguito fornisco le istruzioni per installare Fail2Ban.

In Asterisk 22, PJSIP segnala autenticazioni fallite e altri eventi di sicurezza tramite il **framework degli eventi di sicurezza** di Asterisk, scritto sul canale logger dedicato **`security`**. Per far funzionare Fail2Ban è necessario:

1. Abilitare il canale di sicurezza in `/etc/asterisk/logger.conf`. La sintassi è `<filename> => <levels>`, quindi per inviare il livello di sicurezza a un file chiamato `security` scrivi:

```
[logfiles]
security => security
```

esegui quindi `logger reload` dalla CLI. Questo produce `/var/log/asterisk/security` con una riga per evento di sicurezza, nella forma:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Gli eventi di cui si occupa Fail2Ban sono `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` e `FailedACL`, ognuno dei quali contiene un campo `RemoteAddress="IPV4/UDP/<ip>/<port>"` che identifica l'autore. (Nota che l'indirizzo è avvolto come `IPV4/UDP/.../...`, non come un IP nudo — il tuo filtro deve estrarre l'host da dentro quella stringa.)

2. Puntare la prigione `asterisk` a quel file (`logpath = /var/log/asterisk/security`) e usare un filtro che analizzi questo formato di evento di sicurezza.

Le versioni moderne di Fail2Ban includono un filtro `asterisk` il cui `failregex` corrisponde già agli eventi sopra e estrae `<HOST>` dal campo `RemoteAddress`, per esempio:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX distributions (FreePBX/Sangoma) ship equivalent filters. Prefer the packaged filter over hand‑writing one, since the exact event strings are version‑dependent. One caveat to be aware of: a now‑patched advisory (GHSA-5743-x3p5-3rg7) showed that crafted PJSIP traffic could inject fake log lines — keep both Asterisk and your Fail2Ban filter current.

Below I provide the instructions to install Fail2Ban

1. Install fail2ban on Linux```
   sudo apt-get install fail2ban
   ```

2. Attiva fail2ban per Asterisk e SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   Aggiungi le seguenti righe per attivare fail2ban per ssh e asterisk```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. Riavvia fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Verifica. Cambia il segreto dal tuo softphone e prova a ri‑registrarti 10 volte. Usando `iptables -L`, controlla se l’indirizzo del softphone è stato incluso come indirizzo bloccato.  
5. Rimuovi l’indirizzo dal ban (supponiamo che l’indirizzo sia 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementazione di TLS e SRTP

Dividerò questa sezione in due parti. Nella prima tratteremo TLS per cifrare la segnalazione e nella seconda SRTP per cifrare i media. L'obiettivo è configurare Asterisk per queste risorse.

#### TLS

TLS (Transport Layer Security) è il meccanismo di cifratura definito per proteggere la segnalazione SIP. La tabella seguente riassume quali attacchi TLS protegge:

| Type of attack | Protected? | Notes |
|----------------|-----------|-------|
| Signaling attacks | Yes | TLS assures the integrity of the messages |
| Man in the middle | Yes | TLS checks the server certificate |
| Eavesdropping | No | TLS encrypts signaling, not media |

Per la cifratura dei media (voce/video) utilizzare SRTP.

#### Certificati digitali autofirmati

Esistono due tipologie di certificati: autofirmati e commerciali. I certificati autofirmati sono firmati dal proprio server, mentre i certificati commerciali sono firmati da un'autorità esterna. Per la VoIP, è possibile essere la propria autorità di certificazione. Non è necessario un certificato esterno come GoDaddy o Verisign, poiché rappresenta una spesa non necessaria. Genereremo i nostri certificati usando `ast_tls_cert`.

#### Configurazione di TLS con certificati autofirmati

Di seguito una guida passo‑passo su come implementare TLS. Prima generiamo i certificati, poi configuriamo il trasporto TLS di PJSIP (vedi "Configuring TLS with chan_pjsip") e infine puntiamo il softphone verso di esso. Useremo il SipPulse Softphone, che supporta TLS e SRTP nativamente. (Qualsiasi softphone SIP compatibile con TLS/SRTP funziona allo stesso modo.)

**Step 1.** Creare una chiave RSA privata usando la cifratura 3DES con una lunghezza di 4096 bit per la nostra autorità di certificazione. Il comando sotto, presente in `/usr/src/asterisk-22.x.y/contrib/scripts`, creerà la Certification Authority e il Certificate di Asterisk. Come al solito, adattare le istruzioni se necessario, le versioni cambiano, le directory cambiano. Per favore, fate attenzione a quello che state facendo. Usate il vostro dominio o indirizzo IP nell'opzione `-C`. Il comando `ast_tls_cert` ha tre opzioni.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

Non genererò un certificato client perché non utilizzeremo il certificato per autenticare il client. Il client non è tenuto a presentare un proprio certificato.

**Step 2.** Configurare Asterisk per supportare il nostro client via TLS. Questo avviene in `pjsip.conf` (un trasporto TLS più le impostazioni dell’endpoint) — la configurazione completa è mostrata nella sezione successiva, “Configuring TLS with chan_pjsip”. Non stiamo autenticando con i certificati, ma solo cifrando il traffico.

**Step 3.** Installare un softphone SIP compatibile TLS (l’autore utilizza il SipPulse Softphone).

**Step 4.** Copiare l’autorità di certificazione sul computer che esegue il softphone. Dopo averla installata, copiare il file `/etc/asterisk/keys/ca.crt` sul computer che esegue il softphone (usare scp, o WinSCP su Windows) se si sta usando un certificato autofirmato.

**Step 5.** Creare l’account nel softphone. Nella schermata dell’account aggiungere l’account normalmente come qualsiasi altro account sip. Usare la password corretta, l’autenticazione è ancora basata sulla password.

**Step 6.** Impostare TLS come trasporto nelle impostazioni dell’account. Nella schermata dell’account del SipPulse Softphone (sotto), scegliere **TLS** come trasporto e usare la porta 5061. Regolare il firewall per aprire la porta TCP 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Fidarsi dell’autorità di certificazione. Se il certificato TLS di Asterisk è firmato da una CA pubblica (ad esempio Let’s Encrypt — vedere il capitolo *Deployment*), un softphone moderno come il SipPulse Softphone lo riconosce automaticamente tramite il negozio di certificati di sistema, senza importazione manuale. Se si utilizza un certificato autofirmato, importare la sua CA (`/etc/asterisk/keys/ca.crt`) nel client o nel negozio di fiducia del sistema operativo, o accettarlo quando richiesto.

**Step 8.** Non è necessario un certificato client. Un’idea sbagliata comune è che ogni telefono abbia bisogno di un proprio certificato per autenticarsi — non è così. A questo punto Asterisk **cifra** solo la sessione; l’autenticazione è ancora nome utente e password. Asterisk non verifica i certificati client per impostazione predefinita, quindi non è necessario distribuire un certificato per ogni client.

**Step 9.** Dopo aver cambiato il certificato o il trasporto, riavviare completamente il softphone (uscire e riavviare, non solo chiudere la finestra) così si riconnette sul nuovo trasporto.

### Configuring TLS with chan_pjsip

Ora impariamo come configurare PJSIP per TLS. PJSIP è l’unico canale SIP in Asterisk 22, quindi non c’è nulla da cambiare — basta assicurarsi che `res_pjsip`, `res_pjproject` e `chan_pjsip` siano caricati. Step 1: Confermare che PJSIP sia abilitato in /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Passo 2: Configurare PJSIP per supportare TLS. Aggiungere una sezione per il trasporto TLS nel file /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (or `tlsv1_3` if your OpenSSL/PJSIP build supports it) — TLS 1.0/1.1 are obsolete and insecure and should not be used.

Step 3: Configure the endpoint for blink. Edit `pjsip.conf` and edit the section for blink. Let PJSIP choose the transport automatically.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

Step 4: Verifica. Per verificare che la registrazione sia avvenuta tramite TLS, usa il seguente comando nella console di Asterisk.

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### Making secure calls using SRTP

Il protocollo responsabile della crittografia dei media è il Secure Real Time Protocol (SRTP) definito nella RFC3711. Uno dei punti deboli del protocollo è la mancanza di un metodo standardizzato per lo scambio delle chiavi. Asterisk utilizza lo scambio di chiavi SDES tramite il protocollo SDP protetto dalla crittografia di segnalazione fornita da TLS. Esistono anche altri metodi come MIKEY e ZRTP. ZRTP, sviluppato da Philipp Zimmermann, è uno dei metodi più sofisticati per lo scambio di chiavi e la crittografia dei media. Alcuni softphone e telefoni fissi supportano ZRTP. Tuttavia il metodo standard è ancora SDES e lo troverete in quasi tutti i telefoni disponibili sul mercato. Di seguito un esempio di richiesta con le chiavi crypto definite nel SDP nelle righe a=crypto:1 e a=crypto:2.

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### Configurazione di SRTP su Asterisk

Per configurare SRTP su Asterisk è molto semplice. Imposta `media_encryption=sdes` sull'endpoint; puoi anche richiederlo con `media_encryption_optimistic=no` in modo che i media non crittografati vengano rifiutati anziché consentiti silenziosamente. Nota che SDES richiede che la segnalazione avvenga su TLS così le chiavi non vengono inviate in chiaro.

**Passo 1.** Configurazione di Asterisk

Imposta quanto segue nella sezione `type=endpoint` in `pjsip.conf`:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** Configurazione del Softphone

Nel softphone, abilita SRTP per i media dell'account (imposta l'opzione **SRTP (Media Encryption)** su *Mandatory*) in modo che la voce sia crittografata.

![Le impostazioni dell'account SipPulse Softphone (sezione inferiore) — imposta **Transport** su TLS e **SRTP (Media Encryption)** su *Mandatory* in modo che segnalazione e media siano entrambi crittografati.](../images/softphone/sipphone-config.png){width=35%}

## Abilitare l'autenticazione a due fattori per le chiamate internazionali

A volte il modo migliore è non avere rotte internazionali. Tuttavia, se è davvero necessario comporre numeri internazionali, utilizzare una password aggiuntiva. Useremo l'applicazione Asterisk **vmauthenticate** per richiedere la password della segreteria telefonica prima di effettuare la chiamata internazionale. Questa è configurata nel dialplan in **extensions.conf**. Vedi l'esempio sotto. Così un hacker, anche dopo aver scoperto la password di un peer o compromesso un telefono, dovrà comunque conoscere la password della segreteria per comporre questa destinazione.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` è ancora un'applicazione standard in Asterisk 22. Il `Dial()` sopra instrada la chiamata attraverso un trunk SIP/PJSIP (`PJSIP/<number>@<trunk>`), che è il modo in cui la maggior parte delle installazioni moderne raggiunge la PSTN — adatta `my_trunk` al nome del tuo trunk, e usa `DAHDI/g1/...` solo se disponi effettivamente di uno span DAHDI. Difesa contro le frodi telefoniche nel dialplan — un secondo fattore come questo, combinato con la limitazione dei contesti che possono raggiungere le tue rotte in uscita e internazionali — rimane una delle protezioni più importanti che puoi implementare.

## Riepilogo

In questo capitolo hai appreso i rischi di avere un IP PBX collegato a Internet. Poi abbiamo visto come proteggere il nostro PBX implementando una security police. In questa security police abbiamo implementato iptables, fail2ban, TLS, SRTP e l'autenticazione a due vie per le chiamate internazionali. Spero che tu abbia apprezzato questo capitolo.

## Quiz

1. Qual è la contromisura più importante contro l'Internet Revenue Share Fraud?
   - A. Implementare SRTP
   - B. Mantenere Asterisk aggiornato
   - C. Implementare TLS
   - D. Utilizzare password complesse
2. Il fuzzing SIP è definito come:
   - A. Un attacco DoS con richieste e risposte malformate
   - B. Furto di servizio dove le password vengono forzate a forza bruta
   - C. Intercettazione delle chiamate in corso
   - D. Un DDoS con un'inondazione di richieste SIP
3. TFTPTheft si verifica quando il server fornisce file di configurazione via TFTP. È possibile evitarlo usando:
   - A. FTP
   - B. HTTP
   - C. HTTPS con nome utente e password
   - D. SCP
4. Gli attacchi man-in-the-middle usano una tecnica chiamata:
   - A. TFTP theft
   - B. ARP spoofing
   - C. MAC poisoning
   - D. dsniff
5. Per SRTP, Asterisk utilizza il seguente sistema per lo scambio di chiavi:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. L'utilità che genera l'autorità di certificazione e i certificati, presente in `/usr/src/asterisk-22.x.y/contrib/scripts`, è:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Strategie valide per prevenire l'intercettazione (seleziona tutte le opzioni applicabili):
   - A. Implementare rilevatori analogici di intercettazione
   - B. Utilizzare l'utilità ARPwatch per rilevare ARP spoofing
   - C. Abilitare il rilevamento di ARP-spoofing negli switch
   - D. Utilizzare SRTP
8. Asterisk supporta l'autenticazione forte verificando i certificati client. (Il trasporto TLS di PJSIP può richiedere e verificare il certificato del client.)
   - A. Vero
   - B. Falso
9. Su Asterisk 22, quale impostazione dell'endpoint PJSIP attiva la crittografia media SRTP usando chiavi in‑SDP (SDES)?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. In Asterisk 22, Fail2Ban deve leggere gli eventi di autenticazione fallita di PJSIP dal canale logger dedicato ________ (abilitato in `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
