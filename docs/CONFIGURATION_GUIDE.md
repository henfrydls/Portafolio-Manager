# Configuration Guide - Django Portfolio

This guide explains how to configure the Django Portfolio system with your personal information. This is a **generic portfolio system** that can be customized for any user.

## 🎯 Overview

The Django Portfolio is designed to be completely generic and configurable. **No personal information is hardcoded** in the application. All customization is done through:

1. **Environment Variables** (`.env` file)
2. **Admin Panel** (Django admin interface)
3. **Database Content** (managed through admin)

## 📝 Configuration Methods

### Method 1: Environment Variables (.env file)

Environment variables are used for system-level configuration and sensitive information.

#### Required Variables

```env
# Basic Configuration
PROJECT_NAME=My Portfolio
SECRET_KEY=your-generated-secret-key
DEBUG=False  # Set to True only for development
DJANGO_SETTINGS_MODULE=config.settings.production

# Domain Configuration
DOMAIN=yourdomain.com
PRODUCTION_DOMAIN=yourdomain.com
ALLOWED_HOSTS_PROD=yourdomain.com,www.yourdomain.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Social Media Links (Optional - can also be set in admin)
LINKEDIN_URL=https://linkedin.com/in/your-profile
GITHUB_URL=https://github.com/your-username
```

#### Optional Variables

```env
# Profile Defaults (used if not set in admin)
PROFILE_NAME=Your Name
PROFILE_TITLE=Your Professional Title
PROFILE_EMAIL=contact@yourdomain.com
PROFILE_LOCATION=Your City, Country

# Analytics
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio_db

# Redis (optional - for caching)
REDIS_URL=redis://localhost:6379/0
```

### Method 2: Admin Panel Configuration

Most content and personal information should be managed through the Django admin panel.

#### Step 1: Access Admin Panel

1. Start your server: `python manage.py runserver`
2. Navigate to: `http://localhost:8000/admin/`
3. Login with your superuser credentials

#### Step 2: Configure Your Profile

Navigate to **Profiles** → **Add Profile** (or edit existing):

- **Name**: Your full name
- **Title**: Your professional title
- **Bio**: Your professional summary
- **Email**: Your contact email
- **Phone**: Your phone number (optional)
- **Location**: Your location
- **Profile Photo**: Upload your photo
- **Resume PDF**: Upload your resume
- **LinkedIn URL**: Your LinkedIn profile
- **GitHub URL**: Your GitHub profile

#### Step 3: Add Your Projects

Navigate to **Projects** → **Add Project**:

- **Title**: Project name
- **Description**: Brief description
- **Detailed Description**: Full project details
- **Image**: Project screenshot
- **GitHub URL**: Repository link
- **Demo URL**: Live demo link
- **Technologies**: Select relevant technologies
- **Visibility**: Public/Private
- **Featured**: Mark important projects

#### Step 4: Create Blog Posts

Navigate to **Blog Posts** → **Add Blog Post**:

- **Title**: Post title
- **Content**: Full post content
- **Excerpt**: Brief summary
- **Category**: Select category
- **Post Type**: News, Tutorial, Opinion, etc.
- **Featured Image**: Post image
- **Status**: Draft/Published

#### Step 5: Add Work Experience

Navigate to **Experiences** → **Add Experience**:

- **Company**: Employer name
- **Position**: Your role
- **Description**: Responsibilities and achievements
- **Start Date**: Employment start
- **End Date**: Employment end (or check "Current")

#### Step 6: Add Education

Navigate to **Education** → **Add Education**:

- **Institution**: School/Platform name
- **Degree/Certificate**: Qualification
- **Field of Study**: Subject area
- **Start Date**: Program start
- **End Date**: Completion date
- **Credential URL**: Verification link (optional)

#### Step 7: Add Skills

Navigate to **Skills** → **Add Skill**:

- **Name**: Skill name
- **Category**: Frontend, Backend, Tools, etc.
- **Proficiency**: 1-4 (Basic to Expert)
- **Years Experience**: How long you've used it

## 🔧 Customization Options

### 1. Branding and Colors

Edit `static/css/style.css` to customize:

```css
:root {
    --primary-color: #your-color;
    --secondary-color: #your-color;
    --accent-color: #your-color;
}
```

### 2. Logo and Favicon

Replace these files with your own:
- `static/images/logo.png` - Your logo
- `static/images/favicon.ico` - Your favicon

### 3. Templates

Customize HTML templates in `templates/` directory:
- `templates/base.html` - Base template
- `templates/portfolio/home.html` - Homepage
- `templates/portfolio/about.html` - About page
- `templates/portfolio/projects.html` - Projects page

### 4. Email Templates

Customize email templates in `templates/emails/`:
- `templates/emails/contact_notification.html` - Contact form notification
- `templates/emails/contact_confirmation.html` - User confirmation

## 🌐 Multi-Language Support

The portfolio supports English and Spanish by default.

### Adding Translations

1. Edit translation files in `locale/` directory
2. Run: `python manage.py makemessages -l es`
3. Edit: `locale/es/LC_MESSAGES/django.po`
4. Compile: `python manage.py compilemessages`

### Adding New Languages

1. Add language to `config/settings/base.py`:
   ```python
   LANGUAGES = [
       ('en', 'English'),
       ('es', 'Español'),
       ('fr', 'Français'),  # Add new language
   ]
   ```

