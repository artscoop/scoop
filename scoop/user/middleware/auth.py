# coding: utf-8
import traceback

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy  # Fix pour django_extensions.reset_db
from django.http.response import HttpResponseRedirect
from scoop.core.util.django import formutil
from scoop.user.forms import LoginForm
from scoop.user.models import User


class LoginMiddleware(object):
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
    def process_request(self, request):
        """ Traiter la requête """
        if request.user.is_anonymous() and request.has_post('submit-login'):
            form = request.form([LoginForm])
            if formutil.are_valid([form]):
                try:
                    from scoop.user.forms.configuration import ConfigurationForm
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
        return None


class AutoLogoutMiddleware(object):
    """
    Middleware de déconnexion automatique de l'utilisateur
    Déconnecte un membre connecté dans les cas suivants :
    - est en ligne mais désactivé
    - est en ligne et une déconnexion a été demandée
    """

    def process_request(self, request):
        """ Traiter la requête """
        user = request.user
        if user.is_authenticated() and (user.deleted or not user.is_active or user.is_logout_forced()):
            User.sign(request, None, logout=True)
            cache.delete(User.CACHE_KEY['logout.force'].format(user.pk))
        return None
