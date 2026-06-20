# Legacy channels: analog, TDM & IAX2

في عالم VoIP النقي لعام 2026، أصبحت أنواع القنوات المذكورة في هذا الفصل نادرة بشكل متزايد: معظم النشر الجديد يستخدم trunk‑ات SIP ونقاط النهاية PJSIP عبر Ethernet، دون أي عتاد هاتفية على الإطلاق. ومع ذلك لا يزال Asterisk 22 يدعم معظمها بالكامل. يتم توفير الاتصال التناظري (FXO/FXS) والرقمي TDM (E1/T1/ISDN PRI/BRI) عبر DAHDI — مجموعة التعريفات التي طورتها Digium في الأصل، والتي استحوذت عليها Sangoma في 2018، بعد أن أُعيد تسمية تعريفات Zaptel نتيجة نزاع علامة تجارية. يتم توفير الاتصال من خادم إلى خادم عبر IAX2 بواسطة `chan_iax2`، الذي لا يزال يُشحن ويُدعم لكنه الآن بروتوكول قديم ثابت.

يجمع هذا الفصل أيضًا مادة **legacy SIP**: برنامج التشغيل القديم `chan_sip` وتكوينه `sip.conf` — الذي أُزيل في Asterisk 21 واختفى في Asterisk 22 — إلى جانب دليل كامل لترحيل نظام `sip.conf` الحالي إلى PJSIP. إذا كنت تدير بيئة SIP نقية على PJSIP دون بطاقات هاتفية، دون trunk‑ات IAX2، ودون أي `sip.conf` قديم للتحويل، يمكنك تخطي هذا الفصل بأمان.

## الأهداف

بنهاية هذا الفصل، يجب أن تكون قادرًا على:

- ربط Asterisk بالخطوط التناظرية والهواتف باستخدام واجهات FXO/FXS عبر DAHDI;
- التعرف على الاتصال الرقمي TDM (E1/T1، ISDN PRI/BRI) وكيفية تكوينه;
- تكوين IAX2 (`chan_iax2`) للخطوط بين الخوادم وفهم سبب كونه الآن تقليديًا;
- تحديد برنامج تشغيل `chan_sip` المتقاعد وصياغة `sip.conf` التي قد تصادفها؛ و
- ترحيل نظام `chan_sip`/`sip.conf` الحالي إلى PJSIP.

## القنوات التناظرية (FXO/FXS)

مع إصدار Asterisk 22، لا تزال بطاقات الهاتف التناظرية وDAHDI مدعومة بالكامل، ولا يزال DAHDI يُبنى ضد النوى الحالية. ومع ذلك، فإن الغالبية العظمى من عمليات النشر الجديدة هي VoIP صافية (قنوات SIP، PJSIP)، لذا فإن الأجهزة التناظرية/TD​M أصبحت خيارًا نادرًا — تُستخدم أساسًا في البيئات القديمة، أو في الاتصال الريفي بشبكة PSTN، أو في الأسواق الخاضعة للرقابة. كل ما يلي يظل ساريًا على تلك السيناريوهات.

هناك عدة طرق لربط شبكة الهاتف العامة (PSTN). الطريقة المثلى تعتمد على كيفية توفير شركة الهاتف لهذا الاتصال في منطقتك. أبسط طريقة هي استخدام خط تناظري، مشابه للخط الذي تستخدمه في المنزل. في هذا القسم، سنوضح لك كيفية إعداد بطاقات التناظرية من Sangoma™ (سابقًا Digium™) وXorcom™.

### الأهداف

بنهاية هذا الفصل يجب أن تكون قادرًا على:

- التعرف على المصطلحات والاختصارات الرئيسية في مجال الهاتفية؛
- فهم متى يُستَخدم الدوائر الرقمية والتناظرية؛
- التمييز بين FXS وFXO؛ و
- إعداد Asterisk لـ FXS وFXO.

### أساسيات الهاتفية

تستخدم معظم التطبيقات التناظرية زوجًا من الأسلاك يُسمى tip وring. عندما يُغلق الحلقة، يتلقى الهاتف نغمة الطلب من مفتاح الاتصالات (أو الـ PBX الخاص). الإشارة الأكثر شيوعًا هي loop‑start؛ وهناك إشارات أخرى أقل شيوعًا تشمل ground start، والتي تُستَخدم في عدة دول. الفئات الثلاث للإشارات هي:

- إشارات الإشراف
- إشارات العنوان
- إشارات المعلومات

#### إشارات الإشراف

الإشارات الرئيسية للإشراف هي on‑hook، off‑hook، والرنين.

- **On‑Hook** – عندما يضع المستخدم الهاتف على الخطاف، يقطع الـ PBX التيار الكهربائي ولا يسمح بمروره. في هذه الحالة تُسمى الدائرة on‑hook. في هذا الوضع، يكون الرنين هو العنصر النشط فقط.
- **Off‑Hook** – قبل بدء المكالمة، يحتاج الهاتف إلى الانتقال إلى حالة off‑hook. إزالة السماعة من الخطاف تُغلق الحلقة وتُشير إلى الـ PBX أن المستخدم يرغب في إجراء مكالمة. عند تلقي هذه الإشارة، يولد الـ PBX نغمة طلب، مُشيرًا إلى المستخدم بأنه جاهز لاستقبال عنوان الوجهة (أي رقم الهاتف).
- **Ringing** – عندما يتصل مستخدم بآخر، يُولد جهدًا إلى الرنان يُنبه الطرف الآخر بوجود مكالمة واردة. تختلف الإشارات حسب الدولة، مع نغمات مختلفة لكل دولة.

يمكنك تخصيص نغمات Asterisk لتتناسب مع بلدك عن طريق تعديل ملف `indications.conf`. على سبيل المثال:
---

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### إشارة العنوان

يمكنك استخدام نوعين من الإشارة للاتصال. الأول والأكثر شيوعًا هو إشارة النغمة المزدوجة متعددة التردد (dtmf) بينما الآخر هو الاتصال النبضي (المستخدم في هواتف دوارة قديمة). تحتوي الهواتف على لوحة مفاتيح للاتصال، وكل زر مرتبط بترددين: أحدهما عالي والآخر منخفض. في حالة إشارة dtmf، يجمع هذا المزيج من النغمات لتحديد الرقم المضغوط. يستخدم MFC/R2 نغمة متعددة التردد تختلف عن dtmf.

#### إشارة المعلومات

إشارة المعلومات تُظهر تقدم المكالمة والأحداث المختلفة.

- نغمة طلب الاتصال
- نغمة الانشغال
- نغمة الرنين
- نغمة الازدحام
- نغمة رقم غير صالح
- نغمة التأكيد

### واجهات PSTN

كما هو الحال مع أنظمة PBX القديمة، غالبًا ما يُطلب ربط نظام Asterisk PBX بشبكة PSTN. سنوضح لك هنا كيفية القيام بذلك. عادةً ما يكون لديك ثلاث خيارات لخطوط الهاتف.

- Analog: الشكل الأكثر شيوعًا للمنازل والشركات الصغيرة، عادةً ما يُقدَّم عبر زوج معدني من خطوط النحاس.  
- Digital: يُستخدم عندما تكون الحاجة إلى العديد من الخطوط. عادةً ما تُقدَّم الخطوط الرقمية عبر CSU/DSU أو مُضاعف ألياف. الموصل الخاص بالمستخدم النهائي يكون عادةً RJ45. في بعض البلدان، تُقدَّم خطوط E1 باستخدام موصلين coaxial BNC؛ في هذه الحالة ستحتاج إلى محول لتوصيل مقبس RJ45 بلوحة الهاتف.  
- SIP: تم تطوير هذا الخيار مؤخرًا. تُقدَّم خط الهاتف عبر اتصال بيانات مع إشارة SIP (VoIP). هذا خيار جيد للاستخدام مع Asterisk لأنك لن تحتاج إلى شراء بطاقة هاتفية. تُسلم المكالمات مباشرة إلى منفذ Ethernet. ميزة أخرى هي أنك قد تتمكن من تحرير موارد CPU بتجنب تحويل الترميز.

### واجهات Analog FXS, FXO, و E&M

عدة أنواع من الواجهات التناظرية متاحة. من الأساسي فهم الفروقات بين هذه الواجهات لتعلم كيفية الاتصال بشبكة الهاتف وكذلك مع أنظمة PBX الأخرى. هنا، سنعرض لك واجهة E&M. على الرغم من أنها غير متوفرة حالياً لـ Asterisk وتم إيقافها من قبل عدة بائعين، قد تجد أجهزة توجيه وPBX بهذه الواجهة، لذا من الأفضل أن تعرف ما تتعامل معه.

#### واجهات الصرف الأجنبي (FX)

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![Asterisk بين هاتف تماثلي (FXS) وخط شركة الاتصالات (FXO): يوفر جانب FXS نغمة الطلب والرنين للهاتف، بينما يسحب جانب FXO نغمة الطلب من مكتب التبديل المركزي.](../images/10-legacy-fig01.png)

واجهة FXO تُستخدم للاتصال بمكتب مركزي (CO) أو بامتداد PBX آخر. تتواصل مباشرةً مع خط هاتف يأتي من PSTN. خيار آخر هو ربط واجهة FXO بـ PBX موجود، مما يسمح بالتواصل بين Asterisk و PBX القديم. ربط Asterisk بمنفذ PBX وتوفير امتداد بعيد باستخدام VoIP يُشار إليه غالبًا بامتداد خارج الوعد (OPX). تستقبل واجهة FXO إشارة نغمة الاتصال. محطة التبادل الأجنبية (FXS) تُغذي هاتفًا تناظريًا أو مودمًا أو فاكسًا. توفر FXS نغمة الاتصال والطاقة للهاتف.

#### إشارة الخط

- بدء الحلقة
- بدء الأرضي
- بدء كول

استخدام إشارة kewlstart في Asterisk هو تقريبًا افتراضي. kewlstart ليست إشارة بحد ذاتها، بل تضيف ذكاءً إلى الدائرة من خلال مراقبة ما يحدث على الطرف الآخر. kewlstart مبنية على loop-start. معظم المفاتيح لا تدعم هذه الميزة، التي تُستخدم للحصول على إشعار إنهاء المكالمة.

- Loopstart: يُستخدم في معظم الخطوط التناظرية، ويتيح لل هاتف أن يُظهر حالة “on‑hook” و “off‑hook” وللمفتاح أن يُظهر حالة “ring” و “no‑ring”. هذا هو ما يمتلكه معظم الناس في منازلهم. الاسم يأتي من حقيقة أن الخط يكون دائماً مفتوحاً. عندما تُغلق الحلقة، يوفر المفتاح لك نغمة طلب. يتم الإشارة إلى مكالمة واردة بجهد رنين 100V عبر الزوج المفتوح.

![تشغيل Asterisk كبوابة VoIP: منفذ FXO يتصل بامتداد PBX قديم بينما يقوم Asterisk بعيد بتسليم ذلك الخط إلى هاتف تماثلي عبر IP من خلال منفذ FXS (امتداد خارج الموقع، أو OPX).](../images/10-legacy-fig02.png)

- Groundstart: مشابه لـ Loopstart. عندما تريد إجراء مكالمة، يتم قصر أحد طرفي الخط. عندما يحدد المفتاح هذه الحالة، يعكس الجهد عبر الزوج المفتوح، ثم يُغلق الحلقة. وبالتالي يصبح الخط مشغولًا أولاً قبل أن يُعرض على المتصل.  
- Kewlstart: يضيف ذكاءً إلى الدوائر، مما يسمح بمراقبة الطرف الآخر. Kewlstart يدمج العديد من المزايا من loop-start.

### إعداد قنوات الاتصالات في Asterisk

لتكوين بطاقة واجهة هاتفية، هناك عدة خطوات ضرورية. في هذا الفصل، سنعرض ثلاثة من أكثر السيناريوهات شيوعًا:

- اتصال تناظري باستخدام FXS
- اتصال تناظري باستخدام FXO
- اتصال Astribank™ بواجهات FXS و FXO

### إجراء التكوين (صالح في الحالتين)

قبل اختيار الأجهزة لـ Asterisk، يجب أن تأخذ في الاعتبار عدد المكالمات المتزامنة، والخدمات، والترميزات (codecs) التي سيتم تثبيتها وتفعيلها. Asterisk هو تطبيق يستهلك الكثير من وحدة المعالجة المركزية، ولذلك نوصي باستخدام جهاز مخصص لـ Asterisk. عدد بطاقات الواجهة المثبتة داخل الحاسوب يحده عدد الفتحات ومقاطع المقاطعة المتاحة. من الأفضل تثبيت بطاقة واحدة ذات ثمانية واجهات صوتية بدلاً من بطاقتين بأربع واجهات لكل منهما. خيار آخر هو استخدام بنك قنوات USB، مثل Xorcom Astribank. مؤخراً، بدأ بعض المصنعين (مثل CIANET) في إنتاج بنوك قنوات TDMoE، مما يجعل من السهل أكثر ربط العشرات من الواجهات التناظرية.

![أكسوركم أستربنك: بنك قنوات USB بارتفاع 19 بوصة يمكن تركيبه في رف، يكشف عن العشرات من منافذ FXS/FXO (هنا وحدة بـ 32 منفذ) دون استهلاك فتحات PCI في المضيف.](../images/10-legacy-fig03.png)

#### مثال 1: تركيب FXO واحد، FXS واحد

في هذا المثال، سنستخدم بطاقة واجهة هاتفية Sangoma TDM400 (كانت تُباع سابقًا باسم Digium TDM400) مع وحدة FXS واحدة ووحدة FXO واحدة. الخطوات المطلوبة مُدرجة أدناه:

1. تثبيت بطاقة التناظرية FXS أو FXO أو كليهما.  
2. تكوين الملف `/etc/dahdi/system.conf` (سابقًا `/etc/zaptel.conf`).  
3. إنشاء ملفات التكوين باستخدام `dahdi_genconf`.  
4. تحميل برنامج تشغيل واجهة DAHDI.  
5. تنفيذ `dahdi_test` للتحقق من فقدان المقاطعات.  
6. تنفيذ `dahdi_cfg` لتكوين برنامج التشغيل.  
7. تكوين قناة DAHDI في ملف `chan_dahdi.conf`، ثم تحميل Asterisk.

##### الخطوة 1: تثبيت لوحة TDM400

The TDM404P card contains FXS and FXO modules. Connect the FXS (S110M, green) and FXO (X100M, red) modules. If you are using FXS modules, connect the card directly to the power source using a molex connector. Please wear electrostatic protection before handling interface cards to avoid damage to the hardware. Sangoma (formerly Digium) analog cards also support a hardware echo cancellation module VPMADT032.

##### الخطوة 2: إنشاء التكوين باستخدام dahdi_genconf

الخبر السار بشأن التكوين هو الأداة الجديدة `dahdi_genconf`، التي تكتشف تلقائيًا وتولد تكوين واجهات DAHDI. تولد الأداة ملفين:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (مع الخيار `users`)
- جميع هذه الملفات تستخدم الخيار `chan_dahdi full`

قبل أن تتمكن من تنفيذ `dahdi_genconf`، من المهم تكوين الملف `genconf_parameters` (غالبًا ما يُشار إليه باسم `gen_parameters.conf`):

