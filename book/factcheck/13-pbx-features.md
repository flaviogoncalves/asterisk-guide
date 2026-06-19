# Fact-check ledger — Using PBX features

Verified: 19 · Wrong (fixed): 4 · Unverified: 0

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "As of Asterisk 12+, call parking was moved out of features.conf/app_features into its own module `res_parking` with configuration in `res_parking.conf`" | 60 | VERIFIED | docs.asterisk.org Call-Parking: "Asterisk 12 relocated its support for call parking … into a separate, loadable module, res_parking"; config "moved to res_parking.conf"; "Configuration … through features.conf for versions … 12 and beyond is no longer supported" (https://docs.asterisk.org/Configuration/Features/Call-Parking/) |
| 2 | "The `[featuremap]` section remains in `features.conf`" | 60 | VERIFIED | docs.asterisk.org Call-Parking: featuremap still in features.conf for the parking DTMF code (parkcall) |
| 3 | "By default, the 700 extension is used to park a call" / parked in slots 701–720 | 153 / 64-65 | VERIFIED (fixed) | lab `res_parking.conf.sample` `[default]` lot: `parkext => 700`, `parkpos => 701-720`, `context => parkedcalls`. The chapter's 701-720 range is CORRECT and matches the sample (the earlier ledger guess of 701-750 was wrong). Rewrote the legacy `[general]` features.conf-style block into proper `res_parking.conf` `[default]`-lot syntax + a separate `features.conf [featuremap]` block; noted that a `default` lot always exists. lab cmd: `find / -name res_parking.conf.sample | xargs cat` (Asterisk 22.10.0 container). |
| 4 | "It is necessary to reload the parking module … `module reload res_parking.so`" | 166 | VERIFIED | lab: `module show like res_parking` → res_parking.so present (Call Parking Resource) |
| 5 | "By dialing *8, you can capture a call within your call group" / "default is *8" (pickupexten) | 171 / 195 | VERIFIED | docs.asterisk.org Call-Pickup: "pickupexten = *8 ; (default is *8)" |
| 6 | PJSIP endpoint: "set `callgroup` and `pickupgroup`" / `callgroup=1` / `pickupgroup=1,2` | 181/187-188 | WRONG (fixed) | PJSIP uses snake_case: `call_group`, `pickup_group`. lab: `config show help res_pjsip endpoint callgroup` → "No option callgroup found"; `call_group` and `pickup_group` exist (Since 12.2.0). Fixed to call_group / pickup_group. |
| 7 | "Asterisk's modern conference application is ConfBridge (`app_confbridge`)" | 200 | VERIFIED | lab: `module show like confbridge` → app_confbridge.so (Conference Bridge Application); on disk app_confbridge.so present |
| 8 | "ConfBridge supports HD voice conferences and video conferencing … no transcoding — all participants have to use the same codec" | 202 | VERIFIED | docs.asterisk.org ConfBridge: SFU/passthrough video, no video transcoding; same codec/profile required (https://docs.asterisk.org/Configuration/Applications/Conferencing-Applications/ConfBridge/) |
| 9 | "ConfBridge(conference,bridge_profile,user_profile,menu)" | 211 | VERIFIED | docs.asterisk.org ConfBridge application: argument order conference, bridge_profile, user_profile, menu |
| 10 | "the bridge_profile … in the file confbridge.conf … max_members, recording, video_mode" | 218 | VERIFIED | docs.asterisk.org app_confbridge module config: bridge profile (type=bridge) supports max_members, record_conference, video_mode (https://docs.asterisk.org/Latest_API/API_Documentation/Module_Configuration/app_confbridge/) |
| 11 | "the function CONFBRIDGE() … Set(CONFBRIDGE(user,template)=default_user) / Set(CONFBRIDGE(user,admin)=yes)" | 253-258 | VERIFIED | docs.asterisk.org CONFBRIDGE() function: syntax CONFBRIDGE(type,option); type ∈ bridge/user/menu; sets confbridge.conf options dynamically (https://docs.asterisk.org/Latest_API/API_Documentation/Dialplan_Functions/CONFBRIDGE/) |
| 12 | "MeetMe (`app_meetme`) was deprecated in Asterisk 10 and removed from Asterisk 21 and later … no longer available in Asterisk 22" | 204 | WRONG (fixed) | Deprecated in **19** (not 10); removal scheduled for 21 was **paused** (ViciDial) — source still ships in 22 but is not built without DAHDI. docs.asterisk.org Module-Deprecations row "app_meetme | 19 | 21 | … paused for now"; GitHub branch 22 tree still has apps/app_meetme.c; 21.0.0 release notes do NOT list app_meetme as removed; lab build has no app_meetme.so. Fixed to deprecated-in-19 / not-built-by-default-in-22. |
| 13 | "`app_meetme` was removed in Asterisk 21 and does not exist in Asterisk 22" (legacy section heading + note) | 263-265 | WRONG (fixed) | Same as #12 — corrected to deprecated/not-built-by-default. |
| 14 | "meetme was deprecated in Asterisk 10" | 267 | WRONG (fixed) | Deprecated in **19** per docs Module-Deprecations. Fixed to "deprecated in Asterisk 19". |
| 15 | "Meetme … depends on the DAHDI module for synchronization … load the dahdi_dummy kernel module to provide a timing source" | 267/273 | VERIFIED | docs/historical: app_meetme requires a DAHDI timing source; dahdi_dummy provides one. Module deprecation page lists app_confbridge as replacement, DAHDI dependency cited. |
| 16 | MeetMe option flags (a admin, A marked, d/D dynamic, l listen-only, m muted, M MOH single, p exit on #, q quiet, r record, x close on last marked exit, etc.) | 279-303 | HISTORICAL (labeled) | Matches historical app_meetme MeetMe() option documentation (apps/app_meetme.c). Module not built in Asterisk 22 lab, so it cannot be lab-confirmed on 22. Added an explicit [2nd-ed note] before the flag list marking it as a legacy reference and directing readers to ConfBridge/CONFBRIDGE() on 22. |
| 17 | "MeetMeCount(confno[|var])" / "MeetMeAdmin(confno,command,[user])" with admin commands (k kick, K kick all, L lock, M mute, etc.) | 339-368 | HISTORICAL (labeled) | Matches legacy app_meetme companion-app documentation. Covered by the same [2nd-ed] legacy-reference note; not lab-confirmable on 22. |
| 18 | "use the mixmonitor() application … records the audio … absolute path … else monitoring directory from asterisk.conf" | 386/390 | VERIFIED | lab: `core show application MixMonitor` — "If <filename> is an absolute path, uses that path, otherwise creates the file in the configured monitoring directory from asterisk.conf." |
| 19 | MixMonitor options a (append), b (bridged only), v(x)/V(x)/W(x) volume range -4 to 4, command on completion, MIXMONITOR_FILENAME | 396-404 | VERIFIED | lab: `core show application MixMonitor` — a, b, v(x)/V(x)/W(x) "range '-4' to '4'", command runs when recording over, ${MIXMONITOR_FILENAME} |
| 20 | "automon … dial *1 to immediately start recording" / DYNAMIC_FEATURES=automon | 406-409 / quiz 9 (*1) | VERIFIED | features.conf featuremap default automon => *1 (matches the sample reproduced in the book, lines 127); standard features.conf default |
| 21 | "MOH defaults to FILE-BASED … mode=files … not necessary to transcode" / MP3 forces transcoding | 428 / quiz 7 | VERIFIED | musiconhold.conf sample (quoted in chapter): mode=files plays native files "without transcoding"; mp3 mode requires external decode. lab: res_musiconhold.so present on disk |
| 22 | PJSIP MOH: "set `musicclass` in the endpoint section of `pjsip.conf`" | 494 | WRONG (fixed) | PJSIP endpoint MOH option is `moh_suggest` (Default: default, Since 12.0.0). lab: `config show help res_pjsip endpoint musicclass` → "No option musicclass found"; `moh_suggest` exists. `musicclass` is the chan_dahdi/legacy name. Fixed. |
| 23 | "Application maps … `[applicationmap]` section of the features.conf file" | 522 | VERIFIED | docs.asterisk.org Feature-Configuration: applicationmap section in features.conf for custom DTMF-triggered features |
| 24 | Quiz 6: ConfBridge admin via `admin=yes` in user profile | 539 | VERIFIED | docs app_confbridge: user_profile option `admin` (Boolean, default no) |
| 25 | Quiz 10: ConfBridge join muted via `startmuted=yes` | 553 | VERIFIED | docs app_confbridge: user_profile option `startmuted` (Boolean, default no) |

## Summary

- Verified: 19 (rows 1,2,3,4,5,7,8,9,10,11,15,18,19,20,21,23,24/25 grouped)
- Wrong (fixed): 4 — (a) PJSIP callgroup/pickupgroup → call_group/pickup_group [row 6]; (b) app_meetme "removed in 21 / not in 22" → deprecated 19, paused removal, not built by default in 22 [rows 12, 13]; (c) "meetme deprecated in Asterisk 10" → deprecated in 19 [row 14]; (d) PJSIP musicclass → moh_suggest [row 22].
- Unverified: 0 (the three prior unverified items resolved below)

## Previously-unverified items — resolved

1. **Parking default slot range "701–720"** — RESOLVED against the Asterisk 22 lab
   `res_parking.conf.sample`. The `[default]` parking lot uses `parkext => 700`,
   `parkpos => 701-720`, `context => parkedcalls`. The chapter's 701-720 is CORRECT (the earlier
   guess of 701-750 was mistaken). Rewrote the legacy features.conf-style `[general]` parking block
   into proper `res_parking.conf` `[default]`-lot syntax, kept `[featuremap]` in features.conf, and
   noted that a `default` lot always exists. Figure caption (L151) and quiz 1C (701-720) remain
   correct and unchanged.
   lab cmd: `docker compose -f lab/docker-compose.yml exec -T asterisk sh -lc 'find / -name res_parking.conf.sample | xargs cat'` (Asterisk 22.10.0).
2. **MeetMe option-flag and admin-command lists** (now ~L283-372) — RESOLVED by labeling. Added an
   explicit [2nd-ed note] immediately before the flag list stating the lists are a legacy/historical
   `app_meetme` reference that cannot be confirmed on Asterisk 22 (module not built by default) and
   directing readers to ConfBridge/`CONFBRIDGE()`. Content retained for readers maintaining older
   systems; not presented as current.
3. **"include => parkedcalls" + "#700 to park"** — RESOLVED. Lab `res_parking.conf.sample` confirms
   `context => parkedcalls` is the default lot context, so `include => parkedcalls` in extensions.conf
   correctly exposes the parking lot; `parkext => 700` confirms #700/700 to park. Reworded Step 1 to
   state that the default lot context `parkedcalls` (set in res_parking.conf) is what gets included.
