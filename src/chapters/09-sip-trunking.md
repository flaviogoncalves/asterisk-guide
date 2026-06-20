# SIP trunking, DID & the PSTN

A PBX that can only call itself is not very useful. Sooner or later every system
has to reach the rest of the world — the public switched telephone network
(PSTN), a SIP provider, or another PBX. The link that carries those calls is a
**trunk**. In the TDM era a trunk was a physical circuit: a T1/E1 PRI or a bundle
of analog FXO lines. Today it is almost always a **SIP trunk** — a logical
connection to an Internet Telephony Service Provider (ITSP) carried over the same
IP network as everything else.

This chapter shows how to connect Asterisk 22 to an ITSP with PJSIP, how to choose
between a registration-based and an IP-based trunk, how to route inbound DID
numbers to the right destination, how to send outbound calls with correct
caller-ID and E.164 formatting, and how to build failover and least-cost routing
across several trunks. We finish with NAT handling for trunks and a lab that
stands up a second Asterisk (and SIPp) as a mock ITSP so you can place real calls
across a trunk.

Everything here is verified against the book's Asterisk 22.10.0 lab; the trunk
object pattern is the same one introduced in *Building your first PBX with PJSIP*
and *SIP & PJSIP in depth*.

## Objectives

By the end of this chapter, you should be able to:

- Connect Asterisk 22 to an ITSP with PJSIP
- Choose between registration-based and IP-based (static) trunks
- Route inbound DIDs to the right extension, IVR or queue
- Route outbound calls with correct caller-ID and E.164 formatting
- Build trunk failover and least-cost routing with `${DIALSTATUS}`
- Handle NAT for trunks on the transport and the endpoint

## What is a SIP trunk

A SIP trunk is a logical voice path between your PBX and another SIP system. In
practice that "other system" is one of two things:

- **An ITSP (Internet Telephony Service Provider).** A commercial carrier that
  sells you call origination and termination and, usually, a block of phone
  numbers (DIDs). You point Asterisk at the provider's signalling host, and the
  provider connects your calls to the wider PSTN. This is how most modern systems
  reach the phone network — no telephony hardware required.
- **A PSTN gateway.** A device (or another Asterisk) that has physical PSTN
  interfaces — a PRI card, analog FXO ports, or a GSM/4G gateway — and presents
  them to your PBX as SIP. The gateway does the TDM-to-SIP conversion; from
  Asterisk's point of view it is just another SIP trunk.

Either way, in PJSIP a trunk is **just an endpoint**. The same object family you
used for a phone — `endpoint`, `auth`, `aor`, optionally `identify` and
`registration` — builds a trunk. The differences are in the details: a trunk
authenticates *outbound* (you are the client, so credentials go in
`outbound_auth`, not `auth`), it usually does not register a user agent to you
(you register to *it*, or it sends you traffic from a known IP), and it lands
inbound calls in a dedicated context such as `from-pstn` instead of
`from-internal`.

> **Compared with the old TDM trunk.** A PRI gave you a fixed number of B-channels
> (23 on a T1, 30 on an E1) and signalled call setup over a dedicated D-channel
> (see the *Legacy channels* chapter). A SIP trunk has no fixed channel count —
> capacity is whatever your bandwidth, your provider's policy, and any
> `max_contacts`/concurrent-call limits allow. Caller-ID, DID, and call progress
> that used to ride ISDN information elements now ride SIP headers and SDP.

There are two ways an ITSP will agree to exchange traffic with you, and they
determine how you build the trunk: **registration-based** and **IP-based
(static)**. We cover each in turn.

## Registration-based trunks

A registration-based trunk is the model used when the provider expects *you* to
log in to *them*. Your Asterisk periodically sends a SIP `REGISTER` to the
provider, authenticating with a username and password, exactly the way a phone
registers to your PBX. This is common when your public IP is dynamic, when you are
behind NAT, or when the provider simply identifies customers by SIP credentials
rather than by IP address.

