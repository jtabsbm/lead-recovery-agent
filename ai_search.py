#!/usr/bin/env python3
"""Multi-engine search fallback: Bing (robust parse) + Mojeek. For walled platforms."""
import re, html, subprocess, sys, time, urllib.parse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def fetch(url, extra=None):
    cmd = ["curl", "-sL", "--max-time", "30",
           "-H", f"User-Agent: {UA}",
           "-H", "Accept: text/html,application/xhtml+xml,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9"]
    if extra: cmd += extra
    cmd.append(url)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=40).stdout
    except Exception:
        return ""

def bing(q):
    body = fetch("https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&count=15")
    out = []
    # bing organic results: <li class="b_algo"> ... <h2><a href="URL">TITLE</a>
    for m in re.finditer(r'<li class="b_algo".*?<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a></h2>(.*?)</li>', body, re.S):
        url, title, rest = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)), m.group(3)
        cap = re.search(r'<p[^>]*>(.*?)</p>', rest, re.S)
        snip = re.sub(r"<[^>]+>", "", cap.group(1)) if cap else ""
        out.append((html.unescape(title).strip(), url, html.unescape(snip).strip()[:250]))
    return out

def mojeek(q):
    body = fetch("https://www.mojeek.com/search?q=" + urllib.parse.quote(q))
    out = []
    for m in re.finditer(r'<h2><a[^>]+href="([^"]+)"[^>]*>(.*?)</a></h2>(.*?)(?:<p class="s">|<ul)', body, re.S):
        url, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        snip = re.sub(r"<[^>]+>", " ", m.group(3))
        out.append((html.unescape(title).strip(), url, html.unescape(re.sub(r"\s+", " ", snip)).strip()[:250]))
    return out

targets = {
    "cohere": ["cohere labellers data annotation program apply"],
    "crowdgen": ["crowdgen.com join projects pay rate AI"],
    "e2f": ["e2f.com jobs apply AI data linguist"],
    "stellar": ["stellarai.ai become a contributor expert pay"],
    "micro1": ["micro1.com apply AI specialist rate"],
    "welocalize": ["welocalize careers AI data annotation rater job apply"],
}
for name, queries in targets.items():
    for q in queries:
        res = bing(q)
        if not res:
            res = mojeek(q)
        print(f"===== {name} | {q} | {len(res)} results")
        for t, u, s in res[:4]:
            print(f"  R: {t[:95]}\n     {u[:115]}\n     S: {s[:230]}")
        time.sleep(2)
