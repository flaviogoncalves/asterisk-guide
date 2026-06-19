---
theme: seriph
title: 'Migrating from chan_sip to PJSIP'
info: |
  ## Asterisk Guide — Chapter 9
  Migrating from chan_sip to PJSIP. Asterisk 22 LTS, PJSIP-first.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
transition: slide-left
mdc: true
colorSchema: light
---

# Migrating from chan_sip to PJSIP

Chapter 9

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

- **Explain** why `chan_sip` is gone in Asterisk 22 and what replaces it
- **Map** the `peer`/`user`/`friend` model onto the PJSIP object model
- **Run** the `sip_to_pjsip.py` conversion script and review its output critically
- **Translate** the common device types by hand — phone, inbound trunk, outbound registration
- **Migrate** NAT, media, DTMF, codec, and auth settings option-by-option
- **Update** the dialplan (`SIP/` → `PJSIP/`) and the CLI (`sip show` → `pjsip show`)
- **Migrate** a realtime deployment from `sippeers`/`sipregs` to the Sorcery `ps_*` tables

</v-clicks>

<!--
Frame this as a migration project, not just a version bump. The destination is always PJSIP.
-->

---
layout: section
---

# Why migrate at all

---

# Why migrate at all

`chan_sip` served Asterisk for nearly two decades — but it carried architectural debt.

<div grid="~ cols-2 gap-8" class="mt-2">
<div>

**The legacy you are leaving**

- One monolithic module
- A single config block per device
- Weak multi-transport support
- A SIP stack that fell behind the RFCs

</div>
<div>

**Where you are going**

- **PJSIP** on Teluu's mature pjproject stack
- Introduced in Asterisk 12, the ground-up replacement
- Single-purpose objects that reference each other
- The **only** SIP driver in Asterisk 22

</div>
</div>

<div class="mt-4 p-3 text-sm" style="border-left: 4px solid #1C5D99;">
<code>chan_sip</code> was <strong>deprecated in 17, removed from the default build in 19, and deleted in Asterisk 21</strong>.
There is no flag to turn it back on. The question is <em>how</em>, not <em>whether</em>.
</div>

---

# It simply isn't there

Confirm the situation on any Asterisk 22 system:

```text
*CLI> module show like chan_sip
Module                         Description              Use Count  Status      Support Level
0 modules loaded

*CLI> module show like chan_pjsip
Module                         Description              Use Count  Status      Support Level
chan_pjsip.so                  PJSIP Channel Driver     0          Running     core
1 modules loaded
```

`chan_sip` returns **0 modules loaded** — there is nothing to migrate *to* except PJSIP.

<div class="mt-3 text-sm opacity-70">
The protocol on the wire does not change: a phone that registered and called yesterday will register and call tomorrow.
</div>

---
layout: section
---

# The conceptual mapping

---

# There is no single "peer"

In `sip.conf`, one bracketed block — `peer`, `user`, or `friend` — described **everything**
about a device. PJSIP breaks that into smaller, single-purpose objects, each tagged with a
`type=`, that **reference each other by name**.

<div class="text-sm mt-2">

| PJSIP object (`type=`) | Responsibility |
| --- | --- |
| `endpoint` | Call-handling identity: codecs, context, DTMF, media, NAT; references its `auth`/`aors`/`transport` |
| `aor` | *Where* to reach the device — registered or static contacts, `max_contacts`, qualify |
| `auth` | Credentials for inbound and/or outbound authentication |
| `identify` | Match an inbound request to an endpoint by **source IP** instead of `From` user |
| `transport` | The listening socket(s): protocol, bind address/port, NAT/external addresses |
| `registration` | An **outbound** REGISTER from Asterisk to a provider |

</div>

<div class="mt-3 text-sm opacity-70">
The <code>friend</code>/<code>peer</code>/<code>user</code> distinction disappears — in PJSIP everything is an <strong>endpoint</strong>.
</div>

---

# One block becomes several objects

A single `sip.conf` friend typically becomes three objects (`endpoint` + `auth` + `aor`) that
share a name and point at one another:

