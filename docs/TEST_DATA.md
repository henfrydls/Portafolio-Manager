# Datos de Prueba del Portfolio

Este documento explica cómo poblar el portfolio con datos de prueba para desarrollo y demostración.

## Comando Unificado

Hemos consolidado todos los comandos de datos de prueba en un solo comando: `populate_test_data`

### Uso Básico

```bash
python manage.py populate_test_data
```

Este comando creará:
- ✅ Usuario admin (username: `admin`, password: `admin123`)
- ✅ Perfil completo con información personal
- ✅ 3 experiencias laborales
- ✅ 2 entradas de educación
- ✅ 16 habilidades técnicas
- ✅ 4 idiomas hablados (English, Spanish, French, German)
- ✅ 3 proyectos destacados
- ✅ 2 posts de blog
- ✅ 5 categorías de blog
- ✅ 6 tipos de proyectos
- ✅ Tecnologías con iconos y colores
- ✅ 2 mensajes de contacto de ejemplo

### Opciones Avanzadas

#### Resetear datos existentes

```bash
python manage.py populate_test_data --reset
```

⚠️ **ADVERTENCIA**: Esto eliminará todos los datos existentes antes de crear los nuevos.

#### Cambiar contraseña del admin

```bash
python manage.py populate_test_data --admin-password mipassword123
```

### Ejemplo Completo

```bash
# Resetear todo y crear datos frescos con contraseña personalizada
python manage.py populate_test_data --reset --admin-password supersecret
```

## Datos Creados

### Perfil
- **Nombre**: Alex Developer
- **Título**: Full Stack Developer & Tech Lead
- **Email**: alex@portfolio.com
- **Ubicación**: San Francisco, CA
- **Redes sociales**: LinkedIn, GitHub, Medium

### Experiencias Laborales
1. **Senior Full Stack Developer** en TechCorp Solutions (2022 - Presente)
2. **Full Stack Developer** en StartupXYZ (2020 - 2022)
3. **Backend Developer** en Digital Agency Pro (2019 - 2020)

### Educación
1. **Computer Science, B.S.** - Stanford University (2014 - 2018)
2. **AWS Solutions Architect Professional** - Amazon Web Services (2023)

### Habilidades Técnicas
- **Lenguajes**: Python (Expert), JavaScript (Expert), TypeScript (Advanced)
- **Frontend**: React (Expert), Vue.js (Advanced), HTML5/CSS3 (Expert)
- **Backend**: Django (Expert), FastAPI (Advanced), Node.js (Advanced)
- **Bases de Datos**: PostgreSQL (Expert), MongoDB (Advanced), Redis (Intermediate)
- **DevOps**: Docker (Advanced), AWS (Advanced), Git (Expert)

### Idiomas
1. **English** - Native
2. **Spanish** - C2 (Proficient)
3. **French** - B2 (Upper Intermediate)
4. **German** - A2 (Elementary)

### Proyectos
1. **E-commerce Platform Advanced** - Plataforma completa de e-commerce
2. **Analytics Dashboard Pro** - Dashboard interactivo con visualizaciones
3. **API REST Microservices** - Arquitectura de microservicios escalable

### Posts de Blog
1. **Construyendo APIs Escalables con Django REST Framework**
2. **Introducción a Docker para Desarrolladores**

## URLs de Acceso

Después de ejecutar el comando, puedes acceder a:

- **Portfolio público**: http://localhost:8000/
- **Admin Django**: http://localhost:8000/admin/ (admin/admin123)
- **Dashboard personalizado**: http://localhost:8000/admin-dashboard/
- **Analytics**: http://localhost:8000/admin-analytics/
- **Perfil**: http://localhost:8000/admin-panel/profile/edit/

## Comandos Relacionados

El comando `populate_test_data` es el **único comando necesario** para poblar datos de prueba.

Es completamente autónomo y no depende de otros comandos.

**Comandos eliminados** (ahora integrados en `populate_test_data`):
- ~~`populate_sample_data`~~
- ~~`add_sample_projects`~~
- ~~`populate_categories`~~
- ~~`populate_project_types`~~
- ~~`populate_technologies`~~

## Notas

- El comando es **idempotente**: puedes ejecutarlo múltiples veces sin duplicar datos
- Si un elemento ya existe (por ejemplo, el usuario admin), se reutiliza
- Las tecnologías se auto-pueblan con iconos Font Awesome y colores apropiados
- Los proyectos se asignan tecnologías aleatorias de las disponibles

## Troubleshooting

### Error: "No module named 'portfolio.models'"
Asegúrate de estar en el directorio raíz del proyecto y que el entorno virtual esté activado.

### Error: "UNIQUE constraint failed"
Usa la opción `--reset` para limpiar datos existentes primero.

### Los idiomas no aparecen
Verifica que el modelo `Language` esté en las migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Desarrollo

Para modificar los datos de prueba, edita el archivo:
```
portfolio/management/commands/populate_test_data.py
```

Cada sección tiene su propia función (ej: `create_languages()`, `create_projects()`, etc.)
