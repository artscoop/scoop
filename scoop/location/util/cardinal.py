# coding: utf-8
from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

# Constantes : Noms des points cardinaux à 1/16 (steps à Pi/8)
ANGLE_CARDINAL = {0: _(u"east"), 1: _("east-north-east"), 2: _(u"north-east"), 3: _(u"north-north-east"), 4: _(u"north"),
                  5: _(u"north-north-west"), 6: _(u"north-west"), 7: _(u"west-north-west"), 8: _(u"west"),
                  9: _(u"west-south-west"), 10: _(u"south-west"), 11: _(u"south-south-west"), 12: _(u"south"),
                  13: _(u"south-south-east"), 14: _(u"south-east"), 15: _(u"east-south-east")}

RELATIVE_CARDINAL = {0: _(u"to the east"), 1: _("to the east-north-east"), 2: _(u"to the north-east"), 3: _(u"to the north-north-east"), 4: _(u"to the north"),
                     5: _(u"to the north-north-west"), 6: _(u"to the north-west"), 7: _(u"to the west-north-west"), 8: _(u"to the west"),
                     9: _(u"to the west-south-west"), 10: _(u"to the south-west"), 11: _(u"to the south-south-west"), 12: _(u"to the south"),
                     13: _(u"to the south-south-east"), 14: _(u"to the south-east"), 15: _(u"to the east-south-east")}

SHORT_CARDINAL = {0: "E", 1: "ENE", 2: "NE", 3: "NNE", 4: "N", 5: "NNW", 6: "NW", 7: "WNW", 8: "W", 9: "WSW", 10: "SW", 11: "SSW", 12: "S", 13: "SSE", 14: "SE", 15: "ESE"}
