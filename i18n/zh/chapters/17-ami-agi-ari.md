# 使用 AMI 和 AGI 扩展 Asterisk

在许多情况下，可能需要使用外部应用程序来扩展 Asterisk 的功能。扩展 Asterisk 的方法有很多种。在本章中，我们将介绍将 Asterisk 与其他系统集成的两种经典方式：AMI（Asterisk Manager Interface，Asterisk 管理接口）和 AGI（Asterisk Gateway Interface，Asterisk 网关接口）。我们还将介绍 asterisk –rx 命令和 system() 应用程序。选择哪种方式与 Asterisk 集成取决于具体的应用程序。对于 AGI，最常见的应用是连接到数据库的 IVR。对于 AMI，拨号器（dialer）是最流行的应用。第三种更现代的接口——ARI（Asterisk REST Interface，Asterisk REST 接口）将在下一章中单独介绍。

## 目标

读完本章后，读者应该能够：

- 描述访问外部程序的选项
- 使用 asterisk –rx 命令执行控制台命令
- 在 dialplan 中使用 system() 应用程序调用外部程序
- 解释什么是 AMI 及其工作原理
- 配置 manager.conf 文件并启用 AMI
- 从 PHP 程序执行 AMI 命令
- 解释什么是 Asterisk manager proxy 及其工作原理
- 描述不同的 AGI 类型（DeadAGI、AGI、EAGI、FastAGI）
- 执行一个用 PHP 创建的简单 AGI 程序

## 扩展 Asterisk 的主要方式

Asterisk 提供了多种与外部程序交互的方式。在本章中，我们将介绍：

- Linux 命令行和 Asterisk 控制台
- System() 应用程序
- AMI
- AGI

## 使用控制台 CLI 扩展 Asterisk

应用程序可以使用以下命令轻松地从 Linux shell 调用 Asterisk。

```
asterisk –rx <command>
```

示例：

```
asterisk –rx “stop now”
```

即使是带有输出的命令也可以被调用：

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

## 使用 System() 应用程序扩展 Asterisk

system() 应用程序使 Asterisk 能够调用外部应用程序。

```
asterisk*CLI> show application system
asterisk*CLI>
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

示例：此应用程序使用 netbios WindowsPopup 执行屏幕弹出。

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## 什么是 AMI？

AMI 使客户端程序能够连接到 Asterisk 实例，并通过 TCP 连接发出命令或读取事件。系统集成商会发现这些资源对于跟踪通道状态非常有用。AMI 依赖于一种简单的概念，即通过 TCP 使用 key:value 对的行协议。Asterisk 本身并未准备好处理通过此接口的大量连接。如果您有大量的 AMI 连接，请考虑使用 Asterisk manager proxy。

### 使用哪种语言进行 AMI 开发

如今选择编程语言可能很困难。选项实在太多了——Java、PHP、Perl、C、C#、Python 等等。可以使用任何支持 socket 或 telnet 接口的语言来使用 AMI。由于 PHP 的流行，我们在本书中选择了它。

### AMI 协议行为

- 在向 Asterisk 发送任何命令之前，您需要建立一个 AMI 会话
- 当从客户端发送时，数据包的第一行将具有键 “Action”
- 当来自 Asterisk 时，数据包的第一行将具有键 “Response” 或 “Event”
- 身份验证后，数据包可以在任何方向传输

### 数据包类型

数据包的类型由是否存在以下键决定：

- Action：从连接到 AMI 的客户端发送的请求特定操作的数据包。客户端可用的操作集是有限的。已加载的模块决定了这些操作。数据包包含操作名称及其参数。
- Response：Asterisk 对客户端发送的最后一个操作所做的响应。
- Event：属于在 Asterisk 核心或模块中生成的事件的数据。

当客户端发送 Action 类型的数据包时，会包含一个名为 ActionID 的参数。由于无法预测 Asterisk 发送响应的顺序，因此使用 ActionID 来关联操作和响应。Event 数据包用于两种不同的上下文。首先，事件通知客户端有关 Asterisk 中的更改（例如，新创建的通道、断开连接的通道或代理登录和退出队列）。其次，事件用于将响应传输到客户端操作。

## 配置用户和权限

要访问 AMI，必须建立一个监听 TCP 端口（通常为 5038）的 TCP 连接。您需要配置 /etc/asterisk/manager.conf 文件来创建用户帐户和权限。权限集是有限的：“read”、“write” 或两者兼有。这些权限定义在

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

### 登录到 AMI

要登录并验证 AMI，您需要发送一个 login 类型的 action 数据包，并附带在 manager.conf 中创建的用户名和帐户。

```
Action:login
Username:admin
Secret:password
```

示例：使用 php 登录到 AMI

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
?>
```

