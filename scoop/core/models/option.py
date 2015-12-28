# coding: utf-8
from django.db import models
from django.db.models.base import Model
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy, ugettext
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model
from unidecode import unidecode
from django.apps.registry import apps


class OptionManager(SingleDeleteManager):
    """ Manager des options """

    # Getter
    def get_by_natural_key(self, uuid):
        """ Renvoyer une option par sa clé naturelle """
        return self.get(uuid=uuid)

    def in_group(self, name):
        """ Renvoyer les options faisant partie d'un groupe nommé """
        from scoop.core.models import OptionGroup
        # Renvoyer un queryset vide si le groupe n'existe pas
        try:
            group = OptionGroup.objects.get_by_name(name)
            return self.filter(group=group)
        except OptionGroup.DoesNotExist:
            return self.none()

    def get_by_code(self, group, code, active_only=True):
        """ Renvoyer l'ooption d'un groupe avec un code précis """
        if isinstance(group, str):
            return self.get(group__short_name=group, code=code, **({'active': True} if active_only else {}))
        return self.get(group__id=group, code=code, **({'active': True} if active_only else {}))


class Option(TranslatableModel, UUID64Model, PicturableModel if apps.is_installed('content') else Model):
    """ Option """

    # Choix de codes
    CODES = [[i, i] for i in range(200)]

    # Champs
    group = models.ForeignKey('core.OptionGroup', null=False, blank=False, related_name='options', verbose_name=_("Group"))
    code = models.SmallIntegerField(null=False, blank=False, choices=CODES, db_index=True, verbose_name=_("Code"))
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('option', "Active"))
    parent = models.ForeignKey('core.Option', null=True, blank=True, related_name='children', on_delete=models.SET_NULL, verbose_name=_("Parent"))
    objects = OptionManager()

    # Getter
    def natural_key(self):
        """ Renvoyer la clé naturelle de l'objet """
        return self.uuid,

    @addattr(short_description=_("Name"))
    def get_name(self):
        """ Renvoyer le nom de l'option """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return ugettext("(No name)")

    @addattr(short_description=_("Description"))
    def get_description(self):
        """ Renvoyer la description de l'option """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return ugettext("(No description)")

    def get_children(self):
        """ Renvoyer les descendants de l'option """
        return Option.objects.filter(parent=self)

    def has_children(self):
        """ Renvoyer si l'option a des descendants """
        return self.get_children().exists()

    def get_tree(self):
        """ Renvoyer la hiérarchie de l'option """
        instance, items = self, []
        while instance is not None:
            items.append(instance)
            instance = instance.parent
        items.append(self.group)
        return items.reverse()

    def html(self, **kwargs):
        """ Renvoyer une représentation HTML de l'option """
        mode = kwargs.get('mode', r"default")
        kwargs.update({'item': self})
        return render_to_string("core/display/option-{mode}.html".format(mode=mode), kwargs)

    # Propriétés
    name = property(get_name)
    description = property(get_description)

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return self.get_name()

    def __repr__(self):
        """ Renvoyer une représentation ASCII de l'objet """
        return unidecode(self.get_name())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Option, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("option")
        verbose_name_plural = _("options")
        unique_together = (('group', 'code'),)
        ordering = ['code']
        app_label = 'core'


class OptionTranslation(get_translation_model(Option, "option"), TranslationModel):
    """ Traduction des options """
    name = models.CharField(max_length=120, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Métadonnées
    class Meta:
        app_label = 'core'
