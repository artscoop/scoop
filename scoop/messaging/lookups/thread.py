# coding: utf-8
from ajax_select import LookupChannel
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from scoop.core.util.model.model import search_query
from scoop.messaging.models.thread import Thread


class ThreadLookup(LookupChannel):
    """ Lookup ajax-select de fils de discussion """
    model = Thread
    plugin_options = {'minLength': 3}

    def get_query(self, q, request):
        """ Renvoyer le queryset d'objets correspondant au filtre """
        fields = ['topic', 'messages__text', 'recipients__user__username']
        final_query = search_query(q, fields)
        return get_user_model().objects.filter(final_query).order_by('-id')[0:12]

    def get_result(self, obj):
        """ Renvoyer la représentation texte d'un résultat """
        return obj.__str__()

    def format_match(self, obj):
        """ Renvoyer une représentation du résultat dans le dropdown """
        return obj.__str__()

    def format_item_display(self, obj):
        """ Renvoyer une représentation du résultat dans le deck """
        return "<strong>%s</strong>" % (obj,)

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur courant peut effectuer une requête """
        if not request.user.is_staff:
            raise PermissionDenied()
