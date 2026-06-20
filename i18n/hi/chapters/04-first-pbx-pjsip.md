# Building your first PBX with PJSIP

इस अध्याय में, आप एक बुनियादी Asterisk PBX कॉन्फ़िगरेशन कैसे करें, सीखेंगे। यहाँ मुख्य उद्देश्य यह देखना है कि PBX पहली बार चल रहा है, एक्सटेंशन के बीच डायल कर सकें, चल रहे संदेश को डायल कर सकें, और एकल एनालॉग या SIP ट्रंक पर डायल कर सकें। इस अध्याय का विचार यह सुनिश्चित करना है कि आपका Asterisk यथाशीघ्र चालू और कार्यशील हो। इस अध्याय का कार्य पूरा करने के बाद, आपके पास आगे के अध्यायों के लिए पर्याप्त पृष्ठभूमि होगी, जहाँ हम कॉन्फ़िगरेशन विवरणों में अधिक गहराई से जाएंगे।

## उद्देश्य

इस अध्याय के अंत तक, आप सक्षम होंगे:

- कॉन्फ़िगरेशन फ़ाइलों को समझना और संपादित करना;
- SIP आधारित सॉफ़्टफ़ोन स्थापित करना;
- एक SIP ट्रंक स्थापित और कॉन्फ़िगर करना;
- एक एनालॉग कनेक्शन स्थापित और कॉन्फ़िगर करना;
- एक्सटेंशन के बीच डायल करना;
- फ़ोन और बाहरी गंतव्यों के बीच डायल करना; और
- एक ऑटो अटेंडेंट को कॉन्फ़िगर करना।

## कॉन्फ़िगरेशन फ़ाइलों को समझना

Asterisk को टेक्स्ट कॉन्फ़िगरेशन फ़ाइलों द्वारा नियंत्रित किया जाता है जो /etc/asterisk में स्थित हैं। फ़ाइल फ़ॉर्मेट Windows की “.ini” फ़ाइलों के समान है। एक सेमिकॉलन टिप्पणी वर्ण के रूप में उपयोग किया जाता है, “=” और “=>” चिह्न बराबर हैं, और स्पेस को अनदेखा किया जाता है।

```
;
; The first line without a comment should be the session title.
;
[Session]
Key = value; Variable designation
[Session 2]
Key => value; Object declaration
```

Asterisk “=” और “=>” को समान तरीके से व्याख्या करता है। सिंटैक्स में अंतर का उपयोग ऑब्जेक्ट और वेरिएबल को अलग करने के लिए किया जाता है। जब आप एक वेरिएबल घोषित करना चाहते हैं तो “=” का उपयोग करें और ऑब्जेक्ट को निर्दिष्ट करने के लिए “=>” का उपयोग करें। सभी फ़ाइलों में सिंटैक्स समान है, लेकिन नीचे चर्चा किए अनुसार तीन प्रकार की ग्रामर उपयोग की जाती हैं।

## Grammars

| Grammar | How the object is created | Conf. file | Example |
|---------|---------------------------|------------|---------|
| Simple Group | All in the same line | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| Option Inheritance | Options are defined first, the object inherits the options | `chan_dahdi.conf` | `[channels]; context=default; signalling=fxs_ks; group=1; channel => 1` |
| Complex Entity | Each entity receives a context | `pjsip.conf`, `iax.conf` | `[cisco]; type=endpoint; auth=cisco-auth; aors=cisco; context=trusted` |

### Simple Group

The simple group format used in `extensions.conf` and `voicemail.conf` is the most basic grammar. Each object is declared with options in the same line. Example:

```
[Session]
Object 1 => op1,op2,op3
Object 2=> op1b,op2b,op3b
```

In this example, object 1 is created with options op1, op2, and op3 while object 2 is created with options op1, op2, and op3.

### Object options inheritance grammar

This format is used by the files chan_dahdi.conf and agents.conf, where numerous options are available, and most interfaces and objects share the same options. Typically, one or more sections have objects and channels declarations. Options to the object are declared above the object and can be changed to another object. Although this concept is hard to understand, it is very easy to use. Example:

```
[Session]
op1 = bas
op2 = adv
object=>1
op1 = int
object => 2
```

The first two lines configure the value of the options op1 and op2 to “bas” and “adv”, respectively. When object 1 is instanced, it is created using option 1 as “bas” and option 2 as “adv”. After defining object 1, we change option 1 to “int”. Next, we create object 2 with option 1 as “int” and option 2 as “adv”.

### Complex entity object

This format is used by pjsip.conf, iax.conf, and other configuration files in which numerous entities with many options exist. Typically, this format does not share a large volume of common configurations. Each entity receives a context. Sometimes reserved contexts exist, like [general] for global configurations. Options are declared in the context declarations. Example:

```
[entity1]
op1=value1
op2=value2
[entity2]
op1=value3
op2=value4
```

The entity [entity1] has values “value1” and “value2” for options op1 and op2, respectively. The entity [entity2] has values “value3” and “value4” for options op1 and op2.

## Options to build a LAB for Asterisk

एक PBX को कॉन्फ़िगर करने के लिए आपको कुछ बुनियादी हार्डवेयर की आवश्यकता होगी। यह कठिन या महंगा नहीं है, लेकिन कुछ विकल्पों पर विचार करना आवश्यक है। आपको केवल दो फ़ोन और सार्वजनिक नेटवर्क से कनेक्शन चाहिए। लैब बनाते समय कुछ विकल्प और संयोजन संभव हैं, जिन पर हम नीचे चर्चा करेंगे।

### Option 1: Complete LAB

पूरा LAB होने पर आप सभी उपलब्ध परिदृश्यों का परीक्षण कर सकते हैं और ATA, IP‑phones, और softphones जैसे समाधान की तुलना कर सकते हैं। आप एनालॉग और SIP ट्रंक्स के बारे में भी सीख सकते हैं। आपको चाहिए:

- A SIP analog telephone adapter (ATA)
- An IP phone
- A dedicated server for Asterisk
- A workstation with a softphone
- An analog interface card with at least two interfaces (1 FXO and 1 FXS)
- A VoIP provider account

### Option 2: Economy LAB

Economy LAB में हम इसे थोड़ा सरल बनाते हैं। हम ATA का उपयोग करते हैं, जो आमतौर पर IP‑phone से कम महंगा होता है, और एकल FXO कार्ड, जो वास्तव में सस्ता है। हम सीधे सर्वर से जुड़े एनालॉग फ़ोन का उपयोग नहीं कर पाएंगे, लेकिन यह व्यवहार में आम नहीं है। आपको चाहिए:

- A SIP analog telephone adapter (ATA)
- A dedicated server for Asterisk
- A workstation for the softphone
- An analog interface card with 1 FXO
- An account with a VoIP provider

### Option 3: Super economy lab

तीसरा LAB छात्र के अपने नोटबुक में एक वर्चुअलाइज़्ड सर्वर का उपयोग करता है। इस मॉडल की समस्या UDP पोर्ट द्वारा उत्पन्न टकराव है। कभी‑कभी Asterisk सर्वर और softphone दोनों एक ही पोर्ट तक पहुंचने की कोशिश करते हैं, जिससे Asterisk को पता पोर्ट बाइंड करने से रोका जाता है। एक और समस्या कॉल की गुणवत्ता है; वर्चुअल वातावरण वास्तविक‑समय अनुप्रयोगों जैसे Asterisk के लिए उपयुक्त नहीं होते। सर्वर और वर्कस्टेशन के लिए एक मुफ्त softphone और SIP प्रदाता के साथ एक ट्रंक कनेक्शन का उपयोग करें। आपको चाहिए:

- A laptop running a softphone
- A virtual machine (VirtualBox, VMware, or similar) to install Asterisk
- An account with a VoIP provider

## Installation Sequence

To help you understand the installation sequence, we outlined the sequence of steps necessary to install and configure Asterisk.

![Reference lab layout: SIP/IAX softphones, an IP phone and analog adapters as extensions (1), the Asterisk server with ETH0/FXO/FXS interfaces (3), and the trunks to the PSTN through a VoIP provider or a broadband link (2).](../images/04-first-pbx-fig01.png)

1. Extensions configuration
   - a. SIP extensions (ATA, Softphone, IP Phone)
   - b. IAX extensions
   - c. FXS extensions
2. Trunk configuration
   - a. Configuration of a SIP trunk
   - b. Configuration of a FXO trunk
3. Building a basic dial plan
   - a. Dialing between extensions
   - b. Dialing external destinations
   - c. Receiving a call from in the operator extension
   - d. Receiving a call in an auto-attendant

## Configuration of the extensions

एक्सटेंशन SIP, IAX, या एनालॉग फ़ोन होते हैं जो FXS पोर्ट से जुड़े होते हैं। किसी एक्सटेंशन को कॉन्फ़िगर करने के लिए, आपको संबंधित चैनल की कॉन्फ़िगरेशन फ़ाइल (pjsip.conf, iax.conf, chan_dahdi.conf) को संपादित करना चाहिए।

### SIP extensions

Asterisk 22 पर, PJSIP (`res_pjsip` स्टैक, जिसे `/etc/asterisk/pjsip.conf` में कॉन्फ़िगर किया गया है) SIP चैनल ड्राइवर है। यह प्रत्येक एंडपॉइंट के लिए कई ट्रांसपोर्ट का समर्थन करता है, सक्रिय रूप से मेंटेन किया जाता है, और प्लेटफ़ॉर्म के साथ शिप किया गया एकमात्र SIP ड्राइवर है। (मूल `chan_sip` ड्राइवर को Asterisk 21 में हटा दिया गया था — यदि आपको पुरानी कॉन्फ़िगरेशन को माइग्रेट करना है तो *Legacy channels* अध्याय देखें।)

