#!/usr/bin/env python3
"""Round 10: competehub lablab list; DDG-lite utest; bing utest; wayback retries; codalab date scan."""
import os
import re
import subprocess
import datetime
import time
import html as htmllib
import urllib.parse

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="60", accept="*/*"):
    path = os.path.join(RAW, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", f"Accept: {accept}", "-H", "Accept-Language: en-US,en;q=0.9",
           "-o", path, "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return r.stdout.strip(), size
    except Exception:
        return "ERR", 0


print(f"Round-10 @ {datetime.datetime.now().isoformat()}")
jobs = [
    ("competehub_list", "https://www.competehub.dev/en/competitions", "html", "60"),
    ("ddgl_utest", "https://lite.duckduckgo.com/lite/?q=utest.com+join+sandbox+orientation+new+tester", "html", "45"),
    ("bing_utest", "https://www.bing.com/search?q=utest+%22sandbox%22+new+tester+profile+join+process", "html", "45"),
    ("wayback_utest_avail", "http://archive.org/wayback/available?url=utest.com/testers/get-started&timestamp=2026", "json", "45"),
    ("wayback_lablab_avail", "http://archive.org/wayback/available?url=lablab.ai/ai-hackathons&timestamp=2026", "json", "45"),
]
for name, url, ext, mt in jobs:
    code, size = fetch(name, url, ext, mt)
    print(f"{code}  {size:>8}B  {name}")
    time.sleep(3)

# show wayback availability
for n in ["wayback_utest_avail", "wayback_lablab_avail"]:
    p = os.path.join(RAW, f"{n}.json")
    if os.path.exists(p) and os.path.getsize(p) > 5:
        print(f"\n{n}:", open(p, errors="replace").read()[:400])

# bing results quick parse
p = os.path.join(RAW, "bing_utest.html")
if os.path.exists(p) and os.path.getsize(p) > 5000:
    src = open(p, encoding="utf-8", errors="replace").read()
    res = re.findall(r'<h2><a href="([^"]+)"[^>]*>([\s\S]*?)</a></h2>', src)
    print(f"\nBING RESULTS ({len(res)}):")
    for href, title in res[:10]:
        title = re.sub(r"<[^>]+>", "", title)
        print(f"* {htmllib.unescape(title)[:90]}\n  {href[:120]}")
print("\nDONE")
