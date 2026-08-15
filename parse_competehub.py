#!/usr/bin/env python3
"""Parse CompeteHub IBM Bob 2.0 mirror page — extract prize, dates, eligibility, signup info."""
import re
import html as htmllib
import os

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
src = open(os.path.join(RAW, "competehub_ibm.html"), encoding="utf-8", errors="replace").read()


def strip_html(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


m = re.search(r"<title>(.*?)</title>", src, re.S)
print("TITLE:", m.group(1) if m else "?")
t = strip_html(src)
print("text chars:", len(t))
print("=" * 70)
print(t[:7000])
