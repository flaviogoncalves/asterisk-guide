# डायल प्लान उन्नत सुविधाएँ

Chapter 3 ने डायल प्लान की बुनियादों पर चर्चा की थी। शैक्षिक कारणों से, हमने सभी सुविधाओं को नहीं बताया, बल्कि केवल सबसे महत्वपूर्ण कुछ को ही समझाया। यह अध्याय डायल प्लान में और गहराई से जाएगा, उन्नत तकनीकों, नए अनुप्रयोगों और अवधारणाओं का वर्णन करेगा।

## Objectives

इस अध्याय के अंत तक, आप सक्षम होंगे:

- अपने एक्सटेंशन एंट्रीज़ को सरल बनाना
- डायल प्लान सुरक्षा और फ़िल्टरिंग एक्सटेंशन को संबोधित करना
- एक IVR मेनू का उपयोग करके कॉल प्राप्त करना
- अनावश्यक री‑राइट्स से बचने के लिए सबरूटीन का उपयोग करना
- “Include” का उपयोग करके कुछ डायल प्लान सुरक्षा लागू करना
- AsteriskDB का उपयोग करके फ़ॉलो‑मी लागू करना
- अपने PBX में आफ्टर‑ऑवर्स व्यवहार लागू करना
- स्विच कमांड का उपयोग करके किसी अन्य PBX पर ट्रांसफ़र करना
- प्राइवेसी मैनेजर लागू करना
- वॉइसमेल लागू करना
- एक कॉर्पोरेट डायरेक्टरी लागू करना

## अपने डायल प्लान को सरल बनाना

आप “same” कीवर्ड का उपयोग करके एक एक्सटेंशन को परिभाषित करके अपने डायल प्लान को सरल बना सकते हैं। इससे डायल प्लान में टाइपो की संख्या कम होनी चाहिए। नीचे उदाहरण देखें:

```
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

## Dial Plan Security

Asterisk डायल प्लान में एक त्रुटि पाई गई थी जो उपयोगकर्ता को आपके डायल प्लान में एक नया चैनल और डायल नंबर इंजेक्ट करने की अनुमति देती है। मान लीजिए आपके सर्वर `exten=>_X.,1,Dial(PJSIP/${EXTEN})` में निम्न पंक्ति है और कोई दुर्भावनापूर्ण उपयोगकर्ता सॉफ्टफ़ोन में नंबर `3000&DAHDI/1/011551123456789` डायल करता है। SIP प्रोटोकॉल, डिफ़ॉल्ट रूप से, किसी भी अल्फ़ान्यूमेरिक कैरेक्टर को स्वीकार करता है, इसलिए डायल किया गया एक्सटेंशन वास्तव में दो कॉल्स को ट्रिगर करेगा: एक चैनल PJSIP/3000 के लिए और दूसरा चैनल DAHDI/011551123456789 के लिए, जो एक अंतरराष्ट्रीय नंबर है। इस प्रकार, एक्सटेंशन तक पहुँच वाले कोई भी उपयोगकर्ता वास्तव में दुनिया में कहीं भी कॉल कर सकता है। इस व्यवहार से बचने का सबसे आसान तरीका डायल एप्लिकेशन को कॉल करने से पहले नंबरों को फ़िल्टर करना है। फ़ंक्शन FILTER() इसके लिए बहुत उपयोगी है। उदाहरण:

```
exten=>_X.,1,DIAL(PJSIP/${FILTER(0-9,${EXTEN})})
```

एप्लिकेशन filter आपको डायल किए गए नंबर से सभी कैरेक्टर को फ़िल्टर करने की अनुमति देगा सिवाय 0 से 9 तक के नंबरों के। अधिक जानकारी के लिए Asterisk से उपलब्ध README-SERIOUSLY.bestpractices.txt फ़ाइल देखें।

## कॉल प्राप्त करना IVR मेनू का उपयोग करके.

पिछले भाग में, आपने सभी कॉल्स को DID या ऑपरेटर को फ़ॉरवर्ड करके प्राप्त किया था। अब आप एक IVR मेनू को लागू करना और एक ऑटो‑अटेंडेंट सेवा बनाना सीखेंगे। विशिष्टताओं में जाने से पहले, आइए कुछ नए एप्लिकेशन को देखें। हमने कमांड `core show application` का आउटपुट नीचे दिया है केवल पाठकों के लिए इसे आसान बनाने के उद्देश्य से। आप स्वयं इन विवरणों को `core show application <application_name>` का उपयोग करके प्राप्त कर सकते हैं।

### The Background() एप्लिकेशन

यह एप्लिकेशन कॉल करने वाले चैनल द्वारा डायल किए गए एक्सटेंशन की प्रतीक्षा करते हुए दी गई फ़ाइलों की सूची चलाएगा। इस एप्लिकेशन के फ़ाइलें चलाने के बाद अंकों की प्रतीक्षा जारी रखने के लिए **WaitExten** एप्लिकेशन का उपयोग किया जाना चाहिए। `langoverride` विकल्प स्पष्ट रूप से निर्दिष्ट करता है कि अनुरोधित साउंड फ़ाइलों के लिए कौन सी भाषा का उपयोग करने का प्रयास किया जाए। कोई भी **context** जो निर्दिष्ट किया गया है, वह डायल प्लान **context** होगा जिसका यह एप्लिकेशन डायल किए गए एक्सटेंशन पर निकलते समय उपयोग करता है। यदि अनुरोधित साउंड फ़ाइलों में से कोई मौजूद नहीं है, तो कॉल प्रोसेसिंग समाप्त कर दी जाएगी। **Options:**

- s - यदि चैनल 'up' स्थिति में नहीं है (अर्थात् अभी तक उत्तर नहीं दिया गया है) तो संदेश के प्लेबैक को छोड़ने का कारण बनता है। यदि यह होता है, तो एप्लिकेशन तुरंत लौट आएगा।
- n - फ़ाइलें चलाने से पहले चैनल का उत्तर न दें।
- m - केवल तभी ब्रेक करें जब दर्ज किया गया अंक गंतव्य कॉन्टेक्स्ट में एक-अंकीय एक्सटेंशन से मेल खाता हो।

### Record() एप्लिकेशन

यह एप्लिकेशन channel से दिए गए filename में रिकॉर्ड करता है। यदि फ़ाइल मौजूद है, तो इसे ओवरराइट कर दिया जाएगा।

![10-dialplan-advanced-features चित्र 1](../images/10-dialplan-advanced-features-img01.png)

- 'format' वह फ़ाइल प्रकार का फ़ॉर्मेट है जिसे रिकॉर्ड किया जाना है (wav, gsm, आदि)।
- 'silence' वह सेकंडों की संख्या है जो चुप्पी की अनुमति देती है इससे पहले कि वापस लौटे।
- 'maxduration' अधिकतम रिकॉर्डिंग अवधि सेकंडों में है; यदि यह अनुपस्थित है या शून्य है, तो कोई अधिकतम नहीं है।
- 'options' में निम्नलिखित में से कोई भी अक्षर हो सकता है:
    - `a` — मौजूदा रिकॉर्डिंग में जोड़ता है बजाय उसे बदलने के
    - `n` — उत्तर न दें, लेकिन यदि लाइन अभी तक उत्तर नहीं दी गई है तो फिर भी रिकॉर्ड करें
    - `q` — शांत (बीप टोन न बजाएँ)
    - `s` — यदि लाइन अभी तक उत्तर नहीं दी गई है तो रिकॉर्डिंग को छोड़ दें
    - `t` — डिफ़ॉल्ट `#` के बजाय वैकल्पिक `*` टर्मिनेटर कुंजी (DTMF) का उपयोग करें
    - `x` — सभी टर्मिनेटर कुंजियों (DTMF) को अनदेखा करें और हैंग‑अप तक रिकॉर्डिंग जारी रखें

