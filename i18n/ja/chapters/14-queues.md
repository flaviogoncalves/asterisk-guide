# Call Queues

Call queues（ACD：Automatic Call Distribution）は、顧客からの問い合わせに効率よく対応するためにますます重要になっています。自動呼分配装置（ACD）は、コスト削減、サービス向上、そして売上拡大に貢献します。なぜなら、呼分配は数日といった短期間ではなく、長年にわたってビジネスのあり方に影響を与えるからです。コールセンター環境において最も重要な要素は「人」であり、人こそが最も高コストなリソースです。エージェントの採用、トレーニング、モチベーション維持には時間と費用、そして忍耐が必要です。ACDを導入すれば、必要なエージェント数を正確に見積もり、優秀な担当者とそうでない担当者を管理し、通話フローを分析することで、エージェントの生産性を最大化できます。

## Objectives

本章を読み終えると、以下のことができるようになります。

- Call queuesを使用する理由と方法を理解する
- Call queuesの基本的な理論を理解する
- キューシステムをインストールおよび設定する

## How queues work?

Call queuesは決して新しい概念ではありません。インバウンドの通話フローが多い場合、適切に通話を分配するのは困難です。エージェントが数人しかいない場合を除き、すべてのエージェントの電話を同時に鳴らすグループ戦略はうまくいきません。しかし、Call queuesであれば、一度に1人の空いているエージェントに通話を転送し、空きがない場合は顧客を保留にして保留音（MOH）を流すことができます。キューは、通話を保持しながら、応答可能なエージェントを探すことで機能します。キューの最大の利点の1つは、通話の取りこぼしを防ぎつつ、統計情報を生成できることです。

![Call queue：1-800番号への着信がキューに入り、ACD戦略（ringall、rrmemory、leastrecent、priorityなど）によって空いているエージェントに分配される様子](../images/14-queues-fig01.png)

通常、Call queuesは次のように動作します。

- エージェントがキューにログインする。
- 着信がキューに入れられる。
- キューイング戦略を用いて、通話がエージェントに分配される。
- 発信者が待機している間、保留音が流れる。
- 発信者に対して、待ち時間などを通知するアナウンスを行うことができる。
- エージェントが通話に応答し、統計情報が生成される。

キューの主な用途はカスタマーサービスです。キューを使用すれば、エージェントが忙しいときでも通話の取りこぼしを防げます。キュー内の発信者数が増えていると判断した場合は、新しいエージェントをキューに追加できます。キューのもう一つの利点は、通話放棄率、平均通話時間、通話応答目標といった統計情報を取得できることです。これらの統計情報は、顧客により良いサービスを提供するために何人のエージェントを配置すべきかを判断するのに役立ちます。

### ACD architecture

ACDアーキテクチャは、キューとエージェントによって構成されます。1人のエージェントが同時に2つのキューに所属することも可能です。キューは、エージェント、チャネル、およびエージェントグループを持つことができます。

![ACDアーキテクチャ：各キュー（カスタマーサービス、インサイドセールス）に電話番号が紐付き、物理的なチャネルにバインドされたエージェントに通話を分配する](../images/14-queues-fig02.png)

## Queues

キューは queues.conf 設定ファイルで定義されます。エージェントとは、キューにログインしてメンバーとなる担当者のことです。エージェントは agents.conf ファイルで定義されます。キューシステムは多くのリリースを経て大幅に拡張されており、設定ファイルも大規模になっています。ここでは主要なパラメータのいくつかを説明します。General parameters

```
autofill=yes
```

以前のキューの動作はシリアルタイプでした。キューは、通話がディスパッチされるのを待ってから、次の通話を次のエージェントに送っていました。あるエージェントが通話に応答するのに15秒かかると、キュー内の他の通話はその応答が終わるまで待たなければなりませんでした。大量の通話を扱うキューでは、この動作は非効率的でした。新しい動作である autofill=yes は、通話の応答を待たずに並列で処理を行います。mixmonitor オプションを使用して、キュー内の通話を録音することもできます。このモードでは、通話は録音と同時にミキシングされます。

### Queue configuration file

キューは queues.conf ファイルで設定されます。図には、動作するキューの例を示しています。

![queues.confファイルの動作例。generalセクションと、戦略、サービスレベル、アナウンス、録音、メンバーを持つcustomerserviceキューが表示されている](../images/14-queues-fig03.png)

### Agents

エージェントは agents.conf ファイルで設定できます。エージェントはどのextensionからでもログインして通話を受けることができます。エージェントへのダイヤルは以下のように行います。

```
Dial(agent/<name>)
```

#### Agents

Agent 300

