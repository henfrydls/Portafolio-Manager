# 🚀 Deployment Automatizado

Guía completa para configurar deployments automatizados usando imágenes GHCR.

---

## 📋 Opciones Disponibles

| Opción | Trigger | Complejidad | Control | Recomendado Para |
|--------|---------|-------------|---------|------------------|
| **Opción 1: Watchtower** | Automático (cada hora) | Baja | Bajo | Staging, desarrollo |
| **Opción 2: GitHub Actions** | Manual o auto | Media | Alto | Producción |
| **Opción 3: Webhook** | Al hacer release | Alta | Medio | Avanzado |

---

## Opción 1: Watchtower (Deployment 100% Automático)

### ✅ Ventajas
- Setup súper simple (1 contenedor)
- Completamente automático
- No requiere configuración de GitHub
- Monitorea GHCR y actualiza cuando detecta cambios

### ❌ Desventajas
- Poco control sobre cuándo se despliega
- No hay aprobación manual
- Solo funciona con tag `:latest`

### 🔧 Setup

**1. En tu servidor de producción:**

```bash
cd ~/Portafolio-Manager

# Descargar configuración de Watchtower
curl -O https://raw.githubusercontent.com/henfrydls/Portafolio-Manager/main/deploy/watchtower-docker-compose.yml

# Iniciar Watchtower
docker compose -f deploy/watchtower-docker-compose.yml up -d

# Verificar logs
docker logs watchtower -f
```

**2. Modificar tu `docker-compose.yml`:**

```yaml
services:
  web:
    # Cambiar de 'build: .' a:
    image: ghcr.io/henfrydls/portafolio-manager:latest

    # Añadir etiqueta para que Watchtower lo monitoree
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
```

**3. Aplicar cambios:**

```bash
docker compose up -d web
```

**¡Listo!** Watchtower chequeará cada hora si hay una nueva imagen y actualizará automáticamente.

### ⚙️ Configuración Avanzada

```yaml
# En deploy/watchtower-docker-compose.yml
environment:
  # Chequear cada 30 minutos (1800 segundos)
  WATCHTOWER_POLL_INTERVAL: 1800

  # Solo actualizar a una hora específica (3 AM)
  WATCHTOWER_SCHEDULE: "0 0 3 * * *"

  # Notificaciones por Slack
  WATCHTOWER_NOTIFICATIONS: slack
  WATCHTOWER_NOTIFICATION_SLACK_HOOK_URL: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Opción 2: GitHub Actions Deploy Workflow (Recomendado para Producción)

### ✅ Ventajas
- Control total sobre cuándo desplegar
- Backup automático antes de deployment
- Rollback automático si falla
- Verificación post-deployment
- Logs centralizados en GitHub

### ❌ Desventajas
- Requiere configuración de SSH keys
- Requiere secrets en GitHub

### 🔧 Setup

#### Paso 1: Generar SSH Key para Deployment

En tu servidor de producción:

```bash
# Generar nueva SSH key (sin passphrase)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# Ver la clave privada (la vas a copiar a GitHub Secrets)
cat ~/.ssh/github_actions_deploy

# Agregar la clave pública a authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# Verificar permisos
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### Paso 2: Configurar Secrets en GitHub

Ve a: **GitHub Repository → Settings → Secrets and variables → Actions → New repository secret**

Crea estos 3 secrets:

| Secret Name | Valor | Ejemplo |
|-------------|-------|---------|
| `PRODUCTION_SSH_KEY` | Contenido de `~/.ssh/github_actions_deploy` (la privada) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `PRODUCTION_HOST` | IP o dominio de tu servidor | `3.83.123.45` o `server.henfrydls.com` |
| `PRODUCTION_USER` | Usuario SSH | `ubuntu` |

**Screenshots del proceso:**

```bash
# 1. Copiar la clave privada
cat ~/.ssh/github_actions_deploy

# 2. Ir a GitHub → Settings → Secrets → New secret
# 3. Name: PRODUCTION_SSH_KEY
# 4. Value: Pegar la clave completa (incluyendo -----BEGIN y -----END)
# 5. Add secret
```

#### Paso 3: Deployment Manual

Una vez configurado, puedes deployar desde GitHub:

1. Ve a: **Actions → Deploy to Production → Run workflow**
2. Selecciona:
   - **Version:** `v1.2.0` o `latest`
   - **Environment:** `production` o `staging`
3. Click **Run workflow**

El workflow hará:
1. ✅ Backup de base de datos
2. ✅ Pull de nueva imagen
3. ✅ Actualizar contenedor
4. ✅ Verificar que funciona
5. ✅ Rollback automático si falla

#### Paso 4: Auto-Deploy (Opcional)

Si quieres deployment automático después de cada release exitoso, edita `.github/workflows/deploy.yml`:

```yaml
# Descomentar estas líneas:
workflow_run:
  workflows: ["Release"]
  types:
    - completed
  branches: [main]
```

---

## Opción 3: Webhook + Script de Deployment

### ✅ Ventajas
- Deployment inmediato al hacer release
- No requiere GitHub Actions runners

### ❌ Desventajas
- Requiere configurar webhook endpoint
- Más complejo de setup

### 🔧 Setup

**1. Crear script de deployment en el servidor:**

