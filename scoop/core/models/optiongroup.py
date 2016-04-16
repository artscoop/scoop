# coding: utf-8
from django.apps.registry import apps
from django.db import models
from django.db.models.base import Model
from django.db.utils import ProgrammingError
from django.utils.translation import ugettext_lazy as _
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model

from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class OptionGroupManager(SingleDeleteManager):
    """ Manager des groupes d'options """

    # Getter
    def get_by_name(self, name):
        """ Renvoie un groupe d'options avec un nom court """
        try:
            return self.get(short_name=name.lower())
        except (OptionGroup.DoesNotExist, ProgrammingError):
            return None


class OptionGroup(TranslatableModel, PicturableModel if apps.is_installed('scoop.content') else Model):
    """ Groupe d'options """

    # Choix de codes
    CODES = [[i, i] for i in range(100)]

    # Champs
    code = models.SmallIntegerField(null=False, blank=False, default=0, verbose_name=_("Code"))
    short_name = models.CharField(max_length=20, verbose_name=_("Short name"))
    objects = OptionGroupManager()

    # Getter
    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom du groupe """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _("(No name)")

    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description du groupe """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _("(No description)")

    def get_options(self, active_only=True):
        """ Renvoyer les options du groupe """
        criteria = {'active': True} if active_only else {}
        return self.options.filter(**criteria).order_by('code')

    # Propriétés
    name = property(get_name)
    description = property(get_description)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "%(id)s : %(name)s" % {'id': self.id, 'name': self.get_name() or self.short_name, 'short': self.short_name}

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(OptionGroup, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("option group")
        verbose_name_plural = _("option groups")
        ordering = ['id']
        app_label = 'core'


class OptionGroupTranslation(get_translation_model(OptionGroup, "optiongroup"), TranslationModel):
    """ Traduction de groupe d'options """
    # Champs
    name = models.CharField(max_length=80, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Métadonnées
    class Meta:
        app_label = 'core'
