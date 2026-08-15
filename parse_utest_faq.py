#!/usr/bin/env python3
"""Parse uTest FAQ (real content) + try lablab direct w/ full headers + Zindi direct __NEXT_DATA__."""
import re
import html as htmllib
import subprocess
import os

RAW = "/Users/wendell/zero-cash-revenue-engine/fetches_raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ---------- 1. uTest FAQ ----------
faq = open(f"{RAW}/utest_faq.html", encoding="utf-8", errors="replace").read()


def strip_html(s):
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "\n", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


t = strip_html(faq)
m = re.search(r"<title>(.*?)</title>", faq, re.S)
print("UTEST FAQ TITLE:", m.group(1) if m else "?", "| text chars:", len(t))
print(t[:6000])
