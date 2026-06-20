# Call Queues

تُعَدّ قوائم الانتظار للمكالمات، المعروفة أيضًا باسم ACD (التوزيع التلقائي للمكالمات)، ذات أهمية متزايدة في الرد على مكالمات العملاء بكفاءة. يمكن لموزع المكالمات التلقائي أن يساعد في خفض التكاليف، وزيادة مستوى الخدمة، وتحسين المبيعات حيث إن موزعات المكالمات تؤثر على طريقة عمل عملك—not for a few days, but for many years. في بيئة مركز الاتصال، العامل الأول هو الناس؛ فهم أغلى مورد. يتطلب توظيف الوكلاء وتدريبهم وتحفيزهم وقتًا، ومالًا، وصبرًا. باستخدام ACD، يمكنك تعظيم إنتاجية الوكلاء من خلال تحديد عدد الوكلاء المطلوب بدقة، والتحكم في الحضور الجيد والسيء، وتحليل تدفق المكالمات.

## Objectives

By the end of this chapter, you should be able to:

- Understand why and how to use call queues
- Understand the basic theory of call queues
- Install and configure the queue system

## كيف تعمل قوائم الانتظار؟

قوائم الانتظار ليست بالضرورة ابتكارًا جديدًا. عندما يكون لديك تدفق مكالمات واردة عالي، يصبح من الصعب توزيع المكالمات بشكل مناسب. استخدام استراتيجية مجموعة حيث يرن الهاتف على جميع الوكلاء في آن واحد لا يبدو فعالًا، إلا إذا كان لديك عدد قليل من الوكلاء. ومع ذلك، تقوم قائمة الانتظار بتسليم المكالمات إلى وكيل متاح واحد فقط في كل مرة وتضع العميل في وضع الانتظار مع الموسيقى عندما لا يكون هناك وكلاء متاحين. تعمل القائمة عن طريق الاحتفاظ بالمكالمة أثناء البحث عن وكيل غير مشغول للرد عليها. أحد أكبر فوائد القائمة هو تجنب فقدان المكالمات مع إتاحة إمكانية توليد إحصاءات.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

عادةً، تعمل قائمة الانتظار على النحو التالي:

- يقوم الوكلاء بتسجيل الدخول إلى القائمة.
- تُضع المكالمات الواردة في قائمة الانتظار.
- تُستخدم استراتيجية قائمة الانتظار لتوزيع المكالمات على الوكلاء.
- تُشغل موسيقى الانتظار بينما ينتظر المتصل.
- يمكن تقديم إعلانات للمتصلين، تُعلمهم بوقت الانتظار.
- يرد الوكيل على المكالمة وتُولد الإحصاءات.

التطبيق الرئيسي للقوائم هو خدمة العملاء. عند استخدام القوائم، تتجنب فقدان المكالمات عندما يكون وكلاؤك مشغولين. يمكنك إضافة وكلاء جدد إلى القائمة إذا لاحظت أن عدد المتصلين في القائمة يزداد. ميزة أخرى للقوائم هي إمكانية الحصول على إحصاءات مثل معدل التخلي عن المكالمة، متوسط مدة المكالمة، وهدف الرد على المكالمات. ستساعدك هذه الإحصاءات في تحديد عدد الوكلاء اللازم لتقديم خدمة أفضل لعملائك.

### بنية ACD

تتكون بنية ACD من القوائم والوكلاء. يمكن أن يكون الوكيل في قائمتين في نفس الوقت. يمكن أن تحتوي القائمة على وكلاء، قنوات، ومجموعات وكلاء.

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Queues are defined in the queues.conf configuration file. Agents are attendants who log in and are members of queues. Agents are defined in the agents.conf file. The queue system has grown significantly over many releases, making the configuration file extensive. We will explain some of the major parameters. One general parameter worth highlighting is `autofill`:

```
autofill=yes
```

The old behavior for the queue was serial type. The queue waited for a call to be dispatched before sending the succeeding call to the next agent. If an agent takes 15 seconds to answer a call, the other calls in the queue had to wait until that call was answered. For high-volume queues, this behavior was inefficient. The new behavior autofill=yes does not wait until a call is answered, but rather works in parallel. You can record the calls in the queue using the option mixmonitor. In this mode, calls are recorded and mixed at the same time.

### Queue configuration file

Queues are configured in the queues.conf file. In the figure, you will find a working example of a queue.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

