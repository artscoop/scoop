# coding: utf-8
import getpass
import os
import subprocess
import tempfile

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.text import slugify

from scoop.core.util.stream.request import default_request


class Command(BaseCommand):
    """ Commande de création de fichiers de configuration nginx pour le site actuel """
    args = ''
    help = 'Generate nginx server file for this project'

    def add_arguments(self, parser):
        parser.add_argument('--export', '-e', '--install', '--deploy', action='store_true', dest='export', default=False,
                            help='Exports the configuration file directly into nginx conf folder.')

    def handle(self, *args, **options):
        """ Traiter la commande """
        username = getpass.getuser()
        data = {'MEDIA_ROOT': settings.MEDIA_ROOT, 'STATIC_ROOT': settings.STATIC_ROOT, 'username': username}
        output = render_to_string("core/configuration/nginx-site.conf", data, default_request()).encode('utf-8')
        output_base = render_to_string("core/configuration/nginx.conf", data, default_request()).encode('utf-8')
        confname = slugify(Site.objects.get_current().name)
        destinations = [{'output': output, 'destination': '/etc/nginx/sites-enabled/{name}'.format(name=confname)},
                        {'output': output_base, 'destination': '/etc/nginx/nginx.conf'}]
        # Récupérer la liste des options
        export = options.get('export', False)
        # Effectuer un export ou bien effectuer une sortie
        if export is not False:
            for destination in destinations:
                try:
                    (descriptor, filename) = tempfile.mkstemp()
                    temp = os.fdopen(descriptor, "w")
                    temp.write(destination['output'].decode('utf-8'))
                    temp.close()
                    newname = destination['destination']
                    subprocess.Popen(['sudo', 'cp', filename, newname]).wait()
                    subprocess.Popen(['sudo', 'chmod', '766', newname]).wait()
                    subprocess.Popen(['sudo', 'service', 'nginx', 'restart']).wait()
                finally:
                    os.remove(filename)
        else:
            print(output)
