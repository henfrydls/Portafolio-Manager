# Setup Guide – Portfolio Manager

This guide walks you through installing, configuring, and maintaining the Portfolio Manager project.

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

## 8. Optional: Docker Compose Setup

If you want LibreTranslate running locally:

```bash
cp .env.example .env          # ensure the file exists
docker compose up --build
```

Services exposed:

- Django app: <http://127.0.0.1:8000/>
- LibreTranslate: <http://127.0.0.1:5000/>

Stop and remove containers with `docker compose down`.

## 9. Useful Management Commands

```bash
python manage.py populate_test_data    # Seed demo content
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

## 12. Next Steps

1. Review `docs/ADMIN_USAGE.md` to learn the admin workflows.
2. Customize branding, colors, and copy through the admin.
3. Set up a production environment with HTTPS, a managed database, and persistent media storage.

---

Your development environment is now ready. Enjoy building your portfolio!
