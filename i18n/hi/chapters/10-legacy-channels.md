# Legacy channels: analog, TDM & IAX2

2026 के शुद्ध‑VoIP विश्व में, इस अध्याय में वर्णित चैनल प्रकार धीरे‑धीरे दुर्लभ होते जा रहे हैं: अधिकांश नई तैनाती Ethernet पर SIP ट्रंक और PJSIP एंडपॉइंट्स के रूप में होती हैं, और कोई टेलीफ़ोनी हार्डवेयर नहीं होता। फिर भी Asterisk 22 अधिकांश को पूरी तरह समर्थन देता है। एनालॉग (FXO/FXS) और डिजिटल TDM (E1/T1/ISDN PRI/BRI) कनेक्टिविटी DAHDI के माध्यम से प्रदान की जाती है — वह ड्राइवर स्टैक जो मूल रूप से Digium द्वारा विकसित किया गया था, और 2018 में Sangoma द्वारा अधिग्रहित किया गया, जब पहले के Zaptel ड्राइवरों का नाम ट्रेडमार्क विवाद के कारण बदल दिया गया था। सर्वर‑से‑सर्वर कनेक्टिविटी IAX2 के माध्यम से `chan_iax2` द्वारा प्रदान की जाती है, जो अभी भी शिप और समर्थित है लेकिन अब यह एक पुरानी प्रोटोकॉल है।

यह अध्याय **legacy SIP** सामग्री को भी इकट्ठा करता है: पुराना `chan_sip` ड्राइवर और उसकी `sip.conf` कॉन्फ़िगरेशन — जिसे Asterisk 21 में हटाया गया और Asterisk 22 में पूरी तरह समाप्त कर दिया गया — साथ ही मौजूदा `sip.conf` सिस्टम को PJSIP में माइग्रेट करने के लिए एक पूर्ण गाइड। यदि आप PJSIP पर शुद्ध‑SIP शॉप चला रहे हैं, बिना टेलीफ़ोनी कार्ड, बिना IAX2 ट्रंक, और बिना किसी legacy `sip.conf` को परिवर्तित करने की आवश्यकता के, तो आप इस अध्याय को सुरक्षित रूप से छोड़ सकते हैं।

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk to analog lines and phones with FXO/FXS interfaces through DAHDI;
- Recognize digital TDM connectivity (E1/T1, ISDN PRI/BRI) and how it is configured;
- Configure IAX2 (`chan_iax2`) for server-to-server trunks and understand why it is now legacy;
- Identify the retired `chan_sip` driver and the `sip.conf` syntax you may still encounter; and
- Migrate an existing `chan_sip`/`sip.conf` system to PJSIP.

## Analog channels (FXO/FXS)

Asterisk 22 से, DAHDI और एनालॉग टेलीफ़ोनी कार्ड पूरी तरह से समर्थित हैं, और DAHDI अभी भी वर्तमान कर्नेल्स के खिलाफ बनता है। अधिकांश नई डिप्लॉयमेंट्स फिर भी शुद्ध VoIP (SIP trunks, PJSIP) हैं, इसलिए एनालॉग/TDM हार्डवेयर अब एक निच विकल्प है — मुख्यतः लेगेसी वातावरण, ग्रामीण PSTN कनेक्टिविटी, या नियामक बाजारों में पाया जाता है। नीचे दिया गया सब कुछ उन परिदृश्यों पर लागू होता है।

पब्लिक स्विच्ड टेलीफ़ोन नेटवर्क (PSTN) से जुड़ने के कई तरीके हैं। सबसे अच्छा तरीका इस बात पर निर्भर करता है कि टेलीफ़ोन कंपनी आपके क्षेत्र में यह कनेक्शन कैसे उपलब्ध कराती है। सबसे सरल तरीका है एक एनालॉग लाइन का उपयोग करना, जैसे वह लाइन जो आप घर पर उपयोग करते हैं। इस सेक्शन में, हम आपको Sangoma™ (पहले Digium™) और Xorcom™ के एनालॉग कार्ड को कॉन्फ़िगर करने का तरीका दिखाएंगे।

### Objectives

इस अध्याय के अंत तक आपको सक्षम होना चाहिए:

- मुख्य टेलीफ़ोनी शब्दों और संक्षेपों को पहचानना;
- डिजिटल और एनालॉग सर्किट्स का उपयोग कब करना है, समझना;
- FXS और FXO के बीच अंतर को पहचानना; और
- Asterisk को FXS और FXO के लिए कॉन्फ़िगर करना।

### Telephony basics

अधिकांश एनालॉग इम्प्लीमेंटेशन दो कूपर लाइनों का उपयोग करते हैं जिन्हें tip और ring कहा जाता है। जब लूप बंद हो जाता है, तो फोन टेलीकोम स्विच (या प्राइवेट PBX) से डायल टोन प्राप्त करता है। सबसे अधिक उपयोग किया जाने वाला सिग्नलिंग लूप-स्टार्ट है; अन्य, कम सामान्य सिग्नलिंग प्रकारों में ग्राउंड स्टार्ट शामिल है, जो कई देशों में उपयोग होता है। सिग्नलिंग के तीन वर्ग हैं:

- Supervision signaling
- Address signaling
- Information signaling

#### Supervision signaling

मुख्य सुपरविजन सिग्नलिंग हैं ऑन-हुक, ऑफ-हुक, और रिंगिंग।

- **On-Hook** – जब उपयोगकर्ता फोन को हुक पर रखता है, तो PBX सर्किट को बाधित कर देता है और विद्युत धारा को गुजरने नहीं देता। इस स्थिति में सर्किट को ऑन-हुक कहा जाता है। इस स्थिति में केवल रिंगर सक्रिय रहता है।
- **Off-Hook** – फोन कॉल शुरू करने से पहले, फोन को ऑफ-हुक स्थिति में जाना पड़ता है। हैंडसेट को हुक से हटाने से लूप बंद हो जाता है और PBX को संकेत मिलता है कि उपयोगकर्ता कॉल करना चाहता है। यह संकेत मिलने पर, PBX एक डायल टोन उत्पन्न करता है, जिससे उपयोगकर्ता को पता चलता है कि वह गंतव्य पता (अर्थात् फोन नंबर) दर्ज करने के लिए तैयार है।
- **Ringing** – जब उपयोगकर्ता किसी अन्य फोन को कॉल करता है, तो वह रिंगर को एक वोल्टेज भेजता है जो दूसरे उपयोगकर्ता को कॉल प्राप्त होने की सूचना देता है। सिग्नलिंग देश के अनुसार बदलती है, विभिन्न देशों के लिए अलग-अलग टोन होते हैं।

आप `indications.conf` फ़ाइल को संशोधित करके अपने देश के अनुसार Asterisk टोन को व्यक्तिगत बना सकते हैं। उदाहरण के लिए:

```
[br]
description=Brazil
ringcadance=1000,4000
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
congestion=425/250,0/250,425/750,0/250
callwaiting=425/50,0/1000
```

#### पता संकेत

आप डायलिंग के लिए दो प्रकार के सिग्नलिंग का उपयोग कर सकते हैं। पहला और सबसे आम ड्यूल टोन मल्टी‑फ़्रीक्वेंसी (dtmf) है जबकि दूसरा पल्स डायलिंग (पुराने रोटरी डायल फ़ोन में उपयोग होता था) है। फ़ोन में डायलिंग के लिए एक कीपैड होता है, और प्रत्येक बटन दो फ़्रीक्वेंसी से जुड़ा होता है: एक उच्च और एक निम्न। dtmf सिग्नलिंग के मामले में, इन टोन का संयोजन यह दर्शाता है कि कौन सा अंक दबाया गया है। MFC/R2 एक मल्टी‑फ़्रीक्वेंसी टोन का उपयोग करता है जो dtmf से अलग है।

#### सूचना संकेतन

Information signaling shows the call’s progress and different events.

- डायल टोन
- व्यस्त टोन
- रिंगबैक
- भीड़
- अमान्य संख्या
- पुष्टि टोन

### PSTN इंटरफ़ेस

जैसे पुराने PBX के मामले में, अक्सर Asterisk PBX को PSTN से जोड़ना आवश्यक होता है। यहाँ हम दिखाएंगे कि इसे कैसे किया जाए। आमतौर पर आपके पास टेलीफोन लाइनों के लिए तीन विकल्प होते हैं।

- Analog: घर और छोटे व्यवसायों के लिए सबसे आम रूप, आमतौर पर तांबे की धातु की जोड़ी वाली लाइनों के साथ प्रदान किया जाता है।  
- Digital: कई लाइनों की आवश्यकता होने पर उपयोग किया जाता है। एक डिजिटल लाइन आमतौर पर CSU/DSU या फ़ाइबर मल्टीप्लेक्सर द्वारा प्रदान की जाती है। अंतिम उपयोगकर्ता कनेक्टर आमतौर पर RJ45 होता है। कुछ देशों में, E1 लाइनों को दो कोएक्सियल BNC कनेक्टरों का उपयोग करके प्रदान किया जाता है; इस स्थिति में आपको RJ45 जैक को टेलीफ़ोनी बोर्ड से जोड़ने के लिए एक बैलून की आवश्यकता होगी।  
- SIP: यह विकल्प हाल ही में विकसित किया गया है। टेलीफ़ोन लाइन SIP सिग्नलिंग (VoIP) के साथ डेटा कनेक्शन का उपयोग करके प्रदान की जाती है। यह Asterisk के साथ उपयोग करने के लिए एक अच्छा विकल्प है क्योंकि आपको टेलीफ़ोनी कार्ड खरीदने की आवश्यकता नहीं होगी। फ़ोन कॉल सीधे Ethernet पोर्ट पर पहुंचाए जाएंगे। एक और लाभ यह है कि कोडेक ट्रांसकोडिंग से बचकर आप अपने CPU से संसाधन मुक्त कर सकते हैं।

### एनालॉग FXS, FXO, और E&M इंटरफ़ेस

कई प्रकार के एनालॉग इंटरफ़ेस उपलब्ध हैं। फ़ोन नेटवर्क तथा अन्य PBX से कनेक्ट करने के तरीके को समझने के लिए इन इंटरफ़ेसों के बीच अंतर को समझना मूलभूत है। यहाँ, हम आपको E&M इंटरफ़ेस दिखाएंगे। यद्यपि यह वर्तमान में Asterisk के लिए उपलब्ध नहीं है और कई विक्रेताओं द्वारा इसे बंद कर दिया गया है, आप इस प्रकार के इंटरफ़ेस वाले राउटर और PBX पा सकते हैं, इसलिए यह जानना बेहतर है कि आप किस चीज़ से निपट रहे हैं।

#### विदेशी विनिमय (FX) इंटरफ़ेस

FX interfaces are analog. The term “Foreign eXchange” is applied to access trunks to a PSTN central office (CO). Foreign eXchange Office (FXO)

![एक एस्टरिस्क एनालॉग फोन (FXS) और टेलको लाइन (FXO) के बीच: FXS पक्ष फोन को डायल टोन और रिंगिंग प्रदान करता है, जबकि FXO पक्ष सेंट्रल ऑफिस से डायल टोन लेता है।](../images/10-legacy-fig01.png)

FXO इंटरफ़ेस का उपयोग एक सेंट्रल ऑफिस (CO) या किसी अन्य PBX के एक्सटेंशन से कनेक्ट करने के लिए किया जाता है। यह सीधे PSTN से आने वाली टेलीफ़ोन लाइन के साथ संचार करता है। एक अन्य विकल्प यह है कि FXO इंटरफ़ेस को मौजूदा PBX से जोड़ा जाए, जिससे Asterisk और लेगेसी PBX के बीच संचार संभव हो सके। Asterisk को एक PBX पोर्ट से जोड़ना और VoIP के माध्यम से एक रिमोट एक्सटेंशन प्रदान करना अक्सर ऑफ‑प्रॉमिसेज़ एक्सटेंशन (OPX) कहा जाता है। एक FXO इंटरफ़ेस डायल टोन प्राप्त करता है।  

Foreign eXchange Station (FXS)  
FXS इंटरफ़ेस एक एनालॉग फ़ोन, मोडेम, या फ़ैक्स को सप्लाई करता है। FXS फ़ोन के लिए डायल टोन और पावर प्रदान करता है।

#### ट्रंक सिग्नलिंग

- लूप-स्टार्ट
- ग्राउंड-स्टार्ट
- क्वेलस्टार्ट

Asterisk में kewlstart सिग्नलिंग का उपयोग लगभग डिफ़ॉल्ट है। Kewlstart स्वयं सिग्नलिंग नहीं है, बल्कि सर्किट में बुद्धिमत्ता जोड़ता है जिससे यह पता चलता है कि दूसरी ओर क्या हो रहा है। Kewlstart लूप‑स्टार्ट पर आधारित है। अधिकांश स्विच इस सुविधा का समर्थन नहीं करते, जिसका उपयोग हैंग‑अप नोटिफिकेशन प्राप्त करने के लिए किया जाता है।

- Loopstart: अधिकांश एनालॉग लाइनों में उपयोग किया जाता है, यह टेलीफोन को “ऑन‑हुक” और “ऑफ‑हुक” संकेत देने तथा स्विच को “रिंग” और “नो‑रिंग” संकेत देने की अनुमति देता है। यह संभवतः वही है जो अधिकांश लोगों के घर में होता है। नाम इस तथ्य से आया है कि लाइन हमेशा खुली रहती है। जब आप लूप को बंद करते हैं, तो स्विच आपको डायल टोन प्रदान करता है। एक इनकमिंग कॉल को खुले जोड़े पर 100V रिंगिंग वोल्टेज द्वारा संकेतित किया जाता है।

![Asterisk एक VoIP गेटवे के रूप में कार्य कर रहा है: एक FXO पोर्ट एक लेगेसी PBX एक्सटेंशन से जुड़ता है जबकि एक रिमोट Asterisk उस लाइन को IP के माध्यम से एक एनालॉग फोन तक FXS पोर्ट (एक ऑफ‑प्रेमाइसेस एक्सटेंशन, या OPX) के द्वारा पहुँचाता है।](../images/10-legacy-fig02.png)

- Groundstart: Loopstart के समान। जब आप कॉल करना चाहते हैं, तो लाइन का एक पक्ष शॉर्ट‑सर्किट हो जाता है। जब स्विच इस स्थिति की पहचान करता है, तो वह खुले जोड़े के माध्यम से वोल्टेज को उलट देता है, और फिर लूप बंद हो जाता है। परिणामस्वरूप, लाइन पहले व्यस्त हो जाती है फिर कॉलर को पेश की जाती है।
- Kewlstart: सर्किट्स में बुद्धिमत्ता जोड़ता है, जिससे दूसरी ओर की निगरानी संभव होती है। Kewlstart लूप‑स्टार्ट से कई लाभों को सम्मिलित करता है।

### Asterisk टेलीफ़ोनी चैनल सेटअप

एक टेलीफ़ोनी इंटरफ़ेस कार्ड को कॉन्फ़िगर करने के लिए कई चरण आवश्यक होते हैं। इस अध्याय में, हम सबसे सामान्य तीन परिदृश्यों को दिखाएंगे:

- FXS का उपयोग करके एनालॉग कनेक्शन
- FXO का उपयोग करके एनालॉग कनेक्शन
- FXS और FXO इंटरफ़ेस वाले Astribank™ का कनेक्शन

### कॉन्फ़िगरेशन प्रक्रिया (दोनों मामलों में मान्य)

Asterisk के लिए हार्डवेयर चुनने से पहले, आपको स्थापित और सक्षम किए जाने वाले समानांतर कॉलों की संख्या, सेवाओं और कोडेक्स पर विचार करना चाहिए। Asterisk एक CPU‑गहन एप्लिकेशन है, इसलिए हम Asterisk के लिए एक समर्पित मशीन की सिफारिश करते हैं। कंप्यूटर में स्थापित इंटरफ़ेस कार्डों की संख्या स्लॉट और इंटरप्शन की उपलब्धता पर निर्भर करती है। आठ वॉइस इंटरफ़ेस वाले एक कार्ड को दो चार‑इंटरफ़ेस वाले कार्डों की तुलना में स्थापित करना अधिक पसंदनीय है। एक अन्य विकल्प USB चैनल बैंक का उपयोग करना है, जैसे Xorcom Astribank। हाल ही में कुछ निर्माताओं (जैसे CIANET) ने TDMoE चैनल बैंक बनाना शुरू कर दिया है, जिससे दर्जनों एनालॉग इंटरफ़ेस को जोड़ना और भी आसान हो गया है।

![एक Xorcom Astribank: 19‑इंच रैक‑माउंट USB चैनल बैंक जो कई FXS/FXO पोर्ट्स (यहाँ 32‑पोर्ट यूनिट) को प्रदर्शित करता है, बिना होस्ट में PCI स्लॉट्स का उपयोग किए।](../images/10-legacy-fig03.png)

#### Example 1: One FXO, one FXS installation

इस उदाहरण में, हम एक Sangoma TDM400 टेलीफ़ोनी इंटरफ़ेस कार्ड (पहले Digium TDM400 के रूप में बेचा जाता था) का उपयोग करेंगे जिसमें एक FXS और एक FXO मॉड्यूल है। आवश्यक चरण नीचे सूचीबद्ध हैं:

1. एनालॉग कार्ड FXS, FXO, या दोनों स्थापित करें।  
2. फ़ाइल `/etc/dahdi/system.conf` को कॉन्फ़िगर करें (पहले `/etc/zaptel.conf` था)।  
3. `dahdi_genconf` का उपयोग करके कॉन्फ़िगरेशन फ़ाइलें उत्पन्न करें।  
4. DAHDI इंटरफ़ेस के लिए ड्राइवर लोड करें।  
5. इंटरप्ट मिसेज़ को सत्यापित करने के लिए `dahdi_test` चलाएँ।  
6. ड्राइवर को कॉन्फ़िगर करने के लिए `dahdi_cfg` चलाएँ।  
7. `chan_dahdi.conf` फ़ाइल में DAHDI चैनल को कॉन्फ़िगर करें, फिर Asterisk लोड करें।

##### Step 1: TDM400 बोर्ड स्थापित करें

TDM404P कार्ड में FXS और FXO मॉड्यूल होते हैं। FXS (S110M, हरा) और FXO (X100M, लाल) मॉड्यूल को कनेक्ट करें। यदि आप FXS मॉड्यूल का उपयोग कर रहे हैं, तो कार्ड को सीधे एक मोलेक्स कनेक्टर का उपयोग करके पावर स्रोत से जोड़ें। हार्डवेयर को नुकसान से बचाने के लिए इंटरफ़ेस कार्ड संभालने से पहले इलेक्ट्रोस्टैटिक प्रोटेक्शन पहनें। Sangoma (पहले Digium) एनालॉग कार्ड भी एक हार्डवेयर इको कैंसलेशन मॉड्यूल VPMADT032 का समर्थन करते हैं।

##### चरण 2: dahdi_genconf के साथ कॉन्फ़िगरेशन उत्पन्न करें

कॉन्फ़िगरेशन के बारे में अच्छी खबर यह है कि नया यूटिलिटी `dahdi_genconf`, जो स्वचालित रूप से DAHDI इंटरफ़ेस के लिए कॉन्फ़िगरेशन का पता लगाता है और उत्पन्न करता है। यह यूटिलिटी दो फ़ाइलें बनाती है:

- `/etc/dahdi/system.conf`
- `/etc/asterisk/dahdi-channels.conf`
- `/etc/asterisk/users.conf` (`users` विकल्प के साथ)
- इन सभी फ़ाइलों में विकल्प `chan_dahdi full` का उपयोग किया जाता है

Before you can execute `dahdi_genconf`, it is important to configure the file `genconf_parameters` (often referred to as `gen_parameters.conf`):

![एक Sangoma/Digium TDM404P एनालॉग कार्ड: चार तक FXS या FXO मॉड्यूल क्रमांकित पोर्ट्स में प्लग किए जा सकते हैं, एक वैकल्पिक हार्डवेयर इको‑कैंसलेशन डॉटर कार्ड और FXS मॉड्यूल के लिए समर्पित 12 V पावर कनेक्टर के साथ।](../images/10-legacy-fig04.png)

```
#
# /etc/dahdi/genconf_parameters
#
# This file contains parameters that affect the
# dahdi_genconf configurator generator.
#
#base_exten          4000
#fxs_immediate       no
#fxs_default_start   ks
#lc_country          il
#context_lines       from-pstn
#context_phones      from-internal
#context_input       astbank-input
#context_output      astbank-output
#group_phones        0
#group_lines         5
#brint_overlap
#bri_sig_style       bri_ptmp
#
# The echo canceller to use. If you have a hardware echo canceller, just
# leave it be, as this one won't be used anyway.
#
# The default is mg2, but it may change in the future. E.g: a packager
# that bundles a better echo canceller may set it as the default, or
# dahdi_genconf will scan for the "best" echo canceller.
#
#echo_can            hpec
#echo_can            oslec
#echo_can            none   # to avoid echo cancellers altogether
# bri_hardhdlc: If this parameter is set to 'yes', in the entries for
# BRI cards 'hardhdlc' will be used instead of 'dchan' (an alias for
# 'fcshdlc').
#
#bri_hardhdlc        yes
# For MFC/R2 Support
#pri_connection_type R2
#r2_idle_bits        1101
# pri_types contains a list of settings:
# Currently the only setting is for TE or NT (the default is TE)
#
#pri_termtype
# SPAN/2              NT
# SPAN/4              NT
```

The `genconf_parameters` file lets you customize your configuration. The most important parameters for analog lines are:

```
base_exten          4000
fxs_immediate       no
fxs_default_start   ks
lc_country          br
context_lines       from-pstn
context_phones      from-internal
context_input       astbank-input
context_output      astbank-output
group_phones        0
group_lines         5
#echo_can           hpec
#echo_can           oslec
echo_can            MG2
```

चेतावनी: चैनलों के लिए कम से कम इको कैंसलेशन एल्गोरिद्म को कॉन्फ़िगर करना आवश्यक है। `base_exten` पैरामीटर FXS एक्सटेंशन के लिए बुनियादी डायल प्लान को परिभाषित करता है। इस मामले में, पहला FXS चैनल एक्सटेंशन नंबर 4000 प्राप्त करेगा, दूसरा 4001, और इसी प्रकार आगे। उन लाइनों (`context_phones`) और ट्रंकों (`context_lines`) के संदर्भ का निर्माण बहुत महत्वपूर्ण है। फ़ाइलें जनरेट करने के बाद, आपको फ़ाइल `/etc/asterisk/dahdi-channels.conf` को फ़ाइल `/etc/asterisk/chan_dahdi.conf` में शामिल करना चाहिए:

```
#include dahdi-channels.conf
```

Note: Analog signaling is a bit confusing; it is always the inverse of the card. FXS cards are signaled with FXO whereas FXO cards are signaled with FXS. Asterisk talks to these devices as if it was on the opposite side.

##### Step 3: Load kernel drivers

Now you have to load the chan_dahdi module and the related card kernel driver. Use dahdi_hardware to detect your card and the driver name. For example:

| Card | Driver | Description |
| --- | --- | --- |
| TE410P | wct4xxp | 4xE1/T1 - 3.3V PCI |
| TE405P | wct4xxp | 4xE1/T1 - 5V PCI |
| TDM400P | wctdm | 4 FXS/FXO |
| T100P | wct1xxp | 1 T1 |
| E100P | wct1xxp | 1 E1 |
| X100P | wcfxo | 1 FXO |

Commands to load the drivers:

```
modprobe dahdi
modprobe wctdm
```

##### चरण 4: dahdi_test उपयोगिता का उपयोग करें

एक महत्वपूर्ण उपयोगिता dahdi_test है, जिसका उपयोग DAHDI कार्ड में इंटरप्ट मिसेज़ की जाँच के लिए किया जाता है। ऑडियो गुणवत्ता समस्याएँ अक्सर इंटरप्ट टकराव से जुड़ी होती हैं। यह सत्यापित करने के लिए कि आपका DAHDI कार्ड अन्य कार्डों के साथ इंटरप्ट साझा नहीं कर रहा है, निम्नलिखित कमांड का उपयोग करें:

```
#cat /proc/interrupts
```

आप `dahdi_test` यूटिलिटी का उपयोग करके, जो DAHDI कार्डों के साथ संकलित है, इंटरप्ट मिस की संख्या की जाँच कर सकते हैं। 99.987% से नीचे की संख्या संभावित समस्याओं का संकेत देती है।

