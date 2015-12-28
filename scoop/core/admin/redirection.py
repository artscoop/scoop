# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from pretty_times import pretty
from scoop.core.models.redirection import Redirection
from scoop.core.util.django.admin import GenericModelUtil, ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr


class RedirectionAdmin(ViewOnlyModelAdmin, GenericModelUtil):
    """ Administration des redirections """
    list_select_related = True
    list_display = ['id', 'active', 'base', 'get_content_type_info', 'get_content_object_info', 'get_expires']
    list_display_links = []
    list_filter = ['content_type']
    list_editable = []
    readonly_fields = ['content_type', 'object_id']
    search_fields = []
    actions = []
    exclude = []
    actions_on_top = False
    order_by = ['content_type']

    # Getter
    @addattr(allow_tags=True, admin_order_field='expires', short_description=_("Expires"))
    def get_expires(self, obj):
        """ Renvoyer la date d'expiration d'une redirection """
        return pretty.date(obj.expires).replace(' ', '&nbsp;')

# Enregistrer les classes d'administration
admin.site.register(Redirection, RedirectionAdmin)
