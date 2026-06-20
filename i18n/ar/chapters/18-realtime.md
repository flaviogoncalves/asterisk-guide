# Asterisk Real-Time

كما تعلم، يتم تحقيق تكوين Asterisk من خلال استخدام عدة ملفات نصية في دليل /etc/asterisk. بالرغم من سهولة استخدام الملفات النصية، هناك بعض العيوب المعروفة:

- الحاجة إلى إعادة تحميل Asterisk في كل مرة يتم فيها تغيير الملفات
- زيادة استهلاك الذاكرة لعدد كبير من المستخدمين
- صعوبة كتابة واجهة توفير باستخدام الملفات النصية
- عدم إمكانية التكامل مع قواعد البيانات الموجودة

ARA أو Asterisk Realtime، كما هو معروف، تم إنشاؤه بواسطة Anthony Mennesale II وMark Spencer وConstantine Filin وصُمم للسماح بالتكامل الشفاف مع قواعد بيانات SQL. كما يتوفر واجهة LDAP. يُعرف هذا النظام أيضًا باسم Asterisk External Configuration ويتم تكوينه في /etc/asterisk/extconfig.conf. يمكنك ربط ملفات التكوين بالجداول في قاعدة البيانات (تكوين ثابت) وإدخالات الوقت الحقيقي لإنشاء الكائنات ديناميكيًا دون الحاجة إلى إعادة تحميل Asterisk.

## الأهداف

بنهاية هذا الفصل، يجب أن يكون القارئ قادرًا على:

- فهم مزايا وقيود Asterisk Real Time.
- استخدام ODBC للاستخدام مع ARA
- تجميع وتثبيت ARA باستخدام ODBC
- اختبار النظام في بيئة مختبرية

## كيف يعمل الوقت الحقيقي في Asterisk؟

في بنية الوقت الحقيقي الجديدة، تم نقل جميع التعليمات البرمجية الخاصة بقاعدة البيانات إلى برامج تشغيل القنوات. القناة لا تستدعي سوى روتين عام يبحث في قاعدة البيانات. النتيجة هي عملية أبسط وأكثر نظافة من منظور شفرة المصدر. يتم الوصول إلى قاعدة البيانات عبر ثلاث وظائف:

- STATIC: تُستخدم لإعداد تكوين ثابت عند تحميل الوحدة.
- REALTIME: تُستخدم للبحث عن الكائنات أثناء مكالمة أو حدث آخر.


- UPDATE: تُستخدم لتحديث الكائنات.

في Asterisk 22، يتم التعامل مع نقاط النهاية SIP بواسطة مجموعة **PJSIP** (`res_pjsip`)، التي بُنيت على نموذج الكائن **Sorcery**. باستخدام معالج `realtime`، يقوم Sorcery بتحميل كل كائن PJSIP من قاعدة البيانات عند الطلب، وتصبح تلك الكائنات بعد ذلك ككائنات PJSIP مُكوَّنة عادية — وليس كأقران وقت حقيقي مؤقتة كان سائق SIP القديم يتخلص منها بعد كل مكالمة.

نظرًا لأنها كائنات حقيقية، فإن عبور NAT، والتأهيل، وإشارة انتظار الرسائل (MWI) تعمل جميعًا بشكل طبيعي لنقاط النهاية الوقت الحقيقي. (يمكن أيضًا إخبار Sorcery بتخزين الكائنات في الذاكرة عبر معالج `memory_cache`، لكن ذلك اختياري ومنفصل عن التحميل في الوقت الحقيقي.) عندما تقوم بتغيير كائن في قاعدة البيانات، يتم التقاط التغيير في البحث التالي؛ لا تحتاج إلى إعادة تحميل بعد كل تعديل. (النموذج الوقت الحقيقي المتقاعد `chan_sip`، مع عائلاته `sippeers`/`sipusers`، مغطى فقط في فصل *القنوات القديمة*.)

## Configuring Asterisk Real Time

