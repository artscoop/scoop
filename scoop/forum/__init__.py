# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop

__version__ = (1, 2016, 3)


gettext_noop("Forum")


class ForumConfig(AppConfig):
    """ Configuration de l'application Forum """
    name = 'scoop.forum'
    label = 'forum'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.forum.ForumConfig'