如果您不需要接收事件，可以使用 “Events Off”。

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
fputs($socket, "Events: off\r\n\r\n");
?>
```

### Action 数据包

当您向 Asterisk 发送 action 数据包时，可以通过在 action 之后传递 key:value 对来提供一些额外的键（例如，被叫号码）。也可以将通道变量和全局变量传递给 dialplan。

```
Action: <action type><CRLF>
<Key 1>: <Value 1><CRLF>
<Key 2>: <Value 2><CRLF>
Variable: <Variable 1>=<Value 1><CRLF>
Variable: <Variable 2>=<Value 2><CRLF>
...
<CRLF>
```

### Action 命令

您可以使用 CLI 指令 manager show commands 来列出可用的操作。在 Asterisk 22 中，核心命令集包括（此列表仅供参考；已加载的模块会添加更多）：

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
  UnpauseMonitor   call,all         Unpause monitoring of a channel
  PlayDTMF                        call,all         Play DTMF signal on a specific channel.
  PJSIPShowEndpoints              system,reportin  Lists PJSIP endpoints
  PJSIPShowEndpoint               system,reportin  Detail listing of an endpoint
  PJSIPQualify                    system,all       Qualify a chan_pjsip endpoint
  PJSIPShowRegistrationsOutbound  system,reportin  Lists outbound registrations
  PJSIPShowContacts               system,reportin  Lists PJSIP Contacts
```

```
  AGI              agi,all          Add an AGI command to execute by Async AGI
  StopMonitor      call,all         Stop monitoring a channel
  PauseMonitor     call,all         Pause monitoring of a channel
  ChangeMonitor    call,all         Change monitoring filename of a channel
  ShowDialPlan     config,reportin  List dialplan
  Monitor          call,all         Monitor a channel
  DBDelTree        system,all       Delete DB Tree
  DBDel            system,all       Delete DB Entry
  DBPut            system,all       Put DB Entry
  DBGet            system,reportin  Get DB Entry
  Bridge           call,all         Bridge two channels already in the PBX
  Park             call,all         Park a channel
  ParkedCalls      <none>           List parked calls
```

如果您需要了解特定的命令参数，请使用 manager show command <command>。示例：

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

### Event 数据包

每当 Asterisk 中发生某些事情时，管理接口上就会生成事件——例如创建通道或更改状态、两个通道被桥接或解除桥接、注册更改、添加队列成员等。每个事件都是一个以 `Event:` 标题开头的 `Key: value` 行块。

确切的事件集取决于已加载的模块和 Asterisk 版本，因此与其复制一个很快就会过时的列表，不如查询正在运行的服务器以获取权威集合：

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

例如，呼叫桥接通过 `BridgeCreate`、`BridgeEnter`、`BridgeLeave` 和 `BridgeDestroy` 事件报告（`BridgeEnter` 是“当通道进入桥接时引发”）。较旧的 `Link`/`Unlink` 事件已在 Asterisk 12 中删除。

## Asterisk Gateway Interface

AGI 是类似于 Web 服务器使用的 CGI 的 Asterisk 网关接口。它允许使用 Perl、PHP 和 Python 等高级语言来扩展 Asterisk 的功能。CGI 的主要应用是构建 IVR。AGI 有四种类型：

- 普通 AGI，在 Asterisk 盒子内调用程序。
- Fast AGI，使用 TCP socket 在另一台服务器中调用 AGI。
- EAGI，允许从 AGI 访问和控制声音通道。
- DEADAGI，即使在 hangup() 之后也能访问通道。通常在 ‘h’ extension 中调用。

应用程序格式：

```
asterisk*CLI> core show application agi
asterisk*CLI>
  -= Info about application 'AGI' =-
[Synopsis]
Executes an AGI compliant application
[Description]
  [E|Dead]AGI(command|args): Executes an Asterisk Gateway Interface compliant
program on a channel. AGI allows Asterisk to launch external programs
written in any language to control a telephony channel, play audio,
read DTMF digits, etc. by communicating with the AGI protocol on stdin
and stdout.
Returns -1 on hangup (except for DeadAGI) or if application requested
 hangup, or 0 on non-hangup exit.
Using 'EAGI' provides enhanced AGI, with incoming audio available out of band
on file descriptor 3
Use the CLI command 'agi show' to list available agi commands
```

您可以使用命令 `agi show commands` 显示可用的 AGI 命令（下面的输出仅供参考；Asterisk 22 添加了一些额外的命令）：

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

要进行调试，请使用 agi debug。

### 使用 AGI

在此示例中，我们将使用 php-cli，即 php 命令行版本。如果尚未安装 php-cli，请安装它。按照以下步骤使用 php AGI 脚本。第 1 步：所有 AGI 脚本都位于 /var/lib/asterisk/agi-bin。第 2 步：更改权限以允许执行。

```
chmod 755 *.php
```

第 3 步：Shell 接口（PHP 特定）。脚本的第一行必须是：

```
#!/usr/bin/php -q
<?php
```

第 4 步：打开 I/O 通道：

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

第 5 步：管理 Asterisk 输出。每次调用 AGI 时，Asterisk 都会发送信息集。

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

