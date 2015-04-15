# coding: utf-8
from __future__ import absolute_import

from django.contrib import messages
from django.dispatch.dispatcher import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.signals import record
from scoop.user.util.signals import user_activated, user_deactivated


@receiver(user_activated)
def activation_check(sender, user, request, failed, **kwargs):
    """ Traiter une activation réussie ou échouée """
    if failed is False:
        record.send(None, actor=user, action='user.activation.user')
        if request is not None:
            from scoop.user.models import User
            # Accueillir l'utilisateur avec un message et le connecter
            messages.success(request, _(u"Congratulations! Your account is activated, you are now logged in."))
            User.sign(request, None, logout=False, fake=False, direct_user=user)
    else:
        if request is not None:
            messages.error(request, _(u"This activation code is invalid."), extra_tags="danger")


@receiver(user_deactivated)
def deactivation_update(sender, user, request, **kwargs):
    """ Traiter la désactivation d'un utilisateur """
    user.profile.set_data('deactivation', timezone.now())