##### चरण 5: ड्राइवर को कॉन्फ़िगर करने के लिए `dahdi_cfg` यूटिलिटी का उपयोग करें

DAHDI में ड्राइवर लोड करने की एक असामान्य प्रणाली है। पहले `/etc/dahdi/system.conf` को कॉन्फ़िगर करें, और फिर उन कॉन्फ़िगरेशनों को `dahdi_cfg` का उपयोग करके DAHDI ड्राइवर पर लागू करें। इस मामले में, `dahdi_cfg` का उपयोग FX इंटरफ़ेस के सिग्नलिंग को कॉन्फ़िगर करने के लिए किया जाता है। परिणाम देखने के लिए, आप कमांड में “-vvvvv” जोड़ सकते हैं ताकि विस्तृत आउटपुट प्राप्त हो।

```
#
/sbin/dahdi_cfg -vv
Dahdi Configuration
======================
Channel map:
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

यदि चैनल सफलतापूर्वक लोड हो गए हैं, तो आप ऊपर दिखाए गए उदाहरण के समान आउटपुट देखेंगे। उपयोगकर्ता अक्सर chan_dahdi.conf को चैनलों के बीच उल्टे सिग्नलिंग के साथ गलत तरीके से कॉन्फ़िगर कर देते हैं। यदि ऐसा होता है, तो आप नीचे दिखाए गए संदेश को देखेंगे:

```
DAHDI_CHANCONFIG failed on channel 1: Invalid argument (22)
Did you forget that FXS interfaces are configured with FXO signalling
and that FXO interfaces use FXS signalling?
```

After successfully configuring the hardware, you can proceed to Asterisk configuration.

##### Step 6: Configure the /etc/asterisk/chan_dahdi.conf file

It sounds strange, but after configuring the /etc/dahdi/system.conf, you configured the card itself. DAHDI can be used for other purposes, like routing and SS7. To use it with Asterisk, you must configure the Asterisk DAHDI channels. Every channel in Asterisk has to be defined; SIP/PJSIP channels are defined in pjsip.conf (note: chan_sip and sip.conf were removed in Asterisk 21) while TDM channels are defined in chan_dahdi.conf. This creates the logical TDM channels to be used in your dial plan.

```
signalling=fxs_ks;                  ; FXS signaling for the FXO interface
group=1;                            ; channel group
context=incoming;                   ; context
channel => 1;                       ; channel number
signalling=fxo_ks;                  ; FXO signaling for the FXS interface
group=2;                            ; channel group
context=extensions;                 ; context
channel => 2                        ; channel number
```

### Configuration options

Several options are available in the chan_dahdi.conf file. A description of all options would be boring and counterproductive; instead, we will focus on the main option groups available for easy understanding.

#### General options (channel independent)

These options work for any channel: context: Defines the incoming context.

```
context=default
```

channel: चैनल या चैनल रेंज को परिभाषित करता है। प्रत्येक चैनल परिभाषा उन विकल्पों को विरासत में लेगी जो घोषणा से पहले परिभाषित किए गए हैं। चैनलों की पहचान व्यक्तिगत रूप से या एक ही पंक्ति में कॉमा द्वारा अलग करके की जा सकती है। रेंज को “-” का उपयोग करके परिभाषित किया जा सकता है।

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: चैनल को एक समूह के रूप में संभालने की अनुमति देता है। यदि आप चैनल नंबर के बजाय समूह नंबर डायल करते हैं, तो पहला उपलब्ध चैनल उपयोग किया जाता है। यदि चैनल फोन हैं, तो जब आप समूह को कॉल करते हैं, सभी फोन एक साथ बजेंगे। कॉमा का उपयोग करके आप उसी चैनल के लिए एक से अधिक समूह निर्दिष्ट कर सकते हैं।

```
group=1
group=3,5
```

language: अंतर्राष्ट्रीयकरण को चालू करता है और एक भाषा को कॉन्फ़िगर करता है। यह सुविधा विशिष्ट भाषा के लिए सिस्टम संदेशों को कॉन्फ़िगर करेगी। अंग्रेज़ी एकमात्र भाषा है जिसमें मानक स्थापना के माध्यम से पूर्ण प्रॉम्प्ट उपलब्ध हैं। musiconhold: होल्ड पर संगीत वर्ग का चयन करता है।

#### कॉलर आईडी विकल्प

कॉलरआईडी विकल्प बहुत सारे हैं। कुछ को अक्षम किया जा सकता है, हालांकि अधिकांश डिफ़ॉल्ट रूप से सक्षम होते हैं। usecallerid: बाद के चैनलों के लिए कॉलरआईडी ट्रांसमिशन को सक्षम या अक्षम करता है (Yes/No)। नोट: यदि आपका सिस्टम उत्तर देने से पहले दो बार बजता है, तो इस सुविधा को अक्षम करने का प्रयास करें। यह तुरंत उत्तर देना चाहिए। hidecallerid: आउटगोइंग कॉलरआईडी को छिपाने की परिभाषा देता है (Yes/No)। callerid: विशिष्ट चैनल के लिए कॉलरआईडी स्ट्रिंग को कॉन्फ़िगर करता है। कॉलर को asreceived के साथ कॉन्फ़िगर किया जा सकता है। यह अधिकांशतः ट्रंक इंटरफ़ेस में इनकमिंग कॉलरआईडी को दर्शाने के लिए उपयोग किया जाता है।

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

callwaitingcallerid: कॉल वेटिंग के दौरान callerid का समर्थन करता है।  
usincomingcalleridondahditransfer: ट्रांसफ़र में इनकमिंग callerid का उपयोग करता है।

#### कॉल वेटिंग

Asterisk FXS चैनलों में कॉल वेटिंग का समर्थन करता है। यदि कोई एक्सटेंशन को कॉल करता है तो उपयोगकर्ता को एक वेटिंग टोन मिलेगा। कॉल वेटिंग को सक्षम करने के लिए:

```
callwaiting=yes
```

कॉल वेटिंग में कॉलरआईडी का समर्थन करने के लिए:

```
callwaitingcallerid=yes
```

#### ऑडियो क्वालिटी विकल्प

इको कैंसलेशन को समायोजित करना आधा तकनीकी, आधा कला है। ये विकल्प कुछ Asterisk पैरामीटर को समायोजित करते हैं जो DAHDI चैनलों में ऑडियो क्वालिटी को प्रभावित करते हैं। ये एनालॉग इंटरफेस में ऑडियो क्वालिटी को सुधारने में मदद कर सकते हैं।

#### fxotune यूटिलिटी

fxotune एक यूटिलिटी है जिसका उपयोग FXO मॉड्यूल के कुछ पैरामीटर को फाइन‑ट्यून करने के लिए किया जाता है। इस फाइन‑ट्यूनिंग की आवश्यकता हाइब्रिड द्वारा उत्पन्न इम्पीडेंस मिसमैच को समायोजित करने के लिए होती है। यूटिलिटी के तीन ऑपरेशन मोड हैं:

- Detection (-i): मौजूदा FXO चैनलों का पता लगाता है और उन्हें ठीक करता है तथा कॉन्फ़िगरेशन को सहेजता है

```
fxotune.conf
```

- Dump mode (-d): वेवफ़ॉर्म फ़ाइलें fxotune_dump.vals में उत्पन्न करता है
- Startup mode (-s): फ़ाइल fxotune.conf को पढ़ता है और इसे FXO मॉड्यूल्स पर लागू करता है

It is important to understand that you will have to insert the instruction fxotune –s in the system load before starting Asterisk:

```
#modprobe dahdi
#modprobe wctdm
#fxotune -s
```

### Echo cancellation

अधिकांश इको कैंसलेशन एल्गोरिदम प्राप्त सिग्नल की कई प्रतियों को उत्पन्न करके काम करते हैं, जिनमें से प्रत्येक को एक विशिष्ट समय अवधि के लिए विलंबित किया जाता है। फ़िल्टर की टैप्स की संख्या निर्धारित करती है कि इको विलंब का आकार कितना होना चाहिए जिसे रद्द करना है। इन विलंबित प्रतियों को फिर समायोजित किया जाता है और प्राप्त सिग्नल से घटाया जाता है। कुंजी यह है कि केवल विलंबित सिग्नल को समायोजित किया जाए ताकि इको को हटाया जा सके बिना बहुत अधिक CPU साइकिल उपयोग किए। उपयोगकर्ताओं के दृष्टिकोण से, एक उपयुक्त इको कैंसलेशन एल्गोरिदम चुनना महत्वपूर्ण है। डिफ़ॉल्ट MG2 है; हालांकि, दो अन्य विकल्प उपलब्ध हैं: Sangoma (पूर्व में Digium) का High Performance Echo Cancellation (HPEC) और David Rowe द्वारा विकसित ओपन-सोर्स इको कैंसलेशन (OSLEC)।

OSLEC (https://www.rowetel.com/?page_id=454) को Linux कर्नेल में मर्ज किया गया है — यह कर्नेल के `drivers/staging/echo` क्षेत्र में स्थित है — और DAHDI इसे विरुद्ध बनाया गया है बजाय एक अलग डाउनलोड प्रदान करने के। इको कैंसलेशन एल्गोरिदम बदलने के लिए, `echo_can` पैरामीटर को `/etc/dahdi/system.conf` में सेट करें। उदाहरण के लिए:

```
echo_can=oslec
```

The echo cancellation in Asterisk is controlled by three parameters in the file /etc/asterisk/chan-

```
dahdi.conf.
```

- **echocancel**: इको कैंसलेशन को निष्क्रिय या सक्रिय करता है। आपको इस सुविधा को सक्रिय रखना चाहिए। यह “yes” या टैप्स की संख्या स्वीकार करता है। (व्याख्या: इको कैंसलेशन कैसे काम करता है? अधिकांश इको कैंसलेशन एल्गोरिदम प्राप्त सिग्नल की कई प्रतियों को उत्पन्न करके कार्य करते हैं, प्रत्येक को छोटे अंतराल से विलंबित किया जाता है। इस छोटे प्रवाह को “tap” कहा जाता है। टैप्स की संख्या निर्धारित करती है कि इको विलंब को कितना रद्द किया जा सकता है। ये प्रतियां विलंबित, समायोजित और मूल सिग्नल से घटाई जाती हैं। कुंजी यह है कि विलंबित सिग्नल को ठीक उसी तरह समायोजित किया जाए जितना इको को हटाने के लिए आवश्यक हो।)
- **echocancelwhenbridged**: शुद्ध TDM कॉल के दौरान इको कैंसर को सक्रिय या निष्क्रिय करता है। यह आमतौर पर आवश्यक नहीं होता।
- **rxgain**: ऑडियो रिसेप्शन गेन को समायोजित करता है जिससे रिसेप्शन वॉल्यूम बढ़ाया या घटाया जा सके (-100% से 100% तक)।
- **txgain**: ऑडियो ट्रांसमिशन गेन को समायोजित करता है जिससे ट्रांसमिशन वॉल्यूम बढ़ाया या घटाया जा सके (-100% से 100% तक)।

उदाहरण के लिए:

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### बिलिंग विकल्प

These options change how call information is recorded in the call detail records (CDR) database. amaflags: Configures the AMA flags affecting the CDR categorization. It accepts the following values:

- billing
- documentation
- omit
- default

accountcode: Configures an account code for a specific channel. It can contain any alphanumeric value—usually the department or user name.

```
accountcode=finance
amaflags=billing
```

### कॉल प्रगति विकल्प

ये आइटम कॉल की प्रगति के बारे में जानकारी प्राप्त करने के लिए उपयोग किए जाते हैं। सार्वजनिक इंटरफ़ेस में, कॉल प्रगति का पता लगाना और यह निर्धारित करना उपयोगी हो सकता है कि कॉल का उत्तर दिया गया या व्यस्त था। व्यस्तता का पता लगाना अत्यधिक प्रयोगात्मक है और विशिष्ट पैरामीटरों द्वारा नियंत्रित होता है।

```
busydetect=yes
busycount=4
busypattern=500,500
callprogress=yes
progzone=br
```

ये पैरामीटर (ऊपर) यह निर्धारित करते हैं कि इंटरफ़ेस व्यस्त टोन का पता लगाने की कोशिश करेगा या नहीं, सफल पहचान के लिए कितने टोन उपयोग किए जाएंगे, और व्यस्त पैटर्न क्या है। व्यस्त पहचान काफी हद तक प्रयोगात्मक है, और कुछ अतिरिक्त पैरामीटर Makefile में बदले जा सकते हैं। कॉल के उत्तर का पता लगाने के लिए, जो सटीक बिलिंग के लिए आवश्यक है, सटीक उत्तर समय को संकेत करने के लिए ध्रुवीयता उलटाव का उपयोग किया जा सकता है। यह महत्वपूर्ण है यदि आप कॉल के लिए शुल्क लेना चाहते हैं या केवल तुलना के लिए सटीक बिलिंग चाहते हैं। आमतौर पर आपको इस सेवा का अनुरोध करने के लिए फोन कंपनी से संपर्क करना पड़ता है।

```
answeronpolarityswitch=yes
```

कुछ देशों में, कॉल को समाप्त करने का पता पोलैरिटी रिवर्सल का उपयोग करके भी लगाया जा सकता है।

```
hanguponpolarityswitch=yes
```

#### Options for phones

These options are used for phones connected to the FXS interfaces. All the functionalities delivered to analog phones connected directly to the DAHDI interfaces are controlled by Asterisk.

- **adsi** (Analog Display Services Interface): This is a set of telecom standards used by some telcos to offer services such as ticket buying.
- **cancallforward**: Enables or disables call forwarding (*72 to enable and *73 to disable).
- **calleridcallwaiting**: Enables callerid received during a call waiting indication (Yes/No).
- **immediate**: In immediate mode, instead of providing a dial tone, the channel jumps immediately to the "s" extension in the defined context. This is used to create hotlines.
- **threewaycalling**: Enables or disables three-way conferencing.
- **mailbox**: Warns the user about available voicemail messages. It can be an audible sign or a visual indicator (if the telephone supports this feature). The argument is the mailbox number.
- **callgroup**: Group phones to dial or to pick up.
- **pickupgroup**: Group of phones for call pickup.

### Useful DAHDI CLI commands

Once Asterisk is running with DAHDI channels loaded, you can inspect channel status from the Asterisk CLI. These commands remain current in Asterisk 22:

```
*CLI> dahdi show channels
*CLI> dahdi show channel 1
*CLI> module reload chan_dahdi.so
```

### DAHDI चैनल फ़ॉर्मेट

DAHDI चैनल डायल प्लान में निम्नलिखित फ़ॉर्मेट का उपयोग करते हैं:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

उदाहरण के लिए:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## डिजिटल चैनल (E1/T1/PRI / TDM)

Asterisk 22 के अनुसार, DAHDI और libpri पूरी तरह से समर्थित हैं, लेकिन TDM डिजिटल ट्रंक (E1/T1/ISDN PRI) को नई तैनाती में धीरे‑धीरे SIP ट्रंक द्वारा प्रतिस्थापित किया जा रहा है। यह अनुभाग पूरी तरह से लागू रहता है जहाँ TDM कनेक्टिविटी आवश्यक है; ग्रीनफ़ील्ड परिवेशों में, SIP ट्रंकिंग (Chapter 3) आमतौर पर टेलीफ़ोनी हार्डवेयर के बिना समान चैनल घनत्व प्रदान करती है।

डिजिटल चैनल बहुत सामान्य हैं, इसलिए यदि आप बड़े ग्राहकों पर ध्यान केंद्रित करना चाहते हैं तो आपको इन चैनलों को लागू करना सीखना होगा। जब चैनलों की संख्या अधिक हो—आमतौर पर 8 से अधिक—तो T1/E1/J1 जैसे डिजिटल इंटरफ़ेस का उपयोग करना काफी सामान्य है। T1 संयुक्त राज्य अमेरिका में बहुत सामान्य है, जबकि E1 यूरोप में और J1 जापान में सामान्य है। इन प्रकार के चैनल सर्किट की अच्छी घनत्व प्रदान करते हैं—प्रति T1 चैनल 24 और E1 चैनलों के लिए 30।

Latin America, China, और Africa में, चैनल‑संबंधित सिग्नलिंग (CAS) के एक प्रकार जिसे MFC/R2 कहा जाता है, का उपयोग आम है। यह अध्याय OpenR2 लाइब्रेरी का उपयोग करके MFC/R2 को लागू करने के तरीके की जाँच करेगा। US और Europe में, Integrated Services Digital Networks (ISDN) PRI सबसे आम सिग्नलिंग है। यह अध्याय ISDN Basic Rate Interface (BRI) पर भी चर्चा करेगा, जो यूरोप में मध्यम‑स्तर के अनुप्रयोगों में बहुत सामान्य है।

All examples in the book concentrate on DAHDI channels. Some cards are implemented using proprietary channels, so please check with your manufacturer for further details on how to configure your specific card.

### Objectives
उद्देश्य

इस अध्याय के अंत तक आप सक्षम होंगे:

- डिजिटल टेलीफ़ोनी में उपयोग किए जाने वाले मुख्य शब्दों को पहचानें
- CAS और CCS सिग्नलिंग में अंतर करें
- R2 और ISDN सिग्नलिंग में अंतर करें
- ISDN सिग्नलिंग के साथ इंटरफ़ेस कॉन्फ़िगर करें
- R2 सिग्नलिंग के साथ इंटरफ़ेस कॉन्फ़िगर करें

### E1/T1 डिजिटल लाइन्स

डिजिटल लाइन्स E1/T1 एक विकल्प हैं जब आपको बड़ी संख्या में चैनलों को लागू करने की आवश्यकता होती है। एक एकल E1 सर्किट 30 समकालिक कॉल्स को संभाल सकता है, और आपके पास डायरेक्ट इनवर्ड डायल (DID), कॉलर आईडी (कॉलर आइडेंटिफिकेशन), और उन्नत सिग्नलिंग जैसी सुविधाएँ हो सकती हैं। E1/T1 लाइन आपके कंपनी तक कई तरीकों से पहुँच सकती है, जैसे ट्विस्टेड पेयर, फाइबर, और माइक्रोवेव, यह आपके देश पर निर्भर करता है। डिजिटल लाइन्स UTP, फाइबर, या माइक्रोवेव का उपयोग करके आपकी कंपनी तक पहुँचाई जाती हैं। मॉडेम और मल्टीप्लेक्सर्स (MUX) का उपयोग भौतिक लाइन को डिलीवर करने के लिए किया जाता है। T1 लाइन का कनेक्शन हमेशा RJ45 कनेक्टर पर आधारित होता है। हालांकि, E1 लाइन्स को BNC का उपयोग करके भी प्रोविजन किया जा सकता है। यह बहुत महत्वपूर्ण है कि आप अग्रिम रूप से उस कनेक्टर के प्रकार को जानें जो आपको प्राप्त होगा, विशेष रूप से E1 लाइन्स में। आमतौर पर RJ45 तक का सभी उपकरण TELCO द्वारा प्रदान किया जाता है।

![E1/T1 सर्किट कैसे प्रोविजन किए जाते हैं: टेलको ट्रंक को UTP कॉपर (E1 के लिए HDSL मोडेम, या T1 के लिए डायरेक्ट कार्ड कनेक्शन) के माध्यम से, ऑप्टिकल फाइबर के माध्यम से ऑप्टिकल मल्टीप्लेक्सर के द्वारा, या माइक्रोवेव रेडियो लिंक के माध्यम से प्रदान कर सकता है.](../images/10-legacy-fig05.png)

![UTP या BNC? अधिकांश डिजिटल कार्ड RJ45 (UTP) कनेक्टर का उपयोग करते हैं, लेकिन कुछ E1 लाइनों को डुअल BNC कोएक्स पर डिलीवर किया जाता है, ऐसे में कोएक्सियल पेयर को कार्ड के RJ45 जैक के साथ अनुकूलित करने के लिए एक बैलून की आवश्यकता होती है.](../images/10-legacy-fig06.png)

#### आवाज़ को बिट्स में कैसे परिवर्तित किया जाता है?

एनालॉग सिग्नल को प्रति सेकंड 8,000 बार सैंपल किया जाता है ताकि एनालॉग आवाज़ का डिजिटल संस्करण बनाया जा सके। इस एन्कोडिंग को पल्स कोड मॉड्यूलेशन (PCM) कहा जाता है। संयुक्त राज्य अमेरिका और जापान में, सिग्नल को लॉ (Asterisk में इसे ulaw कहा जाता है) का उपयोग करके एन्कोड किया जाता है। बाकी दुनिया में, एन्कोडिंग alaw होती है।

![पल्स कोड मॉड्यूलेशन (PCM): 4 kHz एनालॉग आवाज़ सिग्नल को प्रति सेकंड 8,000 बार सैंपल किया जाता है (नायक्विस्ट) और इसे 64 Kbps डिजिटल बिट स्ट्रीम में कोड किया जाता है।](../images/10-legacy-fig07.png)

#### समय विभाजन मल्टीप्लेक्सिंग

Analog लाइनों का उपयोग तब समझ में आता है जब आपको केवल कुछ चैनलों की आवश्यकता हो। जब टाइम डिवीजन मल्टिप्लेक्सिंग (TDM) का उपयोग किया जाता है, तो एक ही डेटा कनेक्शन में कई चैनलों को समाहित किया जा सकता है। जब आपको बड़ी संख्या में सर्किट चाहिए होते हैं, तो फोन कंपनी आमतौर पर आपको एक डिजिटल ट्रंक प्रदान करती है, जो एक डेटा सर्किट है जिसमें आवाज़ को PCM का उपयोग करके डिजिटल फ़ॉर्मेट में परिवहन किया जाता है। प्रत्येक टाइमस्लॉट एकल आवाज़ चैनल को परिवहन करने के लिए 64 Kbps बैंडविड्थ का उपयोग करता है।

![E1 और T1 में टाइम-डिवीजन मल्टिप्लेक्सिंग: एक E1 फ्रेम 2048 Kbps पर 32 टाइमस्लॉट्स ले जाता है (फ़्रेम सिंक्रोनाइज़ेशन के लिए DS0 #0, सिग्नलिंग के लिए DS0 #16), जबकि एक T1 फ्रेम 1544 Kbps पर 24 टाइमस्लॉट्स ले जाता है, जिसमें सिंक्रोनाइज़ेशन के लिए एक बिट और सिग्नलिंग के लिए रोब्ड-बिट योजना का उपयोग किया जाता है.](../images/10-legacy-fig08.png)

US में सबसे आम डिजिटल ट्रंक T1 है, जिसमें 24 उपलब्ध लाइन्स होती हैं; यूरोप और लैटिन अमेरिका में, E1 ट्रंक्स में 30 लाइन्स होती हैं। कुछ कंपनियां कम चैनलों के साथ एक फ्रैक्शनल T1/E1 प्रदान करती हैं।  
Robbed bit signaling  
कभी‑कभी एक T1 ट्रंक रोब्ड बिट स्कीम का उपयोग करता है जहाँ एक बिट सिग्नलिंग के लिए उधार ली जाती है। T1 ट्रंक्स पर, डेटा/वॉइस चैनल प्रत्येक टाइमस्लॉट पर 56 Kbps की गति से प्रेषित किया जाता है। जैसा कि आप देख सकते हैं, जब आप रोब्ड बिट का उपयोग करते हैं, तो T1 सर्किट सिंक्रनाइज़ेशन और सिग्नलिंग के लिए दो स्लॉट नहीं खोता।

#### T1/E1 लाइन कोड

T1s और E1s वास्तव में डेटा सर्किट होते हैं और उनका एक डेटा कोडिंग होता है जो निर्धारित करता है कि बिट्स को कैसे व्याख्यायित किया जाता है। E1s के लिए, सबसे सामान्य लाइन कोड लेयर 1 के लिए HDB3 और लेयर 2 के लिए CCS है। यह जानने का सबसे आसान तरीका कि आपका डिजिटल ट्रंक कैसे कॉन्फ़िगर किया गया है, यह है कि आप TELCO से इस जानकारी के बारे में पूछें। आपको इस जानकारी की आवश्यकता होगी फ़ाइल **/etc/dahdi/system.conf** को कॉन्फ़िगर करने के लिए।

#### T1/E1 संकेतन

यह समझना महत्वपूर्ण है कि T1/E1 लाइनों को विभिन्न प्रकार के सिग्नलिंग का उपयोग करके प्रदान किया जा सकता है, जैसे:

- T1 के साथ robbed bit signaling
- T1 के साथ ISDN signaling
- E1 के साथ MFC/R2 (CAS - Channel Associated Signaling)
- E1 के साथ ISDN signaling

ISDN अक्सर यूरोप और यूएस में उपयोग किया जाता है। यह एक डिजिटल वॉइस नेटवर्क है, जिसे अंतर्राष्ट्रीय टेलीकॉम्यूनिकेशन्स यूनियन (ITU) ने 1984 में मानकीकृत किया था। ISDN दो प्रकार के चैनल प्रदान करता है:

- बेयर चैनल
  - वॉयस
  - डेटा
- डेटा चैनल
  - बैंड के बाहर सिग्नलिंग
  - LAPD सिग्नलिंग
  - Q.931

आमतौर पर, एक ISDN लाइन दो भौतिक माध्यमों का उपयोग करके प्रदान की जाती है:

- बेसिक रेट इंटरफ़ेस (BRI)
  - 2B+D के रूप में जाना जाता है
  - दो बेयरर (64K) चैनल और एक डेटा (16K) चैनल
  - 148Kbps के साथ तांबे की दो तारों की जोड़ी का उपयोग करता है।
- प्राइमरी रेट इंटरफ़ेस (PRI)
  - T1/E1 ट्रंक का उपयोग करके प्रदान किया जाता है
  - T1s के लिए 23B+D
  - E1s के लिए 30B+D

कभी‑कभी, E1 सर्किट्स एक CAS सिग्नलिंग स्कीम जिसका नाम MFC/R2 है, का उपयोग करते हैं, जिसे ITU ने Q.421/Q441 नामक मानक के रूप में परिभाषित किया है। यह अक्सर लैटिन अमेरिका और एशिया में पाया जाता है। इन देशों की कई टेलीफ़ोनी कंपनियां MFC/R2 के अनुकूलित संस्करणों का उपयोग करती हैं। इसलिए, इसे कार्य करने के लिए आपको सही देशीय विविधता जाननी होगी।

### ISDN BRI

Channels using ISDN BRI signalling are very popular in Europe. Most ISDN BRI cards for Asterisk supports an S/T interface with NT and TE capabilities. The TE (terminal) connection is the one used to connect to the TELCO or to other PBXs configured as network termination (NT). The NT is used to connect phones and PBXs configured as TE. ISDN BRI provides two data/voice channels and one signalling channel. ISDN BRI cards are available from several vendors of interface cards for Asterisk.

### Asterisk सर्वर के लिए टेलीफ़ोनी कार्ड चुनना

Asterisk के साथ संगत डिजिटल कार्डों के कई निर्माता हैं। कार्ड का चयन निम्नलिखित कारकों में से कुछ पर निर्भर करता है:

#### डेटा बस

आपके PC पर कई प्रकार के बस होते हैं। यह बहुत महत्वपूर्ण है कि आपके सर्वर के लिए सही कार्ड हो। निम्नलिखित अवलोकन सबसे अधिक उपयोग किए जाने वाले कार्डों को दर्शाता है:

- 32 बिट्स PCI 5V अधिकांश कंप्यूटरों में पाया जाता है, जिसमें डेस्कटॉप शामिल हैं
  - Sangoma (formerly Digium) TE405, TE407, TE205, TE207, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
  - Sangoma A101, A102, and A104
- 32/64 बिट्स PCI 3.3V, मूलतः सर्वरों में पाया जाता है
  - Sangoma (formerly Digium) TE410, TE412, TE210, TE212, TE120, TE122, B410, TDM2400, TDM800, TDM410, and TC400
- PCI Express डेस्कटॉप और सर्वरों पर पाया जाता है
  - Sangoma (formerly Digium) TE420, TE220, TE121, AEX2400, and AEX800
  - Sangoma A101, A102, and A104

These card families originated at Digium, which Sangoma acquired in 2018; they are now sold and supported under the Sangoma brand. Many of the older SKUs listed here have been discontinued, so confirm current model availability at www.sangoma.com before purchasing.

- MiniPCI एम्बेडेड सिस्टम पर पाया जाता है
  - OpenVOX A100M(FXO), B100M(ISDN BRI), B200M(ISDN BRI), और B400M(ISDN BRI)
- USB 2.0 अधिकांश आधुनिक PC में पाया जाता है। USB‑आधारित समाधान एनालॉग और डिजिटल चैनलों की बड़ी घनत्व की अनुमति देते हैं। यह बस 480 Mbps का समर्थन करती है, और प्रत्येक आवाज़ चैनल 64 Kbps लेता है। USB हब का उपयोग करने पर एक ही पोर्ट में हजार तक एनालॉग पोर्ट की घनत्व प्राप्त की जा सकती है।
  - Xorcom Astribank (FXS, FXO, E1-ISDN, E1-R2)
- Ethernet। Ethernet का सबसे बड़ा लाभ यह है कि कार्ड को एक से अधिक सर्वर से जोड़ा जा सकता है। हाई अवेलेबिलिटी समाधान आमतौर पर इन उपकरणों के मुख्य उपयोग होते हैं। इस समाधान की ताकत उन सर्वरों के उपयोग में है जिनमें खाली PCI स्लॉट नहीं होते या ब्लेड सर्वर होते हैं।
  - Redfone FoneBridge (अधिकतम चार E1 सर्किट)

### हार्डवेयर इको कैंसलेशन का उपयोग

हार्डवेयर इको कैंसलेशन होस्ट CPU पर लोड को कम करता है। एक से अधिक E1 इंटरफ़ेस वाले कार्डों के लिए, हार्डवेयर इको कैंसलेशन आपके प्रोसेसर को हल्का करने में मदद कर सकता है। OSLEC जैसे नए उन्नत सॉफ़्टवेयर इको कैंसलेशन टूल हार्डवेयर इको कैंसलेशन की आवश्यकता को कम कर रहे हैं। हार्डवेयर और सॉफ़्टवेयर इको कैंसलेशन के बीच चयन करते समय, आपको अपने सर्वर में उपलब्ध प्रोसेसिंग पावर और E1 सर्किटों की संख्या पर विचार करना चाहिए। एक इको कैंसलेशन प्रक्रिया OSLEC (Reference: Xorcom Ltd.) का उपयोग करते हुए 128 टैप्स की एम्प्लिट्यूड के साथ प्रति वॉइस चैनल अधिकतम नौ MIPS (मिलियन इंस्ट्रक्शन पर सेकंड) तक उपयोग कर सकती है। यदि आप प्रत्येक इंस्ट्रक्शन के लिए 1 CPU साइकिल मानते हैं (जो प्रोसेसर और सॉफ़्टवेयर इम्प्लीमेंटेशन पर निर्भर करता है और हमेशा सही नहीं होता), तो चार E1s के लिए यह लगभग 1.080 GHz के बराबर है।

#### संकेतन का प्रकार

Selecting the type of signaling (e.g., T1 CAS, T1 PRI, E1 CAS R2, or E1 CAS ISDN) is not an easy task. It really depends on what you have available in your area and at what price. Common Channel Signaling (CCS) is often better than channel associated signaling (CAS). However, it is often not available. In the US, you can usually choose, as most TELCOS offer T1 CAS for regular users and T1 PRI for advanced users (e.g., call centers). In Latin America, E1 CAS R2 is prevalent, but ISDN PRI is available in some cities.

![DAHDI सॉफ़्टवेयर आर्किटेक्चर: Asterisk `chan_dahdi` चैनल ड्राइवर से बात करता है, जो बदले में प्रोटोकॉल लाइब्रेरीज़ libpri (ISDN), libopenr2 (MFC/R2), और libss7 (SS7) को लोड करता है; ये `/dev/dahdi` इंटरफ़ेस, DAHDI कर्नेल ड्राइवर, और कार्ड-विशिष्ट इंटरफ़ेस कर्नेल ड्राइवर के ऊपर स्थित होते हैं।](../images/10-legacy-fig09.png)

R2 को लागू करना आवश्यक है ताकि OpenR2 (www.libopenr2.org) नामक लाइब्रेरी स्थापित की जा सके, जिसे Moises Silva ने विकसित किया है, और स्थापना से पहले Asterisk को पैच किया जा सके—एक सरल प्रक्रिया जो इस अध्याय में बाद में दिखाई गई है। यह लाइब्रेरी कई परीक्षणों को पास कर चुकी है और हमारे कई ग्राहकों के उत्पादन वातावरण में उपयोग में है। मेरे विचार में, यदि उपलब्ध हो तो ISDN हमेशा सबसे अच्छा विकल्प है। कुछ प्रदाता सिग्नलिंग सिस्टम 7 (SS7) तक पहुँच रख सकते हैं, जो फोन कंपनियों के बीच उपलब्ध एक CCS सिग्नलिंग है। SS7 के लिए स्वामित्व वाली और ओपन सोर्स दोनों समाधान उपलब्ध हैं। लाइब्रेरी libss7 का उपयोग Asterisk पर SS7 को समर्थन देने के लिए किया जाता है।

### Asterisk टेलीफोनी चैनल सेटअप

एक टेलीफ़ोनी इंटरफ़ेस कार्ड को कॉन्फ़िगर करना कई आवश्यक चरणों को शामिल करता है। इस अध्याय में, हम सबसे सामान्य तीन परिदृश्यों को दिखाएंगे:

- डिजिटल कनेक्शन ISDN PRI का उपयोग करके
- डिजिटल कनेक्शन ISDN BRI का उपयोग करके
- डिजिटल कनेक्शन MFC/R2 का उपयोग करके

There are two ways to configure DAHDI channels. The first one is to configure it manually with full control of all parameters. The second way is to use the utility dahdi_genconf to detect and configure the cards.

#### स्वचालित पहचान और कॉन्फ़िगरेशन

Thanks to the DAHDI development team, we now have automatic detection and configuration of the cards. Step 1: To generate the configuration automatically, use the utility dahdi_genconf, which will detect the card and generate the files /etc/dahdi/system.conf and dahdi-channels.conf.

```
dahdi_genconf
```

चरण 2: फ़ाइल chan_dahdi.conf की अंतिम पंक्ति में, फ़ाइल dahdi-channels.conf को शामिल करें

```
#include dahdi_channels.conf
```

Step 3: फ़ाइल modules में सभी अप्रयुक्त मॉड्यूलों पर टिप्पणी करें या बस उपयोग करें:

```
dahdi_genconf modules
```

#### मैन्युअल कॉन्फ़िगरेशन

एक और विकल्प है इंटरफ़ेस को मैन्युअल रूप से कॉन्फ़िगर करना। नीचे DAHDI चैनलों के लिए कॉन्फ़िगरेशन के कुछ उदाहरण दिए गए हैं।

##### Example #1 – दो T1/ E1 चैनल ISDN का उपयोग करके

आवश्यक चरण:

1. TE205P या TE210P इंस्टॉलेशन
2. `/etc/dahdi/system.conf` फ़ाइल कॉन्फ़िगरेशन
3. DAHDI ड्राइवर लोडिंग
4. `dahdi_test` यूटिलिटी
5. `dahdi_cfg` यूटिलिटी
6. `chan_dahdi.conf` फ़ाइल कॉन्फ़िगरेशन
7. Asterisk लोड और टेस्टिंग

Step 1: TE205P इंस्टॉलेशन। TE205P इंस्टॉल करने से पहले, TE205P और TE210P कार्डों के बीच अंतर को समझना महत्वपूर्ण है। TE210P कार्ड 64-बिट बस का उपयोग करता है जो लगभग केवल सर्वर के मदरबोर्ड में मिलने वाले 3.3 वोल्ट द्वारा पावर्ड होती है। यदि आप इस इंटरफ़ेस कार्ड को निर्दिष्ट करते हैं तो सावधान रहें; सुनिश्चित करें कि आपका हार्डवेयर 64-बिट, 3.3V बस को सपोर्ट करता है। TE205P कार्ड 5V PCI का उपयोग करता है, जो अक्सर डेस्कटॉप कंप्यूटरों में पाया जाता है। हमने इस उदाहरण के लिए दो स्पैन वाले TE205P इंटरफ़ेस कार्ड को चुना है क्योंकि इसे एक‑स्पैन कार्ड में घटाना या चार‑स्पैन कार्ड में विस्तारित करना आसान है। ये कार्ड अब Sangoma ब्रांड के तहत बेचे जाते हैं (पहले Digium)।

![A Sangoma/Digium TE205P dual-span E1/T1 card: the two RJ45 ports accept the digital trunks, and an on-board jumper (the E1/T1/J1 selector) sets the line standard.](../images/10-legacy-fig10.png)

```
Step 2: /etc/dahdi/system.conf configuration file
```

TDM डिजिटल कार्डों का कॉन्फ़िगरेशन उनके एनालॉग समकक्षों के कॉन्फ़िगरेशन से थोड़ा अलग होता है। सबसे पहले, हमें बोर्ड स्पैन्स को कॉन्फ़िगर करना होगा और फिर चैनलों को। स्पैन्स क्रमिक रूप से क्रमांकित होते हैं, जो कार्डों की पहचान क्रम पर निर्भर करता है। दूसरे शब्दों में, यदि आपके पास एक से अधिक इंटरफ़ेस कार्ड हैं, तो यह जानना कठिन हो जाता है कि कौन सा स्पैन किस कार्ड से संबंधित है। प्रत्येक स्पैन पर स्थापित हार्डवेयर को जांचने के लिए `dahdi_hardware` का उपयोग करें। उदाहरण #1 (2xT1 PRI)

```
span=1,1,0,esf,b8zs
span=2,0,0,esf,b8zs
bchan=1-23
dchan=24
bchan=25-47
dchan=48
defaultzone=us
loadzone=us
```

उदाहरण #2 (2xE1 PRI)

```
span=1,1,0,ccs,hdb3,crc4 # not always necessary, consult Telco.
span=2,0,0,ccs,hdb3,crc4
bchan=1-15, 17-31
dchan=16
bchan=33-47, 49-63
dchan=48
defaultzone=br
loadzone=br
```

उदाहरण #3 (4xBRI)

```
loadzone=de
defaultzone=de
span=1,1,0,ccs,ami
bchan=1,2
hardhdlc=3
span=2,0,0,ccs,ami
bchan=4,5
hardhdlc=6
span=3,0,0.ccs.ami
bchan=7,8
hardhdlc=9
span=4,0,0,ccs,ami
bchan=10,11
hardhdlc=12
```

चरण 3: कर्नेल ड्राइवर लोड करना जांचें कि आपको कौन सा ड्राइवर स्थापित करने की आवश्यकता है, इसे `dahdi_hardware` का उपयोग करके जांचें।

```
dahdi_hardware
pci:0000:04:02.0     wcte2xxp    e159:0001 Sangoma Wildcard TE205P T1/E1 Board
```

लोड करने के लिए उपयोग करें:

```
modprobe dahdi
modprobe wct2xxp
```

Step 4: Using dahdi_test, check the missing interrupts आप DAHDI कार्ड्स के साथ संकलित dahdi_test यूटिलिटी का उपयोग करके इंटररप्ट मिसेज़ की संख्या सत्यापित कर सकते हैं। 99.987% से कम संख्या संभावित समस्याओं का संकेत देती है। You will find dahdi_test in

```
/usr/sbin.
#./dahdi_test
Opened pseudo zap interface, measuring accuracy...
99.987793% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 100.000000% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000% 100.000000% 99.987793% 100.000000%
100.000000% 100.000000%
100.000000% 100.000000% 100.000000%
--- Results after 26 passes ---
Best: 100.000000 -- Worst: 99.987793 -- Average: 99.999061
```

चरण 5: dahdi_cfg यूटिलिटी का उपयोग  
यह एक फ्रैक्शनल E1 (15 पोर्ट) स्पैन और दो FXO पोर्ट्स के लिए dahdi_cfg का सही आउटपुट है।

```
#./dahdi_cfg -vvvv
Dahdi configuration
======================
SPAN 1: CCS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: Clear channel (Default) (Slaves: 01)
Channel 02: Clear channel (Default) (Slaves: 02)
Channel 03: Clear channel (Default) (Slaves: 03)
Channel 04: Clear channel (Default) (Slaves: 04)
Channel 05: Clear channel (Default) (Slaves: 05)
Channel 06: Clear channel (Default) (Slaves: 06)
Channel 07: Clear channel (Default) (Slaves: 07)
Channel 08: Clear channel (Default) (Slaves: 08)
Channel 09: Clear channel (Default) (Slaves: 09)
Channel 10: Clear channel (Default) (Slaves: 10)
Channel 11: Clear channel (Default) (Slaves: 11)
Channel 12: Clear channel (Default) (Slaves: 12)
Channel 13: Clear channel (Default) (Slaves: 13)
Channel 14: Clear channel (Default) (Slaves: 14)
Channel 15: Clear channel (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
16 channels configured.
```

चरण 6: DAHDI को फ़ाइल /etc/asterisk/chan_dahdi.conf में कॉन्फ़िगर करना उदाहरण #1 (2xT1)

```
callerid="John Doe"<(555)555-1111>
switchtype=national
signalling =pri_cpe
context=from-pstn
group = 1
channel => 1-23
group =2
channel => 25-47
```

# उदाहरण #2 (2xE1)

```
callerid="Flavio Eduardo" <4830258580>
switchtype=euroisdn
signalling = pri_cpe
group = 1
channel => 1-15;17-31
group =2
channel => 32-46;48-62
```

उदाहरण #3 (4xBRI)

```
signaling=bri_cpe
switchtype=euroisdn
group=1
context=from-pstn
channel=>1,2,4,5,7,8,10,11
```

Use signaling=bri_cpe_ptmp for point to multipoint BRI. Currently, BRI point to multipoint is not supported in NT mode.

#### Loading the kernel drivers

After configuring the drivers, you may simply restart the server. If you have installed DAHDI with make config, you won’t need to do anything extra. The kernel driver will be automatically loaded and configured. However, sometimes it is useful to load and unload the drivers manually. Example:

```
modprobe wct11xp
dahdi_cfg -vvvvv
```

The first command loads the driver and the second, dahdi_cfg, applies the configuration to the kernel driver.

### समस्या निवारण

Sometimes things don’t work the first time. Let’s check some resources for troubleshooting DAHDI. Step 1: Check if the card is being recognized by the operation system. Sangoma/Digium cards are usually recognized as the ISDN modem.

```
lspci -v
00:00.0 Host bridge: Intel Corporation E7230/3000/3010 Memory Controller Hub
00:01.0 PCI bridge: Intel Corporation E7230/3000/3010 PCI Express Root Port
00:1c.0 PCI bridge: Intel Corporation 82801G (ICH7 Family) PCI Express Port 1 (rev 01)
00:1c.4 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 5 (rev
01)
00:1c.5 PCI bridge: Intel Corporation 82801GR/GH/GHM (ICH7 Family) PCI Express Port 6 (rev
01)
00:1d.0 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #1 (rev
01)
00:1d.1 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #2 (rev
01)
00:1d.2 USB Controller: Intel Corporation 82801G (ICH7 Family) USB UHCI Controller #3 (rev
01)
00:1d.7 USB Controller: Intel Corporation 82801G (ICH7 Family) USB2 EHCI Controller (rev 01)
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev e1)
00:1f.0 ISA bridge: Intel Corporation 82801GB/GR (ICH7 Family) LPC Interface Bridge (rev 01)
00:1f.1 IDE interface: Intel Corporation 82801G (ICH7 Family) IDE Controller (rev 01)
00:1f.2 IDE interface: Intel Corporation 82801GB/GR/GH (ICH7 Family) SATA IDE Controller (rev
01)
00:1f.3 SMBus: Intel Corporation 82801G (ICH7 Family) SMBus Controller (rev 01)
01:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
01:00.1 PIC: Intel Corporation 6700/6702PXH I/OxAPIC Interrupt Controller A (rev 09)
02:08.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068 PCI-X Fusion-MPT SAS (rev
01)
03:00.0 PCI bridge: Intel Corporation 6702PXH PCI Express-to-PCI Bridge A (rev 09)
04:02.0 Network controller: Tiger Jet Network Inc. Tiger3XX Modem/ISDN interface
05:00.0 Ethernet controller: Broadcom Corporation NetXtreme BCM5721 Gig. Eth.PCI Express (rev
11)
07:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. RTL-8139/8139C/8139C+ (rev 10)
07:05.0 VGA compatible controller: ATI Technologies Inc ES1000 (rev 02)
```

चरण 2: जांचें कि कर्नेल ड्राइवर सही ढंग से लोड हो रहा है या नहीं, इसका उपयोग करके:

```
modprobe wct11xp
dmesg
TE110P: Setting up global serial parameters for E1 FALC V1.2
TE110P: Successfully initialized serial bus for card
TE110P: Span configured for CAS/HDB3
Calling startup (flags is 4099)
Found a Wildcard: Sangoma Wildcard TE110P T1/E1
TE110P: Span configured for CCS/HDB3/CRC4
Calling startup (flags is 4099)
dahdi: Registered tone zone 0 (United States / North America)
wcte1xxp: Setting yellow alarm
```

Step 3: कनेक्शन की फिजिकल लेयर से संबंधित अलार्म की स्थिति सत्यापित करें। E1 कनेक्शन की फिजिकल लेयर को सत्यापित करने के लिए, आप निम्नलिखित Asterisk CLI कमांड का उपयोग कर सकते हैं।

```
dahdi show status
```

अलार्म पोर्ट में समस्याओं को दर्शाते हैं: रेड अलार्म: रिमोट स्विच के साथ सिंक्रनाइज़ेशन बनाए नहीं रख सकता। यह आमतौर पर एक भौतिक समस्या होती है, जैसे लाइन कोड या फ्रेमिंग में असंगति। येलो अलार्म: संकेत देता है कि रिमोट स्विच रेड अलार्म में है। यह दर्शाता है कि रिमोट स्विच आपके ट्रांसमिशन प्राप्त नहीं कर रहा है। ब्लू अलार्म: सभी टाइमस्लॉट्स पर सभी अनफ़्रेम्ड 1s प्राप्त करता है; dahdi_tool वर्तमान में ब्लू अलार्म का पता नहीं लगा पाता। लूपबैक: पोर्ट स्थानीय या रिमोट लूपबैक में है।

```
vtsvoffice*CLI> dahdi show status
Description                              Alarms     IRQ        bpviol     CRC4
Sangoma Wildcard E100P E1/PRA Card 0      OK         0          0          0
Wildcard X100P Board 1                   OK         0          0          0
Wildcard X100P Board 2                   RED        0          0          0
```

चरण 4: DAHDI के साथ Asterisk सर्वर पर समस्याओं का पता लगाने के लिए, पहले यह जांचें कि चैनल पहचान रहे हैं या नहीं, इसका उपयोग करके:

```
dahdi show channels
pabxip01*CLI> dahdi show channels
   Chan Extension  Context         Language   MOH Interpret
 pseudo            default                    default
      1            from-pstn                  default
      2            from-pstn                  default
      3            from-pstn                  default
      4            from-pstn                  default
      5            from-pstn                  default
      6            from-pstn                  default
      7            from-pstn                  default
      8            from-pstn                  default
      9            from-pstn                  default
     10            from-pstn                  default
     11            from-pstn                  default
     12            from-pstn                  default
     13            from-pstn                  default
     14            from-pstn                  default
     15            from-pstn                  default
     17            from-pstn                  default
     18            from-pstn                  default
     19            from-pstn                  default
     20            from-pstn                  default
     21            from-pstn                  default
     22            from-pstn                  default
     23            from-pstn                  default
     24            from-pstn                  default
     25            from-pstn                  default
     26            from-pstn                  default
     27            from-pstn                  default
     28            from-pstn                  default
     29            from-pstn                  default
     30 2171       from-pstn                  default
     31 2171       from-pstn                  default
