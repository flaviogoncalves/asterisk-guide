# The Asterisk REST Interface (ARI)

पिछले अध्याय में AMI और AGI को कवर किया गया था, जो Asterisk पर बाहरी लॉजिक जोड़ने के दो क्लासिक तरीके हैं। दोनों आधुनिक वेब से पहले के हैं: AMI आपको एक TCP सॉकेट पर रॉ, लाइन-ओरिएंटेड इवेंट स्ट्रीम देता है, और AGI कॉल की अवधि के लिए एक सिंगल चैनल को स्क्रिप्ट को सौंपता है। इन्हें उन स्टेटफुल, असिंक्रोनस, मल्टी-चैनल एप्लिकेशनों के लिए डिज़ाइन नहीं किया गया था जो आज लोग बनाते हैं — वेब सर्विसेज़ से बात करने वाले IVR, क्लिक-टू-कल डैशबोर्ड, कॉन्फ्रेंस कंट्रोलर, या आवाज़ बॉट जो ऑडियो को स्पीच इंजन में स्ट्रीम करते हैं।

ARI — The Asterisk REST Interface — को Asterisk 12 में इस अंतर को भरने के लिए पेश किया गया था, और Asterisk 22 में यह नई टेलीफ़ोनी एप्लिकेशन बनाने के लिए अनुशंसित इंटरफ़ेस है। ARI के पीछे विचार एक साफ़ विभाजन है: **Asterisk एक मीडिया इंजन बन जाता है** (यह चैनलों का उत्तर देता है, ब्रिज को मिक्स करता है, ऑडियो प्ले और रिकॉर्ड करता है, DTMF भेजता है), और **आपका एप्लिकेशन सभी कॉल-कंट्रोल लॉजिक को एक REST (HTTP) API और एक WebSocket इवेंट स्ट्रीम के संयोजन के माध्यम से प्रदान करता है**।

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

## What ARI is, and when to use it

ARI दो ट्रांसपोर्ट्स पर आधारित है जो साथ मिलकर काम करते हैं:

- **एक REST (HTTP) API** जिसे आपका एप्लिकेशन *करने* के लिए कॉल करता है — एक चैनल उत्पन्न करना, उसे उत्तर देना, ध्वनि चलाना, एक ब्रिज बनाना, रिकॉर्डिंग शुरू करना, कॉल काटना। ये सामान्य HTTP अनुरोध (`GET`, `POST`, `DELETE`) हैं जो `http://asterisk-host:8088/ari/...` के खिलाफ होते हैं।
- **एक WebSocket इवेंट स्ट्रीम** जिसके माध्यम से Asterisk आपके एप्लिकेशन को बताता है कि क्या हो रहा है — एक चैनल बनाया गया, एक DTMF अंक आया, प्लेबैक समाप्त हुआ, एक चैनल आपके एप्लिकेशन से बाहर चला गया। इवेंट्स JSON ऑब्जेक्ट्स के रूप में भेजे जाते हैं।

यह पैटर्न असिंक्रोनस है: आप एक अनुरोध भेजते हैं, और उस अनुरोध का *परिणाम* आमतौर पर बाद में एक इवेंट के रूप में वापस आता है। उदाहरण के लिए, आप `POST` एक ध्वनि चलाने का अनुरोध; Asterisk तुरंत एक `Playback` ऑब्जेक्ट के साथ उत्तर देता है, और कुछ सेकंड बाद आप एक `PlaybackFinished` इवेंट प्राप्त करते हैं जब ऑडियो समाप्त हो जाता है।

ARI को AMI और AGI पर चुनें जब:

- आपको **चैनल्स और ब्रिजेज़ पर सूक्ष्म नियंत्रण** चाहिए — प्रिमिटिव्स से कॉन्फ्रेंस, पार्किंग, क्यूज़, या कस्टम कॉल फ्लो बनाना, बजाय डायलप्लान एप्लिकेशन्स पर निर्भर रहने के।
- आपका एप्लिकेशन **स्टेटफुल और दीर्घकालिक** है, एक साथ कई चैनल्स रखता है और सभी पर इवेंट्स का जवाब देता है।
- आप **वेब सेवाओं, मैसेज बस, या AI/स्पीच इंजन** के साथ एकीकृत होना चाहते हैं और लाइन प्रोटोकॉल या stdin/stdout स्क्रिप्ट की बजाय JSON over HTTP को प्राथमिकता देते हैं।
- आप **नया प्रोजेक्ट** शुरू कर रहे हैं और वह इंटरफ़ेस चाहते हैं जिसे Asterisk प्रोजेक्ट सक्रिय रूप से सिफ़ारिश करता है।

