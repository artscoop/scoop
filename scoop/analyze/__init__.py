# coding: utf-8
""" Machine Learning et classification """
from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy

__version__ = (1, 2017, 3)


class AnalyzeConfig(AppConfig):
    """ Configuration de l'application Analyze """

    name = 'scoop.analyze'
    label = 'analyze'
    verbose_name = ugettext_lazy("Analyze")

    def ready(self):
        """ Lorsque le registre est prêt """
        from django.conf import settings
        if not settings.SCOOP_DISABLE_SIGNALS:
            from scoop.analyze import listeners


# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.analyze.AnalyzeConfig'
