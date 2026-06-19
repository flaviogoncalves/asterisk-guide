---
theme: seriph
title: 'The Dial Plan — Advanced Features'
info: |
  ## Asterisk Guide — Chapter 10
  The Dial Plan: advanced features. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# The Dial Plan

Chapter 10

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

- **Simplify** extension entries with the `same =>` keyword
- **Secure** the dial plan by filtering dialed digits
- **Receive** calls with an IVR / auto-attendant menu
- **Reuse** dial plan logic with `GoSub` subroutines (not Macro)
- **Control** access with context inclusion and `#include`
- **Implement** follow-me, DND, and blacklists with AstDB
- **Schedule** after-hours behavior with time-based routing
- **Add** voicemail, MWI, and a corporate directory

</v-clicks>

<!--
This is the advanced dial plan chapter — building on the basics from Chapter 3.
Everything is Asterisk 22, PJSIP-only, GoSub-only, comma separators.
-->

---
layout: section
---

# Extensions, priorities & patterns

---

# Contexts, extensions, priorities

The dial plan lives in `extensions.conf`. A **context** groups **extensions**; each extension is a list of **priorities** executed in order.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**The `same =>` shortcut**

Reuse the current extension to cut typos.

```ini
exten => 4000,1,NoOp()
same  =>      n,Dial(PJSIP/005C2B313E22)
```

`n` means "next priority" — no need to renumber.

</div>
<div>

**Golden rules of contexts**

1. A channel may only dial extensions **in its own context**.
2. The context is set in the **channel config** — for SIP that is the `context=` line in the endpoint in `pjsip.conf`.

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Troubleshooting <em>"number not found"</em>? Check the endpoint's <code>context=</code> in <code>pjsip.conf</code>, then confirm the dialed number exists in <strong>that</strong> context.
</div>

---

# Pattern matching

Patterns start with `_` and match families of numbers.

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

| Token | Matches |
|-------|---------|
| `X` | any digit `0–9` |
| `N` | any digit `2–9` |
| `Z` | any digit `1–9` |
| `.` | one or more of any character |
| `[1-5]` | a range / set |

`${EXTEN}` is the dialed number; `${EXTEN:1}` strips the first digit.

</div>
<div>

**Best match wins — check the order**

```text
CLI> dialplan show example
```

```ini
[example]
exten => _912.,1,Dial(DAHDI/1/${EXTEN})
exten => _9.,1,Dial(DAHDI/2/${EXTEN})
```

`912…` matches the **more specific** pattern.
An **included** context is always evaluated *after* patterns in the including context.

</div>
</div>

---
layout: section
---

# Securing the dial plan

---

# Filtering dialed digits

A classic injection flaw: SIP accepts alphanumerics, so a malicious user could dial
`3000&DAHDI/1/011551123456789` and fork a second, international call.

<div class="mt-2">

```ini
; Vulnerable — passes the raw, attacker-controlled string straight to Dial()
exten => _X.,1,Dial(PJSIP/${EXTEN})

; Safe — FILTER() keeps only digits 0-9 before dialing
exten => _X.,1,Dial(PJSIP/${FILTER(0-9,${EXTEN})})
```

</div>

<div class="mt-4 text-sm opacity-70">
The <code>&amp;</code> separator inside <code>Dial()</code> rings several channels <strong>at once</strong> — never trust an unfiltered <code>${EXTEN}</code> in a dial string. See <code>README-SERIOUSLY.bestpractices.txt</code>.
</div>

---

# Context inclusion & #INCLUDE

Two different mechanisms with similar names — don't confuse them.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**`include =>` (a context)**

Pulls one **context** into another so callers gain access to its extensions. Layer classes of service:

```ini
[restrict]
exten => _2000,1,Dial(PJSIP/2000,20,t)

[ld]
include => restrict
exten => _9NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1},20)

[ldi]
include => ld
exten => _901X.,1,Dial(DAHDI/g1/${EXTEN:1},20)
```

</div>
<div>

**`#include` (a file)**

A preprocessor directive that splits configuration across **files**.

```ini
#include "users.conf"
#include "services.conf"
```

Use it to keep `extensions.conf` manageable — local users in one file, special services in another.