AMI अभी भी सही टूल है जब आपको केवल सिस्टम को *देखना* है या कभी‑कभी कमांड्स (डायलर्स, वॉलबोर्ड्स, मॉनिटरिंग) भेजने हैं। AGI अभी भी एक तेज़, स्व-निहित IVR स्क्रिप्ट के लिए सुविधाजनक है। लेकिन जो भी चीज़ कॉल्स को समन्वयित करती है, उसके लिए ARI आधुनिक उत्तर है।

> ARI डायलप्लान को प्रतिस्थापित नहीं करता — यह उसे पूरक करता है। एक चैनल सामान्य रूप से डायलप्लान में चलता रहता है जब तक कि वह `Stasis()` एप्लिकेशन तक नहीं पहुँच जाता, तब नियंत्रण आपके ARI एप्लिकेशन को सौंपा जाता है। जब आपका एप्लिकेशन समाप्त हो जाता है, तो चैनल को फिर से डायलप्लान में भेजा जा सकता है या काटा जा सकता है।

## Enabling ARI: http.conf and ari.conf

ARI rides on top of Asterisk's built-in HTTP server, so two configuration files are involved: `http.conf` enables the web server, and `ari.conf` enables ARI and defines its users.

### http.conf

The HTTP server must be enabled and bound to an address and port. The conventional ARI port is **8088**.

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

For production you should put ARI behind TLS. Asterisk can serve HTTPS directly (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), or you can terminate TLS in a reverse proxy in front of port 8088. Over TLS the URLs become `https://` and `wss://` instead of `http://` and `ws://`.

