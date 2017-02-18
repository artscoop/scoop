# coding: utf-8
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.help.models.group import HelpGroup, HelpGroupTranslation


class HelpGroupTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin de traduction des groupes d'aide """

    # Configuration
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = HelpGroupTranslation
    max_num = len(settings.LANGUAGES)
    extra = 3


@admin.register(HelpGroup)
class HelpGroupAdmin(admin.ModelAdmin):
    """ Administration des groupes d'aide """

    # Configuration
    list_select_related = True
    list_display = ['id', 'uuid', 'active', 'name', 'slug']
    list_filter = []
    list_editable = ['active']
    search_fields = ['uuid', 'name', 'slug']
    ordering = ['-id']
    actions = []
    inlines = [HelpGroupTranslationInlineAdmin]
