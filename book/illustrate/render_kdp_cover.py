#!/usr/bin/env python3
"""KDP paperback WRAPAROUND cover (back | spine | front) for Asterisk Guide.
Dimensions from the KDP formula (see kdp-formatter skill): trim 7.5x9.25, white paper,
spine = pages * 0.002252in, 0.125in bleed all sides, 300 DPI.
Re-run with the correct PAGES after each interior build. Verify against KDP's cover template
generator before publishing.  Output: book/kdp/asterisk-guide-cover.png
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

DPI = 300
TRIM_W, TRIM_H = 7.5, 9.25
BLEED = 0.125
PAGES = 426
SPINE_FACTOR = 0.002252          # white paper, black ink
SPINE = PAGES * SPINE_FACTOR     # inches

def px(inch): return int(round(inch * DPI))
bl, tw, th, sp = px(BLEED), px(TRIM_W), px(TRIM_H), px(SPINE)
W = 2*bl + tw + sp + tw
H = 2*bl + th
BRAND = (28, 93, 153); INK = (20, 48, 74); MUTED = (90, 100, 112); LIGHT = (210, 222, 235)
ACCENT = (232, 119, 34)   # Asterisk orange

def font(paths, s):
    for p in paths:
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, s)
            except Exception: pass
    return ImageFont.load_default()
SANSB = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
SANS  = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]

img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
back_x0 = bl; spine_x0 = bl + tw; front_x0 = bl + tw + sp
band_h = bl + int(0.30 * th)

# continuous blue top band across back + front, and a full-height blue spine
d.rectangle([0, 0, W, band_h], fill=BRAND)
d.rectangle([spine_x0, 0, spine_x0 + sp, H], fill=BRAND)

# ---------------- FRONT panel ----------------
fcx = front_x0 + tw//2
# eyebrow + hero node-graph on the band
fe = font(SANSB, px(0.16)); d.text((front_x0 + px(0.6), bl + px(0.5)), "A S T E R I S K   2 2   L T S", font=fe, fill=(180,205,230))
# hero motif: node-graph (central node + radiating SIP/PBX links), clean & solid white,
# with an Asterisk-orange core. Single hero mark on the front band (compass-star removed).
cx, cy = fcx, band_h - px(0.95)
spoke, sat, hub = px(0.95), px(0.11), px(0.21)
for k in range(6):
    a = math.radians(k*60 - 90); ex, ey = cx + spoke*math.cos(a), cy + spoke*math.sin(a)
    d.line([(cx, cy), (ex, ey)], fill="white", width=px(0.035))
    d.ellipse([ex-sat, ey-sat, ex+sat, ey+sat], fill="white")
d.ellipse([cx-hub, cy-hub, cx+hub, cy+hub], fill="white")
d.ellipse([cx-hub+px(0.05), cy-hub+px(0.05), cx+hub-px(0.05), cy+hub-px(0.05)], fill=ACCENT)
# title
ft = font(SANSB, px(0.62)); ty = band_h + px(0.55)
d.text((front_x0 + px(0.65), ty), "Asterisk", font=ft, fill=INK)
d.text((front_x0 + px(0.65), ty + px(0.66)), "Guide", font=ft, fill=INK)
d.rectangle([front_x0 + px(0.68), ty + px(1.5), front_x0 + px(0.68) + px(2.0), ty + px(1.54)], fill=ACCENT)
fs = font(SANS, px(0.22))
d.text((front_x0 + px(0.65), ty + px(1.7)), "Building an IP PBX with", font=fs, fill=MUTED)
d.text((front_x0 + px(0.65), ty + px(1.7) + px(0.28)), "Asterisk 22 LTS", font=fs, fill=MUTED)
fed = font(SANSB, px(0.17)); fau = font(SANSB, px(0.26))
d.text((front_x0 + px(0.65), bl + th - px(0.95)), "S E C O N D   E D I T I O N", font=fed, fill=BRAND)
d.text((front_x0 + px(0.65), bl + th - px(0.65)), "Flavio E. Gonçalves", font=fau, fill=INK)

# ---------------- SPINE (>=79 pages, so spine text is allowed) ----------------
sp_img = Image.new("RGB", (th, sp), BRAND); sd = ImageDraw.Draw(sp_img)
fsp = font(SANSB, int(sp*0.42))
t1 = "Asterisk Guide"; w1 = sd.textlength(t1, font=fsp)
sd.text(((th - w1)/2, sp*0.18), t1, font=fsp, fill="white")
fsp2 = font(SANS, int(sp*0.30)); t2 = "Gonçalves"; w2 = sd.textlength(t2, font=fsp2)
sd.text((th - w2 - px(0.4), sp*0.30), t2, font=fsp2, fill=(200,218,236))
img.paste(sp_img.rotate(90, expand=True), (spine_x0, 0))

# ---------------- BACK panel ----------------
bx = back_x0 + px(0.6); fy = band_h + px(0.6)
fh = font(SANSB, px(0.30)); d.text((bx, fy), "About this book", font=fh, fill=INK)
fb = font(SANS, px(0.155)); fbb = font(SANSB, px(0.155)); fy += px(0.55)
# Lead hook (bold, from the market analysis): the only current PJSIP-first Asterisk 22 guide.
hook = ("The only current, PJSIP-first guide to Asterisk 22 — while the long-reigning "
        "reference is six years stale and predates PJSIP entirely.")
blurb = ("Asterisk Guide is a hands-on, lab-verified path to building a production IP PBX "
         "with Asterisk 22 LTS — the modern, PJSIP-first way. Every example is tested against "
         "a reproducible Asterisk 22 lab, and the source and lab are free and open.")
def wrap(txt, ff, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t, font=ff) <= maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines
maxw = tw - px(1.2)
for ln in wrap(hook, fbb, maxw):
    d.text((bx, fy), ln, font=fbb, fill=INK); fy += px(0.24)
fy += px(0.08)
for ln in wrap(blurb, fb, maxw):
    d.text((bx, fy), ln, font=fb, fill=(60,68,78)); fy += px(0.24)
fy += px(0.2)
d.text((bx, fy), "Inside:", font=font(SANSB, px(0.17)), fill=BRAND); fy += px(0.34)
topics = ["PJSIP endpoints, trunks and WebRTC", "the dialplan, IVR and voicemail",
          "queues and call-center features", "CDR/CEL billing, AMI / AGI / ARI",
          "realtime (Sorcery), security and TLS", "installation and deployment"]
ftb = font(SANS, px(0.155))
for tp in topics:
    d.ellipse([bx, fy+px(0.05), bx+px(0.07), fy+px(0.12)], fill=BRAND)
    d.text((bx+px(0.16), fy), tp, font=ftb, fill=(60,68,78)); fy += px(0.28)
# author + publisher line near bottom-left (barcode goes bottom-RIGHT, keep it clear/white)
d.text((bx, bl + th - px(0.7)), "Flavio E. Gonçalves — VoIP School", font=font(SANSB, px(0.16)), fill=INK)
d.text((bx, bl + th - px(0.45)), "voip.school", font=font(SANS, px(0.14)), fill=MUTED)

os.makedirs("book/kdp", exist_ok=True)
out = "book/kdp/asterisk-guide-cover.png"
img.save(out, dpi=(DPI, DPI))
print(f"wrote {out}  {W}x{H}px = {W/DPI:.3f}x{H/DPI:.3f}in  (spine {SPINE:.4f}in / {PAGES}pp)")
