# 🚀 Portfolio Template Setup Guide

[🇪🇸 Español](#español) | [🇺🇸 English](#english)

---

## Español

Este es un template de portfolio profesional en Django inspirado en el diseño de Matt Deitke. Perfecto para desarrolladores, diseñadores y profesionales tecnológicos.

## ✨ Características Principales

- **Diseño Fixed Sidebar** inspirado en Matt Deitke
- **Blog estilo Medium** con páginas de detalle profesionales
- **Sistema de administración completo** para gestión de contenido
- **Tecnologías predefinidas** (50+ con iconos y colores automáticos)
- **Diseño responsivo** optimizado para todos los dispositivos
- **Sistema de contacto** con formulario seguro
- **Tracking de visitas** con middleware personalizado
- **Configuración por entornos** (Development, Staging, Production)

## 📋 Requisitos Previos

- Python 3.10+
- Git
- Editor de código (VS Code recomendado)

## 🛠️ Instalación Rápida

### 1. Clona el Repositorio
```bash
git clone https://github.com/your-username/portfolio-template.git
cd portfolio-template
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias por Entorno

**Para Desarrollo:**
```bash
pip install -r requirements/development.txt
```

**Para Staging:**
```bash
pip install -r requirements/staging.txt
```

**Para Producción:**
```bash
pip install -r requirements/production.txt
```

### 4. Configurar Variables de Entorno
```bash
# Copia el archivo de configuración
cp .env.example .env

# Edita .env con tu información personal
```

### 5. Configurar Base de Datos
```bash
# Desarrollo (por defecto)
python manage.py makemigrations --settings=config.settings.development
python manage.py migrate --settings=config.settings.development

# Para otros entornos
python manage.py migrate --settings=config.settings.staging
python manage.py migrate --settings=config.settings.production
```

### 6. Poblar Datos de Muestra (Opcional)

**Para un portfolio completo con contenido de ejemplo:**
```bash
python manage.py populate_sample_data --settings=config.settings.development
```

**Solo tecnologías predefinidas:**
```bash
python manage.py populate_technologies --settings=config.settings.development
```

El comando `populate_sample_data` incluye:
- ✅ Perfil completo con foto y biografía
- ✅ 4 experiencias laborales detalladas
- ✅ 3 educaciones/certificaciones
- ✅ 20+ habilidades técnicas con niveles
- ✅ 6 proyectos de portfolio completos
- ✅ 6 artículos de blog extensos
- ✅ 5 mensajes de contacto de muestra
- ✅ 50+ tecnologías con iconos automáticos

### 7. Crear Superusuario
```bash
python manage.py createsuperuser --settings=config.settings.development
```

### 8. Ejecutar el Servidor

**Desarrollo (recomendado para empezar):**
```bash
python manage.py runserver --settings=config.settings.development
```

**Staging:**
```bash
python manage.py runserver --settings=config.settings.staging
```

**Producción:**
```bash
python manage.py runserver --settings=config.settings.production
```

¡Visita `http://localhost:8000` para ver tu portfolio!
🔧 **RUNNING IN DEVELOPMENT ENVIRONMENT** aparecerá en la consola.

## ⚙️ Configuración Personalizada

### 📝 Archivo .env

Edita el archivo `.env` con tu información:

```env
# Información Básica
PROJECT_NAME=Tu Nombre - Portfolio
SECRET_KEY=genera-una-clave-secreta-nueva
DEBUG=True

# Dominios (para producción)
DOMAIN=localhost
PRODUCTION_DOMAIN=tudominio.com

# Redes Sociales
LINKEDIN_URL=https://linkedin.com/in/tu-perfil
GITHUB_URL=https://github.com/tu-usuario
MEDIUM_URL=https://medium.com/@tu-usuario

# Email (para formulario de contacto)
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-app
```

### 🔐 Generar SECRET_KEY

```python
# En terminal de Python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 🌐 Configurar Hosts Permitidos

Para diferentes puertos o IPs locales, edita en `.env`:

```env
ALLOWED_HOSTS_DEV=localhost,127.0.0.1,0.0.0.0,tu-ip-local
```

## 📱 Gestión de Entornos

### 🔧 Development (Desarrollo Local)
- **Indicador**: 🔧 RUNNING IN DEVELOPMENT ENVIRONMENT
- **Sesiones**: 1 semana (configurable)
- **Debug**: Activado
- **Base de datos**: `db_development.sqlite3`
- **HTTPS**: No requerido

```bash
python manage.py runserver --settings=config.settings.development
```

### 🧪 Staging (Pruebas)
- **Indicador**: 🧪 RUNNING IN STAGING ENVIRONMENT
- **Sesiones**: 12 horas (configurable)
- **Debug**: Activado (para testing)
- **Base de datos**: `db_staging.sqlite3`
- **HTTPS**: Requerido

```bash
python manage.py runserver --settings=config.settings.staging
```

### 🚀 Production (Producción)
- **Indicador**: 🚀 RUNNING IN PRODUCTION ENVIRONMENT
- **Sesiones**: 24 horas (configurable)
- **Debug**: Desactivado
- **Base de datos**: `db_production.sqlite3`
- **HTTPS**: Requerido + configuraciones de seguridad adicionales

```bash
python manage.py runserver --settings=config.settings.production
```

## 📊 Panel de Administración

1. Ve a `http://localhost:8000/admin`
2. Inicia sesión con tu superusuario
3. Configura tu perfil, proyectos y blog posts

### Secciones Principales:

- **👤 Profile**: Tu información personal, biografía, foto, CV en PDF
- **🚀 Projects**: Portfolio de trabajos con tecnologías y enlaces
- **📝 Blog Posts**: Sistema de blog con categorías y contenido markdown
- **🏷️ Categories**: Categorías para blog posts
- **💼 Experience**: Historial laboral y experiencia profesional
- **🎓 Education**: Educación formal, cursos y certificaciones
- **⚡ Skills**: Habilidades técnicas con niveles de competencia
- **🔧 Technologies**: 50+ tecnologías predefinidas con iconos automáticos
- **📧 Contact**: Mensajes del formulario de contacto
- **📈 Page Visits**: Tracking básico de visitas y analytics

### 🎨 Tecnologías Predefinidas

El sistema incluye más de 50 tecnologías con iconos y colores automáticos:

**Lenguajes**: Python, JavaScript, Java, TypeScript, PHP, Swift, Rust, Go, C++, C#, Ruby, Kotlin
**Frontend**: React, Vue.js, Angular, HTML, CSS, Sass, Bootstrap, Tailwind CSS
**Backend**: Django, Flask, Node.js, Express.js, Laravel, Spring Boot, FastAPI
**Bases de Datos**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
**DevOps**: Docker, Kubernetes, AWS, Google Cloud, Azure, Git, GitHub, GitLab

### Comandos Útiles del Admin:

**Datos de muestra completos:**
```bash
# Crear portfolio completo con contenido de ejemplo
python manage.py populate_sample_data --settings=config.settings.development

# Resetear datos existentes y crear nuevos
python manage.py populate_sample_data --reset --settings=config.settings.development

# Crear con password personalizada para admin
python manage.py populate_sample_data --admin-password mipassword123 --settings=config.settings.development
```

**Solo tecnologías:**
```bash
# Poblar todas las tecnologías predefinidas
python manage.py populate_technologies --settings=config.settings.development

# Actualizar tecnologías existentes
python manage.py populate_technologies --update --settings=config.settings.development

# Poblar solo una categoría específica
python manage.py populate_technologies --category frontend --settings=config.settings.development
```

## 🎨 Personalización

### Colores y Estilos
- Edita `static/css/style.css`
- Los colores principales están en variables CSS

### Templates
- `templates/portfolio/` - Páginas principales
- `templates/portfolio/admin/` - Panel de administración

### Logos e Imágenes
- Coloca tu logo en `static/images/`
- Actualiza las referencias en templates

## 🚀 Despliegue

### Estructura de Requirements

El proyecto usa requirements modulares:

```
requirements/
├── base.txt          # Dependencias básicas (Django, Pillow, etc.)
├── development.txt   # Herramientas de desarrollo (debug-toolbar, pytest)
├── staging.txt       # Para entorno de pruebas (debug + coverage)
└── production.txt    # Para producción (gunicorn, reportlab)
```

### Para Heroku:
```bash
# 1. Instala Heroku CLI y crea app
heroku create tu-portfolio

# 2. Configura variables de entorno
heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production
heroku config:set SECRET_KEY=tu-secret-key-aqui
heroku config:set ALLOWED_HOSTS_PROD=tu-app.herokuapp.com

# 3. Instala dependencias y despliega
git push heroku main
heroku run python manage.py migrate --settings=config.settings.production
heroku run python manage.py createsuperuser --settings=config.settings.production
```

### Para VPS/DigitalOcean:
```bash
# 1. Instala dependencias del sistema
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 2. Clona y configura
git clone tu-repo.git
cd portfolio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt

# 3. Configura .env para producción
cp .env.example .env
# Edita .env con configuraciones de producción

# 4. Ejecuta con Gunicorn
gunicorn config.wsgi:application --settings=config.settings.production
```

### Variables de Entorno para Producción:
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=tu-secret-key-super-segura
DEBUG=False
ALLOWED_HOSTS_PROD=tudominio.com,www.tudominio.com
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

## 🆘 Solución de Problemas

### Error de ALLOWED_HOSTS
```env
# En .env, agrega tu IP/dominio
ALLOWED_HOSTS_DEV=localhost,127.0.0.1,tu-ip
```

### Error de Base de Datos
```bash
# Elimina y recrea las migraciones
rm db.sqlite3
rm portfolio/migrations/00*.py
python manage.py makemigrations portfolio
python manage.py migrate
```

### Error de Archivos Estáticos
```bash
python manage.py collectstatic --settings=config.settings.development
```

### Problema con Tecnologías
```bash
# Resetea y vuelve a poblar tecnologías
python manage.py populate_technologies --settings=config.settings.development
```

### Error con Migraciones
```bash
# Elimina y recrea migraciones específicas de portfolio
rm portfolio/migrations/00*.py
python manage.py makemigrations portfolio --settings=config.settings.development
python manage.py migrate --settings=config.settings.development
```

### Error de Entorno Incorrecto
Asegúrate de especificar el entorno correcto:
```bash
# En lugar de: python manage.py runserver
python manage.py runserver --settings=config.settings.development
```

## 🎯 Funcionalidades Avanzadas

### 📈 Sistema de Analytics
- Tracking automático de visitas
- Exclusión inteligente de bots y rutas admin
- Dashboard de analytics en `/admin-analytics/`

### 🔒 Sistema de Seguridad
- Validación de archivos con python-magic
- Headers de seguridad personalizados
- Rate limiting configurable
- Formularios con protección honeypot

### 📧 Sistema de Email
- Formulario de contacto seguro
- Backend configurable por entorno
- Validación anti-spam integrada

## 📞 Soporte

Si necesitas ayuda:
1. Revisa la documentación completa en `README.md`
2. Consulta los issues en GitHub
3. Crea un issue con tu problema específico

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

¡Felicidades! 🎉 Tu portfolio profesional está listo.

**URLs importantes:**
- Portfolio: `http://yourdomain.com/`
- Admin: `http://yourdomain.com/admin/` (admin/admin123)
- Dashboard: `http://yourdomain.com/admin-dashboard/`
- Analytics: `http://yourdomain.com/admin-analytics/`

**Contenido incluido en datos de muestra:**
- 📝 **6 artículos técnicos** completos (Django APIs, Machine Learning, DevOps, React Hooks, Tendencias 2024)
- 🚀 **6 proyectos** detallados (E-commerce, Analytics Dashboard, Microservices, etc.)
- 💼 **4 experiencias** laborales con descripciones profesionales
- 🎓 **3 educaciones** incluyendo universidad y certificaciones
- ⚡ **20+ habilidades** técnicas con niveles de competencia
- 📧 **5 mensajes** de contacto de muestra
- 🔧 **50+ tecnologías** con iconos automáticos

¡Comparte tu increíble trabajo con el mundo! 🚀

---

## English

Professional Django portfolio template inspired by Matt Deitke's design. Perfect for developers, designers, and tech professionals.

## ✨ Key Features

- **Fixed Sidebar Design** inspired by Matt Deitke
- **Medium-style Blog** with professional detail pages
- **Complete Admin System** for content management
- **Predefined Technologies** (50+ with automatic icons and colors)
- **Responsive Design** optimized for all devices
- **Contact System** with secure forms
- **Visit Tracking** with custom middleware
- **Environment Configuration** (Development, Staging, Production)

## 📋 Prerequisites

- Python 3.10+
- Git
- Code editor (VS Code recommended)

## 🛠️ Quick Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-username/portfolio-template.git
cd portfolio-template
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies by Environment

**For Development:**
```bash
pip install -r requirements/development.txt
```

**For Staging:**
```bash
pip install -r requirements/staging.txt
```

**For Production:**
```bash
pip install -r requirements/production.txt
```

### 4. Configure Environment Variables
```bash
# Copy configuration file
cp .env.example .env

# Edit .env with your personal information
```

### 5. Configure Database
```bash
# Development (default)
python manage.py makemigrations --settings=config.settings.development
python manage.py migrate --settings=config.settings.development

# For other environments
python manage.py migrate --settings=config.settings.staging
python manage.py migrate --settings=config.settings.production
```

### 6. Populate Sample Data (Optional)

**For complete portfolio with sample content:**
```bash
python manage.py populate_sample_data --settings=config.settings.development
```

**Only predefined technologies:**
```bash
python manage.py populate_technologies --settings=config.settings.development
```

The `populate_sample_data` command includes:
- ✅ Complete profile with photo and biography
- ✅ 4 detailed work experiences
- ✅ 3 educations/certifications
- ✅ 20+ technical skills with levels
- ✅ 6 complete portfolio projects
- ✅ 6 extensive blog articles
- ✅ 5 sample contact messages
- ✅ 50+ technologies with automatic icons

### 7. Create Superuser
```bash
python manage.py createsuperuser --settings=config.settings.development
```

### 8. Run Server

**Development:**
```bash
python manage.py runserver --settings=config.settings.development
```

**Staging:**
```bash
python manage.py runserver --settings=config.settings.staging
```

**Production:**
```bash
python manage.py runserver --settings=config.settings.production
```

Visit `http://localhost:8000` to see your portfolio!
🔧 **RUNNING IN DEVELOPMENT ENVIRONMENT** will appear in console.

## ⚙️ Custom Configuration

### 📝 .env File

Edit the `.env` file with your information:

```env
# Basic Information
PROJECT_NAME=Your Name - Portfolio
SECRET_KEY=generate-a-new-secret-key
DEBUG=True

# Domains (for production)
DOMAIN=localhost
PRODUCTION_DOMAIN=yourdomain.com

# Social Media
LINKEDIN_URL=https://linkedin.com/in/your-profile
GITHUB_URL=https://github.com/your-username
MEDIUM_URL=https://medium.com/@your-username

# Email (for contact form)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 🔐 Generate SECRET_KEY

```python
# In Python terminal
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 🌐 Configure Allowed Hosts

For different ports or local IPs, edit in `.env`:

```env
ALLOWED_HOSTS_DEV=localhost,127.0.0.1,0.0.0.0,your-local-ip
```

## 📱 Environment Management

### 🔧 Development (Local Development)
- **Indicator**: 🔧 RUNNING IN DEVELOPMENT ENVIRONMENT
- **Sessions**: 1 week (configurable)
- **Debug**: Enabled
- **Database**: `db_development.sqlite3`
- **HTTPS**: Not required

```bash
python manage.py runserver --settings=config.settings.development
```

### 🧪 Staging (Testing)
- **Indicator**: 🧪 RUNNING IN STAGING ENVIRONMENT
- **Sessions**: 12 hours (configurable)
- **Debug**: Enabled (for testing)
- **Database**: `db_staging.sqlite3`
- **HTTPS**: Required

```bash
python manage.py runserver --settings=config.settings.staging
```

### 🚀 Production (Production)
- **Indicator**: 🚀 RUNNING IN PRODUCTION ENVIRONMENT
- **Sessions**: 24 hours (configurable)
- **Debug**: Disabled
- **Database**: `db_production.sqlite3`
- **HTTPS**: Required + additional security configurations

```bash
python manage.py runserver --settings=config.settings.production
```

## 📊 Admin Panel

1. Go to `http://localhost:8000/admin`
2. Login with your superuser
3. Configure your profile, projects and blog posts

### Main Sections:

- **👤 Profile**: Your personal information, biography, photo, PDF CV
- **🚀 Projects**: Portfolio work with technologies and links
- **📝 Blog Posts**: Blog system with categories and markdown content
- **🏷️ Categories**: Categories for blog posts
- **💼 Experience**: Work history and professional experience
- **🎓 Education**: Formal education, courses and certifications
- **⚡ Skills**: Technical skills with competency levels
- **🔧 Technologies**: 50+ predefined technologies with automatic icons
- **📧 Contact**: Contact form messages
- **📈 Page Visits**: Basic visit tracking and analytics

### 🎨 Predefined Technologies

The system includes 50+ technologies with automatic icons and colors:

**Languages**: Python, JavaScript, Java, TypeScript, PHP, Swift, Rust, Go, C++, C#, Ruby, Kotlin
**Frontend**: React, Vue.js, Angular, HTML, CSS, Sass, Bootstrap, Tailwind CSS
**Backend**: Django, Flask, Node.js, Express.js, Laravel, Spring Boot, FastAPI
**Databases**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
**DevOps**: Docker, Kubernetes, AWS, Google Cloud, Azure, Git, GitHub, GitLab

### Useful Admin Commands:

**Complete sample data:**
```bash
# Create complete portfolio with sample content
python manage.py populate_sample_data --settings=config.settings.development

# Reset existing data and create new
python manage.py populate_sample_data --reset --settings=config.settings.development

# Create with custom admin password
python manage.py populate_sample_data --admin-password mypassword123 --settings=config.settings.development
```

**Technologies only:**
```bash
# Populate all predefined technologies
python manage.py populate_technologies --settings=config.settings.development

# Update existing technologies
python manage.py populate_technologies --update --settings=config.settings.development

# Populate only specific category
python manage.py populate_technologies --category frontend --settings=config.settings.development
```

## 🎨 Customization

### Colors and Styles
- Edit `static/css/style.css`
- Main colors are in CSS variables

### Templates
- `templates/portfolio/` - Main pages
- `templates/portfolio/admin/` - Admin panel

### Logos and Images
- Place your logo in `static/images/`
- Update references in templates

## 🚀 Deployment

### Requirements Structure

The project uses modular requirements:

```
requirements/
├── base.txt          # Basic dependencies (Django, Pillow, etc.)
├── development.txt   # Development tools (debug-toolbar, pytest)
├── staging.txt       # For testing environment (debug + coverage)
└── production.txt    # For production (gunicorn, reportlab)
```

### For Heroku:
```bash
# 1. Install Heroku CLI and create app
heroku create your-portfolio

# 2. Configure environment variables
heroku config:set DJANGO_SETTINGS_MODULE=config.settings.production
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set ALLOWED_HOSTS_PROD=your-app.herokuapp.com

# 3. Install dependencies and deploy
git push heroku main
heroku run python manage.py migrate --settings=config.settings.production
heroku run python manage.py createsuperuser --settings=config.settings.production
```

### For VPS/DigitalOcean:
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 2. Clone and configure
git clone your-repo.git
cd portfolio
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt

# 3. Configure .env for production
cp .env.example .env
# Edit .env with production configurations

# 4. Run with Gunicorn
gunicorn config.wsgi:application --settings=config.settings.production
```

### Production Environment Variables:
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secure-secret-key
DEBUG=False
ALLOWED_HOSTS_PROD=yourdomain.com,www.yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🆘 Troubleshooting

### ALLOWED_HOSTS Error
```env
# In .env, add your IP/domain
ALLOWED_HOSTS_DEV=localhost,127.0.0.1,your-ip
```

### Database Error
```bash
# Delete and recreate migrations
rm db.sqlite3
rm portfolio/migrations/00*.py
python manage.py makemigrations portfolio --settings=config.settings.development
python manage.py migrate --settings=config.settings.development
```

### Static Files Error
```bash
python manage.py collectstatic --settings=config.settings.development
```

### Technologies Problem
```bash
# Reset and repopulate technologies
python manage.py populate_technologies --settings=config.settings.development
```

### Migration Error
```bash
# Delete and recreate portfolio-specific migrations
rm portfolio/migrations/00*.py
python manage.py makemigrations portfolio --settings=config.settings.development
python manage.py migrate --settings=config.settings.development
```

### Wrong Environment Error
Make sure to specify correct environment:
```bash
# Instead of: python manage.py runserver
python manage.py runserver --settings=config.settings.development
```

## 🎯 Advanced Features

### 📈 Analytics System
- Automatic visit tracking
- Intelligent bot and admin route exclusion
- Analytics dashboard at `/admin-analytics/`

### 🔒 Security System
- File validation with python-magic
- Custom security headers
- Configurable rate limiting
- Forms with honeypot protection

### 📧 Email System
- Secure contact form
- Configurable backend per environment
- Integrated anti-spam validation

## 📞 Support

If you need help:
1. Review complete documentation in `README.md`
2. Check GitHub issues
3. Create an issue with your specific problem

## 📄 License

MIT License - Free for personal and commercial use.

---

Congratulations! 🎉 Your professional portfolio is ready.

**Important URLs:**
- Portfolio: `http://yourdomain.com/`
- Admin: `http://yourdomain.com/admin/` (admin/admin123)
- Dashboard: `http://yourdomain.com/admin-dashboard/`
- Analytics: `http://yourdomain.com/admin-analytics/`

**Content included in sample data:**
- 📝 **6 technical articles** complete (Django APIs, Machine Learning, DevOps, React Hooks, 2024 Trends)
- 🚀 **6 detailed projects** (E-commerce, Analytics Dashboard, Microservices, etc.)
- 💼 **4 work experiences** with professional descriptions
- 🎓 **3 educations** including university and certifications
- ⚡ **20+ technical skills** with competency levels
- 📧 **5 sample messages** contact
- 🔧 **50+ technologies** with automatic icons

Share your amazing work with the world! 🚀