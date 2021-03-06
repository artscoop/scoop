# coding: utf-8
from django.contrib import admin
from scoop.content.models.classification import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Administration des étiquettes de contenus """

    list_select_related = True
    list_display = ['id', 'active', 'name', 'description', 'short_name', 'parent']
    list_editable = ['parent']
    list_filter = ['active']
    search_fields = ['name', 'description']
    fields = ['short_name', 'name', 'description', 'parent', 'icon']
