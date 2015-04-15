# coding: utf-8
from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr
from scoop.user.models.activation import Activation

__all__ = ['ActivationAdmin']


class ActivationAdmin(admin.ModelAdmin):
    """ Administration des IP enregistrées pour les utilisateurs """
    list_select_related = True
    list_display = ['user', 'uuid', 'active']
    list_filter = []
    list_editable = []
    search_fields = ['uuid']
    ordering = ['-user']
    actions = ['activate']

    @addattr(short_description=_(u"Activate selected users"))
    def activate(self, request, queryset):
        """ Activer les utilisateurs sélectionnés """
        for activation in queryset:
            Activation.objects.activate(activation.uuid, activation.user.username, request)

# ------------------------ Enregistrer la liste des classes pour l'administration
admin.site.register(Activation, ActivationAdmin)
