# coding: utf-8
import IPy
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr
from scoop.rogue.forms import IPBlockForm
from scoop.rogue.models import IPBlock


class IPBlockAdmin(admin.ModelAdmin):
    """ Administration des blocages d'adresses IP """
    # Configuration
    list_select_related = True
    list_display = ['id', 'active', 'get_blocked_ip_count', 'type', 'representation', 'hostname', 'hostname_exclude', 'isp', 'get_ip1', 'get_ip2',
                    'get_expires']
    list_filter = ['active', 'type', 'category', 'hostname', 'harm']
    list_display_links = ['id']
    list_editable = ['active']
    list_per_page = 20
    search_fields = ['hostname', 'representation']
    form = IPBlockForm
    actions = ['resave']
    save_on_top = True
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    fieldsets = ((_("Blocking"), {'fields': ('active', 'type', 'category', 'ip1', 'ip2', 'isp', 'hostname', 'hostname_exclude', 'country_code')}),
                 (_("Extra"), {'fields': ('harm', 'description', 'expires')}))

    # Actions
    @addattr(short_description=_("Update selected IP blocks"))
    def resave(self, request, queryset):
        """ Réenregsitrer les blocages d'IP """
        for ipblock in queryset:
            ipblock.save()
        self.message_user(request, _("Selected blocks successfully updated."))

    # Getter
    @addattr(allow_tags=True, admin_order_field="ip1", short_description=_("IP 1"))
    def get_ip1(self, obj):
        """ Renvoyer l'IP 1 dans un format A.B.C.D """
        output = IPy.IP(int(obj.ip1)).strNormal()
        return output

    @addattr(allow_tags=True, admin_order_field="ip2", short_description=_("IP 2"))
    def get_ip2(self, obj):
        """ Renvoyer l'IP 2 dans un format A.B.C.D """
        output = IPy.IP(int(obj.ip2)).strNormal()
        return output

    @addattr(admin_order_field="expires", short_description=_("Expires"))
    def get_expires(self, obj):
        """ Renvoyer la date d'expiration du blocage """
        if obj.expires is None:
            return _("Never")
        return obj.expires


# Enregistrer les classes d'administration
admin.site.register(IPBlock, IPBlockAdmin)
