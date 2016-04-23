# coding: utf-8
import logging
import os

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.content.util.admin import PicturedModelAdmin
from scoop.core.util.django.admin import ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr
from scoop.location.forms import VenueForm
from scoop.location.models import Venue
from scoop.location.models.currency import Currency
from scoop.location.models.timezone import Timezone

logger = logging.getLogger(__name__)

__all__ = ['VenueAdmin', 'CurrencyAdmin', 'TimezoneAdmin']


class VenueAdmin(admin.ModelAdmin, PicturedModelAdmin):
    """ Administration des lieux """
    list_select_related = True
    list_display = ['id', 'name', 'get_sexagesimal_coordinates', 'city', 'street', 'full', 'get_picture_set']
    list_filter = []
    readonly_fields = []
    raw_id_fields = ['city']
    form = VenueForm
    actions = ['fetch_pictures']
    save_on_top = True

    # Actions
    @addattr(short_description=_("Fetch pictures for selected venues"))
    def fetch_pictures(self, request, queryset):
        """ Récupérer automatiquement des images pour les lieux """
        for item in queryset:
            item.fetch_picture()
        self.message_user(request, _("Pictures were successfully fetched"))

    # Média
    class Media:
        js = (
            os.path.join(settings.STATIC_URL, 'admin/js/SelectBox.js'),
            os.path.join(settings.STATIC_URL, 'admin/js/SelectFilter2.js'),
        )


class CurrencyAdmin(admin.ModelAdmin):
    """ Administration des devises """
    list_select_related = False
    list_display = ['id', 'name', 'short_name', 'balance', 'updated']
    ordering = ['id']
    list_filter = []
    list_display_links = ['id', 'name']
    actions = ['update_currency']
    list_per_page = 25
    readonly_fields = []
    actions_on_bottom = True
    save_on_top = True

    # Actions
    @addattr(short_description=_("Update currency values"))
    def update_currency(self, request, queryset):
        """ Mettre à jour les valeurs des devises sélectionnées """
        for obj in queryset:
            obj.update_balance()
            obj.save()


class TimezoneAdmin(ViewOnlyModelAdmin):
    """ Administration des fuseaux horaires """
    list_select_related = True
    list_display = ['code', 'name', 'get_utc_offset', 'get_dst_offset']
    list_filter = []
    list_per_page = 25
    search_fields = ['code']
    list_display_links = []
    readonly_fields = []
    exclude = []
    actions = []
    actions_on_bottom = True
    save_on_top = True


# Enregistrer les classes d'administration
admin.site.register(Venue, VenueAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Timezone, TimezoneAdmin)
