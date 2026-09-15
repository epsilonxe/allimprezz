#!/usr/bin/env bash
# Starts the backend and frontend dev servers in the background, waits for
# them to become healthy, prints how to access the app, then stays in the
# foreground as a live health monitor (Ctrl+C stops the monitor only —
# the servers keep running; use terminate-app.sh to stop them).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/scripts/.run"
mkdir -p "$RUN_DIR"
# shellcheck source=./lib.sh
source "$REPO_ROOT/scripts/lib.sh"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"
BACKEND_LOG="$RUN_DIR/backend.log"
FRONTEND_LOG="$RUN_DIR/frontend.log"

# --- Guard: already running? ------------------------------------------------
for name_pidfile in "backend:$BACKEND_PID_FILE" "frontend:$FRONTEND_PID_FILE"; do
  name="${name_pidfile%%:*}"; pidfile="${name_pidfile#*:}"
  if [ -f "$pidfile" ] && pid_alive "$(cat "$pidfile")"; then
    echo "Error: $name already appears to be running (pid $(cat "$pidfile"))." >&2
    echo "Run ./scripts/terminate-app.sh first, or remove $pidfile if it's stale." >&2
    exit 1
  fi
done

# --- Guard: ports already occupied by something else? -----------------------
for port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
  if port_in_use "$port"; then
    echo "Error: port $port is already in use by another process." >&2
    echo "Free it, or stop whatever's using it, then try again." >&2
    exit 1
  fi
done

# --- Migrate -----------------------------------------------------------------
echo "Applying database migrations..."
(cd "$REPO_ROOT/backend" && uv run python manage.py migrate)

# --- Start backend -------------------------------------------------------------
echo "Starting backend..."
(cd "$REPO_ROOT/backend" && uv run python manage.py runserver "0.0.0.0:${BACKEND_PORT}" >"$BACKEND_LOG" 2>&1 &
 echo $! >"$BACKEND_PID_FILE")

# --- Start frontend ------------------------------------------------------------
# --host 0.0.0.0 binds Vite to all interfaces (its default is localhost-only),
# so other devices on the LAN can reach it — matches docker-compose.yml.
echo "Starting frontend..."
(cd "$REPO_ROOT/frontend" && npm run dev -- --host 0.0.0.0 >"$FRONTEND_LOG" 2>&1 &
 echo $! >"$FRONTEND_PID_FILE")

# --- Wait for both to become healthy -----------------------------------------
echo "Waiting for services to become healthy..."
READY=0
for _ in $(seq 1 30); do
  pg_status="$(check_postgres)"
  backend_status="$(check_backend)"
  frontend_status="$(check_frontend)"
  if [ "$pg_status" = "UP" ] && { [ "$backend_status" = "200" ] || [ "$backend_status" = "302" ]; } && [ "$frontend_status" = "200" ]; then
    READY=1
    break
  fi
  sleep 1
done

if [ "$READY" -ne 1 ]; then
  echo "Error: app did not become healthy within 30s." >&2
  echo "postgres=$pg_status backend=$backend_status frontend=$frontend_status" >&2
  echo "--- backend.log (tail) ---" >&2
  tail -n 20 "$BACKEND_LOG" >&2 || true
  echo "--- frontend.log (tail) ---" >&2
  tail -n 20 "$FRONTEND_LOG" >&2 || true
  echo "Processes are still running for debugging. Run ./scripts/terminate-app.sh to stop them." >&2
  exit 1
fi

LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"

cat <<EOF

App is running:
  Frontend:     http://localhost:${FRONTEND_PORT}
  Backend API:  http://localhost:${BACKEND_PORT}
  Django Admin: http://localhost:${BACKEND_PORT}/admin/
EOF
if [ -n "$LAN_IP" ]; then
  echo "  LAN:          http://${LAN_IP}:${FRONTEND_PORT}"
fi
cat <<EOF

Logs: $BACKEND_LOG, $FRONTEND_LOG
Stop with: ./scripts/terminate-app.sh

Monitoring health every 5s. Press Ctrl+C to stop watching (the app keeps running).
EOF

# --- Live monitor --------------------------------------------------------------
trap 'echo; echo "Stopping monitor — app still running in background. Run ./scripts/terminate-app.sh to stop it."; exit 0' INT TERM

while true; do
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  pg_status="$(check_postgres)"
  backend_status="$(check_backend)"
  frontend_status="$(check_frontend)"
  echo "[$ts] postgres: $pg_status  backend: $backend_status  frontend: $frontend_status"
  sleep 5
done
