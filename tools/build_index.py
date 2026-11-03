#!/usr/bin/env python3
"""Assemble index.html from tools/index.template.html + tools/map/out/route-map.svg.

Why: the route map is generated from OpenStreetMap data by tools/map/build_map.py.
Keeping the page as a template means a regenerated map can be re-inlined without
touching the hand-written HTML/CSS. Run from anywhere:

    python3 tools/build_index.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, "index.template.html")
SVG = os.path.join(HERE, "map", "out", "route-map.svg")
OUT = os.path.join(ROOT, "index.html")

tpl = open(TPL, encoding="utf-8").read()
svg = open(SVG, encoding="utf-8").read().strip()
svg = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
if "{{MAP_SVG}}" not in tpl:
    sys.exit("placeholder {{MAP_SVG}} missing in template")
if 'class="routemap"' not in svg:
    sys.exit("route-map.svg lacks class=routemap")
open(OUT, "w", encoding="utf-8").write(tpl.replace("{{MAP_SVG}}", svg))
print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes)")
