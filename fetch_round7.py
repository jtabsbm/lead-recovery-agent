#!/usr/bin/env python3
"""Round 7: lablab.ai via public CORS proxies + alternate readers; ServiceNow KB probes on support.utest.com."""
import os
import subprocess
import datetime
import urllib.parse

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="75", accept="text/html,*/*", hdrs=None):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", f"Accept: {accept}", "-H", "Accept-Language: en-US,en;q=0.9"]
    for h in (hdrs or []):
        cmd += ["-H", h]
    cmd += ["-o", path, "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return r.stdout.strip(), size
    except Exception as e:
        return f"ERR", 0


print(f"Round-7 @ {datetime.datetime.now().isoformat()}")
target = "https://lablab.ai/event"
enc = urllib.parse.quote(target, safe="")

proxies = [
    ("lablab_allorigins", f"https://api.allorigins.win/raw?url={enc}"),
    ("lablab_corsproxy", f"https://corsproxy.io/?url={enc}"),
    ("lablab_codetabs", f"https://api.codetabs.com/v1/proxy?quest={enc}"),
]
for name, url in proxies:
    code, size = fetch(name, url)
    print(f"{code}  {size:>8}B  {name}")

# jina with browser engine + long timeout headers
code, size = fetch("lablab_jina_engine", f"https://r.jina.ai/{target}", "md", "110",
                   hdrs=["X-Engine: browser", "X-Timeout: 60", "X-No-Cache: true"])
print(f"{code}  {size:>8}B  lablab_jina_engine")

# ServiceNow KB probes
sn = [
    ("utest_sn_kbsearch", "https://support.utest.com/api/now/kb/search?q=sandbox", "application/json"),
    ("utest_sn_kb_table", "https://support.utest.com/api/now/table/kb_knowledge?sysparm_limit=3", "application/json"),
    ("utest_sn_spsearch", "https://support.utest.com/api/sn_km/knowledge_base/search?query=sandbox", "application/json"),
]
for name, url, acc in sn:
    code, size = fetch(name, url, "json", "45", acc)
    print(f"{code}  {size:>8}B  {name}")
    p = os.path.join(OUT, f"{name}.json")
    if os.path.exists(p) and os.path.getsize(p) < 3000 and os.path.getsize(p) > 0:
        print("   body:", open(p, errors="replace").read()[:200])
print("DONE")
