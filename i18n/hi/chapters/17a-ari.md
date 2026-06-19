# The Asterisk REST Interface (ARI)

पिछला अध्याय AMI और AGI के बारे में था, जो Asterisk के साथ बाहरी लॉजिक जोड़ने के दो क्लासिक तरीके हैं। दोनों ही आधुनिक वेब से पहले के हैं: AMI आपको एक TCP सॉकेट पर कच्चा, लाइन-उन्मुख इवेंट स्ट्रीम देता है, और AGI कॉल की अवधि के लिए एक स्क्रिप्ट को एक सिंगल चैनल सौंपता है। इनमें से कोई भी उस तरह के स्टेटफुल, एसिंक्रोनस, मल्टी-चैनल एप्लिकेशन के लिए डिज़ाइन नहीं किया गया था जिन्हें लोग आज बनाते हैं — जैसे IVR जो वेब सेवाओं से बात करते हैं, क्लिक-टू-कॉल डैशबोर्ड, कॉन्फ्रेंस कंट्रोलर, या वॉयसबॉट्स जो ऑडियो को स्पीच इंजन पर स्ट्रीम करते हैं।

ARI — Asterisk REST Interface — को Asterisk 12 में उस कमी को पूरा करने के लिए पेश किया गया था, और Asterisk 22 में नए टेलीफोनी एप्लिकेशन बनाने के लिए यह अनुशंसित इंटरफ़ेस है। ARI के पीछे का विचार चिंताओं का स्पष्ट पृथक्करण है: **Asterisk एक मीडिया इंजन बन जाता है** (यह चैनलों का उत्तर देता है, ब्रिज को मिक्स करता है, ऑडियो चलाता और रिकॉर्ड करता है, DTMF भेजता है), और **आपका एप्लिकेशन एक REST (HTTP) API और एक WebSocket इवेंट स्ट्रीम के संयोजन के माध्यम से सभी कॉल-कंट्रोल लॉजिक प्रदान करता है**।

## उद्देश्य

इस अध्याय के अंत तक, पाठक को यह सक्षम होना चाहिए:

- यह समझाना कि ARI क्या है और यह AMI और AGI से कैसे भिन्न है
- यह तय करना कि किसी प्रोजेक्ट के लिए ARI सही इंटरफ़ेस कब है
- ARI को सक्षम करने और एक उपयोगकर्ता बनाने के लिए `ari.conf` और `http.conf` को कॉन्फ़िगर करना
- ARI WebSocket इवेंट स्ट्रीम से कनेक्ट करना
- Stasis डायलप्लान एप्लिकेशन और `StasisStart`/`StasisEnd` इवेंट्स का वर्णन करना
- ARI रिसोर्स मॉडल का वर्णन करना: चैनल, ब्रिज, प्लेबैक, रिकॉर्डिंग, एंडपॉइंट और डिवाइस स्टेट्स
- पायथन में एक न्यूनतम Stasis एप्लिकेशन लिखना जो एक चैनल का उत्तर देता है, एक ध्वनि बजाता है, और कॉल काट देता है
- यह समझाना कि `externalMedia` चैनल क्या है और यह AI और वॉयसबॉट इंटीग्रेशन के लिए क्यों महत्वपूर्ण है

## ARI क्या है, और इसका उपयोग कब करें

ARI दो ट्रांसपोर्ट्स पर बना है जो एक साथ काम करते हैं:

- **एक REST (HTTP) API** जिसे आपका एप्लिकेशन *कुछ करने* के लिए कॉल करता है — एक चैनल शुरू करना, उसका उत्तर देना, ध्वनि बजाना, ब्रिज बनाना, रिकॉर्डिंग शुरू करना, कॉल काटना। ये `http://asterisk-host:8088/ari/...` के विरुद्ध सामान्य HTTP अनुरोध (`GET`, `POST`, `DELETE`) हैं।
- **एक WebSocket इवेंट स्ट्रीम** जिसके माध्यम से Asterisk आपके एप्लिकेशन को *बताता है* कि क्या हो रहा है — एक चैनल बनाया गया, एक DTMF डिजिट आया, प्लेबैक समाप्त हुआ, एक चैनल ने आपके एप्लिकेशन को छोड़ दिया। इवेंट्स JSON ऑब्जेक्ट्स के रूप में डिलीवर किए जाते हैं।

