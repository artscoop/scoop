# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from django.contrib import admin

from scoop.rogue.forms.mailblock import MailBlockForm
from scoop.rogue.models import MailBlock, Profanity


class MailBlockAdmin(admin.ModelAdmin):
    """ Administration des blocages d'adresses email """
    # Configuration
    list_select_related = True
    list_display = ['id', 'email', 'user', 'active']
    list_editable = []
    search_fields = ['email', 'user__username']
    readonly_fields = []
    form = make_ajax_form(MailBlock, {'user': 'user'}, MailBlockForm)


class ProfanityAdmin(admin.ModelAdmin):
    """ Administration des filtrages de grossièretés """
    # Configuration
    list_select_related = True
    list_display = ['id', 'active', 'regex', 'standalone']
    list_editable = ['active']
    list_filter = ['active', 'standalone']
    search_fields = ['regex']

# Enregistrer les classes d'administration
admin.site.register(MailBlock, MailBlockAdmin)
admin.site.register(Profanity, ProfanityAdmin)
