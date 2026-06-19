#!/usr/bin/env bash
# Build the book from the single Markdown source.
#   asterisk-guide-sponsored[-LANG].{pdf,epub}  — SPONSORED, every language: the ONLY GitHub downloads
#   asterisk-guide.{pdf,epub,tex}               — CLEAN, English only: KDP/Kindle interior (NOT published)
# Usage:  book/build.sh [both|clean|sponsored]            (default: both)
#         BOOK_LANG=zh book/build.sh                      # Chinese edition (i18n/zh/chapters)
# Translated chapters/sponsor page come from i18n/<lang>/ (book/translate/translate.py);
# figures stay English (src/images); hi/zh/ja PDFs add a Devanagari/CJK font header.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build"
INTERIOR="$ROOT/book/template/interior.tex"
mkdir -p "$OUT"

# Language selection: en (default) or a translated edition under i18n/<lang>/.
# Supported: en pt es fr de it hi zh ja.  hi/zh/ja add a Devanagari/CJK font header.
BOOK_LANG="${BOOK_LANG:-en}"
FONTHDR=""
case "$BOOK_LANG" in
  en) SRC="$ROOT/src/chapters"; META="$ROOT/book/metadata.yaml"; SUF="" ;;
  pt|es|fr|de|it|hi|zh|ja)
      SRC="$ROOT/i18n/$BOOK_LANG/chapters"
      META="$ROOT/book/metadata-$BOOK_LANG.yaml"
      SUF="-$BOOK_LANG" ;;
  *)  echo "Unknown BOOK_LANG '$BOOK_LANG' (use en|pt|es|fr|de|it|hi|zh|ja)" >&2; exit 1 ;;
esac
case "$BOOK_LANG" in hi|zh|ja) FONTHDR="$ROOT/book/template/fonts-$BOOK_LANG.tex" ;; esac
# Sponsor page: English source, or the translated one for a translated edition.
SPONSORS="$ROOT/book/sponsors/sponsors.md"
[ "$BOOK_LANG" != "en" ] && SPONSORS="$ROOT/i18n/$BOOK_LANG/sponsors.md"
[ -d "$SRC" ] || { echo "No chapters at $SRC — run book/translate/translate.py --lang $BOOK_LANG first" >&2; exit 1; }

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
  if [ "${PDF_ONLY:-0}" != "1" ]; then          # PDF_ONLY=1 → skip the EPUB
    echo "→ $name : EPUB"
    pandoc "${COMMON[@]}" "${xf[@]}" -o "$OUT/$name.epub" "$@"
  fi
  if [ "${EPUB_ONLY:-0}" != "1" ]; then         # EPUB_ONLY=1 → skip the PDF
    echo "→ $name : PDF (xelatex)"
    local fh=(); [ -n "${FONTHDR:-}" ] && fh=( --include-in-header="$FONTHDR" )   # CJK/Devanagari
    pandoc "${COMMON[@]}" "${xf[@]}" --pdf-engine=xelatex \
      --include-in-header="$INTERIOR" "${fh[@]}" -o "$OUT/$name.pdf" "$@"
  fi
}

want="${1:-both}"

# CLEAN, ad-free — ENGLISH ONLY: the KDP paperback interior (PDF + LaTeX) and an ad-free EPUB.
# NOT published on GitHub — only the sponsored editions are distributed there, so nobody can
# grab an ad-free copy next to the sponsored one.
if [ "$want" != "sponsored" ] && [ "$BOOK_LANG" = "en" ]; then
  build_variant "asterisk-guide" "${CHAPTERS[@]}"        # clean PDF + EPUB (KDP / Kindle)
  echo "→ asterisk-guide : LaTeX"
  pandoc "${COMMON[@]}" --standalone --include-in-header="$INTERIOR" -o "$OUT/asterisk-guide.tex" "${CHAPTERS[@]}"
fi

# SPONSORED PDF + EPUB for EVERY language — the ONLY editions distributed on GitHub.
# Translated sponsor page ($SPONSORS) + localized per-chapter credits.
if [ "$want" != "clean" ]; then
  EXTRA_FILTER="$ROOT/book/inject-sponsors.lua" \
    build_variant "asterisk-guide-sponsored$SUF" "${SPONSORED[@]}"
fi

echo "Done. Artifacts in $OUT:"
ls -la "$OUT"
