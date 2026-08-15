# Hackathon Submission Checklist

## All Things Agentic Hackathon
**Deadline:** Aug 31, 2026 @ 5:00pm PDT  
**Submission URL:** https://devpost.com/submit-to/30845-all-things-agentic-hackathon/manage/submissions  
**Track:** The Taskmaster  

### What to Submit (checklist)

- [ ] Demo video (3-5 min) — script at `hackathon/demo-video-script.md`
- [ ] Code repository — `hackathon/lead_recovery_agent.py` + `hackathon/demo.html`
- [ ] Architecture diagram — `hackathon/architecture.html`
- [ ] Short write-up (text description)

### Submission Write-Up (ready to paste)

**Project Name:** Lead Recovery Agent

**Short Description:**
An autonomous AI agent that recovers missed leads for home-service businesses. It ingests missed calls, web forms, and after-hours inquiries, classifies each lead using natural-language understanding, drafts approved responses, and routes the next action — all without human intervention for routine cases.

**Long Description:**
Every day, home-service businesses lose revenue from missed calls and unanswered web inquiries. 62% of inbound calls go unanswered, and 85% of callers don't leave voicemail. Each missed call is a job that was already paid for through marketing.

Lead Recovery Agent solves this by running autonomously in the background. When a lead comes in — whether it's a missed call, a web form, or an after-hours inquiry — the agent:

1. **Ingests** the lead from multiple sources
2. **Classifies** it using NL understanding (quote request, scheduling, urgent, complaint, spam)
3. **Generates** an approved draft response using business-specific templates
4. **Routes** the lead to the correct next action (book, escalate, discard)
5. **Logs** everything to a status board with daily reports

The agent handles 8 triage categories, from quote requests to emergency escalations. Urgent and complaint cases are ALWAYS escalated to humans — never auto-resolved. Spam is automatically filtered.

Built with Google Gemini for natural-language classification, Google Agent Development Kit for multi-step orchestration, and Google Cloud for scalable deployment. The prototype runs locally with zero cloud cost.

This isn't just a hackathon project — it's a real business. I'm already selling this as a productized service to San Diego HVAC and plumbing companies.

**Tech Stack:**
- Google Gemini (NL classification + response generation)
- Google Agent Development Kit (ADK) for agent orchestration
- Google Cloud Functions (webhook ingestion)
- Cloud Firestore (status board + reporting)
- Cloud Scheduler (after-hours monitoring)

**Track:** The Taskmaster — handles heavy lifting of massive datasets and automates complex workflows asynchronously.

**Links:**
- Interactive demo: `demo.html`
- Source code: `lead_recovery_agent.py`
- Architecture: `architecture.html`

---

## Agentic Cinema Hackathon
**Deadline:** Sep 7, 2026 @ 2:00pm PDT  
**Submission URL:** TBD (register at https://agentic-cinema.devpost.com/)  

### What to Submit
- [ ] Demo video
- [ ] Code repository — `hackathon/screen_agent.py`
- [ ] Short write-up

### Submission Write-Up (ready to paste)

**Project Name:** ScreenAgent — AI Agent for Filmmakers

**Short Description:**
An AI agent that helps screenwriters and indie filmmakers by analyzing script structure, generating shot lists, checking continuity, estimating budgets, and creating call sheets — all from a screenplay upload.

---

## Agents for Humans Hackathon
**Deadline:** Sep 14, 2026 @ 5:00pm PDT  
**Track:** TBD (uses Strands Agents SDK)

### Submission
- [ ] Adapt Lead Recovery Agent to use Strands Agents SDK
- [ ] Demo video
- [ ] Code repository
- [ ] Short write-up
