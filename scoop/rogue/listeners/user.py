# coding: utf-8
import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch.dispatcher import receiver
from django.template.loader import render_to_string
from scoop.messaging.util.signals import mailable_event
from scoop.rogue.util.signals import user_has_ip_blocked
from scoop.user.models.user import User
from scoop.user.util.signals import online_status_updated, userip_created

logger = logging.getLogger(__name__)


@receiver(user_logged_in, sender=User)
def login_actions(sender, request, user, **kwargs):
    """ Gérer la connexion d'un utilisateur """
    from scoop.rogue.models import MailBlock
    # Désactiver si l'adresse email est bloquée
    if MailBlock.objects.is_blocked(user.email):
        user.set_inactive()


@receiver([online_status_updated])
def online_status_check(sender, online, **kwargs):
    """ Gérer le changement de statut online d'un utilisateur """
    from scoop.rogue.models import IPBlock
    # Uniquement lorsque l'utilisateur est en ligne
    if sender.is_active and online is True:
        task = getattr(IPBlock.objects, 'is_user_blocked')
        task.delay(sender)


@receiver([userip_created])
def userip_creation(sender, **kwargs):
    """ Gérer la création d'une nouvelle IP utilisateur """
    from scoop.rogue.models import IPBlock
    # Vérifier que l'ip est bloquée
    status = IPBlock.objects.is_blocked(sender.ip)
    if status['blocked']:
        user_has_ip_blocked.send(sender.user, ip=sender.ip, harm=status['harm'])


@receiver([user_has_ip_blocked])
def user_ip_is_blocked(sender, ip, harm, **kwargs):
    """ Gérer une IP utilisateur bloquée """
    if sender.is_active:
        from scoop.rogue.models import Flag
        # Créer un signalement si une IP est bloquée
        output = render_to_string('rogue/message/flag-user-ip.html', {'ip': ip})
        result = Flag.objects.flag(sender, typename='profile-harmful', automatic=True, details=output)
        if result is True:
            # Si un nouveau flag est créé (= c'est la première détection pour cet utilisateur)
            mailable_event.send(sender=Flag, mailtype='rogue.ipblock.flag', recipient=User.objects.superusers(), data={'users': sender})
