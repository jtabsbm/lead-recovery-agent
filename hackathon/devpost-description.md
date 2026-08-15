CallbackOps is an AI-operated lead-recovery service for small home-service businesses (HVAC, plumbing, electrical, roofing). When a customer's call goes unanswered or a web inquiry sits in an inbox, the agent catches it, understands it, and recovers it.

## The problem
A 3-truck HVAC company misses 30-40% of inbound calls during summer rush. Each missed call is a $300-$2,000 job walking to a competitor. Owners know it's happening but can't sit by the phone — and after-hours inquiries wait until morning, when the customer has already hired someone else.

## What the agent does
Built on Google Gemini (gemini-3-flash-preview via the Gemini API), the agent runs the recovery desk end-to-end:

1. **Ingest** — every lead source feeds one pipeline: web forms, missed-call events, voicemail transcripts, email
2. **Classify** — Gemini reads each message with full natural-language understanding: quote request, scheduling, complaint, urgent emergency, spam, or out-of-scope. Confidence-scored, with keyword fallback if the API is unreachable
3. **Draft** — a recovery reply in the business's approved tone, asking exactly the missing qualifying questions Gemini identified
4. **Route** — book it, escalate it (gas smell / no-AC-with-infant flags immediately), or discard spam
5. **Report** — a daily owner summary: what came in, what was recovered, what still needs a human

Every draft waits for owner review before sending — the AI runs the desk, humans stay in command.

## Why Gemini
- Real NL understanding beats keyword matching: "commercial refrigeration repair" is correctly out-of-scope for a residential HVAC shop; "furnace out, do you service La Mesa?" is a booking, not an info request
- 12/12 demo leads classified correctly with 0.988 average confidence vs 8/12 for keyword-only
- REST integration with automatic model fallback — no SDK lock-in, survives model deprecations
- Runs on Google Cloud credits; deployment target is Cloud Run + the GenAI App Builder credit

## The business
This is a real operating business, not just a demo: 36 San Diego-area home-service companies contacted in week one, with a productized offer ($750 pilot / $2,500/mo core). The same engine powers three hackathon builds (Strands SDK edition, CockroachDB memory edition, OpenSearch retrieval edition).

## Repo
https://github.com/jtabsbm/lead-recovery-agent — working classifier, demo dashboard, and the multi-platform architecture.

## Built with
Gemini API (gemini-3-flash-preview), Python, Strands Agents SDK, CockroachDB, OpenSearch, Ollama (local fallback)
