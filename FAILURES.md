# Failure & Lessons Log — Zero-Cash Revenue Engine
Running record of every failure, error, blocker, and stopping point. Purpose: pattern-spotting, future prevention, and honest accounting. Newest entries at the bottom.

Format: `## [date time] AREA — what failed → root cause → fix/prevention`

---

## Aug 14, 2026 (Day 1)

### Email infrastructure
- **~10 of 30 outreach emails bounced** ("Address not found") → root cause: guessed `info@domain.com` addresses instead of verifying → fix: only send to verified addresses found on sites/forms; built bounce-fix queue with real emails
- **Gmail session lost mid-session** → root cause: subagent Google OAuth flows disrupted the main session cookies → fix: isolated worker browsers for subagents; never let subagents touch the default session
- **Himalaya CLI email failed** ("No backend matching 'auto'") → abandoned CLI email path; browser Gmail works

### Browser automation
- **Subagents fought over the same browser tab** (repeated hijacks — Upwork agent, Devpost agent, Kaggle agent all grabbing the active tab) → root cause: all shared one Chrome instance → fix: dedicated Chrome per worker (parallel-browser-workers skill), one browser per subagent, browser access by explicit grant only
- **Chrome "Allow remote debugging" permission prompts** kept interrupting → root cause: attaching to user's main Chrome requires prompt → fix: dedicated instances with `--remote-debugging-port` + separate user-data-dir never prompt
- **macOS screen capture failed** ("could not create image from display") → worked around with DOM-text extraction instead of screenshots

### Platform signups
- **DataAnnotation blocked** at reCAPTCHA (human-verification wall) — correctly stopped, no bypass attempted
- **Contra blocked** at password/phone/consent — no fabricated credentials
- **Outlier** not completed (identity verification + assessments required)
- **CRDB signup**: email path → hidden reCAPTCHA; Google OAuth → popup blocked → `window.open` override got to consent, but Auth0 callback needs real `window.opener` handshake → hard technical wall for that flow
- **Prolific** reached profile step, ran out of iterations amid tab instability

### Git/infra
- **GitHub push 403** ("denied to namenotfound-ai") → root cause: credential helper had wrong account active → fix: check `gh auth status` before pushing; later embedded token in remote URL (then removed it for security)

---

## Aug 15, 2026 (Day 2)

### CRITICAL: .env file wiped
- **`~/zero-cash-revenue-engine/.env` truncated to 0 bytes** → root cause: my own Python one-liner did `open(f,'w')` (which truncates immediately) before reading the content it intended to write back → lost: Delphi wallet key (old, unfunded — harmless), H1 TOTP secret (needs manual re-setup), Gemini key (re-added from chat history)
- **Prevention rule:** NEVER open config files for writing in a read-modify-write one-liner. Write to temp file, verify, then move. For .env edits, append or rewrite from known values only.

### Delphi competition
- **Wallet registration took 6+ wizard attempts** → root cause: (1) misread "Agent name" field as second wallet field; (2) `fill_input` appends rather than replaces on some frameworks — must clear first; (3) React modals need full pointer-event sequences (pointerdown/up + mousedown/up + click), plain `.click()` silently fails; (4) final submit button was hidden INSIDE the modal ("Register as Hacker" appears in modal footer, not just Yes/No)
- **Lost first wallet key** (see .env wipe above) → had to unregister and re-register with new wallet — the Unregister button existed, luckily
- **pk910 PoW faucet: INVALID_CAPTCHA** → captcha wall, correctly stopped; also QuickNode/Alchemy faucets require 0.001+ mainnet ETH (anti-bot) — documented for James's manual 2-min task
- **DoraHacks full-site 502** mid-registration → waited out; site recovered
- **quoteBuy reverts** (`SharesOutBelowMinDelta` then `0x5fca91fa`) → first: min shares is 0.01 (1e16 wei), not 0.001; second: undecoded revert — suspected allowlist gating on competition markets; unresolved, will test with real buy when TST funds

### Devpost XPRIZE submission
- **Submission stuck at 3/5 steps across 6+ attempts** → root causes: (1) the "additional info" form is a 38-field business questionnaire, not the simple form it first appeared; (2) my JS value-setter fills didn't persist server-side on ~half the fields — only native fill_input fills survived the round-trip; (3) the form re-renders on every save, invalidating element references mid-batch; (4) the T&C checkbox click triggered navigation, resetting it
- **Resolution:** documented all field answers in xprize-final-steps.md for a 5-minute manual finish. Lesson: when a form fights automation this hard, cut losses and prepare a manual-finish kit instead of attempt #7.

### GitHub migration (TyrannicAwe → jtabsbm)
- **Cross-account repo transfer API returned success but silently didn't transfer** (404 after "transferred" responses) → root cause: transfers to an account without verified email get auto-cancelled; API still returns 200/202 → fix: mirror-push to fresh repos under jtabsbm instead. Lesson: verify side effects, never trust a success response alone.
- **Push 403 with new token** → root cause: macOS keychain credential helper (holding TyrannicAwe creds) intercepted before GIT_ASKPASS → fix: `git -c credential.helper= push` with explicit askpass. Pattern saved to memory.
- **Upwork banned by James mid-session** → immediately retired lane, deleted profile content, cleaned action lists, saved rule to memory.

### Research/delegation
- **Subagent 429 "Insufficient balance"** killed a whole 3-task batch → provider balance ran out; batch re-dispatched later successfully. Lesson: check delegation budget before fan-outs.
- **One subagent died with API timeout** (90s no response) on the micro-products task → I built the two products directly instead. Lesson: for simple deliverables, direct work beats delegation reliability.
- **Task 2 of one batch passed as string instead of object** ("Task 2 must be an object, got str") → fixed by structured resubmit.
- **crypto.jobs listings mostly stale** (460–1,075 days old) → the "$120K/yr crypto jobs" lane needs live-listing verification before application effort.
- **Code4rena winding down entirely** (2 closed contests, nothing live) → security-contest lane pivots to Sherlock/lablab watching only.

### Vision/analysis
- **vision_analyze returned 400** ("messages.content.type invalid, allowed: ['text']") → active model has no vision → all browser work is DOM-text-first (page_info/js/AX tree), never screenshot-dependent.

---

## Recurring Patterns (read before big pushes)

1. **React/modern forms defeat synthetic events** — use native fill_input + full pointer-event sequences + verify persistence after save. If a form resets twice, build a manual kit.
2. **Verify side effects** — success responses lie (repo transfers, form saves). Always confirm the resulting state.
3. **One .env mistake costs hours** — append-only edits, temp-file rewrites, never read-modify-write in one line.
4. **Isolation prevents interference** — one browser per worker, one lane per subagent, browser access by grant.
5. **Captcha/passkey/2FA = human wall** — stop, document, queue for James. Never bypass, never fabricate.
6. **Delegation is for research, not deliverables** — mechanical builds are faster direct; fan-outs shine on parallel info-gathering.
7. **Cut losses on fight-the-form battles** — after ~3 failed attempts on any UI automation, document state + prepare manual path. Sunk-cost automation wastes the clock.
8. **Check provider/delegation budget** before spawning batches.
