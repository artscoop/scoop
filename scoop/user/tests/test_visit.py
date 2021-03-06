# coding: utf-8
from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from scoop.user.models import Visit

User = get_user_model()


class VisitTest(TestCase):
    """ Test des visites de profils """
    fixtures = ['mailtype', 'options']

    def setUp(self):
        """ Préparer l'environnement detest """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user1 = User.objects.create(username='anita', email='anita@foobar.foo')
        self.user2 = User.objects.create(username='benny', email='benny@foobar.foo')
        self.user3 = User.objects.create(username='carla', email='carla@foobar.foo')
        self.user4 = User.objects.create(username='david', email='david@foobar.foo')
        self.v1 = Visit.objects.new(self.user1, self.user2)
        self.v2 = Visit.objects.new(self.user1, self.user3)
        self.v3 = Visit.objects.new(self.user1, self.user4)
        self.v4 = Visit.objects.new(self.user2, self.user3)
        self.v5 = Visit.objects.new(self.user3, self.user1)
        self.v6 = Visit.objects.new(self.user3, self.user4)
        self.v7 = Visit.objects.new(self.user4, self.user1)
        self.v8 = Visit.objects.new(self.user4, self.user4)  # Aucun effet, renvoie False
        self.v9 = Visit.objects.new(self.user3, self.user3)  # Aucun effet, renvoie False
        self.v10 = Visit.objects.new(self.user3, self.user1)  # Doublon, update de v5, renvoie True

    # Tests
    def test_visits(self):
        """ Vérifier que la création de visites fonctionne normalement """
        # Tester l'état de création des visites
        self.assertTrue(self.v1, "visit should be valid and created")
        self.assertTrue(self.v5, "visit should be valid and created")
        self.assertFalse(self.v8, "visit should be invalid")
        # Tester leur nombre
        self.assertEqual(Visit.objects.count(), 7, "only 7 visit records should have been created")
        # Puis effacer les visites à user1 (2)
        Visit.objects.wipe_visitee(self.user1)
        # Vérifier qu'il ne reste que 5 enregistrements
        self.assertEqual(Visit.objects.count(), 5, "only 5 visit records should remain")
        # Vérifier que les utilisateurs récupérés depuis by_user(as_users=True) ont un attribut "when"
        try:
            users = Visit.objects.by_user(self.user1, as_users=True)
            [user.when for user in users]
        except (AttributeError, ValueError):
            self.fail("Les utilisateurs devraient posséder un attribut 'when'.")

    def test_consistency(self):
        """ Vérifier l'état des visites """
        self.assertEqual(self.v10, self.v5)
        self.assertIsInstance(self.v5, Visit)
        self.assertIsInstance(self.v10, Visit)
