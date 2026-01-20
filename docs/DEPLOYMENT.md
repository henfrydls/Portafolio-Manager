# Deployment Guide

Guia para desplegar en produccion usando imagenes Docker de GHCR.

## Resumen Rapido

```bash
# Pull imagen
docker pull ghcr.io/henfrydls/portafolio-manager:latest

# O version especifica (recomendado para produccion)
docker pull ghcr.io/henfrydls/portafolio-manager:v1.2.0
```

---

## Imagenes Docker

**Registry:** `ghcr.io/henfrydls/portafolio-manager`

| Tag | Uso |
|-----|-----|
| `latest` | Desarrollo/Testing |
| `v1.2.0` | Produccion (recomendado) |

**Arquitecturas:** AMD64 (Intel/AMD), ARM64 (Mac M1/M2, AWS Graviton)

---

## Opciones de Deployment

### Opcion 1: Watchtower (Auto-update)

Para staging/desarrollo. Actualiza automaticamente cuando detecta nueva imagen.

```yaml
# docker-compose.yml
services:
  web:
    image: ghcr.io/henfrydls/portafolio-manager:latest
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 3600 --cleanup
```

### Opcion 2: GitHub Actions (Produccion)

Control total con backup y rollback automatico.

**Setup:**

1. Generar SSH key en servidor:
   ```bash
   ssh-keygen -t ed25519 -C "deploy" -f ~/.ssh/deploy
   cat ~/.ssh/deploy.pub >> ~/.ssh/authorized_keys
   ```

2. Agregar secrets en GitHub (Settings > Secrets):
   - `PRODUCTION_SSH_KEY`: contenido de `~/.ssh/deploy`
   - `PRODUCTION_HOST`: IP del servidor
   - `PRODUCTION_USER`: usuario SSH

3. Ejecutar: Actions > Deploy to Production > Run workflow

### Opcion 3: Manual

```bash
# En el servidor
cd ~/portfolio
docker compose pull web
docker compose up -d web
```

---

## Deployment en AWS EC2

```bash
# 1. Conectar
ssh -i key.pem ubuntu@ec2-xx-xx-xx-xx.amazonaws.com

# 2. Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# 3. Crear directorio
mkdir -p /opt/portfolio && cd /opt/portfolio

# 4. Crear .env y docker-compose.yml

# 5. Iniciar
docker compose up -d
```

---

## Comandos Utiles

```bash
# Ver version actual
docker inspect portfolio-web | grep Image

# Rollback
docker compose down
# Editar docker-compose.yml para version anterior
docker compose up -d

# Logs
docker compose logs -f web

# Backup DB antes de actualizar
docker compose exec db pg_dump -U portfolio -d portfolio > backup.sql
```

---

## Checklist Pre-Deployment

- [ ] Backup de base de datos
- [ ] Tests pasando en CI
- [ ] Variables de entorno actualizadas
- [ ] Release notes revisadas

---

## Troubleshooting

**"Cannot pull image"**
```bash
docker logout ghcr.io
docker pull ghcr.io/henfrydls/portafolio-manager:latest
```

**Contenedor se reinicia**
```bash
docker logs portfolio-web
# Verificar: .env completo, DB accesible, puerto disponible
```
