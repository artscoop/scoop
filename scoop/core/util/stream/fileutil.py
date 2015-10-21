# coding: utf-8
from __future__ import absolute_import

import gzip
import io
import logging
import os
import subprocess
import time
from mimetypes import guess_extension
from os.path import join
from zipfile import ZipFile

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.db.models.manager import Manager
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from magic import Magic

from scoop.core.util.data.typeutil import make_iterable

logger = logging.getLogger(__name__)


def walk(storage, top='/', topdown=False, onerror=None):
    """
    An implementation of os.walk() which uses the Django storage for listing directories.
    :param storage: Django storage instance
    :param top: root directory for listing files
    :param topdown: return directories starting from the root
    :param onerror: function to handle os errors while walking the tree
    :type top: unicode or str
    :type topdown: bool
    :type onerror: callable
    """
    try:
        dirs, nondirs = storage.listdir(top)
    except os.error as err:
        if onerror is not None:
            onerror(err)
        return

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = os.path.join(top, name)
        for x in walk(storage, new_path):
            yield x
    if not topdown:
        yield top, dirs, nondirs


def auto_open_file(path, filename):
    """
    Ouvrir un fichier dans le répertoire path
    Reconnaît les fichiers gzip et zip
    :param filename: nom de fichier sans extension
    """
    for files in os.listdir(path):
        if files.lower().startswith('%s' % filename.lower()):
            if '.gz' in files.lower():
                content = gzip.open(os.path.join(path, files), 'rb')
            elif '.zip' in files.lower():
                content = open_zip_file(os.path.join(path, files), filename)
            else:
                content = open(os.path.join(path, files), 'rb')
            content = io.TextIOWrapper(content, encoding='utf-8', newline='')
            return content
    raise ImproperlyConfigured(_("A file named %(file)s was not found in %(path)s") % {'file': filename, 'path': path})


def open_zip_file(path, filename):
    """ Ouvrir un fichier filename dans un fichier zip """
    archive = ZipFile(path, 'r')
    names = archive.namelist()
    name = names[0]
    for n in names:
        if n.lower().startswith("{}.".format(filename.lower())):
            name = n
            content = archive.open(name, 'rU')
            content = io.TextIOWrapper(content, encoding='utf-8', newline='')
            return content
    raise ImproperlyConfigured(_("A file named %(file)s was not found in %(path)s") % {'file': filename, 'path': path})


def clean_orphans(output_log=True, delete=False):
    """ Supprimer les fichiers orphelins du répertoire MEDIA """
    from django.contrib.contenttypes.fields import ContentType
    # Configuration
    dirs = settings.ORPHAN_CHECK_DIRS
    apps = settings.ORPHAN_CHECK_APPS
    fields, db_files, deletable = [], [], []
    counter, deleted = 0, 0
    # Trouver tous les champs FileField
    for model in ContentType.objects.filter(app_label__in=apps):
        model_class = model.model_class()
        model_class.add_to_class('all_objects', Manager())
        for field in model_class._meta.fields:
            if (field.get_internal_type() == 'FileField' and not model_class._meta.abstract):
                fields.append([model_class, field.name, model_class._meta.object_name])
    # Recenser tous les liens vers des fichiers
    for field in fields:
        model, field_name = field[0], field[1]
        files = model.all_objects.exclude(**{field_name: ''}).distinct().values_list(field_name, flat=True)
        files = [join(settings.MEDIA_ROOT, item) for item in files if item]
        db_files += files
    # Parcourir tous les fichiers
    for directory in dirs:
        for root, _dummy, filenames in os.walk(join(settings.MEDIA_ROOT, directory)):
            for filename in filenames:
                filepath = join(root, filename)
                counter += 1
                if filepath not in db_files:
                    deletable.append(filepath)
                    deleted += 1
    # Supprimer les fichiers si demandé
    if delete is True:
        for item in deletable:
            try:
                os.remove(item)
            except:
                deleted -= 1
    # Sortie de journalisation
    if output_log is True:
        output = render_to_string('core/view/orphan-log.txt', {'counter': counter, 'deleted': deleted, 'files_delete': deletable, 'files': db_files, 'fields': fields})
        logger.info(output)
        print(output)
        return output


