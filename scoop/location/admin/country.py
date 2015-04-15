# coding: utf-8
from __future__ import absolute_import

import logging

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.django.admin import ViewOnlyModelAdmin
from scoop.core.util.shortcuts import addattr
from scoop.location.models.city import City
from scoop.location.models.country import Country, CountryName
from scoop.location.tasks.geonames import geonames_fill
from scoop.location.util.geonames import populate_cities, populate_currency, rename_cities, reparent_cities

logger = logging.getLogger(__name__)

__all__ = ['CountryAdmin']


class CountryAlternatesInlineAdmin(admin.TabularInline):
    """ Inline admin des noms alternatifs de pays """
    verbose_name = _(u"Translation")
    verbose_name_plural = _(u"Translations")
    model = CountryName
    max_num = 10
    extra = 4
    formfield_overrides = {models.TextField: {'widget': AdminTextInputWidget}, }


class CountryAdmin(ViewOnlyModelAdmin):
    """ Administration des pays """
    actions = ['fill_all', 'reparent', 'purge_cities', 'short_name_cities']
    actions_on_bottom = True
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    fieldsets = ((_(u"Country"), {'fields': ('code2', 'code3', 'currency', 'regional_level', 'subregional_level', 'public', 'safe')}),)
    inlines = [CountryAlternatesInlineAdmin, ]
    list_display = ['id', 'get_icon', 'get_name', 'get_sexagesimal_coordinates', 'code2', 'code3', 'continent', 'population', 'get_area', 'public', 'safe', 'get_last_update']
    list_display_links = ['id', 'get_name']
    list_editable = ['public', 'safe']
    list_filter = ['continent', 'public', 'currency__name']
    list_per_page = 25
    list_select_related = True
    ordering = ['id']
    readonly_fields = []
    save_on_top = False
    search_fields = ['alternates__name', 'name', 'continent']

    # Actions
    @addattr(short_description=_(u"Populate everything about this country"))
    def fill_all(self, request, queryset):
        """ Renseigner et arranger toutes les informations de pays """
        if settings.DEBUG is True:
            self.message_user(request, _(u"You can autopopulate this country by setting DEBUG to False."), level=messages.ERROR)
        else:
            getattr(geonames_fill, 'delay')(queryset)

    @addattr(short_description=_(u"Populate country from Geonames database file"))
    def populate_from_file(self, request, queryset):
        """ Renseigner toutes les villes d'un pays """
        for item in queryset:
            result = getattr(populate_cities, 'delay')(item)
            if result == -1:
                self.message_user(request, _(u"Set settings.DEBUG to False before populating city tables."))
            elif result == -2:
                self.message_user(request, _(u"You must add a country with the correct code to populate."))

    @addattr(short_description=_(u"Rebuild city hierarchy in country"))
    def reparent(self, request, queryset):
        """ Reconstruire la hiérarchie des villes des pays """
        for item in queryset:
            getattr(reparent_cities, 'delay')(item)
        self.message_user(request, _(u"City tree successfully rebuilt."))

    @addattr(short_description=_(u"Populate country currencies"))
    def populate_currencies(self, request, queryset):
        """ Mettre à jour les devises des pays """
        for country in queryset:
            getattr(populate_currency, 'delay')(country)

    @addattr(short_description=_(u"Rename every city with its short counterpart"))
    def short_name_cities(self, request, queryset):
        """ Renseigner les noms alternatifs des villes de tous les pays """
        getattr(rename_cities, 'delay')()
        self.message_user(request, _(u"Every city in the database had its name successfully updated when required."))

    @addattr(short_description=_(u"Remove all cities from selected countries"))
    def purge_cities(self, request, queryset):
        """ Supprimer toutes les villes des pays sélectionnés """
        for country in queryset:
            cities = City.objects.only('id').filter(country=country)
            cities.delete()
        self.message_user(request, _(u"Cities from selected countries have been successfully deleted."))

    @addattr(short_description=_(u"Set selected countries to private"))
    def unpublish(self, request, queryset):
        """ Rendre des pays non publics """
        for country in queryset:
            country.public = False
            country.save()
        self.message_user(request, _(u"Countries have been made private."))

    # Overrides
    def save_model(self, request, obj, form, change):
        """ Enregistrer l'objet dans la base """
        obj.save()
        if settings.DEBUG is False:
            getattr(geonames_fill, 'delay')(obj)

    # Getter
    @addattr(admin_order_field='updated', short_description=_(u"Updated"))
    def get_last_update(self, obj):
        """ Renvoyer la date de dernier update des villes """
        return obj.updated.strftime("%d/%m/%Y %H:%M")

# Enregistrer les classes d'administration
admin.site.register(Country, CountryAdmin)
