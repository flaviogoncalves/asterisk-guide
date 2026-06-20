# VoIP नेटवर्क का डिजाइन

Voice over IP तेज़ी से टेलीफ़ोनी बाजार में बढ़ रहा है। कन्फ़र्ज़ेंस पैरेडाइम हमारे संवाद करने के तरीके को बदल रहा है, लागत को कम कर रहा है और जानकारी के आदान‑प्रदान के तरीके को बेहतर बना रहा है। आवाज़ केवल एक पूर्ण मल्टीमीडिया संचार युग की शुरुआत है, जिसमें आवाज़, वीडियो और प्रेज़ेंस शामिल हैं। भविष्य में हम लोगों को काम पर नहीं ले जाएंगे, बल्कि काम को लोगों तक पहुँचाएंगे क्योंकि यह साफ़, तेज़ और सस्ता है। VoIP इस क्रांति का केवल एक हिस्सा है। इस अध्याय में हमारी चुनौती एक VoIP नेटवर्क का डिजाइन करना है। ऐसा करने के लिए हमें सत्र प्रोटोकॉल और कोडेक जैसे अवधारणाओं को समझना होगा तथा सर्किटों और बैंडविड्थ की संख्या को कैसे निर्धारित किया जाए, यह जानना होगा।

## Objectives

By the end of this chapter, you should be able to:

- Understand the benefits of VoIP
- Describe how Asterisk handles VoIP
- Describe the concepts of the SIP and IAX channels
- Choose the most adequate protocol for a specific data channel
- Choose the most adequate codec for a specific data channel
- Dimension the required number of channels
- Calculate the required bandwidth

## VoIP benefits

Why would you care about VoIP? VoIP provides benefits to both companies and individuals. Cost reduction is certainly one of them, but in some environments VoIP simplifies the integration of computer systems. Several of the benefits are detailed here:

### Convergence

The primary benefit of VoIP is the combination of data and voice networks to reduce costs (convergence). However, analyzing just voice minute costs may not be enough to justify the adoption of VoIP. The price of the minutes sold by phone companies is quickly becoming cheaper and is something to be considered before adopting VoIP.

### Infrastructure costs

The use of a single network infrastructure reduces the costs associated with additions, removals, and changes. As IP has become pervasive, it has brought VoIP-related technology to several new devices, such as cell phones, PDAs, embedded systems, and laptops.

### Open Standards

Finally, the open standards upon which VoIP is built provide the freedom to choose from different vendors. This single benefit makes the customer king instead of a subordinate to TELCOS and PBX manufacturers.

### Computer Telephony Integration

Telephony is far older than computing. Telephony PBXs are circuit-switch based, and you usually do not have more than a computer for supervision. With VoIP, telephony is from the ground up created based in computer standards. This makes the use of Computer Telephony applications cheaper and easier than in the old model. You can quickly create a long list of telephony applications based on Asterisk. You can develop IVRs, ACDs, CTI, dialers, screen popups, and other applications in a fraction of the time required for traditional PBXs.

## Asterisk VoIP architecture

Asterisk की आर्किटेक्चर नीचे दिखायी गई है। Asterisk सभी VoIP प्रोटोकॉल को चैनल के रूप में मानता है। आप कोई भी कोडेक या कोई भी प्रोटोकॉल उपयोग कर सकते हैं। यहाँ सीखने वाला मुख्य विचार यह है कि Asterisk किसी भी प्रकार के चैनल को किसी अन्य चैनल से जोड़ता है। इस प्रकार, आप SIP और IAX जैसे सिग्नलिंग प्रोटोकॉल को एक दूसरे में और विभिन्न कोडेक्स के साथ भी अनुवादित कर सकते हैं। उदाहरण के लिए, आप स्थानीय एरिया नेटवर्क में एक SIP फ़ोन से G.711 कोडेक का उपयोग करके कॉल को आपके VoIP प्रदाता के SIP ट्रंक पर G.729 कोडेक के साथ अनुवादित कर सकते हैं। अगले अध्यायों में, हम SIP और IAX आर्किटेक्चर के विवरण समझाएंगे। H.323 समर्थन (chan_ooh323 ऐड‑ऑन के माध्यम से) उपलब्ध है लेकिन धीरे‑धीरे दुर्लभ हो रहा है; आधुनिक डिप्लॉयमेंट के लिए SIP/PJSIP मानक है।

