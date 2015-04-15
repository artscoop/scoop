# coding: utf-8
from __future__ import absolute_import

from django.apps.config import AppConfig

__version__ = (1, 2015, 4)


class UserConfig(AppConfig):
    """ Configuration de l'application User """
    name = 'scoop.user'
    label = 'user'

    def ready(self):
        """ Le registre d'applications est prêt """
        from scoop.user import listeners

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.user.UserConfig'
