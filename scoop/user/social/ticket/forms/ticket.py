# coding: utf-8
from django import forms

from scoop.user.social.ticket.models.ticket import Ticket


class TicketForm(forms.ModelForm):
    """ Formulaire d'édition de tickets """

    # Métadonnées
    class Meta:
        model = Ticket
        fields = ('title', 'description')
