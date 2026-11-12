"""
Tests for the text of the SEO metadata.

The generator shipped with accented characters replaced by "?" in its source,
with Spanish wording hardcoded for every language, and with " - Blog" /
" - Proyecto" appended to the titles used in link previews.
"""
from types import SimpleNamespace

from django.test import SimpleTestCase
from django.utils import translation

from portfolio.utils.seo import SEOGenerator


def profile():
    return SimpleNamespace(name="Ada Lovelace", title="Engineer", bio="Bio", profile_image=None)


def category():
    return SimpleNamespace(name="Tutorials", description="", slug="tutorials")


def every_text(seo):
    return " ".join(str(v) for k, v in seo.items() if k in (
        'title', 'description', 'keywords', 'og_title', 'og_description'))


class MetadataTextTest(SimpleTestCase):

    def generated(self):
        return {
            'home without profile': SEOGenerator.generate_home_seo(None),
            'blog list': SEOGenerator.generate_blog_list_seo(),
            'blog category': SEOGenerator.generate_blog_list_seo(category=category()),
            'resume': SEOGenerator.generate_resume_seo(profile()),
            'resume without profile': SEOGenerator.generate_resume_seo(None),
            'website': {'description': SEOGenerator.generate_structured_data_website()['description']},
        }

    def test_no_corrupted_characters(self):
        for language in ('en', 'es'):
            with translation.override(language):
                for page, seo in self.generated().items():
                    with self.subTest(language=language, page=page):
                        self.assertNotIn('?', every_text(seo))

    def test_english_pages_get_english_text(self):
        spanish_words = ('Artículos', 'Currículum', 'Proyecto', 'tecnología', 'educación', 'Desarrollador')
        with translation.override('en'):
            for page, seo in self.generated().items():
                with self.subTest(page=page):
                    for word in spanish_words:
                        self.assertNotIn(word.lower(), every_text(seo).lower())

    def test_spanish_pages_get_spanish_text(self):
        with translation.override('es'):
            self.assertIn('Artículos', SEOGenerator.generate_blog_list_seo()['description'])
            self.assertIn('Artículos sobre tutorials',
                          SEOGenerator.generate_blog_list_seo(category=category())['description'])
            resume = SEOGenerator.generate_resume_seo(profile())
            self.assertIn('Currículum profesional de Ada Lovelace', resume['description'])
            self.assertEqual(resume['og_title'], 'CV - Ada Lovelace')

    def test_english_resume_and_blog_wording(self):
        with translation.override('en'):
            resume = SEOGenerator.generate_resume_seo(profile())
            self.assertEqual(resume['og_title'], 'Resume - Ada Lovelace')
            self.assertIn('Professional resume of Ada Lovelace', resume['description'])
            self.assertEqual(SEOGenerator.generate_blog_list_seo()['og_title'], 'Blog')

    def test_structured_data_description_is_plain_text(self):
        """A lazy translation object would break the JSON-LD serialisation."""
        self.assertIs(type(SEOGenerator.generate_structured_data_website()['description']), str)


class LinkPreviewTitleTest(SimpleTestCase):
    """og:title is what LinkedIn, WhatsApp and Slack show: it must be the
    plain title, without a section suffix."""

    def test_blog_post_title_has_no_suffix(self):
        from django.utils import timezone
        post = SimpleNamespace(
            title="What people protect", excerpt="Excerpt", content="", tags="",
            featured_image=None, get_absolute_url=lambda: '/post/x/',
            publish_date=timezone.now(), updated_at=timezone.now(), category=None,
            get_tags_list=lambda: [],
        )
        seo = SEOGenerator.generate_blog_post_seo(post)
        self.assertEqual(seo['og_title'], "What people protect")
        self.assertEqual(seo['title'], "What people protect")

    def test_project_title_has_no_suffix(self):
        from django.utils import timezone
        project = SimpleNamespace(
            title="Skima", description="Desc", image=None, github_owner="",
            get_absolute_url=lambda: '/project/skima/',
            created_at=timezone.now(), updated_at=timezone.now(),
            knowledge_bases=SimpleNamespace(all=lambda: []),
        )
        for language in ('en', 'es'):
            with translation.override(language):
                seo = SEOGenerator.generate_project_seo(project)
                self.assertEqual(seo['og_title'], "Skima")
