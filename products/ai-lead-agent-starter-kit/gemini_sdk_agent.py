#!/usr/bin/env python3
"""CallbackOps Lead Recovery Agent — All Things Agentic edition.

Google-stack implementation:
  - google-genai SDK (official Google agent framework path) as PRIMARY engine
  - Direct REST fallback chain (gemini-3.5-flash -> 3.5-flash-lite -> 3-flash-preview)
  - Keyword fallback so the demo never dies offline

Usage:
    python3 gemini_sdk_agent.py [--leads 12] [--json out.json]

Requires: GEMINI_API_KEY in env (loaded from ../.env automatically).
The google-genai package is optional at runtime (graceful degradation),
but REQUIRED for the All Things Agentic submission path.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------- env / key
ROOT = Path(__file__).resolve().parent.parent
for env_file in (ROOT / ".env", Path(__file__).resolve().parent / ".env"):
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.strip().startswith("GEMINI_API_KEY="):
                os.environ.setdefault("GEMINI_API_KEY", line.split("=", 1)[1].strip())
                break

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# ------------------------------------------------- optional google-genai SDK
try:
    from google import genai as _genai
    from google.genai import types as _genai_types

    GENAI_SDK_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    _genai = None
    _genai_types = None
    GENAI_SDK_AVAILABLE = False

REST_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
]

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "category": {
            "type": "STRING",
            "enum": [
                "emergency",
                "scheduling",
                "quote",
                "missing_information",
                "no_fit",
                "spam",
            ],
        },
        "confidence": {"type": "NUMBER"},
        "reply": {"type": "STRING"},
        "reason": {"type": "STRING"},
    },
    "required": ["category", "confidence", "reply", "reason"],
}

SYSTEM_PROMPT = """You are the lead-recovery agent for Northside HVAC, a residential
heating and cooling company in San Diego. Classify each inbound lead and draft a reply.

Categories:
- emergency: health/safety risk or no heat/AC in extreme weather -> escalate now
- scheduling: clear intent to book service -> propose slots
- quote: price shopper -> send estimate ranges and invite on-site visit
- missing_information: need more details before acting -> ask focused questions
- no_fit: commercial work, out of area, or services we don't offer -> decline politely
- spam: solicitation/bot -> do not reply

