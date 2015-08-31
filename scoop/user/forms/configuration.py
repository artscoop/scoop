# coding: utf-8
from __future__ import absolute_import

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from scoop.user.util.forms import DataForm


class ConfigurationForm(DataForm):
    """ Formulaire de données utilisateur : Configuration du compte """
    # Configuration
    name = 'user.configuration'
    defaults = {'session_timeout': 259200, 'login_destination': 0, 'receive_emails': True, 'receive_interval': 3600, 'receive_on_message': True, 'receive_on_staff': True,
                'receive_on_favorite': True}
    saved_fields = None
    # Constantes
    SESSION_DURATIONS = [[900, _("15 minutes")], [1800, _("30 minutes")], [10800, _("3 hours")], [259200, _("3 days")], [2592000, _("30 days")]]
    MAIL_INTERVALS = [[300, _("5 minutes")], [900, _("15 minutes")], [3600, _("1 hour")], [21600, _("6 hours")], [172800, _("2 days")]]
    DESTINATIONS = [[0, _("Home page")], [1, _("My profile")], [2, _("My messages")]]
    DESTINATION_URLS = {0: 'index', 1: 'user:self-view', 2: 'messaging:inbox'}
    # Champs
    session_timeout = forms.TypedChoiceField(coerce=int, initial=259200, choices=SESSION_DURATIONS, required=True, label=_("Stay connected for"))
    login_destination = forms.TypedChoiceField(coerce=int, choices=DESTINATIONS, initial=0, required=True, label=_("Destination upon login"))
    receive_emails = forms.BooleanField(initial=True, required=False, label=_("Receive emails"))
    receive_interval = forms.TypedChoiceField(coerce=int, initial=3600, choices=MAIL_INTERVALS, required=True, label=_("Max reception rate"))
    # Options de réception de message
    receive_on_message = forms.BooleanField(initial=True, required=False, label=_("Receive when a user sends you a message"))
    receive_on_staff = forms.BooleanField(initial=True, required=False, label=_("Receive when a staff member sends you a message"))

    # Getter
    @classmethod
    def get_login_destination(cls, user):
        """ Renvoyer l'URL de destination après connexion pour un utilisateur """
        data = cls.get_data_for(user)
        return reverse(cls.DESTINATION_URLS[data['login_destination']])