यहाँ विचार यह है कि एक सरल PBX को कॉन्फ़िगर किया जाए। (आगे के अध्याय सभी विवरणों के साथ एक पूर्ण SIP/PJSIP सत्र प्रदान करेंगे।) PJSIP को `/etc/asterisk/pjsip.conf` में कॉन्फ़िगर किया जाता है और यह SIP फ़ोन और VoIP प्रदाताओं से संबंधित सभी पैरामीटर रखता है। SIP क्लाइंट्स को कॉल करने और प्राप्त करने से पहले कॉन्फ़िगर करना आवश्यक है।

#### The transport

PJSIP में, लिस्नर कॉन्फ़िगरेशन (बाइंड एड्रेस, पोर्ट, प्रोटोकॉल) एक `transport` ऑब्जेक्ट में रहता है। Asterisk में यूज़रनेम अनुमान के खिलाफ बिल्ट‑इन प्रोटेक्शन है — यह अज्ञात और ज्ञात उपयोगकर्ताओं दोनों के लिए हमेशा समान ऑथेंटिकेशन चैलेंज लौटाता है, और एक ही IP से दोहराए गए अनपहचाने अनुरोधों को `[global]` विकल्प `unidentified_request_count`/`unidentified_request_period` के माध्यम से रेट‑लिमिट किया जाता है। एक ट्रांसपोर्ट के मुख्य विकल्प हैं:

- protocol: ट्रांसपोर्ट प्रोटोकॉल — `udp`, `tcp`, `tls`, `ws`, या `wss`।
- bind: एड्रेस और पोर्ट जिस पर लिस्नर बाइंड होता है। यदि आप एड्रेस को `0.0.0.0` सेट करते हैं, तो यह सभी इंटरफ़ेस पर बाइंड हो जाता है; SIP पोर्ट UDP/TCP के लिए डिफ़ॉल्ट रूप से 5060 होता है।

एक न्यूनतम UDP ट्रांसपोर्ट:

```
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

Codec selection (`disallow`/`allow`) and the default `context` are configured on each `endpoint` (shown below), not on the transport. Anonymous/guest calls are handled by an `endpoint` named `anonymous`. Registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`.

#### SIP clients

After completing the transport section, it is time to set up the SIP clients. I would once again like to remind the reader that we will have an entire SIP/PJSIP chapter later in the book. For now, let’s concentrate on the basics and leave the details for later.

In PJSIP a SIP client is built from a set of related objects, tied together by name reference:

- `endpoint`: The call behaviour — codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.
- `auth`: The credentials. `username` is the SIP authentication user and `password` is the secret used to authenticate the device.
- `aor`: The "address of record" — where the endpoint can be reached. Either a static `contact=` (for a device at a fixed IP) or `max_contacts=` to allow the device to register dynamically.

Warning: Use strong passwords, with at least 8 characters, alphanumeric and numeric characters, and at least one symbol. Reports of hacked servers have appeared in the mailing lists, and brute force password crackers for SIP are easily available for script kiddies. Toll fraud costs thousands of dollars for consumers and providers.

Endpoint 6000 is a device at a fixed IP, so its AOR carries a static `contact` instead of allowing registration. Endpoint 6001 is a device that registers, so its AOR allows it to register (`max_contacts=1`):

```
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50

[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

PJSIP अनुमति देता है कि `endpoint`, `auth` और `aor` सेक्शन एक ही सेक्शन नाम साझा करें (उदाहरण के लिए ऊपर के दो `[6001]` ब्लॉक्स, उनके `type=` द्वारा अलग किए गए); कई प्रशासक इसके बजाय उन्हें (`[6001]`, `[6001-auth]`, `[6001]` aor) पढ़ने में आसान बनाने के लिए प्रत्यय जोड़ते हैं। एक डिवाइस जो पंजीकृत होता है, उसके लिए संपर्क फ़ोन के पंजीकरण पर गतिशील रूप से सीखा जाता है, इसलिए AOR को कोई स्थिर `contact` की आवश्यकता नहीं होती।

## IAX Extensions

`chan_iax2` अभी भी Asterisk 22 में शिप किया जाता है लेकिन अब लेगेसी है; नई डिप्लॉयमेंट्स के लिए SIP/PJSIP पसंदीदा प्रोटोकॉल है।

आप IAX extensions भी बना सकते हैं। यह प्रोटोकॉल Asterisk के लिए मूलभूत है, और इस पुस्तक में बाद में इसके लिए एक पूरा अनुभाग होगा। अभी के लिए, चलिए इस प्रोटोकॉल का उपयोग करके कुछ extensions बनाते हैं। कॉन्फ़िगर किए जाने वाले पहले सेक्शन के रूप में, सेक्शन **[general]** में कुछ पैरामीटर सेट करने होते हैं। मुख्य विकल्प हैं:

- allow/disallow: यह निर्धारित करता है कि कौन‑से codecs उपयोग किए जाएंगे।
- bindaddr: वह पता जिससे IAX2 लिस्नर बाइंड करता है। यदि आप इसे 0.0.0.0 (डिफ़ॉल्ट) पर सेट करते हैं, तो यह सभी इंटरफ़ेसों पर बाइंड हो जाएगा।
- context: सभी क्लाइंट्स के लिए डिफ़ॉल्ट context सेट करता है, जब तक कि क्लाइंट सेक्शन में इसे बदला न जाए। हमने सुरक्षा कारणों से dummy उपयोग किया। जब विकल्प **allowguest** को yes पर सेट किया जाता है, तो अनऑथेंटिकेटेड उपयोगकर्ता इस context में प्रवेश करते हैं।
- bindport: IAX2 UDP पोर्ट जिस पर सुनना है (डिफ़ॉल्ट 4569)।
- delayreject: जब इसे yes पर सेट किया जाता है, तो REGREQ या AUTHREQ के लिए ऑथेंटिकेशन रिजेक्ट भेजने में देरी होती है, जिससे ब्रूट‑फ़ोर्स पासवर्ड अटैक के खिलाफ सुरक्षा बढ़ती है।
- bandwidth: जब इसे high पर सेट किया जाता है, तो यह उच्च बैंडविड्थ codecs, जैसे कि g711 के ulaw और alaw वेरिएंट, को चुनने की अनुमति देता है।

निम्नलिखित iax.conf फ़ाइल के **[general]** सेक्शन का एक नमूना है।

```
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

### IAX Clients

जनरल सेक्शन समाप्त करने के बाद, IAX क्लाइंट्स को सेट अप करने का समय है।

- `[name]`: सेक्शन का नाम IAX peer/user नाम है; एक इनकमिंग IAX कनेक्शन नाम से मिलान करके इस पर मैप किया जाता है।
- `type`: कनेक्शन क्लास — `peer`, `user`, या `friend`:
  - `peer`: Asterisk एक peer को कॉल भेजता है।
  - `user`: Asterisk एक उपयोगकर्ता से कॉल प्राप्त करता है।
  - `friend`: दोनों दिशाओं में एक साथ।
- `host`: IP पता या होस्ट नाम। सबसे आम मान है `dynamic`, जो तब उपयोग किया जाता है जब डिवाइस Asterisk में रजिस्टर करता है।
- `secret`: peers और उपयोगकर्ताओं को ऑथेंटिकेट करने के लिए पासवर्ड।

**Warning:** कम से कम 8 अक्षरों, अल्फ़ान्यूमेरिक और न्यूमेरिक कैरेक्टर्स, तथा कम से कम एक सिंबल वाला मजबूत पासवर्ड उपयोग करें। मेलिंग लिस्ट्स में हैक हुए सर्वरों की रिपोर्टें आई हैं, और IAX md5 हैश के लिए ब्रूट‑फ़ोर्स पासवर्ड क्रैकर्स स्क्रिप्ट किडीज़ के लिए उपलब्ध हैं। टोल फ्रॉड उपभोक्ताओं और प्रदाताओं के लिए हजारों डॉलर का खर्च बनता है। उदाहरण:

```
[guest]
type=user
context=dummy
callerid="Guest IAX User"
[6003]
type=friend
context=from-internal
secret=#sup3rs3cr3t#
host=dynamic
[6004]
type=friend
context=from-internal
secret=#s3cr3ts3cr3t#
host=dynamic
```

## Configuring the SIP devices

