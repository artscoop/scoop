# coding: utf-8
from __future__ import absolute_import

import calendar
import datetime
from random import randrange

from django.utils import timezone


def now():
    """ Renvoie la date/heure actuelle en int(timestamp) """
    return calendar.timegm(datetime.datetime.utcnow().utctimetuple())


def to_timestamp(dt):
    """
    Convertit un objet date ou datetime en int(timestamp)
    :type dt: datetime.datetime | datetime.date
    """
    if isinstance(dt, datetime.date):
        dt = datetime.datetime(dt.year, dt.month, dt.day)
    return calendar.timegm(dt.utctimetuple())


def date_age(date, today=None):
    """ Calcule l'âge d'une date en années. Today peut être modifié """
    # Date du jour
    today = today or timezone.now().date()
    # Différence d'années
    age = today.year - date.year
    delta = (today.month - date.month) * 32 + (today.day - date.day)
    return age - 1 if delta < 0 else age


def date_age_days(date, today=None):
    """ Calcule l'âge d'une date en jours. Today peut être modifié """
    diff = (today or datetime.date.today()) - date
    return diff.days


def ages_dates(young, old=None, today=None):
    """
    Renvoie un tuple contenant les dates limites pour une plage d'âges.
    :param young: âge minimum
    :param old: âge maximum. ``None`` si identique à ``young``
    :param today: date à laquelle calculer les âges. ``None`` pour aujourd'hui
    """
    today = today or timezone.now().date()
    # Si young est négatif, remettre à 0
    young = 0 if young < 0 else young
    # Si old est None, alors considérer que old est le même âge que young
    old = young if (old is None or old < young) else old
    max_date = datetime.date(today.year - young, today.month, today.day)
    min_date = datetime.date(today.year - old - 1, today.month, today.day) + datetime.timedelta(days=1)
    return (min_date, max_date)


def from_now(days=0, hours=0, minutes=0, seconds=0, timestamp=False):
    """ Renvoyer une date correspondant à un offset à partir de maintenant """
    when = timezone.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return to_timestamp(when) if timestamp else when


def is_new(date, days=7, hours=0, minutes=0, seconds=0, now=None):
    """ Renvoyer si une date est plus récente que n jours """
    return date > ((now or timezone.now()) - datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds))


# Arrondir un objet Datetime
def datetime_round_hour(value=None):
    """ Arrondir un objet datetime à l'heure pile """
    value = value or timezone.now()
    result = datetime.datetime(value.year, value.month, value.day, value.hour, 0, 0, 0)
    return result


def datetime_round_day(value=None):
    """ Arrondir un objet datetime au jour à minuit """
    value = value or timezone.now()
    result = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
    return result


def datetime_round_month(value=None):
    """ Arrondir un objet datetime au premier du mois, à minuit """
    value = value or timezone.now()
    result = datetime.datetime(value.year, value.month, 1, 0, 0, 0, 0)
    return result


def datetime_round_year(value=None):
    """ Arrondir un objet datetime au premier de l'an, à minuit """
    value = value or timezone.now()
    result = datetime.datetime(value.year, 1, 1, 0, 0, 0, 0)
    return result


def random_date(*date_range):
    """ Renvoyer une date au hasard entre deux dates """
    if type(date_range) in [list, tuple]:
        start = date_range[0]
        end = date_range[1]
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return (start + datetime.timedelta(seconds=random_second))
    return None
