# Bug Bounty Candidate Findings — NO SUBMISSIONS MADE
Researcher: James Thompson (jamesthompson-sd) · Research date: 2026-08-15
Status: documented candidates only. Nothing submitted. Every item below needs a working PoC before reporting (both programs reject scanner-style/no-impact reports).

---

## Program 1: OPPO (hackerone.com/oppo_bbp) — handle is `oppo_bbp`, NOT `/oppo`

Policy verified 2026-08-15. Scope tiers: Low ($1–$10 low sev) / Moderate ($10–$20 low, $45–$80 med) / High ($15–$30 low) / Extremely High ($20–$45 low). Only assets explicitly listed are in scope. Required research header: `X-HackerOne-Research: <h1 username>` (used on all probes).

**Policy sections that matter for low-severity work:**
- Moderate #3: "plain-text password transmission over the HTTP when a HeyTap account is used for sign-in"
- Low #4: "clickjacking on input web pages containing sensitive information (a valid exploit must be provided)"
- Low #5: "inappropriate configuration settings for system/service maintenance and operations"
- Low #2: "minor information leakages" (path/SVN/PHP/exception/config leakage)
- Low #3: open redirect only if OPPO URL redirects to any non-OPPO domain with no prompt
- **NOT rewarded (NSI)**: mixed content, intranet IP/domain leaks (the `x-backend-host`/`x-gateway-host` internal hostnames seen on responses are explicitly NSI), scanner reports without proof of harm, CSRF on non-sensitive actions, meaningless clickjacking

### Candidate O-1: OPPO ad-alliance portal served in full over plain HTTP, no HTTPS redirect
- **URL:** `http://u.oppomobile.com/`
- **Scope:** listed as `https://u.oppomobile.com/` — High Level tier (in scope, eligible)
- **Observation (verified 2026-08-15):** plain-HTTP request returns **HTTP/1.1 200** with the full OPPO广告联盟 (OPPO Ad Alliance) portal HTML — no 301 to HTTPS, no HSTS header on the HTTPS side either. The portal has user login functionality (advertiser/publisher accounts). Nginx, `X-Backend-Host: 0115:80`.
- **Why it may be rewardable:** if the login form transmits credentials over HTTP (HeyTap SSO or portal credentials), it maps to **Moderate #3** ("plain-text password transmission over HTTP when a HeyTap account is used for sign-in", $45–$80) or **Low #2** (non-HeyTap account, $10–$20).
- **Gap to close before reporting:** capture the actual login POST from the HTTP origin and prove credentials go out unencrypted. Without that, this is "mixed content/NSI" territory — do NOT report as-is.
- **Severity if proven:** Moderate ($45–$80) or Low ($10–$20).

### Candidate O-2: Marketing-platform login page lacks all frame-busting + HSTS
- **URL:** `https://e-global.heytap.com/marketing/login`
- **Scope:** listed in-scope, Moderate Level tier (updated May 18, 2026)
- **Observation (verified 2026-08-15):** the credential page (title: 海外营销平台 "Overseas Marketing Platform", React SPA `/marketing/`) is served with **no X-Frame-Options, no CSP frame-ancestors, no HSTS, no Secure cookies** (no Set-Cookie at all at shell load). Response also exposes internal telemetry endpoints (`ums-telemetry-*.wanyol.com`, `ums-telemetry-sgp.heytapmobi.com`) — but note intranet/internal-endpoint leaks are NSI per policy, so the rewardable angle is only the clickjacking one.
- **Why it may be rewardable:** **Low #4** — "clickjacking on input web pages containing sensitive information" — a login/credential page is exactly an "input web page containing sensitive information". Policy demands a valid exploit (iframe-overlay PoC on the username/password fields).
- **Gap to close before reporting:** build the iframe PoC against the *rendered* login form (SPA — verify the form renders inside the iframe and inputs are clickable). Policy explicitly rejects "meaningless clickjacking" without exploit.
- **Severity if proven:** Low ($10–$20, Moderate tier asset).

