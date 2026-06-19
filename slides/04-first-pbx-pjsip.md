---
theme: seriph
title: 'Building Your First PBX (PJSIP)'
info: |
  ## Asterisk Guide — Chapter 3
  Building Your First PBX with PJSIP. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Building Your First PBX (PJSIP)

Chapter 3

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

- **Understand** and edit Asterisk configuration files
- **Install** SIP soft-phones and **configure** SIP extensions in `pjsip.conf`
- **Configure** a SIP trunk to reach the PSTN
- **Configure** an analog connection with DAHDI
- **Dial** between extensions and to external destinations
- **Build** an auto-attendant (digital receptionist)

</v-clicks>

<!--
Goal of this chapter: get a PBX running, dial between extensions, play a prompt, run an echo test.
-->

---
layout: section
---

# Understanding the configuration files

---

# The /etc/asterisk config files

Asterisk is controlled by text files in `/etc/asterisk`. The format resembles Windows `.ini`.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

- `;` is the comment character
- `=` and `=>` are **equivalent** to the parser
- Convention: `=` declares a **variable**, `=>` designates an **object**
- Spaces are ignored

</div>
<div>

```ini
;
; First non-comment line is the section title.
;
[section]
key = value      ; variable designation
[section2]
key => value     ; object declaration
```

</div>
</div>

---

# Three grammars, one syntax

<div class="text-sm">

| Grammar | How the object is created | Conf. file | Example |
|---------|---------------------------|------------|---------|
| **Simple Group** | All on the same line | `extensions.conf` | `exten => 4000,1,Dial(PJSIP/4000)` |
| **Option Inheritance** | Options first; the object inherits them | `chan_dahdi.conf` | `signalling=fxs_ks` then `channel => 1` |
| **Complex Entity** | Each entity receives its own context | `pjsip.conf`, `iax.conf` | `[cisco]` → `type=endpoint` … |

</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<code>pjsip.conf</code> uses the <strong>complex entity</strong> grammar — each <code>endpoint</code>, <code>auth</code>, and <code>aor</code> is its own section.
</div>

---
layout: image-right
image: /images/04-first-pbx-fig01.png
backgroundSize: contain
---

# Planning the lab

The reference layout: phones as **extensions**, the **Asterisk server**, and **trunks** to the PSTN.

**Installation sequence**

<v-clicks>

1. Configure **extensions** (SIP, IAX, FXS)
2. Configure **trunks** (SIP trunk, FXO)
3. Build a basic **dial plan** — dial between extensions, reach the PSTN, receive calls, auto-attendant

</v-clicks>

---
layout: section
---

# Configuring SIP extensions (PJSIP)

---

# PJSIP is the SIP driver in Asterisk 22

SIP phones are configured in `/etc/asterisk/pjsip.conf` via the `res_pjsip` stack.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

- The **only** SIP driver shipped with Asterisk 22
- Multiple transports per endpoint
- Actively maintained

</div>
<div>

- Built-in protection against username guessing
- Identical auth challenge for known/unknown users
- Unidentified requests rate-limited per IP

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>chan_sip was removed in Asterisk 21</strong> — it does not exist in Asterisk 22. See the <em>Legacy Channels</em> chapter only if you must migrate an old config.
</div>

---

# The transport

The listener (bind address, port, protocol) lives in a `transport` object.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**Options**

- `protocol` — `udp`, `tcp`, `tls`, `ws`, or `wss`
- `bind` — address:port; `0.0.0.0` binds all interfaces; SIP defaults to **5060**

Codec choice and `context` live on each **endpoint**, not the transport.

</div>
<div>

```ini
[global]
type=global

[transport-udp]
type=transport
protocol=udp
bind=10.1.30.45:5060
```

</div>
</div>

---

# A SIP client = endpoint + auth + aor

Three related objects, tied together by name reference:

<div grid="~ cols-3 gap-4 text-sm mt-2">
<div>

**`endpoint`**
Call behaviour: codecs (`allow`/`disallow`), the dialplan `context`, and which `auth` and `aors` it uses.