In PJSIP the outbound login lives in a dedicated `registration` object. It
replaces the single `register =>` line that the removed `chan_sip` driver used in
`sip.conf`. Here is a complete registering trunk to a fictional provider,
following the verified pattern from the earlier chapters — note `outbound_auth`
(not `auth`), `server_uri`/`client_uri` (not `server`/`client`),
`from_user`/`from_domain` on the endpoint, and `dtmf_mode=rfc4733`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
outbound_auth=itsp-auth
aors=itsp-aor
from_user=4830001000
from_domain=itsp.example.com

[itsp-auth]
type=auth
auth_type=digest
username=4830001000
password=Lab-itsp-secret

[itsp-aor]
type=aor
contact=sip:itsp.example.com:5060

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:itsp.example.com:5060
client_uri=sip:4830001000@itsp.example.com:5060
contact_user=4830001000
retry_interval=60
```

A few things to notice:

- **`auth_type=digest`, not `userpass`.** Both produce the same digest
  authentication, but in Asterisk 22 `userpass` (and the old `md5`) are
  **deprecated and silently converted to `digest`**. Prefer `digest` in new
  configuration; you will still see `userpass` in older files and in the earlier
  chapters of this book.
- **`outbound_auth` on both the endpoint and the registration.** The registration
  uses it to authenticate the `REGISTER`; the endpoint uses it to answer the
  `407 Proxy Authentication Required` the provider sends back to an outbound
  `INVITE`. They can share one `auth` object.
- **`from_user` / `from_domain`.** Many providers reject calls whose `From`
  header does not carry your account number and their domain. These two options
  set exactly that.
- **`contact_user=4830001000`.** This becomes the user part of the `Contact` you
  register, so the provider knows which number to deliver inbound calls to. It is
  the modern equivalent of the `/9999` suffix on the old `register =>` line.
- **`retry_interval=60`.** If registration fails, retry every 60 seconds.

After a reload, confirm the registration with `pjsip show registrations`. In the
lab — where `itsp.example.com` does not actually answer — the table looks like
this:

```
*CLI> pjsip show registrations

 <Registration/ServerURI..............................>  <Auth....................>  <Status.......>
==========================================================================================

 itsp-reg/sip:itsp.example.com:5060                      itsp-auth                   Rejected          (exp. 56s)

Objects found: 1
```

The `(exp. Ns)` suffix counts down the seconds until the next attempt; once it
crosses zero it briefly reads `(exp. Ns ago)` before the retry fires. Against a
live provider the `Status` column reads `Registered` with the seconds remaining
until the next refresh. `Rejected` (or `Unregistered`) means the provider did not
accept the login — turn on `pjsip set logger on` and read the `401`/`403` reply,
almost always a wrong username, password, or `client_uri` domain.

## IP-based (static) trunks

The second model needs no registration at all. The provider knows your public IP
address and sends calls straight to it; you, in turn, send calls to the
provider's known signalling IP. Authentication is by **source IP address**, not
by SIP credentials. This is typical for trunks between two servers you control, or
for an enterprise trunk where both sides have static addresses.

The key object is `identify`. It tells Asterisk: "any SIP request arriving from
*this* IP belongs to *that* endpoint." Without it, PJSIP tries to match an inbound
request to an endpoint by the `From` user, which a carrier's traffic will not
satisfy — so the call would be rejected or fall to the `anonymous` endpoint.

A static trunk drops the `registration` object and adds `identify`:

```
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
match=203.0.113.10
```

`match` accepts an IP address, a CIDR range, or a hostname. **Hostnames are
resolved once, at configuration load time**, so if your provider's IP changes you
must reload. For a carrier that publishes several media gateways, list each
signalling IP — you can repeat `match` or give a CIDR:

```
[itsp-identify]
type=identify
endpoint=itsp
match=203.0.113.10
match=203.0.113.11
match=198.51.100.0/24
```

Verify what Asterisk will accept with `pjsip show identifies`. Captured from the
lab (the `sipp-identify` line is the lab's pre-existing SIPp endpoint):

```
*CLI> pjsip show identifies

 Identify:  <Identify/Endpoint...........................................................>
      Match:  <criteria...........................>
==========================================================================================

 Identify:  itsp-identify/itsp
      Match: 172.30.0.50/32

 Identify:  sipp-identify/sipp
      Match: 172.30.0.0/24

