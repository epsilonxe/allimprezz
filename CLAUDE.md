# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

All Imprezz Co., Ltd. — a tours and travel company business management web application.
Monorepo with Django backend, Vue.js frontend, and PostgreSQL database.

## Architecture

- **`backend/`** — Django project (Python 3.12, managed with `uv`)
  - `config/` — Django settings, URLs, WSGI/ASGI entry points
  - `apps/` — Django apps (each app is a self-contained feature module)
  - `tests/` — Backend test suite
- **`frontend/`** — Vue.js SPA
  - `src/api/` — API client modules (Axios calls to Django REST endpoints)
  - `src/views/` — Page-level Vue components (mapped to routes)
  - `src/components/` — Reusable UI components
  - `src/router/` — Vue Router config
  - `src/stores/` — Pinia state management
- **`docs/`** — Project documentation

## Tech Stack

- **Backend:** Django + Django REST Framework + psycopg (PostgreSQL adapter)
- **Frontend:** Vue 3 + Vite + Pinia + Vue Router
- **Database:** PostgreSQL
- **Python tooling:** `uv` (package manager and virtualenv)

## Commands

### Backend

```bash
# Install dependencies
cd backend && uv sync

# Run development server
uv run python manage.py runserver

# Run all backend tests
uv run python manage.py test

# Run a single test module
uv run python manage.py test apps.<app_name>.tests

# Create a new Django app
cd backend/apps && uv run python ../manage.py startapp <app_name>

# Database migrations
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Frontend

```bash
# Install dependencies
cd frontend && npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint
npm run lint
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
