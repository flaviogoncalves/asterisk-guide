#!/usr/bin/env python3
"""Front cover for Asterisk Guide — clean typographic design in the house brand style.
Letter ratio (8.5:11) so it works as the EPUB cover and a full-page PDF cover.
Outputs src/images/cover.png."""
from PIL import Image, ImageDraw, ImageFont
import os, math
W, H = 1700, 2200
BRAND = (28, 93, 153)      # #1C5D99
INK = (20, 48, 74)         # brandink
MUTED = (90, 100, 112)
LIGHT = (210, 222, 235)
OUT = "src/images/cover.png"

def font(paths, s):
    for p in paths:
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, s)
            except Exception: pass
    return ImageFont.load_default()
SANSB = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
SANS  = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"]

img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)

# --- top brand band with a stylized asterisk mark ---
band_h = 880
d.rectangle([0, 0, W, band_h], fill=BRAND)
# eyebrow
fe = font(SANSB, 40)
d.text((150, 150), "A S T E R I S K   2 2   L T S", font=fe, fill=(180, 205, 230))
# 6-arm asterisk starburst (white) centered in the band
cx, cy, r, tw = W/2, band_h/2 + 60, 230, 46
for k in range(6):
    a = math.radians(k * 60 - 90)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    d.polygon([(cx+nx*tw, cy+ny*tw), (cx+dx*r+nx*tw*0.25, cy+dy*r+ny*tw*0.25),
               (cx+dx*r-nx*tw*0.25, cy+dy*r-ny*tw*0.25), (cx-nx*tw, cy-ny*tw)], fill="white")
d.ellipse([cx-tw, cy-tw, cx+tw, cy+tw], fill="white")

# --- title block ---
ft = font(SANSB, 168)
d.text((150, band_h + 110), "Asterisk", font=ft, fill=INK)
d.text((150, band_h + 110 + 180), "Guide", font=ft, fill=INK)
# accent rule
d.rectangle([158, band_h + 500, 158 + 520, band_h + 512], fill=BRAND)
# subtitle
fs = font(SANS, 58)
d.text((150, band_h + 560), "Building an IP PBX with", font=fs, fill=MUTED)
d.text((150, band_h + 560 + 70), "Asterisk 22 LTS", font=fs, fill=MUTED)

# --- subtle network motif (central node + spokes) low on the page ---
mx, my, mr = W/2, H - 540, 12
pts = [(mx + 380*math.cos(math.radians(a)), my + 230*math.sin(math.radians(a))) for a in range(0, 360, 60)]
for px, py in pts:
    d.line([(mx, my), (px, py)], fill=LIGHT, width=4)
    d.ellipse([px-10, py-10, px+10, py+10], fill=LIGHT)
d.ellipse([mx-mr, my-mr, mx+mr, my+mr], fill=BRAND)

# --- edition + author footer ---
fed = font(SANSB, 46)
d.text((150, H - 230), "S E C O N D   E D I T I O N", font=fed, fill=BRAND)
fa = font(SANSB, 66)
d.text((150, H - 165), "Flavio E. Gonçalves", font=fa, fill=INK)

img.save(OUT); print("wrote", OUT, img.size)
