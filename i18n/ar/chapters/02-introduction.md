# Introduction to Asterisk PBX

ازداد مؤخرًا انتشار توزيعات جاهزة للتشغيل مثل FreePBX و Issabel. في هذا الكتاب، سنتناول Asterisk الكلاسيكي، وهو الأساس لفهم هذه التوزيعات. Asterisk PBX هو برنامج مفتوح المصدر قادر على تحويل حاسوب شخصي عادي إلى نظام PBX متعدد البروتوكولات قوي. في هذا الفصل، سنتعرف على إمكانيات هذه التقنية الجديدة وهندستها الأساسية.

## الأهداف

- شرح ما هو Asterisk وما يفعله؛
- وصف دور Digium™ وشركتها التابعة Sangoma؛
- التعرف على بنية Asterisk الأساسية ومكوناتها؛
- الإشارة إلى عدة سيناريوهات استخدام؛ و
- تحديد مصادر المعلومات والمساعدة.

## ما هو Asterisk

Asterisk هو برنامج PBX مفتوح المصدر يحول جهاز كمبيوتر عادي إلى PBX متكامل للمستخدمين المنزليين، والمؤسسات، ومزودي خدمات VoIP، وشركات الهاتف. Asterisk هو أيضًا مجتمع مفتوح المصدر ومشروع برعاية Sangoma Technologies (التي استحوذت على Digium في عام 2018). يمكنك استخدام Asterisk وتعديله بحرية لتلبية احتياجاتك. يتيح Asterisk الاتصال في الوقت الحقيقي بين شبكات PSTN وVoIP. بما أن Asterisk أكثر من مجرد PBX، فليس فقط ستحصل على ترقية استثنائية لـ PBX الحالي لديك، بل يمكنك أيضًا القيام بأشياء جديدة في مجال الاتصالات، مثل:

- ربط الموظفين الذين يعملون من المنزل بـ PBX المكتب عبر الإنترنت عالي السرعة؛
- ربط عدة مكاتب في أماكن مختلفة عبر شبكة IP، أو شبكة خاصة، أو حتى عبر الإنترنت نفسه؛
- توفير بريد صوتي للموظفين مدمج مع الويب والبريد الإلكتروني؛
- بناء تطبيقات مثل IVRs تسمح بالاتصال بنظام الطلبات أو تطبيقات أخرى؛
- إعطاء المستخدمين المتنقلين إمكانية الوصول إلى PBX الشركة من أي مكان عبر اتصال إنترنت بسيط أو VPN؛ و
- المزيد الكثير....

يتضمن Asterisk عدة موارد متقدمة كانت في السابق موجودة فقط في الأنظمة عالية المستوى، مثل:

- موسيقى للعملاء في وضع الانتظار في قوائم المكالمات، تدعم بث الوسائط وملفات MP3؛
- قوائم المكالمات، حيث يمكن لفريق من الوكلاء الرد على المكالمات ومراقبة القوائم؛
- التكامل مع تحويل النص إلى كلام والتعرف على الصوت؛
- سجلات مفصلة تُنقل إلى كل من ملفات النص وقواعد بيانات SQL؛ و
- اتصال PSTN عبر الخطوط الرقمية والتناظرية.

## ما هو AsteriskNOW (تاريخيًا) و FreePBX

Asterisk في صوره النقية، المعروف أيضًا باسم “classic asterisk” (تسمية حزمة Debian) يُعتبر أكثر كأداة تطوير من كمنتج نهائي بحد ذاته. كان AsteriskNOW مبادرة لتحويل Asterisk إلى جهاز برمجي. شملت التوزيعة نظام التشغيل CentOS والواجهة الرسومية FreePBX. تم إيقاف AsteriskNOW منذ ذلك الحين.

اليوم، التوزيعة القياسية الجاهزة لـ Asterisk هي **FreePBX** (تُصان من قبل Sangoma)، التي تُدمج Asterisk مع واجهة إدارة ويب ونظام وحدات. تُرخص FreePBX وفقًا لرخصة GPL ويمكن تنزيلها بحرية من www.freepbx.org. بالنسبة للنشر التجاري، تقدم Sangoma أيضًا **FreePBX Distro** (صورة لينكس كاملة) ومنتجها التجاري **PBXact**.

## دور Digium™ و Sangoma

