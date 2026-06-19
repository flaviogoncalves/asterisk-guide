#!/usr/bin/env python3
"""
PATH-1 text/flow figures for chapter 19 (19-security), rendered with Pillow in the house
style (white bg, near-black ink, single blue accent #1C5D99). 16:9, 1600x900, content current
to Asterisk 22. Outputs to book/illustrate/staging/ for review before swapping into src/images/.

Figures produced here:
  fig02 — IRSF three-step flow (buy IPRN -> find vulnerable VoIP device & call -> collect payout)
  fig03 — IPRN provider price-list table (per-country payout rates + test numbers)
  fig04 — TFTP theft: attacker GETs guessable MAC.cfg files, server returns plaintext creds
  fig05 — netstat output: many ports bound by Asterisk (4569 IAX, 2727 MGCP, etc.)
  fig06 — netstat output after disabling unused modules: only UDP 5060 remains
fig01 (botnet) is handled separately by copying the approved style-test image.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
LINE = (170, 178, 190)
TERMBG = (250, 251, 252)
GREEN = (40, 120, 70)
RED = (170, 50, 50)
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


def title(d, text, y=70):
    f = font(SANS_B, 58)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W / 2 - w / 2, y + 78), (W / 2 + w / 2, y + 78)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0]); s = 20
    d.polygon([p2, (p2[0] - s * math.cos(ang - 0.4), p2[1] - s * math.sin(ang - 0.4)),
               (p2[0] - s * math.cos(ang + 0.4), p2[1] - s * math.sin(ang + 0.4))], fill=fill)


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


# simple flat geometric icons ------------------------------------------------
def icon_globe(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=5)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=col, width=4)
    d.line([(cx - r, cy), (cx + r, cy)], fill=col, width=4)
    d.line([(cx - r * 0.87, cy - r * 0.5), (cx + r * 0.87, cy - r * 0.5)], fill=col, width=3)
    d.line([(cx - r * 0.87, cy + r * 0.5), (cx + r * 0.87, cy + r * 0.5)], fill=col, width=3)


def icon_phone(d, x, y, w, h, col):
    # desk IP phone: base + handset + keypad hint
    rbox(d, x, y + h * 0.45, w, h * 0.55, fill="white", outline=col, width=5, r=12)
    rbox(d, x + w * 0.12, y, w * 0.55, h * 0.42, fill="white", outline=col, width=5, r=10)
    for i in range(3):
        for j in range(3):
            cxp = x + w * 0.18 + j * w * 0.20
            cyp = y + h * 0.62 + i * h * 0.12
            d.ellipse([cxp, cyp, cxp + 9, cyp + 9], fill=col)


def icon_money(d, cx, cy, w, h, col):
    rbox(d, cx - w / 2, cy - h / 2, w, h, fill="white", outline=col, width=5, r=10)
    d.ellipse([cx - h * 0.30, cy - h * 0.30, cx + h * 0.30, cy + h * 0.30], outline=col, width=5)
    f = font(SANS_B, int(h * 0.5))
    tw = d.textlength("$", font=f)
    d.text((cx - tw / 2, cy - h * 0.30), "$", font=f, fill=col)


def icon_server(d, x, y, w, h, col, accent=False):
    rbox(d, x, y, w, h, fill="white", outline=col, width=5, r=10)
    rows = 3
    for i in range(rows):
        yy = y + h * (0.18 + i * 0.27)
        d.line([(x + w * 0.14, yy), (x + w * 0.6, yy)], fill=col, width=5)
        led = ACCENT if accent else col
        d.ellipse([x + w * 0.74, yy - 6, x + w * 0.74 + 12, yy + 6], fill=led)


def icon_hacker(d, cx, cy, r, col):
    # simple flat "intruder": head with mask band
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white", outline=col, width=5)
    d.rectangle([cx - r, cy - r * 0.25, cx + r, cy + r * 0.15], fill=col)
    # eyes (white slits in mask)
    d.ellipse([cx - r * 0.5, cy - r * 0.12, cx - r * 0.2, cy + r * 0.06], fill="white")
    d.ellipse([cx + r * 0.2, cy - r * 0.12, cx + r * 0.5, cy + r * 0.06], fill="white")


# --------------------------------------------------------------------------
# fig02 — Internet Revenue Share Fraud, three steps
def fig02():
    img, d = canvas()
    title(d, "Internet Revenue Share Fraud")
    fstep = font(SANS_B, 40)
    fnum = font(SANS_B, 40)
    fdesc = font(SANS, 30)

    steps = [
        ("1", "Buy a premium-rate number (IPRN)",
         "Allocate a high-cost international number; the IPRN provider pays you a share of the per-minute revenue."),
        ("2", "Find a vulnerable VoIP device and call it",
         "Brute-force or scan an exposed PBX (e.g. with svcrack), then place hundreds of calls to the IPRN number."),
        ("3", "Collect the payout",
         "The victim is billed for the traffic; the attacker pockets the revenue share — often tens of thousands of dollars in a weekend."),
    ]

    x_badge = 200
    x_text = 360
    y = 250
    row_h = 200
    icon_x = 1240
    for i, (n, head, body) in enumerate(steps):
        cy = y + 60
        # numbered badge
        d.ellipse([x_badge - 46, cy - 46, x_badge + 46, cy + 46], fill=ACCENT)
        nw = d.textlength(n, font=fnum)
        d.text((x_badge - nw / 2, cy - 30), n, font=fnum, fill="white")
        # heading + body
        d.text((x_text, cy - 56), head, font=fstep, fill=INK)
        for j, ln in enumerate(wrap(d, body, fdesc, 760)):
            d.text((x_text, cy - 2 + j * 36), ln, font=fdesc, fill=MUTED)
        # right-side icon
        if i == 0:
            icon_globe(d, icon_x + 60, cy, 60, ACCENT)
        elif i == 1:
            icon_phone(d, icon_x, cy - 56, 120, 112, ACCENT)
        else:
            icon_money(d, icon_x + 60, cy, 150, 100, ACCENT)
        # connector to next step
        if i < len(steps) - 1:
            conn_arrow(d, (x_badge, cy + 60), (x_badge, cy + row_h - 60), ACCENT, width=5)
        y += row_h
    save(img, "19-security-fig02.png")


# fig03 — IPRN provider price list (clean table)
def fig03():
    img, d = canvas()
    title(d, "IPRN Provider Price List")
    fh = font(SANS_B, 30)
    fc = font(SANS, 30)
    fcm = font(MONO, 28)

    cols = [("ID", 230), ("Country", 360), ("Range", 200), ("Payout", 180),
            ("Currency", 200), ("Test number", 360)]
    x0 = 80
    top = 250
    rh = 78
    # column x positions
    xs = []
    cx = x0
    for name, w in cols:
        xs.append((cx, w))
        cx += w
    table_w = cx - x0

    rows = [
        ("5000252", "Albania", "355", "0.09", "EUR", "355 511 810 62"),
        ("5000246", "Antarctica", "88234", "0.20", "EUR", "88 234 607 76"),
        ("5000318", "Latvia", "371", "0.14", "EUR", "371 661 042 18"),
        ("5000477", "Somalia", "252", "0.31", "EUR", "252 905 117 03"),
    ]

    # header band
    rbox(d, x0, top, table_w, rh, fill=ACCENT, outline=ACCENT, r=12)
    for (name, w), (cxp, cw) in zip(cols, xs):
        d.text((cxp + 18, top + rh / 2 - 18), name, font=fh, fill="white")

    y = top + rh
    for ri, row in enumerate(rows):
        bg = (255, 255, 255) if ri % 2 == 0 else (240, 244, 248)
        d.rectangle([x0, y, x0 + table_w, y + rh], fill=bg)
        for (cxp, cw), val, (cn, _) in zip(xs, row, cols):
            fnt = fcm if cn in ("ID", "Test number", "Range", "Payout") else fc
            d.text((cxp + 18, y + rh / 2 - 17), val, font=fnt, fill=INK)
        y += rh
    # outer frame + column separators
    d.rectangle([x0, top, x0 + table_w, y], outline=LINE, width=2)
    for (cxp, cw) in xs[1:]:
        d.line([(cxp, top), (cxp, y)], fill=LINE, width=1)
    d.line([(x0, top + rh), (x0 + table_w, top + rh)], fill=LINE, width=2)

    cap = font(SANS, 27)
    note = ("Payout = your share per minute. Free-to-allocate numbers on expensive "
            "destinations (satellite, remote ranges) make abuse lucrative.")
    for j, ln in enumerate(wrap(d, note, cap, table_w)):
        d.text((x0, y + 30 + j * 36), ln, font=cap, fill=MUTED)
    save(img, "19-security-fig03.png")


# fig04 — TFTP theft flow
def fig04():
    img, d = canvas()
    title(d, "TFTP Configuration Theft")
    fmono = font(MONO, 32)
    flab = font(SANS_B, 32)
    fsub = font(SANS, 27)

    # attacker (left), TFTP server (right)
    icon_hacker(d, 230, 430, 90, INK)
    d.text((150, 545), "Attacker", font=flab, fill=INK)

    icon_server(d, 1180, 320, 220, 220, INK, accent=True)
    d.text((1190, 560), "TFTP server", font=flab, fill=INK)

    # request arrows: guessable MAC.cfg GETs
    gets = ["GET 001A2B3C4D5E.cfg", "GET 001A2B3C4D5F.cfg", "GET 001A2B3C4D60.cfg"]
    ry = 300
    for g in gets:
        d.text((420, ry - 36), g, font=fmono, fill=ACCENT)
        conn_arrow(d, (330, ry), (1170, ry), ACCENT, width=4)
        ry += 70

    # response arrow: plaintext config back
    conn_arrow(d, (1170, 640), (330, 640), INK, width=4)
    resp = ("Plaintext .cfg returned — SIP username and secret "
            "in clear text (XML or not)")
    for j, ln in enumerate(wrap(d, resp, fsub, 800)):
        d.text((420, 660 + j * 34), ln, font=fsub, fill=MUTED)

    note = ("Filenames are just the phone's MAC address + .cfg, so they are trivially "
            "guessable and enumerable. Fix: serve provisioning over HTTPS with a username "
            "and password.")
    fnote = font(SANS, 28)
    ny = 800
    for j, ln in enumerate(wrap(d, note, fnote, 1440)):
        d.text((80, ny + j * 0), ln, font=fnote, fill=INK) if False else None
    # draw note centered at bottom
    lines = wrap(d, note, fnote, 1440)
    by = H - 30 - len(lines) * 34
    for j, ln in enumerate(lines):
        lw = d.textlength(ln, font=fnote)
        d.text(((W - lw) / 2, by + j * 34), ln, font=fnote, fill=INK)
    save(img, "19-security-fig04.png")


# Shared terminal renderer for fig05 / fig06
def terminal(name, title_text, prompt, cmd, header, rows, caption):
    img, d = canvas()
    title(d, title_text)
    fcap = font(SANS, 28)

    # terminal window
    tx, ty, tw, th = 100, 240, 1400, 480
    rbox(d, tx, ty, tw, th, fill=(35, 39, 46), outline=(35, 39, 46), r=18)
    # title bar dots
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([tx + 28 + i * 34, ty + 22, tx + 28 + i * 34 + 18, ty + 40], fill=c)

    fm = font(MONO, 26)
    fmb = font(MONO_B, 26)
    pad_x = tx + 34
    yy = ty + 70
    lh = 36

    GREENT = (115, 215, 130)
    REDT = (235, 120, 120)
    GREY = (200, 205, 212)
    WHITE = (235, 238, 242)

    # prompt + command line
    d.text((pad_x, yy), prompt, font=fmb, fill=GREENT)
    pw = d.textlength(prompt, font=fmb)
    d.text((pad_x + pw, yy), cmd, font=fm, fill=WHITE)
    yy += lh + 6

    # header line (column titles)
    if header:
        d.text((pad_x, yy), header, font=fm, fill=GREY)
        yy += lh

    # data rows; rows is list of (text, highlight_token)
    for text, hl in rows:
        if hl:
            # split so the trailing 'asterisk' (or highlight) is colored red
            idx = text.rfind(hl)
            base = text[:idx]
            d.text((pad_x, yy), base, font=fm, fill=WHITE)
            bw = d.textlength(base, font=fm)
            d.text((pad_x + bw, yy), hl, font=fm, fill=REDT)
        else:
            d.text((pad_x, yy), text, font=fm, fill=WHITE)
        yy += lh

    # trailing prompt
    yy += 4
    d.text((pad_x, yy), prompt, font=fmb, fill=GREENT)

    lines = wrap(d, caption, fcap, tw)
    cy = ty + th + 34
    for j, ln in enumerate(lines):
        lw = d.textlength(ln, font=fcap)
        d.text(((W - lw) / 2, cy + j * 36), ln, font=fcap, fill=MUTED)
    save(img, name)


def fig05():
    prompt = "root@asterisk:~# "
    header = "Proto Local Address          Foreign Address   State    Program"
    rows = [
        ("tcp   0.0.0.0:2000           0.0.0.0:*         LISTEN   959/asterisk", "asterisk"),
        ("udp   0.0.0.0:45883          0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp   0.0.0.0:5000           0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp   0.0.0.0:5060           0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp   0.0.0.0:5080           0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp   0.0.0.0:4569           0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp   0.0.0.0:2727           0.0.0.0:*                  959/asterisk", "asterisk"),
        ("udp6  :::59502               :::*                       959/asterisk", "asterisk"),
    ]
    terminal("19-security-fig05.png",
             "Ports Bound by Asterisk",
             prompt, "netstat -pantu | grep asterisk",
             header, rows,
             "Many ports are open before hardening — e.g. 4569 (IAX2, chan_iax2) "
             "and 2727 (MGCP). Disable the modules you do not use in modules.conf.")


def fig06():
    prompt = "root@asterisk:~# "
    header = "Proto Local Address          Foreign Address   State    Program"
    rows = [
        ("udp   0.0.0.0:5060           0.0.0.0:*                  1042/asterisk", "asterisk"),
    ]
    terminal("19-security-fig06.png",
             "After Disabling Unused Modules",
             prompt, "netstat -pantu | grep asterisk",
             header, rows,
             "After noload-ing the unused channels, only UDP 5060 — the PJSIP "
             "transport — remains bound by Asterisk.")


if __name__ == "__main__":
    fig02(); fig03(); fig04(); fig05(); fig06()
    print("done")
