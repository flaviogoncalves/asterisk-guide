# Asterisk Real-Time

जैसा कि आप जानते हैं, Asterisk कॉन्फ़िगरेशन /etc/asterisk डायरेक्टरी में कई टेक्स्ट फ़ाइलों के उपयोग के माध्यम से प्राप्त किया जाता है। टेक्स्ट फ़ाइलों का उपयोग करने में आसानी के बावजूद, कुछ ज्ञात कमियां हैं:

- हर बार फ़ाइलें बदलने पर Asterisk को रिलोड करने की आवश्यकता
- उपयोगकर्ताओं की बड़ी संख्या के लिए मेमोरी का अधिक उपयोग
- टेक्स्ट फ़ाइलों का उपयोग करके प्रोविज़निंग इंटरफ़ेस को कोड करना कठिन है
- मौजूदा डेटाबेस के साथ एकीकरण की कोई संभावना नहीं

ARA या Asterisk Realtime, जैसा कि इसे जाना जाता है, को Anthony Minessale II, Mark Spencer और Constantine Filin द्वारा बनाया गया था और इसे SQL डेटाबेस के साथ पारदर्शी एकीकरण की अनुमति देने के लिए डिज़ाइन किया गया था। एक LDAP इंटरफ़ेस भी उपलब्ध है। इस सिस्टम को Asterisk External Configuration के रूप में भी जाना जाता है और इसे /etc/asterisk/extconfig.conf में कॉन्फ़िगर किया जाता है। आप कॉन्फ़िगरेशन फ़ाइलों को डेटाबेस में तालिकाओं (स्टेटिक कॉन्फ़िगरेशन) और Asterisk को रिलोड करने की आवश्यकता के बिना ऑब्जेक्ट्स के गतिशील निर्माण के लिए रीयल-टाइम प्रविष्टियों के साथ मैप कर सकते हैं।

## उद्देश्य

इस अध्याय के अंत तक, पाठक को निम्नलिखित में सक्षम होना चाहिए:

- Asterisk Real Time के लाभों और सीमाओं को समझना।
- ARA के साथ उपयोग के लिए ODBC का उपयोग करना।
- ODBC का उपयोग करके ARA को कंपाइल और इंस्टॉल करना।
- लैब वातावरण में सिस्टम का परीक्षण करना।

## Asterisk Real Time कैसे काम करता है?

नई Real Time आर्किटेक्चर में, सभी डेटाबेस-विशिष्ट कोड को चैनल ड्राइवरों में ले जाया गया था। चैनल केवल एक सामान्य रूटीन को कॉल करता है जो डेटाबेस को खोजता है। सोर्स कोड के दृष्टिकोण से परिणाम बहुत सरल और स्वच्छ प्रक्रिया है। डेटाबेस को तीन कार्यों द्वारा एक्सेस किया जाता है:

- STATIC: मॉड्यूल लोड होने पर स्टेटिक कॉन्फ़िगरेशन सेट करने के लिए उपयोग किया जाता है।
- REALTIME: कॉल या किसी अन्य ईवेंट के दौरान ऑब्जेक्ट्स को खोजने के लिए उपयोग किया जाता है।
- UPDATE: ऑब्जेक्ट्स को अपडेट करने के लिए उपयोग किया जाता है।

Asterisk 22 पर, SIP endpoints को **PJSIP** स्टैक (`res_pjsip`) द्वारा नियंत्रित किया जाता है, जो **Sorcery** ऑब्जेक्ट मॉडल पर बनाया गया है। `realtime` विज़ार्ड के साथ, Sorcery प्रत्येक PJSIP ऑब्जेक्ट को मांग पर डेटाबेस से लोड करता है, और वे ऑब्जेक्ट फिर सामान्य कॉन्फ़िगर किए गए PJSIP ऑब्जेक्ट के रूप में मौजूद होते हैं — न कि उन थ्रोअवे रीयल-टाइम पीयर्स के रूप में जिन्हें पुराना SIP ड्राइवर प्रत्येक कॉल के बाद हटा देता था। चूंकि वे वास्तविक ऑब्जेक्ट हैं, NAT traversal, qualify, और message waiting indication (MWI) सभी रीयल-टाइम endpoints के लिए सामान्य रूप से काम करते हैं। (Sorcery को अतिरिक्त रूप से `memory_cache` विज़ार्ड के माध्यम से मेमोरी में ऑब्जेक्ट्स को कैश करने के लिए कहा जा सकता है, लेकिन यह ऑप्ट-इन है और रीयल-टाइम लोडिंग से अलग है।) जब आप डेटाबेस में कोई ऑब्जेक्ट बदलते हैं, तो परिवर्तन अगले लुकअप पर पिक कर लिया जाता है; आपको हर संपादन के बाद रिलोड करने की आवश्यकता नहीं है। (सेवानिवृत्त `chan_sip` रीयल-टाइम मॉडल, अपने `sippeers`/`sipusers` परिवारों के साथ, केवल *Legacy Channels* अध्याय में कवर किया गया है।)

