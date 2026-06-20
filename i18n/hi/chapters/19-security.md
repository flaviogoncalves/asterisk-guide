# Asterisk Security

शुरुआत से ही, Asterisk की सुरक्षा का मुद्दा अत्यंत महत्वपूर्ण रहा है। SIP, Session Initiation Protocol इंटरनेट पर सबसे अधिक हमले का शिकार प्रोटोकॉल है, जैसा कि CERT.BR ने बताया है। कोई भी व्यक्ति जो हनीपॉट चलाता है, यह पुष्टि कर सकता है। इंटरनेट रिवेन्यू शेयर फ्रॉड की समस्या बहुत गंभीर है और यह सैकड़ों हज़ार डॉलर के नुकसान तक ले जा सकती है। आपको कभी भी बिना उचित सुरक्षा के इंटरनेट से जुड़ा हुआ Asterisk Server इंस्टॉल नहीं करना चाहिए। इस अध्याय में, आप सीखेंगे कि आप किन मुख्य प्रकार के हमलों का सामना कर सकते हैं और उचित सुरक्षा नीति का उपयोग करके उन्हें कैसे रोक सकते हैं। अंत में, आप सुझाई गई सुरक्षा नीति को कैसे लागू करें, यह भी सीखेंगे।

यह अध्याय **Asterisk 22 LTS** को लक्षित करता है, जहाँ PJSIP (`res_pjsip` / `chan_pjsip`) एकमात्र SIP चैनल है। (पुराना `chan_sip` ड्राइवर Asterisk 21 में हटा दिया गया था — यदि आप पुराने सिस्टम को माइग्रेट कर रहे हैं तो *Legacy Channels* अध्याय देखें।) एक सुरक्षा-संबंधी परिणाम: अब विफल प्रमाणीकरण Asterisk **security event framework** और समर्पित `security` लॉगर चैनल के माध्यम से जारी किए जाते हैं, जिससे Fail2Ban की कॉन्फ़िगरेशन बदलती है (इस अध्याय में बाद में कवर किया गया)।

## Objectives

By the end of this chapter you should be able to:

- Identify the main types of attacks frequently made to Asterisk servers
- Define an effective security policy
- Implement the security policy
- Install and configure IPTABLES for Asterisk
- Install and configure Fail2Ban for Asterisk
- Install and configure TLS and SRTP for encryption

## IP टेलीफोनी के मुख्य हमले

मुख्य IP टेलीफ़ोनी हमलों को DOS/DDOS, सेवा चोरी/टोल धोखाधड़ी और ईव्सड्रॉपिंग के रूप में वर्गीकृत किया जा सकता है। कुछ नाम भ्रमित करने वाले हो सकते हैं और विभिन्न स्रोत कभी‑कभी एक ही हमले के लिए अलग‑अलग नाम उपयोग करते हैं। Service Theft, Toll Fraud, Internet Revenue Share Fraud, Phone Fraud वे विभिन्न नाम हैं जिनका उपयोग हैकर आपके PBX का उपयोग करके प्रीमियम रेट नंबर पर ट्रैफ़िक भेजने और प्रदाता से रिबेट प्राप्त करने के लिए करते हैं।

### DDoS/DOS

Denial of Service और Distributed Denial of Service किसी भी IT इन्फ्रास्ट्रक्चर के लिए लोकप्रिय हमले हैं। SIP और अन्य Voice over IP प्रोटोकॉल के साथ भी यह अलग नहीं है। Distributed denial of service आमतौर पर एक बॉटनेट द्वारा किया जाता है जबकि DOS केवल एक एकल कंप्यूटर द्वारा किया जाता है। फरवरी 2011 में Sality बॉटनेट ने पूरे IPv4 एड्रेस स्पेस का एक छिपा, समन्वित स्कैन किया, जिसमें कमजोर SIP सर्वरों की तलाश की गई — UCSD नेटवर्क टेलीस्कोप को देख रहे शोधकर्ताओं ने इसे लगभग तीन मिलियन अलग-अलग स्रोत IPs द्वारा UDP पोर्ट 5060 को प्रोब करने के रूप में वर्गीकृत किया, जो संभवतः टोल फ्रॉड के लिए SIP अकाउंट्स को ब्रूट‑फ़ोर्स करने के उद्देश्य से था।[^sality]

[^sality]: A. Dainotti et al., "‘/0’ स्टेल्थ स्कैन का बॉटनेट से विश्लेषण," *IEEE/ACM Transactions on Networking*, 2015 (DOI 10.1109/TNET.2013.2297678).

![एक पीयर-टू-पीयर बॉटनेट जो सर्वर पर हजारों SIP पंजीकरण प्रयासों को निर्देशित कर रहा है](../images/19-security-fig01.png)

DOS आमतौर पर फ़ज़िंग और फ़्लडिंग जैसी तकनीकों के माध्यम से लागू किया जाता है। फ़्लडिंग SIP, IAX, RTP और अन्य प्रोटोकॉल का उपयोग कर सकती है। वे सेवा को पूरी तरह से रोक सकते हैं या आवाज़ की गुणवत्ता को घटा सकते हैं। यदि पोर्ट इंटरनेट के लिए खुले हों तो इन्हें रोकना बहुत कठिन होता है। नीचे हमलावरों द्वारा उपयोग किए जाने वाले कुछ टूल्स की सूची दी गई है।

**फ़ज़िंग:**

- **PROTOS Test Suite (c07-sip)** — University of Oulu OUSPG से। सॉफ़्टवेयर को रोकने वाले बफ़र ओवरफ़्लो जैसी खराबी उत्पन्न करने के लिए हजारों विकृत पैकेट भेजता है।  
- **Voiper** — सभी SIP गुणों को कवर करने वाले 200,000 से अधिक परीक्षण उत्पन्न करता है और यह सत्यापित करता है कि आपका सर्वर संदेशों को प्रभावी रूप से प्रोसेस कर सकता है। <http://voiper.sourceforge.net/>

**फ़्लडिंग:**

- **INVITE Flooder** — सर्वर को SIP INVITE अनुरोधों से भर देता है। <http://www.hackingvoip.com/tools/inviteflood.tar.gz>
- **IAX Flooder** — सर्वर को IAX2 ट्रैफ़िक से भर देता है। <http://www.hackingvoip.com/tools/iaxflood.tar.gz>
- **RTP Flooder** — सक्रिय मीडिया सत्रों को RTP पैकेटों से भर देता है जिससे आवाज़ की गुणवत्ता घटती है। <http://www.hackingvoip.com/tools/rtpflood.tar.gz>

### DoS/DDoS के लिए शमन तकनीकें

मेरी सिफ़ारिशें हैं

