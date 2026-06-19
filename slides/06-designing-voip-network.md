---
theme: seriph
title: 'Designing a VoIP Network'
info: |
  ## Asterisk Guide — Chapter 4
  Designing a VoIP Network. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Designing a VoIP Network

Chapter 4

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

- **Understand** the benefits of VoIP
- **Describe** how Asterisk handles VoIP as channels
- **Compare** the SIP and IAX2 channels and choose the right protocol
- **Choose** the most adequate codec for a given data channel
- **Dimension** the required number of channels
- **Calculate** the required bandwidth

</v-clicks>

<!--
This chapter is design and dimensioning — the math you do before you touch pjsip.conf.
-->

---
layout: section
---

# Why VoIP?

---

# VoIP benefits

Convergence is changing how we communicate — voice is just the beginning of voice, video, and presence.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**Convergence**
One network for data and voice cuts cost. Weigh it against ever-cheaper per-minute rates.

**Infrastructure costs**
A single infrastructure lowers the cost of adds, moves, and changes.

</div>
<div>

**Open standards**
Freedom to mix vendors — the customer is king, not a subordinate to the TELCO.

**Computer Telephony Integration**
Built on computer standards from the ground up: IVRs, ACDs, CTI, dialers, screen pops — fast and cheap.

</div>
</div>

---
layout: section
---

# Asterisk's VoIP architecture

---
layout: image-right
image: /images/06-voip-network-fig01.png
backgroundSize: contain
---

# Everything is a channel

Asterisk treats every VoIP protocol as a **channel** and bridges any channel to any other.

<v-clicks>

- Translate signaling — **SIP ↔ IAX2** — transparently
- Transcode codecs on the fly when endpoints differ
- e.g. a LAN SIP phone on **G.711** → a SIP trunk on **G.729**
- **SIP via `chan_pjsip`** is the standard; H.323 (`chan_ooh323` add-on) is rare

</v-clicks>

---

# VoIP protocols & the network stack

SIP is an **application-layer** protocol — RFC 3261 defines it against the TCP/IP (IETF) model, not OSI.

<div class="text-sm mt-2">

| TCP/IP (IETF) layer | Protocols | Rough OSI equivalent |
|---|---|---|
| **Application** | SIP, H.323, MGCP, IAX2 signaling; RTP/RTCP; codecs (G.711, G.729, Opus…) | App / Presentation / Session |
| **Transport** | UDP, TCP | Transport |
| **Internet** | IP (QoS such as DiffServ) | Network |
| **Link** | Ethernet, PPP, Frame Relay… | Data link / Physical |

</div>

<div grid="~ cols-3 gap-4 text-sm mt-4">
<div>

**SIP**
UDP/TCP **5060** (TLS **5061**); audio via RTP over a UDP range (`rtp.conf` ships 10000–20000).

</div>
<div>

**H.323**
H.225 signaling over TCP **1720**; RAS over UDP **1719**; RTP for audio.

</div>
<div>

**IAX2**
Signaling **and** media on a single UDP port **4569** — simple NAT/firewall traversal.

</div>
</div>

---
layout: section
---

# Choosing a protocol

---

# How to choose a protocol

<div grid="~ cols-2 gap-8 text-sm mt-2">
<div>

### SIP — Session Initiation Protocol
- IETF open standard, RFC 3261
- The most popular VoIP standard; used by most providers
- Lighter than H.323
- **Weakness:** NAT traversal; not built for billing

### IAX2 — Inter-Asterisk eXchange
- Open protocol from Digium (now Sangoma), RFC 5456 (Informational)
- Binary; one UDP port (**4569**) for signaling + media
- **Strengths:** low bandwidth (no RTP), easy NAT traversal
- Still ships (`chan_iax2`); legacy — great for Asterisk↔Asterisk trunks

</div>
<div>

### MGCP — Media Gateway Control Protocol
- Centralized control at the call agent; scalable
- Asterisk implementation incomplete; rarely used

### H.323
- One of the oldest VoIP protocols; ITU standard
- Still the standard in the gateway market (migrating to SIP)
- **Strengths:** maturity, market adoption
- **Weaknesses:** complex, standards-body costs

</div>
</div>

---

# Protocol comparison

<div class="text-sm mt-2">

