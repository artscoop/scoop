# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from scoop.core.forms.search import BaseSearchForm
from scoop.rogue.models import Flag


class FlagForm(forms.ModelForm):
    """ Formulaire de signalement """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(FlagForm, self).__init__(*args, **kwargs)

    # Validation
    def clean(self):
        """ Valider et renvoyer les données du formulaire """
        if self.cleaned_data['type'].needs_details is True:
            if not self.cleaned_data['details']:
                raise forms.ValidationError(_("This flag type needs details."))
        return self.cleaned_data

    # Métadonnées
    class Meta:
        model = Flag
        fields = ['type', 'details']


class FlagSearchForm(BaseSearchForm):
    """ Formulaire de recherche de signalements """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        if kwargs.get('queryset', None) is not None:
            self.Meta.base_qs = kwargs['queryset']
            del kwargs['queryset']
        super(FlagSearchForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        base_qs = Flag.objects
        search_fields = ['name', 'admin', 'details']
