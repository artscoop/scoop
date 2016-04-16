# coding: utf-8
from django.core.management.base import BaseCommand
from django.test.utils import override_settings

from scoop.location.tasks.geonames import geonames_fill


class Command(BaseCommand):
    """ Mettre à jour les villes depuis une base de données Geonames """
    args = ''
    help = 'Update countries and cities from Geonames'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        from scoop.location.models import Country
        with override_settings(DEBUG=False):
            # Mettre à jour pour tous les pays publics
            geonames_fill(Country.objects.public())
