# coding: utf-8
from importlib import import_module

from django.conf import settings
from django.test import TestCase
from scoop.core.util.shortcuts import get_languages
from scoop.location.models.city import City
from scoop.location.models.country import Country
from scoop.location.tasks.geonames import geonames_fill
from scoop.location.util.geonames import populate_countries
from scoop.user.models.user import User


class CityTest(TestCase):
    """ Test des villes """
    fixtures = ['mailtype', 'options']

    def setUp(self):
        """ Préparer l'environnement de test """
        # Créer un utilisateur
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='commentuser', email='foo@foobar1.foo')
        self.user.set_password('commentuser')
        self.user.save()

    # Tests
    def test_cities(self):
        """ Tester les villes """
        # Peupler la Belgique
        populate_countries(rename=False)
        countries = Country.objects.filter(code2="BE")
        geonames_fill(countries, rename=False)

        languages = get_languages()
        belgium = countries[0]
        liege = City.objects.find_by_name([50.63, 5.56], "Liège")
        brussels = City.objects.find_by_name([50.85, 4.35], "Brussels")
        italy = Country.objects.get_by_code2_or_none("IT")
        # Tests
        self.assertGreater(belgium.get_entries_count(), 500, "Belgium should have at least 501 locations deemed as cities")
        self.assertEqual(italy.get_entries_count(), 0, "Italy should have no city entry populated.")
        self.assertFalse(belgium.latitude == 0.0, "The median latitude of all cities in Belgium should be set in the country position")
        self.assertTrue(italy.latitude == 0.0, "The latitude of Italy should not be populated and be 0.0")
        self.assertFalse(liege.has_name("4000"), "The postal code 4000 should not be a name of Liège")
        self.assertIn(brussels.type, ["PPLC", "PPL"], "Brussels is a PPL/Capital")

        if 'fr' in languages:
            # Speed up test by skipping translation material
            pass
        if 'en' in languages:
            self.assertTrue(liege.has_name("Liège"), "Liège was expected, got {} instead.".format(liege))
            self.assertTrue(belgium.has_name("Belgium"), "Belgium should have its own english name")
            self.assertTrue(brussels.has_name("Brussels"), "Brussels should have its own english name")
