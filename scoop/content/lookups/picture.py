# coding: utf-8
from __future__ import absolute_import

from ajax_select import LookupChannel
from django.core.exceptions import PermissionDenied

from scoop.content.models.picture import Picture
from scoop.core.util.model.model import search_query


class PictureLookup(LookupChannel):
    """ Ajax-select lookup Images """
    model = Picture
    plugin_options = {'minLength': 2, 'delay': 500}

    def get_query(self, q, request):
        """ Répondre à la requête """
        fields = ['title', 'description', 'image']
        final_query = search_query(q, fields)
        return Picture.objects.by_request(request).filter(final_query).order_by('-id')[0:12]

    def get_result(self, obj):
        """ Renvoyer le texte simple du résultat """
        return obj.__unicode__()

    def format_match(self, obj):
        """ Renvoyer le HTML de l'élément dans le dropdown """
        output = u"""<div>{thumb} {name}</div>""".format(thumb=obj.get_thumbnail_html(size=(48, 20), template='picture'), name=obj.title or obj.description)
        return output

    def format_item_display(self, obj):
        """ Renvoyer le HTML de l'élément dans le deck """
        output = u"""<div>{thumb} {name}</div>""".format(thumb=obj.get_thumbnail_html(size=(48, 20)), name=obj.title or obj.description)
        return output

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur peut faire une requête """
        if not request.user.is_authenticated():
            raise PermissionDenied()
