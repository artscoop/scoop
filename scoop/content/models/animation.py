# coding: utf-8
""" Animations vidéo associées à des images """
import logging
import os
import re
import subprocess
from subprocess import STDOUT, check_output
from traceback import print_exc

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.core.files.temp import gettempdir
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.content.acl import ACLModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID128Model
from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr

logger = logging.getLogger(__name__)


class AnimationManager(SingleDeleteManager):
    """ Manager des animations """

    # Constantes
    CODECS = {'mp4': 'h264', 'webm': 'libvpx', 'ogg': 'libtheora'}

    # Getter
    def get_html_for_picture(self, picture, width=None):
        """ Récupérer le code HTML de la vidéo pour un objet Picture """
        animations = self.for_picture(picture)[0:8]
        if animations.exists():
            return render_to_string("content/display/animation/html/default-set.html", {'animations': animations, 'width': width or 160})
        return ""

    def for_picture(self, picture):
        """
        Renvoie les objets animation pour l'image désignée

        :type picture: scoop.content.models.Picture
        """
        return self.filter(picture=picture)

    # Setter
    def create_from_animation(self, picture, extensions=None, reset=False):
        """
        Créer des objets animation pour l'objet Picture

        :type picture: scoop.content.models.Picture | str
        :param reset: Supprimer les animations existantes et les recréer ?
        :param extensions: liste des extensions de sortie, sans le point
        :type reset: bool
        """
        from scoop.content.models import Picture

        if not os.path.exists('/usr/bin/avconv'):
            raise ImproperlyConfigured("You must install anvconv to convert pictures.\nIn Ubuntu 14.04+, run 'apt-get install libav-tools'")
        if isinstance(picture, str):
            picture = Picture.objects.get_by_uuid(picture)
        extensions = extensions or ['mp4']  # mp4 pris en charge par tous les navigateurs pop.
        if isinstance(picture, Picture) and picture.get_extension() in {'.gif'}:
            if reset is True:
                picture.get_animations().delete()
            for extension in [extension for extension in extensions if extension in AnimationManager.CODECS.keys()]:
                # Convertir dans tous les formats de CODECS
                if not picture.has_extension(extension):
                    sequence_name = uuid_bits(32)
                    temp_dir = gettempdir()
                    new_filename = "{0}.{extension}".format(uuid_bits(48), extension=extension)
                    temp_path = "/{tmp}/{0}".format(new_filename, tmp=temp_dir)
                    subprocess.call(['convert', picture.image.path, '-coalesce', '/{tmp}/{0}%05d.jpg'.format(sequence_name, tmp=temp_dir)],
                                    stderr=open(os.devnull, 'wb'))
                    subprocess.call(['avconv', '-i', '/tmp/{0}%05d.jpg'.format(sequence_name), '-vf', 'scale=trunc(in_w/2)*2:trunc(in_h/2)*2', '-c',
                                     AnimationManager.CODECS[extension], temp_path], stderr=open(os.devnull, 'wb'))
                    animation = Animation(extension=extension, description=picture.description)
                    animation.picture = picture
                    animation.file.save(new_filename, File(open(temp_path, 'rb')))
                    animation.get_duration(save=True)  # Renvoie ou calcule la durée de l'animation
                    animation.save()
                    # Nettoyer les fichiers temporaires
                    os.popen('rm /{tmp}/{0}*.jpg && rm {1}'.format(sequence_name, temp_path, tmp=temp_dir))
            # Remplacer l'image GIF par un aperçu
            picture.convert()  # JPG par défaut
            picture.animated = True
            super(Picture, picture).save()
        else:
            picture.animated = False
            super(Picture, picture).save()


