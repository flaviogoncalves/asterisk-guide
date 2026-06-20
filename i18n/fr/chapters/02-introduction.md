# Introduction à Asterisk PBX

La popularité des distributions prêtes à l’emploi telles que FreePBX et Issabel a récemment augmenté. Dans ce livre, nous couvrirons l’Asterisk classique, qui constitue la base pour comprendre ces distributions. Asterisk PBX est un logiciel open‑source capable de transformer un PC ordinaire en un puissant PBX multiprotocole. Dans ce chapitre, nous découvrirons les possibilités de cette nouvelle technologie et son architecture de base.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Expliquer ce qu’est Asterisk et ce qu’il fait ;
- Décrire le rôle de Digium™ et de son successeur Sangoma ;
- Reconnaître l’architecture de base d’Asterisk et ses composants ;
- Identifier plusieurs scénarios d’utilisation ; et
- Identifier les sources d’information et d’aide.

## What is Asterisk

Asterisk est un logiciel PBX open‑source qui transforme un ordinateur ordinaire en un PBX complet pour les utilisateurs domestiques, les entreprises, les fournisseurs de services VoIP et les opérateurs téléphoniques. Asterisk est également à la fois une communauté open‑source et un projet sponsorisé par Sangoma Technologies (qui a acquis Digium en 2018). Vous êtes libre d’utiliser et de modifier Asterisk pour répondre à vos besoins. Asterisk permet la connectivité en temps réel entre les réseaux PSTN et VoIP. Puisqu’Asterisk est bien plus qu’un PBX, vous bénéficiez non seulement d’une mise à niveau exceptionnelle de votre PBX existant, mais vous pouvez également faire de nouvelles choses en téléphonie, telles que :

- Connecter les employés travaillant à domicile à un PBX de bureau via Internet haut débit ;
- Relier plusieurs bureaux situés à différents endroits via un réseau IP, un réseau privé ou même via Internet lui‑même ;
- Offrir à vos employés une messagerie vocale intégrée au web et au courriel ;
- Créer des applications comme des IVR qui permettent des connexions à votre système de commande ou à d’autres applications ;
- Donner aux utilisateurs en déplacement un accès au PBX de l’entreprise depuis n’importe où avec une simple connexion haut débit ou VPN ; et
- bien plus encore....

Asterisk comprend plusieurs ressources avancées auparavant réservées aux systèmes haut de gamme, telles que :

- Musique pour les clients en attente dans les files d’attente, avec prise en charge du streaming multimédia et des fichiers MP3 ;
- Files d’attente d’appels, permettant à une équipe d’agents de répondre aux appels et de surveiller les files ;
- Intégration avec la synthèse vocale et la reconnaissance vocale ;
- Enregistrements détaillés transférés à la fois vers des fichiers texte et des bases de données SQL ; et
- Connectivité PSTN via des lignes numériques et analogiques.

## Qu’est‑ce que AsteriskNOW (Historique) et FreePBX

Asterisk dans sa forme la plus pure, également appelé « classic asterisk » (dénomination du paquet Debian), est considéré davantage comme un outil de développement qu’un produit fini en soi. AsteriskNOW était une initiative visant à transformer Asterisk en une soft‑appliance. La distribution incluait CentOS comme système d’exploitation et FreePBX comme interface graphique. AsteriskNOW a depuis été abandonné.

Aujourd’hui, la distribution clé en main standard d’Asterisk est **FreePBX** (maintenue par Sangoma), qui regroupe Asterisk avec une interface d’administration web et un écosystème de modules. FreePBX est licencié sous la GPL et peut être téléchargé librement depuis www.freepbx.org. Pour les déploiements commerciaux, Sangoma propose également **FreePBX Distro** (une image Linux complète) et son produit commercial **PBXact**.

## Rôle de Digium™ et Sangoma

