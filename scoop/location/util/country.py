# coding: utf-8
from scoop.core.util.django.templateutil import do_render
from scoop.core.util.stream.request import default_request


def get_country_icon_html(code2, title, directory="png24"):
    """ Renvoyer le HTML de l'icône de pays selon un code ISO 2 lettres """
    return do_render(default_request(), "location/display/icon.html", {'type': directory.lower(), 'code': code2.lower(), 'title': title}, string=True)
