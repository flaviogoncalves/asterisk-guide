# Extending Asterisk with AMI and AGI

いくつかの状況では、外部アプリケーションを使用して Asterisk の機能を拡張する必要がある場合があります。拡張方法は多数存在します。本章では、Asterisk と他システムを統合する古典的な方法のうち、2 つである AMI – Asterisk Manager Interface と AGI – Asterisk Gateway Interface を取り上げます。また、`asterisk –rx` コマンドと `system()` アプリケーションについても説明します。どの方法で Asterisk と統合するかは、対象となるアプリケーション次第です。AGI の場合、最も一般的なアプリケーションはデータベースに接続した IVR です。AMI では、ダイヤラーが最も人気のあるアプリです。3 番目の、よりモダンなインターフェースである ARI、Asterisk REST Interface については、次章で別途取り上げます。

## Objectives

この章の終わりまでに、読者は以下ができるようになること：

- 外部プログラムへのアクセスオプションを説明できること
- `asterisk –rx` コマンドを使用してコンソールコマンドを実行できること
- dialplan で `system()` アプリを使って外部プログラムを呼び出せること
- AMI が何か、そしてその動作原理を説明できること
- `manager.conf` ファイルを設定し、AMI を有効化できること
- PHP プログラムから AMI コマンドを実行できること
- Asterisk manager proxy が何か、そしてその動作原理を説明できること
- 異なる AGI フレーバー（DeadAGI、AGI、EAGI、FastAGI）を説明できること
- PHP で作成したシンプルな AGI プログラムを実行できること

## Asterisk を拡張する主な方法

- Linux コマンドラインと Asterisk コンソール
- System() アプリケーション
- AMI
- AGI

## コンソールCLIでAsteriskを拡張する

アプリケーションは、以下のコマンドを使用してLinuxシェルから簡単にAsteriskを呼び出すことができます。

```
asterisk -rx <command>
```

例:

```
asterisk -rx "stop now"
```

出力を伴うコマンドでも呼び出すことができます:

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

## System() アプリケーションを使用した Asterisk の拡張

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

## AMI とは？

AMI はクライアントプログラムが Asterisk インスタンスに接続し、TCP 接続上でコマンドを送信したりイベントを取得したりできるようにします。システムインテグレータは、チャンネル状態の追跡にこれらのリソースが有用であると感じるでしょう。AMI は、TCP 上で key:value ペアを使用するシンプルなラインプロトコルの概念に依存しています。Asterisk 単体ではこのインターフェース上で多数の接続を処理する準備ができていません。AMI への接続が多数ある場合は、Asterisk manager proxy の使用を検討してください。

### AMI に使用する言語

プログラミング言語の選択は近年難しくなっています。選択肢が多すぎます—Java、PHP、Perl、C、C#、Python、その他多数。ソケットまたは telnet インターフェースをサポートしていれば、どの言語でも AMI を使用できます。本書では、人気が高いことから PHP を選びました。

### AMI プロトコルの動作

- Asterisk にコマンドを送る前に、AMI セッションを確立する必要があります
- クライアントから送信されるパケットの最初の行はキー “Action” を持ちます
- Asterisk から送られるパケットの最初の行はキー “Response” または “Event” を持ちます
- 認証後は、任意の方向にパケットを送受信できます

### パケットタイプ

パケットのタイプは以下のキーの有無で決まります。

- Action: AMI に接続したクライアントが特定のアクションを要求するために送るパケット。クライアントが利用できるアクションは有限で、ロードされたモジュールがこれらを決定します。パケットはアクション名とそのパラメータを含みます。
- Response: クライアントが送った最後の Action に対して Asterisk が返す応答。
- Event: Asterisk コアまたはモジュールが生成したイベントに属するデータ。

クライアントが Action タイプのパケットを送るときは、ActionID というパラメータが含まれます。Asterisk から送られる応答の順序は予測できないため、ActionID を使ってアクションと応答を関連付けます。Event パケットは二つの異なるコンテキストで使用されます。第一に、イベントはクライアントに Asterisk の変化（例：新規作成されたチャンネル、切断されたチャンネル、キューへのエージェントのログイン・ログアウト）を通知します。第二に、イベントはクライアントのアクションに対する応答を転送するために使用されます。

## Configuring users and permissions

AMI にアクセスするには、TCP ポート（通常は 5038）でリッスンする TCP 接続を確立する必要があります。/etc/asterisk/manager.conf ファイルを設定してユーザーアカウントと権限を作成します。権限は「read」「write」またはその両方の有限集合です。これらの権限は

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

