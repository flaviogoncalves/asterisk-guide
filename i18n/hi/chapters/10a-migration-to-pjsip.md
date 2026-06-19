# Migrating from chan_sip to PJSIP: a cookbook

यदि आप इसे Asterisk 13, 16, या 18 बॉक्स के साथ पढ़ रहे हैं जो अभी भी प्रोडक्शन में है, तो आपके पास एक समय-सीमा है। `chan_sip` — जिसे `sip.conf` के माध्यम से कॉन्फ़िगर किया गया मूल SIP चैनल ड्राइवर — **Asterisk 17 में डेप्रिकेट (deprecated) कर दिया गया था, Asterisk 19 में डिफ़ॉल्ट बिल्ड से हटा दिया गया था, और Asterisk 21 में पूरी तरह से डिलीट कर दिया गया था**। यह Asterisk 22 LTS में मौजूद नहीं है। इसे वापस चालू करने के लिए कोई फ्लैग नहीं है, बचने के लिए कोई `noload` नहीं है, और इंस्टॉल करने के लिए कोई पैकेज नहीं है। Asterisk 22 में एकमात्र SIP चैनल ड्राइवर **PJSIP** (`res_pjsip` और `chan_pjsip`) है, जिसे `pjsip.conf` के माध्यम से कॉन्फ़िगर किया जाता है।

इसलिए अधिकांश साइटों के लिए Asterisk 22 में अपग्रेड करना, एक वर्ज़न अपडेट के साथ-साथ एक *SIP माइग्रेशन प्रोजेक्ट* भी है। अच्छी खबर यह है कि वायर पर प्रोटोकॉल नहीं बदलता है — जो फोन कल रजिस्टर और कॉल करता था, वह कल भी करेगा — और Asterisk अनुवाद का पहला 80% काम करने के लिए एक कन्वर्जन टूल प्रदान करता है। यह अध्याय एक व्यावहारिक कुकबुक है: कॉन्सेप्ट मैपिंग, कन्वर्जन स्क्रिप्ट, आपके पास मौजूद मामलों के लिए साइड-बाय-साइड `sip.conf` → `pjsip.conf` अनुवाद, इस बदलाव के साथ आने वाले dialplan और CLI परिवर्तन, realtime (डेटाबेस) माइग्रेशन, और एक चेकलिस्ट के साथ-साथ वे नुकसान जो लोगों को परेशान करते हैं।

यहाँ सब कुछ इस पुस्तक की Asterisk 22.10.0 लैब के विरुद्ध सत्यापित है। `chan_sip` पर गहन लीगेसी सामग्री — और एक मल्टी-डिवाइस `sip.conf` का एंड-टू-एंड कन्वर्जन — *Legacy channels* अध्याय में है; यह अध्याय उसका केंद्रित, रेसिपी-शैली का साथी है।

## Objectives

इस अध्याय के अंत तक, आप निम्नलिखित में सक्षम होंगे:

- यह समझाना कि Asterisk 22 में `chan_sip` क्यों चला गया है और उसकी जगह क्या लेता है
- `sip.conf` पीयर/यूज़र/फ्रेंड मॉडल को PJSIP ऑब्जेक्ट मॉडल (endpoint + aor + auth + identify + transport + registration) पर मैप करना
- `sip_to_pjsip.py` कन्वर्जन स्क्रिप्ट चलाना और उसके आउटपुट की आलोचनात्मक समीक्षा करना
- सामान्य डिवाइस प्रकारों (रजिस्टरिंग फोन, इनबाउंड trunk, आउटबाउंड रजिस्ट्रेशन) को `sip.conf` से `pjsip.conf` में मैन्युअल रूप से अनुवादित करना
- NAT, मीडिया, DTMF, codec, और ऑथेंटिकेशन सेटिंग्स को विकल्प-दर-विकल्प माइग्रेट करना
- dialplan (`SIP/` → `PJSIP/`) और CLI (`sip show` → `pjsip show`) को अपडेट करना
- realtime/ARA डिप्लॉयमेंट को `sippeers`/`sipregs` से Sorcery `ps_*` टेबल्स में माइग्रेट करना
- माइग्रेशन चेकलिस्ट के माध्यम से काम करना और क्लासिक नुकसानों से बचना

## Why migrate at all

`chan_sip` ने लगभग दो दशकों तक Asterisk की सेवा की, लेकिन इसमें आर्किटेक्चरल ऋण था: एक अखंड मॉड्यूल, प्रति डिवाइस एक कॉन्फ़िगरेशन ब्लॉक, कमजोर मल्टी-ट्रांसपोर्ट सपोर्ट, और एक SIP स्टैक जो RFCs से पीछे रह गया था। **PJSIP** — जो Teluu के परिपक्व pjproject स्टैक पर निर्मित है और Asterisk 12 में पेश किया गया था — इसका पूरी तरह से प्रतिस्थापन था। Asterisk 21 तक Asterisk प्रोजेक्ट ने काम पूरा कर लिया और ट्री से `chan_sip` को हटा दिया।

