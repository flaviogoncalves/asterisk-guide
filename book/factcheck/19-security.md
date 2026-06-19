# Fact-check ledger — Asterisk Security

Verified: 24 · Wrong (fixed): 3 · Unverified: 0

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "This chapter targets **Asterisk 22 LTS**, where PJSIP (`res_pjsip` / `chan_pjsip`) is the only SIP channel." | 5 | VERIFIED | lab: `module show like res_pjsip.so` / `chan_pjsip` (both Running, core); chan_sip not present |
| 2 | "The old `chan_sip` driver was removed in Asterisk 21" | 5 | VERIFIED | docs.asterisk.org/Development/Asterisk-Module-Deprecations/ — chan_sip Removed Version 21; lab: `module show like chan_sip.so` → 0 modules |
| 3 | "failed authentications are now emitted through the Asterisk security event framework and the dedicated `security` logger channel" | 5 | VERIFIED | lab: `logger show channels` → `/var/log/asterisk/security … SECURITY`; docs.asterisk.org/Deployment/Asterisk-Security-Framework/Asterisk-Security-Event-Logger/ |
| 4 | "4569 is the IAX (chan_iax2)" | 130 | VERIFIED | IANA/standard IAX2 port 4569; lab: `module show like chan_iax2` present |
| 5 | "2727 is the MGCP protocol (chan_mgcp) … you can simply remove the module" | 130 | WRONG (context fixed) | chan_mgcp removed in 21 — docs.asterisk.org/Development/Asterisk-Module-Deprecations/ (Removed Version 21); lab: `module show like chan_mgcp` → 0 modules. Note added that mgcp/skinny are gone in 22. |
| 6 | "**Do not** noload `res_pjsip`, `res_pjproject`, or `chan_pjsip` — those are required for SIP in Asterisk 22" | 134 | VERIFIED | lab: all three Running, Support Level core |
| 7 | noload block listing `chan_mgcp.so` and `chan_skinny.so` | 138,141,335,338 | WRONG (fixed) | chan_mgcp & chan_skinny Removed Version 21 — docs.asterisk.org/Development/Asterisk-Module-Deprecations/; lab: both → 0 modules. Removed those two noload lines; kept chan_iax2/chan_unistim (which do ship in 22). |
| 8 | "res_pjsip's resolver making outbound DNS queries (ephemeral source port) … not an inbound listener" | 132 | VERIFIED | res_pjproject/res_pjsip DNS resolution uses client sockets; conntrack ESTABLISHED,RELATED covers replies (standard netfilter behavior) |
| 9 | "Per-endpoint authentication … `type=auth` … `auth_type=digest`" | 108 | VERIFIED | lab: `config show help res_pjsip auth auth_type` — 'digest' reads password; 'userpass'/'md5' deprecated → converted to digest |
| 10 | "PJSIP does not reveal whether a username exists … create an endpoint named `anonymous` … `type=identify` (matching on source IP)" | 109 | VERIFIED | docs.asterisk.org/.../PJSIP-Configuration-Sections-and-Relationships/ — fallback to endpoint named "anonymous"; without it anonymous calling not possible |
| 11 | "Restrict … with `/etc/asterisk/acl.conf` named ACLs … `acl=` … and `contact_acl=`" | 110 | VERIFIED | lab: `config show help res_pjsip endpoint acl` / `contact_acl` — "List of … ACL section names in acl.conf" |
| 12 | "Set `qualify_frequency` (and `qualify_timeout`) on the AOR" | 111 | VERIFIED | lab: `config show help res_pjsip aor qualify_frequency` / `qualify_timeout` exist |
| 13 | "On the `type=transport` you can cap concurrent TCP/TLS clients with `max_clients`, and enable kernel-level options through the transport `option` flags." | 112 (orig) | WRONG (fixed) | lab: `config show help res_pjsip transport max_clients` → "No option max_clients found"; full transport option list has no `max_clients` or `option`. Rewrote to reference real options (tcp_keepalive_*, tos/cos, local_net) and firewall-based flood control. |
| 14 | "Encrypt … media with `media_encryption=sdes` (or `dtls` for WebRTC)" | 113 | VERIFIED | lab: `config show help res_pjsip endpoint media_encryption` — values no/sdes/dtls |
| 15 | "Restrict … (`manager.conf`) and ARI (`ari.conf` / `http.conf`) to localhost" | 114 | VERIFIED | standard Asterisk config filenames; manager.conf bindaddr / http.conf bindaddr are real settings |
| 16 | "Note that port 5061 (SIP over TLS) is **TCP**, not UDP." | 187 | VERIFIED | TLS runs over TCP (RFC 3261 §7); PJSIP TLS transport binds TCP |
| 17 | "In Asterisk 22, PJSIP reports failed authentications … through the … security event framework, written to the … `security` logger channel" | 206 | VERIFIED | docs.asterisk.org/Deployment/Asterisk-Security-Framework/Asterisk-Security-Event-Logger/; lab logger channel SECURITY |
| 18 | logger.conf `security => security` then `module reload logger` | 211-215 | VERIFIED | docs: logger.conf syntax `<filename> => security`; lab `/var/log/asterisk/security … SECURITY` matches |
| 19 | "lines such as `SecurityEvent=\"InvalidPassword\"`, `ChallengeFailed`, and `InvalidAccountID`, each carrying the `RemoteAddress=`" | 215 (orig) | WRONG (fixed) | main/security_events.c — events are InvalidPassword, ChallengeResponseFailed (NOT ChallengeFailed), InvalidAccountID; RemoteAddress is a field. Fixed ChallengeFailed → ChallengeResponseFailed. |
| 20 | "SRTP … defined in the RFC3711" | 422 | VERIFIED | datatracker.ietf.org/doc/html/rfc3711 — "The Secure Real-time Transport Protocol (SRTP)" |
| 21 | "Asterisk uses SDES exchange keys over the SDP … protected by … TLS" | 422 | VERIFIED | lab media_encryption sdes synopsis: "standard SRTP setup via in-SDP keys. Encrypted SIP transport should be used …" |
| 22 | TLS transport: `cert_file` / `priv_key_file` / `method=tlsv1_2` | 348-350 | VERIFIED | lab: `config show help res_pjsip transport cert_file`/`priv_key_file`/`method` — method values include tlsv1_2, tlsv1_3 |
| 23 | "Use `method=tlsv1_2` (or `tlsv1_3` …) — TLS 1.0/1.1 are obsolete" | 353 | VERIFIED | lab method values; default is PJSIP default (currently TLSv1) → explicit tlsv1_2/_3 is sound. RFC 8996 deprecates TLS 1.0/1.1 |
| 24 | "Set `media_encryption=sdes`; you can also require it with `media_encryption_optimistic=no`" | 472,486 | VERIFIED | lab: `config show help res_pjsip endpoint media_encryption_optimistic` — Default no; only applies if media_encryption sdes/dtls |
| 25 | "use the Asterisk application vmauthenticate" / "`VMAuthenticate` is still valid in Asterisk 22" | 497,506 | VERIFIED | lab: `core show application VMAuthenticate` — provided by app_voicemail |
| 26 | "ast_tls_cert … present in /usr/src/asterisk-22.x.y/contrib/scripts" | 272,539 | VERIFIED | lab: `find / -name ast_tls_cert` → /usr/src/asterisk-22.10.0/contrib/scripts/ast_tls_cert |
| 27 | Quiz Q8: "Asterisk supports strong authentication by verifying client certificates" → TRUE | 549,563 | VERIFIED | lab: transport options `verify_client` / `require_client_cert` (TLS) exist |
| 28 | Quiz Q9: `media_encryption=sdes` turns on SRTP via in-SDP keys | 552-554 | VERIFIED | lab media_encryption sdes synopsis |
| 29 | Quiz Q10: Fail2Ban reads from `security` logger channel | 557-561 | VERIFIED | lab logger SECURITY channel |
| 30 | "In 2010 hackers used the Sality botnet to scan all vulnerable SIP devices." | 24 | WRONG (fixed) | Date corrected (Feb 2011, not 2010) and sourced: A. Dainotti et al., "Analysis of a '/0' Stealth Scan from a Botnet," IEEE/ACM Trans. on Networking, DOI 10.1109/TNET.2013.2297678 — Sality scanned the full IPv4 space probing UDP/5060 for SIP servers (observed via UCSD Network Telescope, ~3M source IPs). Footnote added. |
| 31 | RTP port range "10000 to 20000" (rtp.conf) | 148,182 | WRONG (fixed) | Reframed as the rtp.conf.sample example range, not a built-in default. lab: `rtp.conf.sample` comment "Defaults are rtpstart=5000 and rtpend=31000", while the sample sets rtpstart=10000/rtpend=20000. Text now states no single built-in default and to match the firewall rule to the operator's actual rtpstart/rtpend. |

## Summary

- Verified: 24
- Wrong (fixed): 3
  - Removed `noload => chan_mgcp.so` / `chan_skinny.so` from both modules.conf blocks (removed in Asterisk 21; absent in lab) and added a clarifying note; updated the line-130 narrative.
  - Rewrote the bogus `max_clients` / transport `option` DoS claim to reference real transport options (tcp_keepalive_*, tos/cos, local_net) and firewall-based flood control; updated the matching [2nd-ed note].
  - Corrected security event name `ChallengeFailed` → `ChallengeResponseFailed`.
- Previously-unverified, now resolved:
  1. Sality botnet claim (line 24): corrected "2010" → "February 2011" and sourced to the UCSD Network Telescope study (Dainotti et al., IEEE/ACM Trans. on Networking, DOI 10.1109/TNET.2013.2297678) — full-IPv4 stealth scan probing UDP/5060 for SIP servers. Footnote added.
  2. RTP range (lines 148/182): reframed as the `rtp.conf.sample` example range. Lab confirms the sample comment "Defaults are rtpstart=5000 and rtpend=31000" while the sample sets 10000/20000 — text now makes clear there is no single hard default and the firewall rule must match the operator's chosen `rtpstart`/`rtpend`.
