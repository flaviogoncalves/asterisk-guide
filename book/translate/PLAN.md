# Translation plan — Portuguese (pt) & Spanish (es)

Status: **implemented.** `book/translate/translate.py` translates the chapters with Gemini
(default model `gemini-flash-lite-latest` — cheapest tier; override with `GEMINI_TRANSLATE_MODEL`),
caching by content hash. `book/build.sh` builds a language with `BOOK_LANG=pt|es`. CI translates
+ builds PT/ES on main/tags when the **`GEMINI_API_KEY`** repo secret is set, and attaches them
to releases.

```bash
python3 book/translate/translate.py --lang pt     # -> i18n/pt/chapters/ (cached by hash)
BOOK_LANG=pt bash book/build.sh clean             # -> build/asterisk-guide-pt.{pdf,epub,tex}
```

The agreed spec it implements:

## Decisions (from the author)
- **Engine:** Google **Gemini** does the translation, using the **same API key** already in
  `.env` (the one the illustrator uses) — read it the same way `book/illustrate/nanobanana.py`
  does. Never commit the key.
- **Model:** the **cheapest Gemini text model** (e.g. `gemini-2.0-flash-lite` / current
  flash-lite tier). Make it a configurable constant defaulting to the cheapest available.
- **Images stay in English** — do **not** translate or regenerate figures. The
  `![alt](../images/NAME)` links are kept verbatim, pointing at the same English figures.
  (Translating the alt-text is optional; the image files are untouched.)
- **Targets:** Portuguese (pt-BR) and Spanish (es).

## Approach
1. `book/translate/translate.py` — for each `src/chapters/*.md`, send the Markdown to Gemini
   with a strict prompt: translate prose only; **do not alter** fenced code blocks, inline
   `code`, config, CLI, option names, `![](../images/...)` links, or Markdown structure;
   keep Asterisk technical terms (PJSIP, dialplan, `pjsip.conf`, etc.) untranslated. Chunk per
   chapter (or per heading) to stay within token limits; cache by content hash to avoid
   re-paying for unchanged chapters.
2. Output to `i18n/pt/chapters/` and `i18n/es/chapters/` (same filenames). Figures are shared
   from `src/images/` via `--resource-path`, so no per-language image copies.
3. `book/build.sh` gains a `LANG` parameter (default `en`); build PT/ES the same way →
   `asterisk-guide-pt.{pdf,epub,tex}` and `-es`. Front-matter/metadata strings localized.
4. **CI:** extend `.github/workflows/build-book.yml` with a language matrix
   (`[en, pt, es]`); the translate step runs only when chapters changed, reads
   `GEMINI_API_KEY` from a GitHub Actions **secret**, and the cheapest-model translation is
   cheap enough to run per PR. Releases attach all three languages.

## Open questions for implementation time
- pt-BR vs pt-PT (assume **pt-BR**).
- Whether to also localize the figure alt-text (cheap; images themselves stay English).
- Glossary of terms to force-keep in English (PJSIP, dialplan, channel, trunk, …).