Objects found: 2
```

### The security implication

An IP-based trunk with no authentication is a door, and `identify`/`match` is the
only lock on it. If you `match` too broad a range — or if an attacker can spoof a
source IP — calls land in your `from-pstn` context unauthenticated. Two defences,
used together:

- **Match as narrowly as possible.** Prefer specific host IPs over wide CIDRs.
  Only the provider's real signalling IPs belong in `match`.
- **Pair it with an ACL.** PJSIP can drop traffic at the SIP layer before it ever
  reaches an endpoint, using a `type=acl` object (or `acl.conf`):

```
[itsp-acl]
type=acl
deny=0.0.0.0/0.0.0.0
permit=203.0.113.10
permit=203.0.113.11
```

A `type=acl` section needs no reference: `res_pjsip_acl` applies every such
object to *all* inbound SIP traffic before it reaches any endpoint. (The `acl`
and `contact_acl` options on the object pull named rule lists from `acl.conf`
instead of listing `permit`/`deny` inline as above.) The principle is the same
one from the SIP chapter: deny everything, then permit only what you trust. And
whatever your trunk context does,
**never let it reach a context that can dial back out to the PSTN** without a
deliberate, authenticated rule — that is the classic toll-fraud hole.

> **Which model should I use?** If the provider gives you a username and password,
> use a **registration** trunk. If they ask for your IP address and give you
> theirs, use an **identify** trunk. Some providers support both; many real
> trunks combine a registration (so the provider can find you) with an identify
> (so inbound INVITEs from the provider's media gateways are matched even when
> they arrive from an IP other than the registrar).

## Inbound routing and DID handling

Once inbound calls arrive, they land in the endpoint's `context` — here
`from-pstn`. A **DID** (Direct Inward Dialing number) is simply the dialled number
the provider hands you in the request URI. Your job in the dialplan is to map each
DID to a destination: a single extension, an IVR, a queue, or a ring group.

The number the provider sends is matched as `${EXTEN}` in `from-pstn`. How much of
it you see depends on the provider — some send the full E.164 number
(`+4830001000`), some send the national number, some send only the last few
digits. Inspect a real inbound call with `pjsip set logger on` and look at the
request URI before writing patterns.

### One DID to one extension

The simplest case — a single DID routed straight to a phone:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID: ${EXTEN} from ${CALLERID(num)})
 same =>             n,Dial(PJSIP/6001,30,tT)
 same =>             n,Hangup()
```

### One DID to an IVR (auto attendant)

A main number that should answer with a menu instead of ringing a phone:

```
[from-pstn]
exten => 4830001000,1,Answer()
 same =>             n,Wait(1)
 same =>             n,Goto(ivr-main,s,1)
```

`ivr-main` is the auto-attendant context you built in the dialplan chapters
(`Background()` + `WaitExten()`). Routing the DID is just a `Goto`.

### One DID to a queue

A support line that should land in a call queue:

```
[from-pstn]
exten => 4830002000,1,Answer()
 same =>             n,Queue(support,t,,,300)
 same =>             n,Hangup()
```

### Many DIDs at once

When you buy a block of numbers, a pattern keeps the dialplan small. Suppose your
DID range is `4830003000`–`4830003099` and the provider sends the full number; map
each DID's last two digits to extension `60xx`:

```
[from-pstn]
exten => _48300030XX,1,NoOp(DID ${EXTEN} -> extension 60${EXTEN:-2})
 same =>             n,Dial(PJSIP/60${EXTEN:-2},30,tT)
 same =>             n,Hangup()
```

`${EXTEN:-2}` takes the last two digits (negative offset counts from the right),
so `4830003007` rings `PJSIP/6007`. A `did => extension` lookup table built with
`GoSub` or an Asterisk database (`AstDB`/`func_odbc`) scales further still, but for
a handful of numbers explicit patterns are the clearest.

> **Catch the unmatched DID.** Add an `i` (invalid) extension to `from-pstn` so a
> mis-routed inbound number plays an announcement or rings the operator instead of
> dropping silently:
>
> ```
> exten => i,1,Playback(ss-noservice)
>  same =>  n,Hangup()
> ```

