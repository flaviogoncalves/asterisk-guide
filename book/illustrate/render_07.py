#!/usr/bin/env python3
"""
PATH-1 / PATH-2 figures for chapter 7 (07-sip-and-pjsip), rendered with Pillow in the house
style (white bg, near-black ink, single blue accent #1C5D99). 16:9, 1600x900, content current
to Asterisk 22. These replace dated clip-art flow/topology diagrams; the real CLI captures
(fig15-fig22) are KEPT untouched. Outputs to book/illustrate/staging/ for review before
swapping into src/images/.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
ACCENTBG = (224, 233, 242)
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
    d.line([(W/2 - w/2, y + 72), (W/2 + w/2, y + 72)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)


def center_text(d, cx, cy, lines, f, fill=INK, lh=None):
    if isinstance(lines, str):
        lines = [lines]
    lh = lh or (f.size + 8)
    total = lh * len(lines)
    yy = cy - total/2
    for ln in lines:
        wln = d.textlength(ln, font=f)
        d.text((cx - wln/2, yy), ln, font=f, fill=fill)
        yy += lh


def arrow(d, p1, p2, fill=INK, width=4, head=16, dashed=False):
    if dashed:
        # draw dashed segment
        x1, y1 = p1; x2, y2 = p2
        dist = math.hypot(x2-x1, y2-y1)
        steps = max(1, int(dist // 22))
        for i in range(steps):
            t0 = i/steps; t1 = (i+0.55)/steps
            d.line([(x1+(x2-x1)*t0, y1+(y2-y1)*t0),
                    (x1+(x2-x1)*t1, y1+(y2-y1)*t1)], fill=fill, width=width)
    else:
        d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    d.polygon([p2, (p2[0]-head*math.cos(ang-0.42), p2[1]-head*math.sin(ang-0.42)),
               (p2[0]-head*math.cos(ang+0.42), p2[1]-head*math.sin(ang+0.42))], fill=fill)


def biarrow(d, p1, p2, fill=INK, width=4, head=16):
    d.line([p1, p2], fill=fill, width=width)
    for a, b in ((p1, p2), (p2, p1)):
        ang = math.atan2(b[1]-a[1], b[0]-a[0])
        d.polygon([b, (b[0]-head*math.cos(ang-0.42), b[1]-head*math.sin(ang-0.42)),
                   (b[0]-head*math.cos(ang+0.42), b[1]-head*math.sin(ang+0.42))], fill=fill)


def label(d, x, y, text, f, fill=INK, anchor="lt", bg=None):
    if anchor == "mt":
        w = d.textlength(text, font=f); x -= w/2
    if bg:
        w = d.textlength(text, font=f)
        pad = 6
        d.rectangle([x-pad, y-2, x+w+pad, y+f.size+4], fill=bg)
    d.text((x, y), text, font=f, fill=fill)


# ---------- simple geometric icons ----------
def icon_phone(d, cx, cy, s=46, fill=INK):
    # rounded handset silhouette
    r = s*0.18
    d.rounded_rectangle([cx-s, cy-s*0.7, cx+s, cy+s*0.7], radius=r, outline=fill, width=4)
    d.rounded_rectangle([cx-s*0.6, cy-s*0.4, cx+s*0.6, cy+s*0.4], radius=r*0.6, outline=fill, width=3)


def icon_server(d, cx, cy, s=58, fill=INK, accent=False):
    col = ACCENT if accent else INK
    bg = ACCENTBG if accent else BOXBG
    w, h = s*1.2, s*1.6
    rbox(d, cx-w/2, cy-h/2, w, h, fill=bg, outline=col, width=4, r=10)
    for i in range(3):
        yy = cy-h/2 + 18 + i*(h-30)/3
        d.line([(cx-w/2+14, yy), (cx+w/2-32, yy)], fill=col, width=3)
        d.ellipse([cx+w/2-26, yy-4, cx+w/2-18, yy+4], fill=col)


def icon_db(d, cx, cy, s=52, fill=INK):
    w, h = s*1.5, s*1.7
    ell = h*0.28
    d.ellipse([cx-w/2, cy-h/2, cx+w/2, cy-h/2+ell], outline=fill, width=4)
    d.line([(cx-w/2, cy-h/2+ell/2), (cx-w/2, cy+h/2-ell/2)], fill=fill, width=4)
    d.line([(cx+w/2, cy-h/2+ell/2), (cx+w/2, cy+h/2-ell/2)], fill=fill, width=4)
    d.arc([cx-w/2, cy+h/2-ell, cx+w/2, cy+h/2], 0, 180, fill=fill, width=4)
    d.arc([cx-w/2, cy-h/2+ell/2, cx+w/2, cy-h/2+ell*1.5], 0, 180, fill=fill, width=3)


def icon_cloud(d, cx, cy, s=64, fill=INK):
    # Clean cloud via a single supersampled mask (union of circles), one outline.
    scale = 4
    pad = int(s*1.6)
    msz = pad*2
    mask = Image.new("L", (msz, msz), 0)
    md = ImageDraw.Draw(mask)
    mcx = mcy = pad
    bumps = [(-s*0.55, 0, s*0.5), (-s*0.1, -s*0.45, s*0.55),
             (s*0.4, -s*0.25, s*0.5), (s*0.6, s*0.05, s*0.45),
             (0, s*0.15, s*0.6)]
    for dx, dy, br in bumps:
        md.ellipse([mcx+dx-br, mcy+dy-br, mcx+dx+br, mcy+dy+br], fill=255)
    # outline = dilated edge: draw filled black on canvas then white interior
    from PIL import ImageFilter
    edge = mask.filter(ImageFilter.MaxFilter(7))
    # paste black where edge, white where mask
    bbox = (int(cx-pad), int(cy-pad))
    blackimg = Image.new("RGB", (msz, msz), fill)
    whiteimg = Image.new("RGB", (msz, msz), (255, 255, 255))
    d._image.paste(blackimg, bbox, edge)
    d._image.paste(whiteimg, bbox, mask)


# =========================================================================
# fig01 — SIP main components (architecture overview)
# =========================================================================
def fig01():
    img, d = canvas()
    title(d, "SIP Main Components")
    fsm = font(SANS, 28); fb = font(SANS_B, 30)

    # PSTN cloud (left), Gateway, Server (top-right), three UAs (bottom-right)
    cloud = (200, 470); gw = (430, 470)
    srv = (1080, 240)
    uac = (820, 640); uas = (1080, 640); ua = (1340, 640)

    icon_cloud(d, *cloud, s=84)
    center_text(d, cloud[0], cloud[1]+110, ["PSTN", "or PBX"], fsm)

    # gateway box
    rbox(d, gw[0]-95, gw[1]-55, 190, 110, fill=BOXBG, outline=INK, width=3, r=12)
    center_text(d, gw[0], gw[1], "Gateway", fb)

    # registrar/proxy/redirect server box
    rbox(d, srv[0]-200, srv[1]-80, 400, 160, fill=ACCENTBG, outline=ACCENT, width=3, r=14)
    center_text(d, srv[0], srv[1], ["Registrar / Proxy /", "Redirect Server"], fb, fill=ACCENT)

    # three UA boxes
    for c, lines in ((uac, ["UAC", "User Agent Client"]),
                     (uas, ["UAS", "User Agent Server"]),
                     (ua, ["UA", "User Agent"])):
        rbox(d, c[0]-115, c[1]-60, 230, 120, fill=BOXBG, outline=INK, width=3, r=12)
        center_text(d, c[0], c[1]-12, lines[0], fb)
        center_text(d, c[0], c[1]+24, lines[1], font(SANS, 24), fill=MUTED)

    # PSTN <-> gateway
    biarrow(d, (cloud[0]+86, gw[1]), (gw[0]-98, gw[1]), INK, width=5)
    # gateway <-> server (signaling)
    biarrow(d, (gw[0]+95, gw[1]-30), (srv[0]-205, srv[1]+60), ACCENT, width=4)
    # server <-> each UA (signaling, accent)
    for c in (uac, uas, ua):
        biarrow(d, (srv[0]+(c[0]-srv[0])*0.18, srv[1]+82),
                (c[0]-(c[0]-srv[0])*0.05, c[1]-62), ACCENT, width=4)
    # gateway <-> each UA exists too via signaling to server; show RTP media bus
    media_y = 790
    d.line([(uac[0], uac[1]+62), (uac[0], media_y)], fill=MUTED, width=4)
    d.line([(ua[0], ua[1]+62), (ua[0], media_y)], fill=MUTED, width=4)
    d.line([(gw[0], gw[1]+57), (gw[0], media_y)], fill=MUTED, width=4)
    d.line([(uas[0], uas[1]+62), (uas[0], media_y)], fill=MUTED, width=4)
    d.line([(gw[0], media_y), (ua[0], media_y)], fill=MUTED, width=4)
    label(d, ua[0]+30, media_y-16, "RTP media flow", fsm, fill=MUTED)
    # signaling legend
    label(d, 110, 845, "Signaling (SIP)", font(SANS, 24), fill=ACCENT)
    d.line([(360, 858), (430, 858)], fill=ACCENT, width=4)

    save(img, "07-sip-and-pjsip-fig01.png")


# =========================================================================
# fig02 — SIP REGISTER process
# =========================================================================
def fig02():
    img, d = canvas()
    title(d, "SIP Registration")
    fb = font(SANS_B, 30); fm = font(MONO, 26); fs = font(SANS, 26)

    db = (330, 240)
    reg = (330, 560)
    phone = (1280, 560)

    icon_db(d, *db, s=70)
    center_text(d, db[0]+150, db[1], ["Location", "Database"], fb)

    # registrar box
    icon_server(d, reg[0], reg[1], s=70, accent=True)
    center_text(d, reg[0], reg[1]+115, ["SIP Registrar", "domain: voip.school"], fs, fill=MUTED)

    icon_phone(d, phone[0], phone[1], s=60)
    center_text(d, phone[0], phone[1]+95, "Phone (UAC)", fs, fill=MUTED)

    # store binding: registrar -> db
    arrow(d, (reg[0], reg[1]-95), (db[0], db[1]+115), ACCENT, width=4)
    label(d, db[0]-150, (db[1]+reg[1])/2-50, "store", fm, fill=ACCENT)
    label(d, db[0]-235, (db[1]+reg[1])/2-12, "8500 -> 200.180.1.1", font(MONO, 22), fill=ACCENT)

    # REGISTER message phone -> registrar
    arrow(d, (phone[0]-90, reg[1]-30), (reg[0]+95, reg[1]-30), INK, width=4)
    msg = ["REGISTER sip:voip.school SIP/2.0",
           "From: <sip:8500@voip.school>",
           "To:   <sip:8500@voip.school>",
           "Contact: <sip:8500@200.180.1.1>",
           "Expires: 3600"]
    bx = (reg[0]+phone[0])/2 - 130
    rbox(d, bx, 350, 580, 180, fill=BOXBG, outline=LINE, width=2, r=12)
    yy = 366
    for ln in msg:
        d.text((bx+22, yy), ln, font=fm, fill=INK); yy += 32

    # 200 OK registrar -> phone
    arrow(d, (reg[0]+95, reg[1]+40), (phone[0]-90, reg[1]+40), ACCENT, width=4)
    label(d, (reg[0]+phone[0])/2-90, reg[1]+50, "SIP/2.0 200 OK", fm, fill=ACCENT)

    save(img, "07-sip-and-pjsip-fig02.png")


# =========================================================================
# fig03 — Proxy operation
# =========================================================================
def fig03():
    img, d = canvas()
    title(d, "Proxy Operation")
    fb = font(SANS_B, 28); fs = font(SANS, 24); fnum = font(SANS_B, 30)

    srv = (800, 250)
    a = (210, 560); b = (1390, 560)

    icon_server(d, srv[0], srv[1], s=66, accent=True)
    center_text(d, srv[0], srv[1]+105, ["SIP Proxy", "(Location / Registrar)"], fs, fill=MUTED)

    icon_phone(d, a[0], a[1], s=58); center_text(d, a[0], a[1]+92, "Caller (2400)", fs, fill=MUTED)
    icon_phone(d, b[0], b[1], s=58); center_text(d, b[0], b[1]+92, "Callee (8500)", fs, fill=MUTED)

    # 1 INVITE caller->proxy
    arrow(d, (a[0]+80, a[1]-30), (srv[0]-150, srv[1]+70), ACCENT, width=4)
    label(d, a[0]+120, a[1]-110, "(1) INVITE 8500", fb, fill=ACCENT)
    # 2 lookup in location server (small loop beside the server box)
    label(d, srv[0]+95, srv[1]-55, "(2) lookup", fs, fill=MUTED)
    d.arc([srv[0]+55, srv[1]-50, srv[0]+135, srv[1]+30], 270, 130, fill=MUTED, width=3)
    arrow(d, (srv[0]+58, srv[1]+18), (srv[0]+50, srv[1]+5), MUTED, width=3, head=10)
    # 3 INVITE proxy->callee
    arrow(d, (srv[0]+150, srv[1]+70), (b[0]-80, b[1]-30), ACCENT, width=4)
    label(d, srv[0]+250, a[1]-110, "(3) INVITE 8500", fb, fill=ACCENT)
    # 4 200 OK callee->proxy->caller (return)
    arrow(d, (b[0]-80, b[1]+10), (srv[0]+160, srv[1]+120), INK, width=3)
    arrow(d, (srv[0]-160, srv[1]+120), (a[0]+80, b[1]+10), INK, width=3)
    label(d, srv[0]+200, srv[1]+150, "(4) 200 OK", fs)
    label(d, srv[0]-340, srv[1]+150, "(5) 200 OK", fs)

    # media direct
    arrow(d, (a[0]+80, 800), (b[0]-80, 800), MUTED, width=5)
    arrow(d, (b[0]-80, 805), (a[0]+80, 805), MUTED, width=5)
    label(d, srv[0]-150, 760, "RTP media flows directly", font(SANS, 26), fill=MUTED)

    label(d, 110, 845, "Signaling (SIP)", fs, fill=ACCENT)
    d.line([(330, 858), (400, 858)], fill=ACCENT, width=4)
    save(img, "07-sip-and-pjsip-fig03.png")


# =========================================================================
# fig04 — Redirect operation
# =========================================================================
def fig04():
    img, d = canvas()
    title(d, "Redirect Operation")
    fb = font(SANS_B, 28); fs = font(SANS, 24)

    srv = (800, 250)
    a = (210, 560); b = (1390, 560)

    icon_server(d, srv[0], srv[1], s=66, accent=True)
    center_text(d, srv[0], srv[1]+105, "Redirect Server", fs, fill=MUTED)

    icon_phone(d, a[0], a[1], s=58); center_text(d, a[0], a[1]+92, "Caller (2400)", fs, fill=MUTED)
    icon_phone(d, b[0], b[1], s=58); center_text(d, b[0], b[1]+92, "Callee (8500)", fs, fill=MUTED)

    # 1 INVITE caller -> redirect
    arrow(d, (a[0]+80, a[1]-30), (srv[0]-150, srv[1]+70), ACCENT, width=4)
    label(d, a[0]+90, a[1]-120, "(1) INVITE 8500", fb, fill=ACCENT)
    # 2 302 redirect -> caller
    arrow(d, (srv[0]-150, srv[1]+100), (a[0]+80, a[1]+10), INK, width=3)
    label(d, a[0]+70, a[1]+95, "(2) 302 Moved Temporarily", fs)
    label(d, a[0]+70, a[1]+125, "    Contact: sip:8500@200.180.4.168", font(MONO, 20), fill=MUTED)

    # 3/4/5 direct exchange caller<->callee (proxy steps aside)
    y3 = 720
    arrow(d, (a[0]+90, y3), (b[0]-90, y3), ACCENT, width=4)
    label(d, srv[0]-100, y3-32, "(3) INVITE sip:8500@200.180.4.168", fs, fill=ACCENT)
    arrow(d, (b[0]-90, y3+50), (a[0]+90, y3+50), INK, width=3)
    label(d, srv[0]-30, y3+22, "(4) 200 OK", fs)
    arrow(d, (a[0]+90, y3+100), (b[0]-90, y3+100), INK, width=3)
    label(d, srv[0]-80, y3+72, "(5) ACK -> call established", fs)

    save(img, "07-sip-and-pjsip-fig04.png")


# =========================================================================
# fig05 — direct_media=yes
# =========================================================================
def _directmedia(img, d, anchored):
    fs = font(SANS, 26); fb = font(SANS_B, 28)
    srv = (800, 270)
    a = (250, 620); b = (1350, 620)
    icon_server(d, srv[0], srv[1], s=66, accent=True)
    center_text(d, srv[0], srv[1]+108, "Asterisk", fb, fill=ACCENT)
    icon_phone(d, a[0], a[1], s=58); center_text(d, a[0], a[1]+92, "Phone A", fs, fill=MUTED)
    icon_phone(d, b[0], b[1], s=58); center_text(d, b[0], b[1]+92, "Phone B", fs, fill=MUTED)

    # SIP signaling (always through Asterisk)
    biarrow(d, (a[0]+70, a[1]-40), (srv[0]-150, srv[1]+70), ACCENT, width=4)
    biarrow(d, (srv[0]+150, srv[1]+70), (b[0]-70, b[1]-40), ACCENT, width=4)
    label(d, 430, 420, "SIP signaling", fs, fill=ACCENT)
    label(d, 1010, 420, "SIP signaling", fs, fill=ACCENT)

    if anchored:
        # RTP through Asterisk too
        biarrow(d, (a[0]+80, a[1]+5), (srv[0]-140, srv[1]+120), MUTED, width=5)
        biarrow(d, (srv[0]+140, srv[1]+120), (b[0]-80, b[1]+5), MUTED, width=5)
        label(d, 360, 540, "RTP (audio)", fs, fill=MUTED)
        label(d, 1080, 540, "RTP (audio)", fs, fill=MUTED)
    else:
        # RTP direct between phones
        biarrow(d, (a[0]+85, a[1]), (b[0]-85, b[1]), MUTED, width=6)
        label(d, srv[0]-95, b[1]-60, "RTP (audio) direct", font(SANS_B, 28), fill=MUTED)


def fig05():
    img, d = canvas()
    title(d, "SIP operation with direct_media=yes")
    _directmedia(img, d, anchored=False)
    save(img, "07-sip-and-pjsip-fig05.png")


def fig06():
    img, d = canvas()
    title(d, "SIP operation with direct_media=no")
    _directmedia(img, d, anchored=True)
    save(img, "07-sip-and-pjsip-fig06.png")


# =========================================================================
# fig11 — Full Cone NAT
# =========================================================================
def fig11():
    img, d = canvas()
    title(d, "Full Cone NAT")
    fs = font(SANS, 26); fm = font(MONO, 24); fb = font(SANS_B, 28)

    host = (230, 460); nat = (640, 460)
    c1 = (1280, 300); c2 = (1280, 640)

    icon_phone(d, host[0], host[1], s=56)
    center_text(d, host[0], host[1]+95, ["Internal host", "10.0.0.1:8000"], fs, fill=MUTED)

    # NAT box
    rbox(d, nat[0]-90, nat[1]-90, 180, 180, fill=ACCENTBG, outline=ACCENT, width=3, r=14)
    center_text(d, nat[0], nat[1]-10, "NAT", fb, fill=ACCENT)
    center_text(d, nat[0], nat[1]+40, ["external", "200.180.4.168:1234"], font(MONO, 20), fill=ACCENT)

    icon_server(d, c1[0], c1[1], s=50)
    center_text(d, c1[0]+130, c1[1], ["Host 1", "200.210.1.1:2000"], fs, fill=MUTED)
    icon_server(d, c2[0], c2[1], s=50)
    center_text(d, c2[0]+130, c2[1], ["Host 2", "200.210.1.2:3000"], fs, fill=MUTED)

    arrow(d, (host[0]+70, host[1]), (nat[0]-95, nat[1]), INK, width=4)
    # any external host can reach the mapping
    arrow(d, (c1[0]-70, c1[1]+20), (nat[0]+95, nat[1]-30), ACCENT, width=4)
    arrow(d, (c2[0]-70, c2[1]-20), (nat[0]+95, nat[1]+30), ACCENT, width=4)

    note = "Any external host may send to 200.180.4.168:1234 → delivered to 10.0.0.1:8000"
    rbox(d, 220, 790, 1160, 70, fill=BOXBG, outline=LINE, width=2, r=12)
    center_text(d, 800, 825, note, fs)
    save(img, "07-sip-and-pjsip-fig11.png")


# =========================================================================
# fig12 — Symmetric NAT
# =========================================================================
def fig12():
    img, d = canvas()
    title(d, "Symmetric NAT")
    fs = font(SANS, 26); fm = font(MONO, 22); fb = font(SANS_B, 28)

    host = (230, 460); nat = (640, 460)
    c1 = (1260, 300); c2 = (1260, 640)

    icon_phone(d, host[0], host[1], s=56)
    center_text(d, host[0], host[1]+95, ["Internal host", "10.0.0.1:8000"], fs, fill=MUTED)

    rbox(d, nat[0]-90, nat[1]-110, 180, 220, fill=ACCENTBG, outline=ACCENT, width=3, r=14)
    center_text(d, nat[0], nat[1]-70, "NAT", fb, fill=ACCENT)
    center_text(d, nat[0], nat[1]-15, ["→ Host 1:", ":1234"], font(MONO, 20), fill=ACCENT)
    center_text(d, nat[0], nat[1]+55, ["→ Host 2:", ":5678"], font(MONO, 20), fill=ACCENT)

    icon_server(d, c1[0], c1[1], s=50)
    center_text(d, c1[0]+130, c1[1], ["Host 1", "200.210.1.1:2000"], fs, fill=MUTED)
    icon_server(d, c2[0], c2[1], s=50)
    center_text(d, c2[0]+130, c2[1], ["Host 2", "200.210.1.2:3000"], fs, fill=MUTED)

    arrow(d, (host[0]+70, host[1]), (nat[0]-95, nat[1]), INK, width=4)
    # different external port per destination (outbound, allowed)
    arrow(d, (nat[0]+95, nat[1]-50), (c1[0]-70, c1[1]+20), INK, width=4)
    arrow(d, (nat[0]+95, nat[1]+50), (c2[0]-70, c2[1]-20), INK, width=4)

    # blocked cross-reuse: host1 cannot use port toward host2 (and vice versa)
    def block(p):
        r = 22
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], outline=(190, 40, 40), width=5)
        d.line([(p[0]-r*0.7, p[1]-r*0.7), (p[0]+r*0.7, p[1]+r*0.7)], fill=(190, 40, 40), width=5)
    block((nat[0]+200, nat[1]-40))
    block((nat[0]+200, nat[1]+40))

    note = "A different external port is allocated per destination, so the mapping toward one host cannot be reused by another — this breaks STUN."
    rbox(d, 180, 790, 1240, 80, fill=BOXBG, outline=LINE, width=2, r=12)
    center_text(d, 800, 830, note, font(SANS, 24))
    save(img, "07-sip-and-pjsip-fig12.png")


# =========================================================================
# fig14 — PJSIP object relationships
# =========================================================================
def fig14():
    img, d = canvas()
    title(d, "PJSIP Configuration Object Relationships")
    fb = font(SANS_B, 30); fs = font(SANS, 22)

    def obj(cx, cy, text, accent=False):
        w, hh = 230, 84
        col = ACCENT if accent else INK
        bg = ACCENTBG if accent else BOXBG
        rbox(d, cx-w/2, cy-hh/2, w, hh, fill=bg, outline=col, width=3, r=14)
        center_text(d, cx, cy, text, fb, fill=col)
        return (cx, cy, w, hh)

    # layout
    endpoint = (800, 410)
    identify = (800, 210)
    transport = (300, 630)
    auth = (640, 630)
    aor = (980, 630)
    contact = (1300, 630)
    registration = (470, 830)
    acl = (1380, 250)
    domain = (1380, 400)

    e = obj(*endpoint, "endpoint", accent=True)
    obj(*identify, "identify")
    obj(*transport, "transport")
    obj(*auth, "auth")
    obj(*aor, "aor")
    # contact (smaller)
    rbox(d, contact[0]-95, contact[1]-38, 190, 76, fill=BOXBG, outline=INK, width=3, r=12)
    center_text(d, *contact[:2], "contact", fb)
    obj(*registration, "registration")
    rbox(d, acl[0]-90, acl[1]-36, 180, 72, fill=BOXBG, outline=LINE, width=2, r=12)
    center_text(d, *acl[:2], "acl", font(SANS_B, 26), fill=MUTED)
    rbox(d, domain[0]-110, domain[1]-36, 220, 72, fill=BOXBG, outline=LINE, width=2, r=12)
    center_text(d, *domain[:2], "domain_alias", font(SANS_B, 24), fill=MUTED)

    def link(p1, p2, card, col=INK):
        d.line([p1, p2], fill=col, width=3)
        mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        label(d, mx+8, my-26, card, fs, fill=MUTED, bg="white")

    # identify -> endpoint
    link((identify[0], identify[1]+42), (endpoint[0], endpoint[1]-42), "points to", ACCENT)
    # endpoint -> transport / auth / aor
    link((endpoint[0]-90, endpoint[1]+42), (transport[0], transport[1]-42), "1", ACCENT)
    link((endpoint[0], endpoint[1]+42), (auth[0], auth[1]-42), "0..*", ACCENT)
    link((endpoint[0]+90, endpoint[1]+42), (aor[0], aor[1]-42), "*..*", ACCENT)
    # aor -> contact
    link((aor[0]+115, aor[1]), (contact[0]-95, contact[1]), "*..*")
    # registration -> transport + auth
    link((registration[0]-40, registration[1]-42), (transport[0], transport[1]+42), "transport")
    link((registration[0]+40, registration[1]-42), (auth[0], auth[1]+42), "auth")

    # standalone note
    label(d, 1150, 470, "acl and domain_alias", fs, fill=MUTED)
    label(d, 1150, 498, "stand alone", fs, fill=MUTED)
    save(img, "07-sip-and-pjsip-fig14.png")


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04(); fig05(); fig06()
    fig11(); fig12(); fig14()
    print("done")
