# Asterisk سجلات تفاصيل المكالمات

Asterisk، مثل باقي منصات الاتصالات، يتيح فوترة المكالمات الهاتفية. يمكن لعدة برامج في السوق استيراد السجلات التي تولدها أنظمة PBXs. تُستخدم تلك السجلات للتحقق من صحة مبلغ الفاتورة والإحصاءات، من بين أمور أخرى.

## الأهداف

بحلول نهاية هذا الفصل، يجب أن يكون القارئ قادرًا على:

- وصف مكان وتنسيق السجلات التي يتم إنشاؤها
- إنشاء السجلات باستخدام ODBC (Open Database Connectivity)
- تنفيذ مخطط مصادقة مدمج مع الفوترة

## تنسيق CDR في Asterisk

Asterisk يولد سجل تفاصيل المكالمة (CDR) لكل مكالمة. تُحفظ هذه السجلات، بشكل افتراضي، في ملف نصي بصيغة قيم مفصولة بفواصل (CSV) في ‎/var/log/asterisk/cdr-csv. يُنظم الملف بالحقول التالية:

| الحقل | الوصف | النوع |
|-------|-------|-------|
| Accountcode | رقم الحساب المستخدم | String |
| Src | رقم هوية المتصل | String |
| Dst | امتداد الوجهة | String |
| Dcontext | سياق الوجهة | String |
| Clid | هوية المتصل مع النص | String |
| Channel | القناة المستخدمة | String |
| Dstchannel | قناة الوجهة | String |
| Lastapp | آخر تطبيق | String |
| Lastdata | بيانات آخر تطبيق | String |
| Start | بدء المكالمة | Date/Time |
| Answer | إجابة المكالمة | Date/Time |
| End | انتهاء المكالمة | Date/Time |
| Duration | الوقت من بدء الطلب حتى الإغلاق | Integer (seconds) |
| Billsec | الوقت من الإجابة حتى الإغلاق | Integer (seconds) |
| Disposition | ما حدث للمكالمة (ANSWERED, NO ANSWER, BUSY, FAILED, CONGESTION) | String |
| Amaflags | العلامات (DEFAULT, OMIT, BILLING, DOCUMENTATION) | String |
| Userfield | حقل معرف من قبل المستخدم | String |

عينة من ملف CSV. كل سطر يمثل سجلاً واحدًا؛ تظهر الحقول بالترتيب نفسه كما في الجدول أعلاه (`accountcode` أولاً، `amaflags` أخيرًا):

```text
# accountcode,src,dst,dcontext,clid,channel,dstchannel,lastapp,lastdata,
#   start,answer,end,duration,billsec,disposition,amaflags
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-5f30","PJSIP/8584-9153","Dial","PJSIP/8584,30,tT","2006-03-27 16:05:00","2006-03-27 16:05:00","2006-03-27 16:05:00","0","0","ANSWERED","DOCUMENTATION"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-96f5","PJSIP/8584-3312","Dial","PJSIP/8584,30,tT","2006-03-27 16:16:00","2006-03-27 16:16:00","2006-03-27 16:16:00","0","0","ANSWERED","BILLING"
"1234","4830258576","*72*1234*8584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-74ac","PJSIP/8584-297b","Dial","PJSIP/8584,30,tT","2006-03-27 16:22:00","2006-03-27 16:22:00","2006-03-27 16:22:00","0","0","ANSWERED","BILLING"
"1234","4830258576","2012348584","admin","""Joana D'Arc"" <4830258576>","PJSIP/8576-2c5d","PJSIP/8584-9870","Dial","PJSIP/8584,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
"1234","4830258584","2012348576","default","""Luis Sample"" <4830258584>","PJSIP/8584-03fd","PJSIP/8576-645c","Dial","PJSIP/8576,30,tT","2006-03-27 16:37:00","2006-03-27 16:37:00","2006-03-27 16:37:00","0","0","ANSWERED","BILLING"
```

## رموز الحساب والمحاسبة الآلية للرسائل

يمكنك تحديد رموز الحساب وعلامات ama على كل قناة. عادةً ما يتم ذلك في ملف تكوين القناة (مثل chan_dahdi.conf، pjsip.conf). المعامل amaflags يحدد ما يجب فعله بسجل CDR. القيم الممكنة لـ amaflag هي:

- Default
- Omit
- Billing
- Documentation

مشابه للطريقة التي يمكن فيها وضع علامة على سجل للفوترة أو التوثيق، يمكن تعيين رمز حساب على كل سجل. رمز الحساب هو سلسلة نصية حرة (خيار endpoint `accountcode` يقبل أي String، ويسجل سجل CDR ذلك في حقل بطول 80 حرفًا) يُستخدم عادةً لتخصيص سجل لقسم أو وحدة أعمال. مثال: قسم endpoint في pjsip.conf

