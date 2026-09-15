# Shared helpers for install.sh / launch-app.sh / terminate-app.sh
# Must be sourced, not executed. Expects REPO_ROOT and RUN_DIR to already be set.

BACKEND_PORT=8000
FRONTEND_PORT=5173
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

have() { command -v "$1" >/dev/null 2>&1; }

# postgresql@15 is keg-only on macOS (Homebrew won't symlink it onto PATH),
# so pg_isready/psql/createdb may be missing even though Postgres is running.
# install.sh exports this for its own run, but that doesn't persist to later
# shells/scripts, so every script that needs these tools re-checks here.
if [ "$(uname -s)" = "Darwin" ] && ! have pg_isready && have brew; then
  pg_prefix="$(brew --prefix postgresql@15 2>/dev/null || true)"
  [ -n "$pg_prefix" ] && [ -d "$pg_prefix/bin" ] && PATH="$pg_prefix/bin:$PATH"
fi

# Prints PIDs listening on $1, or nothing if it can't tell (no lsof).
port_pids() {
  if have lsof; then
    lsof -ti ":$1" 2>/dev/null || true
  fi
}

port_in_use() {
  [ -n "$(port_pids "$1")" ]
}

# UP / DOWN text for postgres, with an httpish status code for backend/frontend.
check_postgres() {
  if have pg_isready && pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres >/dev/null 2>&1; then
    echo "UP"
  else
    echo "DOWN"
  fi
}

check_http() {
  local url="$1"
  curl -s -o /dev/null -w '%{http_code}' --max-time 2 "$url" 2>/dev/null || echo "000"
}

check_backend() {
  # /admin/ only proves the Django URLconf loaded (200 or 302), not DB health.
  check_http "http://localhost:${BACKEND_PORT}/admin/"
}

check_frontend() {
  check_http "http://localhost:${FRONTEND_PORT}/"
}

# Recursively kill a process tree rooted at $1 (TERM, then KILL if still alive).
kill_tree() {
  local pid="$1"
  local child
  for child in $(pgrep -P "$pid" 2>/dev/null || true); do
    kill_tree "$child"
  done
  kill -TERM "$pid" 2>/dev/null || true
}

pid_alive() {
  kill -0 "$1" 2>/dev/null
}
