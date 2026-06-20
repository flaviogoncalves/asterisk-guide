# Asterisk PBX का परिचय

FreePBX और Issabel जैसी तैयार-चलाने‑योग्य वितरणों की लोकप्रियता हाल ही में बढ़ी है। इस पुस्तक में, हम क्लासिक Asterisk को कवर करेंगे, जो इन वितरणों को समझने की नींव है। Asterisk PBX एक ओपन‑सोर्स सॉफ़्टवेयर है जो एक सामान्य PC को एक शक्तिशाली मल्टी‑प्रोटोकॉल PBX में बदल सकता है। इस अध्याय में, हम इस नई तकनीक की संभावनाओं और इसकी बुनियादी आर्किटेक्चर के बारे में सीखेंगे।

## उद्देश्य

इस अध्याय के अंत तक आपको सक्षम होना चाहिए:

- यह समझाएँ कि Asterisk क्या है और यह क्या करता है;
- Digium™ और उसके उत्तराधिकारी Sangoma की भूमिका का वर्णन करें;
- Asterisk की मूल संरचना और उसके घटकों को पहचानें;
- कई उपयोग परिदृश्यों की ओर इशारा करें; और
- जानकारी और सहायता के स्रोतों की पहचान करें।

## What is Asterisk

Asterisk एक ओपन-सोर्स PBX सॉफ़्टवेयर है जो एक सामान्य कंप्यूटर को घर उपयोगकर्ताओं, उद्यमों, VoIP सेवा प्रदाताओं और फोन कंपनियों के लिए पूर्ण‑विशेषताओं वाला PBX में बदल देता है। Asterisk एक ओपन‑सोर्स समुदाय भी है और एक प्रोजेक्ट है जिसे Sangoma Technologies (जिसने 2018 में Digium का अधिग्रहण किया) द्वारा प्रायोजित किया गया है। आप अपनी आवश्यकताओं के अनुसार Asterisk को उपयोग और संशोधित करने के लिए स्वतंत्र हैं। Asterisk PSTN और VoIP नेटवर्क के बीच रीयल‑टाइम कनेक्टिविटी की अनुमति देता है। चूँकि Asterisk केवल एक PBX से कहीं अधिक है, आपको न केवल अपने मौजूदा PBX का एक उत्कृष्ट अपग्रेड मिलता है, बल्कि आप टेलीफ़ोनी में नई चीज़ें भी कर सकते हैं, जैसे:

- घर से काम करने वाले कर्मचारियों को ब्रॉडबैंड इंटरनेट के माध्यम से ऑफिस PBX से जोड़ना;
- विभिन्न स्थानों पर स्थित कई कार्यालयों को IP नेटवर्क, प्राइवेट नेटवर्क, या यहाँ तक कि इंटरनेट के माध्यम से जोड़ना;
- अपने कर्मचारियों को वेब और ई‑मेल के साथ एकीकृत वॉइसमेल प्रदान करना;
- ऐसे एप्लिकेशन बनाना जैसे IVR जो आपके ऑर्डरिंग सिस्टम या अन्य एप्लिकेशन से कनेक्शन की अनुमति देते हैं;
- यात्रा कर रहे उपयोगकर्ताओं को कंपनी PBX तक कहीं से भी सरल ब्रॉडबैंड या VPN कनेक्शन के साथ पहुँच देना; और
- बहुत कुछ....

Asterisk कई उन्नत सुविधाएँ शामिल करता है जो पहले केवल हाई‑एंड सिस्टम में पाई जाती थीं, जैसे:

- कॉल क्यू में प्रतीक्षा कर रहे ग्राहकों के लिए संगीत, मीडिया स्ट्रीमिंग और MP3 फ़ाइलों का समर्थन;
- कॉल क्यू, जहाँ एजेंटों की एक टीम कॉल का उत्तर दे सकती है और क्यू को मॉनिटर कर सकती है;
- टेक्स्ट‑टू‑स्पीच और वॉइस रिकग्निशन के साथ एकीकरण;
- विस्तृत रिकॉर्ड्स जो टेक्स्ट फ़ाइलों और SQL डेटाबेस दोनों में स्थानांतरित होते हैं; और
- डिजिटल और एनालॉग दोनों लाइनों के माध्यम से PSTN कनेक्टिविटी।

## AsteriskNOW (Historical) क्या है और FreePBX

Asterisk अपने शुद्ध रूप में, जिसे “classic asterisk” (Debian पैकेज नाम) भी कहा जाता है, स्वयं में एक पूर्ण उत्पाद की बजाय अधिकतर एक विकास उपकरण माना जाता है। AsteriskNOW एक पहल थी जिसका उद्देश्य Asterisk को एक सॉफ्ट‑एप्लायंस में बदलना था। इस वितरण में ऑपरेटिंग सिस्टम के रूप में CentOS और ग्राफिकल इंटरफ़ेस के रूप में FreePBX शामिल था। AsteriskNOW को तब से बंद कर दिया गया है।

