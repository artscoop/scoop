# coding: utf-8
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.commands.compilemessages import Command as CompileMessages

from scoop.core.util.stream.directory import Paths


class Command(CompileMessages):
    """ Générer les fichiers de traduction pour toutes les applications dans le projet """
    help = 'Generate binary files for all locale folders in this project'

    def handle(self, *args, **options):
        """ Exécuter la commande """
        project_paths = getattr(settings, 'MAKEMESSAGES_DIRS', [Paths.get_root_dir()])
        for project_path in project_paths:
            print("Updating locale binaries for project at {path}".format(path=project_path))
            parsable_paths = []
            for root, dirs, _ in os.walk(project_path, topdown=True):
                for directory in dirs:
                    new_directory = os.path.join(root, directory)
                    parsable_paths.append(new_directory)
            for directory in settings.TEMPLATES[0]['DIRS']:
                parsable_paths.append(directory)
            for subdir in parsable_paths:
                os.chdir(subdir)
                if 'locale' in os.listdir(subdir):
                    print("Creating locale binaries for {dir}".format(dir=subdir))
                    call_command('compilemessages', *args, **options)
        print("Finished updating locale binaries.")
