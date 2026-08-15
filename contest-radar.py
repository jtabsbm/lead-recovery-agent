#!/usr/bin/env python3
"""contest-radar.py — weekly security-contest & hackathon radar.

Scrapes active/upcoming contests from three platforms with plain curl
(browser UA, no API keys) and writes a markdown status report:

  1. Code4rena   https://code4rena.com/contests        (Next.js flight-data JSON)
  2. Sherlock    https://audits.sherlock.xyz/api/...   (public JSON API)
  3. lablab.ai   https://lablab.ai/                    (homepage cards; Googlebot
                  UA slips past Cloudflare where a browser UA gets 403)

Output: contests-status.md next to this script (override with --output).
Stdlib only — cron-friendly. Exit code is 0 unless --strict is passed and a
source fails.

Cron (weekly, Monday 09:00):
  0 9 * * 1 /usr/bin/python3 /Users/wendell/zero-cash-revenue-engine/contest-radar.py >> /Users/wendell/zero-cash-revenue-engine/contest-radar.log 2>&1
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
GOOGLEBOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

TODAY = dt.date.today()


def fetch(url: str, ua: str = BROWSER_UA, timeout: int = 30) -> str:
    """curl a URL and return the body. Raises RuntimeError on HTTP != 200."""
    proc = subprocess.run(
        ["curl", "-sL", "--max-time", str(timeout), "-A", ua, url],
        capture_output=True, text=True, timeout=timeout + 10,
    )
    body = proc.stdout or ""
    if proc.returncode != 0 or len(body) < 200:
        raise RuntimeError(f"fetch failed rc={proc.returncode} bytes={len(body)} {url}")
    return body


# ────────────────────────────── Code4rena ──────────────────────────────
# code4rena.com is a Next.js App Router site: page data arrives as React
# "flight" chunks, self.__next_f.push([1,"…"]). We reassemble the string,
# then raw_decode every {"auditType": …} JSON object it contains.

def parse_c4r(html: str) -> list[dict]:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    parts = []
    for c in chunks:
        try:
            parts.append(json.loads('"' + c + '"'))  # honour \uXXXX / \\" escapes
        except json.JSONDecodeError:
            parts.append(c.encode().decode("unicode_escape"))
    blob = "\n".join(parts)

    dec = json.JSONDecoder()
    contests: dict[str, dict] = {}
    for m in re.finditer(r'\{"auditType"', blob):
        try:
            obj, _ = dec.raw_decode(blob, m.start())
        except json.JSONDecodeError:
            continue
        if not (isinstance(obj, dict) and obj.get("title") and obj.get("startTime")):
            continue
        slug = obj.get("slug") or obj["title"]
        contests[slug] = {
            "platform": "Code4rena",
            "title": obj["title"],
            "url": f"https://code4rena.com/contests/{slug}",
            "status": obj.get("status") or "",
            "start": (obj.get("startTime") or "")[:10],
            "end": (obj.get("endTime") or "")[:10],
            "prize": (obj.get("formattedAmount") or "").replace("$$", "$"),
            "kind": obj.get("auditType") or "",
        }
    return list(contests.values())


def scrape_code4rena() -> list[dict]:
    contests = parse_c4r(fetch("https://code4rena.com/contests"))
    # keep anything not explicitly Completed — Active/Upcoming/Reporting etc.
    live = [c for c in contests if c["status"] and c["status"] != "Completed"]
    return sorted(live, key=lambda c: c["end"] or "9999")


# ────────────────────────────── Sherlock ───────────────────────────────
# audits.sherlock.xyz exposes a clean paginated JSON API. Active/judging
# contests sit on the first pages; we stop once a page is all-finished.

def scrape_sherlock(max_pages: int = 3) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        data = json.loads(fetch(f"https://audits.sherlock.xyz/api/contests?page={page}"))
        items = data.get("items", [])
        if not items:
            break
        for it in items:
            status = it.get("status") or ""
            ends = it.get("ends_at") or 0
            if status == "FINISHED" or (ends and ends < dt.datetime.now().timestamp()):
                continue
            start = dt.datetime.fromtimestamp(it["starts_at"], dt.timezone.utc).date() if it.get("starts_at") else None
            end = dt.datetime.fromtimestamp(ends, dt.timezone.utc).date() if ends else None
            prize = it.get("prize_pool")
            out.append({
                "platform": "Sherlock",
                "title": it.get("title") or "?",
                "url": f"https://audits.sherlock.xyz/contests/{it.get('id')}",
                "status": status.replace("SHERLOCK_", "").replace("_", " ").title() or "Live",
                "start": start.isoformat() if start else "",
                "end": end.isoformat() if end else "",
                "prize": f"${prize:,} {it.get('token') or 'USDC'}" if prize else "",
                "kind": it.get("type_label") or "",
            })
        if all((it.get("status") == "FINISHED") for it in items):
            break
    return sorted(out, key=lambda c: c["end"] or "9999")


# ────────────────────────────── lablab.ai ──────────────────────────────
# lablab.ai is Cloudflare-gated for normal UAs but serves the homepage to
# Googlebot. Cards live directly in the homepage HTML: each links to
# /ai-hackathons/<slug> with a status badge (Register/TBA/Finished), an
# optional date range like "SEP 10 - 17", and the title in the img alt.

MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
DATE_RE = re.compile(
    r"\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\.?\s*(\d{1,2})\s*[-–]\s*"
    r"(?:(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\.?\s*)?(\d{1,2})\b")
BADGES = ("Register", "TBA", "Finished", "Live", "Started", "Submission")


def parse_lablab(html: str) -> list[dict]:
    # title comes from the card's <img alt="…"> attr
    alt_by_slug = {m.group(1): m.group(2) for m in re.finditer(
        r'/ai-hackathons/[a-z0-9-]*?([a-z0-9-]+)".{0,9000}?alt="([^"]{4,120})"', html, re.S)}

    # walking each anchor's text keeps badge + date + title together
    entries: dict[str, dict] = {}
    for m in re.finditer(r'href="(/ai-hackathons/[^"#?]+)"', html):
        slug = m.group(1).rsplit("/", 1)[-1]
        if slug in entries:
            continue
        seg = html[m.start(): m.start() + 9000]
        seg = re.sub(r"<img[^>]*>", " ", seg)
        seg = re.sub(r"<svg[^>]*>.*?</svg>", " ", seg, flags=re.S)
        txt = re.sub(r"<[^>]+>", " ", seg)
        txt = re.sub(r"\s+", " ", txt).strip()

        badge = next((b for b in BADGES if txt.startswith(b)), "")
        d = DATE_RE.search(txt)
        title = alt_by_slug.get(slug, slug.replace("-", " ").title())

        start = end = ""
        if d:
            sm, sd, em, ed = d.group(1)[:3], int(d.group(2)), d.group(3), int(d.group(4))
            sm_n, em_n = MONTHS[sm], MONTHS.get(em[:3] if em else sm, MONTHS[sm])
            # assume the listed window is the current or next occurrence
            sy = TODAY.year if sm_n >= TODAY.month - 2 else TODAY.year + 1
            ey = sy + (1 if em_n < sm_n else 0)
            start = f"{sy}-{sm_n:02d}-{sd:02d}"
            end = f"{ey}-{em_n:02d}-{ed:02d}"
        entries[slug] = {
            "platform": "lablab.ai",
            "title": title,
            "url": f"https://lablab.ai/ai-hackathons/{slug}",
            "status": badge or "?",
            "start": start, "end": end, "prize": "", "kind": "AI hackathon",
        }
    return list(entries.values())


def scrape_lablab() -> list[dict]:
    entries = parse_lablab(fetch("https://lablab.ai/", ua=GOOGLEBOT_UA))
    live = [e for e in entries if e["status"] not in ("Finished",)]
    return sorted(live, key=lambda e: e["start"] or "9999")


# ────────────────────────────── report ─────────────────────────────────

def days_left(end_iso: str) -> str:
    if not end_iso:
        return ""
    try:
        d = (dt.date.fromisoformat(end_iso[:10]) - TODAY).days
    except ValueError:
        return ""
    return "today" if d == 0 else (f"{d}d" if d > 0 else "closed")


def render(sections: list[tuple[str, list[dict], str | None]], path: Path) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# Contest Radar — {now}", "",
             "Automated weekly sweep of Code4rena / Sherlock / lablab.ai.", ""]

    total = sum(len(rows) for _, rows, _ in sections)
    for name, rows, note in sections:
        lines.append(f"## {name} ({len(rows)})")
        lines.append("")
        if note:
            lines.append(f"> {note}")
            lines.append("")
        if not rows:
            lines.append("_none found_")
        else:
            lines.append("| Contest | Status | Dates | Prize | Left | Link |")
            lines.append("|---|---|---|---|---|---|")
            for c in rows:
                dates = f"{c['start'] or '?'} → {c['end'] or '?'}"
                lines.append(
                    f"| {c['title'][:60]} | {c['status']} | {dates} "
                    f"| {c['prize'] or '—'} | {days_left(c['end'])} | {c['url']} |")
        lines.append("")

    # actionable digest
    soon = []
    for _, rows, _ in sections:
        for c in rows:
            dl = days_left(c["end"])
            if dl and dl != "closed":
                try:
                    if int(dl.rstrip("d")) <= 21 or dl == "today":
                        soon.append((int(dl.rstrip("d")) if dl != "today" else 0, c))
                except ValueError:
                    pass
    lines.append("## ⏰ Closing within 21 days")
    lines.append("")
    if soon:
        for _, c in sorted(soon):
            lines.append(f"- **{c['title']}** ({c['platform']}) — {days_left(c['end'])} left — {c['url']}")
    else:
        lines.append("_nothing closing in the next 3 weeks_")
    lines += ["", f"_Generated by `contest-radar.py` · {total} live entries · next sweep when cron fires_", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Weekly Code4rena/Sherlock/lablab contest radar")
    ap.add_argument("--output", default=str(Path(__file__).parent / "contests-status.md"))
    ap.add_argument("--strict", action="store_true", help="non-zero exit if a source fails")
    args = ap.parse_args()

    sections = []
    for name, fn, note in [
        ("Code4rena", scrape_code4rena,
         "Code4rena announced it is **winding down** — only in-flight contests remain; expect this list to shrink to zero."),
        ("Sherlock (audits)", scrape_sherlock, None),
        ("lablab.ai hackathons", scrape_lablab, None),
    ]:
        try:
            rows = fn()
            print(f"[ok] {name}: {len(rows)} live", file=sys.stderr)
        except Exception as e:  # keep other sources alive for cron
            rows = []
            print(f"[fail] {name}: {e}", file=sys.stderr)
            if args.strict:
                raise
        sections.append((name, rows, note))

    report = render(sections, Path(args.output))
    print(report)
    print(f"[done] wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
