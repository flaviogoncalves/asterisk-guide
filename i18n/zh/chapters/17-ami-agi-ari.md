# 扩展 Asterisk 与 AMI 和 AGI

在多种情况下，可能需要使用外部应用程序来扩展 Asterisk 的功能。扩展 Asterisk 的方式有很多种。本章将介绍两种经典的将 Asterisk 与其他系统集成的方法：AMI – Asterisk Manager Interface 和 AGI – Asterisk Gateway Interface。我们还会查看 `asterisk –rx` 命令和 `system()` 应用程序。选择哪种方式与 Asterisk 集成取决于具体的应用场景。对于 AGI，最常见的应用是连接数据库的 IVR。对于 AMI，拨号器是最受欢迎的应用。第三种更现代的接口——ARI，即 Asterisk REST Interface——将在下一章单独介绍。

## 目标

通过本章学习，读者应能够：

- 描述访问外部程序的选项  
- 使用 `asterisk –rx` 命令执行控制台指令  
- 在 dialplan 中使用 `system()` 应用调用外部程序  
- 解释 AMI 是什么以及它的工作原理  
- 配置 `manager.conf` 文件并启用 AMI  
- 从 PHP 程序执行 AMI 命令  
- 解释 Asterisk manager proxy 是什么以及它的工作方式  
- 描述不同的 AGI 变体（DeadAGI、AGI、EAGI、FastAGI）  
- 执行使用 PHP 编写的简单 AGI 程序

## 扩展 Asterisk 的主要方式

- Linux 命令行和 Asterisk 控制台
- System() 应用程序
- AMI
- AGI

## 使用控制台 CLI 扩展 Asterisk

应用程序可以轻松地在 Linux shell 中使用以下命令调用 Asterisk。

```
asterisk -rx <command>
```

示例：

```
asterisk -rx "stop now"
```

甚至可以调用带有输出的命令：

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

## Extending Asterisk using the System() application

The system() application enables Asterisk to call an external application.

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

Example: This application does a screen-pop using netbios WindowsPopup.

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## 什么是 AMI？

AMI 使客户端程序能够通过 TCP 连接连接到 Asterisk 实例并发送命令或读取事件。系统集成商会发现这些资源对于跟踪通道状态非常有用。AMI 基于一种使用 key:value 对的行协议在 TCP 上进行通信的简单概念。Asterisk 本身并未准备好处理过多的此接口连接。如果你对 AMI 有大量连接，请考虑使用 Asterisk manager proxy。

### 使用哪种语言来操作 AMI

如今选择编程语言可能很困难。选项实在太多——Java、PHP、Perl、C、C#、Python 以及其他几种语言。只要语言支持套接字或 telnet 接口，就可以使用 AMI。我们在本书中选择了 PHP，因为它的流行度。

### AMI 协议行为

- 在向 Asterisk 发送任何命令之前，需要先建立 AMI 会话
- 当客户端发送数据包时，第一行的键为 “Action”
- 当数据包来自 Asterisk 时，第一行的键为 “Response” 或 “Event”
- 认证完成后，数据包可以在任意方向传输

### 数据包类型

数据包的类型由以下键的存在决定：

- Action：客户端向 AMI 发送的请求特定操作的数据包。客户端可用的操作集合是有限的，由已加载的模块决定。数据包包含操作名称及其参数。
- Response：Asterisk 对客户端最近一次发送的 Action 的响应。
- Event：属于 Asterisk 核心或某个模块生成的事件的数据。

当客户端发送 Action 类型的数据包时，会包含一个名为 ActionID 的参数。由于无法预测 Asterisk 发送的响应顺序，ActionID 用于将操作与响应关联。Event 数据包在两种不同的情境下使用。首先，事件向客户端通报 Asterisk 中的变化（例如，新建通道、通道断开，或坐席登录/退出队列）。其次，事件用于向客户端传递对其 Action 的响应。

## Configuring users and permissions

