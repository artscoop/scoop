# coding: utf-8
from __future__ import absolute_import

import datetime

from django.conf import settings
from django.contrib.gis.db.models.manager import GeoManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.util.model.model import SingleDeleteManager


class PositionManager(SingleDeleteManager, GeoManager):
    """ Manager des positions """

    # Getter
    def in_box(self, box, since=3600):
        """ Renvoyer les positions dans une zone depuis un temps en secondes """
        min_time = Position.now() - datetime.timedelta(seconds=since)
        return Position.objects.filter(time__gt=min_time, latitude__range=(box[0], box[2]), longitude__range=(box[1], box[3]))

    def get_in_circle(self, center, radius, since=3600):
        """ Renvoyer les positions dans une zone circulaire depuis un temps en secondes """
        box = Position.get_bounding_box_at(center, radius)
        positions = self.in_box(box, since)
        return [position for position in positions if position.get_distance(center) <= radius]

    # Setter
    def set_position(self, user, lat=0.0, lon=0.0):
        """ Définir la position d'un utilisateur """
        position, _ = self.get_or_create(user=user)
        position.update(**{'latitude': lat, 'longitude': lon, 'time': position.now()})
        position.save()

    # Maintenance
    def purge(self, days=2, user=None):
        """ Supprimer les positions plus anciennes que n jours """
        max_time = Position().now() - datetime.timedelta(days=days)
        self.filter(time__lt=max_time, user=user).delete()


class Position(CoordinatesModel, DatetimeModel):
    """ Position utilisateur """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("User"))
    objects = PositionManager()

    # Getter
    def get_close_users(self, km):
        """ Renvoyer les utilisateurs proches à n km """
        return Position.get_users_in(self.get_bounding_box(km))

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return "%(user)s @ %(gps)s" % {'user': self.user, 'gps': self.get_formatted_coordinates()}

    # Métadonnées
    class Meta:
        verbose_name = _("user position")
        verbose_name_plural = _("user positioning")
        app_label = 'location'
