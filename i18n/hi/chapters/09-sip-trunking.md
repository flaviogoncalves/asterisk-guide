# SIP trunking, DID & the PSTN

एक PBX जो केवल खुद को ही कॉल कर सकता है, बहुत उपयोगी नहीं है। देर नहीं लगती कि हर सिस्टम को दुनिया के बाकी हिस्सों—पब्लिक स्विच्ड टेलीफोन नेटवर्क (PSTN), एक SIP प्रोवाइडर, या किसी अन्य PBX—से जुड़ना पड़ता है। वह लिंक जो इन कॉल्स को ले जाता है, **trunk** कहलाता है। TDM युग में एक trunk एक भौतिक सर्किट था: एक T1/E1 PRI या एनालॉग FXO लाइनों का बंडल। आज यह लगभग हमेशा एक **SIP trunk** होता है—एक लॉजिकल कनेक्शन जो इंटरनेट टेलीफोनी सर्विस प्रोवाइडर (ITSP) तक उसी IP नेटवर्क पर ले जाता है, जिस पर बाकी सब कुछ चलता है।

यह अध्याय दिखाता है कि कैसे Asterisk 22 को PJSIP के साथ एक ITSP से जोड़ा जाए, कैसे रजिस्ट्रेशन-आधारित और IP-आधारित trunk के बीच चयन किया जाए, कैसे इनबाउंड DID नंबरों को सही गंतव्य पर रूट किया जाए, कैसे आउटबाउंड कॉल्स को सही caller-ID और E.164 फॉर्मेटिंग के साथ भेजा जाए, और कैसे कई trunks के बीच फेलओवर और कम लागत वाले रूटिंग को बनाया जाए। हम NAT हैंडलिंग को trunks के लिए और एक लैब के साथ समाप्त करते हैं जो एक दूसरा Asterisk (और SIPp) को एक मॉक ITSP के रूप में स्थापित करता है ताकि आप एक trunk के माध्यम से वास्तविक कॉल्स कर सकें।

यहाँ सब कुछ पुस्तक के Asterisk 22.10.0 लैब के विरुद्ध सत्यापित किया गया है; trunk ऑब्जेक्ट पैटर्न वही है जो *Building your first PBX with PJSIP* और *SIP & PJSIP in depth* में प्रस्तुत किया गया था।

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk 22 to an ITSP with PJSIP
- Choose between registration-based and IP-based (static) trunks
- Route inbound DIDs to the right extension, IVR or queue
- Route outbound calls with correct caller-ID and E.164 formatting
- Build trunk failover and least-cost routing with `${DIALSTATUS}`
- Handle NAT for trunks on the transport and the endpoint

## What is a SIP trunk

A SIP trunk is a logical voice path between your PBX and another SIP system. In
practice that "other system" is one of two things:

- **An ITSP (Internet Telephony Service Provider).** A commercial carrier that
  sells you call origination and termination and, usually, a block of phone
  numbers (DIDs). You point Asterisk at the provider's signalling host, and the
  provider connects your calls to the wider PSTN. This is how most modern systems
  reach the phone network — no telephony hardware required.
- **A PSTN gateway.** A device (or another Asterisk) that has physical PSTN
  interfaces — a PRI card, analog FXO ports, or a GSM/4G gateway — and presents
  them to your PBX as SIP. The gateway does the TDM-to-SIP conversion; from
  Asterisk's point of view it is just another SIP trunk.

Either way, in PJSIP a trunk is **just an endpoint**. The same object family you
used for a phone — `endpoint`, `auth`, `aor`, optionally `identify` and
`registration` — builds a trunk. The differences are in the details: a trunk
authenticates *outbound* (you are the client, so credentials go in
`outbound_auth`, not `auth`), it usually does not register a user agent to you
(you register to *it*, or it sends you traffic from a known IP), and it lands
inbound calls in a dedicated context such as `from-pstn` instead of
`from-internal`.

> **Compared with the old TDM trunk.** A PRI gave you a fixed number of B-channels
> (23 on a T1, 30 on an E1) and signalled call setup over a dedicated D-channel
> (see the *Legacy channels* chapter). A SIP trunk has no fixed channel count —
> capacity is whatever your bandwidth, your provider's policy, and any
> `max_contacts`/concurrent-call limits allow. Caller-ID, DID, and call progress
> that used to ride ISDN information elements now ride SIP headers and SDP.

There are two ways an ITSP will agree to exchange traffic with you, and they
determine how you build the trunk: **registration-based** and **IP-based
(static)**. We cover each in turn.

