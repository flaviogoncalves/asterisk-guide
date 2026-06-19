# Call Queues

Call queues（ACD：Automatic Call Distribution、自動呼分配）は、顧客からの電話に効率的に対応するためにますます重要になっています。自動呼分配システムは、コスト削減、サービス向上、売上拡大に寄与します。なぜなら、呼分配はビジネスの仕組みそのものに影響を与えるためであり、それは数日といった短期間ではなく、長年にわたって効果を発揮するからです。コールセンター環境において最も重要な要素は「人」であり、人こそが最も高価なリソースです。エージェントの採用、トレーニング、モチベーション維持には時間と費用、そして忍耐が必要です。ACDを導入することで、必要なエージェント数を正確に算出し、優秀な担当者とそうでない担当者を管理し、通話フローを分析することで、エージェントの生産性を最大化できます。

## 目標

この章を読み終えると、以下のことができるようになります。

- なぜ、どのようにCall queuesを使用するのかを理解する
- Call queuesの基本的な理論を理解する
- キューシステムをインストールし、設定する

## キューの仕組み

Call queuesは決して新しい概念ではありません。インバウンドの通話フローが多い場合、適切に通話を分配するのは困難です。すべてのエージェントの電話を同時に鳴らすグループ戦略は、エージェントの数が少ない場合を除き、うまく機能しません。しかし、Call queueは、通話が来るたびに空いている単一のエージェントに通話を転送し、エージェントが空いていない場合は顧客を保留にして保留音（Music on hold）を流します。キューは、通話を保持しながら、応答可能なエージェントを探すことで機能します。キューの最大の利点の一つは、通話の取りこぼしを防ぎつつ、統計情報を生成できることです。

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

通常、Call queueは以下のように動作します。

- エージェントがキューにログインする。
- 着信がキューに入れられる。
- 通話を分配するためのキューイング戦略が使用され、エージェントに通話が送られる。
- 発信者が待機している間、保留音が流れる。
- 発信者に対して、待ち時間を通知するアナウンスを行うことができる。
- エージェントが通話に応答し、統計情報が生成される。

キューの主な用途はカスタマーサービスです。キューを使用することで、エージェントが忙しいときでも通話の取りこぼしを防ぐことができます。キュー内の発信者数が増えていると判断した場合は、新しいエージェントをキューに追加できます。キューのもう一つの利点は、通話放棄率、平均通話時間、通話応答目標などの統計情報を取得できることです。これらの統計情報は、顧客により良いサービスを提供するために何人のエージェントを配置すべきかを判断するのに役立ちます。

### ACDアーキテクチャ

ACDアーキテクチャは、キューとエージェントによって構成されます。一人のエージェントが同時に二つのキューに所属することも可能です。キューは、エージェント、チャネル、エージェントグループを持つことができます。

![ACD architecture: each queue (Customer Service, Inside Sales) is fed by a phone number and delivers calls to agents, who are in turn bound to physical channels](../images/14-queues-fig02.png)

## Queues

キューは queues.conf 設定ファイルで定義されます。エージェントとは、ログインしてキューのメンバーとなる担当者のことです。エージェントは agents.conf ファイルで定義されます。キューシステムは多くのリリースを経て大幅に拡張されており、設定ファイルも大規模になっています。ここでは主要なパラメータのいくつかを説明します。全般パラメータ

```
autofill=yes
```

以前のキューの動作はシリアルタイプでした。キューは、通話がディスパッチされるまで待機してから、次の通話を次のエージェントに送信していました。エージェントが通話に応答するのに15秒かかると、キュー内の他の通話はその応答が終わるまで待たなければなりませんでした。大量の通話を扱うキューでは、この動作は非効率的でした。新しい動作である autofill=yes は、通話が応答されるのを待たずに並列で処理を行います。mixmonitor オプションを使用して、キュー内の通話を録音することもできます。このモードでは、通話は録音と同時にミックスされます。

### キュー設定ファイル

キューは queues.conf ファイルで設定されます。図には、動作するキューの例を示しています。

