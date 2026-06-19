# Fact-check — consolidated unverified-claims list (pre-print review)

This is the book-wide summary of the per-chapter fact-check ledgers in this folder.
Every factual assertion in the 16 content chapters was checked against the Asterisk
22.10.0 lab, docs.asterisk.org, official release notes, or the relevant RFC. The items
below are the ones **no authoritative source could confirm** — they are not necessarily
wrong, but each needs an author decision (cite a source, soften the wording, or drop it)
before print.

**Totals:** ~371 claims verified · 32 corrected in place · 35 flagged below.

Per-chapter pass: 02✓ 03✓ 04✓ 06✓ 07✓(clean) 08✓ 09✓ 12✓ 13✓ 14✓ 16✓ 17✓(clean) 18✓ 19✓ 20✓.

---

## Unverified claims by chapter

### Ch 1 — Introduction (`02-introduction.md`) — 6
- **"Asterisk OEM … used by PBX manufacturers"** (L48) — no primary source for a distinct OEM license tier. Marketing/historical; soften or cite.
- **"300,000 systems run Asterisk; Digium sold 4M voice interfaces"** (L98) — dated secondary marketing stat. Re-source or drop.
- **Eastern Management Group figures** ("18% … 85% of open-source PBX market … second in lines")** (L98) — analyst report not accessible as a primary source.
- **"3,000+ changes between Asterisk 1.0 and 1.2"** (L86) — no changelog tally located.
- **"installations with more than 10,000 users"** (L110) — plausible but no citable deployment reference.
- **"Asterisk does not support silence suppression"** (L299) — not cleanly documented yes/no; Asterisk has comfort-noise/VAD features. Reword.

### Ch 2 — Installing (`03-installing-asterisk.md`) — 3
- **"a single iLBC session can require as much as 18 MIPS"** (L23) — no primary codec-spec source for 18 MIPS. Source or soften.
- **menuselect "Add Default Sources" wording** (L221) — not confirmed against a doc (menuselect not run interactively).
- **Ubuntu ISO URL `ubuntu-24.04-live-server-amd64.iso`** (L67) — returns HTTP 404; only point-release filenames exist now (e.g. `…-24.04.4-…`). Update or point at the directory.

### Ch 3 — First PBX (`04-first-pbx-pjsip.md`) — 2
- **DumpChan sample** — was 1st-ed chan_sip; **now regenerated from a live PJSIP channel** during the chan_sip purge. Effectively resolved; confirm the captured layout if you re-run it.
- **IAX `delayreject` vs `delayrejects`** (L268 vs L278) — prose and example disagree; the correct iax.conf option is `delayreject` (singular). Align both.

### Ch 4 — Designing a VoIP network (`06-designing-voip-network.md`) — 3
- **Sangoma `codec_g729`/`codec_opus` "free download" binaries** (L97/109/112/136) — sangoma.com returned HTTP 403 to the fetcher; per-channel G.729 licensing IS confirmed, but the "free download" + codec_opus binary distribution claims need confirming against Sangoma's current page.
- *(Resolved this pass: H.323 port 1719 corrected to UDP RAS; RTP range corrected; the OSI-vs-TCP/IP figure replaced with the accurate table.)*

### Ch 5 — SIP & PJSIP (`07-sip-and-pjsip.md`) — 0 (clean)

### Ch 6 — WebRTC (`08-webrtc.md`) — 2
- **"`codec_opus` ships freely with Asterisk 22"** (L189) — lab has the Opus *passthrough* module only; the *transcoder* `codec_opus` is an external download. Resolve in the codecs chapter and forward-reference. (Same root issue as Ch 4 and Ch 2.)
- **"the two most common are SIP.js and JsSIP"** (L218) — no source quantifies "most common." Soft claim.

