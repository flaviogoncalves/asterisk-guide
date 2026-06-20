# Call Queues

呼叫队列，也称为 ACD（自动呼叫分配），在高效接听客户来电方面变得日益重要。自动呼叫分配器可以帮助降低成本、提升服务水平并促进销售，因为呼叫分配器会影响企业的运作方式——这不是短期的改变，而是长期的影响。在呼叫中心环境中，最关键的因素是人；他们是最昂贵的资源。招聘、培训和激励坐席需要投入时间、金钱和耐心。使用 ACD，您可以通过精确确定所需坐席数量、控制优秀和不良坐席以及分析呼叫流来最大化坐席的生产力。

## 目标

在本章结束时，您应该能够：

- 理解为何以及如何使用呼叫队列
- 理解呼叫队列的基本原理
- 安装并配置队列系统

## 队列是如何工作的？

呼叫队列并不是全新的概念。当您面对大量的入站呼叫时，难以合理分配呼叫。使用所有坐席同时响铃的组策略往往效果不佳，除非坐席数量很少。然而，呼叫队列每次只会将呼叫分配给一个空闲坐席，并在没有坐席可用时让客户听音乐保持等待。队列的工作原理是保留呼叫，直到找到未占用的坐席来接听。队列的最大优势之一是避免丢失呼叫，同时还能生成统计数据。

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

通常，呼叫队列的工作流程如下：

- 坐席登录到队列。
- 入站呼叫进入队列。
- 使用分配策略将呼叫发送给坐席。
- 在呼叫者等待时播放 hold 音乐。
- 可以向呼叫者播放公告，通知其等待时间
- 坐席接听呼叫并生成统计信息。

队列的主要应用场景是客户服务。使用队列后，当坐席忙碌时可以避免呼叫丢失。如果发现队列中的呼叫者数量在增长，可以向队列中添加新坐席。队列的另一个优势是可以获得呼叫放弃率、平均通话时长、呼叫应答目标等统计数据。这些统计将帮助您确定需要多少坐席，以提供更好的客户服务。

### ACD 架构

ACD 架构由队列和坐席组成。一个坐席可以同时属于两个队列。一个队列可以拥有坐席、通道和坐席组。

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

## 代理

代理实现为代理通道。它们可以在队列中使用。代理通道的另一种用途是分机移动性。用户可以使用任何电话登录并接收其来电。这使得用户可以走到任何房间并将其变成办公室。您可以在dialplan中使用 `dial(agent/<name>)` 拨打代理。您在 `agents.conf` 文件中定义代理。

![代理移动性：用户拿起任意电话，拨打登录分机，并输入代理号码和密码；在 `agentlogin()` 成功后，代理（Agent 300）准备接听来电，您可以使用 CLI 命令 `agent show all` 检查状态](../images/14-queues-fig05.png)

### 代理组

您可以选择使用代理组。此功能不考虑 ACD 策略。您可能更倾向于单独列出所有代理。如果想转接到代理组，可以使用 `queues.conf`：

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### 代理的配置文件

代理在 `agents.conf` 文件中定义。下面是该文件的一个工作示例。

![agents.conf 文件的工作示例：一个包含 `persistentagents` 的通用节，一个包含默认参数（autologoff、ackcall、endcall、wrapuptime、musiconhold）的 agents 节，以及两个代理定义（300 和 301）](../images/14-queues-fig06.png)

## ACD-related applications

Asterisk 队列系统提供了多个应用程序，以在 dialplan 中实现队列。下面展示其中的一些。

### The application queue()

此应用程序将来电排入在 queues.conf 中定义的特定呼叫队列。选项字符串可以包含零个或多个单字母选项（如图所示）。除了转接通话外，通话还可以被置入等待（park），随后由其他用户接听。可选的 URL 将在通道支持时发送给被叫方。可选的 AGI 参数将在呼叫方的通道连接到队列成员后设置并执行 AGI 脚本。超时将在指定的秒数后导致队列失败退出，在每个超时和重试周期之间进行检查。此应用程序在完成后会设置 QUEUE 状态变量：

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### The application agentlogin()

此应用程序要求坐席登录系统。它始终返回 -1。登录后，坐席在收到新来电时会听到提示音。坐席可以通过按 * 键挂断通话。

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### The application addQueueMember()

此应用程序动态将设备（例如 PJSIP/3000）添加到队列中。如果设备已存在，则返回错误。

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### The application removeQueueMember()

此应用程序动态将设备从队列中移除。如果设备不属于该队列，则返回错误。

```
RemoveQueueMember(queuename[|interface])
```

### Support applications and CLI commands

一些应用程序和控制台命令能够帮助队列的管理。以下概述了每个应用程序的功能：

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## 配置任务

下图概括了创建可用队列系统的主要任务。

![The ACD configuration tasks: (1) create the call queue (required), (2) define agent parameters (optional), (3) create agents (optional), (4) put the queue in the dial plan (required), (5) configure agent recording (optional), and (6) verify with agent show all and queue show (optional)](../images/14-queues-fig10.png)

