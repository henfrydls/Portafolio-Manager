"""
Tests for portfolio models.
"""
from datetime import date, timedelta
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from portfolio.models import (
    Profile, SiteConfiguration, Project, ProjectType,
    Experience, Education, Skill, Category, BlogPost,
    Contact, KnowledgeBase, Language
)


def create_test_profile(profile_id=1, name="Test User", title="Test Developer", bio="Test bio",
                       email="test@example.com", location="Test City", language="en"):
    """Helper function to create a test profile using raw SQL (handles legacy columns)."""
    from django.db import connection
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


class ProfileModelTest(TestCase):
    """Test Profile model"""

    def setUp(self):
        self.profile = create_test_profile()

    def test_profile_creation(self):
        """Test profile is created correctly"""
        self.assertEqual(self.profile.email, "test@example.com")
        self.assertEqual(self.profile.name, "Test User")
        self.assertEqual(self.profile.title, "Test Developer")

    def test_profile_singleton(self):
        """Test that only one profile can exist"""
        with self.assertRaises(ValidationError):
            profile2 = Profile()
            profile2.set_current_language('en')
            profile2.name = "Another User"
            profile2.title = "Another Title"
            profile2.bio = "Another bio"
            profile2.email = "another@example.com"
            profile2.location = "Another City"
            profile2.save()

    def test_profile_get_solo(self):
        """Test get_solo class method"""
        # Delete existing profile
        Profile.objects.all().delete()

        # get_solo should create a new profile
        profile = Profile.get_solo()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.pk, 1)

    def test_profile_str(self):
        """Test string representation"""
        self.assertEqual(str(self.profile), "Test User")


class SiteConfigurationModelTest(TestCase):
    """Test SiteConfiguration model"""

    def test_site_configuration_singleton(self):
        """Test that only one configuration can exist"""
        config1 = SiteConfiguration.get_solo()
        self.assertIsNotNone(config1)

        # Try to create another
        with self.assertRaises(ValidationError):
            config2 = SiteConfiguration()
            config2.save()

    def test_get_solo_sets_defaults(self):
        """Test get_solo sets default values"""
        config = SiteConfiguration.get_solo()
        self.assertIsNotNone(config.translation_provider)
        self.assertIsNotNone(config.translation_api_url)

    def test_get_target_languages(self):
        """Test get_target_languages method"""
        config = SiteConfiguration.get_solo()
        config.default_language = 'en'
        config.save()

        targets = config.get_target_languages()
        self.assertIsInstance(targets, list)
        # Should not include default language
        self.assertNotIn('en', targets)


class ProjectTypeModelTest(TestCase):
    """Test ProjectType model"""

    def setUp(self):
        self.project_type = ProjectType.objects.create(slug='web-app')
        self.project_type.set_current_language('en')
        self.project_type.name = "Web Application"
        self.project_type.description = "Web app projects"
        self.project_type.save()

    def test_project_type_creation(self):
        """Test project type is created correctly"""
        self.assertEqual(self.project_type.slug, 'web-app')
        self.assertEqual(self.project_type.name, "Web Application")

    def test_project_type_str(self):
        """Test string representation"""
        self.assertEqual(str(self.project_type), "Web Application")

    def test_project_type_auto_slug(self):
        """Test slug is auto-generated from name"""
        pt = ProjectType()
        pt.set_current_language('en')
        pt.name = "Mobile App"
        pt.description = "Mobile projects"
        pt.save()

        self.assertEqual(pt.slug, 'mobile-app')


class KnowledgeBaseModelTest(TestCase):
    """Test KnowledgeBase model"""

    def setUp(self):
        # Use unique identifier to avoid conflicts with default data
        self.kb = KnowledgeBase.objects.create(identifier='test-tech-unique')
        self.kb.set_current_language('en')
        self.kb.name = "Test Technology"
        self.kb.save()

    def test_knowledge_base_creation(self):
        """Test knowledge base is created correctly"""
        self.assertEqual(self.kb.identifier, 'test-tech-unique')
        self.assertEqual(self.kb.name, "Test Technology")

    def test_knowledge_base_str(self):
        """Test string representation"""
        self.assertEqual(str(self.kb), "Test Technology")


class ProjectModelTest(TestCase):
    """Test Project model"""

    def setUp(self):
        self.project_type = ProjectType.objects.create(slug='web-app')
        self.project_type.set_current_language('en')
        self.project_type.name = "Web Application"
        self.project_type.description = "Web app projects"
        self.project_type.save()

        self.project = Project()
        self.project.set_current_language('en')
        self.project.title = "Test Project"
        self.project.description = "A test project"
        self.project.project_type_obj = self.project_type
        self.project.visibility = 'public'
        self.project.save()

    def test_project_creation(self):
        """Test project is created correctly"""
        self.assertEqual(self.project.title, "Test Project")
        self.assertEqual(self.project.visibility, 'public')

    def test_project_slug_auto_generation(self):
        """Test slug is auto-generated from title"""
        self.assertEqual(self.project.slug, 'test-project')

    def test_project_str(self):
        """Test string representation"""
        self.assertEqual(str(self.project), "Test Project")

    def test_project_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.project.get_absolute_url()
        self.assertIn(self.project.slug, url)