You can configure your agents in the file agents.conf. Agents can log in from any extension to receive calls. You can dial an agent using:

```
Dial(agent/<name>)
```

#### Agent login

The login flow for Agent 300 works like this:

- The user dials an extension that runs the `AgentLogin()` application.
- `AgentLogin()` is executed and the agent is associated with the current channel.
- You can check the status of the agents using the command `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

You can define the agents in the file agents.conf

```
; Agent configuration
[general]
persistentagents=yes
[agents]
autologoff=15
autologoffunavail=yes
ackcall=no
endcall=yes
wrapuptime=5000
musiconhold => default
;
;This section contains the agent definitions, in the form:
;
; agent => agentid,agentpassword,name
;
agent => 300,300
agent => 301,301
```

### Members

Members are active channels responding to the queue. Members can be direct channels (PJSIP, DAHDI) or agents who log in before receiving calls.

### Strategies

Calls are distributed among members according to one of these strategies:

- ringall: Plays all channels available until someone answers.
- leastrecent: Distributes to the least recent member.
- fewestcalls: Distributes to the member with fewest calls.
- random: Ring random interface.
- wrandom: Ring random interface, but use the member’s penalty as a weight when calculating their metric.
- rrmemory: Uses round robin with memory; it remembers where it left off with the call in the last pass.
- rrordered: Same as rrmemory, except the queue member order from the config file is preserved.
- linear: Rings members in the order they are listed in queues.conf; for dynamic members, in the order they were added.

The older `roundrobin` strategy was deprecated back in Asterisk 1.4. It is no longer a documented strategy and should not be used: in Asterisk 22 the parser still accepts the word `roundrobin`, but only as a backward-compatibility alias that maps to `rrmemory`. Use `rrmemory` (or `rrordered`) explicitly instead. The list above is the set of documented strategies for the `strategy` option in the Asterisk 22 `queues.conf`.

## Agents

Agents are implemented as proxy channels. They can be used inside the queues. Another use for the agent channels is extension mobility. The user can log in using any phone and receive its calls. This allows a user to go to any room to make it an office. You can dial an agent in the dial plan using dial(agent/<name>). You define agents in the agents.conf file.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

You may choose to use agent groups. This function does not take ACD strategies into consideration. You will probably prefer to list all agents individually. If you want to transfer to an agent group, you can use `queues.conf`:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Agents are defined in the file agents.conf. Below is a working example of the file.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## التطبيقات المتعلقة بـ ACD

نظام قوائم الانتظار في Asterisk يوفر عدة تطبيقات لتنفيذ القوائم في مخطط الاتصال. أدناه نعرض بعضًا منها.

### التطبيق queue()

هذا التطبيق يضع المكالمات الواردة في قائمة انتظار معينة كما هو معرف في queues.conf. قد يحتوي سلسلة الخيارات على صفر أو أكثر من الخيارات أحرف واحدة (الموضحة في الشكل أدناه). بالإضافة إلى تحويل المكالمة، يمكن إيقاف المكالمة مؤقتًا ثم التقاطها من قبل مستخدم آخر. سيتم إرسال عنوان URL الاختياري إلى الطرف المتصل إذا كان القناة تدعمه. المعامل الاختياري AGI سيُعدّ سكريبت AGI ليُنفّذ على قناة الطرف المتصل بمجرد ربطه بعضو في القائمة. سيؤدي انتهاء المهلة إلى فشل القائمة بعد عدد محدد من الثواني، يتم التحقق منه بين كل دورة مهلة وإعادة محاولة. هذا التطبيق يضبط متغيّر الحالة QUEUE عند الانتهاء:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### التطبيق agentlogin()

هذا التطبيق يطلب من الوكيل تسجيل الدخول إلى النظام. دائمًا ما يُعيد -1. أثناء تسجيل الدخول، سيسمع الوكيل الذي يتلقى المكالمات صوت صفارة عندما تأتي مكالمة جديدة. يمكن للوكيل إنهاء المكالمة بالضغط على المفتاح *.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### التطبيق addQueueMember()

هذا التطبيق يضيف جهازًا (مثل PJSIP/3000) إلى قائمة الانتظار بشكل ديناميكي. إذا كان الجهاز موجودًا بالفعل، سيُعيد خطأ.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### التطبيق removeQueueMember()

هذا التطبيق يزيل جهازًا من القائمة بشكل ديناميكي. إذا لم يكن الجهاز جزءًا من القائمة، سيُعيد خطأ.

```
RemoveQueueMember(queuename[|interface])
```

### التطبيقات الداعمة وأوامر CLI

بعض التطبيقات وأوامر وحدة التحكم يمكنها المساعدة في العمل مع القوائم. يوضح ما يلي ما يفعله كل تطبيق:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## مهام التكوين

تلخص الصورة أدناه المهام الرئيسية لإنشاء نظام طابور عمل.

![مهام تكوين ACD: (1) إنشاء طابور المكالمات (مطلوب)، (2) تعريف معلمات الوكيل (اختياري)، (3) إنشاء الوكلاء (اختياري)، (4) وضع الطابور في مخطط الاتصال (مطلوب)، (5) تكوين تسجيل الوكيل (اختياري)، و (6) التحقق باستخدام agent show all و queue show (اختياري)](../images/14-queues-fig10.png)

الخطوة 1: إنشاء طابور المكالمات في ملف queues.conf:

```
[telemarketing]
music = default
;announce = queue-telemarketing
;context = qoutcon
timeout = 2
retry = 2
maxlen = 0
member => Agent/300
member => Agent/301
[auditing]
music = default
;announce = queue-auditing
;context = qoutcon
timeout = 15
retry = 5
maxlen = 0
member => Agent/600
member => Agent/601
```

الخطوة 2: تعريف معلمات الوكيل في ملف agents.conf:

```
debian:/etc/asterisk# cat agents.conf
;
; Agent configuration
;
[agents]
; Define maxlogintries to allow agent to try max logins before
; failed.
; default to 3
maxlogintries=5
; Define autologoff times if appropriate.  This is how long
; the phone has to ring with no answer before the agent is
; automatically logged off (in seconds)
autologoff=15
; Define autologoffunavail to have agents automatically logged
; out when the extension that they are at returns a CHANUNAVAIL
; status when a call is attempted to be sent there.
; Default is "no".
;autologoffunavail=yes
; Define ackcall to require an acknowledgement by '#' when
; an agent logs in using agentcallbacklogin.  Default is "no".
;ackcall=no
; Define endcall to allow an agent to hangup a call by '*'.
; Default is "yes". Set this to "no" to ignore '*'.
;endcall=yes
; Define wrapuptime.  This is the minimum amount of time when
; after disconnecting before the caller can receive a new call
; note this is in milliseconds.
;wrapuptime=5000
; Define the default musiconhold for agents
; musiconhold => music_class
;musiconhold => default
;
; Define the default good bye sound file for agents
; default to vm-goodbye
;agentgoodbye => goodbye_file
; Define updatecdr. This is whether or not to change the source
; channel in the CDR record for this call to agent/agent_id so
; that we know which agent generates the call
;updatecdr=no
;
; Group memberships for agents (may change in mid-file)
;
;group=3
;group=1,2
;group=
```

الخطوة 3: إنشاء الوكلاء في ملف agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

الخطوة 4: إدراج الطابور في مخطط الاتصال، في الملف `extensions.conf`:

```
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### تكوين تسجيل الطابور

