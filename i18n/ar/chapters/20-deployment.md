# Deployment, monitoring & scaling

Getting Asterisk to answer a call in a lab is one thing; running it as a service
that survives crashes, reboots, upgrades and attackers — and that you can observe,
back up and grow — is another. This chapter is about everything that happens *after*
the dialplan works. We start with the supervisor that keeps Asterisk alive
(systemd), move to packaging it in a container (using the book's own Docker lab as
the worked example), then cover configuration management and backups, monitoring and
observability, and finally the patterns you reach for when one server is not enough:
high availability and scaling, and the realities of hosting in the cloud.

Everything shown is verified against the book's Asterisk 22 lab in `lab/` — the same
container you have been building on throughout the book.

## Objectives

By the end of this chapter, you should be able to:

- Run Asterisk 22 reliably under systemd, as a non-root user, with automatic restart
- Containerize Asterisk with Docker and understand the networking trade-offs
- Keep `/etc/asterisk` in version control and back up the right state
- Monitor a running system through the CLI, CDR/CEL, AMI/ARI and metrics
- Apply active/standby high availability and horizontal scaling patterns
- Host Asterisk in the cloud safely behind NAT and a firewall

## تشغيل Asterisk تحت systemd

في كل توزيعة لينكس حديثة — Debian 12، Ubuntu 22.04/24.04، Rocky/AlmaLinux 9 — مدير الخدمات هو **systemd**. أظهر فصل التثبيت أن خطوة `make config` (تُنفّذ أثناء `make install`) تثبت سكريبت بدء تشغيل التوزيعة (`/etc/init.d/asterisk` على Debian، سكريبت `rc.d` على RedHat)، والذي يقوم systemd بعد ذلك بلفه تلقائيًا كخدمة؛ كما يُوفر Asterisk وحدة systemd أصلية تحت `contrib/systemd/asterisk.service` يمكنك تثبيتها بدلاً منها للتحكم الدقيق.
في كلتا الحالتين، systemd هو الطريقة المدعومة والإنتاجية لتشغيل Asterisk. راجع *Installing Asterisk 22* للبناء نفسه؛ هنا نركز على ما تقدمه الخدمة وكيفية تشغيلها.

### وحدة الخدمة ودورة حياتها

بمجرد أن يقوم `make config` بتثبيت الخدمة، تكون دورة الحياة نظامية في systemd:

```
systemctl enable asterisk     # start automatically at boot
systemctl start asterisk      # start now
systemctl status asterisk     # is it running? recent log lines
systemctl restart asterisk    # full stop + start
systemctl stop asterisk       # stop
journalctl -u asterisk        # service logs via the journal
```

بعض الملاحظات التشغيلية:

- **`restart` مقابل إعادة التحميل السلس.** يقوم `systemctl restart` بإنهاء العملية وإسقاط كل المكالمات. بالنسبة لتغييرات الإعدادات نادراً ما تريد ذلك — استخدم سطر أوامر Asterisk بدلاً من ذلك: `asterisk -rx 'core reload'` (أو إعادة تحميل خاصة بوحدة مثل `pjsip reload`). احجز `systemctl restart` للتحديثات أو عملية عالقة.
- **الاتصال بالعميل الشغال.** مع تشغيل Asterisk كخدمة، افتح وحدة التحكم الخاصة به باستخدام `asterisk -r` (أو `asterisk -rvvv` للإخراج المفصل). هذا يتصل بالعميل الشغال بالفعل عبر مقبس التحكم؛ لا يبدأ نسخة ثانية.

### `Restart=` يحل محل safe_asterisk

تاريخيًا كان يتم إطلاق Asterisk عبر غلاف **safe_asterisk**، وهو سكريبت شل يعيد تشغيل Asterisk إذا تعطل. تحت systemd تُنسب هذه المهمة إلى توجيه الوحدة `Restart=` — يلاحظ systemd خروج العملية ويعيد تشغيلها، مع تأخير يتحكم به `RestartSec=` وحماية من حلقة الانهيار بواسطة `StartLimitIntervalSec=`/`StartLimitBurst=`. لذا على نظام يعمل بـ systemd يصبح **safe_asterisk** **مستبدلاً** وعادةً غير ضروري. إذا لم تقم الوحدة المرفقة بتعيينه مسبقًا، فإن إضافة تجاوز (drop‑in) هي الطريقة النظيفة لإضافة إعادة تشغيل عند الفشل دون تعديل الملف المعبأ:

```
# /etc/systemd/system/asterisk.service.d/override.conf
[Service]
Restart=always
RestartSec=2
```

طبّق ذلك باستخدام `systemctl daemon-reload && systemctl restart asterisk`. استخدام تجاوز (بدلاً من تعديل الوحدة المثبتة) يعني أن تحديثًا مستقبليًا `make config` لن يطيح بتغييراتك.

### التشغيل كمستخدم غير جذري

لا ينبغي تشغيل Asterisk كجذر في بيئة الإنتاج — خطأ برمجي عن بُعد في عملية تعمل كجذر يعني اختراق كامل للمضيف، بينما نفس الخطأ في عملية غير مميزة يبقى محصورًا. هناك مكانان تكميليان يفرضان ذلك:

- **الوحدة / asterisk.conf.** عادةً ما تشغل الوحدة المعبأة Asterisk كمستخدم ومجموعة `asterisk`. يمكنك أيضًا (أو بدلاً من ذلك) تعيين `runuser` و`rungroup` في قسم `[options]` من `asterisk.conf`، الذي يلتزم به العميل عندما يزيل الصلاحيات بعد الربط:

  ```
  [options]
  runuser = asterisk
  rungroup = asterisk
  ```

- **ملكية الملفات.** يجب أن تكون الأدلة التشغيلية قابلة للكتابة بواسطة ذلك المستخدم. بعد إنشاء الحساب، تأكد من الملكية:

  ```
  chown -R asterisk:asterisk /var/lib/asterisk /var/log/asterisk \
        /var/spool/asterisk /var/run/asterisk /etc/asterisk
  ```

نظرًا لأن SIP (5060) وRTP (10000+) كلها منافذ عالية، لا يحتاج Asterisk إلى الجذر للربط بها — فقط المنافذ ذات الأسبقيات من نوع port‑25 تحتاج ذلك، وهو ما لا يستخدمه Asterisk. لذا فإن التشغيل غير مميز مجاني. (يفصل فصل الأمان لماذا هذا مهم؛ انظر *Asterisk Security*.)

## Containerizing Asterisk

حاوية تُعبئ Asterisk واعتمادياتها الدقيقة في صورة واحدة غير قابلة للتغيير، بحيث يكون ما تختبره هو نفسه بالضبط ما تُوزّعه. المقابل هو وسائط الوقت الحقيقي: خادم SIP حساس للكمون ويحتاج إلى نطاق واسع ومتوقع من منافذ UDP يمكن الوصول إليها من الخارج، وقد تعيق شبكة الحاويات ذلك. بقية هذا القسم يمرّ عبر مختبر الكتاب نفسه — `lab/Dockerfile` و`lab/docker-compose.yml` — كمثال عملي ملموس، ثم يوضح الفخ الوحيد الذي يواجهه الجميع: RTP والشبكة المتصلة بالجسر.

### The image: building Asterisk from source

مختبر `Dockerfile` يبني Asterisk 22 من المصدر على Debian 12. شكل هذا البناء يستحق القراءة حتى وإن لم تقم بإنشاء واحد بنفسك:

```dockerfile
FROM debian:12-slim

ARG ASTERISK_VERSION=22.10.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential wget ca-certificates pkg-config \
        libedit-dev libxml2-dev libsqlite3-dev uuid-dev libssl-dev \
        libsrtp2-dev libcurl4-openssl-dev libncurses-dev \
    && rm -rf /var/lib/apt/lists/*

# ... download + tar xzf asterisk-${ASTERISK_VERSION}.tar.gz ...

RUN ./configure --with-jansson-bundled --with-pjproject-bundled \
    && make menuselect.makeopts \
    && menuselect/menuselect --enable res_srtp --enable res_http_websocket menuselect.makeopts \
    && make -j"$(nproc)" \
    && make install \
    && make install-logrotate \
    && ldconfig

EXPOSE 5060/udp 10000-10100/udp
CMD ["asterisk", "-f", "-vvv"]
```

Three things to call out:

- **The version is pinned** (`ARG ASTERISK_VERSION=22.10.0`). Reproducibility is the
  whole point of containerizing — bump it deliberately, rebuild, retest.
- **`--with-pjproject-bundled` and `--with-jansson-bundled`** build the SIP stack
  version-matched to Asterisk, so you depend on fewer apt packages and never fight a
  distro PJSIP that is out of step.
