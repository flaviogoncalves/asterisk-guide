---
theme: seriph
title: 'SIP Trunking'
info: |
  ## Asterisk Guide — Chapter 7
  SIP Trunking, DID & the PSTN. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# SIP Trunking

Chapter 7

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

- **Connect** Asterisk 22 to an ITSP with PJSIP
- **Choose** between registration-based and IP-based (static) trunks
- **Route** inbound DIDs to the right extension, IVR, or queue
- **Route** outbound calls with correct caller-ID and E.164 formatting
- **Build** trunk failover and least-cost routing with `${DIALSTATUS}`
- **Handle** NAT for trunks on the transport and the endpoint

</v-clicks>

<!--
A PBX that can only call itself isn't useful. This chapter connects it to the rest of the world.
-->

---
layout: section
---

# What is a SIP trunk?

---

# What is a SIP trunk?

A logical voice path between your PBX and another SIP system — the modern replacement for a T1/E1 PRI or a bundle of analog FXO lines.

<div grid="~ cols-2 gap-8" class="mt-4">
<div>

**An ITSP**

- Commercial carrier selling origination + termination
- Usually hands you a block of **DIDs**
- Point Asterisk at the provider's signalling host
- No telephony hardware required

</div>
<div>

**A PSTN gateway**

- A device (or another Asterisk) with physical PSTN ports
- PRI card, analog FXO, or GSM/4G gateway
- Does the TDM-to-SIP conversion
- From Asterisk's view, just another SIP trunk

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
In PJSIP a trunk is <strong>just an endpoint</strong> — the same <code>endpoint</code> + <code>auth</code> + <code>aor</code> family as a phone, plus an <code>identify</code> or a <code>registration</code>.
</div>

---

# The big picture

![A SIP trunk between the Asterisk PBX and the ITSP](/images/09-sip-trunking-fig01.png){width=760px class="mx-auto"}

<div class="text-center text-sm opacity-70 mt-2">
The PBX registers as one account; outbound calls dial <code>PJSIP/&lt;num&gt;@trunk</code>, inbound calls land in <code>from-pstn</code>.
</div>

---

# A trunk is just an endpoint — with a twist

The same objects build a phone or a trunk. What changes is the **direction**:

<v-clicks>

- It authenticates **outbound** — *you* are the client, so credentials live in `outbound_auth`, not `auth`.
- It usually does **not** register *to you* — you register *to it*, or it sends traffic from a known IP.
- Inbound calls land in a dedicated context such as **`from-pstn`**, not `from-internal`.

</v-clicks>

<div class="mt-6 text-sm opacity-80">

**vs. the old TDM trunk:** a PRI gave a fixed channel count (23 on a T1, 30 on an E1) signalled over a D-channel. A SIP trunk has no fixed count — capacity is bandwidth, provider policy, and concurrent-call limits. Caller-ID, DID, and call progress now ride SIP headers and SDP.

</div>

---
layout: section
---

# Registration vs. IP-based trunks

---

# Registration-based trunks

The provider expects **you** to log in to **them**. Asterisk periodically sends a SIP `REGISTER` with a username and password — exactly like a phone registering to your PBX. Common with dynamic IPs, NAT, or credential-based providers.

<div class="mt-2">

The outbound login lives in a dedicated `registration` object — it replaces the old `register =>` line from the removed `chan_sip`:

</div>

```ini
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth      ; not auth — we authenticate OUTBOUND
aors=itsp-aor
from_user=4830001000         ; provider identifies you by this
from_domain=itsp.example.com
```

---

# Registration-based trunks — the auth, aor & registration

```ini
[itsp-auth]
type=auth
auth_type=digest             ; not userpass — deprecated in Asterisk 22
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth      ; shared with the endpoint
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000      ; modern equivalent of the old /9999 suffix
retry_interval=60            ; retry every 60s on failure
```

<div class="mt-2 text-sm opacity-80">
<code>userpass</code> and <code>md5</code> are <strong>deprecated and silently converted to <code>digest</code></strong> in Asterisk 22 — prefer <code>digest</code> in new config.
</div>

