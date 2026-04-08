# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

All Imprezz Co., Ltd. — a tours and travel company business management web application.
Monorepo with Django backend, Vue.js frontend, and PostgreSQL database.

## Architecture

- **`backend/`** — Django project (Python 3.12, containerized via Docker)
  - `config/` — Django settings, URLs, WSGI/ASGI entry points
  - `apps/` — Django apps (each app is a self-contained feature module)
    - `accounts/` — Authentication, custom User model, JWT endpoints, role-based permissions
  - `libs/` — Pure Python business logic (no Django imports)
    - `auth/` — RoleManager, PasswordValidator, TokenPayloadBuilder
  - `tests/` — Backend test suite
- **`frontend/`** — Vue.js SPA
  - `src/api/` — API client modules (Axios calls to Django REST endpoints)
  - `src/views/` — Page-level Vue components (mapped to routes)
  - `src/components/` — Reusable UI components
  - `src/router/` — Vue Router config
  - `src/stores/` — Pinia state management
- **`docs/`** — Project documentation

## Tech Stack

- **Backend:** Django + Django REST Framework + SimpleJWT + psycopg (PostgreSQL adapter)
- **Frontend:** Vue 3 + Vite + Pinia + Vue Router (Node 22)
- **Database:** PostgreSQL 15
- **Infrastructure:** Docker Compose (all services containerized)
- **Auth:** JWT-based (djangorestframework-simplejwt), custom User model with email login, role-based access (admin/staff/agent)
- **Python dependencies:** `requirements.txt` + pip (inside Docker)

## Commands

### Docker Compose (primary development method)

```bash
# Start all services (backend, frontend, database)
docker compose up --build

# Start in detached mode
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Run Django management commands inside container
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py test

# Run a single test module
docker compose exec backend python manage.py test apps.<app_name>.tests

# Create a new Django app
docker compose exec backend bash -c "cd apps && python ../manage.py startapp <app_name>"

# Install a new Python package
docker compose exec backend pip install <package>
# Then add it to backend/requirements.txt and rebuild:
docker compose up --build backend
```

## Development Philosophy

Library-first, test-second, integrate-third. Every feature follows this workflow:

1. **Write the library** — Pure Python modules in `backend/libs/`. No Django imports. Business logic lives here as standalone, reusable scripts.
2. **Write tests** — Test the library in isolation before touching Django. Tests go in `backend/libs/tests/`.
3. **Integrate into Django** — Import the tested library into Django apps (`backend/apps/`). Django handles HTTP, serialization, and routing — not business logic.

The frontend (Vue.js) is strictly UI and interactions. It calls the Django REST API but contains no business logic.

## Conventions

- Each Django app lives under `backend/apps/` as a self-contained module
- Business logic lives in `backend/libs/` as pure Python — never in views or serializers
- Frontend API calls are centralized in `frontend/src/api/`
- PostgreSQL is the primary database — use Django's built-in ORM with psycopg adapter
- Commit messages should not mention AI or Claude
