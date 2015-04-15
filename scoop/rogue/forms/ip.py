# coding: utf-8
from __future__ import absolute_import

from django import forms

from scoop.rogue.models import IPBlock
from scoop.user.access.util.widgets import IPIntegerField


class IPBlockForm(forms.ModelForm):
    """ Formulaire de blocage d'IP """
    # Champs
    ip1 = IPIntegerField(widget=forms.TextInput())
    ip2 = IPIntegerField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(IPBlockForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = IPBlock
        fields = ['ip1', 'ip2']
