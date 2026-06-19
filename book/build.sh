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

# --resource-path lets Pandoc resolve the chapters' ../images/ figure links.
# +header_attributes enables {.unnumbered} on the Part divider pages.
COMMON=( --from=gfm+header_attributes
         --metadata-file="$META"
         --resource-path="$SRC"
         --toc --toc-depth=2 )

echo "→ EPUB"
pandoc "${COMMON[@]}" -o "$OUT/$NAME.epub" "${CHAPTERS[@]}"

echo "→ LaTeX"
pandoc "${COMMON[@]}" --standalone -o "$OUT/$NAME.tex" "${CHAPTERS[@]}"

echo "→ PDF (xelatex)"
pandoc "${COMMON[@]}" --pdf-engine=xelatex -o "$OUT/$NAME.pdf" "${CHAPTERS[@]}"

echo "Done. Artifacts in $OUT:"
ls -la "$OUT"
