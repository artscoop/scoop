# coding: utf-8
from django.apps.config import AppConfig

__version__ = (1, 2014, 8)


class TicketConfig(AppConfig):
    """ Configuration de l'application Ticket """
    name = 'ticket'

    def ready(self):
        """ Le registre d'applications est prêt """
        pass
