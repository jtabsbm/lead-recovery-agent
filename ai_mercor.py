#!/usr/bin/env python3
"""Extract Mercor doc details: signup URL, interview flow, payment timing."""
import re, html

for name in ["mercor_earnings", "mercor_createacct", "mercor_interview"]:
    try:
        body = open(f"/Users/wendell/zero-cash-revenue-engine/ai_raw/{name}.html").read()
    except FileNotFoundError:
        continue
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(re.sub(r"\s+", " ", t))
    print(f"===== {name} =====")
    # signup URL
    for m in re.finditer(r"(?:mercor\.com/[a-z/-]+|app\.mercor\.com[a-z/-]*)", body):
        u = m.group(0)
        if "docs" not in u and "cdn" not in u:
            print("  URL:", u)
    for pat in [r"[^.]*interview[^.]*\.", r"[^.]*payment[^.]*\.", r"[^.]*payout[^.]*\.",
                r"[^.]*resume[^.]*\.", r"[^.]*/hr[^.]*\.", r"[^.]*weekly[^.]*\."]:
        hits = [m.group(0).strip()[:280] for m in re.finditer(pat, t, re.I)]
        for h in hits[:3]:
            print(f"  > {h}")
    print()
