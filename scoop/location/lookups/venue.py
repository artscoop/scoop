# coding: utf-8
from __future__ import absolute_import

from ajax_select import LookupChannel
from unidecode import unidecode

from scoop.core.util.model.model import search_query
from scoop.location.models.venue import Venue


class VenueLookup(LookupChannel):
    """ Lookup ajax-select des lieux """
    model = Venue
    plugin_options = {'minLength': 4, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    def get_query(self, q, request):
        """ Renvoyer les villes correspondant à la requête """
        fields = ['name', 'street', 'city__alternates__ascii']
        final_query = search_query(unidecode(q), fields)
        items = Venue.objects.filter(final_query).distinct().order_by('name')[0:12]
        return items

    def get_result(self, obj):
        """ Renvoyer la représentation texte de l'objet """
        output = "{venue}".format(venue=obj)
        return output

    def format_match(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le dropdown """
        output = "{venue}".format(venue=obj)
        return output

    def format_item_display(self, obj):
        """ Renvoyer la représentation HTML de l'objet dans le deck """
        output = "<span class='muted'>{city}</span> <strong>{venue}</strong> {country}".format(city=obj.city.get_name(), venue=obj)
        return output
