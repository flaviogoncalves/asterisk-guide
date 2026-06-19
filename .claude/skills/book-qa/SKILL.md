---
name: book-qa
description: Ruthlessly critical QA of the book — BOTH the rendered layout (page-by-page PDF/EPUB inspection for bleed/overflow/figure/heading/widow defects) AND the content/editorial substance (dead or legacy tech like chan_sip/X-Lite/Zoiper/MeetMe/Macro outside the Legacy chapter, outdated facts, broken or missing cross-references, dead/placeholder links, brand/product inconsistency, and practical gaps such as "where does the student download the SipPulse Softphone?"). Produces a prioritized fix list. Use for a final pre-publish review and after any content or layout change. Be the harsh reviewer who finds the main defects before the reader does.
---

# Book QA — find the defects before the reader does

Two ways the book can be wrong, and this skill hunts both:

1. **Layout** — the source can be perfect and the *rendered* book still wrong: tables overflow,
   code bleeds off the edge, a caption collides with art, a heading is stranded. You only catch
   these by **looking at every page of the actual PDF**.
2. **Content / editorial** — the page can render perfectly and still be *wrong* or *useless*: a
   dead product (X-Lite, Zoiper) the reader is told to download, `chan_sip` taught as current, a
   reference to a figure that was deleted, a lab that never says **where to get the softphone**, a
   contradiction between two chapters. You catch these by **reading the content critically** and
   checking every claim, link, and cross-reference.

Be **adversarial**. Assume earlier reviewers missed things (they do). Your job is to find the
**main, embarrassing defects a customer would hit** — not to be polite. Prefer false alarms you
can dismiss over real defects you let ship.

## Procedure — run BOTH passes

### Pass A — Content & editorial (read the source critically)

Do this first; content defects are the ones that embarrass. Work over `src/chapters/*.md` (and
`labs/`, `slides/` when in scope), fanning out per chapter across parallel reviewers.

1. **Grep the dead-term blocklist** (below) across the source. Every hit outside the *Legacy
   Channels* / *Migration* chapters is a defect.
2. **Read each chapter critically** against the Content checklist below — facts, coherence,
   cross-references, links, and **practical completeness** (can a student actually do this?).
3. **Resolve every reference and link.** A `![...](../images/X.png)` must point at a file that
   exists; a "see Chapter N / the figure above / the next section" must actually be there; every
   URL must resolve (and not be a placeholder). Verify config/CLI against the Asterisk 22 lab.
4. **Record each defect**: `chapter | line/section | category | severity | what | fix`.

### Pass B — Layout (look at every rendered page)

1. **Build the final PDF** (`bash book/build.sh`, or download the CI artifact) and get the page
   count (`mdls -name kMDItemNumberOfPages build/asterisk-guide.pdf`, or `pdfinfo`).
2. **Inspect every page.** The Read tool renders PDF pages as images — `Read(pdf, pages="N")`
   or a small range `"N-M"` (≤ 20 pages/call). For a long book, **fan out**: split the page
   range across parallel reviewers (e.g. ~15–20 pages each) so the whole book is covered.
   Note the running-head folio (book page) vs the PDF page — report **both**.
3. **Run the Layout checklist on each page** (below).
4. **Record each defect** in a table: `book pg | PDF pg | category | severity | what | fix`.

**Then:** aggregate + dedupe; separate **systemic** defects (one root cause across many pages/
chapters — fix once in `book/template/interior.tex`, the build, or a global find-replace) from
**one-off** defects; fix systemic first, then one-offs; rebuild; re-review only what changed.

## Content & editorial defect checklist (be ruthless)

- **Dead / legacy tech presented as current (blocker).** Anything from the blocklist used as the
  recommended/modern way *outside* the Legacy Channels and Migration chapters: `chan_sip`,
  `sip.conf`, `SIP/…` dialstrings, `sip show …`, **X-Lite / Xlite, Zoiper, MicroSIP, Linphone**
  and other named third-party softphones, **AsteriskNOW**, **MeetMe**, **Macro()**, `DBdel`,
  `LookupBlacklist`, Monitor (use MixMonitor), `chan_skinny`/`chan_mgcp`/`chan_h323` as if
  present, Digium (where it should be Sangoma), old version numbers (anything that should be 22).
- **Wrong/outdated facts.** Removed or renamed apps/options/CLI shown as working; defaults that
  changed; capacities/prices/dates that are stale. Verify against `docs.asterisk.org` and the lab.
