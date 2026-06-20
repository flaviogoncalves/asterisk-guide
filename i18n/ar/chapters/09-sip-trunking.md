# SIP trunking, DID & the PSTN

PBX لا يمكنه إلا أن يتصل بنفسه ليس مفيدًا كثيرًا. عاجلاً أم آجلاً يجب على كل نظام أن يصل إلى بقية العالم — شبكة الهاتف العامة (PSTN)، مزود SIP، أو PBX آخر. الرابط الذي يحمل تلك المكالمات هو **trunk**. في عصر TDM كان الـ trunk دائرة فعلية: T1/E1 PRI أو مجموعة من خطوط FXO التناظرية. اليوم هو تقريبًا دائمًا **SIP trunk** — اتصال منطقي بمزود خدمة الهاتف عبر الإنترنت (ITSP) يُنقل عبر نفس شبكة IP التي تُنقل عليها كل الأشياء الأخرى.

يُظهر هذا الفصل كيفية ربط Asterisk 22 بـ ITSP باستخدام PJSIP، وكيفية الاختيار بين trunk يعتمد على التسجيل وآخر يعتمد على IP، وكيفية توجيه أرقام DID الواردة إلى الوجهة الصحيحة، وكيفية إرسال المكالمات الصادرة بمعرف المتصل الصحيح وتنسيق E.164، وكيفية بناء التبديل التلقائي وتوجيه أقل تكلفة عبر عدة trunks. ننتهي بمعالجة NAT للـ trunks ومختبر يُنشئ Asterisk ثاني (وSIPp) كمزود ITSP تجريبي حتى تتمكن من إجراء مكالمات حقيقية عبر trunk.

كل ما هنا تم التحقق منه مقابل مختبر Asterisk 22.10.0 في الكتاب؛ نمط كائن الـ trunk هو نفسه الذي عُرض في *Building your first PBX with PJSIP* و*SIP & PJSIP in depth*.

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk 22 to an ITSP with PJSIP
- Choose between registration-based and IP-based (static) trunks
- Route inbound DIDs to the right extension, IVR or queue
- Route outbound calls with correct caller-ID and E.164 formatting
- Build trunk failover and least-cost routing with `${DIALSTATUS}`
- Handle NAT for trunks on the transport and the endpoint

## ما هو خط SIP

خط SIP هو مسار صوتي منطقي بين PBX الخاص بك ونظام SIP آخر. في
الممارسة، ذلك "النظام الآخر" هو أحد أمرين:

- **مقدم خدمة الاتصالات عبر الإنترنت (ITSP).** ناقل تجاري ي
  يبيع لك بدء وإنهاء المكالمات، وعادةً، مجموعة من أرقام الهواتف
  (DIDs). تقوم بتوجيه Asterisk إلى مضيف الإشارة الخاص بالمزود، و
  يقوم المزود بربط مكالماتك بالشبكة العامة PSTN. هذه هي الطريقة التي
  تصل بها معظم الأنظمة الحديثة إلى شبكة الهاتف — دون الحاجة إلى
  أجهزة هاتفية.
- **بوابة PSTN.** جهاز (أو Asterisk آخر) يحتوي على واجهات PSTN
  مادية — بطاقة PRI، منافذ FXO تماثلية، أو بوابة GSM/4G — ويقدمها
  إلى PBX الخاص بك كـ SIP. تقوم البوابة بتحويل TDM إلى SIP؛ من
  وجهة نظر Asterisk هي مجرد خط SIP آخر.

في كلتا الحالتين، في PJSIP يُعتبر الخط **مجرد نقطة نهاية**. نفس عائلة الكائنات التي
استخدمتها لهاتف — `endpoint`، `auth`، `aor`، اختياريًا `identify` و
`registration` — تُنشئ خطًا. الاختلافات تكمن في التفاصيل: الخط
يُوثق *الصادر* (أنت العميل، لذا تُوضع الاعتمادات في
`outbound_auth`، وليس `auth`)، عادةً لا يسجل وكيل مستخدم لك
(أنت تسجل إلى *هو*، أو يرسل لك حركة مرور من IP معروف)، ويُوجه
المكالمات الواردة إلى سياق مخصص مثل `from-pstn` بدلاً من
`from-internal`.

