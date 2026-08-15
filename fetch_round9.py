#!/usr/bin/env python3
"""Round 9: check ddg_utest body; DDG alpaca + utest retry; competehub mirror pages for lablab events."""
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


def parse_ddg(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    results = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>', src)
    snips = re.findall(r'class="result__snippet"[^>]*>([\s\S]*?)</a>', src)
    out = []
    for i, (href, title) in enumerate(results[:10]):
        title = re.sub(r"<[^>]+>", "", title)
        m = re.search(r"uddg=([^&]+)", href)
        real = htmllib.unescape(urllib.parse.unquote(m.group(1))) if m else href
        snip = re.sub(r"<[^>]+>", "", snips[i]) if i < len(snips) else ""
        out.append((title.strip()[:100], real[:130], htmllib.unescape(snip.strip()[:300])))
    return out


print(f"Round-9 @ {datetime.datetime.now().isoformat()}")

# 1. what did the 202 ddg_utest_signup contain?
p = os.path.join(RAW, "ddg_utest_signup.html")
src = open(p, encoding="utf-8", errors="replace").read()
print("ddg_utest_signup len:", len(src), "| anomaly?" , "anomaly" in src.lower() or "challenge" in src.lower())

# 2. more DDG searches (with pause to avoid bot wall)
time.sleep(8)
code, size = fetch("ddg_alpaca", "https://html.duckduckgo.com/html/?q=lablab.ai+alpaca+AI+trading+agents+hackathon", mt="45")
print(f"{code} {size}B ddg_alpaca")
time.sleep(8)
code, size = fetch("ddg_utest2", "https://html.duckduckgo.com/html/?q=%22utest%22+how+to+join+tester+sandbox+profile", mt="45")
print(f"{code} {size}B ddg_utest2")

# 3. competehub mirrors of lablab events (indexed server-rendered)
code, size = fetch("competehub_ibm", "https://www.competehub.dev/en/competitions/lablabaiibm-bob-2-hackathon")
print(f"{code} {size}B competehub_ibm")

# 4. jina on the NEW lablab url structure
code, size = fetch("lablab_ibm_jina2", "https://r.jina.ai/https://lablab.ai/ai-hackathons/ibm-bob-2-hackathon", "md", "90", "text/plain")
print(f"{code} {size}B lablab_ibm_jina2")

# parse whatever DDG gave us
for n in ["ddg_alpaca", "ddg_utest2"]:
    fp = os.path.join(RAW, f"{n}.html")
    if os.path.exists(fp) and os.path.getsize(fp) > 5000:
        print(f"\n----- {n} -----")
        for t, u, s in parse_ddg(fp)[:8]:
            print(f"* {t}\n  {u}\n  {s[:220]}\n")
print("DONE")