## Asterisk Real Time को कॉन्फ़िगर करना

इस लैब के लिए, हम मान लेंगे कि आपके पास CDR अध्याय से ODBC पहले से इंस्टॉल है। ARA को extconfig.conf टेक्स्ट फ़ाइल में कॉन्फ़िगर किया गया है, जहाँ दो सेक्शन आसानी से देखे जा सकते हैं। पहला स्टेटिक कॉन्फ़िगरेशन फ़ाइल सेक्शन है, जहाँ आप टेक्स्ट कॉन्फ़िगरेशन फ़ाइलों को डेटाबेस तालिकाओं के लिए प्रतिस्थापित कर सकते हैं। दूसरा सेक्शन रीयल-टाइम कॉन्फ़िगरेशन इंजन है, जहाँ आप गतिशील ऑब्जेक्ट्स (peers/users) के लिए डेटाबेस तालिकाओं को कॉन्फ़िगर करते हैं। स्टेटिक कॉन्फ़िगरेशन के लिए टेक्स्ट फ़ाइलों और गतिशील प्रविष्टियों के लिए डेटाबेस का उपयोग करना असामान्य नहीं है। इस मामले में, पहला सेक्शन अछूता रहता है।

```
extconfig.conf file format:
;
; Static and realtime external configuration
; engine configuration
;
; Please read doc/README.extconfig for basic table
; formatting information.
```

![Asterisk Real Time आर्किटेक्चर: कॉन्फ़िगरेशन फ़ाइलें और स्टेटिक डेटाबेस तालिकाएं तब लोड होती हैं जब Asterisk शुरू होता है, जबकि रीयल-टाइम डेटाबेस तालिकाएं गतिशील कॉन्फ़िगरेशन प्रदान करती हैं जिसे कॉल के दौरान मांग पर पढ़ा जाता है।](../images/18-realtime-fig01.png)

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

### स्टेटिक कॉन्फ़िगरेशन सेक्शन

स्टेटिक कॉन्फ़िगरेशन सेक्शन वह जगह है जहाँ आप डेटाबेस में कॉन्फ़िगरेशन फ़ाइलों के समकक्ष स्टोर करते हैं। ये कॉन्फ़िगरेशन Asterisk लोड के दौरान पढ़े जाते हैं। कुछ मॉड्यूल रिलोड करने पर डेटाबेस को फिर से पढ़ते हैं। स्टेटिक कॉन्फ़िगरेशन के उदाहरण हैं:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

स्टेटिक फ़ाइल मैपिंग उन कॉन्फ़िगरेशन फ़ाइलों के लिए सबसे उपयोगी है जिनका कोई प्रति-ऑब्जेक्ट रीयल-टाइम समकक्ष नहीं है। PJSIP के लिए, पूरे `pjsip.conf` को स्टेटिक फ़ाइल के रूप में मैप करने के बजाय इस अध्याय में बाद में वर्णित प्रति-ऑब्जेक्ट रीयल-टाइम परिवारों (`ps_endpoints`, `ps_aors`, आदि) को प्राथमिकता दें।

ऊपर तीन उदाहरण वर्णित हैं। पहले में, आप queues.conf को asteriskdb डेटाबेस में queues तालिका से बांधते हैं। दूसरे उदाहरण में, आप pjsip.conf को odbc कॉन्फ़िगरेशन में परिभाषित डेटाबेस asteriskdb में pjsip_conf तालिका से बांधते हैं। अंतिम उदाहरण में, आप iax.conf को LDAP डायरेक्टरी से बांधते हैं। MyBaseDN वह आधार DN है जिसे खोजा जाना है। पिछले उदाहरण में, एप्लिकेशन app_queue.so लोड होता है जबकि MySQL ड्राइवर डेटाबेस से पूछताछ करता है और आवश्यक जानकारी प्राप्त करता है।

