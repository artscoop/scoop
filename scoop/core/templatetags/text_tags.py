# coding: utf-8
import re

from django import template
from django.conf import settings
from django.db.models.base import Model
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from ngram import NGram
from scoop.core.templatetags.html_tags import linkify
from scoop.core.util.data.textutil import disemvowel, truncate_ellipsis, truncate_longwords, truncate_repeats, humanize_join
from unidecode import unidecode

register = template.Library()


@register.filter(name='truncate_ellipsis')
def truncate_with_ellipsis(value, arg):
    """ Renvoyer une chaîne tronquée et y ajouter une ellipse """
    return truncate_ellipsis(value, arg)


@register.filter
def truncate_stuckkey(value, length=5):
    """
    Renvoyer une chaîne débarrassée de longues suites de la même lettre

    ex. « Saluuuuuuuut » devient « Salut »
    :param value: texte en entrée
    :param length: nombre de répétitions minimum d'une lettre à filtrer
    """
    return truncate_repeats(value, length=length)


@register.filter(name='truncate_longwords')
def truncate_for_longwords(value, length=27):
    """ Découper les mots plus long que le mot français le plus long """
    return truncate_longwords(value, length)


@register.filter(name="disemvowel")
def disemvowel_(value):
    """ Renvoyer le texte sans voyelles et sans accents """
    return disemvowel(value)


@register.simple_tag(name='humanize_join')
def humanize_join_tag(values, enum_count, singular_plural=None, as_links=False):
    """
    Renvoyer une représentation lisible d'une liste d'éléments

    Ex.:
        - a, b et 5 autres personnes
        - a, b, c et 1 autre carte
        - a, b et c
    :param values: itérable de valeurs à traiter
    :param enum_count: nombre d'éléments à lister
    :param singular_plural: nom du type d'objet affiché, au singulier et au pluriel, séparés par un point-virgule.
    :param as_links: afficher les éléments listés comme des liens HTML
    """
    return humanize_join(values, enum_count, singular_plural, as_links)


@register.filter
def gender(value, text):
    """
    Renvoyer une chaîne dépendant du genre de l'objet

    :param value: un genre, 0=H, 1=F ou 2=ND
    :param text: une chaîne de trois textes séparés par des points-virgules
    """
    texts = text.split(';')
    return texts[value]


@register.assignment_tag
def compare(initial, other):
    """
    Renvoyer l'indice de similarité entre deux chaînes

    :returns: un nombre entre 0 et 1
    """
    return NGram.compare(initial, other)


@register.filter
def site_brand(value):
    """ Remplace des occurrences de texte par une version améliorée du nom du site """
    replacement = render_to_string("core/display/site-name.txt").strip('\n ')
    output = re.sub(r'(<(?P<tag>input|textarea).*>)(.*)({0})(.*)(</(?P=tag)>)'.format(settings.CORE_BRAND_NAME_MARKER),
                    '\1\2§brand§\4\5', value)
    output = output.replace(settings.CORE_BRAND_NAME_MARKER, replacement).replace('§brand§', settings.CORE_BRAND_NAME_MARKER)
    return output
