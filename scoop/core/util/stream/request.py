# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.template.context import RequestContext
from django.template.defaultfilters import slugify

from scoop.core.util.django import formutil


class RequestMixin:
    """
    Opérations sur l'objet HttpRequest destinées à l'usage avec plusieurs
    applications. Principalement, l'objectif de l'utilitaire est de manipuler
    IP ou autres éléments de requête HTTP.
    :type RequestMixin: django.http.HttpRequest
    """
    # Constantes
    CHECKS = ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
    METACOPY = ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR', 'REMOTE_HOST', 'SERVER_NAME', 'SERVER_PORT', 'LANG', 'LANGUAGE', 'HTTP_REFERER',
                'CONTENT_LENGTH', 'CONTENT_TYPE', 'HTTP_HOST', 'HTTP_USER_AGENT', 'REMOTE_USER', 'REQUEST_METHOD']
    POST_CACHE_KEY = "post.data.%(user)s.%(name)s"

    # Getter
    def get_ip(self):
        """
        Renvoyer l'adresse IP de la requête, au format texte
        :type self: django.http.HttpRequest
        """
        for entry in RequestMixin.CHECKS:
            if self.META.get(entry, False):
                return self.META[entry]
        return '-'

    def get_referrer(self):
        """
        Renvoyer le référent
        :type self: django.http.HttpRequest
        """
        return self.META.get('HTTP_REFERER', "")

    def is_referrer_external(self):
        """ Renvoyer si le référent est externe au site """
        return not self.get_referrer().startswith(getattr(settings, 'DOMAIN_NAME', '--'))

    def get_reverse(self):
        """ Renvoyer le reverse de l'IP de la requête """
        from scoop.user.access.util.access import reverse_lookup
        # Renvoyer le reverse
        ipstr = self.get_ip()
        return reverse_lookup(ipstr)

    def get_geoip(self):
        if getattr(self, 'geoip', None) is None:
            from scoop.user.access.models import IP
            # Renvoyer les infos GeoIP
            ip = IP.objects.get_by_ip(self.get_ip())
            geoip = ip.get_geoip()
            self.geoip = geoip
        return self.geoip

    def get_city(self):
        """ Renvoyer la ville présumée de la requête """
        from scoop.location.models import City
        # Renvoyer la ville
        geoip = self.get_geoip()
        if geoip is None:
            return None
        latitude = geoip['latitude']
        longitude = geoip['longitude']
        cityname = geoip['city']
        # Trouver la ville alentours au bon nom
        city = City.objects.find_by_name([latitude, longitude], cityname)
        return city

    def list_to_queryset(self, attribute, base_queryset, qs_att='pk', conversion=int):
        """
        Renvoyer un queryset filtré par les valeurs d'un attribut POST
        :type self: django.http.HttpRequest
        """
        if attribute in self.REQUEST:
            values = getattr(self, 'REQUEST').getlist(attribute)
            values = [conversion(value) for value in values]
            filtering = {'{}__in'.format(qs_att): values}
            return base_queryset.filter(**filtering)
        return []

    def has_post(self, action=None):
        """ Renvoyer si la requête a une action dans POST """
        return formutil.has_post(self, action)

    def form(self, config, initial=None):
        """ Créer un ou plusieurs formulaires selon l'état de la requête """
        return formutil.form(self, config, initial=initial)

    def get_id_selection(self, full, selected):
        """
        Renvoyer une liste d'ID cochés et décochés depuis des données POST
        :param full: liste des champs hidden
        :param selected: liste des cases à cocher sélectionnées
        :type self: django.http.HttpRequest
        """
        full_set = set([int(i) for i in self.POST.getlist(full)])
        selected_set = set([int(i) for i in self.POST.getlist(selected)])
        unselected_set = full_set - selected_set
        return {'selected': selected_set, 'unselected': unselected_set}

    def save_post(self, name):
        """
        Sauvegarder des données POST pour un utilisateur et un nom
        :type self: django.http.HttpRequest, RequestMixin
        """
        key = self.POST_CACHE_KEY % {'user': self.user.id, 'name': slugify(name)}
        cache.set(key, self.POST, 2592000)

    def load_post(self, name):
        """ Récupérer des données POST en cache, pour un utilisateur et un nom """
        key = self.POST_CACHE_KEY % {'user': self.user.id, 'name': slugify(name)}
        return cache.get(key, dict())

    def __reduce__(self):
        """
        Préparer l'objet au pickling
        :type self: django.http.HttpRequest
        """
        if hasattr(self, 'user'):
            self.user = self.user._wrapped if hasattr(self.user, '_wrapped') else self.user  # Depuis Django 1.8, user est un LazyObject qui ne peut être picklé en l'état.
        meta = {k: self.META[k] for k in RequestMixin.METACOPY if k in self.META and isinstance(self.META[k], str)}

        return (HttpRequest, (), {'META': meta, 'POST': self.POST, 'GET': self.GET, 'user': getattr(self, 'user', None),
                                  'path': self.path, 'scheme': self.scheme, 'path_info': self.path_info,
                                  'method': self.method, 'encoding': self.encoding
                                  })


SIMPLE_META = {'REMOTE_ADDR': '127.0.0.1', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': 80, 'REQUEST_METHOD': 'GET'}


def default_request():
    """ Créer une requête par défaut """
    request = HttpRequest()
    request.META.update(SIMPLE_META)
    return request


def default_context():
    """ Contexte de requête par défaut """
    return RequestContext(default_request())


def save_post_data(name):
    """ Décorateur de vue, sauvegarde automatiquement les données POST """

    def wrapper(method):
        def wrapped(*args, **kwargs):
            request = args[0]
            if request.has_post():
                request.save_post(name)
            return method(*args, **kwargs)

        wrapped.__doc__ = method.__doc__
        wrapped.__name__ = method.__name__
        return wrapped

    return wrapper
