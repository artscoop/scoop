# coding: utf-8
import logging

from django.conf import settings
from django.utils import timezone

from scoop.core.util.django.middleware import MiddlewareBase
from scoop.core.util.django.templateutil import do_render

logger = logging.getLogger(__name__)


class OpeningHoursMiddleware(MiddlewareBase):
    """ Middleware de restriction des horaires d'ouverture aux membres non autorisés """

    # Définir les horaires d'ouverture du site
    frames = getattr(settings, "OPENING_HOURS", [(0, 24)])
    groups = getattr(settings, "OPENING_HOURS_GROUPS_EXCLUDE", ["VIP"])

    def now_in_timeframes(self, timeframes):
        """ Renvoyer si l'heure est contenue dans une des plages horaires d'ouverture """
        hour = timezone.now().hour
        for timeframe in timeframes:
            if timeframe[0] <= hour < timeframe[1]:
                return True
        return False

    def _call__(self, request):
        """ Traiter la réponse """
        user = request.user
        response = self.get_response(request)
        # Vérifier le groupe et les heures autorisées
        if user.is_authenticated():
            if not self.now_in_timeframes(OpeningHoursMiddleware.frames):
                if not user.is_staff and (self.groups and not user.groups.filter(name__in=self.groups).exists()):
                    # Changer le contenu de la page
                    return do_render(request, template="page/project/restricted/opening-hours.html", data={'hours': self.frames}, status_code=503,
                                     use_request=False)
        return response
