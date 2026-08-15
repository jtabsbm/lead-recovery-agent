#!/usr/bin/env python3
"""
Lead Recovery Agent — Strands Agents SDK Edition
Target: Agents for Humans hackathon (Sep 14, 2026) — strands-agents

Same core logic as the Gemini edition, but expressed as a Strands agent with
explicit @tool functions. Demonstrates the SDK's tool-use model: small,
typed tools the LLM can call, composed by an agent loop.

Run:  python strands_lead_agent.py
"""

import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict

# ─── In-memory lead store (demo) ───────────────────────────────────────────────

LEADS: dict = {}
STATS = {"total": 0, "qualified": 0, "booked": 0, "escalated": 0, "spam": 0}


@dataclass
class Lead:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    contact: str = ""
    message: str = ""
    source: str = "web_form"
    received_at: str = field(default_factory=lambda: datetime.now().isoformat())
    category: str = ""
    urgency: str = "normal"
    missing_info: list = field(default_factory=list)
    draft_reply: str = ""
    action: str = ""
    status: str = "new"


# ─── Tool functions (the Strands pattern: @tool) ──────────────────────────────

try:
    from strands import Agent, tool
    STRANDS_AVAILABLE = True
except ImportError:  # pragma: no cover
    STRANDS_AVAILABLE = False
    Agent = None  # type: ignore[assignment,misc]
    # No-op stand-ins so the file parses and the direct-tool harness still runs
    # when strands-agents is not installed.
    def tool(fn=None, *args, **kwargs):  # type: ignore[no-redef]
        if callable(fn):
            return fn
        return lambda f: f


@tool
def classify_lead(message: str, business_name: str = "Northside HVAC") -> dict:
    """Classify an inbound lead message.

    Args:
        message: The raw lead text (web form, SMS, voicemail transcript).
        business_name: Name of the business receiving the lead.

    Returns:
        dict with category, urgency, missing_info, draft_reply, confidence.
    """
    msg = message.lower()

    emergency_kw = ["no ac", "gas smell", "carbon monoxide", "leak", "fire", "smoke",
                    "95 degrees", "freezing", "infant", "elderly", "baby", "emergency",
                    "medical equipment"]
    complaint_kw = ["unhappy", "complaint", "problem came back", "not satisfied",
                    "terrible", "angry", "still broken"]
    spam_kw = ["viagra", "casino", "crypto", "click here", "free money", "lottery",
               "seo services", "backlink"]
    quote_kw = ["quote", "estimate", "price", "how much", "cost", "pricing"]
    schedule_kw = ["appointment", "schedule", "book", "come out", "available", "when can"]

    if any(w in msg for w in emergency_kw):
        return {"category": "urgent_escalate", "urgency": "emergency",
                "missing_info": ["callback number", "address"],
                "draft_reply": f"This sounds urgent — {business_name} has been flagged for an immediate call. Please expect contact within 30 minutes.",
                "confidence": 0.9}
    if any(w in msg for w in complaint_kw):
        return {"category": "complaint", "urgency": "high",
                "missing_info": ["work order number"],
                "draft_reply": "Sorry to hear this — your message has been routed directly to the owner.",
                "confidence": 0.85}
    if any(w in msg for w in spam_kw):
        return {"category": "spam", "urgency": "normal", "missing_info": [],
                "draft_reply": "", "confidence": 0.95}
    if any(w in msg for w in quote_kw):
        return {"category": "quote_request", "urgency": "normal",
                "missing_info": ["address", "system details"],
                "draft_reply": "Thanks for reaching out! To give an accurate quote we need a few more details — what's the address and system type?",
                "confidence": 0.8}
    if any(w in msg for w in schedule_kw):
        return {"category": "scheduling", "urgency": "normal", "missing_info": [],
                "draft_reply": "Thanks for contacting us! What day and time works best for you?",
                "confidence": 0.8}
    return {"category": "missing_information", "urgency": "normal",
            "missing_info": ["service type", "address", "preferred time"],
            "draft_reply": "Thanks for your inquiry — could you share a few more details so we can help?",
            "confidence": 0.6}


@tool
def route_lead(lead_id: str) -> dict:
    """Route a classified lead to the right next step (book/escalate/respond/close).

    Args:
        lead_id: The lead's unique id from ingest_lead.

    Returns:
        dict with status and suggested action.
    """
    lead = LEADS.get(lead_id)
    if not lead:
        return {"error": "unknown lead_id"}

    if lead.category in ("urgent_escalate", "complaint"):
        lead.status = "escalated"
        action = "⚠️ ESCALATE — immediate human call required"
        STATS["escalated"] += 1
    elif lead.category == "spam":
        lead.status = "spam"
        action = "DISCARD — spam detected"
        STATS["spam"] += 1
    elif lead.category == "no_fit":
        lead.status = "closed"
        action = "CLOSED — outside scope/area"
    elif lead.category in ("scheduling", "service_area_question"):
        lead.status = "booked"
        action = "✓ BOOKED — next available appointment"
        STATS["booked"] += 1
    else:
        lead.status = "responded"
        action = "✓ RESPONDED — draft ready for owner review"
        STATS["qualified"] += 1

    return {"lead_id": lead_id, "status": lead.status, "action": action}


