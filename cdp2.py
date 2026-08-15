#!/usr/bin/env python3
"""CDP driver for the SECOND Chrome instance (port 9223) — no login state.

Used for non-authenticated parallel work so we never fight the primary browser.
"""
import json
import urllib.request
import websocket  # pip install websocket-client


class CDP2:
    def __init__(self, port=9223):
        self.port = port
        self.ws = None
        self.mid = 0
        self.target = None

    def targets(self):
        with urllib.request.urlopen(f"http://localhost:{self.port}/json/list", timeout=10) as r:
            return json.load(r)

    def new_tab(self, url):
        req = urllib.request.Request(
            f"http://localhost:{self.port}/json/new?{urllib.parse.urlencode({'url': url})}",
            method="PUT")
        with urllib.request.urlopen(req, timeout=15) as r:
            t = json.load(r)
        self.target = t
        return t

    def attach(self, target_id=None):
        if target_id is None:
            pages = [t for t in self.targets() if t["type"] == "page"]
            self.target = pages[0]
        t = self.target
        self.ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
        resp = self.send("Target.attachToTarget", targetId=t["id"], flatten=True)
        self.session_id = resp["result"]["sessionId"]
        return self.session_id

    def send(self, method, **params):
        self.mid += 1
        msg = {"id": self.mid, "method": method, "params": params}
        if getattr(self, "session_id", None):
            msg["sessionId"] = self.session_id
        self.ws.send(json.dumps(msg))
        while True:
            resp = json.loads(self.ws.recv())
            if resp.get("id") == self.mid:
                if "error" in resp:
                    raise RuntimeError(resp["error"])
                return resp["result"]

    def goto(self, url):
        return self.send("Page.navigate", url=url)

    def eval(self, expr):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")

    def title(self):
        return self.eval("document.title")

    def body(self, n=500):
        return self.eval(f"document.body ? document.body.innerText.slice(0,{n}) : ''")

    def click(self, sel):
        return self.eval(f'''
        (() => {{
          const el = document.querySelector({json.dumps(sel)});
          if (!el) return "not found";
          el.click(); return "clicked";
        }})()
        ''')


if __name__ == "__main__":
    import urllib.parse
    c = CDP2()
    t = c.new_tab("https://opensearch.org/events/agent-skills-hackathon-us-2026/")
    c.attach(t["id"])
    import time
    time.sleep(4)
    print("TITLE:", c.title())
    print("BODY:", c.body(300))
