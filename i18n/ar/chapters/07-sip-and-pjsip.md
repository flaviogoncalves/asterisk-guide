# SIP & PJSIP in depth

SIP هو البروتوكول؛ PJSIP هو الطريقة التي يتحدث بها Asterisk 22. **PJSIP** (`chan_pjsip`, يتم تكوينه عبر `pjsip.conf`) هو برنامج تشغيل قناة SIP الوحيد في Asterisk 22 LTS. هذه الفصل يغطي أساسيات بروتوكول SIP (التي هي على مستوى البروتوكول وتظل صالحة بنسبة 100٪) ونموذج كائن PJSIP وتكوينه الذي تستخدمه يوميًا. تم تغطية برنامج تشغيل legacy المتقاعد ودليل الترحيل في فصل *Legacy channels*.

## الأهداف

- شرح دور وكلاء مستخدمي SIP، الوكلاء، المسجل، والبوابات؛
- متابعة تدفق مكالمة SIP أساسي (REGISTER، INVITE، الردود الأولية والنهائية، ACK، BYE) وقراءة رسالة SIP؛
- وصف كيفية تفاوض SDP لجلسة الوسائط وكيف يؤثر NAT على إشارات SIP وRTP؛
- رسم خريطة نموذج كائنات PJSIP — `endpoint`، `auth`، `aor`، `transport`، `identify`، و`registration` — وكيف تشير الكائنات إلى بعضها البعض؛
- تكوين هواتف SIP والخطوط في `pjsip.conf`، بما في ذلك خيارات عبور NAT؛ و
- التحقق من نقاط النهاية واستكشاف أخطائها باستخدام أوامر CLI `pjsip show …`.

## أساسيات بروتوكول SIP

بروتوكول بدء الجلسة (SIP) هو بروتوكول نصي يشبه HTTP وSMTP صُمم لبدء، الحفاظ على، وإنهاء جلسات الاتصال التفاعلية بين المستخدمين. قد تشمل هذه الجلسات الصوت، الفيديو، الدردشة، الألعاب التفاعلية، وغيرها. تم تعريف SIP من قبل IETF وأصبح المعيار الفعلي للاتصالات الصوتية. من المهم جداً فهم كيفية عمل SIP. في Asterisk 22، توجد إعدادات SIP في `pjsip.conf`، وهو أحد الملفات التي يتم تعديلها بشكل متكرر في نظام يعتمد على SIP (بعد `extensions.conf` مباشرة).

### نظرية التشغيل

SIP هو بروتوكول إشارة يحتوي على المكونات التالية: User Agent Client, User Agent Servers, SIP Proxies, و SIP Gateways. الشكل التالي يوضح العلاقات بين هذه المكونات.

- UAC (user agent client) – العميل أو الطرفية التي تبدأ إشارة SIP.  
- UAS (user agent server) – الخادم الذي يرد على إشارة SIP القادمة من UAC.  
- UA (user agent) – طرف SIP (هواتف أو بوابات تحتوي على كل من UAC و UAS).  
- Proxy Server – يستقبل الطلبات من UA وينقلها إلى بروكسيات SIP أخرى إذا لم تكن المحطة المعنية تحت إدارته.  
- Redirect Server – يستقبل الطلبات ويرسلها مرة أخرى إلى UA، متضمنًا بيانات الوجهة، بدلاً من توجيهها مباشرة إلى الوجهة.  
- Location Server – يستقبل الطلبات من UA ويحدّث قاعدة بيانات الموقع بهذه المعلومات.

عادةً ما يتم استضافة خوادم الوكيل وإعادة التوجيه والموقع على نفس الجهاز وتستخدم نفس برنامج، والذي نسميه **وكيل SIP**. يكون وكيل SIP مسؤولاً عن صيانة قاعدة بيانات الموقع، إنشاء الاتصال، وإنهاء الجلسة.

![المكونات الرئيسية لـ SIP: وكلاء المستخدم (UAC/UAS/UA)، خادم التسجيل/الوكيل/إعادة التوجيه، وبوابة إلى PSTN، مع تدفق وسائط RTP مباشرة بين نقاط النهاية](../images/07-sip-and-pjsip-fig01.png)

#### عملية تسجيل SIP

قبل أن يتمكن الهاتف من استقبال المكالمات، يحتاج إلى التسجيل في قاعدة بيانات المواقع. في قاعدة بيانات المواقع، سيتم ربط عنوان IP بالاسم. في المثال التالي، سيتم ربط الامتداد 8500 بعنوان IP 200.180.1.1. لا يلزم بالضرورة استخدام أرقام هواتف. في بنية SIP، يمكن أن يكون الامتداد المسجل flavio@voip.school أيضًا.

