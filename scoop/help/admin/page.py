# coding: utf-8
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.help.models.page import Page, PageTranslation


class PageTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin de traduction des groupes d'options """

    # Configuration
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = PageTranslation
    max_num = len(settings.LANGUAGES)
    extra = 3


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """ Administration des pages d'aide """

    # Configuration
    list_select_related = True
    list_display = ['id', 'uuid', 'title', 'active']
    list_filter = []
    list_editable = ['active']
    search_fields = ['uuid', 'text', 'keywords']
    ordering = ['-id']
    actions = []
    inlines = [PageTranslationInlineAdmin]
