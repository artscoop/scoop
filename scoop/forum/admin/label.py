# coding: utf-8
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin

from scoop.forum.models.label import Label


@admin.register(Label)
class LabelAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration de forum """

    # Configuration
    list_display = ['id', 'short_name', 'name', 'description', 'primary', 'status', 'visible']
    list_editable = ['short_name']
    list_filter = ['primary', 'visible', 'status', 'groups']
    search_fields = ['short_name', 'translations__name', 'translations__description', 'translations__html']
    list_per_page = 25
