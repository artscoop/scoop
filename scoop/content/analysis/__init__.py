# coding: utf-8
from django.apps.config import AppConfig

__version__ = (1, 2013, 11)


class AnalysisConfig(AppConfig):
    """ Configuration de l'application Analysis """
    name = 'scoop.content.analysis'
    label = 'analysis'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass
