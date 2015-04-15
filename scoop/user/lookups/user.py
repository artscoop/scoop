# coding: utf-8
from __future__ import absolute_import

from ajax_select import LookupChannel
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from scoop.core.util.model.model import search_query


class UserLookup(LookupChannel):
    """ Lookup ajax-select des utilisateurs """
    model = get_user_model()
    plugin_options = {'minLength': 3}

    def get_query(self, q, request):
        """ Renvoyer un queryset de résultats pour l'expression """
        fields = ['username', 'name', 'email']
        final_query = search_query(q, fields)
        return get_user_model().objects.by_request(request).filter(final_query).order_by('username')[0:12]

    def get_result(self, obj):
        """ Renvoyer la représentation texte de l'élément """
        return obj.__unicode__()

    def format_match(self, obj):
        """ Renvoyer la représentation de l'élément dans le dropdown """
        return obj.__unicode__()

    def format_item_display(self, obj):
        """ Renvoyer la représentation de l'élément dans le deck """
        return u"<strong>{}</strong> / {}".format(obj.username, obj.__unicode__())

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur courant peut effectuer une requête """
        if not request.user.is_authenticated():
            raise PermissionDenied()
