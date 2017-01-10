# coding: utf-8
from importlib import import_module
from random import choice

from django.conf import settings
from django.test import TestCase
from scoop.rogue.models.ipblock import IPBlock
from scoop.rogue.util.ipblock import PROXY_LIST_DIRECTORY, get_proxy_nodes
from scoop.user.access.models.ip import IP
from scoop.user.models.user import User


class IPBlockTest(TestCase):
    """ Test des blocages d'adresses IP """

    # Configuration
    fixtures = ['category', 'mailtype', 'options']

    @classmethod
    def setUp(self):
        """ Définir l'environnement de test """
        self.engine = import_module(settings.SESSION_ENGINE)
        self.session = self.engine.SessionStore()
        self.user = User.objects.create(username='commentuser', email='foo@foobar1.foo')
        self.user.set_password('commentuser')
        self.user.save()

    def test_ipblock_detection(self):
        """ Tester que des IPs saines et bloquées sont détectées correctement """
        proxy_node = choice(list(get_proxy_nodes(PROXY_LIST_DIRECTORY)))
        self.assertTrue(IPBlock.objects.get_ip_status(IP.objects.get_by_ip(proxy_node))['blocked'], "The IP {} should be blocked.".format(proxy_node))
        localhost = IP.objects.get_by_ip('127.0.0.1')
        self.assertFalse(IPBlock.objects.get_ip_status(localhost)['blocked'], "The IP {} should always be allowed.".format(localhost))
        IPBlock.objects.block_ips('127.0.0.1')  # Même si l'IP est bloquée, elle est toujours considérée safe normalement
        self.assertFalse(IPBlock.objects.get_ip_status(localhost)['blocked'], "The IP {} should be protected here.".format(localhost))

    def test_ipblock_host_regex(self):
        """ Tester le blocage d'IP """
        ipblock = IPBlock.objects.block_reverse(r'^host.*', regex=True)
        ip1 = IP.objects.create(string="1.2.3.4", ip=1, reverse="hostodyssey.com")  # bloqué
        ip2 = IP.objects.create(string="1.2.3.5", ip=2, reverse="lostodyssey.com")  # non bloqué
        self.assertTrue(IPBlock.objects.get_ip_status(ip1)['blocked'])
        self.assertEqual(IPBlock.objects.get_ip_status(ip1)['type'], IPBlock.HOST_REGEX)
        self.assertFalse(IPBlock.objects.get_ip_status(ip2)['blocked'])
        self.assertEqual(ipblock.get_blocked_ip_set().count(), 1)