1. अपने Asterisk सर्वर को इंटरनेट पर उजागर न करें, जब तक आवश्यक न हो और उचित सुरक्षा (SBC) के साथ  
2. आंतरिक नेटवर्क में आवाज़ के लिए वर्चुअल LAN का उपयोग करें, विशेष रूप से यदि आप विश्वविद्यालय, कॉलेज में हैं जहाँ उपयोगकर्ताओं की संख्या अधिक है।  
3. बाहरी पहुँच के लिए VPN या TLS का उपयोग करें।

### इंटरनेट राजस्व साझाकरण धोखाधड़ी

This fraud is a bit tricky to understand. The key is to understand the concept of an International premium rate number (IPRN).

![इंटरनेट रिवेन्यू शेयर फ्रॉड के तीन चरण: प्रीमियम रेट नंबर खरीदें, एक कमजोर VoIP डिवाइस खोजें और नंबर पर कॉल करें, फिर भुगतान एकत्र करें](../images/19-security-fig02.png)

एक IPRN वह संख्या है जिसे आप कुछ विशिष्ट इंटरनेट फ़ोन कंपनियों में मुफ्त में आवंटित कर सकते हैं। Internet Premium Rate Number Providers को खोजें और आपको उनकी एक बड़ी सूची मिलेगी। इस प्रकार के ऑपरेटर में आप उदाहरण के तौर पर एक सैटेलाइट नेटवर्क जैसे Iridium में एक संख्या आवंटित कर सकते हैं, जिसका गंतव्य कॉल करने वाले के लिए प्रति मिनट दशमलव डॉलर की लागत रखता है। IPRN प्रदाता आपको प्राप्त किसी भी मिनट के लिए राजस्व का एक प्रतिशत (आय का 10 से 20 %) वापस देगा।

![एक IPRN प्रदाता मूल्य सूची जिसमें प्रति-देश भुगतान दरें और परीक्षण नंबर दिखाए गए हैं](../images/19-security-fig03.png)

आवंटन चरण के बाद, हैकर किसी भी खुले Asterisk सर्वर को खोजने की कोशिश करता है जो आवंटित IPRN को डायल कर सके। पीड़ित के द्वारा नियंत्रित PBX, हैकर के नियंत्रण में, IPRN नंबर पर सैकड़ों कॉल करेगा, जिससे हैकर को बड़ी वापसी और पीड़ित को भारी फोन बिल मिलेगा। कई बार, यह एक ही सप्ताहांत में सैकड़ों हज़ार डॉलर से भी अधिक हो जाता है।

हैकर्स द्वारा PBX पर हमला करने के लिए उपयोग किए जाने वाले मुख्य उपकरण:

1. **SIPVicious**: http://code.google.com/p/sipvicious/. Sipvicious एक सुरक्षा टूल सेट है जो उपयोग में आसान है। इसका मुख्य उद्देश्य संवेदनशील PBX को पहचानना और ब्रूट फोर्स अटैक से SIP पासवर्ड तोड़ना है। सबसे अधिक उपयोग किया जाने वाला टूल svcrack है। यह टूल प्रति सेकंड हजारों पासवर्ड परीक्षण करने में सक्षम है।  
2. **Phone vulnerabilities**. फ़ोन की कमजोरियाँ। हमलावरों द्वारा अक्सर उपयोग किया जाने वाला एक और बिंदु फ़ोन स्वयं है। Asterisk स्थापित करने वाले कई लोग फ़ोन के वेब इंटरफ़ेस में डिफ़ॉल्ट पासवर्ड नहीं बदलते। जब ये फ़ोन इंटरनेट पर खुले होते हैं, तो हमलावर डिफ़ॉल्ट इंटरफ़ेस पासवर्ड का उपयोग करके कॉन्फ़िगरेशन डाउनलोड करने की कोशिश कर सकते हैं, जहाँ वे अक्सर गुप्त SIP पासवर्ड पा लेते हैं।

#### TFTPTheft:

यदि आप TFTP का उपयोग करके फ़ोन की ऑटो प्रोविजनिंग कर रहे हैं, तो आप संभवतः इस प्रकार के हमले के प्रति संवेदनशील हैं। TFTP एक सरल और असुरक्षित फ़ाइल ट्रांसफ़र प्रोटोकॉल का रूप है।

![एक हमलावर TFTP सर्वर से अनुमानित .cfg फ़ाइलें डाउनलोड कर रहा है, कॉन्फ़िगरेशन फ़ाइलों से प्लेनटेक्स्ट क्रेडेंशियल्स एकत्र कर रहा है](../images/19-security-fig04.png)

कॉन्फ़िगरेशन फ़ाइलों के नाम मैक पता के बाद .cfg जोड़कर आसानी से अनुमानित किए जा सकते हैं (उदाहरण के लिए 001A2B3C4D5E.cfg)। एक कुशल हैकर सभी MAC पतों को क्रमिक रूप से आज़माने के लिए एक यूटिलिटी बना सकता है या इसे करने के लिए कोई टूल डाउनलोड कर सकता है। कॉन्फ़िगरेशन फ़ाइल आमतौर पर अनएन्क्रिप्टेड होती है और इसमें गुप्त SIP पासवर्ड शामिल होता है।

#### ब्रूट फोर्स हमलों और tftp चोरी के लिए शमन

इन हमलों को कम करने के लिए आप नीचे दिए गए समाधान लागू कर सकते हैं।

**Brute force:** Brute force हमलों को कम करने का सबसे अच्छा समाधान क्रमिक अनधिकृत प्रयासों को रोकना है। लगभग सभी Asterisk इंस्टॉलर इस目的 के लिए `fail2ban` यूटिलिटी का उपयोग करते हैं। जब `fail2ban` कई बार गलत पासवर्ड या उपयोगकर्ता नाम के साथ प्रयास पहचान लेता है, तो वह हमलावर के IP को एक निश्चित अवधि के लिए ब्लॉक कर देता है। Brute force के खिलाफ दूसरा उपाय मजबूत पासवर्ड का उपयोग करना है, जो 12 अक्षरों से अधिक हों और कम से कम एक विशेष अक्षर शामिल हो।

**Tftptheft:** TFTPTheft को रोकने के लिए provisioning को `https` के साथ नाम और पासवर्ड का उपयोग करने के लिए कॉन्फ़िगर करें। फ़ाइल एन्क्रिप्टेड रूप में ट्रांसमिट होती है और नाम व पासवर्ड हमलावरों को किसी भी फ़ाइल को डाउनलोड करने का प्रयास करने से रोकते हैं।

### सुनवाई

हम इन प्रकार के हमलों को अधिक नहीं देखते क्योंकि अधिकांश मामलों में वे बस पता नहीं चलते। IP वातावरण में ईव्सड्रॉपिंग का पता लगाना बहुत कठिन होता है। UCsniff जैसी मुफ्त उपलब्ध उपयोगिताएँ अधिकांश नेटवर्क में VoIP कॉल को ईव्सड्रॉप करने में सक्षम होती हैं। मुख्य तकनीक ARP स्पूफ़िंग का उपयोग करके ट्रैफ़िक को UCsniff चलाने वाले कंप्यूटर के माध्यम से प्रवाहित कराना और कॉल्स को रिकॉर्ड करना है।