لأجل هذا المختبر، سنفترض أنك قد قمت بالفعل بتثبيت ODBC من فصل CDR. يتم تكوين ARA في ملف النص extconfig.conf، حيث يمكن رؤية قسمين بسهولة. الأول هو قسم ملفات التكوين الثابتة، حيث يمكنك استبدال ملفات التكوين النصية بجداول قاعدة البيانات. القسم الثاني هو محرك التكوين الفوري، حيث تقوم بتكوين جداول قاعدة البيانات للكائنات الديناميكية (الأقران/المستخدمين). ليس من غير المألوف استخدام ملفات نصية للتكوين الثابت وقاعدة البيانات للمدخلات الديناميكية. في هذه الحالة، يبقى القسم الأول دون تعديل.

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

قسم التكوين الثابت هو المكان الذي تخزن فيه ما يعادل ملفات التكوين في قاعدة البيانات. يتم قراءة هذه التكوينات أثناء تحميل Asterisk. بعض الوحدات تعيد قراءة قاعدة البيانات عندما تقوم بإعادة تحميلها. أمثلة على التكوين الثابت هي:

```
<conf filename> => <driver>,<databasename>[,table_name]
queues.conf => mysql,asteriskdb,queues_conf
pjsip.conf => odbc,asteriskdb,pjsip_conf
iax.conf => ldap,MyBaseDN,iax
```

يكون ربط الملف الثابت أكثر فائدة لملفات التكوين التي لا تمتلك ما يعادلها الفوري لكل كائن. بالنسبة لـ PJSIP، يفضَّل استخدام عائلات الفوري لكل كائن (`ps_endpoints`، `ps_aors`، وما إلى ذلك) الموضحة لاحقًا في هذا الفصل بدلاً من ربط كامل `pjsip.conf` كملف ثابت.

ثلاثة أمثلة موصوفة أعلاه. في المثال الأول، تقوم بربط queues.conf بجدول queues في قاعدة البيانات asteriskdb. في المثال الثاني، تقوم بربط pjsip.conf بالجدول pjsip_conf في قاعدة البيانات asteriskdb المعرفة في تكوين ODBC. في المثال الأخير، تقوم بربط iax.conf بدليل LDAP. MyBaseDN هو الـ DN الأساسي الذي يُبحث فيه. في المثال السابق، يتم تحميل التطبيق app_queue.so بينما يستعلم برنامج تشغيل MySQL قاعدة البيانات ويحصل على المعلومات المطلوبة.

### Real Time configuration section

قسم التكوين الفوري (الجزء الثاني من ملف extconfig.conf) هو المكان الذي يتم فيه تكوين، تحديث، وإلغاء تحميل قطعة التكوين التي سيتم تحميلها في الوقت الفعلي. مع الفوري، لا يصبح من الضروري إعادة تحميل التكوينات. تتبع صيغة الفوري القواعد التالية:

```
<family name> => <driver>,<database name>[,table_name]
```

مثال:

```
ps_endpoints => odbc,asterisk,ps_endpoints
ps_aors => odbc,asterisk,ps_aors
queues => odbc,asterisk,queue_table
queue_members => odbc,asterisk,queue_member_table
voicemail => odbc,asterisk,test
```

هنا لدينا خمس أسطر تكوين. في السطر الأول، تقوم بربط عائلة PJSIP/Sorcery `ps_endpoints` بجدول `ps_endpoints` في قاعدة البيانات asteriskdb. في الأخير، تقوم بربط عائلة voicemail بالجدول test في قاعدة البيانات asteriskdb. كل نوع كائن PJSIP (endpoint، aor، auth، contact) يحصل على عائلته وجدوله الخاص؛ المجموعة الكاملة موضحة في قسم "PJSIP Realtime (Sorcery)" أدناه. عائلات `voicemail`، `extensions`، `queues`، و`queue_members` لا تزال صالحة في Asterisk 22.

## PJSIP Realtime (Sorcery)

