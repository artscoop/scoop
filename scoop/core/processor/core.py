# coding: utf-8
from __future__ import absolute_import

from django.conf import settings

CONTEXT = {
    "THEME": settings.THEME,
    "DEBUG": settings.DEBUG,
    "DOMAIN_NAME": settings.DOMAIN_NAME,
    "THEME_URL": "{0}theme/{1}/".format(settings.STATIC_URL, settings.THEME),
    "PROJECT_ROOT": settings.PROJECT_ROOT,
    "SITE": settings.SITE_NAME
}


def core(request):
    """ Mettre à jour le contexte des templates """
    return CONTEXT