def check_file_extension(filename, resource_path, extensions):
    """ Renvoyer le nom d'un fichier avec l'extension correspondant à son type MIME """
    if os.path.exists(resource_path) and filename:
        # Réparer l'extension de fichier
        extension_add = True
        extensions = make_iterable(extensions)
        for extension in extensions:
            if filename.lower().endswith(extension.lower()):
                extension_add = False
        if extension_add:
            # Trouver le type MIME
            mime = Magic(mime=True, keep_going=True)
            mimetype = mime.from_file(resource_path)
            new_extension = guess_extension(mimetype)
            if filename and new_extension:
                filename = "{}{}".format(filename, new_extension)
                if new_extension.lower() in extensions:
                    return filename
            else:
                return None
        else:
            return filename
    return filename


def get_mime_type(resource_path):
    """ Renvoyer le type MIME d'un fichier local """
    mime = Magic(mime=True)
    mimetype = mime.from_buffer(open(resource_path).read())
    return mimetype


def clean_empty_folders(path, output=True):
    """ Supprimer tous les sous-répertoires vides d'un chemin """
    deleted = 1
    total_deleted = 0
    while deleted > 0:
        deleted = 0
        for root, dirs, files in walk(default_storage, path, topdown=False):
            if len(files) == 0 and len(dirs) == 0:
                try:
                    if os.path.exists(join(default_storage.base_location, root)):
                        os.rmdir(join(default_storage.base_location, root))
                        deleted += 1
                        total_deleted += 1
                except Exception as e:
                    logger.warn(e)
                    pass
    if output is True:
        trace = "{count} empty folders have been successfully deleted.".format(count=total_deleted)
        logger.warn(trace)
    if total_deleted > 0:
        clean_empty_folders(path, output=output)


def batch_execute(path, extensions, command):
    """
    Exécuter une commande shell sur tous les fichers de <path> correspondant aux
    extensions passées en paramètre (liste ou simple chaîne)
    @param command: chaîne contenant la commande à exécuter sur chaque fichier.
    Autorise l'utilisation du placeholder {name}
    """
    total_processed = 0
    for root, _dummy, files in os.walk(path):
        for f in files:
            for extension in make_iterable(extensions):
                if extension.lower() in f.lower():
                    for i, _dummyx in enumerate(command):
                        command[i] = command[i].format(file=os.path.join(path, root, f))
                    subprocess.call(command)
                    total_processed += 1
    logger.info("Batch executed successfully on {count} files.".format(count=total_processed))


def delete_old_files(path, days=7):
    """ Supprimer tous les fichiers d'un répertoire, plus vieux que n jours """
    now = time.time()
    for f in os.listdir(path):
        if os.stat(f).st_mtime < now - (days * 86400):
            if os.path.isfile(f):
                os.remove(os.path.join(path, f))


def find_files_in_folder(path, extensions):
    """ Renvoyer tous les fichiers d'un répertoire correspondant à une ou plusieurs extensions """
    files = []
    extensions = make_iterable(extensions)
    for folder, _directories, filenames in os.walk(path):
        for filename in filenames:
            for extension in extensions:
                if filename.lower().endswith(extension):
                    files.append(join(folder, filename))
    return files


def get_free_disk_space(percent=False):
    """ Renvoyer l'espace disque disponible sur la partition du projet """
    s = os.statvfs(__file__)
    if not percent:
        return s.f_bsize * s.f_bavail
    else:
        return 100.0 * s.f_bavail / float(s.f_blocks)


def get_line_count(filename):
    """ Renvoyer le nombre de lignes d'un fichier texte """
    out = subprocess.Popen(['wc', '-l', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
    return int(out.partition(b' ')[0])