| Protocol | Standard body | Used for |
|----------|---------------|----------|
| **SIP** | IETF standard | SIP phones; connecting to SIP service providers |
| **IAX2** | RFC 5456 (Informational) | Asterisk-to-Asterisk trunks; IAX2 phones; IAX providers |
| **H.323** | ITU standard | H.323 phones and gateways (can use an external gatekeeper, cannot be one) |
| **MGCP** | IETF/ITU | MGCP phones (no provider/gateway support) |
| **SCCP** | Cisco proprietary | Cisco phones |

</div>

<div class="mt-6 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
In Asterisk 22 the legacy <strong>peer / user / friend</strong> distinction is gone. PJSIP's
<strong>endpoint</strong> object handles both inbound and outbound calls — see the SIP and PJSIP chapter.
</div>

---
layout: section
---

# Choosing a codec

---
layout: image-right
image: /images/06-voip-network-fig04.png
backgroundSize: contain
---

# Codecs & translation

A codec converts the analog voice wave to a digital signal — PCM samples 4 kHz audio 8000×/s into 64 kbps.

<v-clicks>

- Codecs differ in **quality, compression, bandwidth, CPU**
- Asterisk can **transcode** between codecs — but it's CPU-heavy, so avoid it
- Some codecs (e.g. **G.723.1**) are **pass-through only** — no transcoding
- Translation goes via internal `slinear`

</v-clicks>

---

# Codecs in Asterisk 22

<div grid="~ cols-2 gap-8 text-sm">
<div>

- **G.711 (ulaw/alaw)** — 64 kbps; PSTN baseline (ulaw NA, alaw EU/LatAm)
- **G.722** — 64 kbps; wideband HD voice
- **G.726** — 16/24/32/40 kbps
- **G.723.1** — 5.3/6.3 kbps (pass-through)
- **GSM** — 13 kbps
- **iLBC** — 13.3 kbps

</div>
<div>

- **Speex** — 2.15–44.2 kbps
- **LPC10** — 2.4 kbps
- **G.729** — 8 kbps · external `codec_g729`, **per-channel license required** (`bcg729` is an open alternative)
- **Opus** — 6–510 kbps, variable · external `codec_opus`, no license noted; recommended for WebRTC & modern SIP

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<code>codec_g729</code> and <code>codec_opus</code> are <strong>external binary modules</strong> downloaded from
Digium/Sangoma (<code>support_level=external</code>) — not part of the standard build.
</div>

---

# How to choose a codec

<div grid="~ cols-2 gap-8 mt-2">
<div>

**Selection depends on**

- Sound quality
- Licensing costs
- CPU consumption
- Bandwidth requirements
- Packet-loss concealment
- Availability on Asterisk & phones

</div>
<div class="text-sm">

| Codec | G.711 | G.729A | iLBC | GSM 06.10 |
|---|---|---|---|---|
| Sample interval | 20 ms | 30 ms | 30 ms | RTE/LTP |
| Bandwidth (kbps) | 64 | 8 | 13.33 | 13 |
| Cost / channel | Free | ~USD 10 | Free | Free |
| Frame-erasure resist. | None | 3% | 5% | 3% |
| Complexity (MIPS) | ~0.35 | ~13 | ~18 | ~5 |

</div>
</div>

<div class="mt-3 text-sm opacity-80">
<strong>Recommendations:</strong> <strong>G.711</strong> for PSTN/interop · <strong>G.722</strong> for LAN HD voice ·
<strong>G.729</strong> for low-bandwidth WAN (licensed) · <strong>Opus</strong> for modern/WebRTC endpoints.
</div>

---
layout: section
---

# Bandwidth & header overhead

---
layout: image-right
image: /images/06-voip-network-fig05.png
backgroundSize: contain
---

# Overhead from protocol headers

The codec is small — the **headers dominate**. A 20-byte G.729 payload is wrapped in 58 bytes of Ethernet/IP/UDP/RTP.

<div class="text-sm mt-2">

**G.711 (64 kbps payload)**
- Ethernet → **95.2 kbps**
- PPP → **82.4 kbps**
- Frame Relay → **82.8 kbps**

**G.729 (8 kbps payload)**
- Ethernet → **31.2 kbps**
- PPP → **26.4 kbps**
- Frame Relay → **26.8 kbps**

</div>

<div class="mt-3 text-xs opacity-70">
PPP/FR headers are shorter than Ethernet, so they cost less per call.
</div>

---
layout: section
---

# Traffic engineering

---
layout: image-right
image: /images/06-voip-network-fig06.png
backgroundSize: contain
---

# Simplifications — Example #1

