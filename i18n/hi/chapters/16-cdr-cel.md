# Asterisk Call Detail Records

Asterisk, अन्य टेलीफोनी प्लेटफॉर्म्स की तरह, फोन कॉल्स की बिलिंग की सुविधा देता है। बाजार में कई ऐसे प्रोग्राम उपलब्ध हैं जो PBXs द्वारा उत्पन्न रिकॉर्ड्स को इम्पोर्ट कर सकते हैं। इन रिकॉर्ड्स का उपयोग बिल की सही राशि और सांख्यिकी (statistics) को सत्यापित करने के लिए किया जाता है, अन्य चीजों के अलावा।

## उद्देश्य

इस अध्याय के अंत तक, पाठक निम्नलिखित में सक्षम होना चाहिए:

- यह वर्णन करना कि रिकॉर्ड्स कहाँ और किस प्रारूप में उत्पन्न होते हैं
- ODBC (Open Database Connectivity) का उपयोग करके रिकॉर्ड्स उत्पन्न करना
- बिलिंग के साथ एकीकृत एक प्रमाणीकरण (authentication) योजना को लागू करना

## Asterisk CDR प्रारूप

Asterisk प्रत्येक कॉल के लिए एक कॉल डिटेल रिकॉर्ड (CDR) उत्पन्न करता है। ये रिकॉर्ड्स डिफ़ॉल्ट रूप से, एक टेक्स्ट फ़ाइल में कॉमा सेपरेटेड वैल्यू (CSV) प्रारूप में /var/log/asterisk/cdr-csv में संग्रहीत होते हैं। फ़ाइल को निम्नलिखित फ़ील्ड्स में व्यवस्थित किया गया है: CDR Description Type Size Accountcode Account Number to use String Src Caller ID Number String Dst Destination Extension String Dcontext Destination Context String Caller ID with Text String Channel Channel Used String Dstchannel Destination channel String Lastapp Last application String Lastdata Last application data String Start Start of call Date/Time Answer Answer of call Date/Time End End of Call Date/Time Duration Time, from dial to hang up Integer (seconds) Billsec Time, from answer to hang up Integer (seconds) Disposition What Happened to the call String (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) Amaflags Flags (DEFAULT, OMIT, BILLING, DOCUMENTATION) String User field User defined field String Sample of csv file imported into a table. AccountCode CallerID No. Extension Context CallerID text Src Dst 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-5f30 PJSIP/8584-9153 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-96f5 PJSIP/8584-3312 1234 4830258576 *72*1234*8584 admin "Joana D’Arc" <4830258576> PJSIP/8576-74ac PJSIP/8584-297b 1234 4830258576 2012348584 admin "Joana D’Arc" <4830258576> PJSIP/8576-2c5d PJSIP/8584-9870 1234 4830258584 2012348576 default "Luis Sample" <4830258584> PJSIP/8584-03fd PJSIP/8576-645c Application Appdata Start Answer End Dur Bil Disposition Amaflags Dial PJSIP/8584,30,tT 27/3/2006 16:05 27/3/2006 16:05 27/3/2006 16:05 ANSWERED DOCUMENTATION Dial PJSIP/8584,30,tT 27/3/2006 16:16 27/3/2006 16:16 27/3/2006 16:16 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:22 27/3/2006 16:22 27/3/2006 16:22 ANSWERED BILLING Dial PJSIP/8584,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING Dial PJSIP/8576,30,tT 27/3/2006 16:37 27/3/2006 16:37 27/3/2006 16:37 ANSWERED BILLING

## अकाउंट कोड और स्वचालित संदेश लेखांकन (Automated Message Accounting)

आप प्रत्येक चैनल पर अकाउंट कोड और ama flags निर्दिष्ट कर सकते हैं। आमतौर पर यह चैनल कॉन्फ़िगरेशन फ़ाइल (जैसे, chan_dahdi.conf, pjsip.conf) में किया जाता है। पैरामीटर amaflags यह परिभाषित करता है कि CDR रिकॉर्ड के साथ क्या करना है। संभावित amaflag मान हैं:

- Default
- Omit
- Billing
- Documentation

