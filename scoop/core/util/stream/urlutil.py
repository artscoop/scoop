# coding: utf-8
import logging
import os
from _socket import gaierror
from traceback import print_exc
from urllib.error import HTTPError, URLError
from urllib.parse import unquote

import requests

from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
from pip._vendor.requests.packages import urllib3
from unidecode import unidecode

# Constantes
DEFAULT_HEADERS = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/39.0'}


def get_domain():
    """ Renvoyer le nom de domaine courant """
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    return current_site.domain if "/" in current_site.domain else getattr(settings, "DOMAIN_NAME", "")


def get_url_resource(path, **kwargs):
    """ Renvoyer le contenu d'une URL """
    try:
        resource = requests.get(path, headers=DEFAULT_HEADERS, timeout=6.0, allow_redirects=True)
        return resource.text
    except (IOError, OSError, Exception) as e:
        raise URLError("The resource at {path} was unavailable.".format(path=path), path)


def download_url_resource(path, output=None):
    """ Télécharger un fichier à une URL et renvoyer le chemin du fichier local téléchargé """
    if output and os.path.exists(output):
        logging.warning(_("The download destination file at %(path)s already exists. Skipped.") % {'path': output})
        return output
    resource = requests.get(path, headers=DEFAULT_HEADERS, allow_redirects=True, stream=True)
    resource_file = NamedTemporaryFile(delete=False) if output is None else open(output, 'wb')
    for chunk in resource.iter_content(16384):
        resource_file.write(chunk)
    resource_file.close()
    return resource_file.name


def get_url_path(path):
    """ Renvoyer une URL sans paramètres et sans ancre """
    filename = os.path.basename(path).split('?')[0].split('#')[0]
    return filename


def unquote_url(path, transliterate=True):
    """ Renvoyer une URL en décodant les caractères HTML sous forme % """
    filename = unquote(str(path))
    return filename


def remove_get_parameter(request, name):
    """ Renvoyer l'adresse d'une requête et retirer un paramètre d'URL """
    params = request.GET.copy()
    params.pop(name, None)
    return "?{}".format(params.urlencode())


def add_get_parameter(request, name, value):
    """ Renvoyer l'adresse d'une requête et ajouter un paramètre d'URL """
    params = request.GET.copy()
    params[name] = value
    return "?{}".format(params.urlencode())


def add_breadcrumb(request, initial, *args, **kwargs):
    """ Ajouter un breadcrumb de Django-breadcrumbs """
    request.breadcrumbs(initial[0], reverse(initial[1]))
    extra_breadcrumbs = [(str(item), item.get_absolute_url()) for item in args]
    if extra_breadcrumbs:
        request.breadcrumbs(extra_breadcrumbs)
