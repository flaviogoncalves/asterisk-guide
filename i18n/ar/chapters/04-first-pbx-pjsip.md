# بناء أول نظام PBX الخاص بك باستخدام PJSIP

في هذا الفصل، ستتعلم كيفية إجراء تكوين أساسي لنظام Asterisk PBX. الهدف الرئيسي هنا هو رؤية تشغيل الـ PBX للمرة الأولى، القدرة على الاتصال بين الامتدادات، تشغيل رسالة صوتية، والاتصال بفرع تناظري أو فرع SIP واحد. الفكرة وراء هذا الفصل هي التأكد من أن نظام Asterisk الخاص بك يعمل ويعمل بأسرع ما يمكن. بعد إكمال العمل في هذا الفصل، ستحصل على خلفية كافية للتحضير للفصول اللاحقة، حيث سنتعمق أكثر في تفاصيل التكوين.

## الأهداف

- فهم وتحرير ملفات التكوين؛
- تثبيت هواتف برمجية تعتمد على SIP؛
- تثبيت وتكوين خط SIP trunk؛
- تثبيت وتكوين اتصال تناظري؛
- الاتصال بين الامتدادات؛
- الاتصال بين الهواتف والوجهات الخارجية؛ و
- تكوين موظف تلقائي.

## فهم ملفات التكوين

Asterisk يتم التحكم فيه بواسطة ملفات تكوين نصية تقع في /etc/asterisk. تنسيق الملف مشابه لملفات Windows “.ini”. يُستخدم الفاصلة المنقوطة كحرف ملاحظة، وتُعادل العلامتان “=” و “=>”، وتُهمل الفراغات.

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk يفسّر “=” و “=>” بنفس الطريقة. تُستخدم الاختلافات في الصياغة للتمييز بين الكائنات والمتغيرات. استخدم “=” عندما تريد إعلان متغير و “=>” لتعيين كائن. الصياغة هي نفسها في جميع الملفات، لكن هناك ثلاثة أنواع من القواعد تُستَخدم، كما يُناقش أدناه.

## القواعد

| القاعدة | كيفية إنشاء الكائن | ملف التكوين | مثال |
|---------|-------------------|------------|------|
| مجموعة بسيطة | جميعها في نفس السطر | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| وراثة الخيارات | تُعرّف الخيارات أولاً، ثم يرث الكائن هذه الخيارات | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| كيان معقد | كل كيان يحصل على سياق | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### مجموعة بسيطة

تنسيق المجموعة البسيطة المستخدم في `extensions.conf` و`voicemail.conf` هو أبسط قواعد النحو. يُعلن عن كل كائن مع الخيارات في نفس السطر. مثال:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

في هذا المثال، يُنشأ الكائن 1 بالخيارات op1 وop2 وop3 بينما يُنشأ الكائن 2 بالخيارات op1 وop2 وop3.

### قواعد وراثة خيارات الكائن

يُستخدم هذا التنسيق في ملفي chan_dahdi.conf وagents.conf، حيث تتوفر العديد من الخيارات، وتشارك معظم الواجهات والكائنات نفس الخيارات. عادةً ما تحتوي قسم أو أكثر على إعلانات كائنات وقنوات. تُعلن الخيارات الخاصة بالكائن فوق الكائن ويمكن تغييرها لكائن آخر. رغم أن هذا المفهوم صعب الفهم، إلا أنه سهل الاستخدام للغاية. مثال:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

السطران الأولان يحددان قيمة الخيارين op1 وop2 إلى “bas” و“adv” على التوالي. عندما يُنشأ الكائن 1، يُخلق باستخدام الخيار 1 كـ “bas” والخيار 2 كـ “adv”. بعد تعريف الكائن 1، نغيّر الخيار 1 إلى “int”. بعد ذلك، ننشئ الكائن 2 مع الخيار 1 كـ “int” والخيار 2 كـ “adv”.

### كائن كيان معقد

يُستخدم هذا التنسيق في pjsip.conf وiax.conf وغيرها من ملفات التكوين التي توجد فيها العديد من الكيانات مع خيارات كثيرة. عادةً لا تشترك هذه الصيغة في حجم كبير من التكوينات المشتركة. كل كيان يحصل على سياق. أحيانًا توجد سياقات محجوزة، مثل [general] للتكوينات العامة. تُعلن الخيارات في إعلانات السياق. مثال:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

الكيان [entity1] لديه القيم “value1” و“value2” للخيارات op1 وop2 على التوالي. الكيان [entity2] لديه القيم “value3” و“value4” للخيارات op1 وop2.

## خيارات بناء مختبر لـ Asterisk

لتكوين PBX، ستحتاج إلى بعض الأجهزة الأساسية. ليست صعبة أو مكلفة، لكن هناك بعض الخيارات التي يجب مراعاتها. كل ما تحتاجه هو هاتفان واتصال بالشبكة العامة. هناك خيارات وتوليفات ممكنة عند إنشاء مختبرك، سنناقشها أدناه.

### الخيار 1: مختبر كامل

مع المختبر الكامل، يمكن اختبار جميع السيناريوهات المتاحة ومقارنة الحلول مثل ATA، هواتف IP، والهواتف البرمجية. يمكنك أيضًا التعرف على الخطوط التناظرية وSIP. ستحتاج إلى:

- محول هاتف تناظري SIP (ATA)
- هاتف IP
- خادم مخصص لـ Asterisk
- محطة عمل مع هاتف برمجي
- بطاقة واجهة تناظرية تحتوي على واجهتين على الأقل (1 FXO و 1 FXS)
- حساب مزود خدمة VoIP

### الخيار 2: مختبر اقتصادي

مع المختبر الاقتصادي، نبسط الأمر قليلًا. نستخدم ATA، الذي يكون عادةً أقل تكلفة من هاتف IP، وبطاقة FXO واحدة، وهي رخيصة جدًا. لن نتمكن من استخدام هواتف تناظرية متصلة مباشرة بالخادم، لكن هذا لا يحدث عادةً في الواقع. ستحتاج إلى:

- محول هاتف تناظري SIP (ATA)
- خادم مخصص لـ Asterisk
- محطة عمل للهواتف البرمجية
- بطاقة واجهة تناظرية بواجهة FXO واحدة
- حساب مع مزود خدمة VoIP

### الخيار 3: مختبر اقتصادي فائق

