# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy


__version__ = (1, 2017, 2)


class MenusConfig(AppConfig):
    """ Configuration de l'application Core """

    name = 'scoop.menus'
    label = 'menus'
    verbose_name = ugettext_lazy("Menus")

    def ready(self):
        """ Le registre d'applications est prêt """
        pass

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.menus.MenusConfig'
