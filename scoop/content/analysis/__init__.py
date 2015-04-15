# coding: utf-8
from __future__ import absolute_import

from django.apps.config import AppConfig

__version__ = (1, 2013, 11)


class AnalysisConfig(AppConfig):
    """ Configuration de l'application Analysis """
    name = 'scoop.content.analysis'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass
