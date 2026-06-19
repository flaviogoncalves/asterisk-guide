---
name: chapter-review
description: Review and polish one chapter of Complete Asterisk Training (2nd ed., Asterisk 22 LTS) — technical accuracy lab-verified against the Docker lab, modernization completeness, DOCX image harvest, voip.school branding, prose/structure, and a rendered-PDF check. Use when the user says "review chapter N", "do chapter N", or is working chapter-by-chapter on the book.
---

# Chapter review

Systematically review one chapter of *Complete Asterisk Training* (2nd edition,
Asterisk 22 LTS) to a publishable bar. Work on **one chapter at a time** and report
before moving on.

## Inputs

- Chapter file: `src/chapters/NN-slug.md` (the argument; accept a number or filename).
- The plan & glossary: `PLAN-2ND-EDITION.md`, `CONTEXT.md`, `docs/adr/`.
- The Asterisk 22 lab: `lab/` (use `./lab/lab.sh` to boot/verify).
- The original source with good figures: `~/Downloads/AstV16A.docx` (DOCX —
  better images than the PDF extraction, including EMF/WMF vector diagrams).

## Procedure

Do these in order. Make grounded edits; never invent Asterisk behavior — verify it.

1. **Read the whole chapter** and note its structure (one H1, `##` sections), every
   code block, every figure, and every `> **[2nd-ed note]**` marker.

2. **Technical accuracy (lab-verified).** For each config/CLI example:
   - Boot the lab if needed (`./lab/lab.sh up`).
   - Apply the example's config in the lab (or a scratch copy) and run the commands.
   - Replace invented/placeholder CLI output with **real captured Asterisk 22 output**.
   - Fix anything that does not behave as the text claims. chan_sip is gone — every
     SIP example must be PJSIP (`pjsip.conf`, `PJSIP/...`, `pjsip show ...`).

3. **Modernization completeness.** Confirm: version refs say 22; no `Macro()`
   (use GoSub); MeetMe→ConfBridge; Digium→Sangoma where it means the steward;
   removed/renamed apps and CLI commands corrected; Opus/G.729 are free.

4. **Resolve `[2nd-ed note]` markers.** For each: either fix it now (and delete the
   note) or, if it needs an author decision (ISBN, prices, a product URL), tighten it
   to a one-line actionable note and keep it. Report the ones left for the author.

5. **Images (DOCX harvest).** The PDF-extracted figures are low quality/broken.
   Replace this chapter's figures with the matching images from the DOCX:
   - Extract DOCX media once: `pandoc ~/Downloads/AstV16A.docx -t gfm \
     --extract-media=src/docx-media -o /tmp/docx.md` (idempotent).
   - Map the DOCX images (document order) to this chapter's figures and update the
     `![...](../images/...)` references to the good files.
   - EMF/WMF vector diagrams need conversion to PNG/SVG (LibreOffice headless:
     `soffice --headless --convert-to png`). If no converter is installed, leave a
     one-line `[2nd-ed note]` listing the figures still needing conversion.

6. **Branding.** No `asteriskguide.com`, Udemy, or GitHub `AsteriskTraining` links —
   use **voip.school** / **VoIP School Blackbelt** / `flavio@voip.school`.

7. **Prose & structure.** Fix OCR-era typos and split run-on paragraphs that came
   from PDF extraction. Ensure exactly one H1, sane heading levels, **balanced code
   fences** (count of ``` lines is even), and rebuild any flattened tables as real
   Markdown tables. Keep the author's voice — edit, don't rewrite.

8. **Render check.** Build and look at the chapter in the PDF:
   - `bash book/build.sh` (needs pandoc + xelatex), or push and let CI build.
   - Read the chapter's pages from `build/complete-asterisk-training.pdf` (or the CI
     artifact) and visually confirm headings, code, figures, and tables look right.

9. **Commit** on a branch or `main` with a clear message, push, and confirm CI is green.

10. **Report**: a short bullet list of what changed, which examples were lab-verified,
    which figures were swapped, and every `[2nd-ed note]` left for the author.

## Guardrails

- One chapter per run; stop and report at the end.
- Quote real lab output — do not fabricate CLI results.
- Preserve all figures (swap, don't drop) and all code unless it is provably wrong.
- Keep Markdown Pandoc-clean (`commonmark_x`): `{.unnumbered}` only on part dividers,
  raw LaTeX only in the front matter.
