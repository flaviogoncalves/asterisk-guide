# SIP & PJSIP in depth

SIP प्रोटोकॉल है; PJSIP वह तरीका है जिससे Asterisk 22 इसे उपयोग करता है। **PJSIP** (`chan_pjsip`, configured via `pjsip.conf`) Asterisk 22 LTS में एकमात्र SIP चैनल ड्राइवर है। यह अध्याय SIP प्रोटोकॉल की बुनियादी बातें (जो प्रोटोकॉल‑स्तर की हैं और 100 % वैध रहती हैं) तथा वह PJSIP ऑब्जेक्ट मॉडल और कॉन्फ़िगरेशन कवर करता है जिसका आप रोज़ाना उपयोग करते हैं। पुराने लेगेसी ड्राइवर और माइग्रेशन गाइड *Legacy channels* अध्याय में कवर किए गए हैं।

## Objectives

By the end of this chapter, you should be able to:

- Explain the role of the SIP user agents, proxies, registrar, and gateways;
- Follow a basic SIP call flow (REGISTER, INVITE, provisional and final responses, ACK, BYE) and read a SIP message;
- Describe how SDP negotiates the media session and how NAT affects SIP signaling and RTP;
- Map the PJSIP object model — `endpoint`, `auth`, `aor`, `transport`, `identify`, and `registration` — and how the objects reference one another;
- Configure SIP phones and trunks in `pjsip.conf`, including the NAT-traversal options; and
- Verify and troubleshoot endpoints with the `pjsip show …` CLI commands.

## SIP प्रोटोकॉल मूलभूत बातें

Session Initiation Protocol (SIP) एक टेक्स्ट‑आधारित प्रोटोकॉल है जो HTTP और SMTP के समान है और इसे उपयोगकर्ताओं के बीच इंटरैक्टिव संचार सत्रों को प्रारम्भ, बनाए रखने और समाप्त करने के लिए डिज़ाइन किया गया था। इन सत्रों में आवाज़, वीडियो, चैट, इंटरैक्टिव गेम और अन्य चीज़ें शामिल हो सकती हैं। SIP को IETF द्वारा परिभाषित किया गया था और यह आवाज़ संचार के लिए डि‑फैक्टो मानक बन गया है। यह समझना बहुत महत्वपूर्ण है कि SIP कैसे काम करता है। Asterisk 22 में SIP कॉन्फ़िगरेशन `pjsip.conf` में स्थित है, जो SIP‑आधारित सिस्टम पर सबसे अधिक बार संपादित की जाने वाली फ़ाइलों में से एक है (केवल `extensions.conf` के बाद)।

### ऑपरेशन का सिद्धांत

SIP एक सिग्नलिंग प्रोटोकॉल है जिसमें निम्नलिखित घटक होते हैं: User Agent Client, User Agent Servers, SIP Proxies, और SIP Gateways. निम्नलिखित चित्र इन घटकों के बीच के संबंधों को दर्शाता है।

- UAC (user agent client) – वह क्लाइंट या टर्मिनल जो SIP सिग्नलिंग को प्रारम्भ करता है।  
- UAS (user agent server) – वह सर्वर जो UAC से आने वाले SIP सिग्नलिंग का उत्तर देता है।  
- UA (user agent) – SIP टर्मिनल (फ़ोन या गेटवे जिनमें UAC और UAS दोनों होते हैं)।  
- Proxy Server – UA से अनुरोध प्राप्त करता है और यदि विशेष स्टेशन उनके प्रशासन में नहीं है तो अन्य SIP प्रॉक्सी को स्थानांतरित करता है।  
- Redirect Server – अनुरोध प्राप्त करता है और उन्हें सीधे गंतव्य पर अग्रेषित करने के बजाय, गंतव्य डेटा सहित उन्हें वापस UA को भेजता है।  
- Location Server – UA से अनुरोध प्राप्त करता है और इस जानकारी के साथ लोकेशन डेटाबेस को अपडेट करता है।

Usually, the proxy, redirect, and location servers are hosted within the same hardware and use the same piece of software, which we call the SIP proxy. The SIP proxy is responsible for location database maintenance, connection establishment, and session termination.

![मुख्य SIP घटक: उपयोगकर्ता एजेंट (UAC/UAS/UA), रजिस्ट्रार/प्रॉक्सी/रीडायरेक्ट सर्वर, और PSTN के लिए एक गेटवे, जिसमें RTP मीडिया सीधे एंडपॉइंट्स के बीच प्रवाहित होता है](../images/07-sip-and-pjsip-fig01.png)

#### SIP रजिस्टर प्रक्रिया

फ़ोन को कॉल प्राप्त करने से पहले उसे लोकेशन डेटाबेस में रजिस्टर किया जाना चाहिए। लोकेशन डेटाबेस में, IP पता नाम से बंधा होगा। निम्न उदाहरण में, एक्सटेंशन 8500 को IP पता 200.180.1.1 से बंधा जाएगा। आपको अनिवार्य रूप से फ़ोन नंबरों का उपयोग करने की आवश्यकता नहीं है। SIP आर्किटेक्चर में, रजिस्टर्ड एक्सटेंशन flavio@voip.school भी हो सकता है।

![SIP पंजीकरण: फोन 8500 एक्सटेंशन के साथ REGISTER बाइंडिंग अपने IP पते पर भेजता है, रजिस्ट्रार संपर्क को लोकेशन डेटाबेस में संग्रहीत करता है और 200 OK के साथ उत्तर देता है](../images/07-sip-and-pjsip-fig02.png)

#### प्रॉक्सी संचालन

जब SIP प्रॉक्सी के रूप में कार्य करता है, तो SIP सर्वर सिग्नलिंग के बीच में रहता है और उन्नत रूटिंग और बिलिंग करने में सक्षम होता है। मीडिया फ्लो, जो रियल टाइम प्रोटोकॉल (RTP) पर आधारित है, अभी भी एंडपॉइंट्स के बीच सीधे जाता है।

![प्रॉक्सी संचालन: SIP प्रॉक्सी सिग्नलिंग पथ (INVITE/200 OK) में रहता है और लोकेशन सर्वर में कॉलि को खोजता है, जबकि RTP मीडिया दो एंडपॉइंट्स के बीच सीधे प्रवाहित होता है](../images/07-sip-and-pjsip-fig03.png)

#### पुनर्निर्देशन संचालन

