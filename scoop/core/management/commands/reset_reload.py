# coding: utf-8
from django.core.management import call_command
from django.core.management.base import BaseCommand
from scoop.core.util import shell


class Command(BaseCommand):
    """ Nettoyer et charger les données par défaut de la base de données """
    args = ''
    help = 'Clears the database, and builds it again'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        # Redémarrer PostgreSQL (envoyer le MDP si besoin)
        shell.call_and_type("sudo service postgresql restart", "password", "knt")
        # Réinitialiser la base de données par défaut (envoyer yes)
        shell.call_and_type("dj reset_db --router=default", "yes", "yes")
        # Syncdb et charger les fixtures
        call_command('migrate')
        call_command('loaddata', 'contenttype', 'flagtype', 'options', 'group', 'menus', 'recorder', 'mailtype', 'sites')
        # Copier les fichiers médie, statiques etc. (envoyer yes)
        call_command('copystatic')
        # Charger la liste des pays (traductions) depuis geonames
        call_command('load_countries')
