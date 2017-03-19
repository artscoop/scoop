# coding: utf-8
from django.conf import settings
from django.contrib.contenttypes import fields
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.django.templates import render_to
from scoop.core.util.model.model import limit_to_model_names
from scoop.core.util.shortcuts import import_qualified_name


class Configuration(DatetimeModel, WeightedModel):
    """
    Configuration d'un bloc de page

    Page → Position → Template → Target
    Objet à afficher avec un template à telle position dans une page.
    """

    # Champs
    page = models.ForeignKey('editorial.Page', null=False, related_name='configurations', verbose_name=_("Page"))
    position = models.ForeignKey('editorial.Position', null=False, related_name='configurations', verbose_name=_("Position"))
    template = models.ForeignKey('editorial.Template', null=False, related_name='configurations', limit_choices_to={'full': False},
                                 help_text=_("Select template to use to display the target"), verbose_name=_("Template"))
    notes = models.CharField(max_length=64, blank=True, verbose_name=_("Notes"))
    # Cible
    view_path = models.CharField(max_length=96, blank=True, help_text=_("Fully qualified view to display"), verbose_name=_("View path"))
    limit = limit_to_model_names('editorial.excerpt', 'content.picture', 'content.content', 'content.link')  # limiter les modèles liés
    content_type = models.ForeignKey('contenttypes.ContentType', null=False, blank=False, verbose_name=_("Content type"), limit_choices_to=limit)
    object_id = models.PositiveIntegerField(null=False, blank=True, db_index=False, verbose_name=_("Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # Getter
    def is_valid(self):
        """ Renvoyer si la configuration est valide """
        if self.page.template.positions.filter(pk=self.position.pk).exists():
            return True
        return False

    def render(self, request=None, force=False):
        """ Rendre la configuration """
        if force or self.is_valid():
            if self.view_path:
                try:
                    view = import_qualified_name(self.view_path)
                    return render_to(string=True)(view(request))  # la vue peut renvoyer dict, str ou response
                except ImportError:
                    return _("The view at path could not be imported.")
            else:
                result = render_to_string(self.template.path, {'item': self.content_object, 'page': self.page})
                return result
        if settings.DEBUG:
            return _("The block could not be rendered.")
        return ""

    # Setter
    def move_to(self, position):
        """
        Déplacer dans une autre position

        :type position: scoop.editorial.models.Position | str
        :returns: True if the operation was successful
        """
        page_position = self.page.get_position(position if isinstance(position, str) else position.name)
        if page_position is not None:
            self.position = page_position
            self.save()
            return True
        return False

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("{page}/{item} at {position}").format(page=self.page, item=self.content_object, position=self.position)

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Configuration, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("block configuration")
        verbose_name_plural = _("block configurations")
        unique_together = (('page', 'position', 'template', 'content_type', 'object_id'),)
        app_label = 'editorial'