You can confirm the HTTP server is up from the CLI:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` has a `[general]` section and one section per user.

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

A few notes on these options:

- `enabled` turns ARI on or off globally.
- `pretty` formats JSON responses to be human-readable; turn it off in production.
- Each user is a named section with `type=user`.
- `read_only=yes` restricts that user to read-only (GET) requests.
- `password_format` may be `plain` (the password is in plaintext) or `crypt` (a hashed password, generated with `mkpasswd -m sha-512`).
- `permit`, `deny`, and `acl` allow per-user IP restrictions, following the same rules as `acl.conf`.

After editing the files, reload the relevant modules (`module reload res_ari.so` and `module reload http.so`) or restart Asterisk. You can verify ARI is running with:

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

`ari show apps` lists the Stasis applications currently registered by connected clients. It is empty until a client connects, which is exactly what we do next.

### The WebSocket events URL

A client subscribes to the event stream by opening a WebSocket to the `/ari/events` endpoint, naming the Stasis application it implements and passing its credentials:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

The query parameters are:

- `app` — the name of your Stasis application. This is the same name you will use in the dialplan's `Stasis()` call. You may pass several comma-separated names.
- `api_key` — the credentials, in the form `username:password`, matching a user in `ari.conf`.
- `subscribeAll` — optional boolean (default `false`); when `true`, the application receives all events, not just those for resources it owns.

The same `user:pass` credentials are used as HTTP Basic auth on the REST calls (or appended as an `api_key` query parameter there too).

## Stasis: handing a channel to your application

डायलप्लान और ARI के बीच का पुल **`Stasis()`** डायलप्लान एप्लिकेशन है (अंतर्निहित फ्रेमवर्क को भी Stasis कहा जाता है)। जब कोई चैनल `Stasis(appname[,args])` तक पहुँचता है, Asterisk उस चैनल को `appname` के तहत पंजीकृत ARI एप्लिकेशन को सौंप देता है और उसके लिए डायलप्लान का निष्पादन रोक देता है। अब नियंत्रण आपके कोड के पास है।

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

जब चैनल एप्लिकेशन में प्रवेश करता है, तो `hello` के लिए सब्सक्राइब किए सभी जुड़े क्लाइंट्स को WebSocket के माध्यम से एक **`StasisStart`** इवेंट मिलता है, जिसमें पूरा चैनल ऑब्जेक्ट (उसका ID, नाम, कॉलर ID, स्थिति, और `Stasis()` को पास किए गए किसी भी आर्ग्यूमेंट) शामिल होता है। यह आपका संकेत है कि चैनल को नियंत्रित करना शुरू करें।

जब चैनल एप्लिकेशन से बाहर निकलता है — चाहे आपका कोड उसे `continueInDialplan` के साथ डायलप्लान में वापस ले गया हो, या वह हंग अप हो गया हो — आपको एक **`StasisEnd`** इवेंट प्राप्त होता है। `Stasis()` के डायलप्लान में लौटने के बाद वह `STASISSTATUS` चैनल वेरिएबल (`SUCCESS` या `FAILED`) सेट करता है, जिससे डायलप्लान परिणाम के आधार पर शाखा बना सकता है।

## The ARI resource model

ARI exposes Asterisk's internals as a small set of REST resources. Each resource lives under `/ari/<resource>` and is manipulated with standard HTTP methods. The most important ones:

| Resource | What it represents | Example operations |
|----------|--------------------|--------------------|
| **channels** | एकल कॉल लेग | originate, answer, play, record, hangup |
| **bridges** | एक मिश्रण बिंदु जो चैनलों को जोड़ता है | create, add/remove channels, play to the bridge |
| **playbacks** | चल रहा मीडिया प्लेबैक | get status, stop, pause/unpause |
| **recordings** | लाइव और संग्रहीत रिकॉर्डिंग्स | start, stop, list stored, delete |
| **endpoints** | कॉन्फ़िगर किए गए पीयर (PJSIP, आदि) | list, get state, send a message |
| **deviceStates** | कस्टम डिवाइस स्टेट्स | list, get, set, delete |

Some concrete REST calls (paths shown with the `/ari` prefix that appears on the wire):

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

The `media` parameter on a `play` request takes a media URI. The most common form is a `sound:` URI naming a built-in sound, e.g. `sound:hello-world` or `sound:tt-monkeys`. When the audio finishes, Asterisk emits a `PlaybackFinished` event for that playback ID, which is how your application knows it can move on.

Channels and bridges are the two building blocks you combine to make call flows. To connect two callers, for instance, you originate or accept two channels, create a `mixing` bridge with `POST /ari/bridges`, and add both channels to it with `POST /ari/bridges/{bridgeId}/addChannel`. To build a conference, you simply keep adding channels to the same bridge.

## A worked example: a minimal Stasis application

चलिये सबसे छोटा उपयोगी ARI एप्लिकेशन बनाते हैं। जब कोई भी एक्सटेंशन डायल किया जाता है, कॉल हमारे Stasis ऐप में प्रवेश करती है, जो इसे उत्तर देती है, क्लासिक `hello-world` प्रॉम्प्ट चलाती है, और कॉल को समाप्त कर देती है।

### The dialplan

`extensions.conf` में, चैनल को Stasis को भेजें:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

एप्लिकेशन नाम `hello` हमारे द्वारा कनेक्शन के समय उपयोग किए गए `app=hello` से मेल खाता है।

### The Python client

यह क्लाइंट दो प्रसिद्ध लाइब्रेरीज़ का उपयोग करता है: `requests` REST कॉल्स के लिए और `websocket-client` इवेंट स्ट्रीम के लिए। इन्हें `pip install requests websocket-client` के साथ इंस्टॉल करें।

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

स्क्रिप्ट चलाएँ, फिर किसी पंजीकृत एंडपॉइंट से कोई भी नंबर डायल करें। आपको "Hello, world" सुनाई देना चाहिए, जिसके बाद कॉल रिलीज़ हो जाएगी। Asterisk कंसोल पर, `ari show apps` अब `hello` सूचीबद्ध करेगा जबकि क्लाइंट कनेक्टेड है।

फ़्लो को एक बार ट्रेस करना उपयोगी है:

1. डायलप्लान `Stasis(hello)` चलाता है; Asterisk हमारे ऐप को चैनल सौंपता है और एक `StasisStart` इवेंट भेजता है।
2. हम चैनल का उत्तर देते हैं, फिर Asterisk को `sound:hello-world` चलाने के लिए कहते हैं। Asterisk एक `Playback` ऑब्जेक्ट लौटाता है जिसका `id` हम याद रखते हैं।
3. जब ऑडियो समाप्त हो जाता है, Asterisk `PlaybackFinished` के साथ वह प्लेबैक `id` भेजता है; हम चैनल को खोजते हैं और उसे हंग अप करते हैं।
4. हंग अप करने से चैनल Stasis से बाहर निकलता है, जिससे एक `StasisEnd` इवेंट उत्पन्न होता है।

> **A note on client libraries.** एक उच्च-स्तरीय रैपर जिसका नाम `ari-py` (`ari` पैकेज) है, मौजूद है, लेकिन वह अब मेंटेन नहीं किया जाता और पुराने Python और Swagger टूलिंग युग के लिए लिखा गया था। Asterisk 22 पर नए काम के लिए, ऊपर दिखाए गए स्पष्ट `requests` + WebSocket दृष्टिकोण को प्राथमिकता दें, या यदि आपको समवर्तीता चाहिए तो `asyncari` जैसी asyncio लाइब्रेरी का उपयोग करें। रॉ दृष्टिकोण आपको वास्तविक REST कॉल्स और इवेंट्स के करीब रखता है, जो ARI सीखते समय बिल्कुल वही चाहिए होता है।

## externalMedia: the door to AI and voicebots

The resources above let you play and record *files*. But modern voice applications — speech-to-text transcription, AI voicebots, real-time analytics — need the *live audio stream* of a call delivered to an external process, and they need to inject audio back.

ARI provides this through the **`externalMedia` channel**. A `POST /ari/channels/externalMedia` request creates a special channel that, instead of talking to a phone, streams the call's RTP media to (and from) an external host. You bridge this channel with the caller's channel, and now your external program is in the audio path: it receives the caller's audio as RTP and can send synthesized audio back.

The request requires only:

- `app` — the Stasis application that owns the new channel.
- `format` — the audio format, e.g. `ulaw` or `slin16`.

`external_host` (the `host:port` of your media application) is optional in the schema — it may be empty for a WebSocket-server-style connection — but for a classic RTP voicebot you will supply it. The `encapsulation` parameter defaults to `rtp` and `transport` to `udp`, which is exactly what you want for a streaming media endpoint.

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

This single feature is what turns Asterisk into a front-end for AI: the telephone network terminates on Asterisk, ARI orchestrates the call, and `externalMedia` pipes the audio to a speech/AI engine and back. This is the mechanism on which AI services and voicebots are built.

## Summary

ARI is the modern, recommended interface for building telephony applications on Asterisk 22. It splits the work cleanly: Asterisk is the media engine, and your application — speaking JSON over HTTP and a WebSocket — provides the call-control logic. You enable it through `http.conf` (the built-in web server on port 8088) and `ari.conf` (which turns ARI on and defines users).

The `Stasis()` dialplan application hands a channel to your app, raising `StasisStart` when it enters and `StasisEnd` when it leaves. From there you manipulate a small set of REST resources — channels, bridges, playbacks, recordings, endpoints, and device states — to answer, play, record, bridge, and hang up.

We built a minimal Python Stasis app that answers a call, plays a prompt, and hangs up, and we saw how the `externalMedia` channel streams live RTP to an external program — the foundation for AI and voicebot integrations.

## Quiz

1. ARI को किस संस्करण के Asterisk में प्रस्तुत किया गया था?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. ARI मॉडल में, Asterisk एक मीडिया इंजन के रूप में कार्य करता है जबकि आपका बाहरी एप्लिकेशन कॉल‑कंट्रोल लॉजिक प्रदान करता है।
   - A. True
   - B. False
3. ARI दो ट्रांसपोर्ट एक साथ उपयोग करता है। कौन सा जोड़ा सही है?
   - A. A REST/HTTP API for issuing commands and a WebSocket stream for receiving events
   - B. A TCP line protocol and a stdin/stdout script
   - C. SNMP and SMTP
   - D. Two separate UDP sockets
4. ARI को सक्षम करने के लिए किन दो कॉन्फ़िगरेशन फ़ाइलों को सेट अप करना आवश्यक है?
   - A. `manager.conf` and `agi.conf`
   - B. `http.conf` and `ari.conf`
   - C. `sip.conf` and `rtp.conf`
   - D. `modules.conf` and `cdr.conf`
5. Asterisk HTTP सर्वर (और इसलिए ARI) के लिए पारंपरिक TCP पोर्ट ____ है।
6. कौन सा डायलप्लान एप्लिकेशन एक चैनल को ARI एप्लिकेशन को सौंपता है?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. जब एक चैनल Stasis एप्लिकेशन में प्रवेश करता है, तो कौन सा इवेंट कनेक्टेड क्लाइंट को भेजा जाता है?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. कौन सा ARI अनुरोध एक मिक्सिंग पॉइंट बनाता है जो दो या अधिक चैनलों को एक साथ जोड़ सकता है?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. किसी चैनल पर बिल्ट‑इन प्रॉम्प्ट चलाने के बाद, कौन सा इवेंट आपके एप्लिकेशन को बताता है कि ऑडियो समाप्त हो गया है ताकि वह आगे बढ़ सके?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia` चैनल मुख्यतः किस लिए उपयोग किया जाता है:
    - A. Record a call to a local WAV file
    - B. Stream the call's live audio (RTP) to and from an external application, e.g. an AI/speech engine
    - C. Register a PJSIP endpoint
    - D. Reload the dialplan

**Answers:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