Digium، شركة تقع في هنتسفيل، ألاباما، كانت المُبدِعة والمطوِّرة الأساسية لـ Asterisk منذ تأسيسها في عام 1999. بالإضافة إلى كونها الراعي الرئيسي لتطوير Asterisk، قامت Digium بإنتاج بطاقات واجهة الهاتفية ومعدات أخرى لـ Asterisk PBXs، وأنشأت منتجات تجارية مثل Switchvox (المستهدفة لسوق الشركات الصغيرة والمتوسطة). في عام 2018، تم الاستحواذ على Digium من قبل **Sangoma Technologies**، شركة كندية للاتصالات الموحدة. منذ الاستحواذ، استمرت Sangoma في رعاية تطوير Asterisk وتعمل كالمسؤول الأساسي عنها، محافظةً على المشروع المفتوح المصدر على www.asterisk.org.

تاريخيًا، قدمت Digium Asterisk تحت ثلاثة أنواع من اتفاقيات الترخيص:

- General Public License (GPL) Asterisk. هذا هو الإصدار الأكثر استخدامًا. يتضمن جميع الميزات وهو مجاني للاستخدام والتعديل وفقًا لشروط ترخيص GPL.
- Asterisk Business Edition كان نسخة تجارية من Asterisk. استخدمت بعض الشركات النسخة التجارية لأنها لم ترغب أو لا تستطيع استخدام ترخيص GPL—عادةً لأنها لا تريد نشر شفرتها المصدرية مع Asterisk. **ملاحظة:** تم إيقاف Asterisk Business Edition؛ اليوم يتم توزيع Asterisk فقط تحت ترخيص GPL.
- ترخيص Asterisk OEM. بعد أن توقفت Digium عن بيع Asterisk Business Edition في المتاجر، استمرت في ترخيص تلك النسخة التجارية لعملاء OEM — بائعي المعدات الذين يرغبون في بناء منتجات مملوكة على أساس Asterisk دون نشر شفرتهم المصدرية تحت GPL.

### مشروع Zapata وعلاقته بـ Asterisk

تم تطوير مشروع Zapata بواسطة Jim Dixon، الذي كان أيضًا مسؤولًا عن التصميم الثوري للمعدات المستخدمة مع Asterisk. المعدات مفتوحة المصدر أيضًا؛ وبالتالي يمكن لأي شركة استخدامها، واليوم ينتج عدة مصنعين بطاقات متوافقة مع هذه البنية.

أنتج مشروع Zapata بنية تسمى Zaptel، ثم أعيد تسميتها إلى DAHDI (Digium/Asterisk Hardware Device Interface). أحد الفوائد الرئيسية لهذه البنية هو القدرة على استخدام وحدة المعالجة المركزية للكمبيوتر (PC CPU) لمعالجة تدفق الوسائط، وإلغاء الصدى، والتحويل بين الصيغ. على النقيض من ذلك، تستخدم معظم البطاقات الحالية معالجات إشارة رقمية (DSP) لأداء هذه المهام. استخدام PC CPU بدلاً من DSP مخصص يقلل بشكل كبير من سعر اللوحة. وبالتالي، تكون هذه البطاقات أرخص بكثير من الواجهات المتوفرة سابقًا من قبل مصنّعين آخرين. من ناحية أخرى، تتطلب هذه البطاقات الكثير من وحدة المعالجة المركزية؛ يمكن أن يؤدي سوء استخدام PC CPU إلى تأثير كبير على جودة الصوت. مؤخرًا، أطلقت Digium بطاقة معالج مساعد تستخدم DSPs لتشفير وفك تشفير G.729 و G.723، مما يسمح بقدرة توسعية أفضل لعدد كبير من القنوات.

## لماذا Asterisk؟

أتذكر أول اتصال لي بـ Asterisk. عادةً، تكون الاستجابة الأولى لشيء جديد—وخاصة شيء ينافس ما تعرفه بالفعل—هي رفضه! وهذا بالضبط ما حدث في عام 2003. كان Asterisk ينافس حلاً كنت أبيعها لعميل (بوابة VoIP E1 4)، وكان أقل تكلفة بعشر مرات مما كنت أفرضه على الحل الذي كنت أعرفه. هذا الفارق السعري الكبير دفعني إلى دراسة Asterisk لتحديد العوائق والسلبيات المحتملة. على سبيل المثال، وجدت أن معالج الحاسوب في ذلك الوقت لن يدعم 120 جلسة g.729 متزامنة، وفي النهاية فزت بالمقترح بحل البوابة الخاص بي.

