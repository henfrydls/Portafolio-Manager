"""
SEO utilities for portfolio application.
Provides meta tags, Open Graph, and structured data generation.
"""

from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
import re

class SEOGenerator:
    """
    Utility class for generating SEO meta tags and structured data.
    """
    
    # Default SEO settings
    DEFAULT_TITLE = "Portfolio - Desarrollador Full Stack"
    DEFAULT_DESCRIPTION = "Portfolio profesional de desarrollo web, proyectos innovadores y experiencia en tecnolog?as modernas."
    DEFAULT_KEYWORDS = "desarrollador, full stack, web development, portfolio, proyectos, tecnolog?a"
    DEFAULT_AUTHOR = "Portfolio Developer"
    
    @classmethod
    def get_base_context(cls, request=None):
        """
        Get base SEO context that applies to all pages.
        
        Args:
            request: Django request object
            
        Returns:
            dict: Base SEO context
        """
        base_url = cls._get_base_url(request)
        
        return {
            'site_name': getattr(settings, 'SITE_NAME', 'Portfolio'),
            'base_url': base_url,
            'default_image': f"{base_url}/static/images/default-og-image.jpg",
        }
    
    @classmethod
    def generate_home_seo(cls, profile, request=None):
        """
        Generate SEO data for home page.
        
        Args:
            profile: Profile model instance
            request: Django request object
            
        Returns:
            dict: SEO context for home page
        """
        base_context = cls.get_base_context(request)
        
        if profile:
            title = f"{profile.name} - {profile.title}"
            description = cls._clean_text(profile.bio)[:160] if profile.bio else cls.DEFAULT_DESCRIPTION
            author = profile.name
            image_url = cls._get_image_url(profile.profile_image, request)
        else:
            title = cls.DEFAULT_TITLE
            description = cls.DEFAULT_DESCRIPTION
            author = cls.DEFAULT_AUTHOR
            image_url = base_context['default_image']
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': cls.DEFAULT_KEYWORDS,
            'author': author,
            'canonical_url': base_context['base_url'],
            'og_type': 'website',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            'og_url': base_context['base_url'],
        }
    
    @classmethod
    def generate_project_seo(cls, project, request=None):
        """
        Generate SEO data for project detail page.
        
        Args:
            project: Project model instance
            request: Django request object
            
        Returns:
            dict: SEO context for project page
        """
        base_context = cls.get_base_context(request)
        
        title = f"{project.title} - Proyecto"
        description = cls._clean_text(project.description)[:160]
        keywords = f"proyecto, {project.title}, " + ", ".join([
            tech.safe_translation_getter('name', any_language=True) or tech.identifier
            for tech in project.knowledge_bases.all()[:5]
        ])
        image_url = cls._get_image_url(project.image, request)
        canonical_url = f"{base_context['base_url']}{project.get_absolute_url()}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': keywords,
            'canonical_url': canonical_url,
            'og_type': 'article',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            'og_url': canonical_url,
            'article_author': project.github_owner or base_context.get('site_name'),
            'article_published_time': project.created_at.isoformat(),
            'article_modified_time': project.updated_at.isoformat(),
        }
    
    @classmethod
    def generate_blog_post_seo(cls, post, request=None):
        """
        Generate SEO data for blog post detail page.
        
        Args:
            post: BlogPost model instance
            request: Django request object
            
        Returns:
            dict: SEO context for blog post page
        """
        base_context = cls.get_base_context(request)
        
        title = f"{post.title} - Blog"
        description = post.excerpt or cls._clean_text(post.content)[:160]
        keywords = f"blog, {post.title}"
        if post.tags:
            keywords += f", {post.tags}"
        
        image_url = cls._get_image_url(post.featured_image, request)
        canonical_url = f"{base_context['base_url']}{post.get_absolute_url()}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': keywords,
            'canonical_url': canonical_url,
            'og_type': 'article',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            'og_url': canonical_url,
            'article_author': base_context.get('site_name'),
            'article_published_time': post.publish_date.isoformat(),
            'article_modified_time': post.updated_at.isoformat(),
            'article_section': post.category.name if post.category else 'Blog',
            'article_tag': post.get_tags_list(),
        }
    
    @classmethod
    def generate_blog_list_seo(cls, request=None, category=None):
        """
        Generate SEO data for blog list page.
        
        Args:
            request: Django request object
            category: Category filter if any
            
        Returns:
            dict: SEO context for blog list page
        """
        base_context = cls.get_base_context(request)
        
        if category:
            title = f"Blog - {category.name}"
            description = f"Art?culos sobre {category.name.lower()}. {category.description or 'Contenido especializado y actualizado.'}"
            canonical_url = f"{base_context['base_url']}{reverse('portfolio:post-list')}?category={category.slug}"
        else:
            title = "Blog - Art?culos y Noticias"
            description = "Art?culos sobre desarrollo web, tecnolog?a y proyectos. Contenido actualizado regularmente."
            canonical_url = f"{base_context['base_url']}{reverse('portfolio:post-list')}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': "blog, art?culos, desarrollo web, tecnolog?a, noticias",
            'canonical_url': canonical_url,
            'og_type': 'website',
            'og_title': title,
            'og_description': description,
            'og_image': base_context['default_image'],
            'og_url': canonical_url,
        }
    
    @classmethod
    def generate_resume_seo(cls, profile, request=None):
        """
        Generate SEO data for resume page.
        
        Args:
            profile: Profile model instance
            request: Django request object
            
        Returns:
            dict: SEO context for resume page
        """
        base_context = cls.get_base_context(request)
        
        if profile:
            title = f"CV - {profile.name}"
            description = f"Curr?culum profesional de {profile.name}. {profile.title}. Experiencia, educaci?n y habilidades."
            author = profile.name
        else:
            title = "CV - Curr?culum Profesional"
            description = "Curr?culum profesional con experiencia, educaci?n y habilidades t?cnicas."
            author = cls.DEFAULT_AUTHOR
        
        canonical_url = f"{base_context['base_url']}{reverse('portfolio:resume')}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': "cv, curr?culum, experiencia, educaci?n, habilidades, profesional",
            'author': author,
            'canonical_url': canonical_url,
            'og_type': 'profile',
            'og_title': title,
            'og_description': description,
            'og_image': base_context['default_image'],
            'og_url': canonical_url,
        }
    
    @classmethod
    def generate_structured_data_person(cls, profile, request=None):
        """
        Generate JSON-LD structured data for person/profile.
        
        Args:
            profile: Profile model instance
            request: Django request object
            
        Returns:
            dict: JSON-LD structured data
        """
        if not profile:
            return {}
        
        base_url = cls._get_base_url(request)
        
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": profile.name,
            "jobTitle": profile.title,
            "description": cls._clean_text(profile.bio) if profile.bio else None,
            "url": base_url,
            "email": profile.email,
            "telephone": profile.phone if profile.phone else None,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": profile.location
            } if profile.location else None,
            "sameAs": []
        }
        
        # Add social media profiles
        if profile.linkedin_url:
            structured_data["sameAs"].append(profile.linkedin_url)
        if profile.github_url:
            structured_data["sameAs"].append(profile.github_url)
        if profile.medium_url:
            structured_data["sameAs"].append(profile.medium_url)
        
        # Add profile image
        if profile.profile_image:
            structured_data["image"] = cls._get_image_url(profile.profile_image, request)
        
        # Clean up None values
        return {k: v for k, v in structured_data.items() if v is not None}
    
    @classmethod
    def generate_structured_data_website(cls, request=None):
        """
        Generate JSON-LD structured data for website.
        
        Args:
            request: Django request object
            
        Returns:
            dict: JSON-LD structured data
        """
        base_url = cls._get_base_url(request)
        
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": getattr(settings, 'SITE_NAME', 'Portfolio'),
            "url": base_url,
            "description": cls.DEFAULT_DESCRIPTION,
            "potentialAction": {
                "@type": "SearchAction",
                "target": f"{base_url}/search?q={{search_term_string}}",
                "query-input": "required name=search_term_string"
            }
        }
    
    @classmethod
    def _get_base_url(cls, request):
        """Get base URL from request or settings."""
        if request:
            return f"{request.scheme}://{request.get_host()}"
        return getattr(settings, 'BASE_URL', 'http://localhost:8000')
    
    @classmethod
    def _get_image_url(cls, image_field, request):
        """Get full URL for image field."""
        if not image_field:
            return cls.get_base_context(request)['default_image']
        
        base_url = cls._get_base_url(request)
        return f"{base_url}{image_field.url}"
    
    @classmethod
    def _clean_text(cls, text):
        """Clean HTML and extra whitespace from text."""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = strip_tags(text)
        
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text


