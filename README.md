# Django Portfolio - Professional Portfolio Website

A professional Django-based portfolio website featuring a modern design, comprehensive admin panel, and bilingual support. Perfect for developers, designers, and professionals who want to showcase their work online.

> **⚠️ Important**: All content and configuration must be set through environment variables and the admin panel.

## ✨ Features

- **Modern Portfolio Design** with fixed sidebar layout and responsive design
- **Comprehensive Admin Panel** for content management with analytics dashboard
- **Blog System** with Medium-style posts, categories, and rich content editing
- **Project Showcase** with catalog-driven filtering and public/private visibility
- **Catalog Management** for categories, project types, and knowledge bases
- **Resume Management** with web version and PDF download
- **Contact System** with secure forms and email notifications
- **Analytics Tracking** with visit statistics and performance metrics
- **Bilingual Support** (English/Spanish) with custom translation system
- **SEO Optimization** with meta tags, sitemaps, and structured data
- **Security Features** including CSRF protection, file validation, and rate limiting
- **Automatic Translation Pipeline** (branch `i18n`) with LibreTranslate integration and per-language status tracking

## Project Variants

- **`main`** – single-language template without django-parler or automatic translation. Ideal when you just need the classic portfolio.
- **`i18n`** – multilingual template (this branch) with django-parler, automatic translation, and LibreTranslate integration. Requires the additional setup described below.

Clone the branch that best matches your needs. You can keep both branches up-to-date by cherry-picking neutral improvements from `i18n` into `main`.

## 🛠️ Technologies

