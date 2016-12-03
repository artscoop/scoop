# coding: utf-8
from django.db.models.base import Model
from django.http.request import HttpRequest
from django.test import TestCase
from django.test.utils import override_settings
from scoop.core.util.django.testing import TEST_CONFIGURATION


@override_settings(**TEST_CONFIGURATION)
class MonkeyPatchingTest(TestCase):
    """ Test des utilitaires URL """

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_httprequest_patch(self):
        # Nom de fichier d'une URL
        self.assertTrue(hasattr(HttpRequest, 'get_ip'))
        self.assertTrue(hasattr(HttpRequest, 'form'))
        try:
            self.assertTrue(callable(HttpRequest.form))
        except (AttributeError, ValueError):
            self.fail("HttpRequest devrait avoir une méthode form().")

    def test_model_patch(self):
        # Nom de fichier d'une URL
        self.assertTrue(hasattr(Model, 'update'))
