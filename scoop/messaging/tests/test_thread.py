# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.importlib import import_module

from scoop.messaging.models.mailevent import MailEvent
from scoop.messaging.models.negotiation import Negotiation
from scoop.messaging.models.quota import Quota
from scoop.messaging.models.thread import Thread
from scoop.rogue.models.blocklist import Blocklist
from settings.django import root_dir
from scoop.user.models.activation import Activation
from scoop.user.models.user import User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend',
                   EMAIL_FILE_PATH=root_dir('files', 'tests', 'mail'),
                   DEFAULT_FROM_EMAIL='admin@test.com')
class ThreadTest(TestCase):
    """ Test des fils de discussion """
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
        Activation.objects.activate(None, 'user1')
        Activation.objects.activate(None, 'user2')
        Activation.objects.activate(None, 'user3')
        Activation.objects.activate(None, 'user4')
        MailEvent.objects.process('all')

    # Tests
    def test_a_thread_access(self):
        """ Tester l'accès aux threads """
        thread_12 = Thread.objects.new(self.user1, [self.user2], u"Thread 1-2", u"Thread 1-2 introductory message")['thread']
        # Accès au thread
        self.assertFalse(thread_12.is_recipient(self.user3), "user3 is not a member of thread 1-2")
        self.assertTrue(thread_12.is_recipient(self.user4), "user4 is not a real recipient but should have full access to thread 1-2")
        # Possibilité d'ajouter un message
        self.assertRaises(PermissionDenied, thread_12.add_message, self.user3, u"Unallowed message from user3")
        self.assertIsNotNone(thread_12.add_message(self.user4, u"full permission message from user4"))
        self.assertIsNotNone(thread_12.add_message(self.user2, u"normal reply message from user2"))
        self.assertEqual(thread_12.get_talking_users().count(), 3, u"there should be three different users talking in this thread")
        self.assertEqual(thread_12.get_message_count(), 3, u"three messages should be readable")
        self.assertFalse(thread_12.is_staff(), u"thread_12 is not a staff thread")
        self.assertFalse(thread_12.set_closed(True, self.user2), u"user2 is not the thread owner and shouldn't be able to close it")
        self.assertFalse(thread_12.set_closed(True, self.user1), u"user1 is the thread owner but shouldn't be able to close it immediately")
        self.assertFalse(thread_12.set_closed(False, self.user1), u"user1 is the thread owner and should be able to reopen it but after a timeframe")
        self.assertTrue(thread_12.set_closed(None, self.user4), u"user4 is staff and should be able to open/close any thread, anytime")  # état prévu : fermé
        self.assertRaises(PermissionDenied, thread_12.add_message, self.user1, u"Unallowed message from user1")
        self.assertEqual(Thread.objects.get_common_thread_count(self.user1, self.user2), 1, u"only one thread has user1 ans user2")
        self.assertTrue(thread_12.is_unread(self.user1), u"user2 updated thread_12 last, so it's unread for user1")  # doit être lu par user2 seulement
        self.assertFalse(thread_12.is_unread(self.user2), u"user2 updated thread_12 last, so it's read for user2")  # doit être lu par user2 seulement
        self.assertTrue(thread_12.set_closed(None, self.user4), u"user4 is staff and should be able to open/close any thread, anytime")  # état prévu : ouvert
        # Blacklists
        blacklisted = Blocklist.objects.enlist(self.user1, self.user2)  # empêcher user2 de répondre à user1
        self.assertTrue(blacklisted, u"user2 should be blacklisted by user1")
        self.assertFalse(Thread.objects.simulate(self.user1, [self.user2]), u"simulation of sending message should fail")
        self.assertRaises(PermissionDenied, thread_12.add_message, self.user2, u"user2 is blacklisted and cannot answer to user1")
        # Vérifier les limites de basculement d'un sujet
        closed = thread_12.set_closed(None, self.user1)
        self.assertFalse(closed, u"The thread cannot be closed by user1 because it's too new")
        closed = thread_12.set_closed(True, self.user4)
        self.assertTrue(closed, u"The thread should have been closed by user4/staff")
        opened = thread_12.set_closed(False, self.user4)
        self.assertTrue(opened, u"The thread should have been opened by user4/staff")
        # Tester l'émission de courrier'
        unsent = MailEvent.objects.get_unsent_count()
        sent = MailEvent.objects.process('all', True)
        remaining = MailEvent.objects.get_unsent_count()
        self.assertGreater(unsent, 0, "at least one new mail should be waiting in the queue")
        self.assertGreater(sent, 0, "at least one new mail should have been sent")
        self.assertGreater(unsent, remaining, "there should remain less mails to be sent")

    def test_quota(self):
        """ Tester les quotas """
        self.assertFalse(Quota.objects.exceeded_for(self.user1), u"user1 has only sent 1 mail, quota not exceeded")

    def test_negotiations(self):
        """ Tester les négociations """
        Negotiation.objects.negotiate(self.user3, self.user4)
        self.assertIsNone(Negotiation.objects.accept(self.user4, self.user3), "user4 has never made a request to user3")
        state = Negotiation.objects.accept(self.user3, self.user4)
        self.assertIsNotNone(state, "the negotiation between user3 and user4 should have returned something")
        threads = [result[1] for result in state if isinstance(result[1], Thread)]
        self.assertFalse(threads == [], "the return of the negotiation signals should have returned at least one thread between user3 and user4")
