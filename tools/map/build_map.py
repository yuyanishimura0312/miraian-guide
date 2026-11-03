#!/usr/bin/env python3
"""Build an accurate route map (SVG) for the Mirai-an access guide from OpenStreetMap data.

Why this exists: the earlier hand-drawn schematic placed streets and the university
by eye, and was not accurate. This script projects real OSM geometry, computes the
walking route on public streets only (no campus paths), and writes tools/map/out/route-map.svg
plus route stats (distance) to tools/map/out/route.json.

Data: tools/map/data/osm.json (Overpass extract, © OpenStreetMap contributors, ODbL).
Venue position = the Google Maps place pin confirmed by the owner on 2026-11-04.
"""
import json, math, os, sys
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
OSM = json.load(open(os.path.join(HERE, "data", "osm.json")))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)

VENUE = (35.0263201, 135.7846307)      # confirmed pin (owner, 2026-11-04)
STATION_EXIT = (35.03015, 135.77265)   # Keihan Demachiyanagi, exit 3 (Imadegawa-dori side)
BUS_STOP = (35.02855, 135.78370)       # Kyodai-Nogakubu-mae (OSM nodes, Imadegawa-dori) - owner: 5 min
SEIMON_STOP = (35.02571, 135.77852)    # Kyodai-Seimon-mae (OSM node, Higashioji-dori) - alternative
MILLION = (35.02876, 135.77924)        # Hyakumanben crossing

# view box in lat/lon
LAT0, LAT1 = 35.0223, 35.0322
LON0, LON1 = 135.7700, 135.7885
W = 1000
MY = 111320.0
MX = 111320.0 * math.cos(math.radians((LAT0 + LAT1) / 2))
SCALE = W / ((LON1 - LON0) * MX)          # px per metre
H = round((LAT1 - LAT0) * MY * SCALE)

def P(lat, lon):
    return ((lon - LON0) * MX * SCALE, (LAT1 - lat) * MY * SCALE)

def path_d(coords, close=False):
    pts = [P(c["lat"], c["lon"]) for c in coords]
    s = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return s + ("Z" if close else "")

def dist_m(a, b):
    return math.hypot((a[1] - b[1]) * MX, (a[0] - b[0]) * MY)

ROAD_W = {"primary": 7, "secondary": 6, "tertiary": 4.2, "unclassified": 2.4,
          "residential": 2.0, "living_street": 1.8, "pedestrian": 1.8}
PUBLIC = set(ROAD_W)

layers = {"water": [], "river": [], "campus": [], "wood": [], "shrine": [], "minor": [], "major": [], "rail": []}
G = nx.Graph()
for e in OSM["elements"]:
    t = e.get("tags", {})
    geoms = []
    if e["type"] == "way" and "geometry" in e:
        geoms = [e["geometry"]]
    elif e["type"] == "relation":
        geoms = [m["geometry"] for m in e.get("members", []) if m.get("geometry") and m.get("role") in ("outer", "", "main_stream")]
    for g in geoms:
        hw = t.get("highway")
        if t.get("natural") == "water":
            layers["water"].append(path_d(g, True))
        elif t.get("waterway") in ("river", "canal"):
            layers["river"].append((path_d(g), t.get("waterway"), t.get("name", "")))
        elif t.get("amenity") == "university":
            layers["campus"].append(path_d(g, True))
        elif t.get("natural") == "wood" or t.get("leisure") == "park":
            layers["wood"].append(path_d(g, True))
        elif t.get("amenity") == "place_of_worship" and t.get("religion") == "shinto":
            layers["shrine"].append(path_d(g, True))
        elif t.get("railway") and t.get("tunnel") != "yes" and t.get("layer", "0") >= "0":
            layers["rail"].append(path_d(g))
        elif hw in PUBLIC:
            (layers["major"] if hw in ("primary", "secondary", "tertiary") else layers["minor"]).append((path_d(g), hw))
            for a, b in zip(g, g[1:]):
                pa, pb = (a["lat"], a["lon"]), (b["lat"], b["lon"])
                # prefer named main streets a little: easier to follow on foot
                k = 1.0 if hw in ("primary", "secondary", "tertiary") else 1.35
                G.add_edge(pa, pb, w=dist_m(pa, pb) * k, m=dist_m(pa, pb), name=t.get("name", ""))

