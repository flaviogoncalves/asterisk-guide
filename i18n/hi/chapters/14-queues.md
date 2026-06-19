# Call Queues

Call queues, जिन्हें ACD (Automatic Call Distribution) के रूप में भी जाना जाता है, ग्राहकों की कॉल्स का कुशलतापूर्वक उत्तर देने के लिए तेजी से महत्वपूर्ण होते जा रहे हैं। एक automatic call distributor लागत कम करने, सेवा बढ़ाने और बिक्री में सुधार करने में मदद कर सकता है क्योंकि call distributors इस बात को प्रभावित करते हैं कि आपका व्यवसाय कैसे काम करता है—कुछ दिनों के लिए नहीं, बल्कि कई वर्षों के लिए। एक call center के वातावरण में, सबसे महत्वपूर्ण कारक लोग हैं; वे सबसे महंगे संसाधन हैं। एजेंटों को काम पर रखने, प्रशिक्षित करने और प्रेरित करने में समय, पैसा और धैर्य लगता है। एक ACD के साथ, आप एजेंटों की आवश्यक संख्या का सटीक निर्धारण करके, अच्छे और बुरे अटेंडेंट्स को नियंत्रित करके और call flow का विश्लेषण करके एजेंटों की उत्पादकता को अधिकतम कर सकते हैं।

## Objectives

इस अध्याय के अंत तक, आप निम्नलिखित में सक्षम होंगे:

- यह समझना कि call queues का उपयोग क्यों और कैसे करें
- call queues के मूल सिद्धांत को समझना
- queue system को इंस्टॉल और कॉन्फ़िगर करना

## How queues work?

Call queues कोई नई बात नहीं हैं। जब आपके पास अधिक inbound call flow होता है, तो कॉल्स को उचित रूप से वितरित करना कठिन होता है। एक group strategy का उपयोग करना जहाँ फोन सभी एजेंटों पर एक साथ बजता है, तब तक काम नहीं करता जब तक कि आपके पास केवल कुछ ही एजेंट न हों। हालाँकि, एक call queue हर बार केवल एक उपलब्ध एजेंट को कॉल डिलीवर करेगी और जब कोई एजेंट उपलब्ध नहीं होगा तो ग्राहक को music on hold पर रखेगी। Queue कॉल को तब तक बनाए रखकर काम करती है जब तक कि कॉल का उत्तर देने के लिए कोई खाली एजेंट न मिल जाए। Queue का सबसे बड़ा लाभ कॉल्स को खोने से बचना है, साथ ही सांख्यिकी (statistics) उत्पन्न करने की संभावना प्रदान करना है।

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

आमतौर पर, एक call queue इस तरह काम करती है:

- एजेंट queue में लॉग इन करते हैं।
- आने वाली कॉल्स को queue में रखा जाता है।
- कॉल्स को एजेंटों तक भेजने के लिए कॉल्स वितरित करने वाली एक queuing strategy का उपयोग किया जाता है।
- कॉलर के प्रतीक्षा करने के दौरान music on hold बजाया जाता है।
- कॉलर्स को प्रतीक्षा समय की सूचना देने के लिए घोषणाएं (announcements) की जा सकती हैं।
- एजेंट द्वारा कॉल का उत्तर दिया जाता है और सांख्यिकी उत्पन्न की जाती है।

Queues के लिए मुख्य एप्लिकेशन ग्राहक सेवा है। Queues का उपयोग करते समय, आप अपने एजेंटों के व्यस्त होने पर कॉल्स खोने से बचते हैं। यदि आप पाते हैं कि queue में कॉलर्स की संख्या बढ़ रही है, तो आप queue में नए एजेंट जोड़ सकते हैं। Queues के साथ एक और लाभ यह है कि अब आप call abandon rate, average call duration, और call answering target जैसी सांख्यिकी प्राप्त कर सकते हैं। ये सांख्यिकी आपको यह निर्धारित करने में मदद करेंगी कि अपने ग्राहकों को बेहतर सेवा प्रदान करने के लिए कितने एजेंटों का उपयोग करना है।

