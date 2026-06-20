# توسيع Asterisk باستخدام AMI و AGI

في عدة حالات، قد يكون من الضروري توسيع ميزات Asterisk باستخدام تطبيقات خارجية. هناك طرق عديدة يمكن من خلالها توسيع النظام. في هذا الفصل، سنغطي طريقتين كلاسيكيتين لدمج Asterisk مع أنظمة أخرى: AMI – Asterisk Manager Interface و AGI – Asterisk Gateway Interface. سننظر أيضًا في الأمر `asterisk –rx` وتطبيق `system()`. يعتمد اختيار الطريقة التي تريد دمجها مع Asterisk على التطبيق. بالنسبة لـ AGI، يكون التطبيق الأكثر شيوعًا هو IVR المتصل بقاعدة بيانات. بالنسبة لـ AMI، يعتبر Dialers هو التطبيق الأكثر شعبية. الواجهة الثالثة، الأكثر حداثة — ARI، Asterisk REST Interface — مغطاة بشكل منفصل في الفصل التالي.

## الأهداف

بنهاية هذا الفصل، يجب أن يكون القارئ قادرًا على:

- وصف خيارات الوصول إلى البرامج الخارجية
- استخدام أمر asterisk –rx لتنفيذ أمر في وحدة التحكم
- استخدام تطبيق system() لاستدعاء البرامج الخارجية في مخطط الاتصال
- شرح ما هو AMI وكيف يعمل
- تكوين ملف manager.conf وتمكين AMI
- تنفيذ أمر AMI من برنامج PHP
- شرح ما هو Asterisk manager proxy وكيف يعمل
- وصف نكهات AGI المختلفة (DeadAGI, AGI, EAGI, FastAGI)
- تنفيذ برنامج AGI بسيط تم إنشاؤه باستخدام PHP

## الطرق الرئيسية لتوسيع Asterisk

- سطر أوامر لينكس وواجهة Asterisk Console
- System() Application
- AMI
- AGI

## توسيع Asterisk باستخدام سطر أوامر وحدة التحكم

يمكن لتطبيق بسهولة استدعاء Asterisk من سطر أوامر Linux باستخدام الأمر التالي.

```
asterisk -rx <command>
```

مثال:

```
asterisk -rx "stop now"
```

حتى أمر ينتج مخرجات يمكن استدعاؤه:

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

## توسيع Asterisk باستخدام تطبيق System()

يتيح تطبيق system() لـ Asterisk استدعاء تطبيق خارجي.

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

مثال: يقوم هذا التطبيق بفتح نافذة منبثقة باستخدام netbios WindowsPopup.

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## ما هو AMI؟

AMI يتيح لبرنامج العميل الاتصال بنسخة Asterisk وإصدار الأوامر أو قراءة الأحداث عبر اتصال TCP. سيجد مهندسو الأنظمة هذه الموارد مفيدة لتتبع حالات القنوات. يعتمد AMI على مفهوم بسيط لبروتوكول سطر يستخدم أزواج مفتاح:قيمة عبر TCP. Asterisk بحد ذاته غير جاهز للتعامل مع عدد كبير من الاتصالات عبر هذه الواجهة. إذا كان لديك الكثير من الاتصالات إلى AMI، فكر في استخدام وكيل مدير Asterisk.

### أي لغة تستخدم لـ AMI

اختيار لغة برمجة يمكن أن يكون صعبًا في هذه الأيام. هناك ببساطة الكثير من الخيارات — Java, PHP, Perl, C, C#, Python، والعديد غيرها. يمكن استخدام AMI مع أي لغة تدعم واجهة مقبس أو telnet. اخترنا PHP لهذا الكتاب بسبب شعبيتها.

### سلوك بروتوكول AMI

- قبل إرسال أي أوامر إلى Asterisk، تحتاج إلى إنشاء جلسة AMI
- السطر الأول من الحزمة سيحتوي على المفتاح “Action” عندما يُرسل من عميل
- السطر الأول من الحزمة سيحتوي على المفتاح “Response” أو “Event” عندما يأتي من Asterisk
- يمكن نقل الحزم في أي اتجاه بعد المصادقة

### أنواع الحزم

يتم تحديد نوع الحزمة بوجود المفاتيح التالية:

- Action: حزمة تُرسل من عميل متصل بـ AMI يطلب فيها إجراءً محددًا. هناك مجموعة محدودة من الإجراءات المتاحة للعملاء. تحدد الوحدات المحملة هذه الإجراءات. تحتوي الحزمة على اسم الإجراء ومعاماته.
- Response: الاستجابة التي يرسلها Asterisk إلى آخر إجراء أُرسل من العميل.
- Event: بيانات تتعلق بحدث تم توليده في نواة Asterisk أو بواسطة وحدة.

