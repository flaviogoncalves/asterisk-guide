---
theme: seriph
title: 'SIP and PJSIP'
info: |
  ## Asterisk Guide — Chapter 5
  SIP and PJSIP in depth. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# SIP and PJSIP

Chapter 5

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

- **Explain** how the SIP protocol works — UACs, proxies, registrar, RTP
- **Trace** the register, proxy, and redirect operations
- **Read** SIP methods, responses, and an SDP body
- **Reason** about NAT traversal for both clients and the server
- **Map** the PJSIP object model: endpoint, AOR, auth, transport, identify
- **Write** a real `pjsip.conf` for a softphone and a SIP trunk
- **Verify** your work with `pjsip show …` console commands

</v-clicks>

<!--
SIP is the protocol; PJSIP is how Asterisk 22 speaks it. chan_pjsip is the ONLY SIP
channel driver in Asterisk 22 LTS — chan_sip and sip.conf are gone (Legacy Channels chapter).
-->

---
layout: section
---

# SIP protocol fundamentals

---

# What is SIP?

Session Initiation Protocol — a **text-based** signaling protocol (like HTTP and SMTP) that initializes, maintains, and terminates interactive sessions: voice, video, chat, games.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**The components**

- **UAC** — user agent client; *starts* signaling
- **UAS** — user agent server; *responds* to a UAC
- **UA** — the SIP terminal (phone or gateway; both UAC + UAS)
- **Proxy / Redirect / Location** server — usually one box: the **SIP proxy**

</div>
<div>

**Key facts**

- Defined by the **IETF**; the de-facto standard for voice
- The SIP proxy maintains the location DB, sets up and tears down sessions
- On Asterisk 22, SIP config lives in **`pjsip.conf`** — second only to `extensions.conf` in edits

</div>
</div>

---
layout: image-right
image: /images/07-sip-and-pjsip-fig01.png
backgroundSize: contain
---

# The SIP architecture

User agents, the registrar/proxy/redirect server, and a gateway to the PSTN.

<v-clicks>

- **Signaling** sets up the call through the proxy
- **Media (RTP)** flows **directly** between the endpoints
- The proxy keeps and maintains the **location database**
- An extension can be a number (`8500`) **or** a URI (`flavio@voip.school`)

</v-clicks>

---
layout: image-right
image: /images/07-sip-and-pjsip-fig02.png
backgroundSize: contain
---

# SIP register process

Before a phone can **receive** calls it must register with the location database.

- The phone sends **REGISTER**, binding its name to its IP
- e.g. extension **8500 → 200.180.1.1**
- The registrar stores the contact and replies **200 OK**
- The bound name need not be a number — a URI works too

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Asterisk is the <strong>registrar</strong> and <strong>location server</strong> for its endpoints.
</div>

---
layout: image-right
image: /images/07-sip-and-pjsip-fig03.png
backgroundSize: contain
---

# Proxy operation

As a **proxy**, the SIP server stays in the middle of the signaling.

- Sits in the **INVITE / 200 OK** path
- Looks the callee up in the **location server**
- Capable of advanced **routing and billing**
- The **RTP media still flows directly** between the endpoints

---
layout: image-right
image: /images/07-sip-and-pjsip-fig04.png
backgroundSize: contain
---

# Redirect operation

As a **redirect** server, it answers and then steps aside.

- Replies to INVITE with **302 Moved Temporarily** carrying the contact
- Caller re-sends **INVITE / ACK directly** to the new location
- Very light on resources — but **no control** over the call
- Sometimes used in **load-balancing** designs

---
layout: two-cols-header
---

# How Asterisk handles SIP

Asterisk is **neither** a SIP proxy **nor** a redirector — it is a **back-to-back user agent (B2BUA)**.

::left::

<div class="pr-4">

It connects two UACs **to itself**, bridging two SIP channels together.

A **re-invite** mechanism lets the two channels talk directly, controlled per endpoint by **`direct_media`**.

</div>

::right::

```ini
[6000]
type=endpoint
direct_media=yes   ; RTP peer-to-peer, frees the server
; direct_media=no  ; anchor RTP through Asterisk
```

::bottom::

<div class="mt-3 text-sm opacity-80">
Use <code>direct_media=no</code> when you must <strong>record</strong>, <strong>transcode</strong>, or <strong>transfer</strong> the call.
</div>

