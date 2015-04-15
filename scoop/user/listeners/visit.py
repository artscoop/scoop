# coding: utf-8
from __future__ import absolute_import

from django.dispatch.dispatcher import receiver

from scoop.user.tasks.visit import add_visit
from scoop.user.util.signals import profile_viewed


@receiver(profile_viewed)
def profile_viewed(sender, **kwargs):
    """ Traiter une visite d'un profil """
    visitor, user = kwargs.get('visitor'), kwargs.get('user')
    if visitor.is_active and user.is_active:
        if visitor != user:
            if not visitor.has_perm('user.can_ghost_visit') or not visitor.profile.ghost_mode:
                visitor = getattr(visitor, '_wrapped', visitor)
                add_visit.delay(visitor, user)
