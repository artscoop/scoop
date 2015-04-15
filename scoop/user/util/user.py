# coding: utf-8
from __future__ import absolute_import

from collections import Counter

import Levenshtein
from django.contrib.auth import get_user_model

__all__ = ['get_user_email_domains', 'replace_user_email_domains', 'find_similar_email_domains']


def get_user_email_domains(count=256):
    """
    Renvoyer tous les noms de domaine utilisés pour les emails de la base
    :returns: un tuple de tuples (ndd, occurrences) trié dans l'ordre décroissant d'apparition
    """
    users = get_user_model().objects.active()
    domains = [email.split('@')[1].strip().lower() for email in users.values_list('email', flat=True)]
    return Counter(domains).most_common(count) if count is not None else Counter(domains)


def replace_user_email_domains(source, destination):
    """ Remplacer un NDD d'email pour tous les utilisateurs par un autre """
    source = source.lower().strip()
    destination = destination.lower().strip()
    users = get_user_model().objects.active().filter(email__icontains=u'@{}'.format(source))
    for user in users:
        user.email = user.email.replace(u'@{}'.format(source), u'@{}'.format(destination))
        user.save(update_fields=['email'])
    return True


def _get_splitted(name):
    """ Renvoyer un NDD splitté """
    names = unicode(name).lower().split(u'.', 1)
    while len(names) < 2:
        names.append(u'')
    return names


def _get_distance(source, destination):
    """
    Renvoyer les distances levenshtein entre un NDD et un autre
    :returns: un tuple de type (int, int), avec la distance entre les NDD de niveau 2 et 1
    """
    nd_source, tld_source = _get_splitted(source)
    nd_destination, tld_destination = _get_splitted(destination)
    distance_nd = Levenshtein.distance(nd_source, nd_destination)
    distance_tld = Levenshtein.distance(tld_source, tld_destination)
    return (distance_nd, distance_tld)


def find_similar_email_domains(source, max_distance=None):
    """
    Renvoyer les noms de domaine connus les plus ressemblants
    :param max_distance: tuple d'entiers de distance lenvenshtein max (ndd, tld)
    """
    if max_distance is None:
        max_distance = (len(_get_splitted(source)[0]) / 2, 3)
    domains = map(lambda i: i[0], get_user_email_domains(count=None))
    similarities = {domain: _get_distance(source, domain) for domain in domains}.items()
    filtered_similarities = [similarity for similarity in similarities if similarity[1][0] <= max_distance[0] and similarity[1][1] <= max_distance[1]]
    return sorted(filtered_similarities, key=lambda x: x[1])