المختبر الثالث يستخدم خادمًا افتراضيًا على حاسوب الطالب المحمول. المشكلة في هذا النموذج هي التعارضات التي يولدها منفذ UDP. أحيانًا يحاول كل من خادم Asterisk والهاتف البرمجي الوصول إلى نفس المنفذ، مما يمنع Asterisk من ربط منفذ العنوان. مشكلة أخرى هي جودة المكالمات؛ البيئات الافتراضية غير مناسبة للتطبيقات الفورية مثل Asterisk. استخدم هاتفًا برمجيًا مجانيًا للخادم ومحطة العمل واتصال trunk إلى مزود SIP. ستحتاج إلى:

- حاسوب محمول يعمل بهاتف برمجي
- آلة افتراضية (VirtualBox، VMware، أو ما شابه) لتثبيت Asterisk
- حساب مع مزود خدمة VoIP

## تسلسل التثبيت

لمساعدتك على فهم تسلسل التثبيت، قمنا بتوضيح الخطوات اللازمة لتثبيت وتكوين Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. تكوين الامتدادات
   - a. امتدادات SIP (ATA، Softphone، IP Phone)
   - b. امتدادات IAX
   - c. امتدادات FXS
2. تكوين الخطوط (Trunk)
   - a. تكوين خط SIP
   - b. تكوين خط FXO
3. بناء مخطط طلبات (dial plan) أساسي
   - a. الاتصال بين الامتدادات
   - b. الاتصال بالوجهات الخارجية
   - c. استقبال مكالمة من امتداد المشغل
   - d. استقبال مكالمة في خدمة الرد الآلي (auto‑attendant)

## Configuration of the extensions

The extensions are SIP, IAX, or analog phones connected to an FXS port. To configure an extension, you should edit the configuration file related to the channel (pjsip.conf, iax.conf, chan_dahdi.conf)

### SIP extensions

On Asterisk 22, PJSIP (the `res_pjsip` stack, configured in `/etc/asterisk/pjsip.conf`) is the SIP channel driver. It supports multiple transports per endpoint, is actively maintained, and is the only SIP driver shipped with the platform. (The original `chan_sip` driver was removed in Asterisk 21 — see the *Legacy channels* chapter if you need to migrate an old configuration.)

The idea here is to configure a simple PBX. (Subsequent chapters provide an entire SIP/PJSIP session with all the details.) PJSIP is configured in `/etc/asterisk/pjsip.conf` and holds all the parameters related to SIP phones and VoIP providers. SIP clients have to be configured before you can make and receive calls.

#### The transport

In PJSIP, the listener configuration (bind address, port, protocol) lives in a `transport` object. Asterisk has built-in protection against username guessing — it always returns an identical authentication challenge for unknown and known users, and repeated unidentified requests from one IP are rate-limited via the `[global]` options `unidentified_request_count`/`unidentified_request_period`. The main options of a transport are:

- protocol: The transport protocol — `udp`, `tcp`, `tls`, `ws`, or `wss`.
- bind: Address and port the listener binds to. If you set the address to `0.0.0.0`, it binds to all interfaces; the SIP port defaults to 5060 for UDP/TCP.

A minimal UDP transport:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP allows the `endpoint`, `auth`, and `aor` sections to share the same section name (e.g. the two `[6001]` blocks above, distinguished by their `type=`); many admins instead suffix them (`[6001]`, `[6001-auth]`, `[6001]` aor) for readability. For a device that registers, the contact is learned dynamically when the phone registers, so the AOR needs no static `contact`.

## IAX Extensions

`chan_iax2` لا يزال يُضمّن في Asterisk 22 لكنه الآن قديم؛ SIP/PJSIP هو البروتوكول المفضّل للنشرات الجديدة.

يمكنك أيضاً إنشاء امتدادات IAX. هذا البروتوكول أصلي في Asterisk، وسنخصص له قسماً كاملاً لاحقاً في هذا الكتاب. الآن، لننشئ بعض الامتدادات باستخدام هذا البروتوكول. كأول قسم يتم تكوينه، يحتوي قسم [general] على بعض المعلمات التي يجب ضبطها. الخيارات الرئيسية هي:

- allow/disallow: يحدد أيّ **codecs** سيتم استخدامها.
- bindaddr: العنوان الذي يرتبط به مستمع IAX2. إذا ضبطته على 0.0.0.0 (الإعداد الافتراضي)، سيتصل بجميع الواجهات.
- context: يحدد السياق الافتراضي لجميع العملاء ما لم يتم تغييره في قسم العميل. استخدمنا dummy لأسباب أمنية. المستخدمون غير المصادق عليهم يدخلون هذا السياق عندما يُضبط الخيار allowguest على yes.
- bindport: منفذ UDP الخاص بـ IAX2 للاستماع عليه (الافتراضي 4569).
- delayreject: عندما يُضبط على yes، يؤخر إرسال رفض المصادقة لطلب REGREQ أو AUTHREQ، مما يحسّن الأمان ضد هجمات القوة الغاشمة على كلمة المرور.
- bandwidth: عندما يُضبط على high، يسمح باختيار **codecs** ذات النطاق الترددي العالي، مثل g711 بأشكالها ulaw و alaw.

العينة التالية هي مثال لقسم [general] في ملف iax.conf.

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX Clients

بعد الانتهاء من أقسام العامة، حان الوقت لإعداد عملاء IAX.

- `[name]`: اسم القسم هو اسم الـ IAX peer/user؛ يتم مطابقة اتصال IAX الوارد إليه بالاسم.
- `type`: فئة الاتصال — `peer`، `user`، أو `friend`:
  - `peer`: Asterisk يرسل المكالمات إلى peer.
  - `user`: Asterisk يتلقى المكالمات من user.
  - `friend`: كلا الاتجاهين في آن واحد.
- `host`: عنوان IP أو اسم المضيف. القيمة الأكثر شيوعاً هي `dynamic`، تُستخدم عندما يسجل الجهاز إلى Asterisk.
- `secret`: كلمة المرور للمصادقة على peers و users.

تحذير: استخدم كلمات مرور قوية لا تقل عن 8 أحرف، تشمل أحرفاً أبجدية رقمية ورقمية، وعلى الأقل رمز واحد. ظهرت تقارير عن خوادم مخترقة في قوائم البريد، وتتوفر أدوات كسر كلمة المرور للقوة الغاشمة لهاشات IAX md5 للهاكرز المبتدئين. احتيال المكالمات يكلّف آلاف الدولارات للمستهلكين والمزودين. مثال:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configuring the SIP devices

