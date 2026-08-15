#!/usr/bin/env python3
"""Cloud Run service: Lead Recovery Agent API.

Endpoints:
  GET  /            — service info
  GET  /health      — health check
  POST /classify    — {"message": "...", "business": "...", "service_area": [...]}
                      → Gemini classification JSON
  POST /demo        — runs the full 12-lead demo pipeline, returns the report

Env: GEMINI_API_KEY (required for live Gemini; falls back to keywords)
"""
import json
import os
import sys

from flask import Flask, request, jsonify

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gemini_lead_agent import GeminiClassifier, Lead, LeadStatus, GeminiLeadRecoveryAgent  # noqa: E402

app = Flask(__name__)

CLASSIFIER = GeminiClassifier()
BUSINESS = os.environ.get("BUSINESS_NAME", "Northside HVAC")
AREA = ["San Diego", "La Mesa", "Chula Vista", "Kearny Mesa", "Santee"]


@app.get("/")
def index():
    return jsonify({
        "service": "callbackops-lead-recovery-agent",
        "model": CLASSIFIER.model if CLASSIFIER.available else "keyword-fallback",
        "gemini_live": CLASSIFIER.available,
        "endpoints": ["/health", "/classify", "/demo"],
    })


@app.get("/health")
def health():
    return jsonify({"ok": True, "gemini": CLASSIFIER.available})


@app.post("/classify")
def classify():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message required"}), 400
    out = CLASSIFIER.classify(
        message,
        business_name=data.get("business", BUSINESS),
        service_area=data.get("service_area", AREA),
    )
    return jsonify(out)


@app.post("/demo")
def demo():
    agent = GeminiLeadRecoveryAgent(business_name=BUSINESS, service_area=AREA)
    leads = [
        ("Sarah Mitchell", "sarah@email.com", "My AC stopped working and it's 95 degrees inside. I have a baby and need someone today!"),
        ("John Davis", "jdavis@email.com", "How much for a new AC unit? My house is about 1800 sq ft."),
        ("Maria Garcia", "(619) 555-0142", "Missed call — no voicemail left"),
        ("Tom Wilson", "tom@email.com", "Do you service La Mesa? My furnace won't turn on."),
        ("Lisa Chen", "lchen@email.com", "Your technician was here last week and the problem came back. I'm not happy."),
        ("Bob Smith", "bob@email.com", "I just moved to the area and want to set up annual maintenance."),
        ("Spam Bot", "spam@bot.com", "Get free Viagra pills!!! Click here for casino bonus!!!"),
        ("Mike Johnson", "mike@email.com", "I need commercial refrigeration repair for my restaurant."),
        ("Jennifer Park", "(858) 555-0199", "My heater stopped working at 11pm, I have elderly parents visiting"),
        ("David Brown", "david@email.com", "Price list please"),
        ("Alex Rivera", "alex@email.com", "I have a gas leak near my furnace, I can smell it!"),
        ("Emma Wilson", "emma@email.com", "Can you install a smart thermostat? I already bought the unit."),
    ]
    for name, contact, message in leads:
        agent.ingest(name, contact, message)
    agent.process_all()
    return jsonify(agent.daily_report())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
