# Asterisk Real-Time

Comme vous le savez, la configuration d’Asterisk est réalisée grâce à plusieurs fichiers texte situés dans le répertoire /etc/asterisk. Malgré la simplicité d’utilisation des fichiers texte, certains inconvénients sont connus :

- La nécessité de recharger Asterisk à chaque modification des fichiers
- Une consommation de mémoire accrue pour un grand nombre d’utilisateurs
- Il est difficile de coder une interface de provisioning en utilisant des fichiers texte
- Aucun moyen d’intégration aux bases de données existantes

ARA ou Asterisk Realtime, comme on l’appelle, a été créé par Anthony Minessale II, Mark Spencer et Constantine Filin et a été conçu pour permettre une intégration transparente avec les bases de données SQL. Une interface LDAP est également disponible. Ce système est aussi connu sous le nom d’Asterisk External Configuration et se configure dans /etc/asterisk/extconfig.conf. Vous pouvez associer des fichiers de configuration à des tables dans une base de données (configuration statique) et des entrées en temps réel pour la création dynamique d’objets sans avoir besoin de recharger Asterisk.

## Objectifs

À la fin de ce chapitre, le lecteur devrait être capable de :

- Comprendre les avantages et les limites d’Asterisk Real Time.
- Utiliser ODBC pour l’utiliser avec ARA
- Compiler et installer ARA en utilisant ODBC
- Tester le système dans un environnement de laboratoire

## Comment fonctionne le Real Time d'Asterisk ?

Dans la nouvelle architecture Real Time, tout le code spécifique à la base de données a été déplacé vers les pilotes de canal. Le canal n’appelle qu’une routine générique qui interroge la base de données. Le résultat est un processus beaucoup plus simple et plus propre du point de vue du code source. La base de données est accédée par trois fonctions :

- STATIC : Utilisée pour configurer une configuration statique lorsqu’un module est chargé.  
- REALTIME : Utilisée pour rechercher des objets pendant un appel ou un autre événement.  


- UPDATE : Utilisée pour mettre à jour des objets.

Sur Asterisk 22, les points de terminaison SIP sont gérés par la pile **PJSIP** (`res_pjsip`), qui repose sur le modèle d’objet **Sorcery**. Avec l’assistant `realtime`, Sorcery charge chaque objet PJSIP depuis la base de données à la demande, et ces objets existent alors comme des objets PJSIP configurés ordinaires — et non comme les pairs temporaires du Real Time que l’ancien pilote SIP éliminait après chaque appel.

Comme il s’agit de véritables objets, le traversée NAT, la qualification et l’indication de messages en attente (MWI) fonctionnent normalement pour les points de terminaison realtime. (Sorcery peut également être configuré pour mettre en cache les objets en mémoire via un assistant `memory_cache`, mais cela est optionnel et distinct du chargement realtime.) Lorsque vous modifiez un objet dans la base de données, la modification est prise en compte lors de la prochaine recherche ; vous n’avez pas besoin de recharger après chaque édition. (Le modèle realtime retiré `chan_sip`, avec ses familles `sippeers`/`sipusers`, n’est traité que dans le chapitre *Legacy Channels*.)

## Configurer Asterisk Real Time

Pour ce laboratoire, nous supposerons que vous avez déjà installé ODBC depuis le chapitre CDR. ARA est configuré dans le fichier texte extconfig.conf, où deux sections sont facilement visibles. La première est la section des fichiers de configuration statiques, où vous pouvez remplacer les fichiers de configuration texte par des tables de base de données. La seconde section est le moteur de configuration en temps réel, où vous configurez les tables de base de données pour les objets dynamiques (peers/users). Il n’est pas rare d’utiliser des fichiers texte pour la configuration statique et la base de données pour les entrées dynamiques. Dans ce cas, la première section reste intacte.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time architecture: configuration files and static database tables are loaded when Asterisk starts, while realtime database tables provide dynamic configuration that is read on demand during a call.](../images/18-realtime-fig01.png)

```
;
[settings]
;
; Static configuration files:
;
; file.conf => driver,database[,table]
;
; maps a particular configuration file to the given
; database driver, database and table (or uses the
; name of the file as the table if not specified)
;
;uncomment to load queues.conf via the odbc engine.
;
;queues.conf => odbc,asterisk,ast_config
;
; The following files CANNOT be loaded from Realtime storage:
;       asterisk.conf
;       extconfig.conf (this file)
;       logger.conf
;
; Additionally, the following files cannot be loaded from
; Realtime storage unless the storage driver is loaded
; early using 'preload' statements in modules.conf:
;       manager.conf
;       cdr.conf
;       rtp.conf
;
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
;example => odbc,asterisk,alttable
;ps_endpoints => odbc,asterisk
;ps_aors => odbc,asterisk
;ps_auths => odbc,asterisk
;ps_contacts => odbc,asterisk
;voicemail => odbc,asterisk
;extensions => odbc,asterisk
;queues => odbc,asterisk
;queue_members => odbc,asterisk
```


