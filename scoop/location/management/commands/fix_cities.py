# coding: utf-8
from __future__ import absolute_import

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Quickfixes des villes de France, Belgique et Canada """
    args = ''
    help = 'Populate countries from Geonames'

    def handle(self, *args, **options):
        from scoop.location.models import City
        # Pour la France, Belgique etc. exclure les objets sans code postal
        City.objects.filter(city=True, country__code2__in=['FR', 'BE']).exclude(alternates__language="post").distinct().delete()
        # Inclure les capitales (PPLC en l'absence de sabotage)
        City.objects.filter(type='PPLC').update(city=True)