आप किसी भी Asterisk 22 सिस्टम पर स्थिति की पुष्टि कर सकते हैं:

```
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` *0 modules loaded* लौटाता है — यह वहां मौजूद ही नहीं है। PJSIP के अलावा माइग्रेट करने के लिए कुछ भी नहीं है, इसलिए एकमात्र वास्तविक प्रश्न *कैसे* है, *क्या* नहीं।

## The conceptual mapping: there is no single "peer"

`sip.conf` से आने वाले हर व्यक्ति को जो मानसिक बदलाव परेशान करता है, वह यह है: **PJSIP में कोई `[peer]` नहीं है।** `sip.conf` में एक ब्रैकेटेड ब्लॉक — एक `peer`, एक `user`, या एक `friend` — डिवाइस के बारे में *सब कुछ* वर्णित करता था: उसके क्रेडेंशियल्स, उसे कहाँ तक पहुँचना है, उसके codecs, उसका NAT व्यवहार, उसका dialplan context। PJSIP जानबूझकर उस एकल ब्लॉक को कई छोटे, एकल-उद्देश्य वाले ऑब्जेक्ट्स में तोड़ देता है, जिनमें से प्रत्येक को एक `type=` के साथ टैग किया जाता है, जो *एक-दूसरे को नाम से संदर्भित करते हैं*:

| PJSIP object (`type=`) | जिम्मेदारी |
| --- | --- |
| `endpoint` | डिवाइस की कॉल-हैंडलिंग पहचान: codecs, context, DTMF, मीडिया, NAT, और उसके `auth`/`aors`/`transport` के संदर्भ |
| `aor` (Address of Record) | डिवाइस तक *कहाँ* पहुँचना है — रजिस्टर्ड या स्टेटिक कॉन्टैक्ट्स, `max_contacts`, qualify |
| `auth` | इनबाउंड और/या आउटबाउंड ऑथेंटिकेशन के लिए क्रेडेंशियल्स (यूज़रनेम/पासवर्ड) |
| `identify` | इनबाउंड अनुरोध को `From` यूज़र के बजाय **source IP** द्वारा endpoint से मिलाना |
| `transport` | लिसनिंग सॉकेट(s): प्रोटोकॉल, बाइंड एड्रेस/पोर्ट, NAT/एक्सटर्नल एड्रेस |
| `registration` | Asterisk से प्रोवाइडर के लिए एक **आउटबाउंड** REGISTER |

`friend`/`peer`/`user` का अंतर पूरी तरह से गायब हो जाता है — PJSIP में सब कुछ एक `endpoint` है। इसलिए एक एकल `sip.conf` फ्रेंड आमतौर पर तीन ऑब्जेक्ट्स (`endpoint` + `auth` + `aor`) बन जाता है जो एक नाम साझा करते हैं और एक-दूसरे की ओर इशारा करते हैं:

```
                sip.conf                              pjsip.conf
            ┌──────────────┐              ┌──────────┐   ┌──────┐   ┌─────┐
            │   [2000]     │   becomes    │ endpoint │──▶│ auth │   │ aor │
            │ type=friend  │  ─────────▶  │  [2000]  │   │[2000]│   │[2000]│
            │ host=dynamic │              │  auth=───┼──▶└──────┘   └──────┘
            │ secret=...   │              │  aors=───┼───────────────▶ ▲
            └──────────────┘              └────┬─────┘
                                               │ transport=
                                               ▼
                                          ┌───────────┐
                                          │ transport │  (shared by all endpoints)
                                          └───────────┘
```

Endpoint गोंद (glue) है। यह एक `transport` (या डिफ़ॉल्ट इनहेरिट करता है), एक `auth` ऑब्जेक्ट, और एक या अधिक `aors` को नाम देता है। ऑब्जेक्ट मॉडल को *SIP & PJSIP in depth* में गहराई से कवर किया गया है; यहाँ हमें बस हर अनुवाद के लक्ष्य के रूप में इसकी आवश्यकता है।

## The `sip_to_pjsip.py` conversion tool

Asterisk एक Python स्क्रिप्ट प्रदान करता है जो एक मौजूदा `sip.conf` को पढ़ती है और एक `pjsip.conf` लिखती है। यह CLI कमांड के रूप में नहीं चलती है — यह **Asterisk source tree** में रहती है, न कि इंस्टॉल की गई बाइनरीज़ में:

