# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop

__version__ = (1, 2016, 2)

gettext_noop("Editorial")


class EditorialConfig(AppConfig):
    """ Configuration de l'application Editorial """
    name = 'scoop.editorial'
    label = 'editorial'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.editorial.EditorialConfig'