```

Step 5: ISDN लेयर 3 की स्थिति जाँचें, जिसे q.931 भी कहा जाता है। आप यह जांच सकते हैं कि ISDN लेयर 3 सक्रिय है या नहीं, उपयोग करके: `pri show spans` (सभी स्पैन की सूची के लिए) या `pri show span <n>` किसी विशिष्ट स्पैन के लिए:

```
vtsvoffice*CLI> pri show span 1
Primary D-channel: 16
Status: Provisioned, Up, Active
Switchtype: EuroISDN
Type: CPE
Window Length: 0/7
Sentrej: 0
SolicitFbit: 0
Retrans: 0
Busy: 0
Overlap Dial: 0
T200 Timer: 1000
T203 Timer: 10000
T305 Timer: 30000
T308 Timer: 4000
T313 Timer: 4000
N200 Counter: 3
```

Use `pri show spans` (बहुवचन) का उपयोग करके सभी कॉन्फ़िगर किए गए PRI स्पैन्स की स्थिति एक साथ सूचीबद्ध करें।

एक विशिष्ट चैनल जांचें। dahdi show channel x:

```
vtsvoffice*CLI> dahdi show channel 1
Channel: 1
File Descriptor: 21
Span: 1
Extension:
Dialing: no
Context: entrada
Caller ID: 4832341689
Calling TON: 33
Caller ID name:
Destroy: 0
InAlarm: 0
Signalling Type: PRI Signalling
Radio: 0
Owner: <None>
Real: <None>
Callwait: <None>
Threeway: <None>
Confno: -1
Propagated Conference: -1
Real in conference: 0
DSP: no
Relax DTMF: no
Dialing/CallwaitCAS: 0/0
Default law: alaw
```

debug pri span x: यदि सब कुछ करने के बाद भी आपको समस्याएँ आती हैं, तो pri span को डिबग करना शुरू करें। यह कमांड ISDN कॉल्स का विस्तृत डिबगिंग सक्षम करती है। यह एक महत्वपूर्ण कमांड है जब आपको लगता है कि कुछ सही नहीं है। आप गलत डायल किए गए अंकों और अन्य समस्याओं का पता लगा सकते हैं। नीचे हम सफल कॉल के डिबगिंग आउटपुट का उदाहरण प्रस्तुत करते हैं। यदि आपको असफल कॉल की तुलना बिना समस्याओं वाली कॉल से करनी है तो इस उदाहरण को देखें। एक टिप यह है कि core set verbose=0 का उपयोग करके केवल ISDN q.931 संदेश प्राप्त करें।

```
-- Making new call for cr 32833
> Protocol Discriminator: Q.931 (8)  len=57
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: SETUP (5)
> [04 03 80 90 a3]
> Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
>                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
>                              Ext: 1  User information layer 1: A-Law (35)
> [18 03 a9 83 81]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 1 ]
> [28 0e 46 6c 61 76 69 6f 20 45 64 75 61 72 64 6f]
> Display (len=14) @h@>[ Flavio Eduardo ]
> [6c 0c 21 80 34 38 33 30 32 35 38 35 39 30]
> Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
>                           Presentation: Presentation permitted, user number not screened
(0) '4830258590' ]
> [70 09 a1 33 32 32 34 38 35 38 30]
> Called Number (len=11) [ Ext: 1  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '32248580' ]
> [a1]
> Sending Complete (len= 1)
< Protocol Discriminator: Q.931 (8)  len=10
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CALL PROCEEDING (2)
< [18 03 a9 83 81]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 1 ]
-- Processing IE 24 (cs0, Channel Identification)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: ALERTING (1)
< [1e 02 84 88]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Inband information or
appropriate pattern now available. (8) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=64
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: SETUP (5)
< [04 03 80 90 a3]
< Bearer Capability (len= 5) [ Ext: 1  Q.931 Std: 0  Info transfer capability: Speech (0)
<                              Ext: 1  Trans mode/rate: 64kbps, circuit-mode (16)
<                              Ext: 1  User information layer 1: A-Law (35)
< [18 03 a1 83 82]
< Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Preferred Dchan: 0
<                        ChanSel: Reserved
<                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
<                       Ext: 1  Channel: 2 ]
< [1c 15 91 a1 12 02 01 bc 02 01 0f 30 0a 02 01 01 0a 01 00 a1 02 82 00]
< Facility (len=23, codeset=0) [ 0x91, 0xa1, 0x12, 0x02, 0x01, 0xbc, 0x02, 0x01, 0x0f, '0',
0x0a, 0x02, 0x01, 0x01, 0x0a, 0x01, 0x00, 0xa1, 0x02, 0x82, 0x00 ]
< [1e 02 82 83]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the local user (2)
<                               Ext: 1  Progress Description: Calling equipment is non-ISDN.
(3) ]
< [6c 0c 21 83 34 38 33 32 32 34 38 35 38 30]
< Calling Number (len=14) [ Ext: 0  TON: National Number (2)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1)
<                           Presentation: Presentation allowed of network provided number (3)
'4832248580' ]
< [70 05 c1 38 35 38 30]
< Called Number (len= 7) [ Ext: 1  TON: Subscriber Number (4)  NPI: ISDN/Telephony Numbering
Plan (E.164/E.163) (1) '8580' ]
< [a1]
< Sending Complete (len= 1)
-- Making new call for cr 5720
-- Processing Q.931 Call Setup
-- Processing IE 4 (cs0, Bearer Capability)
-- Processing IE 24 (cs0, Channel Identification)
-- Processing IE 28 (cs0, Facility)
Handle Q.932 ROSE Invoke component
-- Processing IE 30 (cs0, Progress Indicator)
-- Processing IE 108 (cs0, Calling Party Number)
-- Processing IE 112 (cs0, Called Party Number)
-- Processing IE 161 (cs0, Sending Complete)
> Protocol Discriminator: Q.931 (8)  len=10
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CALL PROCEEDING (2)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> Protocol Discriminator: Q.931 (8)  len=14
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: CONNECT (7)
> [18 03 a9 83 82]
> Channel ID (len= 5) [ Ext: 1  IntID: Implicit, PRI Spare: 0, Exclusive Dchan: 0
>                        ChanSel: Reserved
>                       Ext: 1  Coding: 0   Number Specified   Channel Type: 3
>                       Ext: 1  Channel: 2 ]
> [1e 02 81 82]
> Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Private network serving the local user (1)
>                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: CONNECT ACKNOWLEDGE (15)
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: PROGRESS (3)
< [1e 02 84 82]
< Progress Indicator (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location:
Public network serving the remote user (4)
<                               Ext: 1  Progress Description: Called equipment is non-ISDN.
(2) ]
-- Processing IE 30 (cs0, Progress Indicator)
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: CONNECT (7)
> Protocol Discriminator: Q.931 (8)  len=5
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: CONNECT ACKNOWLEDGE (15)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Active, peerstate Connect Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: DISCONNECT (69)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 65/0x41) (Terminator)
< Message type: RELEASE (77)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Release Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 65/0x41) (Originator)
> Message type: RELEASE COMPLETE (90)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
< Protocol Discriminator: Q.931 (8)  len=9
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: DISCONNECT (69)
< [08 02 82 90]
< Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Public network
serving the local user (2)
<                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
-- Processing IE 8 (cs0, Cause)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Disconnect Indication, peerstate Disconnect
Request
> Protocol Discriminator: Q.931 (8)  len=9
> Call Ref: len= 2 (reference 5720/0x1658) (Terminator)
> Message type: RELEASE (77)
> [08 02 81 90]
> Cause (len= 4) [ Ext: 1  Coding: CCITT (ITU) standard (0) 0: 0   Location: Private network
serving the local user (1)
>                  Ext: 1  Cause: Unknown (16), class = Normal Event (1) ]
< Protocol Discriminator: Q.931 (8)  len=5
< Call Ref: len= 2 (reference 5720/0x1658) (Originator)
< Message type: RELEASE COMPLETE (90)
NEW_HANGUP DEBUG: Calling q931_hangup, ourstate Null, peerstate Null
NEW_HANGUP DEBUG: Destroying the call, ourstate Null, peerstate Null
```

### Configuration options in chan_dahdi.conf

फ़ाइल chan_dahdi.conf में कई विकल्प उपलब्ध हैं। सभी विकल्पों का विवरण देना उबाऊ और प्रतिकूल होगा। यहाँ, हम बेहतर समझ प्रदान करने के लिए उपलब्ध मुख्य विकल्प समूहों को विस्तार से बताएँगे।

#### General options (channel independent)

context: आने वाले कॉन्टेक्स्ट को परिभाषित करता है।

```
context=default
```

channel: चैनल या चैनल रेंज को परिभाषित करता है। प्रत्येक चैनल परिभाषा घोषणा से पहले परिभाषित विकल्पों को विरासत में लेगी। चैनलों को व्यक्तिगत रूप से या कॉमा विभाजन के साथ एक ही पंक्ति में पहचाना जा सकता है। रेंज को “-” का उपयोग करके परिभाषित किया जा सकता है।

```
Channel=>1-15
Channel=>16
Channel=>17,18
```

group: चैनलों को एक समूह के रूप में माना जा सकता है। यदि आप चैनल नंबर के बजाय समूह नंबर डायल करते हैं, तो पहला उपलब्ध चैनल उपयोग किया जाता है। यदि चैनल फोन हैं, तो समूह को कॉल करने पर सभी फोन एक साथ बजेंगे। कॉमा का उपयोग करके, आप एक ही चैनल के लिए एक से अधिक समूह निर्दिष्ट कर सकते हैं।

```
group=1
group=3,5
```

language: अंतर्राष्ट्रीयकरण को चालू करता है और एक भाषा को कॉन्फ़िगर करता है। यह सुविधा सिस्टम संदेशों को किसी विशिष्ट भाषा के लिए कॉन्फ़िगर करेगी। अंग्रेज़ी ही एकमात्र भाषा है जिसमें मानक इंस्टॉलेशन से पूर्ण प्रॉम्प्ट उपलब्ध हैं। musiconhold: संगीत ऑन होल्ड क्लास चुनें।

#### ISDN विकल्प

switchtype: PBX या स्विच पर निर्भर करता है। यूरोप और लैटिन अमेरिका में, EuroISDN सामान्य है।

- 5ess: Lucent 5ESS
- euroisdn: EuroISDN
- national: National ISDN
- dms100: Nortel DMS100
- 4ess: AT&T 4ESS
- Qsig: Q.SIG

```
switchtype = EuroISDN
```

pridialplan: कुछ स्विचों के लिए आवश्यक है जिन्हें डायल प्लान विनिर्देशन की आवश्यकता होती है। यह विकल्प कई स्विचों द्वारा अनदेखा किया जाता है। वैध विकल्प हैं private, national, international, और unknown.

```
pridialplan = unknown
```

prilocaldialplan: कुछ स्विचों के लिए आवश्यक, आमतौर पर अज्ञात।

```
prilocaldialplan = unknown
```

overlapdial: Overlap dialing का उपयोग तब किया जाता है जब आप कनेक्शन स्थापित होने के बाद अंक पास करते हैं। आप ब्लॉक मोड नंबरिंग (overlapdial=no) या डिजिट मोड (overlapdial=yes) का उपयोग कर सकते हैं। ब्लॉक मोड अक्सर ऑपरेटरों द्वारा उपयोग किया जाता है।  
signaling: Subsequent चैनलों के लिए signaling प्रकार को कॉन्फ़िगर करता है। ये पैरामीटर chan_dahdi.conf फ़ाइल में मौजूद मानों के अनुरूप होने चाहिए। सही विकल्प उपलब्ध चैनल पर निर्भर करते हैं। ISDN के लिए आप पाँच विकल्प चुन सकते हैं:

- pri_cpe: जब डिवाइस CPE हो, कभी‑कभी इसे क्लाइंट, यूज़र, या स्लेव कहा जाता है। यह सबसे सरल और सबसे अधिक उपयोग किया जाने वाला signaling रूप है। कभी‑कभी, जब आप किसी प्राइवेट PBX से कनेक्ट करने की कोशिश करते हैं, तो PBX भी CPE के रूप में कॉन्फ़िगर किया गया होता है। इस स्थिति में, Asterisk में pri_net signaling का उपयोग करें।  
- pri_net: जब Asterisk किसी प्राइवेट PBX से जुड़ा हो जो CPE के रूप में कॉन्फ़िगर किया गया हो। इस signaling को अक्सर होस्ट, मास्टर, या नेटवर्क कहा जाता है।  
- bri_cpe: जब Asterisk ISDN BRI ट्रंक के लिए CPE के रूप में जुड़ा हो।  
- bri_net: जब Asterisk ISDN फ़ोन या PBX से जुड़ा हो जो टर्मिनल (TE) के रूप में कॉन्फ़िगर किया गया हो।  
- bri_cpe_ptmp: bri_cpe जैसा ही, लेकिन पॉइंट‑टू‑मल्टीपॉइंट आर्किटेक्चर में।

#### CallerID options

कई Caller ID विकल्प उपलब्ध हैं। कुछ को निष्क्रिय किया जा सकता है, हालांकि अधिकांश डिफ़ॉल्ट रूप से सक्षम होते हैं।  
usecallerid: Subsequent चैनलों के लिए Caller ID ट्रांसमिशन को सक्षम या निष्क्रिय करता है (Yes/No)। नोट: यदि आपके सिस्टम को उत्तर देने से पहले दो रिंग चाहिए, तो इस फीचर को निष्क्रिय करने का प्रयास करें ताकि यह तुरंत उत्तर दे सके।  
hidecallerid: Caller ID को छुपाता है (Yes/No)।  
calleridcallwaiting: कॉल वेटिंग संकेत के दौरान Caller ID प्राप्त करने को सक्षम करता है (Yes/No)।  
callerid: किसी विशिष्ट चैनल के लिए Caller ID स्ट्रिंग को कॉन्फ़िगर करता है। कॉलर को trunk interfaces में “asreceived” के साथ कॉन्फ़िगर किया जा सकता है ताकि Caller ID आगे पास हो सके।

```
callerid = "Flavio Eduardo Gonçalves" <48 30258500>
```

**ध्यान दें:** अधिकांश टेलकोज यह अनिवार्य करते हैं कि आप अपना सही कॉलर आईडी कॉन्फ़िगर करें। यदि आप सही कॉलर आईडी पास नहीं करते हैं, तो आपको टेलको के माध्यम से डायल आउट करने की अनुमति नहीं मिलनी चाहिए। दूसरी ओर, कॉलर आईडी कॉन्फ़िगर किए बिना भी आप कॉल प्राप्त कर पाएँगे।

#### ऑडियो क्वालिटी विकल्प

ये विकल्प कुछ Asterisk पैरामीटर को समायोजित करते हैं जो DAHDI चैनलों में ऑडियो क्वालिटी को प्रभावित करते हैं।

- **echocancel**: इको कैंसलेशन को निष्क्रिय या सक्रिय करें। आपको इस सुविधा को सक्रिय रखना चाहिए। यह "yes" या टैप्स की संख्या स्वीकार करता है। (व्याख्या: इको कैंसलेशन कैसे काम करता है? अधिकांश इको कैंसलेशन एल्गोरिदम प्राप्त सिग्नल की कई प्रतियों को उत्पन्न करके कार्य करते हैं, जहाँ प्रत्येक को एक छोटे अंतराल से विलंबित किया जाता है। इस छोटे प्रवाह को "tap" कहा जाता है। टैप्स की संख्या निर्धारित करती है कि इको विलंब को कितना रद्द किया जा सकता है। ये प्रतियां विलंबित, समायोजित और मूल सिग्नल से घटाई जाती हैं। चाल यह है कि विलंबित सिग्नल को ठीक उसी तरह समायोजित किया जाए जितना आवश्यक हो इको को हटाने के लिए।)
- **echocancelwhenbridged**: शुद्ध TDM कॉल के दौरान इको कैंसर को सक्षम या अक्षम करता है। यह आमतौर पर आवश्यक नहीं होता।
- **rxgain**: ऑडियो रिसेप्शन गेन को समायोजित करता है जिससे रिसेप्शन वॉल्यूम बढ़ाया या घटाया जा सके (-100% से 100% तक)।
- **txgain**: ऑडियो ट्रांसमिशन गेन को समायोजित करता है जिससे ट्रांसमिशन वॉल्यूम बढ़ाया या घटाया जा सके (-100% से 100% तक)।

```
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

