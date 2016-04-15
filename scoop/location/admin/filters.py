# coding: utf-8
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class ParentedFilter(SimpleListFilter):
    """ Filtre admin d'objets avec un attribut parent """
    title = _("Parent")
    parameter_name = 'parented'

    def lookups(self, request, model_admin):
        """ Renvoyer toutes les valeurs possibles de filtre """
        return (
            ('true', _('Yes')),
            ('false', _('No')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les objets correspondant aux valeurs du filtre """
        if self.value() == 'true':
            return queryset.filter(parent__isnull=False)
        if self.value() == 'false':
            return queryset.filter(parent__isnull=True)


class PostalCodedFilter(SimpleListFilter):
    """ Filtre admin sur la présence ou non de code postal """
    title = _("Has postal code")
    parameter_name = 'postalcoded'

    def lookups(self, request, model_admin):
        """ Renvoyer toutes les valeurs possibles de filtre """
        return (
            ('true', _('Yes')),
            ('false', _('No')),
        )

    def queryset(self, request, queryset):
        """ Renvoyer les objets correspondant aux valeurs du filtre """
        if self.value() == 'true':
            return queryset.distinct().filter(city=True, alternates__language='post')
        if self.value() == 'false':
            return queryset.distinct().exclude(alternates__language='post')


class LevelFilter(SimpleListFilter):
    """ Filtre admin sur le niveau admin d'une ville """
    title = _("Level")
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        """ Renvoyer toutes les valeurs possibles de filtre """
        level_str = _("Level {level}")
        return ((str(l), level_str.format(level=l)) for l in range(1, 5))

    def queryset(self, request, queryset):
        """ Renvoyer les objets correspondant aux valeurs du filtre """
        if self.value():
            return queryset.filter(level=int(self.value()))
