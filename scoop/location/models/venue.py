# coding: utf-8
from __future__ import absolute_import

from django.contrib.gis.db.models.manager import GeoManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.location.coordinates import CoordinatesModel
from scoop.core.abstract.user.authorable import AuthorableModel
from scoop.core.util.model.model import SingleDeleteManager


class VenueManager(SingleDeleteManager, GeoManager):
    """ Manager des lieux """

    # Getter
    def venues_in(self, box):
        """ Renvoyer les lieux dans une zone rectangulaire """
        return self.filter(latitude__range=(box[0], box[2]), longitude__range=(box[1], box[3]))

    def venues_around(self, coordinates_instance, km=1):
        """ Renvoyer les lieux à n km autour d'une instance de CoordinatesModel """
        if isinstance(coordinates_instance, CoordinatesModel):
            return self.get_venues_in(coordinates_instance.get_bounding_box(km))
        return None


class Venue(CoordinatesModel, PicturableModel, DatetimeModel, AuthorableModel):
    """ Lieu précis avec un nom """
    type = models.ForeignKey('location.VenueType', null=True, verbose_name=_("Venue type"))
    name = models.CharField(max_length=64, db_index=True, verbose_name=_("Name"))
    street = models.CharField(max_length=80, db_index=True, help_text=_("Way number, type and name"), verbose_name=_("Way"))
    city = models.ForeignKey('location.City', related_name='venues', verbose_name=_("City"))
    full = models.CharField(max_length=250, help_text=_("Full address, lines separated by semicolons"), verbose_name=_("Full address"))
    url = models.URLField(max_length=160, blank=True, verbose_name=_("URL"))
    objects = VenueManager()

    # Getter
    def get_country(self):
        """ Renvoyer le pays du lieu """
        return self.city.country if self.city else None

    def get_formatted_text(self):
        """ Renvoyer une représentation textuelle du lieu """
        return _("{name}, {city}, {country}").format(name=self.name, city=self.city, country=self.get_country())

    def get_close_venues(self, km=1):
        """ Renvoyer les lieux à n km du lieu """
        return Venue.objects.venues_around(self, km)

    def get_full_address(self):
        """ Renvoyer l'adresse complète du lieu """
        return self.full.split(";")

    # Propriétés
    split_full = property(get_full_address)

    # Setter
    def fetch_picture(self):
        """ Télécharger automatiquement une image pour le lieu """
        from scoop.content.models.picture import Picture
        # Ne rien faire si des images existent
        if self.pictures.all().exists():
            return
        # Parcourir
        expression = "{name} {city}".format(street=self.street, city=self.city, name=self.name)
        images = Picture.objects.find_by_keyword(expression)
        if len(images) > 0:
            Picture.objects.create_from_uri(images[0]['url'], content_object=self, description=images[0]['title'])

    # Overides
    def __unicode__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return self.split_full

    # Métadonnées
    class Meta:
        verbose_name = _("venue")
        verbose_name_plural = _("venues")
        index_together = []
        unique_together = [['name', 'street', 'city']]
        app_label = 'location'
