# coding: utf-8
from __future__ import absolute_import, division

import math
from math import atan2, degrees, pi

import pyproj
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from scoop.core.templatetags.type_tags import round_multiple
from scoop.core.util.shortcuts import addattr
from scoop.location.util.cardinal import ANGLE_CARDINAL, RELATIVE_CARDINAL, SHORT_CARDINAL


class CoordinatesModel(models.Model):
    """ Mixin d'objet localisé par GPS """
    # Constantes
    KM_LON, KM_LAT = 0.008998308318036208, 0.008983111749910169
    UNIT_RATIO = {'km': 1.0, 'm': 1000, 'mi': 0.621371192237334, 'yd': 1093.6132983377076, 'ft': 3280.839895013123, 'nmi': 0.5399568034557235}
    GEODETIC_MODEL = pyproj.Geod(ellps="WGS84")
    SRID = 4326
    # Position géographique du centre de l'objet
    position = models.PointField(default=Point(0.0, 0.0), srid=SRID)

    # Setter
    def set_coordinates(self, lat, lon):
        """ Définir les coordonnées de l'objet """
        self.position.set_coords(sorted((-180.0, lon, 180.0))[1], sorted((-90.0, lat, 90.0))[1])

    def set_longitude(self, lon):
        self.position.set_x(sorted((-180.0, lon, 180.0))[1])

    def set_latitude(self, lat):
        self.position.set_y(sorted((-90.0, lat, 90.0))[1])

    # Getter
    def get_point(self):
        """ Renvoyer les coordonnées lat,lon de l'objet """
        return [self.position.get_y(), self.position.get_x()]

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
        """ Renvoyer les coordonnées d'un rectangle dont les coins sont à n km autour de l'objet """
        lat_offset = km * self.KM_LAT
        lon_offset = km * self.KM_LON / math.cos(math.radians(self.position.get_y()))
        # Renvoyer un rectangle
        result = [self.latitude - lat_offset, self.longitude - lon_offset, self.latitude + lat_offset, self.longitude + lon_offset]
        return result

    def get_bounding_poly(self, km):
        """ Renvoyer les coordonnées d'un rectangle dont les coins sont à n km autour de l'objet """
        box = self.get_bounding_box(km)
        result = Polygon.from_bbox([box[1], box[0], box[3], box[2]])
        return result

    def __iter__(self):
        """ Renvoyer un itérateur sur les coordonnées de l'objet """
        return iter([self.latitude, self.longitude])

    @staticmethod
    def get_bounding_box_at(point, km):
        """ Renvoyer les coordonnées d'un rectangle n km autour d'un point """
        lat_offset = km * CoordinatesModel.KM_LAT
        lon_offset = km * CoordinatesModel.KM_LON / math.cos(math.radians(point[0]))
        # Renvoyer un rectangle
        result = [point[0] - lat_offset, point[1] - lon_offset, point[0] + lat_offset, point[1] + lon_offset]
        return result

    @staticmethod
    def sexagesimal_from_degrees(degrees, longitudinal=True):
        """ Renvoyer une valeur horaire depuis une valeur en degrés """
        letters = _("WE") if longitudinal else _("SN")
        mnt, sec = divmod(degrees * 3600, 60.0)
        deg, mnt = divmod(mnt, 60)
        letter = letters[0 if deg < 0 else 1]
        # Formater les informations de coordonnées
        output = "{:.0f}°{:.0f}ʹ{:.03n}ʺ {}".format(abs(deg), mnt, sec, letter)
        return output

    @addattr(short_description=_("Coordinates"))
    def get_formatted_coordinates(self):
        """ Renvoyer une représentation des coordonnées de l'objet """
        return "↓:{:.04f} →:{:.04f}".format(self.latitude, self.longitude)

    @addattr(admin_order_field='latitude', short_description=_("Sexagesimal"))
    def get_sexagesimal_coordinates(self):
        """ Renvoyer la représentation horaire des coordonnées de l'objet """
        return "{}, {}".format(self.sexagesimal_from_degrees(self.latitude, longitudinal=False), self.sexagesimal_from_degrees(self.longitude, longitudinal=True))

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
        Renvoyer la position relative d'un point par rapport à l'objet
        :param point: tuple ou liste
        :param mode: name|relative|short, pour renvoyer des variantes de la position relative
        :returns: un texte de position relative en point cardinal
        """
        point, origin = list(point), self.get_point()
        delta = [point[1] - origin[1], point[0] - origin[0]]
        if delta == [0, 0]:
            return ""
        angle = degrees(atan2(delta[1], delta[0]) % (2.0 * pi))
        rounded_angle = round_multiple(angle - 11.25, 22.5)
        angle_tick = int(rounded_angle / 22.5)
        cardinal_modes = {'name': ANGLE_CARDINAL, 'relative': RELATIVE_CARDINAL, 'short': SHORT_CARDINAL}
        result = cardinal_modes.get(mode or 'relative', None)
        return result[angle_tick] if result else int(angle)

    def order_by_distance(self, queryset, reverse=False, as_queryset=True, related={'field': None, 'model': None}, add_field_only=False):
        """
        DEPRECATED: Trier un queryset de CoordinatesModel par leur distance à cet objet
        Utiliser l'annotation Distance dans scoop.location.util.gis ou dans Django 1.9
        :param queryset: queryset d'objets CoordinatesModel
        :param reverse: tri descendant
        :param as_queryset: renvoyer un queryset au lieu d'une liste
        :param related: trier le queryset sur un champ lié. Est un dictionnaire dont
            les clés sont 'field' et 'model'. 'field' est une chaine du type
            "profile__city", où le dernier sous-champ correspond à un CoordinatesModel.
            'model' indique la classe de modèle du champ lié, et doit hériter de
            CoordinatesModel
        :param add_field_only: ne pasa trier, mais ajouter un champ distance aux éléments
            le champ distance ajouté ne contient pas une vraie distance en km mais une
            valeur proportionnelle utilisable pour trier par distance.
        :returns: un queryset ou une liste d'objets triée
        """
        if isinstance(queryset, QuerySet) and (issubclass(queryset.model, CoordinatesModel) or issubclass(related['model'], CoordinatesModel)):
            # Tri du Queryset par calcul dans la requête
            if as_queryset is True:
                db_table = '{}'.format(related['model']._meta.db_table if related['model'] else '')
                lon_ratio = math.cos(math.radians(self.latitude)) ** 2
                delta_lat = "({table}.latitude - {latitude:.06f})".format(table=db_table, latitude=self.latitude)
                delta_lon = "({table}.longitude - {longitude:.06f})".format(table=db_table, longitude=self.longitude)
                output_queryset = queryset.select_related(related['field']).extra(
                    select={'distance': '{dlat}*{dlat} + {dlon}*{dlon}*{ratio:.010f}'.format(dlat=delta_lat, dlon=delta_lon, ratio=lon_ratio)})
                if add_field_only is False:
                    output_queryset = output_queryset.extra(order_by=['distance'])
                    output_queryset = output_queryset.reverse() if reverse else output_queryset
                return output_queryset
            # Tri dont la sortie est une liste d'instances
            elif as_queryset is False:
                if related['field'] is None:
                    output_list = sorted(queryset, key=lambda item: item.get_distance(self))
                else:
                    subfields = related['field'].split('__')

                    def get_distance(instance, subfields):
                        for subfield in subfields:
                            instance = getattr(instance, subfield)
                        return instance.get_distance(self)

                    output_list = sorted(queryset, key=lambda item: get_distance(item, subfields))
                output_list.reverse() if (reverse is True) else ()
                return output_list
        else:
            return queryset or queryset.model._default_manager.none()

    @staticmethod
    def convert_km_to(value, unit):
        """
        Convertir une longueur en km vers une autre unité
        :param unit: entre km|m|yd|ft|mi|nmi
        """
        if unit == 'km':
            return value
        return value * CoordinatesModel.UNIT_RATIO.get(unit, 1.0)

    # Propriétés
    latitude = property(get_latitude, set_latitude)
    longitude = property(get_longitude, set_longitude)

    # Métadonnées
    class Meta:
        abstract = True
