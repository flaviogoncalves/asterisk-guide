# Chapter 13 (PBX features) — illustration routing & AI subjects

Source script for all PATH-1 figures: `book/illustrate/render_13.py` (Pillow, house style
1600x900, white bg, ink #1A1A1A, accent #1C5D99).

| Figure | Path | Notes |
|--------|------|-------|
| fig01 | PATH 1 | Three-column "where features are implemented" list. Modernized: MeetMe → ConfBridge. |
| fig02 | PATH 1 | `[featuremap]` codes from features.conf (blindxfer/disconnect/automon/atxfer/parkcall/automixmon). |
| fig03 | PATH 1 | Blind (#) vs attended (*2 atxfer) transfer step lists. |
| fig04 | PATH 1 | Call parking: lot 701–720, dial 700, + `res_parking.conf [default]` block (parkext 700, parkpos 701-720, context parkedcalls). |
| fig05 | PATH 1 | Call pickup groups. PJSIP snake_case `call_group`/`pickup_group`; operator picks up 1,2,3; *8. |
| fig06 | KEEP | Real CLI capture of `core show application confbridge`. Left untouched. |
| fig07 | PATH 1 | MeetMe conference types (legacy). Note: DAHDI timing (dahdi_dummy), not built by default in Asterisk 22, use ConfBridge. |
| fig08 | PATH 1 | MeetMe() syntax + option flags (legacy/historical reference). |
| fig09 | PATH 1 | MixMonitor() syntax + options a/b/v/V/W + command + ${MIXMONITOR_FILENAME}. |
| fig10 | PATH 1 | musiconhold.conf modes; `files` highlighted as default (no transcoding). |

## AI spend
None. No PATH-3 (Nano Banana) generations were required — every figure was either text/list/
feature-flow (PATH 1) or a real CLI screenshot (KEEP). Total AI cost: **$0.00**.

## PATH-3 fallback subjects (only if a future redraw is ever needed)
- fig07 — flat conference-room concept (three circles: single speaker, password-protected,
  dynamic). Subject line if ever escalated: "three conference rooms shown as circles of
  participant icons — single active speaker, padlock-marked password-protected room, and a
  dynamic room of clustered subgroups; caption that MeetMe needs a DAHDI timing source and is
  legacy/replaced by ConfBridge in Asterisk 22."
