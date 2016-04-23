# coding: utf-8
import logging

from django.dispatch.dispatcher import receiver
from scoop.core.util.signals import record
from scoop.user.util.signals import profile_banned

logger = logging.getLogger(__name__)


@receiver(profile_banned)
def profile_is_banned(sender, user, **kwargs):
    """ Traiter lorsqu'un profil est banni """
    record.send(user, 'user.ban.user', user)
