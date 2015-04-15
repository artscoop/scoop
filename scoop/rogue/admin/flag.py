# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.util.django.admin import GenericModelUtil
from scoop.core.util.shortcuts import addattr
from scoop.rogue.admin.filters import FlagStatusFilter
from scoop.rogue.models import Flag, FlagType, FlagTypeTranslation


class FlagAdmin(AjaxSelectAdmin, AutoAuthoredModelAdmin, GenericModelUtil):
    """ Administration des signalements """
    # Configuration
    list_select_related = True
    list_display = ['id', 'author', 'get_content_type_info', 'get_content_object_info', 'type', 'get_status', 'get_url', 'details', 'automatic', 'get_datetime_ago']
    list_editable = ()
    list_display_links = ('id',)
    search_fields = ['details', 'status', 'name']
    actions = ['wont_fix', 'fix']
    form = make_ajax_form(Flag, {'moderators': 'user', 'author': 'user'})
    exclude = ()
    list_filter = ('type', 'action_done', FlagStatusFilter, 'content_type', 'automatic')
    filter_horizontal = ['moderators']
    readonly_fields = []
    save_on_top = False
    fieldsets = (
        (_(u"Flag"), {'fields': ('author', ('content_type', 'object_id',), 'type', 'status', 'details')}), ('Plus', {'fields': ('moderators', 'admin', 'automatic', 'url', 'priority')}))
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

    # Actions
    @addattr(short_description=_(u"Will not fix"))
    def wont_fix(self, request, queryset):
        """ Classer les signalements comme Won't Fix """
        for flag in queryset:
            flag.close(Flag.WONTFIX)
        self.message_user(request, _(u"Selected flags successfully closed."))

    @addattr(short_description=_(u"Automatically fix"))
    def fix(self, request, queryset):
        """ Traiter automatiquement un signalement """
        for flag in queryset:
            flag.resolve()
        self.message_user(request, _(u"Selected flags successfully resolved."))

    # Getter
    @addattr(allow_tags=True, short_description=_(u"URL"))
    def get_url(self, obj):
        """ Renvoyer l'URL du signalement """
        html = "<a class='modal-action' href='%(url)s'>%(url)s</a>" % {'url': obj.url}
        return html

    @addattr(allow_tags=True, admin_order_field='status', short_description=_(u"Status"))
    def get_status(self, obj):
        """ Renvoyer le statut du signalement """
        types = {0: 'important', 1: 'warning', 2: 'success', 3: 'success', 4: 'sucess', 5: 'info', 6: 'info'}
        html = "<span class='modal-action label label-%(css)s'>%(status)s</span>" % {'status': obj.get_status_display(), 'css': types.get(obj.status)}
        return html

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut de l'administration """
        qs = super(FlagAdmin, self).queryset(request)
        if not request.user.is_superuser:
            return qs.filter(moderators=request.user)
        return qs


class FlagTypeTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin de traduction des types de signalement """
    verbose_name = _(u"Translation")
    verbose_name_plural = _(u"Translations")
    model = FlagTypeTranslation
    max_num = len(settings.LANGUAGES)
    formfield_overrides = {models.TextField: {'widget': AdminTextInputWidget}}
    extra = 2


class FlagTypeAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Administration des types de signalements """
    list_select_related = True
    list_display = ['id', 'short_name', 'get_name', 'get_description', 'get_content_type_info']
    list_editable = ['short_name']
    list_filter = ['content_type']
    search_fields = []
    readonly_fields = []
    inlines = [FlagTypeTranslationInlineAdmin, ]
    fieldsets = ((_(u"Flag type"), {'fields': ('short_name', 'content_type', 'icon')}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

# Enregistrer les classes d'administration
admin.site.register(Flag, FlagAdmin)
admin.site.register(FlagType, FlagTypeAdmin)
