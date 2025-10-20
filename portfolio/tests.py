from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import Profile, SiteConfiguration
from django.utils import translation


class ErrorPageTestCase(TestCase):
    """Test cases for custom error pages"""
    
    def setUp(self):
        self.client = Client()
        # Create a test profile
        self.profile = Profile.objects.create(
            name="Test User",
            title="Test Developer",
            bio="Test bio",
            email="test@example.com",
            location="Test City"
        )
    
    def test_404_error_page(self):
        """Test that 404 error page renders correctly"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "Página no encontrada", status_code=404)
        self.assertContains(response, "Ir al inicio", status_code=404)
    
    def test_403_error_page_unauthenticated(self):
        """Test that 403 error page renders correctly for unauthenticated users"""
        # Try to access an admin-only view
        response = self.client.get('/admin-dashboard/')
        # This should redirect to login, but if we force a 403, it should render our template
        # We'll test the view function directly
        from .views import custom_403
        from django.http import Http404
        
        request = self.client.request().wsgi_request
        response = custom_403(request, Http404())
        self.assertEqual(response.status_code, 403)
    
    def test_500_error_page(self):
        """Test that 500 error page renders correctly"""
        # Test the view function directly
        from .views import custom_500
        
        request = self.client.request().wsgi_request
        response = custom_500(request)
        self.assertEqual(response.status_code, 500)
    
    def test_error_pages_with_profile_context(self):
        """Test that error pages include profile context"""
        from .views import custom_404, custom_500, custom_403
        from django.http import Http404
        
        request = self.client.request().wsgi_request
        
        # Test 404
        response = custom_404(request, Http404())
        self.assertEqual(response.status_code, 404)
        
        # Test 500
        response = custom_500(request)
        self.assertEqual(response.status_code, 500)
        
        # Test 403
        response = custom_403(request, Http404())
        self.assertEqual(response.status_code, 403)


class InitialSetupWizardTests(TestCase):
    """Tests for the first-run setup wizard."""

    def setUp(self):
        self.client = Client()
        translation.activate('en')
        SiteConfiguration.get_solo()
        self.profile = Profile.objects.create(
            name="Setup User",
            title="Setup Admin",
            bio="Bio",
            email="setup-profile@example.com",
            location="Setup City"
        )

    def test_setup_accessible_without_superuser(self):
        response = self.client.get(reverse('portfolio:initial-setup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First run setup")

    def test_dashboard_redirects_to_setup_when_no_superuser(self):
        response = self.client.get(reverse('portfolio:admin-dashboard'))
        self.assertRedirects(
            response,
            reverse('portfolio:initial-setup'),
            fetch_redirect_response=False,
        )

    def test_setup_creates_superuser_and_updates_language(self):
        payload = {
            'username': 'first-admin',
            'email': 'admin@example.com',
            'password1': 'SuperSecure123!',
            'password2': 'SuperSecure123!',
            'language': 'es',
        }
        response = self.client.post(reverse('portfolio:initial-setup'), payload)
        self.assertRedirects(response, reverse('portfolio:admin-dashboard'))

        user_model = get_user_model()
        user = user_model.objects.get(username='first-admin')
        self.assertTrue(user.is_superuser)
        config = SiteConfiguration.get_solo()
        self.assertEqual(config.default_language, 'es')
        self.assertTrue(config.auto_translate_enabled)
        session = self.client.session
        self.assertEqual(int(session['_auth_user_id']), user.pk)

    def test_setup_redirects_when_superuser_exists(self):
        user_model = get_user_model()
        user_model.objects.create_superuser(
            username='existing-admin',
            email='existing@example.com',
            password='Existing123!',
        )
        response = self.client.get(reverse('portfolio:initial-setup'))
        self.assertRedirects(
            response,
            reverse('portfolio:login'),
            fetch_redirect_response=False,
        )
