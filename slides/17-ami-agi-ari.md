---
theme: seriph
title: 'Extending Asterisk with AMI and AGI'
info: |
  ## Asterisk Guide — Chapter 14
  Extending Asterisk with AMI and AGI. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Extending Asterisk with AMI and AGI

Chapter 14

<div class="abs-bl m-6 text-sm opacity-70">
  Asterisk Guide · Asterisk 22 LTS · PJSIP-first
</div>

<style>
h1 { color: #1C5D99; }
</style>

---
layout: default
---

# Objectives

By the end of this chapter you will be able to:

<v-clicks>

- **Describe** the access options for external programs
- **Use** `asterisk -rx` and the `System()` application
- **Explain** what AMI is and configure `manager.conf`
- **Execute** an AMI command from a PHP program
- **Describe** the AGI flavors — AGI, DeadAGI, EAGI, FastAGI
- **Write** and run a simple AGI script
- **Choose** between AMI, AGI, and ARI

</v-clicks>

<!--
This chapter is protocol-heavy. ARI now has its own deck (Chapter 15) — here we stay on AMI + AGI.
-->

---
layout: default
---

# Major ways to extend Asterisk

Asterisk is a development tool. When the dial plan is not enough, you reach for an external program.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**The four classic doors**

- Linux shell → **`asterisk -rx`**
- The **`System()`** dial plan application
- **AMI** — Asterisk Manager Interface (TCP, events + actions)
- **AGI** — Asterisk Gateway Interface (scripts over stdio)

</div>
<div>

**Which one?**

- **AGI** → IVR logic, database lookups *per call*
- **AMI** → dialers, CTI, monitoring channel state
- **ARI** → full channel/bridge control *(next chapter)*

</div>
</div>

<div class="mt-4 text-sm opacity-70">
Changing the C source is the most powerful — and most dangerous — option, and is out of scope here.
</div>

---
layout: section
---

# Quick wins — the shell and the dial plan

---
layout: default
---

# `asterisk -rx` and `System()`

<div grid="~ cols-2 gap-8">
<div>

### From the Linux shell

Connect to a running Asterisk and run one command.

```bash
asterisk -rx "core show version"
asterisk -rx "pjsip show endpoints"
asterisk -rx "stop now"
```

Perfect for cron jobs and quick scripts.

</div>
<div>

### From the dial plan

`System()` runs an external command for the caller.

```ini
exten => 9000,1,System(/usr/local/bin/screenpop.sh ${CALLERID(num)})
 same => n,Dial(PJSIP/9000,15,t)
 same => n,Hangup()
```

Result lands in `${SYSTEMSTATUS}` — `SUCCESS` or `FAILURE`.

</div>
</div>

---
layout: section
---

# AMI — Asterisk Manager Interface

---
layout: default
---

# What is AMI?

A client connects over **TCP** and issues **actions** while reading **events** — a simple line protocol of `Key: value` pairs.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**How it behaves**

- Establish a session before sending commands
- Client packets start with **`Action:`**
- Server packets start with **`Response:`** or **`Event:`**
- After login, traffic flows in **both directions**

</div>
<div>

**Three packet types**

- **Action** — a request from the client (finite set, set by loaded modules)
- **Response** — the reply to the last action
- **Event** — something happened in the core or a module

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Asterisk does not handle many AMI connections well. For lots of clients, put an <strong>Asterisk Manager Proxy</strong> in front.
</div>

---
layout: default
---

# Configuring `manager.conf`

Open the TCP listener (port **5038**) and define a user with `read` / `write` permission classes.

```ini
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

<div class="mt-3 text-sm opacity-70">
AMI is <strong>not</strong> enabled by default. Bind to localhost and lock it down with <code>deny</code>/<code>permit</code> — never expose 5038 to the internet.
</div>

---
layout: default
---

# Logging in from PHP

Authenticate with an `Action: Login` packet carrying the `manager.conf` user and secret.

```php
<?php
$socket = fsockopen("127.0.0.1", 5038, $errno, $errstr, $timeout);
fputs($socket, "Action: Login\r\n");
fputs($socket, "UserName: admin\r\n");
fputs($socket, "Secret: senha\r\n\r\n");

// Don't need the event firehose? Turn it off:
fputs($socket, "Action: Events\r\nEventMask: off\r\n\r\n");
?>
```

<div class="mt-3 text-sm opacity-70">
Any language with a socket interface works — we use PHP for its popularity. The login secret travels in clear text, so AMI belongs on the loopback or behind TLS.
</div>

---
layout: default
---

# Action packets

Each action is a block of `Key: value` lines terminated by a blank line. **`ActionID`** correlates the asynchronous reply.

```text
Action: <action type>
ActionID: <unique id>
<Key 1>: <Value 1>
<Key 2>: <Value 2>
Variable: <Variable 1>=<Value 1>
Variable: <Variable 2>=<Value 2>

```

A small slice of the core actions (`manager show commands` lists them all):

```text
Originate    originate,all    Originate a call
Hangup       system,call,all  Hangup a channel
Status       system,call,...  List channel status
Command      command,all      Execute an Asterisk CLI command
PJSIPShowEndpoints  system,reporting  Lists PJSIP endpoints
```

---
layout: default
---

# Events — query, don't memorize

Events report core changes — channel created, bridged, registration changed, queue member added.

The exact set depends on the build and loaded modules, so ask the running server:

```text
asterisk*CLI> manager show events             ; every event this build can emit
asterisk*CLI> manager show event BridgeEnter  ; one event and its fields
```

<div class="mt-2 text-sm">

Call bridging, for example, is reported through:

</div>

```text
BridgeCreate   BridgeEnter   BridgeLeave   BridgeDestroy
```

<div class="mt-3 text-sm opacity-70">
The older <code>Link</code>/<code>Unlink</code> events were removed back in Asterisk 12 — use the Bridge events instead.
</div>

---
layout: section
---

# AGI — Asterisk Gateway Interface

---
layout: default
---

# What is AGI?

AGI is to Asterisk what CGI is to a web server: it hands a **channel** to an external script that talks the **AGI protocol over stdin/stdout**.

<div grid="~ cols-2 gap-8" class="mt-2 text-sm">
<div>

**Four flavors**

- **AGI** — runs a program on the Asterisk box
- **FastAGI** — runs it on another server over TCP
- **EAGI** — adds inbound audio on file descriptor **3**
- **DeadAGI** — works after hangup (the `h` extension)

</div>
<div>

**Use it for**

- IVRs driven by a database
- Per-call business logic
- Any language with stdio — Perl, PHP, Python, …

</div>
</div>

```text
asterisk*CLI> agi show commands   ; list every AGI command this build supports
asterisk*CLI> agi debug           ; trace the stdin/stdout conversation
```

---
layout: default
---

# The AGI handshake

On launch, Asterisk pushes an environment block (one `agi_*: value` per line) ending in a blank line. Read it first.

```text
agi_request: test.php
agi_channel: PJSIP/4000-00000001
agi_language: en
agi_type: PJSIP
agi_callerid: 4000
agi_context: default
agi_extension: 4000
agi_priority: 1
```

```php
<?php
$agi = array();
while ($line = fgets($stdin)) {
    $line = trim($line);
    if ($line === "") break;          // blank line ends the env block
    list($key, $val) = explode(":", $line, 2);
    $agi[trim($key)] = trim($val);
}
?>
```

---
layout: default
---

# A minimal AGI script (PHP)

Live in `/var/lib/asterisk/agi-bin/`, `chmod 755`, shebang on line 1.

```php
#!/usr/bin/php -q
<?php
ob_implicit_flush(true);
$stdin  = fopen("php://stdin",  "r");
$stdout = fopen("php://stdout", "w");

function command($cmd) {
    global $stdin, $stdout;
    fputs($stdout, $cmd . "\n");
    fflush($stdout);
    return fgets($stdin, 1024);        // read Asterisk's "200 result=..." reply
}

// ... read the agi_* env block first (previous slide) ...
command('VERBOSE "AGI started" 1');
command('SAY NUMBER 4000 ""');         // speak the extension back
?>
```

<div class="mt-2 text-sm opacity-70">
Always read the reply after every command, or the script and Asterisk fall out of step.
</div>

---
layout: default
---

# Calling AGI from the dial plan + FastAGI

<div grid="~ cols-2 gap-8">
<div>

### Local AGI

The script runs on the Asterisk box.

```ini
exten => 4000,1,Answer()
 same => n,AGI(test.php)
 same => n,Hangup()
```

`DeadAGI(...)` in the `h` extension runs after hangup.

</div>
<div>

### FastAGI — offload the CPU

The script runs on **another** server over TCP (default port **4573**), addressed with `agi://`.

```ini
exten => 0800400001,1,AGI(agi://192.168.0.1)
```

Lose the TCP connection and the AGI — and the call — ends.

</div>
</div>

<div class="mt-3 text-sm opacity-70">
For Java, the <strong>Asterisk-Java</strong> library ships a ready-made FastAGI server (github.com/asterisk-java/asterisk-java).
</div>

---
layout: default
---

# AMI vs. AGI vs. ARI

<div class="text-sm">

| | **AMI** | **AGI** | **ARI** |
|---|---|---|---|
| **Shape** | TCP line protocol (`Key: value`) | Script over stdin/stdout | REST + WebSocket (JSON) |
| **Direction** | Events out, actions in | Asterisk drives the script | App drives Asterisk |
| **Scope** | Whole-server state & control | One channel, per call | Channels & bridges, full control |
| **Classic use** | Dialers, CTI, monitoring | IVR + database lookups | Custom call apps |
| **Config** | `manager.conf` :5038 | `agi-bin/` (or `agi://` :4573) | `ari.conf` + `http.conf` |

</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Rule of thumb: <strong>AGI</strong> to script a single call, <strong>AMI</strong> to watch and drive the whole PBX, <strong>ARI</strong> when you want to build the call flow yourself — covered in the next chapter.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Extend Asterisk with AMI and AGI**

Enable `manager.conf`, log in to AMI and `Originate` a call,
then drop a PHP AGI script in `agi-bin/` and call it from the dial plan.

See the **AMI/AGI lab** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Runs on the Asterisk 22 Docker lab — no hardware required.
</div>

---
layout: section
---

# Summary

---
layout: default
---

# Summary

<v-clicks>

- **`asterisk -rx`** and **`System()`** are the quick doors — shell commands and dial plan calls.
- **AMI** is a TCP line protocol of `Key: value` packets — **actions** in, **events** out — enabled in `manager.conf` on port **5038**.
- **`ActionID`** correlates asynchronous responses; query **`manager show commands`** and **`manager show events`** for the live set.
- **AGI** hands a channel to an external script over **stdio** — flavors are **AGI, DeadAGI, EAGI, FastAGI** (TCP :4573).
- Pick **AGI** for per-call logic, **AMI** for server-wide control, **ARI** for full custom apps.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>The Asterisk REST Interface (ARI)</strong> — the modern REST + WebSocket way to control calls.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 14 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which AMI header correlates an asynchronous response back to the action that triggered it?</em>
</div>
