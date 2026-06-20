# Call Queues

Call queues, also known as ACD (Automatic Call Distribution) are becoming increasingly important for answering customer calls efficiently. An automatic call distributor can help reduce costs, increase service, and improve sales as call distributors affect how your business works—not for a few days, but for many years. In a call center environment, the number one factor is people; they are the most expensive resource. It takes time, money, and patience to hire, train, and motivate agents. With an ACD, you can maximize agents’ productivity by precisely dimensioning the number of agents required, controlling good and bad attendants, and analyzing the call flow.

## Objectives

By the end of this chapter, you should be able to:

- Understand why and how to use call queues
- Understand the basic theory of call queues
- Install and configure the queue system

## How queues work?

Call queues are not exactly a novelty. When you have a high inbound call flow, it is hard to distribute calls appropriately. Using a group strategy where the phone simultaneously rings on all agents does not seem to work, unless you have only a few agents. However, a call queue will only deliver calls to a single available agent each time and put the customer on hold with music when there are no agents available. The queue works by retaining the call while finding an unoccupied agent to answer the call. One of the biggest benefits of the queue is to avoid losing calls while providing the possibility to generate statistics.

![A call queue: incoming 1-800 calls enter the queue and an ACD strategy (ringall, rrmemory, leastrecent, priority, and others) distributes them to the available agents](../images/14-queues-fig01.png)

Usually, a call queue works like this:

- Agents log in to the queue.
- Incoming calls are queued.
- A queuing strategy to distribute the calls is used to send calls to agents.
- Music on hold is played while the caller waits.
- Announcements can be made to callers, notifying them of waiting time
- The call is answered by the agent and statistics are generated.

The main application for queues is customer service. When using queues, you avoid losing calls when your agents are busy. You can add new agents to the queue if you find that the number of callers in the queue is growing. Another advantage with queues is you can now have statistics like call abandon rate, average call duration, and call answering target. These statistics will help you determine how many agents to use to provide better service to your customer.

### ACD architecture

The ACD architecture is formed by queues and agents. One agent can be in two queues at the same time. A queue can have agents, channels, and agent groups.

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

## Agents

Agents are implemented as proxy channels. They can be used inside the queues. Another use for the agent channels is extension mobility. The user can log in using any phone and receive its calls. This allows a user to go to any room to make it an office. You can dial an agent in the dial plan using dial(agent/<name>). You define agents in the agents.conf file.

![Agent mobility: the user picks up any phone, dials a login extension, and passes the agent number and password; after agentlogin() succeeds the agent (Agent 300) is ready to take calls, and you can check status with the CLI command `agent show all`](../images/14-queues-fig05.png)

### Agent Groups

You may choose to use agent groups. This function does not take ACD strategies into consideration. You will probably prefer to list all agents individually. If you want to transfer to an agent group, you can use `queues.conf`:

```
member => agent/@1    ; any agent in group 1
member => agent/:1,1  ; any agent in group 1, wait for first available
```

### The configuration file for agents

Agents are defined in the file agents.conf. Below is a working example of the file.

![A working example of the agents.conf file: a general section with persistentagents, an agents section with the default parameters (autologoff, ackcall, endcall, wrapuptime, musiconhold), and two agent definitions (300 and 301)](../images/14-queues-fig06.png)

## ACD-related applications

The Asterisk queue system makes several applications available to implement the queues in the dial plan. Below, we show some of them.

### The application queue()

This application queues incoming calls into a particular call queue as defined in queues.conf. The option string may contain zero or more single-letter options (shown in the figure below). In addition to transferring the call, a call may be parked and then picked up by another user. The optional URL will be sent to the called party if the channel supports it. The optional AGI parameter will set up an AGI script to be executed on the calling party's channel once they are connected to a queue member. The timeout will cause the queue to fail out after a specified number of seconds, checked between each timeout and retry cycle. This application sets the QUEUE status variable upon completion:

![The queue() application: its syntax `Queue(queuename,options,URL,announceoverride,timeout,AGI)` — Asterisk 22 separates the arguments with commas (the older pipe `|` form is gone) — and the available single-letter options (d, h, H, n, i, r, t, T, w, W)](../images/14-queues-fig07.png)

- TIMEOUT
- FULL
- JOINEMPTY
- LEAVEEMPTY
- JOINUNAVAIL
- LEAVEUNAVAIL

### The application agentlogin()

This application asks the agent to log in to the system. It always returns -1. While logged in, the agent receiving calls will hear a beep when a new call comes in. The agent can dump the call by pressing the * key.

![The agentlogin() application: its syntax `AgentLogin([AgentNo][|options])` and the `s` option for a silent login that does not announce the login confirmation](../images/14-queues-fig08.png)

### The application addQueueMember()

This application dynamically adds a device (e.g., PJSIP/3000) to a queue. If the device already exists, it will return an error.

```
AddQueueMember(queuename[|interface][|penalty]):
```

#### The application removeQueueMember()

This application dynamically removes a device from the queue. If the device does not belong to the queue, it will return an error.

```
RemoveQueueMember(queuename[|interface])
```

### Support applications and CLI commands

Some applications and console commands are capable of helping the work with queues. The following outlines what each application does:

![Support applications (AddQueueMember, RemoveQueueMember) and CLI commands (agent show all, queue show, queue show <name>) used to manage queues at runtime](../images/14-queues-fig09.png)

## Configuration tasks

The figure below summarizes the major tasks to create a working queue system.

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

## Queue operation

The following examples explains how to use the queue.

1. Agent login. Example: An agent in the telemarketing queue picks up the phone and dials #9000. The agent hears an invalid login message and is asked for his/her name and password. The auditing queue follows the same procedure.
2. Queue. Once in the queue, the agent will hear MOH, if defined. When a call comes in to the telemarketing queue, the agent will hear a beep and will be connected to that call.
3. Call ending. When the agent finishes the call, he/she can:
   - Press ‘*’ to disconnect and stay in the queue.
   - Disconnect the phone, thereby disconnecting from the queue.
   - Press #8000 to transfer the call for auditing.

## Advanced resources

The Asterisk queue system has some advanced features to prioritize certain customers and agents as well as enable a user menu.

### User menu

You can define a menu for a user while waiting in the queue using one-digit extensions. To enable this option, define a context in the queue configuration queues.conf.

### Penalty

Agents can be configured with a penalty. A queue will send the calls first to users with lower penalty values. For example, since we know that our customers love Susan and her soft voice, we may choose to assign priority 0 to her. Alternatively, the agent named Uber, who has less experience, is less preferred for customer service; therefore, we assign a priority 10 to this agent. In the file queues.conf:

```
[customerservice]
member=300,0,Susan the excellent agent
member=300,10,Uber the new guy
```

### Priority

Queues operate in the FIFO (first in first out) mode. If you want to give priority for special customers (platinum, gold) you can set up differentiated priorities. For platinum or gold customers:

```
exten=>111,1,Playback(welcome)
exten=>111,2,Set(QUEUE_PRIO=10)
exten=>111,3,Queue(customerservice)
```

Blue customers:

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

## Summary

In this chapter you have learned how to use an ACD, its architecture, and how to configure it. Some advanced features such as priorities and penalties were also presented.

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
