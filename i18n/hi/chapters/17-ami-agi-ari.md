# Extending Asterisk with AMI and AGI

कई स्थितियों में, Asterisk की सुविधाओं को बाहरी अनुप्रयोगों के माध्यम से विस्तारित करना आवश्यक हो सकता है। इसे विस्तारित करने के कई विभिन्न तरीके हैं। इस अध्याय में, हम Asterisk को अन्य प्रणालियों के साथ एकीकृत करने के दो क्लासिक तरीकों को कवर करेंगे: AMI – Asterisk Manager Interface और AGI – Asterisk Gateway Interface। हम `asterisk –rx` कमांड और `system()` एप्लिकेशन को भी देखेंगे। यह चुनना कि आप Asterisk के साथ किस तरीके से एकीकृत करना चाहते हैं, अनुप्रयोग पर निर्भर करता है। AGI के लिए सबसे सामान्य अनुप्रयोग डेटाबेस से जुड़ा IVR है। AMI के लिए, डायलर सबसे लोकप्रिय एप्लिकेशन हैं। एक तीसरा, अधिक आधुनिक इंटरफ़ेस — ARI, Asterisk REST Interface — अगले अध्याय में अलग से कवर किया गया है।

## Objectives

By the end of this chapter, the reader should be able to:

- बाहरी प्रोग्रामों तक पहुँच विकल्पों का वर्णन करें
- asterisk –rx कमांड का उपयोग करके एक कंसोल कमांड चलाएँ
- डायलप्लान में बाहरी प्रोग्राम कॉल करने के लिए system() ऐप का उपयोग करें
- समझाएँ कि AMI क्या है और यह कैसे काम करता है
- manager.conf फ़ाइल को कॉन्फ़िगर करें और AMI को सक्षम करें
- एक PHP प्रोग्राम से AMI कमांड निष्पादित करें
- समझाएँ कि Asterisk manager proxy क्या है और यह कैसे काम करता है
- विभिन्न AGI Flavors (DeadAGI, AGI, EAGI, FastAGI) का वर्णन करें
- PHP से निर्मित एक सरल AGI प्रोग्राम चलाएँ

## Asterisk को विस्तारित करने के प्रमुख तरीके

Asterisk के पास बाहरी प्रोग्रामों के साथ इंटरफ़ेस करने के विभिन्न तरीके हैं। इस अध्याय में, हम कवर करेंगे:

- Linux कमांड लाइन और Asterisk कंसोल
- System() एप्लिकेशन
- AMI
- AGI

## Extending Asterisk with console CLI

एक एप्लिकेशन आसानी से Linux शेल से Asterisk को निम्नलिखित कमांड का उपयोग करके कॉल कर सकता है।

```
asterisk -rx <command>
```

उदाहरण:

```
asterisk -rx "stop now"
```

यहाँ तक कि आउटपुट वाले कमांड को भी कॉल किया जा सकता है:

```
asterisk:~# asterisk -rx "pjsip show endpoints"
Endpoint:  <Endpoint/CID.....................................>  <State.....>  <Channels.>
    I/OAuth:  <AuthId/UserName..............................>
         Aor:  <Aor............................................>  <MaxContact>
       Contact:  <Aor/ContactUri..........................> <Hash....> <Status> <RTT(ms)..>
   Transport:  <TransportId........>  <Type>  <cos>  <tos>  <BindAddress..................>
    Identify:  <Identify/Endpoint.........................................................>
         Match:  <criteria.........................>
     Channel:  <ChannelId......................................>  <State.....>  <Time.....>
       Exten: <DialedExten...........>  CLCID: <ConnectedLineCID.......>
=========================================================================================

 Endpoint:  4000                                                 Not in use    0 of inf
```

## System() एप्लिकेशन का उपयोग करके Asterisk का विस्तार

system() एप्लिकेशन Asterisk को बाहरी एप्लिकेशन को कॉल करने में सक्षम बनाता है।

```
asterisk*CLI> core show application System
  -= Info about application 'System' =-
[Synopsis]
Execute a system command
[Description]
  System(command): Executes a command  by  using  system(). If the command
fails, the console should report a fallthrough.
Result of execution is returned in the SYSTEMSTATUS channel variable:
   FAILURE      Could not execute the specified command
   SUCCESS      Specified command successfully executed
```

