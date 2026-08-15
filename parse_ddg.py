#!/usr/bin/env python3
"""Parse DDG HTML results for lablab + uTest leads."""
import re
import html as htmllib
import os

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"

for name in ["ddg_lablab_ibm", "ddg_lablab_upcoming", "ddg_utest_signup"]:
    p = os.path.join(RAW, f"{name}.html")
    src = open(p, encoding="utf-8", errors="replace").read()
    print(f"\n{'='*70}\n{name}\n{'='*70}")
    # DDG html results: <a rel="nofollow" class="result__a" href="...">title</a>
    results = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', src)
    snips = re.findall(r'class="result__snippet"[^>]*>([\s\S]*?)</a>', src)
    for i, (href, title) in enumerate(results[:10]):
        title = re.sub(r"<[^>]+>", "", title)
        # DDG wraps URLs: href="//duckduckgo.com/l/?uddg=<encoded>"
        m = re.search(r"uddg=([^&]+)", href)
        real = htmllib.unescape(__import__("urllib.parse", fromlist=["unquote"]).unquote(m.group(1))) if m else href
        snip = re.sub(r"<[^>]+>", "", snips[i]) if i < len(snips) else ""
        print(f"\n[{i+1}] {title.strip()[:100]}\n    URL: {real[:120]}\n    SNIP: {snip.strip()[:250]}")
