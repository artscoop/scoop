# coding: utf-8
from __future__ import absolute_import

from django import forms

from scoop.messaging.models.quota import Quota


class QuotaAdminForm(forms.ModelForm):
    """ Formulaire admin des quotas """

    # Métadonnées
    class Meta:
        model = Quota
        fields = ['group', 'max_threads']
