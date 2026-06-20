# استخدام ميزات الـ PBX

في أنظمة SIP، يتم تنفيذ معظم ميزات الهاتف في الـ endpoint. هناك مجموعة متنوعة من هواتف SIP والمصنعين، ولا يُضمن التوافق التام بينها. قام فريق تطوير Asterisk بعمل مذهل في تنفيذ معظم هذه الميزات داخل الـ PBX نفسه، مما يجعل Asterisk شبه مستقل عن الـ endpoint. ومع ذلك، قد تجد أحيانًا أن نفس الوظيفة تُنفّذ من قبل كل من الهاتف وAsterisk. تكامل الهاتف مع الـ PBX هو الجبهة التالية في تحسين قابلية الاستخدام، وهو ما تركز عليه الأنظمة المملوكة حالياً. في هذا الفصل، ستتعلم كيفية استخدام معظم هذه الميزات.

## الأهداف

- إيقاف المكالمة
- التقاط المكالمة
- تحويل المكالمة
- مؤتمر المكالمات (ConfBridge)
- تسجيل المكالمة
- موسيقى الانتظار

## أين تُطبق الميزات

أولاً وقبل كل شيء، من المهم أن تفهم متى تُنفَّذ ميزات الـ PBX مقابل متى يقوم الهاتف بكل العمل. على سبيل المثال، يمكنك تحويل مكالمة باستخدام زر **TRANSFER** على الهاتف أو عن طريق طلب # (تحويل غير مشروط يتم تنفيذه بواسطة الـ PBX نفسه).

## الميزات التي ينفذها Asterisk

- Music on hold
- Call parking
- Call pickup
- Call recording
- ConfBridge conference room
- Call transfer (blind and consultative)

## الميزات عادةً ما تُنفّذها خطة الاتصال

هذه الميزات تحتاج إلى برمجتها في خطة الاتصال الخاصة بـ Asterisk (extensions.conf):

- تحويل المكالمة عند الانشغال
- تحويل المكالمة الفوري
- تحويل المكالمة عند عدم الرد
- تصفية المكالمات (القائمة السوداء)
- عدم الإزعاج
- إعادة الاتصال

## الميزات التي عادةً ما تُنفّذها الهاتف

يتم تنفيذ هذه الميزات بواسطة برنامج الهاتف الثابت:

![أين تُنفّذ عادةً ميزات PBX: في Asterisk نفسه، أو في مخطط الاتصال، أو في الهاتف](../images/13-pbx-features-fig01.png)

- وضع المكالمة على الانتظار
- تحويل أعمى
- تحويل استشاري
- مؤتمر ثلاثي الاتجاهات
- مؤشر انتظار الرسائل

## ملف تكوين الميزات

بعض الميزات التي تم تقديمها في هذا الفصل يتم تكوينها في ملف التكوين **features.conf**. يمكن تغيير سلوك بعض الميزات عن طريق تعديل هذا الملف. لقد أدرجنا المقتطف ذي الصلة أدناه. في الأقسام التالية من هذا الفصل، سنصف كل ميزة. مقتطف من الملف النموذجي (Asterisk 22)

![The `[featuremap]` section of features.conf, with the default DTMF feature codes](../images/13-pbx-features-fig02.png)

منذ Asterisk 12، تم نقل **call parking** من `features.conf` إلى وحدة مستقلة، `res_parking`، مع التكوين في `res_parking.conf`. كتلة **parking-lot** أدناه (`parkext`، `parkpos`، `context`، `parkingtime`، وما إلى ذلك) موجودة في `res_parking.conf`. يظل قسم `[featuremap]` (رموز الميزات DTMF، بما في ذلك `parkcall`) في `features.conf`.

خيارات **parking-lot** موجودة في `res_parking.conf`. دائمًا ما يكون هناك موقف سيارات يُدعى `default`، حتى وإن لم يكن موجودًا في ملف التكوين. المقتطف أدناه مأخوذ من Asterisk 22 `res_parking.conf.sample`:

```
; res_parking.conf
[default]                       ; Default Parking Lot
parkext => 700                  ; What extension to dial to park. (optional; if
                                ; specified, extensions will be created for parkext and
                                ; the whole range of parkpos)
parkpos => 701-720              ; What range of parking spaces to use - must be numeric.
                                ; Creates these spaces as extensions if parkext is set.
context => parkedcalls          ; Which context parked calls and the default park
                                ; extension are created in
;parkingtime => 45             ; Number of seconds a call can be parked before returning
;comebacktoorigin = yes        ; When a parked call times out, attempt to send it back to
                               ; the peer that parked it (default is yes)
;courtesytone = beep           ; Sound file to play when someone picks up a parked call
;parkedplay = caller           ; Who to play courtesytone to: parked, caller, both (default caller)
;parkedcalltransfers = caller  ; Enable DTMF transfers when picking up a parked call (default no)
;parkedcallreparking = caller  ; Enable DTMF parking when picking up a parked call (default no)
;parkedcallhangup = caller     ; Enable DTMF hangups when picking up a parked call (default no)
;findslot => next              ; 'next' uses the next space after the most recently used one;
                               ; 'first' (default) uses the lowest-numbered space available
;parkedmusicclass = default    ; MOH class to use for the parked channel
```

رموز ميزات DTMF (بما في ذلك **one-step** `parkcall`) تظل في قسم `[featuremap]` من `features.conf`:

```
; features.conf
[featuremap]
;blindxfer => #1                ; Blind transfer  (default is #) -- Make sure to set the T and/or t option in the Dial() or Queue() app call!
;disconnect => *0               ; Disconnect  (default is *) -- Make sure to set the H and/or h option in the Dial() or Queue() app call!
;atxfer => *2                   ; Attended transfer  -- Make sure to set the T and/or t option in the Dial() or Queue()  app call!
;parkcall => #72                ; Park call (one step parking)  -- Make sure to set the K and/or k option in the Dial() app call!
;automixmon => *3               ; One Touch Record a.k.a. Touch MixMonitor -- Make sure to set the X and/or x option in the Dial() or Queue() app call!
```

## نقل المكالمات

يمكن تنفيذ نقل المكالمات بواسطة الهاتف، أو بواسطة ATA، أو بواسطة Asterisk نفسه. راجع دليل هاتفك لتفهم كيفية نقل المكالمات. إذا كان هاتفك لا يدعم نقل المكالمات، يمكنك استخدام Asterisk لإنجاز هذه المهمة. يتم تنفيذ نقل المكالمات بطريقتين مختلفتين.

الطريقة الأولى هي استخدام ميزة النقل العمياء: اضغط # متبوعًا بالرقم المراد نقله. أحيانًا ستستخدم ميزة النقل في هاتفك IP أو في برنامج الهاتف الناعم IP. يمكنك تغيير حرف النقل عن طريق تعديل المعامل blindxfer في ملف features.conf.

يمكنك تمكين النقل المساعد في Asterisk بإزالة الـ ; قبل المعامل atxfer في ملف features.conf. أثناء المحادثة، تضغط *2. سيقول Asterisk "transfer" ويعطيك نغمة طلب. يُرسل المتصل إلى الموسيقى أثناء الانتظار. بعد أن تتحدث إلى الشخص المقصود وتغلق الهاتف، يقوم النظام بربط المتصل بالوجهة.

