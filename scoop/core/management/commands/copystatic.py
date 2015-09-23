# coding: utf-8
from __future__ import absolute_import

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Collecter les fichiers statiques sans demander de valider """
    help = 'Collects static files without prompt'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        call_command('collectstatic', interactive=False, link=False)
