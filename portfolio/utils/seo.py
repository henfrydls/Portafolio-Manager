"""
SEO utilities for portfolio application.
Provides meta tags, Open Graph, and structured data generation.
"""

from django.conf import settings
from django.urls import reverse, translate_url
from django.utils.html import strip_tags
from django.utils.translation import gettext as _, gettext_lazy
import json
import re

class SEOGenerator:
    """
    Utility class for generating SEO meta tags and structured data.
    """
    
    # Default SEO settings
    # Lazy: these are evaluated per request, in the visitor's language
    DEFAULT_TITLE = gettext_lazy("Portfolio - Full Stack Developer")
    DEFAULT_DESCRIPTION = gettext_lazy(
        "Professional web development portfolio: projects and experience with modern technologies."
    )
    DEFAULT_KEYWORDS = gettext_lazy("developer, full stack, web development, portfolio, projects, technology")
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
            description = cls._truncate(cls._clean_text(profile.bio)) if profile.bio else str(cls.DEFAULT_DESCRIPTION)
            author = profile.name
            image_url = cls._get_image_url(profile.profile_image, request)
        else:
            title = str(cls.DEFAULT_TITLE)
            description = str(cls.DEFAULT_DESCRIPTION)
            author = cls.DEFAULT_AUTHOR
            image_url = base_context['default_image']

        canonical_url = f"{base_context['base_url']}{reverse('portfolio:home')}"

        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': str(cls.DEFAULT_KEYWORDS),
            'author': author,
            'og_type': 'website',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            **cls._page_links(canonical_url),
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
        
        # Plain title: this is what link previews show
        title = project.title
        description = cls._truncate(cls._clean_text(project.description))
        keywords = f"{_('project')}, {project.title}, " + ", ".join([
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
            'og_type': 'article',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            **cls._page_links(canonical_url),
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
        
        # Plain title: this is what link previews show
        title = post.title
        description = post.excerpt or cls._truncate(cls._clean_text(post.content))
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
            'og_type': 'article',
            'og_title': title,
            'og_description': description,
            'og_image': image_url,
            **cls._page_links(canonical_url),
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
            description = _("Posts about %(category)s.") % {'category': category.name.lower()}
            description += " " + (category.description or _("Specialized, up-to-date content."))
            canonical_url = f"{base_context['base_url']}{reverse('portfolio:post-list')}?category={category.slug}"
        else:
            title = "Blog"
            description = _("Posts about web development, technology and projects. Updated regularly.")
            canonical_url = f"{base_context['base_url']}{reverse('portfolio:post-list')}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': _("blog, posts, web development, technology, news"),
            'og_type': 'website',
            'og_title': title,
            'og_description': description,
            'og_image': base_context['default_image'],
            **cls._page_links(canonical_url),
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
            title = _("Resume - %(name)s") % {'name': profile.name}
            description = _(
                "Professional resume of %(name)s. %(title)s. Experience, education and skills."
            ) % {'name': profile.name, 'title': profile.title}
            author = profile.name
        else:
            title = _("Professional resume")
            description = _("Professional resume with experience, education and technical skills.")
            author = cls.DEFAULT_AUTHOR
        
        canonical_url = f"{base_context['base_url']}{reverse('portfolio:resume')}"
        
        return {
            **base_context,
            'title': title,
            'description': description,
            'keywords': _("cv, resume, experience, education, skills, professional"),
            'author': author,
            'og_type': 'profile',
            'og_title': title,
            'og_description': description,
            'og_image': base_context['default_image'],
            **cls._page_links(canonical_url),
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
            # No email or phone: this markup is public and harvested by
            # scrapers. Visitors reach the owner through the contact form.
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
            "description": str(cls.DEFAULT_DESCRIPTION),
        }

    @staticmethod
    def to_json_ld(data):
        """
        Serialize structured data for a <script type="application/ld+json">.

        The text ends up inside a script element, where a "</script>" in a
        bio would close it. Escape the same characters Django's json_script
        does; they stay valid JSON.
        """
        if not data:
            return ''
        text = json.dumps(data, ensure_ascii=False)
        return (text.replace('<', '\\u003C')
                    .replace('>', '\\u003E')
                    .replace('&', '\\u0026'))
    
    @classmethod
    def _page_links(cls, canonical_url):
        """
        The URLs that identify a page to search engines.

        Every language version is its own canonical and lists all versions,
        itself included, as alternates. `x-default` is the default-language
        version, which is the one served without a language prefix.
        """
        alternates = [
            {'hreflang': code, 'href': translate_url(canonical_url, code)}
            for code, _name in settings.LANGUAGES
        ]
        alternates.append({
            'hreflang': 'x-default',
            'href': translate_url(canonical_url, settings.LANGUAGE_CODE),
        })
        return {
            'canonical_url': canonical_url,
            'og_url': canonical_url,
            'hreflang_alternates': alternates,
        }

    @classmethod
    def _truncate(cls, text, limit=160):
        """Shorten text to `limit` characters without cutting a word in half."""
        if len(text) <= limit:
            return text
        cut = text[:limit - 1]
        # Only back up to a space if the cut landed inside a word
        if not text[limit - 1].isspace() and ' ' in cut:
            cut = cut[:cut.rindex(' ')]
        return cut.rstrip(' ,;:.-') + '…'

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