#### सुनवाई के लिए शमन

आप अपने VoIP ट्रैफ़िक को एन्क्रिप्ट करके ईव्सड्रॉपिंग को रोक सकते हैं। दूसरा तरीका है आपके नेटवर्क पर मैन‑इन‑द‑मिडल (MITM) हमलों को रोकना। ARP इन्स्पेक्शन लेयर 2 नेटवर्क में MITM को रोकने के लिए बहुत प्रभावी है। इसे लागू करने के बारे में समझने के लिए अपने नेटवर्क तकनीकी समर्थन से संपर्क करें। बाद में इस पुस्तक में हम TLS और SRTP पर आधारित एन्क्रिप्शन को कैसे स्थापित किया जाए, यह सीखेंगे। आप ARPWatch का उपयोग करके यह भी पता लगा सकते हैं कि कोई अब ARP प्रोटोकॉल का दुरुपयोग करके आपके नेटवर्क पर हमला तो नहीं कर रहा है।

## Asterisk के लिए सुरक्षा नीति

सबसे अच्छा तरीका सुरक्षा को लागू करने का है एक सुरक्षा नीति बनाना। इस प्रशिक्षण के लिए मैं अधिकांश Asterisk इंस्टॉलेशन के लिए एक सुरक्षा नीति का सुझाव दूँगा। इसे आधार प्रारम्भिक बिंदु के रूप में उपयोग करें और अपनी आवश्यकताओं के अनुसार बदलें। नीचे सुझाई गई सुरक्षा नीति दी गई है:

1. अनावश्यक UDP/TCP पोर्ट खुले नहीं होने चाहिए  
2. इंटरनेट पर कोई भी प्रशासनिक इंटरफ़ेस (SSH/HTTPS) खुला नहीं होना चाहिए।  
3. SSH और/या HTTP/HTTPS तक पहुँचने के लिए IPTABLES फ़ायरवॉल में स्पष्ट अपवाद होने चाहिए।  
4. 12 अक्षरों वाले और कम से कम एक विशेष अक्षर वाले मजबूत पासवर्ड।  
5. Fail2ban का उपयोग करके प्रमाणीकरण में 10 से अधिक बार विफल होने वाले IP पते को प्रतिबंधित करें।  
6. अंतर्राष्ट्रीय कॉल के लिए पासवर्ड पुष्टि।  
7. SIP पोर्ट तक पहुँच को आपके ज्ञात IP पते की रेंज तक सीमित रखें।

यदि आपको अपने PBX तक बाहरी पहुँच की आवश्यकता है, तो दो संभावनाएँ हैं। अपने सर्वर को DOS/DDOS से बचाने के लिए एक SBC (Session Border Controller) का उपयोग करें या जब भी आप बाहरी पहुँच चाहते हैं, एक VPN का उपयोग करें। यदि आप इंटरनेट पर पोर्ट 5060 को बिना SBC या VPN के खुला छोड़ते हैं, तो आप DOS/DDOS हमले के प्रति संवेदनशील हो जाते हैं। जोखिम आपका है।

### PJSIP-युग की मजबूती (Asterisk 22)

फ़ायरवॉल और Fail2Ban के अलावा, Asterisk 22 की PJSIP स्टैक कई कॉन्फ़िगरेशन‑स्तर के नियंत्रण प्रदान करती है जो आपके सुरक्षा नीति का हिस्सा होना चाहिए। ये ऊपर बताए गए नेटवर्क नियंत्रणों को पूरक (बदलने के लिए नहीं) करते हैं।

- **प्रति-एंडपॉइंट प्रमाणीकरण।** प्रत्येक एंडपॉइंट को एक समर्पित `type=auth` सेक्शन का संदर्भ देना चाहिए जिसमें एक मजबूत, अद्वितीय `password` (`auth_type=digest`) हो। एंडपॉइंट्स के बीच क्रेडेंशियल्स को कभी दोहराएँ नहीं।  
- **गुमनाम हैंडलिंग अंतर्निहित है।** PJSIP प्रमाणीकरण विफल होने पर यह नहीं बताता कि उपयोगकर्ता नाम मौजूद है या नहीं। सभी गुमनाम कॉल्स को स्वीकार करने के लिए आपको स्पष्ट रूप से `anonymous` नामक एक एंडपॉइंट बनाना होगा और `type=identify` सेक्शन्स (स्रोत IP पर मिलान) का उपयोग करके ज्ञात पीयर्स को एंडपॉइंट्स से मैप करना होगा। यदि आप गुमनाम कॉल्स नहीं चाहते, तो बस `anonymous` एंडपॉइंट न बनाएँ, और अनमैच्ड अनुरोधों को चुनौती/अस्वीकार किया जाएगा।  
- **ACLs।** `/etc/asterisk/acl.conf` नामक ACLs के साथ यह निर्धारित करें कि कौन एक एंडपॉइंट तक पहुँच सकता है, जिसे एंडपॉइंट से `acl=` (सिग्नलिंग/स्रोत ACL) और `contact_acl=` (संपर्क/रजिस्ट्रेशन पते को प्रतिबंधित करता है) के माध्यम से संदर्भित किया जाता है। आप सीधे एंडपॉइंट पर permit/deny भी सेट कर सकते हैं।  
- **`qualify`।** AOR पर `qualify_frequency` (और `qualify_timeout`) सेट करें ताकि Asterisk पंजीकृत संपर्कों की पहुँचयोग्यता को सक्रिय रूप से मॉनिटर करे और मृत संपर्कों को हटाए।  
- **PJSIP ट्रांसपोर्ट हार्डनिंग / DoS सुरक्षा।** `type=transport` प्रति-ट्रांसपोर्ट क्लाइंट कैप नहीं दिखाता, इसलिए कनेक्शन-फ़्लड सुरक्षा फ़ायरवॉल (इस अध्याय में iptables/Fail2Ban नियम) से आती है, न कि PJSIP विकल्प से। ट्रांसपोर्ट *जो* देता है वह है TCP keep-alive ट्यूनिंग (`tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`) ताकि मृत/हाफ-ओपन कनेक्शन को समाप्त किया जा सके, और NAT हैंडलिंग के लिए `local_net`/`external_*` सेटिंग्स। इनको फ़ायरवॉल नियमों के साथ मिलाकर कनेक्शन-फ़्लड हमलों को कम किया जा सकता है।  
- **TLS + SRTP मीडिया के लिए।** सिग्नलिंग को TLS ट्रांसपोर्ट से एन्क्रिप्ट करें और मीडिया को `media_encryption=sdes` (या WebRTC के लिए `dtls`) से एन्क्रिप्ट करें — इस अध्याय में बाद में कवर किया गया है।  
- **AMI/ARI एक्सेस कंट्रोल।** Asterisk Manager Interface (`manager.conf`) और ARI (`ari.conf` / `http.conf`) को localhost या विश्वसनीय प्रबंधन नेटवर्क तक सीमित रखें, मजबूत अद्वितीय सीक्रेट्स का उपयोग करें, HTTP सर्वर को निजी इंटरफ़ेस से बाइंड करें, और इन्हें इंटरनेट पर कभी उजागर न करें।

