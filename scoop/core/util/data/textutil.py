# coding: utf-8
import re
from io import StringIO

import bleach
from django.conf import settings
from django.db.models.base import Model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from ngram import NGram
from unidecode import unidecode

from scoop.core.util.data.htmlutil import linkify


def text_to_list(value):
    """ Renvoyer une liste de chaînes depuis un texte. """
    with StringIO(value) as reader:
        lines = reader.readlines()
        result = [item.strip() for item in lines]
        return result


def text_to_list_of_lists(value, evaluate=False):
    """
    Renvoyer une liste de listes depuis un texte.

    Chaque élément de la liste de rang 1 est séparé par un retour chariot
    Les éléments des listes de rang 2 sont séparées par deux points (:)
    Attention, evaluate peut représenter une faille de sécurité, n'utiliser
    qu'avec du contenu de confiance.
    :param evaluate: évaluer les valeurs, notamment les nombres
    """
    with StringIO(value) as reader:
        lines = reader.readlines()
        result = [[one_line(part) for part in line.split(":")] for line in lines if not line.startswith('#')]
        if evaluate is True:
            for outer, _a in enumerate(result):
                for inner, _b in enumerate(result[outer]):
                    result[outer][inner] = eval(result[outer][inner], {'__builtin__': {}})
    return result


def text_to_dict(value, evaluate=False):
    """
    Renvoyer un dictionnaire depuis un texte

    Chaque couple clé/valeur est sur sa propre ligne, et séparé par deux points (:)
    Attention, evaluate peut représenter une faille de sécurité, n'utiliser
    qu'avec du contenu de confiance.
    :param evaluate: évaluer les valeurs, notamment les nombres
    """
    with StringIO(value) as reader:
        lines = reader.readlines()
        result = dict([[one_line(part) for part in line.split(":", 1)] for line in lines if (':' in line and not line.startswith('#'))])
        if evaluate is True:
            for key in result.keys():
                result[key] = eval(result[key], {'__builtin__': {}})
    return result


def one_line(value):
    """ Renvoyer le texte, mais sur une seule ligne """
    output = re.sub(r"\r?\n", " ", value).strip()
    return output


def replace_dict(instance, dictionary):
    """
    Renvoyer un texte dont les clés du dictionnaire sont remplacées par les valeurs

    ex. "Les chaussettes de la reine", {'Les': 'Le', 'chaussettes': 'saucisson'}
    renvoie "Le saucisson de la reine"

    :param instance: objet de type chaîne possédant la méthode replace
    :param dictionary: dictionnaire, dont les clés sont remplacées par les valeurs correspondantes
    """
    result = instance
    for base in dictionary:
        result = result.replace(base, dictionary[base])
    return result


def count_words(text, html=False):
    """
    Renvoyer le nombre de mots dans un texte

    :param text: texte à analyser
    :param html: indique si le texte est en HTML. Exclut le markup HTML du compte si True
    :type html: bool
    """
    text = strip_tags(text) if html else text
    count = len(re.findall(r'\w+', text))
    return count


def clean_html(text, mode=None):
    """
    Renvoyer un texte HTML avec uniquement des attributs safe

    :param text: texte HTML à filtrer
    :param mode: niveau/mode de filtrage
    """
    mode = mode or 'default'
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'p', 'br', 'strong', 'em', 'strike', 'b', 'small', 'code', 'pre', 'blockquote', 'hr', 'dt', 'dd',
            'ul', 'li', 'ol', 'span', 'center', 'site', 'address', 'caption']
    attrs = {'a': ['href', 'title', 'class', 'id']}
    styles = ['text-align']
    protocols = ['http', 'https']
    return bleach.clean(text, tags=tags, attributes=attrs, styles=styles, protocols=protocols, strip=True)


def truncate_repeats(value, length=5):
    """
    Renvoyer une chaîne débarrassée de longues suites de la même lettre

    ex. « Saluuuuuuuut » devient « Salut »
    :param value: texte en entrée
    :param length: nombre de répétitions minimum d'une lettre à filtrer
    """

    # Sous fonction : récupère un match et le coupe
    def cut_match(match):
        return match.group()[0:1]

    # Supprimer toutes les séquences de la même lettre par cut_match
    pattern = r"(?i)(\w)\1{%d,100}" % (int(length))
    result = re.sub(pattern, cut_match, str(value))
    return result


def truncate_ellipsis(value, length):
    """ Renvoyer une chaîne tronquée et y ajouter une ellipse """
    try:
        length = int(length)
    except ValueError:
        return value
    if not isinstance(value, str):
        value = str(value)
    if len(value) > length:
        return value[:length].strip() + "…"
    else:
        return value


def truncate_longwords(value, length=27):
    """ Découper les mots plus long que le mot français le plus long """

    def cut_match(match):
        """ Couper une correspondance du reste du texte """
        portion = list(match.group())
        portion.insert(length - 1, " ")
        return "".join(portion)

    # Supprimer toutes les séquences de la même lettre par cut_match
    pattern = r"\S{%(length)d}" % {'length': int(length)}
    result = re.sub(pattern, cut_match, value)
    return result


def disemvowel(value):
    """ Renvoyer le texte sans voyelles et sans accents """
    value = unidecode(value)
    value = value.replace(value, re.sub(r'[AEIOUYaeiouy]', '', value))
    return value


def humanize_join(values, enum_count, singular_plural=None, as_links=False):
    """
    Renvoyer une représentation lisible d'une liste d'éléments

    Ex.:
        - a, b et 5 autres personnes
        - a, b, c et 1 autre carte
        - a, b et c
    :param values: iterable d'objets à afficher
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


def gender(value, text):
    """
    Renvoyer une chaîne dépendant du genre de l'objet

    :param value: un genre, 0=H, 1=F ou 2=ND
    :param text: une chaîne de trois textes séparés par des points-virgules
    """
    texts = text.split(';')
    return texts[value]


def compare(initial, other):
    """
    Renvoyer l'indice de similarité entre deux chaînes

    :returns: un nombre entre 0 et 1
    """
    return NGram.compare(initial, other)


def site_brand(value):
    """ Remplace des occurrences de texte par une version améliorée du nom du site """
    replacement = render_to_string("core/display/site-name.txt").strip('\n ')
    return value.replace(settings.CORE_BRAND_NAME_MARKER, replacement)
