# 🐳 Docker Deployment Guide

Guía completa para usar las imágenes Docker publicadas automáticamente en cada release.

---

## 📦 Dónde se Publican las Imágenes

Las imágenes Docker se publican automáticamente en **GitHub Container Registry (GHCR)** cada vez que se crea un nuevo release.

**Registry URL:** `ghcr.io/henfrydls/portafolio-manager`

**Visibilidad:** Pública (cualquiera puede descargar las imágenes)

**Navegador Web:**
https://github.com/henfrydls/Portafolio-Manager/pkgs/container/portafolio-manager

---

## 🏗️ Arquitecturas Disponibles

Cada release incluye imágenes para **2 arquitecturas**:

| Arquitectura | Descripción | Uso Común |
|--------------|-------------|-----------|
| **linux/amd64** (x86_64) | Intel/AMD tradicional | AWS EC2, DigitalOcean, Google Cloud, Azure, servidores físicos |
| **linux/arm64** (ARM64) | Procesadores ARM | Mac M1/M2/M3, AWS Graviton, Raspberry Pi, Oracle ARM |

Docker **automáticamente selecciona** la imagen correcta para tu arquitectura cuando haces `docker pull`.

---

## 🚀 Deployment en Producción

### Opción 1: Deployment Directo (Servidor Único)

```bash
# 1. SSH a tu servidor de producción
ssh user@your-server.com

# 2. Pull la última imagen (o una versión específica)
docker pull ghcr.io/henfrydls/portafolio-manager:latest
# O una versión específica:
docker pull ghcr.io/henfrydls/portafolio-manager:v1.2.0

# 3. Detener el contenedor actual (si existe)
docker stop portfolio_web
docker rm portfolio_web

# 4. Correr la nueva versión
docker run -d \
  --name portfolio_web \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v /data/media:/app/media \
  -v /data/static:/app/staticfiles \
  ghcr.io/henfrydls/portafolio-manager:v1.2.0 \
  gunicorn Portafolio_Manager.wsgi:application --bind 0.0.0.0:8000
```

### Opción 2: Usando Docker Compose (Recomendado)

Actualiza tu `docker-compose.yml` en producción:

```yaml
version: '3.8'

services:
  web:
    image: ghcr.io/henfrydls/portafolio-manager:v1.2.0  # Cambiar versión aquí
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - media:/app/media
      - staticfiles:/app/staticfiles
    depends_on:
      - db
      - redis
    command: gunicorn Portafolio_Manager.wsgi:application --bind 0.0.0.0:8000 --workers 4

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: portfolio
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
  media:
  staticfiles:
```

**Deployment con Docker Compose:**

```bash
# 1. SSH a servidor
ssh user@your-server.com

# 2. Ir al directorio del proyecto
cd /opt/portfolio

# 3. Editar docker-compose.yml para actualizar la versión de la imagen
nano docker-compose.yml  # Cambiar v1.1.0 → v1.2.0

# 4. Pull nueva imagen
docker compose pull web

# 5. Recrear solo el servicio web (sin downtime si tienes nginx)
docker compose up -d web

# 6. Verificar logs
docker compose logs -f web
```

### Opción 3: Blue-Green Deployment (Zero Downtime)

```bash
# 1. Correr nueva versión en puerto diferente
docker run -d \
  --name portfolio_web_new \
  -p 8001:8000 \
  --env-file .env \
  ghcr.io/henfrydls/portafolio-manager:v1.2.0 \
  gunicorn Portafolio_Manager.wsgi:application --bind 0.0.0.0:8000

# 2. Esperar a que esté listo (health check)
curl http://localhost:8001/health || echo "Esperando..."
sleep 5

# 3. Actualizar nginx para apuntar al nuevo puerto
# (editar upstream en /etc/nginx/sites-available/portfolio)

# 4. Reload nginx (sin downtime)
sudo nginx -t && sudo nginx -s reload

# 5. Detener versión anterior
docker stop portfolio_web
docker rm portfolio_web

# 6. Renombrar nuevo contenedor
docker rename portfolio_web_new portfolio_web
```

---

## 🔄 Actualización Automática con Watchtower

Puedes usar **Watchtower** para actualizar automáticamente los contenedores cuando salga una nueva versión:

```yaml
# Agregar a docker-compose.yml
services:
  watchtower:
    image: containrrr/watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 3600 --cleanup portfolio_web
    # Checa cada hora si hay nueva imagen con tag 'latest'
```

**⚠️ Nota:** Esto solo funciona con el tag `:latest`. Para producción, es más seguro usar versiones específicas y actualizar manualmente.

---

## 🏷️ Estrategia de Tags

Las imágenes se publican con múltiples tags:

| Tag | Descripción | Cuándo Usar |
|-----|-------------|-------------|
| `latest` | Última versión estable | **Desarrollo/Testing** |
| `v1.2.0` | Versión específica | **Producción** (recomendado) |
| `v1.2` | Versión minor | Recibir patches automáticos |
| `v1` | Versión major | Recibir features compatibles |