After defining the phones in the Asterisk configuration file, it is time to configure the phone itself. In this example, we will show how to configure a free softphone — the SipPulse Softphone (download it from https://www.sippulse.com/produtos/softphone). Check your device’s manual to understand the parameters of your phone. Step 1: Configure the phone to use the extension 6000. Execute the installation program. After the execution, open the account/SIP settings and add a new SIP account. Fill in the required information.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirm that your phone is registered using the console command `pjsip show endpoints` (or `pjsip show endpoint 6000` for detail; `pjsip show contacts` shows the registered AOR contacts). Repeat the configuration for the phone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## تكوين أجهزة IAX

IAX2 هو بروتوكول قديم (انظر فصل *القنوات القديمة*), و Softphone SipPulse يدعم SIP فقط، لذا لا يمكنه تسجيل حساب IAX. إذا كنت بحاجة لاختبار IAX2، استخدم هاتفًا نرمًا لا يزال يدعمه. أنشئ حساب IAX جديد،

3. اختر حساب IAX جديد.  
4. أدخل الخيارات المتعلقة بهاتف 6003 واختياريًا لهاتف 6004.  
5. احفظ التكوين وتحقق مما إذا كان الهاتف مسجلاً باستخدام `iax2 show peers`.

مهم: استخدم حسابًا واحدًا لـ SIP وآخر لـ IAX. إذا أردت تكوين النظام لينبه كل من IAX و SIP في نفس الوقت، سنوضح لك كيفية القيام بذلك في قسم مخطط الاتصال.

### تكوين واجهة PSTN

للاتصال بـ PSTN، ستحتاج إلى واجهة مكتب تبادل خارجي (FXO) وخط هاتف. يمكنك أيضًا استخدام امتداد PBX موجود. يمكنك الحصول على بطاقة واجهة هاتفية بواجهة FXO من عدة مصنعين. في هذا المثال، سنوضح لك كيفية تثبيت بطاقة واجهة DAHDI.

![FXS and FXO ports: the FXS port drives an analog phone (supplies dial tone and ring), while the FXO port connects Asterisk to the Telco line.](../images/04-first-pbx-fig02.png)

### الخطوط التناظرية باستخدام DAHDI

يمكنك شراء بطاقة تناظرية متوافقة مع DAHDI من عدة مصنعين. كانت X100P واحدة من أولى بطاقات Digium وقد تم إيقاف إنتاجها بالفعل. لا يزال بعض المصنعين ينتجون نسخًا مشابهة. بالإضافة إلى سعر X100P، وجدنا عدة مشكلات بين هذه البطاقات واللوحات الأم الجديدة، لذا استخدمها بحذر. X100P، في رأيي، ليست خيارًا جيدًا لبيئة الإنتاج. أي بطاقة متوافقة مع DAHDI يجب أن تعمل. بفضل فريق مطوري DAHDI، لدينا الآن أداة لاكتشاف وتكوين بطاقات الواجهة تقريبًا تلقائيًا. إذا كنت قد قمت لتوّك بتثبيت تعريفات DAHDI، لا تنس تشغيل make config وإعادة تشغيل الجهاز لتحميلها تلقائيًا. يمكنك استخدام الأوامر أدناه لاكتشاف وتكوين بطاقتك. الخطوة 1: لاكتشاف عتادك، استخدم:

```
dahdi_hardware
```

الخطوة 2: لاستخدام التكوين استخدم:

```
dahdi_genconf
```

الأمر أعلاه سيُنشئ ملفين ‎/etc/dahdi/system.conf‎ و ‎/etc/asterisk/dahdi-channels.conf‎. عادةً ما تكون المعلمات الافتراضية لـ ‎dahdi_genconf‎ مناسبة، لكن يمكنك تعديلها في الملف ‎/etc/dahdi/genconf_parameters‎. بشكلٍ افتراضي، سيُدرج السطر (FXO) في السياق ‎from-pstn‎ والهواتف (FXS) في السياق ‎from-internal‎.  
الخطوة 3: بعد تشغيل ‎dahdi_genconf‎، في السطر الأخير من الملف ‎/etc/asterisk/chan_dahdi.conf‎ أضف السطر التالي:

```
#include dahdi-channels.conf
```

الخطوة 4: حرّر الملف /etc/dahdi/modules وضع تعليقات لجميع التعريفات غير المستخدمة. أعد تشغيل النظام قبل المتابعة وتحقق مما إذا كانت القنوات يتم التعرف عليها باستخدام:

```
*CLI> dahdi show channels
```

### الاتصال بشبكة PSTN عبر مزود VoIP

إذا كان ميزانيتك محدودة للغاية، يمكنك تكوين trunk SIP للاتصال بشبكة PSTN. إنها بالتأكيد الطريقة الأكثر توفيرًا للاتصال بشبكة PSTN. هناك آلاف مزودي VoIP حول العالم. للاتصال بأحدهم، ستحتاج إلى بعض المعلمات. المعلمات التي يوفرها مزود SIP.

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

يجب أن تحدد معلمين بنفسك.

- Extension to receive calls—in this case: 9999
- context: from-sip

في PJSIP، يتم بناء trunk SIP مسجل من نفس عائلة الكائنات المستخدمة لنقطة النهاية، بالإضافة إلى كائنات `registration` و`identify` الصريحة. كائن `registration` يخبر Asterisk بالتسجيل لدى المزود، كائن `identify` يطابق حركة المرور الواردة من عنوان IP الخاص بالمزود إلى نقطة النهاية (PJSIP يصدق INVITEs الواردة بناءً على عنوان IP المصدر)، و`outbound_auth` يوفر بيانات الاعتماد للمكالمات الصادرة والتسجيل.

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

للوصول إلى هذا الـ trunk، سنستخدم اسم القناة `PJSIP/siptrunk`. إعداد `dtmf_mode=rfc4733` ينقل DTMF خارج النطاق (RFC 4733 يلغي RFC 2833 القديم؛ الحمولة هي نفسها). خيار `identify`/`match` يقبل عناوين IP أو CIDR أو أسماء مضيفين، لكن أسماء المضيفين تُحل مرة واحدة عند تحميل الإعدادات، لذا لمزود يتغير عناوين IP الخاصة به يجب إدراج عناوين الإشارة صراحةً. أكد التسجيل باستخدام `pjsip show registrations`.

## مقدمة مخطط الاتصال

مخطط الاتصال يشبه قلب Asterisk. فهو يحدد كيفية معالجة Asterisk لكل مكالمة إلى الـ PBX. يتكون من امتدادات تشكل قائمة تعليمات يتبعها Asterisk. تُنفَّذ التعليمات بواسطة الأرقام التي يتلقاها القناة أو التطبيق. من أجل تكوين Asterisk بنجاح، من الضروري فهم مخطط الاتصال. معظم مخطط الاتصال موجود في ملف extensions.conf داخل دليل /etc/asterisk. يستخدم هذا الملف قواعد مجموعة بسيطة ويحتوي على أربعة مفاهيم رئيسية:

- Extensions
- Priorities
- Applications
- Contexts

لننشئ مخطط اتصال أساسي. في الأقسام اللاحقة من هذا الكتاب، سأخصص فصلاً بالكامل لمخطط الاتصال. إذا قمت بتثبيت الملفات النموذجية (make samples)، فإن ملف extensions.conf موجود بالفعل. احفظه باسم آخر وابدأ بملف فارغ.

## بنية ملف extensions.conf

ملف extensions.conf مقسّم إلى أقسام. الأول هو قسم [general] يليه قسم [globals]. يبدأ كل قسم بتعريف اسمه (مثال: [default]) وينتهي عندما يُنشأ قسم آخر.

### القسم [general]

القسم العام يقع في أعلى الملف. قبل البدء في تكوين مخطط الاتصال، من المفيد معرفة الخيارات العامة التي تتحكم في سلوكيات مخطط الاتصال. هذه الخيارات هي:

- static and write protect: إذا `static=yes` و `writeprotect=no`، يمكنك حفظ مخطط الاتصال الجاري إلى القرص بأمر CLI:

```
*CLI> dialplan save
```

تحذير: إذا نفّذت أمر `dialplan save` من CLI، ستفقد أي ملاحظات وتعليقات في الملف.

- autofallthrough: إذا تم ضبط autofallthrough، فإنّه عندما ينفد ما لدى الامتداد من أوامر، سيُنهي المكالمة بـ BUSY أو CONGESTION أو HANGUP حسب أفضل تخمين لـ Asterisk. هذا هو الإعداد الافتراضي. إذا لم يُضبط autofallthrough، فإنّ Asterisk سينتظر أن يُطلب رقم امتداد جديد عندما ينفد ما لدى الامتداد من أوامر.
- clearglobalvars: إذا تم ضبط clearglobalvars، سيتم مسح المتغيّرات العامة وإعادة تحليلها عند إعادة تحميل مخطط الاتصال أو إعادة تحميل Asterisk. إذا لم يُضبط clearglobalvars، ستستمر المتغيّرات العامة عبر عمليات إعادة التحميل وحتى إذا حُذفت من extensions.conf أو أحد ملفاته المضمّنة، ستظل مُعينة بالقيمة السابقة.
- extenpatternmatchnew: يستخدم خوارزمية مطابقة نمط أسرع، مما يساعد بشكل ملحوظ عندما يكون لديك عدد كبير من الامتدادات. القيمة الافتراضية هي لا.
- userscontext: هذا هو السياق الذي تُسجَّل فيه الإدخالات من users.conf.

### القسم [globals]

في قسم [globals] ستعرّف المتغيّرات العامة وقيمها الأولية. يمكنك الوصول إلى المتغيّر في مخطط الاتصال باستخدام ${GLOBAL(variable)}. يمكنك حتى الوصول إلى المتغيّرات المعرفة في بيئة linux/unix باستخدام ${ENV(variable)}. المتغيّرات العامة غير حساسة لحالة الأحرف. بعض الأمثلة قد تكون:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

في المثال التالي، يمكنك تعيين واختبار متغيّر عام في مخطط الاتصال.

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## السياقات

السياق هو الجزء المسمى من مخطط الاتصال. بعد قسمي [general] و [globals]، يكون مخطط الاتصال مجموعة من السياقات حيث يحتوي كل سياق على عدة امتدادات، كل امتداد له عدة أولويات، وكل أولوية تستدعي تطبيقًا مع عدة معطيات.

![تدفق مكالمات Asterisk: كل مكالمة تصل إلى قناة (IAX، SIP، وغيرها) كطرف مكالمة وارد؛ سياق القناة — المحدد عالميًا أو لكل قناة في ملف إعدادات القناة — يحدد أي سياق في extensions.conf يعالج المكالمة قبل أن تخرج على الطرف الصادر.](../images/04-first-pbx-fig03.png)

![معالجة المكالمة: الـ`context=`المعرف لقناة (في chan_dahdi.conf أو pjsip.conf) يحدد السياق المطابق في extensions.conf حيث يتعامل مخطط الاتصال مع المكالمة.](../images/04-first-pbx-fig04.png)

يمكنك بناء مخطط اتصال بسيط للوصول إلى هواتف أخرى و PSTN. ومع ذلك، Asterisk أقوى بكثير من ذلك. هدفنا هو تعليمك المزيد من التفاصيل حول ما يمكن تحقيقه في مخطط الاتصال.

## Extensions

على عكس نظام الـ PBX التقليدي، حيث ترتبط الامتدادات بالهواتف أو الواجهات أو القوائم، في Asterisk يُعَدُّ الامتداد قائمة من الأوامر التي تُعالج عندما يتم تشغيل رقم أو اسم امتداد معين. تُعالج الأوامر بترتيب الأولوية.

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. Extensions can be numeric, alphanumeric, numeric with caller ID, a pattern, or a standard extension like `s`; priorities can be a number, `n` (next), `s` (same), an offset, or a `hint`.](../images/04-first-pbx-fig05.png)

