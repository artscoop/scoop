# coding: utf-8
from __future__ import absolute_import

from datetime import timedelta

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from django.utils.importlib import import_module

from scoop.core.models.redirection import Redirection
from scoop.core.templatetags.datetime_tags import days_from_now as tt_days_from_now
from scoop.core.templatetags.datetime_tags import is_date_new as tt_is_new
from scoop.core.templatetags.html_tags import linebreaks_convert as tt_linebreaks
from scoop.core.templatetags.html_tags import sanitize as tt_sanitize
from scoop.core.templatetags.html_tags import tags_keep as tt_tags_keep
from scoop.core.util.stream.directory import Paths
from scoop.user.models.user import User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
                   EMAIL_FILE_PATH=Paths.get_root_dir('files', 'tests', 'mail'),
                   DEFAULT_FROM_EMAIL='admin@test.com')
class TemplateTagsTest(TestCase):
    """ Test des template tags """
    fixtures = ['mailtype', 'options']

    def setUp(self):
        """ Préparer l'environnement de test """
        # Créer un utilisateur
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user1 = User.objects.create(username='user1', email='1@thread.foo', is_active=True)
        self.user2 = User.objects.create(username='user2', email='2@thread.foo', is_active=True)
        self.user3 = User.objects.create(username='user3', email='3@thread.foo', is_active=True)
        self.user4 = User.objects.create(username='user4', email='4@thread.foo', is_staff=True, is_active=True)

    # Tests
    def test_datetime_tags(self):
        """ Tester les tags de date """
        now = timezone.now()
        last_hour = timezone.now() - timedelta(hours=1)
        yesterday = timezone.now() - timedelta(days=1)
        last_week = timezone.now() - timedelta(days=7)
        next_week = timezone.now() + timedelta(days=7)
        last_month = timezone.now() - timedelta(days=30)
        redirection = Redirection()
        redirection.set_datetime(last_week)
        # is_new
        self.assertFalse(tt_is_new(last_week, 6))
        self.assertFalse(tt_is_new(last_month, '29d 23h'))
        self.assertTrue(tt_is_new(last_week, 8))
        self.assertTrue(tt_is_new(last_hour, 1))
        self.assertTrue(tt_is_new(next_week, -2))
        self.assertTrue(tt_is_new(redirection, 30))
        self.assertFalse(tt_is_new(redirection, '6d 23h 59m'))
        self.assertFalse(tt_is_new(yesterday, 1))  # à quelques microsecondes
        # days_from_now
        self.assertTrue(tt_days_from_now(-1) < now)
        self.assertTrue(tt_days_from_now(0) > now)  # à quelques microsecondes
        self.assertTrue(tt_days_from_now(1) > now)

    def test_html_tags(self):
        """ Tester les tags HTML """
        insane = "<script type='javascript'>alert('harmful html');</script><h2>Sound part of HTML</h2>"
        filtered_sane = "<h1 style='margin-left: 1em;'>Titre</h1>Nous sommes les garants du bon fonctionnement de l'univers"
        sane = "<h1>Acceptable tag</h1><p>The quick brown fox<br>Jumps over the lazy dog</p>"
        lined_text = "\n\nBonjour,\n\n\n\nnous sommes heureux de vous accueillir.\n"
        # tags_keep
        self.assertNotEqual(insane, tt_tags_keep(insane))
        self.assertNotEqual(insane, tt_sanitize(insane))
        self.assertEqual(sane, tt_tags_keep(sane))
        self.assertEqual(sane, tt_sanitize(sane))
        self.assertNotEqual(filtered_sane, tt_tags_keep(filtered_sane))  # style non conservé
        self.assertNotEqual(filtered_sane, tt_sanitize(filtered_sane))  # style non conservé
        # linebreaks_convert
        self.assertEqual(tt_linebreaks(lined_text).count('<br>'), 2)  # les retours chariot en début de ligne sont enlevés
