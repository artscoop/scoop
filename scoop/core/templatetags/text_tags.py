# coding: utf-8
import re

from django import template
from django.conf import settings
from django.db.models.base import Model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from ngram import NGram
from scoop.core.templatetags.html_tags import linkify
from unidecode import unidecode

register = template.Library()


@register.filter
def truncate_ellipsis(value, arg):
    """ Renvoyer une chaîne tronquée et y ajouter une ellipse """
    try:
        length = int(arg)
    except ValueError:
        return value
    if not isinstance(value, str):
        value = str(value)
    if len(value) > length:
        return value[:length].strip() + "…"
    else:
        return value


@register.filter
def truncate_stuckkey(value, length=5):
    """
    Renvoyer une chaîne débarrassée de longues suites de la même lettre
    ex. « Saluuuuuuuut » devient « Salut »
    """
    re.DEBUG = settings.DEBUG

    # Sous fonction : récupère un match et le coupe
    def cut_match(match):
        return match.group()[0:1]

    # Supprimer toutes les séquences de la même lettre par cut_match
    pattern = r"(?i)(\w)\1{%d,100}" % (int(length))
    result = re.sub(pattern, cut_match, str(value))
    return result


@register.filter
def truncate_longwords(value, length=27):
    """ Découper les mots plus long que le mot français le plus long """
    re.DEBUG = settings.DEBUG

    def cut_match(match):
        """ Couper une correspondance du reste du texte """
        portion = list(match.group())
        portion.insert(length - 1, " ")
        return "".join(portion)

    # Supprimer toutes les séquences de la même lettre par cut_match
    pattern = r"\S{%(length)d}" % {'length': int(length)}
    result = re.sub(pattern, cut_match, value)
    return result


@register.filter(name="disemvowel")
def disemvowel(value):
    """ Renvoyer le texte sans voyelles (+accents) """
    value = unidecode(value)
    value = value.replace(value, re.sub(r'[AEIOUYaeiouy]', '', value))
    return value


@register.simple_tag
def humanize_join(values, enum_count, singular_plural=None, as_links=False):
    """
    Renvoyer une représentation lisible d'une liste d'éléments
    Ex.:
        - a, b et 5 autres personnes
        - a, b, c et 1 autre carte
        - a, b et c
    """
    values = list(values)
    total = len(values)
    rest = total - enum_count
    if singular_plural is not None:
        singular, plural = [word.strip() for word in singular_plural.split(";")]
    elif total > 0 and isinstance(values[0], Model):
        singular, plural = values[0]._meta.verbose_name, values[0]._meta.verbose_name_plural
    else:
        raise TypeError("Values must be a list of Model instances or singular_plural must be passed as an argument.")
    values = [linkify(value) for value in values] if as_links else [str(value) for value in values]
    if rest > 0:
        output = _("%(join)s and %(rest)d %(unit)s") % {'join': ", ".join(values[:enum_count]), 'rest': rest, 'unit': singular if rest == 1 else plural}
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
    """ Renvoyer l'indice de similarité entre deux chaînes """
    return NGram.compare(initial, other)
