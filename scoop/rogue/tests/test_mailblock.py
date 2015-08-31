# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.test import TestCase
from django.utils.importlib import import_module

from scoop.rogue.models.mailblock import MailBlock
from scoop.user.models.user import User


class MailBlockTest(TestCase):
    """ Test des blocages d'adresses mail """
    # Configuration
    fixtures = ['category', 'mailtype', 'options']

    @classmethod
    def setUp(self):
        """ Définir l'environnement de test """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='commentuser', email='foo@foobar1.foo')
        self.user.set_password('commentuser')
        self.user.save()

    def test_mailblock_detection(self):
        """ Tester que des adresses saines et bloquées sont détectées correctement """
        disposable_email = "david.cameron@jetable.org"
        correct_email = "david.cameron@gmail.com"
        self.assertTrue(MailBlock.objects.is_blocked(disposable_email), "The email {} should be blocked.".format(disposable_email))
        self.assertFalse(MailBlock.objects.is_blocked(correct_email), "The email {} should be accepted.".format(correct_email))
