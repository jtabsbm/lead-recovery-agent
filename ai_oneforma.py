#!/usr/bin/env python3
"""Extract OneForma open projects with pay + requirements."""
import re, html

body = open("/Users/wendell/zero-cash-revenue-engine/ai_raw/oneforma_projects.html").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
t = re.sub(r"<[^>]+>", "|", t)
t = html.unescape(re.sub(r"\|+", " | ", t))
t = re.sub(r"\s+", " ", t)

# Project cards contain title, then domain/location/hours/rate info
# Look for rate patterns with wide context
print("== RATE MENTIONS ==")
seen = set()
for m in re.finditer(r"(\$[\d.,]+(?:\s*(?:/|per\s)\s*(?:hr|hour|task|project|word))?|[\d.]+\s*(?:USD|\$))", t):
    s = t[max(0, m.start() - 160):m.end() + 80]
    key = s[-100:]
    if key not in seen:
        seen.add(key)
        print(">>", s.strip()[:260])
    if len(seen) > 30: break

print("\n== PROJECT CARD TITLES ==")
for m in re.finditer(r"\|\s*([A-Z][A-Za-z0-9 &/,'+.-]{12,70}?)\s*\|\s*(?:AI|Language|Software|Health|Law|Data|Marketing|Transcription|Testing|Speech|Search|Evaluat)", t):
    title = m.group(1).strip()
    print(f"  - {title}")
