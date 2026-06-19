#!/usr/bin/env python3
"""
PATH-1 text/flow figures for chapter 3 (04-first-pbx), rendered with Pillow in the house
style (white bg, near-black ink, single blue accent #1C5D99). 16:9, 1600x900, content current
to Asterisk 22. Outputs to book/illustrate/staging/ for review before swapping into src/images/.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 900
INK = (26, 26, 26)
ACCENT = (28, 93, 153)      # #1C5D99
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

def title(d, text, y=70):
    f = font(SANS_B, 58)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=INK)
    d.line([(W/2 - w/2, y + 78), (W/2 + w/2, y + 78)], fill=ACCENT, width=5)

def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print("  wrote", path)

def block_arrow(d, x, y, w, h, fill):
    # right-pointing block arrow, left edge at x, vertical center y, body height h
    head = h * 0.9
    bx = x + w - head
    d.polygon([(x, y - h/2), (bx, y - h/2), (bx, y - head/2), (x + w, y),
               (bx, y + head/2), (bx, y + h/2), (x, y + h/2)], fill=fill)

def conn_arrow(d, p1, p2, fill, width=5):
    d.line([p1, p2], fill=fill, width=width)
    import math
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0]); s = 18
    d.polygon([p2, (p2[0]-s*math.cos(ang-0.4), p2[1]-s*math.sin(ang-0.4)),
               (p2[0]-s*math.cos(ang+0.4), p2[1]-s*math.sin(ang+0.4))], fill=fill)

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

# ---- fig07: Asterisk special extensions (definition list) ----
def fig07():
    img, d = canvas(); title(d, "Asterisk Special Extensions")
    rows = [("s", "Start — where processing begins"),
            ("i", "Invalid — an invalid extension was dialed"),
            ("h", "Hangup — runs when the call hangs up"),
            ("t", "Timeout — no input within the digit timeout"),
            ("T", "Absolute timeout for the call was reached"),
            ("o", "Operator — caller pressed 0 during voicemail"),
            ("a", "Assistant — caller pressed * during voicemail"),
            ("fax", "Used for fax detection"),
            ("Talk", "Used with BackgroundDetect")]
    fk = font(MONO, 38); fv = font(SANS, 36)
    x_key, x_val, y = 360, 560, 250
    for k, v in rows:
        d.text((x_key, y), k, font=fk, fill=ACCENT)
        d.text((x_val, y), v, font=fv, fill=INK)
        y += 62
    save(img, "04-first-pbx-fig07.png")

# ---- fig09: simple dialplan applications (bullet list) ----
def fig09():
    img, d = canvas(); title(d, "Applications to build a dial plan")
    items = [("Answer", "answer a channel"), ("Dial", "call another channel"),
             ("Hangup", "hang up a channel"), ("Playback", "play back an audio file"),
             ("Goto", "jump to a priority, extension, or context")]
    fb = font(SANS_B, 40); fv = font(SANS, 38)
    x, y = 430, 280
    for name, desc in items:
        d.ellipse([x-34, y+14, x-18, y+30], fill=ACCENT)
        d.text((x, y), name, font=fb, fill=INK)
        nw = d.textlength(name, font=fb)
        d.text((x + nw + 16, y+2), "— " + desc, font=fv, fill=MUTED)
        y += 86
    save(img, "04-first-pbx-fig09.png")

# ---- fig03: Asterisk call flow (incoming -> Asterisk -> outgoing, with notes) ----
def fig03():
    img, d = canvas(); title(d, "Asterisk Call Flow")
    flab = font(SANS_B, 40); fnote = font(SANS, 30)
    cx, cy = W/2, 470
    block_arrow(d, 120, cy, 430, 120, (210, 222, 235))
    d.text((175, cy-22), "Incoming Call Leg", font=flab, fill=INK)
    rbox(d, cx-110, cy-90, 220, 180, fill=ACCENT, outline=ACCENT, r=20)
    fa = font(SANS_B, 44); aw = d.textlength("Asterisk", font=fa)
    d.text((cx-aw/2, cy-26), "Asterisk", font=fa, fill="white")
    block_arrow(d, cx+130, cy, 430, 120, (210, 222, 235))
    d.text((cx+185, cy-22), "Outgoing Call Leg", font=flab, fill=INK)
    # notes
    def note(x, y, w, text):
        ls = wrap(d, text, fnote, w-40); h = 30 + len(ls)*38
        rbox(d, x, y, w, h)
        for i, ln in enumerate(ls):
            d.text((x+20, y+18+i*38), ln, font=fnote, fill=INK)
    note(120, 250, 540, "All calls arrive on a channel (PJSIP, IAX2, DAHDI, and others) as the incoming leg.")
    note(120, 660, 600, "The context is set globally in [general] or per channel in the channel config files (pjsip.conf, chan_dahdi.conf, iax.conf).")
    note(900, 660, 580, "The call is processed in the matching context in extensions.conf, for example [incoming].")
    save(img, "04-first-pbx-fig03.png")

# ---- fig04: call processing (config files -> matching contexts) ----
def fig04():
    img, d = canvas(); title(d, "Call Processing")
    fcap = font(SANS_B, 32); fcode = font(MONO, 26)
    def codebox(x, y, w, h, cap, lines, hi=()):
        d.text((x, y-44), cap, font=fcap, fill=ACCENT)
        rbox(d, x, y, w, h)
        yy = y+22
        for ln in lines:
            col = ACCENT if ln in hi else INK
            d.text((x+22, yy), ln, font=fcode, fill=col); yy += 34
        return (x, y, w, h)
    b1 = codebox(110, 250, 560, 240, "chan_dahdi.conf",
                 ["[channels]", "context=incoming", "signalling=fxs_ks",
                  "group=1", "channel => 1"], hi=["context=incoming"])
    b2 = codebox(110, 600, 560, 180, "pjsip.conf",
                 ["[4001]", "type=endpoint", "context=default",
                  "  ; + auth + aor"], hi=["context=default"])
    rx, ry, rw, rh = 760, 250, 730, 530
    d.text((rx, ry-44), "extensions.conf", font=fcap, fill=ACCENT)
    rbox(d, rx, ry, rw, rh)
    code = ["[globals]", "OPERATOR=PJSIP/4000", "",
            "[incoming]", "exten => s,1,Dial(${OPERATOR},20)", "exten => s,n,Hangup()", "",
            "[default]", "; 4XXX -> local extensions",
            "exten => _4XXX,1,Dial(PJSIP/${EXTEN},20)", "exten => _4XXX,n,Hangup()",
            "; 9 + digits -> the PSTN", "exten => _9.,1,Dial(DAHDI/g1/${EXTEN:1},20)",
            "exten => _9.,n,Hangup()"]
    yy = ry+24
    for ln in code:
        col = ACCENT if ln.startswith("[incoming]") or ln.startswith("[default]") else INK
        d.text((rx+24, yy), ln, font=fcode, fill=col); yy += 35
    conn_arrow(d, (b1[0]+b1[2], 290), (rx, ry+78), ACCENT)
    conn_arrow(d, (b2[0]+b2[2], 660), (rx, ry+300), ACCENT)
    save(img, "04-first-pbx-fig04.png")

if __name__ == "__main__":
    fig07(); fig09(); fig03(); fig04()
    print("done")
