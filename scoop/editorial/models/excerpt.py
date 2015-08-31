# coding: utf-8
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from markdown import Markdown
from translatable.models import TranslatableModel, get_translation_model

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.shortcuts import addattr
from scoop.editorial.util.languages import get_country_code


class Excerpt(TranslatableModel, DatetimeModel, AuthoredModel, WeightedModel, UUID64Model):
    """ Extrait de texte """
    # Constantes
    FORMATS = [[0, _("Plain HTML")], [1, _("Markdown")], [2, _("Textile")], [3, _("reStructured Text")], ]
    TRANSFORMS = {1: Markdown().convert}
    # Champs
    name = models.CharField(max_length=48, unique=True, blank=False, verbose_name=_("Name"))
    title = models.CharField(max_length=80, unique=True, blank=False, verbose_name=_("Title"))
    visible = models.BooleanField(default=True, verbose_name=pgettext_lazy('excerpt', "Visible"))
    format = models.SmallIntegerField(choices=FORMATS, default=0, verbose_name=_("Format"))
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))
    libraries = models.CharField(max_length=40, help_text=_("{% load %} libraries, comma separated"), verbose_name=_("Tag libs"))

    # Overrides
    def __unicode__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return "{title} ({name})".format(title=self.title, name=self.name)

    # Getter
    @addattr(short_description=_("Text"))
    def get_text(self):
        """ Renvoyer le texte de l'extrait """
        try:
            return self.get_translation().text
        except:
            return _("(No text)")

    def html(self):
        """ Renvoyer le code HTML de l'extrait (selon le format) """
        content = Excerpt.TRANSFORMS.get(self.format, lambda s: s)(self.get_text())
        return content

    @addattr(allow_tags=True, short_description=_("Languages"))
    def get_language_icons_html(self):
        """ Renvoyer une icone correspondant à la langue de l'extrait """
        output = []
        for translation in self.translations.all():
            output.append(u'<img src="%(url)stool/assets/icons/flag/png/%(code)s.png">' % {'code': get_country_code(translation.language), 'url': settings.STATIC_URL})
        return " ".join(output)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Excerpt, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("excerpt")
        verbose_name_plural = _("excerpts")
        app_label = 'editorial'


class ExcerptTranslation(get_translation_model(Excerpt, "excerpt"), TranslationModel):
    """ Traduction d'un extrait """
    text = models.TextField(blank=False, verbose_name=_("Text"))

    # Métadonnées
    class Meta:
        app_label = 'editorial'