जब रीडायरेक्ट किया जाता है, तो SIP सर्वर बस एक संदेश (जैसे, 302 moved temporarily) उपयोगकर्ता एजेंट को भेजता है और नए संदेशों के मार्ग से बाहर रहता है। यह संसाधन उपयोग के मामले में बहुत हल्का होता है, लेकिन आपके पास बिल्कुल भी नियंत्रण नहीं रहता। रीडायरेक्शन कभी‑कभी लोड बैलेंस डिज़ाइनों में उपयोग किया जाता है।

![रीडायरेक्ट ऑपरेशन: रीडायरेक्ट सर्वर INVITE का जवाब 302 Moved Temporarily के साथ देता है जिसमें संपर्क शामिल है, फिर कॉलर द्वारा नया स्थान पर सीधे INVITE/ACK पुनः भेजे जाने तक पीछे हट जाता है](../images/07-sip-and-pjsip-fig04.png)

#### Asterisk SIP को कैसे संभालता है

यह समझना महत्वपूर्ण है कि Asterisk न तो एक SIP प्रॉक्सी है और न ही एक SIP रीडायरेक्टर। Asterisk रजिस्ट्रार और लोकेशन सर्वर की भूमिका निभा सकता है; हालांकि, यह केवल दो UACs को अपने साथ जोड़ता है। इसलिए, Asterisk को बैक‑टू‑बैक यूज़र एजेंट (B2BUA) माना जाता है। दूसरे शब्दों में, यह दो SIP चैनलों को जोड़ता है और उन्हें आपस में ब्रिज करता है। Asterisk में एक री‑इनवाइट मैकेनिज़्म है जो SIP चैनलों को सीधे एक‑दूसरे से बात करने की अनुमति देता है, बजाय इसके कि वे Asterisk के माध्यम से गुजरें। एक PJSIP एंडपॉइंट पर यह पैरामीटर `direct_media` द्वारा नियंत्रित होता है। `direct_media=yes` का उपयोग करने पर RTP फ्लो सीधे एक एंडपॉइंट से दूसरे एंडपॉइंट तक जाता है, जिससे सर्वर संसाधन मुक्त होते हैं।

#### SIP संचालन direct_media=yes के साथ

![directmedia=yes के साथ SIP संचालन: SIP संकेत Asterisk के माध्यम से प्रवाहित होते हैं जबकि RTP ऑडियो दो फ़ोनों के बीच सीधे जाता है, जिससे सर्वर संसाधन मुक्त होते हैं](../images/07-sip-and-pjsip-fig05.png)

हालांकि, यदि आपको Asterisk का उपयोग करके कॉल को ट्रांसफ़र या रिकॉर्ड करने की आवश्यकता है, तो आप पैरामीटर `direct_media=no` का उपयोग करके RTP प्रवाह को Asterisk सर्वर के माध्यम से मजबूर कर सकते हैं।

#### direct_media=no के साथ SIP संचालन

![directmedia=no के साथ SIP संचालन: दोनों SIP सिग्नलिंग और RTP ऑडियो Asterisk के माध्यम से एंकर किए जाते हैं, जिससे यह कॉल को रिकॉर्ड, ट्रांसकोड या ट्रांसफ़र कर सकता है](../images/07-sip-and-pjsip-fig06.png)

#### SIP संदेश

बेसिक SIP संदेश हैं:

- INVITE – कनेक्शन स्थापित करना  
- ACK – स्वीकृति देना  
- BYE – कनेक्शन समाप्त करना  
- CANCEL – गैर-स्थापित कॉल के लिए कनेक्शन समाप्त करना  
- REGISTER – UAC को SIP प्रॉक्सी पर पंजीकृत करना  
- OPTIONS – उपलब्धता जाँचने के लिए उपयोग किया जा सकता है  
- REFER – SIP कॉल को किसी और को स्थानांतरित करना  
- SUBSCRIBE – सूचना घटनाओं की सदस्यता लेना  
- NOTIFY – चैनल जानकारी भेजना  
- INFO – विभिन्न संदेश भेजना (जैसे, DTMF )  
- MESSAGE – त्वरित संदेश भेजना

SIP प्रतिक्रियाएँ टेक्स्ट फ़ॉर्मेट में होती हैं और आसानी से पढ़ी जा सकती हैं (HTTP संदेशों के समान)। सबसे महत्वपूर्ण प्रतिक्रियाएँ हैं:

- 1XX – सूचना संदेश (100–trying, 180–ringing, 183–progress)  
- 2XX – सफल अनुरोध पूर्ण (200 – OK)  
- 3XX – कॉल पुनर्निर्देशन, अनुरोध को किसी अन्य स्थान पर निर्देशित करना होगा (302 – moved temporarily, 305 – use proxy)  
- 4XX – त्रुटि (403 – Forbidden)  
- 5XX – सर्वर त्रुटि (500 – Internal Server Error; 501 – Not implemented)  
- 6XX – वैश्विक विफलता (606 – Not acceptable)

उदाहरण के लिए:

```
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP
192.168.1.116;rport;branch=z9hG4bKc0a8017400000063452fafbb00006967000000d2
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest
username="2001",realm="asterisk",nonce="6c55905e",uri="sip:2000@192.168.1.133",
response="983c0099eea125d8cdfe93b0ec99f3ec",algorithm=MD5
```

#### सत्र विवरण प्रोटोकॉल (SDP)

SDP मूल रूप से IETF RFC 2327 में परिभाषित किया गया था, जिसे अब RFC 4566 द्वारा अप्रचलित कर दिया गया है। यह सत्र घोषणा, सत्र निमंत्रण, और अन्य प्रकार के मल्टीमीडिया सत्र आरंभ करने के उद्देश्यों के लिए मल्टीमीडिया सत्रों का वर्णन करने के लिए बनाया गया है। SDP में शामिल हैं:

- ट्रांसपोर्ट प्रोटोकॉल (RTP/UDP/IP)
- मीडिया का प्रकार (टेक्स्ट, ऑडियो, वीडियो)
- मीडिया फ़ॉर्मेट या कोडेक (H.261 वीडियो, g.711 ऑडियो, आदि)
- इन मीडिया को प्राप्त करने के लिए आवश्यक जानकारी (पते, पोर्ट, आदि)

निम्नलिखित उदाहरण दो फ़ोनों के बीच एक कॉल का वर्णन करने वाले SDP का प्रतिलेख है।