> **مقارنةً بالخط TDM القديم.** كان PRI يمنحك عددًا ثابتًا من القنوات B
> (23 على T1، 30 على E1) ويشير إلى إعداد المكالمة عبر قناة D مخصصة
> (انظر فصل *القنوات القديمة*). لا يحتوي خط SIP على عدد قنوات ثابت —
> السعة هي ما تسمح به عرض النطاق الترددي الخاص بك، سياسة المزود، وأي
> حدود `max_contacts`/المكالمات المتزامنة. معرف المتصل، DID، وتقدم المكالمة
> الذي كان يُنقل عبر عناصر معلومات ISDN الآن يُنقل عبر رؤوس SIP وSDP.

هناك طريقتان يوافق فيهما ITSP على تبادل الحركة معك، وتحددان
كيفية بناء الخط: **معتمد على التسجيل** و**معتمد على IP
(ثابت)**. سنغطي كل منهما على حدة.

## Registration-based trunks

نموذج trunk القائم على التسجيل هو النموذج المستخدم عندما يتوقع المزود أن *تقوم* أنت
بتسجيل الدخول إلى *هم*. يرسل Asterisk الخاص بك بشكل دوري طلب SIP `REGISTER` إلى
المزود، مع المصادقة باستخدام اسم مستخدم وكلمة مرور، تمامًا كما يسجل الهاتف إلى
PBX الخاص بك. هذا شائع عندما يكون عنوان IP العام لديك ديناميكيًا، أو عندما تكون
خلف NAT، أو عندما يحدد المزود العملاء ببساطة عبر بيانات اعتماد SIP
بدلاً من عنوان IP.

في PJSIP، تسجيل الخروج الخارجي موجود في كائن `registration` مخصص. وهو
يستبدل السطر الوحيد `register =>` الذي كان يستخدمه برنامج تشغيل `chan_sip` المُزال في
`sip.conf`. إليك trunk تسجيل كامل لمزود خيالي،
متبعًا النمط المُتحقق منه من الفصول السابقة — لاحظ `outbound_auth`
(ليس `auth`)، `server_uri`/`client_uri` (ليس `server`/`client`)،
`from_user`/`from_domain` على الطرف النهائي، و`dtmf_mode=rfc4733`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

بعض الأمور التي يجب ملاحظتها:

- **`auth_type=digest`، وليس `userpass`.** كلاهما ينتج نفس مصادقة الـ digest،
  لكن في Asterisk 22 `userpass` (والـ `md5` القديم) **مُهملان ويتم تحويلهما بصمت إلى `digest`**. يفضَّل استخدام `digest` في التكوين الجديد؛ ستظل ترى `userpass` في الملفات القديمة وفي الفصول السابقة من هذا الكتاب.
- **`outbound_auth` على كل من الطرف النهائي والتسجيل.** يستخدم التسجيل
  ذلك لمصادقة `REGISTER`؛ يستخدم الطرف النهائي ذلك للرد على
  `407 Proxy Authentication Required` التي يرسلها المزود إلى طلب خارجي
  `INVITE`. يمكنهما مشاركة كائن `auth` واحد.
- **`from_user` / `from_domain`.** العديد من المزودين يرفضون المكالمات التي لا يحمل فيها رأس `From`
  رقم حسابك ونطاقهم. هذان الخياران يحددان ذلك بالضبط.
- **`contact_user=4830001000`.** يصبح هذا هو الجزء المتعلق بالمستخدم من `Contact` الذي
  تسجِّل به، بحيث يعرف المزود أي رقم يُسلم المكالمات الواردة إليه. إنه
  المكافئ الحديث لللاحقة `/9999` على السطر القديم `register =>`.
- **`retry_interval=60`.** إذا فشل التسجيل، أعد المحاولة كل 60 ثانية.

بعد إعادة التحميل، أكد التسجيل باستخدام `pjsip show registrations`. في
المختبر — حيث لا يجيب `itsp.example.com` فعليًا — يبدو الجدول هكذا:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