### Candidate O-3: Session cookie missing Secure flag on open-platform portal
- **URL:** `https://developers.oppomobile.com/`
- **Scope:** listed in-scope, Low Level tier
- **Observation (verified 2026-08-15):** sets `openplat=<hash>; path=/; HttpOnly` — **no `Secure` attribute** — plus `region=IN` without HttpOnly/Secure. No HSTS on the response (plain HTTP 301s to HTTPS, so cookie theft needs an active MITM first — weak chain).
- **Why it may be rewardable (weak):** **Low #5** "inappropriate configuration settings" is the only hook; a session cookie without Secure on an auth'd developer portal is a config deficiency.
- **Honest risk:** OPPO rejects "scanner's meaningless vulnerability reports" without proof of harm. Only worth reporting bundled with a demonstrated MITM cookie-capture PoC (policy Low #4 mentions MITM-based issues with valid PoC). Otherwise expect NSI.
- **Severity if proven:** Low ($1–$10, Low tier).

### OPPO negatives checked (do not report):
- `id.oppo.com` / `id.heytap.com` (Extremely High tier): HTTP→HTTPS 301 works, CSP frame-ancestors present. No issue.
- `open.oppomobile.com`: despite being listed as `http://` in scope, it 301s to HTTPS properly.
- Internal hostname leakage via `x-backend-host`/`x-gateway-host` on many OPPO responses: **explicitly NSI** ("leaking of IP addresses or domain names in the intranet").
- Mixed content anywhere: **explicitly NSI**.
- `u.oppomobile.com` open-redirect params (`?url=`, `?to=`, `/redirect`, `/r`, `/go`): all returned 200/404 without redirecting — no open redirect found.

---

## Program 2: Bumble (hackerone.com/bumble)

Policy verified 2026-08-15. 55 assets (50 in-scope). Bounties: Low $10–$200 (chatdate.app $10–$50), Medium $50–$600, domain-takeover/dangling-domain findings **accepted at fixed $100**.
**Critical exclusions:** missing security headers/cookie flags without demonstrated exploitability; data enumeration without sensitive exposure; generic rate-limit issues; clickjacking on static pages.

### Candidate B-1: Four in-scope Geneva staging hostnames do not resolve (dangling-domain policy section)
- **URLs:** `web.geneva-staging.com`, `social.geneva-staging.com`, `presence.geneva-staging.com`, `go.geneva-staging.com` (all listed in-scope, Critical-max, eligible; `.chat` twins resolve fine)
- **Observation (verified 2026-08-15):** all four return **NXDOMAIN** — no A/CNAME/NS records. Sibling staging hosts (www/app/api/sockets/router/payments/links/gateway/deeplinks) are live behind Cloudflare. This is stale DNS/infrastructure drift on a staging cluster the program actively pays on (7 resolved reports already on the geneva-staging assets).
- **Why it may be rewardable:** Bumble policy section **"Dangling Domains / Domain Takeover — Although these issues are accepted, valid findings will receive a fixed bounty of $100."** Unresolving in-scope assets are the exact subject of that section.
- **Honest caveat (state this in any report):** no dangling CNAME/NS to a claimable third-party service was found, so **no takeover is demonstrated** — this is a dangling/unregistered-asset report, not a proven takeover. Bumble may still grade it Informative; the $100 fixed bounty applies to *valid* findings. Report once, all four hosts in one report.
- **Severity if accepted:** fixed $100.

### Candidate B-2 (observation only — likely NOT rewardable, keep as context):
- `links.geneva-staging.com` root 301s to a Notion page (`notion.so/genevahq/...`) with `access-control-allow-origin: *`. Bumble's exclusions (no sensitive data, intended redirect behavior) make this Informative at best. Logged for context only — do not report.

### Bumble negatives checked (do not report):
- `badoo.com/signin/`, `m.badoo.com`, `translate.badoo.com`, `corp.badoo.com`, `chatdate.app`, `hotornot.com`: all ship full CSP + HSTS preload + XFO/frame-ancestors. Cookie flags on `device_id` are non-session identifiers (no Secure/HttpOnly needed for impact per policy). Hardened — no honest finding.
- `bma.bumble.com`: TLS connections failed from this network (likely geo-restriction) — untested, not a finding.

---

## PoC status (Aug 15, afternoon)
- **O-2 PoC BUILT**: `recon/clickjacking-poc.html` — target re-verified today: HTTP 200 with NO XFO/CSP-frame-ancestors/HSTS. Load the PoC locally; if the SPA login form renders + accepts input in-frame, O-2 is report-ready.
- **B-1 forensics done**: geneva-staging.com is REGISTERED until 2027-03-31 (Amazon Registrar, Route53 NS). No claimable CNAME → this is a dangling-asset report (their $100 fixed section), NOT a takeover. Report as-is, honestly framed, all 4 hosts in one report.
- **Submission blocker**: H1 account needs TOTP re-setup (2FA secret lost in .env wipe). James: 1 min at hackerone.com → Settings → Security → re-enable 2FA.

## Totals
- **OPPO (oppo_bbp): 3 candidate findings** (O-1, O-2, O-3)
- **Bumble: 1 candidate finding** (B-1, covering 4 in-scope hostnames)
- **Grand total: 4 candidate findings, 0 submitted**

## Next actions (in order)
1. O-1: verify login POST over http://u.oppomobile.com (needs a test account; use `jamesthompson-sd@wearehackerone.com` alias per OPPO test plan).
2. O-2: build iframe-clickjacking PoC on e-global login form.
3. B-1: check the 4 NXDOMAIN hosts periodically for newly dangling CNAMEs (real takeover = stronger claim); file the single dangling-domain report as-is if staging stays broken.
4. Re-check TOTP on the H1 account before any submission (2FA re-setup pending).

## Evidence files
- Recon outputs in `/Users/wendell/zero-cash-revenue-engine/recon/`
- Raw policy/scope text: `h1_oppo_policy.txt`, `h1_oppo_scope_full.txt`, `h1_bumble_full.txt`, `h1_bumble_scope.txt` (in browser workspace `~/.hermes/profiles/side/cache/browser-use/workspace/sa-0-3bf04a25/`)