مع ذلك، قادني هذا التمرين إلى اكتشاف أن Asterisk يمكنه حل مجموعة متنوعة من المشكلات المكلفة للغاية لعملائي. كنا نواجه صعوبات مع عروض أسعار باهظة للـ IVR، والرسائل الموحدة، وتسجيل المكالمات، والدوائر الآلية؛ ومع التخطيط المناسب، يمكن تجاوز مشاكل المعالج. في الواقع، خلال ثلاث سنوات فقط أصبح Asterisk المنتج الرائد في شركتي (قررت فعليًا فتح شركة أخرى مخصصة لأعمال Asterisk). في رأيي، Asterisk ثورة في مجال الاتصالات تمثل للاتصالات عبر IP ما تمثله Apache لخدمات الويب.

### خفض التكلفة بشكل كبير

إذا قارنت نظام PBX تقليدي بـ Asterisk فيما يتعلق بالواجهات الرقمية والهواتف، فإن Asterisk يكون أقل تكلفة قليلاً من تلك الأنظمة. ومع ذلك، يثبت Asterisk قيمته الحقيقية عندما تضيف ميزات متقدمة مثل البريد الصوتي، ACD، IVR وCTI. مع هذه الميزات المتقدمة، يصبح Asterisk أقل تكلفة بشكل ملحوظ من أنظمة PBX التقليدية. في الواقع، مقارنة أنظمة PBX القائمة على Asterisk بأنظمة PBX تناظرية منخفضة المستوى غير عادلة لأن Asterisk يقدم العديد من الميزات غير المتوفرة في الأنظمة التناظرية منخفضة المستوى.

### التحكم في نظام الهاتف والاستقلالية

أحد الفوائد التي يذكرها العملاء كثيرًا بشأن Asterisk هي الاستقلالية التي يوفرها. بعض المصنعين اليوم لا يمنحون العميل حتى كلمة مرور النظام أو وثائق التكوين. مع نهج “افعلها بنفسك” في Asterisk، يحصل المستخدم على حرية كاملة؛ وكميزة إضافية، يحصل المستخدم على واجهة قياسية.

### بيئة تطوير سهلة وسريعة

يمكن توسيع Asterisk باستخدام لغات سكريبت مثل PHP وPerl عبر واجهات AMI وAGI. Asterisk مفتوح المصدر، ويمكن للمستخدم تعديل شفرة المصدر. تُكتب شفرة المصدر في الغالب بلغة ANSI C.

### غني بالميزات

يحتوي Asterisk على عدة ميزات إما غير موجودة أو اختيارية في أنظمة PBX التقليدية (مثل البريد الصوتي، CTI، ACD، IVR، الموسيقى الاحتياطية المدمجة، والتسجيل). تكاليف هذه الميزات في بعض المنصات تتجاوز سعر المنصة نفسها.

### محتوى ديناميكي على الهاتف

يُبرمج Asterisk باستخدام لغة C ولغات أخرى شائعة في بيئات التطوير الحديثة. إمكانية توفير محتوى ديناميكي تكاد تكون لا حدود لها.

### مخطط طلبات (dial plan) مرن وقوي

اختراق آخر في Asterisk هو مخطط الطلبات القوي. في أنظمة PBX التقليدية، حتى الميزات البسيطة مثل توجيه أقل تكلفة (LCR) إما غير ممكنة أو اختيارية. مع Asterisk، يصبح اختيار أفضل مسار سهلًا ونظيفًا.

### مفتوح المصدر يعمل على Linux