![تسجيل SIP: يرسل الهاتف طلب REGISTER يربط الامتداد 8500 إلى عنوان IP الخاص به، يقوم المسجل بتخزين جهة الاتصال في قاعدة بيانات الموقع ويرد بـ 200 OK](../images/07-sip-and-pjsip-fig02.png)

#### تشغيل الوكيل

When operating as a SIP proxy, the SIP server stays in the middle of the signaling and is capable of advanced routing and billing. The media flow, based on the real time protocol (RTP) still goes directly between the endpoints.

![عملية الوكيل: يبقى وكيل SIP في مسار الإشارة (INVITE/200 OK) ويبحث عن المتصل في خادم الموقع، بينما يتدفق وسائط RTP مباشرة بين الطرفين](../images/07-sip-and-pjsip-fig03.png)

#### عملية إعادة التوجيه

عند إعادة التوجيه، يرسل خادم SIP ببساطة رسالة (e.g., 302 moved temporarily) إلى وكيل المستخدم ويظل خارج مسار الرسائل الجديدة. إنه خفيف جدًا من حيث استهلاك الموارد، لكن لا يمكنك التحكم على الإطلاق. تُستخدم إعادة التوجيه أحيانًا في تصاميم موازنة التحميل.

![عملية إعادة التوجيه: يجيب خادم إعادة التوجيه على INVITE برمز 302 Moved Temporarily يحمل معلومات الاتصال، ثم يتنحى جانبًا بينما يعيد المتصل إرسال INVITE/ACK مباشرة إلى الموقع الجديد](../images/07-sip-and-pjsip-fig04.png)

#### كيف يتعامل Asterisk مع SIP

من المهم أن نفهم أن Asterisk ليس بروكسي SIP ولا موجه إعادة توجيه SIP. يمكن لـ Asterisk أن يؤدي دور مسجل الخادم وموقع الخادم؛ ومع ذلك، فإنه يربط فقط بين عميلين مستخدمين (UAC) إلى نفسه. لذلك، يُعتبر Asterisk وكيل مستخدم خلفي إلى خلفي (B2BUA). بعبارة أخرى، يربط بين قناتين SIP، جاعلاً إياهما جسرًا معًا. يمتلك Asterisk آلية إعادة‑دعوة يمكنها جعل قنوات SIP تتحدث مع بعضها مباشرةً بدلاً من المرور عبر Asterisk. في نقطة نهاية PJSIP يتم التحكم في ذلك بواسطة المعامل `direct_media`. عند استخدام `direct_media=yes` يتدفق RTP مباشرةً من نقطة نهاية إلى أخرى، مما يحرر موارد الخادم.

#### تشغيل SIP مع direct_media=yes