After defining the phones in the Asterisk configuration file, it is time to configure the phone itself. In this example, we will show how to configure a free softphone — the SipPulse Softphone (download it from https://www.sippulse.com/produtos/softphone). Check your device’s manual to understand the parameters of your phone. Step 1: Configure the phone to use the extension 6000. Execute the installation program. After the execution, open the account/SIP settings and add a new SIP account. Fill in the required information.

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

Display Name: 6000  User Name: 6000  Password: #MySecret1#7  Authorization User Name: 6000  Domain: ip_of_your_server. Confirm that your phone is registered using the console command `pjsip show endpoints` (or `pjsip show endpoint 6000` for detail; `pjsip show contacts` shows the registered AOR contacts). Repeat the configuration for the phone 6001.

![A registered SipPulse Softphone — the green dot and the account line (`1001@softphone.sippulse.com.br`) confirm the registration; place a call from the keypad or the call/video buttons.](../images/softphone/sipphone-registered.png){width=35%}

## Configuring the IAX devices

IAX2 एक लेगेसी प्रोटोकॉल है (देखें *Legacy channels* अध्याय), और SipPulse Softphone केवल SIP है, इसलिए यह IAX अकाउंट रजिस्टर नहीं कर सकता। यदि आपको IAX2 का परीक्षण करना है, तो ऐसा सॉफ्टफ़ोन उपयोग करें जो अभी भी इसे सपोर्ट करता हो। एक नया IAX अकाउंट बनाएं,

3. नया IAX अकाउंट चुनें।  
4. 6003 फ़ोन के लिए संबंधित विकल्प डालें और वैकल्पिक रूप से 6004 के लिए भी।  
5. कॉन्फ़िगरेशन सहेजें और `iax2 show peers` का उपयोग करके जांचें कि फ़ोन रजिस्टर्ड है या नहीं।

Important: SIP के लिए एक अकाउंट और IAX के लिए दूसरा अकाउंट उपयोग करें। यदि आप सिस्टम को एक साथ IAX और SIP दोनों पर रिंग करने के लिए कॉन्फ़िगर करना चाहते हैं, तो हम आपको यह डायल‑प्लान सेक्शन में दिखाएंगे।

### Configuring a PSTN interface

PSTN से कनेक्ट करने के लिए आपको एक इंटरफ़ेस फ़ॉरेन एक्सचेंज ऑफिस (FXO) और एक टेलीफ़ोन लाइन की आवश्यकता होगी। आप मौजूदा PBX एक्सटेंशन भी उपयोग कर सकते हैं। कई निर्माताओं से आप FXO इंटरफ़ेस वाला टेलीफ़ोनी इंटरफ़ेस कार्ड प्राप्त कर सकते हैं। इस उदाहरण में, हम आपको दिखाएंगे कि DAHDI इंटरफ़ेस कार्ड कैसे स्थापित करें।

![FXS और FXO पोर्ट: FXS पोर्ट एक एनालॉग फ़ोन को चलाता है (डायल टोन और रिंग प्रदान करता है), जबकि FXO पोर्ट Asterisk को टेलको लाइन से जोड़ता है.](../images/04-first-pbx-fig02.png)

### Analog lines using DAHDI

आप कई निर्माताओं से DAHDI के साथ संगत एक एनालॉग कार्ड खरीद सकते हैं। X100P Digium के पहले कार्डों में से एक था और पहले ही बंद कर दिया गया है। कुछ निर्माता अभी भी समान क्लोन बनाते हैं। X100P की कीमत के अलावा, हमने इन कार्डों और नई मदरबोर्ड के बीच कई समस्याएँ पाई हैं, इसलिए इसे सावधानी से उपयोग करें। मेरे विचार में, X100P उत्पादन वातावरण के लिए अच्छा विकल्प नहीं है। DAHDI के साथ संगत कोई भी कार्ड काम करना चाहिए। DAHDI डेवलपर्स की टीम के धन्यवाद से, अब हमारे पास इंटरफ़ेस कार्डों को लगभग स्वचालित रूप से पहचानने और कॉन्फ़िगर करने का टूल है। यदि आपने अभी‑ही DAHDI ड्राइवर स्थापित किए हैं, तो कृपया `make config` चलाना और मशीन को रीबूट करना न भूलें ताकि यह स्वचालित रूप से लोड हो जाए। आप नीचे दिए गए कमांड्स का उपयोग करके अपने कार्ड को पहचान और कॉन्फ़िगर कर सकते हैं। Step 1: अपने हार्डवेयर को पहचानने के लिए उपयोग करें:

```
dahdi_hardware
```

चरण 2: कॉन्फ़िगर करने के लिए उपयोग करें:

```
dahdi_genconf
```

उपरोक्त कमांड दो फ़ाइलें `/etc/dahdi/system.conf` और `/etc/asterisk/dahdi-channels.conf` उत्पन्न करेगा। `dahdi_genconf` के लिए डिफ़ॉल्ट पैरामीटर आमतौर पर ठीक होते हैं, लेकिन आप उन्हें फ़ाइल `/etc/dahdi/genconf_parameters` में बदल सकते हैं। डिफ़ॉल्ट रूप से, यह (FXO) लाइनों को `from-pstn` कॉन्टेक्स्ट में और फ़ोनों (FXS) को `from-internal` कॉन्टेक्स्ट में डाल देगा।  

**Step 3:** `dahdi_genconf` चलाने के बाद, फ़ाइल `/etc/asterisk/chan_dahdi.conf` की अंतिम पंक्ति में निम्नलिखित पंक्ति जोड़ें:

```
#include dahdi-channels.conf
```

चरण 4: फ़ाइल /etc/dahdi/modules को संपादित करें और सभी अप्रयुक्त ड्राइवरों को टिप्पणी करें। आगे बढ़ने से पहले रीबूट करें और जांचें कि चैनल पहचान रहे हैं या नहीं, इसका उपयोग करके:

```
*CLI> dahdi show channels
```

### PSTN से कनेक्ट करना एक VoIP प्रदाता के माध्यम से

यदि आपका बजट वास्तव में सीमित है, तो आप PSTN से कनेक्ट करने के लिए एक SIP ट्रंक कॉन्फ़िगर कर सकते हैं। यह निश्चित रूप से PSTN से कनेक्ट होने का सबसे किफायती तरीका है। दुनिया भर में हजारों VoIP प्रदाता मौजूद हैं। उनमें से किसी एक से कनेक्ट होने के लिए आपको कुछ पैरामीटरों की आवश्यकता होगी। पैरामीटर SIP प्रदाता द्वारा प्रदान किए जाते हैं।

- username: login
- password: secret
- Provider’s domain: domain
- UDP port: 5060
- Allowed codecs: g729, ilbc, alaw

दो पैरामीटर आपके द्वारा निर्धारित किए जाने चाहिए।

- Extension to receive calls—in this case: 9999
- context: from-sip

PJSIP में, एक रजिस्टरिंग SIP ट्रंक उसी ऑब्जेक्ट फ़ैमिली से बनाया जाता है जो एक endpoint के लिए उपयोग होती है, साथ ही स्पष्ट `registration` और `identify` ऑब्जेक्ट्स। `registration` ऑब्जेक्ट Asterisk को प्रदाता के साथ रजिस्टर करने के लिए बताता है, `identify` ऑब्जेक्ट प्रदाता के IP से आने वाले इनबाउंड ट्रैफ़िक को endpoint से मिलाता है (PJSIP स्रोत IP द्वारा इनबाउंड INVITEs को प्रमाणित करता है), और `outbound_auth` आउटबाउंड कॉल्स और रजिस्ट्रेशन के लिए क्रेडेंशियल्स प्रदान करता है।

```
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret

[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

इस ट्रंक तक पहुँचने के लिए, हम चैनल नाम `PJSIP/siptrunk` का उपयोग करेंगे। `dtmf_mode=rfc4733` सेटिंग DTMF को बैंड के बाहर ले जाती है (RFC 4733 पुराने RFC 2833 को अप्रचलित करता है; पेलोड समान है)। `identify`/`match` विकल्प IP पते, CIDR, या होस्टनेम स्वीकार करता है, लेकिन होस्टनेम को कॉन्फ़िग‑लोड समय पर एक बार हल किया जाता है, इसलिए बदलते IP वाले प्रदाता के लिए सिग्नलिंग IP(स) को स्पष्ट रूप से सूचीबद्ध करें। `pjsip show registrations` के साथ पंजीकरण की पुष्टि करें।

## डायल प्लान परिचय

डायल प्लान Asterisk के दिल की तरह है। यह निर्धारित करता है कि Asterisk प्रत्येक कॉल को PBX में कैसे संभालता है। यह एक्सटेंशन से बना होता है जो Asterisk के लिए एक निर्देश सूची बनाते हैं। निर्देश चैनल या एप्लिकेशन से प्राप्त अंकों द्वारा सक्रिय होते हैं। Asterisk को सफलतापूर्वक कॉन्फ़िगर करने के लिए, डायल प्लान को समझना अत्यंत महत्वपूर्ण है। डायल प्लान का अधिकांश भाग /etc/asterisk निर्देशिका में स्थित extensions.conf फ़ाइल में होता है। यह फ़ाइल सरल समूह व्याकरण का उपयोग करती है और चार मुख्य अवधारणाएँ रखती है:

- एक्सटेंशन
- प्रायोरिटी
- एप्लिकेशन
- कॉन्टेक्स्ट

आइए एक बुनियादी डायल प्लान बनाते हैं। इस पुस्तक के बाद के भागों में, मैं डायल प्लान को समर्पित एक अध्याय प्रदान करूंगा। यदि आपने सैंपल फ़ाइलें (make samples) स्थापित की हैं, तो extensions.conf पहले से मौजूद है। इसे किसी अन्य नाम से सहेजें और एक खाली फ़ाइल से शुरू करें।

## The structure of the file extensions.conf

extensions.conf फ़ाइल को विभिन्न सेक्शन में विभाजित किया गया है। पहला है [general] सेक्शन, उसके बाद [globals] सेक्शन आता है। प्रत्येक सेक्शन की शुरुआत उसके नाम की परिभाषा (जैसे, [default]) से होती है और यह तब समाप्त होती है जब कोई नया सेक्शन बनाया जाता है।

### The section [general]

general सेक्शन फ़ाइल के शीर्ष पर स्थित है। डायल प्लान को कॉन्फ़िगर करना शुरू करने से पहले, यह जानना उपयोगी होता है कि कौन‑से सामान्य विकल्प कुछ डायल प्लान व्यवहारों को नियंत्रित करते हैं। ये विकल्प हैं:

- static and write protect: यदि `static=yes` और `writeprotect=no`, तो आप CLI कमांड के द्वारा चल रहे डायल प्लान को डिस्क पर वापस सहेज सकते हैं:

```
*CLI> dialplan save
```

Warning: यदि आप CLI से `dialplan save` कमांड जारी करते हैं, तो फ़ाइल में मौजूद सभी टिप्पणी और नोट्स खो जाएंगे।

- autofallthrough: यदि autofallthrough सेट है, तो जब कोई एक्सटेंशन करने के लिए कुछ नहीं बचता, तो यह कॉल को BUSY, CONGESTION, या HANGUP के साथ समाप्त कर देगा, यह Asterisk के सर्वोत्तम अनुमान पर निर्भर करता है। यह डिफ़ॉल्ट है। यदि autofallthrough सेट नहीं है, तो जब कोई एक्सटेंशन करने के लिए कुछ नहीं बचता, तो Asterisk नई एक्सटेंशन डायल होने की प्रतीक्षा करेगा।
- clearglobalvars: यदि clearglobalvars सेट है, तो ग्लोबल वेरिएबल्स को साफ़ किया जाएगा और डायलप्लान रीलोड या Asterisk रीलोड पर पुनः पार्स किया जाएगा। यदि clearglobalvars सेट नहीं है, तो ग्लोबल वेरिएबल्स रीलोड के दौरान बना रहेगा और — चाहे extensions.conf या उसकी किसी शामिल फ़ाइल से हटाए गए हों — वे पिछले मान पर सेट रहेंगे।
- extenpatternmatchnew: तेज़ पैटर्न‑मैचिंग एल्गोरिद्म का उपयोग करता है, जो बड़ी संख्या में एक्सटेंशन होने पर स्पष्ट रूप से मदद करता है। डिफ़ॉल्ट रूप से नहीं।
- userscontext: यह वह कॉन्टेक्स्ट है जहाँ users.conf से एंट्रीज़ रजिस्टर्ड होती हैं।

### The section [globals]

[globals] सेक्शन में आप ग्लोबल वेरिएबल्स और उनके प्रारंभिक मान परिभाषित करेंगे। आप डायल प्लान में इन वेरिएबल्स को `${GLOBAL(variable)}` के द्वारा एक्सेस कर सकते हैं। आप लिनक्स/यूनिक्स पर्यावरण में परिभाषित वेरिएबल्स को `${ENV(variable)}` के द्वारा भी एक्सेस कर सकते हैं। ग्लोबल वेरिएबल्स केस‑सेंसिटिव नहीं होते। कुछ उदाहरण इस प्रकार हो सकते हैं:

```
INCOMING=>DAHDI/8&DAHDI/9
RINGTIME=>3
```

अगले उदाहरण में, आप डायल प्लान में एक ग्लोबल वेरिएबल सेट और परीक्षण कर सकते हैं।

```
exten=9000,1,set(GLOBAL(RINGTIME)=4)
exten=9000,n,Noop(${GLOBAL(RINGTIME)})
exten=9000,n,hangup()
```

## Contexts

Context is the named partition of the dial plan. After the [general] and [globals] sections, the dial plan is a set of contexts in which each context has several extensions, each extension has several priorities, and each priority calls an application with several arguments.

![Asterisk call flow: every call arrives on a channel (IAX, SIP, and others) as an incoming call leg; the channel's context — set globally or per-channel in the channel config file — decides which context in extensions.conf processes the call before it leaves on the outgoing leg.](../images/04-first-pbx-fig03.png)

![Call processing: the `context=` defined for a channel (in chan_dahdi.conf or pjsip.conf) names the matching context in extensions.conf where the dial plan handles the call.](../images/04-first-pbx-fig04.png)

You can build a simple dial plan to reach other phones and the PSTN. However, Asterisk is much more powerful than that. Our objective is to teach you more details of what is possible in the dial plan.

## एक्सटेंशन

पारंपरिक PBX के विपरीत, जहाँ एक्सटेंशन फ़ोन, इंटरफ़ेस, मेनू आदि से जुड़े होते हैं, Asterisk में एक एक्सटेंशन वह कमांडों की सूची है जो किसी विशिष्ट एक्सटेंशन नंबर या नाम के ट्रिगर होने पर प्रोसेस की जाती है। कमांडों को प्राथमिकता क्रम में प्रोसेस किया जाता है।

![Extension syntax: `exten => number(name),{priority|label}[(alias)],application`. एक्सटेंशन संख्यात्मक, अल्फ़ान्यूमेरिक, कॉलर ID के साथ संख्यात्मक, पैटर्न, या `s` जैसे मानक एक्सटेंशन हो सकते हैं; प्राथमिकताएँ एक संख्या, `n` (अगला), `s` (समान), एक ऑफ़सेट, या `hint` हो सकती हैं.](../images/04-first-pbx-fig05.png)

एक एक्सटेंशन लिटरल, मानक, या विशेष हो सकता है। एक मानक एक्सटेंशन में केवल संख्याएँ या नाम तथा * और # अक्षर होते हैं; 12#89* एक वैध लिटरल एक्सटेंशन है। नामों का उपयोग एक्सटेंशन मिलान के लिए भी किया जा सकता है। एक्सटेंशन केस‑सेंसिटिव होते हैं। हालांकि, आप समान नाम लेकिन अलग केस के दो एक्सटेंशन नहीं बना सकते। जब कोई एक्सटेंशन डायल किया जाता है, तो पहली प्राथमिकता वाला कमांड निष्पादित होता है, उसके बाद प्राथमिकता 2 वाला कमांड आदि। यह तब तक चलता रहता है जब तक कॉल डिस्कनेक्ट नहीं हो जाती या कोई कमांड संख्या एक लौटाता है, जो विफलता दर्शाता है। जब अंतिम प्राथमिकता निष्पादित होती है, तो Asterisk का व्यवहार पैरामीटर autofallthrough द्वारा नियंत्रित होता है। इस अध्याय के [general] सेक्शन को देखें। उदाहरण:

```
exten=>123,1,Answer
exten=>123,n,Playback(tt-weasels)
exten=>123,n,Hangup
```

ऊपर आप विस्तार 123 डायल किए जाने पर प्रोसेस की जाने वाली निर्देशों की सूची पाते हैं। पहली प्राथमिकता चैनल का उत्तर देना है (जब चैनल रिंगिंग स्थिति में हो तो आवश्यक होता है: अर्थात् FXO चैनल)। दूसरी प्राथमिकता एक ऑडियो फ़ाइल जिसका नाम tt-weasels है, उसे प्ले बैक करना है। तीसरी प्राथमिकता चैनल को हांग अप करना है। एक अन्य विकल्प कॉलर आईडी के अनुसार कॉल को हैंडल करना है। आप `/` कैरेक्टर का उपयोग करके प्रोसेस की जाने वाली कॉलर आईडी निर्दिष्ट कर सकते हैं। उदाहरण:

```
exten=>123/100,1,Answer()
exten=>123/100,n,Playback(tt-weasels)
exten=>123/100,n,Hangup()
```

यह उदाहरण एक्सटेंशन 123 को ट्रिगर करेगा और निम्न विकल्पों को केवल तभी निष्पादित करेगा जब कॉलर आईडी 100 हो। इसे नीचे वर्णित पैटर्न का उपयोग करके भी किया जा सकता है।

```
exten=>1234/_256NXXXXXX,1,Answer()
```

hint: maps an extension to a channel. It is used to monitor the channel state. It is used in conjunction with presence. The phone has to support it.

#### Patterns

You can use patterns and literals in the dial plan. Patterns are very useful for reducing the dial plan size. All patterns start with the “_” character. The following characters may be used to define a pattern. The figure identifies the patterns available for use with Asterisk.

![Pattern matching characters: `_` starts a pattern, `.` matches one or more characters, `!` matches zero or more, `[123-7]` matches any listed digit or range, `X` is 0-9, `Z` is 1-9, and `N` is 2-9 — with examples mapping office extension ranges.](../images/04-first-pbx-fig06.png)

### Special extensions

Asterisk uses some extension names as standard extensions.

![Asterisk special extensions: `i` (invalid), `s` (start), `h` (hangup), `t` (timeout), `T` (absolute timeout), `o` (operator), `a` (pressed `*` in voicemail), `fax` (fax detection), and `Talk` (used with BackgroundDetect).](../images/04-first-pbx-fig07.png)

Description:

- **s**: Start. It is used to handle a call when there is no dialed number. It is useful for FXO trunks and in-menu processing.
- **t**: Timeout. It is used when calls remain inactive after a prompt has been played. It is also used to hang up an inactive line.
- **T**: AbsoluteTimeout. If you establish a call limit using the `TIMEOUT(absolute)` dialplan function, once the call exceeds the limit defined, it will be sent to the T extension.
- **h**: Hangup. It is called after the user disconnects the call.
- **i**: Invalid. It is triggered when you call an non-existent extension in the context. Using these extensions can affect the content of CDR records—specifically, the dst that does not contain the number dialed.
- **o**: Operator. It is used to go to operator when the user presses "0" during the voicemail.

The use of these extensions can change the content of the billing records (CDR)—in particular, the field dst will not have the number dialed. To work around this problem, you should use the option g in the dial() application and consider the functions resetcdr(w) and/or nocdr()

## Variables

Asterisk PBX में, वेरिएबल्स ग्लोबल, चैनल-विशिष्ट, और एनवायरनमेंट-विशिष्ट हो सकते हैं। आप NoOP() एप्लिकेशन का उपयोग करके कंसोल में वेरिएबल की सामग्री देख सकते हैं। यह एप्लिकेशन आर्ग्यूमेंट्स के रूप में ग्लोबल वेरिएबल या चैनल-विशिष्ट वेरिएबल का उपयोग कर सकता है। वेरिएबल को नीचे दिए गए उदाहरण की तरह रेफ़र किया जा सकता है, जहाँ varname वेरिएबल का नाम है।

```
${varname}
```

वेरिएबल नाम एक अल्फ़ान्यूमेरिक स्ट्रिंग हो सकता है जो अक्षर से शुरू होती है। ग्लोबल वेरिएबल नाम केस-सेंसिटिव नहीं होते। हालांकि, सिस्टम वेरिएबल्स (Asterisk-परिभाषित या चैनल-परिभाषित) केस-सेंसिटिव होते हैं। इसलिए, वेरिएबल ${EXTEN} और ${exten} अलग हैं।

### Global variables

ग्लोबल वेरिएबल्स को extensions.conf फ़ाइल के [global] सेक्शन में या एप्लिकेशन का उपयोग करके कॉन्फ़िगर किया जा सकता है:

```
set(Global(variable)=content)
```

### Channel-specific variables

चैनल-विशिष्ट वेरिएबल्स को एप्लिकेशन set() के द्वारा कॉन्फ़िगर किया जाता है। प्रत्येक चैनल को अपना वेरिएबल स्पेस मिलता है। विभिन्न चैनलों के वेरिएबल्स के बीच टकराव की कोई संभावना नहीं रहती। एक चैनल-विशिष्ट वेरिएबल चैनल के हैंग अप होने पर नष्ट हो जाता है। सबसे अधिक उपयोग किए जाने वाले वेरिएबल्स में शामिल हैं:

- ${EXTEN} डायल किया गया एक्सटेंशन
- ${CONTEXT} वर्तमान कॉन्टेक्स्ट
- ${CALLERID(name)}
- ${CALLERID(num)}
- ${CALLERID(all)} वर्तमान कॉलर ID
- ${PRIORITY} वर्तमान प्रायोरिटी

अन्य चैनल-विशिष्ट वेरिएबल्स सभी अपरकेस में होते हैं। आप dumpchan() एप्लिकेशन का उपयोग करके कई वेरिएबल्स की सामग्री देख सकते हैं। नीचे dump-channel वेरिएबल्स का एक सरल अंश दिया गया है।

```
exten=9001,1,DumpChan()
exten=9001,n,Echo()
exten=9001,n,Hangup()
```

Dumpchan output:

```
Dumping Info For Channel: PJSIP/4400-00000001:
================================================================================
Info:
Name=               PJSIP/4400-00000001
Type=               PJSIP
UniqueID=           1161186526.1
LinkedID=           1161186526.0
CallerIDNum=        4400
CallerIDName=       laptop
ConnectedLineIDNum= (N/A)
ConnectedLineIDName=(N/A)
DNIDDigits=         9001
RDNIS=              (N/A)
Parkinglot=
Language=           en
State=              Ring (4)
Rings=              0
NativeFormat=       (ulaw)
WriteFormat=        ulaw
ReadFormat=         ulaw
RawWriteFormat=     ulaw
RawReadFormat=      ulaw
WriteTranscode=     No
ReadTranscode=      No
1stFileDescriptor=  16
Framesin=           0
Framesout=          0
TimetoHangup=       0
ElapsedTime=        0h0m0s
BridgeID=           (Not bridged)
Context=            default
Extension=          9001
Priority=           1
CallGroup=
PickupGroup=
Application=        DumpChan
Data=               (Empty)
Blocking_in=        (Not Blocking)
Variables:
```

ऊपर का फ़ील्ड लेआउट Asterisk 22 `DumpChan` आउटपुट है (एक वास्तविक `PJSIP/...` चैनल नाम, `CallerIDNum`/`ConnectedLineID` फ़ील्ड्स, और `Raw*`/`Transcode`/`BridgeID` पंक्तियाँ जो PJSIP चैनल भरते हैं)। पुराने ड्राइवर के विपरीत, एक PJSIP चैनल स्वचालित रूप से `SIPCALLID`/`SIPUSERAGENT` चैनल वेरिएबल्स सेट नहीं करता; समकक्ष SIP विवरण मांग पर `PJSIP_HEADER()` और `CHANNEL()` डायलप्लान फ़ंक्शन्स के साथ पढ़े जाते हैं — उदाहरण के लिए `${CHANNEL(pjsip,call-id)}`, `${PJSIP_HEADER(read,User-Agent)}`, और `${CHANNEL(rtp,dest)}` रिमोट RTP एड्रेस के लिए।

### Environment-specific variables

एनवायरनमेंट-विशिष्ट वेरिएबल्स का उपयोग ऑपरेटिंग सिस्टम में परिभाषित वेरिएबल्स तक पहुँचने के लिए किया जा सकता है। आप फ़ंक्शन ENV() का उपयोग करके एनवायरनमेंट-विशिष्ट वेरिएबल्स सेट कर सकते हैं। उदाहरण के लिए:

```
${ENV(LANG)}
Set(ENV(LANG)=en_US)
```

### Application-specific variables

कुछ एप्लिकेशन डेटा इनपुट और आउटपुट के लिए वेरिएबल्स का उपयोग करते हैं। आप एप्लिकेशन को कॉल करने से पहले वेरिएबल सेट कर सकते हैं या एप्लिकेशन निष्पादन के बाद वेरिएबल प्राप्त कर सकते हैं। उदाहरण के लिए: Dial एप्लिकेशन निम्नलिखित वेरिएबल्स लौटाता है:

- ${DIALEDTIME} -> यह वह समय है जब एक चैनल को डायल किया जाता है से लेकर वह डिस्कनेक्ट होने तक।
- ${ANSWEREDTIME} -> यह वास्तविक कॉल के समय की मात्रा है।
- ${DIALSTATUS} यह कॉल की स्थिति है: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o

## Expressions

Expressions डायल प्लान में बहुत उपयोगी हो सकते हैं। इन्हें स्ट्रिंग्स को बदलने और गणितीय तथा तर्कसंगत ऑपरेशन्स करने के लिए उपयोग किया जाता है।

![Asterisk expressions overview — `$[expression1 operator expression2]` — grouping the math, logical, comparison, regular-expression, and conditional operators available in the dial plan.](../images/04-first-pbx-fig08.png)

Expression सिंटैक्स इस प्रकार परिभाषित है:

```
$[expression1 operator expression2]
```

मान लीजिए हमारे पास “I” नाम का एक वेरिएबल है और हम उस वेरिएबल में 100 जोड़ना चाहते हैं:

```
$[${I}+100]
```

जब Asterisk डायल प्लान में कोई एक्सप्रेशन पाता है, तो वह पूरी एक्सप्रेशन को परिणामस्वरूप मान से बदल देता है।

### Operators

निम्नलिखित ऑपरेटर्स का उपयोग एक्सप्रेशन्स बनाने के लिए किया जा सकता है। ऑपरेटर प्रेसीडेंस पर ध्यान देना महत्वपूर्ण है।

1. Parentheses “()”
2. Unary operators “! -“
3. Regular expression “: =~
4. Multiplicative operators “* / %”
5. Additive operators “+ -“
6. Comparison operators
7. Logical operators
8. Conditional operators

#### Math Operators

- Addition (+)
- Subtraction (-)
- Multiplication(*)
- Division (/)
- Modulus (%)

#### Logical Operators

- Logical “AND” (&)
- Logical “OR” (|)
- Logical Unary Complement (!)

#### Regular expression operators

- Regular expression matching (:)
- Regular expression exact matching (=~)

एक रेगुलर एक्सप्रेशन वह विशेष टेक्स्ट स्ट्रिंग है जिसका उपयोग खोज पैटर्न को वर्णित करने के लिए किया जाता है। आप रेगुलर एक्सप्रेशन्स को वाइल्डकार्ड के रूप में सोच सकते हैं। रेगुलर एक्सप्रेशन्स का उपयोग स्ट्रिंग को पैटर्न से मिलाने और मिलान की जाँच करने के लिए किया जाता है। यदि मिलान सफल होता है और रेगुलर एक्सप्रेशन में कम से कम एक मैच होता है, तो पहला मैच लौटाया जाता है; अन्यथा, परिणाम मिलाए गए अक्षरों की संख्या होता है।

#### Comparison operators

तुलना का परिणाम 1 होता है यदि संबंध सत्य है या 0 यदि वह असत्य है।

- = equal
- != not equal
- < less than
- > greater than
- <= less than or equal to
- >= greater than or equal to

### LAB. Evaluate the following expressions:

इन एक्सप्रेशन्स को अपने डायल प्लान में रखें और NoOP() एप्लिकेशन का उपयोग करके एक्सप्रेशन्स का मूल्यांकन करें। 9002 डायल करें और Asterisk कंसोल में परिणाम देखें। परिणाम दिखाने के लिए verbose 15 का उपयोग करें।

```
exten=9002,1,set(NAME="FLAVIO")                 ;Set NAME=FLAVIO
exten=9002,n,set(I=4)
exten=9002,n,set(URI="40001@voip.school")
exten=9002,n,NoOP(${NAME})
exten=9002,n,NoOP(${I})
exten=9002,n,NoOP($[${I}+${I}])
exten=9002,n,NoOP($[${I}=4])
exten=9002,n,NoOP($[${I}=4 & ${NAME}=FLAVIO])
exten=9002,n,NoOP($[${URI} =~ "4[0-9][0-9][0-9][0-9]@."])
exten=9002,n,NoOP($[${I}=4?"MATCH"::"DO NOT MATCH"])
exten=9002,n,hangup
```

## Functions

कुछ एप्लिकेशन को फ़ंक्शनों द्वारा प्रतिस्थापित किया गया है, जो अभिव्यक्तियों की तुलना में अधिक उन्नत तरीके से वेरिएबल्स को प्रोसेस करने की अनुमति देते हैं। आप निम्नलिखित कंसोल कमांड जारी करके फ़ंक्शनों की पूरी सूची देख सकते हैं:

```
*CLI> core show functions
```

String length: ${LEN(string)} स्ट्रिंग की लंबाई लौटाता है

```
Example:
exten=>100,1,Set(Fruit=pear)
exten=>100,2,NoOp(${LEN(Fruit)})
exten=>100,3,NoOp(${LEN(${Fruit})})
```

पहले ऑपरेशन में, सिस्टम परिणाम के रूप में 5 दिखाता है (शब्द “fruit” में अक्षरों की संख्या)। दूसरा 4 लौटाता है (शब्द “pear” में अक्षरों की संख्या)। Substrings: वह सबस्ट्रिंग लौटाता है, जो “offset” पैरामीटर द्वारा परिभाषित स्थिति से शुरू होती है, और “length” पैरामीटर में परिभाषित स्ट्रिंग लंबाई तक रहती है। यदि ऑफसेट नकारात्मक है, तो यह दाएँ से बाएँ, स्ट्रिंग के अंत से शुरू होता है। यदि लंबाई छोड़ी गई है या नकारात्मक है, तो यह ऑफसेट से शुरू होकर पूरी स्ट्रिंग ले लेता है।

```
${string:offset:length }
```

Example #1: Several substrings

```
${123456789:1}-returns 23456789
${123456789:-4}-returns 6789
${123456789:0:3}-returns 123
${123456789:2:3}-returns 345
${123456789:-4:3}-returns 678
```

Example #2: Take the area code from the first three digits.

```
exten=>_NXX.,1,Set(areacode=${EXTEN:0:3})
```

Example #3: Takes all digits from the variable ${EXTEN}, except for the area code.

```
exten=>_516XXXXXXX,1,Dial(${EXTEN:3})
```

### String concatenation

दो स्ट्रिंग्स को जोड़ने के लिए, बस उन्हें एक साथ लिखें।

```
${foo}${bar}
555${number}
${longdistanceprefix}555${number}
```

## एप्लिकेशन

डायल प्लान बनाने के लिए, हमें एप्लिकेशन की अवधारणा को समझना होगा। आप डायल प्लान में चैनल को संभालने के लिए एप्लिकेशन का उपयोग करेंगे। एप्लिकेशन कई मॉड्यूल में लागू किए गए हैं। उपलब्ध एप्लिकेशन मॉड्यूल पर निर्भर करते हैं। आप कंसोल कमांड का उपयोग करके सभी Asterisk एप्लिकेशन दिखा सकते हैं:

```
*CLI> core show applications
```

वैकल्पिक रूप से, आप निम्नलिखित उदाहरण का उपयोग करके किसी विशिष्ट एप्लिकेशन के विवरण दिखा सकते हैं:

```
*CLI> core show application Dial
```

To build a simple dial plan, you need to know a few applications. We will discuss more advanced examples later in the book.

![The handful of applications needed to build a simple dial plan: Answer (answer a channel), Dial (call another channel), Hangup (hang up a channel), Playback (play an audio file), and Goto (jump to a priority, extension, or context).](../images/04-first-pbx-fig09.png)

We will use these applications (above) to create a simple dial plan for two basic PBXs.

### Answer()

[Synopsis] Answers a channel if ringing [Description] Answer([delay]): If the call has not been answered, the application will answer it. Otherwise, it has no effect on the call. If a delay is specified, Asterisk will wait the number of milliseconds specified in ‘delay’ before answering the call.

### Dial()

The following description can be obtained by issuing the show application dial in the dial plan. For easy searching, it is reproduced below. The syntax for the Dial application is also shown below:

```
;dial to a single channel
Dial(Technology/resource,timeout,options,URL)
;dialing to multiple channels
Dial(Technology/resource[&Tech2/resource2...],timeout,options,URL)
```

यह एप्लिकेशन एक या अधिक निर्दिष्ट चैनलों को कॉल करेगा। जैसे ही अनुरोधित चैनलों में से कोई एक उत्तर देता है, मूल चैनल उत्तर दिया जाएगा—यदि वह पहले से उत्तर नहीं दिया गया है। ये दो चैनल तब एक ब्रिज्ड कॉल में सक्रिय हो जाएंगे। सभी अन्य अनुरोधित चैनल फिर हंग अप हो जाएंगे। जब तक कोई टाइमआउट निर्दिष्ट नहीं किया गया है, Dial एप्लिकेशन अनिश्चितकाल तक प्रतीक्षा करेगा जब तक कि कॉल किए गए चैनलों में से कोई उत्तर न दे, उपयोगकर्ता हंग अप न करे, या सभी कॉल किए गए चैनल व्यस्त या अनुपलब्ध न हों। यदि कोई अनुरोधित चैनल कॉल नहीं किया जा सकता या टाइमआउट समाप्त हो जाता है तो डायल प्लान का निष्पादन जारी रहेगा। यह एप्लिकेशन पूर्ण होने पर निम्नलिखित चैनल वेरिएबल्स सेट करता है:

- DIALEDTIME - यह वह समय है जब एक चैनल को डायल किया जाता है से लेकर वह डिस्कनेक्ट होने तक।
- ANSWEREDTIME - यह वास्तविक कॉल के लिए लिया गया समय है।
- DIALSTATUS - यह कॉल की स्थिति है: o CHANUNAVAIL o CONGESTION o NOANSWER o BUSY o ANSWER o CANCEL o DONTCALL o TORTURE

प्राइवेसी और स्क्रीनिंग मोड्स के लिए, यदि कॉल किया गया पक्ष कॉलिंग पार्टी को 'Go Away' स्क्रिप्ट पर भेजना चुनता है तो DIALSTATUS वेरिएबल DONTCALL पर सेट होगा। यदि कॉल किया गया पक्ष कॉलर को 'torture' स्क्रिप्ट पर भेजना चाहता है तो DIALSTATUS वेरिएबल TORTURE पर सेट होगा। यह एप्लिकेशन सामान्य समाप्ति की रिपोर्ट करेगा यदि मूल चैनल हंग अप हो जाता है या यदि कॉल ब्रिज्ड है और ब्रिज में से किसी भी पक्ष द्वारा कॉल समाप्त की जाती है। वैकल्पिक URL कॉल किए गए पक्ष को भेजा जाएगा यदि चैनल इसका समर्थन करता है। यदि OUTBOUND_GROUP वेरिएबल सेट है, तो इस एप्लिकेशन द्वारा निर्मित सभी पीयर चैनल उस समूह में शामिल किए जाएंगे (जैसे कि

```
Set(GROUP()=...).
```

The following table summarizes some of the most frequently used options for the application Dial. For the complete list, use the console command `core show application Dial`. In Asterisk 22 these options are separated from the channel and timeout by commas — for example `Dial(PJSIP/2000,20,tTm)`.

| Option | Description |
|--------|-------------|
| `A(x)` | कॉल किए गए पक्ष को घोषणा बजाता है, `x` को फ़ाइल के रूप में उपयोग करता है। |
| `C` | इस कॉल के लिए CDR को रीसेट करता है। |
| `d` | कॉल के उत्तर की प्रतीक्षा करते हुए कॉल करने वाले उपयोगकर्ता को 1-अंकीय एक्सटेंशन डायल करने की अनुमति देता है। यदि वह वर्तमान कॉन्टेक्स्ट में मौजूद है तो उस एक्सटेंशन पर जाता है, या यदि मौजूद हो तो `EXITCONTEXT` वेरिएबल में परिभाषित कॉन्टेक्स्ट पर जाता है। |
| `D([called][:calling])` | कॉल किए गए पक्ष के उत्तर देने के बाद, लेकिन कॉल ब्रिज होने से पहले, निर्दिष्ट DTMF स्ट्रिंग्स भेजता है। `called` स्ट्रिंग कॉल किए गए पक्ष को भेजी जाती है और `calling` स्ट्रिंग कॉल करने वाले पक्ष को। कोई भी पैरामीटर अकेले उपयोग किया जा सकता है। |
| `f` | कॉल करने वाले चैनल की Caller ID को डायल प्लान `hint` के माध्यम से चैनल से जुड़े एक्सटेंशन पर सेट करने के लिए मजबूर करता है। यह तब उपयोगी है जब PSTN मनमानी Caller ID की अनुमति नहीं देता। |
| `g` | यदि गंतव्य चैनल हैंग अप करता है तो वर्तमान एक्सटेंशन पर डायल प्लान निष्पादन जारी रखता है। |
| `G(context^exten^pri)` | यदि कॉल उत्तर दिया जाता है, तो कॉल करने वाले पक्ष को निर्दिष्ट प्रायोरिटी पर और कॉल किए गए पक्ष को प्रायोरिटी+1 पर ट्रांसफर करता है। वैकल्पिक रूप से एक एक्सटेंशन (या एक्सटेंशन और कॉन्टेक्स्ट) निर्दिष्ट किया जा सकता है; अन्यथा वर्तमान एक्सटेंशन उपयोग किया जाता है। |
| `h` | कॉल किए गए पक्ष को `*` DTMF अंक भेजकर हैंग अप करने की अनुमति देता है। |
| `H` | कॉल करने वाले पक्ष को `*` DTMF अंक भेजकर हैंग अप करने की अनुमति देता है। |
| `L(x[:y][:z])` | कॉल को `x` ms तक सीमित करता है, जब `y` ms बचते हैं तो एक चेतावनी बजाता है, और हर `z` ms पर चेतावनी दोहराता है। नीचे दिए गए `LIMIT_*` वेरिएबल्स देखें। |
| `m([class])` | कॉल करने वाले पक्ष को अनुरोधित चैनल के उत्तर देने तक म्यूज़िक ऑन होल्ड प्रदान करता है। एक विशिष्ट MusicOnHold क्लास निर्दिष्ट की जा सकती है। |
| `r` | कॉल करने वाले पक्ष को रिंगिंग संकेत देता है और कॉल किए गए चैनल के उत्तर देने तक कोई ऑडियो पास नहीं करता। |
| `S(x)` | कॉल किए गए पक्ष के उत्तर देने के `x` सेकंड बाद कॉल को हैंग अप करता है। |
| `t` | कॉल किए गए पक्ष को `features.conf` में परिभाषित DTMF क्रम भेजकर कॉल करने वाले पक्ष को ट्रांसफर करने की अनुमति देता है। |
| `T` | कॉल करने वाले पक्ष को `features.conf` में परिभाषित DTMF क्रम भेजकर कॉल किए गए पक्ष को ट्रांसफर करने की अनुमति देता है। |
| `w` | कॉल किए गए पक्ष को `features.conf` में परिभाषित DTMF क्रम भेजकर वन-टच रिकॉर्डिंग सक्षम करने की अनुमति देता है। |
| `W` | कॉल करने वाले पक्ष को `features.conf` में परिभाषित DTMF क्रम भेजकर वन-टच रिकॉर्डिंग सक्षम करने की अनुमति देता है। |
| `k` | कॉल किए गए पक्ष को `features.conf` में कॉल पार्किंग के लिए परिभाषित DTMF क्रम भेजकर कॉल को पार्क करने की अनुमति देता है। |
| `K` | कॉल करने वाले पक्ष को `features.conf` में कॉल पार्किंग के लिए परिभाषित DTMF क्रम भेजकर कॉल को पार्क करने की अनुमति देता है। |

The `L(x[:y][:z])` option can be tuned with the following special variables:

- `LIMIT_PLAYAUDIO_CALLER` — `yes|no` (default `yes`): कॉलर के लिए ध्वनियों को चलाता है।
- `LIMIT_PLAYAUDIO_CALLEE` — `yes|no`: कॉल किए गए पक्ष के लिए ध्वनियों को चलाता है।
- `LIMIT_TIMEOUT_FILE` — समय समाप्त होने पर चलाने वाली फ़ाइल।
- `LIMIT_CONNECT_FILE` — कॉल शुरू होने पर चलाने वाली फ़ाइल।
- `LIMIT_WARNING_FILE` — जब `y` परिभाषित हो तो चेतावनी के रूप में चलाने वाली फ़ाइल। डिफ़ॉल्ट रूप से शेष समय बताया जाता है।

उदाहरण:

```
exten=_4XXX,1,Dial(PJSIP/${EXTEN},20,tTm)
```

In the example above, the application will dial to the corresponding PJSIP channel. Both caller and called could transfer the call (Tt). Music on hold will be heard instead of ring back. If nobody answers within 20 seconds, the extension will go to the next priority.

### Hangup()

Hangs up the calling channel [Description] Hangup([causecode]): This application will hang up the calling channel. If a cause code is given, the channel's hang-up cause will be set to the given value.

### Goto()

Jump to a particular priority, extension, or context [Description] Goto([[context|]extension|]priority): This application will cause the calling channel to continue the dial plan execution at the specified priority. If no specific extension (or extension and context) are specified, this application will jump to the specified priority of the current extension. If the attempt to jump to another location in the dial plan is not successful, the channel will continue at the next priority of the current extension.

## डायल प्लान बनाना

एक सरल डायल प्लान बनाने के लिए, आपको सभी इनकमिंग और आउटगोइंग कॉल्स को कंटेक्स्ट्स और एक्सटेंशन्स बनाकर हैंडल करना होगा। इस सेक्शन में, हम आपको सबसे सामान्य एक्सटेंशन्स कैसे बनाएं, यह दिखाएंगे।

### एक्सटेंशन्स के बीच डायलिंग

एक्सटेंशन के बीच डायलिंग को सक्षम करने के लिए, हम चैनल वेरिएबल `${EXTEN}` का उपयोग कर सकते हैं, जो डायल किए गए एक्सटेंशन को दर्शाता है। उदाहरण के लिए, यदि एक्सटेंशन रेंज 4000 से 4999 के बीच है और सभी एक्सटेंशन SIP का उपयोग करते हैं, तो हम निम्नलिखित कमांड अपना सकते हैं:

```
[from-internal]
exten=_4XXX,1,Dial(PJSIP/${EXTEN})
```

### बाहरी गंतव्य पर डायल करना

बाहरी गंतव्य पर डायल करने के लिए आप डायल किए गए नंबर से पहले एक रूट लगा सकते हैं। उत्तर अमेरिका में, बाहरी रूप से डायल किए जाने वाले नंबर से पहले 9 का उपयोग करना सामान्य है। यदि आप PSTN के लिए एनालॉग या डिजिटल चैनल का उपयोग कर रहे हैं, तो कमांड निम्नलिखित जैसा दिखना चाहिए: यदि आप DAHDI के बजाय SIP ट्रंक का उपयोग करना चाहते हैं, तो `PJSIP/...@siptrunk` चैनल का उपयोग करें।

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/1/${EXTEN:1},20,tT)
or
exten=_9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

उपरोक्त पंक्ति आपको 9 डायल करने और इच्छित नंबर तक पहुँचने की अनुमति देगी। दिए गए उदाहरण में, आप पहला DAHDI चैनल (DAHDI/1) उपयोग करेंगे। यदि आपके पास कई लाइनों हैं और यह व्यस्त है, तो कॉल पूरी नहीं होगी। हालांकि, आप निम्नलिखित पंक्ति का उपयोग करके पहला उपलब्ध DAHDI चैनल स्वचालित रूप से चुन सकते हैं। वैकल्पिक रूप से, आप DAHDI के बजाय SIP ट्रंक का उपयोग कर सकते हैं। PJSIP फ़ॉर्म `Dial(PJSIP/number@siptrunk,...)` में, डायल किया गया नंबर उपयोगकर्ता भाग है और `siptrunk` वह endpoint है जो ऊपर कॉन्फ़िगर किया गया है।

```
[from-internal]
exten=_9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

The “g1” पैरामीटर समूह में पहली उपलब्ध चैनल की खोज करेगा, जिससे सभी चैनलों का उपयोग संभव हो सकेगा। नीचे दी गई लाइन का उपयोग करके, आप एक लम्बी दूरी का नंबर डायल कर सकते हैं।

```
[from-internal]
exten=_91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

### 9 डायल करके PSTN लाइन प्राप्त करना

यदि आपके पास बाहरी डायलिंग पर कोई प्रतिबंध नहीं है, तो आप इसे सरल बना सकते हैं और निम्नलिखित का उपयोग कर सकते हैं:

```
[from-internal]
exten=9,1,Dial(DAHDI/g1,20,tT)
```

### ऑपरेटर एक्सटेंशन में कॉल प्राप्त करना

निम्न उदाहरण में, ऑपरेटर एक्सटेंशन 4000 है। PSTN लाइन एक FXO इंटरफ़ेस से जुड़ी हुई है। `chan_dahdi.conf` फ़ाइल में निर्दिष्ट कॉन्टेक्स्ट `from-pstn` है। PSTN से आने वाली कोई भी कॉल डायलप्लान में `from-pstn` कॉन्टेक्स्ट को रूट की जाएगी। इस लाइन में डायरेक्ट इनवर्ड डायलिंग (DID) नहीं है; इसलिए हमें कॉल को “s” एक्सटेंशन के माध्यम से प्राप्त करना होगा। यदि SIP ट्रंक से प्राप्त कर रहे हैं, तो कॉन्टेक्स्ट [from-sip] का उपयोग करें।

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
[from-sip]
exten = s,1,Dial(${OPERATOR},40,tT)
exten = s,n,Hangup()
```

### Receiving a call using direct inward dialing (DID)

यदि आपके पास एक डिजिटल लाइन है, तो आपको डायल किया गया एक्सटेंशन प्राप्त होगा। जब ऐसा होता है, तो आपको कॉल को ऑपरेटर तक फ़ॉरवर्ड करने की आवश्यकता नहीं है; बल्कि, आप कॉल को सीधे गंतव्य पर फ़ॉरवर्ड कर सकते हैं। मान लीजिए आपका DID रेंज 3028550 से 3028599 तक है और अंतिम चार अंक DID में पास किए जाते हैं। कॉन्फ़िगरेशन नीचे दिए गए उदाहरण की तरह दिखेगा:

```
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

### कई एक्सटेंशन एक साथ चलाना

आप Asterisk को इस प्रकार सेट कर सकते हैं कि वह एक एक्सटेंशन डायल करे और यदि वह उत्तर नहीं दिया जाता है, तो कई अन्य एक्सटेंशन एक साथ डायल करे, जैसा कि नीचे दिए गए उदाहरण में दिखाया गया है:

```
exten => 0,1,Dial(DAHDI/1,15,tT)
exten => 0,n,Dial(DAHDI/1&DAHDI/2&DAHDI/3,15)
exten => 0,n,Hangup()
```

In this example, when someone dials the operator, the channel DAHDI/1 is initially tried. If nobody answers after 15 seconds (timeout), the channels DAHDI/1, DAHDI/2 and DAHDI/3 will ring simultaneously for another 15 seconds.

### कॉलर आईडी द्वारा रूटिंग

In this example, you could give different treatments based on the caller ID, which could be useful for call spammers. For example:

```
exten => 8590/4832518888,1,Playback(I-have-moved-to-china)
exten => 8590,1,Dial(DAHDI/1,20)
```

In this example, we have added a special rule that, if the caller ID is 4832518888, you play back a message from the previously recorded file “I-have-moved-to-china”. Other calls are accepted as usual.

### डायल प्लान में वेरिएबल्स का उपयोग

Asterisk डायल प्लान में कुछ एप्लिकेशनों के तर्क के रूप में ग्लोबल और चैनल वेरिएबल्स का उपयोग कर सकता है। निम्नलिखित उदाहरण देखें:

```
[globals]
Flavio => DAHDI/1
Daniel => DAHDI/2&PJSIP/pingtel
Anna => DAHDI/3
Christian => DAHDI/4
[mainmenu]
exten => 1,1,Dial(${Daniel}&${Flavio})
exten => 2,1,Dial(${Anna}&${Christian})
exten => 3,1,Dial(${Anna}&${Flavio})
```

Using variables makes future changes easier. If you change the variable, all references are changed immediately.

### घोषणा रिकॉर्ड करना

इस अनुभाग में बाद में चर्चा किए गए कुछ विकल्पों के लिए, हम रिकॉर्ड किए गए प्रॉम्प्ट्स का उपयोग करेंगे। यहाँ हम उन्हें रिकॉर्ड करने का एक आसान तरीका दिखाते हैं। हम अपने स्वयं के फ़ोन का उपयोग करके घोषणा को सहेजने के लिए Record() एप्लिकेशन का उपयोग करेंगे।

```
[from-internal]
exten => _record.,1,Record(${EXTEN:6}:gsm)
exten => _record.,n,wait(1)
exten => _record.,n,Playback(${EXTEN:6})
exten => _record.,n,Hangup()
```

These instructions allow you to record any message from a softphone. Example: dialing recordmenu from the softphone The instructions will call the recording with the variable ${EXTEN:6} without the first six letters. In other words, the instruction is equivalent to record(menu:gsm). All you have to do is dial record + name_of_the_file_to_be_recorded, press # to finish the recording, and wait to hear the recording.

### कॉलों को एक डिजिटल रिसेप्शनिस्ट में प्राप्त करना

अब जब हमारे पास कुछ सरल उदाहरण हैं, चलिए applications **background()** और **goto()** के बारे में अपनी समझ को विस्तारित करते हैं। Asterisk में इंटरैक्टिव सिस्टम्स के लिए मुख्य एप्लिकेशन **background()** है, जो आपको एक ऑडियो फ़ाइल चलाने की अनुमति देता है और जब कॉलर कोई कुंजी दबाता है, तो वह फ़ाइल बाधित हो जाती है ताकि कॉल को डायल किए गए एक्सटेंशन पर भेजा जा सके। **background()** एप्लिकेशन की सिंटैक्स:

```
exten=>extension, priority, background(filename)
```

एक अन्य बहुत उपयोगी एप्लिकेशन है `goto()`। जैसा कि नाम से स्पष्ट है, यह निर्दिष्ट **context**, **extension**, और **priority** पर कूदता है। एप्लिकेशन `goto()` की सिंटैक्स:

```
exten=>extension, priority,goto(context, extension, priority)
```

Valid formats for the goto() command:

```
goto(context,extension,priority)
goto(extension,priority)
goto(priority)
```

In the following example, we will create a digital receptionist. It is very simple to edit the file extensions.conf and configure the following extensions:

```
[globals]
OPERATOR=PJSIP/6000
[from-pstn]
include=aapstn
[from-sip]
include=aasip
[aapstn]
exten=>s,1,answer()
exten=>s,n,set(TIMEOUT(response)=10)
exten=>s,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>s,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
[aasip]
exten=>9999,1,answer()
exten=>9999,n,set(TIMEOUT(response)=10)
exten=>9999,n,background(menu1)
exten=>s,n,WaitExten(30)
exten=>9999,n,Dial(${OPERATOR})
exten=>6000,1,Dial(PJSIP/6000)
exten=>6001,1,Dial(PJSIP/6001)
exten=>6003,1,Dial(IAX2/6003)
exten=>6004,1,Dial(IAX2/6004)
```

SIP एक्सटेंशन `PJSIP/` का उपयोग करते हैं और IAX एक्सटेंशन `IAX2/` का उपयोग करते हैं — दोनों ड्राइवर Asterisk 22 में शामिल हैं, हालांकि `chan_iax2` को अब लेगेसी माना जाता है और SIP/PJSIP को प्राथमिकता दी जाती है।

फ़ाइल `menu1.gsm` में संदेश “press the extension or wait for the operator” रिकॉर्ड करें। जब उपयोगकर्ता नंबर 6000 डायल करता है, तो उसे एक्सटेंशन 6000 पर भेजा जाएगा। इस बिंदु पर, आपको कई एप्लिकेशनों के उपयोग की स्पष्ट समझ होनी चाहिए, जिसमें `answer()`, `background()`, `goto()`, `hangup()`, और `playback()` शामिल हैं। यदि आपके पास स्पष्ट समझ नहीं है, तो कृपया इस अध्याय को फिर से पढ़ें जब तक आप सामग्री के साथ सहज न हों। आप `background` एप्लिकेशन का बहुत बार उपयोग करेंगे। एक बार जब आप एक्सटेंशन, प्रायोरिटी, और एप्लिकेशनों की बुनियाद समझ लेते हैं, तो एक सरल डायल प्लान बनाना आसान होगा। इन अवधारणाओं को पुस्तक के बाद के भागों में अधिक गहराई से खोजा जाएगा, और आप देखेंगे कि डायल प्लान अधिक शक्तिशाली बन जाएगा।

## सारांश

इस अध्याय में, आपने सीखा कि कॉन्फ़िगरेशन फ़ाइलें **/etc/asterisk** निर्देशिका में संग्रहीत होती हैं। Asterisk का उपयोग करने के लिए पहले चैनलों (जैसे, pjsip, dahdi, iax) को कॉन्फ़िगर करना आवश्यक है। कॉन्फ़िगरेशन फ़ाइलों के लिए तीन अलग-अलग व्याकरण मौजूद हैं: सरल समूह, ऑब्जेक्ट इनहेरिटेंस, और जटिल इकाई। डायल प्लान **extensions.conf** फ़ाइल में बनाया जाता है और यह कॉन्टेक्स्ट और एक्सटेंशन का सेट होता है। डायल प्लान में, प्रत्येक एक्सटेंशन एक एप्लिकेशन को ट्रिगर करता है। आपने playback, background, dial, goto, hangup, और answer एप्लिकेशनों का उपयोग करना सीखा।

## Quiz

1. चैनल कॉन्फ़िगरेशन फ़ाइलें कौन‑सी हैं (सभी लागू विकल्प चुनें):
   - A. `/etc/asterisk/chan_dahdi.conf`
   - B. `/etc/asterisk/pjsip.conf`
   - C. `/etc/asterisk/iax.conf`
   - D. `/etc/asterisk/extensions.conf`
2. Asterisk 22 में, एकल `chan_sip` पीयर `[6001]` (`type=friend`/`host=dynamic`) को `pjsip.conf` में किस संबंधित ऑब्जेक्ट सेट द्वारा प्रतिस्थापित किया गया है?
   - A. एक `type=peer` और एक `type=user`
   - B. एक `type=endpoint`, एक `type=auth`, और एक `type=aor`
   - C. एक एकल `type=friend`
   - D. एक `type=transport` और एक `type=global`
3. चैनल कॉन्फ़िगरेशन फ़ाइल में एक कॉन्टेक्स्ट को परिभाषित करना महत्वपूर्ण है क्योंकि यह उस चैनल से आने वाली कॉल के लिए इनकमिंग कॉन्टेक्स्ट सेट करता है — कॉल उस चैनल से `extensions.conf` में मिलते‑जुलते कॉन्टेक्स्ट में प्रोसेस की जाती है।
   - A. True
   - B. False
4. `Playback()` और `Background()` एप्लिकेशनों के बीच मुख्य अंतर (दो विकल्प चुनें):
   - A. Playback प्रॉम्प्ट चलाता है लेकिन अंकों की प्रतीक्षा नहीं करता।
   - B. Background प्रॉम्प्ट चलाता है लेकिन अंकों की प्रतीक्षा नहीं करता।
   - C. Background संदेश चलाता है और अंकों के दबाए जाने की प्रतीक्षा करता है।
   - D. Playback संदेश चलाता है और अंकों के दबाए जाने की प्रतीक्षा करता है।
5. जब कोई कॉल टेलीफ़ोनी इंटरफ़ेस कार्ड (FXO) के माध्यम से बिना DID के Asterisk में प्रवेश करती है, तो इसे विशेष एक्सटेंशन में संभाला जाता है:
   - A. `0`
   - B. `9`
   - C. `s`
   - D. `i`
6. `Goto()` एप्लिकेशन के वैध फ़ॉर्मेट (तीन विकल्प चुनें):
   - A. `Goto(context,extension,priority)`
   - B. `Goto(priority,context,extension)`
   - C. `Goto(extension,priority)`
   - D. `Goto(priority)`
7. पैटर्न `_7[1-5]XX` किसे मिलाता है (सभी लागू विकल्प चुनें):
   - A. 7100
   - B. 7600
   - C. 7630
   - D. 7230
8. `Dial(PJSIP/${EXTEN},20,tTm)` में, `m` विकल्प क्या करता है?
   - A. कॉल की अधिकतम अवधि को सीमित करता है।
   - B. चैनल के उत्तर देने तक रिंगबैक के बजाय कॉलर को म्यूज़िक ऑन होल्ड प्रदान करता है।
   - C. कॉल किए गए पक्ष के उत्तर देने के बाद DTMF अंकों को भेजता है।
   - D. डायल प्लान हिंट का उपयोग करके कॉलर ID को फ़ोर्स करता है।
9. `chan_dahdi.conf` द्वारा उपयोग किए जाने वाले ऑप्शन‑इनहेरिटेंस ग्रामर में आप:
   - A. ऑब्जेक्ट को एक ही पंक्ति में परिभाषित करते हैं।
   - B. पहले विकल्प परिभाषित करते हैं और परिभाषित विकल्पों के नीचे ऑब्जेक्ट्स घोषित करते हैं।
   - C. प्रत्येक ऑब्जेक्ट के लिए एक अलग कॉन्टेक्स्ट परिभाषित करते हैं।
10. एक एक्सटेंशन में प्रायोरिटीज़ को क्रमिक रूप से (1, 2, 3, …) नंबरित होना चाहिए और `n` का उपयोग नहीं किया जा सकता।
    - A. True
    - B. False

**Answers:** 1 — A, B, C · 2 — B · 3 — A · 4 — A, C · 5 — C · 6 — A, C, D · 7 — A, D · 8 — B · 9 — B · 10 — B
