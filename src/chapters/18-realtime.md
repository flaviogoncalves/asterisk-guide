# Asterisk Real-Time

As you know, the Asterisk configuration is achieved through the use of several text files in the /etc/asterisk directory. Despite the ease of using text files, there are some known drawbacks:

- The need to reload Asterisk each time the files are changed
- Increased memory usage for a large volume of users
- It is difficult to code a provisioning interface using text files
- No possibility of integration to existing databases

ARA or Asterisk Realtime, as it is known, was created by Anthony Minessale II, Mark Spencer, and Constantine Filin and was designed to allow transparent integration with SQL databases. An LDAP interface is available too. This system is also known as Asterisk External Configuration and is configured in /etc/asterisk/extconfig.conf. You can map configuration files to tables in a database (static configuration) and real-time entries for the dynamic creation of objects without the need to reload Asterisk.

## Objectives

By the end of this chapter, the reader should be able to:

- Understand advantages and limitations of Asterisk Real Time.
- Use ODBC for use with ARA
- Compile and install ARA using ODBC
- Test the system in a lab environment

## How does Asterisk Real Time work?

In the new Real Time architecture, all database-specific code was moved to channel drivers. The channel only calls a generic routine that searches the database. The result is a much simpler and cleaner process from the source code point of view. The database is accessed by three functions:

- STATIC: Used to set up a static configuration when a module is loaded.
- REALTIME: Used to search objects during a call or another event.

316 | Capítulo 1 | Introdução ao Asterisk

- UPDATE: Used to update objects.

The channel database support was not changed. There are peers and users called static (normal) and peers and users called real time (database). For the static, it doesn’t matter if it is loaded from a configuration file or from the database kept in the memory. However, the real-time peers/users are loaded only when a call is made. After the call, the peer or user is deleted. Consequently, there is no support for NAT or message waiting indicator (MWI). You can enable real-time caching using the command rtcachefriends=yes in the sip.conf file or from the static database. By doing so, you will have NAT traversal and MWI; however, if you do any updates to this peer/user, you will have to reload.

> **[2nd-ed note]** The description above (sippeers/sipusers, rtcachefriends) applies to the legacy **chan_sip** driver, which was **removed in Asterisk 21 and does not exist in Asterisk 22**. PJSIP realtime works very differently: it is built on the **Sorcery** object model, which has a built-in caching/persistence layer, so the "peer deleted after the call" and rtcachefriends caveats no longer apply. See the new "PJSIP Realtime (Sorcery)" section below for the modern equivalent.

## Configuring Asterisk Real Time

For this lab, we will assume that you already have ODBC installed from the CDR chapter. ARA is configured in the extconfig.conf text file, where two sections can be easily seen. The first one is the static configuration files section, where you can substitute the text configuration files for database tables. The second section is the realtime configuration engine, where you configure database tables for dynamic objects (peers/users). It is not unusual to use text files for the static configuration and the database for dynamic entries. In this case, the first section is untouched.

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![16-asterisk-realtime figure 1](../images/16-asterisk-realtime-img01.png)

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
;iaxusers => odbc,asterisk
;iaxpeers => odbc,asterisk
;sipusers => odbc,asterisk
;sippeers => odbc,asterisk
;voicemail => odbc,asterisk
;extensions => odbc,asterisk
;queues => odbc,asterisk
;queue_members => odbc,asterisk
```

318 | Capítulo 1 | Introdução ao Asterisk

### Static configuration section

The static configuration section is where you store the equivalent to configuration files in the database. These configurations are read during the Asterisk load. Some modules reread the database when you reload. Examples of the static configuration are:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

> **[2nd-ed note]** The original example mapped `sip.conf`, the chan_sip config file removed in Asterisk 21. On Asterisk 22 the SIP config file is `pjsip.conf`; the static-file mechanism itself is unchanged. (Static file mapping is mostly useful for files without a Sorcery/realtime equivalent — for PJSIP, prefer the per-object realtime families described later in this chapter.)

Three examples are described above. In the first one, you bind queues.conf to a table queues in the asteriskdb database. In the second example, you bind pjsip.conf to the table pjsip_conf in the database asteriskdb defined in the odbc configuration. In the last example, you bind iax.conf to an LDAP directory. MyBaseDN is the base DN to be searched. In the previous example, the application app_queue.so is loaded while MySQL driver queries the database and gets the required information.

### Real Time configuration section

The real-time configuration (second part of the extconfig.conf file) is where the configuration piece to be loaded is configured, updated, and unloaded in real time. With real time, it is not necessary to reload the configurations. The real-time syntax follows:

```
<family name> => <driver>,<database name>[,table_name]
```

Example:

```
sippeers => odbc,asterisk,sip_peers
sipusers => odbc,asterisk,sip_users
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

