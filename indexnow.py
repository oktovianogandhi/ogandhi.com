#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver; Bing feeds ChatGPT search and Copilot) that pages changed.

Run after each publish, once GitHub Pages serves the new version:
    python3 indexnow.py                 # every URL in docs/sitemap.xml
    python3 indexnow.py /media/ /about/ # only these paths
The key file static/<key>.txt is copied to the site root by build.py; keep it there.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
HOST = "ogandhi.com"
KEY = next(p.stem for p in (ROOT / "static").glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem))

if len(sys.argv) > 1:
    urls = [f"https://{HOST}{p if p.startswith('/') else '/' + p}" for p in sys.argv[1:]]
else:
    urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8"))

body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.status, f"submitted {len(urls)} URLs")
