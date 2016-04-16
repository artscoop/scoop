# coding: utf-8
""" Contenus textuels, commentaires et fichiers media """
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop


__version__ = (1, 2015, 3)

gettext_noop("Content")


class ContentConfig(AppConfig):
    """ Configuration de l'application Contenu """
    name = 'scoop.content'
    label = 'content'

    def ready(self):
        """ Lorsque le registre est prêt """
        from scoop.content import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.content.ContentConfig'
