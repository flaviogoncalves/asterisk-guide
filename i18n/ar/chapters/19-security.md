# أمان Asterisk

منذ البداية، كانت مسألة الأمان لـ Asterisk حرجة. SIP، بروتوكول بدء الجلسة هو البروتوكول الأكثر تعرضًا للهجمات على الإنترنت وفقًا لـ CERT.BR. أي شخص يدير honeypot يمكنه التأكيد على ذلك. مشكلة احتيال مشاركة إيرادات الإنترنت خطيرة جدًا ويمكن أن تؤدي إلى خسائر تتجاوز مئات الآلاف من الدولارات. لا ينبغي أبدًا تثبيت خادم Asterisk متصل بالإنترنت دون أمان مناسب. في هذا الفصل، ستتعلم كيفية تحديد الأنواع الرئيسية للهجمات التي قد تتلقاها وكيفية الوقاية منها باستخدام سياسة أمان مناسبة. أخيرًا وليس آخرًا، ستتعلم كيفية تنفيذ سياسة الأمان المقترحة.

هذا الفصل يستهدف **Asterisk 22 LTS**، حيث PJSIP (`res_pjsip` / `chan_pjsip`) هو قناة SIP الوحيدة. (تم إزالة برنامج تشغيل `chan_sip` القديم في Asterisk 21 — راجع فصل *Legacy Channels* إذا كنت تقوم بترحيل نظام أقدم.) نتيجة ذات صلة بالأمان: الآن يتم إصدار عمليات المصادقة الفاشلة عبر **إطار أحداث الأمان** في Asterisk وقناة سجل `security` المخصصة، مما يغيّر طريقة تكوين Fail2Ban (المغطى لاحقًا في هذا الفصل).

## الأهداف

بنهاية هذا الفصل يجب أن تكون قادرًا على:

- تحديد الأنواع الرئيسية للهجمات التي تُشن بشكل متكرر على خوادم Asterisk
- تعريف سياسة أمان فعّالة
- تنفيذ سياسة الأمان
- تثبيت وتكوين IPTABLES لـ Asterisk
- تثبيت وتكوين Fail2Ban لـ Asterisk
- تثبيت وتكوين TLS و SRTP للتشفير

## الهجمات الرئيسية على الاتصالات الصوتية عبر IP

يمكن تصنيف الهجمات الرئيسية على الاتصالات الصوتية عبر IP على أنها DOS/DDOS، سرقة الخدمة/احتيال الرسوم والتنصت. قد تكون بعض الأسماء مربكة ومصادر مختلفة أحيانًا لديها أسماء مختلفة لنفس الهجمة. سرقة الخدمة، احتيال الرسوم، احتيال مشاركة إيرادات الإنترنت، احتيال الهاتف هي أسماء مختلفة للقراصنة الذين يستخدمون PBX الخاص بك لضخ الحركة إلى رقم معدل مميز والحصول على عوائد من المزود.

### هجمات DDoS/DOS

إنكار الخدمة (Denial of Service) والهجمات الموزعة لإنكار الخدمة (Distributed Denial of Service) تُعدّ من الهجمات الشائعة على أي بنية تحتية لتقنية المعلومات. ولا يختلف الأمر مع بروتوكول SIP وبروتوكولات الصوت عبر الإنترنت الأخرى. عادةً ما تُنفّذ هجمات الإنكار الموزعة بواسطة شبكة بوتنت، بينما تُنفّذ هجمات الإنكار بواسطة جهاز كمبيوتر واحد فقط. في فبراير 2011، نفّذت شبكة بوتنت Sality مسحًا خفيًا ومنسقًا لكامل مساحة عناوين IPv4 بحثًا عن خوادم SIP معرضة للثغرات — وقد أشار باحثون يراقبون تلسكوب شبكة UCSD إلى أن ذلك تم بواسطة ما يقرب من ثلاثة ملايين عنوان IP مصدر مختلف يستهدفون المنفذ UDP 5060، على الأرجح لمحاولة اختراق حسابات SIP بغرض الاحتيال على المكالمات.[^sality]

[^sality]: A. Dainotti وآخرون، "Analysis of a '/0' Stealth Scan from a Botnet," *IEEE/ACM Transactions on Networking*، 2015 (DOI 10.1109/TNET.2013.2297678).

![شبكة بوتات نظير إلى نظير توجه آلاف محاولات تسجيل SIP إلى خادم](../images/19-security-fig01.png)

عادةً ما يتم تطبيق الـ DOS عبر تقنيات مثل الفuzzing والفيضانات. يمكن للفيضانات استخدام SIP، IAX، RTP وغيرها من البروتوكولات. يمكنها إيقاف الخدمة تمامًا أو تدهور جودة الصوت. من الصعب جدًا التخفيف منها إذا كانت المنافذ مفتوحة على الإنترنت. أدناه بعض الأدوات التي يستخدمها المهاجمون

