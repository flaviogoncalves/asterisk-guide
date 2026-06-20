# Call Queues

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## उद्देश्य

इस अध्याय के अंत तक, आपको सक्षम होना चाहिए:

- कॉल क्यूज़ का उपयोग क्यों और कैसे किया जाता है, इसे समझें
- कॉल क्यूज़ का मूल सिद्धांत समझें
- क्यू सिस्टम को स्थापित और कॉन्फ़िगर करें

## How queues work?

Call queues are not exactly a novelty. When you have a high inbound call flow, it is hard to distribute calls appropriately. Using a group strategy where the phone simultaneously rings on all agents does not seem to work, unless you have only a few agents. However, a call queue will only deliver calls to a single available agent each time and put the customer on hold with music when there are no agents available. The queue works by retaining the call while finding an unoccupied agent to answer the call. One of the biggest benefits of the queue is to avoid losing calls while providing the possibility to generate statistics.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

Usually, a call queue works like this:

- Agents log in to the queue.
- Incoming calls are queued.
- A queuing strategy to distribute the calls is used to send calls to agents.
- Music on hold is played while the caller waits.
- Announcements can be made to callers, notifying them of waiting time
- The call is answered by the agent and statistics are generated.

The main application for queues is customer service. When using queues, you avoid losing calls when your agents are busy. You can add new agents to the queue if you find that the number of callers in the queue is growing. Another advantage with queues is you can now have statistics like call abandon rate, average call duration, and call answering target. These statistics will help you determine how many agents to use to provide better service to your customer.

### ACD architecture

The ACD architecture is formed by queues and agents. One agent can be in two queues at the same time. A queue can have agents, channels, and agent groups.

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

Queues are defined in the queues.conf configuration file. Agents are attendants who log in and are members of queues. Agents are defined in the agents.conf file. The queue system has grown significantly over many releases, making the configuration file extensive. We will explain some of the major parameters. One general parameter worth highlighting is `autofill`:

```
autofill=yes
```

The old behavior for the queue was serial type. The queue waited for a call to be dispatched before sending the succeeding call to the next agent. If an agent takes 15 seconds to answer a call, the other calls in the queue had to wait until that call was answered. For high-volume queues, this behavior was inefficient. The new behavior autofill=yes does not wait until a call is answered, but rather works in parallel. You can record the calls in the queue using the option mixmonitor. In this mode, calls are recorded and mixed at the same time.

### Queue configuration file

Queues are configured in the queues.conf file. In the figure, you will find a working example of a queue.

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### Agents

You can configure your agents in the file agents.conf. Agents can log in from any extension to receive calls. You can dial an agent using:

```
Dial(agent/<name>)
```

#### Agent login

The login flow for Agent 300 works like this:

- The user dials an extension that runs the `AgentLogin()` application.
- `AgentLogin()` is executed and the agent is associated with the current channel.
- You can check the status of the agents using the command `agent show all`.

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

You can define the agents in the file agents.conf

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

Members are active channels responding to the queue. Members can be direct channels (PJSIP, DAHDI) or agents who log in before receiving calls.

### Strategies

Calls are distributed among members according to one of these strategies:

- ringall: Plays all channels available until someone answers.
- leastrecent: Distributes to the least recent member.
- fewestcalls: Distributes to the member with fewest calls.
- random: Ring random interface.
- wrandom: Ring random interface, but use the member’s penalty as a weight when calculating their metric.
- rrmemory: Uses round robin with memory; it remembers where it left off with the call in the last pass.
- rrordered: Same as rrmemory, except the queue member order from the config file is preserved.
- linear: Rings members in the order they are listed in queues.conf; for dynamic members, in the order they were added.

The older `roundrobin` strategy was deprecated back in Asterisk 1.4. It is no longer a documented strategy and should not be used: in Asterisk 22 the parser still accepts the word `roundrobin`, but only as a backward-compatibility alias that maps to `rrmemory`. Use `rrmemory` (or `rrordered`) explicitly instead. The list above is the set of documented strategies for the `strategy` option in the Asterisk 22 `queues.conf`.

