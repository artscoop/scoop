# coding: utf-8
import traceback
from random import randint

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy  # Fix pour django_extensions.reset_db
from django.http.response import HttpResponseRedirect
from scoop.core.util.django import forms
from scoop.core.util.django.middleware import MiddlewareBase
from scoop.user.forms import LoginForm
from scoop.user.forms.configuration import ConfigurationForm
from scoop.user.models import User


class LoginMiddleware(MiddlewareBase):
    """
    Middleware de connexion utilisateur

    Pour connecter l'utilisateur, nécessite :
    - un attribut POST submit-login
    - des attributs POST username et password
    - d'être déconnecté
    """

    # Constantes
    LOGOUT_URL = reverse_lazy('user:logout')

    # Exécuter le middleware
    def __call__(self, request):
        """ Traiter la requête """
        if request.has_post('submit-login') and request.user.is_anonymous():
            form = request.form([LoginForm])
            if forms.are_valid([form]):
                try:
                    # Retrouver l'adresse de destination après connexion
                    user = User.sign(request, request.POST)
                    target = request.GET.get('next', ConfigurationForm.get_login_destination(user))
                    return HttpResponseRedirect(target)
                except ValidationError as exc:
                    messages.warning(request, exc.message)
                except Exception as e:
                    traceback.print_exc(e)
                # Si nous sommes sur la page de logout, changer de page
                if LoginMiddleware.LOGOUT_URL in request.get_full_path():
                    return HttpResponseRedirect(settings.LOGIN_URL)
            else:
                messages.warning(request, "".join(form.errors['__all__']))
        return self.get_response(request)


class AutoLogoutMiddleware(MiddlewareBase):
    """
    Middleware de déconnexion automatique de l'utilisateur

    Déconnecte un membre connecté dans les cas suivants :
    - est en ligne mais désactivé
    - est en ligne et une déconnexion a été demandée
    """

    def __call__(self, request):
        """ Traiter la requête """
        if randint(0, 5) == 0:
            user = request.user
            if user.is_authenticated() and (user.deleted or not user.is_active or user.is_logout_forced()):
                User.sign(request, None, logout=True)
                cache.delete(User.CACHE_KEY['logout.force'].format(user.pk))
        return self.get_response(request)
