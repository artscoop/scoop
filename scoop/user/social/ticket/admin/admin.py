# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.user.social.ticket.models.ticket import Ticket
from scoop.user.social.ticket.models.update import Update


class TicketAdmin(admin.ModelAdmin):
    """ Administration d'un ticket """
    list_select_related = True
    list_display = ['id', 'author', 'title', 'description', 'closed', 'status', 'get_datetime']
    list_filter = ['closed', 'status']
    search_fields = ['title', 'description']
    readonly_fields = ['time']
    filter_horizontal = ['administrators']
    actions = ['close_ticket']

    # Actions
    @addattr(short_description=_("Close selected tickets"))
    def close_ticket(self, request, queryset):
        """ Fermer un ticket """
        for ticket in queryset:
            ticket.close()
        self.message_user(request, _("Selected tickets have been successfully closed."))


class UpdateAdmin(admin.ModelAdmin):
    """ Administration des mises à jour de tickets """
    list_select_related = True
    list_display = ['id', 'author', 'body', 'status']
    list_filter = ['status']
    search_fields = ['body']
    readonly_fields = ['time']
    raw_id_fields = ['author', 'ticket']


# Enregistrer les classes d'administration
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Update, UpdateAdmin)