Here we have five configuration lines. In the first line, you bind the family sippeers to a table sip_peers in the asteriskdb MySQL database. In the last, you bind the voicemail family to the test table in the asteriskdb database. Note that sip_peers and sip_users could point to the same table.

> **[2nd-ed note]** The `sippeers`/`sipusers`/`iaxpeers`/`iaxusers` realtime families belong to **chan_sip**/**chan_iax2**. chan_sip was **removed in Asterisk 21**, so on Asterisk 22 these families no longer load any SIP channel. The modern SIP realtime families are the PJSIP/Sorcery families (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`, etc.) shown in the new "PJSIP Realtime (Sorcery)" section below. The `voicemail`, `extensions`, `queues`, and `queue_members` families are still valid in Asterisk 22.

## PJSIP Realtime (Sorcery)

On Asterisk 22, SIP endpoints are handled exclusively by the **PJSIP** stack (`res_pjsip`), which is built on the **Sorcery** object abstraction layer. Instead of a single `sippeers`/`sipusers` family, PJSIP splits a SIP account into several object types, each stored in its own realtime table:

| Sorcery object type | Realtime table | Replaces (chan_sip) |
|---------------------|----------------|---------------------|
| endpoint | ps_endpoints | most `[peer]` settings (context, codecs, etc.) |
| aor (address of record) | ps_aors | registration / `host=dynamic`, `qualify` |
| auth | ps_auths | `username` / `secret` |
| contact | ps_contacts | the dynamically registered location (was usrloc) |
| domain alias | ps_domain_aliases | — |
| endpoint identifier by IP | ps_endpoint_id_ips | matching by source IP |

Realtime for PJSIP is enabled in two places. First, map the Sorcery object types to realtime in `extconfig.conf` (these are the modern equivalents of the `sippeers` line):

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

Second, tell Sorcery to use the `realtime` wizard for those object types in `sorcery.conf`. The mapping name (here `res_pjsip`) is the module whose objects you are relocating, and the right-hand value points at the family you defined in `extconfig.conf`:

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

> **[2nd-ed note]** You can mix static and realtime objects. If you omit a type from `sorcery.conf`, that object type keeps reading from `pjsip.conf`. A common pattern is static transports/global settings in `pjsip.conf` with endpoints/aors/auths/contacts in the database.

### Creating the PJSIP realtime schema with Alembic

Asterisk ships database migrations for all of its realtime schemas under `contrib/ast-db-manage`. This is the supported way to create (and version-upgrade) the PJSIP tables — you no longer hand-write the `ps_*` table definitions. The `config` migration set contains the PJSIP/Sorcery tables.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

This creates `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`, and the other PJSIP tables with the correct columns for the running Asterisk version. (Alembic requires Python's `alembic` package plus a SQLAlchemy driver such as `pymysql` for MySQL/MariaDB or `psycopg2` for PostgreSQL.)

A minimal realtime endpoint then consists of one row in each of three tables — for example endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

After inserting the rows there is nothing to reload — the next REGISTER/INVITE pulls the objects from the database. You can confirm what realtime returned with:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## Database configuration

Now that we have configured the extconfig.conf file, let’s create the tables. Generally speaking, the database columns need to have the same fields as the configuration files. For example, for a SIP or an IAX object, such as the one described below,

```
[4000]
host=dynamic
secret=senha
context=default
context=ramais
```

The database table should look like this: name Host secret Context ipaddr port regseconds 4000 Dynamic senha default;ramais 10.1.1.1 4569 1765432 To use this with IAX, the tables need to have at least the following fields: name, port, and regseconds. You may configure other columns to the desired fields. For example, if you want the parameter callerid, create a column named callerid (the same parameter as the text file). A SIP table may look like the one below: name Host secret context Ipaddr port regseconds username 4000 Dynamic senha default 10.1.1.1 5060 1765432 4000 A voicemail table should look like this: Uniqueid mailbox Context Password email fullname 4000 Default 4000 joao@silva.com Joao Silva The uniqueid should be unique to each voicemail user and can be autoincrement. It need not have any relationship to the mailbox or context.

### Building a dial plan using Asterisk Real Time

You can also use the real-time system to create the dial plan. ARA uses the statement switch to include the real-time extensions into the normal dial plan contained in the extensions.conf file. The extension table should look like the one below: context Exten priority app Appdata Ramais 4000 dial PJSIP/4000&IAX2/4000 In the dial plan, you have to use the switch command to use the real time.

> **[2nd-ed note]** The `extensions` realtime family is unchanged in Asterisk 22, but the `Appdata` here uses the old `SIP/` technology. On Asterisk 22 (chan_sip removed) dial PJSIP channels instead, e.g. `PJSIP/4000`.

![16-asterisk-realtime figure 2](../images/16-asterisk-realtime-img02.png)

320 | Capítulo 1 | Introdução ao Asterisk

```
[local]
switch => realtime
```

or

```
[local]
Switch =>realtime/ramais@extensions
```

## Lab: Installing and creating the database tables

In this lab, we will prepare the database to receive Asterisk parameters. We will prepare just the REALTIME databases. The static configuration will be left to the configuration text files (Cool isn’t it?). Table creation in MySQL: Step 1: Get into to the MySQL database using root

```
mysql –u root –p
```

Step 2: Log in to the mysql server created in the CDR labs

```
mysql –u astdb –p
```

When asked for the password, type supersecret. Step 3: Create the necessary tables. The legacy static schema files still ship under `contrib/realtime/` (for example `/usr/src/asterisk-22.x/contrib/realtime/mysql`), but on Asterisk 22 the recommended and version-correct way to build the realtime tables — especially the PJSIP `ps_*` tables — is the **Alembic** migrations under `contrib/ast-db-manage` (see the "Creating the PJSIP realtime schema with Alembic" section above).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

> **[2nd-ed note]** The original `mysql_config.sql` import created chan_sip's `sippeers`/`sipusers` tables, which are obsolete on Asterisk 22. Use the Alembic `config` migration set so the PJSIP realtime schema matches the running version.

Use supersecret as the password. Step 4: Verify the creation of the tables

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

You should see the output below:

```
mysql> show tables;
+-----------------------------+
+-----------------------------+
+-----------------------------+
```

Step 6: Install phpmyadmin to handle database tasks

```
apt-get install phpmyadmin
```

Below are two screenshots of the utility log in screen and the table screen. Use astdb/supersecret as name and password.

![16-asterisk-realtime figure 3](../images/16-asterisk-realtime-img03.png)

![16-asterisk-realtime figure 4](../images/16-asterisk-realtime-img04.png)

322 | Capítulo 1 | Introdução ao Asterisk Step 5: Database is already configure for ODBC (since the CDR lab)

## Lab: Configuring and testing ARA

In this lab we will change the extconfig.conf configuration to reflect our database configuration and tables. Step 1: Configure extconfig.conf and reload Asterisk

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

> **[2nd-ed note]** On Asterisk 22, replace the chan_sip `sippeers`/`iaxpeers` lines with the PJSIP/Sorcery families shown above, and add the matching `sorcery.conf` mappings (see the "PJSIP Realtime (Sorcery)" section). The `voicemail` and `extensions` families are unchanged.

Step 2: Real Time extension test. Using phpMyAdmin, create a new 6010 endpoint by inserting one row into each of `ps_auths`, `ps_aors`, and `ps_endpoints`, then try to register this endpoint with a softphone.

```
-- ps_auths
id=6010-auth, auth_type=userpass, username=6010, password=supersecret
-- ps_aors
id=6010, max_contacts=1
-- ps_endpoints
id=6010, transport=transport-udp, aors=6010, auth=6010-auth
```

![16-asterisk-realtime figure 5](../images/16-asterisk-realtime-img05.png)

![16-asterisk-realtime figure 6](../images/16-asterisk-realtime-img06.png)

The remaining account settings are spread across the PJSIP objects. The legacy chan_sip block (context, host=dynamic, disallow/allow, dtmfmode) maps to the PJSIP fields below:

```
-- ps_endpoints columns for 6010
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733        ; was dtmfmode=rfc2833
direct_media=no
-- ps_aors: host=dynamic has no direct field; dynamic registration
--          is implicit, the registered location is stored in ps_contacts
```

> **[2nd-ed note]** In PJSIP the `rfc2833` DTMF mode is named `rfc4733` (`dtmf_mode=rfc4733`). There is no `host=dynamic` setting: an AOR accepts dynamic registrations by default and the contact is written to `ps_contacts` on REGISTER.

Step 3: Try to register the new phone Step 4: Include the extensions in the database

```
mysql -u asterisk -p
```

Enter password:

![16-asterisk-realtime figure 7](../images/16-asterisk-realtime-img07.png)

324 | Capítulo 1 | Introdução ao Asterisk --> Use asterisk when asked. Use phpadmin to include an extension in the database. If you prefer, use the following commands instead in the MySQL client interface.

```
use astdb;
insert into extensions(id, context, exten, priority, app, appdata) VALUES
('1','teste', '6007','1','Dial','PJSIP/bria');
```

Step 8: Include Asterisk Real Time in the dial plan. In the context default:

```
switch => realtime/teste@extensions
```

Reload the extensions to activate the change.

```
asterisk-server*CLI>extensions reload
```

Step 5: Reconfigure one of the phones to the username bria, if you have not already done so. Step 6: Dial 6007 from an existent phone the bria should ring.

## Summary

In this chapter, you have learned that Asterisk Real Time allows you to put your configurations into a database. Databases supported are MySQL and any other Unix ODBC-supported databases. The configuration is divided into static and real time. Static configuration replaces the configuration files, while the real-time configuration creates dynamic objects that are loaded only when a call or other related event happens. We concluded with a practical lab on how to install and configure ARA.

## Quiz

1. Asterisk Realtime is part of the standard Asterisk distribution.
   - A. True
   - B. False
2. A database server's connection parameters are configured in the file:
   - A. extensions.conf
   - B. sip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. The `extconfig.conf` file configures the tables used by Realtime. It has two distinct sections (check two):
   - A. Static configuration
   - B. Realtime configuration
   - C. Outbound routes
   - D. IP addresses and database ports
4. In static configuration, once the objects are loaded from the database they are kept in Asterisk's memory and refreshed only on start or reload.
   - A. True
   - B. False
5. Unlike the old chan_sip realtime, PJSIP realtime (Sorcery) fully supports `qualify` and MWI for realtime endpoints.
   - A. True
   - B. False
6. In PJSIP realtime, which tables hold the endpoints and their registered contacts?
   - A. `ps_endpoints` and `ps_contacts`
   - B. `sippeers` and `sipregs`
   - C. `ps_config` and `ps_data`
   - D. `extconfig` and `res_odbc`
7. You can still use text configuration files even after enabling ARA.
   - A. True
   - B. False
8. phpMyAdmin is mandatory when you use Realtime.
   - A. True
   - B. False
9. The database must be created with every field that exists in the configuration file.
   - A. True
   - B. False

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B