```text
        sip.conf                           pjsip.conf
    ┌──────────────┐          ┌──────────┐   ┌──────┐   ┌──────┐
    │   [2000]     │          │ endpoint │──▶│ auth │   │ aor  │
    │ type=friend  │ becomes  │  [2000]  │   │[2000]│   │[2000]│
    │ host=dynamic │ ───────▶ │  auth=───┼──▶└──────┘   └──────┘
    │ secret=...   │          │  aors=───┼──────────────────▶ ▲
    └──────────────┘          └────┬─────┘
                                   │ transport=
                                   ▼
                              ┌───────────┐
                              │ transport │  (shared by all endpoints)
                              └───────────┘
```

The **endpoint is the glue**: it names a `transport`, an `auth`, and one or more `aors`.

---
layout: section
---

# The conversion tool

---

# `sip_to_pjsip.py`

Asterisk ships a Python script that reads an existing `sip.conf` and writes a `pjsip.conf`.
It is **not** a CLI command — it lives in the Asterisk **source tree**:

```text
${ASTERISK_SRC}/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py
```

```bash
cd /etc/asterisk
python /usr/src/asterisk-22.10.0/contrib/scripts/sip_to_pjsip/sip_to_pjsip.py \
       sip.conf pjsip_generated.conf
```

Its only real options:

```text
-h, --help              show usage
-p, --prefix PREFIX     output prefix for include files (default: pjsip_)
-q, --quiet             don't print messages to stdout
```

<div class="mt-2 text-sm opacity-70">
The same directory holds <code>sip_to_pjsql.py</code> (the realtime variant) and the helper modules.
</div>

---

# Treat the output as a first draft

Anything it cannot map cleanly is fenced into a block at the top of the output file:

```ini
;--
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
[general]
bindport = 5060
[zoiper]
qualify = yes
...
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Non mapped elements end
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
--;
```

<div class="text-sm mt-2">

- **Transports are guessed, not designed** — review and rewrite the transport
- **NAT/external addresses need a human** — confirm `external_*_address`, `local_net` by hand
- **`qualify`, custom timers** land in "non-mapped" — read that block top-to-bottom
- **Codec lists, contexts, security** need review — no device left unintentionally open

</div>

<div class="mt-2 text-sm opacity-70">
Workflow: run into a <em>scratch</em> file, diff and review, fold the good parts into the real <code>pjsip.conf</code>, then test.
</div>

---
layout: section
---

# Side-by-side translations

---

# A registering phone (`host=dynamic`)

A desk phone or softphone that logs in with a secret and registers its own location.

<div grid="~ cols-2 gap-6 text-sm">
<div>

**Legacy (removed in 21) — `sip.conf`**

```ini
[2000]
type=friend
host=dynamic
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmfmode=rfc2833
secret=Sup3rSecret
qualify=yes
```

</div>
<div>

**Asterisk 22 — `pjsip.conf`**

```ini
[2000]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
dtmf_mode=rfc4733
auth=2000
aors=2000

[2000]
type=auth
auth_type=digest
username=2000
password=Sup3rSecret

[2000]
type=aor
max_contacts=1
qualify_frequency=60
```

</div>
</div>

<div class="mt-1 text-sm opacity-70">
<code>host=dynamic</code> → <code>aor</code> with <code>max_contacts</code>; <code>secret=</code> → <code>password=</code> in <code>type=auth</code>; <code>qualify=yes</code> → <code>qualify_frequency=60</code> on the <strong>aor</strong>.
</div>

---

# An inbound trunk (`host=<ip>` / `type=peer`)

A provider that sends calls from a known IP. No registration — authenticate by **source IP**.

<div grid="~ cols-2 gap-6 text-sm">
<div>

**Legacy (removed in 21) — `sip.conf`**

```ini
[itsp-in]
type=peer
host=203.0.113.10
context=from-pstn
disallow=all
allow=ulaw
insecure=invite
```

</div>
<div>

**Asterisk 22 — `pjsip.conf`**

```ini
[itsp-in]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw

[itsp-in]
type=aor
contact=sip:203.0.113.10:5060

[itsp-in]
type=identify
endpoint=itsp-in
match=203.0.113.10
```

</div>
</div>

<div class="mt-2 p-2 text-sm" style="border-left: 4px solid #1C5D99;">
The crucial move: <strong><code>insecure=invite</code> → <code>type=identify</code> + <code>match=</code></strong>. Matching the source IP is more explicit and more secure. <code>match=</code> accepts an IP, a CIDR range, or a hostname.
</div>

---

# An outbound registration (`register =>`)

