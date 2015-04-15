# coding: utf-8
from django.apps.config import AppConfig
from django.utils.translation import gettext_noop


__version__ = (1, 2015, 3)

gettext_noop("Quiz")


class QuestionConfig(AppConfig):
    """ Configuration de l'application Messaging """
    name = 'scoop.question'
    label = 'question'

    def ready(self):
        """ Le registre d'applications est prêt """

# Charger la configuration ci-dessus par défaut
default_app_config = 'scoop.question.QuestionConfig'
