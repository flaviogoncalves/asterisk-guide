# تصميم شبكة VoIP

الصوت عبر بروتوكول الإنترنت ينمو بسرعة في سوق الاتصالات. نموذج التلاقي يغيّر طريقة تواصلنا، ويقلل التكاليف ويعزز طريقة تبادل المعلومات. الصوت هو مجرد بداية لعصر التواصل المتعدد الوسائط الكامل، الذي يشمل الصوت والفيديو والحضور. في المستقبل، لن ننقل الناس إلى العمل، بل سننقل العمل إلى الناس لأنه أنظف وأسرع وأرخص. الـ VoIP هو مجرد جزء من هذه الثورة. التحدي في هذا الفصل هو تصميم شبكة VoIP. للقيام بذلك، سيتعين علينا فهم مفاهيم مثل بروتوكولات الجلسة والترميزات بالإضافة إلى كيفية تحديد عدد الدوائر وعرض النطاق الترددي.

## الأهداف

- فهم فوائد VoIP
- وصف كيفية تعامل Asterisk مع VoIP
- وصف مفاهيم قنوات SIP و IAX
- اختيار البروتوكول الأنسب لقناة بيانات محددة
- اختيار الترميز الأنسب لقناة بيانات محددة
- تحديد عدد القنوات المطلوبة
- حساب عرض النطاق الترددي المطلوب

## فوائد VoIP

لماذا قد تهتم بـ VoIP؟ يوفر VoIP فوائد لكل من الشركات والأفراد. تقليل التكلفة هو بالتأكيد أحدها، ولكن في بعض البيئات يبسط VoIP دمج أنظمة الحاسوب. يتم تفصيل عدة من هذه الفوائد هنا:

### التلاقي

الفائدة الأساسية لـ VoIP هي الجمع بين شبكات البيانات والصوت لتقليل التكاليف (التلاقي). ومع ذلك، قد لا يكون تحليل تكلفة دقائق الصوت وحدها كافياً لتبرير اعتماد VoIP. سعر الدقائق التي تبيعها شركات الهاتف يصبح أرخص بسرعة وهو أمر يجب مراعاته قبل اعتماد VoIP.

### تكاليف البنية التحتية

استخدام بنية تحتية شبكة واحدة يقلل من التكاليف المرتبطة بالإضافات والإزالة والتغييرات. ومع انتشار IP، جلب تكنولوجيا VoIP إلى عدة أجهزة جديدة، مثل الهواتف المحمولة، وأجهزة PDA، والأنظمة المدمجة، وأجهزة الكمبيوتر المحمولة.

### المعايير المفتوحة

أخيراً، المعايير المفتوحة التي بُني عليها VoIP توفر الحرية في الاختيار بين مختلف البائعين. هذه الفائدة الوحيدة تجعل العميل هو الملك بدلاً من أن يكون تابعاً لشركات الاتصالات ومصنعي PBX.

### دمج الحاسوب والاتصالات

الاتصالات أقدم بكثير من الحوسبة. أنظمة PBX للاتصالات تعتمد على التحويل الدائري، وعادةً لا يكون لديك أكثر من حاسوب للمراقبة. مع VoIP، تُبنى الاتصالات من الأساس بناءً على معايير الحاسوب. هذا يجعل استخدام تطبيقات دمج الحاسوب والاتصالات أرخص وأسهل مقارنة بالنموذج القديم. يمكنك بسرعة إنشاء قائمة طويلة من تطبيقات الاتصالات بناءً على Asterisk. يمكنك تطوير IVRs، وACDs، وCTI، ومُنادي الاتصال، والنوافذ المنبثقة، وتطبيقات أخرى في جزء صغير من الوقت المطلوب لأنظمة PBX التقليدية.

## بنية Asterisk VoIP

