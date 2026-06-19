---
name: kdp-formatter
description: Format a book for Amazon KDP print-on-demand (paperback) and Kindle eBook to spec. Encodes KDP's real requirements — trim sizes, interior margins/gutter by page count, bleed, and the SEPARATE wraparound cover (back+spine+front) with correct spine width — and the build workflow. Use to set up or fix a book's print interior and cover so KDP accepts it and it's affordable to produce.
---

# KDP book formatter (paperback + Kindle)

Format the book so **KDP accepts it on the first upload** and it's **cheap to print**. KDP
takes two separate things for a paperback: an **interior PDF** (no cover in it) and a
**wraparound cover PDF** (back + spine + front). The Kindle eBook is a separate EPUB with an
embedded cover image. Get the numbers exactly right — KDP rejects out-of-spec files.

> Sources: KDP [Set Trim Size, Bleed, and Margins](https://kdp.amazon.com/en_US/help/topic/GVBQ3CMEQW3W2VL6),
> [Paperback Submission Guidelines](https://kdp.amazon.com/en_US/help/topic/G201857950),
> [Create a Paperback Cover](https://kdp.amazon.com/en_US/help/topic/G201953020),
> [KDP Cover Calculator](https://kdp.amazon.com/cover-calculator). Verify current values there before publishing.

## 1. Choose trim + paper (cost vs. readability)

- **Trim sizes:** standard list includes 5×8, 5.5×8.5, **6×9** (most common, cheapest, all
  marketplaces), 7×10, 7.44×9.69, **7.5×9.25**, 8×10, 8.5×11. Custom allowed: width 4–8.5",
  height 6–11.69".
- **Pick for the content.** Prose → 6×9. **Code/diagram-heavy technical book → a wider trim
  (7.5×9.25)** so code lines and figures aren't cramped or wrapped to death. Wider trim also
  means *fewer pages*, which offsets cost.
- **Paper/ink:** black ink on **white** paper (higher contrast for code/screenshots; spine
  factor 0.002252"/page) or cream (0.0025"/page). White is the right default for technical books.
- **Affordability:** B&W print cost ≈ a fixed fee + a flat per-page cost, so the big levers are
  page count and trim. A wider trim with fewer pages is often as cheap as 6×9 and far more readable.

## 2. Interior PDF (no cover inside)

- **Margins.** Outside (top/bottom/outer) **≥ 0.25"** without bleed (use ~0.5" for a nicer
  block). **Gutter (inside) by page count** — set it from the *final* page count:

  | Pages | Gutter (inside) |
  |---|---|
  | 24–150 | 0.375" |
  | 151–300 | 0.5" |
  | 301–500 | 0.625" |
  | 501–700 | 0.75" |
  | 701–828 | 0.875" |

  A **larger** gutter than required is always accepted, so a safe shortcut before you know the
  final count is to set the gutter for the next tier up (e.g. 0.75" covers anything ≤700 pages).
- **Bleed:** only if images run to the edge. This book has no full-bleed art → **no-bleed**
  interior (simpler, and outside margin min drops to 0.25").
- **Fonts must be embedded** (xelatex embeds them). Output a normal PDF (PDF/X not required).
- **Pandoc/LaTeX wiring (this repo):** set `geometry` in `book/metadata.yaml` to the trim with
  `inner`(gutter)/`outer`/`top`/`bottom`; **do not** embed the cover in the interior — the
  paperback interior has a title page + content only. Code blocks must wrap (`fvextra`
  `breaklines`) so nothing bleeds past the text block.

## 3. Page count → then the cover

You can't size the spine until the interior's **final page count** is known. So the order is:
**build the interior → read its page count → set the gutter tier → size the cover.**

## 4. Wraparound cover PDF (separate file)

- **One flat image: back cover | spine | front cover**, left to right.
- **Spine width** = page count × paper factor (white 0.002252"/pg, cream 0.0025"/pg).
  Spine **text only if ≥ 79 pages** (otherwise the spine is too thin; leave it blank/solid).
- **Full cover size:**
  - width = 0.125" (bleed) + back width + spine width + front width + 0.125" (bleed),
    where back width = front width = trim width.
  - height = 0.125" + trim height + 0.125".
- **Bleed 0.125" on all four outer edges; 300 DPI minimum.** Keep text/logos ≥ 0.25" inside the
  trim edges and ≥ 0.0625" off the spine folds (the "safe zone").
- **Best practice:** use the **KDP Cover Template Generator** (enter trim + page count + paper) —
  it returns a PNG/PDF template with exact dimensions and fold lines. Build the artwork on that
  template so the math is guaranteed. The per-page factor above is for a first draft only.

## 5. Kindle eBook (separate)

- Reflowable **EPUB** with an embedded **cover image** (`cover-image:` in metadata) — portrait,
  ~1.6:1, ≥ 1600 px tall. No trim/spine/bleed concepts apply to the eBook.

## 6. Validate before publishing

- Open the interior PDF in KDP's **Print Previewer** (or check: trim size correct, gutter on the
  inside edge, nothing in the margins, fonts embedded, no bleed-overflow).
- Build the cover on the KDP template; confirm spine text fits and bleed is filled.
- EPUB: validate (no XHTML errors), cover shows, links work.

## Guardrails
- Interior PDF and cover are **separate files**; never put the cover inside the interior PDF.
- Re-derive the spine + gutter whenever the page count changes (new chapters, font, trim).
- Keep numbers sourced from KDP's current help/calculator — don't hardcode stale values.
- Don't upscale low-res art to hit 300 DPI; regenerate it (see the `illustrator` skill).
