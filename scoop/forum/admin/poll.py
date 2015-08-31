# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.forum.models import Poll


class PollAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration des sondages """
    list_select_related = True
    list_display = ['id', 'title', 'description', 'is_open', 'published', 'expires']
    list_filter = []
    readonly_fields = ['author', 'slug']
    fieldsets = ((_("Poll"), {'fields': ('author', 'title', 'description', 'published', 'content',)}), ('Plus', {'fields': ('answers', 'closed', 'expires',)}))
    form = make_ajax_form(Poll, {'author': 'user'})
    inlines = []
    filter_horizontal = []
    search_fields = ['title', 'description']

# Enregistrer les classes d'administration
admin.site.register(Poll, PollAdmin)