يمكن أن يكون الامتداد حرفيًا، أو قياسيًا، أو خاصًا. الامتداد القياسي يشتمل فقط على أرقام أو أسماء والحرفين * و #؛ 12#89* هو امتداد حرفي صالح. يمكن أيضًا استخدام الأسماء لمطابقة الامتداد. الامتدادات حساسة لحالة الأحرف. ومع ذلك، لا يمكنك إنشاء امتدادين بنفس الاسم ولكن بحالات مختلفة. عندما يتم طلب رقم امتداد، يُنفَّذ الأمر ذو الأولوية الأولى يليه الأمر ذو الأولوية 2 وهكذا. يستمر ذلك حتى يتم قطع المكالمة أو يُعيد أمر ما الرقم واحد، مما يدل على فشل. ما يفعله Asterisk عندما يُنفَّذ آخر أولوية يُحدَّد بواسطة المعامل autofallthrough. راجع قسم [general] في هذا الفصل. مثال:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

أعلاه تجد قائمة التعليمات التي تُعالج عندما يُطلب الامتداد 123. الأولوية الأولى هي الرد على القناة (ضروري عندما تكون القناة في حالة رنين: أي قنوات FXO). الأولوية الثانية هي تشغيل ملف صوتي يُدعى tt-weasels. الأولوية الثالثة تُغلق القناة. خيار آخر هو معالجة المكالمة وفقًا لهوية المتصل. يمكنك استخدام الحرف / لتحديد هوية المتصل التي ستُعالج. أمثلة:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

