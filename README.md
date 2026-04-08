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

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Quick Start

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

### Stopping

```bash
docker compose down
```

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