## एजेंट्स

एजेंट्स को प्रॉक्सी चैनलों के रूप में लागू किया गया है। इन्हें क्यूज़ के भीतर उपयोग किया जा सकता है। एजेंट चैनलों का एक अन्य उपयोग एक्सटेंशन मोबिलिटी है। उपयोगकर्ता किसी भी फ़ोन का उपयोग करके लॉग इन कर सकता है और उसकी कॉल्स प्राप्त कर सकता है। यह उपयोगकर्ता को किसी भी कमरे में जाकर उसे ऑफिस बनाने की अनुमति देता है। आप डायल प्लान में `dial(agent/<name>)` का उपयोग करके एजेंट को डायल कर सकते हैं। आप एजेंट्स को `agents.conf` फ़ाइल में परिभाषित करते हैं।

![एजेंट मोबिलिटी: उपयोगकर्ता कोई भी फ़ोन उठाता है, लॉगिन एक्सटेंशन डायल करता है, और एजेंट नंबर तथा पासवर्ड पास करता है; एजेंटलॉगिन() सफल होने के बाद एजेंट (Agent 300) कॉल्स लेने के लिए तैयार हो जाता है, और आप CLI कमांड `agent show all` से स्थिति जांच सकते हैं](../images/14-queues-fig05.png)

### एजेंट ग्रुप्स

आप एजेंट ग्रुप्स का उपयोग करना चुन सकते हैं। यह फ़ंक्शन ACD रणनीतियों को ध्यान में नहीं रखता। आप संभवतः सभी एजेंट्स को व्यक्तिगत रूप से सूचीबद्ध करना पसंद करेंगे। यदि आप किसी एजेंट ग्रुप को ट्रांसफ़र करना चाहते हैं, तो आप `queues.conf` का उपयोग कर सकते हैं:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### एजेंट्स के लिए कॉन्फ़िगरेशन फ़ाइल

एजेंट्स को `agents.conf` फ़ाइल में परिभाषित किया जाता है। नीचे फ़ाइल का एक कार्यशील उदाहरण दिया गया है।

![agents.conf फ़ाइल का एक कार्यशील उदाहरण: एक सामान्य सेक्शन जिसमें `persistentagents` है, एक एजेंट्स सेक्शन जिसमें डिफ़ॉल्ट पैरामीटर (autologoff, ackcall, endcall, wrapuptime, musiconhold) हैं, और दो एजेंट परिभाषाएँ (300 और 301)](../images/14-queues-fig06.png)

## ACD-संबंधित अनुप्रयोग

Asterisk कतार प्रणाली डायल प्लान में कतारों को लागू करने के लिए कई अनुप्रयोग उपलब्ध कराती है। नीचे, हम उनमें से कुछ दिखाते हैं।

### अनुप्रयोग queue()

यह अनुप्रयोग आने वाली कॉलों को queues.conf में परिभाषित किसी विशेष कॉल कतार में रखता है। विकल्प स्ट्रिंग में शून्य या अधिक एक-अक्षर विकल्प हो सकते हैं (नीचे चित्र में दिखाए गए हैं)। कॉल को स्थानांतरित करने के अलावा, कॉल को पार्क किया जा सकता है और फिर किसी अन्य उपयोगकर्ता द्वारा उठाया जा सकता है। वैकल्पिक URL को कॉल किए गए पक्ष को भेजा जाएगा यदि चैनल इसका समर्थन करता है। वैकल्पिक AGI पैरामीटर कॉल करने वाले पक्ष के चैनल पर एक AGI स्क्रिप्ट सेट करेगा जो एक कतार सदस्य से जुड़ने के बाद निष्पादित होगी। टाइमआउट निर्दिष्ट सेकंडों की संख्या के बाद कतार को विफल कर देगा, प्रत्येक टाइमआउट और पुनः प्रयास चक्र के बीच जाँच किया जाता है। यह अनुप्रयोग पूर्ण होने पर QUEUE स्थिति चर सेट करता है:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### अनुप्रयोग agentlogin()

