# coding: utf-8
from ajax_select.fields import AutoCompleteSelectWidget
from django import forms
from scoop.location.models import Venue


class VenueForm(forms.ModelForm):
    """ Formulaire de lieux """

    # Métadonnées
    class Meta:
        model = Venue
        fields = ['name', 'street', 'city', 'full']
        widgets = {'city': AutoCompleteSelectWidget('citypm', attrs={'class': "form-control"})
                   }

    # Médias
    class Media:
        pass