यदि फ़ाइलनाम में %d शामिल है, तो इन अक्षरों को प्रत्येक बार फ़ाइल रिकॉर्ड होने पर एक संख्या से बदल दिया जाएगा जो एक से बढ़ती है। उपलब्ध फ़ॉर्मेट्स को देखने के लिए `core show file formats` का उपयोग करें। उपयोगकर्ता रिकॉर्डिंग को समाप्त करने और अगले प्रायोरिटी पर जाने के लिए # दबा सकता है। यदि उपयोगकर्ता रिकॉर्डिंग के दौरान कॉल समाप्त कर देता है, तो सभी डेटा खो जाएगा और एप्लिकेशन समाप्त हो जाएगा।

### Playback() एप्लिकेशन

यह एप्लिकेशन दिए गए फ़ाइलनामों (एक्सटेंशन शामिल न करें) को प्ले‑बैक करता है। विकल्प पाइप प्रतीक के बाद भी शामिल किए जा सकते हैं। ‘skip’ विकल्प का अर्थ है कि यदि चैनल ‘up’ स्थिति में नहीं है (अर्थात् अभी तक उत्तर नहीं दिया गया है) तो संदेश का प्ले‑बैक छोड़ दिया जाएगा।

![10-डायलप्लान-उन्नत-विशेषताएँ चित्र 2](../images/10-dialplan-advanced-features-img02.png)

![10-डायलप्लान-उन्नत-विशेषताएँ चित्र 3](../images/10-dialplan-advanced-features-img03.png)

यदि 'skip' निर्दिष्ट किया गया है, तो चैनल यदि हुक पर नहीं है तो एप्लिकेशन तुरंत लौट आएगा। अन्यथा, जब तक 'noanswer' निर्दिष्ट न किया गया हो, चैनल को ध्वनि चलाने से पहले उत्तर दिया जाएगा। सभी चैनल हुक पर रहने के दौरान संदेश चलाने का समर्थन नहीं करते। यदि 'j' निर्दिष्ट किया गया है, तो फ़ाइल के न मिलने पर (यदि मौजूद है) एप्लिकेशन प्राथमिकता n+101 पर कूद जाएगा। इस एप्लिकेशन के पूर्ण होने पर यह निम्नलिखित चैनल वेरिएबल सेट करता है:

- PLAYBACKSTATUS — प्लेबैक प्रयास की स्थिति एक टेक्स्ट स्ट्रिंग के रूप में, निम्नलिखित में से एक:
    - `SUCCESS`
    - `FAILED`

### Read() एप्लिकेशन

This application reads a predetermined number of string digits, a certain number of times, from the user into the given variable.

