# coding: utf-8
import logging
import os
from urllib.error import URLError
from urllib.parse import unquote, urlparse

import requests
from urllib3.util.retry import Retry

from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse_lazy as reverse
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

# Constantes
DEFAULT_HEADERS = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/39.0'}


def get_domain():
    """ Renvoyer le nom de domaine courant """
    from django.contrib.sites.models import Site
    current_site = Site.objects.get_current()
    return current_site.domain if "/" in current_site.domain else getattr(settings, "DOMAIN_NAME", "")


def get_url_resource(path, as_text=True, **kwargs):
    """
    Renvoyer le contenu d'une URL

    :param as_text: Renvoyer le contenu de la réponse uniquement ?
    """
    try:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.25)
        session.mount(get_url_domain(path), requests.adapters.HTTPAdapter(max_retries=retries))
        resource = requests.get(path, headers=DEFAULT_HEADERS, timeout=6.0, allow_redirects=True, **kwargs)
        return resource.text if as_text else resource
    except (IOError, OSError):
        raise URLError("The resource at {path} was unavailable.".format(path=path), path)


def download_url_resource(path, output=None):
    """
    Télécharger un fichier à une URL et renvoyer le chemin du fichier local téléchargé

    :param output: Chemin de sortie, fichier dans le répertoire temporaire si None
    :type output: str | None
    """
    if output and os.path.exists(output):
        logging.warning(_("The download destination file at {path} already exists. Skipped.").format(path=output))
        return output
    try:
        resource = get_url_resource(path, False, stream=True)
    except (IOError, OSError):
        raise URLError("The resource at {path} cannot be downloaded.".format(path=path), path)
    resource_file = NamedTemporaryFile(delete=False) if output is None else open(output, 'wb')
    for chunk in resource.iter_content(16384):
        resource_file.write(chunk)
    resource_file.close()
    return resource_file.name


def get_url_path(path):
    """ Renvoyer une URL sans paramètres et sans ancre """
    filename = os.path.basename(path).split('?')[0].split('#')[0]
    return filename


def get_url_domain(path):
    """
    :param path: URL
    :return: URL de racine du nom de domaine
    """
    components = urlparse(path)
    domain = "{part.scheme}://{part.netloc}".format(part=components)
    return domain


def unquote_url(path, transliterate=True):
    """ Renvoyer une URL en décodant les caractères HTML sous forme % """
    filename = unquote(str(path))
    filename = unidecode(filename) if transliterate else filename
    return filename


def remove_get_parameter(request, name):
    """
    Renvoyer l'adresse d'une requête et retirer un paramètre d'URL

    :param request: Objet request ou URL
    """
    params = request.GET.copy()
    params.pop(name, None)
    return "?{}".format(params.urlencode())


def add_get_parameter(request, name, value):
    """ Renvoyer l'adresse d'une requête et ajouter un paramètre d'URL """
    params = request.GET.copy()
    params[name] = value
    return "?{}".format(params.urlencode())


def add_breadcrumb(request, initial, *args, **kwargs):
    """
    Ajouter un breadcrumb de Django-breadcrumbs

    :param request: Objet de requête
    :param initial: Tuple (name, url)
    """
    request.breadcrumbs(initial[0], reverse(initial[1]))
    extra_breadcrumbs = [(str(item), item.get_absolute_url()) for item in args]
    if extra_breadcrumbs:
        request.breadcrumbs(extra_breadcrumbs)
