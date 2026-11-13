"""
Tests for what the dashboard says after deleting something.

The delete views overrode delete(), which DeleteView no longer calls on POST
since Django 4.0: nothing confirmed the deletion, and deleting a category or
project type that was still in use answered 500.
"""
from django.contrib.messages import get_messages
from django.urls import reverse

from portfolio.models import BlogPost, Category, Contact, Project, ProjectType
from portfolio.tests.test_i18n_language import BasePublicPagesTest, User


class DashboardDeleteTest(BasePublicPagesTest):

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username='admin'))

    def delete(self, url_name, pk):
        response = self.client.post(reverse(url_name, kwargs={'pk': pk}))
        self.assertEqual(response.status_code, 302)
        return [(m.level_tag, str(m)) for m in get_messages(response.wsgi_request)]

    def test_deleting_a_post_confirms_it_by_name(self):
        messages = self.delete('portfolio:admin-blog-delete', self.post.pk)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], 'success')
        self.assertIn('Test Post', messages[0][1])

    def test_deleting_a_project_confirms_it_by_name(self):
        messages = self.delete('portfolio:admin-project-delete', self.project.pk)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(messages[0][0], 'success')
        self.assertIn('Test Project', messages[0][1])

    def test_deleting_a_contact_message_confirms_it(self):
        contact = Contact.objects.create(
            name="Ada", email="ada@example.com", subject="Hi", message="Hello there")
        messages = self.delete('portfolio:admin-contact-delete', contact.pk)
        self.assertFalse(Contact.objects.filter(pk=contact.pk).exists())
        self.assertEqual(messages[0][0], 'success')
        self.assertIn('Ada', messages[0][1])

    def test_a_category_in_use_is_kept_and_explained(self):
        messages = self.delete('portfolio:admin-category-delete', self.category.pk)
        self.assertTrue(Category.objects.filter(pk=self.category.pk).exists())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][0], 'error')
        self.assertIn('Idea', messages[0][1])

    def test_a_project_type_in_use_is_kept_and_explained(self):
        messages = self.delete('portfolio:admin-projecttype-delete', self.project_type.pk)
        self.assertTrue(ProjectType.objects.filter(pk=self.project_type.pk).exists())
        self.assertEqual(messages[0][0], 'error')

    def test_an_unused_category_is_deleted(self):
        unused = Category.objects.create(slug='unused')
        unused.set_current_language('en')
        unused.name = "Unused"
        unused.save()
        messages = self.delete('portfolio:admin-category-delete', unused.pk)
        self.assertFalse(Category.objects.filter(pk=unused.pk).exists())
        self.assertEqual(messages[0][0], 'success')
        self.assertIn('Unused', messages[0][1])