## Registration-based trunks

एक registration‑based trunk वह मॉडल है जिसका उपयोग तब किया जाता है जब प्रदाता आपसे *आप* को *उनके* पास लॉग इन करने की अपेक्षा करता है। आपका Asterisk समय‑समय पर एक SIP `REGISTER` को प्रदाता को भेजता है, उपयोगकर्ता नाम और पासवर्ड के साथ प्रमाणित करता है, बिल्कुल उसी तरह जैसे एक फोन आपके PBX में रजिस्टर करता है। यह आम है जब आपका सार्वजनिक IP गतिशील हो, जब आप NAT के पीछे हों, या जब प्रदाता ग्राहक को IP पते की बजाय SIP क्रेडेंशियल्स से पहचानता है।

PJSIP में outbound login एक समर्पित `registration` ऑब्जेक्ट में रहता है। यह हटाए गए `chan_sip` ड्राइवर द्वारा उपयोग की गई एकल `register =>` लाइन को `sip.conf` में बदल देता है। यहाँ एक पूर्ण रूप से रजिस्टरिंग ट्रंक का उदाहरण है एक काल्पनिक प्रदाता के लिए, पहले के अध्यायों में सत्यापित पैटर्न का पालन करते हुए — ध्यान दें `outbound_auth` (न कि `auth`), `server_uri`/`client_uri` (न कि `server`/`client`), `from_user`/`from_domain` एंडपॉइंट पर, और `dtmf_mode=rfc4733`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

ध्यान देने योग्य कुछ बातें:

- **`auth_type=digest`, न कि `userpass`।** दोनों समान डाइजेस्ट ऑथेंटिकेशन उत्पन्न करते हैं, लेकिन Asterisk 22 में `userpass` (और पुराना `md5`) **डिप्रिकेटेड हैं और चुपचाप `digest` में परिवर्तित हो जाते हैं**। नई कॉन्फ़िगरेशन में `digest` को प्राथमिकता दें; आप अभी भी पुराने फ़ाइलों और इस पुस्तक के पहले के अध्यायों में `userpass` देखेंगे।
- **एंडपॉइंट और रजिस्ट्रेशन दोनों पर `outbound_auth`।** रजिस्ट्रेशन इसका उपयोग `REGISTER` को प्रमाणित करने के लिए करता है; एंडपॉइंट इसका उपयोग उस `407 Proxy Authentication Required` का उत्तर देने के लिए करता है जो प्रदाता आउटबाउंड `INVITE` को वापस भेजता है। वे एक ही `auth` ऑब्जेक्ट साझा कर सकते हैं।
- **`from_user` / `from_domain`।** कई प्रदाता उन कॉलों को अस्वीकार करते हैं जिनके `From` हेडर में आपका अकाउंट नंबर और उनका डोमेन नहीं होता। ये दो विकल्प ठीक वही सेट करते हैं।
- **`contact_user=4830001000`।** यह उस `Contact` का उपयोगकर्ता भाग बन जाता है जिसे आप रजिस्टर करते हैं, इसलिए प्रदाता को पता चलता है कि इनबाउंड कॉल किस नंबर पर डिलीवर करनी है। यह पुराने `register =>` लाइन पर `/9999` उपसर्ग का आधुनिक समकक्ष है।
- **`retry_interval=60`।** यदि रजिस्ट्रेशन विफल हो जाता है, तो हर 60 सेकंड में पुनः प्रयास करें।

रीलोड के बाद, `pjsip show registrations` के साथ रजिस्ट्रेशन की पुष्टि करें। लैब में — जहाँ `itsp.example.com` वास्तव में उत्तर नहीं देता — तालिका इस प्रकार दिखती है:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

`(exp. Ns)` उपसर्ग अगले प्रयास तक के सेकंड गिनता है; जब यह शून्य से नीचे जाता है तो यह संक्षिप्त रूप से `(exp. Ns ago)` पढ़ता है इससे पहले कि पुनः प्रयास शुरू हो। एक लाइव प्रदाता के खिलाफ `Status` कॉलम `Registered` दिखाता है जिसमें अगले रिफ्रेश तक शेष सेकंड होते हैं। `Rejected` (या `Unregistered`) का अर्थ है कि प्रदाता ने लॉगिन स्वीकार नहीं किया — `pjsip set logger on` को चालू करें और `401`/`403` उत्तर पढ़ें, जो लगभग हमेशा गलत उपयोगकर्ता नाम, पासवर्ड, या `client_uri` डोमेन होता है।

