# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) वेब ब्राउज़र को बिना किसी प्लगइन और बिना किसी बाहरी softphone के कॉल करने और प्राप्त करने की सुविधा देता है — बस JavaScript, एक माइक्रोफ़ोन और Asterisk के साथ एक सुरक्षित कनेक्शन की आवश्यकता होती है। Asterisk, Asterisk 11 के बाद से ही WebRTC सर्वर के रूप में कार्य करने में सक्षम है, और Asterisk 12 में PJSIP स्टैक (`res_pjsip`) के आने के बाद से यह इसे करने का अनुशंसित तरीका रहा है; Asterisk 22 में कॉन्फ़िगरेशन कुछ चुनिंदा और अच्छी तरह से समझे गए विकल्पों तक सीमित हो गया है। यह अध्याय दिखाता है कि कैसे एक PJSIP endpoint को ब्राउज़र फ़ोन में बदला जाए, सुरक्षित मीडिया पाथ कैसे काम करता है, और आपको कब Asterisk के इन-बिल्ट WebRTC सपोर्ट का उपयोग करना चाहिए और कब एक समर्पित गेटवे का।

इस अध्याय की हर चीज़ को पुस्तक की Asterisk 22 लैब के विरुद्ध सत्यापित किया गया है; दिखाया गया कॉन्फ़िगरेशन `lab/asterisk/etc` में दिए गए कॉन्फ़िगरेशन जैसा ही है।

## उद्देश्य

इस अध्याय के अंत तक, आप निम्न में सक्षम होंगे:

- यह समझाना कि WebRTC, Asterisk में क्या जोड़ता है और इसका उपयोग कब करना है
- यह वर्णन करना कि WebRTC मीडिया सुरक्षा (DTLS-SRTP) और ICE, सामान्य SIP से कैसे भिन्न हैं
- Asterisk HTTP सर्वर और सुरक्षित WebSocket (`wss`) endpoint को सक्षम करना
- एक `wss` PJSIP ट्रांसपोर्ट और `webrtc=yes` के साथ एक WebRTC endpoint को कॉन्फ़िगर करना
- एक ब्राउज़र softphone (SIP.js) को कनेक्ट करना और कॉल करना
- Asterisk-native WebRTC और Janus जैसे मीडिया गेटवे के बीच निर्णय लेना

## Asterisk के साथ WebRTC क्यों

Asterisk के दृष्टिकोण से, एक WebRTC endpoint केवल एक और PJSIP endpoint है। जो बदलता है वह यह है कि ब्राउज़र उस तक *कैसे* पहुँचता है और मीडिया को कैसे सुरक्षित किया जाता है। सामान्य उपयोगों में शामिल हैं:

- वेबसाइट पर **Click-to-call** — एक विज़िटर वेब पेज से किसी queue या extension को कॉल करता है।
- **Web-based agents** — एक कांटेक्ट-सेंटर एजेंट पूरी तरह से ब्राउज़र में काम करता है, जिसे इंस्टॉल या अपडेट करने के लिए किसी डेस्कटॉप softphone की आवश्यकता नहीं होती।
- आपके अपने वेब एप्लिकेशन में **Embedded calling** — उदाहरण के लिए, SipPulse वेब softphone जो Asterisk से बात करता है।
- **Zero-install internal phones** — कर्मचारी हार्डवेयर फ़ोन या इंस्टॉल किए गए क्लाइंट के बजाय ब्राउज़र टैब का उपयोग करते हैं।

इसका सबसे बड़ा लाभ इसकी पहुँच है: हर आधुनिक ब्राउज़र पहले से ही WebRTC का समर्थन करता है। इसकी कीमत यह है कि WebRTC सख्त है — यह एन्क्रिप्टेड मीडिया और एक सुरक्षित ट्रांसपोर्ट की *मांग* करता है, इसलिए सामान्य UDP SIP फ़ोन की तुलना में इसे कॉन्फ़िगर करने के लिए अधिक काम करना पड़ता है।

## WebRTC, सामान्य SIP से कैसे भिन्न है

एक सामान्य SIP फ़ोन UDP/TCP पर सिग्नलिंग करता है और आमतौर पर ऑडियो को सामान्य RTP के रूप में ले जाता है। एक WebRTC ब्राउज़र क्लाइंट तीन महत्वपूर्ण तरीकों से अलग है, और Asterisk को प्रत्येक से मेल खाना पड़ता है:

- **सिग्नलिंग WebSocket पर चलती है।** UDP पोर्ट 5060 पर SIP के बजाय, ब्राउज़र Asterisk के इन-बिल्ट HTTP सर्वर के लिए एक सुरक्षित WebSocket (`wss://`) खोलता है। SIP संदेश उस WebSocket के अंदर यात्रा करते हैं।
- **मीडिया हमेशा DTLS-SRTP के साथ एन्क्रिप्टेड होता है।** ब्राउज़र सामान्य RTP को अस्वीकार कर देते हैं। दोनों पक्ष एक DTLS हैंडशेक (SDP में आदान-प्रदान किए गए सर्टिफिकेट फिंगरप्रिंट द्वारा प्रमाणित) करते हैं और उससे SRTP कुंजियाँ प्राप्त करते हैं।
- **कनेक्टिविटी ICE के साथ नेगोशिएट की जाती है।** एक पहुँच योग्य IP और पोर्ट मानने के बजाय, दोनों पक्ष उम्मीदवार पते (host, STUN-reflexive, TURN-relayed) एकत्र करते हैं और तब तक उनकी जाँच करते हैं जब तक कि कोई काम न कर जाए। RTP और RTCP आमतौर पर एक ही पोर्ट (`rtcp_mux`) पर मल्टीप्लेक्स किए जाते हैं।

अच्छी खबर: Asterisk 22 में एक एकल endpoint विकल्प, `webrtc=yes`, इन सभी को उचित डिफ़ॉल्ट के साथ चालू कर देता है। हम देखेंगे कि यह वास्तव में क्या सेट करता है।

## चरण 1 — HTTP सर्वर और WebSocket

WebRTC सिग्नलिंग Asterisk के इन-बिल्ट HTTP सर्वर द्वारा परोसी जाती है (`res_http_websocket` इस पर `/ws` पाथ को एक्सपोज़ करता है)। ब्राउज़र को एक *सुरक्षित* WebSocket की आवश्यकता होती है, इसलिए हम TLS को सक्षम करते हैं। `http.conf` को संपादित करें:

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

रीलोड (`module reload res_http_websocket` या रीस्टार्ट) करें और पुष्टि करें:

```
*CLI> http show status
HTTP Server Status:
Server: Asterisk/22.10.0
Server Enabled and Bound to 0.0.0.0:8088

HTTPS Server Enabled and Bound to 0.0.0.0:8089

Enabled URI's:
/ws => Asterisk HTTP WebSocket
```

ब्राउज़र `wss://your-asterisk:8089/ws` से कनेक्ट होगा।

### सर्टिफिकेट के बारे में