पैटर्न एसिंक्रोनस है: आप एक अनुरोध करते हैं, और उस अनुरोध का *परिणाम* आमतौर पर बाद में एक इवेंट के रूप में वापस आता है। उदाहरण के लिए, आप ध्वनि बजाने के लिए एक `POST` अनुरोध करते हैं; Asterisk तुरंत एक `Playback` ऑब्जेक्ट के साथ उत्तर देता है, और कुछ सेकंड बाद आपको एक `PlaybackFinished` इवेंट प्राप्त होता है जब ऑडियो पूरा हो जाता है।

ARI को AMI और AGI के ऊपर तब चुनें जब:

- आपको **चैनलों और ब्रिज का सूक्ष्म नियंत्रण** चाहिए — कॉन्फ्रेंस, पार्किंग, कतारें बनाना, या डायलप्लान एप्लिकेशन पर निर्भर रहने के बजाय प्रिमिटिव्स से कस्टम कॉल फ्लो बनाना।
- आपका एप्लिकेशन **स्टेटफुल और लंबे समय तक चलने वाला** है, जो एक साथ कई चैनलों को होल्ड करता है और उन सभी पर इवेंट्स के प्रति प्रतिक्रिया करता है।
- आप **वेब सेवाओं, मैसेज बसों, या AI/स्पीच इंजनों** के साथ एकीकृत करना चाहते हैं और लाइन प्रोटोकॉल या stdin/stdout स्क्रिप्ट के बजाय HTTP पर JSON को प्राथमिकता देते हैं।
- आप एक **नया प्रोजेक्ट** शुरू कर रहे हैं और वह इंटरफ़ेस चाहते हैं जिसकी Asterisk प्रोजेक्ट सक्रिय रूप से अनुशंसा करता है।

AMI अभी भी सही उपकरण है जब आपको केवल सिस्टम का *अवलोकन* करना हो या कभी-कभार कमांड फायर करने हों (डायलर्स, वॉलबोर्ड, मॉनिटरिंग)। AGI अभी भी एक त्वरित, स्व-निहित IVR स्क्रिप्ट के लिए सुविधाजनक है। लेकिन किसी भी ऐसी चीज़ के लिए जो कॉल को व्यवस्थित करती है, ARI आधुनिक उत्तर है।

> ARI डायलप्लान को प्रतिस्थापित नहीं करता है — यह इसका पूरक है। एक चैनल सामान्य रूप से डायलप्लान में चलता है जब तक कि वह `Stasis()` एप्लिकेशन तक नहीं पहुंच जाता, जिस बिंदु पर नियंत्रण आपके ARI एप्लिकेशन को सौंप दिया जाता है। जब आपका एप्लिकेशन काम पूरा कर लेता है, तो चैनल को वापस डायलप्लान में भेजा जा सकता है या काटा जा सकता है।

## ARI को सक्षम करना: http.conf और ari.conf

ARI Asterisk के इन-बिल्ट HTTP सर्वर के ऊपर चलता है, इसलिए दो कॉन्फ़िगरेशन फ़ाइलें शामिल हैं: `http.conf` वेब सर्वर को सक्षम करता है, और `ari.conf` ARI को सक्षम करता है और इसके उपयोगकर्ताओं को परिभाषित करता है।

### http.conf

HTTP सर्वर को सक्षम किया जाना चाहिए और एक पते और पोर्ट से बाउंड होना चाहिए। पारंपरिक ARI पोर्ट **8088** है।

```ini
[general]
enabled=yes
bindaddr=0.0.0.0
bindport=8088
```