- **`CMD ["asterisk", "-f", "-vvv"]`** runs Asterisk in the *foreground* (`-f`, "do not
  fork"). This is the key difference from a systemd host: a container's main process
  must not daemonize, or the container would exit immediately. So in a container you do
  **not** use the systemd unit at all — the container runtime (Docker, plus `restart:`
  policy) becomes the supervisor that the unit's `Restart=` was on a VM.

### Bind-mounting `/etc/asterisk`

The image deliberately contains **no** configuration. Instead `docker-compose.yml`
bind-mounts the host's config directory in:

```yaml
services:
  asterisk:
    build: .
    image: astbook/asterisk:22.10.0
    container_name: astlab-asterisk
    restart: unless-stopped
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

`./asterisk/etc:/etc/asterisk:ro` يربط الدليل المتحكم فيه بالإصدار `lab/asterisk/etc`
بـ **`/etc/asterisk`** داخل الحاوية، للقراءة فقط (`:ro`). الفائدة كبيرة:
الصورة تبقى غير قابلة للتغيير وقابلة لإعادة الاستخدام، بينما يبقى التكوين على المضيف حيث
يمكن تحريره، وبشكل حاسم، حفظه في git (القسم التالي). لتطبيق تغيير في التكوين
تقوم بتحرير الملف وإعادة التحميل — `docker compose exec asterisk asterisk -rx 'core reload'` —
دون الحاجة لإعادة بناء. `restart: unless-stopped` هو ما يعادل مستوى الـ compose لـ
systemd's `Restart=`: Docker يعيد تشغيل الحاوية إذا خرج Asterisk، لكن ليس إذا
قمت بإيقافه عمدًا.

### المضيف مقابل الشبكة الجسرية — مشكلة RTP

هذا هو أكثر فشل شائع في حاويات Asterisk، لذا من المفيد
فهمه بدقة. بشكل افتراضي، يضع Docker الحاوية على شبكة **جسرية**
وتنشر المنافذ الفردية باستخدام `ports:`. الإشارة تعمل بشكل جيد — 5060 هو منفذ واحد.
المشكلة تكمن في الوسائط: يستخدم RTP *نطاقًا* من منافذ UDP (يحددها `rtp.conf`
`rtpstart=10000` / `rtpend=10100`)، ويجب نشر **كل** منفذ قد يحمل الصوت.

المختبر يفعل ذلك بالضبط:

```yaml
    ports:
      - "5060:5060/udp"
      - "10000-10100:10000-10100/udp"
```

لاحظ أن نطاق نشر RTP (`10000-10100`) يطابق `rtp.conf` تمامًا. إذا أخطأت —  
نشر عدد قليل جدًا من المنافذ، أو نطاق مختلف عن `rtp.conf` — فإن المكالمات تتصل ولكن
تواجه **صوتًا أحادي الاتجاه أو لا صوت على الإطلاق**، لأن حزم RTP تصل إلى منفذ لا يقوم
Docker بإعادة توجيهه. هناك تحذيران إضافيان عند استخدام وضع الجسر:

- **نشر آلاف المنافذ بطيء وثقيل.** عادةً ما يكون نطاق RTP الإنتاجي
  10000–20000. إنشاء Docker لحوالي 10000 تحويل بروكسي من مستوى المستخدم مكلف عند
  بدء التشغيل ويضيف خطوة إضافية في مسار الوسائط. يحتفظ المختبر بنطاق صغير
  متعمد من 100 منفذ لأنه لا يجري سوى مكالمة اختبار أو اثنتين.
- **NAT في SDP.** خلف الجسر، يرى Asterisk عنوان IP الخاص بالحاوية وقد
  يعلن عنه في SDP. على مضيف عام يجب إخبار PJSIP بعنوانه الخارجي باستخدام
  `external_media_address` / `external_signaling_address` على النقل (وتعيين
  `local_net`)، تمامًا كما تفعل خلف أي NAT — راجع *استضافة السحابة* أدناه.

البديل هو **شبكة المضيف** (`network_mode: host`)، التي تزيل الجسر
تمامًا: تشارك الحاوية مكدس شبكة المضيف، لذا يصبح 5060 والنطاق الكامل لـ RTP
قابلين للوصول دون نشر منافذ ولا خطوة وسائط إضافية. هذا هو
الوضع الموصى به لحاوية Asterisk حقيقية — فهو يتجاوز مشكلة نطاق RTP
كليًا. تكلفته هي العزل: يمكن للحاوية ربط أي منفذ على المضيف وتفقد
شبكة كل خدمة في compose. (شبكة المضيف ميزة في لينكس؛ على Docker Desktop
لأنظمة macOS/Windows تتصرف بشكل مختلف، وهذا جزء من سبب استخدام هذا المختبر التعليمي
لمنفذات منشورة صريحة.)

### أحجام دائمة لـ spool والبريد الصوتي

طبقة الكتابة القابلة للكتابة في الحاوية هي **مؤقتة** — عند تدمير الحاوية يختفي كل ما
كتبته. بالنسبة لـ Asterisk يعني ذلك أن البريد الصوتي، والتسجيلات، و spool المكالمات الصادرة
وقاعدة البيانات المحلية ستختفي عند كل `docker compose up --build`. يبقى الإعداد لأن
الملفات مُربطة من المضيف؛ *الحالة* تحتاج إلى نفس المعالجة.
داخل الحاوية الأشجار ذات الصلة هي:

```
/var/spool/asterisk        # voicemail, monitor recordings, outgoing/, etc.
/var/lib/asterisk          # astdb.sqlite3 (the internal database)
/var/log/asterisk          # full, messages, security, cdr-csv/, cel-custom/
```

(The lab's running container shows exactly these — `/var/spool/asterisk` contains
`voicemail`, `monitor`, `outgoing`, `recording`; `/var/lib/asterisk` holds
`astdb.sqlite3`.) To preserve them, mount named volumes for the directories that hold
state you care about:

```yaml
    volumes:
      - ./asterisk/etc:/etc/asterisk:ro     # config (bind, in git)
      - ast-spool:/var/spool/asterisk        # voicemail + recordings (persist)
      - ast-lib:/var/lib/asterisk            # astdb (persist)
      - ast-log:/var/log/asterisk            # logs (persist)

volumes:
  ast-spool:
  ast-lib:
  ast-log:
```

The teaching lab omits these on purpose — it is stateless and reproducible by design, so every `up` is a clean slate — but a production container **must** have them, or you will lose voicemail on the first redeploy.

## إدارة التكوين والنسخ الاحتياطي

تشير عملية الربط (bind‑mount) أعلاه إلى النموذج الصحيح: اعتبر `/etc/asterisk` كـ **code** والبقية كـ **data**.

### احتفظ بـ `/etc/asterisk` في نظام التحكم بالإصدارات

دليل التكوين هو مجموعة مسطحة من ملفات النصوص دون أسرار لا يمكن قوالبتها — وهو مثالي لـ git. ابدأ مستودعًا في `/etc/asterisk` (أو، كما في المختبر، احتفظ بالتكوين بجانب المشروع وربطه). الفوائد:

- كل تغيير يمكن مراجعته وإرجاعه (`git diff`، `git revert`).
- لديك سجل تدقيق يوضح من غير ما غير ومتى.
- بالاشتراك مع صورة حاوية، يصف التزام تكوين معروف مع علامة صورة مثبتة النشر بالكامل.

بعض التحذيرات الخاصة بتكوين Asterisk:

- **الأسرار.** يحتوي `pjsip.conf` (و`manager.conf`، `ari.conf`) على كلمات مرور. لا تلتزم بأسرار حقيقية إلى مستودع مشترك بنص واضح — قوالبها (ملف واحد لكل بيئة، أو مدير أسرار / استبدال بيئة عند النشر) واحتفظ فقط بالعنصر النائب في git. كلمات مرور النمط البسيط `Lab-6001-secret` في المختبر مقبولة *فقط* لأنها موجودة على شبكة Docker خاصة.
- **قوالب لكل بيئة.** القيم الفورية التي تختلف بين التطوير، والاختبار، والإنتاج (عناوين الربط، عناوين IP الخارجية، بيانات اعتماد الـ trunk، عناوين URL لقاعدة البيانات) هي بالضبط السطور التي تقوم بقوالبتها، مع الحفاظ على معظم التكوين متطابقًا عبر البيئات.

### ما الذي يجب نسخه احتياطيًا

يغطي التكوين في git مخطط الاتصال (dialplan) والنقاط الطرفية، لكن نظام PBX الحي يجمع *حالة* ليست موجودة في أي ملف تكوين. النسخة الاحتياطية الكاملة هي:

| ما | أين | لماذا |
|------|-------|-----|
| التكوين | `/etc/asterisk/` | مخطط الاتصال، النقاط الطرفية (أيضًا في git) |
| البريد الصوتي والتسجيلات | `/var/spool/asterisk/` | بيانات المستخدم — لا يمكن استبدالها |
| قاعدة البيانات الداخلية | `/var/lib/asterisk/astdb.sqlite3` | مفاتيح `DB()`، حالة الجهاز |
| CDR / CEL | `/var/log/asterisk/cdr-csv/` أو مخزن SQL | الفوترة والتاريخ |
| قواعد البيانات الخارجية | MySQL/PostgreSQL الخاصة بك | الفورية، CDR، البريد الصوتي |

يستحق **astdb** ملاحظة: هو مخزن القيم المفتاحية الصغير المدمج في Asterisk (ملف SQLite في `/var/lib/asterisk/astdb.sqlite3`) يُستخدم بواسطة وظائف مخطط الاتصال `DB()`، حالات الأجهزة، إعدادات follow‑me وما شابه. يمكنك تفريغه للفحص أو النسخ الاحتياطي من سطر الأوامر:

```
asterisk -rx 'database show'
```

إذا كان CDR/CEL أو البريد الصوتي أو تكوين PJSIP الخاص بك موجودًا في قاعدة بيانات خارجية (انظر *Asterisk Real‑Time* و *Asterisk Call Detail Records*)، فإن تلك القاعدة الآن هي مصدر الحقيقة لتلك البيانات ويجب أن تكون ضمن دورة النسخ الاحتياطي العادية لقاعدة البيانات — النسخ الاحتياطي لـ `/etc/asterisk` وحده غير كاف.

## المراقبة والقابلية للملاحظة

لا يمكنك تشغيل ما لا تراه. يعرّف Asterisk حالته على أربعة مستويات، من
نظرة سريعة للإنسان إلى خط أنابيب القياسات: **CLI**، سجلات **CDR/CEL**،
أحداث **AMI/ARI**، و**مصدّرات القياسات**.

### فحوصات صحة CLI

أسرع فحص "هل هو صحي؟" هو عبر CLI. تُنفّذ الأوامر أدناه مباشرةً على
المختبر. القنوات أولاً:

```
*CLI> core show channels
Channel              Location             State   Application(Data)
0 active channels
0 active calls
0 calls processed
```

`0 active calls` على نظام هادئ أمر طبيعي؛ وعلى نظام مشغول هذا هو التزامنك في الوقت الحقيقي. `core show uptime` يؤكد أن العملية لم تكن تعيد التشغيل تحتك:

```
*CLI> core show uptime
System uptime: 1 hour, 40 minutes, 19 seconds
Last reload: 12 minutes, 32 seconds
```

لصحة SIP، `pjsip show endpoints` يُظهر كل نقطة نهاية وما إذا كانت جهات الاتصال المسجلة قابلة للوصول. من المختبر:

```
*CLI> pjsip show endpoints
 Endpoint:  6001                                                 Unavailable   0 of inf
     InAuth:  6001/6001
        Aor:  6001                                               1
 Endpoint:  6002                                                 Unavailable   0 of inf
     InAuth:  6002/6002
        Aor:  6002                                               1
 Endpoint:  sipp                                                 Unavailable   0 of inf
        Aor:  sipp                                               1
   Identify:  sipp-identify/sipp
        Match: 172.30.0.0/24
 Endpoint:  webrtc-1000                                          Unavailable   0 of inf
     InAuth:  webrtc-1000/webrtc-1000
        Aor:  webrtc-1000                                        1
Objects found: 4
```

`Unavailable` هنا يعني ببساطة أنه لا يوجد هاتف مسجل حاليًا على تلك النقاط الطرفية (المختبر لا يحتوي على عملاء نشطين) — بمجرد أن يسجل برنامج softphone وتؤكد `qualify` ذلك، تُظهر الحالة أن جهة الاتصال قابلة للوصول. أوامر مرافقة: `pjsip show contacts` (التسجيلات الحالية ووقت الرحلة ذهابًا وإيابًا)، `pjsip show transports`، و`pjsip show aor <name>` لعنوان AOR واحد. هذه هي الأدوات اليومية لسؤال "لماذا لا يمكن الوصول إلى الامتداد X؟".

### CDR و CEL

كل مكالمة تترك **سجل تفاصيل المكالمة** (CDR)؛ **تسجيل أحداث القناة** (CEL) يضيف أحداثًا أكثر تفصيلاً لكل قناة. تأكد من أن CDR نشط وأي خلفية تخزنه:

```
*CLI> cdr show status

Call Detail Record (CDR) settings
----------------------------------
  Logging:                    Enabled
  Mode:                       Simple
  Log calls by default:       Yes
  Log unanswered calls:       No
...
* Registered Backends
  -------------------
    (none)
```

المختبر يُظهر `(none)` تحت الأنظمة الخلفية المسجلة لأن تكوين المختبر الأدنى لا يحمل وحدة تخزين CDR — لذا تُحسب السجلات ولكن لا تُكتب في أي مكان. في بيئة الإنتاج تقوم بتحميل نظام خلفي (CSV، أو `cdr_odbc`/`cdr_adaptive_odbc` إلى MySQL/PostgreSQL) ويصبح ذلك مصدر الفوترة والسجل التاريخي. يتم **تعطيل CEL بشكل افتراضي** (`cel show status` reports `CEL Logging: Disabled` in the lab) and you enable it in `cel.conf` فقط عندما تحتاج إلى تفاصيل على مستوى الحدث. كلاهما مغطى بعمق في *Asterisk Call Detail Records*؛ بالنسبة للمراقبة، النقطة هي أن CDR/CEL هما سجلك *التاريخي*، بينما الـ CLI هو عرضك *الحي*.

### AMI and ARI events

للمراقبة البرمجية في الوقت الحقيقي تريد تدفقًا دفعًا للأحداث بدلاً من
استطلاع الـ CLI:

- **AMI (Asterisk Manager Interface)** هو بروتوكول الأحداث/الأوامر عبر TCP القديم
  (`manager.conf`). اشترك وستتلقى `Newchannel`، `Hangup`، `DialBegin`،
  `BridgeEnter`، `PeerStatus` وأحداثًا مشابهة عندما تحدث المكالمات — العمود الفقري للوحّات
  وأدوات حساب المكالمات. في المختبر يتم تعطيل AMI بشكل افتراضي (`manager show settings`
  يُبلغ عن `Manager (AMI): No`)؛ يمكنك تمكينه وتقييده في `manager.conf`.
- **ARI (Asterisk REST Interface)** هو واجهة HTTP + WebSocket الحديثة
  (`ari.conf`، تُقدم عبر خادم HTTP المدمج). تُوفر تدفق أحداث JSON
  وتحكمًا دقيقًا في المكالمات — الخيار المناسب للتكاملات الجديدة.

كلاهما موضح بالتفصيل في *Extending Asterisk with AMI and AGI* و*The Asterisk REST
Interface (ARI)*. التحذير المتعلق بالنشر: **AMI و ARI قويان ويجب ألا يُكشف عنهما للإنترنت أبداً.** اربط
خادم HTTP بـ localhost أو شبكة إدارة، استخدم أسرارًا قوية وفريدة، وقم بجدار حماية المنافذ — راجع *Asterisk Security*.

### Metrics: Prometheus and Grafana

للوحات المعلومات والتنبيهات، يأتي Asterisk 22 بمُصدّر Prometheus،
**`res_prometheus.so`** (وحدة بمستوى دعم *ممتد*), الذي يُظهر المقاييس
على نقطة نهاية HTTP يقوم خادم Prometheus بجمعها. إلى جانب مقاييس عملية النواة، يضم موفّرين قابليين للإضافة يغطيون القنوات، المكالمات، النقاط الطرفية، الجسور وتسجيلات PJSIP الصادرة:

```
# core process
asterisk_core_uptime_seconds
asterisk_core_last_reload_seconds
asterisk_core_scrape_time_ms
asterisk_core_properties
# channels
asterisk_channels_count
asterisk_channels_state
asterisk_channels_duration_seconds
# calls
asterisk_calls_count
asterisk_calls_sum
# endpoints
asterisk_endpoints_count
asterisk_endpoints_state
asterisk_endpoints_channels_count
# bridges
asterisk_bridges_count
asterisk_bridges_channels_count
# PJSIP outbound registrations
asterisk_pjsip_outbound_registration_status
```

يمكنك التأكد من وجود الوحدة في بناء المختبر:

```
*CLI> module show like prometheus
Module                         Description                     Use Count  Status      Support Level
res_prometheus.so              Asterisk Prometheus Module      0          Not Running  extended
```

It shows `Not Running` because the lab does not configure or load it; enabling it
(`prometheus.conf` plus the HTTP server) turns Asterisk into a Prometheus target. Point
Prometheus at the scrape endpoint and Grafana at Prometheus, and you get time-series
dashboards (concurrent calls, registrations, ASR/ACD trends) and alerting (e.g. "active
calls dropped to zero" or "registration failures spiking"). For teams already running
Prometheus/Grafana this is the natural way to fold Asterisk into existing observability,
rather than parsing CLI output.

### رموز استجابة SIP التي تستحق المتابعة

Whatever the pipeline, a few SIP results signal trouble and are worth alerting on:
sustained `401`/`407` challenge failures or `403 Forbidden` suggest a brute-force or
misconfigured-credential storm (cross-reference Fail2Ban in *Asterisk Security*);
`503 Service Unavailable` points at an overloaded or congested server or trunk; and a
spike in `408 Request Timeout`/`480 Temporarily Unavailable` usually means endpoints
have gone unreachable (NAT timeout, qualify failures).

## التوافر العالي والتوسيع

خادم Asterisk واحد هو نقطة فشل واحدة وله حد أقصى ثابت للمكالمات. المشكلتان — *البقاء قيد التشغيل* و *التوسع* — لهما إجابات مختلفة.

### نشط/احتياطي مع عنوان IP عائم

النمط الكلاسيكي المتبع للتوافر العالي في Asterisk هو **نشط/احتياطي** (ليس نشط/نشط — حالة المكالمة في Asterisk صعب مشاركتها مباشرة). خادمان متطابقان، أحدهما نشط والآخر احتياطي، يشتركان في **عنوان IP عائم (افتراضي)** يديره مدير عنقود مثل **keepalived** (VRRP) أو **Pacemaker/Corosync**. الهواتف والخطوط تُسجَّل إلى العنوان العائم، لا إلى أي مضيف حقيقي. إذا فشل الفحص الصحي للعقدة النشطة، ينتقل عنوان IP العائم إلى العقدة الاحتياطية التي تتولى الدور.

التحذير الصريح: فشل IP **يسقط المكالمات الجارية** — لا يقوم Asterisk بتكرار حالة القناة الحية بين العقد، لذا يجب على أي شخص في منتصف مكالمة إعادة الاتصال. تُعاد التسجيلات خلال دورة تأهيل/تسجيل. ما يحققه الفشل هو أن *الخدمة* تستعيد عملها في ثوانٍ دون تدخل يدوي، وهو الهدف لمعظم أنظمة PBX. لجعل العقدة الاحتياطية قادرة فعليًا على الاستيلاء، تحتاج كلتا العقدتين إلى نفس التكوين (ملف git الخاص بك `/etc/asterisk`، مُنَشَّر بشكل متماثل) ونفس *الحالة* — وهذا هو النقطة التالية.

### إظهار الحالة خارجيًا باستخدام PJSIP Realtime

النمط النشط/الاحتياطي يعمل فقط إذا كانت العقدة الاحتياطية تعرف نفس النقاط الطرفية والتسجيلات مثل العقدة النشطة. الطريقة لتحقيق ذلك هي **إيقاف حفظ الحالة في ملفات مسطحة على جهاز واحد** ونقلها إلى قاعدة بيانات مشتركة تقرأها كلتا العقدتين. **PJSIP Realtime** (Sorcery المدعومة بقاعدة بيانات) يفعل ذلك بالضبط: النقاط الطرفية، AORs، المصادقات — وبشكل مهم، **التسجيلات** (جدول `ps_contacts`) — تُخزن في MySQL/PostgreSQL بدلاً من `pjsip.conf` والذاكرة المحلية. كل عقدة Asterisk تشير إلى نفس قاعدة البيانات، لذا الهاتف المسجل عبر عقدة واحدة يكون مرئيًا للآخر. هذا مغطى في *Asterisk Real-Time* (قسم PJSIP Realtime / Sorcery)؛ هنا نقطة النشر هي أن **إظهار الحالة خارجيًا هو الشرط المسبق لكل من التوافر العالي والتوسيع الأفقي** — بدون ذلك، كل عقدة هي جزيرة.

طبق نفس المنطق على باقي حالتك: CDR/CEL إلى مخزن SQL مشترك، البريد الصوتي على تخزين مشترك/مُكرر (أو `ODBC_STORAGE`)، ومفاتيح astdb التي تعتمد عليها إلى قاعدة بيانات. بمجرد أن تصبح الحالة خارجية، تصبح عقد Asterisk أقرب إلى أن تكون واجهات أمامية قابلة للتبادل.

### وكلاء SIP في المقدمة (OpenSIPS)

لتوسيع *ما وراء* سعة خادم واحد، تضع **وكيل SIP/موازن تحميل** أمام مجموعة من خوادم وسائط Asterisk. **OpenSIPS** هو وكيل SIP مُصمم خصيصًا، عالي الإنتاجية (يتعامل مع مئات الآلاف من التسجيلات ويوجه الإشارات دون لمس الوسائط). يقدم الوكيل عنوان SIP واحد للعالم، يحافظ على خدمة التسجيل/الموقع، ويوزع المكالمات عبر الخلفيات Asterisk. هذا الفصل — طبقة وكيل خفيفة تقوم بالتسجيل والتوجيه، وطبقة Asterisk قابلة للتوسيع أفقيًا تقوم بمعالجة المكالمات الفعلية (IVR، قوائم الانتظار، المؤتمرات، التحويل) — هو الطريقة التي تنمو بها النُظم الكبيرة لتتجاوز خادمًا واحدًا. (منصة SipPulse نفسها تستخدم OpenSIPS أمام خوادم الوسائط/التطبيقات لهذا السبب بالذات.)

### توسيع الوسائط

الوكيـل يوزع *الإشارات* بتكلفة منخفضة؛ **الوسائط هي المورد المكلف**. إعادة توجيه RTP، وخاصة التحويل بين الترميزات (مثل

## Cloud hosting

تشغيل Asterisk على جهاز افتراضي سحابي (AWS، GCP، Azure، VPS) شائع ويعمل بشكل جيد، لكن
شبكة السحابة **مُعَدلَة NAT ومحمية بجدار ناري بشكل افتراضي**، وهذا يتعارض مع SIP. ما يلي
هو القضايا الخاصة بالنشر.

### NAT and the SDP

جهاز افتراضي سحابي يمتلك عادةً **عنوان IP خاص** على بطاقة الشبكة وعنوان **IP عام** منفصل
يقوم المزود بترجمته عبر NAT. إذا أعلن Asterisk عن العنوان الخاص في SDP، فإن الهواتف
البعيدة ترسل RTP إلى ثقب أسود — وهو العرض الكلاسيكي لعدم وجود صوت/اتجاه واحد.
أخبر PJSIP بهويته العامة على النقل:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
external_media_address=203.0.113.10      ; the VM's PUBLIC IP
external_signaling_address=203.0.113.10
local_net=10.0.0.0/8                     ; your private/VPC range(s)
```

`external_*` يجعل Asterisk يعيد كتابة العنوان الذي يعلنه إلى النظراء العامين، بينما
`local_net` يخبره أي النظراء محليون (ويجب *عدم* إعادة كتابتهم). هذا هو
نفس معالجة NAT التي نوقشت لشبكات Docker المتصلة أعلاه — جهاز افتراضي سحابي هو، في
الواقع، خلف NAT.

### Firewall and the RTP range

عادةً ما يُطبق جداران ناريان على جهاز افتراضي سحابي: **مجموعة الأمان الخاصة بالمزود** / ACL
الشبكي، و**جدار الحماية الخاص بالمضيف** iptables. يجب على كلاهما فتح نفس المنافذ، وتكون
السياسة هي نفسها المذكورة في فصل الأمان. مجموعة القواعد المستعادة من الإصدار الأول
(`docs/legacy-labs/configs/Lab7/rules.v4`) تلتقط الشكل — قبول SIP ونطاق RTP، قبول الاتصالات القائمة/المتعلقة، إسقاط البقية:

```
-A INPUT -p udp -m udp --dport 5060 -j ACCEPT
-A INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -j DROP
```

تصحيحان يقدمهما فصل الأمان وهما مهمان هنا: فتح **5061 على TCP** (ليس UDP) إذا كنت تستخدم SIP/TLS،
وتذكر أن نطاق UDP الخاص بـ RTP في جدار الحماية يجب أن يطابق
`rtpstart`/`rtpend` في `rtp.conf` تمامًا — نفس النطاق الذي تنشره على الحاوية.
لا تقم بتكرار بناء iptables/Fail2Ban هنا؛ **اتبع أقسام جدار الحماية، Fail2Ban و
TLS/SRTP في *Asterisk Security*** (Fail2Ban يراقب قناة سجل `security` التي يفعّلها المختبر بالفعل في `logger.conf`) وطبق تلك السياسة في *كلا* جدار الحماية
للمضيف ومجموعة الأمان السحابية.

### Latency, region and the SBC

- **اختر منطقة قريبة من مستخدميك.** الصوت حساس للكمون — الكمون من الفم إلى الأذن
  فوق ~150 مللي ثانية يُلاحَظ. استضف الجهاز الافتراضي في المنطقة الأقرب إلى معظم
  هواتفك ونقاط الربط؛ الوسائط عبر القارات تكون أسوأ سمعيًا.
- **ضع SBC أمام أي نشر يواجه الإنترنت.** **Session Border Controller** ينهى SIP/RTP عند الحافة،
  يخفي طوبولوجيتك، يطبع NAT، ويمتص هجمات DoS وحركة الفحص قبل أن تصل إلى Asterisk.
  التوصية الأساسية في فصل الأمان — *لا تعرض Asterisk الخام للإنترنت* — تنطبق
  مرتين في السحابة، حيث يتم فحص عنوان IP العام لجهازك خلال دقائق من تشغيله. SBC
  (أو على الأقل بروكسي SIP مقوى مثل OpenSIPS مع Fail2Ban) هو الحافة القياسية.

## Summary

Deployment is where a working dialplan becomes a dependable service. On a VM, run
Asterisk under **systemd** as a **non-root** user, letting the unit's `Restart=` keep it
alive (safe_asterisk is superseded) and using `core reload` rather than `systemctl
restart` for config changes. **Containerizing** with Docker — as the book's lab does —
gives you an immutable, pinned image with config **bind-mounted** from a git'd
`/etc/asterisk`; the catch is media, so either use **host networking** or publish an RTP
port range that **exactly matches `rtp.conf`**, and mount **persistent volumes** for
spool/voicemail/astdb so state survives a redeploy. Treat config as code and **back up the
state** config does not capture: voicemail, recordings, `astdb.sqlite3`, and CDR/CEL.
**Observe** the system at four levels — the CLI (`core show channels`, `pjsip show
endpoints`) for the live view, **CDR/CEL** for history, **AMI/ARI** for programmatic
events, and the **`res_prometheus`** exporter into Grafana for dashboards and alerts —
while keeping AMI/ARI off the public internet. To **stay up**, run active/standby with a
**floating IP** (accepting that failover drops live calls); to **grow**, externalize state
with **PJSIP Realtime**, front a pool of media servers with **OpenSIPS**, and
minimize transcoding because **media — not registrations — is what caps a server**.
Finally, in the **cloud**, treat the VM as behind NAT (`external_media_address`,
`local_net`), open the firewall per the Security chapter in both the host and the provider
security group, pick a low-latency region, and never expose raw Asterisk — put an **SBC**
at the edge.

## Quiz

1. على مضيف systemd، ما الذي يحل محل مهمة ملف التغليف القديم `safe_asterisk` لإعادة تشغيل Asterisk المتعطل؟
   - A. مهمة cron
   - B. توجيه `Restart=` في ملف الوحدة
   - C. `systemctl enable`
   - D. الـ astdb
2. لتطبيق تغيير في التكوين على Asterisk قيد التشغيل **دون قطع المكالمات**، يجب عليك:
   - A. `systemctl restart asterisk`
   - B. إعادة تشغيل الخادم
   - C. `asterisk -rx 'core reload'`
   - D. إعادة بناء صورة الحاوية
3. Asterisk المُحَوَّل (شبكة جسرية) يربط المكالمات لكنه **لا صوت له**. السبب الأكثر احتمالاً هو:
   - A. خطأ في الـ dialplan
   - B. نطاق منفذ RTP UDP المنشور لا يتطابق مع `rtpstart`/`rtpend` في `rtp.conf`
   - C. تم تعطيل CDR
   - D. الـ CLI غير قابل للوصول
4. أي الأدلة يجب أن تُركّب كـ **أحجام دائمة** حتى لا تفقد الحالة عند إعادة نشر الحاوية؟ (اختر كل ما ينطبق)
   - A. `/var/spool/asterisk` (voicemail, recordings)
   - B. `/var/lib/asterisk` (astdb)
   - C. `/etc/asterisk` (already bind-mounted from the host)
   - D. `/usr/sbin`
5. أي أمر CLI يعطي عدد المكالمات النشطة في الوقت الحقيقي؟
   - A. `cdr show status`
   - B. `core show channels`
   - C. `pjsip show transports`
   - D. `module show like prometheus`
6. في Asterisk 22، الطريقة المدعومة لتصدير مقاييس المكالمات/القنوات إلى مجموعة Prometheus/Grafana هي:
   - A. تحليل ملف السجل `full`
   - B. وحدة `res_prometheus.so`
   - C. سكريبتات AGI
   - D. لا توجد طريقة
7. ما هو الشرط المسبق لكل من الفشل العالي HA والتوسع الأفقي عبر عدة عقد Asterisk؟
   - A. التشغيل كجذر (root)
   - B. إظهار الحالة خارجياً (مثل تسجيلات PJSIP Realtime في قاعدة بيانات مشتركة)
   - C. تعطيل CDR
   - D. استخدام شبكة جسرية
8. أي مورد يحد مباشرةً من عدد المكالمات المتزامنة التي يمكن لخادم Asterisk واحد التعامل معها؟
   - A. عدد المستخدمين المسجلين
   - B. معالجة الوسائط، خاصة التحويل بين الصيغ
   - C. حجم `/etc/asterisk`
   - D. خلفية CDR
9. على جهاز افتراضي سحابي، أي إعدادات نقل `pjsip.conf` تجعل Asterisk يعلن عن عنوانه العام حتى يعمل الصوت عن بُعد؟ (اختر كل ما ينطبق)
   - A. `external_media_address`
   - B. `external_signaling_address`
   - C. `local_net`
   - D. `qualify_frequency`
10. بالنسبة لنشر سحابي يواجه الإنترنت، القاعدة الأساسية في فصل الأمان هي:
    - A. تشغيل NICين دائمًا
    - B. لا تعرض Asterisk الخام على الإنترنت؛ ضع SBC (أو وكيل محكم + Fail2Ban) عند الحافة
    - C. استخدم UDP فقط
    - D. عطل TLS

**Answers:** 1 — B · 2 — C · 3 — B · 4 — A, B · 5 — B · 6 — B · 7 — B · 8 — B · 9 — A, B, C · 10 — B
