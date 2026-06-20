# Asterisk Real-Time

जैसा कि आप जानते हैं, Asterisk का कॉन्फ़िगरेशन /etc/asterisk डायरेक्टरी में कई टेक्स्ट फ़ाइलों के उपयोग से किया जाता है। टेक्स्ट फ़ाइलों के उपयोग की सरलता के बावजूद, कुछ ज्ञात कमियां हैं:

- फ़ाइलों में परिवर्तन होने पर हर बार Asterisk को रीलोड करना पड़ता है
- बड़ी संख्या में उपयोगकर्ताओं के लिए मेमोरी उपयोग बढ़ जाता है
- टेक्स्ट फ़ाइलों का उपयोग करके प्रोविज़निंग इंटरफ़ेस बनाना कठिन है
- मौजूदा डेटाबेस के साथ एकीकरण की कोई संभावना नहीं है

ARA या Asterisk Realtime, जैसा कि इसे जाना जाता है, एंथनी मिनेसाले II, मार्क स्पेंसर, और कॉन्स्टैंटिन फिलिन द्वारा बनाया गया था और इसे SQL डेटाबेस के साथ पारदर्शी एकीकरण की अनुमति देने के लिए डिज़ाइन किया गया था। एक LDAP इंटरफ़ेस भी उपलब्ध है। इस सिस्टम को Asterisk External Configuration भी कहा जाता है और यह /etc/asterisk/extconfig.conf में कॉन्फ़िगर किया जाता है। आप कॉन्फ़िगरेशन फ़ाइलों को डेटाबेस में टेबलों से (स्थैतिक कॉन्फ़िगरेशन) मैप कर सकते हैं और वास्तविक‑समय प्रविष्टियों के माध्यम से ऑब्जेक्ट्स का डायनामिक निर्माण कर सकते हैं, बिना Asterisk को रीलोड किए।

## Objectives

- Understand advantages and limitations of Asterisk Real Time.
- Use ODBC for use with ARA
- Compile and install ARA using ODBC
- Test the system in a lab environment

## How does Asterisk Real Time work?

नए Real Time आर्किटेक्चर में, सभी डेटाबेस‑विशिष्ट कोड को चैनल ड्राइवरों में ले जाया गया है। चैनल केवल एक सामान्य रूटीन को कॉल करता है जो डेटाबेस को खोजता है। परिणामस्वरूप स्रोत कोड के दृष्टिकोण से प्रक्रिया बहुत सरल और साफ़ हो गई है। डेटाबेस को तीन फ़ंक्शन द्वारा एक्सेस किया जाता है:

- STATIC: जब कोई मॉड्यूल लोड होता है तो स्थिर कॉन्फ़िगरेशन सेट करने के लिए उपयोग किया जाता है।
- REALTIME: कॉल या किसी अन्य इवेंट के दौरान ऑब्जेक्ट्स को खोजने के लिए उपयोग किया जाता है।


- UPDATE: ऑब्जेक्ट्स को अपडेट करने के लिए उपयोग किया जाता है।

Asterisk 22 पर, SIP एंडपॉइंट्स **PJSIP** स्टैक (`res_pjsip`) द्वारा संभाले जाते हैं, जो **Sorcery** ऑब्जेक्ट मॉडल पर निर्मित है। `realtime` विज़ार्ड के साथ, Sorcery प्रत्येक PJSIP ऑब्जेक्ट को मांग पर डेटाबेस से लोड करता है, और ये ऑब्जेक्ट फिर सामान्य रूप से कॉन्फ़िगर किए गए PJSIP ऑब्जेक्ट्स के रूप में मौजूद होते हैं — न कि पुराने SIP ड्राइवर द्वारा प्रत्येक कॉल के बाद हटाए जाने वाले अस्थायी realtime पीयर्स के रूप में।

