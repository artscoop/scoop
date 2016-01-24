# coding: utf-8
from importlib import import_module

import loremipsum
from django.conf import settings
from django.test.testcases import TestCase
from django.utils import timezone
from scoop.content.models import Content
from scoop.content.models.content import Category
from scoop.content.models.link import Link
from scoop.user.models.user import User


class LinkTest(TestCase):
    """ Test des liens """
    # Configuration
    fixtures = []

    def setUp(self):
        """ Définit l'environnement des tests """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()

    def test_link_format(self):
        """ Vérifier le format des liens """
        link1 = Link.objects.create(url='http://a.com')  # valide
        link2 = Link.objects.create(url='httu://a.com')  # invalide
        link3 = Link.objects.create(url='http://a.com/?a=1&b=2')  # valide
        self.assertTrue(link1.is_valid(), "This link is formatted properly")
        self.assertFalse(link2.is_valid(), "This link is not formatted properly")
        self.assertTrue(link3.is_valid(), "This link is formatted properly")

    def test_link_access(self):
        """ Vérifier que les liens sont accessibles """
        link1 = Link.objects.create(url='http://example.com')  # accessible
        link2 = Link.objects.create(url='http://a.com')  # inaccessible
        self.assertTrue(link1.exists(), "This URL should be working")
        self.assertFalse(link2.exists(), "This URL should not be working")

    def test_link_html(self):
        """ Vérifier que le HTML du lien est conforme """
        link1 = Link.objects.create(url='http://example.com', nofollow=True)  # accessible
        link2 = Link.objects.create(url='http://example.com', nofollow=False)  # accessible
        self.assertContains(link1.html(), 'nofollow', "The generated HTML code must contain 'nofollow'")
        self.assertNotContains(link2.html(), 'nofollow', "The generated HTML code should not contain 'nofollow'")
