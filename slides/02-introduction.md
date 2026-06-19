---
theme: seriph
title: 'Introduction to Asterisk PBX'
info: |
  ## Asterisk Guide — Chapter 1
  Introduction to Asterisk PBX. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Introduction to Asterisk PBX

Chapter 1

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

- **Explain** what Asterisk is and what it does
- **Describe** the role of Digium™ and its successor Sangoma
- **Recognize** the basic architecture of Asterisk and its components
- **Point out** several usage scenarios
- **Identify** sources of information and help

</v-clicks>

<!--
Set expectations: this is the conceptual foundation before we touch a single config file.
-->

---
layout: section
---

# What is Asterisk?

---

# What is Asterisk?

Open-source software that turns an ordinary server into a powerful, multiprotocol PBX.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**You can use it to**

- Connect home workers to an office PBX over the Internet
- Link multiple offices over an IP network or the Internet
- Provide voicemail integrated with web and e-mail
- Build IVRs that reach your ordering or business systems
- Bridge PSTN ↔ VoIP in real time

</div>
<div>

**Advanced features once found only in high-end systems**

- Music on hold and call queues with live agent monitoring
- Text-to-speech and speech recognition integration
- Detailed records to text files **and** SQL databases
- PSTN connectivity over digital and analog lines

</div>
</div>

<div class="mt-4 text-sm opacity-70">
Sponsored by <strong>Sangoma Technologies</strong> (which acquired Digium in 2018) and a global open-source community.
</div>

---

# Classic Asterisk vs. FreePBX

<div grid="~ cols-2 gap-8">
<div>

### Classic Asterisk

- "Classic asterisk" = Asterisk in its purest form
- More a **development tool** than a finished product
- Configured in text files — what this book teaches
- The foundation under every distribution

</div>
<div>

### FreePBX (Sangoma)

- The standard **turnkey** distribution
- Web GUI + module ecosystem on top of Asterisk
- Free under the GPL — `www.freepbx.org`
- Commercial: **FreePBX Distro**, **PBXact**

*AsteriskNOW was an earlier soft-appliance — now discontinued.*

</div>
</div>

---

# Digium™ → Sangoma

<div class="mt-4">

- **Digium** (Huntsville, AL) created Asterisk in **1999** — primary developer, hardware maker, and sponsor (Switchvox for the SMB market).
- **2018:** Sangoma Technologies (Canada) **acquired Digium**.
- Sangoma is today the **primary steward**, funding development at `www.asterisk.org`.

</div>

<div class="mt-6 text-sm opacity-80">

**Licensing today:** Asterisk is distributed **solely under the GPL**.
(The old *Business Edition* and OEM commercial licenses have been discontinued.)

</div>

<!--
The Zapata project (Jim Dixon) gave Asterisk its open hardware design — Zaptel, later DAHDI —
using the PC CPU instead of dedicated DSPs to slash interface cost. Detail lives in the
Legacy Channels chapter.
-->

---
layout: section
---

# Why Asterisk?

---

# Why Asterisk?

<div grid="~ cols-2 gap-x-10 gap-y-3" class="mt-2">
<div>

**Extreme cost reduction**
Pays off most once you add voicemail, ACD, IVR, CTI.

**Control & independence**
Do-it-yourself; no vendor-locked passwords or hidden configs.

**Rapid development**
Extend with PHP/Perl via AMI & AGI; core is ANSI C.

</div>
<div>

**Feature rich**
Voicemail, ACD, IVR, MoH, recording — built in.

**Flexible, powerful dial plan**
Least-cost routing and complex logic are clean and easy.

**Open source on Linux**
Huge, active community; docs at `docs.asterisk.org`.

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
"Asterisk is to IP telephony what Apache is to web services."
</div>

---

# Addressing the common objections

<div class="text-sm">

| Objection | Reality |
|-----------|---------|
| *Market share is too small* | Free downloads go uncounted; Asterisk powers a huge installed base, from offices to carriers. |
| *If it's free, how does the vendor survive?* | Sangoma funds it via products (PBXact, Switchvox, FreePBX modules), hardware, and services. |
| *Hard to find support* | Sangoma + a global certified-partner network; active forums and mailing lists. |
| *More than 200 extensions?* | Yes — one well-sized server scales far, and you can cluster with load balancing/failover. |
| *Only "geeks" can install it* | FreePBX makes a medium-complexity PBX a few-hours job. |
| *What if the server fails?* | Fault-tolerant pairs are simple and cheap — try that with a legacy PBX. |

</div>

---
layout: image-right
image: /images/01-introduction-fig01.png
backgroundSize: contain
---

# Asterisk Architecture

The core bridges **channels** through **applications**, translating **codecs** as needed.

<v-clicks>

- **Channels** — the digital equivalent of a phone line
- **Codecs** — compress/translate the media
- **Protocols** — signaling that sets up the call
- **Applications** — the features (`Dial`, `VoiceMail`, …)

</v-clicks>

---

# Channels

A channel is a phone line in digital form — a codec + signaling combination.

<div grid="~ cols-2 gap-8" class="text-sm mt-2">
<div>

**VoIP**

