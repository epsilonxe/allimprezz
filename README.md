# All Imprezz Co., Ltd. — Business Management System

A web application for tours and travel business management.

## Tech Stack

| Layer          | Technology              |
| -------------- | ----------------------- |
| Backend        | Django (Python 3.12)    |
| Frontend       | Vue.js 3 + Vite (Node 22) |
| Database       | PostgreSQL 15           |
| Auth           | JWT (djangorestframework-simplejwt) |
| Infrastructure | Docker Compose          |
| Tooling        | pip (Python), npm (Node) |

## Project Structure

```
all_imprezz/
├── backend/            # Django REST API
│   ├── config/         # Settings, URLs, WSGI/ASGI
│   ├── apps/           # Feature modules (Django apps)
│   │   └── accounts/   # Auth, User model, JWT, permissions
│   ├── libs/           # Pure Python business logic
│   │   └── auth/       # Roles, password validation, token utils
│   ├── static/         # Static files
│   ├── templates/      # Server-side templates (if any)
│   └── tests/          # Backend tests
├── frontend/           # Vue.js SPA
│   ├── src/
│   │   ├── api/        # API client modules
│   │   ├── components/ # Reusable UI components
│   │   ├── views/      # Page components
│   │   ├── router/     # Vue Router configuration
│   │   └── stores/     # Pinia state stores
│   └── public/         # Static public assets
└── docs/               # Documentation
```

## Getting Started

You can run the app either with Docker Compose (recommended) or natively on your machine.

### Option A: Docker Compose

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

#### Quick Start

1. Build and start all services:

```bash
docker compose up --build
```

2. Run migrations (first time only):

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

3. Open the application:

| Service        | URL                          |
| -------------- | ---------------------------- |
| Frontend (UI)  | http://localhost:5173         |
| Backend (API)  | http://localhost:8000         |
| Django Admin   | http://localhost:8000/admin/  |

The frontend automatically proxies `/api` requests to the backend.

#### Stopping

```bash
docker compose down
```

### Option B: Local Installation (without Docker)