आज, मानक टर्नकी Asterisk वितरण **FreePBX** (Sangoma द्वारा रखरखाव) है, जो Asterisk को वेब‑आधारित प्रशासन GUI और मॉड्यूल इकोसिस्टम के साथ बंडल करता है। FreePBX GPL के तहत लाइसेंस किया गया है और www.freepbx.org से स्वतंत्र रूप से डाउनलोड किया जा सकता है। व्यावसायिक तैनाती के लिए, Sangoma **FreePBX Distro** (एक पूर्ण Linux इमेज) और अपना व्यावसायिक उत्पाद **PBXact** भी प्रदान करता है।

## Role of Digium™ and Sangoma

Digium, एक कंपनी जो Huntsville, Alabama में स्थित है, 1999 में अपनी स्थापना के बाद से Asterisk का निर्माता और मुख्य डेवलपर रहा है। Asterisk विकास के मुख्य प्रायोजक होने के अलावा, Digium ने Asterisk PBX के लिए टेलीफ़ोनी इंटरफ़ेस कार्ड और अन्य हार्डवेयर बनाए, और Switchvox (SMB बाजार को लक्षित) जैसे व्यावसायिक उत्पाद बनाए। 2018 में, Digium को **Sangoma Technologies** द्वारा अधिग्रहित किया गया, जो एक कनाडाई यूनिफ़ाइड कम्युनिकेशन्स कंपनी है। अधिग्रहण के बाद से, Sangoma ने Asterisk विकास को प्रायोजित करना जारी रखा है और www.asterisk.org पर ओपन‑सोर्स प्रोजेक्ट का मुख्य संरक्षक के रूप में कार्य करता है।

इतिहास में, Digium ने Asterisk को तीन प्रकार के लाइसेंस समझौतों के तहत पेश किया:

- General Public License (GPL) Asterisk. यह सबसे अधिक उपयोग किया जाने वाला संस्करण है। इसमें सभी सुविधाएँ शामिल हैं और GPL लाइसेंस की शर्तों के अनुसार उपयोग और संशोधित किया जा सकता है।
- Asterisk Business Edition एक व्यावसायिक संस्करण था। कुछ कंपनियों ने बिज़नेस एडिशन का उपयोग किया क्योंकि वे GPL लाइसेंस का उपयोग नहीं करना चाहती थीं या नहीं कर सकती थीं—आमतौर पर इसलिए क्योंकि वे अपना स्रोत कोड Asterisk के साथ जारी नहीं करना चाहते थे। **Note:** Asterisk Business Edition को बंद कर दिया गया है; आज Asterisk केवल GPL के तहत वितरित किया जाता है।
- Asterisk OEM licensing. जब Digium ने रिटेल पर Asterisk Business Edition बेचना बंद किया, तो उसने उस व्यावसायिक संस्करण को OEM ग्राहकों को लाइसेंस करना जारी रखा — उपकरण विक्रेताओं को जो Asterisk के ऊपर स्वामित्व वाले उत्पाद बनाना चाहते थे बिना अपना स्रोत कोड GPL के तहत जारी किए।

### The Zapata project and its relationship with Asterisk

Zapata प्रोजेक्ट को Jim Dixon ने विकसित किया, जो Asterisk के साथ उपयोग किए जाने वाले क्रांतिकारी हार्डवेयर डिज़ाइन के लिए भी जिम्मेदार थे। यह हार्डवेयर भी ओपन‑सोर्स है; इसलिए इसे कोई भी कंपनी उपयोग कर सकती है, और आज कई निर्माता इस आर्किटेक्चर के अनुकूल कार्ड बनाते हैं।

Zapata प्रोजेक्ट ने Zaptel नामक एक आर्किटेक्चर तैयार किया, जिसे बाद में DAHDI (Digium/Asterisk Hardware Device Interface) कहा गया। इस आर्किटेक्चर का मुख्य लाभ यह है कि यह PC CPU का उपयोग करके मीडिया स्ट्रीमिंग, इको कैंसलेशन, और ट्रांसकोडिंग को प्रोसेस कर सकता है। इसके विपरीत, अधिकांश मौजूदा कार्ड डिजिटल सिग्नल प्रोसेसर (DSP) का उपयोग करके ये कार्य करते हैं। PC CPU के उपयोग से समर्पित DSP की बजाय बोर्ड की कीमत में नाटकीय कमी आती है। इस प्रकार, ये कार्ड अन्य निर्माताओं के पहले उपलब्ध इंटरफ़ेस की तुलना में काफी सस्ते होते हैं। दूसरी ओर, इन कार्डों को बहुत अधिक CPU की आवश्यकता होती है; PC CPU का अनुचित उपयोग आवाज़ की गुणवत्ता को काफी प्रभावित कर सकता है। हाल ही में, Digium ने एक कोप्रोसेसर कार्ड लॉन्च किया है जो DSP का उपयोग करके G.729 और G.723 को एन्कोड और डिकोड करता है, जिससे बड़ी संख्या में चैनलों के लिए बेहतर स्केलेबिलिटी मिलती है।

## Why Asterisk?

