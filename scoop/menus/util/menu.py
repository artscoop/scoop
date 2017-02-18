# coding: utf-8
from django.conf import settings
from scoop.core.util.shortcuts import import_fullname


menu_cache = dict()


def get_menu(alias):
    """
    Renvoyer un objet de Menu correspondant à l'alias passé

    :param alias: alias de menu
    :type alias: str
    :returns: un objet de type Menu, conservé si possible dans un cache
    """
    if alias not in menu_cache:
        aliases = settings.MENU_ALIASES
        menu_cache[alias] = import_fullname(aliases[alias])
    return menu_cache[alias]
