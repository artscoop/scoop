# coding: utf-8
from django.apps.config import AppConfig

__version__ = (1, 2014, 7)


class PeopleConfig(AppConfig):
    """ Configuration de l'application People """
    name = 'scoop.user.social.people'
    label = 'social_people'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.user.social.people.PeopleConfig'
