#!/usr/bin/env bash
# Build the book from the single Markdown source, in two variants:
#   asterisk-guide            — CLEAN (no sponsor page); for the Amazon/KDP paperback & local use
#   asterisk-guide-sponsored  — SPONSORED (sponsor page in the front matter); for the free EPUB/PDF
# Usage: book/build.sh [both|clean|sponsored]   (default: both)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/src/chapters"
OUT="$ROOT/build"
META="$ROOT/book/metadata.yaml"
SPONSORS="$ROOT/book/sponsors/sponsors.md"
INTERIOR="$ROOT/book/template/interior.tex"
mkdir -p "$OUT"

# Chapter order = numeric filename order. (portable: macOS bash 3.2 has no `mapfile`)
CHAPTERS=()
while IFS= read -r _f; do CHAPTERS+=("$_f"); done < <(ls "$SRC"/*.md | sort)

# Sponsored = the same chapters with the sponsor page inserted right after the front matter.
SPONSORED=()
for _f in "${CHAPTERS[@]}"; do
  SPONSORED+=("$_f")
  case "$_f" in *00-front-matter.md) SPONSORED+=("$SPONSORS") ;; esac
done

echo "Assembling ${#CHAPTERS[@]} chapters."

# commonmark_x is the GFM superset supporting {.unnumbered} headings and {width=} image attrs.
COMMON=( --from=commonmark_x
         --metadata-file="$META"
         --resource-path="$SRC:$ROOT:$ROOT/src/images:$ROOT/book/sponsors"
         --lua-filter="$ROOT/book/strip-notes.lua"
         --lua-filter="$ROOT/book/wrap-tables.lua"
         --toc --toc-depth=2 )

build_variant() {            # $1 = output name; remaining args = source files in order
  local name="$1"; shift
  local xf=()
  [ -n "${EXTRA_FILTER:-}" ] && xf=( --lua-filter="$EXTRA_FILTER" )   # per-chapter sponsor credits
  echo "→ $name : EPUB"
  pandoc "${COMMON[@]}" "${xf[@]}" -o "$OUT/$name.epub" "$@"
  echo "→ $name : PDF (xelatex)"
  pandoc "${COMMON[@]}" "${xf[@]}" --pdf-engine=xelatex --include-in-header="$INTERIOR" -o "$OUT/$name.pdf" "$@"
}

want="${1:-both}"

if [ "$want" != "sponsored" ]; then
  build_variant "asterisk-guide" "${CHAPTERS[@]}"
  echo "→ asterisk-guide : LaTeX"
  pandoc "${COMMON[@]}" --standalone --include-in-header="$INTERIOR" -o "$OUT/asterisk-guide.tex" "${CHAPTERS[@]}"
fi

if [ "$want" != "clean" ]; then
  EXTRA_FILTER="$ROOT/book/inject-sponsors.lua" build_variant "asterisk-guide-sponsored" "${SPONSORED[@]}"
fi

echo "Done. Artifacts in $OUT:"
ls -la "$OUT"
