# Zero-Capital Crypto Earning Lanes — Verified Aug 15, 2026

Method: terminal-only fetches via `curl` + `r.jina.ai` (no browser). Raw evidence in `crypto_fetch/`. Prior session's notes in `crypto-lanes-verified.md` were cross-checked, not blindly copied.

**Bottom line:** Nothing here prints money. The only lanes with verified open cash payouts and zero capital requirement are (a) skill-based bounties/bug bounties and (b) content bounties with brutal competition. Learn-to-earn pays a few dollars total. Testnet farming in Aug 2026 is a lottery with no confirmed payer.

---

## Realism ranking (most → least realistic for James, $0 capital, today)

| # | Lane | Verified status | Honest expected value |
|---|------|-----------------|----------------------|
| 1 | Superteam Earn bounties | ✅ 21 open, $150–$10K USDC/USDG, live API data | $0–500/mo; low-sub dev bounties are the good EV, crowded content ones are ~$2–5 per submitted entry |
| 2 | Immunefi low-sev web/app bugs | ✅ 186 programs live; own program pays flat $1,000 LOW web/app | $0 for months until first valid bug; then $1K+ per finding; requires real web2 sec skills |
| 3 | Cantina bounties | ✅ 52 live, $52.9M historically paid | Expert-tier; $0 until a valid high/critical find |
| 4 | Audit contests (Code4rena/Sherlock/Codehawks) | ⚠️ Code4rena: ZERO open now (K2 $135K in judging); Cantina comp invite-only; Codehawks 1 public (7.25 ETH) | $0 unless a contest is open and you're skilled; check weekly |
| 5 | Gitcoin GG24 grants | ✅ Applications + donations open | Only if James ships a public-good project; not task income; grant sizes vary widely |
| 6 | Learn-to-earn (Coinbase / Binance) | ✅ Exists but small / ⚠️ login-gated | Coinbase: a few $ total, one-time; Binance: not available to US users |
| 7 | Layer3 quests | ✅ Site live; rewards are CUBE points → "closer to airdrops" | ~$0 cash now; speculative points |
| 8 | Dework tasks | ❌ Could not verify (JS-only explore page renders empty via terminal) | Unknown; treat as unverified |
| 9 | Testnet incentive farming | ❌ No confirmed-paying program verified live in Aug 2026 | $0–3/hr expected value; the famous payers already paid |

---

## 1. Immunefi — bug bounties (skill gate: real)

**Verified live:** 186 bounty programs listed (page dated Aug 15, 2026, 16:00 UTC). Filters include "Paid Submissions", "PoC Not Required", "KYC Not Required".

**Lowest-barrier entry points found:**
- **Immunefi's own program** (`immunefi.com/bug-bounty/immunefi`): Web/App **Low = flat $1,000**, Medium = $2,000, High = $2,000–5,000. Total paid $68.9K, **median resolution 9 hours**, KYC required, PoC required. Target: their website/app, not Solidity.
- **The Graph**: max $50K (Critical $15K min), **$1.5M total paid, 1-day median resolution**, KYC not required. Fast-paying, established.
- Vault-funded programs (SSV $320.7k vault, ENS, Lombard) guarantee payout funds are escrowed.

**Honest note:** every program still requires genuine security skill. "Docs bugs" are not a listed paid category anywhere on Immunefi — that lane does not exist as advertised. Web2/low-sev findings are the realistic entry, at ~$1K flat each, found rarely. This is a career skill, not a weekly paycheck.

## 2. Web3 content/bounty platforms

- **Superteam Earn (earn.superteam.fun)** — ✅ REAL AND PAYING NOW. 21 open bounties verified via public API (Aug 15, 2026). Examples: $10K Solana Summit content (1 submission), $1,000 Solana dev challenge (2 subs), $1,000 ecosystem report (0 subs), $5K web2→onchain ideas (15 subs), plus many $150–$700 X-thread/video bounties with 70–314 submissions. USDC/USDG paid to winners. **Strategy that matters: filter for <$10 submissions and match skills (the dev/report bounties), ignore the 300-submission tweet contests.**
- **Gitcoin** — ✅ GG24 is live ("Applications open, Donations open" at grants.gitcoin.co). It's **builder grants**, not task bounties: James needs a public-goods project. Not quick income; old /grants/ URL is 404, program moved.
- **Dework** — homepage live but explore/tasks page renders empty without JS; **unverified** whether paid tasks flow in 2026. Don't count on it.
- **Layer3** — live; rewards are CUBE NFTs/points that "bring you closer to rewards, airdrops, and status." Speculative, no cash. (Solana/Polygon "docs bounties": nothing found on official properties paying for docs today; Superteam has absorbed most of that energy on Solana.)
- **Code4rena / Sherlock / Codehawks**: C4 has zero open contests (K2 $135K ended May 27, judging; nothing since). Sherlock page moved/404 via terminal. Codehawks has 1 public contest (BattleChain, 7.25 ETH) + First Flights.

