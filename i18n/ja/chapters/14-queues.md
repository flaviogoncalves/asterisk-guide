# Call Queues

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## Objectives

この章の終わりまでに、次のことができるようになります：

- コールキューを使用する理由と方法を理解する
- コールキューの基本理論を理解する
- キューシステムをインストールし、設定する

## キューはどのように機能するのか？

コールキューはまったくの新機能というわけではありません。大量のインバウンドコールがあると、適切にコールを分配するのは困難です。すべてのエージェントの電話が同時に鳴るグループ戦略は、エージェントが少数の場合を除いてうまく機能しません。一方、コールキューは毎回 1 人の利用可能なエージェントにだけコールを届け、エージェントがいないときは顧客を音楽付き保留にします。キューは、未使用のエージェントが見つかるまでコールを保持し続けます。キューの最大の利点のひとつは、コールを失うことを防ぎつつ、統計情報を生成できる点です。

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

通常、コールキューは次のように動作します：

- エージェントがキューにログインする。
- 着信コールがキューに入れられる。
- キューイング戦略が使用され、コールがエージェントに分配される。
- 発信者が待機している間、ミュージックオンホールドが再生される。
- 発信者に対して待ち時間を通知するアナウンスが行われることがある。
- エージェントがコールに応答し、統計が生成される。

キューの主な用途はカスタマーサービスです。キューを使用すると、エージェントが忙しいときにコールが失われるのを防げます。キュー内の発信者数が増えていると判断した場合は、エージェントを追加することができます。キューのもう一つの利点は、コール放棄率、平均通話時間、応答目標時間といった統計を取得できることです。これらの統計は、顧客により良いサービスを提供するために必要なエージェント数を判断するのに役立ちます。

### ACD アーキテクチャ

ACD アーキテクチャはキューとエージェントで構成されます。1 人のエージェントが同時に 2 つのキューに所属することができます。キューはエージェント、チャネル、エージェントグループを持つことができます。

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

## エージェント

エージェントはプロキシチャンネルとして実装されています。キュー内で使用することができます。エージェントチャンネルの別の用途はエクステンションモビリティです。ユーザーは任意の電話でログインし、その電話への着信を受け取ることができます。これにより、ユーザーはどの部屋に行ってもそこをオフィスにすることができます。ダイヤルプランで `dial(agent/<name>)` を使用してエージェントにダイヤルできます。エージェントは `agents.conf` ファイルで定義します。

![エージェントモビリティ: ユーザーが任意の電話を取り、ログインエクステンションをダイヤルし、エージェント番号とパスワードを渡す。`agentlogin()` が成功するとエージェント (Agent 300) が通話受信可能になり、CLI コマンド `agent show all`でステータスを確認できる](../images/14-queues-fig05.png)

### エージェントグループ

エージェントグループを使用することもできます。この機能は ACD ストラテジーを考慮しません。通常はすべてのエージェントを個別にリストする方が好まれます。エージェントグループへ転送したい場合は `queues.conf` を使用できます。

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### エージェント用設定ファイル

エージェントは `agents.conf` ファイルで定義されます。以下はそのファイルの動作例です。

![agents.conf ファイルの動作例: 永続エージェントを含む general セクション、デフォルトパラメータ (autologoff, ackcall, endcall, wrapuptime, musiconhold) を持つ agents セクション、そして 2 つのエージェント定義 (300 と 301)](../images/14-queues-fig06.png)

## ACD関連アプリケーション

Asterisk のキューシステムは、ダイヤルプランでキューを実装するためにいくつかのアプリケーションを提供します。以下にその一部を示します。

### アプリケーション queue()

このアプリケーションは、incoming call を `queues.conf` で定義された特定のコールキューに入列させます。オプション文字列には、以下の図に示すように 0 個以上の単一文字オプションを含めることができます。コールの転送に加えて、コールをパークし、別のユーザーがピックアップすることも可能です。オプションの URL は、チャネルがサポートしていれば呼び出し側に送信されます。オプションの AGI パラメータは、キューメンバーに接続されたときに呼び出し側チャネルで実行される AGI スクリプトを設定します。タイムアウトは、指定された秒数後にキューが失敗として終了することを引き起こし、各タイムアウトとリトライサイクルの間でチェックされます。このアプリケーションは完了時に QUEUE ステータス変数を設定します。

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### アプリケーション agentlogin()

このアプリケーションはエージェントにシステムへのログインを要求します。常に -1 を返します。ログイン中は、エージェントが新しい呼び出しを受けるとビープ音が鳴ります。エージェントは `*` キーを押すことで通話を切り上げることができます。

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### アプリケーション addQueueMember()

