# Setup Guide – Portfolio Manager

This guide walks you through installing, configuring, and maintaining the Portfolio Manager project.

## Resumen rápido en Español

- Clona el repositorio y crea un entorno virtual:
  ```bash
  git clone https://github.com/henfrydls/Portafolio-Manager.git
  cd Portafolio-Manager
  python -m venv .venv
  source .venv/bin/activate  # en Windows: .venv\Scripts\activate
  ```
- Instala dependencias y configura variables:
  ```bash
  pip install --upgrade pip
  pip install -r requirements/development.txt
  cp .env.example .env
  ```
- Prepara la base de datos y estáticos:
  ```bash
  python manage.py migrate
  python manage.py collectstatic --noinput
  python manage.py createsuperuser  # o populate_test_data
  python manage.py runserver
  ```
- Docker Compose (Postgres + Redis + LibreTranslate):
  ```bash
  cp .env.example .env
  # Modo desarrollo (puerto 8000 expuesto)
  docker compose up --build
  # Modo staging/prod (solo nginx en 8080)
  docker compose -f docker-compose.yml --profile staging up --build
  ```
- Despliegue tipo producción (EC2 + Gunicorn + Nginx):
  1) Ajusta `.env` con `DJANGO_SETTINGS_MODULE=config.settings.production`, `DATABASE_URL` (Postgres), `REDIS_URL`, dominios y correo.  
  2) En el servidor: instala dependencias del sistema, crea venv, `pip install -r requirements/base.txt`.  
  3) Ejecuta `collectstatic`, `migrate`, crea usuario admin o usa `populate_test_data`.  
  4) Corre Gunicorn como servicio y configura Nginx como proxy con TLS.

## 1. Prerequisites

Make sure you have the following tools:

- Python 3.10 or later
- pip
- Git
- A code editor (VS Code, PyCharm, etc.)
- Optional: Docker Desktop 4.0+ if you plan to run LibreTranslate via Docker

### Verify Installation

```bash
python --version
pip --version
git --version
```

## 2. Clone the Repository

```bash
git clone https://github.com/henfrydls/Portafolio-Manager.git
cd Portafolio-Manager
```

If you downloaded a ZIP archive, extract it and open the extracted folder instead.

## 3. Create and Activate a Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
```

You should see `(.venv)` at the beginning of your terminal prompt.

## 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements/development.txt
```

Check the installed packages if desired:

```bash
pip list
```

## 5. Configure Environment Variables

Copy the example configuration:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

Open `.env` in your editor and update:

- `SECRET_KEY` – generate a unique value (`python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`)
- `DEBUG=True` for local development
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- Email backend credentials if you need outbound mail in development
- Translation service URL (`translation_api_url`) if you will use LibreTranslate

## 6. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

This will also populate default catalog entries (categories, project types, knowledge bases).

## 7. Start the Development Server

```bash
python manage.py runserver
```

Open the following URLs:

- Portfolio: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/admin/>

Log in with the superuser you created and complete your profile, projects, and blog content.

## 8. Optional: Docker Compose Setup (Postgres + Redis + LibreTranslate)

### Development Mode (Direct Django Access)

The project includes `docker-compose.override.yml` which automatically exposes port 8000 in development:

```bash
cp .env.example .env          # ensure the file exists
docker compose up --build
```

**Access points:**
- Django app (Gunicorn): <http://127.0.0.1:8000/> ✅ Direct access
- Admin dashboard: <http://127.0.0.1:8000/admin/>
- Postgres: `db` service (internal only)
- Redis: `redis` service (internal only)
- LibreTranslate: internal only (`http://libretranslate:5000`)

### Staging/Production Mode (Nginx Only)

For production-like testing, **you MUST use `-f docker-compose.yml`** to ignore the override file.

**WARNING:** If you omit `-f docker-compose.yml`, the override file will still be loaded and port 8000 will be exposed (not production-like).

```bash
# Staging (local testing) - MUST include -f flag
docker compose -f docker-compose.yml --profile staging up --build

# Production mode - MUST include -f flag
docker compose -f docker-compose.yml --profile prod up --build
```

