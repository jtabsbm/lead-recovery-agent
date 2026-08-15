#!/usr/bin/env python3
"""Fetch raw pages for platform signup/prize verification. Terminal-only (curl/urllib + r.jina.ai).
Persists every raw fetch under fetches_raw/ so later steps can re-parse without re-fetching."""
import os
import subprocess
import sys
import datetime

OUT = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
os.makedirs(OUT, exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# (name, url, mode) mode: 'jina' = via r.jina.ai, 'direct' = plain curl with browser UA
TARGETS = [
    # lablab.ai — Cloudflare on direct, Jina Reader known-good (skill ref 2026-08-14)
    ("lablab_event_list_jina", "https://lablab.ai/event", "jina"),
    # uTest — main tester page
    ("utest_testers_jina", "https://www.utest.com/testers", "jina"),
    ("utest_testers_direct", "https://www.utest.com/testers", "direct"),
    # Zindi — JS-only app, Jina Reader known-good
    ("zindi_competitions_jina", "https://zindi.africa/competitions", "jina"),
    # CodaLab LISN — server-rendered HTML expected
    ("codalab_competitions_direct", "https://codalab.lisn.upsaclay.fr/competitions", "direct"),
    # Google AI Hub — check what it is now
    ("aihub_jina", "https://aihub.cloud.google.com/", "jina"),
    # lablab.ai specific event pages (verify the two James wants + find signup reqs)
    ("lablab_alpaca_jina", "https://lablab.ai/event/alpaca-ai-trading-agents", "jina"),
]


def fetch(name: str, url: str, mode: str) -> tuple[int, int]:
    path = os.path.join(OUT, f"{name}.{'md' if mode == 'jina' else 'html'}")
    if mode == "jina":
        full = f"https://r.jina.ai/{url}"
        cmd = ["curl", "-sSL", "--max-time", "90", "-A", UA,
               "-H", "Accept: text/plain", "-H", "X-Return-Format: markdown",
               "-o", path, "-w", "%{http_code}", full]
    else:
        cmd = ["curl", "-sSL", "--max-time", "60", "-A", UA,
               "-H", "Accept: text/html,application/xhtml+xml",
               "-H", "Accept-Language: en-US,en;q=0.9",
               "-H", "Sec-Fetch-Mode: navigate", "-H", "Sec-Fetch-Dest: document",
               "-o", path, "-w", "%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        code = r.stdout.strip() or "000"
        size = os.path.getsize(path) if os.path.exists(path) else 0
        return int(code) if code.isdigit() else 0, size
    except Exception as e:
        print(f"  !! {name}: {e}")
        return 0, 0


print(f"Fetch run @ {datetime.datetime.now().isoformat()}")
for name, url, mode in TARGETS:
    code, size = fetch(name, url, mode)
    print(f"{code}  {size:>8}B  {name}  <- {url}")
print("DONE")
