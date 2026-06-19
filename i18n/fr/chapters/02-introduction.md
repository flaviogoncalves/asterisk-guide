# Introduction au PBX Asterisk

La popularité des distributions prêtes à l'emploi telles que FreePBX et Issabel a récemment augmenté. Dans ce livre, nous aborderons l'Asterisk classique, qui constitue la base pour comprendre ces distributions. Asterisk PBX est un logiciel open-source capable de transformer un PC ordinaire en un puissant PBX multiprotocole. Dans ce chapitre, nous découvrirons les possibilités de cette nouvelle technologie et son architecture de base.

## Objectifs

À la fin de ce chapitre, vous devriez être capable de :

- Expliquer ce qu'est Asterisk et ce qu'il fait ;
- Décrire le rôle de Digium™ et de son successeur Sangoma ;
- Reconnaître l'architecture de base d'Asterisk et ses composants ;
- Indiquer plusieurs scénarios d'utilisation ; et
- Identifier les sources d'information et d'aide.

## Qu'est-ce qu'Asterisk

Asterisk est un logiciel PBX open-source qui, une fois installé sur le matériel d'un PC avec les interfaces appropriées, peut être utilisé comme un PBX complet pour les utilisateurs à domicile, les entreprises, les fournisseurs de services VoIP et les compagnies téléphoniques. Asterisk est à la fois une communauté open-source et un projet parrainé par Sangoma Technologies (qui a acquis Digium en 2018). Vous êtes libre d'utiliser et de modifier Asterisk pour répondre à vos besoins. Asterisk permet une connectivité en temps réel entre les réseaux PSTN et VoIP. Comme Asterisk est bien plus qu'un simple PBX, vous disposez non seulement d'une mise à niveau exceptionnelle pour votre PBX existant, mais vous pouvez également accomplir de nouvelles tâches en téléphonie, telles que :

- Connecter les employés travaillant à domicile à un PBX de bureau via Internet haut débit ;
- Connecter plusieurs bureaux situés dans des lieux différents via un réseau IP, un réseau privé ou même via Internet lui-même ;
- Offrir à vos employés une messagerie vocale intégrée au web et aux e-mails ;
- Créer des applications comme des IVR qui permettent des connexions à votre système de commande ou à d'autres applications ;
- Donner aux utilisateurs itinérants un accès au PBX de l'entreprise depuis n'importe où avec une simple connexion haut débit ou VPN ; et
- bien plus encore...

Asterisk inclut plusieurs ressources avancées auparavant uniquement disponibles dans les systèmes haut de gamme, telles que :

- Musique d'attente pour les clients en file d'attente, prenant en charge le streaming multimédia et les fichiers MP3 ;
- Files d'attente d'appels, permettant à une équipe d'agents de répondre aux appels et de surveiller les files d'attente ;
- Intégration avec la synthèse vocale et la reconnaissance vocale ;
- Enregistrements détaillés transférés vers des fichiers texte et des bases de données SQL ; et
- Connectivité PSTN via des lignes numériques et analogiques.

## Qu'est-ce qu'AsteriskNOW (historique) et FreePBX

Asterisk dans sa forme la plus pure, également connu sous le nom d'« Asterisk classique » (dénomination des paquets Debian), est considéré davantage comme un outil de développement qu'un produit fini en soi. AsteriskNOW était une initiative visant à transformer Asterisk en une soft-appliance. La distribution incluait CentOS comme système d'exploitation et FreePBX comme interface graphique. AsteriskNOW a depuis été abandonné.

Aujourd'hui, la distribution Asterisk clé en main standard est **FreePBX** (maintenue par Sangoma), qui regroupe Asterisk avec une interface graphique d'administration basée sur le web et un écosystème de modules. FreePBX est sous licence GPL et peut être téléchargé gratuitement sur www.freepbx.org. Pour les déploiements commerciaux, Sangoma propose également **FreePBX Distro** (une image Linux complète) et son produit commercial **PBXact**.

## Rôle de Digium™ et Sangoma

Digium, une entreprise située à Huntsville, en Alabama, a été le créateur et le principal développeur d'Asterisk depuis sa fondation en 1999. En plus d'être le principal sponsor du développement d'Asterisk, Digium produisait des cartes d'interface téléphonique et d'autres matériels pour les PBX Asterisk, et a créé des produits commerciaux tels que Switchvox (ciblant le marché des PME). En 2018, Digium a été acquise par **Sangoma Technologies**, une entreprise canadienne de communications unifiées. Depuis l'acquisition, Sangoma a continué à parrainer le développement d'Asterisk et sert de principal intendant, maintenant le projet open-source sur www.asterisk.org.

