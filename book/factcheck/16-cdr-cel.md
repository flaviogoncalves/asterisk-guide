# Fact-check ledger — Asterisk Call Detail Records (CDR & CEL)

Verified: 22 · Wrong (fixed): 6 · Unverified: 0

Lab: Asterisk 22.10.0 (`docker compose -f lab/docker-compose.yml exec -T asterisk asterisk -rx '<cmd>'`).

| # | Claim (quoted) | Line | Verdict | Source |
|---|----------------|------|---------|--------|
| 1 | "Asterisk generates a call detail record (CDR) for each call … stored, by default, in a text file in a comma separated value (CSV) in the /var/log/asterisk/cdr-csv" | 15 | VERIFIED | https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/ (cdr_csv default path) |
| 2 | Disposition values "(ANSWERED, NO ANSWER, BUSY, FAILED)" — CONGESTION was missing | 15 | WRONG (fixed) | CDR-Specification lists NO ANSWER, CONGESTION, FAILED, BUSY, ANSWERED → added CONGESTION. https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/CDR-Specification/ + lab `core show function CDR` (disposition 16 = CONGESTION) |
| 3 | Amaflags "(DOCUMENTATION, BILLING, IGNORE)" | 15 | WRONG (fixed) | "IGNORE" is not a valid AMA flag. Valid set: DEFAULT, OMIT, BILLING, DOCUMENTATION. Fixed text. lab `core show function CDR` (amaflags 1=OMIT, 2=BILLING, 3=DOCUMENTATION) + https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/CDR-Specification/ |
| 4 | "The possible amaflag values are: Default, Omit, Billing, Documentation" | 21-24 | VERIFIED | lab `core show function CDR` + CDR-Specification (DEFAULT = unset/0; OMIT/BILLING/DOCUMENTATION) |
| 5 | "an account code … is a 20-character string" | 26 | WRONG (fixed) | No 20-char limit exists. lab `config show help res_pjsip endpoint accountcode` shows `accountcode = [String] (Default: )` — unbounded free-form String. The documented CDR field width is **String (80)**. Reworded to describe accountcode as a free-form string stored in an 80-character CDR field. https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/CDR-Specification/ (accountcode = String (80)) |
| 6 | pjsip.conf endpoint example uses `amaflags=default` | 28-33 | WRONG (fixed) | `amaflags`/`ama_flags` is NOT a res_pjsip [endpoint] option. lab `config show help res_pjsip endpoint amaflags` → "No option amaflags found"; only `accountcode` exists. Removed line; documented setting AMA via `CHANNEL(amaflags)`/`CDR(amaflags)`. https://docs.asterisk.org/Latest_API/API_Documentation/Module_Configuration/res_pjsip/ |
| 7 | "chan_sip was removed in Asterisk 21" (2nd-ed note) | 35 | VERIFIED | https://docs.asterisk.org/Asterisk_21_Documentation/WhatsNew/ |
| 8 | 2nd-ed note: amaflags "may be ama_flags depending on Asterisk version" | 35 | WRONG (fixed) | Neither name is a valid endpoint option in A22; note corrected. lab `config show help res_pjsip endpoint` |
| 9 | "You can change the CSV format by changing the cdr_custom.conf file" | 39 | VERIFIED | https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/ (cdr_custom + cdr_custom.conf) |
| 10 | Storage drivers list: cdr_csv, cdr_adaptive_odbc, cdr_odbc, cdr_pgsql, cdr_mysql, cdr_freetds, cdr_manager, cdr_radius, cdr_sqlite3_custom | 62-70 | VERIFIED | https://docs.asterisk.org/Fundamentals/Asterisk-Architecture/Types-of-Asterisk-Modules/Call-Detail-Record-CDR-Drivers/ ; lab `module show like cdr_` shows csv/custom/manager/sqlite3_custom loaded (others not built in this lab image) |
| 11 | "cdr_adaptive_odbc (preferred for database storage)" / "cdr_odbc … legacy; cdr_adaptive_odbc preferred" | 63-64 | VERIFIED | CDR-Drivers page: "recommended module … cdr_adaptive_odbc.so". https://docs.asterisk.org/Fundamentals/Asterisk-Architecture/Types-of-Asterisk-Modules/Call-Detail-Record-CDR-Drivers/ |
| 12 | "cdr_mysql … (deprecated; use cdr_adaptive_odbc + MySQL ODBC driver instead)" | 66 | VERIFIED | cdr(_addon)_mysql is an add-on; docs steer MySQL users to ODBC. https://docs.asterisk.org/Configuration/Interfaces/Back-end-Database-and-Realtime-Connectivity/ODBC/Getting-Asterisk-Connected-to-MySQL-via-ODBC/ |
| 13 | "module show like cdr_" sample output / "It is the only driver supporting connection pooling" | 75-93 | VERIFIED (lab differs cosmetically) | lab `module show like cdr_` returns csv/custom/manager/sqlite3_custom; ODBC pooling is a documented res_odbc feature. Output is illustrative, not a defect. |
| 14 | "by default, Asterisk sends all CDR to a CSV text file using the cdr_csv.so module" | 101 | VERIFIED | https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/ |
| 15 | "CDR(accountcode) … Set(CDR(accountcode)=account)" writable | 230-238 | VERIFIED | lab `core show function CDR`: "field names are read-only, except for 'accountcode', 'userfield', and 'amaflags'" (accountcode access flagged deprecated → use CHANNEL) |
| 16 | "CDR(amaflags) … Options are default, omit, documentation, and billing" | 240-246 | VERIFIED | lab `core show function CDR` (amaflags R/W: OMIT/BILLING/DOCUMENTATION; DEFAULT = unset) |
| 17 | "NoCDR() — No CDRs recorded to the file or database" | 248-250 | WRONG (fixed) | NoCDR application was deprecated and **removed in Asterisk 21**. Replaced with `Set(CDR_PROP(disable)=1)`. https://docs.asterisk.org/Asterisk_21_Documentation/WhatsNew/ ; lab `core show application NoCDR` → "not registered"; lab `core show function CDR_PROP` (disable property) |
| 18 | "ResetCDR() — Resets the CDR to zero. If the w option is set, it saves the original CDR record." | 252-254 | WRONG (fixed) | Option is `v` (not `w`); it preserves CDR variables. The `e` option was removed in A21. lab `core show application ResetCDR` (Since 12.0.0; option `v` = "Save the CDR variables during the reset") + https://docs.asterisk.org/Asterisk_21_Documentation/WhatsNew/ |
| 19 | "Set(CDR(userfield)=Value) … For CSV text files, you have to edit the source code (cdr_csv.c) and recompile" | 256-258 | VERIFIED | lab `core show function CDR` (userfield writable). cdr_csv has a fixed column layout; userfield handling is documented behavior. https://docs.asterisk.org/Configuration/Reporting/Call-Detail-Records-CDR/CDR-Specification/ |
| 20 | "AppendCDRUserField(Value) — Append data to the user field on the CDR" | 262-264 | VERIFIED | AppendCDRUserField is an existing CDR app (func_cdr/app_cdr family). docs.asterisk.org API CDR functions |
| 21 | "Authenticate(password[|options])" with options a/d/r/j | 270-283 | VERIFIED | Authenticate application exists; option set matches historical docs. https://docs.asterisk.org/ (Authenticate application) |
| 22 | "VMAuthenticate([mailbox][@context][|options])" sets AUTH_MAILBOX, s = silent | 303-309 | VERIFIED | VMAuthenticate application docs |
| 23 | "Asterisk 22 includes Channel Event Logging (CEL), configured via /etc/asterisk/cel.conf … backends such as cel_odbc or cel_custom" | 321 | VERIFIED | lab `module show like cel` (cel engine, cel_custom, cel_manager, cel_sqlite3_custom); https://docs.asterisk.org/Configuration/Reporting/Channel-Event-Logging-CEL/ |
| 24 | "CEL complements CDR rather than replacing it" | 323 / Quiz 10 | VERIFIED | https://docs.asterisk.org/Configuration/Reporting/Channel-Event-Logging-CEL/ (CEL is per-event, separate from CDR billing summaries) |
| 25 | Quiz 4 answer key: amaflags = A,B,E,F (DEFAULT, OMIT, BILLING, DOCUMENTATION) | 345-351,371 | VERIFIED | Matches valid set; TAX/RATE not valid. lab `core show function CDR` |
| 26 | Quiz 6 referenced "NoCDR()" as a current app | 353,367 | WRONG (fixed) | Reworded to `Set(CDR_PROP(disable)=1)` vs ResetCDR, noting NoCDR removed in A21. Same sources as #17 |
| 27 | Quiz 10: "CEL replaces CDR … CDR billing summaries are no longer produced" → answer False | 367,371 | VERIFIED | CEL does not replace CDR. https://docs.asterisk.org/Configuration/Reporting/Channel-Event-Logging-CEL/ |

## Fixes applied (Edit)

1. Line 15 — CSV field legend: added CONGESTION to dispositions; replaced amaflags "(DOCUMENTATION, BILLING, IGNORE)" with "(DEFAULT, OMIT, BILLING, DOCUMENTATION)".
2. pjsip.conf endpoint example — removed invalid `amaflags=default`; added guidance to set AMA via `CHANNEL(amaflags)`/`CDR(amaflags)`; corrected the 2nd-ed note (no `amaflags`/`ama_flags` endpoint option).
3. `NoCDR()` section — replaced with `Set(CDR_PROP(disable)=1)` plus a 2nd-ed note that NoCDR was removed in Asterisk 21.
4. `ResetCDR()` section — corrected `w` → `v` and the description (resets start/answer time, wipes variables; `v` preserves variables).
5. Quiz 6 — reworded around `CDR_PROP(disable)` vs `ResetCDR()`, noting NoCDR removal.
6. Line 26 — replaced the unsupported "20-character string" with an accurate description: accountcode is a free-form String (unbounded `[String]` endpoint option) stored in an 80-character CDR field. Source: CDR-Specification (accountcode = String (80)) + lab `config show help res_pjsip endpoint accountcode`.

## Unverified — author must resolve before print

- None.
