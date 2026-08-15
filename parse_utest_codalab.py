#!/usr/bin/env python3
"""Parse uTest direct HTML + CodaLab direct HTML. Extract text content, links, competition entries."""
import re
import html as htmllib

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"


def strip_html(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def report(name: str, text: str, keywords: list[str], max_len: int = 3500):
    print(f"\n{'='*70}\n{name}  ({len(text)} chars of text)\n{'='*70}")
    low = text.lower()
    for kw in keywords:
        idxs = [m.start() for m in re.finditer(re.escape(kw.lower()), low)][:4]
        print(f"\n--- '{kw}' hits: {len([m for m in re.finditer(re.escape(kw.lower()), low)])}")
        for i in idxs:
            print("  ...", text[max(0, i-120):i+260].replace("\n", " | ")[:380])


def title_of(s: str) -> str:
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    return m.group(1)[:200] if m else "(no title)"


# ---- uTest ----
ut = open(f"{RAW}/utest_testers_direct.html", encoding="utf-8", errors="replace").read()
ut_text = strip_html(ut)
print("UTEST TITLE:", title_of(ut))
report("uTEST /testers", ut_text, [
    "sandbox", "join", "sign up", "signup", "profile", "device", "age",
    "how it works", "get paid", "payment", "paypal", "test cycle", "invite",
])

# links in uTest page
links = re.findall(r'href="([^"]+)"[^>]*>([^<]{0,80})', ut)
seen = set()
print("\n--- uTest links mentioning join/signup/tester/how:")
for href, txt in links:
    key = href[:80]
    if key in seen:
        continue
    seen.add(key)
    blob = (href + " " + txt).lower()
    if any(k in blob for k in ["join", "signup", "sign-up", "sign_up", "how", "tester", "faq", "sandbox"]):
        print(f"  {txt.strip()[:60]:60s} {href[:100]}")

# ---- CodaLab ----
co = open(f"{RAW}/codalab_competitions_direct.html", encoding="utf-8", errors="replace").read()
co_text = strip_html(co)
print("\n\nCODALAB TITLE:", title_of(co))
print("CODALAB text length:", len(co_text))

# competition rows: links to /competitions/<id>
rows = re.findall(r'<a[^>]+href="(/competitions/\d+)"[^>]*>([\s\S]*?)</a>', co)
print(f"\n--- competition links found: {len(rows)}")
for href, inner in rows[:40]:
    label = re.sub(r"<[^>]+>", " ", inner)
    label = re.sub(r"\s+", " ", htmllib.unescape(label)).strip()
    print(f"  {href:25s} {label[:90]}")
