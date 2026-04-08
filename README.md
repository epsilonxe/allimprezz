# All Imprezz Co., Ltd. — Business Management System

A web application for tours and travel business management.

## Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Backend  | Django (Python 3.12)    |
| Frontend | Vue.js 3 + Vite         |
| Database | PostgreSQL              |
| Tooling  | uv (Python), npm (Node) |

## Project Structure

```
all_imprezz/
├── backend/            # Django REST API
│   ├── config/         # Settings, URLs, WSGI/ASGI
│   ├── apps/           # Feature modules (Django apps)
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

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 18+
- PostgreSQL 15+

### Backend Setup

```bash
cd backend
uv sync                              # Install Python dependencies
uv run python manage.py migrate      # Run database migrations
uv run python manage.py runserver    # Start dev server at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install          # Install Node dependencies
npm run dev          # Start dev server at http://localhost:5173
```

## API

The backend exposes a REST API under `/api/`. Detailed endpoint documentation will be added as features are implemented.

| Prefix        | Description              |
| ------------- | ------------------------ |
| `/api/auth/`  | Authentication endpoints |
| `/api/tours/` | Tour management          |
| `/api/bookings/` | Booking operations    |
| `/api/customers/` | Customer management  |

## Commands Reference

### Backend

| Command | Description |
| ------- | ----------- |
| `uv sync` | Install/update Python dependencies |
| `uv run python manage.py runserver` | Start development server |
| `uv run python manage.py test` | Run all tests |
| `uv run python manage.py test apps.<name>.tests` | Run tests for a specific app |
| `uv run python manage.py makemigrations` | Generate migration files |
| `uv run python manage.py migrate` | Apply migrations |
| `uv run python manage.py createsuperuser` | Create admin user |

### Frontend

| Command | Description |
| ------- | ----------- |
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run tests |
| `npm run lint` | Lint and fix files |

## License

Proprietary — All Imprezz Co., Ltd.