When the provider wants *you* to log in to *them*: one `register =>` line becomes a dedicated
`type=registration` object plus an `outbound_auth`.

<div grid="~ cols-2 gap-6 text-sm">
<div>

**Legacy (removed in 21) — `sip.conf`**

```ini
[general]
register => 1020:supersecret@sip.example.com:5600/9999

[itsp]
type=peer
host=sip.example.com
port=5600
defaultuser=1020
secret=supersecret
fromuser=1020
fromdomain=sip.example.com
context=from-pstn
```

</div>
<div>

**Asterisk 22 — `pjsip.conf`**

```ini
[itsp]
type=endpoint
context=from-pstn
disallow=all
allow=ulaw
outbound_auth=itsp-auth
aors=itsp-aor
from_user=1020
from_domain=sip.example.com

[itsp-auth]
type=auth
auth_type=digest
username=1020
password=supersecret

[itsp-aor]
type=aor
contact=sip:sip.example.com:5600

[itsp-reg]
type=registration
transport=transport-udp
outbound_auth=itsp-auth
server_uri=sip:sip.example.com:5600
client_uri=sip:1020@sip.example.com:5600
contact_user=9999
retry_interval=60
```

</div>
</div>

---

# Reading the `register =>` line

```text
register => 1020:supersecret@sip.example.com:5600/9999
            └────┬────────┘ └────────┬──────────┘ └┬─┘
              auth object        server_uri    contact_user
```

<v-clicks>

- `1020:supersecret` → the **`auth`** object (referenced as `outbound_auth`)
- `@sip.example.com:5600` → the **`server_uri`**
- `/9999` (where the provider delivers inbound calls) → **`contact_user=9999`**
- `defaultuser`/`fromuser`, `fromdomain` → `from_user`, `from_domain` on the endpoint

</v-clicks>

<div class="mt-3 text-sm opacity-70">
Note <code>outbound_auth</code> appears <strong>twice</strong>: the registration uses it for the REGISTER; the endpoint uses it to answer the <code>407</code> challenge on outbound INVITEs.
</div>

---
layout: section
---

# Option-by-option reference

---

# Translating by hand

The lookup table — every PJSIP option and its placement verified against the Asterisk 22 lab.

<div class="text-sm">

| Legacy `sip.conf` | Asterisk 22 `pjsip.conf` | Where |
| --- | --- | --- |
| `[peer]` / `[user]` / `[friend]` | `type=endpoint` (+ `auth` + `aor`) | — |
| `host=dynamic` | `max_contacts=1` (device REGISTERs) | aor |
| `host=<ip/host>` | `contact=sip:<host>:<port>` | aor |
| `register => u:p@host/ext` | `type=registration` + `outbound_auth` | registration |
| `secret=` | `password=` | auth |
| `nat=force_rport,comedia` | `force_rport=yes` + `rewrite_contact=yes` + `rtp_symmetric=yes` | endpoint |
| `directmedia=yes/no` | `direct_media=yes/no` | endpoint |
| `dtmfmode=rfc2833` | `dtmf_mode=rfc4733` | endpoint |
| `qualify=yes` | `qualify_frequency=<seconds>` | aor |
| `insecure=invite` | omit auth; use `type=identify` + `match=` | identify |
| `fromuser=` / `fromdomain=` | `from_user=` / `from_domain=` | endpoint |
| `externaddr=` / `externip=` | `external_media_address=` + `external_signaling_address=` | transport |
| `localnet=` | `local_net=` | transport |

</div>

---

# NAT, media, and DTMF in detail

This is where most "it registers but has no audio" tickets come from. PJSIP **splits** the
old `nat=` shorthand so you can reason about each behaviour:

```ini
; sip.conf:  nat=force_rport,comedia
; pjsip.conf (on the endpoint):
force_rport=yes        ; reply to the source IP/port of the request (RFC 3581)
rewrite_contact=yes    ; rewrite the stored Contact to the real source address
rtp_symmetric=yes      ; send RTP back where it actually came from (comedia)
```

<div grid="~ cols-2 gap-6 text-sm mt-2">
<div>

**Media** — `directmedia` → `direct_media` (the underscore is the whole change). Keep `direct_media=no` whenever the call must be anchored on Asterisk.

</div>
<div>

