#!/usr/bin/env python3
"""Round 8: lablab subdomains/RSS + alt markdown proxies + DDG HTML search + applause.com."""
import os
import re
import subprocess
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="60", accept="*/*"):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", f"Accept: {accept}", "-H", "Accept-Language: en-US,en;q=0.9",
           "-o", path, "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return r.stdout.strip(), size
    except Exception:
        return "ERR", 0


print(f"Round-8 @ {datetime.datetime.now().isoformat()}")
jobs = [
    # lablab variants
    ("lablab_www", "https://www.lablab.ai/event", "html"),
    ("lablab_api_sub", "https://api.lablab.ai/", "html"),
    ("lablab_rss", "https://lablab.ai/rss", "xml"),
    ("lablab_feed", "https://lablab.ai/feed.xml", "xml"),
    # alt markdown proxies
    ("lablab_mdhr", "https://md.dhr.wtf/?url=https%3A%2F%2Flablab.ai%2Fevent", "md", "90", "text/plain"),
    ("lablab_microlink", "https://api.microlink.io/?url=https%3A%2F%2Flablab.ai%2Fevent&meta=false", "json", "90", "application/json"),
    # applause (owns uTest)
    ("applause_home", "https://www.applause.com/", "html"),
    # DDG html search (server-rendered)
    ("ddg_lablab_ibm", "https://html.duckduckgo.com/html/?q=lablab.ai+IBM+Bob+2.0+hackathon", "html", "45"),
    ("ddg_lablab_upcoming", "https://html.duckduckgo.com/html/?q=lablab.ai+upcoming+hackathon+September+2026", "html", "45"),
    ("ddg_utest_signup", "https://html.duckduckgo.com/html/?q=utest+signup+sandbox+test+new+testers", "html", "45"),
]
for job in jobs:
    name, url, ext = job[0], job[1], job[2]
    mt = job[3] if len(job) > 3 else "60"
    acc = job[4] if len(job) > 4 else "*/*"
    code, size = fetch(name, url, ext, mt, acc)
    print(f"{code}  {size:>8}B  {name}")
print("DONE")
