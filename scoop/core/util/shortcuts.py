# coding: utf-8
import importlib
from operator import itemgetter

from django.conf import settings


def import_qualified_name(name):
    """
    Importer un attribut d'un module

    :param name: Nom pleinement qualifié du module, ex. os.path.join
    :returns: module
    """
    name, member = name.rsplit(".", 1)
    mod = importlib.import_module(name)
    return getattr(mod, member)


def get_qualified_name(item):
    """
    Renvoyer le nom pleinement qualifié d'un objet

    :returns: ex. 'posixpath.join' pour os.path.join
    :rtype: str
    """
    name = item.__name__ if callable(item) else item.__class__.__name__
    fullname = "{module}.{name}".format(**{'module': item.__module__, 'name': name})
    return fullname


def get_languages():
    """ Renvoyer la liste des codes de langues installées dans la configuration """
    return map(itemgetter(1), settings.LANGUAGES)


def get_website_name():
    """ Renvoyer le nom de site enregistré dans les settings """
    return getattr(settings, 'SITE_NAME', 'N/A')


def addattr(**kwargs):
    """ Définir des attributs à une méthode ou fonction """

    def decorator(func):
        for key in kwargs:
            setattr(func, key, kwargs[key])
        return func

    return decorator