- `chan_pjsip` — **SIP**, the only SIP driver in Asterisk 22. Dial: `PJSIP/endpoint`
- `chan_iax2` — IAX2, still ships but legacy. Dial: `IAX2/peer`
- `chan_unistim` — Nortel/Avaya phones (rarely used)

</div>
<div>

**PSTN & misc**

- `chan_dahdi` — analog (FXO/FXS) & digital (E1/T1/PRI) cards — *Legacy Channels chapter*
- **Local** — pseudo-channel that loops back into the dial plan. Dial: `Local/exten@context`

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>chan_sip was removed in Asterisk 21</strong> — it does not exist in Asterisk 22.
Every SIP example in this book is PJSIP.
</div>

---

# Codecs

Compression lets you fit many calls on one data network — rates beyond 8:1.

<div grid="~ cols-2 gap-8" class="text-sm">
<div>

- **G.711 µ-law / a-law** — 64 kbps (US / Europe)
- **G.722** — HD voice, 64 kbps
- **G.726** — 16/24/32/40 kbps
- **G.729** — 8 kbps (Sangoma binary module; per-channel license)
- **Opus** — 6–510 kbps, modern wideband

</div>
<div>

- **GSM** — 13 kbps
- **iLBC** — 13.3 kbps
- **Speex** — 2.15–44.2 kbps
- **G.723.1 / LPC10** — pass-through / very low rate

</div>
</div>

```text
CLI> core show translation     ; which codecs can convert to which
```

<div class="mt-2 text-sm opacity-70">
Asterisk converts via <code>slinear</code> internally; pass-through codecs can't be transcoded.
</div>

---

# Protocols & Applications

<div grid="~ cols-2 gap-8">
<div>

### Protocols

- **SIP** — via `chan_pjsip` *(dominant, default)*
- **IAX2** — legacy, still ships
- **UNISTIM** — Nortel/Avaya
- H.323 / MGCP / SCCP — legacy, not in a standard 22 build

</div>
<div>

### Applications

Features are applications invoked from the dial plan.

```text
CLI> core show applications
```

`Dial()` bridges two channels; `VoiceMail()`, `Queue()`, `ConfBridge()` add features. Add your own via add-ons or AGI.

</div>
</div>

---
layout: image-right
image: /images/01-introduction-fig02.png
backgroundSize: contain
---

# Overview of an Asterisk system

A hybrid PBX integrating **TDM** and **IP** telephony.

- Connects to PSTN and existing PBXs (analog + digital)
- Serves analog and IP phones
- Acts as soft-switch, media gateway, voicemail, conferencing
- Built-in music on hold, IVR, ACD

---

# The old world vs. telephony with Asterisk

<div grid="~ cols-2 gap-6">
<div>

**Old world** — buy and integrate separately

![Components bought separately](/images/01-introduction-fig03.png)

</div>
<div>

**With Asterisk** — the functions are integrated

![Functions integrated in Asterisk](/images/01-introduction-fig04.png)

</div>
</div>

---
layout: section
---

# Where Asterisk fits — usage scenarios

---

# Usage scenarios

<div grid="~ cols-3 gap-4 text-sm">
<div>

**IP PBX**
![IP PBX](/images/01-introduction-fig06.png)
The classic role: extensions, trunks, features.

</div>
<div>

**IP-enable a legacy PBX**
![IP-enable legacy PBX](/images/01-introduction-fig07.png)
Front a TDM PBX with SIP and VoIP trunks.

</div>
<div>

**Toll bypass**
![Toll bypass over WAN](/images/01-introduction-fig08.png)
Route inter-office calls over the WAN.

</div>
</div>

---

# Usage scenarios (cont.)

<div grid="~ cols-3 gap-4 text-sm">
<div>

**Application server**
![Application server](/images/01-introduction-fig09.png)
IVR, conferencing, voicemail.

</div>
<div>

**Media gateway**
![Media gateway](/images/01-introduction-fig10.png)
Translate between networks and codecs.

</div>
<div>

**Contact center**
![Contact center platform](/images/01-introduction-fig11.png)
Queues, agents, reporting, dialers.

</div>
</div>

---

# Finding information and help

<div grid="~ cols-2 gap-8 mt-4">
<div>

- **Official docs** — `docs.asterisk.org`
- **Project home** — `www.asterisk.org`
- **Community wiki** — `www.voip-info.org`
- Mailing lists & forums — active and fast-moving

</div>
<div>

- This book's **VoIP School Blackbelt** training
- The reproducible **Docker lab** in this repo
- `flavio@voip.school`

</div>
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**One phone, one line — your first PBX**

Boot the Asterisk 22 Docker lab and register a softphone.

See **Lab 0 & Lab 1** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Runs on Windows, macOS, or Linux — no hardware required.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk is **open-source PBX software** that runs on Linux, stewarded by **Sangoma** (ex-Digium).
- Its architecture bridges **channels** through **applications**, translating **codecs**, signaled by **protocols**.
- **SIP via `chan_pjsip`** is the modern path — `chan_sip` is gone in Asterisk 22.
- It scales from a single office PBX to carrier and contact-center deployments.
- Help lives at **`docs.asterisk.org`**, the community, and this book's lab.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Downloading and Installing Asterisk</strong> — and your first build.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 1 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which SIP channel driver does Asterisk 22 use, and what happened to chan_sip?</em>
</div>