على Asterisk 22، يتم التعامل مع نقاط النهاية SIP حصريًا بواسطة مجموعة **PJSIP** (`res_pjsip`)، والتي تُبنى على طبقة التجريد الكائنية **Sorcery**. بدلاً من "نظير" SIP واحد، يقوم PJSIP بتقسيم حساب SIP إلى عدة أنواع كائنات، يُخزن كل منها في جدول realtime خاص به:

| Sorcery object type | Realtime table | What it holds |
|---------------------|----------------|---------------|
| endpoint | ps_endpoints | إعدادات كل حساب (context، codecs، DTMF، إلخ) |
| aor (address of record) | ps_aors | حدود التسجيل وإعدادات `qualify` |
| auth | ps_auths | بيانات اعتماد `username` / `password` |
| contact | ps_contacts | الموقع المُسجل ديناميكيًا |
| domain alias | ps_domain_aliases | نطاقات SIP بديلة لنقطة النهاية |
| endpoint identifier by IP | ps_endpoint_id_ips | مطابقة نقطة النهاية حسب عنوان IP المصدر |

يتم تمكين Realtime لـ PJSIP في مكانين. أولاً، قم بربط أنواع كائنات Sorcery بـ realtime في `extconfig.conf`:

```
[settings]
ps_endpoints => odbc,asterisk
ps_aors => odbc,asterisk
ps_auths => odbc,asterisk
ps_contacts => odbc,asterisk
ps_domain_aliases => odbc,asterisk
ps_endpoint_id_ips => odbc,asterisk
```

ثانيًا، أخبر Sorcery باستخدام معالج `realtime` لتلك الأنواع من الكائنات في `sorcery.conf`. اسم الخريطة (هنا `res_pjsip`) هو الوحدة التي تُعيد توطين كائناتها، والقيمة على الجانب الأيمن تشير إلى العائلة التي عرّفتها في `extconfig.conf`:

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

يمكنك خلط الكائنات الثابتة مع كائنات realtime. إذا حذفت نوعًا من `sorcery.conf`، سيستمر هذا النوع في القراءة من `pjsip.conf`. نمط شائع هو إبقاء النقل الثابت والإعدادات العامة في `pjsip.conf` بينما تُخزن نقاط النهاية، aors، auths، وcontacts في قاعدة البيانات.

### Creating the PJSIP realtime schema with Alembic

توفر Asterisk ترحيلات قاعدة البيانات لجميع مخططات realtime تحت `contrib/ast-db-manage`. هذه هي الطريقة المدعومة لإنشاء (وترقية الإصدارات) جداول PJSIP — لم تعد تحتاج إلى كتابة تعريفات الجداول `ps_*` يدويًا. مجموعة ترحيلات `config` تحتوي على جداول PJSIP/Sorcery.

```
cd /usr/src/asterisk-22.x/contrib/ast-db-manage
cp config.ini.sample config.ini
# edit config.ini → set sqlalchemy.url, e.g.
#   sqlalchemy.url = mysql+pymysql://astdb:CHANGE_ME_DB_PASSWORD@127.0.0.1/astdb
alembic -c config.ini upgrade head
```

ينشئ هذا `ps_endpoints`، `ps_aors`، `ps_auths`، `ps_contacts`، وغيرها من جداول PJSIP بالأعمدة الصحيحة للإصدار الجاري من Asterisk. (يتطلب Alembic حزمة Python `alembic` بالإضافة إلى برنامج تشغيل SQLAlchemy مثل `pymysql` لـ MySQL/MariaDB أو `psycopg2` لـ PostgreSQL.)

نقطة نهاية realtime الحد الأدنى تتكون من صف واحد في كل من الجداول الثلاثة — على سبيل المثال نقطة النهاية `6010`:

```
ps_auths:      id=6010-auth, auth_type=userpass, username=6010, password=supersecret
ps_aors:       id=6010, max_contacts=1
ps_endpoints:  id=6010, transport=transport-udp, aors=6010, auth=6010-auth,
               context=from-internal, disallow=all, allow=ulaw,
               direct_media=no
```

