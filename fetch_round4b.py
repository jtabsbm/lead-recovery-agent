#!/usr/bin/env python3
"""Round 4b: Zindi bundle mining + Wayback attempts for uTest/lablab content pages."""
import os
import re
import subprocess
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="60"):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", "Accept: */*", "-H", "Accept-Language: en-US,en;q=0.9",
           "-o", path, "-w", "%{http_code}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    return r.stdout.strip(), size


print(f"Round-4b @ {datetime.datetime.now().isoformat()}")
jobs = [
    ("zindi_bundle", "https://zindi-app.lon1.digitaloceanspaces.com/static-site/production/bundles/bundle.47a91ec247d35b3712a6.js", "js", "90"),
    ("utest_wayback_testers", "https://web.archive.org/web/2026/https://www.utest.com/testers/get-started", "html", "90"),
    ("lablab_wayback_event", "https://web.archive.org/web/2026/https://lablab.ai/event", "html", "90"),
]
for name, url, ext, mt in jobs:
    res, size = fetch(name, url, ext, mt)
    print(f"{res}  {size:>8}B  {name}")

bp = os.path.join(OUT, "zindi_bundle.js")
if os.path.exists(bp) and os.path.getsize(bp) > 1000:
    src = open(bp, encoding="utf-8", errors="replace").read()
    apis = set(re.findall(r'["\'](/api/[A-Za-z0-9_\-/\.]{2,60})["\']', src))
    apis |= set(re.findall(r'["\'](/ajax/[A-Za-z0-9_\-/\.]{2,60})["\']', src))
    print("\nZINDI API PATHS (%d):" % len(apis))
    for a in sorted(apis)[:50]:
        print(" ", a)
print("DONE")