Historiquement, Digium proposait Asterisk sous trois types d'accords de licence :

- Asterisk sous licence publique générale (GPL). C'est la version la plus utilisée. Elle inclut toutes les fonctionnalités et est libre d'être utilisée et modifiée selon les termes de la licence GPL.
- Asterisk Business Edition était une version commerciale d'Asterisk. Certaines entreprises utilisaient l'édition business parce qu'elles ne voulaient pas ou ne pouvaient pas utiliser la licence GPL — généralement parce qu'elles ne souhaitaient pas publier leur code source avec Asterisk. **Note :** Asterisk Business Edition a été abandonné ; aujourd'hui, Asterisk est distribué uniquement sous licence GPL.
- Licence OEM Asterisk. Après que Digium a cessé de vendre Asterisk Business Edition au détail, elle a continué à concéder cette édition commerciale sous licence aux clients OEM — des fournisseurs d'équipements qui souhaitaient construire des produits propriétaires sur Asterisk sans publier leur propre code source sous la GPL.

### Le projet Zapata et sa relation avec Asterisk

Le projet Zapata a été développé par Jim Dixon, qui était également responsable de la conception matérielle révolutionnaire utilisée avec Asterisk. Le matériel est également open-source ; à ce titre, il peut être utilisé par n'importe quelle entreprise, et aujourd'hui, plusieurs fabricants produisent des cartes compatibles avec cette architecture.

Le projet Zapata a produit une architecture appelée Zaptel, renommée plus tard DAHDI (Digium/Asterisk Hardware Device Interface). L'un des principaux avantages de cette architecture est la capacité d'utiliser le CPU du PC pour traiter le streaming multimédia, l'annulation d'écho et le transcodage. En revanche, la plupart des cartes existantes utilisent des processeurs de signal numérique (DSP) pour effectuer ces tâches. L'utilisation du CPU du PC au lieu de DSP dédiés réduit considérablement le prix de la carte. Ainsi, ces cartes sont nettement moins chères que les interfaces précédemment disponibles auprès d'autres fabricants. D'un autre côté, ces cartes nécessitent beaucoup de CPU ; une mauvaise utilisation du CPU du PC peut avoir un impact significatif sur la qualité de la voix. Récemment, Digium a lancé une carte coprocesseur qui utilise des DSP pour encoder et décoder G.729 et G.723, permettant une meilleure évolutivité pour un grand nombre de canaux.

## Pourquoi Asterisk ?

Je me souviens de mon premier contact avec Asterisk. Habituellement, la première réaction face à quelque chose de nouveau — surtout quelque chose qui concurrence ce que vous connaissez déjà — est de le rejeter ! C'est exactement ce qui s'est passé en 2003. Asterisk concurrençait une solution que je vendais à un client (passerelle VoIP 4 E1), et elle était dix fois moins chère que ce que je facturais pour la solution que je connaissais déjà. Ce prix disproportionné m'a conduit à commencer à étudier Asterisk afin d'identifier les pièges et inconvénients potentiels. Par exemple, j'ai découvert que le CPU du PC à cette époque ne supporterait pas 120 sections G.729 simultanées ; à la fin de la journée, j'ai remporté la proposition avec ma solution de passerelle. Cependant, cet exercice m'a conduit à découvrir qu'Asterisk pouvait résoudre une variété de problèmes très coûteux pour ma clientèle. Nous étions en difficulté avec des devis coûteux pour l'IVR, la messagerie unifiée, l'enregistrement d'appels et les numéroteurs ; avec un dimensionnement approprié, les problèmes de CPU pouvaient être contournés. En effet, en seulement trois ans, Asterisk est devenu le produit phare de mon entreprise (j'ai en fait décidé d'ouvrir une autre entreprise juste pour l'activité Asterisk). À mon avis, Asterisk est une révolution dans les télécommunications qui représente pour la téléphonie IP ce qu'Apache représente pour les services web.

### Réduction extrême des coûts

