# Demo Video Script — Lead Recovery Agent
# LIVE MODEL: gemini-3.5-flash (verified working, 0.9+ confidence)
# For: All Things Agentic Hackathon (Aug 31, 2026 deadline)
# Duration: ~3 minutes

## Scene 1: Problem (0:00-0:30)

**[Screen recording: A busy HVAC company phone ringing, going to voicemail]**

"Every day, home-service businesses lose revenue from missed calls and unanswered web inquiries. A missed call at 6:01 PM might not get returned until tomorrow morning — by then, the customer has already called someone else.

62% of inbound calls to local businesses go unanswered. 85% of callers don't leave a voicemail. Each missed call is a job that was already paid for through marketing."

## Scene 2: Solution (0:30-1:00)

**[Screen recording: Lead Recovery Agent dashboard loading]**

"I built an autonomous AI agent that solves this. It's called the Lead Recovery Agent.

It runs in the background — you don't have to ask it to do anything. When a lead comes in — whether it's a missed call, a web form, or an after-hours inquiry — the agent automatically:

1. Ingests the lead
2. Classifies it using natural language understanding
3. Drafts an approved response
4. Routes it to the correct next action
5. Logs everything to a status board"

## Scene 3: Live Demo (1:00-2:15)

**[Screen recording: demo.html with demo leads loaded]**

"Let me show you. I'll load 10 sample leads to demonstrate how the agent handles different scenarios."

**[Click 'Load Demo Leads' button]**

"First, look at Sarah Mitchell. Her message says 'My AC stopped working and it's 95 degrees' — the agent detected emergency keywords including '95 degrees' and 'baby', classified this as urgent, and escalated it for an immediate human call. The draft reply tells her to expect a call within 30 minutes."

**[Click on Sarah Mitchell's lead]**

"Next, John Davis asks about pricing for a new AC unit. The agent classified this as a quote request, identified what information is missing — address and system brand — and drafted a reply asking for those details."

**[Click on John Davis's lead]**

"Now look at the spam message. The agent detected keywords like 'Viagra' and 'casino' and automatically flagged it as spam — no reply sent, no human time wasted."

**[Click on spam lead]**

"And Lisa Chen's complaint — the agent detected dissatisfaction keywords and escalated it directly to the owner. Complaints are NEVER auto-resolved."

**[Click on Lisa Chen's lead]**

"Notice the stats at the top: 10 leads processed, 1 booked, 3 escalated, 1 spam filtered — all autonomously, in under a second per lead."

## Scene 4: Architecture (2:15-2:40)

**[Screen recording: Architecture diagram from README]**

"The agent is built on Google Gemini for natural-language classification, the Google Agent Development Kit for multi-step orchestration, and Google Cloud for scalable deployment.

The prototype runs locally with zero cloud cost. In production, it deploys as a Cloud Function with webhooks for real phone systems."

## Scene 5: Business Value (2:40-3:00)

**[Screen recording: Daily report output from Python prototype]**

"This isn't just a hackathon project — it's a real business. I'm already selling this as a productized service to San Diego HVAC and plumbing companies. The agent turns missed leads into booked appointments, and the daily report makes the ROI visible to the business owner.

Every lead gets a next action. Every exception gets a human."

**[End with logo and contact: James Thompson, absbm14@gmail.com]**

## Recording Notes

- Use screen recording software (QuickTime on macOS)
- Record at 1920x1080
- Speak clearly, conversational tone
- Keep under 3 minutes (hackathon requirement is typically 3-5 min)
- Upload to YouTube as unlisted and link in Devpost submission