उपर्युक्त सभी विकल्प नाम Asterisk 22.10 के खिलाफ पुष्टि किए गए हैं: `type=transport` सेक्शन `tcp_keepalive_enable`, `tcp_keepalive_idle_time`, `tcp_keepalive_interval_time`, `tcp_keepalive_probe_count`, `tos`, `cos`, `local_net` को उजागर करता है, और `external_*` परिवार को, लेकिन इसमें **कोई** `max_clients` विकल्प नहीं है — कनेक्शन‑फ़्लड सुरक्षा फ़ायरवॉल से आती है, ट्रांसपोर्ट से नहीं। `acl` और `contact_acl` endpoint विकल्प `acl.conf` से सेक्शन नाम लेते हैं, और अनप्रमाणित पीयर्स के लिए स्रोत‑IP मिलान `type=identify` सेक्शनों के साथ किया जाता है (`match=`)।

### अनावश्यक पोर्ट्स को हटाना

सभी Asterisk प्रोटोकॉल से जुड़ी सभी कमजोरियों की खोज करने के बजाय, आइए अनावश्यक पोर्ट्स को हटाकर समस्या को सरल बनाते हैं। Asterisk सर्वर द्वारा खुले सभी पोर्ट्स की सूची प्राप्त करने के लिए उपयोग करें:

```
netstat -pantu |grep asterisk
```

The output of the command is shown below.

![netstat output showing the many ports bound by Asterisk, including 4569 (IAX) and 2727 (MGCP)](../images/19-security-fig05.png)

यदि आप आउटपुट को देखें तो आपको पता चलेगा कि कई पोर्ट खुले हुए हैं। क्या हमें सभी की जरूरत है? जरूरी नहीं, 2727 MGCP प्रोटोकॉल (chan_mgcp) है, 4569 IAX (chan_iax2) है। यदि आप इन प्रोटोकॉल का उपयोग नहीं कर रहे हैं, तो आप configuration फ़ाइल modules.conf में से मॉड्यूल को सरलता से हटा सकते हैं।

आप देख सकते हैं कि Asterisk एक उच्च‑संख्या वाला UDP पोर्ट बाइंड कर रहा है। यह `res_pjsip` के resolver द्वारा आउटबाउंड DNS क्वेरी करने से आता है (स्रोत पोर्ट अस्थायी होता है, जैसे किसी भी क्लाइंट DNS लुकअप में), न कि किसी इनबाउंड लिस्नर से — आपके फ़ायरवॉल को केवल **established/related** रिटर्न ट्रैफ़िक की अनुमति देनी चाहिए (नीचे दिखाया गया iptables `conntrack ESTABLISHED,RELATED` नियम पहले से ही इसे कवर करता है)। आपको PJSIP DNS के लिए व्यापक इनबाउंड हाई‑UDP रेंज खोलने की आवश्यकता **नहीं** है।

अनावश्यक पोर्ट्स को हटाने के लिए, उन मॉड्यूल्स को डिसेबल करें जिनका आप उपयोग नहीं करते। फ़ाइल modules.conf को एडिट करें और उन चैनलों और प्रोटोकॉल्स के लिए `noload` लाइनें जोड़ें जिनका आप उपयोग नहीं कर रहे हैं। **Do not** noload `res_pjsip`, `res_pjproject`, या `chan_pjsip` — ये Asterisk 22 में SIP के लिए आवश्यक हैं।

```
; res_pjsip / res_pjproject / chan_pjsip are REQUIRED in Asterisk 22 - keep them loaded
noload => chan_iax2.so
noload => chan_unistim.so
```

(In Asterisk 22 you no longer need to noload `chan_mgcp` or `chan_skinny` — those drivers were *removed* in Asterisk 21 and are not part of a stock 22 build.) With the instructions above, I have removed all unnecessary channels keeping only PJSIP. You can choose whatever protocol modules you want, just remove the unused ones. The result is shown in the screenshot below — only the SIP port (5060) bound by your PJSIP transport is now exposed inbound.

![netstat output after disabling the unused modules: only UDP port 5060 remains bound by Asterisk](../images/19-security-fig06.png)

### IPTABLES के साथ सुरक्षा नीति लागू करना

IPTABLES या netfilter अधिकांश Linux वितरणों में मौजूद एक मानक फ़ायरवॉल है। इस लैब में हम iptables और fail2ban को कॉन्फ़िगर करेंगे। उद्देश्य Asterisk के लिए अनुशंसित सुरक्षा नीति को लागू करना और सभी अनावश्यक ट्रैफ़िक को ब्लॉक करना है। नीचे दिए गए चरणों का पालन करें:

1. सभी बाहरी ट्रैफ़िक को ब्लॉक करें
2. आंतरिक नेटवर्क या एकल होस्ट से SSH ट्रैफ़िक की अनुमति दें
3. UDP और TCP में SIP ट्रैफ़िक को पोर्ट 5060 पर अनुमति दें
4. UDP मीडिया पोर्ट रेंज में RTP ट्रैफ़िक की अनुमति दें। कोई एकल डिफ़ॉल्ट नहीं है — Asterisk की अपनी `rtp.conf` पोर्ट रेंज सेट न होने पर 5000–31000 पर फ़ॉल्बैक करती है, लेकिन शिप्ड `rtp.conf.sample` `rtpstart=10000` / `rtpend=20000` को कॉन्फ़िगर करता है, इसलिए हम यहाँ उस उदाहरण रेंज का उपयोग करते हैं। अपने फ़ायरवॉल नियम को उस `rtpstart`/`rtpend` के अनुसार मिलाएँ जो आपने `rtp.conf` में वास्तव में सेट किया है।

सुनिश्चित करें कि आपके पास सर्वर तक कंसोल एक्सेस है, आप स्वयं को सिस्टम से बाहर नहीं ब्लॉक करना चाहते। सावधान रहें।

1. पैकेज `net-persistent` इंस्टॉल करें।```
   sudo apt-get install iptables-persistent
   ```

2. लूपबैक से सभी ट्रैफ़िक की अनुमति दें```
   sudo iptables -I INPUT -i lo -j ACCEPT
   sudo iptables -I OUTPUT -o lo -j ACCEPT
   ```

3. स्थापित कनेक्शनों की अनुमति दें```
   sudo iptables -I INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
   ```