</div>
</div>

---
layout: section
---

# Building an IVR / auto-attendant

---

# The applications behind an IVR

Read each application's help with `core show application <name>`.

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

- **`Background()`** — play prompt(s) **while listening** for digits. Options: `s` (skip if not up), `n` (don't answer), `m` (break only on a one-digit match).
- **`WaitExten()`** — keep waiting for digits **after** `Background()` finishes.
- **`Read()`** — collect a fixed number of digits into a variable.

</div>
<div>

- **`Playback()`** — play file(s); no digit collection. Sets `${PLAYBACKSTATUS}` (`SUCCESS`/`FAILED`).
- **`Record()`** — record the channel to a file; `#` stops, `%d` auto-increments the name.
- **`GotoIf()`** — branch on a condition: `?labeliftrue:labeliffalse`.

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
With <code>Background()</code> the caller can press a digit <strong>during</strong> playback — they need not wait for the prompt to finish.
</div>

---

# Reading digits from the caller

`Read()` plays a file, then captures DTMF into a variable you can branch on.

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

```ini
exten => s,1,Read(choice,welcome,1)
same  =>   n,GotoIf($["${choice}" = "1"]?sales,s,1)
same  =>   n,GotoIf($["${choice}" = "2"]?support,s,1)
same  =>   n,Goto(operator,s,1)
```

</div>
<div>

`Read(variable,filename,maxdigits,option,attempts,timeout)`

- **maxdigits** — stop after N digits (`0` = wait for `#`)
- **option** — `s` return if not up · `i` play as indication tone · `n` read even if not up
- **attempts** / **timeout** — retries and per-digit wait

</div>
</div>

![The Read() application help](/images/10-dialplan-advanced-features-img04.png)

---

# Matching as you dial

`Background()` reads the **current context** and finds the longest match — so avoid ambiguous numbering.

<div grid="~ cols-2 gap-8" class="mt-1">
<div>

```ini
[incoming]
exten => s,1,Background(welcome)
exten => 1,1,Dial(DAHDI/1)
exten => 2,1,Dial(DAHDI/2)
exten => 21,1,Dial(DAHDI/3)
exten => 22,1,Dial(DAHDI/4)
exten => 31,1,Dial(DAHDI/5)
exten => 32,1,Dial(DAHDI/6)
```

</div>
<div class="text-sm">

- `1` → calls **immediately** (no longer match exists)
- `2` → **waits** for the timeout (could become `21`/`22`)
- `21`,`22`,`31`,`32` → call immediately

**Lesson:** don't mix `2`, `21`, and `22` in the same menu — callers want a fast answer.

</div>
</div>

---
layout: section
---

# Subroutines with GoSub

---

# GoSub — not Macro

The old `Macro` application (`app_macro`) was **removed in Asterisk 21**. Use **`GoSub`** for all subroutines.

```text
GoSub([[context,]exten,]priority[(arg1[,...][,argN])])
```

<div grid="~ cols-2 gap-8 text-sm" class="mt-2">
<div>

**Define once** — a standard extension with voicemail fallback:

```ini
[stdexten]
exten => s,1,Dial(${ARG1},20,tT)
exten => s,n,Goto(${DIALSTATUS})
exten => s,n,Hangup()
exten => s,n(BUSY),VoiceMail(${ARG2},b)
exten => s,n,Hangup()
exten => s,n(NOANSWER),VoiceMail(${ARG2},u)
exten => s,n,Hangup()
exten => s,n(CONGESTION),Hangup()
```

</div>
<div>

**Call it** — pass args inside parentheses; read them as `${ARG1}`, `${ARG2}`:

```ini
exten => 6000,1,GoSub(stdexten,s,1(PJSIP/6000,${EXTEN}))
exten => 6001,1,GoSub(stdexten,s,1(PJSIP/6001,${EXTEN}))
exten => 6002,1,GoSub(stdexten,s,1(PJSIP/6002,${EXTEN}))
```

`${DIALSTATUS}` drives the branch — one routine serves every extension.

</div>
</div>

---
layout: section
---

# AstDB — storing dial plan data

---

# Asterisk database (AstDB)

A built-in key/value store organized into **families** and **keys** — like a registry. Data persists across restarts.

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**Functions**

```ini
; write
exten => _*21*XXXX,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})
; read
exten => s,1,Set(temp=${DB(CFIM/${EXTEN})})
```

- `${DB(family/key)}` — read
- `DB(family/key)=value` — write
- `${DB_EXISTS(family/key)}` — test
- `${DB_DELETE(family/key)}` — delete one key
- `DBdeltree(family)` — delete a subtree

</div>
<div>

**CLI**

```text
CLI> database put blacklist 5551234 1
CLI> database get  blacklist 5551234
CLI> database show blacklist
CLI> database del  blacklist 5551234
CLI> database deltree blacklist
```

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
In Asterisk 22, AstDB is backed by <strong>SQLite3</strong> (<code>/var/lib/asterisk/astdb.sqlite3</code>) — not the legacy Berkeley DB v1. The <code>DBdel()</code> application was removed; delete one key with the <code>DB_DELETE()</code> function.
</div>

---

# Follow-me, DND & blacklists

Program features with feature codes that write to AstDB.

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**Families**

- `CFIM` — Call Forward Immediate
- `CFBS` — Call Forward on Busy
- `DND` — Do Not Disturb

**Feature codes**

- `*21*` / `#21#` — set / cancel forward immediate
- `*61*` / `#61#` — set / cancel forward on busy
- `*41*` — toggle do-not-disturb
- `*31*` / `#31#` — add / remove blacklist entry

</div>
<div>

**Blacklist (modern form)**

`LookupBlacklist()` was removed — build it with `DB_EXISTS()` + `GotoIf`:

```ini
exten => s,1,GotoIf($[${DB_EXISTS(blacklist/${CALLERID(num)})}]?blocked,s,1)
exten => s,n,Dial(PJSIP/4000,20,tT)
exten => s,n,Hangup()

[blocked]
exten => s,1,Answer()
exten => s,n,Playback(blockedcall)
exten => s,n,Hangup()
```

</div>
</div>

---
layout: section
---

# Time-based routing & DISA

---

# After-hours: time conditions

Two ways to branch on the clock — both use **commas** as separators in Asterisk 22 (the old pipe form silently fails).

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**Time-based context include**

```ini
include => context,<times>,<weekdays>,<mdays>,<months>
```

```ini
[incoming]
include => normalhours,08:00-18:00,mon-fri,*,*
include => afterhours,18:00-23:59,*,*,*
include => afterhours,00:00-07:59,*,*,*
include => afterhours,*,sat-sun,*,*
```

</div>
<div>

**`GotoIfTime()`**

```ini
GotoIfTime(times,weekdays,mdays,months[,tz]?label)
```

```ini
exten => s,1,GotoIfTime(8:00-18:00,mon-fri,*,*?normalhours,s,1)
```

Branches to `normalhours,s,1` during business hours, Monday–Friday. An optional timezone field is supported.

</div>
</div>

---

# DISA & limiting simultaneous calls

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**DISA — a second dial tone**

Lets a caller dial again through the PBX (e.g. for outbound LD on the company's line).

```ini
exten => s,1,DISA(no-password,default)
```

`DISA(passcode|filename[,context[,cid…]])` — calls run in `default` here; without a context the `disa` context is assumed. Use a passcode file in production.

</div>
<div>

**Cap calls with `GROUP()`**

Limit a destination to two concurrent calls (e.g. a 64K leased line):

```ini
exten => _214X,1,Set(GROUP()=Rio)
same  =>      n,GotoIf($[${GROUP_COUNT()} > 1]?outoflimit)
same  =>      n,Dial(PJSIP/${EXTEN})
same  =>      n,Hangup()
same  =>      n(outoflimit),Playback(callsexceedcapacity)
same  =>      n,Hangup()
```

</div>
</div>

---
layout: section
---

# Voicemail & the directory

---

# Configuring voicemail

Three steps: general settings, mailboxes, and dial plan wiring.

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**`voicemail.conf`**

```ini
[general]
format=wav49|gsm
serveremail=pbx@voip.school
maxmsg=100
maxsecs=180
minsecs=3
maxsilence=5

[default]
1234 => 1234,Some User,user@voip.school
```

`mailboxID => pin,fullname,email,pager,options`

</div>
<div>

**Wire it in `extensions.conf`**

```ini
; leave a message (busy greeting)
exten => 9008,1,VoiceMail(4401@default,b)
exten => 9008,n,Hangup()

; mailbox owner self-service
exten => 9000,1,VoiceMailMain()
exten => 9000,n,Hangup()
```

`VoiceMail()` sets `${VMSTATUS}` (`SUCCESS`/`USEREXIT`/`FAILED`). Options: `b` busy, `u` unavailable, `s` skip instructions, `U` urgent.

</div>
</div>

---

# MWI, email & the directory

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**Message Waiting Indication (PJSIP)**

Set the mailbox hint in the **endpoint** section of `pjsip.conf` — handled by `res_pjsip_mwi`:

```ini
[4401]
type=endpoint
mailboxes=4401@default
```

**Voicemail to email**

```ini
attach=yes
delete=yes
mailcmd=/usr/sbin/sendmail -t
```

The MTA (Exim on Debian) delivers the message with the audio attached.

</div>
<div>

**Corporate directory**

Look callers up by name from `voicemail.conf`:

```ini
exten => 9007,1,Directory(default,default)
exten => 9007,n,Hangup()
```

`Directory([vm-context][,dial-context[,options]])` — `e` read the extension, `f`/`l`/`b` first/last/both name, `m` build a menu.

</div>
</div>

![The Comedian Mail / vmail.cgi web voicemail login](/images/10-dialplan-advanced-features-img14.png)

---

# Putting it all together

A complete PBX: 4 analog trunks, 16 SIP extensions, classes of service, after-hours, auto-attendant.

<div grid="~ cols-2 gap-8 text-sm" class="mt-1">
<div>

**Endpoints by class of service** (`pjsip.conf` templates)

```ini
[endpoint-base](!)
type=endpoint
disallow=all
allow=ulaw,gsm
direct_media=yes

[00001A000002](endpoint-base)
context=restrict
auth=00001A000002
aors=00001A000002
mailboxes=20
```

Each device's `context=` decides what it may dial.

</div>
<div>

**Auto-attendant** (`extensions.conf`)

```ini
[globals]
OPERATOR=PJSIP/2060
SALES=PJSIP/2035

[mainmenu]
exten => s,1,Background(welcome)
exten => 1,1,Goto(sales,s,1)
exten => 2,1,Goto(techsupport,s,1)
exten => i,1,Playback(Invalid)
exten => i,n,Hangup()
exten => t,1,Dial(${OPERATOR},20,Tt)
include => restrict
```

</div>
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**A dial plan with an auto-attendant (IVR)**

Build an `[ivr]` context: play a prompt with `Background()`, route `1`/`2`/`0`,
and handle the `i` (invalid) and `t` (timeout) extensions. Dial **500** to enter it.

See **Lab 2** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Verify with <code>dialplan show ivr</code> — you should see <code>start</code>, <code>1</code>, <code>2</code>, <code>0</code>, <code>i</code>, <code>t</code>.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- The dial plan is **contexts → extensions → priorities**; `same =>` and `${EXTEN:n}` keep it tidy.
- **Filter dialed digits** (`FILTER(0-9,…)`) — never pass a raw `${EXTEN}` into a dial string.
- Build IVRs with **`Background`**, **`WaitExten`**, **`Read`**, and **`GotoIf`**.
- Reuse logic with **`GoSub`** — `Macro` was removed in Asterisk 21.
- **AstDB** (SQLite3 in Asterisk 22) stores follow-me, DND, and blacklist state.
- **Comma**-separated time fields drive `include =>` and `GotoIfTime()`; DISA gives a second dial tone.
- **Voicemail** ties in via `VoiceMail`/`VoiceMailMain`, PJSIP `mailboxes=` MWI, and the `Directory` app.

</v-clicks>

<div class="mt-4 text-sm opacity-70">
Next: <strong>PBX Features</strong> — transfers, parking, pickup, and ConfBridge.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 10 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>In Asterisk 22, which character separates the fields of a time-based <code>include =></code> and of <code>GotoIfTime()</code>?</em>
</div>