## IP-based (static) trunks

दूसरा मॉडल बिलकुल भी रजिस्ट्रेशन की आवश्यकता नहीं रखता। प्रोवाइडर आपका पब्लिक IP पता जानता है और कॉल्स सीधे उसी पर भेजता है; आप बदले में प्रोवाइडर के ज्ञात सिग्नलिंग IP पर कॉल्स भेजते हैं। ऑथेंटिकेशन **सोर्स IP एड्रेस** द्वारा किया जाता है, SIP क्रेडेंशियल्स द्वारा नहीं। यह आमतौर पर उन ट्रंक्स के लिए होता है जो दो सर्वरों के बीच होते हैं जिन्हें आप नियंत्रित करते हैं, या किसी एंटरप्राइज़ ट्रंक के लिए जहाँ दोनों पक्षों के पास स्थिर पते होते हैं।

मुख्य ऑब्जेक्ट है `identify`। यह Asterisk को बताता है: “*इस* IP से आने वाला कोई भी SIP अनुरोध *उस* एंडपॉइंट से संबंधित है।” इसके बिना, PJSIP इनबाउंड अनुरोध को `From` यूज़र द्वारा एंडपॉइंट से मिलाने की कोशिश करता है, जो कैरियर के ट्रैफ़िक को संतुष्ट नहीं करेगा — इसलिए कॉल को रिजेक्ट किया जाएगा या `anonymous` एंडपॉइंट पर गिरा दिया जाएगा।

एक स्थिर ट्रंक `registration` ऑब्जेक्ट को हटाता है और `identify` जोड़ता है:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
```

`match` एक IP एड्रेस, CIDR रेंज, या होस्टनेम स्वीकार करता है। **होस्टनेम को कॉन्फ़िगरेशन लोड समय पर एक बार रिज़ॉल्व किया जाता है**, इसलिए यदि आपके प्रोवाइडर का IP बदलता है तो आपको रीलोड करना होगा। उन कैरियर्स के लिए जो कई मीडिया गेटवे प्रकाशित करते हैं, प्रत्येक सिग्नलिंग IP को सूचीबद्ध करें — आप `match` दोहरा सकते हैं या एक CIDR दे सकते हैं:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Asterisk क्या स्वीकार करेगा, इसे `pjsip show identifies` से सत्यापित करें। लैब से कैप्चर किया गया (`sipp-identify` लाइन लैब के पहले से मौजूद SIPp एंडपॉइंट की है):

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### The security implication

कोई ऑथेंटिकेशन न वाला IP-आधारित ट्रंक एक दरवाज़ा है, और `identify`/`match` ही उस पर एकल ताला है। यदि आप `match` बहुत व्यापक रेंज चुनते हैं — या यदि कोई अटैकर सोर्स IP को स्पूफ़ कर सकता है — तो कॉल्स आपके `from-pstn` कॉन्टेक्स्ट में अनऑथेंटिकेटेड लैंड कर जाते हैं। दो डिफेंस, साथ में उपयोग करने के लिए:

- **जितना संभव हो उतना संकीर्ण मिलान करें।** व्यापक CIDR की तुलना में विशिष्ट होस्ट IP को प्राथमिकता दें। केवल प्रोवाइडर के वास्तविक सिग्नलिंग IP ही `match` में होने चाहिए।
- **इसे एक ACL के साथ जोड़ें।** PJSIP SIP लेयर पर ट्रैफ़िक को ड्रॉप कर सकता है, इससे पहले कि वह किसी एंडपॉइंट तक पहुँचे, एक `type=acl` ऑब्जेक्ट (या `acl.conf`) का उपयोग करके:

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

एक `type=acl` सेक्शन को किसी रेफ़रेंस की आवश्यकता नहीं होती: `res_pjsip_acl` प्रत्येक ऐसे ऑब्जेक्ट को *सभी* इनबाउंड SIP ट्रैफ़िक पर लागू करता है, इससे पहले कि वह किसी भी एंडपॉइंट तक पहुँचे। (ऑब्जेक्ट पर `acl` और `contact_acl` विकल्प नामित रूल लिस्ट को `acl.conf` से खींचते हैं, बजाय ऊपर की तरह इनलाइन `permit`/`deny` सूचीबद्ध करने के।) सिद्धांत वही है जो SIP अध्याय में बताया गया था: पहले सब कुछ डिनाय करें, फिर केवल वही अनुमति दें जिस पर आप भरोसा करते हैं। और चाहे आपका ट्रंक कॉन्टेक्स्ट कुछ भी करे,
**कभी भी इसे ऐसे कॉन्टेक्स्ट तक न पहुँचने दें जो PSTN पर वापस डायल कर सके** बिना एक स्पष्ट, ऑथेंटिकेटेड नियम के — यही क्लासिक टोल-फ़्रॉड होल है।

> **Which model should I use?** If the provider gives you a username and password

## Inbound routing and DID handling

एक बार इनबाउंड कॉल्स आते हैं, वे एंडपॉइंट के `context` में उतरते हैं — यहाँ `from-pstn`। एक **DID** (Direct Inward Dialing number) बस वह डायल किया गया नंबर है जो प्रोवाइडर अनुरोध URI में आपको देता है। आपका काम डायलप्लान में प्रत्येक DID को किसी गंतव्य से मैप करना है: एकल एक्सटेंशन, एक IVR, एक क्यू, या एक रिंग ग्रुप।

प्रोवाइडर द्वारा भेजा गया नंबर `${EXTEN}` में `from-pstn` के रूप में मेल खाता है। आप इसे कितना देख पाते हैं यह प्रोवाइडर पर निर्भर करता है — कुछ पूर्ण E.164 नंबर (`+4830001000`) भेजते हैं, कुछ राष्ट्रीय नंबर, कुछ केवल अंतिम कुछ अंक। वास्तविक इनबाउंड कॉल को `pjsip set logger on` से निरीक्षण करें और पैटर्न लिखने से पहले अनुरोध URI देखें।

### One DID to one extension

सबसे सरल केस — एकल DID सीधे एक फोन की ओर रूट किया गया:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

एक मुख्य नंबर जो फोन बजने के बजाय मेन्यू के साथ उत्तर देना चाहिए:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` वह ऑटो-अटेंडेंट कॉन्टेक्स्ट है जिसे आपने डायलप्लान अध्यायों में बनाया था (`Background()` + `WaitExten()`)। DID को रूट करना बस एक `Goto` है।

