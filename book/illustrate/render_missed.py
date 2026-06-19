#!/usr/bin/env python3
"""
PATH-1 figures missed by earlier passes, rendered with Pillow in the house style
(white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900.

GROUP A (04-first-pbx, Asterisk 22 syntax/reference slides):
  04-first-pbx-fig05  extension syntax
  04-first-pbx-fig06  pattern-matching characters + examples
  04-first-pbx-fig08  Asterisk expressions overview

GROUP B (10-legacy-channels, legacy chan_sip content kept faithful):
  07-sip-and-pjsip-fig07  Asterisk -> VoIP provider over Internet/WAN
  07-sip-and-pjsip-fig08  two Asterisk servers over SIP (4400/4401 <-> 4500/4501)
  07-sip-and-pjsip-fig09  connecting SIP servers by domain
  07-sip-and-pjsip-fig10  legacy chan_sip authentication decision flow
  07-sip-and-pjsip-fig13  Asterisk behind NAT

Outputs to book/illustrate/staging/ for review before swapping into src/images/.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
LINE = (170, 178, 190)
ACCENT_BG = (224, 234, 244)
DENYBG = (232, 224, 224)
OUT = os.path.join(os.path.dirname(__file__), "staging")
os.makedirs(OUT, exist_ok=True)

SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc"]
SANS_B = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
          "/System/Library/Fonts/Helvetica.ttc"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Monaco.ttf"]
MONO_B = ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
          "/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"]


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
    f = font(SANS_B, 58)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W/2 - w/2, y + 78), (W/2 + w/2, y + 78)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def conn_arrow(d, p1, p2, fill, width=5, head=18):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    s = head
    d.polygon([p2, (p2[0]-s*math.cos(ang-0.4), p2[1]-s*math.sin(ang-0.4)),
               (p2[0]-s*math.cos(ang+0.4), p2[1]-s*math.sin(ang+0.4))], fill=fill)


def dbl_arrow(d, p1, p2, fill, width=5, head=16):
    conn_arrow(d, p1, p2, fill, width, head)
    conn_arrow(d, p2, p1, fill, width, head)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)


def ctext(d, cx, cy, text, f, fill=INK):
    w = d.textlength(text, font=f)
    asc, desc = f.getmetrics()
    d.text((cx - w/2, cy - (asc+desc)/2), text, font=f, fill=fill)


def ctext_lines(d, cx, cy, lines, f, fill=INK, lh=None):
    asc, desc = f.getmetrics()
    lh = lh or (asc + desc + 6)
    total = lh * len(lines)
    y0 = cy - total/2
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=f)
        d.text((cx - w/2, y0 + i*lh), ln, font=f, fill=fill)


# ---------- house-style flat icons ----------
def server_icon(d, cx, cy, w=120, h=150, accent=False):
    """Flat tower/server icon, house style."""
    x0, y0 = cx - w/2, cy - h/2
    body = ACCENT if accent else (255, 255, 255)
    edge = ACCENT if accent else INK
    rbox(d, x0, y0, w, h, fill=body, outline=edge, width=4, r=12)
    lc = (255, 255, 255) if accent else INK
    for i in range(3):
        yy = y0 + 22 + i*16
        d.line([(x0+18, yy), (x0+w-18, yy)], fill=lc, width=4)
    d.ellipse([x0+18, y0+h-34, x0+34, y0+h-18], outline=lc, width=4)


def phone_icon(d, cx, cy, s=46):
    """Flat desk-phone icon, house style line art."""
    x0, y0 = cx - s, cy - s*0.5
    # base
    rbox(d, x0, y0+s*0.5, s*2, s*0.6, fill=(255, 255, 255), outline=INK, width=4, r=8)
    # handset (rounded bar)
    d.rounded_rectangle([x0+s*0.1, y0, x0+s*1.9, y0+s*0.36], radius=s*0.18,
                        outline=INK, width=4, fill=(255, 255, 255))
    # keypad dots
    for r in range(2):
        for c in range(3):
            dx = x0 + s*0.55 + c*s*0.45
            dy = y0 + s*0.62 + r*s*0.28
            d.ellipse([dx-3, dy-3, dx+3, dy+3], fill=INK)


def firewall_icon(d, cx, cy, w=130, h=150):
    """Flat brick-wall firewall icon."""
    x0, y0 = cx - w/2, cy - h/2
    rbox(d, x0, y0, w, h, fill=(255, 255, 255), outline=INK, width=4, r=10)
    rows = 5
    rh = (h-8) / rows
    for i in range(1, rows):
        yy = y0 + 4 + i*rh
        d.line([(x0+4, yy), (x0+w-4, yy)], fill=INK, width=3)
    for i in range(rows):
        yy = y0 + 4 + i*rh
        off = (w-8)/2 if i % 2 else 0
        for vx in (x0+4+off, x0+4+off + (w-8)/2):
            if x0+4 < vx < x0+w-4:
                d.line([(vx, yy), (vx, yy+rh)], fill=INK, width=3)


def cloud_icon(d, cx, cy, w=320, h=170, lines=None):
    """Flat network 'cloud' drawn as one clean blob (no internal seams).

    Render the union of overlapping circles on a mask, paste a white interior,
    then stroke the blob edge by taking (mask - eroded mask) and painting it ink.
    """
    from PIL import ImageFilter
    img = d._image
    pad = 16
    bx0, by0 = int(cx - w/2 - pad), int(cy - h/2 - pad)
    bw, bh = int(w + 2*pad), int(h + 2*pad)
    mask = Image.new("L", (bw, bh), 0)
    md = ImageDraw.Draw(mask)
    lcx, lcy = bw/2, bh/2
    bumps = [(-0.30, 0.06, 0.40), (-0.04, -0.20, 0.50), (0.28, 0.02, 0.44),
             (0.06, 0.22, 0.52), (0.32, 0.20, 0.34), (-0.30, 0.24, 0.32)]
    for fx, fy, fr in bumps:
        rx = w*fr/2
        ex, ey = lcx + fx*w, lcy + fy*h
        md.ellipse([ex-rx, ey-rx, ex+rx, ey+rx], fill=255)
    # white interior
    img.paste(Image.new("RGB", (bw, bh), (255, 255, 255)), (bx0, by0), mask)
    # edge band = mask minus eroded mask (~4px stroke)
    eroded = mask.filter(ImageFilter.MinFilter(9))
    edge = Image.new("L", (bw, bh), 0)
    edge.paste(mask)
    edge = Image.composite(Image.new("L", (bw, bh), 0), mask, eroded)
    img.paste(Image.new("RGB", (bw, bh), INK), (bx0, by0), edge)
    if lines:
        ctext_lines(d, cx, cy, lines, font(SANS_B, 30))


# =====================================================================
# GROUP A — 04-first-pbx
# =====================================================================

def fig05():
    """Extension syntax + extension format + priority format."""
    img, d = canvas()
    title(d, "Extension Syntax")

    # syntax line (mono), centered
    fsyn_lit = font(MONO_B, 34)
    fsyn = font(MONO, 34)
    syntax = "exten => number(name),{priority|label}[(alias)],application"
    w = d.textlength(syntax, font=fsyn)
    x = (W - w) / 2
    y = 200
    rbox(d, x-30, y-18, w+60, 64, fill=ACCENT_BG, outline=ACCENT, width=2, r=14)
    d.text((x, y), syntax, font=fsyn, fill=INK)

    # two columns of tables
    colL, colR = 130, 830
    cw = 640
    # Extension format
    fhdr = font(SANS_B, 36)
    fk = font(MONO, 30)
    fv = font(SANS, 30)
    d.text((colL, 320), "Extension format", font=fhdr, fill=ACCENT)
    exrows = [("4001", "Numeric"),
              ("alexander", "Alphanumeric"),
              ("4321/1234", "Number with caller ID"),
              ("_4XXX", "Pattern matching"),
              ("s", "Standard")]
    yy = 380
    for k, v in exrows:
        d.text((colL, yy), k, font=fk, fill=INK)
        d.text((colL+330, yy), v, font=fv, fill=INK)
        yy += 56

    # Priority format
    d.text((colR, 320), "Priority format", font=fhdr, fill=ACCENT)
    prows = [("1", "First priority"),
             ("n", "Next priority"),
             ("s", "Same priority"),
             ("n+x / n-x", "Offset from next"),
             ("hint", "Used with presence (BLF)")]
    yy = 380
    for k, v in prows:
        d.text((colR, yy), k, font=fk, fill=INK)
        d.text((colR+300, yy), v, font=fv, fill=INK)
        yy += 56

    # footnote: modern syntax uses commas
    fnote = font(SANS, 24)
    note = "Asterisk 22 uses commas as field separators; pattern extensions begin with _ ."
    ctext(d, W/2, 840, note, fnote, fill=MUTED)
    save(img, "04-first-pbx-fig05.png")


def fig06():
    """Pattern-matching characters and examples."""
    img, d = canvas()
    title(d, "Pattern Matching")

    fk = font(MONO_B, 32)
    fv = font(SANS, 30)
    chars = [("_", "Starts a pattern (first character)"),
             (".", "Matches one or more characters"),
             ("!", "Matches zero or more characters"),
             ("[123-7]", "Any listed digit or range (1, 2, 3 to 7)"),
             ("X", "Any digit from 0 to 9"),
             ("Z", "Any digit from 1 to 9"),
             ("N", "Any digit from 2 to 9")]
    x_k, x_v, y = 150, 440, 170
    for k, v in chars:
        d.text((x_k, y), k, font=fk, fill=ACCENT)
        d.text((x_v, y), v, font=fv, fill=INK)
        y += 46

    # examples table
    fhdr = font(SANS_B, 32)
    d.text((150, 530), "Examples", font=fhdr, fill=ACCENT)
    fc = font(MONO, 26)
    fd = font(SANS, 26)
    d.text((150, 580), "Pattern", font=font(SANS_B, 26), fill=MUTED)
    d.text((520, 580), "Description", font=font(SANS_B, 26), fill=MUTED)
    ex = [("_61XX", "Sao Paulo office (6100–6199)"),
          ("_62XX", "San Francisco office (6200–6299)"),
          ("_63XX", "New York office (6300–6399)"),
          ("_7[1-3]XX", "Bangalore office (7100–7399)"),
          ("_7[04-9]XX", "Beijing office (7000–7099, 7400–7999)"),
          ("_9.", "Any number starting with 9"),
          ("_9XXXXXXX", "Any 8-digit number starting with 9")]
    y = 620
    for k, v in ex:
        d.text((150, y), k, font=fc, fill=INK)
        d.text((520, y), v, font=fd, fill=INK)
        y += 38
    save(img, "04-first-pbx-fig06.png")


def fig08a():
    """Asterisk expressions overview (04-first-pbx-fig08)."""
    img, d = canvas()
    title(d, "Asterisk Expressions")

    fsyn = font(MONO_B, 40)
    syntax = "$[expression1 operator expression2]"
    w = d.textlength(syntax, font=fsyn)
    x = (W - w)/2
    y = 195
    rbox(d, x-34, y-16, w+68, 70, fill=ACCENT_BG, outline=ACCENT, width=2, r=14)
    d.text((x, y), syntax, font=fsyn, fill=INK)

    fhdr = font(SANS_B, 34)
    fv = font(SANS, 30)
    groups = [("Math operators", "Addition (+), Subtraction (-), Multiplication (*), Division (/), Modulus (%)"),
              ("Logical operators", "Logical AND (&), Logical OR (|), Unary NOT (!)"),
              ("Comparison operators", "= , > , >= , < , <= , !="),
              ("Regular-expression operators", "Match (:) , Exact match (=~)"),
              ("Conditional operator", "expression1 ? expression2 :: expression3")]
    x = 150
    y = 320
    for hdr, body in groups:
        d.text((x, y), hdr, font=fhdr, fill=ACCENT)
        d.text((x, y+44), body, font=fv, fill=INK)
        y += 112
    save(img, "04-first-pbx-fig08.png")


# =====================================================================
# GROUP B — 10-legacy-channels (07-sip-* files)
# =====================================================================

def fig07():
    """Asterisk connected to a VoIP service provider over Internet/WAN."""
    img, d = canvas()
    title(d, "Asterisk Connected to a VoIP Service Provider")

    # Asterisk server (left), accent
    sx, sy = 360, 430
    server_icon(d, sx, sy, w=130, h=160, accent=True)
    ctext(d, sx, sy-118, "Asterisk", font(SANS_B, 36), fill=INK)

    # local SIP phones below the server
    p1x, p2x, py = 240, 470, 700
    phone_icon(d, p1x, py, 44)
    phone_icon(d, p2x, py, 44)
    dbl_arrow(d, (sx-30, sy+90), (p1x, py-50), INK, 4)
    dbl_arrow(d, (sx+30, sy+90), (p2x, py-50), INK, 4)
    ctext(d, (p1x+p2x)/2, py+50, "Local SIP phones", font(SANS, 28), fill=MUTED)

    # cloud (center)
    ccx, ccy = 850, 430
    cloud_icon(d, ccx, ccy, w=320, h=170,
               lines=["Internet", "or", "Private WAN"])

    # provider box (right)
    pvx, pvy = 1330, 430
    rbox(d, pvx-150, pvy-90, 300, 180, fill=ACCENT_BG, outline=ACCENT, width=3, r=18)
    ctext_lines(d, pvx, pvy, ["VoIP Service", "Provider"], font(SANS_B, 38), fill=INK)

    # links
    d.line([(sx+75, sy), (ccx-150, ccy)], fill=INK, width=4)
    d.line([(ccx+150, ccy), (pvx-150, pvy)], fill=INK, width=4)
    save(img, "07-sip-and-pjsip-fig07.png")


def _two_server_topology(d, title_lines, lbl_left, lbl_right, ext_left, ext_right):
    sAx, sBx, sy = 470, 1130, 420
    server_icon(d, sAx, sy, w=140, h=170)
    server_icon(d, sBx, sy, w=140, h=170)
    ctext(d, sAx, sy-122, lbl_left, font(SANS_B, 34), fill=ACCENT)
    ctext(d, sBx, sy-122, lbl_right, font(SANS_B, 34), fill=ACCENT)

    # SIP signaling link between servers (accent)
    midy = sy
    dbl_arrow(d, (sAx+78, midy), (sBx-78, midy), ACCENT, 6, head=20)
    ctext_lines(d, W/2, midy-44, ["SIP", "(signaling)"], font(SANS_B, 30), fill=ACCENT)

    # phones under each server
    py = 700
    offs = [-130, 130]
    pxA = [sAx+o for o in offs]
    pxB = [sBx+o for o in offs]
    for px in pxA:
        phone_icon(d, px, py, 44)
        dbl_arrow(d, (sAx, sy+95), (px, py-50), INK, 4)
    for px in pxB:
        phone_icon(d, px, py, 44)
        dbl_arrow(d, (sBx, sy+95), (px, py-50), INK, 4)
    fext = font(MONO, 30)
    for px, e in zip(pxA, ext_left):
        ctext(d, px, py+54, e, fext, fill=INK)
    for px, e in zip(pxB, ext_right):
        ctext(d, px, py+54, e, fext, fill=INK)


def fig08b():
    """Two Asterisk servers connected with SIP (07-sip-and-pjsip-fig08)."""
    img, d = canvas()
    title(d, "Connecting Two Asterisk Servers Using SIP")
    _two_server_topology(d, None, "Server A", "Server B",
                         ["4400", "4401"], ["4500", "4501"])
    save(img, "07-sip-and-pjsip-fig08.png")


def fig09():
    """Connecting SIP servers by domain."""
    img, d = canvas()
    title(d, "Connecting to Other SIP Servers by Domain")
    _two_server_topology(d, None, "youdomain.com", "yourpartnerdomain.com",
                         ["lee", "bruce"], ["chuck", "norris"])
    save(img, "07-sip-and-pjsip-fig09.png")


def fig10():
    """Legacy chan_sip authentication decision flow (kept faithful to legacy)."""
    img, d = canvas()
    title(d, "Legacy chan_sip Authentication Flow")

    fp = font(SANS_B, 22)
    fl = font(SANS_B, 22)

    def proc(cx, cy, w, h, lines, fill=BOXBG, outline=INK, txt=INK):
        rbox(d, cx-w/2, cy-h/2, w, h, fill=fill, outline=outline, width=3, r=10)
        ctext_lines(d, cx, cy, lines, fp, fill=txt, lh=26)

    def diamond(cx, cy, w, h, lines):
        d.polygon([(cx, cy-h/2), (cx+w/2, cy), (cx, cy+h/2), (cx-w/2, cy)],
                  fill=(255, 255, 255), outline=INK, width=3)
        ctext_lines(d, cx, cy, lines, fp, fill=INK, lh=24)

    def deny(cx, cy, w=150, h=66):
        proc(cx, cy, w, h, ["DENY"], fill=DENYBG, outline=INK)

    def allow(cx, cy, w, h, lines):
        proc(cx, cy, w, h, lines, fill=ACCENT_BG, outline=ACCENT, txt=INK)

    def lbl(x, y, t):
        ctext(d, x, y, t, fl, fill=MUTED)

    # ---- center spine of three decisions at y=470 ----
    SPINE = 470
    # Start (far left)
    proc(140, SPINE, 190, 130,
         ["Check the From", "header in the SIP", "packet against", "sip.conf"])
    # D1: type=user matches From
    d1 = (430, SPINE)
    diamond(d1[0], d1[1], 230, 180,
            ["type=user", "exists and", "matches From?"])
    conn_arrow(d, (235, SPINE), (d1[0]-115, SPINE), INK, 4)
    # D3: type=peer matches host IP
    d3 = (820, SPINE)
    diamond(d3[0], d3[1], 240, 190,
            ["type=peer exists", "and matches", "the IP in host="])
    conn_arrow(d, (d1[0]+115, SPINE), (d3[0]-120, SPINE), INK, 4)
    lbl(625, 442, "NO")
    # D4: allowguest?
    d4 = (1210, SPINE)
    diamond(d4[0], d4[1], 190, 150, ["allowguest", "= yes?"])
    conn_arrow(d, (d3[0]+120, SPINE), (d4[0]-95, SPINE), INK, 4)
    lbl(1020, 442, "NO")

    # ---- D1 YES -> up to MD5 user check ----
    d2 = (430, 250)
    diamond(d2[0], d2[1], 210, 140, ["MD5", "credentials?"])
    conn_arrow(d, (d1[0], d1[1]-90), (d2[0], d2[1]+70), INK, 4)
    lbl(485, 360, "YES")
    # MD5 OK -> allow user (right)
    allow(760, 250, 210, 110, ["ALLOW — use", "context from", "user section"])
    conn_arrow(d, (d2[0]+105, d2[1]), (760-105, 250), INK, 4)
    lbl(610, 225, "OK")
    # MD5 NOT OK -> deny (to the left, clear of the title)
    deny(160, 250)
    conn_arrow(d, (d2[0]-105, d2[1]), (160+75, 250), INK, 4)
    lbl(290, 222, "NOT OK")

    # ---- D4 allowguest NO -> deny (up); YES -> allow general (down) ----
    deny(1210, 245)
    conn_arrow(d, (d4[0], d4[1]-75), (1210, 245+33), INK, 4)
    lbl(1270, 360, "NO")
    allow(1210, 720, 210, 110, ["ALLOW — use", "context from", "general section"])
    conn_arrow(d, (d4[0], d4[1]+75), (1210, 720-55), INK, 4)
    lbl(1270, 600, "YES")

    # ---- D3 YES (down) -> insecure=invite? ----
    d5 = (820, 700)
    diamond(d5[0], d5[1], 200, 130, ["insecure", "= invite?"])
    conn_arrow(d, (d3[0], d3[1]+95), (d5[0], d5[1]-65), INK, 4)
    lbl(870, 600, "YES")
    # insecure YES -> allow peer (left)
    allow(490, 700, 200, 110, ["ALLOW — use", "context from", "peer section"])
    conn_arrow(d, (d5[0]-100, 700), (490+100, 700), INK, 4)
    lbl(660, 675, "YES")
    # insecure NO -> MD5 credentials (down) -> deny / allow peer
    d6 = (820, 850)
    diamond(d6[0], d6[1], 170, 80, ["MD5", "credentials?"])
    conn_arrow(d, (d5[0], d5[1]+65), (d6[0], d6[1]-40), INK, 4)
    lbl(870, 780, "NO")
    # OK -> allow (right, small), NOT OK -> deny (left, small)
    allow(1130, 850, 180, 78, ["ALLOW — peer", "section"])
    conn_arrow(d, (d6[0]+85, 850), (1130-90, 850), INK, 4)
    lbl(1000, 825, "OK")
    deny(540, 850, w=150, h=70)
    conn_arrow(d, (d6[0]-85, 850), (540+75, 850), INK, 4)
    lbl(665, 825, "NOT OK")
    save(img, "07-sip-and-pjsip-fig10.png")


def fig13():
    """Asterisk behind NAT."""
    img, d = canvas()
    title(d, "Asterisk Behind NAT")

    # internal Asterisk server
    sx, sy = 300, 470
    server_icon(d, sx, sy, w=130, h=160, accent=True)
    ctext(d, sx, sy+115, "Asterisk", font(SANS_B, 34), fill=INK)
    ctext(d, sx, sy+155, "192.168.1.100", font(MONO, 28), fill=MUTED)

    # firewall in the middle
    fwx, fwy = 720, 470
    firewall_icon(d, fwx, fwy, w=140, h=170)
    ctext(d, fwx, fwy+125, "Firewall / NAT", font(SANS_B, 30), fill=INK)

    # link server <-> firewall
    d.line([(sx+70, sy), (fwx-75, fwy)], fill=INK, width=4)

    # public address label
    ctext(d, 1180, 300, "Public: 200.180.4.168", font(MONO_B, 32), fill=INK)

    # SIP arrow into firewall (from outside)
    conn_arrow(d, (1480, 400), (fwx+80, 400), ACCENT, 6, head=20)
    ctext(d, 1170, 372, "SIP (UDP 5060)", font(SANS_B, 28), fill=ACCENT)

    # RTP arrow
    conn_arrow(d, (1480, 560), (fwx+80, 560), ACCENT, 6, head=20)
    ctext_lines(d, 1180, 635, ["RTP (UDP 10000–20000)", "defined in rtp.conf"],
                font(SANS, 26), fill=MUTED)
    save(img, "07-sip-and-pjsip-fig13.png")


if __name__ == "__main__":
    # GROUP A
    fig05(); fig06(); fig08a()
    # GROUP B  (fig08b/fig09 reuse the topology helper)
    fig07(); fig08b(); fig09(); fig10(); fig13()
    print("done")