```
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
a=setup:active
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:97 iLBC/8000
a=rtpmap:98 iLBC/8000
a=fmtp:98 mode=20
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

### SIP NAT ट्रैवर्सल

Network Address Translation (NAT) अधिकांश नेटवर्कों द्वारा इंटरनेट IP पतों को बचाने के लिए उपयोग की जाने वाली एक सुविधा है। आमतौर पर, एक कंपनी को IP पतों का एक छोटा ब्लॉक मिलता है, और अंतिम उपयोगकर्ता इंटरनेट से जुड़ने पर गतिशील रूप से एक IP पता प्राप्त करता है। NAT आंतरिक पतों को बाहरी पतों में मैप करके पता समस्या का समाधान करता है। यह अपने मेमोरी में आंतरिक से बाहरी पतों का मैपिंग संग्रहीत करता है। यह मैपिंग एक निश्चित अवधि के लिए वैध रहती है, जिसके बाद यह हटा दी जाती है। मैपिंग आंतरिक और बाहरी पतों के लिए IP:port जोड़े का उपयोग करती है। चार प्रकार के NAT मौजूद हैं:

- फुल कोन
- रेस्ट्रिक्टेड कोन
- पोर्ट रेस्ट्रिक्टेड कोन
- सिमेट्रिक

NAT सिद्धांत नीचे — चार NAT प्रकार, Contact-header समस्या, keep-alives, और सर्वर के माध्यम से मीडिया को मजबूर करना — प्रोटोकॉल‑स्तर का है और किसी भी SIP कार्यान्वयन पर लागू होता है। Asterisk 22 (PJSIP) पर प्रत्येक व्यवहार को कैसे कॉन्फ़िगर करें, इस अध्याय में बाद में *Nat traversal on res_pjsip* के तहत कवर किया गया है।

#### फ़ुल कोन

पहला NAT, फुल कोन, बाहरी IP:port जोड़ी से आंतरिक IP:port जोड़ी तक एक स्थिर मैपिंग का प्रतिनिधित्व करता है। कोई भी बाहरी कंप्यूटर बाहरी IP:port जोड़ी का उपयोग करके इससे कनेक्ट हो सकता है। यह उन गैर-स्टेटफुल फ़ायरवॉल्स में लागू होता है जो फ़िल्टरों के उपयोग से बनते हैं।

![Full Cone NAT: आंतरिक होस्ट (10.0.0.1:8000) को स्थिर रूप से बाहरी जोड़ी 200.180.4.168:1234 पर मैप किया गया है, इसलिए कोई भी बाहरी कंप्यूटर उस जोड़ी को पैकेट भेज सकता है और आंतरिक होस्ट तक पहुंच सकता है](../images/07-sip-and-pjsip-fig11.png)

#### प्रतिबंधित शंकु

सीमित कोन परिदृश्य में, बाहरी IP:पोर्ट जोड़ी केवल तब खुलती है जब आंतरिक कंप्यूटर बाहर के पते पर डेटा भेजता है। हालांकि, सीमित कोन NAT किसी अलग पते से आने वाले पैकेटों को ब्लॉक कर देता है। दूसरे शब्दों में, आंतरिक कंप्यूटर को डेटा वापस भेजने से पहले बाहरी कंप्यूटर को डेटा भेजना पड़ता है।

#### पोर्ट प्रतिबंधित कोन

पोर्ट प्रतिबंधित कोन फ़ायरवॉल लगभग प्रतिबंधित कोन के समान है। केवल अंतर यह है कि अब, आने वाला पैकेट ठीक उसी IP और पोर्ट से होना चाहिए जिससे पैकेट भेजा गया था।

#### सममित

अंतिम प्रकार का NAT को सिमेट्रिक कहा जाता है। यह पहले तीन प्रकारों से अलग है क्योंकि प्रत्येक बाहरी पते के लिए एक विशिष्ट मैपिंग की जाती है। केवल विशिष्ट बाहरी पतों को NAT मैपिंग द्वारा वापस आने की अनुमति होती है। यह भविष्यवाणी करना संभव नहीं है कि NAT डिवाइस द्वारा कौन सा बाहरी IP:port जोड़ा उपयोग किया जाएगा। अन्य तीन प्रकार के NAT बाहरी सर्वर का उपयोग करके संचार के लिए बाहरी IP पता खोजने की अनुमति देते हैं। सिमेट्रिक NAT के साथ, भले ही आप किसी बाहरी सर्वर से कनेक्ट कर सकें, खोजा गया पता केवल उसी सर्वर के अलावा किसी अन्य डिवाइस के लिए उपयोग नहीं किया जा सकता।

![Symmetric NAT: प्रत्येक गंतव्य के लिए एक अलग बाहरी स्रोत पोर्ट आवंटित किया जाता है, इसलिए एक सर्वर की ओर खोजा गया मैपिंग दूसरे होस्ट द्वारा पुन: उपयोग नहीं किया जा सकता, जिससे STUN-आधारित ट्रैवर्सल टूट जाता है](../images/07-sip-and-pjsip-fig12.png)

#### NAT फ़ायरवॉल तालिका

निम्न तालिका चार प्रकार के NAT का सारांश प्रस्तुत करती है।

| NAT प्रकार | डेटा पहले भेजना आवश्यक | रिटर्न पैकेट्स के लिए बाहरी IP:पोर्ट निर्धारित कर सकता है | इनकमिंग पैकेट्स को गंतव्य IP:पोर्ट तक सीमित करता है |
| --- | --- | --- | --- |
| Full Cone | नहीं | हाँ | नहीं |
| Restricted Cone | हाँ | हाँ | केवल IP |
| Port Restricted Cone | हाँ | हाँ | हाँ |
| Symmetric | हाँ | नहीं | हाँ |

#### SIP संकेत और RTP NAT के ऊपर

कुछ सबसे बड़े मुद्दे NAT ट्रैवर्सल में यह हैं कि आपको दो समस्याओं को हल करना पड़ता है: SIP सिग्नलिंग और ऑडियो (RTP)। एक‑तरफ़ा ऑडियो की अधिकांश समस्याएँ NAT से संबंधित होती हैं। SIP के बारे में एक दिलचस्प बात यह है कि जब एक UAC पैकेट भेजता है, तो वह SIP “Contact” हेडर फ़ील्ड में IP पता एम्बेड कर देता है। आमतौर पर यह एक आंतरिक (RFC1918) पता होता है; इस पैकेट के जवाब इंटरनेट के माध्यम से UAC तक रूट नहीं किए जा सकते। अवधारणात्मक समाधान हमेशा समान होते हैं:

- **Ignore the Contact/Via address and reply to where the packet actually came from.** This is the behaviour defined in RFC 3581 (`rport`). On PJSIP it is `force_rport=yes`, and `rewrite_contact=yes` rewrites the stored contact to the source address.
- **Send media back to the address the RTP actually arrived from** (symmetric RTP, historically called *comedia*). On PJSIP this is `rtp_symmetric=yes`.
- **Keep the NAT mapping open.** If the mapping times out, Asterisk can no longer send an INVITE to the UAC — the phone can place calls but not receive them. Sending a periodic OPTIONS (a *qualify*) keeps the pinhole open. On PJSIP this is `qualify_frequency=` on the AOR.

यदि उपयोगकर्ता का NAT सममित प्रकार का है, तो एक UAC से दूसरे UAC को सीधे पैकेट भेजना संभव नहीं है; ऐसे मामले में आपको RTP को Asterisk के माध्यम से `direct_media=no` के साथ मजबूर करना पड़ता है। ये कॉन्फ़िगरेशन अधिकांश मामलों के लिए उपयुक्त हैं। ट्रैफ़िक को उन्नत तकनीकों जैसे Simple Traversal of UDP over NAT (STUN) का उपयोग करके अनुकूलित किया जा सकता है, जो पूर्ण कोन, प्रतिबंधित कोन, और पोर्ट प्रतिबंधित कोन, तथा Application Layer Gateway (ALG) के साथ उपयोगी है। दुर्भाग्यवश, आज के अधिकांश फ़ायरवॉल — यहाँ तक कि घर के DSL/केबल राउटर भी — सममित होते हैं, जिससे STUN अनुपयोगी हो जाता है। ALG समस्या का समाधान कर सकता है, लेकिन यह अधिकांश मामलों में समर्थित, लागू या बग‑रहित नहीं है।

#### NAT के पीछे Asterisk

कभी‑कभी Asterisk सर्वर स्वयं फ़ायरवॉल के पीछे NAT के साथ लागू किया जाता है — क्लाउड में डिप्लॉय करते समय यह एक बहुत आम स्थिति है। इस मामले में यह आवश्यक है कि कुछ अतिरिक्त कॉन्फ़िगरेशन किया जाए ताकि Asterisk SIP और SDP हेडर्स में अपने निजी पते के बजाय **सार्वजनिक** पता विज्ञापित करे।

Conceptually there are three steps:

- फ़ायरवॉल से Asterisk सर्वर तक SIP सिग्नलिंग पोर्ट (डिफ़ॉल्ट रूप से UDP 5060) को फ़ॉरवर्ड करें।
- फ़ायरवॉल से Asterisk सर्वर तक RTP मीडिया पोर्ट रेंज (डिफ़ॉल्ट रूप से UDP 10000–20000, `rtp.conf` में सेट) को फ़ॉरवर्ड करें।
- Asterisk को उसका बाहरी पता और कौन सा नेटवर्क स्थानीय है बताएं, ताकि वह हेडर में सार्वजनिक पता डालते समय जान सके।

On PJSIP these last two items map to `external_media_address` / `external_signaling_address` and `local_net=` on the **transport**, and the RTP port range is still configured in `rtp.conf`:

```
; RTP Configuration
;
[general]
;
; RTP start and RTP end configure start and end addresses
;
rtpstart=10000
rtpend=20000
```

The complete, worked PJSIP configuration for an Asterisk server behind NAT is given later in this chapter under *Asterisk Server behind NAT*.

### SIP सीमाएँ

Asterisk incoming RTP flow का उपयोग outgoing flow को synchronize करने के लिए करता है। यदि incoming flow बाधित हो (silence suppression), तो music‑on‑hold कट जाएगा। दूसरे शब्दों में, आपको Asterisk के साथ phones या providers में silence suppression का उपयोग नहीं करना चाहिए।

## PJSIP: the SIP channel

PJSIP Asterisk में SIP चैनल है। इसे पहली बार Asterisk 12 में पेश किया गया था और कई वर्षों के विकास के बाद यह डिफ़ॉल्ट और अनुशंसित SIP चैनल बन गया, और Asterisk 22 (वर्तमान LTS) में यह एकमात्र SIP चैनल ड्राइवर है। PJSIP Teluu के प्रोजेक्ट pjproject पर आधारित है। pjproject स्टैक कई सॉफ्टफ़ोन और व्यावसायिक SIP कार्यान्वयनों द्वारा उपयोग किया जाता है। यह एक बहुमुखी और परिपक्व SIP स्टैक है।

### Why to use PJSIP

PJSIP Asterisk के SIP संवाद को पूरी तरह से पुनः डिज़ाइन किया गया था, और यह समझना महत्वपूर्ण है कि किन विशेषताओं ने इसे मानक बना दिया।

#### Features

चैनल कई विशेषताओं का समर्थन करता है, जिनमें से कुछ का यहाँ उल्लेख किया गया है

- Multiple registrations: You may use more than one phone connected to the same Address of Record. In other words, you can connect two phones to the same endpoint.
- Friendly Application Program Interface (API). The API is modular and easy to extend, built from many small cooperating modules rather than one large block of code.
- Multiple transports: You can listen to multiple addresses, ports and transports when using PJSIP. You are not limited to a single bind address for all your devices. PJSIP is very flexible.

#### A note on configuration

PJSIP configuration is more verbose: it requires a little more effort and more lines of configuration, since each device is described by several related objects instead of one peer block. That extra structure is what gives PJSIP its flexibility, and the configuration wizard (covered later) keeps day-to-day provisioning short.

### PJSIP modules

The PJSIP channel is implemented by many modules described below:

#### res_pjsip

This is the base layer of PJSIP and the main module. It is responsible for some of the main services.

#### res_pjsip_session

This module is responsible for media sessions, session description protocol processing and some addons

#### res_pjsip_messaging

Process SIP messages and parse SIP headers.

#### res_pjsip_registrar

Responsible to handle SIP registrations

#### res_pjsip_pubsub

Responsible to process subscribe, notify and publish. These messages are responsible to handle SIP presence and BLF (Busy Lamp Field).

### PJSIP configuration

PJSIP has many different sections. The format of the section are:

```
[Section Name]
Option = Value
Option = Value
```

#### एंडपॉइंट सेक्शन

सबसे महत्वपूर्ण कॉन्फ़िगरेशन ऑब्जेक्ट endpoint है। endpoint कॉन्फ़िगरेशन में मुख्य कार्यक्षमता होती है और इसे एक AOR और Transport सेक्शन के साथ संबद्ध होना चाहिए। उदाहरण:

```
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

