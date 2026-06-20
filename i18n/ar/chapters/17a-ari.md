# واجهة Asterisk REST (ARI)

الفصل السابق تناول AMI و AGI، الطريقتين التقليديتين لإضافة منطق خارجي إلى Asterisk. كلاهما يسبق الويب الحديث: AMI يزودك بتدفق أحداث خام، سطرًا بسطر، عبر مقبس TCP، و AGI يمنح قناة واحدة لسكريبت طوال مدة المكالمة. لم يُصمَّم أيٌّ منهما لتطبيقات الحالة المتعددة، غير المتزامنة، ومتعددة القنوات التي يبنيها الناس اليوم — مثل IVRs التي تتواصل مع خدمات الويب، ولوحات التحكم بالنقر للاتصال، ومتحكمات المؤتمرات، أو الروبوتات الصوتية التي تبث الصوت إلى محرك الكلام.

ARI — واجهة Asterisk REST — تم تقديمها في Asterisk 12 لسد هذه الفجوة، وفي Asterisk 22 هي الواجهة الموصى بها لبناء تطبيقات هاتفية جديدة. الفكرة وراء ARI هي فصل واضح للمهام: **يصبح Asterisk محرك وسائط** (يجيب على القنوات، يدمج الجسور، يشغل ويسجل الصوت، يرسل DTMF)، و**تطبيقك يوفر كل منطق التحكم في المكالمات** من خلال مزيج من واجهة برمجة تطبيقات REST (HTTP) وتدفق أحداث WebSocket.

## Objectives

By the end of this chapter, the reader should be able to:

- Explain what ARI is and how it differs from AMI and AGI
- Decide when ARI is the right interface for a project
- Configure `ari.conf` and `http.conf` to enable ARI and create a user
- Connect to the ARI WebSocket event stream
- Describe the Stasis dialplan application and the `StasisStart`/`StasisEnd` events
- Describe the ARI resource model: channels, bridges, playbacks, recordings, endpoints, and device states
- Write a minimal Stasis application in Python that answers a channel, plays a sound, and hangs up
- Explain what the `externalMedia` channel is and why it matters for AI and voicebot integrations

## ما هو ARI، ومتى يُستخدم

ARI مبني على نقلين يعملان معًا:

- **واجهة برمجة تطبيقات REST (HTTP)** التي يستدعيها تطبيقك لتـ *يفعل* أشياء — إنشاء قناة، الرد عليها، تشغيل صوت، إنشاء جسر، بدء تسجيل، إنهاء المكالمة. هذه طلبات HTTP عادية (`GET`, `POST`, `DELETE`) ضد `http://asterisk-host:8088/ari/...`.
- **تيار أحداث WebSocket** يُخبر من خلاله Asterisk تطبيقك بما يحدث — تم إنشاء قناة، وصل رقم DTMF، انتهى تشغيل الصوت، غادرت قناة تطبيقك. تُسلم الأحداث ككائنات JSON.

النمط غير متزامن: تُرسل طلبًا، وتعود *نتيجة* ذلك الطلب لاحقًا كحدث. على سبيل المثال، أنت `POST` طلبًا لتشغيل صوت؛ يرد Asterisk فورًا بكائن `Playback`، وبعد بضع ثوانٍ تستقبل حدث `PlaybackFinished` عندما ينتهي الصوت.

اختر ARI بدلاً من AMI و AGI عندما:

- تحتاج إلى **تحكم دقيق في القنوات والجسور** — بناء مؤتمرات، إيقاف مؤقت، قوائم انتظار، أو تدفقات مكالمات مخصصة من العناصر الأساسية بدلاً من الاعتماد على تطبيقات dialplan.
- يكون تطبيقك **حالة مستمرة وطويلة الأمد**، يحتفظ بعدة قنوات في آن واحد ويتفاعل مع الأحداث عبر جميعها.
- تريد التكامل مع **خدمات ويب، حافلات رسائل، أو محركات AI/الصوت** وتفضّل JSON عبر HTTP على بروتوكول سطر أو سكريبت stdin/stdout.
- تبدأ **مشروعًا جديدًا** وتريد الواجهة التي يوصي بها مشروع Asterisk بنشاط.

لا يزال AMI الأداة المناسبة عندما تحتاج فقط إلى *مراقبة* النظام أو إطلاق أوامر عرضية (dialers, wallboards, monitoring). لا يزال AGI ملائمًا لسكريبت IVR سريع ومستقل. لكن لأي شيء يُنظم المكالمات، فإن ARI هو الجواب الحديث.

