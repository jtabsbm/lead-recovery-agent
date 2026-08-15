#!/usr/bin/env python3
"""Upload a file to a Devpost file input in the DEFAULT browser via the harness daemon socket.

Talks the same IPC protocol as browser_harness.helpers: JSON over the bu-default.sock.
Uses CDP DOM.setFileInputFiles to set files without a native dialog.
"""
import json
import socket
import sys
import time

SOCK = "/Users/wendell/.config/browser-harness/runtime/bu-default.sock"


def send(req):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(120)
    s.connect(SOCK)
    s.sendall(json.dumps(req).encode())
    buf = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
        try:
            return json.loads(buf.decode())
        except json.JSONDecodeError:
            continue
    raise RuntimeError("no response")


def main():
    file_path = sys.argv[1]
    selector = sys.argv[2] if len(sys.argv) > 2 else 'input[name="software_photo[data]"]'

    # 1. find the input's node
    r = send({"method": "DOM.getDocument", "params": {}})
    root = r["result"]["root"]["nodeId"]
    r = send({"method": "DOM.querySelector", "params": {"nodeId": root, "selector": selector}})
    nid = r["result"].get("nodeId", 0)
    if not nid:
        print(f"selector not found: {selector}")
        return 1
    r = send({"method": "DOM.resolveNode", "params": {"nodeId": nid}})
    obj = r["result"]["object"]

    # 2. set the file
    r = send({"method": "DOM.setFileInputFiles", "params": {"files": [file_path], "objectId": obj["objectId"]}})
    print("files set:", r)

    # 3. fire change via Runtime on the same node
    r = send({"method": "Runtime.evaluate", "params": {
        "expression": f'(() => {{ const el = document.querySelector({json.dumps(selector)}); el.dispatchEvent(new Event("change", {{bubbles:true}})); el.dispatchEvent(new Event("input", {{bubbles:true}})); return "events fired"; }})()',
        "returnByValue": True}})
    print("events:", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
