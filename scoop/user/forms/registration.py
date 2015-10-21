# coding: utf-8
from __future__ import absolute_import

import floppyforms as forms_
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from scoop.user.util.signals import credentials_form_check_email, credentials_form_check_name, credentials_form_check_username


class RegistrationForm(forms_.ModelForm):
    """ Formulaire d'inscription """
    # Constantes
    PASSWORD_LENGTH_MIN = 4
    USERNAME_LENGTH_MIN = 3
    USERNAME_LENGTH_MAX = 20
    FIRST_NAME_LENGTH_MAX = 20
    LAST_NAME_LENGTH_MAX = 40
    # Champs
    username = forms_.SlugField(max_length=30, min_length=4, widget=forms_.TextInput(attrs={'size': 20}), label=_("User name"))
    email = forms_.EmailField(widget=forms_.TextInput(attrs={'size': 20}), label=_("Email"))
    email_confirm = forms.EmailField(label=_("Retype email"))
    password_confirm = forms.CharField(max_length=128, widget=forms.PasswordInput(), label=_("Retype password"))

    # Validation
    def clean_password(self):
        """" Valider et renvoyer les données du champ mot de passe """
        password = self.cleaned_data['password']
        if not password or len(password) < RegistrationForm.PASSWORD_LENGTH_MIN:
            raise forms.ValidationError(_("Your password should be at least {min} characters long").format(min=RegistrationForm.PASSWORD_LENGTH_MIN))
        return password

    def clean_password_confirm(self):
        """ Valider et renvoyer les données du champ confirmation de mot de passe """
        confirm = self.cleaned_data['password_confirm']
        if 'password_confirm' not in self.cleaned_data or confirm != self.cleaned_data.get('password'):
            raise forms.ValidationError(_("The password must be identical in both fields."))
        return confirm

    def clean_email(self):
        """ Valider et renvoyer les données du champ email """
        email = self.cleaned_data['email'].lower()
        credentials_form_check_email.send(sender=self, email=email)
        if User.objects.filter(email__iexact=email):
            raise forms.ValidationError(_("This e-mail address is already in use."))
        return email

    def clean_email_confirm(self):
        """ Valider et renvoyer les données du champ confirmation de l'email """
        confirm = self.cleaned_data['email_confirm'].lower()
        if not self.fields['email_confirm'].required:
            return confirm
        if 'email_confirm' not in self.cleaned_data or confirm != self.cleaned_data.get('email'):
            raise forms.ValidationError(_("The email addresses must be identical."))
        return confirm

    def clean_name(self):
        """ Valider et renvoyer les données du champ nom """
        name = self.cleaned_data['name']
        credentials_form_check_name.send(sender=self, name=name)
        if len(name) > RegistrationForm.FIRST_NAME_LENGTH_MAX:
            raise forms.ValidationError(_("Your first name must not exceed {max} characters").format(max=RegistrationForm.FIRST_NAME_LENGTH_MAX))
        return name

    def clean_username(self):
        """ Valider et renvoyer les données du champ nom d'utilisateur """
        name = self.cleaned_data['username']
        credentials_form_check_username.send(sender=self, username=name)
        length = len(name)
        # Renvoyer une erreur si le pseudo est utilisé
        if User.objects.filter(username__iexact=name):
            raise forms.ValidationError(_("This nickname is already in use."))
        # Renvoyer une erreur si le pseudo est trop court ou long
        if length > RegistrationForm.USERNAME_LENGTH_MAX or length < RegistrationForm.USERNAME_LENGTH_MIN:
            raise forms.ValidationError(
                _("Your nickname should be between {min} and {max} characters long.").format(min=RegistrationForm.USERNAME_LENGTH_MIN, max=RegistrationForm.USERNAME_LENGTH_MAX))
        return name.lower()

    def clean_eula(self):
        """ Valider et renvoyer les données du champ Accepter les CGU """
        checked = self.cleaned_data.get('eula', True)
        if 'eula' in self.cleaned_data and checked is False:
            raise forms.ValidationError(_("You must accept our EULA to proceed."))
        return True

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(RegistrationForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {'password': forms_.PasswordInput(render_value=True, attrs={'autocomplete': 'off'}), 'username': forms.TextInput(attrs={'size': 20})}


class EULAForm(forms_.Form):
    """ Formulaire de validation des CGU """
    eula = forms_.BooleanField(required=True,
                               help_text=mark_safe(_("By ticking this checkbox, I abide to the {website} license agreement").format(website=getattr(settings, 'SITE_NAME', 'N/A'))),
                               label=_("EULA"))


class RegistrationEULAForm(RegistrationForm):
    """ Formulaire d'inscription avec CGU à valider """
    eula = forms_.BooleanField(required=True,
                               help_text=mark_safe(_("By ticking this checkbox, I abide to the {website} license agreement").format(website=getattr(settings, 'SITE_NAME', 'N/A'))),
                               label=_("EULA"))


class AccountForm(RegistrationForm):
    """ Formulaire de modification du mot de passe du compte """
    original = forms.CharField(widget=forms.PasswordInput(), label=_("Original"))

    # Métadonnées
    class Meta:
        model = User
        fields = ('password', 'password_confirm', 'original')
        widgets = {'password': forms.PasswordInput(attrs={'autocomplete': 'off'})}