> لا يستبدل ARI الـ dialplan — بل يكمله. تعمل قناة في الـ dialplan كالمعتاد حتى تصل إلى تطبيق `Stasis()`، وعندها تُسلم السيطرة إلى تطبيق ARI الخاص بك. عندما ينتهي تطبيقك، يمكن إرجاع القناة إلى الـ dialplan أو إنهاؤها.

## تمكين ARI: http.conf و ari.conf

ARI يعمل فوق خادم HTTP المدمج في Asterisk، لذا هناك ملفا إعداد مشاركان: `http.conf` يُفعّل خادم الويب، و`ari.conf` يُفعّل ARI ويعرّف مستخدميه.

### http.conf

يجب تمكين خادم HTTP وربطه بعنوان ومنفذ. المنفذ التقليدي لـ ARI هو **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

لبيئات الإنتاج يجب وضع ARI خلف TLS. يمكن لـ Asterisk تقديم HTTPS مباشرةً (`tlsenable=yes`، `tlsbindaddr`، `tlscertfile`، `tlsprivatekey`)، أو يمكنك إنهاء TLS في وكيل عكسي أمام المنفذ 8088. عبر TLS تصبح عناوين URL `https://` و`wss://` بدلاً من `http://` و`ws://`.

يمكنك التأكد من أن خادم HTTP يعمل من خلال سطر الأوامر:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

يحتوي `ari.conf` على قسم `[general]` وقسم واحد لكل مستخدم.

```ini
[general]
enabled=yes
pretty=yes              ; pretty-print JSON responses (handy while learning)

[asterisk]
type=user
read_only=no            ; set to yes for a user that may only issue GET requests
password=secret
password_format=plain   ; "plain" (default) or "crypt"
```

بعض الملاحظات حول هذه الخيارات:

- `enabled` يفعّل أو يوقف ARI على مستوى عالمي.
- `pretty` ينسق استجابات JSON لتكون قابلة للقراءة البشرية؛ أوقفه في بيئة الإنتاج.
- كل مستخدم هو قسم مسمى يحتوي على `type=user`.
- `read_only=yes` يقتصر على طلبات القراءة فقط (GET) لهذا المستخدم.
- `password_format` قد يكون `plain` (كلمة المرور بنص صريح) أو `crypt` (كلمة مرور مشفّرة، تُولد باستخدام `mkpasswd -m sha-512`).
- `permit`، `deny`، و`acl` تسمح بتقييد عناوين IP لكل مستخدم، وفقاً لنفس قواعد `acl.conf`.

بعد تعديل الملفات، أعد تحميل الوحدات ذات الصلة (`module reload res_ari.so` و`module reload http.so`) أو أعد تشغيل Asterisk. يمكنك التحقق من تشغيل ARI باستخدام:

```
asterisk*CLI> module show like res_ari
res_ari.so          Asterisk RESTful Interface          Running
res_ari_channels.so RESTful API module - Channel res... Running
res_ari_bridges.so  RESTful API module - Bridge reso... Running
...

asterisk*CLI> ari show apps
Application Name
=========================
```

`ari show apps` يعرض تطبيقات Stasis المسجلة حالياً من قبل العملاء المتصلين. تكون القائمة فارغة حتى يتصل عميل، وهذا ما سنفعله لاحقاً.

### عنوان URL لأحداث WebSocket

يشترك العميل في تدفق الأحداث بفتح WebSocket إلى نقطة النهاية `/ari/events`، مع تحديد تطبيق Stasis الذي ينفّذه وتمرير بيانات الاعتماد الخاصة به:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

معاملات الاستعلام هي:

- `app` — اسم تطبيق Stasis الخاص بك. هذا هو نفس الاسم الذي ستستخدمه في استدعاء `Stasis()` في الـ dialplan. يمكنك تمرير عدة أسماء مفصولة بفواصل.
- `api_key` — بيانات الاعتماد، بصيغة `username:password`، مطابقة لمستخدم في `ari.conf`.
- `subscribeAll` — قيمة منطقية اختيارية (الافتراضي `false`)؛ عندما تكون `true`، يتلقى التطبيق جميع الأحداث، وليس فقط تلك الخاصة بالموارد التي يمتلكها.

