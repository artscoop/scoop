# coding: utf-8
import math
import traceback

from django import template
from django.db.models.base import Model
from scoop.core.util.data.numbers import round_left as roundl

register = template.Library()

# Constantes
SI_PREFIXES = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']


# Arithmétique
@register.filter
def subtract(value, amount):
    """ Soustraire """
    return value - amount


@register.filter
def delta(value, amount):
    """ Cardinal de la soustraction """
    return abs(value - amount)


@register.filter
def round_multiple(x, base=1):
    """ Renvoyer le multiple de *base* le plus proche de *x* """
    return (base * math.floor(float(x) / base)) if type(base) in {int, float} and base > 0 else None


@register.filter
def round_left(x, digits=2):
    """
    Arrondir un nombre aux n chiffres les plus significatifs
    :param digits: nombre de chiffres significatifs
    :returns: ex. 2 500 000 pour 2 567 890 123 avec digits=2
    """
    return roundl(x, digits)


@register.filter
def modulo(value, br):
    """
    Renvoyer un modulo ou comparer un modulo
    :param br: int, float ou chaîne de 2 nombres b et r séparés par une virgule
    :returns: value % br si br est un nombre, sinon renvoie si value % b est égal à r
    """
    try:
        if isinstance(br, str) and "," in br:
            b, r = br.split(",")
            return float(r) - 0.000000001 <= value % float(b) <= float(r) + 0.000000001
        else:
            b = float(br)
            if b > 0:
                result = value % b
                return result
    except:
        pass
    return False


@register.filter
def to_percent(value, ratio=None):
    """ Convertir une valeur en pourcentage """
    return (value * 100.0) / (float(ratio or 1))


@register.filter
def si_suffix(value):
    """
    Renvoyer une représentation d'un nombre avec les unités du système international
    Ex. 234 567 renvoie 234k, 123 567 890 renvoie 123M
    """
    level = math.floor(math.log(value, 1000))
    unit_count = int(value / (1000 ** level))
    return "{count:d}{unit}".format(count=unit_count, unit=SI_PREFIXES[int(level)])


@register.filter
def invert(value):
    """ Renvoyer le contraire d'un booléen """
    return not value


@register.filter
def percent_status(value, asc=True):
    """ Renvoyer un statut de santé depuis un flottant entre 0 et 100 """
    if asc is True:
        if value < 33.33:
            return 'success'
        elif value < 66.67:
            return 'warning'
        else:
            return 'danger'
    else:
        if value > 66.67:
            return 'success'
        elif value > 33.33:
            return 'warning'
        else:
            return 'danger'


@register.filter
def nestedsort(value, item_index=0):
    """ Trier un tuple de tuples en utilisant l'élément de tuple d'index *item_index* """
    try:
        item_index = int(item_index)
        value.sort(key=lambda item: item[item_index])
        return value
    except:
        return value


@register.filter
def model_name(value):
    """ Renvoyer le nom du modèle de l'objet """
    if isinstance(value, Model):
        return value._meta.verbose_name
    return None


@register.filter
def field_error(value):
    """ Renvoyer error si un champ possède des erreurs """
    if value.errors:
        return 'error'
    return ''


@register.filter(name='traceback')
def trace(value):
    """
    Renvoyer les données de traceback
    :returns: une liste de tuples de 4 éléments, dans l'ordre
        nom de fichier, numéro de ligne, nom de fonction, texte
    """
    return traceback.extract_tb(value)
