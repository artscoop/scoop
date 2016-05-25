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
from scoop.core.util.data.textutil import disemvowel, truncate_ellipsis, truncate_longwords, truncate_repeats
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


@register.simple_tag
def humanize_join(values, enum_count, singular_plural=None, as_links=False):
    """
    Renvoyer une représentation lisible d'une liste d'éléments

    Ex.:
        - a, b et 5 autres personnes
        - a, b, c et 1 autre carte
        - a, b et c
    :param enum_count: nombre d'éléments à lister
    :param singular_plural: nom du type d'objet affiché, au singulier et au pluriel, séparés par un point-virgule.
    :param as_links: afficher les éléments listés comme des liens HTML
    """
    values = list(values)
    total = len(values)
    rest = total - enum_count
    if singular_plural is not None:
        singular, plural = [word.strip() for word in singular_plural.split(";", 1)]
    elif total > 0 and isinstance(values[0], Model):
        singular, plural = values[0]._meta.verbose_name, values[0]._meta.verbose_name_plural
    else:
        raise TypeError("Values must be a list of Model instances or singular_plural must be passed as an argument.")
    values = [linkify(value) for value in values] if as_links else [str(value) for value in values]
    if rest > 0:
        output = _("{join} and {rest} {unit}").format(join=", ".join(values[:enum_count]), rest=rest, unit=singular if rest == 1 else plural)
    else:
        if total == 0:
            output = ""
        elif total == 1:
            output = "{item}".format(item=values[0])
        else:
            output = _("{join} and {last}").format(join=", ".join(values[:-1]), last=values[-1])
    return mark_safe(output)


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
