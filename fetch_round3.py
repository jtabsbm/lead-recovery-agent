#!/usr/bin/env python3
"""Round 3: Wayback direct fetches, uTest robots/sitemap + support portal, Zindi API guesses, aihub headers."""
import os
import subprocess
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", max_time="60", extra=None):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", max_time, "-A", UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9"]
    if extra:
        cmd += extra
    cmd += ["-o", path, "-w", "%{http_code} %{url_effective}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return r.stdout.strip(), size
    except Exception as e:
        return f"ERR {e}", 0


print(f"Round-3 @ {datetime.datetime.now().isoformat()}")

jobs = [
    # Wayback direct snapshot URLs (bypass the 429'd availability API)
    ("lablab_wayback", "https://web.archive.org/web/2026/https://lablab.ai/event", "html", "90"),
    ("utest_getstarted_wayback", "https://web.archive.org/web/2026/https://www.utest.com/testers/get-started", "html", "90"),
    # uTest discovery
    ("utest_robots", "https://www.utest.com/robots.txt", "txt", "30"),
    ("utest_sitemap", "https://www.utest.com/sitemap.xml", "xml", "30"),
    ("utest_support", "https://support.utest.com/", "html", "30"),
    # Zindi API guesses
    ("zindi_api_comps", "https://zindi.africa/api/competitions", "json", "45"),
    ("zindi_ajax", "https://zindi.africa/ajax/browse/competitions", "json", "45"),
    # aihub: what does it redirect to?
    ("aihub_head", "https://aihub.cloud.google.com/", "txt", "30", ["-I"]),
]

for job in jobs:
    name, url, ext, mt = job[0], job[1], job[2], job[3]
    extra = job[4] if len(job) > 4 else None
    res, size = fetch(name, url, ext, mt, extra)
    print(f"{res}  {size:>8}B  {name}")
print("DONE")
