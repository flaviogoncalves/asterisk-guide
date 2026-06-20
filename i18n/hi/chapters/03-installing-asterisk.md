# Installing Asterisk 22

पहले अध्याय में, हमने टेलीफ़ोनी वातावरण में Asterisk की उपयोगिता के बारे में थोड़ा जाना। इस अध्याय में, हम Asterisk को डाउनलोड और इंस्टॉल करने की प्रक्रिया को कवर करेंगे। शुरू करने से पहले, इसे कंपाइल और इंस्टॉल करना सीखना आवश्यक है। कंपाइल प्रक्रिया पारंपरिक Microsoft™ Windows™ उपयोगकर्ताओं के लिए अजीब लग सकती है, लेकिन यह Linux™ वातावरण में काफी सामान्य है। Asterisk को कंपाइल करते समय आप अपने हार्डवेयर के लिए अनुकूलित कोड प्राप्त कर सकते हैं, यही हम यहाँ करेंगे। Asterisk कई ऑपरेटिंग सिस्टम पर चलता है, लेकिन हम चीज़ों को आसान रखने के लिए केवल एक का उपयोग करेंगे: Linux। हम **Ubuntu 24.04 LTS** का उपयोग करते हैं क्योंकि इसकी डिपेंडेंसियों को इंस्टॉल करना आसान है और यह एक स्थिर, अच्छी तरह समर्थित सर्वर वितरण है जिसका फ़ुटप्रिंट कम है। यदि आप कोई अन्य वितरण पसंद करते हैं, तो पैकेज नामों को उसी अनुसार समायोजित करें।

यह संस्करण **Asterisk 22 LTS** (रिलीज़ 2024-10-16; पूर्ण समर्थन 2028-10-16 तक, सुरक्षा सुधार 2029-10-16 तक) को लक्षित करता है। Asterisk 22 वर्तमान लोंग‑टर्म सपोर्ट रिलीज़ है। ध्यान दें कि Digium का अधिग्रहण **Sangoma** ने 2018 में किया था, और अब Asterisk को Sangoma द्वारा प्रायोजित किया जाता है — इस अध्याय में "Digium" के सभी उल्लेख ऐतिहासिक हार्डवेयर के लिए पुरानी ब्रांड को दर्शाते हैं।

## उद्देश्य

By the end of this chapter you should be able to:

- Asterisk के लिए हार्डवेयर आवश्यकताओं का निर्धारण करें;
- आवश्यक निर्भरताओं के साथ Linux स्थापित करें;
- HTTPS के माध्यम से एक स्थिर संस्करण डाउनलोड करें;
- Asterisk को संकलित करें; और
- बूट समय पर Asterisk को शुरू करने का तरीका सीखें।

## न्यूनतम हार्डवेयर आवश्यक

Asterisk को चलाने के लिए बहुत अधिक हार्डवेयर की आवश्यकता नहीं होती, लेकिन आपके आवश्यकताओं के लिए सबसे अच्छा हार्डवेयर चुनने के लिए कुछ सुझाव हैं। हार्डवेयर चुनते समय आपको निम्नलिखित मुख्य कारकों पर विचार करना चाहिए:

- पंजीकृत उपयोगकर्ताओं की कुल संख्या। निर्धारित करें कि आपको प्रति सेकंड कितनी रजिस्ट्रेशन का समर्थन करना है
- एक साथ चलने वाली कॉलों की कुल संख्या। निर्धारित करें कि आपको Asterisk सर्वर पर नेटवर्क एडेप्टर और ब्रिज में कितनी नेटवर्क बातचीत को प्रोसेस करना है
- आपको किन codecs का समर्थन करना है। उच्च जटिलता वाले codecs को आपके सर्वर में बहुत अधिक CPU/FPU शक्ति की आवश्यकता होगी; उदाहरण के लिए, iLBC को उसके निर्माता (Global IP Sound) ने लगभग 30 ms फ्रेम के लिए प्रति चैनल 18 MIPS (और 20 ms फ्रेम के लिए लगभग 15 MIPS) TI C54x DSP पर मापा था
- इको कैंसलेशन। इको कैंसलेशन बहुत अधिक CPU/FPU ले सकता है, कुछ मामलों में आपको टेलीफ़ोनी इंटरफ़ेस कार्ड में DSPs का उपयोग करके हार्डवेयर इको कैंसलेशन चुनना चाहिए
- उपलब्धता। उपलब्धता बढ़ाने के लिए RAID1 या 5 का उपयोग करें। याद रखें, Asterisk 24x7 एप्लिकेशन है।

