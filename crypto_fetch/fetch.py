#!/usr/bin/env python3
"""Fetch research URLs via r.jina.ai concurrently, save to crypto_fetch/."""
import sys, os, concurrent.futures, urllib.request, ssl

URLS = {
    "binance_academy_le": "https://r.jina.ai/https://www.binance.com/en/academy/learn-and-earn",
    "testnet_roundup": "https://r.jina.ai/https://tradersunion.com/interesting-articles/testnet/best-testnets-and-airdrops/",
    "superteam_api_check": "https://earn.superteam.fun/api/listings/?filter=bounty&take=1",
}

CTX = ssl.create_default_context()

def fetch(name_url):
    name, url = name_url
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".md")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        with urllib.request.urlopen(req, timeout=75, context=CTX) as r:
            data = r.read()
        with open(out, "wb") as f:
            f.write(data)
        return name, len(data), "ok"
    except Exception as e:
        return name, 0, str(e)[:120]

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    targets = {k: v for k, v in URLS.items() if not only or k in only}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for name, n, status in ex.map(fetch, targets.items()):
            print(f"{name:28s} {n:8d}B  {status}")
