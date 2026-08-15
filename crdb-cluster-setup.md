# CRDB Cluster Setup — Blocked at GitHub Login (needs James)

## Status
- `crdb_lead_agent.py` — BUILT and verified in fallback mode ✓
- CockroachDB Cloud signup requires GitHub OAuth (or email+password)
- Browser has no GitHub session; gh CLI token can't drive web OAuth
- **2 of 2 required CRDB tools ready in code**: serverless cluster (schema+SQL) + vector indexing (embeddings table with <-> similarity)

## For James (~4 minutes)
1. Go to https://cockroachlabs.cloud/signup
2. Accept cookies → check TOS box → "Continue" on the TOS modal → click **Sign up with GitHub**
   (or email signup: absbm14@gmail.com + password — up to $400 free credits advertised)
3. Create a **Serverless cluster** (free): name `lead-agent`, any region
4. SQL → Connection string → copy the `postgresql://...` URL
5. In terminal:
   ```
   export DATABASE_URL="postgresql://...your-string..."
   cd /Users/wendell/zero-cash-revenue-engine/hackathon
   /Users/wendell/.hermes/hermes-agent/venv/bin/pip install psycopg2-binary
   /Users/wendell/.hermes/hermes-agent/venv/bin/python crdb_lead_agent.py
   ```
6. Expect `✓ CockroachDB memory initialized` and `backend: cockroachdb`

Then record demo + submit to https://cockroachdb-ai.devpost.com/ before **Aug 18, 2PM PDT**.
