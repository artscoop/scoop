# coding: utf-8
from importlib import import_module

from django.conf import settings
from django.test import TestCase

from scoop.rogue.models.blocklist import Blocklist
from scoop.user.models.activation import Activation
from scoop.user.models.user import User


class BlocklistTest(TestCase):
    """ Test des blocages """

    # Configuration
    fixtures = ['category', 'mailtype', 'options']

    @classmethod
    def setUp(self):
        """ Définir l'environnement de test """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user1 = User.objects.create(username='user1', email='1@thread.foo', is_active=True)
        self.user2 = User.objects.create(username='user2', email='2@thread.foo', is_active=True)
        self.user3 = User.objects.create(username='user3', email='3@thread.foo', is_active=True)
        self.user4 = User.objects.create(username='user4', email='4@thread.foo', is_staff=True, is_active=True)
        Activation.objects.activate(None, 'user1')
        Activation.objects.activate(None, 'user2')
        Activation.objects.activate(None, 'user3')
        Activation.objects.activate(None, 'user4')

    def test_blocklist(self):
        """ Tester que des blocages fonctionnent """
        blacklisted = self.user1.blocklist.add(self.user2, 'blacklist')  # empêcher user2 de répondre à user1
        self.assertTrue(blacklisted, "user2 should be blacklisted by user1")
        self.assertFalse(Blocklist.objects.is_safe(self.user1, self.user2, 'blacklist'))
        self.assertTrue(Blocklist.objects.is_safe(self.user1, self.user3, 'blacklist'))
        self.assertTrue(Blocklist.objects.is_safe(self.user1, self.user2, 'hidelist'))