Si vous comparez un PBX traditionnel avec Asterisk en ce qui concerne les interfaces numériques et les téléphones, Asterisk est légèrement moins cher que ces PBX. Cependant, Asterisk devient vraiment rentable lorsque vous ajoutez des fonctionnalités avancées telles que la messagerie vocale, l'ACD, l'IVR et le CTI. Avec ces fonctionnalités avancées, Asterisk devient nettement moins cher que les PBX traditionnels. En fait, comparer les PBX Asterisk avec des PBX analogiques bas de gamme est injuste car Asterisk offre tant de fonctionnalités non disponibles dans les systèmes analogiques bas de gamme.

### Contrôle et indépendance du système de téléphonie

L'un des avantages d'Asterisk les plus souvent cités par les clients est l'indépendance qu'il procure. Certains fabricants actuels ne donnent même pas au client le mot de passe du système ou la documentation de configuration. Avec l'approche « faites-le vous-même » d'Asterisk, l'utilisateur obtient une liberté totale ; en prime, l'utilisateur a accès à une interface standard.

### Environnement de développement facile et rapide

Asterisk peut être étendu en utilisant des langages de script comme PHP et Perl avec les interfaces AMI et AGI. Asterisk est open-source, et son code source peut être modifié par l'utilisateur. Le code source est écrit principalement en langage de programmation ANSI C.

### Riche en fonctionnalités

