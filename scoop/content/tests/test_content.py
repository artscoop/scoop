# coding: utf-8
from importlib import import_module

import loremipsum
from django.conf import settings
from django.test.testcases import TestCase
from django.utils import timezone
from scoop.content.models import Content
from scoop.content.models.content import Category
from scoop.user.models.user import User


class ContentTest(TestCase):
    """ Test des contenus """
    # Configuration
    fixtures = ['category', 'mailtype', 'options']

    def setUp(self):
        """ Définit l'environnement des tests """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='commentuser', email='foo@foobar2.foo')
        self.administrator = User.objects.create(username='adminuser', email='foo@foobar3.foo', is_superuser=True, is_staff=True)

    def test_content_visibility(self):
        """ Tester la publication et la visibilité des contenus """
        # Créer des contenus variés
        content1 = Content.objects.post([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True)
        content2 = Content.objects.post(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        content3 = Content.objects.post(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        content3.publish = timezone.now() - timezone.timedelta(hours=1)
        content3.save()
        content4 = Content.objects.post(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        content4.publish = timezone.now() + timezone.timedelta(hours=1)
        content4.save()
        content5 = Content.objects.post(self.administrator, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=True)
        self.assertFalse(content1.is_published(), "content 1 should be unpublished")  # Approval sets published to False for base users
        self.assertFalse(content2.is_published(), "content 2 should be unpublished")
        self.assertFalse(content3.is_published(), "content 3 should be unpublished")
        self.assertFalse(content4.is_published(), "content 4 should be unpublished")
        self.assertFalse(content5.is_published(), "content 5 should be unpublished")
        self.assertEqual(Content.objects.visible().count(), 0, "there should be exactly 1 visible content")
        # Tester le statut du contenu
        self.assertGreater(len(content1.html), 10, "the html display for the content should not be populated")

    def test_content_categories(self):
        """ Tester la publication et la visibilité des contenus """
        content1 = Content.objects.post([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True)
        self.assertIsNotNone(Category.objects.get_by_url('blog'), "a content type with the blog path should exist")
        self.assertGreater(Category.objects.all().count(), 0, "could not find any content type, which should be impossible")
        self.assertEqual(content1.category.short_name, 'blog', "content 1 should be a 'blog' entry")

    def test_content_authors(self):
        """ Tester la publication et la visibilité des contenus """
        content1 = Content.objects.post([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True)
        content5 = Content.objects.post(self.administrator, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=True)
        self.assertTrue(content1.is_author(self.user), "cannot find expected author in content1")
        self.assertTrue(content5.is_author(self.administrator), "cannot find expected author in content5")
        self.assertFalse(content5.is_author(self.user), "found unexpected author in content5")
        self.assertTrue(content1.is_editable(self.user), "content1 should be editable by user")
        self.assertTrue(content1.is_editable(self.administrator), "content5 should be editable by admin")

    def test_content_properties(self):
        """ Tester la publication et la visibilité des contenus """
        content1 = Content.objects.post([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True)
        self.assertTrue(content1.is_new(), "this new content should be considered new")
