# coding: utf-8
import logging

from django.conf import settings
from django.core.urlresolvers import reverse_lazy

from scoop.core.util.django.middleware import MiddlewareBase
from scoop.user.access.tasks import add_access
from scoop.user.util.signals import external_visit

logger = logging.getLogger(__name__)


class AccessMiddleware(MiddlewareBase):
    """ Middleware consignant les accès au site """

    # Liste des répertoires à ne pas compter dans le logging
    ACCESS_LOG_BLACKLIST = {settings.MEDIA_URL, settings.STATIC_URL, settings.ADMIN_MEDIA_PREFIX, reverse_lazy('admin:index'), '/admin_tools/'}
    HTTP_MIN, HTTP_MAX = 200, 309

    def __call__(self, request):
        """ Traiter la requête """
        # Marquer l'utilisateur comme en ligne si utilisateur
        if request.user.is_authenticated():
            request.user.update_online()
        else:
            # Envoyer un événement si un anonyme provient d'un referent externe.
            if request.is_referrer_external():
                external_visit.send(sender=None, request=request, referrer=request.get_referrer(), path=request.path)
        response = self.get_response(request)
        if response is not None and AccessMiddleware.HTTP_MIN <= response.status_code <= AccessMiddleware.HTTP_MAX:
            # Ne rien faire si un chemin blacklisté apparaît dans l'URL
            if [True for i in AccessMiddleware.ACCESS_LOG_BLACKLIST if request.path.startswith(str(i))]:
                return response
            # Enregistrer l'accès à la page
            add_access.delay(request)
        return response
