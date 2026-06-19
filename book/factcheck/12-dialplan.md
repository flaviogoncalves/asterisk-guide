# Fact-check ledger — Dial Plan advanced features

Verified: 26 · Wrong (fixed): 1 · Unverified: 3

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "The function FILTER() is very handy for this" / `FILTER(0-9,${EXTEN})` filters all but digits | 32, 35 | VERIFIED | lab: `core show function FILTER` (func_strings; "Permits all characters listed in <allowed-chars>, filtering all others out"; range syntax `-`) |
| 2 | Dialplan injection: dialing `3000&DAHDI/...` triggers two calls (the `&` separates channels) | 32 | VERIFIED | AST-2010-002 dialplan injection advisory https://www.asterisk.org/security-advisory/ast-2010-002-dialplan-injection-vulnerability/ |
| 3 | Footnote ref AST-2010-002 (dialplan injection security advisory) | 42 | VERIFIED | https://downloads.asterisk.org/pub/security/AST-2010-002.html (note: chapter links a `.pdf`; live file is `.html`) |
| 4 | Background() plays files while waiting for an extension; "If one of the requested sound files does not exist, call processing will be terminated"; options s/n/m | 46-50 | VERIFIED | lab: `core show application Background` — Syntax `BackGround(filename1[&filename2[&...]][,options[,langoverride[,context]]])`; description matches |
| 5 | Record() syntax: format, silence, maxduration, options a/n/q/s/t/x; `%d` increments; `#` terminates | 52-63 | VERIFIED | lab: `core show application Record` — Syntax `Record(filename.format[,silence[,maxduration[,options]]])` |
| 6 | Read() syntax & arguments (variable, filename, maxdigits ≤255, options s/i/n, attempts, timeout) | 77-111 | VERIFIED | lab: `core show application Read` — Syntax `Read(variable[,filename[&...]][,maxdigits[,options[,attempts[,timeout]]]])` |
| 7 | GotoIf() jumps to labeliftrue/labeliffalse; omitted label → next priority | 113-115 | VERIFIED | lab: `core show application GotoIf` — Syntax `GotoIf(condition?[labeliftrue][:labeliffalse])` |
| 8 | Goto() syntax `Goto([[context,]extension,]priority)` (Quiz Q9) | 854-858 | VERIFIED | lab: `core show application Goto` — Syntax `Goto([[context,]extension,]priority)` |
| 9 | "Macro ... was deprecated a long time ago in favor of GOSUB" | 178 | VERIFIED | app_macro deprecated in 16 https://www.asterisk.org/asterisk-21-module-removal/ ; ASTERISK-29558 |
| 10 | GOSUB command format `gosub([[context,]exten,]priority[(arg1[,...][,argN])])` | 181 | VERIFIED | lab: `core show application GoSub` — Syntax `Gosub([[context,]extension,]priority[(arg1[,...][,argN])])` |
| 11 | "GOSUB ... received parameter support in version 10" | 184 | UNVERIFIED | No primary source pinning argument support to exactly v10; docs/changelog not located. Plausible but unconfirmed. |
| 12 | "Macros (`app_macro`) were removed in Asterisk 21; you must use GOSUB" | 184 | VERIFIED | lab: `module show like macro` → 0 modules; `core show application Macro` → not registered. Removed in 21 https://www.asterisk.org/asterisk-21-module-removal/ |
| 13 | "In modern Asterisk (including Asterisk 22) AstDB is backed by SQLite3 (`/var/lib/asterisk/astdb.sqlite3`); older versions used Berkeley DB v1" | 217 | VERIFIED | lab: `ls /var/lib/asterisk/astdb.sqlite3` exists; https://docs.asterisk.org/Fundamentals/Asterisk-Internal-Database/SQLite3-astdb-back-end/ |
| 14 | "Since Asterisk 1.8 the AstDB is stored in SQLite3" (2nd-ed note) — FIXED to "Since Asterisk 10 ... used by Asterisk 1.8 and earlier" | 219 | WRONG (fixed) | Switch was in Asterisk 10; Berkeley DB used by 1.8 and previous. https://docs.asterisk.org/Fundamentals/Asterisk-Internal-Database/SQLite3-astdb-back-end/ |
| 15 | DB(), DB_EXISTS() functions exist | 225-227 | VERIFIED | lab: `core show function DB_EXISTS` (func_db, "Check to see if a key exists") |
| 16 | "the old `DBdel()` application was removed" | 238, 860 | VERIFIED | lab: `core show application DBdel` → not registered |
| 17 | DB_DELETE() is a function returning and deleting a key | 238, 241 | VERIFIED | lab: `core show function DB_DELETE` (func_db, "Return a value from the database and delete it") |
| 18 | "DBdeltree() ... is still an application" | 239, 241 | VERIFIED | lab: `core show application DBdeltree` — present ("Delete a family or keytree from the asterisk database") |
| 19 | CLI commands: database del/put/show/showkey/deltree/get | 245-250 | VERIFIED | lab: `core show help database` — del, deltree, get, put, query, show, showkey all present |
| 20 | "The `LookupBlacklist()` application was removed ... not registered in the 22.10.0 lab" | 286 | VERIFIED | lab: `core show application LookupBlacklist` → not registered |
| 21 | Time-include uses commas, not pipes: `include => context,<times>,<weekdays>,<mdays>,<months>` | 337, 340, 831 | VERIFIED | https://docs.asterisk.org/Configuration/Dialplan/Variables/ ; comma form is current (pipe deprecated 1.6) |
| 22 | GotoIfTime syntax `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])`; comma separators; optional timezone | 353, 356, 360-376 | VERIFIED | lab: `core show application GotoIfTime` — Syntax `GotoIfTime(times,weekdays,mdays,months[,timezone]?[labeliftrue][:labeliffalse])` |
| 23 | DISA syntax `DISA(passcode\|filename[,context[,cid[,mailbox[@context][,options]]]])`; default context `disa`; comma separators | 383-399 | VERIFIED | lab: `core show application DISA` — Syntax `DISA(passcode\|filename[,context[,cid[,mailbox[@context][,options]]]])` |
| 24 | GROUP() / GROUP_COUNT() functions count active channels in a group | 403-407 | VERIFIED | lab: `core show function GROUP` ("Gets or sets the channel group") and `GROUP_COUNT` ("Counts the number of channels in the specified group") |
| 25 | VoiceMail() syntax `VoiceMail(mailbox[@context][&mailbox[@context][&...]][,options])`; options b/d/g/s/u/U/P; 0→'o', *→'a'; VMSTATUS SUCCESS/USEREXIT/FAILED | 445-485 | VERIFIED | lab: `core show application VoiceMail` — Syntax matches |
| 26 | Directory() syntax `Directory([vm-context][,dial-context[,options]])`; names from voicemail.conf; options e/f/l/b/m/p | 591-638 | VERIFIED | lab: `core show application Directory` — Syntax `Directory([vm-context][,dial-context[,options]])` |
| 27 | MWI mailbox set with `mailboxes` option in PJSIP `[endpoint]`; handled by res_pjsip_mwi | 567-573 | VERIFIED | lab: `config show help res_pjsip endpoint mailboxes` (since 12.0.0); `module show like res_pjsip_mwi` → running |
| 28 | Pattern `_912.` matches before `_9.`; "An included context is processed later than a pattern in the same context" | 158-166 | VERIFIED | Asterisk best-match / include ordering — pattern specificity & includes processed last. https://docs.asterisk.org/Configuration/Dialplan/Pattern-Matching/ |
| 29 | "Voicemail notification works with SIP phones, DAHDI phones, and some IAX2 phones" | 567 | UNVERIFIED | General MWI capability; no single authoritative page enumerating "some IAX2" — left as-is (low risk). |
| 30 | vmail.cgi installed via `make webvmail`; Perl + Apache | 545-553 | UNVERIFIED | Could not confirm vmail.cgi still ships in the Asterisk 22 source tree; not testable in lab (no source tree). |
| 31 | Quiz Q6/Q10 answers: AstDB = SQLite3; delete single key = DB_DELETE() | 843-865 | VERIFIED | Same sources as rows 13, 17 |

