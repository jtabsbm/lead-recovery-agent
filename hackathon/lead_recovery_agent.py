#!/usr/bin/env python3
"""
Lead Recovery Agent — Hackathon Prototype
All Things Agentic Hackathon (Aug 31, 2026)

An autonomous AI agent that monitors missed calls and web inquiries for
home-service businesses, qualifies leads, drafts approved responses, and
routes the next step — all without human intervention for routine cases.

Built with Google Gemini + Agent Development Kit (ADK) concepts.
Runs locally with zero cloud cost for the prototype.

Tracks: https://allthingsagentichackathon.devpost.com/
"""

import json
import time
import uuid
import os
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── Data Models ───────────────────────────────────────────────────────────────

class LeadStatus(Enum):
    NEW = "new"
    QUALIFYING = "qualifying"
    RESPONDED = "responded"
    BOOKED = "booked"
    ESCALATED = "escalated"
    CLOSED = "closed"
    SPAM = "spam"

class Urgency(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    EMERGENCY = "emergency"

class LeadSource(Enum):
    MISSED_CALL = "missed_call"
    WEB_FORM = "web_form"
    EMAIL = "email"
    CHAT = "chat"
    AFTER_HOURS = "after_hours"

@dataclass
class Lead:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""
    caller_name: str = ""
    contact: str = ""
    message: str = ""
    received_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = LeadStatus.NEW.value
    urgency: str = Urgency.NORMAL.value
    category: str = ""
    missing_info: list = field(default_factory=list)
    suggested_action: str = ""
    draft_reply: str = ""
    booked_time: str = ""
    escalation_reason: str = ""
    response_sent_at: str = ""

@dataclass
class BusinessConfig:
    name: str = "Northside HVAC"
    service_area: list = field(default_factory=lambda: ["San Diego", "La Mesa", "Chula Vista"])
    business_hours: str = "Mon-Fri 7am-6pm, Sat 8am-4pm"
    after_hours: bool = True
    services: list = field(default_factory=lambda: [
        "AC repair", "heating repair", "HVAC installation",
        "maintenance", "emergency service"
    ])
    exclusions: list = field(default_factory=lambda: [
        "commercial refrigeration", "new construction"
    ])
    emergency_keywords: list = field(default_factory=lambda: [
        "no ac", "gas smell", "carbon monoxide", "leak",
        "fire", "smoke", "95 degrees", "freezing", "infant", "elderly"
    ])
    booking_url: str = ""


# ─── Agent Core ─────────────────────────────────────────────────────────────────

class LeadRecoveryAgent:
    """
    Autonomous agent that:
    1. Ingests missed leads from multiple sources
    2. Classifies and qualifies each lead
    3. Drafts an approved response
    4. Routes the next step (book, callback, escalate)
    5. Logs everything to a status board
    """

    TRIAGE_CATEGORIES = [
        "quote_request", "scheduling", "service_area_question",
        "missing_information", "complaint", "urgent_escalate",
        "no_fit", "spam"
    ]

    def __init__(self, config: BusinessConfig):
        self.config = config
        self.leads: list[Lead] = []
        self.response_templates = self._load_templates()
        self.stats = {
            "total_leads": 0,
            "qualified": 0,
            "booked": 0,
            "escalated": 0,
            "spam_filtered": 0,
            "avg_response_time_seconds": 0,
        }

    def _load_templates(self) -> dict:
        return {
            "quote_request": "Hi {name}, thanks for reaching out! To give you an accurate quote we'd need a few more details: {missing}. Would you like to schedule a free estimate?",
            "scheduling": "Hi {name}, thanks for contacting {business}! We'd be happy to help. What day and time works best for you?",
            "service_area_question": "Hi {name}, yes — {area} is within our service area. We'd be happy to help. When would you like us to come by?",
            "missing_information": "Hi {name}, thanks for your inquiry. Could you provide a few more details so we can help you: {missing}?",
            "complaint": "Hi {name}, I'm sorry to hear about this. I've flagged your message for the owner directly — expect a personal call within 2 business hours.",
            "urgent_escalate": "Hi {name}, this sounds urgent. I've flagged this for {business}'s on-call technician — expect a call within 30 minutes. Please have your address ready.",
            "no_fit": "Hi {name}, thanks for reaching out. Unfortunately, we don't currently handle {exclusion} in {area}. We'd recommend checking with a specialist in that field.",
            "spam": None,  # No reply for spam
        }

    # ─── Lead Ingestion ──────────────────────────────────────────────────────

    def ingest_missed_call(self, caller_name: str, phone: str, called_at: str = ""):
        lead = Lead(
            source=LeadSource.MISSED_CALL.value,
            caller_name=caller_name,
            contact=phone,
            message=f"Missed call from {caller_name} at {phone}",
            received_at=called_at or datetime.now().isoformat(),
        )
        self.leads.append(lead)
        self.stats["total_leads"] += 1
        return lead

    def ingest_web_form(self, name: str, email: str, message: str, form_type: str = "contact"):
        lead = Lead(
            source=LeadSource.WEB_FORM.value,
            caller_name=name,
            contact=email,
            message=message,
        )
        self.leads.append(lead)
        self.stats["total_leads"] += 1
        return lead

    def ingest_after_hours(self, name: str, contact: str, message: str):
        lead = Lead(
            source=LeadSource.AFTER_HOURS.value,
            caller_name=name,
            contact=contact,
            message=message,
        )
        self.leads.append(lead)
        self.stats["total_leads"] += 1
        return lead

    # ─── Classification Engine ───────────────────────────────────────────────

    def classify(self, lead: Lead) -> Lead:
        """Classify a lead using keyword matching and business rules."""
        msg = lead.message.lower()

        # Check for emergency/urgent keywords
        for keyword in self.config.emergency_keywords:
            if keyword in msg:
                lead.urgency = Urgency.EMERGENCY.value
                lead.category = "urgent_escalate"
                lead.escalation_reason = f"Emergency keyword detected: '{keyword}'"
                lead.suggested_action = "ESCALATE: Immediate human call required"
                return lead

        # Check for complaints
        complaint_words = ["unhappy", "complaint", "problem came back", "not satisfied", "terrible", "worst", "angry"]
        for word in complaint_words:
            if word in msg:
                lead.urgency = Urgency.HIGH.value
                lead.category = "complaint"
                lead.suggested_action = "ESCALATE: Route to owner/manager"
                return lead

        # Check for spam
        spam_words = ["viagra", "casino", "crypto", "click here", "free money", "lottery", "prize winner"]
        for word in spam_words:
            if word in msg:
                lead.category = "spam"
                lead.status = LeadStatus.SPAM.value
                lead.suggested_action = "DISCARD: Spam detected"
                self.stats["spam_filtered"] += 1
                return lead

        # Check for quote requests
        quote_words = ["quote", "estimate", "price", "how much", "cost", "pricing"]
        if any(w in msg for w in quote_words):
            lead.category = "quote_request"
            lead.missing_info = self._identify_missing_info(msg)
            lead.suggested_action = "COLLECT: Request missing details, then schedule estimate"
            return lead

        # Check for scheduling
        schedule_words = ["appointment", "schedule", "book", "come out", "available", "when can"]
        if any(w in msg for w in schedule_words):
            lead.category = "scheduling"
            lead.suggested_action = "BOOK: Confirm availability and schedule visit"
            return lead

        # Check for service area questions
        area_words = ["do you service", "do you cover", "area", "location", "near me", "come to"]
        if any(w in msg for w in area_words):
            lead.category = "service_area_question"
            in_area = self._check_service_area(msg)
            if not in_area:
                lead.category = "no_fit"
                lead.suggested_action = "REDIRECT: Outside service area"
            else:
                lead.suggested_action = "CONFIRM: In service area, book appointment"
            return lead

        # Check for exclusions
        for exclusion in self.config.exclusions:
            if exclusion in msg:
                lead.category = "no_fit"
                lead.suggested_action = f"REDIRECT: {exclusion} not in scope"
                return lead

        # Default: missing information
        lead.category = "missing_information"
        lead.missing_info = ["service type needed", "address/area", "preferred time"]
        lead.suggested_action = "COLLECT: Request more details"
        return lead

    def _identify_missing_info(self, msg: str) -> list:
        missing = []
        if "address" not in msg and "area" not in msg and "location" not in msg:
            missing.append("address/service area")
        if "size" not in msg and "sq ft" not in msg and "square" not in msg:
            missing.append("system size or property details")
        if "brand" not in msg and "model" not in msg:
            missing.append("current system brand/model")
        if not missing:
            missing.append("preferred appointment time")
        return missing

    def _check_service_area(self, msg: str) -> bool:
        for area in self.config.service_area:
            if area.lower() in msg:
                return True
        return False

    # ─── Response Generation ─────────────────────────────────────────────────

    def generate_response(self, lead: Lead) -> Lead:
        """Generate a draft response using approved templates."""
        if lead.category == "spam" or lead.status == LeadStatus.SPAM.value:
            lead.draft_reply = "(No reply — flagged as spam)"
            return lead

        template = self.response_templates.get(lead.category, "")
        if not template:
            lead.draft_reply = "(No template available — escalate to human)"
            lead.status = LeadStatus.ESCALATED.value
            return lead

        missing_str = ", ".join(lead.missing_info) if lead.missing_info else "your contact details"
        reply = template.format(
            name=lead.caller_name or "there",
            business=self.config.name,
            missing=missing_str,
            area=", ".join(self.config.service_area[:2]),
            exclusion=lead.category,
        )
        lead.draft_reply = reply
        lead.status = LeadStatus.RESPONDED.value
        lead.response_sent_at = datetime.now().isoformat()
        return lead

    # ─── Routing Engine ──────────────────────────────────────────────────────

    def route(self, lead: Lead) -> Lead:
        """Route the lead to its next action based on classification."""
        if lead.category in ("urgent_escalate", "complaint"):
            lead.status = LeadStatus.ESCALATED.value
            self.stats["escalated"] += 1
        elif lead.category == "spam":
            lead.status = LeadStatus.SPAM.value
        elif lead.category == "no_fit":
            lead.status = LeadStatus.CLOSED.value
        elif lead.category in ("scheduling", "service_area_question"):
            # Auto-book (in production, this would check calendar availability)
            lead.status = LeadStatus.BOOKED.value
            lead.booked_time = "Next available appointment (pending confirmation)"
            self.stats["booked"] += 1
        elif lead.category in ("quote_request", "missing_information"):
            lead.status = LeadStatus.RESPONDED.value
            self.stats["qualified"] += 1

        return lead

    # ─── Full Pipeline ───────────────────────────────────────────────────────

    def process(self, lead: Lead) -> Lead:
        """Run the full recovery pipeline on a single lead."""
        lead = self.classify(lead)
        lead = self.generate_response(lead)
        lead = self.route(lead)
        return lead

    def process_all(self):
        """Process all unprocessed leads."""
        for lead in self.leads:
            if lead.status == LeadStatus.NEW.value:
                self.process(lead)

    # ─── Reporting ───────────────────────────────────────────────────────────

    def status_board(self) -> list[dict]:
        """Return a status board of all leads."""
        return [asdict(lead) for lead in self.leads]

    def daily_report(self) -> dict:
        """Generate a daily summary report."""
        by_category = {}
        by_status = {}
        for lead in self.leads:
            by_category[lead.category] = by_category.get(lead.category, 0) + 1
            by_status[lead.status] = by_status.get(lead.status, 0) + 1

        response_times = []
        for lead in self.leads:
            if lead.response_sent_at:
                try:
                    received = datetime.fromisoformat(lead.received_at)
                    responded = datetime.fromisoformat(lead.response_sent_at)
                    delta = (responded - received).total_seconds()
                    response_times.append(delta)
                except:
                    pass

        avg_response = sum(response_times) / len(response_times) if response_times else 0

        return {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "business": self.config.name,
            "summary": {
                "total_leads": len(self.leads),
                "by_category": by_category,
                "by_status": by_status,
            },
            "metrics": {
                "qualified_conversations": self.stats["qualified"],
                "appointments_booked": self.stats["booked"],
                "escalations": self.stats["escalated"],
                "spam_filtered": self.stats["spam_filtered"],
                "avg_response_time_seconds": round(avg_response, 1),
            },
            "unresolved": [
                {"id": l.id, "name": l.caller_name, "category": l.category, "action": l.suggested_action}
                for l in self.leads if l.status not in (LeadStatus.BOOKED.value, LeadStatus.CLOSED.value, LeadStatus.SPAM.value)
            ],
        }


# ─── Demo / Test Harness ───────────────────────────────────────────────────────

def run_demo():
    """Run a full demo with synthetic leads to showcase the agent."""
    print("=" * 70)
    print("  LEAD RECOVERY AGENT — DEMO")
    print("  All Things Agentic Hackathon Prototype")
    print("=" * 70)

    config = BusinessConfig(
        name="Northside HVAC",
        service_area=["San Diego", "La Mesa", "Chula Vista", "Kearny Mesa", "Santee"],
        business_hours="Mon-Fri 7am-6pm, Sat 8am-4pm",
        services=["AC repair", "heating repair", "HVAC installation", "maintenance"],
        exclusions=["commercial refrigeration", "new construction"],
    )

    agent = LeadRecoveryAgent(config)

    # Simulate incoming leads
    print("\n📥 INGESTING LEADS...\n")

    agent.ingest_web_form("Sarah Mitchell", "sarah@email.com",
        "My AC stopped working and it's 95 degrees inside. I have a baby and need someone today!")

    agent.ingest_web_form("John Davis", "jdavis@email.com",
        "How much for a new AC unit? My house is about 1800 sq ft.")

    agent.ingest_missed_call("Maria Garcia", "(619) 555-0142")

    agent.ingest_web_form("Tom Wilson", "tom@email.com",
        "Do you service La Mesa? My furnace won't turn on.")

    agent.ingest_web_form("Lisa Chen", "lchen@email.com",
        "Your technician was here last week and the problem came back. I'm not happy.")

    agent.ingest_web_form("Bob Smith", "bob@email.com",
        "I just moved to the area and want to set up annual maintenance.")

    agent.ingest_web_form("Unknown", "spam@bot.com",
        "Get free Viagra pills!!! Click here for casino bonus!!!")

    agent.ingest_web_form("Mike Johnson", "mike@email.com",
        "I need commercial refrigeration repair for my restaurant.")

    agent.ingest_after_hours("Jennifer Park", "(858) 555-0199",
        "My heater stopped working at 11pm, I have elderly parents visiting")

    agent.ingest_web_form("David Brown", "david@email.com",
        "Price list please")

    print(f"  {len(agent.leads)} leads ingested")

    # Process all leads
    print("\n⚙️  PROCESSING LEADS...\n")
    agent.process_all()

    # Show results
    print("📊 STATUS BOARD\n")
    print(f"  {'ID':<8} {'Name':<20} {'Category':<22} {'Urgency':<12} {'Status':<12}")
    print(f"  {'--':<8} {'----':<20} {'--------':<22} {'-------':<12} {'------':<12}")
    for lead in agent.leads:
        print(f"  {lead.id:<8} {lead.caller_name[:20]:<20} {lead.category:<22} {lead.urgency:<12} {lead.status:<12}")

    # Show draft replies for first 3 leads
    print("\n💬 SAMPLE DRAFT REPLIES\n")
    for lead in agent.leads[:3]:
        print(f"  ── {lead.caller_name} ({lead.category}) ──")
        print(f"  {lead.draft_reply}")
        print()

    # Daily report
    report = agent.daily_report()
    print("\n📈 DAILY REPORT\n")
    print(f"  Business: {report['business']}")
    print(f"  Total leads: {report['summary']['total_leads']}")
    print(f"  Qualified: {report['metrics']['qualified_conversations']}")
    print(f"  Booked: {report['metrics']['appointments_booked']}")
    print(f"  Escalated: {report['metrics']['escalations']}")
    print(f"  Spam filtered: {report['metrics']['spam_filtered']}")
    print(f"  Avg response time: {report['metrics']['avg_response_time_seconds']}s")
    print(f"  Unresolved: {len(report['unresolved'])}")

    # Export status board as JSON
    output_path = os.path.join(os.path.dirname(__file__), "agent-demo-output.json")
    with open(output_path, "w") as f:
        json.dump({
            "agent": "LeadRecoveryAgent v1.0",
            "business": config.name,
            "status_board": agent.status_board(),
            "daily_report": report,
        }, f, indent=2)
    print(f"\n💾 Full output saved to: {output_path}")

    print("\n" + "=" * 70)
    print("  Demo complete. This agent can be deployed with:")
    print("  - Google Gemini for natural-language lead qualification")
    print("  - Google Cloud for scalable deployment")
    print("  - Google ADK for multi-step agent orchestration")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
