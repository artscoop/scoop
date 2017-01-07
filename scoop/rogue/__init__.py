# coding: utf-8
"""
Traitement des données et utilisateurs qui doivent disparaître du site.
Cela comprend entre autres, les utilisateurs escrocs, mythomanes, vulgaires
et insultants, ainsi que les contenus insultants ou non accessibles à certains
publics
"""
from django.apps.config import AppConfig


__version__ = (1, 2016, 1)


class RogueConfig(AppConfig):
    """ Configuration de l'application Rogue """
    name = 'scoop.rogue'
    label = 'rogue'

    def ready(self):
        """ Le registre d'applications est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.rogue import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.rogue.RogueConfig'
