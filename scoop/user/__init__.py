# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy


__version__ = (1, 2015, 4)


class UserConfig(AppConfig):
    """ Configuration de l'application User """

    name = 'scoop.user'
    label = 'user'
    verbose_name = ugettext_lazy("User")

    def ready(self):
        """ Le registre d'applications est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.user import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.user.UserConfig'