### One DID to a queue

एक सपोर्ट लाइन जो कॉल क्यू में पहुँचना चाहिए:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

जब आप नंबरों का एक ब्लॉक खरीदते हैं, तो एक पैटर्न डायलप्लान को छोटा रखता है। मान लीजिए आपका DID रेंज `4830003000`–`4830003099` है और प्रोवाइडर पूर्ण नंबर भेजता है; प्रत्येक DID के अंतिम दो अंकों को एक्सटेंशन `60xx` से मैप करें:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` अंतिम दो अंकों को लेता है (नकारात्मक ऑफ़सेट दाएँ से गिनता है), इसलिए `4830003007` `PJSIP/6007` को बजाता है। एक `did => extension` लुकअप टेबल जिसे `GoSub` या Asterisk डेटाबेस (`AstDB`/`func_odbc`) से बनाया गया है, आगे स्केल करता है, लेकिन कुछ ही नंबरों के लिए स्पष्ट पैटर्न सबसे स्पष्ट होते हैं।

> **Catch the unmatched DID.** एक `i` (invalid) एक्सटेंशन को `from-pstn` में जोड़ें ताकि एक गलत‑रूटेड इनबाउंड नंबर एक घोषणा बजाए या ऑपरेटर को रिंग करे बजाय चुपचाप ड्रॉप होने के:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Outbound routing, caller-ID and E.164

Outbound calls flow the other way: an internal phone dials a number, your dialplan
matches it, strips any access prefix, sets the caller-ID the provider expects, and
hands the call to the trunk endpoint with `Dial(PJSIP/<number>@itsp)`.

### Sending the call to the trunk

The channel syntax for a trunk is `PJSIP/<number>@<endpoint>`: the part before the
`@` becomes the user portion of the outbound request URI, and the part after the
`@` names the endpoint whose `aor` `contact` supplies the destination host. A
classic "dial 9 for an outside line" rule:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` strips the leading `9` access code before the number is sent. The
pattern `_9NXXXXXXXXX` matches `9` plus a 10-digit number whose first digit is
2–9; adjust it to your dial plan.

### Caller-ID on outbound calls

Most ITSPs ignore — or actively reject — a caller-ID that is not a number you own.
Set the outbound caller-ID number to one of your DIDs with the `CALLERID(num)`
function before `Dial()`, as shown above. You can also set the name:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

