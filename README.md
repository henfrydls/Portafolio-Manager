# Portfolio Manager (Django)

A professional portfolio and blog platform for developers and technology consultants. The application is built on Django 5.2, ships with a modern front-end, and includes tooling to manage projects, blog posts, skills, languages, and resumes from a friendly admin dashboard. English and Spanish translations are handled through django-parler with optional LibreTranslate automation.

> Important: All runtime configuration (branding, personal data, content catalogs, etc.) is managed through environment variables and the Django admin. Edit the codebase only when you want to extend features or adjust the layout.

## Repository

- GitHub: https://github.com/henfrydls/Portafolio-Manager.git
- Default branch: `main`

## Highlights

- Responsive portfolio layout with fixed sidebar navigation.
- Admin analytics dashboard summarizing visits, inbox messages, and catalog stats.
- Project catalog with rich metadata, ordering, visibility control, and knowledge base links.
- Medium-style blog with categories, tags, featured images, and publication workflow.
- Resume module that renders a public HTML profile and generates PDF downloads.
- Secure contact form with rate limiting, server-side validation, and inbox management.
- Automatic translation pipeline (EN/ES) powered by django-parler and LibreTranslate.
- Hardened uploads with file-type checks, image optimization, and safe storage.
- SEO helpers including sitemaps, canonical metadata, and structured data snippets.

## Technology Stack

- Django 5.2 LTS
- SQLite for local development (swap for PostgreSQL in production)
- Bootstrap-based theme bundled with WhiteNoise for static delivery
- Pillow for image processing
- Optional Docker Compose stack for LibreTranslate integration

## Prerequisites

- Python 3.10+
- pip
- Git
- (optional) Docker Desktop 4.0+ if you plan to run the compose stack

## Quick Start

```bash
# Clone the repository
git clone https://github.com/henfrydls/Portafolio-Manager.git
cd Portafolio-Manager

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install --upgrade pip
pip install -r requirements/development.txt
```

Copy the example environment file and customise the values:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

Minimum variables to review:

- `SECRET_KEY`: generate a unique value (`python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`)
- `DEBUG=True` for local development
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- Email settings if you need outbound notifications

Initialize the database and start the development server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Visit the following URLs:

- Portfolio: <http://127.0.0.1:8000/>
- Admin dashboard: <http://127.0.0.1:8000/admin/>

## Resumen en Español (local, Docker y despliegue)

- **Requisitos**: Python 3.10+, pip, Git. Opcional: Docker Desktop si usarás Compose.
- **Local (virtualenv)**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements/development.txt
  cp .env.example .env
  python manage.py migrate && python manage.py collectstatic --noinput
  python manage.py runserver
  ```
- **Docker Compose (Postgres + Redis + LibreTranslate)**:
  ```bash
  cp .env.example .env
  # opcional: ajusta DATABASE_URL/REDIS_URL en .env
  docker compose up --build
  ```
- **Docker Compose con Nginx (staging/prod-like)**:
  ```bash
  # expone la app en http://127.0.0.1:8080
  docker compose --profile staging up --build
  # o docker compose --profile prod up --build
  ```
- **Producción / staging (EC2 + Gunicorn + Nginx, Postgres, Redis)**:
  1) Define `.env` con `DJANGO_SETTINGS_MODULE=config.settings.production`, `DATABASE_URL` (Postgres/RDS), `REDIS_URL`, dominios y correo.  
  2) En el servidor: instala deps del sistema, crea venv, `pip install -r requirements/base.txt`.  
  3) Ejecuta `python manage.py collectstatic --noinput && python manage.py migrate` y crea superusuario o usa `populate_test_data`.  
  4) Levanta Gunicorn y configura Nginx como proxy con TLS.
  - Para staging usa `DJANGO_SETTINGS_MODULE=config.settings.staging` y variables `STAGING_DOMAIN`, `ALLOWED_HOSTS_STAGING`, `CSRF_TRUSTED_ORIGINS_STAGING`, `DATABASE_URL`/`REDIS_URL` de tu entorno de pruebas. Puedes usar el perfil `--profile staging` en Compose para simular el proxy Nginx en http://127.0.0.1:8080.

## Docker Compose (Optional)

### Development Mode (with `docker-compose.override.yml`)

Run the full stack with Django port 8000 exposed for direct access:

```bash
cp .env.example .env          # or use copy on Windows
# Optional: override DATABASE_URL/REDIS_URL in .env for local
docker compose up --build
```

**Services in Development:**

- Django app (Gunicorn): <http://127.0.0.1:8000/> ✅ Direct access
- Postgres: `db` service (internal only)
- Redis: `redis` service (internal only)
- LibreTranslate: internal only (web reaches it at `http://libretranslate:5000`)

