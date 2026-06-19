---
theme: seriph
title: 'PBX Features'
info: |
  ## Asterisk Guide — Chapter 11
  Using PBX Features. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# PBX Features

Chapter 11

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

By the end of this chapter you will be able to understand and use:

<v-clicks>

- **Call parking** and **call pickup**
- **Call transfer** — blind and attended (consultative)
- **Call conference** with **ConfBridge**
- **Call recording** with `MixMonitor()`
- **Music on hold** classes
- **Call forwarding** patterns in the dial plan

</v-clicks>

<!--
In SIP, many features live in the endpoint, but Asterisk implements most of them in the PBX
itself — making it almost endpoint-independent. This chapter is about those PBX-side features.
-->

---
layout: section
---

# Where features are implemented

---
layout: image-right
image: /images/13-pbx-features-fig01.png
backgroundSize: contain
---

# Three places a feature can live

The same function is sometimes done by **both** the phone and Asterisk.

<div grid="~ cols-1 gap-2 text-sm mt-2">
<div>

**In Asterisk (the PBX core)**
Music on hold · call parking · call pickup · call recording · ConfBridge · blind & consultative transfer

**In the dial plan (`extensions.conf`)**
Call forward (busy / immediate / no-answer) · call filtering (blacklist) · do not disturb · redial

**In the phone's firmware**
Call on hold · blind/consultative transfer · three-way conference · message waiting indicator

</div>
</div>

---
layout: section
---

# The features configuration files

---

# features.conf and res_parking.conf

DTMF feature codes live in `features.conf`. Since Asterisk 12+, **parking moved to its own module** `res_parking` (`res_parking.conf`).

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

**`[featuremap]` in `features.conf`**

```ini
; features.conf
[featuremap]
;blindxfer => #     ; Blind transfer
;disconnect => *    ; Disconnect
;automon => *1      ; One-touch record (Monitor)
;atxfer => *2       ; Attended transfer
;parkcall => #72    ; One-step park
;automixmon => *3   ; One-touch MixMonitor
```

</div>
<div>

**Reloading**

```bash
asterisk -rx "module reload features.so"
asterisk -rx "module reload res_parking.so"
```

The default parking lot `default` always exists, even with no config file.

</div>
</div>

<div class="mt-3 text-sm opacity-70">
For <code>blindxfer</code>/<code>atxfer</code>, set the matching <strong>t</strong>/<strong>T</strong> option on <code>Dial()</code> or <code>Queue()</code>.
</div>

---
layout: image-right
image: /images/13-pbx-features-fig02.png
backgroundSize: contain
---

# The parking lot (res_parking.conf)

```ini
; res_parking.conf
[default]               ; Default Parking Lot
parkext => 700          ; Dial to park
parkpos => 701-720      ; Range of parking spaces
context => parkedcalls  ; Context for parked calls
;parkingtime => 45      ; Seconds before returning
;comebacktoorigin = yes ; Return to the peer that parked
;courtesytone = beep    ; Played on pickup
;findslot => next       ; next | first (default)
;parkedmusicclass = default
```

<div class="mt-2 text-sm opacity-70">
The <code>[featuremap]</code> DTMF codes (including <code>parkcall</code>) stay in <code>features.conf</code>.
</div>

---
layout: section
---

# Call transfer

---

# Blind vs. attended transfer

Transfer can be done by the phone, an ATA, or Asterisk itself.

<div grid="~ cols-2 gap-8 text-sm mt-2">
<div>

### Blind transfer

- Dial **#** followed by the destination number
- Change the trigger via `blindxfer` in `features.conf`
- No conversation with the destination first

</div>
<div>

### Attended (consultative)

- Enable by removing the `;` on `atxfer` in `features.conf`
- During the call, press **\*2**
- Asterisk says "transfer" and gives a dial tone; caller hears MoH
- Talk to the destination, then hang up to bridge

</div>
</div>