بعد إدخال الصفوف لا حاجة لإعادة تحميل — سيقوم REGISTER/INVITE التالي بجلب الكائنات من قاعدة البيانات. يمكنك التأكد مما أعاد realtime بالأمر التالي:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

## تكوين قاعدة البيانات

الآن بعد أن قمنا بتكوين ملف extconfig.conf، دعنا ننشئ الجداول. بشكل عام، كل عمود في قاعدة البيانات يطابق اسم خيار من ملف التكوين المقابل. جداول PJSIP `ps_*` تتبع هذه القاعدة: كل عمود `ps_endpoints` يُسمى باسم خيار نقطة النهاية `pjsip.conf`، كل عمود `ps_auths` بعد خيار المصادقة، وهكذا. على سبيل المثال، نقطة النهاية `pjsip.conf` أدناه،

```
[4000](endpoint)
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=4000
aors=4000
```

يتم تخزينها كصف واحد عبر ثلاث جداول. الصف `ps_endpoints` يحتوي على `id=4000, context=from-internal, disallow=all, allow=ulaw, auth=4000, aors=4000`؛ الصف `ps_auths` يحتوي على `id=4000, auth_type=userpass, username=4000, password=supersecret`؛ والصف `ps_aors` يحتوي على `id=4000, max_contacts=1`. لا تحتاج إلا إلى ملء الأعمدة التي تستخدمها فعليًا — أي عمود تتركه NULL سيعود إلى القيمة الافتراضية للخيار. إذا أردت، على سبيل المثال، معلمة `callerid` على نقطة النهاية، املأ عمود `callerid` في `ps_endpoints` (اسم العمود هو نفسه اسم خيار `pjsip.conf`).

جدول البريد الصوتي يتبع نفس الفكرة. أعمدته تُطابق حقول `voicemail.conf`:

| uniqueid | mailbox | context | password | email | fullname |
|----------|---------|---------|----------|-------|----------|
| 1 | 4000 | default | 4000 | john@doe.com | John Doe |

يجب أن يكون `uniqueid` فريدًا لكل مستخدم بريد صوتي ويمكن أن يكون تلقائي الزيادة. لا يلزم أن يكون له أي علاقة بصندوق البريد أو السياق.

### بناء مخطط الاتصال باستخدام Asterisk Real Time

يمكنك أيضًا استخدام نظام الوقت الحقيقي لإنشاء مخطط الاتصال. يستخدم ARA بيان `switch` لتضمين امتدادات الوقت الحقيقي في مخطط الاتصال العادي الموجود في ملف extensions.conf. يجب أن يبدو جدول الامتداد كما هو أدناه:

| context | exten | priority | app | appdata |
|---------|-------|----------|-----|---------|
| from-internal | 4000 | 1 | Dial | PJSIP/4000 |

عائلة الوقت الحقيقي `extensions` لم تتغير في Asterisk 22؛ فقط تأكد من أن عمود `appdata` يطلب قنوات PJSIP، على سبيل المثال `PJSIP/4000`. في مخطط الاتصال، عليك استخدام أمر `switch` لاستخدام الوقت الحقيقي.

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

في هذا المختبر، سنُعِد قاعدة البيانات لاستقبال معلمات Asterisk. سنُعِد فقط جداول REALTIME. سيُترك التكوين الثابت إلى ملفات النصوص التكوينية (رائع، أليس كذلك؟). إنشاء الجداول في MySQL يتبع ما يلي.

Step 1: Get into the MySQL database as root.

```
mysql -u root -p
```

Step 2: Log in to the MySQL server created in the CDR labs.

```
mysql -u astdb -p
```

When asked for the password, type supersecret.

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

You should see the PJSIP `ps_*` tables (created by the Alembic `config` migration), along with the `voicemail`, `extensions`, and other realtime tables:

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

(Alembic creates more tables than these — the list above shows the ones relevant to this lab.)

Step 5: The database is already configured for ODBC (since the CDR lab), so no further ODBC setup is needed here.

