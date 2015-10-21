# coding: utf-8
import os

from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from easy_thumbnails.fields import ThumbnailerImageField

from scoop.core.util.shortcuts import addattr


def get_icon_upload_path(self, name):
    """ Renvoyer le chemin d'upload d'une icône """
    from django.contrib.contenttypes.fields import ContentType
    # Constituer les dictionnaires d'information de fichier
    content_type = ContentType.objects.get_for_model(self)
    format_data = {'app': content_type.app_label, 'model': content_type.name}
    # Dictionnaire d'informations pour constituer un répertoire
    now = timezone.now()
    fmt = now.strftime
    # Remplir le dictionnaire avec les informations de répertoire
    dir_info = {'year': fmt("%Y"), 'month': fmt("%m"), 'day': fmt("%d")}
    # Remplir les données pour le nom de fichier
    name_info = {'name': os.path.splitext(name)[0], 'ext': os.path.splitext(name)[1]}
    # Données de préfixe
    prefix_info = {'hour': fmt("%H"), 'minute': fmt("%M"), 'second': fmt("%S")}
    # Renvoyer le nom de fichier avec un patchwork de ces informations
    data = dict(dir_info.items() + name_info.items() + prefix_info.items() + format_data.items())
    return "file/icon/{app}/{model}/{year}/{name}{ext}".format(**data)


class IconModel(models.Model):
    """ Mixin de modèle avec une icône """
    # Constantes
    ICON_MAX_SIZE = {'w': 64, 'h': 64}
    # Champs
    icon = ThumbnailerImageField(max_length=96, blank=True, resize_source={'size': (ICON_MAX_SIZE['w'], ICON_MAX_SIZE['h']), 'crop': 'smart'}, width_field='icon_width',
                                 height_field='icon_height', upload_to=get_icon_upload_path, help_text=_("Maximum size {}x{}").format(ICON_MAX_SIZE['w'], ICON_MAX_SIZE['h']),
                                 verbose_name=_("Icon"))
    icon_width = models.IntegerField(blank=True, null=True, editable=False, verbose_name=pgettext_lazy("geometry", "Width"))
    icon_height = models.IntegerField(blank=True, null=True, editable=False, verbose_name=pgettext_lazy("geometry", "Height"))

    # Getter
    @addattr(allow_tags=True, short_description=_("Icon"))
    def get_icon_html(self):
        """ Renvoyer la représentation HTML de l'icône """
        return """<img src="{url}">""".format(url=self.icon.url) if self.icon else ""

    @addattr(allow_tags=True, short_description=_("Image"))
    def get_icon_thumbnail_html(self, *args, **kwargs):
        """ Renvoyer une miniature de l'icône """
        if self.icon:
            try:
                size = kwargs.get('size', (48, 36))
                thumbnail_options = {'crop': 'smart', 'size': size}
                result = self.icon.get_thumbnail(thumbnail_options)
                template = kwargs.get('template', 'link')
                template_file = 'content/display/picture/thumbnail/{}.html'.format(template)
                output = render_to_string(template_file, {'picture': self.icon, 'href': self.icon.url, 'title': escape(self.description), 'source': result.url})
                return output
            except Exception as e:
                return '<span class="text-error">{}</span> ({})'.format(pgettext_lazy('thumbnail', "None"), e)
        return '<span class="text-error">{}</span>'.format(pgettext_lazy('thumbnail', "None"))

    def icon_exists(self):
        """ renvoyer si le fichier de l'icône existe """
        return os.path.exists(self.icon.path)

    # Métadonnées
    class Meta:
        abstract = True