اللاحقة `(exp. Ns)` تُظهر العد التنازلي بالثواني حتى المحاولة التالية؛ بمجرد
أن تصل إلى الصفر تُظهر مؤقتًا `(exp. Ns ago)` قبل أن تُطلق إعادة المحاولة. مقابل مزود
حقيقي، عمود `Status` يُظهر `Registered` مع الثواني المتبقية
حتى التحديث التالي. `Rejected` (أو `Unregistered`) يعني أن المزود لم
يقبل تسجيل الدخول — فعّل `pjsip set logger on` واقرأ رد `401`/`403`،
غالبًا ما يكون اسم مستخدم أو كلمة مرور خاطئة، أو نطاق `client_uri` غير صحيح.

## IP-based (static) trunks

النموذج الثاني لا يحتاج إلى تسجيل على الإطلاق. يعرف المزود عنوان الـ IP العام الخاص بك ويرسل المكالمات مباشرةً إليه؛ وأنت بدورك ترسل المكالمات إلى عنوان الـ IP الخاص بالإشارة المعروف للمزود. المصادقة تكون عبر **عنوان IP المصدر**، وليس عبر بيانات اعتماد SIP. هذا نمط شائع للخطوط بين خادمين تتحكم فيهما، أو لخط مؤسسي حيث يكون لدى الطرفين عناوين ثابتة.

الكائن الرئيسي هو `identify`. إنه يخبر Asterisk: "أي طلب SIP يأتي من *هذا* الـ IP ينتمي إلى *ذلك* الطرف." بدون ذلك، يحاول PJSIP مطابقة طلب وارد إلى طرف عبر مستخدم `From`، وهو ما لن يفي به مرور الناقل — لذا سيتم رفض المكالمة أو سقط إلى الطرف `anonymous`.

الخط الثابت يلغي كائن `registration` ويضيف `identify`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` يقبل عنوان IP، نطاق CIDR، أو اسم مضيف. **يتم حل أسماء المضيف مرة واحدة، عند تحميل التكوين**، لذا إذا تغير IP المزود عليك إعادة التحميل. بالنسبة للناقل الذي ينشر عدة بوابات وسائط، قم بإدراج كل عنوان IP للإشارة — يمكنك تكرار `match` أو إعطاء CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

تحقق مما سيقبله Asterisk باستخدام `pjsip show identifies`. مأخوذ من المختبر (السطر `sipp-identify` هو الطرف SIPp الموجود مسبقًا في المختبر):

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### The security implication

خط قائم على IP بدون مصادقة هو باب، و`identify`/`match` هو القفل الوحيد عليه. إذا قمت بـ`match` نطاقًا واسعًا جدًا — أو إذا استطاع المهاجم انتحال عنوان IP المصدر — ستصل المكالمات إلى سياق `from-pstn` غير مصدق. دفاعان، يُستخدمان معًا:

- **طابق بأضيق ما يمكن.** فضل عناوين IP المضيف المحددة على نطاقات CIDR الواسعة. فقط عناوين IP للإشارة الحقيقية للمزود تنتمي إلى `match`.
- **اقترنها مع ACL.** يمكن لـ PJSIP إسقاط الحركة على طبقة SIP قبل أن تصل إلى أي طرف، باستخدام كائن `type=acl` (أو `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

قسم `type=acl` لا يحتاج إلى إشارة: `res_pjsip_acl` يطبق كل كائن من هذا النوع على *جميع* حركة SIP الواردة قبل أن تصل إلى أي طرف. (خياري `acl` و`contact_acl` على الكائن يسحبان قوائم القواعد المسماة من `acl.conf` بدلاً من إدراج `permit`/`deny` مباشرةً كما هو موضح أعلاه.) المبدأ هو نفسه من فصل SIP: رفض كل شيء، ثم السماح فقط بما تثق به. وأيًا كان سياق الخط الخاص بك،
**لا تدعه يصل إلى سياق يمكنه الاتصال مرة أخرى إلى PSTN** دون قاعدة مصدقة ومتعمدة — فهذا هو الثغرة الكلاسيكية للاحتيال على الرسوم.

