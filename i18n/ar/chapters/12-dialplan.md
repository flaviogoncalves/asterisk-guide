# ميزات متقدمة في مخطط الاتصال

ناقش الفصل 3 أساسيات مخطط الاتصال. لأسباب تعليمية، لم نشرح جميع الميزات، بل بعض أهمها فقط. سيتعمق هذا الفصل أكثر في مخطط الاتصال، موضحًا التقنيات المتقدمة، التطبيقات الجديدة، والمفاهيم.

## الأهداف

- تبسيط إدخالات الامتداد الخاصة بك
- معالجة أمان مخطط الاتصال وتصفية الامتدادات
- استقبال المكالمات باستخدام قائمة IVR
- استخدام الروتينات الفرعية لتجنب إعادة الكتابة غير الضرورية
- تنفيذ بعض أمان مخطط الاتصال باستخدام “Include”
- تنفيذ ميزة follow-me باستخدام AsteriskDB
- تنفيذ سلوك ما بعد ساعات العمل في نظام PBX الخاص بك
- استخدام أمر switch للتحويل إلى PBX آخر
- تنفيذ مدير الخصوصية
- تنفيذ البريد الصوتي
- تنفيذ دليل الشركة

## تبسيط مخطط الاتصال الخاص بك

يمكنك تبسيط مخطط الاتصال الخاص بك باستخدام الكلمة المفتاحية “same” لتعريف امتداد. يجب أن يقلل ذلك من عدد الأخطاء المطبعية في مخطط الاتصال. تحقق من المثال أدناه:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## أمان مخطط الاتصال

تم اكتشاف ثغرة في مخطط الاتصال الخاص بـ Asterisk تسمح للمستخدم بحقن قناة جديدة ورقم اتصال في مخطط الاتصال الخاص بك. لنفترض أن لديك السطر التالي في خادمك `exten=>_X.,1,Dial(PJSIP/${EXTEN})` وأن مستخدمًا خبيثًا طلب الرقم `3000&DAHDI/1/011551123456789` في برنامج الهاتف الناعم. بروتوكول SIP، بشكل افتراضي، يقبل أي أحرف أبجدية رقمية، لذا فإن الامتداد المطلوب سيفعل مكالمتين: واحدة للقناة PJSIP/3000 والأخرى للقناة DAHDI/011551123456789، وهو رقم دولي. وبالتالي، أي مستخدم لديه إمكانية الوصول إلى امتداد يمكنه الاتصال بأي مكان في العالم. أسهل طريقة لتجنب هذا السلوك هي تصفية الأرقام قبل استدعاء تطبيق dial. الدالة FILTER() مفيدة جدًا لهذا الغرض. مثال:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

سيسمح لك تطبيق filter بتصفية جميع الأحرف من الرقم المطلوب باستثناء الأرقام من 0 إلى 9. يمكن العثور على مزيد من المعلومات في الملف README‑SERIOUSLY.bestpractices.txt المتوفر من Asterisk.

## استقبال المكالمات باستخدام قائمة IVR.

في القسم السابق، استقبلت جميع المكالمات باستخدام DID أو التحويل إلى المشغل. الآن ستتعلم كيفية تنفيذ قائمة IVR وكذلك إنشاء خدمة موظف تلقائي. قبل الخوض في التفاصيل، دعنا نستعرض بعض التطبيقات الجديدة. وضعنا ناتج الأمر `core show application` أدناه ببساطة لتسهيل الأمر على القراء. يمكنك الحصول على هذه الأوصاف بنفسك باستخدام `core show application <application_name>`.

### تطبيق Background() التطبيق

هذا التطبيق سيقوم بتشغيل قائمة الملفات المعطاة بينما ينتظر أن يتم طلب رقم امتداد من القناة المتصلة. للاستمرار في انتظار الأرقام بعد أن ينتهي هذا التطبيق من تشغيل الملفات، يجب استخدام تطبيق **WaitExten**. خيار **langoverride** يحدد صراحةً اللغة التي يجب محاولة استخدامها للملفات الصوتية المطلوبة. أي سياق يتم تحديده سيكون سياق مخطط الاتصال الذي يستخدمه هذا التطبيق عند الخروج إلى الامتداد المطلوب. إذا لم يكن أحد الملفات الصوتية المطلوبة موجودًا، سيتم إيقاف معالجة المكالمة. الخيارات:

- s - يتسبب في تخطي تشغيل الرسالة إذا لم تكن القناة في حالة 'up' (أي لم يتم الرد عليها بعد). إذا حدث ذلك، سيعود التطبيق فورًا.
- n - لا تقم بالرد على القناة قبل تشغيل الملفات.
- m - يتم الإيقاف فقط إذا كان الضغط على رقم يطابق امتدادًا من رقم واحد في سياق الوجهة.

### تطبيق Record()

هذا التطبيق يسجل من القناة إلى اسم ملف محدد. إذا كان الملف موجودًا، فسيتم استبداله.