---

# Confirming the registration

After a reload, check `pjsip show registrations`:

```text
*CLI> pjsip show registrations

 <Registration/ServerURI.........>  <Auth.......>  <Status.......>
=====================================================================

 itsp-reg/sip:itsp.example.com:5060  itsp-auth      Registered  (exp. 3554s)

Objects found: 1
```

<div grid="~ cols-2 gap-8 mt-2 text-sm">
<div>

- `Status` reads **`Registered`** with the seconds until the next refresh.
- `(exp. Ns)` counts down to that refresh.

</div>
<div>

- `Rejected` / `Unregistered` = login refused.
- Turn on `pjsip set logger on` and read the `401`/`403` — usually a wrong username, password, or `client_uri` domain.

</div>
</div>

---

# IP-based (static) trunks

No registration at all. The provider knows your public IP and sends calls straight to it; you send calls to its known signalling IP. Authentication is by **source IP address**.

<div class="mt-2">

The key object is `identify` — *"any SIP request from this IP belongs to that endpoint."* Drop the `registration`, add `identify`:

</div>

```ini
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-aor]
type=aor
contact=sip:203.0.113.10:5060

[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10           ; IP, CIDR, or hostname (resolved at load time)
```

---

# Matching multiple gateways & verifying

<div grid="~ cols-2 gap-6">
<div>

Carriers with several media gateways — repeat `match` or give a CIDR:

```ini
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Hostnames are **resolved once, at config-load time** — reload if the provider's IP changes.

</div>
<div>

Verify with `pjsip show identifies`:

```text
*CLI> pjsip show identifies

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

</div>
</div>

---

# The security implication

An IP-based trunk with no auth is a door — `identify`/`match` is the only lock.

<div grid="~ cols-2 gap-8 mt-2">
<div>

**Two defences, used together**

- **Match as narrowly as possible** — specific host IPs over wide CIDRs.
- **Pair it with an ACL** — drop traffic at the SIP layer before it reaches an endpoint.

</div>
<div>

```ini
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

Reference from `[global]` (`acl=itsp-acl`) or per-transport.

</div>
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Deny everything, then permit only what you trust. <strong>Never let a trunk context dial back out to the PSTN</strong> without a deliberate, authenticated rule — that is the classic toll-fraud hole.
</div>

---

# Which model should I use?

<div class="mt-6 text-lg">

<v-clicks>

- Provider gives you a **username and password** → use a **registration** trunk.
- Provider asks for your **IP address** and gives you theirs → use an **identify** trunk.
- Many real trunks **combine both** — a registration so the provider can find you, plus an identify so inbound INVITEs from its media gateways are matched even when they arrive from a different IP.

</v-clicks>

</div>

---
layout: section
---

# Inbound routing & DID handling

---

# Inbound DIDs land in `from-pstn`

A **DID** (Direct Inward Dialing number) is the dialled number the provider hands you in the request URI — matched as `${EXTEN}` in your trunk's `context`.

<div class="text-sm mt-1 opacity-80">
How much you see varies: full E.164 (<code>+4830001000</code>), national number, or just the last few digits. Inspect a real call with <code>pjsip set logger on</code> before writing patterns.
</div>

<div grid="~ cols-2 gap-6 mt-2">
<div>

**One DID → one extension**

```ini
[from-pstn]
exten => 4830001000,1,NoOp(DID ${EXTEN})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

**One DID → an IVR**

```ini
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

</div>
<div>

**One DID → a queue**

```ini
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

</div>
</div>

---

# Many DIDs at once

A block of numbers? A pattern keeps the dialplan small. Range `4830003000`–`4830003099`, mapping each DID's last two digits to extension `60xx`:

