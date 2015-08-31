# coding: utf-8
from __future__ import absolute_import

import logging

from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.content.util.admin import PicturedModelAdmin
from scoop.core.admin.filters import RandomOrderFilter
from scoop.core.util.django.admin import ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr
from scoop.location.admin.filters import LevelFilter, ParentedFilter, PostalCodedFilter
from scoop.location.models.city import City, CityName

logger = logging.getLogger(__name__)

__all__ = ['CityAdminModelAdmin']


class CityAlternatesInlineAdmin(admin.TabularInline):
    """ Inline admin des noms alternatifs de villes """
    verbose_name = _("Translation")
    verbose_name_plural = _("Translations")
    model = CityName
    max_num = 10
    extra = 4
    formfield_overrides = {models.TextField: {'widget': AdminTextInputWidget}}


class CityAdminModelAdmin(ViewOnlyModelAdmin, PicturedModelAdmin):
    """ Administration des villes """
    actions = ['flush_city', 'fetch_pictures', 'resave']
    actions_on_bottom = True
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    exclude = []
    fieldsets = ((_("City"), {'fields': ('name', 'ascii', 'country', 'position', 'city')}), (_("Geonames"), {'fields': ('code', 'population', 'type', 'a1', 'a2', 'a3', 'a4')}),)
    list_display = ['id', 'get_name', 'level', 'type', 'city', 'get_city_parent', 'get_country_icon', 'get_city_code', 'population', 'timezone', 'get_picture_set']
    list_display_links = ['id', 'get_name']
    list_filter = [RandomOrderFilter, 'city', 'pictured', ParentedFilter, LevelFilter, PostalCodedFilter, 'type', 'country', 'country__continent']  # , 'country']
    list_per_page = 25
    list_select_related = True
    readonly_fields = ['parent']
    inlines = [CityAlternatesInlineAdmin]
    save_on_top = True
    search_fields = ['alternates__name', 'type', 'parent__name']

    # Actions
    @addattr(short_description=_("Delete every city in the database"))
    def flush_city(self, request, queryset):
        """ Supprimer les villes sélectionnées """
        queryset.delete()

    @addattr(short_description=_("Resave cities"))
    def resave(self, request, queryset):
        """ Réenregistrer les villes du queryset (update) """
        for city in queryset:
            city.save()

    @addattr(short_description=_("Fetch pictures for selected cities"))
    def fetch_pictures(self, request, queryset):
        """ Récupérer automatiquement des images d'illustration pour les villes """
        for item in queryset:
            item.fetch_picture()
        self.message_user(request, _("Pictures were successfully fetched"))

    # Getter
    @addattr(allow_tags=True, admin_order_field='parent', short_description=_("Parent"))
    def get_city_parent(self, obj):
        """ Renvoyer la ville/administration parent direct """
        if obj.parent is not None:
            parent_name = obj.parent.get_name()
            parent_type = obj.parent.type
            return """<small class="muted">{feature}</small> <a href="?q={parent}">{name}</a>""".format(parent=parent_name, name=parent_name, feature=parent_type)
        else:
            return obj.country

    @addattr(allow_tags=True, admin_order_field='code', short_description=_("Code"))
    def get_city_code(self, obj):
        """ Renvoyer le code postal """
        return """{code}<small class="pull-right muted">{codes}</small>""".format(code=obj.get_code(), codes=len(obj.get_codes()) or "")

    # Overrides
    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut de l'admin """
        qs = super(CityAdminModelAdmin, self).get_queryset(request)
        return qs.select_related('parent')

# Enregistrer les classes d'administration
admin.site.register(City, CityAdminModelAdmin)