Digium, une entreprise située à Huntsville, Alabama, a été le créateur et le principal développeur d’Asterisk depuis sa fondation en 1999. En plus d’être le principal sponsor du développement d’Asterisk, Digium produisait des cartes d’interface téléphonique et d’autres matériels pour les PBX Asterisk, et créait des produits commerciaux tels que Switchvox (destiné au marché des PME). En 2018, Digium a été acquis par **Sangoma Technologies**, une société canadienne de communications unifiées. Depuis l’acquisition, Sangoma continue de sponsoriser le développement d’Asterisk et en assure la gouvernance principale, maintenant le projet open‑source sur www.asterisk.org.

Historiquement, Digium proposait Asterisk sous trois types d’accords de licence :

- General Public License (GPL) Asterisk. C’est la version la plus utilisée. Elle comprend toutes les fonctionnalités et est libre d’utilisation et de modification selon les termes de la licence GPL.
- Asterisk Business Edition était une version commerciale d’Asterisk. Certaines entreprises utilisaient l’édition business parce qu’elles ne souhaitaient pas ou ne pouvaient pas utiliser la licence GPL — généralement parce qu’elles ne voulaient pas publier leur code source avec Asterisk. **Note :** Asterisk Business Edition a été abandonnée ; aujourd’hui Asterisk est distribué uniquement sous la GPL.
- Asterisk OEM licensing. Après que Digium a cessé de vendre Asterisk Business Edition au détail, elle a continué à licencier cette édition commerciale aux clients OEM — les fournisseurs d’équipement qui souhaitaient créer des produits propriétaires sur la base d’Asterisk sans publier leur propre code source sous la GPL.

### Le projet Zapata et sa relation avec Asterisk

Le projet Zapata a été développé par Jim Dixon, qui était également responsable de la conception matérielle révolutionnaire utilisée avec Asterisk. Le matériel est également open‑source ; à ce titre, il peut être utilisé par n’importe quelle entreprise, et aujourd’hui plusieurs fabricants produisent des cartes compatibles avec cette architecture.

Le projet Zapata a produit une architecture appelée Zaptel, rebaptisée plus tard DAHDI (Digium/Asterisk Hardware Device Interface). L’un des principaux avantages de cette architecture est la capacité d’utiliser le CPU du PC pour traiter le flux média, l’annulation d’écho et le transcodage. En revanche, la plupart des cartes existantes utilisent des processeurs de signal numérique (DSP) pour effectuer ces tâches. L’utilisation du CPU du PC au lieu de DSP dédiés réduit considérablement le prix de la carte. Ainsi, ces cartes sont nettement moins chères que les interfaces précédemment disponibles chez d’autres fabricants. D’un autre côté, ces cartes exigent beaucoup de CPU ; une mauvaise utilisation du CPU du PC peut affecter fortement la qualité vocale. Récemment, Digium a lancé une carte coprocessor qui utilise des DSP pour encoder et décoder G.729 et G.723, permettant une meilleure évolutivité pour un grand nombre de canaux.

## Pourquoi Asterisk ?

Je me souviens de mon premier contact avec Asterisk. En général, la première réaction face à quelque chose de nouveau—surtout lorsqu’il concurrence ce que vous connaissez déjà—est de le rejeter ! C’est exactement ce qui s’est passé en 2003. Asterisk était en concurrence avec une solution que je vendais à un client (passerelle VoIP 4 E1), et il était dix fois moins cher que ce que je facturais pour la solution que je maîtrisais. Ce prix disproportionné m’a poussé à étudier Asterisk afin d’identifier les éventuels pièges et inconvénients. Par exemple, j’ai découvert que le CPU du PC à l’époque ne pouvait pas supporter 120 sections g.729 simultanées ; au final, j’ai remporté la proposition avec ma solution de passerelle.

Cependant, cet exercice m’a conduit à la découverte qu’Asterisk pouvait résoudre une variété de problèmes très coûteux pour ma clientèle. Nous avions des devis onéreux pour les IVR, la messagerie unifiée, l’enregistrement d’appels et les composeurs ; avec un dimensionnement approprié, les problèmes de CPU pouvaient être contournés. En effet, en seulement trois ans, Asterisk est devenu le produit phare de mon entreprise (j’ai même décidé de créer une autre société uniquement pour l’activité Asterisk). À mon avis, Asterisk est une révolution dans les télécommunications qui représente pour la téléphonie IP ce qu’Apache représente pour les services web.

