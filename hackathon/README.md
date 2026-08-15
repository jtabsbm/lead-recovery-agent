# Lead Recovery Agent

> An autonomous AI agent that recovers missed leads for home-service businesses — built for the **All Things Agentic Hackathon**.

**Team:** James Thompson (solo)  
**Track:** The Taskmaster  
**Demo:** [Live Interactive Demo](./demo.html)  
**Code:** https://github.com/TyrannicAwe/lead-recovery-agent  
**Video:** (to be recorded — script at `demo-video-script.md`)

## The Problem

Home-service businesses (HVAC, plumbing, electrical, roofing) lose revenue every day from missed calls and unanswered web inquiries. A missed call at 6:01 PM might not get returned until the next morning — by then, the customer has called someone else.

**The stat:** 62% of inbound calls to local businesses go unanswered, and 85% of callers don't leave a voicemail. Each missed call is a job that was already paid for through marketing.

## The Solution

Lead Recovery Agent is an autonomous AI agent that:

1. **Ingests** missed leads from multiple sources (missed calls, web forms, after-hours inquiries, chat)
2. **Classifies** each lead using natural-language understanding (quote request, scheduling, urgent, complaint, spam, etc.)
3. **Generates** an approved draft response using business-specific templates
4. **Routes** the lead to the correct next action (book appointment, escalate to human, discard spam)
5. **Logs** everything to a status board with daily reports

The agent runs autonomously in the background — exactly what "agentic AI" means. It doesn't wait for a human to ask it to do something. It detects a missed lead, processes it, and takes action.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LEAD SOURCES                          │
│  Missed Calls │ Web Forms │ Email │ Chat │ After Hours   │
└──────────┬──────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│              LEAD RECOVERY AGENT                         │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │
│  │ Ingest  │→│ Classify │→│ Respond │→│  Route   │  │
│  │ Module  │  │ Engine   │  │ Engine  │  │ Engine   │  │
│  └─────────┘  └──────────┘  └─────────┘  └──────────┘  │
│                      │                                   │
│                      ▼                                   │
│              ┌───────────────┐                           │
│              │  Status Board  │                          │
│              │  + Reports     │                          │
│              └───────────────┘                           │
└─────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────┐          ┌──────────────────────┐
│  ROUTING OUTPUT   │          │  HUMAN ESCALATION     │
│  ✓ Booked         │          │  ⚠️ Emergency call     │
│  ✓ Response sent  │          │  ⚠️ Complaint → owner  │
│  ✓ Spam filtered  │          │  ⚠️ Out of scope       │
│  ✓ Closed         │          │                       │
└──────────────────┘          └──────────────────────┘
```

## How It Uses Gemini + Google Cloud

- **Gemini** for natural-language lead classification and response generation (replacing the keyword-based prototype with true NL understanding)
- **Google Cloud Functions** for serverless lead ingestion webhooks
- **Cloud Firestore** for the lead status board and reporting
- **Agent Development Kit (ADK)** for multi-step agent orchestration
- **Cloud Scheduler** for after-hours monitoring

## Key Features

- **Autonomous**: Runs without human prompts — detects and processes leads automatically
- **Multi-source**: Handles missed calls, web forms, email, chat, and after-hours inquiries
- **Safety-first**: Urgent and complaint cases are ALWAYS escalated to humans, never auto-resolved
- **Spam filtering**: Automatically detects and discards spam
- **Approved templates**: All responses use business-approved language — no hallucinated pricing or promises
- **Daily reports**: Summary of leads, response times, bookings, and escalations
- **Zero-CRM**: Works with existing tools (phone, email, calendar, spreadsheet)

## Triage Categories

| Category | What it catches | Default action |
|---|---|---|
| Quote request | Pricing, estimates | Collect missing info → schedule estimate |
| Scheduling | Appointments, booking | Confirm availability → book |
| Service area | Location eligibility | Confirm or redirect |
| Missing info | Vague inquiries | Request specifics |
| Complaint | Dissatisfaction | **Escalate to owner** |
| Urgent/Escalate | No AC, gas smell, safety | **Immediate human call** |
| No-fit | Out of scope | Polite redirect |
| Spam | Unsolicited commercial | Discard |

## Tech Stack

- **AI**: Google Gemini (NL classification + response generation)
- **Framework**: Google Agent Development Kit (ADK)
- **Cloud**: Google Cloud Functions, Firestore, Cloud Scheduler
- **Frontend**: HTML/CSS/JS (interactive demo)
- **Backend**: Python (prototype), Cloud Functions (production)

## Files

- `lead_recovery_agent.py` — Python prototype with full agent logic
- `demo.html` — Interactive web demo (no dependencies, runs locally)
- `agent-demo-output.json` — Sample output from the prototype

## What's Next

- Integrate Gemini API for NL-based classification (replacing keywords)
- Add Google Calendar integration for real booking
- Deploy as Cloud Function with webhook for real phone systems
- Add SMS/email delivery for approved responses
- Build multi-business support with per-client configurations

## License

MIT — Built for All Things Agentic Hackathon 2026
