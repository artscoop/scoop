# coding: utf-8
""" Contenus texte """
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, TranslatableModelManager, get_translation_model

from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


logger = logging.getLogger(__name__)


class CategoryManager(SingleDeleteManager, TranslatableModelManager):
    """ Manager des types de contenus """

    def get_by_natural_key(self, url):
        """ Clé naturelle """
        return self.get(url=url)

    def get_by_name(self, name):
        """ Renvoyer un type de contenu selon nom de code """
        candidates = self.filter(short_name__iexact=name)
        return candidates.first() if candidates.exists() else None

    def get_by_url(self, url):
        """ Renvoyer un type de contenu selon son url"""
        candidates = self.filter(url=url.lower())
        return candidates.first() if candidates.exists() else None


class Category(TranslatableModel, IconModel, DataModel):
    """
    Type de contenu

    Sépare les contenus par URL de base.
    Permet d'assigner des métadonnées à des types de contenu.
    Permet aussi d'utiliser des templates différents selon
    le tyoe de contenu.
    """

    # Champs
    short_name = models.CharField(max_length=10, verbose_name=_("Identifier"))
    url = models.CharField(max_length=16, help_text=_("e.g. blog, story or article"), verbose_name=_("URL"))
    has_index = models.BooleanField(default=True, verbose_name=_("Has index"))
    visible = models.BooleanField(default=True, verbose_name=_("Visible"))
    objects = CategoryManager()

    # Getter
    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom au singulier du type de contenu """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _("(No name)")

    @addattr(short_description=_("Plural"))
    def get_plural(self):
        """ Renvoyer le nom au pluriel du type de contenu """
        try:
            return self.get_translation().plural
        except MissingTranslation:
            return _("(No name)")

    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description du type de contenu """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    def get_contents(self, **kwargs):
        """ Renvoyer tous les contenus correspondant à ce type """
        return self.contents.filter(**kwargs)

    # Propriétés
    name = property(get_name)
    plural = property(get_plural)
    description = property(get_description)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.url = self.url.lower().strip()
        super(Category, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if not self.content_set.all().exists():
            super(Category, self).delete(*args, **kwargs)

    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return str(self.get_name())

    # Métadonnées
    class Meta:
        verbose_name = _("content type")
        verbose_name_plural = _("content types")
        app_label = 'content'


class CategoryTranslation(get_translation_model(Category, "category"), TranslationModel):
    """ Traduction de type de contenu """

    # Champs
    name = models.CharField(max_length=64, blank=False, verbose_name=_("Name"))
    plural = models.CharField(max_length=64, blank=False, default="__", verbose_name=_("Plural"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.plural == self._meta.get_field('plural').default:
            self.plural = "{}s".format(self.name)
        super(CategoryTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'content'
        verbose_name = _("translation")
        verbose_name_plural = _("translations")
