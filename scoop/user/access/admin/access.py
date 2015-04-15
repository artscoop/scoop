# coding: utf-8
from __future__ import absolute_import

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.django.admin import ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr
from scoop.user.access.models.access import Access
from user.access.admin.filters import AccessIPCountryFilter

__all__ = ['AccessAdmin']


class AccessAdmin(ViewOnlyModelAdmin):
    """ Administration des accès au site """
    # Configuration
    list_select_related = True
    list_display = ['id', 'user', 'get_image', 'page', 'referrer', 'ip', 'get_country', 'get_datetime']
    list_filter = [AccessIPCountryFilter]
    list_editable = []
    list_per_page = 25
    search_fields = ['ip__string', 'user__username', 'page__path']
    ordering = ['-id']
    actions = ['purge']

    # Actions
    @addattr(short_description=_(u"Purge selected access log entries"))
    def purge(self, request, queryset):
        """ Supprimer les accès sélectionnés """
        queryset.delete()

    # Getter
    @addattr(admin_order_field='ip__country', short_description=_(u"Country"))
    def get_country(self, obj):
        """ Renvoyer le pays de l'adresse IP """
        return obj.ip.country if obj.ip else None

    @addattr(allow_tags=True, short_description=_(u"User picture"))
    def get_image(self, obj):
        """ Renvoyer la vignette HTML du portrait de l'utilisateur """
        if obj.user and obj.user.is_active and obj.user.profile.picture:
            return obj.user.profile.picture.get_thumbnail_html(size=(48, 20))

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset de l'administration """
        qs = super(AccessAdmin, self).queryset(request)
        qs = qs.select_related('user', 'ip', 'user__profile__picture')
        return qs

    def get_actions(self, request):
        """ Renvoyer la liste des actions disponibles pour l'admin """
        actions = super(AccessAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# Enregistrer les classes d'administration
admin.site.register(Access, AccessAdmin)
