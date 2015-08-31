# coding: utf-8
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class FlagStatusFilter(SimpleListFilter):
    """ Filtre admin de statut de signalement """
    title = _("status")
    parameter_name = 'status_ext'

    def lookups(self, request, model_admin):
        """ Renvoyer les paramètres d'URL et leur label """
        return (
            ('closed', _('closed')),
            ('open', _('open')),
            ('fixed', _('fixed')),
            ('undone', _('undone')),
            ('done', _('done')),
        )

    def queryset(self, request, queryset):
        """ Filtrer le queryset selon le paramètre d'URL """
        if self.value() == 'closed':
            return queryset.filter(status__in=[2, 3, 4])
        if self.value() == 'open':
            return queryset.filter(status__in=[0, 1, 5, 6])
        if self.value() == 'fixed':
            return queryset.filter(status__in=[2, 3])
        if self.value() == 'undone':
            return queryset.filter(action_done=False)
        if self.value() == 'done':
            return queryset.filter(action_done=True)
