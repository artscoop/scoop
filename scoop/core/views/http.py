# coding: utf-8
from __future__ import absolute_import

import sys

from django.conf import settings
from django.views.decorators.cache import cache_page

from scoop.core.util.django.templateutil import render_to


@render_to("http/500.html", status_code=500)
def http_500(request, template_name='http/500.html'):
    """ Rendre la page d'erreur serveur """
    # Récupérer tous les attributs de settings
    attributes, template_dict = dir(settings), {'request': request}
    # Créer un dictionnaire contenant les attributs écrits en Majuscules
    template_dict['settings'] = [[attribute, getattr(settings, attribute)] for attribute in attributes if attribute == attribute.upper()]
    for item in template_dict['settings']:
        if any(word in item[0] for word in {'PASSWORD', 'KEY', 'SECRET', 'PRIVATE', 'PUBLIC', 'DATABASES'}):
            item[1] = "* private *"
    context_dict = {'exception': sys.exc_info(), 'exception_type': sys.exc_info()[1].__class__.__name__, 'settings_data': sorted(template_dict['settings'])}
    return context_dict


@cache_page(3600)
@render_to("http/503.html", status_code=503)
def http_503(request):
    """ Rendre la page de maintenance """
    return {}


@cache_page(60)
@render_to("http/404.html", status_code=404)
def http_404(request):
    """ Rendre la page HTTP 404 """
    return {}


@render_to("http/410.html", status_code=410)
def http_410(request):
    """ Rendre la page HTTP 410 """
    return {}


@render_to("http/robots.txt", content_type='text/plain')
def robots_txt(request):
    """ Rendre le fichier robots.txt """
    return {}