उदाहरण: यह एप्लिकेशन netbios WindowsPopup का उपयोग करके स्क्रीन‑पॉप करता है।

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## What is AMI?

AMI एक क्लाइंट प्रोग्राम को Asterisk इंस्टेंस से कनेक्ट करने और TCP कनेक्शन के माध्यम से कमांड भेजने या इवेंट पढ़ने की सुविधा देता है। सिस्टम इंटीग्रेटर्स को चैनल स्टेट्स को ट्रैक करने के लिए ये संसाधन उपयोगी लगेंगे। AMI एक सरल लाइन प्रोटोकॉल पर आधारित है जो TCP के ऊपर key:value जोड़े उपयोग करता है। Asterisk स्वयं इस इंटरफ़ेस पर बहुत अधिक कनेक्शन संभालने के लिए तैयार नहीं है। यदि आपके पास AMI पर बहुत सारे कनेक्शन हैं, तो Asterisk मैनेजर प्रॉक्सी का उपयोग करने पर विचार करें।

### What language to use for AMI

आजकल प्रोग्रामिंग भाषा चुनना कठिन हो सकता है। विकल्प बहुत अधिक हैं—Java, PHP, Perl, C, C#, Python, और कई अन्य। किसी भी ऐसी भाषा के साथ AMI का उपयोग संभव है जो सॉकेट या टेलनेट इंटरफ़ेस को सपोर्ट करती हो। हमने इस पुस्तक के लिए PHP को चुना है क्योंकि यह बहुत लोकप्रिय है।

### AMI protocol behavior

- Asterisk को कोई भी कमांड भेजने से पहले, आपको एक AMI सत्र स्थापित करना होगा
- क्लाइंट से भेजे जाने वाले पैकेट की पहली लाइन में कुंजी “Action” होगी
- Asterisk से आने वाले पैकेट की पहली लाइन में कुंजी “Response” या “Event” होगी
- प्रमाणीकरण के बाद पैकेट किसी भी दिशा में प्रेषित किए जा सकते हैं

### Packet types

पैकेट का प्रकार निम्नलिखित कुंजियों की उपस्थिति से निर्धारित होता है:

- Action: एक क्लाइंट द्वारा AMI से जुड़कर भेजा गया पैकेट जो किसी विशिष्ट कार्रवाई का अनुरोध करता है। क्लाइंट्स के लिए उपलब्ध कार्रवाइयों का एक सीमित सेट होता है। लोडेड मॉड्यूल इन कार्रवाइयों को निर्धारित करते हैं। पैकेट में कार्रवाई का नाम और उसके पैरामीटर होते हैं।
- Response: Asterisk द्वारा क्लाइंट द्वारा भेजी गई अंतिम कार्रवाई के जवाब में भेजा गया उत्तर।
- Event: Asterisk कोर या किसी मॉड्यूल द्वारा उत्पन्न इवेंट से संबंधित डेटा।

जब क्लाइंट Action प्रकार के पैकेट भेजता है, तो एक पैरामीटर जिसका नाम ActionID है, शामिल किया जाता है। चूँकि Asterisk से भेजे गए उत्तरों का क्रम पूर्वानुमानित नहीं किया जा सकता, ActionID का उपयोग कार्रवाइयों और उत्तरों को आपस में जोड़ने के लिए किया जाता है। Event पैकेट दो अलग-अलग संदर्भों में उपयोग किए जाते हैं। पहला, इवेंट क्लाइंट को Asterisk में हुए बदलावों के बारे में सूचित करते हैं (जैसे, नए बनाए गए चैनल, डिस्कनेक्ट हुए चैनल, या एजेंट्स का क्यू में लॉग इन/आउट होना)। दूसरा, इवेंट क्लाइंट की कार्रवाई के उत्तरों को ले जाने के लिए उपयोग किए जाते हैं।

## Configuring users and permissions

To access AMI, it is necessary to establish a TCP connection listening to a TCP port (usually 5038). You will need to configure the /etc/asterisk/manager.conf file to create a user account and permissions. There is a finite set of permissions: “read,” “write,” or both. These permissions are defined in the

