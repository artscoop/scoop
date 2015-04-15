# coding: utf-8
__version__ = (1, 2015, 3, 8)
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop

gettext_noop("Location")


class LocationConfig(AppConfig):
    """ Configuration de l'application Location """
    name = 'scoop.location'
    label = 'location'

    def ready(self):
        """ Le registre d'applications est prêt """
        from scoop.location import listeners

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.location.LocationConfig'
