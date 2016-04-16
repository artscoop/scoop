# coding: utf-8
from django.template.loader import render_to_string

from scoop.core.util.stream.request import default_context


def get_country_icon_html(code2, title, directory="png24"):
    """ Renvoyer le HTML de l'icône de pays selon un code ISO 2 lettres """
    return render_to_string("location/display/icon.html", {'type': directory.lower(), 'code': code2.lower(), 'title': title}, default_context())
