# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.models.option import Option, OptionTranslation
from scoop.core.models.optiongroup import OptionGroup, OptionGroupTranslation
from scoop.core.util.shortcuts import addattr


class OptionTranslationInlineAdmin(admin.TabularInline):
    """ Inline d'admin des traductions d'options """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = OptionTranslation
    max_num = len(settings.LANGUAGES)
    extra = 2
    formfield_overrides = {models.TextField: {'widget': AdminTextInputWidget}, }


class OptionAdmin(admin.ModelAdmin):
    """ Administration des options """
    list_select_related = True
    list_display = ['id', 'get_uuid_html', 'group', 'get_short_name', 'code', 'name', 'parent', 'active']
    list_display_links = []
    list_filter = ['group']
    list_editable = ['active']
    list_per_page = 25
    readonly_fields = []
    search_fields = ['translations__name', 'code']
    actions = []
    save_on_top = False
    fieldsets = ((_("Option"), {'fields': ('group', 'code', 'active', 'parent')}),)
    inlines = [OptionTranslationInlineAdmin, ]
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    ordering = ['-group', 'code']

    # Getter
    @addattr(short_description=_("Short name"))
    def get_short_name(self, obj):
        """ Renvoyer le nom court du groupe de l'option """
        return obj.group.short_name


class OptionGroupTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin de traduction des groupes d'options """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = OptionGroupTranslation
    max_num = len(settings.LANGUAGES)
    extra = 4
    formfield_overrides = {models.TextField: {'widget': admin.widgets.AdminTextInputWidget}, }


class OptionGroupAdmin(admin.ModelAdmin):
    """ Administration des groupes d'options """
    list_select_related = True
    list_display = ['id', 'name', 'short_name', 'code']
    list_display_links = []
    list_filter = ['code']
    list_editable = ['short_name', 'code']
    readonly_fields = []
    search_fields = ['name', 'short__name', 'code']
    actions = []
    save_on_top = False
    fieldsets = ((_("Option group"), {'fields': ('code', 'short_name')}),)
    inlines = [OptionGroupTranslationInlineAdmin, ]
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'

# Enregistrer les classes d'administration
admin.site.register(Option, OptionAdmin)
admin.site.register(OptionGroup, OptionGroupAdmin)