سيؤدي هذا المثال إلى تشغيل الامتداد 123 وتنفيذ الخيارات التالية فقط إذا كانت هوية المتصل 100. يمكن أيضًا القيام بذلك باستخدام النمط الموضح أدناه:

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: يربط امتدادًا بقناة. يُستخدم لمراقبة حالة القناة. يُستَخدم بالتزامن مع presence. يجب أن يدعم الهاتف ذلك.

#### Patterns

يمكنك استخدام الأنماط والحرفيات في dialplan. الأنماط مفيدة جدًا لتقليل حجم dialplan. جميع الأنماط تبدأ بالحرف “_”. يمكن استخدام الأحرف التالية لتعريف نمط. الشكل يحدد الأنماط المتاحة للاستخدام مع Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk يستخدم بعض أسماء الامتدادات كامتدادات قياسية.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

الوصف:

- **s**: Start. يُستخدم لمعالجة مكالمة عندما لا يكون هناك رقم مُطَلَب. وهو مفيد لأقسام FXO وفي معالجة القوائم.
- **t**: Timeout. يُستخدم عندما تظل المكالمات غير نشطة بعد تشغيل موجه. كما يُستخدم لإنهاء خط غير نشط.
- **T**: AbsoluteTimeout. إذا قمت بتحديد حد للمكالمات باستخدام دالة dialplan `TIMEOUT(absolute)`، بمجرد تجاوز المكالمة للحد المحدد، سيتم تحويلها إلى امتداد T.
- **h**: Hangup. يُستدعى بعد أن يقوم المستخدم بقطع المكالمة.
- **i**: Invalid. يُtrigger عندما تتصل بامتداد غير موجود في السياق. يمكن أن تؤثر هذه الامتدادات على محتوى سجلات CDR—وبشكل خاص،

## Variables

في نظام Asterisk PBX، يمكن أن تكون المتغيّرات عامة أو خاصة بالقناة أو خاصة بالبيئة. يمكنك استخدام التطبيق NoOP() لرؤية محتوى المتغيّر في وحدة التحكم. يمكنه استخدام متغيّر عام أو متغيّر خاص بالقناة كوسائط للتطبيق. يمكن الإشارة إلى المتغيّر كما في المثال التالي، حيث varname هو اسم المتغيّر.

```
${varname}
```

يمكن أن يكون اسم المتغيّر سلسلة أبجدية رقمية تبدأ بحرف. أسماء المتغيّرات العامة غير حساسة لحالة الأحرف. ومع ذلك، المتغيّرات النظامية (المعرفة من قبل Asterisk أو القناة) حساسة لحالة الأحرف. وبالتالي، المتغيّر ${EXTEN} يختلف عن ${exten}.

### Global variables

يمكن تكوين المتغيّرات العامة في القسم [global] في ملف extensions.conf أو باستخدام التطبيق:

```
set(Global(variable)=content)
```

### Channel-specific variables

يتم تكوين المتغيّرات الخاصة بالقناة باستخدام التطبيق set(). كل قناة تحصل على مساحة متغيّرات خاصة بها. لا توجد فرصة لتصادم المتغيّرات بين القنوات المختلفة. يتم تدمير المتغيّر الخاص بالقناة عندما تُنهى المكالمة. بعض المتغيّرات الأكثر شيوعًا هي:

- ${EXTEN} الرقم المُطلب
- ${CONTEXT} السياق الحالي
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} معرف المتصل الحالي
- ${PRIORITY} الأولوية الحالية

المتغيّرات الخاصة بالقناة الأخرى كلها بأحرف كبيرة. يمكنك رؤية محتوى عدة متغيّرات باستخدام التطبيق dumpchan(). أدناه مقتطف بسيط من متغيّرات dump-channel.

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

مخرجات Dumpchan:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

تنسيق الحقول أعلاه هو مخرجات Asterisk 22 `DumpChan` (اسم قناة حقيقي `PJSIP/...`، حقول `CallerIDNum`/`ConnectedLineID`، وصفوف `Raw*`/`Transcode`/`BridgeID` التي تُملأها قنوات PJSIP). على عكس السائق القديم، لا تقوم قناة PJSIP بتعيين تلقائي للمتغيّرات القنوية `SIPCALLID`/`SIPUSERAGENT`؛ يتم قراءة تفاصيل SIP المكافئة عند الطلب باستخدام دوال dialplan `PJSIP_HEADER()` و`CHANNEL()` — على سبيل المثال `${CHANNEL(pjsip,call-id)}`، `${PJSIP_HEADER(read,User-Agent)}`، و`${CHANNEL(rtp,dest)}` لعنوان RTP البعيد.

### Environment-specific variables

يمكن استخدام المتغيّرات الخاصة بالبيئة للوصول إلى المتغيّرات المعرفة في نظام التشغيل. يمكنك تعيين المتغيّرات الخاصة بالبيئة باستخدام الدالة ENV(). على سبيل المثال:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

بعض التطبيقات تستخدم المتغيّرات لإدخال البيانات وإخراجها. يمكنك تعيين المتغيّرات قبل استدعاء التطبيق أو استرجاع المتغيّر بعد تنفيذ التطبيق. على سبيل المثال: تطبيق Dial يُعيد المتغيّرات التالية:

- ${DIALEDTIME} -> هذا هو الوقت من طلب القناة حتى انقطاعها.
- ${ANSWEREDTIME} -> هذا هو مقدار الوقت للمكالمة الفعلية.
- ${DIALSTATUS} هذا هو حالة المكالمة: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE
- ${CAUSECODE} -> رسالة الخطأ للمكالمة.

## Expressions

Expressions can be very useful in the dial plan. They are used to manipulate strings and perform math and logical operations.

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

The expression syntax is defined as follows:

```
$[expression1 operator expression2]
```

Let’s suppose that we have a variable called “I” and we want to add 100 to the variable:

```
$[${I}+100]
```

When Asterisk finds an expression in the dial plan, it changes the entire expression by the resulting value.

### Operators

The following operators can be used to build expressions. It is important to observe operator precedence.

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

A regular expression is a special text string used to describe a search pattern. You can think of regular expressions as wildcards. Regular expressions are used to match a string to a pattern to check the matching. If the match succeeds and the regular expression contains at least one match, the first match is returned; otherwise, the result is the number of characters matched.

