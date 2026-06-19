# Fact-check ledger — Designing a VoIP network (Chapter 6)

Verified: 25 · Wrong (fixed): 4 · Unverified: 0

Lab = Asterisk 22.10.0 running in `/Users/flavio/crosscall/astbook/lab` (docker compose exec asterisk).

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "SIP is an Internet Engineering Task Force (IETF) open standard, largely defined in RFC 3261" | 57 | VERIFIED | RFC 3261 (SIP), IETF Standards Track, June 2002 — https://datatracker.ietf.org/doc/html/rfc3261 |
| 2 | "SIP uses UDP or TCP in port 5060 to transport signaling" | 49 | VERIFIED | RFC 3261 §19.1.1 / IANA: SIP default port 5060 (UDP/TCP) — https://datatracker.ietf.org/doc/html/rfc3261 |
| 3 | "RTP transports the audio stream using ports 1000 to 2000 in Asterisk (as defined in rtp.conf)" | 49 | WRONG (fixed) | Asterisk sample `rtp.conf` uses rtpstart=10000/rtpend=20000 (documented internal defaults 5000–31000); 1000–2000 is incorrect. Fixed to "10000 to 20000". Source: https://github.com/asterisk/asterisk/blob/master/configs/samples/rtp.conf.sample ; lab `rtp show settings` (lab override 10000–10100) |
| 4 | "H.323 uses TCP in ports 1720 and 1719 to transport signaling" | 49 | WRONG (fixed) | Rewrote the section: H.225 call signaling on TCP 1720; H.225 RAS on UDP 1719. https://www.cisco.com/c/en/us/support/docs/voice/h323/5244-understand-gatekeepers.html |
| 5 | "IAX ... transports signaling and media through the same UDP port (4569)" | 61 | VERIFIED | RFC 5456 §3: IAX uses well-known UDP port 4569 for all traffic — https://datatracker.ietf.org/doc/html/rfc5456 |
| 6 | "IAX is an open protocol originally developed by Digium (now Sangoma)" | 61 | VERIFIED | RFC 5456 (IAX/Inter-Asterisk eXchange v2), Digium authors; Digium acquired by Sangoma 2018 — https://datatracker.ietf.org/doc/html/rfc5456 |
| 7 | "IAX2 (version 2) still ships in Asterisk 22 via the `chan_iax2` module" | 61, 80 | VERIFIED | lab: `module show like chan_iax2` → `chan_iax2.so ... core` (1 module loaded) |
| 8 | "IAX2 | IETF draft" (comparison table standard body) | 80 | WRONG (fixed) | Changed the table cell to "RFC 5456 (Informational)". https://datatracker.ietf.org/doc/html/rfc5456 |
| 9 | "chan_sip was removed in Asterisk 21" | 85 | VERIFIED | lab: `module show like chan_sip` → 0 modules loaded (absent in 22); removal in 21 — https://docs.asterisk.org/Deployment/Module-Loading-and-Configuration/Configuring-chan_pjsip/ and Asterisk 21 release notes |
| 10 | "In Asterisk 22, SIP is handled exclusively by `chan_pjsip`" / "only SIP channel driver in Asterisk 22" | 85, 251 | VERIFIED | lab: `module show like chan_pjsip` → `chan_pjsip.so ... Running ... core`; chan_sip absent |
| 11 | "H.323 ... available only through the community `ooh323` add-on" / "chan_ooh323 add-on" | 39, 251 | VERIFIED | lab: `module show like ooh323` → 0 modules (not in standard build); chan_ooh323 is the addons/community H.323 module |
| 12 | "MGCP ... no longer part of a standard Asterisk 22 build" (chan_mgcp) | 251 | VERIFIED | lab: `module show like chan_mgcp` → 0 modules loaded |
| 13 | "SCCP (Skinny) channels are no longer part of a standard Asterisk 22 build" (chan_skinny) | 251 | VERIFIED | lab: `module show like chan_skinny` → 0 modules loaded |
| 14 | "GSM: 13 Kbps" | 103 | VERIFIED | GSM 06.10 full-rate ~13 kbps — https://www.techtarget.com/searchunifiedcommunications/tip/VoIP-codecs-explained-How-to-optimize-VoIP-quality ; lab `core show codecs audio` lists gsm |
| 15 | "iLBC: 13.3 Kbps" | 104 | VERIFIED | iLBC = 13.33 kbps (30 ms frames) — https://en.wikipedia.org/wiki/Internet_Low_Bitrate_Codec |
| 16 | "ITU G.711 (ulaw/alaw): 64 Kbps" | 105 | VERIFIED | G.711 = 64 kbps — https://www.techtarget.com/searchunifiedcommunications/tip/VoIP-codecs-explained-How-to-optimize-VoIP-quality ; lab codecs list ulaw/alaw |
| 17 | "ITU G.722: 64 Kbps — wideband" | 106 | VERIFIED | G.722 ITU-T wideband, up to 64 kbit/s — https://en.wikipedia.org/wiki/G.722 ; lab codecs list g722 |
| 18 | "ITU G.723.1: 5.3/6.3 Kbps" | 107 | VERIFIED | G.723.1 dual-rate 5.3 & 6.3 kbps (ITU-T) — https://www.techtarget.com/searchunifiedcommunications/tip/VoIP-codecs-explained-How-to-optimize-VoIP-quality |
| 19 | "ITU G.726: 16/24/32/40 Kbps" | 108 | VERIFIED | G.726 ADPCM modes 16/24/32/40 kbps — https://en.wikipedia.org/wiki/G.726 |
| 20 | "ITU G.729: 8 Kbps" | 109, 208 | VERIFIED | G.729 = 8 kbps — https://www.techtarget.com/searchunifiedcommunications/tip/VoIP-codecs-explained-How-to-optimize-VoIP-quality ; lab codecs list g729 (G.729A) |
| 21 | "Speex: 2.15 to 44.2 Kbps" | 110 | VERIFIED | Speex range 2.15–44 kbps — https://speex.org/docs/manual/speex-manual/node4.html ; lab codecs list speex |
| 22 | "LPC10: 2.5 Kbps" | 111 | WRONG (fixed) | LPC-10 / FS-1015 = 2.4 kbps. Fixed "2.5" → "2.4". Source: FS-1015/LPC-10 STANAG 4198, 2.4 kbps — https://en.wikipedia.org/wiki/FS-1015 |
| 23 | "Opus: 6–510 Kbps, variable" | 112 | VERIFIED | Opus 6–510 kbit/s, RFC 6716 (IETF) — https://en.wikipedia.org/wiki/Opus_(audio_format) ; lab codecs list opus |
| 24 | "g723 ... supported only in pass-thru mode" | 114 | VERIFIED | lab: `core show translation` — g723 has no translation paths (absent from translate matrix); pass-through only |
| 25 | "RTP header compression was defined in RFC 2508" | 225 | VERIFIED | RFC 2508 = Compressing IP/UDP/RTP Headers (CRTP), IETF — https://datatracker.ietf.org/doc/html/rfc2508 |
| 26 | "a g.729 conversation consumes 31.2 Kbps" (Ethernet, 20-byte payload + 58B headers) | 142, 150 | VERIFIED | Standard reference figure: G.729 on Ethernet ≈ 31.2 kbps at 20 ms ptime — https://www.cisco.com/c/en/us/support/docs/voice/voice-quality/7934-bwidth-consume.html |
| 27 | "SIP | IETF standard" / "H.323 | ITU standard" (table standard bodies) | 79–81 | VERIFIED | SIP = IETF (RFC 3261); H.323 = ITU-T recommendation — https://datatracker.ietf.org/doc/html/rfc3261 ; ITU-T H.323 |
| 28 | "lawful G.729 use ... requires a purchased per-channel license" | 97, 109, 134 | VERIFIED | Sangoma G.729 license keys are per-channel, per-server activations — https://help.sangoma.com/s/article/How-to-determine-which-G729-codec-binary-I-should-use-in-my-asterisk-system (Sangoma G.729 Codec Policy) |
| 29 | "Sangoma distributes a `codec_g729` binary module ... free of charge" / `codec_opus` free binary module | 126, 138, 141 | VERIFIED (reworded) | Asterisk `menuselect` source `codecs/codecs.xml` (the lab's own build source) lists both as `<support_level>external</support_level>` downloadable binaries: codec_opus displayname = "Download the Opus codec from Digium. See https://downloads.digium.com/pub/telephony/codec_opus/README."; codec_g729a displayname = "Download the g729a codec from Digium. **A license must be purchased for this codec.** See https://downloads.digium.com/pub/telephony/codec_g729/README." Lab confirms neither ships in the standard build (`module show like codec` lists only core codecs, no g729/opus). The unsourced "free of charge" wording was removed; G.729 now states "a license must be purchased" (per codecs.xml), and Opus states "no license purchase noted, unlike G.729." Source: https://github.com/asterisk/asterisk/blob/master/codecs/codecs.xml ; lab `module show like codec` |

## Fixes applied (3)

- **Line 49** — "ports 1000 to 2000 in Asterisk (as defined in rtp.conf)" → "a configurable UDP port range in Asterisk (the shipped `rtp.conf` sample uses 10000 to 20000)". Asterisk's sample `rtp.conf` ships 10000–20000; 1000–2000 is wrong.
- **Line 111** — LPC10 "2.5 Kbps" → "2.4 Kbps". FS-1015/LPC-10 standard rate is 2.4 kbps.
- **Lines 126/138/141** — Removed the unsourced "free of charge / free download" wording for the `codec_g729` and `codec_opus` add-ons. Both are now described accurately as external (`support_level=external`) binary modules downloaded from Digium/Sangoma, per Asterisk's `codecs/codecs.xml`. G.729 wording now matches the codecs.xml note "A license must be purchased for this codec"; Opus wording notes no purchase requirement is stated (unlike G.729) rather than asserting it is "free." Source: https://github.com/asterisk/asterisk/blob/master/codecs/codecs.xml ; lab `module show like codec`.

## Unverified items for the author to resolve before print (0)

_None remaining — both items resolved: H.323 ports corrected in the rewritten network-stack section (TCP 1720 / UDP 1719), and the IAX2 comparison-table cell now reads "RFC 5456 (Informational)."_
