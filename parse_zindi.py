#!/usr/bin/env python3
"""Parse Zindi v1 API competitions JSON into a clean table."""
import json

d = json.load(open("/Users/wendell/zero-cash-revenue-engine/fetches_raw/zindi_api_comps2.json"))
comps = d.get("data", d if isinstance(d, list) else [])
print(f"Total entries returned: {len(comps)}\n")
print(f"{'TITLE':58s} {'KIND':10s} {'REWARD':16s} {'ENDS':17s} {'ENTRANTS':>8s}  {'FLAGS'}")
print("-" * 130)
for c in comps:
    flags = []
    if c.get("is_beginner_friendly"):
        flags.append("beginner")
    if c.get("is_access_restricted"):
        flags.append("RESTRICTED")
    if c.get("secret_code_required"):
        flags.append("CODE-REQ")
    if c.get("reward_type") != "prize":
        flags.append(f"type={c.get('reward_type')}")
    print(f"{c.get('title','?')[:57]:58s} {c.get('kind','?'):10s} {str(c.get('reward','?'))[:16]:16s} "
          f"{str(c.get('end_time','?'))[:10]:17s} {c.get('participations_count',0):>8d}  {','.join(flags)}")
print("\nmeta keys:", list(d.keys()) if isinstance(d, dict) else "(list)")
