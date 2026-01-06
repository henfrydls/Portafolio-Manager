# Cómo Usar el Workflow de Release

## ¿Qué hace el workflow de release.yml?

El workflow `release.yml` automatiza la creación de releases en GitHub cuando creas un tag de versión. Realiza las siguientes acciones:

1. **Genera changelog automático** - Extrae commits desde el último release
2. **Crea GitHub Release** - Release formal con notas
3. **Construye Docker images multi-platform** - AMD64 y ARM64
4. **Genera SBOM** - Software Bill of Materials para seguridad
5. **(Opcional) Publica a PyPI** - Si lo configuras

## Dos formas de usar el workflow:

### 1. **Automática** - Crear un tag (Recomendado)

Cuando estés listo para crear un release:

```bash
# 1. Asegúrate de estar en main y todo esté actualizado
git checkout main
git pull origin main

# 2. Crea un tag con versión semántica (v1.0.0, v1.2.3, etc.)
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial production release"

# 3. Push el tag a GitHub
git push origin v1.0.0
```

**Esto automáticamente:**
- ✅ Ejecuta todos los tests
- ✅ Construye Docker images
- ✅ Crea el GitHub Release con changelog
- ✅ Publica las imágenes a GitHub Container Registry

### 2. **Manual** - Desde GitHub Actions UI

Si prefieres hacerlo manualmente desde GitHub:

1. Ve a tu repositorio en GitHub
2. Click en **Actions** tab
3. Selecciona **Release** workflow en la barra lateral
4. Click en **Run workflow**
5. Ingresa la versión (ej: `v1.2.3`)
6. Click **Run workflow**

## Versionamiento Semántico

Usa [Semantic Versioning](https://semver.org/):

- **v1.0.0** - Primera versión de producción
- **v1.0.1** - Bug fix (patch)
- **v1.1.0** - Nueva funcionalidad compatible (minor)
- **v2.0.0** - Cambios incompatibles con versión anterior (major)

## Ejemplo de Flujo Completo

```bash
# Después de completar una serie de features y fixes en develop:

# 1. Merge develop a main
git checkout main
git merge develop
git push origin main

# 2. Espera que pasen todos los CI checks

# 3. Crea y push el tag
git tag -a v1.2.0 -m "Release v1.2.0

- Add user authentication
- Fix email validation bug
- Improve performance by 30%
"
git push origin v1.2.0

# 4. El workflow automáticamente:
#    - Ejecuta tests
#    - Construye Docker images
#    - Crea GitHub Release con changelog
#    - Publica imágenes

# 5. Revisa el release en GitHub:
#    https://github.com/henfrydls/Portafolio-Manager/releases
```

## Ver Releases

Tus releases estarán visibles en:
- `https://github.com/henfrydls/Portafolio-Manager/releases`

## Configuración Opcional

### Para publicar a PyPI (no configurado por defecto):

1. Crea cuenta en PyPI: https://pypi.org/
2. Genera API token
3. Agrega a GitHub Secrets: `PYPI_API_TOKEN`
4. Descomenta la sección PyPI en `release.yml`

## Notas Importantes

- **No borres tags** - Los tags de versión deben ser permanentes
- **No reutilices versiones** - Cada versión debe ser única
- **Prueba antes de tag** - Asegúrate que todo funciona en main
- El workflow NO hace deployment automático a producción (por seguridad)

## Comandos Útiles

```bash
# Ver todos los tags
git tag

# Ver detalles de un tag
git show v1.0.0

# Borrar un tag local (si te equivocaste)
git tag -d v1.0.0

# Borrar un tag remoto (USAR CON CUIDADO)
git push origin --delete v1.0.0
```

## FAQ

**Q: ¿Cuándo debo crear un release?**
A: Cuando tengas un conjunto de cambios estables listos para producción.

**Q: ¿Puedo crear releases desde ramas que no sean main?**
A: Técnicamente sí, pero es mejor práctica hacerlo solo desde main.

**Q: ¿Qué pasa si el workflow falla?**
A: Puedes ver los logs en la pestaña Actions y volver a ejecutarlo después de arreglar el problema.

**Q: ¿Necesito el release.yml ahora mismo?**
A: No es necesario hasta que estés listo para hacer releases formales. Puedes dejarlo configurado para cuando lo necesites.