要访问 AMI，需要建立一个监听 TCP 端口（通常是 5038）的 TCP 连接。您需要配置 /etc/asterisk/manager.conf 文件来创建用户账户并分配权限。权限集合是有限的：“read”、“write”或两者兼有。这些权限在

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

要登录并认证 AMI，您需要发送一个类型为 login 的 action 包，并提供在 manager.conf 中创建的用户名和账户。

```
Action:login
Username:admin
Secret:password
```

示例：使用 php 登录 AMI

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

### Action packets

当您向 Asterisk 发送 action 包时，可以通过在 action 之后传递 key:value 对来提供一些额外的键（例如，被叫号码）。也可以将通道和全局变量传递给 dialplan。

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

您可以使用 CLI 指令 `manager show` 命令列出可用的 actions。在 Asterisk 22 中，核心命令集包括（此列表仅作示例；加载的模块会添加更多）：

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

如果需要了解特定命令的参数，请使用 `manager show <command>`。示例：

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

每当 Asterisk 中发生某些事件时，管理接口会生成事件——通道被创建或状态改变、两个通道被桥接或解除桥接、注册信息变化、队列成员被添加，等等。每个事件都是一段

`Key: value` 行，以 `Event:` 头部开始。

具体的事件集合取决于已加载的模块和 Asterisk 版本，因此与其复制一个很快就会过时的列表，不如查询运行中的服务器以获取权威的集合：

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

例如，呼叫桥接通过 `BridgeCreate`、`BridgeEnter`、`BridgeLeave` 和 `BridgeDestroy` 事件报告（`BridgeEnter` 为 “当通道进入桥接时触发”）。较早的 `Link`/`Unlink` 事件已在 Asterisk 12 中移除。

## Asterisk Gateway Interface

AGI 是一种类似于 Web 服务器使用的 CGI 的 Asterisk 网关接口。它允许使用 Perl、PHP、Python 等高级语言来扩展 Asterisk 的功能。CGI 的主要应用是构建 IVR。AGI 有四种类型：

- Normal AGI，在 Asterisk 本机内部调用程序。
- Fast AGI，使用 TCP 套接字在另一台服务器上调用 AGI。
- EAGI，允许从 AGI 访问和控制声音通道。
- DeadAGI，即使在 hangup() 之后仍可访问通道。通常在 ‘h’ 扩展中调用。请注意，在 Asterisk 22 中 `DeadAGI` 应用已被弃用——常规 `AGI` 应用会检测到已挂断的通道并自动以 “dead” 模式运行脚本，因此新的 dialplan 应直接调用 `AGI()`。

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

您可以使用命令 `agi show commands` 查看可用的 AGI 命令（以下输出仅作示例；Asterisk 22 添加了若干额外命令）：

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

调试时，使用 agi debug。

### Using AGI

在本例中，我们将使用 php-cli，即 php 的命令行版本。如果系统中尚未安装 php-cli，请先进行安装。按照以下步骤使用 php AGI 脚本。

1. 所有 AGI 脚本位于 `/var/lib/asterisk/agi-bin`
2. 更改权限以允许执行。

```
chmod 755 *.php
```

3. Shell 接口（php 特有）。脚本的前几行必须是：

```
#!/usr/bin/php -q
<?php
```

4. 打开 I/O 通道：

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

5. 管理 Asterisk 输出。Asterisk 在每次调用 AGI 时都会发送信息集合。

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

上述脚本将创建一个名为 $agi 的数组。可用选项包括：

- agi_request – AGI 文件名
- agi_channel – AGI 发起的通道
- agi_language – 设置的语言
- agi_type – 通道类型（例如 SIP、DAHDI）
- agi_uniqueid – 唯一标识符
- agi_callerid – 主叫号码（例如 Flavio <8590>）
- agi_context – 发起的 context
- agi_extension – 被叫的 extensions
- agi_priority – 优先级
- agi_accountcode – 发起的 account code