Asterisk possède plusieurs fonctionnalités qui sont soit absentes, soit optionnelles dans les PBX traditionnels (par exemple, messagerie vocale, CTI, ACD, IVR, musique d'attente intégrée et enregistrement). Les coûts de ces fonctionnalités sur certaines plateformes dépassent le prix de la plateforme elle-même.

### Contenu dynamique sur le téléphone

Asterisk est programmé en utilisant le langage C et d'autres langages courants dans l'environnement de développement actuel. La possibilité de fournir du contenu dynamique est pratiquement illimitée.

### Plan de numérotation flexible et puissant

Une autre percée d'Asterisk est son puissant dialplan. Dans les PBX traditionnels, même des fonctionnalités simples comme le routage au moindre coût (LCR) sont soit irréalisables, soit optionnelles. Avec Asterisk, choisir le meilleur itinéraire est facile et propre.

### Open-source fonctionnant sous Linux

L'une des plus grandes caractéristiques d'Asterisk est sa communauté. Plusieurs ressources sont disponibles, notamment la documentation officielle d'Asterisk (docs.asterisk.org), le wiki VoIP-Info maintenu par la communauté (www.voip-info.org <http://www.voip-info.org>), les listes de distribution par e-mail et les forums. À mesure qu'Asterisk est de plus en plus adopté, les bugs sont trouvés et corrigés rapidement. Avec une large base d'utilisateurs et une équipe de développement active, Asterisk est parmi les plateformes PBX les plus largement testées au monde, ce qui aide à maintenir la base de code stable et mature.

### Limitations de l'architecture Asterisk

Certaines limitations d'Asterisk découlent de l'utilisation de la conception téléphonique Zapata. Dans cette conception, Asterisk utilise le CPU du PC pour traiter les canaux vocaux au lieu de processeurs de signal numérique (DSP) dédiés, qui sont courants sur d'autres plateformes. Bien que cela permette une énorme réduction des coûts de l'interface matérielle, le système devient dépendant du CPU du PC. Ma recommandation est d'exécuter Asterisk sur une machine dédiée et d'être conservateur sur le dimensionnement du matériel. Vous pouvez également utiliser Asterisk dans un VLAN séparé pour éviter les diffusions excessives qui consomment le CPU (tempêtes de diffusion causées par des boucles ou des virus). Certaines cartes d'interface plus récentes de plusieurs fournisseurs incluent désormais des DSP pour traiter l'annulation d'écho, les codecs et d'autres fonctionnalités, ce qui rendra Asterisk encore meilleur.

## Principales objections au PBX Asterisk

Il est courant d'entendre des objections à l'adoption d'Asterisk, auxquelles nous répondrons ici.

### La part de marché d'Asterisk est trop petite

La part de marché est généralement mesurée par le nombre de PBX vendus. Ces statistiques sont généralement acquises auprès des plus grands distributeurs. Asterisk est un logiciel libre qui peut être téléchargé et déployé sans qu'aucune vente ne soit enregistrée, il est donc systématiquement sous-estimé dans ces chiffres. Même ainsi, Asterisk alimente une très large base installée dans le monde entier — des PBX de bureau à serveur unique aux grands déploiements d'opérateurs et de centres de contact — et reste le moteur dominant derrière l'écosystème PBX open-source (y compris les distributions clé en main telles que FreePBX).

### S'il est gratuit, comment le fabricant survit-il ?

En fait, il n'existe pas de fabricant de logiciels open-source au sens traditionnel. Digium a développé Asterisk depuis 1999, se soutenant par la vente de cartes d'interface téléphonique, de produits PBX commerciaux tels que Switchvox et de logiciels associés. En 2018, Sangoma Technologies a acquis Digium. Sangoma continue de financer le développement d'Asterisk et génère des revenus grâce à des produits commerciaux (modules commerciaux FreePBX, PBXact, Switchvox), des ventes de matériel et des services professionnels.

### Il est difficile de trouver un support technique !

Sangoma fournit un support technique commercial pour Asterisk via son écosystème de partenaires et directement via ses offres de produits. Un réseau mondial de professionnels certifiés fournit un support de premier niveau et des services professionnels. Le support communautaire reste actif via les forums Asterisk et les listes de diffusion sur www.asterisk.org.

### Asterisk supporte-t-il plus de 200 extensions ?

Oui, absolument. Un seul serveur Asterisk bien dimensionné peut gérer un grand nombre d'extensions, et Asterisk évolue davantage en distribuant les utilisateurs sur plusieurs serveurs avec équilibrage de charge et basculement, permettant de grands déploiements multisites.

### Seuls les « geeks » sont capables d'installer Asterisk

Avec FreePBX (disponible en tant que distribution autonome auprès de Sangoma), même les professionnels ayant des connaissances limitées sur Linux sont capables d'installer et de configurer un PBX de complexité moyenne. Avec l'aide d'une interface graphique, il est possible de configurer un PBX entier en quelques heures seulement.

### Que se passe-t-il si le serveur tombe en panne ?

L'un des principaux avantages d'Asterisk est sa capacité à fonctionner dans des systèmes tolérants aux pannes. Il est relativement simple et peu coûteux d'avoir deux serveurs fonctionnant en parallèle. Je vous mets au défi d'essayer cela avec un PBX conventionnel !

### Notre entreprise n'utilise pas de logiciels open-source

Votre entreprise utilise probablement des logiciels open-source sans même s'en rendre compte. Plusieurs appareils utilisent Linux comme système d'exploitation. De plus, un support commercial et des déploiements gérés sont disponibles auprès de Sangoma et de son réseau de partenaires certifiés.

### L'utilisation du CPU du PC pour traiter la signalisation et les médias n'est pas recommandée

Asterisk utilise le CPU du serveur pour traiter la signalisation et les médias pour les canaux vocaux au lieu d'avoir des DSP dédiés. Bien que cela permette une réduction des coûts allant jusqu'à cinq fois, cela rend le système dépendant des performances du CPU principal. Avec le dimensionnement correct, Asterisk est capable de gérer de grands volumes. Si vous souhaitez toujours libérer le CPU principal de ces tâches, vous pouvez également utiliser l'annulation d'écho matérielle et même des cartes transcodeuses, telles que la Sangoma (anciennement Digium) TC400B basée sur des DSP.

## Architecture d'Asterisk

Cette section expliquera comment fonctionne l'architecture d'Asterisk. La figure ci-dessous montre l'architecture de base d'Asterisk. Ensuite, nous expliquerons les concepts liés à l'architecture, notamment les canaux, les codecs et les applications.

![L'architecture d'Asterisk](../images/01-introduction-fig01.png)

### Canaux

Un canal est l'équivalent d'une ligne téléphonique, mais dans un format numérique. Il consiste généralement en un système de signalisation analogique ou numérique (TDM) ou une combinaison de codec et de protocole de signalisation (par exemple, SIP-GSM, IAX-uLaw). Initialement, toutes les connexions téléphoniques étaient analogiques et sensibles à l'écho et au bruit. Plus tard, la plupart des systèmes ont été convertis en systèmes numériques, avec le son analogique converti en format numérique utilisant la modulation par impulsions et codage (PCM) dans la plupart des cas. Ce format permet une transmission vocale à 64 kilobits/seconde sans compression.

Canaux s'interfaçant avec le réseau téléphonique public commuté (PSTN) :

- `chan_dahdi` : cartes TDM analogiques (FXO/FXS) et numériques (E1/T1/PRI) de Sangoma (anciennement Digium), Xorcom et autres. Construites séparément contre DAHDI — voir le chapitre *Canaux hérités*.

Canaux s'interfaçant avec la voix sur IP :

- `chan_pjsip` : SIP — le pilote de canal SIP principal et unique dans Asterisk 22 LTS. Chaîne de numérotation : `PJSIP/endpoint_name`. (**Note :** l'ancien `chan_sip` a été supprimé dans Asterisk 21 et n'existe pas dans Asterisk 22. Voir *Construire votre premier PBX avec PJSIP* pour la configuration.)
- `chan_iax2` : le protocole IAX2 — toujours livré dans Asterisk 22 mais est hérité ; SIP/PJSIP est préféré pour les nouveaux déploiements. Chaîne de numérotation : `IAX2/peer`.
- `chan_unistim` : téléphones Nortel/Avaya UNISTIM. Toujours disponible (support étendu) mais rarement utilisé.

Les anciens canaux VoIP ne font plus partie d'une version standard d'Asterisk 22 : `chan_h323` (H.323) survit uniquement en tant qu'add-on communautaire `ooh323`, et `chan_mgcp` (MGCP) et `chan_skinny` (Cisco SCCP) ont été obsolètes et supprimés de l'ensemble des canaux modernes. Si vous devez interopérer avec ces protocoles, une passerelle devant Asterisk est l'approche habituelle.

Canaux divers :

- **Local** : un pseudo-canal (intégré au cœur) qui boucle dans le dialplan dans un contexte différent — utile pour le routage récursif et pour diffuser un appel vers plusieurs destinations. Chaîne de numérotation : `Local/extension@context`.

### Codec et traduction de codec

Nous essayons généralement de mettre autant de connexions vocales que possible dans un réseau de données. Les codecs permettent de nouvelles fonctionnalités dans la voix numérique, y compris la compression, qui est l'une des fonctionnalités les plus importantes car elle permet des taux de compression supérieurs à 8 pour 1. De nombreux codecs définissent également des fonctionnalités telles que la détection d'activité vocale (suppression du silence), la dissimulation de perte de paquets et la génération de bruit de confort, bien qu'Asterisk lui-même ne génère pas de bruit de confort et n'effectue pas de suppression du silence. Plusieurs codecs sont disponibles pour Asterisk et peuvent être traduits de manière transparente de l'un à l'autre. En interne, Asterisk utilise slinear comme format de flux lorsqu'il doit convertir d'un codec à un autre. Certains codecs dans Asterisk ne sont pris en charge qu'en mode pass-through ; ces codecs ne peuvent pas être traduits. Pour vérifier quels codecs sont installés sur votre système, vous pouvez utiliser la commande de console :

```
CLI>core show translation
```

Les codecs suivants sont pris en charge :

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (Haute Définition) – (64 Kbps)
- G.723.1 - Mode pass-through uniquement
- G.726 - (16/24/32/40kbps)
- G.729 - Module de codec binaire distribué par Sangoma ; le téléchargement est gratuit, mais l'utilisation légale nécessite l'achat d'une licence par canal (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocoles

L'envoi de données d'un téléphone à un autre devrait être facile à condition que les données trouvent un chemin vers l'autre téléphone par elles-mêmes. Malheureusement, cela ne se passe pas ainsi, et un protocole de signalisation est nécessaire afin d'établir des connexions entre les téléphones, découvrir les appareils finaux et implémenter la signalisation téléphonique. SIP est le protocole de signalisation dominant dans les déploiements modernes et est le seul canal SIP disponible dans Asterisk 22 LTS (via chan_pjsip). IAX2 est toujours disponible mais considéré comme hérité. Asterisk prend en charge les protocoles suivants.

- SIP — via `chan_pjsip`
- IAX2 — hérité, toujours livré dans Asterisk 22
- UNISTIM — téléphones Nortel/Avaya (support étendu)
- H.323, MGCP et SCCP (Cisco Skinny) — protocoles hérités qui ne sont plus dans une version standard d'Asterisk 22 (H.323 uniquement via l'add-on communautaire `ooh323`)