- filename -- विकल्प i के साथ अंकों या टोन को पढ़ने से पहले चलाने वाली फ़ाइल  
- maxdigits -- स्वीकार्य अंकों की अधिकतम संख्या। maxdigits दर्ज होने के बाद पढ़ना बंद कर देता है (उपयोगकर्ता को # कुंजी दबाने की आवश्यकता के बिना)। डिफ़ॉल्ट 0 है - कोई सीमा नहीं - उपयोगकर्ता को # कुंजी दबाने की प्रतीक्षा करने के लिए। 0 से कम कोई भी मान वही अर्थ रखता है। अधिकतम स्वीकार्य मान 255 है।

![10-डायलप्लान-उन्नत-विशेषताएँ चित्र 4](../images/10-dialplan-advanced-features-img04.png)

![10-dialplan-advanced-features चित्र 5](../images/10-dialplan-advanced-features-img05.png)

- option -- विकल्प हैं `s`, `i`, `n`:
    - `s` — यदि लाइन सक्रिय नहीं है तो तुरंत लौटें
    - `i` — अपने `indications.conf` से फ़ाइलनाम को संकेत टोन के रूप में चलाएँ
    - `n` — यदि लाइन सक्रिय नहीं है तो भी अंकों को पढ़ें
- attempts -- यदि 1 से अधिक है, तो डेटा नहीं दर्ज होने पर किए जाने वाले प्रयासों की संख्या
- timeout -- एक पूर्णांक सेकंड की संख्या जो अंकीय प्रतिक्रिया की प्रतीक्षा के लिए है। यदि 0 से अधिक है, तो यह मान डिफ़ॉल्ट टाइमआउट को ओवरराइड करेगा।

The read() application should disconnect if the function fails or errors out.

### Gotoif() एप्लिकेशन

यह एप्लिकेशन कॉलिंग चैनल को डायल प्लान में निर्दिष्ट स्थान पर कंडीशन के मूल्यांकन के आधार पर ले जाएगा। यदि कंडीशन सत्य है तो चैनल labeliftrue पर जारी रहेगा, या यदि कंडीशन असत्य है तो 'labeliffalse' पर। लेबल्स को उसी सिंटैक्स के साथ निर्दिष्ट किया जाता है जैसा कि Goto एप्लिकेशन में उपयोग किया जाता है। यदि कंडीशन द्वारा चुना गया लेबल छोड़ा जाता है, तो कोई जंप नहीं किया जाता; बल्कि, निष्पादन डायल प्लान में अगली प्रायोरिटी के साथ जारी रहता है।

### प्रयोगशाला: चरण-दर-चरण IVR मेनू बनाना

IVR मेनू बनाते हैं जिसमें निम्नलिखित कार्यक्षमता हो। जब डायल किया जाए, तो IVR एक ऑडियो फ़ाइल चलाता है जिसमें संदेश है “Welcome to the XYZ Corporation; press 1 for sales, 2 for tech support, 3 for training, or wait to speak to a representative.” अंक कॉलर को इस प्रकार रूट करते हैं:

- `1` — बिक्री को ट्रांसफ़र (PJSIP/4001)
- `2` — तकनीकी सहायता को ट्रांसफ़र (PJSIP/4002)
- `3` — प्रशिक्षण को ट्रांसफ़र (PJSIP/4003)
- कोई अंक नहीं दबाया गया — ऑपरेटर को ट्रांसफ़र (PJSIP/4000)

**चरण 1 – प्रॉम्प्ट रिकॉर्ड करें**

आइए एक एक्सटेंशन बनाते हैं जो प्रॉम्प्ट्स को रिकॉर्ड करे। प्रॉम्प्ट रिकॉर्ड करने के लिए, सॉफ्टफोन से `9003<filename>` पर डायल करें (उदाहरण के लिए, `9003welcome`)। जब आप बीप सुनें, रिकॉर्डिंग शुरू करें; रोकने के लिए `#` दबाएँ। आपको बीप सुनाई देगा, और सिस्टम रिकॉर्ड किए गए प्रॉम्प्ट को वापस चलाएगा।

**Step 2 – मेनू लॉजिक बनाएं**

जब 9004 एक्सटेंशन डायल किया जाता है, प्रोसेसिंग `s` एक्सटेंशन के मेन्यू पर, प्रायोरिटी 1 पर चली जाती है।

### डायल करते समय मिलान

This is a company setup menu for receiving calls. The `Background()` application plays the welcome prompt and then waits for digits, matching what the caller dials against the extensions defined in the current context.

```
[incoming]
exten=>s,1,Background(welcome)
exten=>1,1,Dial(DAHDI/1)
exten=>2,1,Dial(DAHDI/2)
exten=>21,1,Dial(DAHDI/3)
exten=>22,1,Dial(DAHDI/4)
exten=>31,1,Dial(DAHDI/5)
exten=>32,1,Dial(DAHDI/6)
```

जब आप इस कंपनी को डायल करते हैं, तो सबसे पहले स्वागत संदेश बजता है। उसके बाद, Asterisk एक अंक डायल होने की प्रतीक्षा करता है:

| डायल किया गया नंबर | Asterisk कार्रवाई |
|---------------|-----------------|
| 1 | तुरंत `Dial(DAHDI/1)` को कॉल करता है |
| 2 | टाइमआउट का इंतज़ार करता है, फिर `Dial(DAHDI/2)` को कॉल करता है |
| 21 | तुरंत `Dial(DAHDI/3)` को कॉल करता है |
| 22 | तुरंत `Dial(DAHDI/4)` को कॉल करता है |
| 3 | टाइमआउट का इंतज़ार करता है, फिर कनेक्शन समाप्त करता है |
| 31 | तुरंत `Dial(DAHDI/5)` को कॉल करता है |
| 32 | तुरंत `Dial(DAHDI/6)` को कॉल करता है |

मेन्यू में अस्पष्टता से बचना महत्वपूर्ण है। हर कोई जल्दी उत्तर चाहता है। इस कारण, आपको नंबर 2, 21, या 22 का उपयोग नहीं करना चाहिए।

### लैब: Read() एप्लिकेशन का उपयोग

कृपया read() एप्लिकेशन के साथ लैब आज़माएँ। Read उपयोगकर्ता से अंक स्वीकार करता है और उन्हें निर्दिष्ट वेरिएबल में डालता है; आप फिर gotoif एप्लिकेशन का उपयोग करके कॉल को पुनर्निर्देशित कर सकते हैं।

## Context inclusion

एक context दूसरे context की सामग्री को शामिल कर सकता है। ऊपर के उदाहरण में, कोई भी चैनल internal context में किसी भी एक्सटेंशन को डायल कर सकता है, लेकिन केवल 4003 चैनल अंतरराष्ट्रीय एक्सटेंशन को डायल कर सकता है। आप context inclusion का उपयोग करके डायल प्लान बनाना आसान बना सकते हैं। context inclusion का उपयोग करके आप यह नियंत्रित कर सकते हैं कि किसके पास कौन से एक्सटेंशन तक पहुँच है।

### Troubleshooting the message “number not found”

“number not found” संदेश प्राप्त होना बहुत आम है। अधिकांश लोग included contexts की अवधारणा को भ्रमित करते हैं क्योंकि यह वास्तव में सहज नहीं है। एक सामान्य नियम के रूप में, पहले incoming channel configuration फ़ाइल, जैसे `pjsip.conf`, `chan_dahdi.conf`, और `iax.conf`, पर जाएँ और वर्तमान context निर्धारित करें। फिर, extensions.conf फ़ाइल में डायल प्लान पर जाएँ और जांचें कि डायल किया गया नंबर उस context में पाया जाता है या नहीं। यदि नहीं, तो आपके डायल प्लान में कुछ गड़बड़ है। contexts के स्वर्ण नियम हैं: 1. एक चैनल केवल उसी context के भीतर नंबर डायल कर सकता है जिसमें वह चैनल है। 2. वह context जहाँ कॉल प्रोसेस की जाती है, incoming channel configuration फ़ाइल (`chan_dahdi.conf`, `iax.conf`, `pjsip.conf`) में परिभाषित होती है।

## स्विच स्टेटमेंट का उपयोग

आप स्विच कमांड का उपयोग करके डायलप्लान प्रोसेसिंग को किसी अन्य सर्वर पर भेज सकते हैं। आपको अन्य सर्वर का नाम और कुंजी चाहिए होगी। कॉन्टेक्स्ट गंतव्य कॉन्टेक्स्ट है।

![10-डायलप्लान-एडवांस्ड-फ़ीचर चित्र 6](../images/10-dialplan-advanced-features-img06.png)

## Dial plan processing order

जब Asterisk को कोई इनकमिंग कॉल मिलती है, तो वह चैनल द्वारा परिभाषित कॉन्टेक्स्ट में देखता है। कुछ मामलों में, यदि एक से अधिक पैटर्न डायल किए गए नंबर से मेल खाते हैं, तो Asterisk कॉल को ठीक उसी तरह प्रोसेस नहीं कर पाता जैसा आप सोचते हैं। आप `dialplan show` CLI कमांड का उपयोग करके मैचिंग क्रम देख सकते हैं। उदाहरण: मान लीजिए आप 912 को एक एनालॉग ट्रंक (DAHDI/1) पर रूट करना चाहते हैं और 9 से शुरू होने वाले सभी अन्य नंबरों को दूसरे एनालॉग ट्रंक (DAHDI/2) पर। आप कुछ इस तरह लिखेंगे:

```
[example]
exten=>_912.,1,Dial(DAHDI/1/${EXTEN})
exten=>_9.,1,Dial(DAHDI/2/${EXTEN})
```

यदि दो पैटर्न किसी एक्सटेंशन से मेल खाते हैं, तो आप शामिल किए गए कॉन्टेक्स्ट्स का उपयोग करके यह नियंत्रित कर सकते हैं कि कौन सा एक्सटेंशन पहले प्रोसेस हो। एक शामिल किया गया कॉन्टेक्स्ट उसी कॉन्टेक्स्ट में पैटर्न की तुलना में बाद में प्रोसेस किया जाता है।

## The #INCLUDE statement

क्या हमें एक बड़ी फ़ाइल का उपयोग करना चाहिए या कई फ़ाइलें? आप अपने extensions.conf में अन्य फ़ाइलों को शामिल करने के लिए #include <filename> कथन का उपयोग कर सकते हैं। उदाहरण के लिए, हम स्थानीय उपयोगकर्ताओं के लिए users.conf और विशेष सेवाओं के लिए services.conf बना सकते हैं। ध्यान रखें कि #include <filename> को ... के साथ भ्रमित न करें

```
include=>context statement.
```

## GOSUB के साथ सबरूटीन

पुराने संस्करणों में Asterisk में आपके पास Macro कमांड था। यह कमांड बहुत समय पहले GOSUB के पक्ष में अप्रचलित कर दिया गया था। हम यहाँ दिखाएंगे कि कैसे आसान और व्यवस्थित तरीके से voicemail प्रोसेसिंग के लिए सबरूटीन बनाएँ। कमांड फ़ॉर्मेट:

```
gosub([[context,]exten,]priority[(arg1[,...][,argN])])
```

GOSUB कमांड Asterisk 1.6 से उपलब्ध है और यह आर्ग्यूमेंट पास करने का समर्थन करता है (सबरूटीन के अंदर `${ARG1}`, `${ARG2}` आदि के रूप में उपलब्ध)। आर्ग्यूमेंट्स के साथ, अब पुराने Macro कमांड को पूरी तरह से बदलना संभव है। Macros (`app_macro`) को Asterisk 21 में हटा दिया गया; आपको सबरूटीन के लिए GOSUB का उपयोग करना होगा।

### सबरूटीन बनाना

परिभाषा बहुत समान है। नीचे voicemail के लिए stdexten नाम से परिभाषित सबरूटीन देखें (आप अपनी पसंद का नाम चुन सकते हैं)। पहले आर्ग्यूमेंट (channel का नाम) के साथ Dial कमांड को कॉल करने के बाद हम ${DIALSTATUS} की जाँच करते हैं ताकि कॉल लॉजिक को अगले चरण में भेजा जा सके।

```
[stdexten]
exten=>s,1,Dial(${ARG1},20,tT)
exten=>s,n,Goto(${DIALSTATUS})
exten=>s,n,hangup()
exten=>s,n(BUSY),voicemail(${ARG2},b)
exten=>s,n,hangup()
exten=>s,n(NOANSWER),voicemail(${ARG2},u)
exten=>s,n,hangup()
exten=>s,n(CANCEL),hangup
exten=>s,n(CHANUNAVAIL),hangup
exten=>s,n(CONGESTION),hangup
```

### सबरूटीन को कॉल करना

सबरूटीन को कॉल करते समय पैरामीटर से पहले कोष्ठक (parenthesis) का उपयोग करना याद रखें।

```
exten=>6000,1,Gosub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten=>6001,1,Gosub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten=>6002,1,Gosub(stdexten,s,1(PJSIP/6002,${EXTEN}))
exten=>6003,1,Gosub(stdexten,s,1(PJSIP/6003,${EXTEN}))
```

## Using Asterisk DB

कॉल फ़ॉरवर्ड और ब्लैक लिस्ट को लागू करने के लिए हमें डेटा को संग्रहीत और पुनः प्राप्त करने का कोई तरीका चाहिए। सौभाग्य से, Asterisk एक बिल्ट‑इन डेटाबेस AstDB से डेटा स्टोर और रिट्रीव करने का मैकेनिज़्म प्रदान करता है। आधुनिक Asterisk (जिसमें Asterisk 22 भी शामिल है) में AstDB **SQLite3** (फ़ाइल `/var/lib/asterisk/astdb.sqlite3`) द्वारा समर्थित है; Asterisk 1.8 और उससे पहले Berkeley DB v1 का उपयोग करता था। यह Windows रजिस्ट्री डेटाबेस के समान है जहाँ फ़ैमिली और कीज़ की पदानुक्रमित अवधारणा होती है। डेटा Asterisk रीस्टार्ट के बीच बना रहता है। फ़ैमिली/की API पुराने बैकएंड से अपरिवर्तित है; केवल ऑन‑डिस्क स्टोरेज फ़ॉर्मेट बदल गया है।

### Functions, applications, and CLI commands

AstDB के साथ काम करने वाले कुछ फ़ंक्शन, एप्लिकेशन और CLI कमांड हैं:

- variable=${DB(<family/key>)}
- DB(<family/key>)=value
- DB_EXISTS(<family/key>)

Examples:

```
exten=_*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
exten=s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

कुछ एप्लिकेशन AstDB को मैनीपुलेट करने के लिए उपयोग किए जा सकते हैं:

- DB_DELETE(<family/key>) — फ़ंक्शन जो एकल की को रिटर्न करता है और डिलीट करता है
- DBdeltree(<family>) — एप्लिकेशन जो पूरी फ़ैमिली/सबट्री को डिलीट करता है

पुराना `DBdel()` एप्लिकेशन Asterisk 22 में अब मौजूद नहीं है। एकल की को डिलीट करने के लिए `DB_DELETE()` डायलप्लान फ़ंक्शन का उपयोग करें — उदाहरण के लिए `Set(x=${DB_DELETE(family/key)})` या, लिखने के ऑपरेशन के रूप में, `Set(DB_DELETE(family/key)=)`। `DBdeltree()` (पूरी फ़ैमिली/सबट्री को डिलीट करना) अभी भी एक एप्लिकेशन है।

CLI कमांड्स का उपयोग करके भी कीज़ को सेट और डिलीट किया जा सकता है:

- database del
- database put
- database show <family[/key]>
- database showkey
- database deltree
- database get

![10-dialplan-advanced-features figure 7](../images/10-dialplan-advanced-features-img07.png)

![10-dialplan-advanced-features figure 8](../images/10-dialplan-advanced-features-img08.png)

### Implementing Call Forward, DND, and Blacklists

इस उदाहरण में, आप कॉल फ़ॉरवर्ड इमीडिएट और कॉल फ़ॉरवर्ड ऑन बज़ी को कैसे लागू किया जाता है, सीखेंगे। हम *21* का उपयोग करके कॉल फ़ॉरवर्ड इमीडिएट प्रोग्राम करेंगे और *61* का उपयोग करके कॉल फ़ॉरवर्ड ऑन बज़ी स्टेटस प्रोग्राम करेंगे। प्रोग्रामिंग को कैंसल करने के लिए क्रमशः #21# और #61# का उपयोग करें। ऊपर दिया गया उदाहरण डेटाबेस को पॉप्युलेट करने के लिए उपयोग करें। उपयोग की गई फ़ैमिली:

- CFIM – Call Forward Immediate
- CFBS – Call Forward on Busy status
- DND – Do Not Disturb

डेटाबेस को पॉप्युलेट करने के लिए डायल करें:

- *21* (कॉल फ़ॉरवर्ड इमीडिएट के लिए डेस्टिनेशन एक्सटेंशन)
- *61* (कॉल फ़ॉरवर्ड ऑन बज़ी स्टेटस के लिए डेस्टिनेशन एक्सटेंशन)
- *41* (डू नॉट डिस्ट्रब नहीं करने के लिए एक्सटेंशन)

CLI कमांड `database show` का उपयोग करके जोड़ी गई फ़ैमिली, कीज़ और वैल्यूज़ देखें।

![10-dialplan-advanced-features figure 9](../images/10-dialplan-advanced-features-img09.png)

![10-dialplan-advanced-features figure 10](../images/10-dialplan-advanced-features-img10.png)

### Call Forward, Blacklist, DND

सबरूटीन यह जांचता है कि डेटाबेस में CFIM, CFBS, या DND के अनुरूप key:value जोड़े मौजूद हैं या नहीं, और फिर उन्हें उपयुक्त रूप से हैंडल करता है। निम्नलिखित सबरूटीन डायलिंग रूटीन को कॉल करता है:

```
exten=_4XXX,1,gosub(stdexten,s,1(${EXTEN}))
```

## Using a blacklist

पुराना `LookupBlacklist()` एप्लिकेशन **हटा दिया गया** है Asterisk से (यह लेगेसी "priority+101 jump" मेकेनिज़्म के साथ गायब हो गया)। Asterisk 22 में आप सीधे `DB_EXISTS()` फ़ंक्शन के साथ एक ब्लैकलिस्ट बनाते हैं (जो एक कुंजी की जाँच करता है और, यदि मिलती है, तो उसकी वैल्यू को `${DB_RESULT}` में उजागर करता है) साथ ही `GotoIf` का उपयोग करके। प्रत्येक ब्लॉक किए गए नंबर को एक `blacklist` फ़ैमिली में कुंजी के रूप में संग्रहीत करें, फिर अपने इनकमिंग कॉन्टेक्स्ट के शीर्ष पर कॉलर आईडी की जाँच करें:

```
[incoming]
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()
[blocked]
exten => s,1,Answer()
exten => s,2,Playback(blockedcall)
exten => s,3,Hangup()
```

`DB_EXISTS(blacklist/${CALLERID(num)})` तब `1` लौटाता है जब कॉलर का नंबर डेटाबेस में मौजूद होता है (कॉल को `blocked` कॉन्टेक्स्ट में भेजते हुए) और अन्यथा `0`, इसलिए कॉल सामान्य `Dial()` की ओर बढ़ता है।

ब्लैकलिस्ट में एक नंबर जोड़ने के लिए, हम पहले की तरह ही रिसोर्स का उपयोग कर सकते हैं, *31* के बाद उन एक्सटेंशन को लिखें जिन्हें ब्लैकलिस्ट में डालना है। ब्लैकलिस्ट से एक नंबर हटाने के लिए, आपको #31# के बाद हटाने वाले नंबर को लिखना चाहिए।

```
[apps]
exten=>_*31*X.,1,Set(DB(blacklist/${EXTEN:4})=1)
exten=>_*31*X.,2,Hangup()
exten=>_#31#X.,1,Set(x=${DB_DELETE(blacklist/${EXTEN:4})})
exten=>_#31#X.,2,Hangup()
```

आप कंसोल CLI का उपयोग करके भी ब्लैकलिस्ट में नंबर जोड़ सकते हैं:

```
*CLI>database put blacklist <name/number> 1
```

ध्यान दें: किसी भी वैल्यू को कुंजी के साथ जोड़ा जा सकता है। `DB_EXISTS()` टेस्ट कुंजी की खोज करता है, वैल्यू नहीं। ब्लैकलिस्ट से नंबर हटाने के लिए, आप उपयोग कर सकते हैं:

```
*CLI>database del blacklist <name/number>
```

## Time-based contexts

निम्न चित्र में, हमारे पास तीन कॉन्टेक्स्ट वाले एक डायल प्लान हैं। **[incoming]** कॉन्टेक्स्ट वह जगह है जहाँ आमतौर पर कॉल प्राप्त होते हैं। हमने चार लाइनों को शामिल किया है जो सिस्टम समय के आधार पर व्यवहार बदलते हैं, जैसा कि नीचे उदाहरण दिया गया है:

```
include => context,<times>,<weekdays>,<mdays>,<months>
```

Modern Asterisk (including 22) समय-शामिल फ़ील्ड को **कॉमा** से अलग करता है, पाइप नहीं। लेगेसी पाइप रूप (`include => context|times|weekdays|mdays|months`) को एक साधारण लिटरल कॉन्टेक्स्ट नाम के रूप में पार्स किया जाता है और किसी भी समय शर्त को लागू करने में चुपचाप विफल हो जाता है।

नियमित कार्य समय के दौरान, प्रोसेसिंग को mainmenu की ओर पुनः निर्देशित किया जाएगा, जहाँ यह संभवतः एक IVR को कॉल करेगा ताकि इनकमिंग कॉल को संभाला जा सके। यदि कॉल कार्य समय के बाद आती है, तो यह ${SECURITY} वेरिएबल में परिभाषित सुरक्षा एक्सटेंशन को कॉल करेगा। यदि सुरक्षा एक्सटेंशन कॉल का उत्तर नहीं देता, तो इसे ऑपरेटर की voicemail पर भेज दिया जाएगा।

![10-dialplan-advanced-features figure 11](../images/10-dialplan-advanced-features-img11.png)

![10-dialplan-advanced-features figure 12](../images/10-dialplan-advanced-features-img12.png)

## Time-based messages using gotoiftime()

The GotoIfTime() syntax is shown below.

```
GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])
```

In Asterisk 22 the field separator is a **comma**, not a pipe (the pipe form was deprecated in Asterisk 1.6). An optional `timezone` field is supported, and each branch label uses the usual `[[context,]extension,]priority` form.

This application can replace the time-based context and seems easier to understand and read. You can specify the time as follows:

- <timerange>=<hour>':'<minute>'-'<hour>':'<minute> |"*"
- <daysofweek>=<dayname>|<dayname>'-'<dayname>|"*"
- <dayname>="sun"|"mon"|"tue"|"wed"|"thu"|"fri"|"sat"
- <daysofmonth>=<daynum>|<daynum>'-'<daynum> |"*"
- <daynum>=number from 1 to 31
- <hour>=number from 0 to 23
- <minute>=number from 0 to 59
- <months>=<monthname>|<monthname>'-'<monthname>|"*"
- <monthname>="jan"|"feb"|"mar"|"apr"|"may"|"jun"|"jul"|"aug"|"sep"|"oct"|"nov"|"dec"

Names for days and months are not case sensitive.

```
exten=>s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