यहाँ TLS सर्टिफिकेट *WebSocket* (सिग्नलिंग चैनल) को सुरक्षित करता है। लैब में एक सेल्फ-साइन्ड सर्टिफिकेट ठीक है — आप इसे ब्राउज़र में एक बार स्वीकार करते हैं। प्रोडक्शन में एक वास्तविक सर्टिफिकेट (उदाहरण के लिए Let's Encrypt) का उपयोग करें जिसका नाम उस होस्ट से मेल खाता हो जिससे ब्राउज़र कनेक्ट होता है, अन्यथा ब्राउज़र WebSocket को अस्वीकार कर देगा।

लैब के लिए, `lab/make-certs.sh` `CN=localhost` (प्लस `localhost`/`127.0.0.1` SANs) के साथ एक सेल्फ-साइन्ड सर्टिफिकेट उत्पन्न करता है और इसे `asterisk/etc/keys/` में लिखता है। सार्वजनिक तैनाती के लिए, इसके बजाय एक वास्तविक सर्टिफिकेट प्राप्त करें — उदाहरण के लिए Let's Encrypt के साथ:

```
certbot certonly --standalone -d voip.example.com
```

फिर `http.conf` को जारी की गई फ़ाइलों पर इंगित करें और `res_http_websocket` को रीलोड करें:

```
tlscertfile=/etc/letsencrypt/live/voip.example.com/fullchain.pem
tlsprivatekey=/etc/letsencrypt/live/voip.example.com/privkey.pem
```

सुनिश्चित करें कि सर्टिफिकेट का नाम उस होस्ट से मेल खाता है जिससे ब्राउज़र कनेक्ट होता है, और इसके समाप्त होने से पहले इसे नवीनीकृत करें (certbot का टाइमर इसे स्वचालित रूप से करता है), अन्यथा WebSocket विफल हो जाएगा।

यह सर्टिफिकेट मीडिया को एन्क्रिप्ट करने के लिए उपयोग किए जाने वाले DTLS सर्टिफिकेट के समान **नहीं** है — Asterisk इसे स्वचालित रूप से उत्पन्न करता है, जैसा कि हम देखेंगे।

## चरण 2 — WSS ट्रांसपोर्ट

PJSIP को `wss` प्रकार के ट्रांसपोर्ट की आवश्यकता होती है। इसे `pjsip.conf` में जोड़ें:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

सत्यापित करें कि यह लोड हो गया है:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

`wss` ट्रांसपोर्ट के लिए दिखाए गए `0.0.0.0:5060` से भ्रमित न हों — WebSocket को पोर्ट 5060 पर सर्व **नहीं** किया जाता है। WebRTC सिग्नलिंग उस HTTP सर्वर द्वारा सर्व की जाती है जिसे आपने चरण 1 में कॉन्फ़िगर किया था (`wss` के लिए पोर्ट 8089)। PJSIP `wss` ट्रांसपोर्ट `res_http_websocket` पर एक पतला आवरण है, इसलिए इसके लिए प्रिंट किया गया `bind` पता कॉस्मेटिक है और इसे अनदेखा किया जा सकता है; जो पोर्ट मायने रखता है वह `http.conf` में `tlsbindaddr` है।

## चरण 3 — WebRTC endpoint

अब endpoint की बात करते हैं। कुंजी `webrtc=yes` है:

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
auth_type=userpass
username=webrtc-1000
password=Lab-webrtc-secret

[webrtc-1000]
type=aor
max_contacts=1
```

`webrtc=yes` एक सुविधा स्विच है। यह WebRTC-आवश्यक सभी विकल्पों को मैन्युअल रूप से सेट करने के बराबर है। आप पुष्टि कर सकते हैं कि इसने वास्तव में क्या चालू किया है:

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

उस आउटपुट को पढ़ना:

- `media_encryption: dtls` और `dtls_auto_generate_cert: Yes` — मीडिया DTLS-SRTP है, और Asterisk स्वचालित रूप से DTLS सर्टिफिकेट उत्पन्न करता है, इसलिए आप स्वयं एक नहीं बनाते हैं। फिंगरप्रिंट का विज्ञापन SDP (`SHA-256`) में किया जाता है।
- `ice_support: true` — Asterisk ICE उम्मीदवारों को इकट्ठा और नेगोशिएट करता है।
- `rtcp_mux: true` — RTP और RTCP एक पोर्ट साझा करते हैं, जैसा कि ब्राउज़र अपेक्षा करते हैं।
- `use_avpf: true` — AVPF RTP प्रोफ़ाइल (फीडबैक), जो WebRTC द्वारा आवश्यक है।

`allow=opus` अनुशंसित है — Opus वह कोडेक है जिसे ब्राउज़र पसंद करते हैं। Asterisk 22 कोर में Opus *passthrough* (`res_format_attr_opus` मॉड्यूल) के साथ आता है, जो बिना री-एनकोडिंग के दो Opus-सक्षम लेग्स के बीच Opus को रिले करने के लिए पर्याप्त है। Opus को किसी अन्य कोडेक में *ट्रांसकोड* करने के लिए अलग `codec_opus` मॉड्यूल की आवश्यकता होती है, जिसे आधिकारिक WebRTC गाइड वैकल्पिक लेकिन अत्यधिक अनुशंसित के रूप में सूचीबद्ध करता है और जिसे आप बेस बिल्ड के ऊपर इंस्टॉल करते हैं; *Designing a VoIP network* में कोडेक चर्चा देखें। गैर-WebRTC लेग्स के साथ ब्रिजिंग के लिए `ulaw` को फॉलबैक के रूप में रखें जो Opus नहीं बोल सकते।

## चरण 4 — ICE, STUN और TURN

एक फ्लैट LAN पर, होस्ट उम्मीदवारों के साथ ICE पर्याप्त है और किसी अन्य चीज़ की आवश्यकता नहीं है। इंटरनेट पर आप आमतौर पर एक STUN सर्वर जोड़ते हैं ताकि Asterisk और ब्राउज़र अपने सार्वजनिक पते खोज सकें, और उन मामलों के लिए एक TURN सर्वर जहाँ सीधा मीडिया असंभव है (symmetric NAT, प्रतिबंधात्मक फ़ायरवॉल)। Asterisk को `rtp.conf` में उन पर इंगित करें:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

ब्राउज़र को JavaScript (`RTCPeerConnection` `iceServers` सूची) में अपने स्वयं के ICE सर्वर के साथ कॉन्फ़िगर किया गया है। पूरी तरह से आंतरिक तैनाती के लिए आप STUN/TURN को पूरी तरह से छोड़ सकते हैं।

`turnaddr` एक वैकल्पिक पोर्ट (डिफ़ॉल्ट `3478`) लेता है; `turnusername` और `turnpassword` रिले के लिए प्रमाणित करते हैं। STUN केवल एक पीयर को अपना सार्वजनिक पता *खोजने* में मदद करता है — जब दोनों छोर symmetric NAT या प्रतिबंधात्मक फ़ायरवॉल के पीछे बैठते हैं, तो सीधा मीडिया असंभव होता है और एक TURN रिले ही एकमात्र ऐसी चीज़ है जो ऑडियो को प्रवाहित करती है।

**प्रोडक्शन अनुशंसा:** एक सार्वजनिक STUN सर्वर (जैसे Google का) पता खोजने के लिए ठीक है, लेकिन वास्तविक ट्रैफ़िक के लिए सार्वजनिक TURN पर भरोसा **न करें** — TURN आपके सभी मीडिया को रिले करता है, इसलिए आप इसे अपने नियंत्रण में रखना चाहते हैं। अपना स्वयं का [coturn](https://github.com/coturn/coturn) सर्वर चलाएं। दीर्घकालिक क्रेडेंशियल्स के साथ एक न्यूनतम `/etc/turnserver.conf` इस तरह दिखता है:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

फिर Asterisk को `rtp.conf` में उस पर इंगित करें:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

ब्राउज़र को उसकी `iceServers` सूची में वही TURN सर्वर दें ताकि दोनों लेग्स रिले कर सकें। मोबाइल नेटवर्क या कॉर्पोरेट फ़ायरवॉल के पीछे उपयोगकर्ताओं के साथ प्रोडक्शन के लिए, एक सेल्फ-होस्टेड coturn अनिवार्य रूप से आवश्यक है।

## चरण 5 — ब्राउज़र क्लाइंट

कोई भी WebRTC SIP लाइब्रेरी काम करती है; दो व्यापक रूप से उपयोग की जाने वाली **SIP.js** और **JsSIP** हैं। लैब में `lab/webrtc/index.html` पर एक न्यूनतम SIP.js softphone शामिल है। आवश्यक हिस्सा ट्रांसपोर्ट URL और क्रेडेंशियल्स हैं:

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

याद रखने के लिए दो ब्राउज़र वास्तविकताएं:

- **सुरक्षित संदर्भ।** `getUserMedia` (माइक्रोफ़ोन एक्सेस) केवल `https://` पेजों या `http://localhost` पर काम करता है। प्रोडक्शन में पेज को HTTPS पर सर्व करें।
- **सर्टिफिकेट को एक बार स्वीकार करें।** सेल्फ-साइन्ड लैब सर्टिफिकेट के साथ, पहले उसी ब्राउज़र में `https://your-asterisk:8089/ws` पर जाएं और चेतावनी स्वीकार करें, अन्यथा WebSocket चुपचाप विफल हो जाएगा।

SipPulse वेब softphone इन्हीं प्रिमिटिव्स पर निर्मित एक प्रोडक्शन-ग्रेड संदर्भ क्लाइंट है।

## WebRTC कॉल को सत्यापित करना

ब्राउज़र के पंजीकृत होने के साथ, `pjsip show contacts` डायनामिक कांटेक्ट दिखाता है, और एक कॉल चैनल को रोशन करती है:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

यदि ऑडियो वन-वे है या अनुपस्थित है, तो यह लगभग हमेशा ICE या सर्टिफिकेट होता है — नीचे समस्या निवारण देखें।

## Asterisk WebRTC बनाम मीडिया गेटवे

Asterisk सीधे WebRTC को समाप्त कर सकता है, लेकिन यह हमेशा सही उपकरण नहीं होता है:

- **Asterisk-native WebRTC का उपयोग करें** जब ब्राउज़र आपके PBX पर एक *फ़ोन* हो — एक एजेंट, एक आंतरिक extension, एक क्लिक-टू-कॉल जो आपके dialplan में आता है। ब्राउज़र बस एक और endpoint है और सब कुछ (queues, voicemail, IVR) काम करता है।
- **एक समर्पित गेटवे (जैसे Janus) का उपयोग करें** जब आपको कॉल नियंत्रण से स्वतंत्र रूप से कई ब्राउज़र सत्रों को स्केल करने, बड़े सम्मेलनों/स्ट्रीमिंग के लिए चयनात्मक अग्रेषण करने, या मीडिया प्लेन को PBX से अलग रखने की आवश्यकता हो। एक गेटवे WebRTC को सामान्य SIP से जोड़ता है, और Asterisk तब एक सामान्य SIP लेग देखता है।

कई वास्तविक सिस्टम दोनों को जोड़ते हैं: कॉल नियंत्रण के लिए Asterisk, ब्राउज़र-साइड मीडिया स्केलिंग के लिए एक गेटवे। (यह SipPulse के अपने स्टैक के पीछे का आर्किटेक्चर है।)

## समस्या निवारण

- **WebSocket कनेक्ट नहीं होगा:** ब्राउज़र ने TLS सर्टिफिकेट को अस्वीकार कर दिया। `https://host:8089/ws` को सीधे खोलें और इसे स्वीकार करें, या एक विश्वसनीय सर्टिफिकेट इंस्टॉल करें।
- **पंजीकरण होता है लेकिन ऑडियो नहीं:** ICE विफल रहा — STUN जोड़ें, और यदि NAT के पार है तो TURN जोड़ें। `pjsip set logger on` की जाँच करें और SDP उम्मीदवारों को देखें।
- **वन-वे ऑडियो:** आमतौर पर एक तरफ NAT/ICE, या बिना किसी सामान्य मिलान वाला कोडेक — सुनिश्चित करें कि `allow=opus,ulaw` है।
- **उत्तर देने पर कॉल ड्रॉप:** DTLS हैंडशेक विफल; पुष्टि करें कि `dtls_auto_generate_cert` `Yes` है और सिस्टम घड़ी सही है (सर्टिफिकेट समय-संवेदनशील होते हैं)।

## लैब

1. `./lab.sh up` चलाएं, फिर `bash lab/make-certs.sh` और Asterisk को रीस्टार्ट करें।
2. `lab/webrtc/index.html` (`lab/webrtc` से `python3 -m http.server`) सर्व करें और इसे खोलें; `https://localhost:8089/ws` पर सर्टिफिकेट स्वीकार करें।
3. `webrtc-1000` के रूप में रजिस्टर करें और `600` (इको टेस्ट) को कॉल करें — आपको खुद को सुनना चाहिए।
4. `6001` के रूप में पंजीकृत SipPulse Softphone से, ब्राउज़र को रिंग करने के लिए `1000` डायल करें।
5. नेगोशिएशन का निरीक्षण करें: `pjsip set logger on`, एक कॉल करें, और SDP में DTLS फिंगरप्रिंट और ICE उम्मीदवार खोजें।

## सारांश

WebRTC एक ब्राउज़र को प्रथम श्रेणी का Asterisk endpoint बनाता है। रेसिपी छोटी लेकिन सख्त है: TLS के साथ HTTP सर्वर को सक्षम करें ताकि ब्राउज़र एक सुरक्षित WebSocket खोल सके, एक `wss` PJSIP ट्रांसपोर्ट जोड़ें, और endpoint पर `webrtc=yes` सेट करें — जो DTLS-SRTP (एक स्वचालित रूप से उत्पन्न सर्टिफिकेट के साथ), ICE, RTP/RTCP मल्टीप्लेक्सिंग और AVPF प्रोफ़ाइल को चालू करता है। NAT को पार करते समय STUN/TURN जोड़ें, अपने पेज को HTTPS पर सर्व करें, और एक SIP.js (या JsSIP) क्लाइंट को `wss://asterisk:8089/ws` पर इंगित करें। अपने PBX पर ब्राउज़र फ़ोन के लिए, Asterisk-native WebRTC सबसे सरल रास्ता है; बड़े पैमाने पर मीडिया के लिए, इसे एक गेटवे के साथ जोड़ें।

## प्रश्नोत्तरी

1. WebRTC ब्राउज़र क्लाइंट Asterisk तक SIP सिग्नलिंग ले जाने के लिए किस ट्रांसपोर्ट का उपयोग करता है?
   - A. पोर्ट 5060 पर सामान्य UDP
   - B. Asterisk के HTTP सर्वर के लिए एक सुरक्षित WebSocket (`wss://`)
   - C. पोर्ट 5061 पर TLS
   - D. पोर्ट 8088 पर एक रॉ TCP सॉकेट

2. ब्राउज़र और Asterisk के बीच WebRTC मीडिया किस तंत्र का उपयोग करके एन्क्रिप्ट किया जाता है?
   - A. SDES-SRTP (SDP में आदान-प्रदान की गई कुंजियाँ)
   - B. DTLS-SRTP (DTLS हैंडशेक से प्राप्त कुंजियाँ)
   - C. IPsec
   - D. सामान्य RTP — WebRTC मीडिया को एन्क्रिप्ट नहीं करता है

3. सही या गलत: जब आप `webrtc=yes` सेट करते हैं, तो आपको मीडिया को एन्क्रिप्ट करने के लिए उपयोग किए जाने वाले DTLS सर्टिफिकेट को मैन्युअल रूप से उत्पन्न और इंस्टॉल करना होगा।

4. लैब का Asterisk HTTP सर्वर WebRTC के लिए **सुरक्षित** WebSocket को किस पोर्ट पर एक्सपोज़ करता है?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. निम्नलिखित में से किसे `webrtc=yes` डिफ़ॉल्ट रूप से चालू करता है? (सभी लागू चुनें।)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. रिक्त स्थान भरें: WebRTC कनेक्टिविटी को नेगोशिएट करता है, जिसमें दोनों पक्ष ________ फ्रेमवर्क का उपयोग करके उम्मीदवार पते (host, STUN-reflexive, TURN-relayed) एकत्र और जांचते हैं।

7. `rtp.conf` में, कौन सी दो सेटिंग्स Asterisk को एक बाहरी सर्वर पर इंगित करती हैं ताकि वह अपना सार्वजनिक पता खोज सके और सीधे रास्ते विफल होने पर मीडिया को रिले कर सके? (सभी लागू चुनें।)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. वह URL पाथ जिसे Asterisk का `res_http_websocket` WebRTC सिग्नलिंग के लिए एक्सपोज़ करता है, वह ________ है।

9. अध्याय के अनुसार, आपको Asterisk-native WebRTC के बजाय समर्पित मीडिया गेटवे (जैसे Janus) के लिए कब जाना चाहिए?
   - A. जब भी किसी ब्राउज़र को कॉल करने की आवश्यकता हो
   - B. जब आपको कॉल नियंत्रण से स्वतंत्र रूप से कई ब्राउज़र मीडिया सत्रों को स्केल करना हो, बड़े सम्मेलनों के लिए चयनात्मक अग्रेषण करना हो, या मीडिया प्लेन को PBX से अलग रखना हो
   - C. केवल जब ब्राउज़र DTLS का समर्थन नहीं करता है
   - D. जब आप चाहते हैं कि ब्राउज़र endpoint के लिए voicemail और IVR काम करें

10. सही या गलत: `getUserMedia` (माइक्रोफ़ोन एक्सेस) किसी भी `http://` पेज पर काम करता है, इसलिए ब्राउज़र softphone को HTTPS पर सर्व करना वैकल्पिक है।

**उत्तर:** 1 — B · 2 — B · 3 — गलत (Asterisk स्वचालित रूप से DTLS सर्टिफिकेट उत्पन्न करता है; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — गलत (सुरक्षित संदर्भ आवश्यक: `getUserMedia` केवल `https://` या `http://localhost` पर काम करता है)