- コマンド `agent show all` を使用してエージェントのステータスを確認できます。
- agentlogin コマンドが実行されると、エージェントが現在のチャネルに関連付けられます。
- ユーザーは agentlogin アプリケーションを実行するextensionにダイヤルします。

![エージェント：ユーザーはagentloginアプリケーションを実行するextensionにダイヤルしてログインし、Agent 300を現在のチャネルにバインドする。エージェントのステータスは`agent show all`で確認可能](../images/14-queues-fig04.png)

エージェントは agents.conf ファイルで定義できます。

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

メンバーとは、キューに応答するアクティブなチャネルのことです。メンバーには、直接的なチャネル（PJSIP、DAHDI）や、通話を受ける前にログインするエージェントが含まれます。


### Strategies

通話は以下のいずれかの戦略に従ってメンバーに分配されます。

- ringall：誰かが応答するまで、利用可能なすべてのチャネルを鳴らす。
- leastrecent：最も最近まで通話していなかったメンバーに分配する。
- fewestcalls：通話数が最も少ないメンバーに分配する。
- random：ランダムなインターフェースを鳴らす。
- wrandom：ランダムなインターフェースを鳴らすが、メンバーのペナルティを重みとして計算に使用する。
- rrmemory：ラウンドロビン（メモリ付き）を使用する。前回のパスでどこまで進んだかを記憶する。
- rrordered：rrmemoryと同じだが、設定ファイル内のキューメンバーの順序が保持される。
- linear：queues.conf にリストされている順序でメンバーを鳴らす。動的メンバーの場合は、追加された順序に従う。

古い `roundrobin` 戦略は Asterisk 1.4 で非推奨となり削除されました。Asterisk 22 には存在しません。代わりに `rrmemory`（または `rrordered`）を使用してください。上記の戦略は、Asterisk 22 の `queues.conf` における `strategy` オプションで受け入れられる完全なセットです。

## Agents

エージェントはプロキシチャネルとして実装されます。これらはキュー内で使用できます。エージェントチャネルのもう一つの用途は、extensionのモビリティです。ユーザーはどの電話機からでもログインして通話を受けることができます。これにより、ユーザーはどの部屋でも自分のオフィスにすることができます。ダイヤルプランでは dial(agent/<name>) を使用してエージェントにダイヤルできます。エージェントは agents.conf ファイルで定義します。

![エージェントのモビリティ：ユーザーは任意の電話機を取り、ログイン用extensionにダイヤルし、エージェント番号とパスワードを入力する。agentlogin()が成功すると、エージェント（Agent 300）は通話を受けられる状態になり、CLIコマンド`agent show all`でステータスを確認できる](../images/14-queues-fig05.png)

### Agent Groups

エージェントグループを使用することもできます。この機能はACD戦略を考慮しません。通常は、すべてのエージェントを個別にリストする方が好ましいでしょう。エージェントグループに転送したい場合は、

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### The configuration file for agents

エージェントは agents.conf ファイルで定義されます。以下にファイルの動作例を示します。

![agents.confファイルの動作例：persistentagentsを含むgeneralセクション、デフォルトパラメータ（autologoff, ackcall, endcall, wrapuptime, musiconhold）を持つagentsセクション、および2つのエージェント定義（300と301）](../images/14-queues-fig06.png)

## ACD-related applications

Asteriskのキューシステムでは、ダイヤルプランでキューを実装するためにいくつかのアプリケーションが利用可能です。以下にその一部を紹介します。

### The application queue()

このアプリケーションは、queues.conf で定義された特定のCall queueに着信を入れます。オプション文字列には、以下の文字を0個以上含めることができます。通話の転送に加え、通話をパークして別のユーザーがピックアップすることも可能です。オプションのURLは、チャネルがサポートしていれば相手先に送信されます。オプションのAGIパラメータは、発信者がキューメンバーに接続された際に実行されるAGIスクリプトを設定します。タイムアウトを指定すると、指定秒数経過後にキューから外れます。このアプリケーションは、完了時に QUEUE ステータス変数を設定します。

