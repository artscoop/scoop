# coding: utf-8
from django.apps.config import AppConfig


__version__ = (1, 2015, 4)


class AccessConfig(AppConfig):
    """ Configuration de l'application User """
    name = 'scoop.user.access'
    label = 'access'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.user.access.AccessConfig'
