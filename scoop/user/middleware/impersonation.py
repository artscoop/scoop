# coding: utf-8
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.django.middleware import MiddlewareBase
from scoop.core.util.signals import record
from scoop.core.util.stream.urlutil import remove_get_parameter

logger = logging.getLogger(__name__)

# Constantes
IMPERSONATE_PARAMETER = "__as"
EXIT_PARAMETER = "__self"
SESSION_ITEM = "_as_user"


class ImpersonationMiddleware(MiddlewareBase):
    """
    Middleware : Permet à un superutilisateur de se faire passer pour n'importe quel membre.

    Ceci est rendu possible grâce à un paramètre d'URL,
    nommé __as=id. Il est ensuite possible de retrouver son identité
    avec le paramètre d'URL __self
    """

    # Getter
    @staticmethod
    def get_url(user, as_redirect=False):
        """ Renvoyer l'URL poue commencer à imiter un utilisateur """
        username = user.username
        output = "?{key}={value}".format(key=IMPERSONATE_PARAMETER, value=username)
        return HttpResponseRedirect(output) if as_redirect else output

    # Setter
    @staticmethod
    def impersonate(request, user=None):
        """ Imiter un utilisateur """
        request.session[SESSION_ITEM] = user.username if user else request.GET[IMPERSONATE_PARAMETER]

    def __call__(self, request):
        """ Traiter la requête """
        if request.user.is_superuser and settings.STATIC_URL not in request.path:
            if IMPERSONATE_PARAMETER in request.GET and SESSION_ITEM not in request.session:
                request.session[SESSION_ITEM] = request.GET[IMPERSONATE_PARAMETER]
                record.send(None, actor=request.user, action='user.impersonate', target=request.GET[IMPERSONATE_PARAMETER])
            elif EXIT_PARAMETER in request.GET and SESSION_ITEM in request.session:
                del request.session[SESSION_ITEM]
                messages.info(request, _("{name}, your impersonation session has been properly shut down.").format(name=request.user.get_short_name()))
                return HttpResponseRedirect(remove_get_parameter(request, EXIT_PARAMETER))
            if SESSION_ITEM in request.session:
                try:
                    request.user = get_user_model().objects.active().get(username__iexact=request.session[SESSION_ITEM])
                    messages.info(request,
                                  _("""You are viewing {path} as {name}. <a href="?{exit}">Quit</a>""").format(name=request.session[SESSION_ITEM],
                                                                                                               path=request.path, exit=EXIT_PARAMETER))
                except ObjectDoesNotExist:
                    messages.error(request, _("There is no active user with the username {name}.").format(name=request.session[SESSION_ITEM]))
                    del request.session[SESSION_ITEM]
        return self.get_response(request)
