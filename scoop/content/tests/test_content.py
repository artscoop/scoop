# coding: utf-8
from __future__ import absolute_import

import loremipsum
from django.conf import settings
from django.test.testcases import TestCase
from django.utils import timezone
from django.utils.importlib import import_module

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
        self.user.set_password('commentuser')
        self.user.save()
        # Créer des contenus variés
        self.content1 = Content.objects.create([self.user], 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(8), visible=True)
        self.content2 = Content.objects.create(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        self.content3 = Content.objects.create(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        self.content3.publish = timezone.now() - timezone.timedelta(hours=1)
        self.content3.save()
        self.content4 = Content.objects.create(self.user, 'blog', loremipsum.get_sentence()[0:100], loremipsum.get_paragraphs(12), visible=False)
        self.content4.publish = timezone.now() + timezone.timedelta(hours=1)
        self.content4.save()

    def test_content(self):
        """ Tester la publication et la visibilité des contenus """
        self.assertIsNotNone(Category.objects.get_by_url('blog'), "a content type with the blog path should exist")
        self.assertGreater(Category.objects.all().count(), 0, "could not find any content type, which should be impossible")
        self.assertEqual(self.content1.category.short_name, 'blog', "content 1 should be a 'blog' entry")
        self.assertTrue(self.content1.is_published(), "content 1 should be published")
        self.assertFalse(self.content2.is_published(), "content 2 should be unpublished")
        self.assertTrue(self.content3.is_published(), "content 3 should be published")
        self.assertFalse(self.content4.is_published(), "content 4 should be unpublished")
        self.assertEqual(Content.objects.visible().count(), 2, "there should be exactly 2 visible contents")
        self.assertTrue(self.content1.is_author(self.user), "cannot find expected author in content1")
        self.assertTrue(self.content1.is_new(), "this new content should be considered new")
        # Tester le statut du contenu
        self.assertGreater(len(self.content1.html), 10, "the html display for the content should be populated")
        self.assertTrue(self.content1.is_editable(self.user), "the content should be editable by user")