### Section de configuration statique

La section de configuration statique est l’endroit où vous stockez l’équivalent des fichiers de configuration dans la base de données. Ces configurations sont lues lors du chargement d’Asterisk. Certains modules relisent la base de données lorsque vous effectuez un reload. Des exemples de configuration statique sont :

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

Le mappage de fichiers statiques est le plus utile pour les fichiers de configuration qui n’ont pas d’équivalent en temps réel par objet. Pour PJSIP, privilégiez les familles en temps réel par objet (`ps_endpoints`, `ps_aors`, etc.) décrites plus loin dans ce chapitre plutôt que de mapper l’ensemble de `pjsip.conf` comme fichier statique.

Trois exemples sont décrits ci‑dessus. Dans le premier, vous liez queues.conf à une table queues dans la base de données asteriskdb. Dans le deuxième exemple, vous liez pjsip.conf à la table pjsip_conf dans la base de données asteriskdb définie dans la configuration odbc. Dans le dernier exemple, vous liez iax.conf à un annuaire LDAP. MyBaseDN est le DN de base à rechercher. Dans l’exemple précédent, l’application app_queue.so est chargée tandis que le pilote MySQL interroge la base de données et récupère les informations requises.

### Section de configuration en temps réel

La configuration en temps réel (deuxième partie du fichier extconfig.conf) est l’endroit où l’élément de configuration à charger est configuré, mis à jour et déchargé en temps réel. Avec le temps réel, il n’est pas nécessaire de recharger les configurations. La syntaxe du temps réel est la suivante :

```
<family name> => <driver>,<database name>[,table_name]
```

Exemple :

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Ici nous avons cinq lignes de configuration. Dans la première ligne, vous liez la famille PJSIP/Sorcery `ps_endpoints` à une table `ps_endpoints` dans la base de données asteriskdb. Dans la dernière, vous liez la famille voicemail à la table test dans la base de données asteriskdb. Chaque type d’objet PJSIP (endpoint, aor, auth, contact) possède sa propre famille et table ; l’ensemble complet est présenté dans la section « PJSIP Realtime (Sorcery) » ci‑dessous. Les familles `voicemail`, `extensions`, `queues` et `queue_members` restent valides dans Asterisk 22.

## PJSIP Realtime (Sorcery)

Sur Asterisk 22, les points de terminaison SIP sont gérés exclusivement par la pile **PJSIP** (`res_pjsip`), qui repose sur la couche d’abstraction d’objets **Sorcery**. Au lieu d’un seul « peer » SIP, PJSIP divise un compte SIP en plusieurs types d’objets, chacun stocké dans sa propre table realtime :

| Sorcery object type | Realtime table | What it holds |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | paramètres par compte (context, codecs, DTMF, etc.) |
| aor (address of record) | ps_aors | limites d’enregistrement et paramètres `qualify` |
| auth | ps_auths | informations d’identification `username` / `password` |
| contact | ps_contacts | l’emplacement enregistré dynamiquement |
| domain alias | ps_domain_aliases | domaines SIP alternatifs pour un point de terminaison |
| endpoint identifier by IP | ps_endpoint_id_ips | correspondance d’un point de terminaison par adresse IP source |

Le realtime pour PJSIP est activé à deux endroits. Tout d’abord, mappez les types d’objets Sorcery vers le realtime dans `extconfig.conf` :

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Ensuite, indiquez à Sorcery d’utiliser l’assistant `realtime` pour ces types d’objets dans `sorcery.conf`. Le nom de mappage (ici `res_pjsip`) est le module dont vous déplacez les objets, et la valeur de droite pointe vers la famille que vous avez définie dans `extconfig.conf` :

```
[res_pjsip]
endpoint=realtime,ps_endpoints
aor=realtime,ps_aors
auth=realtime,ps_auths
domain_alias=realtime,ps_domain_aliases
contact=realtime,ps_contacts

[res_pjsip_endpoint_identifier_ip]
identify=realtime,ps_endpoint_id_ips
```

