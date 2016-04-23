# coding: utf-8
import socket

from dns import resolver as dnsresolver
from dns import reversename

from django.core.cache import cache
from django.utils.lru_cache import lru_cache
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.data.dateutil import now

# Codes de statut de résolution
STATUS = {'ok': 0, 'timeout': 1, 'noanswer': 2, 'nonameservers': 3, 'nxdomain': 4}
STATUS_CHOICES = [
    [STATUS['ok'], _("Ok")],
    [STATUS['timeout'], _("Timed out")],
    [STATUS['noanswer'], _("Empty answer")],
    [STATUS['nonameservers'], _("Broken NS")],
    [STATUS['nxdomain'], _("Domain not found")]
]


def reverse_lookup(ip):
    """
    Résoudre une adresse IP en son nom inversé.

    @requires: dnspython3
    @param ip: chaîne de type A.B.C.D
    @return: dictionnaire aux clés "name" et "status"
    """
    address = reversename.from_address(ip)
    resolver = dnsresolver.Resolver()
    # Configurer le resolver
    resolver.timeout = 2.0  # par serveur dns
    resolver.lifetime = 6.0  # timeout total
    # Demander le RRSet PTR, renvoyer timeout si timeout
    try:
        ptr_rrset = resolver.query(address, 'PTR').rrset
    except dnsresolver.Timeout:
        return {'name': '', 'status': STATUS['timeout']}
    except dnsresolver.NoAnswer:
        return {'name': '', 'status': STATUS['noanswer']}
    except dnsresolver.NoNameservers:
        return {'name': '', 'status': STATUS['nonameservers']}
    except dnsresolver.NXDOMAIN:
        return {'name': '', 'status': STATUS['nxdomain']}
    # Un Resource Record Set est normalement renseigné
    if len(ptr_rrset) > 0:
        return {'name': ptr_rrset[0].to_text(), 'status': STATUS['ok']}
    # Ce cas ne devrait jamais être atteint
    return {'name': '', 'status': 99}


@lru_cache(16)
def get_local_ip():
    """
    Récupérer l'IP locale, normalement autre que 127.0.0.1

    via l'interface qui permet d'atteindre le DNS Google, à l'IP 8.8.8.8
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()
    s.close()
    return ip[0] if isinstance(ip, tuple) else ip


class VisitorIPManager(object):
    """ Gestionnaire d'accès par IP récents """

    def get_ip_list(self):
        """
        Récupérer la liste des IPs

        @return: dictionnaire à clés IP dont la valeur est un timestamp
        """
        return cache.get('access.visitor.ip', dict())

    def set_ip_list(self, data):
        """
        Définir la liste des IPs visiteurs

        @param data: liste d'IPs au format décimal
        """
        cache.set('access.visitor.ip', data or dict)

    def add(self, request):
        """
        Ajouter une entrée à la liste d'accès par IP

        @param request: objet HttpRequest avec une IP valide
        """
        state = self.get_ip_list()
        state[request.get_ip()] = now()
        self.set_ip_list(state)

    def clean(self, minutes=60):
        """
        Nettoyer les entrées plus anciennes que n minutes

        @param minutes: ancienneté minimum en minutes
        """
        limit = now() - minutes * 60
        state = self.get_ip_list()
        for key in state:
            if state[key] < limit:
                del state[key]
        self.set_ip_list(state)
