# Chapter 12 — Dial Plan advanced features: figure routing

No PATH 3 (Nano Banana / paid AI) figures were generated for this chapter.
**Total AI spend: $0.00.**

All redrawn figures were produced by `book/illustrate/render_12.py` (Pillow, house style:
white bg, ink #1A1A1A, single blue accent #1C5D99, 1600x900 / 16:9, system fonts).
Filenames keep the chapter's referenced names (`10-dialplan-advanced-features-imgNN.png`).

Every figure's content was modernized to **Asterisk 22**: comma argument/field separators
(no pipes), `PJSIP/` dialstrings (no `SIP/`/`Zap/`), `DB_DELETE()` function (the removed
`DBdel()` application is gone), `DBdeltree()` retained as an application, `pjsip.conf`
endpoints (no `sip.conf`). Cross-checked against the chapter text and `book/factcheck/12-dialplan.md`.

| fig | route | reason / what changed |
|-----|-------|-----------------------|
| img01 | PATH 1 | Background() reference slide. Old pipe syntax `(...\|options\|langoverride\|context)` → comma syntax `Background(filename1[&...][,options[,langoverride[,context]]])`. |
| img02 | PATH 1 | Record() reference (synopsis + syntax + args). Old `Record(filename.format\|silence...)` → `Record(filename.format[,silence[,maxduration[,options]]])`. |
| img03 | PATH 1 | Record() options a/n/q/s/t/x — re-typeset clean; content matches `core show application Record`. |
| img04 | PATH 1 | Read() reference. Old pipe syntax → `Read(variable[,filename[&...]][,maxdigits[,options[,attempts[,timeout]]]])`. |
| img05 | PATH 1 | Read() options s/i/n + attempts/timeout — re-typeset clean. |
| img06 | PATH 1 | Context-inclusion diagram. `sip.conf`→`pjsip.conf` (`type=endpoint`), `SIP/`→`PJSIP/`, `Zap/`→`DAHDI/`, `internat`→`ldi`; arrows redrawn flat with accent. |
| img07 | PATH 1 | AstDB family/key tree + Functions/Applications. Added "SQLite3" + `astdb.sqlite3` path; dropped removed `dbdel()`, added `DB_DELETE()` function + note; kept `DBdeltree()` as application. |
| img08 | PATH 1 | AstDB CLI commands — verified set (get/put/del/deltree/show/showkey/query) per `core show help database`. |
| img09 | PATH 1 | Call-forward-immediate / DND programming. `DBdel(...)` → `Set(x=${DB_DELETE(...)})`. |
| img10 | PATH 1 | Call-forward-on-busy programming. `DBdel(...)` → `Set(x=${DB_DELETE(...)})`; added CLI `database show` examples. |
| img11 | PATH 1 | Time-based contexts. Pipe field separators → commas (`include => normalhours,08:00-18:00,mon-fri,*,*`). |
| img12 | PATH 1 | normalhours/afterhours contexts. `Dial(SIP/${SECURITY})` → `Dial(PJSIP/${SECURITY},20,tT)`. |
| img13 | PATH 1 | VoiceMailMain() menu tree — re-typeset flat with accent connectors; menu content current. |
| img16 | PATH 1 | "Putting it all together" scenario + network topology. Redrawn flat (PSTN cloud, Asterisk PBX, LAN, ATA/IP phone/softphone); "SIP based extensions" → "PJSIP-based extensions". Dated clip-art network — done as flat Pillow vector rather than paid PATH 3 (cheapest faithful path). |

## KEPT (not redrawn)

- **img14** + **img15** — real screenshot of the `vmail.cgi` "Comedian Mail" web login page
  (Asterisk Web-Voicemail). It is a genuine UI capture (the script still ships in Asterisk 22 at
  `contrib/scripts/vmail.cgi`, per the fact-check ledger), so it is left untouched — redrawing a
  browser screenshot would fabricate UI. Note: the capture shows dated IE6 / Windows XP browser
  chrome and a "Copyright 2004, Digium" footer; a future re-capture on a modern browser/Asterisk
  22 lab would refresh it, but that is a re-shoot, not an illustration task.
