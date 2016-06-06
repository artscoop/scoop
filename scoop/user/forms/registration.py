# coding: utf-8
import floppyforms.__future__ as forms_
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from scoop.core.util.shortcuts import get_website_name
from scoop.user.util.signals import credentials_form_check_email, credentials_form_check_name, credentials_form_check_username


class UserNewForm(forms.ModelForm):
    """ Formulaire d'inscription """

    # Constantes
    PASSWORD_LENGTH_MIN = 4
    USERNAME_LENGTH_MIN = 3
    USERNAME_LENGTH_MAX = 20
    FIRST_NAME_LENGTH_MAX = 20
    LAST_NAME_LENGTH_MAX = 40

    # Champs
    username = forms_.SlugField(max_length=30, min_length=4, label=_("User name"),
                                widget=forms_.TextInput(attrs={'placeholder': _("Letters, digits and underscores")}))
    email = forms_.EmailField(label=_("Email"), widget=forms_.TextInput(attrs={'placeholder': _("A non disposable email")}))
    email_confirm = forms_.EmailField(label=_("Retype email"))
    password_confirm = forms_.CharField(max_length=128, widget=forms_.PasswordInput(render_value=True), label=_("Retype password"))

    # Validation
    def clean_password(self):
        """" Valider et renvoyer les données du champ mot de passe """
        password = self.cleaned_data['password']
        if not password or len(password) < UserNewForm.PASSWORD_LENGTH_MIN:
            raise forms.ValidationError(_("Your password should be at least {min} characters long").format(min=UserNewForm.PASSWORD_LENGTH_MIN))
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
        if get_user_model().objects.filter(email__iexact=email).exists():
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
        if len(name) > UserNewForm.FIRST_NAME_LENGTH_MAX:
            raise forms.ValidationError(_("Your first name must not exceed {max} characters").format(max=UserNewForm.FIRST_NAME_LENGTH_MAX))
        return name

    def clean_username(self):
        """ Valider et renvoyer les données du champ nom d'utilisateur """
        name = self.cleaned_data['username']
        credentials_form_check_username.send(sender=self, username=name)
        length = len(name)
        # Renvoyer une erreur si le pseudo est utilisé
        if get_user_model().objects.filter(username__iexact=name):
            raise forms.ValidationError(_("This nickname is already in use."))
        # Renvoyer une erreur si le pseudo est trop court ou long
        if length > UserNewForm.USERNAME_LENGTH_MAX or length < UserNewForm.USERNAME_LENGTH_MIN:
            raise forms.ValidationError(
                _("Your nickname should be between {min} and {max} characters long.").format(min=UserNewForm.USERNAME_LENGTH_MIN,
                                                                                             max=UserNewForm.USERNAME_LENGTH_MAX))
        return name.lower()

    def clean_eula(self):
        """ Valider et renvoyer les données du champ Accepter les CGU """
        checked = self.cleaned_data.get('eula', True)
        if 'eula' in self.cleaned_data and checked is False:
            raise forms.ValidationError(_("You must accept our EULA to proceed."))
        return True

    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(UserNewForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'email_confirm', 'password', 'password_confirm')
        widgets = {'password': forms_.PasswordInput(render_value=True, attrs={'autocomplete': 'off'}),
                   'password_confirm': forms_.PasswordInput(render_value=False, attrs={'autocomplete': 'off'}),
                   'username': forms_.TextInput(attrs={'placeholder': _("4 characters minimum")}),
                   }


class UserEditForm(UserNewForm):
    """ Formulaire de modification du mot de passe du compte """
    original = forms.CharField(widget=forms.PasswordInput(), label=_("Original"))

    # Métadonnées
    class Meta:
        model = get_user_model()
        fields = ('password', 'password_confirm', 'original')
        widgets = {'password': forms.PasswordInput(attrs={'autocomplete': 'off'})}


class EULAForm(forms.Form):
    """ Formulaire de validation des CGU """

    # Constantes
    CHOICES = ((False, _("I refuse to comply to the EULA and do not want to use this website")),
               (True, _("I abide to the {website} EULA").format(website=get_website_name()))
               )

    # Champs
    eula = forms_.BooleanField(required=True, label=_("EULA"), widget=forms.Select(choices=CHOICES))

    # Initialiseur
    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        super(EULAForm, self).__init__(*args, **kwargs)
        self.fields['eula'].error_messages = {'required': _("You must abide to the EULA to continue")}