![Asterisk's modular architecture: applications and channels connect to the PBX switch core through APIs, with codec translation and file-format modules loaded dynamically.](../images/06-voip-network-fig01.png)

## VoIP protocols and the network stack

VoIP विभिन्न प्रोटोकॉल के सेट को एक साथ काम करता है। इसे सात-परत OSI रेफ़रेंस मॉडल के खिलाफ क्रमबद्ध करना आकर्षक लगता है, और कई पुराने आरेख बिल्कुल ऐसा ही करते हैं — SIP और H.323 को “session” परत पर और कोडेक्स को “presentation” परत पर रखते हैं। यह मैपिंग हमेशा विवादास्पद रही है। IETF, जो SIP को मानकीकृत करता है, OSI मॉडल का उपयोग नहीं करता; यह पुराने चार-परत TCP/IP (DoD) मॉडल का अनुसरण करता है, और RFC 3261 **SIP को एक application-layer प्रोटोकॉल** के रूप में परिभाषित करता है। मीडिया भी वही पैटर्न अपनाता है: RTP और कोडेक्स application payload में होते हैं, जो transport परत पर UDP के माध्यम से ले जाए जाते हैं। नीचे दिया गया तालिका मुख्य VoIP प्रोटोकॉल को TCP/IP मॉडल पर मैप करता है, जिसे IETF वास्तव में उपयोग करता है, और केवल संदर्भ के लिए मोटा OSI समकक्ष दिखाया गया है।

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| Application | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | Application / Presentation / Session |
| Transport | UDP, TCP | Transport |
| Internet | IP (with QoS such as DiffServ) | Network |
| Link | Ethernet, PPP, Frame Relay… | Data link / Physical |

QoS तंत्र जैसे DiffServ IP परत पर आवाज़ पैकेटों को प्राथमिकता देने और कॉल गुणवत्ता सुधारने के लिए काम करते हैं। कुछ प्रोटोकॉल विशिष्टताएँ:

- **SIP** UDP या TCP पर पोर्ट 5060 (TLS पर 5061) का उपयोग करके सिग्नलिंग ले जाता है। ऑडियो अलग से RTP द्वारा एक कॉन्फ़िगरेबल UDP पोर्ट रेंज (Asterisk के shipped `rtp.conf` sample में 10000 से 20000) पर ले जाया जाता है, जिसे G.711 जैसे कोडेक से एन्कोड किया जाता है।
- **H.323** कॉल सिग्नलिंग को TCP (पोर्ट 1720 पर H.225 कॉल सिग्नलिंग) के माध्यम से ले जाता है, जबकि H.225 RAS चैनल UDP पर पोर्ट 1719 का उपयोग करता है; RTP ऑडियो को ट्रांसपोर्ट करता है।
- **IAX2** असामान्य है: यह सिग्नलिंग और मीडिया दोनों को एक ही UDP पोर्ट (4569) पर मल्टीप्लेक्स करता है, जिससे NAT और फ़ायरवॉल ट्रैवर्सल सरल हो जाता है।


## How to choose a protocol

Given the many protocols, how can you choose the best one for your network? In this section, we will highlight the advantages and drawbacks of each protocol.

### SIP - Session Initiated Protocol

SIP is an Internet Engineering Task Force (IETF) open standard, largely defined in RFC 3261. Most modern VoIP providers use SIP; indeed, it is becoming the most popular VoIP standard. The strength of SIP is that it is an IETF-based standard. SIP is light when compared to the older H.323. SIP’s main weakness is the NAT traversal—a challenge to most SIP VoIP providers. IETF did not create SIP with billing in mind, but for open communications between peers. Billing is usually a concern for VoIP providers.

### IAX – Inter Asterisk eXchange

IAX is an open protocol originally developed by Digium (now Sangoma). IAX is an all-in-one protocol as it transports signaling and media through the same UDP port (4569). Mark Spencer developed IAX as a binary protocol for reduced bandwidth. The main strength of IAX is its reduced bandwidth usage (it does not use RTP); it is also very easy for NAT and firewall traversal since it uses only one UDP port (4569).

If a traditional PBX manufacturer were to have created IAX, it would probably have marketed the protocol as the "best thing since ice cream"; in some situations, IAX in trunk mode can reduce voice bandwidth use by one third. IAX2 (version 2) still ships in Asterisk 22 via the `chan_iax2` module and remains useful for Asterisk-to-Asterisk trunks, though it is considered legacy; SIP/PJSIP is preferred for new deployments. IAX2 is specified in [RFC 5456](https://www.rfc-editor.org/rfc/rfc5456) (Informational).

### MGCP – Media Gateway Control Protocol

MGCP is a protocol used in conjunction with H.323, SIP, and IAX. Its greatest advantage is scalability. It is configured in the call agent instead of the gateways. This simplifies the configuration process and permits centralized management. However, Asterisk implementation is not complete, and it seems that not many people use it.

### H.323

H.323 is largely being used in VoIP. It is one of the first VoIP protocols and is essential for connecting older VoIP infrastructures based in gateways. H.323 is still the standard in the gateway market, although the market is slowly migrating to SIP. H.323’s strengths include the large market adoption and maturity. H.323’s weaknesses are related to the complexity of implementation and standard bodies’ associated costs.

### Protocol comparison table

The following table summarizes the differences among the session protocols.

| Protocol | Standard body | Asterisk 22 module / status | Used for |
|----------|---------------|-----------------------------|----------|
| SIP | IETF standard | `chan_pjsip` (core; the only SIP driver — `chan_sip` was removed in Asterisk 21) | SIP phones; connecting to SIP service providers |
| IAX2 | RFC 5456 (Informational) | `chan_iax2` (core; still shipped, considered legacy) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX service providers |
| H.323 | ITU standard | `chan_ooh323` (external community add-on, not in the base build) | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| MGCP | IETF/ITU | `chan_mgcp` removed in Asterisk 21 — no longer available | (legacy MGCP phones) |
| SCCP (Skinny) | Cisco proprietary | `chan_skinny` removed in Asterisk 21 — no longer available | (legacy Cisco phones) |

## One endpoint per device

Asterisk 22 में PJSIP स्टैक हर फोन, ट्रंक, या गेटवे को `pjsip.conf` में एक एकल **endpoint** ऑब्जेक्ट के रूप में मॉडल करता है। एक endpoint कॉल को प्लेस और रिसीव दोनों करता है; इसकी क्रेडेंशियल्स `auth` ऑब्जेक्ट में रहती हैं, उसका रजिस्टर्ड एड्रेस `aor` में, और उसका नेटवर्क पाथ `transport` में। आप प्रत्येक डिवाइस के लिए एक endpoint कॉन्फ़िगर करते हैं और उसे आवश्यक भागों को अटैच करते हैं — यहाँ कोई अलग “user” बनाम “peer” भूमिका नहीं है जिसके बारे में सोचना पड़े। (पूरा ऑब्जेक्ट मॉडल *SIP & PJSIP in depth* में कवर किया गया है।)

## Codecs and codec translation

आप आवाज़ को एनालॉग वेव से डिजिटल सिग्नल में बदलने के लिए एक codec का उपयोग करेंगे। Codecs ध्वनि गुणवत्ता, संपीड़न दर, बैंडविड्थ, और कंप्यूटिंग आवश्यकताओं जैसे पहलुओं में एक‑दूसरे से अलग होते हैं। सेवाएँ, फ़ोन, और गेटवे आमतौर पर इन पहलुओं में से कई का समर्थन करते हैं। codec G.729 बहुत लोकप्रिय है। यह मानक Asterisk 22 बिल्ड का हिस्सा नहीं है; बल्कि यह एक बाहरी ऐड‑ऑन मॉड्यूल (`codec_g729`) के रूप में आता है जिसे आप Digium (अब Sangoma) से डाउनलोड करते हैं। Asterisk के `menuselect` स्रोत में इसे `support_level=external` के साथ सूचीबद्ध किया गया है और स्पष्ट रूप से लिखा है: "Digium से g729a codec डाउनलोड करें। इस codec के लिए एक लाइसेंस खरीदा जाना आवश्यक है।" दूसरे शब्दों में, वैध G.729 उपयोग के लिए प्रति‑चैनल लाइसेंस खरीदना आवश्यक है। (एक ओपन‑सोर्स विकल्प, `bcg729`, भी उपलब्ध है।)

![Pulse Code Modulation (PCM): a 4000 Hz analog signal is sampled 8000 times per second (Nyquist theorem) and coded into a 64 Kbps digital bitstream.](../images/06-voip-network-fig04.png)

Asterisk 22 निम्नलिखित codecs (और भी कई) का समर्थन करता है:

- GSM: 13 Kbps
- iLBC: 13.3 Kbps
- ITU G.711 (ulaw/alaw): 64 Kbps — मानक PSTN गुणवत्ता; ulaw उत्तर अमेरिका में सामान्य, alaw यूरोप और लैटिन अमेरिका में सामान्य
- ITU G.722: 64 Kbps — वाइडबैंड (HD voice), G.711 के समान बैंडविड्थ पर अच्छी गुणवत्ता
- ITU G.723.1: 5.3/6.3 Kbps
- ITU G.726: 16/24/32/40 Kbps
- ITU G.729: 8 Kbps — Digium/Sangoma से डाउनलोड किया गया बाहरी `codec_g729` बाइनरी मॉड्यूल (`support_level=external`; उपयोग के लिए लाइसेंस खरीदना आवश्यक है)
- Speex: 2.15 से 44.2 Kbps
- LPC10: 2.4 Kbps
- **Opus**: 6–510 Kbps, वैरिएबल — आधुनिक वाइडबैंड/फुलबैंड codec; उत्कृष्ट गुणवत्ता और पैकेट‑लॉस प्रतिरोध; Digium/Sangoma से डाउनलोड किया गया बाहरी `codec_opus` बाइनरी मॉड्यूल (`support_level=external`; G.729 के विपरीत कोई लाइसेंस खरीदने की आवश्यकता नहीं बताई गई); WebRTC और आधुनिक SIP endpoints के लिए अनुशंसित। (GitHub पर ओपन‑सोर्स बिल्ड विकल्प उपलब्ध हैं।)

इसके अतिरिक्त, Asterisk codecs के बीच अनुवाद की अनुमति देता है। कुछ मामलों में यह संभव नहीं होता, जैसे g723, जो केवल पास‑थ्रू मोड में समर्थित है। एक codec से दूसरे में अनुवाद करने में CPU से कई संसाधन खर्च होते हैं। इसलिए, जब भी संभव हो, इसे पूरी तरह से टालें।

## How to choose a Codec

Codec selection depends on several options, such as:

- Sound quality
- Licensing costs
- CPU-processing consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability for Asterisk and phone devices

The following table compares the most popular codecs. The quality of these codecs is considered “toll”—in other words, similar to PSTN.

| Codec | G.711 | G.722 | Opus | G.729A | iLBC | GSM |
|---|---|---|---|---|---|---|
| Audio band | Narrow | Wide (HD) | Narrow–full | Narrow | Narrow | Narrow |
| Bandwidth (Kbps) | 64 | 64 | 6–510 | 8 | 13.33 | 13 |
| Cost/channel | Free | Free | Free | License¹ | Free | Free |
| Frame-erasure² | None | Low | Excellent | ~3% | ~5% | ~3% |
| CPU cost | Very low | Low | Mod.–high | High | High | Low |

The Asterisk 22 modules are: G.711 `codec_ulaw` / `codec_alaw` (core), G.722 `codec_g722` (core), Opus `codec_opus` (external), G.729 `codec_g729` (external), iLBC `codec_ilbc` (core), and GSM `codec_gsm` (core). Opus is "Narrow–full" because it scales from narrowband up to fullband; its bandwidth (6–510 Kbps) is variable, and its frame-erasure resistance comes from built-in FEC/PLC.

The PSTN baseline is **G.711** — it is the reference for "toll" quality and transcodes for free inside Asterisk. **G.722** delivers wideband (HD) voice at the same 64 Kbps and is a good LAN/internal choice. **Opus** is the modern default for WebRTC and capable SIP endpoints: it adapts its bitrate, has built-in forward error correction, and resists packet loss well; it ships as the external `codec_opus` binary (free to download). **G.729** stays useful on low-bandwidth WAN trunks, but lawful use requires either Sangoma's licensed `codec_g729` (free to download, per-channel license to use) or the open-source **bcg729** implementation as an alternative.

¹ Sangoma's `codec_g729` binary is free to download but requires a purchased per-channel license to use lawfully. The open-source `bcg729` is a license-free alternative.

² Resistance to frame erasure refers to how well perceived quality (MOS) holds up under packet loss. The exact crossover point varies with packetization and network conditions; use this column for relative comparison, not as a precise figure.

**Codec recommendations for Asterisk 22:**

- **G.711 (ulaw/alaw):** Use for PSTN trunks and maximum interoperability; zero transcoding cost within Asterisk.
- **G.729:** Useful for low-bandwidth WAN trunks; Sangoma's `codec_g729` module is free to download but requires a purchased per-channel license to use.
- **G.722:** Good choice for wideband (HD voice) on LAN/internal extensions; same bandwidth as G.711 with better quality.
- **Opus:** Recommended for modern endpoints, WebRTC clients, and any deployment where the endpoint supports it. Adaptive bitrate, excellent packet-loss resilience, freely available via Sangoma's `codec_opus` binary module.

## प्रोटोकॉल हेडर द्वारा उत्पन्न ओवरहेड

हालांकि कोडेक्स बैंडविड्थ का बहुत कम उपयोग करते हैं, हमें Ethernet, IP, UDP, और RTP जैसे प्रोटोकॉल हेडर द्वारा उत्पन्न ओवरहेड पर विचार करना पड़ता है। इस प्रकार, वास्तविक रूप से उपयोग की गई बैंडविड्थ हेडर पर निर्भर करती है। Ethernet नेटवर्क पर आवश्यकता PPP नेटवर्क की तुलना में अधिक होती है, क्योंकि PPP हेडर Ethernet हेडर से छोटा होता है। उदाहरण के लिए, एकल G.729 आवाज़ पैकेट केवल 20 बाइट्स का पेलोड ले जाता है लेकिन लगभग 58 बाइट्स के Ethernet, IP, UDP, और RTP हेडर में लिपटा होता है — इसलिए हेडर, कोडेक नहीं, बैंडविड्थ को नियंत्रित करते हैं (नीचे चित्र देखें)।

![Ethernet पर एकल g.729 आवाज़ पैकेट: 20 बाइट्स पेलोड को 58 बाइट्स Ethernet, IP, UDP, और RTP हेडर में लपेटा गया — एक g.729 वार्तालाप 31.2 Kbps उपभोग करता है.](../images/06-voip-network-fig05.png)

- Ethernet (Ethernet+IP+UDP+RTP+G.711) = 95.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.711) = 82.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.711) = 82.8 Kbps

