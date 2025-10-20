"""
Sitemaps for portfolio application.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone, translation
from .models import Project, BlogPost, Category

class StaticViewSitemap(Sitemap):
    """Sitemap for static views."""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['portfolio:home', 'portfolio:resume', 'portfolio:post-list']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()

class ProjectSitemap(Sitemap):
    """Sitemap for projects."""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return Project.objects.filter(visibility='public').order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts."""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(Sitemap):
    """Sitemap for blog categories."""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        current_language = translation.get_language()
        qs = Category.objects.filter(is_active=True)
        if current_language:
            qs = qs.filter(translations__language_code=current_language)
        return qs.order_by('translations__name')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return f"{reverse('portfolio:post-list')}?category={obj.slug}"

# Sitemap index
sitemaps = {
    'static': StaticViewSitemap,
    'projects': ProjectSitemap,
    'blog': BlogPostSitemap,
    'categories': CategorySitemap,
}
