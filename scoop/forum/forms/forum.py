# coding: utf-8
from django import forms

from scoop.forum.models import Label


class LabelAdminForm(forms.ModelForm):
    """ Formulaire admin des forums """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(LabelAdminForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Label
        exclude = []