मैं अपनी पहली बार Asterisk से संपर्क को याद करता हूँ। आमतौर पर, कुछ नया—विशेषकर वह जो आप पहले से जानते हैं, उससे प्रतिस्पर्धा करता है—को अस्वीकार करने की पहली प्रतिक्रिया होती है! यही 2003 में हुआ। Asterisk उस समाधान के साथ प्रतिस्पर्धा कर रहा था जिसे मैं एक ग्राहक को बेच रहा था (4 E1 VoIP Gateway), और यह उस समाधान की तुलना में दस गुना सस्ता था जिसे मैं पहले से जानता था। इस अत्यधिक कीमत अंतर ने मुझे संभावित खामियों और नुकसानों की पहचान करने के लिए Asterisk का अध्ययन करने के लिए प्रेरित किया। उदाहरण के तौर पर, मैंने पाया कि उस समय का PC CPU 120 g.729 समकालिक सेक्शन को सपोर्ट नहीं करता था, अंत में, मैंने अपने Gateway समाधान के साथ प्रस्ताव जीत लिया।

हालाँकि, इस अभ्यास ने मुझे यह खोजने में मदद की कि Asterisk मेरे ग्राहक आधार के लिए विभिन्न बहुत महँगे समस्याओं को हल कर सकता है। हमें IVR, यूनिफाइड मैसेजिंग, कॉल रिकॉर्डिंग, और डायलर्स के लिए महँगे कोट्स से परेशानी थी; उचित डाइमेंशनिंग के साथ, CPU समस्याओं को बायपास किया जा सकता था। वास्तव में, सिर्फ तीन वर्षों में Asterisk मेरी कंपनी का प्रमुख उत्पाद बन गया (मैंने वास्तव में Asterisk व्यवसाय के लिए एक अलग कंपनी खोलने का फैसला किया)। मेरी राय में, Asterisk टेलीकम्युनिकेशन में एक क्रांति है जो IP टेलीफोनी के लिए वही प्रतिनिधित्व करता है जैसा Apache वेब सेवाओं के लिए करता है।

### Extreme cost reduction

यदि आप डिजिटल इंटरफ़ेस और फ़ोन के संदर्भ में पारंपरिक PBX की तुलना Asterisk से करते हैं, तो Asterisk उन PBX की तुलना में थोड़ा सस्ता है। हालांकि, जब आप voicemail, ACD, IVR और CTI जैसी उन्नत सुविधाएँ जोड़ते हैं, तो Asterisk वास्तव में फायदेमंद साबित होता है। इन उन्नत सुविधाओं के साथ, Asterisk पारंपरिक PBX की तुलना में काफी कम महँगा हो जाता है। वास्तव में, Asterisk PBX की तुलना कम‑स्तरीय एनालॉग PBX से करना अनुचित है क्योंकि Asterisk कई ऐसी सुविधाएँ प्रदान करता है जो कम‑स्तरीय एनालॉग सिस्टम में उपलब्ध नहीं हैं।

### Telephony system control and independence

ग्राहकों द्वारा अक्सर उद्धृत किया जाने वाला Asterisk का एक लाभ इसकी स्वतंत्रता है। आज के कुछ निर्माताओं द्वारा ग्राहक को सिस्टम का पासवर्ड या कॉन्फ़िगरेशन दस्तावेज़ भी नहीं दिया जाता। Asterisk के “do-it-yourself” दृष्टिकोण के साथ, उपयोगकर्ता को पूर्ण स्वतंत्रता मिलती है; बोनस के तौर पर, उपयोगकर्ता को एक मानक इंटरफ़ेस तक पहुँच मिलती है।

### Easy and rapid development environment

Asterisk को AMI और AGI इंटरफ़ेस के साथ PHP और Perl जैसी स्क्रिप्ट भाषाओं का उपयोग करके विस्तारित किया जा सकता है। Asterisk ओपन‑सोर्स है, और इसका स्रोत कोड उपयोगकर्ता द्वारा संशोधित किया जा सकता है। स्रोत कोड मुख्यतः ANSI C प्रोग्रामिंग भाषा में लिखा गया है।

### Feature rich

Asterisk में कई ऐसी सुविधाएँ हैं जो पारंपरिक PBX में नहीं मिलतीं या वैकल्पिक होती हैं (जैसे voicemail, CTI, ACD, IVR, बिल्ट‑इन music on hold, और रिकॉर्डिंग)। इन सुविधाओं की लागत कुछ प्लेटफ़ॉर्म में प्लेटफ़ॉर्म की कीमत से भी अधिक हो जाती है।

### Dynamic content on the phone

Asterisk को C भाषा और आज के विकास वातावरण में सामान्य अन्य भाषाओं का उपयोग करके प्रोग्राम किया जाता है। डायनामिक कंटेंट प्रदान करने की संभावना लगभग असीमित है।

### Flexible and powerful dial plan

Asterisk की एक और बड़ी उपलब्धि इसका शक्तिशाली डायल प्लान है। पारंपरिक PBX में, सबसे कम लागत वाले रूटिंग (LCR) जैसी सरल सुविधाएँ भी या तो असंभव या वैकल्पिक होती हैं। Asterisk के साथ, सबसे अच्छा मार्ग चुनना आसान और साफ़ है।

### Open-source running on top of Linux

Asterisk की सबसे बड़ी विशेषताओं में से एक इसका समुदाय है। कई संसाधन उपलब्ध हैं, जिसमें आधिकारिक Asterisk दस्तावेज़ (docs.asterisk.org), समुदाय‑रक्षित VoIP‑Info विकी (www.voip-info.org <http://www.voip-info.org>), ई‑मेल वितरण सूचियाँ, और फ़ोर

## Main objections to Asterisk PBX

It is common to hear objections to adopting Asterisk, which we will address here.

### Asterisk’s market share is too small

The market share is usually measured by the number of PBXs sold. These statistics are generally acquired from the biggest distributors. Asterisk is free software that can be downloaded and deployed without any sale being recorded, so it is systematically undercounted in those figures. Even so, Asterisk powers a very large installed base worldwide — from single-server office PBXs to large carrier and contact-center deployments — and remains the dominant engine behind the open-source PBX ecosystem (including turnkey distributions such as FreePBX).

### If it is free, how does the manufacturer survive?

Actually, there is no such thing as an open-source software manufacturer in the traditional sense. Digium developed Asterisk since 1999, sustaining itself through sales of telephony interface cards, commercial PBX products such as Switchvox, and related software. In 2018, Sangoma Technologies acquired Digium. Sangoma continues to fund Asterisk development and generates revenue through commercial products (FreePBX commercial modules, PBXact, Switchvox), hardware sales, and professional services.

### It is hard to find technical support!

Sangoma provides commercial technical support for Asterisk through its partner ecosystem and directly via its product offerings. A global network of certified professionals provides first-line support and professional services. Community support remains active through the Asterisk forums and mailing lists at www.asterisk.org.

### Does Asterisk support more than 200 extensions?

Yes, absolutely. A single well-dimensioned Asterisk server can handle a large number of extensions, and Asterisk scales further by distributing users across multiple servers with load balancing and failover, allowing large multi-site deployments.

### Only “geeks” are able to install Asterisk

With FreePBX (available as a standalone distro from Sangoma), even professionals with limited knowledge about Linux are able to install and configure a PBX of medium complexity. With the help of a GUI, it is possible to configure an entire PBX in just a few hours.

### What if the server fails?

One of the main advantages of Asterisk is its capability to run in fault-tolerant systems. It is relatively simple and inexpensive to have two servers running in parallel. I dare you to try this with a conventional PBX!

### Our company does not use open-source software

Your company probably uses open-source software without even realizing it. Several appliances use Linux as their operating system. Moreover, commercial support and managed deployments are available from Sangoma and its certified partner network.

### Using the PC's CPU to process signaling and media is not recommended

Asterisk uses the server's CPU to process signaling and media for voice channels instead of having dedicated DSPs. Although this allows a cost reduction of up to five times, it makes the system dependent on the performance of the main CPU. With the correct dimensioning, Asterisk is capable of handling large volumes. If you still want to release the main CPU from these tasks, you can also use hardware echo cancellation and even transcoder cards, such as the Sangoma (formerly Digium) TC400B based on DSPs.

## Asterisk Architecture

This section will explain how Asterisk’s architecture works. The figure below shows the basic Asterisk architecture. Next, we will explain architecture-related concepts, including channels, codecs, and applications.

![The Asterisk architecture](../images/01-introduction-fig01.png)

### Channels

A channel is the equivalent of a telephone line, but in a digital format. It usually consists of an analog or digital (TDM) signaling system or a combination of codec and signaling protocol (e.g., SIP-GSM, IAX-uLaw). Initially, all telephony connections were analog and susceptible to echo and noise. Later, most systems were converted to digital systems, with the analogical sound converted into a digital format using pulse code modulation (PCM) in most cases. This format allows voice transmission in 64 kilobits/second without compression.

Channels interfacing with the Public Switched Telephone Network (PSTN):

- `chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards from Sangoma (formerly Digium), Xorcom, and others. Built separately against DAHDI — see the *Legacy channels* chapter.

Channels interfacing with Voice over IP:

- `chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS. Dial string: `PJSIP/endpoint_name`. (**Note:** the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22. See *Building your first PBX with PJSIP* for configuration.)
- `chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy; SIP/PJSIP is preferred for new deployments. Dial string: `IAX2/peer`.
- `chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support) but rarely used.

The older VoIP channels are no longer part of a standard Asterisk 22 build: `chan_h323` (H.323) survives only as the community `ooh323` add-on, and `chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set. If you must interwork with those protocols, a gateway in front of Asterisk is the usual approach.

Miscellaneous channels:

- **Local**: a pseudo-channel (built into the core) that loops back into the dial plan in a different context — useful for recursive routing and for fanning a call out to multiple destinations. Dial string: `Local/extension@context`.

### Codec and codec translation

We usually try to put as many voice connections as possible in a data network. Codecs enable new features in digital voice, including compression, which is one of the most important features as it allows compression rates larger than 8 to 1. Many codecs also define features such as voice activity detection (silence suppression), packet loss concealment, and comfort noise generation, though Asterisk itself does not generate comfort noise or perform silence suppression. Several codecs are available for Asterisk and can be transparently translated from one to another. Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another. Some codecs in Asterisk are supported only in pass-through mode; these codecs cannot be translated. To verify which codecs are installed in your system, you can use the console command:

```
CLI>core show translation
```

The following codecs are supported:

- G.711 ulaw (USA) - (64 Kbps).
- G.711 alaw (Europe) - (64 Kbps).
- G.722 (High Definition) – (64 Kbps)
- G.723.1 - Only pass-through mode
- G.726 - (16/24/32/40kbps)
- G.729 - Binary codec module distributed by Sangoma; the download is free of charge, but lawful use requires purchasing a per-channel license (8Kbps)
- GSM - (12-13 Kbps)
- iLBC - (15 Kbps)
- LPC10 - (2.4 Kbps)
- Speex - (2.15-44.2 Kbps)
- Opus - (6-510 Kbps)

### Protocols

एक फ़ोन से दूसरे फ़ोन तक डेटा भेजना आसान होना चाहिए बशर्ते डेटा स्वयं दूसरे फ़ोन तक पहुँचने का मार्ग खोज ले। दुर्भाग्यवश, ऐसा नहीं होता, और फ़ोनों के बीच कनेक्शन स्थापित करने, अंतिम उपकरणों की खोज करने, तथा टेलीफ़ोनी सिग्नलिंग को लागू करने के लिए एक सिग्नलिंग प्रोटोकॉल आवश्यक होता है। SIP आधुनिक डिप्लॉयमेंट्स में प्रमुख सिग्नलिंग प्रोटोकॉल है और Asterisk 22 LTS में उपलब्ध एकमात्र SIP चैनल है (chan_pjsip के माध्यम से)। IAX2 अभी भी उपलब्ध है लेकिन इसे लेगेसी माना जाता है। Asterisk निम्नलिखित प्रोटोकॉल का समर्थन करता है।

- SIP — via `chan_pjsip`
- IAX2 — लेगेसी, अभी भी Asterisk 22 में शामिल
- UNISTIM — Nortel/Avaya फ़ोन (विस्तारित समर्थन)
- H.323, MGCP, और SCCP (Cisco Skinny) — लेगेसी प्रोटोकॉल जो मानक Asterisk 22 बिल्ड में अब नहीं होते (H.323 केवल समुदाय `ooh323` ऐड‑ऑन के माध्यम से)

### Applications

एक फ़ोन से दूसरे फ़ोन तक कॉल को ब्रिज करने के लिए, एप्लिकेशन `dial()` का उपयोग किया जाता है। अधिकांश Asterisk सुविधाएँ (जैसे voicemail और conferencing) एप्लिकेशन के रूप में लागू की गई हैं। आप `core show applications` कंसोल कमांड का उपयोग करके उपलब्ध Asterisk एप्लिकेशन देख सकते हैं।

```
CLI>core show applications
```

आप Asterisk ऐड‑ऑन, तृतीय‑पक्ष प्रदाताओं से एप्लिकेशन जोड़ सकते हैं, या यहाँ तक कि वे भी जो आप स्वयं विकसित करते हैं।

## Asterisk सिस्टम का अवलोकन

Asterisk एक ओपन-सोर्स PBX है जो एक हाइब्रिड PBX की तरह कार्य करता है, जिसमें TDM और IP टेलीफ़ोनी जैसी तकनीकों को एकीकृत किया गया है। Asterisk इंटरैक्टिव वॉइस रिस्पॉन्स (IVR) और ऑटोमैटिक कॉल डिस्ट्रिब्यूशन (ACD) जैसी कार्यक्षमताओं को लागू करने के लिए तैयार है; moreover, as previously mentioned, it is open to the development of new applications. यह चित्र दर्शाता है कि Asterisk कैसे PSTN और मौजूदा PBX‑ओं से एनालॉग और डिजिटल इंटरफ़ेस का उपयोग करके जुड़ता है तथा एनालॉग और IP फ़ोन को सपोर्ट करता है। यह एक सॉफ्ट‑स्विच, मीडिया गेटवे, वॉइसमेल, और ऑडियो कॉन्फ़्रेंस के रूप में कार्य कर सकता है और इसमें बिल्ट‑इन म्यूज़िक ऑन होल्ड भी है।

![Asterisk सिस्टम का अवलोकन](../images/01-introduction-fig02.png)

## Comparing the old and the new world

पुराने सॉफ़्ट‑स्विच मॉडल में, सभी घटकों को अलग‑अलग बेचा जाता था, अर्थात् आपको प्रत्येक घटक को अलग‑अलग खरीदना पड़ता था और फिर उसे PBX या सॉफ़्ट‑स्विच वातावरण में एकीकृत करना पड़ता था। लागत और जोखिम दोनों अधिक थे और अधिकांश उपकरण स्वामित्व वाले थे।

![The old world: components bought and integrated separately](../images/01-introduction-fig03.png)

### Telephony using Asterisk

सभी कार्य Asterisk प्लेटफ़ॉर्म में एक ही या विभिन्न बॉक्सों में आयाम के अनुसार एकीकृत होते हैं, और सभी GPL लाइसेंस के तहत हैं। कभी‑कभी Asterisk को स्थापित करना मुख्यधारा के IP‑PBX को लाइसेंस करने से आसान होता है।

![Telephony using Asterisk: the functions are integrated](../images/01-introduction-fig04.png)

## Building a test system

When implementing an Asterisk solution, our first step is generally to build a test system. The goal is a minimal **1×1 PBX** — one phone that can call another — so you can try out endpoints, dialplan, and features before touching production. Today this is entirely software: you do not need any telephony hardware.

![A simple Asterisk test system](../images/01-introduction-fig05.png)

### The modern way: a software lab (recommended)

The fastest test system is Asterisk 22 running in a container or virtual machine, with **softphones** for the endpoints and, optionally, a **SIP trunk** to reach the public network:

- **Asterisk 22** on a small Linux box, VM, or Docker container. This book ships a ready-made Docker lab (see the lab guide) that boots a fully configured Asterisk 22 with a single command — no compilation, no hardware.
- **Two softphones** registered as PJSIP endpoints, so you can place a real call between them. Throughout this book we use the **SipPulse Softphone** (free download: <https://www.sippulse.com/produtos/softphone>), available for desktop and mobile.
- **A SIP trunk** (optional) from a VoIP provider, for when you want to reach the PSTN. No card and no analog line — just credentials.

This is how every example in this book is built and verified, and you can reproduce it on any laptop.

### The legacy way: analog/digital cards

Before VoIP, a test PBX needed physical interfaces: an **FXO** port to connect to an existing telephone line and an **FXS** port to connect an analog phone, which together gave you a 1×1 PBX. A single card carrying one FXO and one FXS interface was the classic starter kit. These DAHDI-based cards (from Sangoma, formerly Digium) still exist for sites that must terminate analog or T1/E1 lines, but they are niche today — most deployments are pure VoIP. If you only need to connect analog phones or lines, see the *Legacy Channels* chapter; otherwise you can skip telephony hardware entirely.

## Asterisk परिदृश्य

Asterisk को कई विभिन्न परिदृश्यों में उपयोग किया जा सकता है। हम उनमें से कुछ की सूची देंगे और प्रत्येक के लाभ और संभावित सीमाओं को समझाएंगे।

### IP PBX

सबसे आम परिदृश्य नया PBX स्थापित करना या मौजूदा PBX को बदलना है। यदि आप Asterisk की तुलना कुछ अन्य विकल्पों से करते हैं, तो आप पाएँगे कि यह अधिकांश उपलब्ध PBX की तुलना में सस्ता और सुविधाओं में अधिक समृद्ध है। कई कंपनियाँ अब अपने विनिर्देशों को अन्य ब्रांड‑नाम PBX की बजाय Asterisk में बदल रही हैं।

![Asterisk एक IP PBX के रूप में](../images/01-introduction-fig06.png)

### IP-सक्षम लेगेसी PBXs

The following image illustrates one of the most commonly used setups. Large companies generally do not want to take significant risk when investing in new technologies and simultaneously wish to preserve their investments in legacy equipment. IP-enabling legacy PBX can be very expensive; thus, connecting an Asterisk PBX using T1/E1 lines can be a good alternative for cost-conscious customers. Another benefit is the possibility of connecting to a VoIP service provider with better telephony rates.

![लेगेसी PBX को IP-सक्षम बनाना](../images/01-introduction-fig07.png)

### टोल बायपास

A very useful application for VoIP is connecting branch offices over the Internet or a WAN. Using an existing data connection allows you to bypass toll charges incurred in telecommunication connections between headquarters and branch offices.

![WAN पर कार्यालयों के बीच टोल बायपास](../images/01-introduction-fig08.png)

### एप्लिकेशन सर्वर (IVR, Conference, Voicemail)

Asterisk को मौजूदा PBX के लिए एक एप्लिकेशन सर्वर के रूप में उपयोग किया जा सकता है या सीधे PSTN से जोड़ा जा सकता है। Asterisk वॉइसमेल, फ़ैक्स रिसेप्शन, कॉल रिकॉर्डिंग, डेटाबेस से जुड़ा IVR, और एक ऑडियो कॉन्फ़्रेंसिंग सर्वर जैसी सेवाएँ प्रदान करता है। यदि आप वॉइसमेल और फ़ैक्स को मौजूदा ई‑मेल सर्वर में एकीकृत करते हैं, तो आपके पास एक एकीकृत मैसेजिंग सिस्टम होगा, जो आमतौर पर एक महँगा समाधान होता है। Asterisk को एप्लिकेशन सर्वर के रूप में उपयोग करने से अन्य समाधानों की तुलना में अत्यधिक लागत में कमी आती है।

![एस्टेरिस्क एक एप्लिकेशन सर्वर के रूप में](../images/01-introduction-fig09.png)

### Media Gateway

अधिकांश वॉइस-ओवर IP सेवा प्रदाता सभी SIP उपयोगकर्ताओं की पंजीकरण, स्थान और प्रमाणीकरण को होस्ट करने के लिए एक SIP प्रॉक्सी का उपयोग करते हैं। उन्हें अभी भी कॉल को सीधे PSTN पर भेजना पड़ता है या एक थोक कॉल टर्मिनेशन प्रदाता के माध्यम से SIP या H.323 वॉइस-ओवर IP कनेक्शन का उपयोग करके रूट करना पड़ता है। Asterisk बैक-टू-बैक यूज़र एजेंट (B2BUA) या मीडिया गेटवे के रूप में कार्य कर सकता है, जिससे बहुत महंगे सॉफ्ट स्विच या मीडिया गेटवे की जगह ली जा सकती है। मुख्य बाजार निर्माताओं से चार E1/T1 गेटवे की कीमत की तुलना Asterisk से करें। Asterisk समाधान अन्य समाधानों की तुलना में कई गुना कम लागत वाला हो सकता है और सिग्नलिंग प्रोटोकॉल (H.323, SIP, IAX…) और कोडेक (G.711, G.729…) को अनुवादित करने में सक्षम है।

![मीडिया गेटवे के रूप में Asterisk](../images/01-introduction-fig10.png)

### संपर्क केंद्र प्लेटफ़ॉर्म

एक संपर्क केंद्र एक बहुत जटिल समाधान है जो कई तकनीकों को मिलाता है, जैसे स्वचालित कॉल वितरण (ACD), इंटरैक्टिव वॉइस रिस्पॉन्स (IVR), और कॉल सुपरविजन। मूल रूप से, संपर्क केंद्रों के तीन प्रकार उपलब्ध हैं: इनबाउंड, आउटबाउंड, और ब्लेंडेड।

Inbound contact centers बहुत परिष्कृत होते हैं और आमतौर पर ACD, IVR, CTI, रिकॉर्डिंग, सुपरविजन, और रिपोर्ट्स की आवश्यकता होती है। Asterisk में कॉलों को कतारबद्ध करने के लिए एक अंतर्निहित ACD है। IVR को Asterisk Gateway Interface (AGI) या आंतरिक तंत्र जैसे application background() का उपयोग करके किया जा सकता है। कंप्यूटर टेलीफ़ोनी इंटीग्रेशन (CTI) को Asterisk Manager Interface (AMI) के माध्यम से प्राप्त किया जाता है; रिकॉर्डिंग और रिपोर्टिंग Asterisk में निर्मित हैं।

एक आउटबाउंड कॉन्टैक्ट सेंटर के लिए, प्रेडिक्टिव या पावर डायलर मुख्य घटकों में से एक है। जबकि ओपन-सोर्स Asterisk के लिए कई डायलर उपलब्ध हैं, यदि आप चाहें तो प्लेटफ़ॉर्म के लिए अपना स्वयं का बनाना कठिन नहीं है। एक ब्लेंडेड कॉन्टैक्ट सेंटर समकालिक इनबाउंड और आउटबाउंड संचालन की अनुमति देता है, एजेंट के समय के बेहतर उपयोग को सुनिश्चित करके पैसे बचाता है। Asterisk और उसके ACD मैकेनिज़्म का उपयोग करके एक ब्लेंडेड समाधान लागू करना संभव है।

![एक Asterisk संपर्क-केन्द्र मंच](../images/01-introduction-fig11.png)

## जानकारी और सहायता प्राप्त करना

यह अनुभाग Asterisk से संबंधित मुख्य सूचना स्रोतों में से कुछ प्रदान करेगा।

- Asterisk की आधिकारिक वेबसाइट: <https://www.asterisk.org> यहाँ आप जानकारी पा सकते हैं:
- Documentation & Wiki -> <https://docs.asterisk.org>
- Community forum -> <https://community.asterisk.org>
- Bug tracking -> <https://github.com/asterisk/asterisk/issues>
- Wiki (legacy, largely superseded by docs.asterisk.org) -> <https://wiki.asterisk.org>

### Community forum

Asterisk समुदाय फ़ोरम ने पुराने मेलिंग सूचियों को काफी हद तक प्रतिस्थापित कर दिया है और यह प्रश्न पूछने की जगह है। पोस्ट करने से पहले यथासंभव अधिक जानकारी इकट्ठा करने का प्रयास करें। यदि आपने अपना होमवर्क नहीं किया है तो कोई भी आपकी मदद नहीं करेगा — कम से कम एक बार स्वयं समस्या को हल करने की कोशिश करें।

- <https://community.asterisk.org>

## Summary

Asterisk एक सॉफ़्टवेयर है जो GPL के तहत लाइसेंस किया गया है और एक सामान्य PC को एक शक्तिशाली IP PBX प्लेटफ़ॉर्म के रूप में कार्य करने में सक्षम बनाता है। Digium के Mark Spencer ने 1990 के दशक के अंत में Asterisk बनाया, और Digium ने Asterisk‑संबंधित हार्डवेयर और व्यावसायिक उत्पाद बेचकर अपना संचालन जारी रखा। Digium का 2018 में Sangoma Technologies द्वारा अधिग्रहण किया गया; अब Sangoma Asterisk विकास को प्रायोजित करता है। हार्डवेयर इंटरफ़ेस डिज़ाइन की उत्पत्ति Jim Dixon द्वारा विकसित Zapata प्रोजेक्ट से हुई, जिससे DAHDI का जन्म हुआ।

Asterisk आर्किटेक्चर में निम्नलिखित मुख्य घटक होते हैं:

- CHANNELS: Analog, digital, या voice‑over IP. Asterisk 22 LTS में, SIP को केवल `chan_pjsip` द्वारा संभाला जाता है।
- PROTOCOLS: संचार प्रोटोकॉल, जो कॉल सिग्नलिंग के लिए ज़िम्मेदार होते हैं, जिसमें SIP (via PJSIP), H.323, MGCP, और IAX2 शामिल हैं।
- CODECS: आवाज़ के डिजिटल फ़ॉर्मेट को अनुवादित करते हैं जिससे संपीड़न और पैकेट लॉस कंसिलिएशन संभव हो सके। ध्यान दें कि Asterisk स्वयं साइलेंस सप्रेशन (voice activity detection) या कॉफ़र्ट‑नॉइज़ जेनरेशन नहीं करता; जब एंडपॉइंट VAD का उपयोग करते हैं, तो क्लाइंट साइड पर कॉफ़र्ट नॉइज़ को निष्क्रिय किया जाना चाहिए।
- APPLICATIONS: Asterisk PBX कार्यक्षमता के लिए ज़िम्मेदार। Conference, voicemail, और fax Asterisk एप्लिकेशनों के उदाहरण हैं।

Asterisk को विभिन्न परिदृश्यों में उपयोग किया जा सकता है, छोटे IP PBX से लेकर एक परिष्कृत कॉन्टैक्ट सेंटर तक। आप आसानी से मदद www.asterisk.org और docs.asterisk.org पर पा सकते हैं।

## Quiz

1. कौन सी कंपनी ने 2018 में Digium का अधिग्रहण किया और अब Asterisk ओपन‑सोर्स प्रोजेक्ट की मुख्य देखरेख करती है?
   - A. Cisco Systems
   - B. Sangoma Technologies
   - C. Nortel Networks
   - D. Red Hat

2. Asterisk 22 LTS में, कौन सा चैनल ड्राइवर SIP कनेक्टिविटी प्रदान करता है?
   - A. `chan_sip`
   - B. `chan_skinny`
   - C. `chan_pjsip`
   - D. `chan_h323`

3. सत्य या असत्य: `chan_sip` चैनल ड्राइवर को Asterisk 21 में हटा दिया गया और यह मानक Asterisk 22 बिल्ड में मौजूद नहीं है।

4. निम्नलिखित में से कौन‑से चैनल/प्रोटोकॉल **अब** मानक Asterisk 22 बिल्ड का हिस्सा नहीं हैं? (सभी लागू विकल्प चुनें।)
   - A. MGCP (`chan_mgcp`)
   - B. SCCP / Cisco Skinny (`chan_skinny`)
   - C. IAX2 (`chan_iax2`)
   - D. H.323 (`chan_h323`, केवल समुदाय `ooh323` ऐड‑ऑन के रूप में बचा है)

5. Zapata प्रोजेक्ट की हार्डवेयर आर्किटेक्चर, जिसे मूल रूप से Zaptel कहा जाता था, बाद में ____ नाम से पुनःनामित की गई।
   - A. DAHDI
   - B. PJSIP
   - C. PRI
   - D. mISDN

6. जब Asterisk को एक कोडेक से दूसरे कोडेक में ऑडियो बदलना पड़ता है, तो वह किस आंतरिक स्ट्रीम फ़ॉर्मेट के माध्यम से अनुवाद करता है?
   - A. G.711 ulaw
   - B. GSM
   - C. slinear (signed linear)
   - D. Opus

7. अध्याय के अनुसार, Sangoma द्वारा वितरित G.729 कोडेक मॉड्यूल का लाइसेंसिंग स्थिति क्या है?
   - A. यह GPL है और किसी भी उपयोग के लिए पूरी तरह मुफ्त है।
   - B. डाउनलोड मुफ्त है, लेकिन वैध उपयोग के लिए प्रति‑चैनल लाइसेंस खरीदना आवश्यक है।
   - C. इसे बिल्कुल भी प्राप्त नहीं किया जा सकता जब तक कि Asterisk Business Edition न खरीदा जाए।
   - D. यह केवल पास‑थ्रू मोड में काम करता है और स्थापित नहीं किया जा सकता।

8. कौन सा Asterisk एप्लिकेशन एक कॉल को एक फोन से दूसरे फोन तक ब्रिज करने के लिए उपयोग किया जाता है?
   - A. `Background()`
   - B. `Dial()`
   - C. `Queue()`
   - D. `Goto()`

9. Asterisk में `Local` चैनल क्या है?
   - A. एनालॉग फ़ोनों के लिए हार्डवेयर FXS इंटरफ़ेस।
   - B. स्थानीय सेवा प्रदाता के लिए एक SIP ट्रंक।
   - C. एक छद्म‑चैनल जो कॉल को अलग संदर्भ में डायल‑प्लान में वापस लूप करता है।
   - D. ऑन‑नेट कॉलों के लिए उपयोग किया जाने वाला कोडेक।

10. किस उपयोग परिदृश्य में Asterisk एक बैक‑टू‑बैक यूज़र एजेंट (B2BUA) के रूप में कार्य करता है, सिग्नलिंग प्रोटोकॉल और कोडेक्स के बीच अनुवाद करके महंगे SoftSwitch को बदलता है?
    - A. लेगेसी PBX को IP‑सक्षम बनाना
    - B. टोल बायपास
    - C. मीडिया गेटवे
    - D. कॉन्टैक्ट सेंटर प्लेटफ़ॉर्म

**Answers:** 1 — B · 2 — C · 3 — True · 4 — A, B, D · 5 — A · 6 — C · 7 — B · 8 — B · 9 — C · 10 — C
