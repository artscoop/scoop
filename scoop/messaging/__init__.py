# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop

__version__ = (1, 2015, 3)


gettext_noop("Messaging")
gettext_noop("Smileys")


class MessagingConfig(AppConfig):
    """ Configuration de l'application Messaging """
    name = 'scoop.messaging'
    label = 'messaging'

    def ready(self):
        """ Le registre d'applications est prêt """
        from scoop.messaging import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.messaging.MessagingConfig'