نفس بيانات الاعتماد `user:pass` تُستخدم كمصادقة أساسية HTTP في استدعاءات REST (أو تُضاف كمعامل استعلام `api_key` هناك أيضاً).

## Stasis: تسليم القناة إلى تطبيقك

الجسر بين الـ dialplan و ARI هو تطبيق الـ dialplan **`Stasis()`** (الإطار الأساسي يُسمى أيضاً Stasis). عندما تصل قناة إلى `Stasis(appname[,args])`، يقوم Asterisk بتسليم تلك القناة إلى تطبيق ARI المسجل تحت `appname` ويتوقف عن تنفيذ الـ dialplan لها. التحكم الآن يعود إلى شفرتك.

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

عند دخول القناة إلى التطبيق، كل عميل متصل مشترك في `hello` يتلقى حدث **`StasisStart`** عبر الـ WebSocket، يحمل كائن القناة الكامل (معرفها، اسمها، معرف المتصل، حالتها، وأي وسائط تم تمريرها إلى `Stasis()`). هذا هو إشارة لك لبدء التحكم في القناة.

عند خروج القناة من التطبيق — لأن شفرتك أعادتها إلى الـ dialplan باستخدام `continueInDialplan`، أو لأنها تم إنهاؤها — تتلقى حدث **`StasisEnd`**. بعد أن يعود `Stasis()` إلى الـ dialplan يضبط متغير القناة `STASISSTATUS` (`SUCCESS` أو `FAILED`)، بحيث يمكن للـ dialplan التفرع بناءً على النتيجة.

## نموذج موارد ARI

ARI يعرّف داخليات Asterisk كمجموعة صغيرة من موارد REST. كل مورد يقع تحت `/ari/<resource>` ويتم التلاعب به باستخدام طرق HTTP القياسية. أهمها:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | A single call leg | originate, answer, play, record, hangup |
| **bridges** | A mixing point that joins channels | create, add/remove channels, play to the bridge |
| **playbacks** | An in-progress media playback | get status, stop, pause/unpause |
| **recordings** | Live and stored recordings | start, stop, list stored, delete |
| **endpoints** | Configured peers (PJSIP, etc.) | list, get state, send a message |
| **deviceStates** | Custom device states | list, get, set, delete |

بعض استدعاءات REST الملموسة (المسارات موضحة مع بادئة `/ari` التي تظهر على السلك):

```
# Channels
POST   /ari/channels                          # originate a new channel
POST   /ari/channels/{channelId}/answer       # answer an incoming channel
POST   /ari/channels/{channelId}/play         # play media (body: media=sound:hello-world)
POST   /ari/channels/{channelId}/record       # record the channel
DELETE /ari/channels/{channelId}              # hang up the channel

# Bridges
POST   /ari/bridges                           # create a bridge (e.g. type=mixing)
POST   /ari/bridges/{bridgeId}/addChannel     # add a channel (param: channel=<id>)
POST   /ari/bridges/{bridgeId}/play           # play media to everyone in the bridge
DELETE /ari/bridges/{bridgeId}                # destroy the bridge

# Read-only resources
GET    /ari/endpoints
GET    /ari/deviceStates
GET    /ari/recordings/stored
GET    /ari/playbacks/{playbackId}
```

معامل `media` في طلب `play` يأخذ URI وسائط. الشكل الأكثر شيوعًا هو URI من نوع `sound:` يحدد صوتًا مدمجًا، مثل `sound:hello-world` أو `sound:tt-monkeys`. عندما ينتهي الصوت، يصدر Asterisk حدث `PlaybackFinished` لذلك المعرف playback، وهو ما يتيح لتطبيقك معرفة أنه يمكن المتابعة.

القنوات والجسور هما العنصران الأساسيان اللذان تجمعهما لإنشاء تدفقات المكالمات. لربط متصلين، على سبيل المثال، تقوم بإنشاء أو قبول قناتين، وإنشاء جسر `mixing` باستخدام `POST /ari/bridges`، وإضافة القناتين إليه باستخدام `POST /ari/bridges/{bridgeId}/addChannel`. لبناء مؤتمر، ما عليك سوى الاستمرار في إضافة القنوات إلى نفس الجسر.

## مثال عملي: تطبيق Stasis بسيط

لنُنشئ أصغر تطبيق ARI مفيد. عندما يُطلب أي امتداد، ينتقل المكالمة إلى تطبيق Stasis الخاص بنا، الذي يجيب عليها، يشغل الموجه الكلاسيكي `hello-world`، ثم يقطع الاتصال.

