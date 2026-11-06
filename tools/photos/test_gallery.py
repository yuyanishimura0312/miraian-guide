#!/usr/bin/env python3
"""Functional check of the gallery: filters, lightbox open / prev / next / keys / close.

Usage: test_gallery.py <page url>   (serve the repo root first, e.g. python3 -m http.server)
Exits non-zero on the first failed check. Uses the installed Chrome via Playwright.
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(url)
    pg.wait_for_load_state("networkidle")
    total = pg.locator(".album-grid li").count()
    check("album has tiles", total > 0)

    pg.click('.filters button[data-f="garden"]')
    vis = pg.locator(".album-grid li:not([hidden])").count()
    garden = pg.locator('.album-grid li[data-cat="garden"]').count()
    check(f"garden filter shows {garden} of {total}", vis == garden and 0 < vis < total)
    check("pressed state moves", pg.get_attribute('.filters button[data-f="garden"]', "aria-pressed") == "true"
          and pg.get_attribute('.filters button[data-f="all"]', "aria-pressed") == "false")

    first = pg.locator(".album-grid li:not([hidden]) button").first
    first.click()
    check("lightbox opens", pg.evaluate("document.getElementById('lb').open"))
    check("counter counts only filtered", pg.text_content("#lb .lb-n") == f"1 / {garden}")
    src1 = pg.get_attribute("#lb img", "src")
    pg.click("#lb .next")
    check("next changes image", pg.get_attribute("#lb img", "src") != src1 and pg.text_content("#lb .lb-n") == f"2 / {garden}")
    pg.keyboard.press("ArrowLeft")
    check("ArrowLeft goes back", pg.get_attribute("#lb img", "src") == src1)
    pg.keyboard.press("ArrowLeft")
    check("wraps to last", pg.text_content("#lb .lb-n") == f"{garden} / {garden}")
    img_ok = pg.evaluate("new Promise(r=>{const i=document.querySelector('#lb img'); if(i.complete) r(i.naturalWidth); else i.onload=()=>r(i.naturalWidth)})")
    check("full image loads", img_ok > 1000)
    pg.keyboard.press("Escape")
    check("Escape closes", not pg.evaluate("document.getElementById('lb').open"))

    pg.click('.filters button[data-f="all"]')
    check("all restores", pg.locator(".album-grid li:not([hidden])").count() == total)
    pg.locator(".gallery button").first.click()
    check("mosaic opens lightbox (4 photos)", pg.text_content("#lb .lb-n") == "1 / 4")
    pg.click("#lb .x")
    broken = pg.evaluate("[...document.images].filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('loading')!=='lazy').map(i=>i.src)")
    check("no broken eager images", not broken)
    check("no JS errors", not errors)
    b.close()

sys.exit(1 if fails else 0)
