# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from translatable.models import get_translation_model

from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.shortcuts import addattr


class VenueType(PicturableModel):
    """ Type de lieu """
    short_name = models.CharField(max_length=32, blank=False, db_index=True, verbose_name=_(u"Short name"))
    parent = models.ForeignKey('self', null=True, related_name='children', verbose_name=_(u"Parent"))

    # Getter
    @addattr(short_description=_(u"Name"))
    def get_name(self):
        """ Renvoyer le nom du type de lieu """
        try:
            return self.get_translation().name
        except:
            return _(u"(No name)")

    @addattr(short_description=_(u"Plural"))
    def get_plural(self):
        """ Renvoyer le nom du type de lieu au pluriel """
        try:
            return self.get_translation().plural
        except:
            return _(u"(No name)")

    @addattr(short_description=_(u"Description"))
    def get_description(self):
        """ Renvoyer la description du type de lieu """
        try:
            return self.get_translation().description
        except:
            return _(u"(No description)")

    def get_children(self):
        """ Renvoyer les types enfants """
        return self.children.all()

    # Métadonnées
    class Meta:
        verbose_name = _(u"venue type")
        verbose_name_plural = _(u"venue types")
        app_label = 'location'


class VenueTypeTranslation(get_translation_model(VenueType, "venuetype"), TranslationModel):
    """ Traduction de type de lieu """
    name = models.CharField(max_length=48, blank=False, verbose_name=_(u"Name"))
    plural = models.CharField(max_length=48, blank=False, default="__", verbose_name=_(u"Plural"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.plural == '__':
            self.plural = "{}s".format(self.name)
        super(VenueTypeTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'location'