यह अनुप्रयोग एजेंट को सिस्टम में लॉग इन करने के लिए कहता है। यह हमेशा -1 लौटाता है। लॉग इन रहने पर, एजेंट को नई कॉल आने पर एक बीप सुनाई देगा। एजेंट * कुंजी दबाकर कॉल को समाप्त कर सकता है।

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### अनुप्रयोग addQueueMember()

यह अनुप्रयोग गतिशील रूप से किसी डिवाइस (जैसे, PJSIP/3000) को कतार में जोड़ता है। यदि डिवाइस पहले से मौजूद है, तो यह एक त्रुटि लौटाएगा।

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### अनुप्रयोग removeQueueMember()

यह अनुप्रयोग गतिशील रूप से किसी डिवाइस को कतार से हटाता है। यदि डिवाइस कतार का हिस्सा नहीं है, तो यह एक त्रुटि लौटाएगा।

```
RemoveQueueMember(queuename[|interface])
```

### समर्थन अनुप्रयोग और CLI कमांड

कुछ अनुप्रयोग और कंसोल कमांड कतारों के साथ काम करने में मदद कर सकते हैं। नीचे प्रत्येक अनुप्रयोग क्या करता है, इसका सारांश दिया गया है:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

नीचे दिया गया चित्र कार्यशील क्यू सिस्टम बनाने के प्रमुख कार्यों का सारांश प्रस्तुत करता है।

![The ACD configuration tasks: (1) create the call queue (required), (2) define agent parameters (optional), (3) create agents (optional), (4) put the queue in the dial plan (required), (5) configure agent recording (optional), and (6) verify with agent show all and queue show (optional)](../images/14-queues-fig10.png)

Step 1: Create the call queue In the file queues.conf:

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

Step 2: Define agent parameters In the file agents.conf:

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

Step 3: Create the agents In the file agents.conf:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Step 4: Insert the queue in the dial plan, in the file `extensions.conf`:

```
; Telemarketing queue.
exten=>_0800XXXXXXX,1,Answer
exten=>_0800XXXXXXX,2,Set(CHANNEL(musicclass)=default)
exten=>_0800XXXXXXX,3,Set(TIMEOUT(digit)=5)
exten=>_0800XXXXXXX,4,Set(TIMEOUT(response)=10)
exten=>_0800XXXXXXX,5,Background(welcome)
exten=>_0800XXXXXXX,6,Queue(telemarketing)
; Transfer to the queue auditing
exten => 8000,1,Queue(auditing)
exten => 8000,2,Playback(demo-echotest); No auditor available
exten => 8000,3,Goto(8000,1) ; Verify auditor again
; Agent login for the telemarketing and auditing queues
exten => 9000,1,Wait(1)
exten => 9000,2,AgentLogin()
```

### Configure queue recording

Calls may be recorded using Asterisk's MixMonitor application. (The standalone Monitor application was removed in Asterisk 22, and the queues.conf `monitor-type` option now accepts only MixMonitor.) Recording can be enabled from within the queue application, beginning when the call is actually picked up. Only successful calls are recorded, and no recordings are performed while people are listening to MOH. To enable monitoring, simply specify monitor-format. This feature is otherwise disabled. You can set the filename for the recording using `Set(MONITOR_FILENAME=<filename>)`; otherwise it will use `MONITOR_FILENAME=${UNIQUEID}`.

In the file queues.conf:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Queue operation

निम्नलिखित उदाहरण दर्शाते हैं कि कतार (queue) का उपयोग कैसे किया जाता है।

