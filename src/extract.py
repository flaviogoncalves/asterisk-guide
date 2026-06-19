#!/usr/bin/env python3
"""Recover 'Complete Asterisk Training' from PDF into structured Markdown.

Classifies each line by font: Arial -> heading, LucidaConsole/Courier -> code,
TimesNewRoman -> body. Groups code into fenced blocks, extracts images.
"""
import fitz, os, re, hashlib

PDF = "/Users/flavio/Downloads/AstV16A.pdf"
OUT = os.path.join(os.path.dirname(__file__), "chapters")
IMG = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True); os.makedirs(IMG, exist_ok=True)

# (start_page_1indexed, title). End = next start.
CHAPTERS = [
    (1,  "00-front-matter"),
    (17, "01-introduction-to-asterisk"),
    (35, "02-download-and-install"),
    (53, "03-building-a-simple-pbx"),
    (87, "04-analog-channels"),
    (103,"05-digital-channels"),
    (137,"06-designing-a-voip-network"),
    (154,"07-the-iax-protocol"),
    (178,"08-the-sip-protocol"),
    (204,"09-pjsip-the-new-sip-channel"),
    (223,"10-dialplan-advanced-features"),
    (254,"11-using-pbx-features"),
    (274,"12-call-queues"),
    (289,"13-call-detail-records"),
    (299,"14-ami-and-agi"),
    (313,"15-asterisk-security"),
    (331,"16-asterisk-realtime"),
]
END = 342  # one past last page

MONO = ("LucidaConsole", "CourierNew", "Courier")
HEADING = "Arial"

# Lines to drop: running header/footer/margin noise
NOISE = re.compile(r"^(complete asterisk training|chapter \d+)\s*$", re.I)
PAGENUM = re.compile(r"^[-–]\s*\d{1,3}\s*[-–]$")          # "- 174 -"
MARGIN  = re.compile(r"^\|.*\|.*$")                         # "| Chapter 8 ... |"
BULLET_FONTS = ("Symbol", "Wingdings")
BULLET_CHARS = "•●▪"

IMG_MIN_BYTES = 4096   # below this = inline glyph/icon, skip

def is_mono(font): return any(m in font for m in MONO)
def is_bullet_span(s):
    return any(b in s["font"] for b in BULLET_FONTS) or s["text"].strip() in BULLET_CHARS

def line_info(line):
    """Return (text, kind, size). kind in {heading,code,body,bullet,blank}."""
    spans = line["spans"]
    text = "".join(s["text"] for s in spans)
    if not text.strip():
        return text, "blank", 0
    # bullet: first non-space span is a bullet glyph -> list item
    if spans and is_bullet_span(spans[0]):
        rest = "".join(s["text"] for s in spans[1:]).strip()
        return rest, "bullet", 0
    # dominant span by char count
    dom = max(spans, key=lambda s: len(s["text"]))
    size = round(max(s["size"] for s in spans))
    font = dom["font"]
    if HEADING in font and size >= 13:
        return text, "heading", size
    if is_mono(font):
        return text, "code", size
    return text, "body", size

def hlevel(size):
    if size >= 26: return "#"
    if size >= 16: return "##"
    if size >= 14: return "###"
    return "####"

doc = fitz.open(PDF)
seen_imgs = set()  # global dedupe (logos/icons repeat every chapter)

