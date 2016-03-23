# coding: utf-8
import datetime

from annoying.fields import AutoOneToOneField
from django.conf import settings
from django.contrib.gis.db.models.manager import GeoManager
from django.contrib.gis.geos.point import Point
from django.contrib.gis.measure import D
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.model.model import SingleDeleteManager


class PositionManager(SingleDeleteManager, GeoManager):
    """ Manager des positions """

    # Getter
    def in_box(self, box, since=3600):
        """
        Renvoyer les positions dans une zone depuis un temps en secondes

        :param box: [lat1, lon1, lat2, lon2]
        :param since: renvoyer les mises à jour plus récentes que n secondes
        """
        min_time = Position.now() - since
        return self.filter(time__gt=min_time, latitude__range=(box[0], box[2]), longitude__range=(box[1], box[3]))

    def in_radius(self, point, km, since=3600):
        """
        Renvoyer les positions dans une zone circulaire depuis un temps en secondes

        :param point: centre de recherche des positions
        :param km: rayon de recherche en km
        :param since: renvoyer les résultats mis à jour plus récemment que n secondes
        """
        min_time = Position.now() - since
        center = Point(point[1], point[0], srid=CoordinatesModel.SRID)
        return self.filter(time__gt=min_time, position__distance_lt=(center, D(km=km)))

    # Setter
    def set_position(self, user, lat=0.0, lon=0.0):
        """
        Définir la position d'un utilisateur

        :param user: utilisateur
        :param lat: latitude WGS84
        :param lon: longitude WGS84
        """
        position, _ = self.get_or_create(user=user)
        position.update(time=position.now(), position=Point(x=lon, y=lat))
        position.save()
        return position

    # Maintenance
    def purge(self, days=2, user=None):
        """ Supprimer les positions plus anciennes que n jours

        :param user: utilisateur
        :param days: nombre de jours d'ancienneté minimum
        """
        max_time = Position().now() - days * 86400
        self.filter(time__lt=max_time, user=user).delete()


class Position(CoordinatesModel, DatetimeModel):
    """ Position utilisateur """

    # Champs
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name='position', verbose_name=_("User"))
    objects = PositionManager()

    # Getter
    def get_close_users(self, km):
        """
        Renvoyer les utilisateurs proches à n km

        :param km: distance max en km
        """
        return Position.get_users_in(self.get_bounding_box(km))

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "{user} @ {gps}".format(user=self.user, gps=self.get_formatted_coordinates())

    # Métadonnées
    class Meta:
        verbose_name = _("user position")
        verbose_name_plural = _("user positioning")
        app_label = 'location'
