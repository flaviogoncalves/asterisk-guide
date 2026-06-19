---
name: book-qa
description: Page-by-page visual QA of the rendered book PDF (and EPUB). Render every page and inspect it for layout defects — text/tables/code/figures bleeding past the margins, tables that overflow, figure-caption problems, over-long run-on paragraphs, orphan headings, widows/orphans, bad page breaks, low-res figures — then produce a prioritized, page-referenced fix list. Use for a final pre-print review and after any layout change.
---

# Book QA — look at every page of the rendered book

The source can be perfect and the *rendered* book still be wrong: tables overflow, code
bleeds off the edge, a figure caption collides with the image, a paragraph runs half a page,
a heading is stranded at the bottom. The only way to catch these is to **look at every page of
the actual PDF** — what the reader sees. This skill does that systematically and turns it into
a fix list.

## Procedure

1. **Build the final PDF** (`bash book/build.sh`, or download the CI artifact) and get the page
   count (`mdls -name kMDItemNumberOfPages build/asterisk-guide.pdf`, or `pdfinfo`).
2. **Inspect every page.** The Read tool renders PDF pages as images — `Read(pdf, pages="N")`
   or a small range `"N-M"` (≤ 20 pages/call). For a long book, **fan out**: split the page
   range across parallel reviewers (e.g. ~15–20 pages each) so the whole book is covered.
   Note the running-head folio (book page) vs the PDF page — report **both**.
3. **Run the defect checklist on each page** (below).
4. **Record each defect** in a table: `book pg | PDF pg | category | severity | what | fix`.
5. **Aggregate + dedupe.** Separate **systemic** defects (one root cause across many pages — fix
   once in `book/template/interior.tex` or the build) from **one-off** content defects (fix in
   the chapter source / re-render a figure).
6. **Fix systemic first, then one-offs; rebuild; re-review only the affected pages.**

## Defect checklist (per page)

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

A single prioritized report: counts by severity, the systemic root-causes up top with their one
global fix each, then the per-page one-off list. Each row: book page, PDF page, category,
severity, the element, and the concrete fix. After fixing, re-run QA on the changed pages and
confirm the defect is gone.

## Guardrails

- Review the **final rendered PDF** (and the EPUB for its own issues), not the Markdown source.
- Always report **both** page numbers (book folio + PDF page) so a defect can be found again.
- Every defect needs a concrete fix, not just "looks off".
- Don't hand-tune one page in a way that breaks reflow — prefer global/systemic fixes.
