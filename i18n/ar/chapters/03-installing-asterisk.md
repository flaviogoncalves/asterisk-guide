# Installing Asterisk 22

في الفصل الأول، تعلمنا قليلاً عن كيفية استفادة Asterisk في بيئة الاتصالات. في هذا الفصل، سنغطي كيفية تنزيل وتثبيت Asterisk. قبل البدء، من الضروري معرفة كيفية تجميعه وتثبيته. قد يبدو عملية التجميع غريبة لمستخدمي Microsoft™ Windows™ التقليديين، لكنها شائعة إلى حد كبير في بيئة Linux™. يمكن الحصول على كود مُحسّن لأجهزتك عند تجميع Asterisk، وهذا ما سنقوم به هنا. يعمل Asterisk على عدة أنظمة تشغيل، لكننا سنبسط الأمور ونستخدم نظامًا واحدًا فقط: Linux. نستخدم **Ubuntu 24.04 LTS** لأن تبعياته سهلة التثبيت وهو توزيعة خادم مستقرة ومدعومة جيدًا وبصمة منخفضة. إذا كنت تفضل توزيعة أخرى، عدّل أسماء الحزم وفقًا لذلك.

هذه النسخة تستهدف **Asterisk 22 LTS** (صُدرت في 2024-10-16؛ دعم كامل حتى 2028-10-16، تصحيحات أمان حتى 2029-10-16). Asterisk 22 هو الإصدار الحالي ذو الدعم طويل الأمد. لاحظ أن Digium تم الاستحواذ عليها من قبل **Sangoma** في 2018، وأن Asterisk الآن برعاية Sangoma — الإشارات إلى "Digium" في هذا الفصل تشير إلى العلامة التجارية القديمة للأجهزة التاريخية.

## الأهداف

بنهاية هذا الفصل يجب أن تكون قادرًا على:

- تحديد متطلبات العتاد لـ Asterisk;
- تثبيت Linux مع الاعتمادات المطلوبة;
- تنزيل نسخة مستقرة عبر HTTPS;
- تجميع Asterisk؛ و
- تعلم كيفية بدء تشغيل Asterisk عند إقلاع النظام.

## Minimum Hardware Required

Asterisk لا يحتاج إلى الكثير من العتاد للتشغيل، إلا أن هناك بعض النصائح لاختيار أفضل عتاد لمتطلباتك. يجب أن تأخذ في الاعتبار العوامل الرئيسية التالية عند اختيار العتاد:

- إجمالي عدد المستخدمين المسجلين. حدد عدد عمليات التسجيل في الثانية التي تحتاج إلى دعمها
- إجمالي عدد المكالمات المتزامنة. حدد عدد المحادثات الشبكية التي تحتاج إلى معالجتها في محول الشبكة والجسر على خادم Asterisk
- أيّ **codecs** تحتاج إلى دعمها. **codecs** ذات التعقيد العالي ستتطلب الكثير من طاقة CPU/FPU في الخادم؛ على سبيل المثال، تم قياس iLBC من قبل منشئه (Global IP Sound) بحوالي 18 MIPS لكل قناة لإطارات 30 ms (وحوالي 15 MIPS لإطارات 20 ms) على معالج DSP من طراز TI C54x
- إلغاء الصدى. إلغاء الصدى قد يستهلك الكثير من CPU/FPU، وفي بعض الحالات يجب اختيار إلغاء صدى مادي باستخدام DSPs في بطاقة واجهة الهاتف
- التوافر. استخدم RAID1 أو 5 لزيادة التوافر. تذكر أن Asterisk هو تطبيق يعمل 24×7.

المكوّن الرئيسي لخادم Asterisk هو محول الشبكة. يُنصح باستخدام محول شبكة خادم جيد. CPU مهم عندما تحتاج إلى دعم **codecs** ذات تعقيد عالي مثل g.729 و iLBC وإلغاء الصدى. يمكنك اختيار تفريغ هذا العبء إلى DSPs مخصصة: توفر Sangoma (سابقًا Digium) بطاقة DSP تسمى TC400B قادرة على دعم 120 مكالمة g.729 متزامنة.