**التخمين العشوائي:**

- **PROTOS Test Suite (c07-sip)** — من جامعة أولو OUSPG. يرسل آلاف الحزم المشوهة لاستثارة عطل مثل تجاوز سعة الذاكرة المؤقتة الذي يوقف البرنامج.  
- **Voiper** — يولد أكثر من 200,000 اختبار يغطي جميع سمات SIP ويتحقق مما إذا كان الخادم الخاص بك يستطيع معالجة الرسائل بفعالية. <http://voiper.sourceforge.net/>

**الفيض:**

- **INVITE Flooder** — يملأ الخادم بطلبات SIP INVITE. <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — يملأ الخادم بحركة مرور IAX2. <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — يملأ جلسات الوسائط النشطة بحزم RTP لتقليل جودة الصوت. <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### تقنيات التخفيف من هجمات DoS/DDoS

توصياتي هي

1. لا تكشف خادم Asterisk الخاص بك على الإنترنت، إلا إذا كان ذلك ضروريًا مع حماية مناسبة (SBC)  
2. في الشبكة الداخلية استخدم شبكة محلية افتراضية (VLAN) للصوت، خاصة إذا كنت في جامعة أو كلية حيث عدد المستخدمين كبير.  
3. استخدم VPN أو TLS للوصول الخارجي.

### احتيال مشاركة الإيرادات عبر الإنترنت

هذا الاحتيال صعب الفهم إلى حد ما. المفتاح هو فهم مفهوم رقم السعر المميز الدولي (IPRN).