عند إرسال العميل لحزم من نوع Action، يتم تضمين معامل يُدعى ActionID. بما أن ترتيب الاستجابات المرسلة من Asterisk لا يمكن التنبؤ به، يُستخدم ActionID لربط الإجراءات والاستجابات. تُستخدم حزم Event في سياقين مختلفين. أولاً، تُعلم الأحداث العميل بالتغييرات في Asterisk (مثل القنوات التي تم إنشاؤها حديثًا، القنوات التي انقطعت، أو الوكلاء الذين سجلوا الدخول والخروج من قائمة الانتظار). ثانيًا، تُستخدم الأحداث لنقل الاستجابات إلى إجراء العميل.

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

AGI هو واجهة بوابة إلى Asterisk مشابهة لـ CGI المستخدمة من قبل خوادم الويب. يسمح باستخدام لغات عالية المستوى مثل Perl و PHP و Python لتوسيع وظائف Asterisk. التطبيق الرئيسي لـ CGI هو بناء IVR. هناك أربعة أنواع من AGI:

- Normal AGI، الذي يستدعي برنامجًا داخل صندوق Asterisk.
- Fast AGI، الذي يستدعي AGI في خادم آخر باستخدام مقابس TCP.
- EAGI، الذي يتيح الوصول إلى قناة الصوت والتحكم فيها من خلال AGI.
- DeadAGI، الذي يمنح الوصول إلى القناة حتى بعد استدعاء hangup(). عادةً ما يُستدعى في امتداد ‘h’. لاحظ أنه في Asterisk 22 تم إهمال تطبيق `DeadAGI` — تطبيق `AGI` العادي يكتشف قناة تم إنهاؤها ويشغل السكريبت في وضع "dead" تلقائيًا، لذا يجب على مخططات الاتصال الجديدة استدعاء `AGI()` فقط.

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

يمكنك عرض أوامر AGI المتاحة باستخدام الأمر `agi show commands` (الإخراج أدناه تمثيلي؛ يضيف Asterisk 22 بعض الأوامر الإضافية):

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

لتصحيح الأخطاء، استخدم `agi debug`.

### استخدام AGI

في هذا المثال، سنستخدم `php-cli`، نسخة سطر الأوامر من PHP. ثبّت `php-cli` إذا لم يكن مثبتًا بالفعل. اتبع الخطوات التالية لاستخدام سكريبتات PHP AGI.

1. جميع سكريبتات AGI موجودة في `/var/lib/asterisk/agi-bin`
2. غيّر الأذونات للسماح بالتنفيذ.

```
chmod 755 *.php
```

3. واجهة سطر الأوامر (php specific). يجب أن تكون الأسطر الأولى للسكريبت:

```
#!/usr/bin/php -q
<?php
```

4. فتح قنوات الإدخال/الإخراج:

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

5. إدارة مخرجات Asterisk. يقوم Asterisk بإرسال مجموعة المعلومات في كل مرة يتم فيها استدعاء AGI.

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

احفظ المعلومات المرسلة:

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

النص السابق سينشئ مصفوفة باسم $agi. الخيارات المتاحة هي:

- agi_request – اسم ملف AGI
- agi_channel – القناة التي نشأت منها AGI
- agi_language – اللغة المحددة
- agi_type – نوع القناة (مثال: SIP, DAHDI)
- agi_uniqueid – المعرف الفريد
- agi_callerid – معرف المتصل (مثال: Flavio <8590>)
- agi_context – السياق الأصلي
- agi_extension – الامتدادات المستدعاة
- agi_priority – الأولوية
- agi_accountcode – رمز حساب المصدر

لاستدعاء متغير باسم agi_extensions، استخدم $agi[agi_extensions].

6. استخدم قناة AGI. في هذه المرحلة، يمكنك البدء في التحدث إلى Asterisk. استخدم أمر fputs لإرسال الأوامر إلى AGI. يمكنك أيضًا استخدام أمر echo.

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

ملاحظات حول استخدام الاقتباسات:

- خيارات أوامر AGI ليست اختيارية
- بعض الخيارات تحتاج إلى أن تُحاط بعلامات اقتباس <escape digits>
- بعض الخيارات لا يجب أن تُحاط بعلامات اقتباس <digit string>
- بعض الخيارات يمكن أن تُكتب بصيغتين
- يمكنك استخدام علامات اقتباس مفردة

الخطوة 7 – تمرير المتغيّرات  
يمكن تعيين متغيّرات القناة في AGI، لكن لا يمكن استخدامها داخل AGI. المثال التالي لا يعمل داخل AGI.

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

المثال التالي يعمل:

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

Step 8: Asterisk responses التالي ضروري للتحقق من الاستجابات من Asterisk:

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

Step 9: Kill the locked (zombie) processes إذا فشل البرنامج النصي الخاص بك لسبب ما، ستبقى العملية معلقة. استخدم أمر killproc لتنظيفها قبل الاختبار مرة أخرى.

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

