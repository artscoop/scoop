# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop, ugettext_lazy


__version__ = (1, 2015, 3)


class MessagingConfig(AppConfig):
    """ Configuration de l'application Messaging """

    name = 'scoop.messaging'
    label = 'messaging'
    verbose_name = ugettext_lazy("Messaging")

    def ready(self):
        """ Le registre d'applications est prêt """
        ugettext_lazy("Smileys")
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.messaging import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.messaging.MessagingConfig'