#### Comparison operators

The result of a comparison is 1 if the relation is true or 0 if it is false.

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

Put these expressions in your dial plan and use the NoOP() application to evaluate the expressions. Dial 9002 and examine the results in the Asterisk console. Use verbose 15 to show the results.

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Functions

Some applications have been replaced by functions, which allow the processing of variables in a more advanced way than expressions alone. You can see the full list of functions by issuing the following console command:

```
*CLI> core show functions
```

String length: ${LEN(string)} returns the string length

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

In the first operation, the system shows 5 as the result (the number of letters in the word “fruit”). The second returns the number 4 (the number of letters in the word “pear”). Substrings: Returns the substring, starting from the positing defined by the “offset” parameter, with the string length defined in the “length” parameter. If the offset is negative, it starts from right to left, beginning at the end of the string. If the length is omitted or negative, it takes the whole string starting with the offset.

```
${string:offset:length }
```

Example #1: Several substrings

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Example #2: Take the area code from the first three digits.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Example #3: Takes all digits from the variable ${EXTEN}, except for the area code.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### String concatenation

To concatenate two strings, simply write them together.

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## Applications

To build a dial plan, we need to understand the concept of applications. You will use applications to handle the channel in the dial plan. Applications are implemented in several modules. Available applications depend on modules. You can show all Asterisk applications using the console command:

```
*CLI> core show applications
```

بدلاً من ذلك، يمكنك عرض تفاصيل تطبيق معين باستخدام المثال التالي:

```
*CLI> core show application Dial
```

لبناء مخطط اتصال بسيط، تحتاج إلى معرفة بعض التطبيقات. سنناقش أمثلة أكثر تقدماً لاحقاً في الكتاب.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

سنستخدم هذه التطبيقات (أعلاه) لإنشاء مخطط اتصال بسيط لِـِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِِ)  

### Answer()

[Synopsis] Answers a channel if ringing [Description] Answer([delay]): إذا لم يتم الرد على المكالمة، سيقوم التطبيق بالرد عليها. وإلا، لن يكون له أي تأثير على المكالمة. إذا تم تحديد تأخير، سيُنتظر عدد المللي ثانية المحدد في ‘delay’ قبل الرد على المكالمة.

### Dial()

يمكن الحصول على الوصف التالي عن طريق تنفيذ الأمر `show application dial` في مخطط الاتصال. لتسهيل البحث، تم إعادة إنتاجه أدناه. كما يُظهر الصياغة لتطبيق Dial أدناه:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

هذا التطبيق سيجري مكالمات إلى قناة واحدة أو أكثر محددة. بمجرد أن يجيب أحد القنوات المطلوبة، سيتم الرد على القناة الأصلية — إذا لم يتم الرد عليها مسبقًا. ستصبح هاتان القناتان نشطتين في مكالمة موصولة. سيتم إنهاء جميع القنوات المطلوبة الأخرى. ما لم يتم تحديد مهلة، سيبقى تطبيق Dial ينتظر إلى ما لا نهاية حتى يجيب أحد القنوات التي تم الاتصال بها، أو يقطع المستخدم الاتصال، أو تكون جميع القنوات التي تم الاتصال بها مشغولة أو غير متاحة. سيستمر تنفيذ مخطط الاتصال إذا لم يمكن الاتصال بأي قناة مطلوبة أو إذا انتهت المهلة. يقوم هذا التطبيق بتعيين متغيرات القناة التالية عند الانتهاء:

- DIALEDTIME - هذا هو الوقت من بدء طلب الاتصال بقناة حتى وقت قطع الاتصال.
- ANSWEREDTIME - هذا هو مقدار الوقت للمكالمة الفعلية.
- DIALSTATUS - هذه هي حالة المكالمة: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

