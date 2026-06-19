#!/usr/bin/env bash
# Build the book in all three formats from the single Markdown source.
# Outputs land in build/ and are what CI uploads/releases.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/src/chapters"
OUT="$ROOT/build"
META="$ROOT/book/metadata.yaml"
NAME="complete-asterisk-training"

mkdir -p "$OUT"

# Chapter order = numeric filename order (00-front-matter, 01-…, … 16-…).
# After the restructure this becomes an explicit order file; numeric sort holds for now.
mapfile -t CHAPTERS < <(ls "$SRC"/*.md | sort)
echo "Assembling ${#CHAPTERS[@]} chapters:"
printf '  %s\n' "${CHAPTERS[@]##*/}"

# commonmark_x is the GFM superset that also supports the {.unnumbered} heading
# attribute used on the Part divider pages (plain gfm rejects header_attributes).
# --resource-path lets Pandoc resolve the chapters' ../images/ figure links.
COMMON=( --from=commonmark_x
         --metadata-file="$META"
         --resource-path="$SRC"
         --toc --toc-depth=2 )

echo "→ EPUB"
pandoc "${COMMON[@]}" -o "$OUT/$NAME.epub" "${CHAPTERS[@]}"

# Interior typesetting (fonts, headings, running heads, boxed code, callouts).
# xelatex-only — applied to the LaTeX/PDF outputs, not the EPUB.
INTERIOR="$ROOT/book/template/interior.tex"

echo "→ LaTeX"
pandoc "${COMMON[@]}" --standalone --include-in-header="$INTERIOR" -o "$OUT/$NAME.tex" "${CHAPTERS[@]}"

echo "→ PDF (xelatex)"
pandoc "${COMMON[@]}" --pdf-engine=xelatex --include-in-header="$INTERIOR" -o "$OUT/$NAME.pdf" "${CHAPTERS[@]}"

echo "Done. Artifacts in $OUT:"
ls -la "$OUT"