## 3. Testnet incentives — honest verdict: no confirmed payer live

- **Historical confirmed payers** (why the lane is famous): zkSync Era (Codehawks-era $500K+ audit pool; ZKS airdrop), LayerZero (retroactive airdrop), Scroll, Celestia, Taiko, ZetaChain — **all already launched tokens and paid**; their testnet windows are closed.
- **Aug 2026 roundups** (tradersunion, airdrops.io) push Monad, ZetaChain, Plume, Pharos, etc. as "testnet airdrops 2026" — none show a confirmed, on-chain payout to ordinary participants; they're repeated-snapshot engagement schemes. airdrops.io's own live list is Discord/XP check-in tasks (near-zero value).
- **Realism: $0–3/hr lottery ticket.** A testnet *bug report* that triages into a bounty is worth more than 100 hours of quest-clicking, and needs no capital either.

## 4. Learn-to-earn

- **Coinbase**: /earn is now staking/USDC/lending (all require capital — excluded). "Learning Rewards" (quiz) still exists at coinbase.com/learning-rewards but requires login to see eligibility; historically ~$1–3 per lesson, limited campaigns, one-time. **Realistic total: under $10, once.** US-eligible.
- **Binance Learn & Earn**: live at binance.com/en/academy/learn-and-earn (TURTLE, Bitcoin Basics courses visible) but eligibility is login-gated **and Binance global doesn't serve US users** (Binance.US is a separate, stripped product). **Effectively unavailable for James.**

## 5. Paid smart-contract test/audit feedback, no capital

- **Cantina**: 52 always-on bounties live, $66M available / $52.9M paid historically — real, expert-tier. Live competition (Royco $30K) is invite-only.
- **Codehawks First Flights** (#35–59, beginner-friendly): pay **100 EXP points, not cash** — but they're the free on-ramp to paid contests (the ZKsync Era contest that paid $500K was on the same platform).
- **Immunefi "Paid Submissions" filter**: some programs pay even for out-of-scope-quality reports; rare.
- Honest EV for a beginner: $0 for the first 1–3 months of study; First Flights + Superteam dev bounties are the free training ground.

---

## Hard rules honored
No lane above requires upfront capital, deposits, node licenses, or real-money gas (Superteam pays gas-free USDC; bounties pay on delivery). Excluded on sight: "buy a node license" schemes, trading/arbitrage (needs capital), seed-phrase or deposit-required "tasks". If a lane realistically pays ~$5/mo, the table says so.

## Recommended action for James (this week)
1. Create Superteam Earn profile; submit to the **2 low-submission $1,000 bounties** (dev challenge / ecosystem report) before Aug 23–Sep 1 deadlines. Best real EV found.
2. In parallel, run 2–3 Codehawks First Flights to test whether security work suits him (free).
3. If any bug is found anywhere: file on Immunefi's own program (web2 low-sev, flat $1K, 9-hr median triage) or The Graph ($1.5M paid, 1-day median).
4. Ignore: testnet farming, Layer3 points, tweet-storm bounties with 300 submissions, learn-to-earn (except as a 30-min Coinbase one-off).

*Sources fetched Aug 15, 2026 → `crypto_fetch/`: immunefi_explore.md, immunefi_own_program.md, immunefi_thegraph.md, superteam_api.json, cantina_competitions.md, code4rena_active.md, codehawks_firstflights.md, gitcoin_grants_sub.md, binance_academy_le.md, coinbase_earn.md, coinbase_learning_rewards.md, layer3.md, dework.md, testnet_roundup.md, airdrops_testnets.md.*