## Outbound routing, caller-ID and E.164

Outbound calls flow the other way: an internal phone dials a number, your dialplan
matches it, strips any access prefix, sets the caller-ID the provider expects, and
hands the call to the trunk endpoint with `Dial(PJSIP/<number>@itsp)`.

### Sending the call to the trunk

The channel syntax for a trunk is `PJSIP/<number>@<endpoint>`: the part before the
`@` becomes the user portion of the outbound request URI, and the part after the
`@` names the endpoint whose `aor` `contact` supplies the destination host. A
classic "dial 9 for an outside line" rule:

```
[from-internal]
exten => _9NXXXXXXXXX,1,NoOp(Outbound to ${EXTEN:1} via itsp)
 same =>             n,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp,60,tT)
 same =>             n,Hangup()
```

`${EXTEN:1}` strips the leading `9` access code before the number is sent. The
pattern `_9NXXXXXXXXX` matches `9` plus a 10-digit number whose first digit is
2–9; adjust it to your dial plan.

### Caller-ID on outbound calls

Most ITSPs ignore — or actively reject — a caller-ID that is not a number you own.
Set the outbound caller-ID number to one of your DIDs with the `CALLERID(num)`
function before `Dial()`, as shown above. You can also set the name:

```
 same => n,Set(CALLERID(num)=4830001000)
 same => n,Set(CALLERID(name)=ACME Corp)
```

If the provider still strips or overrides your caller-ID name, that is their
policy — many carriers source the displayed name from their own CNAM database
keyed on the number, not from your `From` header.

Two endpoint options interact with this:

- **`from_user`** sets the user part of the `From` header at the SIP level, which
  some providers use to identify your account regardless of `CALLERID(num)`.
- **`trust_id_outbound`** (default `no`) controls whether Asterisk will send
  privacy-sensitive identity headers (`P-Asserted-Identity`/`P-Preferred-Identity`)
  outbound. Leave it off unless your provider documents that they want PAI, in
  which case set `trust_id_outbound=yes` and `send_pai=yes`.

### Normalizing to E.164

E.164 is the international number format: a leading `+`, country code, then the
national number, with no spaces or punctuation (for example `+5548999990000` or
`+14155550100`). Carriers increasingly expect — or require — E.164 on the trunk.
Rather than scatter formatting across the dialplan, normalize once in the outbound
context.

A North-American example that accepts a 10-digit local number, an 11-digit
`1`-prefixed number, or an already-E.164 number, and always presents `+1…` to the
trunk:

```
[from-internal]
; 10-digit local: 4155550100  -> +14155550100
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

Some providers want the `+`; others want the bare digits. If yours rejects the
`+`, strip it on the way out with `${EXTEN:1}` in the `Dial`. The point is that
all the format knowledge lives in one place, so switching providers — or adding a
second one — is a one-line change.

## Failover and least-cost routing

With one trunk, a provider outage means no outbound calls. With two or more, you
can fail over automatically and even pick the cheapest route per destination —
*least-cost routing* (LCR).

### Failover with `${DIALSTATUS}`

`Dial()` sets the `${DIALSTATUS}` channel variable when it returns. The values you
care about for failover are `CHANUNAVAIL` (the trunk could not be reached at all)
and `CONGESTION` (the call was rejected, e.g. all circuits busy). Try the primary
trunk; if it could not carry the call, fall through to the backup:

```
[from-internal]
exten => _9NXXXXXXXXX,1,Set(CALLERID(num)=4830001000)
 same =>             n,Dial(PJSIP/${EXTEN:1}@itsp_primary,60,tT)
 same =>             n,NoOp(Primary returned ${DIALSTATUS})
 same =>             n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?backup:done)
 same =>             n(backup),Dial(PJSIP/${EXTEN:1}@itsp_backup,60,tT)
 same =>             n(done),Hangup()