## Summary

- Verified: 26
- Wrong (fixed): 1
- Unverified: 3

## Wrong / fixed

- Line 219 (2nd-ed note): "Since Asterisk 1.8 the AstDB is stored in SQLite3" → corrected to "Since Asterisk 10 ... used by Asterisk 1.8 and earlier." The SQLite3 switch landed in Asterisk 10; Berkeley DB was used by 1.8 and previous. Source: https://docs.asterisk.org/Fundamentals/Asterisk-Internal-Database/SQLite3-astdb-back-end/

## Unverified — author to resolve before print

1. Line 184 — "GOSUB ... received parameter support in version 10." Could not find a primary doc/changelog pinning Gosub argument support to exactly Asterisk 10. The fact that Gosub takes args is verified (lab); the version is the unconfirmed part.
2. Line 567 — "Voicemail notification works with SIP phones, DAHDI phones, and some IAX2 phones." MWI generally works; the "some IAX2" qualifier has no single authoritative citation.
3. Lines 545-553 — vmail.cgi / `make webvmail`. Could not confirm this web interface still ships in the Asterisk 22 source distribution (no source tree available in the lab to check).

## Other notes (not fact errors)

- Line 42 footnote links `http://downloads.asterisk.org/pub/security/AST-2010-002.pdf`; the live advisory is served as `.html` (https://downloads.asterisk.org/pub/security/AST-2010-002.html). Consider updating the URL/extension.