要调用名为 agi_extensions 的变量，使用 $agi[agi_extensions]。

6. 使用通道 AGI。此时，您可以开始与 Asterisk 对话。使用 fputs 命令向 AGI 发送指令，也可以使用 echo 命令。

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

关于使用引号的注意事项：

- AGI 命令选项不是可选的
- 某些选项需要用引号括起来 <escape digits>
- 某些选项不应使用引号 <digit string>
- 某些选项两种格式皆可
- 可以使用单引号

Step 7 – Pass variables 通道变量可以在 AGI 中设置，但不能在 AGI 内部使用。下面的示例在 AGI 中无法工作。

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

下面的示例可以工作：

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

Step 8: Asterisk responses 为了验证 Asterisk 的响应，需要执行以下操作：

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

Step 9: Kill the locked (zombie) processes 如果脚本因某种原因失败，进程会挂起。使用 killproc 命令在再次测试前将其清除。

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

DeadAGI 在没有实时通道时使用。通常在 ‘h’ 扩展中执行 DeadAGI。在 Asterisk 22 中 `DeadAGI` 应用已被弃用，未来版本可能会移除；标准 `AGI` 应用现在会自动处理已挂断（“dead”）的通道，因此在新 dialplan 中应优先使用 `AGI()`。

### FASTAGI

Fast AGI 通过 TCP 端口（默认 4573）实现 AGI，作为输入/输出通道。FastAGI 的格式为 (agi://)。例如：

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

当 TCP 连接丢失或断开时，AGI 结束，TCP

## 更改源代码

Asterisk 是用 C 语言（而非 C++）开发的。教授 C 编程超出本文档的范围。如果您感兴趣，可以在 https://docs.asterisk.org 找到相关文档，其中提供了关于如何为 Asterisk 应用补丁以及大部分由 Doxygen 软件生成的 API 文档的实用技巧。对于熟悉 C 编程的人来说，修改应用程序的源代码是扩展 Asterisk 最强大（也是最危险）的方式。

## 摘要

在本章中，您学习了如何将外部程序与 Asterisk PBX 接口。我们从使用 asterisk –rx 将命令从 Linux shell 传递到 Asterisk 控制台开始。接着，我们了解了 System() 应用程序，它允许在 dialplan 中调用外部程序。AMI 是最接近传统 PBX 中常见的 CTI 接口的接口。要从 dialplan 调用应用程序，我们使用了 AGI，并尝试了其不同的变体：用于死通道的 DeadAGI、用于处理音频流的 EAGI、使用 TCP 套接字作为输入/输出接口的 Fast AGI，以及在同一台 Asterisk 机器上调用和处理脚本的普通 AGI。下一章将专注于 ARI，这个现代的 REST/WebSocket API 为外部应用程序提供对 Asterisk 通道和桥接的完整控制。

## Quiz

1. 以下哪项不是 Asterisk 的接口方式？
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMI 允许通过 TCP 套接字传递 Asterisk 命令，并且此接口在全新 Asterisk 安装中默认启用。
   - A. True
   - B. False
3. AMI 非常安全，因为它的认证使用 MD5 挑战/响应。
   - A. True
   - B. False
4. FastAGI 让 dialplan 可以通过 TCP 套接字（通常是 4573 端口）调用另一台机器上的外部脚本。
   - A. True
   - B. False
5. DeadAGI 用于活动通道。它可以在 DAHDI 通道上使用，但不能在 SIP 或 IAX 通道上使用。
   - A. True
   - B. False
6. AGI 只支持 PHP 作为脚本语言。
   - A. True
   - B. False
7. 命令 ___ 显示所有可用的 AGI 命令。
8. 命令 ___ 显示所有可用的 AMI 命令。
9. 在 AMI action 包中，客户端包含哪个头部，以便将异步响应和事件与触发它们的操作关联起来？
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. 为了运行 `Originate` 操作并发起外呼，用户必须拥有 AMI manager.conf 的哪个权限类？
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**Answers:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
