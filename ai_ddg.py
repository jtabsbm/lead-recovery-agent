#!/usr/bin/env python3
"""DDG HTML fallback for Cloudflare-walled platforms. Paced to avoid rate limit."""
import re, html, subprocess, sys, time, urllib.parse

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

def ddg(query, retries=2):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    for i in range(retries + 1):
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-H", f"User-Agent: {UA}", url],
                           capture_output=True, text=True, timeout=40)
        body = r.stdout
        if "202" in body[:200] and "anomaly" in body.lower():
            time.sleep(10); continue
        if len(body) > 5000:
            return body
        time.sleep(9)
    return body

def parse(body):
    results = []
    # result links: <a rel="nofollow" class="result__a" href="...uddg=<encoded>...">
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', body, re.S):
        href, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        if "uddg=" in href:
            href = urllib.parse.unquote(re.search(r"uddg=([^&]+)", href).group(1))
        results.append((html.unescape(title).strip(), href))
    # snippets
    snips = [re.sub(r"<[^>]+>", "", s) for s in re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', body, re.S)]
    return results, [html.unescape(s).strip() for s in snips]

queries = {
    "cohere": "cohere.com data annotation careers AI trainer",
    "crowdgen": "crowdgen.com join sign up AI training projects pay",
    "e2f": "e2f.com careers AI data annotation linguist pay",
    "stellar": "stellarai.ai join AI training contributors pay per hour",
    "micro1": "micro1.com apply AI specialist hourly rate",
    "welocalize": "welocalize AI training data annotation jobs apply",
}
for name, q in queries.items():
    body = ddg(q)
    results, snips = parse(body)
    print(f"===== {name}: {q}")
    for (t, h), s in list(zip(results, snips + [""] * 10))[:5]:
        print(f"  R: {t[:90]}\n     {h[:110]}\n     S: {s[:220]}")
    time.sleep(9)