```
manager.conf file.
[general]
enabled=yes
port=5038
bindaddr=127.0.0.1
[admin]
secret=senha
read=system,call,log,verbose,command,agent,user
write=system,call,log,verbose,command,agent,user
deny=0.0.0.0/0.0.0.0
permit=127.0.0.1/255.255.255.255
```

### Logging in to the AMI

To log in to and authenticate AMI, you will need to send an action packet of the login type with a username and account created in the manager.conf.

```
Action:login
Username:admin
Secret:password
```

Example: Logging in to AMI using php

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
?>
```

If you don’t need to receive the events, you can use “Events Off”.

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
fputs($socket, "Events: off\r\n\r\n");
?>
```

### Action packets

When you send an action packet to Asterisk, you can provide some extra keys (e.g., called number) by passing key:value pairs after the action. It is also possible to pass channel and global variables to the dial plan.

```
Action: <action type><CRLF>
<Key 1>: <Value 1><CRLF>
<Key 2>: <Value 2><CRLF>
Variable: <Variable 1>=<Value 1><CRLF>
Variable: <Variable 2>=<Value 2><CRLF>
...
<CRLF>
```

### Action commands

You can use the CLI instruction manager show commands to list the available actions. In Asterisk 22 the core set of commands includes (this list is representative; loaded modules add more):

```
Action Privilege Synopsis
  WaitEvent        <none>           Wait for an event to occur
  ModuleCheck      system,all       Check if module is loaded
  ModuleLoad       system,all       Module management
  CoreShowChannels system,reportin  List currently active channels
  Reload           system,config,a  Send a reload event
  CoreStatus       system,reportin  Show PBX core status variables
  CoreSettings     system,reportin  Show PBX core settings (version etc)
  VoicemailUsersL  call,reporting,  List All Voicemail User Information
  UserEvent        user,all         Send an arbitrary event
  SendText         call,all         Send text message to channel
  ListCommands     <none>           List available manager commands
  MailboxCount     call,reporting,  Check Mailbox Message Count
  MailboxStatus    call,reporting,  Check Mailbox
  AbsoluteTimeout  system,call,all  Set Absolute Timeout
  ExtensionState   call,reporting,  Check Extension Status
  Command          command,all      Execute Asterisk CLI Command
  Originate        originate,all    Originate Call
  Atxfer           call,all         Attended transfer
  Redirect         call,all         Redirect (transfer) a call
  ListCategories   config,all       List categories in configuration file
  CreateConfig     config,all       Creates an empty file in the configuration directory
  UpdateConfig     config,all       Update basic configuration
  GetConfigJSON    system,config,a  Retrieve configuration (JSON format)
  GetConfig        system,config,a  Retrieve configuration
  Getvar           call,reporting,  Gets a Channel Variable
  Setvar           call,all         Set Channel Variable
  Status           system,call,rep  Lists channel status
  Hangup           system,call,all  Hangup Channel
  Challenge        <none>           Generate Challenge for MD5 Auth
  Login            <none>           Login Manager
  Logoff           <none>           Logoff Manager
  Events           <none>           Control Event Flow
  Ping             <none>           Keepalive command
  DAHDIRestart     <none>           Fully Restart DAHDI channels (terminates calls)
  DAHDIShowChanne  <none>           Show status DAHDI channels
  DAHDIDNDoff      <none>           Toggle DAHDI channel Do Not Disturb status OFF
  DAHDIDNDon       <none>           Toggle DAHDI channel Do Not Disturb status ON
  DAHDIDialOffhoo  <none>           Dial over DAHDI channel while offhook
  DAHDIHangup      <none>           Hangup DAHDI Channel
  DAHDITransfer    <none>           Transfer DAHDI Channel
  IAXnetstats      system,reportin  Show IAX Netstats
  IAXpeerlist      system,reportin  List IAX Peers
  IAXpeers         system,reportin  List IAX Peers
  QueueRule        <none>           Queue Rules
  QueuePenalty     agent,all        Set the penalty for a queue member
  QueueLog         agent,all        Adds custom entry in queue_log
  QueuePause       agent,all        Makes a queue member temporarily unavailable
  QueueRemove      agent,all        Remove interface from queue.
  QueueAdd         agent,all        Add interface to queue.
  QueueSummary     <none>           Queue Summary
  QueueStatus      <none>           Queue Status
  Queues           <none>           Queues
  AgentLogoff      agent,all        Sets an agent as no longer logged in
  Agents           agent,all        Lists agents and their status
  PlayDTMF                        call,all         Play DTMF signal on a specific channel.
  PJSIPShowEndpoints              system,reportin  Lists PJSIP endpoints
  PJSIPShowEndpoint               system,reportin  Detail listing of an endpoint
  PJSIPQualify                    system,all       Qualify a chan_pjsip endpoint
  PJSIPShowRegistrationsOutbound  system,reportin  Lists outbound registrations
  PJSIPShowContacts               system,reportin  Lists PJSIP Contacts
```

