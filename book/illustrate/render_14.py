#!/usr/bin/env python3
"""
PATH-1 text/code/flow figures for chapter 14 (14-queues), rendered with Pillow in the house
style (white bg, near-black ink #1A1A1A, single blue accent #1C5D99). 16:9, 1600x900, content
current to Asterisk 22 (PJSIP/ not SIP/, rrmemory not roundrobin, `agent show all` / `queue show`
CLI, MixMonitor not Monitor). Outputs to book/illustrate/staging/ for review before swapping
into src/images/. Source template: render_ch3_slides.py.
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


def conn_arrow(d, p1, p2, fill, width=4):
    d.line([p1, p2], fill=fill, width=width)
    ang = math.atan2(p2[1]-p1[1], p2[0]-p1[0]); s = 16
    d.polygon([p2, (p2[0]-s*math.cos(ang-0.4), p2[1]-s*math.sin(ang-0.4)),
               (p2[0]-s*math.cos(ang+0.4), p2[1]-s*math.sin(ang+0.4))], fill=fill)


def block_arrow(d, x, y, w, h, fill):
    head = h * 0.9
    bx = x + w - head
    d.polygon([(x, y - h/2), (bx, y - h/2), (bx, y - head/2), (x + w, y),
               (bx, y + head/2), (bx, y + h/2), (x, y + h/2)], fill=fill)


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


def person(d, cx, cy, s=1.0, fill=ACCENT):
    # simple flat person icon: head + shoulders
    hr = 16 * s
    d.ellipse([cx-hr, cy-hr, cx+hr, cy+hr], fill=fill)
    bw, bh = 44*s, 34*s
    d.rounded_rectangle([cx-bw/2, cy+hr*0.6, cx+bw/2, cy+hr*0.6+bh], radius=12*s, fill=fill)


def phone(d, x, y, s=1.0, fill=INK):
    # simple flat desk-phone glyph in a rounded square
    w, h = 64*s, 64*s
    rbox(d, x, y, w, h, fill="white", outline=fill, width=3, r=10)
    # handset (rounded bar) + base
    d.rounded_rectangle([x+12*s, y+12*s, x+w-12*s, y+22*s], radius=5*s, fill=fill)
    d.line([(x+16*s, y+22*s), (x+16*s, y+36*s)], fill=fill, width=int(4*s))
    d.line([(x+w-16*s, y+22*s), (x+w-16*s, y+36*s)], fill=fill, width=int(4*s))
    d.rounded_rectangle([x+16*s, y+40*s, x+w-16*s, y+h-12*s], radius=4*s, fill=fill)


# ---- fig01: Call queue + ACD strategy -> agents ----
def fig01():
    img, d = canvas()
    title(d, "A Call Queue (ACD)")
    flab = font(SANS_B, 34)
    fsm = font(SANS, 28)
    # incoming 1-800
    block_arrow(d, 70, 300, 200, 70, ACCENT)
    d.text((84, 278), "1-800", font=flab, fill="white")
    # queue box (cylinder-free flat capsule)
    qx, qy, qw, qh = 320, 250, 300, 100
    rbox(d, qx, qy, qw, qh, fill=BOXBG, outline=INK, width=3, r=50)
    tw = d.textlength("Call Queue", font=flab)
    d.text((qx + qw/2 - tw/2, qy + qh/2 - 22), "Call Queue", font=flab, fill=INK)
    # arrow to ACD
    conn_arrow(d, (qx+qw, 300), (760, 360), ACCENT, width=5)
    # ACD strategy box
    ax, ay, aw, ah = 760, 300, 720, 150
    rbox(d, ax, ay, aw, ah, fill=ACCENT, outline=ACCENT, r=20)
    acd = "ACD strategy"
    aw_t = d.textlength(acd, font=flab)
    d.text((ax + aw/2 - aw_t/2, ay + 18), acd, font=flab, fill="white")
    strat = "ringall  rrmemory  leastrecent  fewestcalls"
    s2 = "random  wrandom  rrordered  linear"
    for i, ln in enumerate([strat, s2]):
        lw = d.textlength(ln, font=fsm)
        d.text((ax + aw/2 - lw/2, ay + 66 + i*36), ln, font=fsm, fill="white")
    # agents row
    names = ["Agent 1", "Agent 2", "Agent 3", "Agent 4", "Agent N"]
    n = len(names)
    x0, x1 = 360, 1480
    ay_p = 720
    for i, nm in enumerate(names):
        cx = x0 + (x1 - x0) * i / (n - 1)
        conn_arrow(d, (ax + aw/2, ay + ah), (cx, ay_p - 40), INK, width=3)
        person(d, cx, ay_p, s=1.6)
        nw = d.textlength(nm, font=fsm)
        d.text((cx - nw/2, ay_p + 56), nm, font=fsm, fill=INK)
    save(img, "14-queues-fig01.png")


# ---- fig02: ACD architecture (queues -> agents -> channels) ----
def fig02():
    img, d = canvas()
    title(d, "ACD Architecture")
    fq = font(SANS_B, 30)
    fl = font(SANS, 26)
    fc = font(MONO, 24)
    # two queue capsules on the left, fed by phone numbers
    queues = [("Customer Service", "1-800-555-1212", 250),
              ("Inside Sales", "1-800-555-1211", 560)]
    qx, qw, qh = 230, 320, 96
    qcenters = []
    for label, num, qy in queues:
        block_arrow(d, 70, qy + qh/2, 140, 56, ACCENT)
        nw = d.textlength(num, font=fl)
        d.text((70, qy + qh/2 - 56), num, font=fl, fill=INK)
        rbox(d, qx, qy, qw, qh, fill=BOXBG, outline=INK, width=3, r=48)
        lw = d.textlength(label, font=fq)
        d.text((qx + qw/2 - lw/2, qy + qh/2 - 20), label, font=fq, fill=INK)
        qcenters.append((qx + qw, qy + qh/2))
    # agents in the middle, channels on the right (PJSIP, not SIP)
    agents = [("Agent 300", "PJSIP/2000", 230),
              ("Agent 301", "PJSIP/2001", 430),
              ("Agent 302", "PJSIP/2002", 630)]
    aX = 760
    chX = 1180
    acenters = []
    for nm, ch, ay in agents:
        person(d, aX, ay, s=1.8)
        nw = d.textlength(nm, font=fl)
        d.text((aX - nw/2, ay + 80), nm, font=fl, fill=INK)
        acenters.append((aX, ay))
        # channel box
        cy = ay
        phone(d, chX, cy - 34, s=1.0, fill=INK)
        d.text((chX + 80, cy - 16), ch, font=fc, fill=ACCENT)
        conn_arrow(d, (aX + 50, ay), (chX - 6, cy), INK, width=3)
    # queue -> agents links (customer service feeds 300+301; inside sales feeds 302)
    conn_arrow(d, qcenters[0], (acenters[0][0]-54, acenters[0][1]), ACCENT, width=3)
    conn_arrow(d, qcenters[0], (acenters[1][0]-54, acenters[1][1]), ACCENT, width=3)
    conn_arrow(d, qcenters[1], (acenters[2][0]-54, acenters[2][1]), ACCENT, width=3)
    save(img, "14-queues-fig02.png")


# ---- generic code-listing renderer (for conf files) ----
def code_listing(name, header, lines, hi_prefixes=("[",), fsize=30, lh=40, top=210):
    img, d = canvas()
    title(d, header)
    f = font(MONO, fsize)
    x = 150
    bw = W - 2*x
    bh = top + len(lines)*lh + 30
    if bh > H - 40:
        bh = H - 40
    rbox(d, x, top - 30, bw, bh - (top-30), fill=BOXBG, outline=LINE, width=2, r=14)
    y = top
    for ln in lines:
        col = INK
        ls = ln.lstrip()
        if any(ls.startswith(p) for p in hi_prefixes):
            col = ACCENT
        elif ls.startswith(";"):
            col = MUTED
        d.text((x + 30, y), ln, font=f, fill=col)
        y += lh
    save(img, name)


def fig03():
    # queues.conf working example (typos fixed: customerservice; Asterisk 22 current)
    lines = [
        "[general]",
        "persistentmembers = yes",
        "autofill = yes",
        "monitor-type = MixMonitor",
        "",
        "[customerservice]",
        "musicclass = default",
        "announce = queue-customerservice",
        "strategy = rrmemory",
        "servicelevel = 60",
        "context = customerservice",
        "timeout = 15",
        "retry = 5",
        "wrapuptime = 15",
        "announce-frequency = 90",
        "announce-holdtime = yes",
        "monitor-format = wav",
        "member => Agent/300,300",
        "member => Agent/301,301",
    ]
    code_listing("14-queues-fig03.png", "queues.conf", lines,
                 hi_prefixes=("[",), fsize=28, lh=34, top=180)


def fig06():
    # agents.conf working example (matches chapter text)
    lines = [
        "; Agent configuration",
        "[general]",
        "persistentagents=yes",
        "[agents]",
        "autologoff=15",
        "autologoffunavail=yes",
        "ackcall=no",
        "endcall=yes",
        "wrapuptime=5000",
        "musiconhold => default",
        ";",
        "; This section contains the agent definitions, in the form:",
        ";",
        ";   agent => agentid,agentpassword,name",
        ";",
        "agent => 300,300",
        "agent => 301,301",
    ]
    code_listing("14-queues-fig06.png", "agents.conf", lines,
                 hi_prefixes=("[",), fsize=28, lh=36, top=190)


# ---- fig04: Agents — login flow (flat icons + correct CLI) ----
def fig04():
    img, d = canvas()
    title(d, "Agents")
    fb = font(SANS_B, 32)
    fnote = font(SANS, 30)
    fmono = font(MONO, 26)
    # phone + person on the left
    phone(d, 200, 280, s=3.2, fill=INK)
    person(d, 250, 560, s=3.4)
    # Agent 300 badge linked to phone
    rbox(d, 470, 300, 230, 110, fill=BOXBG, outline=INK, width=3, r=14)
    d.text((510, 340), "Agent 300", font=fb, fill=ACCENT)
    conn_arrow(d, (400, 350), (470, 355), INK, width=3)
    # notes
    def note(x, y, w, lines):
        yy = y
        for ln, fnt, col in lines:
            for wl in wrap(d, ln, fnt, w):
                d.text((x, yy), wl, font=fnt, fill=col)
                yy += 40
            yy += 6
        return yy
    note(820, 240, 700, [
        ("1. The user dials an extension that runs the agentlogin() application.", fnote, INK),
    ])
    note(820, 360, 700, [
        ("2. agentlogin() runs and binds Agent 300 to the current channel.", fnote, INK),
    ])
    note(820, 480, 700, [
        ("3. Check agent status with the CLI command:", fnote, INK),
    ])
    d.text((820, 560), "asterisk*CLI> agent show all", font=fmono, fill=ACCENT)
    save(img, "14-queues-fig04.png")


# ---- fig05: Agent mobility (flat icons + correct CLI) ----
def fig05():
    img, d = canvas()
    title(d, "Agent Mobility")
    fb = font(SANS_B, 32)
    fnote = font(SANS, 30)
    fmono = font(MONO, 26)
    phone(d, 200, 270, s=3.2, fill=INK)
    person(d, 250, 560, s=3.4)
    rbox(d, 470, 290, 230, 110, fill=BOXBG, outline=INK, width=3, r=14)
    d.text((510, 330), "Agent 300", font=fb, fill=ACCENT)
    conn_arrow(d, (400, 345), (470, 345), INK, width=3)
    def note(x, y, w, text):
        yy = y
        for wl in wrap(d, text, fnote, w):
            d.text((x, yy), wl, font=fnote, fill=INK)
            yy += 40
        return yy
    y = note(820, 230, 700,
             "1. The user picks up any phone and dials a login extension, passing the "
             "agent number and password.")
    y = note(820, y + 24, 700,
             "2. After agentlogin() succeeds, Agent 300 is ready to take calls.")
    note(820, y + 24, 700, "3. Check status with the CLI command:")
    d.text((820, y + 110), "asterisk*CLI> agent show all", font=fmono, fill=ACCENT)
    save(img, "14-queues-fig05.png")


# ---- fig07: Queue() application syntax + options ----
def fig07():
    img, d = canvas()
    title(d, "The Queue() Application")
    fmono = font(MONO, 28)
    fk = font(MONO, 30)
    fv = font(SANS, 28)
    # syntax box
    syn = "Queue(queuename[,options[,URL][,announceoverride][,timeout][,AGI]])"
    rbox(d, 110, 180, W-220, 80, fill=BOXBG, outline=LINE, width=2, r=14)
    d.text((140, 206), syn, font=fmono, fill=ACCENT)
    # options two-column list
    opts = [
        ("d", "data-quality (modem) call (minimum delay)"),
        ("h", "allow callee to hang up by pressing *"),
        ("H", "allow caller to hang up by pressing *"),
        ("n", "no retries on the timeout; exit this application"),
        ("i", "ignore call-forward requests from queue members"),
        ("r", "ring instead of playing MOH"),
        ("t", "allow the called user to transfer the call"),
        ("T", "allow the calling user to transfer the call"),
        ("w", "allow the called user to record via MixMonitor"),
        ("W", "allow the calling user to record via MixMonitor"),
    ]
    d.text((150, 300), "Options:", font=font(SANS_B, 30), fill=INK)
    y = 360
    for k, v in opts:
        d.text((180, y), k, font=fk, fill=ACCENT)
        d.text((250, y), "— " + v, font=fv, fill=INK)
        y += 50
    save(img, "14-queues-fig07.png")


# ---- fig08: AgentLogin() application syntax + option ----
def fig08():
    img, d = canvas()
    title(d, "The AgentLogin() Application")
    fmono = font(MONO, 30)
    fk = font(MONO, 32)
    fv = font(SANS, 30)
    fnote = font(SANS, 28)
    d.text((180, 230), "Asks the agent to log in. Always returns -1.",
           font=font(SANS, 30), fill=INK)
    rbox(d, 110, 300, W-220, 80, fill=BOXBG, outline=LINE, width=2, r=14)
    d.text((140, 326), "AgentLogin([AgentNo][,options])", font=fmono, fill=ACCENT)
    d.text((150, 430), "Option:", font=font(SANS_B, 30), fill=INK)
    d.text((180, 500), "s", font=fk, fill=ACCENT)
    d.text((250, 502), "— silent login: do not announce the login confirmation",
           font=fv, fill=INK)
    d.text((180, 600),
           "While logged in, the agent hears a beep on each new call and",
           font=fnote, fill=MUTED)
    d.text((180, 640),
           "can dump the call by pressing the * key.",
           font=fnote, fill=MUTED)
    save(img, "14-queues-fig08.png")


# ---- fig09: Support applications + CLI commands ----
def fig09():
    img, d = canvas()
    title(d, "Managing Queues at Runtime")
    fh = font(SANS_B, 36)
    fk = font(MONO, 30)
    fv = font(SANS, 30)
    fc = font(MONO, 30)
    # Support applications
    d.text((150, 220), "Dialplan applications", font=fh, fill=ACCENT)
    apps = [
        ("AddQueueMember()", "dynamically add a member (e.g. PJSIP/3000) to a queue"),
        ("RemoveQueueMember()", "dynamically remove a member from a queue"),
        ("PauseQueueMember()", "temporarily pause a member without removing them"),
    ]
    y = 290
    for k, v in apps:
        d.ellipse([170, y+14, 186, y+30], fill=ACCENT)
        d.text((210, y), k, font=fk, fill=INK)
        kw = d.textlength(k, font=fk)
        d.text((210 + kw + 16, y+2), "— " + v, font=fv, fill=MUTED)
        y += 64
    # CLI commands
    d.text((150, y + 40), "CLI commands", font=fh, fill=ACCENT)
    y += 110
    cmds = [
        ("agent show all", "list all configured agents and their status"),
        ("queue show", "list all queues"),
        ("queue show <name>", "show a specific queue's data"),
    ]
    for c, v in cmds:
        d.ellipse([170, y+14, 186, y+30], fill=ACCENT)
        d.text((210, y), c, font=fc, fill=INK)
        cw = d.textlength(c, font=fc)
        d.text((210 + cw + 16, y+2), "— " + v, font=fv, fill=MUTED)
        y += 64
    save(img, "14-queues-fig09.png")


# ---- fig10: ACD configuration tasks (numbered) ----
def fig10():
    img, d = canvas()
    title(d, "ACD Configuration Tasks")
    fnum = font(SANS_B, 34)
    ftxt = font(SANS, 34)
    ftag = font(SANS_B, 26)
    tasks = [
        ("1", "Create the call queue", "required", "queues.conf"),
        ("2", "Define agent parameters", "optional", "agents.conf"),
        ("3", "Create the agents", "optional", "agents.conf"),
        ("4", "Put the queue in the dial plan", "required", "extensions.conf"),
        ("5", "Configure agent recording", "optional", "queues.conf"),
        ("6", "Verify with agent show all and queue show", "optional", "CLI"),
    ]
    x = 220
    y = 250
    for num, txt, tag, where in tasks:
        d.ellipse([x, y, x+50, y+50], fill=ACCENT)
        nw = d.textlength(num, font=fnum)
        d.text((x+25-nw/2, y+5), num, font=fnum, fill="white")
        d.text((x+80, y+5), txt, font=ftxt, fill=INK)
        # required/optional tag
        tagcol = ACCENT if tag == "required" else MUTED
        tw = d.textlength(tag, font=ftag)
        bx = 1180
        rbox(d, bx, y+4, tw+30, 42, fill="white",
             outline=tagcol, width=2, r=20)
        d.text((bx+15, y+10), tag, font=ftag, fill=tagcol)
        y += 90
    save(img, "14-queues-fig10.png")


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04(); fig05()
    fig06(); fig07(); fig08(); fig09(); fig10()
    print("done")
