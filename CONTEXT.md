# Asterisk Guide — 2nd Edition

The canonical terminology for the book. The 2nd edition targets **Asterisk 22 LTS**,
where PJSIP is the only SIP channel. Use these terms consistently across every chapter;
prefer the canonical term and avoid the listed aliases (except when explicitly teaching
legacy/historical material, where an alias may appear marked as legacy).

## Language

### SIP / channels

**Endpoint**:
A PJSIP configuration object (`type=endpoint`) representing a SIP entity (phone or trunk).
_Avoid_: peer, friend, user (these are removed chan_sip/`sip.conf` concepts — legacy only).

**PJSIP**:
The SIP channel driver in Asterisk 22 (`chan_pjsip` + the `res_pjsip_*` stack).
_Avoid_: "the new SIP channel" (it is no longer new), chan_sip (removed in Asterisk 21).

**AOR** (Address of Record):
The PJSIP object (`type=aor`) that stores where to reach an endpoint (its contacts).

**Contact**:
A reachable SIP URI registered to an AOR. An AOR may hold multiple contacts.

**Transport**:
A PJSIP object (`type=transport`) binding an IP/port/protocol (udp, tcp, tls, ws, wss).

**Channel**:
A live communication path to/from Asterisk (e.g. `PJSIP/6001-0000001a`). A call bridges channels.

**Trunk**:
An endpoint that connects Asterisk to a provider (ITSP) or another PBX, rather than to a user's phone.

### Dialplan

**Dialplan**:
The call-routing logic in `extensions.conf` (or AEL/realtime), organized into contexts.
_Avoid_: "the config", "routing rules" (be specific).

**Context**:
A named section of the dialplan that groups extensions and defines a security/reachability boundary.

**Extension**:
A labelled set of dialplan steps (priorities) matched against dialed digits/patterns.
_Avoid_: using "extension" loosely to mean "a phone/endpoint".

### Data & realtime

**Realtime (ARA)**:
Asterisk Realtime Architecture — loading configuration from a database via `res_config_*`.

**Sorcery**:
The PJSIP object-persistence layer; the mechanism behind PJSIP realtime (`ps_*` tables).

## Relationships

- An **Endpoint** references one or more **AOR**s and zero or more **Auth**s and a **Transport**.
- An **AOR** holds zero or more **Contact**s (dynamic registration or static).
- A **Trunk** is an **Endpoint** plus (usually) an outbound **Registration** and/or **Identify**.
- A **Dialplan** is composed of **Context**s; a **Context** contains **Extension**s.
- An **Extension** uses `Dial(PJSIP/...)` to create and bridge **Channel**s.

## Example dialogue

> **Reader:** "I defined a `[6001]` peer in sip.conf but it won't register on Asterisk 22."
> **Author:** "chan_sip was removed in Asterisk 21 — there is no `sip.conf`. You define
> a **PJSIP endpoint** plus an **AOR** and an **Auth**; the phone registers a **Contact**
> to the AOR. See the SIP & PJSIP chapter."

## Flagged ambiguities

- "peer/friend/user" — 1st-edition chan_sip vocabulary. Resolved: the canonical object is
  the **Endpoint** (+ AOR/Auth/Transport). Aliases appear only in legacy/migration sections.
- "the new SIP channel" — 1st-edition framing of PJSIP. Resolved: PJSIP is now *the* SIP channel.
