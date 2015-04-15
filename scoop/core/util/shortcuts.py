# coding: utf-8
from __future__ import absolute_import

import importlib

from django.conf import settings


def import_fullname(name):
    """
    Importer un attribut d'un module
    :param name: Nom pleinement qualifié du module, ex. os.path.join
    """
    name, member = name.rsplit(".", 1)
    mod = importlib.import_module(name)
    return getattr(mod, member)


def get_fullname(item):
    """ Renvoyer le nom pleinement qualifié d'un objet """
    name = item.__name__ if callable(item) else item.__class__.__name__
    fullname = "{module}.{name}".format(**{'module': item.__module__, 'name': name})
    return fullname


def get_languages():
    """ Renvoyer la liste des codes de langues installées dans la configuration """
    return map(lambda l: l[0], settings.LANGUAGES)


def addattr(**kwargs):
    """ Définir des attributs à une méthode ou fonction """

    def decorator(func):
        for key in kwargs:
            setattr(func, key, kwargs[key])
        return func

    return decorator