प्रोडक्शन के लिए आपको ARI को TLS के पीछे रखना चाहिए। Asterisk सीधे HTTPS सर्व कर सकता है (`tlsenable=yes`, `tlsbindaddr`, `tlscertfile`, `tlsprivatekey`), या आप पोर्ट 8088 के सामने एक रिवर्स प्रॉक्सी में TLS को समाप्त कर सकते हैं। TLS पर URL `http://` और `ws://` के बजाय `https://` और `wss://` बन जाते हैं।

आप CLI से पुष्टि कर सकते हैं कि HTTP सर्वर चालू है:

```
asterisk*CLI> http show status
HTTP Server Status:
Server Enabled and Bound to 0.0.0.0:8088
```

### ari.conf

`ari.conf` में एक `[general]` सेक्शन और प्रति उपयोगकर्ता एक सेक्शन होता है।

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

इन विकल्पों पर कुछ नोट्स:

- `enabled` ARI को वैश्विक स्तर पर चालू या बंद करता है।
- `pretty` JSON प्रतिक्रियाओं को मानव-पठनीय बनाने के लिए फॉर्मेट करता है; प्रोडक्शन में इसे बंद रखें।
- प्रत्येक उपयोगकर्ता `type=user` के साथ एक नामित सेक्शन है।
- `read_only=yes` उस उपयोगकर्ता को केवल-पढ़ने (GET) अनुरोधों तक सीमित करता है।
- `password_format` `plain` (पासवर्ड सादे टेक्स्ट में है) या `crypt` (एक हैशेड पासवर्ड, जिसे `mkpasswd -m sha-512` के साथ उत्पन्न किया गया है) हो सकता है।
- `permit`, `deny`, और `acl` `acl.conf` के समान नियमों का पालन करते हुए, प्रति-उपयोगकर्ता IP प्रतिबंधों की अनुमति देते हैं।

फ़ाइलों को संपादित करने के बाद, संबंधित मॉड्यूल (`module reload res_ari.so` और `module reload http.so`) को पुनः लोड करें या Asterisk को पुनरारंभ करें। आप सत्यापित कर सकते हैं कि ARI चल रहा है:

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

`ari show apps` कनेक्टेड क्लाइंट्स द्वारा वर्तमान में पंजीकृत Stasis एप्लिकेशन को सूचीबद्ध करता है। यह तब तक खाली रहता है जब तक कोई क्लाइंट कनेक्ट नहीं होता, जो कि हम आगे करने जा रहे हैं।

### WebSocket इवेंट्स URL

एक क्लाइंट `/ari/events` एंडपॉइंट पर एक WebSocket खोलकर इवेंट स्ट्रीम की सदस्यता लेता है, उस Stasis एप्लिकेशन का नाम देता है जिसे वह लागू करता है और अपने क्रेडेंशियल्स पास करता है:

```
ws://asterisk-host:8088/ari/events?app=hello&api_key=asterisk:secret
```

क्वेरी पैरामीटर हैं:

- `app` — आपके Stasis एप्लिकेशन का नाम। यह वही नाम है जिसका उपयोग आप डायलप्लान के `Stasis()` कॉल में करेंगे। आप अल्पविराम से अलग किए गए कई नाम पास कर सकते हैं।
- `api_key` — क्रेडेंशियल्स, `username:password` के रूप में, जो `ari.conf` में एक उपयोगकर्ता से मेल खाते हैं।
- `subscribeAll` — वैकल्पिक बूलियन (डिफ़ॉल्ट `false`); जब `true` होता है, तो एप्लिकेशन को सभी इवेंट्स प्राप्त होते हैं, न कि केवल उन संसाधनों के लिए जो उसके स्वामित्व में हैं।

वही `user:pass` क्रेडेंशियल्स REST कॉल पर HTTP बेसिक ऑथ के रूप में उपयोग किए जाते हैं (या वहां भी एक `api_key` क्वेरी पैरामीटर के रूप में जोड़े जाते हैं)।

