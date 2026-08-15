#!/usr/bin/env python3
"""Direct REST test: classify one lead with the newest Gemini model.

Uses plain urllib against generativelanguage.googleapis.com — no deprecated SDK.
Tries a list of candidate model names in order.
"""
import json
import os
import sys
import urllib.error
import urllib.request

KEY = os.environ.get("GEMINI_API_KEY")
if not KEY:
    print("set GEMINI_API_KEY"); sys.exit(1)

CANDIDATES = ["gemini-3-flash-preview", "gemini-flash-latest", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-lite-latest"]

PROMPT = """You are a lead classification agent for a home-service business (HVAC, plumbing, electrical, roofing).
Analyze the lead message and return ONLY valid JSON with:
category (one of: quote_request, scheduling, service_area_question, missing_information, complaint, urgent_escalate, no_fit, spam),
urgency (low, normal, high, emergency),
missing_info (list),
draft_reply (professional, brief),
confidence (0.0-1.0).
Never invent prices, availability, or diagnoses. URGENT: no AC, gas smell, leak, fire, smoke, extreme heat/cold, infant, elderly, medical.

Lead message: "My AC stopped working and it's 95 degrees inside. I have a baby and need someone today!"
"""

for model in CANDIDATES:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"
    body = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read().decode())
        text = d["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        print(f"MODEL OK: {model}")
        print(json.dumps(parsed, indent=2))
        sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"model {model}: HTTP {e.code} — {e.read().decode()[:120]}")
    except Exception as e:
        print(f"model {model}: {type(e).__name__}: {str(e)[:120]}")
sys.exit(1)
