# Modernization plan: Asterisk 16 → 22 LTS

Target: **Asterisk 22 (LTS, released 2024, fully supported through Oct 2028)** —
the newest long-term-support branch. Asterisk 20 (LTS, 2022) is the conservative
fallback; 23 is the current standard release.

Source: docs.asterisk.org/About-the-Project/Asterisk-Versions/

## Major changes since Asterisk 16

| Area | Asterisk 16 (book today) | Asterisk 22 | Impact |
|------|--------------------------|-------------|--------|
| **chan_sip** | Fully documented (Ch 8) | **REMOVED in Asterisk 21+** — gone entirely | High — Ch 8 must be reframed |
| **PJSIP** | "the new channel" (Ch 9) | The *only* SIP channel; the default | High — promote to primary |
| **app_macro** | Already migrated to GoSub in this ed. | Removed | Low — already done |
| **Install** | `./configure && make menuselect` | Same flow; new `./contrib/scripts/install_prereq`, newer pjproject bundled | Medium — version strings, deps |
| **DAHDI** | Ch 5 digital channels | Still available but niche; build separately | Low — add a "still relevant?" note |
| **Realtime** | ODBC (Ch 16) | Same; `res_config_*` unchanged | Low — version strings |
| **AMI/AGI** | Ch 14 | Stable, minor action additions | Low |
| **Security** | iptables/fail2ban (Ch 15) | Same; PJSIP has built-in rate limiting + `security` events | Medium — add PJSIP-era hardening |
| **Codecs** | ulaw/alaw/g722/opus | `codec_opus` now openly distributed; same config | Low |

## Per-chapter work

1. **01 Introduction** — version numbers, history (Digium→Sangoma), "AsteriskNOW"
   is discontinued → mention FreePBX distro. Architecture section still valid.
2. **02 Download & install** — bump versions, dependency script, supported Linux
   distros (Rocky/Alma/Debian 12/Ubuntu 22.04+), menuselect changes.
3. **03 Simple PBX** — convert sip.conf examples to pjsip.conf; CLI command updates.
4. **04 Analog** — minor; DAHDI relevance note.
5. **05 Digital** — minor; DAHDI relevance note.
6. **06 VoIP network** — largely conceptual, still valid; refresh codec/NAT notes.
7. **07 IAX** — chan_iax2 still present but deprecated-ish; add a status note.
8. **08 SIP protocol (chan_sip)** — **DECISION NEEDED** (see below).
9. **09 PJSIP** — promote to *the* SIP chapter; expand wizard/config examples.
10. **10 Dialplan** — mostly valid; verify app names, GoSub patterns.
11. **11 PBX features** — verify feature/func names.
12. **12 Queues** — app_queue still valid; refresh options.
13. **13 CDR** — cdr_adaptive_odbc current; refresh.
14. **14 AMI/AGI** — refresh action/command lists.
15. **15 Security** — add PJSIP rate-limiting, ACLs, TLS defaults, fail2ban regex updates.
16. **16 Realtime** — refresh ODBC config and sorcery (PJSIP realtime).

## Open editorial decisions

- **Ch 8 chan_sip:** keep as historical/"legacy, removed in 21+" with a migration
  pointer, or replace wholesale with PJSIP? (chan_sip no longer ships.)
- **Target version:** lock to 22 LTS (recommended) vs 20 LTS (conservative).
