#!/usr/bin/env python3
"""Fetch + parse the OpenSearch hackathon official rules page for key facts."""
import urllib.request, html, re

url = "https://opensearch.org/events/agent-skills-hackathon-us-2026/official-rules/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
t = re.sub(r"<[^>]+>", " ", t)
t = html.unescape(re.sub(r"\s+", " ", t))
for kw in ["Submission Period", "deadline", "August 17", "register", "Grand Prize", "First Prize", "Second Prize", "eligib", "United States", "18 year"]:
    m = re.search(kw, t, re.I)
    if m:
        s = max(0, m.start() - 100)
        print(f"[{kw}]", t[s:m.end() + 200].strip()[:300], "\n")
