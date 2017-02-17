# coding: utf-8
from ajax_select.admin import AjaxSelectAdmin
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.user.social.models.event import Event
from scoop.user.social.models.event.eventcategory import EventCategory


@admin.register(Event)
class EventAdmin(AjaxSelectAdmin):
    """ Admin des événements """
    list_select_related = True
    list_display = ['author', 'title', 'description']
    list_filter = ['access']
    list_editable = []
    readonly_fields = ['author']


class EventCategoryInlineAdmin(admin.TabularInline):
    """ Admin inline des catégories d'événements """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = EventCategory
    max_num = len(settings.LANGUAGES)
    extra = 4
    formfield_overrides = {models.TextField: {'widget': admin.widgets.AdminTextInputWidget}}


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    """ Admin des catégories d'événements """
    list_select_related = True
    list_display = ['icon', 'get_name', 'parent']
    list_filter = []
    list_editable = []
    search_fields = ['translations__name']
    readonly_fields = []
    inlines = [EventCategoryInlineAdmin]
    fieldsets = ((_("event category"), {'fields': ('icon', 'parent')}),)
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
