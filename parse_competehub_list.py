#!/usr/bin/env python3
"""Round 10b: parse competehub list for lablab events + parse bing utest results (different selectors)."""
import os
import re
import html as htmllib

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"


def strip_html(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


# ---- CompeteHub list ----
src = open(os.path.join(RAW, "competehub_list.html"), encoding="utf-8", errors="replace").read()
# links to competition detail pages
links = re.findall(r'<a[^>]+href="(/en/competitions/[^"]+)"[^>]*>([\s\S]*?)</a>', src)
print(f"COMPETEHUB competition links: {len(links)}")
lablab_events = []
for href, inner in links:
    label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", inner)).strip()
    if label:
        lablab_events.append((href, label[:110]))
seen = set()
for href, label in lablab_events:
    if href in seen:
        continue
    seen.add(href)
    print(f"  {href[16:70]:55s} {label}")