```
  AGI              agi,all          Add an AGI command to execute by Async AGI
  MixMonitor       system,all       Record a call and mix the audio during recording
  StopMixMonitor   system,call,all  Stop recording a call through MixMonitor
  MixMonitorMute   system,call,all  Mute / unMute a Mixmonitor recording
  ShowDialPlan     config,reportin  List dialplan
  DBDelTree        system,all       Delete DB Tree
  DBDel            system,all       Delete DB Entry
  DBPut            system,all       Put DB Entry
  DBGet            system,reportin  Get DB Entry
  Bridge           call,all         Bridge two channels already in the PBX
  Park             call,all         Park a channel
  ParkedCalls      <none>           List parked calls
```

If you need to know specific command parameters, use the manager show command <command>. Example:

```
asterisk*CLI> manager show command Originate

  -= Info about Manager Command 'Originate' =-

[Synopsis]
Originate a call.

[Provided By]
builtin

[Since]
0.2.0

[Description]
Generates an outgoing call to a <Extension>/<Context>/<Priority> or
<Application>/<Data>

[Syntax]
Action: Originate
[ActionID:] <value>
Channel: <value>
[Exten:] <value>
[Context:] <value>
[Priority:] <value>
[Application:] <value>
[Data:] <value>
[Timeout:] <value>
[CallerID:] <value>
[Variable:] <value>
[Account:] <value>
[EarlyMedia:] <value>
[Async:] <value>
[Codecs:] <value>
[ChannelId:] <value>
[OtherChannelId:] <value>
[PreDialGoSub:] <value>

[Arguments]
Channel
    Channel name to call.
Exten
    Extension to use (requires 'Context' and 'Priority')
Context
    Context to use (requires 'Exten' and 'Priority')
Priority
    Priority to use (requires 'Exten' and 'Context')
Application
    Application to execute.
Data
    Data to use (requires 'Application').
Timeout
    How long to wait for call to be answered (in ms.).
CallerID
    Caller ID to be set on the outgoing channel.
Variable
    Channel variable to set, multiple Variable: headers are allowed.
Account
    Account code.
EarlyMedia
    Set to 'true' to force call bridge on early media.
Async
    Set to 'true' for fast origination.
Codecs
    Comma-separated list of codecs to use for this call.
ChannelId
    Channel UniqueId to be set on the channel.
OtherChannelId
    Channel UniqueId to be set on the second local channel.
PreDialGoSub
    Context,Extension,Priority to set options/headers needed before
    starting the outgoing extension.

[Privilege]
originate,all

[See Also]
OriginateResponse
```

### Event packets

Events are generated on the manager interface whenever something happens in Asterisk —
a channel is created or changes state, two channels are bridged or unbridged, a
registration changes, a queue member is added, and so on. Each event is a block of
`Key: value` lines beginning with an `Event:` header.

The exact set of events depends on the loaded modules and the Asterisk version, so rather
than reproduce a list that quickly goes stale, query the running server for the
authoritative set:

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

