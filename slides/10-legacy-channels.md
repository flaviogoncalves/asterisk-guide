---
theme: seriph
title: 'Legacy Channels'
info: |
  ## Asterisk Guide — Chapter 8
  Legacy Channels: analog/TDM (DAHDI), IAX2, and the removed chan_sip. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Legacy Channels

Chapter 8

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

- **Distinguish** what is *removed* from what is *still present but legacy* in Asterisk 22
- **Recognize** analog (FXO/FXS) and digital (E1/T1/PRI/BRI) telephony and their signaling
- **Configure** TDM hardware with DAHDI and `chan_dahdi.conf`
- **Use** IAX2 (`chan_iax2`) to interconnect Asterisk servers, including trunk mode
- **Explain** the history of `chan_sip` — removed in Asterisk 21 — and where these channels fit today

</v-clicks>

<!--
This is the one chapter where chan_sip, sip.conf, DAHDI and IAX2 appear. Always frame historically.
-->

---

# What "legacy" means in Asterisk 22

The channel types in this chapter are increasingly rare in a pure-VoIP world — but their status differs.

<div grid="~ cols-2 gap-8" class="mt-2 text-sm">
<div>

### Still present, but legacy

- **`chan_dahdi`** — analog (FXO/FXS) & digital (E1/T1/ISDN PRI/BRI) TDM hardware. Fully supported.
- **`chan_iax2`** — Inter-Asterisk eXchange v2. Still ships and is supported; little new deployment.
- **`chan_unistim`** — Nortel/Avaya phones. Rarely used.

</div>
<div>

### Removed — gone in 22

- **`chan_sip` / `sip.conf`** — the old SIP driver. Deprecated for years, **removed in Asterisk 21**.
- **H.323 / MGCP / SCCP** — not part of a standard Asterisk 22 build.

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
If you run a pure-PJSIP shop with no telephony cards, no IAX2 trunks and no <code>sip.conf</code> to convert, you can safely skip this chapter.
</div>

---
layout: section
---

# Analog channels — FXO / FXS

---

# FX interfaces: who feeds the dial tone?