```
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

लैब के Asterisk 22.10.0 पर पूरा पथ, उदाहरण के लिए, `/usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py` है। उसी डायरेक्टरी में `sip_to_pjsql.py` (realtime/SQL वेरिएंट, बाद में कवर किया गया) और हेल्पर मॉड्यूल `astconfigparser.py`, `astdicts.py`, और `sqlconfigparser.py` मौजूद हैं।

### Running it

स्क्रिप्ट वैकल्पिक पोजीशनल आर्गुमेंट्स लेती है — `[input-file [output-file]]` — जो वर्तमान डायरेक्टरी में `sip.conf` और `pjsip.conf` पर डिफ़ॉल्ट होते हैं:

```
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

इसके एकमात्र वास्तविक विकल्प हैं:

```
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

यह इनपुट को पढ़ती है, `Converting to PJSIP...` प्रिंट करती है, और आउटपुट फ़ाइल लिखती है। आंतरिक रूप से यह हर `sip.conf` सेक्शन में जाती है और, प्रति डिवाइस, मिलान वाले `endpoint`, `auth`, `aor`, `registration`, और (जहाँ यह उनका अनुमान लगा सकती है) `transport` ऑब्जेक्ट्स उत्सर्जित करती है, जो अगले सेक्शन में विकल्प मैपिंग को स्वचालित रूप से लागू करती है।

### What it does — and its limits

आउटपुट को **पहला ड्राफ्ट मानें, तैयार फ़ाइल नहीं।** स्क्रिप्ट अपने स्वयं के अंतराल के बारे में ईमानदार है: जो कुछ भी यह स्पष्ट रूप से मैप नहीं कर सकती है, उसे आउटपुट फ़ाइल के शीर्ष पर एक स्पष्ट रूप से फेन्स्ड ब्लॉक में लिखा जाता है:

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[softphone]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

उस वास्तविक अंश में ध्यान दें कि `sip.conf` पीयर से `qualify = yes` *non-mapped* ब्लॉक में चला गया — क्योंकि PJSIP `qualify_frequency` (सेकंड) के साथ **aor** पर क्वालिफाई करता है, न कि डिवाइस पर बूलियन के साथ, स्क्रिप्ट इसे आपके लिए जानबूझकर सेट करने के लिए छोड़ देती है। योजना बनाने के लिए व्यावहारिक सीमाएँ:

- **ट्रांसपोर्ट का अनुमान लगाया जाता है, डिज़ाइन नहीं किया गया।** स्क्रिप्ट `bindport`/`bindaddr` से एक बुनियादी `transport-udp` उत्सर्जित करती है, लेकिन यह आपके TLS certs, आपके TCP आवश्यकताओं, या आपके मल्टी-बाइंड लेआउट को नहीं जान सकती है। ट्रांसपोर्ट की समीक्षा करें और उसे फिर से लिखें।
- **NAT और एक्सटर्नल एड्रेस के लिए एक इंसान की आवश्यकता होती है।** `externaddr`/`localnet` स्पष्ट रूप से जीवित नहीं रह सकते हैं; हाथ से ट्रांसपोर्ट पर `external_media_address`, `external_signaling_address`, और `local_net` की पुष्टि करें।
- **`qualify`, कस्टम टाइमर, और मुट्ठी भर विकल्प "non-mapped" में चले जाते हैं।** उस ब्लॉक को ऊपर से नीचे तक पढ़ें और प्रत्येक के बारे में निर्णय लें।
- **Codec सूचियाँ, कॉन्टेक्स्ट, और सुरक्षा की समीक्षा की आवश्यकता है।** `disallow`/`allow`, dialplan `context` को सत्यापित करें, और यह सुनिश्चित करें कि कोई भी डिवाइस अनजाने में खुला न रह जाए।

इसलिए वर्कफ़्लो यह है: स्क्रिप्ट को एक *scratch* फ़ाइल में चलाएं, उसे diff और रिव्यू करें, अच्छे हिस्सों को अपने वास्तविक `pjsip.conf` में डालें, फिर प्रोडक्शन से पहले पूरी तरह से परीक्षण करें।

## Side-by-side translations

ये रेसिपी हैं। बाईं ओर `sip.conf`, दाईं ओर सत्यापित `pjsip.conf` समकक्ष (पेज की चौड़ाई के लिए यहाँ स्टैक किया गया)। दाईं ओर के हर विकल्प के नाम और मान को `config show help res_pjsip ...` के साथ Asterisk 22 लैब के विरुद्ध चेक किया गया है।

### A registering phone (`host=dynamic`)

सबसे आम डिवाइस: एक डेस्क फोन या softphone जो एक secret के साथ लॉग इन करता है और अपना स्थान रजिस्टर करता है।

**Legacy `sip.conf`:**

```
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

**Asterisk 22 `pjsip.conf`:**