For example, call bridging is reported through the `BridgeCreate`, `BridgeEnter`,
`BridgeLeave`, and `BridgeDestroy` events (`BridgeEnter` is "Raised when a channel enters a
bridge"). The older `Link`/`Unlink` events were removed in Asterisk 12.

## Asterisk Gateway Interface

AGI एक गेटवे इंटरफ़ेस है Asterisk के लिए, जो वेब सर्वरों द्वारा उपयोग किए जाने वाले CGI के समान है। यह Perl, PHP, और Python जैसी उच्च‑स्तरीय भाषाओं का उपयोग करके Asterisk की कार्यक्षमता का विस्तार करने की अनुमति देता है। CGI का मुख्य अनुप्रयोग IVR निर्माण है। AGI के चार प्रकार हैं:

- Normal AGI, जो Asterisk के बॉक्स के भीतर एक प्रोग्राम को कॉल करता है।
- Fast AGI, जो TCP सॉकेट्स का उपयोग करके किसी अन्य सर्वर पर AGI को कॉल करता है।
- EAGI, जो AGI को साउंड चैनल तक पहुँच और नियंत्रण प्रदान करता है।
- DeadAGI, जो हैंगअप() के बाद भी चैनल तक पहुँच देता है। आमतौर पर ‘h’ एक्सटेंशन में कॉल किया जाता है। ध्यान दें कि Asterisk 22 में `DeadAGI` एप्लिकेशन को डिप्रिकेट किया गया है — नियमित `AGI` एप्लिकेशन एक हँग‑अप्ड चैनल का पता लगाता है और स्क्रिप्ट को “dead” मोड में स्वचालित रूप से चलाता है, इसलिए नए डायलप्लान को केवल `AGI()` को कॉल करना चाहिए।

Application format:

```
asterisk*CLI> core show application AGI
  -= Info about Application 'AGI' =-
[Synopsis]
Executes an AGI compliant application.
[Description]
Executes an Asterisk Gateway Interface compliant program on a channel. AGI
allows Asterisk to launch external programs written in any language to control
a telephony channel, play audio, read DTMF digits, etc. by communicating with
the AGI protocol.
The following variants of AGI exist, and are chosen based on the value passed
to <command>:
    AGI - The classic variant of AGI, this will launch the script specified by
    <command> as a new process. Communication with the script occurs on 'stdin'
    and 'stdout'.
    FastAGI - Connect Asterisk to a FastAGI server using a TCP connection. The
    URI to the FastAGI server should be given in the form
    '[scheme]://host.domain[:port][/script/name]', where <scheme> is either
    'agi' or 'hagi'.
    AsyncAGI - Use AMI to control the channel in AGI. AsyncAGI should be invoked
    by passing 'agi:async' to the <command> parameter.
This application sets the channel variable ${AGISTATUS} on completion, one of:
SUCCESS, FAILURE, NOTFOUND, HANGUP.
[Syntax]
AGI(command[,arg1[,arg2[,...]]])
Use the CLI command 'agi show commands' to list available agi commands
```

आप उपलब्ध AGI कमांड्स को कमांड `agi show commands` का उपयोग करके दिखा सकते हैं (नीचे दिया गया आउटपुट प्रतिनिधि है; Asterisk 22 कुछ अतिरिक्त कमांड जोड़ता है):

```
Dead                        Command   Description
   No                         answer   Answer channel
   No                 channel status   Returns status of the connected channel
  Yes                   database del   Removes database key/value
  Yes               database deltree   Removes database keytree/value
  Yes                   database get   Gets database value
  Yes                   database put   Adds/updates database value
  Yes                           exec   Executes a given Application
   No                       get data   Prompts for DTMF on a channel
  Yes              get full variable   Evaluates a channel expression
   No                     get option   Stream file, prompt for DTMF, with timeout
  Yes                   get variable   Gets a channel variable
   No                         hangup   Hangup the current channel
  Yes                           noop   Does nothing
   No                   receive char   Receives one character from channels supporting it
   No                   receive text   Receives text from channels supporting it
   No                    record file   Records to a given file
   No                      say alpha   Says a given character string
   No                     say digits   Says a given digit string
   No                     say number   Says a given number
   No                   say phonetic   Says a given character string with phonetics
   No                       say date   Says a given date
   No                       say time   Says a given time
   No                   say datetime   Says a given time as specfied by the format given
   No                     send image   Sends images to channels supporting it
   No                      send text   Sends text to channels supporting it
   No                 set autohangup   Autohangup channel in some time
   No                   set callerid   Sets callerid for the current channel
   No                    set context   Sets channel context
   No                  set extension   Changes channel extension
   No                      set music   Enable/Disable Music on hold generator
   No                   set priority   Set channel dialplan priority
  Yes                   set variable   Sets a channel variable
   No                    stream file   Sends audio file on channel
   No            control stream file   Sends audio file and allows the listener cont.the
stream
   No                       tdd mode   Toggles TDD mode (for the deaf)
  Yes                        verbose   Logs a message to the asterisk verbose log
   No                 wait for digit   Waits for a digit to be pressed
   No                  speech create   Creates a speech object
   No                     speech set   Sets a speech engine setting
  Yes                 speech destroy   Destroys a speech object
   No            speech load grammar   Loads a grammar
  Yes          speech unload grammar   Unloads a grammar
   No        speech activate grammar   Activates a grammar
   No      speech deactivate grammar   Deactivates a grammar
   No               speech recognize   Recognizes speech
   No                          gosub   Execute a dialplan subroutine
```

डिबग करने के लिए, `agi debug` का उपयोग करें।

### Using AGI

इस उदाहरण में, हम `php-cli` का उपयोग करेंगे, जो php का कमांड‑लाइन संस्करण है। यदि `php-cli` अभी तक स्थापित नहीं है तो इसे स्थापित करें। `php` AGI स्क्रिप्ट्स का उपयोग करने के लिए निम्न चरणों का पालन करें।

1. सभी AGI स्क्रिप्ट्स `/var/lib/asterisk/agi-bin` में स्थित हैं
2. निष्पादन की अनुमति देने के लिए अनुमतियों को बदलें।

```
chmod 755 *.php
```

3. शेल इंटरफ़ेस (php विशिष्ट). स्क्रिप्ट की पहली पंक्तियों को यह होना चाहिए:

```
#!/usr/bin/php -q
<?php
```

4. I/O चैनल खोलें:

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

5. Asterisk आउटपुट को प्रबंधित करें। Asterisk प्रत्येक बार AGI को कॉल किए जाने पर जानकारी सेट भेजता है।

```
agi_request:testephp
agi_channel: Dahdi/1-1
agi_language: en
agi_type: Dahdi
agi_callerid:
agi_dnid:
agi_context: default
agi_extension: 4000
agi_priority: 1
```

भेजी गई जानकारी सहेजें:

```
while (!feof($stdin)) {
  $temp = fgets($stdin);
  $temp = str_replace("\n","",$temp);
  $s = explode(":",$temp);
  $agi[$s[0]] = trim($s[1]);
  if (($temp == "") || ($temp == "\n")) {
    break;
  }
}
```

The previous script will create an array named $agi. Available options are:

- agi_request – AGI file name
- agi_channel – AGI originating channel
- agi_language – Language set
- agi_type – Channel type (e.g., SIP, DAHDI)
- agi_uniqueid – Unique identifier
- agi_callerid – CallerID (Ex. Flavio <8590>)
- agi_context – Originating context
- agi_extension – Called extensions
- agi_priority – Priority
- agi_accountcode – Originating account code

To call a variable named agi_extensions, use $agi[agi_extensions].

6. Use channel AGI. At this point, you can start talking to Asterisk. Use the fputs command to send commands to AGI. You can also use the echo command.

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

नोट्स क्वोट्स के उपयोग के बारे में:

- AGI कमांड विकल्प वैकल्पिक नहीं होते
- कुछ विकल्पों को क्वोट्स में बंद करना आवश्यक है <escape digits>
- कुछ विकल्पों को क्वोट्स में नहीं बंद करना चाहिए <digit string>
- कुछ विकल्प दोनों फॉर्मेट में उपयोग किए जा सकते हैं
- आप सिंगल क्वोट्स का उपयोग कर सकते हैं

Step 7 – पास वेरिएबल्स  
Channel वेरिएबल्स को AGI में सेट किया जा सकता है, लेकिन उन्हें AGI के अंदर उपयोग नहीं किया जा सकता। निम्नलिखित उदाहरण AGI के अंदर काम नहीं करता।

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

निम्नलिखित उदाहरण काम करता है:

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

चरण 8: Asterisk प्रतिक्रियाएँ  
Asterisk से प्रतिक्रियाओं को सत्यापित करने के लिए निम्नलिखित आवश्यक है:

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

Step 9: लॉक्ड (zombie) प्रक्रियाओं को समाप्त करें यदि आपका स्क्रिप्ट किसी कारणवश विफल हो जाता है, तो प्रक्रिया लटक जाएगी। फिर से परीक्षण करने से पहले killproc कमांड का उपयोग करके इसे साफ़ करें।

```
 #!/usr/bin/php -q
 <?php
 ob_implicit_flush(true);
 set_time_limit(6);
 $in = fopen("php://stdin","r");
 $stdlog = fopen("/var/log/asterisk/agi.log", "w");
 // Enable debug (more verbose)
 $debug = false;
 // Functions definition
 function read() {
   global $in, $debug, $stdlog;
   $input = str_replace("\n", "", fgets($in, 4096));
   if ($debug) fputs($stdlog, "read: $input\n");
   return $input;
 }
 function errlog($line) {
   global $err;
   echo "VERBOSE \"$line\"\n";
 }
 function write($line) {
   global $debug, $stdlog;
   if ($debug) fputs($stdlog, "write: $line\n");
   echo $line."\n";
 }
 // Put agi headers in the array
 while ($env=read()) {
   $s = split(": ",$env);
   $agi[str_replace("agi_","",$s[0])] = trim($s[1]);
   if (($env == "") || ($env == "\n")) {
     break;
   }
 }
 // main program
 echo "VERBOSE \"Start here!\" 2\n";
 read();
 errlog("Call from ".$agi['channel']." - Phone ringing ");
 read();
 write("SAY DIGITS 22 X"); // X is the escape digit. since X is not DTMF, no ex
it is possible
 read();
 write("SAY NUMBER 2233 X"); // X is the escape digit. since X is not DTMF, no
exit is possible
 read();
 // clean up file handlers etc.
 fclose($in);
 fclose($stdlog);
 exit;
 ?>
```

### DeadAGI

DeadAGI का उपयोग तब किया जाता है जब आपके पास कोई लाइव चैनल न हो। आमतौर पर आप DeadAGI को `h` एक्सटेंशन में निष्पादित करते हैं। Asterisk 22 में `DeadAGI` एप्लिकेशन को अप्रचलित कर दिया गया है और भविष्य के रिलीज़ में इसे हटाया जा सकता है; मानक `AGI` एप्लिकेशन अब स्वचालित रूप से हँग‑अप (“dead”) चैनलों को संभालता है, इसलिए नए डायलप्लान में `AGI()` को प्राथमिकता दें।

### FASTAGI

Fast AGI, AGI को एक TCP पोर्ट (डिफ़ॉल्ट रूप से 4573) का उपयोग करके Input/Output चैनल के रूप में लागू करता है। FastAGI फ़ॉर्मेट (agi://) है। उदाहरण के लिए:

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

जब TCP कनेक्शन खो जाता है या डिस्कनेक्ट हो जाता है, तो AGI समाप्त हो जाता है और TCP कनेक्शन बंद हो जाता है, जिसके बाद कॉल डिस्कनेक्ट हो जाती है। यह संसाधन आपके Asterisk सर्वर पर चल रहे स्क्रिप्ट्स की CPU लोड को कम करने में मददगार है जो बाहरी सर्वर पर चल रहे हैं। आप FastAGI के बारे में अधिक विवरण स्रोत कोड डायरेक्टरी में प्राप्त कर सकते हैं (कृपया फ़ाइल “agi/fastagi-test” देखें)। Asterisk-Java लाइब्रेरी Java के लिए एक FastAGI सर्वर इम्प्लीमेंटेशन प्रदान करती है। अधिक जानकारी के लिए देखें https://github.com/asterisk-java/asterisk-java

ARI, आधुनिक REST/WebSocket इंटरफ़ेस, अपना स्वयं का अध्याय अगले भाग में प्राप्त करता है।

## Changing the source code

Asterisk C भाषा में विकसित किया गया है (C++ नहीं)। C प्रोग्रामिंग सिखाना इस दस्तावेज़ के दायरे से बाहर है। यदि आप रुचि रखते हैं, तो आप संबंधित दस्तावेज़ https://docs.asterisk.org पर पाएँगे, जहाँ Asterisk पर पैच लागू करने और बनाने के बारे में अच्छे सुझाव तथा मुख्यतः Doxygen सॉफ़्टवेयर द्वारा उत्पन्न API दस्तावेज़ उपलब्ध हैं। C प्रोग्रामिंग से परिचित लोगों के लिए, एप्लिकेशन का स्रोत कोड बदलना Asterisk को विस्तारित करने का सबसे शक्तिशाली (और खतरनाक) तरीका हो सकता है।

## Summary

इस अध्याय में, आपने सीखा कि बाहरी प्रोग्रामों को Asterisk PBX से कैसे जोड़ा जाए। हमने asterisk –rx के साथ शुरू किया, जिससे Linux शेल से कमांड्स को Asterisk कंसोल में पास किया जाता है। इसके बाद, हमने System() एप्लिकेशन के बारे में जाना, जो डायलप्लान से बाहरी प्रोग्राम को कॉल करने की अनुमति देता है। AMI पारंपरिक PBX में सामान्य CTI इंटरफ़ेस के सबसे निकट का इंटरफ़ेस है। डायलप्लान से किसी एप्लिकेशन को कॉल करने के लिए, हमने AGI का उपयोग किया, जिसमें इसके विभिन्न प्रकार शामिल हैं: डेड चैनलों के लिए DeadAGI, ऑडियो स्ट्रीमिंग को संभालने के लिए EAGI, इनपुट/आउटपुट इंटरफ़ेस के रूप में TCP सॉकेट का उपयोग करने के लिए Fast AGI, और उसी Asterisk बॉक्स के भीतर स्क्रिप्ट्स को कॉल करने और प्रोसेस करने के लिए सामान्य AGI। अगला अध्याय ARI को समर्पित है, जो आधुनिक REST/WebSocket API है और बाहरी एप्लिकेशनों को Asterisk चैनलों और ब्रिजेज़ पर पूर्ण नियंत्रण प्रदान करता है।

## प्रश्नोत्तरी

1. निम्नलिखित में से कौन सा Asterisk के लिए इंटरफ़ेसिंग विधि नहीं है?
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMI TCP सॉकेट्स के माध्यम से Asterisk कमांड पास करने की अनुमति देता है, और यह इंटरफ़ेस एक नई Asterisk इंस्टॉल में डिफ़ॉल्ट रूप से सक्षम होता है।
   - A. True
   - B. False
3. AMI बहुत सुरक्षित है, क्योंकि इसकी प्रमाणीकरण MD5 चुनौती/प्रतिक्रिया का उपयोग करती है।
   - A. True
   - B. False
4. FastAGI डायल प्लान को TCP सॉकेट्स (आमतौर पर पोर्ट 4573) के माध्यम से किसी अन्य मशीन पर बाहरी स्क्रिप्ट्स को कॉल करने देता है।
   - A. True
   - B. False
5. DeadAGI सक्रिय चैनलों पर उपयोग किया जाता है। इसे DAHDI चैनलों पर उपयोग किया जा सकता है लेकिन SIP या IAX चैनलों पर नहीं।
   - A. True
   - B. False
6. AGI केवल PHP को स्क्रिप्टिंग भाषा के रूप में समर्थन करता है।
   - A. True
   - B. False
7. कमांड ___ सभी उपलब्ध AGI कमांड दिखाता है।
8. कमांड ___ सभी उपलब्ध AMI कमांड दिखाता है।
9. एक AMI एक्शन पैकेट में, कौन सा हेडर क्लाइंट शामिल करता है ताकि असिंक्रोनस प्रतिक्रियाएँ और घटनाएँ जो Asterisk से वापस आती हैं, उन्हें उस एक्शन से जोड़ा जा सके जिसने उन्हें ट्रिगर किया?
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. कौन सा AMI manager.conf अनुमति वर्ग उपयोगकर्ता को `Originate` एक्शन चलाने और आउटबाउंड कॉल करने के लिए आवश्यक है?
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**Answers:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
