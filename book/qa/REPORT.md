# Book QA — page-by-page review of the rendered PDF (389 pp, 7.5x9.25)

Full-book visual review via the `book-qa` skill (12 reviewers, every page inspected).

## Global fixes (template/build) — DONE
- **[2nd-ed note] TODOs printing in the book** → stripped from print/EPUB by `book/strip-notes.lua`
  (kept in Markdown source for the author).
- **Line-break aids** for bleeds → `xurl` + `\emergencystretch` + `\sloppy`; tables already `\footnotesize`.

## Per-chapter source repairs (content; from the page review)
- **10-legacy (ch8) [BLOCKER]:** config dumps (gen_parameters.conf/system.conf) shredded into mini
  code-boxes + bullets → re-fence as single code blocks; **leaked Portuguese**; flattened install
  Steps 3/5; MFC/R2 signal tables rendered as run-on prose → real tables.
- **14-queues (ch11) [BLOCKER]:** image refs print as literal `![...](...)` because the alt text
  contains `[general]`/`[customerservice]` brackets that break the image markdown → escape/strip
  brackets in alt text (queues.conf example + 14-queues-fig06).
- **20-deployment (ch16):** "What to back up" table bleeds (restructure); Prometheus metric names
  bleed inline (→ code block/list); `pjsip show aor` transcript split into boxes/bullets (single
  fenced block); quiz Q10 options detach from the list.
- **12-dialplan (ch9):** Dial() options run-on (→ table); `o` pseudo-bullets + empty Read()-option
  code boxes; IVR-lab & Voicemail Step-1 run-ons; emailsubject/emailbody inline (→ code block).
- **06-designing (ch4):** codec comparison table-as-prose (→ table); stray `>`/`>=` bullet glyphs.
- **13-pbx (ch10):** Portuguese ConfBridge paragraph; `vendas` → `sales`.
- **18-realtime (ch14):** scrambled lab Step numbering; empty `show tables` output.
- **19-security (ch15):** empty Fuzzing/Flooding code boxes (tool URLs).
- **16-cdr (ch12):** ODBC "Step N" headings merging onto config lines.
- **02-introduction (ch1):** widow lead-in before list; one run-on; quiz list nesting.
- **Front matter:** duplicate Roman folios (TOC i–vi then i–iii); resolve ISBN (note now stripped).

## Clean
Chapters 6 (WebRTC) and 7 (SIP trunking) and most of the book are well-typeset: code wraps,
running heads/folios correct, figures within margins. Defects cluster in the OCR/PT-imported
legacy + lab chapters.