```

Note the deliberate choice **not** to fail over on `BUSY` or `NOANSWER` — those
mean the *called party* was reached and declined, so retrying on another trunk
would re-ring a phone that already said no (and could cost you a second call).
Only re-route when the *trunk itself* failed.

### A reusable routing subroutine

Repeating that logic for every dial pattern is error-prone. Factor it into a
`GoSub` routine that takes the destination number and tries each trunk in order:

```
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

Now every outbound pattern is one `GoSub` call, and the trunk order is defined in
exactly one place.

### Least-cost routing by destination

True LCR chooses the trunk by where the call is going. A common shape is to match
the destination prefix and send each class of call to the provider that is
cheapest for it — for example, international calls to a wholesale carrier and
local/national calls to your primary:

```
[from-internal]
; international (011 + ...) -> wholesale trunk, then fall back to primary
exten => _9011.,1,GoSub(dialout-intl,s,1(${EXTEN:1}))
 same =>      n,Hangup()
; everything else -> domestic routing
exten => _9NXXXXXXXXX,1,GoSub(dialout,s,1(${EXTEN:1}))
 same =>             n,Hangup()

[dialout-intl]
exten => s,1,Set(NUM=${ARG1})
 same =>   n,Dial(PJSIP/${NUM}@itsp_wholesale,60,tT)
 same =>   n,GotoIf($["${DIALSTATUS}" = "CHANUNAVAIL" | "${DIALSTATUS}" = "CONGESTION"]?fb:end)
 same =>   n(fb),Dial(PJSIP/${NUM}@itsp_primary,60,tT)
 same =>   n(end),Return()
```

For more than a few prefixes, store the route table in a database
(`func_odbc`/`AstDB`) and look the trunk up by prefix instead of hard-coding
patterns. The dialplan stays small and the rates live in a table you can edit
without reloading logic.

## NAT and trunks

NAT is the single most common cause of trunk problems — typically one-way audio,
or a trunk that registers but never receives inbound calls. The cause is the same
as for phones (covered in *SIP & PJSIP in depth* and *Designing a VoIP network*):
Asterisk advertises its own idea of its address in SIP and SDP, and behind NAT
that is a private RFC 1918 address the provider cannot route back to.

