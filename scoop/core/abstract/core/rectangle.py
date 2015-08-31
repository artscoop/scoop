# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from cmath import sqrt
from scoop.core.util.shortcuts import addattr


class RectangleObject(object):
    """ Mixin d'objet pour un rectangle """
    width = 0.0
    height = 0.0

    # Getter
    @addattr(short_description=_("Dimension"))
    def get_formatted_dimension(self):
        """ Renvoyer la représentation chaîne des dimensions """
        return "{width}x{height}".format(width=self.width, height=self.height)

    def has_dimension(self):
        """ Renvoyer si les dimensions de l'objet sont valides """
        return self.width and self.height

    def get_perimeter(self):
        """ Renvoyer le périmètre du rectangle """
        return self.width * 2 + self.height * 2 if self.has_dimension() else 0

    def get_area(self):
        """ Renvoyer l'aire du rectangle """
        return self.width * self.height if self.has_dimension() else 0

    def get_diagonal(self):
        """ Renvoyer la longueur de la diagonale du rectangle """
        return sqrt(self.width ** 2 + self.height ** 2) if self.has_dimension() else 0

    @addattr(short_description=_("Ratio"))
    def get_dimension_ratio(self):
        """ Renvoyer la représentation chaîne du ration de l'image """
        RATIOS = {133: "4:3", 160: "16:10", 200: "2:1 wide", 177: "16:9", 125: "5:4", 100: "Square", 150: "3:2"}
        ratio = 100.0 * self.width / self.height
        valid = [RATIOS[item] for item in RATIOS if (item - ratio) ** 2 <= 16] or ['']
        return valid[0]


class RectangleModel(models.Model, RectangleObject):
    """ Mixin de modèle avec des dimensions """
    width = models.IntegerField(default=0, blank=True, null=True, verbose_name=pgettext_lazy("geometry", "Width"))
    height = models.IntegerField(default=0, blank=True, null=True, verbose_name=pgettext_lazy("geometry", "Height"))

    # Métadonnées
    class Meta:
        abstract = True


class FloatRectangleModel(models.Model, RectangleObject):
    """ Mixin de modèle ayant des dimensions à virgule flottante """
    width = models.FloatField(default=0.0, blank=True, null=True, verbose_name=pgettext_lazy("geometry", "Width"))
    height = models.FloatField(default=0.0, blank=True, null=True, verbose_name=pgettext_lazy("geometry", "Height"))

    # Métadonnées
    class Meta:
        abstract = True