![A working example of the queues.conf file, showing the general section and a customerservice queue with strategy, service level, announcements, recording, and members](../images/14-queues-fig03.png)

### エージェント

エージェントは agents.conf ファイルで設定できます。エージェントはどのextensionからでもログインして通話を受けることができます。エージェントにダイヤルするには以下を使用します。

```
Dial(agent/<name>)
```

#### エージェント

Agent 300

- コマンド `agent show all` を使用してエージェントのステータスを確認できます。
- agentlogin コマンドが実行されると、エージェントは現在のチャネルに関連付けられます。
- ユーザーは agentlogin アプリケーションを実行するextensionにダイヤルします。

![Agents: a user logs in by dialing an extension that runs the agentlogin application, which binds Agent 300 to the current channel; you can check agent status with `agent show all`](../images/14-queues-fig04.png)

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

### メンバー

メンバーとは、キューに応答するアクティブなチャネルのことです。メンバーには、直接的なチャネル（PJSIP、DAHD）や、通話を受ける前にログインするエージェントが含まれます。


### 戦略

通話は以下のいずれかの戦略に従ってメンバーに分配されます。

- ringall: 誰かが応答するまで、利用可能なすべてのチャネルを鳴らします。
- leastrecent: 最も最近まで通話していなかったメンバーに分配します。
- fewestcalls: 最も通話回数が少ないメンバーに分配します。
- random: ランダムなインターフェースを鳴らします。
- wrandom: ランダムなインターフェースを鳴らしますが、メンバーのペナルティを重みとして計算に使用します。
- rrmemory: ラウンドロビン（メモリ付き）を使用します。前回のパスでどこまで通話を回したかを記憶しています。
- rrordered: rrmemory と同じですが、設定ファイル内のキューメンバーの順序が保持されます。
- linear: queues.conf にリストされている順序でメンバーを鳴らします。動的メンバーの場合は、追加された順序に従います。

> **[2nd-ed note]** `roundrobin` 戦略は初期のAsteriskリリースで `rrmemory` に置き換えられ、現在は利用できません。以前の版のテキストに記載されている場合は、戦略リストから削除してください。上記に記載されたすべての戦略は、Asterisk 22で存在することが確認されています。

## エージェント

エージェントはプロキシチャネルとして実装されています。これらはキュー内で使用できます。エージェントチャネルのもう一つの用途は、extensionのモビリティです。ユーザーはどの電話からでもログインして通話を受けることができます。これにより、ユーザーはどの部屋にいてもそこをオフィスにすることができます。dialplan内で dial(agent/<name>) を使用してエージェントにダイヤルできます。エージェントは agents.conf ファイルで定義します。

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### エージェントグループ

エージェントグループを使用することもできます。この機能はACD戦略を考慮しません。通常は、すべてのエージェントを個別にリストする方が好ましいでしょう。エージェントグループに転送したい場合は、

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### エージェントの設定ファイル

エージェントは agents.conf ファイルで定義されます。以下にファイルの動作例を示します。

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## ACD関連アプリケーション

Asteriskのキューシステムでは、dialplan内でキューを実装するためにいくつかのアプリケーションが利用可能です。以下にその一部を紹介します。

### queue() アプリケーション

このアプリケーションは、queues.conf で定義された特定のCall queueに着信を入れます。オプション文字列には、以下の文字を0個以上含めることができます。通話の転送に加え、通話をパークして別のユーザーがピックアップすることも可能です。オプションのURLは、チャネルがサポートしていれば被呼者に送信されます。オプションのAGIパラメータは、キューメンバーに接続された時点で発信者のチャネルで実行されるAGIスクリプトを設定します。タイムアウトを指定すると、各タイムアウトと再試行サイクルの間でチェックが行われ、指定された秒数後にキューが失敗します。このアプリケーションは、完了時に QUEUE ステータス変数を設定します。