1. एजेंट लॉगिन। उदाहरण: टेलीमार्केटिंग कतार में एक एजेंट फोन उठाता है और #9000 डायल करता है। एजेंट को एक अमान्य लॉगिन संदेश सुनाई देता है और उसका/उसका नाम तथा पासवर्ड माँगा जाता है। ऑडिटिंग कतार भी वही प्रक्रिया अपनाती है।
2. कतार। एक बार कतार में प्रवेश करने पर, एजेंट को MOH सुनाई देगा, यदि परिभाषित हो। जब टेलीमार्केटिंग कतार में कॉल आती है, तो एजेंट को एक बीप सुनाई देगा और वह कॉल से जुड़ जाएगा।
3. कॉल समाप्ति। जब एजेंट कॉल समाप्त कर लेता है, तो वह/वह:
   - ‘*’ दबा कर डिस्कनेक्ट कर सकता है और कतार में बना रह सकता है।
   - फोन डिस्कनेक्ट कर सकता है, जिससे वह कतार से भी डिस्कनेक्ट हो जाएगा।
   - कॉल को ऑडिटिंग के लिए ट्रांसफ़र करने हेतु #8000 दबा सकता है।

## उन्नत संसाधन

Asterisk कतार प्रणाली में कुछ उन्नत सुविधाएँ हैं जो कुछ ग्राहकों और एजेंटों को प्राथमिकता देती हैं तथा उपयोगकर्ता मेनू को सक्षम करती हैं।

### उपयोगकर्ता मेनू

आप कतार में प्रतीक्षा करते समय एक-अंकीय एक्सटेंशन का उपयोग करके उपयोगकर्ता के लिए एक मेनू परिभाषित कर सकते हैं। इस विकल्प को सक्षम करने के लिए, कतार कॉन्फ़िगरेशन `queues.conf` में एक कॉन्टेक्स्ट परिभाषित करें।

### दंड (Penalty)

एजेंटों को दंड (penalty) के साथ कॉन्फ़िगर किया जा सकता है। एक कतार पहले उन उपयोगकर्ताओं को कॉल भेजेगी जिनका दंड मान कम हो। उदाहरण के लिए, चूँकि हमें पता है कि हमारे ग्राहक सुसान और उसकी मुलायम आवाज़ को पसंद करते हैं, हम उसे प्राथमिकता 0 असाइन कर सकते हैं। वैकल्पिक रूप से, उबर नामक एजेंट, जिसके पास कम अनुभव है, ग्राहक सेवा के लिए कम पसंद किया जाता है; इसलिए हम इस एजेंट को प्राथमिकता 10 असाइन करते हैं। फ़ाइल `queues.conf` में:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### प्राथमिकता (Priority)

कतारें FIFO (first in first out) मोड में कार्य करती हैं। यदि आप विशेष ग्राहकों (प्लैटिनम, गोल्ड) को प्राथमिकता देना चाहते हैं तो आप विभेदित प्राथमिकताएँ सेट कर सकते हैं। प्लैटिनम या गोल्ड ग्राहकों के लिए:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

नीले ग्राहकों के लिए:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## एप्लिकेशन agentcallbacklogin() हटाया गया है

एप्लिकेशन `agentcallbacklogin()` को Digium ने Asterisk 1.4 (जुलाई 2006) में अप्रचलित कर दिया था और यह अब Asterisk 22 में उपलब्ध नहीं है। अनुशंसित तरीका है कि PJSIP इंटरफ़ेस के साथ `AddQueueMember()` का उपयोग करके कॉलबैक‑स्टाइल मेंबर को डायनामिक रूप से क्यू में जोड़ा जाए। दस्तावेज़ `queues-with-callback-members.txt` को पुराने Asterisk `/doc` निर्देशिकाओं में माइग्रेशन गाइडेंस के लिए शामिल किया गया था।

