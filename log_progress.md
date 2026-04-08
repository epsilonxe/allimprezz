# Progress Log

## 2026-04-08

- Initialized project repository
- Created monorepo structure: `backend/` (Django), `frontend/` (Vue.js), `docs/`
- Added README.md, CLAUDE.md, todo.md, log_progress.md
- Switched database from MongoDB to PostgreSQL
- Initialized Django project (Django 5.2, DRF, psycopg, django-cors-headers)
- Initialized Vue.js project (Vue 3, Vite, Pinia, Vue Router, Vitest, ESLint, Prettier)
- Set up Axios API client and Vite dev proxy to Django backend
- Added Docker Compose infrastructure (backend, frontend, PostgreSQL services)
- Dockerfiles for backend (Python 3.12 + uv) and frontend (Node 18)
- Django settings now read database config from environment variables
- Removed uv — using pip + requirements.txt inside Docker containers