أحد أعظم ميزات Asterisk هو مجتمعه. تتوفر عدة موارد، بما في ذلك وثائق Asterisk الرسمية (docs.asterisk.org)، ويكي VoIP-Info الذي يُديره المجتمع (www.voip-info.org <http://www.voip-info.org>)، قوائم توزيع البريد الإلكتروني، والمنتديات. مع تزايد اعتماد Asterisk، يتم اكتشاف الأخطاء وإصلاحها بسرعة. بفضل قاعدة مستخدمين كبيرة وفريق تطوير نشط، يُعد Asterisk من أكثر منصات PBX اختبارًا في العالم، مما يساعد على الحفاظ على استقرار ونضج قاعدة الشيفرة.

### قيود بنية Asterisk

بعض القيود في Asterisk تنبع من استخدام تصميم Zapata للاتصالات. في هذا التصميم، يستخدم Asterisk معالج الحاسوب لمعالجة قنوات الصوت بدلاً من معالجات الإشارة الرقمية (DSP) المخصصة، وهي شائعة في منصات أخرى. على الرغم

## الاعتراضات الرئيسية على Asterisk PBX

من الشائع سماع الاعتراضات على اعتماد Asterisk، والتي سنعالجها هنا.

### حصة السوق لـ Asterisk صغيرة جدًا

عادةً ما تُقاس حصة السوق بعدد أنظمة PBX المباعة. تُستخلص هذه الإحصاءات عمومًا من أكبر الموزعين. Asterisk هو برنامج مجاني يمكن تنزيله ونشره دون تسجيل أي عملية بيع، لذا يتم احتسابه بشكل منهجي أقل في تلك الأرقام. ومع ذلك، يقدّم Asterisk قاعدة مثبتة كبيرة جدًا على مستوى العالم — من أنظمة PBX المكتبية ذات الخادم الواحد إلى عمليات النشر الكبيرة للناقلين ومراكز الاتصال — ولا يزال المحرك السائد وراء نظام PBX مفتوح المصدر (بما في ذلك التوزيعات الجاهزة مثل FreePBX).

### إذا كان مجانيًا، كيف يبقى المُصنِّع على قيد الحياة؟

في الواقع، لا وجود لما يُسمّى مُصنِّع برمجيات مفتوحة المصدر بالمفهوم التقليدي. طوّرت Digium Asterisk منذ عام 1999، واعتمدت على مبيعات بطاقات واجهة الهاتف، ومنتجات PBX التجارية مثل Switchvox، والبرمجيات ذات الصلة. في عام 2018، استحوذت Sangoma Technologies على Digium. تواصل Sangoma تمويل تطوير Asterisk وتولّد إيرادات من خلال المنتجات التجارية (وحدات FreePBX التجارية، PBXact، Switchvox)، ومبيعات الأجهزة، والخدمات المهنية.

### من الصعب العثور على دعم فني!

توفر Sangoma دعمًا فنيًا تجاريًا لـ Asterisk عبر نظام شركائها ومباشرةً من خلال عروض منتجاتها. شبكة عالمية من المتخصصين المعتمدين تقدم الدعم الأولي والخدمات المهنية. يظل الدعم المجتمعي نشطًا عبر منتديات Asterisk وقوائم البريد على www.asterisk.org.

### هل يدعم Asterisk أكثر من 200 امتداد؟

نعم، بالتأكيد. يمكن لخادم Asterisk مُصمم جيدًا أن يتعامل مع عدد كبير من الامتدادات، ويُوسّع Asterisk أكثر عبر توزيع المستخدمين على عدة خوادم مع موازنة الأحمال والاحتياطي، مما يسمح بنشر متعدد المواقع على نطاق واسع.

### فقط “المهووسون” قادرون على تثبيت Asterisk

مع FreePBX (المتوفر كتوزيعة مستقلة من Sangoma)، حتى المتخصصين ذوي المعرفة المحدودة بنظام Linux يستطيعون تثبيت وتكوين PBX متوسط التعقيد. بفضل واجهة المستخدم الرسومية، يمكن تكوين نظام PBX كامل في بضع ساعات فقط.

### ماذا لو فشل الخادم؟

أحد المزايا الرئيسية لـ Asterisk هو قدرته على العمل في أنظمة مقاومة للأخطاء. من السهل نسبيًا وغير مكلف أن يكون هناك خادمان يعملان بالتوازي. أتحداك أن تجرب ذلك مع PBX تقليدي!

### شركتنا لا تستخدم برمجيات مفتوحة المصدر

من المحتمل أن شركتك تستخدم برمجيات مفتوحة المصدر دون أن تدرك ذلك. تستخدم العديد من الأجهزة Linux كنظام تشغيل لها. علاوةً على ذلك، يتوفر الدعم التجاري والنشر المُدار من Sangoma وشبكة شركائها المعتمدين.

### استخدام وحدة معالجة الكمبيوتر لمعالجة الإشارات والوسائط غير مُستحسن

يستخدم Asterisk وحدة معالجة الخادم لمعالجة الإشارات والوسائط لقنوات الصوت بدلاً من الاعتماد على DSP مخصص. على الرغم من أن ذلك يسمح بتقليل التكلفة حتى خمس مرات، إلا أنه يجعل النظام يعتمد على أداء وحدة المعالجة الرئيسية. مع التصميم الصحيح، يستطيع Asterisk التعامل مع أحجام كبيرة. إذا كنت لا تزال ترغب في إخلاء وحدة المعالجة الرئيسية من هذه المهام، يمكنك أيضًا استخدام إلغاء الصدى بالأجهزة وحتى بطاقات التحويل، مثل بطاقة Sangoma (سابقًا Digium) TC400B القائمة على DSPs.

## Asterisk Architecture

This section will explain how Asterisk’s architecture works. The figure below shows the basic Asterisk architecture. Next, we will explain architecture-related concepts, including channels, codecs, and applications.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

A channel is the equivalent of a telephone line, but in a digital format. It usually consists of an analog or digital (TDM) signaling system or a combination of codec and signaling protocol (e.g., SIP-GSM, IAX-uLaw). Initially, all telephony connections were analog and susceptible to echo and noise. Later, most systems were converted to digital systems, with the analogical sound converted into a digital format using pulse code modulation (PCM) in most cases. This format allows voice transmission in 64 kilobits/second without compression.

Channels interfacing with the Public Switched Telephone Network (PSTN):

- `chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards from Sangoma (formerly Digium), Xorcom, and others. Built separately against DAHDI — see the *Legacy channels* chapter.

Channels interfacing with Voice over IP:

- `chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS. Dial string: `PJSIP/endpoint_name`. (**Note:** the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22. See *Building your first PBX with PJSIP* for configuration.)
- `chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy; SIP/PJSIP is preferred for new deployments. Dial string: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support) but rarely used.

The older VoIP channels are no longer part of a standard Asterisk 22 build: `chan_h323` (H.323) survives only as the community `ooh323` add-on, and `chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set. If you must interwork with those protocols, a gateway in front of Asterisk is the usual approach.

Miscellaneous channels:

- **Local**: a pseudo-channel (built into the core) that loops back into the dial plan in a different context — useful for recursive routing and for fanning a call out to multiple destinations. Dial string: `Local/extension@context`.

### Codec and codec translation

We usually try to put as many voice connections as possible in a data network. Codecs enable new features in digital voice, including compression, which is one of the most important features as it allows compression rates larger than 8 to 1. Many codecs also define features such as voice activity detection (silence suppression), packet loss concealment, and comfort noise generation, though Asterisk itself does not generate comfort noise or perform silence suppression. Several codecs are available for Asterisk and can be transparently translated from one to another. Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another. Some codecs in Asterisk are supported only in pass-through mode; these codecs cannot be translated. To verify which codecs are installed in your system, you can use the console command:

```
CLI>core show translation
```

The following codecs are supported:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Only pass-through mode
- G.726 - (16/24/32/40kbps)
- G.729 - Binary codec module distributed by Sangoma; the download is free of charge, but lawful use requires purchasing a per-channel license (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

إرسال البيانات من هاتف إلى آخر يجب أن يكون سهلاً بشرط أن تجد البيانات مسارًا إلى الهاتف الآخر من تلقاء نفسها. للأسف، لا يحدث ذلك، ويكون بروتوكول الإشارة ضروريًا لإنشاء الاتصالات بين الهواتف، واكتشاف الأجهزة الطرفية، وتنفيذ إشارات الهاتف. SIP هو بروتوكول الإشارة السائد في النشر الحديث وهو القناة الوحيدة المتاحة لـ SIP في Asterisk 22 LTS (عبر chan_pjsip). لا يزال IAX2 متاحًا لكنه يعتبر قديمًا. يدعم Asterisk البروتوكولات التالية.

- SIP — via `chan_pjsip`
- IAX2 — legacy, still ships in Asterisk 22
- UNISTIM — Nortel/Avaya phones (extended support)
- H.323, MGCP, and SCCP (Cisco Skinny) — legacy protocols no longer in a standard Asterisk 22 build (H.323 only via the community `ooh323` add-on)

### Applications

لجسر المكالمات من هاتف إلى آخر، يُستخدم التطبيق dial(). معظم ميزات Asterisk (مثل البريد الصوتي والمؤتمرات) تُنفّذ كتطبيقات. يمكنك رؤية التطبيقات المتاحة في Asterisk باستخدام أمر وحدة التحكم core show applications.

```
CLI>core show applications
```

يمكنك إضافة التطبيقات من إضافات Asterisk، أو من مزودي الطرف الثالث، أو حتى تلك التي تطورها بنفسك.

## نظرة عامة على نظام Asterisk

Asterisk هو نظام PBX مفتوح المصدر يعمل كـ PBX هجين، يدمج تقنيات مثل TDM والاتصالات الصوتية عبر IP. Asterisk جاهز لتنفيذ وظائف مثل الاستجابة الصوتية التفاعلية (IVR) وتوزيع المكالمات التلقائي (ACD)؛ علاوة على ذلك، كما ذُكر سابقًا، فهو مفتوح لتطوير تطبيقات جديدة. يوضح الشكل التالي كيف يتصل Asterisk بشبكة PSTN وأنظمة PBX الموجودة باستخدام واجهات تناظرية ورقمية، بالإضافة إلى دعمه للهواتف التناظرية وهواتف IP. يمكنه أن يعمل كـ soft-switch، بوابة وسائط، بريد صوتي، ومؤتمر صوتي، كما يحتوي على موسيقى الانتظار مدمجة.

![نظرة عامة على نظام Asterisk](../images/01-introduction-fig02.png)

## مقارنة بين العالم القديم والعالم الجديد

في نموذج الـ SoftSwitch القديم، كانت جميع المكونات تُباع بشكل منفصل، مما يعني أنه كان عليك شراء كل مكوّن على حدة ثم دمجه في بيئة الـ PBX أو الـ SoftSwitch. كانت التكاليف والمخاطر مرتفعة وكانت معظم المعدات مملوكة.

![العالم القديم: مكونات تم شراؤها ودمجها بشكل منفصل](../images/01-introduction-fig03.png)

### الاتصالات باستخدام Asterisk

جميع الوظائف مدمجة في منصة Asterisk في نفس الصندوق أو في صناديق مختلفة حسب حجم التصميم، وجميعها مرخصة تحت رخصة GPL. أحيانًا يكون تثبيت Asterisk أسهل من ترخيص بعض أنظمة الـ IP-PBX السائدة.

![الاتصالات باستخدام Asterisk: الوظائف مدمجة](../images/01-introduction-fig04.png)

## بناء نظام اختبار

عند تنفيذ حل Asterisk، تكون خطوتنا الأولى عادةً بناء نظام اختبار. الهدف هو **PBX 1×1** بسيط — هاتف واحد يمكنه الاتصال بآخر — حتى تتمكن من تجربة النقاط الطرفية، وخطة الاتصال، والميزات قبل التعامل مع بيئة الإنتاج. اليوم كل ذلك يتم برمجياً: لا تحتاج إلى أي عتاد هاتفية.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### الطريقة الحديثة: مختبر برمجي (مُوصى به)

أسرع نظام اختبار هو Asterisk 22 يعمل داخل حاوية أو آلة افتراضية، مع **softphones** للنقاط الطرفية، واختياريًا **SIP trunk** للوصول إلى الشبكة العامة:

- **Asterisk 22** على جهاز لينكس صغير، أو آلة افتراضية، أو حاوية Docker. يوفّر هذا الكتاب مختبر Docker جاهز (انظر دليل المختبر) يُشغّل Asterisk 22 مُكوَّنًا بالكامل بأمر واحد — دون تجميع، دون عتاد.
- **هاتفان نرمَيان** مسجلان كنقاط طرفية PJSIP، بحيث يمكنك إجراء مكالمة حقيقية بينهما. طوال هذا الكتاب نستخدم **SipPulse Softphone** (تحميل مجاني: <https://www.sippulse.com/produtos/softphone>)، المتوفر لأجهزة الحاسوب والهواتف المحمولة.
- **خط SIP** (اختياري) من مزود VoIP، عندما تريد الوصول إلى PSTN. لا بطاقة ولا خط تماثلي — فقط بيانات الاعتماد.

هذه هي الطريقة التي يُبنى ويُتحقق منها كل مثال في هذا الكتاب، ويمكنك تكرارها على أي حاسوب محمول.

### الطريقة التقليدية: بطاقات تماثلية/رقمية

قبل VoIP، كان نظام PBX الاختباري يحتاج إلى واجهات مادية: منفذ **FXO** للاتصال بخط هاتف موجود ومنفذ **FXS** لتوصيل هاتف تماثلي، مما يمنحك PBX 1×1. كانت بطاقة واحدة تحمل واجهة FXO وواجهة FXS هي مجموعة البدء الكلاسيكية. لا تزال هذه البطاقات القائمة على DAHDI (من Sangoma، سابقةً Digium) موجودة للمواقع التي يجب أن تنهي خطوط تماثلية أو T1/E1، لكنها اليوم نادرة — معظم النشرات تعتمد على VoIP فقط. إذا كنت تحتاج فقط إلى توصيل هواتف أو خطوط تماثلية، راجع فصل *Legacy Channels*؛ وإلا يمكنك إهمال عتاد الهاتفية تمامًا.

## Asterisk scenarios

Asterisk can be used in several different scenarios. We will list some of them and explain the advantages and possible limitations of each.

### IP PBX

The most common scenario is the installation of a new or the replacement of an existing PBX. If you compare Asterisk with some other alternatives, you will find it to be cheaper and richer in features than most PBXs currently available on the market. Several companies are now changing their specifications to Asterisk instead of other brand-name PBXs.

![Asterisk as an IP PBX](../images/01-introduction-fig06.png)

### IP-enabling legacy PBXs

The following image illustrates one of the most commonly used setups. Large companies generally do not want to take significant risk when investing in new technologies and simultaneously wish to preserve their investments in legacy equipment. IP-enabling legacy PBX can be very expensive; thus, connecting an Asterisk PBX using T1/E1 lines can be a good alternative for cost-conscious customers. Another benefit is the possibility of connecting to a VoIP service provider with better telephony rates.

![IP-enabling a legacy PBX](../images/01-introduction-fig07.png)

### Toll Bypass

A very useful application for VoIP is connecting branch offices over the Internet or a WAN. Using an existing data connection allows you to bypass toll charges incurred in telecommunication connections between headquarters and branch offices.

![Toll bypass between offices over a WAN](../images/01-introduction-fig08.png)

### Application Server (IVR, Conference, Voicemail)

Asterisk can be used as an application server for the existing PBX or be directly connected to PSTN. Asterisk offers services such as voicemail, fax reception, call recording, IVR connected to a database, and an audio conferencing server. If you integrate voicemail and fax into an existing e-mail server, you will have a unified messaging system, which is usually an expensive solution. Using Asterisk as an application server provides extreme cost reduction compared to other solutions.

![Asterisk as an application server](../images/01-introduction-fig09.png)

### Media Gateway

Most voice-over IP service providers use an SIP proxy to host all registration, location, and authentication of SIP users. They still have to send calls to the PSTN directly or route it through a wholesale call termination provider using an SIP or H.323 voice-over IP connection. Asterisk can act as a back-to-back user agent (B2BUA) or media gateway, replacing very expensive soft switches or media gateways. Compare the price of a four E1/T1 gateway from the main market manufacturers with Asterisk. The Asterisk solution can cost several times less than other solutions and is capable of translating signaling protocols (H.323, SIP, IAX…) and codecs (G.711, G.729…).

![Asterisk as a media gateway](../images/01-introduction-fig10.png)

### Contact Center Platform

A contact center is a very complex solution that combines several technologies, such as automatic call distribution (ACD), interactive voice response (IVR), and call supervision. Basically, three types of contact centers are available: inbound, outbound, and blended.

Inbound contact centers are very sophisticated and usually require ACD, IVR, CTI, recording, supervision, and reports. Asterisk has a built-in ACD to queue the calls. IVR can be done using Asterisk Gateway Interface (AGI) or internal mechanisms such as the application background(). Computer telephony integration (CTI) is achieved using Asterisk Manager Interface (AMI); recording and reporting are built in to Asterisk.

For an outbound contact center, a predictive or power dialer is one of the main components. Although several dialers are available for the open-source Asterisk, it is not hard to build your own for the platform if you so desire. A blended contact center allows simultaneous inbound and outbound operation, saving money by ensuring better use of the agent's time. It is possible to use Asterisk and its ACD mechanism to implement a blended solution.

![An Asterisk contact-center platform](../images/01-introduction-fig11.png)

## العثور على المعلومات والمساعدة

سيوفر هذا القسم بعض المصادر الرئيسية للمعلومات المتعلقة بـ Asterisk.

- الموقع الرسمي لـ Asterisk: <https://www.asterisk.org> يمكنك هنا العثور على معلومات حول:
- الوثائق والويكي -> <https://docs.asterisk.org>
- منتدى المجتمع -> <https://community.asterisk.org>
- تتبع الأخطاء -> <https://github.com/asterisk/asterisk/issues>
- الويكي (قديم، تم استبداله إلى حد كبير بـ docs.asterisk.org) -> <https://wiki.asterisk.org>

### منتدى المجتمع

لقد حلّ منتدى مجتمع Asterisk محل القوائم البريدية القديمة إلى حد كبير وهو المكان المناسب لطرح الأسئلة. حاول جمع أكبر قدر ممكن من المعلومات قبل النشر. لن يساعدك أحد إذا لم تقم بواجبك المنزلي — حاول مرة واحدة على الأقل حل المشكلة بنفسك.

- <https://community.asterisk.org>

## Summary

Asterisk هو برنامج مرخص وفقًا لرخصة GPL يتيح لجهاز كمبيوتر عادي أن يعمل كمنصة PBX IP قوية. أنشأ مارك سبنسر من Digium Asterisk في أواخر التسعينيات، واستمرت Digium في تمويل نفسها ببيع الأجهزة والمنتجات التجارية المتعلقة بـ Asterisk. تم الاستحواذ على Digium من قبل Sangoma Technologies في عام 2018؛ وتقوم Sangoma الآن برعاية تطوير Asterisk. نشأ تصميم واجهة الأجهزة في مشروع Zapata الذي طوره جيم ديكسون، والذي أدى إلى ظهور DAHDI.

تتكون بنية Asterisk من المكونات الرئيسية التالية:

- CHANNELS: تماثلية، رقمية، أو صوت عبر IP. في Asterisk 22 LTS، يتم التعامل مع SIP حصريًا بواسطة `chan_pjsip`.
- PROTOCOLS: بروتوكولات الاتصال، المسؤولة عن إشارة المكالمات، بما في ذلك SIP (عبر PJSIP)، H.323، MGCP، و IAX2.
- CODECS: ترجمة الصيغ الرقمية للصوت مما يسمح بالضغط وإخفاء فقدان الحزم. لاحظ أن Asterisk نفسه لا يقوم بضغط الصمت (اكتشاف نشاط الصوت) أو توليد ضوضاء الراحة؛ عندما تستخدم النقاط الطرفية VAD، يجب تعطيل ضوضاء الراحة على جانب العميل.
- APPLICATIONS: مسؤولة عن وظائف PBX في Asterisk. المؤتمرات، البريد الصوتي، والفاكس هي أمثلة على تطبيقات Asterisk.

يمكن استخدام Asterisk في سيناريوهات مختلفة، من PBX IP صغير إلى مركز اتصال متطور. يمكنك بسهولة العثور على المساعدة في www.asterisk.org و docs.asterisk.org.

## Quiz

1. أي شركة استحوذت على Digium في عام 2018 وتعمل الآن كالمسؤول الأساسي عن مشروع Asterisk مفتوح المصدر؟
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. في Asterisk 22 LTS، أي برنامج تشغيل قناة يوفر الاتصال عبر SIP؟
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. صواب أم خطأ: تم إزالة برنامج تشغيل القناة `chan_sip` في Asterisk 21 ولا يوجد في بناء Asterisk 22 القياسي.

4. أي من القنوات/البروتوكولات التالية **لم تعد** جزءًا من بناء Asterisk 22 القياسي؟ (اختر كل ما ينطبق.)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`، يبقى فقط كملحق المجتمع `ooh323`)

5. تم تسمية بنية الأجهزة لمشروع Zapata، التي كانت تُدعى أصلاً Zaptel، لاحقًا إلى ____.
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. عندما يحتاج Asterisk إلى تحويل الصوت من ترميز إلى آخر، أي تنسيق تدفق داخلي يترجم من خلاله؟
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. وفقًا للفصل، ما هو وضع الترخيص لوحدة ترميز G.729 التي توزعها Sangoma؟
   - A. هي GPL ومجانية تمامًا لأي استخدام.
   - B. التحميل مجاني، لكن الاستخدام القانوني يتطلب شراء ترخيص لكل قناة.
   - C. لا يمكن الحصول عليها على الإطلاق دون شراء Asterisk Business Edition.
   - D. تعمل فقط في وضع المرور فقط ولا يمكن تثبيتها.

8. أي تطبيق في Asterisk يُستخدم لربط مكالمة من هاتف إلى آخر؟
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. ما هو قناة `Local` في Asterisk؟
   - A. واجهة FXS مادية للهواتف التناظرية.
   - B. خط SIP إلى مزود خدمة محلي.
   - C. قناة زائفة تعيد توجيه المكالمة إلى مخطط الاتصال في سياق مختلف.
   - D. ترميز يُستخدم للمكالمات داخل الشبكة.

10. في أي سيناريو استخدام يعمل Asterisk كوكيل مستخدم خلفي (B2BUA)، يترجم بين بروتوكولات الإشارة والترميزات لاستبدال المفاتيح الناعمة المكلفة؟
    - A. تمكين IP لمركز تحكم PBX قديم
    - B. تجاوز الرسوم
    - C. بوابة وسائط
    - D. منصة مركز اتصال

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