يمكن تسجيل المكالمات باستخدام تطبيق MixMonitor الخاص بـ Asterisk. (تم إزالة تطبيق Monitor المستقل في Asterisk 22، وخيار queues.conf `monitor-type` الآن يقبل فقط MixMonitor.) يمكن تمكين التسجيل من داخل تطبيق الطابور، بدءًا عندما يتم الرد على المكالمة فعليًا. تُسجل المكالمات الناجحة فقط، ولا يتم إجراء أي تسجيلات أثناء استماع الأشخاص إلى MOH. لتمكين المراقبة، ما عليك سوى تحديد monitor-format. هذه الميزة غير مفعلة بخلاف ذلك. يمكنك تعيين اسم الملف للتسجيل باستخدام `Set(MONITOR_FILENAME=<filename>)`؛ وإلا سيستخدم `MONITOR_FILENAME=${UNIQUEID}`.

في ملف queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## تشغيل الصف

الأمثلة التالية توضح كيفية استخدام الصف.

1. تسجيل دخول الوكيل. مثال: وكيل في صف التسويق الهاتفي يرفع السماعة ويطلب #9000. يسمع الوكيل رسالة تسجيل دخول غير صالحة ويُطلب منه اسمه وكلمة المرور. يتبع صف التدقيق نفس الإجراء.
2. الصف. بمجرد الدخول إلى الصف، سيستمع الوكيل إلى موسيقى الانتظار إذا تم تعريفها. عندما يرد اتصال إلى صف التسويق الهاتفي، سيصدر صوت صفير للوكيل وسيتم ربطه بذلك الاتصال.
3. إنهاء المكالمة. عندما ينتهي الوكيل من المكالمة، يمكنه:
   - الضغط على ‘*’ للقطع والبقاء في الصف.
   - قطع الهاتف، وبالتالي قطع الاتصال بالصف.
   - الضغط على #8000 لتحويل المكالمة للتدقيق.

