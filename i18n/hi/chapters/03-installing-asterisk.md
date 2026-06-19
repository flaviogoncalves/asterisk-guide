# Asterisk 22 इंस्टॉल करना

पहले अध्याय में, हमने टेलीफोनी वातावरण में Asterisk की उपयोगिता के बारे में थोड़ा जाना। इस अध्याय में, हम Asterisk को डाउनलोड और इंस्टॉल करने का तरीका जानेंगे। शुरू करने से पहले, इसे कंपाइल और इंस्टॉल करना सीखना आवश्यक है। कंपाइलेशन की प्रक्रिया पारंपरिक Microsoft™ Windows™ उपयोगकर्ताओं के लिए अजीब लग सकती है, लेकिन Linux™ वातावरण में यह काफी सामान्य है। Asterisk को कंपाइल करते समय आप अपने हार्डवेयर के लिए अनुकूलित (optimized) कोड प्राप्त कर सकते हैं, और हम यहाँ यही करेंगे। Asterisk कई ऑपरेटिंग सिस्टम में चलता है, लेकिन हमने चीजों को आसान रखने के लिए उनमें से केवल एक के साथ शुरुआत करने का निर्णय लिया है: Linux। हमने Linux™ वितरण के रूप में Debian को चुना है क्योंकि इसकी डिपेंडेंसी (dependencies) इंस्टॉल करना आसान है और यह वितरण स्थिर है, जिसका फुटप्रिंट भी कम है। यदि आप किसी अन्य वितरण का उपयोग करना चाहते हैं, तो कृपया डिपेंडेंसी के नाम तदनुसार बदल लें।

> **[2nd-ed note]** यह संस्करण **Asterisk 22 LTS** (2024 में जारी, 2028-10-16 तक पूर्ण समर्थन) को लक्षित करता है। Asterisk 22 वर्तमान लॉन्ग-टर्म सपोर्ट रिलीज़ है। ध्यान दें कि Digium का अधिग्रहण **Sangoma** (2018) द्वारा किया गया था, और अब Asterisk को Sangoma द्वारा प्रायोजित किया जाता है — इस पूरे अध्याय में "Digium" के संदर्भ विरासत हार्डवेयर के लिए पुराने ब्रांड को दर्शाते हैं।

## उद्देश्य

इस अध्याय के अंत तक आप निम्नलिखित में सक्षम होंगे:

- Asterisk के लिए हार्डवेयर आवश्यकताओं का निर्धारण करना;
- आवश्यक डिपेंडेंसी के साथ Linux इंस्टॉल करना;
- HTTPS के माध्यम से एक स्थिर संस्करण डाउनलोड करना;
- Asterisk को कंपाइल करना; और
- बूट समय पर Asterisk को शुरू करना सीखना।

## न्यूनतम आवश्यक हार्डवेयर

Asterisk को चलाने के लिए बहुत अधिक हार्डवेयर की आवश्यकता नहीं होती है, हालाँकि आपकी आवश्यकताओं के लिए सर्वोत्तम हार्डवेयर चुनने के लिए कुछ सुझाव दिए गए हैं। अपना हार्डवेयर चुनते समय आपको निम्नलिखित मुख्य कारकों पर विचार करना चाहिए:

- पंजीकृत उपयोगकर्ताओं की कुल संख्या। यह परिभाषित करें कि आपको प्रति सेकंड कितने पंजीकरणों का समर्थन करने की आवश्यकता है
- एक साथ होने वाली कॉलों की कुल संख्या। यह परिभाषित करें कि आपको Asterisk सर्वर पर नेटवर्क एडेप्टर और ब्रिज में कितनी नेटवर्क बातचीत को प्रोसेस करने की आवश्यकता है
- आपको किन कोडेक्स (codecs) का समर्थन करने की आवश्यकता है। उच्च जटिलता वाले कोडेक्स के लिए आपके सर्वर में बहुत अधिक CPU/FPU पावर की आवश्यकता होगी; उदाहरण के लिए, iLBC को इसके निर्माता (Global IP Sound) द्वारा TI C54x DSP पर 30 ms फ्रेम के लिए लगभग 18 MIPS प्रति चैनल (और 20 ms फ्रेम के लिए लगभग 15 MIPS) मापा गया था
- इको कैंसलेशन (Echo cancellation)। इको कैंसलेशन में बहुत अधिक CPU/FPU लग सकता है, कुछ मामलों में आपको टेलीफोनी इंटरफेस कार्ड में DSP का उपयोग करके हार्डवेयर इको कैंसलेशन चुनना चाहिए
- उपलब्धता। उपलब्धता बढ़ाने के लिए RAID1 या 5 का उपयोग करें। याद रखें, Asterisk एक 24x7 एप्लिकेशन है।

