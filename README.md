# henfrydls.com - Personal Portfolio

[🇪🇸 Español](#español) | [🇺🇸 English](#english)

---

## English

Personal portfolio website for Henfry de los Santos built with Django.

### Features

- **Single-page portfolio** inspired by Matt Deitke's design with fixed sidebar layout
- **Fixed profile sidebar** with personal information, contact details, and navigation
- **Recent posts section** with clickable Medium-like blog articles
- **Featured Work section** showcasing major projects and achievements
- **Projects section** displaying all development work and technologies
- **Medium-style blog detail pages** with professional typography and responsive design
- **Admin panel** for content management
- **Responsive design** optimized for desktop and mobile devices

### Design Inspiration

This portfolio is inspired by **Matt Deitke's website** design, featuring:
- **Fixed sidebar layout** with profile information always visible
- **Clean typography** using Montserrat font family
- **Minimalist aesthetic** with consistent spacing and neutral colors
- **Professional color scheme** with #fafafa background and #0085ff accent color

### Technologies

- **Backend**: Django 5.2
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, JavaScript, Montserrat Typography
- **Design System**: Matt Deitke-inspired layout with Medium-style blog posts
- **Static Files**: WhiteNoise
- **Email**: Django Email Backend

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd henfrydls-portfolio
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate --settings=config.settings.development
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser --settings=config.settings.development
   ```

7. **Start development server**
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```

8. **Access the application**
   - Website: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

### URL Structure

- `/` - Single-page portfolio homepage
- `/post/<slug>/` - Medium-style blog post detail pages
- `/admin-dashboard/` - Admin dashboard (protected)
- `/admin-analytics/` - Analytics dashboard (protected)
- `/admin/` - Django admin panel

**Main sections accessible via anchors:**
- `/#about` - About section
- `/#recent` - Recent posts
- `/#featured` - Featured work
- `/#projects` - All projects

### Production Deployment

1. **Install production dependencies**
   ```bash
   pip install -r requirements/production.txt
   ```

2. **Set production environment variables**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.production
   export SECRET_KEY=your-production-secret-key
   export EMAIL_HOST_USER=your-email@gmail.com
   export EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Run migrations and collect static files**
   ```bash
   python manage.py migrate --settings=config.settings.production
   python manage.py collectstatic --settings=config.settings.production
   ```

4. **Run with Gunicorn**
   ```bash
   gunicorn config.wsgi:application --settings=config.settings.production
   ```

---

## Español

Portafolio web personal de Henfry de los Santos desarrollado con Django.

### Características

- **Portafolio de una sola página** inspirado en el diseño de Matt Deitke con barra lateral fija
- **Barra lateral de perfil fija** con información personal, detalles de contacto y navegación
- **Sección Recent** con artículos de blog clickeables estilo Medium
- **Sección Featured Work** mostrando proyectos principales y logros
- **Sección Projects** mostrando todo el trabajo de desarrollo y tecnologías
- **Páginas de detalle de blog estilo Medium** con tipografía profesional y diseño responsivo
- **Panel de administración** para gestión de contenido
- **Diseño responsivo** optimizado para escritorio y móvil

### Tecnologías

- **Backend**: Django 5.2
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (listo para producción)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Archivos Estáticos**: WhiteNoise
- **Generación PDF**: ReportLab / WeasyPrint
- **Email**: Django Email Backend

### Inicio Rápido

#### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

#### Configuración del Entorno de Desarrollo

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd henfrydls-portfolio
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   
   # En Windows
   .venv\Scripts\activate
   
   # En Linux/Mac
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar migraciones**
   ```bash
   python manage.py migrate --settings=config.settings.development
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser --settings=config.settings.development
   ```

7. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```

8. **Acceder a la aplicación**
   - Sitio web: http://127.0.0.1:8000/
   - Panel de administración: http://127.0.0.1:8000/admin/

### Estructura de URLs

- `/` - Portafolio de una sola página
- `/post/<slug>/` - Páginas de detalle de blog estilo Medium
- `/admin-dashboard/` - Dashboard de admin (protegido)
- `/admin-analytics/` - Dashboard de análiticas (protegido)
- `/admin/` - Panel de administración de Django

**Secciones principales accesibles via anchors:**
- `/#about` - Sección Acerca de
- `/#recent` - Posts recientes
- `/#featured` - Trabajo destacado
- `/#projects` - Todos los proyectos

### Configuración de Producción

1. **Instalar dependencias de producción**
   ```bash
   pip install -r requirements/production.txt
   ```

2. **Configurar variables de entorno de producción**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.production
   export SECRET_KEY=your-production-secret-key
   export EMAIL_HOST_USER=your-email@gmail.com
   export EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Ejecutar migraciones y recopilar archivos estáticos**
   ```bash
   python manage.py migrate --settings=config.settings.production
   python manage.py collectstatic --settings=config.settings.production
   ```

4. **Ejecutar con Gunicorn**
   ```bash
   gunicorn config.wsgi:application --settings=config.settings.production
   ```

### Estructura del Proyecto

```
portfolio_managment/
├── .venv/                      # Entorno virtual
├── config/                     # Configuración Django
│   ├── settings/              # Settings modulares
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI configuration
├── portfolio/                  # Aplicación principal
│   ├── models.py             # Modelos de datos
│   ├── views.py              # Vistas
│   ├── urls.py               # URLs de la app
│   ├── admin.py              # Configuración admin
│   ├── forms.py              # Formularios
│   └── utils.py              # Utilidades
├── static/                     # Archivos estáticos
├── media/                      # Archivos subidos
├── templates/                  # Templates HTML
├── requirements/               # Dependencias por entorno
└── manage.py                   # Script de gestión Django
```

### Comandos Útiles

```bash
# Ejecutar tests
python manage.py test --settings=config.settings.development

# Crear migraciones
python manage.py makemigrations --settings=config.settings.development

# Shell de Django
python manage.py shell --settings=config.settings.development

# Recopilar archivos estáticos
python manage.py collectstatic --settings=config.settings.development

# Poblar tecnologías predefinidas
python manage.py populate_technologies --settings=config.settings.development

# Actualizar tecnologías existentes
python manage.py populate_technologies --update --settings=config.settings.development

# Poblar solo una categoría específica
python manage.py populate_technologies --category frontend --settings=config.settings.development

# Verificar configuración del sistema
python manage.py check --settings=config.settings.development
```

### Modelos de Datos

El proyecto incluye los siguientes modelos principales:

- **Profile**: Información personal y configuración del portafolio
- **Project**: Proyectos con soporte para visibilidad pública/privada
- **Technology**: Tecnologías con más de 50 opciones predefinidas, iconos automáticos y colores oficiales
- **Experience**: Historial laboral
- **Education**: Educación formal, cursos online, certificaciones
- **Skill**: Habilidades técnicas con niveles de competencia y barras visuales
- **BlogPost**: Sistema de blog con múltiples tipos de contenido y gestión avanzada
- **Contact**: Mensajes del formulario de contacto con estado de lectura
- **PageVisit**: Tracking básico de visitas con middleware personalizado

### 🎨 Sistema de Tecnologías Avanzado

El modelo Technology incluye funcionalidades avanzadas:

#### Tecnologías Predefinidas (50+)
- **Lenguajes**: Python, JavaScript, Java, PHP, Swift, Rust, Go, C++, C#, Ruby, Kotlin, TypeScript
- **Frontend**: React, Vue.js, Angular, HTML, CSS, Sass, Bootstrap, Tailwind CSS
- **Backend**: Django, Flask, Node.js, Express.js, Laravel, Spring Boot, FastAPI
- **Bases de Datos**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
- **DevOps**: Docker, Kubernetes, AWS, Google Cloud, Azure, Git, GitHub, GitLab
- **Herramientas**: Linux, Ubuntu, Windows, macOS, VS Code, Figma, Slack, Trello

#### Comandos de Gestión
```bash
# Poblar todas las tecnologías predefinidas
python manage.py populate_technologies --settings=config.settings.development

# Actualizar tecnologías existentes con sugerencias
python manage.py populate_technologies --update --settings=config.settings.development

# Poblar solo una categoría específica
python manage.py populate_technologies --category languages --settings=config.settings.development
```

#### Funcionalidades del Admin
- **Sugerencias Automáticas**: Iconos y colores basados en el nombre de la tecnología
- **Aplicación Masiva**: Acciones para aplicar sugerencias a múltiples tecnologías
- **Vista Previa Visual**: Iconos y colores mostrados en tiempo real
- **Enlaces de Referencia**: Links directos a Font Awesome, Devicon y Simple Icons

### 📊 Middleware de Tracking

Sistema de tracking personalizado que incluye:

- **Exclusión Inteligente**: Automáticamente excluye rutas admin, archivos estáticos y bots conocidos
- **Información Capturada**: URL, título de página, IP, user agent, timestamp
- **Limpieza Automática**: Eliminación periódica de registros antiguos (configurable)
- **Configuración Flexible**: Personalizable a través de settings de Django

### Contribución

Este es un proyecto personal, pero si encuentras algún bug o tienes sugerencias, no dudes en crear un issue.

### Licencia

Este proyecto es de uso personal y educativo.

### Contacto

- **Email**: henfry@henfrydls.com
- **GitHub**: https://github.com/henfrydls
- **LinkedIn**: https://linkedin.com/in/henfrydls

---

## Project Status

✅ **Models**: Data models implemented  
🔄 **Views**: In development  
🔄 **Templates**: In development  
🔄 **Admin**: In development  
🔄 **Tests**: Pending  

### Contributing

This is a personal project, but if you find any bugs or have suggestions, feel free to create an issue.

### License

This project is for personal and educational use.

### Contact

- **Email**: henfry@henfrydls.com
- **GitHub**: https://github.com/henfrydls
- **LinkedIn**: https://linkedin.com/in/henfrydls