The previous statement transfers the processing to the extension s in the normalhours context if the call is between 08:00AM and 06:00PM from Monday to Friday.

## Using DISA to get a new dial tone

DISA, या “direct inward system access,” एक प्रणाली है जो उपयोगकर्ताओं को दूसरा डायल टोन प्राप्त करने की अनुमति देती है। यह उपयोगकर्ताओं को फिर से किसी अन्य गंतव्य पर डायल करने की सुविधा देती है। यह अक्सर तकनीशियनों द्वारा सप्ताहांत में तकनीकी सहायता के लिए लांग‑डिस्टेंस कॉल करने के समय उपयोग किया जाता है; अपने घर से सीधे गंतव्य पर डायल करने के बजाय, वे ऑफिस के DISA नंबर को कॉल करते हैं, डायल टोन प्राप्त करते हैं, और फिर गंतव्य को कॉल करते हैं। लांग‑डिस्टेंस शुल्क कंपनी पर लागू होते हैं, न कि घर के फोन पर।

```
DISA(passcode|filename[,context[,cid[,mailbox[@context][,options]]]])
```

उदाहरण:

```
exten => s,1,DISA(no-password,default)
```

पिछले कथन का उपयोग करते हुए, उपयोगकर्ता PBX को डायल करता है और—बिना किसी पासवर्ड की आवश्यकता के—डायल टोन प्राप्त करता है। DISA का उपयोग करने वाली कोई भी कॉल `default` कॉन्टेक्स्ट का उपयोग करके प्रोसेस की जाएगी। इस एप्लिकेशन के तर्कों में एक ग्लोबल पासवर्ड या फ़ाइल में व्यक्तिगत पासवर्ड शामिल हो सकता है। यदि कोई कॉन्टेक्स्ट निर्दिष्ट नहीं किया गया है, तो `disa` कॉन्टेक्स्ट मान लिया जाता है। यदि आप पासवर्ड फ़ाइल का उपयोग करते हैं, तो पूर्ण पथ निर्दिष्ट करना आवश्यक है। DISA बाहरी डायलिंग के लिए एक कॉलर ID भी निर्दिष्ट की जा सकती है। उदाहरण:

```
exten => s,1,DISA(numeric-passcode,default,"Flavio" <4830258590>)
```

Asterisk 22 तर्क विभाजकों के रूप में कॉमा का उपयोग करता है (पाइप रूप 1.6 में अप्रचलित कर दिया गया था)। पहला तर्क या तो एकल पासकोड या पासकोड फ़ाइल का पथ होता है, और जब कोई तर्क नहीं दिया जाता तो डिफ़ॉल्ट कॉन्टेक्स्ट `disa` है।

## समानांतर कॉल्स को सीमित करें

GROUP() फ़ंक्शन आपको यह गिनने की अनुमति देता है कि आप एक समूह में एक ही समय में कितने सक्रिय चैनल रख रहे हैं। उदाहरण: आपके पास रियो डी जनेरियो में एक शाखा है, जहाँ फ़ोन “_214X” पैटर्न का अनुसरण करते हैं। इस स्थान को एक लीज़्ड लाइन द्वारा सर्व किया जाता है, जिसमें आवाज़ बैंडविड्थ के लिए 64K आरक्षित है। इस मामले में, अनुमत अधिकतम कॉल्स की संख्या 2 है (G.729, प्रति कॉल लगभग 31.2K)। रियो के लिए कॉल्स को दो तक सीमित करने के लिए:

```
exten=>_214X,1,set(GROUP()=Rio)
exten=>_214X,n,Gotoif($[${GROUP_COUNT()} > 1]?outoflimit)
exten=>_214X,n,Dial(PJSIP/${EXTEN})
exten=>_214X,n,hangup
exten=>_214X,n(outoflimit),playback(callsexceedcapacity)
exten=>_214X,n,hangup
```

## Voicemail

Voicemail एक कंप्यूटरीकृत टेलीफ़ोन उत्तर प्रणाली है जो आने वाले आवाज़ संदेशों को रिकॉर्ड करती है, उन्हें डिस्क पर सहेजती है या ई‑मेल के माध्यम से भेजती है। कभी‑कभी इसमें एक निर्देशिका होती है जहाँ आप नाम से voicemail बॉक्स देख सकते हैं। पहले, voicemail प्रणालियाँ बहुत महंगी थीं। अब, IP टेलीफ़ोनी के साथ, voicemail एक मानक सुविधा बनती जा रही है।

Voicemail को कॉन्फ़िगर करने के लिए, आपको निम्नलिखित चरणों से गुजरना चाहिए।

**Step 1: Edit `voicemail.conf` and set the general parameters.**

- `format` — संदेश को रिकॉर्ड करने के लिए उपयोग किया जाने वाला codec (उदा., wav49, wav, gsm)
- `serveremail` — ई‑मेल सूचना किससे आ रही दिखनी चाहिए
- `maxmsg` — मेलबॉक्स में अधिकतम संदेशों की संख्या; इस सीमा के बाद संदेश हटा दिए जाते हैं
- `maxsecs` — voicemail संदेश की अधिकतम लंबाई, सेकंड में
- `minsecs` — संदेश की न्यूनतम लंबाई, सेकंड में; इस सीमा से कम होने पर कोई संदेश रिकॉर्ड नहीं किया जाता
- `maxsilence` — कितने सेकंड की चुप्पी को संदेश के अंत के रूप में माना जाए

