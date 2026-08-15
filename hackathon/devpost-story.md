## The problem: home-service businesses lose 40%+ of inbound leads

When a plumber is under a sink, the phone rings out. When an HVAC crew is on a roof in August, the web-form inquiry sits unanswered for hours. Industry data puts missed-call rates for home-service trades at 25-40%, and leads contacted after the first hour decay fast. Small operators cannot hire a $4,000/month receptionist, so the leads they already paid to attract (Google Ads, Angie, Yelp, postcards) quietly die.

## What it does

**CallbackOps — Gemini Lead Recovery Agent** recovers those leads. It connects to a business's existing phone/web/email intake (no new hardware, no CRM migration), reads every missed call, voicemail transcript, and web inquiry, and for each one:

1. **Classifies** urgency and intent with Gemini 3.5 Flash (emergency / scheduling / quote / missing_information / no_fit / spam) with a confidence score
2. **Drafts** a specific, human-reviewed recovery reply that references the actual message content
3. **Routes**: books appointments for scheduling intent, escalates emergencies to the on-call tech within seconds, requests missing info, and filters spam

A daily owner report summarizes total leads, qualified leads, bookings, escalations, spam caught, and average response time. Human review at every step — nothing sends without approval.

## How we built it

- **Gemini 3.5 Flash via direct REST** (the new Interactions endpoint) with a model-probe fallback chain: `gemini-3.5-flash` → `gemini-3.5-flash-lite` → `gemini-3-flash-preview` → `gemini-flash-latest` → keyword fallback, so the agent survives model rotations
- **12-lead realistic test bench** spanning emergencies, scheduling, quotes, cross-selling, missing info, no-fit commercial work, and spam — classified at **0.965 average confidence** with **3.6s average latency** on the Gemini 3.5 family
- **Zero-dependency Python** (stdlib only) so any small business or MSP can deploy it on a $5 VPS or even a Raspberry Pi
- **Six editions from one core**: the same lead-recovery engine wrapped for six competition tracks (Gemini/ADK, Strands SDK, CockroachDB persistent memory, OpenSearch retrieval, and more)

## Challenges we ran into

- The official `google.generativeai` SDK is dead (deprecated + models retired for new users) — we rebuilt on raw REST, which turned out to be more robust than the SDK anyway
- Keyword matching calls everything "missing_information"; Gemini catches commercial-refrigeration no-fits, real emergencies vs. solicitation, and booking intent that keywords miss entirely
- Keeping latency under 4s per lead while extracting structured JSON from the model
- Building honest evaluation: every claim in this write-up is backed by a scripted run (`hackathon/gemini-agent-output.json` in the repo)

## Accomplishments we're proud of

- 12/12 leads correctly classified, avg confidence 0.965
- One codebase, six competition submissions
- $0 spent on infrastructure — the whole stack runs free-tier

## What we learned

- Structured-output prompting (schema-constrained JSON) is the difference between a demo and a product
- The fallback chain pattern (probe models at startup, degrade gracefully) is essential for anything built on preview models

## What's next for CallbackOps

- Live pilot with a San Diego HVAC operator (pipeline of 55 prospects)
- Voice channel via Gemini Live API
- Spanish-language support for San Diego's bilingual market
