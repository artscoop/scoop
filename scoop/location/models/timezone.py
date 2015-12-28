# coding: utf-8
import datetime
import zlib

import pytz
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr


class Timezone(models.Model):
    """ Fuseau horaire """

    # Champs
    name = models.CharField(max_length=80, blank=False, unique=True, verbose_name=_("Name"))
    code = models.BigIntegerField(primary_key=True, editable=True, help_text=_("Adler32 hash of timezone standard name"), verbose_name=_("Name hash"))

    # Getter
    @staticmethod
    def _hash_name(name):
        """
        Renvoyer le hash d'un nom de timezone
        :type name: str
        """
        return zlib.adler32(bytes(name, 'UTF-8'))

    @staticmethod
    def by_name(name):
        """ Renvoyer un fuseau horaire par son nom """
        timezone = Timezone.objects.filter(code=Timezone._hash_name(name))
        if timezone.exists():
            return timezone.first()
        else:
            try:
                pytz.timezone(name)  # vérifier que le nom est valide
                timezone = Timezone(name=name, code=Timezone._hash_name(name))
                timezone.save()
                return timezone
            except:
                raise

    @staticmethod
    def get_dict():
        """ Renvoyer un dictionnaire de nom:timezone """
        for name in pytz.common_timezones:
            Timezone.by_name(name)
        timezones = Timezone.objects.all()
        return {timezone.name: timezone for timezone in timezones}

    def get_info(self):
        """ Renvoyer les informations de fuseau horaire """
        return pytz.timezone(self.name)

    @addattr(short_description=_("UTC Offset"))
    def get_utc_offset(self, as_str=True):
        """ Renvoyer le décalage UTC du fuseau horaire """
        offset = self.get_info().utcoffset(datetime.datetime.now())
        return Timezone._get_offset_str(offset) if as_str else offset

    @addattr(short_description=_("DST Offset"))
    def get_dst_offset(self, as_str=True):
        """ Renvoyer le décalage de l'heure d'été """
        offset = self.get_info().dst(datetime.datetime.now())
        return Timezone._get_offset_str(offset) if as_str else offset

    @addattr(short_description=_("Base Offset"))
    def get_base_offset(self, as_str=True):
        """ Renvoyer le décalage UTC sans le décalage d'été """
        offset = self.get_utc_offset() - self.get_dst_offset()
        return Timezone._get_offset_str(offset) if as_str else offset

    @staticmethod
    def _get_offset_str(offset):
        """ Renvoyer une représentation texte d'un décalage """
        offset, extra = (datetime.timedelta() - offset, '-') if offset.days < 0 else (offset, '+')
        return "{ex}{delta}".format(**{'ex': extra, 'delta': offset})

    # Overrides
    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return self.name

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if not self.code:
            self.code = Timezone._hash_name(self.name)
        super(Timezone, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("timezone")
        verbose_name_plural = _("timezones")
        app_label = 'location'
