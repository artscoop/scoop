# coding: utf-8
from django.conf import settings
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
            if getattr(settings, 'USER_LOGIN_ON_ACTIVATION', True) is True:
                # Accueillir l'utilisateur avec un message et le connecter
                from scoop.user.models import User
                messages.success(request, _("Congratulations! Your account is activated, you are now logged in."))
                User.sign(request, None, logout=False, fake=False, direct_user=user)
            else:
                messages.success(request, _("Congratulations! Your account is activated, you can now log in."))
    else:
        if request is not None:
            messages.error(request, _("This activation code is invalid."), extra_tags="danger")


@receiver(user_deactivated)
def deactivation_update(sender, user, request, **kwargs):
    """ Traiter la désactivation d'un utilisateur """
    # Ajouter une date de désactivation aux désactivations déjà enregistrées
    deactivation_dates = [timezone.now()] + user.profile.get_data('deactivation', [])
    user.profile.set_data('deactivation', deactivation_dates)
