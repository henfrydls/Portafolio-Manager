# Context Variables Documentation

Este documento lista todas las variables de contexto requeridas por cada vista y template.

**Última actualización**: 2026-01-04
**Propósito**: Prevenir errores de variables faltantes en templates después de refactorizaciones.

---

## HomeView (`portfolio/views/general.py`)

**Template**: `templates/portfolio/home.html`
**URL**: `/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `profile` | Profile | Información del perfil del usuario | ✅ Pasada |
| `featured_projects` | QuerySet | Proyectos marcados como destacados | ✅ Pasada |
| `recent_projects` | QuerySet | 6 proyectos más recientes | ✅ Pasada |
| `featured_posts` | QuerySet | Posts destacados del blog | ✅ Pasada |
| `latest_posts` | QuerySet | 3 posts más recientes | ✅ Pasada |
| `featured_items` | List | Mezcla de proyectos y posts destacados (max 4) | ✅ Pasada (fix: bb06113) |
| `projects` | Page | Proyectos paginados para "Work & Projects" | ✅ Pasada (fix: bf5fc57) |
| `projects_paginator` | Paginator | Paginador de proyectos | ✅ Pasada (fix: bf5fc57) |
| `projects_page_obj` | Page | Objeto de página actual | ✅ Pasada (fix: bf5fc57) |
| `contact_form` | Form | Formulario de contacto | ✅ Pasada |
| `seo` | Dict | Metadatos SEO | ✅ Pasada |
| `structured_data` | List | JSON-LD estructurado | ✅ Pasada |

### Notas
- `featured_items` se genera con `QueryOptimizer.get_featured_items_optimized(limit=4)`
- Combina proyectos y posts destacados ordenados por `order` y fecha
- `projects` usa paginación de 10 elementos por página

---

## BlogListView (`portfolio/views/blog.py`)

**Template**: `templates/portfolio/blog_list.html`
**URL**: `/blog/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `posts` | QuerySet (paginado) | Posts del blog publicados | ✅ Pasada (context_object_name) |
| `profile` | Profile | Información del perfil | ✅ Pasada |
| `categories` | QuerySet | Categorías activas (max 6) | ✅ Pasada |
| `available_tags` | List | Lista única de tags | ✅ Pasada |
| `current_category` | str | Slug de categoría filtrada | ✅ Pasada |
| `current_tag` | str | Tag filtrado | ✅ Pasada |
| `current_search` | str | Término de búsqueda | ✅ Pasada |
| `featured_posts` | QuerySet | Posts destacados (max 5) | ✅ Pasada |
| `seo` | Dict | Metadatos SEO | ✅ Pasada |
| `is_paginated` | bool | Si hay paginación | ✅ Auto (ListView) |
| `page_obj` | Page | Objeto de página | ✅ Auto (ListView) |

### Notas
- `paginate_by = 10`
- Filtros: category, tag, search
- Tags extraídos de `post.get_tags_list()`

---

## BlogDetailView (`portfolio/views/blog.py`)

**Template**: `templates/portfolio/blog_detail.html`
**URL**: `/blog/<slug>/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `post` | BlogPost | Post individual | ✅ Pasada (context_object_name) |
| `seo` | Dict | Metadatos SEO del post | ✅ Pasada |

### Notas
- Solo posts con `status='published'`
- SEO generado con `SEOGenerator.generate_blog_post_seo()`

---

## ProjectListView (`portfolio/views/projects.py`)

**Template**: `templates/portfolio/project_list.html`
**URL**: `/projects/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `projects` | QuerySet (paginado) | Proyectos públicos | ✅ Pasada (context_object_name) |
| `knowledge_bases` | QuerySet | Tecnologías para filtro | ✅ Pasada |
| `current_tech` | str | Tecnología filtrada | ✅ Pasada |
| `current_search` | str | Término de búsqueda | ✅ Pasada |
| `is_paginated` | bool | Si hay paginación | ✅ Auto (ListView) |
| `page_obj` | Page | Objeto de página | ✅ Auto (ListView) |

### Notas
- `paginate_by = 12`
- Filtros: tech, search
- Solo proyectos con `visibility='public'`
- Optimizado con `select_related` y `prefetch_related`

---

## ProjectDetailView (`portfolio/views/projects.py`)

