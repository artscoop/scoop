# coding: utf-8
from __future__ import absolute_import, division

import math
from math import atan2, pi

import pyproj
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, Polygon
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.templatetags.type_tags import round_multiple
from scoop.core.util.shortcuts import addattr
from scoop.location.util.cardinal import ANGLE_CARDINAL, ANGLE_TICKS, RELATIVE_CARDINAL, SHORT_CARDINAL


class CoordinatesModel(models.Model):
    """ Mixin d'objet localisé par GPS """

    # Constantes
    KM_LON, KM_LAT = 0.008998308318036208, 0.008983111749910169
    UNIT_RATIO = {'km': 1.0, 'm': 1000, 'mi': 0.621371192237334, 'yd': 1093.6132983377076, 'ft': 3280.839895013123, 'nmi': 0.5399568034557235}
    GEODETIC_MODEL = pyproj.Geod(ellps="WGS84")
    SRID = 4326

    # Position géographique du centre de l'objet
    position = models.PointField(default=Point(0.0, 0.0), srid=SRID, spatial_index=True)

    # Setter
    def set_coordinates(self, lat, lon):
        """ Définir les coordonnées de l'objet """
        self.position.set_coords((sorted((-180.0, lon, 180.0))[1], sorted((-90.0, lat, 90.0))[1]))

    def set_point(self, point):
        """
        Définir les coordonnées de l'objet

        :param point: liste ou tuple de deux éléments lat, lon
        """
        self.set_coordinates(point[0], point[1])

    def set_longitude(self, lon):
        self.position.set_x(sorted((-180.0, lon, 180.0))[1])

    def set_latitude(self, lat):
        self.position.set_y(sorted((-90.0, lat, 90.0))[1])

    # Getter
    def get_point(self):
        """
        Renvoyer les coordonnées lat,lon de l'objet

        :rtype: tuple
        """
        return self.position.get_y(), self.position.get_x()

    def get_latitude(self):
        """ Renvoyer la latitude du point """
        return self.position.get_y()

    def get_longitude(self):
        """ Renvoyer la longitude du point """
        return self.position.get_x()

    def get_point_dict(self):
        """ Renvoyer un dictionnaire des coordonnées de l'objet """
        return {'latitude': self.position.get_y(), 'longitude': self.position.get_x()}

    def get_bounding_box(self, km):
        """
        Renvoyer les coordonnées d'un rectangle dont les coins sont à n km autour de l'objet

        :rtype: list
        """
        return CoordinatesModel.get_bounding_box_at(self.point, km)

    def get_bounding_poly(self, km):
        """ Renvoyer les coordonnées d'un rectangle dont les coins sont à n km autour de l'objet """
        box = self.get_bounding_box(km)
        result = Polygon.from_bbox([box[1], box[0], box[3], box[2]])
        return result

    @staticmethod
    def get_bounding_box_at(point, km):
        """ Renvoyer les coordonnées d'un rectangle n km autour d'un point """
        latitude = point[0]
        latitude = latitude if latitude not in (90, -90) else latitude + 1
        lat_offset = km * CoordinatesModel.KM_LAT
        lon_offset = km * CoordinatesModel.KM_LON / math.cos(math.radians(latitude))
        # Renvoyer un rectangle
        result = [point[0] - lat_offset, point[1] - lon_offset, point[0] + lat_offset, point[1] + lon_offset]
        return result

    @staticmethod
    def get_bounding_poly_at(point, km):
        """ Renvoyer les coordonnées d'un rectangle dont les coins sont à n km autour de l'objet """
        box = CoordinatesModel.get_bounding_box_at(point, km)
        result = Polygon.from_bbox([box[1], box[0], box[3], box[2]])
        return result

    @staticmethod
    def sexagesimal_from_degrees(degrees, longitudinal=True):
        """ Renvoyer une valeur horaire depuis une valeur en degrés """
        letters = pgettext_lazy('coordinates', "WE") if longitudinal else pgettext_lazy('coordinates', "SN")
        mnt, sec = divmod(degrees * 3600, 60.0)
        deg, mnt = divmod(mnt, 60)
        letter = letters[0 if deg < 0 else 1]
        # Formater les informations de coordonnées
        output = "{:.0f}°{:.0f}ʹ{:.03f}ʺ {}".format(abs(deg), mnt, sec, letter)
        return output

    @addattr(short_description=_("Coordinates"))
    def get_formatted_coordinates(self):
        """
        Renvoyer une représentation des coordonnées de l'objet
        """
        return "↑:{:.04f} →:{:.04f}".format(self.latitude, self.longitude)

    @addattr(admin_order_field='latitude', short_description=_("Sexagesimal"))
    def get_sexagesimal_coordinates(self):
        """ Renvoyer la représentation horaire des coordonnées de l'objet """
        return "{}, {}".format(self.sexagesimal_from_degrees(self.latitude, longitudinal=False),
                               self.sexagesimal_from_degrees(self.longitude, longitudinal=True))

    def get_distance(self, point=None, **kwargs):
        """
        Renvoyer la distance entre cet objet et une coordonnée

        :param point: liste, tuple, dictionnaire ou CoordinatesModel
        :returns: distance en kilomètres
        """
        if isinstance(point, (list, tuple)):
            return CoordinatesModel.GEODETIC_MODEL.inv(self.longitude, self.latitude, point[1], point[0])[2] / 1000.0
        elif isinstance(point, dict):
            return self.get_distance([point['latitude'], point['longitude']])
        elif isinstance(point, CoordinatesModel):
            return self.get_distance(point.get_point())
        return None

    def get_cardinal_position(self, point=None, mode='relative'):
        """
        Renvoyer la position relative d'un point (WGS84) par rapport à l'objet

        :param point: tuple ou liste représentant les coordonnées du point distant
        :param mode: name | relative | short | tick, choix du mode d'affichage de la position relative
            "name" : renvoyer des positions du type "Nord", "Sud"
            "relative" : renvoyer des positions du type "Au Nord", "Au Sud"
            "short" : renvoyer des positions du type "N", "S"
            "tick" : renvoyer un entier entre 0 et 15, où 0 = Est, et 4 = Nord
            Si un mode invalide est utilisé, "relative" est utilisé à la place
        :type mode: str
        :type point: list | tuple
        :returns: un texte de position relative en point cardinal, ex
            "au nord", "sud", "SE". Le texte de position peut être traduit.
            Renvoie une chaîne vide si les deux points sont confondus.
        :rtype: int | str
        """
        point, origin = list(point), self.get_point()
        delta = [point[1] - origin[1], point[0] - origin[0]]
        if delta == [0, 0]:
            return ""
        angle = math.degrees(atan2(delta[1], delta[0]) % (2.0 * pi))
        rounded_angle = round_multiple(angle, 22.5)
        angle_tick = int(rounded_angle / 22.5)
        cardinal_modes = {'name': ANGLE_CARDINAL, 'relative': RELATIVE_CARDINAL, 'short': SHORT_CARDINAL, 'tick': ANGLE_TICKS}
        result = cardinal_modes.get(mode or 'relative', RELATIVE_CARDINAL)
        return result[angle_tick % 16] if result else int(angle)

    def annotate_distance(self, queryset, related_field=None):
        """
        Annoter un queryset de CoordinatesModel avec un champ "distance", représentant la distance à cet objet

        :param queryset: queryset d'objets CoordinatesModel à trier autour de self
        :param related_field: trier le queryset sur un champ lié. Est une chaîne
            ex. "profile__city", où le dernier sous-champ correspond à un CoordinatesModel.
        :type related_field: str
        :returns: un queryset
        """
        # Calculer automatiquement la classe de modèle lié selon field
        related_model = queryset.model
        if related_field:
            for subfield in related_field.split('__')[:-1]:
                related_model = getattr(related_model, subfield).get_queryset().model

        if isinstance(queryset, QuerySet) and (issubclass(queryset.model, CoordinatesModel) or issubclass(related_model, CoordinatesModel)):
            queryset = queryset.annotate(distance=Distance(related_field, self.position))
            return queryset
        else:
            return queryset or []

    @staticmethod
    def convert_km_to(value, unit):
        """
        Convertir une longueur en km vers une autre unité

        :param unit: entre km|m|yd|ft|mi|nmi
        :type unit: str
        """
        if unit == 'km':
            return value
        return value * CoordinatesModel.UNIT_RATIO.get(unit, 1.0)

    # Overrides
    def __iter__(self):
        """ Renvoyer un itérateur sur les coordonnées de l'objet """
        return iter(self.get_point())

    # Propriétés
    latitude = property(get_latitude, set_latitude)
    longitude = property(get_longitude, set_longitude)
    point = property(get_point, set_point)

    # Métadonnées
    class Meta:
        abstract = True