```bash
# Crear script
cat > ~/deploy-portfolio.sh << 'EOF'
#!/bin/bash
set -e

DEPLOY_DIR="/home/ubuntu/Portafolio-Manager"
BACKUP_DIR="/home/ubuntu/backups"

echo "🚀 Starting deployment..."

cd $DEPLOY_DIR

# 1. Backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
docker compose exec -T db pg_dump -U portfolio -d portfolio -F c > \
  $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).dump

# 2. Pull nueva imagen
echo "⬇️  Pulling new image..."
docker compose pull web

# 3. Actualizar
echo "🔄 Updating containers..."
docker compose up -d web

# 4. Verificar
sleep 10
if docker compose ps | grep -q "Up.*web"; then
  echo "✅ Deployment successful!"
else
  echo "❌ Deployment failed!"
  exit 1
fi

# 5. Cleanup
echo "🧹 Cleaning up old images..."
docker image prune -a -f --filter "until=72h"

echo "🎉 Deployment completed!"
EOF

# Hacer ejecutable
chmod +x ~/deploy-portfolio.sh
```

**2. Instalar webhook listener:**

```bash
# Instalar webhook (https://github.com/adnanh/webhook)
sudo apt-get install webhook

# Crear configuración
cat > ~/hooks.json << 'EOF'
[
  {
    "id": "deploy-portfolio",
    "execute-command": "/home/ubuntu/deploy-portfolio.sh",
    "command-working-directory": "/home/ubuntu/Portafolio-Manager",
    "response-message": "Deployment started",
    "trigger-rule": {
      "match": {
        "type": "payload-hash-sha256",
        "secret": "YOUR_WEBHOOK_SECRET_HERE",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature-256"
        }
      }
    }
  }
]
EOF

# Iniciar webhook listener
webhook -hooks hooks.json -verbose -port 9000
```

**3. Configurar en GitHub:**

Ve a: **Repository → Settings → Webhooks → Add webhook**

- **Payload URL:** `http://YOUR_SERVER_IP:9000/hooks/deploy-portfolio`
- **Content type:** `application/json`
- **Secret:** (el mismo que pusiste en hooks.json)
- **Events:** Solo `Releases`

---

## 📊 Comparación de Opciones

### Para Staging/Desarrollo:
**Recomendado: Watchtower**
- Simple
- Automático
- Siempre en la última versión

### Para Producción:
**Recomendado: GitHub Actions**
- Control total
- Aprobación manual
- Rollback automático
- Versiones específicas

---

## 🔄 Flujo de Deployment Completo

### Con GitHub Actions (Recomendado)

```mermaid
graph LR
    A[Merge PR a main] --> B[CI tests pasan]
    B --> C[Crear release v1.2.0]
    C --> D[Build multi-arch image]
    D --> E[Push a GHCR]
    E --> F[Manual: Run Deploy Workflow]
    F --> G[Backup DB]
    G --> H[Pull nueva imagen]
    H --> I[Update containers]
    I --> J[Verify deployment]
    J --> K{Éxito?}
    K -->|Sí| L[✅ Deployment completo]
    K -->|No| M[⚠️ Rollback automático]
```

### Con Watchtower

```mermaid
graph LR
    A[Merge PR a main] --> B[CI tests pasan]
    B --> C[Crear release]
    C --> D[Build multi-arch image]
    D --> E[Push a GHCR]
    E --> F[Watchtower detecta cambio]
    F --> G[Pull nueva imagen]
    G --> H[Update containers automático]
    H --> I[✅ Deployment completo]
```

---

## 🛠️ Comandos Útiles

### Verificar deployment

```bash
# Ver versión actual corriendo
docker inspect portafolio-manager-web-1 | grep -i image

# Ver logs de Watchtower
docker logs watchtower --tail=50 -f

# Verificar que el sitio funciona
curl -I https://henfrydls.com/
```

### Rollback manual

```bash
# Cambiar a versión anterior en docker-compose.yml
sed -i 's|:v1.2.0|:v1.1.4|' docker-compose.yml

# Actualizar
docker compose pull web
docker compose up -d web
```

### Pausar Watchtower temporalmente

```bash
# Detener Watchtower (no actualizará)
docker stop watchtower

# Reiniciar después
docker start watchtower
```

---

## 🔐 Seguridad

### GitHub Actions
- ✅ SSH keys solo para deployment (sin acceso root)
- ✅ Secrets encriptados en GitHub
- ✅ Logs auditables

### Watchtower
- ✅ Solo monitorea GHCR (no ejecuta código arbitrario)
- ✅ Corre con privilegios mínimos
- ⚠️ Recomienda usar solo en staging con `:latest`

---

## 📝 Checklist Pre-Deployment

- [ ] Backup de base de datos (automático con GitHub Actions)
- [ ] Tests pasando en CI/CD
- [ ] Release notes revisadas
- [ ] No hay breaking changes
- [ ] Variables de entorno actualizadas (si necesario)
- [ ] Notificar al equipo (si aplicable)

---

## 🆘 Troubleshooting

### GitHub Actions: "Permission denied (publickey)"

```bash
# Verificar que la SSH key está en GitHub Secrets correctamente
# Verificar que authorized_keys tiene la clave pública

# En el servidor:
tail -1 ~/.ssh/authorized_keys

# Debe coincidir con:
ssh-keygen -y -f ~/.ssh/github_actions_deploy
```

### Watchtower: "No updates found"

```bash
# Verificar que el tag es 'latest'
docker compose config | grep image

# Verificar logs de Watchtower
docker logs watchtower --tail=100

# Forzar chequeo inmediato
docker restart watchtower
```

### Deployment falla en verificación

```bash
# Ver logs del contenedor
docker compose logs web --tail=100

# Verificar que todas las dependencias están corriendo
docker compose ps

# Verificar conectividad a DB
docker compose exec web python manage.py check
```

---

**Última actualización:** 2026-01-18
**Versión del documento:** 1.0.0
