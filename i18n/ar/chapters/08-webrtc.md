# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) lets a web browser place and receive calls
with no plugin and no external softphone — just JavaScript, a microphone, and a
secure connection to Asterisk. Asterisk has been able to act as a WebRTC server
since Asterisk 11, and since the PJSIP stack (`res_pjsip`) arrived in Asterisk 12
it has been the recommended way to do it; in Asterisk 22 the configuration has settled into a
handful of well-understood options. This chapter shows how to turn a PJSIP
endpoint into a browser phone, how the secure media path works, and when you
should reach for Asterisk's built-in WebRTC support versus a dedicated gateway.

Everything in this chapter is verified against the book's Asterisk 22 lab; the
configuration shown is the same one in `lab/asterisk/etc`.

## Objectives

By the end of this chapter, you should be able to:

- Explain what WebRTC adds to Asterisk and when to use it
- Describe how WebRTC media security (DTLS-SRTP) and ICE differ from plain SIP
- Enable the Asterisk HTTP server and the secure WebSocket (`wss`) endpoint
- Configure a `wss` PJSIP transport and a WebRTC endpoint with `webrtc=yes`
- Connect a browser softphone (SIP.js) and place a call
- Decide between Asterisk-native WebRTC and a media gateway such as Janus

## لماذا WebRTC مع Asterisk

نقطة النهاية WebRTC، من منظور Asterisk، هي مجرد نقطة نهاية PJSIP أخرى. ما يتغير هو *كيف* يصل المتصفح إليها وكيف يتم تأمين الوسائط. الاستخدامات النموذجية تشمل:

- **النقر للاتصال** على موقع ويب — يقوم الزائر بالاتصال بطابور أو امتداد من صفحة ويب.
- **الوكلاء عبر الويب** — يعمل وكيل مركز الاتصال بالكامل في المتصفح، دون الحاجة إلى تثبيت أو تحديث برنامج هاتف نرمجي على سطح المكتب.
- **الاتصال المدمج** في تطبيقك الويب الخاص — على سبيل المثال، برنامج الهاتف النرمجي SipPulse يتحدث مع Asterisk.
- **هواتف داخلية بلا تثبيت** — يستخدم الموظفون علامة تبويب المتصفح بدلاً من هاتف مادي أو عميل مثبت.

## كيف يختلف WebRTC عن SIP العادي

هاتف SIP العادي يُرسل الإشارات عبر UDP/TCP وعادةً ما يحمل الصوت كـ RTP عادي. عميل المتصفح WebRTC يختلف بثلاث طرق مهمة، وعلى Asterisk أن يتطابق مع كل منها:

- **الإشارة تُنقل عبر WebSocket.** بدلاً من SIP عبر منفذ UDP 5060، يفتح المتصفح WebSocket آمن (`wss://`) إلى خادم HTTP المدمج في Asterisk. رسائل SIP تنتقل داخل ذلك الـ WebSocket.
- **الوسائط دائمًا مشفرة باستخدام DTLS‑SRTP.** المتصفحات ترفض RTP العادي. الطرفان يقومان بمصافحة DTLS (مُصادقة ببصمات الشهادات المتبادلة في SDP) وتستخرج مفاتيح SRTP منها.
- **الاتصال يتم التفاوض عليه عبر ICE.** بدلاً من افتراض عنوان IP ومنفذ يمكن الوصول إليهما، يجمع الطرفان عناوين مرشحة (مضيف، STUN‑reflexive، TURN‑relayed) ويختبرانها حتى يعمل أحدها. عادةً ما يتم دمج RTP وRTCP على منفذ واحد (`rtcp_mux`).

الأخبار السارة: في Asterisk 22 خيار نقطة النهاية الواحد، `webrtc=yes`، يُفعِّل كل هذا مع الإعدادات الافتراضية المعقولة. سنرى بالضبط ما يضبطه.

## Step 1 — the HTTP server and the WebSocket

WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket`
exposes the `/ws` path on it). Browsers require a *secure* WebSocket, so we enable
TLS. Edit `http.conf`:

```
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088