**Step 2: Edit `voicemail.conf` and create the users’ mailboxes.**

### Voicemail.conf

एक मेलबॉक्स को प्रत्येक मेलबॉक्स के लिए एक पंक्ति के रूप में परिभाषित किया जाता है, इस रूप में:

```
mailboxID => pincode,fullname,email,pager-email,options
```

फ़ील्ड्स हैं:

- **MailboxID** — आमतौर पर एक्सटेंशन नंबर
- **Pincode** — voicemail प्रणाली तक पहुँचने का पासवर्ड
- **Full name** — निर्देशिका अनुप्रयोग द्वारा उपयोग किया जाता है
- **E-mail** — voicemail सूचना के लिए पता
- **Pager e-mail** — SMS गेटवे या पेजर के माध्यम से सूचना के लिए पता
- **Options** — प्रति‑मेलबॉक्स विकल्प (`[general]` में वही विकल्प, लेकिन इस मेलबॉक्स पर लागू)

Voicemail में कई विकल्प होते हैं जो उसके व्यवहार को नियंत्रित करते हैं। अभी के लिए, हम डिफ़ॉल्ट विकल्पों पर ही रहेंगे और मेलबॉक्स परिभाषा पर ध्यान देंगे। फ़ाइल में `[general]` सेक्शन के बाद, आप प्रत्येक कॉन्टेक्स्ट में मेलबॉक्स IDs को कॉन्फ़िगर करना शुरू करते हैं। उदाहरण:

```
[general]
[default]
1234=>1234,SomeUser,email@address.com,pager@address.com,saycid=yes|dialout=fromvm|callback=fromvm|review=yes|operator=yes
```

फ़ाइल `voicemail.conf` में उन्नत विकल्पों की जाँच करें।

**Step 3: Configure the file `extensions.conf`.**

पहले दिखाए गए `stdexten` सबरूटीन (*Subroutines with GOSUB* के तहत) ठीक वही कॉल/voicemail हैंडलर है जिसकी आपको यहाँ आवश्यकता है: यह एक्सटेंशन डायल करता है और चैनल वेरिएबल `${DIALSTATUS}` के मान का उपयोग करके कॉल फ्लो को उचित voicemail अभिवादन (busy के लिए `b`, unavailable के लिए `u`) की ओर रीडायरेक्ट करता है। इसे `Gosub(stdexten,s,1(PJSIP/<device>,<mailbox>))` के साथ प्रत्येक एक्सटेंशन में `extensions.conf` से कॉल करें।

## Using the VoiceMailMain() application

The application voicemailmain() is used to configure the voicemail mailbox. Users can dial the application, record their greeting, and listen to their voicemail. To call the application in the dial plan, use:

```
exten=>9000,1,VoiceMailMain()
```

Below you will find a list of the options available for the application.

### Voicemail application syntax

This application allows the calling party to leave a message for a specified list of mailboxes. When multiple mailboxes are specified, the greeting will be taken from the first specified mailbox. The dial plan execution will stop if the specified mailbox does not exist. The syntax is shown below:

```
 [Synopsis]
Leave a Voicemail message.
[Description]
This application allows the calling party to leave a message for the specified
list of mailboxes. When multiple mailboxes are specified, the greeting will
be taken from the first mailbox specified. Dialplan execution will stop if
the specified mailbox does not exist.
The Voicemail application will exit if any of the following DTMF digits are
received:
    0 - Jump to the 'o' extension in the current dialplan context.
    * - Jump to the 'a' extension in the current dialplan context.
This application will set the following channel variable upon completion:
${VMSTATUS}: This indicates the status of the execution of the VoiceMail
application.
    SUCCESS
    USEREXIT
    FAILED
[Syntax]
VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])
[Arguments]
options
```

![10-dialplan-advanced-features figure 13](../images/10-dialplan-advanced-features-img13.png)

```
    b: Play the 'busy' greeting to the calling party.
    d([c]): Accept digits for a new extension in context <c>, if played
    during the greeting. Context defaults to the current context.
    g(#): Use the specified amount of gain when recording the voicemail
    message. The units are whole-number decibels (dB). Only works on supported
    technologies, which is DAHDI only.
    s: Skip the playback of instructions for leaving a message to the
    calling party.
    u: Play the 'unavailable' greeting.
    U: Mark message as 'URGENT'.
    P: Mark message as 'PRIORITY'.
```

In all cases, the beep.gsm file will be played before the recording begins. Voicemail messages will be stored in the inbox directory.

```
/var/spool/asterisk/voicemail/context/boxnumber/INBOX/
```

If a caller presses 0 (zero) during the announcement, it will be moved to the ‘o’ (out) extension in the voicemail current context. This can be used to exit to the operator. If during the recording the caller presses # or the silence limit times out, recording is stopped and the call goes to the next priority. Make sure that you handle the call after the voicemail is played, as shown below.

```
exten=>somewhere,5,Playback(Goodbye)
exten=>somewhere,6,Hangup
```

### Tagging voicemail messages as urgent

You may tag some messages as “urgent.” Two methods are available for this:

- Pass the option ‘U’ in the application voicemail()
- Specify review=yes in the file voicemail.conf. If using this option, the user will be able to tag the message as urgent after recording the voice instructions.

## ई‑मेल पर वॉइसमेल भेजना

कुछ मामलों में (जैसे मेरे), हम वॉइसमेलमेन() एप्लिकेशन का उपयोग करके ई‑मेल पढ़ते नहीं हैं। सभी संदेशों को ऑडियो के साथ संलग्न करके ई‑मेल पर भेजना सरल और अधिक व्यावहारिक है। ‘attach’ और ‘delete’ पैरामीटर का उपयोग करके आप सभी मेल को ई‑मेल पर भेज सकते हैं और उन्हें मेलबॉक्स से हटा सकते हैं।

```
attach=yes
delete=yes
```

वॉइसमेल को ई‑मेल पर भेजने के लिए, वॉइसमेल एप्लिकेशन आपके ऑपरेटिंग सिस्टम के संदेश ट्रांसफ़र एजेंट (MTA) का उपयोग करता है। डेबियन MTA के रूप में Exim का उपयोग करता है। वह एप्लिकेशन जो ई‑मेल भेजता है, उसे ‘mailcmd’ पैरामीटर में परिभाषित किया गया है।

```
mailcmd =/usr/sbin/sendmail -t
```

डेबियन वितरण वाले लिनक्स में, MTA Exim है। डेबियन में Exim को कॉन्फ़िगर करने के लिए, उपयोग करें:

```
dpkg-reconfigure exim4-config
```

आप चुन सकते हैं कि आपका MTA सीधे SMTP के माध्यम से या एक स्मार्टहोस्ट (आमतौर पर आपके कंपनी के मेल सर्वर) के माध्यम से ई‑मेल भेजे। Asterisk सर्वर से आपके ई‑मेल सर्वर तक ई‑मेल भेजने का सर्वोत्तम तरीका जानने के लिए अपने ई‑मेल प्रशासक से पुष्टि करें।

## Customizing the e-mail message

आप संदेशों को कैसे भेजा जाए, इसे निम्नलिखित वेरिएबल्स सेट करके नियंत्रित कर सकते हैं: ई‑मेल विषय और ई‑मेल बॉडी के लिए वेरिएबल्स:

- VM_NAME
- VM_DUR
- VM_MSGNUM
- VM_MAILBOX
- VM_CIDNUM
- VM_CIDNAME
- VM_CALLERID
- VM_DATE

ई‑मेल बॉडी और विषय एक टेम्प्लेट से बनते हैं जिसे आप `[general]` सेक्शन में `voicemail.conf` में सेट करते हैं। आप बॉडी और विषय दोनों को संशोधित कर सकते हैं, लेकिन संदेश का आकार सीमा 512 बाइट्स है। टेम्प्लेट में, `\n` एक नई पंक्ति डालता है और `\t` एक टैब डालता है।