```
[8576]
type=endpoint
accountcode=Support
```

علامة AMA ليست خيار endpoint `pjsip.conf` في Asterisk 22؛ قم بتعيينها لكل مكالمة من خلال dialplan باستخدام الدالة `CHANNEL` (على سبيل المثال `Set(CHANNEL(amaflags)=billing)`)، أو باستخدام `Set(CDR(amaflags)=billing)`.

## تغيير تنسيق CSV و/أو CDR

يمكنك تغيير تنسيق CSV عن طريق تعديل ملف cdr_custom.conf.

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

يمكنك تغيير تنسيق CDR في ملف cdr_custom.conf.

## تخزين سجلات المكالمات (CDR)

يمكن تحقيق تخزين سجلات المكالمات بعدة طرق. أهم طريقة هي ملفات نصية بصيغة CSV يمكن استيرادها بسهولة إلى جداول البيانات. بالنسبة للمؤسسات الصغيرة، يكون هذا عادةً كافياً. بعض برامج الفوترة تقبل ملفات CSV بشكل افتراضي. ومع ذلك، فإن تخزين سجلات المكالمات في قاعدة بيانات يكون أفضل بكثير وأكثر أماناً. يدعم Asterisk عدة أنواع من قواعد البيانات. هناك بعض الواجهات الرسومية للفوترة في السوق. مع وجود العديد من السواقات، أي واحدة يجب اختيارها؟

### السواقات المتاحة للتخزين

- cdr_csv – ملفات نصية بصيغة قيم مفصولة بفواصل
- cdr_custom – ملفات نصية قابلة للتخصيص بصيغة قيم مفصولة بفواصل
- cdr_adaptive_odbc – خلفية ODBC متكيفة (مفضلة لتخزين قاعدة البيانات)
- cdr_odbc – قواعد بيانات مدعومة بـ unixODBC (قديمة؛ يفضَّل cdr_adaptive_odbc)
- cdr_pgsql – قواعد بيانات Postgres
- cdr_tds (cdr_freetds) – قواعد بيانات Sybase و MSSQL عبر FreeTDS
- cdr_manager – CDR إلى واجهة المدير
- cdr_radius – واجهة CDR radius
- cdr_sqlite3_custom – وحدة CDR مخصصة لـ SQLite3

تمت إزالة الوحدة `cdr_addon_mysql` (cdr_mysql) التي كانت تُنصح بها الأدلة القديمة في Asterisk 19، لذا لا يوجد سائق MySQL أصلي لسجلات المكالمات في Asterisk 22. لكتابة سجلات المكالمات إلى MySQL/MariaDB، استخدم `cdr_adaptive_odbc` مع سائق MySQL ODBC — وهو النهج المستخدم في هذا الفصل.

يتم تسجيل سجلات المكالمات لجميع الوحدات النشطة المحملة في الملف /etc/asterisk/modules.conf. إذا تم ضبط المعامل autoload=yes، يتم تحميل جميع الوحدات. للتحقق من السواقات cdr_drivers المحملة حالياً في النظام استخدم الأمر أدناه:

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

إذا رأيت لقطة الشاشة أعلاه، فإن cdr_adaptive_odbc و cdr_csv و cdr_custom و cdr_manager و cdr_odbc و cdr_sqlite3_custom تعمل على الأقل. في السنوات الأخيرة بعد بعض astricons أصبح واضحاً لي أن فريق Asterisk يفضّل ODBC. فهو السائق الوحيد الذي يدعم تجميع الاتصالات. تجميع الاتصالات يُعد ميزة كبيرة من حيث الأداء لأنه لا يتعين عليك فتح اتصال جديد لكل عملية. كُتب هذا الفصل في الأصل باستخدام cdr_mysql. انتقلت إلى cdr_adaptive_odbc لهذه النسخة مع العلم أنه أكثر تعقيداً قليلاً في الإعداد. اختيار cdr_adaptive_odbc يتيح لنا أيضاً تخصيص سجلات المكالمات. يمكنك ببساطة ضبط متغيّر CDR جديد في الـ dialplan وإضافة العمود المطابق إلى قاعدة البيانات. على سبيل المثال، لتسجيل تذبذب الصوت:

```
Set(CDR(jitter)=${RTPAUDIOQOSJITTER})
```

### تخزين CSV

