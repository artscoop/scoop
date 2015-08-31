# coding: utf-8
from __future__ import absolute_import

from ajax_select import LookupChannel
from unidecode import unidecode

from scoop.core.util.model.model import search_query
from scoop.forum.models.forum import Forum


class ForumLookup(LookupChannel):
    """ Lookup ajax-select des forums """
    model = Forum
    plugin_options = {'minLength': 4, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    def get_query(self, q, request):
        """ Renvoyer les objets correspondant à la requête """
        fields = ['name', 'description']
        final_query = search_query(unidecode(q), fields)
        items = Forum.objects.filter(final_query).distinct().order_by('-population')[0:12]
        return items

    def get_result(self, obj):
        """ Renvoyer la représentation texte de l'élément """
        return "{name}".format(name=obj.name)

    def format_match(self, obj):
        """ Renvoyer la représentation HTML de l'élément dans le dropdown """
        return "{name}".format(name=obj.name)

    def format_item_display(self, obj):
        """ Renvoyer la représentation HTML de l'élément dans le deck """
        return "{name}".format(name=obj.name)