क्योंकि वे वास्तविक ऑब्जेक्ट्स हैं, NAT ट्रैवर्सल, क्वालिफ़ाई, और मैसेज वेटिंग इंडिकेशन (MWI) सभी realtime एंडपॉइंट्स के लिए सामान्य रूप से काम करते हैं। (Sorcery को अतिरिक्त रूप से `memory_cache` विज़ार्ड के माध्यम से ऑब्जेक्ट्स को मेमोरी में कैश करने के लिए कहा जा सकता है, लेकिन यह ऑप्ट‑इन है और realtime लोडिंग से अलग है।) जब आप डेटाबेस में किसी ऑब्जेक्ट को बदलते हैं, तो परिवर्तन अगले लुकअप पर उठाया जाता है; आपको हर संपादन के बाद री‑लोड करने की आवश्यकता नहीं है। (रिटायर किया गया `chan_sip` realtime मॉडल, उसके `sippeers`/`sipusers` परिवारों के साथ, केवल *Legacy Channels* अध्याय में कवर किया गया है।)

## Configuring Asterisk Real Time

इस लैब के लिए, हम मान लेंगे कि आपके पास पहले से ही CDR अध्याय से ODBC स्थापित है। ARA को extconfig.conf टेक्स्ट फ़ाइल में कॉन्फ़िगर किया जाता है, जहाँ दो सेक्शन आसानी से देखे जा सकते हैं। पहला स्थैतिक कॉन्फ़िगरेशन फ़ाइलों का सेक्शन है, जहाँ आप टेक्स्ट कॉन्फ़िगरेशन फ़ाइलों को डेटाबेस टेबल्स से बदल सकते हैं। दूसरा सेक्शन रीयल‑टाइम कॉन्फ़िगरेशन इंजन है, जहाँ आप डेटाबेस टेबल्स को डायनामिक ऑब्जेक्ट्स (peers/users) के लिए कॉन्फ़िगर करते हैं। स्थैतिक कॉन्फ़िगरेशन के लिए टेक्स्ट फ़ाइलें और डायनामिक एंट्रीज़ के लिए डेटाबेस का उपयोग करना असामान्य नहीं है। इस मामले में, पहला सेक्शन अपरिवर्तित रहता है।

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

### Static configuration section

स्थैतिक कॉन्फ़िगरेशन सेक्शन वह जगह है जहाँ आप डेटाबेस में कॉन्फ़िगरेशन फ़ाइलों के समकक्ष को संग्रहीत करते हैं। ये कॉन्फ़िगरेशन Asterisk लोड होने के दौरान पढ़े जाते हैं। कुछ मॉड्यूल जब आप री‑लोड करते हैं तो डेटाबेस को फिर से पढ़ते हैं। स्थैतिक कॉन्फ़िगरेशन के उदाहरण हैं:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

स्थैतिक फ़ाइल मैपिंग उन कॉन्फ़िगरेशन फ़ाइलों के लिए सबसे उपयोगी है जिनका कोई ऑब्जेक्ट‑वाइज़ रीयल‑टाइम समकक्ष नहीं होता। PJSIP के लिए, इस अध्याय में बाद में वर्णित ऑब्जेक्ट‑वाइज़ रीयल‑टाइम फ़ैमिलीज़ (`ps_endpoints`, `ps_aors`, आदि) को प्राथमिकता दें, बजाय पूरे `pjsip.conf` को स्थैतिक फ़ाइल के रूप में मैप करने के।

ऊपर तीन उदाहरण वर्णित हैं। पहले में, आप queues.conf को asteriskdb डेटाबेस में queues टेबल से बाइंड करते हैं। दूसरे उदाहरण में, आप pjsip.conf को odbc कॉन्फ़िगरेशन में परिभाषित asteriskdb डेटाबेस की pjsip_conf टेबल से बाइंड करते हैं। अंतिम उदाहरण में, आप iax.conf को एक LDAP डायरेक्टरी से बाइंड करते हैं। MyBaseDN वह बेस DN है जिसे खोजा जाना है। पिछले उदाहरण में, एप्लिकेशन app_queue.so लोड होता है जबकि MySQL ड्राइवर डेटाबेस को क्वेरी करके आवश्यक जानकारी प्राप्त करता है।

