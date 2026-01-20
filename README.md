<div align="center">
  <img src="static/images/logo/logo.svg" alt="Portfolio Manager Logo" width="120" height="120">

  # Portfolio Manager

  [![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
</div>

Portfolio and blog platform for developers. Built with Django 5.2, includes project catalog, blog, resume module, contact form, and automatic EN/ES translations.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/henfrydls/Portafolio-Manager.git
cd Portafolio-Manager
python -m venv .venv && .venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install and configure
pip install -r requirements/development.txt
copy .env.example .env  # Edit SECRET_KEY, DEBUG=True

# Run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000 (portfolio) and http://localhost:8000/admin (dashboard).

## Docker

```bash
# Development (port 8000)
docker compose up --build

# Staging/Production (nginx on port 80)
docker compose -f docker-compose.yml --profile staging up --build
```

See [docs/DOCKER_COMMANDS.md](docs/DOCKER_COMMANDS.md) for details.

## Test Data

```bash
python manage.py populate_test_data  # Creates admin/admin123 + demo content
```

## Documentation

| Guide | Purpose |
|-------|---------|
| [SETUP.md](docs/SETUP.md) | Installation, configuration, troubleshooting |
| [DOCKER_COMMANDS.md](docs/DOCKER_COMMANDS.md) | Docker Compose commands |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment (AWS, GHCR) |
| [CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md) | Environment variables |
| [ADMIN_USAGE.md](docs/ADMIN_USAGE.md) | Admin panel workflows |

## Features

- Responsive portfolio with sidebar navigation
- Project catalog with metadata and visibility control
- Blog with categories, tags, and publication workflow
- Resume module with PDF export
- Contact form with rate limiting
- Automatic translations (EN/ES) via LibreTranslate
- SEO: sitemaps, canonical URLs, structured data

## License

MIT License. See [LICENSE](LICENSE).
