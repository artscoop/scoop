# coding: utf-8
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from scoop.messaging.models.label import Label


class LabelNewForm(forms.Form):
    """ Formulaire admin des étiquettes """

    # Champs
    label = forms.CharField(max_length=40, min_length=3, strip=True, label=_("Label"))

    # Clean
    def clean_label(self):
        """ Vérifier le contenu du champ label """
        label = self.cleaned_data['label']
        user = self.request.user  # il faut initialiser le formulaire via core.util.django.formutil.form
        if Label.objects.filter(author=user, name=label).exists():
            raise ValidationError("You already have created this label.")
        return label
