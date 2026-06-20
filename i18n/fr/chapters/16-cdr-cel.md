# Enregistrements détaillés des appels Asterisk

Asterisk, comme les autres plateformes de téléphonie, permet la facturation des appels téléphoniques. Plusieurs programmes sur le marché peuvent importer les enregistrements générés par les PBX. Ces enregistrements sont utilisés pour vérifier le montant correct de la facture et les statistiques, entre autres.

## Objectives

By the end of this chapter, the reader should be able to:

- Describe where and in what format the records are generated
- Generate records using ODBC (Open Database Connectivity)
- Implement an authentication scheme integrated with billing

## Format CDR d'Asterisk

Asterisk génère un enregistrement détaillé d'appel (CDR) pour chaque appel. Ces enregistrements sont stockés, par défaut, dans un fichier texte au format valeurs séparées par des virgules (CSV) dans le répertoire **/var/log/asterisk/cdr-csv**. Le fichier est organisé selon les champs suivants :

| Champ | Description | Type |
|-------|-------------|------|
| Accountcode | Numéro de compte à utiliser | String |
| Src | Numéro d'ID appelant | String |
| Dst | Extension de destination | String |
| Dcontext | Contexte de destination | String |
| Clid | ID appelant avec texte | String |
| Channel | Canal utilisé | String |
| Dstchannel | Canal de destination | String |
| Lastapp | Dernière application | String |
| Lastdata | Données de la dernière application | String |
| Start | Début de l'appel | Date/Time |
| Answer | Réponse de l'appel | Date/Time |
| End | Fin de l'appel | Date/Time |
| Duration | Temps, du numérotation à la fin | Integer (seconds) |
| Billsec | Temps, de la réponse à la fin | Integer (seconds) |
| Disposition | Ce qui est arrivé à l'appel (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | Drapeaux (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | Champ défini par l'utilisateur | String |

Exemple d'un fichier CSV. Chaque ligne représente un enregistrement ; les champs apparaissent dans le même ordre que le tableau ci‑dessus (**`accountcode`** en premier, **`amaflags`** en dernier) :

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Codes de compte et comptabilisation automatisée des messages

Vous pouvez spécifier des codes de compte et des indicateurs ama sur chaque canal. En général, cela se fait dans le fichier de configuration du canal (par exemple, chan_dahdi.conf, pjsip.conf). Le paramètre amaflags définit ce qu’il faut faire avec l’enregistrement CDR. Les valeurs possibles d’amaflag sont :

- Default
- Omit
- Billing
- Documentation

De la même manière qu’un enregistrement peut être marqué pour la facturation ou la documentation, un code de compte peut être défini sur chaque enregistrement. Le code de compte est une chaîne libre (l’option d’endpoint `accountcode` accepte n’importe quelle String, et l’enregistrement CDR le stocke dans un champ de 80 caractères) généralement utilisé pour attribuer un enregistrement à un département ou à une unité commerciale. Exemple : section endpoint de pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

L’indicateur AMA n’est pas une option d’endpoint `pjsip.conf` dans Asterisk 22 ; définissez‑le par appel depuis le dialplan avec la fonction `CHANNEL` (par exemple `Set(CHANNEL(amaflags)=billing)`), ou avec `Set(CDR(amaflags)=billing)`.

## Modification du format CSV et/ou CDR

Vous pouvez modifier le format CSV en modifiant le fichier cdr_custom.conf.

```
;
; Mappings for custom config file
;
[mappings]
Master.csv =>
"${CDR(clid)}","${CDR(src)}","${CDR(dst)}","${CDR(dcontext)}","${CDR(channel)}"
,"${CDR(dstchannel)}","${CDR(lastapp)}","${CDR(lastdata)}","${CDR(start)}","${C
DR(answer)}","${CDR(end)}","${CDR(duration)}","${CDR(billsec)}","${CDR(disposit
ion)}","${CDR(amaflags)}","${CDR(accountcode)}","${CDR(uniqueid)}","${CDR(userf
ield)}"
```

Vous pouvez modifier le format CDR dans le fichier cdr_custom.conf.

## Stockage des CDR

Le stockage des CDR peut être réalisé de plusieurs manières. La méthode la plus importante est les fichiers texte CSV qui peuvent être facilement importés dans des feuilles de calcul. Pour les petites entreprises, cela suffit généralement. Certains logiciels de facturation acceptent, par défaut, les fichiers CSV. Cependant, stocker les CDR dans une base de données est bien meilleur et plus sûr. Asterisk prend en charge plusieurs types de bases de données. Il existe des interfaces graphiques pour la facturation sur le marché. Avec tant de pilotes, lequel choisir ?

