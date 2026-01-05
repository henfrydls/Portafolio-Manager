"""
Tests for public views (non-admin).
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone, translation
from django.contrib.auth import get_user_model
from django.db import connection, transaction

from portfolio.models import (
    Profile, Project, ProjectType, BlogPost, Category,
    KnowledgeBase, Contact, SiteConfiguration
)

User = get_user_model()


def create_test_profile(profile_id=1, name="Test User", title="Test Developer", bio="Test bio",
                       email="test@example.com", location="Test City", language="en"):
    """Helper function to create a test profile using raw SQL (handles legacy columns)."""
    with transaction.atomic():
        cursor = connection.cursor()
        # Insert into main table with legacy columns
        cursor.execute(
            "INSERT INTO portfolio_profile (id, email, phone, linkedin_url, github_url, medium_url, "
            "profile_image, resume_pdf, resume_pdf_es, show_web_resume, created_at, updated_at, "
            "name, title, bio, location) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s)",
            [profile_id, email, '', '', '', '', '', '', '', True, name, title, bio, location]
        )

        # Create translations
        cursor.execute(
            "INSERT INTO portfolio_profile_translation (master_id, language_code, name, title, bio, location) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            [profile_id, language, name, title, bio, location]
        )

        return Profile.objects.get(pk=profile_id)


class HomeViewTest(TestCase):
    """Test HomeView"""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')

        # Create superuser to bypass setup redirect middleware
        User = get_user_model()
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )

        # Create project type
        self.project_type = ProjectType.objects.create(slug='web-app')
        self.project_type.set_current_language('en')
        self.project_type.name = "Web Application"
        self.project_type.description = "Web apps"
        self.project_type.save()

    def test_home_view_loads(self):
        """Test that home view loads successfully"""
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio/home.html')

    def test_home_view_has_profile(self):
        """Test that home view includes profile in context"""
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        self.assertEqual(response.context['profile'].email, 'test@example.com')

    def test_home_view_has_contact_form(self):
        """Test that home view includes contact form"""
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('contact_form', response.context)

    def test_home_view_contact_form_submission(self):
        """Test contact form submission on home page"""
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Test message',
            'honeypot': '',  # Honeypot field should be empty
        }
        response = self.client.post(reverse('portfolio:home'), data)

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Contact should be created
        self.assertEqual(Contact.objects.count(), 1)
        contact = Contact.objects.first()
        self.assertEqual(contact.name, 'John Doe')
        self.assertEqual(contact.email, 'john@example.com')

    def test_home_view_honeypot_protection(self):
        """Test that honeypot field blocks spam"""
        data = {
            'name': 'Spammer',
            'email': 'spam@example.com',
            'subject': 'Spam',
            'message': 'Spam message',
            'honeypot': 'http://spam.com',  # Honeypot filled = spam
        }
        response = self.client.post(reverse('portfolio:home'), data)

        # Should redirect (appears to succeed)
        self.assertEqual(response.status_code, 302)

        # But no contact should be created
        self.assertEqual(Contact.objects.count(), 0)

    def test_home_view_has_projects_context(self):
        """Test that home view has projects pagination"""
        response = self.client.get(reverse('portfolio:home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)
        self.assertIn('projects_paginator', response.context)


class BlogListViewTest(TestCase):
    """Test BlogListView"""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')

        # Create superuser to bypass setup redirect middleware
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )

        # Create category
        self.category = Category.objects.create(slug='tech')
        self.category.set_current_language('en')
        self.category.name = "Technology"
        self.category.description = "Tech posts"
        self.category.save()

        # Create published post
        self.post = BlogPost()
        self.post.set_current_language('en')
        self.post.title = "Test Post"
        self.post.content = "Test content"
        self.post.excerpt = "Test excerpt"
        self.post.category = self.category
        self.post.status = 'published'
        self.post.publish_date = timezone.now()
        self.post.save()

    def test_blog_list_view_loads(self):
        """Test that blog list view loads successfully"""
        response = self.client.get(reverse('portfolio:post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio/blog_list.html')

    def test_blog_list_view_shows_published_posts(self):
        """Test that only published posts are shown"""
        response = self.client.get(reverse('portfolio:post-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        self.assertEqual(len(response.context['posts']), 1)

    def test_blog_list_view_hides_draft_posts(self):
        """Test that draft posts are not shown"""
        # Create draft post
        draft = BlogPost()
        draft.set_current_language('en')
        draft.title = "Draft Post"
        draft.content = "Draft content"
        draft.excerpt = "Draft excerpt"
        draft.category = self.category
        draft.status = 'draft'
        draft.publish_date = timezone.now()  # Required even for drafts
        draft.save()

        response = self.client.get(reverse('portfolio:post-list'))
        self.assertEqual(response.status_code, 200)
        # Should only show the published post
        self.assertEqual(len(response.context['posts']), 1)
        self.assertEqual(response.context['posts'][0].title, "Test Post")

    def test_blog_list_view_filter_by_category(self):
        """Test filtering posts by category"""
        response = self.client.get(reverse('portfolio:post-list') + '?category=tech')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), 1)


class BlogDetailViewTest(TestCase):
    """Test BlogDetailView"""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')

        # Create superuser to bypass setup redirect middleware
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )

        # Create category
        self.category = Category.objects.create(slug='tech')
        self.category.set_current_language('en')
        self.category.name = "Technology"
        self.category.description = "Tech posts"
        self.category.save()

        # Create published post
        self.post = BlogPost()
        self.post.set_current_language('en')
        self.post.title = "Test Post"
        self.post.content = "Test content with enough words to have a reading time."
        self.post.excerpt = "Test excerpt"
        self.post.category = self.category
        self.post.status = 'published'
        self.post.publish_date = timezone.now()
        self.post.save()

    def test_blog_detail_view_loads(self):
        """Test that blog detail view loads successfully"""
        response = self.client.get(
            reverse('portfolio:post-detail', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio/blog_detail.html')

    def test_blog_detail_view_shows_post_content(self):
        """Test that post content is displayed"""
        response = self.client.get(
            reverse('portfolio:post-detail', kwargs={'slug': self.post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Post")
        self.assertContains(response, "Test content")

    def test_blog_detail_view_404_for_draft(self):
        """Test that draft posts return 404"""
        draft = BlogPost()
        draft.set_current_language('en')
        draft.title = "Draft Post"
        draft.content = "Draft content"
        draft.excerpt = "Draft excerpt"
        draft.category = self.category
        draft.status = 'draft'
        draft.publish_date = timezone.now()  # Required even for drafts
        draft.save()

        response = self.client.get(
            reverse('portfolio:post-detail', kwargs={'slug': draft.slug})
        )
        self.assertEqual(response.status_code, 404)


# Note: ProjectListView does not exist as a public view
# Projects are displayed on the home page instead


class ProjectDetailViewTest(TestCase):
    """Test ProjectDetailView"""

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        translation.activate('en')

        # Create superuser to bypass setup redirect middleware
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )

        # Create project type
        self.project_type = ProjectType.objects.create(slug='web-app')
        self.project_type.set_current_language('en')
        self.project_type.name = "Web Application"
        self.project_type.description = "Web apps"
        self.project_type.save()

        # Create public project
        self.project = Project()
        self.project.set_current_language('en')
        self.project.title = "Test Project"
        self.project.description = "Detailed project description"
        self.project.project_type_obj = self.project_type
        self.project.visibility = 'public'
        self.project.save()

    def test_project_detail_view_loads(self):
        """Test that project detail view loads successfully"""
        response = self.client.get(
            reverse('portfolio:project-detail', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'portfolio/project_detail.html')

    def test_project_detail_view_shows_content(self):
        """Test that project content is displayed"""
        response = self.client.get(
            reverse('portfolio:project-detail', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Project")
        self.assertContains(response, "Detailed project description")

    def test_project_detail_view_404_for_private(self):
        """Test that private projects return 404"""
        private = Project()
        private.set_current_language('en')
        private.title = "Private Project"
        private.description = "Private description"
        private.project_type_obj = self.project_type
        private.visibility = 'private'
        private.save()

        response = self.client.get(
            reverse('portfolio:project-detail', kwargs={'slug': private.slug})
        )
        self.assertEqual(response.status_code, 404)


class RobotsAndSEOViewsTest(TestCase):
    """Test robots.txt and other SEO views"""

    def setUp(self):
        self.client = Client()

        # Create superuser to bypass setup redirect middleware
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )

    def test_robots_txt_view(self):
        """Test robots.txt view"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'User-agent')
        self.assertContains(response, 'Sitemap')

    def test_manifest_json_view(self):
        """Test manifest.json view"""
        response = self.client.get('/manifest.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