## موارد متقدمة

نظام طابور Asterisk يحتوي على بعض الميزات المتقدمة لتفضيل بعض العملاء والوكلاء بالإضافة إلى تمكين قائمة مستخدم.

### قائمة المستخدم

يمكنك تعريف قائمة لمستخدم أثناء الانتظار في الطابور باستخدام امتدادات ذات رقم واحد. لتمكين هذا الخيار، عرّف سياقًا في تكوين الطابور في ملف queues.conf.

### العقوبة

يمكن تكوين الوكلاء بعقوبة. سيُرسل الطابور المكالمات أولاً إلى المستخدمين الذين لديهم قيم عقوبة أقل. على سبيل المثال، بما أننا نعلم أن عملائنا يحبون سوزان وصوتها الناعم، قد نختار تعيين أولوية 0 لها. بدلاً من ذلك، الوكيل المسمى أوبير، الذي يملك خبرة أقل، يكون أقل تفضيلاً لخدمة العملاء؛ لذلك نُعطيه أولوية 10. في ملف queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### الأولوية

تعمل الطوابير في وضع FIFO (الأول يدخل أولاً يخرج). إذا أردت إعطاء أولوية لعملاء خاصين (بلاتيني، ذهبي) يمكنك إعداد أولويات متميزة. للعملاء البلاتينيين أو الذهبيين:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

العملاء الزرقاء:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## تم إزالة تطبيق agentcallbacklogin()

تم إهمال التطبيق `agentcallbacklogin()` من قبل Digium في Asterisk 1.4 (يوليو 2006) ولم يعد متاحًا في Asterisk 22. النهج الموصى به هو استخدام `AddQueueMember()` مع واجهة PJSIP لإضافة أعضاء بنمط الاسترجاع إلى قائمة الانتظار بشكل ديناميكي. تم تضمين المستند `queues-with-callback-members.txt` في أدلة Asterisk `/doc` القديمة لتوجيه عملية الترحيل.

تم أيضًا إزالة برنامج تشغيل القناة `chan_agent`؛ وقد أُعيد كتابة وظائفه في الوحدة `app_agent_pool`، وهي التي توفر `AgentLogin()`، `AgentRequest()` ووظيفة dialplan `AGENT()` في Asterisk 22 (هذه لا تزال موجودة — `app_agent_pool.so` تُشحن مع بناء 22 القياسي). بالنسبة لمراكز الاتصال الحديثة، فإن النمط القياسي هو تخطي قنوات الوكيل تمامًا وإضافة جهاز PJSIP الخاص بالوكيل مباشرة إلى القائمة باستخدام `AddQueueMember()`/`RemoveQueueMember()` (ثابتًا في `queues.conf`، أو ديناميكيًا من dialplan أو AMI). هذا أبسط، ويتكامل بشكل نظيف مع حالة جهاز PJSIP، وهو النهج المستخدم طوال هذا الفصل.

## إحصائيات الطابور

جميع الأحداث من الطوابير تُسجل في ‎/var/log/asterisk/queue_log. تم نشر تنسيق سجل الطابور في المستند ‎queuelog.txt‎ داخل دليل ‎/doc‎ من وثائق Asterisk. أدناه بعض أهم الأحداث المسجلة.

- ABANDON(position|origposition|waittime)
- AGENTDUMP
- AGENTLOGIN(channel)
- AGENTLOGOFF(channel|logintime)
- ATTENDEDTRANSFER(destexten|destcontext|holdtime|calltime|origposition)
- BLINDTRANSFER(extension|context|holdtime|calltime|origposition)
- COMPLETEAGENT(holdtime|calltime|origposition)
- COMPLETECALLER(holdtime|calltime|origposition)
- CONFIGRELOAD
- CONNECT(holdtime|bridgedchanneluniqueid)
- ENTERQUEUE(url|callerid)
- EXITEMPTY(position|origposition|waittime)
- EXITWITHKEY(key|position)
- EXITWITHTIMEOUT(position|origposition|waittime)
- QUEUESTART
- RINGNOANSWER(ringtime)
- SYSCOMPAT