पुराना `chan_agent` चैनल ड्राइवर भी हटा दिया गया; इसकी कार्यक्षमता को `app_agent_pool` मॉड्यूल के रूप में पुनः लिखा गया, जो Asterisk 22 में `AgentLogin()`, `AgentRequest()` और `AGENT()` डायलप्लान फ़ंक्शन प्रदान करता है (ये अभी भी मौजूद हैं — `app_agent_pool.so` एक स्टॉक 22 बिल्ड के साथ आता है)। आधुनिक कॉल सेंटर के लिए, हालांकि, मानक पैटर्न यह है कि एजेंट चैनलों को पूरी तरह छोड़ दिया जाए और एजेंट के PJSIP डिवाइस को सीधे `AddQueueMember()`/`RemoveQueueMember()` के साथ क्यू में जोड़ा जाए (स्थैतिक रूप से `queues.conf` में, या डायलप्लान या AMI से डायनामिक रूप से)। यह सरल है, PJSIP डिवाइस स्थिति के साथ साफ़ एकीकरण करता है, और इस अध्याय में पूरे उपयोग किया गया तरीका है।

## Queue statistics

All events from queues are logged to /var/log/asterisk/queue_log. The format of the queue log is published in the document queuelog.txt in the /doc directory of the Asterisk documentation. Below are some of the most important events logged.

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

You can build your own utility to process these events or use a ready-to-run statistics package:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – a commercial, actively maintained package that parses `queue_log` and remains one of the most complete reporting tools for Asterisk call centers.
- **Roll your own** – because the `queue_log` format above is stable and well documented, it is straightforward to parse it with a small script (Python, etc.) and feed the events into a database or dashboard.

For a more event-driven approach than tailing `queue_log`, the **Asterisk REST Interface (ARI)** and the **AMI** `QueueSummary`/`QueueStatus` actions let you build live queue dashboards and custom integrations against real-time queue state rather than after-the-fact log parsing. ARI is the modern, supported integration surface for this kind of work in Asterisk 22.

## सारांश

इस अध्याय में आपने ACD का उपयोग कैसे करें, उसकी संरचना, और इसे कैसे कॉन्फ़िगर करें, सीखा है। प्राथमिकताओं और दंड जैसी कुछ उन्नत सुविधाएँ भी प्रस्तुत की गई थीं।

## Quiz

1. Which of the following are valid queue distribution strategies in `queues.conf` (choose all that apply)?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. You can record a conversation between an agent and a customer from within the queue by setting the ___ option in the `queues.conf` file.
3. Which `strategy` rings members in the exact order they are listed in `queues.conf`?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. When the agent finishes a call in the telemarketing example, which actions can they take (choose all that apply)?
   - A. Press `*` to disconnect and stay in the queue
   - B. Hang up the phone and disconnect from the queue
   - C. Press `#8000` to transfer the call for auditing
   - D. Press `#` to log off all queues immediately
5. Which two tasks are *required* to get a working queue (choose all that apply)?
   - A. Create the queue
   - B. Create the agents
   - C. Configure agent parameters
   - D. Configure recording
   - E. Put the queue in the dial plan
6. In a call queue you can offer a single-digit menu the caller can dial while waiting. This is enabled by defining a(n) ___ in the queue's `queues.conf` section:
   - A. agent
   - B. menu
   - C. context
   - D. application
7. The support applications `AddQueueMember()` and `RemoveQueueMember()` are used in the ___ to add or remove members at runtime:
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Since chan_sip was removed in Asterisk 21, a static queue member must reference a channel such as ___ rather than `SIP/1001`.
9. The `wrapuptime` parameter is the minimum time after an agent disconnects a call before the queue will send that agent a new call.
   - A. True
   - B. False
10. A caller can be given a higher position in the same queue by setting the `QUEUE_PRIO` channel variable before calling `Queue()`.
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin is not a documented strategy; in Asterisk 22 it survives only as a deprecated alias for rrmemory) · 2 — `monitor-format` (recording from the queue is enabled by specifying `monitor-format`; in Asterisk 22 `monitor-type` only supports MixMonitor) · 3 — C (linear) · 4 — A, B, C (`*` disconnects and stays; `#` is not a log-off-all key) · 5 — A, E · 6 — C (the `context` option) · 7 — A (the dial plan) · 8 — `PJSIP/1001` (any `PJSIP/` interface) · 9 — True · 10 — True
