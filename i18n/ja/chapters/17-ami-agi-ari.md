# AMIとAGIによるAsteriskの拡張

いくつかの状況において、外部アプリケーションを使用してAsteriskの機能を拡張する必要が生じることがあります。Asteriskを拡張する方法は多岐にわたります。本章では、Asteriskを他のシステムと統合するための古典的な2つの方法、すなわちAMI（Asterisk Manager Interface）とAGI（Asterisk Gateway Interface）について解説します。また、`asterisk –rx`コマンドと`system()`アプリケーションについても見ていきます。Asteriskとの統合方法を選択する際は、アプリケーションの性質に依存します。AGIの場合、最も一般的な用途はデータベースに接続されたIVRです。AMIの場合、ダイヤラーが最も人気のあるアプリケーションです。より現代的な3つ目のインターフェースであるARI（Asterisk REST Interface）については、次章で個別に解説します。

## 学習目標

本章を読み終えることで、読者は以下のことができるようになります。

- 外部プログラムへのアクセスオプションを説明する
- `asterisk –rx`コマンドを使用してコンソールコマンドを実行する
- `system()`アプリを使用してダイヤルプランから外部プログラムを呼び出す
- AMIとは何か、どのように動作するかを説明する
- `manager.conf`ファイルを構成し、AMIを有効にする
- PHPプログラムからAMIコマンドを実行する
- Asterisk manager proxyとは何か、どのように動作するかを説明する
- さまざまなAGIの種類（DeadAGI、AGI、EAGI、FastAGI）を説明する
- PHPで作成した単純なAGIプログラムを実行する

## Asteriskを拡張する主な方法

Asteriskには、外部プログラムとインターフェースするためのさまざまな方法があります。本章では、以下について解説します。

- LinuxコマンドラインおよびAsteriskコンソール
- `System()`アプリケーション
- AMI
- AGI

## コンソールCLIによるAsteriskの拡張

アプリケーションは、以下のコマンドを使用してLinuxシェルからAsteriskを簡単に呼び出すことができます。

```
asterisk –rx <command>
```

例：

```
asterisk –rx “stop now”
```

出力のあるコマンドも呼び出すことができます：

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

## System()アプリケーションを使用したAsteriskの拡張

`system()`アプリケーションを使用すると、Asteriskから外部アプリケーションを呼び出すことができます。

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

例：このアプリケーションは、`netbios`の`WindowsPopup`を使用して画面ポップアップを行います。

```
exten => 9000,1,System(/bin/echo -e "'Incoming Call From -> ${CALLERID(num)}
\\r Received: ${DATETIME}'"|/usr/bin/smbclient -M target_netbiosname)
exten => 9000,2,Dial(PJSIP/9000,15,t)
exten => 9000,3,Hangup
```

## AMIとは何か？

AMIを使用すると、クライアントプログラムがAsteriskインスタンスに接続し、TCP接続を介してコマンドの発行やイベントの読み取りを行うことができます。システムインテグレーターは、これらのリソースをチャネル状態の追跡に役立てることができます。AMIは、TCP上でkey:valueペアを使用する単純な行プロトコルという概念に基づいています。Asterisk単体では、このインターフェースを介した多数の接続を処理する準備はできていません。AMIへの接続数が多い場合は、Asterisk manager proxyの使用を検討してください。

### AMIで使用する言語

今日、プログラミング言語を選択するのは難しい場合があります。Java、PHP、Perl、C、C#、Pythonなど、選択肢が多すぎるためです。ソケットまたはtelnetインターフェースをサポートする言語であれば、どの言語でもAMIを使用することが可能です。本書では、その普及度からPHPを選択しました。

### AMIプロトコルの動作

- Asteriskにコマンドを送信する前に、AMIセッションを確立する必要があります
- クライアントから送信されるパケットの最初の行には、"Action"というキーが含まれます
- Asteriskから送信されるパケットの最初の行には、"Response"または"Event"というキーが含まれます
- 認証後、パケットはどちらの方向にも送信可能です

### パケットタイプ

