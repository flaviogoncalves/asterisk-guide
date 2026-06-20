# Asterisk कॉल विवरण रिकॉर्ड

Asterisk, अन्य टेलीफ़ोनी प्लेटफ़ॉर्म की तरह, फोन कॉलों का बिलिंग करने की सुविधा देता है। बाजार में कई प्रोग्राम हैं जो PBX द्वारा उत्पन्न रिकॉर्ड को आयात कर सकते हैं। इन रिकॉर्डों का उपयोग बिल की सही राशि और आँकड़ों की पुष्टि करने आदि के लिए किया जाता है।

## उद्देश्य

- रिकॉर्ड कहाँ और किस फ़ॉर्मेट में उत्पन्न होते हैं, इसका वर्णन करें
- ODBC (Open Database Connectivity) का उपयोग करके रिकॉर्ड उत्पन्न करें
- बिलिंग के साथ एकीकृत प्रमाणीकरण योजना लागू करें

## Asterisk CDR Format

Asterisk प्रत्येक कॉल के लिए एक कॉल डिटेल रिकॉर्ड (CDR) उत्पन्न करता है। ये रिकॉर्ड डिफ़ॉल्ट रूप से /var/log/asterisk/cdr-csv में कॉमा सेपरेटेड वैल्यू (CSV) फ़ाइल में संग्रहीत होते हैं। फ़ाइल निम्नलिखित फ़ील्ड्स में व्यवस्थित है:

| Field | Description | Type |
|-------|-------------|------|
| Accountcode | उपयोग करने के लिए खाता संख्या | String |
| Src | कॉलर आईडी नंबर | String |
| Dst | गंतव्य एक्सटेंशन | String |
| Dcontext | गंतव्य कॉन्टेक्स्ट | String |
| Clid | टेक्स्ट के साथ कॉलर आईडी | String |
| Channel | उपयोग किया गया चैनल | String |
| Dstchannel | गंतव्य चैनल | String |
| Lastapp | अंतिम एप्लिकेशन | String |
| Lastdata | अंतिम एप्लिकेशन डेटा | String |
| Start | कॉल की शुरुआत | Date/Time |
| Answer | कॉल का उत्तर | Date/Time |
| End | कॉल का अंत | Date/Time |
| Duration | डायल से हैंग अप तक का समय | Integer (seconds) |
| Billsec | उत्तर से हैंग अप तक का समय | Integer (seconds) |
| Disposition | कॉल के साथ क्या हुआ (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | फ़्लैग्स (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | उपयोगकर्ता-परिभाषित फ़ील्ड | String |

CSV फ़ाइल का नमूना। प्रत्येक पंक्ति एक रिकॉर्ड है; फ़ील्ड्स उसी क्रम में दिखाई देते हैं जैसा ऊपर तालिका में है (`accountcode` पहले, `amaflags` आख़िर में):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## Account codes and automated message accounting

आप प्रत्येक चैनल पर अकाउंट कोड और ama फ्लैग निर्दिष्ट कर सकते हैं। आमतौर पर यह चैनल कॉन्फ़िगरेशन फ़ाइल (जैसे, chan_dahdi.conf, pjsip.conf) में किया जाता है। पैरामीटर amaflags यह निर्धारित करता है कि CDR रिकॉर्ड के साथ क्या किया जाए। संभावित amaflag मान हैं:

- Default
- Omit
- Billing
- Documentation

जिस प्रकार कोई रिकॉर्ड बिलिंग या डॉक्यूमेंटेशन के लिए फ़्लैग किया जा सकता है, उसी तरह प्रत्येक रिकॉर्ड पर एक अकाउंट कोड सेट किया जा सकता है। अकाउंट कोड एक फ्री‑फ़ॉर्म स्ट्रिंग है (`accountcode` endpoint विकल्प कोई भी String लेता है, और CDR रिकॉर्ड इसे 80‑character फ़ील्ड में संग्रहीत करता है) जो आमतौर पर रिकॉर्ड को किसी विभाग या बिज़नेस यूनिट को असाइन करने के लिए उपयोग किया जाता है। उदाहरण: pjsip.conf endpoint सेक्शन

```
[8576]
type=endpoint
accountcode=Support
```

AMA फ्लैग Asterisk 22 में एक `pjsip.conf` endpoint विकल्प नहीं है; इसे डायलप्लान से `CHANNEL` फ़ंक्शन के साथ (उदाहरण के लिए `Set(CHANNEL(amaflags)=billing)`) या `Set(CDR(amaflags)=billing)` के साथ प्रत्येक कॉल पर सेट करें।

## CSV और/या CDR फ़ॉर्मेट बदलना

आप cdr_custom.conf फ़ाइल को बदलकर CSV फ़ॉर्मेट बदल सकते हैं।

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

आप cdr_custom.conf फ़ाइल में CDR फ़ॉर्मेट बदल सकते हैं।

## CDR Storage

CDR संग्रह कई तरीकों से किया जा सकता है। सबसे महत्वपूर्ण तरीका CSV टेक्स्ट फ़ाइलें हैं जिन्हें आसानी से स्प्रेडशीट में इम्पोर्ट किया जा सकता है। छोटे व्यवसायों के लिए यह आमतौर पर ठीक रहता है। कुछ बिलिंग सॉफ़्टवेयर डिफ़ॉल्ट रूप से CSV फ़ाइलें स्वीकार करता है। हालांकि, CDR को डेटाबेस में संग्रहीत करना बहुत बेहतर और सुरक्षित है। Asterisk कई डेटाबेस फ़्लेवर का समर्थन करता है। बाजार में बिलिंग के लिए कुछ ग्राफ़िकल इंटरफ़ेस उपलब्ध हैं। इतने सारे ड्राइवरों में से कौन सा चुनें?

### Storage drivers available

- cdr_csv – कॉमा सेपरेटेड वैल्यू टेक्स्ट फ़ाइलें
- cdr_custom – कस्टमाइज़ेबल कॉमा-सेपरेटेड-वैल्यू टेक्स्ट फ़ाइलें
- cdr_adaptive_odbc – एडेप्टिव ODBC बैकएंड (डेटाबेस स्टोरेज के लिए पसंदीदा)
- cdr_odbc – unixODBC समर्थित डेटाबेस (लेगेसी; cdr_adaptive_odbc पसंदीदा)
- cdr_pgsql – Postgres डेटाबेस
- cdr_tds (cdr_freetds) – FreeTDS के माध्यम से Sybase और MSSQL डेटाबेस
- cdr_manager – CDR टू मैनेजर इंटरफ़ेस
- cdr_radius – CDR रेडियस इंटरफ़ेस
- cdr_sqlite3_custom – SQLite3 कस्टम CDR मॉड्यूल

पुराने गाइड्स में सुझाए गए `cdr_addon_mysql` (cdr_mysql) मॉड्यूल को Asterisk 19 में हटा दिया गया, इसलिए Asterisk 22 पर कोई नेटिव MySQL CDR ड्राइवर नहीं है। MySQL/MariaDB में CDR लिखने के लिए `cdr_adaptive_odbc` को MySQL ODBC ड्राइवर के साथ उपयोग करें — इस अध्याय में उपयोग किया गया तरीका।

CDR रिकॉर्डिंग सभी सक्रिय मॉड्यूल्स में /etc/asterisk/modules.conf फ़ाइल में लोड किए गए होते हैं। यदि पैरामीटर autoload=yes सेट है, तो सभी मॉड्यूल लोड हो जाते हैं। वर्तमान में सिस्टम में कौन से cdr_drivers लोड हैं, यह जांचने के लिए नीचे दिया गया कमांड उपयोग करें:

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

यदि आप ऊपर का स्क्रीनशॉट देखते हैं, तो कम से कम cdr_adaptive_odbc, cdr_csv, cdr_custom, cdr_manager, cdr_odbc और cdr_sqlite3_custom चल रहे हैं। पिछले कुछ वर्षों में कुछ astricons के बाद यह स्पष्ट हो गया कि Asterisk टीम ODBC को प्राथमिकता दे रही है। यह वह एकमात्र ड्राइवर है जो कनेक्शन पूलिंग का समर्थन करता है। कनेक्शन पूलिंग प्रदर्शन के लिहाज़ से बड़ा लाभ है क्योंकि आपको हर ऑपरेशन के लिए नई कनेक्शन खोलनी नहीं पड़ती। यह अध्याय पहले cdr_mysql का उपयोग करके लिखा गया था। मैंने इस संस्करण के लिए cdr_adaptive_odbc पर स्विच किया है, भले ही इसे सेटअप करना थोड़ा अधिक जटिल है। cdr_adaptive_odbc का चयन हमें CDR को कस्टमाइज़ करने की भी अनुमति देता है। आप डायलप्लान में एक नया CDR वेरिएबल सेट कर सकते हैं और डेटाबेस में मिलते‑जुलते कॉलम को जोड़ सकते हैं। उदाहरण के लिए, ऑडियो जिटर रिकॉर्ड करने के लिए:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### CSV Storage

जैसा कि हमने पहले कहा, डिफ़ॉल्ट रूप से Asterisk सभी CDR को cdr_csv.so मॉड्यूल का उपयोग करके CSV टेक्स्ट फ़ाइल में भेजता है। यदि आप /var/log/asterisk/cdr-csv में फ़ाइलें नहीं देख पा रहे हैं, तो CLI कमांड `module show` का उपयोग करके जांचें कि मॉड्यूल लोड हो रहा है या नहीं। यदि लोड नहीं है, तो modules.conf देखें। इस अध्याय में हम बैकअप के रूप में cdrs को cdr_csv पर भेजेंगे।

### Configuring the file modules.conf

केवल आवश्यक मॉड्यूल लोड करने के लिए, modules.conf फ़ाइल में नीचे दी गई लाइनों का उपयोग करें

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

अब हमारे पास केवल c

## Installing and configuring ODBC on Ubuntu 22.04

मैं हमेशा पुस्तक में विस्तृत निर्देश प्रकाशित करने पर पछताता हूँ। वे कभी‑कभी पुस्तक प्रकाशित होने से पहले ही बदल सकते हैं। संस्करण बदलते हैं, मॉड्यूल बदलते हैं, इसलिए यहाँ दिए गए कमांड को अपनी स्थिति के अनुसार अनुकूलित करने की कोशिश करें। अधिकांश समय छोटे‑छोटे बदलाव ही इंस्टॉलेशन को दोहराने के लिए पर्याप्त होते हैं। उन चरणों पर ध्यान दें जो अनुभवी Linux उपयोगकर्ताओं को भी ODBC ड्राइवर स्थापित करने में कठिन लग सकते हैं।

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

कई एप्लिकेशन बिलिंग से संबंधित हैं।

### CDR(accountcode)

दूसरे एप्लिकेशन `dial()` को कॉल करने से पहले एक अकाउंट कोड सेट करता है; उदाहरण के लिए: Format:

```
Set(CDR(accountcode)=account)
```

अकाउंट कोड को चैनल वेरिएबल `${CDR(accountcode)}` का उपयोग करके सत्यापित किया जा सकता है।

### CDR(amaflags)

बिलिंग उद्देश्यों के लिए एक फ़्लैग सेट करता है। विकल्प हैं `default`, `omit`, `documentation`, और `billing`।

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

वर्तमान चैनल के लिए CDR रिकॉर्डिंग को निष्क्रिय करता है, इसलिए कोई CDR फ़ाइल या डेटाबेस में नहीं लिखा जाता। इसे `0` पर सेट करने से रिकॉर्डिंग फिर से सक्षम हो जाती है।

```
Set(CDR_PROP(disable)=1)
```

पहले संस्करणों में उपयोग किया गया `NoCDR()` एप्लिकेशन Asterisk 21 में हटा दिया गया; Asterisk 22 में आप चैनल की CDR को `Set(CDR_PROP(disable)=1)` से निष्क्रिय करते हैं।

### ResetCDR()

Call Data Record को रीसेट करता है: `start` समय (और, यदि उत्तर दिया गया हो, तो `answer` समय) वर्तमान समय पर सेट हो जाता है और सभी CDR वेरिएबल्स मिटा दिए जाते हैं। यदि `v` विकल्प सेट है, तो रीसेट के दौरान CDR वेरिएबल्स संरक्षित रहते हैं।

### Set(CDR(userfield)=Value)

यह कमांड CDR में एक यूज़र फ़ील्ड सेट करता है। जब `cdr_adaptive_odbc` का उपयोग किया जाता है, तो यदि CDR टेबल में `userfield` कॉलम मौजूद है तो यूज़र फ़ील्ड स्वचालित रूप से संग्रहीत हो जाता है — कोई स्रोत पुनः संकलन आवश्यक नहीं। CSV टेक्स्ट फ़ाइलों के लिए, यदि आप यूज़र फ़ील्ड का उपयोग करना चाहते हैं तो आपको स्रोत कोड (`cdr_csv.c`) को संपादित करके Asterisk को पुनः संकलित करना होगा।

पहले संस्करणों में CDR को MySQL में `cdr_addon_mysql` मॉड्यूल (`cdr_mysql.conf`) के साथ संग्रहीत किया जाता था। वह मॉड्यूल Asterisk 19 में हटा दिया गया, इसलिए यह Asterisk 22 पर उपलब्ध नहीं है। अब समर्थित मार्ग `cdr_adaptive_odbc` है, जिसमें MySQL ODBC ड्राइवर के साथ यूज़र फ़ील्ड — और कोई भी अन्य कस्टम कॉलम — को उसके अनुकूल कॉलम मैपिंग के माध्यम से मूल रूप से संग्रहीत किया जाता है।

### Appending to the user field

पहले संस्करणों में डेटा को CDR यूज़र फ़ील्ड में जोड़ने के लिए `AppendCDRUserField()` एप्लिकेशन का उपयोग किया जाता था। वह एप्लिकेशन Asterisk से हटा दिया गया; Asterisk 22 में आप `CDR` फ़ंक्शन के साथ इसे पढ़कर और पुनः सेट करके यूज़र फ़ील्ड में जोड़ते हैं, उदाहरण के लिए

`Set(CDR(userfield)=${CDR(userfield)}extra)`।

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## उपयोगकर्ता प्रमाणीकरण

कुछ कंपनियां अपने कर्मचारियों को किए गए कॉलों का बिल बनाती हैं। Asterisk में आप एक प्रमाणीकरण योजना सेट कर सकते हैं जो आपको प्रमाणित उपयोगकर्ता को CDR पर बिल करने की अनुमति देती है। यह प्रमाणीकरण `Authenticate` एप्लिकेशन को पास किए गए पासवर्ड पैरामीटर—एक पासवर्ड फ़ाइल, पैरामीटर से पहले `/` (स्लैश) द्वारा संकेतित, या Asterisk डेटाबेस कुंजी (`d` विकल्प का उपयोग करके)—के माध्यम से किया जा सकता है। स्वरूप:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

विकल्प:

- a – दर्ज किए गए पासवर्ड को चैनल के अकाउंट कोड में सेट करता है।
- d – दिए गए पथ को एक लिटरल फ़ाइल के बजाय Asterisk DB कुंजी के रूप में व्याख्या करता है।
- m – पथ को `accountcode:passwordhash` पंक्तियों वाली फ़ाइल के रूप में व्याख्या करता है।
- r – सफल प्रमाणीकरण के बाद डेटाबेस कुंजी को हटा देता है (केवल `d` के साथ वैध)।

यदि कॉलर सभी तीन प्रयासों में विफल रहता है, तो चैनल को हंग अप कर दिया जाता है; डायलप्लान निष्पादन जारी नहीं रहता, इसलिए `Authenticate()` के बाद वाली पंक्ति पर विफलता पथ को संभालें। उदाहरण (अंतर्राष्ट्रीय कॉल):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

पुराना `j` विकल्प (विफलता पर प्राथमिकता n+101 पर कूदना) और `+101` प्राथमिकता सम्मेलन को Asterisk से बहुत समय पहले हटा दिया गया था; एक विफल `Authenticate()` केवल हंग अप करता है।

कंसोल से DB कुंजी में पासवर्ड डालने के लिए:

```
asterisk*CLI> database put senha 123456 1
```

## वॉइसमेल से पासवर्ड का उपयोग

यह एप्लिकेशन authenticate के समान कार्य करता है, लेकिन पासवर्ड के लिए वॉइसमेल कॉन्फ़िगरेशन फ़ाइल का उपयोग करता है।

```
VMAuthenticate([mailbox][@context][,options])
```

यदि कोई मेलबॉक्स निर्दिष्ट किया गया है, तो केवल उस मेलबॉक्स का पासवर्ड मान्य माना जाएगा। यदि मेलबॉक्स निर्दिष्ट नहीं किया गया है, तो चैनल वेरिएबल `${AUTH_MAILBOX}` को प्रमाणित मेलबॉक्स के साथ सेट किया जाएगा। यदि `s` विकल्प सेट किया गया है, तो प्रारंभिक प्रॉम्प्ट छोड़ दिए जाते हैं। उदाहरण (अंतर्राष्ट्रीय कॉल):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

CDR रिकॉर्ड प्रत्येक कॉल के लिए एक सारांश पंक्ति प्रदान करते हैं। अधिक विस्तृत इवेंट ट्रैकिंग के लिए — जैसे व्यक्तिगत चैनल स्थिति परिवर्तन, ब्रिज एंटर/लीव इवेंट, और अटेंडेड ट्रांसफ़र लेग्स — Asterisk 22 में **Channel Event Logging (CEL)** शामिल है, जिसे `/etc/asterisk/cel.conf` के माध्यम से कॉन्फ़िगर किया जाता है और `cel_odbc` या `cel_custom` जैसे बैकएंड्स के माध्यम से संग्रहीत किया जाता है।

CEL, CDR को प्रतिस्थापित करने के बजाय पूरक करता है: CDR बिलिंग सारांशों के लिए मानक बना रहता है, जबकि CEL धोखाधड़ी का पता लगाने, गुणवत्ता मॉनिटरिंग, और उन्नत रिपोर्टिंग के लिए उपयोगी सूक्ष्म-प्रति-इवेंट डेटा प्रदान करता है।

`cel.conf` कॉन्फ़िगरेशन पैटर्न `cdr.conf` को प्रतिबिंबित करता है: आप `[general]` सेक्शन में `cel.conf` के भीतर इच्छित इवेंट प्रकारों को सक्षम करते हैं, फिर प्रत्येक स्टोरेज बैक‑एंड को अपनी फ़ाइल में कॉन्फ़िगर करते हैं — CSV के लिए `cel_custom.conf`, ODBC डेटाबेस के लिए `cel_odbc.conf` (CDR के लिए उपयोग किए जाने वाले वही `res_odbc.conf` कनेक्शन)। आप CLI पर `cel show status` के साथ पुष्टि कर सकते हैं कि CEL सक्रिय है या नहीं।

## सारांश

इस अध्याय में हमने टेक्स्ट फ़ाइलों और MySQL डेटाबेस में CDR रिकॉर्डिंग को लागू करना सीखा। हमने amaflags और account codes सेट करना भी सीखा। अध्याय के अंत में, हमने CDR और बिलिंग के साथ एकीकृत प्रमाणीकरण योजना का उपयोग करना सीखा।

## Quiz

1. By default, Asterisk records the CDR in the /var/log/asterisk/cdr-csv directory.
   - A. False
   - B. True
2. Asterisk can write CDRs to (select all that apply):
   - A. MySQL
   - B. Native Oracle
   - C. Microsoft SQL Server
   - D. CSV text files
   - E. unixODBC-supported databases
3. Asterisk generates a CDR for only one kind of storage at a time.
   - A. False
   - B. True
4. Which Asterisk amaflags are available?
   - A. DEFAULT
   - B. OMIT
   - C. TAX
   - D. RATE
   - E. BILLING
   - F. DOCUMENTATION
5. To associate a department with a CDR you use the ___ command, and the account code can be read with the ___ channel variable.
6. The difference between `Set(CDR_PROP(disable)=1)` and `ResetCDR()` is that disabling the CDR prevents any record from being written, while `ResetCDR()` resets (zeroes) the current record. (The `NoCDR()` application that previously disabled CDRs was removed in Asterisk 21.)
   - A. False
   - B. True
7. To use a user-defined field with the `cdr_csv.so` module, you must edit the source code and recompile Asterisk.
   - A. False
   - B. True
8. The three authentication methods available to the Authenticate() application are:
   - A. Password
   - B. Password file
   - C. Asterisk DB (dbput and dbget)
   - D. Voicemail
9. Voicemail passwords are specified in a separate section of `voicemail.conf` and are not the same as the voicemail users.
   - A. False
   - B. True
10. Channel Event Logging (CEL) replaces CDR in Asterisk 22 — once CEL is enabled, CDR billing summaries are no longer produced.
    - A. False
    - B. True

**Answers:** 1 — B · 2 — A, B, C, D, E · 3 — A · 4 — A, B, E, F · 5 — `Set(CDR(accountcode)=...)`; `${CDR(accountcode)}` · 6 — B · 7 — A · 8 — A, B, C · 9 — B · 10 — A
