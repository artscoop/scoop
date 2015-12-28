# coding: utf-8
from admin_tools.dashboard.models import DashboardPreferences
from django.contrib import admin

__all__ = ['DashboardPreferencesAdmin']


class DashboardPreferencesAdmin(admin.ModelAdmin):
    """ Administration des préférences de dashboard d'admin-tools """

    # Configuration
    list_select_related = True
    list_display = ['id', 'user', 'dashboard_id']
    list_display_links = []
    list_filter = []
    list_editable = []
    readonly_fields = []
    search_fields = ['user']
    actions = []
    exclude = []
    actions_on_top = True
    order_by = ['id']

# Enregistrer les classes d'administration
admin.site.register(DashboardPreferences, DashboardPreferencesAdmin)
