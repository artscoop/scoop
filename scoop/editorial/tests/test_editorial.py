# coding: utf-8
import os

from django.http.response import HttpResponse
from django.test import TestCase

from scoop.core.util.stream.request import default_request
from scoop.editorial.models.configuration import Configuration
from scoop.editorial.models.excerpt import Excerpt, ExcerptTranslation
from scoop.editorial.models.page import Page
from scoop.editorial.models.template import Template
from scoop.user.models.user import User


class EditorialTest(TestCase):
    """ Test des configurations éditoriales """

    # Configuration
    fixtures = ['mailtype', 'options']
    urls = 'settings.urlconf.base'

    def setUp(self):
        """ Définir l'environnement de test """
        self.user = User.objects.create(username='user1', email='foo@foobar3.foo')

    def test_editorial_page(self):
        """ Tester la création de contenus page """
        template = Template.objects.create(name='t1', path='tests/editorial/base_template.html')
        excerpt_template = Template.objects.create(name='t2', path='tests/editorial/excerpt.html')

        # Créer un extrait
        excerpt = Excerpt.objects.create_translated({'en': {'text': "Excerpt"}}, name='x1', title="Excerpt", description="Excerpt", author=self.user)

        # Créer une page
        page = Page.objects.create(name='p1', title='Page', path='/p1', template=template, author=self.user)
        position = page.get_position('title')

        # Créer une configuration
        configuration = Configuration(page=page, position=position, template=excerpt_template, content_object=excerpt)
        configuration.save()

        # Rendu
        output = HttpResponse(page.render(default_request()))

        # Test du template
        self.assertTrue(template.exists(), "the template file should be found.")
        self.assertTrue(template.full, "the template should be autodetected as a full HTML template")
        self.assertTrue(template.has_positions(), "the template should have one position detected")
        self.assertEqual(template.get_position_count(), 1, "the template should have one position detected")

        self.assertIsInstance(output, HttpResponse, "At least the output should be an HTTPResponse")
        self.assertContains(output, '<html lang="en">', 1)
        self.assertContains(output, '</html>')
        self.assertContains(output, '<head>')
        self.assertContains(output, '</head>')
        self.assertContains(output, '<body>')
        self.assertContains(output, '</body>')
        self.assertContains(output, 'Excerpt')