### Real Time configuration section

रीयल‑टाइम कॉन्फ़िगरेशन (extconfig.conf फ़ाइल का दूसरा भाग) वह जगह है जहाँ लोड होने वाले कॉन्फ़िगरेशन टुकड़े को रीयल‑टाइम में कॉन्फ़िगर, अपडेट और अनलोड किया जाता है। रीयल‑टाइम के साथ, कॉन्फ़िगरेशन को री‑लोड करने की आवश्यकता नहीं होती। रीयल‑टाइम सिंटैक्स इस प्रकार है:

```
<family name> => <driver>,<database name>[,table_name]
```

उदाहरण:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

यहाँ हमारे पास पाँच कॉन्फ़िगरेशन लाइन्स हैं। पहली लाइन में, आप PJSIP/Sorcery फ़ैमिली `ps_endpoints` को asteriskdb डेटाबेस में टेबल `ps_endpoints` से बाइंड करते हैं। अंतिम में, आप voicemail फ़ैमिली को asteriskdb डेटाबेस में test टेबल से बाइंड करते हैं। प्रत्येक PJSIP ऑब्जेक्ट टाइप (endpoint, aor, auth, contact) की अपनी फ़ैमिली और टेबल होती है; पूरा सेट नीचे "PJSIP Realtime (Sorcery)" सेक्शन में दिखाया गया है। `voicemail`, `extensions`, `queues`, और `queue_members` फ़ैमिली अभी भी Asterisk 22 में वैध हैं।

## PJSIP Realtime (Sorcery)

On Asterisk 22, SIP endpoints are handled exclusively by the **PJSIP** stack (`res_pjsip`), which is built on the **Sorcery** object abstraction layer. Rather than a single SIP "peer", PJSIP splits a SIP account into several object types, each stored in its own realtime table:

| Sorcery object type | Realtime table | What it holds |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | प्रति‑खाता सेटिंग्स (context, codecs, DTMF, आदि) |
| aor (address of record) | ps_aors | पंजीकरण सीमाएँ और `qualify` सेटिंग्स |
| auth | ps_auths | `username` / `password` क्रेडेंशियल्स |
| contact | ps_contacts | गतिशील रूप से पंजीकृत स्थान |
| domain alias | ps_domain_aliases | एक endpoint के लिए वैकल्पिक SIP डोमेन्स |
| endpoint identifier by IP | ps_endpoint_id_ips | स्रोत IP द्वारा endpoint से मिलान |

Realtime for PJSIP is enabled in two places. First, map the Sorcery object types to realtime in `extconfig.conf`:

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

You can mix static and realtime objects. If you omit a type from `sorcery.conf`, that object type keeps reading from `pjsip.conf`. A common pattern is to keep static transports and global settings in `pjsip.conf` while storing endpoints, aors, auths, and contacts in the database.

### Creating the PJSIP realtime schema with Alembic

Asterisk ships database migrations for all of its realtime schemas under `contrib/ast-db-manage`. This is the supported way to create (and version-upgrade) the PJSIP tables — you no longer hand-write the `ps_*` table definitions. The `config` migration set contains the PJSIP/Sorcery tables.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
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

अब जब हमने `extconfig.conf` फ़ाइल को कॉन्फ़िगर कर लिया है, चलिए टेबल्स बनाते हैं। सामान्यतः, प्रत्येक डेटाबेस कॉलम संबंधित कॉन्फ़िगरेशन फ़ाइल के विकल्प नाम से मेल खाता है। PJSIP `ps_*` टेबल्स इस नियम का पालन करती हैं: हर `ps_endpoints` कॉलम का नाम एक `pjsip.conf` endpoint विकल्प के बाद रखा जाता है, हर `ps_auths` कॉलम का नाम एक auth विकल्प के बाद रखा जाता है, आदि। उदाहरण के लिए, नीचे दिया गया `pjsip.conf` endpoint,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

