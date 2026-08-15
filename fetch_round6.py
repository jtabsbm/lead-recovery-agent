#!/usr/bin/env python3
"""Round 6: identify support.utest.com platform + mine uTest chunks; CDX API for wayback;
lablab event page probes; aihub status."""
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
           "-o", path, "-w", "%{http_code} %{url_effective}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    return r.stdout.strip(), size


print(f"Round-6 @ {datetime.datetime.now().isoformat()}")

# 1. What is support.utest.com? inspect saved HTML
sup = open(f"{OUT}/utest_support.html", encoding="utf-8", errors="replace").read()
print("support.utest.com len:", len(sup))
for pat in [r'<meta name="generator"[^>]*>', r'zendesk|freshdesk|intercom|helpscout|document360|gorgias',
            r'<script[^>]*src="([^"]+)"']:
    hits = re.findall(pat, sup, re.I)
    if pat.startswith("<script"):
        print("SCRIPTS:", hits[:12])
    else:
        m = re.search(pat, sup, re.I)
        print("PLATFORM HINT:", m.group(0)[:120] if m else "none")

# routes embedded in support portal HTML
routes = set(re.findall(r'(?:href|path)["\']?\s*[:=]\s*["\'](/[a-z0-9\-/]{3,50})["\']', sup))
print("SUPPORT ROUTES:", sorted(routes)[:30])

# 2. fetch uTest app chunk JS and mine for API/signup endpoints
code, size = fetch("utest_chunk1", "https://www.utest.com/chunk-ZWPBBEG7.js", "js", "60")
print(f"\nutest chunk1: {code} {size}B")
if os.path.exists(f"{OUT}/utest_chunk1.js") and os.path.getsize(f"{OUT}/utest_chunk1.js") > 500:
    src = open(f"{OUT}/utest_chunk1.js", encoding="utf-8", errors="replace").read()
    apis = set(re.findall(r'["\'](/api/[A-Za-z0-9_\-/\.]{2,60})["\']', src))
    auth = set(re.findall(r'["\']([^"\']*(?:signup|register|sandbox|orientation)[^"\']{0,50})["\']', src))
    print("API PATHS:", sorted(apis)[:25])
    print("AUTH/SIGNUP STRINGS:", sorted(auth)[:25])

# 3. Wayback CDX API (different endpoint than availability API)
code, size = fetch("cdx_utest_getstarted",
                   "https://web.archive.org/cdx/search/cdx?url=utest.com/testers/get-started&output=json&limit=5&from=2026", "json", "90")
print(f"\nCDX utest: {code} {size}B")
if os.path.exists(f"{OUT}/cdx_utest_getstarted.json") and size > 10:
    print(open(f"{OUT}/cdx_utest_getstarted.json").read()[:600])

code, size = fetch("cdx_lablab",
                   "https://web.archive.org/cdx/search/cdx?url=lablab.ai/event&output=json&limit=5&from=2026", "json", "90")
print(f"CDX lablab: {code} {size}B")
if os.path.exists(f"{OUT}/cdx_lablab.json") and size > 10:
    print(open(f"{OUT}/cdx_lablab.json").read()[:600])

# 4. lablab event pages via jina (different path may pass CF)
for name, url in [
    ("lablab_ibm_jina", "https://lablab.ai/event/ibm-bob-2-0"),
    ("lablab_techcrunch_jina", "https://r.jina.ai/https%3A%2F%2Flablab.ai%2Fevent"),
]:
    if name.endswith("try"):
        continue

# 5. aihub — check response headers
r = subprocess.run(["curl", "-sSI", "--max-time", "30", "-A", UA, "https://aihub.cloud.google.com/"],
                   capture_output=True, text=True, timeout=60)
print("\nAIHUB HEADERS:\n", r.stdout[:500])
print("DONE")