Estimate simultaneous calls by **user type** when you have no traffic data.

<div class="text-sm mt-2">

- **Business PBX:** 1 call per **5** extensions
- **Residential:** 1 call per **16** users

**Topology:** HQ (120 ext) + Branch #1 (30) + Branch #2 (15), Frame Relay between sites, T1 to the PSTN.

</div>

<div class="text-sm mt-3">

**T1 lines** — 120+30+15 = 165 ext ÷ 5 = **33 trunks ≈ 2×T1**
**Bandwidth (G.729, Frame Relay)**
- Branch #1: 26.8 × 6 = **160.8 kbps**
- Branch #2: 26.8 × 3 = **80.4 kbps**

</div>

---
layout: image-right
image: /images/06-voip-network-fig07.png
backgroundSize: contain
---

# Erlang B — when you have data

An **Erlang** measures one hour of traffic: 20 calls × 5 min = 100 min ÷ 60 = **1.66 Erlangs**.

<div class="text-sm mt-2">

Erlang B assumes random (Poisson) arrivals; blocked calls cleared. Needs **Busy Hour Traffic** (BHT ≈ 17% of daily call minutes) and a **Grade of Service** (e.g. GoS = 0.01 → 1% lost).

**From the call logger (GoS = 0.01):**
- HQ → Branch #1: 300 min/60 = **5 Erlangs → 11 lines**
- HQ → Branch #2: 170 min/60 = **2.83 Erlangs → 8 lines**

**Bandwidth (G.729, Frame Relay):**
- Branch #1: 26.8 × 11 = **294.8 kbps**
- Branch #2: 26.8 × 8 = **214.4 kbps**

</div>

---
layout: section
---

# Reducing VoIP bandwidth

---

# Three ways to save bandwidth

<div grid="~ cols-3 gap-4 text-sm">
<div>

**RTP header compression**
![RTP header compression](/images/06-voip-network-fig08.png)
RFC 2508 on Frame Relay/PPP. Drops a call from 26.8 → **11.2 kbps** — a **58.2%** cut. Check router feature support.

</div>
<div>

**IAX2 trunk mode**
![IAX2 trunk mode](/images/06-voip-network-fig08.png)
Asterisk↔Asterisk only. First call full headers (31.2 kbps); each extra call shares them, ~**9.6 kbps** each.
`31.2 + (n−1)×9.6`

</div>
<div>

**Increase voice payload**
![Increasing the voice payload](/images/06-voip-network-fig09.png)
Pack more frames per packet — trade latency for bandwidth. 60-byte G.729 → ~**16.05 kbps**.

</div>
</div>

---

# IAX2 trunk vs. payload — the numbers

<div grid="~ cols-2 gap-8 mt-2">
<div>

**IAX2 trunk mode (G.729)**

```text
Branch #1 (11 calls):
  31.2 + (11-1)*9.6 = 127.2 kbps
Branch #2 (8 calls):
  31.2 + (8-1)*9.6  = 98.4 kbps
```

First call 31.2 kbps; each additional call only 9.6 kbps.

</div>
<div>

**Increasing the payload**

Append the frame size to the codec in `allow`:

```ini
allow=ulaw
use_ptime=yes
```

Bigger packets amortize the 58-byte header stack over more voice — at the cost of latency.

</div>
</div>

---
layout: center
class: text-center
---

# 🧪 Practice

**Run the dimensioning math on your own network**

This chapter has no dedicated lab — instead, take a real topology
and size its trunks, lines, and bandwidth using the methods here.

See the general labs in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Try an online bandwidth calculator (voip.school/bandcalc) and an Erlang B calculator (erlang.com).
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Asterisk treats every VoIP protocol as a **channel** and bridges any channel to any other, **transcoding** when needed.
- It supports **SIP via `chan_pjsip`** (the only SIP driver in 22) and **IAX2**; H.323 is add-on only; MGCP/SCCP are gone.
- **SIP** wins on vendor support; **IAX2** wins on bandwidth and NAT traversal.
- Choose codecs by quality, license, CPU, and bandwidth — **G.711, G.722, G.729 (licensed), Opus**.
- **Header overhead dominates** — dimension with simplifications or **Erlang B**, then save bandwidth via RTP compression, IAX2 trunks, or bigger payloads.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>SIP and PJSIP</strong> — configuring endpoints in pjsip.conf.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 4 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which UDP port carries both IAX2 signaling and media — and why does that ease NAT traversal?</em>
</div>
