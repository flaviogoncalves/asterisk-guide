#!/usr/bin/env python3
"""
PATH-1 text/flow/diagram figures for chapter 12 (12-dialplan), rendered with Pillow in the
house style (white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900,
content current to Asterisk 22 (comma separators, PJSIP/ dialstrings, DB_DELETE()/DBdeltree(),
no chan_sip/sip.conf/Zap, no removed apps). Outputs to book/illustrate/staging/ for review
before swapping into src/images/. Filenames keep the chapter's referenced names
(10-dialplan-advanced-features-imgNN.png).
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
MUTED = (90, 90, 90)
BOXBG = (245, 247, 250)
CODEBG = (244, 246, 249)
LINE = (170, 178, 190)
OUT = os.path.join(os.path.dirname(__file__), "staging")
os.makedirs(OUT, exist_ok=True)

SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc"]
SANS_B = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
          "/System/Library/Fonts/Helvetica.ttc"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Monaco.ttf"]
MONO_B = ["/System/Library/Fonts/Supplemental/Courier New Bold.ttf", "/System/Library/Fonts/Menlo.ttc"]


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
    d.line([(W/2 - w/2, y + 76), (W/2 + w/2, y + 76)], fill=ACCENT, width=5)


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)


def rbox(d, x, y, w, h, fill=BOXBG, outline=LINE, width=2, r=16):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)


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


import math
def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0]); s = 18
    d.polygon([p2, (p2[0]-s*math.cos(ang-0.4), p2[1]-s*math.sin(ang-0.4)),
               (p2[0]-s*math.cos(ang+0.4), p2[1]-s*math.sin(ang+0.4))], fill=fill)


def app_card(name, synopsis, syntax, opt_title, opts, fname, syntax2=None):
    """Reusable 'application reference' card: title, one-line synopsis, mono syntax line(s),
    then a labelled option list. All current Asterisk 22 (comma separators)."""
    img, d = canvas()
    title(d, name)
    fsyn = font(SANS, 36)
    fmono = font(MONO, 30)
    fopt_h = font(SANS_B, 34)
    fk = font(MONO_B, 30)
    fv = font(SANS, 30)
    y = 210
    for ln in wrap(d, synopsis, fsyn, W - 320):
        d.text((160, y), ln, font=fsyn, fill=INK); y += 46
    y += 16
    # syntax box
    syn_lines = [syntax] + ([syntax2] if syntax2 else [])
    bh = 28 + len(syn_lines) * 40
    rbox(d, 160, y, W - 320, bh, fill=CODEBG, outline=LINE)
    yy = y + 16
    for s in syn_lines:
        d.text((188, yy), s, font=fmono, fill=ACCENT); yy += 40
    y += bh + 40
    if opt_title:
        d.text((160, y), opt_title, font=fopt_h, fill=INK); y += 52
    for k, v in opts:
        d.text((190, y), k, font=fk, fill=ACCENT)
        kw = d.textlength(k, font=fk)
        d.text((190 + max(kw, 70) + 20, y + 2), "— " + v, font=fv, fill=INK)
        y += 48
    save(img, fname)


# ---- img01: Background() application reference ----
def img01():
    app_card(
        "Background()",
        "Play an audio file while waiting for the caller to dial an extension. "
        "Use WaitExten() to keep waiting for digits after playback ends.",
        "Background(filename1[&filename2...][,options[,langoverride[,context]]])",
        "Options",
        [("s", "skip playback if the channel is not answered"),
         ("n", "don't answer the channel before playing the files"),
         ("m", "only break if a digit matches a one-digit extension")],
        "10-dialplan-advanced-features-img01.png")


# ---- img02 + img03: Record() reference (split into two slides in the original) ----
def img02():
    app_card(
        "Record()",
        "Record audio from the channel into a file. If the file exists it is overwritten.",
        "Record(filename.format[,silence[,maxduration[,options]]])",
        "Arguments",
        [("format", "file type to record (wav, gsm, ...)"),
         ("silence", "seconds of silence allowed before returning"),
         ("maxduration", "maximum recording duration in seconds (0 = no limit)")],
        "10-dialplan-advanced-features-img02.png")


def img03():
    img, d = canvas()
    title(d, "Record() — options")
    fk = font(MONO_B, 32); fv = font(SANS, 32)
    opts = [("a", "append to an existing recording instead of replacing it"),
            ("n", "do not answer, but record anyway if line is not yet answered"),
            ("q", "quiet — do not play a beep tone"),
            ("s", "skip recording if the line is not yet answered"),
            ("t", "use alternate '*' terminator key (DTMF) instead of '#'"),
            ("x", "ignore terminator keys (DTMF) and record until hang-up")]
    y = 250
    for k, v in opts:
        d.text((230, y), "'%s'" % k, font=fk, fill=ACCENT)
        d.text((330, y + 2), v, font=fv, fill=INK)
        y += 78
    fn = font(SANS, 28)
    note = ("If filename contains %d it is replaced by an auto-incrementing number. "
            "The caller presses # to stop and continue to the next priority.")
    yy = y + 14
    for ln in wrap(d, note, fn, W - 360):
        d.text((230, yy), ln, font=fn, fill=MUTED); yy += 38
    save(img, "10-dialplan-advanced-features-img03.png")


# ---- img04 + img05: Read() reference ----
def img04():
    app_card(
        "Read()",
        "Read a number of DTMF digits from the caller into a dialplan variable.",
        "Read(variable[,filename[&...]][,maxdigits[,options",
        "Arguments",
        [("variable", "dialplan variable to store the digits"),
         ("filename", "prompt to play before reading (tone with option i)"),
         ("maxdigits", "maximum number of digits (0 = no limit, max 255)")],
        "10-dialplan-advanced-features-img04.png",
        syntax2="          [,attempts[,timeout]]]])")


def img05():
    img, d = canvas()
    title(d, "Read() — options & arguments")
    fk = font(MONO_B, 30); fv = font(SANS, 30); fh = font(SANS_B, 32)
    y = 210
    d.text((220, y), "options", font=fh, fill=INK); y += 54
    for k, v in [("s", "return immediately if the line is not up"),
                 ("i", "play filename as an indication tone from indications.conf"),
                 ("n", "read digits even if the line is not up")]:
        d.text((280, y), "'%s'" % k, font=fk, fill=ACCENT)
        d.text((370, y + 2), v, font=fv, fill=INK); y += 52
    y += 24
    rows = [("attempts", "if greater than 1, the number of read attempts to make"),
            ("timeout", "seconds to wait for a digit response (overrides default)")]
    for k, v in rows:
        d.text((220, y), k, font=fk, fill=ACCENT)
        d.text((480, y + 2), v, font=fv, fill=INK); y += 58
    save(img, "10-dialplan-advanced-features-img05.png")


# ---- img06: Context inclusion (pjsip.conf -> extensions.conf) ----
def img06():
    img, d = canvas()
    title(d, "Context inclusion")
    fcap = font(SANS_B, 34); fmono = font(MONO, 24)
    # left: pjsip.conf endpoints with contexts
    lx, ly, lw, lh = 110, 220, 430, 600
    d.text((lx + 90, ly - 50), "pjsip.conf", font=fcap, fill=ACCENT)
    rbox(d, lx, ly, lw, lh, fill=BOXBG, outline=LINE)
    eps = [("[4000]", "context=internal", 70),
           ("[4001]", "context=local", 200),
           ("[4002]", "context=ld", 330),
           ("[4003]", "context=ldi", 460)]
    anchor = []
    for tag, ctx, off in eps:
        yy = ly + 20 + off
        d.text((lx + 28, yy), tag, font=fmono, fill=INK)
        d.text((lx + 28, yy + 30), "type=endpoint", font=fmono, fill=MUTED)
        d.text((lx + 28, yy + 58), ctx, font=fmono, fill=ACCENT)
        anchor.append(yy + 44)
    # right: extensions.conf contexts
    rx, ry, rw, rh = 700, 220, 790, 600
    d.text((rx + 230, ry - 50), "extensions.conf", font=fcap, fill=ACCENT)
    rbox(d, rx, ry, rw, rh, fill=CODEBG, outline=LINE)
    blocks = [
        (["[internal]",
          "exten => _4XXX,1,Dial(PJSIP/${EXTEN},20)"], 30),
        (["[local]",
          "exten => _9NXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1})",
          "include => internal"], 165),
        (["[ld]",
          "exten => _91NXXNXXXXXX,1,Dial(DAHDI/g1/${EXTEN:1})",
          "include => local"], 320),
        (["[ldi]",
          "exten => _9011.,1,Dial(DAHDI/g1/${EXTEN:1})",
          "include => ld"], 460),
    ]
    targets = []
    for lines, off in blocks:
        yy = ry + 22 + off
        targets.append(yy + 8)
        for i, ln in enumerate(lines):
            col = ACCENT if ln.startswith("[") else INK
            d.text((rx + 24, yy + i * 30), ln, font=fmono, fill=col)
    for ay, ty in zip(anchor, targets):
        conn_arrow(d, (lx + lw, ay), (rx, ty), ACCENT, width=3)
    save(img, "10-dialplan-advanced-features-img06.png")


# ---- img07: AstDB family/key tree + functions/apps/CLI (current) ----
def img07():
    img, d = canvas()
    title(d, "AstDB (SQLite3)")
    fmono = font(MONO, 30); flab = font(SANS_B, 32)
    # family/key tree
    ty = 220
    d.text((180, ty + 40), "Family", font=fmono, fill=INK)
    fx = 340
    d.line([(340, ty + 56), (440, ty + 56)], fill=INK, width=3)        # stem
    d.line([(440, ty + 4), (440, ty + 108)], fill=INK, width=3)        # vertical
    d.line([(440, ty + 4), (520, ty + 4)], fill=INK, width=3)
    d.line([(440, ty + 108), (520, ty + 108)], fill=INK, width=3)
    d.text((540, ty - 14), "KEY1 = VALUE", font=fmono, fill=ACCENT)
    d.text((540, ty + 90), "KEY2 = VALUE", font=fmono, fill=ACCENT)
    d.text((900, ty + 36),
           "/var/lib/asterisk/astdb.sqlite3", font=font(MONO, 24), fill=MUTED)
    # two columns: functions / applications
    cy = 410
    d.text((180, cy), "Functions", font=flab, fill=INK)
    for i, ln in enumerate(["${DB(family/key)}",
                            "DB(family/key)=value",
                            "DB_EXISTS(family/key)",
                            "DB_DELETE(family/key)"]):
        d.text((180, cy + 56 + i * 46), ln, font=fmono, fill=INK)
    d.text((900, cy), "Applications", font=flab, fill=INK)
    for i, ln in enumerate(["DBdeltree(family)"]):
        d.text((900, cy + 56 + i * 46), ln, font=fmono, fill=INK)
    fn = font(SANS, 24)
    d.text((900, cy + 120),
           "DBdel() was removed — use the", font=fn, fill=MUTED)
    d.text((900, cy + 150),
           "DB_DELETE() function instead.", font=fn, fill=MUTED)
    save(img, "10-dialplan-advanced-features-img07.png")


# ---- img08: AstDB CLI commands ----
def img08():
    img, d = canvas()
    title(d, "AstDB — CLI commands")
    fmono = font(MONO, 34)
    cmds = [["database get <family> <key>", "database put <family> <key> <value>"],
            ["database del <family> <key>", "database deltree <family> [keytree]"],
            ["database show [family [key]]", "database showkey <key>"],
            ["database query \"<sql>\"", ""]]
    y = 260
    for left, right in cmds:
        d.text((200, y), left, font=fmono, fill=INK)
        if right:
            d.text((860, y), right, font=fmono, fill=INK)
        y += 90
    save(img, "10-dialplan-advanced-features-img08.png")


# ---- img09: Call Forward / DND programming (current DB_DELETE) ----
def img09():
    img, d = canvas()
    title(d, "Call Forward & DND — programming")
    fmono = font(MONO, 25)
    code = [
        ("[apps]", "h"),
        ("; call forward immediate", "c"),
        ("exten => _*21*X.,1,Set(DB(CFIM/${CALLERID(num)})=${EXTEN:4})", ""),
        ("exten => _*21*X.,n,Hangup()", ""),
        ("exten => _#21#,1,Set(x=${DB_DELETE(CFIM/${CALLERID(num)})})", ""),
        ("exten => _#21#,n,Hangup()", ""),
        ("", ""),
        ("; do not disturb", "c"),
        ("exten => _*41*,1,Set(DB(DND/${CALLERID(num)})=YES)", ""),
        ("exten => _*41*,n,Hangup()", ""),
        ("exten => _#41#,1,Set(x=${DB_DELETE(DND/${CALLERID(num)})})", ""),
        ("exten => _#41#,n,Hangup()", ""),
    ]
    rbox(d, 130, 220, W - 260, 560, fill=CODEBG, outline=LINE)
    y = 250
    for ln, kind in code:
        col = ACCENT if kind == "h" else (MUTED if kind == "c" else INK)
        d.text((170, y), ln, font=fmono, fill=col)
        y += 41
    save(img, "10-dialplan-advanced-features-img09.png")


# ---- img10: Call Forward on busy programming (current DB_DELETE) ----
def img10():
    img, d = canvas()
    title(d, "Call Forward on Busy — programming")
    fmono = font(MONO, 26)
    code = [
        ("; call forward on busy status", "c"),
        ("exten => _*61*X.,1,Set(DB(CFBS/${CALLERID(num)})=${EXTEN:4})", ""),
        ("exten => _*61*X.,n,Hangup()", ""),
        ("exten => _#61#,1,Set(x=${DB_DELETE(CFBS/${CALLERID(num)})})", ""),
        ("exten => _#61#,n,Hangup()", ""),
        ("", ""),
        ("; inspect the stored entries from the CLI:", "c"),
        ("CLI> database show CFBS", "cli"),
        ("CLI> database show DND", "cli"),
    ]
    rbox(d, 130, 240, W - 260, 480, fill=CODEBG, outline=LINE)
    y = 280
    for ln, kind in code:
        if kind == "c":
            col = MUTED
        elif kind == "cli":
            col = ACCENT
        else:
            col = INK
        d.text((170, y), ln, font=fmono, fill=col)
        y += 46
    save(img, "10-dialplan-advanced-features-img10.png")


# ---- img11: Time-based contexts (comma separators) ----
def img11():
    img, d = canvas()
    title(d, "Time-based contexts")
    fmono = font(MONO, 28)
    code = [
        ("; normal hours behavior", "c"),
        ("[incoming]", "h"),
        ("include => normalhours,08:00-18:00,mon-fri,*,*", ""),
        ("", ""),
        ("; after hours behavior", "c"),
        ("include => afterhours,18:00-23:59,*,*,*", ""),
        ("include => afterhours,00:00-07:59,*,*,*", ""),
        ("include => afterhours,*,sat-sun,*,*", ""),
    ]
    rbox(d, 130, 240, W - 260, 470, fill=CODEBG, outline=LINE)
    y = 290
    for ln, kind in code:
        col = ACCENT if kind == "h" else (MUTED if kind == "c" else INK)
        d.text((170, y), ln, font=fmono, fill=col)
        y += 48
    fn = font(SANS, 26)
    d.text((170, 745),
           "Fields are separated by commas: context,times,weekdays,mdays,months",
           font=fn, fill=MUTED)
    save(img, "10-dialplan-advanced-features-img11.png")


# ---- img12: normalhours / afterhours contexts (PJSIP/) ----
def img12():
    img, d = canvas()
    title(d, "Normal-hours & after-hours contexts")
    fmono = font(MONO, 28)
    code = [
        ("[normalhours]", "h"),
        ("exten => s,1,Goto(mainmenu,s,1)", ""),
        ("", ""),
        ("[afterhours]", "h"),
        ("exten => s,1,Playback(afterhoursmessage)", ""),
        ("exten => s,n,Dial(PJSIP/${SECURITY},20,tT)", ""),
        ("exten => s,n,Voicemail(${OPERATOR},u)", ""),
    ]
    rbox(d, 130, 250, W - 260, 450, fill=CODEBG, outline=LINE)
    y = 300
    for ln, kind in code:
        col = ACCENT if kind == "h" else INK
        d.text((170, y), ln, font=fmono, fill=col)
        y += 52
    save(img, "10-dialplan-advanced-features-img12.png")


# ---- img13: VoiceMailMain() menu tree ----
def img13():
    img, d = canvas()
    f = font(SANS_B, 40)
    d.text((90, 60), "VoiceMailMain() — menu tree", font=f, fill=INK)
    d.line([(90, 118), (760, 118)], fill=ACCENT, width=4)
    fl = font(SANS_B, 26); fi = font(SANS, 24)

    def menu(x, y, w, header, items, hcol=ACCENT):
        n = len(items)
        h = 56 + n * 34
        rbox(d, x, y, w, h, fill=BOXBG, outline=LINE)
        d.text((x + 18, y + 14), header, font=fl, fill=hcol)
        for i, it in enumerate(items):
            d.text((x + 24, y + 54 + i * 34), it, font=fi, fill=INK)
        return (x, y, w, h)

    root = menu(80, 230, 320, "Top level",
                ["0  Mailbox options", "1  Read voicemail messages",
                 "2  Change folders", "*  Help", "#  Exit"])
    m0 = menu(560, 150, 360, "0  Mailbox options",
              ["1  Record unavailable message", "2  Record busy message",
               "3  Record your name", "4  Record temporary message",
               "5  Change your password", "*  Return to main menu"])
    m1 = menu(560, 430, 360, "1  Read messages",
              ["3  Advanced options", "4  Play previous message",
               "5  Repeat current message", "6  Play next message",
               "7  Delete current message", "8  Forward to another mailbox",
               "9  Save message in folder"])
    m2 = menu(560, 760, 360, "2  Folders",
              ["0 inbox   1 old   2 work", "3 family  4 friends  5/6 cust"])
    adv = menu(1180, 470, 320, "3  Advanced",
               ["1  Reply", "2  Call back", "3  Envelope", "4  Outgoing call"])
    # connectors
    for tgt in (m0, m1, m2):
        conn_arrow(d, (root[0] + root[2], root[1] + 40),
                   (tgt[0], tgt[1] + 30), ACCENT, width=3)
    conn_arrow(d, (m1[0] + m1[2], m1[1] + 30), (adv[0], adv[1] + 30), ACCENT, width=3)
    save(img, "10-dialplan-advanced-features-img13.png")


# ---- img16: 'Putting it all together' — scenario + network topology ----
def img16():
    img, d = canvas()
    title(d, "Lab scenario — putting it all together")
    # bulleted requirements list (top)
    fb = font(SANS, 30); fbs = font(SANS, 27)
    items = [("4 analog trunks (FXO)", 0),
             ("16 PJSIP-based extensions", 0),
             ("3 service classes:", 0),
             ("restrict (internal, local, 1-800)", 1),
             ("ld (long distance)", 1),
             ("ldi (international)", 1),
             ("After-hours message", 0),
             ("Auto-attendant (IVR)", 0)]
    x0, y = 880, 200
    for txt, lvl in items:
        fx = x0 + lvl * 50
        d.ellipse([fx, y + 12, fx + 12, y + 24], fill=ACCENT)
        d.text((fx + 26, y), txt, font=(fb if lvl == 0 else fbs), fill=INK)
        y += 48

    # --- flat network topology (left/bottom) ---
    fl = font(SANS_B, 26)
    # PSTN cloud
    cx, cy = 230, 250
    for off in [(-90, 0, 90, 70), (-50, -35, 60, 75), (10, -25, 100, 65),
                (-30, 10, 110, 80)]:
        d.ellipse([cx + off[0], cy + off[1], cx + off[2], cy + off[3]],
                  outline=INK, width=3, fill="white")
    d.text((cx - 30, cy + 8), "PSTN", font=fl, fill=INK)

    # Asterisk PBX box
    px, py = 150, 560
    rbox(d, px, py, 190, 130, fill=ACCENT, outline=ACCENT, r=14)
    fa = font(SANS_B, 28)
    d.text((px + 24, py + 30), "Asterisk", font=fa, fill="white")
    d.text((px + 38, py + 66), "PBX", font=fa, fill="white")
    # trunk line cloud->PBX
    d.line([(cx, cy + 55), (px + 95, py)], fill=INK, width=3)
    d.text((px + 110, 430), "Analog 4x FXO", font=font(SANS, 24), fill=MUTED)

    # LAN bus
    by = 700
    d.line([(px + 95, py + 130), (px + 95, by)], fill=INK, width=3)
    rbox(d, 150, by, 600, 16, fill=(225, 230, 236), outline=LINE, r=8)
    d.text((430, by - 36), "Ethernet LAN", font=font(SANS_B, 24), fill=INK)

    def phone(x, y, label):
        # simple handset glyph
        cxp = x + 28
        d.line([(cxp, by + 16), (cxp, y)], fill=INK, width=2)
        d.rounded_rectangle([x, y, x + 56, y + 40], radius=8, outline=INK, width=3, fill="white")
        d.rectangle([x + 12, y + 10, x + 44, y + 22], outline=INK, width=2)
        lw = d.textlength(label, font=font(SANS, 22))
        d.text((cxp - lw / 2, y + 50), label, font=font(SANS, 22), fill=MUTED)

    phone(220, 770, "ATA")
    phone(400, 770, "IP phone")
    phone(580, 770, "Softphone")

    save(img, "10-dialplan-advanced-features-img16.png")


if __name__ == "__main__":
    img01(); img02(); img03(); img04(); img05()
    img06(); img07(); img08(); img09(); img10()
    img11(); img12(); img13(); img16()
    print("done")
