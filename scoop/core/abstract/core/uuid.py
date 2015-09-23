# coding: utf-8
from __future__ import absolute_import

from math import ceil

from django.db import models
from django.utils.baseconv import base64
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.data.uuid import uuid_bits
from scoop.core.util.shortcuts import addattr


class UUIDField(models.CharField):
    """ Champ de modèle UUID/Base64 """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """ Initialiser le champ """
        kwargs['unique'] = kwargs.get('unique', True)
        kwargs['editable'] = False
        self.bits = int(kwargs.get('bits', 64))
        if self.bits < 16:
            self.bits = 16
        if self.bits > 128:
            self.bits = 128
        kwargs['max_length'] = int(ceil(self.bits / 6.0))
        kwargs['default'] = kwargs.get('default', self._generate)
        if 'bits' in kwargs:
            del kwargs['bits']
        kwargs.pop('verbose_name', None)
        models.CharField.__init__(self, *args, **kwargs)

    def deconstruct(self):
        """ Déconstruire le champ """
        name, path, args, kwargs = super(UUIDField, self).deconstruct()
        kwargs['bits'] = self.bits
        kwargs['default'] = ''
        return name, path, args, kwargs

    # Getter
    def _generate(self):
        """ Renvoyer une valeur pour le champ """
        value = uuid_bits(self.bits)
        return value

    # Overrides
    def pre_save(self, model_instance, add):
        """ Pré-enregistrer le champ """
        value = getattr(model_instance, self.attname)
        if not value:
            value = self._generate()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)


class FreeUUIDModel(models.Model):
    """ Mixin de modèle avec UUID, sans champ UUID """

    # Getter
    def get_real_uuid(self):
        """ Renvoyer l'UUID au format UUID """
        s = "%x" % base64.decode(self.uuid)
        uuid = "-".join([s[0:4], s[4:8], s[8:12], s[12:16]])
        return uuid

    @addattr(allow_tags=True, short_description="Code")
    def get_uuid_html(self):
        """ Renvoyer un snippet HTML contenant l'UUID """
        return "<div class='copy-container' style='position:relative;display:inline-block;'><span class='copy-code'>%(uuid)s</span></div>" % {'uuid': self.uuid}

    # Métadonnées
    class Meta:
        abstract = True


class UUID64Model(FreeUUIDModel):
    """ Mixin de modèle avec un UUID 64 bits """
    uuid = UUIDField(verbose_name=_("Code"), bits=64)

    # Métadonnées
    class Meta:
        abstract = True


class UUID128Model(FreeUUIDModel):
    """ Mixin de modèle avec un UUID 128 bits """
    uuid = UUIDField(verbose_name=_("Code"), bits=128, max_length=22)

    # Métadonnées
    class Meta:
        abstract = True


class UUID32Model(FreeUUIDModel):
    """ Mixin de modèle avec un UUID 32 bits """
    uuid = UUIDField(verbose_name=_("Code"), bits=32, max_length=6)

    # Métadonnées
    class Meta:
        abstract = True