### Pilotes de stockage disponibles

- cdr_csv – fichiers texte à valeurs séparées par des virgules
- cdr_custom – fichiers texte à valeurs séparées par des virgules personnalisables
- cdr_adaptive_odbc – backend ODBC adaptatif (préféré pour le stockage en base de données)
- cdr_odbc – bases de données supportées par unixODBC (héritage ; cdr_adaptive_odbc préféré)
- cdr_pgsql – bases de données Postgres
- cdr_tds (cdr_freetds) – bases de données Sybase et MSSQL via FreeTDS
- cdr_manager – CDR vers l’interface Manager
- cdr_radius – interface CDR radius
- cdr_sqlite3_custom – module CDR SQLite3 personnalisé

Le module `cdr_addon_mysql` (cdr_mysql) recommandé dans les anciens guides a été supprimé dans Asterisk 19, il n’existe donc aucun pilote CDR MySQL natif dans Asterisk 22. Pour écrire des CDR dans MySQL/MariaDB, utilisez `cdr_adaptive_odbc` avec un pilote MySQL ODBC — l’approche utilisée dans ce chapitre.

L’enregistrement des CDR se fait pour tous les modules actifs chargés dans le fichier /etc/asterisk/modules.conf. Si le paramètre autoload=yes est défini, tous les modules sont chargés. Pour vérifier quels cdr_drivers sont actuellement chargés dans le système, utilisez la commande ci‑dessous :

```
asterisk*CLI> module show like cdr_
Module                 Description                              Use Count  Status
Support Level
cdr_adaptive_odbc.so   Adaptive ODBC CDR backend                0          Running
core
cdr_csv.so             Comma Separated Values CDR Backend       0          Running
extended
cdr_custom.so          Customizable Comma Separated Values CDR  0          Running
core
cdr_manager.so         Asterisk Manager Interface CDR Backend   0          Running
core
cdr_odbc.so            ODBC CDR Backend                         0          Running
extended
cdr_sqlite3_custom.so  SQLite3 Custom CDR Module                0          Not Running
extended
6 modules loaded
```

Si vous voyez la capture d’écran ci‑above, au moins cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc et cdr_sqlite3_custom sont en cours d’exécution. Au cours des dernières années, après quelques astricons, il est devenu clair pour moi que l’équipe Asterisk favorisait ODBC. C’est le seul pilote supportant le pool de connexions. Le pool de connexions est un grand avantage en termes de performances car il n’est pas nécessaire d’ouvrir une nouvelle connexion pour chaque opération. Ce chapitre était auparavant rédigé avec cdr_mysql. Je suis passé à cdr_adaptive_odbc pour cette édition même en sachant qu’il est un peu plus complexe à configurer. Le choix de cdr_adaptive_odbc nous permet également de personnaliser le CDR. Vous pouvez simplement définir une nouvelle variable CDR dans le dialplan et ajouter la colonne correspondante dans la base de données. Par exemple, pour enregistrer le jitter audio :

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### Stockage CSV

Comme nous l’avons indiqué précédemment, par défaut, Asterisk envoie tous les CDR vers un fichier texte CSV en utilisant le module cdr_csv.so. Si vous ne voyez pas les fichiers dans /var/log/asterisk/cdr-csv, vérifiez que le module est chargé à l’aide de la commande CLI module show. S’il n’est pas chargé, vérifiez modules.conf. Dans ce chapitre, nous enverrons les CDR vers cdr_csv comme sauvegarde.

### Configuration du fichier modules.conf

Pour ne charger que les modules appropriés, utilisez les lignes ci‑dessous dans le fichier modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

Nous n’avons maintenant que cdr_csv et cdr_adaptive_odbc chargés.

## Installing and configuring ODBC on Ubuntu 22.04

I always regret to publish detailed instructions in the book. They will change sometimes sooner than the book is published. Versions change, modules change, so try to adapt the command here to your own situation. Most of the time minor changes are enough to reproduce the installation. Pay attention on the steps even experienced Linux users will find hard to install the ODBC drivers.

Step 1 - Install the required packages:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

Step 2 - Create a database and a user:

```
mysql -u root -p
```

(Use the password defined when you created the mysql server) Type this commands in mysql command line

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

Step 3 - Create the database

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

Step 4: Download the MySQL ODBC connector from Oracle. Check your operating system using: `lsb_release -a`. For Ubuntu 22.04 (x86_64), visit https://dev.mysql.com/downloads/connector/odbc/ and choose the current 8.x or 9.x release for Ubuntu 22.04. The exact filename and version number change over time, so set `VER` (below) to whatever the current Linux glibc build is called.

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

