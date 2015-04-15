# coding: utf-8
from django.conf import settings
from django.core.management.base import BaseCommand

from scoop.core.util.stream.fileutil import clean_empty_folders


class Command(BaseCommand):
    """ Supprimer les répertoires vides dans MEDIA_ROOT """
    args = ''
    help = 'Delete empty MEDIA_ROOT folders'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        clean_empty_folders(settings.MEDIA_ROOT)
