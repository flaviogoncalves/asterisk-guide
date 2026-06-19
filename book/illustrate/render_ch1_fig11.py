#!/usr/bin/env python3
"""PATH-2/flow figure: ch1 fig11 — contact-center queue -> ACD -> agents, rendered with
Pillow in the house style. Strategies are current to Asterisk 22 (roundrobin removed)."""
from PIL import Image, ImageDraw, ImageFont
import os, math
W, H = 1600, 900
INK = (26, 26, 26); ACCENT = (28, 93, 153); MUTED = (90, 90, 90); BOXBG = (245, 247, 250); LINE = (170, 178, 190)
OUT = os.path.join(os.path.dirname(__file__), "staging"); os.makedirs(OUT, exist_ok=True)

def font(paths, s):
    for p in paths:
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, s)
            except Exception: pass
    return ImageFont.load_default()
SANS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]
SANSB = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
MONO = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Supplemental/Courier New.ttf"]

img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
tf = font(SANSB, 54); t = "Contact-Center Queue and ACD"; tw = d.textlength(t, font=tf)
d.text(((W - tw) / 2, 60), t, font=tf, fill=INK); d.line([(W/2 - tw/2, 148), (W/2 + tw/2, 148)], fill=ACCENT, width=5)

def rbox(x, y, w, h, fill=BOXBG, outline=LINE, wdt=2, r=18):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=wdt)
def arrow(p1, p2, fill=ACCENT, width=6):
    d.line([p1, p2], fill=fill, width=width); a = math.atan2(p2[1]-p1[1], p2[0]-p1[0]); s = 20
    d.polygon([p2, (p2[0]-s*math.cos(a-0.4), p2[1]-s*math.sin(a-0.4)), (p2[0]-s*math.cos(a+0.4), p2[1]-s*math.sin(a+0.4))], fill=fill)

fb = font(SANSB, 38); fm = font(MONO, 30); fs = font(SANS, 30)
rbox(70, 300, 210, 90, fill=ACCENT, outline=ACCENT, r=45); d.text((110, 322), "1-800", font=fb, fill="white")
rbox(360, 270, 300, 150, r=22); d.text((430, 300), "Call Queue", font=fb, fill=INK); d.text((400, 352), "callers wait in line", font=fs, fill=MUTED)
rbox(760, 255, 700, 180, fill=(235, 242, 250), outline=ACCENT, r=22); d.text((980, 278), "ACD", font=fb, fill=ACCENT)
d.text((800, 345), "strategy: ringall · leastrecent ·", font=fm, fill=INK)
d.text((800, 385), "fewestcalls · rrmemory · linear", font=fm, fill=INK)
arrow((280, 345), (355, 345)); arrow((660, 345), (755, 345))
for i, nm in enumerate(["Agent 1", "Agent 2", "Agent 3", "Agent N"]):
    cx = 860 + i*150; ay = 640
    arrow((1110, 440), (cx, ay-60), width=4)
    d.ellipse([cx-26, ay-26, cx+26, ay+26], fill=INK); d.ellipse([cx-12, ay-14, cx+12, ay+10], fill="white")
    tw = d.textlength(nm, font=fs); d.text((cx-tw/2, ay+40), nm, font=fs, fill=INK)
img.save(os.path.join(OUT, "01-introduction-fig11.png")); print("wrote fig11")
