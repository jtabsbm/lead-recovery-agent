#!/usr/bin/env python3
"""Fetch AI-training platform pages: direct curl-first, r.jina.ai fallback.
Saves raw fetches to ai_raw/ and prints extraction snippets."""
import json, os, re, subprocess, sys, html

RAW = "/Users/wendell/zero-cash-revenue-engine/ai_raw"
os.makedirs(RAW, exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
HDRS = ["-H", f"User-Agent: {UA}",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-H", "Sec-Fetch-Mode: navigate",
        "-H", "Sec-Fetch-Dest: document",
        "-H", "Sec-Fetch-Site: none",
        "-H", "Sec-Fetch-User: ?1",
        "--compressed", "-sL", "--max-time", "45"]

def fetch(url, name):
    """Fetch URL direct; on thin/blocked body retry via r.jina.ai. Returns (mode, body)."""
    fn = os.path.join(RAW, f"{name}.html")
    # Try direct
    try:
        r = subprocess.run(["curl"] + HDRS + [url], capture_output=True, text=True, timeout=60)
        body = r.stdout
        if len(body) > 6000 and not _looks_blocked(body, url):
            _save(fn, url, "direct", body)
            return "direct", body
    except Exception as e:
        body = f"ERROR {e}"
    # Jina fallback
    try:
        r2 = subprocess.run(["curl", "-sL", "--max-time", "60",
                             "-H", f"User-Agent: {UA}",
                             "-H", "X-Return-Format: markdown",
                             f"https://r.jina.ai/{url}"],
                            capture_output=True, text=True, timeout=75)
        b2 = r2.stdout
        if len(b2) > 1500 and "Just a moment" not in b2[:400] and "403" != b2[:3]:
            _save(fn, url, "jina", b2)
            return "jina", b2
        # last resort: jina with browser engine
        r3 = subprocess.run(["curl", "-sL", "--max-time", "90",
                             "-H", f"User-Agent: {UA}",
                             "-H", "X-Engine: browser",
                             "-H", "X-Return-Format: markdown",
                             f"https://r.jina.ai/{url}"],
                            capture_output=True, text=True, timeout=105)
        b3 = r3.stdout
        if len(b3) > 1500:
            _save(fn, url, "jina-browser", b3)
            return "jina-browser", b3
    except Exception as e:
        b2 = f"JINA_ERROR {e}"
    _save(fn, url, "failed", (body or "")[:500] + "\n---JINA---\n" + b2[:500])
    return "failed", body

def _save(fn, url, mode, body):
    with open(fn, "w") as f:
        f.write(f"<!-- URL: {url}\n     MODE: {mode} -->\n" + body)

def _looks_blocked(body, url):
    b = body[:2000].lower()
    if "just a moment" in b or "cf-browser-verification" in b or "attention required" in b:
        return True
    if "enable javascript" in b and len(body) < 30000 and "<article" not in body.lower():
        return True
    return False

def extract(body):
    """Pull title, meta desc, pay-rate lines, signup/apply/waitlist mentions."""
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    title = html.unescape(t.group(1)).strip() if t else "(no title)"
    md = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', body, re.S | re.I)
    desc = html.unescape(md.group(1)).strip() if md else ""
    # strip tags for text scan
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(re.sub(r"\s+", " ", text))
    # markdown mode (jina): body is already text
    if title == "(no title)":
        t2 = re.search(r"^Title:\s*(.+)$", body, re.M)
        if t2: title = t2.group(1).strip()
    pay_lines = []
    for m in re.finditer(r"[^.!?]*\$\s?\d[\d,.]*\s*(?:-|–|to)?\s*\$?\d?[\d,.]*\s*(?:/|per\s+)hour[^.!?]*[.!?]?", text, re.I):
        pay_lines.append(m.group(0).strip()[:220])
    for m in re.finditer(r"[^.!?]*\$\s?\d[\d,.]*\s*(?:/|per\s)(?:hr|hour)[^.!?]*", text, re.I):
        s = m.group(0).strip()[:220]
        if s not in pay_lines: pay_lines.append(s)
    kw = {}
    for k in ["apply now", "sign up", "join now", "waitlist", "wait list", "not accepting",
              "invite only", "assessment", "resume", "cv", "government id", "identity verific",
              "id verific", "onboarding", "weekly pay", "paypal", "airtm", "direct deposit",
              "availability of work", "full-time", "part-time", "contract"]:
        n = len(re.findall(re.escape(k), text, re.I))
        if n: kw[k] = n
    first = text[:700]
    return {"title": title, "desc": desc[:300],
            "pay_lines": pay_lines[:8], "keywords": kw, "text_head": first}

if __name__ == "__main__":
    targets = json.loads(sys.argv[1])
    for name, url in targets:
        mode, body = fetch(url, name)
        if mode == "failed":
            print(f"### {name} [{url}] -> FAILED")
            continue
        ex = extract(body)
        print(f"### {name} [{url}] mode={mode} len={len(body)}")
        print(f"TITLE: {ex['title']}")
        if ex['desc']: print(f"DESC: {ex['desc']}")
        if ex['pay_lines']:
            print("PAY LINES:")
            for p in ex['pay_lines']: print(f"  $ | {p}")
        print(f"KEYWORDS: {json.dumps(ex['keywords'])}")
        print(f"HEAD: {ex['text_head'][:400]}")
        print()