الممارسة المثلى هي اختيار حاسوب جديد من فئة الخوادم من مصنع معروف. لمعرفة عدد المكالمات المتزامنة أو عدد المستخدمين المسجلين التي يمكن لجهاز معين دعمها، يجب اختبار هذا العتاد بأداة اختبار ضغط مثل SIPP (http://sipp.sourceforge.net). بعض مصنعي العتاد مثل Xorcom (http://www.xorcom.com) ينشرون نتائجه على موقعهم.

ملاحظة: بعض تطبيقات Asterisk، مثل ConfBridge و music on hold، تحتاج إلى مصدر توقيت داخلي. في لينكس الحديث يتم توفير ذلك تلقائيًا بواسطة الوحدة المدمجة `res_timing_timerfd` — لا يلزم أي عتاد هاتف. (المؤقت البرمجي القديم `dahdi_dummy` لم يعد موجودًا؛ تم دمج وظيفته في الوحدة النواة الرئيسية `dahdi` في DAHDI Linux 2.3.0.) يمكنك التأكد من المؤقت النشط بأمر CLI `timing test`.

### Hardware configuration

عتاد Asterisk لا يحتاج إلى تعقيد. لا تحتاج إلى بطاقة فيديو باهظة الثمن أو عدد كبير من الملحقات. بعض النصائح حول تكوين العتاد:

- عطل منافذ USB، التسلسلية والمتوازية غير المستخدمة لتجنب استهلاك المقاطعات غير الضرورية.
- بطاقة واجهة شبكة قوية أمر أساسي.
- احرص بشكل خاص إذا كنت تستخدم بطاقات واجهة هاتف. بعض البطاقات تستخدم ناقل PCI بجهد 3.3 فولت، وليس من السهل العثور على اللوحات الأم لها. في هذه الأيام، PCI Express أكثر توفرًا.
- انتبه جيدًا إلى القرص الصلب، فـ PBX يعمل بنظام 24×7 بينما تعمل الحواسيب المكتبية 8×5. لا تستخدم عتاد الحواسيب المكتبية لـ PBX، عادةً ما يفشل القرص الصلب قبل السنة الأولى. توصية هي استخدام جهاز خادم أو جهاز مخصص لتشغيل تطبيقات 24×7.

### IRQ sharing (legacy PCI cards only)

هذا القلق ينطبق **فقط** إذا قمت بتركيب بطاقات هاتف مادية PCI/PCI-Express (عتاد DAHDI). هذه البطاقات تولد عددًا كبيرًا من المقاطعات، وعلى الأنظمة القديمة ذات المعالج الواحد، مشاركة خط IRQ مع جهاز آخر قد تحرم السائق وتؤثر سلبًا على جودة الصوت. إذا كنت تستخدم بطاقات هاتف، خصص الجهاز لـ Asterisk، عطل أي أجهزة مدمجة غير مستخدمة في BIOS، وتحقق من المقاطعات المعينة باستخدام `cat /proc/interrupts`. الخوادم الحديثة متعددة النوى التي تستخدم مقاطعات MSI/MSI‑X تجعل مشاركة IRQ غير مشكلة عمليًا، ولا تحتاج عملية نشر VoIP صافية (بدون بطاقات) إلى القلق بشأنها على الإطلاق.

## اختيار توزيعة لينكس

تم تطوير Asterisk في البداية للعمل على لينكس. ومع ذلك، يمكنه أيضًا العمل على BSD Unix أو macOS. إذا كنت جديدًا على Asterisk، جرب استخدام لينكس أولاً لأنه أسهل كثيرًا. تستهدف Asterisk رسميًا عائلة RHEL (CentOS/RHEL/Fedora)، Ubuntu، وDebian. الخيارات العملية الجيدة اليوم هي **Debian 12**، **Ubuntu 22.04 LTS / 24.04 LTS**، و**Rocky Linux 9 / AlmaLinux 9** — فإن CentOS Linux انتهت دورة حياته، لذا يُفضَّل اختيار Rocky أو AlmaLinux على أنظمة عائلة RHEL. لهذا الكتاب سأستخدم Ubuntu 24.04 LTS. حمّل أحدث صورة خادم لإصدار 24.04 من دليل الإصدارات الرسمي أدناه (اسم الملف الدقيق يتضمن الإصدار الفرعي الحالي، مثال `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### إعداد لينكس لـ Asterisk

قبل تجميع Asterisk تحتاج إلى نظام لينكس يعمل مع حزم البناء المثبتة. ثبّت **Ubuntu 24.04 LTS Server** في آلة افتراضية أو على جهاز مخصص (استخدم الصورة 64‑bit؛ كل ما في هذا الكتاب 64‑bit، رغم أن Asterisk نفسه لا يزال يدعم 32‑bit x86). استخدمنا VirtualBox لهذا التدريب؛ يمكنك تنزيل الصورة من <https://releases.ubuntu.com/24.04>. تثبيت لينكس نفسه خارج نطاق هذا الكتاب — المعرفة الأساسية بلينكس شرط مسبق. بعد تثبيت لينكس، ستضيف تبعيات بناء Asterisk (انظر *Installing dependencies* أدناه) ثم تقوم بتجميع Asterisk.

## تثبيت لينكس لـ Asterisk

قم بتثبيت لينكس كالمعتاد، بدون سطح مكتب رسومي. أثناء التثبيت، فعّل أيضًا عميل نقل البريد (نستخدم **exim4**) — سيحتاج Asterisk إليه لإرسال إشعارات البريد الصوتي إلى البريد الإلكتروني لاحقًا في هذا الكتاب. **تحذير:** تثبيت نظام تشغيل يمحو القرص الهدف. إذا قمت بالتثبيت على عتاد مادي، احفظ بياناتك أولاً؛ التثبيت داخل آلة افتراضية يترك المضيف غير متأثر. إقلاع المثبت من صورة Ubuntu Server ISO (أو محرك الأقراص الضوئي الافتراضي للآلة الافتراضية) وأجب على المطالبات — معظمها واضح.

## Installing dependencies

لتثبيت Asterisk و DAHDI عليك تثبيت العديد من تبعيات البرمجيات. الطريقة الموصى بها للقيام بذلك في Asterisk 22 هي استخدام السكريبت المرفق مع شجرة المصدر، والذي يعرف أسماء الحزم الصحيحة لكل توزيعة مدعومة. بعد تنزيل واستخراج مصدر Asterisk (انظر "Compiling Asterisk" أدناه)، نفّذ:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. سجّل الدخول كـ root (أو استخدم `sudo`).
2. إذا كنت تفضّل تثبيت التبعيات يدوياً على نظام Debian/Ubuntu، فقائمة الحزم المكافئة هي:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

لاحظ أن مصدر Asterisk مستضاف الآن على Git، لذا لم يعد `subversion` مطلوباً، وتُرسل إصدارات Debian/Ubuntu الحديثة `libncurses-dev` بدلاً من `libncurses5-dev` ذات الإصدارات المحددة. يُفضَّل استخدام `./contrib/scripts/install_prereq install` على قائمة يدوية الصيانة، لأن السكريبت يتتبع دائماً أسماء الحزم الصحيحة لتوزيعتك.

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) هو بنية التعريفات لبطاقات الأنالوج والرقمية. قبل تثبيت Asterisk من المهم تثبيت DAHDI إذا كنت تخطط لاستخدام واجهات أنالوج أو رقمية. لا يزال DAHDI موجوداً لبطاقات الهاتفية الأنالوج/الرقمية لكنه أصبح نادراً — معظم النشر الحديث يعتمد بالكامل على VoIP ويمكنه تخطي هذا القسم تماماً. ثبّت DAHDI فقط إذا كان لديك عتاد هاتفية مادي. احصل على ملفات المصدر باستخدام:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

افك ضغط الملفات باستخدام:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

ستحتاج إلى تجميع وحدات DAHDI. تم تقديم الأوامر ./configure و make menuselect قبل عدة سنوات. يتيح الأخير لك اختيار الأدوات والوحدات التي تريد بناؤها. الأوامر التالية ستقوم بذلك:

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config تم تكوين DAHDI. إذا كان لديك أي عتاد DAHDI يُنصح الآن بتحرير /etc/dahdi/modules لتحميل الدعم فقط للعتاد DAHDI المثبت في هذا النظام. بشكل افتراضي يتم تحميل الدعم لجميع عتاد DAHDI عند بدء DAHDI. أعتقد أن عتاد DAHDI الموجود في نظامك هو: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware هذه الشاشة (أعلاه) تطلب منك تغيير ملف /etc/dahdi/modules لتحميل فقط التعريفات المطلوبة لتكوينك المحدد وعرض العتاد المكتشف. حرّر ملف /etc/dahdi/modules وحمّل فقط العتاد المطلوب. في حالتي، كنت أستخدم جهاز اختبار به Xorcom Astribank 6FXS و 2FXO. الملف موضح أدناه.

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

أعد تشغيل حاسوبك وتحقق من التحميل الصحيح للتعريفات.

## أي نسخة يجب اختيارها

كقاعدة عامة، يجب عليك استخدام النسخة التي تحتوي على الميزات المطلوبة. يتبع Asterisk نموذج إصدار يتناوب بين إصدارات LTS (دعم طويل الأمد) والإصدارات القياسية. في وقت إصدار هذا الطبعة، **Asterisk 22 هو الإصدار LTS الحالي** (صدر في أكتوبر 2024؛ أحدث إصدار نقطي هو 22.10.0)، مما يجعله الخيار الأفضل الآن. Asterisk 20 هو LTS السابق، والنسخة 16 (المستخدمة في الطبعة الأولى) وصلت إلى نهاية عمرها. بالنسبة للأنظمة الإنتاجية، اختر دائمًا إصدار LTS.

## تجميع Asterisk

إذا كنت قد جمعت برامج من قبل، فإن تجميع Asterisk سيكون مهمة سهلة. نفّذ الأوامر التالية لتجميع وتثبيت Asterisk. تذكّر أنه يمكنك اختيار التطبيقات والوحدات التي تريد بناؤها باستخدام **make menuselect**.  

الخطوة 1: تنزيل شفرة المصدر  

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

الخطوة 2: تثبيت المتطلبات المسبقة للبناء (انظر “Installing dependencies” أعلاه)  

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

الخطوة 3: تكوين عملية البناء  

```
./configure
```

الخطوة 4: اختيار الوحدات التي تريد بناؤها  

```
make menuselect
```

استخدم **make menuselect** لتثبيت الوحدات الضرورية فقط. في Asterisk 22 قناة SIP هي **chan_pjsip** (مُبنية افتراضيًا)؛ تم إزالة **chan_sip** القديمة في Asterisk 21 ولم تعد موجودة. يعمل تمرير Opus *pass‑through* مباشرةً (الوحدة `res_format_attr_opus` المدمجة تتعامل مع تفاوض SDP)، لكن وحدة **codec_opus** للتحويل لا تزال وحدة خارجية، ذات شفرة مغلقة من Sangoma/Digium — اختيارها في menuselect يقوم بتحميلها من خوادم Digium. الوحدة مجانية. راجع “Selecting modules with menuselect” أدناه للمزيد من التفاصيل.

الخطوة 5: بناء وتثبيت Asterisk، ثم إنشاء الإعدادات الافتراضية والملفات النموذجية  

```
make
make install
make samples
make config
ldconfig
```

`make install` يثبت الثنائيات والوحدات، `make samples` يكتب ملفات الإعداد النموذجية في `/etc/asterisk`، `make config` يثبت سكريبت بدء تشغيل SysV init لتوزيعتك المكتشفة (مثلاً `/etc/init.d/asterisk` على Debian/Ubuntu)، و`ldconfig` يحدث ذاكرة التخزين المؤقت للمكتبات المشتركة. كما تُرفق وحدة systemd في شجرة المصدر في `contrib/systemd/asterisk.service`، لكن `make config` لا تثبتها تلقائيًا — انسخها إلى المكان المناسب إذا رغبت في تشغيل Asterisk تحت systemd (انظر أدناه).

### اختيار الوحدات باستخدام menuselect

`make menuselect` يفتح قائمة نصية حيث تختار بالضبط التطبيقات، الترميزات، القنوات، والموارد التي تريد بناؤها. بعض الملاحظات الخاصة بـ Asterisk 22:

- **chan_pjsip** (تحت *Channel Drivers*) هي قناة SIP الحديثة ومفعّلة افتراضيًا؛ وهي القناة الوحيدة لـ SIP في Asterisk 22.  
- **codec_opus** (تحت *Codec Translators*) هي وحدة **خارجية** (مدخل menuselect الخاص بها يقرأ “Download the Opus codec from Digium”)؛ تفعيلها يجعل `make` يجلب الثنائي المجاني ذو الشفرة المغلقة من Sangoma/Digium. تمرير Opus نفسه لا يحتاج إلى وحدة إضافية. وحدة **codec_g729** من Sangoma متاحة أيضًا — الثنائي مجاني للتحميل، لكن التحويل القانوني لـ G.729 يتطلب ترخيصًا مدفوعًا لكل قناة.  
- اختر صيغ الصوت واللغات التي تريدها في قوائم *Core Sound Packages* و*Music On Hold File Packages* و*Extras Sound Packages*؛ أي شيء تحدده هناك يتم تحميله وتثبيته تلقائيًا أثناء `make install`.

بعد إتمام اختياراتك، اختر **Save & Exit** واستمر مع `make`.

## بدء وإيقاف Asterisk

مع هذا التكوين البسيط، يمكن بدء Asterisk بنجاح. للتعلم وإزالة الأخطاء، يمكنك تشغيل Asterisk في الواجهة الأمامية المرتبطة بالكونسول:

```
/usr/sbin/asterisk -vvvgc
```

استخدم أمر CLI `core stop now` لإغلاق Asterisk:

```
*CLI> core stop now
```

### بدء Asterisk باستخدام systemd

في توزيعات لينكس الحديثة (Debian 12، Ubuntu 22.04/24.04، Rocky/AlmaLinux 9)، مدير خدمة النظام هو **systemd**. يأتي Asterisk بوحدة systemd في `contrib/systemd/asterisk.service` داخل شجرة المصدر؛ انسخها إلى `/etc/systemd/system/asterisk.service` وشغّل `systemctl daemon-reload`. بمجرد التثبيت، الطريقة الموصى بها لتشغيل Asterisk في بيئة الإنتاج هي عبر `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

بعد تشغيل Asterisk كخدمة، اتصل بواجهة الأوامر الخاصة به باستخدام `asterisk -r` (الاتصال) أو `asterisk -rvvv` (الاتصال مع إخراج مفصل).

في الأنظمة القديمة كان يتم بدء Asterisk عبر سكريبت التهيئة القديم SysV (`/etc/init.d/asterisk`) وملف التغليف **safe_asterisk**، الذي يعيد تشغيل Asterisk تلقائيًا إذا تعطل. مع systemd، يتم التعامل مع إعادة التشغيل التلقائي عبر توجيه `Restart=` في ملف الوحدة، لذا فإن `safe_asterisk` لم يعد ضروريًا عادة. لا يزال نهج init/`safe_asterisk` القديم يعمل لكنه مُهمل في التوزيعات القائمة على systemd.

### خيارات تشغيل Asterisk في وقت التنفيذ

عملية بدء Asterisk بسيطة جدًا. إذا تم تشغيل Asterisk دون أي معلمات، يتم إطلاقه كخدمة خلفية.

```
/sbin/asterisk
```

يمكنك الوصول إلى كونسول Asterisk بتنفيذ الأمر التالي. يرجى ملاحظة أنه يمكن تشغيل أكثر من عملية كونسول في نفس الوقت.

```
/sbin/asterisk -r
```

### الخيارات المتاحة لتشغيل Asterisk في وقت التنفيذ

يمكنك عرض الخيارات المتاحة في وقت التنفيذ باستخدام `asterisk -h`

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## دلائل التثبيت

Asterisk يتم تثبيته في عدة دلائل، ويمكن تعديلها في ملف asterisk.conf. لأغراض التدريب سأغير مستوى الإيضاح من 3 إلى 15، أما في الإنتاج فابقه عند 3. الخياران `maxcalls` و`maxload` خيارات جيدة لحماية نظامك من التحميل الزائد.

### asterisk.conf (مقتطف)

القسم `[directories]` يحدد أين يحتفظ Asterisk بإعداداته، وحداته، بياناته، مجلد الـ spool، والسجلات:

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
```

القسم `[options]` يحتوي على ضبط الأداء أثناء التشغيل. أكثر الخيارات فائدة هي الموضحة أدناه (أزل التعليق لتفعيلها)؛ الملف يأتي مع العديد من الخيارات الأخرى، كل منها موثّق بتعليق داخل السطر:

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## ملفات السجل وتدوير السجل

يقوم نظام Asterisk PBX بتسجيل رسائله في `/var/log/asterisk`. يتم التحكم في التسجيل عبر `logger.conf`. الجزء الأساسي هو قسم `[logfiles]`، حيث يحدد كل سطر قناة سجل ومستويات الرسائل التي تلتقطها (مقتطف):

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

بعد التحرير، طبّق التغيير باستخدام `logger reload` وتأكد من القنوات عبر `logger show channels`:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

يمكن أن تنمو ملفات السجل بسرعة، لذا قم بتدويرها باستخدام خدمة النظام `logrotate` — أضف ملفًا تحت `/etc/logrotate.d/`:

```text
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

يمكن الحصول على مزيد من المعلومات حول logrotate باستخدام:

```
#man logrotate
```

## إلغاء تثبيت Asterisk

To uninstall Asterisk, use:

```
make uninstall
```

To uninstall Asterisk and all configuration files, use:

```
make uninstall-all
```

## ملاحظات تثبيت Asterisk

سوف يقدم هذا القسم بعض النصائح حول القضايا التي يجب معالجتها قبل تثبيت Asterisk.

### أنظمة الإنتاج

إذا تم تثبيت Asterisk في بيئة إنتاج، يجب إيلاء الاهتمام لتصميم النظام. يجب تحسين الخادم بطريقة تجعل أنظمة الاتصالات لها أولوية على عمليات النظام الأخرى. لا ينبغي تشغيل Asterisk جنبًا إلى جنب مع برامج تستهلك المعالج بشكل كبير مثل X-Windows. إذا كنت بحاجة إلى تشغيل عمليات كثيفة الاستخدام للمعالج (مثل قاعدة بيانات ضخمة)، استخدم خادمًا منفصلًا. بشكل عام، Asterisk حساس لتقلبات أداء العتاد. لذلك، حاول استخدام Asterisk في بيئة عتادية لا تتطلب أكثر من 40٪ من استهلاك المعالج.

### نصائح الشبكة

إذا كنت تخطط لاستخدام هواتف IP، فمن المهم أن تولي اهتمامًا لشبكتك. بروتوكولات الصوت جيدة جدًا ومقاومة للكمون وحتى الارتجافات؛ ومع ذلك، إذا استخدمت شبكة محلية مُكوَّنة بشكل سيء، سيتأثر جودة الصوت. لا يمكن ضمان جودة صوت جيدة إلا باستخدام جودة الخدمة (QoS) في المفاتيح والموجهات. الصوت في الشبكة المحلية عادةً ما يكون جيدًا، ولكن حتى في بيئة LAN، إذا كان لديك محاور 10 Mbps مع الكثير من التصادمات، ستنتهي بك الأمر بصوت مشوّه أو رديء. اتبع هذه التوصيات لضمان أفضل جودة صوت ممكنة:

- استخدم QoS من الطرف إلى الطرف إذا كان ذلك ممكنًا أو اقتصاديًا قابلًا للتنفيذ. مع QoS من الطرف إلى الطرف، تكون جودة الصوت مثالية. لا أعذار!
- تجنب استخدام محاور 10/100 Mbps للصوت في بيئة إنتاج. يمكن أن تفرض التصادمات ارتجافات على الشبكة. يُفضَّل استخدام 10/100 Mbps مزدوجة كاملًا لأن لا تصادمات تحدث.
- استخدم VLANs لعزل البث غير الضروري لشبكة الصوت. لا تريد فيروسًا يدمر شبكة الصوت عبر بث ARP.
- علم المستخدمين بتوقعاتهم في شبكة الصوت. بدون QoS، لا تقول إن الصوت سيكون مثاليًا لأن معظم الحالات لن تكون كذلك. غالبًا ما يتم تحقيق جودة صوت مشابهة للهاتف المحمول. استخدم هواتف ذات جودة لأن مشاكل البرامج الثابتة وتصميم العتاد شائعة.

## ملخص

في هذا الفصل، تعلمت عن الحد الأدنى لمتطلبات العتاد وكذلك كيفية تنزيل وتثبيت وتجميع Asterisk. يجب تشغيل Asterisk باستخدام مستخدم غير جذري لأسباب أمنية. يجب عليك فحص بيئة الشبكة الخاصة بك قبل بدء بيئة الإنتاج.

## Quiz

1. في Asterisk 22، أي برنامج تشغيل قناة يوفر دعم SIP، وماذا حدث للـ `chan_sip` القديم؟
   - A. `chan_sip` لا يزال هو الافتراضي؛ `chan_pjsip` اختياري.
   - B. `chan_pjsip` هو قناة SIP الافتراضية؛ `chan_sip` أُزيل في Asterisk 21 ولم يعد موجودًا.
   - C. كلاهما مُبنيان افتراضيًا وتختار بينهما وقت التشغيل.
   - D. تم إزالة دعم SIP تمامًا لصالح IAX2.
2. بطاقات واجهة الهاتفية لـ Asterisk عادةً ما تحتوي على معالجات إشارة رقمية (DSPs) مدمجة وبالتالي لا تحتاج إلى الكثير من وحدة المعالجة المركزية من الحاسوب.
   - A. صحيح
   - B. خطأ
3. إذا كنت تريد جودة صوت مثالية، تحتاج إلى تنفيذ جودة خدمة من الطرف إلى الطرف (QoS).
   - A. صحيح
   - B. خطأ
4. يجب عليك دائمًا اختيار أحدث نسخة من Asterisk، لأنها الأكثر استقرارًا.
   - A. صحيح
   - B. خطأ
5. ما هي الطريقة الموصى بها لتثبيت تبعيات البناء لـ Asterisk 22؟
6. إذا لم يكن لديك بطاقة واجهة TDM، فستظل لديك مصدر توقيت داخلي للمزامنة، يقدمه وحدة `res_timing_timerfd` على لينكس. يُستخدم هذا التوقيت من قبل تطبيقات مثل ________ و ________.
7. عند تثبيت Asterisk من الأفضل ترك بيئات سطح المكتب مثل GNOME أو KDE خارجًا، لأن الواجهات الرسومية تستهلك دورات CPU.
   - A. صحيح
   - B. خطأ
8. ملفات تكوين Asterisk موجودة في الدليل ________.
9. لتثبيت ملفات تكوين Asterisk النموذجية، اكتب الأمر: ________
10. لماذا من المهم تشغيل Asterisk كمستخدم غير جذري؟

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
