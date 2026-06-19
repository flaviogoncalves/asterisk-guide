# Source is free; the print book and VoIP School Blackbelt training are the paid artifacts

The Markdown source and the Docker lab are treated as commodity and are published as a
**public GitHub repository** that acts as a marketing funnel. The monetizable artifacts are
the **paper book** (Amazon KDP) and the **VoIP School Blackbelt training**, not the digital text.

**CI/CD as the press:** GitHub Actions (`.github/workflows/build-book.yml`) rebuilds the book on
every push and pull request, uploading the **PDF, EPUB and LaTeX** as downloadable artifacts;
version tags (`v*`) publish those three formats as **GitHub Release** assets. A PR is therefore
reviewed as the finished book, not just a diff.

## Consequences

- Everything in this repo must be safe to open-source: no secrets, no customer data, no
  licensed third-party content, clean commit history, an explicit license decision before going public.
- The Docker lab and verified config files are written to stand alone as a usable companion
  (delivered through VoIP School Blackbelt now; potentially public later).
- Editorial choices favour teaching value and shareability over gating content.
