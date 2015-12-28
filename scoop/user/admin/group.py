# coding: utf-8
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr


class GroupAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration des groupes d'utilisateurs """
    list_select_related = True
    list_display = ['name', 'get_permissions']
    list_filter = []
    search_fields = ['name']
    actions = []
    filter_horizontal = ['permissions']
    form = make_ajax_form(Group, {'permissions': 'permission'})
    save_on_top = False

    # Getter
    @addattr(short_description=_("Permissions"))
    def get_permissions(self, obj):
        """ Renvoyer la représentation texte des permissions du groupe """
        return " | ".join([item.codename for item in obj.permissions.all()])

# Enregistrer les classes d'administration
try:
    admin.site.unregister(Group)
except:
    pass
admin.site.register(Group, GroupAdmin)
