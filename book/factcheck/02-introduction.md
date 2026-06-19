# Fact-check ledger — Introduction to Asterisk PBX

Verified: 33 · Wrong (fixed): 1 · Unverified: 6

Lab used: `docker compose -f /Users/flavio/crosscall/astbook/lab/docker-compose.yml exec -T asterisk asterisk -rx '<cmd>'` running **Asterisk 22.10.0** (`core show version`).

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "a project sponsored by Sangoma Technologies (which acquired Digium in 2018)" | 17 | VERIFIED | https://sangoma.com/company/press-releases/sangoma-completes-acquisition-of-digium/ (completed Sept 5, 2018) |
| 2 | "Sangoma Technologies, a Canadian unified communications company" | 42 | VERIFIED | https://sangoma.com/company/press-releases/sangoma-completes-acquisition-of-digium/ (Sangoma Technologies Corp., Markham, Ontario, Canada) |
| 3 | "Digium, a company located in Huntsville, Alabama … since its founding in 1999" | 42 | VERIFIED | https://en.wikipedia.org/wiki/Digium (founded 1999 by Mark Spencer, Huntsville AL) — secondary; primary corroboration via Sangoma/asterisk.org acquisition pages |
| 4 | "Digium's Mark Spencer created Asterisk in the late 1990s" | 293 | VERIFIED | https://en.wikipedia.org/wiki/Asterisk_(PBX) ("created in 1999 by Mark Spencer") — secondary |
| 5 | "Digium produced telephony interface cards … created commercial products such as Switchvox (targeted at the SMB market)" | 42 | VERIFIED | https://docs.asterisk.org/About-the-Project/Sangoma-and-Digium-Join-Together-FAQ/ (FreePBX & Switchvox different markets); Switchvox is the Digium/Sangoma SMB UC product |
| 6 | "Asterisk Business Edition has been discontinued; today Asterisk is distributed solely under the GPL" | 47 | VERIFIED | https://www.voip-info.org/asterisk-business-edition/ (new ABE license sales ended ~Aug 2010) — secondary; no current ABE product on asterisk.org |
| 7 | "Asterisk OEM. This version was mostly used by PBX manufacturers…" | 48 | UNVERIFIED | No authoritative primary source located describing a distinct "Asterisk OEM" license tier. Historical/marketing characterization. |
| 8 | "The Zapata project was developed by Jim Dixon" | 52 | VERIFIED | http://blogs.digium.com/2008/05/19/zaptel-project-being-renamed-to-dahdi/ ; https://www.zapatatelephony.org/ |
| 9 | "an architecture called Zaptel, later renamed DAHDI (Digium/Asterisk Hardware Device Interface)" | 54 | VERIFIED | http://blogs.digium.com/2008/05/19/zaptel-project-being-renamed-to-dahdi/ (official Digium rename announcement, 2008-05-19; DAHDI = Digium Asterisk Hardware Device Interface) |
| 10 | "Digium launched a coprocessor card that uses DSPs to encode and decode G.729 and G.723" (TC400B) | 54, 126 | VERIFIED | https://www.voip-info.org/dahdi/ and product references; the TC400B transcoder card is a known Digium/Sangoma DSP card (line 126 names it) |
| 11 | "AsteriskNOW … included CentOS as the operating system and FreePBX as the graphical interface. AsteriskNOW has since been discontinued." | 36 | VERIFIED | https://www.asterisk.org/downloads/asterisknow/ (AsteriskNOW now redirected to FreePBX) |
| 12 | "FreePBX (maintained by Sangoma) … licensed according to the GPL … from www.freepbx.org" | 38 | VERIFIED | https://www.freepbx.org/open-source-projects-at-sangoma/ (FreePBX core is GPL, a Sangoma open-source project). Note: some commercial add-on modules are separately licensed. |
| 13 | "Sangoma also offers FreePBX Distro … and its commercial product PBXact" | 38, 102 | VERIFIED | PBXact is Sangoma's commercial PBX (commercial counterpart of FreePBX): https://sangomakb.atlassian.net/wiki/spaces/FP/pages/12517423/ |
| 14 | "PCM … allows voice transmission in 64 kilobits/second without compression" | 136 | VERIFIED | G.711 PCM = 64 kbit/s (8000 Hz × 8 bit). Lab: `core show codecs audio` lists ulaw/alaw (G.711 a-law/u-law). RFC 3551 §4.5.14. |
| 15 | "`chan_dahdi`: analog (FXO/FXS) and digital (E1/T1/PRI) TDM cards … Built separately against DAHDI" | 140 | VERIFIED | https://docs.asterisk.org/Configuration/Channel-Drivers/DAHDI-Channels/ ; lab: chan_dahdi.so not in build (requires DAHDI), consistent with "built separately" |
| 16 | "`chan_pjsip`: SIP — the primary and only SIP channel driver in Asterisk 22 LTS" | 144 | VERIFIED | lab: `module show like chan_pjsip` → chan_pjsip.so Running, support level core; `module show like chan_sip` → 0 modules. https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/ |
| 17 | "the old `chan_sip` was removed in Asterisk 21 and does not exist in Asterisk 22" | 144, 180, 297, 318 | VERIFIED | https://github.com/asterisk/asterisk/releases/tag/21.0.0 ("chan_sip: Remove deprecated module. … deprecated in Asterisk 17 and is now being removed"). lab confirms absent in 22.10.0. |
| 18 | "Asterisk 22 LTS" (Long Term Support) | 144, 178, 297, 312 | VERIFIED | https://docs.asterisk.org/About-the-Project/Asterisk-Versions/ (22 = LTS; released 2024-10-16, security-fix 2028-10-16, EOL 2029-10-16) |
| 19 | "`chan_iax2`: the IAX2 protocol — still ships in Asterisk 22 but is legacy" | 145, 182 | VERIFIED | lab: `module show like chan_iax2` → chan_iax2.so present, support level **core** (chan_iax2.so on disk). Note: "legacy" is editorial — IAX2 is NOT officially deprecated. |
| 20 | "`chan_unistim`: Nortel/Avaya UNISTIM phones. Still available (extended support)" | 146, 182 | VERIFIED | lab: `module show like chan_unistim` → chan_unistim.so, Support Level **extended** |
| 21 | "`chan_h323` (H.323) survives only as the community `ooh323` add-on" | 148, 183 | VERIFIED (with nuance) | https://github.com/asterisk/asterisk/blob/master/addons/chan_ooh323.c — chan_ooh323 ships in the official repo under `addons/` (extended support); chan_h323 absent from 22. lab: no chan_h323.so / chan_ooh323.so in default build. Nuance: ooh323 is in the official tree's addons, not strictly an outside community project. |
| 22 | "`chan_mgcp` (MGCP) and `chan_skinny` (Cisco SCCP) were deprecated and dropped from the modern channel set" / "no longer part of a standard Asterisk 22 build" | 148, 183 | VERIFIED | https://github.com/asterisk/asterisk/releases/tag/21.0.0 ("chan_mgcp: Remove deprecated module … deprecated in Asterisk 19"; same for chan_skinny). lab: neither on disk in 22.10.0. (Precision: removed in 21, not merely deprecated.) |
| 23 | "**Local**: a pseudo-channel (built into the core) … Dial string: `Local/extension@context`" | 152 | VERIFIED | lab: `core show channeltypes` → "Local — Local Proxy Channel Driver"; no chan_local.so on disk (built into core). https://docs.asterisk.org/Configuration/Channel-Drivers/Local-Channel/ |
| 24 | "Internally, Asterisk uses slinear as the stream format when it needs to convert from one codec to another" | 156 | VERIFIED | lab: `core show translation` — all cross-codec paths route through slin/slinXX (signed linear); slin is the universal intermediate format |
| 25 | "Some codecs … are supported only in pass-through mode; these codecs cannot be translated" / "G.723.1 - Only pass-through mode" | 156, 167 | VERIFIED | lab: `core show codecs audio` lists g723 (no g723 translator in `core show translation` table → pass-through only) |
| 26 | "G.711 ulaw (64 Kbps)" / "G.711 alaw (64 Kbps)" | 164–165 | VERIFIED | RFC 3551 §4.5.14 (PCMU/PCMA, 64 kbit/s); lab `core show codecs audio` (ulaw, alaw) |
| 27 | "G.722 (High Definition) – (64 Kbps)" | 166 | VERIFIED | ITU-T G.722 wideband, 64 kbit/s; lab `core show codecs audio` → g722 |
| 28 | "G.726 - (16/24/32/40kbps)" | 168 | VERIFIED | ITU-T G.726 ADPCM rates 16/24/32/40 kbit/s; lab `core show codecs audio` → g726, g726aal2 |
| 29 | "G.729 - Binary codec module distributed by Sangoma; the download is free of charge, but lawful use requires purchasing a per-channel license (8Kbps)" | 169 | VERIFIED | https://www.asterisk.org/products/add-ons/g729-codec/ ; Sangoma G.729 Codec Policy — module downloads free, per-channel license required. 8 kbit/s = ITU-T G.729. lab: g729 codec present (G.729A). |
| 30 | "GSM - (12-13 Kbps)" | 170 | VERIFIED | GSM 06.10 full-rate = 13 kbit/s; lab `core show codecs audio` → gsm |
| 31 | "iLBC - (15 Kbps)" | 171 | VERIFIED | RFC 3951 iLBC: 15.2 kbit/s (20 ms) / 13.33 kbit/s (30 ms); lab → ilbc |
| 32 | "Opus (5.3-510Kbps)" | 174 | VERIFIED | RFC 6716 Opus operating range 6–510 kbit/s; lab `core show codecs audio` → opus. (Lower bound ~6 kbps; "5.3" is marginally off — see Unverified note.) |
| 33 | "the application dial() is used … to bridge calls" (and `core show applications`) | 187, 344 | VERIFIED | lab: `core show application Dial` → "Attempt to connect to another device or endpoint and bridge the call. Provided By app_dial". https://docs.asterisk.org/Asterisk_22_Documentation/API_Documentation/Dialplan_Applications/Dial/ |
| 34 | "Asterisk wiki (www.voip-info.org)" | 86 | WRONG (fixed) | voip-info.org is a third-party community wiki, NOT the official Asterisk wiki. Official docs/wiki: https://docs.asterisk.org (chapter line 283 itself lists wiki.asterisk.org). Fixed: reworded to "official Asterisk documentation (docs.asterisk.org), the community-maintained VoIP-Info wiki". |
| 35 | "more than 300,000 systems run Asterisk, and Digium has sold more than 4 million voice interfaces" (VoIP-Supply) | 98 | UNVERIFIED | Dated secondary marketing statistic; no authoritative primary source found. Could not corroborate. |
| 36 | "Eastern Management Group concluded that open-source PBXs account for 18% … 85% of the open-source PBX market is based on Asterisk … now ranks second in terms of lines connected to an IP PBX" | 98 | UNVERIFIED | Dated analyst figures; original Eastern Management Group report not accessible as a verifiable primary source. |
| 37 | "more than 3,000 changes and bugs … corrected" between Asterisk 1.0 and 1.2 | 86 | UNVERIFIED | No authoritative changelog tally located to confirm the exact "3,000" figure for 1.0→1.2. |
| 38 | "Asterisk has been used in installations with more than 10,000 users" | 110 | UNVERIFIED | Plausible scalability claim but no citable authoritative deployment reference found. |
| 39 | "Opus (5.3-510Kbps)" lower bound 5.3 | 174 | UNVERIFIED (minor) | RFC 6716 states Opus 6–510 kbit/s; the "5.3" lower bound is slightly off (likely conflated with G.723.1's 5.3 kbps). Left for author — not unambiguously a typo in this codec list. |
| 40 | "Asterisk does not support silence suppression" | 299 | UNVERIFIED | Internal/editorial summary claim. Asterisk does support comfort-noise/VAD-related features; "silence suppression" support status is not cleanly documented as a yes/no. Flagged for author. |

## Unverified claims the author must resolve before print

- **#35** Market-size statistics ("300,000 systems", "4 million interfaces", VoIP-Supply) — dated, no primary source.
- **#36** Eastern Management Group market-share figures ("18%", "85%", "second in lines") — analyst report not verifiable.
- **#37** "more than 3,000 changes and bugs" between Asterisk 1.0 and 1.2 — no authoritative changelog tally.
- **#38** "more than 10,000 users" deployment claim — no citable reference.
- **#39** Opus lower bitrate "5.3 Kbps" — RFC 6716 gives ~6 kbps; consider correcting to 6–510 kbps.
- **#40** "Asterisk does not support silence suppression" — internal claim; verify intent.
- **#7** "Asterisk OEM" license tier — historical claim, no authoritative primary source.

## Fixes applied

- **Line 86** (ledger #34): changed "Asterisk wiki (www.voip-info.org)" to clarify that the official documentation is docs.asterisk.org and VoIP-Info is a community-maintained wiki. Source: https://docs.asterisk.org and the chapter's own line 283 (wiki.asterisk.org).
