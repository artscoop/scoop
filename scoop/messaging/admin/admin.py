# coding: utf-8
from ajax_select import make_ajax_form
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.db import models
from django.utils.translation import ugettext_lazy as _
from scoop.core.templatetags.html_tags import ol, ul
from scoop.core.util.shortcuts import addattr
from scoop.messaging.forms import MessageAdminForm, RecipientAdminForm
from scoop.messaging.forms.machinery import QuotaAdminForm
from scoop.messaging.models.alert import Alert
from scoop.messaging.models.mailevent import MailEvent
from scoop.messaging.models.mailtype import MailType, MailTypeTranslation
from scoop.messaging.models.message import Message
from scoop.messaging.models.quota import Quota
from scoop.messaging.models.recipient import Recipient


class MailTypeTranslationInlineAdmin(admin.TabularInline):
    """ Administration inline des traductions de types de courrier """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = MailTypeTranslation
    max_num = len(settings.LANGUAGES)
    formfield_overrides = {models.TextField: {'widget': admin.widgets.AdminTextInputWidget}, }
    max_num = len(settings.LANGUAGES)
    extra = 2


class MailTypeAdmin(admin.ModelAdmin):
    """ Administration des types de courrier """

    # Configuration
    list_select_related = True
    list_display = ['id', 'short_name', 'get_category_list', 'template', 'get_interval']
    list_filter = []
    readonly_fields = []
    search_fields = ['short_name', 'translations__description', 'template', 'category']
    inlines = [MailTypeTranslationInlineAdmin]

    # Getter
    @addattr(short_description=_("Categories"), admin_order_field='category')
    def get_category_list(self, obj):
        """ Renvoyer la liste des catégories """
        return ol(obj.get_categories())


class RecipientInlineAdmin(TabularInline):
    """ Inline admin de destinataires d'un message """
    model = Recipient
    form = make_ajax_form(Recipient, {'user': 'user'}, RecipientAdminForm)
    max_num = 8
    extra = 0


class QuotaAdmin(admin.ModelAdmin):
    """ Administration des quotas d'envois """
    list_select_related = True
    list_display = ['group', 'max_threads']
    list_display_links = ['group']
    list_filter = []
    readonly_fields = []
    form = QuotaAdminForm


class MailEventAdmin(admin.ModelAdmin):
    """ Administration des courriers électroniques """
    list_select_related = True
    list_display = ['id', 'type', 'recipient', 'get_data_repr', 'forced', 'sent']
    list_display_links = ['id']
    list_filter = []
    readonly_fields = []


class AlertAdmin(admin.ModelAdmin):
    """ Administration des alertes """
    list_select_related = True
    list_display = ['id', 'user', 'title', 'read', 'level', 'get_data_repr']
    list_display_links = ['id']
    list_filter = []
    readonly_fields = []

# Enregistrer les classes d'administration
admin.site.register(MailType, MailTypeAdmin)
admin.site.register(Quota, QuotaAdmin)
admin.site.register(MailEvent, MailEventAdmin)
admin.site.register(Alert, AlertAdmin)