---

# Direct media: yes vs. no

<div grid="~ cols-2 gap-6">
<div>

**`direct_media=yes`** — signaling through Asterisk, RTP peer-to-peer

![SIP operation with direct_media=yes](/images/07-sip-and-pjsip-fig05.png)

Frees server resources.

</div>
<div>

**`direct_media=no`** — both signaling **and** RTP anchored through Asterisk

![SIP operation with direct_media=no](/images/07-sip-and-pjsip-fig06.png)

Required to record, transcode, or transfer.

</div>
</div>

---

# SIP messages

The basic SIP methods:

<div grid="~ cols-2 gap-8 text-sm">
<div>

- **INVITE** — connection establishment
- **ACK** — acknowledge
- **BYE** — connection termination
- **CANCEL** — terminate a non-established call
- **REGISTER** — register a UAC to a proxy
- **OPTIONS** — check availability

</div>
<div>

- **REFER** — transfer a call to someone else
- **SUBSCRIBE** — subscribe to events
- **NOTIFY** — send channel information
- **INFO** — various messages (e.g. DTMF)
- **MESSAGE** — instant messages

</div>
</div>

<div class="mt-3 text-sm">

**Responses** (HTTP-style): **1XX** info (100 trying · 180 ringing · 183 progress) · **2XX** success (200 OK) · **3XX** redirect (302 · 305) · **4XX** client error (403) · **5XX** server error (500 · 501) · **6XX** global failure (606)

</div>

---

# An INVITE on the wire

```text
INVITE sip:2000@192.168.1.133 SIP/2.0
Via: SIP/2.0/UDP 192.168.1.116;rport;branch=z9hG4bKc0a80174...
From: "unknown"<sip:2001@192.168.1.133>;tag=1556140623845
To: <sip:2000@192.168.1.133>
Contact: <sip:2001@192.168.1.116>
Call-ID: 64B4C8EC-FCFC-49E9-98B1-90982EEEBED3@192.168.1.116
CSeq: 2 INVITE
Max-Forwards: 70
User-Agent: SJphone/1.61.312b (SJ Labs)
Content-Length: 335
Content-Type: application/sdp
Proxy-Authorization: Digest username="2001",realm="asterisk",
  nonce="6c55905e",uri="sip:2000@192.168.1.133",response="983c0099...",algorithm=MD5
```

<div class="mt-2 text-sm opacity-70">
Note the <code>Contact</code> header carries the phone's own (often RFC1918) IP — the seed of every NAT problem.
</div>

---

# Session Description Protocol (SDP)

Carried in the INVITE body — describes the media session. Defined in **RFC 4566** (obsoletes RFC 2327).

<div grid="~ cols-2 gap-6">
<div>

**Describes**

- Transport protocol (RTP/UDP/IP)
- Media type (audio, video, text)
- Codec / media format
- Addresses and ports to receive media

</div>
<div>

```text
v=0
o=- 3369741883 3369741883 IN IP4 192.168.1.116
s=SJphone
c=IN IP4 192.168.1.116
t=0 0
m=audio 49160 RTP/AVP 3 97 98 8 0 101
a=rtpmap:3 GSM/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-11,16
```

</div>
</div>

---
layout: section
---

# NAT traversal

---

# The four kinds of NAT

NAT maps internal IP:port pairs to external ones for a limited lifetime. Four behaviours exist:

<div class="text-sm mt-2">

| NAT type | Must send data first | Can determine external IP:port for return | Restricts incoming to dest IP:port |
| --- | :---: | :---: | :---: |
| **Full Cone** | No | Yes | No |
| **Restricted Cone** | Yes | Yes | Only IP |
| **Port Restricted Cone** | Yes | Yes | Yes |
| **Symmetric** | Yes | **No** | Yes |

</div>

<div class="mt-4 text-sm opacity-80">
STUN works with the first three; <strong>symmetric NAT breaks STUN</strong> — and most home DSL/cable routers are symmetric.
</div>

---

# Full Cone vs. Symmetric

<div grid="~ cols-2 gap-6">
<div>

**Full Cone** — static external↔internal mapping; **any** external host can reach it.