class Animation(DatetimeModel, UUID128Model, ACLModel):
    """ Animation vidéo """

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='owned_animations', on_delete=models.SET_NULL,
                               verbose_name=_("Author"))
    file = models.FileField(max_length=192, upload_to=ACLModel.get_acl_upload_path, verbose_name=_("File"))
    picture = models.ForeignKey('content.Picture', null=True, blank=True, on_delete=models.CASCADE, related_name='animations', verbose_name=_("Picture"))
    extension = models.CharField(max_length=8, default='mp4', verbose_name=_("Extension"))
    duration = models.FloatField(default=0.0, editable=False, db_index=True, help_text=_("In seconds"), verbose_name=_("Duration"))
    title = models.CharField(max_length=96, blank=True, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Description text. Enter an URL here to download a picture"))
    autoplay = models.BooleanField(default=False, verbose_name=_("Auto play"))
    loop = models.BooleanField(default=True, verbose_name=_("Loop"))
    deleted = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', "Deleted"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('picture', "Updated"))
    objects = AnimationManager()

    # Getter
    @addattr(short_description=pgettext_lazy('animation', "Visible"))
    def is_visible(self, request):
        """ Renvoyer la visibilité de l'animation """
        if request is None or self.picture is None or request.user.is_staff:
            return True
        return self.picture.is_visible(request)

    @addattr(short_description=pgettext_lazy('animation', "Valid"))
    def is_valid(self):
        """ Renvoyer la validité de l'objet """
        duration = self.get_duration(save=True)
        return duration > 0

    @addattr(boolean=True, short_description=pgettext_lazy('animation', "Valid"))
    def exists(self):
        """ Renvoyer True si le fichier existe """
        return self.id and self.file and self.file.path and default_storage.exists(self.file.name)

    @addattr(short_description=_("HTML"))
    def get_html(self, width=None):
        """
        Renvoyer le markup HTML d'affichage de l'animation
        :param width: largeur en pixels pour afficher la vidéo
        """
        return render_to_string("content/display/animation/html/default-set.html", {'animations': [self], 'width': width or 160})

    @addattr(short_description=_("Filename"))
    def get_filename(self):
        """ Renvoyer le nom du fichier de l'animation """
        if self.exists():
            return os.path.basename(self.file.path)
        return pgettext_lazy('file', "None")

    @addattr(short_description=_("Duration"))
    def get_duration(self, save=False):
        """ Renvoyer la durée de l'animation en secondes """
        if self.duration == 0:
            try:
                output = check_output("""avprobe -of json -show_streams {}""".format(self.file.path), shell=True, stderr=STDOUT)
                matches = re.search(r"Duration: .{0,15}(\d{2,4}):(\d{2}):(\d{2}\.\d+)", str(output))
                if matches:
                    hours, minutes, seconds = [float(group) for group in matches.groups()]
                    total_seconds = hours * 3600.0 + minutes * 60.0 + seconds
                    self.duration = total_seconds
                    if save is True:
                        self.save(update_fields=['duration'])
                    return self.duration
                else:
                    return 0
            except TypeError as e:
                print_exc(e)
                return -1.0
        else:
            return self.duration

    @addattr(short_description=_("Extension"))
    def get_extension(self):
        """ Renvoyer l'extension du fichier vidéo """
        if self.exists():
            return os.path.splitext(self.file.path)[1].lower()
        return None

    @addattr(short_description=_("Size"))
    def get_file_size(self, raw=False):
        """
        Renvoyer la taille du fichier en chaîne lisible

        :param raw: définit si une taille en octets est retournée (int)
        :returns: la taille du fichier en octets ou en chaîne lisible
        :rtype: int | str
        """
        if self.exists():
            return filesizeformat(self.file.size) if not raw else self.file.size
        else:
            return pgettext_lazy('size', "None")

    def _get_file_attribute_name(self):
        """ Renvoyer le nom de l'attribut fichier """
        return 'file'

    # Setter
    def delete_file(self):
        """ Supprimer le fichier lié à l'animation """
        if self.exists():
            try:
                default_storage.delete(self.file.name)
            except (NotImplementedError,):
                logger.warning("Could not delete file {path}".format(path=self.file.name))
                pass

    # Overrides
    def delete(self, *args, **kwargs):
        """
        Supprimer l'objet de la base de données

        :param clear: supprimer totalement l'objet du disque et de la base
        :type clear: bool
        """
        if kwargs.pop('clear', False):
            self.delete_file()
            super(Animation, self).delete(*args, **kwargs)
        else:
            self.deleted = True
            super(Animation, self).save(update_fields=['deleted'])

    # Métadonnées
    class Meta:
        verbose_name = _("Animation")
        verbose_name_plural = _("Animations")
        app_label = 'content'
