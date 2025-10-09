"""
Database query optimization utilities for portfolio application.
Provides optimized querysets with select_related and prefetch_related.
"""

from django.db.models import Prefetch, Q, Count
import logging

logger = logging.getLogger('portfolio')


class QueryOptimizer:
    """
    Utility class for optimizing database queries in the portfolio application.
    Focuses on reducing N+1 queries through proper use of select_related and prefetch_related.
    """
    
    @classmethod
    def get_optimized_profile(cls):
        """
        Get profile with optimized query.
        
        Returns:
            Profile: Profile instance or None
        """
        from .models import Profile
        try:
            return Profile.objects.first()
        except Profile.DoesNotExist:
            return None
    
    @classmethod
    def get_optimized_projects(cls, visibility='public', featured_only=False, limit=None):
        """
        Get projects with optimized queries (select_related, prefetch_related).
        
        Args:
            visibility: 'public', 'private', or 'all'
            featured_only: Only return featured projects
            limit: Maximum number of projects to return
            
        Returns:
            QuerySet: Optimized projects queryset
        """
        from .models import Project
        
        # Build base queryset with optimizations to avoid N+1 queries
        queryset = Project.objects.select_related('project_type_obj').prefetch_related(
            'technologies'
        )
        
        # Apply filters
        if visibility != 'all':
            queryset = queryset.filter(visibility=visibility)
        
        if featured_only:
            queryset = queryset.filter(featured=True)
        
        # Order and limit
        queryset = queryset.order_by('order', '-created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @classmethod
    def get_optimized_blog_posts(cls, status='published', featured_only=False, 
                                category_slug=None, limit=None):
        """
        Get blog posts with optimized queries (select_related).
        
        Args:
            status: 'published', 'draft', or 'all'
            featured_only: Only return featured posts
            category_slug: Filter by category slug
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet: Optimized blog posts queryset
        """
        from .models import BlogPost
        
        # Build base queryset with optimizations to avoid N+1 queries
        queryset = BlogPost.objects.select_related('category')
        
        # Apply filters
        if status != 'all':
            queryset = queryset.filter(status=status)
        
        if featured_only:
            queryset = queryset.filter(featured=True)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Order and limit
        queryset = queryset.order_by('-publish_date')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @classmethod
    def get_optimized_technologies(cls):
        """
        Get all technologies ordered by name.
        
        Returns:
            QuerySet: Technologies queryset
        """
        from .models import Technology
        return Technology.objects.all().order_by('name')
    
    @classmethod
    def get_optimized_categories(cls, active_only=True):
        """
        Get categories ordered by order and name.
        
        Args:
            active_only: Only return active categories
            
        Returns:
            QuerySet: Categories queryset
        """
        from .models import Category
        queryset = Category.objects.all()
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('order', 'name')
    
    @classmethod
    def get_featured_items_optimized(cls, limit=4):
        """
        Get mixed featured items (projects and posts) with optimized queries.
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            list: Mixed list of featured projects and posts
        """
        # Get featured projects with optimized query
        featured_projects = cls.get_optimized_projects(
            visibility='public', 
            featured_only=True
        )
        
        # Get featured posts with optimized query
        featured_posts = cls.get_optimized_blog_posts(
            status='published', 
            featured_only=True
        )
        
        # Combine and prepare items
        featured_items = []
        
        # Add projects
        for project in featured_projects:
            featured_url = project.get_featured_link_url()
            is_external = project.featured_link_type in ['github', 'demo', 'pdf', 'custom']
            
            featured_items.append({
                'type': 'project',
                'object': project,
                'title': project.title,
                'description': project.description,
                'image': project.image,
                'url': project.get_absolute_url() if hasattr(project, 'get_absolute_url') else None,
                'external_url': featured_url if is_external else None,
                'featured_url': featured_url,
                'featured_link_type': project.featured_link_type,
                'featured_icon': project.get_featured_link_icon(),
                'has_featured_link': project.has_featured_link(),
                'date': project.created_at,
                'order': project.order,
                'technologies': list(project.technologies.all()[:3]),
                'is_external': is_external
            })
        
        # Add posts
        for post in featured_posts:
            featured_items.append({
                'type': 'post',
                'object': post,
                'title': post.title,
                'description': post.excerpt or post.content[:200],
                'image': post.featured_image,
                'url': post.get_absolute_url(),
                'external_url': None,
                'date': post.publish_date,
                'order': 999,  # Posts go after projects by default
                'category': post.category,
                'reading_time': post.reading_time,
                'is_external': False
            })
        
        # Sort by order first, then by date (most recent first)
        featured_items.sort(key=lambda x: (x['order'], -x['date'].timestamp()))
        
        # Limit results
        return featured_items[:limit]