يُستخدم DeadAGI عندما لا يكون لديك قناة حية. عادةً ما تقوم بتنفيذ DeadAGI في امتداد ´h´. في Asterisk 22 تم إهمال التطبيق `DeadAGI` وقد يُزال في إصدار مستقبلي؛ التطبيق القياسي `AGI` الآن يتعامل مع القنوات التي تم قطعها ("الميتة") تلقائيًا، لذا يُفضَّل استخدام `AGI()` في مخططات الاتصال الجديدة.

### FASTAGI

يُطبق Fast AGI بروتوكول AGI باستخدام منفذ TCP (4573 افتراضيًا) كقناة إدخال/إخراج. صيغة FastAGI هي (agi://). على سبيل المثال:

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

عند فقدان اتصال TCP أو انقطاعه، ينتهي الـ AGI ويُغلق اتصال TCP، يتبعه قطع المكالمة. هذه الميزة مفيدة لتخفيف حمل وحدة المعالجة المركزية من خادم Asterisk الخاص بك الذي يشغّل سكريبتات على خادم خارجي. يمكنك الحصول على مزيد من التفاصيل حول FastAGI في دليل شفرة المصدر (يرجى الاطلاع على الملف “agi/fastagi-test”). توفر مكتبة Asterisk-Java تنفيذ خادم FastAGI للغة Java. لمزيد من المعلومات، راجع https://github.com/asterisk-java/asterisk-java

ARI، واجهة REST/WebSocket الحديثة، ستحصل على فصلها الخاص في التالي.

## تغيير شفرة المصدر

Asterisk يتم تطويره بلغة C (ليس C++). تعليم برمجة C خارج نطاق هذا المستند. إذا كنت مهتمًا، ستجد الوثائق ذات الصلة على https://docs.asterisk.org، التي تقدم نصائح جيدة حول كيفية تطبيق وإنشاء تصحيحات لـ Asterisk بالإضافة إلى وثائق API التي تُنشئ في الغالب بواسطة برنامج Doxygen. بالنسبة لأولئك الذين لديهم خبرة في برمجة C، فإن تعديل شفرة المصدر للتطبيقات يمكن أن يكون أقوى (وأخطر) طريقة لتوسيع Asterisk.

## Summary

في هذا الفصل، تعلمت كيفية ربط البرامج الخارجية بـ Asterisk PBX. بدأنا بأمر asterisk –rx لتمرير الأوامر من سطر أوامر لينكس إلى وحدة تحكم Asterisk. بعد ذلك، تعرفنا على تطبيق System() الذي يسمح باستدعاء برنامج خارجي من الـ dial plan. AMI هو أقرب واجهة إلى واجهة CTI الشائعة في أنظمة PBX التقليدية. لاستدعاء تطبيق من الـ dial plan، استخدمنا AGI، مع استعراض أنواعه المختلفة: DeadAGI للقنوات الميتة، EAGI لمعالجة تدفق الصوت، Fast AGI لاستخدام مقابس TCP كواجهة إدخال/إخراج، وAGI العادي لاستدعاء ومعالجة السكريبتات داخل نفس خادم Asterisk. الفصل التالي مخصص لـ ARI، واجهة REST/WebSocket الحديثة التي تمنح التطبيقات الخارجية تحكمًا كاملاً في قنوات وجسور Asterisk.

## Quiz

1. أي مما يلي ليس طريقة ربط لـ Asterisk؟
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. يسمح AMI بتمرير أوامر Asterisk عبر مقابس TCP، ويتم تمكين هذه الواجهة افتراضيًا في تثبيت Asterisk جديد.
   - A. True
   - B. False
3. AMI آمن جدًا، لأن المصادقة تستخدم تحدي/استجابة MD5.
   - A. True
   - B. False
4. يتيح FastAGI لخطة الاتصال استدعاء سكريبتات خارجية على جهاز آخر عبر مقابس TCP (عادةً المنفذ 4573).
   - A. True
   - B. False
5. يُستخدم DeadAGI على القنوات النشطة. يمكن استخدامه على قنوات DAHDI لكن ليس على قنوات SIP أو IAX.
   - A. True
   - B. False
6. يدعم AGI لغة برمجة واحدة فقط وهي PHP.
   - A. True
   - B. False
7. الأمر ___ يعرض جميع أوامر AGI المتاحة.
8. الأمر ___ يعرض جميع أوامر AMI المتاحة.
9. في حزمة إجراء AMI، أي رأس يضيفه العميل بحيث يمكن ربط الاستجابات غير المتزامنة والأحداث العائدة من Asterisk بالإجراء الذي تسبب فيها؟
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. أي فئة صلاحية في manager.conf يجب أن يمتلكها المستخدم لتشغيل إجراء `Originate` وإجراء مكالمة صادرة؟
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**Answers:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
