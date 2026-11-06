#!/usr/bin/env python3
"""List the Mirai-an photo folder on Google Drive and fetch resized copies.

Why thumbnails instead of originals: the recent photos are ~100MB PNGs each and
the local disk is nearly full. Drive serves a resized rendition via
thumbnailLink (=sNNNN), which is all a web page needs.

Usage:
  fetch_drive.py list  <out.json>                 # recursive inventory
  fetch_drive.py fetch <inventory.json> <dir> <size>  # download =s<size> renditions
"""
import json, os, re, sys, time
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

ROOT = "1eSAIicK6Yal-XAItXnDmEc8I2E-lPJzb"
TOKEN = os.path.expanduser("~/.config/google-workspace-mcp/esse.miratuku@gmail.com.json")


def creds():
    d = json.load(open(TOKEN))
    c = Credentials(d["token"], refresh_token=d["refresh_token"], token_uri=d["token_uri"],
                    client_id=d["client_id"], client_secret=d["client_secret"], scopes=d["scopes"])
    if not c.valid:
        c.refresh(Request())
    return c


def api(c, params):
    r = requests.get("https://www.googleapis.com/drive/v3/files",
                     headers={"Authorization": f"Bearer {c.token}"}, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def walk(c, folder, path):
    out, token = [], None
    while True:
        p = {"q": f"'{folder}' in parents and trashed=false", "pageSize": 1000,
             "fields": "nextPageToken,files(id,name,mimeType,size,thumbnailLink,imageMediaMetadata(width,height,time),createdTime)",
             "supportsAllDrives": True, "includeItemsFromAllDrives": True}
        if token:
            p["pageToken"] = token
        d = api(c, p)
        for f in d["files"]:
            if f["mimeType"] == "application/vnd.google-apps.folder":
                out += walk(c, f["id"], path + [f["name"]])
            elif f["mimeType"].startswith("image/"):
                f["path"] = "/".join(path)
                out.append(f)
        token = d.get("nextPageToken")
        if not token:
            return out


def fetch_original(c, f, dst, size):
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    tmp = dst + ".orig"
    try:
        with requests.get(f"https://www.googleapis.com/drive/v3/files/{f['id']}",
                          params={"alt": "media", "supportsAllDrives": True},
                          headers={"Authorization": f"Bearer {c.token}"}, stream=True, timeout=600) as r:
            if r.status_code != 200:
                return False
            with open(tmp, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        im = Image.open(tmp)
        im.thumbnail((size, size), Image.LANCZOS)
        im.convert("RGB").save(dst, "JPEG", quality=90)
        return True
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    c = creds()
    if sys.argv[1] == "list":
        items = walk(c, ROOT, [])
        json.dump(items, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
        print(len(items), "images")
    elif sys.argv[1] == "fetch":
        items = json.load(open(sys.argv[2]))
        outdir, size = sys.argv[3], sys.argv[4]
        os.makedirs(outdir, exist_ok=True)
        ok = fail = 0
        for f in items:
            dst = os.path.join(outdir, f["id"] + ".jpg")
            if os.path.exists(dst) and os.path.getsize(dst) > 1000:
                ok += 1
                continue
            link = f.get("thumbnailLink")
            if not link:
                # Very large originals (the ~100MB PNGs) get no Drive thumbnail.
                # Stream the original to a temp file, shrink it, then delete it
                # straight away so the nearly-full disk never holds more than one.
                if fetch_original(c, f, dst, int(size)):
                    ok += 1
                else:
                    print("fail original:", f["path"], f["name"]); fail += 1
                continue
            url = re.sub(r"=s\d+$", f"=s{size}", link)
            for attempt in range(3):
                r = requests.get(url, headers={"Authorization": f"Bearer {c.token}"}, timeout=120)
                if r.status_code == 200 and r.content[:2] in (b"\xff\xd8", b"\x89P", b"RI"):
                    open(dst, "wb").write(r.content); ok += 1; break
                time.sleep(2)
            else:
                print("fail", r.status_code, f["path"], f["name"]); fail += 1
        print("ok", ok, "fail", fail)


if __name__ == "__main__":
    main()
