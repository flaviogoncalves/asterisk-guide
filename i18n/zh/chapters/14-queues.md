# Call Queues

呼叫队列（Call Queues），也称为 ACD（自动呼叫分配），对于高效应答客户呼叫正变得越来越重要。自动呼叫分配器可以帮助降低成本、提升服务质量并增加销售额，因为呼叫分配器会影响企业的运作方式——这不仅是几天的事，而是长达数年的影响。在呼叫中心环境中，首要因素是人员；他们是最昂贵的资源。招聘、培训和激励坐席需要时间、金钱和耐心。借助 ACD，您可以通过精确计算所需的坐席数量、控制优秀与不称职的接待员，以及分析呼叫流程，从而最大限度地提高坐席的生产力。

## 目标

读完本章后，您应该能够：

- 理解为什么要使用呼叫队列以及如何使用它们
- 理解呼叫队列的基本理论
- 安装并配置队列系统

## 队列是如何工作的？

呼叫队列并不是什么新鲜事物。当您有大量的呼入呼叫流时，很难适当地分配呼叫。除非您只有少数几个坐席，否则使用那种让所有坐席电话同时响铃的组策略似乎并不奏效。然而，呼叫队列每次只会将呼叫发送给单个可用的坐席，并在没有可用坐席时让客户保持在等待状态并播放保持音乐。队列的工作原理是在寻找空闲坐席来应答呼叫的同时保持该呼叫。队列最大的好处之一是避免丢失呼叫，同时还能提供生成统计数据的可能性。

![呼叫队列：呼入的 1-800 呼叫进入队列，ACD 策略（ringall、rrmemory、leastrecent、priority 等）将其分配给可用的坐席](../images/14-queues-fig01.png)

通常，呼叫队列的工作方式如下：

- 坐席登录到队列。
- 呼入呼叫进入队列。
- 使用队列分配策略将呼叫发送给坐席。
- 当呼叫者等待时，播放保持音乐。
- 可以向呼叫者发布公告，通知他们等待时间。
- 坐席应答呼叫并生成统计数据。

队列的主要应用是客户服务。使用队列时，您可以避免在坐席忙碌时丢失呼叫。如果您发现队列中的呼叫者数量在增加，可以向队列添加新坐席。队列的另一个优势是，您现在可以获得诸如呼叫放弃率、平均通话时长和呼叫应答目标等统计数据。这些统计数据将帮助您确定需要多少坐席来为客户提供更好的服务。

### ACD 架构

ACD 架构由队列和坐席组成。一个坐席可以同时处于两个队列中。一个队列可以拥有坐席、通道和坐席组。

![ACD 架构：每个队列（客户服务、内部销售）由一个电话号码提供呼叫，并将呼叫分发给坐席，坐席进而绑定到物理通道](../images/14-queues-fig02.png)

## 队列

队列在 queues.conf 配置文件中定义。坐席是登录并成为队列成员的接待员。坐席在 agents.conf 文件中定义。队列系统在多个版本中得到了显著发展，使得配置文件变得非常庞大。我们将解释一些主要的参数。通用参数

```
autofill=yes
```

队列的旧行为是串行类型。队列在发送下一个呼叫给下一个坐席之前，会等待呼叫被分发。如果一个坐席需要 15 秒来应答一个呼叫，队列中的其他呼叫必须等待直到该呼叫被应答。对于高容量队列，这种行为效率低下。新的行为 autofill=yes 不会等待呼叫被应答，而是并行工作。您可以使用选项 mixmonitor 记录队列中的呼叫。在此模式下，呼叫会被同时记录和混合。

### 队列配置文件

队列在 queues.conf 文件中配置。在图中，您将找到一个有效的队列示例。

![queues.conf 文件的有效示例，显示了通用部分以及一个带有策略、服务级别、公告、录音和成员的 customerservice 队列](../images/14-queues-fig03.png)

### 坐席

您可以在 agents.conf 文件中配置您的坐席。坐席可以从任何 extension 登录以接收呼叫。您可以使用以下方式拨打坐席：

```
Dial(agent/<name>)
```

#### 坐席

Agent 300

- 您可以使用命令 `agent show all` 检查坐席的状态
- 执行 agentlogin 命令，坐席将与当前通道关联。
- 用户拨打带有 agentlogin 应用程序的 extension。

