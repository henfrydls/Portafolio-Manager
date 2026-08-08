# Bloque de suscripción a la newsletter — Diseño

**Fecha:** 2026-08-08
**Estado:** diseño aprobado, pendiente plan de implementación

## Contexto y objetivo

El lector que termina un post es la persona más interesada que pasa por el sitio, y hoy el único llamado al final del artículo es de contacto. La newsletter "Prueba de concepto" vive en LinkedIn (cadencia mensual). Objetivo: un bloque al final de cada post del blog que invite a suscribirse, con el destino configurable desde el dashboard sin necesidad de deploy.

## Decisiones tomadas

1. **Destino: la newsletter de LinkedIn.** No se integra Kit/ConvertKit (issue #11, queda como upgrade futuro si crece el tráfico directo) ni se construye sistema propio (issue #52, se recomienda cerrar).
2. **Sin modal ni popup.** Bloque inline al final del artículo. Razones: los popups interrumpen la lectura y Google penaliza los interstitials intrusivos en móvil, que es donde llega el tráfico de LinkedIn.
3. **URL configurable, copy en template.** La URL del botón vive en `SiteConfiguration` (editable desde el dashboard); el texto vive en el template con `{% trans %}`. Cuando exista una segunda serie se agregará el override por categoría, no antes.
4. **El bloque reemplaza al CTA de contacto** "Enjoyed this post?" (`post-contact-cta`). El contacto no se pierde: sigue disponible en "Get in touch" de la bio del autor, justo arriba.
5. **URL vacía = bloque oculto.** Ese es el interruptor de apagado; no se agrega ningún booleano extra.

## Cambios concretos

| # | Archivo | Cambio |
|---|---|---|
| 1 | `portfolio/models.py` | Campo `newsletter_url` (`URLField`, `blank=True`, `default=''`) en `SiteConfiguration` + migración. |
| 2 | `portfolio/forms/config.py` | Agregar `newsletter_url` a `SiteConfigurationForm.Meta.fields` con su widget (`URLInput`, clase `form-control`). |
| 3 | `templates/portfolio/admin/site_configuration.html` | Campo nuevo en el formulario del dashboard. |
| 4 | `templates/portfolio/components/subscribe_cta.html` | Componente nuevo: título, descripción y botón. Solo se renderiza si `site_config.newsletter_url` tiene valor. |
| 5 | `templates/portfolio/blog_detail.html` | Quitar el bloque `post-contact-cta` (líneas 213–222) e incluir el componente en su lugar. El componente reutiliza las clases CSS existentes (`post-contact-cta`, `cta-content`, `cta-title`, `cta-text`, `cta-button`), sin CSS nuevo. |

`site_config` ya está disponible en todos los templates vía el context processor (`portfolio/context_processors.py`), no hace falta tocar vistas.

## Copy

| | ES | EN |
|---|---|---|
| Título | Prueba de concepto | Prueba de concepto (nombre de marca, no se traduce) |
| Texto | Ideas puestas a prueba dentro de una empresa real. Una entrega al mes. | Ideas tested inside a real company. One issue a month. |
| Botón | Suscribirse en LinkedIn | Subscribe on LinkedIn |

## Métricas

El botón lleva `data-umami-event="newsletter-subscribe"` para contar clics en Umami. Nota: el script de Umami no está en los templates del repo (se asume inyectado en producción); el atributo es inofensivo si el script no está, pero **al desplegar hay que verificar que el evento registre**.

El enlace usa `target="_blank" rel="noopener"`.

## Manejo de errores

No hay backend nuevo ni llamadas externas, por lo tanto no hay estados de error. Con `newsletter_url` vacía el bloque simplemente no se renderiza.

## Tests

1. Con `newsletter_url` configurada, la página de detalle del post contiene el bloque y el enlace apunta a esa URL.
2. Sin `newsletter_url`, el bloque no aparece en el HTML.
3. `SiteConfigurationForm` guarda `newsletter_url` correctamente.

## Fuera de alcance

- **Bug de i18n del sitio** (la sesión queda en `en`): el copy en español no se verá hasta que se arregle; mientras tanto el bloque sale en inglés como el resto del sitio.
- **Slide-in al ~80% de scroll:** posible fase 2; primero medir los clics del bloque inline con Umami.
- **Overrides por categoría** para series futuras.
- **Integración con Kit** (issue #11).