![بطاقة تناظرية Sangoma/Digium TDM404P: يمكن توصيل ما يصل إلى أربع وحدات FXS أو FXO في المنافذ المرقمة، مع بطاقة فرعية اختيارية لإلغاء الصدى المدمجة وموصل طاقة مخصص بجهد 12 فولت لوحدات FXS.](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

ملف `genconf_parameters` يتيح لك تخصيص إعداداتك. أهم المعلمات للخطوط التناظرية هي:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

تحذير: من الضروري أن تقوم بتكوين خوارزمية إلغاء الصدى على الأقل للقنوات. تُعرّف المعلمة base_exten خطة الطلب الأساسية لامتدادات FXS. في هذه الحالة، سيحصل القناة الأولى من نوع FXS على رقم الامتداد 4000، والثانية على 4001، وهكذا. السياق الذي تُنشأ فيه الخطوط (context_phones) والخطوط الخلفية (context_lines) مهم جداً. بعد توليد الملفات، يجب أن تُدرج الملف `/etc/asterisk/dahdi-channels.conf` في الملف `/etc/asterisk/chan_dahdi.conf`:

```
#include dahdi-channels.conf
```

Note: الإشارة التناظرية قد تكون مربكة بعض الشيء؛ فهي دائمًا عكس البطاقة. بطاقات FXS تُشار إليها بـ FXO بينما بطاقات FXO تُشار إليها بـ FXS. يتعامل Asterisk مع هذه الأجهزة كما لو كان على الجانب المقابل.

##### الخطوة 3: تحميل برامج تشغيل النواة

Now you have to load the chan_dahdi module and the related card kernel driver. Use dahdi_hardware to detect your card and the driver name. For example:

| البطاقة | برنامج التشغيل | الوصف |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - 3.3V PCI |
| TE405P | wct4xxp | 4xE1/T1 - 5V PCI |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

أوامر تحميل برامج التشغيل:

```
modprobe dahdi
modprobe wctdm
```

##### Step 4: Use the dahdi_test utility

أداة مهمة هي dahdi_test، تُستخدم للتحقق من فقدان المقاطعات في بطاقة DAHDI. غالبًا ما تكون مشاكل جودة الصوت مرتبطة بتصادم المقاطعات. للتحقق من أن بطاقة DAHDI الخاصة بك لا تشارك مقاطعة مع بطاقات أخرى، استخدم الأمر التالي:

```
#cat /proc/interrupts
```

يمكنك التحقق من عدد فقدان المقاطعات باستخدام أداة `dahdi_test` المجمعة مع بطاقات DAHDI. رقم أقل من 99.987٪ يشير إلى احتمال وجود مشاكل.

##### الخطوة 5: استخدم أداة `dahdi_cfg` لتكوين برنامج التشغيل

يحتوي DAHDI على نظام غير معتاد لتحميل برامج التشغيل. أولاً قم بتكوين الملف `/etc/dahdi/system.conf`، ثم طبّق تلك التكوينات على برنامج تشغيل DAHDI باستخدام `dahdi_cfg`. في هذه الحالة، يُستخدم `dahdi_cfg` لتكوين الإشارة لواجهات FX. لرؤية النتائج، يمكنك إلحاق “-vvvvv” بالأمر للحصول على تفاصيل أكثر.

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

إذا تم تحميل القنوات بنجاح، ستظهر مخرجات مشابهة لتلك المعروضة أعلاه. غالبًا ما يقوم المستخدمون بتكوين chan_dahdi.conf بشكل غير صحيح مع إشارة مقلوبة بين القنوات. إذا حدث ذلك، ستظهر رسالة مثل تلك المعروضة أدناه.

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

بعد الانتهاء من تكوين الأجهزة بنجاح، يمكنك المتابعة إلى تكوين Asterisk.

##### الخطوة 6: تكوين ملف /etc/asterisk/chan_dahdi.conf

قد يبدو ذلك غريبًا، ولكن بعد تكوين /etc/dahdi/system.conf، تكون قد قمت بتكوين البطاقة نفسها. يمكن استخدام DAHDI لأغراض أخرى، مثل التوجيه وSS7. لاستخدامه مع Asterisk، يجب تكوين قنوات DAHDI الخاصة بـ Asterisk. يجب تعريف كل قناة في Asterisk؛ تُعرّف قنوات SIP/PJSIP في pjsip.conf (ملاحظة: تم إزالة chan_sip وsip.conf في Asterisk 21) بينما تُعرّف قنوات TDM في chan_dahdi.conf. هذا يُنشئ القنوات المنطقية لـ TDM لتُستخدم في مخطط الاتصال الخاص بك.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### خيارات التكوين

تتوفر عدة خيارات في ملف `chan_dahdi.conf`. سيكون من الممل وغير المفيد وصف جميع الخيارات؛ بدلاً من ذلك، سنركز على مجموعات الخيارات الرئيسية المتاحة لتسهيل الفهم.

#### خيارات عامة (غير معتمدة على القناة)

هذه الخيارات تعمل مع أي قناة: `context:` يحدد السياق الوارد.

```
context=default
```

channel: يعرّف القناة أو نطاق القنوات. كل تعريف قناة سيورث الخيارات المعرفة قبل الإعلان. يمكن التعرف على القنوات بشكل فردي أو في نفس السطر بفصلها بفواصل. يمكن تعريف النطاقات باستخدام “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: يسمح بمعالجة القنوات كمجموعة. إذا قمت بالاتصال برقم مجموعة بدلاً من رقم قناة، يتم استخدام أول قناة متاحة. إذا كانت القنوات هواتف، عند الاتصال بمجموعة، سترن جميع الهواتف في آن واحد. باستخدام الفواصل، يمكنك تحديد أكثر من مجموعة لنفس القناة.

```
group=1
group=3,5
```

language: يشغّل التعريب ويضبط اللغة. هذه الميزة ستُعد رسائل النظام للغة معينة. الإنجليزية هي اللغة الوحيدة التي تتوفر لها جميع الرسائل من خلال التثبيت القياسي. musiconhold: يختار فئة الموسيقى أثناء الانتظار.

#### خيارات معرف المتصل

هناك العديد من خيارات معرف المتصل. يمكن تعطيل بعضها، رغم أن معظمها مفعّل افتراضيًا. usecallerid: يفعّل أو يعطّل نقل معرف المتصل للقنوات اللاحقة (Yes/No). ملاحظة: إذا كان نظامك يرن مرتين قبل الرد، جرّب تعطيل هذه الميزة. يجب أن يجيب فورًا. hidecallerid: يحدد ما إذا كان يجب إخفاء معرف المتصل الصادر أم لا (Yes/No). callerid: يضبط سلسلة معرف المتصل لقناة معينة. يمكن ضبط المتصل بـ asreceived. يُستخدم هذا في الغالب في واجهات الـ trunk للإشارة إلى معرف المتصل الوارد.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: يدعم معرف المتصل أثناء الانتظار على المكالمة. useincomingcalleridondahditransfer: يستخدم معرف المتصل الوارد في عملية التحويل.

#### Call Waiting

يدعم Asterisk خاصية الانتظار على المكالمة في قنوات FXS. سيتلقى المستخدم نغمة انتظار إذا حاول شخص ما الاتصال بالامتداد. لتمكين الانتظار على المكالمة:

```
callwaiting=yes
```

لدعم معرف المتصل في الانتظار للاتصال:

```
callwaitingcallerid=yes
```

#### خيارات جودة الصوت

ضبط إلغاء الصدى هو نصف تقنية ونصف فن. هذه الخيارات تعدل بعض معلمات Asterisk التي تؤثر على جودة الصوت في قنوات DAHDI. يمكن أن تساعد في تحسين جودة الصوت في الواجهات التناظرية.

#### أداة fxotune

أداة fxotune هي أداة تُستخدم لضبط بعض المعلمات لموديلات FXO بدقة. هذا الضبط الدقيق مطلوب لتصحيح عدم توافق المقاومة الناتج عن الـ hybrid. للأداة ثلاث أوضاع تشغيل:

- Detection (-i): يكتشف ويصلح القنوات FXO الحالية ويحفظ التكوين إلى

```
fxotune.conf
```

- وضع التفريغ (-d): يولد ملفات الشكل الموجي إلى fxotune_dump.vals
- وضع بدء التشغيل (-s): يقرأ الملف fxotune.conf ويطبّقه على وحدات FXO

من المهم أن تفهم أنه سيتعين عليك إدراج التعليمة fxotune –s في تحميل النظام قبل بدء تشغيل Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### إلغاء الصدى

معظم خوارزميات إلغاء الصدى تعمل عن طريق توليد نسخ متعددة من الإشارة المستلمة، حيث يتم تأخير كل نسخة بمدة زمنية محددة. عدد نقاط الفلتر يحدد حجم تأخير الصدى الذي يجب إلغاؤه. تُضبط هذه النسخ المؤخرة ثم تُطرح من الإشارة المستلمة. الحيلة هي ضبط الإشارة المؤخرة فقط لإزالة الصدى دون استهلاك الكثير من دورات المعالج. من منظور المستخدمين، من المهم اختيار خوارزمية إلغاء صدى مناسبة. الإعداد الافتراضي هو MG2؛ ومع ذلك، هناك خياران آخران متاحان: إلغاء الصدى عالي الأداء (HPEC) من Sangoma (سابقًا Digium) وإلغاء الصدى المفتوح المصدر (OSLEC) الذي طوره David Rowe.

OSLEC (https://www.rowetel.com/?page_id=454) تم دمجه في نواة لينكس — وهو موجود في منطقة النواة `drivers/staging/echo` — وDAHDI يُبنى ضده بدلاً من توفير تحميل منفصل. لتغيير خوارزمية إلغاء الصدى، اضبط المعامل `echo_can` في `/etc/dahdi/system.conf`. على سبيل المثال:

```
echo_can=oslec
```

إلغاء صدى الصوت في Asterisk يتم التحكم به عبر ثلاثة معلمات في الملف /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: يعطل أو يفعّل إلغاء الصدى. يجب إبقاء هذه الميزة مفعّلة. يقبل القيمة "yes" أو عدد النقرات. (شرح: كيف يعمل إلغاء الصدى؟ معظم خوارزميات إلغاء الصدى تعمل عن طريق توليد نسخ متعددة من الإشارة المستلمة، بحيث يتم تأخير كل نسخة بفاصل زمني صغير. تُسمى هذه العملية "نقرة". عدد النقرات يحدّد مقدار تأخير الصدى الذي يمكن إلغاؤه. تُؤخر هذه النسخ، تُضبط، وتُطرح من الإشارة الأصلية. الحيلة هي ضبط الإشارة المؤخرة بدقة لتكون ما يلزم لإزالة الصدى.)
- **echocancelwhenbridged**: يفعّل أو يعطل مُلغِّي الصدى أثناء مكالمة TDM صافية. عادةً لا يكون ذلك ضرورياً.
- **rxgain**: يضبط كسب استقبال الصوت إما لزيادة أو خفض مستوى الاستقبال (-100% إلى 100%).
- **txgain**: يضبط كسب إرسال الصوت إما لزيادة أو خفض مستوى الإرسال (-100% إلى 100%).

For example:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### خيارات الفوترة

هذه الخيارات تغير طريقة تسجيل معلومات المكالمات في قاعدة بيانات سجلات تفاصيل المكالمات (CDR). amaflags: يضبط علامات AMA التي تؤثر على تصنيف الـ CDR. يقبل القيم التالية:

- billing
- documentation
- omit
- default

accountcode: يضبط رمز حساب لقناة معينة. يمكن أن يحتوي على أي قيمة أبجدية رقمية — عادةً اسم القسم أو اسم المستخدم.

```
accountcode=finance
amaflags=billing
```

### خيارات تقدم المكالمة

تُستخدم هذه العناصر للحصول على معلومات حول تقدم المكالمة. في الواجهات العامة، قد يكون من المفيد اكتشاف تقدم المكالمة وتحديد ما إذا تم الرد عليها أو كانت مشغولة. الكشف عن الانشغال تجريبي إلى حد كبير ويتم تنظيمه بواسطة معلمات محددة.

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

هذه المعلمات (أعلاه) تحدد ما إذا كانت الواجهة ستحاول اكتشاف نغمة الانشغال، وعدد النغمات التي ستُستخدم للاكتشاف الناجح، وما هو نمط الانشغال. اكتشاف الانشغال تجريبي إلى حد كبير، ويمكن تغيير بعض المعلمات الإضافية في ملف Makefile. لاكتشاف إجابة المكالمة، وهو أمر أساسي للفوترة الدقيقة، يمكن استخدام عكس القطبية للإشارة إلى وقت الإجابة بالضبط. هذا مهم إذا كنت تخطط لفرض رسوم على المكالمة أو ترغب فقط في الحصول على فواتير دقيقة للمقارنة. عادةً ما يتعين عليك الاتصال بشركة الهاتف لطلب هذه الخدمة.

```
answeronpolarityswitch=yes
```

في بعض البلدان، من الممكن أيضًا اكتشاف إنهاء المكالمة باستخدام عكس القطبية.

```
hanguponpolarityswitch=yes
```

#### Options for phones

These options are used for phones connected to the FXS interfaces. All the functionalities delivered to analog phones connected directly to the DAHDI interfaces are controlled by Asterisk.

- **adsi** (Analog Display Services Interface): This is a set of telecom standards used by some telcos to offer services such as ticket buying.
- **cancallforward**: Enables or disables call forwarding (*72 to enable and *73 to disable).
- **calleridcallwaiting**: Enables callerid received during a call waiting indication (Yes/No).
- **immediate**: In immediate mode, instead of providing a dial tone, the channel jumps immediately to the "s" extension in the defined context. This is used to create hotlines.
- **threewaycalling**: Enables or disables three-way conferencing.
- **mailbox**: Warns the user about available voicemail messages. It can be an audible sign or a visual indicator (if the telephone supports this feature). The argument is the mailbox number.
- **callgroup**: Group phones to dial or to pick up.
- **pickupgroup**: Group of phones for call pickup.

### Useful DAHDI CLI commands

Once Asterisk is running with DAHDI channels loaded, you can inspect channel status from the Asterisk CLI. These commands remain current in Asterisk 22:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### تنسيق قناة DAHDI

قنوات DAHDI تستخدم الصيغة التالية في مخطط الاتصال:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

على سبيل المثال:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## القنوات الرقمية (E1/T1/PRI / TDM)

اعتبارًا من Asterisk 22، لا يزال DAHDI و libpri مدعومين بالكامل، لكن خطوط TDM الرقمية (E1/T1/ISDN PRI) تُستبدل تدريجيًا بخطوط SIP في النشرات الجديدة. يظل هذا القسم قابلًا للتطبيق بالكامل حيث يلزم الاتصال بـ TDM؛ في البيئات الخضراء، عادةً ما يوفر SIP trunking (Chapter 3) نفس كثافة القنوات دون الحاجة إلى أجهزة هاتفية.

القنوات الرقمية شائعة للغاية، لذا سيتعين عليك تعلم كيفية تنفيذ هذه القنوات إذا كنت ترغب في التركيز على العملاء الكبار. عندما يكون عدد القنوات مرتفعًا—عادةً أكثر من ٨—من الشائع إلى حد ما استخدام واجهات رقمية مثل T1/E1/J1. T1 شائع جدًا في الولايات المتحدة، بينما E1 شائع في أوروبا وJ1 في اليابان. هذه الأنواع من القنوات تسمح بكثافة جيدة للدوائر—٢٤ لكل قناة T1 و٣٠ لكل قناة E1.

في أمريكا اللاتينية، الصين، وأفريقيا، من الشائع استخدام نوع من الإشارة المرتبطة بالقناة (CAS) المعروف باسم MFC/R2. سيتناول هذا الفصل كيفية تنفيذ MFC/R2 باستخدام مكتبة OpenR2. في الولايات المتحدة وأوروبا، يعتبر Integrated Services Digital Networks (ISDN) PRI هو الإشارة الأكثر شيوعًا. سيتناول الفصل أيضًا ISDN Basic Rate Interface (BRI)، الذي هو شائع جدًا في أوروبا في التطبيقات المتوسطة.

كل الأمثلة في الكتاب تركز على قنوات DAHDI. بعض البطاقات مُنفذة باستخدام قنوات مملوكة، لذا يرجى مراجعة الشركة المصنعة للحصول على مزيد من التفاصيل حول كيفية تكوين بطاقتك المحددة.

### الأهداف

بنهاية هذا الفصل ستكون قادرًا على:

- التعرف على المصطلحات الرئيسية المستخدمة في الاتصالات الرقمية
- التمييز بين إشارة CAS وإشارة CCS
- التمييز بين إشارة R2 وإشارة ISDN
- تكوين الواجهات بإشارة ISDN
- تكوين الواجهات بإشارة R2

### خطوط E1/T1 الرقمية

الخطوط الرقمية E1/T1 هي خيار متاح كلما احتجت إلى تنفيذ عدد كبير من القنوات. يمكن لدائرة E1 واحدة أن تدعم 30 مكالمة متزامنة، وقد تتضمن ميزات مثل الاتصال الداخلي المباشر (DID)، ومعرف المتصل (Caller ID)، والإشارة المتقدمة. قد تصل خط E1/T1 إلى شركتك بطرق متعددة باستخدام الزوج الملتوي، أو الألياف، أو الموجات الدقيقة، وذلك حسب بلدك. تُسلم الخطوط الرقمية إلى شركتك عبر UTP أو الألياف أو الموجات الدقيقة. تُستخدم المودمات ومضاعفات الإشارة (MUX) لتوصيل الخط الفعلي. الاتصال بخط T1 يكون دائمًا عبر موصل RJ45. ومع ذلك، يمكن أيضًا توفير خطوط E1 باستخدام موصل BNC. من المهم جدًا معرفة نوع الموصل الذي ستستلمه مسبقًا، خاصةً في خطوط E1. عادةً ما يتم توفير جميع المعدات حتى موصل RJ45 من قبل شركة الاتصالات.

![كيف يتم توفير دوائر E1/T1: يمكن لمزود الخدمة نقل الخط عبر النحاس UTP (مودم HDSL لـ E1، أو اتصال بطاقة مباشر لـ T1)، عبر الألياف البصرية من خلال مضاعف بصري، أو عبر رابط راديو ميكروويف.](../images/10-legacy-fig05.png)

![UTP أو BNC؟ معظم البطاقات الرقمية تستخدم موصلات RJ45 (UTP)، لكن بعض خطوط E1 تُنقل عبر كابل مزدوج BNC، وفي هذه الحالة يلزم وجود بالون لتكييف الزوج الكوكسالي مع مقبس RJ45 للبطاقة.](../images/10-legacy-fig06.png)

#### كيف يتم تحويل الصوت إلى بتات؟

يتم أخذ عينات الإشارة التناظرية 8,000 مرة في الثانية لإنشاء نسخة رقمية من الصوت التناظري. يُعرف هذا الترميز باسم تعديل شفرة النبضة (PCM). في الولايات المتحدة واليابان، يتم ترميز الإشارة باستخدام law (في Asterisk يُشار إليه بـ ulaw). في باقي أنحاء العالم، يكون الترميز alaw.

![تعديل النبضات المشفرة (PCM): يتم أخذ عينات لإشارة الصوت التناظرية ذات 4 كيلوهرتز 8,000 مرة في الثانية (نيوكويست) وتُشفَّر إلى تدفق رقمي بسرعة 64 كبت/ثانية.](../images/10-legacy-fig07.png)

#### تقسيم الوقت المتعدد

الخطوط التناظرية تكون منطقية عندما تحتاج إلى عدد قليل فقط من القنوات. عند استخدام تعدد الإرسال بتقسيم الزمن (TDM)، يمكن حزم عدة قنوات في اتصال بيانات واحد. عندما تحتاج إلى عدد كبير من الدوائر، عادةً ما توفر لك شركة الهاتف خطًا رقميًا، وهو دائرة بيانات تُنقل فيها الصوت بصيغة رقمية باستخدام PCM. كل فتحة زمنية تستخدم 64 كيلوبت في الثانية من عرض النطاق لت نقل قناة صوتية واحدة.

![تقسيم الوقت المتعدد في E1 و T1: يحمل إطار E1 32 فتحة زمنية بسرعة 2048 كbps (DS0 #0 لمزامنة الإطار، DS0 #16 للإشارة)، بينما يحمل إطار T1 24 فتحة زمنية بسرعة 1544 كbps باستخدام بت واحد للمزامنة ومخطط سرقة البت للإشارة.](../images/10-legacy-fig08.png)

في الولايات المتحدة، أكثر خط رقمي شائع هو T1، والذي يحتوي على 24 خطًا متاحًا؛ في أوروبا وأمريكا اللاتينية، خطوط E1 تحتوي على 30 خطًا. بعض الشركات توفر نسخة جزئية من T1/E1 بعدد قنوات أقل. إشارة البت المسروق أحيانًا يستخدم خط T1 مخطط إشارة البت المسروق حيث يُستعار بت واحد للإشارة. على خطوط T1، يتم نقل قناة البيانات/الصوت بسرعة 56 كbps على كل فاصل زمني. كما قد تلاحظ، عند استخدام البت المسروق، لا يفقد مسار T1 فتحتين للمزامنة والإشارة.

#### T1/E1 رمز الخط

T1s و E1s هي في الواقع دوائر بيانات ولها ترميز بيانات يحدد طريقة تفسير البتات. بالنسبة لـ E1s، أكثر رموز الخط شيوعًا هو HDB3 للطبقة 1 و CCS للطبقة 2. أسهل طريقة لمعرفة كيفية تكوين الخط الرقمي الخاص بك هي سؤال شركة الاتصالات عن هذه المعلومات. ستحتاج إلى هذه المعلومات لتكوين الملف /etc/dahdi/system.conf.

#### إشارة T1/E1

من المهم أن نفهم أن خطوط T1/E1 قد تُقدم باستخدام أنواع مختلفة من الإشارة، مثل:

- T1 مع إشارة robbed bit signaling
- T1 مع إشارة ISDN signaling
- E1 مع MFC/R2 (CAS - Channel Associated Signaling)
- E1 مع إشارة ISDN signaling

ISDN غالبًا ما يُستخدم في أوروبا والولايات المتحدة. إنه شبكة صوتية رقمية، تم توحيدها من قبل الاتحاد الدولي للاتصالات (ITU) في عام 1984. يوفر ISDN نوعين من القنوات:

- قنوات الحامل
  - صوت
  - بيانات
- قنوات البيانات
  - إشارة خارج النطاق
  - إشارة LAPD
  - Q.931

عادةً، يتم توفير خط ISDN باستخدام وسيلتين ماديّتين:

- واجهة المعدل الأساسي (BRI)
  - معروفة باسم 2B+D
  - قناتان حاملتان (64K) وقناة بيانات (16K)
  - تستخدم زوجًا من الأسلاك النحاسية بسرعة 148Kbps.
- واجهة المعدل الأولي (PRI)
  - تُسلم باستخدام خط T1/E1
  - 23B+D لـ T1s
  - 30B+D لـ E1s

Sometimes, E1 circuits use a CAS signaling scheme called MFC/R2, which was defined by the ITU as a standard known as Q.421/Q441. This is frequently found in Latin America and Asia. Several telephony companies in these countries use customized variants of MFC/R2. Hence, you will need to know the correct country variation in order to make it work.

### ISDN BRI

القنوات التي تستخدم إشارة ISDN BRI شائعة جدًا في أوروبا. معظم بطاقات ISDN BRI لـ Asterisk تدعم واجهة S/T مع قدرات NT و TE. الاتصال TE (الطرف النهائي) هو الذي يُستخدم للاتصال بشركة الاتصالات أو إلى أنظمة PBX أخرى مُكوَّنة كإنهاء شبكة (NT). يُستخدم NT لتوصيل الهواتف وأنظمة PBX المُكوَّنة كـ TE. توفر ISDN BRI قنالي بيانات/صوت وقناة إشارة واحدة. تتوفر بطاقات ISDN BRI من عدة بائعين لبطاقات الواجهة لـ Asterisk.

### اختيار بطاقة هاتفية لخادم Asterisk الخاص بك

هناك عدة مصنعين لبطاقات رقمية متوافقة مع Asterisk. يعتمد اختيار البطاقة على بعض العوامل التالية:

#### ناقل البيانات

هناك عدة أنواع من الحافلات في جهاز الكمبيوتر الخاص بك. من المهم جدًا أن يكون لديك البطاقة المناسبة لخادمك. يوضح الاستعراض التالي أكثر البطاقات استخدامًا:

- 32 Bits PCI 5V موجودة في معظم الحواسيب، بما في ذلك أجهزة سطح المكتب
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 32/64 bits PCI 3.3V، أساساً موجودة في الخوادم
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express موجودة على أجهزة سطح المكتب والخوادم
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

هذه العائلات من البطاقات نشأت في Digium، التي استحوذت عليها Sangoma في عام 2018؛ وهي الآن تُباع وتُدعم تحت علامة Sangoma التجارية. العديد من نماذج SKU القديمة المذكورة هنا قد تم إيقافها، لذا تحقق من توفر الطراز الحالي على www.sangoma.com قبل الشراء.

- MiniPCI موجودة في الأنظمة المدمجة
  - OpenVOX A100M(FXO)، B100M(ISDN BRI)، B200M(ISDN BRI)، و B400M(ISDN BRI)
- USB 2.0 موجودة في معظم أجهزة الحاسوب الحديثة. الحلول القائمة على USB تسمح بكثافة عالية من القنوات التناظرية والرقمية. يدعم هذا الناقل 480 Mbps، ويشغل كل قناة صوتية 64 Kbps. عند استخدام محاور USB، يمكن الحصول على كثافات تصل إلى ألف منفذ تناظري في منفذ واحد.
  - Xorcom Astribank (FXS، FXO، E1-ISDN، E1-R2)
- Ethernet. الميزة الأكبر للـ Ethernet هي السماح بربط البطاقة بأكثر من خادم واحد. عادةً ما تكون حلول التوافر العالي هي التطبيق الأساسي لهذه الأجهزة. قوة هذا الحل تكمن في استخدام خوادم لا تحتوي على فتحات PCI مجانية أو خوادم شفرات.
  - Redfone FoneBridge (حتى أربعة دوائر E1)

### استخدام إلغاء الصدى عبر الأجهزة

إلغاء صدى الأجهزة يقلل العبء على وحدة المعالجة المركزية للمضيف. بالنسبة للبطاقات التي تحتوي على أكثر من واجهة E1 واحدة، يمكن أن يساعد إلغاء صدى الأجهزة في تخفيف عبء المعالج. مُلغيات الصدى البرمجية المحسّنة الجديدة مثل OSLEC تقلل الحاجة إلى مُلغِي صدى الأجهزة. لاختيار بين مُلغِي صدى الأجهزة والبرمجيات، يجب أن تأخذ في الاعتبار مقدار طاقة المعالجة المتوفرة في الخادم وعدد دوائر E1. قد يستخدم عملية إلغاء الصدى ما يصل إلى تسعة ملايين تعليمات في الثانية (MIPS) لكل قناة صوتية مع 128 نبضة من السعة باستخدام OSLEC (المرجع: Xorcom Ltd.). إذا اعتبرت دورة وحدة معالجة واحدة لكل تعليمة (وهو ليس دائمًا صحيحًا بناءً على المعالج وتنفيذ البرنامج نفسه)، فإننا نتحدث عن 1.080 جيجاهرتز لأربعة E1.

#### نوع الإشارة

اختيار نوع الإشارة (مثل T1 CAS، T1 PRI، E1 CAS R2، أو E1 CAS ISDN) ليس مهمة سهلة. يعتمد ذلك حقًا على ما هو متاح في منطقتك وبأي سعر. غالبًا ما يكون الإشارة المشتركة للقناة (CCS) أفضل من الإشارة المرتبطة بالقناة (CAS). ومع ذلك، غالبًا ما تكون غير متوفرة. في الولايات المتحدة، يمكنك عادةً الاختيار، حيث تقدم معظم شركات الاتصالات T1 CAS للمستخدمين العاديين وT1 PRI للمستخدمين المتقدمين (مثل مراكز الاتصال). في أمريكا اللاتينية، ينتشر E1 CAS R2، لكن ISDN PRI متاح في بعض المدن.

![معمارية برنامج DAHDI: يتواصل Asterisk مع برنامج تشغيل القناة `chan_dahdi`، والذي بدوره يحمل مكتبات البروتوكول libpri (ISDN)، libopenr2 (MFC/R2)، و libss7 (SS7)؛ هذه تجلس فوق واجهة `/dev/dahdi`، برنامج تشغيل نواة DAHDI، وبرنامج تشغيل نواة الواجهة الخاصة بالبطاقة.](../images/10-legacy-fig09.png)

تنفيذ R2 ضروري لتثبيت مكتبة تُدعى OpenR2 (www.libopenr2.org)، التي طورها مويسيس سيلفا، ولإجراء تصحيح على Asterisk قبل التثبيت—إجراء بسيط يُعرض لاحقًا في هذا الفصل. لقد اجتازت المكتبة عدة اختبارات وتُستخدم في بيئات الإنتاج لدى عدد من عملائنا. في رأيي، ISDN هو دائمًا الخيار الأفضل إذا كان متاحًا. بعض المزودين يمكنهم الوصول إلى نظام الإشارة 7 (SS7)، وهو إشارة CCS متاحة بين شركات الهاتف. تتوفر حلول مملوكة ومفتوحة المصدر لـ SS7. تُستخدم المكتبة libss7 لدعم SS7 على Asterisk.

### إعداد قنوات الاتصالات في Asterisk

تهيئة بطاقة واجهة الهاتفية يتطلب عدة خطوات ضرورية. في هذا الفصل، سنعرض ثلاثة من أكثر السيناريوهات شيوعًا.

- الاتصال الرقمي باستخدام ISDN PRI
- الاتصال الرقمي باستخدام ISDN BRI
- الاتصال الرقمي باستخدام MFC/R2

هناك طريقتان لتكوين قنوات DAHDI. الأولى هي تكوينها يدوياً مع التحكم الكامل في جميع المعلمات. الطريقة الثانية هي استخدام الأداة dahdi_genconf لاكتشاف وتكوين البطاقات.

#### الكشف التلقائي والتهيئة

Thanks to the DAHDI development team, we now have automatic detection and configuration of the cards. Step 1: To generate the configuration automatically, use the utility dahdi_genconf, which will detect the card and generate the files /etc/dahdi/system.conf and dahdi-channels.conf.

```
dahdi_genconf
```

Step 2: في السطر الأخير من الملف chan_dahdi.conf، قم بتضمين الملف dahdi-channels.conf

```
#include dahdi_channels.conf
```

الخطوة 3: علّق على جميع الوحدات غير المستخدمة في ملف modules أو استخدم ببساطة:

```
dahdi_genconf modules
```

#### التكوين اليدوي

خيار آخر هو تكوين الواجهات يدويًا. أدناه بعض أمثلة التكوين لقنوات DAHDI.

##### المثال #1 – قناتان T1/ E1 باستخدام ISDN

الخطوات المطلوبة:

1. تثبيت TE205P أو TE210P
2. تكوين ملف `/etc/dahdi/system.conf`
3. تحميل برنامج تشغيل DAHDI
4. أداة `dahdi_test`
5. أداة `dahdi_cfg`
6. تكوين ملف `chan_dahdi.conf`
7. تحميل Asterisk والاختبار

الخطوة 1: تثبيت TE205P. قبل تثبيت TE205P، من المهم فهم الاختلافات بين بطاقات TE205P و TE210P. بطاقة TE210P تستخدم ناقل 64‑bit بجهد 3.3 فولت موجود تقريبًا فقط في اللوحات الأم للخوادم. احرص على عدم اختيار هذه البطاقة إذا لم يدعم عتادك ناقل 64‑bit بجهد 3.3 فولت. بطاقة TE205P تستخدم PCI بجهد 5 فولت، وهو ما يُوجد غالبًا في الحواسيب المكتبية. اخترنا بطاقة TE205P ذات المدى المزدوج لهذا المثال لأنها تسهل تحويلها إلى بطاقة ذات مدى واحد أو توسيعها إلى بطاقة ذات أربعة امتدادات. تُباع هذه البطاقات الآن تحت علامة Sangoma (سابقًا Digium).

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

تكوين بطاقات TDM الرقمية يختلف قليلاً عن تكوين نظيراتها التناظرية. أولاً، سنحتاج إلى تكوين امتدادات اللوحة ثم القنوات. تُرقم الامتدادات (spans) تسلسليًا اعتمادًا على ترتيب التعرف على البطاقات. بمعنى آخر، إذا كان لديك أكثر من بطاقة واجهة واحدة، يكون من الصعب معرفة أي امتداد يخص كل بطاقة. استخدم `dahdi_hardware` للتحقق من الأجهزة المثبتة على كل امتداد. مثال #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

مثال #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

مثال #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

الخطوة 3: تحميل برامج تشغيل النواة تحقق من برنامج التشغيل الذي تحتاج إلى تثبيته باستخدام dahdi_hardware.

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

للتحميل استخدم:

```
modprobe dahdi
modprobe wct2xxp
```

الخطوة 4: باستخدام dahdi_test، تحقق من الفواصل المفقودة للانقطاعات  
يمكنك التحقق من عدد الانقطاعات المفقودة باستخدام أداة dahdi_test المجمعة مع بطاقات DAHDI.  
القيمة التي تقل عن 99.987٪ تشير إلى وجود مشاكل محتملة.  
ستجد dahdi_test في

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

الخطوة 5: استخدام أداة dahdi_cfg  
هذا هو الإخراج الصحيح لأداة dahdi_cfg لامتداد E1 جزئي واحد (15 منفذ) واثنين من منافذ FXO.

```
#./dahdi_cfg -vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

الخطوة 6: تكوين DAHDI في الملف /etc/asterisk/chan_dahdi.conf المثال #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

مثال #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

مثال #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

استخدم signaling=bri_cpe_ptmp لـ BRI من نقطة إلى متعدد نقاط. حاليًا، لا يتم دعم BRI من نقطة إلى متعدد نقاط في وضع NT.

#### تحميل برامج تشغيل النواة

بعد تكوين برامج التشغيل، يمكنك ببساطة إعادة تشغيل الخادم. إذا قمت بتثبيت DAHDI باستخدام make config، لن تحتاج إلى القيام بأي شيء إضافي. سيتم تحميل برنامج تشغيل النواة تلقائيًا وتكوينه. ومع ذلك، في بعض الأحيان يكون من المفيد تحميل وإلغاء تحميل برامج التشغيل يدويًا. مثال:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

الأمر الأول يحمل برنامج التشغيل والثاني، dahdi_cfg، يطبق الإعدادات على برنامج تشغيل النواة.

### استكشاف الأخطاء وإصلاحها

أحيانًا لا تعمل الأشياء من المرة الأولى. دعنا نتحقق من بعض الموارد لاستكشاف أخطاء DAHDI. الخطوة 1: تحقق مما إذا كانت البطاقة يتم التعرف عليها من قبل نظام التشغيل. بطاقات Sangoma/Digium عادةً ما يتم التعرف عليها كمودم ISDN.

```
lspci -v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

الخطوة 2: تحقق مما إذا كان برنامج تشغيل النواة يتم تحميله بشكل صحيح باستخدام:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Step 3: Verify the status of alarms related to the physical layer of the connection. To verify the physical layer of the E1 connection, you may use the following Asterisk CLI command.

```
dahdi show status
```

تشير الإنذارات إلى مشاكل في المنفذ:  
الإنذار الأحمر: لا يمكن الحفاظ على المزامنة مع المفتاح البعيد. عادةً ما يكون ذلك مشكلة مادية، مثل عدم توافق شفرة الخط أو الإطار.  
الإنذار الأصفر: يشير إلى أن المفتاح البعيد في حالة الإنذار الأحمر. هذا يدل على أن المفتاح البعيد لا يتلقى إرسالاتك.  
الإنذار الأزرق: يتلقى جميع الـ 1 غير المؤطرة على جميع الفواصل الزمنية؛ أداة **dahdi_tool** لا تكتشف حاليًا إنذارًا أزرق.  
العودة إلى الذات (Loopback): يكون المنفذ إما في وضعية عودة إلى الذات محلية أو بعيدة.

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

Step 4: لاكتشاف المشكلات مع DAHDI على خادم Asterisk، تحقق أولاً مما إذا كانت القنوات يتم التعرف عليها باستخدام:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

الخطوة 5: تحقق من حالة طبقة ISDN المستوى 3، المعروفة أيضًا باسم q.931. يمكنك التحقق مما إذا كانت طبقة ISDN المستوى 3 مفعلة باستخدام: `pri show spans` (لسرد جميع الفواصل) أو `pri show span <n>` لفاصل محدد:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

استخدم `pri show spans` (plural) لسرد حالة جميع مسارات PRI المكوَّنة مرة واحدة.

تحقق من قناة محددة. dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: إذا بعد كل شيء لا تزال تواجه مشاكل، ابدأ بتصحيح الأخطاء في الـ pri span. هذا الأمر يتيح تصحيحًا مفصَّلًا لمكالمات ISDN. إنه أمر مهم عندما تعتقد أن شيئًا ما غير صحيح. يمكنك اكتشاف الأرقام التي تم طلبها بشكل خاطئ ومشكلات أخرى. أدناه نقدم مثالًا لمخرجات تصحيح الأخطاء لمكالمة ناجحة. ارجع إلى هذا المثال إذا احتجت إلى مقارنة مكالمة غير ناجحة بأخرى بدون مشاكل. نصيحة واحدة هي استخدام `core set verbose=0` لتلقي رسائل ISDN q.931 فقط.

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### خيارات التكوين في chan_dahdi.conf

تتوفر عدة خيارات في ملف chan_dahdi.conf. سيكون وصف جميع الخيارات مملاً وغير مفيد. هنا، سنفصل مجموعات الخيارات الرئيسية المتاحة لتوفير فهم أفضل.

#### General options (channel independent)

context: يحدد السياق الوارد.

```
context=default
```

channel: يعرّف القناة أو نطاق القنوات. كل تعريف قناة سيورث الخيارات المعرفة قبل الإعلان. يمكن التعرف على القنوات بشكل فردي أو في نفس السطر بفصلها بفواصل. يمكن تعريف النطاقات باستخدام “-”.

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: يسمح بمعاملة القنوات كمجموعة. إذا قمت بالاتصال برقم مجموعة بدلاً من رقم قناة، يتم استخدام أول قناة متاحة. إذا كانت القنوات هواتف، عند الاتصال بمجموعة، سترن جميع الهواتف في آن واحد. باستخدام الفواصل، يمكنك تحديد أكثر من مجموعة لنفس القناة.

```
group=1
group=3,5
```

language: تشغيل التعريب وتكوين اللغة. هذه الميزة ستُعد رسائل النظام للغة معينة. الإنجليزية هي اللغة الوحيدة التي تتوفر لها جميع الإرشادات من التثبيت القياسي. musiconhold: اختيار فئة الموسيقى أثناء الانتظار.

#### خيارات ISDN

switchtype: يعتمد على الـ PBX أو المفتاح المستخدم. في أوروبا وأمريكا اللاتينية، يُستخدم EuroISDN بشكل شائع.

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: مطلوب لبعض المفاتيح التي تحتاج إلى تحديد مخطط الاتصال. يتم تجاهل هذا الخيار من قبل العديد من المفاتيح. الخيارات الصالحة هي private, national, international, و unknown.

```
pridialplan = unknown
```

prilocaldialplan: ضروري لبعض المفاتيح، عادة غير معروف.

```
prilocaldialplan = unknown
```

overlapdial: يتم استخدام الاتصال المتداخل عندما تقوم بتمرير أرقام بعد إنشاء الاتصال. يمكنك استخدام ترقيم وضع الكتلة (overlapdial=no) أو وضع الأرقام (overlapdial=yes). يُستخدم وضع الكتلة غالبًا من قبل المشغلين.  
signaling: يضبط نوع الإشارة للقنوات اللاحقة. يجب أن تتطابق هذه المعلمات مع تلك الموجودة في ملف chan_dahdi.conf. الاختيارات الصحيحة تعتمد على القناة المتاحة. بالنسبة لـ ISDN قد تختار أحد الخيارات الخمسة:

- pri_cpe: يُستخدم عندما يكون الجهاز CPE، يُشار إليه أحيانًا بالعميل أو المستخدم أو التابع. هذا هو أبسط وأشهر شكل من الإشارة. أحيانًا، عندما تحاول الاتصال بـ PBX خاص، يكون الـ PBX قد تم تكوينه كـ CPE أيضًا. في هذه الحالة، استخدم إشارة pri_net في Asterisk.  
- pri_net: يُستخدم عندما يكون Asterisk متصلًا بـ PBX خاص مُكوَّن كـ CPE. غالبًا ما تُشار إلى الإشارة بالمضيف أو الرئيس أو الشبكة.  
- bri_cpe: يُستخدم عندما يكون Asterisk متصلًا كـ CPE إلى خط ISDN BRI trunk  
- bri_net: يُستخدم عندما يكون Asterisk متصلًا بهاتف ISDN أو PBX مُكوَّن كطرف نهائي (TE).  
- bri_cpe_ptmp: نفس bri_cpe، لكن في بنية نقطة إلى متعدد نقاط.

#### خيارات CallerID

تتوفر العديد من خيارات معرف المتصل. يمكن تعطيل بعضها، رغم أن معظمها مفعَّل افتراضيًا.  
usecallerid: يفعّل أو يعطّل نقل معرف المتصل للقنوات اللاحقة (Yes/No). ملاحظة: إذا كان نظامك يتطلب رنينين قبل الرد، جرّب تعطيل هذه الميزة حتى يرد فورًا.  
hidecallerid: يخفي معرف المتصل (Yes/No).  
calleridcallwaiting: يفعّل استقبال معرف المتصل أثناء إشارة الانتظار (Yes/No).  
callerid: يضبط سلسلة معرف المتصل لقناة محددة. يمكن تكوين المتصل بـ “asreceived” في واجهات الـ trunk لتمرير معرف المتصل إلى الأمام.

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

ملاحظة: معظم شركات الاتصالات تطلب منك تكوين معرف المتصل الصحيح. إذا لم تقم بتمرير معرف المتصل الصحيح، يجب ألا تتمكن من إجراء مكالمات صادرة عبر شركة الاتصالات. من ناحية أخرى، ستتمكن من استقبال المكالمات حتى بدون تكوين معرف المتصل.

#### خيارات جودة الصوت

هذه الخيارات تعدل بعض معلمات Asterisk التي تؤثر على جودة الصوت في قنوات DAHDI.

- **echocancel**: تعطيل أو تمكين إلغاء الصدى. يجب إبقاء هذه الميزة مفعلة. تقبل القيمة "yes" أو عدد النقرات. (شرح: كيف يعمل إلغاء الصدى؟ معظم خوارزميات إلغاء الصدى تعمل عن طريق إنشاء نسخ متعددة من الإشارة المستلمة، يتم تأخير كل نسخة بفاصل زمني صغير. يُسمى هذا التدفق الصغير "tap". عدد النقرات يحدد تأخير الصدى الذي يمكن إلغاؤه. تُؤخر هذه النسخ، وتُضبط، وتُطرح من الإشارة الأصلية. الحيلة هي ضبط الإشارة المؤخرة بدقة لتكون ما يلزم لإزالة الصدى.)
- **echocancelwhenbridged**: تمكين أو تعطيل مُلغي الصدى أثناء مكالمة TDM صافية. عادةً لا يكون ذلك مطلوبًا.
- **rxgain**: ضبط كسب استقبال الصوت إما لزيادة أو خفض مستوى الاستقبال (-100% إلى 100%).
- **txgain**: ضبط كسب إرسال الصوت إما لزيادة أو خفض مستوى الإرسال (-100% إلى 100%).

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### خيارات الفوترة

هذه الخيارات تغير الطريقة التي يتم بها تسجيل معلومات المكالمات في قاعدة بيانات سجلات تفاصيل المكالمات (CDR). **amaflags**: يؤثر على تصنيف الـ CDR. يقبل القيم التالية:

- billing
- documentation
- omit
- default

**accountcode**: يضبط رمز حساب لقناة محددة. يمكن أن يحتوي على أي قيمة أبجدية رقمية، عادةً اسم القسم أو اسم المستخدم.

```
accountcode=finance
amaflags=billing
```

### تكوين MFC/R2

MFC/R2 يُستخدم في عدة دول في أمريكا اللاتينية، الصين، وأفريقيا بالإضافة إلى بعض الدول الأوروبية. ISDN أفضل ومُفضَّل إذا كان متاحًا في منطقتك.

#### فهم المشكلة

البطاقة المستخدمة لإشارة MFC/R2 هي نفسها المستخدمة لإشارة ISDN. من الممكن استخدام MFC/R2 على قنوات DAHDI باستخدام المكتبة المسماة libopenR2 (www.libopenr2.com). هذه المكتبة لم تكن جزءًا من إصدارات Asterisk قبل 1.6.2.

##### فهم بروتوكول MFC/R2

يجمع بروتوكول MFC/R2 بين الإشارة داخل النطاق وخارج النطاق. يتم توجيه إشارة العنوان داخل النطاق باستخدام مجموعة من النغمات بينما يتم نقل معلومات القناة عبر الفتحة الزمنية 16 كإشارة خارج النطاق.

**إشارة الخط (ITU-T Q.421).** في الفتحة الزمنية 16، يستخدم كل قناة صوتية أربعة بتات ABCD للإشارة إلى حالاتها والتحكم في المكالمة. نادراً ما تُستَخدم البتات C و D. في بعض البلدان، يمكن استخدامها للقياس (القياس النبضي للفوترة). في محادثة عادية، يكون هناك طرفان يعملان: المتصل والطرف المتصل إليه. تُسمى الإشارة الصادرة من جانب المتصل إشارةً أمامية بينما يستخدم الطرف المتصل إليه إشارةً خلفية. سنُشير إلى Af و Bf للإشارة الأمامية وإلى Ab و Bb للإشارة الخلفية.

| الحالة | ABCD forward | ABCD backward |
| --- | --- | --- |
| خامل/محرّر | 1001 | 1001 |
| مُستولى | 0001 | 1001 |
| تأكيد الاستيلاء | 0001 | 1101 |
| مُجاب | 0001 | 0101 |
| مسح خلفي | 0001 | 1101 |
| مسح أمامي (قبل مسح خلفي) | 1001 | 0101 |
| مسح أمامي (تأكيد الانقطاع) | 1001 | 1001 |
| محجوز | 1001 | 1101 |

MFC/R2 تم تعريفه من قبل ITU. للأسف، قامت عدة دول بتخصيص المعيار وفقًا لاحتياجاتها الخاصة. نتيجةً لذلك، ظهرت اختلافات في المعايير بين الدول.

**الإشارات بين السجلات (ITU-T Q.441).** يستخدم إشارة MFC/R2 مزيجًا من نغمتين. الجداول أدناه تُظهر المعيار ITU.

مجموعة الإشارة I (إلى الأمام):

| الوصف | إشارة التوجيه |
| --- | --- |
| الرقم 1 | I-1 |
| الرقم 2 | I-2 |
| الرقم 3 | I-3 |
| الرقم 4 | I-4 |
| الرقم 5 | I-5 |
| الرقم 6 | I-6 |
| الرقم 7 | I-7 |
| الرقم 8 | I-8 |
| الرقم 9 | I-9 |
| الرقم 0 | I-10 |
| مؤشر رمز الدولة، مطلوب كابح صدى نصف صادر | I-11 |
| مؤشر رمز الدولة، لا يلزم كابح صدى | I-12 |
| مؤشر اختبار المكالمة | I-13 |
| مؤشر رمز الدولة، تم إدراج كابح صدى نصف صادر | I-14 |
| غير مستخدم | I-15 |

Signal group II (forward):

| Description | Forward signal |
| --- | --- |
| مشترك بدون أولوية | II-1 |
| مشترك مع أولوية | II-2 |
| معدات صيانة | II-3 |
| احتياطي | II-4 |
| مشغل | II-5 |
| نقل بيانات | II-6 |
| مشترك أو مشغل بدون مرفق تحويل أمامي | II-7 |
| نقل بيانات | II-8 |
| مشترك مع أولوية | II-9 |
| مشغل مع مرفق تحويل أمامي | II-10 |
| احتياطي | II-11 |
| احتياطي | II-12 |
| احتياطي | II-13 |
| احتياطي | II-14 |
| احتياطي | II-15 |

مجموعة الإشارة A (عكسية):

| الوصف | الإشارة العكسية |
| --- | --- |
| إرسال الرقم التالي (n+1) | A-1 |
| إرسال الرقم قبل الأخير (n-1) | A-2 |
| العنوان مكتمل، التحويل إلى استقبال إشارات المجموعة ب | A-3 |
| ازدحام في الشبكة الوطنية | A-4 |
| إرسال فئة الطرف المتصل | A-5 |
| العنوان مكتمل، الفوترة، إعداد ظروف الكلام | A-6 |
| إرسال الرقم قبل ما قبل الأخير (n-2) | A-7 |
| إرسال الرقم قبل ما قبل ما قبل الأخير (n-3) | A-8 |
| احتياطي | A-9 |
| احتياطي | A-10 |
| إرسال مؤشر رمز الدولة | A-11 |
| إرسال رقم اللغة أو التمييز | A-12 |
| إرسال طبيعة الدائرة | A-13 |
| طلب معلومات حول استخدام كابح الصدى | A-14 |
| ازدحام في تبادل دولي أو في مخرجه | A-15 |

مجموعة الإشارة B (للخلف):

| Description | Backward signal |
| --- | --- |
| احتياطي | B-1 |
| إرسال نغمة معلومات خاصة | B-2 |
| خط المشترك مشغول | B-3 |
| ازدحام (بعد تحويل المجموعة A إلى B) | B-4 |
| رقم غير مخصص | B-5 |
| خط المشترك متاح، رسوم | B-6 |
| خط المشترك متاح، بدون رسوم | B-7 |
| خط المشترك معطل | B-8 |
| احتياطي | B-9 |
| احتياطي | B-10 |
| احتياطي | B-11 |
| احتياطي | B-12 |
| احتياطي | B-13 |
| احتياطي | B-14 |
| احتياطي | B-15 |

#### تسلسل MFC/R2

التسلسل التالي يوضح مكالمة تنشأ من امتداد Asterisk إلى طرف في PSTN. يقوم PSTN بإنهاء المكالمة وإنهاء الاتصال.

![تدفق مكالمة كامل لـ MFC/R2 بين Asterisk وشبكة الهاتف: يتم تبادل إشارات الخط (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) في الفتحة الزمنية 16، وتنتقل الأرقام التي تم طلبها وإشارات "إرسال الرقم التالي" العكسية (المجموعات I/A/B) داخل النطاق، وتصل النغمات السمعية إلى المشترك.](../images/10-legacy-fig11.png)

### كيفية استخدام برنامج تشغيل libopenr2

المشروع الذي بدأه مويسيس سيلفا استُلهم من برنامج تشغيل قناة Unicall الذي كتبه ستيف أندروود. مكتبة OpenR2 هي حالياً أكثر حل برمجي استقراراً لـ Asterisk. باستخدام هذا الحل، يمكننا استعمال أي بطاقة رقمية متوافقة مع DAHDI. سابقاً، كانت الحلول المملوكة فقط متاحة لـ MFC/R2، وأحد أفضل ما استخدمته هو ذلك المتاح من Khomp، www.khomp.com.br. في Asterisk 22، يتم تضمين دعم MFC/R2 عبر libopenR2 عندما تكون المكتبة موجودة أثناء التجميع — لا يلزم أي تصحيح خارجي. الخطوات أدناه توضح عملية التثبيت اليدوي التاريخية للرجوع إليها؛ على الأنظمة الحديثة، قم بتثبيت `libopenr2-dev` من مدير الحزم الخاص بتوزيعتك قبل تشغيل `./configure`، ثم فعّل `chan_dahdi` في `make menuselect`.

الخطوات أدناه تُنشئ openr2 و Asterisk من مستودعات Git الحالية. يتم الاحتفاظ بها كمرجع للمواقع التي تُبني من المصدر؛ في توزيعة حديثة يمكنك عادةً تخطيها تمامًا عن طريق تثبيت حزمة `libopenr2-dev` وبناء Asterisk 22 المعبأ، لأن `chan_dahdi` يُجمّع دعم R2 مباشرةً ضد libopenr2 دون أي تصحيح خارجي.

Step 1: قم بتثبيت أدوات البناء التي تحتاجها.

```
apt-get install git
```

الخطوة 2: استنساخ مكتبة openr2 ومصدر Asterisk. لا حاجة لشجرة مُعدَّلة خاصة على Asterisk 22 — فعملية السحب الأصلية تُبني دعم R2 طالما أن libopenr2 موجود.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

الخطوة 3: تجميع وتثبيت يرجى عمل BACK UP لخادمك قبل المتابعة.

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

ملاحظة: لا تقم بتنفيذ “make samples” لتجنب الكتابة فوق ملفات التكوين الخاصة بك.

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

لنفترض أن لديك بطاقة بواجهة E1 واحدة.

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

الخطوة 5: تشغيل الأمر dahdi_cfg لتطبيق التغييرات على برنامج التشغيل:

```
dahdi_cfg -vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

Step 5: Change the file chan_dahdi.conf

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Step 6: Change the dial plan in the file extensions.conf

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

ملاحظة: بعض شركات الاتصالات لا تقبل المكالمات بدون معرف المتصل. يرجى ضبط معرف المتصل إلى أحد أرقام الـ DID المخصصة من قبل المشغل. في بعض البلدان، لا تكون هذه الخطوة ضرورية.  
الخطوة 7: اختبار الحل: الآن، مع وجود امتداد في السياق `from-internal`، اتصل بأي رقم وراقب وحدة التحكم. تحقق مما إذا كانت هناك أية أخطاء تحدث.  
-- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack  
-- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack  

#### Debugging OpenR2

لكشف الأخطاء في المكالمات، يمكنك تفعيل وضع التصحيح. للقيام بذلك، اتبع الخطوات أدناه.

1. حرر الملف `chan_dahdi.conf` وأضف الأسطر الثلاثة التالية إلى الإعدادات:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. أعد تشغيل خادم Asterisk
3. اختبر المكالمة وتحقق من ملفات المكالمات في `/var/log/asterisk/mfcr2/span1`

فيما يلي تتبع لمكالمة عادية. قارنها بما تتلقاه في مكالمتك.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2 Configuration

الخيارات موثقة داخل الملف chan_dahdi.conf. بعض أهم الخيارات موضحة هنا. المعلمات الإلزامية: mfcr2_variant, mfcr2_max_ani و mfcr2_max_dnis. mfcr2_variant: نسخة الدولة.

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: الحد الأقصى لعدد أرقام ANI المطلوب طلبها  
mfcr2_max_dnis: الحد الأقصى لعدد أرقام DNIS المطلوب طلبها  
mfcr2_get_ani_first: ما إذا كان يجب الحصول على ANI قبل DNIS (مطلوب من قبل بعض شركات الاتصالات)  
mfcr2_category: فئة المتصل. يمكنك تعيين المتغير MFCR2_CATEGORY قبل بدء المكالمة  
mfcr2_logdir: الدليل لتسجيل ملفات المكالمات. (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files: ما إذا كان يجب تسجيل المكالمات  

- mfcr2_logging: قيم التسجيل  
- cas – بتات ABCD للإرسال والاستقبال  
- mf – نغمات متعددة التردد  
- stack – إخراج مفصل لمكدس القناة والسياق  
- all – جميع الأنشطة  
- nothing – لا تسجل شيئًا  

mfcr2_mfback_timeout: هذه القيمة تستحق الذكر. أحيانًا إذا كنت تتصل بهاتف محمول أو أي مكالمة تستغرق وقتًا طويلاً لإكمالها، قد ينتهي مهلة هذا المعامل، لذا يتم تغييره غالبًا لضبط الأداء. إذا لم تُكمل بعض مكالماتك، فهذا هو المعامل الذي يجب تغييره أولاً.  
mfcr2_metering_pulse_timeout: تُستخدم النبضات في بعض متغيرات R2 للإشارة إلى التكلفة  
mfcr2_allow_collect_calls: في البرازيل، يُستخدم النغمة II-8 للإشارة إلى مكالمة جمع؛ يتيح لك هذا المعامل حظر مكالمات الجمع.  
mfcr2_double_answer: يُستخدم أيضًا لتجنب مكالمات الجمع عندما تكون إجابة مزدوجة مطلوبة. مع double_answer=yes تقوم فعليًا بحظر مكالمات الجمع.  
mfcr2_immediate_accept: يتيح لك تخطي استخدام إشارات المجموعة B/II والانتقال مباشرة إلى حالة القبول.  
mfcr2_forced_release: يتيح لك تسريع إنهاء المكالمة؛ يعمل مع المتغير البرازيلي.  

#### ANI and DNIS

التعريف الآلي للرقم (ANI) هو رقم المتصل. خدمة التعريف برقم الطلب (DNIS) هي الرقم الذي تم الاتصال به أو، بعبارة أخرى، الرقم الذي تم طلبه. عند استلام مكالمة، عادةً ما يتم تمرير آخر أربعة أرقام إلى الـ PBX في عملية تُعرف بالاتصال الداخلي المباشر (DID). رقم ANI هو في الواقع هوية المتصل (Caller ID). سيحتوي ANI على امتداد المتصل عند الطلب بينما سيحتوي DNIS على وجهة المكالمة. من المهم تكوين هذه المعاملات بشكل صحيح. بعض المحولات تُرسل فقط الأربعة أرقام الأخيرة بينما تُرسل أخرى الرقم الكامل.  

### DAHDI channel format

قنوات DAHDI تستخدم الصيغة التالية في مخطط الطلب:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

أمثلة:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## بروتوكول IAX2

في هذا الفصل، سنتعلم عن بروتوكول Inter-Asterisk eXchange (IAX)، بما في ذلك نقاط قوته وضعفه. سيتم أيضًا تغطية تفاصيل مثل وضع الـ trunk وربط خادمين Asterisk معًا. جميع الإشارات في هذا المستند تتطابق مع نسخة IAX 2.

بروتوكول IAX يوفر نقل الوسائط والإشارة للصوت والفيديو. يُعد IAX مبتكرًا جدًا؛ فهو يوفر عرض النطاق الترددي في وضع الـ trunk ويكون أبسط بكثير من SIP عندما تحتاج إلى عبور الـ NAT. الاستخدام الأساسي لـ IAX في الوقت الحالي هو ربط خوادم Asterisk معًا. تم إنشاء IAX في الأصل للصوت، لكنه يمكنه أيضًا استيعاب الفيديو وتدفقات الوسائط المتعددة الأخرى.

IAX استُلهم من بروتوكولات VoIP أخرى، مثل SIP و MGCP. بدلاً من استخدام بروتوكولين منفصلين للإشارة والإعلام، قام IAX بدمجهما لإنشاء بروتوكول فريد. لا يستخدم IAX RTP لنقل الإعلام؛ بل يدمج الإعلام في نفس اتصال UDP.

**الحالة في Asterisk 22.** `chan_iax2` ما زال مدرجًا ومدعومًا بالكامل في Asterisk 22 LTS، لذا كل ما في هذا القسم يظل صالحًا. ومع ذلك، فإن IAX2 بروتوكول قديم يرى قليلًا من النشر الجديد: الصناعة قد توحدت إلى حد كبير على SIP (via `chan_pjsip` in Asterisk 22) لكل من توصيل مزودي الخدمات والربط بين الخوادم. الميزة المتبقية الرئيسية لـ IAX2 هي تصميمه ذو المنفذ الواحد — جميع الإشارات والوسائط تمر عبر منفذ UDP واحد (4569 افتراضيًا)، مما يبسط إعداد جدار الحماية وNAT مقارنةً بـ SIP بالإضافة إلى تدفقات RTP المنفصلة. بالنسبة إلى وصلة Asterisk-to-Asterisk جديدة حيث لا يُعد NAT مصدر قلق، يُنصح باستخدام وصلة PJSIP كنهج حديث؛ تم تغطية IAX2 هنا لأنه لا يزال خيارًا صالحًا، خاصةً عندما يمكن فتح منفذ UDP واحد فقط عبر جدار الحماية.

### الأهداف

بنهاية هذا الفصل، يجب أن تكون قادرًا على:

- تحديد نقاط القوة والضعف في بروتوكول IAX
- وصف سيناريوهات الاستخدام لبروتوكول IAX
- وصف مزايا وضع trunk لبروتوكول IAX
- تكوين iax.conf للهواتف
- تكوين iax.conf للاتصال بمزود VoIP
- تكوين iax.conf للربط بين أنظمة Asterisk
- فهم مصادقة IAX

### تصميم IAX

الأهداف الرئيسية لتصميم IAX هي:

- لتقليل النطاق الترددي المطلوب لنقل الوسائط والإشارة
- لتوفير شفافية NAT
- لتكون قادرًا على نقل معلومات dial plan
- لدعم الاستخدام الفعال للpaging والintercom

IAX هو بروتوكول إشارة وإعلام وسائط من نظير إلى نظير يشبه SIP دون استخدام RTP. النهج الأساسي هو دمج تدفقات الوسائط المتعددة عبر اتصال UDP واحد بين مضيفين. أكبر فائدة لهذا النهج هي بساطته عند عبور الاتصالات عبر NAT، التي توجد بانتظام في مودمات xDSL. يستخدم IAX منفذًا واحدًا، UDP 4569 افتراضيًا، ثم يستخدم رقم مكالمة مكوّن من 15 بتًا لدمج جميع التدفقات. يستخدم بروتوكول IAX عمليات التسجيل والمصادقة المشابهة لبروتوكول SIP. يمكن العثور على وصف للبروتوكول على http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt

![بروتوكول IAX ي multiplex العديد من المكالمات بين نقطتي طرف عبر منفذ UDP واحد (4569 افتراضيًا)، باستخدام رقم مكالمة 15‑بت للحفاظ على فصل التدفقات — مما يجعل اجتياز NAT بسيطًا.](../images/10-legacy-fig12.png)

### استخدام النطاق الترددي

إن عرض النطاق الترددي المستخدم في شبكات VoIP يتأثر بعدة عوامل؛ الترميزات ورؤوس البروتوكول هي الأكثر أهمية. يتمتع بروتوكول IAX بميزة مفاجئة تُسمى وضع trunk، حيث يقوم بتعدد الإرسال لعدة مكالمات باستخدام رأس واحد. من خلال تجربة حاسبة عرض النطاق الترددي في Asterisk، ستلاحظ كيف يمكن لـ trunks IAX أن توفر لك ما يصل إلى 80 % من حركة المرور عند وجود مكالمات متعددة.

![مقارنة بين عبء IAX و SIP: تحتاج مكالمتان SIP/RTP إلى حزمتين (40 بايت من الحمولة تحت 156 بايت من العبء)، بينما وضع trunk في IAX2 يحمل المكالمتين في حزمة واحدة (40 بايت من الحمولة تحت 66 بايت فقط من العبء) عن طريق مشاركة رأس IP/UDP واحد عبر العديد من الإطارات الصغيرة.](../images/10-legacy-fig13.png)

### تسمية القناة

من المهم فهم قواعد تسمية القنوات لأنك ستستخدم هذه الأسماء عند تحديد قناة في مخطط الاتصال. تنسيق اسم قناة IAX المستخدم للقنوات الصادرة هو:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — معرف المستخدم على الطرف البعيد، أو اسم العميل المُكوَّن في iax.conf  
- `<secret>` — كلمة المرور. بدلاً من ذلك يمكن أن يكون اسم ملف مفتاح RSA بدون الامتداد النهائي (.key أو .pub) ومُحاط بأقواس مربعة  
- `<peer>` — اسم الخادم للاتصال به  
- `<portno>` — رقم المنفذ للاتصال  
- `<exten>` — الامتداد في خادم Asterisk البعيد  
- `<context>` — السياق في خادم Asterisk البعيد  
- `<options>` — الخيار الوحيد المتاح هو 'a'، أي 'طلب الإجابة التلقائية'  

#### مثال على القنوات الصادرة:

القنوات الصادرة تُظهر في وحدة تحكم Asterisk.

- `IAX2/8590:secret@myserver/8590@default` — اتصل بامتداد 8590 في myserver. يستخدم 8590:secret كزوج الاسم/كلمة المرور  
- `IAX2/iaxphone` — اتصل بـ "iaxphone"  
- `IAX2/judy:[judyrsa]@somewhere.com` — اتصل بـ somewhere.com باستخدام judy كاسم مستخدم ومفتاح RSA للمصادقة  

#### صيغة قناة IAX الواردة هي:

القنوات الواردة تُظهر في وحدة تحكم Asterisk.

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — اسم المستخدم إذا كان معروفًا  
- `<host>` — المضيف المتصل  
- `<callno>` — رقم المكالمة المحلي  

مثال على قناة واردة:

- `IAX2[flavio@8.8.30.34]/10` — رقم المكالمة 10 من عنوان IP 8.8.30.34 باستخدام flavio كمستخدم.  
- `IAX2[8.8.30.50]/11` — رقم المكالمة 11 من عنوان IP 8.8.30.50.  

### استخدام IAX  

يمكنك استخدام IAX بطرق متعددة. في هذا القسم، سنوضح لك كيفية إعداد IAX لعدة سيناريوهات، بما في ذلك:

- ربط هاتف نرمجي باستخدام IAX  
- ربط IAX بمزود VoIP باستخدام IAX  
- ربط خادمين باستخدام IAX  
- ربط خادمين باستخدام IAX في وضع trunk  
- استكشاف أخطاء اتصال IAX  
- استخدام مفاتيح RSA الزوجية للمصادقة  

#### ربط هاتف نرمجي باستخدام IAX  

يدعم Asterisk هواتف IP تعتمد على IAX مثل ATCOM و ATA القديم من Digium (المسمى IAXy) وكذلك الهواتف النرمجية التي لا تزال تنفذ بروتوكول IAX2. العملية للهواتف النرمجية، ATA، والهواتف الصلبة متشابهة. لتكوين جهاز IAX، تحتاج إلى تحرير ملف iax.conf في ‎/etc/asterisk

```
directory.
```

We will use an IAX2-capable softphone as an example.

1. Make a backup of the original `iax.conf` file using:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. ابدأ بتحرير ملف `iax.conf` جديد:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; معامل مهم جدًا، يغيّر الترميزات المتاحة

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

لقد حاولت الحفاظ على الأسطر الافتراضية (غير المعلقة) في ملف العينة. تم تعديل المعلمات التالية:

```
bandwidth=high
```

هذا السطر يؤثر على اختيار الـ codec. استخدام الإعداد العالي يسمح باختيار codec عالي النطاق الترددي وعالي الجودة مثل g.711 المحدد بواسطة كلمة المفتاح ulaw. إذا احتفظت بالمعامل الافتراضي، لن تتمكن من اختيار ulaw. في هذه الحالة، سيظهر لك Asterisk الرسالة “no codec available” للتكوين أدناه.

```
disallow=all
allow=ulaw
```

في الأوامر الموضحة أعلاه، قمنا بتعطيل جميع الـ codecs وتمكين ulaw فقط. في الشبكات المحلية (LANs)، يفضّل معظم الأشخاص استخدام ulaw لأنه لا يستهلك موارد المعالج كثيرًا ويوفر دورات CPU. وعلى الرغم من استهلاكه لمزيد من النطاق الترددي، يُعتبر هذا الـ codec مفضلاً لأن الشبكات المحلية عادةً ما تكون ذات سرعة 100 ميغابت إيثيرنت أو حتى جيجابت. مكالمة صوتية تستخدم ulaw تستهلك تقريبًا 100 كيلوبت في الثانية من النطاق الترددي في شبكتك، وهو استهلاك خفيف جدًا بالنسبة لشبكات LAN عالية السرعة اليوم. في الشبكات الواسعة (WAN) أو الإنترنت، عادةً ما يتم تعطيل ulaw، مع التضحية ببعض دورات CPU المتاحة من خلال ضغط الصوت للحصول على استخدام أفضل للنطاق الترددي. توفر الـ codecs gsm و g729 و ilbc أيضًا عامل ضغط جيد.

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

في الأوامر أعلاه، قمنا بتعريف صديق يُدعى [2003]. السياق هو الافتراضي (في المختبرات الأولى نستخدم دائمًا السياق الافتراضي لتجنب الالتباس؛ سيتم شرح هذا السياق بالكامل عندما نغطي مخطط الاتصال). السطر “host=dynamic” يوفر تسجيلًا ديناميكيًا لعنوان IP الخاص بالهاتف.

3. قم بتنزيل وتثبيت برنامج هاتف softphone يدعم IAX2. يمكنك اختيار أي برنامج softphone لا يزال يدعم بروتوكول IAX2 للمختبر.  
4. قم بتهيئة حساب IAX في العميل (عادةً *Add account* → IAX). لاحظ أن برنامج SipPulse Softphone يدعم SIP فقط ولا يمكنه التسجيل عبر IAX2، لذا لاختبار IAX تحتاج إلى عميل لا يزال يدعم هذا البروتوكول.

5. قم بتهيئة ملف `extensions.conf` لاختبار جهاز IAX الخاص بك.

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

الآن يمكنك إجراء مكالمات بين هواتف SIP التي تم إنشاؤها في الفصل 3 وهاتف IAX الذي تم إنشاؤه في المختبر.

#### الاتصال بمزود VoIP باستخدام IAX

بعض مزودي VoIP يدعمون IAX. يمكنك بسهولة العثور على مزود IAX بالبحث عن “IAX providers”. استخدام مزود IAX منطقي للغاية لأن IAX يمكنه توفير الكثير من النطاق الترددي، ويتجاوز NAT بسهولة، ويمكنه المصادقة باستخدام أزواج مفاتيح RSA.

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

عدد مزودي VoIP التجاريين القادرين على IAX قد انخفض بشكل حاد خلال الإصدارات الأخيرة من Asterisk؛ معظم المزودين الآن يقدمون خطوط SIP/PJSIP حصراً. قبل الالتزام بمزود IAX، تأكد من أنهم يحافظون بنشاط على بنية IAX الخاصة بهم. بالنسبة لتكامل مزود جديد، يُنصح باستخدام خط PJSIP (الفصل 3) كبديل.

#### الاتصال بمزود باستخدام IAX

الخطوة 1: افتح حساباً لدى مزودك المفضل. سيزودك المزود بثلاثة أشياء.

- Name
- Secret
- IP address or Host name
- RSA public key

الخطوة 2: قم بتهيئة ملف iax.conf لتسجيل Asterisk الخاص بك مع المزود. أضف السطور التالية إلى قسم [general] في الملف.

```
[general]
register=>name:secret@hostname/2003
```

في التعليمات الموضحة أعلاه، قمت بالتسجيل لدى موفر الخدمة باستخدام حسابك وكلمة المرور. في اللحظة التي تتلقى فيها مكالمة، سيتم تحويلها إلى الامتداد 2003.

```
[name]
```

- ; اسم حسابك أو رقمك

```
type=peer
secret=secret
; Your password
host=hostname
```

في التعليمات الموضحة أعلاه، أنشأنا peer يتCorrespond للمزود لأغراض الاتصال.

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

هذا مطلوب للمصادقة باستخدام RSA. استخدام المفتاح العام من موفر الخدمة يضمن لك أن المكالمة المستلمة هي حقًا من الموفر الحقيقي. إذا حاول أي شخص آخر استخدام نفس المسار، فلن يتمكن من المصادقة لأنه لا يملك المفتاح الخاص المقابل. الخطوة 4: جرّب الاتصال. لاختبار الاتصال، اتصل بأي رقم. بعض البائعين يوفرون اختبار صدى. للقيام بذلك، يرجى تعديل ملف **extensions.conf**.

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

انتقل إلى سطر أوامر Asterisk وقم بتنفيذ أمر reload. للتحقق مما إذا كان Asterisk مسجلاً لدى المزود، استخدم الأمر التالي.

```
*CLI>reload
*CLI>iax2 show register
```

الآن ما عليك سوى طلب *98 من برنامج softphone المتصل بخادم Asterisk.

#### ربط خادمين Asterisk عبر خط IAX

من السهل جداً ربط خادم بآخر. لن تحتاج إلى تسجيلهما لأن عناوين IP معروفة مسبقاً. سيتعين عليك إنشاء الـ peers والمستخدمين في ملف iax.conf. جميع التحويلات في موقع HQ تبدأ بـ 20 متبوعة برقمين (مثال، 2000). في الفرع، جميع التحويلات تبدأ بـ 22 متبوعة برقمين (مثال، 2200). سنستخدم الخط. ستحتاج إلى مصدر توقيت DAHDI لتفعيل هذه الميزة. الخطوة 1: حرّر ملف iax.conf في خادم الفرع.

![ربط خادمين Asterisk عبر خط IAX: خادم HQ (192.168.1.1، التحويلات 20xx) وخادم الفرع (192.168.1.2، التحويلات 22xx) يتواصلان عبر خط IAX واحد — لا حاجة للتسجيل لأن عناوين IP ثابتة ومعروفة.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

# الخطوة 2: تكوين ملف extensions.conf في الخادم الفرعي

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

الخطوة 3: Configure the iax.conf file in the HQ server

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

الخطوة 4: قم بتكوين ملف extensions.conf في الخادم الرئيسي.

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![The IAX authentication decision flow for an incoming call: Asterisk branches on whether a username is provided, whether it matches a section, whether the source IP is allowed, and whether the secret (plaintext, MD5, or RSA) matches — accepting the call with that section's context and peer options, or denying it.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

إذا كان للاتصال اسم مستخدم محدد، مثل:

- guest
- iaxtel
- iax-gateway
- iax-friend

سوف يحاول Asterisk توثيق المكالمة باستخدام الإدخال المقابل فقط في ملف iax.conf. إذا تم تحديد أي أسماء أخرى، سيتم رفض المكالمة. إذا لم يُحدد أي مستخدم، سيحاول Asterisk توثيق الاتصال كـ guest. ومع ذلك، إذا لم يكن guest موجودًا، سيحاول أي اتصال آخر يمتلك سرًا مطابقًا. بعبارة أخرى، إذا لم يكن لديك قسم guest في ملف iax.conf الخاص بك، قد يحاول مستخدم خبيث تخمين أي سر مطابق بعدم تحديد اسم المستخدم. تُطبق قيود الحظر/السماح لعناوين IP أيضًا. طريقة جيدة لتجنب تخمين السر هي استخدام توثيق RSA. طريقة أخرى هي تقييد عناوين IP المسموح لها بالاتصال.

#### قيود عنوان IP

يتم التحكم في الوصول باستخدام سطري `permit` و `deny`:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

القواعد تُفسَّر بالتسلسل، ويتم تقييم جميعها (هذا المفهوم مختلف عن قوائم التحكم بالوصول التي توجد عادةً في الموجهات وجدران الحماية). التعليمات المطابقة الأخيرة تحل محل السابقة.

مثال #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

سيتم رفض أي حزمة من شبكة 192.168.0.0/24.

مثال #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

سيسمح هذا بأي حزمة، لأن التعليمة الأخيرة تتجاوز الأولى.

#### الاتصالات الصادرة

تستحوذ الاتصالات الصادرة على معلومات المصادقة باستخدام الطرق التالية:

- وصف قناة IAX2 الممرّر بواسطة تطبيق `dial()`.
- إدخال مع `type=peer` أو `type=friend` في ملف `iax.conf`.
- مزيج من الطريقتين.

#### ربط خادمين Asterisk باستخدام مفاتيح RSA

يمكن استخدام IAX مع مصادقة قوية باستخدام مفاتيح RSA غير المتماثلة. وفقًا لكود المصدر (`res_krypto.c`)، يستخدم Asterisk مفاتيح RSA مع خوارزمية SHA-1 لتلخيص الرسائل بدلاً من MD5 الأضعف. أدناه دليل خطوة بخطوة لإعداد خادمين باستخدام مفاتيح RSA.

##### تكوين الخادم للفرع

الخطوة 1: توليد مفاتيح RSA في خادم الفرع

```
astgenkey -n
```

عند الطلب، استخدم اسم المفتاح **branch**. لقد استخدمنا المعامل **–n** لتجنب تمرير عبارة مرور كلما أعاد **Asterisk** التهيئة. إذا كنت ترغب في تحسين الأمان، لا تستخدم **–n** وابدأ **Asterisk** بالأمر **asterisk -i**. الخطوة 2: انسخ المفاتيح إلى الدليل **/var/lib/asterisk/keys**

```
cp branch.* /var/lib/asterisk/keys
```

# الخطوة ٣: نسخ المفتاح العام إلى خادم المقر الرئيسي

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

Step 4: Edit the iax.conf file in the Branch server.

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

الخطوة 8: تكوين ملف extensions.conf في خادم الفرع

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### تكوين الخادم للمقر الرئيسي

الخطوة 1: إنشاء مفاتيح RSA في خادم المقر الرئيسي

```
astgenkey -n
```

عند الطلب استخدم اسم المفتاح hq. الخطوة 2: انسخ المفاتيح إلى الدليل /var/lib/asterisk/keys

```
cp hq.* /var/lib/asterisk/keys
```

الخطوة 3: نسخ المفتاح العام إلى خادم BRANCH

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

الخطوة 4: تكوين ملف iax.conf في الخادم الرئيسي

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

الخطوة 10: قم بتكوين ملف extensions.conf في الخادم الرئيسي.

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### ملف تكوين iax.conf

ملف iax.conf يحتوي على عدة معلمات؛ من الممل وغير المفيد مناقشة كل معلمة على حدة. يمكن العثور على جميع المعلمات مع شرحها في ملف العينة. في الويكي www.voip-info.org ستجد معلومات مفصلة عن كل واحدة. هنا سنعرض بعض أهم المعلمات لتكوين القسم العام، والأقران، والمستخدمين.

#### قسم [General]

عناوين الخادم:

- `bindport = <portnum>` — يحدد منفذ UDP الخاص بـ IAX. القيمة الافتراضية هي 4569.
- `bindaddr = <ipaddr>` — استخدم 0.0.0.0 لربط Asterisk بجميع الواجهات، أو حدد عنوان IP لواجهة معينة.

اختيار الترميز:

- `bandwidth = [low|medium|high]` — High = جميع الترميزات؛ Medium = جميع الترميزات ما عدا ulaw و alaw؛ Low = ترميزات منخفضة النطاق الترددي.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — ضبط دقيق لاختيار الترميز.

### مخزن التذبذب (Jitter buffer)

التذبذب هو تغير التأخير بين الحزم. وهو أهم عامل يؤثر على جودة الصوت. يُستخدم مخزن التذبذب لتعويض تغير التأخير. فهو يضحي بالكمون لصالح تقليل التذبذب. يمكنك تشبيه مخزن التذبذب بخزان ماء. كلاهما يمكن أن يتلقى حزم أو ماء على فترات غير منتظمة، لكنه سيُخرج تدفقًا منتظمًا في النهاية.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

التذبذب الصغير (أي أقل من 20 مللي ثانية) عادةً لا يُلاحظ. ومع ذلك، التذبذب فوق هذا المستوى يكون مزعجًا. يجب الحفاظ على الكمون أو التأخير أقل من 150 مللي ثانية. إنشاء مخزن تذبذب سيضحي ببعض التأخير لتقليل التذبذب—مفهوم يُعرف بـ “ميزانية التأخير”. يمكنك التأثير على مخزن التذبذب باستخدام هذه المعلمات:

- Jitterbuffer=<yes/no> – يفعّل أو يعيّق
- Dropcount=<number> - الحد الأقصى لعدد الإطارات التي يجب تأخيرها في الثانيتين الأخيرتين. الإعداد الموصى به هو 3 (1.5% من الإطارات المسقطة)
- Maxjitterbuffer=<ms> - عادةً أقل من 100 مللي ثانية
- Maxexcessbuffer=<ms> - إذا تحسّن تأخير الشبكة، قد يصبح مخزن التذبذب كبيرًا جدًا. وبالتالي سيحاول Asterisk تقليصه.
- Minexcessbuffer=<ms> - بمجرد أن ينخفض المخزن الزائد إلى هذه القيمة، يبدأ Asterisk بزيادة حجم المخزن.

### وسم الإطار (Frame tagging)

المعلمة أدناه تُعلِّم حزمة IP في حقل نوع الخدمة. يمكن للموجهات قراءة هذا الوسم، وبالتالي إعطاء أولوية للمرور. يستخدم Asterisk رموز DSCP لهذا الحقل (RFC 2474). القيم المسموح بها هي CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, و ef (أي التسليم المعجل).

```
tos=ef
```

### تشفير IAX2

يدعم IAX تشفير المكالمات باستخدام مفتاح متماثل، شيفرة كتلية 128‑بت تسمى AES (Advanced Encryption Standard). من السهل جداً تفعيل التشفير بين خطوط IAX. في ملف iax.conf استخدم:

```
encryption=yes
```

لإجبار التشفير:

```
forceencryption=yes
```

لضمان التوافق مع الإصدارات القديمة، قد تحتاج إلى تعطيل تدوير المفاتيح باستخدام:

```
keyrotate=no
```

### أوامر تصحيح IAX2

فيما يلي بعض أهم أوامر وحدة التحكم لتصحيح المشكلات في Asterisk.

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Looking at this output, identify the beginning and end of the call. Observe the delay and jitter information obtained using poke and pong packets. These packets help create the output of the “iax2 show netstats” command.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

لإيقاف التصحيح، استخدم:

```
vtsvoffice*CLI>iax2 no debug
```

### الملخص

هذا الفصل استعرض نقاط القوة والضعف في بروتوكول IAX. وقد أظهر كيف يعمل IAX في عدة سيناريوهات، مثل softphones و trunk بين خادمين Asterisk. وضع trunk يسمح لك بتوفير النطاق الترددي عن طريق حمل أكثر من مكالمة في حزمة واحدة. أخيرًا، تعلمت أوامر وحدة التحكم التي يمكنك استخدامها للتحقق من الحالة وتصحيح البروتوكول.

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** Everything in this section uses the old `chan_sip`
> driver and its `sip.conf` configuration file. `chan_sip` was deprecated for
> several releases and **removed in Asterisk 21**, so it **does not exist in
> Asterisk 22**. None of the `sip.conf` examples below will run on a current
> system — they are kept here only to document how legacy deployments worked and
> to help you migrate them. For the modern, supported way to do any of this, see
> the *PJSIP: the SIP channel* section of the *SIP & PJSIP in depth* chapter. The
> SIP *protocol* theory (methods, registration, proxy/redirect, SDP, NAT types)
> is protocol-level and lives in that chapter; what follows is purely the removed
> `chan_sip` **configuration**.

On legacy systems through Asterisk 20, SIP was configured in `/etc/asterisk/sip.conf`, which used to be the second most changed file (just after `extensions.conf`). The sections below show how `chan_sip` connected Asterisk to a SIP provider, how to connect two Asterisks together using SIP, domain support, presence, codec/DTMF/QoS options, authentication, and NAT — followed by a guide to migrating all of it to PJSIP.

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk is often used to connect to a SIP VoIP provider. VoIP providers usually have better rates for phone calls than traditional providers. Another interesting and attractive point of VoIP providers is the possibility to buy DID numbers in other cities—even in foreign countries. These are good reasons to use VoIP for telecommunications. In this section, you will learn how legacy `chan_sip` connected Asterisk to a VoIP provider. Three steps are required to connect Asterisk to a SIP provider. Tests can be conducted by establishing an account with your favorite provider. Step 1: Registering with a SIP provider in sip.conf To connect to a SIP provider, you will need the following information from the provider:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (Use secret to authenticate inbound requests and remotesecret for outbound requests)
- hostname
- domain
- codecs allowed

This configuration will allow your provider to locate Asterisk’s IP address. In the following statement, we are telling Asterisk to register to a SIP provider defined by the hostname and inform the provider of Asterisk’s IP address. The statement says that you want to receive calls at extension 4100. In the [general] section of the sip.conf file, enter the following line:

```
register=>name:secret@hostname/4100
```

الخطوة 2: Configure the [peer] on sip.conf Create an entry of peer type to the desired provider to simplify Asterisk’s dialing.

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

الخطوة 3: إنشاء مسار إلى المزود في مخطط الاتصال  
سنختار الأرقام 010 كمسار الوجهة إلى المزود. للاتصال بـ #610000 داخل المزود، ما عليك سوى طلب 010610000.

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### خيارات SIP المحددة لسيناريو المزود

تناقش الفقرة التالية تفاصيل الخيارات المحددة في ملف sip.conf للاتصال بمزود VoIP.

```
register=>username:password@hostname/4100
```

التعليمـة المسجَّلة في ملف **sip.conf** تُستَخدم للتسجيل لدى موفر الخدمة. يتم توثيق معاملة التسجيل باستخدام الاسم والسر. يمكنك استخدام شرطة مائلة (“/”) لتحديد امتداد للمكالمات الواردة. من الناحية التقنية، سيُوضع الامتداد في حقل رأس **Contact** لطلب **SIP**. يمكن التحكم في سلوك التسجيل عبر بعض المعلمات:

```
registertimeout=20
registerattempts=10
```

للتحقق مما إذا كان التسجيل ناجحًا، كان أمر وحدة التحكم القديمة هو `sip show registry`. في Asterisk 22 الأمر المكافئ هو `pjsip show registrations` (التسجيلات الصادرة) و`pjsip show endpoints` لحالة النقطة الطرفية.

المعامل “username” يُستخدم في ملخص المصادقة. يتم حساب الملخص باستخدام اسم المستخدم، السر، والنطاق:

```
username=username
```

المضيف يحدد عنوان موفر VoIP أو اسمه:

```
host=hostname
```

المعلمات Fromuser و Fromdomain تُطلب أحيانًا للمصادقة. تُستخدم هذه المعلمات في حقل رأس SIP From:

```
fromuser=username
fromdomain=hostname
```

عند الاتصال بمزود VoIP، تُطلب بيانات الاعتماد. بعد الدعوة الأولية، يرسل لك المزود رسالة تُسمى “407 Proxy Authentication Required”؛ تقوم بتوفير بيانات الاعتماد في رسالة INVITE اللاحقة. بالنسبة للمكالمات الواردة، سيطلب خادم Asterisk الخاص بك بيانات الاعتماد للمزود. من الواضح أن المزود لا يمتلك بيانات اعتماد صالحة لخادم Asterisk الخاص بك. عندما تستخدم insecure=invite، فأنت تخبر Asterisk بعدم إرسال “407 Proxy Authentication Required” إلى المزود وللقبول بالمكالمات الواردة. يمكنك أيضًا استخدام insecure=port, invite لمطابقة الطرف بناءً على عنوان IP دون مطابقة رقم المنفذ.

```
insecure=invite, port
```

### ربط خادمين Asterisk معًا باستخدام SIP (sip.conf)

يمكنك استخدام SIP لربط صندوقي Asterisk معًا. من المهم إيلاء الاهتمام بخطة الاتصال قبل المتابعة في هذا الإعداد. عادةً ما يرغب المستخدمون في ربط أنظمة PBX أخرى بأقل جهد ممكن. الفكرة هنا هي استخدام رقم امتداد فقط للاتصال بـ PBX الآخر. الخطوة 1: حرّر ملف sip.conf في الخادم A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

الخطوة 2: حرّر ملف sip.conf في الخادم B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![ربط خادمين Asterisk باستخدام SIP: الخادم A (الامتدادات 4400/4401) والخادم B (الامتدادات 4500/4501) يتبادلان إشارات SIP بحيث يمكن للمستخدمين على كل PBX الاتصال بالآخر](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

الخطوة 3: تحرير ملف extensions.conf في الخادم A:

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

الخطوة 4: حرّر ملف extensions.conf في الخادم B:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### دعم نطاق Asterisk (sip.conf)

يتبع بروتوكول SIP بنية الإنترنت. أول شيء يجب القيام به قبل تكوين SIP هو ضبط خوادم DNS بشكل صحيح. في بيئة SIP، يمكنك الاتصال بمستخدم موجود في أي وكيل SIP، ويمكن للمستخدمين الآخرين الاتصال بك أيضًا باستخدام معرف المورد الموحد (URI) الخاص بـ SIP. لضبط خادم DNS لـ SIP، عليك إضافة سجلات SRV إلى خادم DNS الخاص بك.

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

بعد تكوين DNS، يمكنك استخدام الـ URI الذي يشير إلى مستخدم SIP أو هاتف SIP أو امتداد هاتف. يشبه URI الـ SIP عنوان البريد الإلكتروني (مثال: sip:chuck@yourpartnerdomain.com). باستخدام عناوين SIP URI، لا يلزم رقم هاتف لإجراء مكالمة من هاتف SIP إلى آخر. للاتصال بمستخدم خارجي، ما عليك سوى استخدام بيان كما هو موضح أدناه.

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

Certain parameters can control domain behavior.

```
srvlookup=yes
```

هذا المعامل يتيح عمليات البحث DNS SRV في المكالمات الصادرة. باستخدام هذا المعامل، يمكن إجراء مكالمات باستخدام أسماء SIP المستندة إلى النطاق.

```
allowguest=yes
```

هذا المعامل يسمح بمعالجة دعوة خارجية دون مصادقة. يقوم بمعالجة المكالمة ضمن السياق المحدد في القسم العام أو في بيان النطاق. تحذير: إذا عرّفت سياقًا في القسم العام مع إمكانية الوصول إلى PSTN، يمكن لمستخدم خارجي طلب الاتصال بـ PSTN عبر نظام PBX الخاص بك. في هذه الحالة، ستتحمل أي رسوم. اسمح فقط بامتداداتك الخاصة في السياق المحدد في القسم العام.

![Connecting to other SIP servers by domain: youdomain.com and yourpartnerdomain.com exchange SIP signaling, so users such as lee and bruce can call chuck and norris using SIP URIs](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

يتيح لك أمر domain التعامل مع أكثر من نطاق داخل Asterisk. إذا جاء اتصال من نطاق محدد، يتم توجيهه إلى سياق محدد.

```
;autodomain=yes
```

يتضمن هذا المعامل عنوان IP المحلي واسم المضيف في المجالات المسموح بها.

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: الآن قم بتكوين برنامج الهاتف الناعم لاستخدام الوجود. سنوضح لك كيفية تكوين SipPulse Softphone.

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Change the presence model from peer-to-peer to presence agent, which will make the softphone subscribe Asterisk for SIP events.

Step 3: أضف جهة الاتصال إلى برامج الهاتف الناعم الأخرى. في هذا المثال، SipPulse Softphone هو الحساب 2000، لذا سنضيف جهة اتصال للحساب 2001. Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Fill the name 2001. Display as 2001 and don’t forget to check the box Show this contact’s availability.

Step 4: الآن اتصل بالامتداد 2001 وتحقق من حالة الهاتف في اللوحة اليمنى لبرنامج الهاتف الناعم. استخدم أمر وحدة التحكم `core show hints` لرؤية تغير حالة الوجود في الخادم (في chan_sip القديم، `sip show inuse` أظهر عدد المكالمات التي كانت لديك على كل خط). على Asterisk 22، استخدم `pjsip show endpoints` لتفقد حالة النقطة الطرفية والقناة. تظهر حالة الوجود/BLF في جهات اتصال برنامج الهاتف الناعم أو لوحة BLF — الطريقة التي تُعرض بها تعتمد على العميل.

#### Codec configuration

Codec configuration is simple and straightforward. You can set the words allow and disallow in the [general] section or peer/user section. The best practice is to standardize the codec to avoid transcoding, which is processor intensive. Please use the same codec for messages and prompts.

```
[general]
disallow=all
allow=g729
```

#### خيارات DTMF

في بعض الحالات، ستمرّر أرقامًا إلى تطبيق مثل البريد الصوتي أو الاستجابة الصوتية التفاعلية (IVR). من المهم تمرير DTMF بشكل صحيح. أبسط طريقة لتمرير DTMF تُسمّى inband. يتم ضبطها في القسم [general] أو قسم peer/user من ملف sip.conf. عندما تضبط dtmfmode=inband، تُولد نغمات DTMF كأصوات في قناة الصوت. المشكلة الرئيسية مع هذه الطريقة هي أنه عندما تقوم بضغط قناة الصوت باستخدام برنامج ترميز مثل g729، تتشوه الأصوات ولا يتم التعرف على نغمات DTMF بشكل صحيح. إذا كنت تخطط لاستخدام dtmfmode=inband، استخدم برنامج الترميز g.711 (ulaw و alaw).

```
dtmfmode=inband
```

نهج آخر هو استخدام RFC2833، والذي يسمح بتمرير نغمات DTMF كأحداث مسماة في حزم RTP.

```
dtmfmode=rfc2833
```

Finally, you can pass DTMF digits inside SIP packets, instead of RTP packets. This method is defined in the RFC3265 (signaling events) and RFC2976.

```
dtmfmode=info
```

بعد إصدار النسخة 1.2، أصبح الآن من الممكن استخدام:

```
dtmfmode=auto
```

هذا يحاول استخدام RFC2833؛ إذا لم يكن ذلك ممكنًا، استخدم نغمات النطاق.

#### تكوين وضع علامة جودة الخدمة (QoS)

QoS هي مجموعة من التقنيات المسؤولة عن جودة الصوت. يتم تنفيذ QoS بطريقة تقلل من عرض النطاق الترددي، والكمون، والارتداد. الوظائف الرئيسية لـ QoS هي جدولة الحزم، والتجزئة، وضغط رؤوس الحزم. يتم تنفيذ QoS في المفاتيح والموجهات، وليس بواسطة Asterisk نفسه. ومع ذلك، يمكن لـ Asterisk مساعدة الموجهات والمفاتيح عن طريق وضع علامة على الحزم لتسليمها بسرعة. يتم وضع العلامة باستخدام نقاط رمز الخدمة المتميزة (DSCP) المعرفة في RFCs 2474 و RFC2475.

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Starting from version 1.4, you can specify different codes for signaling (SIP), audio (RTP), and video (RTP).

### SIP authentication (sip.conf)

When legacy `chan_sip` received a SIP call, it followed the rules described in the following diagram. Three parameters played an important role in SIP authentication. On Asterisk 22, authentication is configured instead with PJSIP `auth` objects (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenced by an endpoint, and IP access control is done with `permit=`/`deny=` on the endpoint or via an `acl`.

![تدفق قرار المصادقة لــ chan_sip القديم: يتحقق Asterisk من رأس From مقابل sip.conf، يجرب قسم type=user/peer المطابق وبيانات الاعتماد MD5، ثم يعود إلى insecure=invite أو allowguest قبل السماح أو رفض المكالمة](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

هذا المعامل يتحكم فيما إذا كان بإمكان مستخدم لا يمتلك نظيرًا مطابقًا المصادقة دون اسم وسر. ناقشنا هذا المعامل في قسم دعم النطاق.

```
insecure=invite,port
```

عند استخدام insecure=invite، لا يقوم Asterisk بإنشاء الرسالة “407 Proxy Authentication Required”. بدون هذه الرسالة، يمكن للمستخدم إجراء مكالمة دون مصادقة. يُستخدم هذا غالبًا للاتصال بمزودي خدمة VoIP. عادةً ما تكون المكالمات الواردة من مزود خدمة VoIP غير مصادقة.

```
autocreatepeer=yes/no
```

هذا الأمر يُستخدم عندما يكون Asterisk متصلاً بــ SIP proxy. يقوم بإنشاء نظير (peer) ديناميكياً لكل مكالمة. عند تفعيل هذا الخيار، يمكن لأي UAC الاتصال بخادم Asterisk. من المهم تقييد اتصال الـ IP إلى الـ SIP proxy. يتولى الـ SIP proxy بدوره التحكم في الوصول. تُبنى إعدادات النظير على الخيارات العامة وكذلك حقل رأس “Contact” في حزمة SIP. تحذير: استخدم هذا بحذر شديد لأنه يفتح Asterisk بالكامل.

```
secret=secret, remotesecret=secret
```

هذا المعامل يضبط السر للمصادقة؛ استخدم **secret** للطلبات الواردة و **remotesecret** للطلبات الصادرة. إذا كنت لا تريد عرض الأسرار في ملفات النص، يمكنك استخدام **md5secret** لتضمين تجزئة بدلاً من السر. لإنشاء سر MD5، يمكنك استخدام:

```
echo -n "username:realm:secret" |md5sum
```

ثم استخدم العبارة التالية:

```
md5secret=0b0e5d467890....
```

تحذير: لا تنسَ استخدام المعامل –n؛ سيتم استخدام عودة السطر في حساب md5.

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

العبارات أعلاه ستحرم جميع عناوين IP وتسمح لـ UAC فقط من الشبكة المحلية (192.168.1.0/24).

#### خيارات RTP

يمكن التحكم في بعض معلمات RTP.

```
rtptimeout=60
```

هذا ينهي المكالمات التي لا يوجد فيها نشاط RTP لأكثر من 60 ثانية عندما لا تكون في وضع الانتظار.

```
rtpholdtimeout=120
```

This terminates calls without RTP activity even on hold (should be bigger than rtptimeout).

### عبور NAT في SIP (sip.conf)

النظرية الخاصة بـ NAT (أنواع NAT الأربعة، مشكلة رأس Contact، رسائل keep-alive، وإجبار الوسائط على المرور عبر الخادم) هي على مستوى البروتوكول وتم تغطيتها في فصل *SIP & PJSIP in depth*. المعلمات `sip.conf` المعروضة هنا (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) هي **legacy chan_sip** وقد أزيلت في Asterisk 21+. في PJSIP هذه تُطابق إعدادات النقل/النقطة الطرفية مثل `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, و`local_net=` على النقل، بالإضافة إلى `qualify_frequency=` على الـ AOR.

في legacy chan_sip، كان للمعامل `nat` خمسة خيارات:

- nat = no — لا تقم بأي معالجة خاصة لـ NAT بخلاف RFC3581
- nat = force_rport — تظاهر بوجود معامل rport حتى وإن لم يكن موجودًا
- nat = comedia — أرسل الوسائط إلى المنفذ الذي استقبل منه Asterisk المكالمة بغض النظر عما يحدده SDP.
- nat = auto_force_rport — اضبط خيار force_rport إذا اكتشف Asterisk وجود NAT (الإعداد الافتراضي)
- nat = auto_comedia — اضبط خيار comedia إذا اكتشف Asterisk وجود NAT

عند وضع العبارة “nat=force_rport” في ملف sip.conf، فأنت تخبر Asterisk بتجاهل العنوان الموجود في حقل رأس “Contact” في رأس SIP واستخدام عنوان IP المصدر والمنفذ في رأس حزمة IP، وكذلك بإرسال الوسائط مرة أخرى إلى العنوان الذي استُلمت منه متجاهلًا محتوى رأس SDP.

```
nat=force_rport,comedia
```

It is necessary to keep the NAT mapping open. If NAT times out, Asterisk cannot send an invite to the UAC. The UAC is able to send calls, but not receive any. The following statement can be used to keep NAT open.

```
qualify=yes
```

Qualify سيُرسل حزمة SIP باستخدام طريقة OPTIONS بانتظام، مما سيساعد على إبقاء NAT مفتوحًا. Qualify يرسل OPTIONS كل 60 ثانية وكل ثانية عشرية عندما لا يكون المضيف قابلًا للوصول. يمكنك استخدام “sip show peers” لرؤية زمن الانتقال للـ peers. إذا كان NAT الخاص بالمستخدم من النوع المتماثل، فإنه لا يمكن إرسال الحزم من UAC إلى آخر مباشرة؛ في هذه الحالة عليك إجبار RTP على المرور عبر Asterisk باستخدام:

```
directmedia=no
```

#### Asterisk خلف NAT (sip.conf)

كل السيناريوهات السابقة تفترض أن خادم Asterisk يمتلك عنوان إنترنت خارجي (صحيح). أحيانًا يتم تنفيذ خادم Asterisk خلف جدار ناري مع NAT. في هذه الحالة، من الضروري إجراء بعض التكوينات الإضافية.

![Asterisk خلف NAT: جدار ناري يطابق العنوان العام 200.180.4.168 مع خادم Asterisk الداخلي (192.168.1.100)، مع توجيه SIP على UDP 5060 ونطاق RTP UDP 10000–20000 المحدد في rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. قم بتكوين الجدار الناري لإعادة توجيه منفذ UDP 5060 بشكل ثابت إلى خادم Asterisk.
2. قم بتكوين الجدار الناري لإعادة توجيه منافذ UDP من 10000 إلى 20000 بشكل ثابت.

إذا أردت تقييد عدد المنافذ المفتوحة، يمكنك تعديل ملف `rtp.conf` لتغيير نطاق منافذ RTP. طريقة أخرى هي استخدام جدار ناري ذكي يدعم بروتوكول SIP لفتح منافذ RTP بشكل ديناميكي.

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

الخطوة 3: قم بتكوين Asterisk لتضمين العنوان الخارجي في حقول رؤوس حزم SIP بما في ذلك بروتوكول وصف الجلسة (SDP). يمكنك تحقيق ذلك بإضافة البيانين التاليين إلى ملف sip.conf:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

المعامل الأول `externaddr` يُخبر Asterisk بضم عنوان الـ IP الخارجي داخل رؤوس SIP للوجهات الخارجية. المعامل الثاني `localnet` يسمح لـ Asterisk بتمييز العناوين الخارجية عن الداخلية. بشكل اختياري، يمكنك استخدام `externhost` إذا كنت تستعمل DNS ديناميكي مع عنوان DHCP على الخادم.

### SIP dial strings (chan_sip)

تقنية سلسلة الاتصال `SIP/...` المعروضة أدناه هي برنامج تشغيل `chan_sip` المُزال. في Asterisk 22 استخدم تقنية `PJSIP/...` بدلاً منها — على سبيل المثال `Dial(PJSIP/2000)` أو `Dial(PJSIP/${EXTEN}@provider)`. الصيغ والمعاني متشابهة بخلاف ذلك.

يمكنك استدعاء وجهة SIP قديمة باستخدام سلاسل اتصال مختلفة:

```
SIP/peer
```

- ; يجب أن يكون هناك نظير معرف في sip.conf

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

تشمل الأمثلة:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## ترحيل نظام chan_sip القديم إلى PJSIP

نظرًا لأن `chan_sip` تم إزالته في Asterisk 21 ولم يعد موجودًا في Asterisk 22، يجب ترحيل أي نشر `sip.conf` إلى PJSIP. أكبر تحول مفاهيمي هو أن **نقطة النهاية** `sip.conf` `[peer]` أو `[friend]` تُقسم إلى عدة كائنات PJSIP، كل منها يحتوي على `type=`: **endpoint** (إعدادات المكالمة/الترميز/الوسائط)، كائن أو أكثر من **aor** (حيث يمكن الوصول إلى الجهاز / التسجيل)، كائن **auth** (بيانات الاعتماد)، و**transport** مشترك (مقبس الاستماع، عناوين NAT). الجدول التالي يطابق أكثر المفاهيم شيوعًا.

| مفهوم sip.conf القديم | ما يعادله في PJSIP (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` (مُشار إليه عبر `auth=` و`aors=`) |
| `type=friend` / `type=peer` / `type=user` | **a single** `type=endpoint` (PJSIP لا يميز بين friend/peer/user) |
| `host=dynamic` (الجهاز يسجل) | `type=aor` مع `max_contacts=1`؛ الجهاز يُرسل REGISTER لتحديث جهته |
| `host=<ip/hostname>` (ثابت) | `type=aor` مع `contact=sip:host:port` ثابت |
| `register=>user:secret@host/ext` (صادر) | `type=registration` (`server_uri=`، `client_uri=`، `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`، `auth_type=userpass`، `username=`، `password=` |
| `context=` | `context=` على الـ endpoint |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` على الـ endpoint (نفس الصياغة) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — أيضًا `inband`، `info`، `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` على الـ endpoint |
| `nat=force_rport,comedia` | `force_rport=yes`، `rewrite_contact=yes`، `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (ثوانٍ) على **aor** |
| `externaddr=` | `external_media_address=` و`external_signaling_address=` على **transport** |
| `localnet=` | `local_net=` على **transport** |
| `insecure=invite` (مزود، بدون مصادقة) | احذف `auth=`/`outbound_auth=` واستخدم `identify` (`type=identify`، `match=`) |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (استخدم بحذر) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (و`cos_audio` / `cos_video`) على الـ endpoint |

امتداد مسجل كان يبدو هكذا في `sip.conf` القديم:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

يصبح ما يلي في `pjsip.conf` على Asterisk 22:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### The sip_to_pjsip.py conversion script

Asterisk ships a helper script, **`sip_to_pjsip.py`**, that reads an existing
`sip.conf` and produces a `pjsip.conf`. You can run it directly in the
/etc/asterisk directory. The utility is in the Asterisk source tree under
`contrib/scripts/sip_to_pjsip/`, where `${PATH_TO_ASTERISK_SOURCE}` is the path
where the Asterisk source files are found (usually /usr/src/asterisk-22.x.y/):

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

إذا شَغَّلْتَهُ باستخدام الخيار `--help` سَتَرَى خِيَارَاتِهِ:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

It also accepts optional positional arguments — `[input-file [output-file]]`,
defaulting to `sip.conf` and `pjsip.conf` in the current directory.

Treat its output as a **starting point**: review every generated object,
especially transports, NAT settings, and codec lists, and test thoroughly before
going to production.

Let’s migrate the sip.conf in our companion labs at VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

بينما يبدو التحويل جيدًا، يمكننا أن نرى أن بعض العناصر مثل qualify=yes لا يمكن تعيينها مباشرة. لإصلاح ذلك، عليك إضافة الأمر qualify_frequency=time بالثواني إلى قسم aor. المثال أدناه.

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

تم تغطية تكوين PJSIP الكامل في الفصل *SIP & PJSIP in depth*، وتوفر الوثائق الرسمية على docs.asterisk.org تغطية كاملة للقناة. في مختبراتنا المصاحبة على voip.school، يتيح لك المختبر 5 ممارسة ما تعلمته للتو.

## Summary

This chapter gathered the channel technologies that predate today's pure-VoIP deployments but that Asterisk 22 still supports. You saw how **analog** lines and phones attach through **FXO/FXS** interfaces on DAHDI, how **digital TDM** links (E1/T1 and ISDN PRI/BRI) are provisioned, and how **IAX2** (`chan_iax2`) still serves as an efficient, NAT-friendly server-to-server trunk even though it is now firmly legacy. You also revisited the retired **`chan_sip`** driver and its `sip.conf` syntax — which you will meet in older systems but which no longer exists in Asterisk 22 — and worked through migrating such a system to PJSIP with the concept-mapping table and the `sip_to_pjsip.py` script. The rule of thumb: reach for anything in this chapter only when real hardware or an existing legacy system forces your hand; everything green-field is PJSIP over IP.

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
