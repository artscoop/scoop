# coding: utf-8
from django.conf import settings


# Contexte supplémentaire
CONTEXT = {
    "DEBUG": settings.DEBUG,
    "DOMAIN_NAME": settings.DOMAIN_NAME,
    "PROJECT_ROOT": settings.PROJECT_ROOT,
    "SITE": settings.SITE_NAME,
    "THEME": settings.THEME,
    "THEME_URL": "{0}theme/{1}/".format(settings.STATIC_URL, settings.THEME)
}


def core(request):
    """ Mettre à jour le contexte des templates """
    return CONTEXT
