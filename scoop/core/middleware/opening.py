# coding: utf-8
import logging

from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import timezone


logger = logging.getLogger(__name__)


class OpeningHoursMiddleware(object):
    """ Middleware de restriction des horaires d'ouverture aux membres non autorisés """
    # Définir les horaires d'ouverture du site
    frames = getattr(settings, "OPENING_HOURS", [[0, 24]])
    groups = getattr(settings, "OPENING_HOURS_GROUPS_EXCLUDE", ["VIP"])

    def now_in_timeframes(self, timeframes):
        """ Renvoyer si l'heure est contenue dans une des plages horaires d'ouverture """
        now = timezone.now()
        hour = now.hour
        for timeframe in timeframes:
            if timeframe[0] <= hour < timeframe[1]:
                return True
        return False

    def process_response(self, request, response):
        """ Traiter la réponse """
        user = request.user
        # Vérifier le groupe et les heures autorisées
        if user.is_authenticated():
            if not self.now_in_timeframes(self.frames):
                if not user.is_staff and not user.groups.filter(name__in=self.groups).exists():
                    # Changer le contenu de la page
                    return render_to_response("page/project/restricted/opening-hours.html", {'hours': self.frames}, context_instance=RequestContext(request))
        return response
