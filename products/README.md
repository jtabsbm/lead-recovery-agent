# CallbackOps Digital Product Catalog

Three sellable digital products built from CallbackOps' real operating IP — the working lead-recovery service docs (offer.md, outreach.md, fulfillment.md) and the tested Gemini lead-classification agent (12/12 leads, avg confidence 0.947 on the verified run). $0 upfront to build; designed for Gumroad.

**Seller:** James Thompson · absbm14@gmail.com
**Honesty policy across all listings:** no fabricated testimonials, no invented statistics, no earnings claims. Every performance number cited traces to a run log shipped inside the product.

---

## Catalog

| # | Product | Price | Format | Dir |
|---|---------|-------|--------|-----|
| 1 | The Home-Service Lead Recovery Playbook | **$29** | Long-form guide (PDF) + copy-paste appendices | `lead-recovery-playbook/` |
| 2 | AI Lead Agent Starter Kit | **$79** | Python code + docs (zip) | `ai-lead-agent-starter-kit/` |
| 3 | Cold Outreach Pack for Home Services | **$19** | Template pack (PDF) | `cold-outreach-pack/` |

À la carte total: $127. Bundle opportunity: all three at $99 (future).

---

## 1. The Home-Service Lead Recovery Playbook — $29

**Files:** `PLAYBOOK.md` (the book) · `LISTING.md` (title, description, bullets, FAQ, pricing rationale)

A complete operating system for recovering missed calls, web forms, after-hours messages, and quiet quotes in home-service businesses. 15 chapters + 5 appendices: the seven failure modes, the speed-to-lead worksheet (own-numbers arithmetic, no borrowed stats), the 14-day baseline, the 13-column tracker, the missed-call SOP (4 attempts / 2 days / exact timings), the 5-touch/14-day follow-up cadence, the 8-script library, qualification checklist, routing table, escalation rules, where AI fits, and objection handling. Adapted from fulfillment.md + outreach.md, expanded with industry-standard practice.

**Key differentiator, stated in the listing:** no testimonials, no unsourced "78% of buyers" stats — the book teaches the reader to generate their own numbers via the baseline.

## 2. AI Lead Agent Starter Kit — $79

**Files:** `README.md` (setup) · `PROMPTS.md` (prompts + 5 trade variations) · `CUSTOMIZE.md` (adaptation guide) · `gemini_sdk_agent.py` · `gemini_lead_agent.py` · `sample-output.json` · `sample-output-rest-agent.json` · `requirements.txt` · `LISTING.md`

The actual working code: two tested agents (google-genai SDK-first with REST fallback chain and keyword safety net; full REST-path agent with status board + daily report), the system prompts and JSON schema, trade variations for HVAC/plumbing/electrical/roofing/general, the customization guide (categories, routing, price guardrails, confidence thresholds, integration patterns), and both verified run logs.

**Verified numbers used in copy (from `sample-output.json`, run 2026-08-15):** 12/12 leads classified in one run via google-genai SDK / gemini-3.5-flash; avg confidence 0.947 overall; 11 Gemini-classified leads averaged 0.969; 1 keyword fallback mid-run (per-lead engine/model logged). REST agent: avg confidence 0.965, avg response ~3.6s.

## 3. Cold Outreach Pack for Home Services — $19

**Files:** `OUTREACH-PACK.md` (the pack) · `LISTING.md`

The working B2B outreach SOP adapted from outreach.md, personalized for 5 trades (HVAC, plumbing, electrical, roofing, garage door): universal 3-touch sequence with exact copy, per-trade initial emails + observation prompts + objection scripts, phone opener, sample-audit template, 14-field tracker spec, bounce-recovery protocol, daily 10/5/5/1 cadence, diagnostics table, compliance notes (CAN-SPAM/CASL/GDPR).

---

## Status / next steps (Gumroad signup handled separately)

- [x] All product content written (this directory)
- [x] Code verified: both scripts py_compile clean; SDK agent re-run end-to-end at packaging time (keyword-fallback path exercised via REST per-lead fallback chain, JSON report written)
- [x] Listing copy written for all three (title, long description, bullets, FAQ, pricing rationale)
- [ ] Export PLAYBOOK.md and OUTREACH-PACK.md to PDF for delivery (pandoc or similar)
- [ ] Zip the starter-kit directory for delivery
- [ ] Gumroad account + listings live (browser-gated, handled later)
- [ ] Optional: $99 bundle listing

## Content integrity rules used throughout

1. Statistics: only numbers from our own verified run logs; "industry studies" language avoided entirely rather than cited loosely.
2. The 12-lead test used synthetic leads — every listing says so explicitly, and no revenue/recovery-rate claims are derived from it.
3. No testimonials exist, so none are quoted; the sales evidence story is the labeled sample audit + live role-play + baseline pilot (per offer.md).
4. Pricing ladders from learn ($29) → build ($79) → done-for-you service ($1,500 + $1,500/mo founding pilot per offer.md).
