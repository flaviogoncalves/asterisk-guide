# Complete Asterisk Training — 2nd Edition

[![Build book](../../actions/workflows/build-book.yml/badge.svg)](../../actions/workflows/build-book.yml)

The open source of *Complete Asterisk Training* by **Flavio E. Gonçalves** — a systematic guide
to building an IP PBX with **Asterisk 22 LTS**. The Markdown source and the lab are free; the
**paper book** (Amazon KDP) and the **VoIP School Blackbelt** training are the supported products.

## Download the book

Every push and pull request builds the book in three formats. Grab them from:

- **Releases** — tagged versions (`v*`) attach the PDF, EPUB and LaTeX. *(downloads here)*
- **Actions → latest run → Artifacts** — the build for any branch or PR.

## Build locally

```bash
# needs: pandoc + a LaTeX engine (xelatex)
bash book/build.sh        # → build/complete-asterisk-training.{pdf,epub,tex}
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