### ACD architecture

ACD architecture queues और एजेंटों द्वारा बनता है। एक एजेंट एक ही समय में दो queues में हो सकता है। एक queue में एजेंट, चैनल्स और एजेंट ग्रुप हो सकते हैं।

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Queues को queues.conf कॉन्फ़िगरेशन फ़ाइल में परिभाषित किया जाता है। एजेंट वे अटेंडेंट्स होते हैं जो लॉग इन करते हैं और queues के सदस्य होते हैं। एजेंटों को agents.conf फ़ाइल में परिभाषित किया जाता है। Queue system कई रिलीज़ में काफी विकसित हुआ है, जिससे कॉन्फ़िगरेशन फ़ाइल विस्तृत हो गई है। हम कुछ प्रमुख मापदंडों (parameters) की व्याख्या करेंगे। सामान्य मापदंड

```
autofill=yes
```

Queue के लिए पुराना व्यवहार serial type था। Queue अगले एजेंट को अगली कॉल भेजने से पहले कॉल के डिस्पैच होने का इंतजार करती थी। यदि किसी एजेंट को कॉल का उत्तर देने में 15 सेकंड लगते हैं, तो queue में अन्य कॉल्स को तब तक इंतजार करना पड़ता था जब तक कि उस कॉल का उत्तर न मिल जाए। उच्च-वॉल्यूम वाली queues के लिए, यह व्यवहार अक्षम था। नया व्यवहार autofill=yes कॉल का उत्तर मिलने तक इंतजार नहीं करता है, बल्कि समानांतर (parallel) में काम करता है। आप mixmonitor विकल्प का उपयोग करके queue में कॉल्स को रिकॉर्ड कर सकते हैं। इस मोड में, कॉल्स को एक ही समय में रिकॉर्ड और मिक्स किया जाता है।

### Queue configuration file

Queues को queues.conf फ़ाइल में कॉन्फ़िगर किया जाता है। चित्र में, आपको एक queue का कार्यशील उदाहरण मिलेगा।

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

आप अपने एजेंटों को agents.conf फ़ाइल में कॉन्फ़िगर कर सकते हैं। एजेंट कॉल्स प्राप्त करने के लिए किसी भी extension से लॉग इन कर सकते हैं। आप किसी एजेंट को डायल कर सकते हैं:

```
Dial(agent/<name>)
```

#### Agents

Agent 300

- आप `agent show all` कमांड का उपयोग करके एजेंटों की स्थिति की जांच कर सकते हैं।
- agentlogin कमांड निष्पादित की जाती है और एजेंट को वर्तमान चैनल के साथ जोड़ा जाता है।
- उपयोगकर्ता agentlogin एप्लिकेशन के साथ एक extension डायल करता है।

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

आप agents.conf फ़ाइल में एजेंटों को परिभाषित कर सकते हैं

```
; Agent configuration
[general]
persistentagents=yes
[agents]
autologoff=15
autologoffunavail=yes
ackcall=no
endcall=yes
wrapuptime=5000
musiconhold => default
;
;This section contains the agent definitions, in the form:
;
; agent => agentid,agentpassword,name
;
agent => 300,300
agent => 301,301
```

### Members

सदस्य (Members) वे सक्रिय चैनल्स हैं जो queue को प्रतिक्रिया देते हैं। सदस्य सीधे चैनल्स (PJSIP, DAHDI) या वे एजेंट हो सकते हैं जो कॉल्स प्राप्त करने से पहले लॉग इन करते हैं।


### Strategies

कॉल्स को इन रणनीतियों में से एक के अनुसार सदस्यों के बीच वितरित किया जाता है:

