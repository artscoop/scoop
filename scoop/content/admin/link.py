# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.content.models.link import Link
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin


class LinkAdmin(AutoAuthoredModelAdmin, AjaxSelectAdmin):
    """ Administration des liens """
    list_select_related = True
    list_display = ['id', 'author', 'url', 'anchor', 'title', 'target', 'nofollow', 'group', 'get_uuid_html']
    list_display_links = ['id', 'url']
    list_editable = ['nofollow']
    list_filter = ['nofollow', 'group']
    search_fields = ['url', 'anchor', 'title']
    fieldsets = ((_("Link"), {'fields': ('author', 'group', 'url', 'anchor', 'title', 'target', 'nofollow')}), ('Plus', {'fields': (('content_type', 'object_id'), 'remainder', 'information')}))
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = make_ajax_form(Link, {'author': 'user'})


# Enregistrer les classes d'administration
admin.site.register(Link, LinkAdmin)
