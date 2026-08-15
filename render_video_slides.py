#!/usr/bin/env python3
"""Render the demo video frames with PIL: dark theme, code blocks, live API results.

Slides follow demo-video-script.md: problem → solution → LIVE Cloud Run proof →
live classify → repo/architecture → business traction → close.
"""
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (11, 16, 32)
FG = (240, 244, 255)
GREEN = (159, 232, 112)
BLUE = (120, 180, 255)
GRAY = (150, 160, 180)
OUT = "/tmp/demo-frames-v2"

import os
os.makedirs(OUT, exist_ok=True)


def font(size, bold=False):
    path = "/System/Library/Fonts/Helvetica.ttc" if not bold else "/System/Library/Fonts/Helvetica Bold.ttf"
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def new_slide():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    return img, d


def text(d, xy, s, size=24, color=FG, bold=False, mono=False):
    f = font(size, bold)
    d.text(xy, s, font=f, fill=color)
    return f


def code_block(d, xy, lines, w=900, size=17, border=GREEN):
    f = font(size)
    x, y = xy
    lh = size + 8
    box_h = lh * len(lines) + 24
    d.rounded_rectangle([x - 14, y - 12, x + w, y + box_h], radius=10, fill=(16, 24, 44), outline=border, width=2)
    for i, ln in enumerate(lines):
        color = FG if not ln.startswith("#") else GRAY
        d.text((x, y + i * lh), ln, font=f, fill=color)


def slide_header(d, kicker, title):
    text(d, (70, 60), kicker.upper(), 20, GREEN, bold=True)
    text(d, (70, 95), title, 44, FG, bold=True)
    d.line([70, 160, 1210, 160], fill=(40, 55, 90), width=2)


def badge(d, xy, s, color=GREEN):
    f = font(18, True)
    w = d.textlength(s, font=f) + 28
    d.rounded_rectangle([xy[0], xy[1], xy[0] + w, xy[1] + 34], radius=17, fill=(16, 24, 44), outline=color, width=2)
    d.text((xy[0] + 14, xy[1] + 6), s, font=f, fill=color)


# ── fetch LIVE data for authenticity ─────────────────────────────────────────

def live(path, payload=None):
    url = f"https://callbackops-agent-1087493193698.us-west1.run.app{path}"
    if payload:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


health = live("/health")
cls = live("/classify", {"message": "AC is out, 95 degrees, baby at home"})
cls2 = live("/classify", {"message": "How much for a new AC unit? 1800 sq ft house"})

slides = []

# 1. Title
img, d = new_slide()
slide_header(d, "All Things Agentic 2026 · The Taskmaster", "CallbackOps — Gemini Lead Recovery Agent")
text(d, (70, 200), "AI that recovers missed leads for home-service businesses", 26, BLUE)
code_block(d, (70, 280), [
    "agent = GeminiClassifier()        # gemini-3.5-flash-lite via REST",
    f"health = GET /health             # → {json.dumps(health)}",
    "",
    "pipeline: ingest → classify → draft → route → report",
    "human reviews every reply before it sends",
], w=880)
badge(d, (70, 520), "LIVE on Google Cloud Run")
badge(d, (300, 520), "Gemini 3.5", BLUE)
badge(d, (470, 520), "12/12 leads @ 0.96 conf")
slides.append(img)

# 2. Problem
img, d = new_slide()
slide_header(d, "The problem", "Missed calls are jobs walking away")
for i, (stat, expl) in enumerate([
    ("30-40%", "of inbound calls missed during summer rush"),
    ("85%", "of callers don't leave a voicemail"),
    ("$300-$2,000", "value of each lost job"),
    ("6:01 PM", "after-hours inquiries wait until morning — customer hires someone else"),
]):
    y = 210 + i * 105
    text(d, (70, y), stat, 40, GREEN, bold=True)
    text(d, (420, y + 12), expl, 24, FG)
slides.append(img)

# 3. LIVE Cloud Run proof
img, d = new_slide()
slide_header(d, "Proof — running on Google Cloud", "Live on Cloud Run (us-west1)")
code_block(d, (70, 210), [
    "$ curl https://callbackops-agent-1087493193698.us-west1.run.app/health",
    "",
    json.dumps(health),
    "",
    "$ curl -X POST .../classify -d '{\"message\": \"AC is out, 95 degrees...\"}'",
], w=1050, size=16)
text(d, (70, 500), "Deployed from source with gcloud run deploy — revision serving 100% traffic", 20, GRAY)
badge(d, (70, 560), ".run.app URL — judges can call it now")
slides.append(img)

# 4. Live classify result
img, d = new_slide()
slide_header(d, "Live classification", "Gemini 3.5 reads the message — for real")
code_block(d, (70, 210), [
    'POST /classify {"message": "AC is out, 95 degrees, baby at home"}',
    "",
    f"category:     {cls['category']}   (confidence {cls['confidence']})",
    f"urgency:      {cls['urgency']}",
    f"missing_info: {', '.join(cls['missing_info'])}",
    "",
    "draft_reply:",
    f"  \"{cls['draft_reply'][:95]}\"",
], w=1050, size=16)
slides.append(img)

# 5. Second example
img, d = new_slide()
slide_header(d, "Live classification — 2nd example", "Quote request handled differently")
code_block(d, (70, 210), [
    'POST /classify {"message": "How much for a new AC unit? 1800 sq ft house"}',
    "",
    f"category:     {cls2['category']}   (confidence {cls2['confidence']})",
    f"urgency:      {cls2['urgency']}",
    f"missing_info: {', '.join(cls2.get('missing_info', []))}",
    "",
    "draft_reply:",
    f"  \"{cls2['draft_reply'][:95]}\"",
], w=1050, size=16)
slides.append(img)

# 6. Architecture
img, d = new_slide()
slide_header(d, "Architecture", "One engine, four platform editions")
rows = [
    ("Gemini 3.5 (REST)", "classifier + draft replies", "→ All Things Agentic"),
    ("Strands Agents SDK", "@tool pipeline, local Ollama", "→ Agents for Humans"),
    ("CockroachDB", "persistent agent memory", "→ CRDB Agentic Memory"),
    ("OpenSearch", "lead retrieval layer", "→ OpenSearch Skills"),
]
for i, (a, b, c) in enumerate(rows):
    y = 210 + i * 90
    text(d, (70, y), a, 26, GREEN, bold=True)
    text(d, (400, y + 4), b, 22, FG)
    text(d, (820, y + 4), c, 22, BLUE)
text(d, (70, 600), "Human review gate before any customer contact — always.", 22, GRAY)
slides.append(img)

# 7. Business traction
img, d = new_slide()
slide_header(d, "Not just a demo", "A real operating business")
for i, (stat, expl) in enumerate([
    ("36", "San Diego home-service companies contacted in week one"),
    ("$750 / $2,500/mo", "productized pilot and core offers"),
    ("12/12 @ 0.96", "benchmark classification confidence"),
    ("4 hackathons", "same engine, four platform editions"),
]):
    y = 210 + i * 105
    text(d, (70, y), stat, 38, GREEN, bold=True)
    text(d, (470, y + 10), expl, 24, FG)
slides.append(img)

# 8. Close
img, d = new_slide()
slide_header(d, "CallbackOps", "Recover the leads you already paid for")
code_block(d, (70, 220), [
    "Live agent:  https://callbackops-agent-1087493193698.us-west1.run.app",
    "Code:        github.com/TyrannicAwe/lead-recovery-agent",
    "Endpoints:   GET /health · POST /classify · POST /demo",
    "",
    "Built by James Thompson · All Things Agentic Hackathon 2026",
], w=1000, size=18)
text(d, (70, 520), "Gemini 3.5 Flash · Google Cloud Run · Strands SDK · CockroachDB · OpenSearch", 20, GRAY)
slides.append(img)

# save
for i, s in enumerate(slides):
    s.save(f"{OUT}/slide_{i:02d}.png")
print(f"{len(slides)} slides rendered with LIVE API data → {OUT}")
print("classify sample:", cls["category"], cls["confidence"])
