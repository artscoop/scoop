# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django_filters.filters import ChoiceFilter
from django_filters.filterset import FilterSet
from django_filters.widgets import LinkWidget
from scoop.rogue.models.flag import Flag


class FlagFilterSet(FilterSet):
    """ Filtre django-filters des signalements """

    # Constantes
    AUTOMATIC_CHOICES = (('1', _("Automatic")), ('0', _("Manual")),)

    # Champs
    automatic = ChoiceFilter(widget=LinkWidget, choices=AUTOMATIC_CHOICES, label=_("Automatic"))

    # Overrides
    def __init__(self, *args, **kwargs):
        """ Initialiser le filtre """
        super(FlagFilterSet, self).__init__(*args, **kwargs)
        self.filters['type'].widget = LinkWidget(attrs={'class': ''})
        self.filters['status'].widget = LinkWidget(attrs={'class': ''})
        self.filters['automatic'].widget = LinkWidget(attrs={'class': ''})
        for _name, field in self.filters.items():
            if isinstance(field, ChoiceFilter):
                field.extra['choices'] = tuple([("", _("All"))] + list(field.extra['choices']))

    # Métadonnées
    class Meta:
        model = Flag
        fields = ['type', 'status', 'automatic']
