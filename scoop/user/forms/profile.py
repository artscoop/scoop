# coding: utf-8
from __future__ import absolute_import

from datetime import datetime

import floppyforms.__future__ as forms_
from ajax_select.fields import AutoCompleteSelectWidget
from annoying.decorators import autostrip
from django import forms
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from form_utils.fields import ClearableImageField

from scoop.content.models.picture import Picture
from scoop.content.util.widgets import PictureInlineWidget
from scoop.core.util.data.dateutil import date_age
from scoop.core.util.model.widgets import SelectDateWidget, SimpleCheckboxSelectMultiple
from scoop.user.models.profile import BaseProfile


@autostrip
class ProfileForm(forms_.ModelForm):
    """ Formulaire d'édition de profil """
    # Constantes
    MINIMUM_AGE = getattr(settings, 'USER_REGISTRATION_MINIMUM_AGE', 18)

    # Validation
    def clean_birth(self):
        """ Valider et renvoyer les données du champ date de naissance """
        date = self.cleaned_data['birth']
        age = date_age(date)
        if age < ProfileForm.MINIMUM_AGE:
            raise forms.ValidationError(_(u"You must be {age:d} or older.").format(age=ProfileForm.MINIMUM_AGE))
        return date

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        ProfileForm.MINIMUM_AGE = kwargs.get('minimum_age', ProfileForm.MINIMUM_AGE)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['city'].required = True

    # Métadonnées
    class Meta:
        model = BaseProfile
        widgets = {'birth': SelectDateWidget(years=range(1940, datetime.now().year + 1 - getattr(settings, 'USER_REGISTRATION_MINIMUM_AGE', 18))),
                   'city': AutoCompleteSelectWidget('citypm', attrs={'class': "control", 'placeholder': _(u"Enter your postcode or city name")})
                   }
        fields = ('gender', 'birth', 'city')


@autostrip
class ProfileAdminForm(forms.ModelForm):
    """ Formulaire admin d'édition de profil """

    # Métadonnées
    class Meta:
        model = BaseProfile
        exclude = []


@autostrip
class ProfileInlineAdminForm(forms.ModelForm):
    """ Formulaire admin inline d'édition de profil """

    # Métadonnées
    class Meta:
        model = BaseProfile
        exclude = ['updated', 'user', 'data']


class ProfilePictureForm(forms_.ModelForm):
    """ Formulaire d'édition d'image de profil """
    image = ClearableImageField(widget=PictureInlineWidget, template=_(u"%(input)s <span class='clear'>%(checkbox)s <span>Remove picture</span></span>"), label=_(u"Main picture"))

    # Validation
    def is_valid(self):
        """ Renvoyer si l'état du formulaire est valide """
        valid = super(ProfilePictureForm, self).is_valid()
        if valid is True and self.request:
            messages.success(self.request, _(u"Your picture may need to be reviewed by moderators before being visible."))
        return valid

    # Métadonnées
    class Meta:
        model = Picture
        fields = ['image']


class ProfileSearchForm(forms.Form):
    """ Formulaire de recherche de profils """
    gender = forms.MultipleChoiceField(choices=BaseProfile.GENDER, required=False, label=_(u"Gender"))
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
