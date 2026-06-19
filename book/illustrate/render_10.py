#!/usr/bin/env python3
"""
PATH-1 text/flow figures for chapter 10 (10-legacy-channels), rendered with Pillow in the
house style (white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900,
content current to Asterisk 22 (DAHDI, chan_dahdi.conf, libpri/libopenr2/libss7). Outputs to
book/illustrate/staging/ for review before swapping into src/images/.

This chapter is the Legacy Channels chapter: analog (FXS/FXO), digital (E1/T1 TDM, PCM),
MFC/R2 line+inter-register signalling, DAHDI architecture, and IAX2. Labels are cross-checked
against the chapter text (MFC/R2 ABCD line states, E1/T1 framing, IAX 4569 / 15-bit call no.).
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
ACCENT_BG = (224, 233, 242)
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


def title(d, text, y=60):
    f = font(SANS_B, 56)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W / 2 - w / 2, y + 74), (W / 2 + w / 2, y + 74)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def ctext(d, cx, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text((cx - w / 2, y), text, font=f, fill=fill)


def block_arrow(d, x, y, w, h, fill):
    head = h * 0.9
    bx = x + w - head
    d.polygon([(x, y - h / 2), (bx, y - h / 2), (bx, y - head / 2), (x + w, y),
               (bx, y + head / 2), (bx, y + h / 2), (x, y + h / 2)], fill=fill)


def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0]); s = 18
    d.polygon([p2, (p2[0] - s * math.cos(ang - 0.4), p2[1] - s * math.sin(ang - 0.4)),
               (p2[0] - s * math.cos(ang + 0.4), p2[1] - s * math.sin(ang + 0.4))], fill=fill)


def harrow(d, x1, x2, y, fill, width=4, dash=None, double=False):
    """Horizontal arrow from x1 to x2 (head at x2). dash=(on,off) for dashed line."""
    if dash:
        on, off = dash; x = min(x1, x2); xe = max(x1, x2); cur = x
        while cur < xe:
            d.line([(cur, y), (min(cur + on, xe), y)], fill=fill, width=width)
            cur += on + off
    else:
        d.line([(x1, y), (x2, y)], fill=fill, width=width)
    s = 16; dirn = 1 if x2 >= x1 else -1
    d.polygon([(x2, y), (x2 - dirn * s, y - s * 0.6), (x2 - dirn * s, y + s * 0.6)], fill=fill)
    if double:
        d.polygon([(x1, y), (x1 + dirn * s, y - s * 0.6), (x1 + dirn * s, y + s * 0.6)], fill=fill)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines


def asterisk_box(d, cx, cy, s=80, label="Asterisk"):
    """Simple flat 'Asterisk inside' server box with an asterisk glyph."""
    rbox(d, cx - s, cy - s, 2 * s, 2 * s, fill="white", outline=INK, width=3, r=12)
    # asterisk glyph
    fg = font(SANS_B, int(s * 1.3))
    ctext(d, cx, cy - s * 0.72, "*", fg, ACCENT)
    fl = font(SANS_B, 26)
    ctext(d, cx, cy + s * 0.45, label, fl, INK)


def phone(d, cx, cy, scale=1.0, fill=INK):
    """Minimal flat desk-phone glyph."""
    w = 70 * scale; h = 46 * scale
    rbox(d, cx - w / 2, cy - h / 2, w, h, fill="white", outline=fill, width=3, r=8)
    # handset
    d.rounded_rectangle([cx - w / 2 - 8 * scale, cy - h / 2 - 14 * scale,
                         cx + w / 2 + 8 * scale, cy - h / 2 - 4 * scale],
                        radius=6, fill=fill)
    # keypad dots
    for r in range(2):
        for c in range(3):
            dx = cx - 16 * scale + c * 16 * scale
            dy = cy - 6 * scale + r * 14 * scale
            d.ellipse([dx - 3 * scale, dy - 3 * scale, dx + 3 * scale, dy + 3 * scale], fill=fill)


def cloud(d, cx, cy, w, h, label, fill=BOXBG, outline=LINE):
    bumps = [(-0.42, 0.05, 0.30), (-0.15, -0.28, 0.34), (0.18, -0.30, 0.32),
             (0.42, 0.02, 0.30), (0.18, 0.28, 0.34), (-0.18, 0.30, 0.32), (0.0, 0.0, 0.42)]
    for bx, by, br in bumps:
        d.ellipse([cx + bx * w - br * h, cy + by * h - br * h,
                   cx + bx * w + br * h, cy + by * h + br * h], fill=fill, outline=outline, width=2)
    d.ellipse([cx - 0.5 * w, cy - 0.34 * h, cx + 0.5 * w, cy + 0.34 * h], fill=fill)
    fl = font(SANS_B, 34)
    ctext(d, cx, cy - 22, label, fl, INK)


# ---------------------------------------------------------------------------
# fig01: FXS / FXO analog roles
# ---------------------------------------------------------------------------
def fig01():
    img, d = canvas(); title(d, "FXS and FXO Analog Ports")
    cy = 480
    px, ax, tx = 270, 800, 1340
    phone(d, px, cy, scale=2.4)
    asterisk_box(d, ax, cy, s=110)
    cloud(d, tx, cy, 280, 170, "Telco")
    # links
    d.line([(px + 95, cy), (ax - 110, cy)], fill=INK, width=4)
    d.line([(ax + 110, cy), (tx - 150, cy)], fill=INK, width=4)
    fb = font(SANS_B, 40); fs = font(SANS, 30)
    ctext(d, (px + 95 + ax - 110) / 2, cy - 56, "FXS", fb, ACCENT)
    ctext(d, (ax + 110 + tx - 150) / 2, cy - 56, "FXO", fb, ACCENT)
    # RING + dial tone notes
    ctext(d, px, cy - 200, "RING", fb, INK)
    ctext(d, tx, cy - 230, "RING", fb, INK)
    ctext(d, (px + 95 + ax - 110) / 2, cy + 110, "FXS provides dial tone", fs, MUTED)
    ctext(d, (px + 95 + ax - 110) / 2, cy + 148, "and ringing to the phone", fs, MUTED)
    ctext(d, (ax + 110 + tx - 150) / 2, cy + 110, "FXO draws dial tone", fs, MUTED)
    ctext(d, (ax + 110 + tx - 150) / 2, cy + 148, "from the central office", fs, MUTED)
    save(img, "10-legacy-fig01.png")


# ---------------------------------------------------------------------------
# fig02: Asterisk as a VoIP gateway (OPX)
# ---------------------------------------------------------------------------
def fig02():
    img, d = canvas(); title(d, "Asterisk as a VoIP Gateway")
    cy = 470
    fb = font(SANS_B, 36); fs = font(SANS, 28)
    # legacy PBX (box)
    pbx_x = 200
    rbox(d, pbx_x - 70, cy - 90, 140, 180, fill="white", outline=INK, width=3, r=10)
    for i in range(3):
        d.rectangle([pbx_x - 50, cy - 60 + i * 40, pbx_x + 50, cy - 40 + i * 40],
                    outline=INK, width=2)
    ctext(d, pbx_x, cy - 140, "Legacy PBX", fb, INK)
    ctext(d, pbx_x, cy + 110, "Extension 1234", fs, MUTED)
    # gateway A
    gax = 560
    asterisk_box(d, gax, cy, s=90)
    # IP cloud
    cx_cloud = 800
    cloud(d, cx_cloud, cy - 10, 240, 150, "IP Network")
    # gateway B
    gbx = 1040
    asterisk_box(d, gbx, cy, s=90)
    # remote phone
    rpx = 1360
    phone(d, rpx, cy, scale=2.0)
    ctext(d, rpx, cy - 150, "RING", fb, INK)
    ctext(d, rpx, cy + 100, "Remote OPX 1234", fs, MUTED)
    # links
    d.line([(pbx_x + 70, cy), (gax - 90, cy)], fill=INK, width=4)
    ctext(d, (pbx_x + 70 + gax - 90) / 2, cy - 52, "FXO", fb, ACCENT)
    d.line([(gax + 90, cy - 10), (cx_cloud - 150, cy - 10)], fill=INK, width=4)
    d.line([(cx_cloud + 150, cy - 10), (gbx - 90, cy - 10)], fill=INK, width=4)
    d.line([(gbx + 90, cy), (rpx - 80, cy)], fill=INK, width=4)
    ctext(d, (gbx + 90 + rpx - 80) / 2, cy - 52, "FXS", fb, ACCENT)
    save(img, "10-legacy-fig02.png")


# ---------------------------------------------------------------------------
# fig05: How E1/T1 circuits are provisioned
# ---------------------------------------------------------------------------
def fig05():
    img, d = canvas(); title(d, "How E1/T1 Circuits Are Provisioned")
    # Telco block
    rbox(d, 130, 320, 320, 360, fill=ACCENT_BG, outline=ACCENT, width=3, r=18)
    ft = font(SANS_B, 60)
    ctext(d, 290, 470, "TELCO", ft, ACCENT)
    fb = font(SANS_B, 38); fs = font(SANS, 28)
    rx = 1240
    rows = [
        (390, "UTP", "HDSL modem (E1) /", "direct card connection (T1)"),
        (500, "Optical Fiber", "Optical MUX", "n x T1/E1"),
        (610, "Microwave Link", "Radio MUX", "n x T1/E1"),
    ]
    for y, mid, top, bot in rows:
        harrow(d, 450, rx - 200, y, ACCENT, width=5, double=True)
        ctext(d, (450 + rx - 200) / 2, y - 52, mid, fb, INK)
        # endpoint device box
        rbox(d, rx - 190, y - 40, 380, 80, fill=BOXBG, outline=LINE, width=2, r=10)
        ctext(d, rx, y - 30, top, fs, INK)
        ctext(d, rx, y + 4, bot, fs, MUTED)
    save(img, "10-legacy-fig05.png")


# ---------------------------------------------------------------------------
# fig07: PCM
# ---------------------------------------------------------------------------
def fig07():
    img, d = canvas(); title(d, "PCM — Pulse Code Modulation")
    fb = font(SANS_B, 32); fs = font(SANS, 28)
    cy = 470
    phone(d, 150, cy, scale=1.8)
    # analog sine
    ax0, ax1 = 250, 520
    pts = []
    for i in range(ax1 - ax0 + 1):
        t = i / (ax1 - ax0)
        pts.append((ax0 + i, cy - 120 * math.sin(t * 4 * math.pi)))
    d.line(pts, fill=INK, width=4)
    ctext(d, (ax0 + ax1) / 2, cy + 150, "Analog signal", fs, INK)
    ctext(d, (ax0 + ax1) / 2, cy + 184, "4 kHz", fs, MUTED)
    # arrow (codec)
    block_arrow(d, 560, cy, 230, 70, ACCENT)
    ctext(d, 675, cy + 150, "Sample &", fs, INK)
    ctext(d, 675, cy + 184, "quantize (codec)", fs, MUTED)
    # sampled sine (with vertical sample bars)
    sx0, sx1 = 830, 1100
    spts = []
    for i in range(sx1 - sx0 + 1):
        t = i / (sx1 - sx0)
        spts.append((sx0 + i, cy - 120 * math.sin(t * 4 * math.pi)))
    d.line(spts, fill=INK, width=3)
    for k in range(28):
        x = sx0 + k * (sx1 - sx0) / 28
        t = k / 28
        yv = cy - 120 * math.sin(t * 4 * math.pi)
        d.line([(x, cy), (x, yv)], fill=ACCENT, width=2)
    ctext(d, (sx0 + sx1) / 2, cy + 150, "8,000 samples/s", fs, INK)
    ctext(d, (sx0 + sx1) / 2, cy + 184, "(Nyquist)", fs, MUTED)
    # arrow to bits
    block_arrow(d, 1140, cy, 150, 60, ACCENT)
    fm = font(MONO, 40)
    d.text((1320, cy - 60), "01010", font=fm, fill=INK)
    ctext(d, 1420, cy + 60, "64 Kbps bits", fs, INK)
    save(img, "10-legacy-fig07.png")


# ---------------------------------------------------------------------------
# fig08: E1/T1 framing (TDM)
# ---------------------------------------------------------------------------
def fig08():
    img, d = canvas(); title(d, "TDM Framing — E1 vs T1")
    fb = font(SANS_B, 36); fs = font(SANS, 26); fsl = font(SANS, 18)

    def frame(y, n, x0, x1, hi_idx):
        rbox(d, x0, y, x1 - x0, 84, fill="white", outline=INK, width=3, r=4)
        step = (x1 - x0) / n
        for i in range(1, n):
            d.line([(x0 + i * step, y), (x0 + i * step, y + 84)], fill=INK, width=1)
        for idx, col in hi_idx:
            d.rectangle([x0 + idx * step + 1, y + 2, x0 + (idx + 1) * step - 1, y + 82], fill=col)
        return step

    # E1 frame: 32 timeslots, TS0 sync, TS16 signaling
    ctext(d, W / 2, 220, "E1 — 32 timeslots @ 2048 Kbps  (no robbed bits)", fb, INK)
    stepE = frame(270, 32, 200, 1400, [(0, ACCENT_BG), (16, ACCENT_BG)])
    conn_arrow(d, (200 + 0.5 * stepE, 420), (200 + 0.5 * stepE, 356), ACCENT, width=3)
    ctext(d, 200 + 0.5 * stepE, 430, "DS0 #0", fs, INK)
    ctext(d, 200 + 0.5 * stepE, 462, "frame sync", fsl, MUTED)
    conn_arrow(d, (200 + 16.5 * stepE, 420), (200 + 16.5 * stepE, 356), ACCENT, width=3)
    ctext(d, 200 + 16.5 * stepE, 430, "DS0 #16", fs, INK)
    ctext(d, 200 + 16.5 * stepE, 462, "signaling (CAS)", fsl, MUTED)

    # T1 frame: 24 timeslots
    ctext(d, W / 2, 580, "T1 — 24 timeslots @ 1544 Kbps", fb, INK)
    stepT = frame(630, 24, 200, 1400, [])
    note = "1 framing bit per frame; robbed-bit signaling (CAS) or the 24th channel as the D-channel (PRI/ISDN)"
    fy = 760
    for ln in wrap(d, note, fs, 1200):
        ctext(d, W / 2, fy, ln, fs, MUTED); fy += 34
    save(img, "10-legacy-fig08.png")


# ---------------------------------------------------------------------------
# fig09: DAHDI architecture (layered stack)
# ---------------------------------------------------------------------------
def fig09():
    img, d = canvas(); title(d, "DAHDI Software Architecture")
    x0, x1 = 430, 1170; w = x1 - x0
    fb = font(SANS_B, 40); fs = font(SANS, 26)

    def layer(y, h, label, fill, outline, txtcol):
        rbox(d, x0, y, w, h, fill=fill, outline=outline, width=3, r=12)
        ctext(d, W / 2, y + h / 2 - 24, label, fb, txtcol)
        return y + h + 18

    y = 200
    y = layer(y, 78, "Asterisk", "white", INK, INK)
    # chan_dahdi layer with the three protocol libs inside
    cy = y
    rbox(d, x0, cy, w, 130, fill=BOXBG, outline=INK, width=3, r=12)
    fm = font(MONO, 32)
    ctext(d, W / 2, cy + 14, "chan_dahdi", fm, INK)
    libs = [("libpri", "ISDN"), ("libopenr2", "MFC/R2"), ("libss7", "SS7")]
    lw = (w - 80) / 3
    fml = font(MONO, 26); fsl = font(SANS, 20)
    for i, (lib, proto) in enumerate(libs):
        lx = x0 + 25 + i * (lw + 7.5)
        rbox(d, lx, cy + 60, lw, 56, fill=ACCENT_BG, outline=ACCENT, width=2, r=8)
        ctext(d, lx + lw / 2, cy + 66, lib, fml, ACCENT)
        ctext(d, lx + lw / 2, cy + 94, proto, fsl, MUTED)
    y = cy + 130 + 18
    fm2 = font(MONO, 34)
    rbox(d, x0, y, w, 70, fill="white", outline=INK, width=3, r=12)
    ctext(d, W / 2, y + 16, "/dev/dahdi", fm2, INK); y += 88
    y = layer(y, 70, "DAHDI kernel driver", "white", INK, INK)
    y = layer(y, 70, "Card interface kernel driver", "white", INK, INK)
    save(img, "10-legacy-fig09.png")


# ---------------------------------------------------------------------------
# fig11: MFC/R2 call flow (sequence)
# ---------------------------------------------------------------------------
def fig11():
    img, d = canvas(); title(d, "MFC/R2 Call Flow (Asterisk ↔ Telco)")
    # four actors
    ext, ast, tel, rem = 130, 560, 1040, 1470
    fa = font(SANS_B, 26); fm = font(SANS, 21); fl = font(SANS, 18)
    top = 200; bot = 820
    for x, name in [(ext, "Extension"), (ast, "Asterisk"), (tel, "Telco"), (rem, "Telco Ext.")]:
        ctext(d, x, 168, name, fa, INK)
        d.line([(x, top), (x, bot)], fill=LINE, width=2)
    BLACK = INK; DASH = (on := 9, off := 7)
    y = top + 10
    GAP = 27

    def msg(x1, x2, label, y, dash=False, fill=BLACK, fnt=fm):
        harrow(d, x1, x2, y, fill, width=3, dash=(DASH if dash else None))
        ctext(d, (x1 + x2) / 2, y - 25, label, fnt, fill)

    # phase 1: off-hook / dial tone (in-band ext<->ast) + line state TS16 (ast<->tel dashed)
    msg(ext, ast, "Off-Hook", y); msg(ast, tel, "10  Idle", y, dash=True); y += GAP + 10
    msg(ast, ext, "Dial Tone", y); y += GAP
    msg(ext, ast, "Digit sent", y); y += GAP
    msg(ast, tel, "00  Seized", y, dash=True); y += GAP
    msg(tel, ast, "Seize Ack  11", y, dash=True); y += GAP + 6
    # phase 2: inter-register MF tones (in-band, ast<->tel solid)
    msg(ast, tel, "First digit (I-X)", y); y += GAP
    msg(tel, ast, "Send next digit (A-1)", y); y += GAP
    msg(ast, tel, "...  last digit (I-X)", y); y += GAP
    msg(tel, ast, "Address complete (A-3)", y); y += GAP
    msg(tel, ast, "Subscriber free, charge (B-6)", y); y += GAP + 6
    # phase 3: ringback to caller (audible), ring to called ext
    harrow(d, ast, ext, y, ACCENT, width=3)
    ctext(d, (ast + ext) / 2, y - 25, "Ringback (audible)", fm, ACCENT)
    msg(tel, rem, "Ring", y); y += GAP
    msg(rem, tel, "Off-Hook", y); y += GAP
    msg(tel, ast, "Answer  01", y, dash=True); y += GAP + 4
    # conversation
    harrow(d, ext, rem, y, ACCENT, width=3, double=True)
    ctext(d, (ext + rem) / 2, y - 25, "Conversation", fm, ACCENT); y += GAP + 6
    # teardown
    msg(rem, tel, "On-hook", y); y += GAP
    msg(tel, ast, "Clearback  11", y, dash=True); y += GAP
    msg(ast, tel, "10  Clear Forward", y, dash=True); y += GAP
    msg(ext, ast, "On-hook", y)
    # legend
    ly = 858
    d.line([(150, ly), (240, ly)], fill=INK, width=3)
    d.text((250, ly - 13), "In-band MF / audio", font=fl, fill=INK)
    harrow(d, 620, 700, ly, INK, width=3, dash=DASH)
    d.text((715, ly - 13), "Timeslot 16 line signaling (ABCD)", font=fl, fill=INK)
    d.line([(1230, ly), (1320, ly)], fill=ACCENT, width=3)
    d.text((1330, ly - 13), "Audible / voice", font=fl, fill=ACCENT)
    save(img, "10-legacy-fig11.png")


# ---------------------------------------------------------------------------
# fig12: IAX protocol multiplexing
# ---------------------------------------------------------------------------
def fig12():
    img, d = canvas(); title(d, "IAX2 Multiplexing Over a Single UDP Port")
    cy = 480
    fb = font(SANS_B, 34); fs = font(SANS, 28); fp = font(SANS, 26)
    lax, rax = 470, 1130
    asterisk_box(d, lax, cy, s=95)
    asterisk_box(d, rax, cy, s=95)
    cloud(d, 800, cy, 230, 150, "IP Network")
    # left phones
    for i, lbl in enumerate(["Call #1", "Call #2", "Call #n"]):
        py = cy - 130 + i * 130
        phone(d, 180, py, scale=1.5)
        ctext(d, 180, py + 50, lbl, fp, MUTED)
        d.line([(245, py), (lax - 95, cy - 60 + i * 60)], fill=INK, width=3)
    for i, lbl in enumerate(["Call #1", "Call #2", "Call #n"]):
        py = cy - 130 + i * 130
        phone(d, 1420, py, scale=1.5)
        ctext(d, 1420, py + 50, lbl, fp, MUTED)
        d.line([(rax + 95, cy - 60 + i * 60), (1355, py)], fill=INK, width=3)
    # single UDP link through cloud (accent)
    d.line([(lax + 95, cy), (685, cy)], fill=ACCENT, width=6)
    d.line([(915, cy), (rax - 95, cy)], fill=ACCENT, width=6)
    ctext(d, 800, cy + 110, "UDP port 4569", fb, ACCENT)
    ctext(d, 800, cy + 150, "15-bit call number keeps streams apart", fs, MUTED)
    save(img, "10-legacy-fig12.png")


# ---------------------------------------------------------------------------
# fig13: IAX vs SIP overhead
# ---------------------------------------------------------------------------
def fig13():
    img, d = canvas(); title(d, "Comparing IAX2 Trunk and SIP Overhead")
    fb = font(SANS_B, 30); fs = font(SANS, 24); ff = font(SANS, 16)

    def fields(x0, y, cells, h=150):
        total = sum(c[2] for c in cells)
        scale = 1.0
        x = x0
        for name, sub, wbytes, kind in cells:
            cw = wbytes * scale
            if kind == "pay":
                fill = ACCENT_BG; oc = ACCENT
            elif kind == "ovh":
                fill = (236, 238, 242); oc = LINE
            else:
                fill = BOXBG; oc = LINE
            d.rectangle([x, y, x + cw, y + h], fill=fill, outline=oc, width=2)
            # vertical text
            tmp = Image.new("RGBA", (h, int(cw)), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            lbl = f"{name} ({sub})" if sub else name
            lines = wrap(td, lbl, ff, h - 8)
            ty = 4
            for ln in lines:
                lw = td.textlength(ln, font=ff)
                td.text(((h - lw) / 2, ty), ln, font=ff, fill=(INK if kind != "pay" else ACCENT))
                ty += 18
            tmp = tmp.rotate(90, expand=True)
            img.paste(tmp, (int(x + cw / 2 - tmp.width / 2), int(y + h / 2 - tmp.height / 2)), tmp)
            x += cw
        return x

    # bytes scaled so rows fit; use real byte counts
    sip_cells = [("Eth Dst", "6", 28, "ovh"), ("Eth Src", "6", 28, "ovh"),
                 ("EthType", "2", 22, "ovh"), ("IP Hdr", "20", 60, "ovh"),
                 ("UDP", "8", 34, "ovh"), ("RTP", "12", 44, "ovh"),
                 ("Voice G.729", "20", 70, "pay"), ("Eth CRC", "4", 26, "ovh")]
    # Two SIP packets
    ctext(d, 470, 230, "Two SIP / RTP calls = two packets", fb, INK)
    x_end = fields(120, 280, sip_cells, h=130)
    fields(x_end + 40, 280, sip_cells, h=130)
    ctext(d, W / 2, 430, "40 bytes payload under 156 bytes of overhead", fs, MUTED)

    # One IAX2 trunk packet
    ctext(d, W / 2, 510, "Two IAX2 trunk calls = one packet", fb, INK)
    iax_cells = [("Eth Dst", "6", 28, "ovh"), ("Eth Src", "6", 28, "ovh"),
                 ("EthType", "2", 22, "ovh"), ("IP Hdr", "20", 60, "ovh"),
                 ("UDP", "8", 34, "ovh"), ("IAX2 Hdr", "12", 44, "shared"),
                 ("Mini", "4", 30, "shared"), ("Voice G.729", "20", 70, "pay"),
                 ("Mini", "4", 30, "shared"), ("Voice #2", "20", 70, "pay"),
                 ("Eth CRC", "4", 26, "ovh")]
    fields(360, 560, iax_cells, h=150)
    ctext(d, W / 2, 740, "40 bytes payload under just 66 bytes of overhead", fs, MUTED)
    save(img, "10-legacy-fig13.png")


# ---------------------------------------------------------------------------
# fig14: IAX trunk to a VoIP provider
# ---------------------------------------------------------------------------
def fig14():
    img, d = canvas(); title(d, "IAX Trunk to a VoIP Provider")
    cy = 500
    fb = font(SANS_B, 34); fs = font(SANS, 28)
    asterisk_box(d, 300, cy, s=110)
    ctext(d, 300, cy + 150, "Customer's Asterisk", fs, MUTED)
    cloud(d, 800, cy, 280, 170, "Internet")
    # provider building
    px = 1300
    rbox(d, px - 90, cy - 120, 180, 240, fill="white", outline=INK, width=3, r=8)
    for r in range(3):
        for c in range(3):
            d.rectangle([px - 60 + c * 40, cy - 90 + r * 60, px - 30 + c * 40, cy - 50 + r * 60],
                        outline=INK, width=2)
    ctext(d, px, cy + 150, "VoIP Provider", fs, MUTED)
    # single IAX trunk
    d.line([(410, cy), (640, cy)], fill=ACCENT, width=6)
    d.line([(960, cy), (px - 90, cy)], fill=ACCENT, width=6)
    ctext(d, 525, cy - 48, "IAX Trunk", fb, ACCENT)
    ctext(d, 1075, cy - 48, "IAX Trunk", fb, ACCENT)
    ctext(d, 800, cy + 200, "A single trunk carries all calls to and from the provider", fs, MUTED)
    save(img, "10-legacy-fig14.png")


# ---------------------------------------------------------------------------
# fig15: two Asterisk servers over an IAX trunk
# ---------------------------------------------------------------------------
def fig15():
    img, d = canvas(); title(d, "Connecting Two Asterisk Servers (IAX Trunk)")
    cy = 430
    fb = font(SANS_B, 36); fs = font(SANS, 28); fp = font(SANS, 26)
    hq, br = 470, 1130
    asterisk_box(d, hq, cy, s=110)
    asterisk_box(d, br, cy, s=110)
    ctext(d, hq, cy - 175, "HQ", fb, INK)
    ctext(d, hq, cy - 138, "192.168.1.1", fs, MUTED)
    ctext(d, br, cy - 175, "Branch", fb, INK)
    ctext(d, br, cy - 138, "192.168.1.2", fs, MUTED)
    # trunk
    d.line([(hq + 110, cy), (br - 110, cy)], fill=ACCENT, width=6)
    ctext(d, W / 2, cy - 46, "IAX Trunk", fb, ACCENT)
    # phones below each server
    for x, exts in [(hq, ["2000", "2001"]), (br, ["2200", "2201"])]:
        for i, e in enumerate(exts):
            pxp = x - 80 + i * 160
            py = cy + 230
            phone(d, pxp, py, scale=1.6)
            d.line([(x, cy + 110), (pxp, py - 40)], fill=INK, width=2)
            ctext(d, pxp, py + 50, e, fp, MUTED)
    ctext(d, W / 2, cy + 300, "No registration — both IP addresses are fixed and known", fs, MUTED)
    save(img, "10-legacy-fig15.png")


# ---------------------------------------------------------------------------
# fig16: IAX authentication decision flow
# ---------------------------------------------------------------------------
def fig16():
    img, d = canvas(); title(d, "IAX Authentication Decision Flow")
    fs = font(SANS, 19); fy = font(SANS_B, 17); fd = font(SANS_B, 22)
    GREEN = (224, 238, 226); GO = (60, 130, 80)
    RED = (244, 230, 230); RO = (170, 70, 70)

    def diamond(cx, cy, label, w=160, h=96):
        d.polygon([(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)],
                  fill=BOXBG, outline=INK, width=3)
        lines = wrap(d, label, fs, w - 30)
        ty = cy - len(lines) * 12
        for ln in lines:
            ctext(d, cx, ty, ln, fs, INK); ty += 24

    def box(cx, cy, label, fill, oc, w=200, h=84):
        rbox(d, cx - w / 2, cy - h / 2, w, h, fill=fill, outline=oc, width=3, r=12)
        lines = wrap(d, label, fs, w - 24)
        ty = cy - len(lines) * 12
        for ln in lines:
            ctext(d, cx, ty, ln, fs, INK); ty += 23

    def lbl(x, y, t, col=ACCENT):
        d.text((x, y), t, font=fy, fill=col)

    # ---- top row: username -> match -> IP -> secret -> ACCEPT ----
    y1 = 330
    xs = [225, 460, 700, 940]
    labels = ["Username provided?", "Matches a section?", "Source IP allowed?", "Secret matches?"]
    for x, t in zip(xs, labels):
        diamond(x, y1, t)
    # entry
    d.text((70, y1 - 14), "IAX call", font=fd, fill=INK)
    harrow(d, 160, xs[0] - 83, y1, INK, width=3)
    # YES chain
    for a, b in [(0, 1), (1, 2), (2, 3)]:
        harrow(d, xs[a] + 83, xs[b] - 83, y1, INK, width=3)
        lbl((xs[a] + xs[b]) / 2 - 16, y1 - 34, "YES", GO)
    # ACCEPT (secret matches YES)
    acc_x = 1230
    box(acc_x, y1, "ACCEPT  —  use the matched section's context + peer options",
        GREEN, GO, w=290, h=150)
    harrow(d, xs[3] + 83, acc_x - 145, y1, GO, width=3); lbl(xs[3] + 95, y1 - 34, "YES", GO)
    # DENY (top): NO from match / IP / secret all go up to one rail -> DENY box
    deny_y = 195; deny_x = 1230
    box(deny_x, deny_y, "DENY CALL", RED, RO, w=180, h=72)
    rail_y = deny_y + 70
    for i in [1, 2, 3]:
        d.line([(xs[i], y1 - 48), (xs[i], rail_y)], fill=RO, width=3)
        lbl(xs[i] + 10, y1 - 96, "NO", RO)
    d.line([(xs[1], rail_y), (deny_x, rail_y)], fill=RO, width=3)
    conn_arrow(d, (deny_x, rail_y), (deny_x, deny_y + 38), RO, width=3)

    # ---- lower branch: no username -> guest -> secret matches a user ----
    y2 = 540; y3 = 730
    conn_arrow(d, (xs[0], y1 + 48), (xs[0], y2 - 48), INK, width=3); lbl(xs[0] + 12, y1 + 62, "NO", INK)
    diamond(xs[0], y2, "Guest user exists?")
    box(575, y2, "ALLOW as guest", GREEN, GO, w=210, h=72)
    harrow(d, xs[0] + 83, 472, y2, GO, width=3); lbl(xs[0] + 100, y2 - 34, "YES", GO)
    conn_arrow(d, (xs[0], y2 + 48), (xs[0], y3 - 48), INK, width=3); lbl(xs[0] + 12, y2 + 62, "NO", INK)
    diamond(xs[0], y3, "Secret matches a user?")
    # YES -> accept
    box(575, y3, "ACCEPT  —  use that user's context + peer options", GREEN, GO, w=230, h=110)
    harrow(d, xs[0] + 83, 462, y3, GO, width=3); lbl(xs[0] + 100, y3 - 34, "YES", GO)
    # NO -> deny (down-left)
    box(xs[0], y3 + 130, "DENY CALL", RED, RO, w=180, h=68)
    conn_arrow(d, (xs[0], y3 + 48), (xs[0], y3 + 94), RO, width=3); lbl(xs[0] + 12, y3 + 60, "NO", RO)
    save(img, "10-legacy-fig16.png")


# ---------------------------------------------------------------------------
# fig17: jitter buffer as a water tank
# ---------------------------------------------------------------------------
def fig17():
    img, d = canvas(); title(d, "The Jitter Buffer")
    fb = font(SANS_B, 30); fs = font(SANS, 26)
    # tank
    tank_l, tank_r = 560, 1120; top = 430; bottom = 760
    fill_level = 600
    # water (accent)
    d.rectangle([tank_l, fill_level, tank_r, bottom], fill=ACCENT_BG)
    d.line([(tank_l, top), (tank_l, bottom)], fill=INK, width=6)
    d.line([(tank_r, top), (tank_r, bottom)], fill=INK, width=6)
    d.line([(tank_l, bottom), (tank_r, bottom)], fill=INK, width=6)
    # incoming pipe + irregular drops
    d.rounded_rectangle([220, 330, 560, 390], radius=24, fill=(225, 228, 233), outline=INK, width=3)
    # pipe mouth
    d.ellipse([544, 332, 576, 388], fill="white", outline=INK, width=3)
    for dx, dy in [(0, 20), (35, 55), (15, 90), (55, 105), (30, 145)]:
        d.ellipse([568 + dx, 390 + dy, 588 + dx, 410 + dy], fill=ACCENT)
    ctext(d, 380, 250, "Packets arrive irregularly", fs, INK)
    ctext(d, 380, 286, "from the network", fs, MUTED)
    # outflow at bottom right (steady)
    block_arrow(d, tank_r, bottom - 30, 320, 70, ACCENT)
    ctext(d, tank_r + 170, bottom + 30, "steady voice flow", fs, ACCENT)
    # dimension: buffer size (full height)
    dim_x = 470
    d.line([(dim_x, top), (dim_x, bottom)], fill=INK, width=3)
    conn_arrow(d, (dim_x, top + 30), (dim_x, top), INK, width=3)
    conn_arrow(d, (dim_x, bottom - 30), (dim_x, bottom), INK, width=3)
    tmp = Image.new("RGBA", (340, 40), (0, 0, 0, 0)); td = ImageDraw.Draw(tmp)
    td.text((0, 0), "Jitter buffer size (ms)", font=fb, fill=INK)
    tmp = tmp.rotate(90, expand=True)
    img.paste(tmp, (dim_x - 60, (top + bottom) // 2 - tmp.height // 2), tmp)
    # excess band (top -> fill level)
    dim_x2 = 540
    d.line([(dim_x2, top), (dim_x2, fill_level)], fill=ACCENT, width=3)
    conn_arrow(d, (dim_x2, top + 24), (dim_x2, top), ACCENT, width=3)
    conn_arrow(d, (dim_x2, fill_level - 24), (dim_x2, fill_level), ACCENT, width=3)
    ctext(d, 800, top - 12, "Excess buffer band", fs, ACCENT)
    conn_arrow(d, (700, top + 4), (dim_x2 + 6, (top + fill_level) // 2 - 30), ACCENT, width=2)
    save(img, "10-legacy-fig17.png")


if __name__ == "__main__":
    fig01(); fig02(); fig05(); fig07(); fig08(); fig09()
    fig11(); fig12(); fig13(); fig14(); fig15(); fig16(); fig17()
    print("done")