![الخطوات الثلاث للاحتيال على مشاركة إيرادات الإنترنت: شراء رقم بمعدل مرتفع، العثور على جهاز VoIP ضعيف واستدعاء الرقم، ثم جمع العائد】(../images/19-security-fig02.png)

An IPRN هو رقم يمكنك تخصيصه مجانًا في بعض شركات الهاتف عبر الإنترنت المحددة. ابحث عن مزودي أرقام الإنترنت ذات السعر المميز Premium Rate Number Providers وستجد مجموعة منهم. في هذا النوع من المشغل يمكنك تخصيص، على سبيل المثال، رقم في شبكة أقمار صناعية مثل Iridium، وهو وجهة تكلف عشرات الدولارات لكل دقيقة على المتصل. سيُعيد لك مزود IPRN نسبة من العائد (10 إلى 20٪ من الدخل) عن كل دقيقة يتم استلامها.

![قائمة أسعار مزود IPRN تُظهر معدلات الدفع حسب الدولة وأرقام الاختبار](../images/19-security-fig03.png)

بعد مرحلة التخصيص، يحاول الهاكر العثور على أي خادم Asterisk مفتوح قادر على طلب رقم IPRN المخصص. سيقوم نظام PBX الخاص بالضحية، الذي يتحكم فيه الهاكر، بإجراء مئات المكالمات إلى رقم IPRN مما يولد عائدًا كبيرًا للهاكر وفاتورة هاتف ضخمة للضحية. كثيرًا ما يتجاوز ذلك مئات الآلاف من الدولارات في عطلة نهاية أسبوع واحدة.

الأدوات الرئيسية التي يستخدمها القراصنة لمهاجمة نظام PBX:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious هي مجموعة أدوات أمان سهلة الاستخدام. هدفها الرئيسي هو التعرف على أنظمة PBX الضعيفة واختراق كلمات مرور SIP باستخدام هجوم القوة الغاشمة. الأداة الأكثر استخدامًا هي svcrack. الأداة قادرة على اختبار آلاف كلمات المرور في الثانية.  
2. **Phone vulnerabilities**. نقطة أخرى يستخدمها القراصنة كثيرًا كمتجه هجوم هي الهاتف نفسه. كثير من الأشخاص الذين يثبتون Asterisk لا يغيرون كلمة المرور الافتراضية في واجهة الويب للهاتف. بمجرد أن تكون هذه الهواتف مفتوحة على الإنترنت، يمكن للقراصنة محاولة استخدام كلمة مرور الواجهة الافتراضية لتنزيل التكوين حيث يمكنهم غالبًا العثور على كلمة مرور SIP السرية.

#### سرقة TFTP:

If you are using auto provisioning of phones using TFTP, you are probably open to this type of attack. TFTP is a simple and insecure form of a File Transfer Protocol.

![مهاجم يقوم بتنزيل ملفات .cfg يمكن تخمينها من خادم TFTP، يجمع بيانات الاعتماد النصية الصريحة من ملفات التكوين】(../images/19-security-fig04.png)

اسم ملفات التكوين يمكن تخمينه بسهولة باستخدام عنوان mac متبوعًا بـ .cfg (مثال: 001A2B3C4D5E.cfg). يمكن للقراصنة الأذكياء إنشاء أداة بسهولة لتجربة جميع عناوين MAC بشكل متسلسل أو ببساطة تنزيل أداة للقيام بذلك. عادةً ما تكون ملف التكوين غير مشفر وتحتوي على كلمة مرور SIP السرية بداخلها.

#### التخفيف من هجمات القوة الغاشمة وسرقة tftp

لتخفيف هذه الهجمات يمكنك تطبيق الحلول أدناه.  

Brute force: أفضل حل لتخفيف هجمات القوة الغاشمة هو منع محاولات غير مصرح بها متتالية. يستخدم تقريبًا أي مثبت لـ Asterisk أداة fail2ban لهذا الغرض. عندما يكتشف fail2ban محاولات متعددة بكلمة مرور أو اسم مستخدم خاطئ، يحظر عنوان IP للمهاجم لفترة زمنية معينة. الإجراء الثاني ضد القوة الغاشمة هو استخدام كلمات مرور قوية، أكثر من 12 حرفًا، مع وجود حرف خاص واحد على الأقل.  

Tftptheft: لمنع TFTPTheft، قم بتهيئة التزويد لاستخدام https مع اسم وكلمة مرور. يتم نقل الملف مشفرًا، ويمنع الاسم وكلمة المرور المهاجمين من محاولة تنزيل أي ملفات.

### التنصت

We don’t see a lot these types of attack because in most cases they are simply not detected. Eavesdropping is very hard to detect in an IP environment. Utilities such as UCsniff freely available are capable to eavesdrop a VoIP call in most networks. The main technique is to use ARP spoofing to force the traffic thru the computer running UCsniff and record the calls.

#### التخفيف من التنصت

يمكنك منع التنصت عن طريق تشفير حركة مرور VoIP الخاصة بك. الطريقة الأخرى هي منع هجمات الرجل في الوسط (MITM) على شبكتك. فحص ARP فعال جدًا لمنع MITM في شبكات الطبقة 2. تحقق مع دعم التقنية في شبكتك لفهم كيفية التنفيذ. لاحقًا في هذا الكتاب سنتعلم كيفية تثبيت التشفير بناءً على TLS و SRTP. يمكنك أيضًا استخدام ARPWatch لاكتشاف ما إذا كان أي شخص يسيء الآن استخدام بروتوكول ARP لمهاجمة شبكتك.

## سياسة الأمان لـ Asterisk

The best way to implement security is to create a security policy. For this training I will suggest a security policy for most Asterisk installations. Use it as the base starting point and change it according to your needs. The suggested security policy follows below:

1. عدم فتح منافذ UDP/TCP غير ضرورية  
2. عدم وجود وصول إلى أي واجهة إدارية (SSH/HTTPS) مفتوحة على الإنترنت.  
3. للوصول إلى SSH و/أو HTTP/HTTPS يجب أن تكون هناك استثناءات صريحة في جدار الحماية IPTABLES  
4. كلمات مرور قوية بطول 12 حرفًا وعلى الأقل حرف خاص واحد  
5. حظر عناوين IP التي تفشل أكثر من 10 مرات في المصادقة باستخدام Fail2ban  
6. تأكيد كلمة المرور للمكالمات الدولية  
7. تحديد وصول منفذ SIP إلى نطاق عناوين IP المعروف لديك

إذا كنت تحتاج إلى وصول خارجي إلى PBX الخاص بك، هناك احتمالان. استخدم SBC (Session Border Controller) لحماية خادمك ضد هجمات DOS/DDOS أو استخدم VPN كلما أردت وصولًا خارجيًا. إذا تركت المنفذ 5060 مفتوحًا على الإنترنت دون SBC أو VPN، فأنت معرض لهجمة DOS/DDOS. الخطر عليك.

### تقوية عصر PJSIP (Asterisk 22)

ما وراء جدار الحماية وFail2Ban، يوفر مكدس PJSIP في Asterisk 22 عدة ضوابط على مستوى التكوين يجب أن تكون جزءًا من سياسة الأمان الخاصة بك. هذه تكمل (لا تستبدل) ضوابط الشبكة المذكورة أعلاه:

- **المصادقة لكل نقطة نهاية.** يجب أن تشير كل نقطة نهاية إلى قسم `type=auth` مخصص مع `password` قوي وفريد (`auth_type=digest`). لا تعيد استخدام بيانات الاعتماد عبر نقاط النهاية.
- **معالجة المجهولين مدمجة.** لا يكشف PJSIP ما إذا كان اسم المستخدم موجودًا عندما تفشل المصادقة. لقبول المكالمات المجهولة تمامًا يجب إنشاء نقطة نهاية باسم `anonymous` واستخدام أقسام `type=identify` (مطابقة على عنوان IP المصدر) لربط الأقران المعروفين بنقاط النهاية. إذا كنت لا تريد المكالمات المجهولة، ببساطة لا تنشئ نقطة نهاية `anonymous`، وتُرفض الطلبات غير المطابقة.
- **قوائم التحكم في الوصول (ACLs).** قيد من يمكنه الوصول إلى نقطة النهاية باستخدام قوائم ACL مسماة بـ `/etc/asterisk/acl.conf`، يتم الإشارة إليها من نقطة النهاية بـ `acl=` (قائمة التحكم في الإشارة/المصدر) و`contact_acl=` (تقيد عنوان الاتصال/التسجيل). يمكنك أيضًا تعيين permit/deny مباشرة على نقطة النهاية.
- **`qualify`.** عيّن `qualify_frequency` (و`qualify_timeout`) على الـ AOR حتى يقوم Asterisk بمراقبة إمكانية الوصول إلى جهات الاتصال المسجلة وإزالة غير النشطة.
- **تقوية نقل PJSIP / حماية من هجمات حجب الخدمة (DoS).** لا يُظهر `type=transport` حدًا للعميل لكل نقل، لذا يأتي الحماية من فيض الاتصالات من جدار الحماية (قواعد iptables/Fail2Ban في هذا الفصل) بدلاً من خيار PJSIP. ما يقدمه النقل هو ضبط keep-alive لـ TCP (`tcp_keepalive_enable`، `tcp_keepalive_idle_time`، `tcp_keepalive_interval_time`، `tcp_keepalive_probe_count`) لإغلاق الاتصالات الميتة/النصف مفتوحة، وإعدادات `local_net`/`external_*` للتعامل الصحيح مع NAT. اجمع هذه مع قواعد جدار الحماية لتخفيف هجمات فيض الاتصالات.
- **TLS + SRTP للوسائط.** شفر الإشارة باستخدام نقل TLS والوسائط باستخدام `media_encryption=sdes` (أو `dtls` لـ WebRTC) على نقطة النهاية — سيتم تغطية ذلك لاحقًا في هذا الفصل.
- **التحكم في الوصول إلى AMI/ARI.** قيد واجهة مدير Asterisk (`manager.conf`) و ARI (`ari.conf` / `http.conf`) إلى localhost أو شبكة إدارة موثوقة، استخدم أسرارًا قوية وفريدة، اربط خادم HTTP بواجهة خاصة، ولا تكشف عنها على الإنترنت.

All of the option names above are confirmed against Asterisk 22.10: the `type=transport` section exposes `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net`, and the `external_*` family, but it has **no** `max_clients` option — connection-flood protection comes from the firewall, not from the transport. The `acl` and `contact_acl` endpoint options take section names from `acl.conf`, and source-IP matching for unauthenticated peers is done with `type=identify` sections (`match=`).

### إزالة المنافذ غير الضرورية

بدلاً من اكتشاف جميع الثغرات المرتبطة بجميع بروتوكولات Asterisk، دعنا نبسط المشكلة بإزالة المنافذ غير الضرورية. لسرد جميع المنافذ المفتوحة بواسطة خادم Asterisk استخدم:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

If you look at the output, you will discover that many ports are open. Do we need them? Not necessarily, 2727 is the MGCP protocol (chan_mgcp), 4569 is the IAX (chan_iax2). If you are not using these protocols, you can simply remove the module in the configuration file modules.conf.

You may notice Asterisk binding a high-numbered UDP port. This comes from `res_pjsip`'s resolver making outbound DNS queries (the source port is ephemeral, like any client DNS lookup), not from an inbound listener — your firewall only needs to allow **established/related** return traffic for it (the iptables `conntrack ESTABLISHED,RELATED` rule shown below already covers this). You do **not** need to open a wide inbound high-UDP range just for PJSIP DNS.

To remove the unnecessary ports, disable the modules you don't use. Edit the file modules.conf and add `noload` lines for the channels and protocols you are not using. **Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22:

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(في Asterisk 22 لم تعد بحاجة إلى noload `chan_mgcp` أو `chan_skinny` — تم *إزالة* تلك المشغلات في Asterisk 21 ولا هي جزء من بناء 22 القياسي.) مع التعليمات أعلاه، قمت بإزالة جميع القنوات غير الضرورية مع الاحتفاظ بـ PJSIP فقط. يمكنك اختيار أي وحدات بروتوكول تريدها، فقط احذف غير المستخدمة. النتيجة موضحة في لقطة الشاشة أدناه — فقط منفذ SIP (5060) المرتبط بنقل PJSIP الخاص بك هو الآن مكشوف للاتصالات الواردة.

![netstat output after disabling the unused modules: only UDP port 5060 remains bound by Asterisk](../images/19-security-fig06.png)

### تنفيذ سياسة الأمان باستخدام IPTABLES

IPTABLES أو netfilter هو جدار ناري قياسي موجود في معظم توزيعات لينكس. في هذا المختبر سنقوم بتهيئة iptables وfail2ban. الهدف هو تنفيذ سياسة الأمان الموصى بها لـ Asterisk وحظر جميع الحركة غير الضرورية. اتبع الخطوات أدناه:

1. حظر جميع الحركة الخارجية
2. السماح بحركة SSH من شبكة داخلية أو مضيف واحد
3. السماح بحركة SIP عبر UDP وTCP على المنفذ 5060
4. السماح بحركة RTP في نطاق منافذ الوسائط UDP. لا يوجد نطاق افتراضي مدمج واحد — `rtp.conf` الخاص بـ Asterisk يعود إلى المنافذ 5000–31000 عندما لا يتم ضبط شيء، لكن `rtp.conf.sample` المرفق يكوّن `rtpstart=10000` / `rtpend=20000`، لذا نستخدم ذلك النطاق كمثال هنا. طابق قاعدة الجدار الناري الخاصة بك مع أي `rtpstart`/`rtpend` قمت فعليًا بتعيينه في `rtp.conf`.

تأكد من أن لديك وصولًا إلى وحدة التحكم في الخادم، فلا تريد أن تحظر نفسك من النظام. كن حذرًا.

1. ثبّت الحزمة net-persistent.```
   sudo apt-get install iptables-persistent
   ```

2. السماح بجميع حركة المرور من الحلقة الخلفية```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. السماح بالاتصالات القائمة```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. السماح بحركة مرور SSH/HTTPS من الشبكة 192.168.0.0```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. إدراج قواعد Asterisk```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   لاحظ أن المنفذ 5061 (SIP over TLS) هو **TCP**، وليس UDP. القواعد أعلاه تفتح 5060 على كل من UDP و TCP و 5061 على TCP. إذا كنت تستخدم TLS فقط، يمكنك حذف قواعد 5060 العادية تمامًا. افتح فقط المنافذ التي يرتبط بها نقلات PJSIP الفعلية.

   `-I` يعني PREPEND

6. يجب أن تكون القاعدة الأخيرة عملية إسقاط```
   sudo iptables -A INPUT -j DROP
   ```

`-A` يعني APPEND. ملاحظة: احرص عند صيانة القواعد الجديدة، عليك إضافة القواعد قبل DROP. استخدم PREPEND للقواعد الجديدة `-I`

7. احفظ القواعد وأعد تشغيل iptables```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### استخدام Fail2Ban لحظر محاولات المصادقة الفاشلة المتعددة

Fail2Ban هو تقريبًا معيار لـ Asterisk. معظم المستخدمين ينفذونه لتعزيز الأمان. هذه الأداة تفحص سجلات Asterisk للبحث عن محاولات فاشلة وتمنع عناوين IP للمهاجمين. أدناه أقدم التعليمات لتثبيت Fail2Ban.

في Asterisk 22، يقوم PJSIP بالإبلاغ عن عمليات المصادقة الفاشلة وغيرها من أحداث الأمان عبر **إطار أحداث الأمان** في Asterisk، الذي يُكتب إلى قناة السجل المخصصة **`security`**. لجعل Fail2Ban يعمل عليك أن:

1. فعّل قناة الأمان في `/etc/asterisk/logger.conf`. الصياغة هي `<filename> => <levels>`، لذا لإرسال مستوى الأمان إلى ملف اسمه `security` اكتب:

```
[logfiles]
security => security
```

ثم قم بتشغيل `logger reload` من سطر الأوامر. ينتج ذلك `/var/log/asterisk/security` بسطر واحد لكل حدث أمني، بالشكل:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

الأحداث التي يهتم بها Fail2Ban هي `InvalidPassword`، `ChallengeResponseFailed`، `InvalidAccountID`، و`FailedACL`، كل منها يحمل حقل `RemoteAddress="IPV4/UDP/<ip>/<port>"` يحدد المخالف. (لاحظ أن العنوان مُغلف كـ `IPV4/UDP/.../...`، وليس IP عادي — يجب على المرشح الخاص بك استخراج المضيف من داخل تلك السلسلة.)

2. وجه سجن `asterisk` إلى ذلك الملف (`logpath = /var/log/asterisk/security`) واستخدم مرشحًا يحلل تنسيق حدث الأمان هذا.

يأتي Fail2Ban الحديث مع مرشح `asterisk` حيث أن `failregex` يتطابق بالفعل مع الأحداث المذكورة أعلاه ويستخرج `<HOST>` من حقل `RemoteAddress`، على سبيل المثال:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX distributions (FreePBX/Sangoma) ship equivalent filters. Prefer the packaged filter over hand‑writing one, since the exact event strings are version‑dependent. One caveat to be aware of: a now‑patched advisory (GHSA-5743-x3p5-3rg7) showed that crafted PJSIP traffic could inject fake log lines — keep both Asterisk and your Fail2Ban filter current.

Below I provide the instructions to install Fail2Ban

1. Install fail2ban on Linux```
   sudo apt-get install fail2ban
   ```

2. تفعيل fail2ban لـ Asterisk و SSH```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   أضف الأسطر التالية لتفعيل fail2ban لـ ssh و asterisk```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. إعادة تشغيل fail2ban```
   /etc/init.d/fail2ban restart
   ```

4. Verify. Change the secret from your softphone and try to re-register 10 times. Using `iptables -L`, check if the softphone address was included as a blocked address.
5. Remove the address from the ban (suppose the address is 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### تنفيذ TLS و SRTP

سأقسم هذا القسم إلى جزأين. في الجزء الأول سنغطي TLS لتشفير الإشارات وفي الجزء الثاني SRTP لتشفير الوسائط. الهدف هنا هو إعداد Asterisk لهذه الموارد.

#### TLS

TLS (Transport Layer Security) هو آلية التشفير المحددة لحماية إشارات SIP. يلخص الجدول أدناه أنواع الهجمات التي يحمي منها TLS:

| نوع الهجوم | محمي؟ | ملاحظات |
|----------------|-----------|-------|
| هجمات الإشارة | نعم | TLS يضمن سلامة الرسائل |
| رجل في الوسط | نعم | TLS يتحقق من شهادة الخادم |
| التنصت | لا | TLS يشفر الإشارة فقط، وليس الوسائط |

لتشفير الوسائط (الصوت/الفيديو) استخدم SRTP.

#### شهادات رقمية موقعة ذاتيًا

هناك نوعان من الشهادات يمكنك استخدامها: موقعة ذاتيًا وتجارية. الشهادات الموقعة ذاتيًا يتم توقيعها من قبل خادمك الخاص بينما الشهادات التجارية يتم توقيعها من قبل سلطة خارجية. بالنسبة للـ VoIP، يمكنك أن تكون سلطة الشهادات الخاصة بك. لا حاجة لشهادة خارجية مثل GoDaddy أو Verisign، فذلك يُعد تكلفة غير ضرورية. سنولد شهاداتنا الخاصة باستخدام ast_tls_cert.

#### إعداد TLS بشهادات موقعة ذاتيًا

فيما يلي دليل خطوة بخطوة لكيفية تنفيذ TLS. أولاً نقوم بإنشاء الشهادات، ثم نضبط نقل PJSIP TLS (انظر "Configuring TLS with chan_pjsip")، وأخيرًا نوجه الـ softphone إليه. سنستخدم SipPulse Softphone، الذي يدعم TLS و SRTP بشكل أصلي. (أي برنامج SIP softphone يدعم TLS/SRTP يعمل بنفس الطريقة.)

**Step 1.** Create a private RSA key using 3DES encryption with length of 4096 bits for our certification authority. The command below present in /usr/src/asterisk-22.x.y/contrib/scripts will create the Certification Authority and The Asterisk Certificate. As usual adapt the instructions if required, versions change, directories change. Please, pay attention on what you are doing. Use your domain or IP address in the –C option. The command ast_tls_cert has three options.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

لن أقوم بإنشاء شهادة عميل لأننا لن نستخدم الشهادة لمصادقة العميل. العميل غير مطلوب منه تقديم شهادته الخاصة.

**Step 2.** قم بتهيئة Asterisk لدعم عميلنا عبر TLS. يتم ذلك في `pjsip.conf` (نقل TLS بالإضافة إلى إعدادات الطرف النهائي) — التكوين الكامل موضح في القسم التالي، "Configuring TLS with chan_pjsip." نحن لا نقوم بالمصادقة باستخدام الشهادات، بل نشفّر فقط حركة المرور.

**Step 3.** ثبّت برنامج softphone يدعم TLS لـ SIP (المؤلف يستخدم SipPulse Softphone).

**Step 4.** انسخ سلطة الشهادة إلى الحاسوب الذي يشغّل الـ softphone. بعد تثبيتها، انسخ الملف `/etc/asterisk/keys/ca.crt` إلى الحاسوب الذي يشغّل الـ softphone (استخدم scp، أو WinSCP على Windows) إذا كنت تستخدم شهادة موقعة ذاتيًا.

**Step 5.** أنشئ الحساب في الـ softphone. في شاشة الحساب أضف الحساب كأي حساب sip آخر. استخدم كلمة المرور الصحيحة، فالمصادقة لا تزال تعتمد على كلمة المرور.

**Step 6.** عيّن TLS كوسيلة النقل في إعدادات الحساب. في شاشة حساب SipPulse Softphone (أدناه)، اختر **TLS** كوسيلة النقل واستخدم المنفذ 5061. عدّل جدار الحماية لفتح منفذ TCP 5061.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** وثّق سلطة الشهادة. إذا كانت شهادة TLS الخاصة بـ Asterisk موقعة من سلطة شهادة عامة (مثلاً Let's Encrypt — راجع فصل *Deployment*)، فإن برنامج softphone حديث مثل SipPulse Softphone يثق بها تلقائيًا عبر مخزن شهادات النظام، دون حاجة لاستيراد يدوي. إذا استخدمت شهادة موقعة ذاتيًا، استورد سلطة شهادتها (`/etc/asterisk/keys/ca.crt`) إلى العميل أو مخزن الثقة في نظام التشغيل، أو قَبِلها عند المطالبة.

**Step 8.** أنت **لست** بحاجة إلى شهادة عميل. هناك مفهوم خاطئ شائع بأن كل هاتف يحتاج إلى شهادته الخاصة للمصادقة — وهذا غير صحيح. في هذه المرحلة يقوم Asterisk فقط *بتشفير* الجلسة؛ لا تزال المصادقة تعتمد على اسم المستخدم وكلمة المرور. لا يتحقق Asterisk من شهادات العملاء بشكل افتراضي، لذا لا حاجة لتوزيع شهادة لكل عميل.

**Step 9.** بعد تغيير الشهادة أو وسيلة النقل، أعد تشغيل الـ softphone بالكامل (أغلقه وأعد تشغيله، لا تكتفِ بإغلاق النافذة فقط) حتى يعيد الاتصال عبر وسيلة النقل الجديدة.

### Configuring TLS with chan_pjsip

الآن دعنا نتعلم كيفية تهيئة PJSIP لـ TLS. PJSIP هو القناة الوحيدة لـ SIP في Asterisk 22، لذا لا يوجد ما يُبدَّل — فقط تأكد من تحميل `res_pjsip`، `res_pjproject` و`chan_pjsip`. الخطوة 1: تأكد من تمكين PJSIP في /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

الخطوة 2: قم بتكوين PJSIP لدعم TLS. أضف قسماً لنقل TLS في الملف /etc/asterisk/pjsip.conf

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

استخدم `method=tlsv1_2` (أو `tlsv1_3` إذا كان بناء OpenSSL/PJSIP الخاص بك يدعمها) — TLS 1.0/1.1 قديمة وغير آمنة ولا ينبغي استخدامها.

الخطوة 3: قم بتهيئة النقطة الطرفية لـ blink. حرّر `pjsip.conf` وعدّل القسم الخاص بـ blink. دع PJSIP يختار النقل تلقائيًا.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

الخطوة 4: التحقق. للتحقق من أن التسجيل تم عبر TLS، استخدم الأمر التالي في وحدة تحكم Asterisk.

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### إجراء مكالمات آمنة باستخدام SRTP

البروتوكول المسؤول عن تشفير الوسائط هو Secure Real Time Protocol (SRTP) المُعرّف في RFC3711. أحد العوائق القصيرة للبروتوكول هو عدم وجود طريقة موحدة لتبادل المفاتيح. يستخدم Asterisk تبادل مفاتيح SDES عبر بروتوكول SDP محمي بتشفير الإشارة المقدم بواسطة TLS. هناك أيضًا طرق أخرى مثل MIKEY وZRTP. تم تطوير ZRTP بواسطة Philipp Zimmermann وهو من أكثر الطرق تعقيدًا لتبادل المفاتيح وتشفير الوسائط. تسمح بعض softphones والهواتف الصلبة بـ ZRTP. ومع ذلك، لا يزال الأسلوب القياسي هو SDES وستجد هذه الطريقة في تقريبًا أي هاتف متاح في السوق. أدناه مثال لطلب يحتوي على مفاتيح التشفير المعرفة في SDP في السطرين a=crypto:1 و a=crypto:2.

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### تكوين SRTP على Asterisk

لتكوين SRTP على Asterisk أمر بسيط للغاية. اضبط `media_encryption=sdes` على الطرف النهائي؛ يمكنك أيضًا طلب ذلك باستخدام `media_encryption_optimistic=no` بحيث يتم رفض الوسائط غير المشفرة بدلاً من السماح بها صامتًا. لاحظ أن SDES يتطلب تشغيل الإشارة عبر TLS حتى لا تُرسل المفاتيح بوضوح.

**Step 1.** Asterisk configuration

Set the following on the `type=endpoint` section in `pjsip.conf`:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** تكوين برنامج الهاتف الناعم

في برنامج الهاتف الناعم، فعّل SRTP لوسائط الحساب (اضبط خيار **SRTP (Media Encryption)** إلى *Mandatory*) حتى يتم تشفير الصوت.

![إعدادات حساب SipPulse Softphone (القسم السفلي) — اضبط **Transport** إلى TLS و **SRTP (Media Encryption)** إلى *Mandatory* بحيث يتم تشفير الإشارة والوسائط معًا.](../images/softphone/sipphone-config.png){width=35%}

## تمكين المصادقة الثنائية للمكالمات الدولية

أحيانًا تكون أفضل طريقة هي عدم وجود مسارات دولية. ومع ذلك، إذا كنت بحاجة فعلًا إلى الاتصال الدولي، استخدم كلمة مرور إضافية. سنستخدم تطبيق Asterisk `vmauthenticate` لطلب كلمة مرور البريد الصوتي قبل الاتصال دوليًا. يتم تكوين ذلك في الـ dialplan داخل ملف `extensions.conf`. انظر المثال أدناه. وبالتالي، سيحتاج المخترق، حتى بعد اكتشاف كلمة مرور الـ peer أو اختراق هاتف، إلى كلمة مرور البريد الصوتي للاتصال بهذا الوجهة.

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` لا يزال تطبيقًا قياسيًا في Asterisk 22. الـ `Dial()` أعلاه يوجه المكالمة عبر خط SIP/PJSIP (`PJSIP/<number>@<trunk>`)، وهو ما تستخدمه معظم التركيبات الحديثة للوصول إلى الـ PSTN — عدّل `my_trunk` ليتناسب مع اسم الخط الخاص بك، واستخدم `DAHDI/g1/...` فقط إذا كان لديك فعلاً امتداد DAHDI. الدفاع ضد الاحتيال في الرسوم داخل الـ dialplan — عامل ثانٍ مثل هذا، مع تقييد أي السياقات يمكنها الوصول إلى مساراتك الصادرة والدولية — يظل أحد أهم الحمايات التي يمكنك نشرها.

## الملخص

في هذا الفصل تعلمت عن مخاطر توصيل نظام IP PBX بالإنترنت. ثم تعلمنا كيفية حماية نظام PBX الخاص بنا من خلال تنفيذ سياسة أمان. في هذه السياسة الأمنية قمنا بتنفيذ iptables، fail2ban، TLS، SRTP والمصادقة ذات الاتجاهين للمكالمات الدولية. آمل أن تكون قد استمتعت بهذا الفصل.

## Quiz

1. ما هو أهم إجراء مضاد للاحتيال في مشاركة إيرادات الإنترنت؟
   - A. تنفيذ SRTP
   - B. الحفاظ على تحديث Asterisk
   - C. تنفيذ TLS
   - D. استخدام كلمات مرور قوية
2. يُعرّف fuzzing في SIP بأنه:
   - A. هجوم DoS باستخدام طلبات وردود مشوهة
   - B. سرقة خدمة حيث تُكسر كلمات المرور بالقوة
   - C. التنصت على المكالمات الحالية
   - D. هجوم DDoS بفيض من طلبات SIP
3. يحدث TFTPTheft عندما يقدم الخادم ملفات التكوين عبر TFTP. يمكنك تجنبه باستخدام:
   - A. FTP
   - B. HTTP
   - C. HTTPS مع اسم مستخدم وكلمة مرور
   - D. SCP
4. تستخدم هجمات الرجل في الوسط تقنية تسمى:
   - A. TFTP theft
   - B. ARP spoofing
   - C. MAC poisoning
   - D. dsniff
5. بالنسبة لـ SRTP، يستخدم Asterisk النظام التالي لتبادل المفاتيح:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. الأداة التي تُنشئ سلطة الشهادات والشهادات، الموجودة في `/usr/src/asterisk-22.x.y/contrib/scripts`، هي:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. استراتيجيات صالحة لمنع التنصت (اختر كل ما ينطبق):
   - A. تنفيذ كواشف تنصت تناظرية
   - B. استخدام أداة ARPwatch لاكتشاف ARP spoofing
   - C. تمكين اكتشاف ARP-spoofing في المفاتيح
   - D. استخدام SRTP
8. يدعم Asterisk المصادقة القوية عن طريق التحقق من شهادات العملاء. (يمكن لنقل PJSIP TLS أن يطلب ويُحقق من شهادة العميل.)
   - A. True
   - B. False
9. في Asterisk 22، أي إعداد لنقطة النهاية PJSIP يُفعّل تشفير وسائط SRTP باستخدام مفاتيح in‑SDP (SDES)؟
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. في Asterisk 22، يجب أن يقرأ Fail2Ban أحداث فشل المصادقة في PJSIP من قناة السجل المخصصة ________ (مفعلة في `logger.conf`).
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
