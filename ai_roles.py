#!/usr/bin/env python3
"""Extract role listings with rates from saved raw fetches."""
import re, html, os, sys

RAW = "/Users/wendell/zero-cash-revenue-engine/ai_raw"

def textify(body):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(re.sub(r"\s+", " ", t))

# Mercor homepage: "Role Title $X-$Y/hr ... N hired recently Apply"
name = sys.argv[1]
body = open(os.path.join(RAW, f"{name}.html")).read()
text = textify(body)

if name == "mercor_home":
    # find segments: Title $range/hr ... hired recently Apply
    roles = re.findall(r"([A-Z][^$]{3,60}?)\s+(\$\d[\d,]*)(?:\s*[-–]\s*(\$[\d,]+))?\s*/\s*hr", text)
    print("MERCOR ROLES (title, rate):")
    for r in roles[:40]:
        print(f"  {r[0].strip()[-55:]} | {r[1]}{'-' + r[2] if r[2] else ''}/hr")
elif name == "alignerr_jobs":
    roles = re.findall(r"([A-Z][^$]{3,70}?)\s+\$(\d[\d,]*)\s*[-–]\s*\$(\d[\d,]*)\s*/\s*hr\s*(Remote|Hybrid|Onsite)?", text)
    print("ALIGNERR ROLES:")
    for r in roles[:50]:
        print(f"  {r[0].strip()[-60:]} | ${r[1]}-${r[2]}/hr {r[3]}")
elif name == "turing_jobs" or name == "turing":
    # Turing lists weekly amounts e.g. "Priority $200 Role Name description"
    roles = re.findall(r"(?:Priority\s+)?\$(\d[\d,]*)\s+([A-Z][^$]{5,70}?)(?=\s+(?:Priority\s+\$|Evaluate|Review|Rate|Improve|Audit|Validate|Assess|Write|Create|Test|Annotate|Label))", text)
    print("TURING ROLES (weekly $, title):")
    for r in roles[:40]:
        print(f"  ${r[0]}/wk | {r[1].strip()[:60]}")
    # also any /hr mentions
    hrs = re.findall(r"(\$\d[\d,]*(?:\s*[-–]\s*\$?\d[\d,]*)?)\s*/\s*(?:hr|hour)[^.]{0,120}", text)
    for h in hrs[:10]:
        print(f"  HOURLY: {h.strip()[:150]}")
