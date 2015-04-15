# coding: utf-8
from __future__ import absolute_import

from os.path import join

from django.conf import settings
from django.core.management.base import BaseCommand

from scoop.core.util.stream.fileutil import batch_execute


class Command(BaseCommand):
    """ Supprimer les profils ICC des images statiques """
    args = ''
    help = 'Delete ICC profiles of themes images'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        batch_execute(join(settings.STATIC_ROOT, 'theme'), ['.jpg', '.jpeg', '.png'], ["convert", "-strip", "{file}", "{file}"])