4. नेटवर्क 192.168.0.0 से SSH/HTTPS ट्रैफ़िक की अनुमति दें```
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 22 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   sudo iptables -I INPUT -p tcp -s 192.168.0.0/16 --dport 443 -m conntrack --ctstate
   NEW,ESTABLISHED -j ACCEPT
   ```

5. Asterisk नियम सम्मिलित करें```
   sudo iptables -I INPUT -p udp -m udp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5060 -j ACCEPT
   sudo iptables -I INPUT -p tcp -m tcp --dport 5061 -j ACCEPT
   sudo iptables -I INPUT -p udp -m udp --dport 10000:20000 -j ACCEPT
   ```

   Note that port 5061 (SIP over TLS) is **TCP**, not UDP. The rules above open 5060 on both UDP and TCP and 5061 on TCP. If you only run TLS, you can drop the plain 5060 rules entirely. Only open the ports your PJSIP transports actually bind to.

   `-I` means PREPEND

6. The last rule has to be a drop```
   sudo iptables -A INPUT -j DROP
   ```

`-A` का अर्थ APPEND है। नोट: नई नियमों को बनाए रखते समय सावधान रहें, आपको नियम DROP से पहले जोड़ने होंगे। नए नियमों के लिए PREPEND का उपयोग करें `-I`

7. नियमों को सहेजें और iptables को पुनः प्रारंभ करें```
   sudo iptables-save >/etc/iptables/rules.v4
   sudo /etc/init.d/netfilter-persistent restart
   ```

### Using Fail2Ban to block multiple failed attempts to authenticate

Fail2Ban लगभग Asterisk के लिए एक मानक बन चुका है। अधिकांश उपयोगकर्ता सुरक्षा बढ़ाने के लिए इसे लागू करते हैं। यह उपयोगिता Asterisk लॉग्स में विफल प्रयासों को स्कैन करती है और हमलावरों के IP पते को प्रतिबंधित करती है। नीचे मैं Fail2Ban को स्थापित करने के निर्देश प्रदान करता हूँ।

Asterisk 22 में, PJSIP विफल प्रमाणीकरण और अन्य सुरक्षा घटनाओं को Asterisk **security event framework** के माध्यम से रिपोर्ट करता है, जो समर्पित **`security`** logger चैनल में लिखा जाता है। Fail2Ban को काम करने के लिए आपको करना होगा:

1. `/etc/asterisk/logger.conf` में सुरक्षा चैनल को सक्षम करें। सिंटैक्स `<filename> => <levels>` है, इसलिए सुरक्षा स्तर को **`security`** नामक फ़ाइल में भेजने के लिए लिखें:

```
[logfiles]
security => security
```

then run `logger reload` from the CLI. This produces `/var/log/asterisk/security` with one line per security event, in the form:

```
[2026-01-15 10:23:45] SECURITY[1234] res_security_log.c: SecurityEvent="InvalidPassword",...,RemoteAddress="IPV4/UDP/203.0.113.7/5060",...
```

The events Fail2Ban cares about are `InvalidPassword`, `ChallengeResponseFailed`, `InvalidAccountID`, and `FailedACL`, each carrying a `RemoteAddress="IPV4/UDP/<ip>/<port>"` field that identifies the offender. (Note the address is wrapped as `IPV4/UDP/.../...`, not a bare IP — your filter must extract the host from inside that string.)

2. Point the `asterisk` jail at that file (`logpath = /var/log/asterisk/security`) and use a filter that parses this security-event format.

Modern Fail2Ban ships an `asterisk` filter whose `failregex` already matches the events above and extracts `<HOST>` from the `RemoteAddress` field, for example:

```
failregex = ^SecurityEvent="(?:FailedACL|InvalidAccountID|ChallengeResponseFailed|InvalidPassword)".*,RemoteAddress="IPV[46]/[^/"]+/<HOST>/\d+"
```

PBX वितरण (FreePBX/Sangoma) समान फ़िल्टर प्रदान करते हैं। हाथ से फ़िल्टर लिखने की बजाय पैकेज्ड फ़िल्टर को प्राथमिकता दें, क्योंकि सटीक इवेंट स्ट्रिंग्स संस्करण‑निर्भर होती हैं। एक बात ध्यान में रखें: एक हालिया पैच किया गया advisory (GHSA-5743-x3p5-3rg7) दिखाता है कि निर्मित PJSIP ट्रैफ़िक नकली लॉग लाइनों को इंजेक्ट कर सकता है — Asterisk और आपका Fail2Ban फ़िल्टर दोनों को अद्यतित रखें।

नीचे मैं Fail2Ban स्थापित करने के निर्देश प्रदान करता हूँ

1. Linux पर fail2ban स्थापित करें```
   sudo apt-get install fail2ban
   ```

2. Asterisk और SSH के लिए fail2ban सक्रिय करें```
   sudo vi /etc/fail2ban/jails.d/defaults-debian.conf
   ```

   ssh और asterisk के लिए fail2ban को सक्रिय करने के लिए निम्नलिखित पंक्तियों को जोड़ें

  ```
   [sshd]
   enabled = true
   [asterisk]
   enabled=true
   ```

3. fail2ban को पुनः प्रारंभ करें```
   /etc/init.d/fail2ban restart
   ```

4. सत्यापित करें। अपने softphone से secret बदलें और 10 बार पुनः‑रजिस्टर करने का प्रयास करें। Using `iptables -L`, check if the softphone address was included as a blocked address.  
5. Remove the address from the ban (suppose the address is 192.168.0.5)```
   sudo fail2ban-client set asterisk unbanip 192.168.0.5
   ```

Note: In the command replace 192.168.0.5 by the ip address of your phone

### Implementing TLS and SRTP

I will split this section in two. In the first part we will cover TLS to encrypt signaling and in the second part SRTP to encrypt media. The objective here is to configure Asterisk for these resources.

#### TLS

TLS (Transport Layer Security) is the encryption mechanism defined to protect the SIP signaling. The table below summarizes which attacks TLS protects against:

| हमले का प्रकार | सुरक्षित? | नोट्स |
|----------------|-----------|-------|
| सिग्नलिंग हमले | हाँ | TLS संदेशों की अखंडता सुनिश्चित करता है |
| मध्यस्थ हमला | हाँ | TLS सर्वर प्रमाणपत्र की जाँच करता है |
| ईव्सड्रॉपिंग | नहीं | TLS सिग्नलिंग को एन्क्रिप्ट करता है, मीडिया नहीं |

For media (voice/video) encryption use SRTP.

#### Self-signed digital certificates

There are two types of certificates you can use self-signed and commercial. Self-signed certificates are signed by your own server while commercial certificates are signed by an external authority. For VoIP, you can be your own certificate authority. There is no need for an external certificate such as GoDaddy and Verisign, this is an unnecessary expense. We will generate our own certificates using ast_tls_cert.

