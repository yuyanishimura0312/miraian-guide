#!/usr/bin/env python3
"""Make numbered contact sheets so a human (or Claude) can review and pick photos.

Usage: contact_sheet.py <inventory.json> <img_dir> <out_dir> [per_sheet]
Each tile is labelled with its index in the inventory, so picks can be
recorded as indices in tools/photos/selection.json.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageOps

inv = json.load(open(sys.argv[1]))
src, out = sys.argv[2], sys.argv[3]
per = int(sys.argv[4]) if len(sys.argv) > 4 else 24
os.makedirs(out, exist_ok=True)
cols, tw, th = 6, 320, 214
tiles = []
for i, f in enumerate(inv):
    p = os.path.join(src, f["id"] + ".jpg")
    if os.path.exists(p):
        tiles.append((i, f, p))
for s in range(0, len(tiles), per):
    chunk = tiles[s:s + per]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for k, (i, f, p) in enumerate(chunk):
        im = ImageOps.exif_transpose(Image.open(p))
        im.thumbnail((tw - 6, th - 6))
        x, y = (k % cols) * tw, (k // cols) * (th + 18)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 4, y + th), f"#{i} {f['path'][-8:]}", fill="black")
    sheet.save(os.path.join(out, f"sheet_{s // per:02d}.jpg"), quality=80)
print(len(tiles), "tiles")