</div>
<div>

**`auth`**
The credentials. `username` is the SIP auth user; `password` is the device secret.

</div>
<div>

**`aor`**
Address of record — `contact=` for a fixed IP, or `max_contacts=` to let the device register.

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Use strong passwords</strong> — 8+ chars, alphanumeric, with a symbol. SIP brute-force tools are everywhere; toll fraud is expensive.
</div>

---

# Two endpoints: fixed-IP vs. registering

<div grid="~ cols-2 gap-6 text-sm">
<div>

**6000 — device at a fixed IP** (static `contact`)

```ini
[6000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6000-auth
aors=6000

[6000-auth]
type=auth
auth_type=digest
username=6000
password=#MySecret1#7

[6000]
type=aor
contact=sip:6000@10.1.30.50
```

</div>
<div>

**6001 — device that registers** (`max_contacts`)

```ini
[6001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=digest
username=6001
password=Mys3cr3t#

[6001]
type=aor
max_contacts=1
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
A registering device learns its contact dynamically — its AOR needs no static <code>contact</code>.
</div>

---
layout: image-right
image: /images/softphone/sipphone-account.png
backgroundSize: contain
---

# Configuring the soft-phone

X-Lite is discontinued — use any modern free SIP soft-phone (Zoiper, Linphone, MicroSIP).

**Account settings for 6000**

- **Server / Domain** — your Asterisk IP
- **Username / Auth user** — `6000`
- **Password** — `#MySecret1#7`
- **Transport** — UDP, TCP, or TLS

Repeat for `6001`.

---
layout: image-right
image: /images/softphone/sipphone-registered.png
backgroundSize: contain
---

# Confirming registration

Verify from the Asterisk CLI:

```text
CLI> pjsip show endpoints
CLI> pjsip show endpoint 6000
CLI> pjsip show contacts
```

A registered endpoint reports **`Not in use`** instead of `Unavailable`; the green dot on the phone and the account line confirm it on the device side.

---
layout: section
---

# IAX extensions (legacy)

---

# IAX extensions still ship — but are legacy

`chan_iax2` remains in Asterisk 22, configured in `iax.conf`. SIP/PJSIP is preferred for new work.

<div grid="~ cols-2 gap-6 text-sm">
<div>

**`[general]`**

```ini
[general]
bindport = 4569
bindaddr = 10.1.30.45 ;(use your IP)
context = dummy
delayreject=yes
bandwidth=high
disallow = all
allow = ulaw
```

</div>
<div>

**IAX clients**

```ini
[6003]
type=friend
host=dynamic
secret=#sup3rs3cr3t#
context=from-internal

[6004]
type=friend
host=dynamic
secret=#s3cr3ts3cr3t#
context=from-internal
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
<code>type</code>: <code>peer</code> (Asterisk sends to it), <code>user</code> (Asterisk receives from it), or <code>friend</code> (both). The SipPulse Softphone is SIP-only — use a client that still supports IAX to test.
</div>

---
layout: section
---

# Connecting to the PSTN

---
layout: image-right
image: /images/04-first-pbx-fig02.png
backgroundSize: contain
---

# FXO and FXS ports

To reach the PSTN you need an **FXO** interface and a telephone line.

<v-clicks>

- **FXS** drives an analog phone — supplies dial tone and ring
- **FXO** connects Asterisk to the **Telco line**
- Use any **DAHDI-compatible** card

</v-clicks>

<div class="mt-4 text-sm opacity-70">
The old X100P clone is unreliable on modern boards — avoid it for production.
</div>

---

# Analog lines with DAHDI

After installing the DAHDI drivers (`make config`, then reboot), detect and configure the card.

<div grid="~ cols-2 gap-8 text-sm">
<div>

```bash
dahdi_hardware     # detect the card
dahdi_genconf      # generate config
```

Generates `/etc/dahdi/system.conf` and `/etc/asterisk/dahdi-channels.conf`.

</div>
<div>

In the last line of `chan_dahdi.conf`:

```ini
#include dahdi-channels.conf
```

Verify the channels:

```text
CLI> dahdi show channels
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
FXO lines land in context <code>from-pstn</code>; FXS phones in <code>from-internal</code> by default.
</div>

