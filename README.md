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

### Scripts

`scripts/` automates the manual steps in Option B above:

| Script | What it does |
| ------ | ------------ |
| `./scripts/install.sh` | Installs uv, Node.js 22, and PostgreSQL 15 if missing, creates the `all_imprezz` database, and installs backend/frontend dependencies. Safe to re-run. |
| `./scripts/launch-app.sh` | Runs migrations, starts both dev servers in the background, waits for them to become healthy, prints access URLs, then stays running as a live health monitor (Ctrl+C stops the monitor only — the app keeps running). |
| `./scripts/terminate-app.sh` | Stops both dev servers. |

Logs and PID files are written to `scripts/.run/` (gitignored). After `install.sh`, run `uv run python manage.py createsuperuser` from `backend/` once to create an admin user before logging into `/admin/`.

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