तीन टेबल्स में एक पंक्ति के रूप में संग्रहीत होता है। `ps_endpoints` पंक्ति में `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000` रखी जाती है; `ps_auths` पंक्ति में `id=4000, auth_type=userpass, username=4000, password=supersecret` रखी जाती है; और `ps_aors` पंक्ति में `id=4000, max_contacts=1` रखी जाती है। आपको केवल उन कॉलम्स को भरना है जो आप वास्तव में उपयोग करते हैं — किसी भी कॉलम को NULL छोड़ने पर वह विकल्प का डिफ़ॉल्ट मान ले लेता है। यदि आप उदाहरण के तौर पर किसी endpoint पर `callerid` पैरामीटर चाहते हैं, तो `callerid` कॉलम को `ps_endpoints` में भरें (कॉलम का नाम वही है जो `pjsip.conf` विकल्प नाम है)।

एक voicemail टेबल भी इसी विचार का पालन करती है। इसके कॉलम `voicemail.conf` फ़ील्ड्स से मैप होते हैं:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid` प्रत्येक voicemail उपयोगकर्ता के लिए अद्वितीय होना चाहिए और ऑटोइन्क्रिमेंट हो सकता है। इसे mailbox या context से कोई संबंध रखने की आवश्यकता नहीं है।

### Building a dial plan using Asterisk Real Time

आप रियल‑टाइम सिस्टम का उपयोग करके डायल प्लान भी बना सकते हैं। ARA `switch` स्टेटमेंट का उपयोग करके रियल‑टाइम एक्सटेंशन को सामान्य डायल प्लान में शामिल करता है, जो `extensions.conf` फ़ाइल में रहता है। एक्सटेंशन टेबल नीचे दिखाए अनुसार होनी चाहिए:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions` रियल‑टाइम फ़ैमिली Asterisk 22 में अपरिवर्तित है; बस यह सुनिश्चित करें कि `appdata` कॉलम PJSIP चैनल डायल करता है, उदाहरण के तौर पर `PJSIP/4000`। डायल प्लान में, रियल‑टाइम उपयोग करने के लिए आपको `switch` कमांड का उपयोग करना होगा।

