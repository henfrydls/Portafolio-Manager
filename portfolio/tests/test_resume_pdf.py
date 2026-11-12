"""
Tests for /resume/pdf/.

The route pointed at a template that was never in the repository, so every
request ended in a 500. It now sends the visitor to the uploaded PDF for the
active language, or answers 404 when there is none.
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import translation

from portfolio.models import Profile
from portfolio.tests.test_views_public import create_test_profile


class ResumePDFViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.profile = create_test_profile()
        # Without a superuser the first-run middleware redirects every request
        get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='testpass123'
        )
        translation.activate('en')
        self.url = reverse('portfolio:resume-pdf')

    def upload(self, **files):
        Profile.objects.filter(pk=self.profile.pk).update(**files)

    def test_returns_404_when_no_pdf_is_uploaded(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_returns_404_when_there_is_no_profile(self):
        Profile.objects.all().delete()
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_redirects_to_the_uploaded_pdf(self):
        self.upload(resume_pdf='resumes/cv-en.pdf')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('resumes/cv-en.pdf'))

    def test_spanish_page_gets_the_spanish_pdf(self):
        self.upload(resume_pdf='resumes/cv-en.pdf', resume_pdf_es='resumes/cv-es.pdf')
        with translation.override('es'):
            url = reverse('portfolio:resume-pdf')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('resumes/cv-es.pdf'))

    def test_falls_back_to_the_only_pdf_available(self):
        self.upload(resume_pdf_es='resumes/cv-es.pdf')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('resumes/cv-es.pdf'))
