# coding: utf-8
import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch.dispatcher import receiver

from scoop.location.tasks.city import weather_prefetch


logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def login_actions(sender, request, user, **kwargs):
    """ Traiter la connexion d'un utilisateur """
    try:
        if hasattr(user, 'profile') and hasattr(user.profile, 'city'):
            # Récupérer la météo de sa ville
            getattr(weather_prefetch, 'delay')(user.profile.city)
    except (OSError, IOError):
        pass