**Recomendación para Producción:** Usar tags de **versión específica** (e.g., `v1.2.0`) para evitar actualizaciones inesperadas.

---

## 📋 Checklist de Deployment

Antes de actualizar en producción:

- [ ] Crear backup de la base de datos
- [ ] Leer release notes del nuevo release
- [ ] Verificar que no haya breaking changes
- [ ] Revisar logs de CI/CD (todos los tests pasaron)
- [ ] Pull de la nueva imagen en servidor de staging
- [ ] Probar en staging primero
- [ ] Crear snapshot/backup del servidor
- [ ] Ejecutar deployment en producción
- [ ] Verificar que todo funcione correctamente
- [ ] Monitorear logs por 15-30 minutos

---

## 🔍 Verificar Versión Actual en Producción

```bash
# Ver qué imagen está corriendo
docker ps | grep portfolio

# Inspeccionar la imagen para ver el tag
docker inspect portfolio_web | grep -i image

# Ver logs de la aplicación (debería mostrar versión en startup)
docker logs portfolio_web | head -20
```

---

## 🛠️ Comandos Útiles

### Ver todas las versiones disponibles

```bash
# Listar tags disponibles en GHCR
docker pull ghcr.io/henfrydls/portafolio-manager --all-tags
```

### Rollback a versión anterior

```bash
# Si algo sale mal, volver a la versión anterior
docker compose down
# Editar docker-compose.yml para usar v1.1.4
docker compose up -d
```

### Inspeccionar imagen antes de deployment

```bash
# Pull de la imagen
docker pull ghcr.io/henfrydls/portafolio-manager:v1.2.0

# Inspeccionar capas y tamaño
docker history ghcr.io/henfrydls/portafolio-manager:v1.2.0

# Verificar arquitectura
docker inspect ghcr.io/henfrydls/portafolio-manager:v1.2.0 | grep -i arch

# Correr comandos dentro de la imagen
docker run --rm -it ghcr.io/henfrydls/portafolio-manager:v1.2.0 /bin/bash
```

---

## 🌐 Ejemplo: Deployment en AWS EC2

```bash
# 1. Conectar a EC2
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 2. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 3. Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Crear directorio para la aplicación
mkdir -p /opt/portfolio
cd /opt/portfolio

# 5. Crear archivo .env con variables de entorno
nano .env

# 6. Crear docker-compose.yml (como el ejemplo de arriba)
nano docker-compose.yml

# 7. Pull de la imagen
docker compose pull

# 8. Iniciar servicios
docker compose up -d

# 9. Verificar logs
docker compose logs -f web
```

---

## 📊 Monitoring Post-Deployment

```bash
# Verificar que todos los contenedores estén running
docker compose ps

# Ver logs en tiempo real
docker compose logs -f web

# Ver uso de recursos
docker stats portfolio_web

# Verificar endpoint de salud (si existe)
curl http://localhost:8000/health

# Ver últimas 100 líneas de logs
docker compose logs --tail=100 web
```

---

## 🔐 Seguridad

Las imágenes publicadas en GHCR son **públicas**, pero esto es seguro porque:

✅ No contienen secretos (variables de entorno se pasan en runtime)
✅ Son escaneadas por Trivy, CodeQL, Semgrep antes de publicarse
✅ Incluyen SBOM (Software Bill of Materials) para auditoría
✅ Son firmadas con attestations de GitHub Actions

**Nunca incluir en la imagen:**
- Archivos `.env`
- Credenciales de base de datos
- API keys
- Certificados SSL

Todo esto debe pasarse mediante:
- Variables de entorno (`--env-file .env`)
- Secrets de Docker/Kubernetes
- Volúmenes externos

---

## 🆘 Troubleshooting

### Error: "Cannot pull image"

```bash
# La imagen es pública, no necesitas autenticación
# Pero si tienes problemas, verifica:
docker logout ghcr.io
docker pull ghcr.io/henfrydls/portafolio-manager:latest
```

### Error: "Architecture mismatch"

```bash
# Verificar arquitectura del servidor
uname -m
# Si es ARM (aarch64), asegúrate que Docker esté usando la imagen ARM64
docker inspect ghcr.io/henfrydls/portafolio-manager:latest | grep -i arch
```

### Contenedor se reinicia constantemente

```bash
# Ver logs completos
docker logs portfolio_web

# Errores comunes:
# - Variables de entorno faltantes (.env incompleto)
# - Base de datos no accesible
# - Puerto 8000 ya en uso
```

---

## 📚 Recursos Adicionales

- **GitHub Releases:** https://github.com/henfrydls/Portafolio-Manager/releases
- **Container Registry:** https://github.com/henfrydls/Portafolio-Manager/pkgs/container/portafolio-manager
- **Docker Documentation:** https://docs.docker.com/
- **Docker Compose Reference:** https://docs.docker.com/compose/

---

**Última actualización:** 2026-01-17
**Versión del documento:** 1.0.0
