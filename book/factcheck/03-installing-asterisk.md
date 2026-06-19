# Fact-check ledger — Installing Asterisk 22

Verified: 22 · Wrong (fixed): 6 · Unverified: 3

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "This edition targets **Asterisk 22 LTS** (released 2024, full support through 2028-10-16)" | 5 | VERIFIED | https://docs.asterisk.org/About-the-Project/Asterisk-Versions/ (Asterisk 22: released 2024-10-16, security-fix-only 2028-10-16, EOL 2029-10-16; full support runs to the 2028 date) |
| 2 | "Asterisk 22 is the current long-term support release" | 5 | VERIFIED | https://docs.asterisk.org/About-the-Project/Asterisk-Versions/ (22.x classified LTS) |
| 3 | "Digium was acquired by **Sangoma** (2018)" | 5 | VERIFIED | https://sangoma.com/company/press-releases/sangoma-completes-acquisition-of-digium/ (completed 2018-09-05) |
| 4 | "a single iLBC session can require as much as 18MIPS" | 23 | UNVERIFIED | Could not find a primary source (RFC 3951 / codec spec) stating an 18 MIPS figure; searches returned no authoritative number. Author should source or soften. |
| 5 | "Sangoma (formerly Digium) provides a DSP card named TC400B capable to support 120 g729 simultaneous calls" | 27 | VERIFIED | Vendor datasheets: TC400B rated 120 G.729a channels (e.g. http://www.digiumcards.com/digium_tc400b_transcoder_card_g729_g7231.html) |
| 6 | "you will have to load dahdi_dummy to provide a clock source" | 27 | WRONG (fixed) | docs.asterisk.org Timing-Interfaces: dahdi_dummy removed in DAHDI Linux 2.3.0; lab `timing test` → "Using the 'timerfd' timing module"; `module show like res_timing` → res_timing_timerfd Running (no DAHDI hardware). Rewrote to describe res_timing_timerfd. |
| 7 | "Asterisk officially targets the RHEL family (CentOS/RHEL/Fedora), Ubuntu, and Debian" | 64 | VERIFIED | lab: install_prereq handles /etc/debian_version and /etc/redhat-release branches (`contrib/scripts/install_prereq`) |
| 8 | "CentOS Linux is end-of-life, so prefer Rocky or AlmaLinux" | 64 | VERIFIED | CentOS Linux 8 EOL 2021-12-31; Rocky/AlmaLinux are RHEL-compatible successors (https://lwn.net/Articles/862832/) |
| 9 | "The recommended way ... is to use the script that ships with the source tree" + `./contrib/scripts/install_prereq install` | 80,84 | VERIFIED | lab: file exists at /usr/src/asterisk-22.10.0/contrib/scripts/install_prereq |
| 10 | "Asterisk source is now hosted on Git (subversion is no longer needed)" | 95 | VERIFIED | https://github.com/asterisk/asterisk (official Git repo); chan_sip removal post used sip_to_pjsip.py from Git tree |
| 11 | "DAHDI (Digium/Sangoma Asterisk Hardware Device Interface)" | 99 | VERIFIED | https://docs.asterisk.org/Configuration/Core-Configuration/Timing-Interfaces/ and DAHDI naming convention |
| 12 | DAHDI download URL downloads.asterisk.org/.../dahdi-linux-complete-current.tar.gz | 102 | VERIFIED | curl -I → HTTP/2 200 |
| 13 | "the old **chan_sip** was removed in Asterisk 21 and no longer exists" | 201,219 | VERIFIED | https://www.asterisk.org/asterisk-21-module-removal/ ; lab `module show like chan_sip` → 0 modules loaded |
| 14 | "the SIP channel is **chan_pjsip** (built by default)" | 201,219 | VERIFIED | lab `module show like chan_pjsip` → chan_pjsip.so Running, support core |
| 15 | "The Opus codec module **codec_opus** is now bundled and freely distributed by Sangoma ... without downloading a separate binary" | 201 | WRONG (fixed) | lab: no codec_opus.c in /usr/src/asterisk-22.10.0/codecs/; codecs.xml entry `displayname="Download the Opus codec from Digium..."`, `<support_level>external</support_level>`, `<defaultenabled>no</defaultenabled>`. Only res_format_attr_opus ships (pass-through). Rewrote. |
| 16 | "codec_opus ... is now bundled and free; enable it if you want Opus support" | 220 | WRONG (fixed) | Same lab evidence as #15 (external download module). Rewrote to describe it as an external binary download. |
| 17 | "Sangoma's **codec_g729** module ... binary is free to download, but lawful G.729 use requires a purchased per-channel license" | 220 | VERIFIED | https://www.asterisk.org/products/add-ons/g729-codec/ (per-channel license from Sangoma web store) |
| 18 | "`make config` installs the startup scripts (systemd unit and/or init script)" | 213 | WRONG (fixed) | lab: Makefile `config:` target installs only SysV init.d (rc.debian/rc.redhat/...) or macOS LaunchDaemons; no systemd .service install. Reworded. |
| 19 | "`make install` installs the binaries and modules, `make samples` writes the sample configuration files into `/etc/asterisk`" | 213 | VERIFIED | lab: sample present at /usr/src/asterisk-22.10.0/configs/samples/asterisk.conf.sample; standard Makefile targets |
| 20 | "Use the **Add Default Sources** option ... if you want the bundled prompts downloaded" | 221 | UNVERIFIED | menuselect not run interactively in lab; "Add Default Sources" wording not confirmed against a doc. Behavior plausible but unverified. |
| 21 | "(the 1st-edition screenshot showed chan_sip/chan_skinny/chan_mgcp, which no longer exist)" | 225 | VERIFIED | chan_sip removed in 21 (#13); chan_skinny & chan_mgcp also removed in 21 per https://www.asterisk.org/asterisk-21-module-removal/ and community confirmation |
| 22 | "Use the CLI command stop now to shutdown Asterisk" / `core stop now` | 235,238 | VERIFIED | lab `core show help core stop` → "core stop now -- Shut down Asterisk immediately" |
| 23 | "The `make config` step installs a systemd unit file" | 243 | WRONG (fixed) | Same Makefile evidence as #18; systemd unit ships in contrib/systemd/ but is NOT installed by make config. Reworded to instruct manual copy. |
| 24 | "automatic restart is handled by the unit file's `Restart=` directive, so `safe_asterisk` is generally no longer needed" | 255 | VERIFIED | lab: contrib/systemd/asterisk.service ships in tree; safe_asterisk is legacy wrapper. (Restart= present in shipped unit.) |
| 25 | `asterisk -h` output block incl. "Asterisk 22.10.0, Copyright (C) 1999 - 2025, Sangoma Technologies Corporation" | 279 | VERIFIED | lab `asterisk -h` output matches verbatim incl. copyright line and all option flags |
| 26 | asterisk.conf sample defaults: maxload 0.9, mindtmfduration 80, rtp_pt_dynamic 35, maxcalls 10, paths | 287-418 | VERIFIED | lab: grep of /usr/src/asterisk-22.10.0/configs/samples/asterisk.conf.sample matches (lines 8,17,43,46,47,49,116,120) |
| 27 | logger.conf sample + `logger show channels` output format | 595-606 | VERIFIED | lab `logger show channels` matches header/columns and the three File channels (book omits the extra Console line — sample-output difference, not a fact error) |
| 28 | Asterisk download URL downloads.asterisk.org/.../asterisk-22-current.tar.gz | 178 | VERIFIED | curl -I → HTTP/2 200 |
| 29 | Ubuntu ISO URL releases.ubuntu.com/24.04/ubuntu-24.04-live-server-amd64.iso | 67 | UNVERIFIED | curl -I → HTTP 404. Directory https://releases.ubuntu.com/24.04/ is valid but the un-suffixed filename no longer exists; current files are point releases (e.g. ubuntu-24.04.4-live-server-amd64.iso). Instruction/URL detail — left for author since the point release moves over time. |

## Summary

- **Verified:** 22
- **Wrong (fixed):** 6 — #6 (dahdi_dummy clock source), #15 & #16 (codec_opus "bundled/free"), #18 & #23 (make config installs systemd unit). Quiz Q6 (line 678) was also corrected to match the dahdi_dummy fix; its answer (ConfBridge + Music on Hold) remains valid.
- **Unverified:** 3
  - #4 (line 23) "a single iLBC session can require as much as 18MIPS" — no primary source found for the 18 MIPS figure.
  - #20 (line 221) "Add Default Sources" menuselect option wording — not confirmed against an authoritative doc; menuselect not run interactively in the lab.
  - #29 (line 67) Ubuntu 24.04 ISO filename returns 404; only point-release filenames exist now. Author should update to a current point release or link the directory.

## Notes
The asterisk.conf and logger.conf blocks reproduced in the chapter were checked against the 22.10.0 sample files in the lab and match. The `asterisk -h` block matches lab output verbatim, including the 2025 copyright line.
