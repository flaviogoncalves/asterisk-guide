#!/usr/bin/env python3
"""
PATH-1 figure for chapter 16 (16-cdr-cel), rendered with Pillow in the house style
(white bg, near-black ink, single blue accent #1C5D99). 16:9, 1600x900, content current
to Asterisk 22.

fig01 replaces src/images/13-call-detail-records-img01.png — the original is a synthetic
terminal screenshot of `mysql> select * from cdr;`. The 16-column-wide raw dump is illegible
at 6x9 print, so it is redrawn as a clean field-by-field CDR record card: every CDR column is
shown with the sample answered call's value, faithful to the original lab data (PJSIP channels,
amaflags 3 = DOCUMENTATION). Outputs to book/illustrate/staging/ for review before swapping
into src/images/.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
ACCENTBG = (225, 234, 243)
LINE = (170, 178, 190)
OUT = os.path.join(os.path.dirname(__file__), "staging")
os.makedirs(OUT, exist_ok=True)

SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc"]
SANS_B = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
          "/System/Library/Fonts/Helvetica.ttc"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Monaco.ttf"]


def font(paths, size):
    for p in paths:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def canvas():
    img = Image.new("RGB", (W, H), "white")
    return img, ImageDraw.Draw(img)


def title(d, text, y=58):
    f = font(SANS_B, 54)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W / 2 - w / 2, y + 70), (W / 2 + w / 2, y + 70)], fill=ACCENT, width=5)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=14):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


# ---- fig01: the CDR table fields, shown as a sample answered-call record ----
def fig01():
    img, d = canvas()
    title(d, "A CDR row:  SELECT * FROM cdr")

    # Sample row taken faithfully from the original screenshot (lab data, PJSIP channels).
    # amaflags 3 = DOCUMENTATION. Fields per the CDR specification (cdr table columns).
    rows = [
        ("calldate", "2019-01-22 11:39:18", "when the call started"),
        ("clid", '"6003" <bria>', "caller ID (name + number)"),
        ("src", "bria", "source / calling party"),
        ("dst", "6000", "destination extension"),
        ("dcontext", "to-ld", "destination context"),
        ("channel", "PJSIP/bria-00000000", "channel that placed the call"),
        ("dstchannel", "PJSIP/zoiper-00000001", "channel that was dialed"),
        ("lastapp", "Dial", "last dialplan application run"),
        ("lastdata", "PJSIP/zoiper,20,tT", "arguments to that application"),
        ("duration", "5", "seconds from dial to hang-up"),
        ("billsec", "1", "seconds from answer to hang-up"),
        ("disposition", "ANSWERED", "ANSWERED / NO ANSWER / BUSY / FAILED / CONGESTION"),
        ("amaflags", "3  (DOCUMENTATION)", "DEFAULT / OMIT / BILLING / DOCUMENTATION"),
        ("accountcode", "", "billing account / department"),
        ("uniqueid", "1548157158.0", "unique call identifier"),
        ("userfield", "", "free-form user-defined field"),
    ]

    fk = font(MONO, 31)
    fv = font(MONO, 31)
    fd = font(SANS, 24)

    x0, y0 = 90, 250
    col_w = 720
    row_h = 62
    key_w = 230      # column key width
    val_w = 360      # value column width

    n = len(rows)
    half = (n + 1) // 2
    cols = [rows[:half], rows[half:]]

    for ci, col in enumerate(cols):
        cx = x0 + ci * col_w
        # header band
        rbox(d, cx, y0 - 64, col_w - 40, 48, fill=ACCENTBG, outline=ACCENT, width=2, r=10)
        d.text((cx + 18, y0 - 54), "field", font=font(SANS_B, 27), fill=ACCENT)
        d.text((cx + key_w + 18, y0 - 54), "value", font=font(SANS_B, 27), fill=ACCENT)
        for ri, (k, v, desc) in enumerate(col):
            ry = y0 + ri * row_h
            if ri % 2 == 0:
                d.rectangle([cx, ry - 8, cx + col_w - 40, ry + row_h - 12], fill=(248, 250, 252))
            d.text((cx + 18, ry), k, font=fk, fill=ACCENT)
            disp = v if v else "(empty)"
            vfill = INK if v else MUTED
            d.text((cx + key_w + 18, ry), disp, font=fv, fill=vfill)

    # footnote describing the data
    fnote = font(SANS, 24)
    note = ("One summary row per call. Channels are PJSIP; amaflags 3 = DOCUMENTATION. "
            "Add columns (e.g. CDR(jitter)) with cdr_adaptive_odbc.")
    nw = d.textlength(note, font=fnote)
    d.text(((W - nw) / 2, H - 70), note, font=fnote, fill=MUTED)

    save(img, "13-call-detail-records-img01.png")


if __name__ == "__main__":
    fig01()
    print("done")