### Real Time कॉन्फ़िगरेशन सेक्शन

रीयल-टाइम कॉन्फ़िगरेशन (extconfig.conf फ़ाइल का दूसरा भाग) वह जगह है जहाँ लोड किए जाने वाले कॉन्फ़िगरेशन पीस को रीयल-टाइम में कॉन्फ़िगर, अपडेट और अनलोड किया जाता है। रीयल-टाइम के साथ, कॉन्फ़िगरेशन को रिलोड करना आवश्यक नहीं है। रीयल-टाइम सिंटैक्स इस प्रकार है:

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

यहाँ हमारे पास पाँच कॉन्फ़िगरेशन लाइनें हैं। पहली लाइन में, आप PJSIP/Sorcery परिवार `ps_endpoints` को asteriskdb डेटाबेस में `ps_endpoints` तालिका से बांधते हैं। अंतिम में, आप voicemail परिवार को asteriskdb डेटाबेस में test तालिका से बांधते हैं। प्रत्येक PJSIP ऑब्जेक्ट प्रकार (endpoint, aor, auth, contact) का अपना परिवार और तालिका होती है; पूरा सेट नीचे "PJSIP Realtime (Sorcery)" सेक्शन में दिखाया गया है। `voicemail`, `extensions`, `queues`, और `queue_members` परिवार Asterisk 22 में अभी भी मान्य हैं।

## PJSIP Realtime (Sorcery)

Asterisk 22 पर, SIP endpoints को विशेष रूप से **PJSIP** स्टैक (`res_pjsip`) द्वारा नियंत्रित किया जाता है, जो **Sorcery** ऑब्जेक्ट एब्स्ट्रैक्शन लेयर पर बनाया गया है। एक एकल SIP "peer" के बजाय, PJSIP एक SIP खाते को कई ऑब्जेक्ट प्रकारों में विभाजित करता है, जिनमें से प्रत्येक अपनी रीयल-टाइम तालिका में संग्रहीत होता है:

| Sorcery ऑब्जेक्ट प्रकार | रीयल-टाइम तालिका | यह क्या रखता है |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | प्रति-खाता सेटिंग्स (context, codecs, DTMF, आदि) |
| aor (address of record) | ps_aors | पंजीकरण सीमाएं और `qualify` सेटिंग्स |
| auth | ps_auths | `username` / `password` क्रेडेंशियल्स |
| contact | ps_contacts | गतिशील रूप से पंजीकृत स्थान |
| domain alias | ps_domain_aliases | एक endpoint के लिए वैकल्पिक SIP डोमेन |
| endpoint identifier by IP | ps_endpoint_id_ips | स्रोत IP द्वारा एक endpoint का मिलान |

PJSIP के लिए रीयल-टाइम दो स्थानों पर सक्षम है। सबसे पहले, Sorcery ऑब्जेक्ट प्रकारों को `extconfig.conf` में रीयल-टाइम से मैप करें:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

दूसरा, Sorcery को `sorcery.conf` में उन ऑब्जेक्ट प्रकारों के लिए `realtime` विज़ार्ड का उपयोग करने के लिए कहें। मैपिंग नाम (यहाँ `res_pjsip`) वह मॉड्यूल है जिसके ऑब्जेक्ट्स को आप स्थानांतरित कर रहे हैं, और दाईं ओर का मान उस परिवार की ओर इशारा करता है जिसे आपने `extconfig.conf` में परिभाषित किया है:

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

आप स्टेटिक और रीयल-टाइम ऑब्जेक्ट्स को मिला सकते हैं। यदि आप `sorcery.conf` से किसी प्रकार को छोड़ देते हैं, तो वह ऑब्जेक्ट प्रकार `pjsip.conf` से पढ़ना जारी रखता है। एक सामान्य पैटर्न स्टेटिक ट्रांसपोर्ट और वैश्विक सेटिंग्स को `pjsip.conf` में रखना है जबकि endpoints, aors, auths, और contacts को डेटाबेस में स्टोर करना है।

### Alembic के साथ PJSIP रीयल-टाइम स्कीमा बनाना