```
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

मुख्य कदम: `host=dynamic` एक `aor` बन जाता है जिसमें `max_contacts` होता है (डिवाइस अपने कॉन्टैक्ट को भरने के लिए REGISTER करता है); `secret=` एक `type=auth` के अंदर `password=` बन जाता है; `qualify=yes` **aor** पर `qualify_frequency=60` (सेकंड) बन जाता है, न कि endpoint पर। `max_contacts` को 1 से ऊपर तभी सेट करें यदि आप वास्तव में एक ही समय में कई डिवाइस पर एक ही अकाउंट चाहते हैं।

### An inbound trunk (`host=<ip>` / `type=peer`)

एक प्रोवाइडर जो आपको एक ज्ञात IP एड्रेस से कॉल भेजता है। यहाँ कोई रजिस्ट्रेशन नहीं है — आप `identify` का उपयोग करके *कैरियर के ट्रैफ़िक को उसके source IP द्वारा* ऑथेंटिकेट करते हैं।

**Legacy `sip.conf`:**

```
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

महत्वपूर्ण अनुवाद **`insecure=invite` → `identify`** है। `chan_sip` में, `insecure=invite` ने Asterisk को बताया "ऑथेंटिकेशन के लिए इस पीयर से इनबाउंड INVITEs को चुनौती न दें।" PJSIP उसी प्रभाव को `type=identify`/`match=` के साथ *source IP को endpoint से मिलाकर* प्राप्त करता है, जो अधिक स्पष्ट और अधिक सुरक्षित दोनों है। स्टेटिक `host=` `aor` पर एक स्थायी `contact=` बन जाता है ताकि आप कैरियर को *आउट* भी डायल कर सकें। `match=` एक IP, एक CIDR रेंज, या एक होस्टनेम स्वीकार करता है (कॉन्फ़िगरेशन-लोड समय पर रिज़ॉल्व किया गया — यदि प्रोवाइडर का IP बदलता है तो रिलोड करें)।

### An outbound registration (`register =>`)

जब प्रोवाइडर चाहता है कि *आप* उनके पास लॉग इन करें, तो `chan_sip` ने `[general]` में एक एकल `register =>` लाइन का उपयोग किया। PJSIP इसे एक समर्पित `type=registration` ऑब्जेक्ट और एक `outbound_auth` के साथ बदल देता है।

**Legacy `sip.conf`:**

```
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

**Asterisk 22 `pjsip.conf`:**

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

`register =>` फ़ील्ड्स को एक-से-एक मैप करें: `1020:supersecret` क्रेडेंशियल्स `auth` ऑब्जेक्ट बन जाते हैं (`outbound_auth` के रूप में संदर्भित); `@sip.example.com:5600` `server_uri` बन जाता है; `/9999` सफ़िक्स — वह यूज़र भाग जिसे प्रोवाइडर इनबाउंड कॉल डिलीवर करता है — `contact_user=9999` बन जाता है। `defaultuser`/`fromuser` और `fromdomain` endpoint पर `from_user` और `from_domain` बन जाते हैं। ध्यान दें कि `outbound_auth` *दो बार* दिखाई देता है: रजिस्ट्रेशन इसे REGISTER के लिए उपयोग करता है, endpoint इसे आउटबाउंड INVITEs पर `407` चुनौती का उत्तर देने के लिए उपयोग करता है।

## Option-by-option migration reference

जब आप हाथ से अनुवाद कर रहे हों (या स्क्रिप्ट के आउटपुट का ऑडिट कर रहे हों), तो यह टेबल लुकअप है। हर PJSIP विकल्प का नाम और प्लेसमेंट (endpoint / aor / auth / transport) Asterisk 22 लैब के विरुद्ध सत्यापित है।

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | कहाँ |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (डिवाइस REGISTERs) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `username=` / `defaultuser=` | `username=` | auth |
| `secret=` (auth method) | `auth_type=digest` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `disallow=` / `allow=` | `disallow=` / `allow=` (समान सिंटैक्स) | endpoint |
| `context=` | `context=` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | auth छोड़ें; `type=identify` + `match=` का उपयोग करें | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

### A note on `secret` → `auth` and `auth_type`

`chan_sip` का `secret=` एक `type=auth` ऑब्जेक्ट का `password=` फ़ील्ड बन जाता है। **ऑथेंटिकेशन मेथड** को `auth_type` के साथ सेट किया जाता है। `auth_type=digest` का उपयोग करें। पुराने मान `userpass` और `md5` अभी भी काम करते हैं लेकिन **डेप्रिकेट हो चुके हैं और चुपचाप `digest` में परिवर्तित हो जाते हैं** — सीधे लैब से सत्यापित:

```
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

आप पुराने कॉन्फ़िगरेशन और कन्वर्जन स्क्रिप्ट के आउटपुट (और इस पुस्तक के पिछले अध्यायों में) में `auth_type=userpass` देखेंगे। यह हानिरहित है, लेकिन कुछ भी नया लिखते समय `digest` लिखें।

### NAT, media, and DTMF in detail

