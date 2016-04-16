# coding: utf-8

from django.test import TestCase

from scoop.user.access.models.ip import IP


class IPTest(TestCase):
    """ Test des visites de profils """

    # Tests
    def test_ip(self):
        """ Vérifier que le modèle IP fonctionne normalement """
        # Tester l'évaluation des adresses IP'
        self.assertEqual(IP.get_ip_value('32,10'), 0)
        self.assertEqual(IP.get_ip_value('0'), 0)
        self.assertEqual(IP.get_ip_value('19'), IP.get_ip_value('19.0.0.0'))
        self.assertEqual(IP.get_ip_value('256'), 256)
        self.assertEqual(IP.get_ip_value('25600'), 25600)
