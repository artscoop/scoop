# coding: utf-8
import logging
import os
from math import ceil, floor
from os.path import basename, splitext

import PIL

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify
from django.utils import timezone
from easy_thumbnails.models import Source, Thumbnail
from scoop.content.util.webkit import Screenshot
from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.stream.directory import Paths
from scoop.core.util.stream.fileutil import check_file_extension, walk
from scoop.core.util.stream.urlutil import download_url_resource, get_url_path, unquote_url
from unidecode import unidecode

logger = logging.getLogger(__name__)
root_dir = Paths.get_root_dir


def get_image_upload_path(picture, name, update=False):
    """
    Renvoyer le chemin et le nom de fichier par défaut des
    uploads d'images.
    :param picture: instance de modèle d'image
    :param name: nom du fichier uploadé
    :param update: mettre à jour le chemin mais conserver le nom de fichier
    """
    name = unidecode(name).lower() if name else picture.get_filename() if picture else uuid_bits(64)
    name = name.split('?')[0].split('#')[0]
    name = name or uuid_bits(64)  # si le ? est au début de la chaîne, générer un nom de fichier
    # Créer les dictionnaires de données de noms de fichiers
    now = picture.get_datetime() if picture else timezone.now()
    fmt = now.strftime
    # Remplir le dictionnaire avec les informations de répertoire
    picture_type = picture.content_type
    author = slugify(picture.author.username) if picture.author is not None else "__no_author"
    dir_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'week': fmt("%W"), 'day': fmt("%d"), 'picture_type': picture_type}
    name_info = {'name': slugify(splitext(basename(name))[0]), 'ext': splitext(basename(name))[1]}
    prefix_info = {'hour': fmt("%H"), 'minute': fmt("%M"), 'second': fmt("%S"), 'week': fmt("%W"), 'author': author}
    data = dir_info
    data.update(name_info)
    data.update(prefix_info)
    # Renvoyer le répertoire ou le chemin complet du fichier
    path = "file/pic/{year}/{month}{week}" if update else "file/pic/{year}/{month}{week}/{author}/{name}{ext}"
    path = "test/{}".format(path) if settings.TEST else path
    path = path.format(**data)
    return path


def get_animation_upload_path(animation, name, update=False):
    """
    Renvoyer le chemin et le nom de fichier par défaut des
    uploads d'animations.
    :param animation: instance de modèle d'animation
    :param name: nom du fichier uploadé
    :param update: mettre à jour le chemin mais conserver le nom de fichier
    """
    name = unidecode(name).lower() if name else animation.get_filename() if animation else uuid_bits(64)
    name = name.split('?')[0].split('#')[0]
    name = name or uuid_bits(64)  # si le ? est au début de la chaîne, générer un nom de fichier
    # Créer les dictionnaires de données de noms de fichiers
    now = animation.get_datetime() if animation else timezone.now()
    fmt = now.strftime
    # Remplir le dictionnaire avec les informations de répertoire
    author = slugify(animation.author.username) if animation.author is not None else "__no_author"
    dir_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'week': fmt("%W"), 'day': fmt("%d")}
    name_info = {'name': slugify(splitext(basename(name))[0]), 'ext': splitext(basename(name))[1]}
    prefix_info = {'hour': fmt("%H"), 'minute': fmt("%M"), 'second': fmt("%S"), 'week': fmt("%W"), 'author': author}
    data = dir_info
    data.update(name_info)
    data.update(prefix_info)
    # Renvoyer le répertoire ou le chemin complet du fichier
    path = "file/ani/{year}/{month}{week}" if update else "file/ani/{year}/{month}{week}/{author}/{name}{ext}"
    path = "test/{}".format(path) if settings.TEST else path
    path = path.format(**data)
    return path