## Stasis: एक चैनल को अपने एप्लिकेशन को सौंपना

डायलप्लान और ARI के बीच का सेतु **`Stasis()`** डायलप्लान एप्लिकेशन है (अंतर्निहित फ्रेमवर्क को भी Stasis कहा जाता है)। जब कोई चैनल `Stasis(appname[,args])` तक पहुंचता है, तो Asterisk उस चैनल को `appname` के तहत पंजीकृत ARI एप्लिकेशन को सौंप देता है और उसके लिए डायलप्लान निष्पादित करना बंद कर देता है। नियंत्रण अब आपके कोड का है।

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

जब चैनल एप्लिकेशन में प्रवेश करता है, तो `hello` की सदस्यता लेने वाले प्रत्येक कनेक्टेड क्लाइंट को WebSocket पर एक **`StasisStart`** इवेंट प्राप्त होता है, जिसमें पूर्ण चैनल ऑब्जेक्ट (उसकी ID, नाम, कॉलर ID, स्थिति, और `Stasis()` को पास किए गए कोई भी तर्क) होता है। यह चैनल को नियंत्रित करना शुरू करने का आपका संकेत है।

जब चैनल एप्लिकेशन छोड़ता है — क्योंकि आपके कोड ने इसे `continueInDialplan` के साथ वापस डायलप्लान में ले लिया, या क्योंकि इसे काट दिया गया — तो आपको एक **`StasisEnd`** इवेंट प्राप्त होता है। जब `Stasis()` डायलप्लान में वापस आता है तो यह `STASISSTATUS` चैनल वेरिएबल (`SUCCESS` या `FAILED`) सेट करता है, ताकि डायलप्लान परिणाम पर शाखा (branch) कर सके।

## ARI रिसोर्स मॉडल

ARI Asterisk के आंतरिक हिस्सों को REST संसाधनों के एक छोटे सेट के रूप में उजागर करता है। प्रत्येक संसाधन `/ari/<resource>` के अंतर्गत रहता है और मानक HTTP विधियों के साथ हेरफेर किया जाता है। सबसे महत्वपूर्ण हैं:

| संसाधन | यह क्या दर्शाता है | उदाहरण संचालन |
|----------|--------------------|--------------------|
| **channels** | एक सिंगल कॉल लेग | originate, answer, play, record, hangup |
| **bridges** | एक मिक्सिंग पॉइंट जो चैनलों को जोड़ता है | create, add/remove channels, play to the bridge |
| **playbacks** | एक चल रहा मीडिया प्लेबैक | get status, stop, pause/unpause |
| **recordings** | लाइव और संग्रहीत रिकॉर्डिंग | start, stop, list stored, delete |
| **endpoints** | कॉन्फ़िगर किए गए पीयर्स (PJSIP, आदि) | list, get state, send a message |
| **deviceStates** | कस्टम डिवाइस स्टेट्स | list, get, set, delete |

कुछ ठोस REST कॉल (वायर पर दिखाई देने वाले `/ari` उपसर्ग के साथ दिखाए गए पथ):

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

`play` अनुरोध पर `media` पैरामीटर एक मीडिया URI लेता है। सबसे सामान्य रूप एक `sound:` URI है जो एक इन-बिल्ट ध्वनि का नाम देता है, उदा. `sound:hello-world` या `sound:tt-monkeys`। जब ऑडियो समाप्त हो जाता है, तो Asterisk उस प्लेबैक ID के लिए एक `PlaybackFinished` इवेंट उत्सर्जित करता है, जिससे आपके एप्लिकेशन को पता चलता है कि वह आगे बढ़ सकता है।

