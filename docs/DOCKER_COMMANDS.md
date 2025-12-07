# Docker Compose - Comandos de Referencia Rápida

## ⚠️ Advertencia Importante

El archivo `docker-compose.override.yml` se carga **automáticamente** con cualquier comando `docker compose`. Para ignorarlo, debes usar `-f docker-compose.yml` explícitamente.

## 📋 Comandos por Entorno

### 🔧 Desarrollo (con acceso directo a Django)

```bash
# Iniciar
docker compose up --build

# Iniciar en segundo plano
docker compose up -d

# Detener
docker compose down

# Ver logs
docker compose logs -f web
```

**Resultado:**
- ✅ Puerto 8000: Accesible (Django directo)
- ❌ Puerto 8080: No disponible (nginx no está activo)
- 📍 Acceso: `http://localhost:8000/`

---

### 🚀 Staging Local (solo nginx, production-like)

```bash
# ✅ CORRECTO - Inicia con -f para ignorar override
docker compose -f docker-compose.yml --profile staging up --build

# ✅ CORRECTO - En segundo plano
docker compose -f docker-compose.yml --profile staging up -d

# ✅ CORRECTO - Detener
docker compose -f docker-compose.yml --profile staging down

# ✅ CORRECTO - Ver logs
docker compose -f docker-compose.yml --profile staging logs -f web
docker compose -f docker-compose.yml --profile staging logs -f nginx

# ❌ INCORRECTO - Esto sigue cargando override file
docker compose --profile staging up
```

**Resultado:**
- ❌ Puerto 8000: NO accesible (solo interno)
- ✅ Puerto 80: Accesible (nginx) - **puede requerir permisos de administrador**
- 📍 Acceso: `http://localhost:80/` o `http://localhost/`

---

### 🌐 Producción (solo nginx, production)

```bash
# ✅ CORRECTO - Inicia con -f para ignorar override
docker compose -f docker-compose.yml --profile prod up --build

# ✅ CORRECTO - En segundo plano
docker compose -f docker-compose.yml --profile prod up -d

# ✅ CORRECTO - Detener
docker compose -f docker-compose.yml --profile prod down

# ❌ INCORRECTO - Esto sigue cargando override file
docker compose --profile prod up
```

**Resultado:**
- ❌ Puerto 8000: NO accesible (solo interno)
- ✅ Puertos 80/443: Configurados en nginx
- 📍 Acceso: `https://tudominio.com/`

---

## 🔍 Verificar Configuración Actual

```bash
# Ver puertos expuestos
docker compose ps

# Ver qué archivos está usando Docker Compose
docker compose config --files
```

**Esperado en Staging/Prod:**
```
henfrydls-web-1: 8000/tcp            ✅ Solo interno
henfrydls-nginx-1: 0.0.0.0:80->80/tcp  ✅ Expuesto
```

**NO esperado en Staging/Prod:**
```
henfrydls-web-1: 0.0.0.0:8000->8000/tcp  ❌ Expuesto (ERROR)
```

---

## 🛠️ Comandos Útiles

```bash
# Ejecutar comandos dentro del contenedor web
docker compose -f docker-compose.yml --profile staging exec web python manage.py migrate
docker compose -f docker-compose.yml --profile staging exec web python manage.py createsuperuser
docker compose -f docker-compose.yml --profile staging exec web python manage.py collectstatic

# Ver configuración final (merged)
docker compose config

# Ver configuración sin override
docker compose -f docker-compose.yml config

# Rebuild sin cache
docker compose -f docker-compose.yml --profile staging build --no-cache
```

---

## 📊 Tabla Comparativa

| Aspecto | Desarrollo | Staging Local | Producción |
|---------|-----------|---------------|------------|
| **Comando** | `docker compose up` | `docker compose -f docker-compose.yml --profile staging up` | `docker compose -f docker-compose.yml --profile prod up` |
| **Override file** | ✅ Cargado | ❌ Ignorado | ❌ Ignorado |
| **Puerto 8000** | ✅ Expuesto | ❌ Solo interno | ❌ Solo interno |
| **Puerto 80** | ❌ No disponible | ✅ Expuesto (puede requerir admin) | ✅ Expuesto |
| **Puerto 443** | ❌ No usado | ❌ No usado (SSL no configurado) | ✅ Expuesto (con SSL) |
| **Nginx activo** | ❌ No | ✅ Sí | ✅ Sí |
| **Acceso directo Django** | ✅ Sí | ❌ No | ❌ No |

---

## 🔑 Regla de Oro

**Si ves `--profile staging` o `--profile prod`, SIEMPRE debe incluir `-f docker-compose.yml` antes.**

### ✅ Ejemplos correctos:
```bash
docker compose -f docker-compose.yml --profile staging up
docker compose -f docker-compose.yml --profile prod up -d
docker compose -f docker-compose.yml --profile staging logs -f web
```

### ❌ Ejemplos incorrectos:
```bash
docker compose --profile staging up          # ❌ Carga override
docker compose --profile prod up             # ❌ Carga override
docker compose --profile staging logs web    # ❌ Carga override
```

---

## 🐛 Troubleshooting

### Problema: Puedo acceder a puerto 8000 en staging

**Causa:** Estás usando `docker compose --profile staging` sin `-f docker-compose.yml`

**Solución:**
```bash
# Detener todo
docker compose down

# Iniciar correctamente
docker compose -f docker-compose.yml --profile staging up -d

# Verificar puertos
docker compose -f docker-compose.yml --profile staging ps
```

### Problema: Cambié .env pero no veo cambios

**Solución:**
```bash
# Detener y reconstruir
docker compose -f docker-compose.yml --profile staging down
docker compose -f docker-compose.yml --profile staging up --build
```

### Problema: Error "Permission denied" al iniciar nginx en puerto 80

**Causa:** El puerto 80 requiere privilegios de administrador/root en algunos sistemas operativos.

**Solución (Linux/Mac):**
```bash
# Opción 1: Ejecutar con sudo
sudo docker compose -f docker-compose.yml --profile staging up

# Opción 2: Cambiar temporalmente el puerto en docker-compose.yml
# Editar nginx ports de "80:80" a "8080:80"
# Luego acceder vía http://localhost:8080/
```

**Solución (Windows):**
```bash
# Ejecutar PowerShell o CMD como Administrador, luego:
docker compose -f docker-compose.yml --profile staging up
```

**Nota:** En producción (servidor AWS EC2, DigitalOcean, etc.) normalmente no tendrás este problema porque Docker tiene los permisos necesarios.

---

**Última actualización:** 2025-12-07
