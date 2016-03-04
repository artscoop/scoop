# coding: utf-8
from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from scoop.core.models.redirection import Redirection
from scoop.core.templatetags.datetime_tags import days_from_now as tt_days_from_now
from scoop.core.templatetags.datetime_tags import is_date_new as tt_is_new
from scoop.core.templatetags.html_tags import html_urlize as tt_html_urlize
from scoop.core.templatetags.html_tags import linebreaks_convert as tt_linebreaks
from scoop.core.templatetags.html_tags import sanitize as tt_sanitize
from scoop.core.templatetags.html_tags import tags_keep as tt_tags_keep
from scoop.core.util.django.testing import TEST_CONFIGURATION
from scoop.core.util.stream.request import default_request
from scoop.core.util.stream.urlutil import add_get_parameter, get_url_path, remove_get_parameter, unquote_url
from scoop.user.models.user import User


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
        # self.assertEqual(remove_get_parameter('http://a.com/a?name=11', 'name'), 'http://a.com/a')
        # self.assertEqual(remove_get_parameter('http://a.com/a?name=11', 'code'), 'http://a.com/a?name=11')

        # Aouter un paramètre GET
        # self.assertEqual(add_get_parameter('http://a.com/a', 'name', '11'), 'http://a.com/a?name=11')

    def test_urlutil_breadcrumb(self):
        # Ajouter un breadcrum à une requête
        pass