> **Which model should I use?** إذا كان المزود يزودك باسم مستخدم وكلمة مرور،
> استخدم خط **تسجيل**. إذا طلب عنوان IP الخاص بك وأعطاك عنوانه، استخدم خط **identify**. بعض المزودين يدعمون كلا الخيارين؛ العديد من الخطوط الحقيقية تجمع بين تسجيل (حتى يتمكن المزود من العثور عليك) وidentify (حتى يتم مطابقة INVITEs الواردة من بوابات وسائط المزود حتى عندما تأتي من IP غير مسجل).

## توجيه المكالمات الواردة ومعالجة الـ DID

عند وصول المكالمات الواردة، يتم توجيهها إلى `context` الخاص بالنقطة الطرفية — هنا
`from-pstn`. الـ **DID** (رقم الاتصال الداخلي المباشر) هو ببساطة الرقم الذي يطلبه
المزود لك في URI الطلب. مهمتك في مخطط الاتصال هي ربط كل
DID بوجهة: امتداد واحد، IVR، طابور انتظار، أو مجموعة رنين.

الرقم الذي يرسله المزود يُطابق كـ `${EXTEN}` في `from-pstn`. مقدار ما تراه يعتمد على المزود —
بعضهم يرسل الرقم الكامل وفقًا لـ E.164 (`+4830001000`)، وبعضهم يرسل الرقم الوطني،
وبعضهم يرسل فقط آخر عدة أرقام. افحص مكالمة واردة حقيقية باستخدام `pjsip set logger on` وانظر إلى
URI الطلب قبل كتابة الأنماط.

### DID واحد إلى امتداد واحد

أبسط حالة — DID واحد يُوجه مباشرة إلى هاتف:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### DID واحد إلى IVR (مستقبل تلقائي)

رقم رئيسي يجب أن يرد بقائمة بدلاً من رنين هاتف:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` هو سياق المستقبل التلقائي الذي أنشأته في فصول مخطط الاتصال
(`Background()` + `WaitExten()`). توجيه الـ DID هو مجرد `Goto`.

### DID واحد إلى طابور انتظار

خط دعم يجب أن يوجه إلى طابور مكالمات:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### عدة DIDs في آن واحد

عند شراء مجموعة من الأرقام، يحافظ نمط واحد على صغر مخطط الاتصال. افترض أن
نطاق الـ DID الخاص بك هو `4830003000`–`4830003099` وأن المزود يرسل الرقم الكامل؛ قم بربط
آخر رقمين من كل DID بالامتداد `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` يأخذ آخر رقمين (الإزاحة السلبية تُحسب من اليمين)، لذا فإن `4830003007` يرن
`PJSIP/6007`. جدول بحث `did => extension` مبني باستخدام
`GoSub` أو قاعدة بيانات Asterisk (`AstDB`/`func_odbc`) يمكنه التوسع أكثر، لكن لعدد
قليل من الأرقام تكون الأنماط الصريحة هي الأكثر وضوحًا.

> **التقاط الـ DID غير المتطابق.** أضف امتداد `i` (غير صالح) إلى `from-pstn` بحيث
> عندما يُوجه رقم وارد بشكل غير صحيح يتم تشغيل إعلان أو رنين المشغل بدلاً من
> الانقطاع الصامت:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## التوجيه الصادر، معرف المتصل ومعيار E.164

تتدفق المكالمات الصادرة في الاتجاه المعاكس: يطلب هاتف داخلي رقمًا، يطابقه مخطط الاتصال الخاص بك، يزيل أي بادئة وصول، يضبط معرف المتصل كما يتوقع المزود، ويسلم المكالمة إلى نقطة النهاية للخط مع `Dial(PJSIP/<number>@itsp)`.

### إرسال المكالمة إلى الخط

صيغة القناة للخط هي `PJSIP/<number>@<endpoint>`: الجزء قبل `@` يصبح الجزء المتعلق بالمستخدم في URI الطلب الصادر، والجزء بعد `@` يحدد نقطة النهاية التي يوفر `aor` `contact` المضيف الوجهة. قاعدة كلاسيكية "اتصل بالرقم 9 للحصول على خط خارجي":

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` يزيل رمز الوصول `9` الأول قبل إرسال الرقم. النمط `_9NXXXXXXXXX` يطابق `9` بالإضافة إلى رقم مكوّن من 10 أرقام يبدأ أولها بالرقم 2–9؛ عدّل ذلك وفق مخطط الاتصال الخاص بك.

