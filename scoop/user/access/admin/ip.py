# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr
from scoop.user.access.admin.filters import IPCountryFilter
from scoop.user.access.models.ip import IP

__all__ = ['IPAdmin']


class IPAdmin(admin.ModelAdmin):
    """ Administration des IPs connues """
    # Configuration
    list_select_related = True
    list_display = ['id', 'string', 'get_hex', 'get_ip_class', 'reverse', 'isp', 'harm', 'blocked', 'updated', 'country', 'city_name']
    raw_id_fields = []
    list_filter = [IPCountryFilter, 'blocked', 'harm', 'updated']
    list_display_links = ['id', 'string']
    list_editable = []
    list_per_page = 50
    search_fields = ['string', 'ip', 'reverse', 'isp']
    save_on_top = True
    actions = ['update_ip']

    # Actions
    def get_actions(self, request):
        """ Renvoyer les actions disponibles """
        return super(IPAdmin, self).get_actions(request)

    @addattr(short_description=_("Update selected IPs"))
    def update_ip(self, request, queryset):
        """ Mettre à jour les informations des IP sélectionnées """
        count = queryset.count()
        for item in queryset:
            item.set_ip_address(item.string)
            item.save()
        self.message_user(request, _("{} IP adresses were successfully updated.").format(count))

# Enregistrer les classes d'administration
admin.site.register(IP, IPAdmin)
