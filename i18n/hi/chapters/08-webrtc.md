# WebRTC with Asterisk

WebRTC (Web Real-Time Communication) एक वेब ब्राउज़र को बिना किसी प्लगइन और बाहरी सॉफ्टफ़ोन के कॉल करने और प्राप्त करने की सुविधा देता है — केवल जावास्क्रिप्ट, एक माइक्रोफ़ोन, और Asterisk के साथ एक सुरक्षित कनेक्शन। Asterisk ने Asterisk 11 से WebRTC सर्वर के रूप में कार्य करने की क्षमता रखी है, और जब PJSIP स्टैक (`res_pjsip`) Asterisk 12 में आया तो यह इसे करने का अनुशंसित तरीका बन गया; Asterisk 22 में कॉन्फ़िगरेशन कुछ समझ में आने वाले विकल्पों में समेट लिया गया है। यह अध्याय दिखाता है कि कैसे एक PJSIP endpoint को ब्राउज़र फ़ोन में बदला जाए, सुरक्षित मीडिया पाथ कैसे काम करता है, और कब आपको Asterisk के बिल्ट‑इन WebRTC समर्थन की ओर रुख करना चाहिए बनाम एक समर्पित गेटवे।

इस अध्याय की सभी जानकारी पुस्तक के Asterisk 22 लैब के विरुद्ध सत्यापित की गई है; दिखाया गया कॉन्फ़िगरेशन वही है जो `lab/asterisk/etc` में है।

## उद्देश्य

By the end of this chapter, you should be able to:

- समझाएँ कि WebRTC Asterisk में क्या जोड़ता है और इसे कब उपयोग करना चाहिए
- वर्णन करें कि WebRTC मीडिया सुरक्षा (DTLS-SRTP) और ICE साधारण SIP से कैसे अलग हैं
- Asterisk HTTP सर्वर और सुरक्षित WebSocket (`wss`) एंडपॉइंट को सक्षम करें
- एक `wss` PJSIP ट्रांसपोर्ट और `webrtc=yes` के साथ एक WebRTC एंडपॉइंट को कॉन्फ़िगर करें
- एक ब्राउज़र सॉफ्टफ़ोन (SIP.js) को कनेक्ट करें और कॉल करें
- Asterisk-नेटिव WebRTC और Janus जैसे मीडिया गेटवे के बीच चयन करें

## Why WebRTC with Asterisk

A WebRTC endpoint is, from Asterisk's point of view, just another PJSIP endpoint.
What changes is *how* the browser reaches it and how media is secured. Typical
uses include:

- **Click-to-call** on a website — a visitor calls a queue or an extension from a
  web page.
- **Web-based agents** — a contact-center agent works entirely in the browser, no
  desktop softphone to install or update.
- **Embedded calling** in your own web application — for example, the SipPulse web
  softphone talking to Asterisk.
- **Zero-install internal phones** — staff use a browser tab instead of a hardware
  phone or installed client.

The big advantage is reach: every modern browser already speaks WebRTC. The cost
is that WebRTC is strict — it *requires* encrypted media and a secure transport,
so there is more to configure than a plain UDP SIP phone.

## How WebRTC differs from plain SIP

एक सामान्य SIP फ़ोन UDP/TCP पर संकेत देता है और आमतौर पर ऑडियो को plain RTP के रूप में ले जाता है। एक WebRTC ब्राउज़र क्लाइंट तीन महत्वपूर्ण तरीकों से अलग है, और Asterisk को प्रत्येक के साथ मेल खाना पड़ता है:

- **Signaling rides a WebSocket.** Instead of SIP over UDP port 5060, the browser
  opens a secure WebSocket (`wss://`) to Asterisk's built-in HTTP server. SIP
  messages travel inside that WebSocket.
- **Media is always encrypted with DTLS-SRTP.** Browsers refuse plain RTP. The two
  sides perform a DTLS handshake (authenticated by certificate fingerprints
  exchanged in the SDP) and derive SRTP keys from it.
- **Connectivity is negotiated with ICE.** Rather than assuming a reachable IP and
  port, both sides gather candidate addresses (host, STUN-reflexive, TURN-relayed)
  and probe them until one works. RTP and RTCP are usually multiplexed on a single
  port (`rtcp_mux`).

The good news: in Asterisk 22 a single endpoint option, `webrtc=yes`, turns all of
this on with sensible defaults. We will see exactly what it sets.

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

PJSIP को `wss` प्रकार का एक ट्रांसपोर्ट चाहिए। इसे `pjsip.conf` में जोड़ें:

```
[transport-wss]
type=transport
protocol=wss
bind=0.0.0.0
```

लोड हुआ है या नहीं जाँचें:

```
*CLI> pjsip show transports
Transport:  transport-udp             udp      0      0  0.0.0.0:5060
Transport:  transport-wss             wss      0      0  0.0.0.0:5060
```

`0.0.0.0:5060` में दिखाए गए `wss` ट्रांसपोर्ट से भ्रमित न हों — WebSocket **पोर्ट 5060** पर सर्व नहीं किया जाता। WebRTC सिग्नलिंग वह HTTP सर्वर द्वारा सर्व किया जाता है जिसे आपने Step 1 में कॉन्फ़िगर किया था (`wss` के लिए पोर्ट 8089)। PJSIP `wss` ट्रांसपोर्ट `res_http_websocket` के ऊपर एक हल्का शिम है, इसलिए इसके लिए प्रिंट किया गया `bind` पता केवल दिखावे के लिये है और इसे अनदेखा किया जा सकता है; वास्तविक महत्व वाला पोर्ट `tlsbindaddr` है जो `http.conf` में है।

## Step 3 — the WebRTC endpoint

अब endpoint स्वयं। मुख्य है `webrtc=yes`:

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

`webrtc=yes` एक सुविधा स्विच है। यह सभी WebRTC‑आवश्यक विकल्पों को हाथ से सेट करने के बराबर है। आप ठीक‑ठीक देख सकते हैं कि यह क्या चालू करता है:

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

उस आउटपुट को पढ़ते हुए:

- `media_encryption: dtls` और `dtls_auto_generate_cert: Yes` — मीडिया DTLS‑SRTP है, और Asterisk DTLS प्रमाणपत्र स्वतः उत्पन्न करता है, इसलिए आपको खुद से बनाना **ज़रूरी नहीं** है। फ़िंगरप्रिंट SDP (`SHA-256`) में विज्ञापित किया जाता है।
- `ice_support: true` — Asterisk ICE उम्मीदवारों को इकट्ठा करता है और उनका वार्ता करता है।
- `rtcp_mux: true` — RTP और RTCP एक ही पोर्ट साझा करते हैं, जैसा कि ब्राउज़र अपेक्षा करते हैं।
- `use_avpf: true` — AVPF RTP प्रोफ़ाइल (फ़ीडबैक), जो WebRTC के लिए आवश्यक है।

`allow=opus` की सिफ़ारिश की जाती है — Opus वह codec है जिसे ब्राउज़र पसंद करते हैं। Asterisk 22 कोर में Opus *passthrough* (`res_format_attr_opus` मॉड्यूल) के साथ आता है, जो दो Opus‑सक्षम लेग्स के बीच Opus को पुनः‑एन्कोड किए बिना रिले करने के लिए पर्याप्त है। Opus को किसी अन्य codec में *Transcoding* करने के लिए अलग `codec_opus` मॉड्यूल की आवश्यकता होती है, जिसे आधिकारिक WebRTC गाइड वैकल्पिक लेकिन अत्यधिक सिफ़ारिश करता है और जिसे आप बेस बिल्ड के ऊपर स्थापित करते हैं; *Designing a VoIP network* में codecs पर चर्चा देखें। `ulaw` को एक fallback के रूप में रखें ताकि non‑WebRTC लेग्स जो Opus नहीं बोल सकते, उनके साथ ब्रिज किया जा सके।

## Step 4 — ICE, STUN and TURN

On a flat LAN, ICE with host candidates is enough and nothing else is needed. Across
the internet you usually add a STUN server so Asterisk and the browser can discover
their public addresses, and a TURN server for the cases where direct media is
impossible (symmetric NAT, restrictive firewalls). Point Asterisk at them in
`rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
; turnaddr=turn.example.com:3478
; turnusername=...
; turnpassword=...
```

The browser is configured with its own ICE servers in JavaScript (the
`RTCPeerConnection` `iceServers` list). For a purely internal deployment you can skip
STUN/TURN entirely.

`turnaddr` takes an optional port (default `3478`); `turnusername` and `turnpassword`
authenticate to the relay. STUN only helps a peer *discover* its public address — when
both ends sit behind symmetric NAT or a restrictive firewall, direct media is
impossible and a TURN relay is the only thing that makes audio flow.

