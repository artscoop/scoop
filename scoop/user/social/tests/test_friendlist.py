# coding: utf-8
from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from scoop.core.util.django.testing import TEST_CONFIGURATION
from scoop.user.models.activation import Activation

User = get_user_model()


@override_settings(**TEST_CONFIGURATION)
class FriendlistTest(TestCase):
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

    def test_friendship(self):
        """ Vérifier le lien entre plusieurs utilisateurs """
        pass
