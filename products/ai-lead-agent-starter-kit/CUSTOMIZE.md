# Customization Guide — AI Lead Agent Starter Kit

The agents ship configured for "Northside HVAC" in San Diego. This guide adapts them to your business in under an hour, and sketches how to wire them to real lead sources.

---

## 1. The five things to change first

### Business name and service area

`gemini_lead_agent.py` — constructor defaults:

```python
agent = GeminiLeadRecoveryAgent(
    business_name="Your Business Name",
    service_area=["Your Metro", "Suburb A", "Suburb B"],
)
```

The service area matters more than the name: the classifier uses it to decide `no_fit` for out-of-area leads. List the towns you actually serve.

`gemini_sdk_agent.py` — edit the `SYSTEM_PROMPT` business context lines (see PROMPTS.md §1) and the `build_leads()` sample set if you want the demo to match your trade.

### Categories

The routing table is the `route()` dict in `gemini_sdk_agent.py`:

```python
def route(category: str) -> str:
    return {
        "emergency": "ESCALATE to on-call tech (SMS + call)",
        "scheduling": "BOOK: propose 2 time slots",
        ...
    }.get(category, "REVIEW manually")
```

Add or rename categories in three places, keeping them consistent: the system prompt's category list, the `SCHEMA` enum, and `route()`. If they drift apart, the model will return a category your router doesn't know and it falls to "REVIEW manually" — annoying, not fatal.

### Routing actions

Make `route()` return what your operation actually does. Examples:

```python
"emergency": "CALL the on-call phone within 5 minutes",
"scheduling": "Send the booking link: https://cal.com/yourbiz/30min",
"quote": "Send the estimate-range sheet + offer free on-site visit",
"spam": "Archive, no reply",
```

### Price-range guardrails

The prompt says "give ranges only." Give the model your real ranges so drafts are useful: add a line like `Typical ranges: mini-split install $3.5k-$7k; system swap $6k-$12k; tune-up $89-$150.` to the system prompt. Never remove the "never invent prices" rule — replace vague with bounded.

### Fallback keywords

`classify_keyword()` in both scripts is the safety net when Gemini is unreachable. Replace its keyword lists with your trade's terms so even the degraded path routes sensibly. It's dumb matching — keep it that way; it's a fallback, not a feature.

## 2. Adapt to another trade (worked example: plumbing)

1. Rewrite the system prompt's first block with the Plumbing variation from PROMPTS.md §4.
2. Replace category hints: burst pipe / gas smell / sewage backup → emergency; repipe / water heater → quote.
3. Update `route()` strings to your dispatch habits.
4. Replace the 12 synthetic leads in `build_leads()` / `run_demo()` with 12 messages your business actually receives (redact real customer details first).
5. Run and read the JSON report: every category should match what your best dispatcher would do. Where it doesn't, fix the prompt, not the code.

## 3. Confidence thresholds and human review

Verified run data: 11 Gemini-classified leads averaged 0.969 confidence; the keyword fallback answers in the 0.6–0.9 range.

Suggested policy (from our operating docs):

- **≥ 0.90** — auto-draft is fine; human glance before send.
- **0.70–0.89** — human reads the message and the draft before any send.
- **< 0.70** — treat as manual: the draft is a suggestion only.
- **Always escalate emergencies to a human regardless of confidence.** The agent drafting "please leave the house and call 911" is correct behavior, but a human must own what happens next. Never auto-send emergency replies.

Confidence is the model's self-report, not a correctness guarantee. In your first weeks, review 100% of drafts and lower the auto threshold only as trust is earned from your own data.

## 3b. Protecting customer data (do this before real leads)

- Redact or mask contact details in any lead text you paste into prompts, logs, or demo files.
- Keep API calls to Google's Generative Language API only; don't add third-party loggers that see lead bodies.
- Follow Google's current terms for the Gemini API on personal data; if you're in the EU/UK or handle sensitive data, review GDPR/UK GDPR obligations first.
- Store run reports (they contain lead text) somewhere access-controlled; delete them on a schedule.

## 4. Calling the classifier from your own code

The classifier is a plain object — reuse it anywhere:

```python
from gemini_lead_agent import GeminiClassifier

c = GeminiClassifier()          # picks up GEMINI_API_KEY from the environment
result = c.classify(
    "Hi, our water heater is leaking — someone available today?",
    business_name="Your Biz Plumbing",
    service_area=["Your Metro", "Suburb A"],
)
print(result["category"], result["urgency"], result["draft_reply"])
```

For the SDK agent, import and drive `classify_lead` + `route`:

```python
import gemini_sdk_agent as sdk
engine, client = sdk.pick_engine()
r = sdk.classify_lead({"id": 1, "name": "Jane", "channel": "web form",
                       "message": "Furnace is making a banging noise."}, engine, client)
print(r["category"], sdk.route(r["category"]))
```

## 5. Wiring it to a real lead source (pattern)

The kit is intentionally channel-agnostic. The generic integration:

```
lead source → your handler → agent.classify() → route() → human review → send
```

- **Web form** (Wix/Squarespace/WordPress): point the form's webhook at a small Flask/FastAPI receiver you host; call the classifier; write the row + draft to a sheet; email yourself escalations.
- **Email inbox**: poll with IMAP (e.g. a cron job every 2 minutes), classify unread messages from your lead alias, mark processed.
- **Zapier/Make**: Webhooks by Zapier → your endpoint, or use Code by Zapier to run the REST call directly with the prompt from PROMPTS.md.
- **Missed-call alerts**: if your phone system can email/SMS on missed call, that notification becomes the lead event — often the row is just "missed call, no voicemail," which classifies as missing_information and routes to a callback task, which is exactly right.

Start manual-first: log leads to the sheet with drafts for a week before automating sends. When you do automate, automate the *logging and drafting*, keep a human on the *send* button for anything customer-facing.

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| "Gemini: no API key set" banner | `export GEMINI_API_KEY=...` (or `../.env` for the SDK agent). |
| All REST models fail | Model names retired — update `GEMINI_MODELS` / `REST_MODELS` from Google's current models page. |
| Results are JSON with markdown fences | You're on a path without schema enforcement; parse defensively or install `google-genai` for the SDK path. |
| Categories don't match routing | Prompt enum, `SCHEMA`, and `route()` drifted apart — realign the three. |
| Confidence always ~1.0 | Prompt is too easy or leading; add harder boundary cases to your test set (out-of-area, commercial, vague one-liners). |
| One lead took 40+ seconds | Normal occasionally; the chain retries the next model on failure. For batches, run leads concurrently or off-peak. |
| Keyword fallback firing often | Check quota/rate limits in AI Studio; the fallback means every Gemini path failed. |
