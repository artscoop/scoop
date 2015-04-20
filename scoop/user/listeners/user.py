# coding: utf-8
from __future__ import absolute_import

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.data.dateutil import date_age_days
from scoop.core.util.signals import record
from scoop.user.forms.configuration import ConfigurationForm
from scoop.user.models.activation import Activation
from scoop.user.models.user import User
from scoop.user.util.auth import get_profile_model
from scoop.user.util.signals import check_stale, user_demoted

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created(sender, instance, raw, created, **kwargs):
    """ Traiter lorsqu'un utilisateur vient d'être sauvegardé """
    if created is True:
        if instance and instance.id:
            try:
                instance.groups.add(Group.objects.get(name='members'))
            except:
                pass
            # Générer un profil par défaut
            if not getattr(instance, 'profile', None):
                instance.profile = get_profile_model().objects.create(user=instance)
            # Générer l'activation
            if getattr(settings, 'USER_ACTIVATION_NEEDED', False):
                instance.update(is_active=False, save=True)
                instance.activation = Activation.objects.create(user=instance)
                instance.activation.active = True
                instance.activation.save()
                instance.activation.send_mail()


@receiver(user_logged_in, sender=User)
def login_actions(sender, request, user, **kwargs):
    """ Traiter la connexion d'un utilisateur """
    # Changer l'expiration de la session
    timeout = ConfigurationForm.get_option_for(user, 'session_timeout')
    request.session.set_expiry(timedelta(seconds=timeout))
    logins = user.profile.get_data('logins', 0)
    user.profile.set_data('logins', logins + 1, save=True)
    messages.success(request, _(u"Hello, {name}!").format(name=capfirst(user)))
    # Actions publiques et enregistrements
    record.send(None, actor=user, action='user.login')


@receiver(user_logged_out, sender=User)
def logout_actions(sender, request, user, **kwargs):
    """ Traiter la déconnexion d'un utilisateur """
    messages.success(request, _(u"Thanks for visiting."))
    record.send(None, actor=user, action='user.logout')


@receiver(user_demoted)
def demotion_actions(sender, user, **kwargs):
    """ Traiter un utilisateur déchu de son statut """
    record.send(None, actor=user, action='user.demote')


@receiver(check_stale)
def check_stale_user(sender, user, profile, **kwargs):
    """ Vérifier et renvoyer si un utilisateur est laissé à l'abandon """
    if date_age_days(user.last_login) > 365:
        return True
    return False
