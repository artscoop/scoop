# coding: utf-8
from django import forms

from scoop.forum.models.message import Message


class MessageForm(forms.ModelForm):
    """ Formulaire admin des forums """

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super().__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = Message
        fields = ['text']