#### Configuring TLS with self signed certificates

Below is a step-by-step guide on how to implement TLS. We first generate the certificates, then configure the PJSIP TLS transport (see "Configuring TLS with chan_pjsip"), and finally point the softphone at it. We will use the SipPulse Softphone, which supports TLS and SRTP natively. (Any TLS/SRTP-capable SIP softphone works the same way.)

**Step 1.** Create a private RSA key using 3DES encryption with length of 4096 bits for our certification authority. The command below present in /usr/src/asterisk-22.x.y/contrib/scripts will create the Certification Authority and The Asterisk Certificate. As usual adapt the instructions if required, versions change, directories change. Please, pay attention on what you are doing. Use your domain or IP address in the –C option. The command ast_tls_cert has three options.

- -C host or IP address (I have used 192.168.0.74, the IP address of my VM)
- -O Organizational name
- -d Directory where to store the keys

```
mkdir /etc/asterisk/keys
cd /usr/src/asterisk-22.0.0/contrib/scripts
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts# ./ast_tls_cert -C 192.168.0.74 -O "AsteriskGuide" -d /etc/asterisk/keys
No config file specified, creating '/etc/asterisk/keys/tmp.cfg'
You can use this config file to create additional certs without
re-entering the information for the fields in the certificate
Creating CA key /etc/asterisk/keys/ca.key
Generating RSA private key, 4096 bit long modulus
........................................................++
........................................................++
e is 65537 (0x010001)
Enter pass phrase for /etc/asterisk/keys/ca.key:
Verifying - Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating CA certificate /etc/asterisk/keys/ca.crt
Enter pass phrase for /etc/asterisk/keys/ca.key:
Creating certificate /etc/asterisk/keys/asterisk.key
Generating RSA private key, 2048 bit long modulus
........................++++++
......................++++++
e is 65537 (0x010001)
Creating signing request /etc/asterisk/keys/asterisk.csr
Creating certificate /etc/asterisk/keys/asterisk.crt
Signature ok
subject=CN = 192.168.0.74, O = AsteriskGuide
Getting CA Private Key
Enter pass phrase for /etc/asterisk/keys/ca.key:
Combining key and crt into /etc/asterisk/keys/asterisk.pem
root@asterisk:/usr/src/asterisk-22.0.0/contrib/scripts#
```

मैं क्लाइंट प्रमाणपत्र नहीं बनाऊँगा क्योंकि हम क्लाइंट को प्रमाणित करने के लिए प्रमाणपत्र का उपयोग नहीं करने वाले हैं। क्लाइंट को अपना स्वयं का प्रमाणपत्र प्रस्तुत करने की आवश्यकता नहीं है।

**Step 2.** Asterisk को TLS के माध्यम से हमारे क्लाइंट को सपोर्ट करने के लिए कॉन्फ़िगर करें। यह `pjsip.conf` में किया जाता है (एक TLS ट्रांसपोर्ट प्लस एंडपॉइंट सेटिंग्स) — पूरी कॉन्फ़िगरेशन अगले सेक्शन, "Configuring TLS with chan_pjsip." में दिखायी गई है। हम प्रमाणपत्रों से प्रमाणित नहीं कर रहे हैं, केवल ट्रैफ़िक को एन्क्रिप्ट कर रहे हैं।

**Step 3.** एक TLS‑सक्षम SIP सॉफ्टफ़ोन स्थापित करें (लेखक SipPulse Softphone का उपयोग करता है)।

**Step 4.** सॉफ्टफ़ोन चलाने वाले कंप्यूटर पर प्रमाणपत्र प्राधिकरण को कॉपी करें। इसे स्थापित करने के बाद, फ़ाइल `/etc/asterisk/keys/ca.crt` को सॉफ्टफ़ोन चलाने वाले कंप्यूटर पर कॉपी करें (scp का उपयोग करें, या Windows पर WinSCP) यदि आप स्वयं‑हस्ताक्षरित प्रमाणपत्र का उपयोग कर रहे हैं।

**Step 5.** सॉफ्टफ़ोन में अकाउंट बनाएँ। अकाउंट स्क्रीन में किसी भी अन्य sip अकाउंट की तरह सामान्य रूप से अकाउंट जोड़ें। सही पासवर्ड उपयोग करें, प्रमाणन अभी भी पासवर्ड पर आधारित है।

**Step 6.** अकाउंट सेटिंग्स में ट्रांसपोर्ट को TLS सेट करें। SipPulse Softphone अकाउंट स्क्रीन (नीचे) में **TLS** को ट्रांसपोर्ट चुनें और पोर्ट 5061 उपयोग करें। फ़ायरवॉल को समायोजित करके TCP पोर्ट 5061 खोलें।

![The SipPulse Softphone account screen — enter the Server (your Asterisk IP or domain), Username, Password, and Display Name, then choose the Transport (UDP, TCP, or TLS).](../images/softphone/sipphone-account.png){width=35%}

