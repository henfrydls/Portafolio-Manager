from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    """Convert markdown text to HTML"""
    if not text:
        return ''

    # Configure markdown with extensions for better formatting
    md = markdown.Markdown(extensions=[
        'codehilite',  # Syntax highlighting for code blocks
        'fenced_code',  # Support for fenced code blocks (```)
        'tables',  # Support for tables
        'toc',     # Table of contents
        'nl2br',   # Convert newlines to <br> tags
    ], extension_configs={
        'codehilite': {
            'css_class': 'highlight',
            'use_pygments': False,  # Use CSS instead of inline styles
        }
    })

    html = md.convert(text)
    return mark_safe(html)