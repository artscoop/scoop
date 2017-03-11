# coding: utf-8
""" Contenus textuels, commentaires et fichiers media """
from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy


__version__ = (1, 2015, 3)


class ContentConfig(AppConfig):
    """ Configuration de l'application Contenu """

    name = 'scoop.content'
    label = 'content'
    verbose_name = ugettext_lazy("Content")

    def ready(self):
        """ Lorsque le registre est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.content import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.content.ContentConfig'