चैनल और ब्रिज दो बिल्डिंग ब्लॉक्स हैं जिन्हें आप कॉल फ्लो बनाने के लिए जोड़ते हैं। दो कॉलर्स को जोड़ने के लिए, उदाहरण के लिए, आप दो चैनलों को ओरिजिनेट या स्वीकार करते हैं, `POST /ari/bridges` के साथ एक `mixing` ब्रिज बनाते हैं, और `POST /ari/bridges/{bridgeId}/addChannel` के साथ दोनों चैनलों को इसमें जोड़ते हैं। कॉन्फ्रेंस बनाने के लिए, आप बस उसी ब्रिज में चैनल जोड़ते रहते हैं।

## एक कार्यशील उदाहरण: एक न्यूनतम Stasis एप्लिकेशन

आइए सबसे छोटा उपयोगी ARI एप्लिकेशन बनाएं। जब कोई भी एक्सटेंशन डायल किया जाता है, तो कॉल हमारे Stasis ऐप में प्रवेश करती है, जो इसका उत्तर देती है, क्लासिक `hello-world` प्रॉम्प्ट बजाती है, और कॉल काट देती है।

### डायलप्लान

`extensions.conf` में, चैनल को Stasis में भेजें:

```
[from-internal]
exten => _X.,1,Stasis(hello)
 same => n,Hangup()
```

एप्लिकेशन का नाम `hello` उस `app=hello` से मेल खाता है जिसका उपयोग हम कनेक्ट करते समय करते हैं।

### पायथन क्लाइंट

यह क्लाइंट दो प्रसिद्ध लाइब्रेरीज़ का उपयोग करता है: REST कॉल के लिए `requests` और इवेंट स्ट्रीम के लिए `websocket-client`। उन्हें `pip install requests websocket-client` के साथ इंस्टॉल करें।

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

स्क्रिप्ट चलाएं, फिर किसी पंजीकृत एंडपॉइंट से कोई भी नंबर डायल करें। आपको "Hello, world" सुनाई देना चाहिए, जिसके बाद कॉल रिलीज़ हो जाती है। Asterisk कंसोल पर, `ari show apps` अब `hello` को सूचीबद्ध करेगा जबकि क्लाइंट कनेक्टेड है।

प्रवाह को एक बार ट्रेस करना उचित है:

1. डायलप्लान `Stasis(hello)` चलाता है; Asterisk चैनल को हमारे ऐप को सौंप देता है और एक `StasisStart` इवेंट भेजता है।
2. हम चैनल का उत्तर देते हैं, फिर Asterisk को `sound:hello-world` बजाने के लिए कहते हैं। Asterisk एक `Playback` ऑब्जेक्ट लौटाता है जिसकी `id` हमें याद रहती है।
3. जब ऑडियो समाप्त हो जाता है, तो Asterisk उस प्लेबैक `id` के साथ `PlaybackFinished` भेजता है; हम चैनल को देखते हैं और उसे काट देते हैं।
4. कॉल काटने से चैनल Stasis छोड़ देता है, जिससे एक `StasisEnd` इवेंट उत्पन्न होता है।

> **क्लाइंट लाइब्रेरीज़ पर एक नोट।** `ari-py` (`ari` पैकेज) नामक एक उच्च-स्तरीय रैपर मौजूद है, लेकिन यह अप्रचलित है और पायथन और Swagger टूलिंग के पुराने युग के लिए लिखा गया था। Asterisk 22 पर नए काम के लिए, ऊपर दिखाए गए स्पष्ट `requests` + WebSocket दृष्टिकोण को प्राथमिकता दें, या यदि आपको समवर्ती (concurrency) की आवश्यकता है तो `asyncari` जैसी asyncio लाइब्रेरी का उपयोग करें। कच्चा दृष्टिकोण आपको वास्तविक REST कॉल और इवेंट्स के करीब रखता है, जो कि ARI सीखते समय आप वास्तव में चाहते हैं।

## externalMedia: AI और वॉयसबॉट्स का द्वार

