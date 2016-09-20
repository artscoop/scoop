# coding: utf-8
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest
from django.template.context import RequestContext
from django.template.defaultfilters import slugify
from scoop.core.util.django import formutil
from scoop.core.util.django.apps import is_installed


class RequestMixin(object):
    """
    Opérations sur l'objet HttpRequest

    Principalement, l'objectif de l'utilitaire est de manipuler
    IP ou autres éléments de requête HTTP.
    Monkey-patching done in scoop.core.__init__
    :type RequestMixin: django.http.HttpRequest
    """

    # Constantes
    CHECKS = ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']
    PICKLABLE_META = ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR', 'REMOTE_HOST', 'SERVER_NAME', 'SERVER_PORT', 'LANG', 'LANGUAGE', 'HTTP_REFERER',
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
        if is_installed('scoop.location'):
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
        return None

    def list_to_queryset(self, post_param, base_queryset, attribute='pk', conversion=int):
        """
        Renvoyer un queryset filtré par les valeurs d'un attribut POST/GET

        :type self: django.http.HttpRequest
        :param post_param: nom du paramètre POST/GET contenant une liste d'identifiants
        :param base_queryset: queryset de base
        :param attribute: nom de l'attribut de modèle à filtrer par la liste d'identifiants <post_param>
        :param conversion: type vers lequel convertir les identifiants de la liste (depuis str)
        :type post_param: str
        :type base_queryset: django.db.models.Queryset
        :type attribute: str
        :type conversion: type
        """
        if post_param in self.POST:
            values = self.POST.getlist(post_param)
            values = [conversion(value) for value in values]
            filtering = {'{}__in'.format(attribute): values}
            return base_queryset.filter(**filtering)
        return []

    def has_post(self, action=None):
        """ Renvoyer si la requête possède un attribut dans POST """
        return formutil.has_post(self, action)

    def form(self, config, initial=None):
        """
        Créer un ou plusieurs formulaires selon l'état de la requête

        Si la méthode de requete est POST, générer les formulaires depuis les données POST.
        Si la méthode de requete est GET, générer les formulaires par défaut.
        """
        return formutil.form(self, config, initial=initial)

    def get_id_selection(self, full, selected):
        """
        Renvoyer une liste d'ID cochés et décochés depuis des données POST

        La méthode fonctionne si le formulaire contient pour chaque entrée :
        - un champ caché (cela permet de recenser aussi bien les éléments cochés que non)
        - un champ checkbox (seuls les éléments cochés sont passés via POST)
        :param full: attribut POST contenant la liste des champs hidden
        :param selected: attribut POST contenant la liste des cases cochées
        :type self: django.http.HttpRequest |
        :type full: str | MultiValueDict
        :type selected: str | MultiValueDict
        """
        full_set = set([i for i in self.POST.getlist(full)])
        selected_set = set([i for i in self.POST.getlist(selected)])
        unselected_set = full_set - selected_set
        return {'selected': selected_set, 'unselected': unselected_set}

    def save_post(self, name):
        """
        Sauvegarder des données POST pour l'utilisateur courant

        avec un nom d'enregistrement.
        :type self: django.http.HttpRequest, RequestMixin
        :param name: nom du slot des données POST
        """
        key = self.POST_CACHE_KEY % {'user': self.user.id, 'name': slugify(name)}
        cache.set(key, self.POST, 2592000)

    def load_post(self, name):
        """
        Charger des données POST en cache, pour l'utilisateur courant

        et avec le nom d'enregistrement spécifié
        """
        key = self.POST_CACHE_KEY % {'user': self.user.id, 'name': slugify(name)}
        return cache.get(key, dict())

    def __reduce__(self):
        """
        Préparer l'objet au pickling

        :type self: django.http.HttpRequest
        """
        if hasattr(self, 'user'):
            # Depuis Django 1.8, user est un LazyObject qui ne peut être picklé en l'état.
            self.user = self.user._wrapped if hasattr(self.user, '_wrapped') else self.user
        meta = {k: self.META[k] for k in RequestMixin.PICKLABLE_META if k in self.META and isinstance(self.META[k], str)}
        return (HttpRequest, (), {'META': meta, 'POST': self.POST, 'GET': self.GET, 'user': getattr(self, 'user', None),
                                  'path': self.path, 'scheme': self.scheme, 'path_info': self.path_info,
                                  'method': self.method, 'encoding': self.encoding
                                  })


SIMPLE_META = {'REMOTE_ADDR': '127.0.0.1', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': 80, 'REQUEST_METHOD': 'GET'}


@lru_cache()
def default_request():
    """ Créer une requête par défaut """
    request = HttpRequest()
    request.META.update(SIMPLE_META)
    return request


def default_context():
    """
    Contexte de requête par défaut

    Renvoie un contexte de template tel qu'on le trouve dans une vue standard.
    Contient les clés de contexte définies par les CONTEXT_PROCESSORS et MIDDLEWARE
    L'IP de requête pour le contexte est 127.0.0.1
    """
    return RequestContext(default_request())


def save_post_data(name):
    """
    Décorateur de vue, sauvegarde automatiquement les données POST

    see RequestMixin.save_post
    """

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