![Full Cone NAT](/images/07-sip-and-pjsip-fig11.png)

</div>
<div>

**Symmetric** — a **different** mapping per destination; a discovered address can't be reused.

![Symmetric NAT](/images/07-sip-and-pjsip-fig12.png)

</div>
</div>

<div class="mt-2 text-sm opacity-70">
This is why symmetric NAT defeats STUN-based traversal.
</div>

---

# Two problems: signaling and RTP

Most one-way-audio faults are NAT-related. The conceptual fixes are always the same — and PJSIP names each one:

<div class="text-sm mt-2">

| Problem | Conceptual fix | PJSIP setting |
| --- | --- | --- |
| `Contact`/`Via` carries a private IP | Reply to where the packet **actually** came from (RFC 3581 `rport`) | `force_rport=yes` · `rewrite_contact=yes` |
| Media sent to a private IP | Send RTP back to where it **arrived** from (symmetric RTP / *comedia*) | `rtp_symmetric=yes` |
| NAT mapping times out — phone can't be called | Keep the pinhole open with a periodic OPTIONS (*qualify*) | `qualify_frequency=` (on the **AOR**) |

</div>

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
If the client is behind <strong>symmetric</strong> NAT, force RTP through Asterisk with <code>direct_media=no</code>.
</div>

---

# Asterisk server behind NAT

Common in cloud deployments — Asterisk must advertise its **public** address in SIP/SDP headers.

<div grid="~ cols-2 gap-6">
<div>

**Three steps**

- Forward the **SIP port** (UDP 5060) to the server
- Forward the **RTP range** (UDP 10000–20000, in `rtp.conf`)
- Tell Asterisk its external address and local network

On the **transport**: `external_media_address`, `external_signaling_address`, `local_net=`.

</div>
<div>

```ini
; rtp.conf
[general]
rtpstart=10000
rtpend=20000
```

```ini
[tnat]
type=transport
protocol=udp
bind=0.0.0.0
local_net=172.16.30.0/24
local_net=127.0.0.1/32
external_media_address=54.232.1.20
external_signaling_address=54.232.1.20
```

</div>
</div>

---
layout: section
---

# PJSIP: the SIP channel

---

# Why PJSIP

PJSIP arrived in Asterisk 12, became the default, and in **Asterisk 22 LTS is the only SIP channel driver**. Built on Teluu's mature **pjproject** stack.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**Features**

- **Multiple registrations** — two phones on one Address of Record
- **Friendly, modular API** — many small cooperating modules
- **Multiple transports** — many addresses, ports, and protocols at once

</div>
<div>

**The modules**

- `res_pjsip` — base layer, core services
- `res_pjsip_session` — media sessions, SDP
- `res_pjsip_messaging` — SIP messages/headers
- `res_pjsip_registrar` — registrations
- `res_pjsip_pubsub` — SUBSCRIBE/NOTIFY/PUBLISH (presence, BLF)

</div>
</div>

<div class="mt-3 text-sm opacity-70">
PJSIP config is more verbose — each device is several related objects, not one peer block. That structure is what buys the flexibility.
</div>

---
layout: image-right
image: /images/07-sip-and-pjsip-fig14.png
backgroundSize: contain
---

# The PJSIP object model

The **endpoint** is the glue linking every section together.

<div class="text-sm">

- **endpoint** → a transport, an AOR, an auth, a dialplan **context**
- **AOR** holds the **contacts** (and mailboxes, qualify)
- **auth** — inbound / outbound credentials
- **transport** — IP, port, protocol (UDP/TCP/TLS/WSS), NAT addresses
- **registration** — an **outbound** registration to a trunk
- **identify** — match inbound requests by **IP** instead of `From`
- **acl** / **domain_alias** — stand alone

</div>

---

# Relationships between entities

```text
ENDPOINT  ── transport   zero-to-many → at least one
ENDPOINT  ── auth        zero-to-many → zero-or-one
ENDPOINT  ── aor         many-to-many
ENDPOINT  ── identify    zero-to-many → one
AOR       ── contact     many-to-many

REGISTRATION ── transport  zero-to-many → at least one
REGISTRATION ── auth       zero-to-many → zero-or-one

ACL, DOMAIN_ALIAS  ── no relationship configuration
```