नीचे दिया गया `emailsubject` उदाहरण सरल है। `emailbody` उदाहरण डिफ़ॉल्ट के बहुत करीब है; डिफ़ॉल्ट केवल CIDNAME दिखाता है जब वह नल नहीं होता, अन्यथा CIDNUM, या जब दोनों नल हों तो "an unknown caller" दिखाता है।

```
emailsubject=[PBX]: New message ${VM_MSGNUM} in mailbox ${VM_MAILBOX}

emailbody=Dear ${VM_NAME}:\n\n\tjust wanted to let you know you were just left a ${VM_DUR} long message (number ${VM_MSGNUM})\nin mailbox ${VM_MAILBOX} from ${VM_CALLERID}, on ${VM_DATE}, so you might\nwant to check it when you get a chance. Thanks!\n\n\t\t\t\t--Asterisk\n
```

## Voicemail Web interface

There is a Perl script in the source distribution called `vmail.cgi`, located at `contrib/scripts/vmail.cgi` in the Asterisk source tree (it still ships with Asterisk 22). The command `make install` does not install this interface; you must run `make webvmail` from the source directory. This script requires the Perl command interpreter and a web server (such as Apache) to be installed on the server.

```
make webvmail
```

The `make webvmail` target installs the script (setuid root) into your web server's CGI directory (`HTTP_CGIDIR`) and copies the supporting images from `images/*.gif` into `HTTP_DOCSDIR/_asterisk` (by default `/var/www/html/_asterisk`). If those paths do not match your web server layout, edit the `HTTP_CGIDIR` and `HTTP_DOCSDIR` variables in the top-level `Makefile` before running the target.

## Voicemail notification

आप नई वॉइसमेल मिलने पर अपने फ़ोन पर एक नोटिफ़िकेशन संदेश भेजने के लिए वॉइसमेल को कॉन्फ़िगर कर सकते हैं। Asterisk 22 में, Message Waiting Indication (MWI) PJSIP और SIP फ़ोनों के साथ-साथ DAHDI फ़ोनों पर भी काम करता है। अनसुनी वॉइसमेल को दर्शाने के लिए, एक इंडिकेटर लाइट ब्लिंक कर सकती है या फ़ोन एक शटर टोन बजा सकता है। आपको संबंधित चैनल कॉन्फ़िगरेशन फ़ाइल में मेलबॉक्स को कॉन्फ़िगर करना होगा। उदाहरण: `pjsip.conf` (एंडपॉइंट सेक्शन में):

```
mailboxes=8590
```

PJSIP में मेलबॉक्स हिंट को `mailboxes` विकल्प के साथ `pjsip.conf` के एंडपॉइंट सेक्शन में सेट किया जाता है, न कि पुराने `mailbox=` के `sip.conf` में। MWI सब्सक्रिप्शन को `res_pjsip_mwi` मॉड्यूल द्वारा संभाला जाता है।

![The Comedian Mail web interface (`vmail.cgi`): the Asterisk Web-Voicemail login — enter your mailbox and password to play, save, forward, or delete voicemail from a browser. It still ships with Asterisk 22 and is installed with `make webvmail`.](../images/10-dialplan-advanced-features-img14.png)

### Lab: Message Notification in the Phone

यह लैब एक SIP सॉफ्टफ़ोन का उपयोग करके परीक्षण की गई थी।

1. `pjsip.conf` को संपादित करें और डिवाइस जिसका नाम 4401 है, उसके एंडपॉइंट सेक्शन में `mailboxes=4401` जोड़ें।
2. `extensions.conf` को संपादित करें और 4401 एक्सटेंशन के लिए एक एक्सटेंशन बनाकर वॉइसमेल रिकॉर्ड करें।

```
exten=9008,1,voicemail(4401,b)
```

3. कंसोल पर जाएँ और रीलोड करें।
4. SipPulse Softphone में, SIP अकाउंट सेटिंग्स खोलें और अकाउंट के लिए वॉइसमेल (message-waiting) जांच को सक्षम करें।
5. 9008 डायल करें और एक संदेश छोड़ें।
6. फ़ोन पर संदेश आइकन को देखें।

## Using the directory application

यह एप्लिकेशन आपको जल्दी से किसी उपयोगकर्ता को डायल करने के लिए खोजने की सुविधा देता है। नामों की सूची और संबंधित एक्सटेंशन voicemail कॉन्फ़िगरेशन फ़ाइल voicemail.conf से प्राप्त किए जाते हैं। एप्लिकेशन की सिंटैक्स को core show application directory का उपयोग करके दिखाया जा सकता है:

```
-= Info about application 'Directory' =-
[Synopsis]
Provide directory of voicemail extensions.
[Description]
This application will present the calling channel with a directory of
extensions from which they can search by name. The list of names and
corresponding extensions is retrieved from the voicemail configuration file,
"voicemail.conf".
This application will immediately exit if one of the following DTMF digits
are received and the extension to jump to exists:
'0' - Jump to the 'o' extension, if it exists.
'*' - Jump to the 'a' extension, if it exists.
[Syntax]
Directory([vm-context][,dial-context[,options]])
[Arguments]
vm-context
    This is the context within voicemail.conf to use for the Directory.
    If not specified and 'searchcontexts=no' in "voicemail.conf", then
    'default' will be assumed.
dial-context
    This is the dialplan context to use when looking for an extension
    that the user has selected, or when jumping to the 'o' or 'a' extension.
options
    e: In addition to the name, also read the extension number to the
    caller before presenting dialing options.
    f(n): Allow the caller to enter the first name of a user in the
    directory instead of using the last name.  If specified, the optional
    number argument will be used for the number of characters the user should
    enter.
    l(n): Allow the caller to enter the last name of a user in the
    directory.  This is the default.  If specified, the optional number
    argument will be used for the number of characters the user should enter.
    b(n):  Allow the caller to enter either the first or the last name
    of a user in the directory.  If specified, the optional number argument
    will be used for the number of characters the user should enter.
    m: Instead of reading each name sequentially and asking for
    confirmation, create a menu of up to 8 names.
    p(n): Pause for n milliseconds after the digits are typed.  This
    is helpful for people with cellphones, who are not holding the receiver
    to their ear while entering DTMF.
    NOTE: Only one of the <f>, <l>, or <b> options may be specified.
    *If more than one is specified*, then Directory will act as  if <b> was
    specified.  The number of characters for the user to type defaults to
    '3'.
```

### Lab: Using the directory application

1. voicemail.conf फ़ाइल को संपादित करें और डायल प्लान में दो एक्सटेंशन जोड़ें

```
[default]
; Define maximum number of messages per folder for a particular context.
;maxmsg=50
4400=>4400,Clint Eastwood,ceastwood@voip.school
4401=>4401,John Wayne,jwayne@voip.school
```

2. इन एक्सटेंशन को अपने डायल प्लान में बनाएं

```
exten=9006,1,VoiceMailMain()
exten=9006,n,Hangup()
exten=9007,1,Directory(default,default)
exten=9007,n,Hangup()
```

3. कंसोल पर जाएँ और रीलोड करें  
4. 9006 डायल करें और प्रत्येक एक्सटेंशन (4400, 4401) के लिए एक नाम रिकॉर्ड करें  
5. 9007 डायल करें और एक एक्सटेंशन के लिए अंतिम नाम के तीन अक्षर चुनें (Eas=327)। यदि यह सही विकल्प है, तो नाम पर ट्रांसफ़र करने के लिए ‘1’ दबाएँ।

## Lab: Putting it all together

Thus far, you have learned several dial plan concepts. Let’s put all the applications, functions, and concepts in a dial plan example so you can understand how they are used together. Let’s guide you through the whole PBX configuration for the scenario below.

- 4 analog trunks
- 16 SIP-based extensions
- 3 service classes:
    - restrict (internal, local, and 1-800)
    - ld (long distance)
    - ldi (international)
- After-hours message
- Auto attendant

### Step 1 – Configuring channels