![坐席：用户通过拨打运行 agentlogin 应用程序的 extension 进行登录，该应用程序将 Agent 300 绑定到当前通道；您可以使用 `agent show all` 检查坐席状态](../images/14-queues-fig04.png)

您可以在 agents.conf 文件中定义坐席

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

### 成员

成员是响应队列的活动通道。成员可以是直接通道（PJSIP、DAHDI）或在接收呼叫前登录的坐席。


### 策略

呼叫根据以下策略之一在成员之间分配：

- ringall：让所有可用通道响铃，直到有人应答。
- leastrecent：分配给最近最少通话的成员。
- fewestcalls：分配给通话次数最少的成员。
- random：随机响铃接口。
- wrandom：随机响铃接口，但在计算指标时将成员的惩罚值（penalty）作为权重。
- rrmemory：使用带记忆的轮询（round robin）；它会记住上次呼叫结束时的位置。
- rrordered：与 rrmemory 相同，但保留了配置文件中队列成员的顺序。
- linear：按照 queues.conf 中列出的顺序响铃成员；对于动态成员，按照添加的顺序。

较旧的 `roundrobin` 策略早在 Asterisk 1.4 中就被弃用并移除；它在 Asterisk 22 中已不存在。请改用 `rrmemory`（或 `rrordered`）。上述策略是 Asterisk 22 `queues.conf` 中 `strategy` 选项所接受的完整集合。

## 坐席

坐席作为代理通道实现。它们可以在队列内部使用。坐席通道的另一个用途是 extension 移动性。用户可以使用任何电话登录并接收其呼叫。这允许用户去任何房间将其作为办公室。您可以在 dialplan 中使用 dial(agent/<name>) 拨打坐席。您在 agents.conf 文件中定义坐席。

![坐席移动性：用户拿起任何电话，拨打登录 extension，并输入坐席号码和密码；agentlogin() 成功后，该坐席（Agent 300）即可接听呼叫，您可以使用 CLI 命令 `agent show all` 检查状态](../images/14-queues-fig05.png)

### 坐席组

您可以选择使用坐席组。此功能不考虑 ACD 策略。您可能更倾向于单独列出所有坐席。如果您想转接到坐席组，您

```
can use queues.conf:
member=>agent/@1 ;any agent in group 1
member=>agent/:1,1 ;any agent in group 1, wait for first available, ;do not
use agent groups.
```

### 坐席配置文件

坐席在 agents.conf 文件中定义。以下是该文件的一个有效示例。

![agents.conf 文件的有效示例：包含 persistentagents 的通用部分，包含默认参数（autologoff、ackcall、endcall、wrapuptime、musiconhold）的 agents 部分，以及两个坐席定义（300 和 301）](../images/14-queues-fig06.png)

## ACD 相关应用程序

Asterisk 队列系统提供了多个应用程序，用于在 dialplan 中实现队列。下面我们展示其中一些。

### 应用程序 queue()

此应用程序将呼入呼叫排入 queues.conf 中定义的特定呼叫队列。选项字符串可能包含零个或多个以下字符：除了转接呼叫外，呼叫还可以被驻留，然后由另一个用户接起。如果通道支持，可选的 URL 将发送给被叫方。可选的 AGI 参数将设置一个 AGI 脚本，在呼叫方连接到队列成员后在其通道上执行。超时将导致队列在指定的秒数后失败，并在每次超时和重试周期之间进行检查。此应用程序在完成后设置 QUEUE 状态变量：