Step 6: Inspect and populate the tables from the MySQL client. You do not need a graphical tool such as phpMyAdmin — every step in this chapter is plain, copy-pasteable SQL run from the `mysql` command line. Connect to the `astdb` database (use `supersecret` when prompted):

```
mysql -u astdb -p astdb
```

You can confirm the columns of a table at any time with `DESCRIBE`, for example:

```
mysql> DESCRIBE ps_endpoints;
mysql> DESCRIBE ps_auths;
mysql> DESCRIBE ps_aors;
```

These tables were created by the Alembic `config` migration, so their columns already match the `pjsip.conf` option names for the running Asterisk version — you only fill in the columns you need.

## مختبر: تكوين واختبار ARA

في هذا المختبر سنقوم بتغيير تكوين ملف **extconfig.conf** ليعكس تكوين قاعدة البيانات والجداول الخاصة بنا.

الخطوة 1: تكوين **extconfig.conf** وإعادة تحميل Asterisk.

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

لاحظ عائلات `ps_endpoints`، `ps_aors`، `ps_auths`، و`ps_contacts` أعلاه؛ مع تطابق تعيينات `sorcery.conf` (انظر قسم "PJSIP Realtime (Sorcery)") تجعل PJSIP يقرأ حساباته من قاعدة البيانات. عائلتا `voicemail` و`extensions` تكملان المثال.

الخطوة 2: اختبار امتداد الوقت الحقيقي. أنشئ نقطة نهاية **`6010`** جديدة بإدخال صف واحد في كل من `ps_auths`، `ps_aors`، و`ps_endpoints`، ثم حاول تسجيل هذه النقطة النهاية باستخدام هاتف برمجي. نفّذ الأمر SQL التالي في عميل `mysql` (`mysql -u astdb -p astdb`):

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

الصفوف الثلاثة معًا تصف حساب SIP واحد. إعدادات الحساب المتبقية موزعة عبر كائنات PJSIP: السياق، الترميزات، وضع DTMF، ومعالجة الوسائط التي تعيش على نقطة النهاية (الأعمدة الستة الأخيرة أعلاه)؛ التسجيل الديناميكي يعيش على الـ AOR. لا يوجد علم "ديناميكي" منفصل — الـ AOR يقبل REGISTERs ديناميكية طالما أن `max_contacts` أكبر من الصفر، ويتم كتابة كل موقع مسجل إلى `ps_contacts`.

في PJSIP يُطلق على وضع DTMF خارج النطاق RFC 2833 / RFC 4733 اسم `rfc4733`، و`dtmf_mode=rfc4733` هو الإعداد الافتراضي — لذا فإن العمود `dtmf_mode` أعلاه اختياري ويُظهر فقط للتوضيح.

الخطوة 3: حاول تسجيل الهاتف الجديد باستخدام هاتف برمجي مع اسم المستخدم `6010` وكلمة المرور `supersecret`. أكد التسجيل على سطر أوامر Asterisk:

```
asterisk-server*CLI> pjsip show endpoint 6010
asterisk-server*CLI> pjsip show contacts
```

الخطوة 4: أدرج الامتدادات في قاعدة البيانات.

```
mysql -u astdb -p
```

أدخل كلمة المرور:

استخدم **supersecret** عندما يُطلب منك ذلك، ثم أدخل صف الامتداد من عميل MySQL:

```sql
USE astdb;
INSERT INTO extensions (id, context, exten, priority, app, appdata)
VALUES ('1', 'test', '6007', '1', 'Dial', 'PJSIP/bria');
```

الخطوة 5: أدمج الوقت الحقيقي لـ Asterisk في مخطط الاتصال. في السياق `default`:

```
switch => realtime/test@extensions
```

أعد تحميل الامتدادات لتفعيل التغيير.

```
asterisk-server*CLI> extensions reload
```

الخطوة 6: أعد تكوين أحد الهواتف إلى اسم المستخدم `bria`، إذا لم تقم بذلك مسبقًا.

