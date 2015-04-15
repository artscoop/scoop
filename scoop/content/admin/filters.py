# coding: utf-8
from __future__ import absolute_import

from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class DimensionsFilter(SimpleListFilter):
    """ Filtre admin sur les dimensions des images """
    title = _(u"image size")
    parameter_name = 'imagesize'

    def lookups(self, request, model_admin):
        return (
            ('small', _('small')), ('smallish', _('quite small')), ('medium', _('medium')), ('large', _('large')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer un queryset selon la valeur de l'option choisie """
        if self.value() == 'small':
            return queryset.filter(width__lte=100, height__lte=100)
        if self.value() == 'smallish':
            return queryset.filter(width__range=(101, 320), height__range=(101, 320))
        if self.value() == 'medium':
            return queryset.filter(width__range=(101, 1000), height__range=(101, 1000))
        if self.value() == 'large':
            return queryset.filter(width__gte=1001, height__gte=1001)