def nearest(pt):
    return min(G.nodes, key=lambda n: dist_m(n, pt))

def route(a, b):
    nodes = nx.shortest_path(G, nearest(a), nearest(b), weight="w")
    length = sum(G[u][v]["m"] for u, v in zip(nodes, nodes[1:]))
    legs = []
    for u, v in zip(nodes, nodes[1:]):
        n = G[u][v]["name"] or "(無名の道)"
        if legs and legs[-1][0] == n: legs[-1][1] += G[u][v]["m"]
        else: legs.append([n, G[u][v]["m"]])
    print([(n, round(m)) for n, m in legs if m > 15])
    return nodes, length

r_station, len_station = route(STATION_EXIT, VENUE)
r_bus, len_bus = route(BUS_STOP, VENUE)
r_seimon, len_seimon = route(SEIMON_STOP, VENUE)

def line(nodes):
    pts = [P(*n) for n in nodes]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

json.dump({"station_m": round(len_station), "bus_m": round(len_bus), "seimon_m": round(len_seimon),
           "station_min_80m": round(len_station / 80), "bus_min_80m": round(len_bus / 80)},
          open(os.path.join(OUT, "route.json"), "w"), ensure_ascii=False, indent=1)

def lbl(lat, lon, text, cls="lbl", dx=0, dy=0, anchor="middle", rot=0):
    x, y = P(lat, lon); x += dx; y += dy
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}"{tr}>{text}</text>'

vx, vy = P(*VENUE); sx, sy = P(*STATION_EXIT); bx, by = P(*BUS_STOP); mx, my = P(*MILLION); gx, gy = P(*SEIMON_STOP)
bar = 200 * SCALE  # 200 m

