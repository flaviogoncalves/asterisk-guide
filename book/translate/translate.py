#!/usr/bin/env python3
"""
Translate the book's Markdown chapters to Portuguese (pt-BR) or Spanish (es) with Google
Gemini, preserving all code/config/CLI/Markdown structure and the English figures.

- Engine: Gemini text model, cheapest tier (configurable). Reads the API key the same way
  book/illustrate/nanobanana.py does (.env / environment). Never prints the key.
- Images stay English: ![alt](../images/NAME) link targets are kept verbatim (alt text may be
  translated). No figure is regenerated.
- Caches by source content hash, so unchanged chapters are not re-translated (and not re-paid).

Usage:
  python3 book/translate/translate.py --lang pt            # all chapters -> i18n/pt/chapters/
  python3 book/translate/translate.py --lang es --only 05-part2.md
  python3 book/translate/translate.py --lang pt --force    # ignore cache
"""
import argparse, hashlib, json, os, re, socket, sys, time, urllib.request, urllib.error


def mask_code(md):
    """Replace every fenced and inline code span with an opaque sentinel so the model can
    never alter code/CLI/config. Returns (masked_text, blocks)."""
    blocks = []

    def repl(m):
        blocks.append(m.group(0))
        return "【C%d】" % (len(blocks) - 1)   # 【C0】 — distinctive, model leaves it alone

    md = re.sub(r"```.*?```", repl, md, flags=re.S)      # fenced blocks first
    md = re.sub(r"`[^`\n]+`", repl, md)                  # then inline code
    return md, blocks


def unmask_code(md, blocks):
    for i, b in enumerate(blocks):
        md = md.replace("【C%d】" % i, b)
    return md

DEFAULT_MODEL = os.environ.get("GEMINI_TRANSLATE_MODEL", "gemini-flash-lite-latest")
KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY")
LANG_NAMES = {"pt": "Brazilian Portuguese (pt-BR)", "es": "Latin American Spanish (es)",
              "fr": "French", "de": "German", "it": "Italian", "hi": "Hindi",
              "zh": "Simplified Chinese (Mandarin)", "ja": "Japanese"}
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load_api_key():
    for n in KEY_NAMES:
        if os.environ.get(n):
            return os.environ[n].strip()
    for envf in (os.path.join(ROOT, ".env"), os.path.join(ROOT, "..", ".env")):
        if os.path.isfile(envf):
            for line in open(envf):
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() in KEY_NAMES:
                    return v.strip().strip('"').strip("'")
    sys.exit("ERROR: no Gemini API key. Set one of %s in env or .env." % ", ".join(KEY_NAMES))


def prompt_for(lang_name, glossary, md):
    keep = ", ".join(glossary)
    return f"""You are a professional technical translator. Translate the following Markdown \
chapter of a book about Asterisk (VoIP/telephony) from English into {lang_name}.

STRICT RULES — follow exactly:
- Translate ONLY human-readable prose: paragraph text, headings, list-item text, table-cell \
text, blockquote text, image alt-text, and captions.
- DO NOT translate or alter in any way:
  * fenced code blocks (between ``` ```), including comments inside them — copy byte for byte;
  * inline `code`, configuration keys/values, CLI commands and their output, file paths, \
option names, numbers, version strings, URLs, and email addresses;
  * Markdown syntax: heading markers (#), list bullets, table pipes (|), blockquote >, link \
and image targets — keep every `](target)` and `](path)` EXACTLY (you may translate an image's \
alt text, never its path); Pandoc attributes like {{.unnumbered}} and {{width=...}}.
- The text contains opaque placeholders like 【C0】, 【C1】 (these stand for code/CLI/config). \
Keep every placeholder EXACTLY as-is and in place — never translate, edit, remove, reorder, or \
add spaces inside them.
- Keep these technical terms in English (do not translate): {keep}.
- Preserve all blank lines and the overall layout so the Markdown renders identically.
- Output ONLY the translated Markdown. No preamble, no explanation, and do NOT wrap the whole \
document in a code fence.

--- BEGIN MARKDOWN ---
{md}
--- END MARKDOWN ---"""


def translate(model, key, text):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 65536}}
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model
    # Retry transient failures (read timeouts, 429/5xx) so one hiccup doesn't kill a whole run.
    data = None
    for attempt in range(5):
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json",
                                              "x-goog-api-key": key})
        try:
            resp = urllib.request.urlopen(req, timeout=300)
            data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(5 * (attempt + 1)); continue
            sys.exit("ERROR: Gemini HTTP %s: %s" % (e.code, e.read().decode()[:500]))
        except (socket.timeout, urllib.error.URLError) as e:
            if attempt < 4:
                time.sleep(5 * (attempt + 1)); continue
            sys.exit("ERROR: Gemini request failed after retries: %s" % e)
    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (KeyError, IndexError):
        sys.exit("ERROR: unexpected Gemini response: %s" % json.dumps(data)[:500])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, choices=list(LANG_NAMES))
    ap.add_argument("--src", default=os.path.join(ROOT, "src", "chapters"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--glossary", default=os.path.join(HERE, "glossary.txt"))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--only", default=None, help="translate just this filename")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    a = ap.parse_args()

    out = a.out or os.path.join(ROOT, "i18n", a.lang, "chapters")
    os.makedirs(out, exist_ok=True)
    glossary = [ln.strip() for ln in open(a.glossary)
                if ln.strip() and not ln.startswith("#")]
    key = load_api_key()
    manifest_path = os.path.join(out, ".hashes.json")
    manifest = json.load(open(manifest_path)) if os.path.isfile(manifest_path) else {}

    files = sorted(f for f in os.listdir(a.src) if f.endswith(".md"))
    if a.only:
        files = [a.only]
    done = skipped = 0
    for f in files:
        src = open(os.path.join(a.src, f)).read()
        h = hashlib.sha256(src.encode()).hexdigest()
        dst = os.path.join(out, f)
        if not a.force and manifest.get(f) == h and os.path.isfile(dst):
            print("  = %s (cached)" % f); skipped += 1; continue
        print("  → %s (%s)" % (f, LANG_NAMES[a.lang]))
        masked, blocks = mask_code(src)
        prompt = prompt_for(LANG_NAMES[a.lang], glossary, masked)
        # Translate, with up to 3 attempts: the model sometimes drops or duplicates a 【Ci】
        # sentinel (a code block missing/doubled). Retry until every block restores exactly once.
        restored, missing = None, ["?"]
        for attempt in range(3):
            translated = translate(a.model, key, prompt)
            # All real code is a sentinel, so any ``` the model emitted is spurious — strip it.
            translated = translated.replace("```", "")
            # Keep only the first occurrence of each sentinel (the model sometimes repeats one).
            _seen = set()
            translated = re.sub(r"【C\d+】",
                                lambda m: "" if m.group(0) in _seen else (_seen.add(m.group(0)) or m.group(0)),
                                translated)
            missing = [i for i in range(len(blocks)) if ("【C%d】" % i) not in translated]
            restored = unmask_code(translated, blocks)
            if not missing and "【C" not in restored:
                break
            print("    … attempt %d dropped %d block(s) in %s — retrying" % (attempt + 1, len(missing), f))
        open(dst, "w").write(restored.rstrip() + "\n")
        done += 1
        if missing or "【C" in restored:
            print("    ! WARNING: %s still imperfect after retries — NOT caching" % f)
            continue
        manifest[f] = h
        json.dump(manifest, open(manifest_path, "w"), indent=0)
    print("Done: %d translated, %d cached → %s" % (done, skipped, out))


if __name__ == "__main__":
    main()
