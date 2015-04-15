# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.db.models import permalink


class FlaggableModelUtil:
    """ Mixin d'objet pouvant être signalé"""

    @permalink
    def get_flag_url(self):
        """ Renvoyer l'URL pour signaler l'objet """
        from django.contrib.contenttypes.models import ContentType
        content_type_id = ContentType.objects.get_for_model(self).id
        identifier = self.id
        return ('rogue:flag-new', [content_type_id, identifier])

# Patcher la classe Model
models.Model.__bases__ += (FlaggableModelUtil,)