يمكنك بناء أداة خاصة لمعالجة هذه الأحداث أو استخدام حزمة إحصائيات جاهزة للتنفيذ:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – حزمة تجارية تُصان بانتظام وتقوم بتحليل `queue_log` وتظل واحدة من أكثر أدوات التقارير اكتمالاً لمراكز اتصال Asterisk.
- **Roll your own** – لأن تنسيق `queue_log` أعلاه ثابت وموثّق جيداً، فمن السهل تحليله باستخدام سكربت صغير (Python، إلخ) وإدخال الأحداث إلى قاعدة بيانات أو لوحة معلومات.

لنهج أكثر توجهاً نحو الأحداث مقارنةً بمتابعة `queue_log`، تسمح **واجهة Asterisk REST (ARI)** وعمليات **AMI** `QueueSummary`/`QueueStatus` لك ببناء لوحات طابور حية وتكاملات مخصصة ضد حالة الطابور في الوقت الحقيقي بدلاً من تحليل السجلات بعد حدوثها. ARI هي الواجهة الحديثة المدعومة لهذا النوع من العمل في Asterisk 22.

## الملخص

في هذا الفصل تعلمت كيفية استخدام ACD، وهيكليته، وكيفية تكوينه. كما تم تقديم بعض الميزات المتقدمة مثل الأولويات والعقوبات.

## Quiz

1. أي من استراتيجيات توزيع الطابور التالية صالحة في `queues.conf` (اختر كل ما ينطبق)؟
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. يمكنك تسجيل محادثة بين الوكيل والعميل من داخل الطابور عن طريق ضبط خيار ___ في ملف `queues.conf`.
3. أي من `strategy` يرن للأعضاء بالترتيب الدقيق الذي تم إدراجهم به في `queues.conf`؟
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. عندما ينتهي الوكيل من المكالمة في مثال التسويق الهاتفي، أي من الإجراءات يمكنه اتخاذها (اختر كل ما ينطبق)؟
   - A. اضغط `*` لفصل الاتصال والبقاء في الطابور
   - B. إنهاء المكالمة وفصل الاتصال عن الطابور
   - C. اضغط `#8000` لتحويل المكالمة للتدقيق
   - D. اضغط `#` لتسجيل الخروج من جميع الطوابير فورًا
5. أي مهمتين *مطلوبتين* للحصول على طابور يعمل (اختر كل ما ينطبق)؟
   - A. إنشاء الطابور
   - B. إنشاء الوكلاء
   - C. تكوين معلمات الوكيل
   - D. تكوين التسجيل
   - E. وضع الطابور في مخطط الاتصال
6. في طابور المكالمات يمكنك تقديم قائمة رقمية أحادية يمكن للمتصل اختيارها أثناء الانتظار. يتم تمكين ذلك بتعريف ___ في قسم `queues.conf` الخاص بالطابور:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. تُستخدم تطبيقات الدعم `AddQueueMember()` و`RemoveQueueMember()` في ___ لإضافة أو إزالة الأعضاء أثناء التشغيل:
   - A. مخطط الاتصال
   - B. واجهة سطر الأوامر
   - C. queues.conf
   - D. agents.conf
8. بما أن chan_sip أُزيل في Asterisk 21، يجب أن يشير عضو الطابور الثابت إلى قناة مثل ___ بدلاً من `SIP/1001`.
9. المعامل `wrapuptime` هو الحد الأدنى للوقت بعد أن يفصل الوكيل المكالمة قبل أن يرسل الطابور لهذا الوكيل مكالمة جديدة.
   - A. True
   - B. False
10. يمكن إعطاء المتصل موقعًا أعلى في نفس الطابور عن طريق ضبط متغير القناة `QUEUE_PRIO` قبل استدعاء `Queue()`.
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin is not a documented strategy; in Asterisk 22 it survives only as a deprecated alias for rrmemory) · 2 — `monitor-format` (recording from the queue is enabled by specifying `monitor-format`; in Asterisk 22 `monitor-type` only supports MixMonitor) · 3 — C (linear) · 4 — A, B, C (`*` disconnects and stays; `#` is not a log-off-all key) · 5 — A, E · 6 — C (the `context` option) · 7 — A (the dial plan) · 8 — `PJSIP/1001` (any `PJSIP/` interface) · 9 — True · 10 — True