class CategoryModelTest(TestCase):
    """Test Category model"""

    def setUp(self):
        self.category = Category.objects.create(slug='tech')
        self.category.set_current_language('en')
        self.category.name = "Technology"
        self.category.description = "Tech posts"
        self.category.save()

    def test_category_creation(self):
        """Test category is created correctly"""
        self.assertEqual(self.category.slug, 'tech')
        self.assertEqual(self.category.name, "Technology")

    def test_category_str(self):
        """Test string representation"""
        self.assertEqual(str(self.category), "Technology")

    def test_category_auto_slug(self):
        """Test slug is auto-generated"""
        cat = Category()
        cat.set_current_language('en')
        cat.name = "Business"
        cat.description = "Business posts"
        cat.save()

        self.assertEqual(cat.slug, 'business')


class BlogPostModelTest(TestCase):
    """Test BlogPost model"""

    def setUp(self):
        self.category = Category.objects.create(slug='tech')
        self.category.set_current_language('en')
        self.category.name = "Technology"
        self.category.description = "Tech posts"
        self.category.save()

        self.post = BlogPost()
        self.post.set_current_language('en')
        self.post.title = "Test Post"
        self.post.content = "This is a test post content."
        self.post.excerpt = "Test excerpt"
        self.post.category = self.category
        self.post.status = 'published'
        self.post.publish_date = timezone.now()
        self.post.save()

    def test_blog_post_creation(self):
        """Test blog post is created correctly"""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.status, 'published')

    def test_blog_post_slug_auto_generation(self):
        """Test slug is auto-generated"""
        self.assertEqual(self.post.slug, 'test-post')

    def test_blog_post_str(self):
        """Test string representation"""
        self.assertEqual(str(self.post), "Test Post")

    def test_blog_post_get_absolute_url(self):
        """Test get_absolute_url method"""
        url = self.post.get_absolute_url()
        self.assertIn(self.post.slug, url)

    def test_blog_post_reading_time(self):
        """Test reading_time property"""
        # Short content should have low reading time
        reading_time = self.post.reading_time
        self.assertGreater(reading_time, 0)

    def test_blog_post_tags(self):
        """Test get_tags_list method"""
        self.post.tags = "python, django, web"
        self.post.save()

        tags = self.post.get_tags_list()
        self.assertEqual(len(tags), 3)
        self.assertIn("python", tags)
        self.assertIn("django", tags)
        self.assertIn("web", tags)


class ExperienceModelTest(TestCase):
    """Test Experience model"""

    def setUp(self):
        self.experience = Experience()
        self.experience.set_current_language('en')
        self.experience.company = "Test Company"
        self.experience.position = "Software Engineer"
        self.experience.description = "Working on projects"
        self.experience.start_date = date(2020, 1, 1)
        self.experience.current = True
        self.experience.save()

    def test_experience_creation(self):
        """Test experience is created correctly"""
        self.assertEqual(self.experience.company, "Test Company")
        self.assertTrue(self.experience.current)

    def test_experience_current_sets_end_date_null(self):
        """Test that current=True sets end_date to None"""
        self.experience.end_date = date(2023, 1, 1)
        self.experience.current = True
        self.experience.save()

        self.assertIsNone(self.experience.end_date)

    def test_experience_str(self):
        """Test string representation"""
        expected = "Software Engineer en Test Company"
        self.assertEqual(str(self.experience), expected)


class EducationModelTest(TestCase):
    """Test Education model"""

    def setUp(self):
        self.education = Education()
        self.education.set_current_language('en')
        self.education.institution = "Test University"
        self.education.degree = "Bachelor of Science"
        self.education.field_of_study = "Computer Science"
        self.education.description = "CS degree"
        self.education.start_date = date(2016, 9, 1)
        self.education.end_date = date(2020, 6, 30)
        self.education.education_type = 'formal'
        self.education.save()

    def test_education_creation(self):
        """Test education is created correctly"""
        self.assertEqual(self.education.institution, "Test University")
        self.assertEqual(self.education.education_type, 'formal')

    def test_education_str(self):
        """Test string representation"""
        expected = "Bachelor of Science - Test University"
        self.assertEqual(str(self.education), expected)


class SkillModelTest(TestCase):
    """Test Skill model"""

    def setUp(self):
        self.skill = Skill()
        self.skill.set_current_language('en')
        self.skill.name = "Python"
        self.skill.proficiency = 4
        self.skill.years_experience = 5
        self.skill.category = "Programming Languages"
        self.skill.save()

    def test_skill_creation(self):
        """Test skill is created correctly"""
        self.assertEqual(self.skill.name, "Python")
        self.assertEqual(self.skill.proficiency, 4)

    def test_skill_str(self):
        """Test string representation"""
        # Skill __str__ includes proficiency in parentheses
        self.assertIn("Python", str(self.skill))
        self.assertIn("Experto", str(self.skill))


class ContactModelTest(TestCase):
    """Test Contact model"""

    def test_contact_creation(self):
        """Test contact is created correctly"""
        contact = Contact.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="Test message"
        )

        self.assertEqual(contact.name, "John Doe")
        self.assertFalse(contact.read)

    def test_contact_str(self):
        """Test string representation"""
        contact = Contact.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="Test message"
        )

        expected = "John Doe - Test Subject"
        self.assertEqual(str(contact), expected)


class LanguageModelTest(TestCase):
    """Test Language model"""

    def setUp(self):
        self.language = Language.objects.create(
            code="en",
            proficiency="Native"
        )
        self.language.set_current_language('en')
        self.language.name = "English"
        self.language.save()

    def test_language_creation(self):
        """Test language is created correctly"""
        self.assertEqual(self.language.code, "en")
        self.assertEqual(self.language.proficiency, "Native")

    def test_language_str(self):
        """Test string representation"""
        # Language __str__ format is "name (proficiency)"
        self.assertEqual(str(self.language), "English (Native)")