svg = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="mp-t mp-d" class="routemap">',
       '<title id="mp-t">出町柳駅・京大正門前から未来庵までの道順の地図</title>',
       '<desc id="mp-d">京阪出町柳駅の出口3から今出川通を東へ進み、百万遍交差点を渡ってさらに東へ。京大農学部前のバス停の先で右（南）へ曲がって約230メートル進むと、京都大学の東側に未来庵があります。点線は京大正門前のバス停から東一条通を通る道です。</desc>',
       f'<rect width="{W}" height="{H}" class="m-bg"/>',
       '<g class="m-wood">' + "".join(f'<path d="{d}"/>' for d in layers["wood"]) + '</g>',
       '<g class="m-campus">' + "".join(f'<path d="{d}"/>' for d in layers["campus"]) + '</g>',
       '<g class="m-shrine">' + "".join(f'<path d="{d}"/>' for d in layers["shrine"]) + '</g>',
       '<g class="m-water">' + "".join(f'<path d="{d}"/>' for d in layers["water"]) + '</g>',
       '<g class="m-river">' + "".join(f'<path d="{d}" class="{k}"/>' for d, k, n in layers["river"]) + '</g>',
       '<g class="m-minor">' + "".join(f'<path d="{d}"/>' for d, hw in layers["minor"]) + '</g>',
       '<g class="m-major">' + "".join(f'<path d="{d}" style="stroke-width:{ROAD_W[hw]}"/>' for d, hw in layers["major"]) + '</g>',
       f'<path class="m-route-bus" d="{line(r_seimon)}"/>',
       f'<path class="m-route" d="{line(r_station)}"/>',
       # labels
       lbl(35.0272, 135.7812, "京都大学", "m-area"),
       lbl(35.0272, 135.7812, "KYOTO UNIVERSITY", "m-area-en", dy=22),
       lbl(35.0247, 135.7872, "吉田山", "m-area"),
       lbl(35.0247, 135.7872, "吉田神社", "m-area-en", dy=20),
       lbl(35.0300, 135.7712, "鴨川", "m-water-l", dx=-14, rot=-78),
       lbl(35.0318, 135.7738, "高野川", "m-water-l", dx=18, rot=-62),
       lbl(35.02885, 135.7755, "今出川通", "m-road", dy=-13),
       lbl(35.0238, 135.7791, "東大路通", "m-road", dx=-13, rot=-90),
       lbl(35.02525, 135.7812, "東一条通", "m-road", dy=19),
       f'<g class="m-stop"><circle cx="{sx:.1f}" cy="{sy:.1f}" r="13"/><text x="{sx:.1f}" y="{sy:.1f}">1</text></g>',
       f'<text x="{sx:.1f}" y="{sy+36:.1f}" class="m-pt" text-anchor="middle">出町柳駅</text>',
       f'<text x="{sx:.1f}" y="{sy+54:.1f}" class="m-pt-en" text-anchor="middle">DEMACHIYANAGI · 出口3</text>',
       f'<g class="m-stop"><circle cx="{mx:.1f}" cy="{my:.1f}" r="13"/><text x="{mx:.1f}" y="{my:.1f}">2</text></g>',
       f'<text x="{mx-18:.1f}" y="{my-20:.1f}" class="m-pt" text-anchor="end">百万遍</text>',
       f'<g class="m-stop"><circle cx="{bx:.1f}" cy="{by:.1f}" r="13"/><text x="{bx:.1f}" y="{by:.1f}">3</text></g>',
       f'<text x="{bx:.1f}" y="{by-24:.1f}" class="m-pt" text-anchor="middle">京大農学部前</text>',
       f'<text x="{bx:.1f}" y="{by-42:.1f}" class="m-pt-en" text-anchor="middle">BUS STOP</text>',
       f'<g class="m-sub"><circle cx="{gx:.1f}" cy="{gy:.1f}" r="8"/></g>',
       f'<text x="{gx-16:.1f}" y="{gy+5:.1f}" class="m-pt-s" text-anchor="end">京大正門前</text>',
       f'<text x="{gx-16:.1f}" y="{gy+21:.1f}" class="m-pt-en" text-anchor="end">BUS STOP</text>',
       f'<circle class="m-goal-pulse" cx="{vx:.1f}" cy="{vy:.1f}" r="16"/>',
       f'<g class="m-goal"><path d="M{vx:.1f} {vy:.1f} c-11 -15 -17 -24 -17 -33 a17 17 0 0 1 34 0 c0 9 -6 18 -17 33z"/><circle cx="{vx:.1f}" cy="{vy-33:.1f}" r="6.5"/></g>',
       f'<text x="{vx+24:.1f}" y="{vy+2:.1f}" class="m-goal-l">未来庵</text>',
       f'<text x="{vx+24:.1f}" y="{vy+20:.1f}" class="m-pt-en">MIRAI-AN</text>',
       # north + scale
       f'<g transform="translate({W-44} 46)" class="m-north"><path d="M0 -18 L8 9 L0 3 L-8 9Z"/><text y="28" text-anchor="middle">N</text></g>',
       f'<g transform="translate(28 {H-30})" class="m-scale"><path d="M0 0 H{bar:.1f}"/><path d="M0 -5 V5 M{bar:.1f} -5 V5"/><text x="{bar/2:.1f}" y="-10" text-anchor="middle">200 m</text></g>',
       f'<text x="{W-14}" y="{H-12}" class="m-attr" text-anchor="end">地図データ © OpenStreetMap contributors</text>',
       '</svg>']
open(os.path.join(OUT, "route-map.svg"), "w").write("\n".join(svg))
print(json.load(open(os.path.join(OUT, "route.json"))), "size", W, H)
