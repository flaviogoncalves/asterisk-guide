#!/usr/bin/env python3
"""
PATH-1 house-style topology figure for chapter 7 / Lab 5 (09-sip-trunking):
a real SIP trunk between the Asterisk PBX and the ITSP (sip.flagonc.com).

House style: white bg, near-black ink #1A1A1A, single blue accent #1C5D99, 16:9 @ 1600x900.
Current to Asterisk 22 / PJSIP. Output to staging/ for review, then swap into src/images/.

fig01 — Softphones -> Asterisk PBX -> SIP trunk (REGISTER/INVITE + RTP, UDP :5600) -> ITSP -> PSTN
"""
from PIL import Image, ImageDraw, ImageFont
import os

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


def box(d, x, y, w, h, title_txt, lines, accent=False, r=18):
    fill = ACCENT_L if accent else BOXBG
    edge = ACCENT if accent else LINE
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=edge, width=3)
    fb = font(SANS_B, 34)
    ctext(d, x + w / 2, y + 20, title_txt, fb, INK)
    fs = font(SANS, 26)
    yy = y + 66
    for ln in lines:
        ctext(d, x + w / 2, yy, ln, fs, MUTED)
        yy += 34


def arrow(d, x1, y1, x2, y2, color, width=5, head=16):
    d.line([(x1, y1), (x2, y2)], fill=color, width=width)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (-1, 1):
        a = ang + s * 0.42
        d.line([(x2, y2), (x2 - head * math.cos(a), y2 - head * math.sin(a))], fill=color, width=width)


def main():
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    # title
    ft = font(SANS_B, 52)
    ctext(d, W / 2, 56, "A SIP trunk to the ITSP", ft)
    d.line([(W / 2 - 250, 122), (W / 2 + 250, 122)], fill=ACCENT, width=5)

    midy = 440
    # Softphones
    box(d, 40, midy - 105, 230, 210, "Softphones",
        ["PJSIP/6001", "PJSIP/6002", "(your LAN)"])
    # Asterisk PBX
    box(d, 370, midy - 120, 290, 240, "Asterisk 22 PBX",
        ["chan_pjsip", "endpoint + auth", "+ aor + registration", "from-pstn context"], accent=True)
    # ITSP   (wide gap to the PBX so the trunk labels sit clear of both boxes)
    box(d, 950, midy - 120, 290, 240, "ITSP",
        ["sip.flagonc.com", "UDP :5600", "accts 1010-1050", "registrar + proxy"], accent=True)
    # PSTN
    box(d, 1360, midy - 90, 200, 180, "PSTN", ["the phone", "network"])

    # links
    arrow(d, 270, midy, 370, midy, LINE)            # phones <-> PBX
    arrow(d, 370, midy, 270, midy, LINE)
    # trunk link (accent) PBX <-> ITSP, only spanning the clear gap 660..950
    arrow(d, 660, midy - 38, 950, midy - 38, ACCENT, width=6)   # outbound REGISTER / INVITE
    arrow(d, 950, midy + 38, 660, midy + 38, ACCENT, width=6)   # inbound calls
    arrow(d, 1240, midy, 1360, midy, LINE)          # ITSP <-> PSTN
    arrow(d, 1360, midy, 1240, midy, LINE)

    # trunk annotations — centered in the 660..950 gap (cx=805), clear of both boxes
    fa = font(MONO, 22)
    ctext(d, 805, midy - 78, "REGISTER / INVITE", fa, ACCENT)
    ctext(d, 805, midy + 56, "inbound calls", fa, ACCENT)

    # caption strip
    fc = font(SANS, 26)
    ctext(d, W / 2, 760, "The PBX registers as one account; outbound calls dial PJSIP/<num>@trunk and",
          fc, MUTED)
    ctext(d, W / 2, 796, "inbound calls land in the from-pstn context. RTP media flows over UDP.",
          fc, MUTED)
    ctext(d, W / 2, 832, "Lab 5 connects to sip.flagonc.com.", fc, MUTED)

    out = os.path.join(OUT, "09-sip-trunking-fig01.png")
    img.save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