![الشكل 1 - ميزات مخطط الاتصال المتقدمة](../images/10-dialplan-advanced-features-img01.png)

- 'format' هو تنسيق نوع الملف الذي سيُسجَّل (wav, gsm, إلخ).
- 'silence' هو عدد الثواني من الصمت المسموح قبل الإرجاع.
- 'maxduration' هو الحد الأقصى لمدة التسجيل بالثواني؛ إذا كان مفقودًا أو صفرًا، لا يوجد حد أقصى.
- 'options' قد تحتوي على أي من الحروف التالية:
    - `a` — يضيف إلى تسجيل موجود بدلاً من استبداله
    - `n` — لا يجيب، لكن يسجل على أي حال إذا لم يتم الرد على الخط بعد
    - `q` — صامت (لا يشغل نغمة صفير)
    - `s` — يتخطى التسجيل إذا لم يتم الرد على الخط بعد
    - `t` — يستخدم مفتاح الإنهاء البديل `*` (DTMF) بدلاً من الافتراضي `#`
    - `x` — يتجاهل جميع مفاتيح الإنهاء (DTMF) ويستمر في التسجيل حتى الإغلاق

إذا كان اسم الملف يحتوي على %d، فسيتم استبدال هذه الأحرف برقم يزداد بواحد في كل مرة يتم فيها تسجيل الملف. استخدم core show file formats لرؤية الصيغ المتاحة على نظامك. يمكن للمستخدم الضغط على # لإنهاء التسجيل والمتابعة إلى الأولوية التالية. إذا أنهى المستخدم المكالمة أثناء التسجيل، فستفقد جميع البيانات وسيتم إنهاء التطبيق.

### تطبيق Playback()

هذا التطبيق يعيد تشغيل أسماء الملفات المعطاة (لا تشمل الامتداد). يمكن أيضًا تضمين الخيارات بعد رمز الأنبوب. خيار `skip` يتسبب في تخطي تشغيل الرسالة إذا لم تكن القناة في حالة `up` (أي لم يتم الرد عليها بعد).

![10-ميزات مخطط الاتصال المتقدمة الشكل 2](../images/10-dialplan-advanced-features-img02.png)

![10-ميزات-متقدمة-مخطط-الاتصال الشكل 3](../images/10-dialplan-advanced-features-img03.png)

إذا تم تحديد 'skip'، سيعود التطبيق فورًا إذا لم تكن القناة غير معلقة. وإلا، ما لم يتم تحديد 'noanswer'، سيتم الرد على القناة قبل تشغيل الصوت. ليست كل القنوات تدعم تشغيل الرسائل بينما لا تزال معلقة. إذا تم تحديد 'j'، سيقفز التطبيق إلى الأولوية n+101 عندما لا يكون الملف موجودًا، إذا كان موجودًا. هذا التطبيق يضع متغير القناة التالي عند الانتهاء:

- PLAYBACKSTATUS — حالة محاولة التشغيل كنص، واحدة من:
    - `SUCCESS`
    - `FAILED`

### تطبيق Read() التطبيق

هذا التطبيق يقرأ عددًا محددًا مسبقًا من أرقام السلسلة، عددًا معينًا من المرات، من المستخدم إلى المتغيّر المعطى.