![تشغيل SIP مع directmedia=yes: إشارة SIP تمر عبر Asterisk بينما ينتقل صوت RTP مباشرة بين الهاتفين، مما يحرر موارد الخادم】(../images/07-sip-and-pjsip-fig05.png)

مع ذلك، إذا كنت بحاجة إلى تحويل أو تسجيل المكالمة باستخدام Asterisk، يمكنك استخدام المعامل `direct_media=no` لإجبار تدفق RTP عبر خادم Asterisk.

#### تشغيل SIP مع direct_media=no

![تشغيل SIP مع directmedia=no: كل من إشارات SIP وصوت RTP يتم تثبيتهما عبر Asterisk، مما يسمح له بتسجيل المكالمة أو تحويل الترميز أو نقل المكالمة】(../images/07-sip-and-pjsip-fig06.png)

#### رسائل SIP

الرسائل الأساسية لـ SIP هي:

- INVITE – إنشاء الاتصال
- ACK – تأكيد
- BYE – إنهاء الاتصال
- CANCEL – إنهاء الاتصال لمكالمة غير مُنشأة
- REGISTER – تسجيل UAC إلى بروكسي SIP
- OPTIONS – يمكن استخدامها للتحقق من التوفر
- REFER – نقل مكالمة SIP إلى شخص آخر
- SUBSCRIBE – الاشتراك في أحداث الإشعارات
- NOTIFY – إرسال معلومات القناة
- INFO – إرسال رسائل متنوعة (مثال، DTMF )
- MESSAGE – إرسال رسائل فورية

استجابات SIP هي بصيغة نصية ويمكن قراءتها بسهولة (مشابهة لرسائل HTTP). أهم الاستجابات هي:

- 1XX – رسائل معلوماتية (100–trying, 180–ringing, 183–progress)
- 2XX – طلب ناجح مكتمل (200 – OK)
- 3XX – إعادة توجيه المكالمة، يجب توجيه الطلب إلى مكان آخر (302 – moved temporarily, 305 – use proxy)
- 4XX – خطأ (403 – Forbidden)
- 5XX – خطأ في الخادم (500 – Internal Server Error; 501 – Not implemented)
- 6XX – فشل عالمي (606 – Not acceptable)

على سبيل المثال:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### بروتوكول وصف الجلسة (SDP)

تم تعريف SDP أصلاً في IETF RFC 2327، وتم إلغاؤه الآن بـ RFC 4566. يهدف إلى وصف جلسات الوسائط المتعددة لأغراض إعلان الجلسة، دعوة الجلسة، وأشكال أخرى من بدء جلسة الوسائط المتعددة. يتضمن SDP:

- بروتوكول النقل (RTP/UDP/IP)
- نوع الوسائط (نص، صوت، فيديو)
- تنسيق الوسائط أو الترميز (فيديو H.261، صوت g.711، إلخ)
- المعلومات اللازمة لاستلام هذه الوسائط (عناوين، منافذ، إلخ)

المثال التالي هو نسخة مكتوبة من SDP تصف مكالمة بين هاتفين.

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### تجاوز NAT لبروتوكول SIP

Network Address Translation (NAT) هي ميزة تُستخدم في معظم الشبكات لتوفير عناوين IP على الإنترنت. عادةً، تتلقى الشركة كتلة صغيرة من عناوين IP، ويتلقى المستخدمون النهائيون عنوان IP واحد بشكل ديناميكي عند الاتصال بالإنترنت. يحل NAT مشكلة العنونة عن طريق ربط العناوين الداخلية بالعناوين الخارجية. يخزن ربط العناوين الداخلية إلى الخارجية في ذاكرته. يكون هذا الربط صالحًا لمدة زمنية محددة، وبعدها يتم حذف الربط. يستخدم الربط أزواج IP:port للعناوين الداخلية والخارجية. هناك أربعة أنواع من NAT:

- مخروط كامل
- مخروط مقيد
- مخروط مقيد بالمنفذ
- متناظر

نظرية NAT أدناه — الأنواع الأربعة لـ NAT، مشكلة رأس Contact، رسائل keep-alives، وإجبار الوسائط عبر الخادم — هي على مستوى البروتوكول وتطبق على أي تنفيذ SIP. الطريقة التي تقوم فيها بتكوين كل سلوك على Asterisk 22 (PJSIP) مغطاة لاحقًا في هذا الفصل تحت *Nat traversal on res_pjsip*.

#### مخروط كامل

أول NAT، full cone، يمثل تعيينًا ثابتًا من زوج IP:port خارجي إلى زوج IP:port داخلي. يمكن لأي حاسوب خارجي الاتصال به باستخدام زوج IP:port الخارجي. هذا هو الحال في الجدران النارية غير الحالة التي تُنفّذ باستخدام الفلاتر.

![Full Cone NAT: المضيف الداخلي (10.0.0.1:8000) يتم تعيينه ثابتًا إلى الزوج الخارجي 200.180.4.168:1234، بحيث يمكن لأي حاسوب خارجي إرسال حزم إلى ذلك الزوج والوصول إلى المضيف الداخلي](../images/07-sip-and-pjsip-fig11.png)

#### المخروط المقيد

في سيناريو الـ **restricted cone**، يتم فتح زوج الـ IP:port الخارجي فقط عندما يرسل الحاسوب الداخلي بيانات إلى عنوان خارجي. ومع ذلك، يقوم الـ **restricted cone NAT** بحظر أي حزم واردة من عنوان مختلف. بعبارة أخرى، يجب على الحاسوب الداخلي إرسال بيانات إلى حاسوب خارجي قبل أن يتمكن من استلام بيانات مرة أخرى.

#### مخروط مقيد بالمنفذ

جدار الحماية من نوع المخروط المقيد بالمنفذ يكاد يكون مطابقا للمخروط المقيد. الفرق الوحيد هو أنه الآن يجب أن تأتي الحزمة الواردة من نفس عنوان الـ IP والمنفذ تمامًا للحزمة المرسلة.

#### متناظر

النوع الأخير من NAT يُسمى متماثل. وهو يختلف عن الأنواع الثلاثة الأولى في أن هناك تعيينًا محددًا يُجرى لكل عنوان خارجي. يُسمح فقط لعناوين خارجية محددة بالعودة عبر تعيين الـ NAT. لا يمكن التنبؤ بزوج الـ IP:port الخارجي الذي سيستخدمه جهاز الـ NAT. الأنواع الثلاثة الأخرى من NAT تسمح باستخدام خادم خارجي لاكتشاف عنوان الـ IP الخارجي للتواصل. مع الـ NAT المتماثل، حتى إذا استطعت الاتصال بخادم خارجي، لا يمكن استخدام العنوان المكتشف لأي جهاز آخر سوى هذا الخادم.

![NAT متماثل: يتم تخصيص منفذ مصدر خارجي مختلف لكل وجهة، لذا لا يمكن إعادة استخدام الخريطة المكتشفة نحو خادم واحد من قبل مضيف آخر، مما يكسر التجاوز القائم على STUN](../images/07-sip-and-pjsip-fig12.png)

#### جدول جدار الحماية NAT

الجدول التالي يلخص الأنواع الأربعة لـ NAT.

| نوع NAT | يجب إرسال البيانات أولاً | يمكن تحديد عنوان IP:المنفذ الخارجي للحزم العائدة | يقيّد الحزم الواردة إلى عنوان IP:المنفذ الوجهة |
| --- | --- | --- | --- |
| Full Cone | لا | نعم | لا |
| Restricted Cone | نعم | نعم | IP فقط |
| Port Restricted Cone | نعم | نعم | نعم |
| Symmetric | نعم | لا | نعم |

#### إشارة SIP و RTP عبر NAT

بعض أكبر المشكلات في تجاوز NAT هي أنه يجب حل مشكلتين: إشارة SIP والصوت (RTP). معظم مشاكل الصوت أحادي الاتجاه مرتبطة بـ NAT. شيء مثير للاهتمام حول SIP هو أنه عندما يرسل UAC حزمة، يدمج عنوان IP في حقل رأس SIP “Contact”. عادةً ما يكون هذا عنوانًا داخليًا (RFC1918)؛ ولا يمكن توجيه الردود على هذه الحزمة عبر الإنترنت إلى الـ UAC. الإصلاحات المفهومية تكون دائمًا هي نفسها:

- **تجاهل عنوان Contact/Via والرد إلى المكان الذي وصل منه الحزمة فعليًا.** هذا هو السلوك المحدد في RFC 3581 (`rport`). على PJSIP هو `force_rport=yes`، و`rewrite_contact=yes` يعيد كتابة عنوان الاتصال المخزن إلى عنوان المصدر.  
- **إرسال الوسائط مرة أخرى إلى العنوان الذي وصل منه RTP فعليًا** (RTP متماثل، كان يُطلق عليه تاريخيًا *comedia*). على PJSIP هذا هو `rtp_symmetric=yes`.  
- **الحفاظ على خريطة NAT مفتوحة.** إذا انتهت مهلة الخريطة، لا يستطيع Asterisk إرسال INVITE إلى UAC — يمكن للهاتف إجراء المكالمات لكنه لا يستطيع استقبالها. إرسال OPTIONS دوريًا (وهو *qualify*) يحافظ على الفتحة مفتوحة. على PJSIP هذا هو `qualify_frequency=` على الـ AOR.

إذا كان NAT الخاص بالمستخدم من النوع المتماثل، لا يمكن إرسال الحزم من UAC إلى آخر مباشرةً؛ في هذه الحالة يجب إجبار RTP على المرور عبر Asterisk باستخدام `direct_media=no`. هذه التكوينات مناسبة لمعظم الحالات. يمكن تحسين حركة المرور باستخدام تقنيات متقدمة مثل Simple Traversal of UDP over NAT (STUN)، والتي تكون مفيدة مع full cone و restricted cone و port restricted cone، و Application Layer Gateway (ALG). للأسف، معظم جدران الحماية اليوم — حتى أجهزة توجيه DSL/الكابل المنزلية — تكون متماثلة، مما يجعل STUN غير قابل للاستخدام. قد يحل ALG المشكلة، لكنه غير مدعوم أو غير مُنفَّذ أو يحتوي على أخطاء في معظم الحالات.

#### Asterisk خلف NAT

أحيانًا يتم تنفيذ خادم Asterisk نفسه خلف جدار ناري مع NAT — وهو وضع شائع جدًا عند النشر في السحابة. في هذه الحالة من الضروري إجراء بعض التكوين الإضافي بحيث يعلن Asterisk عن عنوانه **public** في رؤوس SIP و SDP بدلاً من عنوانه الخاص.

مفهومياً هناك ثلاث خطوات:

- قم بإعادة توجيه منفذ إشارة SIP (UDP 5060 افتراضيًا) من الجدار الناري إلى خادم Asterisk.
- قم بإعادة توجيه نطاق منافذ وسائط RTP (UDP 10000–20000 افتراضيًا، محدد في `rtp.conf`) من الجدار الناري إلى خادم Asterisk.
- أخبر Asterisk بعنوانه الخارجي والشبكة المحلية، حتى يعرف متى يستبدل العنوان العام في الرؤوس.

في PJSIP تُطابق هاتان العنصران الأخيران إلى `external_media_address` / `external_signaling_address` و`local_net=` على **transport**، ولا يزال نطاق منفذ RTP مُكوَّنًا في `rtp.conf`:

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

The complete, worked PJSIP configuration for an Asterisk server behind NAT is given later in this chapter under *Asterisk Server behind NAT*.

### قيود SIP

Asterisk يستخدم تدفق RTP الوارد لمزامنة التدفق الصادر. إذا تم قطع التدفق الوارد (كتم الصمت)، سيتوقف تشغيل الموسيقى أثناء الانتظار. بعبارة أخرى، لا ينبغي لك استخدام كتم الصمت في الهواتف أو المزودين مع Asterisk.

## PJSIP: قناة SIP

PJSIP هي قناة SIP في Asterisk. تم تقديمها لأول مرة في Asterisk 12 وبعد سنوات من التطوير أصبحت القناة الافتراضية والمُوصى بها، وفي Asterisk 22 (الإصدار طويل الدعم الحالي) هي السائق الوحيد لقناة SIP. PJSIP مبنية على مشروع Teluu المسمى pjproject. تُستَخدم مجموعة pjproject من قبل العديد من softphones وتنفيذات SIP التجارية. إنها مجموعة SIP متعددة الاستخدامات وناضجة.

### لماذا نستخدم PJSIP

PJSIP كان إعادة تصميم من الصفر لكيفية تواصل Asterisk مع SIP، ومن المفيد فهم الميزات التي جعلتها المعيار.

#### الميزات

القناة تدعم العديد من الميزات، وبعضها يستحق الذكر هنا

- تسجيلات متعددة: يمكنك استخدام أكثر من هاتف متصل بنفس Address of Record. بعبارة أخرى، يمكنك ربط هاتفين بنفس endpoint.
- واجهة برمجة تطبيقات (API) صديقة. الـ API معيارية وسهلة التوسيع، مبنية من عدة وحدات صغيرة متعاونة بدلاً من كتلة شفرة واحدة كبيرة.
- نقلات متعددة: يمكنك الاستماع إلى عناوين، منافذ ونقلات متعددة عند استخدام PJSIP. لست مقيدًا بعنوان ربط واحد لجميع أجهزتك. PJSIP مرنة جدًا.

#### ملاحظة حول التكوين

تكوين PJSIP أكثر تفصيلاً: يتطلب جهدًا قليلًا أكثر وعددًا أكبر من أسطر التكوين، لأن كل جهاز يُوصف بعدة كائنات مرتبطة بدلاً من كتلة peer واحدة. هذا الهيكل الإضافي هو ما يمنح PJSIP مرونتها، ومعالج التكوين (المغطى لاحقًا) يبقي عملية التزويد اليومية قصيرة.

### وحدات PJSIP

قناة PJSIP تُنفَّذ بواسطة العديد من الوحدات الموضحة أدناه:

#### res_pjsip

هذه هي الطبقة الأساسية لـ PJSIP والوحدة الرئيسية. هي المسؤولة عن بعض الخدمات الأساسية.

#### res_pjsip_session

هذه الوحدة مسؤولة عن جلسات الوسائط، معالجة بروتوكول وصف الجلسة وبعض الإضافات.

#### res_pjsip_messaging

معالجة رسائل SIP وتحليل رؤوس SIP.

#### res_pjsip_registrar

مسؤولة عن معالجة تسجيلات SIP.

#### res_pjsip_pubsub

مسؤولة عن معالجة الاشتراك، الإشعار والنشر. هذه الرسائل مسؤولة عن معالجة وجود SIP وBLF (Busy Lamp Field).

### تكوين PJSIP

لـ PJSIP أقسام متعددة. صيغة القسم هي:

```
[Section Name]
Option = Value
Option = Value
```

#### قسم نقطة النهاية

أهم كائن تكوين هو endpoint. تكوين endpoint يحتوي على وظائف أساسية ويجب ربطه بـ AOR وقسم Transport. مثال:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

If you look at the example above, the endpoint is a kind of glue linking all sections together. It specifies a transport, the address of record and the authentication for a phone. Also defines the most important part, the context entry point in the dialplan.

#### Address of Record (AOR)

This object tells Asterisk where to contact the endpoint. It stores the contact addresses. It also allow the configuration of mailboxes. Example:

```
[softphone]
type=aor
max_contacts=2
```

#### المصادقة

هذا القسم مسؤول عن المصادقة الواردة والصادرة. الوثائق موجودة في ملف المثال pjsip.conf. مثال:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### النقل

يسمح لك قسم النقل بتعريف عناوين IPV4 و IPV6 وبروتوكول النقل، TCP، UDP، TLS، Websockets وما إلى ذلك. يمكنك أيضًا تكوين عناوين مُعَنوَنَة في هذا القسم. يمكنك إنشاء عدة نقلات، لكن لا يمكنها مشاركة نفس عنوان IP والمنفذ ولا يمكنك ربط عدة نقلات TCP أو TLS لنفس نسخة IP. مثال:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### التسجيل

يُستخدم هذا الكائن لتكوين تسجيل صادر. مثال:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### التعريف

هذا الكائن يتحكم في تحديد أي طلب SIP ينتمي إلى كل نقطة نهاية. إذا لم يكن لديك قسم تعريف، سيطابق النظام محتوى رأس “From” مع اسم نقطة النهاية. باستخدام هذا القسم، يمكنك تعيين عناوين IP محددة لنقاط نهاية محددة، يتم التعرف عليها بواسطة اسم المستخدم أو عنوان IP. مثال:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

كائن ACL يتيح لك تكوين شبكات محددة للوصول إلى endpoint. الآن يتم تعريف ACLs في قسم محدد أو في acl.conf. مثال:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### العلاقة بين الكيانات

العلاقة بين كائنات التكوين توفر مرونة كبيرة في الإعداد. ومع ذلك، قد تبدو معقدة قليلاً لأي مبتدئ.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

المخطط أعلاه يعني:

#### العلاقات:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | متعدد إلى متعدد |
| ENDPOINT / AUTH | صفر إلى متعدد، إلى صفر إلى واحد |
| ENDPOINT / IDENTIFY | صفر إلى واحد |
| ENDPOINT / TRANSPORT | صفر إلى متعدد، إلى على الأقل واحد |
| REGISTRATION / AUTH | صفر إلى متعدد، إلى صفر إلى واحد |
| REGISTRATION / TRANSPORT | صفر إلى متعدد، إلى على الأقل واحد |
| AOR / CONTACT | متعدد إلى متعدد |

ACL و DOMAIN_ALIAS لا يمتلكان علاقة تكوين مباشرة مع الكائنات الأخرى.

### إعداد Softphone

لإعداد Softphone عليك تعريف أقسام متعددة مختلفة. أدناه مثال على كيفية إعداد Softphone. للجانب العميل يمكنك استخدام SipPulse Softphone (https://www.sippulse.com/produtos/softphone)، والذي يمكنك تحميله وتسجيله ضد الـ endpoint أدناه.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

The configuration above sets a transport for UDP in the port 5060, then define an endpoint, its authentication by username and password and then the Address of Record with a maximum of two contacts.

### تكوين خط SIP

To configure a SIP trunk you need to have the IP address or Host of the SIP trunk, name and password. You have to create a new registration section for this purpose.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Nat traversal on res_pjsip

تم إنشاء ترجمة عناوين الشبكة (NAT) منذ زمن طويل كطريقة للتعامل مع نقص عناوين IPv4. يستخدم الكثيرون NAT أيضًا كميزة أمان لإخفاء العناوين الداخلية لشبكة ما عن الإنترنت العام. أحيانًا سيتعين عليك التعامل مع عبور NAT. في بعض الحالات قد يكون الخادم خلف NAT، مثلما يحدث عندما تقوم بنشر الخادم في السحابة. كثيرًا ما يكون المستخدمون أيضًا خلف موجه NAT عند النشر في السحابة. لتنظيم الأمور، سنقسم هذا إلى جزأين. الجزء الأول هو خادم Asterisk خلف NAT كما في نشر السحابة. في القسم الثاني، سنغطي كيفية دعم العملاء خلف NAT باستخدام res_pjsip.

#### Asterisk Server behind NAT

عند وجود خادم Asterisk خلف NAT، يجب إعلامه بالعناوين الخارجية والداخلية المحلية في قسم النقل. سيكون لدينا التوجيهات التالية.

##### direct_media

هل يتدفق الوسائط مباشرةً من نظير إلى نظير أم عبر الخادم؟ بالنسبة لـ NAT يجب أن يتدفق عبر الخادم. بالنسبة لـ NAT اختر لا. مثال:

```
direct_media=no
```

##### external_media_address

عنوان الوسائط للتعامل مع RTP الخارجي. عادةً يكون هو نفسه external_signaling_address. استخدم عنوان IP العام لخادمك للوسائط والإشارة. مثال:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

عنوان SIP الخارجي لتلقي الرسائل. مثال:

```
external_signaling_address=54.232.1.20
```

##### local_net

الشبكة التي تعتبرها شبكتك المحلية. مثال:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### مثال كامل للنقل لخادم Asterisk خلف NAT

لاستخدام خادم Asterisk خلف NAT يجب تنفيذ خطوتين. أولاً، تعريف نقل خلف NAT. ثانياً، ربط هذا النقل بنقطة النهاية.

##### إنشاء النقل خلف NAT

لإنشاء النقل خلف NAT في ملف pjsip.conf، أنشئ قسماً كما هو موضح أدناه.

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

ربط النقل بنقطة النهاية

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

بالنسبة لخطوط SIP trunks يجب أيضًا ربط الـ transport بقسم التسجيل كما هو موضح أدناه.

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### استخدام Asterisk مع العملاء خلف NAT

لاستخدام الهواتف خلف NAT يجب عليك ضبط بعض المعلمات الإضافية لكل نقطة نهائية.

##### direct_media

هل يتدفق الوسائط مباشرةً من نظير إلى نظير أم عبر الخادم؟ بالنسبة لـ NAT يجب أن يتدفق عبر الخادم. مثال:

```
direct_media=no
```

##### rtp_symmetric

هذا ما نسميه comedia. بدلاً من الاعتماد على العنوان المحدد في رأس SDP كما هو معتاد في SIP، استخدم العنوان الذي تستقبل منه أول حزمة rtp وأرسل الرد من نفس العنوان. مثال:

```
rtp_symmetric=yes
```

##### force_rport

هذا هو السلوك المحدد في RFC3581. بدلاً من استخدام العنوان في رأس VIA، أرسل الردود من حيث تأتي الطلبات. مثال:

```
force_rport=yes
```

##### qualify_frequency

يجب تطبيق هذا الإعداد على الـ AOR (ليس على الـ endpoint). هناك أيضًا الخطوة الأخيرة، وهي تكوين خيار الـ qualify. يجب أن يكون لديك دائمًا بعض الحزم التي تُرسل ping إلى الوجهة للحفاظ على فتح خريطة الـ NAT. يتم ذلك في قسم الـ AOR. مثال:

- qualify_frequency=15

مثال كامل على endpoint يكون فيه الخادم والعميل خلف الـ NAT

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### Channel Naming

كما هو معتاد، أحد الجوانب المهمة للقناة هو تسميتها ولـ PJSIP بعض التفاصيل المثيرة للاهتمام. تقوم بالاتصال بنقطة نهاية PJSIP باستخدام تقنية `PJSIP/`.

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

ميزة مفيدة هي إمكانية طلب جميع جهات الاتصال المسجلة إلى AOR مرة واحدة. سيتم ترجمة الدالة PJSIP_DIAL_CONTACTS إلى قائمة جهات الاتصال التي سيتم طلبها.

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

To dial a trunk is slightly different. Assume the trunk won’t be registered to your platform or don’t have and IP address associated with your AOR address of record. You can specify the address of the trunk directly in the line. Using an international dial as the example.

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

إذا كنت تفضل تحديد عنوان الخط في قسم AOR، يمكنك أيضًا استخدامه.

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### معالج إعداد PJSIP

PJSIP قوي لكنه مطول في الإعداد: أقسام متعددة مختلفة، وقوالب قد تكون مربكة في البداية. الخبر السار هو وجود معالج إعداد PJSIP. من خلال تعريف كل قناة في بضع سطور، يتيح لك إنشاء قوالب وتبسيط إعداد الأجهزة الجديدة. استخدم الملف **pjsip_wizard.conf** للإعداد. لا يزال عليك تعريف أقسام النقل والعالمية في الملف **pjsip.conf**. شخصيًا، أفضل استخدام المعالج فقط للهواتف، أما بالنسبة للـ sip trunks فعادةً ما يكون العدد غير كبير ويمكنك الإعداد مباشرةً في pjsip. أكبر ميزة للمعالج هي إمكانية استخدام القوالب وإنشاء الهواتف بسرعة.

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### تحميل وإلغاء تحميل PJSIP

PJSIP هو القناة الوحيدة لـ SIP في Asterisk 22، ويتم تحميل وحداته بشكل افتراضي. في حالات نادرة قد ترغب في التحكم بتحميل الوحدات من ملف modules.conf — على سبيل المثال، لتعطيل PJSIP على خادم يستخدم فقط IAX2 أو DAHDI.

#### لتعطيل PJSIP

حرّر ملف modules.conf وأضف السطور التالية.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### أوامر وحدة التحكم

الآن بعد أن قمت بتكوين نقاط النهاية PJSIP الخاصة بك، حان الوقت لمعرفة كيفية فحص تكوينك. هناك العديد من أوامر وحدة التحكم التي تساعدك في هذه المهمة. بعد تعديل pjsip.conf، أعد تحميل التكوين باستخدام:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

This command lists the configured Address of Record objects and their contacts, so you can confirm where Asterisk will send calls for each endpoint.

#### pjsip show registrations

The command below shows the registrations made by our own server.

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

The command list is a little friendlier and show less data, but better structured. Listing endpoints:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

Listing contacts:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

The most useful troubleshooting command is the SIP packet logger. It prints every SIP request and reply to the console as it is sent or received, which is invaluable when diagnosing registration and call setup problems.

```
pjsip set logger on
pjsip set logger off
```

يمكنك أيضًا تقييد التسجيل إلى مضيف واحد باستخدام `pjsip set logger host <ip>`.

#### pjsip set history on

إضافة رائعة إلى PJSIP هي مفهوم السجل. يمكنك التقاط وتحليل طلبات SIP والردود عليها في الوقت الحقيقي بطريقة سهلة. لبدء السجل استخدم الأمر أدناه.

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

الآن يمكنك عرض السجل:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

ثم لرؤية طلب أو رد محدد، اعرض عنصر السجل:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

سهل جدًا، أليس كذلك؟ يمكنك أيضًا مسح السجل في أي وقت باستخدام `pjsip set history clear`.

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Summary

SIP هو بروتوكول الإشارة الخاص بـ IETF الذي يُنشئ، يُعدِّل، ويُنهِي جلسات الوسائط. وكلاء المستخدمين، الوكلاء، مسجِّل التسجيل، والبوابات يتبادلون رسائل نصية — REGISTER، INVITE، الردود الأولية والنهائية، ACK، و BYE — بينما يتفاوض SDP على الترميزات و RTP ينقل الوسائط. هذه النظرية البروتوكولية خالدة وتُطبق على أي تنفيذ لـ SIP.

في Asterisk 22 تتحدث SIP عبر **PJSIP** (`chan_pjsip`)، مُكوَّن في `pjsip.conf`. بدلاً من نظير موحد واحد، يُنمذج الجهاز كمجموعة من الكائنات الصغيرة ذات الإشارة المتبادلة: `endpoint` (سلوك المكالمة والترميزات)، `auth` (بيانات الاعتماد)، `aor` (مكان الوصول إليه)، و`transport` (المستمع)، بالإضافة إلى `identify` (مطابقة خط النقل حسب IP) و`registration` (تسجيل صادر) لمزودي الخدمة. رأيت كيف تتناسق هذه الكائنات معًا، وكيف تُكوّن كلًا من الهواتف وخطوط النقل، وكيف تحل خيارات عبور NAT (`force_rport`، `rewrite_contact`، `rtp_symmetric`، `direct_media`، و`external_*`/`local_net` الخاصة بالنقل) مشكلات النشر في العالم الحقيقي، وكيفية فحص كل ذلك باستخدام `pjsip show endpoints`، `aors`، `contacts`، و`registrations`.

## Quiz

1. في بنية SIP، أي مكوّن يستقبل طلبًا ويجيب عليه برد توجيه (مثل `302 Moved Temporarily`) يحمل الموقع الجديد، ثم يخرج من مسار الرسائل اللاحقة؟
   - A. خادم الوكيل
   - B. خادم التوجيه
   - C. خادم الموقع
   - D. مسجل التسجيل

2. ما الدور الذي يلعبه Asterisk عندما يتعامل مع مكالمة SIP بين هاتفين؟
   - A. وكيل SIP يبقى فقط في مسار الإشارة
   - B. خادم توجيه SIP
   - C. وكيل مستخدم خلفي (B2BUA) يربط قناتين SIP
   - D. موازن تحميل SIP عديم الحالة

3. أي طريقة SIP يستخدمها الهاتف لإبلاغ المسجل بعنوان IP الحالي حتى يتمكن من تلقي المكالمات لاحقًا؟
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. صواب أم خطأ: في Asterisk 22، لا يزال `chan_sip` و`sip.conf` متاحين كخيار قديم إلى جانب PJSIP.

5. أي كائنات تكوين يجب ربطها بنقطة النهاية حتى يعرف Asterisk مقبس الاستماع الذي سيستخدمه وإلى أين يرسل المكالمات لهذا الجهاز؟ (اختر كل ما ينطبق.)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. في كائن PJSIP `aor`، أي إعداد يبقي خريطة NAT مفتوحة عن طريق تأهيل الاتصال دوريًا، وما هي وحدته؟
   - A. `qualify=yes` (منطقي)
   - B. `qualify_frequency` (ثوانٍ)
   - C. `rtp_timeout` (مللي ثانية)
   - D. `nat=force_rport`

7. املأ الفراغ: لجعل Asterisk يطابق طلب SIP وارد إلى نقطة نهاية محددة حسب عنوان IP المصدر (بدلاً من رأس `From`)، تنشئ قسمًا بـ `type=________`.

8. أي كائن PJSIP يُستخدم لتكوين **تسجيل صادر** من Asterisk إلى موفر trunk SIP؟
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. على سطر أوامر Asterisk 22 CLI، أي أمر يفعّل مسجل حزم SIP الذي يطبع كل طلب ورد SIP إلى وحدة التحكم؟
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. على نقطة نهاية PJSIP تخدم هاتفًا خلف NAT متماثل، أي زوج من الإعدادات يجعل Asterisk يرد على عنوان المصدر للطلب (RFC 3581) ويرسل الوسائط إلى المكان الذي يصل منه RTP فعليًا؟
    - A. `direct_media=yes` و`srvlookup=yes`
    - B. `force_rport=yes` و`rtp_symmetric=yes`
    - C. `allowguest=yes` و`insecure=invite`
    - D. `qualify=yes` و`nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
