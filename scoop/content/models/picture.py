# coding: utf-8
from __future__ import absolute_import

import logging
import math
import os
import subprocess
import traceback
import urlparse
from os.path import join
from random import randrange
from traceback import print_exc
from urlparse import urljoin

import cv2
import simplejson
from django.conf import settings
from django.contrib.contenttypes import fields
from django.core.cache import cache
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.template.defaultfilters import filesizeformat, slugify, urlencode
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.models import Source, Thumbnail
from PIL import Image

from scoop.content.util.picture import clean_thumbnails, convex_hull, convex_hull_to_rect, download, get_image_upload_path
from scoop.core.abstract.content.license import AudienceModel, CreationLicenseModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.moderation import ModeratedModel, ModeratedQuerySetMixin
from scoop.core.abstract.core.rectangle import RectangleModel
from scoop.core.abstract.core.uuid import FreeUUIDModel, UUIDField
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.data.dateutil import now
from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.django.templateutil import render_to
from scoop.core.util.model.fields import WebImageField
from scoop.core.util.shortcuts import addattr
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
                print e, picture.id, picture.image
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
        path = u'https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={keyword}&searchType=image&imgType=photo&fileType=jpg&rights=cc_sharealike&alt=json'
        response = get_url_resource(path.format(keyword=urlencode(keyword), key=settings.GOOGLE_API_KEY, cx=settings.GOOGLE_API_CX))
        data = simplejson.loads(response)  # récupérer les données JSON d'images correspondant à la recherche
        images = data.get('items')
        results = [{'url': image['link'], 'title': image['title'], 'page': image.get('contextLink', '')} for image in images] if images else []
        return results

    # Setter
    def create_from_uri(self, path, **fields):
        """ Créer une image depuis une URI """
        content_object = fields.pop('content_object', None)
        picture = Picture(description=path)
        picture.update_from_description()
        picture.content_object = content_object
        for name in fields.keys():
            if hasattr(picture, name):
                setattr(picture, name, fields[name])
        picture.save()
        return picture

    def create_from_file(self, path, **fields):
        """ Créer depuis un fichier local, sans schéma d'URI """
        picture = self.create_from_uri('file://{path}'.format(path=path), **fields)
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
        clean_thumbnails()


class PictureQuerySet(models.QuerySet, PictureQuerySetMixin, ModeratedQuerySetMixin):
    """ Queryset des images """
    pass


class PictureManager(models.Manager.from_queryset(PictureQuerySet), models.Manager, PictureQuerySetMixin, ModeratedQuerySetMixin):
    """ Manager des images """
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


