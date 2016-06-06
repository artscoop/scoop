# coding: utf-8
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.helpers import make_ajax_form
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.forum.models.label import Label
from scoop.forum.models.thread import Thread


class LabelAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration de forum """

    # Configuration
    list_display = ['id', 'short_name', 'name', 'description', 'primary', 'status', 'visible']
    list_editable = ['short_name']
    list_filter = ['primary', 'visible', 'status', 'groups']
    search_fields = ['short_name', 'translations__name', 'translations__description', 'translations__html']
    list_per_page = 25


class ThreadAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration de forum """

    # Configuration
    list_display = ['id', 'topic', 'author', 'started', 'updated', 'counter', 'visible', 'sticky', 'locked']
    list_filter = ['visible', 'sticky', 'locked', 'started', 'updated']
    search_fields = ['topic', 'messages__text']
    form = make_ajax_form(Thread, {'author': 'user'})
    actions = ['resave', 'lock', 'hide']
    list_per_page = 25

    # Actions
    @addattr(short_description=_("Update information of selected threads"))
    def resave(self, request, queryset):
        """ Sauvegarder à nouveau le contenu pour mettre à jour les informations """
        for thread in queryset:
            thread.save()
        self.message_user(request, _("The selected threads have been successfully updated."))

    @addattr(short_description=_("Lock selected threads"))
    def lock(self, request, queryset):
        """ Verrouiller les fils """
        count = 0
        for thread in queryset:
            count += 1 if thread.lock() else 0
        self.message_user(request, _("{count} threads have been locked.").format(count=count))

    @addattr(short_description=_("Hide selected threads"))
    def hide(self, request, queryset):
        """ Verrouiller les fils """
        count = 0
        for thread in queryset:
            count += 1 if thread.set_visible(False) else 0
        self.message_user(request, _("{count} threads have been hidden.").format(count=count))


# Enregistrer les classes d'administration
admin.site.register(Label, LabelAdmin)
admin.site.register(Thread, ThreadAdmin)
