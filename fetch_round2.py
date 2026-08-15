#!/usr/bin/env python3
"""Round 2: retry blocked targets with alternates — uTest subpages direct, Jina retries,
lablab sitemap/API guesses, archive.org fallbacks."""
import os
import subprocess
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
os.makedirs(OUT, exist_ok=True)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

TARGETS = [
    # uTest subpages (direct curl worked for the shell; try real content pages)
    ("utest_get_started", "https://www.utest.com/testers/get-started", "direct"),
    ("utest_faq", "https://www.utest.com/faq", "direct"),
    ("utest_signup", "https://www.utest.com/testers/signup", "direct"),
    # lablab.ai retries via jina
    ("lablab_event_jina_try2", "https://lablab.ai/event", "jina"),
    ("lablab_sitemap_jina", "https://lablab.ai/sitemap.xml", "jina"),
    ("lablab_api_events", "https://lablab.ai/api/events", "direct"),
    # Zindi retry
    ("zindi_jina_try2", "https://zindi.africa/competitions", "jina"),
    # aihub direct (see what it serves plain)
    ("aihub_direct", "https://aihub.cloud.google.com/", "direct"),
    # archive fallbacks
    ("lablab_event_wayback", "http://archive.org/wayback/available?url=lablab.ai/event", "direct"),
    ("utest_testers_wayback", "http://archive.org/wayback/available?url=utest.com/testers", "direct"),
]


def fetch(name, url, mode):
    ext = "md" if mode == "jina" else ("json" if "wayback/available" in url else "html")
    path = os.path.join(OUT, f"{name}.{ext}")
    if mode == "jina":
        full = f"https://r.jina.ai/{url}"
        cmd = ["curl", "-sSL", "--max-time", "90", "-A", UA, "-H", "Accept: text/plain",
               "-o", path, "-w", "%{http_code}", full]
    else:
        cmd = ["curl", "-sSL", "--max-time", "60", "-A", UA,
               "-H", "Accept: text/html,application/xhtml+xml,*/*",
               "-H", "Accept-Language: en-US,en;q=0.9",
               "-o", path, "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        code = r.stdout.strip() or "000"
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return code, size
    except Exception as e:
        return f"ERR:{e}", 0


print(f"Round-2 fetch @ {datetime.datetime.now().isoformat()}")
for name, url, mode in TARGETS:
    code, size = fetch(name, url, mode)
    print(f"{code}  {size:>8}B  {name}  <- {url}")
print("DONE")