![The queue() application: its syntax `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### agentlogin() アプリケーション

このアプリケーションは、エージェントにシステムへのログインを要求します。常に -1 を返します。ログイン中、新しい通話が来るとエージェントはビープ音を聞きます。エージェントは '*' キーを押すことで通話を切断できます。

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### addQueueMember() アプリケーション

このアプリケーションは、デバイス（例: PJSIP/3000）をキューに動的に追加します。デバイスが既に存在する場合はエラーを返します。

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### removeQueueMember() アプリケーション

このアプリケーションは、デバイスをキューから動的に削除します。デバイスがそのキューに属していない場合はエラーを返します。

```
RemoveQueueMember(queuename[|interface])
```

### サポートアプリケーションとCLIコマンド

いくつかのアプリケーションとコンソールコマンドが、キューの運用を支援します。以下に各アプリケーションの役割を概説します。

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## 設定タスク

以下の図は、動作するキューシステムを作成するための主要なタスクをまとめたものです。

![The ACD configuration tasks: (1) create the call queue (required), (2) define agent parameters (optional), (3) create agents (optional), (4) put the queue in the dial plan (required), (5) configure agent recording (optional), and (6) verify with agent show all and queue show (optional)](../images/14-queues-fig10.png)

ステップ 1: Call queueを作成する（queues.conf ファイル内）:

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

ステップ 2: エージェントパラメータを定義する（agents.conf ファイル内）:

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

ステップ 3: エージェントを作成する（agents.conf ファイル内）:

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

ステップ 4: dialplanにキューを挿入する

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

### キュー録音の設定

通話はAsteriskの MixMonitor アプリケーションを使用して録音できます。（スタンドアロンの Monitor アプリケーションはAsterisk 22で削除されたため、queues.conf の `monitor-type` オプションは MixMonitor のみを受け付けます。）録音はキューアプリケーション内から有効にでき、通話が実際に応答された時点から開始されます。成功した通話のみが録音され、MOHを聞いている間は録音されません。モニタリングを有効にするには、monitor-format を指定するだけです。この機能は、指定しない限り無効です。Set(MONITOR_FILENAME=<filename>) を使用して録音ファイル名を設定できます。設定しない場合は、

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

queues.conf ファイル内:

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## キューの運用

以下の例では、キューの使用方法を説明します。ステップ 1: エージェントログイン 例: テレマーケティングキューのエージェントが電話を取り、#9000をダイヤルします。エージェントは無効なログインメッセージを聞き、名前とパスワードを求められます。監査キューも同様の手順に従います。ステップ 2: キュー キューに入ると、エージェントは定義されていればMOHを聞きます。テレマーケティングキューに着信があると、エージェントはビープ音を聞き、その通話に接続されます。ステップ 3: 通話終了 エージェントが通話を終了したとき、以下の操作が可能です。

- '*' を押して切断し、キューに留まる。
- 電話を切断し、キューからログオフする。
- #8000 を押して、監査のために通話を転送する。

## 高度なリソース

Asteriskのキューシステムには、特定の顧客やエージェントの優先順位付けや、ユーザーメニューの有効化など、高度な機能がいくつかあります。

### ユーザーメニュー

キューで待機中のユーザーに対して、1桁のextensionを使用したメニューを定義できます。このオプションを有効にするには、キュー設定ファイル queues.conf で context を定義します。

### ペナルティ

エージェントにはペナルティを設定できます。キューは、ペナルティ値が低いユーザーに優先的に通話を送ります。例えば、顧客がSusanの優しい声を好むことがわかっている場合、彼女に優先度0を割り当てることができます。一方、経験の浅いUberというエージェントはカスタマーサービスにはあまり適していないため、優先度10を割り当てます。queues.conf ファイル内:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### 優先度

キューはFIFO（先入れ先出し）モードで動作します。特別な顧客（プラチナ、ゴールド）に優先順位を与えたい場合は、差別化された優先度を設定できます。プラチナまたはゴールドの顧客の場合:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

ブルーの顧客の場合:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## agentcallbacklogin() アプリケーションの削除

`agentcallbacklogin()` アプリケーションはAsterisk 1.4（2006年7月）で非推奨となり、Asterisk 22では利用できません。推奨されるアプローチは、PJSIPインターフェースを使用して `AddQueueMember()` を使用し、コールバック形式のメンバーをキューに動的に追加することです。移行ガイダンスについては、古いAsteriskの `/doc` ディレクトリに含まれていた `queues-with-callback-members.txt` ドキュメントを参照してください。

> **[2nd-ed note]** `chan_agent` チャネルドライバ（app_agent_pool）がAsterisk 22でもエージェントコールバック動作の推奨メカニズムであるか、あるいは `AddQueueMember()`/`RemoveQueueMember()` を使用した直接的なPJSIPメンバーが標準パターンであるかを確認してください。

## キュー統計

キューからのすべてのイベントは /var/log/asterisk/queue_log に記録されます。キューログの形式は、Asteriskドキュメントの /doc ディレクトリにある queuelog.txt ドキュメントで公開されています。以下に、記録される最も重要なイベントの一部を示します。

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

これらのイベントを処理する独自のユーティリティを構築するか、すぐに使える統計パッケージを使用できます。voip.schoolでは以下の2つのユーティリティをテストしました。

- Qlog analyzer (http://www.micpc.com/qloganalyzer/) – 優れたオープンソースパッケージ
- Queue metrics (http://queuemetrics.com/) – キュー統計のための最も完全なパッケージの一つ

> **[2nd-ed note]** 上記のサードパーティ製統計ツールが、現在もメンテナンスされており、Asterisk 22の queue_log 形式と互換性があるかを確認してください。カスタムキューレポート統合を構築するための現代的な代替手段として、Asterisk REST Interface (ARI) への参照を追加することを検討してください。

## まとめ

この章では、ACDの使用方法、そのアーキテクチャ、および設定方法を学びました。優先度やペナルティといった高度な機能についても紹介しました。

## クイズ

1. `queues.conf` において有効なキュー分配戦略はどれですか（該当するものすべてを選択してください）?
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. キュー内からエージェントと顧客の会話を録音するには、___ ファイルで ___ オプションを設定します。
3. `queues.conf` にリストされている順序でメンバーを鳴らすのはどれですか?
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. テレマーケティングの例でエージェントが通話を終了したとき、どのようなアクションを取れますか（該当するものすべてを選択してください）?
   - A. `*` を押して切断し、キューに留まる
   - B. 電話を切ってキューから切断する
   - C. `#8000` を押して監査のために通話を転送する
   - D. `#` を押してすべてのキューから即座にログオフする
5. 動作するキューを作成するために*必須*のタスクはどれですか（該当するものすべてを選択してください）?
   - A. キューを作成する
   - B. エージェントを作成する
   - C. エージェントパラメータを設定する
   - D. 録音を設定する
   - E. dialplanにキューを入れる
6. Call queueでは、待機中に発信者がダイヤルできる1桁のメニューを提供できます。これは、キューの `queues.conf` セクションで ___ を定義することで有効になります。
   - A. agent
   - B. menu
   - C. context
   - D. application
7. サポートアプリケーションの `AddQueueMember()` と `RemoveQueueMember()` は、実行時にメンバーを追加または削除するために ___ で使用されます。
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. Asterisk 21で chan_sip が削除されたため、静的なキューメンバーは `SIP/1001` ではなく、___ のようなチャネルを参照する必要があります。
9. `wrapuptime` パラメータは、エージェントが通話を切断してから、キューがそのエージェントに新しい通話を送るまでの最小時間です。
   - A. True
   - B. False
10. `Queue()` を呼び出す前に `QUEUE_PRIO` チャネル変数を設定することで、同じキュー内で発信者により高い順位を与えることができます。
    - A. True
    - B. False

**回答:** 1 — A, C, D, E, F (roundrobinはrrmemoryに置き換えられ、存在しません) · 2 — `monitor-format` (キューからの録音は `monitor-format` を指定することで有効になります; `monitor-type` は MixMonitor と Monitor を選択します) · 3 — C (linear) · 4 — A, B, C (`*` は切断して留まる; `#` は全ログオフキーではありません) · 5 — A, E · 6 — C (`context` オプション) · 7 — A (dial plan) · 8 — `PJSIP/1001` (任意の `PJSIP/` インターフェース) · 9 — True · 10 — True
