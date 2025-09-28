# portfolio/templatetags/markdown_extras.py
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import html
import markdown as md

register = template.Library()

# Extensiones combinadas
_EXTENSIONS = [
    "extra",        # tablas, notas al pie, etc.
    "fenced_code",  # bloques de código con ```
    "tables",       # soporte explícito de tablas
    "toc",          # tabla de contenidos (anclas)
    "nl2br",        # saltos de línea -> <br>
    "codehilite",   # resaltado de código (envoltura/clases)
]

# Configuración combinada
_EXTENSION_CONFIGS = {
    "codehilite": {
        "css_class": "highlight",
        "linenums": False,
        # Mantengo False porque así lo tenías; si quieres colores reales,
        # cambia a True e incluye CSS de Pygments (noclasses=False).
        "use_pygments": False,
    },
    # Opcionalmente, puedes configurar 'toc' (permalink a títulos):
    # "toc": {"permalink": True},
}

@register.filter(name="markdown")
@stringfilter
def markdown_filter(value: str) -> str:
    """
    Convierte Markdown a HTML con extensiones útiles (extra, toc, tablas, etc.)
    """
    if not value:
        return ""

    # Unescape HTML entities that Django may have escaped
    unescaped_value = html.unescape(value)

    result = md.markdown(
        unescaped_value,
        extensions=_EXTENSIONS,
        extension_configs=_EXTENSION_CONFIGS,
        output_format="html5",
    )
    return mark_safe(result)
