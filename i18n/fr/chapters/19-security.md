# Asterisk Security

Depuis le début, la question de la sécurité pour Asterisk est cruciale. SIP, Session Initiation Protocol, est le protocole le plus attaqué sur Internet selon le CERT.BR. Toute personne exécutant un honeypot peut le confirmer. Le problème de la fraude de partage de revenus sur Internet est très sérieux et peut entraîner des pertes supérieures à plusieurs centaines de milliers de dollars. Vous ne devez jamais installer un serveur Asterisk connecté à Internet sans une sécurité appropriée. Dans ce chapitre, vous apprendrez à identifier les principaux types d'attaques que vous pouvez recevoir et comment les prévenir en utilisant une politique de sécurité adéquate. Enfin, vous apprendrez à mettre en œuvre la politique de sécurité proposée.

Ce chapitre cible **Asterisk 22 LTS**, où PJSIP (`res_pjsip` / `chan_pjsip`) est le seul canal SIP. (L'ancien pilote `chan_sip` a été supprimé dans Asterisk 21 — voir le chapitre *Legacy Channels* si vous migrez un système plus ancien.) Une conséquence pertinente pour la sécurité : les authentifications échouées sont désormais émises via le **security event framework** d'Asterisk et le canal de journal dédié `security`, ce qui modifie la façon dont Fail2Ban est configuré (abordé plus loin dans ce chapitre).

## Objectives

À la fin de ce chapitre, vous devriez être capable de :

- Identifier les principaux types d'attaques fréquemment dirigées contre les serveurs Asterisk
- Définir une politique de sécurité efficace
- Mettre en œuvre la politique de sécurité
- Installer et configurer IPTABLES pour Asterisk
- Installer et configurer Fail2Ban pour Asterisk
- Installer et configurer TLS et SRTP pour le chiffrement

## Principales attaques contre la téléphonie IP

Les principales attaques contre la téléphonie IP peuvent être classées comme DOS/DDOS, vol de service/fraude de péage et écoute clandestine. Certains des noms peuvent prêter à confusion et différentes sources utilisent parfois des appellations différentes pour la même attaque. Vol de service, fraude de péage, fraude de partage de revenus Internet, fraude téléphonique sont des noms différents pour les pirates qui utilisent votre PBX pour acheminer du trafic vers un numéro à tarif premium et obtenir des remises du fournisseur.

### DDoS/DOS

Les attaques par déni de service et déni de service distribué sont courantes contre toute infrastructure informatique. Il en est de même pour SIP et les autres protocoles VoIP. Le déni de service distribué est généralement perpétré par un botnet, tandis que le DOS l’est simplement par un ordinateur unique. En février 2011, le botnet Sality a effectué un balayage furtif et coordonné de l’ensemble de l’espace d’adresses IPv4 à la recherche de serveurs SIP vulnérables — des chercheurs observant le UCSD Network Telescope ont attribué cela à environ trois millions d’adresses IP sources distinctes sondant le port UDP 5060, très probablement pour forcer les comptes SIP afin de commettre une fraude tarifaire.[^sality]

[^sality]: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![Un botnet peer-to-peer dirigeant des milliers de tentatives d'enregistrement SIP vers un serveur](../images/19-security-fig01.png)

Le DOS est généralement appliqué via des techniques telles que le fuzzing et le flooding. Le flooding peut utiliser SIP, IAX, RTP et d’autres protocoles. Ils peuvent arrêter le service complètement ou dégrader la qualité vocale. Ils sont très difficiles à atténuer si les ports sont ouverts à Internet. Ci‑dessous quelques‑uns des outils utilisés par les attaquants

**Fuzzing :**

- **PROTOS Test Suite (c07-sip)** — de l'Université d'Oulu OUSPG. Envoie des milliers de paquets malformés pour provoquer un dysfonctionnement tel qu'un débordement de tampon qui arrête le logiciel.  
- **Voiper** — génère plus de 200 000 tests couvrant tous les attributs SIP et vérifie si votre serveur peut traiter les messages efficacement. <http://voiper.sourceforge.net/>

**Inondation:**

- **INVITE Flooder** — inonde le serveur de requêtes SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — inonde le serveur de trafic IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — inonde les sessions média actives de paquets RTP pour dégrader la qualité vocale. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### Techniques d'atténuation pour DoS/DDoS

Mes recommandations sont

1. Ne pas exposer votre serveur Asterisk sur Internet, sauf si nécessaire avec une protection adéquate (SBC)
2. Dans le réseau interne utilisez un VLAN virtuel pour la voix, surtout si vous êtes dans une université, un collège où le nombre d'utilisateurs est élevé.
3. Utilisez VPN ou TLS pour l'accès externe.

### Fraude au partage des revenus Internet

Cette fraude est un peu difficile à comprendre. L'essentiel est de comprendre le concept de numéro à tarif premium international (IPRN).

![Les trois étapes de la fraude de partage de revenus Internet : acheter un numéro à tarif premium, trouver un appareil VoIP vulnérable et appeler le numéro, puis collecter le paiement](../images/19-security-fig02.png)

Un IPRN est un numéro que vous pouvez obtenir gratuitement auprès de certaines sociétés de téléphonie Internet spécifiques. Recherchez « Internet Premium Rate Number Providers » et vous en trouverez plusieurs. Avec ce type d’opérateur, vous pouvez, par exemple, attribuer un numéro sur un réseau satellite tel qu’Iridium, une destination coûtant quelques dixièmes de dollar par minute pour l’appelant. Le fournisseur d’IPRN vous reversera un pourcentage des revenus (10 à 20 % du chiffre d’affaires) pour chaque minute reçue.

![Une liste de prix d'un fournisseur IPRN montrant les taux de paiement par pays et les numéros de test](../images/19-security-fig03.png)

Après la phase d’allocation, le hacker tente de trouver un serveur Asterisk ouvert capable de composer le IPRN alloué. Le PBX de la victime, contrôlé par le hacker, passera des centaines d’appels vers le numéro IPRN, générant un important remboursement pour le hacker et une facture téléphonique énorme pour la victime. Souvent, cela dépasse plusieurs centaines de milliers de dollars en un seul week‑end.

Principaux outils utilisés par les hackers pour attaquer une PBX:

1. **SIPVicious** : http://code.google.com/p/sipvicious/. Sipvicious est un ensemble d'outils de sécurité facile à utiliser. Son objectif principal est de reconnaître les PBX vulnérables et de craquer les mots de passe SIP à l'aide d'une attaque par force brute. L'outil le plus utilisé est svcrack. Cet outil est capable de tester des milliers de mots de passe par seconde.  
2. **Vulnérabilités des téléphones**. Un autre point fréquemment exploité par les pirates comme vecteur d'attaque est le téléphone lui‑même. De nombreuses personnes qui installent Asterisk ne changent pas le mot de passe par défaut dans l'interface web du téléphone. Une fois ces téléphones exposés sur Internet, les pirates peuvent essayer d'utiliser le mot de passe d'interface par défaut pour télécharger la configuration où ils trouvent souvent le secret du mot de passe SIP.

#### TFTPTheft:

Si vous utilisez l'auto‑provisionnement des téléphones avec TFTP, vous êtes probablement vulnérable à ce type d'attaque. TFTP est une forme simple et peu sécurisée d'un protocole de transfert de fichiers.

![Un attaquant téléchargeant des fichiers .cfg devinables depuis un serveur TFTP, récupérant des identifiants en texte clair à partir des fichiers de configuration](../images/19-security-fig04.png)

Le nom des fichiers de configuration est facilement devinable en utilisant l'adresse mac suivie de .cfg (par ex. 001A2B3C4D5E.cfg). Un hacker avisé peut facilement créer un utilitaire pour essayer toutes les adresses MAC séquentiellement ou simplement télécharger un outil pour le faire. Le fichier de configuration est généralement non chiffré et contient le mot de passe secret SIP à l'intérieur.

#### Atténuation des attaques par force brute et vol de tftp

Pour atténuer ces attaques, vous pouvez appliquer les solutions ci‑dessous.  
Brute force : La meilleure solution pour atténuer les attaques par force brute est d’empêcher les tentatives non autorisées séquentielles. La quasi‑toute installation d’Asterisk utilise l’utilitaire fail2ban à cet effet. Lorsque fail2ban détecte plusieurs tentatives avec un mot de passe ou un nom d’utilisateur incorrect, il bannit l’adresse IP de l’attaquant pendant un certain temps. La deuxième mesure contre la force brute consiste à utiliser des mots de passe forts, de plus de 12 caractères, contenant au moins un caractère spécial.  
Tftptheft : Pour empêcher le TFTPTheft, configurez le provisioning pour utiliser https avec un nom et un mot de passe. Le fichier est transmis chiffré et un nom et un mot de passe empêchent les attaquants de tenter de télécharger des fichiers.

### Écoute clandestine

Nous ne voyons pas beaucoup ce type d’attaque car dans la plupart des cas elles ne sont tout simplement pas détectées. L’écoute clandestine est très difficile à détecter dans un environnement IP. Des utilitaires tels que UCsniff, librement disponibles, sont capables d’espionner un appel VoIP dans la plupart des réseaux. La technique principale consiste à utiliser l’usurpation ARP pour forcer le trafic à passer par l’ordinateur exécutant UCsniff et enregistrer les appels.

#### Atténuation de l'espionnage

Vous pouvez empêcher l'écoute clandestine en chiffrant votre trafic VoIP. L'autre façon est d'empêcher les attaques de type homme du milieu (MITM) sur votre réseau. L'inspection ARP est très efficace pour prévenir les MITM dans les réseaux de couche 2. Consultez le support technique de votre réseau pour comprendre comment la mettre en œuvre. Plus tard dans ce livre, nous apprendrons comment installer le chiffrement basé sur TLS et SRTP. Vous pouvez également utiliser ARPWatch pour découvrir si quelqu’un abuse maintenant du protocole ARP pour attaquer votre réseau.

## Security policy for Asterisk

La meilleure façon de mettre en œuvre la sécurité est de créer une politique de sécurité. Pour cette formation, je suggère une politique de sécurité adaptée à la plupart des installations Asterisk. Utilisez‑la comme point de départ et modifiez‑la selon vos besoins. La politique de sécurité proposée se trouve ci‑dessous :

1. Aucun port UDP/TCP inutile ouvert
2. Aucun accès à une interface d’administration (SSH/HTTPS) ouvert sur Internet.
3. Pour accéder à SSH et/ou HTTP/HTTPS, il doit y avoir des exceptions explicites dans le pare‑feu IPTABLES
4. Mots de passe forts de 12 caractères avec au moins un caractère spécial
5. Bannir les adresses IP échouant plus de 10 fois à l’authentification avec Fail2ban
6. Confirmation du mot de passe pour les appels internationaux
7. Limiter l’accès au port SIP à votre plage d’adresses IP connue

Si vous avez besoin d’un accès externe à votre PBX, deux possibilités s’offrent à vous. Utilisez un SBC (Session Border Controller) pour protéger votre serveur contre les attaques DOS/DDOS ou utilisez un VPN chaque fois que vous avez besoin d’un accès externe. Si vous laissez le port 5060 ouvert sur Internet sans SBC ni VPN, vous vous exposez à une attaque DOS/DDOS. Le risque vous incombe.

### PJSIP-era hardening (Asterisk 22)

Au‑delà du pare‑feu et de Fail2Ban, la pile PJSIP d’Asterisk 22 propose plusieurs contrôles au niveau de la configuration qui devraient faire partie de votre politique de sécurité. Ils complètent (et ne remplacent pas) les contrôles réseau ci‑dessus :

- **Per-endpoint authentication.** Every endpoint should reference a dedicated `type=auth` section with a strong, unique `password` (`auth_type=digest`). Never reuse credentials across endpoints.
- **Anonymous handling is built in.** PJSIP does not reveal whether a username exists when authentication fails. To accept anonymous calls at all you must explicitly create an endpoint named `anonymous` and use `type=identify` sections (matching on source IP) to map known peers to endpoints. If you do not want anonymous calls, simply do not create an `anonymous` endpoint, and unmatched requests are challenged/rejected.
- **ACLs.** Restrict who can reach an endpoint with `/etc/asterisk/acl.conf` named ACLs, referenced from the endpoint with `acl=` (signalling/source ACL) and `contact_acl=` (restricts the contact/registration address). You can also set permit/deny directly on the endpoint.
- **`qualify`.** Set `qualify_frequency` (and `qualify_timeout`) on the AOR so Asterisk actively monitors reachability of registered contacts and prunes dead ones.
- **PJSIP transport hardening / DoS protection.** The `type=transport` does not expose a per-transport client cap, so connection-flood protection comes from the firewall (the iptables/Fail2Ban rules in this chapter) rather than a PJSIP option. What the transport *does* give you is TCP keep-alive tuning (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) to reap dead/half-open connections, and `local_net`/`external_*` settings for correct NAT handling. Combine these with the firewall rules to blunt connection-flood attacks.
- **TLS + SRTP for media.** Encrypt signalling with a TLS transport and media with `media_encryption=sdes` (or `dtls` for WebRTC) on the endpoint — covered later in this chapter.
- **AMI/ARI access control.** Restrict the Asterisk Manager Interface (`manager.conf`) and ARI (`ari.conf` / `http.conf`) to localhost or a trusted management network, use strong unique secrets, bind the HTTP server to a private interface, and never expose these to the Internet.

All of the option names above are confirmed against Asterisk 22.10: the `type=transport` section exposes `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, and the `external_*` family, but it has **no** `max_clients` option — connection-flood protection comes from the firewall, not from the transport. The `acl` and `contact_acl` endpoint options take section names from `acl.conf`, and source-IP matching for unauthenticated peers is done with `type=identify` sections (`match=`).

### Removing unnecessary ports

Instead of

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

(In Asterisk 22 you no longer need to noload `chan_mgcp` or `chan_skinny` — those drivers were *removed* in Asterisk 21 and are not part of a stock 22 build.) With the instructions above, I have removed all unnecessary channels keeping only PJSIP. You can choose whatever protocol modules you want, just remove the unused ones. The result is shown in the screenshot below — only the SIP port (5060) bound by your PJSIP transport is now exposed inbound.

![netstat output after disabling the unused modules: only UDP port 5060 remains bound by Asterisk](../images/19-security-fig06.png)

### Mise en œuvre de la politique de sécurité avec IPTABLES

IPTABLES ou netfilter est un pare‑feu standard présent dans la plupart des distributions Linux. Dans ce laboratoire nous allons configurer iptables et fail2ban. L’objectif est d’appliquer la politique de sécurité recommandée pour Asterisk et de bloquer tout le trafic inutile. Suivez les étapes ci‑dessous :

1. Bloquer tout le trafic externe
2. Autoriser le trafic SSH depuis un réseau interne ou un hôte unique
3. Autoriser le trafic SIP en UDP et TCP sur les ports 5060
4. Autoriser le trafic RTP dans la plage de ports médias UDP. Il n’existe pas de valeur par défaut intégrée unique — le `rtp.conf` d’Asterisk revient aux ports 5000–31000 lorsqu’aucune configuration n’est définie, mais le `rtp.conf.sample` fourni configure `rtpstart=10000` / `rtpend=20000`, nous utilisons donc cet exemple de plage ici. Faites correspondre votre règle de pare‑feu à tout `rtpstart`/`rtpend` que vous avez réellement défini dans `rtp.conf`.

Assurez‑vous d’avoir un accès console au serveur, vous ne voulez pas vous bloquer hors du système. Soyez prudent.

1. Installez le paquet net-persistent.```
   sudo apt-get install iptables-persistent
   ```

2. Autoriser tout le trafic depuis la boucle locale```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. Autoriser les connexions établies```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. Autoriser le trafic SSH/HTTPS depuis le réseau 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Insérer les règles Asterisk```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   Notez que le port 5061 (SIP over TLS) est **TCP**, pas UDP. Les règles ci‑dessus ouvrent le 5060 à la fois en UDP et en TCP et le 5061 en TCP. Si vous n’utilisez que TLS, vous pouvez supprimer complètement les règles pour le 5060 en clair. Ouvrez uniquement les ports auxquels vos transports PJSIP se lient réellement.

   `-I` signifie PREPEND

6. La dernière règle doit être un drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` signifie APPEND. Note : Faites attention lors de la maintenance de nouvelles règles, vous devez ajouter les règles avant le DROP. Utilisez PREPEND pour les nouvelles règles `-I`

7. Enregistrez les règles et redémarrez iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Utilisation de Fail2Ban pour bloquer plusieurs tentatives d'authentification échouées

Fail2Ban est presque une norme pour Asterisk. La plupart des utilisateurs l'implémentent pour renforcer la sécurité. Cet utilitaire analyse les journaux d'Asterisk à la recherche de tentatives échouées et bannit les adresses IP des attaquants. Ci‑dessous, je fournis les instructions pour installer Fail2Ban.

Dans Asterisk 22, PJSIP signale les authentifications échouées et d'autres événements de sécurité via le **cadre d'événements de sécurité** d'Asterisk, écrit dans le canal de journal dédié **`security`**. Pour que Fail2Ban fonctionne, vous devez :

1. Activer le canal de sécurité dans `/etc/asterisk/logger.conf`. La syntaxe est `<filename> => <levels>`, donc pour envoyer le niveau de sécurité vers un fichier nommé `security` écrivez :

```
[logfiles]
security => security
```

exécutez `logger reload` depuis la CLI. Cela produit `/var/log/asterisk/security` avec une ligne par événement de sécurité, sous la forme:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

Les événements que Fail2Ban surveille sont `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID` et `FailedACL`, chacun contenant un champ `RemoteAddress="IPV4/UDP/<ip>/<port>"` qui identifie l’auteur de l’infraction. (Notez que l’adresse est encapsulée sous la forme `IPV4/UDP/.../...`, et non comme une simple IP — votre filtre doit extraire l’hôte à l’intérieur de cette chaîne.)

2. Pointez la prison `asterisk` vers ce fichier (`logpath = /var/log/asterisk/security`) et utilisez un filtre qui analyse ce format d’événement de sécurité.

Les versions récentes de Fail2Ban incluent un filtre `asterisk` dont le `failregex` correspond déjà aux événements ci‑dessus et extrait `<HOST>` du champ `RemoteAddress`, par exemple :

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX distributions (FreePBX/Sangoma) ship equivalent filters. Prefer the packaged filter over hand‑writing one, since the exact event strings are version‑dependent. One caveat to be aware of: a now‑patched advisory (GHSA-5743-x3p5-3rg7) showed that crafted PJSIP traffic could inject fake log lines — keep both Asterisk and your Fail2Ban filter current.

Below I provide the instructions to install Fail2Ban

1. Install fail2ban on Linux```
   sudo apt-get install fail2ban
   ```

2. Activer fail2ban pour Asterisk et SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   Ajoutez les lignes suivantes pour activer fail2ban pour ssh et asterisk```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. Redémarrer fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Vérifiez. Changez le secret de votre softphone et essayez de vous réenregistrer 10 fois. En utilisant `iptables -L`, vérifiez si l’adresse du softphone a été incluse comme adresse bloquée.  
5. Supprimez l’adresse du bannissement (supposons que l’adresse soit 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note : Dans la commande, remplacez 192.168.0.5 par l'adresse IP de votre téléphone

### Implémentation de TLS et SRTP

Je vais diviser cette section en deux parties. Dans la première, nous aborderons TLS pour chiffrer la signalisation et, dans la seconde, SRTP pour chiffrer les médias. L'objectif ici est de configurer Asterisk pour ces ressources.

#### TLS

TLS (Transport Layer Security) est le mécanisme de chiffrement défini pour protéger la signalisation SIP. Le tableau ci‑dessous résume les attaques contre lesquelles TLS protège :

| Type d'attaque | Protégé ? | Remarques |
|----------------|-----------|-----------|
| Attaques sur la signalisation | Oui | TLS assure l'intégrité des messages |
| Attaque de l'homme du milieu | Oui | TLS vérifie le certificat du serveur |
| Écoute clandestine | Non | TLS chiffre la signalisation, pas les médias |

Pour le chiffrement des médias (voix/vidéo), utilisez SRTP.

#### Certificats numériques auto‑signés

Il existe deux types de certificats : auto‑signés et commerciaux. Les certificats auto‑signés sont signés par votre propre serveur tandis que les certificats commerciaux sont signés par une autorité externe. Pour la VoIP, vous pouvez être votre propre autorité de certification. Il n’est pas nécessaire d’obtenir un certificat externe tel que GoDaddy ou Verisign, ce qui représente une dépense inutile. Nous allons générer nos propres certificats à l’aide de `ast_tls_cert`.

#### Configuration de TLS avec des certificats auto‑signés

Voici un guide étape par étape pour implémenter TLS. Nous générons d’abord les certificats, puis configurons le transport TLS de PJSIP (voir « Configuring TLS with chan_pjsip »), et enfin nous pointons le softphone vers celui‑ci. Nous utiliserons le SipPulse Softphone, qui supporte nativement TLS et SRTP. (Tout softphone SIP compatible TLS/SRTP fonctionne de la même manière.)

**Étape 1.** Créez une clé RSA privée en utilisant le chiffrement 3DES d’une longueur de 4096 bits pour notre autorité de certification. La commande ci‑dessous, présente dans `/usr/src/asterisk-22.x.y/contrib/scripts`, créera l’Autorité de Certification et le Certificat Asterisk. Comme d’habitude, adaptez les instructions si nécessaire, les versions changent, les répertoires changent. Veuillez faire attention à ce que vous faites. Utilisez votre domaine ou adresse IP dans l’option `-C`. La commande `ast_tls_cert` possède trois options.

- `-C` hôte ou adresse IP (j’ai utilisé 192.168.0.74, l’adresse IP de ma VM)
- `-O` nom de l’organisation
- `-d` répertoire où stocker les clés

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

Je ne vais pas générer de certificat client car nous n’allons pas utiliser le certificat pour authentifier le client. Le client n’est pas tenu de présenter son propre certificat.

**Step 2.** Configurez Asterisk pour prendre en charge notre client via TLS. Cela se fait dans `pjsip.conf` (un transport TLS plus les paramètres de l’endpoint) — la configuration complète est présentée dans la section suivante, « Configuring TLS with chan_pjsip ». Nous n’authentifions pas à l’aide de certificats, nous chiffrons simplement le trafic.

**Step 3.** Installez un softphone SIP compatible TLS (l’auteur utilise le SipPulse Softphone).

**Step 4.** Copiez l’autorité de certification sur l’ordinateur exécutant le softphone. Après l’avoir installé, copiez le fichier `/etc/asterisk/keys/ca.crt` sur l’ordinateur exécutant le softphone (utilisez scp, ou WinSCP sous Windows) si vous utilisez un certificat auto‑signé.

**Step 5.** Créez le compte dans le softphone. Dans l’écran du compte, ajoutez le compte normalement comme n’importe quel autre compte sip. Utilisez le bon mot de passe, l’authentification repose toujours sur le mot de passe.

**Step 6.** Définissez TLS comme transport dans les paramètres du compte. Dans l’écran du compte du SipPulse Softphone (ci‑dessous), choisissez **TLS** comme transport et utilisez le port 5061. Ajustez votre pare‑feu pour ouvrir le port TCP 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** Faites confiance à l’autorité de certification. Si le certificat TLS d’Asterisk est signé par une CA publique (par exemple Let’s Encrypt — voir le chapitre *Deployment*), un softphone moderne tel que le SipPulse Softphone le fait confiance automatiquement via le magasin de certificats du système, sans importation manuelle. Si vous utilisez un certificat auto‑signé, importez son CA (`/etc/asterisk/keys/ca.crt`) dans le client ou le magasin de confiance du système d’exploitation, ou acceptez‑le lorsqu’on vous le demande.

**Step 8.** Vous **n’avez pas** besoin d’un certificat client. Une idée reçue courante est que chaque téléphone a besoin de son propre certificat pour s’authentifier — ce n’est pas le cas. À ce stade, Asterisk ne fait que *chiffrer* la session ; l’authentification repose toujours sur le nom d’utilisateur et le mot de passe. Asterisk ne vérifie pas les certificats client par défaut, il n’est donc pas nécessaire de distribuer un certificat par client.

**Step 9.** Après avoir modifié le certificat ou le transport, redémarrez complètement le softphone (quittez‑le et relancez‑le, pas seulement fermez la fenêtre) afin qu’il se reconnecte via le nouveau transport.

### Configuring TLS with chan_pjsip

Voyons maintenant comment configurer PJSIP pour TLS. PJSIP est le seul canal SIP dans Asterisk 22, il n’y a donc rien à changer — assurez‑vous simplement que `res_pjsip`, `res_pjproject` et `chan_pjsip` sont chargés. Étape 1 : confirmez que PJSIP est activé dans /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Étape 2 : Configurer PJSIP pour prendre en charge TLS. Ajouter une section pour le transport TLS dans le fichier /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Utilisez `method=tlsv1_2` (ou `tlsv1_3` si votre compilation OpenSSL/PJSIP le prend en charge) — TLS 1.0/1.1 sont obsolètes et peu sûrs et ne doivent pas être utilisés.

Étape 3 : Configurez le point de terminaison pour blink. Modifiez `pjsip.conf` et modifiez la section pour blink. Laissez PJSIP choisir le transport automatiquement.

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

Étape 4 : Vérification. Pour vérifier que l’enregistrement a eu lieu via TLS, utilisez la commande suivante dans la console Asterisk.

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

Le protocole responsable du chiffrement des médias est le Secure Real Time Protocol (SRTP) défini dans la RFC3711. L’un des inconvénients du protocole est l’absence d’une méthode standardisée pour l’échange de clés. Asterisk utilise l’échange de clés SDES via le protocole SDP, protégé par le chiffrement de signalisation fourni par TLS. Il existe également d’autres méthodes telles que MIKEY et ZRTP. ZRTP, développé par Philipp Zimmermann, est l’une des méthodes les plus sophistiquées d’échange de clés et de chiffrement des médias. Certains softphones et téléphones matériels prennent en charge ZRTP. Cependant, la méthode standard reste SDES et vous la trouverez dans presque tous les téléphones disponibles sur le marché. Ci‑dessous un exemple de requête avec les clés crypto définies dans le SDP aux lignes a=crypto:1 et a=crypto:2.

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

#### Configuration de SRTP sur Asterisk

Configurer SRTP sur Asterisk est très simple. Définissez `media_encryption=sdes` sur le point de terminaison ; vous pouvez également l’exiger avec `media_encryption_optimistic=no` afin que les médias non chiffrés soient rejetés plutôt que silencieusement autorisés. Notez que SDES nécessite que la signalisation s’exécute sur TLS afin que les clés ne soient pas envoyées en clair.

**Étape 1.** Configuration d'Asterisk

Définissez ce qui suit dans la section `type=endpoint` de `pjsip.conf`:

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

**Étape 2.** Configuration du softphone

Dans le softphone, activez SRTP pour les médias du compte (définissez l’option **SRTP (Media Encryption)** sur *Mandatory*) afin que la voix soit chiffrée.

![Les paramètres du compte SipPulse Softphone (section inférieure) — définissez **Transport** sur TLS et **SRTP (Media Encryption)** sur *Mandatory* afin que la signalisation et les médias soient tous deux chiffrés.](../images/softphone/sipphone-config.png){width=35%}

## Activation de l’authentification à deux facteurs pour les appels internationaux

Parfois, la meilleure solution consiste à ne pas disposer de routes internationales. Cependant, si vous devez vraiment composer à l’international, utilisez un mot de passe supplémentaire. Nous allons utiliser l’application Asterisk **vmauthenticate** pour demander le mot de passe de la messagerie vocale avant de composer un appel international. Cette configuration se trouve dans le dialplan du fichier **extensions.conf**. Voir l’exemple ci‑dessous. Ainsi, même si un hacker découvre le mot de passe d’un pair ou compromet un téléphone, il aura toujours besoin du mot de passe de la messagerie vocale pour appeler cette destination.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` reste une application standard dans Asterisk 22. Le `Dial()` ci‑dessus dirige l’appel via un trunk SIP/PJSIP (`PJSIP/<number>@<trunk>`), qui est la façon dont la plupart des installations modernes accèdent au PSTN — adaptez `my_trunk` à votre propre nom de trunk, et utilisez `DAHDI/g1/...` uniquement si vous avez réellement un span DAHDI. La défense contre la fraude tarifaire dans le dialplan — un second facteur comme celui‑ci, combiné à la restriction des contextes pouvant atteindre vos routes sortantes et internationales — reste l’une des protections les plus importantes que vous puissiez déployer.

## Résumé

Dans ce chapitre, vous avez découvert les risques liés à la connexion d’un IP PBX à Internet. Nous avons ensuite vu comment protéger notre PBX en mettant en place une politique de sécurité. Dans cette politique, nous avons implémenté iptables, fail2ban, TLS, SRTP et une authentification à double facteur pour les appels internationaux. J’espère que ce chapitre vous a plu.

## Quiz

1. Quelle est la contre‑mesure la plus importante contre la fraude de partage de revenus sur Internet ?
   - A. Implémenter SRTP
   - B. Garder Asterisk à jour
   - C. Implémenter TLS
   - D. Utiliser des mots de passe forts
2. Le fuzzing SIP est défini comme :
   - A. Une attaque DoS utilisant des requêtes et réponses malformées
   - B. Un vol de service où les mots de passe sont forcés par bruteforce
   - C. Une écoute clandestine des appels en cours
   - D. Un DDoS avec un flot de requêtes SIP
3. TFTPTheft se produit lorsque le serveur fournit des fichiers de configuration via TFTP. Vous pouvez l’éviter en utilisant :
   - A. FTP
   - B. HTTP
   - C. HTTPS avec nom d’utilisateur et mot de passe
   - D. SCP
4. Les attaques de type homme‑du‑milieu utilisent une technique appelée :
   - A. TFTP theft
   - B. ARP spoofing
   - C. MAC poisoning
   - D. dsniff
5. Pour SRTP, Asterisk utilise le système suivant pour échanger les clés :
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. L’utilitaire qui génère l’autorité de certification et les certificats, trouvé dans `/usr/src/asterisk-22.x.y/contrib/scripts`, est :
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. Stratégies valides pour empêcher l’écoute clandestine (cochez tout ce qui s’applique) :
   - A. Implémenter des détecteurs d’écoute analogiques
   - B. Utiliser l’utilitaire ARPwatch pour détecter l’ARP spoofing
   - C. Activer la détection d’ARP‑spoofing dans les commutateurs
   - D. Utiliser SRTP
8. Asterisk prend en charge une authentification forte en vérifiant les certificats clients. (Le transport TLS de PJSIP peut exiger et vérifier le certificat du client.)
   - A. Vrai
   - B. Faux
9. Sur Asterisk 22, quel paramètre d’endpoint PJSIP active le chiffrement média SRTP en utilisant des clés in‑SDP (SDES) ?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. Dans Asterisk 22, Fail2Ban doit lire les événements d’authentification échouée PJSIP depuis le canal de journal dédié ________ (activé dans `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