DAHDI (originally Digium's drivers; Sangoma acquired Digium in **2018**) provides analog connectivity.

<div grid="~ cols-2 gap-8" class="text-sm mt-2">
<div>

- **FXO** — *Office* side. Connects to a PSTN central office **or** a legacy PBX extension. It **receives** dial tone.
- **FXS** — *Station* side. Feeds an analog phone, fax or modem. It **provides** dial tone and ringing power.

**Trunk signaling:** loop-start, ground-start, **kewlstart** (the near-default — adds hang-up detection on top of loop-start).

</div>
<div>

![Asterisk between an analog phone (FXS) and the telco line (FXO).](/images/10-legacy-fig01.png)

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Signaling is inverted:</strong> FXS interfaces are configured with FXO signaling and vice-versa — Asterisk talks as if it were on the opposite side.
</div>

---

# Signaling categories

<div grid="~ cols-3 gap-4 text-sm mt-2">
<div>

**Supervision**

- On-hook / off-hook
- Ringing

Tones vary by country — customize in `indications.conf`.

</div>
<div>

**Address**

- DTMF (high+low tone per digit)
- Pulse (rotary)
- MFC/R2 (multi-frequency)

</div>
<div>

**Information**

- Dial tone / busy
- Ringback
- Congestion
- Invalid number
- Confirmation

</div>
</div>

```ini
; indications.conf — a country tone set (Brazil)
[br]
description=Brazil
dial=425
busy=425/250,0/250
ring=425/1000,0/4000
```

---

# OPX and channel banks

<div grid="~ cols-2 gap-6 text-sm">
<div>

**Off-premises extension (OPX)**

An FXO port fronts a legacy PBX extension; a remote Asterisk delivers that line to an analog phone over IP through an FXS port.

![Asterisk as a VoIP gateway delivering an OPX over IP.](/images/10-legacy-fig02.png)

</div>
<div>

**USB channel banks**

Instead of consuming PCI slots, a USB channel bank (e.g. **Xorcom Astribank**) exposes dozens of FXS/FXO ports.

![A 19-inch rack-mount Xorcom Astribank USB channel bank.](/images/10-legacy-fig03.png)

</div>
</div>

---

# Configuring an analog card with DAHDI

Example: a Sangoma (ex-Digium) **TDM400** with one FXS and one FXO module.

<div grid="~ cols-2 gap-6 text-sm">
<div>

1. Install the FXS / FXO modules
2. `dahdi_genconf` → generates `/etc/dahdi/system.conf` + `dahdi-channels.conf`
3. Load drivers: `modprobe dahdi`, `modprobe wctdm`
4. `dahdi_test` — check interrupt misses (>99.987%)
5. `dahdi_cfg -vv` — apply config to the driver
6. Configure `chan_dahdi.conf`, then load Asterisk

</div>
<div>

![A Sangoma/Digium TDM404P analog card with FXS/FXO modules.](/images/10-legacy-fig04.png)

</div>
</div>

```text
*CLI> ; dahdi_cfg output
Channel 01: FXS Kewlstart (Default) (Slaves: 01)
Channel 02: FXO Kewlstart (Default) (Slaves: 02)
2 channels configured.
```

---

# chan_dahdi.conf — defining the channels

The hardware is set in `/etc/dahdi/system.conf`; `chan_dahdi.conf` defines the **Asterisk** channels.

```ini
; FXS interface — signaled with FXO
signalling=fxo_ks
group=2
context=extensions
channel => 2

; FXO interface — signaled with FXS
signalling=fxs_ks
group=1
context=incoming
channel => 1
```

<div class="mt-2 text-sm opacity-80">
Include the generated channels: <code>#include dahdi-channels.conf</code>. SIP/PJSIP channels live in <code>pjsip.conf</code> — <strong>chan_sip and sip.conf were removed in Asterisk 21</strong>.
</div>

---

# chan_dahdi.conf — key option groups

<div grid="~ cols-2 gap-6 text-sm">
<div>

**General** — `context`, `channel`, `group`, `language`, `musiconhold`

**Caller ID** — `usecallerid`, `hidecallerid`, `callerid`, `callwaitingcallerid`

**Audio quality** — echo & gain

```ini
echocancel=yes
echocancelwhenbridged=yes
txgain=-10%
rxgain=10%
```

</div>
<div>

**Billing** — `accountcode`, `amaflags`

**Call progress** — busy/answer detection

```ini
busydetect=yes
busycount=4
busypattern=500,500
answeronpolarityswitch=yes
```

**Phone options** — `callwaiting`, `immediate` (hotlines), `threewaycalling`, `mailbox`, `callgroup`, `pickupgroup`

</div>
</div>

<div class="mt-2 text-sm opacity-70">
Echo canceller default is <strong>MG2</strong>; alternatives are <strong>HPEC</strong> (Sangoma) and <strong>OSLEC</strong> (open source). The <code>fxotune</code> utility tunes FXO impedance.
</div>

---
layout: section
---

# Digital channels — E1 / T1 / PRI / TDM

---

# Why digital? Density and signaling

<div grid="~ cols-2 gap-6 text-sm">
<div>

When you need **more than ~8 channels**, the telco delivers a digital trunk (TDM).

- **T1** — 24 channels, 1544 kbps (US/Japan)
- **E1** — 30 channels, 2048 kbps (Europe/LatAm)
- Voice is digitized with **PCM**: sampled 8000×/s → 64 kbps DS0 (µ-law US/Japan, a-law elsewhere)

</div>
<div>

![TDM in E1 and T1: E1 carries 32 timeslots, T1 carries 24.](/images/10-legacy-fig08.png)

</div>
</div>

<div class="mt-2 text-sm opacity-70">
Provisioned over UTP copper, fiber (optical MUX), or microwave; some E1 lines arrive on dual BNC coax and need a <strong>balun</strong> to a card's RJ45.
</div>

---

# CAS vs CCS — signaling families

<div grid="~ cols-2 gap-8 text-sm">
<div>

### ISDN (CCS — Common Channel)

- Out-of-band signaling on a **D-channel** (Q.931)
- **PRI:** 23B+D (T1) / 30B+D (E1)
- **BRI:** 2B+D — popular in Europe
- The preferred choice when available

`switchtype`: `euroisdn`, `national`, `dms100`, `4ess`, `5ess`, `qsig`

</div>
<div>

### MFC/R2 (CAS — Channel Associated)

- ABCD bits in **timeslot 16** + in-band tones
- Common in **Latin America, China, Africa**
- Many country variants — must match exactly
- Provided by **libopenr2** (built into `chan_dahdi` when present at compile time — no patch in Asterisk 22)

</div>
</div>

---

# The DAHDI software architecture

<div grid="~ cols-2 gap-6">
<div class="text-sm">

`chan_dahdi` loads the protocol libraries it needs and sits on top of the kernel drivers:

- **libpri** — ISDN
- **libopenr2** — MFC/R2
- **libss7** — SS7

These talk to `/dev/dahdi`, the DAHDI kernel driver, and the card-specific driver.

</div>
<div>

![The DAHDI software architecture stack.](/images/10-legacy-fig09.png)

</div>
</div>

---

# Configuring a PRI span

`/etc/dahdi/system.conf` sets the spans and channels; `chan_dahdi.conf` defines the Asterisk channels.

<div grid="~ cols-2 gap-6">
<div>

```ini
; system.conf — 2× E1 PRI
span=1,1,0,ccs,hdb3,crc4
span=2,0,0,ccs,hdb3,crc4
bchan=1-15,17-31
dchan=16
bchan=33-47,49-63
dchan=48
defaultzone=br
loadzone=br
```

</div>
<div>

```ini
; chan_dahdi.conf — 2× E1 PRI
switchtype=euroisdn
signalling=pri_cpe
group=1
channel => 1-15,17-31
group=2
channel => 32-46,48-62
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
<code>pri_cpe</code> = client/user side (most common); <code>pri_net</code> = network side. BRI uses <code>bri_cpe</code> / <code>bri_net</code> / <code>bri_cpe_ptmp</code>.
</div>

---

# Verifying & troubleshooting TDM

```text
*CLI> dahdi show status      ; physical layer / alarms
Description                          Alarms   IRQ  bpviol  CRC4
Sangoma Wildcard E100P E1 Card 0     OK       0    0       0

*CLI> dahdi show channels    ; are channels recognized?
*CLI> pri show spans         ; ISDN layer 3 (Q.931) up?
*CLI> pri show span 1
```

<div class="mt-2 text-sm">

| Alarm | Meaning |
|-------|---------|
| **Red** | Cannot sync with the remote switch — usually line code / framing mismatch |
| **Yellow** | Remote switch is in red alarm — it is not receiving your transmissions |
| **Blue** | Unframed all-1s on every timeslot |

</div>

<div class="mt-1 text-sm opacity-70">Use <code>pri debug span 1</code> to trace Q.931 SETUP / CONNECT / DISCONNECT messages.</div>

---

# MFC/R2 in practice

<div grid="~ cols-2 gap-6 text-sm">
<div>

Line signaling (ABCD bits in TS16) plus in-band inter-register tones carry the call through Idle → Seized → Answer → Clearback.

```ini
; chan_dahdi.conf — MFC/R2 (Brazil)
signalling=mfcr2
mfcr2_variant=br
mfcr2_max_ani=20
mfcr2_max_dnis=4
mfcr2_category=national_subscriber
group=1
context=from-mfcr2
channel => 1-15,17-31
```

</div>
<div>

![A complete MFC/R2 call flow between Asterisk and the telco.](/images/10-legacy-fig11.png)

</div>
</div>

<div class="mt-1 text-sm opacity-70">
<strong>ANI</strong> = caller number; <strong>DNIS</strong> = dialed number. Tune <code>mfcr2_mfback_timeout</code> first if calls fail to complete.
</div>

---
layout: section
---

# The IAX2 protocol

---

# IAX2 — one protocol, one port

<div grid="~ cols-2 gap-6 text-sm">
<div>

`chan_iax2` unifies **signaling and media** in a single UDP stream — no separate RTP.

- One port (**UDP 4569**), a 15-bit call number multiplexes calls
- **Simple NAT traversal** — its main remaining advantage
- Primary use today: **Asterisk-to-Asterisk** interconnection

</div>
<div>

![IAX multiplexes many calls over a single UDP port using a 15-bit call number.](/images/10-legacy-fig12.png)

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Still supported in Asterisk 22, but legacy.</strong> For new Asterisk-to-Asterisk trunks where NAT is not a concern, a <strong>PJSIP</strong> trunk is the recommended modern approach.
</div>

---

# IAX2 trunk mode saves bandwidth

<div grid="~ cols-2 gap-6 text-sm">
<div>

Trunk mode shares **one IP/UDP header** across many mini-frames — up to ~80% overhead savings on multiple concurrent calls.

- Two SIP/RTP calls: 2 packets, 156 B overhead for 40 B payload
- IAX2 trunk: 1 packet, 66 B overhead for the same 40 B payload

A **DAHDI timing source** is required to enable trunking.

</div>
<div>

![Comparing IAX2 trunk overhead with SIP/RTP overhead.](/images/10-legacy-fig13.png)

</div>
</div>

---

# Connecting two Asterisk servers over IAX2

No registration needed — both IPs are known. Define peers/users in `iax.conf`.

<div grid="~ cols-2 gap-6">
<div>

```ini
; iax.conf — HQ server
[general]
bindaddr=0.0.0.0
bindport=4569
disallow=all
allow=ulaw

[Branch]
type=peer
host=192.168.2.9
username=Branch
secret=password
trunk=yes
```

</div>
<div>

![Two Asterisk servers (HQ 20xx, Branch 22xx) joined by a single IAX trunk.](/images/10-legacy-fig15.png)

</div>
</div>

```ini
; extensions.conf — route 22xx over the trunk
exten => _22XX,1,Dial(IAX2/Branch/${EXTEN})
```

---

# IAX2 authentication & encryption

<div grid="~ cols-2 gap-8 text-sm">
<div>

**Auth methods** — plaintext, **MD5**, or **RSA** key pairs.

RSA (SHA-1 digest) is strongest: generate with `astkeygen -n`, keep the **private** key secret, share the **public** key with the peer.

```ini
[hq]
type=user
auth=rsa
inkeys=hq
host=192.168.2.10
trunk=yes
```

</div>
<div>

**Encryption** — 128-bit AES on the trunk:

```ini
encryption=yes
forceencryption=yes
```

**IP restrictions** — rules evaluated in sequence, last match wins:

```ini
deny=192.168.0.0/255.255.255.0
permit=0.0.0.0/0.0.0.0
```

</div>
</div>

<div class="mt-1 text-sm opacity-70">
Debug with <code>iax2 show registry</code>, <code>iax2 show peers</code>, <code>iax2 show netstats</code>, <code>iax2 debug</code>.
</div>

---

# Channel naming & dial strings

<div grid="~ cols-2 gap-8 text-sm">
<div>

**DAHDI**

```text
DAHDI/<id>[c][r<cadence>]
DAHDI/2          ; channel 2
DAHDI/g1         ; first free in group 1
```

</div>
<div>

**IAX2**

```text
IAX2/[user[:secret]@]peer[/exten[@context]]
IAX2/iaxphone
IAX2/8590:secret@myserver/8590@default
```

</div>
</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
For SIP, the dial string is <code>PJSIP/...</code> (e.g. <code>Dial(PJSIP/2000)</code>). The removed <code>chan_sip</code> used <code>SIP/...</code> — do not use it on Asterisk 22.
</div>

---
layout: section
---

# Legacy SIP — chan_sip (removed in Asterisk 21)

---

# chan_sip is gone — kept here only as history

<div class="text-sm">

`chan_sip` and its `/etc/asterisk/sip.conf` were deprecated for several releases and **removed in Asterisk 21** — they **do not exist in Asterisk 22**. None of the examples below will run on a current system; the modern, supported driver is `chan_pjsip`.

</div>

```ini
; LEGACY sip.conf — a registering extension (does NOT run on Asterisk 22)
[2000]
type=friend
host=dynamic
context=default
dtmfmode=rfc2833
disallow=all
allow=ulaw
secret=senha
```

<div class="mt-2 text-sm opacity-80">
A single <code>sip.conf</code> <code>[peer]</code>/<code>[friend]</code> is split into several PJSIP objects, each with a <code>type=</code>: <strong>endpoint</strong>, <strong>aor</strong>, <strong>auth</strong>, plus a shared <strong>transport</strong>.
</div>

---

# Migrating to PJSIP — the mapping

<div class="text-sm">

| Legacy sip.conf | PJSIP equivalent (pjsip.conf) |
|-----------------|-------------------------------|
| `[peer]` / `[friend]` block | `type=endpoint` + `type=aor` + `type=auth` |
| `type=friend/peer/user` | a single `type=endpoint` |
| `host=dynamic` | `type=aor`, `max_contacts=1` (device REGISTERs) |
| `register=>user:secret@host/ext` | `type=registration` (`server_uri`, `client_uri`, `outbound_auth`) |
| `secret=` / `username=` | `type=auth`, `auth_type=userpass` |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` |
| `nat=force_rport,comedia` | `force_rport=yes`, `rewrite_contact=yes`, `rtp_symmetric=yes` |
| `qualify=yes` | `qualify_frequency=` on the **aor** |
| `insecure=invite` (provider) | omit auth + `type=identify` (`match=`) |

</div>

<div class="mt-1 text-sm opacity-70">Asterisk ships <code>sip_to_pjsip.py</code> (under <code>contrib/scripts/sip_to_pjsip/</code>) to bootstrap the conversion — treat its output as a starting point and test thoroughly.</div>

---

# The same extension, converted

```ini
; pjsip.conf on Asterisk 22 — the modern equivalent
[2000]
type=endpoint
context=default
disallow=all
allow=ulaw
dtmf_mode=rfc4733
direct_media=no
auth=2000
aors=2000

[2000]
type=auth
auth_type=userpass
username=2000
password=senha

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

<div class="mt-1 text-sm opacity-70">
Check it with <code>pjsip show endpoints</code> and <code>pjsip show registrations</code> (the legacy <code>sip show ...</code> commands are gone). Full PJSIP coverage is in the <em>SIP &amp; PJSIP</em> chapter and at <code>docs.asterisk.org</code>.
</div>

---
layout: center
class: text-center
---

# Where this fits today

**Most new deployments are pure VoIP** — SIP trunks and PJSIP endpoints over Ethernet, no telephony hardware.

<div class="mt-4 text-sm">

DAHDI/`chan_dahdi` stays for **analog and TDM hardware** (legacy, rural PSTN, regulated markets) ·
IAX2 stays for **single-port Asterisk-to-Asterisk** links · `chan_sip` is **removed** — migrate to PJSIP.

</div>

<div class="mt-6 text-sm opacity-70">
Legacy hardware is out of scope for the hands-on labs — there is no lab for this chapter.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- **Still present but legacy:** `chan_dahdi` (analog FXO/FXS + digital E1/T1/PRI/BRI) and `chan_iax2`.
- **Removed in Asterisk 21:** `chan_sip` / `sip.conf` — gone in 22. H.323/MGCP/SCCP are not in a standard build.
- **DAHDI** separates hardware (`/etc/dahdi/system.conf`) from Asterisk channels (`chan_dahdi.conf`); ISDN (CCS) is preferred, MFC/R2 (CAS) is common in LatAm/Asia.
- **IAX2** unifies signaling + media on one UDP port (4569) — easy NAT traversal and bandwidth-saving trunk mode — but PJSIP trunks are the modern choice.
- Any legacy `sip.conf` system must be **migrated to PJSIP** — one block becomes endpoint + aor + auth; `sip_to_pjsip.py` helps.

</v-clicks>

<div class="mt-6 text-sm opacity-70">
Next: <strong>Migrating from chan_sip to PJSIP</strong> — a full conversion walkthrough.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 8 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>Which utility auto-detects DAHDI cards and generates <code>system.conf</code> and <code>dahdi-channels.conf</code>? And what happened to <code>chan_sip</code> in Asterisk 21?</em>
</div>