If the provider still strips or overrides your caller-ID name, that is their
policy — many carriers source the displayed name from their own CNAM database
keyed on the number, not from your `From` header.

Two endpoint options interact with this:

- **`from_user`** sets the user part of the `From` header at the SIP level, which
  some providers use to identify your account regardless of `CALLERID(num)`.
- **`trust_id_outbound`** (default `no`) controls whether Asterisk will send
  privacy-sensitive identity headers (`P-Asserted-Identity`/`P-Preferred-Identity`)
  outbound. Leave it off unless your provider documents that they want PAI, in
  which case set `trust_id_outbound=yes` and `send_pai=yes`.

### Normalizing to E.164

E.164 is the international number format: a leading `+`, country code, then the
national number, with no spaces or punctuation (for example `+5548999990000` or
`+14155550100`). Carriers increasingly expect — or require — E.164 on the trunk.
Rather than scatter formatting across the dialplan, normalize once in the outbound
context.

A North-American example that accepts a 10-digit local number, an 11-digit
`1`-prefixed number, or an already-E.164 number, and always presents `+1…` to the
trunk:

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

Some providers want the `+`; others want the bare digits. If yours rejects the
`+`, strip it on the way out with `${EXTEN:1}` in the `Dial`. The point is that
all the format knowledge lives in one place, so switching providers — or adding a
second one — is a one-line change.

## Failover and least-cost routing

एक ट्रंक होने पर, प्रोवाइडर आउटेज का मतलब है कोई आउटबाउंड कॉल नहीं होना। दो या अधिक ट्रंक होने पर, आप स्वचालित रूप से फेलओवर कर सकते हैं और यहाँ तक कि प्रत्येक गंतव्य के लिए सबसे सस्ता मार्ग चुन सकते हैं — *least-cost routing* (LCR)।

### Failover with `${DIALSTATUS}`

`Dial()` जब यह रिटर्न करता है तो `${DIALSTATUS}` चैनल वेरिएबल सेट करता है। फेलओवर के लिए आपके लिए महत्वपूर्ण मान हैं `CHANUNAVAIL` (ट्रंक बिल्कुल नहीं पहुँच सका) और `CONGESTION` (कॉल रिजेक्ट हो गई, जैसे सभी सर्किट व्यस्त)। प्राथमिक ट्रंक को आज़माएँ; यदि वह कॉल ले नहीं सकता, तो बैकअप पर जाएँ:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

ध्यान दें कि जानबूझकर **नहीं** फेलओवर किया गया है `BUSY` या `NOANSWER` पर — इनका मतलब है कि *कॉल किए गए पक्ष* तक पहुँच गया और उसने इनकार कर दिया, इसलिए किसी अन्य ट्रंक पर पुनः प्रयास करने से वह फ़ोन फिर से बजेगा जिसने पहले ही नहीं कहा था (और यह आपको दूसरी कॉल की लागत दे सकता है)। केवल तब रीरूट करें जब *ट्रंक स्वयं* विफल हो।

### A reusable routing subroutine

हर डायल पैटर्न के लिए इस लॉजिक को दोहराना त्रुटिप्रवण होता है। इसे एक `GoSub` सबरूटीन में फैक्टर करें जो गंतव्य नंबर लेता है और क्रम में प्रत्येक ट्रंक को आज़माता है:

```
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

अब हर आउटबाउंड पैटर्न केवल एक `GoSub` कॉल है, और ट्रंक क्रम बिल्कुल एक ही जगह पर परिभाषित है।

### Least-cost routing by destination

सही LCR कॉल के गंतव्य के आधार पर ट्रंक चुनता है। एक सामान्य पैटर्न है गंतव्य प्रीफ़िक्स से मिलाना और प्रत्येक कॉल वर्ग को उस प्रोवाइडर को भेजना जो उसके लिए सबसे सस्ता हो — उदाहरण के लिए, अंतरराष्ट्रीय कॉल को एक होलसेल कैरियर को और स्थानीय/राष्ट्रीय कॉल को आपके प्राथमिक को:

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

कई प्रीफ़िक्स होने पर, रूट टेबल को डेटाबेस (`func_odbc`/`AstDB`) में रखें और प्रीफ़िक्स के आधार पर ट्रंक को लुक‑अप करें, बजाय हार्ड‑कोडिंग पैटर्न के। डायलप्लान छोटा रहता है और रेट्स एक टेबल में होते हैं जिन्हें आप लॉजिक री‑लोड किए बिना संपादित कर सकते हैं।

## NAT and trunks

NAT ट्रंक समस्याओं का सबसे आम कारण है — आमतौर पर एक‑तरफ़ा ऑडियो, या ऐसा ट्रंक जो रजिस्टर तो हो जाता है लेकिन इनबाउंड कॉल नहीं प्राप्त करता। कारण फोन की तरह ही है (*SIP & PJSIP in depth* और *Designing a VoIP network* में कवर किया गया): Asterisk SIP और SDP में अपने पते का अपना विचार विज्ञापित करता है, और NAT के पीछे यह एक निजी RFC 1918 पता होता है जिसे प्रदाता वापस रूट नहीं कर सकता।

ट्रंक के लिए समाधान दो भागों में होता है — **transport** (आपका सार्वजनिक पता) पर सेटिंग्स और **endpoint** (प्रदाता के मीडिया को कैसे संभालें) पर सेटिंग्स।

### On the transport — your public address

जब Asterisk सर्वर स्वयं NAT के पीछे हो (क्लाउड या ऑन‑प्रेम बॉक्स जिसमें निजी IP और 1:1 सार्वजनिक IP हो), तो transport को उसका सार्वजनिक पता और कौन‑से नेटवर्क स्थानीय हैं, बताएँ। ये विकल्प एक बार `transport` पर सेट होते हैं, और उस पर सभी ट्रैफ़िक पर लागू होते हैं:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — सार्वजनिक IP जिसे Asterisk SIP हेडर (`Via`, `Contact`) में लिखता है उन गंतव्यों के लिए जो `local_net` के बाहर हैं।
- **`external_media_address`** — सार्वजनिक IP जिसे Asterisk SDP `c=` लाइन में लिखता है ताकि RTP सही जगह वापस आए। आमतौर पर सिग्नलिंग पते के समान।
- **`local_net`** — नेटवर्क जिन्हें Asterisk आंतरिक मानता है, इसलिए वह LAN पीयर्स के लिए पतों को पुनः लिखता नहीं है। सभी आंतरिक सबनेट सूचीबद्ध करें।

### On the endpoint — the provider's media

दूसरा भाग उस प्रदाता को संभालता है जो स्वयं NAT के पीछे बैठा है, या बस SDP में दिए गए पते से अलग पते से मीडिया भेजता है। इन्हें प्रत्येक ट्रंक endpoint के लिए सेट करें:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — मीडिया को Asterisk के माध्यम से ही प्रवाहित रखें, दोनो टोकन को सीधे बात करने न दें। NAT के पार यह आवश्यक है, और यदि आप कॉल रिकॉर्ड, ट्रांसकोड या मॉनिटर करना चाहते हैं तो अनिवार्य है।
- **`rtp_symmetric=yes`** — क्लासिक *comedia* व्यवहार: RTP को उस पते पर भेजें जहाँ से मीडिया वास्तव में आया है, न कि SDP में दावे किए गए पते पर।
- **`force_rport=yes`** — SIP का जवाब अनुरोध के स्रोत IP/पोर्ट (RFC 3581) से दें, बजाय `Via` हेडर पर भरोसा करने के।
- **`rewrite_contact=yes`** — इस endpoint से आने वाले इनबाउंड SIP संदेशों पर, `Contact` हेडर (या उपयुक्त `Record-Route` हेडर) को उस स्रोत IP पते और पोर्ट में पुनः लिखें जिससे पैकेट वास्तव में आया है। विकल्प के अपने दस्तावेज़ के अनुसार, यह “NAT के पीछे स्थित endpoint के साथ सर्वर संचार को आसान बनाता है” और “TCP और TLS जैसे विश्वसनीय ट्रांसपोर्ट कनेक्शन को पुनः उपयोग करने में मदद करता है।”

> **Recommendation — phones vs trunks.** `rewrite_contact` लगभग हमेशा फ़ोनों के लिए सही विकल्प है, क्योंकि उनका विज्ञापित संपर्क आमतौर पर एक निजी RFC 1918 पता होता है जिसे वापस रूट नहीं किया जा सकता। एक स्थिर IP‑आधारित ट्रंक पर प्रदाता का संपर्क आमतौर पर पहले से ही सही सार्वजनिक पता होता है, इसलिए उसे पुनः लिखना अक्सर अनावश्यक होता है; कुछ ऑपरेटर इसे केवल रजिस्ट्रेशन ट्रंक और NAT‑ड फ़ोनों के लिए सक्षम करना पसंद करते हैं। विकल्प का दस्तावेज़ित प्रभाव केवल ऊपर बताए गए इनबाउंड `Contact`/`Record-Route` पुनः लेखन तक सीमित है — इसलिए सुरक्षित अभ्यास यह है कि स्थिर ट्रंक पर इसे सक्रिय करने से पहले अपने विशिष्ट कैरियर के विरुद्ध परीक्षण करें।

आप किसी भी endpoint पर प्रभावी सेटिंग्स की पुष्टि कर सकते हैं
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, और बाकी सभी पैर

## लैब — एक मॉक ITSP दूसरे Asterisk और SIPp के साथ

आपको अभ्यास करने के लिए कोई पेड ट्रंक की जरूरत नहीं है। पुस्तक की लैब पहले से ही एक Asterisk
22.10.0 कंटेनर और एक SIPp कंटेनर को निजी `172.30.0.0/24` नेटवर्क पर चलाती है; हम
SIPp कंटेनर को "कैरियर" मानेंगे जो इनबाउंड कॉल्स करता है, और एक
ट्रंक एंडपॉइंट जोड़ेंगे जो उन कॉल्स को `from-pstn` कॉन्टेक्स्ट में लैंड कराता है।

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. ट्रंक एंडपॉइंट जोड़ें

एक IP-आधारित ट्रंक `lab/asterisk/etc/pjsip.conf` में जोड़ें जो लैब के SIPp
होस्ट से मेल खाता है और इनबाउंड कॉल्स को `from-pstn` में लैंड कराता है:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. इनबाउंड DID को रूट करें

`lab/asterisk/etc/extensions.conf` में, एक `from-pstn` कॉन्टेक्स्ट जोड़ें जो
उस DID का उत्तर देता है जिसे मॉक कैरियर डायल करेगा और उसे वापस प्ले करता है, फिर एक आउटबाउंड नियम जोड़ें:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

दोनों फ़ाइलों को रीलोड करें (`core reload`) और ट्रंक लोड हुआ है यह सत्यापित करें:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. ट्रंक के माध्यम से एक इनबाउंड कॉल रखें

PBX पर एक SIPp सीनारियो को DID को टारगेट यूज़र के रूप में सेट करके पॉइंट करें। लैब पहले से ही
`lab/sipp/uac_9000.xml` प्रदान करती है, जो एक्सटेंशन `9000` को INVITE करती है; इसे
`uac_did.xml` पर कॉपी करें और request-URI/`To` यूज़र को `9000` से `4830001000` में बदलें,
फिर इसे SIPp कंटेनर से चलाएँ:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

कॉल को Asterisk कंसोल पर `from-pstn` पर हिट होते देखें (`pjsip set logger on`
इनबाउंड INVITE दिखाता है; `core show channels` `PJSIP/itsp-…` चैनल को
`demo-congrats` प्ले होते हुए दिखाता है)। क्योंकि SIPp स्रोत IP `identify` से मेल खाता है,
कॉल बिना ऑथेंटिकेशन के स्वीकार हो जाता है — बिल्कुल वही जैसा एक स्थैतिक कैरियर ट्रंक
व्यवहार करता है।

### 4. ट्रंक का निरीक्षण करें

अपने नोट्स के लिए ट्रंक की पूरी कॉन्फ़िगरेशन कैप्चर करें:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) इसे एक रजिस्ट्रेशन ट्रंक बनाएं

*दूसरे* Asterisk कंटेनर को एक वास्तविक रजिस्टार के रूप में सेट करें: उसे एक
`endpoint`+`auth`+`aor` दें अकाउंट `4830001000` के लिए, फिर PBX पर
`identify` ब्लॉक को इस अध्याय की शुरुआत से `registration` ब्लॉक से बदलें
(जो `server_uri` को दूसरे कंटेनर के IP की ओर इशारा करता है)। पुष्टि करें
`pjsip show registrations` से कि स्टेटस `Registered` पढ़ता है, फिर प्रत्येक दिशा में एक कॉल रखें।

## Summary

एक SIP ट्रंक आपके PBX को बाहरी दुनिया से जोड़ता है, और PJSIP में यह बस वही
endpoint है जो आप पहले से जानते हैं `endpoint` + `auth` + `aor` परिवार से बना,
प्लस एक `identify` या एक `registration`। जब प्रदाता आपको उपयोगकर्ता नाम
और पासवर्ड देता है तो **registration trunk** (`type=registration` with `outbound_auth`) का उपयोग करें;
जब प्रमाणीकरण स्रोत IP द्वारा किया जाता है तो **IP-based trunk** (`type=identify` with `match`) का उपयोग करें — और बाद वाले को एक संकीर्ण `match`
और एक `acl` के साथ लॉक करें, क्योंकि अनप्रमाणित ट्रंक टोल-धोखाधड़ी का लक्ष्य होता है। इनबाउंड,
प्रदाता का DID आपके `from-pstn` context में `${EXTEN}` के रूप में आता है, जहाँ आप
इसे एक एक्सटेंशन, एक IVR, या एक क्यू में रूट करते हैं — पैटर्न और `${EXTEN:-N}` DID ब्लॉकों को कॉम्पैक्ट रखते हैं। आउटबाउंड, `CALLERID(num)` को अपने स्वामित्व वाले नंबर पर सेट करें, एक ही जगह E.164 में सामान्यीकृत करें, और कॉल को `PJSIP/<number>@trunk` को सौंपें। कई ट्रंकों को आज़माकर और `${DIALSTATUS}` पर शाखा बनाकर (`CHANUNAVAIL`/`CONGESTION` का अर्थ पुनः‑रूट है; `BUSY`/`NOANSWER` नहीं), लिस्ट‑कॉस्ट रूटिंग को एक `GoSub` तालिका में रखें। अंत में, ट्रंकों के लिए NAT दो‑तरफ़ा है:
`external_media_address`/`external_signaling_address`/`local_net` आपके सार्वजनिक पते के **transport** पर, और `direct_media=no`, `rtp_symmetric`,
`force_rport`, और `rewrite_contact` प्रदाता के मीडिया के **endpoint** पर।

## Quiz

1. PJSIP में, *outbound* कॉल या प्रोवाइडर को रजिस्ट्रेशन के लिए उपयोग किए जाने वाले क्रेडेंशियल्स को संदर्भित किया जाता है:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. आपको एक `type=registration` ट्रंक का उपयोग तब करना चाहिए जब:
   - A. प्रोवाइडर आपको आपके स्रोत IP पते से पहचानता है।
   - B. प्रोवाइडर आपको एक उपयोगकर्ता नाम और पासवर्ड देता है और आपसे लॉग इन करने की अपेक्षा करता है।
   - C. आप कभी नहीं चाहते कि Asterisk एक `REGISTER` भेजे।
   - D. ट्रंक दो स्थिर-IP सर्वरों के बीच है जिन्हें आप नियंत्रित करते हैं।
3. `identify` ऑब्जेक्ट का `match` विकल्प (सभी लागू विकल्प चुनें) स्वीकार करता है:
   - A. एक IP पता
   - B. एक CIDR रेंज
   - C. एक होस्टनेम (कॉन्फ़िग-लोड समय पर रिज़ॉल्व्ड)
   - D. केवल एक SIP उपयोगकर्ता नाम
4. Asterisk 22 पर, `auth_type=userpass` है:
   - A. एकमात्र वैध मान
   - B. अप्रचलित और `digest` में परिवर्तित
   - C. हटा दिया गया और लोड त्रुटि उत्पन्न करता है
   - D. आउटबाउंड रजिस्ट्रेशन के लिए आवश्यक
5. एक इनबाउंड DID नंबर डायलप्लान में इस प्रकार आता है:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` ट्रंक एंडपॉइंट के `context` में
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. डायल किए गए DID `4830003007` के अंतिम दो अंक को एक एक्सटेंशन को भेजने के लिए, आप उपयोग करेंगे:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. एक ट्रंक पर `Dial()` के बाद, आपको बैकअप ट्रंक पर फेलओवर करना चाहिए जिसमें `${DIALSTATUS}` मान (दो चुनें)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. डायल आउट करने से पहले प्रोवाइडर को प्रस्तुत किए जाने वाले कॉलर-ID नंबर को सेट करने के लिए उपयोग करें:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. विकल्प जो Asterisk को उसके *public* पते के बारे में बताते हैं जब सर्वर NAT के पीछे हो, सेट किए जाते हैं:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. एक ट्रंक एंडपॉइंट पर `rtp_symmetric=yes` Asterisk को करता है:
    - A. RTP को SRTP के साथ एन्क्रिप्ट करता है
    - B. RTP को उस पते पर भेजता है जहाँ मीडिया वास्तव में आया था, SDP को अनदेखा करता है
    - C. RTP को पूरी तरह से निष्क्रिय करता है
    - D. एंडपॉइंट्स के बीच सीधे मीडिया को मजबूर करता है

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
