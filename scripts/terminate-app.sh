#!/usr/bin/env bash
# Stops the backend and frontend dev servers started by launch-app.sh.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/scripts/.run"
# shellcheck source=./lib.sh
source "$REPO_ROOT/scripts/lib.sh"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

STOPPED_ANY=0

stop_by_pidfile() {
  local name="$1" pidfile="$2"
  if [ ! -f "$pidfile" ]; then
    return
  fi
  local pid
  pid="$(cat "$pidfile")"
  if pid_alive "$pid"; then
    echo "Stopping $name (pid $pid)..."
    kill_tree "$pid"
    for _ in $(seq 1 10); do
      pid_alive "$pid" || break
      sleep 0.5
    done
    if pid_alive "$pid"; then
      echo "  still alive, sending SIGKILL"
      kill -KILL "$pid" 2>/dev/null || true
    fi
    STOPPED_ANY=1
  else
    echo "$name pid file present but process not running"
  fi
  rm -f "$pidfile"
}

stop_by_pidfile backend "$BACKEND_PID_FILE"
stop_by_pidfile frontend "$FRONTEND_PID_FILE"

# --- Verify ports are actually free, clean up any leftovers -----------------
for port_name in "$BACKEND_PORT:backend" "$FRONTEND_PORT:frontend"; do
  port="${port_name%%:*}"; name="${port_name#*:}"
  pids="$(port_pids "$port")"
  if [ -n "$pids" ]; then
    echo "Warning: port $port ($name) still has listener(s): $pids — force killing."
    for p in $pids; do
      kill -KILL "$p" 2>/dev/null || true
    done
    STOPPED_ANY=1
  elif ! have lsof; then
    echo "Note: lsof not available, could not verify port $port ($name) is free."
  fi
done

if [ "$STOPPED_ANY" -eq 1 ]; then
  echo "Done. App stopped."
else
  echo "Nothing was running."
fi