- filename -- الملف الذي يُشغَّل قبل قراءة الأرقام أو النغمة باستخدام الخيار i
- maxdigits -- الحد الأقصى المقبول لعدد الأرقام. يتوقف القراءة بعد إدخال maxdigits (دون الحاجة إلى ضغط المستخدم لمفتاح #). القيمة الافتراضية هي 0 - لا حد - للانتظار حتى يضغط المستخدم مفتاح #. أي قيمة أقل من 0 تعني نفس الشيء. الحد الأقصى المقبول هو 255.

![10-dialplan-advanced-features الشكل 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features الشكل 5](../images/10-dialplan-advanced-features-img05.png)

- option -- الخيارات هي `s`, `i`, `n`:
    - `s` — إرجاع فورًا إذا لم يكن الخط متاحًا
    - `i` — تشغيل اسم الملف كإشارة نغمة من `indications.conf` الخاص بك
    - `n` — قراءة الأرقام حتى إذا لم يكن الخط متاحًا
- attempts -- إذا كان أكبر من 1، عدد المحاولات التي ستُجرى في حال عدم إدخال بيانات
- timeout -- عدد صحيح من الثواني للانتظار لاستجابة رقم. إذا كان أكبر من 0، ستستبدل هذه القيمة مهلة الانتظار الافتراضية.

يجب على تطبيق read() قطع الاتصال إذا فشلت الدالة أو حدث خطأ.

### تطبيق Gotoif()

هذا التطبيق سيجعل قناة الاتصال تقفز إلى الموقع المحدد في مخطط الاتصال بناءً على تقييم الشرط المعطى. ستستمر القناة عند **labeliftrue** إذا كان الشرط صحيحًا، أو عند **'labeliffalse'** إذا كان الشرط خاطئًا. يتم تحديد العلامات باستخدام نفس الصياغة المستخدمة داخل تطبيق **Goto**. إذا تم حذف العلامة التي يختارها الشرط، لن يتم إجراء أي قفزة؛ بل سيستمر التنفيذ مع الأولوية التالية في مخطط الاتصال.

### Lab: إنشاء قائمة IVR خطوة بخطوة

لننشئ قائمة IVR بالوظيفة التالية. عند الاتصال، تقوم الـ IVR بتشغيل ملف صوتي يحتوي على الرسالة “Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.” تقوم الأرقام بتوجيه المتصل كما يلي:

- `1` — تحويل إلى المبيعات (PJSIP/4001)
- `2` — تحويل إلى الدعم الفني (PJSIP/4002)
- `3` — تحويل إلى التدريب (PJSIP/4003)
- لم يتم ضغط أي رقم — تحويل إلى المشغل (PJSIP/4000)

**الخطوة 1 – تسجيل المطالبات**

Let’s create an extension to record the prompts. To record a prompt, dial from a soft phone to `9003<filename>` (for example, `9003welcome`). When you hear the beep, start recording; press `#` to stop. You will hear a beep, and the system will play back the recorded prompt.

**الخطوة 2 – إنشاء منطق القائمة**

عند طلب التحويل إلى الامتداد 9004، ينتقل المعالجة إلى القائمة في الامتداد `s`، الأولوية 1.

### المطابقة أثناء الطلب

هذه قائمة إعداد الشركة لاستقبال المكالمات. يقوم تطبيق `Background()` بتشغيل رسالة الترحيب ثم ينتظر الأرقام، مطابقًا ما يطلبه المتصل مع الامتدادات المعرفة في السياق الحالي.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

عند الاتصال بهذه الشركة، يتم تشغيل رسالة الترحيب أولاً. بعد ذلك، ينتظر Asterisk رقمًا ليُطلب:

| الرقم المُطلب | إجراء Asterisk |
|---------------|-----------------|
| 1 | يتصل فورًا بـ`Dial(DAHDI/1)` |
| 2 | ينتظر مهلة الانتظار، ثم يتصل بـ`Dial(DAHDI/2)` |
| 21 | يتصل فورًا بـ`Dial(DAHDI/3)` |
| 22 | يتصل فورًا بـ`Dial(DAHDI/4)` |
| 3 | ينتظر مهلة الانتظار، ثم يقطع الاتصال |
| 31 | يتصل فورًا بـ`Dial(DAHDI/5)` |
| 32 | يتصل فورًا بـ`Dial(DAHDI/6)` |

من المهم تجنّب الغموض في القوائم. الجميع يرغب في الحصول على رد سريع. لهذا السبب، لا ينبغي استخدام الأرقام 2 أو 21 أو 22.

### مختبر: استخدام تطبيق Read()

يرجى تجربة المختبر باستخدام تطبيق read(). يقوم Read بقبول الأرقام من المستخدم وإدراجها في المتغيّر المحدد؛ يمكنك بعد ذلك استخدام تطبيق gotoif لإعادة توجيه المكالمة.

## تضمين السياق

يمكن للسياق أن يتضمن محتويات سياق آخر. في المثال أعلاه، يمكن لأي قناة طلب أي امتداد في السياق الداخلي، لكن قناة 4003 فقط يمكنها طلب امتدادات دولية. يمكنك استخدام تضمين السياق لتسهيل إنشاء مخطط الاتصال. باستخدام تضمين السياق، يمكنك التحكم في من يملك الوصول إلى أي امتدادات.

### استكشاف رسالة “الرقم غير موجود” وإصلاحها

من الشائع جدًا تلقي رسالة “الرقم غير موجود”. يخلط معظم الناس بين مفهوم السياقات المتضمنة لأنه ليس بديهيًا. كقاعدة عامة، ابدأ بالانتقال إلى ملف تكوين القناة الواردة، مثل `pjsip.conf`، `chan_dahdi.conf`، و`iax.conf`، وحدد السياق الحالي. ثم انتقل إلى مخطط الاتصال في ملف extensions.conf وتحقق مما إذا كان الرقم الذي تم طلبه موجودًا في ذلك السياق. إذا لم يكن كذلك، فهناك خطأ ما في مخطط الاتصال الخاص بك. القواعد الذهبية للسياقات هي: 1. لا يمكن للقناة طلب أرقام إلا ضمن نفس السياق الخاص بها. 2. السياق الذي تتم معالجة المكالمة فيه يُحدد في ملف تكوين القناة الواردة (`chan_dahdi.conf`، `iax.conf`، `pjsip.conf`).

## Using the switch statement

يمكنك إرسال معالجة الـ dial plan إلى خادم آخر باستخدام أمر switch. ستحتاج إلى اسم ومفتاح الخادم الآخر. الـ context هو الـ context الوجهة.

![10-dialplan-advanced-features الشكل 6](../images/10-dialplan-advanced-features-img06.png)

## ترتيب معالجة مخطط الاتصال

عند تلقي Asterisk مكالمة واردة، يبحث في السياق المحدد بواسطة القناة. في بعض الحالات، إذا كان هناك أكثر من نمط يطابق الرقم المطلوب، قد لا يتمكن Asterisk من معالجة المكالمة بالطريقة التي تتوقعها تمامًا. يمكنك رؤية ترتيب المطابقة باستخدام أمر CLI `dialplan show`. مثال: لنفترض أنك تريد طلب الرقم 912 لتوجيهه إلى خط تماثلي (DAHDI/1) وجميع الأرقام الأخرى التي تبدأ بـ 9 إلى خط تماثلي آخر (DAHDI/2). ستكتب شيئًا مثل:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

إذا تطابق نمطان مع امتداد، يمكنك التحكم في أي امتداد يُعالج أولاً باستخدام السياقات المتضمنة. يتم معالجة السياق المتضمن بعد النمط في نفس السياق.

## بيان #INCLUDE

هل ينبغي علينا استخدام ملف كبير أم عدة ملفات؟ يمكنك استخدام عبارة #include <filename> لتضمين ملفات أخرى في ملف extensions.conf الخاص بك. على سبيل المثال، يمكننا إنشاء ملف users.conf للمستخدمين المحليين وملف services.conf للخدمات الخاصة. احرص على عدم الخلط بين #include <filename> و

```
include=>context statement.
```

## الروتينات الفرعية مع GOSUB

في الإصدارات القديمة من Asterisk كان لديك الأمر Macro. تم إهمال هذا الأمر منذ زمن طويل لصالح GOSUB. سنوضح هنا كيفية إنشاء روتينات فرعية لمعالجة البريد الصوتي بطريقة سهلة ومنظمة. صيغة الأمر:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

الأمر GOSUB متاح منذ Asterisk 1.6 ويدعم تمرير الوسائط (المتاحة داخل الروتين الفرعي كـ `${ARG1}`، `${ARG2}`، وهكذا). باستخدام الوسائط، أصبح من الممكن استبدال أوامر Macro القديمة بالكامل. تم إزالة Macros (`app_macro`) في Asterisk 21؛ يجب عليك استخدام GOSUB للروتينات الفرعية.

### إنشاء الروتين الفرعي

التعريف مشابه جدًا. انظر إلى الروتين الفرعي أدناه المعرف للبريد الصوتي بالاسم stdexten (اختر الاسم الذي تفضله). بعد استدعاء الأمر Dial مع الوسيط الأول (اسم القناة) نتحقق من ${DIALSTATUS} لإرسال منطق المكالمة إلى الخطوة التالية.

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### استدعاء الروتين الفرعي

احرص عند استدعاء الروتين الفرعي على استخدام الأقواس قبل المعاملات.

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Using Asterisk DB

لتنفيذ تحويل المكالمات والقوائم السوداء، نحتاج إلى طريقة لتخزين البيانات واستعادتها. لحسن الحظ، يوفر Asterisk آلية لتخزين واسترجاع البيانات من قاعدة بيانات مدمجة تسمى AstDB. في إصدارات Asterisk الحديثة (بما فيها Asterisk 22) تُدعم AstDB بواسطة **SQLite3** (الملف `/var/lib/asterisk/astdb.sqlite3`)؛ بينما كان Asterisk 1.8 وما قبله يستخدم Berkeley DB v1. هذا يشبه قاعدة بيانات سجل Windows التي تستخدم مفهوم العائلة والمفاتيح الهرمية. تستمر البيانات في البقاء بين عمليات إعادة تشغيل Asterisk. واجهة برمجة التطبيقات للعائلة/المفتاح لم تتغير عن الخلفية القديمة؛ فقط تنسيق التخزين على القرص تغير.

### Functions, applications, and CLI commands

هناك بعض الدوال، التطبيقات، وأوامر سطر الأوامر التي تعمل مع AstDB:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

أمثلة:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

بعض التطبيقات يمكن استخدامها للتلاعب بـ AstDB:

- DB_DELETE(<family/key>) — دالة تُعيد وتحذف مفتاحًا واحدًا
- DBdeltree(<family>) — تطبيق يحذف عائلة/شجرة فرعية كاملة

التطبيق القديم `DBdel()` لم يعد موجودًا في Asterisk 22. احذف مفتاحًا واحدًا باستخدام دالة dialplan `DB_DELETE()` — مثال `Set(x=${DB_DELETE(family/key)})` أو، كعملية كتابة، `Set(DB_DELETE(family/key)=)`. ما زال `DBdeltree()` (حذف عائلة/شجرة فرعية كاملة) تطبيقًا متاحًا.

يمكن أيضًا استخدام أوامر سطر الأوامر لتعيين وحذف المفاتيح:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementing Call Forward, DND, and Blacklists

في هذا المثال، ستتعلم كيفية تنفيذ تحويل المكالمات الفوري وتحويل المكالمات عند الانشغال. سنستخدم *21* لبرمجة تحويل المكالمات الفوري و*61* لبرمجة تحويل المكالمات عند الانشغال. لإلغاء البرمجة، استخدم #21# و#61# على التوالي. استخدم المثال أعلاه لملء قاعدة البيانات. العائلات المستخدمة:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

جرّب ملء قاعدة البيانات بالاتصال:

- *21* (الامتداد الوجهة لتحويل المكالمات الفوري)
- *61* (الامتداد الوجهة لتحويل المكالمات عند الانشغال)
- *41* (الامتداد لتفعيل عدم الإزعاج)

استخدم أمر سطر الأوامر `database show` لرؤية العائلات، المفاتيح، والقيم المضافة.

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward, Blacklist, DND

الروتين الفرعي يتحقق مما إذا كانت قاعدة البيانات تحتوي على أزواج المفتاح:القيمة المقابلة لـ CFIM أو CFBS أو DND، ثم يتعامل معها بالشكل المناسب. الروتين الفرعي التالي يستدعي روتين الطلب:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Using a blacklist

تم **إزالة** تطبيق `LookupBlacklist()` القديم من Asterisk (اختفى مع آلية القفز legacy "priority+101"). في Asterisk 22 يمكنك بناء قائمة حظر مباشرة باستخدام دالة `DB_EXISTS()` (التي تختبر المفتاح وعند العثور تُظهر قيمته في `${DB_RESULT}`) بالإضافة إلى `GotoIf`. احفظ كل رقم محظور كمفتاح في عائلة `blacklist`، ثم تحقق من هوية المتصل في أعلى السياق الوارد الخاص بك:

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

يرجع `DB_EXISTS(blacklist/${CALLERID(num)})` القيمة `1` عندما يكون رقم المتصل موجودًا في قاعدة البيانات (مُحوِّلًا المكالمة إلى سياق `blocked`) ويُعيد `0` خلاف ذلك، وبالتالي تستمر المكالمة إلى `Dial()` العادي.

لإدراج رقم في قائمة الحظر، يمكننا استخدام نفس المورد كما في السابق، باستخدام *31* متبوعًا بالامتدادات التي تريد حظرها. لإزالة رقم من قائمة الحظر، يجب عليك استخدام #31# متبوعًا بالرقم المراد إزالته.

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

يمكنك أيضًا إدراج الأرقام في قائمة الحظر عبر واجهة سطر الأوامر (CLI) الخاصة بالكونسول:

```
*CLI>database put blacklist <name/number> 1
```

ملاحظة: يمكن ربط أي قيمة بالمفتاح. اختبار `DB_EXISTS()` يبحث عن المفتاح، وليس عن القيمة. لمسح الرقم من قائمة الحظر، يمكنك استخدام:

```
*CLI>database del blacklist <name/number>
```

## السياقات المستندة إلى الوقت

في الشكل التالي، لدينا مخطط طلب يحتوي على ثلاثة سياقات. سياق [incoming] هو المكان الذي تُستقبل فيه المكالمات عادةً. لقد أدرجنا أربع سطور تغير السلوك اعتمادًا على وقت النظام، كما هو موضح أدناه:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

يفصل Asterisk الحديث (بما في ذلك الإصدار 22) حقول time-include باستخدام **فواصل**، وليس الأنابيب. يتم تحليل الشكل القديم للأنابيب (`include => context|times|weekdays|mdays|months`) كاسم سياق حرفي عادي ويفشل بصمت في تطبيق أي شرط زمني.

خلال ساعات العمل العادية، سيتم إعادة توجيه المعالجة إلى mainmenu، حيث من المحتمل أن يتم استدعاء IVR للتعامل مع المكالمة الواردة. إذا حدثت المكالمة بعد ساعات العمل، فستستدعي الامتداد الأمني المحدد في المتغير ${SECURITY}. إذا لم يرد الامتداد الأمني على المكالمة، فسيتم إرسالها إلى بريد الصوت الخاص بالمشغل.

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Time-based messages using gotoiftime()

The GotoIfTime() syntax is shown below.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

In Asterisk 22 the field separator is a **comma**, not a pipe (the pipe form was deprecated in Asterisk 1.6). An optional `timezone` field is supported, and each branch label uses the usual `[[context,]extension,]priority` form.

This application can replace the time-based context and seems easier to understand and read. You can specify the time as follows:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Names for days and months are not case sensitive.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

The previous statement transfers the processing to the extension s in the normalhours context if the call is between 08:00AM and 06:00PM from Monday to Friday.

## Using DISA to get a new dial tone

DISA، أو “الوصول المباشر إلى النظام الداخلي”، هو نظام يسمح للمستخدمين بالحصول على إشارة اتصال ثانية. يتيح للمستخدمين إعادة الطلب إلى وجهة أخرى. يُستخدم غالبًا من قبل الفنيين عند إجراء مكالمات طويلة المسافة للدعم الفني في عطلات نهاية الأسبوع؛ بدلاً من الاتصال من منازلهم مباشرة إلى الوجهة، يتصلون برقم DISA الخاص بالمكتب، يحصلون على إشارة اتصال، ثم يتصلون بالوجهة. تُتحمل الشركة رسوم المكالمات الطويلة بدلاً من هاتف المنزل.

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

Example:

```
exten => s,1,DISA(no-password,default)
```

باستخدام العبارة السابقة، يقوم المستخدم بالاتصال بـ PBX و—دون الحاجة إلى أي كلمة مرور—يتلقى إشارة اتصال. أي مكالمة تستخدم DISA ستُعالج باستخدام سياق `default`. تشمل المعطيات لهذا التطبيق كلمة مرور عامة أو كلمة مرور فردية داخل ملف. إذا لم يُحدد سياق، يُفترض سياق `disa`. إذا استخدمت ملف كلمة مرور، يجب تحديد المسار الكامل. يمكن تحديد معرف المتصل للاتصال الخارجي عبر DISA أيضًا. Example:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

يستخدم Asterisk 22 الفواصل كفواصل للمعطيات (تم إهمال الشكل القائم على الأنابيب في الإصدار 1.6). المعطى الأول هو إما رمز مرور واحد أو مسار ملف رمز المرور، والسياق الافتراضي عندما لا يُعطى أي شيء هو `disa`.

## تحديد عدد المكالمات المتزامنة

تسمح لك الدالة GROUP() بحساب عدد القنوات النشطة التي لديك في مجموعة واحدة في نفس الوقت. مثال: لديك فرع في ريو دي جانيرو، حيث تتبع الهواتف النمط “_214X”. يتم خدمة هذا الموقع عبر خط مستأجر، مع تخصيص 64K لعرض النطاق الصوتي. في هذه الحالة، الحد الأقصى لعدد المكالمات المسموح بها هو 2 (G.729، حوالي 31.2K لكل مكالمة). لتحديد المكالمات إلى ريو إلى اثنتين:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail هو نظام إجابة هاتفية محوسب يسجل الرسائل الصوتية الواردة، ويحفظها على القرص أو يرسلها عبر البريد الإلكتروني. أحيانًا يحتوي على دليل يمكنك من خلاله البحث عن صناديق البريد الصوتي بالاسم. في الماضي، كانت أنظمة البريد الصوتي مكلفة جدًا. الآن، مع الاتصالات عبر IP، يصبح البريد الصوتي ميزة قياسية.

لتكوين البريد الصوتي، يجب عليك اتباع الخطوات التالية.

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — codec used to record the message (e.g., wav49, wav, gsm)
- `serveremail` — who the e-mail notification should appear to come from
- `maxmsg` — maximum number of messages in the mailbox; after this threshold, messages are discarded
- `maxsecs` — maximum length of a voicemail message, in seconds
- `minsecs` — minimum length of a message, in seconds; below this threshold, no message is recorded
- `maxsilence` — how many seconds of silence to treat as the end of the message

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

A mailbox is defined with one line per mailbox, in the form:

```
mailboxID => pincode,fullname,email,pager-email,options
```

The fields are:

- **MailboxID** — usually the extension number
- **Pincode** — password to access the voicemail system
- **Full name** — used by the directory application
- **E-mail** — address for voicemail notification
- **Pager e-mail** — address for notification via an SMS gateway or pager
- **Options** — per-mailbox options (the same options as in `[general]`, but applied to this mailbox)

Voicemail has several options that control its behavior. For now, we will stick to the default options and concentrate on the mailbox definition. After the `[general]` section in the file, you start configuring the mailbox IDs, each in its own context. Example:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

Please check for advanced options in the file `voicemail.conf`.

**Step 3: Configure the file `extensions.conf`.**

The `stdexten` subroutine shown earlier (under *Subroutines with GOSUB*) is exactly the call/voicemail handler you need here: it dials the extension and uses the value of the channel variable `${DIALSTATUS}` to redirect the call flow to the proper voicemail greeting (`b` for busy, `u` for unavailable). Call it with `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` from each extension in `extensions.conf`.

## Using the VoiceMailMain() application

The application voicemailmain() is used to configure the voicemail mailbox. Users can dial the application, record their greeting, and listen to their voicemail. To call the application in the dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Below you will find a list of the options available for the application.

### Voicemail application syntax

This application allows the calling party to leave a message for a specified list of mailboxes. When multiple mailboxes are specified, the greeting will be taken from the first specified mailbox. The dial plan execution will stop if the specified mailbox does not exist. The syntax is shown below:

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

In all cases, the beep.gsm file will be played before the recording begins. Voicemail messages will be stored in the inbox directory.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

If a caller presses 0 (zero) during the announcement, it will be moved to the ‘o’ (out) extension in the voicemail current context. This can be used to exit to the operator. If during the recording the caller presses # or the silence limit times out, recording is stopped and the call goes to the next priority. Make sure that you handle the call after the voicemail is played, as shown below.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

You may tag some messages as “urgent.” Two methods are available for this:

- Pass the option ‘U’ in the application voicemail()
- Specify review=yes in the file voicemail.conf. If using this option, the user will be able to tag the message as urgent after recording the voice instructions.

## إرسال البريد الصوتي إلى البريد الإلكتروني

في بعض الحالات (مثل حالتي)، لا نستخدم تطبيق voicemailmain() لقراءة البريد الإلكتروني. يكون من الأبسط والأكثر عملية إرسال جميع الرسائل إلى البريد الإلكتروني مع إرفاق الصوت. باستخدام المعاملين ‘attach’ و ‘delete’، يمكنك إرسال جميع الرسائل إلى البريد الإلكتروني وحذفها من صندوق البريد.

```
attach=yes
delete=yes
```

لإرسال البريد الصوتي إلى البريد الإلكتروني، يستخدم تطبيق voicemail وكيل نقل الرسائل (MTA)، وهو مكوّن من نظام التشغيل الخاص بك. يستخدم Debian برنامج Exim كـ MTA. يتم تعريف التطبيق الذي يرسل البريد الإلكتروني في المعامل ‘mailcmd’.

```
mailcmd =/usr/sbin/sendmail -t
```

في توزيعة Debian من لينكس، يكون MTA هو Exim. لتكوين Exim في Debian، استخدم:

```
dpkg-reconfigure exim4-config
```

يمكنك اختيار جعل MTA الخاص بك يرسل البريد الإلكتروني مباشرة عبر SMTP أو عبر smarthost (عادةً خادم البريد الخاص بشركتك). تحقق مع مسؤول البريد الإلكتروني عن أفضل طريقة لإرسال البريد من خادم Asterisk إلى خادم البريد الخاص بك.

## تخصيص رسالة البريد الإلكتروني

يمكنك التحكم في طريقة إرسال الرسائل عن طريق إعداد المتغيرات التالية: متغيرات موضوع البريد الإلكتروني ومحتوى البريد الإلكتروني:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

يتم بناء محتوى البريد الإلكتروني والموضوع من قالب تقوم بتحديده في قسم `[general]` من `voicemail.conf`. يمكنك تعديل كل من المحتوى والموضوع، لكن الحد الأقصى لحجم الرسالة هو 512 بايت. في القالب، يُدرج `\n` سطرًا جديدًا و`\t` علامة تبويب.

المثال `emailsubject` أدناه بسيط. المثال `emailbody` قريب جدًا من الإعداد الافتراضي؛ حيث يُظهر الافتراضي اسم المتصل CIDNAME فقط عندما لا يكون فارغًا، وإلا يُظهر رقم المتصل CIDNUM، أو "متصل غير معروف" عندما يكون كلاهما فارغًا.

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## واجهة الويب للبريد الصوتي

هناك برنامج نصي بلغة Perl في توزيع المصدر يُدعى `vmail.cgi`، يقع في `contrib/scripts/vmail.cgi` داخل شجرة مصدر Asterisk (لا يزال يُرفق مع Asterisk 22). الأمر `make install` لا يقوم بتثبيت هذه الواجهة؛ يجب تشغيل `make webvmail` من دليل المصدر. يتطلب هذا البرنامج النصي مفسّر أوامر Perl وخادم ويب (مثل Apache) مثبتين على الخادم.

```
make webvmail
```

الهدف `make webvmail` يثبت البرنامج النصي (setuid root) في دليل CGI الخاص بخادم الويب لديك (`HTTP_CGIDIR`) وينسخ الصور الداعمة من `images/*.gif` إلى `HTTP_DOCSDIR/_asterisk` (بشكل افتراضي `/var/www/html/_asterisk`). إذا لم تتطابق تلك المسارات مع تخطيط خادم الويب الخاص بك، حرّر المتغيّرين `HTTP_CGIDIR` و`HTTP_DOCSDIR` في ملف `Makefile` الأعلى قبل تشغيل الهدف.

## إشعار البريد الصوتي

يمكنك تكوين البريد الصوتي لإرسال رسالة إشعار إلى هاتفك عندما يكون لديك بريد صوتي جديد. في Asterisk 22، يعمل مؤشر انتظار الرسائل (MWI) مع هواتف PJSIP و SIP وكذلك هواتف DAHDI. للإشارة إلى بريد صوتي غير مسموع، قد يومض ضوء المؤشر أو قد يصدر الهاتف نغمة إغلاق. تحتاج إلى تكوين صندوق البريد في ملف تكوين القناة المقابل. مثال: `pjsip.conf` (في قسم endpoint):

```
mailboxes=8590
```

في PJSIP يتم تعيين تلميح صندوق البريد باستخدام خيار `mailboxes` داخل قسم endpoint في `pjsip.conf`، بدلاً من `mailbox=` القديم في `sip.conf`. يتم التعامل مع اشتراكات MWI بواسطة وحدة `res_pjsip_mwi`.

![واجهة الويب لـ The Comedian Mail (`vmail.cgi`): تسجيل الدخول إلى Web-Voicemail في Asterisk — أدخل صندوق بريدك وكلمة المرور لتشغيل، حفظ، تحويل أو حذف البريد الصوتي من المتصفح. لا يزال يأتي مع Asterisk 22 ويتم تثبيته باستخدام `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### المختبر: إشعار الرسائل في الهاتف

تم اختبار هذا المختبر باستخدام softphone SIP.

1. حرر `pjsip.conf` وأضف `mailboxes=4401` في قسم endpoint للجهاز المسمى 4401.
2. حرر `extensions.conf` وأنشئ امتدادًا لتسجيل بريد صوتي إلى امتدادات 4401.

```
exten=9008,1,voicemail(4401,b)
```

3. انتقل إلى وحدة التحكم وأعد التحميل.
4. في SipPulse Softphone، افتح إعدادات حساب SIP ومكّن فحص البريد الصوتي (message-waiting) للحساب.
5. اطلب 9008 واترك رسالة.
6. راقب أيقونة الرسالة على الهاتف.

## استخدام تطبيق الدليل

هذا التطبيق يتيح لك العثور بسرعة على مستخدم للاتصال به. يتم جلب قائمة الأسماء والامتدادات المقابلة من ملف إعداد البريد الصوتي voicemail.conf. يمكن إظهار صياغة التطبيق باستخدام الأمر core show application directory:

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### مختبر: استخدام تطبيق الدليل

1. حرّر ملف voicemail.conf لإضافة امتدادين في مخطط الاتصال

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. أنشئ هذه الامتدادات في مخطط الاتصال الخاص بك

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. انتقل إلى وحدة التحكم وأعد التحميل
4. اطّلق 9006 وسجّل اسماً لكل امتداد (4400، 4401)
5. اطّلق 9007 واختر الأحرف الثلاثة من اسم العائلة لامتداد واحد (Eas=327). إذا كان هذا هو الخيار الصحيح، اضغط ‘1’ للتحويل إلى الاسم.

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## ملخص

في هذا الفصل، تعلمت كيفية استقبال المكالمات باستخدام IVR أو موظف تلقائي. درست مفهوم تضمين السياق ونفذت بعض الأمثلة. تم استخدام الروتينات الفرعية لتجنب الكتابة المتكررة، واُستخدم قاعدة بيانات Asterisk (AstDB، المدعومة بـ SQLite3 في Asterisk 22) للوظائف التي تتطلب تخزين البيانات (مثل تحويل المكالمات، عدم الإزعاج، القوائم السوداء). أخيرًا، تعلمت كيفية تنفيذ سلوك ما بعد ساعات العمل ونفذت مخطط طلب كامل باستخدام هذه المفاهيم.

## Quiz

1. A time-dependent context include uses the form `include => context,<times>,<weekdays>,<mdays>,<months>`. What does `include => normalhours,08:00-18:00,mon-fri,*,*` do?
   - A. Execute the extensions Monday to Friday, 08:00 to 18:00
   - B. Execute the options every day in all months
   - C. Nothing; the format is invalid
2. In modern Asterisk (including Asterisk 22), the fields of a time-based `include =>` and of `GotoIfTime()` are separated by which character?
   - A. The pipe `|`
   - B. The comma `,`
   - C. The semicolon `;`
   - D. The slash `/`
3. To dial several channels at once (ringing them simultaneously), you separate them inside `Dial()` with the ___ character.
4. A voice menu that plays a prompt while waiting for the caller to dial an extension is usually created with the ___ application.
5. You can include the contents of another file inside `extensions.conf` using the ___ statement (note: this is different from the `include =>` context statement).
6. In Asterisk 22, the built-in AstDB database is backed by:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. When you use `Dial(type1/identifier1&type2/identifier2)`, Asterisk dials each channel in sequence, waiting 20 seconds between them.
   - A. False
   - B. True
8. With the Background() application, you must wait until the message finishes playing before you can press a DTMF digit to choose an option.
   - A. False
   - B. True
9. Given the syntax `Goto([[context,]extension,]priority)`, which of the following are valid invocations of the Goto() application? (mark all that apply)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. To delete a single key from AstDB in the Asterisk 22 dial plan, you use:
    - A. The `DBdel()` application
    - B. The `DB_DELETE()` function
    - C. The `DBdeltree()` application
    - D. The `LookupBlacklist()` application

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
