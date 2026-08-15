#!/usr/bin/env python3
"""Debug DDG response + try alternate engines (Bing, LiteDDG) for walled platforms."""
import re, html, subprocess, urllib.parse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def fetch(url, extra=None):
    cmd = ["curl", "-sL", "--max-time", "30", "-H", f"User-Agent: {UA}"]
    if extra:
        cmd += extra
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return r.stdout

# 1. Inspect the raw DDG body
body = fetch("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote("crowdgen.com join pay"))
print(f"DDG body len={len(body)}")
print("HEAD:", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))[:300])

# 2. Try lite.duckduckgo.com
body2 = fetch("https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote("crowdgen.com join sign up pay"))
print(f"\nLITE body len={len(body2)}")
print("HEAD:", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body2))[:400])

# 3. Try Bing
body3 = fetch("https://www.bing.com/search?q=" + urllib.parse.quote("crowdgen.com join sign up pay rate"))
print(f"\nBING body len={len(body3)}")
links = re.findall(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', body3)
for h, t in links[:6]:
    print(f"  B: {re.sub(r'<[^>]+>', '', t)[:80]} | {h[:100]}")