For trunks the fix has two parts — settings on the **transport** (your public
address) and settings on the **endpoint** (how to treat the provider's media).

### On the transport — your public address

When the Asterisk server itself is behind NAT (a cloud or on-prem box with a
private IP and a 1:1 public IP), tell the transport its public address and which
networks are local. These options are set once, on the `transport`, and apply to
all traffic over it:

```
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060
local_net=172.30.0.0/24
local_net=10.0.0.0/8
external_media_address=203.0.113.50
external_signaling_address=203.0.113.50
```

- **`external_signaling_address`** — the public IP Asterisk writes into SIP
  headers (`Via`, `Contact`) for destinations outside `local_net`.
- **`external_media_address`** — the public IP Asterisk writes into the SDP `c=`
  line so RTP comes back to the right place. Usually identical to the signalling
  address.
- **`local_net`** — networks Asterisk treats as internal, so it does *not* rewrite
  addresses for LAN peers. List every internal subnet.

### On the endpoint — the provider's media

The other half handles a provider that itself sits behind NAT, or simply sends
media from an address other than the one in its SDP. Set these per trunk endpoint:

```
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
from_user=4830001000
from_domain=itsp.example.com
```

- **`direct_media=no`** — keep media flowing through Asterisk rather than letting
  the two legs talk directly. Essential across NAT, and required anyway if you
  want to record, transcode, or monitor the call.
- **`rtp_symmetric=yes`** — the classic *comedia* behaviour: send RTP back to the
  address the media actually came from, not the address the SDP claims.
- **`force_rport=yes`** — reply to SIP from the source IP/port of the request
  (RFC 3581), instead of trusting the `Via` header.
- **`rewrite_contact=yes`** — on inbound SIP messages from this endpoint, rewrite
  the `Contact` header (or an appropriate `Record-Route` header) to the source IP
  address and port the packet really came from. Per the option's own
  documentation, this "helps servers communicate with endpoints that are behind
  NATs" and "helps reuse reliable transport connections such as TCP and TLS."

> **Recommendation — phones vs trunks.** `rewrite_contact` is almost always the
> right choice for phones, because their advertised contact is typically a private
> RFC 1918 address that is not routable back to them. On a static IP-based trunk
> the provider's contact is usually already a correct public address, so rewriting
> it is often unnecessary; some operators prefer to leave it off there and enable
> it only for registration trunks and NAT'd phones. The documented effect of the
> option is purely the inbound `Contact`/`Record-Route` rewrite above — so the
> safe practice is to test against your specific carrier before flipping it on a
> static trunk.

You can confirm the effective settings on any endpoint with
`pjsip show endpoint <name>` — `direct_media`, `rtp_symmetric`, `force_rport`,
`rewrite_contact`, and the rest are all printed in the parameter dump.

## Lab — a mock ITSP with a second Asterisk and SIPp

You do not need a paid trunk to practise. The book's lab already runs an Asterisk
22.10.0 container and a SIPp container on a private `172.30.0.0/24` network; we
will treat the SIPp container as the "carrier" placing inbound calls, and add a
trunk endpoint that lands those calls in a `from-pstn` context.

![A SIP trunk between the Asterisk PBX and the ITSP: the PBX registers as one account, outbound calls dial `PJSIP/<num>@trunk`, and inbound calls land in the `from-pstn` context.](../images/09-sip-trunking-fig01.png)

### 1. Add the trunk endpoint

Add an IP-based trunk to `lab/asterisk/etc/pjsip.conf` that matches the lab's SIPp
host and lands inbound calls in `from-pstn`:

```
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
aors=itsp-aor

[itsp-aor]
type=aor
contact=sip:172.30.0.50:5060

[itsp-identify]
type=identify
endpoint=itsp
match=172.30.0.50
```

### 2. Route the inbound DID

In `lab/asterisk/etc/extensions.conf`, add a `from-pstn` context that answers the
DID the mock carrier will dial and plays it back, then add an outbound rule:

```
[from-pstn]
exten => 4830001000,1,NoOp(Inbound DID ${EXTEN} from ${CALLERID(num)})
 same =>             n,Answer()
 same =>             n,Playback(demo-congrats)
 same =>             n,Hangup()
exten => i,1,Playback(ss-noservice)
 same =>  n,Hangup()

[from-internal]
; outbound across the trunk
exten => _9X.,1,Set(CALLERID(num)=4830001000)
 same =>     n,Dial(PJSIP/${EXTEN:1}@itsp,30,tT)
 same =>     n,Hangup()
```

Reload both files (`core reload`) and verify the trunk loaded:

```
*CLI> pjsip show endpoint itsp
 Endpoint:  itsp                                                 Not in use    0 of inf
        Aor:  itsp-aor                                           0
      Contact:  itsp-aor/sip:172.30.0.50:5060              ...        NonQual         nan
   Identify:  itsp-identify/itsp
        Match: 172.30.0.50/32
```

### 3. Place an inbound call across the trunk

Point a SIPp scenario at the PBX with the DID as the target user. The lab already
ships `lab/sipp/uac_9000.xml`, which INVITEs extension `9000`; copy it to
`uac_did.xml` and change the request-URI/`To` user from `9000` to `4830001000`,
then run it from the SIPp container:

```
docker compose -f lab/docker-compose.yml exec -T sipp \
  sipp -sf /sipp/uac_did.xml 172.30.0.10:5060 -m 1 -nostdin
```

Watch the call hit `from-pstn` on the Asterisk console (`pjsip set logger on`
shows the inbound INVITE; `core show channels` shows the `PJSIP/itsp-…` channel
playing `demo-congrats`). Because the SIPp source IP matches the `identify`, the
call is accepted with no authentication — exactly how a static carrier trunk
behaves.

### 4. Inspect the trunk

Capture the trunk's full configuration for your notes:

```
pjsip show endpoint itsp
pjsip show aors
pjsip show identifies
```

### 5. (Stretch) make it a registration trunk

Stand up the *second* Asterisk container as a real registrar: give it an
`endpoint`+`auth`+`aor` for account `4830001000`, then on the PBX swap the
`identify` block for the `registration` block from the start of this chapter
(pointing `server_uri` at the second container's IP). Confirm with
`pjsip show registrations` that the status reads `Registered`, then place a call
in each direction.

## Summary

A SIP trunk connects your PBX to the outside world, and in PJSIP it is just an
endpoint built from the same `endpoint` + `auth` + `aor` family you already know,
plus an `identify` or a `registration`. Use a **registration trunk**
(`type=registration` with `outbound_auth`) when the provider gives you a username
and password; use an **IP-based trunk** (`type=identify` with `match`) when
authentication is by source IP — and lock the latter down with a narrow `match`
and an `acl`, because an unauthenticated trunk is a toll-fraud target. Inbound,
the provider's DID arrives as `${EXTEN}` in your `from-pstn` context, where you
route it to an extension, an IVR, or a queue — patterns and `${EXTEN:-N}` keep
DID blocks compact. Outbound, set `CALLERID(num)` to a number you own, normalize
to E.164 in one place, and hand the call to `PJSIP/<number>@trunk`. Build
resilience by trying multiple trunks and branching on `${DIALSTATUS}`
(`CHANUNAVAIL`/`CONGESTION` mean re-route; `BUSY`/`NOANSWER` do not), and put
least-cost routing in a `GoSub` table. Finally, NAT for trunks is two-sided:
`external_media_address`/`external_signaling_address`/`local_net` on the
**transport** for your public address, and `direct_media=no`, `rtp_symmetric`,
`force_rport`, and `rewrite_contact` on the **endpoint** for the provider's media.

## Quiz

1. In PJSIP, the credentials used to authenticate an *outbound* call or
   registration to a provider are referenced with:
   - A. `auth=`
   - B. `outbound_auth=`
   - C. `secret=`
   - D. `remotesecret=`
2. You should use a `type=registration` trunk when:
   - A. The provider identifies you by your source IP address.
   - B. The provider gives you a username and password and expects you to log in.
   - C. You never want Asterisk to send a `REGISTER`.
   - D. The trunk is between two static-IP servers you control.
3. The `identify` object's `match` option accepts (choose all that apply):
   - A. An IP address
   - B. A CIDR range
   - C. A hostname (resolved at config-load time)
   - D. A SIP username only
4. On Asterisk 22, `auth_type=userpass` is:
   - A. The only valid value
   - B. Deprecated and converted to `digest`
   - C. Removed and causes a load error
   - D. Required for outbound registration
5. An inbound DID number arrives in the dialplan as:
   - A. `${CALLERID(num)}`
   - B. `${EXTEN}` in the trunk endpoint's `context`
   - C. `${DIALSTATUS}`
   - D. `${CONTEXT}`
6. To send the last two digits of the dialled DID `4830003007` to an extension,
   you would use:
   - A. `${EXTEN:2}`
   - B. `${EXTEN:0:2}`
   - C. `${EXTEN:-2}`
   - D. `${EXTEN:8}`
7. After `Dial()` to a trunk, you should fail over to a backup trunk on which
   `${DIALSTATUS}` values (choose two)?
   - A. `CHANUNAVAIL`
   - B. `BUSY`
   - C. `CONGESTION`
   - D. `NOANSWER`
8. To set the caller-ID number presented to the provider before dialling out, use:
   - A. `Set(CALLERID(num)=4830001000)`
   - B. `Set(from_user=4830001000)`
   - C. `Set(DIALSTATUS=4830001000)`
   - D. `Set(CONNECTEDLINE(num)=4830001000)`
9. The options that tell Asterisk its *public* address when the server is behind
   NAT are set on the:
   - A. `endpoint`
   - B. `aor`
   - C. `transport` (`external_media_address` / `external_signaling_address`)
   - D. `registration`
10. `rtp_symmetric=yes` on a trunk endpoint causes Asterisk to:
    - A. Encrypt RTP with SRTP
    - B. Send RTP back to the address the media actually arrived from, ignoring the SDP
    - C. Disable RTP entirely
    - D. Force direct media between endpoints

**Answers:** 1 — B · 2 — B · 3 — A, B, C · 4 — B · 5 — B · 6 — C · 7 — A, C · 8 — A · 9 — C · 10 — B
