# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import addattr
from scoop.user.models.activation import Activation

__all__ = ['ActivationAdmin']


@admin.register(Activation)
class ActivationAdmin(admin.ModelAdmin):
    """ Administration des IP enregistrées pour les utilisateurs """

    # Configuration
    list_select_related = True
    list_display = ['user', 'uuid', 'active']
    list_filter = []
    list_editable = []
    search_fields = ['uuid']
    ordering = ['-user']
    actions = ['activate']

    # Actions
    @addattr(short_description=_("Activate selected users"))
    def activate(self, request, queryset):
        """ Activer les utilisateurs sélectionnés """
        for activation in queryset:
            Activation.objects.activate(activation.uuid, activation.user.username, request)