def download(instance, path, screenshot=True):
    """
    Télécharger une image pour un objet Picture

    :param instance: Objet Picture pour lequel télécharger l'image
    :param screenshot: Effectuer un screenshot d'une URL si path n'est pas une image
    """
    from scoop.content.models.picture import Picture

    try:
        path = path.decode('utf-8') if isinstance(path, bytes) else path
        outfile = download_url_resource(path)
        # Transformer le chemin de l'URL en nom de fichier utilisable
        filename = get_url_path(path)
        filename = unquote_url(filename, transliterate=True)
        # Peut être None si aucun traitement nécessaire, auquel cas garder le filename original
        filename = check_file_extension(filename, outfile, ['.png', '.jpg', '.jpeg', '.gif']) or filename
        # Si une image était déjà liée à l'instance, supprimer le fichier
        if instance.exists():
            instance.delete_file()
        # Si le chemin est égal à celui de la description de l'instance, vider
        if path == instance.description:
            instance.description = ""
        # Sauver l'image dans le nouveau fichier
        instance.image.save(filename, File(open(outfile, 'rb')))
        super(Picture, instance).save()
    except (KeyError, Exception):
        try:
            img_temp = NamedTemporaryFile(suffix='.jpg', prefix='screen-', delete=False)
            image = PIL.Image.new('RGB', (64, 64))
            image.save(img_temp.name, optimize=True)
            # Si une image était déjà liée à l'instance, supprimer le fichier
            if instance.exists():
                instance.delete_file()
            if path == instance.description:
                instance.description = ""
            # Sauver l'image dans le nouveau fichier
            instance.image.save(img_temp.name, File(img_temp))
            # Si screenshot est True, remplacer l'image par un screenshot
            if screenshot is True:
                Screenshot().capture(path, instance.image.path)
                instance.update_size()
        except Exception:
            raise


def clean_thumbnails():
    """ Nettoyer toutes les miniatures cassées """
    sources = Source.objects.all().iterator()
    for source in sources:
        if not default_storage.exists(source.name):
            thumbs = Thumbnail.objects.filter(source=source)
            for thumb in thumbs:
                try:
                    try:
                        default_storage.delete(thumb.name)
                    except Exception as e:
                        print(e)
                    thumb.delete()
                except Exception as e:
                    print(e)
            source.delete()
    # Supprimer les miniatures qui ne correspondent pas à un fichier
    thumbnails = Thumbnail.objects.all().iterator()
    for thumbnail in thumbnails:
        if not default_storage.exists(thumbnail.name):
            thumbnail.delete()
    # Supprimer les miniatures qui ne sont pas dans la base
    for root, _, files in walk(default_storage, 'thumb'):
        for file_ in files:
            path = os.path.join(root, file_)
            if not Thumbnail.objects.filter(name=path).exists():
                default_storage.delete(path)


def get_context_picture_url(self, name, ext=None, *args):
    """
    Renvoyer un chemin d'image dans le répertoire d'images par défaut
    :param name: nom du contexte de l'image
    :param ext: None ou une extension de fichier, sans le point
    :param args: paramètres du contexte, utilisés dans le nom de fichier
    """
    filename = "context-{name}-{args}.{ext}".format(name=name, args="-".join(args), ext=ext or "jpg")
    fullpath = os.path.join(settings.USER_DEFAULT_PICTURE_PATH, filename)
    return fullpath


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """
    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))
    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list.
    return lower[:-1] + upper[:-1]


def convex_hull_to_rect(hull):
    """ Convertir une coque convexe en sa boîte englobante """
    coordinates = {'left': None, 'right': None, 'top': None, 'bottom': None}
    for point in hull:
        if coordinates['left'] is None or point[0] < coordinates['left']:
            coordinates['left'] = int(floor(point[0]))
        if coordinates['right'] is None or point[0] > coordinates['right']:
            coordinates['right'] = int(ceil(point[0]))
        if coordinates['top'] is None or point[1] < coordinates['top']:
            coordinates['top'] = int(floor(point[1]))
        if coordinates['bottom'] is None or point[1] > coordinates['bottom']:
            coordinates['bottom'] = int(ceil(point[1]))
    return [coordinates['left'], coordinates['top'], coordinates['right'], coordinates['bottom']]