Step 5: Install the ODBC driver

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

Step 6 - Configure the ODBC connector edit the file /etc/odbc.ini to create the DSN (Data Source Name)

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

Step 7: Test the driver access using iSQL. iSQL is a command line utility to connect to the database over unixodbc.

```
isql -v astconn astdb supersecret
>show tables
```

Please, do not procede with Asterisk configuration if you can’t see the result of the isql command.

### Configuring ODBC in the Asterisk

Before you can configure the cdr_adaptive_odbc, you should first configure the ODBC resource file.

Step 1 - Connect Asterisk to ODBC. Edit the file res_odbc.conf:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

Step 2 – Restart Asterisk and test using

```
asterisk*CLI> odbc show
```

The output is shown below.

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

Step 3 – Configure the adaptive ODBC driver in /etc/asterisk/cdr_adaptive_odbc.conf

```
[cdr]
connection=cdr
table=cdr
```

Here `connection` points to the `[cdr]` connection section defined in `res_odbc.conf`, and `table` is the database table where CDRs are written.

Step 4 – Reload the module cdr_adaptive_odbc.so:

```
asterisk*CLI> reload cdr_adaptive_odbc
```

Step 5 – Make same calls and check the database fro new records. To check the database:

```
mysql -u root -p
>use astdb
>select * from cdr;
```

## Applications and functions

Plusieurs applications sont liées à la facturation.

### CDR(accountcode)

Définit un code de compte avant d’appeler une autre application dial(); par exemple : Format:

```
Set(CDR(accountcode)=account)
```

Le code de compte peut être vérifié à l’aide de la variable de canal ${CDR(accountcode)}

### CDR(amaflags)

Définit un drapeau à des fins de facturation. Les options sont default, omit, documentation et billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

Désactive l’enregistrement CDR pour le canal actuel, de sorte qu’aucun CDR n’est écrit dans le fichier ou la base de données. Le remettre à `0` réactive l’enregistrement.

```
Set(CDR_PROP(disable)=1)
```

L’application `NoCDR()` que les éditions précédentes utilisaient pour cela a été supprimée dans Asterisk 21 ; sur Asterisk 22 vous désactivez le CDR d’un canal avec `Set(CDR_PROP(disable)=1)` à la place.

### ResetCDR()

Réinitialise le Call Data Record : le temps `start` (et, si répondu, le temps `answer`) est fixé à l’heure actuelle et toutes les variables CDR sont effacées. Si l’option `v` est définie, les variables CDR sont conservées pendant la réinitialisation.

### Set(CDR(userfield)=Value)

Cette commande définit un champ utilisateur dans le CDR. Lors de l’utilisation de `cdr_adaptive_odbc`, le champ utilisateur est automatiquement stocké si une colonne `userfield` existe dans la table CDR — aucune recompilation de la source n’est nécessaire. Pour les fichiers texte CSV, vous devez modifier le code source (cdr_csv.c) et recompiler Asterisk si vous voulez utiliser les champs utilisateur.

Les éditions antérieures stockaient les CDR dans MySQL avec le module `cdr_addon_mysql` (`cdr_mysql.conf`). Ce module a été supprimé dans Asterisk 19, il n’est donc pas disponible sur Asterisk 22. Le chemin pris en charge est maintenant `cdr_adaptive_odbc` avec un pilote MySQL ODBC, qui stocke le champ utilisateur — et toute autre colonne personnalisée — nativement via son mappage adaptatif de colonnes.

### Appending to the user field

