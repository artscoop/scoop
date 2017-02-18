# coding: utf-8
from autoslug.fields import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model, TranslatableModelManager


class HelpGroupQuerySet(models.QuerySet, TranslatableModelManager):
    """ Manager de l'aide """

    # Getter
    def active(self):
        """ Renvoyer les groupes actifs """
        return self.filter(active=True)

    def get_by_uuid(self, uuid):
        """ Renvoyer une page portant un UUID """
        return self.get(uuid=uuid)

    def get_by_slug(self, slug):
        """ Renvoyer une page portant un slug """
        return self.get(slug=slug)


class HelpGroup(DatetimeModel, UUID64Model, TranslatableModel, WeightedModel):
    """
    Groupe d'aide

    Un groupe d'aide permet d'organiser les éléments d'aide dans des
    catégories spécifiques.
    """

    # Champs
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('group', "Active"))
    name = models.CharField(max_length=32, blank=False, unique=True, verbose_name=_("Codename"))
    slug = AutoSlugField(max_length=128, populate_from='name', unique_with=['id'], blank=False, verbose_name=_("Slug"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('page', "Updated"))
    objects = HelpGroupQuerySet.as_manager()

    # Getter
    @addattr(short_description=_("Text"))
    def get_text(self):
        """ Renvoyer la description de l'option """
        try:
            return self.get_translation().text
        except MissingTranslation:
            return _("(No text)")

    @addattr(short_description=_("Title"))
    def get_title(self):
        """ Renvoyer le titre de la page """
        try:
            return self.get_translation().title
        except MissingTranslation:
            return _("(No title)")

    # Propriétés
    text = property(get_text)
    title = property(get_title)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return "help group - {0}".format(self.slug)

    # Métadonnées
    class Meta:
        verbose_name = _("Help group")
        verbose_name_plural = _("Help groups")
        app_label = 'help'


class HelpGroupTranslation(get_translation_model(HelpGroup, "helpgroup"), TranslationModel):
    """ Traduction des pages """

    # Champs
    title = models.CharField(max_length=128, blank=False, verbose_name=_("Title"))
    text = models.TextField(blank=False, help_text=_("Markdown"), verbose_name=_("Text"))

    # Métadonnées
    class Meta:
        app_label = 'help'
