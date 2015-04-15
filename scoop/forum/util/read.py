# coding: utf-8
from __future__ import absolute_import

from django.utils import timezone


def default_expiry(self=None):
    """ Renvoyer la date d'expiration par défaut d'un objet Read """
    return timezone.now() + timezone.timedelta(days=30)
