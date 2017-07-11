# coding: utf-8

from django.test import TestCase
from django.test.utils import override_settings

from scoop.core.util.django.testing import TEST_CONFIGURATION
from scoop.core.util.shortcuts import get_languages


@override_settings(**TEST_CONFIGURATION)
class ShortcutUtilityTest(TestCase):
    """ Test des utilitaires de raccourcis """

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_language_shortcuts(self):
        languages = get_languages()
        self.assertTrue(all([code == code.lower() for code in languages]))
