"""
Sitemaps for portfolio application.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Project, BlogPost, Category


class BilingualSitemap(Sitemap):
    """
    Lists every page once per language and tells crawlers the entries are
    versions of each other, mirroring the hreflang links in the page head.
    """
    i18n = True
    alternates = True
    x_default = True


class StaticViewSitemap(BilingualSitemap):
    """Sitemap for static views."""
    priority = 0.8
    changefreq = 'weekly'
    
    def items(self):
        return ['portfolio:home', 'portfolio:resume', 'portfolio:post-list']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()

class ProjectSitemap(BilingualSitemap):
    """Sitemap for projects."""
    changefreq = 'monthly'
    priority = 0.7
    
    def items(self):
        return Project.objects.filter(visibility='public').order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class BlogPostSitemap(BilingualSitemap):
    """Sitemap for blog posts."""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()

class CategorySitemap(BilingualSitemap):
    """Sitemap for blog categories."""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        # A category page with no published posts is an empty page
        return (
            Category.objects
            .filter(is_active=True, blogpost__status='published')
            .distinct()
            .order_by('order', 'slug')
        )
    
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
