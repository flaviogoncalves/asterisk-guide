# Fact-check — resolution log (formerly the unverified-claims list)

Every factual assertion in the 16 content chapters was checked against the Asterisk
22.10.0 lab, docs.asterisk.org, official release notes, the module source, or the
relevant RFC. The 35 items that originally had **no confirming source** have now all been
resolved: each was either **replaced with a sourced/corrected statement** or, when no
authoritative source existed, **removed**.

**Status: 0 unverified claims remaining** across all chapters.
Totals after this pass: ~371 claims verified · 41 corrected/reworded · 0 open.

Per-chapter ledgers in this folder carry the row-level citations. Summary of how the
formerly-unverified items were closed:

## Replaced with a sourced/corrected statement

- **Ch 1 (intro):** "Asterisk OEM" reworded to the actual Business-Edition/OEM licensing
  history (nojitter); silence-suppression claim confirmed and the contradictory codec
  bullet fixed; Opus 5.3→6–510 kbps and LPC10 2.5→2.4 kbps (RFC 6716 / FS-1015).
- **Ch 2 (installing):** iLBC "18 MIPS" anchored to the GIPS iLBC white paper (TI C54x,
  30 ms frame); menuselect sound-package menu names corrected; Ubuntu ISO URL → current
  point-release / releases.ubuntu.com directory.
- **Ch 3 (first PBX):** IAX `delayrejects` → `delayreject` (iax.conf.sample).
- **Ch 4 (designing):** codec_g729/codec_opus "free" claim → `codecs.xml`
  `support_level=external` (G.729 "a license must be purchased"); H.323 port 1719
  corrected to UDP RAS; RTP range corrected; OSI figure replaced by the TCP/IP table;
  IAX2 "IETF draft" → "RFC 5456 (Informational)".
- **Ch 6 (WebRTC):** Opus passthrough (`res_format_attr_opus`, bundled) vs the
  separately-installed `codec_opus` transcoder, sourced; SIP.js/JsSIP ranking neutralised.
- **Ch 7 (trunking):** `pjsip show registrations` output captured from a real lab
  registration; `rewrite_contact` SBC advice reframed as a sourced recommendation.
- **Ch 8 (dialplan):** GoSub argument support since 1.6 (not 10); MWI works with
  PJSIP/SIP/DAHDI (IAX2 qualifier dropped); `vmail.cgi`/`make webvmail` confirmed to
  still ship in 22, paths corrected.
- **Ch 9 (PBX features):** parking `parkpos 701-720` confirmed against
  `res_parking.conf.sample`; legacy features.conf-style block rewritten to res_parking
  syntax; MeetMe flag/admin lists explicitly labelled legacy.
- **Ch 10 (queues):** AgentCallbackLogin deprecation corrected to 1.4; `Monitor()` →
  MixMonitor; queue_log catalog verified against `app_queue.c` (dropped the nonexistent
  `AGENTCALLBACKLOGOFF`, replaced `TRANSFER` with `ATTENDEDTRANSFER`/`BLINDTRANSFER`).
- **Ch 11 (CDR):** accountcode "20-character" → free-form string, 80-char CDR field
  (CDR Specification).
- **Ch 13 (realtime):** Sorcery "caching" reworded to on-demand realtime loading
  (memory_cache is opt-in); realtime driver list expanded to ODBC/MySQL/PostgreSQL/LDAP.
- **Ch 14 (security):** Sality botnet corrected to the Feb 2011 UCSD Network Telescope
  scan, cited to the IEEE/ACM ToN paper (footnote); RTP range reframed as the rtp.conf
  sample's example, not a built-in default.
- **Ch 15 (deployment):** res_prometheus metric list upgraded to the exact metric names
  grepped from the module source (core/channels/calls/endpoints/bridges/pjsip).

## Removed (no authoritative source; dated)

- **Ch 1 (intro):** the "300,000 systems / 4M interfaces" VoIP-Supply stat, the Eastern
  Management Group market-share figures, the "3,000+ changes 1.0→1.2" tally, and the
  "10,000-user installations" figure — all dated, uncorroborated marketing/analyst
  numbers, replaced with undated qualitative statements.
- Various dead/expired URLs (handled in the broken-link pass): IAX IETF draft → RFC 5456,
  OrderlyCalls → Asterisk-Java, PROTOS ee.oulu.fi (URL dropped, name+attribution kept),
  MySQL Connector/ODBC version-pinned link generalised, mailing-lists → community forum,
  svn.digium.com → GitHub git repos.

---

## Editorial rewrites still flagged (not single-fact items — for the author)

These are *dated sections* rather than wrong claims, so they were left for an editorial pass:

- **Ch 12 (AMI), "Link / Unlink events"** — removed in Asterisk 12; 22 emits
  `BridgeCreate`/`BridgeEnter`/`BridgeLeave`/`BridgeDestroy`. Regenerate from
  `manager show events`.
- **Ch 12 (AMI), "Events available" list** — legacy AMI-v1 catalog; regenerate from
  `manager show events`.
- **Ch 12 (AMI), Originate help block** — old `Variables:` format; 22 uses
  `[Synopsis]/[Syntax]/[Arguments]`. Low priority.
- **Ch 4 figure** — commission a redrawn TCP/IP-model figure if a visual is wanted (the
  OSI figure was replaced by a table).
- **Ch 13 (realtime) phpMyAdmin screenshots** — refresh with a current tool or convert
  to plain SQL.
- **Codec policy** — Ch 3's trunk example still uses `ilbc`/`g729`; reconcile against the
  PCMU/PCMA/G.722/Opus-only policy and the codecs chapter.