#### बिलिंग विकल्प

ये विकल्प कॉल विवरण रिकॉर्ड (CDR) डेटाबेस में कॉल जानकारी रिकॉर्ड होने के तरीके को बदलते हैं। amaflags: CDR की वर्गीकरण को प्रभावित करता है। यह निम्न मानों को स्वीकार करता है:

- billing
- documentation
- omit
- default

accountcode: यह एक विशिष्ट चैनल के लिए अकाउंट कोड कॉन्फ़िगर करता है। यह कोई भी अल्फ़ान्यूमेरिक मान रख सकता है, आमतौर पर विभाग या उपयोगकर्ता का नाम।

```
accountcode=finance
amaflags=billing
```

### MFC/R2 कॉन्फ़िगरेशन

MFC/R2 कई लैटिन अमेरिकी, चीन, और अफ्रीका के देशों में तथा कुछ यूरोपीय देशों में उपयोग किया जाता है। ISDN श्रेष्ठ है और यदि आपके क्षेत्र में उपलब्ध हो तो प्राथमिकता दी जाती है।

#### समस्या को समझना

कार्ड जिसका उपयोग MFC/R2 को संकेत देने के लिए किया जाता है, वही कार्ड ISDN को संकेत देने के लिए भी उपयोग किया जाता है। यह संभव है कि DAHDI चैनलों पर MFC/R2 का उपयोग libopenR2 (www.libopenr2.com) नामक लाइब्रेरी के माध्यम से किया जाए। यह लाइब्रेरी Asterisk के 1.6.2 से पहले के संस्करणों में शामिल नहीं थी।

##### MFC/R2 प्रोटोकॉल को समझना

MFC/R2 प्रोटोकॉल इन-बैंड और आउट-ऑफ़-बैंड सिग्नलिंग को मिलाता है। पता सिग्नलिंग इन-बैंड एक सेट टोन का उपयोग करके अग्रेषित की जाती है जबकि चैनल जानकारी टाइमस्लॉट 16 के माध्यम से आउट-ऑफ़-बैंड सिग्नलिंग के रूप में प्रेषित की जाती है।

**Line Signaling (ITU-T Q.421).** टाइमस्लॉट 16 में, प्रत्येक वॉइस चैनल अपनी स्थितियों और कॉल नियंत्रण को संकेत करने के लिए चार ABCD बिट्स का उपयोग करता है। बिट्स C और D का बहुत कम उपयोग होता है। कुछ देशों में, इन्हें मीटरिंग (बिलिंग के लिए पल्स मीटरिंग) के लिए इस्तेमाल किया जा सकता है। एक सामान्य बातचीत में, दोनों पक्ष सक्रिय होते हैं: कॉल करने वाला और कॉल प्राप्त करने वाला पक्ष। कॉल करने वाले पक्ष से संकेत को फॉरवर्ड सिग्नलिंग कहा जाता है जबकि कॉल प्राप्त करने वाले पक्ष से संकेत को बैकवर्ड सिग्नलिंग कहा जाता है। हम फॉरवर्ड सिग्नलिंग के लिए Af और Bf तथा बैकवर्ड सिग्नलिंग के लिए Ab और Bb निर्दिष्ट करेंगे।

| State | ABCD forward | ABCD backward |
| --- | --- | --- |
| Idle/Released | 1001 | 1001 |
| Seized | 0001 | 1001 |
| Seize Ack | 0001 | 1101 |
| Answered | 0001 | 0105 |
| ClearBack | 0001 | 1101 |
| ClearFwd (before clear-back) | 1001 | 0101 |
| ClearFwd (disconnection confirmation) | 1001 | 1001 |
| Blocked | 1001 | 1101 |

MFC/R2 को ITU द्वारा परिभाषित किया गया था। दुर्भाग्यवश, कई देशों ने मानक को अपनी आवश्यकताओं के अनुसार अनुकूलित किया। परिणामस्वरूप, देशों के बीच मानकों में विविधताएँ उत्पन्न हुईं।

**इंटर-रजिस्टर सिग्नल (ITU-T Q.441).** MFC/R2 सिग्नलिंग दो टोन के संयोजन का उपयोग करता है। नीचे दी गई तालिकाएँ ITU मानक को दर्शाती हैं।

सिग्नल समूह I (आगे):

| Description | Forward signal |
| --- | --- |
| अंक 1 | I-1 |
| अंक 2 | I-2 |
| अंक 3 | I-3 |
| अंक 4 | I-4 |
| अंक 5 | I-5 |
| अंक 6 | I-6 |
| अंक 7 | I-7 |
| अंक 8 | I-8 |
| अंक 9 | I-9 |
| अंक 0 | I-10 |
| देश कोड संकेतक, आउटगोइंग हाफ‑इको सप्रेसर आवश्यक | I-11 |
| देश कोड संकेतक, कोई इको सप्रेसर आवश्यक नहीं | I-12 |
| टेस्ट कॉल संकेतक | I-13 |
| देश कोड संकेतक, आउटगोइंग हाफ‑इको सप्रेसर डाला गया | I-14 |
| प्रयुक्त नहीं | I-15 |

सिग्नल समूह II (फ़ॉरवर्ड):

| Description | Forward signal |
| --- | --- |
| प्राथमिकता रहित ग्राहक | II-1 |
| प्राथमिकता वाला ग्राहक | II-2 |
| रखरखाव उपकरण | II-3 |
| स्पेयर | II-4 |
| ऑपरेटर | II-5 |
| डेटा ट्रांसमिशन | II-6 |
| फ़ॉरवर्ड ट्रांसफ़र सुविधा के बिना ग्राहक या ऑपरेटर | II-7 |
| डेटा ट्रांसमिशन | II-8 |
| प्राथमिकता वाला ग्राहक | II-9 |
| फ़ॉरवर्ड ट्रांसफ़र सुविधा वाला ऑपरेटर | II-10 |
| स्पेयर | II-11 |
| स्पेयर | II-12 |
| स्पेयर | II-13 |
| स्पेयर | II-14 |
| स्पेयर | II-15 |

सिग्नल समूह A (पीछे की ओर):

| Description | Backward signal |
| --- | --- |
| अगला अंक भेजें (n+1) | A-1 |
| अंतिम से एक पहले का अंक भेजें (n-1) | A-2 |
| पता पूर्ण, Group B संकेतों की प्राप्ति में परिवर्तन | A-3 |
| राष्ट्रीय नेटवर्क में भीड़ | A-4 |
| कॉल करने वाले की श्रेणी भेजें | A-5 |
| पता पूर्ण, शुल्क, वार्तालाप स्थितियों की सेटिंग | A-6 |
| अंतिम से दो पहले का अंक भेजें (n-2) | A-7 |
| अंतिम से तीन पहले का अंक भेजें (n-3) | A-8 |
| अतिरिक्त | A-9 |
| अतिरिक्त | A-10 |
| देश कोड संकेतक भेजें | A-11 |
| भाषा या भेदभाव अंक भेजें | A-12 |
| सर्किट की प्रकृति भेजें | A-13 |
| इको सप्रेसर के उपयोग की जानकारी का अनुरोध | A-14 |
| अंतर्राष्ट्रीय एक्सचेंज या उसके आउटपुट में भीड़ | A-15 |

सिग्नल समूह B (पीछे की ओर):

| Description | Backward signal |
| --- | --- |
| Spare | B-1 |
| विशेष सूचना टोन भेजें | B-2 |
| ग्राहक की लाइन व्यस्त | B-3 |
| भीड़ (समूह A से B में परिवर्तन के बाद) | B-4 |
| अनिर्धारित संख्या | B-5 |
| ग्राहक की लाइन मुक्त, शुल्क | B-6 |
| ग्राहक की लाइन मुक्त, कोई शुल्क नहीं | B-7 |
| ग्राहक की लाइन खराब | B-8 |
| Spare | B-9 |
| Spare | B-10 |
| Spare | B-11 |
| Spare | B-12 |
| Spare | B-13 |
| Spare | B-14 |
| Spare | B-15 |

#### MFC/R2 अनुक्रम

निम्न क्रम एक कॉल को दर्शाता है जो Asterisk के एक्सटेंशन से PSTN में एक टर्मिनल तक उत्पन्न होती है। PSTN कॉल को ड्रॉप कर देती है और संचार को समाप्त कर देती है।

![Asterisk और टेलको के बीच एक पूर्ण MFC/R2 कॉल फ्लो: लाइन सिग्नलिंग (Idle, Seized, Seize Ack, Answer, Clearback, Clear Forward) टाइमस्लॉट 16 में विनिमय होता है, डायल किए गए अंक और पीछे की ओर "अगला अंक भेजें" संकेत (समूह I/A/B) इन‑बैंड यात्रा करते हैं, और श्रव्य टोन सब्सक्राइबर तक पहुँचते हैं.](../images/10-legacy-fig11.png)

### ड्राइवर libopenr2 का उपयोग कैसे करें

