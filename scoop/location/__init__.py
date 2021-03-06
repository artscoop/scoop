# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop, ugettext_lazy


__version__ = (1, 2016, 12, 11)


gettext_noop("Location")


class LocationConfig(AppConfig):
    """ Configuration de l'application Location """

    name = 'scoop.location'
    label = 'location'
    verbose_name = ugettext_lazy("Location")

    def ready(self):
        """ Le registre d'applications est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.location import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.location.LocationConfig'
