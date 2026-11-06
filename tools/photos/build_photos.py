#!/usr/bin/env python3
"""Turn the selected Drive photos into self-hosted WebP files + gallery markup.

Input : tools/photos/selection.json and a folder of 2400px renditions named
        <drive_id>.jpg (made by fetch_drive.py; kept outside the repo).
Output: assets/photos/<key>-640.webp / -1600.webp (hero also -900 / -2400)
        tools/photos/out/manifest.json  (key -> sizes, average colour)
        tools/photos/out/gallery.html   (inlined by build_index.py at {{GALLERY}})

Why self-host: the old page hot-linked 4 images from a rental-space CDN that we
do not control. Why the average colour: it fills each tile before the image
loads (dominant-colour placeholder), so the grid never flashes white.

Usage: build_photos.py <rendition_dir>
       build_photos.py --markup-only   (rebuild gallery.html / counts.json from the existing
                                        manifest.json, e.g. after editing "mosaic"; no images touched)
"""
import html, json, os, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_IMG = os.path.join(ROOT, "assets", "photos")
OUT = os.path.join(HERE, "out")
SIZES = [640, 1600]
HERO_SIZES = [900, 1600, 2400]


def avg_hex(im):
    c = im.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))
    return "#%02X%02X%02X" % c


def main():
    src = sys.argv[1]
    sel = json.load(open(os.path.join(HERE, "selection.json")))
    if src == "--markup-only":
        manifest = json.load(open(os.path.join(OUT, "manifest.json")))
        missing = [p["key"] for p in sel["photos"] if p["key"] not in manifest]
        if missing:
            sys.exit(f"not in manifest.json (run with a rendition dir first): {missing}")
        write_markup(sel, manifest)
        return
    os.makedirs(OUT_IMG, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for p in sel["photos"]:
        im = ImageOps.exif_transpose(Image.open(os.path.join(src, p["drive_id"] + ".jpg"))).convert("RGB")
        sizes = HERO_SIZES if p["key"] == sel["hero"] else SIZES
        made = []
        for w in sizes:
            w = min(w, max(im.size))
            r = im.copy()
            r.thumbnail((w, w), Image.LANCZOS)
            r.save(os.path.join(OUT_IMG, f"{p['key']}-{w}.webp"), "WEBP", quality=78, method=6)
            made.append((w, r.size))
        manifest[p["key"]] = {"w": im.size[0], "h": im.size[1], "color": avg_hex(im),
                              "files": [[f"assets/photos/{p['key']}-{w}.webp", s[0], s[1]] for w, s in made]}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    # Remove files of photos dropped from the selection so stale images are not published.
    keep = {os.path.basename(f[0]) for m in manifest.values() for f in m["files"]}
    for f in os.listdir(OUT_IMG):
        if f not in keep:
            os.remove(os.path.join(OUT_IMG, f))
            print("removed stale", f)

    write_markup(sel, manifest)


def write_markup(sel, manifest):
    # Gallery tiles: thumbnails are the 640 file, the lightbox loads the 1600 file.
    # The "mosaic" photos (the arrival landmarks) are shown in the arrival section, so they are not repeated in the album.
    album = [p for p in sel["photos"] if p["key"] not in sel["mosaic"]]
    tiles = []
    for n, p in enumerate(album):
        m = manifest[p["key"]]
        small, large = m["files"][0], m["files"][-1] if p["key"] != sel["hero"] else m["files"][1]
        cap, alt = html.escape(p["caption"]), html.escape(p["alt"])
        tiles.append(
            f'<li data-cat="{p["cat"]}" style="--lqip:{m["color"]}">'
            f'<button type="button" data-full="{large[0]}" data-i="{n}" aria-label="写真を拡大：{cap}">'
            f'<img src="{small[0]}" alt="{alt}" width="{small[1]}" height="{small[2]}" loading="lazy" decoding="async">'
            f'<span class="cap">{cap}</span></button></li>')
    open(os.path.join(OUT, "gallery.html"), "w", encoding="utf-8").write("\n".join(tiles))
    counts = {}
    for p in album:
        counts[p["cat"]] = counts.get(p["cat"], 0) + 1
    json.dump(counts, open(os.path.join(OUT, "counts.json"), "w"))
    total = sum(os.path.getsize(os.path.join(OUT_IMG, f)) for f in os.listdir(OUT_IMG))
    print(f"{len(sel['photos'])} photos, {counts}, assets/photos = {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