**DTMF** — the RFC was renumbered: `dtmfmode=rfc2833` → `dtmf_mode=rfc4733`. Valid values: `rfc4733`, `inband`, `info`, `auto`, `auto_info` (default `rfc4733`).

</div>
</div>

<div class="mt-2 text-sm opacity-70">
<strong>Codecs:</strong> nothing changes — <code>disallow=all</code> then <code>allow=ulaw</code> uses the identical syntax on the endpoint.
</div>

---

# `secret` → `auth` and `auth_type`

`chan_sip`'s `secret=` becomes the `password=` of a `type=auth` object; the method is set with
`auth_type`. **Use `auth_type=digest`.**

```text
*CLI> config show help res_pjsip auth auth_type
...
 The older 'md5' and 'userpass' values are deprecated and converted to 'digest'.
    userpass - Deprecated.  Use 'digest'.
    md5 - Deprecated.  Use 'digest'.
    digest - If selected, the 'password' ... parameters must be provided.
```

<div class="mt-3 text-sm opacity-80">
You will see <code>auth_type=userpass</code> in older configs and in the script's output — it is harmless and silently converted, but write <code>digest</code> in anything new.
</div>

---
layout: section
---

# Dialplan and CLI changes

---

# Channel strings: `SIP/` → `PJSIP/`

Every `Dial()` and channel reference in `extensions.conf` that named the old technology must
be updated:

```text
; Before (chan_sip) — the legacy you are replacing
exten => 2000,1,Dial(SIP/2000,30,tT)

; After (chan_pjsip)
exten => 2000,1,Dial(PJSIP/2000,30,tT)
```

Trunk dial strings follow the same pattern — `Dial(SIP/${EXTEN}@itsp)` → `Dial(PJSIP/${EXTEN}@itsp)`.

<div class="mt-3 text-sm opacity-80">
PJSIP also adds <code>PJSIP_DIAL_CONTACTS()</code> (ring every contact on an AOR at once), <code>PJSIP_HEADER()</code>, and <code>PJSIP_MEDIA_OFFER()</code>. Grep your dialplan for <code>SIP/</code>, <code>SIPPEER</code>, <code>SIPCHANINFO</code>, and SIP <code>CHANNEL(...)</code> references and translate each.
</div>

---

# CLI: `sip show ...` → `pjsip show ...`

The entire `sip ...` command tree is gone with the driver — the old commands return
*No such command*, not an error your monitoring will catch.

<div class="text-sm">

| `chan_sip` command | Asterisk 22 (`chan_pjsip`) |
| --- | --- |
| `sip show peers` | `pjsip show endpoints` |
| `sip show peer <name>` | `pjsip show endpoint <name>` |
| `sip show registry` | `pjsip show registrations` |
| `sip show channels` | `core show channels` (or `pjsip show channels`) |
| `sip set debug on` | `pjsip set logger on` |
| `sip reload` | `module reload res_pjsip.so` (or `core reload`) |

</div>

<div class="mt-3 text-sm opacity-70">
Also available: <code>pjsip show aors</code>, <code>pjsip show auths</code>, <code>pjsip show contacts</code>, <code>pjsip show identifies</code>. Focus the logger with <code>pjsip set logger host &lt;ip&gt;</code>.
</div>

---
layout: section
---

# Realtime (ARA) migration

---

# `sippeers`/`sipregs` → Sorcery `ps_*` tables

If you ran `chan_sip` from a database, PJSIP uses a different storage layer — **Sorcery** —
with one table *per object type*.

<div class="text-sm">

| `chan_sip` realtime table | PJSIP / Sorcery table(s) |
| --- | --- |
| `sippeers` | `ps_endpoints`, `ps_aors`, `ps_auths` (one row each, split out) |
| `sipregs` | `ps_contacts` (dynamic registrations) |
| — (outbound `register=>`) | `ps_registrations` |
| — (IP matching) | `ps_endpoint_id_ips` (the `identify` objects) |
| — (domain aliases) | `ps_domain_aliases` |

</div>

<div grid="~ cols-2 gap-6 text-sm mt-3">
<div>

**The schema is generated for you** — run `alembic upgrade head` against the `config` database (migrations under `contrib/ast-db-manage/`).

</div>
<div>

**There is a SQL conversion script** — `sip_to_pjsql.py` emits `INSERT` statements for the `ps_*` tables. Review before loading. Then point `sorcery.conf` at your database.

</div>
</div>