**Access points:**
- Nginx: <http://127.0.0.1:8080/> ✅ Only access point
- Django port 8000: Internal only (not accessible from host) ❌
- Admin dashboard: <http://127.0.0.1:8080/admin/>

**Why this setup?**
- Development needs direct Django access for debugging
- Staging/Production should only expose Nginx (production-like architecture)
- Port 8000 is never exposed to the internet in real deployments

### Data Volumes

- Postgres: `pgdata`
- Redis: `redisdata`
- Static files: `staticfiles`
- Media files: `mediafiles`

### Useful Docker Commands

```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Seed demo data
docker compose exec web python manage.py populate_test_data

# Environment sanity check (runs automatically on startup)
docker compose exec web python manage.py check_env

# View logs
docker compose logs -f web
docker compose logs -f nginx
```

Stop and remove containers with `docker compose down` (add `-v` to drop data volumes).

## 9. Useful Management Commands

```bash
python manage.py populate_test_data    # Seed demo content (local shell)
docker compose exec web python manage.py populate_test_data    # Seed demo content (Docker)
python manage.py populate_test_data --reset    # Reset seeded data (or delete db_development.sqlite3)
python manage.py list_translations     # Example custom command if added later
python verify_translations.py          # Check translation coverage
```

## 10. Troubleshooting

### Port 8000 Already in Use

```bash
python manage.py runserver 8001
```

On Windows you can find the process with:

```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

macOS / Linux:

```bash
lsof -ti:8000 | xargs kill -9
```

### Static Files Missing

```bash
python manage.py collectstatic --noinput
```

### Database Errors During Development

```bash
del db_development.sqlite3           # Windows
# rm db_development.sqlite3          # macOS / Linux
python manage.py migrate
```

### Translation Failures

- Confirm LibreTranslate is running and reachable.
- Re-run `python verify_translations.py` to identify missing locales.
- Disable `auto_translate_enabled` temporarily if the service is unavailable.

## 11. Updating the Project

```bash
git pull origin main
.venv\Scripts\activate                # or source .venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

## 12. Deploying to EC2 (PostgreSQL, Redis, Gunicorn, Nginx)

1. Copy `.env.example` to `.env` and set:  
   - `DJANGO_SETTINGS_MODULE=config.settings.production` (or `config.settings.staging` for staging)  
   - `DATABASE_URL=postgres://user:password@host:5432/dbname` (set `DB_SSL_REQUIRED=True` if RDS enforces SSL)  
   - `REDIS_URL=redis://default:password@host:6379/0` (optional but recommended for cache/sessions)  
   - `ALLOWED_HOSTS_*`, `CSRF_TRUSTED_ORIGINS_*`, `PRODUCTION_DOMAIN`, email creds.
2. Install system packages on the EC2 instance:
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential libpq-dev nginx
   ```
3. Install Python deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements/base.txt
   ```
4. Build and migrate:
   ```bash
   python manage.py collectstatic --noinput
   python manage.py migrate
   python manage.py createsuperuser  # or python manage.py populate_test_data
   ```
5. Run Gunicorn (example):
   ```bash
   gunicorn config.wsgi:application --bind unix:/run/portfolio.sock --workers 3 --timeout 60
   ```
   For production use a systemd unit to keep it running and restart on boot.
6. Configure Nginx to serve `/static` and `/media` directly and proxy `/` to the Gunicorn socket:
   ```
   location /static/ { alias /path/to/project/staticfiles/; access_log off; expires 30d; }
   location /media/  { alias /path/to/project/media/; access_log off; expires 30d; }
   location / { proxy_pass http://unix:/run/portfolio.sock:; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto https; }
   ```
   Enable TLS (Let’s Encrypt/Certbot or ACM behind a load balancer).
7. Repeat with separate `.env`, databases, Redis, and domain for staging using `config.settings.staging`.

## 13. Next Steps

1. Review `docs/ADMIN_USAGE.md` to learn the admin workflows.
2. Customize branding, colors, and copy through the admin.
3. Set up a production environment with HTTPS, a managed database, and persistent media storage.

---

Your development environment is now ready. Enjoy building your portfolio!
