#!/usr/bin/env python3
"""
PATH-1 text/flow figures for chapter 13 (13-pbx-features), rendered with Pillow in the house
style (white bg, near-black ink, single blue accent #1C5D99). 16:9, 1600x900, content current
to Asterisk 22 (ConfBridge replaces MeetMe; res_parking parkext 700/parkpos 701-720/context
parkedcalls; PJSIP snake_case call_group/pickup_group/moh_suggest; pickupexten *8). Outputs to
book/illustrate/staging/ for review before swapping into src/images/.

fig06 (core show application confbridge) is a REAL CLI capture and is intentionally NOT rendered
here — it is kept untouched.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import math

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


def title(d, text, y=64):
    f = font(SANS_B, 56)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W / 2 - w / 2, y + 74), (W / 2 + w / 2, y + 74)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill, outline=outline, width=width)


def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    s = 20
    d.polygon([p2, (p2[0] - s * math.cos(ang - 0.4), p2[1] - s * math.sin(ang - 0.4)),
               (p2[0] - s * math.cos(ang + 0.4), p2[1] - s * math.sin(ang + 0.4))], fill=fill)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def person(d, cx, cy, s=1.0, fill=ACCENT):
    # simple flat person glyph: head + shoulders
    r = 13 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    bw, bh = 34 * s, 26 * s
    d.rounded_rectangle([cx - bw / 2, cy + r * 0.6, cx + bw / 2, cy + r * 0.6 + bh],
                        radius=10 * s, fill=fill)


# ---- fig01: where the PBX features are usually implemented (three columns) ----
def fig01():
    img, d = canvas()
    title(d, "Where the features are usually implemented")
    fh = font(SANS_B, 34)
    fi = font(SANS, 27)
    cols = [
        ("Asterisk itself", ["Music on hold", "Call parking", "Call pickup",
                             "Call recording", "ConfBridge conference room",
                             "Call transfer (blind and consultative)"]),
        ("Dial plan", ["Call forward on busy", "Call forward immediate",
                       "Call forward on unanswered", "Call filtering (blacklist)",
                       "Do not disturb", "Redial"]),
        ("Phone itself", ["Call on hold", "Blind transfer", "Consultative transfer",
                          "Three-way conference", "Message waiting indicator"]),
    ]
    cw = 480
    gap = 30
    x0 = (W - (cw * 3 + gap * 2)) / 2
    top = 240
    boxh = 540
    for i, (head, items) in enumerate(cols):
        x = x0 + i * (cw + gap)
        fillbg = ACCENTBG if i == 0 else BOXBG
        rbox(d, x, top, cw, boxh, fill=fillbg, outline=LINE, width=2, r=18)
        # header bar
        d.text((x + 30, top + 26), head, font=fh, fill=ACCENT if i == 0 else INK)
        d.line([(x + 30, top + 76), (x + cw - 30, top + 76)], fill=LINE, width=2)
        yy = top + 100
        for it in items:
            d.ellipse([x + 32, yy + 13, x + 46, yy + 27], fill=ACCENT)
            d.text((x + 62, yy), it, font=fi, fill=INK)
            yy += 62
    save(img, "13-pbx-features-fig01.png")


# ---- fig02: [featuremap] section of features.conf ----
def fig02():
    img, d = canvas()
    title(d, "features.conf  —  [featuremap] feature codes")
    fcode = font(MONO, 30)
    fcap = font(SANS, 28)
    rows = [
        ("[featuremap]", "", True),
        (";blindxfer => #1", "Blind transfer (default #)", False),
        (";disconnect => *0", "Disconnect (default *)", False),
        (";automon => *1", "One Touch Record (Monitor)", False),
        (";atxfer => *2", "Attended transfer", False),
        (";parkcall => #72", "Park call (one-step parking)", False),
        (";automixmon => *3", "One Touch Record (MixMonitor)", False),
    ]
    x, y = 250, 250
    bw = 1100
    rbox(d, x - 40, y - 30, bw, 470, fill=BOXBG, outline=LINE, width=2, r=18)
    for code, cap, isheader in rows:
        col = ACCENT if isheader else INK
        d.text((x, y), code, font=fcode, fill=col)
        if cap:
            d.text((x + 470, y + 2), "; " + cap, font=fcap, fill=MUTED)
        y += 62
    save(img, "13-pbx-features-fig02.png")


# ---- fig03: Call transfer steps (blind vs attended) ----
def fig03():
    img, d = canvas()
    title(d, "Call Transfer")
    fh = font(SANS_B, 36)
    fi = font(SANS, 29)
    fk = font(SANS_B, 30)
    cw = 690
    gap = 60
    x0 = (W - (cw * 2 + gap)) / 2
    top = 230
    boxh = 560
    cols = [
        ("Blind transfer", "#  followed by the extension", [
            "Enable with the t / T option in Dial()",
            "Press # during the call",
            "Enter the extension to transfer to",
            "Hang up",
            "If no answer, the call rings back",
        ]),
        ("Attended transfer", "*2  (atxfer)", [
            "Enable atxfer in features.conf",
            "Press *2 to start the transfer",
            "Dial the destination extension",
            "Talk to the destination",
            "Hang up; caller is bridged through",
        ]),
    ]
    for i, (head, code, steps) in enumerate(cols):
        x = x0 + i * (cw + gap)
        rbox(d, x, top, cw, boxh, fill=BOXBG, outline=LINE, width=2, r=18)
        d.text((x + 34, top + 28), head, font=fh, fill=INK)
        # accent code chip
        chipw = d.textlength(code, font=fk) + 36
        rbox(d, x + 34, top + 86, chipw, 50, fill=ACCENT, outline=ACCENT, r=12)
        d.text((x + 52, top + 94), code, font=fk, fill="white")
        yy = top + 170
        for n, s in enumerate(steps, 1):
            d.ellipse([x + 36, yy + 4, x + 72, yy + 40], fill=ACCENT)
            num = str(n)
            nw = d.textlength(num, font=font(SANS_B, 24))
            d.text((x + 54 - nw / 2, yy + 8), num, font=font(SANS_B, 24), fill="white")
            for j, ln in enumerate(wrap(d, s, fi, cw - 130)):
                d.text((x + 92, yy + j * 34), ln, font=fi, fill=INK)
            yy += 76
    save(img, "13-pbx-features-fig03.png")


# ---- fig04: Call parking (lot grid + steps + res_parking.conf) ----
def fig04():
    img, d = canvas()
    title(d, "Call Parking")
    # parking lot grid
    lot_x, lot_y, lot_w, lot_h = 90, 210, 760, 360
    rbox(d, lot_x, lot_y, lot_w, lot_h, fill=BOXBG, outline=LINE, width=2, r=18)
    flot = font(SANS_B, 28)
    d.text((lot_x + 24, lot_y + 18), "Parking lot  (slots 701–720)", font=flot, fill=ACCENT)
    fslot = font(SANS_B, 24)
    cols, rows = 5, 4
    cellw = (lot_w - 60) / cols
    cellh = (lot_h - 110) / rows
    gx, gy = lot_x + 30, lot_y + 70
    n = 701
    for r in range(rows):
        for c in range(cols):
            cx = gx + c * cellw
            cy = gy + r * cellh
            rbox(d, cx + 6, cy + 6, cellw - 16, cellh - 14, fill="white", outline=LINE, width=2, r=10)
            t = str(n)
            tw = d.textlength(t, font=fslot)
            d.text((cx + (cellw - 16) / 2 - tw / 2 + 6, cy + (cellh - 14) / 2 - 14), t, font=fslot, fill=INK)
            n += 1
    # park extension 700 chip
    rbox(d, lot_x + lot_w / 2 - 130, lot_y + lot_h + 26, 260, 70, fill=ACCENT, outline=ACCENT, r=14)
    f700 = font(SANS_B, 40)
    lab = "Dial 700 to park"
    lw = d.textlength(lab, font=font(SANS_B, 28))
    d.text((lot_x + lot_w / 2 - lw / 2, lot_y + lot_h + 44), lab, font=font(SANS_B, 28), fill="white")
    conn_arrow(d, (lot_x + lot_w / 2, lot_y + lot_h + 26), (lot_x + lot_w / 2, lot_y + lot_h + 6), ACCENT)

    # steps on the right
    fs = font(SANS, 29)
    steps = [
        "Transfer the active call to extension 700.",
        "Asterisk parks it in the first free slot "
        "(701–720) and announces that slot number.",
        "Dial the announced slot from any phone to "
        "retrieve the call.",
    ]
    sx, sy = 900, 220
    for i, s in enumerate(steps, 1):
        rbox(d, sx, sy, 44, 44, fill=ACCENT, outline=ACCENT, r=12)
        nw = d.textlength(str(i), font=font(SANS_B, 26))
        d.text((sx + 22 - nw / 2, sy + 6), str(i), font=font(SANS_B, 26), fill="white")
        ls = wrap(d, s, fs, 560)
        for j, ln in enumerate(ls):
            d.text((sx + 64, sy + j * 36), ln, font=fs, fill=INK)
        sy += 36 * len(ls) + 30

    # res_parking.conf code box at the bottom
    cb_x, cb_y, cb_w, cb_h = 90, 660, 1420, 200
    rbox(d, cb_x, cb_y, cb_w, cb_h, fill=BOXBG, outline=LINE, width=2, r=16)
    fc = font(MONO, 26)
    code = [
        ("; res_parking.conf", MUTED),
        ("[default]", ACCENT),
        ("parkext => 700                ; extension dialed to park", INK),
        ("parkpos => 701-720            ; range of parking slots", INK),
        ("context => parkedcalls        ; context for parked calls", INK),
    ]
    yy = cb_y + 18
    for ln, col in code:
        d.text((cb_x + 26, yy), ln, font=fc, fill=col)
        yy += 35
    save(img, "13-pbx-features-fig04.png")


# ---- fig05: Call pickup groups (Sales / P&D / Operator) ----
def fig05():
    img, d = canvas()
    title(d, "Call Pickup  (*8)")
    fg = font(SANS_B, 32)
    fc = font(MONO, 26)
    fn = font(SANS, 27)

    def group(cx, cy, rad, label, lines, n_people, op=False):
        col = ACCENT
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=col, width=4, fill=(248, 250, 252))
        d.text((cx - d.textlength(label, font=fg) / 2, cy - rad - 50), label, font=fg, fill=INK)
        # people
        if n_people == 1:
            person(d, cx, cy - 70, 1.4, fill=ACCENT)
        else:
            for k in range(n_people):
                px = cx - 55 + (k % 2) * 110
                py = cy - 95 + (k // 2) * 70
                person(d, px, py, 1.0, fill=MUTED)
        yy = cy + 5
        for ln in lines:
            tw = d.textlength(ln, font=fc)
            d.text((cx - tw / 2, yy), ln, font=fc, fill=ACCENT)
            yy += 34
        if op:
            ot = "(Operator)"
            d.text((cx - d.textlength(ot, font=fn) / 2, yy + 6), ot, font=fn, fill=MUTED)

    group(370, 320, 175, "Sales", ["call_group=1", "pickup_group=1"], 4)
    group(1230, 320, 175, "P&D", ["call_group=2", "pickup_group=2"], 4)
    group(800, 640, 165, "Operator", ["call_group=3", "pickup_group=1,2,3"], 1, op=True)

    conn_arrow(d, (470, 470), (700, 560), ACCENT)
    conn_arrow(d, (1130, 470), (900, 560), ACCENT)

    fnote = font(SANS, 28)
    d.multiline_text((70, 600), "Members capture calls\nonly inside their\nown group",
                     font=fnote, fill=INK, spacing=8)
    d.multiline_text((1300, 600), "Operator can capture\ncalls from groups\n1, 2 and 3",
                     font=fnote, fill=INK, spacing=8)
    save(img, "13-pbx-features-fig05.png")


# ---- fig07: MeetMe conference types (LEGACY / historical reference) ----
def fig07():
    img, d = canvas()
    title(d, "MeetMe conference types  (legacy)")
    fl = font(SANS_B, 30)
    fc = (150, 150, 150)
    centers = [(370, 340), (800, 340), (1230, 340)]
    labels = ["Single speaker", "Password protected", "Dynamic conference"]
    for (cx, cy), lab in zip(centers, labels):
        d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], outline=INK, width=4, fill=(250, 250, 250))
        d.text((cx - d.textlength(lab, font=fl) / 2, cy + 165), lab, font=fl, fill=INK)
    # single speaker: 1 accent + 3 muted
    person(d, centers[0][0], centers[0][1] - 70, 1.3, fill=ACCENT)
    for px, py in [(-90, 20), (90, 20), (0, 90)]:
        person(d, centers[0][0] + px, centers[0][1] + py, 1.0, fill=fc)
    # password: people with a lock glyph each (small)
    for px, py in [(0, -80), (-90, 30), (90, 30), (0, 95)]:
        person(d, centers[1][0] + px, centers[1][1] + py, 1.0, fill=MUTED)
        d.rectangle([centers[1][0] + px + 18, centers[1][1] + py + 4,
                     centers[1][0] + px + 34, centers[1][1] + py + 18], fill=ACCENT)
    # dynamic: small clustered subgroups
    for sx, sy in [(0, -75), (-80, 35), (80, 35), (0, 90)]:
        ccx, ccy = centers[2][0] + sx, centers[2][1] + sy
        d.ellipse([ccx - 38, ccy - 30, ccx + 38, ccy + 38], outline=MUTED, width=2)
        person(d, ccx - 16, ccy, 0.55, fill=fc)
        person(d, ccx + 16, ccy, 0.55, fill=fc)

    fnote = font(SANS, 28)
    note = ("MeetMe needs a DAHDI timing source (load dahdi_dummy if you have no card). "
            "MeetMe is not built by default in Asterisk 22 — use ConfBridge for new "
            "deployments.")
    ls = wrap(d, note, fnote, 1380)
    yy = 620
    for ln in ls:
        d.text((W / 2 - d.textlength(ln, font=fnote) / 2, yy), ln, font=fnote, fill=MUTED)
        yy += 38
    save(img, "13-pbx-features-fig07.png")


# ---- fig08: MeetMe() application syntax + option flags (legacy) ----
def fig08():
    img, d = canvas()
    title(d, "MeetMe()  application  (legacy)")
    fc = font(MONO, 30)
    rbox(d, 250, 200, 1100, 70, fill=ACCENTBG, outline=LINE, width=2, r=14)
    syn = "MeetMe([confno][,[options][,pin]])"
    d.text((280, 218), syn, font=fc, fill=ACCENT)
    fk = font(MONO, 26)
    fv = font(SANS, 26)
    rows = [
        ("a", "set admin mode"),
        ("c", "announce user count on joining"),
        ("d / D", "dynamically add conference (D prompts for PIN)"),
        ("e / E", "select an empty (E: pinless) conference"),
        ("i / I", "announce join/leave (i: with review)"),
        ("l", "listen-only mode"),
        ("m", "join initially muted"),
        ("M", "music on hold when only one caller"),
        ("q", "quiet mode (no enter/leave sounds)"),
        ("t", "talk-only mode"),
        ("r", "record the conference"),
        ("x", "close conference when last marked user exits"),
        ("1", "no message when the first person enters"),
    ]
    x_key, x_val, y = 290, 470, 300
    for k, v in rows:
        d.text((x_key, y), k, font=fk, fill=ACCENT)
        d.text((x_val, y + 1), v, font=fv, fill=INK)
        y += 44
    save(img, "13-pbx-features-fig08.png")


# ---- fig09: MixMonitor() application ----
def fig09():
    img, d = canvas()
    title(d, "MixMonitor()  —  call recording")
    fc = font(MONO, 30)
    rbox(d, 250, 200, 1100, 70, fill=ACCENTBG, outline=LINE, width=2, r=14)
    syn = "MixMonitor(<file>.<ext>[,<options>[,<command>]])"
    d.text((280, 218), syn, font=fc, fill=ACCENT)
    fd = font(SANS, 29)
    d.text((290, 300),
           "Records the channel audio to <file>; absolute path is used as-is,",
           font=fd, fill=INK)
    d.text((290, 338),
           "otherwise the monitoring directory from asterisk.conf is used.",
           font=fd, fill=INK)
    fk = font(MONO, 26)
    fv = font(SANS, 27)
    rows = [
        ("a", "Append to the file instead of overwriting"),
        ("b", "Only record while the channel is bridged (not conferences)"),
        ("v(<x>)", "Adjust heard volume by factor x (-4 to 4)"),
        ("V(<x>)", "Adjust spoken volume by factor x (-4 to 4)"),
        ("W(<x>)", "Adjust both heard and spoken volumes (-4 to 4)"),
        ("<command>", "Runs when recording ends; ${MIXMONITOR_FILENAME} set"),
    ]
    x_key, x_val, y = 290, 520, 430
    for k, v in rows:
        d.text((x_key, y), k, font=fk, fill=ACCENT)
        d.text((x_val, y + 1), v, font=fv, fill=INK)
        y += 56
    save(img, "13-pbx-features-fig09.png")


# ---- fig10: musiconhold.conf modes ----
def fig10():
    img, d = canvas()
    title(d, "musiconhold.conf  —  MOH modes")
    fc = font(MONO, 28)
    fv = font(SANS, 28)
    rows = [
        ("quietmp3", "decode an MP3 stream (quiet)"),
        ("mp3", "decode an MP3 stream (loud)"),
        ("mp3nb", "MP3, unbuffered"),
        ("quietmp3nb", "MP3, quiet unbuffered"),
        ("custom", "run a custom application"),
        ("files", "play native files from a directory (default, no transcoding)"),
    ]
    x_key, x_val, y = 300, 620, 280
    for k, v in rows:
        hi = (k == "files")
        d.text((x_key, y), "mode=" + k, font=fc, fill=ACCENT if hi else INK)
        d.text((x_val, y + 1), v, font=fv, fill=INK)
        y += 60
    # highlighted default config box
    rbox(d, 300, 690, 1000, 150, fill=ACCENTBG, outline=LINE, width=2, r=16)
    cd = font(MONO, 28)
    code = ["[default]", "mode=files", "directory=/var/lib/asterisk/moh"]
    yy = 710
    for ln in code:
        d.text((330, yy), ln, font=cd, fill=ACCENT if ln == "[default]" else INK)
        yy += 38
    save(img, "13-pbx-features-fig10.png")


if __name__ == "__main__":
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig07()
    fig08()
    fig09()
    fig10()
    print("done (fig06 is a real CLI capture, kept untouched)")