ये तीन वे हैं जहाँ से अधिकांश पोस्ट-माइग्रेशन "यह रजिस्टर होता है लेकिन इसमें ऑडियो नहीं है" टिकट आते हैं। `chan_sip` शॉर्टहैंड `nat=force_rport,comedia` ने एक विकल्प में तीन व्यवहार पैक किए; PJSIP उन्हें विभाजित करता है ताकि आप प्रत्येक के बारे में तर्क कर सकें:

```
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

**मीडिया** के लिए, `directmedia` `direct_media` बन जाता है (अंडरस्कोर ही पूरा बदलाव है); जब भी कॉल को Asterisk पर एंकर किया जाना चाहिए — NAT के पार, या रिकॉर्ड/ट्रांसकोड/ट्रांसफर करने के लिए — तो `direct_media=no` रखें। **DTMF** के लिए, RFC को फिर से नंबर दिया गया था: `chan_sip` का `dtmfmode=rfc2833` PJSIP का `dtmf_mode=rfc4733` है (समान आउट-ऑफ-बैंड टेलीफोन-इवेंट मैकेनिज्म, वर्तमान RFC नंबर)। लैब पुष्टि करती है कि वैध `dtmf_mode` मान `rfc4733`, `inband`, `info`, `auto`, और `auto_info` हैं, जो डिफ़ॉल्ट रूप से `rfc4733` होते हैं।

**Codecs** के लिए, कुछ नहीं बदलता: `disallow=all` जिसके बाद `allow=ulaw` (आदि) PJSIP endpoint पर समान सिंटैक्स का उपयोग करता है।

## Dialplan and CLI changes

माइग्रेशन `pjsip.conf` पर नहीं रुकता। दैनिक उपयोग में दो चीजें बदलती हैं।

### Channel strings: `SIP/` → `PJSIP/`

`extensions.conf` में हर `Dial()` और चैनल संदर्भ जो पुरानी तकनीक का नाम लेता था, उसे अपडेट किया जाना चाहिए:

```
; Before (chan_sip)
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Trunk डायल स्ट्रिंग्स उसी पैटर्न का पालन करती हैं — `Dial(SIP/${EXTEN}@itsp)` `Dial(PJSIP/${EXTEN}@itsp)` बन जाता है। PJSIP एक साथ AOR से बंधे हर कॉन्टैक्ट को रिंग करने के लिए `PJSIP_DIAL_CONTACTS()` फ़ंक्शन, और `PJSIP_HEADER()` / `PJSIP_MEDIA_OFFER()` dialplan फ़ंक्शंस भी जोड़ता है; अपने dialplan में `SIP/`, `SIPPEER`, `SIPCHANINFO`, और `CHANNEL(...)` SIP संदर्भों के लिए grep करें और प्रत्येक का अनुवाद करें।

### CLI: `sip show ...` → `pjsip show ...`

पूरा `sip ...` कमांड ट्री ड्राइवर के साथ चला गया है। प्रतिस्थापन:

