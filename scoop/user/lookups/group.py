# coding: utf-8
from __future__ import absolute_import

from ajax_select import LookupChannel
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from scoop.core.util.model.model import search_query


class GroupLookup(LookupChannel):
    """ Lookup ajax-select des groupes d'utilisateurs """
    model = Group
    plugin_options = {'minLength': 1}

    def get_query(self, q, request):
        """ Renvoyer le queryset de résultat de recherche """
        fields = ['name']
        final_query = search_query(q, fields)
        return Group.objects.filter(final_query).order_by('name')

    def get_result(self, obj):
        """ Renvoyer la représentation texte de l'élément """
        return obj.__unicode__()

    def format_match(self, obj):
        """ Renvoyer la représentation de l'élément dans le dropdown """
        return obj.__unicode__()

    def format_item_display(self, obj):
        """ Renvoyer la représentation de l'objet dans le deck """
        return "{}".format(obj)

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur en cours peut effectuer une requête """
        if not request.user.is_staff:
            raise PermissionDenied()