Codec G.729 (8 Kbps)

- Ethernet (Ethernet+IP+UDP+RTP+G.729) = 31.2 Kbps
- PPP (PPP+IP+UDP+RTP+G.729) = 26.4 Kbps
- Frame-Relay (FR+IP+UDP+RTP+G.729) = 26.8 Kbps

आप ऑनलाइन VoIP बैंडविड्थ कैलकुलेटर जैसे <https://www.voip.school/bandcalc/bandcalc.php> का उपयोग करके अन्य बैंडविड्थ आवश्यकताओं की आसानी से गणना कर सकते हैं।


## Traffic Engineering

VoIP नेटवर्कों के डिज़ाइन में मुख्य समस्या यह है कि किसी विशिष्ट गंतव्य, जैसे कि रिमोट ऑफिस या सर्विस प्रोवाइडर, के लिए लाइनों की संख्या और आवश्यक बैंडविड्थ को कैसे निर्धारित किया जाए। यह भी महत्वपूर्ण है कि Asterisk की समकालिक कॉलों की संख्या (Asterisk के डाइमेंशनिंग का मुख्य पैरामीटर) को निर्धारित किया जाए।

### Simplifications

मुख्य और सबसे अधिक उपयोग की जाने वाली सरलीकरण यह है कि उपयोगकर्ता प्रकार के आधार पर कॉलों की संख्या का अनुमान लगाया जाए। उदाहरण के लिए:

- Business PBXs (हर पाँच एक्सटेंशन के लिए एक समकालिक कॉल)
- Residential users (हर सोलह उपयोगकर्ताओं के लिए एक समकालिक कॉल)

Example #1 कंपनी के मुख्यालय में 120 एक्सटेंशन और दो शाखाएँ हैं—पहली में 30 एक्सटेंशन और दूसरी में 15 एक्सटेंशन। हमारा उद्देश्य मुख्यालय में E1 ट्रंक्स की संख्या और Frame-Relay नेटवर्क के लिए आवश्यक बैंडविड्थ को निर्धारित करना है।

![Example network topology (same city): headquarters with 120 extensions connects to the PSTN over T1 lines, and to branch #1 (30 extensions) and branch #2 (15 extensions) over a Frame-Relay cloud.](../images/06-voip-network-fig06.png)

1a Number of T1 lines

- Total number of extensions using T1 lines: 120+30+15=165 lines
- Using one trunk for each five extensions for business use
- Total number of lines = 33 or approximately 2xT1 lines

1b Bandwidth requirements We choose the g.729 codec because of bandwidth requirements, sound quality, and medium CPU consumption.

With one trunk for every five extensions:

- Required bandwidth for branch #1 (Frame-relay): 26.8*6=160.8 Kbps
- Required bandwidth for branch #2 (Frame-relay): 26.8*3= 80.4 Kbps

### Erlang B method

जब आपके पास ऐतिहासिक डेटा हो, तो आप ट्रंक को अधिक वैज्ञानिक तरीके से आकार दे सकते हैं बजाय सरलीकरण के। हम Agner Karup Erlang (Copenhagen Telephone Company, 1909) के कार्य का उपयोग करेंगे, जिन्होंने दो शहरों के बीच ट्रंक समूह में लाइनों की संख्या की गणना के लिए एक सूत्र विकसित किया।

एक **Erlang** टेलीकॉम में सामान्य ट्रैफ़िक-माप इकाई है; यह एक घंटे के दौरान ट्रैफ़िक की मात्रा को दर्शाती है। उदाहरण के लिए, मान लीजिए एक घंटे में 20 कॉल होते हैं, प्रत्येक का औसत वार्तालाप समय 5 मिनट है:

- Traffic minutes in the hour: 20 × 5 = 100 minutes
- Hours of traffic within one hour: 100 / 60 = **1.66 Erlangs**

आप इन मापों को कॉल लॉगर से पढ़ सकते हैं और अपने नेटवर्क को डिजाइन करने तथा आवश्यक लाइनों की संख्या की गणना करने के लिए उपयोग कर सकते हैं। एक बार लाइनों की संख्या ज्ञात हो जाने पर, आप बैंडविड्थ आवश्यकताओं की गणना कर सकते हैं।

**Erlang B** ट्रंक समूह में लाइनों की संख्या की गणना के लिए सबसे अधिक उपयोग की जाने वाली विधि है। यह मानता है कि कॉलें यादृच्छिक रूप से आती हैं (Poisson वितरण) और ब्लॉक्ड कॉलें तुरंत क्लियर हो जाती हैं। यह आवश्यक है कि आप **Busy Hour Traffic (BHT)** को जानें, जिसे आप कॉल लॉगर से प्राप्त कर सकते हैं या सरलीकरण के रूप में अनुमानित कर सकते हैं: BHT = एक दिन के कॉल मिनटों का 17%।

![Erlang B calculator results: 5 Erlangs at 1% blocking requires 11 lines (headquarters to branch #1), and 2.83 Erlangs at 1% blocking requires 8 lines (headquarters to branch #2).](../images/06-voip-network-fig07.png)

एक अन्य महत्वपूर्ण चर Grade of Service (GoS) है, जो लाइन की कमी के कारण ब्लॉक्ड कॉलों की संभावना को परिभाषित करता है। आप इस पैरामीटर को तय कर सकते हैं, जो आमतौर पर 0.05 (5% कॉल खोए) या 0.01 (1% कॉल खोए) होता है। Example #1: इस अनुभाग में पहले प्रस्तुत किए गए मुख्यालय‑और‑दो‑शाखाओं के उदाहरण का उपयोग करते हुए, हम आपको ट्रैफ़िक पैट

## VoIP के लिए आवश्यक बैंडविड्थ को कम करना

VoIP कॉल्स के लिए आवश्यक बैंडविड्थ को कम करने के तीन तरीके हैं:

- RTP हेडर संपीड़न
- IAX ट्रंकीड
- VoIP पेलोड

### RTP हेडर संपीड़न

Frame-Relay और PPP नेटवर्क्स में आप RTP हेडर संपीड़न का उपयोग कर सकते हैं। RTP हेडर संपीड़न RFC 2508 में परिभाषित है। यह कई राउटरों में उपलब्ध एक IETF मानक है। हालांकि, सावधान रहें, क्योंकि कुछ राउटरों को इस सुविधा को उपलब्ध कराने के लिए अलग फीचर सेट की आवश्यकता होती है। RTP हेडर संपीड़न के उपयोग का प्रभाव शानदार है क्योंकि यह हमारे उदाहरण में आवाज़ वार्तालाप के लिए आवश्यक बैंडविड्थ को 26.8 Kbps से घटाकर 11.2 Kbps कर देता है—58.2% की कमी!

### IAX2 ट्रंक मोड

यदि आप दो Asterisk सर्वरों को जोड़ रहे हैं, तो आप IAX2 प्रोटोकॉल को ट्रंक मोड में उपयोग कर सकते हैं। यह क्रांतिकारी तकनीक किसी विशेष राउटर की आवश्यकता नहीं रखती और किसी भी प्रकार के डेटा लिंक पर लागू की जा सकती है।

![IAX2 ट्रंक मोड Ethernet पर: एकल g.729 कॉल को उसके पूर्ण हेडर स्टैक (31.2 Kbps) की आवश्यकता होती है, लेकिन दूसरी कॉल उन हेडरों को साझा करती है और केवल एक छोटा IAX2 मिनीफ़्रेम जोड़ती है, अतिरिक्त कॉल प्रति औसतन लगभग 9.6 Kbps अतिरिक्त बैंडविड्थ जोड़ती है.](../images/06-voip-network-fig08.png)

IAX2 ट्रंक मोड दूसरे कॉल और उसके बाद के कॉलों से वही हेडर पुन: उपयोग करता है। PPP लिंक में g729 का उपयोग करते हुए, पहली कॉल 30 Kbps बैंडविड्थ खपत करेगी, जबकि दूसरी कॉल पहली के समान हेडर का उपयोग करेगी और अतिरिक्त कॉल के लिए आवश्यक बैंडविड्थ को 9.6 Kbps तक घटा देगी। हम ट्रंक मोड में आवश्यक बैंडविड्थ को इस प्रकार गणना कर सकते हैं:  
Branch #1 (11 कॉल) बैंडविड्थ = 31.2 + (11-1)* 9.6 Kbps = 127.2 Kbps  
Branch #2 (8 कॉल) बैंडविड्थ = 31.2 + (8-1)* 9.6 Kbps = 98.4 Kbps  
पहली कॉल 31.2 Kbps उपयोग करती है, अगली 9.6 Kbps, और इसी प्रकार आगे।

### आवाज़ पेलोड बढ़ाना

यह विधि इंटरनेट पर VoIP गेटवे का उपयोग करते समय बहुत सामान्य है। बड़े पेलोड का उपयोग करने पर आप बैंडविड्थ को कम करने के बदले लेटेंसी का बलिदान करेंगे। आप `allow` निर्देश में कोडेक के साथ फ्रेम आकार जोड़कर RTP पैकेटाइज़ेशन बदल सकते हैं।

![आवाज़ पेलोड बढ़ाना: 60 बाइट्स के g.729 पेलोड को एक पैकेट में पैक करना (20 के बजाय) 58 बाइट्स के हेडर को अधिक आवाज़ में वितरित करता है, जिससे बैंडविड्थ लगभग 16.05 Kbps प्रति कॉल तक गिर जाती है, लेकिन लेटेंसी बढ़ जाती है.](../images/06-voip-network-fig09.png)

उदाहरण:

```
allow=ulaw:30
```

कोलन के बाद का नंबर मिलिसेकंड में पैकेटाइज़ेशन अंतराल है — प्रत्येक RTP पैकेट में कितना आवाज़ ले जाया जाता है। बड़ा मान स्थिर हेडर ओवरहेड को अधिक ऑडियो में वितरित करता है (कम बैंडविड्थ) लेकिन लेटेंसी बढ़ाता है। प्रत्येक कोडेक का अपना न्यूनतम, अधिकतम, और डिफ़ॉल्ट फ्रेम आकार होता है; G.711 (`ulaw`/`alaw`) के लिए, उदाहरण के तौर पर, डिफ़ॉल्ट 20 ms है।

## Summary

इस अध्याय में, आपने सीखा कि Asterisk चैनलों का उपयोग करके VoIP को संभालता है। यह SIP (via `chan_pjsip` in Asterisk 22) और IAX2 को सपोर्ट करता है; H.323 केवल community `ooh323` add‑on के माध्यम से उपलब्ध है, और पुराने MGCP और SCCP (Skinny) चैनल अब मानक Asterisk 22 बिल्ड का हिस्सा नहीं हैं। आपने तुलना की और सीखा कि VoIP चैनलों के लिए सिग्नलिंग प्रोटोकॉल और codec कैसे चुनें। IAX2 अधिक बैंडविड्थ‑कुशल है और NAT को आसानी से पार कर सकता है। SIP/PJSIP तीसरे‑पक्ष फ़ोन और गेटवे विक्रेताओं द्वारा सबसे अधिक समर्थित प्रोटोकॉल है और Asterisk 22 में एकमात्र SIP चैनल ड्राइवर है। H.323 प्रोटोकॉल सबसे पुराना है और इसे लेगेसी VoIP इन्फ्रास्ट्रक्चर से कनेक्ट करने के लिए उपयोग किया जाना चाहिए। Traffic Engineering अनुभाग में, हमने सीखा कि VoIP नेटवर्क को कैसे डिजाइन और आकार दिया जाए।

## Quiz

1. Which of the following are benefits of VoIP described in this chapter (check all that apply)?
   - A. Convergence of data and voice networks to reduce cost
   - B. Lower infrastructure cost for additions, removals, and changes
   - C. Open standards that free you from a single vendor
   - D. Easier and cheaper Computer Telephony Integration
   - E. Guaranteed lower per-minute calling rates than any phone company
2. Convergence is the integration of voice, data, and video in a single network; its primary benefit is cost reduction in the implementation and maintenance of separate networks.
   - A. False
   - B. True
3. Asterisk treats every VoIP protocol as a channel and can bridge any channel type to any other, transcoding between codecs when needed.
   - A. False
   - B. True
4. In Asterisk 22, SIP is handled by which channel driver?
   - A. chan_sip
   - B. chan_pjsip
   - C. chan_skinny
   - D. chan_mgcp
5. In the TCP/IP (IETF) model that SIP is actually defined against in RFC 3261, the signaling protocols SIP, H.323, and IAX2 operate at the ___ layer.
   - A. Presentation
   - B. Application
   - C. Physical
   - D. Session
   - E. Data link
6. SIP is the most adopted protocol for IP phones and is an open standard largely defined by the IETF in RFC 3261.
   - A. False
   - B. True
7. IAX2 transports both signaling and media over a single UDP port, which makes it efficient and easy to traverse NAT. Which UDP port does IAX2 use?
   - A. 5060
   - B. 1720
   - C. 4569
   - D. 5061
8. IAX was originally developed by Digium (now Sangoma). Despite limited adoption by phone vendors, IAX is excellent when you need (check all that apply):
   - A. To reduce bandwidth usage (it does not use RTP)
   - B. A video media format
   - C. Easy NAT and firewall traversal
   - D. Trunk mode to combine many Asterisk-to-Asterisk calls and amortize header overhead
9. In Asterisk 22, a device is configured as a single PJSIP `endpoint` object that both places and receives calls — there is no separate "user" or "peer" role.
   - A. False
   - B. True
10. Regarding codecs in Asterisk 22, check all the true statements:
    - A. G.711 is equivalent to PCM and uses 64 Kbps of bandwidth.
    - B. Sangoma's codec_g729 module is free to download, but lawful use requires a purchased per-channel license.
    - C. GSM is popular because it uses about 13 Kbps and needs no license.
    - D. G.711 u-law is common in North America, while a-law is common in Europe and Latin America.
    - E. G.729 is light and uses very few CPU resources to encode and decode compared with G.711.

**Answers:** 1 — A, B, C, D · 2 — B · 3 — B · 4 — B · 5 — B (Application — SIP is an application-layer protocol in the TCP/IP model the IETF uses) · 6 — B · 7 — C · 8 — A, C, D · 9 — B · 10 — A, B, C, D
