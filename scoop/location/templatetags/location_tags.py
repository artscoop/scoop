# coding: utf-8
from __future__ import absolute_import

from django import template
from django.template.loader import render_to_string

from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.location.models.city import City
from scoop.location.models.country import Country

register = template.Library()


@register.filter(name='distance_html')
def distance(value, endpoint):
    """ Renvoyer la distance en km entre deux points """
    result = value.get_distance(point=endpoint) if isinstance(value, CoordinatesModel) and isinstance(endpoint, CoordinatesModel) else None
    return render_to_string('location/display/distance.html', {'distance': result})


@register.filter(name='distance_unit')
def distance_unit(value, unit):
    """ Renvoyer une distance convertie dans une autre unité """
    return CoordinatesModel.convert_km_to(value, unit)


@register.filter(name='area')
def city_parent(city, level=None):
    """ Renvoyer le parent par défaut d'une ville """
    return city.get_auto_parent(level) if isinstance(city, CoordinatesModel) else None


@register.filter(name='flag')
def flag_icon(value, folder="png"):
    """ Renvoyer l'icône du pays """
    if isinstance(value, City):
        return value.country.get_icon(folder)
    if isinstance(value, Country):
        return value.get_icon(folder)
    return None


@register.filter(name='cardinal')
def cardinal_position(location, target):
    """ Renvoyer la position relative d'une cible par rapport à un lieu """
    if isinstance(location, CoordinatesModel) and isinstance(target, CoordinatesModel):
        return location.get_cardinal_position(target)
    return None


@register.simple_tag(name='cardinal')
def cardinal_position_tag(center, target, mode=None):
    """
    Renvoyer la position relative d'une cible par rapport à un lieu
    :type mode: "short|relative|name"
    """
    if isinstance(center, CoordinatesModel) and isinstance(target, CoordinatesModel):
        return center.get_cardinal_position(target, mode=mode)
    return None