- **Brand / product consistency.** The only softphone the book installs is the **SipPulse
  Softphone** — used consistently, named consistently, with the **download source given the first
  time it's introduced** (`https://www.sippulse.com/produtos/softphone`). Flag every place that
  introduces a tool/package/softphone/cert **without telling the reader where to get it** ("where
  does the student download this?"). OpenSIPS not Kamailio (brand rule).
- **Practical completeness (a student must be able to follow it).** Labs and step-by-steps need:
  prerequisites, exact commands, **credentials/links present** (no "<your-password>" with no
  source), the download/where-to-get-it for every tool, and an expected result. A step that says
  "register your softphone" without saying which one, where to get it, and what to register to is
  a defect.
- **Coherence & cross-references.** No contradictions between chapters; every "see Chapter N / the
  figure above / the table below / the next section" actually resolves; **no orphaned reference to
  a figure, section, or example that was deleted**; quiz questions match the chapter and the
  answer key matches the questions.
- **Relevance.** No dated tangents, dead links, or content that doesn't serve the chapter's stated
  objective; nothing that reads as leftover from the 1st edition.
- **Editorial scaffolding leaks.** No `[2nd-ed note]`, `TODO`, `XXX`, `<placeholder>`, lorem text,
  or "(verify this)" left in the prose.
- **Links.** Every URL resolves and isn't a placeholder/example domain presented as real; product
  and download links point where they should.

### Dead-term sweep (run first, it's cheap and catches the embarrassing ones)

```bash
# Every hit OUTSIDE the Legacy Channels / Migration chapters is a defect:
grep -rinE 'chan_sip|sip\.conf|SIP/[0-9]|sip show|x-?lite|zoiper|microsip|linphone|asterisknow|meetme|Macro\(|DBdel|LookupBlacklist|Kamailio' \
  src/chapters/ slides/ labs/ | grep -vE '10-legacy-channels|10a-migration'

# Tools/softphones introduced — confirm each says WHERE to get it (download URL / install cmd):
grep -rinE 'download|install|register (your|the) softphone|configure (a|the) softphone' src/chapters/ labs/
```

Then read around each hit: is it legitimate (a "removed in 21" mention, the Legacy chapter) or a
real defect (taught as current, a dead product, a tool with no download source)?

## Layout defect checklist (per page)

- **Bleed (blocker):** any text, inline code, **table**, code block, or image crossing the text
  block into the margin — especially off the **right** or **bottom**. Code must wrap; tables
  must fit the measure.
- **Tables:** fit the text width; no column or long-`code`-token overflow; readable font; nothing
  clipped; header repeats if the table breaks across pages.
- **Figures:** inside the margins; not stretched/blurry; legible at print size; **has a proper
  caption rendered as text (below the figure), not only labels baked into the image**, and the
  caption doesn't overlap the artwork; figure + caption not split across a page break; consistent
  sizing with sibling figures.
- **Paragraphs:** no excessively long run-on paragraph (split into shorter ones; common in
  PDF/OCR-imported text); sensible inter-paragraph spacing.
- **Headings:** no heading orphaned at the very bottom of a page (no following text); consistent
  style and numbering; chapter openers correct.
- **Widows/orphans:** no single stranded line of a paragraph at the top/bottom of a page.
- **Page flow:** no near-empty "overflow" pages; sensible breaks; running heads + folios present
  and correct; no duplicated/missing page numbers.
- **Code blocks:** boxed, wrapped (continuation marker on wrapped lines), and breaking cleanly
  across pages (not clipped at the bottom edge).
- **Front/back matter:** title page, TOC (entries match, page numbers right), part dividers.

## Common systemic fixes (one root cause → fix once)

- **Tables bleeding:** long unbreakable `inline code` in cells overflows. Reduce table font
  (`\AtBeginEnvironment{longtable}{\footnotesize}` via etoolbox), allow `\texttt` to break, or
  shorten/restructure the offending cells. Verify wide tables fit the measure.
- **Code bleeding right:** ensure `fvextra` `breaklines`/`breakanywhere` is on and the code font
  is small enough.
- **Figures without captions:** enable pandoc implicit figures so the alt-text renders as a real
  caption (or add explicit captions); keep captions below the image.
- **Run-on paragraphs:** split at the source (these are content edits, not a template change).

## Output

A single prioritized report covering **both passes**: counts by severity; the **systemic**
root-causes up top (a dead product used book-wide, a missing download source repeated in many
labs, a template bleed) each with its one global fix; then the per-defect list. Each row:
location (chapter + line for content, book folio + PDF page for layout), category, severity,
the element, and the **concrete fix**. Lead with the blockers — the defects a customer would
hit and complain about. After fixing, re-run the relevant pass and confirm each defect is gone.

## Guardrails

- Run **both** passes: content/editorial (the Markdown source + cross-refs + links) **and**
  layout (the rendered PDF/EPUB). Neither alone is enough.
- Be **critical, not polite** — surface the main defects plainly; a missed dead product or a
  lab with no download link is worse than an over-eager flag.
- For layout defects report **both** page numbers (book folio + PDF page); for content defects
  report the **chapter + line/section** so it can be found again.
- Every defect needs a **concrete fix**, not just "looks off" or "feels outdated".
- Verify technical claims, config, and CLI against `docs.asterisk.org` and the Asterisk 22 lab —
  don't assume. Prefer global/systemic fixes over hand-tuning one page in a way that breaks reflow.