### معرف المتصل في المكالمات الصادرة

معظم مزودي خدمة الإنترنت (ITSPs) يتجاهلون — أو يرفضون بنشاط — معرف المتصل الذي ليس رقمًا تملكه. اضبط رقم معرف المتصل الصادر إلى أحد أرقام الـ DID الخاصة بك باستخدام الدالة `CALLERID(num)` قبل `Dial()`، كما هو موضح أعلاه. يمكنك أيضًا ضبط الاسم:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

إذا استمر المزود في إزالة أو استبدال اسم معرف المتصل الخاص بك، فهذه سياساته — العديد من الناقلين يحصلون على الاسم المعروض من قاعدة بيانات CNAM الخاصة بهم المرتبطة بالرقم، وليس من رأس `From` الخاص بك.

خياران لنقطة النهاية يتفاعلان مع ذلك:

- **`from_user`** يضبط الجزء المتعلق بالمستخدم في رأس `From` على مستوى SIP، والذي يستخدمه بعض المزودين لتحديد حسابك بغض النظر عن `CALLERID(num)`.
- **`trust_id_outbound`** (الافتراضي `no`) يتحكم فيما إذا كان Asterisk سيرسل رؤوس هوية حساسة للخصوصية (`P-Asserted-Identity`/`P-Preferred-Identity`) صادرة. اتركه معطلاً ما لم يذكر مزودك في وثائقه أنه يريد PAI، وفي هذه الحالة اضبط `trust_id_outbound=yes` و`send_pai=yes`.

### التطبيع إلى معيار E.164

E.164 هو تنسيق الرقم الدولي: علامة «+» أولية `+`، رمز الدولة، ثم الرقم الوطني، دون مسافات أو علامات ترقيم (مثال `+5548999990000` أو `+14155550100`). يتوقع الناقلون بشكل متزايد — أو يطلبون — E.164 على الخط. بدلاً من توزيع تنسيق الأرقام عبر مخطط الاتصال، قم بالتطبيع مرة واحدة في السياق الصادر.

مثال من أمريكا الشمالية يقبل رقمًا محليًا مكوّنًا من 10 أرقام، أو رقمًا مكوّنًا من 11 رقمًا يبدأ بـ `1`، أو رقمًا بالفعل بصيغة E.164، ويقدم دائمًا `+1…` إلى الخط:

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

بعض المزودين يريدون `+`؛ وآخرون يفضلون الأرقام الصافية. إذا كان مزودك يرفض `+`، قم بإزالتها عند الخروج باستخدام `${EXTEN:1}` في `Dial`. الفكرة هي أن كل معرفة التنسيق موجودة في مكان واحد، لذا فإن تغيير المزود — أو إضافة مزود ثانٍ — يصبح تعديلًا سطرًا واحدًا فقط.

## الفشل التلقائي وتوجيه أقل تكلفة

مع وجود خط واحد فقط، يعني انقطاع المزود عدم وجود مكالمات صادرة. مع وجود خطين أو أكثر، يمكنك
التبديل تلقائيًا وحتى اختيار أرخص مسار لكل وجهة —
*توجيه أقل تكلفة* (LCR).

### الفشل التلقائي باستخدام `${DIALSTATUS}`

`Dial()` يضبط المتغيّر القنوي `${DIALSTATUS}` عند عودته. القيم التي تهمك للفشل التلقائي هي `CHANUNAVAIL` (لم يتم الوصول إلى الخط مطلقًا)
و`CONGESTION` (تم رفض المكالمة، مثلًا جميع الدوائر مشغولة). جرّب الخط الأساسي؛ إذا لم يتمكن من نقل المكالمة، انتقل إلى الخط الاحتياطي:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

