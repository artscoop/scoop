# coding: utf-8
import datetime
import time

from django.db import models
from django.template.defaultfilters import date as datefilter
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from pretty_times import pretty
from pytz import timezone as _tz
from scoop.core.util.data.dateutil import now as now_
from scoop.core.util.data.dateutil import datetime_round_day, from_now, to_timestamp
from scoop.core.util.shortcuts import addattr

# Constantes
DELTA = {'minute': 60, 'hour': 3600, 'day': 86400, 'week': 604800, 'year': 31536000}


class DatetimeModel(models.Model):
    """ Mixin de modèle avec un timestamp de création """
    time = models.PositiveIntegerField(default=now_, editable=False, db_index=True, verbose_name=_("Timestamp"))

    # Getter
    def now(self=None):
        """ Renvoyer le timestamp actuel """
        return now_()  # calendar.timegm(datetime.datetime.utcnow().utctimetuple())

    @staticmethod
    def get_timestamp(value):
        """ Renvoyer un timestamp à partir d'un objet datetime """
        return to_timestamp(value)

    @staticmethod
    def get_relative_format(value):
        """ Renvoyer un texte lisible indiquant la proximité d'un datetime """
        if isinstance(value, datetime.datetime):
            return pretty.date(value)
        elif isinstance(value, DatetimeModel):
            return pretty.date(value.datetime)

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Time"))
    def get_datetime(self):
        """ Renvoyer le timestamp de l'objet converti en datetime """
        return datetime.datetime.fromtimestamp(self.time, _tz('UTC'))

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Time"))
    def get_datetime_format(self, format_string="j F Y H:i"):
        """ Renvoyer une représentation texte du timestamp """
        return datefilter(self.get_datetime(), format_string)

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Time"))
    def get_datetime_ago(self):
        """ Renvoyer une représentation relative du timestamp """
        return pretty.date(self.datetime)

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Time"))
    def get_short_datetime_format(self, format_string="j M y G:i"):
        """ Renvoyer une représentation texte courte du timestamp """
        return self.get_datetime_format(format_string)

    @addattr(admin_order_field='time', short_description=pgettext_lazy("datetime", "Date"))
    def get_date_format(self, format_string="j F Y"):
        """ Renvoyer une représentation texte du jour du timestamp """
        return self.get_datetime_format(format_string)

    @staticmethod
    def since(delta=None):
        """
        Renvoyer une date ancienne d'un certain offset en secondes ou en timedelta

        :param delta: différence en timedelta, en secondes, ou date
        """
        if delta is not None:
            td = type(delta)
            if td == datetime.timedelta:
                timestamp = now_() - int(delta.total_seconds())
            elif td in {int, float}:
                timestamp = now_() - delta
            elif td == datetime.datetime:
                timestamp = DatetimeModel.get_timestamp(delta)
                timestamp = min(now_(), timestamp)
            return timestamp
        return now_()

    @staticmethod
    def get_last_days(days=3, timestamp=True):
        """ Renvoyer une datetime correspondant à il y a n jours à minuit """
        value = datetime_round_day(from_now(days=-days))
        value = DatetimeModel.get_timestamp(value) if timestamp else value
        return value

    @staticmethod
    def make_expiry(days, timestamp=True):
        """
        Renvoyer une date d'expiration dans le futur, en timestamp

        :param days: nombre de jours à partir de maintenant
        :param timestamp: renvoyer la date future en timestamp plutôt qu'en datetime
        :type days: int
        :type timestamp: bool
        """
        value = from_now(days=days)
        value = DatetimeModel.get_timestamp(value) if timestamp else value
        return value

    @addattr(boolean=True, admin_order_field='time', short_description=_("New"))
    def is_new(self, days=7, hours=0, minutes=0):
        """
        Renvoyer si le timestamp de l'objet est récent

        :param days: nombre de jours
        :param hours: nombre d'heures
        :param minutes: nombre de minutes
        :type days: int
        :type hours: int
        :type minutes: int
        """
        return self.time >= now_() - days * DELTA['day'] - hours * DELTA['hour'] - minutes * DELTA['minute']

    # Setter
    def set_datetime(self, value):
        """
        Définir le timestamp

        :param value: date/heure
        :type value: datetime.datetime
        """
        self.time = time.mktime(value.timetuple())

    def add_time(self, seconds=0, minutes=0, hours=0, days=0):
        """
        Avancer le timestamp d'un offset

        :param days: nombre de jours
        :param hours: nombre d'heures
        :param minutes: nombre de minutes
        :param seconds: nombre de secondes
        """
        self.time += (seconds + days * DELTA['day'] + hours * DELTA['hour'] + minutes * DELTA['minute'])

    # Propriétés
    datetime = property(get_datetime, set_datetime)  # Renvoie un datetime depuis le timestamp

    # Métadonnées
    class Meta:
        abstract = True
