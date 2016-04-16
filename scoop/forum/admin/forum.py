# coding: utf-8
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin

from scoop.forum.models.label import Label


class LabelAdmin(AjaxSelectAdmin, admin.ModelAdmin):
    """ Administration de forum """
    list_display = ['id']


# Enregistrer les classes d'administration
admin.site.register(Label, LabelAdmin)
