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
- Implemented Authentication & Users feature:
  - Created pure Python auth library (`libs/auth/`): RoleManager, PasswordValidator, TokenPayloadBuilder
  - Added djangorestframework-simplejwt for JWT authentication
  - Created custom User model with email-based login and roles (admin/staff/agent)
  - Built accounts Django app with login, logout, token refresh, user CRUD, and profile endpoints
  - Role-based permissions: IsAdmin, IsStaffUser, IsAgent
  - Frontend: login page, dashboard, Pinia auth store, Axios JWT interceptors, route guards
  - 20 pure Python unit tests for auth library
  - Django integration tests for all auth endpoints
- Fixed Vite 8 dev server issues:
  - Added `server.allowedHosts: true` to vite.config.js for Docker compatibility
  - Set `API_URL: http://backend:8000` in docker-compose.yml for Vite proxy to reach backend
