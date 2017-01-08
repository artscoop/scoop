# coding: utf-8
from django.apps.config import AppConfig


__version__ = (1, 2017, 1)


class MenusConfig(AppConfig):
    """ Configuration de l'application Core """

    name = 'scoop.menus'
    label = 'menus'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.menus.MenusConfig'