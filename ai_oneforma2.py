#!/usr/bin/env python3
"""Dump OneForma project-card structure: title|desc|tags|geo|rate|Apply blocks."""
import re, html

body = open("/Users/wendell/zero-cash-revenue-engine/ai_raw/oneforma_projects.html").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
t = re.sub(r"<[^>]+>", "|", t)
t = html.unescape(re.sub(r"\|+", " | ", t))
t = re.sub(r"[ \t]+", " ", t)

# Split on "Apply" — each project card ends with Apply
cards = re.split(r"\|\s*Apply\s*\|", t)
print(f"total cards: {len(cards)}")
for i, c in enumerate(cards[:-1]):
    # last 700 chars of each segment = the card content
    seg = c[-800:].strip()
    # compress pipes/spaces
    seg = re.sub(r"(\|\s*)+\|", "| ", seg)
    print(f"--- CARD {i+1} ---")
    print(seg[-600:])
    print()