यदि आप ऊपर के उदाहरण को देखें, तो एंडपॉइंट सभी सेक्शन को आपस में जोड़ने वाला एक प्रकार का गोंद है। यह एक ट्रांसपोर्ट, एड्रेस ऑफ़ रिकॉर्ड और फ़ोन के लिए ऑथेंटिकेशन निर्दिष्ट करता है। साथ ही यह सबसे महत्वपूर्ण भाग, डायलप्लान में कॉन्टेक्स्ट एंट्री पॉइंट को परिभाषित करता है।

#### एड्रेस ऑफ़ रिकॉर्ड (AOR)

यह ऑब्जेक्ट एस्टेरिस्क को बताता है कि एंडपॉइंट से कहाँ संपर्क किया जाए। यह संपर्क पतों को संग्रहीत करता है। यह मेलबॉक्स की कॉन्फ़िगरेशन की भी अनुमति देता है। उदाहरण:

```
[softphone]
type=aor
max_contacts=2
```

#### प्रमाणीकरण

यह अनुभाग इनबाउंड और आउटबाउंड प्रमाणीकरण के लिए जिम्मेदार है। दस्तावेज़ उदाहरण फ़ाइल pjsip.conf में पाया जाता है। उदाहरण:

```
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
```

#### ट्रांसपोर्ट