### Réduction de coûts extrême

Si vous comparez un PBX traditionnel avec Asterisk en ce qui concerne les interfaces numériques et les téléphones, Asterisk est légèrement moins cher que ces PBX. Cependant, Asterisk devient réellement rentable lorsque vous ajoutez des fonctionnalités avancées telles que la messagerie vocale, l’ACD, l’IVR et le CTI. Avec ces fonctionnalités avancées, Asterisk devient nettement moins cher que les PBX traditionnels. En fait, comparer les PBX Asterisk avec des PBX analogiques bas de gamme est injuste, car Asterisk offre tant de fonctionnalités indisponibles sur les systèmes analogiques bas de gamme.

### Contrôle du système téléphonique et indépendance

L’un des bénéfices le plus souvent cités par les clients d’Asterisk est l’indépendance qu’il procure. Certains fabricants d’aujourd’hui ne donnent même pas au client le mot de passe du système ou la documentation de configuration. Avec l’approche « do‑it‑yourself » d’Asterisk, l’utilisateur obtient une liberté totale ; en prime, il a accès à une interface standard.

### Environnement de développement facile et rapide

Asterisk peut être étendu à l’aide de langages de script comme PHP et Perl avec les interfaces AMI et AGI. Asterisk est open‑source, et son code source peut être modifié par l’utilisateur. Le code source est principalement écrit en langage de programmation ANSI C.

### Richesse fonctionnelle

Asterisk possède plusieurs fonctionnalités qui sont soit absentes, soit optionnelles dans les PBX traditionnels (par ex., messagerie vocale, CTI, ACD, IVR, musique d’attente intégrée et enregistrement). Le coût de ces fonctionnalités sur certaines plateformes dépasse le prix même de la plateforme.

### Contenu dynamique sur le téléphone

Asterisk est programmé en langage C et d’autres langages courants dans l’environnement de développement actuel. La possibilité de fournir du contenu dynamique est pratiquement illimitée.

### Plan de numérotation flexible et puissant

Une autre percée d’Asterisk est son plan de numérotation puissant. Dans les PBX traditionnels, même des fonctionnalités simples comme le routage au moindre coût (LCR) sont soit impossibles, soit optionnelles. Avec Asterisk, choisir la meilleure route est simple et propre.

### Open‑source fonctionnant sur Linux

