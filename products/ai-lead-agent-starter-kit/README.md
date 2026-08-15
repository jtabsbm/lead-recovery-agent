# AI Lead Agent Starter Kit — Setup Guide

Classify, prioritize, and draft replies for inbound home-service leads with Google Gemini. Two tested agents, three engine paths, zero paid dependencies beyond a free Gemini API key.

**What was verified at build time (2026-08-15):** 12/12 synthetic leads classified in a single run through the `google-genai` SDK with model `gemini-3.5-flash` — overall average confidence **0.947** (the 11 leads classified by Gemini averaged **0.969**; one lead fell back to keyword classification mid-run). Full run log included as `sample-output.json`. The REST-path agent averaged **0.965** confidence with ~3.6s average response time on its 12-lead run (`sample-output-rest-agent.json`).

---

## What's in the kit

| File | What it is |
|---|---|
| `gemini_sdk_agent.py` | Primary agent. google-genai SDK first, REST fallback chain, keyword fallback so it never dies. Emits a JSON report. |
| `gemini_lead_agent.py` | Full agent with lead dataclasses, status board, routing, and daily report. REST-only (no SDK dependency). |
| `sample-output.json` | Verified run log: SDK path, 12 leads, per-lead category/confidence/reply/latency. |
| `sample-output-rest-agent.json` | Verified run log: REST-path agent, 12 leads. |
| `PROMPTS.md` | The system prompts, response schema, and variations per trade. |
| `CUSTOMIZE.md` | How to adapt business name, service area, categories, and routing to any trade. |
| `requirements.txt` | One optional dependency. |

Both agents run on Python 3.11+ with **zero required pip installs** — the SDK path is optional and the agents degrade gracefully without it.

---

## Setup in 5 minutes

### 1. Get a free Gemini API key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with any Google account and click **Create API key**
3. Copy the key (starts with `AIza...`)

The free tier is enough to test and run small batches. You are responsible for reading Google's current terms and rate limits for your usage.

### 2. Make the key available

Either export it in your shell (recommended):

```bash
export GEMINI_API_KEY="AIza...your-key..."
```

Or create a `.env` file **one directory above** the scripts (the SDK agent looks for `../.env` relative to its own location):

```
GEMINI_API_KEY=AIza...your-key...
```

> `gemini_sdk_agent.py` loads `GEMINI_API_KEY=` from `ROOT/.env` where `ROOT` is the parent of the script's folder. `gemini_lead_agent.py` reads only the environment variable — use `export` for that one. `GOOGLE_API_KEY` is accepted as an alternate name by both.

**Never hardcode the key in the scripts, commit it to git, or paste it into chat/shared docs.** If a key leaks, revoke it in AI Studio and create a new one.

### 3. Run it

```bash
# Primary agent (SDK path if google-genai installed, else REST, else keywords)
python3 gemini_sdk_agent.py --json my-run.json

# REST-path agent with status board and daily report
python3 gemini_lead_agent.py
```

Expected output: one line per lead with category, confidence, and latency, then a summary block and a JSON report file.

### 4. (Optional) install the official SDK for the best path

```bash
pip install google-genai
```

With the SDK installed and a key set, `gemini_sdk_agent.py` uses structured output (`responseSchema`) for the most reliable JSON. Without it, both agents call the Gemini REST API directly with `urllib` — no dependencies at all.

### 5. Feed it a real lead

In `gemini_lead_agent.py`, replace a synthetic tuple in `run_demo()`:

```python
agent.ingest("Jane Doe", "jane@email.com", "Hi, my water heater is leaking — can someone come today?", "web_form")
```

or call the SDK agent's `classify_lead()` from your own code (see `CUSTOMIZE.md` §4).

---

## How the engine chain works

```
google-genai SDK  →  REST fallback models  →  keyword fallback
(structured JSON)    (gemini-3.5-flash,       (always answers,
                      3.5-flash-lite,          lower confidence)
                      3-flash-preview,
                      flash-latest)
```

- The SDK agent probes models in order and uses the first one that answers.
- Any failure on a lead drops that lead to the keyword classifier — the run never crashes on a bad model name or a rate-limit blip.
- `engine` and `model` are recorded **per lead** in the JSON report, so you can always see which path handled what. Audit that field before trusting batch results.

## Reading a result

```json
{
  "name": "Elena Rodriguez",
  "category": "scheduling",
  "confidence": 0.98,
  "reply": "Hi Elena, this is Northside HVAC. We can certainly help... Tuesday 1:00 PM or 3:30 PM?",
  "reason": "The lead has a clear intent to book service for Tuesday afternoon.",
  "engine": "google-genai-sdk",
  "model": "gemini-3.5-flash",
  "latency_ms": 44221
}
```

- **category** → routing decision (see `route()` in the script).
- **confidence** → the model's self-reported certainty, not a guarantee of correctness. Below ~0.7, review manually.
- **reply** → a *draft* for a human to approve. The system prompt forbids inventing prices or diagnoses, but you should still read every customer-facing message before it goes out, especially in early weeks.

## Honest limits (read this)

- The included runs used **synthetic leads**. They demonstrate classification behavior, not revenue outcomes. No earnings or recovery-rate claims are made or implied.
- Latency in `sample-output.json` reached 44s on one lead and one lead hit the keyword fallback — expect occasional slow calls and always keep the fallback armed.
- Model names (`gemini-3.5-flash`, etc.) change over time; that's why both scripts carry a fallback list. If all REST models 404, update the lists at the top of each script from Google's current model page.
- This kit classifies and drafts. It does not send emails, make calls, or write to your CRM — wiring it to a channel (web form hook, email inbox, Zapier) is your integration step, and `CUSTOMIZE.md` §5 sketches the pattern.

## License / usage

Single-business license: use and modify the code for your own business or client work you personally deliver. Do not resell or redistribute the kit itself. No warranty — you are responsible for customer-facing wording, applicable telemarketing/messaging rules, and data handling in your jurisdiction.
