# coding: utf-8
from django.contrib import admin
from scoop.help.models.context import ContextHelp


@admin.register(ContextHelp)
class ContextHelpAdmin(admin.ModelAdmin):
    """ Administration des aides contextuelles """

    # Configuration
    list_select_related = True
    list_display = ['id', 'uuid', 'language', 'active', 'name', 'text']
    list_filter = ['active', 'language']
    list_editable = ['active']
    search_fields = ['uuid', 'text', 'name']
    ordering = ['-id']
    actions = []
    inlines = []