### Applications

Pour relier les appels d'un téléphone à un autre, l'application dial() est utilisée. La plupart des fonctionnalités d'Asterisk (par exemple, messagerie vocale et conférence) sont implémentées en tant qu'applications. Vous pouvez voir les applications Asterisk disponibles en utilisant la commande de console core show applications.

```
CLI>core show applications
```

Vous pouvez ajouter des applications à partir d'add-ons Asterisk, de fournisseurs tiers, ou même celles que vous développez vous-même.

## Aperçu d'un système Asterisk

Asterisk est un PBX open-source qui agit comme un PBX hybride, intégrant des technologies telles que le TDM et la téléphonie IP. Asterisk est prêt à implémenter des fonctionnalités telles que la réponse vocale interactive (IVR) et la distribution automatique des appels (ACD) ; de plus, comme mentionné précédemment, il est ouvert au développement de nouvelles applications. Cette figure montre comment Asterisk se connecte au PSTN et aux PBX existants en utilisant des interfaces analogiques et numériques ainsi qu'en prenant en charge les téléphones analogiques et IP. Il peut agir comme un soft-switch, une passerelle multimédia, une messagerie vocale et une conférence audio, et dispose également d'une musique d'attente intégrée.

![Aperçu d'un système Asterisk](../images/01-introduction-fig02.png)

## Comparaison de l'ancien et du nouveau monde

Dans l'ancien modèle de soft-switch, tous les composants étaient vendus séparément, ce qui signifiait que vous deviez acheter chaque composant séparément, puis l'intégrer à l'environnement PBX ou soft-switch. Les coûts et les risques étaient élevés et la plupart des équipements étaient propriétaires.

![L'ancien monde : composants achetés et intégrés séparément](../images/01-introduction-fig03.png)

### Téléphonie utilisant Asterisk

Toutes les fonctions sont intégrées dans la plateforme Asterisk dans la même boîte ou dans des boîtes différentes selon le dimensionnement, et toutes sont sous licence GPL. Parfois, il est plus facile d'installer Asterisk que d'obtenir une licence pour certains des IP-PBX grand public.

![Téléphonie utilisant Asterisk : les fonctions sont intégrées](../images/01-introduction-fig04.png)

## Construire un système de test

Lors de l'implémentation d'une solution Asterisk, notre première étape consiste généralement à construire une machine de test. La machine de test la plus simple est le PBX 1x1, incluant au moins un téléphone et une ligne. Il existe plusieurs façons de faire cela.

![Un système de test Asterisk simple](../images/01-introduction-fig05.png)

### Un FXO, un FXS

La première et la plus simple façon de construire une machine de test est d'acheter une carte avec une interface FXO et une interface FXS. Connectez le port FXO à une ligne existante et connectez un FXS à un téléphone analogique. Ainsi, vous avez un PBX 1x1.

### Fournisseur de services VoIP : ATA

C'est l'option VoIP. Dans ce cas, vous vous inscrirez auprès d'un fournisseur de services vocaux pour avoir les trunks SIP et devrez acheter un adaptateur de téléphonie analogique SIP. Vous dépenserez probablement moins d'une centaine de dollars si vous avez déjà le PC.

### Carte FXO ou ATA peu coûteuse

J'ai commencé avec une carte FXO peu coûteuse. Certains modems fax V.90 peu coûteux fonctionnent avec Asterisk comme carte FXO. Certaines des premières cartes Digium ont été créées en utilisant ces cartes (par exemple, X100P et X101P), qui sont d'anciens modems basés sur des chipsets Motorola et Intel (Motorola 68202-51, Intel 537PU, Intel 537PG et Intel Ambient MD3200 sont connus pour fonctionner). Ces modems sont souvent incompatibles avec les nouvelles cartes mères. Récemment, certains fabricants ont commencé à vendre ces cartes comme des clones X100P. Certaines des incompatibilités peuvent être résolues en utilisant un patch, plus d'informations peuvent être trouvées sur :

- http://www.voip.school/mediawiki/index.php/Asterisk_patch_for_the_X100P_card

## Scénarios Asterisk

Asterisk peut être utilisé dans plusieurs scénarios différents. Nous en listerons quelques-uns et expliquerons les avantages et les limitations possibles de chacun.

### IP PBX

Le scénario le plus courant est l'installation d'un nouveau PBX ou le remplacement d'un PBX existant. Si vous comparez Asterisk avec d'autres alternatives, vous constaterez qu'il est moins cher et plus riche en fonctionnalités que la plupart des PBX actuellement disponibles sur le marché. Plusieurs entreprises changent maintenant leurs spécifications pour Asterisk au lieu d'autres PBX de marque.

![Asterisk en tant qu'IP PBX](../images/01-introduction-fig06.png)

### IP-enabling de PBX hérités

L'image suivante illustre l'une des configurations les plus couramment utilisées. Les grandes entreprises ne veulent généralement pas prendre de risques importants lors de l'investissement dans de nouvelles technologies et souhaitent simultanément préserver leurs investissements dans l'équipement hérité. L'IP-enabling d'un PBX hérité peut être très coûteux ; ainsi, connecter un PBX Asterisk en utilisant des lignes T1/E1 peut être une bonne alternative pour les clients soucieux des coûts. Un autre avantage est la possibilité de se connecter à un fournisseur de services VoIP avec de meilleurs tarifs téléphoniques.

![IP-enabling d'un PBX hérité](../images/01-introduction-fig07.png)

### Contournement de péage (Toll Bypass)

Une application très utile pour la VoIP est la connexion de succursales via Internet ou un WAN. L'utilisation d'une connexion de données existante vous permet de contourner les frais de péage encourus dans les connexions de télécommunication entre le siège social et les succursales.

![Contournement de péage entre bureaux via un WAN](../images/01-introduction-fig08.png)

### Serveur d'applications (IVR, Conférence, Messagerie vocale)

Asterisk peut être utilisé comme serveur d'applications pour le PBX existant ou être directement connecté au PSTN. Asterisk propose des services tels que la messagerie vocale, la réception de fax, l'enregistrement d'appels, l'IVR connecté à une base de données et un serveur de conférence audio. Si vous intégrez la messagerie vocale et le fax dans un serveur e-mail existant, vous aurez un système de messagerie unifiée, qui est généralement une solution coûteuse. L'utilisation d'Asterisk comme serveur d'applications offre une réduction extrême des coûts par rapport à d'autres solutions.

![Asterisk en tant que serveur d'applications](../images/01-introduction-fig09.png)

### Passerelle multimédia

La plupart des fournisseurs de services voix sur IP utilisent un proxy SIP pour héberger toute l'enregistrement, la localisation et l'authentification des utilisateurs SIP. Ils doivent toujours envoyer les appels vers le PSTN directement ou les acheminer via un fournisseur de terminaison d'appel en gros utilisant une connexion voix sur IP SIP ou H.323. Asterisk peut agir comme un back-to-back user agent (B2BUA) ou une passerelle multimédia, remplaçant des soft-switches ou des passerelles multimédia très coûteux. Comparez le prix d'une passerelle quatre E1/T1 des principaux fabricants du marché avec Asterisk. La solution Asterisk peut coûter plusieurs fois moins cher que d'autres solutions et est capable de traduire les protocoles de signalisation (H.323, SIP, IAX…) et les codecs (G.711, G.729…).

![Asterisk en tant que passerelle multimédia](../images/01-introduction-fig10.png)

### Plateforme de centre de contact

Un centre de contact est une solution très complexe qui combine plusieurs technologies, telles que la distribution automatique des appels (ACD), la réponse vocale interactive (IVR) et la supervision des appels. Fondamentalement, trois types de centres de contact sont disponibles : entrant, sortant et mixte. Les centres de contact entrants sont très sophistiqués et nécessitent généralement l'ACD, l'IVR, le CTI, l'enregistrement, la supervision et des rapports. Asterisk dispose d'un ACD intégré pour mettre les appels en file d'attente. L'IVR peut être réalisé en utilisant l'Asterisk Gateway Interface (AGI) ou des mécanismes internes tels que l'application background(). L'intégration téléphonie-informatique (CTI) est réalisée en utilisant l'Asterisk Manager Interface (AMI) ; l'enregistrement et les rapports sont intégrés à Asterisk. Pour un centre de contact sortant, un numéroteur prédictif ou automatique est l'un des composants principaux. Bien que plusieurs numéroteurs soient disponibles pour l'Asterisk open-source, il n'est pas difficile de construire le vôtre pour la plateforme si vous le souhaitez. Un centre de contact mixte permet une opération entrante et sortante simultanée, économisant de l'argent en assurant une meilleure utilisation du temps de l'agent. Il est possible d'utiliser Asterisk et son mécanisme ACD pour implémenter une solution mixte.

![Une plateforme de centre de contact Asterisk](../images/01-introduction-fig11.png)

## Trouver des informations et de l'aide

Cette section fournira certaines des principales sources d'informations liées à Asterisk.

- Site officiel d'Asterisk : <https://www.asterisk.org> Ici, vous pouvez trouver des informations sur :
- Documentation & Wiki -> <https://docs.asterisk.org>
- Forum communautaire -> <https://community.asterisk.org>
- Suivi des bugs -> <https://github.com/asterisk/asterisk/issues>
- Wiki (hérité, largement remplacé par docs.asterisk.org) -> <https://wiki.asterisk.org>

### Forum communautaire

Le forum de la communauté Asterisk a largement remplacé les anciennes listes de diffusion et est l'endroit où poser des questions. Essayez de rassembler autant d'informations que possible avant de publier. Personne ne vous aidera si vous n'avez pas fait vos devoirs — essayez au moins une fois de résoudre le problème par vous-même.

- <https://community.asterisk.org>

## Résumé

Asterisk est un logiciel sous licence GPL qui permet à un PC ordinaire d'agir comme une puissante plateforme IP PBX. Mark Spencer de Digium a créé Asterisk à la fin des années 1990, et Digium s'est soutenu en vendant du matériel lié à Asterisk et des produits commerciaux. Digium a été acquise par Sangoma Technologies en 2018 ; Sangoma parraine maintenant le développement d'Asterisk. La conception de l'interface matérielle provient du projet Zapata développé par Jim Dixon, qui a donné naissance à DAHDI.

L'architecture Asterisk comporte les composants principaux suivants :

- CANAUX : Analogiques, numériques ou voix sur IP. Dans Asterisk 22 LTS, SIP est géré exclusivement par chan_pjsip.
- PROTOCOLES : Protocoles de communication, responsables de la signalisation des appels, incluant SIP (via PJSIP), H323, MGCP et IAX2.
- CODECS : Traduisent les formats numériques de la voix permettant la compression et la dissimulation de perte de paquets. Notez qu'Asterisk lui-même n'effectue pas de suppression du silence (détection d'activité vocale) ou de génération de bruit de confort ; lorsque les endpoints utilisent VAD, le bruit de confort doit être désactivé côté client.
- APPLICATIONS : Responsables de la fonctionnalité du PBX Asterisk. Conférence, messagerie vocale et fax sont des exemples d'applications Asterisk.

Asterisk peut être utilisé dans divers scénarios, d'un petit IP PBX à un centre de contact sophistiqué. Vous pouvez facilement trouver de l'aide sur www.asterisk.org et docs.asterisk.org.

## Quiz

1. Quelle entreprise a acquis Digium en 2018 et sert maintenant de principal intendant du projet open-source Asterisk ?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. Dans Asterisk 22 LTS, quel pilote de canal fournit la connectivité SIP ?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. Vrai ou Faux : Le pilote de canal `chan_sip` a été supprimé dans Asterisk 21 et n'est pas présent dans une version standard d'Asterisk 22.

4. Lesquels des canaux/protocoles suivants ne font **plus** partie d'une version standard d'Asterisk 22 ? (Choisissez tout ce qui s'applique.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, survivant uniquement en tant qu'add-on communautaire `ooh323`)

5. L'architecture matérielle du projet Zapata, initialement appelée Zaptel, a été renommée plus tard en ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. Lorsqu'Asterisk doit convertir l'audio d'un codec à un autre, à travers quel format de flux interne traduit-il ?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. Selon le chapitre, quelle est la situation de licence du module de codec G.729 distribué par Sangoma ?
   - A. Il est GPL et totalement gratuit pour toute utilisation.
   - B. Le téléchargement est gratuit, mais l'utilisation légale nécessite l'achat d'une licence par canal.
   - C. Il ne peut pas être obtenu du tout sans acheter Asterisk Business Edition.
   - D. Il ne fonctionne qu'en mode pass-through et ne peut pas être installé.

8. Quelle application Asterisk est utilisée pour relier un appel d'un téléphone à un autre ?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Qu'est-ce que le canal `Local` dans Asterisk ?
   - A. Une interface FXS matérielle pour les téléphones analogiques.
   - B. Un trunk SIP vers un fournisseur de services local.
   - C. Un pseudo-canal qui boucle un appel dans le dialplan dans un contexte différent.
   - D. Un codec utilisé pour les appels sur le réseau.

10. Dans quel scénario d'utilisation Asterisk agit-il comme un back-to-back user agent (B2BUA), traduisant entre les protocoles de signalisation et les codecs pour remplacer des soft-switches coûteux ?
    - A. IP-enabling d'un PBX hérité
    - B. Contournement de péage
    - C. Passerelle multimédia
    - D. Plateforme de centre de contact

**Réponses :** 1 — B · 2 — C · 3 — Vrai · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
