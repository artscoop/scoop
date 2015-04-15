# coding: utf-8
from __future__ import absolute_import

from django import forms

from scoop.user.social.ticket.models.update import Update


class UpdateForm(forms.ModelForm):
    """ Formulaire d'édition des mises à jour de tickets """

    # Métadonnées
    class Meta:
        model = Update
        fields = ('status', 'body')
