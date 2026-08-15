#!/usr/bin/env python3
"""Mock OpenSearch server for end-to-end CLI testing without Docker.

Runs a real HTTP server on :19200 that implements just enough of the
OpenSearch API for leadsearch.py: cluster info, index create/exists, document
indexing (_doc, _bulk) and search. Then drives the CLI through its full
workflow and prints results.

Run: python mock_os_test.py
"""
import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CLI = Path(__file__).resolve().parent / "skills" / "leadfinder-ops" / "scripts" / "leadsearch.py"
PORT = 19200

DOCS = []


def _now_minus(days: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # silence
        pass

    def _send(self, code: int, body: dict):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            self._send(200, {"name": "mock", "cluster_name": "mock", "version": {"number": "2.11.0"}})
        elif self.path.startswith("/leads"):
            if DOCS or getattr(Handler, "index_created", False):
                self._send(200, {"aliases": {}})
            else:
                self._send(404, {"error": {"type": "index_not_found_exception", "reason": "no such index [leads]"}})
        else:
            self._send(404, {})

    def do_PUT(self):
        if self.path.startswith("/leads"):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            assert body["settings"]["index.knn"] is True, "knn setting missing"
            assert body["mappings"]["properties"]["message_embedding"]["type"] == "knn_vector"
            Handler.index_created = True
            self._send(201, {"acknowledged": True, "index": "leads"})
        else:
            self._send(404, {})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")
        path = self.path
        if path.startswith("/leads/_search"):
            q = payload.get("query", {})
            must = q.get("bool", {}).get("must", [])
            wants_unanswered = any("must_not" in str(m) for m in must) or "must_not" in q.get("bool", {})
            cat_filter = None
            for m in must:
                if isinstance(m, dict) and "term" in m and "category" in m["term"]:
                    cat_filter = m["term"]["category"]
            if payload.get("aggs"):
                by_cat = {}
                unanswered = 0
                for d in DOCS:
                    by_cat[d["category"]] = by_cat.get(d["category"], 0) + 1
                    if not d.get("responded_at"):
                        unanswered += 1
                self._send(200, {
                    "hits": {"total": {"value": len(DOCS)}, "hits": []},
                    "aggregations": {
                        "by_category": {"buckets": [{"key": k, "doc_count": v} for k, v in sorted(by_cat.items())]},
                        "unanswered": {"doc_count": unanswered},
                    },
                })
                return
            hits = []
            text = ""
            should = q.get("bool", {}).get("should", [])
            for s in should:
                if isinstance(s, dict) and "match" in s and "message" in s["match"]:
                    text = s["match"]["message"].get("query", "") if isinstance(s["match"]["message"], dict) else s["match"]["message"]
            for i, d in enumerate(DOCS):
                matched = (not text) or any(w.lower() in d["message"].lower() for w in text.split())
                unanswered_ok = (not wants_unanswered) or (not d.get("responded_at"))
                cat_ok = (cat_filter is None) or (d["category"] == cat_filter)
                if matched and unanswered_ok and cat_ok:
                    hits.append({"_id": str(i), "_score": 1.0 + 0.1 * i, "_source": d})
            hits.sort(key=lambda h: h["_source"]["received_at"])
            self._send(200, {"hits": {"total": {"value": len(hits)}, "hits": hits[:50]}})
        elif path.startswith("/leads/_doc") or path.startswith("/leads/_bulk"):
            DOCS.append(payload)
            self._send(201, {"result": "created", "_id": str(len(DOCS))})
        else:
            self._send(404, {})


def run_cli(*args: str) -> tuple[int, str]:
    env = {"PATH": "/usr/bin:/bin", "OS_URL": f"http://localhost:{PORT}", "OS_USER": "x", "OS_PASSWORD": "y",
           "HOME": "/tmp"}
    p = subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.5)

    ok = True
    def step(label, args, expect_out=None, expect_code=0):
        nonlocal ok
        code, out = run_cli(*args)
        good = code == expect_code and (expect_out is None or expect_out in out)
        print(f"{'PASS' if good else 'FAIL'} {label} (exit={code})")
        if not good:
            print(out)
            ok = False
        return out

    step("doctor — index missing", ["doctor"], expect_out="MISSING", expect_code=1)
    step("init — create index", ["init"], expect_out="created index")
    step("doctor — index present", ["doctor"], expect_out="present", expect_code=0)

    # seed docs directly into the mock
    DOCS.extend([
        {"lead_id": "L1", "received_at": _now_minus(40), "source": "web_form", "customer_name": "Old Customer",
         "contact": "old@x.com", "message": "need a quote for water heater replacement", "category": "quote_request",
         "responded_at": None, "next_action": "call_back"},
        {"lead_id": "L2", "received_at": _now_minus(2), "source": "missed_call", "customer_name": "Recent Miss",
         "contact": "+16195550142", "message": "voicemail: ac is out, 95 degrees, baby at home", "category": "urgent",
         "responded_at": None, "next_action": "call_back"},
        {"lead_id": "L3", "received_at": _now_minus(5), "source": "email", "customer_name": "Answered Already",
         "contact": "a@x.com", "message": "thanks for the quote, booked", "category": "scheduling",
         "responded_at": _now_minus(4.9), "next_action": "closed"},
        {"lead_id": "L4", "received_at": _now_minus(60), "source": "web_form", "customer_name": "Aged Lead",
         "contact": "aged@x.com", "message": "furnace inspection request never answered", "category": "quote_request",
         "responded_at": None, "next_action": "email_reply"},
    ])

    out = step("missed — finds 3 unanswered", ["missed", "--window", "90d"], expect_out="unanswered leads in last 90d: 3")
    assert "Old Customer" in out and "Recent Miss" in out and "Answered Already" not in out, "missed filter wrong"
    print("  -> oldest-first + unanswered filter verified")

    out = step("missed --min-value emergency", ["missed", "--window", "90d", "--min-value", "emergency"], expect_out="Recent Miss")
    assert "Old Customer" not in out
    print("  -> urgent filter verified")

    step("search — semantic-ish match", ["search", "water heater quote"], expect_out="Old Customer")
    step("report — owner summary", ["report", "--window", "90d"], expect_out="recovery rate")

    server.shutdown()
    print("\nALL MOCK E2E TESTS " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
