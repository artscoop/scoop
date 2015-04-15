# coding: utf-8
"""
Traitement des données et utilisateurs qui doivent disparaître du site.
Cela comprend entre autres, les utilisateurs escrocs, mythomanes, vulgaires
et insultants, ainsi que les contenus insultants ou non accessibles à certains
publics
"""
__version__ = (1, 2013, 8)
from django.apps.config import AppConfig


class RogueConfig(AppConfig):
    """ Configuration de l'application Rogue """
    name = 'scoop.rogue'
    label = 'rogue'

    def ready(self):
        """ Le registre d'applications est prêt """
        from scoop.rogue import listeners

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.rogue.RogueConfig'