उपरोक्त संसाधन आपको *फ़ाइलें* बजाने और रिकॉर्ड करने देते हैं। लेकिन आधुनिक वॉयस एप्लिकेशन — स्पीच-टू-टेक्स्ट ट्रांसक्रिप्शन, AI वॉयसबॉट्स, रीयल-टाइम एनालिटिक्स — को एक कॉल के *लाइव ऑडियो स्ट्रीम* की आवश्यकता होती है जिसे एक बाहरी प्रक्रिया तक पहुंचाया जाए, और उन्हें ऑडियो वापस इंजेक्ट करने की आवश्यकता होती है।

ARI इसे **`externalMedia` चैनल** के माध्यम से प्रदान करता है। एक `POST /ari/channels/externalMedia` अनुरोध एक विशेष चैनल बनाता है जो, फोन से बात करने के बजाय, कॉल के RTP मीडिया को एक बाहरी होस्ट तक (और वहां से) स्ट्रीम करता है। आप इस चैनल को कॉलर के चैनल के साथ ब्रिज करते हैं, और अब आपका बाहरी प्रोग्राम ऑडियो पथ में है: यह कॉलर का ऑडियो RTP के रूप में प्राप्त करता है और सिंथेसाइज्ड ऑडियो वापस भेज सकता है।

अनुरोध के लिए केवल इसकी आवश्यकता होती है:

- `app` — Stasis एप्लिकेशन जो नए चैनल का स्वामी है।
- `format` — ऑडियो फॉर्मेट, उदा. `ulaw` या `slin16`।

`external_host` (आपके मीडिया एप्लिकेशन का `host:port`) स्कीमा में वैकल्पिक है — यह WebSocket-सर्वर-शैली कनेक्शन के लिए खाली हो सकता है — लेकिन एक क्लासिक RTP वॉयसबॉट के लिए आप इसे प्रदान करेंगे। `encapsulation` पैरामीटर डिफ़ॉल्ट रूप से `rtp` और `transport` डिफ़ॉल्ट रूप से `udp` होता है, जो कि स्ट्रीमिंग मीडिया एंडपॉइंट के लिए बिल्कुल वही है जो आप चाहते हैं।

```
POST /ari/channels/externalMedia
    app=hello
    external_host=127.0.0.1:9000
    format=slin16
```

यह एकल विशेषता वह है जो Asterisk को AI के लिए फ्रंट-एंड में बदल देती है: टेलीफोन नेटवर्क Asterisk पर समाप्त होता है, ARI कॉल को व्यवस्थित करता है, और `externalMedia` ऑडियो को स्पीच/AI इंजन तक और वापस पाइप करता है। यह वह तंत्र है जिस पर AI सेवाएं और वॉयसबॉट्स बनाए जाते हैं।

## सारांश

ARI Asterisk 22 पर टेलीफोनी एप्लिकेशन बनाने के लिए आधुनिक, अनुशंसित इंटरफ़ेस है। यह काम को स्पष्ट रूप से विभाजित करता है: Asterisk मीडिया इंजन है, और आपका एप्लिकेशन — HTTP और WebSocket पर JSON बोलकर — कॉल-कंट्रोल लॉजिक प्रदान करता है। आप इसे `http.conf` (पोर्ट 8088 पर इन-बिल्ट वेब सर्वर) और `ari.conf` (जो ARI को चालू करता है और उपयोगकर्ताओं को परिभाषित करता है) के माध्यम से सक्षम करते हैं। `Stasis()` डायलप्लान एप्लिकेशन एक चैनल को आपके ऐप को सौंपता है, प्रवेश करने पर `StasisStart` और छोड़ने पर `StasisEnd` उत्पन्न करता है। वहां से आप REST संसाधनों के एक छोटे सेट — चैनल, ब्रिज, प्लेबैक, रिकॉर्डिंग, एंडपॉइंट और डिवाइस स्टेट्स — का हेरफेर करते हैं ताकि उत्तर दिया जा सके, बजाया जा सके, रिकॉर्ड किया जा सके, ब्रिज किया जा सके और कॉल काटा जा सके। हमने एक न्यूनतम पायथन Stasis ऐप बनाया जो कॉल का उत्तर देता है, एक प्रॉम्प्ट बजाता है, और कॉल काट देता है, और हमने देखा कि कैसे `externalMedia` चैनल लाइव RTP को एक बाहरी प्रोग्राम में स्ट्रीम करता है — जो AI और वॉयसबॉट इंटीग्रेशन के लिए आधार है।