الخطوة 7: اطّلق الرقم 6007 من هاتف موجود؛ يجب أن يرن هاتف `bria`.

## الملخص

في هذا الفصل، تعلمت أن Asterisk Real Time يتيح لك وضع إعداداتك في قاعدة بيانات. تُوفر Asterisk مشغلات real‑time محلية لـ ODBC (التي تصل إلى أي قاعدة بيانات مدعومة من UnixODBC، بما في ذلك MySQL/MariaDB و SQLite) و PostgreSQL، بالإضافة إلى مشغل LDAP real‑time لخدمات الدليل. يتم الوصول إلى MySQL/MariaDB من خلال ODBC، كما فعلنا في هذا الفصل (هناك إضافة مخصصة `res_config_mysql` أيضاً، لكنها تقع خارج بناء النواة، لذا فإن ODBC هو المسار الشائع). تُقسم الإعدادات إلى ثابتة و real‑time. تستبدل الإعدادات الثابتة ملفات الإعداد، بينما تُنشئ إعدادات real‑time كائنات ديناميكية تُحمَّل فقط عندما يحدث اتصال أو حدث مرتبط آخر. اختتمنا بمختبر عملي حول كيفية تثبيت وتكوين ARA.

## Quiz

1. Asterisk Realtime هو جزء من توزيع Asterisk القياسي.  
   - A. True  
   - B. False  
2. يتم تكوين معلمات اتصال خادم قاعدة البيانات في الملف:  
   - A. extensions.conf  
   - B. pjsip.conf  
   - C. res_odbc.conf  
   - D. extconfig.conf  
3. ملف `extconfig.conf` يكوّن الجداول المستخدمة بواسطة Realtime. له قسمان مميزان (اختر اثنين):  
   - A. Static configuration  
   - B. Realtime configuration  
   - C. Outbound routes  
   - D. IP addresses and database ports  
4. في التكوين الثابت، بمجرد تحميل الكائنات من قاعدة البيانات تُحفظ في ذاكرة Asterisk وتُحدَّث فقط عند البدء أو إعادة التحميل.  
   - A. True  
   - B. False  
5. PJSIP realtime (Sorcery) يدعم بالكامل `qualify` و MWI لنقاط النهاية في الوقت الحقيقي، لأن Sorcery يحملها ككائنات PJSIP مُكوَّنة عادية بدلاً من إهمالها بعد كل مكالمة كما كان يحدث مع أقران SIP realtime القديمة.  
   - A. True  
   - B. False  
6. في PJSIP realtime، أي الجداول تحتفظ بنقاط النهاية وجهات الاتصال المسجلة الخاصة بها؟  
   - A. `ps_endpoints` and `ps_contacts`  
   - B. `ps_peers` and `ps_registry`  
   - C. `ps_config` and `ps_data`  
   - D. `extconfig` and `res_odbc`  
7. لا يزال بإمكانك استخدام ملفات التكوين النصية حتى بعد تمكين ARA.  
   - A. True  
   - B. False  
8. phpMyAdmin إلزامي عند استخدام Realtime.  
   - A. True  
   - B. False  
9. يجب إنشاء قاعدة البيانات بكل حقل موجود في ملف التكوين.  
   - A. True  
   - B. False  
10. في Asterisk 22، ما هي الطريقة الموصى بها، المتوافقة مع الإصدار، لإنشاء جداول PJSIP realtime (`ps_endpoints`، `ps_aors`، `ps_auths`، `ps_contacts`)؟  
    - A. Hand-write the `CREATE TABLE` statements for each `ps_*` table  
    - B. Import the legacy `mysql_config.sql` from `contrib/realtime/`  
    - C. Run the Alembic `config` migrations under `contrib/ast-db-manage` (`alembic -c config.ini upgrade head`)  
    - D. The tables are created automatically the first time Asterisk starts  

**Answers:** 1 — A · 2 — C · 3 — A, B · 4 — A · 5 — A · 6 — A · 7 — A · 8 — B · 9 — B · 10 — C
