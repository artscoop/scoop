# coding: utf-8
from django.apps.config import AppConfig


__version__ = (1, 2014, 7)


class SocialConfig(AppConfig):
    """ Configuratoin de l'application Social """
    name = 'scoop.user.social'
    label = 'social'

    def ready(self):
        """ Le registre d'applications est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.user.social import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.user.social.SocialConfig'
