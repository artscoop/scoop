# coding: utf-8
from __future__ import absolute_import

import floppyforms as forms
from annoying.decorators import autostrip
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from scoop.user.models.user import User


@autostrip
class LoginForm(forms.Form):
    """ Formulaire de connexion """
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': _("User name or email")}), label=_("Identifier"))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'placeholder': _("Password")}), label=_("Password"))

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(LoginForm, self).__init__(*args, **kwargs)
        self.request = kwargs.get('request', None)

    # Validation
    def clean(self):
        """ Valider et renvoyer les données du formulaire """
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        if username and password:
            User.sign(self.request, {'username': username, 'password': password}, fake=True)
            return self.cleaned_data
        raise ValidationError(_("You must provide an username or email and a password."))