- **Backend**: Django 5.2 LTS
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Static Files**: WhiteNoise for efficient static file serving
- **Email**: Django Email Backend with SMTP support
- **Image Processing**: Pillow for image optimization
- **Security**: Django security middleware and custom protections

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git
- Code editor (VS Code recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd portfolio

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# At minimum, set:
# - SECRET_KEY (generate a new one)
# - DEBUG=True (for development)
# - ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 4. Run Development Server

```bash
# Start the development server
python manage.py runserver

# Access the application:
# - Portfolio: http://127.0.0.1:8000/
# - Admin Panel: http://127.0.0.1:8000/admin/
```

### Optional: Docker Compose (app + LibreTranslate)

For a ready-to-run stack (Django + LibreTranslate), make sure Docker Desktop is running and then:

```bash
cp .env.example .env  # populate with your values
docker compose up --build
```

Services exposed:

- Portfolio: http://127.0.0.1:8000/
- LibreTranslate API: http://127.0.0.1:5000/

The `web` container mounts your local project, so code changes reload automatically. Stop the stack with `docker compose down`.

## 📝 Initial Setup

After running the server, configure your portfolio:

1. **Login to Admin Panel**: http://127.0.0.1:8000/admin/
2. **Create Profile**: Add your personal information
3. **Add Projects**: Showcase your work
4. **Write Blog Posts**: Share your thoughts
5. **Configure Skills**: List your expertise
6. **Add Experience**: Your work history

See [Admin Usage Guide](docs/ADMIN_USAGE.md) for detailed instructions.

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite by default)
# No configuration needed for development

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Security (for production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

See [Configuration Guide](docs/CONFIGURATION_GUIDE.md) for all options.

## 📧 Email Configuration

For contact form functionality, configure email settings:

1. **Development**: Uses console backend (emails printed to console)
2. **Production**: Configure SMTP settings in `.env`

See [Email Setup Guide](docs/EMAIL_SETUP.md) for detailed instructions.

## 🎨 Customization

### Adding Content

All content is managed through the admin panel:
- **Profile**: Personal information and social links
- **Projects**: Portfolio items with images and descriptions
- **Blog Posts**: Articles and tutorials
- **Catalogs**: Categories, project types, and knowledge bases that feed filters
- **Skills**: Technical skills and proficiency levels
- **Experience**: Work history
- **Education**: Academic background and certifications

### Bilingual Support

The site supports English and Spanish:
- **Language Switcher**: Top-right corner for easy language switching
- **Translatable UI**: All interface text is translatable
- **Multilingual CVs**: Upload separate PDF resumes for English and Spanish
  - System automatically serves the correct CV based on visitor's language
  - Falls back to available CV if requested language is not available
  - Manage both versions through the admin panel
- **Automatic Detection**: Language preference is detected and applied automatically

## 🗂️ Project Structure

```
portfolio/
├── config/                     # Django settings
│   ├── settings/
│   │   ├── base.py            # Base settings
│   │   └── development.py     # Development settings
│   ├── urls.py                # URL configuration
│   └── wsgi.py                # WSGI configuration
│
├── portfolio/                  # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── admin.py               # Admin configuration
│   ├── forms.py               # Form definitions
│   └── templatetags/          # Custom template tags
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   └── portfolio/             # App templates
│
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User-uploaded files
├── locale/                     # Translation files
├── requirements/               # Dependencies
│   ├── base.txt               # Base dependencies
│   └── development.txt        # Development dependencies
│
├── docs/                       # Documentation
├── .env.example               # Environment variables template
├── manage.py                  # Django management script
└── README.md                  # This file
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test portfolio

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Create superuser
python manage.py createsuperuser
```

- **Translation (i18n branch)**

```env
TRANSLATION_PROVIDER=libretranslate
TRANSLATION_API_URL=http://libretranslate:5000
TRANSLATION_API_KEY=            # optional if your server requires it
```

- If you run `docker compose up`, these defaults already point to the bundled LibreTranslate service.
- After enabling “Auto translate” in **Dashboard → Settings**, the site will attempt to translate new/updated content into every language listed in `settings.LANGUAGES` except the default one.

### Static Files

```bash
# Collect static files
python manage.py collectstatic

# Clear collected static files
python manage.py collectstatic --clear
```

### Translation Verification

```bash
# Verify all translations are complete
python verify_translations.py
```

### Automatic Translation Workflow (i18n branch)

1. Ensure a translation provider is reachable. The included docker compose file launches LibreTranslate on port 5000.
2. Add/update the configuration in **Dashboard → Settings**:
   - Default language (source language for content entry)
   - Enable automatic translation
   - Provider: `libretranslate`
   - API URL: e.g. `http://libretranslate:5000`
   - Timeout (seconds) according to your environment
3. Edit your profile, projects, blog posts, etc. in the default language.
4. After saving, the edit view shows the status of every target language (generated, pending, or failed). Failures include the returned error so you can retry.
5. You can regenerate translations manually by editing the item again after fixing the root cause (e.g., API downtime).

## 📚 Documentation

### Getting Started
1. **[SETUP.md](SETUP.md)** - Complete installation guide
   - Prerequisites and requirements
   - Step-by-step installation
   - Initial configuration
   - Troubleshooting

2. **[docs/CONFIGURATION_GUIDE.md](docs/CONFIGURATION_GUIDE.md)** - System configuration
   - Environment variables
   - Settings configuration
   - Security settings

### User Guides
3. **[docs/ADMIN_USAGE.md](docs/ADMIN_USAGE.md)** - Admin panel guide
   - Content management
   - Profile setup
   - Projects and blog management
   - Skills and experience

4. **[docs/EMAIL_SETUP.md](docs/EMAIL_SETUP.md)** - Email configuration
   - SMTP setup
   - Email testing
   - Troubleshooting

5. **[docs/MULTILINGUAL_CV.md](docs/MULTILINGUAL_CV.md)** - CV feature
   - Upload CVs in multiple languages
   - Automatic language detection
   - Admin interface

### Maintenance Tools
- **verify_translations.py** - Verify translation completeness
  ```bash
  python verify_translations.py
  ```

## 🔒 Security

### Development
- DEBUG mode enabled
- Console email backend
- Permissive CORS settings

### Production Considerations
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use strong `SECRET_KEY`
- Enable HTTPS settings
- Configure real email backend
- Set up proper database (PostgreSQL recommended)

## 🐛 Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Use different port
python manage.py runserver 8001
```

**Static files not loading**:
```bash
# Collect static files
python manage.py collectstatic --noinput
```

**Database errors**:
```bash
# Reset migrations (development only!)
python manage.py migrate --run-syncdb
```

**Translation issues**:
```bash
# Verify translations
python verify_translations.py
```

**Template syntax errors**:
```bash
# If you see "Invalid block tag" errors:
# - Check that template tags are not split across multiple lines
# - Ensure {% if %}, {% for %}, {% trans %} tags are properly closed
# - Django template tags must be on single lines or properly indented
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For questions, issues, or contributions:
- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Create an issue on your GitHub repository
- **Django Community**: https://forum.djangoproject.com/

---

**Version**: 1.0  
**Django**: 5.2 LTS  
**Python**: 3.10+  
**Status**: Production Ready
