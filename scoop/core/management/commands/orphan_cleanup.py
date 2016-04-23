# coding: utf-8
from django.conf import settings
from django.core.management.base import BaseCommand
from scoop.core.util.stream.fileutil import clean_empty_folders, clean_orphans


class Command(BaseCommand):
    """ Effacer les fichiers Media orphelins """
    args = ''
    help = 'Delete free files that are most likely not tied to a database entry anymore'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        clean_orphans(output_log=True, delete=True)
        clean_empty_folders(settings.MEDIA_ROOT)