Moises Silva द्वारा शुरू किया गया प्रोजेक्ट Steve Underwood द्वारा लिखे गए Unicall चैनल ड्राइवर से प्रेरित था। OpenR2 लाइब्रेरी वर्तमान में Asterisk के लिए सबसे स्थिर सॉफ़्टवेयर समाधान है। इस समाधान के साथ, हम किसी भी डिजिटल कार्ड का उपयोग कर सकते हैं जो DAHDI के साथ संगत हो। पहले, MFC/R2 के लिए केवल स्वामित्व वाले समाधान उपलब्ध थे, जिनमें से सबसे अच्छा जो मैंने उपयोग किया वह Khomp द्वारा उपलब्ध कराया गया था, www.khomp.com.br। Asterisk 22 में, libopenR2 के माध्यम से MFC/R2 समर्थन तब निर्मित होता है जब कंपाइल समय पर लाइब्रेरी मौजूद हो — कोई बाहरी पैच आवश्यक नहीं है। नीचे दिए गए चरण ऐतिहासिक मैनुअल इंस्टॉलेशन को संदर्भ के लिए दिखाते हैं; आधुनिक सिस्टमों पर, `libopenr2-dev` को अपने वितरण के पैकेज मैनेजर से इंस्टॉल करें, फिर `./configure` चलाने से पहले, `chan_dahdi` को `make menuselect` में सक्षम करें।

नीचे दिए गए चरण openr2 और Asterisk को उनके वर्तमान Git रिपॉज़िटरीज़ से बनाते हैं। इन्हें स्रोत से बनाते साइटों के लिए एक संदर्भ के रूप में रखा गया है; एक आधुनिक वितरण पर आप आमतौर पर इन्हें पूरी तरह से छोड़ सकते हैं, `libopenr2-dev` पैकेज और एक पैकेज्ड Asterisk 22 बिल्ड स्थापित करके, क्योंकि `chan_dahdi` libopenr2 के खिलाफ सीधे R2 समर्थन को संकलित करता है बिना किसी बाहरी पैच के।

चरण 1: आवश्यक बिल्ड टूलिंग स्थापित करें।

```
apt-get install git
```

Step 2: Clone the openr2 library and the Asterisk source. No special patched tree is needed on Asterisk 22 — a stock checkout builds R2 support as long as libopenr2 is present.

```
cd /usr/src
git clone https://github.com/moises-silva/openr2.git
git clone https://github.com/asterisk/asterisk.git
```

Step 3: संकलित करें और स्थापित करें  
कृपया, अपने सर्वर का BACK UP करें आगे बढ़ने से पहले।

```
cd /usr/src/openr2
./configure && make && make install && ldconfig
cd /usr/src/asterisk
./configure && make menuselect && make && make install
```

Note: “make samples” को निष्पादित न करें ताकि आपकी कॉन्फ़िगरेशन फ़ाइलें ओवरराइट न हों।

```
Step 4: Changing the file /etc/dahdi/system.conf:
vim /etc/dahdi/system.conf
```

मान लीजिए आपके पास एक कार्ड है जिसमें एक E1 इंटरफ़ेस है।

```
span=1,1,0,cas,hdb3
cas=1-15:1101
cas=17-31:1101
dchan=16
loadzone=br
defaultzone=br
```

Step 5: ड्राइवर में बदलाव लागू करने के लिए कमांड dahdi_cfg चलाएँ:

```
dahdi_cfg -vvvvvvvv
Dahdi Version:SVN-branch-1.4-r4348
Echo Canceller: MG2
Configuration
======================
SPAN 1: CAS/HDB3 Build-out: 0 db (CSU)/0-133 feet (DSX-1)
Channel map:
Channel 01: CAS / User (Default) (Slaves: 01)
Channel 02: CAS / User (Default) (Slaves: 02)
Channel 03: CAS / User (Default) (Slaves: 03)
Channel 04: CAS / User (Default) (Slaves: 04)
Channel 05: CAS / User (Default) (Slaves: 05)
Channel 06: CAS / User (Default) (Slaves: 06)
Channel 07: CAS / User (Default) (Slaves: 07)
Channel 08: CAS / User (Default) (Slaves: 08)
Channel 09: CAS / User (Default) (Slaves: 09)
Channel 10: CAS / User (Default) (Slaves: 10)
Channel 11: CAS / User (Default) (Slaves: 11)
Channel 12: CAS / User (Default) (Slaves: 12)
Channel 13: CAS / User (Default) (Slaves: 13)
Channel 14: CAS / User (Default) (Slaves: 14)
Channel 15: CAS / User (Default) (Slaves: 15)
Channel 16: D-channel (Default) (Slaves: 16)
Channel 17: CAS / User (Default) (Slaves: 17)
Channel 18: CAS / User (Default) (Slaves: 18)
Channel 19: CAS / User (Default) (Slaves: 19)
Channel 20: CAS / User (Default) (Slaves: 20)
Channel 21: CAS / User (Default) (Slaves: 21)
Channel 22: CAS / User (Default) (Slaves: 22)
Channel 23: CAS / User (Default) (Slaves: 23)
Channel 24: CAS / User (Default) (Slaves: 24)
Channel 25: CAS / User (Default) (Slaves: 25)
Channel 26: CAS / User (Default) (Slaves: 26)
Channel 27: CAS / User (Default) (Slaves: 27)
Channel 28: CAS / User (Default) (Slaves: 28)
Channel 29: CAS / User (Default) (Slaves: 29)
Channel 30: CAS / User (Default) (Slaves: 30)
Channel 31: CAS / User (Default) (Slaves: 31)
31 channels to configure.
-----------------------------------------------------------------------
```

चरण 5: फ़ाइल chan_dahdi.conf बदलें

```
vim /etc/asterisk/chan_dahdi.conf
[channels]
usecallerid=yes
callwaiting=yes
usecallingpres=yes
callwaitingcallerid=yes
threewaycalling=yes
transfer=yes
canpark=yes
cancallforward=yes
callreturn=yes
echocancel=yes
echotrainning=yes
echocancelwhenbridged=yes
signalling=mfcr2
mfcr2_variant=br
mfcr2_get_ani_first=no
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
mfcr2_logdir=span1
mfcr2_logging=all
group=1
callgroup=1
pickupgroup=1
callerid=asreceived
context=from-mfcr2
channel => 1-15,17-31
```

Step 6: फ़ाइल extensions.conf में डायल प्लान बदलें

```
vim /etc/asterisk/extensions.conf
[default]
exten => _XXXXXXXX,1,Set(CALLERID(num)=1145678990)
exten => _XXXXXXXX,n,Dial(DAHDI/g1/${EXTEN},60,tT)
```

Note: Some TELCOS do not accept calls without the caller ID. Please set the caller ID to one of the DID numbers assigned by the operator. In some countries, this step is not required. Step 7: Test the solution: Now, with an extension in the context from-internal, call any number and observe the console. Check to see if any errors are occurring. -- Executing Set("SIP/8564-081ca5d8", "CALLERID(num)=1145678990") in new stack -- Executing Dial("SIP/8564-081ca5d8", "DAHDI/g1/35678899|60|tT") in new stack

#### Debugging OpenR2

To detect errors in the calls, you can activate the debug. To do this, follow the steps below.

1. Edit the file `chan_dahdi.conf` and add the following three lines to the configuration:

```
mfcr2_logdir=span1
mfcr2_logging=all
mfcr2_call_files=yes
```

2. Asterisk सर्वर को पुनः प्रारंभ करें
3. कॉल का परीक्षण करें और `/var/log/asterisk/mfcr2/span1` पर कॉल फ़ाइलों की जाँच करें

Below is a trace for a normal call. Compare it to what you receive in your call.

```
[15:05:47:710] [Thread: 3078019984] [Chan 1] - Call started at Mon Jul  6 15:05:47 2009 on
chan 1
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Tx >> [SEIZE] 0x00
[15:05:47:710] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x01
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Bits changed from 0x08 to 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - CAS Rx << [SEIZE ACK] 0x0C
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 2
[15:05:47:951] [Thread: 3078019984] [Chan 1] - timer id 2 found, cancelling it now
[15:05:47:951] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 3
[15:05:47:951] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:070] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 0
[15:05:48:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:48:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 2
[15:05:48:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:48:350] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:450] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:550] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:550] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:650] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:48:750] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:48:750] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:48:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 5
[15:05:48:950] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [ON]
[15:05:48:950] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:050] [Thread: 3078019984] [Chan 1] - MF Tx >> 5 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 8
[15:05:49:150] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:49:150] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:250] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Sending DNIS digit 4
[15:05:49:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:330] [Thread: 3078019984] [Chan 1] - Group A DNIS request handled
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:590] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:670] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:49:670] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:770] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:49:850] [Thread: 3078019984] [Chan 1] - Sending ANI digit 4
[15:05:49:850] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:49:930] [Thread: 3078019984] [Chan 1] - MF Tx >> 4 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:030] [Thread: 3078019984] [Chan 1] - Sending ANI digit 8
[15:05:50:030] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:130] [Thread: 3078019984] [Chan 1] - MF Tx >> 8 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:230] [Thread: 3078019984] [Chan 1] - Sending ANI digit 3
[15:05:50:230] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:330] [Thread: 3078019984] [Chan 1] - MF Tx >> 3 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:430] [Thread: 3078019984] [Chan 1] - Sending ANI digit 0
[15:05:50:430] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:530] [Thread: 3078019984] [Chan 1] - MF Tx >> 0 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:50:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:50:810] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:50:810] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:50:910] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:010] [Thread: 3078019984] [Chan 1] - Sending ANI digit 2
[15:05:51:010] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:110] [Thread: 3078019984] [Chan 1] - MF Tx >> 2 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:210] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:210] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:310] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:410] [Thread: 3078019984] [Chan 1] - Sending ANI digit 7
[15:05:51:410] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:510] [Thread: 3078019984] [Chan 1] - MF Tx >> 7 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:610] [Thread: 3078019984] [Chan 1] - Sending ANI digit 1
[15:05:51:610] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [ON]
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:710] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Rx << 5 [OFF]
[15:05:51:810] [Thread: 3078019984] [Chan 1] - Sending more ANI unavailable
[15:05:51:810] [Thread: 3078019984] [Chan 1] - MF Tx >> F [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [ON]
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:51:990] [Thread: 3078019984] [Chan 1] - MF Tx >> F [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Rx << 3 [OFF]
[15:05:52:090] [Thread: 3078019984] [Chan 1] - Sending category National Subscriber
[15:05:52:090] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [ON]
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:05:53:350] [Thread: 3078019984] [Chan 1] - MF Tx >> 1 [OFF]
[15:05:53:430] [Thread: 3078019984] [Chan 1] - MF Rx << 1 [OFF]
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - Cannot cancel timer 0
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Tx >> [CLEAR FORWARD] 0x08
[15:06:03:322] [Thread: 3078019984] [Chan 1] - CAS Raw Tx >> 0x09
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Bits changed from 0x0C to 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - CAS Rx << [IDLE] 0x08
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Call ended
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Attempting to cancel timer timer 0
[15:06:03:569] [Thread: 3085228944] [Chan 1] - Cannot cancel timer 0
```

#### MFC/R2 कॉन्फ़िगरेशन

विकल्पों का दस्तावेज़ फ़ाइल chan_dahdi.conf के भीतर है। यहाँ कुछ सबसे महत्वपूर्ण विकल्पों का विवरण दिया गया है। अनिवार्य पैरामीटर: mfcr2_variant, mfcr2_max_ani और mfcr2_max_dnis। mfcr2_variant: देश वैरिएंट।

```
r2test -l
Variant Code        Country
AR                  Argentina
BR                  Brazil
CN                  China
CZ                  Czech Republic
CO                  Colombia
EC                  Ecuador
ITU                 International Telecommunication Union
MX                  Mexico
PH                  Philippines
VE                  Venezuela
```

mfcr2_max_ani: Max amount of ANI digits to ask for  
mfcr2_max_dnis: Max amount of DNIS digits to ask for  
mfcr2_get_ani_first: Whether or not to get ANI before DNIS (required by some TELCOS)  
mfcr2_category: Caller category. You can set the variable MFCR2_CATEGORY before starting the call  
mfcr2_logdir: Directory to log the call files. (/var/log/asterisk/mfcr2/directory)  
mfcr2_call_files: Whether or not to log the calls  

- mfcr2_logging: logging values  
- cas – ABCD bits for tx and rx  
- mf – Multifrequency tones  
- stack – verbose output of the channel and context stack  
- all – all activities  
- nothing – do not log anything  

mfcr2_mfback_timeout: This value deserves to be mentioned. Sometimes if you are calling a cell phone or any call that takes a long time to complete, this parameter can time out, so it is often changed for fine tuning. If some of your calls are not being completed, this is the parameter you should change first.  
mfcr2_metering_pulse_timeout: Pulses are used by some R2 variants to indicate costs  
mfcr2_allow_collect_calls: In Brazil, the tone II-8 is used to indicate a collect call; this parameter allows you to block collect calls.  
mfcr2_double_answer: Also used to avoid collect calls when a double answer is required. With double_answer=yes you actually block the collect calls.  
mfcr2_immediate_accept: Allows you to skip the use of group B/II signals and go directly to the accepted state.  
mfcr2_forced_release: Allows you to speed up the release of the call; works for the Brazilian variant.  

#### ANI and DNIS

Automatic Number Identification (ANI) is the caller’s number. Dialed Number Identification Service (DNIS ) is the number called or, in other words, the number dialed. When a call is received, usually the last four numbers are passed to the PBX in a process referred to as direct inward dial (DID). The ANI number is actually the Caller ID. ANI will have the caller’s extension when dialing while DNIS will contain the call destination. It is important that these parameters be configured correctly. Some switches send just the last four digits while others send the complete number.

### DAHDI channel format

DAHDI channels use the following format in the dial plan:

```
DAHDI/[g]<identifier>[c][r<cadence>]
<identifier> - Physical channel numeric identifier
[g] - Group identifier
[c] - Answer confirmation. A number is not considered until the callee presses "#"
[r] - customized ringing
[cadence] - Integer from 1 to 4
```

उदाहरण:

```
DAHDI/2     - channel 2
DAHDI/g1    - First available channel in group 1
```

## IAX2 प्रोटोकॉल

In this chapter, we will learn about the Inter-Asterisk eXchange (IAX) protocol, including its strengths and weaknesses. Details such as trunk mode and the interconnection of two Asterisk servers will also be covered. All references in this document correspond to IAX version 2.

IAX प्रोटोकॉल आवाज़ और वीडियो के लिए मीडिया ट्रांसपोर्ट और सिग्नलिंग प्रदान करता है। IAX बहुत नवाचारी है; यह ट्रंक मोड में बैंडविड्थ बचाता है और जब आपको NAT को पार करना हो तो SIP की तुलना में बहुत सरल है। आजकल IAX का मुख्य उपयोग Asterisk सर्वरों को आपस में जोड़ना है। IAX मूलतः आवाज़ के लिए बनाया गया था, लेकिन यह वीडियो और अन्य मल्टीमीडिया स्ट्रीम्स को भी संभाल सकता है।

IAX अन्य VoIP प्रोटोकॉल, जैसे SIP और MGCP से प्रेरित था। सिग्नलिंग और मीडिया के लिए दो अलग-अलग प्रोटोकॉल का उपयोग करने के बजाय, IAX ने उन्हें एकीकृत करके एक अनूठा प्रोटोकॉल बनाया। IAX मीडिया ट्रांसपोर्ट के लिए RTP का उपयोग नहीं करता; इसके बजाय, यह मीडिया को उसी UDP कनेक्शन में एम्बेड करता है।

**Status in Asterisk 22.** `chan_iax2` अभी भी Asterisk 22 LTS में शामिल है और पूरी तरह समर्थित है, इसलिए इस अनुभाग में सभी जानकारी वैध रहती है। IAX2, हालांकि, एक पुराना प्रोटोकॉल है जिसका नया उपयोग अपेक्षाकृत कम है: उद्योग ने अधिकांशतः SIP (via `chan_pjsip` in Asterisk 22) को प्रोवाइडर ट्रंकिंग और सर्वर इंटरकनेक्शन दोनों के लिए अपनाया है। IAX2 का मुख्य शेष लाभ इसका सिंगल‑पोर्ट डिज़ाइन है — सभी सिग्नलिंग और मीडिया एक ही UDP पोर्ट (डिफ़ॉल्ट रूप से 4569) पर प्रवाहित होते हैं, जिससे SIP और उसके अलग RTP स्ट्रीम्स की तुलना में फ़ायरवॉल और NAT कॉन्फ़िगरेशन सरल हो जाता है। एक नए Asterisk‑to‑Asterisk ट्रंक के लिए जहाँ NAT समस्या नहीं है, PJSIP ट्रंक को आधुनिक अनुशंसित तरीका माना जाता है; IAX2 यहाँ शामिल किया गया है क्योंकि यह अभी भी एक वैध विकल्प है, विशेषकर जब फ़ायरवॉल के माध्यम से केवल एक UDP पोर्ट ही खोला जा सकता है।

### उद्देश्य

इस अध्याय के अंत तक, आप सक्षम होंगे:

- Identify strengths and weakness of IAX protocol
- Describe usage scenarios for the IAX protocol
- Describe the advantages of IAX trunk mode
- Configure iax.conf for phones
- Configure iax.conf for connection to a VoIP provider
- Configure iax.conf for Asterisk interconnection
- Understand IAX authentication

### IAX डिज़ाइन

IAX डिजाइन के मुख्य उद्देश्य हैं:

- मीडिया ट्रांसपोर्ट और सिग्नलिंग के लिए आवश्यक बैंडविड्थ को कम करने के लिए
- NAT ट्रांसपेरेंसी प्रदान करने के लिए
- डायल प्लान जानकारी प्रसारित करने में सक्षम होने के लिए
- पेजिंग और इंटरकॉम के कुशल उपयोग को समर्थन देने के लिए

IAX एक पीयर‑टू‑पीयर सिग्नलिंग और मीडिया प्रोटोकॉल है जो RTP का उपयोग किए बिना SIP के समान है। मूल दृष्टिकोण दो होस्टों के बीच एक ही UDP कनेक्शन पर मल्टीमीडिया स्ट्रीम को मल्टीप्लेक्स करना है। इस दृष्टिकोण का सबसे बड़ा लाभ NAT के ऊपर कनेक्शन को पार करने की सरलता है, जो अक्सर xDSL मॉडेम में पाया जाता है। IAX डिफ़ॉल्ट रूप से एक ही पोर्ट, UDP 4569, का उपयोग करता है, और फिर सभी स्ट्रीम को मल्टीप्लेक्स करने के लिए 15‑बिट कॉल नंबर का उपयोग करता है। IAX प्रोटोकॉल SIP प्रोटोकॉल के समान पंजीकरण और प्रमाणीकरण प्रक्रियाओं का उपयोग करता है। प्रोटोकॉल का विवरण http://www.ietf.org/internet-drafts/draft-guy-iax-05.txt पर पाया जा सकता है।

![IAX प्रोटोकॉल कई कॉल्स को दो एंडपॉइंट्स के बीच एक ही UDP पोर्ट (डिफ़ॉल्ट रूप से 4569) पर मल्टीप्लेक्स करता है, 15‑बिट कॉल नंबर का उपयोग करके स्ट्रीम्स को अलग रखता है — जिससे NAT ट्रैवर्सल सरल हो जाता है.](../images/10-legacy-fig12.png)

### बैंडविड्थ उपयोग

VoIP नेटवर्क में उपयोग की जाने वाली बैंडविड्थ कई कारकों से प्रभावित होती है; कोडेक और प्रोटोकॉल हेडर सबसे महत्वपूर्ण हैं। IAX प्रोटोकॉल में एक आश्चर्यजनक विशेषता है जिसे ट्रंक मोड कहा जाता है, जिसके द्वारा यह एक ही हेडर का उपयोग करके कई कॉलों को मल्टीप्लेक्स करता है। Asterisk बैंडविड्थ कैलकुलेटर के साथ प्रयोग करके आप देखेंगे कि IAX ट्रंक कई कॉलों के साथ ट्रैफ़िक का **80%** तक बचा सकते हैं।

![IAX और SIP ओवरहेड की तुलना: दो SIP/RTP कॉल्स को दो पैकेट्स (40 बाइट पेलोड 156 बाइट ओवरहेड के तहत) की आवश्यकता होती है, जबकि IAX2 ट्रंक मोड दोनों कॉल्स को एक ही पैकेट (40 बाइट पेलोड केवल 66 बाइट ओवरहेड के तहत) में ले जाता है, कई मिनी‑फ़्रेम्स में एक IP/UDP हेडर साझा करके.](../images/10-legacy-fig13.png)

### चैनल नामकरण

डायलप्लान में चैनल निर्दिष्ट करते समय आप इन नामों का उपयोग करेंगे, इसलिए चैनल‑नामकरण परम्पराओं को समझना महत्वपूर्ण है।  
आउटबाउंड चैनलों के लिए उपयोग किए जाने वाले IAX चैनल नाम का स्वरूप इस प्रकार है:

```
IAX/[<user>[:<secret>]@]<peer>[:<portno>][/<exten>[@<context>][/<options>]
```

- `<user>` — रिमोट पीयर पर UserID, या iax.conf में कॉन्फ़िगर किए गए क्लाइंट का नाम  
- `<secret>` — पासवर्ड। वैकल्पिक रूप से यह RSA कुंजी की फ़ाइलनाम हो सकता है, बिना अंत में .key या .pub एक्सटेंशन के, और वर्ग कोष्ठकों में बंद किया गया हो  
- `<peer>` — कनेक्ट करने के लिए सर्वर का नाम  
- `<portno>` — कनेक्शन के लिए पोर्ट नंबर  
- `<exten>` — रिमोट Asterisk सर्वर में एक्सटेंशन  
- `<context>` — रिमोट Asterisk सर्वर में कॉन्टेक्स्ट  
- `<options>` — उपलब्ध एकमात्र विकल्प 'a' है, जिसका अर्थ है 'request autoanswer'  

#### Outbound channels example:

Outbound channels Asterisk कंसोल में दिखते हैं।

- `IAX2/8590:secret@myserver/8590@default` — myserver में 8590 एक्सटेंशन को कॉल करें। यह 8590:secret को नाम/पासवर्ड जोड़ी के रूप में उपयोग करता है  
- `IAX2/iaxphone` — "iaxphone" को कॉल करें  
- `IAX2/judy:[judyrsa]@somewhere.com` — somewhere.com को कॉल करें, जहाँ उपयोगकर्ता नाम judy है और प्रमाणीकरण के लिए RSA कुंजी उपयोग की जाती है  

#### The format of an incoming IAX channel is:

Inbound channels Asterisk कंसोल में दिखते हैं।

```
IAX2/[<username>@]<host>]-<callno>
```

- `<username>` — यदि ज्ञात हो तो उपयोगकर्ता नाम
- `<host>` — कनेक्ट हो रहा होस्ट
- `<callno>` — स्थानीय कॉल नंबर

Incoming channel example:

- `IAX2[flavio@8.8.30.34]/10` — कॉल नंबर 10, IP पता 8.8.30.34 से, उपयोगकर्ता flavio के साथ।
- `IAX2[8.8.30.50]/11` — कॉल नंबर 11, IP पता 8.8.30.50 से।

### Using IAX

आप IAX को कई तरीकों से उपयोग कर सकते हैं। इस अनुभाग में, हम आपको कई परिदृश्यों के लिए IAX को कॉन्फ़िगर करने का तरीका दिखाएंगे, जिसमें शामिल हैं:

- IAX का उपयोग करके एक softphone को कनेक्ट करना
- IAX का उपयोग करके एक VoIP प्रदाता से कनेक्ट करना
- IAX का उपयोग करके दो सर्वरों को कनेक्ट करना
- ट्रंक मोड में IAX का उपयोग करके दो सर्वरों को कनेक्ट करना
- IAX कनेक्शन को डिबग करना
- प्रमाणीकरण के लिए RSA पेयर कुंजियों का उपयोग करना

#### Connecting a softphone using IAX

Asterisk IP फ़ोन को समर्थन देता है जो IAX पर आधारित हैं, जैसे ATCOM और Digium का पुराना ATA (जिसे IAXy कहा जाता है) तथा वे softphone जो अभी भी IAX2 प्रोटोकॉल को लागू करते हैं। softphone, ATA, और हार्ड‑फ़ोन के लिए प्रक्रिया समान है। एक IAX डिवाइस को कॉन्फ़िगर करने के लिए, आपको /etc/asterisk में स्थित iax.conf फ़ाइल को संपादित करना होगा।

```
directory.
```

हम एक IAX2‑सक्षम सॉफ्टफ़ोन को उदाहरण के रूप में उपयोग करेंगे।

1. मूल `iax.conf` फ़ाइल का बैकअप बनाएं, उपयोग करके:

```
#cd /etc/asterisk
#mv iax.conf iax.conf.backup
```