A full walkthrough from cloning the repo to running both servers, with commands for **macOS** (Homebrew) and **Linux** (Ubuntu/Debian, apt). If you already have uv, Node.js 22, and PostgreSQL 15 installed, skip to [step 5](#5-set-up-the-database).

> **Prefer a script?** After cloning, run `./scripts/install.sh`, then `./scripts/launch-app.sh` (stop with `./scripts/terminate-app.sh`) instead of the manual steps below. See [Scripts](#scripts) for details.

#### 1. Clone the repository

```bash
git clone <repo-url>
cd all_imprezz
```

#### 2. Install uv

Same install script on both OSes — uv manages the Python 3.12 interpreter and virtual environment for you:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 3. Install Node.js 22

- **macOS:**
  ```bash
  brew install node@22
  ```
- **Linux (Ubuntu/Debian):**
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```

#### 4. Install and start PostgreSQL 15

- **macOS:**
  ```bash
  brew install postgresql@15
  brew services start postgresql@15
  ```
  `postgresql@15` is keg-only on macOS, so `psql`/`createdb` won't be on your `PATH` afterward. Add this to your shell profile (`~/.zshrc`/`~/.bashrc`):
  ```bash
  export PATH="$(brew --prefix)/opt/postgresql@15/bin:$PATH"
  ```
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt install -y postgresql-15
  sudo systemctl start postgresql
  ```

#### 5. Set up the database

Create a database and role matching `backend/.env.example` (or adjust the env vars later to match your own setup):

- **macOS:** Homebrew's cluster makes the installing user the superuser and doesn't create a `postgres` role — create one first:
  ```bash
  createuser -s postgres
  createdb -U postgres all_imprezz
  psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"
  ```
- **Linux (Ubuntu/Debian):** the `postgres` role already exists; run commands as that OS user via `sudo`:
  ```bash
  sudo -u postgres createdb all_imprezz
  sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
  ```

> On Linux, PostgreSQL defaults to peer authentication for the `postgres` OS user — if the commands above fail with a role/permission error, prefix them with `sudo -u postgres` (e.g. `sudo -u postgres createdb all_imprezz`).

#### 6. Backend: install dependencies, configure, and run

```bash
cd backend
```

Install dependencies (uv provisions Python 3.12 and creates `.venv` automatically):

```bash
uv sync
```

Configure environment:

```bash
cp .env.example .env       # edit if your local Postgres differs from the defaults
```

Run migrations and create an admin user:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
```

Start the server:

```bash
uv run python manage.py runserver
```

> `backend/pyproject.toml`/`uv.lock` drive this native uv workflow; `backend/requirements.txt` remains the dependency source for the Docker image. Add new dependencies to both when they change.

#### 7. Frontend: install dependencies and run

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

By default the frontend dev server proxies `/api` to `http://localhost:8000`, matching the backend above — no extra configuration needed. If your backend runs elsewhere, copy `frontend/.env.example` to `.env` and export `API_URL` before starting Vite (e.g. `export API_URL=http://localhost:8000 && npm run dev`).

#### 8. Open the application

Same URLs as the Docker setup:

| Service        | URL                          |
| -------------- | ---------------------------- |
| Frontend (UI)  | http://localhost:5173         |
| Backend (API)  | http://localhost:8000         |
| Django Admin   | http://localhost:8000/admin/  |

#### LAN access

`./scripts/launch-app.sh` binds the frontend to all interfaces (`--host 0.0.0.0`) and prints a `LAN:` URL if it can detect the machine's IP, so other devices on the same network can reach it. If that doesn't work:

- **macOS Firewall:** the first time `python`/`node` bind a listening socket, macOS may prompt "Allow incoming connections?" — accept it. If it was previously denied, check System Settings → Network → Firewall.
- **CORS for direct API calls:** the frontend normally talks to the backend through Vite's same-origin `/api` proxy, so this usually isn't needed. But if something calls the backend directly from a LAN browser, add that origin to `backend/.env`'s `DJANGO_CORS_ALLOWED_ORIGINS` (comma-separated) and restart the backend.
- **Same network:** confirm the client device is on the same Wi-Fi/subnet, and that the network doesn't have client/AP isolation enabled (common on guest Wi-Fi).
- **Right IP:** use the host machine's LAN IP (e.g. `192.168.x.x`), not `localhost`.

### Scripts

`scripts/` automates the manual steps in Option B above:

| Script | What it does |
| ------ | ------------ |
| `./scripts/install.sh` | Installs uv, Node.js 22, and PostgreSQL 15 if missing, creates the `all_imprezz` database, and installs backend/frontend dependencies. Safe to re-run. |
| `./scripts/launch-app.sh` | Runs migrations, starts both dev servers in the background, waits for them to become healthy, prints access URLs, then stays running as a live health monitor (Ctrl+C stops the monitor only — the app keeps running). |
| `./scripts/terminate-app.sh` | Stops both dev servers. |

Logs and PID files are written to `scripts/.run/` (gitignored). After `install.sh`, run `uv run python manage.py createsuperuser` from `backend/` once to create an admin user before logging into `/admin/`.

## Database Backup & Restore

Use `pg_dump`/`pg_restore` (logical backups) rather than copying the data directory while the server is running. The database is `all_imprezz`, role `postgres` (see `backend/.env`).

### Where the data lives

| Setup | Location |
| ----- | -------- |
| Docker Compose | `postgres_data` named volume (mounted at `/var/lib/postgresql/data` in the `db` container) |
| macOS (Homebrew) | `/opt/homebrew/var/postgresql@15` (Intel: `/usr/local/var/postgresql@15`) |
| Linux (apt) | `/var/lib/postgresql/15/main` |

Run `psql -U postgres -c "SHOW data_directory;"` to confirm on a native install.

### Backup

Custom format (compressed, recommended):

```bash
# Native
pg_dump -h localhost -U postgres -Fc all_imprezz > all_imprezz_$(date +%F).dump

# Docker Compose
docker compose exec -T db pg_dump -U postgres -Fc all_imprezz > all_imprezz_$(date +%F).dump
```

On Linux with peer auth, prefix native commands with `sudo -u postgres` (and write the file somewhere that user can access, e.g. `/tmp`).

### Restore

Stop the backend first so nothing is connected, then drop and recreate the database:

```bash
# Native
dropdb -h localhost -U postgres --if-exists all_imprezz
createdb -h localhost -U postgres all_imprezz
pg_restore -h localhost -U postgres -d all_imprezz --no-owner all_imprezz_2026-01-01.dump

# Docker Compose
docker compose exec -T db dropdb -U postgres --if-exists all_imprezz
docker compose exec -T db createdb -U postgres all_imprezz
docker compose exec -T db pg_restore -U postgres -d all_imprezz --no-owner < all_imprezz_2026-01-01.dump
```

> Restoring **replaces all current data**. Take a fresh backup first if unsure. After restoring onto a newer code version, run `python manage.py migrate` (`uv run` natively, `docker compose exec backend` in Docker).

Plain SQL dumps (`pg_dump ... > file.sql`) restore with `psql -U postgres -d all_imprezz -f file.sql` instead of `pg_restore`.

### Moving to another machine

Back up on the source, copy the `.dump` file across (e.g. `scp`), then restore on the target after `./scripts/install.sh` has created the empty `all_imprezz` database (use `--clean --if-exists` with `pg_restore` instead of dropping it manually).

## API

The backend exposes a REST API under `/api/`.

### Authentication (`/api/accounts/`)

| Endpoint | Method | Auth | Description |
| -------- | ------ | ---- | ----------- |
| `/api/accounts/auth/login/` | POST | No | Obtain JWT access + refresh tokens |
| `/api/accounts/auth/refresh/` | POST | No | Refresh access token |
| `/api/accounts/auth/logout/` | POST | Yes | Blacklist refresh token |
| `/api/accounts/users/` | GET | Admin | List all users |
| `/api/accounts/users/create/` | POST | Admin | Create a new user |
| `/api/accounts/profile/` | GET, PATCH | Yes | View/update own profile |

### Planned Endpoints

| Prefix | Description |
| ------ | ----------- |
| `/api/tours/` | Tour management |
| `/api/bookings/` | Booking operations |
| `/api/customers/` | Customer management |

## Commands Reference

### Docker Compose

| Command | Description |
| ------- | ----------- |
| `docker compose up --build` | Build and start all services |
| `docker compose up -d` | Start in detached mode |
| `docker compose down` | Stop all services |
| `docker compose logs -f <service>` | Follow logs (backend, frontend, db) |
| `docker compose exec backend python manage.py test` | Run all backend tests |
| `docker compose exec backend python manage.py migrate` | Apply migrations |
| `docker compose exec backend python manage.py createsuperuser` | Create admin user |
| `docker compose exec backend python manage.py makemigrations` | Generate migration files |

## License

Proprietary — All Imprezz Co., Ltd.