; TLS / WSS for WebRTC. Browsers require a secure WebSocket (wss://).
tlsenable=yes
tlsbindaddr=0.0.0.0:8089
tlscertfile=/etc/asterisk/keys/asterisk.crt
tlsprivatekey=/etc/asterisk/keys/asterisk.key
```

Reload (`module reload res_http_websocket` or restart) and confirm:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

The browser will connect to `wss://your-asterisk:8089/ws`.

### About the certificate

The TLS certificate here secures the *WebSocket* (the signaling channel). In a lab
a self-signed certificate is fine — you accept it once in the browser. In
production use a real certificate (for example Let's Encrypt) whose name matches
the host the browser connects to, otherwise the browser will refuse the WebSocket.

For the lab, `lab/make-certs.sh` generates a self-signed certificate with
`CN=localhost` (plus `localhost`/`127.0.0.1` SANs) and writes it to
`asterisk/etc/keys/`. For a public deployment, obtain a real certificate instead — for
example with Let's Encrypt:

```
certbot certonly --standalone -d voip.example.com
```

Then point `http.conf` at the issued files and reload `res_http_websocket`:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

Make sure the certificate name matches the host the browser connects to, and renew it
(certbot's timer does this automatically) before it expires, or the WebSocket will fail.

This certificate is **not** the same as the DTLS certificate used to encrypt the
media — Asterisk generates that one automatically, as we will see.

## Step 2 — the WSS transport

PJSIP needs a transport of type `wss`. Add it to `pjsip.conf`:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

Verify it loaded:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

Do not be misled by the `0.0.0.0:5060` shown for the `wss` transport — the WebSocket
is **not** served on port 5060. WebRTC signaling is served by the HTTP server you
configured in Step 1 (port 8089 for `wss`). The PJSIP `wss` transport is a thin shim
over `res_http_websocket`, so the `bind` address printed for it is cosmetic and can be
ignored; the port that matters is `tlsbindaddr` in `http.conf`.

## Step 3 — the WebRTC endpoint

Now the endpoint itself. The key is `webrtc=yes`:

```
[webrtc-1000]
type=endpoint
context=internal
disallow=all
allow=opus,ulaw
webrtc=yes
transport=transport-wss
aors=webrtc-1000
auth=webrtc-1000

[webrtc-1000]
type=auth
auth_type=digest
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` is a convenience switch. It is equivalent to setting all of the
WebRTC-required options by hand. You can confirm exactly what it turned on:

```
*CLI> pjsip show endpoint webrtc-1000
 dtls_auto_generate_cert            : Yes
 dtls_fingerprint                   : SHA-256
 dtls_setup                         : actpass
 ice_support                        : true
 media_encryption                   : dtls
 rtcp_mux                           : true
 use_avpf                           : true
 webrtc                             : yes
```

Reading that output:

- `media_encryption: dtls` and `dtls_auto_generate_cert: Yes` — media is DTLS-SRTP,
  and Asterisk auto-generates the DTLS certificate, so you do **not** create one
  yourself. The fingerprint is advertised in the SDP (`SHA-256`).
- `ice_support: true` — Asterisk gathers and negotiates ICE candidates.
- `rtcp_mux: true` — RTP and RTCP share one port, as browsers expect.
- `use_avpf: true` — the AVPF RTP profile (feedback), required by WebRTC.

`allow=opus` is recommended — Opus is the codec browsers prefer. Asterisk 22 ships
Opus *passthrough* in core (the `res_format_attr_opus` module), which is enough to
relay Opus between two Opus-capable legs without re-encoding. *Transcoding* Opus to
another codec requires the separate `codec_opus` module, which the official WebRTC
guide lists as optional but highly recommended and which you install on top of the
base build; see the codecs discussion in *Designing a VoIP network*. Keep `ulaw` as a
fallback for bridging to non-WebRTC legs that cannot speak Opus.

## Step 4 — ICE, STUN and TURN

على شبكة LAN مسطحة، يكفي ICE مع مرشحات المضيف ولا حاجة لأي شيء آخر. عبر
الإنترنت عادةً ما تُضيف خادم STUN حتى يتمكن Asterisk والمتصفح من اكتشاف
عناوينهما العامة، وخادم TURN للحالات التي يكون فيها نقل الوسائط مباشرةً
مستحيلًا (NAT متماثل، جدران نارية مقيدة). وجه Asterisk إليه في
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

يُكوَّن المتصفح بخوادم ICE الخاصة به في JavaScript (قائمة
`RTCPeerConnection` `iceServers`). في حالة نشر داخلي بحت يمكنك تخطي
STUN/TURN تمامًا.

`turnaddr` يأخذ منفذًا اختياريًا (الافتراضي `3478`)؛ `turnusername` و`turnpassword`
يُوثّقان إلى الممر. STUN يساعد النظير فقط على *اكتشاف* عنوانه العام — عندما
يكون الطرفان خلف NAT متماثل أو جدار ناري مقيد، يصبح نقل الوسائط مباشرةً
مستحيلًا ويكون ممر TURN هو الوحيد الذي يسمح بتدفق الصوت.

**توصية للإنتاج:** خادم STUN عام (مثل خادم Google) يكفي لاكتشاف العناوين،
لكن لا **تعتمد** على TURN عام للمرور الفعلي — ممرات TURN تنقل كل وسائطك،
لذلك تريد أن تكون تحت سيطرتك. شغّل خادم
[coturn](https://github.com/coturn/coturn) الخاص بك. مثال على إعداد `/etc/turnserver.conf`
ببيانات اعتماد طويلة الأمد يبدو هكذا:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

ثم وجه Asterisk إليه في `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

امنح المتصفح نفس خادم TURN في قائمة `iceServers` حتى يتمكن كلا الطرفين من التمرير.
للإنتاج مع المستخدمين على شبكات الجوال أو خلف جدران نارية مؤسسية، يكون
coturn المستضاف ذاتيًا ضروريًا فعليًا.

## الخطوة 5 — عميل المتصفح

أي مكتبة WebRTC SIP تعمل؛ اثنتان شائعتان هما **SIP.js** و **JsSIP**. يتضمن المختبر برنامج هاتف SIP.js بسيط في `lab/webrtc/index.html`. الجزء الأساسي هو عنوان URL للنقل والبيانات الاعتمادية:

```javascript
const ua = new SIP.UserAgent({
  uri: SIP.UserAgent.makeURI('sip:webrtc-1000@your-asterisk'),
  transportOptions: { server: 'wss://your-asterisk:8089/ws' },
  authorizationUsername: 'webrtc-1000',
  authorizationPassword: 'Lab-webrtc-secret',
});
await ua.start();
await new SIP.Registerer(ua).register();
// place a call to the echo test
const inviter = new SIP.Inviter(ua, SIP.UserAgent.makeURI('sip:600@your-asterisk'));
await inviter.invite();
```

حقيقتان للمتصفح يجب تذكرهما:

- **السياق الآمن.** `getUserMedia` (الوصول إلى الميكروفون) لا يعمل إلا على صفحات `https://` أو `http://localhost`. قدِّم الصفحة عبر HTTPS في بيئة الإنتاج.
- **قبول الشهادة مرة واحدة.** باستخدام شهادة مختبر موقعة ذاتيًا، قم بزيارة `https://your-asterisk:8089/ws` في المتصفح نفسه أولًا وقبل التحذير، وإلا سيفشل WebSocket بصمت.

برنامج الهاتف الويب SipPulse هو عميل مرجعي من فئة الإنتاج مبني على نفس هذه الأساسيات.

## التحقق من مكالمة WebRTC

مع تسجيل المتصفح، `pjsip show contacts` يُظهر جهة الاتصال الديناميكية، وتُظهر المكالمة القناة:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

إذا كان الصوت أحادي الاتجاه أو غير موجود، فغالبًا ما يكون السبب في ICE أو الشهادة — راجع قسم استكشاف الأخطاء وإصلاحها أدناه.

## Asterisk WebRTC vs a media gateway

Asterisk يمكنه إنهاء WebRTC مباشرةً، لكنه ليس دائمًا الأداة المناسبة:

- **استخدم WebRTC الأصلي في Asterisk** عندما يكون المتصفح *هاتفًا* على نظام PBX الخاص بك — وكيلًا، امتدادًا داخليًا، أو زر نقر للاتصال ينتقل إلى مخطط الاتصال الخاص بك. المتصفح هو مجرد نقطة نهاية أخرى وكل شيء (قوائم الانتظار، البريد الصوتي، IVR) يعمل.
- **استخدم بوابة مخصصة (مثل Janus)** عندما تحتاج إلى توسيع عدد كبير من جلسات المتصفح بشكل مستقل عن التحكم في المكالمات، أو تنفيذ تحويل انتقائي لمؤتمرات/بث كبير، أو إبقاء طبقة الوسائط منفصلة عن PBX. البوابة تربط WebRTC بـ SIP العادي، ثم يرى Asterisk طرف SIP عادي.

العديد من الأنظمة الحقيقية تجمع بين الاثنين: Asterisk للتحكم في المكالمات، وبوابة لتوسيع وسائط المتصفح. (هذا هو العمارة وراء مجموعة SipPulse الخاصة.)

## استكشاف الأخطاء وإصلاحها

- **WebSocket won't connect:** المتصفح رفض شهادة TLS. افتح `https://host:8089/ws` مباشرةً وقبلها، أو ثبّت شهادة موثوقة.  
- **Registers but no audio:** فشل ICE — أضف STUN، وTURN إذا كان عبر NAT. تحقق من `pjsip set logger on` وانظر إلى مرشحات SDP.  
- **One-way audio:** عادةً NAT/ICE على جانب واحد، أو ترميز لا يوجد له تطابق مشترك — تأكد من `allow=opus,ulaw`.  
- **Call drops at answer:** فشل مصافحة DTLS؛ تأكد من أن `dtls_auto_generate_cert` هو `Yes` وأن ساعة النظام صحيحة (الشهادات حساسة للوقت).

## المختبر

1. شغّل `./lab.sh up`، ثم `bash lab/make-certs.sh` وأعد تشغيل Asterisk.
2. قدّم `lab/webrtc/index.html` (`python3 -m http.server` من `lab/webrtc`) وافتحه؛ قَبِل الشهادة عند `https://localhost:8089/ws`.
3. سجّل كـ `webrtc-1000` واتصل بـ `600` (اختبار صدى) — يجب أن تسمع صوتك.
4. من برنامج SipPulse Softphone المسجَّل كـ `6001`، اطّلق الرقم `1000` لتجعل المتصفح يرن.
5. افحص التفاوض: `pjsip set logger on`، أجرِ مكالمة، وابحث عن بصمة DTLS ومرشحات ICE في SDP.

## Summary

WebRTC يحول المتصفح إلى نقطة نهاية Asterisk من الدرجة الأولى. الوصفة صغيرة لكنها صارمة: فعّل خادم HTTP مع TLS حتى يتمكن المتصفح من فتح WebSocket آمن، أضف نقل PJSIP `wss`، واضبط `webrtc=yes` على نقطة النهاية — مما يُفعِّل DTLS‑SRTP (مع شهادة مُولَّدة تلقائيًا)، ICE، تعدد RTP/RTCP، وملف تعريف AVPF. أضف STUN/TURN عند عبور NAT، قدِّم صفحتك عبر HTTPS، ووجّه عميل SIP.js (أو JsSIP) إلى `wss://asterisk:8089/ws`. بالنسبة لهواتف المتصفح على PBX الخاص بك، فإن WebRTC الأصلي في Asterisk هو المسار الأبسط؛ بالنسبة للوسائط على نطاق واسع، اجمعه مع بوابة.

## Quiz

1. أي بروتوكول نقل يستخدمه عميل متصفح WebRTC لحمل إشارات SIP إلى
   Asterisk؟
   - A. UDP عادي على المنفذ 5060
   - B. WebSocket آمن (`wss://`) إلى خادم HTTP الخاص بـ Asterisk
   - C. TLS على المنفذ 5061
   - D. مقبس TCP خام على المنفذ 8088

2. وسائط WebRTC بين المتصفح و Asterisk مشفرة باستخدام أي آلية؟
   - A. SDES‑SRTP (المفاتيح يتم تبادلها في SDP)
   - B. DTLS‑SRTP (المفاتيح مستمدة من مصافحة DTLS)
   - C. IPsec
   - D. RTP عادي — WebRTC لا يشفر الوسائط

3. صواب أم خطأ: عندما تقوم بتعيين `webrtc=yes`، يجب عليك إنشاء شهادة DTLS يدوياً وتثبيتها
   المستخدمة لتشفير الوسائط.

4. على أي منفذ يُظهر خادم HTTP الخاص بـ Asterisk في المختبر **WebSocket** الآمن
   لـ WebRTC؟
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. أي مما يلي يتم تشغيله افتراضياً بواسطة `webrtc=yes`؟ (اختر كل ما ينطبق.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. املأ الفراغ: يتفاوض WebRTC على الاتصال من خلال جمع الطرفين
   وفحص عناوين المرشحين (المضيف، STUN‑reflexive، TURN‑relayed) باستخدام
   إطار العمل ________.

7. في `rtp.conf`، أي إعدادين يوجهان Asterisk إلى خادم خارجي حتى يتمكن
   من اكتشاف عنوانه العام وإعادة توجيه الوسائط عندما تفشل المسارات المباشرة؟ (اختر كل ما ينطبق.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. مسار URL الذي يُظهره `res_http_websocket` الخاص بـ Asterisk لإشارات WebRTC هو
   ________.

9. وفقاً للفصل، متى يجب اللجوء إلى بوابة وسائط مخصصة
   (مثل Janus) بدلاً من WebRTC الأصلي في Asterisk؟
   - A. كلما احتاج أي متصفح لإجراء مكالمة
   - B. عندما تحتاج إلى توسيع عدد جلسات وسائط المتصفح بشكل مستقل عن التحكم في المكالمات، وإجراء توجيه انتقائي للمؤتمرات الكبيرة، أو إبقاء طبقة الوسائط منفصلة عن PBX
   - C. فقط عندما لا يدعم المتصفح DTLS
   - D. عندما تريد أن يعمل البريد الصوتي و IVR للمتصفح الطرفي

10. صواب أم خطأ: `getUserMedia` (الوصول إلى الميكروفون) يعمل على أي صفحة `http://`، لذا
    تقديم هاتف المتصفح عبر HTTPS اختياري.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
