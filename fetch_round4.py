#!/usr/bin/env python3
"""Round 4: uTest real pages from robots.txt allowlist + Zindi bundle mining."""
import os
import subprocess
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="60"):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9",
           "-o", path, "-w", "%{http_code}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    return r.stdout.strip(), size


print(f"Round-4 @ {datetime.datetime.now().isoformat()}")
jobs = [
    # uTest robots-allowed pages
    ("utest_why", "https://www.utest.com/why-utest"),
    ("utest_about", "https://www.utest.com/about-us"),
    ("utest_projects", "https://www.utest.com/projects"),
    ("utest_signup_page", "https://www.utest.com/signup"),
    ("utest_guidelines", "https://www.utest.com/utest-guidelines"),
    ("utest_terms", "https://www.utest.com/terms-and-conditions"),
    # Zindi site JS bundle — mine for API endpoints
    ("zindi_bundle", "https://zindi-app.lon1.digitaloceanspaces.com/static-site/production/bundles/bundle.47a91ec247d35b3712a6.js", "js", "90"),
]
for name, url in jobs:
    res, size = fetch(name, url)
    print(f"{res}  {size:>8}B  {name}")

# mine zindi bundle for API paths
bp = os.path.join(OUT, "zindi_bundle.js")
if os.path.exists(bp) and os.path.getsize(bp) > 1000:
    src = open(bp, encoding="utf-8", errors="replace").read()
    import re
    apis = set(re.findall(r'["\'](/api/[A-Za-z0-9_\-/\.]{2,60})["\']', src))
    apis |= set(re.findall(r'["\'](/ajax/[A-Za-z0-9_\-/\.]{2,60})["\']', src))
    hosts = set(re.findall(r'https?://[a-z0-9\-\.]*zindi[a-z0-9\-\.]*/[A-Za-z0-9_\-/\.]{0,50}', src))
    print("\nZINDI API PATHS:")
    for a in sorted(apis)[:40]:
        print(" ", a)
    print("ZINDI HOSTS:")
    for h in sorted(hosts)[:15]:
        print(" ", h)
print("DONE")
