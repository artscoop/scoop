# coding: utf-8
from __future__ import absolute_import

from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = ['GenericModel', 'NullableGenericModel']


class GenericModelMixin(object):
    """ Mixin de modèle avec un lien générique """

    # Actions
    def attach_to(self, instance):
        """ Attacher l'objet à une cible """
        if isinstance(instance, models.Model) or instance is None:
            self.content_object = instance
            self.save()

    def detach(self):
        """ Détacher l'objet d'une cible """
        self.attach_to(None)

    # Getter
    @staticmethod
    def get_object_dict(item):
        """ Renvoyer un dictionnaire avec le content type et l'id """
        content_type = ContentType.objects.get_for_model(item)
        return {'content_type': content_type, 'object_id': item.pk}

    # Overrides
    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        self.content_object = None
        super(GenericModel, self).delete(*args, **kwargs)  # Call the "real" save() method.


class GenericModel(models.Model, GenericModelMixin):
    """ Mixin de modèle avec lien générique """
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, db_index=True, verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(null=True, db_index=True, verbose_name=_(u"Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    content_object.short_description = _(u"Content object")

    # Métadonnées
    class Meta:
        abstract = True


class NullableGenericModel(models.Model, GenericModelMixin):
    """ Mixin de modèle avec lien générique nullable """
    content_type = models.ForeignKey('contenttypes.ContentType', null=True, blank=True, db_index=True, verbose_name=_(u"Content type"))
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True, verbose_name=_(u"Object Id"))
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    # Métadonnées
    class Meta:
        abstract = True
