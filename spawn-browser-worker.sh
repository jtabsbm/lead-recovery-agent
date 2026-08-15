#!/bin/bash
# spawn-browser-worker.sh — launch an isolated parallel Chrome + browser-harness daemon
# Usage: spawn-browser-worker.sh <name> [port]
#   name: session name for browser_exec(session=<name>) — [a-z0-9-]
#   port: CDP port (default: 9230 + hash of name mod 50)
set -euo pipefail

NAME="${1:?usage: spawn-browser-worker.sh <name> [port]}"
PORT="${2:-$((9230 + ($(printf '%s' "$NAME" | cksum | cut -d' ' -f1) % 50)))}"
PROFILE="/tmp/chrome-$NAME"
RUNTIME="$HOME/.config/browser-harness/runtime"
PY="/Users/wendell/.local/share/uv/tools/browser-use/bin/python"

# 1. Already running?
if [ -S "$RUNTIME/bu-$NAME.sock" ]; then
  echo "daemon $NAME already running (socket present)"
  exit 0
fi

# 2. Chrome instance for this worker (own profile = own cookies/state)
if ! curl -s "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
  mkdir -p "$PROFILE"
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --user-data-dir="$PROFILE" \
    --remote-debugging-port="$PORT" \
    --no-first-run --no-default-browser-check \
    --window-size=1400,900 --window-position=2000,40 \
    "about:blank" >/dev/null 2>&1 &
  for i in $(seq 1 20); do
    curl -s "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1 && break
    sleep 0.5
  done
fi
echo "chrome on :$PORT"

# 3. Daemon wired to that Chrome (env must be on the SAME line-process)
BU_NAME="$NAME" BU_CDP_URL="http://127.0.0.1:$PORT" nohup "$PY" -m browser_harness.daemon \
  >/dev/null 2>&1 &

# 4. Wait for socket
for i in $(seq 1 20); do
  [ -S "$RUNTIME/bu-$NAME.sock" ] && break
  sleep 0.5
done
if [ -S "$RUNTIME/bu-$NAME.sock" ]; then
  echo "OK: browser_exec(session='$NAME') is now isolated on port $PORT"
  echo "log: $HOME/.config/browser-harness/tmp/bu-$NAME.log"
else
  echo "FAILED — check $HOME/.config/browser-harness/tmp/bu-$NAME.log" >&2
  exit 1
fi
