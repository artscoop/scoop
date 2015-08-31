# coding: utf-8
from __future__ import absolute_import

from ajax_select import make_ajax_form
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.util.django.admin import GenericModelUtil
from scoop.core.util.shortcuts import addattr
from scoop.editorial.forms.editorial import ConfigurationInlineForm, ExcerptTranslationInlineForm
from scoop.editorial.models.configuration import Configuration
from scoop.editorial.models.excerpt import Excerpt, ExcerptTranslation
from scoop.editorial.models.page import Page
from scoop.editorial.models.position import Position
from scoop.editorial.models.template import Template


class ConfigurationInlineAdmin(admin.TabularInline):
    """ Inline admin de configuration de page """
    verbose_name = _("Configuration")
    verbose_name_plural = _("Configurations")
    model = Configuration
    form = ConfigurationInlineForm
    max_num = 20
    extra = 4


class ConfigurationAdmin(admin.ModelAdmin, GenericModelUtil):
    """ Administration des configurations """
    list_select_related = True
    list_display = ['id', 'position', 'template', 'get_content_object_info', 'is_valid']
    list_editable = []
    search_fields = []
    inlines = []


class PageAdmin(AutoAuthoredModelAdmin):
    """ Administration des pages """
    list_select_related = True
    list_display = ['id', 'name', 'title', 'path', 'template', 'active', 'anonymous', 'authenticated', 'uuid']
    list_editable = ['active', 'anonymous', 'authenticated']
    list_filter = ['active', 'anonymous', 'authenticated']
    search_fields = []
    fieldsets = (
        (_("Page"), {'fields': ('path', 'name', 'title', 'description', 'author', 'template', 'parent', 'active',)}), ('Plus', {'fields': ('anonymous', 'authenticated', 'heading',)}))
    form = make_ajax_form(Page, {'author': 'user'})
    inlines = [ConfigurationInlineAdmin, ]
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'


class ExcerptTranslationInlineAdmin(admin.TabularInline):
    """ Inline d'administration des extraits """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = ExcerptTranslation
    max_num = len(settings.LANGUAGES)
    form = ExcerptTranslationInlineForm
    extra = 2


class ExcerptAdmin(admin.ModelAdmin):
    """ Administration des extraits de texte """
    list_select_related = True
    list_display = ['id', 'name', 'visible', 'uuid']
    list_editable = ['visible']
    search_fields = ['name', 'translations__text']
    list_filter = ['visible']
    fieldsets = ((_("Excerpt"), {'fields': ('name', 'author', 'format', 'visible', 'weight',)}),)
    form = make_ajax_form(Excerpt, {'author': 'user'})
    inlines = [ExcerptTranslationInlineAdmin]
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'


class PositionAdmin(admin.ModelAdmin):
    """ Administration des positions d'un template """
    list_select_related = True
    list_display = ['id', 'get_icon_html', 'name', 'title', 'anonymous', 'authenticated']
    list_editable = ['anonymous', 'authenticated']
    list_filter = ['anonymous', 'authenticated']
    search_fields = ['name', 'title', 'description']
    inlines = []


class TemplateAdmin(admin.ModelAdmin):
    """ Administration des templates """
    list_select_related = True
    list_display = ['id', 'name', 'path', 'full', 'exists', 'get_position_count']
    list_editable = ['full']
    list_filter = ['full']
    search_fields = ['name', 'path']
    inlines = []
    filter_horizontal = ['positions']
    actions = ['auto_fill']

    # Actions
    @addattr(short_description=_("Automatically fill selected templates information"))
    def auto_fill(self, request, queryset):
        """ Découvrir automatiquement les positions du template """
        for template in queryset:
            template.auto_fill()
        self.message_user(request, _("The selected templates have been updated."))

    # Getter
    @addattr(short_description=_("Positions"))
    def get_position_count(self, obj):
        """ Renvoyer le nombre de positions dans le template """
        return obj.positions.all().count()

# Enregistrer les classes d'administration
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Excerpt, ExcerptAdmin)