Vous pouvez mélanger objets statiques et objets realtime. Si vous omettez un type de `sorcery.conf`, ce type d’objet continue de lire depuis `pjsip.conf`. Un schéma courant consiste à garder les transports statiques et les paramètres globaux dans `pjsip.conf` tout en stockant les points de terminaison, aors, auths et contacts dans la base de données.

### Création du schéma realtime PJSIP avec Alembic

Asterisk fournit des migrations de base de données pour tous ses schémas realtime sous `contrib/ast-db-manage`. C’est la méthode supportée pour créer (et mettre à jour) les tables PJSIP — vous n’avez plus besoin d’écrire manuellement les définitions de tables `ps_*`. Le jeu de migrations `config` contient les tables PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

Cela crée `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts` et les autres tables PJSIP avec les colonnes correctes pour la version d’Asterisk en cours d’exécution. (Alembic nécessite le paquet Python `alembic` ainsi qu’un driver SQLAlchemy tel que `pymysql` pour MySQL/MariaDB ou `psycopg2` pour PostgreSQL.)

Un point de terminaison realtime minimal consiste alors en une ligne dans chacune des trois tables — par exemple le point de terminaison `6010` :

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

Après avoir inséré les lignes, il n’y a rien à recharger — le prochain REGISTER/INVITE récupère les objets depuis la base de données. Vous pouvez confirmer ce que le realtime a renvoyé avec :

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Configuration de la base de données

Now that we have configured the extconfig.conf file, let’s create the tables. Generally speaking, each database column matches an option name from the corresponding configuration file. The PJSIP `ps_*` tables follow this rule: every `ps_endpoints` column is named after a `pjsip.conf` endpoint option, every `ps_auths` column after an auth option, and so on. For example, the `pjsip.conf` endpoint below,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

is stored as one row across three tables. The `ps_endpoints` row holds `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`; the `ps_auths` row holds `id=4000, auth_type=userpass, username=4000, password=supersecret`; and the `ps_aors` row holds `id=4000, max_contacts=1`. You only need to populate the columns you actually use — any column you leave NULL falls back to the option's default. If you want, for example, the `callerid` parameter on an endpoint, fill in the `callerid` column of `ps_endpoints` (the column name is the same as the `pjsip.conf` option name).

A voicemail table follows the same idea. Its columns map to the `voicemail.conf` fields:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

The `uniqueid` should be unique to each voicemail user and can be autoincrement. It need not have any relationship to the mailbox or context.

### Construction d'un plan de numérotation avec Asterisk Real Time

You can also use the real-time system to create the dial plan. ARA uses the `switch` statement to include the real-time extensions into the normal dial plan contained in the extensions.conf file. The extension table should look like the one below:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

The `extensions` realtime family is unchanged in Asterisk 22; just make sure the `appdata` column dials PJSIP channels, for example `PJSIP/4000`. In the dial plan, you have to use the `switch` command to use the real time.

