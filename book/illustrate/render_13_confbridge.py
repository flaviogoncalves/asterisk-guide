#!/usr/bin/env python3
"""
PATH-1 house-style figure for chapter 11 (13-pbx-features): a ConfBridge conference.
Several SIP endpoints join one named conference (101) via ConfBridge(); one is admin; the
mixing and timing are handled by res_confbridge + the built-in res_timing_* timer (no DAHDI).

House style: white bg, near-black ink #1A1A1A, single blue accent #1C5D99, 16:9 @ 1600x900.
Output to staging/ for review, then swap into src/images/13-pbx-features-fig09.png.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)
ACCENT_L = (214, 226, 238)
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
LINE = (170, 178, 190)
OUT = os.path.join(os.path.dirname(__file__), "staging")
os.makedirs(OUT, exist_ok=True)
SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
SANS_B = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf"]


def font(paths, size):
    for p in paths:
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def ctext(d, cx, y, text, f, fill=INK):
    w = d.textlength(text, font=f)
    d.text((cx - w / 2, y), text, font=f, fill=fill)


def phone(d, cx, cy, label, sub, admin=False):
    w, h = 230, 120
    x, y = cx - w / 2, cy - h / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=16,
                        fill=ACCENT_L if admin else BOXBG, outline=ACCENT if admin else LINE, width=3)
    ctext(d, cx, y + 22, label, font(SANS_B, 30), INK)
    ctext(d, cx, y + 60, sub, font(SANS, 24), MUTED)
    if admin:
        ctext(d, cx, y + 88, "admin", font(MONO, 22), ACCENT)


def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    ft = font(SANS_B, 50)
    ctext(d, W / 2, 50, "One ConfBridge conference, many endpoints", ft)
    d.line([(W / 2 - 360, 116), (W / 2 + 360, 116)], fill=ACCENT, width=5)

    cx, cy, r = W / 2, 470, 150
    # central conference bridge
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT_L, outline=ACCENT, width=4)
    ctext(d, cx, cy - 52, "Conference", font(SANS_B, 34), INK)
    ctext(d, cx, cy - 14, "101", font(MONO, 40), ACCENT)
    ctext(d, cx, cy + 34, "ConfBridge()", font(MONO, 24), MUTED)

    # four endpoints around the bridge
    spots = [(cx - 520, cy - 150, "PJSIP/6001", "Alice", True),
             (cx + 520, cy - 150, "PJSIP/6002", "Bob", False),
             (cx - 520, cy + 150, "PJSIP/6003", "Carol", False),
             (cx + 520, cy + 150, "PJSIP/6004", "Dave", False)]
    for px, py, lbl, sub, adm in spots:
        # connector from phone edge toward the bridge
        ang = math.atan2(cy - py, cx - px)
        ex, ey = px + 120 * math.cos(ang), py + 70 * math.sin(ang)
        bx, by = cx - (r + 6) * math.cos(ang), cy - (r + 6) * math.sin(ang)
        d.line([(ex, ey), (bx, by)], fill=ACCENT if adm else LINE, width=4)
        phone(d, px, py, lbl, sub, admin=adm)

    # callout box: mixing + timing
    bx0, by0, bx1, by1 = W / 2 - 360, 770, W / 2 + 360, 858
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=BOXBG, outline=LINE, width=2)
    ctext(d, W / 2, by0 + 16,
          "Mixing + timing by res_confbridge + the built-in res_timing_* timer",
          font(SANS, 25), INK)
    ctext(d, W / 2, by0 + 50, "— no DAHDI / dahdi_dummy required —", font(SANS, 23), ACCENT)

    out = os.path.join(OUT, "13-pbx-features-fig09.png")
    img.save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