تُظهر البنية أدناه. يتعامل Asterisk مع جميع بروتوكولات VoIP كقنوات. يمكنك استخدام أي codec أو أي بروتوكول. المفهوم الذي يجب تعلمه هنا هو أن Asterisk يربط أي نوع من القنوات بأي قناة أخرى. وبالتالي، يمكنك ترجمة بروتوكولات الإشارة مثل SIP و IAX إلى بعضها البعض وحتى مع codecs مختلفة. على سبيل المثال، يمكنك ترجمة مكالمة من هاتف SIP في الشبكة المحلية باستخدام codec G.711 إلى قناة SIP لمزود VoIP الخاص بك باستخدام codec G.729. في الفصول التالية، سنشرح تفاصيل بنية SIP و IAX. دعم H.323 (عبر الإضافة chan_ooh323) متاح لكنه نادر بشكل متزايد؛ SIP/PJSIP هو المعيار للنشر الحديث.

![Asterisk's modular architecture: applications and channels connect to the PBX switch core through APIs, with codec translation and file-format modules loaded dynamically.](../images/06-voip-network-fig01.png)

## بروتوكولات VoIP وطبقة الشبكة

يستخدم VoIP مجموعة من البروتوكولات المختلفة التي تعمل معًا. من السهل أن نرتبها
مقابل نموذج OSI المرجعي المكوّن من سبع طبقات، والعديد من المخططات القديمة تفعل ذلك
بالضبط — حيث توضع SIP و H.323 في طبقة "الجلسة" وتوضع الترميزات في طبقة
"العرض". كان هذا التعيين دائمًا موضع جدل. لا يستخدم IETF، الذي يحدد معيار SIP،
نموذج OSI؛ بل يتبع نموذج TCP/IP (DoD) القديم المكوّن من أربع طبقات، ويعرّف RFC 3261
**SIP كبروتوكول طبقة تطبيق**. تتبع الوسائط نفس النمط: RTP والترميزات تعيش في حمولة
التطبيق، تُنقل عبر UDP في طبقة النقل. يربط الجدول أدناه بروتوكولات VoIP الرئيسية
مع نموذج TCP/IP الذي يستخدمه IETF فعليًا، مع إظهار ما يعادلها تقريبًا في OSI فقط
للتوضيح.

| طبقة TCP/IP (IETF) | البروتوكولات | ما يعادلها تقريبًا في OSI |
|---|---|---|
| التطبيق | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | التطبيق / العرض / الجلسة |
| النقل | UDP, TCP | النقل |
| الإنترنت | IP (مع QoS مثل DiffServ) | الشبكة |
| الرابط | Ethernet, PPP, Frame Relay… | ربط البيانات / الفيزيائية |

آليات QoS مثل DiffServ تعمل في طبقة IP لتحديد أولوية حزم الصوت
وتحسين جودة المكالمة. بعض التفاصيل الخاصة بالبروتوكولات:

- **SIP** يستخدم UDP أو TCP على المنفذ 5060 (TLS على 5061) لنقل الإشارة. يتم نقل الصوت
  بشكل منفصل عبر RTP على نطاق منافذ UDP قابل للتكوين (العينة المرفقة مع Asterisk
  `rtp.conf` تستخدم من 10000 إلى 20000)، مُشفَّر بترميز مثل G.711.
- **H.323** ينقل إشارة المكالمة عبر TCP (إشارة مكالمة H.225 على المنفذ 1720)، بينما
  يستخدم قناة H.225 RAS UDP على المنفذ 1719؛ ينقل RTP الصوت.
- **IAX2** غير معتاد: يجمع بين الإشارة والوسائط عبر منفذ UDP واحد
  (4569)، مما يبسط عبور NAT والجدران النارية.


## كيف تختار بروتوكولًا

نظرًا لتعدد البروتوكولات، كيف يمكنك اختيار الأنسب لشبكتك؟ في هذا القسم، سنسلط الضوء على مزايا وعيوب كل بروتوكول.

### SIP - Session Initiated Protocol

SIP هو معيار مفتوح من Internet Engineering Task Force (IETF)، معرّف إلى حد كبير في RFC 3261. معظم مزودي VoIP الحديثين يستخدمون SIP؛ في الواقع، أصبح هو المعيار الأكثر شعبية في VoIP. قوة SIP تكمن في كونه معيارًا قائمًا على IETF. SIP خفيف مقارنةً بـ H.323 القديم. الضعف الرئيسي لـ SIP هو عبور NAT — وهو تحدٍ لمعظم مزودي VoIP الذين يستخدمون SIP. لم تُنشئ IETF SIP مع مراعاة الفوترة، بل للاتصالات المفتوحة بين النظائر. عادةً ما تكون الفوترة مصدر قلق لمزودي VoIP.

### IAX – Inter Asterisk eXchange

IAX هو بروتوكول مفتوح تم تطويره أصلاً بواسطة Digium (الآن Sangoma). IAX هو بروتوكول شامل لأنه ينقل الإشارة والوسائط عبر نفس منفذ UDP (4569). طور مارك سبنسر IAX كبروتوكول ثنائي لتقليل استهلاك النطاق الترددي. القوة الرئيسية لـ IAX هي تقليل استهلاك النطاق الترددي (لا يستخدم RTP)؛ كما أنه سهل جدًا لعبور NAT والجدار الناري لأنه يستخدم منفذ UDP واحد فقط (4569).

لو أن مصنع PBX تقليديًا كان قد أنشأ IAX، لكان ربما روج للبروتوكول باعتباره "أفضل شيء منذ الآيس كريم"؛ في بعض الحالات، يمكن أن يقلل IAX في وضع trunk من استهلاك النطاق الصوتي إلى الثلث. لا يزال IAX2 (الإصدار 2) موجودًا في Asterisk 22 عبر وحدة `chan_iax2` ويظل مفيدًا لخطوط trunk بين Asterisk وAsterisk، رغم أنه يُعتبر قديمًا؛ يُفضَّل SIP/PJSIP للنشر الجديد. تم تحديد IAX2 في [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP هو بروتوكول يُستخدم بالاشتراك مع H.323 وSIP وIAX. أكبر ميزة له هي القابلية للتوسع. يتم تكوينه في وكيل المكالمات بدلاً من البوابات. هذا يبسط عملية التكوين ويسمح بالإدارة المركزية. ومع ذلك، تنفيذ Asterisk غير كامل، ويبدو أن عددًا قليلًا من الأشخاص يستخدمونه.

### H.323

H.323 يُستخدم إلى حد كبير في VoIP. هو أحد أولى بروتوكولات VoIP وهو أساسي لربط البُنى التحتية القديمة القائمة على البوابات. لا يزال H.323 هو المعيار في سوق البوابات، رغم أن السوق ينتقل ببطء إلى SIP. تشمل نقاط قوة H.323 الانتشار الواسع في السوق والنضج. أما نقاط ضعفه فترتبط بتعقيد التنفيذ وتكاليف الهيئات المعيارية المرتبطة.

### جدول مقارنة البروتوكولات

الجدول التالي يلخص الفروقات بين بروتوكولات الجلسة.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## One endpoint per device

في Asterisk 22 يُنمذج مكدس PJSIP كل هاتف أو خط أو بوابة ككائن **endpoint** واحد في `pjsip.conf`. يقوم endpoint واحد كل من وضع المكالمات واستقبالها؛ بيانات الاعتماد الخاصة به تعيش في كائن `auth`، وعنوانه المسجل في `aor`، ومسار شبكته في `transport`. تقوم بتكوين endpoint واحد لكل جهاز وتربط الأجزاء التي يحتاجها — لا يوجد دور منفصل “user” مقابل “peer” للتفكير فيه. (النموذج الكامل للكائنات مغطى في *SIP & PJSIP in depth*.)

## Codecs and codec translation

ستستخدم **codec** لتحويل الصوت من موجة تماثلية إلى إشارة رقمية. تختلف الـ codecs عن بعضها في جوانب مثل جودة الصوت، معدل الضغط، عرض النطاق الترددي، ومتطلبات الحوسبة. عادةً ما تدعم الخدمات والهواتف والبوابات عدة من هذه الجوانب. الـ codec G.729 شائع جداً. وهو ليس جزءاً من بناء Asterisk 22 القياسي؛ بل يُوزَّع كإضافة خارجية (`codec_g729`) يمكنك تحميلها من Digium (الآن Sangoma). تُدرج مصدر `menuselect` الخاص بـ Asterisk ذلك مع `support_level=external` وتذكر بوضوح: "Download the g729a codec from Digium. A license must be purchased for this codec." بعبارة أخرى، استخدام G.729 قانونياً يتطلب رخصة تُشترى لكل قناة. (هناك بديل مفتوح المصدر، `bcg729`، موجود أيضاً.)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

يدعم Asterisk 22 الـ codecs التالية (among others):

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — جودة PSTN قياسية؛ ulaw شائع في أمريكا الشمالية، alaw شائع في أوروبا وأمريكا اللاتينية
- ITU G.722: 64 Kbps — نطاق واسع (HD voice)، جودة جيدة بنفس عرض النطاق الترددي لـ G.711
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — وحدة ثنائية خارجية `codec_g729` تم تحميلها من Digium/Sangoma (`support_level=external`؛ يجب شراء رخصة لاستخدامها)
- Speex: 2.15 to 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, variable — codec حديث نطاق واسع/كامل النطاق؛ جودة ممتازة ومقاومة لفقدان الحزم؛ يُوفر كوحدة ثنائية خارجية `codec_opus` تم تحميلها من Digium/Sangoma (`support_level=external`؛ لا توجد إشارة إلى شراء رخصة، على عكس G.729)؛ يُنصح به لـ WebRTC و endpoints SIP الحديثة. (توجد بدائل بناء مفتوحة المصدر على GitHub.)

بالإضافة إلى ذلك، يسمح Asterisk بترجمة بين الـ codecs. في بعض الحالات، هذا غير ممكن، مثل حالة g723 التي تُدعم فقط في وضع pass‑thru. ترجمة codec إلى آخر تستهلك موارد كثيرة من الـ CPU. لذا، تجنّب ذلك تماماً كلما أمكن.

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## الحمل الزائد الناتج عن رؤوس البروتوكول

على الرغم من أن الترميزات (codecs) تستهلك القليل من النطاق الترددي، يجب أن نأخذ في الاعتبار الحمل الزائد الناتج عن رؤوس البروتوكول مثل Ethernet و IP و UDP و RTP. وبالتالي، النطاق الترددي المستهلك فعليًا يعتمد على الرؤوس المستخدمة. في شبكة Ethernet يكون المتطلب أعلى مقارنةً بشبكة PPP، لأن رأس PPP أقصر من رأس Ethernet. حزمة صوتية واحدة بتقنية G.729، على سبيل المثال، تحمل 20 بايت فقط من الحمولة ولكنها ملفوفة بحوالي 58 بايت من رؤوس Ethernet و IP و UDP و RTP — لذا فإن الرؤوس، وليس الترميز، هي التي تهيمن على النطاق الترددي (انظر الشكل أدناه).

![A single g.729 voice packet on Ethernet: 20 bytes of payload wrapped in 58 bytes of Ethernet, IP, UDP, and RTP headers — a g.729 conversation consumes 31.2 Kbps.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

ترميز G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

يمكنك بسهولة حساب متطلبات النطاق الترددي الأخرى باستخدام حاسبة النطاق الترددي للـ VoIP على الإنترنت مثل <https://www.voip.school/bandcalc/bandcalc.php>.


## هندسة المرور

مسألة رئيسية في تصميم شبكات VoIP هي تحديد عدد الخطوط وعرض النطاق الترددي المطلوب إلى وجهة معينة، مثل مكتب بعيد أو مزود خدمة. كما أنه من المهم تحديد عدد المكالمات المتزامنة في Asterisk (المعامل الرئيسي لتحديد أبعاد Asterisk).

### تبسيطات

التبسيط الأساسي والأكثر استخدامًا هو تقدير عدد المكالمات حسب نوع المستخدم. على سبيل المثال:

- أنظمة PBX التجارية (مكالمة متزامنة واحدة لكل خمس امتدادات)
- المستخدمون السكنيون (مكالمة متزامنة واحدة لكل ستة عشر مستخدمًا)

مثال #1 المقر الرئيسي للشركة يحتوي على 120 امتدادًا وفرعين—الأول به 30 امتدادًا والثاني به 15 امتدادًا. هدفنا هو تحديد عدد خطوط E1 في المقر الرئيسي وعرض النطاق الترددي المطلوب لشبكة Frame‑Relay.

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a عدد خطوط T1

- إجمالي عدد الامتدادات التي تستخدم خطوط T1: 120+30+15=165 خطًا
- استخدام خط واحد لكل خمس امتدادات للاستخدام التجاري
- إجمالي عدد الخطوط = 33 أو تقريبًا 2×T1 خطوط

1b متطلبات عرض النطاق الترددي نختار ترميز g.729 بسبب متطلبات عرض النطاق الترددي، جودة الصوت، واستهلاك CPU المتوسط.

مع خط واحد لكل خمس امتدادات:

- عرض النطاق الترددي المطلوب للفرع #1 (Frame‑relay): 26.8×6=160.8 Kbps
- عرض النطاق الترددي المطلوب للفرع #2 (Frame‑relay): 26.8×3= 80.4 Kbps

### طريقة Erlang B

عندما تتوفر بيانات تاريخية، يمكنك تحديد حجم الخط بصورة علمية بدلاً من التبسيط. سنستخدم عمل Agner Karup Erlang (شركة Copenhagen Telephone، 1909)، الذي وضع صيغة لحساب عدد الخطوط في مجموعة خطوط بين مدينتين.

**Erlang** هو وحدة قياس للمرور شائعة في الاتصالات؛ تصف حجم المرور خلال ساعة واحدة. على سبيل المثال، إذا حدثت 20 مكالمة في ساعة، بمتوسط 5 دقائق لكل مكالمة:

- دقائق المرور في الساعة: 20 × 5 = 100 دقيقة
- ساعات المرور داخل الساعة: 100 ÷ 60 = **1.66 Erlangs**

يمكنك استخراج هذه القياسات من سجل المكالمات واستخدامها لتصميم شبكتك وحساب عدد الخطوط المطلوبة. بمجرد معرفة عدد الخطوط، يمكنك حساب متطلبات عرض النطاق الترددي.

**Erlang B** هي الطريقة الأكثر شيوعًا لحساب عدد الخطوط في مجموعة خطوط. تفترض أن المكالمات تصل عشوائيًا (توزيع بواسون) وأن المكالمات المحجوبة تُلغى فورًا. تتطلب معرفة **Busy Hour Traffic (BHT)**، والتي يمكنك الحصول عليها من سجل المكالمات أو تقديرها كتبسيط: BHT = 17% من دقائق المكالمات في يوم واحد.

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

متغير مهم آخر هو Grade of Service (GoS)، الذي يحدد احتمال حجب المكالمات بسبب نقص الخطوط. يمكنك تعديل هذا المتغير، والذي يكون عادةً 0.05 (فقدان 5% من المكالمات) أو 0.01 (فقدان 1% من المكالمات). مثال #1: باستخدام مثال المقر الرئيسي والفرعين المذكورين سابقًا في هذا القسم، سنزودك ببعض البيانات حول أنماط المرور. من سجل المكالمات، اكتشفنا هذه البيانات: بيانات من سجل المكالمات (دقائق المكالمات وBHT):

- المقر الرئيسي إلى الفرع #1 = 2,000 دقيقة، BHT = 300 دقيقة
- المقر الرئيسي إلى الفرع #2 = 1,000 دقيقة، BHT = 170 دقيقة
- الفرع #1 إلى الفرع #

## تقليل النطاق الترددي المطلوب للـ VoIP

يمكن استخدام ثلاث طرق لتقليل النطاق الترددي المطلوب لمكالمات الـ VoIP:

- ضغط رأس RTP
- IAX Trunked
- حمولة الـ VoIP

### ضغط رأس RTP

في شبكات Frame-Relay و PPP، يمكنك استخدام ضغط رأس RTP. تم تعريف ضغط رأس RTP في RFC 2508. وهو معيار IETF متوفر في عدة راوترات. ومع ذلك، كن حذرًا، فبعض الراوترات تتطلب مجموعة ميزات مختلفة لكي يكون هذا المورد متاحًا. تأثير استخدام ضغط رأس RTP رائع حيث يقلل النطاق الترددي المطلوب في مثالنا من 26.8 Kbps لكل محادثة صوتية إلى 11.2 Kbps — انخفاض بنسبة 58.2%!

### وضع trunk لـ IAX2

إذا كنت تقوم بربط خادمين Asterisk، يمكنك استخدام بروتوكول IAX2 في وضع trunk. هذه التقنية الثورية لا تحتاج إلى أي راوترات خاصة ويمكن تطبيقها على أي نوع من روابط البيانات.

![وضع trunk لـ IAX2 على Ethernet: مكالمة واحدة g.729 تحتاج إلى كامل مكدس الرأس (31.2 Kbps)، لكن المكالمة الثانية تشارك تلك الرؤوس وتضيف فقط إطارًا صغيرًا من IAX2، بمتوسط حوالي 9.6 Kbps من النطاق الترددي الإضافي لكل مكالمة إضافية.](../images/06-voip-network-fig08.png)

يعيد وضع trunk لـ IAX2 استخدام نفس الرؤوس من المكالمة الثانية وما بعدها. باستخدام g729 في رابط PPP، ستستهلك المكالمة الأولى 30 Kbps من النطاق الترددي، بينما ستستخدم المكالمة الثانية نفس الرأس كما في الأولى وتقلل النطاق الترددي اللازم للمكالمة الإضافية إلى 9.6 Kbps. يمكننا حساب النطاق الترددي المطلوب في وضع trunk كما يلي: الفرع #1 (11 مكالمة) النطاق الترددي = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps الفرع #2 (8 مكالمات) النطاق الترددي = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps المكالمة الأولى تستخدم 31.2 Kbps، التالية 9.6، وهكذا.

### زيادة حمولة الصوت

هذه الطريقة شائعة جدًا عند استخدام بوابات VoIP عبر الإنترنت. عند استخدام حمولة أكبر، ستضحي بالكمون لصالح تقليل النطاق الترددي. يمكنك تغيير تجزئة حزم RTP بإضافة حجم الإطار إلى الـ codec في تعليمة allow.

![زيادة حمولة الصوت: تعبئة 60 بايت من حمولة g.729 في حزمة واحدة (بدلاً من 20) توزع 58 بايت من الرؤوس على صوت أكثر، مما يخفض النطاق الترددي إلى حوالي 16.05 Kbps لكل مكالمة على حساب زيادة الكمون.](../images/06-voip-network-fig09.png)

مثال:

```
allow=ulaw:30
```

الرقم بعد النقطتين هو فترة التجزئة بالمللي ثانية — مقدار الصوت المنقول في كل حزمة RTP. قيمة أكبر توزع عبء الرأس الثابت على صوت أكثر (نطاق ترددي أقل) على حساب زيادة الكمون. لكل codec حدوده الدنيا والقصوى والحجم الافتراضي للإطار؛ G.711 (`ulaw`/`alaw`)، على سبيل المثال، يحدد افتراضيًا 20 ms.

## Summary

في هذا الفصل، تعلمت أن Asterisk يتعامل مع VoIP باستخدام القنوات. يدعم SIP (via `chan_pjsip` في Asterisk 22) و IAX2؛ بروتوكول H.323 متاح فقط من خلال الإضافة المجتمعية `ooh323`، والقنوات القديمة MGCP و SCCP (Skinny) لم تعد جزءًا من بناء Asterisk 22 القياسي. قمت بالمقارنة وتعلمت كيفية اختيار بروتوكول الإشارة وcodec لقنوات VoIP. الـ IAX2 أكثر كفاءة في استهلاك النطاق الترددي ويمكنه عبور NAT بسهولة. SIP/PJSIP هو البروتوكول الأكثر دعمًا من قبل بائعين الهواتف والبوايب الخارجية الطرف الثالث وهو القناة الوحيدة لـ SIP في Asterisk 22. بروتوكول H.323 هو الأقدم ويجب استخدامه للاتصال بالبنى التحتية legacy لـ VoIP. في قسم هندسة المرور، تعلمنا كيفية تصميم وتحديد أبعاد شبكة VoIP.

## Quiz

1. أي من التالي هو من فوائد VoIP الموضحة في هذا الفصل (اختر كل ما ينطبق)؟
   - A. دمج شبكات البيانات والصوت لتقليل التكلفة
   - B. انخفاض تكلفة البنية التحتية للإضافات والإزالة والتغييرات
   - C. معايير مفتوحة تحرّكك من الاعتماد على بائع واحد
   - D. تكامل الحاسوب والاتصالات (CTI) أسهل وأرخص
   - E. ضمان معدلات اتصال دقيقة أقل من أي شركة هاتفية
2. الدمج هو دمج الصوت والبيانات والفيديو في شبكة واحدة؛ فائدته الأساسية هي تقليل التكلفة في تنفيذ وصيانة الشبكات المنفصلة.
   - A. False
   - B. True
3. يعامل Asterisk كل بروتوكول VoIP كقناة ويمكنه ربط أي نوع قناة بأي أخرى، مع تحويل الترميز بين codecs عند الحاجة.
   - A. False
   - B. True
4. في Asterisk 22، أي برنامج تشغيل قناة يتعامل مع SIP؟
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. في نموذج TCP/IP (IETF) الذي يُعرّف فيه SIP في RFC 3261، تعمل بروتوكولات الإشارة SIP و H.323 و IAX2 في طبقة ___.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP هو البروتوكول الأكثر اعتمادًا للهواتف IP وهو معيار مفتوح يُعرّف إلى حد كبير من قبل IETF في RFC 3261.
   - A. False
   - B. True
7. ينقل IAX2 كلًا من الإشارة والوسائط عبر منفذ UDP واحد، مما يجعله فعالًا وسهل عبور NAT. أي منفذ UDP يستخدمه IAX2؟
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. تم تطوير IAX أصلاً بواسطة Digium (الآن Sangoma). على الرغم من اعتماد محدود من قبل بائعي الهواتف، فإن IAX ممتاز عندما تحتاج (اختر كل ما ينطبق):
   - A. لتقليل استهلاك النطاق الترددي (لا يستخدم RTP)
   - B. تنسيق وسائط فيديو
   - C. عبور NAT والجدار الناري بسهولة
   - D. وضع Trunk لدمج العديد من مكالمات Asterisk‑to‑Asterisk وتقليل عبء رؤوس الحزم
9. في Asterisk 22، يُكوَّن الجهاز ككائن PJSIP `endpoint` واحد يضع ويتلقى المكالمات — لا يوجد دور "مستخدم" أو "نظير" منفصل.
   - A. False
   - B. True
10. بخصوص codecs في Asterisk 22، اختر كل العبارات الصحيحة:
    - A. G.711 يعادل PCM ويستخدم 64 كيلوبت في الثانية من النطاق الترددي.
    - B. وحدة Sangoma codec_g729 مجانية للتحميل، لكن الاستخدام القانوني يتطلب ترخيصًا لكل قناة يتم شراؤه.
    - C. GSM شائع لأنه يستخدم حوالي 13 كيلوبت في الثانية ولا يحتاج إلى ترخيص.
    - D. G.711 u‑law شائع في أمريكا الشمالية، بينما a‑law شائع في أوروبا وأمريكا اللاتينية.
    - E. G.729 خفيف ويستهلك موارد CPU قليلة جدًا للتشفير وفك التشفير مقارنةً بـ G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