---

# A SIP trunk to a VoIP provider

In PJSIP a registering trunk reuses the endpoint family plus `registration` and `identify`.

<div grid="~ cols-2 gap-6 text-sm">
<div>

```ini
[siptrunk]
type=endpoint
context=from-sip
disallow=all
allow=ilbc
allow=alaw
allow=g729
dtmf_mode=rfc4733
outbound_auth=siptrunk-auth
aors=siptrunk
from_user=login
from_domain=domain

[siptrunk-auth]
type=auth
auth_type=digest
username=login
password=secret
```

</div>
<div>

```ini
[siptrunk]
type=aor
contact=sip:domain:5060

[siptrunk]
type=identify
endpoint=siptrunk
match=domain

[siptrunk-reg]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:domain:5060
client_uri=sip:login@domain:5060
contact_user=9999
retry_interval=60
```

</div>
</div>

<div class="mt-1 text-sm opacity-70">
PJSIP authenticates inbound INVITEs by source IP (<code>identify</code>/<code>match</code>). Dial the trunk as <code>PJSIP/...@siptrunk</code>. Confirm with <code>pjsip show registrations</code>.
</div>

---
layout: section
---

# The dial plan

---
layout: image-right
image: /images/04-first-pbx-fig03.png
backgroundSize: contain
---

# Contexts route every call

Most of the dial plan lives in `extensions.conf` (simple-group grammar). Four concepts:

<v-clicks>

- **Extensions** — a list of instructions for a number or name
- **Priorities** — the order of execution
- **Applications** — the features invoked
- **Contexts** — named partitions of the dial plan

</v-clicks>

<div class="mt-4 text-sm opacity-70">
A channel's <code>context=</code> (in <code>pjsip.conf</code> / <code>chan_dahdi.conf</code>) names the context that processes its calls.
</div>

---
layout: image-right
image: /images/04-first-pbx-fig05.png
backgroundSize: contain
---

# Extensions, priorities, applications

An extension is a list of commands run in **priority order**.

```ini
exten => 123,1,Answer()
exten => 123,n,Playback(tt-weasels)
exten => 123,n,Hangup()
```

<div class="text-sm mt-2">

- Priority `1` runs first, then `n` (next), and so on
- Extensions can be numeric, alphanumeric, a **pattern**, or special (`s`)
- `/` after the extension matches on **caller ID**

</div>

---
layout: image-right
image: /images/04-first-pbx-fig06.png
backgroundSize: contain
---

# Pattern matching

Patterns shrink the dial plan. Every pattern starts with `_`.

<div class="text-sm">

- `X` — any digit `0–9`
- `Z` — `1–9`
- `N` — `2–9`
- `[123-7]` — any listed digit or range
- `.` — one or more characters
- `!` — zero or more characters

</div>

```ini
exten => _4XXX,1,Dial(PJSIP/${EXTEN})
```

---
layout: image-right
image: /images/04-first-pbx-fig07.png
backgroundSize: contain
---

# Special extensions

Asterisk reserves certain extension names:

<div class="text-sm">

- `s` — **start** (no dialed number; FXO trunks, menus)
- `i` — **invalid** extension
- `h` — **hangup** (after the user disconnects)
- `t` — **timeout** (line idle after a prompt)
- `T` — absolute timeout
- `o` — operator
- `fax` — fax detection

</div>

<div class="mt-3 text-sm opacity-70">
Using <code>s</code>/<code>i</code>/<code>o</code> can affect the <code>dst</code> field in CDRs.
</div>

---
layout: image-right
image: /images/04-first-pbx-fig09.png
backgroundSize: contain
---

# A handful of applications

You only need a few to build a simple PBX:

<div class="text-sm">