2. नई `iax.conf` फ़ाइल को संपादित करना शुरू करें:

```
[general]
bindport=4569
bindaddr=8.8.1.4
bandwidth=high
```

- ; बहुत महत्वपूर्ण पैरामीटर, यह उपलब्ध कोडेक्स को बदलता है

```
disallow=all
allow=ulaw
jitterbuffer=no
forcejitterbuffer=no
tos=lowdelay
autokill=yes
[guest]
type=user
context=guest
callerid="Guest IAX User"
; Trust Caller*ID Coming from iaxtel.com
;
[iaxtel]
type=user
context=default
auth=rsa
inkeys=iaxtel
;
; Trust Caller*ID Coming from iax.fwdnet.net
;
[iaxfwd]
type=user
context=default
auth=rsa
inkeys=freeworlddialup
;
; Trust callerid delivered over DUNDi/e164
;
;
;[dundi]
;type=user
;dbsecret=dundi/secret
;context=dundi-e164-local
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

मैंने सैंपल फ़ाइल की डिफ़ॉल्ट (गैर‑टिप्पणीकृत) लाइनों को संरक्षित रखने की कोशिश की है।  
निम्नलिखित पैरामीटर संशोधित किए गए थे:

```
bandwidth=high
```

यह पंक्ति कोडेक चयन को प्रभावित करती है। उच्च सेटिंग का उपयोग करने से उच्च बैंडविड्थ और उच्च गुणवत्ता वाले कोडेक, जैसे कि `g.711` जिसे `ulaw` कुंजी‑शब्द द्वारा परिभाषित किया गया है, का चयन संभव हो जाता है। यदि आप डिफ़ॉल्ट पैरामीटर को रखते हैं, तो आप `ulaw` चुन नहीं पाएँगे। इस स्थिति में, Asterisk नीचे दिए गए कॉन्फ़िगरेशन के लिए “no codec available” संदेश देगा।

```
disallow=all
allow=ulaw
```

ऊपर वर्णित कमांडों में, हमने सभी कोडेक्स को अक्षम कर केवल ulaw को सक्षम किया। LAN में, अधिकांश लोग ulaw का उपयोग करना पसंद करते हैं क्योंकि यह प्रोसेसर‑गहन नहीं है और CPU साइकिल बचाता है। अधिक बैंडविड्थ का उपयोग करने के बावजूद, यह कोडेक पसंदीदा है क्योंकि LAN में आमतौर पर 100‑मेगाबिट ईथरनेट या यहाँ तक कि गीगाबिट उपलब्ध होते हैं। ulaw का उपयोग करने वाली एक आवाज़ कॉल आपके नेटवर्क से लगभग 100 kilobits प्रति सेकंड बैंडविड्थ लेती है, जो आज के हाई‑स्पीड LAN के लिए बहुत हल्का उपयोग है। WAN या इंटरनेट नेटवर्क में, आप आमतौर पर ulaw को अक्षम कर देते हैं, आवाज़ संपीड़न के द्वारा उपलब्ध CPU साइकिल को कुछ हद तक बदलते हुए बेहतर बैंडविड्थ उपयोग प्राप्त करने के लिए। कोडेक्स gsm, g729, और ilbc भी अच्छा संपीड़न कारक प्रदान करते हैं।

```
[2003]
type=friend
context=default
secret=senha
host=dynamic
```

ऊपर के कमांड्स में, हमने एक मित्र जिसका नाम [2003] है, को परिभाषित किया है। कॉन्टेक्स्ट डिफ़ॉल्ट है (पहले लैब्स में हम हमेशा भ्रम से बचने के लिए डिफ़ॉल्ट कॉन्टेक्स्ट का उपयोग करते हैं; यह कॉन्टेक्स्ट तब पूरी तरह समझाया जाएगा जब हम डायल प्लान को कवर करेंगे)। लाइन “host=dynamic” फोन के IP एड्रेस की डायनामिक रजिस्ट्रेशन प्रदान करती है।

3. एक IAX2-सक्षम सॉफ्टफ़ोन डाउनलोड और इंस्टॉल करें। आप कोई भी सॉफ्टफ़ोन चुन सकते हैं जो अभी भी लैब के लिए IAX2 प्रोटोकॉल को सपोर्ट करता हो।  
4. क्लाइंट में एक IAX अकाउंट कॉन्फ़िगर करें (आमतौर पर *Add account* → IAX)। ध्यान दें कि SipPulse Softphone केवल SIP-केवल है और IAX2 पर रजिस्टर नहीं कर सकता, इसलिए IAX परीक्षण के लिए आपको ऐसा क्लाइंट चाहिए जो अभी भी प्रोटोकॉल को सपोर्ट करता हो।

5. अपने IAX डिवाइस का परीक्षण करने के लिए `extensions.conf` फ़ाइल को कॉन्फ़िगर करें।

```
[default]
exten=>2000,1,Dial(SIP/2000)
exten=>2001,1,Dial(SIP/2001)
exten=>2003,1,Dial(IAX2/2003)
```

Now you can dial between the SIP phones created in Chapter 3 and the IAX phone created in the lab.

#### Connecting to a VoIP provider using IAX

कुछ VoIP प्रदाता IAX का समर्थन करते हैं। “IAX providers” खोजकर आप आसानी से एक IAX प्रदाता पा सकते हैं। IAX का उपयोग करना समझदारी है क्योंकि यह बहुत बैंडविड्थ बचा सकता है, NAT को आसानी से पार करता है, और RSA कुंजी जोड़े के माध्यम से प्रमाणीकरण कर सकता है।

![A customer's Asterisk connected to a VoIP provider over an IAX trunk across the Internet: a single trunk carries all calls to and from the provider.](../images/10-legacy-fig14.png)

पिछले कई Asterisk रिलीज़ों में IAX‑सक्षम व्यावसायिक VoIP प्रदाताओं की संख्या में तीव्र गिरावट आई है; अधिकांश प्रदाता अब केवल SIP/PJSIP ट्रंक प्रदान करते हैं। IAX प्रदाता को चुनने से पहले यह पुष्टि कर लें कि वे अपने IAX इन्फ्रास्ट्रक्चर को सक्रिय रूप से बनाए रखते हैं। नए प्रदाता एकीकरण के लिए, PJSIP ट्रंक (Chapter 3) अनुशंसित विकल्प है।

#### Connecting to a provider using IAX

Step 1: Open an account in your favorite provider. Your provider will provide you three things.

- Name
- Secret
- IP address or Host name
- RSA public key

Step 2: Configure the iax.conf file to register your Asterisk with your provider. Add the following lines to the [general] section of the file.

```
[general]
register=>name:secret@hostname/2003
```

ऊपर वर्णित निर्देशों में, आपने अपने प्रोवाइडर के साथ अपने अकाउंट और पासवर्ड का उपयोग करके रजिस्टर किया। जैसे ही आपको कॉल प्राप्त होगी, वह 2003 एक्सटेंशन पर फॉरवर्ड कर दी जाएगी।

```
[name]
```

- ; आपका खाता नाम या संख्या

```
type=peer
secret=secret
; Your password
host=hostname
```

ऊपर वर्णित निर्देशों में, हमने डायलिंग उद्देश्यों के लिए प्रदाता के अनुरूप एक पीयर बनाया है।

```
[nameiax]
type=user
context=default
auth=rsa
inkeys=hostname
```

यह RSA प्रमाणीकरण के लिए आवश्यक है। आपके प्रदाता की सार्वजनिक कुंजी का उपयोग करने से आप यह सुनिश्चित कर सकते हैं कि प्राप्त हो रही कॉल वास्तव में वास्तविक प्रदाता से ही है। यदि कोई अन्य व्यक्ति समान पथ का उपयोग करने का प्रयास करता है, तो वह इसे प्रमाणित नहीं कर पाएगा क्योंकि उसके पास संबंधित निजी कुंजी नहीं है। चरण 4: कनेक्शन का प्रयास करें। कनेक्शन का परीक्षण करने के लिए, किसी भी नंबर पर कॉल करें। कुछ विक्रेता एक इको टेस्ट प्रदान करते हैं। इसे पूरा करने के लिए, कृपया `extensions.conf` फ़ाइल को संपादित करें।

```
[default]
exten=>*98,1,Dial(IAX2/name:secret@hostname/*98,20,r)
```

Go to the Asterisk CLI and issue a reload. To verify if Asterisk is registered with the provider, use the next command.

```
*CLI>reload
*CLI>iax2 show register
```

Now simply dial *98 on the softphone connected to the Asterisk server.

#### दो Asterisk सर्वरों को IAX ट्रंक के माध्यम से जोड़ना

यह बहुत आसान है कि एक सर्वर को दूसरे से जोड़ा जाए। आपको उन्हें रजिस्टर करने की आवश्यकता नहीं होगी क्योंकि IP पते पहले से ही ज्ञात हैं। आपको iax.conf फ़ाइल में peers और users बनाना होगा। HQ साइट में सभी एक्सटेंशन 20 से शुरू होते हैं, उसके बाद दो अंक (उदाहरण के लिए, 2000)। ब्रांच में, सभी एक्सटेंशन 22 से शुरू होते हैं, उसके बाद दो अंक (उदाहरण के लिए, 2200)। हम ट्रंक का उपयोग करेंगे। इस सुविधा को सक्षम करने के लिए आपको एक DAHDI टाइमिंग स्रोत की आवश्यकता होगी। Step 1: ब्रांच सर्वर में iax.conf फ़ाइल को संपादित करें।

![IAX ट्रंक के साथ दो Asterisk सर्वरों को जोड़ना: HQ सर्वर (192.168.1.1, एक्सटेंशन 20xx) और ब्रांच सर्वर (192.168.1.2, एक्सटेंशन 22xx) एक ही IAX ट्रंक पर एक-दूसरे से जुड़े हैं — कोई रजिस्ट्रेशन आवश्यक नहीं क्योंकि दोनों IP पते स्थिर और ज्ञात हैं.](../images/10-legacy-fig15.png)

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;allow=gsm
[Branch]
type=user
context=default
secret=password
host=192.168.2.10
trunk=yes
notransfer=yes
[HQ]
type=peer
context=default
username=HQ
secret=password
host=192.168.2.10
callerID='HQ'
trunk=yes
notransfer=yes
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2000'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2001'
```

चरण 2: ब्रांच सर्वर में extensions.conf फ़ाइल को कॉन्फ़िगर करें

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_20XX,1,dial(IAX2/HQ/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

Step 3: HQ सर्वर में iax.conf फ़ाइल को कॉन्फ़िगर करें

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
[Branch]
type=peer
context=default
username=Branch
secret=password
host=192.168.2.9
callerid="Branch"
trunk=yes
notransfer=yes
[HQ]
type=user
secret=password
context=default
host=192.168.2.9
callerid="HQ"
trunk=yes
notransfer=yes
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2200"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2201"
host=dynamic
```

Step 4: HQ सर्वर में extensions.conf फ़ाइल को कॉन्फ़िगर करें।

```
[general]
static=yes
writeprotect=no
autofallthrough=yes
clearglobalvars=no
priorityjumping=no
[default]
exten=>_22XX,1,Dial(IAX2/Branch/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 5: Test a call from the phone 2000 in the HQ server to the phone 2200 in the Branch server.

### IAX authentication

Now let’s analyze the IAX authentication process from the practical standpoint to help you choose the best method for each specific requirement.

#### Incoming connections

![एक इनकमिंग कॉल के लिए IAX प्रमाणीकरण निर्णय प्रवाह: Asterisk यह निर्धारित करता है कि उपयोगकर्ता नाम प्रदान किया गया है या नहीं, क्या वह किसी सेक्शन से मेल खाता है, क्या स्रोत IP की अनुमति है, और क्या सीक्रेट (plaintext, MD5, या RSA) मेल खाता है — उस सेक्शन के context और peer विकल्पों के साथ कॉल को स्वीकार करता है, या उसे अस्वीकार करता है.](../images/10-legacy-fig16.png)

When Asterisk receives an incoming connection, the initial information can include a user name (from the field "username=") or not. The incoming connection has an IP address too, which Asterisk uses for authentication as well.

If a user is provided, Asterisk:

1. Searches iax.conf for an entry with type=user (or type=friend with a section name matching the username). If it did not find it, Asterisk refuses the connection.
2. If the entry found has deny/allow configurations, it compares the IP address from the caller to determine whether to accept the call or not depending on the deny/allow clauses.
3. It checks the password (secret) using plaintext, md5, or RSA.
4. It accepts the connection and sends the call to the context specified in the line "context=" from the iax.conf file.

If a username is not provided, Asterisk:

1. Searches for an entry containing type=user (or type=friend) in the iax.conf file without a specified secret. It checks deny/allow clauses as well. If an entry is found, the connection is accepted and the section name is used as the user's name.
2. Searches for an entry containing type=user (or type=friend) in the iax.conf file with a secret or RSA key specified. It checks deny/allow clauses. If an entry is found, it tries to authenticate the caller using the specified secret; if it matches, it accepts the connection. Section name is the user's name.

Let's suppose your iax.conf file has the following entries:

```
[guest]
type=user
context=guest
[iaxtel]
type=user
context=incoming
auth=rsa
inkeys=iaxtel
[iax-gateway]
type=friend
allow=192.168.0.1
context=incoming
host=192.168.0.1
[iax-friend]
type=user
secret=this_is_secret
auth=md5
context=incoming
```

यदि कॉल में निर्दिष्ट उपयोगकर्ता नाम है, जैसे:

- guest
- iaxtel
- iax-gateway
- iax-friend

Asterisk केवल iax.conf फ़ाइल में संबंधित प्रविष्टि का उपयोग करके कॉल को प्रमाणित करने का प्रयास करेगा। यदि कोई अन्य नाम निर्दिष्ट किया जाता है, तो कॉल को अस्वीकार कर दिया जाएगा। यदि कोई उपयोगकर्ता निर्दिष्ट नहीं किया गया है, तो Asterisk कनेक्शन को guest के रूप में प्रमाणित करने का प्रयास करेगा। हालांकि, यदि guest मौजूद नहीं है, तो यह मिलते‑जुलते सीक्रेट वाले किसी भी अन्य कनेक्शन को आज़माएगा। दूसरे शब्दों में, यदि आपके iax.conf फ़ाइल में guest सेक्शन नहीं है, तो एक दुर्भावनापूर्ण उपयोगकर्ता उपयोगकर्ता नाम निर्दिष्ट किए बिना किसी भी मिलते‑जुलते सीक्रेट का अनुमान लगाने की कोशिश कर सकता है। IP पतों के deny/allow प्रतिबंध भी लागू होते हैं। सीक्रेट अनुमान से बचने का एक अच्छा तरीका RSA प्रमाणिकरण का उपयोग करना है। एक अन्य विधि यह है कि कॉल करने की अनुमति वाले IP पतों को सीमित किया जाए।

#### IP address restrictions

Access is controlled with `permit` and `deny` lines:

```
permit = <ipaddr>/<netmask>
deny = <ipaddr>/<netmask>
```

नियमों को क्रम में व्याख्यायित किया जाता है, और सभी का मूल्यांकन किया जाता है (यह अवधारणा राउटर और फ़ायरवॉल में आमतौर पर मिलने वाले ACLs से अलग है)। अंतिम मिलते‑जुलते निर्देश पहले वाले को अधिलेखित कर देता है।

उदाहरण #1:

```
permit=0.0.0.0/0.0.0.0
deny=192.168.0.0/255.255.255.0
```

यह 192.168.0.0/24 नेटवर्क से किसी भी पैकेट को अस्वीकार कर देगा।

उदाहरण #2:

```
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

यह किसी भी पैकेट की अनुमति देगा, क्योंकि अंतिम निर्देश पहले वाले को अधिलेखित करता है।

#### आउटबाउंड कनेक्शन

आउटबाउंड कनेक्शन निम्नलिखित तरीकों से प्रमाणीकरण जानकारी प्राप्त करते हैं:

- `dial()` एप्लिकेशन द्वारा पास किया गया IAX2 चैनल विवरण।
- `iax.conf` फ़ाइल में `type=peer` या `type=friend` वाला एंट्री।
- दोनों तरीकों का संयोजन।

#### दो Asterisk सर्वरों को RSA कुंजियों के साथ जोड़ना

असिमेट्रिक RSA कुंजियों का उपयोग करके IAX के साथ मजबूत प्रमाणीकरण संभव है। स्रोत कोड (`res_krypto.c`) के अनुसार, Asterisk संदेश डाइजेस्ट के लिए कमजोर MD5 के बजाय SHA-1 एल्गोरिद्म के साथ RSA कुंजियों का उपयोग करता है। नीचे दो सर्वरों को RSA कुंजियों के साथ सेटअप करने के लिए चरण-दर-चरण मार्गदर्शिका दी गई है।

##### शाखा के लिए सर्वर को कॉन्फ़िगर करना

चरण 1: शाखा सर्वर में RSA कुंजियों को जनरेट करें

```
astgenkey -n
```

जब पूछा जाए, तो कुंजी नाम **branch** का उपयोग करें। हमने पैरामीटर **–n** का उपयोग किया है ताकि Asterisk के पुनः आरंभ होने पर पासफ़्रेज़ न पास करना पड़े। यदि आप सुरक्षा को बेहतर बनाना चाहते हैं, तो **–n** का उपयोग न करें और Asterisk को `asterisk -i` के साथ शुरू करें। **Step 2:** कुंजियों को निर्देशिका **/var/lib/asterisk/keys** में कॉपी करें।

```
cp branch.* /var/lib/asterisk/keys
```

चरण 3: सार्वजनिक कुंजी को HQ सर्वर पर कॉपी करें

```
scp branch.pub root@hq_ip_address:/var/lib/asterisk/keys
```

चरण 4: Branch सर्वर में iax.conf फ़ाइल को संपादित करें।

```
[general]
bindport=4569                   ; bindport and bindaddr may be specified
bindaddr=0.0.0.0                ; more than once to bind to multiple
disallow=all
allow=ulaw
;Create an entry for the HQ server
[hq]
type=user
context=default
host=192.168.2.10
trunk=yes
notransfer=yes
auth=rsa
inkeys=hq
[2200]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2200'
[2201]
type=friend
auth=md5
context=default
secret=password
host=dynamic
callerid='2201'
```

Step 8: ब्रांच सर्वर में extensions.conf फ़ाइल को कॉन्फ़िगर करें

```
 [default]
exten=>_20XX,1,dial(IAX2/branch:[branch]@192.168.2.10/${EXTEN},20)
exten=>_20XX,2,hangup
exten=>_22XX,1,dial(IAX2/${EXTEN},20)
exten=>_22XX,2,hangup
```

##### मुख्यालय के लिए सर्वर को कॉन्फ़िगर करना

चरण 1: HQ सर्वर में RSA कुंजियों को उत्पन्न करें

```
astgenkey -n
```

जब पूछा जाए तो कुंजी नाम **hq** का उपयोग करें। चरण 2: कुंजियों को निर्देशिका **/var/lib/asterisk/keys** में कॉपी करें

```
cp hq.* /var/lib/asterisk/keys
```

चरण 3: सार्वजनिक कुंजी को BRANCH सर्वर पर कॉपी करें

```
scp hq.pub root@branch_ip_address:/var/lib/asterisk/keys
```

# Step 4: HQ सर्वर में iax.conf फ़ाइल को कॉन्फ़िगर करें

```
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw
allow=gsm
;Configure an entry for the branch server
[branch]
type=user
context=default
host=192.168.2.9
trunk=yes
notransfer=yes
auth=rsa
inkeys=branch
[2000]
type=friend
auth=md5
context=default
secret=password
callerid="2000"
host=dynamic
[2001]
type=friend
auth=md5
context=default
secret=password
callerid="2001"
host=dynamic
```

Step 10: HQ सर्वर में extensions.conf फ़ाइल को कॉन्फ़िगर करें।

```
[default]
exten=>_22XX,1,Dial(IAX2/hq:[hq]@192.168.2.9/${EXTEN})
exten=>_22XX,2,hangup
exten=>_20XX,1,Dial(IAX2/${EXTEN})
exten=>_20XX,2,hangup
```

Step 11: Test a call from the 2000 phone in the HQ server to the 2200 phone in the Branch server.

### The iax.conf file configuration

The file iax.conf has several parameters; discussing each parameter one by one would be boring and counterproductive. All parameters, along with a description, can be found in the sample file. In the wiki www.voip-info.org you will find detailed information about each one. Here we will show some of the most important parameters for the configuration of the general section, peers, and users.

#### [General] Section

Server addresses:

- `bindport = <portnum>` — Configures the IAX UDP port. Default is 4569.
- `bindaddr = <ipaddr>` — Use 0.0.0.0 to bind Asterisk to all interfaces, or specify the IP address of a specific interface.

Codec selection:

- `bandwidth = [low|medium|high]` — High = all codecs; Medium = all codecs except ulaw and alaw; Low = low bandwidth codecs.
- `allow/disallow = [alaw|ulaw|gsm|g.729| etc.]` — Codec selection fine tuning.

### Jitter buffer

Jitter is the delay variation between packets. It is the most important factor affecting voice quality. A Jitter buffer is used to compensate for the delay variation. It sacrifices latency in favor of lower jitter. You can make an analogy between the jitter buffer and a water tank. Both can receive packets or water at irregular intervals, but will ultimately deliver a regular flow.

![The jitter buffer as a water tank: packets arrive irregularly from the network and fill the buffer, which then releases them at a steady rate to produce a smooth voice flow. The buffer size (in ms) trades a little latency for lower jitter; the excess-buffer band lets Asterisk grow or shrink the buffer as network conditions change.](../images/10-legacy-fig17.png)

A small jitter (i.e., below 20 ms) is usually imperceptible. However, jitter above this level is annoying. The latency or delay should be kept to below 150ms. Creating a jitter buffer will sacrifice some delay for a lower jitter—a concept known as “delay-budget”. You can affect the jitter buffer using these parameters:

- Jitterbuffer=<yes/no> – Enables or disables
- Dropcount=<number> - Maximum amount of frames that should be delayed in the last two seconds. The recommended setting is 3 (1.5% of dropped frames)
- Maxjitterbuffer=<ms> - Usually below 100 ms
- Maxexcessbuffer=<ms> - If the network delay improves, the jitter buffer could be oversized. Consequently, Asterisk will try to reduce it.
- Minexcessbuffer=<ms> - Once the excess buffer drops to this value, Asterisk starts to increase the buffer size.

### Frame tagging

The parameter below marks the IP packet in the type of service field. Routers can read this tag, thereby prioritizing traffic. Asterisk uses DSCP codes for this field (RFC 2474). Allowed values are CS0, CS1, CS2, CS3, CS4, CS5, CS6, CS7, AF11, AF12, AF13, AF21, AF22, AF23, AF31, AF32, AF33, AF41, AF42, AF43, and ef (i.e., expedited forwarding).

```
tos=ef
```

### IAX2 एन्क्रिप्शन

IAX सममित कुंजी, 128‑बिट ब्लॉक सिफर जिसे AES (Advanced Encryption Standard) कहा जाता है, का उपयोग करके कॉल एन्क्रिप्शन का समर्थन करता है। IAX ट्रंक के बीच एन्क्रिप्शन को सक्रिय करना बहुत सरल है। फ़ाइल iax.conf में उपयोग करें:

```
encryption=yes
```

एन्क्रिप्शन को बाध्य करने के लिए:

```
forceencryption=yes
```

पुराने संस्करणों के साथ संगतता सुनिश्चित करने के लिए, आपको कुंजी घुमाव को निष्क्रिय करने की आवश्यकता हो सकती है, उपयोग करके:

```
keyrotate=no
```

### IAX2 डिबग कमांड

नीचे Asterisk के लिए कुछ सबसे महत्वपूर्ण ट्रबलशूटिंग कंसोल कमांड्स दिए गए हैं।

```
iax2 show netstats
vtsvoffice*CLI> iax2 show netstats
                        -------- LOCAL ---------------------  -------- REMOTE ---------------
-----
Channel           RTT  Jit  Del  Lost   %  Drop  OOO  Kpkts  Jit  Del  Lost   %  Drop  OOO
Kpkts
IAX2/8590-1        16   -1    0    -1  -1     0   -1      1   60  110     3   0     0    0
0
iax2 show channels
vtsvoffice*CLI> iax2 show channels
Channel       Peer             Username    ID (Lo/Rem)  Seq (Tx/Rx)  Lag      Jitter  JitBuf
Format
IAX2/8590-2   8.8.30.43        8590        00002/26968  00004/00003  00000ms  -0001ms  0000ms
unknow
iax2 show peers
vtsvoffice*CLI> iax2 show peers
Name/Username    Host                 Mask             Port          Status
8584             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8564             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8576             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8572             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8571             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8585             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8589             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
8590             8.8.30.43       (D)  255.255.255.255  4569          OK (16 ms)
3232             (Unspecified)   (D)  255.255.255.255  0             UNKNOWN
9 iax2 peers [1 online, 8 offline, 0 unmonitored]
iax2 debug
```

Looking at this output, identify the beginning and end of the call. Observe the delay and jitter information obtained using poke and pong packets. These packets help create the output of the “iax2 show netstats” command.

```
vtsvoffice*CLI> iax2 debug
IAX2 Debugging Enabled
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: REGREQ
   Timestamp: 00003ms  SCall: 26975  DCall: 00000 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: REGAUTH
   Timestamp: 00009ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 137472844
   USERNAME        : 8590
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: REGREQ
   Timestamp: 00016ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
   USERNAME        : 8590
   REFRESH         : 60
   MD5 RESULT      : f772b6512e77fa4a44c2f74ef709e873
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: REGACK
   Timestamp: 00025ms  SCall: 00003  DCall: 26975 [8.8.30.43:4569]
   USERNAME        : 8590
   DATE TIME       : 2006-04-17  16:03:00
   REFRESH         : 60
   APPARENT ADDRES : IPV4 8.8.30.43:4569
   CALLING NUMBER  : 4830258590
   CALLING NAME    : Flavio
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00025ms  SCall: 26975  DCall: 00003 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: POKE
   Timestamp: 00003ms  SCall: 00006  DCall: 00000 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: PONG
   Timestamp: 00003ms  SCall: 26976  DCall: 00006 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Tx-Frame Retry[-01] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00006  DCall: 26976 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[000] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: AUTHREQ
   Timestamp: 00007ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   AUTHMETHODS     : 2
   CHALLENGE       : 190271661
   USERNAME        : 8590
Rx-Frame Retry[Yes] -- OSeqno: 000 ISeqno: 000 Type: IAX     Subclass: NEW
   Timestamp: 00003ms  SCall: 26977  DCall: 00000 [8.8.30.43:4569]
   VERSION         : 2
   CALLING NUMBER  : 8590
   CALLING NAME    : 4830258590
   FORMAT          : 2
   CAPABILITY      : 1550
   USERNAME        : 8590
   CALLED NUMBER   : 8580
   DNID            : 8580
Tx-Frame Retry[-01] -- OSeqno: 000 ISeqno: 001 Type: IAX     Subclass: ACK
   Timestamp: 00003ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 001 ISeqno: 001 Type: IAX     Subclass: AUTHREP
   Timestamp: 00063ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   MD5 RESULT      : 57cc5c48affba14106c29439944413a1
Tx-Frame Retry[000] -- OSeqno: 001 ISeqno: 002 Type: IAX     Subclass: ACCEPT
   Timestamp: 00054ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   FORMAT          : 1024
Tx-Frame Retry[000] -- OSeqno: 002 ISeqno: 002 Type: CONTROL Subclass: ANSWER
   Timestamp: 00057ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 003 ISeqno: 002 Type: VOICE   Subclass: 138
   Timestamp: 00090ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 002 Type: IAX     Subclass: ACK
   Timestamp: 00054ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00057ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: IAX     Subclass: ACK
   Timestamp: 00090ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 002 ISeqno: 004 Type: VOICE   Subclass: 138
   Timestamp: 00210ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[-01] -- OSeqno: 004 ISeqno: 003 Type: IAX     Subclass: ACK
   Timestamp: 00210ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 003 ISeqno: 004 Type: IAX     Subclass: PING
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Tx-Frame Retry[000] -- OSeqno: 004 ISeqno: 004 Type: IAX     Subclass: PONG
   Timestamp: 02083ms  SCall: 00004  DCall: 26977 [8.8.30.43:4569]
   RR_JITTER       : 0
   RR_LOSS         : 0
   RR_PKTS         : 1
   RR_DELAY        : 40
   RR_DROPPED      : 0
   RR_OUTOFORDER   : 0
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: ACK
   Timestamp: 02083ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
Rx-Frame Retry[ No] -- OSeqno: 004 ISeqno: 005 Type: IAX     Subclass: HANGUP
   Timestamp: 08693ms  SCall: 26977  DCall: 00004 [8.8.30.43:4569]
   CAUSE           : Dumped Call
```

डिबगिंग बंद करने के लिए, उपयोग करें:

```
vtsvoffice*CLI>iax2 no debug
```

### Summary

इस अध्याय में IAX प्रोटोकॉल की ताकतों और कमजोरियों की समीक्षा की गई है। यह दर्शाया गया है कि IAX कई परिदृश्यों में कैसे काम करता है, जैसे सॉफ्टफ़ोन और दो Asterisk सर्वरों के बीच एक ट्रंक। ट्रंक मोड आपको एक ही पैकेट में एक से अधिक कॉल ले जाकर बैंडविड्थ बचाने की अनुमति देता है। अंत में, आपने कंसोल कमांड सीखे जो आप प्रोटोकॉल की स्थिति जांचने और डिबग करने के लिए उपयोग कर सकते हैं।

## Legacy SIP: chan_sip and sip.conf (removed in Asterisk 21+)

> **Legacy / historical:** इस सेक्शन में सब कुछ पुरानी `chan_sip` ड्राइवर और उसकी `sip.conf` कॉन्फ़िगरेशन फ़ाइल का उपयोग करता है। `chan_sip` कई रिलीज़ों के लिए डिप्रिकेट किया गया था और **Asterisk 21 में हटा दिया गया**, इसलिए यह **Asterisk 22 में मौजूद नहीं है**। नीचे दिए गए `sip.conf` उदाहरण वर्तमान सिस्टम पर नहीं चलेंगे — इन्हें केवल यह दस्तावेज़ करने के लिए रखा गया है कि लेगेसी डिप्लॉयमेंट कैसे काम करते थे और आपको उन्हें माइग्रेट करने में मदद करने के लिए। आधुनिक, समर्थित तरीका देखने के लिए *PJSIP: the SIP channel* सेक्शन देखें *SIP & PJSIP in depth* अध्याय में। SIP *protocol* सिद्धांत (methods, registration, proxy/redirect, SDP, NAT types) प्रोटोकॉल‑लेवल का है और उस अध्याय में रहता है; इसके बाद केवल हटाए गए `chan_sip` **configuration** का विवरण है।

लेगेसी सिस्टम में Asterisk 20 तक, SIP को `/etc/asterisk/sip.conf` में कॉन्फ़िगर किया जाता था, जो दूसरे सबसे अधिक बदले जाने वाली फ़ाइल थी (केवल `extensions.conf` के बाद)। नीचे के सेक्शन दिखाते हैं कि `chan_sip` ने Asterisk को SIP प्रोवाइडर से कैसे जोड़ा, दो Asterisk को SIP के माध्यम से कैसे कनेक्ट किया, डोमेन सपोर्ट, प्रेज़ेंस, कोडेक/DTMF/QoS विकल्प, ऑथेंटिकेशन, और NAT — और फिर सभी को PJSIP में माइग्रेट करने के लिए एक गाइड।

### Connecting Asterisk to a SIP provider (sip.conf)

Asterisk अक्सर एक SIP VoIP प्रोवाइडर से कनेक्ट करने के लिए उपयोग किया जाता है। VoIP प्रोवाइडर आमतौर पर पारंपरिक प्रोवाइडर की तुलना में कॉल रेट्स में बेहतर होते हैं। VoIP प्रोवाइडर का एक और रोचक और आकर्षक पहलू यह है कि आप अन्य शहरों—या यहाँ तक कि विदेशी देशों—में DID नंबर खरीद सकते हैं। ये सभी कारण टेलीकॉम्यूनिकेशन्स के लिए VoIP उपयोग करने के अच्छे कारण हैं। इस सेक्शन में, आप सीखेंगे कि लेगेसी `chan_sip` ने Asterisk को एक VoIP प्रोवाइडर से कैसे जोड़ा। Asterisk को SIP प्रोवाइडर से कनेक्ट करने के लिए तीन चरण आवश्यक हैं। परीक्षण आपके पसंदीदा प्रोवाइडर के साथ एक अकाउंट स्थापित करके किए जा सकते हैं।  
Step 1: Registering with a SIP provider in sip.conf  
SIP प्रोवाइडर से कनेक्ट करने के लिए, आपको प्रोवाइडर से निम्नलिखित जानकारी चाहिए:

![Asterisk connected to a VoIP service provider over the Internet or a private WAN, with local SIP phones registered to the Asterisk server](../images/07-sip-and-pjsip-fig07.png)

- username
- secret and remotesecret (इनबाउंड अनुरोधों को ऑथेंटिकेट करने के लिए secret और आउटबाउंड अनुरोधों के लिए remotesecret का उपयोग करें)
- hostname
- domain
- codecs allowed

यह कॉन्फ़िगरेशन आपके प्रोवाइडर को Asterisk का IP पता खोजने में सक्षम करेगा। अगले कथन में, हम Asterisk को बताते हैं कि वह hostname द्वारा परिभाषित SIP प्रोवाइडर में रजिस्टर करे और प्रोवाइडर को Asterisk का IP पता सूचित करे। यह कथन बताता है कि आप एक्सटेंशन 4100 पर कॉल प्राप्त करना चाहते हैं। sip.conf फ़ाइल के [general] सेक्शन में, निम्नलिखित लाइन दर्ज करें:

```
register=>name:secret@hostname/4100
```

चरण 2: sip.conf पर [peer] को कॉन्फ़िगर करें वांछित प्रदाता के लिए peer प्रकार का एक एंट्री बनाएं ताकि Asterisk की डायलिंग सरल हो सके।

```
[provider]
context=incoming
type=friend
dtmfmode=rfc2833
directmedia=no
username=username
remotesecret=secret
host=hostname
fromuser=username
fromdomain=domain
insecure=invite
disallow=all
allow=ulaw ; or any other codec available from your provider
```

Step 3: Create a route to the provider in the dial plan  
हम डायल प्लान में प्रोवाइडर के लिए एक रूट बनाएँगे। हम गंतव्य रूट के रूप में अंक 010 चुनेंगे।  
प्रोवाइडर के भीतर #610000 डायल करने के लिए, बस 010610000 डायल करें।

```
exten=>_010.,1,Set(CALLERID(num)=username)
exten=>_010.,n,Set(CALLERID(Name)="Flavio Gonçalves")
exten=>_010.,n,Dial(SIP/${EXTEN:3}@provider)
exten=>_010.,n,Hangup
```

#### प्रदाता परिदृश्य के लिए विशिष्ट SIP विकल्प

निम्नलिखित चर्चा VoIP प्रदाता से कनेक्शन के लिए sip.conf फ़ाइल में सेट किए गए विकल्पों के विवरण की जांच करती है।

```
register=>username:password@hostname/4100
```

sip.conf फ़ाइल में पंजीकृत निर्देश का उपयोग प्रोवाइडर के साथ रजिस्टर करने के लिए किया जाता है। रजिस्टर लेन‑देन को नाम और सीक्रेट द्वारा प्रमाणित किया जाता है। आप स्लैश (“/”) का उपयोग करके इनकमिंग कॉल्स के लिए एक एक्सटेंशन प्रदान कर सकते हैं। तकनीकी रूप से, एक्सटेंशन SIP अनुरोध के “Contact” हेडर फ़ील्ड में रखा जाएगा। पंजीकरण व्यवहार को कुछ पैरामीटरों द्वारा नियंत्रित किया जा सकता है:

```
registertimeout=20
registerattempts=10
```

To check if registration was successful, the legacy console command was `sip show registry`. On Asterisk 22 the equivalent command is `pjsip show registrations` (outbound registrations) and `pjsip show endpoints` for endpoint status.

The parameter “username” is used in the authentication digest. The digest is computed using username, secret, and realm:

```
username=username
```

होस्ट VoIP प्रदाता का पता या नाम निर्धारित करता है:

```
host=hostname
```

पैरामीटर Fromuser और Fromdomain कभी‑कभी प्रमाणीकरण के लिए आवश्यक होते हैं। इन पैरामीटरों का उपयोग SIP From हेडर फ़ील्ड में किया जाता है:

```
fromuser=username
fromdomain=hostname
```

जब आप किसी VoIP प्रदाता से कनेक्ट होते हैं, तो प्रमाणपत्र (credentials) आवश्यक होते हैं। प्रारंभिक invite के बाद, प्रदाता आपको “407 Proxy Authentication Required” नामक एक संदेश भेजता है; आप अगले INVITE संदेश में प्रमाणपत्र प्रदान करते हैं। इनकमिंग कॉल्स के लिए, आपका Asterisk सर्वर प्रदाता से प्रमाणपत्र माँगेगा। स्पष्ट रूप से, प्रदाता के पास आपके Asterisk सर्वर के लिए वैध प्रमाणपत्र नहीं होता। जब आप `insecure=invite` का उपयोग करते हैं, तो आप Asterisk को यह बताते हैं कि वह “407 Proxy Authentication Required” को प्रदाता को न भेजे और इनकमिंग कॉल्स को स्वीकार करे। आप `insecure=port,invite` का उपयोग भी कर सकते हैं ताकि पोर्ट नंबर से मेल न खाते हुए IP पते के आधार पर पीयर से मेल खा सके।

```
insecure=invite, port
```

### SIP (sip.conf) का उपयोग करके दो Asterisk सर्वरों को जोड़ना

आप SIP का उपयोग करके दो Asterisk बॉक्सों को आपस में जोड़ सकते हैं। इस कॉन्फ़िगरेशन को आगे बढ़ाने से पहले डायल प्लान पर ध्यान देना महत्वपूर्ण है। उपयोगकर्ता आमतौर पर न्यूनतम प्रयास से अन्य PBX को कनेक्ट करना चाहते हैं। यहाँ विचार यह है कि केवल एक एक्सटेंशन नंबर का उपयोग करके दूसरे PBX से जुड़ें। Step 1: Edit the sip.conf file in server A:

```
[B]
type=user
secret=B
host=A
disallow=all
allow=ulaw
directmedia=no
[B-out]
type=peer
fromuser=A
username=A
remotesecret=A
host=B
disallow=all
allow=ulaw
directmedia=no
```

Step 2: Edit the sip.conf file in server B:

```
[A]
type=user
host=B
secret=A
disallow=all
allow=ulaw
directmedia=no
[A-out]
```

![SIP का उपयोग करके दो Asterisk सर्वरों को जोड़ना: सर्वर A (एक्सटेंशन 4400/4401) और सर्वर B (एक्सटेंशन 4500/4501) SIP सिग्नलिंग का आदान-प्रदान करते हैं ताकि प्रत्येक PBX के उपयोगकर्ता दूसरे को डायल कर सकें](../images/07-sip-and-pjsip-fig08.png)

```
type=peer
host=A
fromuser=B
username=B
remotesecret=B
disallow=all
allow=ulaw
directmedia=no
```

Step 3: Edit the extensions.conf file in server A: → चरण 3: सर्वर A में extensions.conf फ़ाइल को संपादित करें।

```
[default]
exten=_44XX,1,dial(SIP/${EXTEN},20)
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/B-out/${EXTEN})
exten=_45XX,2,hangup()
```

Step 4: सर्वर B में extensions.conf फ़ाइल को संपादित करें:

```
[default]
exten=_44XX,1,dial(SIP/A-out/${EXTEN})
exten=_44XX,2,hangup()
exten=_45XX,1,dial(SIP/${EXTEN})
exten=_45XX,2,hangup()
```

### Asterisk डोमेन समर्थन (sip.conf)

SIP प्रोटोकॉल इंटरनेट आर्किटेक्चर का पालन करता है। SIP को कॉन्फ़िगर करने से पहले करने वाली पहली बात DNS सर्वरों को सही तरीके से सेट करना है। एक SIP वातावरण में, आप किसी भी SIP प्रॉक्सी में स्थित उपयोगकर्ता को कॉल कर सकते हैं, और अन्य उपयोगकर्ता भी आपके SIP Uniform Resource Identifier (URI) का उपयोग करके आपको कॉल कर सकते हैं। SIP के लिए DNS सर्वर सेट करने हेतु, आपको अपने DNS सर्वर में SRV रिकॉर्ड जोड़ने होंगे।

```
; SIP server/proxy and its backup server/proxy
sip1.yourdomain.com
21600 IN A
200.180.4.169
sip2.yourdomain.com
21600 IN A
200.175.61.150
;
; DNS SRV records for SIP
_sip._udp.yourdomain.com  21600 IN SRV 10 0 5060 sip1.voip.school.
_sip._udp.yourdomain.com  21600 IN SRV 20 0 5060 sip2.voip.school.
```

DNS को कॉन्फ़िगर करने के बाद, आप URI का उपयोग कर सकते हैं, जो एक SIP उपयोगकर्ता, SIP फ़ोन, या टेलीफ़ोन एक्सटेंशन की ओर इशारा करता है। एक SIP URI ई‑मेल पते के समान दिखता है (उदाहरण के लिए, sip:chuck@yourpartnerdomain.com)। SIP URI का उपयोग करके, एक SIP फ़ोन से दूसरे SIP फ़ोन पर कॉल करने के लिए कोई टेलीफ़ोन नंबर आवश्यक नहीं होता। बाहरी उपयोगकर्ता को डायल करने के लिए, नीचे दिखाए गए समान कथन का उपयोग करें।

```
exten=4000,1,dial(SIP/chuck@yourpartnerdomain.com)
```

कुछ पैरामीटर डोमेन व्यवहार को नियंत्रित कर सकते हैं।

```
srvlookup=yes
```

यह पैरामीटर आउटबाउंड कॉल्स पर DNS SRV लुकअप को सक्षम करता है। इस पैरामीटर का उपयोग करके, डोमेन के आधार पर SIP नामों का उपयोग करके कॉल डायल करना संभव है।

```
allowguest=yes
```

यह पैरामीटर बाहरी इनवाइट को बिना प्रमाणीकरण के प्रोसेस करने की अनुमति देता है। यह कॉल को सामान्य सेक्शन या डोमेन स्टेटमेंट में परिभाषित कॉन्टेक्स्ट के भीतर प्रोसेस करता है। चेतावनी: यदि आप सामान्य सेक्शन में PSTN तक पहुँच वाले कॉन्टेक्स्ट को परिभाषित करते हैं, तो एक बाहरी उपयोगकर्ता आपके PBX के माध्यम से PSTN डायल कर सकता है। इस स्थिति में, आपको कोई भी शुल्क लग सकता है। सामान्य सेक्शन में परिभाषित कॉन्टेक्स्ट में केवल अपने स्वयं के एक्सटेंशन की अनुमति दें।

![डोमेन द्वारा अन्य SIP सर्वरों से कनेक्ट करना: youdomain.com और yourpartnerdomain.com SIP सिग्नलिंग का आदान‑प्रदान करते हैं, इसलिए lee और bruce जैसे उपयोगकर्ता SIP URIs का उपयोग करके chuck और norris को कॉल कर सकते हैं](../images/07-sip-and-pjsip-fig09.png)

```
domain=acme.com,default
```

डोमेन कमांड आपको Asterisk के भीतर एक से अधिक डोमेन को संभालने की अनुमति देता है। यदि कोई कॉल किसी विशिष्ट डोमेन से आती है, तो उसे एक विशिष्ट कॉन्टेक्स्ट की ओर निर्देशित किया जाता है।

```
;autodomain=yes
```

यह पैरामीटर अनुमत डोमेनों में स्थानीय IP और होस्टनेम को शामिल करता है।

```
;allowexternaldomains=no
```

The default is yes. Uncomment the line to disallow calls to outside domains.

### SIP advanced configurations (sip.conf)

This section explains some advanced parameters of the legacy SIP channel, such as presence, codec selection, DTMF options, and QoS packet marking. The **concepts** (BLF/presence, codec negotiation, DTMF modes, DSCP marking) carry over to PJSIP, but the `sip.conf` parameter names shown here do **not** exist in Asterisk 22. On PJSIP, DTMF mode is `dtmf_mode=` on an endpoint, and codecs are set with `allow=`/`disallow=`.

#### SIP Presence

SIP presence is partially implemented in Asterisk. Asterisk supports requests such as SUBSCRIBE and NOTIFY users depending on the state of a channel. Asterisk does not support the SIP method PUBLISH. In other words, you can subscribe to the states (busy, idle, and ringing) of a channel, but cannot publish information such as “away” or “do not disturb”. The most common scenario for presence is busy lamp field (BLF), in which you simulate the behavior of a KS system with lamps for each extension and trunk. SIP parameters for presence:

- allowsubscribe=yes: Allow SIP subscription methods
- subscribecontext=sip_subscribers: Context where to look for hints
- notifyring=yes: Send SIP NOTIFY on ring
- notifyhold=yes: Send SIP NOTIFY on hole
- counteronpeer (renamed from limitonpeer for Asterisk 1.4.x): Apply the counter only on the peer side
- callcounter=yes: Enable call counters in the device.
- busylevel=1: Threshold for the number of calls for considering the device as busy.

For example: Step 1: Testing SIP presence with Asterisk is not that hard. First, let’s configure the files sip.conf and extensions.conf.

In the file sip.conf

```
[general]
bindaddr=0.0.0.0
bindport=5060
disallow=all
allow=ulaw
allowsubscribe=yes
notifyringing=yes
notifyhold=yes
limitonpeer=yes
counteronpeer=yes
subscribecontext=default
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
[2001]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
secret=senha
callcounter=yes
busylevel=1
In the file extensions.conf
[default]
exten=2000,hint,SIP/2000
exten=2001,hint,SIP/2001
exten=_20XX,1,dial(SIP/${EXTEN})
exten=_20XX,n,Hangup()
```

Step 2: अब सॉफ्टफ़ोन को प्रेज़ेंस उपयोग करने के लिए कॉन्फ़िगर करें। हम आपको दिखाएंगे कि SipPulse Softphone को कैसे कॉन्फ़िगर किया जाता है।

- Sequence: right-click->SIP Account Settings->Properties->Presence
- Presence मॉडल को peer-to-peer से presence agent में बदलें, जिससे सॉफ्टफ़ोन Asterisk को SIP इवेंट्स के लिए सब्सक्राइब करेगा।

Step 3: अन्य सॉफ्टफ़ोन में संपर्क जोड़ें। इस उदाहरण में, SipPulse Softphone खाता 2000 है, इसलिए हम खाता 2001 के लिए एक संपर्क जोड़ेंगे। Sequence: Open the right panel (presence panel in the softphone)->Click in Contacts->Add a contact. Fill the name 2001. Display as 2001 and don’t forget to check the box Show this contact’s availability.

Step 4: अब एक्सटेंशन 2001 को कॉल करें और सॉफ्टफ़ोन के दाएँ पैनल में फोन की स्थिति जांचें। सर्वर में प्रेज़ेंस स्थिति बदलते देखना है तो कंसोल कमांड `core show hints` का उपयोग करें (legacy chan_sip में, `sip show inuse` दिखाता था कि प्रत्येक लाइन पर कितनी कॉल्स थीं)। Asterisk 22 पर, endpoint और channel स्थिति जांचने के लिए `pjsip show endpoints` का उपयोग करें। प्रेज़ेंस/BLF स्थिति सॉफ्टफ़ोन के contacts या BLF पैनल में दिखाई देती है — यह क्लाइंट पर निर्भर करता है कि यह कैसे दिखाया जाता है।

#### Codec configuration

Codec configuration सरल और सीधा है। आप [general] सेक्शन या peer/user सेक्शन में शब्द allow और disallow सेट कर सकते हैं। सर्वोत्तम अभ्यास यह है कि ट्रांसकोडिंग से बचने के लिए codec को मानकीकृत किया जाए, क्योंकि यह प्रोसेसर‑इंटेन्सिव होता है। कृपया संदेशों और प्रॉम्प्ट्स के लिए एक ही codec उपयोग करें।

```
[general]
disallow=all
allow=g729
```

#### DTMF विकल्प

कुछ स्थितियों में, आप voicemail या interactive voice response (IVR) जैसे एप्लिकेशन को अंक पास करेंगे। DTMF को सही तरीके से पास करना महत्वपूर्ण है। DTMF पास करने की सबसे सरल विधि को inband कहा जाता है। इसे sip.conf फ़ाइल के [general] या peer/user सेक्शन में सेट किया जाता है। जब आप dtmfmode=inband सेट करते हैं, तो DTMF टोन ऑडियो चैनल में ध्वनि के रूप में उत्पन्न होते हैं। इस विधि की मुख्य समस्या यह है कि जब आप ऑडियो चैनल को g729 जैसे कोडेक से संपीड़ित करते हैं, तो ध्वनि विकृत हो जाती है और DTMF टोन सही ढंग से पहचाने नहीं जाते। यदि आप dtmfmode=inband का उपयोग करने की योजना बना रहे हैं, तो g.711 कोडेक (ulaw और alaw) का उपयोग करें।

```
dtmfmode=inband
```

एक और तरीका है RFC2833 का उपयोग करना, जो आपको RTP पैकेटों में नामित घटनाओं के रूप में DTMF टोन पास करने की अनुमति देता है।

```
dtmfmode=rfc2833
```

अंत में, आप RTP पैकेट्स के बजाय SIP पैकेट्स के भीतर DTMF अंकों को पास कर सकते हैं। यह विधि RFC3265 (signaling events) और RFC2976 में परिभाषित है।

```
dtmfmode=info
```

संस्करण 1.2 के रिलीज़ के बाद, अब यह संभव है कि उपयोग किया जाए:

```
dtmfmode=auto
```

यह RFC2833 का उपयोग करने का प्रयास करता है; यदि यह संभव नहीं है, तो बैंड टोन का उपयोग करें।

#### Quality of service (QoS) marking configuration

QoS आवाज़ की गुणवत्ता के लिए जिम्मेदार तकनीकों का एक सेट है। QoS इस तरह लागू किया जाता है कि बैंडविड्थ, लेटेंसी, और जिटर को कम किया जा सके। मुख्य QoS कार्य हैं पैकेट शेड्यूलिंग, फ्रैगमेंटेशन, और हेडर कम्प्रेशन। QoS स्विच और राउटर में लागू किया जाता है, न कि Asterisk में। हालांकि, Asterisk राउटर और स्विच को पैकेट को तेज़ डिलीवरी के लिए मार्क करके मदद कर सकता है। मार्किंग को डिफरेंशिएटेड सर्विसेज कोड पॉइंट्स (DSCP) का उपयोग करके किया जाता है, जो RFCs 2474 और RFC2475 में परिभाषित हैं।

```
tos_sip=cs3
tos_audio=ef
tos_video=af41
```

Starting from version 1.4, you can specify different codes for signaling (SIP), audio (RTP), and video (RTP).

### SIP authentication (sip.conf)

When legacy `chan_sip` received a SIP call, it followed the rules described in the following diagram. Three parameters played an important role in SIP authentication. On Asterisk 22, authentication is configured instead with PJSIP `auth` objects (`type=auth`, `auth_type=userpass`, `username=`, `password=`) referenced by an endpoint, and IP access control is done with `permit=`/`deny=` on the endpoint or via an `acl`.

![Legacy chan_sip authentication decision flow: Asterisk checks the From header against sip.conf, tries the matching type=user/peer section and MD5 credentials, and falls back to insecure=invite or allowguest before allowing or denying the call](../images/07-sip-and-pjsip-fig10.png)

```
allowguest=yes/no
```

यह पैरामीटर नियंत्रित करता है कि क्या एक उपयोगकर्ता जिसके पास संबंधित पीयर नहीं है, बिना नाम और सीक्रेट के प्रमाणित हो सकता है। हमने इस पैरामीटर पर डोमेन समर्थन अनुभाग में चर्चा की थी।

```
insecure=invite,port
```

जब हम insecure=invite का उपयोग करते हैं, Asterisk “407 Proxy Authentication Required” संदेश उत्पन्न नहीं करता। इस संदेश के बिना, उपयोगकर्ता बिना प्रमाणीकरण के कॉल कर सकता है। यह अक्सर VoIP सेवा प्रदाताओं से कनेक्ट करने के लिए उपयोग किया जाता है। VoIP सेवा प्रदाता से आने वाली कॉलें आमतौर पर प्रमाणित नहीं होतीं।

```
autocreatepeer=yes/no
```

यह कमांड तब उपयोग किया जाता है जब Asterisk को एक SIP प्रॉक्सी से जोड़ा जाता है। यह प्रत्येक कॉल के लिए गतिशील रूप से एक peer बनाता है। जब यह विकल्प सक्षम किया जाता है, तो कोई भी UAC Asterisk सर्वर से कनेक्ट हो सकता है। SIP प्रॉक्सी के लिए IP कनेक्शन को सीमित करना महत्वपूर्ण है। SIP प्रॉक्सी, बदले में, एक्सेस कंट्रोल का ध्यान रखता है। Peer कॉन्फ़िगरेशन सामान्य विकल्पों और SIP पैकेट के “Contact” हेडर फ़ील्ड दोनों पर आधारित होता है। चेतावनी: इसे अत्यधिक सावधानी के साथ उपयोग करें क्योंकि यह Asterisk को पूरी तरह से खोल देता है।

```
secret=secret, remotesecret=secret
```

यह पैरामीटर प्रमाणीकरण के लिए secret को कॉन्फ़िगर करता है; इनबाउंड अनुरोधों के लिए secret और आउटबाउंड अनुरोधों के लिए remotesecret का उपयोग करें। यदि आप टेक्स्ट फ़ाइलों में secrets को प्रदर्शित नहीं करना चाहते हैं, तो आप md5secret का उपयोग करके secret के बजाय एक हैश शामिल कर सकते हैं। MD5 secret उत्पन्न करने के लिए, आप उपयोग कर सकते हैं:

```
echo -n "username:realm:secret" |md5sum
```

--- BEGIN MARKDOWN ---
फिर निम्नलिखित कथन का उपयोग करें:
--- END MARKDOWN ---

```
md5secret=0b0e5d467890....
```

Warning: –n पैरामीटर का उपयोग करना न भूलें; कैरिज रिटर्न md5 गणना में उपयोग किया जाएगा।

```
deny=0.0.0.0/0.0.0.0
permit=192.168.1.0/255.255.255.0
```

The statements above will deny all IP addresses and allow UAC only from the local network (192.168.1.0/24).

#### RTP विकल्प

It is possible to control some RTP parameters.

```
rtptimeout=60
```

यह कॉल को समाप्त कर देता है जब होल्ड में नहीं होते और RTP गतिविधि 60 सेकंड से अधिक नहीं होती।

```
rtpholdtimeout=120
```

This terminates calls without RTP activity even on hold (should be bigger than rtptimeout).

### SIP NAT traversal (sip.conf)

The NAT *theory* (the four NAT types, the Contact-header problem, keep-alives, and forcing media through the server) is protocol-level and is covered in the *SIP & PJSIP in depth* chapter. The `sip.conf` parameters shown here (`nat=`, `qualify=`, `directmedia=`, `externaddr=`, `localnet=`) are **legacy chan_sip** and were removed in Asterisk 21+. On PJSIP these map to transport/endpoint settings such as `rewrite_contact=yes`, `force_rport=yes`, `rtp_symmetric=yes`, `direct_media=no`, `external_media_address`, `external_signaling_address`, and `local_net=` on the transport, plus `qualify_frequency=` on the AOR.

In legacy chan_sip, the parameter `nat` had five options:

- nat = no — Do no special NAT handling other than RFC3581
- nat = force_rport — Pretend there was an rport parameter even if there wasn't
- nat = comedia — Send media to the port Asterisk received it from regardless of where the SDP says to send it.
- nat = auto_force_rport — Set the force_rport option if Asterisk detects NAT (default)
- nat = auto_comedia — Set the comedia option if Asterisk detects NAT

When you put the statement “nat=force_rport” in the sip.conf file, you are telling Asterisk to ignore the address contained in the “Contact” header field of the SIP header and use the source IP address and port in the packet’s IP header and also to send the media back to the address from where it was received ignoring the content of the SDP header.

```
nat=force_rport,comedia
```

It is necessary to keep the NAT mapping open. If NAT times out, Asterisk cannot send an invite to the UAC. The UAC is able to send calls, but not receive any. The following statement can be used to keep NAT open.

```
qualify=yes
```

Qualify नियमित रूप से OPTIONS मेथड का उपयोग करके एक SIP पैकेट भेजेगा, जो NAT को खुला रखने में मदद करेगा। Qualify प्रत्येक 60 सेकंड में और जब होस्ट पहुँच योग्य न हो तो हर 10वें सेकंड में एक OPTIONS भेजता है। आप “sip show peers” का उपयोग करके peers की latency देख सकते हैं। यदि उपयोगकर्ता का NAT सममित प्रकार का है, तो एक UAC से दूसरे UAC को सीधे पैकेट भेजना संभव नहीं है; ऐसे में आपको RTP को Asterisk के माध्यम से मजबूर करना होगा:

```
directmedia=no
```

#### Asterisk behind NAT (sip.conf)

All the previous scenarios assume that the Asterisk server has an external (valid) Internet address. Sometimes the Asterisk server is implemented behind a firewall with NAT. In this case, it is necessary to do some extra configurations.

![Asterisk behind NAT: a firewall maps the public address 200.180.4.168 to the internal Asterisk server (192.168.1.100), forwarding SIP on UDP 5060 and the RTP range UDP 10000–20000 defined in rtp.conf](../images/07-sip-and-pjsip-fig13.png)

1. फ़ायरवॉल को कॉन्फ़िगर करें ताकि UDP पोर्ट 5060 स्थैतिक रूप से Asterisk सर्वर की ओर रीडायरेक्ट हो।
2. फ़ायरवॉल को कॉन्फ़िगर करें ताकि UDP पोर्ट 10000 से 20000 तक स्थैतिक रूप से रीडायरेक्ट हों।

यदि आप खुले पोर्टों की संख्या को सीमित करना चाहते हैं, तो आप `rtp.conf` फ़ाइल को संपादित करके RTP पोर्ट रेंज बदल सकते हैं। एक अन्य तरीका यह है कि आप एक इंटेलिजेंट फ़ायरवॉल का उपयोग करें जो SIP प्रोटोकॉल को सपोर्ट करता हो और RTP पोर्ट को डायनामिक रूप से खोलता हो।

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

Step 3: Asterisk को इस तरह कॉन्फ़िगर करें कि वह SIP पैकेटों के हेडर फ़ील्ड्स में, जिसमें Session Description Protocol (SDP) भी शामिल है, बाहरी पता जोड़ दे। आप यह `sip.conf` फ़ाइल में निम्न दो कथनों को जोड़कर कर सकते हैं:

```
externaddr=200.180.4.168
;External IP address
localnet=192.168.1.0/255.255.255.0
;Internal Network Address
nat=force_rport,comedia
```

पहला पैरामीटर `externaddr` Asterisk को बाहरी गंतव्यों के लिए SIP हेडर्स में बाहरी IP पता शामिल करने के लिए बताता है। दूसरा पैरामीटर `localnet` Asterisk को बाहरी और आंतरिक पतों के बीच अंतर करने में सक्षम बनाता है। वैकल्पिक रूप से, यदि आप सर्वर पर DHCP पते के साथ एक डायनामिक DNS का उपयोग करते हैं तो आप `externhost` का उपयोग कर सकते हैं।

### SIP डायल स्ट्रिंग्स (chan_sip)

नीचे दिखाया गया `SIP/...` डायल-स्ट्रिंग तकनीक हटाए गए `chan_sip` ड्राइवर का प्रतिनिधित्व करता है। Asterisk 22 में इसके बजाय `PJSIP/...` तकनीक का उपयोग करें — उदाहरण के लिए `Dial(PJSIP/2000)` या `Dial(PJSIP/${EXTEN}@provider)`। फ़ॉर्म और अर्थ अन्यथा समान हैं।

आप विभिन्न डायल स्ट्रिंग्स का उपयोग करके एक लेगेसी SIP गंतव्य को कॉल कर सकते हैं:

```
SIP/peer
```

- ; sip.conf में एक परिभाषित पीयर होना आवश्यक है

```
SIP/flavio@voffice.com.br ; By the URI
SIP/[exten@]peer[:portno]
SIP/[user:password@domain/extension
```

उदाहरण शामिल हैं:

```
exten=>s,1,Dial(SIP/ipphone)
exten=>s,1,Dial(SIP/info@voffice.com.br)
exten=>s,1,Dial(SIP/192.168.1.8:5060,20)
exten=>s,1,Dial(SIP/8500@sip.com:9876)
```

## Legacy chan_sip सिस्टम को PJSIP में माइग्रेट करना

क्योंकि `chan_sip` को Asterisk 21 में हटा दिया गया था और Asterisk 22 में यह मौजूद नहीं है, किसी भी मौजूदा `sip.conf` डिप्लॉयमेंट को PJSIP में माइग्रेट करना आवश्यक है। सबसे बड़ा अवधारणात्मक बदलाव यह है कि एकल `sip.conf` `[peer]` या `[friend]` को कई PJSIP ऑब्जेक्ट्स में विभाजित किया जाता है, प्रत्येक के पास एक `type=` होता है: एक **endpoint** (कॉल/कोडेक/मीडिया सेटिंग्स), एक या अधिक **aor** ऑब्जेक्ट्स (जहाँ डिवाइस पहुँचा जा सकता है / रजिस्ट्रेशन), एक **auth** ऑब्जेक्ट (क्रेडेंशियल्स), और एक साझा **transport** (लिसनिंग सॉकेट, NAT एड्रेस)। नीचे दिया गया टेबल सबसे सामान्य अवधारणाओं का मानचित्रण करता है।

| Legacy sip.conf concept | PJSIP equivalent (pjsip.conf) |
| --- | --- |
| `[peer]` / `[friend]` ब्लॉक | `type=endpoint` + `type=aor` + `type=auth` (`auth=` और `aors=` के माध्यम से संदर्भित) |
| `type=friend` / `type=peer` / `type=user` | एकल `type=endpoint` (PJSIP में कोई friend/peer/user अंतर नहीं) |
| `host=dynamic` (डिवाइस रजिस्टर करता है) | `type=aor` के साथ `max_contacts=1`; डिवाइस अपने कॉन्टैक्ट को अपडेट करने के लिए REGISTER करता है |
| `host=<ip/hostname>` (स्थिर) | `type=aor` के साथ एक स्थिर `contact=sip:host:port` |
| `register=>user:secret@host/ext` (आउटबाउंड) | `type=registration` (`server_uri=`, `client_uri=`, `outbound_auth=`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass`, `username=`, `password=` |
| `context=` | `context=` endpoint पर |
| `disallow=all` / `allow=ulaw` | `disallow=all` / `allow=ulaw` endpoint पर (एक ही सिंटैक्स) |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` (PJSIP) — साथ ही `inband`, `info`, `auto` |
| `directmedia=yes/no` | `direct_media=yes/no` endpoint पर |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` (endpoint) |
| `qualify=yes` | `qualify_frequency=` (सेकंड) **aor** पर |
| `externaddr=` | `external_media_address=` और `external_signaling_address=` **transport** पर |
| `localnet=` | `local_net=` **transport** पर |
| `insecure=invite` (प्रोवाइडर, कोई auth नहीं) | `auth=`/`outbound_auth=` को हटाएँ और `identify` (`type=identify`, `match=`) का उपयोग करें |
| `allowguest=yes` | `anonymous` endpoint + `allow_unauthenticated_options` (सावधानी से उपयोग करें) |
| `tos_sip` / `tos_audio` | `tos_audio` / `tos_video` (और `cos_audio` / `cos_video`) endpoint पर |

एक रजिस्टर करने वाला एक्सटेंशन जो लेगेसी `sip.conf` में इस प्रकार दिखता था:

```
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

Asterisk 22 पर `pjsip.conf` में यह इस प्रकार बन जाता है:

```
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

### sip_to_pjsip.py रूपांतरण स्क्रिप्ट

Asterisk एक सहायक स्क्रिप्ट, **`sip_to_pjsip.py`**, प्रदान करता है, जो मौजूदा
`sip.conf` को पढ़ती है और एक `pjsip.conf` बनाती है। आप इसे सीधे
/etc/asterisk निर्देशिका में चला सकते हैं। यह उपयोगिता Asterisk स्रोत पेड़ में
`contrib/scripts/sip_to_pjsip/` पर स्थित है, जहाँ `${PATH_TO_ASTERISK_SOURCE}` वह पथ है
जहाँ Asterisk स्रोत फ़ाइलें मिलती हैं (आमतौर पर /usr/src/asterisk-22.x.y/).

```
${PATH_TO_ASTERISK_SOURCE}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

यदि आप इसे `--help` विकल्प के साथ चलाते हैं तो आप इसके विकल्प देखेंगे:

```
-h, --help                help
-p, --prefix PREFIX       prefix to use for the included config files
-q, --quiet               suppress warnings and informational messages
```

It also accepts optional positional arguments — `[input-file [output-file]]`,
defaulting to `sip.conf` and `pjsip.conf` in the current directory.

Treat its output as a **starting point**: review every generated object,
especially transports, NAT settings, and codec lists, and test thoroughly before
going to production.

Let’s migrate the sip.conf in our companion labs at VoIP School Blackbelt (voip.school)

#### sip.conf

```
[general]
bindport=5060
bindaddr=0.0.0.0
context=dummy
disallow=all
allow=ulaw
alwaysauthreject=yes
allowguest=no
register=>1020:supersecret@sip.flagonc.com:5600/9999
[alice]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[bob]
type=friend
secret=#supersecret#
host=dynamic
qualify=yes
directmedia=no
context=from-internal
[siptrunk]
type=peer
defaultuser=1020
secret=supersecret
port=5600 ; nor 5060, 5600
insecure=invite
host=sip.flagonc.com
fromuser=1020
fromdomain=sip.flagonc.com
context=from-siptrunk
```

#### pjsip.conf

```
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[alice]
qualify = yes
[bob]
qualify = yes
[siptrunk]
defaultuser = 1020
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
[transport-udp]
type = transport
protocol = udp
bind = 0.0.0.0:5060
[reg_sip.flagonc.com]
type = registration
retry_interval = 20
max_retries = 10
contact_user = 9999
expiration = 120
transport = transport-udp
outbound_auth = auth_reg_sip.flagonc.com
client_uri = sip:1020@sip.flagonc.com:5600
server_uri = sip:sip.flagonc.com:5600
[auth_reg_sip.flagonc.com]
type = auth
password = supersecret
username = 1020
[alice]
type = aor
max_contacts = 1
[alice]
type = auth
username = alice
password = #supersecret#
[alice]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = alice
outbound_auth = alice
aors = alice
[bob]
type = aor
max_contacts = 1
[bob]
type = auth
username = bob
password = #supersecret#
[bob]
type = endpoint
context = from-internal
disallow = all
allow = ulaw
direct_media = no
auth = bob
outbound_auth = bob
aors = bob
[siptrunk]
type = aor
contact = sip:1020@sip.flagonc.com:5600
[siptrunk]
type = identify
endpoint = siptrunk
match = sip.flagonc.com
[siptrunk]
type = auth
username = siptrunk
password = supersecret
[siptrunk]
type = endpoint
context = from-siptrunk
disallow = all
allow = ulaw
from_user = 1020
from_domain = sip.flagonc.com
auth = siptrunk
outbound_auth = siptrunk
aors = siptrunk
```

जब रूपांतरण ठीक लगता है, तब हम देख सकते हैं कि कुछ तत्व जैसे `qualify=yes` को सीधे मैप नहीं किया जा सकता। इसे ठीक करने के लिए आपको `aor` सेक्शन में `qualify_frequency=time` (सेकंड में) कमांड जोड़ना होगा। नीचे उदाहरण दिया गया है।

```
[bob]
type = aor
max_contacts = 1
qualify_frequency=15
```

पूर्ण PJSIP कॉन्फ़िगरेशन *SIP & PJSIP in depth* अध्याय में कवर किया गया है, और आधिकारिक दस्तावेज़ docs.asterisk.org पर चैनल का पूर्ण कवरेज है। हमारे सहायक लैब्स voip.school पर, लैब 5 आपको अभी सीखा हुआ अभ्यास करने देता है।

## Summary

यह अध्याय उन चैनल तकनीकों को एकत्र करता है जो आज के शुद्ध‑VoIP डिप्लॉयमेंट्स से पहले की हैं लेकिन Asterisk 22 अभी भी उनका समर्थन करता है। आपने देखा कि **analog** लाइनों और फ़ोनों को DAHDI पर **FXO/FXS** इंटरफ़ेस के माध्यम से कैसे जोड़ा जाता है, **digital TDM** लिंक (E1/T1 और ISDN PRI/BRI) को कैसे प्रोविजन किया जाता है, और **IAX2** (`chan_iax2`) अभी भी एक कुशल, NAT‑friendly सर्वर‑से‑सर्वर ट्रंक के रूप में कार्य करता है जबकि यह अब दृढ़ता से लेगेसी बन चुका है। आपने हटाए गए **`chan_sip`** ड्राइवर और उसके `sip.conf` सिंटैक्स को भी दोबारा देखा — जिससे आप पुराने सिस्टम में मिलेंगे लेकिन जो अब Asterisk 22 में मौजूद नहीं है — और PJSIP में माइग्रेट करने के लिए कॉन्सेप्ट‑मैपिंग टेबल और `sip_to_pjsip.py` स्क्रिप्ट के साथ काम किया। मुख्य नियम: इस अध्याय में कुछ भी तभी अपनाएँ जब वास्तविक हार्डवेयर या मौजूदा लेगेसी सिस्टम आपका हाथ मजबूर करे; सभी नई‑फ़ील्ड डिप्लॉयमेंट्स के लिए PJSIP over IP है।

## Quiz

1. Regarding the two analog Foreign eXchange interfaces, mark the correct statements (choose all that apply):
   - A. An FXO interface connects to the public switched telephone network (PSTN) central office and draws dial tone from it.
   - B. An FXS interface provides dial tone and ringing power to a standard analog phone, fax, or modem.
   - C. An FXS interface is the correct way to connect Asterisk to a telco line.
   - D. An FXO interface can also be connected to an extension port of a legacy PBX.
2. Supervision signaling on an analog line includes which of the following (choose all that apply)?
   - A. On-hook
   - B. Off-hook
   - C. Ringing
   - D. DTMF
3. Echo, pops, and noise on a DAHDI analog card are most often caused by:
   - A. The way Asterisk was compiled
   - B. PCI interrupt conflicts
   - C. An incorrect SIP codec
   - D. A missing dial plan
4. For precise billing on analog channels you must detect exactly when the far end answers. Which feature do you activate on Asterisk (and request from the telco) to do this?
   - A. Answer reversal
   - B. Billing reversal
   - C. Polarity reversal
   - D. Dial-tone generation
5. The DAHDI hardware is independent of Asterisk: the physical card is configured in `/etc/dahdi/system.conf`, while `chan_dahdi.conf` defines the Asterisk channels, not the hardware itself.
   - A. True
   - B. False
6. Regarding digital trunk capacity and signaling, mark the correct statements (choose all that apply):
   - A. An E1 trunk carries 30 voice channels and a T1 trunk carries 24.
   - B. An ISDN PRI uses 30B+D on an E1 and 23B+D on a T1.
   - C. ISDN is an example of CCS signaling, while MFC/R2 is an example of CAS signaling.
   - D. T1 is the digital trunk most commonly used in Europe and Latin America.
7. Which utility automatically detects DAHDI cards and generates `/etc/dahdi/system.conf` and `dahdi-channels.conf`?
   - A. dahdi_generator
   - B. dahdi_genconf
   - C. dahdi_cfg
   - D. generate_dahdi
8. When migrating a legacy `sip.conf` `[friend]` to PJSIP, a single block must be split into several objects. Which set of PJSIP `type=` objects normally replaces one registering `[friend]`?
   - A. `type=endpoint`, `type=aor`, and `type=auth`
   - B. `type=peer` and `type=user`
   - C. `type=sip` only
   - D. `type=channel` and `type=device`
9. What is the main practical advantage of using IAX2 trunk mode between two Asterisk servers?
   - A. It encrypts every call with TLS by default
   - B. It carries several calls under a single header, saving bandwidth
   - C. It removes the need for any codec
   - D. It allocates a separate UDP port per call for better quality
10. RSA keys can be used for IAX2 authentication. Which key must you keep secret, and which do you give to the other server?
    - A. Keep the public key secret; share the private key
    - B. Keep the private key secret; share the public key
    - C. Keep the shared key secret; share the private key
    - D. Both keys must be shared

**Answers:** 1 — A, B, D · 2 — A, B, C · 3 — B · 4 — C · 5 — A · 6 — A, B, C · 7 — B · 8 — A · 9 — B · 10 — B
