#!/usr/bin/env python3
"""Assemble index.html from tools/index.template.html + generated parts.

Why: the route map is generated from OpenStreetMap data by tools/map/build_map.py,
and the photo gallery by tools/photos/build_photos.py. Keeping the page as a
template means either can be regenerated and re-inlined without touching the
hand-written HTML/CSS. Run from anywhere:

    python3 tools/build_index.py

Placeholders: {{MAP_SVG}}  {{GALLERY}}  {{N_ALL}} {{N_<cat>}}  {{C:<photo key>}} (placeholder colour)
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, "index.template.html")
SVG = os.path.join(HERE, "map", "out", "route-map.svg")
PH = os.path.join(HERE, "photos", "out")
OUT = os.path.join(ROOT, "index.html")

tpl = open(TPL, encoding="utf-8").read()
svg = open(SVG, encoding="utf-8").read().strip()
svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
for ph in ("{{MAP_SVG}}", "{{GALLERY}}"):
    if ph not in tpl:
        sys.exit(f"placeholder {ph} missing in template")
if 'class="routemap"' not in svg:
    sys.exit("route-map.svg lacks class=routemap")

gallery = open(os.path.join(PH, "gallery.html"), encoding="utf-8").read()
counts = json.load(open(os.path.join(PH, "counts.json")))
manifest = json.load(open(os.path.join(PH, "manifest.json")))

out = tpl.replace("{{MAP_SVG}}", svg).replace("{{GALLERY}}", gallery)
out = out.replace("{{N_ALL}}", str(sum(counts.values())))
for k, v in counts.items():
    out = out.replace("{{N_%s}}" % k, str(v))
out = re.sub(r"\{\{C:([\w-]+)\}\}", lambda m: manifest[m.group(1)]["color"], out)

left = re.findall(r"\{\{[^}]+\}\}", out)
if left:
    sys.exit(f"unfilled placeholders: {sorted(set(left))}")
# every local image the page references must exist
missing = [p for p in set(re.findall(r'assets/photos/[\w-]+\.webp', out)) if not os.path.exists(os.path.join(ROOT, p))]
if missing:
    sys.exit(f"missing photo files: {missing}")
open(OUT, "w", encoding="utf-8").write(out)
print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes)")
