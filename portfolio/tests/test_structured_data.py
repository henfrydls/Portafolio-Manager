"""
Tests for the JSON-LD on the home page.

The view stored the data under `structured_data` while the template read
`person_structured_data` and `website_structured_data`, so nothing was
ever rendered.
"""
import json
import re

from django.test import SimpleTestCase

from portfolio.models import Profile
from portfolio.tests.test_i18n_language import BasePublicPagesTest
from portfolio.utils.seo import SEOGenerator


def json_ld_blocks(html):
    return [json.loads(block) for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


class HomeStructuredDataTest(BasePublicPagesTest):

    def blocks(self):
        return {block['@type']: block for block in json_ld_blocks(self.client.get('/').content.decode())}

    def test_person_and_website_are_rendered(self):
        blocks = self.blocks()
        self.assertEqual(blocks['Person']['name'], "Test User")
        self.assertEqual(blocks['Person']['jobTitle'], "Test Developer")
        self.assertEqual(blocks['Person']['url'], 'http://testserver')
        self.assertEqual(blocks['WebSite']['url'], 'http://testserver')

    def test_contact_details_are_not_published(self):
        Profile.objects.update(phone='+1 809 555 0100')
        html = self.client.get('/').content.decode()
        person = self.blocks()['Person']
        self.assertNotIn('email', person)
        self.assertNotIn('telephone', person)
        self.assertNotIn('809 555', ''.join(re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)))

    def test_no_search_action_for_a_search_page_that_does_not_exist(self):
        self.assertNotIn('potentialAction', self.blocks()['WebSite'])


class JsonLdSerializationTest(SimpleTestCase):

    def test_round_trips_and_keeps_accents_readable(self):
        text = SEOGenerator.to_json_ld({'name': 'José <b>&'})
        self.assertIn('José', text)
        self.assertNotIn('<', text)
        self.assertNotIn('&', text)
        self.assertEqual(json.loads(text), {'name': 'José <b>&'})

    def test_markup_in_the_data_cannot_close_the_script_element(self):
        text = SEOGenerator.to_json_ld({'description': '</script><script>alert(1)</script>'})
        self.assertNotIn('</script>', text)
        self.assertEqual(json.loads(text)['description'], '</script><script>alert(1)</script>')

    def test_empty_data_renders_nothing(self):
        self.assertEqual(SEOGenerator.to_json_ld({}), '')