एक Asterisk सर्वर के लिए मुख्य घटक नेटवर्क एडाप्टर है। एक अच्छा सर्वर नेटवर्क एडाप्टर अनुशंसित है। जब आपको g.729 और iLBC जैसे उच्च जटिलता वाले कोडेक्स और इको कैंसलेशन को सपोर्ट करना हो तो CPU महत्वपूर्ण है। आप इसे समर्पित DSPs को ऑफलोड करने का चयन कर सकते हैं: Sangoma (पूर्व में Digium) एक DSP कार्ड प्रदान करता है जिसका नाम TC400B है और जो 120 G.729 समकालिक कॉल्स को सपोर्ट करने में सक्षम है।

सर्वोत्तम अभ्यास यह है कि ज्ञात निर्माता से नया, सर्वर‑क्लास कंप्यूटर चुना जाए। यह जानने के लिए कि कोई विशिष्ट मशीन कितनी समकालिक कॉल या कितने पंजीकृत उपयोगकर्ताओं को समर्थन दे सकती है, आपको इस हार्डवेयर का परीक्षण एक तनाव‑परीक्षण उपकरण जैसे SIPP (http://sipp.sourceforge.net) से करना चाहिए। कुछ हार्डवेयर निर्माताओं जैसे Xorcom (http://www.xorcom.com) अपने परिणाम वेबसाइट पर प्रकाशित करते हैं।

ध्यान दें: कुछ Asterisk एप्लिकेशन, जैसे ConfBridge और music on hold, को एक आंतरिक टाइमिंग स्रोत की आवश्यकता होती है। आधुनिक Linux पर यह बिल्ट‑इन `res_timing_timerfd` मॉड्यूल द्वारा स्वतः प्रदान किया जाता है — कोई टेलीफ़ोनी हार्डवेयर आवश्यक नहीं है। (पुराना `dahdi_dummy` सॉफ़्टवेयर टाइमर अब मौजूद नहीं है; इसकी कार्यक्षमता मुख्य `dahdi` कर्नेल मॉड्यूल में DAHDI Linux 2.3.0 में सम्मिलित कर दी गई है।) आप सक्रिय टाइमर की पुष्टि CLI कमांड `timing test` से कर सकते हैं।

### हार्डवेयर कॉन्फ़िगरेशन

The Asterisk hardware does not need to be sophisticated. You don't need an expensive video card or numerous peripherals. Some tips about hardware configuration:

- अनावश्यक इंटरप्ट्स की खपत से बचने के लिए अप्रयुक्त USB, सीरियल और पैरेलल पोर्ट को निष्क्रिय करें।  
- एक मजबूत नेटवर्क इंटरफ़ेस कार्ड आवश्यक है।  
- टेलीफ़ोनी इंटरफ़ेस कार्ड का उपयोग करते समय विशेष ध्यान दें। कुछ कार्ड 3.3 वोल्ट PCI बस का उपयोग करते हैं, और उनके लिए मदरबोर्ड ढूँढ़ना आसान नहीं होता। आजकल, PCI एक्सप्रेस अधिक आसानी से उपलब्ध है।  
- हार्ड डिस्क पर विशेष ध्यान दें, PBX 24x7 मोड में काम करता है जबकि डेस्कटॉप 8x5 में। डेस्कटॉप हार्डवेयर को PBX के लिए उपयोग न करें, आमतौर पर हार्ड डिस्क पहले साल में ही फेल हो जाती है। मेरी सिफ़ारिश है कि आप सर्वर मशीन या 24x7 एप्लिकेशन चलाने के लिए डिज़ाइन किया गया एप्लायंस उपयोग करें।

### IRQ साझा करना (केवल लेगेसी PCI कार्ड)

यह चिंता **केवल** तब लागू होती है जब आप भौतिक PCI/PCI-Express टेलीफ़ोनी कार्ड (DAHDI हार्डवेयर) स्थापित करते हैं। ऐसे कार्ड बड़ी संख्या में इंटररप्ट उत्पन्न करते हैं, और पुराने सिंगल‑CPU सिस्टम पर, किसी अन्य डिवाइस के साथ IRQ लाइन साझा करने से ड्राइवर स्टार्व हो सकता है और आवाज़ की गुणवत्ता घट सकती है। यदि आप टेलीफ़ोनी कार्ड का उपयोग करते हैं, तो मशीन को केवल Asterisk के लिए समर्पित करें, BIOS में किसी भी अनउपयोगी ऑन‑बोर्ड डिवाइस को निष्क्रिय करें, और `cat /proc/interrupts` के साथ असाइन किए गए इंटररप्ट की जाँच करें। आधुनिक मल्टी‑कोर सर्वर जो MSI/MSI‑X इंटररप्ट का उपयोग करते हैं, व्यावहारिक रूप से IRQ शेयरिंग को एक समस्या नहीं बनाते, और शुद्ध‑VoIP डिप्लॉयमेंट (कोई कार्ड नहीं) को इसके बारे में बिल्कुल भी चिंता करने की आवश्यकता नहीं है।

## Choosing a Linux distribution

Asterisk प्रारम्भ में Linux पर चलाने के लिए विकसित किया गया था। हालांकि, यह BSD Unix या macOS पर भी चल सकता है। यदि आप Asterisk में नए हैं, तो पहले Linux का उपयोग करने की कोशिश करें क्योंकि यह बहुत आसान है। Asterisk आधिकारिक रूप से RHEL परिवार (CentOS/RHEL/Fedora), Ubuntu, और Debian को लक्षित करता है। आज के व्यावहारिक विकल्प हैं **Debian 12**, **Ubuntu 22.04 LTS / 24.04 LTS**, और **Rocky Linux 9 / AlmaLinux 9** — CentOS Linux अब समाप्त हो चुका है, इसलिए RHEL‑परिवार सिस्टम पर Rocky या AlmaLinux को प्राथमिकता दें। इस पुस्तक के लिए मैं Ubuntu 24.04 LTS का उपयोग करूँगा। आधिकारिक रिलीज़ डायरेक्टरी से नवीनतम 24.04 पॉइंट‑रिलीज़ सर्वर इमेज डाउनलोड करें (सटीक फ़ाइलनाम में वर्तमान पॉइंट रिलीज़ शामिल है, उदाहरण के लिए `ubuntu-24.04.4-live-server-amd64.iso`):

```
https://releases.ubuntu.com/24.04/
```

### Preparing Linux for Asterisk

Asterisk को संकलित करने से पहले आपको बिल्ड पैकेजों के साथ एक कार्यशील Linux सिस्टम चाहिए। **Ubuntu 24.04 LTS Server** को एक वर्चुअल मशीन या समर्पित बॉक्स पर स्थापित करें (64‑bit इमेज का उपयोग करें; इस पुस्तक में सभी चीज़ें 64‑bit हैं, हालांकि Asterisk स्वयं अभी भी 32‑bit x86 को समर्थन देता है)। हमने इस प्रशिक्षण के लिए VirtualBox का उपयोग किया; आप इमेज <https://releases.ubuntu.com/24.04> से डाउनलोड कर सकते हैं। Linux को स्वयं स्थापित करना इस पुस्तक के दायरे से बाहर है — बुनियादी Linux ज्ञान एक पूर्वापेक्षा है। Linux स्थापित होने के बाद, आप Asterisk बिल्ड निर्भरताएँ जोड़ेंगे (नीचे *Installing dependencies* देखें) और फिर Asterisk को संकलित करेंगे।

## Asterisk के लिए Linux स्थापित करना

Linux को सामान्य रूप से स्थापित करें, बिना ग्राफिकल डेस्कटॉप के। स्थापना के दौरान, एक मेल ट्रांसफर एजेंट भी सक्षम करें (हम **exim4** का उपयोग करते हैं) — Asterisk को बाद में इस पुस्तक में voicemail-to-email सूचनाएँ भेजने के लिए इसकी आवश्यकता होगी। **सावधान:** ऑपरेटिंग सिस्टम स्थापित करने से लक्ष्य डिस्क मिट जाता है। यदि आप भौतिक हार्डवेयर पर स्थापित कर रहे हैं, तो पहले अपना डेटा बैकअप लें; वर्चुअल मशीन में स्थापित करने से आपका होस्ट अप्रभावित रहता है। Ubuntu Server ISO (या VM के वर्चुअल ऑप्टिकल ड्राइव) से इंस्टॉलर बूट करें और प्रॉम्प्ट्स का उत्तर दें — अधिकांश सरल हैं।

## Installing dependencies

Asterisk और DAHDI को स्थापित करने के लिए आपको कई सॉफ़्टवेयर निर्भरताएँ स्थापित करनी होंगी। Asterisk 22 में इसे करने का अनुशंसित तरीका स्रोत ट्री के साथ आने वाले स्क्रिप्ट का उपयोग करना है, जो प्रत्येक समर्थित वितरण के लिए सही पैकेज नामों को जानता है। Asterisk स्रोत को डाउनलोड और एक्सट्रैक्ट करने के बाद (नीचे “Compiling Asterisk” देखें), चलाएँ:

```
cd /usr/src/asterisk-22.x.y
./contrib/scripts/install_prereq install
```

1. रूट के रूप में लॉगिन करें (या `sudo` का उपयोग करें)।
2. यदि आप Debian/Ubuntu सिस्टम पर निर्भरताएँ मैन्युअल रूप से स्थापित करना पसंद करते हैं, तो समकक्ष पैकेज सूची इस प्रकार है:

```
apt-get install build-essential git wget openssl libssl-dev libxml2-dev \
  libsqlite3-dev uuid-dev libjansson-dev libedit-dev libncurses-dev \
  libcurl4-openssl-dev pkg-config autoconf-archive
```

ध्यान दें कि Asterisk स्रोत अब Git पर होस्ट किया गया है, इसलिए `subversion` अब आवश्यक नहीं है, और आधुनिक Debian/Ubuntu `libncurses-dev` प्रदान करते हैं न कि संस्करणित `libncurses5-dev`। हाथ से रखी गई सूची के बजाय `./contrib/scripts/install_prereq install` को प्राथमिकता दें, क्योंकि स्क्रिप्ट हमेशा आपके वितरण के लिए सही पैकेज नामों को ट्रैक करती है।

### DAHDI

DAHDI (Digium/Sangoma Asterisk Hardware Device Interface) एनालॉग और डिजिटल कार्डों के लिए ड्राइवरों की आर्किटेक्चर है। Asterisk स्थापित करने से पहले यदि आप एनालॉग या डिजिटल इंटरफ़ेस का उपयोग करने की योजना बना रहे हैं तो DAHDI को स्थापित करना महत्वपूर्ण है। DAHDI अभी भी एनालॉग/डिजिटल टेलीफ़ोनी कार्डों के लिए मौजूद है लेकिन यह धीरे‑धीरे निचे हो रहा है — अधिकांश आधुनिक डिप्लॉयमेंट्स शुद्ध VoIP हैं और इस भाग को पूरी तरह छोड़ सकते हैं। केवल तभी DAHDI स्थापित करें जब आपके पास भौतिक टेलीफ़ोनी इंटरफ़ेस हार्डवेयर हो। स्रोत फ़ाइलें प्राप्त करने के लिए उपयोग करें:

```
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
```

फ़ाइलों को अनज़िप करने के लिए उपयोग करें:

```
tar -xzvf dahdi-linux-complete-current.tar.gz
```

### Compiling DAHDI drivers

आपको DAHDI मॉड्यूल्स को संकलित करना होगा। कमांड `./configure` और `make menuselect` कई साल पहले पेश किए गए थे। बाद वाला आपको यह चुनने की अनुमति देता है कि कौन‑से यूटिलिटीज़ और मॉड्यूल्स बनाना हैं। निम्नलिखित कमांड्स यह करेंगे:

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

`make install-config` DAHDI को कॉन्फ़िगर किया गया है। यदि आपके पास कोई DAHDI हार्डवेयर है तो अब अनुशंसा की जाती है कि आप `/etc/dahdi/modules` को संपादित करके केवल स्थापित DAHDI हार्डवेयर के लिए समर्थन लोड करें। डिफ़ॉल्ट रूप से सभी DAHDI हार्डवेयर का समर्थन DAHDI शुरू होने पर लोड हो जाता है। मेरा मानना है कि आपके सिस्टम पर मौजूद DAHDI हार्डवेयर है: `usb:004/002 xpp_usb- e4e4:1150 Astribank-multi no-firmware` यह स्क्रीन (ऊपर) आपको फ़ाइल `/etc/dahdi/modules` को बदलने के लिए कहती है ताकि केवल आपके विशिष्ट कॉन्फ़िगरेशन के लिए आवश्यक ड्राइवर लोड हों और पता लगाए गए हार्डवेयर को दिखाया जा सके। फ़ाइल `/etc/dahdi/modules` को संपादित करें और केवल आवश्यक हार्डवेयर लोड करें। मेरे मामले में, मैं एक टेस्ट मशीन पर Xorcom Astribank 6FXS और 2FXO के साथ काम कर रहा था। फ़ाइल नीचे दिखायी गई है।

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

अपने कंप्यूटर को पुनः आरंभ करें और ड्राइवरों के सही लोड होने की पुष्टि करें।

## कौन सा संस्करण चुनें

सामान्य नियम के तौर पर, आपको आवश्यक सुविधाओं वाले संस्करण का उपयोग करना चाहिए। Asterisk एक रिलीज़ मॉडल का पालन करता है जिसमें LTS (लॉन्ग-टर्म सपोर्ट) और मानक रिलीज़ बारी-बारी से आती हैं। इस संस्करण के समय, **Asterisk 22 वर्तमान LTS रिलीज़** है (अक्टूबर 2024 में जारी; नवीनतम पॉइंट रिलीज़ 22.10.0 है), जो इसे अभी चुनने के लिए सबसे अच्छा बनाता है। Asterisk 20 पिछला LTS है, और संस्करण 16 (पहले संस्करण में उपयोग किया गया) अब समाप्त हो चुका है। उत्पादन प्रणालियों के लिए हमेशा एक LTS रिलीज़ चुनें।

## Compiling Asterisk

यदि आपने पहले सॉफ़्टवेयर को संकलित किया है, तो Asterisk को संकलित करना आसान कार्य होगा। Asterisk को संकलित और स्थापित करने के लिए निम्नलिखित कमांड चलाएँ। याद रखें, आप make menuselect का उपयोग करके कौन‑से एप्लिकेशन और मॉड्यूल बनाना है चुन सकते हैं।  

Step 1: Download the source code

```
cd /usr/src
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-22-current.tar.gz
tar -xzvf asterisk-22-current.tar.gz
```

Step 2: Install the build prerequisites (see "Installing dependencies" above)

```
cd asterisk-22.x.y (adapt to the version downloaded)
./contrib/scripts/install_prereq install
```

Step 3: Configure the build

```
./configure
```

Step 4: Select the modules to build

```
make menuselect
```

make menuselect का उपयोग करके केवल आवश्यक मॉड्यूल स्थापित करें। Asterisk 22 में SIP चैनल **chan_pjsip** है (डिफ़ॉल्ट रूप से निर्मित); पुराना **chan_sip** Asterisk 21 में हटा दिया गया था और अब मौजूद नहीं है। Opus *pass-through* बॉक्स से बाहर काम करता है (इन‑ट्री `res_format_attr_opus` मॉड्यूल SDP वार्ता को संभालता है), लेकिन **codec_opus** ट्रांसकोडिंग मॉड्यूल अभी भी Sangoma/Digium से प्राप्त एक बाहरी, बंद‑स्रोत बाइनरी है — menuselect में इसे चुनने से यह Digium के सर्वरों से डाउनलोड हो जाता है। बाइनरी निःशुल्क है। विवरण के लिए नीचे "Selecting modules with menuselect" देखें।

Step 5: Build and install Asterisk, then create the default config and sample files

```
make
make install
make samples
make config
ldconfig
```

`make install` बाइनरी और मॉड्यूल स्थापित करता है, `make samples` नमूना कॉन्फ़िगरेशन फ़ाइलें `/etc/asterisk` में लिखता है, `make config` आपके पहचाने गए वितरण के लिए SysV init स्टार्टअप स्क्रिप्ट स्थापित करता है (उदाहरण के लिए Debian/Ubuntu पर `/etc/init.d/asterisk`), और `ldconfig` साझा‑लाइब्रेरी कैश को रीफ़्रेश करता है। एक systemd यूनिट भी स्रोत वृक्ष में `contrib/systemd/asterisk.service` पर उपलब्ध है, लेकिन `make config` इसे स्वचालित रूप से स्थापित नहीं करता — यदि आप Asterisk को systemd के तहत चलाना चाहते हैं तो स्वयं इसे उचित स्थान पर कॉपी करें (नीचे देखें)।

### Selecting modules with menuselect

`make menuselect` एक टेक्स्ट‑आधारित मेनू खोलता है जहाँ आप ठीक‑ठीक चुनते हैं कि कौन‑से एप्लिकेशन, कोडेक, चैनल और संसाधन बनाना हैं। Asterisk 22 के लिए कुछ विशेष नोट्स:

- **chan_pjsip** (*Channel Drivers* के तहत) आधुनिक SIP चैनल है और डिफ़ॉल्ट रूप से सक्षम है; यह Asterisk 22 में एकमात्र SIP चैनल है।
- **codec_opus** (*Codec Translators* के तहत) एक **external** मॉड्यूल है (इसका menuselect एंट्री पढ़ता है "Download the Opus codec from Digium"); इसे सक्षम करने से `make` Sangoma/Digium से निःशुल्क, बंद‑स्रोत बाइनरी प्राप्त करता है। Opus pass-through को स्वयं कोई अतिरिक्त मॉड्यूल नहीं चाहिए। Sangoma का **codec_g729** मॉड्यूल भी उपलब्ध है — बाइनरी निःशुल्क डाउनलोड किया जा सकता है, लेकिन वैध G.729 ट्रांसकोडिंग के लिए प्रति‑चैनल लाइसेंस खरीदना आवश्यक है।
- *Core Sound Packages*, *Music On Hold File Packages*, और *Extras Sound Packages* मेनू में आप जिन ध्वनि स्वरूपों और भाषाओं को चाहते हैं, उन्हें चुनें; आप जो भी यहाँ चेक करेंगे, वह `make install` के दौरान स्वचालित रूप से डाउनलोड और स्थापित हो जाएगा।

अपनी चयन करने के बाद, **Save & Exit** चुनें और `make` के साथ आगे बढ़ें।

## Starting and stopping Asterisk

With this minimal configuration, it’s possible to start Asterisk successfully. For learning and debugging, you can start Asterisk in the foreground attached to the console:

```
/usr/sbin/asterisk -vvvgc
```

Use the CLI command `core stop now` to shut down Asterisk:

```
*CLI> core stop now
```

### Starting Asterisk with systemd

On modern Linux distributions (Debian 12, Ubuntu 22.04/24.04, Rocky/AlmaLinux 9), the system service manager is **systemd**. Asterisk ships a systemd unit at `contrib/systemd/asterisk.service` in the source tree; copy it to `/etc/systemd/system/asterisk.service` and run `systemctl daemon-reload`. Once installed, the recommended way to run Asterisk in production is through `systemctl`:

```
systemctl start asterisk      # start the service
systemctl stop asterisk       # stop the service
systemctl restart asterisk    # restart the service
systemctl status asterisk     # show current status
systemctl enable asterisk     # start automatically at boot
```

Once Asterisk is running as a service, attach to its CLI with `asterisk -r` (connect) or `asterisk -rvvv` (connect with verbose output).

On older systems Asterisk was started via the legacy SysV init script (`/etc/init.d/asterisk`) and the **safe_asterisk** wrapper, which restarted Asterisk automatically if it crashed. With systemd, automatic restart is handled by the unit file's `Restart=` directive, so `safe_asterisk` is generally no longer needed. The legacy init/`safe_asterisk` approach still works but is deprecated on systemd-based distributions.

### Asterisk runtime options

The Asterisk starting process is very simple. If Asterisk is run without any parameters, it is launched as a daemon.

```
/sbin/asterisk
```

You can access the Asterisk console by executing the following command. Please note that more than one console process can be run at the same time.

```
/sbin/asterisk -r
```

### Available runtime options for Asterisk

You can show the available runtime options using `asterisk -h`

```text
sipast:/usr/src/asterisk-22.x.y# asterisk -h
Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation and others.
Usage: asterisk [OPTIONS]
Valid Options:
   -V              Display version number and exit
   -C <configfile> Use an alternate configuration file
   -G <group>      Run as a group other than the caller
   -U <user>       Run as a user other than the caller
   -c              Provide console CLI
   -d              Increase debugging (multiple d's = more debugging)
   -f              Do not fork
   -F              Always fork
   -g              Dump core in case of a crash
   -h              This help screen
   -i              Initialize crypto keys at startup
   -L <load>       Limit the maximum load average before rejecting new calls
   -M <value>      Limit the maximum number of calls to the specified value
   -m              Mute debugging and console output on the console
   -n              Disable console colorization. Can be used only at startup.
   -p              Run as pseudo-realtime thread
   -q              Quiet mode (suppress output)
   -r              Connect to Asterisk on this machine
   -R              Same as -r, except attempt to reconnect if disconnected
   -s <socket>     Connect to Asterisk via socket <socket> (only valid with -r)
   -t              Record soundfiles in /var/tmp and move them where they
                   belong after they are done
   -T              Display the time in [Mmm dd hh:mm:ss] format for each line
                   of output to the CLI. Cannot be used with remote console mode.
   -v              Increase verbosity (multiple v's = more verbose)
   -x <cmd>        Execute command <cmd> (implies -r)
   -X              Enable use of #exec in asterisk.conf
   -W              Adjust terminal colors to compensate for a light background
```

## इंस्टॉलेशन डायरेक्टरी

Asterisk कई डायरेक्टरीज़ में स्थापित होता है, जिन्हें asterisk.conf फ़ाइल में संशोधित किया जा सकता है। प्रशिक्षण उद्देश्यों के लिए मैं verbose को 3 से 15 कर दूँगा, उत्पादन में इसे 3 पर रखें। विकल्प `maxcalls` और `maxload` आपके सिस्टम को ओवरलोडिंग से बचाने के अच्छे विकल्प हैं।

### asterisk.conf (अंश)

`[directories]` सेक्शन यह निर्धारित करता है कि Asterisk अपनी कॉन्फ़िगरेशन, मॉड्यूल, डेटा, स्पूल, और लॉग्स कहाँ रखता है:

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
```

`[options]` सेक्शन रनटाइम ट्यूनिंग रखता है। नीचे दिखाए गए सबसे उपयोगी विकल्प हैं (सक्षम करने के लिए अनकमेंट करें); फ़ाइल में कई और विकल्प होते हैं, प्रत्येक एक इनलाइन टिप्पणी द्वारा दस्तावेज़ित है:

```
[options]
;verbose = 3      ; Console verbosity (raise to 15 for training, keep 3 in production)
;debug = 3        ; Debug level
;maxcalls = 10    ; Maximum number of simultaneous calls allowed
;maxload = 0.9    ; Stop accepting new calls when load average exceeds this
;maxfiles = 1000  ; Maximum number of open files
;runuser = asterisk   ; The user to run as
;rungroup = asterisk  ; The group to run as
```

## Log files and log rotation

Asterisk PBX अपने संदेशों को `/var/log/asterisk` में लॉग करता है। लॉगिंग को `logger.conf` द्वारा नियंत्रित किया जाता है। मुख्य भाग `[logfiles]` सेक्शन है, जहाँ प्रत्येक पंक्ति एक लॉग चैनल और वह संदेश स्तर निर्धारित करती है जिसे वह कैप्चर करता है (excerpt):

```ini
; logger.conf (excerpt)
[general]
;dateformat = %F %T.%3q          ; ISO 8601 timestamps, with milliseconds

[logfiles]
; <logger_name> => [formatter]<levels>
console  => notice,warning,error
messages => notice,warning,error
full     => notice,warning,error,verbose,dtmf,fax
security => security              ; PJSIP/auth security events (used by Fail2Ban)
```

संपादन के बाद, परिवर्तन को `logger reload` के साथ लागू करें और चैनलों की पुष्टि `logger show channels` से करें:

```text
*CLI> logger show channels
Channel                       Type   Formatter  Status   Configuration
/var/log/asterisk/security    File   default    Enabled  - SECURITY
/var/log/asterisk/full        File   default    Enabled  - NOTICE WARNING ERROR VERBOSE DTMF FAX
/var/log/asterisk/messages    File   default    Enabled  - NOTICE WARNING ERROR
```

लॉग फ़ाइलें जल्दी बढ़ सकती हैं, इसलिए उन्हें सिस्टम `logrotate` डेमॉन के साथ घुमाएँ — `/etc/logrotate.d/` के तहत एक फ़ाइल जोड़ें:

```text
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

logrotate के बारे में अधिक जानकारी निम्नलिखित का उपयोग करके प्राप्त की जा सकती है:

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

## Asterisk installation notes

This section will provide some advice about issues to address before installing Asterisk.

### Production Systems

If Asterisk is installed in a production environment, you should pay attention to the system design. A server has to be optimized in such a way that telephony systems have priority over other system processes. Asterisk should not run together with processor-intensive software such as X-Windows. If you need to run CPU-intensive processes (e.g., a huge database), use a separate server. Generally speaking, Asterisk is susceptible to hardware performance variations. Thus, try using Asterisk in a hardware environment that does not require more than 40% of CPU utilization.

### Network Tips

If you plan to use IP phones, it is important that you pay attention to your network. Voice protocols are very good and resistant to latency and even jitters; however, if you use a poorly configured local area network, voice quality will suffer. It is only possible to guarantee good voice quality using quality of service (QoS) in switches and routers. Voice in a local area network tends to be good, but even in a LAN environment, if you have 10 Mbps hubs with too many collisions, you will end up having a distorted or crappy voice. Follow these recommendations to ensure the best possible voice quality:

- Use end-to-end QoS if possible or economically feasible. With end-to-end QoS, the voice quality is perfect. No excuses!
- Avoid using 10/100 Mbps hubs for voice in a production environment. Collisions can impose jitters on the network. Full duplex 10/100 Mbps are preferred because no collisions occur.
- Use VLANs to separate unnecessary broadcasts of the voice network. You don’t want a virus destroying your voice network with ARP broadcasts.
- Educate users about expectations in a voice network. Without QoS, don’t state that the voice will be perfect as in most cases it won’t be. A quality of voice similar to a mobile phone will most often be achieved. Use quality phones as problems with firmware and hardware design are common.

## सारांश

इस अध्याय में, आपने न्यूनतम हार्डवेयर आवश्यकताओं के साथ-साथ Asterisk को डाउनलोड, इंस्टॉल और कंपाइल करने के बारे में सीखा है। सुरक्षा कारणों से Asterisk को एक नॉन-रूट उपयोगकर्ता के साथ चलाया जाना चाहिए। उत्पादन वातावरण शुरू करने से पहले आपको अपने नेटवर्क पर्यावरण की जाँच करनी चाहिए।

## Quiz

1. In Asterisk 22, which channel driver provides SIP support, and what happened to the older `chan_sip`?
   - A. `chan_sip` is still the default; `chan_pjsip` is optional.
   - B. `chan_pjsip` is the default SIP channel; `chan_sip` was removed in Asterisk 21 and no longer exists.
   - C. Both are built by default and you choose between them at runtime.
   - D. SIP support was removed entirely in favor of IAX2.
2. Telephony interface cards for Asterisk usually have Digital Signal Processors (DSPs) built in and so do not need much CPU from the PC.
   - A. True
   - B. False
3. If you want perfect voice quality, you need to implement end-to-end quality of service (QoS).
   - A. True
   - B. False
4. You should always choose the latest Asterisk version, as it is the most stable.
   - A. True
   - B. False
5. What is the recommended way to install the build dependencies for Asterisk 22?
6. If you don't have a TDM interface card you will still have an internal timing source for synchronization, provided by the `res_timing_timerfd` module on Linux. This timing is used by applications such as ________ and ________.
7. When installing Asterisk it is better to leave desktop environments such as GNOME or KDE out, because graphical interfaces consume CPU cycles.
   - A. True
   - B. False
8. Asterisk configuration files are located in the ________ directory.
9. To install the Asterisk sample configuration files, type the command: ________
10. Why is it important to run Asterisk as a non-root user?

**Answers:** 1 — B · 2 — B · 3 — A · 4 — B · 5 — Run `./contrib/scripts/install_prereq install` from the extracted Asterisk source tree · 6 — ConfBridge and Music on Hold · 7 — A · 8 — `/etc/asterisk` · 9 — `make samples` · 10 — Security (limits the damage if Asterisk is compromised)