لاحظ الاختيار المتعمد **عدم** الفشل التلقائي عند `BUSY` أو `NOANSWER` — فهذه تعني أن *الطرف المتصل* تم الوصول إليه ورفض، لذا فإن إعادة المحاولة على خط آخر سيعيد رنين هاتف قد قال لا بالفعل (وقد يكلفك مكالمة ثانية).
أعد التوجيه فقط عندما يفشل *الخط نفسه*.

### روتين فرعي لإعادة الاستخدام في التوجيه

تكرار هذا المنطق لكل نمط طلب مكالمة عرضة للخطأ. قم بتجميعه في روتين `GoSub` يأخذ رقم الوجهة ويحاول كل خط بالترتيب:

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

الآن كل نمط صادر هو مكالمة `GoSub` واحدة، ويتم تعريف ترتيب الخطوط في
مكان واحد فقط.

### توجيه أقل تكلفة حسب الوجهة

اختيار LCR الحقيقي يحدد الخط بناءً على وجهة المكالمة. الشكل الشائع هو مطابقة
بادئة الوجهة وإرسال كل فئة من المكالمات إلى المزود الذي يكون
أرخص لها — على سبيل المثال، المكالمات الدولية إلى مزود جملة الجملة
والمكالمات المحلية/الوطنية إلى الخط الأساسي الخاص بك:

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

لأكثر من بضع بادئات، احفظ جدول التوجيه في قاعدة بيانات
(`func_odbc`/`AstDB`) وابحث عن الخط حسب البادئة بدلاً من ترميز الأنماط يدويًا.
يبقى مخطط الطلب صغيرًا وتعيش الأسعار في جدول يمكنك تحريره
دون الحاجة إلى إعادة تحميل المنطق.

## NAT and trunks

NAT هو السبب الأكثر شيوعًا لمشكلات الخطوط — عادةً صوت أحادي الاتجاه،
أو خط يُسجِّل لكنه لا يتلقى مكالمات واردة. السبب هو نفسه
كما هو الحال مع الهواتف (المغطى في *SIP & PJSIP in depth* و*Designing a VoIP network*):
Asterisk يعلن عن عنوانه الخاص في SIP وSDP، وخلف NAT
هذا عنوان RFC 1918 خاص لا يستطيع المزود توجيه الحركة إليه.

بالنسبة للخطوط، الإصلاح يتكون من جزأين — إعدادات على **النقل** (عنوانك العام)
وإعدادات على **نقطة النهاية** (كيفية التعامل مع وسائط المزود).

### On the transport — your public address

عندما يكون خادم Asterisk نفسه خلف NAT (سحابة أو جهاز محلي بعنوان
IP خاص وعنوان IP عام 1:1)، أخبر النقل بعنوانه العام وأي
شبكات هي محلية. تُضبط هذه الخيارات مرة واحدة، على `transport`، وتطبق على
جميع الحركة عبره:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — عنوان IP العام الذي يكتبه Asterisk في رؤوس SIP
  (`Via`، `Contact`) للوجهات خارج `local_net`.
- **`external_media_address`** — عنوان IP العام الذي يكتبه Asterisk في سطر SDP `c=`
  بحيث يعود RTP إلى المكان الصحيح. عادةً يكون مطابقًا لعنوان الإشارة.
- **`local_net`** — الشبكات التي يعتبرها Asterisk داخلية، لذا لا يعيد
  كتابة العناوين لأقران LAN. قوّم كل شبكة فرعية داخلية.

### On the endpoint — the provider's media

النصف الآخر يتعامل مع مزود يجلس خلف NAT، أو يرسل
الوسائط من عنوان غير ذلك الموجود في SDP الخاص به. اضبط هذه لكل نقطة نهاية للخط:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — حافظ على تدفق الوسائط عبر Asterisk بدلاً من السماح
  للقدمين بالتواصل مباشرة. أمر أساسي عبر NAT، ومطلوب أيضًا إذا أردت
  تسجيل أو تحويل أو مراقبة المكالمة.
- **`rtp_symmetric=yes`** — سلوك *comedia* الكلاسيكي: أرسل RTP إلى
  العنوان الذي جاءت منه الوسائط فعليًا، وليس العنوان الذي يدعيه SDP.
- **`force_rport=yes`** — الرد على SIP من عنوان IP/منفذ المصدر للطلب
  (RFC 3581)، بدلاً من الثقة في رأس `Via`.
