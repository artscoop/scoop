# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop, ugettext_lazy


__version__ = (1, 2016, 5)


class HelpConfig(AppConfig):
    """ Configuration de l'application Help """

    name = 'scoop.help'
    label = 'help'
    verbose_name = ugettext_lazy("Help")

    def ready(self):
        """ Le registre d'applications est prêt """
        pass


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.help.HelpConfig'
