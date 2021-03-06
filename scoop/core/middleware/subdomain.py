# coding: utf-8
import re

from django.conf import settings

from scoop.core.util.django.middleware import MiddlewareBase


class SubdomainsMiddleware(MiddlewareBase):
    """
    Middleware qui remplace complètement la Root URL configuration

    selon le nom de sous-domaine actuel.
    La liste des sous-domaines est décrite dans settings.SUBDOMAINS.
    Le fichier URLconf à utiliser pour chaque sous-domaine de la liste se trouve
    à settings.urlconf.<nom du sous-domaine>
    IMPORTANT : settings.SESSION_COOKIE_DOMAIN doit débuter par un point
    si vous souhaitez conserver les sessions entre les sous-domaines. Ex:
    SESSION_COOKIE_DOMAIN = ".localhost" ou ".domaine.com"
    """

    def __call__(self, request):
        """ Traiter la requête """
        response = self.get_response(request)
        # Récupérer le nom de domaine et les parties du ndd
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        parts = request.domain.split('.')
        # accepte les nnd de la forme sub.dom.ext ou sub.localhost:8000
        if len(parts) == 3 or (re.match("^localhost", parts[-1]) and len(parts) == 2):
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])
        # Remplacer le URL Conf à utiliser selon le nom de sous-domaine
        if request.subdomain in settings.SUBDOMAINS:
            request.urlconf = 'project.settings.urlconf.{name}'.format(name=request.subdomain)
        return response