كما ذكرنا سابقاً، بشكل افتراضي، يرسل Asterisk جميع سجلات المكالمات إلى ملف نصي بصيغة CSV باستخدام وحدة cdr_csv.so. إذا لم تتمكن من رؤية الملفات في /var/log/asterisk/cdr-csv، تحقق مما إذا كانت الوحدة تُحمَّل باستخدام أمر CLI module show. إذا لم تكن محملة، راجع modules.conf. في هذا الفصل سنرسل سجلات المكالمات إلى cdr_csv كنسخة احتياطية.

### تكوين ملف modules.conf

لتحميل الوحدات المناسبة فقط، استخدم الأسطر أدناه في ملف modules.conf

```
noload => cdr_custom.so
noload => cdr_odbc.so
noload => cdr_manager.so
noload => cdr_sqlite3_custom.so
```

الآن لدينا فقط cdr_csv و cdr_adaptive_odbc محملين.

## Installing and configuring ODBC on Ubuntu 22.04

أنا دائمًا أندم على نشر تعليمات مفصلة في الكتاب. فهي قد تتغير أحيانًا قبل نشر الكتاب. تتغير الإصدارات، وتتغير الوحدات، لذا حاول تعديل الأمر هنا ليتناسب مع وضعك الخاص. في معظم الأحيان تكون التغييرات الطفيفة كافية لإعادة تنفيذ التثبيت. انتبه إلى الخطوات التي قد يجد حتى مستخدمو لينكس ذوو الخبرة صعوبة في تثبيت برامج تشغيل ODBC.

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

## التطبيقات والوظائف

عدة تطبيقات مرتبطة بالفوترة.

### CDR(accountcode)

يضبط رمز حساب قبل استدعاء تطبيق آخر dial(); على سبيل المثال: الصيغة:

```
Set(CDR(accountcode)=account)
```

يمكن التحقق من رمز الحساب باستخدام متغير القناة ${CDR(accountcode)}

### CDR(amaflags)

يضبط علامة لأغراض الفوترة. الخيارات هي default, omit, documentation, و billing.

```
Set(CDR(amaflags)=amaflags)
```

### Set(CDR_PROP(disable)=1)

يعطل تسجيل CDR للقناة الحالية، بحيث لا يُكتب أي CDR إلى الملف أو قاعدة البيانات. إعادته إلى `0` يعيد تمكين التسجيل.

```
Set(CDR_PROP(disable)=1)
```

تم إزالة تطبيق `NoCDR()` الذي استخدمته الإصدارات السابقة لهذا في Asterisk 21؛ في Asterisk 22 يمكنك تعطيل CDR للقناة باستخدام `Set(CDR_PROP(disable)=1)` بدلاً من ذلك.

### ResetCDR()

يعيد ضبط سجل بيانات المكالمة: يتم ضبط وقت `start` (وإذا تم الرد، وقت `answer`) إلى الوقت الحالي ويتم مسح جميع متغيرات CDR. إذا تم ضبط خيار `v`، تُحفظ متغيرات CDR أثناء إعادة الضبط.

### Set(CDR(userfield)=Value)

هذا الأمر يضبط حقل مستخدم في CDR. عند استخدام `cdr_adaptive_odbc`، يُخزن حقل المستخدم تلقائيًا إذا كان هناك عمود `userfield` في جدول CDR — دون الحاجة إلى إعادة تجميع المصدر. بالنسبة لملفات النص CSV، يجب تعديل شفرة المصدر (cdr_csv.c) وإعادة تجميع Asterisk إذا أردت استخدام حقول المستخدم.

الإصدارات السابقة كانت تخزن CDRs في MySQL باستخدام وحدة `cdr_addon_mysql` (`cdr_mysql.conf`). تم إزالة تلك الوحدة في Asterisk 19، لذا فهي غير متوفرة في Asterisk 22. المسار المدعوم الآن هو `cdr_adaptive_odbc` مع برنامج تشغيل MySQL ODBC، الذي يخزن حقل المستخدم — وأي عمود مخصص آخر — بشكل أصلي عبر تخطيط الأعمدة التكيفية الخاص به.

### إلحاق بحقل المستخدم

الإصدارات السابقة استخدمت تطبيق `AppendCDRUserField()` لإلحاق بيانات بحقل المستخدم في CDR. تم إزالة ذلك التطبيق من Asterisk؛ في Asterisk 22 يمكنك إلحاق بحقل المستخدم بقراءة وإعادة ضبطه باستخدام دالة `CDR`، على سبيل المثال
`Set(CDR(userfield)=${CDR(userfield)}extra)`.

![13-call-detail-records figure 1](../images/13-call-detail-records-img01.png)

