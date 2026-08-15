# Product Listing — AI Lead Agent Starter Kit

## Title

**AI Lead Agent Starter Kit — classify, prioritize, and draft replies to inbound leads with Gemini**

## Price

**$79**

## Gumroad description (long)

Every inbound lead your home-service business receives has to be triaged: is this an emergency? a price shopper? spam? out of your service area? Right now that triage happens in someone's head, between jobs, hours after the message arrived — or not at all.

This kit is the exact classification agent we built and ran for our own lead-recovery operation, packaged for you to install and adapt. It reads an inbound lead message and returns a structured decision: category, confidence, a customer-ready draft reply, and the routing action to take next.

**What's inside:**

- Two complete, tested Python agents — an SDK-first agent with a REST fallback chain, and a full REST-path agent with lead dataclasses, status board, routing, and daily reporting
- The exact system prompts and JSON response schema, with ready-to-edit variations for HVAC, plumbing, electrical, roofing, and a general template
- A customization guide: business context, categories, routing actions, price-range guardrails, and confidence-threshold policy
- Two verified run logs so you can see exactly what output looks like before you run anything
- Zero required dependencies. Runs on Python 3.11+. A free Gemini API key is all you need.

**Verified, not hypothetical.** At build time we ran the SDK agent against 12 realistic leads covering every category: 12/12 classified in one run, average confidence 0.947 overall — 0.969 across the 11 leads Gemini handled, with 1 lead served by the keyword fallback mid-run (per-lead engine and model are logged in the report so you can always audit which path did what). Full logs included. These were synthetic leads demonstrating classification behavior — no revenue or recovery-rate claims are made.

**The engine chain never dies on you:** google-genai SDK → REST fallback across current Gemini models → keyword classifier. A rate-limit blip or a retired model name degrades a single lead to fallback; the run completes and tells you exactly which rows to re-check.

**Honest limits, stated plainly:** the kit classifies and drafts — it does not send anything. Emergencies always route to a human. It's tested on synthetic leads, and you should review 100% of drafts in your first weeks. Full limits are printed in the README.

For agencies and consultants: this is also the fastest way to put a working lead-triage demo in front of a home-service client — run the included sample leads live on a discovery call.

## Bullets (for the sales page)

- Two tested Python agents: SDK-first + REST fallback chain + keyword safety net
- Structured output every time: category, confidence, draft reply, routing action
- Verified 12-lead run log included — avg confidence 0.947, per-lead engine/model audit trail
- Prompt variations for HVAC, plumbing, electrical, roofing + general template
- Customization guide: categories, routing, price guardrails, confidence thresholds
- Zero required dependencies; free Gemini API key; Python 3.11+
- Integration patterns for web forms, email inboxes, Zapier, and missed-call alerts
- Honest-scope license: use for your business or your own client work; no reselling the kit

## FAQ

**Q: Do I need to know how to code?**
A: You need to be comfortable running a Python script from a terminal and editing a text file. If you can follow a README, you can run this. If you can edit a prompt, you can customize it. Non-technical owners often pair this with a technical friend or VA for the initial setup — the README is written for exactly that handoff.

**Q: What does it cost to run?**
A: A free Gemini API key from Google AI Studio covers testing and small batches. Heavier use depends on Google's current pricing and rate limits, which change — check them before production use.

**Q: Will it work outside the US?**
A: The code is region-agnostic; the prompts ship in English with US examples. The system prompt is the only place locale lives — swap the business context lines and it adapts.

**Q: Does it send emails or texts to my leads?**
A: No — deliberately. It classifies, drafts, and routes. A human approves customer-facing messages. The customization guide shows how to wire it to a web form, inbox, or Zapier when you're ready, and recommends keeping a human on the send button.

**Q: What if Gemini changes their model names?**
A: That's why both agents carry a fallback model list and per-lead engine logging. When models retire, update one list at the top of the script — the troubleshooting table covers it.

**Q: Can I use it for a trade other than the five listed?**
A: Yes. The general template in PROMPTS.md works for any service business; the worked plumbing example shows the full adaptation path.

**Q: Is this an agency? Will you run it for me?**
A: This is a DIY kit. If you'd rather have someone run lead recovery as a done-for-you service, that's a different engagement — contact details are on file.

**Q: Refunds?**
A: If the kit doesn't run as documented on Python 3.11+ with a valid API key, email within 14 days with your error output and we'll refund or fix.

## Pricing rationale (internal)

- **$79** anchors below the psychological $100 line for a code product while pricing it as a tool, not an ebook. The kit contains two runnable scripts, verified run logs, prompts, and docs — comparable DIY automation kits list $49–$149.
- It captures the "technical owner / agency" segment above the playbook's $29, while the done-for-you service (from our offer docs: $1,500 setup + $1,500/mo founding pilot) remains the upsell for non-technical buyers. The ladder reads: learn ($29) → build ($79) → have us run it (service).
- Value anchor from our own operating docs: one recovered job in most home-service trades exceeds $79 many times over. We don't promise recovery rates — we price against the cost of the problem, not the cost of production.
- Gumroad fees (~9% + $0.30) leave ~$71/net at this price point — fine for a $0-upfront catalog.
