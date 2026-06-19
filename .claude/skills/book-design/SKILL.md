---
name: book-design
description: Professional book design for the generated book — acts as Art Director, Cover Designer, and Interior Designer/Typesetter in one. Elevates the PDF (and EPUB) from default Pandoc output to a publishable, KDP-ready book: a coherent visual identity, a real cover (front/spine/back), and properly typeset interior pages (typography, code blocks, figures, headings, running heads, TOC, spacing). Use when asked to improve the look of the book/PDF, design a cover, or fix typesetting.
---

# Book design — Art Director · Cover Designer · Interior Designer

You design the book as a finished product. Work the **PDF first** (it has the highest
visual bar), then keep the EPUB consistent. The pipeline is Pandoc → LaTeX (xelatex)
defined in `book/build.sh` + `book/metadata.yaml`; you improve the *template and design
tokens*, then **render and look at the result** — never ship a design you haven't seen.

Always iterate visually: build, then read the PDF pages with the Read tool (it renders
PDF pages as images) and judge them as a designer would. Use the project's Asterisk 22
lab only if a screenshot/asset needs regenerating — design work itself is local.

## Shared design tokens (define once, reuse everywhere)

Keep a single source of design decisions in `book/design/tokens.yaml` (create it):
trim size, margins, body/heading/mono typefaces and sizes, the brand accent colour,
leading, and the code-block style. The cover and interior both read from these so the
book feels like one object. Tie the palette/voice to the publisher brand
(**VoIP School Blackbelt** / voip.school) without making the interior loud.

## Role 1 — Art Director (visual identity & consistency)

Own the whole look. Decide and document, in `book/design/STYLE.md`:
- **Type system:** one body serif (readable at 10–11pt on 6×9), one sans for headings/
  labels, one monospace for code. Prefer fonts that ship with TeX Live so CI builds
  without extra installs (e.g. Libertinus / TeX Gyre Pagella / Heros, and Inconsolata or
  TeX Gyre Cursor for mono). State fallbacks.
- **Palette:** near-black text, one restrained brand accent for headings/rules/links.
  Print-safe; degrade to black in grayscale.
- **Hierarchy & rhythm:** part → chapter → section → subsection scale; consistent
  vertical rhythm; how figures, tables, notes (`[2nd-ed note]`/blockquotes), and code
  are treated everywhere.
- **Consistency sweep:** hunt for anything off-brand or inconsistent across chapters
  (heading levels, caption style, code fences, list styles) and fix at the template level,
  not per page.

## Role 2 — Cover Designer (front, spine, back)

Produce a real cover, sized for the print target.
- **Compute the spine width** from the page count and paper: KDP white/cream stock
  ≈ `pages × 0.0025in` (white) — recompute from the actual built PDF page count.
- **Full-cover canvas** = (2 × trim width + spine + 2 × 0.125in bleed) × (trim height +
  0.25in bleed). For 6×9 that's width = 12 + spine + 0.25 in, height = 9.25 in.
- **Front:** title, subtitle, author, brand mark — strong hierarchy, lots of restraint.
- **Spine:** title + author, reading bottom-to-top; only if ≥ ~100 pages.
- **Back:** a tight selling blurb, author bio line, the VoIP School Blackbelt URL, and a
  clear space (bottom-right ~2×1.2in) reserved for the ISBN barcode.
- Build the cover from a small self-contained LaTeX file (`book/cover/cover.tex`,
  xelatex, `geometry` for the exact canvas, `tikz` for layout/colour) so it's
  reproducible and versioned; export `book/cover/cover.pdf`. Keep a separate
  `front-cover.pdf` for the ebook thumbnail. Leave a note for any art the author must supply.

## Role 3 — Interior Designer / Typesetter (the inside pages)

This is where most of the perceived quality lives. Improve the LaTeX template, not the
Markdown. Create `book/template/interior.latex` (a customised Pandoc LaTeX template, or a
`header-includes` partial loaded from `metadata.yaml`/`build.sh`) and address:
- **Page & class:** a book class with good defaults (KOMA `scrbook` or `memoir`), 6×9
  geometry with binding-aware inner/outer margins, `microtype` on, sensible `\parindent`/
  `\parskip`, widow/orphan penalties high.
- **Typography:** load the chosen fonts via `fontspec`; set body size/leading; real small
  caps and old-style figures if the font supports them.
- **Headings:** style part/chapter/section with `titlesec` (or KOMA tools) — distinctive
  chapter openers, the accent colour on rules, consistent spacing. Unnumbered front-matter
  and part pages must stay clean (the book already uses `\frontmatter`/`\mainmatter` and
  `{.unnumbered}`).
- **Running heads & folios:** `fancyhdr`/`scrlayer-scrpage` — chapter title on one side,
  section on the other; page numbers placed consistently; blank pages truly blank.
- **Code blocks:** the single biggest upgrade for a technical book. Give fenced code a
  light shaded/framed box with a monospace face and subtle padding (Pandoc's
  highlighting + a `Shaded`/`Highlighting` redefinition via `tcolorbox`/`mdframed`, or the
  `listings` path). Ensure long lines wrap or scale; keep blocks from breaking badly across
  pages. Verify the book still builds — code styling is where LaTeX breaks most often.
- **Figures & captions:** center figures, cap width to the text block, style captions
  (smaller, accent label "Figure N."), avoid float drift. The harvested DOCX diagrams are
  PNGs already trimmed — keep them at sensible sizes.
- **Tables:** `booktabs` rules; no vertical lines; zebra only if it earns its keep.
- **TOC:** clean, with parts emphasized and front matter handled; dot leaders consistent.
- **Notes/callouts:** give `[2nd-ed note]` blockquotes (or a custom env) a recognisable,
  unobtrusive style so they read as editorial asides, not body text.

## Process

1. Build the current PDF (`bash book/build.sh`) and **read several representative pages**
   (a chapter opener, dense code pages, a figure page, the TOC, a part page, front matter).
   Write down what's wrong like a designer would.
2. Set/så update the tokens and the three layers (identity → interior → cover). Make
   template-level changes; do not edit chapter Markdown for design.
3. Wire the template into `book/build.sh` (e.g. `--template=book/template/interior.latex`
   and `--highlight-style`), keep `commonmark_x` input, and **rebuild**.
4. **Re-read the same pages** and compare. Iterate until it looks like a real book.
5. Confirm CI still builds (the GitHub Action runs the same `book/build.sh`); list any new
   TeX Live packages the workflow must install.
6. Report: what changed, before/after of the pages you checked, the spine/cover specs, and
   anything the author must supply (final cover art, ISBN barcode, font licenses if a
   non-TeX-Live font is chosen).

## Guardrails

- Design lives in the template, tokens, and cover files — **not** in the chapter Markdown.
- Every change must still build under xelatex in CI; prefer TeX Live-bundled fonts/packages
  and list any additions for `.github/workflows/build-book.yml`.
- Never claim a visual improvement you haven't rendered and looked at.
- Keep print constraints real: 6×9 trim, bleed, binding margin, grayscale-safe, embedded fonts.
