# coding: utf-8
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.models.optiongroup import OptionGroupTranslation
from scoop.help.models.faq import FAQ, FAQTranslation


class FAQTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin de traduction des groupes d'options """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = FAQTranslation
    max_num = len(settings.LANGUAGES)
    extra = 4


class FAQAdmin(admin.ModelAdmin):
    """ Administration des groupes d'options """
    list_select_related = True
    list_display = ['pk', 'uuid', 'question', 'group', 'active']
    list_display_links = []
    list_filter = ['active']
    list_editable = ['active']
    readonly_fields = []
    search_fields = ['group']
    actions = []
    save_on_top = False
    inlines = [FAQTranslationInlineAdmin]


# Enregistrer les classes d'administration
admin.site.register(FAQ, FAQAdmin)
