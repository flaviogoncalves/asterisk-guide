#!/usr/bin/env python3
"""
PATH-1 flow/architecture figures for chapter 18 (18-realtime), rendered with Pillow in the
house style (white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900,
content current to Asterisk 22 / PJSIP / Sorcery. Outputs to book/illustrate/staging/ for
review before swapping into src/images/.

fig01: ARA architecture — config files + static DB tables load at start; realtime DB tables
       are read on demand during a call.
fig02: Building a dialplan with ARA — extensions.conf `switch => realtime` pulls extension
       rows (context, exten, priority, app, data) from a database table. Uses PJSIP/ (not SIP/).
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
LINE = (170, 178, 190)
DBFILL = (233, 240, 247)
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
    f = font(SANS_B, 56)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W / 2 - w / 2, y + 76), (W / 2 + w / 2, y + 76)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)


def conn_arrow(d, p1, p2, fill, width=6):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    s = 22
    d.polygon([p2, (p2[0] - s * math.cos(ang - 0.42), p2[1] - s * math.sin(ang - 0.42)),
               (p2[0] - s * math.cos(ang + 0.42), p2[1] - s * math.sin(ang + 0.42))], fill=fill)


def ctext(d, cx, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text((cx - w / 2, y), text, font=f, fill=fill)


def db_cylinder(d, cx, top, w, h, fill=DBFILL, outline=ACCENT, width=3):
    """Flat database cylinder centered horizontally at cx."""
    x0, x1 = cx - w / 2, cx + w / 2
    ell = w * 0.28  # ellipse vertical extent
    # body
    d.rectangle([x0, top + ell / 2, x1, top + h - ell / 2], fill=fill, outline=None)
    d.line([(x0, top + ell / 2), (x0, top + h - ell / 2)], fill=outline, width=width)
    d.line([(x1, top + ell / 2), (x1, top + h - ell / 2)], fill=outline, width=width)
    # bottom arc
    d.arc([x0, top + h - ell, x1, top + h], 0, 180, fill=outline, width=width)
    # top ellipse
    d.ellipse([x0, top, x1, top + ell], fill=fill, outline=outline, width=width)


def doc_stack(d, x, y, w, h, n=3, gap=16):
    """A small stack of document sheets (flat, dog-eared)."""
    for i in range(n - 1, -1, -1):
        ox, oy = x + i * gap, y - i * gap
        fold = 30
        # body with folded corner
        d.polygon([(ox, oy), (ox + w - fold, oy), (ox + w, oy + fold),
                   (ox + w, oy + h), (ox, oy + h)],
                  fill="white", outline=INK)
        # fold triangle
        d.polygon([(ox + w - fold, oy), (ox + w - fold, oy + fold), (ox + w, oy + fold)],
                  fill=BOXBG, outline=INK)
    return x, y, w, h  # geometry of frontmost (i=0)


# ---- fig01: ARA architecture ----
def fig01():
    img, d = canvas()
    title(d, "Asterisk Real Time Architecture")
    fc = font(MONO, 30)
    flab = font(SANS_B, 34)
    fsub = font(SANS, 28)

    # Central Asterisk box
    ax, ay, aw, ah = W / 2 - 150, 380, 300, 150
    rbox(d, ax, ay, aw, ah, fill=ACCENT, outline=ACCENT, r=22)
    fa = font(SANS_B, 46)
    ctext(d, W / 2, ay + 40, "Asterisk", fa, "white")
    ctext(d, W / 2, ay + 96, "(res_pjsip / Sorcery)", font(SANS, 24), (220, 230, 242))

    # LEFT: config files -> load at start
    dx, dy, dw, dh = 120, 360, 200, 150
    doc_stack(d, dx, dy, dw, dh, n=3, gap=18)
    files = ["pjsip.conf", "extensions.conf", "extconfig.conf"]
    fy = dy + 40
    for fn in files:
        d.text((dx + 60, fy), fn, font=font(MONO, 24), fill=INK)
        fy += 34
    ctext(d, dx + dw / 2 + 18, dy + dh + 30, "Configuration files", flab, INK)
    ctext(d, dx + dw / 2 + 18, dy + dh + 70, "Loaded when Asterisk starts", fsub, MUTED)
    conn_arrow(d, (dx + dw + 36, ay + ah / 2), (ax - 14, ay + ah / 2), INK, width=6)

    # TOP-RIGHT: realtime DB tables -> read on demand
    rcx, rtop = 1230, 175
    db_cylinder(d, rcx, rtop, 170, 150)
    ctext(d, rcx, rtop + 168, "Realtime tables", flab, ACCENT)
    ctext(d, rcx, rtop + 208, "ps_endpoints, ps_aors,", font(MONO, 24), INK)
    ctext(d, rcx, rtop + 240, "ps_auths, ps_contacts ...", font(MONO, 24), INK)
    ctext(d, rcx, rtop + 280, "Read on demand during a call", fsub, MUTED)
    conn_arrow(d, (rcx - 90, rtop + 130), (ax + aw - 8, ay + 40), ACCENT, width=6)

    # BOTTOM-RIGHT: static DB tables -> load at start
    scx, stop = 1230, 560
    db_cylinder(d, scx, stop, 170, 150)
    ctext(d, scx, stop + 168, "Static tables", flab, INK)
    ctext(d, scx, stop + 208, "(config files stored in DB)", font(SANS, 24), MUTED)
    ctext(d, scx, stop + 244, "Loaded when Asterisk starts", fsub, MUTED)
    conn_arrow(d, (scx - 90, stop + 60), (ax + aw - 8, ay + ah - 40), INK, width=6)

    save(img, "18-realtime-fig01.png")


# ---- fig02: building a dialplan with ARA ----
def fig02():
    img, d = canvas()
    title(d, "Building a Dial Plan with Real Time")
    fcode = font(MONO, 28)
    fcap = font(SANS_B, 32)

    # LEFT: extensions.conf document
    dx, dy, dw, dh = 110, 230, 470, 470
    fold = 50
    d.polygon([(dx, dy), (dx + dw - fold, dy), (dx + dw, dy + fold),
               (dx + dw, dy + dh), (dx, dy + dh)], fill="white", outline=INK, width=2)
    d.polygon([(dx + dw - fold, dy), (dx + dw - fold, dy + fold), (dx + dw, dy + fold)],
              fill=BOXBG, outline=INK)
    lines = ["[default]", "exten => ...", "exten => ...", "",
             "switch => realtime/ramais@extensions"]
    ly = dy + 110
    for ln in lines:
        col = ACCENT if ln.startswith("switch") else INK
        ft = font(MONO, 26) if ln.startswith("switch") else fcode
        d.text((dx + 40, ly), ln, font=ft, fill=col)
        ly += 56
    ctext(d, dx + dw / 2, dy + dh + 24, "extensions.conf", fcap, INK)

    # arrow into DB
    conn_arrow(d, (dx + dw + 30, dy + dh / 2), (760, dy + dh / 2 + 10), ACCENT, width=7)

    # RIGHT: database cylinder + extension table
    dbcx, dbtop = 980, 470
    db_cylinder(d, dbcx, dbtop, 200, 180)
    ctext(d, dbcx, dbtop + 196, "extensions table", font(SANS_B, 28), ACCENT)

    # extension table (above the cylinder)
    cols = ["context", "exten", "priority", "app", "data"]
    widths = [180, 130, 130, 110, 200]
    row = ["ramais", "4000", "1", "Dial", "PJSIP/4000"]
    tx, ty = 760, 180
    th = 56
    ch = font(SANS_B, 26)
    cb = font(MONO, 26)
    # header
    cx = tx
    for c, w in zip(cols, widths):
        d.rectangle([cx, ty, cx + w, ty + th], fill=BOXBG, outline=LINE, width=2)
        ctext(d, cx + w / 2, ty + 13, c, ch, INK)
        cx += w
    # data row
    cx = tx
    for v, w in zip(row, widths):
        d.rectangle([cx, ty + th, cx + w, ty + 2 * th], fill="white", outline=LINE, width=2)
        col = ACCENT if v.startswith("PJSIP") else INK
        ctext(d, cx + w / 2, ty + th + 13, v, cb, col)
        cx += w

    save(img, "18-realtime-fig02.png")


if __name__ == "__main__":
    fig01()
    fig02()
    print("done")
