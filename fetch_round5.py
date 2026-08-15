#!/usr/bin/env python3
"""Round 5: zindi pagination meta; uTest SPA chunk mining for /api/v1; support.utest.com Zendesk probe;
lablab Jina retry."""
import json
import os
import re
import subprocess
import time
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def fetch(name, url, ext="html", mt="60", accept="*/*"):
    path = os.path.join(OUT, f"{name}.{ext}")
    cmd = ["curl", "-sSL", "--max-time", mt, "-A", UA,
           "-H", f"Accept: {accept}", "-H", "Accept-Language: en-US,en;q=0.9",
           "-o", path, "-w", "%{http_code}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    size = os.path.getsize(path) if os.path.exists(path) else 0
    return r.stdout.strip(), size


print(f"Round-5 @ {datetime.datetime.now().isoformat()}")

# 1. Zindi pagination
try:
    meta = json.load(open(f"{OUT}/zindi_api_comps2.json")).get("meta", {})
    print("ZINDI META:", json.dumps(meta)[:400])
except Exception as e:
    print("zindi meta err:", e)

# 2. uTest SPA chunks — find content/API endpoints
shell = open(f"{OUT}/utest_testers_direct.html", encoding="utf-8", errors="replace").read()
chunks = re.findall(r'href="(chunk-[^"]+\.js)"', shell)
print(f"\nUTEST CHUNKS: {chunks}")

# 3. probe uTest api v1
for probe in [
    ("utest_api_v1_root", "https://www.utest.com/api/v1/"),
    ("utest_api_v1_pages", "https://www.utest.com/api/v1/pages"),
]:
    code, size = fetch(probe[0], probe[1], "json", "30", "application/json")
    print(f"{code}  {size:>7}B  {probe[0]}")

# 4. support.utest.com — is it Zendesk/Freshdesk/Intercom? probe help center APIs
for probe in [
    ("utest_zendesk_articles", "https://support.utest.com/api/v2/help_center/articles.json?per_page=5", "json"),
    ("utest_zendesk_sections", "https://support.utest.com/api/v2/help_center/en-us/articles.json", "json"),
]:
    code, size = fetch(probe[0], probe[1], probe[2], "45", "application/json")
    print(f"{code}  {size:>7}B  {probe[0]}")

# 5. lablab Jina retries (after pause)
time.sleep(20)
code, size = fetch("lablab_event_jina_try3", "https://lablab.ai/event", "md", "90", "text/plain")
print(f"{code}  {size:>7}B  lablab_event_jina_try3")
print("DONE")
