# coding: utf-8
from __future__ import absolute_import

import re
from os import listdir
from os.path import isfile, join

import requests
from django.core.cache import cache

from scoop.core.util.stream.directory import Paths

PROXY_LIST_DIRECTORY = Paths.get_root_dir('isolated', 'database', 'rogue', 'proxies')


def get_tor_nodes(path='http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv'):
    """
    Charger la liste de nœuds pour le réseau TOR
    L'URL de la liste peut changer au cours du temps
    - 30.01.2013 : https://www.dan.me.uk/torlist/ (inaccessible via urllib)
    - 07.06.2014 : http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv
    """
    # Renvoyer la liste mise en cache si existante
    cached = cache.get('rogue.torlist', None)
    if cached is not None:
        return cached
    # Sinon, mettre le fichier distant en cache
    try:
        data = requests.get(path)
        results = frozenset([row.strip() for row in data.content.split('\n') if row.strip()])
        cache.set('rogue.torlist', results, timeout=86400 * 3)
    except:
        results = frozenset()
        cache.set('rogue.torlist', results, timeout=3600 * 3)
    return results


def is_tor_node(ip_string):
    """ Renvoyer si une IP est un nœud Tor """
    return ip_string in get_tor_nodes()


def get_proxy_nodes(directory='/'):
    """
    Charger une liste de nœuds proxy
    La fonction cherche tous les fichiers texte du répertoire passé
    et en extrait les IPs, permettant l'agrégation de plusieurs listes.
    Sites proposant des listes de proxy :
    - gatherproxy.com : marceddie@get2mail.fr - hrl*R)}9 (expire le 2016.04.13)
    """
    # Renvoyer la liste mise en cache si existante
    cached = cache.get('rogue.proxylist', None)
    if cached is not None:
        return cached
    # Définir les fichiers de listes à charger
    paths = [join(directory, f) for f in listdir(directory) if f.endswith('.txt') and isfile(join(directory, f))]
    # Liste des IPs répertoriées
    ip_set = set()
    # Parcourir les données
    for path in paths:
        data = open(path).read()
        ip_list = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", data)
        ip_set.update(ip_list)
    cache.set('rogue.proxylist', ip_set, timeout=86400 * 3)
    return ip_set


def is_proxy_node(ip_string):
    """ Renvoyer si une IP est un nœud Proxy """
    return ip_string in get_proxy_nodes(PROXY_LIST_DIRECTORY)


def is_relay_node(ip_string):
    """ Renvoyer si une IP est un nœud Tor ou un Proxy """
    return is_proxy_node(ip_string) or is_tor_node(ip_string)
