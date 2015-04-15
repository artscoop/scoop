# coding: utf-8
""" Animations vidéo associées à des images """
from __future__ import absolute_import

import os
import re
import subprocess
from subprocess import STDOUT, check_output

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.content.util.picture import get_animation_upload_path
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID128Model
from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class AnimationManager(SingleDeleteManager):
    """ Manager des animations """
    # Constantes
    CODECS = {'mp4': 'h264', 'webm': 'libvpx', 'ogg': 'libtheora'}

    def get_html_for_picture(self, picture, width=None):
        """ Récupérer le code HTML de la vidéo pour un objet Picture """
        animations = self.filter(picture=picture)[0:8]
        if animations.exists():
            return render_to_string("content/display/animation/html/default-set.html", {'animations': animations, 'width': width or 160})
        return u""

    def create_from_animation(self, picture, extensions=None, reset=False):
        """ Créer des objets animation pour l'objet Picture """
        from scoop.content.models import Picture

        if isinstance(picture, basestring):
            picture = Picture.objects.get_by_uuid(picture)
        extensions = extensions or ['mp4', 'webm', 'ogg']
        if picture is not None and picture.get_extension() in {'.gif'}:
            if reset is True:
                picture.get_animations().delete()
            for extension in [extension for extension in extensions if extension in AnimationManager.CODECS.keys()]:
                if not picture.has_extension(extension):
                    sequence_name = uuid_bits(32)
                    new_filename = "{}.{extension}".format(uuid_bits(48), extension=extension)
                    temp_path = "/tmp/{}".format(new_filename)
                    subprocess.call(['convert', picture.image.path, '-coalesce', '/tmp/{}%05d.jpg'.format(sequence_name)], stderr=open(os.devnull, 'wb'))
                    subprocess.call(['avconv', '-i', '/tmp/{}%05d.jpg'.format(sequence_name), '-vf', 'scale=trunc(in_w/2)*2:trunc(in_h/2)*2', '-c', AnimationManager.CODECS[extension], temp_path], stderr=open(os.devnull, 'wb'))
                    animation = Animation(extension=extension, description=picture.description)
                    animation.picture = picture
                    animation.file.save(new_filename, File(open(temp_path)))
                    animation.get_duration(save=True)  # Renvoie ou calcule la durée de l'animation
                    animation.save()
                    # Nettoyer les fichiers temporaires
                    os.popen('rm /tmp/{}*.jpg && rm {}'.format(sequence_name, temp_path))
            # Remplacer l'image GIF par un aperçu
            picture.convert()  # JPG par défaut
        else:
            picture.animated = False
            super(Picture, picture).save()


class Animation(DatetimeModel, UUID128Model):
    """ Animation vidéo """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='owned_animations', on_delete=models.SET_NULL, verbose_name=_(u"Author"))
    file = models.FileField(max_length=192, upload_to=get_animation_upload_path, verbose_name=_(u"File"))
    picture = models.ForeignKey('content.Picture', null=True, blank=True, on_delete=models.CASCADE, related_name='animations', verbose_name=_(u"Picture"))
    extension = models.CharField(max_length=8, default='mp4', verbose_name=_(u"Extension"))
    duration = models.FloatField(default=0.0, editable=False, db_index=True, help_text=_(u"In seconds"), verbose_name=_(u"Duration"))
    title = models.CharField(max_length=96, blank=True, verbose_name=_(u"Title"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"), help_text=_(u"Description text. Enter an URL here to download a picture"))
    autoplay = models.BooleanField(default=False, verbose_name=_(u"Auto play"))
    loop = models.BooleanField(default=True, verbose_name=_(u"Loop"))
    deleted = models.BooleanField(default=False, verbose_name=pgettext_lazy('picture', u"Deleted"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('picture', u"Updated"))
    objects = AnimationManager()

    # Getter
    def is_visible(self, request):
        """ Renvoyer la visibilité de l'animation """
        if request is None or self.picture is None or request.user.is_staff:
            return True
        return self.picture.is_visible(request)

    @addattr(short_description=_(u"Valid"))
    def is_valid(self):
        """ Renvoyer la validité de l'objet """
        duration = self.get_duration(save=True)
        return duration > 0

    @addattr(boolean=True, short_description=_(u"Is valid"))
    def exists(self):
        """ Renvoyer True si le fichier existe """
        return self.id and self.file and self.file.path and default_storage.exists(self.file.name)

    def get_html(self, width=None):
        """
        Renvoyer le markup HTML d'affichage de l'animation
        :param width: largeur en pixels pour afficher la vidéo
        """
        return render_to_string("content/display/animation/html/default-set.html", {'animations': [self], 'width': width or 160})

    @addattr(short_description=_(u"Filename"))
    def get_filename(self):
        """ Renvoyer le nom du fichier de l'animation """
        if self.exists():
            return os.path.basename(self.file.path)
        return pgettext_lazy('file', u"None")

    @addattr(short_description=_(u"Duration"))
    def get_duration(self, save=False):
        """ Renvoyer la durée de l'animation en secondes """
        if self.duration == 0:
            try:
                output = check_output(u"""avprobe -of json -show_streams {}""".format(self.file.path), shell=True, stderr=STDOUT)
                matches = re.search(r"Duration\: (\d+)\:(\d+)\:([\d\.]+)", output)
                hours, minutes, seconds = [float(group) for group in matches.groups()]
                total_seconds = hours * 3600.0 + minutes * 60.0 + seconds
                self.duration = total_seconds
                if save is True:
                    self.save(update_fields=['duration'])
                return self.duration
            except Exception:
                return 0
        else:
            return self.duration

    @addattr(short_description=_(u"Extension"))
    def get_extension(self):
        """ Renvoyer l'extension du fichier vidéo """
        if self.exists():
            return os.path.splitext(self.file.path)[1].lower()
        return None

    @addattr(short_description=_(u"Size"))
    def get_file_size(self, raw=False):
        """
        Renvoyer la taille du fichier en chaîne lisible
        :param raw: définit si une taille en octets est retournée
        """
        if self.exists():
            return filesizeformat(self.file.size) if not raw else self.file.size
        else:
            return pgettext_lazy('size', u"None")

    # Setter
    def delete_file(self):
        """ Supprimer le fichier lié à l'animation """
        if self.exists():
            try:
                default_storage.delete(self.file.name)
            except Exception:
                pass

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if kwargs.pop('clear', False):
            self.delete_file()
            super(Animation, self).delete(*args, **kwargs)
        else:
            self.deleted = True
            super(Animation, self).save(update_fields=['deleted'])

    # Métadonnées
    class Meta:
        verbose_name = _(u"Animation")
        verbose_name_plural = _(u"Animations")
        app_label = 'content'