**Production recommendation:** a public STUN server (such as Google's) is fine for
address discovery, but do **not** rely on public TURN for real traffic — TURN relays
all of your media, so you want it under your control. Run your own
[coturn](https://github.com/coturn/coturn) server. A minimal `/etc/turnserver.conf`
with long-term credentials looks like:

```
listening-port=3478
fingerprint
lt-cred-mech
user=asterisk:Strong-TURN-secret
realm=voip.example.com
external-ip=203.0.113.10
```

Then point Asterisk at it in `rtp.conf`:

```
[general]
icesupport=yes
stunaddr=stun.l.google.com:19302
turnaddr=turn.example.com:3478
turnusername=asterisk
turnpassword=Strong-TURN-secret
```

Give the browser the same TURN server in its `iceServers` list so both legs can relay.
For production with users on mobile networks or behind corporate firewalls, a
self-hosted coturn is effectively mandatory.

## Step 5 — the browser client

Any WebRTC SIP library works; two widely used ones are **SIP.js** and **JsSIP**. The
lab includes a minimal SIP.js softphone at `lab/webrtc/index.html`. The essential
part is the transport URL and the credentials:

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

Two browser realities to remember:

- **Secure context.** `getUserMedia` (microphone access) only works on `https://`
  pages or `http://localhost`. Serve the page over HTTPS in production.
- **Accept the cert once.** With a self-signed lab certificate, visit
  `https://your-asterisk:8089/ws` in the same browser first and accept the warning,
  or the WebSocket will fail silently.

The SipPulse web softphone is a production‑grade reference client built on these same
primitives.

## WebRTC कॉल की पुष्टि करना

ब्राउज़र पंजीकृत होने पर, `pjsip show contacts` डायनेमिक कॉन्टैक्ट दिखाता है, और एक कॉल चैनल को सक्रिय कर देता है:

```
*CLI> pjsip show contacts
  Contact:  webrtc-1000/sip:webrtc-1000@... NonQual Avail
*CLI> core show channels
PJSIP/webrtc-1000-00000001  internal  600  Up  Echo
```

यदि ऑडियो एकतरफा या अनुपलब्ध है, तो यह लगभग हमेशा ICE या प्रमाणपत्र के कारण होता है — नीचे ट्रबलशूटिंग देखें।

## Asterisk WebRTC vs a media gateway

Asterisk सीधे WebRTC को समाप्त कर सकता है, लेकिन यह हमेशा सही उपकरण नहीं होता:

- **Use Asterisk-native WebRTC** जब ब्राउज़र आपके PBX पर *फ़ोन* हो — एक एजेंट, एक आंतरिक एक्सटेंशन, एक click-to-call जो आपके dialplan में पहुँचता है। ब्राउज़र सिर्फ एक और endpoint है और सब कुछ (queues, voicemail, IVR) काम करता है।
- **Use a dedicated gateway (e.g. Janus)** जब आपको कई ब्राउज़र सत्रों को कॉल नियंत्रण से स्वतंत्र रूप से स्केल करना हो, बड़े कॉन्फ्रेंस/स्ट्रीमिंग के लिए selective forwarding करना हो, या मीडिया प्लेन को PBX से अलग रखना हो। एक gateway WebRTC को साधारण SIP से जोड़ता है, और Asterisk फिर एक सामान्य SIP लेग को देखता है।

बहुत से वास्तविक सिस्टम दोनों को मिलाते हैं: कॉल नियंत्रण के लिए Asterisk, ब्राउज़र-साइड मीडिया स्केलिंग के लिए एक gateway। (यह SipPulse के अपने स्टैक के पीछे की आर्किटेक्चर है।)

## समस्या निवारण

- **WebSocket won't connect:** ब्राउज़र ने TLS प्रमाणपत्र को अस्वीकार कर दिया। `https://host:8089/ws` को सीधे खोलें और स्वीकार करें, या एक विश्वसनीय प्रमाणपत्र स्थापित करें।
- **Registers but no audio:** ICE विफल हुआ — यदि NAT के पार है तो STUN जोड़ें, और TURN भी। `pjsip set logger on` की जाँच करें और SDP उम्मीदवारों को देखें।
- **One-way audio:** आमतौर पर एक पक्ष पर NAT/ICE, या कोई कोडेक जिसका सामान्य मिलान नहीं है — सुनिश्चित करें `allow=opus,ulaw`।
- **Call drops at answer:** DTLS हैंडशेक विफल हुआ; पुष्टि करें कि `dtls_auto_generate_cert` `Yes` है और सिस्टम घड़ी सही है (प्रमाणपत्र समय‑संवेदनशील होते हैं)।

## प्रयोगशाला

1. `./lab.sh up` चलाएँ, फिर `bash lab/make-certs.sh` और Asterisk को पुनः प्रारंभ करें।
2. `lab/webrtc/index.html` सर्व करें (`python3 -m http.server` से `lab/webrtc`) और इसे खोलें; `https://localhost:8089/ws` पर प्रमाणपत्र स्वीकार करें।
3. `webrtc-1000` के रूप में पंजीकरण करें और `600` को कॉल करें (इको परीक्षण) — आपको अपनी आवाज़ सुनाई देनी चाहिए।
4. SipPulse Softphone से, जो `6001` के रूप में पंजीकृत है, ब्राउज़र को बजाने के लिए `1000` डायल करें।
5. वार्ता की जाँच करें: `pjsip set logger on`, एक कॉल रखें, और SDP में DTLS फ़िंगरप्रिंट और ICE उम्मीदवार खोजें।

## सारांश

WebRTC एक ब्राउज़र को प्रथम‑श्रेणी का Asterisk endpoint बना देता है। यह विधि छोटी लेकिन सख्त है: HTTP सर्वर को TLS के साथ सक्षम करें ताकि ब्राउज़र एक सुरक्षित WebSocket खोल सके, एक `wss` PJSIP ट्रांसपोर्ट जोड़ें, और endpoint पर `webrtc=yes` सेट करें — जो DTLS‑SRTP (एक स्वतः‑जनित प्रमाणपत्र के साथ), ICE, RTP/RTCP मल्टीप्लेक्सिंग और AVPF प्रोफ़ाइल को सक्रिय करता है। NAT को पार करने पर STUN/TURN जोड़ें, अपना पृष्ठ HTTPS पर सर्व करें, और एक SIP.js (या JsSIP) क्लाइंट को `wss://asterisk:8089/ws` की ओर इंगित करें। आपके PBX पर ब्राउज़र फ़ोन के लिए, Asterisk‑नेटिव WebRTC सबसे सरल मार्ग है; बड़े‑पैमाने पर मीडिया के लिए, इसे एक गेटवे के साथ जोड़ें।

## Quiz

1. Which transport does a WebRTC browser client use to carry SIP signaling to
   Asterisk?
   - A. Plain UDP on port 5060
   - B. A secure WebSocket (`wss://`) to Asterisk's HTTP server
   - C. TLS on port 5061
   - D. A raw TCP socket on port 8088

2. WebRTC media between the browser and Asterisk is encrypted using which mechanism?
   - A. SDES-SRTP (keys exchanged in the SDP)
   - B. DTLS-SRTP (keys derived from a DTLS handshake)
   - C. IPsec
   - D. Plain RTP — WebRTC does not encrypt media

3. True or false: when you set `webrtc=yes`, you must manually generate and install
   the DTLS certificate used to encrypt the media.

4. On which port does the lab's Asterisk HTTP server expose the **secure** WebSocket
   for WebRTC?
   - A. 5060
   - B. 5061
   - C. 8088
   - D. 8089

5. Which of the following does `webrtc=yes` turn on by default? (Choose all that
   apply.)
   - A. `media_encryption: dtls`
   - B. `ice_support: true`
   - C. `rtcp_mux: true`
   - D. `use_avpf: true`
   - E. `transport: transport-udp`

6. Fill in the blank: WebRTC negotiates connectivity by having both sides gather and
   probe candidate addresses (host, STUN-reflexive, TURN-relayed) using the
   ________ framework.

7. In `rtp.conf`, which two settings point Asterisk at an external server so it can
   discover its public address and relay media when direct paths fail? (Choose all
   that apply.)
   - A. `icesupport=yes`
   - B. `stunaddr=`
   - C. `turnaddr=`
   - D. `tlsbindaddr=`

8. The URL path that Asterisk's `res_http_websocket` exposes for WebRTC signaling is
   ________.

9. According to the chapter, when should you reach for a dedicated media gateway
   (such as Janus) instead of Asterisk-native WebRTC?
   - A. Whenever any browser needs to make a call
   - B. When you must scale many browser media sessions independently of call
     control, do selective forwarding for large conferences, or keep the media plane
     separate from the PBX
   - C. Only when the browser does not support DTLS
   - D. When you want voicemail and IVR to work for the browser endpoint

10. True or false: `getUserMedia` (microphone access) works on any `http://` page, so
    serving the browser softphone over HTTPS is optional.

**Answers:** 1 — B · 2 — B · 3 — False (Asterisk auto-generates the DTLS cert; `dtls_auto_generate_cert: Yes`) · 4 — D · 5 — A, B, C, D · 6 — ICE · 7 — B, C · 8 — `/ws` · 9 — B · 10 — False (secure context required: `getUserMedia` only works on `https://` or `http://localhost`)
