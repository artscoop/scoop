# coding: utf-8
from django import forms

from scoop.rogue.models.mailblock import MailBlock


class MailBlockForm(forms.ModelForm):
    """ Formulaire de blocage d'adresse email """

    def __init__(self, *args, **kwargs):
        """ Initialiser """
        super(MailBlockForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = MailBlock
        fields = ['email', 'user', 'reason', 'active']