このアプリケーションはデバイス（例: PJSIP/3000）をキューに動的に追加します。デバイスがすでに存在する場合はエラーを返します。

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### アプリケーション removeQueueMember()

このアプリケーションはデバイスをキューから動的に削除します。デバイスがキューに属していない場合はエラーを返します。

```
RemoveQueueMember(queuename[|interface])
```

### サポートアプリケーションと CLI コマンド

いくつかのアプリケーションとコンソールコマンドは、キューの操作を支援することができます。以下に各アプリケーションの機能を概説します。

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

以下の図は、動作するキューシステムを作成するための主要なタスクをまとめたものです。

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

## キューの操作

以下の例はキューの使用方法を説明します。

1. エージェントのログイン。例：テレマーケティングキューのエージェントが電話を取り、#9000 をダイヤルします。エージェントは無効なログインメッセージを聞き、名前とパスワードの入力を求められます。監査キューも同じ手順です。
2. キュー。キューに入ると、エージェントは定義されていればMOHを聞きます。テレマーケティングキューに着信があると、エージェントはビープ音を聞き、その通話に接続されます。
3. 通話終了。エージェントが通話を終了したとき、以下が可能です：
   - ‘*’ を押して切断し、キューに残る。
   - 電話を切断し、キューからも切断される。
   - #8000 を押して通話を監査用に転送する。

## Advanced resources
Asterisk のキューシステムには、特定の顧客やエージェントを優先させる高度な機能や、ユーザーメニューを有効にする機能があります。

### User menu
キュー待ち中のユーザー向けに、1 桁の内線番号を使ったメニューを定義できます。このオプションを有効にするには、`queues.conf` のキュー設定でコンテキストを定義します。

### Penalty
エージェントにペナルティを設定できます。キューはペナルティ値が低いユーザーに先にコールを送ります。たとえば、顧客がスーザンの柔らかい声を好むことが分かっているので、彼女に優先度 0 を割り当てることができます。逆に、経験が浅く顧客サービスにあまり適さないエージェントの Uber には、優先度 10 を割り当てます。`queues.conf` ファイルでは次のように記述します。

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority
キューは FIFO（先入れ先出し）モードで動作します。特別な顧客（プラチナ、ゴールド）に優先順位を付けたい場合は、差別化された優先度を設定できます。プラチナまたはゴールド顧客の場合:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

ブルー顧客の場合:

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

The application `agentcallbacklogin()` was deprecated by Digium in Asterisk 1.4 (July 2006) and is no longer available in Asterisk 22. The recommended approach is to use `AddQueueMember()` with a PJSIP interface to dynamically add callback-style members to a queue. The document `queues-with-callback-members.txt` was included in older Asterisk `/doc` directories for migration guidance.

The old `chan_agent` channel driver was likewise removed; its functionality was rewritten as the `app_agent_pool` module, which is what provides `AgentLogin()`, `AgentRequest()` and the `AGENT()` dialplan function in Asterisk 22 (these are still present — `app_agent_pool.so` ships with a stock 22 build). For modern call centers, however, the standard pattern is to skip agent channels entirely and add the agent's PJSIP device directly to the queue with `AddQueueMember()`/`RemoveQueueMember()` (statically in `queues.conf`, or dynamically from the dialplan or AMI). This is simpler, integrates cleanly with PJSIP device state, and is the approach used throughout this chapter.

## キュー統計

キューからのすべてのイベントは /var/log/asterisk/queue_log に記録されます。キューログのフォーマットは Asterisk ドキュメントの /doc ディレクトリにある queuelog.txt に掲載されています。以下は記録される最も重要なイベントの一部です。

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

これらのイベントを処理する独自のユーティリティを作成することも、既成の統計パッケージを使用することもできます。

- **QueueMetrics** (<https://www.queuemetrics.com/>) – 商用で、積極的にメンテナンスされているパッケージで、`queue_log`を解析し、Asterisk コールセンター向けの最も完全なレポートツールの一つです。
- **Roll your own** – 上記の`queue_log`フォーマットは安定しており十分に文書化されているため、Python などの小さなスクリプトで簡単に解析し、イベントをデータベースやダッシュボードに流し込むことができます。

`queue_log`をテイルするよりもイベント駆動型のアプローチを求める場合、**Asterisk REST Interface (ARI)** と **AMI** `QueueSummary`/`QueueStatus` アクションを使用すると、リアルタイムのキュー状態に基づくライブキューダッシュボードやカスタム統合を構築できます。ARI は Asterisk 22 におけるこの種の作業向けに推奨される最新の統合インターフェースです。

## 要約

この章では、ACD の使用方法、そのアーキテクチャ、および設定方法を学びました。また、優先度やペナルティなどの高度な機能も紹介しました。

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