![Construction d'un plan de numérotation avec Asterisk Real Time : extensions.conf utilise une instruction `switch => realtime` pour extraire les lignes d'extension (context, exten, priority, app, data) d'une table de base de données au lieu du fichier texte.](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

or

```
[local]
switch => realtime/from-internal@extensions
```

## Lab: Installation et création des tables de base de données

Dans ce laboratoire, nous préparerons la base de données pour recevoir les paramètres d’Asterisk. Nous ne préparerons que les tables REALTIME. La configuration statique sera laissée aux fichiers texte de configuration (cool, n’est‑ce pas ?). La création des tables dans MySQL suit.

Étape 1 : Accédez à la base de données MySQL en tant que root.

```
mysql -u root -p
```

Étape 2 : Connectez‑vous au serveur MySQL créé dans les laboratoires CDR.

```
mysql -u astdb -p
```

Lorsque le mot de passe est demandé, saisissez **supersecret**.

Étape 3 : Créez les tables nécessaires. Les fichiers de schéma statique hérités sont toujours fournis sous `contrib/realtime/` (par exemple `/usr/src/asterisk-22.x/contrib/realtime/mysql`), mais sur Asterisk 22 la méthode recommandée et adaptée à la version pour construire les tables realtime — en particulier les tables PJSIP `ps_*` — est la migration **Alembic** sous `contrib/ast-db-manage` (voir la section « Creating the PJSIP realtime schema with Alembic » ci‑dessus).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Le jeu de migrations Alembic `config` crée les tables PJSIP `ps_*` (ainsi que `voicemail`, `extensions` et les autres schémas realtime) avec exactement les colonnes attendues par la version d’Asterisk en cours d’exécution, de sorte que le schéma corresponde toujours à la build.

Utilisez **supersecret** comme mot de passe.

Étape 4 : Vérifiez la création des tables.

```
mysql -u astdb -p astdb
mysql>use astdb;
mysql>show tables;
```

Vous devriez voir les tables PJSIP `ps_*` (créées par la migration Alembic `config`), ainsi que les tables `voicemail`, `extensions` et les autres tables realtime :

```
mysql> show tables;
+----------------------------+
| Tables_in_astdb            |
+----------------------------+
| ps_aors                    |
| ps_auths                   |
| ps_contacts                |
| ps_domain_aliases          |
| ps_endpoint_id_ips         |
| ps_endpoints               |
| ps_registrations           |
| extensions                 |
| voicemail                  |
+----------------------------+
```

(Alembic crée plus de tables que celles‑ci — la liste ci‑dessus montre celles pertinentes pour ce laboratoire.)

Étape 5 : La base de données est déjà configurée pour ODBC (depuis le laboratoire CDR), aucune configuration ODBC supplémentaire n’est donc nécessaire ici.

Étape 6 : Inspectez et remplissez les tables depuis le client MySQL. Vous n’avez pas besoin d’un outil graphique tel que phpMyAdmin — chaque étape de ce chapitre est du SQL simple, copiable‑collable, exécuté depuis la ligne de commande `mysql`. Connectez‑vous à la base de données `astdb` (utilisez `supersecret` lorsqu’on vous le demande) :

```
mysql -u astdb -p astdb
```

Vous pouvez confirmer les colonnes d’une table à tout moment avec `DESCRIBE`, par exemple :

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

Ces tables ont été créées par la migration Alembic `config`, leurs colonnes correspondent donc déjà aux noms d’options `pjsip.conf` de la version d’Asterisk en cours d’exécution — vous ne remplissez que les colonnes dont vous avez besoin.

## Lab: Configuring and testing ARA

Dans ce laboratoire, nous allons modifier la configuration de **extconfig.conf** afin qu’elle reflète notre configuration de base de données et les tables.

Étape 1 : Configurez **extconfig.conf** et rechargez Asterisk.

```
; Realtime configuration engine
;
; maps a particular family of realtime
; configuration to a given database driver,
; database and table (or uses the name of
; the family if the table is not specified
;
ps_endpoints => odbc,cdr
ps_aors => odbc,cdr
ps_auths => odbc,cdr
ps_contacts => odbc,cdr
voicemail => odbc,cdr,voicemail
extensions => odbc,cdr,extensions
```

Notez les familles `ps_endpoints`, `ps_aors`, `ps_auths` et `ps_contacts` ci‑dessus ; avec les correspondances `sorcery.conf` (voir la section « PJSIP Realtime (Sorcery) ») elles permettent à PJSIP de lire ses comptes depuis la base de données. Les familles `voicemail` et `extensions` complètent l’exemple.

Étape 2 : Test d’extension en temps réel. Créez un nouveau point d’accès `6010` en insérant une ligne dans chacune des tables `ps_auths`, `ps_aors` et `ps_endpoints`, puis essayez d’enregistrer ce point d’accès avec un softphone. Exécutez la requête SQL suivante dans le client `mysql` (`mysql -u astdb -p astdb`) :

```sql
INSERT INTO ps_auths (id, auth_type, username, password)
VALUES ('6010-auth', 'userpass', '6010', 'supersecret');

INSERT INTO ps_aors (id, max_contacts)
VALUES ('6010', 1);

INSERT INTO ps_endpoints
  (id, transport, aors, auth, context, disallow, allow, dtmf_mode, direct_media)
VALUES
  ('6010', 'transport-udp', '6010', '6010-auth', 'from-internal',
   'all', 'ulaw', 'rfc4733', 'no');
```

Les trois lignes décrivent ensemble un compte SIP. Les paramètres restants du compte sont répartis parmi les objets PJSIP : contexte, codecs, mode DTMF et gestion du média directement sur le point d’accès (les six dernières colonnes ci‑dessus) ; l’enregistrement dynamique vit dans l’AOR. Il n’existe pas de drapeau « dynamic » séparé — un AOR accepte les REGISTER dynamiques tant que `max_contacts` est supérieur à zéro, et chaque localisation enregistrée est écrite dans `ps_contacts`.

Dans PJSIP, le mode DTMF hors bande RFC 2833 / RFC 4733 porte le nom `rfc4733`, et `dtmf_mode=rfc4733` est la valeur par défaut — ainsi la colonne `dtmf_mode` ci‑dessus est optionnelle et n’est affichée que pour plus de clarté.

Étape 3 : Essayez d’enregistrer le nouveau téléphone avec un softphone en utilisant le nom d’utilisateur `6010` et le mot de passe `supersecret`. Confirmez l’enregistrement sur l’interface CLI d’Asterisk :

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Étape 4 : Incluez les extensions dans la base de données.

```
mysql -u astdb -p
```

Saisissez le mot de passe :

Utilisez **supersecret** lorsqu’on le demande, puis insérez la ligne d’extension depuis le client MySQL :

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Étape 5 : Incluez Asterisk Real Time dans le dialplan. Dans le contexte `default` :

```
switch => realtime/test@extensions
```

Rechargez les extensions pour activer la modification.

```
asterisk-server*CLI> extensions reload
```

Étape 6 : Reconfigurez l’un des téléphones avec le nom d’utilisateur `bria`, si cela n’a pas déjà été fait.

Étape 7 : Composez le 6007 depuis un téléphone existant ; le téléphone `bria` devrait sonner.

## Résumé

Dans ce chapitre, vous avez appris que Asterisk Real Time vous permet de placer vos configurations dans une base de données. Asterisk fournit des pilotes realtime natifs pour ODBC (qui accède à toute base de données prise en charge par UnixODBC, y compris MySQL/MariaDB et SQLite) et PostgreSQL, ainsi qu’un pilote realtime LDAP pour les annuaires. MySQL/MariaDB est atteint via ODBC, comme nous l’avons fait dans ce chapitre (un module complémentaire dédié `res_config_mysql` existe également, mais il vit en dehors du cœur du build, donc ODBC est le chemin commun). La configuration est divisée en statique et en temps réel. La configuration statique remplace les fichiers de configuration, tandis que la configuration en temps réel crée des objets dynamiques qui ne sont chargés que lorsqu’un appel ou un autre événement connexe se produit. Nous avons conclu avec un laboratoire pratique sur la façon d’installer et de configurer ARA.

## Quiz

1. Asterisk Realtime fait partie de la distribution standard d’Asterisk.  
   - A. Vrai  
   - B. Faux  
2. Les paramètres de connexion d’un serveur de base de données sont configurés dans le fichier :  
   - A. extensions.conf  
   - B. pjsip.conf  
   - C. res_odbc.conf  
   - D. extconfig.conf  
3. Le fichier `extconfig.conf` configure les tables utilisées par Realtime. Il comporte deux sections distinctes (cochez deux) :  
   - A. Configuration statique  
   - B. Configuration Realtime  
   - C. Routes sortantes  
   - D. Adresses IP et ports de base de données  
4. En configuration statique, une fois les objets chargés depuis la base de données ils restent en mémoire d’Asterisk et ne sont rafraîchis qu’au démarrage ou au rechargement.  
   - A. Vrai  
   - B. Faux  
5. Le realtime PJSIP (Sorcery) prend en charge pleinement `qualify` et MWI pour les points de terminaison realtime, car Sorcery les charge comme des objets PJSIP configurés ordinaires plutôt que de les ignorer après chaque appel comme le faisaient les anciens pairs SIP realtime.  
   - A. Vrai  
   - B. Faux  
6. Dans le realtime PJSIP, quelles tables contiennent les points de terminaison et leurs contacts enregistrés ?  
   - A. `ps_endpoints` et `ps_contacts`  
   - B. `ps_peers` et `ps_registry`  
   - C. `ps_config` et `ps_data`  
   - D. `extconfig` et `res_odbc`  
7. Vous pouvez toujours utiliser des fichiers de configuration texte même après avoir activé ARA.  
   - A. Vrai  
   - B. Faux  
8. phpMyAdmin est obligatoire lorsque vous utilisez Realtime.  
   - A. Vrai  
   - B. Faux  
9. La base de données doit être créée avec chaque champ qui existe dans le fichier de configuration.  
   - A. Vrai  
   - B. Faux  
10. Sur Asterisk 22, quelle est la méthode recommandée et conforme à la version pour créer les tables realtime PJSIP (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`) ?  
    - A. Écrire manuellement les instructions `CREATE TABLE` pour chaque table `ps_*`  
    - B. Importer le legacy `mysql_config.sql` depuis `contrib/realtime/`  
    - C. Exécuter les migrations Alembic `config` sous `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)  
    - D. Les tables sont créées automatiquement la première fois qu’Asterisk démarre  

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
