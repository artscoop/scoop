# coding: utf-8
import gc
import sys

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext
from scoop.content.models.picture import Picture


class Command(BaseCommand):
    """ Commande pour effacer toutes les miniatures """
    args = ''
    help = ugettext("Update path of all pictures in the database to default")

    def handle(self, *args, **options):
        """ Exécuter la commande """
        pictures = Picture.objects.exclude(image__startswith='public').order_by('id')
        count = pictures.count()
        print("{0:06n} images total.".format(count))
        failures = 0
        for ind, picture in enumerate(pictures, start=1):
            print("{i:06n}/{count:06n} : {f}".format(i=ind, count=count, f=picture.get_filename()), file=sys.stderr)
            try:
                result = picture.update_file_path()
                failures += 1 if result is False else 0
                if ind % 256 == 0:
                    gc.collect()
            except [OSError, IOError]:
                failures += 1
        print("{count} files did not update.".format(count=failures))
