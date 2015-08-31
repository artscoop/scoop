# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model

from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID32Model
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class EventCategoryManager(SingleDeleteManager):
    """ Manager des catégories d'événements """

    # Getter
    def get_queryset(self):
        """ Renvoyer le queryset par défaut"""
        return super(EventCategoryManager, self).get_queryset()

    def get_public(self):
        """ Renvoyer les types d'événements publics """
        return self.filter(public=True)

    def get_by_name(self, name):
        """ Renvoyer les catégories d'événements par nom """
        return self.filter(translations__name__icontains=name)

    def get_by_parent_name(self, name):
        """ Renvoyer les catégories par nom de parent """
        return self.filter(parent__translations__name__icontains=name)


class EventCategory(TranslatableModel, IconModel, UUID32Model):
    """ Catégorie d'événement """
    # Champs
    parent = models.ForeignKey('self', null=True, related_name='children', verbose_name=_("Parent"))
    public = models.BooleanField(default=True, verbose_name=_("Public"))
    objects = EventCategoryManager()

    # Getter
    @addattr(admin_order_field='translations__name', short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom de la catégorie """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _("(No name)")

    @addattr(admin_order_field='translations__description', short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description de la catégorie """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    def get_children(self):
        """ Renvoyer les catégories enfants """
        return self.children.all()

    # Propriétés
    name = property(get_name)

    # Métadonnées
    class Meta:
        verbose_name = _("event category")
        verbose_name_plural = _("event categories")
        app_label = "social"


class EventCategoryTranslation(get_translation_model(EventCategory, "eventcategory"), TranslationModel):
    """ Traduction de catégorie d'événements """
    # Champs
    name = models.CharField(max_length=48, blank=False, verbose_name=_("Name"))
    description = models.TextField(default="", blank=True, verbose_name=_("Description"))

    # Métadonnées
    class Meta:
        app_label = 'social'
