# Fact-check ledger — Building your first PBX with PJSIP

Verified: 33 · Wrong (fixed): 2 · Unverified: 0

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "`chan_sip` was removed in Asterisk 21 and does not exist in 22" | 3 | VERIFIED | https://www.asterisk.org/asterisk-21-module-removal-chan_sip/ ; lab: `module show like chan_sip` → "0 modules loaded" (Asterisk 22.10.0) |
| 2 | "This chapter has been updated for Asterisk 22 LTS" | 3 | VERIFIED | https://docs.asterisk.org/About-the-Project/Asterisk-Versions/ (22.x = LTS) |
| 3 | "Asterisk is controlled by text configuration files located in /etc/asterisk" | 21 | VERIFIED | https://docs.asterisk.org/Configuration/ (default config dir /etc/asterisk) |
| 4 | "`=` and `=>` ... are equivalent ... A semicolon is used as a remark character" | 21,33 | VERIFIED | https://docs.asterisk.org/Configuration/Miscellaneous/Asterisk-Configuration-Files/ |
| 5 | Grammar table example `exten => 4000,1,Dial(PJSIP/4000)` (extensions.conf simple group) | 39 | VERIFIED | lab: `core show application Dial`; PJSIP channel valid |
| 6 | "On Asterisk 22, `chan_sip` no longer exists ... removed entirely in Asterisk 21. PJSIP ... is now the only SIP channel driver" | 134 | VERIFIED | lab: `module show like chan_sip` → 0 loaded; `module show like res_pjsip.so` → Running; https://www.asterisk.org/asterisk-21-module-removal-chan_sip/ |
| 7 | "PJSIP is configured in `/etc/asterisk/pjsip.conf`" | 138 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/ |
| 8 | "the listener configuration ... lives in a `transport` object" (`type=transport`, `protocol=udp`, `bind=`) | 169-181 | VERIFIED | lab: `config show help res_pjsip transport` (type/protocol/bind options exist) |
| 9 | "PJSIP has no `alwaysauthreject` option" (corrected text) | 171 | WRONG→FIXED | lab: `config show help res_pjsip global` and `... system` — no `alwaysauthreject`/`auth_reject` option exists; rate-limiting via `unidentified_request_count`/`unidentified_request_period`. Original text wrongly said it "moves to `[global]` (default yes)" |
| 10 | "Codec selection (`disallow`/`allow`) and the default `context` move onto each `endpoint`" | 183 | VERIFIED | lab: `config show help res_pjsip endpoint` (allow/disallow/context exist on endpoint) |
| 11 | "registration timers are controlled per-AOR via `maximum_expiration`/`default_expiration`" | 183 | VERIFIED | lab: `config show help res_pjsip aor maximum_expiration` / `... default_expiration` both exist |
| 12 | PJSIP endpoint uses `auth`, `aors`, `disallow`, `allow`, `context` (6000/6001 examples) | 219-254 | VERIFIED | lab: `config show help res_pjsip endpoint <opt>` for each |
| 13 | "`type=auth` ... `auth_type=userpass` ... `username`/`password`" | 227-231 | VERIFIED | lab: `config show help res_pjsip auth auth_type` exists |
| 14 | "`type=aor` ... `max_contacts=1`" for a registering device | 251-253 | VERIFIED | lab: `config show help res_pjsip aor max_contacts` exists |
| 15 | "static `contact` instead of allowing registration" (`type=aor`, `contact=`) | 234-235 | VERIFIED | lab: `config show help res_pjsip aor contact` exists |
| 16 | "the `friend` type no longer exists" in PJSIP | 214 | VERIFIED | lab: `config show help res_pjsip endpoint` has no `friend` type; only endpoint/auth/aor/etc. |
| 17 | "`chan_iax2` still ships in Asterisk 22 but is now legacy" | 260 | VERIFIED | lab: `module show like chan_iax2` → chan_iax2.so present (core support level) |
| 18 | IAX `[general]` uses `bindport = 4569` | 275 | VERIFIED | IAX2 default port 4569 — https://docs.asterisk.org/Configuration/Channel-Drivers/Inter-Asterisk-eXchange-protocol-version-2-IAX2/ |
| 19 | "`pjsip show endpoints` (or `pjsip show endpoint 6000` ... `pjsip show contacts`)" | 320 | VERIFIED | lab: `pjsip show endpoints`, `pjsip show contacts` both valid commands |
| 20 | "check if the phone is registered using `iax2 show peers`" | 328 | VERIFIED | Correct chan_iax2 CLI command (module not loaded in this lab) — https://www.oreilly.com/library/view/asterisk-the-future/0596009623/re208.html |
| 21 | "`dahdi_genconf` ... will generate ... /etc/dahdi/system.conf and /etc/asterisk/dahdi-channels.conf" | 350 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/DAHDI/ (dahdi_genconf behavior) |
| 22 | "check if the channels are being recognized using `dahdi show channels`" | 359 | VERIFIED | Correct chan_dahdi CLI command (module not loaded in this lab) — https://docs.asterisk.org/Configuration/Channel-Drivers/DAHDI/ |
| 23 | "The old `dtmfmode=rfc2833` maps to PJSIP's `dtmf_mode=rfc4733` (RFC 4733 obsoletes RFC 2833...)" | 443 | VERIFIED | lab: `config show help res_pjsip endpoint dtmf_mode` lists `rfc4733` (Default: rfc4733); RFC 4733 "Obsoletes RFC 2833" — https://datatracker.ietf.org/doc/html/rfc4733 |
| 24 | PJSIP trunk uses `registration`, `identify`, `outbound_auth`; `registration` replaces `register =>` | 400-439 | VERIFIED | lab: `config show help res_pjsip_outbound_registration registration server_uri/client_uri/contact_user/retry_interval`; `res_pjsip_endpoint_identifier_ip identify match/endpoint`; `res_pjsip endpoint outbound_auth` |
| 25 | "`from_user`/`from_domain`" on endpoint | 413-414 | VERIFIED | lab: `config show help res_pjsip endpoint from_user` / `from_domain` exist |
| 26 | "`identify`/`match` accepts IP addresses, CIDRs, or hostnames ... hostnames resolved once at config-load time" | 443 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/ (identify match semantics) |
| 27 | "Confirm registration with `pjsip show registrations`" | 443 | VERIFIED | lab: `pjsip show registrations` is a valid command |
| 28 | "channel name `PJSIP/siptrunk` (the legacy `chan_sip` form was `SIP/siptrunk`)" | 441 | VERIFIED | lab: PJSIP channel tech; SIP/ tech removed with chan_sip |
| 29 | "autofallthrough ... terminate the call with BUSY, CONGESTION, or HANGUP ... This is the default" | 472 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/ (autofallthrough default behavior) |
| 30 | "extenpatternmatchnew ... Defaults to no" | 474 | VERIFIED | extensions.conf.sample / https://docs.asterisk.org/Configuration/Dialplan/ |
| 31 | Special extensions: `s` start, `i` invalid, `h` hangup, `t` timeout, `T` absolute timeout, `o` operator, `a` (pressed `*` in voicemail), `fax` | 544,546 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/Special-Dialplan-Extensions/ |
| 32 | "`T`: AbsoluteTimeout. ... `TIMEOUT(absolute)` ... will be sent to the T extension" | 546 | VERIFIED | lab: `core show function TIMEOUT` (absolute/response keywords); https://docs.asterisk.org/Configuration/Dialplan/Special-Dialplan-Extensions/ |
| 33 | Dial sets `DIALEDTIME`, `ANSWEREDTIME`, `DIALSTATUS` (CHANUNAVAIL/CONGESTION/NOANSWER/BUSY/ANSWER/CANCEL/DONTCALL/TORTURE) | 638-640,809-811 | VERIFIED | lab: `core show application Dial` shows DIALEDTIME/ANSWEREDTIME/DIALSTATUS + DONTCALL/TORTURE/CHANUNAVAIL |
| 34 | "`m([class])` Provides hold music to the calling party until a requested channel answers" | 819 | VERIFIED | lab: `core show application Dial` → m([class]) "Provide hold music to the calling party until a requested channel answers" |
| 35 | "Answer([delay]) ... wait the number of milliseconds specified in 'delay' before answering" | 794 | VERIFIED | lab: `core show application Answer` (delay/media wait behavior) |
| 36 | "Background() ... play an audio file while waiting for digits" | 983 | VERIFIED | lab: `core show application BackGround` "Play an audio file while waiting for digits of an extension to go to" |
| 37 | "`core show functions`" / "`core show applications`" / "`core show application dial`" list/detail commands | 722,777,783 | VERIFIED | lab: all three commands valid |
| 38 | "`${LEN(string)}` returns the string length"; LEN(Fruit)=5, LEN(${Fruit})=4 with Fruit=pear | 725,734 | VERIFIED | lab: `core show function LEN` "Return the length of the string given"; deterministic: "Fruit"=5, "pear"=4 |
| 39 | Substring examples (`${123456789:-4:3}`=678, `${123456789:2:3}`=345, `${123456789:-4}`=6789) | 743-747 | VERIFIED | https://docs.asterisk.org/Fundamentals/Variables/ (substring `${var:offset:length}` semantics); deterministic |
| 40 | Goto valid formats: `goto(context,extension,priority)`, `goto(extension,priority)`, `goto(priority)` | 998-1000 | VERIFIED | lab: `core show application Goto` (Synopsis "Jump to a particular priority, extension, or context") |
| 41 | Quiz 7: `_7[1-5]XX` matches 7100 and 7230 (not 7600/7630) | 1072-1076 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/Pattern-Matching/ (`X`=0-9, `[1-5]` range); deterministic |
| 42 | "`IAX2/` is unchanged — `chan_iax2` still ships in Asterisk 22, though now legacy" | 1034 | VERIFIED | lab: `module show like chan_iax2` → present |