Asterisk अपने सभी रीयल-टाइम स्कीमा के लिए डेटाबेस माइग्रेशन `contrib/ast-db-manage` के तहत भेजता है। PJSIP तालिकाओं को बनाने (और संस्करण-अपग्रेड करने) का यह समर्थित तरीका है — आप अब `ps_*` तालिका परिभाषाओं को हाथ से नहीं लिखते हैं। `config` माइग्रेशन सेट में PJSIP/Sorcery तालिकाएं शामिल हैं।

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:supersecret@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

यह `ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`, और अन्य PJSIP तालिकाओं को चल रहे Asterisk संस्करण के लिए सही कॉलम के साथ बनाता है। (Alembic को Python के `alembic` पैकेज के साथ-साथ MySQL/MariaDB के लिए `pymysql` या PostgreSQL के लिए `psycopg2` जैसे SQLAlchemy ड्राइवर की आवश्यकता होती है।)

एक न्यूनतम रीयल-टाइम endpoint में तीन तालिकाओं में से प्रत्येक में एक पंक्ति होती है — उदाहरण के लिए endpoint `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

पंक्तियों को सम्मिलित करने के बाद रिलोड करने के लिए कुछ भी नहीं है — अगला REGISTER/INVITE डेटाबेस से ऑब्जेक्ट्स को खींचता है। आप पुष्टि कर सकते हैं कि रीयल-टाइम ने क्या लौटाया:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## डेटाबेस कॉन्फ़िगरेशन

अब जब हमने extconfig.conf फ़ाइल को कॉन्फ़िगर कर लिया है, तो आइए तालिकाएं बनाएं। सामान्य तौर पर, प्रत्येक डेटाबेस कॉलम संबंधित कॉन्फ़िगरेशन फ़ाइल से एक विकल्प नाम से मेल खाता है। PJSIP `ps_*` तालिकाएं इस नियम का पालन करती हैं: प्रत्येक `ps_endpoints` कॉलम का नाम एक `pjsip.conf` endpoint विकल्प के नाम पर रखा गया है, प्रत्येक `ps_auths` कॉलम का नाम एक auth विकल्प के बाद, और इसी तरह। उदाहरण के लिए, नीचे दिया गया `pjsip.conf` endpoint,

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

तीन तालिकाओं में एक पंक्ति के रूप में संग्रहीत है। `ps_endpoints` पंक्ति `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000` रखती है; `ps_auths` पंक्ति `id=4000, auth_type=userpass, username=4000, password=supersecret` रखती है; और `ps_aors` पंक्ति `id=4000, max_contacts=1` रखती है। आपको केवल उन कॉलम को पॉप्युलेट करने की आवश्यकता है जिनका आप वास्तव में उपयोग करते हैं — कोई भी कॉलम जिसे आप NULL छोड़ते हैं, वह विकल्प के डिफ़ॉल्ट पर वापस आ जाता है। यदि आप चाहते हैं, उदाहरण के लिए, एक endpoint पर `callerid` पैरामीटर, तो `ps_endpoints` के `callerid` कॉलम को भरें (कॉलम का नाम `pjsip.conf` विकल्प नाम के समान है)।

एक voicemail तालिका उसी विचार का पालन करती है। इसके कॉलम `voicemail.conf` फ़ील्ड्स के साथ मैप होते हैं:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

`uniqueid` प्रत्येक voicemail उपयोगकर्ता के लिए अद्वितीय होना चाहिए और यह ऑटोइंक्रीमेंट हो सकता है। इसका mailbox या context के साथ कोई संबंध होना आवश्यक नहीं है।

### Asterisk Real Time का उपयोग करके डायल प्लान बनाना

आप डायल प्लान बनाने के लिए रीयल-टाइम सिस्टम का भी उपयोग कर सकते हैं। ARA extensions.conf फ़ाइल में निहित सामान्य डायल प्लान में रीयल-टाइम एक्सटेंशन को शामिल करने के लिए `switch` स्टेटमेंट का उपयोग करता है। एक्सटेंशन तालिका नीचे दी गई तालिका जैसी दिखनी चाहिए:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

`extensions` रीयल-टाइम परिवार Asterisk 22 में अपरिवर्तित है; बस सुनिश्चित करें कि `appdata` कॉलम PJSIP चैनलों को डायल करता है, उदाहरण के लिए `PJSIP/4000`। डायल प्लान में, आपको रीयल-टाइम का उपयोग करने के लिए `switch` कमांड का उपयोग करना होगा।

![Asterisk Real Time के साथ डायल प्लान बनाना: extensions.conf एक डेटाबेस तालिका से एक्सटेंशन पंक्तियाँ (context, exten, priority, app, data) खींचने के लिए एक `switch => realtime` स्टेटमेंट का उपयोग करता है, न कि टेक्स्ट फ़ाइल से।](../images/18-realtime-fig02.png)

```
[local]
switch => realtime
```

या

```
[local]
switch => realtime/from-internal@extensions
```

## लैब: डेटाबेस तालिकाएं इंस्टॉल करना और बनाना

इस लैब में, हम Asterisk पैरामीटर्स प्राप्त करने के लिए डेटाबेस तैयार करेंगे। हम केवल REALTIME तालिकाएं तैयार करेंगे। स्टेटिक कॉन्फ़िगरेशन को कॉन्फ़िगरेशन टेक्स्ट फ़ाइलों पर छोड़ दिया जाएगा (कूल है, है ना?)। MySQL में तालिका निर्माण नीचे दिया गया है।

चरण 1: root के रूप में MySQL डेटाबेस में प्रवेश करें।

```
mysql –u root –p
```

चरण 2: CDR लैब में बनाए गए MySQL सर्वर में लॉग इन करें।

```
mysql –u astdb –p
```

जब पासवर्ड मांगा जाए, तो supersecret टाइप करें।

चरण 3: आवश्यक तालिकाएं बनाएं। लेगेसी स्टेटिक स्कीमा फ़ाइलें अभी भी `contrib/realtime/` के तहत भेजी जाती हैं (उदाहरण के लिए `/usr/src/asterisk-22.x/contrib/realtime/mysql`), लेकिन Asterisk 22 पर रीयल-टाइम तालिकाएं बनाने का अनुशंसित और संस्करण-सही तरीका — विशेष रूप से PJSIP `ps_*` तालिकाएं — `contrib/ast-db-manage` के तहत **Alembic** माइग्रेशन है (ऊपर "Alembic के साथ PJSIP रीयल-टाइम स्कीमा बनाना" सेक्शन देखें)।

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# set sqlalchemy.url for your astdb database, then:
alembic -c config.ini upgrade head
```