def extract_range(start, end, slug):
    md = []
    code_buf = []
    body_buf = []
    bullet_buf = []      # fragments of the current list item
    list_indent = [0]    # x where the current item's text starts
    img_idx = 0

    def sep_after_list():
        if md and md[-1].startswith("- "):
            md.append("")

    def flush_code():
        nonlocal code_buf
        if code_buf:
            sep_after_list()
            # strip trailing blank lines
            while code_buf and not code_buf[-1].strip(): code_buf.pop()
            while code_buf and not code_buf[0].strip(): code_buf.pop(0)
            if code_buf:
                md.append("```")
                md.extend(code_buf)
                md.append("```")
                md.append("")
            code_buf = []

    def flush_bullet():
        nonlocal bullet_buf
        if bullet_buf:
            item = re.sub(r"\s+", " ", " ".join(bullet_buf)).strip()
            if item:
                md.append(f"- {item}")
            bullet_buf = []

    def flush_body():
        nonlocal body_buf
        if body_buf:
            sep_after_list()
            para = " ".join(x.strip() for x in body_buf if x.strip())
            para = re.sub(r"\s+", " ", para).strip()
            if para:
                md.append(para); md.append("")
            body_buf = []

    for pno in range(start-1, end-1):
        page = doc[pno]
        d = page.get_text("dict")
        # images on this page
        imgs = page.get_images(full=True)

        # --- gather all text lines with position, then reflow by reading order ---
        raw = []
        for b in d["blocks"]:
            if b.get("type") == 1:
                continue
            for l in b.get("lines", []):
                x0, y0 = l["bbox"][0], l["bbox"][1]
                # a bullet marker = SymbolMT glyph with (almost) no other text
                marker = (l["spans"] and is_bullet_span(l["spans"][0])
                          and not "".join(s["text"] for s in l["spans"][1:]).strip())
                raw.append({"x": x0, "y": y0, "line": l, "marker": marker})

        # associate standalone bullet markers with the body line at the same y
        markers = [r for r in raw if r["marker"]]
        bodies  = [r for r in raw if not r["marker"]]
        bullet_ys = []
        for m in markers:
            cand = [bd for bd in bodies if abs(bd["y"] - m["y"]) < 6 and bd["x"] > m["x"]]
            if cand:
                cand.sort(key=lambda r: abs(r["y"] - m["y"]))
                cand[0]["force_bullet"] = True
            else:
                bullet_ys.append(m["y"])  # orphan marker, text may follow inline

        # emit in reading order (top-to-bottom, then left-to-right)
        bodies.sort(key=lambda r: (round(r["y"]), r["x"]))
        for r in bodies:
                l = r["line"]
                text, kind, size = line_info(l)
                if r.get("force_bullet"):
                    kind = "bullet"
                    text = text.strip()
                stripped = text.strip()
                if kind == "blank":
                    if code_buf: code_buf.append("")
                    elif not bullet_buf: flush_body()
                    continue
                if NOISE.match(stripped) or PAGENUM.match(stripped) or MARGIN.match(stripped):
                    continue
                # page number only line
                if re.fullmatch(r"[ivxlcdm]+|\d{1,3}", stripped, re.I) and kind != "code":
                    continue
                if kind == "heading":
                    flush_code(); flush_bullet(); flush_body(); sep_after_list()
                    if size >= 50:   # chapter number -> skip, title follows
                        continue
                    md.append(f"{hlevel(size)} {stripped}")
                    md.append("")
                elif kind == "bullet":
                    flush_code(); flush_bullet(); flush_body()
                    bullet_buf.append(stripped)
                    list_indent[0] = r["x"]
                elif kind == "code":
                    flush_bullet(); flush_body()
                    code_buf.append(text.rstrip())
                else:  # body
                    if bullet_buf and r["x"] >= list_indent[0] - 3:
                        bullet_buf.append(stripped)        # wrapped continuation
                    else:
                        flush_bullet(); flush_code()
                        body_buf.append(text)
        # extract images for this page: skip tiny glyphs, dedupe by content hash
        for info in imgs:
            xref = info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                data = pix.tobytes("png")
                if len(data) < IMG_MIN_BYTES:
                    continue
                if pix.width < 64 or pix.height < 64:
                    continue
                h = hashlib.md5(data).hexdigest()
                if h in seen_imgs:
                    continue
                seen_imgs.add(h)
                img_idx += 1
                fn = f"{slug}-img{img_idx:02d}.png"
                with open(os.path.join(IMG, fn), "wb") as imf:
                    imf.write(data)
                flush_code(); flush_bullet(); flush_body(); sep_after_list()
                md.append(f"![{slug} figure {img_idx}](../images/{fn})")
                md.append("")
            except Exception:
                pass
    flush_code(); flush_bullet(); flush_body()
    return "\n".join(md), img_idx

total_imgs = 0
for i, (start, slug) in enumerate(CHAPTERS):
    end = CHAPTERS[i+1][0] if i+1 < len(CHAPTERS) else END
    text, nimg = extract_range(start, end, slug)
    with open(os.path.join(OUT, slug + ".md"), "w") as f:
        f.write(text)
    total_imgs += nimg
    print(f"{slug:40} pages {start:>3}-{end-1:<3} {len(text):>7} chars  {nimg} imgs")
print("Total images:", total_imgs)