**How it works:** The `docker-compose.override.yml` file automatically exposes port 8000 in development mode. This file is automatically merged when you run `docker compose up`.

### Staging/Production Mode (production-like)

Run with Nginx as reverse proxy (no direct Django access):

**IMPORTANT:** Must use `-f docker-compose.yml` to ignore the override file.

```bash
# Staging (MUST include -f to ignore override)
docker compose -f docker-compose.yml --profile staging up --build

# Production (MUST include -f to ignore override)
docker compose -f docker-compose.yml --profile prod up --build
```

**Services in Staging/Prod:**

- Django app (Gunicorn): Port 8000 (internal only) ❌ No direct access
- Nginx: <http://127.0.0.1:8080/> ✅ Only access point
- Postgres: `db` service (internal only)
- Redis: `redis` service (internal only)
- LibreTranslate: internal only

**How it works:** Using `-f docker-compose.yml` explicitly ignores the override file, so port 8000 is NOT exposed to the host. All traffic goes through Nginx on port 8080.

### 🌐 How Ports Work: From `localhost:8080` to `tudominio.com`

**Question:** Why do we use `:8080` locally but production URLs like `tudominio.com` don't have a port?

**Answer:** HTTP/HTTPS have **default ports** that browsers automatically use:

| Protocol | Default Port | What You Type | What Browser Uses |
|----------|--------------|---------------|-------------------|
| HTTP     | 80           | `http://tudominio.com` | `http://tudominio.com:80` |
| HTTPS    | 443          | `https://tudominio.com` | `https://tudominio.com:443` |

**Local Development/Staging:**
```
http://localhost:8080/
```
- Port 8080 is needed because port 80 requires admin privileges
- Nginx listens on port 8080 and forwards to Django on port 8000 (internal)

**Production (Real Server):**
```
https://tudominio.com/  (automatically uses port 443)
```
- Nginx listens on **port 443** (HTTPS) with SSL certificate
- Nginx forwards requests to Django on port 8000 (internal, not exposed)
- Users never see `:443` because it's the default HTTPS port

