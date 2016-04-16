# coding: utf-8
from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from scoop.core.forms.search import BaseSearchForm
from scoop.user.models.user import User


class UserAdminForm(forms.ModelForm):
    """ Formulaire admin des utilisateur """

    # Constructeur
    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    # Métadonnées
    class Meta:
        model = User
        exclude = []


class PasswordForm(forms.Form):
    """ Formulaire de mise à jour du mot de passe """
    original = forms.CharField(required=True)
    new = forms.CharField(required=True, widget=forms.PasswordInput())
    confirm = forms.CharField(required=True, widget=forms.PasswordInput())

    # Validation
    def clean_original(self):
        """ Valider et renvoyer les données du champ mot de passe original """
        original = self.cleaned_data['original']
        if not self.request.user.can_edit(self.user):
            raise forms.ValidationError(_("You cannot edit this user."))
        if not authenticate(username=self.user.username, password=original):
            raise forms.ValidationError(_("Wrong password"))
        return original

    # Overrides
    def __init__(self, *args, **kwargs):
        """ Initialiser le formulaire """
        self.user = kwargs.get('user', None)
        self.request = kwargs.get('request', None)
        if self.user:
            del kwargs['user']
        if self.request:
            del kwargs['request']
        super(PasswordForm, self).__init__(*args, **kwargs)


class UsernameSearchForm(BaseSearchForm):
    """ Formulaire de recherche d'utilisateurs par nom d'utilisateur """

    def __init__(self, qs=None, *args, **kwargs):
        """ Initialiser le formulaire """
        super(UsernameSearchForm, self).__init__(*args, **kwargs)
        self.Meta.base_qs = qs or User.objects

    # Métadonnées
    class Meta:
        base_qs = User.objects
        search_fields = ['username']


class LoginForm(forms.Form):
    """ Formulaire de connexion """
    username = forms.CharField(required=True, label=_("User name"))
    password = forms.CharField(required=True, widget=forms.PasswordInput(), label=_("Password"))
    remember = forms.BooleanField(required=False, label=_("Remember me"))

    # Constructeur
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