| `chan_sip` कमांड | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (या `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (या `core reload`) |

पुराने कमांड केवल अलग तरह से व्यवहार नहीं करते — वे अब मौजूद ही नहीं हैं। लैब पर, `sip show peers` *No such command* लौटाता है, जबकि `pjsip show endpoints`, `pjsip show aors`, `pjsip show auths`, `pjsip show contacts`, `pjsip show registrations`, और `pjsip show identifies` सभी मौजूद हैं। सबसे उपयोगी ट्रबलशूटिंग कमांड — SIP पैकेट लॉगर जो `sip set debug` के साथ हर संदेश प्रिंट करता था — अब **`pjsip set logger on`** है (एक पीयर पर ध्यान केंद्रित करने के लिए `pjsip set logger host <ip>` के साथ)।

## Realtime (ARA) migration

यदि आपने डेटाबेस (Asterisk Realtime Architecture) से `chan_sip` चलाया है, तो आपके डिवाइस `sippeers` टेबल में और रजिस्ट्रेशन `sipregs` में रहते थे। PJSIP एक पूरी तरह से अलग स्टोरेज लेयर का उपयोग करता है — **Sorcery** — जिसमें *प्रति ऑब्जेक्ट प्रकार* एक टेबल होती है। मैपिंग:

| `chan_sip` realtime table | PJSIP / Sorcery table(s) |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (प्रत्येक एक पंक्ति, अलग की गई) |
| `sipregs` | `ps_contacts` (डायनामिक रजिस्ट्रेशन) |
| — (आउटबाउंड `register=>`) | `ps_registrations` |
| — (IP मिलान) | `ps_endpoint_id_ips` (`identify` ऑब्जेक्ट्स) |
| — (डोमेन उपनाम) | `ps_domain_aliases` |

वैचारिक विभाजन फ्लैट-फ़ाइल मामले के समान है: एक `sippeers` पंक्ति तीन तालिकाओं (`ps_endpoints` + `ps_aors` + `ps_auths`) में *तीन* पंक्तियाँ बन जाती है जो endpoint नाम से एक-दूसरे को संदर्भित करती हैं।

दो चीजें इसे सुगम बनाती हैं:

- **स्कीमा आपके लिए जनरेट किया जाता है।** Asterisk `contrib/ast-db-manage/` के तहत Alembic माइग्रेशन प्रदान करता है जो हर `ps_*` टेबल बनाता है। हाथ से DDL लिखने के बजाय वर्तमान PJSIP स्कीमा बनाने के लिए `config` डेटाबेस के विरुद्ध `alembic upgrade head` चलाएं।
- **एक SQL कन्वर्जन स्क्रिप्ट है।** `sip_to_pjsip.py` के साथ उसी `contrib/scripts/sip_to_pjsip/` डायरेक्टरी में **`sip_to_pjsql.py`** स्थित है; यह उसी `convert()` लॉजिक का पुन: उपयोग करती है लेकिन फ्लैट कॉन्फ़िग फ़ाइल के बजाय `ps_*` तालिकाओं के लिए `INSERT` स्टेटमेंट्स की एक `pjsip.sql` फ़ाइल उत्सर्जित करती है। फ्लैट-फ़ाइल टूल की तरह, इसे लोड करने से पहले आउटपुट की समीक्षा करें।

अंत में, `sorcery.conf` को अपने डेटाबेस पर इंगित करें ताकि PJSIP `ps_*` तालिकाओं (`res_config_odbc` / `res_pjsip_realtime` के माध्यम से) से endpoints, aors, auths, और कॉन्टैक्ट्स को पढ़े, ठीक वैसे ही जैसे `extconfig.conf` ने कभी `chan_sip` के लिए `sippeers` को डेटाबेस पर इंगित किया था। Realtime मैकेनिक्स को *Realtime* अध्याय में कवर किया गया है; माइग्रेशन-विशिष्ट बिंदु केवल यह है कि *कौन सी तालिकाएँ किससे मैप होती हैं*।

## Migration checklist

प्रोडक्शन कटओवर के लिए संचालन का एक व्यावहारिक क्रम:

1. **इन्वेंट्री।** `sip.conf` (या हर `sippeers`/`sipregs` पंक्ति) में हर डिवाइस, trunk, और `register =>` को सूचीबद्ध करें। कस्टम NAT, codec, और DTMF सेटिंग्स नोट करें।
2. **कनवर्टर को एक scratch फ़ाइल में चलाएं।** `sip_to_pjsip.py sip.conf pjsip_generated.conf`। इसे अपने लाइव `pjsip.conf` पर इंगित **न करें**।
3. **आउटपुट के शीर्ष पर "Non mapped elements" ब्लॉक पढ़ें** और हर लाइन को हल करें — विशेष रूप से `qualify`, टाइमर, और NAT-संबंधित कुछ भी।
4. **ट्रांसपोर्ट(s) को हाथ से डिज़ाइन करें।** प्रति IP/पोर्ट एक ट्रांसपोर्ट; आवश्यकतानुसार TLS/TCP जोड़ें; क्लाउड/NAT बॉक्स के लिए `external_*_address` और `local_net` सेट करें।
5. **ऑथेंटिकेशन सत्यापित करें।** हर `auth` ऑब्जेक्ट पर `auth_type=digest`, यूज़रनेम, और पासवर्ड की पुष्टि करें।
6. **NAT/मीडिया/DTMF सत्यापित करें।** आवश्यकतानुसार प्रति endpoint `force_rport`/`rewrite_contact`/`rtp_symmetric`, `direct_media`, `dtmf_mode=rfc4733`।
7. **Dialplan अपडेट करें।** हर जगह `SIP/` → `PJSIP/`; `SIP*` फ़ंक्शंस और चैनल वेरिएबल्स की जाँच करें।
8. **स्क्रिप्ट और मॉनिटरिंग अपडेट करें।** कोई भी टूल या AMI उपभोक्ता जो `sip show ...` आउटपुट को पार्स करता था, उसे `pjsip show ...` / PJSIP AMI क्रियाओं में जाना चाहिए।
9. **रिलोड और सत्यापित करें।** `module reload res_pjsip.so`, फिर `pjsip show endpoints`, `pjsip show registrations`, `pjsip show identifies`।
10. **पैकेट लॉगर के साथ परीक्षण करें।** `pjsip set logger on`; एक रजिस्ट्रेशन, एक इनबाउंड कॉल, और एक आउटबाउंड कॉल करें और SIP एक्सचेंज को एंड-टू-एंड पढ़ें।

## Common pitfalls

- **`alwaysauthreject` अब इन-बिल्ट है — इसे न खोजें।** `chan_sip` को `alwaysauthreject=yes` की आवश्यकता थी ताकि यह खराब यूज़रनेम का अलग तरह से उत्तर देकर यह लीक न करे कि कौन से एक्सटेंशन मौजूद थे। PJSIP डिज़ाइन द्वारा सुरक्षित काम करता है: यह कभी नहीं बताता कि कोई endpoint मौजूद है या नहीं। सेट करने के लिए कोई `alwaysauthreject` विकल्प नहीं है। संबंधित सुरक्षा — अज्ञात प्रेषकों को थ्रॉटल करना — डिफ़ॉल्ट रूप से चालू, वैश्विक `unidentified_request_count` / `unidentified_request_period` है।

- **`insecure=invite` एक PJSIP विकल्प नहीं है — `identify` का उपयोग करें।** `pjsip.conf` में कोई `insecure=` नहीं है। एक ज्ञात कैरियर से अनऑथेंटिकेटेड INVITEs स्वीकार करने का तरीका यह है कि `type=identify` / `match=` के साथ *endpoint को source IP द्वारा पहचाना जाए*। जितना संभव हो उतना संकीर्ण रूप से मिलान करें (विशिष्ट होस्ट IPs, न कि विस्तृत CIDRs), और इसे एक `type=acl` के साथ बैक करें — बिना ऑथेंटिकेशन वाला IP-मैच्ड trunk टोल-फ्रॉड का लक्ष्य है।

- **प्रति IP/पोर्ट एक ट्रांसपोर्ट।** आप एक ही IP:पोर्ट पर दो ट्रांसपोर्ट बाइंड नहीं कर सकते, और आप एक ही IP वर्ज़न के कई TCP या TLS ट्रांसपोर्ट बाइंड नहीं कर सकते। कन्वर्जन स्क्रिप्ट एक ऐसा ट्रांसपोर्ट उत्सर्जित कर सकती है जो आपके पास पहले से मौजूद ट्रांसपोर्ट से टकराता है — एक एकल, जानबूझकर डिज़ाइन किए गए ट्रांसपोर्ट लेयर में समेकित करें।

- **`qualify=yes` बूलियन में अनुवादित नहीं होता है।** यह `qualify_frequency=<seconds>` के रूप में **aor** पर संबंधित है। कनवर्टर `qualify=yes` को non-mapped ब्लॉक में ठीक इसलिए डालता है क्योंकि endpoint पर कोई समकक्ष बूलियन नहीं है।

- **`secret=` एक endpoint विकल्प नहीं है।** क्रेडेंशियल्स केवल एक `type=auth` ऑब्जेक्ट में रहते हैं जिसे endpoint *संदर्भित* करता है (इनबाउंड के लिए `auth=`, आउटबाउंड के लिए `outbound_auth=`)। Endpoint पर पासवर्ड डालने से कुछ नहीं होता।

- **CLI और कोई भी स्क्रैपिंग स्क्रिप्ट चुपचाप टूट जाती है।** `sip show ...` "No such command" लौटाता है, न कि कोई त्रुटि जिसे आपकी मॉनिटरिंग आवश्यक रूप से पकड़ेगी। कटओवर से पहले हर क्रॉन जॉब, Nagios चेक, और AMI क्लाइंट के लिए `sip ` कमांड का ऑडिट करें।

## Summary

Asterisk 22 में माइग्रेट करने का मतलब `chan_sip` से माइग्रेट करना है, क्योंकि ड्राइवर को Asterisk 21 में हटा दिया गया था और PJSIP ही एकमात्र SIP चैनल है जो बचा है। काम का मूल प्रत्येक `sip.conf` `peer`/`user`/`friend` को फिर से व्यक्त करना है — जिसने सब कुछ एक ब्लॉक में पैक किया था — सहयोग करने वाले PJSIP ऑब्जेक्ट्स के एक सेट के रूप में: एक `endpoint` और एक `auth`, एक `aor`, और, डिवाइस के आधार पर, एक `identify` (इनबाउंड trunk), एक `registration` (आउटबाउंड लॉगिन), और एक साझा `transport`। `contrib/scripts/sip_to_pjsip/` में `sip_to_pjsip.py` स्क्रिप्ट थोक अनुवाद करती है और ईमानदारी से उन चीजों को फ्लैग करती है जिन्हें वह "Non mapped elements" ब्लॉक में मैप नहीं कर सकती है, लेकिन इसका आउटपुट एक पहला ड्राफ्ट है: ट्रांसपोर्ट, NAT, और सुरक्षा को हाथ से डिज़ाइन करें और प्रोडक्शन से पहले परीक्षण करें। कॉन्फ़िगरेशन के आसपास, dialplan (`SIP/` → `PJSIP/`) और अपनी उंगलियों और स्क्रिप्ट्स (`sip show` → `pjsip show`, `sip set debug` → `pjsip set logger`) को अपडेट करें। Realtime डिप्लॉयमेंट `sippeers`/`sipregs` से Sorcery `ps_endpoints`/`ps_aors`/`ps_auths`/`ps_contacts` तालिकाओं में चले जाते हैं, जिसमें मदद के लिए `sip_to_pjsql.py` और `contrib/ast-db-manage` स्कीमा है। नुकसानों पर नज़र रखें — `alwaysauthreject` इन-बिल्ट है, `insecure=invite` `identify` बन जाता है, `qualify=yes` `qualify_frequency` बन जाता है, और प्रति IP/पोर्ट एक ट्रांसपोर्ट — और कटओवर रहस्यमय होने के बजाय यांत्रिक है।

## Quiz

1. Asterisk 22 डिप्लॉयमेंट को SIP के लिए PJSIP का उपयोग क्यों करना चाहिए?
   - A. `chan_sip` धीमा है लेकिन अभी भी उपलब्ध है
   - B. `chan_sip` को Asterisk 21 में हटा दिया गया था और यह Asterisk 22 में मौजूद नहीं है
   - C. PJSIP डिफ़ॉल्ट है लेकिन `chan_sip` को `modules.conf` के साथ लोड किया जा सकता है
   - D. `chan_sip` Asterisk 22 में केवल TLS के साथ काम करता है

2. एक एकल `sip.conf` `type=friend` ब्लॉक सबसे आम तौर पर PJSIP ऑब्जेक्ट्स का कौन सा सेट बन जाता है?
   - A. एक एकल `type=peer`
   - B. केवल `type=endpoint`
   - C. `type=endpoint` + `type=auth` + `type=aor`
   - D. `type=transport` + `type=registration`

3. `sip.conf` में, `host=dynamic` (डिवाइस अपना स्थान रजिस्टर करता है) मैप होता है:
   - A. `type=identify` के साथ `match=dynamic`
   - B. `max_contacts` (डिवाइस REGISTERs) के साथ एक `type=aor`
   - C. endpoint पर `direct_media=yes`
   - D. `type=registration`

4. `sip_to_pjsip.py` कन्वर्जन स्क्रिप्ट है:
   - A. एक CLI कमांड: `asterisk -rx 'sip_to_pjsip'`
   - B. `contrib/scripts/sip_to_pjsip/` के तहत Asterisk source tree में एक Python स्क्रिप्ट
   - C. बूट पर लोड किया गया एक कंपाइल किया हुआ मॉड्यूल
   - D. `res_pjsip.so` का हिस्सा

5. सही या गलत: `sip_to_pjsip.py` का आउटपुट प्रोडक्शन-रेडी है और बिना समीक्षा के लोड किया जाना चाहिए।

6. `chan_sip` शॉर्टहैंड `nat=force_rport,comedia` एक PJSIP endpoint पर किन तीन विकल्पों में अनुवादित होता है?
   - A. `nat=yes`, `qualify=yes`, `directmedia=no`
   - B. `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes`
   - C. `external_media_address`, `external_signaling_address`, `local_net`
   - D. `insecure=invite`, `identify`, `match`

7. `sip.conf` का `dtmfmode=rfc2833` कौन सी PJSIP सेटिंग बन जाता है?
   - A. `dtmf_mode=rfc2833`
   - B. `dtmf_mode=inband`
   - C. `dtmf_mode=rfc4733`
   - D. `dtmf_mode=info`

8. Asterisk 22 पर, एक `auth` ऑब्जेक्ट को किस `auth_type` का उपयोग करना चाहिए, और `userpass` की स्थिति क्या है?
   - A. `auth_type=userpass`; यह एकमात्र वैध मान है
   - B. `auth_type=digest`; `userpass` डेप्रिकेट हो चुका है और `digest` में परिवर्तित हो गया है
   - C. `auth_type=md5`; `digest` डेप्रिकेट हो चुका है
   - D. `auth_type=plaintext`; `digest` को हटा दिया गया था

9. `insecure=invite` (ज्ञात IP से अनऑथेंटिकेटेड INVITEs स्वीकार करें) के साथ एक `chan_sip` प्रोवाइडर पीयर को PJSIP में माइग्रेट किया जाता है:
   - A. endpoint पर `insecure=invite`
   - B. `[global]` में `allowguest=yes`
   - C. `match=<provider IP>` के साथ एक `type=identify` ऑब्जेक्ट
   - D. `auth_type=anonymous`

10. Realtime माइग्रेशन में, `chan_sip` `sippeers` टेबल को किन PJSIP/Sorcery तालिकाओं द्वारा प्रतिस्थापित किया जाता है?
    - A. एक एकल `pjsip_peers` टेबल
    - B. `ps_endpoints`, `ps_aors`, और `ps_auths`
    - C. `sipregs` और `voicemail`
    - D. केवल `ps_contacts`

**उत्तर:** 1 — B · 2 — C · 3 — B · 4 — B · 5 — गलत · 6 — B · 7 — C · 8 — B · 9 — C · 10 — B