- **`rewrite_contact=yes`** — عند رسائل SIP الواردة من هذه النقطة النهاية، أعد كتابة
  رأس `Contact` (أو رأس `Record-Route` المناسب) إلى عنوان IP
  المصدر والمنفذ الذي جاء منه الحزمة فعليًا. وفقًا لتوثيق الخيار نفسه،
  هذا "يساعد الخوادم على التواصل مع نقاط النهاية التي تقع خلف
  NATs" و"يساعد على إعادة استخدام اتصالات النقل الموثوقة مثل TCP وTLS."

> **Recommendation — phones vs trunks.** `rewrite_contact` هو تقريبًا دائمًا
> الخيار الصحيح للهواتف، لأن جهة الاتصال المعلنة عادةً ما تكون عنوانًا خاصًا
> RFC 1918 غير قابل للتوجيه إليهم. في خط ثابت يعتمد على IP
> تكون جهة اتصال المزود عادةً عنوانًا عامًا صحيحًا بالفعل، لذا قد لا يكون
> إعادة الكتابة ضرورية؛ بعض المشغلين يفضلون تركها معطلة هناك وتمكينها
> فقط لخطوط التسجيل والهواتف التي عبر NAT. التأثير الموثق للخيار هو فقط
> إعادة كتابة `Contact`/`Record-Route` الواردة أعلاه — لذا
> الممارسة الآمنة هي اختبارها مع مزودك المحدد قبل تفعيلها على
> خط ثابت.

يمكنك التأكد من الإعدادات الفعّالة على أي نقطة نهاية باستخدام
`pjsip show endpoint <name>` — `direct_media`، `rtp_symmetric`، `force_rport`،
`rewrite_contact`، والبقية كلها تُطبع في تفريغ المعاملات.

## مختبر — مزوّد خدمة إنترنت افتراضي (ITSP) تجريبي مع أستركس ثاني وSIPp

أنت لا تحتاج إلى خط مدفوع للتدريب. المختبر في الكتاب يشغّل حاوية Asterisk
22.10.0 وحاوية SIPp على شبكة خاصة `172.30.0.0/24`؛ سنعامل حاوية SIPp كـ "الناقل"
الذي يضع المكالمات الواردة، ونضيف نقطة طرفية للخط تُحوّل تلك المكالمات إلى سياق `from-pstn`.

![خط SIP بين نظام Asterisk PBX وITSP: يقوم الـ PBX بالتسجيل كحساب واحد، المكالمات الصادرة تُطلب إلى `PJSIP/<num>@trunk`، والمكالمات الواردة تُنزل في سياق `from-pstn`.](../images/09-sip-trunking-fig01.png)

### 1. إضافة نقطة طرفية للخط

أضف خطًا قائمًا على IP إلى `lab/asterisk/etc/pjsip.conf` يتطابق مع مضيف SIPp في المختبر
ويُحوّل المكالمات الواردة إلى `from-pstn`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. توجيه الـ DID الوارد

في `lab/asterisk/etc/extensions.conf`، أضف سياق `from-pstn` يجيب على
الـ DID الذي سيُطلبه الناقل التجريبي ويعيد تشغيله، ثم أضف قاعدة صادرة:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

أعد تحميل كلا الملفين (`core reload`) وتحقق من تحميل الخط:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. إجراء مكالمة واردة عبر الخط

وجه سيناريو SIPp إلى الـ PBX مع الـ DID كمستخدم هدف. المختبر بالفعل
يوفر `lab/sipp/uac_9000.xml`، الذي يرسل INVITE إلى الامتداد `9000`؛ انسخه إلى
`uac_did.xml` وغيّر طلب الـ URI/مستخدم `To` من `9000` إلى `4830001000`،
ثم شغّله من حاوية SIPp:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

راقب وصول المكالمة إلى `from-pstn` على وحدة تحكم Asterisk (`pjsip set logger on`
يظهر INVITE الوارد؛ `core show channels` يظهر قناة `PJSIP/itsp-…`
تشغّل `demo-congrats`). لأن عنوان IP لمصدر SIPp يطابق `identify`،
فإن المكالمة تُقبل دون مصادقة — تمامًا كما يتصرف خط ناقل ثابت.