## प्रश्नोत्तरी

1. ARI को Asterisk के किस संस्करण में पेश किया गया था?
   - A. Asterisk 1.4
   - B. Asterisk 11
   - C. Asterisk 12
   - D. Asterisk 18
2. ARI मॉडल में, Asterisk एक मीडिया इंजन के रूप में कार्य करता है जबकि आपका बाहरी एप्लिकेशन कॉल-कंट्रोल लॉजिक प्रदान करता है।
   - A. सही
   - B. गलत
3. ARI एक साथ दो ट्रांसपोर्ट्स का उपयोग करता है। कौन सा जोड़ा सही है?
   - A. कमांड जारी करने के लिए एक REST/HTTP API और इवेंट्स प्राप्त करने के लिए एक WebSocket स्ट्रीम
   - B. एक TCP लाइन प्रोटोकॉल और एक stdin/stdout स्क्रिप्ट
   - C. SNMP और SMTP
   - D. दो अलग-अलग UDP सॉकेट
4. ARI को सक्षम करने के लिए किन दो कॉन्फ़िगरेशन फ़ाइलों को सेट अप किया जाना चाहिए?
   - A. `manager.conf` और `agi.conf`
   - B. `http.conf` और `ari.conf`
   - C. `sip.conf` और `rtp.conf`
   - D. `modules.conf` और `cdr.conf`
5. Asterisk HTTP सर्वर (और इसलिए ARI) के लिए पारंपरिक TCP पोर्ट ____ है।
6. कौन सा डायलप्लान एप्लिकेशन एक चैनल को ARI एप्लिकेशन को सौंपता है?
   - A. `AGI()`
   - B. `Dial()`
   - C. `Stasis()`
   - D. `System()`
7. जब कोई चैनल Stasis एप्लिकेशन में प्रवेश करता है, तो कनेक्टेड क्लाइंट को कौन सा इवेंट भेजा जाता है?
   - A. `ChannelDestroyed`
   - B. `StasisStart`
   - C. `Newchannel`
   - D. `Hangup`
8. कौन सा ARI अनुरोध एक मिक्सिंग पॉइंट बनाता है जो दो या अधिक चैनलों को एक साथ जोड़ सकता है?
   - A. `POST /ari/channels`
   - B. `POST /ari/bridges`
   - C. `GET /ari/endpoints`
   - D. `DELETE /ari/recordings/stored`
9. चैनल पर इन-बिल्ट प्रॉम्प्ट बजाने के लिए, कौन सा इवेंट आपके एप्लिकेशन को बताता है कि ऑडियो समाप्त हो गया है ताकि वह आगे बढ़ सके?
   - A. `PlaybackStarted`
   - B. `DTMFReceived`
   - C. `PlaybackFinished`
   - D. `ChannelTalkingFinished`
10. `externalMedia` चैनल का उपयोग मुख्य रूप से किसके लिए किया जाता है:
    - A. कॉल को स्थानीय WAV फ़ाइल में रिकॉर्ड करना
    - B. कॉल के लाइव ऑडियो (RTP) को एक बाहरी एप्लिकेशन, उदा. AI/स्पीच इंजन तक और वहां से स्ट्रीम करना
    - C. एक PJSIP एंडपॉइंट पंजीकृत करना
    - D. डायलप्लान को पुनः लोड करना

**उत्तर:** 1 — C · 2 — A · 3 — A · 4 — B · 5 — `8088` · 6 — C · 7 — B · 8 — B · 9 — C · 10 — B