## توثيق المستخدم

بعض الشركات تقوم بفاتورة المكالمات لموظفيها. في Asterisk يمكنك ضبط مخطط توثيق يتيح لك فوتر المستخدم الموثق على سجل تفاصيل المكالمات (CDR). يمكن إجراء هذا التوثيق باستخدام كلمة مرور تُمرَّر كمعامل لتطبيق Authenticate—ملف كلمة مرور، يُشار إليه بـ / (شرطة مائلة) قبل المعامل، أو مفتاح قاعدة بيانات Asterisk (باستخدام خيار `d`). الصيغة:

```
Authenticate(password[,options[,maxdigits[,prompt]]])
Authenticate(/passwdfile[,options])
```

الخيارات:

- a – يضبط رمز حساب القناة إلى كلمة المرور المدخلة.
- d – يفسّر المسار المعطى كمفتاح قاعدة بيانات Asterisk بدلاً من ملف حرفي.
- m – يفسّر المسار كملف يحتوي على أسطر `accountcode:passwordhash`.
- r – يزيل مفتاح قاعدة البيانات بعد التوثيق الناجح (صالح مع `d` فقط).

إذا فشل المتصل في جميع المحاولات الثلاث، يتم قطع القناة؛ لا يستمر تنفيذ مخطط الاتصال، لذا عالج مسار الفشل في السطر بعد `Authenticate()`. مثال (المكالمات الدولية):

```
exten=_9011.,1,Authenticate(/password,d)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

تم إزالة خيار `j` (القفز إلى الأولوية n+101 عند الفشل) واتفاقية الأولوية `+101` من Asterisk منذ زمن بعيد؛ فشل `Authenticate()` يؤدي ببساطة إلى قطع الاتصال.

لإدخال كلمة المرور في مفتاح قاعدة بيانات من وحدة التحكم:

```
asterisk*CLI> database put senha 123456 1
```

## استخدام كلمات المرور من البريد الصوتي

هذا التطبيق يقوم بنفس وظيفة authenticate، لكنه يستخدم ملف إعدادات البريد الصوتي لكلمة المرور.

```
VMAuthenticate([mailbox][@context][,options])
```

إذا تم تحديد صندوق بريد، فستُعتبر كلمة مرور ذلك الصندوق فقط صالحة. إذا لم يتم تحديد صندوق البريد، سيتم تعيين المتغيّر القنوي `${AUTH_MAILBOX}` بصندوق البريد المصادق عليه. إذا تم تعيين خيار `s`، سيتم تخطي المطالبات الأولية. مثال (المكالمات الدولية):

```
exten=_9011.,1,VMAuthenticate(${CALLERID(num)}@local,s)
 same=>n,Dial(DAHDI/g1/${EXTEN:1},20,tT)
 same=>n,Hangup()
```

## Channel Event Logging (CEL)

تُوفر سجلات CDR صفًّا ملخّصًا واحدًا لكل مكالمة. للحصول على تتبع أكثر تفصيلًا للأحداث — مثل انتقالات حالة القناة الفردية، أحداث دخول/خروج الجسر، وأرجل التحويل المدعومة — يتضمن Asterisk 22 **Channel Event Logging (CEL)**، الذي يُضبط عبر `/etc/asterisk/cel.conf` ويُخزن عبر خلفيات مثل `cel_odbc` أو `cel_custom`.

يُكمل CEL سجلات CDR بدلاً من استبدالها: تظل CDR المعيار لملخصات الفوترة، بينما يوفر CEL بيانات دقيقة لكل حدث مفيدة لاكتشاف الاحتيال، ومراقبة الجودة، وإعداد التقارير المتقدمة.

نمط تكوين `cel.conf` يعكس `cdr.conf`: تقوم بتمكين أنواع الأحداث التي تريدها في قسم `[general]` من `cel.conf`، ثم تُعدّ كل خلفية تخزين في ملفها الخاص — `cel_custom.conf` للـ CSV، `cel_odbc.conf` لقاعدة بيانات ODBC (نفس اتصال `res_odbc.conf` المستخدم لسجلات CDR). يمكنك التأكد مما إذا كان CEL نشطًا باستخدام `cel show status` على سطر الأوامر.

## الملخص

في هذا الفصل تعلمنا كيفية تنفيذ تسجيل CDR في ملفات نصية وفي قاعدة بيانات MySQL. كما تعلمنا كيفية ضبط amaflags وأكواد الحساب. في نهاية الفصل، تعلمنا كيفية استخدام مخطط مصادقة مدمج مع CDR والفوترة.

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
