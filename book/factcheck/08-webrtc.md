# Fact-check ledger — WebRTC with Asterisk

Verified: 19 · Wrong (fixed): 1 · Resolved (was unverified): 2 · Unverified: 0

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "Since Asterisk 11 the PJSIP stack has been able to act as a WebRTC server" | 5 | WRONG (fixed) | WebRTC support was added in Asterisk 11, but the PJSIP stack (`res_pjsip`/`chan_pjsip`) was introduced in Asterisk **12**, not 11. https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/ ("the new SIP resources and channel driver included with Asterisk 12"). Fixed text to separate the two facts. |
| 2 | "a single endpoint option, `webrtc=yes`, turns all of this on with sensible defaults" | 61-62 | VERIFIED | https://docs.asterisk.org/Configuration/WebRTC/Configuring-Asterisk-for-WebRTC-Clients/ — webrtc=yes is shorthand for use_avpf, media_encryption=dtls, dtls_verify=fingerprint, dtls_setup=actpass, ice_support, media_use_received_transport, rtcp_mux |
| 3 | "WebRTC signaling is served by Asterisk's built-in HTTP server (`res_http_websocket` exposes the `/ws` path)" | 66-67 | VERIFIED | lab: `module show like res_http_websocket` → res_http_websocket.so Running core; `http show status` → "/ws => Asterisk HTTP WebSocket" |
| 4 | http.conf: enabled=yes, bindport=8088, tlsenable=yes, tlsbindaddr=0.0.0.0:8089 | 71-80 | VERIFIED | lab file lab/asterisk/etc/http.conf matches; `http show status` shows HTTP bound 0.0.0.0:8088, HTTPS bound 0.0.0.0:8089 |
| 5 | "HTTPS Server Enabled and Bound to 0.0.0.0:8089 ... /ws => Asterisk HTTP WebSocket" | 91-94 | VERIFIED | lab: `http show status` (output also lists `/media/...` which the book omits — abbreviation, not an error) |
| 6 | "The browser will connect to `wss://your-asterisk:8089/ws`" | 97 | VERIFIED | docs WebRTC page uses `https://pbx.example.com:8089/ws`; lab HTTPS bound to 8089 with /ws enabled |
| 7 | "PJSIP needs a transport of type `wss`" / protocol=wss | 115-122 | VERIFIED | lab: `pjsip show transports` → transport-wss wss; lab/asterisk/etc/pjsip.conf has protocol=wss |
| 8 | "pjsip show transports ... transport-wss wss ... 0.0.0.0:5060" | 127-130 | VERIFIED | lab: `pjsip show transports` → "transport-wss  wss  0  0  0.0.0.0:5060" (exact match, incl. the cosmetic 5060) |
| 9 | webrtc-1000 endpoint config: webrtc=yes, transport=transport-wss, allow=opus,ulaw | 143-162 | VERIFIED | lab/asterisk/etc/pjsip.conf; `pjsip show endpoint webrtc-1000` confirms webrtc=yes |
| 10 | "dtls_auto_generate_cert: Yes" | 169 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → dtls_auto_generate_cert : Yes |
| 11 | "dtls_fingerprint: SHA-256" | 170 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → dtls_fingerprint : SHA-256 |
| 12 | "dtls_setup: actpass" | 171 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → dtls_setup : actpass |
| 13 | "ice_support: true" | 172 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → ice_support : true |
| 14 | "media_encryption: dtls" | 173 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → media_encryption : dtls |
| 15 | "rtcp_mux: true" | 174 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → rtcp_mux : true |
| 16 | "use_avpf: true ... the AVPF RTP profile (feedback), required by WebRTC" | 175,186 | VERIFIED | lab: `pjsip show endpoint webrtc-1000` → use_avpf : true; docs WebRTC page: "the AVPF profile" |
| 17 | "`codec_opus` ships freely with Asterisk 22" | 189 | RESOLVED (rewritten) | Inaccurate as written. Lab: `module show like opus` → only `res_format_attr_opus.so` (Opus Format Attribute Module, **core**) is loaded; `codec_opus.so` (transcoder) is NOT present. Official WebRTC guide lists `codec_opus` as a prerequisite module you install separately ("codec_opus (optional but highly recommended)"; "presuming that you installed the Opus codec for Asterisk"): https://docs.asterisk.org/Configuration/WebRTC/Configuring-Asterisk-for-WebRTC-Clients/ . Rewrote to distinguish bundled Opus **passthrough** (res_format_attr_opus, core) from the separately-installed `codec_opus` **transcoder**; removed the "ships freely" framing. |
| 18 | "rtp.conf: icesupport=yes, stunaddr=stun.l.google.com:19302, turnaddr/turnusername/turnpassword" | 200-207 | VERIFIED | https://docs.asterisk.org/Configuration/Miscellaneous/Interactive-Connectivity-Establishment-ICE-in-Asterisk/ — uses exactly `stunaddr=stun.l.google.com:19302` and the turnaddr/turnusername/turnpassword options |
| 19 | "the two most common are SIP.js and JsSIP" | 218 | RESOLVED (reworded) | No authoritative/primary source quantifies "most common". Reworded to a neutral, defensible statement: "two widely used ones are SIP.js and JsSIP" — removes the unsourced popularity ranking while keeping both libraries (both are real, actively maintained WebRTC SIP libraries). |
| 20 | "getUserMedia (microphone access) only works on https:// pages or http://localhost" | 238-239 | VERIFIED | https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia — getUserMedia available only in secure contexts (HTTPS or localhost) |
| 21 | "Media is always encrypted with DTLS-SRTP. Browsers refuse plain RTP ... keys derived from DTLS handshake" | 53-55 | VERIFIED | WebRTC mandates DTLS-SRTP (RFC 8827 / W3C); corroborated by docs WebRTC page "the DTLS method of media encryption" |
| 22 | "ICE ... gather candidate addresses (host, STUN-reflexive, TURN-relayed)" | 56-58 | VERIFIED | https://docs.asterisk.org/Configuration/Miscellaneous/Interactive-Connectivity-Establishment-ICE-in-Asterisk/ — STUN for reflexive, TURN for relay candidates |

## Summary

- **Verified:** 19
- **Wrong (fixed):** 1
- **Resolved (was unverified):** 2
- **Unverified:** 0

### Wrong (fixed)
1. Line 5 — "Since Asterisk 11 the PJSIP stack has been able to act as a WebRTC server." The PJSIP stack (`res_pjsip`) arrived in Asterisk **12**; only generic WebRTC support dates to Asterisk 11. Text rewritten to separate the two facts.

### Resolved (previously unverified)
1. Line 189 — "`codec_opus` ships freely with Asterisk 22." **Rewritten.** Asterisk 22 bundles Opus *passthrough* in core (`res_format_attr_opus`, confirmed loaded via `module show like opus` in the lab; the lab does NOT load the `codec_opus` transcoder). The official WebRTC guide treats `codec_opus` as a separately-installed optional module ("optional but highly recommended"; "presuming that you installed the Opus codec for Asterisk"): https://docs.asterisk.org/Configuration/WebRTC/Configuring-Asterisk-for-WebRTC-Clients/ . New text distinguishes passthrough (bundled) from the transcoder (installed on top) and drops the "ships freely" framing.
2. Line 218 — "the two most common [WebRTC SIP libraries] are SIP.js and JsSIP." **Reworded** to "two widely used ones are SIP.js and JsSIP." No authoritative source quantifies "most common"; the popularity ranking was removed while keeping both (real, actively maintained) libraries.
