# coding: utf-8
from django.contrib import admin

from scoop.content.models.advertisement import Advertisement
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin


class TagAdmin(admin.ModelAdmin):
    """ Administration des étiquettes de contenu """
    list_select_related = True
    list_display = ['id', 'name', 'icon']
    list_editable = []
    list_filter = []
    search_fields = []


@admin.register(Advertisement)
class AdvertisementAdmin(AutoAuthoredModelAdmin):
    """ Administration des annonces publicitaires """
    list_select_related = True
    list_display = ['id', 'name', 'group', 'network', 'weight', 'width', 'height', 'get_datetime_format', 'views']
    list_editable = []
    list_filter = ['group', 'network']
    search_fields = ['group', 'name']
    readonly_fields = []
    order_by = ['group']
