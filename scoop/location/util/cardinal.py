# coding: utf-8
from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

# Constantes : Noms des points cardinaux à 1/16 (steps à Pi/8)
ANGLE_CARDINAL = {0: _("east"), 1: _("east-north-east"), 2: _("north-east"), 3: _("north-north-east"), 4: _("north"),
                  5: _("north-north-west"), 6: _("north-west"), 7: _("west-north-west"), 8: _("west"),
                  9: _("west-south-west"), 10: _("south-west"), 11: _("south-south-west"), 12: _("south"),
                  13: _("south-south-east"), 14: _("south-east"), 15: _("east-south-east")}

RELATIVE_CARDINAL = {0: _("to the east"), 1: _("to the east-north-east"), 2: _("to the north-east"), 3: _("to the north-north-east"), 4: _("to the north"),
                     5: _("to the north-north-west"), 6: _("to the north-west"), 7: _("to the west-north-west"), 8: _("to the west"),
                     9: _("to the west-south-west"), 10: _("to the south-west"), 11: _("to the south-south-west"), 12: _("to the south"),
                     13: _("to the south-south-east"), 14: _("to the south-east"), 15: _("to the east-south-east")}

SHORT_CARDINAL = {0: "E", 1: "ENE", 2: "NE", 3: "NNE", 4: "N", 5: "NNW", 6: "NW", 7: "WNW", 8: "W", 9: "WSW", 10: "SW", 11: "SSW", 12: "S", 13: "SSE", 14: "SE", 15: "ESE"}
