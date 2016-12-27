# coding: utf-8
from ajax_select import LookupChannel
from scoop.core.util.model.model import search_query
from scoop.forum.models.label import Label
from unidecode import unidecode


class LabelLookup(LookupChannel):
    """ Lookup ajax-select des forums """

    # Configuration
    model = Label
    plugin_options = {'minLength': 4, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    def get_query(self, q, request):
        """ Renvoyer les objets correspondant à la requête """
        fields = ['short_name', 'translations__name']
        final_query = search_query(unidecode(q), fields)
        items = Label.objects.filter(final_query).distinct()[0:12]
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