Alembic `config` माइग्रेशन सेट PJSIP `ps_*` तालिकाएं (`voicemail`, `extensions`, और अन्य रीयल-टाइम स्कीमा के साथ) उन कॉलम के साथ बनाता है जिनकी चल रहे Asterisk संस्करण को अपेक्षा होती है, इसलिए स्कीमा हमेशा बिल्ड से मेल खाता है।

पासवर्ड के रूप में supersecret का उपयोग करें।

चरण 4: तालिकाओं के निर्माण को सत्यापित करें।

```
mysql –u astdb –p astdb
mysql>use astdb;
mysql>show tables;
```

आपको PJSIP `ps_*` तालिकाएं (Alembic `config` माइग्रेशन द्वारा बनाई गई) देखनी चाहिए, साथ ही `voicemail`, `extensions`, और अन्य रीयल-टाइम तालिकाएं:

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

(Alembic इनसे अधिक तालिकाएं बनाता है — ऊपर दी गई सूची इस लैब के लिए प्रासंगिक तालिकाएं दिखाती है।)

चरण 5: डेटाबेस पहले से ही ODBC के लिए कॉन्फ़िगर है (CDR लैब से), इसलिए यहाँ किसी और ODBC सेटअप की आवश्यकता नहीं है।

चरण 6: डेटाबेस कार्यों को संभालने के लिए phpMyAdmin इंस्टॉल करें

```
apt-get install phpmyadmin
```

नीचे उपयोगिता की लॉग-इन स्क्रीन और तालिका स्क्रीन के दो स्क्रीनशॉट दिए गए हैं। नाम और पासवर्ड के रूप में astdb/supersecret का उपयोग करें।

> **[2nd-ed note]** इसे वर्तमान डेटाबेस-एडमिन स्क्रीनशॉट (phpMyAdmin/Adminer) से बदलें, या इन चरणों को सादे SQL (CREATE TABLE/INSERT) में बदलें।

## लैब: ARA को कॉन्फ़िगर और टेस्ट करना

इस लैब में हम अपने डेटाबेस कॉन्फ़िगरेशन और तालिकाओं को प्रतिबिंबित करने के लिए extconfig.conf कॉन्फ़िगरेशन को बदलेंगे।

