# Docker Compose - Comandos de Referencia Rápida

## Arquitectura Simplificada

El proyecto usa un solo servicio `web` que siempre se levanta. La diferencia entre entornos es:

- **Desarrollo:** Puerto 8000 expuesto directamente (via `docker-compose.override.yml`)
- **Staging/Prod:** Nginx como reverse proxy en puerto 80 (ignora el override)

---

## Comandos por Entorno

### Desarrollo (acceso directo a Django)

```bash
# Iniciar (el override expone puerto 8000 automáticamente)
docker compose up --build

# Iniciar en segundo plano
docker compose up -d

# Detener
docker compose down

# Ver logs
docker compose logs -f web
```

**Resultado:**
- Puerto 8000: Accesible (Django directo)
- Puerto 80: No disponible (nginx no está activo)
- Acceso: `http://localhost:8000/`

---

### Staging Local (nginx, production-like)

```bash
# Iniciar con -f para ignorar override
docker compose -f docker-compose.yml --profile staging up --build

# En segundo plano
docker compose -f docker-compose.yml --profile staging up -d

# Detener
docker compose -f docker-compose.yml --profile staging down

# Ver logs
docker compose -f docker-compose.yml --profile staging logs -f web
docker compose -f docker-compose.yml --profile staging logs -f nginx
```

**Resultado:**
- Puerto 8000: NO accesible (solo interno)
- Puerto 80: Accesible (nginx) - puede requerir permisos de administrador
- Acceso: `http://localhost/`

---

### Produccion (nginx, production)

```bash
# Iniciar con -f para ignorar override
docker compose -f docker-compose.yml --profile prod up --build

# En segundo plano
docker compose -f docker-compose.yml --profile prod up -d

# Detener
docker compose -f docker-compose.yml --profile prod down
```

**Resultado:**
- Puerto 8000: NO accesible (solo interno)
- Puertos 80/443: Configurados en nginx
---

## Tabla Comparativa

| Aspecto | Desarrollo | Staging | Produccion |
|---------|-----------|---------|------------|
| **Comando** | `docker compose up` | `docker compose -f docker-compose.yml --profile staging up` | `docker compose -f docker-compose.yml --profile prod up` |
| **Override file** | Cargado | Ignorado | Ignorado |
| **Puerto 8000** | Expuesto | Solo interno | Solo interno |
| **Puerto 80** | No disponible | Expuesto | Expuesto |
| **Nginx activo** | No | Si | Si |

---

## Regla de Oro

**Si usas `--profile staging` o `--profile prod`, SIEMPRE incluye `-f docker-compose.yml` antes.**

### Ejemplos correctos:
```bash
docker compose up                                              # Desarrollo
docker compose -f docker-compose.yml --profile staging up      # Staging
docker compose -f docker-compose.yml --profile prod up -d      # Produccion
```

### Ejemplos incorrectos:
```bash
docker compose --profile staging up    # Carga override, expone puerto 8000
docker compose --profile prod up       # Carga override, expone puerto 8000
```

---

## Comandos Utiles

```bash
# Ejecutar comandos en el contenedor web
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic

# Ver configuracion final (merged con override)
docker compose config

# Ver configuracion sin override
docker compose -f docker-compose.yml config

# Rebuild sin cache
docker compose build --no-cache

# Ver puertos expuestos
docker compose ps
```

---

## Troubleshooting

### Problema: Puedo acceder a puerto 8000 en staging

**Causa:** Usaste `docker compose --profile staging` sin `-f docker-compose.yml`

**Solucion:**
```bash
docker compose down
docker compose -f docker-compose.yml --profile staging up -d
docker compose -f docker-compose.yml --profile staging ps
```

### Problema: Cambios en .env no se reflejan

**Solucion:**
```bash
docker compose down
docker compose up --build
```

### Problema: Error "Permission denied" al iniciar nginx en puerto 80

**Causa:** El puerto 80 requiere privilegios de administrador en algunos sistemas.

**Solucion (Windows):**
```bash
# Ejecutar PowerShell como Administrador
docker compose -f docker-compose.yml --profile staging up
```

**Solucion (Linux/Mac):**
```bash
sudo docker compose -f docker-compose.yml --profile staging up
```

---

**Ultima actualizacion:** 2026-01-19
