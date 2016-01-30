# coding: utf-8
import datetime
import re

from django import template
from django.utils import timezone
from django.utils.timezone import timedelta
from pytz import timezone as _tz
from scoop.core.util.data.dateutil import is_new as dt_is_new

register = template.Library()


@register.filter(name='is_new')
def is_date_new(value, by):
    """
    Renvoyer si un objet datetime ou DatetimeModel est plus récent que

    :param by: chaîne au format "#d #h #m" ou un nombre en jours
    """
    from scoop.core.abstract.core.datetime import DatetimeModel
    # Traiter le cas possibles, ou False si non supporté
    if isinstance(by, str):
        days = int(getattr(re.search(r"(\d+)d", by, re.IGNORECASE), 'groups', lambda: [0])()[0])
        hours = int(getattr(re.search(r"(\d+)h", by, re.IGNORECASE), 'groups', lambda: [0])()[0])
        minutes = int(getattr(re.search(r"(\d+)m", by, re.IGNORECASE), 'groups', lambda: [0])()[0])
        if isinstance(value, DatetimeModel):
            return value.is_new(days=days, hours=hours, minutes=minutes)
        elif isinstance(value, datetime.datetime):
            return dt_is_new(value, days=days, hours=hours, minutes=minutes)
    elif isinstance(by, (int, float)):
        if isinstance(value, DatetimeModel):
            return value.is_new(days=by)
        elif isinstance(value, datetime.datetime):
            return dt_is_new(value, days=by)
    return False


@register.simple_tag(name='from_now')
def days_from_now(days=-1):
    """ Renvoyer une date exactement à n jours de maintenant """
    return timezone.now() + timedelta(days=days)


@register.filter
def to_datetime(value):
    """ Convertir un timestamp en date """
    return datetime.datetime.fromtimestamp(value, _tz('UTC'))