![Building a dial plan with Asterisk Real Time: extensions.conf uses a `switch => realtime` statement to pull extension rows (context, exten, priority, app, data) from a database table instead of from the text file.](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

or

```
[local]
switch => realtime/from-internal@extensions
```

## Lab: Installing and creating the database tables

इस लैब में, हम Asterisk पैरामीटर प्राप्त करने के लिए डेटाबेस तैयार करेंगे। हम केवल REALTIME टेबल्स को तैयार करेंगे। स्थिर कॉन्फ़िगरेशन को कॉन्फ़िगरेशन टेक्स्ट फ़ाइलों में छोड़ दिया जाएगा (कूल, है ना?)। MySQL में टेबल निर्माण इस प्रकार है।

Step 1: Get into the MySQL database as root.

```
mysql -u root -p
```

Step 2: Log in to the MySQL server created in the CDR labs.

```
mysql -u astdb -p
```

जब पासवर्ड पूछा जाए, तो supersecret टाइप करें।

Step 3: Create the necessary tables. The legacy static schema files still ship under `contrib/realtime/` (for example `/usr/src/asterisk-22.x/contrib/realtime/mysql`), but on Asterisk 22 the recommended and version-correct way to build the realtime tables — especially the PJSIP `ps_*` tables — is the **Alembic** migrations under `contrib/ast-db-manage` (see the "Creating the PJSIP realtime schema with Alembic" section above).

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

The Alembic `config` migration set builds the PJSIP `ps_*` tables (along with `voicemail`, `extensions`, and the other realtime schemas) with exactly the columns the running Asterisk version expects, so the schema always matches the build.

Use supersecret as the password.

Step 4: Verify the creation of the tables.

```
mysql -u astdb -p astdb
mysql>use astdb;
mysql>show tables;
```

आपको PJSIP `ps_*` टेबल्स (Alembic `config` migration द्वारा बनाई गई) दिखनी चाहिए, साथ ही `voicemail`, `extensions`, और अन्य realtime टेबल्स:

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

(Alembic इन टेबल्स से अधिक टेबल्स बनाता है — ऊपर की सूची में केवल इस लैब से संबंधित टेबल्स दिखाए गए हैं।)

Step 5: The database is already configured for ODBC (since the CDR lab), so no further ODBC setup is needed here.

Step 6: Inspect and populate the tables from the MySQL client. You do not need a graphical tool such as phpMyAdmin — every step in this chapter is plain, copy-pasteable SQL run from the `mysql` command line. Connect to the `astdb` database (use `supersecret` when prompted):

```
mysql -u astdb -p astdb
```

आप किसी भी समय टेबल के कॉलम की पुष्टि `DESCRIBE` से कर सकते हैं, उदाहरण के लिए:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

ये टेबल्स Alembic `config` migration द्वारा बनाई गई हैं, इसलिए उनके कॉलम पहले से ही चल रहे Asterisk संस्करण के `pjsip.conf` विकल्प नामों से मेल खाते हैं — आपको केवल उन कॉलमों को भरना है जिनकी आपको आवश्यकता है।

## Lab: Configuring and testing ARA

In this lab we will change the extconfig.conf configuration to reflect our database configuration and tables.

Step 1: Configure extconfig.conf and reload Asterisk.

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

Note the `ps_endpoints`, `ps_aors`, `ps_auths`, and `ps_contacts` families above; together with the matching `sorcery.conf` mappings (see the "PJSIP Realtime (Sorcery)" section) they make PJSIP read its accounts from the database. The `voicemail` and `extensions` families round out the example.

Step 2: Real Time extension test. Create a new `6010` endpoint by inserting one row into each of `ps_auths`, `ps_aors`, and `ps_endpoints`, then try to register this endpoint with a softphone. Run the following SQL in the `mysql` client (`mysql -u astdb -p astdb`):

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

The three rows together describe one SIP account. The remaining account settings are spread across the PJSIP objects: context, codecs, DTMF mode, and media handling live on the endpoint (the last six columns above); dynamic registration lives on the AOR. There is no separate "dynamic" flag — an AOR accepts dynamic REGISTERs as long as `max_contacts` is greater than zero, and each registered location is written to `ps_contacts`.

In PJSIP the RFC 2833 / RFC 4733 out-of-band DTMF mode is named `rfc4733`, and `dtmf_mode=rfc4733` is the default — so the `dtmf_mode` column above is optional and shown only for clarity.

Step 3: Try to register the new phone with a softphone using username `6010` and password `supersecret`. Confirm the registration on the Asterisk CLI:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

Step 4: Include the extensions in the database.

```
mysql -u astdb -p
```

Enter password:

Use supersecret when asked, then insert the extension row from the MySQL client:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

Step 5: Include Asterisk Real Time in the dial plan. In the context `default`:

```
switch => realtime/test@extensions
```

Reload the extensions to activate the change.

```
asterisk-server*CLI> extensions reload
```

Step 6: Reconfigure one of the phones to the username `bria`, if you have not already done so.

Step 7: Dial 6007 from an existing phone; the `bria` phone should ring.

## Summary

इस अध्याय में, आपने सीखा कि Asterisk Real Time आपको अपनी कॉन्फ़िगरेशन को डेटाबेस में रखने की अनुमति देता है। Asterisk ODBC (जो किसी भी UnixODBC‑समर्थित डेटाबेस तक पहुँचता है, जिसमें MySQL/MariaDB और SQLite शामिल हैं) और PostgreSQL के लिए मूल realtime ड्राइवर प्रदान करता है, साथ ही डायरेक्टरी बैकएंड के लिए एक LDAP realtime ड्राइवर भी। MySQL/MariaDB ODBC के माध्यम से पहुँचा जाता है, जैसा कि हमने इस अध्याय में किया (एक समर्पित `res_config_mysql` ऐड‑ऑन भी मौजूद है, लेकिन वह कोर बिल्ड के बाहर रहता है, इसलिए ODBC सामान्य मार्ग है)। कॉन्फ़िगरेशन को स्थैतिक और realtime में विभाजित किया गया है। स्थैतिक कॉन्फ़िगरेशन फ़ाइलों को बदलती है, जबकि realtime कॉन्फ़िगरेशन गतिशील ऑब्जेक्ट बनाती है जो केवल कॉल या अन्य संबंधित इवेंट होने पर लोड होते हैं। हमने ARA को स्थापित और कॉन्फ़िगर करने के व्यावहारिक लैब के साथ निष्कर्ष निकाला।

## Quiz

1. Asterisk Realtime मानक Asterisk वितरण का हिस्सा है।
   - A. True
   - B. False
2. डेटाबेस सर्वर के कनेक्शन पैरामीटर किस फ़ाइल में कॉन्फ़िगर किए जाते हैं:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf` फ़ाइल Realtime द्वारा उपयोग की जाने वाली तालिकाओं को कॉन्फ़िगर करती है। इसमें दो अलग-अलग सेक्शन होते हैं (दोनों चुनें):
   - A. Static configuration
   - B. Realtime configuration
   - C. Outbound routes
   - D. IP addresses and database ports
4. स्थिर कॉन्फ़िगरेशन में, एक बार जब ऑब्जेक्ट्स डेटाबेस से लोड हो जाते हैं, वे Asterisk की मेमोरी में रखे जाते हैं और केवल स्टार्ट या रीलोड पर रीफ़्रेश होते हैं।
   - A. True
   - B. False
5. PJSIP realtime (Sorcery) पूरी तरह से `qualify` और MWI को realtime endpoints के लिए सपोर्ट करता है, क्योंकि Sorcery उन्हें सामान्य रूप से कॉन्फ़िगर किए गए PJSIP ऑब्जेक्ट्स के रूप में लोड करता है न कि प्रत्येक कॉल के बाद उन्हें हटाता है जैसा कि पुराने SIP realtime peers करते थे।
   - A. True
   - B. False
6. PJSIP realtime में, कौन सी तालिकाएँ endpoints और उनके पंजीकृत संपर्कों को रखती हैं?
   - A. `ps_endpoints` and `ps_contacts`
   - B. `ps_peers` and `ps_registry`
   - C. `ps_config` and `ps_data`
   - D. `extconfig` and `res_odbc`
7. आप ARA को सक्षम करने के बाद भी टेक्स्ट कॉन्फ़िगरेशन फ़ाइलें उपयोग कर सकते हैं।
   - A. True
   - B. False
8. phpMyAdmin Realtime उपयोग करने पर अनिवार्य है।
   - A. True
   - B. False
9. डेटाबेस को कॉन्फ़िगरेशन फ़ाइल में मौजूद प्रत्येक फ़ील्ड के साथ बनाया जाना चाहिए।
   - A. True
   - B. False
10. Asterisk 22 पर, PJSIP realtime तालिकाएँ (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`) बनाने का अनुशंसित, संस्करण‑सही तरीका क्या है?
    - A. Hand-write the `CREATE TABLE` statements for each `ps_*` table
    - B. Import the legacy `mysql_config.sql` from `contrib/realtime/`
    - C. Run the Alembic `config` migrations under `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)
    - D. The tables are created automatically the first time Asterisk starts

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
