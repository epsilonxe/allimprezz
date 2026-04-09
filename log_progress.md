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

## 2026-04-09

- Added Tailwind CSS 4 with `@tailwindcss/vite` plugin for frontend styling
- Added superuser role above admin in role hierarchy; admins and superusers both pass IsAdmin permission
- Superusers are hidden from user list and cannot be managed by admins
- Added user detail endpoint (`/users/<id>/`) with update and delete (admin-only, self-delete prevented)
- Added password change endpoint (`/accounts/profile/password/`) for authenticated users
- Added UserUpdateSerializer (role, name, is_active) and PasswordChangeSerializer with validation
- Frontend: added user management pages (list, create, detail/edit) under `/admin/users/`
- Frontend: added profile page with password change at `/profile`
- Frontend: added users API module and Pinia users store
- Frontend: added shared navigation bar in App.vue with logout and role badge
- Frontend: added admin route guard (`requiresAdmin` meta) in Vue Router
- Frontend: restyled login and dashboard views with Tailwind CSS
- Docker Compose: added PostgreSQL healthcheck, backend waits for healthy db
- Docker Compose: switched frontend node_modules to a named volume



