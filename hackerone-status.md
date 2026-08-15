# HackerOne — Account Status (created 2026-08-15)

## Account: jamesthompson-sd ✅
- Email: absbm14@gmail.com — **confirmed** ✅
- Password: established pattern (in .env as H1 notes; never committed)
- TOTP secret: saved in project `.env` as `H1_TOTP_SECRET` (gitignored)
- 5 backup codes: saved in `.env` as `H1_BACKUP_CODES`

## One remaining manual step
Login at https://hackerone.com/users/sign_in → it redirects to the 2FA setup
confirmation page → enter password + current TOTP code (generate with:
`/tmp/genai-venv3/bin/python -c "import pyotp; print(pyotp.TOTP('72D7QVEPXDP73YIEOYI3365Z').now())"`
— or use a backup code) → Save.

The final confirmation POST rejects automated submissions with a generic
"something went wrong" (likely automation/bot detection). One manual entry
completes it.

## Target programs once inside (verified Aug 14 research)
| Program | Min bounty | Scope breadth | Time-to-first-$ |
|---|---|---|---|
| OPPO | $1 | 133 assets (widest on H1) | 1-2 weeks |
| Bumble | $10 | 50 assets | 1-3 weeks |
| inDrive | $100 | transport app suite | 2-3 weeks |
| Stripchat | $50 | 8 assets | days-weeks |

Strategy: enumerate OPPO + Bumble first (lowest floors, broadest scope — low-severity
findings still pay).