![queue() 应用程序：其语法 `Queue(queuename[|options[|URL][|announceoverride][|timeout][|AGI]])` 以及可用的单字母选项（d, h, H, n, i, r, t, T, w, W）](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### 应用程序 agentlogin()

此应用程序要求坐席登录到系统。它总是返回 -1。登录后，当有新呼叫进入时，接收呼叫的坐席会听到一声蜂鸣音。坐席可以通过按 * 键挂断呼叫。

![agentlogin() 应用程序：其语法 `AgentLogin([AgentNo][|options])` 以及用于静默登录（不宣布登录确认）的 `s` 选项](../images/14-queues-fig08.png)

### 应用程序 addQueueMember()

此应用程序动态地将设备（例如 PJSIP/3000）添加到队列中。如果设备已存在，它将返回错误。

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### 应用程序 removeQueueMember()

此应用程序动态地从队列中移除设备。如果设备不属于该队列，它将返回错误。

```
RemoveQueueMember(queuename[|interface])
```

### 支持应用程序和 CLI 命令

一些应用程序和控制台命令能够帮助处理队列。以下概述了每个应用程序的功能：

![支持应用程序（AddQueueMember, RemoveQueueMember）和 CLI 命令（agent show all, queue show, queue show <name>），用于在运行时管理队列](../images/14-queues-fig09.png)

## 配置任务

下图总结了创建有效队列系统的主要任务。

![ACD 配置任务：（1）创建呼叫队列（必需），（2）定义坐席参数（可选），（3）创建坐席（可选），（4）将队列放入 dialplan（必需），（5）配置坐席录音（可选），以及（6）使用 agent show all 和 queue show 进行验证（可选）](../images/14-queues-fig10.png)

第 1 步：创建呼叫队列 在 queues.conf 文件中：

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

第 2 步：定义坐席参数 在 agents.conf 文件中：

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

第 3 步：创建坐席 在 agents.conf 文件中：

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

第 4 步：将队列插入 dialplan

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

### 配置队列录音

可以使用 Asterisk 的 MixMonitor 应用程序录制呼叫。（独立的 Monitor 应用程序已在 Asterisk 22 中移除，queues.conf 的 `monitor-type` 选项现在仅接受 MixMonitor。）录音可以在队列应用程序内启用，从呼叫实际被接起时开始。只有成功的呼叫才会被录制，当人们在听 MOH 时不会进行录音。要启用监控，只需指定 monitor-format。此功能默认禁用。您可以使用 Set (MONITOR_FILENAME=<filename>) 设置录音文件名；否则

```
it will use MONITOR_FILENAME=${UNIQUEID}.
```

在 queues.conf 文件中：

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## 队列操作

以下示例解释了如何使用队列。第 1 步：坐席登录 示例：电话营销队列中的一名坐席拿起电话并拨打 #9000。坐席听到无效登录消息，并被要求输入姓名和密码。审计队列遵循相同的程序。第 2 步：队列 一旦进入队列，如果已定义，坐席将听到 MOH。当呼叫进入电话营销队列时，坐席会听到蜂鸣音并连接到该呼叫。第 3 步：通话结束 当坐席结束通话时，他/她可以：

- 按 ‘*’ 断开连接并留在队列中。
- 断开电话，从而从队列中注销。
- 按 #8000 将呼叫转接进行审计。

## 高级资源

Asterisk 队列系统具有一些高级功能，可以优先处理特定客户和坐席，并启用用户菜单。

### 用户菜单

您可以使用一位数的 extension 为等待队列中的用户定义菜单。要启用此选项，请在队列配置 queues.conf 中定义一个 context。

### 惩罚值（Penalty）

可以为坐席配置惩罚值。队列将首先把呼叫发送给惩罚值较低的用户。例如，因为我们知道客户喜欢 Susan 和她柔和的声音，我们可能会选择为她分配优先级 0。或者，名为 Uber 的坐席经验较少，在客户服务中不太受欢迎；因此，我们为该坐席分配优先级 10。在 queues.conf 文件中：

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### 优先级

队列以 FIFO（先进先出）模式运行。如果您想为特殊客户（白金、黄金）提供优先级，可以设置差异化优先级。对于白金或黄金客户：

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

蓝色客户：

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## 应用程序 agentcallbacklogin() 已被移除

应用程序 `agentcallbacklogin()` 已于 2006 年 7 月在 Asterisk 1.4 中被 Digium 弃用，在 Asterisk 22 中不再可用。推荐的方法是使用带有 PJSIP 接口的 `AddQueueMember()` 来动态地向队列添加回调式成员。文档 `queues-with-callback-members.txt` 已包含在旧版 Asterisk `/doc` 目录中，以提供迁移指导。

旧的 `chan_agent` 通道驱动程序也同样被移除；其功能被重写为 `app_agent_pool` 模块，该模块在 Asterisk 22 中提供了 `AgentLogin()`、`AgentRequest()` 和 `AGENT()` dialplan 函数（这些仍然存在——`app_agent_pool.so` 随标准 22 版本发布）。然而，对于现代呼叫中心，标准的模式是完全跳过坐席通道，并使用 `AddQueueMember()`/`RemoveQueueMember()` 直接将坐席的 PJSIP 设备添加到队列中（在 `queues.conf` 中静态添加，或从 dialplan 或 AMI 动态添加）。这更简单，与 PJSIP 设备状态集成良好，也是本章采用的方法。

## 队列统计

来自队列的所有事件都会记录到 /var/log/asterisk/queue_log 中。队列日志的格式发布在 Asterisk 文档 /doc 目录下的 queuelog.txt 文档中。以下是一些记录的最重要事件。

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

您可以构建自己的实用程序来处理这些事件，或者使用现成的统计包：

- **QueueMetrics** (<https://www.queuemetrics.com/>) – 一个商业的、积极维护的包，它解析 `queue_log`，并且仍然是 Asterisk 呼叫中心最完整的报告工具之一。
- **自行开发** – 因为上面的 `queue_log` 格式稳定且文档齐全，使用小脚本（Python 等）解析它并将事件馈送到数据库或仪表板非常简单。

对于比跟踪 `queue_log` 更具事件驱动的方法，**Asterisk REST Interface (ARI)** 和 **AMI** `QueueSummary`/`QueueStatus` 操作允许您构建实时队列仪表板和针对实时队列状态的自定义集成，而不是事后解析日志。ARI 是 Asterisk 22 中此类工作的现代、受支持的集成界面。

## 总结

在本章中，您学习了如何使用 ACD、其架构以及如何配置它。还介绍了优先级和惩罚值等一些高级功能。

## 测验

1. 在 `queues.conf` 中，以下哪些是有效的队列分配策略（选择所有适用项）？
   - A. ringall
   - B. roundrobin
   - C. leastrecent
   - D. fewestcalls
   - E. rrmemory
   - F. linear
2. 您可以通过在 `queues.conf` 文件中设置 ___ 选项，在队列内录制坐席与客户之间的对话。
3. 哪种 `strategy` 会按照它们在 `queues.conf` 中列出的确切顺序响铃成员？
   - A. random
   - B. wrandom
   - C. linear
   - D. fewestcalls
4. 在电话营销示例中，当坐席结束通话时，他们可以采取哪些操作（选择所有适用项）？
   - A. 按 `*` 断开连接并留在队列中
   - B. 挂断电话并从队列中注销
   - C. 按 `#8000` 将呼叫转接进行审计
   - D. 按 `#` 立即从所有队列中注销
5. 要获得一个有效的队列，哪两项任务是 *必需* 的（选择所有适用项）？
   - A. 创建队列
   - B. 创建坐席
   - C. 配置坐席参数
   - D. 配置录音
   - E. 将队列放入 dialplan
6. 在呼叫队列中，您可以提供一个呼叫者在等待时可以拨打的一位数菜单。这是通过在队列的 `queues.conf` 部分定义一个 ___ 来启用的：
   - A. agent
   - B. menu
   - C. context
   - D. application
7. 支持应用程序 `AddQueueMember()` 和 `RemoveQueueMember()` 用于在 ___ 中动态添加或移除成员：
   - A. dial plan
   - B. command-line interface
   - C. queues.conf
   - D. agents.conf
8. 由于 chan_sip 已在 Asterisk 21 中移除，静态队列成员必须引用诸如 ___ 之类的通道，而不是 `SIP/1001`。
9. `wrapuptime` 参数是坐席断开通话后，队列向该坐席发送新呼叫之前的最短时间。
   - A. True
   - B. False
10. 在调用 `Queue()` 之前，可以通过设置 `QUEUE_PRIO` 通道变量来为呼叫者在同一队列中提供更高的位置。
    - A. True
    - B. False

**答案：** 1 — A, C, D, E, F（roundrobin 已被 rrmemory 取代且不再存在） · 2 — `monitor-format`（通过指定 `monitor-format` 启用队列录音；`monitor-type` 选择 MixMonitor 与 Monitor） · 3 — C (linear) · 4 — A, B, C（`*` 断开连接并保持；`#` 不是注销所有键） · 5 — A, E · 6 — C（`context` 选项） · 7 — A (dial plan) · 8 — `PJSIP/1001`（任何 `PJSIP/` 接口） · 9 — True · 10 — True
