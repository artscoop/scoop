# coding: utf-8
from ajax_select import LookupChannel
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from scoop.core.util.model.model import search_query


class PermissionLookup(LookupChannel):
    """ Lookup ajax-select des permissions """
    model = Permission
    plugin_options = {'minLength': 2}

    def get_query(self, q, request):
        """ Renvoyer le queryset de résultats pour l'expression """
        fields = ['name', 'codename']
        final_query = search_query(q, fields)
        return Permission.objects.filter(final_query).order_by('name')

    def get_result(self, obj):
        """ Renvoyer la représentation texte d'un résultat """
        return obj.__str__()

    def format_match(self, obj):
        """ Renvoyer la représentation de l'élément dans le dropdown """
        return obj.__str__()

    def format_item_display(self, obj):
        """ Renvoyer la représentation de l'élément dans le deck """
        return "{}".format(obj)

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur courant peut effectuer des requêtes """
        if not request.user.is_staff:
            raise PermissionDenied()
