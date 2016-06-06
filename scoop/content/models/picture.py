# coding: utf-8
import logging
import math
import os
import subprocess
import traceback
from os.path import join
from random import randrange
from urllib import parse

import cv2
import simplejson
from PIL import Image

from django.conf import settings
from django.contrib.contenttypes import fields
from django.core.cache import cache
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.db.models.fields.files import FieldFile
from django.template.defaultfilters import filesizeformat, urlencode
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from easy_thumbnails.alias import aliases
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.models import Source, Thumbnail
from scoop.content.util.picture import clean_thumbnails, convex_hull, convex_hull_to_rect, download
from scoop.core.abstract.content.acl import ACLModel
from scoop.core.abstract.content.license import AudienceModel, CreationLicenseModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.moderation import ModeratedModel, ModeratedQuerySetMixin
from scoop.core.abstract.core.rectangle import RectangleModel
from scoop.core.abstract.core.uuid import FreeUUIDModel, UUIDField
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.data.dateutil import now
from scoop.core.util.data.typeutil import string_to_dict
from scoop.core.util.django.templateutil import render_to
from scoop.core.util.model.fields import WebImageField
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.directory import Paths
from scoop.core.util.stream.fileutil import check_file_extension
from scoop.core.util.stream.urlutil import get_url_resource

logger = logging.getLogger(__name__)


class PictureQuerySetMixin(object):
    """ Mixin de Queryset et de Manager des images """

    # Constantes
    TOTAL_SIZE_CACHE_KEY = 'content.picture.total_size'

    # Getter
    def get_by_uuid(self, uuid, default=None):
        """ Renvoyer l'image possédant l'UUID désiré """
        if uuid is not None:
            try:
                return self.get(uuid=uuid)
            except Picture.DoesNotExist:
                return default
        return default

    def get_total_size(self, boundary=4096):
        """ Renvoyer la taille totale des images """
        cached = cache.get(self.TOTAL_SIZE_CACHE_KEY)
        if False and cached is not None:
            return cached
        # Calculer la taille totale
        total = 0
        for picture in self.all().iterator():
            try:
                if picture.exists():
                    total += math.ceil(picture.image.size / float(boundary)) * boundary
                else:
                    picture.delete()
            except (IOError, TypeError) as e:
                print(e, picture.id, picture.image)
        cache.set(self.TOTAL_SIZE_CACHE_KEY, int(total), 86400)
        return total

    def by_marker(self, marker, **kwargs):
        """ Renvoyer les images possédant exactement un marqueur """
        kwargs.pop('marker', None)
        return self.filter(marker=marker, **kwargs)

    def get_thumbnail_count(self, full=False):
        """ Renvoyer le nombre total de miniatures des images """
        if full is True:
            total, names = 0, self.values_list('image', flat=True)
            for name in names:
                source = Source.objects.filter(name=name)
                total += Thumbnail.objects.filter(source__in=source).count()
            return total
        return Thumbnail.objects.count()

    def find_by_keyword(self, keyword):
        """ Renvoyer des informations d'URL d'images pour une expression """
        path = 'https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={keyword}' \
               '&searchType=image&imgType=photo&fileType=jpg&rights=cc_sharealike&alt=json'
        response = get_url_resource(path.format(keyword=urlencode(keyword), key=settings.GOOGLE_API_KEY, cx=settings.GOOGLE_API_CX))
        data = simplejson.loads(response)  # récupérer les données JSON d'images correspondant à la recherche
        images = data.get('items')
        results = [{'url': image['link'], 'title': image['title'], 'page': image.get('contextLink', '')} for image in images] if images else []
        return results

    # Setter
    def create_from_uri(self, path, **extra_fields):
        """ Créer une image depuis une URI """
        content_object = extra_fields.pop('content_object', None)
        picture = Picture(description=path)
        picture.update_from_description()
        picture.content_object = content_object
        for name in extra_fields.keys():
            if hasattr(picture, name) and not callable(getattr(picture, name)):
                setattr(picture, name, extra_fields[name])
        picture.save()
        return picture

    def create_from_file(self, path, **extra_fields):
        """ Créer depuis un fichier local, sans schéma d'URI """
        picture = self.create_from_uri('file://{path}'.format(path=path), **extra_fields)
        return picture

    def clear_transient(self):
        """ Supprimer les images volatiles (après 24h de délai) """
        time_limit = now() - 86400
        images = self.filter(transient=True, time__lt=time_limit)
        for image in images:
            image.delete(clear=True)

    @transaction.atomic
    def update_size(self):
        """ Mettre à jour les dimensions des images """
        for picture in self.all():
            picture.update_size()

    @staticmethod
    def clean_thumbnails():
        """ Supprimer les miniatures """
        return clean_thumbnails()

    def clear_markers(self):
        """ Supprimer les marqueurs des images du queryset """
        self.update(marker='')


