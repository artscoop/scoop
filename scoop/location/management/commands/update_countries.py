# coding: utf-8
from __future__ import absolute_import

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext


class Command(BaseCommand):
    """ Peupler la liste des pays """
    args = ''
    help = ugettext("Populate countries from Geonames")

    def handle(self, *args, **options):
        """ Exécuter la commande """
        from scoop.location.util.geonames import populate_countries
        populate_countries(rename=True)
