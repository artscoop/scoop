# coding: utf-8
from __future__ import absolute_import

import calendar
import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pretty_times import pretty

from scoop.core.util.data.dateutil import date_age
from scoop.core.util.shortcuts import addattr


class BirthManager(object):
    """ Mixin manager pour les naissances, âges et dates d'anniversaire """

    # Getter
    def get_birthdays(self, days=0):
        """ Renvoyer les entités dont c'est aujourd'hui et pendant n jours l'anniversaire """
        today = timezone.now().date()
        end = today + datetime.timedelta(days=days)
        dayid = today.day + today.month * 100
        endid = end.day + end.month * 100
        birthdays = self.filter(birthday__range=(dayid, endid))
        if endid >= 1300:
            birthdays &= self.filter(birthday__range=(101, endid - 1200))
        return birthdays


class BirthModel(models.Model):
    """ Mixin de modèle avec date de naissance, d'anniversaire et âge """
    # Constantes
    SIGNS = {120: _("Capricorn"), 218: _("Aquarius"), 320: _("Pisces"), 420: _("Aries"), 521: _("Taurus"), 621: _("Gemini"), 722: _("Cancer"), 823: _("Leo"), 923: _("Virgo"),
             1023: _("Libra"), 1122: _("Scorpion"), 1222: _("Sagittarius"), 1232: _("Capricorn")}
    # Champs
    birth = models.DateField(null=False, default=datetime.date(1990, 1, 1), blank=False, verbose_name=_("Birth date"))
    birthday = models.IntegerField(null=True, editable=False, blank=True, verbose_name=_("Birth day"))
    age = models.SmallIntegerField(editable=False, db_index=True, verbose_name=_("Age"))

    # Getter
    def get_birthday_dict(self):
        """ Renvoyer un dictionnaire de la date d'anniversaire """
        return {'month': int(self.birthday / 100), 'month_name': calendar.month_name[int(self.birthday / 100)], 'day': self.birthday % 100}

    @addattr(short_description=_("Birthday"))
    def get_next_birthday(self):
        """ Renvoyer la date du prochain anniversaire """
        today = timezone.now().date()
        birth_day = self.get_birthday_dict()
        dayid = today.day + today.month * 100
        year_shift = 0 if dayid < self.birthday else 1
        next_birthday = datetime.date(today.year + year_shift, birth_day['month'], birth_day['day'])
        return next_birthday

    @addattr(short_description=_("Birthday"))
    def get_next_birthday_relative(self):
        """ Renvoyer une version texte relative de la date du prochain anniversaire """
        return pretty.date(self.get_next_birthday())

    @addattr(boolean=True)
    def is_birthday(self):
        """ Renvoie si aujourd'hui c'est l'anniversaire de l'objet """
        today = timezone.now().date()
        dayid = today.day + today.month * 100
        return self.birthday == dayid

    @addattr(admin_order_field='-birth', short_description=_("Age"))
    def get_age(self):
        """ Renvoie l'âge de l'objet """
        return date_age(self.birth)

    @addattr(short_description=_("Sign"))
    def get_zodiac_sign(self):
        """ Renvoyer le signe zodiacal de l'objet """
        for sign in self.SIGNS.items():
            if self.birthday < sign[0]:
                return sign[1]

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet en base de données """
        if self.birth:
            self.birthday = self.birth.day + self.birth.month * 100
            self.age = self.get_age()
        return super(BirthModel, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        abstract = True