**Step 7.** प्रमाणपत्र प्राधिकरण पर भरोसा करें। यदि आपका Asterisk TLS प्रमाणपत्र सार्वजनिक CA (उदाहरण के लिए Let's Encrypt — देखें *Deployment* अध्याय) द्वारा हस्ताक्षरित है, तो SipPulse Softphone जैसे आधुनिक सॉफ्टफ़ोन इसे सिस्टम प्रमाणपत्र स्टोर के माध्यम से स्वचालित रूप से भरोसा करता है, बिना मैन्युअल आयात के। यदि आप स्वयं‑हस्ताक्षरित प्रमाणपत्र उपयोग करते हैं, तो उसका CA (`/etc/asterisk/keys/ca.crt`) क्लाइंट या ऑपरेटिंग‑सिस्टम ट्रस्ट स्टोर में आयात करें, या प्रॉम्प्ट पर स्वीकार करें।

**Step 8.** आपको क्लाइंट प्रमाणपत्र की **ज़रूरत नहीं** है। एक आम गलतफ़हमी यह है कि प्रत्येक फ़ोन को प्रमाणित करने के लिए अपना स्वयं का प्रमाणपत्र चाहिए — ऐसा नहीं है। इस बिंदु पर Asterisk केवल *एन्क्रिप्ट* करता है सत्र; प्रमाणन अभी भी उपयोगकर्ता नाम और पासवर्ड है। डिफ़ॉल्ट रूप से Asterisk क्लाइंट प्रमाणपत्रों को सत्यापित नहीं करता, इसलिए प्रति‑क्लाइंट प्रमाणपत्र वितरित करने की आवश्यकता नहीं है।

**Step 9.** प्रमाणपत्र या ट्रांसपोर्ट बदलने के बाद, सॉफ्टफ़ोन को पूरी तरह रीस्टार्ट करें (विंडो बंद करने के बजाय बाहर निकलें और फिर से लॉन्च करें) ताकि वह नए ट्रांसपोर्ट पर पुनः कनेक्ट हो सके।

### Configuring TLS with chan_pjsip

अब सीखते हैं कि PJSIP को TLS के लिए कैसे कॉन्फ़िगर किया जाए। PJSIP Asterisk 22 में एकमात्र SIP चैनल है, इसलिए स्विच करने की कोई बात नहीं — बस यह सुनिश्चित करें कि `res_pjsip`, `res_pjproject` और `chan_pjsip` लोडेड हों। Step 1: Confirm PJSIP is enabled in /etc/asterisk/modules.conf.

```
; res_pjsip / res_pjproject / chan_pjsip must be loaded (do NOT noload them)
noload => chan_iax2.so
noload => chan_unistim.so
```

Step 2: TLS को समर्थन देने के लिए PJSIP को कॉन्फ़िगर करें। फ़ाइल /etc/asterisk/pjsip.conf में TLS ट्रांसपोर्ट के लिए एक सेक्शन जोड़ें।

```
[transport-tls]
type=transport
protocol=tls
bind=0.0.0.0:5061
cert_file=/etc/asterisk/keys/asterisk.crt
priv_key_file=/etc/asterisk/keys/asterisk.key
method=tlsv1_2
```

Use `method=tlsv1_2` (or `tlsv1_3` if your OpenSSL/PJSIP build supports it) — TLS 1.0/1.1 are obsolete and insecure and should not be used.

Step 3: Configure the endpoint for blink. Edit `pjsip.conf` and edit the section for blink. Let PJSIP choose the transport automatically.

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
dtmf_mode=rfc4733
media_encryption=sdes
[blink]
type=aor
max_contacts=2
remove_existing=yes
[blink]
type=auth
auth_type=digest
username=blink
password=supersecret
```

चरण 4: सत्यापन। TLS के माध्यम से पंजीकरण हुआ है यह सत्यापित करने के लिए, Asterisk कंसोल में निम्नलिखित कमांड का उपयोग करें।

```text
asterisk*CLI> pjsip show aor blink

      Aor:  <Aor.............................................>  <MaxContact>
    Contact:  <Aor/ContactUri........................> <Hash....> <Status> <RTT(ms)..>
==========================================================================================

      Aor:  blink                                                2
    Contact:  blink/sip:03694827@192.168.0.67:56295;transp 620d91556d NonQual    nan
 ParameterName        : ParameterValue
 ====================================================================
 authenticate_qualify : false
 contact              : sip:03694827@192.168.0.67:56295;transport=tls
 default_expiration   : 3600
 max_contacts         : 2
 maximum_expiration   : 7200
 minimum_expiration   : 60
 qualify_frequency    : 0
 qualify_timeout      : 3.000000
 remove_existing      : true
 support_path         : false
```

### SRTP का उपयोग करके सुरक्षित कॉल करना

मीडिया एन्क्रिप्शन के लिए जिम्मेदार प्रोटोकॉल Secure Real Time Protocol (SRTP) है, जिसे RFC3711 में परिभाषित किया गया है। इस प्रोटोकॉल की एक कमी यह है कि कुंजियों का आदान‑प्रदान करने का कोई मानकीकृत तरीका नहीं है। Asterisk SDES का उपयोग करता है, जो SDP प्रोटोकॉल के माध्यम से कुंजियों का आदान‑प्रदान करता है और TLS द्वारा प्रदान की गई सिग्नलिंग एन्क्रिप्शन से सुरक्षित रहता है। अन्य विधियाँ भी हैं जैसे MIKEY और ZRTP। Philipp Zimmermann द्वारा विकसित ZRTP कुंजी आदान‑प्रदान और मीडिया एन्क्रिप्शन के सबसे परिष्कृत तरीकों में से एक है। कुछ सॉफ्टफ़ोन और हार्ड फ़ोन ZRTP को सपोर्ट करते हैं। हालांकि मानक तरीका अभी भी SDES ही है और आप इस विधि को लगभग सभी उपलब्ध फ़ोन में पाएँगे। नीचे एक अनुरोध का उदाहरण दिया गया है जिसमें SDP में a=crypto:1 और a=crypto:2 लाइनों में क्रिप्टो कुंजियों को परिभाषित किया गया है।

```
INVITE sip:8000@192.168.1.237 SIP/2.0
Via:
SIP/2.0/tls
192.168.1.192:65525;rport;branch=z9hG4bKPj9fa224a14b17488ea15625ead833ea3a
Max-Forwards: 70
From:
"Flavio"
<sip:flavio@192.168.1.237>;tag=35afe6cc11274934867b24e43c805638
To: <sip:8000@192.168.1.237>
Contact: <sip:pyhkxnjz@192.168.1.192:65524;transport=tls>
Call-ID: 530a339c72af47f0a76e7ecb2a58ac43
CSeq: 5669 INVITE
Allow: SUBSCRIBE, NOTIFY, PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, MESSAGE
Supported: 100rel
User-Agent: Blink 0.2.5 (Windows)
Authorization: Digest username="flavio", realm="asterisk", nonce="72ff51ad",
uri="sip:8000@192.168.1.237",
response="ba8c10672751baa7007d82eb34e2340e",
algorithm=MD5
Content-Type: application/sdp
Content-Length: 544
v=0
o=- 3509174186 3509174186 IN IP4 192.168.1.192
s=Blink 0.2.5 (Windows)
c=IN IP4 192.168.1.192
t=0 0
m=audio 50004 RTP/SAVP 9 104 103 102 0 8 101
a=rtcp:50005
a=rtpmap:9 G722/8000
a=rtpmap:104 speex/32000
a=rtpmap:103 speex/16000
a=rtpmap:102 speex/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=crypto:1
AES_CM_128_HMAC_SHA1_80
inline:WrtZH82ztz93albRNT8o+oMcK9GvlAHRoaR1STvJ
a=crypto:2
AES_CM_128_HMAC_SHA1_32
inline:4Ma9jJOCEEGMPzzkmgyf6ttp1qhN16yumdXB7eRv
a=sendrecv
```

#### Asterisk पर SRTP कॉन्फ़िगर करना

Asterisk पर SRTP कॉन्फ़िगर करना बहुत सरल है। एंडपॉइंट पर `media_encryption=sdes` सेट करें; आप इसे `media_encryption_optimistic=no` के साथ भी आवश्यक बना सकते हैं ताकि अनएन्क्रिप्टेड मीडिया को चुपचाप अनुमति देने के बजाय अस्वीकार किया जाए। ध्यान दें कि SDES को सिग्नलिंग को TLS के ऊपर चलाने की आवश्यकता होती है ताकि कुंजियाँ स्पष्ट रूप में न भेजी जाएँ।

**Step 1.** Asterisk कॉन्फ़िगरेशन

`type=endpoint` सेक्शन में `pjsip.conf` पर निम्नलिखित सेट करें:

```
[blink]
type=endpoint
aors=blink
auth=blink
context=from-internal
disallow=all
allow=ulaw
transport=transport-tls
media_encryption=sdes
media_encryption_optimistic=no
```

**Step 2.** Softphone कॉन्फ़िगरेशन

In the softphone, enable SRTP for the account media (set the **SRTP (Media Encryption)** option to *Mandatory*) so that voice is encrypted.

![SipPulse Softphone अकाउंट सेटिंग्स (निचला भाग) — **Transport** को TLS पर सेट करें और **SRTP (Media Encryption)** को *Mandatory* पर सेट करें ताकि सिग्नलिंग और मीडिया दोनों एन्क्रिप्टेड हों।](../images/softphone/sipphone-config.png){width=35%}

## अंतरराष्ट्रीय कॉल के लिए दो‑तरफ़ा प्रमाणीकरण सक्षम करना

कभी‑कभी सबसे अच्छा तरीका यह है कि अंतरराष्ट्रीय मार्ग न रखें। हालांकि, यदि आपको वास्तव में अंतरराष्ट्रीय डायल करना है, तो एक अतिरिक्त पासवर्ड का उपयोग करें। हम Asterisk एप्लिकेशन `vmauthenticate` का उपयोग करके अंतरराष्ट्रीय डायल करने से पहले वॉइसमेल पासवर्ड पूछेंगे। यह `extensions.conf` में डायलप्लान में कॉन्फ़िगर किया जाता है। नीचे उदाहरण देखें। इस प्रकार एक हैकर, चाहे वह पीयर पासवर्ड खोज ले या फोन को समझौता कर ले, फिर भी इस गंतव्य को डायल करने के लिए वॉइसमेल पासवर्ड की आवश्यकता होगी।

```
exten=_9011.,1,Playback(pleasedialyourvmpassword)
exten=_9011.,2,VMAuthenticate(${CALLERID(num)}@default,s)
exten=_9011.,3,Dial(PJSIP/${EXTEN:1}@my_trunk,20,tT)
exten=_9011.,4,Hangup()
```

`VMAuthenticate` अभी भी Asterisk 22 में एक मानक एप्लिकेशन है। ऊपर दिया गया `Dial()` कॉल को एक SIP/PJSIP ट्रंक (`PJSIP/<number>@<trunk>`) के माध्यम से रूट करता है, जो अधिकांश आधुनिक इंस्टॉलेशन PSTN तक पहुँचने के लिए उपयोग करते हैं — अपने ट्रंक नाम के अनुसार `my_trunk` को अनुकूलित करें, और केवल तभी `DAHDI/g1/...` का उपयोग करें जब आपके पास वास्तव में एक DAHDI स्पैन हो। डायलप्लान में टोल‑धोखाधड़ी रक्षा — इस प्रकार का दूसरा कारक, साथ ही यह प्रतिबंध कि कौन‑से कॉन्टेक्स्ट आपके आउटबाउंड और अंतरराष्ट्रीय मार्गों तक पहुँच सकते हैं — वह सबसे महत्वपूर्ण सुरक्षा उपायों में से एक है जिसे आप लागू कर सकते हैं।

## सारांश

इस अध्याय में आपने इंटरनेट से जुड़े IP PBX के जोखिमों के बारे में सीखा। फिर हमने एक सुरक्षा नीति लागू करके अपने PBX की सुरक्षा कैसे की, यह जाना। इस सुरक्षा नीति में हमने iptables, fail2ban, TLS, SRTP और अंतरराष्ट्रीय कॉलों के लिए दो‑तरफ़ा प्रमाणीकरण लागू किया। आशा है आपको यह अध्याय पसंद आया।

## Quiz

1. इंटरनेट रिवेन्यू शेयर फ्रॉड के खिलाफ सबसे महत्वपूर्ण प्रतिकार क्या है?
   - A. Implement SRTP
   - B. Keep Asterisk updated
   - C. Implement TLS
   - D. Use strong passwords
2. SIP fuzzing को इस प्रकार परिभाषित किया जाता है:
   - A. A DoS attack using malformed requests and replies
   - B. Service theft where passwords are brute-forced
   - C. Eavesdropping on current calls
   - D. A DDoS with a flood of SIP requests
3. TFTPTheft तब होता है जब सर्वर TFTP के माध्यम से कॉन्फ़िगरेशन फ़ाइलें प्रदान करता है। आप इसे इस प्रकार टाल सकते हैं:
   - A. FTP
   - B. HTTP
   - C. HTTPS with username and password
   - D. SCP
4. Man-in-the-middle attacks एक तकनीक का उपयोग करते हैं जिसे कहा जाता है:
   - A. TFTP theft
   - B. ARP spoofing
   - C. MAC poisoning
   - D. dsniff
5. SRTP के लिए, Asterisk कुंजियों का आदान‑प्रदान करने के लिए निम्नलिखित प्रणाली का उपयोग करता है:
   - A. MIKEY
   - B. SDES
   - C. ZRTP
   - D. Pluto
6. वह यूटिलिटी जो प्रमाणपत्र प्राधिकरण और प्रमाणपत्र उत्पन्न करती है, जो `/usr/src/asterisk-22.x.y/contrib/scripts` में पाई जाती है, वह है:
   - A. ast_tls_cert
   - B. gen_tls
   - C. gen_ast_tls
   - D. tls_generator
7. ईव्सड्रॉपिंग को रोकने के वैध रणनीतियाँ (सभी लागू विकल्प चुनें):
   - A. Implement analog eavesdropping detectors
   - B. Use the ARPwatch utility to detect ARP spoofing
   - C. Enable ARP-spoofing detection in the switches
   - D. Use SRTP
8. Asterisk क्लाइंट प्रमाणपत्रों को सत्यापित करके मजबूत प्रमाणीकरण का समर्थन करता है। (PJSIP TLS ट्रांसपोर्ट क्लाइंट के प्रमाणपत्र को आवश्यक और सत्यापित कर सकता है।)
   - A. True
   - B. False
9. Asterisk 22 में, कौन सा PJSIP endpoint सेटिंग इन‑SDP (SDES) कुंजियों का उपयोग करके SRTP मीडिया एन्क्रिप्शन को सक्रिय करता है?
   - A. `encryption=yes`
   - B. `media_encryption=sdes`
   - C. `srtp=mandatory`
   - D. `transport=tls`
10. Asterisk 22 में, Fail2Ban को PJSIP failed‑authentication इवेंट्स को समर्पित ________ logger चैनल से पढ़ना चाहिए (जो `logger.conf` में सक्षम है)।
   - A. `console`
   - B. `messages`
   - C. `security`
   - D. `verbose`

**Answers:** 1 — D · 2 — A · 3 — C · 4 — B · 5 — B · 6 — A · 7 — B, C, D · 8 — A · 9 — B · 10 — C
