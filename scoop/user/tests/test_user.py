# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.importlib import import_module

from scoop.core.util.data.typeutil import list_contains
from scoop.core.util.stream.directory import Paths
from scoop.messaging.models.mailevent import MailEvent
from scoop.user.models.activation import Activation
from scoop.user.templatetags.user_tags import distance_to

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH=Paths.get_root_dir('files', 'tests', 'mail'), DEFAULT_FROM_EMAIL='admin@test.com')
class UserTest(TestCase):
    """ Test des utilisateurs """
    fixtures = ['mailtype', 'options']

    def setUp(self):
        """ Préparer l'environnement de test """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='testuser', email='foo@foobar.foo')
        self.user.set_password('testuser')
        self.user.save()
        Activation.objects.activate(None, 'testuser')
        self.user = User.objects.get(username='testuser')

    def test_creation(self):
        """ Vérifier l'état de création des utilisateurs """
        self.assertIsNotNone(self.user, "user testuser cannot be created")
        self.assertTrue(hasattr(self.user, 'activation'), "activation information is missing")
        if hasattr(self.user, 'profile'):
            self.assertTrue(hasattr(self.user.profile, 'city'), "user profile should have a city field")
            self.assertFalse(getattr(self.user.profile, 'banned', True), "user profile should have a banned field set to False")

    def test_authentication(self):
        """ Vérifier que la connexion à un compte fonctionne normalement """
        user2 = auth.authenticate(username='TestUser', password='testuser')  # pseudo avec mauvaise casse (ok) et bon mot de passe
        user1 = auth.authenticate(username='testuser', password='testuser')  # pseudo exact et bon mot de passe
        user3 = auth.authenticate(username='testuser', password='testUser')  # pseudo exact et mauvais mot de passe (casse)
        # Authentifier les 3 utilisateurs
        self.assertIsNotNone(user1, "normal credentials failed to authenticate")
        self.assertIsNotNone(user2, "mixed case credentials failed to authenticate")
        self.assertIsNone(user3, "wrong password must not authenticate")
        # Login
        if list_contains(settings.AUTHENTICATION_BACKENDS, '.email.CaseInsensitiveEmailModelBackend'):
            user4 = auth.authenticate(username='foo@foobar.foo', password='testuser')  # email et bon mot de passe
            user5 = auth.authenticate(username='foo@foobar.foo', password='Testuser')  # email et mauvais mot de passe (casse)
            user6 = auth.authenticate(username='FOO@foobar.foo', password='testuser')  # email avec mauvaise casse (ok) et bon mot de passe
            self.assertIsNotNone(user4, "email credentials failed to authenticate")
            self.assertIsNotNone(user6, "email credentials failed to authenticate")
            self.assertIsNone(user5, "wrong password must not authenticate")

    def test_attributes(self):
        """ Vérifier les atributs des objets utilisateur """
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff or self.user.is_superuser)
        if hasattr(self.user, 'profile'):
            self.assertTrue(isinstance(self.user.profile.get_picture(None), str), "user picture should be a path by default")
            self.assertTrue(hasattr(self.user.profile, 'updated'), "user profile should have an updated field")
            self.assertTrue(getattr(self.user.profile, 'gender', None) is not None, "user profile should have a gender attribute defined")

    def test_template_tags(self):
        """ Vérifier que les template tags fonctionnent comme prévu """
        self.assertEquals(distance_to(self.user, self.user), "")

    def test_usernames(self):
        """ Vérifier que les noms d'utilisateurs répondent toujours à un format """
        user1 = User.objects.create(username=u'métal1234', email="metal1234@example.com")
        self.assertEquals(user1.username, 'metal1234', "username should be metal1234")

    def test_new_user_email(self):
        """ Vérifier que l'envoi d'emails fonctionne comme prévu """
        unsent = MailEvent.objects.get_unsent_count()
        sent = MailEvent.objects.process('all')
        remaining = MailEvent.objects.get_unsent_count()
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.filebased.EmailBackend', "the email backend is {} but should be file based".format(settings.EMAIL_BACKEND))
        self.assertGreater(unsent, 0, "at least one activation mail should be waiting in the queue")
        self.assertGreater(sent, 0, "at least one activation mail should have been sent")
        self.assertGreater(unsent, remaining, "there should remain less mails to be sent")