- **`Answer()`** — answer a ringing channel
- **`Dial()`** — call another channel
- **`Hangup()`** — hang up
- **`Playback()`** — play an audio file (no digits)
- **`Background()`** — play a file **and wait** for digits
- **`Goto()`** — jump to a priority / extension / context

</div>

<div class="mt-3 text-sm opacity-70">
In Asterisk 22, <code>Dial</code> options are comma-separated: <code>Dial(PJSIP/2000,20,tTm)</code>.
</div>

---

# Dialing: internal and external

<div grid="~ cols-2 gap-6 text-sm">
<div>

**Between extensions** (4000–4999, all SIP)

```ini
[from-internal]
exten => _4XXX,1,Dial(PJSIP/${EXTEN})
```

**To the PSTN — dial 9 first**

```ini
[from-internal]
exten => _9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20,tT)
```

</div>
<div>

**Over the SIP trunk instead of DAHDI**

```ini
[from-internal]
exten => _9NXXXXXX,1,Dial(PJSIP/${EXTEN:1}@siptrunk,20,tT)
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
<code>${EXTEN:1}</code> strips the leading <code>9</code>. <code>g1</code> hunts the first free channel in DAHDI group 1. <code>tT</code> lets either party transfer.
</div>

---

# Receiving calls: operator & DID

<div grid="~ cols-2 gap-6 text-sm">
<div>

**No DID — send to the operator via `s`**

```ini
[globals]
OPERATOR=PJSIP/6000

[from-pstn]
exten => s,1,Dial(${OPERATOR},40,tT)
exten => s,n,Hangup()

[from-sip]
exten => s,1,Dial(${OPERATOR},40,tT)
exten => s,n,Hangup()
```

</div>
<div>

**With DID — route by the dialed digits**

```ini
[from-pstn]
exten => _85[5-9]X,1,Answer()
exten => _85[5-9]X,n,Dial(PJSIP/${EXTEN},15,tT)
exten => _85[5-9]X,n,Hangup()
```

</div>
</div>

---

# A digital receptionist (auto-attendant)

`Background()` plays a menu and waits; `Goto()` and `WaitExten()` route the choice.

<div grid="~ cols-2 gap-6 text-sm">
<div>

```ini
[globals]
OPERATOR=PJSIP/6000

[from-sip]
include=aasip

[aasip]
exten => 9999,1,Answer()
exten => 9999,n,Set(TIMEOUT(response)=10)
exten => 9999,n,Background(menu1)
exten => s,n,WaitExten(30)
exten => 9999,n,Dial(${OPERATOR})
```

</div>
<div>

```ini
exten => 6000,1,Dial(PJSIP/6000)
exten => 6001,1,Dial(PJSIP/6001)
exten => 6003,1,Dial(IAX2/6003)
exten => 6004,1,Dial(IAX2/6004)
```

SIP extensions use `PJSIP/`; IAX use `IAX2/`. Record `menu1` with *"press the extension or wait for the operator."*

</div>
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Your first PBX — register two phones and call**

Boot the Asterisk 22 Docker lab, register **`6001`** and **`6002`**, call between them, and run the **echo test** on `600`.

See **Lab 0 & Lab 1** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Verify with <code>pjsip show endpoints</code> — registered phones show <strong>Not in use</strong>.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk config files live in **`/etc/asterisk`** and use three grammars: **simple group**, **option inheritance**, and **complex entity**.
- SIP phones are configured in **`pjsip.conf`** as **`endpoint` + `auth` + `aor`** — `chan_sip` is gone in Asterisk 22.
- A **transport** sets the listener; a **SIP trunk** adds `registration` and `identify`.
- The **dial plan** in `extensions.conf` is a set of **contexts**, each with **extensions**, **priorities**, and **applications**.
- A few apps — `Answer`, `Dial`, `Hangup`, `Playback`, `Background`, `Goto` — build a working PBX with an auto-attendant.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Designing a VoIP Network</strong> — codecs, NAT, and the media path.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 3 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>On Asterisk 22, which set of PJSIP objects replaces a single <code>chan_sip</code> peer?</em>
</div>