**Template**: `templates/portfolio/project_detail.html`
**URL**: `/projects/<slug>/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `project` | Project | Proyecto individual | ✅ Pasada (context_object_name) |
| `related_projects` | QuerySet | Proyectos relacionados (max 3) | ✅ Pasada |
| `seo` | Dict | Metadatos SEO | ✅ Pasada |

### Notas
- Proyectos relacionados filtrados por `knowledge_bases` compartidos
- Solo proyectos con `visibility='public'`

---

## ResumeView (`portfolio/views/resume.py`)

**Template**: `templates/portfolio/resume.html`
**URL**: `/cv/` o `/resume/`

### Variables Requeridas

| Variable | Tipo | Descripción | Estado |
|----------|------|-------------|---------|
| `profile` | Profile | Información del perfil | ✅ Pasada |
| `last_updated` | datetime | Fecha de última actualización | ✅ Pasada |
| `experiences` | QuerySet | Experiencias laborales | ✅ Pasada |
| `formal_education` | QuerySet | Educación formal | ✅ Pasada |
| `certifications` | QuerySet | Certificaciones | ✅ Pasada |
| `online_courses` | QuerySet | Cursos online | ✅ Pasada |
| `bootcamps` | QuerySet | Bootcamps y workshops | ✅ Pasada |
| `top_institutions` | List[Dict] | Top 5 instituciones (nombre, count) | ✅ Pasada |
| `skills_by_category` | Dict | Skills agrupados por categoría | ✅ Pasada |
| `languages` | QuerySet | Idiomas | ✅ Pasada |
| `seo` | Dict | Metadatos SEO | ✅ Pasada |

### Notas
- `top_institutions` calculado con `Counter` de instituciones de `online_courses`
- Skills agrupados manualmente por categoría en la vista
- Educación filtrada por tipo: formal, certification, online_course, bootcamp/workshop

---

## Convenciones de Nomenclatura

### Variables Comunes (Todas las Vistas)

| Variable | Tipo | Cuándo Usar |
|----------|------|-------------|
| `profile` | Profile | Siempre que se muestre header/footer con info del usuario |
| `seo` | Dict | Todas las vistas públicas (generado por `SEOGenerator`) |
| `structured_data` | List/Dict | Vistas principales para Schema.org markup |

### Variables de Paginación (ListView)

| Variable | Tipo | Automático | Manual |
|----------|------|------------|--------|
| `is_paginated` | bool | ✅ | - |
| `page_obj` | Page | ✅ | - |
| `paginator` | Paginator | ✅ | - |
| `<object>_list` o `<context_object_name>` | QuerySet | ✅ | - |

### Variables de Filtros

Patrón: `current_<filter_name>`

Ejemplos:
- `current_category` (BlogListView)
- `current_tag` (BlogListView)
- `current_tech` (ProjectListView)
- `current_search` (varias vistas)

---

## Checklist de Prevención

Cuando crees o modifiques una vista:

1. **Leer el template primero**
   ```bash
   grep -E "{% if |{% for " templates/portfolio/<template>.html
   ```

2. **Listar variables esperadas**
   - Identificar todas las variables usadas en condicionales `{% if %}`
   - Identificar todas las variables en loops `{% for %}`

3. **Verificar que la vista las pase**
   ```python
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['variable_esperada'] = ...
       return context
   ```

4. **Probar en local antes de deploy**
   - Visitar la página en desarrollo
   - Verificar que no haya secciones vacías
   - Revisar logs de Django para errores de variables

5. **Actualizar este documento**
   - Agregar nuevas variables descubiertas
   - Marcar estado (✅ Pasada / ❌ Faltante)

---

## Problemas Comunes Resueltos

### 1. Media Files No Se Muestran

**Síntoma**: Imágenes no cargan
**Causas**:
- Volumen Docker vs bind mount
- Permisos de directorio (`chmod 755 /home/ubuntu`)

**Solución**: Cambiar a bind mount en `docker-compose.yml`
```yaml
volumes:
  - ./media:/app/media  # ✅ Bind mount
  # - mediafiles:/app/media  # ❌ Volumen aislado
```

### 2. Secciones Vacías en Templates

**Síntoma**: Sección no aparece en la página
**Causa**: Variable de contexto faltante

**Ejemplo**:
```html
{% if featured_items %}  <!-- Si esta variable es None, toda la sección se oculta -->
<div class="section">...</div>
{% endif %}
```

**Solución**: Agregar variable en la vista
```python
context['featured_items'] = QueryOptimizer.get_featured_items_optimized(limit=4)
```

### 3. Paginación No Funciona

**Síntoma**: No hay controles de paginación
**Causa**: No se pasó el objeto paginador o página

**Solución**: Para vistas manuales (no ListView)
```python
from django.core.paginator import Paginator

all_items = MyModel.objects.all()
page_num = self.request.GET.get('page', 1)
paginator = Paginator(all_items, 10)
page_obj = paginator.get_page(page_num)

context['items'] = page_obj
context['paginator'] = paginator  # Template necesita esto
context['page_obj'] = page_obj    # Template necesita esto
```

---

## Recursos

- **SEO Generator**: `portfolio/utils/seo.py`
- **Query Optimizer**: `portfolio/query_optimizations.py`
- **Decorators**: `portfolio/utils/decorators.py`
- **Forms**: `portfolio/forms/*.py`

---

## Historial de Cambios

| Fecha | Commit | Cambio |
|-------|--------|--------|
| 2026-01-04 | `859f3c7` | Fix media files sync (bind mount) |
| 2026-01-04 | `bf5fc57` | Fix: add pagination for projects in HomeView |
| 2026-01-04 | `bb06113` | Fix: add featured_items to HomeView context |
| 2026-01-04 | - | Documento creado |