जिस तरह से किसी रिकॉर्ड को बिलिंग या डॉक्यूमेंटेशन के लिए फ्लैग किया जा सकता है, उसी तरह प्रत्येक रिकॉर्ड पर एक अकाउंट कोड सेट किया जा सकता है। अकाउंट कोड एक फ्री-फॉर्म स्ट्रिंग है (`accountcode` endpoint विकल्प कोई भी String लेता है, और CDR रिकॉर्ड इसे 80-कैरेक्टर के फ़ील्ड में संग्रहीत करता है) जिसका उपयोग आमतौर पर किसी रिकॉर्ड को किसी विभाग या व्यावसायिक इकाई को असाइन करने के लिए किया जाता है। उदाहरण: pjsip.conf endpoint सेक्शन

```
[8576]
type=endpoint
accountcode=Support
```

AMA फ्लैग Asterisk 22 में एक `pjsip.conf` endpoint विकल्प नहीं है; इसे dialplan से `CHANNEL` फ़ंक्शन (उदाहरण के लिए `Set(CHANNEL(amaflags)=billing)`) के साथ, या `Set(CDR(amaflags)=billing)` के साथ प्रति कॉल सेट करें।

## CSV और/या CDR प्रारूप बदलना

आप cdr_custom.conf फ़ाइल को बदलकर CSV प्रारूप बदल सकते हैं।

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

आप cdr_custom.conf फ़ाइल में CDR प्रारूप बदल सकते हैं।

## CDR स्टोरेज

CDR स्टोरेज कई तरीकों से प्राप्त किया जा सकता है। सबसे महत्वपूर्ण तरीका CSV टेक्स्ट फ़ाइलें हैं जिन्हें आसानी से स्प्रेडशीट में इम्पोर्ट किया जा सकता है। छोटे व्यवसायों के लिए, यह आमतौर पर ठीक है। कुछ बिलिंग सॉफ़्टवेयर डिफ़ॉल्ट रूप से CSV फ़ाइलों को स्वीकार करते हैं। हालाँकि, CDRs को डेटाबेस में संग्रहीत करना बहुत बेहतर और सुरक्षित है। Asterisk कई डेटाबेस फ्लेवर का समर्थन करता है। बाजार में बिलिंग के लिए कुछ ग्राफिकल इंटरफेस उपलब्ध हैं। इतने सारे ड्राइवर्स के साथ, किसे चुनें?

### उपलब्ध स्टोरेज ड्राइवर्स

- cdr_csv – Comma Separated Value टेक्स्ट फ़ाइलें
- cdr_adaptive_odbc – Adaptive ODBC बैकएंड (डेटाबेस स्टोरेज के लिए पसंदीदा)
- cdr_odbc – unixODBC समर्थित डेटाबेस (लेगेसी; cdr_adaptive_odbc पसंदीदा)
- cdr_pgsql – Postgres डेटाबेस
- cdr_mysql – MySQL डेटाबेस (**deprecated**; इसके बजाय cdr_adaptive_odbc + MySQL ODBC ड्राइवर का उपयोग करें)
- cdr_freetds – Sybase और MSSQL डेटाबेस
- cdr_manager – CDR to Manager Interface
- cdr_radius – CDR radius इंटरफेस
- cdr_sqlite3_custom – SQLite3 कस्टम CDR मॉड्यूल

CDR रिकॉर्डिंग /etc/asterisk/modules.conf फ़ाइल में लोड किए गए सभी सक्रिय मॉड्यूल के लिए की जाती है। यदि पैरामीटर autoload=yes सेट है, तो सभी मॉड्यूल लोड हो जाते हैं। यह जांचने के लिए कि सिस्टम में वर्तमान में कौन से cdr_drivers लोड हैं, नीचे दिए गए कमांड का उपयोग करें:

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