class PictureQuerySet(models.QuerySet, PictureQuerySetMixin, ModeratedQuerySetMixin):
    """ Queryset des images """
    pass


class PictureManager(models.Manager.from_queryset(PictureQuerySet), models.Manager, PictureQuerySetMixin, ModeratedQuerySetMixin):
    """ Manager des images """

    # Configuration
    use_for_related_fields = True

    def get_queryset(self):
        """ Renvoyer le queryset par défaut """
        return super(PictureManager, self).get_queryset()

    # Getter
    def by_request(self, request):
        """ Renvoyer les images accessibles par un utilisateur """
        return self if request is None or request.user.is_staff else self.filter(deleted=False, moderated=True)

    def visible(self):
        """ Renvoyer les images visibles """
        return self.filter(deleted=False, transient=False, moderated=True)

    def deleted(self, **kwargs):
        """ Renvoyer les images marquées comme supprimées """
        return self.filter(deleted=True, **kwargs)


class Picture(DatetimeModel, WeightedModel, RectangleModel, ModeratedModel, FreeUUIDModel, CreationLicenseModel, AudienceModel, DataModel, ACLModel):
    """ Image """

    # Constantes
    DATA_KEYS = ['colors', 'clones', 'features']

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False, related_name='owned_pictures', on_delete=models.SET_NULL,
                               verbose_name=_("Author"))
    image = WebImageField(upload_to=ACLModel.get_acl_upload_path, max_length=240, db_index=True, width_field='width', height_field='height',
                          min_dimensions=(64, 64),
                          help_text=_("Only .gif, .jpeg or .png image files, 64x64 minimum"), verbose_name=_("Image"))
    title = models.CharField(max_length=96, blank=True, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Description text. Enter an URL here to download a picture"))
    marker = models.CharField(max_length=36, blank=True, help_text=_("Comma separated"), verbose_name=_("Internal marker"))
    uuid = UUIDField(verbose_name=_("Code"), bits=48)
    deleted = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', "Deleted"))
    animated = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', "Animated"))
    transient = models.BooleanField(default=False, db_index=False, verbose_name=pgettext_lazy('picture', "Transient"))  # temporaire avant effacement
    updated = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('picture', "Updated"))
    limit = models.Q(model__in=['profile', 'content', 'city'])  # limite de content_type
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, verbose_name=_("Content type"), limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    objects = PictureManager()

    # Getter
    @staticmethod
    def by_request(request):
        """ Renvoyer les images accessibles à l'utilisateur """
        return Picture.objects.by_request(request)

    def is_visible(self, request_user):
        """
        Renvoyer si l'image est visible à l'utilisateur

        :type request_user: HttpRequest | User
        """
        if hasattr(request_user, 'user'):
            return (self.moderated and not self.deleted) or (request_user.user.is_authenticated() and request_user.user.is_staff)
        else:
            return (self.moderated and not self.deleted) or (request_user.is_authenticated() and request_user.is_staff)

    def get_thumbnail(self, **kwargs):
        """
        Renvoyer l'URL d'une miniature de l'image

        :param kwargs: options de miniature de easy-thumbnails.
        ex. size:(w,h), crop:'smart', bw:bool, quality:0..100, format:'PNG'|'JPG'
        """
        return get_thumbnailer(self.image.name).get_thumbnail(thumbnail_options=kwargs)

    def has_animation(self, extension=None):
        """ Renvoyer si l'image possède des versions animées """
        if extension is None:
            return self.animations.exists()
        return self.animations.filter(extension=extension).exists()

    def get_animations(self):
        """ Renvoyer les instances d'animation de l'image """
        return self.animations.all()

    def get_animation_duration(self):
        """ Renvoyer la durée des animations de l'image en secondes """
        if self.animated and self.has_animation():
            return self.get_animations()[0].get_duration()
        return None

    @addattr(allow_tags=True, short_description=_("Image"))
    def get_thumbnail_html(self, *args, **kwargs):
        """ Renvoyer le HTML d'une miniature de l'image """
        if self.exists():
            try:
                size = kwargs.get('size', (48, 36))
                thumbnail_options = {'crop': 'smart', 'size': size}
                result = self.get_thumbnail(**thumbnail_options)
                template = kwargs.get('template', 'link')
                template_file = 'content/display/picture/thumbnail/{}.html'.format(template)
                output = render_to_string(template_file, {'picture': self, 'href': self.image.url, 'title': escape(self.description), 'source': result.url})
                return output
            except Exception as e:
                return '<span class="text-error" title="path:{2}">{0}</span> ({1})'.format(pgettext_lazy('thumbnail', "None"), e, self.image.name)
        return '<span class="text-error">{}</span>'.format(pgettext_lazy('thumbnail', "None"))

    @addattr(short_description=_("#"))
    def get_thumbnail_count(self):
        """ Renvoyer le nombre de miniatures de l'image """
        try:
            source = Source.objects.get(name=self.image.name)
            thumbs = Thumbnail.objects.filter(source=source)
            return thumbs.count()
        except Source.DoesNotExist:
            return 0

    @addattr(short_description=_("Filename"))
    def get_filename(self, extension=True):
        """ Renvoyer le nom du fichier """
        if self.exists():
            if extension is True:
                return os.path.basename(self.image.path)
            else:
                return os.path.splitext(os.path.basename(self.image.path))[0]
        return pgettext_lazy('file', "None")

    def _get_file_attribute_name(self):
        """ Renvoyer le nom de l'attribut fichier """
        return 'image'

    @addattr(short_description=_("Extension"))
    def get_extension(self):
        """
        Renvoyer le suffixe du fichier avec le point

        :returns: ex. ".jpg"
        """
        if self.exists():
            return os.path.splitext(self.image.path)[1].lower()
        return None

    def has_extension(self, extension):
        """
        Renvoyer si le fichier a une extension

        :param extension: extension de fichier, ex. ".gif" ou "png"
        """
        return self.get_extension().lstrip('.') == extension.lower().lstrip('.')

    @addattr(short_description=_("Size"))
    def get_file_size(self, raw=False):
        """ Renvoyer la taille du fichier au format lisible """
        if self.exists():
            return filesizeformat(self.image.size) if not raw else self.image.size
        else:
            return pgettext_lazy('size', "None") if not raw else 0

    @render_to('content/display/picture/license/default.html', string=True)
    def get_formatted_license_info(self):
        """ Renvoyer les informations de license de l'image """
        return {'picture': self}

    @staticmethod
    def _parse_scheme(uri):
        """
        Renvoyer le schema d'une URI, ex. "http://"

        :param uri: chaîne d'URI de la ressource, au format protocole://ressource
        :type uri: str
        """
        return parse.urlparse(uri).scheme

    @addattr(boolean=True, short_description=_("Is valid"))
    def exists(self):
        """ Renvoyer si le fichier existe et est valide """
        file_exists = self.id and self.image and self.image.path and default_storage.exists(self.image.name)
        if file_exists and default_storage.size(self.image.name) < 64:  # Un fichier de moins de 64 octets est nécessairement défectueux, supprimer
            default_storage.delete(self.image.name)
            file_exists = False
        return file_exists

    @addattr(short_description=_("Markers"))
    def get_markers(self):
        """ Renvoyer le marqueur splitté par virgules """
        return [marker.lower().strip() for marker in self.marker.split(',')]

    def has_marker(self, name):
        """ Renvoyer si un marqueur est associé à l'image """
        return name.lower().strip() in self.get_markers()

    def get_clones(self):
        """ Renvoyer les clones directs de l'image """
        uuids = self.get_data('clones', {})
        clones = Picture.objects.filter(uuid__in=uuids)
        return clones

    @addattr(boolean=True, short_description=_("Deletable transient"))
    def can_delete_transient(self):
        """ Renvoyer si l'image est volatile et suppressible """
        return self.transient and not self.is_new(days=2)

    @addattr(short_description=_("Duplicates found"))
    def get_google_similar_count(self, request):
        """ Renvoyer le nombre d'images similaires trouvées par Google """
        from scoop.content.templatetags.picture_tags import lookup_url
        # Charger l'URL et récupérer le nombre de résultats
        url = lookup_url(self, request)
        resource = get_url_resource(url)
        count = resource.count('h3 class="r"')
        return count

    @staticmethod
    def get_display(request, image=None, **kwargs):
        """
        Renvoyer des informations pour afficher une miniature d'image

        :param image: URL d'image ou objet du modèle content.Picture
        :param request: requête HTTP
        :param kwargs: dictionnaire des paramètres
            - alias : alias de configuration de miniature
            - options : chaîne décrivant les options easy-thumbails de génération
            - image_class : classe CSS de l'élément img
            - image_rel : attribut rel de l'élément img
            - link : doit-on afficher un lien autour de l'image ?
            - link_title : attribut title de l'élément a
            - link_class : classe CSS de l'élément a
            - link_id : ID de l'élément a
            - link_rel : attribut rel de l'élément a
            - link_target : URL ou objet avec une méthode get_absolute_url
            - image_title : attribut title de l'élément img
            - image_alt : attribut alt de l'élément img
        :rtype: dict
        """
        display = dict()
        # Afficher une image par UUID (remplacer image par uuid)
        if 'uuid' in kwargs:
            image = Picture.objects.get_by_uuid(kwargs.pop('uuid', None), default=image)
        # N'afficher que si l'objet Picture est visible pour l'objet Request
        if image is not None and isinstance(image, (Picture, str, FieldFile)):
            # Définir les informations d'affichage selon que image est un chemin ou un Picture
            if isinstance(image, Picture) and image.is_visible(request) and image.exists():
                display['image_url'] = image.image
                display['link_target'] = kwargs.pop('link_target', "{}{}".format(settings.MEDIA_URL, image.image))
                display['image_title'] = kwargs.pop('image_title', image.title)
                display['image_alt'] = kwargs.pop('image_alt', image.description)
            elif isinstance(image, (str, FieldFile)):
                display['image_url'] = image
                display['link_target'] = kwargs.pop('link_target', "{}{}".format(settings.MEDIA_URL, image))
                display['image_title'] = kwargs.pop('image_title', None)
                display['image_alt'] = kwargs.pop('image_alt', None)
            # Définir les autres options d'affichage si l'URL d'image est définie
            if display.get('image_url', False):
                display['alias'] = kwargs.pop('alias')  # alias de vignette
                display['image_class'] = kwargs.pop('image_class', None)
                display['image_rel'] = kwargs.pop('image_rel', None)
                display['link_title'] = kwargs.pop('link_title', None)
                display['link_class'] = kwargs.pop('link_class', None)
                display['link_id'] = kwargs.pop('link_id', None)
                display['link_rel'] = kwargs.pop('link_rel', None)
                display['link'] = kwargs.pop('link', True)
                display['options'] = kwargs.pop('options', None)  # options easy-thumbnails de type bool
                # Si link_target est un objet, convertir en URL
                if 'link_target' in display and hasattr(display['link_target'], 'get_absolute_url'):
                    display['link_target'] = display['link_target'].get_absolute_url()
                # Convertir l'image en thumbnail si possible
                options = kwargs
                options.update(aliases.get(display['alias'], None) or {'size': display['alias']})
                options.update(string_to_dict(display['options']))
                display['image_thumbnail'] = get_thumbnailer(display['image_url']).get_thumbnail(options)
            return display
        return None

    # Setter
    def set_description(self, description):
        """ Définir la description de l'image """
        self.description = description
        self.save(update_fields=['description'])

    def set_marker(self, content, save=True):
        """ Définir le marqueur """
        content = content[0:Picture._meta.get_field('marker').max_length]
        self.marker = content
        if save is True:
            self.save(update_fields=['marker'])

    def set_license(self, license_id, author_name, save=True):
        """
        Définir la licence et le propriétaire légal

        :param license_id: id de la license, voir scoop.core.abstract.content.license.CreationLicenseModel
        :param author_name: Nom de l'auteur (1 ou +) possédant les droits
        :type license_id: int
        """
        self.license = "{license}{sep}{author}".format(license=license_id, author=author_name,
                                                       sep=CreationLicenseModel.LICENSE_SEPARATOR)
        if save is True:
            self.save(update_fields=['license'])

    def delete_file(self):
        """ Supprimer le fichier """
        try:
            self.clean_thumbnail()
            default_storage.delete(self.image.name)
        except Exception as e:
            logger.warning(e)

    def set_from_url(self, path):
        """ Télécharger depuis une URL """
        result = download(self, path)
        return result

    def set_from_file(self, uri):
        """ Définir depuis un fichier local """
        parts = parse.urlparse(uri)
        if parts.scheme in {'', 'file'}:
            path = parts.path
            filename = os.path.basename(path)
            try:
                self.image.save(filename, File(open(path, 'rb')))
                self.title = filename
                self.save()
            except Exception as e:
                traceback.print_exc(e)
                pass

    def find_from_uri(self, uri):
        """ Définir depuis une image trouvée via une URL find:// """
        parts = parse.urlparse(uri.replace('find://', 'http://'))
        query = parse.parse_qs(parts.query)
        expression = parts.netloc
        index = query.get('id', 0)
        index = index[0] if isinstance(index, list) else index
        # Trouver une liste d'images pour l'expression
        results = Picture.objects.find_by_keyword(expression)
        if index in {'r', 'random'}:
            index = randrange(len(results))
        if int(index) < 0:
            index = 0
        elif int(index) >= len(results):
            index = len(results) - 1
        if int(index) >= 0:
            result = results[int(index)]
            self.title = result.get('title') or result.get('page')
            self.set_from_url(result.get('url'))
        return bool(results)

    def update_size(self):
        """ Mettre à jour les dimensions de l'image """
        if self.exists():
            width, height = self.width, self.height
            try:
                self.width, self.height = Image.open(self.image.path).size
            except IOError:
                self.width, self.height = None, None
            if (width, height) != (self.width, self.height):
                super(Picture, self).save(update_fields=['width', 'height'])
        else:
            Picture.objects.filter(pk=self.pk).update(width=None, height=None)

    def prepare_file_path_update(self):
        """ Préparer au déplacement du nom de fichier """
        self.clean_thumbnail()

    def set_correct_extension(self):
        """
        Renommer le fichier s'il possède la mauvaise extension

        :returns: True si le fichier est valide
        """
        if self.exists():
            extensions = {'.jpe', '.jpg', '.gif', '.png', '.tga', '.tif', '.bmp', '.jpeg', '.tiff'}
            if self.get_extension() not in extensions:
                path = self.image.path
                filename = os.path.basename(self.image.path)
                new_name = check_file_extension(filename, path, extensions)
                if new_name is not None:
                    new_path = os.path.join(os.path.dirname(path), new_name)
                    os.rename(path, new_path)
                    self.image.save(new_name, File(open(new_path)))
                    super(Picture, self).save()
                    logger.info("Picture extension set: {}".format(new_name))
                    # Si après traitement, ce n'est toujours pas une image, supprimer
                    if self.get_extension() not in extensions:
                        self.delete(clear=True)
                        logger.warning("Could not find a correct extension for {}, deleted".format(self.image.path))
                        return False
                    return True
                else:
                    self.delete(clear=True)
        return False

    def finalize(self):
        """ Définir l'image comme non temporaire """
        if self.transient is True:
            self.transient = False
            self.save(update_fields=['transient'])
            return True
        return False

    def paste(self, source_path, absolute=False, position='center center', offset=None):
        """
        Coller une autre image locale via son chemin sur cette image

        :param source_path: chemin local du fichier source, sans protocole
        :param absolute: si False, path est relatif à STATIC_ROOT
        :param position: texte de positionnement, "[left|right|center] [top|bottom|center]"
        :param offset: tuple d'offset en pixels depuis le positionnement texte
        :type offset: tuple | list
        """
        hpos, vpos = position.split(" ")
        current = Image.open(self.image.path, 'r')
        if absolute is False:
            source_path = join(settings.STATIC_ROOT, source_path)
        overlay = Image.open(source_path, 'r')
        offset = offset or (0, 0)
        xposition = {'left': 0 + offset[0], 'center': (current.size[0] - overlay.size[0]) / 2 + offset[0],
                     'right': current.size[0] - overlay.size[0] + offset[0]}
        yposition = {'top': 0 + offset[1], 'center': (current.size[1] - overlay.size[1]) / 2 + offset[1],
                     'bottom': current.size[1] - overlay.size[1] + offset[1]}
        current.paste(overlay, (xposition.get(hpos, 0), yposition.get(vpos, 0)))
        current.save(self.image.path)

    # Actions
    def clean_thumbnail(self):
        """ Supprimer les miniatures de l'image """
        if self.image:
            sources = Source.objects.filter(name=self.image.name)
            if sources.exists():
                for thumb in Thumbnail.objects.filter(source=sources[0]):
                    try:
                        os.remove(os.path.join(settings.MEDIA_ROOT, thumb.name))
                        thumb.delete()
                    except Exception as e:
                        logger.warning(e)

    def fix_exif(self):
        """ Réorienter l'image jpeg avec un champ EXIF Rotation différent de 0 """
        if self.get_extension() in {'.jpg', '.jpeg'}:
            subprocess.call(["exiftran", "-a", "-i", "-p", self.image.path], stderr=open(os.devnull, 'wb'))
            self.update_size()

    def convert(self, ext='jpg'):
        """ Convertir l'image en un format jpg ou png """
        if ext in {'png', 'jpg', 'jpeg'}:
            original_path = self.image.path
            path_basename, extension = os.path.splitext(self.image.path)
            new_basename = os.path.basename(self.image.path).replace(extension, '.{}'.format(ext), 1)
            new_path = "{}.{}".format(path_basename, ext)
            subprocess.call(["convert", "{}[0]".format(self.image.path), new_path])
            self.image.save(new_basename, File(open(new_path, 'rb')))
            os.unlink(original_path)

    def optimize(self):
        """ Optimiser la taille du fichier image """
        if self.exists():
            extension = self.get_extension()
            if extension in {".jpg", ".jpeg"}:
                subprocess.call(["jpegoptim", "-o", "-p", "--strip-com", self.image.path], stderr=open(os.devnull, 'wb'))
            elif extension == ".png":
                subprocess.call(["pngquant", "--speed", "2", "--force", "--quality", "70-100", "--ext", ".png", self.image.path], stderr=open(os.devnull, 'wb'))
                subprocess.call(["optipng", "-strip", "all", "-o7", self.image.path], stderr=open(os.devnull, 'wb'))
            return True
        return False

    def resize(self, width=None, height=None):
        """ Redimensionner l'image en conservant le ratio """
        if self.exists():
            if width is None or height is None:
                width, height = settings.DEFAULT_THUMBNAIL_DIMENSIONS.values()
            if self.width >= width or self.height >= height:
                subprocess.call(["convert", self.image.path, "-resize", "{}x{}>".format(width, height), self.image.path])
                self.update_size()

    def remove_icc(self):
        """ Supprimer le profil de couleur et les métadonnées """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-strip", self.image.path])

    def rotate(self, angle=90):
        """ Pivoter l'image dans le sens des aiguilles d'une montre """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-rotate", "{}".format(angle), self.image.path])
            self.update_size()

    def mirror(self, orientation='x'):
        """ Appliquer un miroir à l'image dans le sens x ou y """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-flop" if orientation == "x" else "-flip", self.image.path])

    def autocrop(self):
        """ Rogner automatiquement par couleur de bordure """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-fuzz", "5%", "-trim", "+repage", self.image.path])
            self.update_size()

    def autocrop_feature_detection(self):
        """ Rogner automatiquement selon les zones d'intérêt """
        if self.exists():
            image = cv2.imread(self.image.path)
            orb = cv2.ORB_create(nfeatures=500)  # Alternative libre à SIFT pour la détection de caractéristiques
            points = orb.detect(image, None)
            points, _ = orb.compute(image, points)
            coordinates = [point.pt for point in points]
            hull = convex_hull(coordinates)
            r = convex_hull_to_rect(hull)
            subprocess.call(["convert", self.image.path, "-crop", "{0}x{1}+{2}x{3}".format(r[2] - r[0], r[3] - r[1], r[0], r[1]), self.image.path])
            self.update_size()

    def detect_features(self, name, cascades=None):
        """
        Inscrire les 'caractéristiques' trouvées dans l'image

        Inscrit dans les données 'data' de l'image les informations
        sur les coordonnées des types d'objet cherchés, via OpenCV
        :param name: Nom de la feature à retrouver. Si aucun fichier de cascade Haar n'existe, ne cherche rien.
        """
        if 'features' not in self.data:
            self.data['features'] = dict()
        self.data['features'][name] = list()
        image = cv2.cvtColor(cv2.imread(self.image.path), cv2.COLOR_BGR2GRAY)  # Image en noir et blanc
        for cascade in cascades:
            cascade_file = join(Paths.get_root_dir('isolated', 'database', 'opencv', 'haar'), 'haarcascade_{0}.xml'.format(cascade))
            classifier = cv2.CascadeClassifier(cascade_file)  # Créer un classifieur avec les données de cascade
            features = classifier.detectMultiScale(image, scaleFactor=1.1, minNeighbors=3, minSize=(32, 32), maxSize=(2048, 2048))
            rectangles = [(x, y, x + w, y + h) for (x, y, w, h) in features]
            self.data['features'][name] += rectangles
        self.save(update_fields=['data'])

    def quantize(self, save=True):
        """ Convertir l'image en 8 bits avec tramage """
        if self.exists():
            if save:
                self.clone(self.description)
            subprocess.call(["convert", self.image.path, "-dither", "FloydSteinberg", "-colors", "256", self.image.path])

    def contrast(self, save=True):
        """ Augmenter le contraste dans l'espace de couleur Lab """
        if self.exists():
            if save:
                self.clone(self.description)
            subprocess.call(["convert", self.image.path,
                             "-modulate", "100,130,100", "-colorspace", "Lab", "-channel", "R",
                             "-brightness-contrast", "4x30", "+channel", "-colorspace", "sRGB",
                             self.image.path])

    def liquid(self, width=80, height=80, save=True):
        """ Redimensionner de façon liquide (seam carving) """
        if self.exists():
            if save:
                self.clone(self.description)
            subprocess.call(["convert", self.image.path, "-liquid-rescale", "{}x{}%".format(width, height), self.image.path])
            self.update_size()

    def enhance(self, save=True):
        """ Traiter l'image et améliorer son rendu """
        if self.exists():
            if save:
                self.clone(self.description)
            os.system('convert "%s" \(-clone 0 -fill "#440000" -colorize 100%%\)'
                      '-compose blend -define compose:args=20,80 -composite -sigmoidal-contrast 10x33%%'
                      '-modulate 100,75,100 -adaptive-sharpen 1x0.6 "%s"' % (self.image.path, self.image.path))
            os.system('convert "%s" \(-clone 0 -colorspace gray -channel RGB -threshold 50%% -fill "#ffddee" -opaque "#000000" -blur 12x6\)'
                      '-channel RGB -compose multiply -composite "%s"' % (self.image.path, self.image.path))
            os.system('convert "%s" \(-clone 0 -blur 30x15\) -compose dissolve -define compose:args=20 -composite "%s"' % (self.image.path, self.image.path))

    def clone(self, description=None):
        """
        Dupliquer l'image

        :param description: texte descriptif de la nouvelle image
        """
        if self.exists():
            clone = Picture(title=self.title, author=self.author, description=description or _("Clone of picture {uuid}").format(uuid=self.uuid))
            clone.set_from_file(self.image.path)
            clones = set(self.get_data('clones') or {})
            clones.add(clone.uuid)
            self.set_data('clones', clones, save=True)
            return clone

    def update_from_description(self, *args, **kwargs):
        """ Télécharger une image selon l'URI dans le champ description """
        if self.description and '://' in self.description and not self.id and not self.image:
            scheme = Picture._parse_scheme(self.description)
            if scheme == 'find':
                self.find_from_uri(self.description)
            elif scheme in {'http', 'https'}:
                self.set_from_url(self.description)
                self.title = (_("Picture ({})").format(self.get_formatted_dimension())) if not self.title else self.title
            elif scheme == 'file':
                self.set_from_file(self.description)
            if self.image:
                self.license = "1:N/A"
                super(Picture, self).save(*args, **kwargs)
            self.description = ""
            self.set_data('clones', {})
            return True
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{image}").format(image=self.title or self.description or self.get_filename())

    def __html__(self):
        """ Renvoyer la représentation HTML de l'objet """
        return self.get_thumbnail_html(size=(48, 20))

    def delete(self, *args, **kwargs):
        """ Supprimer l'image """
        for animation in self.animations.all():  # supprimer l'image
            animation.delete(*args, **kwargs)
        if kwargs.pop('clear', False):  # supprimer définitivement
            self.delete_file()
            super(Picture, self).delete(*args, **kwargs)
        else:  # sinon marquer comme supprimé
            self.deleted = True
            super(Picture, self).save(update_fields=['deleted'])

    def save(self, *args, **kwargs):
        """ Enregistrer l'image dans la base de données """
        self.updated = timezone.now()
        super(Picture, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'image """
        return self.content_object.get_absolute_url() if self.content_object and hasattr(self.content_object, 'get_absolute_url') else "#"

    # Métadonnées
    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        index_together = [['content_type', 'object_id']]
        permissions = [['can_upload_picture', "Can upload a picture"],
                       ['can_download_description_picture', "Can download a picture using a URL in description"],
                       ['can_moderate_picture', "Can moderate pictures"]]
        app_label = 'content'