चरण 1: extconfig.conf को कॉन्फ़िगर करें और Asterisk को रिलोड करें।

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

ऊपर `ps_endpoints`, `ps_aors`, `ps_auths`, और `ps_contacts` परिवारों पर ध्यान दें; मिलान `sorcery.conf` मैपिंग ( "PJSIP Realtime (Sorcery)" सेक्शन देखें) के साथ मिलकर वे PJSIP को डेटाबेस से अपने खाते पढ़ने के लिए मजबूर करते हैं। `voicemail` और `extensions` परिवार उदाहरण को पूरा करते हैं।

चरण 2: Real Time एक्सटेंशन टेस्ट। phpMyAdmin का उपयोग करके, `ps_auths`, `ps_aors`, और `ps_endpoints` में से प्रत्येक में एक पंक्ति सम्मिलित करके एक नया `6010` endpoint बनाएं, फिर इस endpoint को सॉफ्टफ़ोन के साथ पंजीकृत करने का प्रयास करें।

```
-- ps_auths
id=6010-auth, auth_type=userpass, username=6010, password=supersecret
-- ps_aors
id=6010, max_contacts=1
-- ps_endpoints
id=6010, transport=transport-udp, aors=6010, auth=6010-auth
```

> **[2nd-ed note]** इसे वर्तमान डेटाबेस-एडमिन स्क्रीनशॉट (phpMyAdmin/Adminer) से बदलें, या इन चरणों को सादे SQL (CREATE TABLE/INSERT) में बदलें।

शेष खाता सेटिंग्स PJSIP ऑब्जेक्ट्स में फैली हुई हैं। Context, codecs, DTMF मोड, और मीडिया हैंडलिंग endpoint पर रहते हैं; गतिशील पंजीकरण AOR पर रहता है:

```
-- ps_endpoints columns for 6010
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
-- ps_aors: dynamic registration is implicit; the AOR accepts
--          registrations and the contact is written to ps_contacts
```

PJSIP में RFC 2833 / RFC 4733 DTMF मोड को `rfc4733` (`dtmf_mode=rfc4733`, डिफ़ॉल्ट) कहा जाता है। पंजीकरण के लिए कोई अलग "गतिशील" ध्वज नहीं है: एक AOR गतिशील REGISTERs को तब तक स्वीकार करता है जब तक कि वह कम से कम एक संपर्क (`max_contacts` शून्य से अधिक) की अनुमति देता है, और प्रत्येक पंजीकृत स्थान को `ps_contacts` में लिखा जाता है।

चरण 3: उपयोगकर्ता नाम `6010` और पासवर्ड `supersecret` का उपयोग करके सॉफ्टफ़ोन के साथ नए फ़ोन को पंजीकृत करने का प्रयास करें। Asterisk CLI पर पंजीकरण की पुष्टि करें:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

चरण 4: डेटाबेस में एक्सटेंशन शामिल करें।

```
mysql -u astdb -p
```

पासवर्ड दर्ज करें:

पूछे जाने पर supersecret का उपयोग करें। डेटाबेस में एक्सटेंशन शामिल करने के लिए phpMyAdmin का उपयोग करें। यदि आप चाहें, तो इसके बजाय MySQL क्लाइंट इंटरफ़ेस में निम्नलिखित कमांड का उपयोग करें।

```
use astdb;
insert into extensions(id, context, exten, priority, app, appdata) VALUES
('1','test', '6007','1','Dial','PJSIP/bria');
```

चरण 5: डायल प्लान में Asterisk Real Time शामिल करें। Context `default` में:

```
switch => realtime/test@extensions
```

परिवर्तन को सक्रिय करने के लिए एक्सटेंशन को रिलोड करें।

```
asterisk-server*CLI>extensions reload
```

चरण 6: यदि आपने पहले से ऐसा नहीं किया है, तो फ़ोन में से एक को उपयोगकर्ता नाम `bria` पर पुनर्गठित करें।

चरण 7: मौजूदा फ़ोन से 6007 डायल करें; `bria` फ़ोन बजना चाहिए।

## सारांश