<div class="mt-3 text-sm opacity-80">
This web of objects looks complex at first — but it is exactly what makes PJSIP flexible. The configuration <strong>wizard</strong> keeps day-to-day provisioning short.
</div>

---

# Configuring a softphone

Each device is described by four related objects — note they **share the same section name** but differ by `type`. On the client, register the **SipPulse Softphone** (<https://www.sippulse.com/produtos/softphone>) against this endpoint.

<div grid="~ cols-2 gap-6">
<div>

```ini
[transport-udp-main]
type=transport
protocol=udp
bind=0.0.0.0:5060

[softphone]
type=endpoint
transport=transport-udp-main
context=from-internal
disallow=all
allow=ulaw
aors=softphone
auth=softphone
```

</div>
<div>

```ini
[softphone]
type=auth
auth_type=digest
username=softphone
password=#supersecret#

[softphone]
type=aor
max_contacts=2
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
UDP transport on 5060 · an endpoint into <code>from-internal</code> · username/password auth · an AOR allowing two contacts.
</div>

---

# Configuring a SIP trunk

A trunk adds a **registration** and an **identify** — Asterisk registers outbound and matches the provider by host.

<div grid="~ cols-2 gap-6 text-sm">
<div>

```ini
[siptrunk]
type=endpoint
transport=transport-udp-main
context=from-siptrunk
direct_media=no
disallow=all
allow=ulaw
outbound_auth=siptrunk
aors=siptrunk

[siptrunk]
type=aor
contact=sip:sip.flagonc.com:5600
```

</div>
<div>

```ini
[siptrunk]
type=auth
auth_type=digest
username=1020
password=supersecret

[siptrunk]
type=registration
outbound_auth=siptrunk
server_uri=sip:1020@sip.flagonc.com:5600
client_uri=sip:1020@sip.flagonc.com
contact_user=9999

[siptrunk]
type=identify
endpoint=siptrunk
match=sip.flagonc.com
```

</div>
</div>

---

# Dialing PJSIP & the wizard

<div grid="~ cols-2 gap-6">
<div>

**Channel naming** — the `PJSIP/` technology

```ini
exten => 6000,1,Dial(PJSIP/6000,20,tT)

; dial every contact on an AOR at once
exten => 6000,1,Dial(${PJSIP_DIAL_CONTACTS(6000)},20,tT)

; out a trunk to an explicit address
exten => _9011.,1,Dial(PJSIP/siptrunk/sip:${EXTEN:1}@sip.flagonc.com)
```

</div>
<div>

**The wizard** — `pjsip_wizard.conf`, templates for fast provisioning

```ini
[phone_default](!)
type = wizard
accepts_auth = yes
accepts_registrations = yes
transport = tnat
endpoint/allow = ulaw
endpoint/context = from-internal
endpoint/direct_media = no
aor/qualify_frequency = 15

[alice](phone_default)
inbound_auth/username = alice
inbound_auth/password = supersecret
```

</div>
</div>

<div class="mt-2 text-sm opacity-70">
Transport and global sections still live in <code>pjsip.conf</code>. Great for phones; trunks are usually few enough to write out directly.
</div>

---

# Console commands

After editing `pjsip.conf`, reload **just PJSIP**:

```bash
asterisk -rx 'module reload res_pjsip.so'
```

<div class="text-sm mt-2">

There is **no bare `pjsip reload`** — only `pjsip reload qualify aor|endpoint`. A plain `reload` reloads every module. List the rest with `help pjsip`.

</div>

<div grid="~ cols-2 gap-8 text-sm mt-2">
<div>

**Inspect configuration**

- `pjsip show endpoints` — all endpoints + availability
- `pjsip show endpoint <name>` — every parameter
- `pjsip show aors` — AORs and their contacts
- `pjsip show registrations` — our outbound registrations

</div>
<div>

**Compact & troubleshoot**

- `pjsip list endpoints` / `pjsip list contacts`
- `pjsip set logger on` — log every SIP packet
- `pjsip set logger host <ip>` — scope to one host
- `pjsip set history on` → `pjsip show history`

</div>
</div>

---
layout: image-right
image: /images/07-sip-and-pjsip-fig15.png
backgroundSize: contain
---

# `pjsip show endpoints`

```text
 Endpoint:  <Endpoint/CID.....................>  <State.....>  <Channels.>
    I/OAuth:  <AuthId/UserName...........................................>
        Aor:  <Aor............................................>  <MaxContact>
      Contact:  <Aor/ContactUri..................> <Hash....> <Status> <RTT(ms)..>
    Transport:  <TransportId........>  <Type>  <cos>  <tos>  <BindAddress....>
===========================================================================

 Endpoint:  softphone                            Not in use    0 of inf
     InAuth:  softphone/softphone
        Aor:  softphone                                          2
      Contact:  softphone/sip:softphone@192.168.1.116:... e8e29c5f10 Avail  21.482
```

<div class="text-sm mt-2 opacity-80">
The <code>softphone</code> contact is registered — <strong>Avail</strong>.
</div>

---

# Inspecting one endpoint

<div grid="~ cols-2 gap-4">
<div>

**`pjsip show endpoint softphone`** — the full parameter list for a single endpoint.

![pjsip show endpoint softphone](/images/07-sip-and-pjsip-fig16.png)

</div>
<div>

**`pjsip show registrations`** — our **outbound** registrations and their status.

![pjsip show registrations](/images/07-sip-and-pjsip-fig17.png)

<div class="text-sm mt-1 opacity-80">
The trunk reads <strong>Registered</strong>.
</div>

</div>
</div>

---

# The friendlier `pjsip list`

`pjsip list` shows less data, but better structured — one line per object.

<div grid="~ cols-2 gap-6">
<div>

**`pjsip list endpoints`**

![pjsip list endpoints](/images/07-sip-and-pjsip-fig18.png)

</div>
<div>

**`pjsip list contacts`**

![pjsip list contacts](/images/07-sip-and-pjsip-fig19.png)

</div>
</div>

---

# SIP history — capture & replay

```bash
asterisk -rx 'pjsip set history on'
```

<div grid="~ cols-3 gap-3 text-sm mt-1">
<div>

**Enable**

![pjsip set history on](/images/07-sip-and-pjsip-fig20.png)

</div>
<div>

**`pjsip show history`**

![pjsip show history](/images/07-sip-and-pjsip-fig21.png)

REGISTER · 401 · REGISTER · 200 OK

</div>
<div>

**`… history entry`**

![pjsip show history entry](/images/07-sip-and-pjsip-fig22.png)

A full captured message.

</div>
</div>

<div class="mt-2 text-sm opacity-70">
Clear with <code>pjsip set history clear</code>. Migrating a legacy <code>chan_sip</code> system? See the <em>Legacy Channels</em> chapter.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Register a softphone and inspect your endpoint**

Boot the Asterisk 22 Docker lab, register `6001`/`6002`, then confirm the endpoint
is **Avail** with `pjsip show endpoint`.

See **Lab 1 — Your first calls** in `labs/LAB-GUIDE.md`

```bash
docker compose -f lab/docker-compose.yml exec asterisk \
  asterisk -rx 'pjsip show endpoints'
```

<div class="mt-2 text-sm opacity-70">
Call <code>6001 ↔ 6002</code>, then dial <strong>600</strong> for the echo test to prove two-way RTP.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- **SIP** is the text-based signaling protocol; **RTP** carries the media — often directly between phones.
- A SIP server can act as **registrar, proxy, or redirect** — but Asterisk is a **B2BUA** that bridges two channels.
- **`direct_media`** decides whether RTP is peer-to-peer or anchored through Asterisk (record / transcode / transfer).
- **NAT** breaks SIP in two places — fix with `force_rport`, `rtp_symmetric`, and `qualify_frequency`; symmetric NAT forces `direct_media=no`.
- **PJSIP** is the only SIP driver in Asterisk 22: an **endpoint** ties together **transport, auth, AOR**, plus **registration** and **identify** for trunks.
- Verify everything with **`pjsip show endpoints / endpoint / registrations`** and trace SIP with the **logger and history**.

</v-clicks>

<div class="mt-4 text-sm opacity-70">
Next: <strong>WebRTC</strong> — bringing SIP into the browser.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 5 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>On a phone behind symmetric NAT, which pair of settings makes Asterisk reply to the request's source address (RFC 3581) and send media back to where the RTP actually arrives from?</em>
</div>
