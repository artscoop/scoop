# coding: utf-8
from __future__ import absolute_import

from django.contrib import admin

from scoop.core.models.uuidentry import UUIDEntry
from scoop.core.util.django.admin import GenericModelUtil, ViewOnlyModelAdmin


class UUIDEntryAdmin(ViewOnlyModelAdmin, GenericModelUtil):
    """ Administration du registre des UUID """
    list_select_related = True
    list_display = ['id', 'uuid', 'get_content_type_info', 'get_content_object_info']
    list_display_links = []
    list_filter = ['content_type']
    list_editable = []
    readonly_fields = ['uuid', 'content_type', 'object_id']
    search_fields = ['uuid']
    actions = []
    exclude = []
    actions_on_top = False
    order_by = ['content_type']

# Enregistrer les classes d'administration
admin.site.register(UUIDEntry, UUIDEntryAdmin)
