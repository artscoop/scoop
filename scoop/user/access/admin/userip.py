# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr


__all__ = ['UserIPAdmin']


class UserIPAdmin(admin.ModelAdmin):
    """ Administration des IP avec lesquelles des utilisateurs ont navigué """
    list_select_related = True
    list_display = ['user', 'ip', 'get_isp', 'get_harmful']
    list_filter = ['ip__harmful', 'ip__isp']
    list_editable = []
    search_fields = ['ip__string']
    ordering = ['-id']
    actions = []

    # Actions
    def get_actions(self, request):
        """ Renvoyer la liste des actions disponibles """
        return []

    # Getter
    @addattr(boolean=True, admin_order_field='ip__harmful', short_description=_("Harmful"))
    def get_harmful(self, obj):
        """ Renvoyer si l'IP est considérée dangereuse """
        return obj.ip.harmful

    @addattr(admin_order_field='ip__isp', short_description=_("ISP"))
    def get_isp(self, obj):
        """ Renvoyer le FAI de l'IP """
        return obj.ip.isp
