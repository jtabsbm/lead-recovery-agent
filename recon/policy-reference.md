# Policy Reference (captured 2026-08-15 from live H1 pages)

## OPPO — hackerone.com/oppo_bbp (handle: oppo_bbp)
- Stats: bounty launched Feb 2025; 97% response efficiency; avg bounty $35-45; 133 in-scope assets; fast payment <1 month
- Required header when testing: `X-HackerOne-Research: <H1 username>`
- Test accounts: sign up free on website, use h1username@wearehackerone.com alias
- Repeated-vuln rule: similar vulns in same system = ONE package report (only first counts if separate)
- Scanner results without proof of harm = invalid. AI-generated reports require manual verification + screenshots.

### Scope tiers (web assets verified in-scope):
- **Extremely High** ($20-45 Low / $230-430 Med / $2900-3500 High / $5000-11500 Crit):
  id.oppo.com, id.heytap.com, safe.heytap.com, cloud.oppo.com, ColorOS
- **High** ($15-30 Low / $150-300 Med / $720-1200 High / $2900-4300 Crit):
  opposhop.cn, www.opposhop.cn, www.oppo.com/{th,my,in,id}/store, u.oppomobile.com, gcsm.oppoit.com, e.oppo.com, drp.myoppo.com, com.oppo.store, com.oppo.market, com.oplus.themestore, com.heytap.wallet, com.oplus.play, com.oplus.aimemory, gamecenter APKs
- **Moderate** ($10-20 Low / $45-80 Med / $150-450 High / $450-700 Crit):
  e-global.heytap.com/marketing/login, communityin.oppo.com, community.oppo.com, c.realme.com/{ru,in,id,global,eg}, http://open.oppomobile.com, com.heytap.health.international, com.heytap.xgame, com.coloros.assistantscreen, katanlabs games
- **Low** ($1-10 Low / $10-20 Med / $30-70 High / $70-150 Crit):
  zhongbao.heytap.com, zhongbao-ear.heytap.com, www.coloros.com, developers.oppomobile.com, com.qpon.*, com.oplus.{studycenter,melody,accesscard}, com.heytap.wearable.*
- **Mobile Devices** (48 hardware assets): $20-45 Low ... $5000-11500 Crit
- **Excluded**: anything not explicitly listed; com.fullmetalgamedev.fruitshooting
- Also hardware scope; full details in linked Google Sheet (docs.google.com/spreadsheets/d/1K2knhissfw817g_wLNQYJLGIn--j9HKHYBXsdALrD8Y)

### Key severity mappings (Web Application Scoring):
- Moderate #3: plaintext password over HTTP w/ HeyTap sign-in
- Low #2: minor info leaks (path/SVN/PHP/exceptions/config/log); plaintext password HTTP non-HeyTap
- Low #3: open redirect to non-OPPO domain without prompts
- Low #4: clickjacking on input pages w/ sensitive info (valid exploit required); MITM RCE w/ PoC
- Low #5: inappropriate config settings for ops/maintenance
- Low #6: SMS/email bombing >50 codes/30min to same target
- **NSI (NOT rewarded): mixed content, intranet IP/domain leaks, scanner-only reports, CSRF on non-sensitive actions, meaningless clickjacking/self-XSS, CORS-via-interaction, non-sensitive traversals**

## Bumble — hackerone.com/bumble
- Stats: launched Jun 2017; 80% response efficiency; $143,263 total paid; avg $250-300; 50 in-scope assets
- Bounty table by asset: Geneva $50-200 Low ... $4k-6k Crit; chatdate.app $10-50 Low ... $500-750 Crit; com.bumble.app / com.badoo.mobile $50-200 Low ... $4k-6k Crit
- **Dangling domains/domain takeover: accepted, FIXED $100 bounty**
- High-interest assets: Bumble mobile app, BFF mobile app, www.bumble.com (Tier 1), bma.bumble.com

### In-scope web assets (50 total in scope):
www.bumble.com (Tier 1), bma.bumble.com, badoo.com, us1/eu1/m/mus1/meu1/translate/corp/ccardsus1/ccardseu1/bma.badoo.com, badoocdn.com, hotornot.com, chatdate.app, com.hotornot.app,
geneva-staging.com set: www/web/app/api/sockets/social/router/presence/payments/links/go/gateway/deeplinks.geneva-staging.com + same for .chat + geneva-staging.chat
Apps: com.bumble.app, com.badoo.mobile, com.badoo.twa, com.bumblebff.app, com.genevachat.staging, iOS 930441707/6444040977/403684733/351331194, BFF TestFlight
Geneva staging OTP creds (OTP 000000): Member +1 880 999 0001, Owner +1 880 999 0009

### Out of scope: thebeehive/shop/honey/brand/blog.bumble.com
### Exclusions: missing headers/cookie flags w/o exploitability; enumeration w/o sensitive exposure/scalability; generic rate-limits; clickjacking on static pages; SPF/DMARC; rooted-device-only; theoretical/no-PoC; scanner-only reports
