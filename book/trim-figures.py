#!/usr/bin/env python3
"""Trim white margins from figure PNGs (LibreOffice renders WMF/EMF onto a full
A4 canvas, leaving huge borders). Usage: trim-figures.py <file-or-glob> ...
Crops to the bounding box of non-white content plus a small padding."""
import sys, glob
from PIL import Image, ImageChops

PAD = 16          # px of breathing room kept around the content
WHITE = (255, 255, 255)

def trim(path):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, WHITE)
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()          # tightest box around anything non-white
    if not bbox:
        return False
    l, t, r, b = bbox
    l = max(0, l - PAD); t = max(0, t - PAD)
    r = min(im.width, r + PAD); b = min(im.height, b + PAD)
    im.crop((l, t, r, b)).save(path)
    return True

def main(args):
    files = []
    for a in args:
        files += glob.glob(a)
    n = 0
    for f in sorted(set(files)):
        before = Image.open(f).size
        if trim(f):
            after = Image.open(f).size
            print(f"{f}: {before} -> {after}")
            n += 1
    print(f"trimmed {n} file(s)")

if __name__ == "__main__":
    main(sys.argv[1:] or ["src/images/*.png"])