यदि आप ऊपर दिया गया स्क्रीनशॉट देखते हैं, तो कम से कम cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc और cdr_sqlite3_custom चल रहे हैं। कुछ astricons के बाद के वर्षों में मेरे लिए यह स्पष्ट हो गया कि Asterisk टीम ODBC का पक्ष ले रही थी। यह कनेक्शन पूलिंग का समर्थन करने वाला एकमात्र ड्राइवर है। प्रदर्शन के मामले में कनेक्शन पूलिंग एक बड़ा लाभ है क्योंकि आपको प्रत्येक ऑपरेशन के लिए एक नया कनेक्शन खोलने की आवश्यकता नहीं होती है। यह अध्याय पहले cdr_mysql का उपयोग करके लिखा गया था। मैंने इस संस्करण के लिए cdr_adaptive_odbc पर स्विच किया है, यह जानते हुए भी कि इसे सेटअप करना थोड़ा अधिक जटिल है। cdr_adaptive_odbc का विकल्प हमें CDR को कस्टमाइज़ करने की भी अनुमति देता है। आप बस dialplan में एक नया CDR वेरिएबल सेट कर सकते हैं और डेटाबेस में कॉलम जोड़ सकते हैं। Set(CDR(jitter)=

```
${RTPAUDIOQOSJITTER}).
```

### CSV स्टोरेज

जैसा कि हमने पहले कहा, डिफ़ॉल्ट रूप से, Asterisk cdr_csv.so मॉड्यूल का उपयोग करके सभी CDR को एक CSV टेक्स्ट फ़ाइल में भेजता है। यदि आप /var/log/asterisk/cdr-csv में फ़ाइलें नहीं देख पा रहे हैं, तो CLI कमांड module show का उपयोग करके जांचें कि क्या मॉड्यूल लोड हो रहा है। यदि यह लोड नहीं है, तो modules.conf की जांच करें। इस अध्याय में हम बैकअप के रूप में cdrs को cdr_csv में भेजेंगे।

### modules.conf फ़ाइल को कॉन्फ़िगर करना

केवल उपयुक्त मॉड्यूल लोड करने के लिए, modules.conf फ़ाइल में नीचे दी गई लाइनों का उपयोग करें

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

अब हमारे पास केवल cdr_csv और cdr_adaptive_odbc लोड हैं।

## Ubuntu 22.04 पर ODBC इंस्टॉल और कॉन्फ़िगर करना

> **[2nd-ed note]** मूल चरण Ubuntu 18.04 और MySQL Connector/ODBC 8.0.14 को लक्षित थे। नीचे दिए गए चरण Ubuntu 22.04 LTS के लिए अपडेट किए गए हैं; dev.mysql.com से वर्तमान MySQL Connector/ODBC रिलीज़ से मेल खाने के लिए पैकेज संस्करणों और डाउनलोड URLs को समायोजित करें।

मुझे किताब में विस्तृत निर्देश प्रकाशित करने पर हमेशा पछतावा होता है। वे कभी-कभी किताब प्रकाशित होने से पहले ही बदल जाते हैं। संस्करण बदलते हैं, मॉड्यूल बदलते हैं, इसलिए यहाँ दिए गए कमांड को अपनी स्थिति के अनुसार अनुकूलित करने का प्रयास करें। अधिकांश समय इंस्टॉलेशन को दोहराने के लिए छोटे बदलाव ही पर्याप्त होते हैं। उन चरणों पर ध्यान दें जिन्हें अनुभवी Linux उपयोगकर्ता भी ODBC ड्राइवर्स को इंस्टॉल करने के लिए कठिन पाएंगे।

चरण 1 - आवश्यक पैकेज इंस्टॉल करें:

```
apt-get install mysql-server unixodbc unixodbc-dev libltdl-dev libtool
```

चरण 2 - एक डेटाबेस और एक उपयोगकर्ता बनाएं:

```
mysql -u root -p
```

(mysql सर्वर बनाते समय परिभाषित पासवर्ड का उपयोग करें) mysql कमांड लाइन में ये कमांड टाइप करें

```
CREATE USER 'astdb'@'%' IDENTIFIED BY 'supersecret';
CREATE DATABASE cdr;
GRANT ALL PRIVILEGES ON cdr.* TO 'astdb'@'%';
FLUSH PRIVILEGES;
EXIT
```

चरण 3 - डेटाबेस बनाएं

```
cd /usr/src/asterisk-22.*/contrib/scripts/realtime/mysql
mysql -u root -p astdb <mysql_cdr.sql
```

चरण 4: Oracle से MySQL ODBC कनेक्टर डाउनलोड करें। अपने ऑपरेटिंग सिस्टम की जांच करें: `lsb_release -a` का उपयोग करके। Ubuntu 22.04 (x86_64) के लिए, https://dev.mysql.com/downloads/connector/odbc/ पर जाएं और Ubuntu 22.04 के लिए वर्तमान 8.x या 9.x रिलीज़ चुनें।

> **[2nd-ed note]** dev.mysql.com पर सटीक डाउनलोड URL और फ़ाइल नाम सत्यापित करें; संस्करण संख्या और Ubuntu प्रत्यय पहले संस्करण से भिन्न होंगे। नीचे दिया गया उदाहरण एक प्लेसहोल्डर संस्करण का उपयोग करता है।

```
cd /usr/src
# Pick the current Linux (glibc) build for your platform from
# https://dev.mysql.com/downloads/connector/odbc/ and set VER to its name:
VER=mysql-connector-odbc-9.0.0-linux-glibc2.28-x86-64bit
wget https://dev.mysql.com/get/Downloads/Connector-ODBC/9.0/$VER.tar.gz
tar -xzvf $VER.tar.gz
```

चरण 5: ODBC ड्राइवर इंस्टॉल करें

```
cd /usr/src/$VER
cp bin/* /usr/local/bin
cp lib/* /usr/local/lib
myodbc-installer -a -d -n "MySQL" -t "Driver=/usr/local/lib/libmyodbc9w.so"
```

चरण 6 - ODBC कनेक्टर को कॉन्फ़िगर करें, DSN (Data Source Name) बनाने के लिए /etc/odbc.ini फ़ाइल को संपादित करें

```
[astconn]
Description = MySQL connector for astdb database
Driver = /usr/local/lib/libmyodbc9w.so
Database = astdb
Server = localhost
Port = 3306
```

चरण 7: iSQL का उपयोग करके ड्राइवर एक्सेस का परीक्षण करें। iSQL, unixodbc पर डेटाबेस से कनेक्ट करने के लिए एक कमांड लाइन उपयोगिता है।

```
isql -v astconn astdb supersecret
>show tables
```

कृपया, यदि आप isql कमांड का परिणाम नहीं देख पा रहे हैं तो Asterisk कॉन्फ़िगरेशन के साथ आगे न बढ़ें।

### Asterisk में ODBC को कॉन्फ़िगर करना

cdr_adaptive_odbc को कॉन्फ़िगर करने से पहले, आपको पहले ODBC रिसोर्स फ़ाइल को कॉन्फ़िगर करना चाहिए।

चरण 1 - Asterisk को ODBC से कनेक्ट करें। res_odbc.conf फ़ाइल को संपादित करें:

```
[cdr]
enabled => yes
dsn => astconn
username => astdb
password => supersecret
pre-connect => yes
```

चरण 2 – Asterisk को पुनरारंभ करें और परीक्षण करें

```
CLI>odbc show
```

आउटपुट नीचे दिखाया गया है।

```
asterisk*CLI> odbc show
ODBC DSN Settings
-----------------
Name:   cdr
DSN:    astconn
  Number of active connections: 1 (out of 20)
```

चरण 3 – /etc/asterisk/cdr_adaptive_odbc.conf में एडेप्टिव ODBC ड्राइवर को कॉन्फ़िगर करें

```
[cdr]
connection=cdr
table=cdr
```

यहाँ `connection` उस `[cdr]` कनेक्शन सेक्शन की ओर इशारा करता है जो `res_odbc.conf` में परिभाषित है, और `table` वह डेटाबेस टेबल है जहाँ CDRs लिखे जाते हैं।

चरण 4 – मॉड्यूल cdr_adaptive_odbc.so को पुनः लोड करें:

```
asterisk*CLI>reload cdr_adaptive_odbc
```

चरण 5 – कुछ कॉल्स करें और नए रिकॉर्ड्स के लिए डेटाबेस की जांच करें। डेटाबेस की जांच करने के लिए:

```
mysql –u root –p
>use astdb
>select * from cdr
```

## एप्लिकेशन और फ़ंक्शन

कई एप्लिकेशन बिलिंग से संबंधित हैं।

### CDR(accountcode)

किसी अन्य एप्लिकेशन dial() को कॉल करने से पहले एक अकाउंट कोड सेट करता है; उदाहरण के लिए: प्रारूप:

```
Set(CDR(accountcode)=account)
```

अकाउंट कोड को चैनल वेरिएबल ${CDR(accountcode)} का उपयोग करके सत्यापित किया जा सकता है

### CDR(amaflags)

बिलिंग उद्देश्यों के लिए एक फ्लैग सेट करें। विकल्प default, omit, documentation, और billing हैं।

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

वर्तमान चैनल के लिए CDR रिकॉर्डिंग को अक्षम करता है, ताकि कोई CDR फ़ाइल या डेटाबेस में न लिखा जाए। इसे वापस `0` पर सेट करने से रिकॉर्डिंग फिर से सक्षम हो जाती है।

```
Set(CDR_PROP(disable)=1)
```

> **[2nd-ed note]** मूल टेक्स्ट ने `NoCDR()` एप्लिकेशन का उपयोग किया था। `NoCDR` को Asterisk 21 में deprecated कर दिया गया था और फिर हटा दिया गया था; इसके बजाय `Set(CDR_PROP(disable)=1)` का उपयोग करें।

### ResetCDR()

कॉल डेटा रिकॉर्ड को रीसेट करता है: `start` समय (और, यदि उत्तर दिया गया है, तो `answer` समय) वर्तमान समय पर सेट हो जाता है और सभी CDR वेरिएबल मिटा दिए जाते हैं। यदि `v` विकल्प सेट है, तो रीसेट के दौरान CDR वेरिएबल सुरक्षित रहते हैं।

### Set(CDR(userfield)=Value)

यह कमांड CDR में एक यूजर फ़ील्ड सेट करती है। `cdr_adaptive_odbc` का उपयोग करते समय, यदि CDR टेबल में एक `userfield` कॉलम मौजूद है तो यूजर फ़ील्ड स्वचालित रूप से संग्रहीत हो जाता है — किसी सोर्स पुनर्संकलन (recompilation) की आवश्यकता नहीं है। CSV टेक्स्ट फ़ाइलों के लिए, यदि आप यूजर फ़ील्ड का उपयोग करना चाहते हैं तो आपको सोर्स कोड (cdr_csv.c) को संपादित करना होगा और Asterisk को पुनर्संकलित करना होगा।

> **[2nd-ed note]** मूल टेक्स्ट ने `cdr_addon_mysql` और `cdr_mysql.conf` को संदर्भित किया था। `cdr_mysql` मॉड्यूल Asterisk 22 में deprecated है; अनुशंसित मार्ग MySQL ODBC ड्राइवर के साथ `cdr_adaptive_odbc` है, जो एडेप्टिव कॉलम मैपिंग के माध्यम से मूल रूप से यूजर फ़ील्ड का समर्थन करता है।

### AppendCDRUserField(Value)

CDR पर यूजर फ़ील्ड में डेटा जोड़ें।

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## उपयोगकर्ता प्रमाणीकरण

कुछ कंपनियां अपने कर्मचारियों से कॉल्स का बिल लेती हैं। Asterisk में आप एक प्रमाणीकरण योजना सेट कर सकते हैं जो आपको CDR पर प्रमाणित उपयोगकर्ता को बिल करने में सक्षम बनाती है। यह प्रमाणीकरण Authenticate एप्लिकेशन को पैरामीटर के रूप में पास किए गए पासवर्ड का उपयोग करके किया जा सकता है — एक पासवर्ड फ़ाइल, जिसे पैरामीटर से पहले / (स्लैश) द्वारा इंगित किया जाता है, या एक Asterisk डेटाबेस (dbput/dbget)। प्रारूप:

```
Authenticate(password[|options])
Authenticate(/passwdfile|[|options])
Authenticate(</db-keyfamily|d>options)
```

विकल्प:

- a – अकाउंट कोड को पासवर्ड के रूप में सेट करता है।
- d – पैरामीटर को Asterisk DB की के रूप में व्याख्या करता है
- r – सफल प्रमाणीकरण के बाद की को हटा देता है (केवल ´d´ विकल्प के साथ)
- j – अमान्य प्रमाणीकरण के लिए प्रायोरिटी n+101 पर जंप करता है

उदाहरण: (अंतर्राष्ट्रीय कॉल्स)

```
exten=_9011.,1,Authenticate(/password|daj)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

कंसोल से DB की में पासवर्ड डालने के लिए:

```
CLI> database put senha 123456 1
```

## Voicemail से पासवर्ड का उपयोग करना

यह एप्लिकेशन authenticate के समान ही काम करता है, लेकिन पासवर्ड के लिए Voicemail कॉन्फ़िगरेशन फ़ाइल का उपयोग करता है।

```
VMAuthenticate([mailbox][@context][|options])
```

यदि कोई मेलबॉक्स निर्दिष्ट है, तो केवल मेलबॉक्स पासवर्ड को ही मान्य माना जाएगा। यदि मेलबॉक्स निर्दिष्ट नहीं है, तो एक चैनल वेरिएबल AUTH_MAILBOX प्रमाणित मेलबॉक्स के साथ सेट किया जाएगा। यदि विकल्प ´s´ (silent) सेट है, तो कोई प्रॉम्प्ट निष्पादित नहीं किया जाएगा। उदाहरण: (अंतर्राष्ट्रीय कॉल्स)

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local|ajs)
exten=_9011.,2,Dial(DAHDI/g1/${EXTEN:1},20,tT)
exten=_9011.,3,Hangup()
exten=_9011.,102,Playback(unauthorized)
exten=_9011.,103,Hangup()
```

## Channel Event Logging (CEL)

CDR रिकॉर्ड्स प्रति कॉल एक सारांश पंक्ति प्रदान करते हैं। अधिक विस्तृत इवेंट ट्रैकिंग के लिए — जैसे व्यक्तिगत चैनल स्टेट ट्रांज़िशन, ब्रिज एंटर/लीव इवेंट्स, और अटेंडेड ट्रांसफर लेग्स — Asterisk 22 में **Channel Event Logging (CEL)** शामिल है, जिसे `/etc/asterisk/cel.conf` के माध्यम से कॉन्फ़िगर किया जाता है और `cel_odbc` या `cel_custom` जैसे बैकएंड के माध्यम से संग्रहीत किया जाता है।

CEL CDR को बदलने के बजाय उसका पूरक है: CDR बिलिंग सारांश के लिए मानक बना हुआ है, जबकि CEL धोखाधड़ी का पता लगाने, गुणवत्ता निगरानी और उन्नत रिपोर्टिंग के लिए उपयोगी दानेदार प्रति-इवेंट डेटा देता है।

> **[2nd-ed note]** यदि पाठ्यक्रम में शामिल है तो एक संक्षिप्त CEL उपखंड या उन्नत बिलिंग अध्याय के लिए एक फॉरवर्ड संदर्भ जोड़ने पर विचार करें। `cel.conf` कॉन्फ़िगरेशन पैटर्न `cdr.conf` को दर्शाता है।

## सारांश

इस अध्याय में हमने सीखा है कि टेक्स्ट फ़ाइलों और MySQL डेटाबेस में CDR रिकॉर्डिंग को कैसे लागू किया जाए। हमने यह भी सीखा है कि amaflags और अकाउंट कोड कैसे सेट करें। अध्याय के अंत में, हमने सीखा कि CDR और बिलिंग के साथ एकीकृत प्रमाणीकरण योजना का उपयोग कैसे करें।

## प्रश्नोत्तरी

1. डिफ़ॉल्ट रूप से, Asterisk CDR को /var/log/asterisk/cdr-csv डायरेक्टरी में रिकॉर्ड करता है।
   - A. गलत
   - B. सही
2. Asterisk CDRs को कहाँ लिख सकता है (सभी लागू विकल्प चुनें):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV टेक्स्ट फ़ाइलें
   - E. unixODBC-समर्थित डेटाबेस
3. Asterisk एक समय में केवल एक प्रकार के स्टोरेज के लिए CDR उत्पन्न करता है।
   - A. गलत
   - B. सही
4. कौन से Asterisk amaflags उपलब्ध हैं?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. किसी विभाग को CDR के साथ जोड़ने के लिए आप ___ कमांड का उपयोग करते हैं, और अकाउंट कोड को ___ चैनल वेरिएबल के साथ पढ़ा जा सकता है।
6. `Set(CDR_PROP(disable)=1)` और `ResetCDR()` के बीच का अंतर यह है कि CDR को अक्षम करने से कोई भी रिकॉर्ड नहीं लिखा जाता है, जबकि `ResetCDR()` वर्तमान रिकॉर्ड को रीसेट (शून्य) कर देता है। (`NoCDR()` एप्लिकेशन जिसने पहले CDRs को अक्षम किया था, उसे Asterisk 21 में हटा दिया गया था।)
   - A. गलत
   - B. सही
7. `cdr_csv.so` मॉड्यूल के साथ यूजर-डिफ़ाइंड फ़ील्ड का उपयोग करने के लिए, आपको सोर्स कोड को संपादित करना होगा और Asterisk को पुनर्संकलित करना होगा।
   - A. गलत
   - B. सही
8. Authenticate() एप्लिकेशन के लिए उपलब्ध तीन प्रमाणीकरण विधियाँ हैं:
   - A. पासवर्ड
   - B. पासवर्ड फ़ाइल
   - C. Asterisk DB (dbput और dbget)
   - D. Voicemail
9. Voicemail पासवर्ड `voicemail.conf` के एक अलग सेक्शन में निर्दिष्ट होते हैं और Voicemail उपयोगकर्ताओं के समान नहीं होते हैं।
   - A. गलत
   - B. सही
10. Channel Event Logging (CEL) Asterisk 22 में CDR की जगह लेता है — एक बार CEL सक्षम हो जाने पर, CDR बिलिंग सारांश अब उत्पन्न नहीं होते हैं।
    - A. गलत
    - B. सही

**उत्तर:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
