# Lead Recovery Agent

> An autonomous AI agent that recovers missed leads for home-service businesses — one engine, four platform editions (Gemini, Strands SDK, CockroachDB, OpenSearch).

**Team:** James Thompson (solo)
**Hackathon:** All Things Agentic 2026 — Track: The Taskmaster
**Demo:** [Interactive dashboard](./demo.html) · [Architecture](./architecture.png)
**Status:** Live — classifying leads with **Gemini 3.5 Flash** at 0.9+ average confidence

## Quick start (a stranger can run this)

```bash
git clone https://github.com/jtabsbm/lead-recovery-agent
cd lead-recovery-agent

# Option A — no API key needed (keyword fallback classifier)
python3 gemini_lead_agent.py

# Option B — live Gemini classification (get a free key at https://aistudio.google.com/app/apikey)
export GEMINI_API_KEY="your-key"
python3 gemini_lead_agent.py
```

**Expected output:** a status board of 12 synthetic leads, each classified
(category, urgency, confidence), routed (escalated / booked / responded / spam),
with sample draft replies and a daily owner report. JSON output lands in
`gemini-agent-output.json`.

No pip installs required for the Gemini edition — it talks REST to the Gemini
API with the Python standard library. The model chain auto-probes
`gemini-3.5-flash → gemini-3.5-flash-lite → gemini-3-flash-preview → gemini-flash-latest`
and falls back to keywords if no key/network is available.

### Strands SDK edition (fully local, no cloud)

```bash
# requires: pip install strands-agents ollama ; ollama pull qwen2.5:7b
python3 strands_lead_agent.py
```

Deterministic @tool pipeline (ingest → classify → route → report) + an LLM
question-answering phase on the populated store, running on local Ollama.

### CockroachDB memory edition

```bash
# requires: pip install psycopg2-binary ; a free CRDB Cloud serverless cluster
export DATABASE_URL="postgresql://..."
python3 crdb_lead_agent.py
```

Every lead, classification, routing decision, and event lives in CockroachDB —
the process is stateless, memory survives restarts.

## The problem

Home-service businesses (HVAC, plumbing, electrical, roofing) lose revenue every
day from missed calls and unanswered web inquiries. A missed call at 6:01 PM
often isn't returned until morning — by then the customer has hired someone else.

## What the agent does

1. **Ingest** leads from web forms, missed-call events, voicemail transcripts, email
2. **Classify** with natural-language understanding: quote request, scheduling,
   complaint, urgent emergency, spam, out-of-scope — confidence-scored
3. **Draft** a recovery reply in the business's approved tone, asking the exact
   missing qualifying questions
4. **Route**: book, escalate (gas smell / no-AC-with-infant flags immediately),
   or discard spam
5. **Report**: daily owner summary of recovered vs missed

Every draft waits for owner review before sending — the AI runs the desk,
humans stay in command. The agent never invents prices, availability, or
diagnoses.

## Why Gemini 3.5

- "Commercial refrigeration repair" is correctly out-of-scope for a residential
  HVAC shop (keyword matchers get this wrong)
- "Furnace out — do you service La Mesa?" is a booking, not an info request
- 12/12 benchmark leads classified correctly at ~0.93 average confidence,
  vs 8/12 for the keyword fallback

## Architecture

See [architecture.png](./architecture.png) — one core pipeline, four platform
wrappers, human review gate before any customer contact.

## Real-world validation

This is an operating business, not just a demo: 36 San Diego-area home-service
companies contacted in week one with a productized offer ($750 pilot /
$2,500/mo core). Lead categories and reply templates come from that pipeline.

## License

MIT
