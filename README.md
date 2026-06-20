# Asterisk Guide — 2nd Edition

[![Build book](../../actions/workflows/build-book.yml/badge.svg)](../../actions/workflows/build-book.yml)

The open source of *Asterisk Guide* by **Flavio E. Gonçalves** — a systematic guide
to building an IP PBX with **Asterisk 22 LTS**. The Markdown source and the lab are free; the
**paper book** (Amazon KDP) and the **VoIP School Blackbelt** training are the supported products.

## Download the book

The book is **free to download**. Tagged releases (`v*`) attach:

- **`asterisk-guide-sponsored.pdf` and `.epub`** — the free, **sponsored English** editions.
  This is the **verified, current** download. Sponsored by **[SipPulse](https://www.sippulse.com)**
  — the SIP authority behind **200+ operators** — plus per-lab sponsors.

Only the sponsored editions are published here. The clean, ad-free interior
(`asterisk-guide.pdf/.epub/.tex`) is built for the paid Amazon paperback/Kindle and is **not**
distributed on GitHub — so nobody picks an ad-free copy sitting next to the sponsored one.

Grab them from **Releases**, or build any branch from **Actions → latest run → Artifacts**.

### Translated editions (preview — off by default)

The book also builds in **8 more languages** (pt, es, fr, de, it, hi, zh, ja) — machine-translated
with Gemini, figures kept in English. **These are gated off until the translations are verified**:
CI builds and releases them only when the repo variable **`BUILD_TRANSLATIONS`** is set to `true`
(and the `GEMINI_API_KEY` secret exists). Until then, every release is **English only**. Build one
locally any time with `BOOK_LANG=pt bash book/build.sh` (sponsored PDF + EPUB).

## Build locally

```bash
# needs: pandoc + a LaTeX engine (xelatex)
bash book/build.sh        # → build/asterisk-guide.{pdf,epub,tex}
```

## Repository layout

```
src/chapters/   the book, one Markdown file per chapter (single source of truth)
src/images/     figures
src/extract.py  the original PDF→Markdown recovery pipeline
book/           Pandoc build (metadata.yaml, build.sh)
lab/            reproducible Asterisk 22 Docker lab used to verify every example
docs/adr/       architecture/decision records
CONTEXT.md      canonical glossary (terminology used across the book)
PLAN-2ND-EDITION.md   the modernization plan & roadmap
.github/workflows/build-book.yml   CI: build PDF/EPUB/LaTeX on every PR, release on tags
```

## Contributing

Open a PR. CI rebuilds the book and attaches the rendered PDF/EPUB/LaTeX as artifacts so the
change can be reviewed as the finished book, not just the diff. Examples are expected to be
verified against the Asterisk 22 lab in [`lab/`](./lab).

## License

Everything in this repository is licensed **CC BY-NC-SA 4.0** (see [`LICENSE`](./LICENSE)) —
free to read, share, and adapt for non-commercial purposes with attribution. The paper book
(Amazon KDP) and the VoIP School Blackbelt training are the author's commercial products.