Rules:
- Replies are from the business, under 60 words, warm and specific to the message.
- Never invent prices for specific equipment; give ranges only.
- Ask at most two clarifying questions."""


# ------------------------------------------------------------------- leads
def build_leads() -> list[dict]:
    return [
        {"id": 1, "name": "Sarah Mitchell", "message": "My furnace is making a loud banging noise and I smell gas. There's a baby in the house.", "channel": "voicemail"},
        {"id": 2, "name": "Tom Wilson", "message": "Do you service La Mesa? Our furnace won't turn on, it's cold.", "channel": "web form"},
        {"id": 3, "name": "Mike Johnson", "message": "Need a quote for a 5-ton rooftop unit for my restaurant.", "channel": "web form"},
        {"id": 4, "name": "Elena Rodriguez", "message": "AC stopped cooling yesterday, can you come Tuesday afternoon?", "channel": "missed call"},
        {"id": 5, "name": "Spam Bot", "message": "URGENT: you won a free SEO audit, click here to claim", "channel": "email"},
        {"id": 6, "name": "Karen Lee", "message": "How much for a new thermostat installed?", "channel": "web form"},
        {"id": 7, "name": "David Park", "message": "Our evaporative cooler is leaking water all over the roof.", "channel": "missed call"},
        {"id": 8, "name": "Amanda Foster", "message": "I'm selling my house and need a furnace inspection certificate.", "channel": "email"},
        {"id": 9, "name": "Robert Chen", "message": "Do you offer maintenance plans? What do they include?", "channel": "web form"},
        {"id": 10, "name": "Lisa Wang", "message": "The tenant at my rental says the heater isn't working. Property is in El Cajon.", "channel": "missed call"},
        {"id": 11, "name": "Mark Davis", "message": "Looking to add a ductless mini-split in my garage workshop.", "channel": "web form"},
        {"id": 12, "name": "Nina Patel", "message": "Your competitor quoted me $8k for a system swap, what would you charge?", "channel": "email"},
    ]


# --------------------------------------------------------------- SDK path
def classify_via_sdk(client: "genai.Client", model: str, lead: dict) -> dict:
    resp = client.chats.create(
        model=model,
        config=_genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=SCHEMA,
        ),
    )
    resp = client.models.generate_content(
        model=model,
        config=_genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=SCHEMA,
        ),
        contents=f"Lead from {lead['name']} via {lead['channel']}:\n{lead['message']}",
    )
    data = json.loads(resp.text)
    return normalize(data, model, lead)


# -------------------------------------------------------------- REST path
def classify_via_rest(model: str, lead: dict) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    body = json.dumps(
        {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"Lead from {lead['name']} via {lead['channel']}:\n{lead['message']}"
                        }
                    ],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": SCHEMA,
            },
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        out = json.load(r)
    data = json.loads(out["candidates"][0]["content"]["parts"][0]["text"])
    return normalize(data, model, lead)


# ------------------------------------------------------------- keyword path
EMERGENCY_KW = ("gas", "smoke", "fire", "carbon monoxide", "burning smell", "sparked")
def classify_keyword(lead: dict) -> dict:
    msg = lead["message"].lower()
    if any(k in msg for k in EMERGENCY_KW):
        cat, conf, reply = "emergency", 0.9, "Please call us immediately — we're escalating this to our on-call technician."
    elif "http" in msg or "seo" in msg or "won " in msg or "claim" in msg:
        cat, conf, reply = "spam", 0.8, ""
    elif "quote" in msg or "how much" in msg or "charge" in msg:
        cat, conf, reply = "quote", 0.7, "Thanks for reaching out — we'd be happy to give an estimate."
    elif "book" in msg or "tuesday" in msg or "appointment" in msg or "come" in msg:
        cat, conf, reply = "scheduling", 0.7, "We have openings this week — Tuesday afternoon works for us."
    else:
        cat, conf, reply = "missing_information", 0.6, "Thanks for your inquiry. Could you share a few more details so we can help?"
    return {
        "id": lead["id"], "name": lead["name"], "category": cat,
        "confidence": conf, "reply": reply, "reason": "keyword fallback",
        "engine": "keyword-fallback", "model": None,
    }


def normalize(data: dict, model: str, lead: dict) -> dict:
    return {
        "id": lead["id"],
        "name": lead["name"],
        "category": data.get("category", "missing_information"),
        "confidence": float(data.get("confidence", 0.5)),
        "reply": data.get("reply", ""),
        "reason": data.get("reason", ""),
        "engine": "google-genai-sdk" if GENAI_SDK_AVAILABLE else "rest",
        "model": model,
    }


# ------------------------------------------------------------------ engine
def pick_engine() -> tuple[str, object | None]:
    """Return (engine_name, sdk_client_or_None). Preference: SDK > REST > keywords."""
    if API_KEY and GENAI_SDK_AVAILABLE:
        try:
            client = _genai.Client(api_key=API_KEY)
            return "google-genai-sdk", client
        except Exception:
            pass
    if API_KEY:
        return "rest", None
    return "keyword", None


def classify_lead(lead: dict, engine: str, client, model_idx: int = 0) -> dict:
    if engine == "google-genai-sdk":
        models = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]
        for m in models[model_idx:] or models[:1]:
            try:
                return classify_via_sdk(client, m, lead)
            except Exception:
                continue
        return classify_keyword(lead)
    if engine == "rest":
        for m in REST_MODELS[model_idx:]:
            try:
                return classify_via_rest(m, lead)
            except Exception:
                continue
        return classify_keyword(lead)
    return classify_keyword(lead)


def route(category: str) -> str:
    return {
        "emergency": "ESCALATE to on-call tech (SMS + call)",
        "scheduling": "BOOK: propose 2 time slots",
        "quote": "SEND quote ranges + link",
        "missing_information": "REPLY: ask clarifying questions",
        "no_fit": "DECLINE politely + referral",
        "spam": "FILTER (no reply)",
    }.get(category, "REVIEW manually")


# -------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    engine, client = pick_engine()
    print(f"Engine: {engine}   SDK available: {GENAI_SDK_AVAILABLE}")
    leads = build_leads()
    results, t0 = [], time.time()

    for lead in leads:
        started = time.perf_counter()
        r = classify_lead(lead, engine, client)
        r["latency_ms"] = int((time.perf_counter() - started) * 1000)
        results.append(r)
        icon = {"emergency": "🚨", "scheduling": "📅", "quote": "💰",
                "missing_information": "❓", "no_fit": "🚫", "spam": "🗑️"}.get(r["category"], "•")
        print(f"{icon} {r['name']:18s} {r['category']:20s} conf={r['confidence']:.2f} [{r['latency_ms']}ms]")
        if r["reply"]:
            print(f"   ↳ {r['reply'][:100]}")

    elapsed = time.time() - t0
    confs = [r["confidence"] for r in results]
    report = {
        "business": "Northside HVAC",
        "engine": engine,
        "model": next((r["model"] for r in results if r.get("model")), None),
        "sdk_version": __import__("importlib.metadata", fromlist=["version"]).version("google-genai") if GENAI_SDK_AVAILABLE else None,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "total_leads": len(results),
        "qualified": sum(1 for r in results if r["category"] not in ("spam", "no_fit")),
        "escalated": sum(1 for r in results if r["category"] == "emergency"),
        "scheduling": sum(1 for r in results if r["category"] == "scheduling"),
        "spam_filtered": sum(1 for r in results if r["category"] == "spam"),
        "avg_confidence": round(statistics.mean(confs), 3),
        "avg_latency_ms": int(statistics.mean([r["latency_ms"] for r in results])),
        "total_elapsed_s": round(elapsed, 1),
        "leads": results,
    }

    print("\n" + "=" * 60)
    print(f"  Engine {engine} | model {report['model']} | avg conf {report['avg_confidence']}")
    print(f"  {report['qualified']} qualified, {report['escalated']} escalated, "
          f"{report['scheduling']} scheduling, {report['spam_filtered']} spam")
    print("=" * 60)

    out_path = Path(args.json) if args.json else Path(__file__).parent / "gemini-sdk-agent-output.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"💾 {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