2. Create translations:
   ```bash
   python manage.py makemessages -l fr
   python manage.py compilemessages
   ```

## 🔒 Security Configuration

### Production Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Generate new `SECRET_KEY` for production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags:
  ```env
  SESSION_COOKIE_SECURE=True
  CSRF_COOKIE_SECURE=True
  SECURE_SSL_REDIRECT=True
  ```
- [ ] Configure CORS if needed
- [ ] Set up rate limiting
- [ ] Configure firewall rules

### Email Security

For Gmail:
1. Enable 2-Factor Authentication
2. Generate App Password at: https://myaccount.google.com/apppasswords
3. Use the 16-character password in `.env`

## 📊 Analytics Configuration

### Google Analytics

1. Create Google Analytics account
2. Get your Measurement ID (GA_MEASUREMENT_ID)
3. Add to `.env`:
   ```env
   GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   ```

### Custom Analytics

The portfolio includes built-in visit tracking:
- View statistics: `python manage.py visit_stats`
- Clean old data: `python manage.py cleanup_old_visits`

## 🎨 Theme Customization

### Color Schemes

Edit `static/css/style.css`:

```css
/* Light Theme */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --text-primary: #212529;
    --text-secondary: #6c757d;
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1a1a1a;
        --bg-secondary: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
    }
}
```

### Layout Options

Choose between different layouts by editing templates:
- **Fixed Sidebar**: Current default
- **Top Navigation**: Modify `templates/base.html`
- **Full Width**: Adjust CSS grid/flexbox

## 🔄 Content Migration

### Importing Existing Content

If you have existing content, you can import it:

1. **From JSON**:
   ```bash
   python manage.py loaddata your_data.json
   ```

2. **From CSV**:
   Create a custom management command or use admin import

3. **From Another Portfolio**:
   Export from old system, transform data, import to new system

### Exporting Content

```bash
# Export all data
python manage.py dumpdata portfolio > backup.json

# Export specific models
python manage.py dumpdata portfolio.Project > projects.json
python manage.py dumpdata portfolio.BlogPost > blog.json
```

## 🧪 Testing Your Configuration

### 1. Test Environment Variables

```bash
python manage.py check_env
```

### 2. Test Email Configuration

```bash
python manage.py test_email
```

### 3. Test Database Connection

```bash
python manage.py check --database default
```

### 4. Test Static Files

```bash
python manage.py collectstatic --dry-run
```

### 5. Run System Checks

```bash
python manage.py check --deploy
```

## 📝 Configuration Examples

### Example 1: Personal Developer Portfolio

```env
PROJECT_NAME=John Doe - Full Stack Developer
PROFILE_NAME=John Doe
PROFILE_TITLE=Full Stack Developer
PROFILE_EMAIL=john@johndoe.com
DOMAIN=johndoe.com
LINKEDIN_URL=https://linkedin.com/in/johndoe
GITHUB_URL=https://github.com/johndoe
```

### Example 2: Design Portfolio

```env
PROJECT_NAME=Jane Smith - UX/UI Designer
PROFILE_NAME=Jane Smith
PROFILE_TITLE=UX/UI Designer
PROFILE_EMAIL=hello@janesmith.design
DOMAIN=janesmith.design
LINKEDIN_URL=https://linkedin.com/in/janesmith
BEHANCE_URL=https://behance.net/janesmith
```

### Example 3: Freelancer Portfolio

```env
PROJECT_NAME=Alex Johnson - Freelance Developer
PROFILE_NAME=Alex Johnson
PROFILE_TITLE=Freelance Web Developer
PROFILE_EMAIL=contact@alexjohnson.dev
DOMAIN=alexjohnson.dev
LINKEDIN_URL=https://linkedin.com/in/alexjohnson
GITHUB_URL=https://github.com/alexjohnson
UPWORK_URL=https://upwork.com/freelancers/alexjohnson
```

## 🆘 Troubleshooting

### Configuration Not Loading

1. Check `.env` file exists in project root
2. Verify environment variables with: `python manage.py check_env`
3. Restart server after changing `.env`

### Profile Not Showing

1. Check if profile exists in admin panel
2. Verify profile is not marked as inactive
3. Check template rendering in browser console

### Email Not Working

1. Test email configuration: `python manage.py test_email`
2. Verify SMTP credentials
3. Check firewall/security settings
4. For Gmail, ensure App Password is used

### Static Files Not Loading

1. Run: `python manage.py collectstatic`
2. Check `STATIC_ROOT` and `STATIC_URL` settings
3. Verify web server configuration (Nginx/Apache)

## 🧪 Test Data

Para desarrollo y pruebas, puedes poblar el portfolio con datos de ejemplo:

```bash
python manage.py populate_test_data
```

Este comando crea un portfolio completo con:
- Usuario admin (username: `admin`, password: `admin123`)
- Perfil, experiencias, educación, habilidades
- **Idiomas** (English, Spanish, French, German)
- Proyectos, posts de blog, categorías
- Tecnologías con iconos

Para más detalles, consulta: [Test Data Guide](TEST_DATA.md)

## 📚 Additional Resources

- [Installation Guide](INSTALLATION_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Admin Usage Guide](ADMIN_USAGE.md)
- [Management Commands](MANAGEMENT_COMMANDS.md)
- [Test Data Guide](TEST_DATA.md)

---

**Remember**: This is a generic portfolio system. All personal information should come from configuration, not from hardcoded values in the code.