L’une des plus grandes forces d’Asterisk est sa communauté. Plusieurs ressources sont disponibles, notamment la documentation officielle d’Asterisk (docs.asterisk.org), le wiki communautaire VoIP‑Info (www.voip-info.org <http://www.voip-info.org>), les listes de diffusion e‑mail et les forums. À mesure qu’Asterisk est de plus en plus adopté, les bugs sont découverts et corrigés rapidement. Avec une large base d’utilisateurs et une équipe de développement active, Asterisk figure parmi les plateformes PBX les plus largement testées au monde, ce qui contribue à maintenir le code stable et mature.

### Limitations de l’architecture d’Asterisk

Certaines limitations d’Asterisk proviennent de

## Principales objections à Asterisk PBX

Il est fréquent d’entendre des objections à l’adoption d’Asterisk, que nous aborderons ici.

### La part de marché d’Asterisk est trop petite

La part de marché est généralement mesurée par le nombre de PBX vendus. Ces statistiques sont généralement obtenues auprès des plus grands distributeurs. Asterisk est un logiciel libre qui peut être téléchargé et déployé sans qu’aucune vente ne soit enregistrée, il est donc systématiquement sous‑décompté dans ces chiffres. Même ainsi, Asterisk alimente une très grande base installée dans le monde — des PBX de bureau à serveur unique aux déploiements de grands opérateurs et centres de contact — et reste le moteur dominant derrière l’écosystème des PBX open‑source (y compris les distributions clés en main telles que FreePBX).

### S’il est gratuit, comment le fabricant survit‑il ?

En fait, il n’existe pas de fabricant de logiciel open‑source au sens traditionnel. Digium a développé Asterisk depuis 1999, se finançant grâce à la vente de cartes d’interface téléphonique, de produits PBX commerciaux tels que Switchvox, et de logiciels associés. En 2018, Sangoma Technologies a acquis Digium. Sangoma continue de financer le développement d’Asterisk et génère des revenus grâce aux produits commerciaux (modules commerciaux FreePBX, PBXact, Switchvox), aux ventes de matériel et aux services professionnels.

### Il est difficile de trouver du support technique !

Sangoma fournit un support technique commercial pour Asterisk via son écosystème de partenaires et directement via ses offres de produits. Un réseau mondial de professionnels certifiés assure le support de première ligne et les services professionnels. Le support communautaire reste actif grâce aux forums Asterisk et aux listes de diffusion sur www.asterisk.org.

### Asterisk supporte‑t‑il plus de 200 extensions ?

Oui, absolument. Un serveur Asterisk bien dimensionné peut gérer un grand nombre d’extensions, et Asterisk s’étend davantage en répartissant les utilisateurs sur plusieurs serveurs avec équilibrage de charge et basculement, permettant des déploiements multi‑sites de grande envergure.

### Seuls les « geeks » peuvent installer Asterisk

Avec FreePBX (disponible en tant que distribution autonome de Sangoma), même les professionnels ayant des connaissances limitées en Linux peuvent installer et configurer un PBX de complexité moyenne. Grâce à une interface graphique, il est possible de configurer un PBX complet en quelques heures seulement.

### Que se passe‑t‑il si le serveur tombe en panne ?

L’un des principaux avantages d’Asterisk est sa capacité à fonctionner dans des systèmes tolérants aux pannes. Il est relativement simple et peu coûteux d’avoir deux serveurs fonctionnant en parallèle. Je vous mets au défi d’essayer cela avec un PBX conventionnel !

### Notre entreprise n’utilise pas de logiciel open‑source

Votre entreprise utilise probablement des logiciels open‑source sans même s’en rendre compte. De nombreux appareils utilisent Linux comme système d’exploitation. De plus, le support commercial et les déploiements gérés sont disponibles auprès de Sangoma et de son réseau de partenaires certifiés.

### Utiliser le CPU du PC pour traiter la signalisation et les médias n’est pas recommandé

Asterisk utilise le CPU du serveur pour traiter la signalisation et les médias des canaux voix au lieu d’utiliser des DSP dédiés. Bien que cela permette une réduction de coût pouvant atteindre cinq fois, cela rend le système dépendant des performances du CPU principal. Avec un dimensionnement correct, Asterisk est capable de gérer de gros volumes. Si vous souhaitez tout de même libérer le CPU principal de ces tâches, vous pouvez également recourir à la suppression d’écho matérielle et même à des cartes de transcodage, comme la Sangoma (anciennement Digium) TC400B basée sur des DSP.

## Asterisk Architecture

This section will explain how Asterisk’s architecture works. The figure below shows the basic Asterisk architecture. Next, we will explain architecture-related concepts, including channels, codecs, and applications.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

A channel is the equivalent of a telephone line, but in a digital format. It usually consists of an analog or digital (TDM) signaling system or a combination of codec and signaling protocol (e.g., SIP-GSM, IAX-uLaw). Initially, all telephony connections were analog and susceptible to echo and noise. Later, most systems were converted to digital systems, with the analogical sound converted into a digital format using pulse code modulation (PCM) in most cases. This format allows voice transmission in 64 kilobits/second without compression.

Channels interfacing with the Public Switched Telephone Network (PSTN):

- `chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards from Sangoma (formerly Digium), Xorcom, and others. Built separately against DAHDI — see the *Legacy channels* chapter.

Channels interfacing with Voice over IP:

- `chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS. Dial string: `PJSIP/endpoint_name`. (**Note:** the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22. See *Building your first PBX with PJSIP* for configuration.)
- `chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy; SIP/PJSIP is preferred for new deployments. Dial string: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support) but rarely used.

The older VoIP channels are no longer part of a standard Asterisk 22 build: `chan_h323` (H.323) survives only as the community `ooh323` add-on, and `chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set. If you must interwork with those protocols, a gateway in front of Asterisk is the usual approach.

Miscellaneous channels:

- **Local**: a pseudo-channel (built into the core) that loops back into the dial plan in a different context — useful for recursive routing and for fanning a call out to multiple destinations. Dial string: `Local/extension@context`.

### Codec and codec translation

We usually try to put as many voice connections as possible in a data network. Codecs enable new features in digital voice, including compression, which is one of the most important features as it allows compression rates larger than 8 to 1. Many codecs also define features such as voice activity detection (silence suppression), packet loss concealment, and comfort noise generation, though Asterisk itself does not generate comfort noise or perform silence suppression. Several codecs are available for Asterisk and can be transparently translated from one to another. Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another. Some codecs in Asterisk are supported only in pass-through mode; these codecs cannot be translated. To verify which codecs are installed in your system, you can use the console command:

```
CLI>core show translation
```

Les codecs suivants sont pris en charge :

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (Haute Définition) – (64 Kbps)
- G.723.1 - Mode uniquement en passage direct
- G.726 - (16/24/32/40 kbps)
- G.729 - Module de codec binaire distribué par Sangoma ; le téléchargement est gratuit, mais une utilisation légale nécessite l’achat d’une licence par canal (8 Kbps)
- GSM - (12‑13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2,4 Kbps)
- Speex - (2,15‑44,2 Kbps)
- Opus - (6‑510 Kbps)

### Protocoles

Faire transiter les données d’un téléphone à un autre devrait être simple, à condition que les données trouvent d’elles‑mêmes un chemin vers l’autre téléphone. Malheureusement, ce n’est pas le cas, et un protocole de signalisation est nécessaire pour établir les connexions entre téléphones, découvrir les appareils terminaux et mettre en œuvre la signalisation téléphonique. SIP est le protocole de signalisation dominant dans les déploiements modernes et est le seul canal SIP disponible dans Asterisk 22 LTS (via chan_pjsip). IAX2 est encore disponible mais considéré comme hérité. Asterisk prend en charge les protocoles suivants.

- SIP — via `chan_pjsip`
- IAX2 — hérité, toujours fourni avec Asterisk 22
- UNISTIM — téléphones Nortel/Avaya (support étendu)
- H.323, MGCP et SCCP (Cisco Skinny) — protocoles hérités ne figurant plus dans une version standard d’Asterisk 22 (H.323 uniquement via le module communautaire `ooh323`)

### Applications

Pour relier des appels d’un téléphone à un autre, l’application dial() est utilisée. La plupart des fonctionnalités d’Asterisk (par ex., la messagerie vocale et la conférence) sont implémentées sous forme d’applications. Vous pouvez voir les applications Asterisk disponibles en utilisant la commande console core show applications.

```
CLI>core show applications
```

Vous pouvez ajouter des applications provenant des modules complémentaires d'Asterisk, de fournisseurs tiers, ou même celles que vous développez vous‑même.

## Vue d'ensemble d'un système Asterisk

Asterisk est une PBX open‑source qui agit comme une PBX hybride, intégrant des technologies telles que la téléphonie TDM et IP. Asterisk est prête à implémenter des fonctionnalités telles que la réponse vocale interactive (IVR) et la distribution automatique des appels (ACD) ; de plus, comme mentionné précédemment, elle est ouverte au développement de nouvelles applications. Cette figure montre comment Asterisk se connecte au PSTN et aux PBX existantes en utilisant des interfaces analogiques et numériques ainsi qu’en supportant les téléphones analogiques et IP. Elle peut fonctionner comme un soft‑switch, une passerelle média, une messagerie vocale et une conférence audio et possède également de la musique d’attente intégrée.

![Vue d'ensemble d'un système Asterisk](../images/01-introduction-fig02.png)

## Comparaison de l’ancien et du nouveau monde

Dans l’ancien modèle de SoftSwitch, tous les composants étaient vendus séparément, ce qui signifiait que vous deviez acheter chaque composant individuellement puis l’intégrer à l’environnement PBX ou SoftSwitch. Les coûts et les risques étaient élevés et la plupart du matériel était propriétaire.

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### Téléphonie avec Asterisk

Toutes les fonctions sont intégrées dans la plateforme Asterisk dans le même ou dans différents boîtiers selon le dimensionnement, et toutes sont sous licence GPL. Parfois il est plus simple d’installer Asterisk que de licencier certains des IP‑PBX grand public

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## Construire un système de test

Lors de la mise en œuvre d’une solution Asterisk, notre première étape consiste généralement à construire un système de test. L’objectif est un **PBX 1×1** minimal — un téléphone pouvant appeler un autre — afin de pouvoir essayer les endpoints, le dialplan et les fonctionnalités avant de toucher à la production. Aujourd’hui, tout cela est purement logiciel : aucun matériel téléphonique n’est nécessaire.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### La méthode moderne : un laboratoire logiciel (recommandé)

Le système de test le plus rapide est Asterisk 22 exécuté dans un conteneur ou une machine virtuelle, avec des **softphones** pour les endpoints et, éventuellement, un **SIP trunk** pour atteindre le réseau public :

- **Asterisk 22** sur une petite boîte Linux, VM ou conteneur Docker. Ce livre fournit un laboratoire Docker prêt à l’emploi (voir le guide du laboratoire) qui démarre un Asterisk 22 entièrement configuré avec une seule commande — aucune compilation, aucun matériel.
- **Deux softphones** enregistrés comme endpoints PJSIP, afin de pouvoir passer un appel réel entre eux. Tout au long de ce livre, nous utilisons le **SipPulse Softphone** (téléchargement gratuit : <https://www.sippulse.com/produtos/softphone>), disponible pour ordinateur de bureau et mobile.
- **Un SIP trunk** (optionnel) d’un fournisseur VoIP, pour quand vous souhaitez atteindre le PSTN. Pas de carte et pas de ligne analogique — seulement des identifiants.

C’est ainsi que chaque exemple de ce livre est construit et vérifié, et vous pouvez le reproduire sur n’importe quel ordinateur portable.

### La méthode héritée : cartes analogiques/numériques

Avant le VoIP, un PBX de test nécessitait des interfaces physiques : un port **FXO** pour se connecter à une ligne téléphonique existante et un port **FXS** pour brancher un téléphone analogique, ce qui, ensemble, vous donnait un PBX 1×1. Une seule carte portant une interface FXO et une interface FXS était le kit de démarrage classique. Ces cartes basées sur DAHDI (de Sangoma, anciennement Digium) existent encore pour les sites qui doivent terminer des lignes analogiques ou T1/E1, mais elles sont aujourd’hui de niche — la plupart des déploiements sont purement VoIP. Si vous avez seulement besoin de connecter des téléphones ou lignes analogiques, consultez le chapitre *Legacy Channels* ; sinon, vous pouvez ignorer complètement le matériel téléphonique.

## Scénarios Asterisk

Asterisk peut être utilisé dans plusieurs scénarios différents. Nous en listerons quelques-uns et expliquerons les avantages ainsi que les éventuelles limitations de chacun.

### IP PBX

Le scénario le plus courant est l'installation d'un nouveau ou le remplacement d'un PBX existant. Si vous comparez Asterisk avec d'autres alternatives, vous constaterez qu'il est moins cher et plus riche en fonctionnalités que la plupart des PBX actuellement disponibles sur le marché. Plusieurs entreprises modifient désormais leurs spécifications pour Asterisk au lieu d'autres PBX de marques.

![Asterisk en tant que IP PBX](../images/01-introduction-fig06.png)

### Activation IP des PBX hérités

L'image suivante illustre l'une des configurations les plus couramment utilisées. Les grandes entreprises ne souhaitent généralement pas prendre de risques importants lorsqu'elles investissent dans de nouvelles technologies et souhaitent simultanément préserver leurs investissements dans les équipements hérités. L'activation IP d'un PBX hérité peut être très coûteuse ; ainsi, connecter un PBX Asterisk via des lignes T1/E1 peut constituer une bonne alternative pour les clients soucieux des coûts. Un autre avantage est la possibilité de se connecter à un fournisseur de services VoIP offrant de meilleurs tarifs téléphoniques.

![Mise en réseau IP d'un PBX hérité](../images/01-introduction-fig07.png)

### Contournement des péages

Une application très utile pour la VoIP consiste à connecter des succursales via Internet ou un WAN. Utiliser une connexion de données existante vous permet d'éviter les frais de péage engendrés par les liaisons télécom entre le siège et les succursales.

![Contournement de péage entre bureaux sur un WAN](../images/01-introduction-fig08.png)

### Serveur d'application (IVR, Conférence, Messagerie vocale)

Asterisk peut être utilisé comme serveur d’applications pour le PBX existant ou être connecté directement au PSTN. Asterisk offre des services tels que la messagerie vocale, la réception de fax, l’enregistrement d’appels, l’IVR connecté à une base de données, et un serveur de conférence audio. Si vous intégrez la messagerie vocale et le fax à un serveur de messagerie existant, vous disposerez d’un système de messagerie unifiée, qui est généralement une solution coûteuse. Utiliser Asterisk comme serveur d’applications permet de réduire considérablement les coûts par rapport à d’autres solutions.

![Asterisk en tant que serveur d'application](../images/01-introduction-fig09.png)

### Passerelle multimédia

La plupart des fournisseurs de services voix sur IP utilisent un proxy SIP pour héberger toutes les enregistrements, la localisation et l’authentification des utilisateurs SIP. Ils doivent encore acheminer les appels vers le PSTN directement ou les router via un fournisseur de terminaison d’appels en gros en utilisant une connexion voix sur IP SIP ou H.323. Asterisk peut agir comme un agent utilisateur bout‑en‑bout (B2BUA) ou une passerelle média, remplaçant des commutateurs logiciels ou des passerelles média très coûteux. Comparez le prix d’une passerelle quatre E1/T1 des principaux fabricants du marché avec Asterisk. La solution Asterisk peut coûter plusieurs fois moins cher que les autres solutions et est capable de traduire les protocoles de signalisation (H.323, SIP, IAX…) et les codecs (G.711, G.729…).

![Asterisk en tant que passerelle multimédia](../images/01-introduction-fig10.png)

### Plateforme de centre de contact

Un centre de contact est une solution très complexe qui combine plusieurs technologies, telles que la distribution automatique d’appels (ACD), la réponse vocale interactive (IVR) et la supervision des appels. En gros, trois types de centres de contact sont disponibles : entrant, sortant et mixte.

Les centres de contact entrants sont très sophistiqués et nécessitent généralement ACD, IVR, CTI, l'enregistrement, la supervision et les rapports. Asterisk possède un ACD intégré pour mettre les appels en file d’attente. L’IVR peut être réalisé en utilisant Asterisk Gateway Interface (AGI) ou des mécanismes internes tels que l’application background(). L’intégration téléphonie‑informatique (CTI) est obtenue en utilisant Asterisk Manager Interface (AMI) ; l’enregistrement et les rapports sont intégrés à Asterisk.

Pour un centre de contact sortant, un composeur prédictif ou à puissance variable est l’un des principaux composants. Bien que plusieurs composeurs soient disponibles pour l’Asterisk open‑source, il n’est pas difficile de créer le vôtre pour la plateforme si vous le souhaitez. Un centre de contact mixte permet une opération simultanée entrante et sortante, économisant de l’argent en assurant une meilleure utilisation du temps des agents. Il est possible d’utiliser Asterisk et son mécanisme ACD pour mettre en œuvre une solution mixte.

![Une plateforme de centre de contact Asterisk](../images/01-introduction-fig11.png)

## Recherche d'informations et d'aide

Cette section fournira quelques‑unes des principales sources d'information liées à Asterisk.

- Site officiel d'Asterisk : <https://www.asterisk.org> Vous y trouverez des informations sur :
- Documentation et Wiki -> <https://docs.asterisk.org>
- Forum communautaire -> <https://community.asterisk.org>
- Suivi des bugs -> <https://github.com/asterisk/asterisk/issues>
- Wiki (hérité, largement remplacé par docs.asterisk.org) -> <https://wiki.asterisk.org>

### Forum communautaire

Le forum communautaire d'Asterisk a largement remplacé les anciennes listes de diffusion et est l'endroit où poser des questions. Essayez de rassembler le plus d'informations possible avant de publier. Personne ne vous aidera si vous n'avez pas fait vos devoirs — essayez au moins une fois de résoudre le problème vous‑même.

- <https://community.asterisk.org>

## Résumé

Asterisk est un logiciel sous licence GPL qui permet à un PC ordinaire d’agir comme une puissante plateforme IP PBX. Mark Spencer de Digium a créé Asterisk à la fin des années 1990, et Digium s’est maintenue en vendant du matériel et des produits commerciaux liés à Asterisk. Digium a été rachetée par Sangoma Technologies en 2018 ; Sangoma sponsorise désormais le développement d’Asterisk. La conception de l’interface matérielle provient du projet Zapata développé par Jim Dixon, qui a donné naissance à DAHDI.

L’architecture d’Asterisk comprend les composants principaux suivants :

- CHANNELS : Analogique, numérique ou voix sur IP. Dans Asterisk 22 LTS, SIP est géré exclusivement par `chan_pjsip`.  
- PROTOCOLS : Protocoles de communication, responsables de la signalisation des appels, incluant SIP (via PJSIP), H.323, MGCP et IAX2.  
- CODECS : Convertissent les formats numériques de la voix en permettant la compression et la dissimulation de perte de paquets. Notez qu’Asterisk ne réalise pas la suppression de silence (détection d’activité vocale) ni la génération de bruit de confort ; lorsque les endpoints utilisent le VAD, le bruit de confort doit être désactivé côté client.  
- APPLICATIONS : Responsables des fonctionnalités PBX d’Asterisk. Conférence, voicemail et fax sont des exemples d’applications Asterisk.

Asterisk peut être utilisé dans divers scénarios, d’un petit IP PBX à un centre de contact sophistiqué. Vous pouvez facilement trouver de l’aide sur www.asterisk.org et docs.asterisk.org.

## Quiz

1. Quelle entreprise a acquis Digium en 2018 et est désormais le principal responsable du projet open‑source Asterisk ?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. Dans Asterisk 22 LTS, quel pilote de canal fournit la connectivité SIP ?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Vrai ou Faux : le pilote de canal `chan_sip` a été supprimé dans Asterisk 21 et n’est pas présent dans une installation standard d’Asterisk 22.

4. Lesquels des canaux/protocoles suivants ne font **plus** partie d’une installation standard d’Asterisk 22 ? (Choisissez toutes les réponses applicables.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, survivant uniquement sous forme de l’add‑on communautaire `ooh323`)

5. L’architecture matérielle du projet Zapata, initialement appelée Zaptel, a ensuite été renommée en ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Lorsque Asterisk doit convertir l’audio d’un codec à un autre, quel format de flux interne utilise‑t‑il comme intermédiaire ?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Selon le chapitre, quelle est la situation de licence du module codec G.729 distribué par Sangoma ?
   - A. Il est GPL et totalement gratuit pour toute utilisation.
   - B. Le téléchargement est gratuit, mais une utilisation légale nécessite l’achat d’une licence par canal.
   - C. Il ne peut pas être obtenu du tout sans acheter Asterisk Business Edition.
   - D. Il ne fonctionne qu’en mode pass‑through et ne peut pas être installé.

8. Quelle application Asterisk est utilisée pour mettre en pont un appel d’un téléphone à un autre ?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Qu’est‑ce que le canal `Local` dans Asterisk ?
   - A. Une interface matérielle FXS pour téléphones analogiques.
   - B. Un trunk SIP vers un fournisseur de services local.
   - C. Un pseudo‑canal qui renvoie un appel dans le dialplan dans un contexte différent.
   - D. Un codec utilisé pour les appels sur le réseau interne.

10. Dans quel scénario d’utilisation Asterisk agit comme un agent utilisateur bout‑en‑bout (B2BUA), traduisant entre protocoles de signalisation et codecs pour remplacer des soft‑switches coûteux ?
    - A. IP‑activation d’un PBX hérité
    - B. Contournement de péage
    - C. Media Gateway
    - D. Plateforme de centre de contact

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
