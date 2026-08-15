#!/usr/bin/env python3
"""
Lead Recovery Agent — Gemini-Powered Edition
Multi-hackathon submission: All Things Agentic, Agents for Humans, Agentic Cinema

Uses Google Gemini API for natural-language lead classification and response generation.
Replaces the keyword-based prototype with true NL understanding.

Requirements:
    pip install google-generativeai

Usage:
    # Set your Gemini API key (free tier available)
    export GEMINI_API_KEY="your-key-here"
    
    # Or use the GCP service account already on this machine
    # The $1,000 GenAI App Builder credit covers API costs

    python gemini_lead_agent.py

Free Gemini API key: https://aistudio.google.com/app/apikey
"""

import os
import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum

# ─── Gemini Integration ────────────────────────────────────────────────────────
#
# Uses the Gemini REST API directly (no SDK dependency). The legacy
# google-generativeai SDK is deprecated and older model names are retired;
# direct REST with a current model is the durable path.

GEMINI_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-flash-latest"]


class GeminiClassifier:
    """Classifies leads with Gemini via the REST API; keyword fallback on any failure."""

    SYSTEM_PROMPT = """You are a lead classification agent for a home-service business (HVAC, plumbing, electrical, roofing).

    Your job is to analyze incoming lead messages and return a JSON object with:
    - category: one of [quote_request, scheduling, service_area_question, missing_information, complaint, urgent_escalate, no_fit, spam]
    - urgency: one of [low, normal, high, emergency]
    - missing_info: list of specific information needed from the customer
    - draft_reply: a professional response using the business's approved tone
    - confidence: 0.0 to 1.0

    Rules:
    - NEVER invent prices, availability, or technical diagnoses
    - URGENT keywords: no AC, gas smell, leak, fire, smoke, extreme heat/cold, infant, elderly, medical equipment
    - COMPLAINT keywords: unhappy, not satisfied, problem came back, terrible, angry
    - SPAM: viagra, casino, crypto, free money, lottery, promotional links
    - Always be professional and brief in the draft reply
    - If the message is too vague, classify as missing_information
    - If outside service area or scope, classify as no_fit

    Return ONLY valid JSON, no markdown formatting.
    """

    def __init__(self, api_key: str = None):
        self.model = None
        self.available = False
        self._key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self._key:
            print("Gemini: no API key set (GEMINI_API_KEY) — keyword fallback active")
            return
        if self._probe():
            self.available = True
            print(f"✓ Gemini connected via REST ({self.model})")

    def _call(self, prompt: str, timeout: int = 60):
        import urllib.request
        import urllib.error
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{self.model}:generateContent?key={self._key}")
        body = {
            "system_instruction": {"parts": [{"text": self.SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode())
        return json.loads(d["candidates"][0]["content"]["parts"][0]["text"])

    def _probe(self) -> bool:
        """Find a working model from the candidate list with one cheap call."""
        import urllib.request
        import urllib.error
        for m in GEMINI_MODELS:
            self.model = m
            try:
                out = self._call('Lead message: "hello are you open today?"', timeout=60)
                if "category" in out:
                    return True
            except Exception:
                continue
        return False

    def classify(self, message: str, business_name: str = "Northside HVAC",
                 service_area: list = None) -> dict:
        """Classify a lead message using Gemini NL understanding."""
        if not self.available:
            return self._fallback_classify(message)

        context = (f"Business: {business_name}\n"
                   f"Service area: {', '.join(service_area or ['San Diego'])}\n\n"
                   f'Lead message: "{message}"')
        try:
            result = self._call(context)
            result.setdefault("category", "missing_information")
            result.setdefault("urgency", "normal")
            result.setdefault("missing_info", [])
            result.setdefault("draft_reply", "")
            result.setdefault("confidence", 0.7)
            result["model"] = self.model
            return result
        except Exception as e:
            print(f"Gemini error: {str(e)[:120]} — falling back to keywords")
            return self._fallback_classify(message)
    
    def _fallback_classify(self, message: str) -> dict:
        """Keyword-based fallback when Gemini is not available."""
        msg = message.lower()
        
        emergency_kw = ["no ac", "gas smell", "carbon monoxide", "leak", "fire", "smoke", 
                       "95 degrees", "freezing", "infant", "elderly", "baby", "emergency"]
        complaint_kw = ["unhappy", "complaint", "problem came back", "not satisfied", "terrible", "angry"]
        spam_kw = ["viagra", "casino", "crypto", "click here", "free money", "lottery"]
        quote_kw = ["quote", "estimate", "price", "how much", "cost", "pricing"]
        schedule_kw = ["appointment", "schedule", "book", "come out", "available", "when can"]
        
        if any(w in msg for w in emergency_kw):
            return {"category": "urgent_escalate", "urgency": "emergency", 
                    "missing_info": ["address"], "draft_reply": "This sounds urgent. I've flagged this for immediate attention. Please expect a call within 30 minutes.", 
                    "confidence": 0.9, "model": "keyword-fallback"}
        if any(w in msg for w in complaint_kw):
            return {"category": "complaint", "urgency": "high", 
                    "missing_info": ["work order number"], "draft_reply": "I'm sorry to hear this. I've flagged your message for the owner directly.", 
                    "confidence": 0.85, "model": "keyword-fallback"}
        if any(w in msg for w in spam_kw):
            return {"category": "spam", "urgency": "normal", "missing_info": [], 
                    "draft_reply": "(No reply — flagged as spam)", "confidence": 0.95, "model": "keyword-fallback"}
        if any(w in msg for w in quote_kw):
            return {"category": "quote_request", "urgency": "normal", 
                    "missing_info": ["address", "system details"], "draft_reply": "Thanks for reaching out! To give you an accurate quote, we'd need a few more details.", 
                    "confidence": 0.8, "model": "keyword-fallback"}
        if any(w in msg for w in schedule_kw):
            return {"category": "scheduling", "urgency": "normal", "missing_info": [], 
                    "draft_reply": "Thanks for contacting us! What day and time works best for you?", 
                    "confidence": 0.8, "model": "keyword-fallback"}
        
        return {"category": "missing_information", "urgency": "normal", 
                "missing_info": ["service type", "address", "preferred time"], 
                "draft_reply": "Thanks for your inquiry. Could you provide a few more details so we can help you?", 
                "confidence": 0.6, "model": "keyword-fallback"}


# ─── Data Models ───────────────────────────────────────────────────────────────

class LeadStatus(Enum):
    NEW = "new"
    RESPONDED = "responded"
    BOOKED = "booked"
    ESCALATED = "escalated"
    CLOSED = "closed"
    SPAM = "spam"

@dataclass
class Lead:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""
    caller_name: str = ""
    contact: str = ""
    message: str = ""
    received_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = LeadStatus.NEW.value
    category: str = ""
    urgency: str = "normal"
    missing_info: list = field(default_factory=list)
    draft_reply: str = ""
    confidence: float = 0.0
    model_used: str = ""
    tokens_used: int = 0
    suggested_action: str = ""
    response_time_ms: int = 0


# ─── Agent Core ─────────────────────────────────────────────────────────────────

class GeminiLeadRecoveryAgent:
    """
    Full Gemini-powered lead recovery agent.
    
    Multi-hackathon submission:
    - All Things Agentic (Gemini + Google Cloud)
    - Agents for Humans (can adapt to Strands Agents SDK)
    - Agentic Cinema (can adapt for media production workflows)
    """
    
    def __init__(self, business_name: str = "Northside HVAC", 
                 service_area: list = None, gemini_api_key: str = None):
        self.business_name = business_name
        self.service_area = service_area or ["San Diego", "La Mesa", "Chula Vista"]
        self.classifier = GeminiClassifier(gemini_api_key)
        self.leads: list[Lead] = []
        self.stats = {
            "total_leads": 0,
            "qualified": 0,
            "booked": 0,
            "escalated": 0,
            "spam_filtered": 0,
            "avg_confidence": 0.0,
            "total_tokens": 0,
            "avg_response_ms": 0,
        }
    
    def ingest(self, name: str, contact: str, message: str, source: str = "web_form") -> Lead:
        """Ingest a new lead from any source."""
        lead = Lead(
            source=source,
            caller_name=name,
            contact=contact,
            message=message,
        )
        self.leads.append(lead)
        self.stats["total_leads"] += 1
        return lead
    
    def process(self, lead: Lead) -> Lead:
        """Run the full Gemini-powered pipeline on a single lead."""
        start_time = time.time()
        
        # Step 1: Classify with Gemini
        result = self.classifier.classify(
            lead.message, 
            self.business_name, 
            self.service_area
        )
        
        lead.category = result.get("category", "missing_information")
        lead.urgency = result.get("urgency", "normal")
        lead.missing_info = result.get("missing_info", [])
        lead.draft_reply = result.get("draft_reply", "")
        lead.confidence = result.get("confidence", 0.0)
        lead.model_used = result.get("model", "unknown")
        lead.tokens_used = result.get("tokens_used", 0)
        
        # Step 2: Route based on classification
        if lead.category in ("urgent_escalate", "complaint"):
            lead.status = LeadStatus.ESCALATED.value
            lead.suggested_action = "⚠️ ESCALATE: Immediate human call required"
            self.stats["escalated"] += 1
        elif lead.category == "spam":
            lead.status = LeadStatus.SPAM.value
            lead.suggested_action = "DISCARD: Spam detected"
            self.stats["spam_filtered"] += 1
        elif lead.category == "no_fit":
            lead.status = LeadStatus.CLOSED.value
            lead.suggested_action = "CLOSED: Outside scope/area"
        elif lead.category in ("scheduling", "service_area_question"):
            lead.status = LeadStatus.BOOKED.value
            lead.suggested_action = "✓ BOOKED: Next available appointment"
            self.stats["booked"] += 1
        else:
            lead.status = LeadStatus.RESPONDED.value
            lead.suggested_action = "✓ RESPONDED: Draft ready for owner review"
            self.stats["qualified"] += 1
        
        # Track performance
        lead.response_time_ms = int((time.time() - start_time) * 1000)
        self.stats["total_tokens"] += lead.tokens_used
        confidences = [l.confidence for l in self.leads if l.confidence > 0]
        self.stats["avg_confidence"] = sum(confidences) / len(confidences) if confidences else 0
        response_times = [l.response_time_ms for l in self.leads if l.response_time_ms > 0]
        self.stats["avg_response_ms"] = int(sum(response_times) / len(response_times)) if response_times else 0
        
        return lead
    
    def process_all(self):
        """Process all unprocessed leads."""
        for lead in self.leads:
            if lead.status == LeadStatus.NEW.value:
                self.process(lead)
    
    def daily_report(self) -> dict:
        """Generate a comprehensive daily report."""
        by_category = {}
        by_status = {}
        by_urgency = {}
        for l in self.leads:
            by_category[l.category] = by_category.get(l.category, 0) + 1
            by_status[l.status] = by_status.get(l.status, 0) + 1
            by_urgency[l.urgency] = by_urgency.get(l.urgency, 0) + 1
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "business": self.business_name,
            "model": (self.classifier.model or "keyword-fallback") if self.classifier.available else "Keyword Fallback",
            "summary": {
                "total_leads": len(self.leads),
                "by_category": by_category,
                "by_status": by_status,
                "by_urgency": by_urgency,
            },
            "metrics": {
                "qualified_conversations": self.stats["qualified"],
                "appointments_booked": self.stats["booked"],
                "escalations": self.stats["escalated"],
                "spam_filtered": self.stats["spam_filtered"],
                "avg_confidence": round(self.stats["avg_confidence"], 3),
                "total_tokens_used": self.stats["total_tokens"],
                "avg_response_ms": self.stats["avg_response_ms"],
            },
            "leads": [asdict(l) for l in self.leads],
        }


# ─── Demo ──────────────────────────────────────────────────────────────────────

def run_demo():
    """Run a full demo with synthetic leads."""
    print("=" * 70)
    print("  Lead Recovery Agent — Gemini-Powered Edition")
    print("  Multi-Hackathon Submission")
    print("=" * 70)
    
    # Initialize agent
    agent = GeminiLeadRecoveryAgent(
        business_name="Northside HVAC",
        service_area=["San Diego", "La Mesa", "Chula Vista", "Kearny Mesa", "Santee"],
    )
    
    # Synthetic leads covering all categories
    test_leads = [
        ("Sarah Mitchell", "sarah@email.com", "My AC stopped working and it's 95 degrees inside. I have a baby and need someone today!", "web_form"),
        ("John Davis", "jdavis@email.com", "How much for a new AC unit? My house is about 1800 sq ft.", "web_form"),
        ("Maria Garcia", "(619) 555-0142", "Missed call — no voicemail left", "missed_call"),
        ("Tom Wilson", "tom@email.com", "Do you service La Mesa? My furnace won't turn on.", "web_form"),
        ("Lisa Chen", "lchen@email.com", "Your technician was here last week and the problem came back. I'm not happy.", "web_form"),
        ("Bob Smith", "bob@email.com", "I just moved to the area and want to set up annual maintenance.", "web_form"),
        ("Spam Bot", "spam@bot.com", "Get free Viagra pills!!! Click here for casino bonus!!!", "web_form"),
        ("Mike Johnson", "mike@email.com", "I need commercial refrigeration repair for my restaurant.", "web_form"),
        ("Jennifer Park", "(858) 555-0199", "My heater stopped working at 11pm, I have elderly parents visiting", "after_hours"),
        ("David Brown", "david@email.com", "Price list please", "web_form"),
        ("Alex Rivera", "alex@email.com", "I have a gas leak near my furnace, I can smell it!", "web_form"),
        ("Emma Wilson", "emma@email.com", "Can you install a smart thermostat? I already bought the unit.", "web_form"),
    ]
    
    print(f"\n📥 Ingesting {len(test_leads)} leads...\n")
    for name, contact, message, source in test_leads:
        agent.ingest(name, contact, message, source)
    
    print("⚙️  Processing with Gemini...\n")
    agent.process_all()
    
    # Status board
    print("📊 STATUS BOARD\n")
    print(f"  {'ID':<8} {'Name':<20} {'Category':<22} {'Urgency':<12} {'Status':<12} {'Conf':<6} {'Model'}")
    print(f"  {'--':<8} {'----':<20} {'--------':<22} {'-------':<12} {'------':<12} {'----':<6} {'-----'}")
    for lead in agent.leads:
        print(f"  {lead.id:<8} {lead.caller_name[:20]:<20} {lead.category:<22} {lead.urgency:<12} {lead.status:<12} {lead.confidence:<6.1f} {lead.model_used[:15]}")
    
    # Sample replies
    print("\n💬 SAMPLE GEMINI DRAFT REPLIES\n")
    for lead in agent.leads[:4]:
        print(f"  ── {lead.caller_name} ({lead.category}, conf={lead.confidence:.1f}) ──")
        print(f"  {lead.draft_reply[:200]}")
        print()
    
    # Daily report
    report = agent.daily_report()
    print("\n📈 DAILY REPORT\n")
    print(f"  Business: {report['business']}")
    print(f"  Model: {report['model']}")
    print(f"  Total leads: {report['summary']['total_leads']}")
    print(f"  Qualified: {report['metrics']['qualified_conversations']}")
    print(f"  Booked: {report['metrics']['appointments_booked']}")
    print(f"  Escalated: {report['metrics']['escalations']}")
    print(f"  Spam filtered: {report['metrics']['spam_filtered']}")
    print(f"  Avg confidence: {report['metrics']['avg_confidence']}")
    print(f"  Total tokens: {report['metrics']['total_tokens_used']}")
    print(f"  Avg response time: {report['metrics']['avg_response_ms']}ms")
    
    # Save output
    output_path = os.path.join(os.path.dirname(__file__), "gemini-agent-output.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Full output saved to: {output_path}")
    
    print("\n" + "=" * 70)
    print("  Multi-hackathon submission:")
    print("  • All Things Agentic (Gemini + ADK) — Aug 31")
    print("  • Agents for Humans (Strands SDK adaptation) — Sep 14")
    print("  • Agentic Cinema (media workflow adaptation) — Sep 7")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
