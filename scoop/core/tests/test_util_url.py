# coding: utf-8

from django.test import TestCase
from django.test.utils import override_settings

from scoop.core.util.django.testing import TEST_CONFIGURATION
from scoop.core.util.stream.urlutil import get_url_path, change_url_parameters, unquote_url


@override_settings(**TEST_CONFIGURATION)
class URLUtilityTest(TestCase):
    """ Test des utilitaires URL """

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_urlutil(self):
        # Nom de fichier d'une URL
        self.assertEqual(get_url_path('http://pal.com/konami.html'), 'konami.html')
        self.assertEqual(get_url_path('http://sélénium.com/ébène.html'), 'ébène.html')

        # Déquoter une URL
        self.assertEqual(unquote_url('http://a.com/the%20end'), 'http://a.com/the end')

        # Enlever le paramtre GET
        self.assertEqual(change_url_parameters('http://a.com/a?name=11', 'name'), 'http://a.com/a')
        self.assertEqual(change_url_parameters('http://a.com/a?name=11', 'code'), 'http://a.com/a?name=11')

        # Aouter un paramètre GET
        self.assertEqual(change_url_parameters('http://a.com/a', name='11'), 'http://a.com/a?name=11')

    def test_urlutil_breadcrumb(self):
        # Ajouter un breadcrum à une requête
        pass