- ringall: सभी उपलब्ध चैनल्स को तब तक बजाता है जब तक कोई उत्तर न दे दे।
- leastrecent: सबसे कम हाल ही में उपयोग किए गए सदस्य को वितरित करता है।
- fewestcalls: सबसे कम कॉल्स वाले सदस्य को वितरित करता है।
- random: रैंडम इंटरफ़ेस को रिंग करता है।
- wrandom: रैंडम इंटरफ़ेस को रिंग करता है, लेकिन अपनी मीट्रिक की गणना करते समय सदस्य की पेनल्टी को भार (weight) के रूप में उपयोग करता है।
- rrmemory: round robin with memory का उपयोग करता है; यह याद रखता है कि पिछली बार कॉल के साथ यह कहाँ रुका था।
- rrordered: rrmemory के समान, सिवाय इसके कि कॉन्फ़िगरेशन फ़ाइल से queue सदस्य का क्रम संरक्षित रहता है।
- linear: सदस्यों को उस क्रम में रिंग करता है जिस क्रम में वे queues.conf में सूचीबद्ध हैं; डायनामिक सदस्यों के लिए, उस क्रम में जिसमें उन्हें जोड़ा गया था।

पुरानी `roundrobin` रणनीति को Asterisk 1.4 में हटा दिया गया था; यह अब Asterisk 22 में मौजूद नहीं है। इसके बजाय `rrmemory` (या `rrordered`) का उपयोग करें। उपरोक्त रणनीतियाँ Asterisk 22 `queues.conf` में `strategy` विकल्प द्वारा स्वीकार किया गया पूरा सेट हैं।

## Agents

एजेंटों को प्रॉक्सी चैनल्स के रूप में लागू किया जाता है। उनका उपयोग queues के अंदर किया जा सकता है। एजेंट चैनल्स का एक और उपयोग extension mobility है। उपयोगकर्ता किसी भी फोन का उपयोग करके लॉग इन कर सकता है और अपनी कॉल्स प्राप्त कर सकता है। यह उपयोगकर्ता को किसी भी कमरे में जाकर उसे अपना कार्यालय बनाने की अनुमति देता है। आप dialplan में dial(agent/<name>) का उपयोग करके किसी एजेंट को डायल कर सकते हैं। आप agents.conf फ़ाइल में एजेंटों को परिभाषित करते हैं।

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

आप एजेंट समूहों का उपयोग करना चुन सकते हैं। यह फ़ंक्शन ACD रणनीतियों को ध्यान में नहीं रखता है। आप शायद सभी एजेंटों को व्यक्तिगत रूप से सूचीबद्ध करना पसंद करेंगे। यदि आप किसी एजेंट समूह में ट्रांसफर करना चाहते हैं, तो आप

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### The configuration file for agents

एजेंटों को agents.conf फ़ाइल में परिभाषित किया जाता है। नीचे फ़ाइल का एक कार्यशील उदाहरण दिया गया है।

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## ACD-related applications

Asterisk queue system dialplan में queues को लागू करने के लिए कई एप्लिकेशन उपलब्ध कराता है। नीचे, हम उनमें से कुछ दिखाते हैं।

### The application queue()

यह एप्लिकेशन आने वाली कॉल्स को queues.conf में परिभाषित एक विशिष्ट call queue में डालता है। विकल्प स्ट्रिंग में निम्नलिखित में से शून्य या अधिक वर्ण हो सकते हैं: कॉल ट्रांसफर करने के अलावा, एक कॉल को पार्क किया जा सकता है और फिर किसी अन्य उपयोगकर्ता द्वारा उठाया जा सकता है। यदि चैनल इसका समर्थन करता है तो वैकल्पिक URL को कॉल किए गए पक्ष को भेजा जाएगा। वैकल्पिक AGI पैरामीटर एक AGI स्क्रिप्ट को सेटअप करेगा जिसे कॉल करने वाले पक्ष के चैनल पर निष्पादित किया जाएगा, एक बार जब वे queue सदस्य से जुड़ जाते हैं। टाइमआउट के कारण queue एक निर्दिष्ट सेकंड के बाद विफल हो जाएगी, जिसे प्रत्येक टाइमआउट और पुनः प्रयास चक्र के बीच जांचा जाता है। यह एप्लिकेशन पूरा होने पर QUEUE स्थिति चर सेट करता है:

![The queue() application: its syntax `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### The application agentlogin()

यह एप्लिकेशन एजेंट को सिस्टम में लॉग इन करने के लिए कहता है। यह हमेशा -1 लौटाता है। लॉग इन रहने के दौरान, कॉल प्राप्त करने वाला एजेंट नई कॉल आने पर बीप की आवाज सुनेगा। एजेंट * कुंजी दबाकर कॉल को डंप कर सकता है।

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### The application addQueueMember()

यह एप्लिकेशन डायनामिक रूप से एक डिवाइस (जैसे, PJSIP/3000) को queue में जोड़ता है। यदि डिवाइस पहले से मौजूद है, तो यह एक त्रुटि लौटाएगा।

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### The application removeQueueMember()

यह एप्लिकेशन डायनामिक रूप से queue से एक डिवाइस को हटाता है। यदि डिवाइस queue से संबंधित नहीं है, तो यह एक त्रुटि लौटाएगा।

```
RemoveQueueMember(queuename[|interface])
```

### Support applications and CLI commands

कुछ एप्लिकेशन और कंसोल कमांड queues के साथ काम करने में मदद करने में सक्षम हैं। निम्नलिखित रूपरेखा बताती है कि प्रत्येक एप्लिकेशन क्या करता है:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

नीचे दिया गया चित्र एक कार्यशील queue system बनाने के लिए प्रमुख कार्यों का सारांश देता है।

![The ACD configuration tasks: (1) create the call queue (required), (2) define agent parameters (optional), (3) create agents (optional), (4) put the queue in the dial plan (required), (5) configure agent recording (optional), and (6) verify with agent show all and queue show (optional)](../images/14-queues-fig10.png)

चरण 1: Call queue बनाएँ queues.conf फ़ाइल में:

```
[telemarketing]
music = default
;announce = queue-telemarketing
;context = qoutcon
timeout = 2
retry = 2
maxlen = 0
member => Agent/300
member => Agent/301
[auditing]
music = default
;announce = queue-auditing
;context = qoutcon
timeout = 15
retry = 5
maxlen = 0
member => Agent/600
member => Agent/601
```

चरण 2: एजेंट मापदंडों को परिभाषित करें agents.conf फ़ाइल में:

```
debian:/etc/asterisk# cat agents.conf
;
; Agent configuration
;
[agents]
; Define maxlogintries to allow agent to try max logins before
; failed.
; default to 3
maxlogintries=5
; Define autologoff times if appropriate.  This is how long
; the phone has to ring with no answer before the agent is
; automatically logged off (in seconds)
autologoff=15
; Define autologoffunavail to have agents automatically logged
; out when the extension that they are at returns a CHANUNAVAIL
; status when a call is attempted to be sent there.
; Default is "no".
;autologoffunavail=yes
; Define ackcall to require an acknowledgement by '#' when
; an agent logs in using agentcallbacklogin.  Default is "no".
;ackcall=no
; Define endcall to allow an agent to hangup a call by '*'.
; Default is "yes". Set this to "no" to ignore '*'.
;endcall=yes
; Define wrapuptime.  This is the minimum amount of time when
; after disconnecting before the caller can receive a new call
; note this is in milliseconds.
;wrapuptime=5000
; Define the default musiconhold for agents
; musiconhold => music_class
;musiconhold => default
;
; Define the default good bye sound file for agents
; default to vm-goodbye
;agentgoodbye => goodbye_file
; Define updatecdr. This is whether or not to change the source
; channel in the CDR record for this call to agent/agent_id so
; that we know which agent generates the call
;updatecdr=no
;
; Group memberships for agents (may change in mid-file)
;
;group=3
;group=1,2
;group=
```

चरण 3: एजेंट बनाएँ agents.conf फ़ाइल में:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

चरण 4: Dialplan में queue डालें

```
In the file extensions.conf:
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue,(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configure queue recording

कॉल्स को Asterisk के MixMonitor एप्लिकेशन का उपयोग करके रिकॉर्ड किया जा सकता है। (स्टैंडअलोन Monitor एप्लिकेशन को Asterisk 22 में हटा दिया गया था, और queues.conf `monitor-type` विकल्प अब केवल MixMonitor स्वीकार करता है।) रिकॉर्डिंग को queue एप्लिकेशन के भीतर से सक्षम किया जा सकता है, जो कॉल के वास्तव में उठाए जाने पर शुरू होती है। केवल सफल कॉल्स रिकॉर्ड की जाती हैं, और जब लोग MOH सुन रहे होते हैं तो कोई रिकॉर्डिंग नहीं की जाती है। मॉनिटरिंग सक्षम करने के लिए, बस monitor-format निर्दिष्ट करें। यह सुविधा अन्यथा अक्षम है। आप Set (MONITOR_FILENAME=<filename>) का उपयोग करके रिकॉर्डिंग के लिए फ़ाइल नाम सेट कर सकते हैं; अन्यथा

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

queues.conf फ़ाइल में:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Queue operation

निम्नलिखित उदाहरण बताते हैं कि queue का उपयोग कैसे करें। चरण 1: एजेंट लॉगिन उदाहरण: टेलीमार्केटिंग queue में एक एजेंट फोन उठाता है और #9000 डायल करता है। एजेंट एक अमान्य लॉगिन संदेश सुनता है और उससे उसका नाम और पासवर्ड मांगा जाता है। ऑडिटिंग queue भी इसी प्रक्रिया का पालन करती है। चरण 2: Queue एक बार queue में, एजेंट MOH सुनेगा, यदि परिभाषित है। जब टेलीमार्केटिंग queue में कोई कॉल आती है, तो एजेंट एक बीप सुनेगा और उस कॉल से जुड़ जाएगा। चरण 3: कॉल समाप्त करना जब एजेंट कॉल समाप्त करता है, तो वह:

- डिस्कनेक्ट करने और queue में बने रहने के लिए '*' दबा सकता है।
- फोन डिस्कनेक्ट कर सकता है, जिससे queue से डिस्कनेक्ट हो जाएगा।
- ऑडिटिंग के लिए कॉल ट्रांसफर करने के लिए #8000 दबा सकता है।

## Advanced resources

Asterisk queue system में कुछ ग्राहकों और एजेंटों को प्राथमिकता देने के साथ-साथ उपयोगकर्ता मेनू सक्षम करने के लिए कुछ उन्नत सुविधाएँ हैं।

### User menu

आप queue में प्रतीक्षा करते समय एक-अंकीय extensions का उपयोग करके उपयोगकर्ता के लिए एक मेनू परिभाषित कर सकते हैं। इस विकल्प को सक्षम करने के लिए, queue कॉन्फ़िगरेशन queues.conf में एक context परिभाषित करें।

### Penalty

एजेंटों को पेनल्टी के साथ कॉन्फ़िगर किया जा सकता है। एक queue कॉल्स को पहले कम पेनल्टी मान वाले उपयोगकर्ताओं को भेजेगी। उदाहरण के लिए, चूंकि हम जानते हैं कि हमारे ग्राहक सुसान और उसकी मधुर आवाज को पसंद करते हैं, इसलिए हम उसे प्राथमिकता 0 देना चुन सकते हैं। वैकल्पिक रूप से, उबर नाम का एजेंट, जिसके पास कम अनुभव है, ग्राहक सेवा के लिए कम पसंद किया जाता है; इसलिए, हम इस एजेंट को प्राथमिकता 10 देते हैं। queues.conf फ़ाइल में:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority

Queues FIFO (first in first out) मोड में काम करती हैं। यदि आप विशेष ग्राहकों (प्लैटिनम, गोल्ड) को प्राथमिकता देना चाहते हैं तो आप विभेदित प्राथमिकताएं सेट कर सकते हैं। प्लैटिनम या गोल्ड ग्राहकों के लिए:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

ब्लू ग्राहक:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

एप्लिकेशन `agentcallbacklogin()` को Digium द्वारा Asterisk 1.4 (जुलाई 2006) में हटा दिया गया था और यह अब Asterisk 22 में उपलब्ध नहीं है। अनुशंसित दृष्टिकोण एक PJSIP इंटरफ़ेस के साथ `AddQueueMember()` का उपयोग करना है ताकि queue में डायनामिक रूप से callback-style सदस्यों को जोड़ा जा सके। माइग्रेशन मार्गदर्शन के लिए पुराने Asterisk `/doc` निर्देशिकाओं में `queues-with-callback-members.txt` दस्तावेज़ शामिल किया गया था।

पुराने `chan_agent` चैनल ड्राइवर को भी हटा दिया गया था; इसकी कार्यक्षमता को `app_agent_pool` मॉड्यूल के रूप में फिर से लिखा गया था, जो Asterisk 22 में `AgentLogin()`, `AgentRequest()` और `AGENT()` dialplan फ़ंक्शन प्रदान करता है (ये अभी भी मौजूद हैं — `app_agent_pool.so` स्टॉक 22 बिल्ड के साथ आता है)। आधुनिक call centers के लिए, हालांकि, मानक पैटर्न एजेंट चैनल्स को पूरी तरह से छोड़ना और एजेंट के PJSIP डिवाइस को सीधे `AddQueueMember()`/`RemoveQueueMember()` के साथ queue में जोड़ना है (statically `queues.conf` में, या dialplan या AMI से डायनामिक रूप से)। यह सरल है, PJSIP डिवाइस स्थिति के साथ स्पष्ट रूप से एकीकृत होता है, और यह वह दृष्टिकोण है जिसका उपयोग इस पूरे अध्याय में किया गया है।

## Queue statistics

Queues की सभी घटनाओं को /var/log/asterisk/queue_log में लॉग किया जाता है। Queue लॉग का प्रारूप Asterisk दस्तावेज़ीकरण की /doc निर्देशिका में queuelog.txt दस्तावेज़ में प्रकाशित किया गया है। नीचे लॉग की गई कुछ सबसे महत्वपूर्ण घटनाएँ दी गई हैं।

- ABANDON(position|origposition|waittime)
- AGENTDUMP
- AGENTLOGIN(channel)
- AGENTLOGOFF(channel|logintime)
- ATTENDEDTRANSFER(destexten|destcontext|holdtime|calltime|origposition)
- BLINDTRANSFER(extension|context|holdtime|calltime|origposition)
- COMPLETEAGENT(holdtime|calltime|origposition)
- COMPLETECALLER(holdtime|calltime|origposition)
- CONFIGRELOAD
- CONNECT(holdtime|bridgedchanneluniqueid)
- ENTERQUEUE(url|callerid)
- EXITEMPTY(position|origposition|waittime)
- EXITWITHKEY(key|position)
- EXITWITHTIMEOUT(position|origposition|waittime)
- QUEUESTART
- RINGNOANSWER(ringtime)
- SYSCOMPAT

आप इन घटनाओं को संसाधित करने के लिए अपनी खुद की उपयोगिता बना सकते हैं या उपयोग के लिए तैयार सांख्यिकी पैकेज का उपयोग कर सकते हैं:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – एक व्यावसायिक, सक्रिय रूप से बनाए रखा गया पैकेज जो `queue_log` को पार्स करता है और Asterisk call centers के लिए सबसे पूर्ण रिपोर्टिंग टूल में से एक बना हुआ है।
- **Roll your own** – क्योंकि उपरोक्त `queue_log` प्रारूप स्थिर और अच्छी तरह से प्रलेखित है, इसे एक छोटी स्क्रिप्ट (Python, आदि) के साथ पार्स करना और घटनाओं को डेटाबेस या डैशबोर्ड में फीड करना सीधा है।

`queue_log` को टेल करने की तुलना में अधिक event-driven दृष्टिकोण के लिए, **Asterisk REST Interface (ARI)** और **AMI** `QueueSummary`/`QueueStatus` क्रियाएं आपको बाद में लॉग पार्सिंग के बजाय वास्तविक समय की queue स्थिति के खिलाफ लाइव queue डैशबोर्ड और कस्टम एकीकरण बनाने देती हैं। ARI Asterisk 22 में इस तरह के काम के लिए आधुनिक, समर्थित एकीकरण सतह है।

## Summary

इस अध्याय में आपने सीखा है कि ACD का उपयोग कैसे करें, इसकी वास्तुकला क्या है, और इसे कैसे कॉन्फ़िगर करें। प्राथमिकताएं और पेनल्टी जैसी कुछ उन्नत सुविधाएँ भी प्रस्तुत की गईं।

## Quiz

1. `queues.conf` में कौन सी वैध queue वितरण रणनीतियाँ हैं (सभी लागू होने वाले चुनें)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. आप `queues.conf` फ़ाइल में ___ विकल्प सेट करके queue के भीतर से एक एजेंट और ग्राहक के बीच बातचीत को रिकॉर्ड कर सकते हैं।
3. कौन सा `strategy` सदस्यों को उसी क्रम में रिंग करता है जिस क्रम में वे `queues.conf` में सूचीबद्ध हैं?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. जब एजेंट टेलीमार्केटिंग उदाहरण में कॉल समाप्त करता है, तो वे कौन सी क्रियाएं कर सकते हैं (सभी लागू होने वाले चुनें)?
   - A. डिस्कनेक्ट करने और queue में बने रहने के लिए `*` दबाएं
   - B. फोन काटें और queue से डिस्कनेक्ट करें
   - C. ऑडिटिंग के लिए कॉल ट्रांसफर करने के लिए `#8000` दबाएं
   - D. सभी queues से तुरंत लॉग ऑफ करने के लिए `#` दबाएं
5. कार्यशील queue प्राप्त करने के लिए कौन से दो कार्य *आवश्यक* हैं (सभी लागू होने वाले चुनें)?
   - A. Queue बनाएँ
   - B. एजेंट बनाएँ
   - C. एजेंट मापदंडों को कॉन्फ़िगर करें
   - D. रिकॉर्डिंग कॉन्फ़िगर करें
   - E. Dialplan में queue डालें
6. एक call queue में आप एक-अंकीय मेनू प्रदान कर सकते हैं जिसे कॉलर प्रतीक्षा करते समय डायल कर सकता है। यह queue के `queues.conf` अनुभाग में एक ___ को परिभाषित करके सक्षम किया जाता है:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. सपोर्ट एप्लिकेशन `AddQueueMember()` और `RemoveQueueMember()` का उपयोग रनटाइम पर सदस्यों को जोड़ने या हटाने के लिए ___ में किया जाता है:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. चूंकि chan_sip को Asterisk 21 में हटा दिया गया था, इसलिए एक स्टेटिक queue सदस्य को `SIP/1001` के बजाय ___ जैसे चैनल को संदर्भित करना चाहिए।
9. `wrapuptime` पैरामीटर वह न्यूनतम समय है जिसके बाद एक एजेंट कॉल डिस्कनेक्ट करता है, इससे पहले कि queue उस एजेंट को नई कॉल भेजे।
   - A. True
   - B. False
10. `Queue()` को कॉल करने से पहले `QUEUE_PRIO` चैनल चर सेट करके एक कॉलर को उसी queue में उच्च स्थान दिया जा सकता है।
    - A. True
    - B. False

**उत्तर:** 1 — A, C, D, E, F (roundrobin को rrmemory द्वारा प्रतिस्थापित किया गया था और अब मौजूद नहीं है) · 2 — `monitor-format` (queue से रिकॉर्डिंग `monitor-format` निर्दिष्ट करके सक्षम की जाती है; `monitor-type` MixMonitor बनाम Monitor का चयन करता है) · 3 — C (linear) · 4 — A, B, C (`*` डिस्कनेक्ट करता है और बना रहता है; `#` लॉग-ऑफ-ऑल कुंजी नहीं है) · 5 — A, E · 6 — C (`context` विकल्प) · 7 — A (dial plan) · 8 — `PJSIP/1001` (कोई भी `PJSIP/` इंटरफ़ेस) · 9 — True · 10 — True
