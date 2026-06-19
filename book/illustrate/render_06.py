#!/usr/bin/env python3
"""
PATH-1 text/flow/packet figures for chapter 6 (06-designing-voip-network), rendered with Pillow
in the house style (white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900,
content current to Asterisk 22. Outputs to book/illustrate/staging/ for review before swapping into
src/images/. Adapted from render_ch3_slides.py.

Figures:
  fig01 — Asterisk modular architecture (APIs + core blocks)
  fig03 — Peer / User / Friend (Asterisk's point of view)
  fig04 — PCM (analog -> sample -> 64 Kbps bitstream)
  fig05 — Single g.729 voice packet on Ethernet (header byte breakdown)
  fig08 — IAX2 trunk mode (two calls sharing one header stack)
  fig09 — Increasing the voice payload (60-byte g.729 payload)
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1600, 900
INK = (26, 26, 26)          # #1A1A1A
ACCENT = (28, 93, 153)      # #1C5D99
ACCENT_L = (214, 226, 238)  # light accent fill
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
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


def title(d, text, y=64):
    f = font(SANS_B, 56)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W/2 - w/2, y + 74), (W/2 + w/2, y + 74)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)


def ctext(d, cx, y, text, f, fill=INK):
    w = d.textlength(text, font=f)
    d.text((cx - w/2, y), text, font=f, fill=fill)


def cbox_text(d, x, y, w, h, lines, f, fill=INK, lh=None):
    """centered, vertically-centered multiline text inside box [x,y,w,h]."""
    if lh is None:
        lh = f.size + 10
    total = lh * len(lines)
    yy = y + (h - total) / 2
    for ln in lines:
        ctext(d, x + w/2, yy, ln, f, fill)
        yy += lh


def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    s = 20
    d.polygon([p2, (p2[0]-s*math.cos(ang-0.4), p2[1]-s*math.sin(ang-0.4)),
               (p2[0]-s*math.cos(ang+0.4), p2[1]-s*math.sin(ang+0.4))], fill=fill)


# ---- fig01: Asterisk modular architecture ----
def fig01():
    img, d = canvas()
    title(d, "Asterisk Modular Architecture")
    fapi = font(SANS_B, 34)
    fblk = font(SANS_B, 32)
    fside = font(SANS, 27)
    fcap = font(SANS, 26)

    # Top API bar
    rbox(d, 360, 230, 880, 64, fill=ACCENT, outline=ACCENT, r=12)
    cbox_text(d, 360, 230, 880, 64, ["Asterisk Application API"], fapi, fill="white")
    # Bottom API bar (channels)
    rbox(d, 360, 690, 880, 64, fill=ACCENT, outline=ACCENT, r=12)
    cbox_text(d, 360, 690, 880, 64, ["Asterisk Channel API"], fapi, fill="white")
    # Left vertical API (codec translation)
    rbox(d, 300, 230, 56, 524, fill=ACCENT_L, outline=LINE, r=12)
    # rotated side labels
    def vlabel(text, cx, cy):
        tw = d.textlength(text, font=fside)
        tmp = Image.new("RGBA", (int(tw) + 8, fside.size + 10), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((4, 2), text, font=fside, fill=INK)
        tmp = tmp.rotate(90, expand=True)
        img.paste(tmp, (int(cx - tmp.width/2), int(cy - tmp.height/2)), tmp)
    vlabel("Codec Translation API", 328, 492)
    # Right vertical API (file format)
    rbox(d, 1244, 230, 56, 524, fill=ACCENT_L, outline=LINE, r=12)
    vlabel("File Format API", 1272, 492)

    # Core blocks in the middle
    blocks = [
        (430, 330, 320, 92, ["PBX Switching", "Core"]),
        (850, 330, 350, 92, ["Codec", "Translator"]),
        (430, 452, 320, 92, ["Application", "Launcher"]),
        (850, 452, 350, 92, ["Scheduler and", "I/O Manager"]),
        (430, 574, 320, 92, ["Dynamic Module", "Loader"]),
        (850, 574, 350, 92, ["Frame and", "Format API"]),
    ]
    for (x, y, w, h, lines) in blocks:
        rbox(d, x, y, w, h, fill=BOXBG, outline=INK, width=3, r=14)
        cbox_text(d, x, y, w, h, lines, fblk)

    # captions outside the side bars
    cbox_text(d, 30, 360, 250, 90,
              ["Applications:", "Voicemail, Conference,", "Directory, Billing"], fcap, fill=MUTED, lh=34)
    cbox_text(d, 1320, 360, 250, 90,
              ["Channels:", "PJSIP, IAX2, DAHDI,", "Local, Custom HW"], fcap, fill=MUTED, lh=34)
    cbox_text(d, 30, 560, 250, 90,
              ["Codecs:", "ulaw, alaw, G.722,", "G.729, Opus, GSM"], fcap, fill=MUTED, lh=34)
    cbox_text(d, 1320, 560, 250, 90,
              ["File formats:", "WAV, GSM, G.722,", "sln, Opus"], fcap, fill=MUTED, lh=34)
    save(img, "06-voip-network-fig01.png")


# ---- fig03: Peer / User / Friend ----
def fig03():
    img, d = canvas()
    title(d, "Peer, User, and Friend (Asterisk's view)")
    flab = font(SANS_B, 46)
    fdesc = font(SANS, 30)
    fast = font(SANS_B, 40)

    # Asterisk server box on the right
    sx, sy, sw, sh = 1170, 320, 300, 240
    rbox(d, sx, sy, sw, sh, fill=ACCENT, outline=ACCENT, r=20)
    cbox_text(d, sx, sy, sw, sh, ["Asterisk", "Server"], fast, fill="white")

    # phone icon (simple handset) on the left at three rows
    def phone(cx, cy):
        # simple deskphone: base + handset
        d.rounded_rectangle([cx-46, cy+6, cx+46, cy+40], radius=8, fill=INK)
        d.rounded_rectangle([cx-50, cy-34, cx+50, cy-6], radius=10, fill=INK)
        # handset cradle hint
        d.line([(cx-30, cy+6), (cx-30, cy-6)], fill="white", width=3)
        d.line([(cx+30, cy+6), (cx+30, cy-6)], fill="white", width=3)

    rows = [
        (250, "User", "Places calls to Asterisk", "out"),    # phone -> Asterisk
        (470, "Peer", "Receives calls from Asterisk", "in"),  # Asterisk -> phone
        (690, "Friend", "Makes and receives calls (user + peer)", "both"),
    ]
    px = 200
    for (cy, lab, desc, direction) in rows:
        phone(px, cy)
        # label pill in the middle
        lw = d.textlength(lab, font=flab)
        bx = 640
        rbox(d, bx - lw/2 - 30, cy - 44, lw + 60, 70, fill=ACCENT_L, outline=ACCENT, width=2, r=18)
        ctext(d, bx, cy - 30, lab, flab, fill=INK)
        ctext(d, bx, cy + 36, desc, fdesc, fill=MUTED)
        # arrows between phone and server
        ph_edge = (px + 60, cy)
        sv_edge = (sx, cy)
        if direction == "out":
            conn_arrow(d, ph_edge, sv_edge, INK)
        elif direction == "in":
            conn_arrow(d, sv_edge, ph_edge, INK)
        else:
            conn_arrow(d, ph_edge, sv_edge, ACCENT)
            conn_arrow(d, sv_edge, ph_edge, ACCENT)
    save(img, "06-voip-network-fig03.png")


# ---- fig04: PCM ----
def fig04():
    img, d = canvas()
    title(d, "PCM — Pulse Code Modulation")
    flab = font(SANS_B, 32)
    fsub = font(SANS, 28)

    midy = 470
    # analog sine on the left
    import math as m
    ax0, ax1 = 150, 470
    pts = []
    for i in range(ax1 - ax0 + 1):
        t = i / (ax1 - ax0)
        y = midy - 110 * m.sin(t * 2 * m.pi * 2)
        pts.append((ax0 + i, y))
    d.line(pts, fill=INK, width=4)
    d.line([(ax0, midy), (ax1, midy)], fill=LINE, width=2)
    cbox_text(d, ax0 - 20, midy + 150, 360, 70, ["Analog signal", "4000 Hz"], flab, lh=40)

    # accent arrow (codec)
    conn_arrow(d, (510, midy), (660, midy), ACCENT, width=8)
    cbox_text(d, 470, midy + 150, 250, 110,
              ["Codec:", "sample, quantize,", "encode"], fsub, fill=MUTED, lh=36)

    # sampled bars (PAM) on the right
    bx0, bx1 = 720, 1040
    n = 18
    for i in range(n + 1):
        t = i / n
        x = bx0 + (bx1 - bx0) * t
        y = midy - 110 * m.sin(t * 2 * m.pi * 2)
        d.line([(x, midy), (x, y)], fill=INK, width=6)
    d.line([(bx0, midy), (bx1, midy)], fill=LINE, width=2)
    cbox_text(d, bx0 - 20, midy + 150, 360, 110,
              ["8000 samples/s", "(Nyquist theorem)", "64 Kbps"], flab, lh=40)

    # accent arrow + bitstream
    conn_arrow(d, (1080, midy), (1230, midy), ACCENT, width=8)
    fbits = font(MONO, 40)
    cbox_text(d, 1250, midy - 30, 300, 60, ["01010..."], fbits, fill=INK)
    cbox_text(d, 1250, midy + 150, 300, 40, ["Digital bitstream"], fsub, fill=MUTED)
    save(img, "06-voip-network-fig04.png")


# ---- packet-strip helper ----
def _draw_packet(img, d, x, y, w, h, fields):
    total = sum(max(b, 3) for (_, b, _) in fields)
    flab = font(SANS, 22)
    cx = x
    for (text, b, kind) in fields:
        fw = w * max(b, 3) / total
        if kind == "pay":
            fill, oc = ACCENT_L, ACCENT
        else:
            fill, oc = BOXBG, INK
        d.rectangle([cx, y, cx + fw, y + h], fill=fill, outline=oc, width=2)
        ls = text.split("\n")
        lh = flab.size + 3
        tmp = Image.new("RGBA", (h - 14, max(int(fw) - 6, 24)), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        ty = (tmp.height - lh * len(ls)) / 2
        for ln in ls:
            lw = td.textlength(ln, font=flab)
            td.text(((tmp.width - lw) / 2, ty), ln, font=flab, fill=INK)
            ty += lh
        tmp = tmp.rotate(90, expand=True)
        gx = int(cx + (fw - tmp.width) / 2)
        gy = int(y + (h - tmp.height) / 2)
        img.paste(tmp, (gx, gy), tmp)
        cx += fw


# ---- fig05: single g.729 packet on Ethernet ----
def fig05():
    img, d = canvas()
    title(d, "A g.729 Voice Packet on Ethernet")
    fields = [
        ("Eth Dest\nAddr (6)", 6, "hdr"),
        ("Eth Src\nAddr (6)", 6, "hdr"),
        ("Eth\nType (2)", 2, "hdr"),
        ("IP\nHeader (20)", 20, "hdr"),
        ("UDP\nHeader (8)", 8, "hdr"),
        ("RTP\nHeader (12)", 12, "hdr"),
        ("Voice Payload\nG.729 (20)", 20, "pay"),
        ("Eth\nCRC (4)", 4, "hdr"),
    ]
    _draw_packet(img, d, 200, 250, 1200, 300, fields)
    fcap = font(SANS, 30)
    fbold = font(SANS_B, 34)
    cbox_text(d, 200, 600, 1200, 120, [
        "20 ms g.729 frame: 20 bytes payload + 58 bytes of headers = 78 bytes.",
        "Simple proportion: if 20 bytes = 8 Kbps, then 78 bytes = 31.2 Kbps.",
    ], fcap, fill=INK, lh=46)
    cbox_text(d, 200, 760, 1200, 50,
              ["A g.729 conversation on Ethernet consumes 31.2 Kbps."], fbold, fill=ACCENT)
    save(img, "06-voip-network-fig05.png")


# ---- fig08: IAX2 trunk mode ----
def fig08():
    img, d = canvas()
    title(d, "IAX2 Trunk Mode on Ethernet")
    fcap = font(SANS, 28)
    fbold = font(SANS_B, 30)

    # First call: full header stack (IAX2 instead of RTP)
    fields1 = [
        ("Eth Dest (6)", 6, "hdr"),
        ("Eth Src (6)", 6, "hdr"),
        ("Type (2)", 2, "hdr"),
        ("IP (20)", 20, "hdr"),
        ("UDP (8)", 8, "hdr"),
        ("IAX2 Hdr (12)", 12, "hdr"),
        ("Voice Payload\nG.729 (20)", 20, "pay"),
        ("Eth CRC (4)", 4, "hdr"),
    ]
    _draw_packet(img, d, 200, 215, 1200, 170, fields1)
    cbox_text(d, 200, 395, 1200, 40,
              ["First call: full header stack → 31.2 Kbps"], fbold, fill=INK)

    # Trunk frame: shared headers + two miniframes/payloads
    fields2 = [
        ("Eth Dest (6)", 6, "hdr"),
        ("Eth Src (6)", 6, "hdr"),
        ("Type (2)", 2, "hdr"),
        ("IP (20)", 20, "hdr"),
        ("UDP (8)", 8, "hdr"),
        ("IAX2 Hdr (12)", 12, "hdr"),
        ("Mini (4)", 4, "hdr"),
        ("Payload\nG.729 (20)", 20, "pay"),
        ("Mini (4)", 4, "hdr"),
        ("Payload (20)\n2nd call", 20, "pay"),
        ("CRC (4)", 4, "hdr"),
    ]
    _draw_packet(img, d, 200, 480, 1200, 170, fields2)
    cbox_text(d, 200, 665, 1200, 110, [
        "Trunk mode: later calls reuse the same header stack and add only a",
        "small IAX2 miniframe (4 bytes) + payload — about 9.6 Kbps per extra call.",
    ], fcap, fill=INK, lh=44)
    cbox_text(d, 200, 800, 1200, 40,
              ["Bandwidth = 31.2 + (N−1) × 9.6 Kbps"], fbold, fill=ACCENT)
    save(img, "06-voip-network-fig08.png")


# ---- fig09: increasing the voice payload ----
def fig09():
    img, d = canvas()
    title(d, "Increasing the Voice Payload")
    fields = [
        ("Eth Dest (6)", 6, "hdr"),
        ("Eth Src (6)", 6, "hdr"),
        ("Type (2)", 2, "hdr"),
        ("IP (20)", 20, "hdr"),
        ("UDP (8)", 8, "hdr"),
        ("RTP (12)", 12, "hdr"),
        ("Voice Payload  G.729 (60)", 60, "pay"),
        ("CRC (4)", 4, "hdr"),
    ]
    _draw_packet(img, d, 200, 250, 1200, 300, fields)
    fcap = font(SANS, 30)
    fbold = font(SANS_B, 34)
    cbox_text(d, 200, 600, 1200, 120, [
        "Pack 60 bytes of g.729 payload per packet (instead of 20) + 58 bytes headers = 138 bytes.",
        "Simple proportion: if 60 bytes = 8 Kbps, then 138 bytes = 16.05 Kbps.",
    ], fcap, fill=INK, lh=46)
    cbox_text(d, 200, 760, 1200, 50,
              ["Larger payload → 16.05 Kbps per call, at the cost of added latency."],
              fbold, fill=ACCENT)
    save(img, "06-voip-network-fig09.png")


if __name__ == "__main__":
    fig01(); fig03(); fig04(); fig05(); fig08(); fig09()
    print("done")