AMI にログインして認証するには、manager.conf で作成したユーザー名とアカウントを使用して login タイプのアクションパケットを送信する必要があります。

```
Action:login
Username:admin
Secret:password
```

例: php を使用した AMI へのログイン

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
?>
```

イベントを受信する必要がない場合は “Events Off” を使用できます。

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

Asterisk にアクションパケットを送信する際、アクションの後に key:value ペアを渡すことで追加のキー（例: 呼び出し番号）を提供できます。また、チャネル変数やグローバル変数をダイヤルプランに渡すことも可能です。

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

CLI コマンド `manager show` を使用して利用可能なアクションを一覧表示できます。Asterisk 22 ではコアセットのコマンドは次のとおりです（このリストは代表的なもので、ロードされたモジュールがさらに追加します）：

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

特定のコマンドパラメータを知りたい場合は `manager show command <command>` を使用します。例：

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

イベントはマネージャインターフェース上で Asterisk で何かが起こるたびに生成されます――チャネルが作成または状態変更されたとき、2 つのチャネルがブリッジまたはブリッジ解除されたとき、登録が変更されたとき、キューのメンバーが追加されたとき、などです。各イベントは`Key: value`行からなるブロックで、`Event:`ヘッダーで始まります。

正確なイベントの集合はロードされたモジュールと Asterisk のバージョンに依存するため、すぐに古くなるリストを再現するよりも、実行中のサーバーに対して権威ある集合を問い合わせる方が良いでしょう：

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

例えば、コールブリッジは`BridgeCreate`、`BridgeEnter`、`BridgeLeave`、`BridgeDestroy`イベントで報告されます（`BridgeEnter`は「チャネルがブリッジに入ったときに発生」）。古い`Link`/`Unlink`イベントは Asterisk 12 で削除されました。

## Asterisk Gateway Interface

AGI は、ウェブサーバーで使用される CGI に似た Asterisk へのゲートウェイインターフェースです。Perl、PHP、Python などの高級言語を使用して Asterisk の機能を拡張することができます。CGI の主な用途は IVR の構築です。AGI には次の 4 種類があります。

- Normal AGI、Asterisk のボックス内でプログラムを呼び出すもの。
- Fast AGI、TCP ソケットを使用して別サーバー上の AGI を呼び出すもの。
- EAGI、AGI からサウンドチャンネルへのアクセスと制御を可能にするもの。
- DeadAGI、hangup() 後でもチャンネルへのアクセスを提供するもの。通常は ‘h’ エクステンションで呼び出されます。Asterisk 22 では `DeadAGI` アプリケーションは非推奨となっており、通常の `AGI` アプリケーションがハングアップしたチャンネルを検出し、自動的に「dead」モードでスクリプトを実行するため、新しいダイヤルプランでは `AGI()` を呼び出すだけで構いません。

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

You can show the available AGI commands using the command `agi show commands` (output below is representative; Asterisk 22 adds a few additional commands):

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

デバッグするには、agi debug を使用します。

### AGI の使用

この例では、php-cli（PHP のコマンドライン版）を使用します。php-cli がまだインストールされていない場合はインストールしてください。php AGI スクリプトを使用する手順は以下の通りです。

1. すべての AGI スクリプトは `/var/lib/asterisk/agi-bin` にあります
2. 実行できるように権限を変更します

```
chmod 755 *.php
```

3. シェルインターフェース（php 固有）。スクリプトの最初の行は次のようにする必要があります：

```
#!/usr/bin/php -q
<?php
```

4. I/O チャネルを開く:

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

5. Asterisk の出力を管理する。Asterisk は AGI が呼び出されるたびに情報セットを送信します。

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

送信された情報を保存する:

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

前のスクリプトは $agi という配列を作成します。利用可能なオプションは次のとおりです：

- agi_request – AGI ファイル名
- agi_channel – AGI 発信元チャネル
- agi_language – 設定された言語
- agi_type – チャネルタイプ（例：SIP、DAHDI）
- agi_uniqueid – ユニーク識別子
- agi_callerid – 発信者ID（例：Flavio <8590>）
- agi_context – 発信元コンテキスト
- agi_extension – 呼び出されたエクステンション
- agi_priority – 優先度
- agi_accountcode – 発信元アカウントコード

変数 agi_extensions を呼び出すには、$agi[agi_extensions] を使用します。

6. チャネル AGI を使用します。この時点で Asterisk と対話を開始できます。fputs コマンドで AGI にコマンドを送信できます。echo コマンドも使用可能です。

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

Notes about using quotes:

- AGI コマンドオプションは省略できません
- 一部のオプションは引用符で囲む必要があります <escape digits>
- 一部のオプションは引用符で囲んではいけません <digit string>
- 一部のオプションは両方の形式が使用可能です
- シングルクオートも使用できます

Step 7 – Pass variables Channel variables can be set in the AGI, but cannot be used inside the AGI. The following example does not work inside an AGI.

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

以下の例は動作します:

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

Step 8: Asterisk responses  
以下は Asterisk からの応答を検証するために必要です：

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

Step 9: ロックされた（ゾンビ）プロセスを終了する スクリプトが何らかの理由で失敗すると、プロセスがハングします。再テストする前に killproc コマンドを使用してクリーンアップしてください。

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

DeadAGI はライブチャネルがない場合に使用します。通常、´h´ エクステンションで DeadAGI を実行します。Asterisk 22 では `DeadAGI` アプリケーションは非推奨となっており、将来のリリースで削除される可能性があります；標準の `AGI` アプリケーションがハングアップ（「dead」）チャネルを自動的に処理するようになったので、新しいダイヤルプランでは `AGI()` を使用することを推奨します。

### FASTAGI

Fast AGI は TCP ポート（デフォルトは 4573）を入出力チャネルとして使用し、AGI を実装します。FastAGI の形式は (agi://) です。例えば：

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

TCP 接続が失われるか切断されると、AGI は終了し TCP 接続が閉じられ、続いて通話が切断されます。このリソースは、外部サーバーでスクリプトを実行している Asterisk サーバーの CPU 負荷を軽減するのに役立ちます。FastAGI の詳細はソースコードディレクトリで確認できます（「agi/fastagi-test」ファイルをご参照ください）。Asterisk-Java ライブラリは Java 用の FastAGI サーバ実装を提供しています。詳しくは https://github.com/asterisk-java/asterisk-java をご覧ください。

ARI（モダンな REST/WebSocket インターフェース）は、次の章で取り上げます。

## ソースコードの変更

Asterisk は C 言語（C++ ではありません）で開発されています。C プログラミングの指導は本書の範囲を超えますが、興味がある方は https://docs.asterisk.org にて関連ドキュメントを見つけることができます。そこでは、Asterisk にパッチを適用・作成する方法や、主に Doxygen ソフトウェアで生成された API ドキュメントに関する有用なヒントが提供されています。C プログラミングに慣れている方にとって、アプリケーションのソースコードを変更することは、Asterisk を拡張する最も強力（かつ危険）な手段となり得ます。

## 概要

この章では、外部プログラムを Asterisk PBX にインターフェースする方法を学びました。Linux シェルから Asterisk コンソールへコマンドを渡す `asterisk –rx` から始めました。次に、ダイヤルプランから外部プログラムを呼び出すことができる `System()` アプリケーションについて学びました。AMI は従来の PBX で一般的な CTI インターフェースに最も近いインターフェースです。ダイヤルプランからアプリケーションを呼び出すために、AGI を使用し、そのさまざまなフレーバーを体験しました：DeadAGI はデッドチャンネル用、EAGI はオーディオストリーミングの処理用、Fast AGI は TCP ソケットを入出力インターフェースとして使用するもの、通常の AGI は同じ Asterisk ボックス内でスクリプトを呼び出し処理するためのものです。次の章は ARI に専念しており、外部アプリケーションに Asterisk のチャンネルとブリッジを完全に制御できる最新の REST/WebSocket API です。

## Quiz

1. Which of the following is NOT an interfacing method for Asterisk?
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMI allows passing Asterisk commands over TCP sockets, and this interface is enabled by default in a fresh Asterisk install.
   - A. True
   - B. False
3. AMI is very safe, because its authentication uses MD5 challenge/response.
   - A. True
   - B. False
4. FastAGI lets the dial plan call external scripts on another machine over TCP sockets (usually port 4573).
   - A. True
   - B. False
5. DeadAGI is used on active channels. It can be used on DAHDI channels but not on SIP or IAX channels.
   - A. True
   - B. False
6. AGI supports only PHP as a scripting language.
   - A. True
   - B. False
7. The command ___ shows all available AGI commands.
8. The command ___ shows all available AMI commands.
9. In an AMI action packet, which header does the client include so that the asynchronous responses and events coming back from Asterisk can be correlated with the action that triggered them?
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. Which AMI manager.conf permission class must a user have in order to run the `Originate` action and place an outbound call?
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**Answers:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
