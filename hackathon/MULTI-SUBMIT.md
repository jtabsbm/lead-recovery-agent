# One Codebase → Three Hackathons

The Lead Recovery Agent is deliberately architected so a single core (`tools.py`
logic: ingest → classify → route → report) can be wrapped three ways for three
August–September 2026 competitions. Judges in each track see a native, track-specific
entry — not a reused project shoehorned in.

| Competition | Deadline | Wrap | File | Model |
|---|---|---|---|--- |
| All Things Agentic (Google Cloud) | Aug 31 | Gemini + ADK-style classifier | `gemini_lead_agent.py` | Gemini 1.5 Flash (falls back to keywords) |
| Agentic Cinema | Sep 7 | Production-workflow adaptation | `screen_agent.py` | Screenplay structure analysis |
| Agents for Humans (Strands SDK) | Sep 14 | Strands `@tool` agent | `strands_lead_agent.py` | Local Ollama qwen2.5:7b (zero-credential) |

## Shared core (all three use this)

1. **ingest** — log lead from any channel (web form, missed call, SMS, after-hours)
2. **classify** — category + urgency + missing info + draft reply + confidence
3. **route** — book / escalate / respond / close / discard-spam
4. **report** — owner-facing daily summary with counts and drafts

## Per-track story (what judges are told)

- **All Things Agentic:** "Gemini 1.5 Flash classifies every missed lead in <2s and
  drafts an approved-tone reply; $1,000 GenAI App Builder credit powers deployment."
- **Agents for Humans:** "The same workflow as a Strands agent with four @tool
  functions, running on a fully local Ollama model — no cloud credentials, human
  reviews every draft before it sends."
- **Agentic Cinema:** "The classify→route pattern applied to screenplay submissions:
  structure analysis, coverage drafting, and pass/consider/recommend routing for
  indie filmmakers drowning in unread scripts."

## Rules check before each submit

- [ ] Confirm each competition's rules permit shared code across entries
- [ ] Customize each Devpost write-up around that track's story
- [ ] Record a track-specific 2–3 min demo video (script: `demo-video-script.md`)
- [ ] Tag the correct repo/commit per submission
