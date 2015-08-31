# coding: utf-8
from __future__ import absolute_import

from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django_countries.data import COUNTRIES


class IPCountryFilter(SimpleListFilter):
    """ Filtre admin des pays des IPs """
    title = _("Country")
    parameter_name = 'countrys'

    def lookups(self, request, model_admin):
        """ Renvoyer les options des pays  """
        queryset = model_admin.queryset(request)
        results = queryset.values_list('country').order_by('country').distinct()
        data = ((code[0] or 'none', dict(COUNTRIES).get(code[0], _("None"))) for code in results if code[0] not in ['None', ''])
        return data

    def queryset(self, request, queryset):
        """ Filtrer le queryset par le pays sélectionné """
        value = self.value()
        if value == 'none':
            return queryset.filter(country='')
        elif value:
            return queryset.filter(country=value)


class AccessIPCountryFilter(SimpleListFilter):
    """ Filtre admin des pays des IP des accès """
    title = _("Country")
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        """ Renvoyer les options de pays """
        queryset = model_admin.queryset(request)
        results = queryset.values_list('ip__country').order_by('ip__country').distinct()
        data = ((code[0] or 'none', dict(COUNTRIES).get(code[0], _("None"))) for code in results if code[0] not in ['None', ''])
        return data

    def queryset(self, request, queryset):
        """ Filtrer le queryset par le pays sélectionné """
        value = self.value()
        if value == 'none':
            return queryset.filter(ip__country='')
        elif value:
            return queryset.filter(ip__country=self.value())