![Blind transfer (press # during the call) vs. attended transfer (press *2)](/images/13-pbx-features-fig03.png)

---

# Transfer — configuration task list

<v-clicks>

- If the phone is **SIP/PJSIP** based, make sure media flows through Asterisk so it can intercept DTMF:
  set `direct_media=no` on the endpoint, **or** use the `t`/`T` option on `Dial()`.

</v-clicks>

```ini
; pjsip.conf
[4x00]
type=endpoint
direct_media=no
```

```ini
; extensions.conf
exten => _4XXX,1,Dial(PJSIP/${EXTEN},20,tT)
```

<div class="mt-3 text-sm opacity-70">
The <code>t</code>/<code>T</code> options let the called/calling party transfer via the feature code.
</div>

---
layout: section
---

# Call parking & call pickup

---
layout: image-right
image: /images/13-pbx-features-fig04.png
backgroundSize: contain
---

# Call parking

Park a call to retrieve it from any phone.

<v-clicks>

- During a call, press **#** to send the call to the park extension **700**
- Asterisk announces a slot, e.g. **701** or **702**
- Hang up — the caller is held; dial that slot from your desk to retrieve it
- On timeout, the originally dialed extension rings again

</v-clicks>

```ini
; extensions.conf — make the lot reachable
include => parkedcalls
```

<div class="mt-2 text-sm opacity-70">
Parking extensions don't appear in <code>dialplan show</code>. Reload with <code>module reload res_parking.so</code>.
</div>

---
layout: image-right
image: /images/13-pbx-features-fig05.png
backgroundSize: contain
---

# Call pickup

Capture a ringing call from a colleague in **your** call group by dialing **\*8**.

```ini
; pjsip.conf  (snake_case options)
[4x00]
type=endpoint
call_group=1
pickup_group=1,2
```

```ini
; features.conf — change the pickup code (optional)
pickupexten = *8
```

<div class="mt-2 text-sm opacity-70">
Members capture only within their own group; an operator with <code>pickup_group=1,2,3</code> can pick up every group.
</div>

---
layout: section
---

# Conferencing with ConfBridge

---

# ConfBridge — the modern conference

For more than a phone's three-way call, run a conference room with `app_confbridge`.

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

- HD voice **and** video conferencing
- Video uses **follow-the-talker** (shows the last speaker)
- No transcoding for video — all participants share one codec/profile
- Custom DTMF menus per user

</div>
<div>

```ini
; extensions.conf
ConfBridge(conference,bridge_profile,user_profile,menu)
```

```bash
asterisk -rx "core show application confbridge"
```

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>MeetMe is gone in practice:</strong> <code>app_meetme</code> was deprecated in Asterisk 19 and is <strong>not built by the default Asterisk 22 build</strong> (it needs DAHDI). Use ConfBridge for all new deployments.
</div>

---
layout: image-right
image: /images/13-pbx-features-fig06.png
backgroundSize: contain
---

# ConfBridge profiles (confbridge.conf)

Three section types: **bridge**, **user**, and **menu**.

```ini
; confbridge.conf
[default_bridge]
type=bridge
max_members=10
record_conference=yes

[admin_user]
type=user
admin=yes

[my_menu]
type=menu
*=playback_and_continue
1=toggle_mute
2=decrease_listening_volume
3=increase_listening_volume
6=leave_conference
```

---

# ConfBridge — dynamic options with CONFBRIDGE()

Set bridge/user options on the fly from the dial plan with the `CONFBRIDGE()` function.

```ini
; extensions.conf
exten => 1,1,Answer()
exten => 1,n,Set(CONFBRIDGE(user,template)=default_user)
exten => 1,n,Set(CONFBRIDGE(user,admin)=yes)
exten => 1,n,Set(CONFBRIDGE(user,marked)=yes)
exten => 1,n,ConfBridge(sales)
```

<div class="mt-3 text-sm opacity-70">
<code>admin=yes</code> grants kick / mute-others / lock. <code>marked=yes</code> marks a key participant (e.g. to gate start/stop).
</div>

---
layout: section
---

# Call recording

---
layout: image-right
image: /images/13-pbx-features-fig09.png
backgroundSize: contain
---

# MixMonitor()

Records and **mixes** both legs of the channel to a single file.

```ini
; extensions.conf
exten => _4XXX,1,Set(DYNAMIC_FEATURES=automon)
exten => _4XXX,n,Dial(PJSIP/${EXTEN},20,jtTwW)
```

<div class="text-sm mt-2">

- **`automon`** — one-touch record: dial **\*1** to start recording mid-call (`wW` enables it)
- Options: `a` append · `b` only while bridged · `v`/`V`/`W(x)` volume (-4…4)
- A `<command>` can run when recording ends; `MIXMONITOR_FILENAME` holds the file

</div>

---

# Recording — globals and post-processing

Set the feature globally instead of before every `Dial()`:

```ini
; extensions.conf
[globals]
DYNAMIC_FEATURES => automon
```

Older split recordings (IN / OUT) land in `/var/spool/asterisk/monitor` and can be combined with `sox`:

```bash
soxmix *in.wav *out.wav output.wav
```

<div class="mt-3 text-sm opacity-70">
<code>MixMonitor()</code> writes one already-mixed file, so post-mixing is usually unnecessary.
</div>

---
layout: section
---

# Music on hold

---
layout: image-right
image: /images/13-pbx-features-fig10.png
backgroundSize: contain
---

# Music on hold classes

The modern default is **file-based** (`mode=files`) — no transcoding, no wasted CPU.

```ini
; musiconhold.conf
[default]
mode=files
directory=/var/lib/asterisk/moh

;[native-random]
;mode=files
;directory=/var/lib/asterisk/moh
;random=yes      ; Play files in random order
```

<div class="text-sm mt-2">
Valid modes: <code>files</code> (native), <code>quietmp3</code>, <code>mp3</code>, <code>mp3nb</code>, <code>custom</code>. Each section is a <strong>class</strong>.
</div>

---

# Using a MOH class

For **PJSIP** endpoints, suggest a class with `moh_suggest`:

```ini
; pjsip.conf
[4x00]
type=endpoint
moh_suggest=default
```

In the dial plan, set or test music on hold:

```ini
; extensions.conf
exten => 100,1,Set(CHANNEL(musicclass)=default)
exten => 100,n,Dial(PJSIP/2000)

exten => 6601,1,Answer()
exten => 6601,n,WaitMusicOnHold(30)
```

<div class="mt-2 text-sm opacity-70">
The legacy <code>musicclass</code> option name applies to <code>chan_dahdi</code> and other drivers — for PJSIP use <code>moh_suggest</code>.
</div>

---
layout: section
---

# Call forwarding & application maps

---

# Call forwarding in the dial plan

Forwarding is **not** a built-in feature — you program it in `extensions.conf`.

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

- **Forward immediate** — jump straight to the target
- **Forward on busy** — on `CHANUNAVAIL`/busy
- **Forward on no-answer** — after a timeout
- Pair with **DND**, **blacklist**, **redial** patterns

</div>
<div>

**Application maps** (`features.conf`)
Add new DTMF-triggered features via the `[applicationmap]` section — e.g. tag a call center customer type and run a `GoSub` to count answered calls per type.

</div>
</div>

```ini
; extensions.conf — forward on busy / no-answer
exten => 4000,1,Dial(PJSIP/4000,20)
exten => 4000,n,GotoIf($["${DIALSTATUS}" = "BUSY"]?busy:noanswer)
exten => 4000,n(busy),Goto(forward,4000,1)
exten => 4000,n(noanswer),Goto(forward,4000,1)
```

---
layout: center
class: text-center
---

# 🧪 Lab

**Voicemail — send missed calls to a mailbox**

Create two mailboxes, route unanswered calls to voicemail, and retrieve messages with **\*97**.

See **Lab 3 — Voicemail** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Mailboxes <code>6001</code>/<code>6002</code>, PIN <code>1234</code> · ~20 min · builds on Lab 1.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk implements most PBX features **in the core** — making it almost endpoint-independent.
- **Parking** lives in `res_parking.conf` (lot `default`, ext **700**, slots **701–720**); DTMF codes stay in `features.conf`.
- **Transfer** is **blind (#)** or **attended (\*2)** — keep media on Asterisk with `direct_media=no` or `Dial(...,tT)`.
- **Pickup** with **\*8** works within your `call_group`/`pickup_group`.
- **Conferencing is ConfBridge** (`confbridge.conf` + `CONFBRIDGE()`); MeetMe is not built by default in Asterisk 22.
- **`MixMonitor()`** (and one-touch **automon / \*1**) records calls; **MOH** defaults to file-based, set per PJSIP endpoint with `moh_suggest`.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Queues and Call Centers</strong>.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 11 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which extension parks a call by default, and which slots receive parked calls?</em>
</div>