步骤 1：在文件 **queues.conf** 中创建呼叫队列：

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

步骤 2：在文件 **agents.conf** 中定义坐席参数：

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

步骤 3：在文件 **agents.conf** 中创建坐席：

```
;agent => agentid,agentpassword,name
[agents]
agent => 300,300,Test Rep - 300
agent => 301,301,Test Rep . 301
agent => 600,600,Test Ver - 600
agent => 601,601,Test Ver . 601
```

步骤 4：在文件 `extensions.conf` 中将队列插入 dialplan：

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

### 配置队列录音

可以使用 Asterisk 的 MixMonitor 应用程序对通话进行录音。（独立的 Monitor 应用在 Asterisk 22 中已被移除，queues.conf `monitor-type`选项现在仅接受 MixMonitor。）录音可以在队列应用内部启用，从实际接听通话时开始。仅对成功的通话进行录音，且在有人监听 MOH 时不会进行录音。要启用监控，只需指定 **monitor-format**。否则此功能默认关闭。您可以使用 `Set(MONITOR_FILENAME=<filename>)` 设置录音文件名；否则将使用 `MONITOR_FILENAME=${UNIQUEID}`。

在文件 **queues.conf** 中：

```
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

## 队列操作

以下示例说明如何使用队列。

1. 坐席登录。示例：电话营销队列中的坐席接起电话并拨打 #9000。坐席听到无效登录提示，并被要求输入姓名和密码。审计队列遵循相同的流程。
2. 队列。进入队列后，坐席将听到音乐等待（MOH），如果已定义。当有呼入电话进入电话营销队列时，坐席会听到提示音并被接通该通话。
3. 通话结束。当坐席结束通话后，他/她可以：
   - 按 ‘*’ 断开并保持在队列中。
   - 挂断电话，从而退出队列。
   - 按 #8000 将通话转接进行审计。

## 高级资源

Asterisk 队列系统具有一些高级功能，可对特定客户和坐席进行优先级排序，并启用用户菜单。

### 用户菜单

您可以在用户等待队列时使用单数字分机定义一个菜单。要启用此选项，请在队列配置文件 `queues.conf` 中定义一个 context。

### 惩罚

可以为坐席配置惩罚值。队列会先将呼叫发送给惩罚值较低的用户。例如，鉴于我们的客户喜欢 Susan 以及她柔和的声音，我们可以为她分配优先级 0。另一方面，名为 Uber 的坐席经验较少，客户服务的优先度较低；因此，我们为该坐席分配优先级 10。在文件 `queues.conf` 中：

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### 优先级

队列以 FIFO（先进先出）模式运行。如果您想为特殊客户（白金、金卡）提供优先级，可设置差异化的优先级。针对白金或金卡客户：

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

蓝卡客户：

```
exten=>112,1,Playback(welcome)
exten=>112,2,Set(QUEUE_PRIO=5)
exten=>112,3,Queue(customerservice)
```

## The application agentcallbacklogin() is removed

The application `agentcallbacklogin()` was deprecated by Digium in Asterisk 1.4 (July 2006) and is no longer available in Asterisk 22. The recommended approach is to use `AddQueueMember()` with a PJSIP interface to dynamically add callback-style members to a queue. The document `queues-with-callback-members.txt` was included in older Asterisk `/doc` directories for migration guidance.

The old `chan_agent` channel driver was likewise removed; its functionality was rewritten as the `app_agent_pool` module, which is what provides `AgentLogin()`, `AgentRequest()` and the `AGENT()` dialplan function in Asterisk 22 (these are still present — `app_agent_pool.so` ships with a stock 22 build). For modern call centers, however, the standard pattern is to skip agent channels entirely and add the agent's PJSIP device directly to the queue with `AddQueueMember()`/`RemoveQueueMember()` (statically in `queues.conf`, or dynamically from the dialplan or AMI). This is simpler, integrates cleanly with PJSIP device state, and is the approach used throughout this chapter.

## Queue statistics

All events from queues are logged to /var/log/asterisk/queue_log. The format of the queue log is published in the document queuelog.txt in the /doc directory of the Asterisk documentation. Below are some of the most important events logged.

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

You can build your own utility to process these events or use a ready-to-run statistics package:

- **QueueMetrics** (<https://www.queuemetrics.com/>) – a commercial, actively maintained package that parses `queue_log` and remains one of the most complete reporting tools for Asterisk call centers.
- **Roll your own** – because the `queue_log` format above is stable and well documented, it is straightforward to parse it with a small script (Python, etc.) and feed the events into a database or dashboard.

For a more event-driven approach than tailing `queue_log`, the **Asterisk REST Interface (ARI)** and the **AMI** `QueueSummary`/`QueueStatus` actions let you build live queue dashboards and custom integrations against real-time queue state rather than after-the-fact log parsing. ARI is the modern, supported integration surface for this kind of work in Asterisk 22.

## 概要

在本章中，您已经学习了如何使用 ACD、其架构以及如何配置它。还介绍了一些高级功能，如优先级和惩罚。

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