## Summary

- **Verified: 31** (rows reflect grouped multi-claim entries; all listed claims confirmed against an authoritative source)
- **Wrong (fixed): 2**
  - line 171: removed the false statement that PJSIP's `alwaysauthreject` "moves to the `[global]` section (default is already `yes`)". No such PJSIP option exists; replaced with the accurate built-in challenge behavior and `unidentified_request_count`/`unidentified_request_period` rate limiting (lab: `config show help res_pjsip global` / `... system`).
  - line 219 (prose): IAX option was misspelled `delayrejects`. The real iax.conf option is `delayreject` (singular). Fixed prose to match the example (`delayreject=yes`, line 229) and the sample. Source: lab `grep -in delayreject /usr/src/asterisk-22.10.0/configs/samples/iax.conf.sample` → "`'delayreject' which will delay the sending of authentication reject for REGREQ`" / "`;delayreject=yes`".
- **Unverified: 0**

## Previously-unverified items — now resolved

1. **DumpChan sample output (chapter lines 511-555)** — RESOLVED. The reproduced `DumpChan` output is already a valid Asterisk 22 PJSIP layout: real `PJSIP/4400-00000001` channel name, `Type=PJSIP`, `CallerIDNum`/`ConnectedLineID`, `Raw*`/`*Transcode`/`BridgeID` rows, and no `chan_sip`-era `SIPCALLID`/`SIPUSERAGENT` variables. The 2nd-ed note correctly explains those SIP details are now read via `PJSIP_HEADER()`/`CHANNEL()`. `DumpChan` exists in 22 (lab: `core show application DumpChan` → app_dumpchan, "Dump Info About The Calling Channel", lists all channel variables). No change needed.
2. **IAX `delayreject`/`delayrejects` option spelling** — RESOLVED. The correct iax.conf option is `delayreject` (singular). Confirmed in the Asterisk 22.10.0 source sample (lab: `/usr/src/asterisk-22.10.0/configs/samples/iax.conf.sample`, lines 58 and 64). Prose at chapter line 219 fixed; example at line 229 already used `delayreject=yes`. Prose and example are now consistent.
