# coding: utf-8
from scoop.core.models.redirection import Redirection
from scoop.core.util.django.middleware import MiddlewareBase


class RedirectionFallbackMiddleware(MiddlewareBase):
    """ Middleware de redirection manuelle d'URLs """

    def __call__(self, request):
        """ Traiter la réponse """
        response = self.get_response(request)
        # En cas autre que 404/410, renvoyer la réponse inchangée
        if response.status_code not in {404, 410}:
            return response
        # Renvoyer l'URL de l'objet cible si l'ancienne adresse est reconnue
        redirection = Redirection.objects.at_path(request.path)
        if redirection is not None:
            return redirection.get_redirect(request)
        # Dans les autres cas, laisser le 404 vivre sa vie
        return response
