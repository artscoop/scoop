# coding: utf-8

from django.test import TestCase

from scoop.menus.elements.item import Item


class MenuTest(TestCase):
    """ Test des menus """
    
    fixtures = []

    def setUp(self):
        """ Préparer l'environnement de test """
        pass

    # Tests
    def test_menu_item(self):
        """ Tester les éléments de menu """
        menu = Item(label="Home", identifier="home", target="/")
        self.assertEqual(menu.get_absolute_url(), "/")
        self.assertEqual(menu.get_html_id(), 'menu-id-home')
        self.assertEqual(menu.get_label(), "Home")
