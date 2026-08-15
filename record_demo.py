#!/usr/bin/env python3
"""Record a demo video of the live Cloud Run agent using CDP screencast frames.

Drives the default browser (via harness cdp helper through browser_exec is not
available here), so we talk to the harness daemon socket directly with its
documented one-line-JSON protocol.

Flow (per demo-video-script.md):
  1. .run.app service page (proof of Google Cloud)
  2. Live classify POST via a rendered console page
  3. Terminal-style report of the 12-lead demo

Output: frames → ffmpeg → mp4 (~4 min target, we'll compress segments)
"""
import base64
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

SOCK = "/Users/wendell/.config/browser-harness/runtime/bu-default.sock"
OUT = Path("/tmp/demo-frames")
OUT.mkdir(exist_ok=True)


def send(req, timeout=60):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect(SOCK)
    s.sendall(json.dumps(req).encode() + b"\n")
    buf = b""
    while True:
        chunk = s.recv(1 << 20)
        if not chunk:
            break
        buf += chunk
        try:
            return json.loads(buf.decode())
        except json.JSONDecodeError:
            continue
    raise RuntimeError("no reply")


def cdp(method, **params):
    r = send({"method": method, "params": params})
    if "error" in r:
        raise RuntimeError(r["error"])
    return r.get("result", {})


def eval_js(expr):
    r = cdp("Runtime.evaluate", expression=expr, returnByValue=True)
    return r.get("result", {}).get("value")


def grab(fname):
    r = cdp("Page.captureScreenshot", format="png")
    (OUT / fname).write_bytes(base64.b64decode(r["data"]))
    print("frame:", fname)


def main():
    n = 0

    def step(url_action, wait, frames=3, label=""):
        nonlocal n
        url_action()
        time.sleep(wait)
        for i in range(frames):
            grab(f"frame_{n:04d}.png")
            n += 1
            time.sleep(1.2)
        print("step done:", label)

    # 1. service page (cloud proof)
    step(lambda: eval_js("location.href = 'https://callbackops-agent-1087493193698.us-west1.run.app/'"),
         4, 4, "service page")

    # 2. health check
    step(lambda: eval_js("location.href = 'https://callbackops-agent-1087493193698.us-west1.run.app/health'"),
         3, 3, "health")

    # 3. live classify — build a small local page that POSTs and shows the JSON
    classify_page = """
    document.open();
    document.write(`<html><body style="font-family:monospace;background:#0b1020;color:#9fe870;padding:40px;font-size:18px">
    <h2 style="color:#fff">Live classify — Gemini 3.5 on Cloud Run</h2>
    <div id="out">POST /classify {"message": "AC is out, 95 degrees, baby at home"}</div>
    <pre id="res" style="color:#fff">...</pre></body></html>`);
    document.close();
    fetch('https://callbackops-agent-1087493193698.us-west1.run.app/classify', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: 'AC is out, 95 degrees, baby at home'})
    }).then(r => r.json()).then(j => {
      document.getElementById('res').textContent = JSON.stringify(j, null, 2);
    });
    """
    step(lambda: eval_js(f"(() => {{ {classify_page} }})()"), 6, 6, "live classify")

    # 4. repo page
    step(lambda: eval_js("location.href = 'https://github.com/TyrannicAwe/lead-recovery-agent'"),
         5, 4, "repo")

    print(f"\n{n} frames captured → {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