パケットのタイプは、以下のキーの存在によって決定されます。

- Action: AMIに接続されたクライアントから、特定の操作を要求するために送信されるパケット。クライアントが利用可能なアクションのセットは有限です。読み込まれたモジュールによってこれらのアクションが決定されます。パケットには、アクション名とそのパラメータが含まれます。
- Response: クライアントから送信された最後のアクションに対して、Asteriskから送信される応答。
- Event: Asteriskコアまたはモジュールによって生成されたイベントに属するデータ。

クライアントがActionタイプのパケットを送信する際、`ActionID`というパラメータが含まれます。Asteriskから送信される応答の順序は予測できないため、`ActionID`を使用してアクションと応答を関連付けます。Eventパケットは2つの異なるコンテキストで使用されます。第一に、イベントはAsterisk内の変更（例：新しく作成されたチャネル、切断されたチャネル、キューへのエージェントのログイン/ログアウトなど）をクライアントに通知します。第二に、イベントはクライアントのアクションに対する応答を転送するために使用されます。

## ユーザーと権限の構成

AMIにアクセスするには、TCPポート（通常は5038）でリッスンしているTCP接続を確立する必要があります。`/etc/asterisk/manager.conf`ファイルを構成して、ユーザーアカウントと権限を作成する必要があります。権限には「read」、「write」、またはその両方の有限のセットがあります。これらの権限は以下で定義されます。

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

### AMIへのログイン

AMIにログインして認証するには、`manager.conf`で作成したユーザー名とアカウントを使用して、ログインタイプのアクションパケットを送信する必要があります。

```
Action:login
Username:admin
Secret:password
```

