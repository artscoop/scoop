# coding: utf-8
from __future__ import absolute_import

import math
from random import shuffle
from xmlrpclib import Server

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from scoop.core.util.signals import ping_failed

# Liste de moteurs de Ping de sitemap ou RSS
PING_ENGINES = [
    "http://rpc.pingomatic.com", "http://rpc.twingly.com", "http://api.feedster.com/ping",
    "http://api.moreover.com/RPC2", "http://api.moreover.com/ping", "http://www.blogdigger.com/RPC2",
    "http://www.blogshares.com/rpc.php", "http://www.blogsnow.com/ping",
    "http://www.blogstreet.com/xrbin/xmlrpc.cgi", "http://bulkfeeds.net/rpc",
    "http://www.newsisfree.com/xmlrpctest.php", "http://ping.blo.gs/", "http://ping.feedburner.com",
    "http://ping.syndic8.com/xmlrpc.php", "http://ping.weblogalot.com/rpc.php",
    "http://rpc.blogrolling.com/pinger/", "http://rpc.technorati.com/rpc/ping",
    "http://rpc.weblogs.com/RPC2", "http://www.feedsubmitter.com", "http://blo.gs/ping.php",
    "http://www.pingerati.net", "http://www.pingmyblog.com", "http://geourl.org/ping",
    "http://ipings.com", "http://www.weblogalot.com/ping"
]


def ping_feed(url_name, args=None, kwargs=None, percent=25):
    """
    Ping des moteurs
    - ping aux services XML-RPC de blogs
    - envoie l'adresse du flux
    - utilise <percent>% de moteurs dans la liste de moteurs
    """
    # Récupérer le chemin depuis le nom d'URL
    path = reverse(url_name, args or [], kwargs or {})
    domain = Site.objects.get_current().domain
    full_path = "%(domain)s%(path)s" % {'domain': domain, 'path': path}
    # Récupérer une liste de percent% des moteurs
    shuffle(PING_ENGINES)
    count = math.ceil(percent * len(PING_ENGINES) / 100.0)
    selected = PING_ENGINES[0:int(count)]
    # Pinger chacun des moteurs choisis
    for url in selected:
        try:
            engine = Server(url)
            result = engine.weblogUpdates.ping(full_path)
        except:
            ping_failed.send(None, engine=url, feed=full_path)
    return result