**Analog trunks (`chan_dahdi.conf`).** First, we will configure the analog trunks in the DAHDI channel configuration file `chan_dahdi.conf`. In this case, we will use a T400P Digium card with 4 FXO interfaces. Let’s assume that the driver is already loaded and the driver configuration file (/etc/dahdi/system.conf) is correctly configured.

![10-dialplan-advanced-features figure 16](../images/10-dialplan-advanced-features-img16.png)

```
signalling=fxs_ks
language=en
context=incoming
group=1
channel => 1-4
```

**SIP channels (`pjsip.conf`).** We have chosen the dial plan numbering from 2000 to 2099. Two codecs will be used: G.729 and G.711 ulaw. The first one will be used for phones using Asterisk over the Internet or WAN while the second one will be used for phones using the local network. In `pjsip.conf`, we will arbitrate which devices will belong to each class of service (restrict, ld, ldi). To reduce the vulnerability to brute force attacks, we will use the phone’s MAC addresses as device names. I strongly advise that you use strong passwords to avoid brute force attacks!

We define a transport and three reusable templates — an endpoint base with the
shared codecs, a digest auth, and a single-contact AOR — then attach each device
to the templates and override only what differs (its class-of-service context and
credentials). `host=dynamic` becomes an AOR that the phone registers against, and
`directmedia` becomes `direct_media`:

```ini
; pjsip.conf
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[auth-digest](!)
type=auth
auth_type=digest

[aor-single](!)
type=aor
max_contacts=1

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
[00001A000002](auth-digest)
username=00001A000002
password=#s2cr2t#
[00001A000002](aor-single)

[00001A000003](endpoint-base)
context=ld
dtmf_mode=rfc4733
auth=00001A000003
aors=00001A000003
mailboxes=20
[00001A000003](auth-digest)
username=00001A000003
password=#s3cr3t#
[00001A000003](aor-single)

[00001A000004](endpoint-base)
context=ldi
dtmf_mode=rfc4733
auth=00001A000004
aors=00001A000004
mailboxes=20
[00001A000004](auth-digest)
username=00001A000004
password=#s3cr3t#
[00001A000004](aor-single)
```

### Step 2 – Configure the dial plan

Now let’s start to configure the extensions.conf. Define internal extensions and local dialing

```
[restrict]
exten=>_2000,1,Dial(PJSIP/00001A000002,20,t)
exten=>_2030,1,Dial(PJSIP/00001A000003,20,t)
exten=>_2040,1,Dial(PJSIP/00001A000004,20,t)
exten=>_9XXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20) ; local calls
exten=>_91800.,1,Dial(DAHDI/g1/${EXTEN:1},20); 1-800
```

Define LD (long distance)

```
[ld]
Include=>restrict
exten=>_9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

Define international calls

```
[ldi]
include=>ld
exten=>_901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

### Step 3 - Receiving calls using an auto-attendant

To receive calls, use two contexts. The first one is for normal-hours operation, where the call will be received by an auto-attendant. The second one is for after hours, where the caller will receive a message such as “you have called company XYZ, our normal hours are from 08:00 AM to 06:00 PM; if you know the destination extension number you can try dialing it now or hang up.” Menus: Normal-hours, After-hours In the menus below, the system will play a message warning the caller that the company was reached after regular working hours, allowing the caller to dial the destination extension number (someone may be working after regular working hours).

```
[incoming]
include=>normalhours,08:00-18:00,mon-fri,*,*
include=>afterhours,18:00-23:59,*,*,*
include=>afterhours,00:00-07:59,*,*,*
include=>afterhours,*,sat-sun,*,*
[normalhours]
exten=>s,1,Goto(mainmenu,s,1)
[afterhours]
exten=>s,1,Background(afterhours)
exten=>s,2,hangup()
exten=>i,1,hangup()
exten=>t,1,hangup()
include=>restrict
```

Menus: Main and Sales During normal working hours, the call is answered by an auto-attendant menu, receiving a message such as “welcome to XYZ Company; dial 1 for sales, 2 for tech support, 3 for training, or the desired extension number”.

```
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035
TECHSUPPORT=PJSIP/2004
TRAINING=PJSIP/2036
[mainmenu]
exten=> s,1,Background(welcome)
exten=>1,1,Goto(sales,s,1)
exten=>2,1,Goto(techsupport,s,1)
exten=>3,1,Goto(training,s,1)
exten=>i,1,Playback(Invalid)
exten=>i,2,hangup()
exten=>t,1,Dial(${OPERATOR},20,Tt)
include=>restrict
[sales]
exten=>s,1,Dial(${SALES},20,Tt)
[techsupport]
exten=>s,1,Dial(${TECHSUPPORT},20,Tt)
[training]
exten=>s,1,Dial(${TRAINING},20,Tt)
```

With all these statements, the functionality of your dialing plan is now ready. In the next section, we will demonstrate how to operate the PBX.

## सारांश

इस अध्याय में, आपने IVR या ऑटो-अटेंडेंट का उपयोग करके कॉल प्राप्त करने के तरीके सीखे हैं। आपने कॉन्टेक्स्ट इन्क्लूजन की अवधारणा का अध्ययन किया और कुछ उदाहरण लागू किए। दोहराव वाले टाइपिंग से बचने के लिए सबरूटीन का उपयोग किया गया, और Asterisk डेटाबेस (AstDB, Asterisk 22 में SQLite3 द्वारा समर्थित) का उपयोग उन कार्यों के लिए किया गया जिन्हें डेटा स्टोरेज की आवश्यकता होती है (जैसे, कॉल फ़ॉरवर्ड, डू नॉट डिस्ट्रब, ब्लैकलिस्ट)। अंत में, आपने आफ्टर-ऑवर्स व्यवहार को लागू करना सीखा और इन अवधारणाओं का उपयोग करके एक पूर्ण डायल प्लान लागू किया।

## Quiz

1. A time-dependent context include uses the form `include => context,<times>,<weekdays>,<mdays>,<months>`. What does `include => normalhours,08:00-18:00,mon-fri,*,*` do?
   - A. Execute the extensions Monday to Friday, 08:00 to 18:00
   - B. Execute the options every day in all months
   - C. Nothing; the format is invalid
2. In modern Asterisk (including Asterisk 22), the fields of a time-based `include =>` and of `GotoIfTime()` are separated by which character?
   - A. The pipe `|`
   - B. The comma `,`
   - C. The semicolon `;`
   - D. The slash `/`
3. To dial several channels at once (ringing them simultaneously), you separate them inside `Dial()` with the ___ character.
4. A voice menu that plays a prompt while waiting for the caller to dial an extension is usually created with the ___ application.
5. You can include the contents of another file inside `extensions.conf` using the ___ statement (note: this is different from the `include =>` context statement).
6. In Asterisk 22, the built-in AstDB database is backed by:
   - A. Berkeley DB v1
   - B. MySQL
   - C. SQLite3
   - D. PostgreSQL
7. When you use `Dial(type1/identifier1&type2/identifier2)`, Asterisk dials each channel in sequence, waiting 20 seconds between them.
   - A. False
   - B. True
8. With the Background() application, you must wait until the message finishes playing before you can press a DTMF digit to choose an option.
   - A. False
   - B. True
9. Given the syntax `Goto([[context,]extension,]priority)`, which of the following are valid invocations of the Goto() application? (mark all that apply)
   - A. Goto(context,extension)
   - B. Goto(context,extension,priority)
   - C. Goto(extension,priority)
   - D. Goto(priority)
10. To delete a single key from AstDB in the Asterisk 22 dial plan, you use:
    - A. The `DBdel()` application
    - B. The `DB_DELETE()` function
    - C. The `DBdeltree()` application
    - D. The `LookupBlacklist()` application

**Answers:** 1 — A · 2 — B · 3 — `&` · 4 — Background() · 5 — #include · 6 — C · 7 — A · 8 — A · 9 — B, C, D · 10 — B