```ini
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

<div class="mt-2 text-sm opacity-80">
<code>${EXTEN:-2}</code> takes the last two digits (negative offset counts from the right), so <code>4830003007</code> rings <code>PJSIP/6007</code>.
</div>

<div class="mt-4 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
<strong>Catch the unmatched DID.</strong> Add an <code>i</code> (invalid) extension so a mis-routed number plays an announcement instead of dropping silently:

```ini
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()
```
</div>

---
layout: section
---

# Outbound routing, caller-ID & E.164

---

# Sending the call to the trunk

Channel syntax is `PJSIP/<number>@<endpoint>` — the part before `@` is the user portion of the request URI; the part after `@` names the endpoint whose `aor` `contact` supplies the host.

A classic "dial 9 for an outside line":

```ini
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

<div class="mt-2 text-sm opacity-80">
<code>${EXTEN:1}</code> strips the leading <code>9</code> access code. The pattern <code>_9NXXXXXXXXX</code> matches <code>9</code> + a 10-digit number whose first digit is 2–9.
</div>

---

# Caller-ID on outbound calls

Most ITSPs ignore — or reject — a caller-ID that isn't a number you own. Set it before `Dial()`:

```ini
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

<div class="mt-2 text-sm opacity-80">
If the provider still overrides the <em>name</em>, that's their policy — many source the displayed name from their own CNAM database keyed on the number.
</div>

<div class="mt-4">

**Two endpoint options interact with this:**

- **`from_user`** — sets the user part of the `From` header at the SIP level; some providers identify your account by it regardless of `CALLERID(num)`.
- **`trust_id_outbound`** (default `no`) — whether Asterisk sends `P-Asserted-Identity` / `P-Preferred-Identity`. Leave off unless the provider documents PAI; then set `trust_id_outbound=yes` and `send_pai=yes`.

</div>

---

# Normalizing to E.164

E.164 = leading `+`, country code, national number, no punctuation (`+5548999990000`). Normalize **once** in the outbound context rather than scattering formatting everywhere:

```ini
[from-internal]
; 10-digit local: 4155550100 -> +14155550100
exten => _NXXNXXXXXX,1,Set(E164=+1${EXTEN})
 same =>            n,Goto(send-pstn,${E164},1)

; 11-digit with national prefix: 14155550100 -> +14155550100
exten => _1NXXNXXXXXX,1,Set(E164=+${EXTEN})
 same =>             n,Goto(send-pstn,${E164},1)

; already E.164: the user dialled + first
exten => _+X.,1,Goto(send-pstn,${EXTEN},1)

[send-pstn]
exten => _+X.,1,Set(CALLERID(num)=+14155550000)
 same =>     n,Dial(PJSIP/${EXTEN}@itsp,60,tT)
 same =>     n,Hangup()
```

<div class="mt-1 text-sm opacity-80">
Provider rejects the <code>+</code>? Strip it with <code>${EXTEN:1}</code> in the <code>Dial</code>. All format knowledge lives in one place.
</div>

---
layout: section
---

# Failover & least-cost routing

---

# Failover with `${DIALSTATUS}`

`Dial()` sets `${DIALSTATUS}` on return. Re-route only when the **trunk itself** failed:

```ini
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

<div class="mt-3 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
Fail over on <strong><code>CHANUNAVAIL</code></strong> (trunk unreachable) and <strong><code>CONGESTION</code></strong> (rejected / all circuits busy). <strong>Not</strong> on <code>BUSY</code>/<code>NOANSWER</code> — those mean the <em>called party</em> was reached and declined; retrying re-rings a phone that already said no.
</div>

---

# A reusable routing subroutine

Factor the failover into a `GoSub` so the trunk order lives in exactly one place:

```ini
[from-internal]
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Set(CALLERID(num)=4830001000)
 same =>   n,Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try2:end)
 same =>   n(try2),Dial(PJSIP/${NUM}@itsp_backup,60,tT)
 same =>   n(try2-chk),GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?try3:end)
 same =>   n(try3),Dial(PJSIP/${NUM}@itsp_thirdparty,60,tT)
 same =>   n(end),Return()
```

<div class="mt-2 text-sm opacity-80">
Now every outbound pattern is one <code>GoSub</code> call.
</div>

---

# Least-cost routing by destination

True LCR picks the trunk by **where the call is going** — international to a wholesale carrier, local/national to your primary:

```ini
[from-internal]
; international (011 + ...) -> wholesale, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))   ; everything else
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

<div class="mt-2 text-sm opacity-80">
For many prefixes, store the route table in a database (<code>func_odbc</code>/<code>AstDB</code>) and look the trunk up by prefix — the dialplan stays small and rates edit without reloading logic.
</div>

---
layout: section
---

# NAT and trunks

---

# NAT is two-sided

The single most common cause of trunk problems — **one-way audio**, or a trunk that registers but never receives inbound calls. Behind NAT, Asterisk advertises a private RFC 1918 address the provider cannot route back to.

<div grid="~ cols-2 gap-8 mt-4">
<div>

### On the transport
Your **public** address — set once, applies to all traffic:

```ini
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

</div>
<div>

- **`external_signaling_address`** — public IP written into SIP `Via`/`Contact`.
- **`external_media_address`** — public IP written into the SDP `c=` line so RTP returns correctly.
- **`local_net`** — networks treated as internal (not rewritten). List every internal subnet.

</div>
</div>

---

# On the endpoint — the provider's media

For a provider behind NAT, or one that sends media from an address other than its SDP claims:

```ini
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes
outbound_auth=itsp-auth
aors=itsp-aor
```

<div grid="~ cols-2 gap-6 mt-2 text-sm">
<div>

- **`direct_media=no`** — keep media through Asterisk (required to record/transcode/monitor).
- **`rtp_symmetric=yes`** — classic *comedia*: send RTP back where media actually came from.

</div>
<div>

- **`force_rport=yes`** — reply to the source IP/port of the request (RFC 3581).
- **`rewrite_contact=yes`** — rewrite inbound `Contact`/`Record-Route` to the real source.

</div>
</div>

<div class="mt-2 text-sm opacity-80">
<strong>Phones vs trunks:</strong> <code>rewrite_contact</code> is almost always right for phones (private contacts). On a static IP trunk the provider's contact is usually already public — test against your carrier before flipping it on. Confirm any endpoint with <code>pjsip show endpoint &lt;name&gt;</code>.
</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Connect a real SIP trunk**

Register your lab PBX to a real ITSP and place calls across the trunk.

`sip.flagonc.com` · port **`5600`** · accounts **`1010`–`1050`** / `supersecret`

`from_user` stamping lets the provider recognize your outbound calls · dial **`*98`** for the free echo test.

See **Lab 5** in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Pick any one account in 1010–1050 — they share the password. Note the provider port is <strong>5600</strong>, not 5060.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- A SIP trunk connects your PBX to the outside world; in PJSIP it is **just an endpoint** — `endpoint` + `auth` + `aor`, plus an `identify` or a `registration`.
- Use a **registration trunk** (`type=registration`, `outbound_auth`) when the provider gives you a **username/password**; use an **IP-based trunk** (`type=identify`, `match`) when auth is by **source IP** — and lock it down with a narrow `match` + an `acl`.
- Inbound, the DID arrives as **`${EXTEN}`** in `from-pstn`; route it to an extension, IVR, or queue — patterns and `${EXTEN:-N}` keep DID blocks compact.
- Outbound, set `CALLERID(num)` to a number you own, normalize to **E.164** in one place, and dial `PJSIP/<number>@trunk`.
- Build resilience by branching on `${DIALSTATUS}` (`CHANUNAVAIL`/`CONGESTION` re-route; `BUSY`/`NOANSWER` don't), and put LCR in a `GoSub` table.
- NAT is two-sided: `external_*_address`/`local_net` on the **transport**; `direct_media=no`, `rtp_symmetric`, `force_rport`, `rewrite_contact` on the **endpoint**.

</v-clicks>

<div class="mt-4 text-sm opacity-70">
Next: <strong>Legacy Channels</strong> — DAHDI, analog & digital PSTN interfaces.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 7 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>When should you use a <code>type=registration</code> trunk rather than a <code>type=identify</code> trunk — and which credentials object authenticates an outbound REGISTER?</em>
</div>
