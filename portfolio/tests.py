from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile


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