في وضعيات الخصوصية والفرز، سيتم تعيين المتغير DIALSTATUS إلى DONTCALL إذا اختار الطرف المتصل إرسال الطرف المتصل إلى برنامج النص 'Go Away'. سيتم تعيين المتغير DIALSTATUS إلى TORTURE إذا أراد الطرف المتصل إرسال المتصل إلى برنامج النص 'torture'. سيبلغ هذا التطبيق عن إنهاء طبيعي إذا قطعت القناة الأصلية الاتصال أو إذا تم ربط المكالمة وانتهى أحد الطرفين في الجسر المكالمة. سيتم إرسال عنوان URL الاختياري إلى الطرف المتصل إذا كانت القناة تدعمه. إذا تم تعيين المتغير OUTBOUND_GROUP، فستُضمَّن جميع القنوات النظيرة التي أنشأها هذا التطبيق في تلك المجموعة (كما في

```
Set(GROUP()=...).
```

The following table summarizes some of the most frequently used options for the application Dial. For the complete list, use the console command `core show application Dial`. In Asterisk 22 these options are separated from the channel and timeout by commas — for example `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | Plays an announcement to the called party, using `x` as the file. |
| `C` | Resets the CDR for this call. |
| `d` | Allows the calling user to dial a 1-digit extension while waiting for the call to be answered. Exits to that extension if it exists in the current context, or to the context defined in the `EXITCONTEXT` variable, if it exists. |
| `D([called][:calling])` | Sends the specified DTMF strings after the called party answers, but before the call is bridged. The `called` string is sent to the called party and the `calling` string to the calling party. Either parameter can be used alone. |
| `f` | Forces the caller ID of the calling channel to be set to the extension associated with the channel via a dial plan `hint`. Useful where the PSTN does not allow an arbitrary caller ID. |
| `g` | Proceeds with dial plan execution at the current extension if the destination channel hangs up. |
| `G(context^exten^pri)` | If the call is answered, transfers the calling party to the specified priority and the called party to priority+1. Optionally an extension (or extension and context) can be specified; otherwise the current extension is used. |
| `h` | Allows the called party to hang up by sending the `*` DTMF digit. |
| `H` | Allows the calling party to hang up by sending the `*` DTMF digit. |
| `L(x[:y][:z])` | Limits the call to `x` ms, plays a warning when `y` ms are left, and repeats the warning every `z` ms. See the `LIMIT_*` variables below. |
| `m([class])` | Provides music on hold to the calling party until the requested channel answers. A specific MusicOnHold class can be specified. |
| `r` | Indicates ringing to the calling party and passes no audio until the called channel answers. |
| `S(x)` | Hangs up the call `x` seconds after the called party answers. |
| `t` | Allows the called party to transfer the calling party by sending the DTMF sequence defined in `features.conf`. |
| `T` | Allows the calling party to transfer the called party by sending the DTMF sequence defined in `features.conf`. |
| `w` | Allows the called party to enable one-touch recording by sending the DTMF sequence defined in `features.conf`. |
| `W` | Allows the calling party to enable one-touch recording by sending the DTMF sequence defined in `features.conf`. |
| `k` | Allows the called party to park the call by sending the DTMF sequence defined for call parking in `features.conf`. |
| `K` | Allows the calling party to park the call by sending the DTMF sequence defined for call parking in `features.conf`. |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): plays sounds for the caller.
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: plays sounds for the called party.
- `LIMIT_TIMEOUT_FILE` — file to be played when time is up.
- `LIMIT_CONNECT_FILE` — file to be played when the call begins.
- `LIMIT_WARNING_FILE` — file to be played as a warning when `y` is defined. The default is to say the time remaining.

Example:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

في المثال أعلاه، سيقوم التطبيق بالاتصال بالقناة PJSIP المقابلة. يمكن لكل من المتصل والمتصل به نقل المكالمة (Tt). سيتم سماع الموسيقى أثناء الانتظار بدلاً من رنين الرجوع. إذا لم يجب أحد خلال 20 ثانية، ستنتقل الامتداد إلى الأولوية التالية.

### Hangup()

Hangs up the calling channel [Description] Hangup([causecode]): This application will hang up the calling channel. If a cause code is given, the channel's hang-up cause will be set to the given value.

### Goto()

Jump to a particular priority, extension, or context [Description] Goto([[context|]extension|]priority): This application will cause the calling channel to continue the dial plan execution at the specified priority. If no specific extension (or extension and context) are specified, this application will jump to the specified priority of the current extension. If the attempt to jump to another location in the dial plan is not successful, the channel will continue at the next priority of the current extension.

## بناء مخطط الاتصال

لبناء مخطط اتصال بسيط، تحتاج إلى معالجة جميع المكالمات الواردة والصادرة بإنشاء سياقات (contexts) وامتدادات (extensions). في هذا القسم، سنوضح لك كيفية بناء أكثر الامتدادات شيوعًا.

### الاتصال بين الامتدادات

لتمكين الاتصال بين الامتدادات، يمكننا استخدام المتغير القنوي ${EXTEN}، الذي يشير إلى الامتداد المطلوب. على سبيل المثال، إذا كان نطاق الامتدادات بين 4000 و 4999 وجميع الامتدادات تستخدم SIP، يمكننا اعتماد الأمر التالي:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### Dialing to an external destination

للاتصال بوجهة خارجية يمكنك وضع مسار قبل الرقم المطلوب طلبه. في أمريكا الشمالية، من الشائع استخدام 9 متبوعًا بالرقم الذي يُ dial خارجيًا. إذا كنت تستخدم قناة تماثلية أو رقمية إلى PSTN، يجب أن يبدو الأمر كما يلي: إذا كنت تريد استخدام SIP trunk بدلاً من DAHDI، استخدم القناة `PJSIP/...@siptrunk`.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

السطر أعلاه سيسمح لك بطلب الرقم 9 والرقم المطلوب. في المثال المذكور، ستستخدم القناة الأولى من DAHDI (DAHDI/1). إذا كان لديك عدة خطوط وكان هذا الخط مشغولاً، لن يتم إكمال المكالمة. ومع ذلك، يمكنك استخدام السطر التالي لاختيار أول قناة DAHDI متاحة تلقائيًا. بشكل اختياري، يمكنك استخدام خط SIP trunk بدلاً من DAHDI. في نموذج PJSIP `Dial(PJSIP/number@siptrunk,...)`، الرقم الذي تم طلبه هو جزء المستخدم و`siptrunk` هو نقطة النهاية التي تم تكوينها أعلاه.

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

معامل “g1” سيبحث عن أول قناة متاحة في المجموعة، مما يسمح باستخدام جميع القنوات. باستخدام السطر أدناه، يمكنك طلب رقم بعيد.

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### Dialing 9 to get a PSTN line

If you do not have any restrictions to external dialing, you could simplify and use the following:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### استقبال مكالمة في امتداد المشغل

في المثال التالي، امتداد المشغل هو 4000. خط الـ PSTN متصل بواجهة FXO. في ملف chan_dahdi.conf، السياق المحدد هو from-pstn. أي مكالمة قادمة من الـ PSTN سيتم توجيهها إلى السياق from-pstn في الـ dial plan. هذا الخط لا يحتوي على Direct Inward Dialing (DID)؛ لذلك سيتعين علينا استقبال المكالمة عبر امتداد “s”. إذا كان الاستقبال من الـ SIP trunk، استخدم السياق [from-sip].

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### استقبال مكالمة باستخدام الاتصال الداخلي المباشر (DID)

إذا كان لديك خط رقمي، ستستقبل الامتداد المطلوب. عندما يكون الأمر كذلك، لا تحتاج إلى تحويل المكالمة إلى المشغل؛ بل يمكنك تحويل المكالمة مباشرة إلى الوجهة. افترض أن نطاق DID الخاص بك هو من 3028550 إلى 3028599 وأن الأرقام الأربعة الأخيرة تُمرَّر في الـ DID. سيبدو التكوين كما في المثال التالي:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### تشغيل عدة امتدادات في وقت واحد

يمكنك ضبط Asterisk لطلب رقم امتداد، وإذا لم يُجب، لطلب عدة امتدادات أخرى في وقت واحد، كما هو موضح في المثال التالي:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

في هذا المثال، عندما يطلب أحدهم المشغل، يتم تجربة القناة DAHDI/1 أولاً. إذا لم يرد أحد بعد 15 ثانية (مهلة)، سترن القنوات DAHDI/1 و DAHDI/2 و DAHDI/3 في آن واحد لمدة 15 ثانية أخرى.

### التوجيه حسب هوية المتصل

في هذا المثال، يمكنك تقديم معالجات مختلفة بناءً على هوية المتصل، مما قد يكون مفيدًا لمكافحة المتصلين المزعجين. على سبيل المثال:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

في هذا المثال، أضفنا قاعدة خاصة تفيد بأنه إذا كان معرف المتصل هو 4832518888، يتم تشغيل رسالة من الملف المسجل مسبقًا “I-have-moved-to-china”. تُقبل المكالمات الأخرى كالمعتاد.

### استخدام المتغيّرات في الـ dial plan

يمكن لـ Asterisk استخدام المتغيّرات العامة ومتغيّرات القناة في الـ dial plan كوسائط لتطبيقات معينة. انظر إلى الأمثلة التالية:

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

استخدام المتغيّرات يجعل التغييرات المستقبلية أسهل. إذا قمت بتغيير المتغيّر، يتم تعديل جميع الإشارات إليه فورًا.

### تسجيل إعلان

في بعض الخيارات التي ستُناقش لاحقًا في هذا القسم، سنستخدم تنبيهات مسجلة. هنا نُظهر لك طريقة سهلة لتسجيلها. سنستخدم التطبيق `Record()` لحفظ الإعلان باستخدام هاتفك الخاص.

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

هذه التعليمات تسمح لك بتسجيل أي رسالة من softphone. مثال: طلب رقم recordmenu من الـ softphone ستستدعي التعليمات التسجيل بالمتغيّر ${EXTEN:6} بدون الأحرف الستة الأولى. بعبارة أخرى، التعليمات تعادل record(menu:gsm). كل ما عليك هو طلب رقم record + اسم_الملف_الذي_يجب_تسجيله، اضغط # لإنهاء التسجيل، وانتظر لسماع التسجيل.

### استقبال المكالمات في موظف استقبال رقمي

الآن بعد أن لدينا بعض الأمثلة البسيطة، دعنا نوسّع معرفتنا حول تطبيقات background() و goto(). المفتاح للأنظمة التفاعلية في Asterisk هو تطبيق background()، الذي يتيح لك تشغيل ملف صوتي، وعند ضغط المتصل على مفتاح يتم مقاطعة التشغيل لإرسال المكالمة إلى الامتداد المطلوب. صيغة تطبيق background():

```
exten=>extension, priority, background(filename)
```

تطبيق آخر مفيد جدًا هو goto(). كما يشير الاسم، فإنه ينتقل إلى السياق والامتداد والأولوية المحددة. صيغة التطبيق goto():

```
exten=>extension, priority,goto(context, extension, priority)
```

الصيغ الصالحة لأمر goto():

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

في المثال التالي، سنقوم بإنشاء موظف استقبال رقمي. من السهل جدًا تعديل ملف extensions.conf وتكوين الامتدادات التالية:

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

ملحقات SIP تستخدم `PJSIP/` وملحقات IAX تستخدم `IAX2/` — كلا السائقين موجودان في Asterisk 22، رغم أن `chan_iax2` يعتبر الآن قديمًا ويفضل استخدام SIP/PJSIP.

في الملف menu1.gsm، سجِّل الرسالة “press the extension or wait for the operator”. عندما يطلب المستخدم الرقم 6000، سيتم إرساله إلى الملحق 6000. في هذه المرحلة، يجب أن يكون لديك فهم واضح لاستخدام عدة تطبيقات، بما في ذلك answer()، background()، goto()، hangup()، وplayback(). إذا لم يكن لديك فهم واضح، يرجى قراءة هذا الفصل مرة أخرى حتى تشعر بالراحة مع المحتوى. ستستخدم تطبيق background كثيرًا. بمجرد أن تفهم أساسيات الملحقات، الأولويات، والتطبيقات، سيكون من السهل إنشاء مخطط اتصال بسيط. سيتم استكشاف هذه المفاهيم بعمق أكبر لاحقًا في الكتاب، وسترى أن مخطط الاتصال سيصبح أكثر قوة.

## الملخص

في هذا الفصل، تعلمت أن ملفات التكوين تُخزن في الدليل **/etc/asterisk**. لاستخدام Asterisk، يجب أولاً تكوين القنوات (مثل pjsip، dahdi، iax). هناك ثلاثة صيغ مختلفة لملفات التكوين: مجموعة بسيطة، وراثة كائن، وكيان معقد. يتم إنشاء مخطط الاتصال في الملف **extensions.conf** وهو مجموعة من السياقات والامتدادات. في مخطط الاتصال، كل امتداد يُشغِّل تطبيقًا. تعلمت استخدام تطبيقات **playback**، **background**، **dial**، **goto**، **hangup**، و**answer**.

## Quiz

1. ملفات تكوين القنوات هي (اختر كل ما ينطبق):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. في Asterisk 22، تم استبدال الـ `chan_sip` الـ peer الواحد `[6001]` (`type=friend`/`host=dynamic`) في `pjsip.conf` بأي مجموعة من الكائنات المرتبطة؟
   - A. `type=peer` و `type=user`
   - B. `type=endpoint`، `type=auth`، و `type=aor`
   - C. `type=friend` واحد
   - D. `type=transport` و `type=global`
3. تعريف context في ملف تكوين القناة مهم لأنه يحدد context الوارد للمكالمات من تلك القناة — تُعالج المكالمة من القناة في الـ context المطابق في `extensions.conf`.
   - A. True
   - B. False
4. الاختلافات الرئيسية بين تطبيقات `Playback()` و `Background()` هي (اختر اثنين):
   - A. Playback يشغل تنبيهًا لكنه لا ينتظر الأرقام.
   - B. Background يشغل تنبيهًا لكنه لا ينتظر الأرقام.
   - C. Background يشغل رسالة وينتظر ضغط الأرقام.
   - D. Playback يشغل رسالة وينتظر ضغط الأرقام.
5. عندما تدخل مكالمة إلى Asterisk عبر بطاقة واجهة هاتفية (FXO) بدون DID، يتم التعامل معها في الامتداد الخاص:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. الصيغ الصالحة لتطبيق `Goto()` هي (اختر ثلاثة):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. النمط `_7[1-5]XX` يطابق (اختر كل ما ينطبق):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. في `Dial(PJSIP/${EXTEN},20,tTm)`، ماذا يفعل خيار `m`؟
   - A. يحد من مدة المكالمة إلى أقصى حد.
   - B. يوفر موسيقى انتظار للمتصل بدلاً من نغمة الرنين حتى يجيب القناة.
   - C. يرسل أرقام DTMF بعد أن يجيب الطرف المتصل.
   - D. يفرض معرف المتصل باستخدام تلميح مخطط الاتصال.
9. في قواعد وراثة الخيارات المستخدمة بواسطة `chan_dahdi.conf`، أنت:
   - A. تعرف الكائن في سطر واحد.
   - B. تعرف الخيارات أولاً وتعلن عن الكائنات تحت الخيارات المعرفة.
   - C. تعرف سياقًا منفصلًا لكل كائن.
10. يجب أن تكون الأولويات في الامتداد مرقمة بشكل متتابع (1, 2, 3, …) ولا يمكن استخدام `n`.
    - A. True
    - B. False

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
