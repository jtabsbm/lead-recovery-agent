# XPRIZE Build with Gemini — Submission Package
Deadline: Aug 17, 2026 1:00 PM PDT (Monday)

## Entry: CallbackOps — AI-operated missed-lead recovery business

XPRIZE rules require an "AI-operated business": the AI must run core operations,
not just assist. CallbackOps qualifies:
- Gemini classifies every inbound lead (quote/urgent/complaint/spam) with
  natural-language understanding
- Gemini drafts every recovery reply in the business's approved tone
- The agent decides routing (book/escalate/respond/discard) autonomously
- Humans review drafts before sending (safety, not operation)

## What we have (verifiable)
- Working classifier agent (gemini_lead_agent.py) — keyword fallback verified,
  Gemini path ready (needs API key)
- 4 agent editions (Gemini/Strands/CRDB/OpenSearch) sharing one core
- 34 real businesses contacted — real pipeline activity, real user (James)
- GitHub repos with commit history proving build timeline

## What XPRIZE likely requires (per Devpost form)
- Working demo (video) — script ready in demo-video-script.md
- Description of the AI-operated business model
- Evidence of real usage (our 34-contact pipeline is evidence of operations,
  though the SaaS itself has no paying users yet — be honest about stage)

## Submission checklist
- [ ] Gemini API key (AI Studio — blocked on Chrome permission prompt)
- [ ] Run gemini_lead_agent.py with real API, capture output
- [ ] Record 3-min demo video
- [ ] Fill Devpost submission form at devpost.com/submit-to/29541
- [ ] Submit before Aug 17 1:00 PM PDT
