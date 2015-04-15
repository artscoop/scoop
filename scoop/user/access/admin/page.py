# coding: utf-8
from __future__ import absolute_import

from django.contrib import admin

__all__ = ['PageAdmin']


class PageAdmin(admin.ModelAdmin):
    """ Administration des pages visitées sur le site """
    list_select_related = True
    list_display = ['id', 'path']
    list_filter = []
    search_fields = ['path']
    actions = []

    # Actions
    def get_actions(self, request):
        """ Renvoyer la liste des actions disponibles """
        return []
