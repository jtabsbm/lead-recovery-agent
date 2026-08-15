# Multi-Browser Parallel Architecture (SOLVED)

## Problem
Subagents and the main session shared one Chrome instance → constant tab hijacking, and every new named session attaching to the user's main Chrome triggered the "Allow remote debugging?" permission prompt.

## Solution: dedicated Chrome instances per session
Each named session gets its own Chrome process with its own profile dir + CDP port. The `--remote-debugging-port` launch flag is an explicit opt-in, so **no permission prompt ever appears**.

## Setup (one command per worker)

```bash
# 1. Launch dedicated Chrome (pick unique port + profile dir)
mkdir -p /tmp/bu-profiles/workerN
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=933N \
  --user-data-dir=/tmp/bu-profiles/workerN \
  --no-first-run --no-default-browser-check about:blank &
# On Apple Silicon: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# On Intel: same path works; adjust if using Chromium.

# 2. Start the harness daemon for that session
cd /Users/wendell/.local/share/uv/tools/browser-use/lib/python3.11/site-packages
BU_CDP_URL=http://127.0.0.1:933N BU_NAME=workerN \
  /Users/wendell/.local/share/uv/tools/browser-use/bin/python -m browser_harness.daemon &

# 3. Use it from any agent: browser_exec(session="workerN", code="...")
```

## Worker registry
| Session | CDP Port | Profile | Purpose |
|---------|----------|---------|---------|
| worker1 | 9333 | /tmp/bu-profiles/worker1 | Login flows (Google-verified tasks) |
| (default) | — | user's main Chrome | User-visible browsing, subagent lane |

## Rules
1. **Subagents get workerN sessions only** — never the default session. This ends tab hijacking permanently.
2. **Default session** = the user's main Chrome, for tasks needing existing logins (Devpost, Gmail).
3. Login walls (Google passkey, reCAPTCHA, phone verify) are still human-gated — no automation can or should bypass them.
4. Profile dirs under /tmp are wiped on reboot. For persistent worker logins, use ~/Library/Application Support/bu-profiles/workerN instead.

## Verified working
- worker1 launched with zero prompts, isolated tabs, navigated Kaggle → Google sign-in autonomously.
- Google passkey challenge correctly identified as the human gate (expected — fresh profile, no trusted device).
