# coding: utf-8
from ajax_select import LookupChannel
from django.core.exceptions import PermissionDenied
from django.templatetags.l10n import localize
from scoop.content.models.content import Content
from scoop.core.templatetags.text_tags import humanize_join
from scoop.core.util.model.model import search_query
from unidecode import unidecode


class ContentLookup(LookupChannel):
    """ Ajax-select lookup Contenus """
    model = Content
    plugin_options = {'minLength': 4, 'position': {"my": "left bottom", "at": "left top", "collision": "flip"}}

    def get_query(self, q, request):
        """ Répondre à la requête """
        fields = ['title', 'teaser', 'tags__name']
        final_query = search_query(unidecode(q), fields)
        items = Content.objects.by_request(request).filter(final_query).distinct().order_by('-updated')[0:12]
        return items

    def get_result(self, obj):
        """ Renvoyer le texte simple du résultat """
        return "{}".format(obj.title)

    def format_match(self, obj):
        """ Renvoyer le HTML de l'élément dans le dropdown """
        return "{}".format(obj.title)

    def format_item_display(self, obj):
        """ Renvoyer le HTML de l'élément dans le deck """
        return "<strong>{title}</strong><br><small>{when}</small><br>{author}".format(title=obj.title, author=humanize_join(obj.get_authors(), 2),
                                                                                      when=localize(obj.created))

    def check_auth(self, request):
        """ Renvoyer si l'utilisateur peut faire une requête """
        if not request.user.is_authenticated():
            raise PermissionDenied()