@tool
def ingest_lead(name: str, contact: str, message: str, source: str = "web_form") -> str:
    """Log a new inbound lead.

    Args:
        name: Caller/customer name.
        contact: Phone or email.
        message: Raw message text.
        source: Lead source (web_form, missed_call, sms, after_hours).

    Returns:
        The new lead's id.
    """
    lead = Lead(name=name, contact=contact, message=message, source=source)
    LEADS[lead.id] = lead
    STATS["total"] += 1
    return lead.id


@tool
def draft_owner_report() -> dict:
    """Generate the end-of-day owner report across all leads."""
    by_cat, by_status = {}, {}
    for l in LEADS.values():
        by_cat[l.category] = by_cat.get(l.category, 0) + 1
        by_status[l.status] = by_status.get(l.status, 0) + 1
    return {
        "generated_at": datetime.now().isoformat(),
        "total_leads": len(LEADS),
        "by_category": by_cat,
        "by_status": by_status,
        "stats": STATS,
    }


# ─── Agent assembly (Strands) ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the after-hours desk agent for a home-service business.
You have four tools: ingest_lead, classify_lead, route_lead, draft_owner_report.
Always ingest first, then classify, then route. Use draft_owner_report at the end.
Be concise. Never invent prices, availability, or diagnoses. Escalate anything
that sounds like a safety issue (gas, smoke, carbon monoxide, medical, extreme
temps with vulnerable people)."""


def run_strands_demo():
    """Run the Strands agent over the same demo leads."""
    print("=" * 70)
    print("  Lead Recovery Agent — Strands Agents SDK Edition")
    print("  Target: Agents for Humans hackathon (Sep 14)")
    print("=" * 70)

    if STRANDS_AVAILABLE:
        try:
            agent = Agent(system_prompt=SYSTEM_PROMPT,
                          tools=[ingest_lead, classify_lead, route_lead, draft_owner_report])
            print("✓ Strands Agent assembled with 4 tools")
            demo_prompt = (
                "Process these 3 leads and then give me the owner report:\n"
                "1. Sarah, sarah@x.com, 'AC out, 95 degrees, baby at home' (web_form)\n"
                "2. John, jd@x.com, 'How much for a new unit? 1800 sq ft house' (web_form)\n"
                "3. Spam Bot, spam@bot.com, 'free casino crypto viagra click here' (web_form)"
            )
            result = agent(demo_prompt)
            print("\n--- Agent output ---\n")
            print(str(result)[:1500])
        except Exception as e:
            print(f"Strands agent runtime error (needs credentials): {e}")
            print("Falling back to direct tool invocation demo.\n")
            _direct_tool_demo()
    else:
        print("strands-agents not importable — running direct tool demo.\n")
        _direct_tool_demo()


def _direct_tool_demo():
    """Exercise the same @tool functions directly (no LLM needed)."""
    demo = [
        ("Sarah Mitchell", "sarah@email.com", "My AC stopped working and it's 95 degrees inside. I have a baby and need someone today!"),
        ("John Davis", "jdavis@email.com", "How much for a new AC unit? My house is about 1800 sq ft."),
        ("Lisa Chen", "lchen@email.com", "Your technician was here last week and the problem came back. I'm not happy."),
        ("Spam Bot", "spam@bot.com", "Get free Viagra pills!!! Click here for casino bonus!!!"),
        ("Tom Wilson", "tom@email.com", "Can you install a smart thermostat? I already bought the unit."),
    ]
    print(f"Processing {len(demo)} leads through the tool pipeline:\n")
    for name, contact, message in demo:
        lid = ingest_lead(name, contact, message)
        c = classify_lead(message)
        lead = LEADS[lid]
        lead.category = c["category"]
        lead.urgency = c["urgency"]
        lead.missing_info = c["missing_info"]
        lead.draft_reply = c["draft_reply"]
        r = route_lead(lid)
        print(f"  {name:18s} → {c['category']:20s} {r['status']:10s} {r['action']}")
    print("\n--- Owner report ---\n")
    print(json.dumps(draft_owner_report(), indent=2))


if __name__ == "__main__":
    run_strands_demo()
