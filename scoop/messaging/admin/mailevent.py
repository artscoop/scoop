# coding: utf-8
from ajax_select import make_ajax_form
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.messaging.models.mailevent import MailEvent


@admin.register(MailEvent)
class MailEventAdmin(admin.ModelAdmin):
    """ Administration des courriers électroniques """

    # Configuration
    list_select_related = True
    list_display = ['id', 'type', 'recipient', 'sent_email', 'get_data_repr', 'forced', 'sent', 'discarded', 'minimum_time']
    list_display_links = ['id']
    list_filter = ['sent', 'discarded', 'forced', 'type']
    readonly_fields = []
    form = make_ajax_form(MailEvent, {'recipient': "user"})
    actions = ['discard']

    # Actions
    @addattr(short_description=_("Discard selected mail events"))
    def discard(self, request, queryset):
        """ Annuler l'envoi des messages sélectionnés """
        discarded = 0
        for mailevent in queryset:
            discarded += int(mailevent.discard())
        self.message_user(request, _("{count} mail events have been successfully discarded.").format(count=discarded))