इस अध्याय में, आपने सीखा है कि Asterisk Real Time आपको अपने कॉन्फ़िगरेशन को डेटाबेस में रखने की अनुमति देता है। Asterisk ODBC (जो किसी भी UnixODBC-समर्थित डेटाबेस तक पहुँचता है, जिसमें MySQL/MariaDB और SQLite शामिल हैं), MySQL, और PostgreSQL के लिए नेटिव रीयल-टाइम ड्राइवर भेजता है, साथ ही डायरेक्टरी बैकएंड के लिए एक LDAP रीयल-टाइम ड्राइवर भी भेजता है। कॉन्फ़िगरेशन को स्टेटिक और रीयल-टाइम में विभाजित किया गया है। स्टेटिक कॉन्फ़िगरेशन कॉन्फ़िगरेशन फ़ाइलों को प्रतिस्थापित करता है, जबकि रीयल-टाइम कॉन्फ़िगरेशन गतिशील ऑब्जेक्ट्स बनाता है जो केवल तब लोड होते हैं जब कोई कॉल या अन्य संबंधित ईवेंट होता है। हमने ARA को इंस्टॉल और कॉन्फ़िगर करने के तरीके पर एक व्यावहारिक लैब के साथ निष्कर्ष निकाला।

## प्रश्नोत्तरी

1. Asterisk Realtime मानक Asterisk वितरण का हिस्सा है।
   - A. True
   - B. False
2. डेटाबेस सर्वर के कनेक्शन पैरामीटर्स किस फ़ाइल में कॉन्फ़िगर किए जाते हैं:
   - A. extensions.conf
   - B. pjsip.conf
   - C. res_odbc.conf
   - D. extconfig.conf
3. `extconfig.conf` फ़ाइल रीयल-टाइम द्वारा उपयोग की जाने वाली तालिकाओं को कॉन्फ़िगर करती है। इसमें दो अलग-अलग सेक्शन हैं (दो चुनें):
   - A. स्टेटिक कॉन्फ़िगरेशन
   - B. रीयल-टाइम कॉन्फ़िगरेशन
   - C. आउटबाउंड रूट
   - D. IP पते और डेटाबेस पोर्ट
4. स्टेटिक कॉन्फ़िगरेशन में, एक बार जब ऑब्जेक्ट्स डेटाबेस से लोड हो जाते हैं तो उन्हें Asterisk की मेमोरी में रखा जाता है और केवल स्टार्ट या रिलोड पर रिफ्रेश किया जाता है।
   - A. True
   - B. False
5. PJSIP रीयल-टाइम (Sorcery) रीयल-टाइम endpoints के लिए `qualify` और MWI का पूरी तरह से समर्थन करता है, क्योंकि Sorcery उन्हें प्रत्येक कॉल के बाद हटाने के बजाय सामान्य कॉन्फ़िगर किए गए PJSIP ऑब्जेक्ट्स के रूप में लोड करता है, जैसा कि पुराने SIP रीयल-टाइम पीयर्स करते थे।
   - A. True
   - B. False
6. PJSIP रीयल-टाइम में, कौन सी तालिकाएं endpoints और उनके पंजीकृत संपर्कों को रखती हैं?
   - A. `ps_endpoints` और `ps_contacts`
   - B. `ps_peers` और `ps_registry`
   - C. `ps_config` और `ps_data`
   - D. `extconfig` और `res_odbc`
7. ARA सक्षम करने के बाद भी आप टेक्स्ट कॉन्फ़िगरेशन फ़ाइलों का उपयोग कर सकते हैं।
   - A. True
   - B. False
8. जब आप Realtime का उपयोग करते हैं तो phpMyAdmin अनिवार्य है।
   - A. True
   - B. False
9. डेटाबेस को कॉन्फ़िगरेशन फ़ाइल में मौजूद प्रत्येक फ़ील्ड के साथ बनाया जाना चाहिए।
   - A. True
   - B. False
10. Asterisk 22 पर, PJSIP रीयल-टाइम तालिकाएं (`ps_endpoints`, `ps_aors`, `ps_auths`, `ps_contacts`) बनाने का अनुशंसित, संस्करण-सही तरीका क्या है?
    - A. प्रत्येक `ps_*` तालिका के लिए `CREATE TABLE` स्टेटमेंट हाथ से लिखें
    - B. `contrib/realtime/` से लेगेसी `mysql_config.sql` आयात करें
    - C. `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`) के तहत Alembic `config` माइग्रेशन चलाएं
    - D. पहली बार Asterisk शुरू होने पर तालिकाएं स्वचालित रूप से बन जाती हैं

**उत्तर:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
