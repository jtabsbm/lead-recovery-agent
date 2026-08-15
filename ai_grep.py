#!/usr/bin/env python3
"""Deep-grep raw fetches for pay rates, requirements, process details."""
import re, html, sys, os

RAW = "/Users/wendell/zero-cash-revenue-engine/ai_raw"

def load(name):
    with open(os.path.join(RAW, f"{name}.html")) as f:
        return f.read()

def textify(body):
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text))

def grep_around(text, pattern, width=260, limit=6, flags=re.I):
    outs = []
    for m in re.finditer(pattern, text, flags):
        s = max(0, m.start() - width//2)
        e = min(len(text), m.end() + width)
        s = text.rfind(" ", s, m.start()) + 1 if text.rfind(" ", s, m.start()) != -1 else s
        outs.append(text[s:e].strip())
        if len(outs) >= limit: break
    return outs

for name in sys.argv[1:]:
    body = load(name)
    text = textify(body)
    print(f"===== {name} (len {len(body)}) =====")
    for pat, label in [
        (r"\$\s?\d[\d,.]*\s*(?:/|per\s+)(?:hr|hour)", "HOURLY-RATE"),
        (r"\$\s?\d[\d,.]{2,}", "DOLLAR-AMOUNT"),
        (r"resume|c\.v\.|\bcv\b", "RESUME"),
        (r"assessment|qualification|screening|interview", "ASSESSMENT"),
        (r"identity|government id|id verif|kyc|passport|driver", "ID-VERIFY"),
        (r"payout|paid (?:weekly|bi-?weekly|monthly)|paypal|airtm|stripe|wise|direct deposit", "PAYOUT"),
        (r"python|coding|programmer|software engineer|developer", "PYTHON/CODE"),
        (r"generalist|bachelor|degree|phd|master", "DEGREE"),
        (r"accepting|waitlist|closed|invite[- ]only", "STATUS"),
        (r"hour[s]? per week|hours per week|weekly hours|20 hours|40 hours", "HOURS"),
    ]:
        hits = grep_around(text, pat, limit=4)
        if hits:
            print(f"  [{label}]")
            for h in hits:
                print(f"    - {h[:300]}")
    print()