**The Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT                             │
├─────────────────────────────────────────────────────────────────┤
│ Browser → http://localhost:8000 → Django (direct)               │
│ Browser → http://localhost:8080 → Nginx → Django (port 8000)    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    STAGING (Local Testing)                      │
├─────────────────────────────────────────────────────────────────┤
│ Browser → http://localhost:8080 → Nginx → Django (port 8000)    │
│ (port 8000 NOT accessible from outside)                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  PRODUCTION (Real Server)                       │
├─────────────────────────────────────────────────────────────────┤
│ Browser → https://tudominio.com → Nginx:443 → Django (port 8000)│
│ (port 8000 NOT accessible from internet)                        │
│ (port 443 is default HTTPS, so users don't type it)             │
└─────────────────────────────────────────────────────────────────┘
```

**Key Takeaways:**
- **Development:** Direct access to Django on port 8000 for debugging
- **Staging:** Production-like with Nginx on custom port 8080 (since 80 needs admin)
- **Production:** Nginx on port 443 (HTTPS) - invisible to users because it's the default

Data volumes:

- Postgres: `pgdata`
- Redis: `redisdata`

Useful commands:

```bash
# Run migrations (already executed on startup, but re-run manually if needed)
docker compose exec web python manage.py migrate
# Seed demo data
docker compose exec web python manage.py populate_test_data
# Create superuser
docker compose exec web python manage.py createsuperuser
# Environment sanity check (runs automatically on container start)
# docker compose exec web python manage.py check_env
# With Nginx profile (staging/prod-like) listening on 8080
# docker compose --profile staging up --build
# If you need to test LibreTranslate manually, temporarily expose its port in docker-compose.yml:
#   libretranslate:
#     ports:
#       - "5000:5000"
# and revert it when done to keep it internal.
```

Stop the stack with `docker compose down` (add `-v` to drop data volumes).

## Initial Configuration Checklist

1. Sign in to the Django admin and complete your **Profile** record.
2. Review the autogenerated catalog entries (project types, categories, knowledge bases). They are seeded via migrations; if you re-run migrations on a fresh database you will always get exactly one record per slug.
3. Add projects, blog posts, skills, experiences, languages, and resume entries.
4. Configure **Dashboard -> Settings** to enable automatic translations. Point `translation_api_url` to LibreTranslate (local or hosted) and toggle `auto_translate_enabled`.
5. Test the public website and contact form to confirm emails and analytics tracking are working.

## Documentation Index

- `DOCKER_COMMANDS.md`: **quick reference for Docker Compose commands** (development, staging, production).
- `docs/SETUP.md`: detailed installation, troubleshooting, and maintenance guide.
- `docs/CONFIGURATION_GUIDE.md`: environment variables, production hints, and security settings.
- `docs/ADMIN_USAGE.md`: workflows for managing profile, projects, blog posts, and catalogs.
- `docs/EMAIL_SETUP.md`: SMTP configuration for Gmail, Outlook, and custom providers.
- `docs/TEST_DATA.md`: using the management command to populate sample content.
- `docs/DOCUMENTATION_INDEX.md`: master table of contents that links every guide.

## Developer Utilities

- Run tests: `python manage.py test`
- Seed demo content (local shell): `python manage.py populate_test_data`
- Seed demo content (Docker): `docker compose exec web python manage.py populate_test_data`
- Reset demo content: delete `db_development.sqlite3` or run `python manage.py populate_test_data --reset`
- Review translation status: `python verify_translations.py`

## Production Considerations

- Set `DEBUG=False`, configure strong `SECRET_KEY`, and lock down `ALLOWED_HOSTS`.
- Switch the database to a managed service (PostgreSQL recommended) and update `.env`.
- Use Redis for cache/sessions/rate limits when available (`REDIS_URL`, `USE_CACHE_SESSIONS`).
- Serve static files via Nginx + Gunicorn (or keep WhiteNoise) and enable HTTPS/TLS.
- Configure media storage (local disk for small installs, or S3/Blob + CDN).
- Use HTTPS and apply Django security middleware settings (`SECURE_*`, `SESSION_COOKIE_SECURE`, etc.).
- Provision a robust email backend (e.g., SendGrid, Mailgun, SES).
- Add monitoring/logging (Sentry, ELK, or similar) as part of your deployment pipeline.

### EC2 Quick Recipe (Postgres + Redis + Gunicorn + Nginx)

1) Copy `.env.example` to `.env`, set `DJANGO_SETTINGS_MODULE=config.settings.production`, `DATABASE_URL` (PostgreSQL/RDS), `DB_SSL_REQUIRED=True` if needed, `REDIS_URL`, `ALLOWED_HOSTS_PROD`, `CSRF_TRUSTED_ORIGINS_PROD`, `PRODUCTION_DOMAIN`, and email creds.  
2) Install system deps: `sudo apt-get install build-essential libpq-dev nginx` (plus `certbot` if using Let’s Encrypt).  
3) Install Python deps: `python -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements/base.txt`.  
4) Build assets/data: `python manage.py collectstatic --noinput && python manage.py migrate` and create an admin user (`createsuperuser`) or seed demo data (`populate_test_data`).  
5) Run Gunicorn (example): `gunicorn config.wsgi:application --bind unix:/run/portfolio.sock --workers 3 --timeout 60`.  
6) Nginx (example): serve `/static` and `/media`, proxy `/` to `unix:/run/portfolio.sock`, set `proxy_set_header X-Forwarded-Proto https`, and enable TLS.  
7) Repeat with separate `.env`/RDS/Redis for staging using `DJANGO_SETTINGS_MODULE=config.settings.staging` and a different domain.

## Contributing

Issues and pull requests are welcome. Please describe the motivation for changes and reference any relevant documentation updates in your PR.

## License

This project is available under the MIT License. See [LICENSE](https://github.com/henfrydls/Portafolio-Manager/blob/main/LICENSE) for the full text.
