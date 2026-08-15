#!/usr/bin/env python3
"""List available Gemini models for this API key (names only)."""
import os
import sys
import json
import urllib.request

key = os.environ.get("GEMINI_API_KEY") or sys.argv[1]
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}&pageSize=50"
req = urllib.request.Request(url)
d = json.load(urllib.request.urlopen(req, timeout=20))
for m in d.get("models", []):
    name = m.get("name", "").replace("models/", "")
    methods = ",".join(x.split("/")[-1] for x in m.get("supportedGenerationMethods", []))
    if "generateContent" in methods:
        print(name)