ट्रांसपोर्ट सेक्शन आपको IPV4 और IPV6 पते तथा ट्रांसपोर्ट प्रोटोकॉल—TCP, UDP, TLS, Websockets आदि—परिभाषित करने की अनुमति देता है। आप इस सेक्शन में Natted पते भी कॉन्फ़िगर कर सकते हैं। आप कई ट्रांसपोर्ट बना सकते हैं, लेकिन वे एक ही IP और पोर्ट साझा नहीं कर सकते और आप एक ही IP संस्करण के कई TCP या TLS ट्रांसपोर्ट बाइंड नहीं कर सकते। Example:

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
```

#### पंजीकरण

यह ऑब्जेक्ट आउटबाउंड पंजीकरण को कॉन्फ़िगर करने के लिए उपयोग किया जाता है। उदाहरण:

```
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
```

#### पहचान

यह ऑब्जेक्ट नियंत्रित करता है कि प्रत्येक एंडपॉइंट से कौन‑सा SIP अनुरोध जुड़ा है। यदि आपके पास कोई identify सेक्शन नहीं है, तो सिस्टम “From” हेडर की सामग्री को एंडपॉइंट नाम से मिलाएगा। इस सेक्शन का उपयोग करके आप उपयोगकर्ता नाम या IP द्वारा पहचाने गए विशिष्ट एंडपॉइंट्स को विशिष्ट IP पते असाइन कर सकते हैं। उदाहरण:

```
[siptrunk]
type=identify
endpoint=siptrunk
match=52.37.87.85
```

#### ACL

ACL ऑब्जेक्ट आपको विशिष्ट नेटवर्क को एंडपॉइंट तक पहुँच देने के लिए कॉन्फ़िगर करने की अनुमति देता है। अब ACL को एक विशिष्ट सेक्शन या acl.conf में परिभाषित किया जाता है। उदाहरण:

```
[acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=209.16.236.0
permit=209.16.236.1
```

### Relationship between entities

The relationship between the configuration objects provides a great flexibility for configuration. However, it seems a bit complex for anyone starting.

![Relationships between PJSIP configuration objects: the endpoint links to transport, auth, and AOR (which holds contacts); registration ties to transport and auth; identify points at the endpoint, while ACL and domain alias stand alone](../images/07-sip-and-pjsip-fig14.png)

The graphic above means:

#### Relationships:

| Objects | Cardinality |
| --- | --- |
| ENDPOINT / AOR | many to many |
| ENDPOINT / AUTH | zero to many, to zero to one |
| ENDPOINT / IDENTIFY | zero to one |
| ENDPOINT / TRANSPORT | zero to many, to at least one |
| REGISTRATION / AUTH | zero to many, to zero to one |
| REGISTRATION / TRANSPORT | zero to many, to at least one |
| AOR / CONTACT | many to many |

ACL and DOMAIN_ALIAS don’t have a direct configuration relationship to the other objects.

### Configuring a Softphone

To configure a softphone you have to define many different sections. Below an example on how to configure a softphone. For the client side you can use the SipPulse Softphone (https://www.sippulse.com/produtos/softphone), which you can download and register against the endpoint below.

```
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060
[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#
[softphone]
type=aor
max_contacts=2
```

The configuration above sets a transport for UDP in the port 5060, then define an endpoint, its authentication by username and password and then the Address of Record with a maximum of two contacts.

### SIP ट्रंक को कॉन्फ़िगर करना

To configure a SIP trunk you need to have the IP address or Host of the SIP trunk, name and password. You have to create a new registration section for this purpose.

```
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk
[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret
[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999
[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

### Nat traversal on res_pjsip

नेटवर्क एड्रेस ट्रांसलेशन को बहुत समय पहले IPv4 पतों की कमी को दूर करने के लिए बनाया गया था। कई लोग NAT को एक सुरक्षा सुविधा के रूप में भी उपयोग करते हैं, जिससे नेटवर्क के आंतरिक पते सार्वजनिक इंटरनेट से छिपे रहते हैं। कभी‑कभी आपको NAT ट्रैवर्सल को संभालना पड़ता है। कुछ मामलों में, सर्वर NAT के पीछे हो सकता है, जैसे जब आप सर्वर को क्लाउड में डिप्लॉय कर रहे हों। अक्सर यदि आप क्लाउड में डिप्लॉय कर रहे हैं तो आपके उपयोगकर्ता भी एक NAT राउटर के पीछे होते हैं। चीज़ों को व्यवस्थित करने के लिए, हम इसे दो भागों में बाँटेंगे। पहला भाग क्लाउड डिप्लॉयमेंट जैसे NAT के पीछे स्थित Asterisk सर्वर है। दूसरे भाग में, हम देखेंगे कि कैसे res_pjsip का उपयोग करके NAT के पीछे स्थित क्लाइंट्स को सपोर्ट किया जाए।

#### Asterisk Server behind NAT

जब Asterisk सर्वर NAT के पीछे हो, तो आपको ट्रांसपोर्ट सेक्शन में बाहरी और आंतरिक स्थानीय पतों को सूचित करना चाहिए। हमें निम्नलिखित निर्देशों की आवश्यकता होगी।

##### direct_media

क्या मीडिया पीयर‑टू‑पीयर सीधे प्रवाहित होता है या सर्वर के माध्यम से? NAT के लिए इसे सर्वर के माध्यम से प्रवाहित होना चाहिए। NAT के लिए **no** चुनें। उदाहरण:

```
direct_media=no
```

##### external_media_address

बाहरी RTP को संभालने के लिए मीडिया पता। आमतौर पर यह external_signaling_address के समान होता है। मीडिया और सिग्नलिंग के लिए अपने सर्वर का सार्वजनिक IP पता उपयोग करें। उदाहरण:

```
external_media_address=54.232.1.20
```

##### external_signaling_address

बाहरी SIP पता जहाँ संदेश प्राप्त किए जाते हैं। उदाहरण:

```
external_signaling_address=54.232.1.20
```

##### local_net

आपके द्वारा स्थानीय नेटवर्क माना जाने वाला नेटवर्क। उदाहरण:

```
local_net=172.16.30.0/24
local_net=127.0.0.1/32
```

#### NAT के पीछे एक Asterisk सर्वर के लिए ट्रांसपोर्ट का पूर्ण उदाहरण

NAT के पीछे एक Asterisk सर्वर का उपयोग करने के लिए आपको दो चरण करने होंगे। पहला, NAT के पीछे एक ट्रांसपोर्ट परिभाषित करें। दूसरा, इस ट्रांसपोर्ट को endpoint से जोड़ें।

##### NAT के पीछे ट्रांसपोर्ट बनाना

NAT के पीछे ट्रांसपोर्ट बनाने के लिए pjsip.conf फ़ाइल में नीचे दिखाए अनुसार एक सेक्शन बनाएँ।

```
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

# ट्रांसपोर्ट को एक एंडपॉइंट से जोड़ें

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
auth=6000
aors=6000
```

SIP ट्रंक के लिए आपको नीचे दिखाए अनुसार ट्रांसपोर्ट को रजिस्ट्रेशन सेक्शन से भी जोड़ना चाहिए।

```
[siptrunk_reg]
type=registration
transport=tnat
server_uri=sip:sip.flagonc.com:5600
outbound_auth=siptrunk_auth
client_uri=sip:23456789@flagonc.com
contact_user=9999
```

#### Asterisk को NAT के पीछे क्लाइंट्स के साथ उपयोग करना

NAT के पीछे फ़ोन का उपयोग करने के लिए आपको प्रत्येक endpoint के लिए कुछ अतिरिक्त पैरामीटर कॉन्फ़िगर करने होंगे।

##### direct_media

क्या मीडिया सीधे peer‑to‑peer प्रवाहित होता है या सर्वर के माध्यम से? NAT के लिए इसे सर्वर के माध्यम से प्रवाहित होना चाहिए। Example:

```
direct_media=no
```

##### rtp_symmetric

यह वह है जिसे हम कॉमेडिया कहते हैं। SIP में सामान्यतः उपयोग किए जाने वाले इस SDP हेडर में परिभाषित पते पर निर्भर रहने के बजाय, पहले RTP पैकेट को प्राप्त करने वाले पते का उपयोग करें और उसी पते से वापस भेजें। उदाहरण:

```
rtp_symmetric=yes
```

##### force_rport

यह RFC3581 में परिभाषित व्यवहार है। VIA हेडर में दिए गए पते का उपयोग करने के बजाय, प्रतिक्रियाएँ उसी स्थान से भेजें जहाँ से अनुरोध आ रहे हैं। उदाहरण:

```
force_rport=yes
```

##### qualify_frequency

यह सेटिंग AOR पर लागू करनी होती है (एंडपॉइंट पर नहीं)। अंतिम चरण के रूप में, qualify विकल्प को कॉन्फ़िगर करना भी आवश्यक है। आपको हमेशा कुछ पैकेट्स को गंतव्य पर पिंग करते रहना चाहिए ताकि NAT मैपिंग खुली रहे। यह सेटिंग AOR सेक्शन में की जाती है। उदाहरण:

- qualify_frequency=15

एक एंडपॉइंट का पूर्ण उदाहरण जहाँ सर्वर और क्लाइंट दोनों NAT के पीछे हैं।

```
[6000]
type=endpoint
transport=tnat
context=from-internal
direct_media=no
force_rport=yes
rtp_symmetric=yes
auth=6000
aors=6000
[6000]
type=aor
qualify_frequency=15
```

### चैनल नामकरण

जैसा कि हमेशा होता है, चैनल का एक महत्वपूर्ण पहलू उसका नामकरण है और PJSIP में कुछ रोचक विवरण हैं। आप `PJSIP/` तकनीक के साथ एक PJSIP endpoint को डायल करते हैं:

```
exten=>6000,1,Dial(PJSIP/6000,20,tT)
```

एक उपयोगी सुविधा यह है कि एक ही बार में AOR में पंजीकृत सभी संपर्कों को डायल किया जा सके। फ़ंक्शन PJSIP_DIAL_CONTACTS को डायल करने के लिए संपर्कों की सूची में अनुवादित किया जाएगा।

```
exten=>6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)
```

ट्रंक को डायल करना थोड़ा अलग होता है। मान लीजिए कि ट्रंक आपके प्लेटफ़ॉर्म पर पंजीकृत नहीं होगा या आपके AOR रिकॉर्ड के साथ जुड़ा कोई IP पता नहीं है। आप लाइन में सीधे ट्रंक का पता निर्दिष्ट कर सकते हैं। इस उदाहरण के रूप में एक अंतरराष्ट्रीय डायल का उपयोग किया गया है।

```
exten=>9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

यदि आप ट्रंक का पता AOR सेक्शन में निर्दिष्ट करना पसंद करते हैं, तो आप इसका भी उपयोग कर सकते हैं।

```
exten=>9011.,1,Dial(PJSIP/${EXTEN:1}@siptrunk)
```

### PJSIP कॉन्फ़िगरेशन विज़ार्ड

PJSIP शक्तिशाली है लेकिन कॉन्फ़िगर करने में विस्तृत है: कई अलग‑अलग सेक्शन और टेम्प्लेट होते हैं जो शुरू में भ्रमित कर सकते हैं। अच्छी बात यह है कि PJSIP कॉन्फ़िगरेशन विज़ार्ड उपलब्ध है। कुछ लाइनों में प्रत्येक चैनल को परिभाषित करके, यह आपको टेम्प्लेट बनाने और नए डिवाइसों की कॉन्फ़िगरेशन को सरल बनाने की अनुमति देता है। फ़ाइल **pjsip_wizard.conf** का उपयोग करके कॉन्फ़िगर करें। आपको अभी भी फ़ाइल **pjsip.conf** में ट्रांसपोर्ट और ग्लोबल सेक्शन को परिभाषित करना होगा। व्यक्तिगत रूप से, मैं विज़ार्ड को केवल फ़ोनों के लिए उपयोग करना पसंद करता हूँ; SIP ट्रंक के लिए आमतौर पर संख्या अधिक नहीं होती और आप सीधे pjsip में कॉन्फ़िगर कर सकते हैं। विज़ार्ड का सबसे बड़ा लाभ टेम्प्लेट का उपयोग करने और फ़ोनों को जल्दी बनाने की संभावना है।

```
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media=no
endpoint/force_rport=yes
endpoint/rtp_symmetric=yes
aor/qualify_frequency=15
[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
[bob](phone_default)
inbound_auth/username = bob
inbound_auth/password = supersecret
```

### Loading and unloading PJSIP

PJSIP Asterisk 22 में एकमात्र SIP चैनल है, और इसके मॉड्यूल डिफ़ॉल्ट रूप से लोड होते हैं। दुर्लभ मामलों में आप अभी भी modules.conf फ़ाइल से मॉड्यूल लोडिंग को नियंत्रित करना चाह सकते हैं — उदाहरण के लिए, ऐसे सर्वर पर PJSIP को निष्क्रिय करने के लिए जो केवल IAX2 या DAHDI का उपयोग करता है।

#### To disable PJSIP

Edit the file modules.conf and add the following lines.

```
noload => res_pjsip.so
noload => res_pjsip_pubsub.so
noload => res_pjsip_session.so
noload => chan_pjsip.so
noload => res_pjsip_exten_state.so
```

### कंसोल कमांड्स

अब जब आपने अपने PJSIP endpoints को कॉन्फ़िगर कर लिया है, तो यह देखना समय है कि अपनी कॉन्फ़िगरेशन की जाँच कैसे करें। इस कार्य में मदद के लिए कई कंसोल कमांड्स उपलब्ध हैं। pjsip.conf को संपादित करने के बाद, कॉन्फ़िगरेशन को रीलोड करें:

```
module reload res_pjsip.so
```

A plain `reload` (or `core reload`) reloads all modules including PJSIP. (Note there is no bare `pjsip reload` command — `pjsip reload` only exists in the form `pjsip reload qualify aor|endpoint`.) You can list all available PJSIP console commands with `help pjsip`.

#### pjsip show endpoints

This command shows the endpoints available. In the picture below, we have a screenshot. You can see the address of the softphone endpoint and see that is available.

![Output of `pjsip show endpoints` listing the blink, siptrunk, and softphone endpoints with their AOR, auth, transport, and availability — the softphone contact is registered (Avail)](../images/07-sip-and-pjsip-fig15.png)

#### pjsip show endpoint <endpoint>

With the command above, you can see each parameter of the endpoint. The list below was cut to less than half of the current parameters.

![Output of `pjsip show endpoint softphone` showing the full parameter list for a single endpoint, from 100rel and allow=(ulaw) down through callerid and connected_line_method](../images/07-sip-and-pjsip-fig16.png)

#### pjsip show aors

यह कमांड कॉन्फ़िगर किए गए Address of Record ऑब्जेक्ट्स और उनके कॉन्टैक्ट्स को सूचीबद्ध करता है, जिससे आप पुष्टि कर सकते हैं कि प्रत्येक endpoint के लिए Asterisk कॉल्स कहाँ भेजेगा।

#### pjsip show registrations

नीचे दिया गया कमांड हमारे स्वयं के सर्वर द्वारा किए गए रजिस्ट्रेशन को दिखाता है।

![Output of `pjsip show registrations`: the outbound registration siptrunk/sip:1020@sip.flagonc.com:5600 is shown with status Registered](../images/07-sip-and-pjsip-fig17.png)

#### pjsip list

कमांड सूची थोड़ा अधिक उपयोगकर्ता‑मित्र है और कम डेटा दिखाती है, लेकिन बेहतर संरचित है। एंडपॉइंट्स की सूची:

![Output of `pjsip list endpoints`: a compact one-line-per-endpoint listing (blink, siptrunk, softphone) with their state and channel count](../images/07-sip-and-pjsip-fig18.png)

कॉन्टैक्ट्स की सूची:

![Output of `pjsip list contacts` showing the siptrunk and softphone contact URIs with their hash and qualify status](../images/07-sip-and-pjsip-fig19.png)

#### pjsip set logger on

सबसे उपयोगी ट्रबलशूटिंग कमांड SIP पैकेट लॉगर है। यह प्रत्येक SIP अनुरोध और उत्तर को कंसोल पर प्रिंट करता है जब वह भेजा या प्राप्त होता है, जो रजिस्ट्रेशन और कॉल सेटअप समस्याओं का निदान करने में अत्यंत मूल्यवान है।

```
pjsip set logger on
pjsip set logger off
```

आप एकल होस्ट तक लॉगिंग को सीमित भी कर सकते हैं `pjsip set logger host <ip>`.

#### pjsip set history on

PJSIP में एक शानदार जोड़ है इतिहास (history) की अवधारणा। आप वास्तविक समय में SIP अनुरोध और प्रतिक्रियाओं को आसानी से कैप्चर और विश्लेषण कर सकते हैं। इतिहास शुरू करने के लिए नीचे दिया गया कमांड उपयोग करें।

![Running `pjsip set history on` returns "PJSIP History enabled"](../images/07-sip-and-pjsip-fig20.png)

अब आप इतिहास दिखा सकते हैं:

![Output of `pjsip show history`: a numbered table of captured SIP messages — REGISTER, 401 Unauthorized, REGISTER, 200 OK — with timestamps, direction, and address](../images/07-sip-and-pjsip-fig21.png)

फिर किसी विशिष्ट अनुरोध या प्रतिक्रिया को देखने के लिए, इतिहास आइटम दिखाएँ:

![Output of `pjsip show history entry`: the full text of a single captured SIP message — here Asterisk 22's `404 Not Found` reply to an OPTIONS probe — showing the Via (with `rport`/`received`), Call-ID, From, To and CSeq headers, the `Allow`/`Supported` capabilities, and the `Server: Asterisk PBX 22.10.0` header](../images/07-sip-and-pjsip-fig22.png)

बहुत आसान, है ना? आप चाहें तो कभी भी `pjsip set history clear` का उपयोग करके इतिहास साफ़ कर सकते हैं।

> **Migrating an existing chan_sip/sip.conf system?** The legacy `chan_sip`
> driver and a complete **sip.conf → pjsip.conf migration guide** (including the
> concept-mapping table and the `sip_to_pjsip.py` conversion script) are covered
> in the *Legacy channels* chapter.

## Summary

SIP वह IETF सिग्नलिंग प्रोटोकॉल है जो मीडिया सत्रों को स्थापित, संशोधित और समाप्त करता है। इसके यूज़र एजेंट, प्रॉक्सी, रजिस्ट्रार, और गेटवे टेक्स्ट‑आधारित संदेशों का आदान‑प्रदान करते हैं — REGISTER, INVITE, प्रावvisional और अंतिम प्रतिक्रियाएँ, ACK, और BYE — जबकि SDP कोडेक्स पर बातचीत करता है और RTP मीडिया को ले जाता है। यह प्रोटोकॉल सिद्धांत कालातीत है और किसी भी SIP कार्यान्वयन पर लागू होता है।

Asterisk 22 में आप **PJSIP** (`chan_pjsip`) के माध्यम से SIP का उपयोग करते हैं, जिसे `pjsip.conf` में कॉन्फ़िगर किया जाता है। एक एकल मोनोलिथिक पीयर के बजाय, एक डिवाइस को छोटे, आपस में जुड़े ऑब्जेक्ट्स के सेट के रूप में मॉडल किया जाता है: `endpoint` (कॉल व्यवहार और कोडेक्स), `auth` (क्रेडेंशियल्स), `aor` (जहाँ यह पहुँचा जा सकता है), और `transport` (लिस्नर), साथ ही `identify` (IP द्वारा ट्रंक मिलाना) और `registration` (आउटबाउंड रजिस्टर) सेवा प्रदाताओं के लिए। आपने देखा कि ये ऑब्जेक्ट्स कैसे एक साथ फिट होते हैं, दोनों फ़ोन और ट्रंक को कैसे कॉन्फ़िगर किया जाता है, NAT‑ट्रैवर्सल विकल्प (`force_rport`, `rewrite_contact`, `rtp_symmetric`, `direct_media`, और ट्रांसपोर्ट के `external_*`/`local_net`) वास्तविक‑विश्व डिप्लॉयमेंट को कैसे हल करते हैं, और सभी को कैसे निरीक्षण किया जाता है `pjsip show endpoints`, `aors`, `contacts`, और `registrations` के साथ।

## Quiz

1. SIP आर्किटेक्चर में, कौन सा घटक अनुरोध प्राप्त करता है और उसे एक रीडायरेक्ट प्रतिक्रिया (जैसे `302 Moved Temporarily`) के साथ नया स्थान प्रदान करता है, फिर फॉलो‑अप संदेशों के मार्ग से बाहर रहता है?
   - A. Proxy server
   - B. Redirect server
   - C. Location server
   - D. Registrar

2. जब Asterisk दो फ़ोनों के बीच SIP कॉल को संभालता है, तो वह कौन सी भूमिका निभाता है?
   - A. एक SIP प्रॉक्सी जो केवल सिग्नलिंग पाथ में रहता है
   - B. एक SIP रीडायरेक्ट सर्वर
   - C. एक back-to-back user agent (B2BUA) जो दो SIP चैनलों को जोड़ता है
   - D. एक stateless SIP लोड बैलेंसर

3. कौन सी SIP मेथड फ़ोन द्वारा रजिस्ट्रार को उसका वर्तमान IP पता बताने के लिए उपयोग की जाती है ताकि बाद में कॉल प्राप्त की जा सके?
   - A. INVITE
   - B. OPTIONS
   - C. SUBSCRIBE
   - D. REGISTER

4. सत्य या असत्य: Asterisk 22 में, `chan_sip` और `sip.conf` अभी भी PJSIP के साथ एक लेगेसी फॉलबैक के रूप में उपलब्ध हैं।

5. कौन से कॉन्फ़िगरेशन ऑब्जेक्ट्स के साथ एक endpoint को संबद्ध होना चाहिए ताकि Asterisk को पता चल सके कि कौन सा लिसनिंग सॉकेट उपयोग करना है और उस डिवाइस के लिए कॉल कहाँ भेजनी है? (सभी लागू विकल्प चुनें।)
   - A. `type=transport`
   - B. `type=aor`
   - C. `type=identify`
   - D. `type=registration`

6. एक PJSIP `aor` ऑब्जेक्ट में, कौन सी सेटिंग NAT मैपिंग को खुला रखती है द्वारा समय‑समय पर कॉन्टैक्ट को क्वालिफ़ाई करना, और उसकी इकाई क्या है?
   - A. `qualify=yes` (boolean)
   - B. `qualify_frequency` (seconds)
   - C. `rtp_timeout` (milliseconds)
   - D. `nat=force_rport`

7. खाली स्थान भरें: इनबाउंड SIP अनुरोध को स्रोत IP पते (`From` हेडर के बजाय) के आधार पर किसी विशिष्ट endpoint से मिलाने के लिए, आप `type=________` के साथ एक सेक्शन बनाते हैं।

8. कौन सा PJSIP ऑब्जेक्ट Asterisk से SIP ट्रंक प्रोवाइडर तक **आउटबाउंड** रजिस्ट्रेशन को कॉन्फ़िगर करने के लिए उपयोग किया जाता है?
   - A. `type=aor`
   - B. `type=identify`
   - C. `type=registration`
   - D. `type=auth`

9. Asterisk 22 CLI पर, कौन सा कमांड SIP पैकेट लॉगर को सक्षम करता है जो हर SIP अनुरोध और उत्तर को कंसोल पर प्रिंट करता है?
   - A. `sip set debug on`
   - B. `pjsip set logger on`
   - C. `pjsip debug on`
   - D. `sip show registry`

10. एक PJSIP endpoint पर जो एक सिमेट्रिक NAT के पीछे फ़ोन को सर्व करता है, कौन सा सेटिंग‑जोड़ Asterisk को अनुरोध के स्रोत पते (RFC 3581) पर उत्तर देने और RTP को उसी स्थान पर भेजने को सक्षम करता है जहाँ वह वास्तव में आता है?
    - A. `direct_media=yes` and `srvlookup=yes`
    - B. `force_rport=yes` and `rtp_symmetric=yes`
    - C. `allowguest=yes` and `insecure=invite`
    - D. `qualify=yes` and `nat=no`

**Answers:** 1 — B · 2 — C · 3 — D · 4 — False · 5 — A, B · 6 — B · 7 — identify · 8 — C · 9 — B · 10 — B