![Call transfer: the steps for a blind transfer (press # during the call) and an attended transfer (press *2)](../images/13-pbx-features-fig03.png)

### قائمة مهام التكوين

1. بالنسبة لنقطة النهاية PJSIP، تأكد من أن الخيار `direct_media` مضبوط على `no` (حتى يتدفق الوسائط عبر Asterisk وتُكتشف رموز المميزات)، أو استخدم خيار `t`/`T` في تطبيق `Dial()`

## Call parking

يُستخدم هذا الميزة لإيقاف مكالمة مؤقتًا. يساعد ذلك، على سبيل المثال، عندما تجيب على مكالمة هاتفية من خارج غرفتك وتريد تحويل المكالمة مرة أخرى إلى مكتبك. يمكنك تحقيق ذلك بإيقاف المكالمة في امتداد. بمجرد وصولك إلى مكتبك، ما عليك سوى طلب رقم امتداد الإيقاف لاستعادة المكالمة.

![Call parking: dial 700 to park a call into the first free slot (701–720); Asterisk announces the slot, which you dial from any phone to retrieve the call](../images/13-pbx-features-fig04.png)

بشكل افتراضي، يُستخدم امتداد 700 لإيقاف المكالمة. في وسط المحادثة، اضغط # لنقل المكالمة إلى امتداد 700. الآن سيعلن Asterisk عن امتداد الإيقاف الخاص بك، مثل 701 أو 702. اغلق الهاتف، وسيتم وضع المتصل في وضع الانتظار. انتقل إلى هاتف مكتبك واطلب رقم امتداد الإيقاف المعلن لاستعادة المكالمة. إذا تم إيقاف المتصل لفترة طويلة، سيتفعيل ميزة انتهاء المهلة وسيعود الامتداد الأصلي الذي تم طلبه إلى الرنين مرة أخرى.

### Configuration task list

اتبع الخطوات أدناه لتمكين إيقاف المكالمات. الخطوة 1: اجعل ساحة الإيقاف قابلة للوصول من مخطط الاتصال الخاص بك (مطلوب). ساحة الإيقاف الافتراضية `context` هي `parkedcalls` (محددة في `res_parking.conf`). أدرج ذلك السياق في السياق الذي تُجري هواتفك الاتصالات منه، في `extensions.conf`:

```
include => parkedcalls
```

الخطوة 2: اختبر ميزة إيقاف المكالمات بطلب #700. ملاحظات:

- لن يظهر امتداد الإيقاف في أمر CLI `dialplan show`.
- من الضروري إعادة تحميل وحدة الإيقاف بعد تعديل ملف تكوين الإيقاف: `module reload res_parking.so`. لتغييرات features.conf، `module reload features.so`.
- لإيقاف مكالمة، تحتاج إلى النقل إلى #700. تحقق من خيارات `t` و`T` في تطبيق `Dial()`.

## التقاط المكالمات

يتيح لك التقاط المكالمات التقاط مكالمة من زميل في نفس مجموعة المكالمات. سيساعد ذلك على تجنّب، على سبيل المثال، الاستيقاظ للرد على مكالمة تُرنّ لشخص آخر في غرفتك لكنه غير موجود. عن طريق طلب *8، يمكنك التقاط مكالمة ضمن مجموعة مكالماتك. يمكن تعديل هذا الرقم في ملف `features.conf`.

![التقاط المكالمات: الأعضاء يمكنهم فقط التقاط المكالمات داخل مجموعتهم الخاصة؛ المشغل (pickupgroup=1,2,3) يمكنه التقاط المكالمات من جميع المجموعات](../images/13-pbx-features-fig05.png)

### قائمة مهام التكوين

اتبع الخطوات أدناه لتكوين ميزة التقاط المكالمات. الخطوة 1: تكوين مجموعة مكالمات لامتداداتك. يتم ذلك في ملف تكوين القناة (pjsip.conf, iax.conf, chan_dahdi.conf). بالنسبة لنقاط النهاية PJSIP، عيّن `call_group` و`pickup_group` في قسم النقطة النهاية في `pjsip.conf` (يستخدم pjsip.conf أسماء خيارات snake_case). هذه المهمة مطلوبة.

For PJSIP (pjsip.conf):
```
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```


الخطوة 2: تغيير رقم ميزة التقاط المكالمات (اختياري). يتم ضبطه في قسم `[general]` من `features.conf`، وليس في `pjsip.conf`:

```
; features.conf
[general]
pickupexten = *8   ; Configures the call pickup extension (default is *8)
```

## مؤتمر (مؤتمر مكالمات)

هناك طرق مختلفة لتنفيذ مؤتمر على Asterisk. الخيار الأول هو ببساطة استخدام قدرة المؤتمر الثلاثي في الهاتف. باستخدام هذه الميزة في الهاتف لا تحتاج إلى أي دعم في الخادم نفسه. ومع ذلك، عندما تريد مؤتمرًا يضم أكثر من 3 أشخاص، يجب تشغيل غرفة مؤتمر. تطبيق المؤتمر الحديث في Asterisk هو ConfBridge (`app_confbridge`).

يدعم ConfBridge مؤتمرات صوتية عالية الدقة ومؤتمرات فيديو. هناك بعض القيود على مؤتمرات الفيديو مثل عدم وجود تحويل ترميز — يجب على جميع المشاركين استخدام نفس الـ codec والملف التعريفي. يستخدم مؤتمر الفيديو وضع "اتبع المتحدث"، حيث يتم عرض صورة آخر شخص يتحدث. يمكنك بسهولة تكوين قوائم DTMF جديدة في ConfBridge.

يحل ConfBridge محل تطبيق MeetMe القديم، الذي تم إهماله في Asterisk 19. لا يزال MeetMe موجودًا في شجرة مصدر Asterisk 22، لكنه يعتمد على DAHDI ولا يُبنى بشكل افتراضي، لذا في تثبيت PJSIP النموذجي يكون غير متوفر ببساطة — ConfBridge هو تطبيق المؤتمر المدعوم. على عكس MeetMe، لا يتطلب ConfBridge **DAHDI** أو مصدر توقيت مادي: فهو يعتمد على واجهة التوقيت المدمجة في Asterisk (`res_timing_timerfd` على Linux، أو `res_timing_pthread`)، لذا لا يلزم وجود وحدة `dahdi_dummy`. إذا كنت تقوم بالترحيل من نظام أقدم يستخدم `MeetMe()` و`meetme.conf`، استبدلهما بـ`ConfBridge()` و`confbridge.conf` كما هو موضح أدناه.

### ConfBridge

لبدء غرفة مؤتمر، يتم سرد الصياغة أدناه.

```
ConfBridge(conference,bridge_profile,user_profile,menu)
```

للحصول على وصف كامل للأمر يمكنك استخدام `core show application confbridge`.

![Output of `core show application confbridge`, showing the synopsis, syntax, and the bridge_profile, user_profile, and menu arguments](../images/13-pbx-features-fig06.png)

![Several PJSIP endpoints join one named ConfBridge conference (101); one participant is the admin. The mixing and timing are handled by `app_confbridge` together with `bridge_softmix` and the built-in `res_timing_*` timer — no DAHDI required.](../images/13-pbx-features-fig09.png)

كما ترى أعلاه هناك ثلاثة وسائط مهمة، كل منها يطابق نوع قسم في `confbridge.conf`. **bridge_profile** (قسم `type=bridge`): هنا تختار الحد الأقصى لعدد المشاركين (`max_members`)، التسجيل (`record_conference`)، `video_mode`، والعديد من المعلمات العامة للجسر.

ليس من المنطقي إعادة إنتاج ملف المثال الكامل هنا، لذا دعني أقدم لك مثالًا بسيطًا حول كيفية تكوين `bridge_profile` في ملف `confbridge.conf`.

```
[default_bridge]
type=bridge
max_members=10
record_conference=yes
```

**user_profile** (a `type=user` section): هنا تقوم بتعريف الخيارات التي تكون محددة لكل مستخدم، مثل ما إذا كان المستخدم مسؤولًا (`admin=yes`)، وما إذا كان يبدأ صامتًا (`startmuted=yes`)، موسيقى الانتظار، والعديد من الخيارات الأخرى لكل مستخدم. مثال:

```
[admin_user]
type=user
admin=yes
```

**menu** (a `type=menu` section): هنا تقوم بتعريف تخطيط لوحة المفاتيح (DTMF) للمؤتمر — على سبيل المثال أي مفتاح يبدّل كتم الصوت، يضبط مستوى الصوت، أو يخرج من المؤتمر. تحقق من ملف `confbridge.conf.sample` لرؤية جميع الإجراءات المتاحة. مثال:

```
[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
4=decrease_talking_volume
5=increase_talking_volume
6=leave_conference
```

#### وظائف Confbridge

يمكن تمرير خيارات جسر المؤتمرات ديناميكياً في مخطط الاتصال باستخدام الدالة CONFBRIDGE(). راجع الأمثلة أدناه:

```
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

### أوامر إدارة ConfBridge والترحيل من MeetMe

إذا كنت قادماً من MeetMe، فإن وظائف الإدارة التي كنت تستخدمها عبر `MeetMeAdmin()` وخيار `a` (admin) تُعبَّر الآن من خلال **ملف تعريف المستخدم الإداري** (`admin=yes`) بالإضافة إلى إجراءات **القائمة**. يمكن للمسؤول الذي ينضم بملف تعريف إداري وقائمة تحتوي على إجراءات إدارية أن يقفل الغرفة، يطرد المستخدمين، ويكتم المشاركين مباشرةً من لوحة المفاتيح. إجراءات القائمة ذات الصلة في `confbridge.conf` هي:

- `admin_kick_last` -- طرد آخر مستخدم انضم
- `admin_toggle_mute_participants` -- كتم/إلغاء كتم جميع المشاركين غير الإداريين
- `toggle_mute` -- كتم/إلغاء كتم نفسك
- `participant_count` -- الإعلان عن عدد المشاركين
- `leave_conference` -- مغادرة الجسر والاستمرار في الـ dialplan

هذه تستبدل أعلام خيار MeetMe `MeetMe()` (`a`، `A`، `m`، `M`، `l`، `x`، …) وأوامر `MeetMeAdmin()` (`k`، `K`، `L`، `M`، `N`، …). في تثبيت PJSIP حديث لن تقوم بتحميل `app_meetme` مطلقاً؛ جميع إعدادات المؤتمر موجودة في `confbridge.conf`، ويتم تطبيق التغييرات باستخدام `module reload app_confbridge.so` (منطق ConfBridge موجود في `app_confbridge`؛ لا يوجد وحدة `res_confbridge`).

### مثال ConfBridge

لإنشاء غرفة مؤتمر يمكن الوصول إليها عبر الامتداد 500، في `extensions.conf`:

```
exten => 500,1,Answer()
 same => n,ConfBridge(101,default_bridge,default_user,sample_user_menu)
```

المتصل الأول الذي يطلب 500 ينشئ مؤتمر `101`؛ المتصلون اللاحقون ينضمون إليه. الملفات الشخصية والقوائم المشار إليها هنا (`default_bridge`، `default_user`، `sample_user_menu`) معرفة في `confbridge.conf`. لفرض رمز PIN، اضبط `pin=` في ملف المستخدم؛ لجعل مشارك مديرًا للمؤتمر، امنحه ملف مستخدم يحتوي على `admin=yes`.

## Call Recording

هناك عدة طرق لتسجيل مكالمة في Asterisk. يمكنك استخدام تطبيق `MixMonitor()` لتسجيل المكالمات بسهولة. (تم إزالة التطبيق الأقدم `Monitor`، الذي كان يسجل ملفين منفصلين؛ استخدم `MixMonitor` بدلاً منه.)

### Using the MixMonitor application

تطبيق `MixMonitor` يسجل الصوت في القناة الحالية إلى الملف المحدد. إذا كان اسم الملف مسارًا مطلقًا، فإنه يستخدم ذلك المسار. وإلا، فإنه ينشئ الملف في دليل المراقبة المُكوَّن في asterisk.conf.

![The MixMonitor() application: records and mixes the audio of a channel to a file, with options for append, bridged-only, and volume adjustment](../images/13-pbx-features-fig09.png)

### MixMonitor()

سجِّل مكالمة وامزج الصوت أثناء التسجيل. الصياغة: `MixMonitor(filename.extension[,options[,command]])`. يسجل الصوت على القناة الحالية إلى الملف المحدد. الخيارات الصالحة:

- a - يضيف إلى الملف بدلاً من استبداله.
- b - يحفظ الصوت إلى الملف فقط بينما تكون القناة متصلة.
- ملاحظة: لا يشمل المؤتمرات.
- v(<x>) - يضبط مستوى الصوت المسموع بمعامل <x> (يتراوح بين -4 إلى 4)
- V(<x>) - يضبط مستوى الصوت المنطوق بمعامل <x> (يتراوح بين -4 إلى 4)
- W(<x>) - يضبط كلاً من مستويات الصوت المسموع والمنطوق بمعامل <x> (يتراوح بين -4 إلى 4)
- <command> سيتم تنفيذها عندما ينتهي التسجيل. أي سلاسل تطابق ^{X} سيتم إلغاء هروبها إلى ${X} وسيتم تقييم جميع المتغيرات في ذلك الوقت. المتغير MIXMONITOR_FILENAME سيحتوي على اسم الملف المستخدم للتسجيل.

مورد مثير للاهتمام هو ميزة التسجيل بلمسة واحدة `automixmon`، التي تسمح للطرف بضغط رمز DTMF (العينة `features.conf` تقترح `*3`؛ لا يوجد إعداد افتراضي مدمج، لذا عليك تعيينه) أثناء المكالمة لبدء التسجيل فورًا (وتعطيله). تم بناء هذه الميزة على MixMonitor، لذا فهي تكتب ملفًا مختلطًا واحدًا. مثال:

```
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automixmon)
 same => n,Dial(PJSIP/${EXTEN},20,jtTXx) ; X and x enable one-touch MixMonitor recording
```

The `X` and `x` options enable the one-touch MixMonitor feature for the caller and callee respectively. Because MixMonitor records a single mixed file, there is no need to combine separate IN/OUT files afterward (the old `automon`/`Monitor` approach, which produced two files for `soxmix`, was removed along with the `Monitor` application).

If you don’t want to use Set() before the Dial() application, you can set this in the globals section:

```
[globals]
DYNAMIC_FEATURES=automixmon
```

### Music on hold

Music on hold (MOH) has changed several times among versions 1.0, 1.2, and 1.4. In the latest version, MOH defaults to "FILE-BASED". In other words, Asterisk will supply the MOH files in formats such as g729, alaw, ulaw, and gsm. Thus, it is not necessary to transcode the music before sending it to the channel. This saves processor time, which is a welcomed modification for those working with production systems.

In older versions, MOH was usually provided by MP3 (it still can be configured that way). Providing MOH using MP3 obligates Asterisk to transcode, spending valuable CPU power in the process.

The new configuration file is shown below. Note that the default class now uses the native file format mode=files. All other modes are commented. Each section is a class. The only uncommented class at this point is default. If you want to have different classes for different files, you will need to create new sections (classes).

![عينة تكوين musiconhold.conf، تُظهر أوضاع MOH الصالحة (quietmp3, mp3, custom, files, …)](../images/13-pbx-features-fig10.png)

```
; Music on Hold -- Sample Configuration
;[samplemp3]
;mode=quietmp3
;directory=/var/lib/asterisk/mohmp3
;
; valid mode options:
; quietmp3      -- default
; mp3           -- loud
; mp3nb         -- unbuffered
; quietmp3nb    -- quiet unbuffered
; custom        -- run a custom application (See examples below)
; files         -- read files from a directory in any Asterisk supported
;                  media format. (See examples below)
;[manual]
;mode=custom
; Note that with mode=custom, a directory is not required, such as when reading
; from a stream.
;directory=/var/lib/asterisk/mohmp3
;application=/usr/bin/mpg123 -q -r 8000 -f 8192 -b 2048 --mono -s
;[ulawstream]
;mode=custom
;application=/usr/bin/streamplayer 192.168.100.52 888
;format=ulaw
; mpg123 on Solaris does not always exit properly; madplay may be a better
; choice
;[solaris]
;mode=custom
;directory=/var/lib/asterisk/mohmp3
;application=/site/sw/bin/madplay -Q -o raw:- --mono -R 8000 -a -12
;
;
; File-based (native) music on hold
;
; This plays files directly from the specified directory, no external
; processes are required. Files are played in normal sorting order
; (same as a sorted directory listing), and no volume or other
; sound adjustments are available. If the file is available in
; the same format as the channel's codec, then it will be played
; without transcoding (same as Playback would do in the dialplan).
; Files can be present in as many formats as you wish, and the
; 'best' format will be chosen at playback time.
;
; NOTE:
; If you are not using "autoload" in modules.conf, then you
; must ensure that the format modules for any formats you wish
; to use are loaded _before_ res_musiconhold. If you do not do
; this, res_musiconhold will skip the files it is not able to
; understand when it loads.
;
[default]
mode=files
directory=/var/lib/asterisk/moh
;
;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes     ; Play the files in a random order
```

### مهام تكوين MOH

الآن، لاستخدام الموسيقى أثناء الانتظار، قم بتعيين فئة MOH في ملفات تكوين القنوات (chan_dahdi.conf، pjsip.conf، iax.conf، وما إلى ذلك). بالنسبة لنقاط النهاية PJSIP، عيّن `moh_suggest` في قسم نقطة النهاية في `pjsip.conf` (اسم الخيار القديم `musicclass` ينطبق على chan_dahdi وغيرها من برامج تشغيل القنوات، وليس على PJSIP). النغمات المجانية المثبتة الآن بصيغة wav. عند وقت التثبيت، يمكنك اختيار (باستخدام make menuselect) صيغ ملفات MOH المتاحة. إذا أردت إضافة ملفات MOH جديدة، سيتعين عليك توفيرها بالصيغ المطلوبة. على سبيل المثال:

في `/etc/asterisk/chan_dahdi.conf`، أضف السطر `musiconhold`.

```
[channels]
musiconhold=default
```

ثم قم بتحرير `/etc/asterisk/musiconhold.conf` لتعريف تلك الفئة:

```
[default]
mode=files
directory=/var/lib/asterisk/moh
```

في مخطط الاتصال، يمكنك تشغيل الموسيقى أثناء الانتظار على قناة باستخدام `StartMusicOnHold` (وإيقافها باستخدام `StopMusicOnHold`):

```
exten => 100,1,StartMusicOnHold(default)
 same => n,Dial(PJSIP/2)
```

لتشغيل موسيقى الانتظار لمدة ثابتة كاختبار سريع، استخدم تطبيق `MusicOnHold` مع مدة (بالثواني):

```
[local]
exten => 6601,1,MusicOnHold(default,30)
```

## خرائط التطبيقات

تسمح لك خرائط التطبيقات بإضافة ميزات جديدة باستخدام القسم `[applicationmap]` من ملف features.conf. افترض أنك تحتاج إلى تحديد نوع العميل الذي تجيب عليه في مركز الاتصال. يمكنك إنشاء خريطة تطبيق لكل نوع من العملاء، والتي يمكنها عد عدد العملاء الذين تم الرد عليهم لكل نوع.

## Summary

في هذا الفصل تعلمت أين توجد ميزات PBX في Asterisk — بعضها في النواة، وبعضها في مخطط الاتصال، وبعضها على الهاتف — وكيف يتم ربط رموز ميزات DTMF في قسم `[featuremap]` من `features.conf`. قمت بتكوين **نقل المكالمات** (العمياء والمراقبة) و**إيقاف المكالمات** (`res_parking.conf`، مع خيارات الاتصال `k`/`K` و مجموعة `parkedcalls`)، **التقاط المكالمات** حسب المجموعة، و**المؤتمرات** باستخدام **ConfBridge** (ملفات تعريف الجسر/المستخدم/القائمة `confbridge.conf`)، التي تحل محل MeetMe القديمة. أعددت **التسجيل بلمسة واحدة** باستخدام MixMonitor (`automixmon`، خيارات الاتصال `X`/`x` و`DYNAMIC_FEATURES`)، وقمت بتكوين **الموسيقى أثناء الانتظار**، ورأيت كيف تسمح **خرائط التطبيقات** بربط منطق مخطط الاتصال الخاص بك بتسلسل DTMF. باستخدام هذه اللبنات الأساسية يمكنك تقديم الميزات اليومية التي يتوقعها المستخدمون من PBX تجاري.

## Quiz

1. Which statements are true about call parking?
   - A. By default, extension 800 is used for call parking.
   - B. When you are away from your desk and receive a call, you can park it; the system announces the parking slot, and you dial that slot from any phone to retrieve the call.
   - C. By default, extension 700 parks a call, and calls are parked in slots 701–720.
   - D. You dial 700 to retrieve a parked call.
2. To use the call-pickup feature, all extensions must be in the same ___. For DAHDI channels this is configured in the ___ file.
3. When transferring a call you can choose between a ___ transfer, where the destination is not consulted first, and an ___ transfer, where you talk to the destination before completing it.
4. To make an attended (consultative) transfer you use the ___ sequence; for a blind transfer you use ___.
   - A. #1, *2
   - B. *2, #1
   - C. #2, #1
   - D. #1, #2
5. To host conference calls in Asterisk 22, you use the ___ application.
6. In ConfBridge, a participant is granted administrator privileges (kick, mute others, lock the room) by setting ___ in their user profile (`confbridge.conf`):
   - A. admin=yes
   - B. marked=yes
   - C. moderator=yes
   - D. type=admin
7. The best format for music on hold is MP3, because it uses very little processing power on the Asterisk server.
   - A. True
   - B. False
8. To pick up a call from a specific call group, you must be in the matching ___ group.
9. You can record a call with the MixMonitor() application or the one-touch recording (`automixmon`) feature. In the `features.conf` sample, `automixmon` is mapped to the ___ DTMF sequence.
   - A. *1
   - B. *2
   - C. *3
   - D. #1
10. In ConfBridge, which `confbridge.conf` user-profile option makes a participant join muted (they can hear the conference but cannot be heard until unmuted)?
    - A. startmuted=yes
    - B. listen=only
    - C. muteall=yes
    - D. quiet=yes

**Answers:** 1 — B, C · 2 — pickup group; `chan_dahdi.conf` · 3 — blind; attended · 4 — B · 5 — ConfBridge() · 6 — A · 7 — B · 8 — pickup · 9 — C · 10 — A
