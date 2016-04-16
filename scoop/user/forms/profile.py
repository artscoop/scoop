# coding: utf-8

import floppyforms.__future__ as forms_
from django import forms
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from form_utils.fields import ClearableImageField

from scoop.content.models.picture import Picture
from scoop.content.util.widgets import PictureInlineWidget
from scoop.core.util.data.dateutil import date_age
from scoop.core.util.model.widgets import SimpleCheckboxSelectMultiple
from scoop.user.models.profile import BaseProfile


class ProfileForm(forms.ModelForm):
    """ Formulaire d'édition de profil """

    # Constantes
    MINIMUM_AGE = getattr(settings, 'USER_REGISTRATION_MINIMUM_AGE', 18)

    # Validation
    def clean_birth(self):
        """ Valider et renvoyer les données du champ date de naissance """
        date = self.cleaned_data['birth']
        age = date_age(date)
        if age < ProfileForm.MINIMUM_AGE:
            raise forms.ValidationError(_("You must be {age:d} or older.").format(age=ProfileForm.MINIMUM_AGE))
        return date

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        ProfileForm.MINIMUM_AGE = kwargs.get('minimum_age', ProfileForm.MINIMUM_AGE)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['city'].required = True


class ProfilePictureForm(forms_.ModelForm):
    """ Formulaire d'édition d'image de profil """

    # Champs
    image = ClearableImageField(widget=PictureInlineWidget, template=_("%(input)s <span class='clear'>%(checkbox)s <span>Remove picture</span></span>"),
                                label=_("Main picture"))

    # Validation
    def is_valid(self):
        """ Renvoyer si l'état du formulaire est valide """
        valid = super(ProfilePictureForm, self).is_valid()
        if valid is True and self.request:
            messages.success(self.request, _("Your picture may need to be reviewed by moderators before being visible."))
        return valid

    # Métadonnées
    class Meta:
        model = Picture
        fields = ['image']


class ProfileSearchForm(forms.Form):
    """ Formulaire de recherche de profils """
    gender = forms.MultipleChoiceField(choices=BaseProfile.GENDER, required=False, label=_("Gender"))
    seen_online = forms.BooleanField(required=False)


class SearchForm(forms.ModelForm):
    """ Formulaire de recherche de profils """
    genders = forms.MultipleChoiceField(choices=BaseProfile.GENDER, widget=SimpleCheckboxSelectMultiple(), required=False)
    age_min = forms.IntegerField(required=False, initial=18)
    distance = forms.IntegerField(required=False, initial=50)

    # Métadonnées
    class Meta:
        model = BaseProfile
        fields = ('genders', 'age_min')
