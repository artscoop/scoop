# coding: utf-8
from __future__ import absolute_import

from django import forms
from django.utils.translation import ugettext_lazy as _

from scoop.content.models.album import Album


class AlbumForm(forms.ModelForm):
    """ Formulaire d'albums """
    # Constantes
    NAME_LENGTH_MIN = 2
    DEFAULT_NAME = _("{author}'s album")

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(AlbumForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Album
        fields = ['name']