---
layout: section
---

# Checklist and pitfalls

---

# Migration checklist

A pragmatic order of operations for a production cutover:

<div class="text-sm">

1. **Inventory** every device, trunk, and `register =>` (or every `sippeers`/`sipregs` row)
2. **Run the converter into a scratch file** — never point it at your live `pjsip.conf`
3. **Read the "Non mapped elements" block** and resolve every line
4. **Design the transport(s) by hand** — one per IP/port; add TLS/TCP; set `external_*`/`local_net`
5. **Verify auth** — `auth_type=digest`, usernames, passwords on every `auth` object
6. **Verify NAT/media/DTMF** per endpoint — `force_rport`/`rewrite_contact`/`rtp_symmetric`, `direct_media`, `dtmf_mode=rfc4733`
7. **Update the dialplan** — `SIP/` → `PJSIP/` everywhere; check `SIP*` functions and variables
8. **Update scripts and monitoring** — any AMI/CLI consumer of `sip show ...` must move to `pjsip show ...`
9. **Reload and verify** — `module reload res_pjsip.so`, then `pjsip show endpoints` / `registrations` / `identifies`
10. **Test with the packet logger** — `pjsip set logger on`; place a registration, an inbound call, and an outbound call

</div>

---

# Common pitfalls

<div class="text-sm">

<v-clicks>

- **`alwaysauthreject` is built-in now — don't look for it.** PJSIP never reveals whether an endpoint exists. Throttling is the global `unidentified_request_count`/`unidentified_request_period`, on by default.
- **`insecure=invite` is not a PJSIP option — use `identify`.** Match as narrowly as possible (specific host IPs, not wide CIDRs) and back it with a `type=acl`. An IP-matched trunk with no auth is a toll-fraud target.
- **One transport per IP/port.** You cannot bind two transports to the same IP:port, nor multiple TCP/TLS transports of the same IP version. Consolidate.
- **`qualify=yes` doesn't translate to a boolean.** It belongs on the **aor** as `qualify_frequency=<seconds>` — which is why the converter drops it in "non-mapped".
- **`secret=` is not an endpoint option.** Credentials live only in a `type=auth` the endpoint *references* (`auth=` inbound, `outbound_auth=` outbound).
- **The CLI and scraping scripts break silently.** `sip show ...` returns "No such command". Audit every cron job, Nagios check, and AMI client before cutover.

</v-clicks>

</div>

---
layout: center
class: text-center
---

# 🧪 Lab

**Convert a legacy `sip.conf` to `pjsip.conf`**

Run `sip_to_pjsip.py` against a sample config, read the *Non-mapped elements* block,
hand-build the transport, and verify with `pjsip show endpoints` + `pjsip set logger on`.

See the matching lab in `labs/LAB-GUIDE.md`

<div class="mt-4 text-sm opacity-70">
Verified against the book's Asterisk 22.10.0 lab — registration, inbound call, and outbound call end to end.
</div>

---
layout: section
---

# Summary

---

# Summary

<v-clicks>

- Migrating to Asterisk 22 means migrating **off `chan_sip`** — removed in 21, with PJSIP the only SIP channel left.
- Re-express each `peer`/`user`/`friend` block as **cooperating objects**: `endpoint` + `auth` + `aor`, plus `identify` (inbound trunk), `registration` (outbound login), and a shared `transport`.
- `sip_to_pjsip.py` does the bulk translation and flags what it cannot map — but its output is a **first draft**: design transport, NAT, and security by hand and test before production.
- Update the dialplan (`SIP/` → `PJSIP/`) and your fingers and scripts (`sip show` → `pjsip show`, `sip set debug` → `pjsip set logger`).
- Realtime moves from `sippeers`/`sipregs` to the Sorcery `ps_*` tables, with `sip_to_pjsql.py` and `contrib/ast-db-manage` to help.

</v-clicks>

<div class="mt-4 text-sm opacity-70">
Watch the pitfalls and the cutover is <strong>mechanical rather than mysterious</strong>.
</div>

---
layout: center
class: text-center
---

# Quiz

Ten questions at the end of Chapter 9 in *Asterisk Guide*.

<div class="mt-4 text-sm opacity-70">
e.g. <em>A single <code>sip.conf</code> <code>type=friend</code> block most commonly becomes which set of PJSIP objects?</em>
</div>