例：PHPを使用してAMIにログインする

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
?>
```

イベントを受信する必要がない場合は、"Events Off"を使用できます。

```
<?php
$socket = fsockopen("127.0.0.1","5038", $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");
fputs($socket, "Events: off\r\n\r\n");
?>
```

### アクションパケット

Asteriskにアクションパケットを送信する際、アクションの後にkey:valueペアを渡すことで、追加のキー（例：呼び出し番号）を提供できます。チャネル変数やグローバル変数をダイヤルプランに渡すことも可能です。

```
Action: <action type><CRLF>
<Key 1>: <Value 1><CRLF>
<Key 2>: <Value 2><CRLF>
Variable: <Variable 1>=<Value 1><CRLF>
Variable: <Variable 2>=<Value 2><CRLF>
...
<CRLF>
```

### アクションコマンド

CLI命令の`manager show commands`を使用して、利用可能なアクションを一覧表示できます。Asterisk 22では、コアコマンドセットには以下が含まれます（このリストは代表的なものであり、読み込まれたモジュールによって追加されます）：

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

特定のコマンドパラメータを知る必要がある場合は、`manager show command <command>`を使用してください。例：

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

### イベントパケット

イベントは、Asterisk内で何かが発生するたびにマネージャーインターフェース上で生成されます。チャネルの作成や状態の変化、2つのチャネルのブリッジングやブリッジ解除、登録の変更、キューメンバーの追加などです。各イベントは、ヘッダー`Event:`で始まる`Key: value`行のブロックです。

イベントの正確なセットは、読み込まれたモジュールとAsteriskのバージョンに依存するため、すぐに古くなるリストを再現するのではなく、実行中のサーバーに問い合わせて信頼できるセットを取得してください：

```
asterisk*CLI> manager show events             ; list every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; describe one event and its fields
```

例えば、通話のブリッジングは`BridgeCreate`、`BridgeEnter`、`BridgeLeave`、および`BridgeDestroy`イベントを通じて報告されます（`BridgeEnter`は「チャネルがブリッジに入ったときに発生」します）。古い`Link`/`Unlink`イベントはAsterisk 12で削除されました。

## Asterisk Gateway Interface

AGIは、Webサーバーで使用されるCGIに似たAsteriskへのゲートウェイインターフェースです。Perl、PHP、Pythonなどの高水準言語を使用してAsteriskの機能を拡張できます。CGIの主な用途はIVRの構築です。AGIには4つのタイプがあります。

- 通常のAGI：Asteriskのボックス内でプログラムを呼び出します。
- Fast AGI：TCPソケットを使用して別のサーバー上のAGIを呼び出します。
- EAGI：AGIからサウンドチャネルへのアクセスと制御を可能にします。
- DEADAGI：`hangup()`後でもチャネルへのアクセスを提供します。通常は`h`エクステンションで呼び出されます。

アプリケーション形式：

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

利用可能なAGIコマンドは、コマンド`agi show commands`を使用して表示できます（以下の出力は代表的なものです。Asterisk 22ではいくつかの追加コマンドが増えています）：

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

デバッグには、`agi debug`を使用します。

### AGIの使用

この例では、PHPのコマンドラインバージョンである`php-cli`を使用します。インストールされていない場合は`php-cli`をインストールしてください。PHP AGIスクリプトを使用するには、以下の手順に従います。ステップ1：すべてのAGIスクリプトは`/var/lib/asterisk/agi-bin`に配置されます。ステップ2：実行を許可するように権限を変更します。

```
chmod 755 *.php
```

ステップ3：シェルインターフェース（PHP固有）。スクリプトの最初の行は次のようである必要があります：

```
#!/usr/bin/php -q
<?php
```

ステップ4：I/Oチャネルを開く：

```
$stdin = fopen('php://stdin', 'r');
$stdout = fopen('php://stdout', 'w');
$stdlog = fopen('agi.log', 'w');
```

ステップ5：Asteriskの出力を管理する。AGIが呼び出されるたびに、Asteriskは情報セットを送信します。

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

送信された情報を保存します：

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

前のスクリプトは、`$agi`という名前の配列を作成します。利用可能なオプションは以下の通りです：

- `agi_request` – AGIファイル名
- `agi_channel` – AGIの発信元チャネル
- `agi_language` – 設定された言語
- `agi_type` – チャネルタイプ（例：SIP、DAHDI）
- `agi_uniqueid` – 一意の識別子
- `agi_callerid` – CallerID（例：Flavio <8590>）
- `agi_context` – 発信元のコンテキスト
- `agi_extension` – 呼び出されたエクステンション
- `agi_priority` – 優先度
- `agi_accountcode` – 発信元のアカウントコード

`agi_extensions`という名前の変数を呼び出すには、`$agi[agi_extensions]`を使用します。ステップ6：チャネルAGIを使用する。この時点で、Asteriskとの対話を開始できます。`fputs`コマンドを使用してAGIにコマンドを送信します。`echo`コマンドを使用することもできます。

```
fputs($stdout,"SAY NUMBER 4000 '79#' \n");
fflush($stdout);
```

引用符の使用に関する注意：

- AGIコマンドのオプションは省略できません
- 一部のオプションは引用符で囲む必要があります <escape digits>
- 一部のオプションは引用符で囲むべきではありません <digit string>
- 一部のオプションは両方の形式を使用できます
- 単一引用符を使用できます

ステップ7 – 変数を渡す。チャネル変数はAGI内で設定できますが、AGI内では使用できません。以下の例はAGI内では機能しません。

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/${EXTEN}"
```

以下の例は機能します：

```
SET VARIABLE MY_DIALCOMMAND "PJSIP/4000"
```

ステップ8：Asteriskの応答。Asteriskからの応答を検証するには、以下が必要です：

```
$msg  = fgets($stdin,1024);
fputs($stdlog,$msg . "\n");
```

ステップ9：ロックされた（ゾンビ）プロセスを終了する。何らかの理由でスクリプトが失敗した場合、プロセスがハングします。再度テストする前に、`killproc`コマンドを使用してクリーンアップしてください。

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

DeadAGIは、ライブチャネルがない場合に使用されます。通常、`h`エクステンションでDeadAGIを実行します。

### FASTAGI

Fast AGIは、入出力チャネルとしてTCPポート（デフォルトでは4573）を使用してAGIを実装します。FastAGIの形式は（`agi://`）です。例：

```
exten => 0800400001, 1, Agi(agi://192.168.0.1)
```

TCP接続が失われたり切断されたりすると、AGIは終了し、TCP接続が閉じられ、続いて通話が切断されます。このリソースは、外部サーバーでスクリプトを実行することでAsteriskサーバーのCPU負荷を軽減するのに役立ちます。FastAGIの詳細については、ソースコードディレクトリ（“agi/fastagi-test”ファイルを参照）で確認できます。Asterisk-Javaライブラリは、Java用のFastAGIサーバー実装を提供しています。詳細については、https://github.com/asterisk-java/asterisk-java を参照してください。

現代的なREST/WebSocketインターフェースであるARIについては、次章で解説します。

## ソースコードの変更

AsteriskはC言語（C++ではありません）で開発されています。Cプログラミングの指導は本書の範囲外です。興味がある場合は、https://docs.asterisk.org で関連ドキュメントを見つけることができます。そこには、Asteriskへのパッチの適用や作成方法に関する優れたヒントや、主にDoxygenソフトウェアによって生成されたAPIドキュメントが提供されています。Cプログラミングに精通している人にとって、アプリケーションのソースコードを変更することは、Asteriskを拡張するための最も強力（かつ危険）な方法となり得ます。

## まとめ

本章では、外部プログラムをAsterisk PBXにインターフェースする方法を学びました。まず、LinuxシェルからAsteriskコンソールにコマンドを渡す`asterisk –rx`から始めました。次に、ダイヤルプランから外部プログラムを呼び出すことができる`System()`アプリケーションについて学びました。AMIは、従来のPBXで一般的なCTIインターフェースに最も近いインターフェースです。ダイヤルプランからアプリケーションを呼び出すためにAGIを使用し、そのさまざまな種類（デッドチャネル用のDeadAGI、オーディオストリーミングを処理するためのEAGI、入出力インターフェースとしてTCPソケットを使用するFast AGI、そして同じAsteriskボックス内でスクリプトを呼び出して処理するための通常のAGI）について触れました。次章は、外部アプリケーションにAsteriskのチャネルとブリッジの完全な制御を与える、現代的なREST/WebSocket APIであるARIに捧げられています。

## クイズ

1. 次のうち、Asteriskのインターフェース方法ではないものはどれですか？
   - A. AMI
   - B. AGI
   - C. `asterisk -rx`
   - D. System()
   - E. External()
2. AMIはTCPソケットを介してAsteriskコマンドを渡すことを可能にし、このインターフェースはAsteriskの新規インストール時にデフォルトで有効になっています。
   - A. True
   - B. False
3. AMIはMD5チャレンジ/レスポンス認証を使用しているため、非常に安全です。
   - A. True
   - B. False
4. FastAGIを使用すると、ダイヤルプランからTCPソケット（通常はポート4573）を介して別のマシンの外部スクリプトを呼び出すことができます。
   - A. True
   - B. False
5. DeadAGIはアクティブなチャネルで使用されます。DAHDIチャネルでは使用できますが、SIPやIAXチャネルでは使用できません。
   - A. True
   - B. False
6. AGIはスクリプト言語としてPHPのみをサポートしています。
   - A. True
   - B. False
7. コマンド ___ は、利用可能なすべてのAGIコマンドを表示します。
8. コマンド ___ は、利用可能なすべてのAMIコマンドを表示します。
9. AMIアクションパケットにおいて、Asteriskから返される非同期の応答やイベントを、それをトリガーしたアクションと関連付けるために、クライアントが含めるヘッダーはどれですか？
   - A. `ActionID`
   - B. `Variable`
   - C. `Secret`
   - D. `Event`
10. ユーザーが`Originate`アクションを実行して発信通話を行うには、どのAMI `manager.conf`権限クラスが必要ですか？
    - A. `originate`
    - B. `verbose`
    - C. `log`
    - D. `reporting`

**回答:** 1 — E · 2 — B · 3 — B · 4 — A · 5 — B · 6 — B · 7 — `agi show commands` · 8 — `manager show commands` · 9 — A · 10 — A