Les éditions antérieures utilisaient l’application `AppendCDRUserField()` pour ajouter des données au champ utilisateur du CDR. Cette application a été supprimée d’Asterisk ; sur Asterisk 22 vous ajoutez au champ utilisateur en le lisant puis en le re‑définissant avec la fonction `CDR`, par exemple `Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## Authentification des utilisateurs

Certaines entreprises facturent les appels à leurs employés. Dans Asterisk, vous pouvez définir un schéma d'authentification qui vous permet de facturer l'utilisateur authentifié sur le CDR. Cette authentification peut être effectuée à l'aide d'un mot de passe passé en paramètre à l'application Authenticate—un fichier de mots de passe, indiqué par un / (slash) avant le paramètre, ou une clé de base de données Asterisk (en utilisant l'option `d`). Format :

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

Options :

- a – Définit le code de compte du canal sur le mot de passe saisi.
- d – Interprète le chemin fourni comme une clé de base de données Asterisk plutôt que comme un fichier littéral.
- m – Interprète le chemin comme un fichier de lignes `accountcode:passwordhash`.
- r – Supprime la clé de base de données après une authentification réussie (valide uniquement avec `d`).

Si l'appelant échoue les trois tentatives, le canal est raccroché ; l'exécution du dialplan ne continue pas, il faut donc gérer le chemin d'échec sur la ligne après `Authenticate()`. Exemple (Appels internationaux) :

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

L'ancienne option `j` (saut à la priorité n+101 en cas d'échec) et la convention de priorité `+101` ont été supprimées d'Asterisk depuis longtemps ; un `Authenticate()` échoué se contente de raccrocher.

Pour insérer le mot de passe dans une clé DB depuis la console :

```
asterisk*CLI> database put senha 123456 1
```

## Utilisation des mots de passe de la messagerie vocale

Cette application fait la même chose que authenticate, mais utilise le fichier de configuration de la messagerie vocale pour le mot de passe.

```
VMAuthenticate([mailbox][@context][,options])
```

Si une boîte aux lettres est spécifiée, seul le mot de passe de cette boîte sera considéré comme valide. Si la boîte aux lettres n’est pas spécifiée, la variable de canal `${AUTH_MAILBOX}` sera définie avec la boîte aux lettres authentifiée. Si l’option `s` est définie, les invites initiales sont ignorées. Exemple (Appels internationaux) :

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

Les enregistrements CDR fournissent une ligne de résumé par appel. Pour un suivi d'événements plus détaillé — comme les transitions d’état de canal individuelles, les événements d’entrée/sortie de pont, et les jambes de transfert assisté — Asterisk 22 inclut **Channel Event Logging (CEL)**, configuré via `/etc/asterisk/cel.conf` et stocké via des back‑ends tels que `cel_odbc` ou `cel_custom`.

CEL complète le CDR plutôt que de le remplacer : le CDR reste la référence pour les résumés de facturation, tandis que le CEL fournit des données granulaire par événement utiles pour la détection de fraude, le suivi de la qualité et les rapports avancés.

Le modèle de configuration `cel.conf` reflète `cdr.conf` : vous activez les types d’événements souhaités dans la section `[general]` de `cel.conf`, puis configurez chaque back‑end de stockage dans son propre fichier — `cel_custom.conf` pour CSV, `cel_odbc.conf` pour une base de données ODBC (la même connexion `res_odbc.conf` utilisée pour les CDR). Vous pouvez vérifier si le CEL est actif avec `cel show status` sur la CLI.

## Résumé

Dans ce chapitre, nous avons appris comment implémenter l’enregistrement des CDR dans des fichiers texte et dans une base de données MySQL. Nous avons également vu comment définir les amaflags et les codes de compte. À la fin du chapitre, nous avons découvert comment utiliser un schéma d’authentification intégré aux CDR et à la facturation.

## Quiz

1. Par défaut, Asterisk enregistre le CDR dans le répertoire /var/log/asterisk/cdr-csv.
   - A. Faux
   - B. Vrai
2. Asterisk peut écrire les CDRs vers (cochez tout ce qui s’applique) :
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. Fichiers texte CSV
   - E. Bases de données prises en charge par unixODBC
3. Asterisk génère un CDR pour un seul type de stockage à la fois.
   - A. Faux
   - B. Vrai
4. Quels amaflags Asterisk sont disponibles ?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. Pour associer un département à un CDR, vous utilisez la commande ___, et le code de compte peut être lu avec la variable de canal ___.
6. La différence entre `Set(CDR_PROP(disable)=1)` et `ResetCDR()` est que désactiver le CDR empêche tout enregistrement d’être écrit, tandis que `ResetCDR()` réinitialise (met à zéro) l’enregistrement actuel. (L’application `NoCDR()` qui désactivait auparavant les CDR a été supprimée dans Asterisk 21.)
   - A. Faux
   - B. Vrai
7. Pour utiliser un champ défini par l’utilisateur avec le module `cdr_csv.so`, vous devez modifier le code source et recompiler Asterisk.
   - A. Faux
   - B. Vrai
8. Les trois méthodes d’authentification disponibles pour l’application Authenticate() sont :
   - A. Mot de passe
   - B. Fichier de mots de passe
   - C. Asterisk DB (dbput et dbget)
   - D. Messagerie vocale
9. Les mots de passe de messagerie vocale sont spécifiés dans une section séparée de `voicemail.conf` et ne sont pas les mêmes que les utilisateurs de messagerie vocale.
   - A. Faux
   - B. Vrai
10. Le Channel Event Logging (CEL) remplace le CDR dans Asterisk 22 — une fois le CEL activé, les résumés de facturation CDR ne sont plus produits.
    - A. Faux
    - B. Vrai

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
