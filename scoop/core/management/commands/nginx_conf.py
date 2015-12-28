# coding: utf-8
import os
import subprocess
import tempfile
from optparse import make_option

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.text import slugify
from scoop.core.util.stream.request import default_context


class Command(BaseCommand):
    """ Commande de création de fichiers de configuration nginx pour le site actuel """
    args = ''
    help = 'Generate nginx server file for this project'
    option_list = BaseCommand.option_list + (
        make_option('--export', '-e', '--install', '--deploy', action='store_true', dest='export', default=False,
                    help='Exports the configuration file directly into nginx conf folder.'),
    )

    def handle(self, *args, **options):
        """ Traiter la commande """
        context = default_context()
        data = {'MEDIA_ROOT': settings.MEDIA_ROOT, 'STATIC_ROOT': settings.STATIC_ROOT}
        output = render_to_string("core/configuration/nginx-site.conf", data, context).encode('utf-8')
        output_base = render_to_string("core/configuration/nginx.conf", data, context).encode('utf-8')
        confname = slugify(Site.objects.get_current().name)
        destinations = [{'output': output, 'destination': '/etc/nginx/sites-enabled/{name}'.format(name=confname)}, {'output': output_base, 'destination': '/etc/nginx/nginx.conf'}]
        # Récupérer la liste des options
        export = options.get('export', False)
        # Effectuer un export ou bien effectuer une sortie
        if export is not False:
            for destination in destinations:
                try:
                    (descriptor, filename) = tempfile.mkstemp()
                    temp = os.fdopen(descriptor, "w")
                    temp.write(destination['output'])
                    temp.close()
                    newname = destination['destination']
                    subprocess.Popen(['sudo', 'cp', filename, newname]).wait()
                    subprocess.Popen(['sudo', 'chmod', '766', newname]).wait()
                    subprocess.Popen(['sudo', 'service', 'nginx', 'restart']).wait()
                finally:
                    os.remove(filename)
        else:
            print(output)