class Picture(DatetimeModel, WeightedModel, RectangleModel, ModeratedModel, FreeUUIDModel, CreationLicenseModel, AudienceModel):
    """ Image """
    # Constantes
    AUDIENCES = [[0, _(u"Everyone")], [5, _(u"Adults only")]]
    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=False, related_name='owned_pictures', on_delete=models.SET_NULL, verbose_name=_(u"Author"))
    image = WebImageField(upload_to=get_image_upload_path, max_length=200, db_index=True, width_field='width', height_field='height', min_dimensions=(64, 64),
                          help_text=_(u"Only .gif, .jpeg or .png image files, 64x64 minimum"), verbose_name=_(u"Image"))
    title = models.CharField(max_length=96, blank=True, verbose_name=_(u"Title"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"), help_text=_(u"Description text. Enter an URL here to download a picture"))
    marker = models.CharField(max_length=36, blank=True, help_text=_(u"Comma separated"), verbose_name=_(u"Internal marker"))
    uuid = UUIDField(verbose_name=_(u"Code"), bits=48)
    deleted = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', u"Deleted"))
    animated = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', u"Animated"))
    transient = models.BooleanField(default=False, db_index=False, verbose_name=pgettext_lazy('picture', u"Transient"))  # temporaire avant effacement
    updated = models.DateTimeField(default=timezone.now, verbose_name=pgettext_lazy('picture', u"Updated"))
    limit = models.Q(model__in=['profile', 'content', 'city'])  # limite de content_type
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, verbose_name=_(u"Content type"), limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name=_(u"Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    objects = PictureManager()

    # Getter
    @staticmethod
    def by_request(request):
        """ Renvoyer les images accessibles à l'utilisateur """
        return Picture.objects.by_request(request)

    def is_visible(self, request):
        """ Renvoyer si l'image est visible à l'utilisateur """
        return (self.moderated and not self.deleted) or (request.user.is_authenticated() and request.user.is_staff)

    def get_thumbnail(self, **kwargs):
        """
        Renvoyer l'URL d'une miniature de l'image
        :param kwargs: options de miniature de easy-thumbnails
        """
        # kwargs : size:(w,h), crop:'smart', bw:bool, quality:0..100, format:'PNG'|'JPG'
        return get_thumbnailer(self.image.name).get_thumbnail(thumbnail_options=kwargs)

    def has_animation(self, extension=None):
        """ Renvoyer si l'image possède des versions animées """
        if extension is None:
            return self.animations.exists()
        return self.animations.filter(extension=extension).exists()

    def get_animations(self):
        """ Renvoyer les instances d'animation de l'image """
        return self.animations.all()

    @addattr(allow_tags=True, short_description=_(u"Image"))
    def get_thumbnail_html(self, *args, **kwargs):
        """ Renvoyer le HTML d'une miniature de l'image """
        if self.exists():
            try:
                size = kwargs.get('size', (48, 36))
                thumbnail_options = {'crop': 'smart', 'size': size}
                result = self.get_thumbnail(**thumbnail_options)
                template = kwargs.get('template', 'link')
                template_file = u'content/display/picture/thumbnail/{}.html'.format(template)
                output = render_to_string(template_file, {'picture': self, 'href': self.image.url, 'title': escape(self.description), 'source': result.url})
                return output
            except Exception as e:
                print_exc(e)
                return u'<span class="text-error" title="path:{2}">{0}</span> ({1})'.format(pgettext_lazy('thumbnail', u"None"), e, self.image.name)
        return u'<span class="text-error">{}</span>'.format(pgettext_lazy('thumbnail', u"None"))

    @addattr(short_description=_(u"#"))
    def get_thumbnail_count(self):
        """ Renvoyer le nombre de miniatures de l'image """
        try:
            source = Source.objects.get(name=self.image.name)
            thumbs = Thumbnail.objects.filter(source=source)
            return thumbs.count()
        except Source.DoesNotExist:
            return 0

    @addattr(short_description=_(u"Filename"))
    def get_filename(self, extension=True):
        """ Renvoyer le nom du fichier """
        if self.exists():
            if extension is True:
                return os.path.basename(self.image.path)
            else:
                return os.path.splitext(os.path.basename(self.image.path))[0]
        return pgettext_lazy('file', u"None")

    @addattr(short_description=_(u"Extension"))
    def get_extension(self):
        """ Renvoyer le suffixe du fichier avec le point """
        if self.exists():
            return os.path.splitext(self.image.path)[1].lower()
        return None

    def has_extension(self, extension):
        """
        Renvoyer si le fichier a une extension
        :param extension: extension de fichier, ex. ".gif"
        """
        return self.get_extension() == extension.lower()

    @addattr(short_description=_(u"Size"))
    def get_file_size(self, raw=False):
        """ Renvoyer la taille du fichier au format lisible """
        if self.exists():
            return filesizeformat(self.image.size) if not raw else self.image.size
        else:
            return pgettext_lazy('size', u"None")

    @render_to('content/display/picture/license/default.html', string=True)
    def get_formatted_license_info(self):
        """ Renvoyer les informations de license de l'image """
        return {'picture': self}

    @staticmethod
    def _parse_scheme(uri):
        """ Renvoyer le schema d'une URI, ex. file:// """
        return urlparse.urlparse(uri).scheme

    @addattr(boolean=True, short_description=_(u"Is valid"))
    def exists(self):
        """ Renvoyer si le fichier existe et est valide """
        file_exists = self.id and self.image and self.image.path and default_storage.exists(self.image.name)
        if file_exists and default_storage.size(self.image.name) < 64:  # Un fichier de moins de 64 octets est nécessairement défectueux, supprimer
            default_storage.delete(self.image.name)
            file_exists = False
        return file_exists

    @addattr(short_description=_(u"Markers"))
    def get_markers(self):
        """ Renvoyer le marqueur splitté par virgules """
        return [marker.lower().strip() for marker in self.marker.split(',')]

    @addattr(boolean=True, short_description=_(u"Deletable transient"))
    def can_delete_transient(self):
        """ Renvoyer si l'image est volatile et suppressible """
        return self.transient and not self.is_new(days=2)

    @addattr(short_description=_(u"Duplicates found"))
    def get_google_similar_count(self, request):
        """ Renvoyer le nombre d'images similaires trouvées par Google """
        from scoop.content.templatetags.picture_tags import lookup_url


        url = lookup_url(self, request)
        resource = get_url_resource(url)
        count = resource.count('h3 class="r"')
        return count

    # Setter
    def set_marker(self, content, save=True):
        """ Définir le marqueur """
        content = content[0:Picture._meta.get_field('marker').max_length]
        self.marker = content
        if save is True:
            self.save(update_fields=['marker'])

    def set_license(self, license_id, author, save=True):
        """ Définir la licence """
        self.license = u"{license}:{author}".format(license=license_id, author=author)
        if save is True:
            self.save(update_fields=['license'])

    def delete_file(self):
        """ Supprimer le fichier """
        try:
            self.clean_thumbnail()
            default_storage.delete(self.image.name)
        except Exception, e:
            logger.warning(e)

    def set_from_url(self, path):
        """ Télécharger depuis une URL """
        result = download(self, path)
        return result

    def set_from_file(self, uri):
        """ Définir depuis un fichier local """
        parts = urlparse.urlparse(uri)
        if parts.scheme in {'', 'file'}:
            path = parts.path
            filename = os.path.basename(path)
            try:
                self.image.save(filename, File(open(path)))
                self.title = filename
                self.save()
            except Exception, e:
                traceback.print_exc(e)
                pass

    def find_from_uri(self, uri):
        """ Définir depuis une image trouvée via une URL find:// """
        parts = urlparse.urlparse(uri.replace('find://', 'http://'))
        query = urlparse.parse_qs(parts.query)
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
        return True

    def update_size(self):
        """ Mettre à jour les dimensions de l'image """
        if self.exists():
            try:
                self.width, self.height = Image.open(self.image.path).size
            except IOError:
                self.width, self.height = None, None
            super(Picture, self).save(update_fields=['width', 'height'])
        else:
            Picture.objects.filter(pk=self.pk).update(width=None, height=None)

    def update_path(self, force_name=None):
        """
        Déplacer l'image vers son chemin par défaut
        :param force_name: Forcer un nouveau nom de fichier
        :type force_name: str
        """
        if self.exists():
            # Supprimer les miniatures de l'image
            self.clean_thumbnail()
            # Changer la position du fichier
            new_path = get_image_upload_path(self, self.get_filename(), update=True)
            basename, ext = os.path.splitext(self.get_filename())
            basename = force_name if force_name else basename
            filename = "{}{}".format(slugify(basename), ext)
            output_file = os.path.join(new_path, filename)
            old_path = self.image.name
            target_path = get_image_upload_path(self, output_file)
            # Puis recréer l'image depuis le nouveau chemin
            if target_path != old_path:  # ne rien faire si le chemin est inchangé, sinon : https://docs.djangoproject.com/en/1.7/_modules/django/core/files/storage/#Storage.get_available_name
                with File(self.image) as original:
                    self.image.open()
                    self.image.save(output_file, original)
                    self.save(force_update=True)
                default_storage.delete(old_path)
                return True
        return False

    def set_correct_extension(self):
        """ Renommer le fichier s'il possède la mauvaise extension """
        if self.exists():
            extensions4, extensions5 = {'.jpe', '.jpg', '.gif', '.png', '.tga', '.tif', '.bmp'}, {'.jpeg', '.tiff'}
            if self.image.path[-4:] not in extensions4 and self.image.path[-5:] not in extensions5:
                path = self.image.path
                filename = os.path.basename(self.image.path)
                new_name = check_file_extension(filename, path, extensions4 | extensions5)
                if new_name is not None:
                    new_path = os.path.join(os.path.dirname(path), new_name)
                    os.rename(path, new_path)
                    self.image.save(new_name, File(open(new_path)))
                    super(Picture, self).save()
                    logger.info(u"Picture extension set: {}".format(new_name))
                    # Si après traitement, ce n'est toujours pas une image, supprimer
                    if self.image.path[-4:] not in extensions4 and self.image.path[-5:] not in extensions5:
                        self.delete(clear=True)
                        logger.warn(u"Could not find a correct extension for {}, deleted".format(self.image.path))
                else:
                    self.delete(clear=True)

    def finalize(self):
        """ Définir l'image comme non temporaire """
        if self.transient is True:
            self.transient = False
            self.save(update_fields=['transient'])

    def paste(self, path, absolute=False, position='center center', offset=None):
        """
        Coller une autre image locale via son chemin sur cette image
        :param path: chemin local du fichier, sans protocole
        :param absolute: si False, path est relatif à STATIC_ROOT
        :param position: texte de positionnement, "[left|right|center] [top|bottom|center]"
        :param offset: tuple d'offset en pixels depuis le positionnement texte
        :type offset: tuple or list
        """
        hpos, vpos = position.split(" ")
        current = Image.open(self.image.path, 'r')
        if absolute is False:
            path = join(settings.STATIC_ROOT, path)
        overlay = Image.open(path, 'r')
        offset = offset or (0, 0)
        xposition = {'left': 0 + offset[0], 'center': (current.size[0] - overlay.size[0]) / 2 + offset[0], 'right': current.size[0] - overlay.size[0] + offset[0]}
        yposition = {'top': 0 + offset[1], 'center': (current.size[1] - overlay.size[1]) / 2 + offset[1], 'bottom': current.size[1] - overlay.size[1] + offset[1]}
        current.paste(overlay, (xposition.get('hpos', 0), yposition.get('vpos', 0)))
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
                    except Exception, e:
                        logger.warning(e)

    def _fix_exif(self):
        """ Réorienter l'image jpeg avec un champ EXIF Rotation différent de 0 """
        if self.get_extension() in {'.jpg', '.jpeg'}:
            subprocess.call(["exiftran", "-a", "-i", "-p", self.image.path], stderr=open(os.devnull, 'wb'))

    def convert(self, ext='jpg'):
        """ Convertir l'image en un format jpg ou png """
        if ext in {'png', 'jpg', 'jpeg'}:
            original_path = self.image.path
            path_basename, extension = os.path.splitext(self.image.path)
            new_basename = os.path.basename(self.image.path).replace(extension, '.{}'.format(ext), 1)
            new_path = "{}.{}".format(path_basename, ext)
            subprocess.call(["convert", "{}[0]".format(self.image.path), new_path])
            self.image.save(new_basename, File(open(new_path)))
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

    def remove_icc(self):
        """ Supprimer le profil de couleur et les métadonnées """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-strip", self.image.path])

    def rotate(self, angle=90):
        """ Pivoter l'image dans le sens des aiguilles d'une montre """
        if self.exists():
            subprocess.call(["convert", self.image.path, "-rotate", "{}".format(angle), self.image.path])

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
        """ Rogner automatiquement par zones d'intérêt """
        if self.exists():
            image = cv2.imread(self.image.path)
            surf = cv2.xfeatures2d.SURF_create(200)
            points, _ = surf.detectAndCompute(image, None)
            coordinates = [point.pt for point in points]
            hull = convex_hull(coordinates)
            rectangle = convex_hull_to_rect(hull)
            subprocess.call(
                ["convert", self.image.path, "-crop", "{0}x{1}+{2}x{3}".format(rectangle[2] - rectangle[0], rectangle[3] - rectangle[1], rectangle[0], rectangle[1]), self.image.path])
            self.update_size()

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
            subprocess.call(["convert", self.image.path, "-modulate", "100,130,100", "-colorspace", "Lab", "-channel", "R", "-brightness-contrast", "4x30", "+channel", "-colorspace", "sRGB",
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
            os.system(
                'convert "%s" \( -clone 0 -fill "#440000" -colorize 100%% \)  -compose blend -define compose:args=20,80 -composite -sigmoidal-contrast 10x33%% -modulate 100,75,100 -adaptive-sharpen 1x0.6 "%s"' % (
                self.image.path, self.image.path))
            os.system(
                'convert "%s" \( -clone 0 -colorspace gray -channel RGB -threshold 50%% -fill "#ffddee" -opaque "#000000" -blur 12x6 \) -channel RGB -compose multiply -composite "%s"' % (
                self.image.path, self.image.path))
            os.system('convert "%s" \( -clone 0 -blur 30x15 \) -compose dissolve -define compose:args=20 -composite "%s"' % (self.image.path, self.image.path))

    def clone(self, description=None):
        """ Dupliquer l'image """
        if self.exists():
            clone = Picture(description=urljoin(settings.DOMAIN_NAME, self.image.url), title=self.title, author=self.author)
            clone.save()
            clone.description = (description or _(u"Clone of picture {uuid}")).format(uuid=self.uuid)
            clone.update_path(force_name=uuid_bits(48))
            return clone

    def update_from_description(self, *args, **kwargs):
        """ Télécharger une image selon l'URI dans le champ description """
        if self.description and '://' in self.description and not self.id and not self.image:
            scheme = Picture._parse_scheme(self.description)
            if scheme == 'find':
                self.find_from_uri(self.description)
            elif scheme in {'http', 'https'}:
                self.set_from_url(self.description)
                self.title = (_(u"Picture ({})").format(self.get_formatted_dimension())) if not self.title else self.title
            elif scheme == 'file':
                self.set_from_file(self.description)
            if self.image:
                self.license = "1:N/A"
                super(Picture, self).save(*args, **kwargs)
            self.description = ""
            return True
        return False

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _(u"{image}").format(image=self.title or self.description or self.get_filename())

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
        verbose_name = _(u'image')
        verbose_name_plural = _(u'images')
        index_together = [['content_type', 'object_id']]
        permissions = [['can_upload_picture', u"Can upload a picture"],
                       ['can_moderate_picture', u"Can moderate pictures"]]
        app_label = 'content'
