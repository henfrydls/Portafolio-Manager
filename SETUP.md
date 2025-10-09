# Setup Guide - Django Portfolio

Complete installation and configuration guide for the Django Portfolio system.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **pip** (Python package manager)
- **Git** for version control
- **Code editor** (VS Code, PyCharm, or similar)
- **Virtual environment** tool (venv, included with Python)

### Verify Prerequisites

```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Check pip
pip --version

# Check git
git --version
```

---

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd portfolio

# Or if you downloaded as ZIP
unzip portfolio.zip
cd portfolio
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
# Install development dependencies
pip install -r requirements/development.txt

# Verify installation
pip list
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# On Windows (if cp doesn't work):
copy .env.example .env
```

Edit `.env` file with your settings:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite - no configuration needed)

# Email Configuration (optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Security (keep False for development)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
```

**Important**: Generate a new SECRET_KEY:

```python
# In Python shell:
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 5: Initialize Database

```bash
# Run migrations to create database tables
python manage.py migrate

# You should see output like:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, portfolio, sessions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   ...
```

### Step 6: Create Superuser

```bash
# Create admin user
python manage.py createsuperuser

# Follow the prompts:
# Username: admin
# Email: your-email@example.com
# Password: (enter a strong password)
# Password (again): (confirm password)
```

### Step 7: Collect Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# This copies all static files to the staticfiles/ directory
```

### Step 8: Run Development Server

```bash
# Start the development server
python manage.py runserver

# You should see:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CTRL-BREAK.
```

### Step 9: Access the Application

Open your browser and navigate to:

- **Portfolio**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

Login with the superuser credentials you created.

---

## 🎨 Initial Configuration

### 1. Create Your Profile

1. Go to **Admin Panel** → **Profiles** → **Add Profile**
2. Fill in your information:
   - Name
   - Professional title
   - Bio
   - Email
   - Location
   - Social media links (LinkedIn, GitHub, Medium)
   - Upload profile image
   - Upload CV (optional)

### 2. Add Technologies

1. Go to **Technologies** → **Add Technology**
2. Add technologies you use:
   - Name (e.g., "Python", "Django", "React")
   - Icon class (e.g., "fab fa-python")
   - Color (hex code, e.g., "#3776ab")

**Tip**: The system suggests icons and colors for common technologies!

### 3. Add Projects

1. Go to **Projects** → **Add Project**
2. Fill in project details:
   - Title and description
   - Project type
   - Technologies used
   - GitHub URL (optional)
   - Demo URL (optional)
   - Upload project image
   - Set visibility (public/private)
   - Mark as featured (optional)

### 4. Write Blog Posts

1. Go to **Blog Posts** → **Add Blog Post**
2. Create your first post:
   - Title and slug
   - Content (supports Markdown)
   - Excerpt
   - Category
   - Tags
   - Featured image
   - Set status (draft/published)
   - Set publish date

### 5. Add Skills

1. Go to **Skills** → **Add Skill**
2. Add your skills:
   - Skill name
   - Proficiency level (1-4)
   - Years of experience
   - Category (e.g., "Programming", "Cloud", "Business")

### 6. Add Experience

1. Go to **Experience** → **Add Experience**
2. Add work history:
   - Company and position
   - Description
   - Start and end dates
   - Mark as current (if applicable)

### 7. Add Education

1. Go to **Education** → **Add Education**
2. Add academic background:
   - Institution and degree
   - Field of study
   - Education type (formal, certification, online course, etc.)
   - Dates
   - Credential ID and URL (for certifications)

---

## 🔧 Configuration Options

### Email Setup

For contact form functionality, configure email in `.env`:

**Development (Console Backend)**:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails will be printed to the console.

**Production (SMTP)**:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

See [Email Setup Guide](docs/EMAIL_SETUP.md) for detailed instructions.

### Language Settings

The site supports English and Spanish:
- Default language: English
- Language switcher in top-right corner
- Upload CVs in both languages

### Database

By default, the project uses SQLite:
- Database file: `db_development.sqlite3`
- No additional configuration needed
- Perfect for development

For production, consider PostgreSQL or MySQL.

---

## 🧪 Verification

### Test the Installation

1. **Homepage**: http://127.0.0.1:8000/
   - Should display your portfolio
   - Profile sidebar should show your information

2. **Admin Panel**: http://127.0.0.1:8000/admin/
   - Should be accessible with superuser credentials
   - All models should be visible

3. **Contact Form**: Test the contact form
   - Fill out the form
   - Check console for email output (development mode)

4. **Language Switcher**: Test bilingual support
   - Click EN/ES switcher in top-right
   - UI should change language

5. **Translations**: Verify translations
   ```bash
   python verify_translations.py
   ```

---

## 🐛 Troubleshooting

### Virtual Environment Issues

**Problem**: Virtual environment not activating
```bash
# Windows
.venv\Scripts\activate.bat  # Try this instead

# macOS/Linux
source .venv/bin/activate
```

### Installation Errors

**Problem**: pip install fails
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then try again
pip install -r requirements/development.txt
```

**Problem**: Pillow installation fails
```bash
# Install Pillow separately
pip install Pillow==10.0.0

# Then install rest
pip install -r requirements/development.txt
```

### Database Issues

**Problem**: Migration errors
```bash
# Delete database and start fresh (development only!)
rm db_development.sqlite3  # On Windows: del db_development.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**Problem**: "Table already exists" error
```bash
# Run migrations with --run-syncdb
python manage.py migrate --run-syncdb
```

### Static Files Issues

**Problem**: CSS/JS not loading
```bash
# Collect static files again
python manage.py collectstatic --clear --noinput
```

**Problem**: Images not displaying
```bash
# Check MEDIA_ROOT and MEDIA_URL in settings
# Ensure media/ directory exists
mkdir media
```

### Port Issues

**Problem**: Port 8000 already in use
```bash
# Use different port
python manage.py runserver 8001

# Or find and kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

### Permission Issues

**Problem**: Permission denied errors
```bash
# Windows: Run terminal as Administrator
# macOS/Linux: Check file permissions
chmod +x manage.py
```

---

## 📚 Next Steps

After successful installation:

1. **Read Documentation**:
   - [Admin Usage Guide](docs/ADMIN_USAGE.md)
   - [Configuration Guide](docs/CONFIGURATION_GUIDE.md)
   - [Email Setup Guide](docs/EMAIL_SETUP.md)

2. **Customize Your Portfolio**:
   - Add your projects
   - Write blog posts
   - Update your profile
   - Upload your CV

3. **Test Features**:
   - Contact form
   - Language switching
   - Admin panel
   - Blog functionality

4. **Explore Admin Panel**:
   - Dashboard with analytics
   - Content management
   - User messages
   - Visit tracking

---

## 🔄 Updating

To update the project:

```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install new dependencies
pip install -r requirements/development.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart server
python manage.py runserver
```

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review the [Documentation Index](DOCUMENTATION_INDEX.md)
3. Check the [Admin Usage Guide](docs/ADMIN_USAGE.md)
4. Verify your `.env` configuration
5. Ensure all prerequisites are installed

---

**Setup Complete!** 🎉

Your Django Portfolio is now ready to use. Start by logging into the admin panel and adding your content.

For detailed usage instructions, see the [Admin Usage Guide](docs/ADMIN_USAGE.md).