Asterisk सर्वर के लिए मुख्य घटक नेटवर्क एडेप्टर है। एक अच्छे सर्वर नेटवर्क एडेप्टर की सिफारिश की जाती है। जब आपको g.729 और iLBC जैसे उच्च जटिलता वाले कोडेक्स और इको कैंसलेशन का समर्थन करने की आवश्यकता होती है, तो CPU महत्वपूर्ण होता है। आप समर्पित DSP का उपयोग करना चुन सकते हैं, Sangoma (पूर्व में Digium) TC400B नामक एक DSP कार्ड प्रदान करता है जो 120 g729 एक साथ कॉलों का समर्थन करने में सक्षम है। सबसे अच्छा अभ्यास किसी ज्ञात निर्माता से एक नया, सर्वर-क्लास कंप्यूटर चुनना है। यह जानने के लिए कि कोई विशिष्ट मशीन वास्तव में कितनी एक साथ कॉलों या कितने पंजीकृत उपयोगकर्ताओं का समर्थन कर सकती है, आपको इस हार्डवेयर का SIPP (http://sipp.sourceforge.net) जैसे स्ट्रेस टेस्ट टूल के साथ परीक्षण करना चाहिए। Xorcom (http://www.xorcom.com) जैसे कुछ हार्डवेयर निर्माता अपनी वेबसाइट पर इसके परिणाम प्रकाशित करते हैं। नोट: कुछ Asterisk एप्लिकेशन, जैसे ConfBridge और music on hold, को एक आंतरिक टाइमिंग स्रोत की आवश्यकता होती है। आधुनिक Linux पर यह स्वचालित रूप से इन-बिल्ट `res_timing_timerfd` मॉड्यूल द्वारा प्रदान किया जाता है — किसी टेलीफोनी हार्डवेयर की आवश्यकता नहीं है। (पुराना `dahdi_dummy` सॉफ्टवेयर टाइमर अब मौजूद नहीं है; इसकी कार्यक्षमता DAHDI Linux 2.3.0 में मुख्य `dahdi` कर्नेल मॉड्यूल में शामिल कर दी गई थी।) आप CLI कमांड `timing test` के साथ सक्रिय टाइमर की पुष्टि कर सकते हैं।

### हार्डवेयर कॉन्फ़िगरेशन

Asterisk हार्डवेयर को बहुत परिष्कृत होने की आवश्यकता नहीं है। आपको महंगे वीडियो कार्ड या कई पेरिफेरल्स की आवश्यकता नहीं है। हार्डवेयर कॉन्फ़िगरेशन के बारे में कुछ सुझाव:

- अनावश्यक इंटरप्ट्स की खपत से बचने के लिए अप्रयुक्त USB, सीरियल और समानांतर पोर्ट को अक्षम करें।
- एक मजबूत नेटवर्क इंटरफेस कार्ड आवश्यक है।
- यदि आप टेलीफोनी इंटरफेस कार्ड का उपयोग कर रहे हैं तो विशेष सावधानी बरतें। कुछ कार्ड 3.3 वोल्ट PCI बस का उपयोग करते हैं, और उनके लिए मदरबोर्ड ढूंढना आसान नहीं है। आजकल, PCI express अधिक आसानी से मिल जाता है।
- हार्ड डिस्क पर विशेष ध्यान दें, PBX 24x7 शासन में काम करने के लिए उपयोग किया जाता है जबकि डेस्कटॉप 8x5 काम करते हैं। PBX के लिए डेस्कटॉप हार्डवेयर का उपयोग न करें, आमतौर पर हार्ड डिस्क पहले वर्ष से पहले ही विफल हो जाती है। मेरी सिफारिश एक सर्वर मशीन या 24x7 एप्लिकेशन चलाने के लिए डिज़ाइन किए गए उपकरण का उपयोग करने की है।

### IRQ शेयरिंग

टेलीफोनी इंटरफेस कार्ड (जैसे, X100P) बड़ी मात्रा में इंटरप्ट्स उत्पन्न करते हैं। इन इंटरप्ट्स को पूरा करने के लिए प्रोसेसर समय की आवश्यकता होती है। यदि आपके पास कोई अन्य डिवाइस उसी इंटरप्ट का उपयोग कर रहा है, तो ड्राइवर यह प्रोसेसिंग नहीं कर सकते हैं। एक सिंगल CPU सिस्टम में, आपको डिवाइसों के बीच IRQ शेयरिंग से बचना चाहिए। हम Asterisk चलाने के लिए समर्पित हार्डवेयर के उपयोग की सलाह देते हैं। किसी भी बाहरी या अनावश्यक हार्डवेयर को अक्षम करना न भूलें। कुछ हार्डवेयर को मदरबोर्ड BIOS सेटअप में अक्षम किया जा सकता है। एक बार जब आप अपना कंप्यूटर शुरू कर लेते हैं, तो /proc/interrupts में अपने असाइन किए गए इंटरप्ट्स देखें।

```
#cat /proc/interrupts
CPU0
0: 41353058 XT-PIC timer
1: 1988 XT-PIC keyboard
2: 0 XT-PIC cascade
3: 413437739 XT-PIC wctdm <-- TDM400
4: 5721494 XT-PIC eth0
7: 413453581 XT-PIC wcfxo <-- X100P
8: 1 XT-PIC rtc
9: 413445182 XT-PIC wcfxo <-- X100P
12: 0 XT-PIC PS/2 Mouse
14: 179578 XT-PIC ide0
15: 3 XT-PIC ide1
NMI: 0
ERR: 0
```

यहाँ आप तीन Digium कार्ड देख सकते हैं, प्रत्येक अपने स्वयं के IRQ में। यदि आपके सिस्टम में ऐसा है, तो आगे बढ़ें और हार्डवेयर ड्राइवर इंस्टॉल करें। यदि ऐसा नहीं है, तो वापस जाएं और IRQ शेयरिंग से बचने के लिए कुछ और प्रयास करें।

## Linux वितरण चुनना

Asterisk को शुरू में Linux पर चलने के लिए विकसित किया गया था। हालाँकि, यह BSD Unix या macOS पर भी चल सकता है। यदि आप Asterisk में नए हैं, तो पहले Linux का उपयोग करने का प्रयास करें क्योंकि यह बहुत आसान है। Asterisk आधिकारिक तौर पर RHEL परिवार (CentOS/RHEL/Fedora), Ubuntu, और Debian को लक्षित करता है। आज अच्छे व्यावहारिक विकल्प **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, और **Rocky Linux 9 / AlmaLinux 9** हैं — CentOS Linux का जीवनकाल समाप्त हो चुका है, इसलिए RHEL-परिवार के सिस्टम पर Rocky या AlmaLinux को प्राथमिकता दें। इस पुस्तक के लिए मैं Ubuntu 24.04 LTS का उपयोग करूँगा। नीचे दी गई आधिकारिक रिलीज़ निर्देशिका से नवीनतम 24.04 पॉइंट-रिलीज़ सर्वर इमेज डाउनलोड करें (सटीक फ़ाइल नाम में वर्तमान पॉइंट रिलीज़ शामिल है, उदाहरण के लिए `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Asterisk के लिए Linux तैयार करना

Asterisk इंस्टॉल करने के तुरंत बाद, हम Asterisk और DAHDI ड्राइवरों के बाद के कंपाइलेशन के लिए आवश्यक पैकेज इंस्टॉल करेंगे। सबसे पहले, हम Debian को बताएंगे कि पैकेज कहाँ से डाउनलोड किए जाएंगे। यह apt-setup यूटिलिटी का उपयोग करके किया जाता है। चरण 1: वर्चुअल मशीन में Ubuntu 24.04 LTS सर्वर इंस्टॉल करें (64-बिट इमेज का उपयोग करें; इस पुस्तक में उपयोग किए गए वितरण 64-बिट हैं, हालाँकि Asterisk स्वयं अभी भी 32-बिट x86 का समर्थन करता है)। हमने इस प्रशिक्षण के लिए VirtualBox का उपयोग किया है। आप https://releases.ubuntu.com/24.04 से इमेज डाउनलोड कर सकते हैं। Linux इंस्टॉलेशन इस प्रशिक्षण के दायरे से बाहर है। Linux का बुनियादी ज्ञान इस प्रशिक्षण के लिए पूर्वापेक्षा है।

## Asterisk के लिए Linux इंस्टॉल करना

अपने Linux को सामान्य रूप से इंस्टॉल करें, बिना ग्राफिकल यूजर इंटरफेस के। ईमेल सर्वर को भी इंस्टॉल और कॉन्फ़िगर करें। हमें इस पुस्तक में बाद में वॉइसमेल नोटिफिकेशन भेजने के लिए ईमेल सर्वर (exim4) की आवश्यकता होगी। सावधानी: यह इंस्टॉलेशन आपके PC को फॉर्मेट कर देगा। आपका सारा डिस्क डेटा मिटा दिया जाएगा। कृपया शुरू करने से पहले सभी डेटा का बैकअप लेना सुनिश्चित करें। चरण 1: CD को CD-ROM ड्राइव में डालें और अपने PC को बूट करें। अधिकांश प्रश्नों के उत्तर देना बहुत सरल है।

## डिपेंडेंसी इंस्टॉल करना

Asterisk और DAHDI इंस्टॉल करने के लिए आपको कई सॉफ्टवेयर डिपेंडेंसी इंस्टॉल करनी होंगी। Asterisk 22 में ऐसा करने का अनुशंसित तरीका सोर्स ट्री के साथ आने वाली स्क्रिप्ट का उपयोग करना है, जो प्रत्येक समर्थित वितरण के लिए सही पैकेज नाम जानती है। Asterisk सोर्स को डाउनलोड और एक्सट्रैक्ट करने के बाद (नीचे "Asterisk को कंपाइल करना" देखें), चलाएँ:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

चरण 1: रूट के रूप में लॉगिन करें (या `sudo` का उपयोग करें)। चरण 2: यदि आप Debian/Ubuntu सिस्टम पर मैन्युअल रूप से डिपेंडेंसी इंस्टॉल करना पसंद करते हैं, तो समकक्ष पैकेज सूची है:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf
```

> **[2nd-ed note]** मूल सूची में `subversion`, `libnewt-dev`, और `libncurses5-dev` का संदर्भ दिया गया था। Asterisk सोर्स अब Git पर होस्ट किया गया है (subversion की अब आवश्यकता नहीं है), और आधुनिक Debian/Ubuntu वर्शन्ड `libncurses5-dev` के बजाय `libncurses-dev` शिप करते हैं। हाथ से बनाए रखी गई सूची के बजाय `./contrib/scripts/install_prereq install` को प्राथमिकता दें।

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) एनालॉग और डिजिटल कार्ड के लिए ड्राइवरों का आर्किटेक्चर है। Asterisk इंस्टॉल करने से पहले, यदि आप एनालॉग या डिजिटल इंटरफेस का उपयोग करने की योजना बना रहे हैं, तो DAHDI इंस्टॉल करना महत्वपूर्ण है। DAHDI अभी भी एनालॉग/डिजिटल टेलीफोनी कार्ड के लिए मौजूद है लेकिन तेजी से विशिष्ट (niche) होता जा रहा है — अधिकांश आधुनिक परिनियोजन शुद्ध VoIP हैं और इस अनुभाग को पूरी तरह से छोड़ सकते हैं। DAHDI केवल तभी इंस्टॉल करें जब आपके पास भौतिक टेलीफोनी इंटरफेस हार्डवेयर हो। सोर्स फ़ाइलें प्राप्त करने के लिए उपयोग करें:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

फ़ाइलों को अनकंप्रेस करने के लिए उपयोग करें:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### DAHDI ड्राइवरों को कंपाइल करना

आपको DAHDI मॉड्यूल को कंपाइल करने की आवश्यकता होगी। ./configure और make menuselect कमांड कई साल पहले पेश किए गए थे। बाद वाला आपको यह चुनने में सक्षम बनाता है कि कौन सी यूटिलिटी और मॉड्यूल बनाने हैं। निम्नलिखित कमांड ऐसा करेंगे:

```
cd dahdi-linux-complete-X.Y.Z+X.Y.Z/linux   # adapt to the version downloaded
make
make install
cd ../tools
autoreconf -i
./configure
make
make install
```

make install-config DAHDI को कॉन्फ़िगर कर दिया गया है। यदि आपके पास कोई DAHDI हार्डवेयर है, तो अब यह अनुशंसा की जाती है कि आप इस सिस्टम में इंस्टॉल किए गए DAHDI हार्डवेयर के लिए ही समर्थन लोड करने के लिए /etc/dahdi/modules को संपादित करें। डिफ़ॉल्ट रूप से, DAHDI शुरू होने पर सभी DAHDI हार्डवेयर के लिए समर्थन लोड किया जाता है। मुझे लगता है कि आपके सिस्टम पर जो DAHDI हार्डवेयर है वह है: usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware यह स्क्रीन (ऊपर) आपसे आपके विशिष्ट कॉन्फ़िगरेशन के लिए केवल आवश्यक ड्राइवरों को लोड करने के लिए /etc/dahdi/modules फ़ाइल को बदलने और पता लगाए गए हार्डवेयर को दिखाने के लिए कहती है। /etc/dahdi/modules फ़ाइल को संपादित करें और केवल आवश्यक हार्डवेयर लोड करें। मेरे मामले में, मैं Xorcom Astribank 6FXS और 2FXO वाली एक टेस्ट मशीन का उपयोग कर रहा था। फ़ाइल नीचे दिखाई गई है।

```
# Contains the list of modules to be loaded / unloaded by /etc/init.d/dahdi.
#
# NOTE:  Please add/edit /etc/modprobe.d/dahdi or /etc/modprobe.conf if you
#        would like to add any module parameters.
#
# Format of this file: list of modules, each in its own line.
# Anything after a '#' is ignore, likewise trailing and leading
# whitespaces and empty lines.
# Digium TE205P/TE207P/TE210P/TE212P: PCI dual-port T1/E1/J1
# Digium TE405P/TE407P/TE410P/TE412P: PCI quad-port T1/E1/J1
# Digium TE220: PCI-Express dual-port T1/E1/J1
# Digium TE420: PCI-Express quad-port T1/E1/J1
#wct4xxp
# Digium TE120P: PCI single-port T1/E1/J1
# Digium TE121: PCI-Express single-port T1/E1/J1
# Digium TE122: PCI single-port T1/E1/J1
#wcte12xp
# Digium T100P: PCI single-port T1
# Digium E100P: PCI single-port E1
#wct1xxp
# Digium TE110P: PCI single-port T1/E1/J1
#wcte11xp
# Digium TDM2400P/AEX2400: up to 24 analog ports
# Digium TDM800P/AEX800: up to 8 analog ports
# Digium TDM410P/AEX410: up to 4 analog ports
#wctdm24xxp
# X100P - Single port FXO interface
# X101P - Single port FXO interface
#wcfxo
# Digium TDM400P: up to 4 analog ports
#wctdm
# Xorcom Astribank Devices
xpp_usb
```

अपने कंप्यूटर को री-इनिशियलाइज़ करें और ड्राइवरों के सही लोडिंग को सत्यापित करें।

## कौन सा संस्करण चुनें

अंगूठे के नियम के रूप में, आपको आवश्यक सुविधाओं वाले संस्करण का उपयोग करना चाहिए। Asterisk LTS (लॉन्ग-टर्म सपोर्ट) और मानक रिलीज़ के वैकल्पिक रिलीज़ मॉडल का पालन करता है। इस संस्करण के समय, **Asterisk 22 वर्तमान LTS रिलीज़ है** (2024 में जारी, 2028 तक समर्थित), जो इसे अभी चुनने के लिए सबसे अच्छा बनाता है। Asterisk 20 पिछला LTS है, और संस्करण 16 (पहले संस्करण में उपयोग किया गया) का जीवनकाल समाप्त हो चुका है। प्रोडक्शन सिस्टम के लिए, हमेशा एक LTS रिलीज़ चुनें।

> **[2nd-ed note]** प्रिंट करने से पहले downloads.asterisk.org पर सटीक वर्तमान पॉइंट रिलीज़ को सत्यापित करें। इस लेखन के समय 22 शाखा सक्रिय LTS है।

## Asterisk को कंपाइल करना

यदि आपने पहले सॉफ्टवेयर कंपाइल किया है, तो Asterisk को कंपाइल करना एक आसान काम होगा। Asterisk को कंपाइल और इंस्टॉल करने के लिए निम्नलिखित कमांड चलाएँ। याद रखें, आप make menuselect का उपयोग करके चुन सकते हैं कि कौन से एप्लिकेशन और मॉड्यूल बनाने हैं। चरण 1: सोर्स कोड डाउनलोड करें

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

चरण 2: बिल्ड पूर्वापेक्षाएँ इंस्टॉल करें (ऊपर "डिपेंडेंसी इंस्टॉल करना" देखें)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

चरण 3: बिल्ड को कॉन्फ़िगर करें

```
./configure
```

चरण 4: बनाने के लिए मॉड्यूल चुनें

```
make menuselect
```

केवल आवश्यक मॉड्यूल इंस्टॉल करने के लिए make menuselect का उपयोग करें। Asterisk 22 में SIP चैनल **chan_pjsip** है (डिफ़ॉल्ट रूप से निर्मित); पुराना **chan_sip** Asterisk 21 में हटा दिया गया था और अब मौजूद नहीं है। Opus *pass-through* बॉक्स के बाहर काम करता है (इन-ट्री `res_format_attr_opus` मॉड्यूल SDP नेगोशिएशन को संभालता है), लेकिन **codec_opus** ट्रांसकोडिंग मॉड्यूल अभी भी Sangoma/Digium से एक बाहरी, क्लोज्ड-सोर्स बाइनरी है — इसे menuselect में चुनने पर यह Digium के सर्वर से डाउनलोड हो जाता है। बाइनरी निःशुल्क है। विवरण के लिए नीचे "menuselect के साथ मॉड्यूल चुनना" देखें।

चरण 5: Asterisk को बिल्ड और इंस्टॉल करें, फिर डिफ़ॉल्ट कॉन्फ़िग और सैंपल फ़ाइलें बनाएँ

```
make
make install
make samples
make config
ldconfig
```

`make install` बाइनरी और मॉड्यूल इंस्टॉल करता है, `make samples` सैंपल कॉन्फ़िगरेशन फ़ाइलों को `/etc/asterisk` में लिखता है, `make config` आपके पता लगाए गए वितरण के लिए SysV init स्टार्टअप स्क्रिप्ट इंस्टॉल करता है (उदाहरण के लिए Debian/Ubuntu पर `/etc/init.d/asterisk`), और `ldconfig` शेयर्ड-लाइब्रेरी कैश को रिफ्रेश करता है। एक systemd यूनिट भी सोर्स ट्री में `contrib/systemd/asterisk.service` पर शिप होती है, लेकिन `make config` इसे स्वचालित रूप से इंस्टॉल नहीं करता है — यदि आप systemd के तहत Asterisk चलाना पसंद करते हैं तो इसे स्वयं कॉपी करें (नीचे देखें)।

### menuselect के साथ मॉड्यूल चुनना

`make menuselect` एक टेक्स्ट-आधारित मेनू खोलता है जहाँ आप चुनते हैं कि वास्तव में कौन से एप्लिकेशन, कोडेक्स, चैनल और संसाधन बनाने हैं। Asterisk 22 के लिए विशिष्ट कुछ नोट्स:

- **chan_pjsip** (*Channel Drivers* के तहत) आधुनिक SIP चैनल है और डिफ़ॉल्ट रूप से सक्षम है; यह Asterisk 22 में एकमात्र SIP चैनल है।
- **codec_opus** (*Codec Translators* के तहत) एक **बाहरी** मॉड्यूल है (इसकी menuselect प्रविष्टि "Download the Opus codec from Digium" पढ़ती है); इसे सक्षम करने से `make` Sangoma/Digium से मुफ्त, क्लोज्ड-सोर्स बाइनरी को फेच करता है। Opus pass-through को किसी अतिरिक्त मॉड्यूल की आवश्यकता नहीं है। Sangoma का **codec_g729** मॉड्यूल भी उपलब्ध है — बाइनरी डाउनलोड करने के लिए मुफ्त है, लेकिन वैध G.729 ट्रांसकोडिंग के लिए खरीदे गए प्रति-चैनल लाइसेंस की आवश्यकता होती है।
- *Core Sound Packages*, *Music On Hold File Packages*, और *Extras Sound Packages* मेनू में उन साउंड फॉर्मेट और भाषाओं को चुनें जिन्हें आप चाहते हैं; आप वहाँ जो कुछ भी चेक करते हैं, वह `make install` के दौरान स्वचालित रूप से डाउनलोड और इंस्टॉल हो जाता है।

अपने चयन करने के बाद, **Save & Exit** चुनें और `make` के साथ जारी रखें।

> **[2nd-ed note]** Asterisk 22 से कैप्चर किया गया एक नया `make menuselect` स्क्रीनशॉट डालें (पहले संस्करण के स्क्रीनशॉट में chan_sip/chan_skinny/chan_mgcp दिखाया गया था, जो अब मौजूद नहीं हैं)। Channel Drivers स्क्रीन में chan_pjsip दिखना चाहिए और chan_sip नहीं।

## Asterisk को शुरू और बंद करना

इस न्यूनतम कॉन्फ़िगरेशन के साथ, Asterisk को सफलतापूर्वक शुरू करना संभव है। सीखने और डिबगिंग के लिए, आप Asterisk को कंसोल से जुड़े हुए फोरग्राउंड में शुरू कर सकते हैं:

```
/usr/sbin/asterisk –vvvgc
```

Asterisk को शटडाउन करने के लिए CLI कमांड stop now का उपयोग करें।

```
CLI>core stop now
```

### systemd के साथ Asterisk शुरू करना

आधुनिक Linux वितरणों (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9) पर, सिस्टम सर्विस मैनेजर **systemd** है। Asterisk सोर्स ट्री में `contrib/systemd/asterisk.service` पर एक systemd यूनिट शिप करता है; इसे `/etc/systemd/system/asterisk.service` पर कॉपी करें और `systemctl daemon-reload` चलाएँ। एक बार इंस्टॉल हो जाने के बाद, प्रोडक्शन में Asterisk चलाने का अनुशंसित तरीका `systemctl` के माध्यम से है:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

एक बार जब Asterisk एक सर्विस के रूप में चल रहा हो, तो इसके CLI से `asterisk -r` (कनेक्ट) या `asterisk -rvvv` (वर्बोस आउटपुट के साथ कनेक्ट) के साथ जुड़ें।

> **[2nd-ed note]** पुराने सिस्टम पर Asterisk को लेगेसी SysV init स्क्रिप्ट (`/etc/init.d/asterisk`) और **safe_asterisk** रैपर के माध्यम से शुरू किया गया था, जो क्रैश होने पर Asterisk को स्वचालित रूप से पुनरारंभ करता था। systemd के साथ, स्वचालित पुनरारंभ यूनिट फ़ाइल के `Restart=` निर्देश द्वारा संभाला जाता है, इसलिए `safe_asterisk` की आमतौर पर अब आवश्यकता नहीं है। लेगेसी init/`safe_asterisk` दृष्टिकोण अभी भी काम करता है लेकिन systemd-आधारित वितरणों पर इसे बहिष्कृत (deprecated) कर दिया गया है।

### Asterisk रनटाइम विकल्प

Asterisk शुरू करने की प्रक्रिया बहुत सरल है। यदि Asterisk को बिना किसी पैरामीटर के चलाया जाता है, तो इसे डेमन के रूप में लॉन्च किया जाता है।

```
/sbin/asterisk
```

आप निम्नलिखित कमांड निष्पादित करके Asterisk कंसोल तक पहुँच सकते हैं। कृपया ध्यान दें कि एक ही समय में एक से अधिक कंसोल प्रक्रियाएं चलाई जा सकती हैं।

```
/sbin/asterisk -r
```

### Asterisk के लिए उपलब्ध रनटाइम विकल्प

आप asterisk –h का उपयोग करके उपलब्ध रनटाइम विकल्प दिखा सकते हैं

```
sipast:/usr/src/asterisk-22.x.y# asterisk -h
```

Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others. Usage: asterisk [OPTIONS] Valid Options: -V Display version number and exit -C <configfile> Use an alternate configuration file -G <group> Run as a group other than the caller -U <user> Run as a user other than the caller -c Provide console CLI -d Increase debugging (multiple d's = more debugging) -f Do not fork -F Always fork -g Dump core in case of a crash -h This help screen -i Initialize crypto keys at startup -L <load> Limit the maximum load average before rejecting new calls -M <value> Limit the maximum number of calls to the specified value -m Mute debugging and console output on the console -n Disable console colorization. Can be used only at startup. -p Run as pseudo-realtime thread -q Quiet mode (suppress output) -r Connect to Asterisk on this machine -R Same as -r, except attempt to reconnect if disconnected -s <socket> Connect to Asterisk via socket <socket> (only valid with -r) -t Record soundfiles in /var/tmp and move them where they belong after they are done -T Display the time in [Mmm dd hh:mm:ss] format for each line of output to the CLI. Cannot be used with remote console mode. -v Increase verbosity (multiple v's = more verbose) -x <cmd> Execute command <cmd> (implies -r) -X Enable use of #exec in asterisk.conf -W Adjust terminal colors to compensate for a light background

## इंस्टॉलेशन निर्देशिकाएँ

Asterisk कई निर्देशिकाओं में इंस्टॉल होता है, जिन्हें asterisk.conf फ़ाइल में संशोधित किया जा सकता है। प्रशिक्षण उद्देश्यों के लिए मैं वर्बोस को 3 से 15 में बदल दूँगा, प्रोडक्शन के लिए इसे 3 में रखें। max_calls और max_load विकल्प आपके सिस्टम को ओवरलोडिंग से बचाने के लिए अच्छे विकल्प हैं।

### asterisk.conf

```
[directories](!) ; remove the (!) to enable this
astetcdir => /etc/asterisk
astmoddir => /usr/lib/asterisk/modules
astvarlibdir => /var/lib/asterisk
astdbdir => /var/lib/asterisk
astkeydir => /var/lib/asterisk
astdatadir => /var/lib/asterisk
astagidir => /var/lib/asterisk/agi-bin
astspooldir => /var/spool/asterisk
astrundir => /var/run/asterisk
astlogdir => /var/log/asterisk
astsbindir => /usr/sbin
[options]
;verbose = 3
;debug = 3
;refdebug = yes                 ; Enable reference count debug logging.
;alwaysfork = yes               ; Same as -F at startup.
;nofork = yes                   ; Same as -f at startup.
;quiet = yes                    ; Same as -q at startup.
;timestamp = yes                ; Same as -T at startup.
;execincludes = yes             ; Support #exec in config files.
;console = yes                  ; Run as console (same as -c at startup).
;highpriority = yes             ; Run realtime priority (same as -p at
                                ; startup).
;initcrypto = yes               ; Initialize crypto keys (same as -i at
                                ; startup).
;nocolor = yes                  ; Disable console colors.
;dontwarn = yes                 ; Disable some warnings.
;dumpcore = yes                 ; Dump core on crash (same as -g at startup).
;languageprefix = yes           ; Use the new sound prefix path syntax.
;systemname = my_system_name    ; Prefix uniqueid with a system name for
                                ; Global uniqueness issues.
;autosystemname = yes           ; Automatically set systemname to hostname,
                                ; uses 'localhost' on failure, or systemname if
                                ; set.
;mindtmfduration = 80           ; Set minimum DTMF duration in ms (default 80
ms)
                                ; If we get shorter DTMF messages, these will
be
                                ; changed to the minimum duration
;maxcalls = 10                  ; Maximum amount of calls allowed.
;maxload = 0.9                  ; Asterisk stops accepting new calls if the
                                ; load average exceed this limit.
;maxfiles = 1000                ; Maximum amount of openfiles.
;minmemfree = 1                 ; In MBs, Asterisk stops accepting new calls if
                                ; the amount of free memory falls below this
                                ; watermark.
;cache_media_frames = yes       ; Cache media frames for performance
                                ; Disable this option to help track down media
frame
                                ; mismanagement when using valgrind or
MALLOC_DEBUG.
                                ; The cache gets in the way of determining if
the
                                ; frame is used after being freed and who freed
it.
                                ; NOTE: This option has no effect when Asterisk
is
                                ; compiled with the LOW_MEMORY compile time
option
                                ; enabled because the cache code does not
exist.
                                ; Default yes
;cache_record_files = yes       ; Cache recorded sound files to another
                                ; directory during recording.
;record_cache_dir = /tmp        ; Specify cache directory (used in conjunction
                                ; with cache_record_files).
;transmit_silence = yes         ; Transmit silence while a channel is in a
                                ; waiting state, a recording only state, or
                                ; when DTMF is being generated.  Note that the
                                ; silence internally is generated in raw signed
                                ; linear format. This means that it must be
                                ; transcoded into the native format of the
                                ; channel before it can be sent to the device.
                                ; It is for this reason that this is optional,
                                ; as it may result in requiring a temporary
                                ; codec translation path for a channel that may
                                ; not otherwise require one.
;transcode_via_sln = yes        ; Build transcode paths via SLINEAR, instead of
                                ; directly.
;runuser = asterisk             ; The user to run as.
;rungroup = asterisk            ; The group to run as.
;lightbackground = yes          ; If your terminal is set for a light-colored
                                ; background.
;forceblackbackground = yes     ; Force the background of the terminal to be
                                ; black, in order for terminal colors to show
                                ; up properly.
;defaultlanguage = en           ; Default language
documentation_language = en_US  ; Set the language you want documentation
                                ; displayed in. Value is in the same format as
                                ; locale names.
;hideconnect = yes              ; Hide messages displayed when a remote console
                                ; connects and disconnects.
;lockconfdir = no               ; Protect the directory containing the
                                ; configuration files (/etc/asterisk) with a
                                ; lock.
;live_dangerously = no          ; Enable the execution of 'dangerous' dialplan
                                ; functions from external sources (AMI,
                                ; etc.) These functions (such as SHELL) are
                                ; considered dangerous because they can allow
                                ; privilege escalation.
                                ; Default no
;entityid=00:11:22:33:44:55     ; Entity ID.
                                ; This is in the form of a MAC address.
                                ; It should be universally unique.
                                ; It must be unique between servers
communicating
                                ; with a protocol that uses this value.
                                ; This is currently is used by DUNDi and
                                ; Exchanging Device and Mailbox State
                                ; using protocols: XMPP, Corosync and PJSIP.
;rtp_use_dynamic = yes          ; When set to "yes" RTP dynamic payload types
                                ; are assigned dynamically per RTP instance vs.
                                ; allowing Asterisk to globally initialize them
                                ; to pre-designated numbers (defaults to
"yes").
;rtp_pt_dynamic = 35            ; Normally the Dynamic RTP Payload Type numbers
                                ; are 96-127, which allow just 32 formats. The
                                ; starting point 35 enables the range 35-63 and
                                ; allows 29 additional formats. When you use
                                ; more than 32 formats in the dynamic range and
                                ; calls are not accepted by a remote
                                ; implementation, please report this and go
                                ; back to value 96.
; Changing the following lines may compromise your security.
;[files]
;astctlpermissions = 0660
;astctlowner = root
;astctlgroup = apache
;astctl = asterisk.ctl
```

## लॉग फ़ाइलें और लॉग रोटेशन

Asterisk PBX अपने संदेशों को /var/log/asterisk निर्देशिका में लॉग करता है। वह फ़ाइल जो लॉग को नियंत्रित करती है

```
is the logger.conf.
;
; Logging Configuration
;
; In this file, you configure logging to files or to
; the syslog system.
;
; "logger reload" at the CLI will reload configuration
; of the logging system.
[general]
;
; Customize the display of debug message time stamps
; this example is the ISO 8601 date format (yyyy-mm-dd HH:MM:SS)
;
; see strftime(3) Linux manual for format specifiers.  Note that there is also
; a fractional second parameter which may be used in this field.  Use %1q
; for tenths, %2q for hundredths, etc.
;
;dateformat=%F %T       ; ISO 8601 date format
;dateformat=%F %T.%3q   ; with milliseconds
;
;
; This makes Asterisk write callids to log messages
; (defaults to yes)
;use_callids = no
;
; This appends the hostname to the name of the log files.
;appendhostname = yes
;
; This determines whether or not we log queue events to a file
; (defaults to yes).
;queue_log = no
;
; Determines whether the queue_log always goes to a file, even
; when a realtime backend is present (defaults to no).
;queue_log_to_file = yes
;
; Set the queue_log filename
; (defaults to queue_log)
;queue_log_name = queue_log
;
; When using realtime for the queue log, use GMT for the timestamp
; instead of localtime.  The default of this option is 'no'.
;queue_log_realtime_use_gmt = yes
;
; Log rotation strategy:
; none:  Do not perform any logrotation at all.  You should make
;        very sure to set up some external logrotate mechanism
;        as the asterisk logs can get very large, very quickly.
; sequential:  Rename archived logs in order, such that the newest
;              has the highest sequence number [default].  When
;              exec_after_rotate is set, ${filename} will specify
;              the new archived logfile.
; rotate:  Rotate all the old files, such that the oldest has the
;          highest sequence number [this is the expected behavior
;          for Unix administrators].  When exec_after_rotate is
;          set, ${filename} will specify the original root filename.
; timestamp:  Rename the logfiles using a timestamp instead of a
;             sequence number when "logger rotate" is executed.
;             When exec_after_rotate is set, ${filename} will
;             specify the new archived logfile.
;rotatestrategy = rotate
;
; Run a system command after rotating the files.  This is mainly
; useful for rotatestrategy=rotate. The example allows the last
; two archive files to remain uncompressed, but after that point,
; they are compressed on disk.
;
; exec_after_rotate=gzip -9 ${filename}.2
;
;
; For each file, specify what to log.
;
; For console logging, you set options at start of
; Asterisk with -v for verbose and -d for debug
; See 'asterisk -h' for more information.
;
; Directory for log files is configures in asterisk.conf
; option astlogdir
;
; All log messages go to a queue serviced by a single thread
; which does all the IO.  This setting controls how big that
; queue can get (and therefore how much memory is allocated)
; before new messages are discarded.
; The default is 1000
;logger_queue_limit = 250
;
;
[logfiles]
;
; Format is:
;
; logger_name => [formatter]levels
;
; The name of the logger dictates not only the name of the logging
; channel, but also its type. Valid types are:
;   - 'console'  - The root console of Asterisk
;   - 'syslog'   - Linux syslog, with facilities specified afterwards with
;                  a period delimiter, e.g., 'syslog.local0'
;   - 'filename' - The name of the log file to create. This is the default
;                  for log channels.
;
; Filenames can either be relative to the standard Asterisk log directory
; (see 'astlogdir' in asterisk.conf), or absolute paths that begin with
; '/'.
;
; An optional formatter can be specified prior to the log levels sent
; to the log channel. The formatter is defined immediately preceeding the
; levels, and is enclosed in square brackets. Valid formatters are:
;   - [default] - The default formatter, this outputs log messages using a
;                 human readable format.
;   - [json]    - Log the output in JSON. Note that JSON formatted log entries,
;                 if specified for a logger type of 'console', will be formatted
;                 per the 'default' formatter for log messages of type VERBOSE.
;                 This is due to the remote consoles intepreting verbosity
;                 outside of the logging subsystem.
;
; Log levels include the following, and are specified in a comma delineated
; list:
;    debug
;    notice
;    warning
;    error
;    verbose(<level>)
;    dtmf
;    fax
;    security
;
; Verbose takes an optional argument, in the form of an integer level.
; Verbose messages with higher levels will not be logged to the file.  If
; the verbose level is not specified, it will log verbose messages following
; the current level of the root console.
;
; Special level name "*" means all levels, even dynamic levels registered
; by modules after the logger has been initialized (this means that loading
; and unloading modules that create/remove dynamic logger levels will result
; in these levels being included on filenames that have a level name of "*",
; without any need to perform a 'logger reload' or similar operation).
; Note that there is no value in specifying both "*" and specific level names
; for a filename; the "*" level means all levels.  The only exception is if
; you need to specify a specific verbose level. e.g, "verbose(3),*".
;
; We highly recommend that you DO NOT turn on debug mode if you are simply
; running a production system.  Debug mode turns on a LOT of extra messages,
; most of which you are unlikely to understand without an understanding of
; the underlying code.  Do NOT report debug messages as code issues, unless
; you have a specific issue that you are attempting to debug.  They are
; messages for just that -- debugging -- and do not rise to the level of
; something that merit your attention as an Asterisk administrator.  Debug
; messages are also very verbose and can and do fill up logfiles quickly;
; this is another reason not to have debug mode on a production system unless
; you are in the process of debugging a specific issue.
;
;debug => debug
;security => security
console => notice,warning,error
;console => notice,warning,error,debug
messages => notice,warning,error
;full => notice,warning,error,debug,verbose,dtmf,fax
;
;full-json => [json]debug,verbose,notice,warning,error,dtmf,fax
;
;syslog keyword : This special keyword logs to syslog facility
;
;syslog.local0 => notice,warning,error
```

; कुछ कंसोल कमांड लॉगर प्रक्रिया से जुड़े होते हैं।

```
CLI> logger show channels
Logger queue limit: 1000

Channel                             Type     Formatter  Status    Configuration
-------                             ----     ---------  ------    -------------
/var/log/asterisk/security          File     default    Enabled    - SECURITY
/var/log/asterisk/full              File     default    Enabled    - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages          File     default    Enabled    - NOTICE WARNING ERROR
CLI> logger rotate
  == Parsing '/etc/asterisk/logger.conf': Found
Asterisk Event Logger restarted
Asterisk Queue Logger restarted
You can control the log rotation using the logrotate daemon. Edit the file
/etc/logrotate.d and include the content below to start rotating the log files.
/var/log/asterisk/messages /var/log/asterisk/*log {
   missingok
   rotate 5
   weekly
   create 0640 asterisk asterisk
   postrotate
       /usr/sbin/asterisk -rx 'logger reload'
   endscript
}
```

logrotate के बारे में अधिक जानकारी प्राप्त की जा सकती है:

```
#man logrotate
```

## Asterisk को अनइंस्टॉल करना

Asterisk को अनइंस्टॉल करने के लिए, उपयोग करें:

```
make uninstall
```

Asterisk और सभी कॉन्फ़िगरेशन फ़ाइलों को अनइंस्टॉल करने के लिए, उपयोग करें:

```
make uninstall-all
```

## Asterisk इंस्टॉलेशन नोट्स

यह अनुभाग Asterisk इंस्टॉल करने से पहले संबोधित करने वाले मुद्दों के बारे में कुछ सलाह प्रदान करेगा।

### प्रोडक्शन सिस्टम

यदि Asterisk को प्रोडक्शन वातावरण में इंस्टॉल किया जाता है, तो आपको सिस्टम डिज़ाइन पर ध्यान देना चाहिए। एक सर्वर को इस तरह से अनुकूलित किया जाना चाहिए कि टेलीफोनी सिस्टम को अन्य सिस्टम प्रक्रियाओं पर प्राथमिकता मिले। Asterisk को X-Windows जैसे प्रोसेसर-गहन सॉफ्टवेयर के साथ नहीं चलना चाहिए। यदि आपको CPU-गहन प्रक्रियाओं (जैसे, एक विशाल डेटाबेस) को चलाने की आवश्यकता है, तो एक अलग सर्वर का उपयोग करें। सामान्य तौर पर, Asterisk हार्डवेयर प्रदर्शन विविधताओं के प्रति संवेदनशील है। इसलिए, Asterisk का उपयोग ऐसे हार्डवेयर वातावरण में करने का प्रयास करें जिसे 40% से अधिक CPU उपयोग की आवश्यकता न हो।

### नेटवर्क टिप्स

यदि आप IP फोन का उपयोग करने की योजना बना रहे हैं, तो यह महत्वपूर्ण है कि आप अपने नेटवर्क पर ध्यान दें। वॉयस प्रोटोकॉल बहुत अच्छे हैं और विलंबता (latency) और यहां तक कि जिटर (jitters) के प्रति प्रतिरोधी हैं; हालाँकि, यदि आप खराब तरीके से कॉन्फ़िगर किए गए लोकल एरिया नेटवर्क का उपयोग करते हैं, तो वॉयस क्वालिटी प्रभावित होगी। स्विच और राउटर में क्वालिटी ऑफ सर्विस (QoS) का उपयोग करके ही अच्छी वॉयस क्वालिटी की गारंटी देना संभव है। लोकल एरिया नेटवर्क में वॉयस अच्छी होती है, लेकिन LAN वातावरण में भी, यदि आपके पास बहुत अधिक टकराव (collisions) वाले 10 Mbps हब हैं, तो आपको अंततः विकृत या खराब वॉयस मिलेगी। सर्वोत्तम संभव वॉयस क्वालिटी सुनिश्चित करने के लिए इन सिफारिशों का पालन करें:

- यदि संभव हो या आर्थिक रूप से व्यवहार्य हो तो एंड-टू-एंड QoS का उपयोग करें। एंड-टू-एंड QoS के साथ, वॉयस क्वालिटी एकदम सही होती है। कोई बहाना नहीं!
- प्रोडक्शन वातावरण में वॉयस के लिए 10/100 Mbps हब का उपयोग करने से बचें। टकराव नेटवर्क पर जिटर लगा सकते हैं। फुल डुप्लेक्स 10/100 Mbps को प्राथमिकता दी जाती है क्योंकि कोई टकराव नहीं होता है।
- वॉयस नेटवर्क के अनावश्यक प्रसारणों को अलग करने के लिए VLANs का उपयोग करें। आप नहीं चाहेंगे कि कोई वायरस ARP प्रसारण के साथ आपके वॉयस नेटवर्क को नष्ट कर दे।
- वॉयस नेटवर्क में अपेक्षाओं के बारे में उपयोगकर्ताओं को शिक्षित करें। QoS के बिना, यह न कहें कि वॉयस एकदम सही होगी क्योंकि ज्यादातर मामलों में ऐसा नहीं होगा। मोबाइल फोन के समान वॉयस क्वालिटी अक्सर प्राप्त की जाएगी। गुणवत्तापूर्ण फोन का उपयोग करें क्योंकि फर्मवेयर और हार्डवेयर डिज़ाइन के साथ समस्याएं आम हैं।

## सारांश

इस अध्याय में, आपने न्यूनतम हार्डवेयर आवश्यकताओं के साथ-साथ Asterisk को डाउनलोड, इंस्टॉल और कंपाइल करने के तरीके के बारे में सीखा है। सुरक्षा कारणों से Asterisk को नॉन-रूट उपयोगकर्ता के साथ निष्पादित किया जाना चाहिए। प्रोडक्शन वातावरण शुरू करने से पहले आपको अपने नेटवर्क वातावरण की जांच करनी चाहिए।

## प्रश्नोत्तरी

1. Asterisk 22 में, कौन सा चैनल ड्राइवर SIP समर्थन प्रदान करता है, और पुराने `chan_sip` का क्या हुआ?
   - A. `chan_sip` अभी भी डिफ़ॉल्ट है; `chan_pjsip` वैकल्पिक है।
   - B. `chan_pjsip` डिफ़ॉल्ट SIP चैनल है; `chan_sip` को Asterisk 21 में हटा दिया गया था और अब मौजूद नहीं है।
   - C. दोनों डिफ़ॉल्ट रूप से निर्मित होते हैं और आप रनटाइम पर उनके बीच चयन करते हैं।
   - D. SIP समर्थन को पूरी तरह से IAX2 के पक्ष में हटा दिया गया था।
2. Asterisk के लिए टेलीफोनी इंटरफेस कार्ड में आमतौर पर डिजिटल सिग्नल प्रोसेसर (DSPs) इन-बिल्ट होते हैं और इसलिए उन्हें PC से बहुत अधिक CPU की आवश्यकता नहीं होती है।
   - A. सही
   - B. गलत
3. यदि आप एकदम सही वॉयस क्वालिटी चाहते हैं, तो आपको एंड-टू-एंड क्वालिटी ऑफ सर्विस (QoS) लागू करने की आवश्यकता है।
   - A. सही
   - B. गलत
4. आपको हमेशा नवीनतम Asterisk संस्करण चुनना चाहिए, क्योंकि यह सबसे स्थिर है।
   - A. सही
   - B. गलत
5. Asterisk 22 के लिए बिल्ड डिपेंडेंसी इंस्टॉल करने का अनुशंसित तरीका क्या है?
6. यदि आपके पास TDM इंटरफेस कार्ड नहीं है, तो भी आपके पास सिंक्रोनाइज़ेशन के लिए एक आंतरिक टाइमिंग स्रोत होगा, जो Linux पर `res_timing_timerfd` मॉड्यूल द्वारा प्रदान किया जाता है। इस टाइमिंग का उपयोग ________ और ________ जैसे एप्लिकेशन द्वारा किया जाता है।
7. Asterisk इंस्टॉल करते समय GNOME या KDE जैसे डेस्कटॉप वातावरण को छोड़ना बेहतर है, क्योंकि ग्राफिकल इंटरफेस CPU चक्रों का उपभोग करते हैं।
   - A. सही
   - B. गलत
8. Asterisk कॉन्फ़िगरेशन फ़ाइलें ________ निर्देशिका में स्थित होती हैं।
9. Asterisk सैंपल कॉन्फ़िगरेशन फ़ाइलें इंस्टॉल करने के लिए, कमांड टाइप करें: ________
10. Asterisk को नॉन-रूट उपयोगकर्ता के रूप में चलाना क्यों महत्वपूर्ण है?

**उत्तर:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — एक्सट्रैक्ट किए गए Asterisk सोर्स ट्री से `./contrib/scripts/install_prereq install` चलाएँ · 6 — ConfBridge और Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — सुरक्षा (यदि Asterisk से समझौता किया जाता है तो नुकसान को सीमित करता है)
