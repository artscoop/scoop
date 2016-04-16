# coding: utf-8
from ajax_select import LookupChannel
from django.core.exceptions import PermissionDenied
from unidecode import unidecode

from scoop.content.models.comment import Comment
from scoop.core.util.model.model import search_query


class CommentLookup(LookupChannel):
    """ Ajax-select lookup Commentaires """
    model = Comment
    plugin_options = {'minLength': 5, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    def get_query(self, q, request):
        """ Répondre à la requête """
        fields = ['name', 'body', 'url', 'email']
        final_query = search_query(unidecode(q), fields)
        items = Comment.objects.filter(final_query).distinct().order_by('-time')[0:12]
        return items

    def get_result(self, obj):
        """ Renvoyer le texte simple du résultat """
        return "{}".format(obj.body)

    def format_match(self, obj):
        """ Renvoyer le HTML de l'élément dans le dropdown """
        return "{}".format(obj.body)

    def format_item_display(self, obj):
        """ Renvoyer le HTML de l'élément dans le deck """
        return "{}".format(obj.body)

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur peut faire une requête """
        if not request.user.is_authenticated():
            raise PermissionDenied()