### Ch 7 — SIP trunking (`09-sip-trunking.md`) — 2
- **`rewrite_contact` SBC in-dialog routing guidance** (L572, 576-578) — sound expert advice, not a documented default. Keep as guidance or cite.
- **`pjsip show registrations` "(exp. 4s ago)" literal** (L147) — columns are real; the exact suffix is illustrative (couldn't reproduce without a configured registration).

### Ch 8 — Dialplan (`12-dialplan.md`) — 3
- **"GoSub received parameter support in version 10"** (L184) — argument support is real (lab) but not pinned to exactly v10 by a changelog. Drop the version or source it.
- **"MWI works with … some IAX2 phones"** (L567) — general MWI is fine; the "some IAX2" qualifier is uncitable. Low risk.
- **vmail.cgi via `make webvmail`** (L545-553) — couldn't confirm the Perl web interface still ships in the 22 source tree. Verify or note as legacy.

### Ch 9 — PBX features (`13-pbx-features.md`) — 3
- **Parking default ext / slot range** (L64-65, 153) — `res_parking.conf` has no hardcoded default; the sample uses `parkext=700`, `parkpos 701-750` (not 701-720). Tie to the planned res_parking.conf rewrite.
- **MeetMe option-flag / admin-command lists** (L279-303, 339-368) — verified only against legacy docs (module isn't built in 22). Fine as a historical section; label it so.
- **`include => parkedcalls` / "#700 to park"** (L160) — pre-12 default-lot flow; confirm against the res_parking.conf rewrite (default lot context is still `parkedcalls`).

### Ch 10 — Queues (`14-queues.md`) — 3
- **"AgentCallbackLogin deprecated in 1.2, removed in 12"** (L352) — removal-from-22 is confirmed; the specific 1.2/12 versions are not. Drop the version specifics or source them.
- **"recorded using monitor or mixmonitor"** (L292) — standalone `Monitor()` is removed in 22; reword to MixMonitor (queues.conf `monitor-type` accepts only MixMonitor).
- **queue_log event catalog** (L360-376) — mostly consistent, but `AGENTCALLBACKLOGOFF`/`SYSCOMPAT` should be re-verified against current app_queue source.

### Ch 11 — CDR & CEL (`16-cdr-cel.md`) — 1
- **"an account code … is a 20-character string"** (L26) — no documented 20-char limit in A22 (`accountcode` is an unbounded String). Cite the limit or soften.

### Ch 12 — AMI/AGI/ARI (`17-ami-agi-ari.md`) — 0 unverified, but see **Editorial rewrites** below.

### Ch 13 — Realtime (`18-realtime.md`) — 4
- **"Sorcery has a built-in caching … layer"** (L32) and **Quiz 5** (L399) — Sorcery caching is an opt-in `memory_cache` wizard, not always-on. The functional point (qualify/MWI/NAT work for realtime PJSIP, unlike chan_sip's discarded peers) is correct; reword the "cached" rationale.
- **"MySQL and any other Unix ODBC-supported databases"** (L379) — omits the LDAP realtime driver mentioned earlier; minor completeness gap.
- **ODBC realtime** — verified against docs + Alembic sources only; the lab image lacks `res_config_odbc.so` so it wasn't exercised end-to-end.

### Ch 14 — Security (`19-security.md`) — 2
- **"In 2010 hackers used the Sality botnet to scan all vulnerable SIP devices"** (L24) — historical claim, no primary advisory. Cite or soften.
- **RTP range 10000–20000** (L150, 184) — an operator/distro policy value, not an Asterisk built-in default; fine as a recommendation but framed as if fixed.

### Ch 15 — Deployment (`20-deployment.md`) — 1
- **res_prometheus metric inventory** (L427-428) — module presence + "extended" support level are verified; the specific counter list ("call/channel/endpoint/bridge") isn't enumerated in the official config doc. Confirm against a live `/metrics` scrape.

---

## Editorial rewrites flagged (not single-fact fixes)

These are sections that are *dated* rather than a single wrong claim — they need a rewrite,
so they were flagged rather than auto-edited:

- **Ch 12 (AMI), "Link / Unlink events"** — those AMI events were removed in Asterisk 12;
  22 emits `BridgeCreate`/`BridgeEnter`/`BridgeLeave`/`BridgeDestroy`. The "Unlink" example
  also mislabels itself `Event: Link`. Replace the section, regenerated from `manager show events`.
- **Ch 12 (AMI), "Events available" list** — a legacy AMI-v1 catalog (includes removed
  `MeetMe*`, `LinkEvent`/`UnlinkEvent`, etc.). Regenerate from `manager show events`.
- **Ch 12 (AMI), Originate help block** — quoted in the old `Variables:` format; 22 uses
  `[Synopsis]/[Syntax]/[Arguments]`. Content fine, formatting dated. Low priority.
- **Ch 4 figure** — the OSI-stack figure was replaced by a table this pass; commission a
  redrawn TCP/IP-model figure if a visual is wanted.
- **Ch 13 (realtime) phpMyAdmin screenshots** — replace with a current tool (phpMyAdmin/
  Adminer) or convert those lab steps to plain SQL.
- **Codec policy** — Ch 3's trunk example still uses `ilbc`/`g729`; reconcile against the
  PCMU/PCMA/G.722/Opus-only policy and the codecs chapter.