### 4. فحص الخط

التقط التكوين الكامل للخط لتدوين ملاحظاتك:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (تمديد) جعله خط تسجيل

قم بتشغيل حاوية Asterisk *الثانية* كمسجل حقيقي: أعطها
`endpoint`+`auth`+`aor` للحساب `4830001000`، ثم على الـ PBX استبدل
كتلة `identify` بكتلة `registration` من بداية هذا الفصل
(مُشيرًا `server_uri` إلى عنوان IP الخاص بالحاوية الثانية). أكد ذلك باستخدام
`pjsip show registrations` أن الحالة تُظهر `Registered`، ثم أجرِ مكالمة
في كل اتجاه.

## Summary

يُعرّف **trunk** SIP اتصال PBX الخاص بك بالعالم الخارجي، وفي PJSIP هو مجرد
نقطة نهاية مبنية من نفس عائلة `endpoint` + `auth` + `aor` التي تعرفها بالفعل،
بالإضافة إلى `identify` أو `registration`. استخدم **trunk** تسجيل
(`type=registration` مع `outbound_auth`) عندما يزودك المزود باسم مستخدم
وكلمة مرور؛ واستخدم **trunk** قائم على IP (`type=identify` مع `match`) عندما
يكون المصادقة عبر عنوان IP المصدر — وقم بتقيد الأخير باستخدام `match`
ضيق و`acl`، لأن **trunk** غير موثّق يُعد هدفًا للاحتيال على المكالمات. عند
الوصول، يصل DID الخاص بالمزود كـ `${EXTEN}` في سياق `from-pstn` الخاص بك، حيث
توجهه إلى امتداد، أو IVR، أو طابور — الأنماط و`${EXTEN:-N}` تحافظ
على كتل DID مدمجة. عند الصعود، اضبط `CALLERID(num)` إلى رقم تملكه، وحوّل
إلى E.164 في مكان واحد، وسلّم المكالمة إلى `PJSIP/<number>@trunk`. بنِ
المرونة عبر تجربة عدة **trunks** والتفرّع بناءً على `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` تعني إعادة توجيه؛ `BUSY`/`NOANSWER` لا تعني)، وضع
التوجيه الأقل تكلفة في جدول `GoSub`. أخيرًا، الـ NAT للـ **trunks** ذو جانبين:
`external_media_address`/`external_signaling_address`/`local_net` على **النقل** لعنوانك العام، و`direct_media=no`،`rtp_symmetric`،
`force_rport`، و`rewrite_contact` على **نقطة النهاية** لوسائط المزود.

## Quiz

1. In PJSIP, the credentials used to authenticate an *outbound* call or
   registration to a provider are referenced with:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. You should use a `type=registration` trunk when:
   - A. The provider identifies you by your source IP address.
   - B. The provider gives you a username and password and expects you to log in.
   - C. You never want Asterisk to send a `REGISTER`.
   - D. The trunk is between two static-IP servers you control.
3. The `identify` object's `match` option accepts (choose all that apply):
   - A. An IP address
   - B. A CIDR range
   - C. A hostname (resolved at config-load time)
   - D. A SIP username only
4. On Asterisk 22, `auth_type=userpass` is:
   - A. The only valid value
   - B. Deprecated and converted to `digest`
   - C. Removed and causes a load error
   - D. Required for outbound registration
5. An inbound DID number arrives in the dialplan as:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` in the trunk endpoint's `context`
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. To send the last two digits of the dialled DID `4830003007` to an extension,
   you would use:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. After `Dial()` to a trunk, you should fail over to a backup trunk on which
   `${DIALSTATUS}` values (choose two)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. To set the caller-ID number presented to the provider before dialling out, use:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. The options that tell Asterisk its *public* address when the server is behind
   NAT are set on the:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` on a trunk endpoint causes Asterisk to:
    - A. Encrypt RTP with SRTP
    - B. Send RTP back to the address the media actually arrived from, ignoring the SDP
    - C. Disable RTP entirely
    - D. Force direct media between endpoints

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