保存发送的信息：

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

前面的脚本将创建一个名为 $agi 的数组。可用选项包括：

- agi_request – AGI 文件名
- agi_channel – AGI 发起通道
- agi_language – 设置的语言
- agi_type – 通道类型（例如 SIP、DAHDI）
- agi_uniqueid – 唯一标识符
- agi_callerid – CallerID（例如 Flavio <8590>）
- agi_context – 发起上下文
- agi_extension – 被叫 extension
- agi_priority – 优先级
- agi_accountcode – 发起帐户代码

要调用名为 agi_extensions 的变量，请使用 $agi[agi_extensions]。第 6 步：使用通道 AGI。此时，您可以开始与 Asterisk 对话。使用 fputs 命令向 AGI 发送命令。您也可以使用 echo 命令。

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

关于使用引号的说明：

- AGI 命令选项不是可选的
- 某些选项需要用引号括起来 <escape digits>
- 某些选项不应加引号 <digit string>
- 某些选项可以使用两种格式
- 您可以使用单引号

第 7 步 – 传递变量。通道变量可以在 AGI 中设置，但不能在 AGI 内部使用。以下示例在 AGI 内部不起作用。

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

以下示例确实有效：

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

第 8 步：Asterisk 响应。验证来自 Asterisk 的响应是必要的：

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

第 9 步：终止锁定（僵尸）进程。如果您的脚本因某种原因失败，进程将挂起。在再次测试之前，请使用 killproc 命令清理它。

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
 errlog("Call from ".$agi['channel']." – Phone ringing ");
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

当您没有活动通道时使用 DeadAGI。通常您在 ‘h’ extension 中执行 DeadAGI。

### FASTAGI

Fast AGI 使用 TCP 端口（默认 4573）作为输入/输出通道来实现 AGI。FastAGI 格式为 (agi://)。例如：

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

当 TCP 连接丢失或断开时，AGI 结束，TCP 连接关闭，随后呼叫断开。此资源对于减轻在外部服务器上运行脚本的 Asterisk 服务器的 CPU 负载非常有用。您可以在源代码目录中获取有关 FastAGI 的更多详细信息（请参阅文件 “agi/fastagi-test”）。Asterisk-Java 库为 Java 提供了 FastAGI 服务器实现。有关更多信息，请参阅 https://github.com/asterisk-java/asterisk-java

ARI，即现代的 REST/WebSocket 接口，将在下一章中单独介绍。

## 更改源代码

Asterisk 是用 C 语言（非 C++）开发的。教授 C 编程超出了本文档的范围。如果您感兴趣，可以在 https://docs.asterisk.org 找到相关文档，其中提供了关于如何应用和创建 Asterisk 补丁的好建议，以及主要由 Doxygen 软件生成的 API 文档。对于熟悉 C 编程的人来说，更改应用程序源代码可能是扩展 Asterisk 最强大（也最危险）的方法。

## 总结

在本章中，您学习了如何将外部程序与 Asterisk PBX 接口。我们从 asterisk –rx 开始，将命令从 Linux shell 传递到 Asterisk 控制台。接下来，我们了解了 System() 应用程序，它允许从 dialplan 调用外部程序。AMI 是最接近传统 PBX 中常见的 CTI 接口的接口。为了从 dialplan 调用应用程序，我们使用了 AGI，并体验了它的不同类型：用于死通道的 DeadAGI，用于处理音频流的 EAGI，用于使用 TCP socket 作为输入/输出接口的 Fast AGI，以及用于在同一个 Asterisk 盒子内调用和处理脚本的普通 AGI。下一章专门介绍 ARI，这是现代的 REST/WebSocket API，它使外部应用程序能够完全控制 Asterisk 通道和桥接。

## 测验

1. 以下哪项不是 Asterisk 的接口方法？
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMI 允许通过 TCP socket 传递 Asterisk 命令，并且此接口在全新的 Asterisk 安装中默认启用。
   - A. True
   - B. False
3. AMI 非常安全，因为它的身份验证使用 MD5 质询/响应。
   - A. True
   - B. False
4. FastAGI 允许 dialplan 通过 TCP socket（通常是端口 4573）在另一台机器上调用外部脚本。
   - A. True
   - B. False
5. DeadAGI 用于活动通道。它可以在 DAHDI 通道上使用，但不能在 SIP 或 IAX 通道上使用。
   - A. True
   - B. False
6. AGI 仅支持 PHP 作为脚本语言。
   - A. True
   - B. False
7. 命令 ___ 显示所有可用的 AGI 命令。
8. 命令 ___ 显示所有可用的 AMI 命令。
9. 在 AMI action 数据包中，客户端包含哪个标题，以便从 Asterisk 返回的异步响应和事件可以与触发它们的动作相关联？
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. 用户必须具备哪个 AMI manager.conf 权限类才能运行 `Originate` 操作并拨打出站呼叫？
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**答案：** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
