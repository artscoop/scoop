# coding: utf-8
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Télécharger les noms alternatifs de villes """
    args = ''
    help = 'Populate city names from Geonames'

    def handle(self, *args, **options):
        from scoop.location.util.geonames import rename_cities
        # Télécharger et renommer
        rename_cities()