### مخطط الاتصال

في `extensions.conf`، أرسل القناة إلى Stasis:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

اسم التطبيق `hello` يطابق الـ `app=hello` الذي نستخدمه عند الاتصال.

### عميل Python

هذا العميل يستخدم مكتبتين معروفتين: `requests` لاستدعاءات REST و`websocket-client` لتدفق الأحداث. ثبّتها باستخدام `pip install requests websocket-client`.

```python
#!/usr/bin/env python3
"""Minimal ARI Stasis app: answer, play hello-world, hang up."""
import json
import requests
from websocket import create_connection

ARI_HOST = "127.0.0.1"
ARI_PORT = 8088
ARI_USER = "asterisk"
ARI_PASS = "secret"
APP = "hello"

BASE = f"http://{ARI_HOST}:{ARI_PORT}/ari"
AUTH = (ARI_USER, ARI_PASS)

def answer(channel_id):
    requests.post(f"{BASE}/channels/{channel_id}/answer", auth=AUTH)

def play(channel_id, media):
    # Returns the Playback object; we could track its id to await PlaybackFinished.
    r = requests.post(
        f"{BASE}/channels/{channel_id}/play",
        params={"media": media},
        auth=AUTH,
    )
    return r.json()

def hangup(channel_id):
    requests.delete(f"{BASE}/channels/{channel_id}", auth=AUTH)

def main():
    ws_url = (
        f"ws://{ARI_HOST}:{ARI_PORT}/ari/events"
        f"?app={APP}&api_key={ARI_USER}:{ARI_PASS}"
    )
    ws = create_connection(ws_url)
    print(f"Connected to ARI, waiting for calls into Stasis app '{APP}'...")

    # Track which channel each playback belongs to, so we hang up when it ends.
    playback_owner = {}

    while True:
        event = json.loads(ws.recv())
        kind = event["type"]

        if kind == "StasisStart":
            channel_id = event["channel"]["id"]
            print(f"StasisStart on channel {channel_id}")
            answer(channel_id)
            pb = play(channel_id, "sound:hello-world")
            playback_owner[pb["id"]] = channel_id

        elif kind == "PlaybackFinished":
            pb_id = event["playback"]["id"]
            channel_id = playback_owner.pop(pb_id, None)
            if channel_id:
                print(f"Playback done, hanging up {channel_id}")
                hangup(channel_id)

        elif kind == "StasisEnd":
            print(f"StasisEnd on channel {event['channel']['id']}")

if __name__ == "__main__":
    main()
```

شغّل السكريبت، ثم اطلب أي رقم من نقطة نهاية مسجلة. يجب أن تسمع "Hello, world"، ثم يُحرّر المكالمة. على وحدة تحكم Asterisk، سيعرض `ari show apps` الآن `hello` بينما يكون العميل متصلاً.

من المفيد تتبع التدفق مرة واحدة:

1. يُنفّذ مخطط الاتصال `Stasis(hello)`؛ تقوم Asterisk بتسليم القناة إلى تطبيقنا وتُرسل حدث `StasisStart`.
2. نجيب القناة، ثم نطلب من Asterisk تشغيل `sound:hello-world`. تُعيد Asterisk كائن `Playback` نحتفظ بـ `id` الخاص به.
3. عندما ينتهي الصوت، تُرسل Asterisk `PlaybackFinished` مع تشغيل الـ `id` ذلك؛ نبحث عن القناة ونقطعها.
4. قطع الاتصال يجعل القناة تغادر Stasis، مُنتِجًا حدث `StasisEnd`.

> **ملاحظة حول مكتبات العميل.** هناك غلاف عالي المستوى يُدعى `ari-py` (حزمة `ari`) موجود، لكنه غير مُصان وقد كُتب لعصر أقدم من Python وأدوات Swagger. للعمل الجديد على Asterisk 22، يُفضَّل النهج الصريح `requests` + WebSocket الموضح أعلاه، أو مكتبة asyncio مثل `asyncari` إذا كنت تحتاج إلى التزامن. النهج الخام يبقيك قريبًا من استدعاءات REST الفعلية والأحداث، وهو بالضبط ما تريده أثناء تعلم ARI.

## externalMedia: the door to AI and voicebots

الموارد المذكورة أعلاه تسمح لك بتشغيل وتسجيل *الملفات*. لكن تطبيقات الصوت الحديثة — تحويل الكلام إلى نص، روبوتات الصوت المدعومة بالذكاء الاصطناعي، التحليلات في الوقت الحقيقي — تحتاج إلى *تدفق الصوت الحي* للمكالمة يُرسل إلى عملية خارجية، وتحتاج إلى حقن الصوت مرة أخرى.

ARI يوفر ذلك عبر **`externalMedia` channel**. طلب `POST /ari/channels/externalMedia` ينشئ قناة خاصة، بدلاً من التحدث إلى هاتف، تقوم ببث وسائط RTP للمكالمة إلى (ومن) مضيف خارجي. تقوم بربط هذه القناة مع قناة المتصل، والآن برنامجك الخارجي يكون في مسار الصوت: يتلقى صوت المتصل كـ RTP ويمكنه إرسال صوت مُصنّع مرة أخرى.

يتطلب الطلب فقط:

- `app` — تطبيق Stasis الذي يمتلك القناة الجديدة.
- `format` — تنسيق الصوت، مثل `ulaw` أو `slin16`.

`external_host` (الـ `host:port` لتطبيق الوسائط الخاص بك) اختياري في المخطط — قد يكون فارغًا لاتصال على نمط خادم WebSocket — ولكن بالنسبة لروبوت صوتي RTP كلاسيكي ستقوم بتزويده. المعامل `encapsulation` ي默认 إلى `rtp` و`transport` إلى `udp`، وهو بالضبط ما تحتاجه لنقطة نهاية وسائط بث.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

هذه الميزة الوحيدة هي ما يحول Asterisk إلى واجهة أمامية للذكاء الاصطناعي: شبكة الهاتف تنتهي على Asterisk، ARI يدير المكالمة، و`externalMedia` ينقل الصوت إلى محرك الكلام/الذكاء الاصطناعي ويعيده. هذا هو الآلية التي تُبنى عليها خدمات الذكاء الاصطناعي وروبوتات الصوت.

## Summary

ARI هو الواجهة الحديثة الموصى بها لبناء تطبيقات الاتصالات على Asterisk 22. فهو يفصل العمل بوضوح: Asterisk هو محرك الوسائط، وتطبيقك — يتحدث JSON عبر HTTP وWebSocket — يوفر منطق التحكم في المكالمات. تقوم بتمكينه من خلال `http.conf` (خادم الويب المدمج على المنفذ 8088) و`ari.conf` (الذي يشغل ARI ويعرّف المستخدمين).

تطبيق dialplan `Stasis()` يسلم قناة لتطبيقك، مرفّعًا `StasisStart` عند دخوله و`StasisEnd` عند خروجه. من هناك تقوم بالتعامل مع مجموعة صغيرة من موارد REST — القنوات، الجسور، التشغيلات، التسجيلات، النقاط الطرفية، وحالات الأجهزة — للإجابة، التشغيل، التسجيل، الجسر، وإنهاء المكالمة.

قمنا بإنشاء تطبيق Stasis بسيط بلغة Python يجيب على مكالمة، يشغل تنبيهًا، ثم ينهى المكالمة، ورأينا كيف تقوم قناة `externalMedia` ببث RTP مباشر إلى برنامج خارجي — الأساس لتكاملات الذكاء الاصطناعي وروبوتات الصوت.

## Quiz

1. ARI was introduced in which version of Asterisk?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. In the ARI model, Asterisk acts as a media engine while your external application provides the call-control logic.
   - A. True
   - B. False
3. ARI uses two transports together. Which pair is correct?
   - A. A REST/HTTP API for issuing commands and a WebSocket stream for receiving events
   - B. A TCP line protocol and a stdin/stdout script
   - C. SNMP and SMTP
   - D. Two separate UDP sockets
4. Which two configuration files must be set up to enable ARI?
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. The conventional TCP port for the Asterisk HTTP server (and therefore ARI) is ____.
6. Which dialplan application hands a channel over to an ARI application?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. When a channel enters a Stasis application, which event is sent to the connected client?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. Which ARI request creates a mixing point that can join two or more channels together?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. To play a built-in prompt on a channel, which event tells your application that the audio has finished so it can move on?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. The `externalMedia` channel is primarily used to:
    - A. Record a call to a local WAV file
    - B. Stream the call's live audio (RTP) to and from an external application, e.g. an AI/speech engine
    - C. Register a PJSIP endpoint
    - D. Reload the dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
