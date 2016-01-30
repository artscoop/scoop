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
        user1 = User.objects.create(username='user1', email='user1@foo.bar', is_active=True)
        user2 = User.objects.create(username='user2', email='user2@foo.bar', is_active=True)
        user3 = User.objects.create(username='user3', email='user3@foo.bar')
        user4 = User.objects.create(username='user4', email='user4@foo.bar')

        # Créer une demande d'amitié et un lien d'amitié
        user1.friends.add_sent(user3)
        user2.friends.add_friend(user3)

        self.assertTrue(user1.friends.is_sent(user3), "user1 has sent a request to user3")
        self.assertFalse(user2.friends.is_sent(user3), "user2 has not sent a request to user3")
        self.assertFalse(user3.friends.is_sent(user1), "user3 has not sent a request to user1")
        self.assertTrue(user2.friends.is_friend(user3), "user2 should be friends with user3")
