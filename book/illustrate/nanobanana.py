#!/usr/bin/env python3
"""
nanobanana.py — generate/modernize a book figure with Nano Banana Pro (Gemini image).

LAST-RESORT, PAID path of the `illustrator` skill. Prefer scripted text-slides or Mermaid.

- Always generates at the 1K tier (~$0.067/image). Refuses 2K/4K unless --force.
- Carries a reference image so the model preserves the figure's meaning (image-to-image).
- Generates N cheap *variations* so you can pick the best, then keep one and delete the rest.
- Reads the API key from .env (astbook/.env or the parent repo .env). Never prints the key.

Examples:
  python3 book/illustrate/nanobanana.py --ref src/images/19-security-fig01.png \
      --out src/images/19-security-fig01.png --variations 3 \
      --prompt "Design a publication-quality diagram based on the uploaded reference image. \
Style: clean, modern, instructional. Background: white. Palette: black and white with a single \
blue accent. All labels legible and accurate. Format 16:9. Accuracy over aesthetics. \
Subject: a peer-to-peer botnet sending many SIP REGISTER attempts at one Asterisk server."

  python3 book/illustrate/nanobanana.py --prompt-file book/illustrate/prompts/19-fig01.txt \
      --ref src/images/19-security-fig01.png --out src/images/19-security-fig01.png
"""
import argparse, base64, json, mimetypes, os, sys, urllib.request, urllib.error

# Nano Banana Pro = Gemini 3 Pro Image. Override with --model or NANOBANANA_MODEL if it changes.
DEFAULT_MODEL = os.environ.get("NANOBANANA_MODEL", "gemini-3-pro-image-preview")
PRICE_1K = 0.067  # USD per 1K image, per the project's cost note
KEY_NAMES = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY",
             "NANO_BANANA_API_KEY", "NANOBANANA_API_KEY")


def load_api_key():
    # 1) environment, 2) .env files (key name=value), searching repo + parent.
    for n in KEY_NAMES:
        if os.environ.get(n):
            return os.environ[n].strip()
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", ".env"),        # astbook/.env
        os.path.join(here, "..", "..", "..", ".env"),   # parent repo .env
    ]
    for path in candidates:
        if not os.path.isfile(path):
            continue
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() in KEY_NAMES:
                return v.strip().strip('"').strip("'")
    sys.exit("ERROR: no API key found. Set one of %s in the environment or .env." % ", ".join(KEY_NAMES))


def inline_part(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        return {"inlineData": {"mimeType": mime, "data": base64.b64encode(f.read()).decode()}}


def generate(model, key, prompt, refs, aspect, size):
    parts = [{"text": prompt}] + [inline_part(p) for p in refs]
    body = {
        "contents": [{"parts": parts}],
        # imageConfig is what pins the 1K tier + book aspect ratio. If the API rejects
        # responseModalities for this model, drop it (the pro image model returns an image).
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect, "imageSize": size},
        },
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},  # key in header, not URL
    )
    try:
        resp = urllib.request.urlopen(req, timeout=180)
    except urllib.error.HTTPError as e:
        sys.exit("API error %s: %s" % (e.code, e.read().decode("utf-8", "ignore")[:800]))
    data = json.loads(resp.read())
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob and blob.get("data"):
                return base64.b64decode(blob["data"])
    sys.exit("No image in response: %s" % json.dumps(data)[:800])


def main():
    ap = argparse.ArgumentParser(description="Generate/modernize a figure with Nano Banana Pro.")
    ap.add_argument("--prompt"); ap.add_argument("--prompt-file")
    ap.add_argument("--ref", action="append", default=[], help="reference image (repeatable)")
    ap.add_argument("--out", required=True, help="output path; variations save as <out>.vN.png")
    ap.add_argument("--variations", type=int, default=1)
    ap.add_argument("--aspect", default="16:9")
    ap.add_argument("--size", default="1K", choices=["1K", "2K", "4K"])
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--force", action="store_true", help="allow >1K (more expensive)")
    a = ap.parse_args()

    if a.size != "1K" and not a.force:
        sys.exit("Refusing %s (more expensive than 1K ~$%.3f). Re-run with --force to override."
                 % (a.size, PRICE_1K))
    prompt = a.prompt or (open(a.prompt_file).read() if a.prompt_file else None)
    if not prompt:
        sys.exit("Provide --prompt or --prompt-file.")
    for r in a.ref:
        if not os.path.isfile(r):
            sys.exit("reference image not found: %s" % r)

    key = load_api_key()
    base, ext = os.path.splitext(a.out)
    ext = ext or ".png"
    n = max(1, a.variations)
    saved = []
    for i in range(1, n + 1):
        img = generate(a.model, key, prompt, a.ref, a.aspect, a.size)
        out = a.out if n == 1 else "%s.v%d%s" % (base, i, ext)
        with open(out, "wb") as f:
            f.write(img)
        saved.append(out)
        print("  saved %s" % out)
    est = n * PRICE_1K
    print("Done: %d image(s), %s %s, ~$%.3f estimated (%s)."
          % (n, a.aspect, a.size, est, a.model))
    if n > 1:
        print("Review the variations, copy the best over '%s', and delete the rest." % a.out)


if __name__ == "__main__":
    main()