![queue()アプリケーション：その構文`Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])`と利用可能な1文字オプション（d, h, H, n, i, r, t, T, w, W）](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### The application agentlogin()

このアプリケーションは、エージェントにシステムへのログインを要求します。常に -1 を返します。ログイン中、通話を受けるエージェントは新しい着信時にビープ音を聞きます。エージェントは '*' キーを押すことで通話を切断できます。

![agentlogin()アプリケーション：その構文`AgentLogin([AgentNo][|options])`と、ログイン確認のアナウンスを行わないサイレントログイン用の`s`オプション](../images/14-queues-fig08.png)

### The application addQueueMember()

このアプリケーションは、デバイス（例：PJSIP/3000）を動的にキューに追加します。デバイスが既に存在する場合はエラーを返します。

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### The application removeQueueMember()

このアプリケーションは、キューからデバイスを動的に削除します。デバイスがそのキューに属していない場合はエラーを返します。

```
RemoveQueueMember(queuename[|interface])
```

### Support applications and CLI commands

いくつかのアプリケーションとコンソールコマンドが、キューの運用を支援します。各アプリケーションの機能は以下の通りです。

![サポートアプリケーション（AddQueueMember, RemoveQueueMember）とCLIコマンド（agent show all, queue show, queue show <name>）。実行時にキューを管理するために使用する](../images/14-queues-fig09.png)

## Configuration tasks

以下の図は、動作するキューシステムを作成するための主要なタスクをまとめたものです。

![ACD設定タスク：(1)Call queueの作成（必須）、(2)エージェントパラメータの定義（オプション）、(3)エージェントの作成（オプション）、(4)ダイヤルプランへのキューの組み込み（必須）、(5)エージェント録音の設定（オプション）、(6)agent show allおよびqueue showによる確認（オプション）](../images/14-queues-fig10.png)

Step 1: Create the call queue queues.conf ファイル内：

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

Step 2: Define agent parameters agents.conf ファイル内：

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

Step 3: Create the agents agents.conf ファイル内：

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

Step 4: Insert the queue in the dial plan

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

通話はAsteriskの MixMonitor アプリケーションを使用して録音できます。（スタンドアロンの Monitor アプリケーションは Asterisk 22 で削除され、queues.conf の `monitor-type` オプションは MixMonitor のみを受け入れるようになりました。）録音はキューアプリケーション内から有効にでき、通話が実際に応答された時点から開始されます。成功した通話のみが録音され、MOHを聞いている間は録音されません。モニタリングを有効にするには、monitor-format を指定するだけです。この機能はデフォルトでは無効です。Set(MONITOR_FILENAME=<filename>) を使用して録音ファイル名を設定できます。そうでない場合は、

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

queues.conf ファイル内：

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## Queue operation

以下の例では、キューの使用方法を説明します。Step 1: Agent login 例：テレマーケティングキューのエージェントが電話を取り、#9000 にダイヤルします。エージェントは無効なログインメッセージを聞き、名前とパスワードを求められます。監査キューも同じ手順に従います。Step 2: Queue キューに入ると、エージェントは定義されていればMOHを聞きます。テレマーケティングキューに着信があると、エージェントはビープ音を聞き、その通話に接続されます。Step 3: Call ending エージェントが通話を終了したとき、以下の操作が可能です。

- '*' を押して切断し、キューに留まる。
- 電話を切断し、キューからログオフする。
- #8000 を押して監査用に通話を転送する。

## Advanced resources

Asteriskのキューシステムには、特定の顧客やエージェントに優先順位を付けたり、ユーザーメニューを有効にしたりするための高度な機能がいくつかあります。

### User menu

キューで待機中のユーザーに対して、1桁のextensionを使用したメニューを定義できます。このオプションを有効にするには、キュー設定ファイル queues.conf でコンテキストを定義します。

### Penalty

エージェントにはペナルティを設定できます。キューは、ペナルティ値が低いユーザーに優先的に通話を送ります。例えば、顧客がSusanの優しい声を好むことがわかっている場合、彼女に優先度0を割り当てることができます。逆に、経験の浅いUberというエージェントはカスタマーサービスにはあまり適していないため、優先度10を割り当てます。queues.conf ファイル内：

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority

キューは FIFO（先入れ先出し）モードで動作します。特別な顧客（プラチナ、ゴールド）に優先順位を付けたい場合は、差別化された優先度を設定できます。プラチナまたはゴールドの顧客の場合：

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

ブルーの顧客の場合：

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

アプリケーション `agentcallbacklogin()` は Digium によって Asterisk 1.4（2006年7月）で非推奨となり、Asterisk 22 では利用できません。推奨されるアプローチは、PJSIPインターフェースを使用して `AddQueueMember()` を使用し、コールバック形式のメンバーをキューに動的に追加することです。ドキュメント `queues-with-callback-members.txt` は、移行ガイダンスとして古い Asterisk `/doc` ディレクトリに含まれていました。

古い `chan_agent` チャネルドライバも同様に削除されました。その機能は `app_agent_pool` モジュールとして書き直され、Asterisk 22 では `AgentLogin()`、 `AgentRequest()`、および `AGENT()` ダイヤルプラン関数を提供しています（これらは現在も存在します。 `app_agent_pool.so` は標準の 22 ビルドに同梱されています）。しかし、現代のコールセンターでは、エージェントチャネルを完全にスキップし、エージェントのPJSIPデバイスを `AddQueueMember()`/`RemoveQueueMember()` で直接キューに追加する（`queues.conf` で静的に、またはダイヤルプランやAMIから動的に）のが標準的なパターンです。これはよりシンプルで、PJSIPのデバイス状態とクリーンに統合できるため、本書全体を通してこのアプローチを採用しています。

## Queue statistics

キューからのすべてのイベントは /var/log/asterisk/queue_log に記録されます。キューログの形式は、Asteriskドキュメントの /doc ディレクトリにある queuelog.txt に公開されています。以下に、記録される最も重要なイベントの一部を示します。

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

これらのイベントを処理する独自のユーティリティを構築するか、すぐに使える統計パッケージを使用できます。

- **QueueMetrics** (<https://www.queuemetrics.com/>) – 商用で積極的にメンテナンスされているパッケージであり、 `queue_log` を解析します。Asteriskコールセンター向けの最も完全なレポートツールの1つです。
- **自作ツール** – 上記の `queue_log` 形式は安定しており十分に文書化されているため、小さなスクリプト（Pythonなど）で解析し、イベントをデータベースやダッシュボードにフィードするのは簡単です。

`queue_log` を監視するよりもイベント駆動型のアプローチが必要な場合は、**Asterisk REST Interface (ARI)** および **AMI** の `QueueSummary`/`QueueStatus` アクションを使用することで、事後のログ解析ではなく、リアルタイムのキュー状態に基づいたライブキューダッシュボードやカスタム統合を構築できます。ARIは、Asterisk 22におけるこの種の作業のための、現代的でサポートされた統合インターフェースです。

## Summary

本章では、ACDの使用方法、そのアーキテクチャ、および設定方法を学びました。優先順位やペナルティといった高度な機能についても紹介しました。

## Quiz

1. `queues.conf` において有効なキュー分配戦略はどれですか（該当するものをすべて選択してください）。
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. キュー内からエージェントと顧客の会話を録音するには、 `queues.conf` ファイルで ___ オプションを設定します。
3. `queues.conf` にリストされている順序でメンバーを鳴らすのはどれですか（`strategy`）。
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. テレマーケティングの例でエージェントが通話を終了したとき、どのような操作が可能ですか（該当するものをすべて選択してください）。
   - A. `*` を押して切断し、キューに留まる
   - B. 電話を切ってキューから切断する
   - C. `#8000` を押して監査用に通話を転送する
   - D. `#` を押してすべてのキューから即座にログオフする
5. 動作するキューを作成するために *必須* のタスクはどれですか（該当するものをすべて選択してください）。
   - A. キューの作成
   - B. エージェントの作成
   - C. エージェントパラメータの設定
   - D. 録音の設定
   - E. ダイヤルプランへのキューの組み込み
6. Call queueでは、待機中に発信者がダイヤルできる1桁のメニューを提供できます。これは、キューの `queues.conf` セクションで ___ を定義することで有効になります。
   - A. agent
   - B. menu
   - C. context
   - D. application
7. サポートアプリケーションの `AddQueueMember()` および `RemoveQueueMember()` は、実行時にメンバーを追加または削除するために ___ で使用されます。
   - A. ダイヤルプラン
   - B. コマンドラインインターフェース
   - C. queues.conf
   - D. agents.conf
8. Asterisk 21 で chan_sip が削除されたため、静的キューメンバーは `SIP/1001` ではなく、___ のようなチャネルを参照する必要があります。
9. `wrapuptime` パラメータは、エージェントが通話を切断してからキューがそのエージェントに新しい通話を送るまでの最小時間です。
   - A. True
   - B. False
10. `Queue()` を呼び出す前に `QUEUE_PRIO` チャネル変数を設定することで、同じキュー内で発信者に高い順位を与えることができます。
    - A. True
    - B. False

**Answers:** 1 — A, C, D, E, F (roundrobin は rrmemory に置き換わり、存在しません) · 2 — `monitor-format` (キューからの録音は `monitor-format` を指定することで有効になります。 `monitor-type` は MixMonitor と Monitor を選択します) · 3 — C (linear) · 4 — A, B, C (`*` は切断して留まる操作。 `#` は全ログオフキーではありません) · 5 — A, E · 6 — C (`context` オプション) · 7 — A (ダイヤルプラン) · 8 — `PJSIP/1001` (任意の `PJSIP/` インターフェース) · 9 — True · 10 — True
