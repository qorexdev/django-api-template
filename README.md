# django-api-template

Production-ready Django REST API starter with JWT auth, Docker, PostgreSQL, Redis, and Celery.

## Stack

- **Django 5** + Django REST Framework
- **PostgreSQL** — primary database
- **Redis** + **Celery** — async task queue
- **SimpleJWT** — access + refresh token auth
- **drf-spectacular** — auto OpenAPI docs (Swagger + Redoc)
- **Docker Compose** — one-command local setup
- **GitHub Actions** — CI with lint + tests

## Quick Start

```bash
git clone https://github.com/qorexdev/django-api-template
cd django-api-template
cp .env.example .env
docker compose up --build
```

API available at `http://localhost:8000`
Swagger docs: `http://localhost:8000/api/docs/`
Admin panel: `http://localhost:8000/admin/`

## API Endpoints

### Auth
| Method | URL | Description |
|:---|:---|:---|
| `POST` | `/api/v1/auth/register/` | Register new user |
| `POST` | `/api/v1/auth/login/` | Login, get JWT tokens |
| `POST` | `/api/v1/auth/logout/` | Logout, blacklist refresh token |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh access token |

### Users
| Method | URL | Description |
|:---|:---|:---|
| `GET` | `/api/v1/users/me/` | Get current user profile |
| `PATCH` | `/api/v1/users/me/` | Update profile |
| `PUT` | `/api/v1/users/me/change-password/` | Change password |

## Example Requests

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user","password":"Pass1234!","password2":"Pass1234!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass1234!"}'

# Get profile (with token)
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

## Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
pytest

# Lint
ruff check .
```

## Project Structure

```
django-api-template/
├── app/
│   ├── core/               # settings, urls, wsgi, celery
│   └── users/              # user model, auth endpoints
├── .github/workflows/      # CI pipeline
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Docker

The project runs 5 services via Docker Compose: `web` (Django + gunicorn), `db` (PostgreSQL 16), `redis`, `celery` worker, and `celery-beat` scheduler.

```bash
cp .env.example .env   # edit as needed
docker compose up -d --build
```

This runs migrations and collectstatic automatically on startup.

To check logs:
```bash
docker compose logs -f web
docker compose logs -f celery
```

Stop everything:
```bash
docker compose down        # keeps data
docker compose down -v     # wipes volumes (db, static, media)
```

`.env.example` has all the env vars you need — `DATABASE_URL` and `REDIS_URL` point to the compose services by default, so it works out of the box.

## Adding a New App

```bash
python manage.py startapp myapp app/myapp
```

Register in `app/core/settings.py` under `LOCAL_APPS`.

---

<p align="center">
  <sub>developed by qorex &nbsp;
    <a href="https://github.com/qorexdev">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:middle;opacity:0.6">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
      </svg>
    </a>
    &nbsp;
    <a href="https://t.me/qorexdev">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:middle;opacity:0.6">
        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.537-.194 1.006.131.833.941z"/>
      </svg>
    </a>
  </sub>
</p>
