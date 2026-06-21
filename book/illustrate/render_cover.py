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
ACCENT = (232, 119, 34)    # Asterisk orange
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
# hero motif: node-graph (central node + radiating SIP/PBX links) centered on the band.
# Clean, solid, white spokes/satellites; the center node carries the Asterisk-orange accent.
cx, cy = W/2, band_h/2 + 70
spoke, sat, hub = 250, 30, 56
for k in range(6):
    a = math.radians(k * 60 - 90)
    px_, py_ = cx + spoke*math.cos(a), cy + spoke*math.sin(a)
    d.line([(cx, cy), (px_, py_)], fill="white", width=10)
    d.ellipse([px_-sat, py_-sat, px_+sat, py_+sat], fill="white")
# center hub: white ring with an orange core
d.ellipse([cx-hub, cy-hub, cx+hub, cy+hub], fill="white")
d.ellipse([cx-hub+14, cy-hub+14, cx+hub-14, cy+hub-14], fill=ACCENT)

# --- title block ---
ft = font(SANSB, 168)
d.text((150, band_h + 110), "Asterisk", font=ft, fill=INK)
d.text((150, band_h + 110 + 180), "Guide", font=ft, fill=INK)
# accent rule (Asterisk orange)
d.rectangle([158, band_h + 500, 158 + 520, band_h + 512], fill=ACCENT)
# subtitle
fs = font(SANS, 58)
d.text((150, band_h + 560), "Building an IP PBX with", font=fs, fill=MUTED)
d.text((150, band_h + 560 + 70), "Asterisk 22 LTS", font=fs, fill=MUTED)

# (the node-graph now lives on the top band as the single hero motif; the old
#  low-page network sketch was removed because it overlapped the subtitle text.)

# --- edition + author footer ---
fed = font(SANSB, 46)
d.text((150, H - 230), "S E C O N D   E D I T I O N", font=fed, fill=BRAND)
fa = font(SANSB, 66)
d.text((150, H - 165), "Flavio E. Gonçalves", font=fa, fill=INK)

img.save(OUT); print("wrote", OUT, img.size)
