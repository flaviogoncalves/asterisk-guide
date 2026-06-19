---
theme: seriph
title: 'Queues and Call Centers'
info: |
  ## Asterisk Guide — Chapter 12
  Queues and Call Centers. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Queues and Call Centers

Chapter 12

<div class="abs-bl m-6 text-sm opacity-70">
  Asterisk Guide · Asterisk 22 LTS · PJSIP-first
</div>

<style>
h1 { color: #1C5D99; }
/* QA: keep code inside the 16:9 frame — shrink slightly + wrap long lines (lossless) */
.slidev-layout pre { font-size: 0.8em; line-height: 1.32; }
.slidev-layout pre code { white-space: pre-wrap; overflow-wrap: anywhere; }
</style>

---
layout: default
---

# Objectives

By the end of this chapter you will be able to:

<v-clicks>

- **Understand** why and how to use call queues (ACD)
- **Explain** the basic theory behind call queues
- **Install and configure** the queue system with `queues.conf`
- **Choose** a distribution strategy and add members and agents
- **Place** a queue in the dial plan and manage it at runtime

</v-clicks>

<!--
ACD = Automatic Call Distribution. This is the contact-center chapter: maximize agent
productivity, stop losing calls, and produce real statistics.
-->

---
layout: section
---

# How queues work

---
layout: image-right
image: /images/14-queues-fig01.png
backgroundSize: contain
---

# What a queue does

A queue **holds** the caller while it finds an unoccupied agent — instead of ringing everyone at once.

<v-clicks>

- Agents **log in** to the queue
- Incoming calls are **queued**
- A **strategy** distributes calls to agents
- **Music on hold** plays while the caller waits
- **Announcements** can tell callers their wait time
- The call is answered and **statistics** are generated

</v-clicks>

<div class="mt-4 text-sm opacity-70">
The main use is customer service: avoid lost calls, scale agents to demand, and measure abandon rate, average duration, and answer targets.
</div>

---
layout: image-right
image: /images/14-queues-fig02.png
backgroundSize: contain
---

# ACD architecture

The ACD is built from **queues** and **agents**.

<v-clicks>

- One **agent** can belong to two queues at once
- A **queue** can contain agents, channels, and agent groups
- Each queue is fed by a **phone number** in the dial plan
- Agents are bound to physical **channels** (`PJSIP/…`)

</v-clicks>

<div class="mt-6 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Example queues: <strong>Customer Service</strong> and <strong>Inside Sales</strong>, each with its own number and member list.
</div>

---
layout: section
---

# Configuring queues

---

# queues.conf — general behavior

Queues are defined in **`queues.conf`**. Start with the general section.

```ini
[general]
autofill = yes
```

<div grid="~ cols-2 gap-8 mt-2 text-sm">
<div>

**Old (serial) behavior**

- The queue waited for one call to be dispatched before sending the next
- A 15-second answer delay blocked every other caller
- Inefficient for high-volume queues

</div>
<div>

**`autofill = yes` (modern)**

- Does **not** wait for a call to be answered
- Distributes calls in **parallel**
- Record calls with **`mixmonitor`** — recorded and mixed at once

</div>
</div>

---
layout: image-right
image: /images/14-queues-fig03.png
backgroundSize: contain
---

# A working queues.conf

A complete queue defines its **strategy**, **service level**, **announcements**, **recording**, and **members**.

```ini
[customerservice]
strategy = ringall
timeout = 15
retry = 5
musicclass = default
member => PJSIP/3000
member => PJSIP/3001
```

<div class="mt-3 text-sm opacity-70">
Members are active channels that respond to the queue — direct channels (<code>PJSIP</code>, <code>DAHDI</code>) or agents who log in first.
</div>

---

# Distribution strategies

Calls are distributed among members by **one** of these strategies:

<div grid="~ cols-2 gap-x-10 gap-y-1 text-sm mt-2">
<div>

- **ringall** — ring all available channels until one answers
- **leastrecent** — to the least-recently-used member
- **fewestcalls** — to the member with the fewest calls
- **random** — ring a random interface
- **wrandom** — random, weighted by member penalty

</div>
<div>

- **rrmemory** — round robin **with memory** of where it left off
- **rrordered** — like rrmemory, but keeps config-file order
- **linear** — ring members in the order listed in `queues.conf`

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>roundrobin</strong> was replaced by <strong>rrmemory</strong> in early releases and no longer exists. All strategies above are present in Asterisk 22.
</div>

---
layout: section
---

# Members and agents

---
layout: image-right
image: /images/14-queues-fig04.png
backgroundSize: contain
---

# Agents

Agents are attendants who **log in** and become members of a queue.

<v-clicks>

- A user dials an extension that runs the **`AgentLogin()`** application
- `AgentLogin()` binds the agent (e.g. **Agent 300**) to the current channel
- Agents can log in from **any** extension — extension mobility
- Check status with the CLI command:

</v-clicks>

```text
CLI> agent show all
```

<div class="mt-3 text-sm opacity-70">
Agents are defined in <code>agents.conf</code>; dial one with <code>Dial(Agent/&lt;name&gt;)</code>.
</div>

---

# agents.conf

Agents are proxy channels, defined in **`agents.conf`**.

```ini
; Agent configuration
[general]
persistentagents = yes

[agents]
autologoff = 15
autologoffunavail = yes
ackcall = no
endcall = yes
wrapuptime = 5000
musiconhold => default

; agent => agentid,agentpassword,name
agent => 300,300
agent => 301,301
```

<div class="mt-2 text-sm opacity-70">
<code>wrapuptime</code> (ms) is the minimum time after disconnect before the queue sends the agent a new call.
</div>

---
layout: image-right
image: /images/14-queues-fig05.png
backgroundSize: contain
---

# Agent mobility

Agents are implemented as **proxy channels** — perfect for "hot desking."

<v-clicks>

- The user picks up **any** phone
- Dials a **login extension**
- Passes the **agent number** and **password**
- After `AgentLogin()` succeeds, **Agent 300** is ready to take calls
- Any room becomes the user's office

</v-clicks>

```text
CLI> agent show all
```

---
layout: section
---

# ACD applications

---

# Queue() and member apps

<div grid="~ cols-2 gap-8">
<div>

### `Queue()`

Places an incoming call into a queue defined in `queues.conf`.

```ini
exten => _0800XXXXXXX,1,Answer()
 same =  n,Background(welcome)
 same =  n,Queue(customerservice)
```

Sets the **`QUEUESTATUS`** variable: `TIMEOUT`, `FULL`, `JOINEMPTY`, `LEAVEEMPTY`, `JOINUNAVAIL`, `LEAVEUNAVAIL`.

</div>
<div>

### Dynamic membership

Add or remove members at runtime — **from the dial plan**.

```ini
exten => 9001,1,AddQueueMember(customerservice,PJSIP/3000)
exten => 9002,1,RemoveQueueMember(customerservice,PJSIP/3000)
```

`AddQueueMember()` errors if the device already exists; `RemoveQueueMember()` errors if it is not a member.

</div>
</div>

<div class="mt-3 text-sm opacity-70">
Since chan_sip was removed in Asterisk 21, members reference <strong>PJSIP/…</strong> — never <code>SIP/…</code>.
</div>

---
layout: image-right
image: /images/14-queues-fig09.png
backgroundSize: contain
---

# Support apps & CLI

Manage queues at runtime with applications and console commands.

<v-clicks>

- **`AddQueueMember()`** / **`RemoveQueueMember()`** — dynamic members
- **`AgentLogin()`** — log an agent into the system

</v-clicks>

```text
CLI> agent show all
CLI> queue show
CLI> queue show customerservice
```

<div class="mt-3 text-sm opacity-70">
<code>queue show &lt;name&gt;</code> reports calls waiting, the strategy in use, and each member's state and call count.
</div>

---
layout: section
---

# Putting it together

---
layout: image-right
image: /images/14-queues-fig10.png
backgroundSize: contain
---

# Configuration tasks

The major tasks to build a working queue:

<v-clicks>

1. **Create the call queue** — *required*
2. Define agent parameters — *optional*
3. Create agents — *optional*
4. **Put the queue in the dial plan** — *required*
5. Configure agent recording — *optional*
6. Verify with `agent show all` and `queue show` — *optional*

</v-clicks>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Only steps <strong>1</strong> and <strong>4</strong> are required to get calls flowing.
</div>

---

# Step 1 — Create the queue & Step 4 — Dial plan

<div grid="~ cols-2 gap-6">
<div>

**`queues.conf`**

```ini
[telemarketing]
musicclass = default
timeout = 2
retry = 2
maxlen = 0
member => PJSIP/3000
member => PJSIP/3001

[auditing]
musicclass = default
timeout = 15
retry = 5
maxlen = 0
member => PJSIP/6000
member => PJSIP/6001
```

</div>
<div>

**`extensions.conf`**

```ini
; Telemarketing queue
exten => _0800XXXXXXX,1,Answer()
 same =  n,Set(CHANNEL(musicclass)=default)
 same =  n,Background(welcome)
 same =  n,Queue(telemarketing)

; Transfer to the auditing queue
exten => 8000,1,Queue(auditing)
 same =  n,Playback(demo-echotest)
 same =  n,Goto(8000,1)

; Agent login
exten => 9000,1,Wait(1)
 same =  n,AgentLogin()
```

</div>
</div>

---

# Queue recording

Calls are recorded with **MixMonitor**, enabled inside the queue.

```ini
; In queues.conf
monitor-format = wav
monitor-type = MixMonitor
monitor-join = yes
```

<div grid="~ cols-2 gap-8 mt-3 text-sm">
<div>

- Recording starts when the call is **picked up**
- Only **successful** calls are recorded
- Nothing is recorded while the caller hears MOH
- Specify **`monitor-format`** to enable it

</div>
<div>

- Set the filename with `Set(MONITOR_FILENAME=<name>)`
- Otherwise it uses `${UNIQUEID}`

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
The standalone <strong>Monitor</strong> application was removed in Asterisk 21 (absent in 22) — <code>monitor-type</code> now accepts only <strong>MixMonitor</strong>.
</div>

---
layout: section
---

# Advanced resources

---

# Penalty & priority

<div grid="~ cols-2 gap-8">
<div>

### Penalty — prefer better agents

The queue sends calls first to members with the **lowest penalty**.

```ini
[customerservice]
member => PJSIP/3000,0    ; Susan — excellent
member => PJSIP/3001,10   ; Uber — the new guy
```

Susan (penalty 0) is tried before Uber (penalty 10).

</div>
<div>

### Priority — prefer better customers

Queues are **FIFO**. Raise a caller's position with **`QUEUE_PRIO`**.

```ini
exten => 111,1,Playback(welcome)   ; platinum/gold
 same =  n,Set(QUEUE_PRIO=10)
 same =  n,Queue(customerservice)

exten => 112,1,Playback(welcome)   ; blue
 same =  n,Set(QUEUE_PRIO=5)
 same =  n,Queue(customerservice)
```

</div>
</div>

<div class="mt-3 text-sm opacity-70">
A <strong>user menu</strong> of one-digit options can be offered while waiting — define a <code>context</code> in the queue's <code>queues.conf</code> section.
</div>

---

# Queue statistics

Every queue event is logged to **`/var/log/asterisk/queue_log`**.

<div grid="~ cols-2 gap-x-10 gap-y-1 text-sm mt-2">
<div>

- `ENTERQUEUE(url|callerid)`
- `CONNECT(holdtime|uniqueid)`
- `ABANDON(pos|origpos|waittime)`
- `COMPLETEAGENT(holdtime|calltime|origpos)`
- `COMPLETECALLER(holdtime|calltime|origpos)`

</div>
<div>

- `AGENTLOGIN(channel)`
- `AGENTLOGOFF(channel|logintime)`
- `RINGNOANSWER(ringtime)`
- `EXITWITHTIMEOUT(...)` / `EXITWITHKEY(...)`
- `QUEUESTART` · `CONFIGRELOAD`

</div>
</div>

<div class="mt-4 text-sm opacity-70">
Process these events yourself, feed a reporting tool, or build a modern integration via the <strong>Asterisk REST Interface (ARI)</strong>.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**A call queue**

Define a `support` queue with `strategy=ringall`, route a number into it, and ring both agents (`PJSIP/6001`, `PJSIP/6002`).

See **Lab 4** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Reload <code>app_queue.so</code> and confirm with <code>queue show support</code> — members read <em>Unavailable</em> until their softphones register.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- A **queue (ACD)** holds callers and delivers them to one available agent — avoiding lost calls and producing real statistics.
- The ACD is built from **queues** (`queues.conf`) and **agents** (`agents.conf`); **members** are channels such as **`PJSIP/3000`**.
- A **strategy** (`ringall`, `leastrecent`, `fewestcalls`, `rrmemory`, `linear`, …) decides who rings; **`roundrobin` is gone**.
- **`Queue()`** places calls; **`AddQueueMember()`** / **`RemoveQueueMember()`** manage members at runtime from the dial plan.
- **Penalty** prefers better agents, **`QUEUE_PRIO`** prefers better customers, and **MixMonitor** records the calls.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>CDR and CEL</strong> — recording what every call did.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 12 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which queue strategy rings members in the exact order they are listed in <code>queues.conf</code> — and what replaced <code>roundrobin</code>?</em>
</div>
