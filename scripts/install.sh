#!/usr/bin/env bash
# Sets up everything needed to run the app natively (without Docker):
# uv, Node.js 22, PostgreSQL 15, the app database, and backend/frontend deps.
# Safe to re-run — every step is guarded and skips work that's already done.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/scripts/.run"
mkdir -p "$RUN_DIR"
# shellcheck source=./lib.sh
source "$REPO_ROOT/scripts/lib.sh"

OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM=macos ;;
  Linux)  PLATFORM=linux ;;
  *) echo "Unsupported OS: $OS (this script supports macOS and Linux/Ubuntu-Debian)" >&2; exit 1 ;;
esac
echo "Detected platform: $PLATFORM"

# --- 1. uv ---------------------------------------------------------------
if have uv; then
  echo "uv already installed ($(uv --version))"
else
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# --- 2. Node.js 22 ---------------------------------------------------------
if have node && [ "$(node -v | sed -E 's/^v([0-9]+).*/\1/')" -ge 20 ]; then
  echo "Node already installed ($(node -v))"
else
  echo "Installing Node.js 22..."
  if [ "$PLATFORM" = macos ]; then
    have brew || { echo "Homebrew is required to install Node on macOS: https://brew.sh" >&2; exit 1; }
    brew install node@22
    export PATH="$(brew --prefix)/opt/node@22/bin:$PATH"
  else
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
  fi
fi

# --- 3. PostgreSQL 15 --------------------------------------------------------
if [ "$PLATFORM" = macos ]; then
  # postgresql@15 is keg-only on macOS: brew won't put it on PATH.
  export PATH="$(brew --prefix)/opt/postgresql@15/bin:$PATH"
fi

if have pg_isready && pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" >/dev/null 2>&1; then
  echo "PostgreSQL already installed and running"
else
  echo "Installing/starting PostgreSQL 15..."
  if [ "$PLATFORM" = macos ]; then
    have brew || { echo "Homebrew is required to install PostgreSQL on macOS: https://brew.sh" >&2; exit 1; }
    brew install postgresql@15
    export PATH="$(brew --prefix)/opt/postgresql@15/bin:$PATH"
    # brew services needs a GUI login session (launchd gui/<uid> domain); it
    # fails with "Bootstrap failed: 5" over SSH or without a console login.
    if ! brew services start postgresql@15; then
      echo "brew services failed (no GUI login session?); starting PostgreSQL with pg_ctl instead."
      echo "Note: it won't auto-start on reboot; re-run this script or pg_ctl start after a restart."
      PGDATA="$(brew --prefix)/var/postgresql@15"
      PGLOG="$(brew --prefix)/var/log/postgresql@15.log"
      mkdir -p "$(dirname "$PGLOG")"
      if [ ! -f "$PGDATA/PG_VERSION" ]; then
        echo "Initialising PostgreSQL data directory..."
        initdb --locale=C -E UTF-8 "$PGDATA"
      fi
      # A leftover postmaster.pid from a crashed/aborted start blocks pg_ctl.
      if [ -f "$PGDATA/postmaster.pid" ] && ! pg_ctl -D "$PGDATA" status >/dev/null 2>&1; then
        echo "Removing stale postmaster.pid"
        rm -f "$PGDATA/postmaster.pid"
      fi
      if ! pg_ctl -D "$PGDATA" -l "$PGLOG" -w start; then
        echo "Could not start PostgreSQL. Last lines of $PGLOG:" >&2
        tail -20 "$PGLOG" >&2 || true
        exit 1
      fi
    fi
    echo "Note: postgresql@15 is keg-only. Add this to your shell profile to use psql/createdb directly:"
    echo "  export PATH=\"$(brew --prefix)/opt/postgresql@15/bin:\$PATH\""
  else
    sudo apt update
    sudo apt install -y postgresql-15
    sudo systemctl start postgresql
  fi
  # Give the server a moment to accept connections.
  for _ in $(seq 1 10); do
    pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" >/dev/null 2>&1 && break
    sleep 1
  done
fi

# --- 4. Database -----------------------------------------------------------
# Linux's postgresql package pre-creates a 'postgres' OS user/role and uses
# peer auth, so admin commands must run as that OS user via sudo. Homebrew's
# cluster instead makes the installing macOS user the superuser and creates
# no 'postgres' role at all, so it must be created first.
if [ "$PLATFORM" = linux ]; then
  pg_admin() { sudo -u postgres "$@"; }
else
  pg_admin() { "$@"; }
  if ! psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='postgres'" 2>/dev/null | grep -q 1; then
    echo "Creating 'postgres' superuser role..."
    createuser -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -s postgres
  fi
fi

if pg_admin psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres -lqt 2>/dev/null | cut -d'|' -f1 | grep -qw all_imprezz; then
  echo "Database 'all_imprezz' already exists"
else
  echo "Creating database 'all_imprezz'..."
  pg_admin createdb -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres all_imprezz \
    || echo "Warning: could not create database automatically — create it manually (createdb all_imprezz) and re-run." >&2
fi

pg_admin psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';" >/dev/null 2>&1 \
  || echo "Note: could not set the 'postgres' role password automatically — set it manually if needed." >&2

# --- 5. Backend --------------------------------------------------------------
echo "Installing backend dependencies (uv sync)..."
(cd "$REPO_ROOT/backend" && uv sync)
# Empty dirs aren't tracked by git; Django warns (staticfiles.W004) if it's missing.
mkdir -p "$REPO_ROOT/backend/static"
if [ -f "$REPO_ROOT/backend/.env" ]; then
  echo "backend/.env already exists, leaving it as-is"
else
  cp "$REPO_ROOT/backend/.env.example" "$REPO_ROOT/backend/.env"
  echo "Created backend/.env from backend/.env.example"
fi

# --- 6. Frontend -------------------------------------------------------------
echo "Installing frontend dependencies (npm install)..."
(cd "$REPO_ROOT/frontend" && npm install)
if [ -f "$REPO_ROOT/frontend/.env" ]; then
  echo "frontend/.env already exists, leaving it as-is"
else
  cp "$REPO_ROOT/frontend/.env.example" "$REPO_ROOT/frontend/.env"
  echo "Created frontend/.env from frontend/.env.example"
fi

cat <<EOF

Install complete.

Next steps:
  cd backend && uv run python manage.py migrate        # applied automatically by launch-app.sh too
  cd backend && uv run python manage.py createsuperuser # create an admin user (interactive, run once)

Then start the app:
  ./scripts/launch-app.sh
EOF
