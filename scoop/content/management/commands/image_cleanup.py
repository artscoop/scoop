# coding: utf-8
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext
from easy_thumbnails.management.commands.thumbnail_cleanup import ThumbnailCollectionCleaner
from scoop.content.models.picture import Picture


class Command(BaseCommand):
    """ Commande pour effacer toutes les miniatures """
    args = ''
    help = ugettext("Delete orphan image references and thumbnails from the database")

    def handle(self, *args, **options):
        """ Exécuter la commande """
        ThumbnailCollectionCleaner().clean_up()
        cleaned = Picture.objects.clean_thumbnails()
        print("Cleaned {count} thumnails".format(count=cleaned))
