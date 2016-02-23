# coding: utf-8
from datetime import datetime

from django.test import TestCase
from django.test.utils import override_settings

from scoop.core.util.data.dateutil import date_age
from scoop.core.util.data.numbers import round_left
from scoop.core.util.data.textutil import text_to_list_of_lists, text_to_dict, one_line, replace_dict, count_words
from scoop.core.util.data.typeutil import str_to, make_iterable, closest_color
from scoop.core.util.django.testing import TEST_CONFIGURATION


@override_settings(**TEST_CONFIGURATION)
class DataUtilityTest(TestCase):
    """ Test des utilitaires URL """

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_dateutil(self):
        year = datetime.now().year
        past_date = datetime(year - 4, 1, 1)
        # Tester que la fonction renvoie bien 4 pour une date antérieure de 4 ans
        self.assertEqual(date_age(past_date), 4)

    def test_numbers(self):
        # Vérifier l'arrondi des nombres décimaux
        self.assertEqual(round_left(3.14159, 2), 3.1)
        self.assertEqual(round_left(3.14159, 1), 3)
        self.assertEqual(round_left(3.5, 1), 4)
        self.assertEqual(round_left(1234, 2), 1200)
        self.assertEqual(round_left(1256, 2), 1300)

    def test_textutil(self):
        # Vérifier la conversion texte → liste de listes/dictionnaire
        self.assertEqual(text_to_list_of_lists("a:1\nb\nc:2"), [['a', '1'], ['b'], ['c', '2']])
        self.assertEqual(text_to_list_of_lists("\n"), [[""]])
        self.assertEqual(text_to_dict("a:1 \n b:2 \n #Comment", evaluate=True), {'a': 1, 'b': 2})
        self.assertEqual(text_to_dict("a:1 \n b:2 \n #Ignored", evaluate=False), {'a': '1', 'b': '2'})

        # Tester le one-liner
        self.assertEqual(one_line("la\nla\nla\nla\n"), "la la la la")

        # Tester les remplacements
        self.assertEqual(replace_dict("Cyrano de Bergerac", {'Cyrano': "Olivier", "Bergerac": "Kersauzon"}), "Olivier de Kersauzon")

        # Tester le décompte de mots
        self.assertEqual(count_words("Cyrano de Bergerac"), 3)
        self.assertEqual(count_words("<span>Cyrano<span> <p>de Bergerac</p>", html=False), 7)  # span Cyrano span p de Bergerac p
        self.assertEqual(count_words("<span>Cyrano<span> <p>de Bergerac</p>", html=True), 3)  # Cyrano de Bergerac

    def test_typeutil(self):
        # Tester la conversion de chaîne à un autre type
        self.assertEqual(str_to("c", int), 0)
        self.assertEqual(str_to("9", int), 9)

        # Tester make_iterable
        self.assertEqual(make_iterable(None), [])
        self.assertEqual(make_iterable([1, 2, 3], tuple), (1, 2, 3))

        # Tester les noms de couleur
        self.assertIn(closest_color((0, 255, 255)), ('aqua', 'cyan'))
