#!/usr/bin/env python3
"""Full Mercor explore role extraction + count generalist-relevant roles."""
import re, html

body = open("/Users/wendell/zero-cash-revenue-engine/ai_raw/mercor_explore.html").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
t = re.sub(r"<[^>]+>", " ", t)
t = html.unescape(re.sub(r"\s+", " ", t))

# Roles: "Title Apply $rate / hour ... N hired this month"
roles = re.findall(r"([A-Z][A-Za-z0-9 &/,'+.\u2014\u2013-]{4,70}?)\s+Apply\s+(\$[\d,.]+\s*(?:-\s*\$[\d,.]+)?)\s*/\s*(hour|task|week)", t)
print(f"ROLES PARSED: {len(roles)}")
for r in roles[:35]:
    print(f"  {r[0].strip()[:55]:55s} | {r[1]} /{r[2]}")
# hired counts
hc = re.findall(r"\$(\d[\d,]*)\s*\n?\s*(\d[\d,]*)\s*hired (?:this month|recently)", t.replace(" hired", " hired"))
print("\nHIRED-COUNT (monthly wage $, hired):", hc[:15])
# page count
pg = re.findall(r"More pages\s+(\d+)\s+(\d+)\s+Next", t)
print("PAGES:", pg)
# signup link
sign = re.findall(r'https://[a-z.]*merc[a-z]*\.com/[a-z/-]*sign[a-z/-]*', body)
print("SIGNUP:", list(set(sign))[:5])
