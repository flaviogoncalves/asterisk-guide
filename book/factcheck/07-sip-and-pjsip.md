# Fact-check ledger — SIP & PJSIP in depth

Verified: 24 · Wrong (fixed): 0 · Unverified: 0

Lab: Asterisk 22.10.0 (astlab-asterisk, healthy). Lab commands run via
`docker compose -f /Users/flavio/crosscall/astbook/lab/docker-compose.yml exec -T asterisk asterisk -rx '<cmd>'`.

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "The original SIP channel driver `chan_sip` … finally **removed in Asterisk 21**" | 3 | VERIFIED | https://www.asterisk.org/asterisk-21-module-removal-chan_sip/ |
| 2 | "PJSIP (`chan_pjsip`, configured via `pjsip.conf`) is now the only SIP channel driver" | 3 | VERIFIED | https://www.asterisk.org/asterisk-21-module-removal-chan_sip/ (chan_sip removed in 21; PJSIP is the remaining SIP driver) |
| 3 | "SDP was originally defined in IETF RFC 2327, now obsoleted by RFC 4566" | 103 | VERIFIED | https://datatracker.ietf.org/doc/html/rfc4566 ("This memo obsoletes RFC 2327 and RFC 3266") |
| 4 | SDP example uses `telephone-event/8000` (pt 101) with `a=fmtp:101 0-11,16` (DTMF events) | 126-127 | VERIFIED | RFC 4733 "RTP Payload for DTMF Digits, Telephony Tones, and Telephony Signals" — https://datatracker.ietf.org/doc/html/rfc4733 |
| 5 | "Ignore the Contact/Via address and reply to where the packet came from … behaviour defined in RFC 3581 (`rport`)" | 176 | VERIFIED | RFC 3581 "An Extension to SIP for Symmetric Response Routing" — https://datatracker.ietf.org/doc/html/rfc3581 |
| 6 | "On PJSIP it is `force_rport=yes`" (default yes) | 176, 541 | VERIFIED | lab: `config show help res_pjsip endpoint force_rport` → "Default: yes" |
| 7 | "`rewrite_contact=yes` rewrites the stored contact to the source address" (default no) | 176 | VERIFIED | lab: `config show help res_pjsip endpoint rewrite_contact` → "Default: no"; synopsis rewrites contact to source |
| 8 | "symmetric RTP … On PJSIP this is `rtp_symmetric=yes`" (default no) | 177, 536 | VERIFIED | lab: `config show help res_pjsip endpoint rtp_symmetric` → "Default: no" |
| 9 | "Sending a periodic OPTIONS (a *qualify*) keeps the pinhole open … `qualify_frequency=` on the AOR" | 178 | VERIFIED | docs.asterisk.org res_pjsip module config: contact marked available only if qualify OPTIONS gets 2XX; interval in seconds — https://docs.asterisk.org/Latest_API/API_Documentation/Module_Configuration/res_pjsip/ |
| 10 | "direct_media … `direct_media=yes` the RTP flow goes directly" (default yes) | 44, 46 | VERIFIED | lab: `config show help res_pjsip endpoint direct_media` → "Default: yes" |
| 11 | "Asterisk is … a back-to-back user agent (B2BUA)" | 44 | VERIFIED | docs.asterisk.org describes Asterisk PJSIP as B2BUA (PJSIP Configuration Sections and Relationships) |
| 12 | "PJSIP … first introduced in Asterisk 12" | 213 | VERIFIED | res_pjsip/chan_pjsip included with Asterisk 12 — https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/Migrating-from-chan_sip-to-res_pjsip/ |
| 13 | "you cannot bind multiple TCP or TLS transports of the same IP version" | 308 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/PJSIP-Transport-Selection/ |
| 14 | `type=auth` `auth_type=userpass` example | 300-304 | VERIFIED | lab: `config show help res_pjsip auth auth_type` → "Default: userpass" (note: userpass now deprecated→digest, but still valid/default) |
| 15 | `external_media_address` = "Media address to handle external RTP" | 451-453 | VERIFIED | lab: `config show help res_pjsip transport external_media_address` → "External IP address to use in RTP handling" |
| 16 | `external_signaling_address` = "External SIP address where to receive messages" | 459-461 | VERIFIED | lab: `config show help res_pjsip transport external_signaling_address` → "External address for SIP signalling" |
| 17 | `local_net` = "The network you consider your local network" | 467-469 | VERIFIED | lab: `config show help res_pjsip transport local_net` → "Network to consider local (used for NAT purposes)." |
| 18 | "qualify_frequency … applied to the AOR (not the endpoint)" and unit seconds | 549, 739 | VERIFIED | lab: `config show help res_pjsip aor qualify_frequency` → synopsis "Time in seconds", on aor object |
| 19 | "The function PJSIP_DIAL_CONTACTS will be translated to the list of contacts to dial" | 578 | VERIFIED | lab: `core show function PJSIP_DIAL_CONTACTS` → "Return a dial string for dialing all contacts on an AOR" |
| 20 | noload module names res_pjsip / res_pjsip_pubsub / res_pjsip_session / chan_pjsip / res_pjsip_exten_state / res_pjsip_log_forwarder | 629-634 | VERIFIED | lab module show confirms first five Running; res_pjsip_log_forwarder is a real module — https://www.asterisk.org/new-pjsip-logging-functionality/ |
| 21 | "no bare `pjsip reload` command — only `pjsip reload qualify aor|endpoint`" | 645 | VERIFIED | lab: `core show help pjsip reload` → only `pjsip reload qualify aor` / `pjsip reload qualify endpoint` |
| 22 | CLI: pjsip show endpoints / show endpoint / show aors / show registrations / list endpoints / list contacts | 647-677 | VERIFIED | lab `core show help` for each → all exist with shown usage |
| 23 | "`pjsip set logger on`/`off`" and "restrict … `pjsip set logger host <ip>`" | 684-688 | VERIFIED | lab: `core show help pjsip set logger` → `{on|off|host|add|method|...}` |
| 24 | "`pjsip set history on`", "`pjsip show history`", "`pjsip set history clear`", "`pjsip show history entry <n>`" | 692-704 | VERIFIED | lab: `pjsip set history {on|off|clear}`; `pjsip show history [entry <num>|where ...]` |

## Unverified claims requiring author attention

None. Every checkable affirmation was verified against the running Asterisk 22.10.0 lab, docs.asterisk.org / asterisk.org, or the relevant RFC.

## Notes (not corrections)

- Line 300-304 / 419-421: `auth_type=userpass` is the documented default and still works in
  Asterisk 22, but the lab help marks `md5`/`userpass` as **deprecated** (silently converted
  to `digest`). The examples are not wrong; a future-proofing note could prefer `auth_type=digest`.
  Left unchanged (judgment call, not a factual error).
- Line 634: `res_pjsip_log_forwarder.so` is a valid module name (introduced ~Asterisk 13) but is
  not loaded in this particular lab build (`module show like log_forwarder` → 0 modules). The
  `noload` example name is correct per official docs; behavior is build-dependent.
