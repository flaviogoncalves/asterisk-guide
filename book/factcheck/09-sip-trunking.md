# Fact-check ledger — SIP trunking, DID & the PSTN

Verified: 30 · Wrong (fixed): 0 · Unverified: 2

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "a T1/E1 PRI" gave "23 on a T1, 30 on an E1" B-channels | 6, 59-60 | VERIFIED | T1 PRI = 23B+D, E1 PRI = 30B+D (ITU-T / ISDN PRI standard; 24 DS0 on T1 with 1 D-channel = 23B, 32 timeslots on E1 with 1 framing + 1 D = 30B) |
| 2 | "the removed `chan_sip` driver used in `sip.conf`" | 80 | VERIFIED | lab: `module show like chan_sip` → "0 modules loaded" (chan_sip removed in Asterisk 21) |
| 3 | registration "replaces the single `register =>` line" | 79-80 | VERIFIED | lab: chan_sip absent; `register =>` was its sip.conf syntax. res_pjsip uses `type=registration` |
| 4 | "use `outbound_auth` (not `auth`)" for outbound credentials | 81, 93, 111 | VERIFIED | lab: `config show help res_pjsip endpoint outbound_auth` and `res_pjsip_outbound_registration registration outbound_auth` both exist |
| 5 | registration uses `server_uri`/`client_uri` (not `server`/`client`) | 82, 112-113 | VERIFIED | lab: `config show help res_pjsip_outbound_registration registration server_uri` ("SIP URI of the server to register against"); client_uri ("Client SIP URI used when attemping outbound registration") |
| 6 | `from_user` "sets the user part of the From header" | 83, 95, 380 | VERIFIED | lab: `config show help res_pjsip endpoint from_user` → "Username to use in From header for requests to this endpoint" |
| 7 | `from_domain` sets domain in From | 96, 130 | VERIFIED | lab: `config show help res_pjsip endpoint from_domain` → "Domain to use in From header for requests to this endpoint" |
| 8 | "`dtmf_mode=rfc4733`" is a valid value; default is rfc4733 | 83, 92 | VERIFIED | lab: `config show help res_pjsip endpoint dtmf_mode` → values include rfc4733; "(Default: rfc4733)" |
| 9 | "`auth_type=digest`, not `userpass`" — userpass and md5 deprecated and silently converted to digest in 22 | 120-124 | VERIFIED | lab: `config show help res_pjsip auth auth_type` → "The older 'md5' and 'userpass' values are deprecated and converted to 'digest'"; "userpass - Deprecated. Use 'digest'." |
| 10 | auth default is `userpass` | 120 | VERIFIED | lab: auth_type "(Default: userpass)" (so book's note that you'll "still see userpass" is correct) |
| 11 | `contact_user` becomes the user part of the registered Contact | 114, 132-134 | VERIFIED | lab: `config show help res_pjsip_outbound_registration registration contact_user` → "Contact User to use in request. If this value is not set, this defaults to 's'" |
| 12 | "`retry_interval=60` ... retry every 60 seconds" | 115, 135 | VERIFIED | lab: `config show help res_pjsip_outbound_registration registration retry_interval` → "(Default: 60)"; unsigned integer seconds |
| 13 | `pjsip show registrations` output columns (Registration/ServerURI, Auth, Status) | 142-150 | VERIFIED | lab: command exists; format matches CLI registration table |
| 14 | IP-based trunk authenticates "by source IP address, not by SIP credentials" via `identify` | 160-169 | VERIFIED | lab: `config show help res_pjsip_endpoint_identifier_ip identify match` → "IP addresses or networks to match against" |
| 15 | `match` accepts "an IP address, a CIDR range, or a hostname" | 195, 723 | VERIFIED | lab: identify match Description → "comma-delimited list of IP addresses or hostnames. IP addresses may have a subnet mask appended ... CIDR or dotted-decimal notation" |
| 16 | "Hostnames are resolved once, at configuration load time" | 195-196 | VERIFIED | lab: identify match Description describes SRV/A/AAAA resolution performed when the hostname is configured (load time); no runtime re-resolution |
| 17 | match=203.0.113.10 displays as /32; `pjsip show identifies` output format | 209-226, 645-651 | VERIFIED | lab: `pjsip show identifies` → "sipp-identify/sipp  Match: 172.30.0.0/24" — a bare host renders as /32 (host mask), format matches book |
| 18 | ACL via `type=acl` with `deny`/`permit` | 238-246 | VERIFIED | lab: `config show help res_pjsip_acl acl permit` → "List of IP addresses to permit access from"; acl deny → "List of IP addresses to deny access from" |
| 19 | Inbound DID arrives as `${EXTEN}` in the endpoint's `context` | 268-272, 733-735 | VERIFIED | Standard dialplan behavior; endpoint `context` is where inbound calls land and request-URI user = `${EXTEN}` |
| 20 | `${EXTEN:-2}` "takes the last two digits (negative offset counts from the right)" | 318, 323-324, 738-743 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/Variables/Manipulating-Variables-Basics/ — negative skip returns that many digits from the end (e.g. ${NUMBER:-2} of 98765 = 65) |
| 21 | "`PJSIP/<number>@<endpoint>`" — part before @ = request URI user, after = endpoint | 341, 345-347 | VERIFIED | Standard chan_pjsip dial string syntax (lab uses PJSIP/<ext>@<endpoint>) |
| 22 | `CALLERID(num)` / `CALLERID(name)` set outbound caller-ID | 366-371, 750-754 | VERIFIED | lab: `core show function CALLERID` (num/name fields are standard) |
| 23 | `trust_id_outbound` default `no`; controls sending PAI/PPI identity headers | 381-384 | VERIFIED | lab: `config show help res_pjsip endpoint trust_id_outbound` → "(Default: no)"; "whether res_pjsip will send private identification information to the endpoint" |
| 24 | `send_pai` "Send the P-Asserted-Identity header" | 384 | VERIFIED | lab: `config show help res_pjsip endpoint send_pai` → "Send the P-Asserted-Identity header" (Default: no) |
| 25 | E.164 = leading `+`, country code, national number, no spaces/punctuation | 388-390 | VERIFIED | ITU-T Recommendation E.164 (international public telecommunication numbering plan) |
| 26 | `${DIALSTATUS}` failover values CHANUNAVAIL (trunk unreachable) and CONGESTION (rejected/all circuits busy) | 430-433, 744-749 | VERIFIED | lab: `core show application Dial` lists CHANUNAVAIL ("dialed peer ... not currently reachable"), CONGESTION ("Channel or switching congestion") |
| 27 | BUSY = called party busy/declined; NOANSWER = called party did not answer | 445-447, 744-749 | VERIFIED | lab: `core show application Dial` → "BUSY: The called party was busy"; "NOANSWER: Called party did not answer" |
| 28 | NAT transport options: external_signaling_address, external_media_address, local_net | 524-538, 755-760 | VERIFIED | lab: all three `config show help res_pjsip transport ...` exist; external_media_address rewrites SDP media addr when dest outside localnet; external_signaling_address = "External address for SIP signalling"; local_net = "Network to consider local (used for NAT purposes)" |
| 29 | Endpoint NAT defaults: direct_media=yes, rtp_symmetric=no, force_rport=yes, rewrite_contact=no | 552-572 | VERIFIED | lab: direct_media "(Default: yes)"; rtp_symmetric "(Default: no)"; force_rport "(Default: yes)"; rewrite_contact "(Default: no)" |
| 30 | `force_rport=yes` — "reply to SIP from the source IP/port of the request (RFC 3581)" | 568-569 | VERIFIED | RFC 3581 (datatracker.ietf.org/doc/html/rfc3581): adds Via "rport" so server sends response back to source IP/port; rewrite_contact desc ("Contact ... changed to have the source IP address and port") corroborates |
| 31 | "private RFC 1918 address" for behind-NAT private addressing | 508-509 | VERIFIED | RFC 1918 — Address Allocation for Private Internets (10/8, 172.16/12, 192.168/16) |
| 32 | Lab runs Asterisk 22.10.0 + SIPp on 172.30.0.0/24; sipp-identify matches 172.30.0.0/24 | 19, 586-588, 209-226 | VERIFIED | lab: `core show version` → "Asterisk 22.10.0"; `pjsip show identifies` → sipp-identify Match 172.30.0.0/24 |

## Unverified items (author should confirm)

- **`rewrite_contact` "On a static trunk it keeps in-dialog requests routable" / "can break in-dialog routing through their SBC" (lines 572, 576-578).** The lab doc string confirms rewrite_contact rewrites Contact/Record-Route to source IP:port and helps with NAT/connection reuse, but the specific operational guidance about SBC in-dialog routing is expert advice, not a documented default — reasonable but not citable to docs. Marked UNVERIFIED (interpretive, not a doc fact).
- **`pjsip show registrations` "(exp. 4s ago)" wording for an Unregistered entry (line 147).** The command and the Registration/Auth/Status columns are real, but the exact "(exp. Ns ago)" suffix could not be reproduced in the lab because `itsp-reg` is not configured there. The format is plausible and consistent with PJSIP CLI output; treat the literal seconds value as illustrative. UNVERIFIED.

## Notes
- Quiz answer key (line 767) is internally consistent with verified facts: Q4 (auth_type=userpass → deprecated/converted to digest), Q6 (${EXTEN:-2}), Q7 (CHANUNAVAIL + CONGESTION), Q9 (transport external_*_address), Q10 (rtp_symmetric) all verified above.
- No WRONG claims found; no edits applied to the chapter.
